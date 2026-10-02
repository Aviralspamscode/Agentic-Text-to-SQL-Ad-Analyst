from eval.run_eval import classify_failure


def test_wrong_status_not_other():
    item = {
        "id": "A03",
        "question": "What is our ROAS in rupees?",
        "gold_sql": "NOT_IN_DATA",
        "grade": "status",
        "gold_status": ["NOT_IN_DATA"],
    }
    assert classify_failure(item, "REFUSE", "REFUSED", "status_mismatch") == "wrong_status"


def test_answered_ambiguous_is_not_flagged():
    item = {
        "id": "A01",
        "question": "Which campaign is best?",
        "gold_sql": "NEEDS_CLARIFICATION",
        "grade": "status",
        "gold_status": ["NEEDS_CLARIFICATION", "ANSWERED"],
    }
    assert (
        classify_failure(item, "SELECT 1", "ANSWERED", "missing_assumption")
        == "ambiguity_not_flagged"
    )
