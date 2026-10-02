"""Print gold SQL results for an eval batch (10 items)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.tools import execute_sql, stringify_labels

BATCHES = {
    1: ["E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10"],
    2: ["E11", "E12", "E13", "E14", "E15", "M01", "M02", "M03", "M04", "M05"],
    3: ["M06", "M07", "M08", "M09", "M10", "X01", "X02", "X03", "X04", "X05"],
    4: ["X06", "X07", "A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08"],
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=1)
    args = parser.parse_args()
    ids = BATCHES[args.batch]
    ev = yaml.safe_load((ROOT / "eval" / "questions.yaml").read_text(encoding="utf-8"))
    by_id = {q["id"]: q for q in ev["questions"]}
    for i, qid in enumerate(ids, 1):
        q = by_id[qid]
        sql = q["gold_sql"].strip()
        print(f"\n{'='*72}\n{qid} [{q['tier']}] {q['question']}\n")
        print("GOLD SQL:\n" + sql + "\n")
        if q.get("gold_status"):
            print("GOLD STATUS:", q["gold_status"], "grade:", q.get("grade", "status"))
        if sql.upper() in {
            "REFUSE",
            "UNKNOWN",
            "PENDING_USER",
            "NEEDS_CLARIFICATION",
            "NOT_IN_DATA",
            "OUT_OF_SCOPE",
            "REFUSED",
            "ANSWERED",
        }:
            print("RESULT:", sql)
        else:
            df = stringify_labels(execute_sql(sql))
            print(f"RESULT ({len(df)} rows):")
            print(df.to_string(index=False))
        print("LOGIC:", q.get("notes", ""))


if __name__ == "__main__":
    main()
