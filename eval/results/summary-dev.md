# Eval summary

Tuning of D/E/F used `eval/dev_questions.yaml` only. Per-item eval logs were not used while changing prompts, views, or the plan node.

## Accuracy by config (3 runs)
- **D**: mean 73.3% (min 73.3%, max 73.3%)
- **E**: mean 66.7% (min 66.7%, max 66.7%)

## Accuracy by tier (mean across runs, all configs)
### Config D
- adversarial: 100.0%
- easy: 100.0%
- hard: 33.3%
- medium: 60.0%

### Config E
- adversarial: 100.0%
- easy: 100.0%
- hard: 33.3%
- medium: 40.0%

## Best config: D
- Median latency: 2799 ms; p90 3577 ms
- Mean tokens in/out: 2228 / 94
- Mean cost per query: INR 0.0376
- Repair rescues: 1/1 (100.0% of repaired)

## Failure taxonomy (best config, majority-fail items)
P2.4 scope: best config (D), 4 items.
- other: 2
- wrong_metric_definition: 2

### Examples
- **D09** `other` rule=value_mismatch
  SQL: `SELECT * FROM (SELECT COUNT(DISTINCT conversion_id) * 1.0 / SUM(click) AS share_later_convert FROM impressions WHERE click = 1) AS _q LIMIT 1000`
- **D10** `wrong_metric_definition` rule=value_mismatch
  SQL: `SELECT * FROM (SELECT COUNT(*) AS n_segments FROM v_segment_cpa_default WHERE period = 'full' AND cpa > 1) AS _q LIMIT 1000`
- **D11** `wrong_metric_definition` rule=row_count_mismatch
  SQL: `SELECT * FROM (SELECT CAST(r.unit AS TEXT) AS unit, v.cpa FROM reallocation_plan AS r JOIN v_segment_cpa_default AS v ON r.unit = v.unit WHERE v.period = 'full') AS _q LIMIT 1000`
