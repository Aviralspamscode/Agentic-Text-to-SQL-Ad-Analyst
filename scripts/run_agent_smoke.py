"""Run 5 test questions through the agent and print results."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.graph import run_question
from agent.llm import complete  # noqa: F401  # fail fast if .env missing


def main() -> None:
    spec = yaml.safe_load((ROOT / "agent" / "smoke_questions.yaml").read_text(encoding="utf-8"))
    rows = []
    for item in spec["questions"]:
        print(f"\n===== {item['id']} =====")
        print(item["question"])
        result = run_question(item["question"])
        df = result.get("result_df")
        print("SQL:", result.get("sql"))
        print("error:", result.get("validation_error") or "")
        if df is not None:
            print(df.head(15).to_string(index=False))
        print("ANSWER:", result.get("answer"))
        print("chart:", result.get("chart_spec"))
        print(
            f"tokens in/out={result.get('tokens_in')}/{result.get('tokens_out')} "
            f"latency_ms={result.get('latency_ms'):.0f}"
        )
        rows.append(
            {
                "id": item["id"],
                "question": item["question"],
                "sql": result.get("sql"),
                "answer": result.get("answer"),
                "tokens_in": result.get("tokens_in"),
                "tokens_out": result.get("tokens_out"),
                "latency_ms": result.get("latency_ms"),
                "error": result.get("validation_error"),
            }
        )
    out = ROOT / "eval" / "results" / "smoke_2b.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
