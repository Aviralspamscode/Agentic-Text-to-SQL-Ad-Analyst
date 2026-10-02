"""Schema retrieval, SQL validation, read-only execution."""

from __future__ import annotations

import re
from pathlib import Path

import duckdb
import pandas as pd
import sqlglot
import yaml
from sqlglot import exp

ROOT = Path(__file__).resolve().parents[1]
WAREHOUSE = ROOT / "warehouse.duckdb"
LAYER_PATH = Path(__file__).resolve().parent / "semantic_layer.yaml"

_MUTATION = re.compile(
    r"\b(insert|update|delete|drop|alter|copy|attach|detach|create|replace|truncate|grant)\b",
    re.IGNORECASE,
)


LABEL_COLUMNS = {
    "unit",
    "campaign",
    "uid",
    "conversion_id",
    "journey_id",
    "cat1",
    "cat2",
    "cat3",
    "cat4",
    "cat5",
    "cat6",
    "cat7",
    "cat8",
    "cat9",
}


def load_layer() -> dict:
    return yaml.safe_load(LAYER_PATH.read_text(encoding="utf-8"))


def stringify_labels(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    out = df.copy()
    for col in out.columns:
        if col.lower() in LABEL_COLUMNS:
            out[col] = out[col].map(lambda v: None if v is None else str(v))
    return out


def allowed_schema() -> dict[str, set[str]]:
    layer = load_layer()
    return {name: set(spec["columns"]) for name, spec in layer["tables"].items()}


def _score_tables(question: str, layer: dict) -> list[tuple]:
    q = question.lower()
    scored = []
    for name, spec in layer["tables"].items():
        blob = " ".join(
            [name, spec.get("grain", "")]
            + [f"{c} {d['desc']}" for c, d in spec["columns"].items()]
        ).lower()
        words = {w for w in re.findall(r"[a-z0-9_]+", q) if len(w) > 2}
        score = sum(1 for w in words if w in blob)
        if name.replace("_", " ") in q:
            score += 5
        scored.append((score, name, spec))
    scored.sort(reverse=True)
    return scored


def retrieve_schema(question: str, max_tables: int = 6, config: str = "B") -> str:
    """config A = names/types only; B/C = descriptions, metrics, pitfalls."""
    layer = load_layer()
    scored = _score_tables(question, layer)
    picked = [row for row in scored if row[0] > 0][:max_tables]
    if not picked:
        picked = scored[:4]
    if config in {"E", "F"}:
        have = {n for _, n, _ in picked}
        extra = [(0, n, layer["tables"][n]) for n in layer["tables"] if n.startswith("v_") and n not in have]
        picked = extra + picked
    chunks = []
    if config != "A":
        chunks.append("Metrics:")
        for k, v in layer.get("metrics", {}).items():
            chunks.append(f"- {k}: {v}")
        chunks.append("Pitfalls:")
        for p in layer.get("pitfalls", []):
            chunks.append(f"- {p}")
    chunks.append("Tables:")
    for _, name, spec in picked:
        if config == "A":
            chunks.append(f"\n## {name}")
            for col, meta in spec["columns"].items():
                chunks.append(f"- {col} {meta['type']}")
        else:
            chunks.append(f"\n## {name} (grain: {spec['grain']})")
            for col, meta in spec["columns"].items():
                chunks.append(f"- {col} {meta['type']}: {meta['desc']}")
    return "\n".join(chunks)


def retrieve_fewshot(question: str, k: int = 3) -> str:
    pairs = yaml.safe_load((ROOT / "agent" / "fewshot.yaml").read_text(encoding="utf-8"))["pairs"]
    qwords = {w for w in re.findall(r"[a-z0-9_]+", question.lower()) if len(w) > 2}
    ranked = []
    for p in pairs:
        words = {w for w in re.findall(r"[a-z0-9_]+", p["question"].lower()) if len(w) > 2}
        ranked.append((len(qwords & words), p))
    ranked.sort(key=lambda x: x[0], reverse=True)
    chunks = ["Few-shot examples:"]
    for _, p in ranked[:k]:
        chunks.append(f"Q: {p['question']}\nSQL:\n{p['sql'].strip()}")
    return "\n\n".join(chunks)


def _strip_fence(sql: str) -> str:
    s = sql.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:sql)?\s*", "", s, flags=re.IGNORECASE)
        s = re.sub(r"\s*```$", "", s)
    return s.strip().rstrip(";")


def validate_sql(sql: str) -> tuple[str | None, str | None]:
    """Return (clean_sql, error)."""
    raw = _strip_fence(sql)
    token = raw.upper()
    if token in {
        "REFUSE",
        "UNKNOWN",
        "NEEDS_CLARIFICATION",
        "NOT_IN_DATA",
        "OUT_OF_SCOPE",
        "REFUSED",
        "ANSWERED",
    }:
        return token, None
    if _MUTATION.search(raw):
        return None, "Rejected: statement is not a read-only SELECT."
    try:
        parsed = sqlglot.parse(raw, read="duckdb")
    except sqlglot.errors.ParseError as exc:
        return None, f"sqlglot parse error: {exc}"
    if not parsed or len(parsed) != 1:
        return None, "Rejected: expected exactly one statement."
    tree = parsed[0]
    if not isinstance(tree, (exp.Select, exp.Union)):
        # WITH is wrapped as Select
        if not (isinstance(tree, exp.Command) is False and tree.find(exp.Select)):
            return None, "Rejected: not a single SELECT/WITH."
        if not isinstance(tree, exp.Select):
            return None, "Rejected: not a single SELECT/WITH."

    allowed = allowed_schema()
    for tbl in tree.find_all(exp.Table):
        name = tbl.name
        if name and name.lower() not in allowed and name.lower() not in {a.lower() for a in allowed}:
            # CTE names are also Table nodes; allow if defined
            cte_names = {c.alias_or_name.lower() for c in tree.find_all(exp.CTE)}
            if name.lower() in cte_names:
                continue
            return None, f"Unknown table: {name}"
    for col in tree.find_all(exp.Column):
        col_name = col.name
        tbl = col.table
        if not col_name or col_name == "*":
            continue
        if tbl:
            match = next((n for n in allowed if n.lower() == tbl.lower()), None)
            if match and col_name.lower() not in {c.lower() for c in allowed[match]}:
                return None, f"Unknown column {tbl}.{col_name}"

    out = tree.sql(dialect="duckdb")
    if "limit" not in out.lower():
        out = f"SELECT * FROM ({out}) AS _q LIMIT 1000"
    return out, None


def execute_sql(sql: str) -> pd.DataFrame:
    con = duckdb.connect(str(WAREHOUSE), read_only=True)
    try:
        con.execute("SET memory_limit = '2GB'")
        return stringify_labels(con.execute(sql).df())
    finally:
        con.close()
