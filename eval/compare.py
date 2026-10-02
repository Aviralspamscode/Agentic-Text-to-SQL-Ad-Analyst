"""Result comparator for the eval harness.

Gold columns may appear under any predicted name. Extra predicted columns are
allowed. Shares and percentages (×100) match within relative tolerance 1e-6.
"""

from __future__ import annotations

import math
import re
from itertools import combinations, permutations

import pandas as pd

REL_TOL = 1e-6

STATUSES = (
    "ANSWERED",
    "NEEDS_CLARIFICATION",
    "NOT_IN_DATA",
    "REFUSED",
    "OUT_OF_SCOPE",
)

SQL_STATUS = {
    "REFUSE": "REFUSED",
    "REFUSED": "REFUSED",
    "UNKNOWN": "NOT_IN_DATA",
    "NOT_IN_DATA": "NOT_IN_DATA",
    "NEEDS_CLARIFICATION": "NEEDS_CLARIFICATION",
    "OUT_OF_SCOPE": "OUT_OF_SCOPE",
}


def asks_ordering(question: str) -> bool:
    q = question.lower()
    return bool(
        re.search(
            r"\b(top|rank|ranking|order|highest|lowest|least|most|"
            r"largest|smallest|biggest|cheapest|expensive|flatter)\b",
            q,
        )
    )


def _as_number(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    if isinstance(v, bool):
        return float(v)
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if s.endswith("%"):
        try:
            return float(s[:-1])
        except ValueError:
            return None
    try:
        return float(s)
    except ValueError:
        return None


def cells_equivalent(gold_v, pred_v) -> tuple[bool, bool]:
    """Return (match, used_percent_scale)."""
    gn = _as_number(gold_v)
    pn = _as_number(pred_v)
    if gn is None and pn is None:
        return str(gold_v) == str(pred_v), False
    if gn is None or pn is None:
        return str(gold_v) == str(pred_v), False
    scale = max(abs(gn), abs(pn), 1e-12)
    if abs(gn - pn) / scale <= REL_TOL or abs(gn - pn) <= 1e-12:
        return True, False
    if abs(pn - 100.0 * gn) / max(abs(100.0 * gn), 1e-12) <= REL_TOL:
        return True, True
    if abs(gn - 100.0 * pn) / max(abs(100.0 * pn), 1e-12) <= REL_TOL:
        return True, True
    return False, False


def _rows_equivalent(grow: tuple, prow: tuple) -> tuple[bool, bool]:
    used_pct = False
    for gv, pv in zip(grow, prow, strict=True):
        ok, pct = cells_equivalent(gv, pv)
        if not ok:
            return False, False
        used_pct = used_pct or pct
    return True, used_pct


def match_results(
    pred: pd.DataFrame | None,
    gold: pd.DataFrame | None,
    question: str,
    key_columns: list[str] | None = None,
) -> tuple[bool, str]:
    if pred is None or gold is None:
        return False, "missing_frame"
    if key_columns:
        missing = [c for c in key_columns if c not in gold.columns]
        if missing:
            return False, "missing_key_columns_in_gold"
        gold = gold.loc[:, list(key_columns)].copy()
    if len(pred) != len(gold):
        return False, "row_count_mismatch"
    if gold.shape[1] == 0:
        return True, "empty_gold"
    if pred.shape[1] < gold.shape[1]:
        return False, "missing_columns"

    ordered = asks_ordering(question)
    gcols = list(gold.columns)
    pcols = list(pred.columns)
    gvals = gold.to_numpy()

    for chosen in combinations(pcols, len(gcols)):
        for perm in permutations(chosen):
            pvals = pred.loc[:, list(perm)].to_numpy()
            if ordered:
                used_pct = False
                ok = True
                for i in range(len(gold)):
                    row_ok, pct = _rows_equivalent(tuple(gvals[i]), tuple(pvals[i]))
                    if not row_ok:
                        ok = False
                        break
                    used_pct = used_pct or pct
                if ok:
                    return True, _rule(
                        ordered, len(pcols) > len(gcols), used_pct, bool(key_columns)
                    )
            else:
                used = [False] * len(pred)
                used_pct = False
                ok = True
                for i in range(len(gold)):
                    found = False
                    for j in range(len(pred)):
                        if used[j]:
                            continue
                        row_ok, pct = _rows_equivalent(tuple(gvals[i]), tuple(pvals[j]))
                        if row_ok:
                            used[j] = True
                            used_pct = used_pct or pct
                            found = True
                            break
                    if not found:
                        ok = False
                        break
                if ok:
                    return True, _rule(
                        ordered, len(pcols) > len(gcols), used_pct, bool(key_columns)
                    )
    return False, "value_mismatch"


def normalize_status(raw: str | None) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip().upper().replace(" ", "_")
    if s in SQL_STATUS:
        return SQL_STATUS[s]
    if s in STATUSES:
        return s
    return None


def status_pass(
    pred_status: str | None,
    pred_assumption: str | None,
    allowed: list[str] | str,
    *,
    require_assumption_if_answered: bool = True,
) -> tuple[bool, str]:
    got = normalize_status(pred_status)
    allow = [normalize_status(x) for x in ([allowed] if isinstance(allowed, str) else allowed)]
    allow = [x for x in allow if x]
    if got not in allow:
        return False, "status_mismatch"
    if got == "ANSWERED" and require_assumption_if_answered and not str(pred_assumption or "").strip():
        return False, "missing_assumption"
    return True, f"status:{got}"


def _rule(ordered: bool, extra: bool, percent: bool, key_cols: bool = False) -> str:
    parts = ["ordered" if ordered else "unordered"]
    if extra:
        parts.append("extra_columns")
    if percent:
        parts.append("percent_scale")
    if key_cols:
        parts.append("key_columns")
    return "+".join(parts)
