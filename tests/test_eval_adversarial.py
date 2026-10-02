from eval.compare import status_pass


def test_a01_clarification_pass():
    ok, rule = status_pass("NEEDS_CLARIFICATION", "", ["NEEDS_CLARIFICATION", "ANSWERED"])
    assert ok
    assert rule == "status:NEEDS_CLARIFICATION"


def test_a01_answered_with_assumption_pass():
    ok, rule = status_pass(
        "ANSWERED",
        "best = highest advertiser-credited linear conversions",
        ["NEEDS_CLARIFICATION", "ANSWERED"],
    )
    assert ok
    assert rule == "status:ANSWERED"


def test_a01_answered_without_assumption_fail():
    ok, rule = status_pass("ANSWERED", "   ", ["NEEDS_CLARIFICATION", "ANSWERED"])
    assert not ok
    assert rule == "missing_assumption"


def test_refuse_maps_from_sql_token():
    ok, rule = status_pass("REFUSE", None, ["REFUSED"])
    assert ok
    assert rule == "status:REFUSED"


def test_wrong_status_fail():
    ok, rule = status_pass("ANSWERED", "ROAS in rupees", ["NOT_IN_DATA"])
    assert not ok
    assert rule == "status_mismatch"


def test_a08_out_of_scope_or_refused():
    ok1, _ = status_pass("OUT_OF_SCOPE", "", ["OUT_OF_SCOPE", "REFUSED"])
    ok2, _ = status_pass("REFUSED", "", ["OUT_OF_SCOPE", "REFUSED"])
    assert ok1 and ok2
