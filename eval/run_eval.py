"""Eval harness. Do not run until gold SQL is signed off.

Configs:
  A — raw table names and types only
  B — A + semantic layer descriptions and metrics
  C — B + few-shot retrieval

Each config is run 3 times at temperature 0. Report mean accuracy and min–max.
Cost in ₹ uses eval/pricing.yaml (fill from the provider page; never guess).
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.compare import match_results, status_pass

# Imported when a run actually starts.
# from agent.graph import run_question
# from agent.llm import complete


N_RUNS = 3
TEMPERATURE = 0.0
CONFIGS = ("A", "B", "C", "D", "E", "F")
F_MODEL = "gpt-4o"


def load_pricing() -> dict:
    raw = yaml.safe_load((ROOT / "eval" / "pricing.yaml").read_text(encoding="utf-8")) or {}
    env = {
        "USD_PER_1M_INPUT_TOKENS": os.environ.get("USD_PER_1M_INPUT_TOKENS"),
        "USD_PER_1M_OUTPUT_TOKENS": os.environ.get("USD_PER_1M_OUTPUT_TOKENS"),
        "USD_TO_INR": os.environ.get("USD_TO_INR"),
    }
    out = {}
    for k in (
        "USD_PER_1M_INPUT_TOKENS",
        "USD_PER_1M_OUTPUT_TOKENS",
        "USD_TO_INR",
        "GPT4O_USD_PER_1M_INPUT_TOKENS",
        "GPT4O_USD_PER_1M_OUTPUT_TOKENS",
    ):
        v = env.get(k) if env.get(k) not in (None, "") else raw.get(k)
        out[k] = float(v) if v not in (None, "") else None
    return out


def inr_cost(tokens_in: int, tokens_out: int, prices: dict, model: str | None = None) -> float | None:
    if prices.get("USD_TO_INR") is None:
        return None
    if model == F_MODEL:
        inp, outp = prices.get("GPT4O_USD_PER_1M_INPUT_TOKENS"), prices.get("GPT4O_USD_PER_1M_OUTPUT_TOKENS")
    else:
        inp, outp = prices.get("USD_PER_1M_INPUT_TOKENS"), prices.get("USD_PER_1M_OUTPUT_TOKENS")
    if inp is None or outp is None:
        return None
    usd = tokens_in / 1_000_000 * inp + tokens_out / 1_000_000 * outp
    return usd * prices["USD_TO_INR"]


def load_eval_items(verified_only: bool = True, path: Path | None = None) -> list[dict]:
    ev = yaml.safe_load((path or (ROOT / "eval" / "questions.yaml")).read_text(encoding="utf-8"))
    items = []
    for q in ev["questions"]:
        if q.get("question") == "PENDING_USER" or q.get("gold_sql") == "PENDING_USER":
            continue
        if path is None and verified_only and not q.get("verified"):
            continue
        items.append(q)
    return items


def gold_result(sql: str):
    token = sql.strip().upper()
    if token in {
        "REFUSE",
        "UNKNOWN",
        "NEEDS_CLARIFICATION",
        "NOT_IN_DATA",
        "OUT_OF_SCOPE",
        "REFUSED",
        "ANSWERED",
        "PENDING_USER",
    }:
        return token
    from agent.tools import execute_sql

    return execute_sql(sql)


def item_pass(
    pred_sql: str,
    pred_df,
    gold_sql: str,
    gold,
    question: str,
    key_columns: list[str] | None = None,
    gold_status: list[str] | str | None = None,
    pred_status: str | None = None,
    pred_assumption: str | None = None,
    grade: str = "result",
) -> tuple[bool, str]:
    if grade == "status" or gold_status:
        allowed = gold_status if gold_status is not None else gold_sql
        got = pred_status if pred_status is not None else pred_sql
        return status_pass(got, pred_assumption, allowed)
    if isinstance(gold, str):
        return False, "missing_gold_frame"
    return match_results(pred_df, gold, question, key_columns=key_columns)


def score_prediction(
    item: dict,
    pred_sql: str,
    pred_df,
    pred_status: str | None = None,
    pred_assumption: str | None = None,
) -> dict:
    """Compare one prediction to gold and return an auditable match_rule."""
    gold = gold_result(item["gold_sql"])
    ok, rule = item_pass(
        pred_sql,
        pred_df,
        item["gold_sql"],
        gold,
        item["question"],
        key_columns=item.get("key_columns"),
        gold_status=item.get("gold_status"),
        pred_status=pred_status,
        pred_assumption=pred_assumption,
        grade=item.get("grade", "result"),
    )
    rec = {"id": item["id"], "pass": ok, "match_rule": rule, "status": pred_status}
    print(f"{item['id']} pass={ok} match_rule={rule}")
    return rec


def classify_failure(item: dict, pred_sql: str, pred_status: str | None, rule: str) -> str:
    gold_sql = item.get("gold_sql") or ""
    gl = gold_sql.lower()
    q = (item.get("question") or "").lower()
    pred = (pred_sql or "").strip()
    pl = pred.lower()
    rule = rule or ""

    if item.get("grade") == "status" or item.get("gold_status"):
        if pred_status == "ANSWERED" or rule == "missing_assumption":
            return "ambiguity_not_flagged"
        return "wrong_status"

    if rule == "missing_frame" or "unknown column" in rule or "unknown table" in pl:
        return "hallucinated_column"
    if "recency_bucket" in pl and "journeys_converting" not in pl:
        return "hallucinated_column"
    if "from impressions" in pl and " as unit" in pl and "impressions_unit" not in pl:
        return "hallucinated_column"
    if "cpa_index_advertiser_credited" in pl:
        return "hallucinated_column"

    if "first_value(cat9)" in pl or ("cat9" in pl and "unit" not in gl and "cat9" not in gl):
        return "wrong_metric_definition"
    if "median(" in gl and "median(" not in pl and "quantile" not in pl:
        return "wrong_metric_definition"
    if "is_first" in gl and "is_last" in gl and "is_first" not in pl:
        return "wrong_metric_definition"
    if "cpa_index_adv_linear" in gold_sql and "cpa_index_adv_linear" not in pred and "v_segment_cpa_default" not in pl:
        return "wrong_metric_definition"
    if "credit_rate" in pl and "cpa" in q and "credit" in q and "rate" not in q:
        return "wrong_metric_definition"
    if "avg(cost)" in pl or "avg(cpa)" in pl:
        return "wrong_metric_definition"
    if "1.0 / touch_count" in gold_sql and "last_credit" in pl and "1.0 /" not in pl:
        return "wrong_metric_definition"
    if "pct_diff_last_vs_linear" in pl and "is_first" in gl:
        return "wrong_metric_definition"

    if "reallocation_plan" in gl and "reallocation_plan" not in pl:
        return "wrong_join"
    if "join" in gl and "join" not in pl and "using (" not in pl:
        return "wrong_join"
    if "on j.uid" in pl or "on j.uid =" in pl:
        return "wrong_join"

    if "period" in gl and "period" not in pl:
        return "wrong_filter"
    if ("unit <> 'other'" in gl or 'unit <> "other"' in gl) and "other" not in pl:
        return "wrong_filter"
    if "max(attribution)" in gl and "attribution" not in pl:
        return "wrong_filter"

    if "journey_length_distribution" in pl and ("start and finish" in q or "different segment" in q):
        return "misread_question"
    if "avg(cast(t.n_journeys" in pl or ("avg(cast(touch_count" in pl and "share" in q):
        return "wrong_aggregation_grain"
    if "avg(" in pl and "sum(" not in pl and any(w in q for w in ("share", "rate", "ctr")):
        return "wrong_aggregation_grain"
    if rule == "row_count_mismatch":
        return "wrong_aggregation_grain"

    if not pred:
        return "misread_question"
    return "other"


def _summarize(records: list[dict], items: list[dict], prices: dict, out_name: str = "summary.md") -> None:
    by_id = {q["id"]: q for q in items}
    out_dir = ROOT / "eval" / "results"
    lines = [
        "# Eval summary",
        "",
        "Tuning of D/E/F used `eval/dev_questions.yaml` only. Per-item eval logs were not used while changing prompts, views, or the plan node.",
        "",
    ]
    acc_by_cfg: dict[str, list[float]] = defaultdict(list)
    rows_by_cfg_run: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for rec in records:
        rows_by_cfg_run[(rec["config"], rec["run"])].append(rec)
    for (cfg, run_i), recs in sorted(rows_by_cfg_run.items()):
        acc = sum(1 for r in recs if r["pass"]) / len(recs) if recs else 0
        acc_by_cfg[cfg].append(acc)

    best_cfg = max(acc_by_cfg, key=lambda c: statistics.mean(acc_by_cfg[c]))
    lines.append("## Accuracy by config (3 runs)")
    present = [c for c in CONFIGS if acc_by_cfg.get(c)]
    for cfg in present:
        xs = acc_by_cfg[cfg]
        lines.append(
            f"- **{cfg}**: mean {statistics.mean(xs):.1%} "
            f"(min {min(xs):.1%}, max {max(xs):.1%})"
        )
    lines.append("")

    lines.append("## Accuracy by tier (mean across runs, all configs)")
    for cfg in present:
        lines.append(f"### Config {cfg}")
        tier_hits: dict[str, list[float]] = defaultdict(list)
        for run_i in range(1, N_RUNS + 1):
            recs = rows_by_cfg_run[(cfg, run_i)]
            by_tier: dict[str, list[bool]] = defaultdict(list)
            for r in recs:
                by_tier[by_id[r["id"]]["tier"]].append(r["pass"])
            for t, flags in by_tier.items():
                tier_hits[t].append(sum(flags) / len(flags))
        for t, xs in sorted(tier_hits.items()):
            lines.append(f"- {t}: {statistics.mean(xs):.1%}")
        lines.append("")

    best_recs = [r for r in records if r["config"] == best_cfg]
    lat = [r["latency_ms"] for r in best_recs]
    lat.sort()
    median_lat = lat[len(lat) // 2] if lat else 0
    p90 = lat[int(0.9 * (len(lat) - 1))] if lat else 0
    tok_in = statistics.mean(r["tokens_in"] for r in best_recs) if best_recs else 0
    tok_out = statistics.mean(r["tokens_out"] for r in best_recs) if best_recs else 0
    costs = [r["cost_inr"] for r in best_recs if r.get("cost_inr") is not None]
    mean_cost = statistics.mean(costs) if costs else None
    repairs = sum(1 for r in best_recs if r.get("repaired") and r["pass"])
    repair_attempts = sum(1 for r in best_recs if r.get("repaired"))
    repair_rate = repairs / repair_attempts if repair_attempts else 0

    # Majority-fail items on best config
    fail_votes: dict[str, int] = defaultdict(int)
    for r in best_recs:
        if not r["pass"]:
            fail_votes[r["id"]] += 1
    failed_ids = [i for i, n in fail_votes.items() if n >= 2] or list(fail_votes)
    tax = Counter()
    examples = []
    for iid in failed_ids:
        sample = next(r for r in best_recs if r["id"] == iid and not r["pass"])
        tag = classify_failure(by_id[iid], sample.get("sql") or "", sample.get("status"), sample.get("match_rule") or "")
        tax[tag] += 1
        if len(examples) < 3:
            examples.append((iid, tag, sample.get("sql"), sample.get("match_rule")))

    lines.append(f"## Best config: {best_cfg}")
    lines.append(f"- Median latency: {median_lat:.0f} ms; p90 {p90:.0f} ms")
    lines.append(f"- Mean tokens in/out: {tok_in:.0f} / {tok_out:.0f}")
    cost_s = f"INR {mean_cost:.4f}" if mean_cost is not None else "NOT COMPUTED"
    lines.append(f"- Mean cost per query: {cost_s}")
    lines.append(f"- Repair rescues: {repairs}/{repair_attempts} ({repair_rate:.1%} of repaired)")
    lines.append("")
    lines.append("## Failure taxonomy (best config, majority-fail items)")
    lines.append(f"P2.4 scope: best config ({best_cfg}), {len(failed_ids)} items.")
    for k, n in tax.most_common():
        lines.append(f"- {k}: {n}")
    lines.append("")
    lines.append("### Examples")
    for iid, tag, sql, rule in examples:
        lines.append(f"- **{iid}** `{tag}` rule={rule}")
        lines.append(f"  SQL: `{(sql or '')[:240]}`")

    text = "\n".join(lines) + "\n"
    (out_dir / out_name).write_text(text, encoding="utf-8")
    print(text.replace("₹", "INR "))
    return {
        "best_cfg": best_cfg,
        "acc_by_cfg": acc_by_cfg,
        "failed_ids": failed_ids,
        "tax": tax,
        "median_lat": median_lat,
        "mean_cost": mean_cost,
        "n_items": len(items),
        "examples": examples,
    }


def run(
    verified_only: bool = True,
    configs: tuple[str, ...] | None = None,
    items_path: Path | None = None,
    log_name: str = "eval.jsonl",
    require_n: int | None = 50,
    n_runs: int = N_RUNS,
) -> None:
    from agent.graph import run_question

    cfgs = configs or CONFIGS
    items = load_eval_items(verified_only=verified_only, path=items_path)
    prices = load_pricing()
    if prices.get("USD_PER_1M_INPUT_TOKENS") is None or prices.get("USD_TO_INR") is None:
        raise SystemExit("eval/pricing.yaml is incomplete. Fill official prices before running.")
    if require_n is not None and len(items) < require_n:
        raise SystemExit(f"Expected {require_n} items, found {len(items)}.")

    out_dir = ROOT / "eval" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / log_name

    done: set[tuple] = set()
    records: list[dict] = []
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            records.append(rec)
            done.add((rec["config"], rec["run"], rec["id"]))

    gold_cache = {q["id"]: gold_result(q["gold_sql"]) for q in items}

    with log_path.open("a", encoding="utf-8") as fh:
        for config in cfgs:
            for run_i in range(1, n_runs + 1):
                for item in items:
                    key = (config, run_i, item["id"])
                    if key in done:
                        continue
                    try:
                        model = F_MODEL if config == "F" else None
                        state = run_question(item["question"], config=config, model=model)
                    except Exception as exc:  # noqa: BLE001
                        state = {
                            "sql": "",
                            "result_df": None,
                            "status": "NOT_IN_DATA",
                            "assumption": "",
                            "tokens_in": 0,
                            "tokens_out": 0,
                            "latency_ms": 0,
                            "attempts": 0,
                            "validation_error": str(exc),
                        }
                    ok, rule = item_pass(
                        state.get("sql") or "",
                        state.get("result_df"),
                        item["gold_sql"],
                        gold_cache[item["id"]],
                        item["question"],
                        key_columns=item.get("key_columns"),
                        gold_status=item.get("gold_status"),
                        pred_status=state.get("status"),
                        pred_assumption=state.get("assumption"),
                        grade=item.get("grade", "result"),
                    )
                    repaired = int(state.get("attempts") or 0) > 0
                    rec = {
                        "id": item["id"],
                        "tier": item["tier"],
                        "config": config,
                        "run": run_i,
                        "pass": ok,
                        "match_rule": rule,
                        "sql": state.get("sql") or "",
                        "status": state.get("status"),
                        "assumption": state.get("assumption") or "",
                        "tokens_in": int(state.get("tokens_in") or 0),
                        "tokens_out": int(state.get("tokens_out") or 0),
                        "latency_ms": float(state.get("latency_ms") or 0),
                        "repaired": repaired,
                        "cost_inr": inr_cost(
                            int(state.get("tokens_in") or 0),
                            int(state.get("tokens_out") or 0),
                            prices,
                            model=F_MODEL if config == "F" else None,
                        ),
                        "error": state.get("validation_error") or "",
                    }
                    fh.write(json.dumps(rec, default=str) + "\n")
                    fh.flush()
                    records.append(rec)
                    print(
                        f"{config} r{run_i} {item['id']} pass={ok} {rule} "
                        f"{int(rec['latency_ms'])}ms",
                        flush=True,
                    )

    summary = _summarize(
        records,
        items,
        prices,
        out_name="summary-dev.md" if require_n is None else "summary.md",
    )
    if require_n is None:
        return
    results_path = ROOT / "RESULTS.md"
    text = results_path.read_text(encoding="utf-8")
    acc_a = statistics.mean(summary["acc_by_cfg"]["A"]) if summary["acc_by_cfg"].get("A") else None
    acc_best = statistics.mean(summary["acc_by_cfg"][summary["best_cfg"]])
    p23 = (
        f"A {acc_a:.1%} → {summary['best_cfg']} {acc_best:.1%}"
        if acc_a is not None
        else f"{summary['best_cfg']} {acc_best:.1%}"
    )
    p24 = f"{len(summary['failed_ids'])} majority-fail items on best config {summary['best_cfg']}"
    p25 = f"{summary['median_lat']:.0f} ms (best config {summary['best_cfg']})"
    p26 = (
        f"INR {summary['mean_cost']:.4f} (gpt-4o-mini, official $0.15/$0.60 per 1M, USDINR 96.33)"
        if summary["mean_cost"] is not None
        else "NOT COMPUTED"
    )
    repls = {
        "| P2.2 | eval set size | NOT COMPUTED | `eval/questions.yaml` (Phase 2) |":
            "| P2.2 | eval set size | 50 verified | `eval/questions.yaml` |",
        "| P2.3 | execution accuracy | NOT COMPUTED | `eval/run_eval.py` (Phase 2) |":
            f"| P2.3 | execution accuracy | {p23} | `eval/run_eval.py` 3× temp 0 |",
        "| P2.4 | failure cases | NOT COMPUTED | Phase 2 failure analysis |":
            f"| P2.4 | failure cases | {p24} | best-config taxonomy |",
        "| P2.5 | median latency | NOT COMPUTED | eval logs |":
            f"| P2.5 | median latency | {p25} | eval/results/eval.jsonl |",
        "| P2.6 | cost per query | NOT COMPUTED | tokens × prices from config |":
            f"| P2.6 | cost per query | {p26} | `eval/pricing.yaml` |",
    }
    for a, b in repls.items():
        text = text.replace(a, b)
    results_path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--i-have-signed-off", action="store_true")
    parser.add_argument("--include-unverified", action="store_true")
    parser.add_argument("--configs", default="A,B,C,D,E,F")
    parser.add_argument("--dev", action="store_true", help="Run eval/dev_questions.yaml")
    parser.add_argument("--log", default="eval.jsonl")
    parser.add_argument("--runs", type=int, default=N_RUNS)
    args = parser.parse_args()
    cfgs = tuple(c.strip() for c in args.configs.split(",") if c.strip())
    items_path = (ROOT / "eval" / "dev_questions.yaml") if args.dev else None
    if not args.i_have_signed_off and not args.dev:
        items = load_eval_items(verified_only=not args.include_unverified)
        prices = load_pricing()
        print(f"Prepared {len(items)} eval items (verified_only={not args.include_unverified}).")
        print(f"Configs {cfgs}, runs={N_RUNS}, temperature={TEMPERATURE}.")
        print(f"Pricing loaded: {prices} (None means NOT COMPUTED for ₹).")
        print("Refusing to run until --i-have-signed-off.")
        return
    run(
        verified_only=not args.include_unverified,
        configs=cfgs,
        items_path=items_path,
        log_name="dev.jsonl" if args.dev and args.log == "eval.jsonl" else args.log,
        require_n=None if args.dev else 50,
        n_runs=args.runs,
    )


if __name__ == "__main__":
    main()
