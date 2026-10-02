"""Re-score eval.jsonl after a grader-rule change. Does not call the LLM."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.tools import execute_sql
from eval.compare import SQL_STATUS
from eval.run_eval import gold_result, item_pass, load_eval_items


def _pred_frame(sql: str, cache: dict):
    token = (sql or "").strip().upper()
    if not sql or token in SQL_STATUS:
        return None
    if sql in cache:
        return cache[sql]
    try:
        cache[sql] = execute_sql(sql)
    except Exception:  # noqa: BLE001
        cache[sql] = None
    return cache[sql]


def main() -> int:
    items = {q["id"]: q for q in load_eval_items(verified_only=True)}
    log_path = ROOT / "eval" / "results" / "eval.jsonl"
    recs = [json.loads(l) for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    gold_cache = {}
    pred_cache: dict = {}
    changed = []
    old_acc: dict[str, list[bool]] = defaultdict(list)
    new_acc: dict[str, list[bool]] = defaultdict(list)

    out_lines = []
    for rec in recs:
        item = items[rec["id"]]
        old = bool(rec["pass"])
        old_acc[rec["config"]].append(old)
        gsql = item["gold_sql"]
        if gsql not in gold_cache:
            gold_cache[gsql] = gold_result(gsql)
        pred_df = _pred_frame(rec.get("sql") or "", pred_cache)
        ok, rule = item_pass(
            rec.get("sql") or "",
            pred_df,
            gsql,
            gold_cache[gsql],
            item["question"],
            key_columns=item.get("key_columns"),
            gold_status=item.get("gold_status"),
            pred_status=rec.get("status"),
            pred_assumption=rec.get("assumption"),
            grade=item.get("grade", "result"),
        )
        rec["pass"] = ok
        rec["match_rule"] = rule
        rec["rescored"] = True
        new_acc[rec["config"]].append(ok)
        if old != ok:
            changed.append(
                {
                    "id": rec["id"],
                    "config": rec["config"],
                    "run": rec["run"],
                    "old": old,
                    "new": ok,
                    "rule": rule,
                }
            )
        out_lines.append(json.dumps(rec, ensure_ascii=False))

    log_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    report = ROOT / "eval" / "results" / "grader_audit.md"
    lines = [
        "# Grader audit (key_columns)",
        "",
        "Rule: if the gold answer is a single label or value, `key_columns` is that column only.",
        "Existing `eval.jsonl` rows were re-executed and re-graded. No LLM re-runs.",
        "",
        "## Accuracy old vs new (mean over 150 calls)",
        "",
    ]
    print("config old new")
    for cfg in "ABCDEF":
        if cfg not in old_acc:
            continue
        o = sum(old_acc[cfg]) / len(old_acc[cfg])
        n = sum(new_acc[cfg]) / len(new_acc[cfg])
        lines.append(f"- **{cfg}**: {o:.1%} → {n:.1%}")
        print(cfg, f"{o:.3f}", f"{n:.3f}")
    lines.append("")
    lines.append(f"## Grade flips ({len(changed)} of {len(recs)} rows)")
    lines.append("")
    if not changed:
        lines.append("None.")
    else:
        lines.append("| id | config | run | old | new | match_rule |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for c in changed:
            lines.append(
                f"| {c['id']} | {c['config']} | {c['run']} | {c['old']} | {c['new']} | {c['rule']} |"
            )
            print(c)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
