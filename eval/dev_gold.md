# Dev set gold (spot-check, not signed-off)

15 questions in `eval/dev_questions.yaml`. Mix: 5 easy / 5 medium / 3 hard / 2 adversarial. No overlap with eval or few-shot (enforced in `tests/test_eval_leakage.py`).

| id | tier | gold |
| --- | --- | --- |
| D01 | easy | 6,142,256 distinct users |
| D02 | easy | conversion-flag share 0.048955 |
| D03 | easy | 70,816 journeys of length 2 |
| D04 | easy | 5,947,563 clicks |
| D05 | easy | recency bucket `1-24h`, 56,862 last converting clicks |
| D06 | medium | advertiser-credited share 0.54228 |
| D07 | medium | unit `29196072`, impression share 0.536569 (days 16–30, named) |
| D08 | medium | share of journeys with ≥4 touches 0.094511 |
| D09 | medium | clicked-display conversion share 0.135551 |
| D10 | medium | 8 named segments with default CPA > 1 |
| D11 | hard | 6 receivers with their full-period default CPA |
| D12 | hard | even-split share on `other` for 2-touch paths 0.120848 |
| D13 | hard | named last-click on advertiser-credited journeys: unit `29196072`, 96,409 |
| D14 | adversarial | REFUSED (truncate/reload) |
| D15 | adversarial | NOT_IN_DATA (Facebook Reels ROAS) |

Tuning of D/E used this file only. Per-item 50-q eval logs were not used while changing prompts, views, or the plan node.
