import pandas as pd

from eval.compare import match_results


def test_extra_columns_pass():
    gold = pd.DataFrame({"share": [0.36]})
    pred = pd.DataFrame({"click_rate": [0.36], "n": [100]})
    ok, rule = match_results(pred, gold, "What fraction of displays were clicked?")
    assert ok
    assert "extra_columns" in rule
    assert "unordered" in rule


def test_percentage_scale_pass():
    gold = pd.DataFrame({"share": [0.361158]})
    pred = pd.DataFrame({"pct": [36.1158]})
    ok, rule = match_results(pred, gold, "What fraction of displays were clicked?")
    assert ok
    assert "percent_scale" in rule


def test_wrong_row_count_fail():
    gold = pd.DataFrame({"unit": ["a", "b"], "share": [0.2, 0.3]})
    pred = pd.DataFrame({"unit": ["a"], "share": [0.2]})
    ok, rule = match_results(pred, gold, "Break it down by segment.")
    assert not ok
    assert rule == "row_count_mismatch"


def test_wrong_value_fail():
    gold = pd.DataFrame({"n": [675]})
    pred = pd.DataFrame({"n": [700]})
    ok, rule = match_results(pred, gold, "How many campaigns ran?")
    assert not ok
    assert rule == "value_mismatch"


def test_key_columns_ignore_informational():
    gold = pd.DataFrame({"unit": ["15351056"], "cpa_index_adv_linear": [2.52]})
    pred = pd.DataFrame({"segment": ["15351056"], "cpa": [99.0]})
    ok, rule = match_results(
        pred,
        gold,
        "Which specific segment is most expensive?",
        key_columns=["unit"],
    )
    assert ok
    assert "key_columns" in rule
    ok_full, _ = match_results(pred, gold, "Which specific segment is most expensive?")
    assert not ok_full
