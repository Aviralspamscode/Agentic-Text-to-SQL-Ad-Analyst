"""Fail if few-shot, eval, or smoke questions overlap."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _load_questions() -> dict[str, list[str]]:
    smoke = yaml.safe_load((ROOT / "agent" / "smoke_questions.yaml").read_text(encoding="utf-8"))
    few = yaml.safe_load((ROOT / "agent" / "fewshot.yaml").read_text(encoding="utf-8"))
    ev = yaml.safe_load((ROOT / "eval" / "questions.yaml").read_text(encoding="utf-8"))
    return {
        "smoke": [_norm(q["question"]) for q in smoke["questions"]],
        "fewshot": [_norm(p["question"]) for p in few["pairs"]],
        "eval": [_norm(q["question"]) for q in ev["questions"] if q.get("question") != "PENDING_USER"],
    }


def test_no_question_overlap():
    bags = _load_questions()
    pairs = [("smoke", "fewshot"), ("smoke", "eval"), ("fewshot", "eval")]
    for a, b in pairs:
        overlap = set(bags[a]) & set(bags[b])
        assert not overlap, f"Overlap between {a} and {b}: {overlap}"


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9_]+", (text or "").lower()) if len(w) > 2}


def test_max_jaccard_eval_vs_fewshot():
    ev = yaml.safe_load((ROOT / "eval" / "questions.yaml").read_text(encoding="utf-8"))
    few = yaml.safe_load((ROOT / "agent" / "fewshot.yaml").read_text(encoding="utf-8"))
    worst = 0.0
    for q in ev["questions"]:
        tq = _tokens(q["question"])
        for p in few["pairs"]:
            tp = _tokens(p["question"])
            if not tq or not tp:
                continue
            worst = max(worst, len(tq & tp) / len(tq | tp))
    assert worst <= 0.85, worst


def test_dev_no_overlap():
    ev = yaml.safe_load((ROOT / "eval" / "questions.yaml").read_text(encoding="utf-8"))
    few = yaml.safe_load((ROOT / "agent" / "fewshot.yaml").read_text(encoding="utf-8"))
    smoke = yaml.safe_load((ROOT / "agent" / "smoke_questions.yaml").read_text(encoding="utf-8"))
    dev = yaml.safe_load((ROOT / "eval" / "dev_questions.yaml").read_text(encoding="utf-8"))
    bags = {
        "eval": {_norm(q["question"]) for q in ev["questions"]},
        "few": {_norm(p["question"]) for p in few["pairs"]},
        "smoke": {_norm(q["question"]) for q in smoke["questions"]},
        "dev": {_norm(q["question"]) for q in dev["questions"]},
    }
    assert len(dev["questions"]) == 15
    for other in ("eval", "few", "smoke"):
        hit = bags["dev"] & bags[other]
        assert not hit, hit


def test_eval_counts():
    ev = yaml.safe_load((ROOT / "eval" / "questions.yaml").read_text(encoding="utf-8"))
    assert len(ev["questions"]) == 50
    few = yaml.safe_load((ROOT / "agent" / "fewshot.yaml").read_text(encoding="utf-8"))
    assert 15 <= len(few["pairs"]) <= 20
