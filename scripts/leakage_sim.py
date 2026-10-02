"""Token-overlap (Jaccard) of each eval question vs the few-shot pool."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9_]+", (text or "").lower()) if len(w) > 2}


def jaccard(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def main() -> int:
    ev = yaml.safe_load((ROOT / "eval" / "questions.yaml").read_text(encoding="utf-8"))
    few = yaml.safe_load((ROOT / "agent" / "fewshot.yaml").read_text(encoding="utf-8"))
    flagged = []
    print(f"{'eval':<6} {'max':>6}  few-shot  eval question")
    for q in ev["questions"]:
        best = 0.0
        best_id = ""
        for p in few["pairs"]:
            s = jaccard(q["question"], p["question"])
            if s > best:
                best, best_id = s, p["id"]
        flag = " FLAG" if best > 0.85 else ""
        print(f"{q['id']:<6} {best:6.3f}  {best_id:<8} {q['question'][:70]}{flag}")
        if best > 0.85:
            flagged.append((q["id"], best, best_id, q["question"]))
    print(f"\nFlagged (>0.85): {len(flagged)}")
    for row in flagged:
        print(row)
    return 0 if not flagged else 1


if __name__ == "__main__":
    sys.exit(main())
