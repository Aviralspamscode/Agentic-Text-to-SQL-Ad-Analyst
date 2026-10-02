# Results

Numbers below are written by running code. If a later placeholder is missing, it stays `NOT COMPUTED`.

Cost in this dataset is an anonymised scaled unit. Do not format it as currency. New tables use spend share and CPA index only.

- Run date: 2026-10-02
- Command: `uv run python attribution/reallocate.py`
- Warehouse: `warehouse.duckdb`

## Phase 0 — load and profile

### profile_schema

| column_name | data_type |
| --- | --- |
| timestamp | BIGINT |
| uid | BIGINT |
| campaign | BIGINT |
| conversion | INTEGER |
| conversion_timestamp | BIGINT |
| conversion_id | BIGINT |
| attribution | INTEGER |
| click | INTEGER |
| click_pos | INTEGER |
| click_nb | INTEGER |
| cost | DOUBLE |
| cpo | DOUBLE |
| time_since_last_click | BIGINT |
| cat1 | BIGINT |
| cat2 | BIGINT |
| cat3 | BIGINT |
| cat4 | BIGINT |
| cat5 | BIGINT |
| cat6 | BIGINT |
| cat7 | BIGINT |
| cat8 | BIGINT |
| cat9 | BIGINT |


### profile_kpis

| scope | n_impressions | n_campaigns | n_users | n_conversion_ids | share_conversion_1 | share_click_1 | share_attribution_1 | total_cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full | 16468027 | 675 | 6142256 | 435810 | 0.0489552 | 0.361158 | 0.0268656 | 4829.34 |
| sample | 1650244 | 675 | 615245 | 43333 | 0.0483844 | 0.361457 | 0.0266918 | 486.872 |


### profile_touchpoints

| scope | n_converting_journeys | touches_min | touches_median | touches_mean | touches_p95 | touches_max | n_journeys_multi_campaign | share_journeys_multi_campaign | max_campaigns_in_journey |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full | 435810 | 1 | 1 | 1.84988 | 5 | 164 | 2859 | 0.0065602 | 3 |
| sample | 43333 | 1 | 1 | 1.84261 | 5 | 69 | 22 | 0.000507696 | 2 |


### profile_multi_campaign_raw

| scope | n_conversion_ids | n_multi_campaign | share_multi_campaign |
| --- | --- | --- | --- |
| full_no_ts_filter | 435810 | 2859 | 0.0065602 |


### profile_flag_cross

| click | conversion | has_conversion_id | n_impressions |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 10520464 |
| 1 | 0 | 0 | 5141367 |
| 1 | 1 | 1 | 806196 |


### profile_attributed

| n_conversion_ids_with_any_attribution | n_conversion_ids | n_conversion_ids_where_conversion_flag | n_impressions_conversion_1 | n_impressions_attribution_1 |
| --- | --- | --- | --- | --- |
| 236331 | 435810 | 435810 | 806196 | 442424 |


### profile_journey_length_share

| n_converting_journeys | n_single_touch | n_multi_touch | share_multi_touch |
| --- | --- | --- | --- |
| 435810 | 294992 | 140818 | 0.323118 |


### profile_recency

| recency_bucket | n_impressions | share |
| --- | --- | --- |
| <1h | 18194 | 0.227864 |
| 1-24h | 8918 | 0.11169 |
| 1-7d | 22741 | 0.284811 |
| 7-30d | 29993 | 0.375636 |


### profile_cat_unit_screen

| col | n_multi_journeys | share_mixed | n_distinct_all | share_nonnull_nonconverting | meets_unit_rule |
| --- | --- | --- | --- | --- | --- |
| cat9 | 140818 | 0.97065 | 30 | 1 | 1 |
| cat7 | 140818 | 0.453791 | 57196 | 1 | 1 |
| cat8 | 140818 | 0.447145 | 11 | 1 | 1 |
| cat6 | 140818 | 0.445504 | 30 | 1 | 1 |
| cat4 | 140818 | 0.191289 | 21 | 1 | 0 |
| cat3 | 140818 | 0.102643 | 1829 | 1 | 0 |
| cat2 | 140818 | 0.101315 | 70 | 1 | 0 |
| cat1 | 140818 | 0.0830789 | 9 | 1 | 0 |
| cat5 | 140818 | 0.018776 | 51 | 1 | 0 |


### profile_unit_choice

| source_column | bucketing | n_raw_levels | n_unit_levels | share_impr_in_named_levels | n_multi_journeys | share_mixed_after_bucket | mix_threshold | chosen_unit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cat9 | top_14_plus_other | 30 | 15 | 0.943336 | 140818 | 0.961788 | 0.25 | cat9_bucketed |


### unit_level_map

| raw_value | n_impressions | rk | unit |
| --- | --- | --- | --- |
| 29196072 | 8770820 | 1 | 29196072 |
| 8661623 | 1020792 | 2 | 8661623 |
| 8661620 | 946711 | 3 | 8661620 |
| 18291877 | 902988 | 4 | 18291877 |
| 21091108 | 870721 | 5 | 21091108 |
| 21091111 | 858380 | 6 | 21091111 |
| 29520629 | 676929 | 7 | 29520629 |
| 18291872 | 422270 | 8 | 18291872 |
| 29520626 | 419061 | 9 | 29520626 |
| 9491354 | 193322 | 10 | 9491354 |
| 9491351 | 118164 | 11 | 9491351 |
| 15351053 | 116611 | 12 | 15351053 |
| 16022563 | 109069 | 13 | 16022563 |
| 15351056 | 109044 | 14 | 15351056 |
| 6083952 | 106877 | 15 | other |
| 16022558 | 98093 | 16 | other |
| 6083947 | 97077 | 17 | other |
| 21748264 | 96501 | 18 | other |
| 32145478 | 88448 | 19 | other |
| 21748261 | 86745 | 20 | other |
| 32145483 | 84323 | 21 | other |
| 22419790 | 79534 | 22 | other |
| 22419795 | 51537 | 23 | other |
| 23549935 | 49224 | 24 | other |
| 358246 | 28575 | 25 | other |
| 17152695 | 19818 | 26 | other |
| 358249 | 16610 | 27 | other |
| 17152692 | 10527 | 28 | other |
| 6755489 | 10314 | 29 | other |
| 6755486 | 8942 | 30 | other |


### validity_summary

| col | spearman_cpa | n_levels_both_halves | cpa_spread_days_1_15 | cpa_spread_days_16_30 | cpa_spread_observed | cpa_spread_shuffled | mix_observed | mix_shuffled | mean_tv_day | mean_tv_hour | max_unit_hour_share | time_explained | passed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cat9 | 0.992857 | 15 | 3.04275 | 3.49584 | 3.31024 | 1.55771 | 0.961788 | 0.919918 | 0.0186655 | 0.0258144 | 0.100242 | False | True |


### validity_decision

| chosen_column | passed | spearman_cpa | cpa_spread_observed | cpa_spread_shuffled | time_explained | note |
| --- | --- | --- | --- | --- | --- | --- |
| cat9 | True | 0.992857 | 3.31024 | 1.55771 | False | Keep as contextual segment unit |


## Phase 1a — journeys

### journey_stats

| journey_type | n_touches | n_journeys | n_users | mean_touch_count | median_touch_count | share_clicks | spend |
| --- | --- | --- | --- | --- | --- | --- | --- |
| converting | 79846 | 43333 | 32499 | 1.84261 | 1 | 1 | 80.6891 |
| non_converting | 1.47174e+06 | 749278 | 595260 | 1.96422 | 1 | 0.337811 | 344.384 |


### journey_headline

| n_converting_journeys | n_non_converting_journeys | n_journeys_total | n_journeys_thousands | converting_share_clicks |
| --- | --- | --- | --- | --- |
| 435810 | 7482922 | 7918732 | 7918.73 | 1 |


## Phase 1b–1c — attribution on contextual segments

### journeys_converting_stats

| n_touches | n_journeys | share_clicks | n_single_touch_rows_flag | n_multi_touch_journeys | n_single_touch_journeys |
| --- | --- | --- | --- | --- | --- |
| 806196 | 435810 | 1 | 294992 | 140818 | 294992 |


### attr_credit_check

| model | n_conversions | n_bad |
| --- | --- | --- |
| first_touch | 435810 | 0 |
| last_touch | 435810 | 0 |
| linear | 435810 | 0 |
| position | 435810 | 0 |


### attr_compare_headline

| scope | unit_set | n_units | n_over_credited | n_under_credited | max_pct_diff_last_vs_linear | min_pct_diff_last_vs_linear |
| --- | --- | --- | --- | --- | --- | --- |
| all | all_including_other | 15 | 10 | 2 | 0.305591 | -0.135666 |
| multi_touch | all_including_other | 15 | 11 | 3 | 0.413862 | -0.951365 |
| all | named_only | 14 | 9 | 2 | 0.249448 | -0.135666 |
| multi_touch | named_only | 14 | 10 | 3 | 0.361347 | -0.951365 |


### attr_compare_named_top

| scope | unit | pct_diff_last_vs_linear | last_vs_linear_flag |
| --- | --- | --- | --- |
| all | 16022563 | 0.249448 | over_credited |
| multi_touch | 16022563 | 0.361347 | over_credited |


### attr_compare

| scope | unit | first_credit | last_credit | linear_credit | position_credit | pct_diff_last_vs_linear | last_vs_linear_flag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all | other | 13046 | 39615 | 30342.6 | 27811 | 0.305591 | over_credited |
| all | 9491351 | 2257 | 4558 | 3763.6 | 3545.18 | 0.211073 | over_credited |
| all | 15351056 | 1938 | 4216 | 3436.5 | 3206.9 | 0.226829 | over_credited |
| all | 8661623 | 28356 | 30320 | 28788.4 | 29201.3 | 0.053202 | within_10pct |
| all | 18291877 | 29745 | 22883 | 25266.5 | 25900 | -0.0943357 | within_10pct |
| all | 29520629 | 14274 | 24992 | 20912.5 | 20152.8 | 0.195074 | over_credited |
| all | 15351053 | 2197 | 4443 | 3692.35 | 3459.54 | 0.203298 | over_credited |
| all | 29520626 | 9622 | 14834 | 12826.8 | 12490.3 | 0.156481 | over_credited |
| all | 9491354 | 3761 | 7365 | 6057.1 | 5752.31 | 0.215928 | over_credited |
| all | 29196072 | 242687 | 184814 | 208072 | 211356 | -0.11178 | under_credited |
| all | 21091111 | 21806 | 27276 | 24713.2 | 24689.7 | 0.103701 | over_credited |
| all | 18291872 | 14538 | 10328 | 11949.1 | 12230 | -0.135666 | under_credited |
| all | 21091108 | 20708 | 29525 | 25722.9 | 25423.3 | 0.147811 | over_credited |
| all | 8661620 | 29123 | 26110 | 26639.6 | 27274.2 | -0.019879 | within_10pct |
| all | 16022563 | 1752 | 4531 | 3626.4 | 3317.62 | 0.249448 | over_credited |
| multi_touch | 16022563 | 629 | 3408 | 2503.4 | 2194.62 | 0.361347 | over_credited |
| multi_touch | 8661620 | 11762 | 8749 | 9278.57 | 9913.23 | -0.0570743 | within_10pct |
| multi_touch | 21091108 | 9882 | 18699 | 14896.9 | 14597.3 | 0.255229 | over_credited |
| multi_touch | 18291872 | 4663 | 453 | 2074.08 | 2354.97 | -0.78159 | under_credited |
| multi_touch | other | 5108 | 31677 | 22404.6 | 19873 | 0.413862 | over_credited |
| multi_touch | 29196072 | 59062 | 1189 | 24447.4 | 27730.8 | -0.951365 | under_credited |
| multi_touch | 21091111 | 9992 | 15462 | 12899.2 | 12875.7 | 0.198678 | over_credited |
| multi_touch | 8661623 | 12358 | 14322 | 12790.4 | 13203.3 | 0.119746 | over_credited |
| multi_touch | 18291877 | 10947 | 4085 | 6468.54 | 7101.99 | -0.368482 | under_credited |
| multi_touch | 29520626 | 4609 | 9821 | 7813.84 | 7477.33 | 0.256873 | over_credited |
| multi_touch | 15351053 | 1015 | 3261 | 2510.35 | 2277.54 | 0.299021 | over_credited |
| multi_touch | 29520629 | 7090 | 17808 | 13728.5 | 12968.8 | 0.297155 | over_credited |
| multi_touch | 9491354 | 1778 | 5382 | 4074.1 | 3769.31 | 0.321027 | over_credited |
| multi_touch | 9491351 | 1042 | 3343 | 2548.6 | 2330.18 | 0.311698 | over_credited |
| multi_touch | 15351056 | 881 | 3159 | 2379.5 | 2149.9 | 0.327588 | over_credited |


### upper_funnel_check

| unit | spend_share | impression_share | share_first | share_middle | share_last | n_multi_touch_touches | last_credit_multi_touch | linear_credit_multi_touch | pct_diff_multi_touch | last_credit_all | linear_credit_all | pct_diff_all | verified_upper_funnel |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 29196072 | 0.247095 | 0.532597 | 0.971958 | 0.00847513 | 0.0195669 | 60766 | 1189 | 24447.4 | -0.951365 | 184814 | 208072 | -0.11178 | 1 |


### recency_credit_share

| recency_bucket | last_credit | linear_credit | last_share | linear_share |
| --- | --- | --- | --- | --- |
| <1h | 169591 | 146629 | 0.38914 | 0.336451 |
| 1-24h | 56862 | 51559.9 | 0.130474 | 0.118308 |
| 1-7d | 97753 | 105693 | 0.224302 | 0.24252 |
| 7-30d | 111604 | 131929 | 0.256084 | 0.30272 |


### advertiser_gap_overall

| n_criteo_touched_conversions | n_advertiser_credited | share_advertiser_credited |
| --- | --- | --- |
| 435810 | 236331 | 0.54228 |


### advertiser_gap_by_unit

| unit | n_criteo_touched | n_advertiser_credited | share_advertiser_credited | spend_share | cpa_index_advertiser_credited | cpa_index_criteo_touched |
| --- | --- | --- | --- | --- | --- | --- |
| 18291872 | 10328 | 5129 | 0.496611 | 0.0130291 | 0.600349 | 0.54979 |
| 18291877 | 22883 | 11615 | 0.507582 | 0.0299714 | 0.609829 | 0.570809 |
| 8661620 | 26110 | 13446 | 0.514975 | 0.0354175 | 0.622509 | 0.591165 |
| 29196072 | 184814 | 96409 | 0.521654 | 0.247095 | 0.605712 | 0.582674 |
| 8661623 | 30320 | 16204 | 0.534433 | 0.0475969 | 0.694187 | 0.684142 |
| 21091111 | 27276 | 14928 | 0.547294 | 0.0546117 | 0.864579 | 0.872573 |
| 21091108 | 29525 | 16317 | 0.55265 | 0.0813199 | 1.17781 | 1.20034 |
| 29520626 | 14834 | 8451 | 0.569705 | 0.0518656 | 1.45041 | 1.52377 |
| 29520629 | 24992 | 14554 | 0.582346 | 0.109616 | 1.77997 | 1.91148 |
| 15351056 | 4216 | 2459 | 0.583254 | 0.022019 | 2.11621 | 2.27611 |
| 15351053 | 4443 | 2628 | 0.591492 | 0.022456 | 2.01943 | 2.20269 |
| 9491354 | 7365 | 4375 | 0.594026 | 0.0366591 | 1.98027 | 2.16923 |
| 16022563 | 4531 | 2763 | 0.609799 | 0.024065 | 2.05838 | 2.31467 |
| other | 39615 | 24260 | 0.612394 | 0.201959 | 1.9674 | 2.22178 |
| 9491351 | 4558 | 2793 | 0.612769 | 0.0223192 | 1.88855 | 2.13403 |


## Phase 1d — segment economics (shares and CPA index only)

### segment_economics

| period | unit | n_impressions | impression_share | spend_share | linear_conversions | last_conversions | adv_linear_conversions | adv_last_conversions | linear_conv_share | adv_linear_conv_share | cpa_index_linear | cpa_index_last | cpa_index_adv_linear | cpa_index_adv_last | low_confidence_linear | low_confidence_adv_linear |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| days_1_15 | 8661623 | 528554 | 0.063695 | 0.0497585 | 10652.9 | 10343 | 6727.27 | 6576 | 0.0681287 | 0.0662884 | 0.73036 | 0.752247 | 0.750637 | 0.767905 | 0 | 0 |
| days_1_15 | 21091108 | 442726 | 0.0533521 | 0.0817192 | 9796.71 | 10626 | 6351.13 | 6829 | 0.0626528 | 0.0625819 | 1.30432 | 1.20252 | 1.3058 | 1.21442 | 0 | 0 |
| days_16_30 | 15351056 | 56518 | 0.00691789 | 0.0233373 | 2146.61 | 2637 | 1191.24 | 1403 | 0.00768169 | 0.00883407 | 3.03805 | 2.47308 | 2.64174 | 2.24301 | 0 | 0 |
| days_16_30 | 21091111 | 419357 | 0.05133 | 0.053517 | 15514.6 | 17696 | 7938.92 | 8856 | 0.0555194 | 0.058874 | 0.963934 | 0.84511 | 0.909009 | 0.814878 | 0 | 0 |
| days_16_30 | 21091108 | 427995 | 0.0523873 | 0.0809645 | 15926.2 | 18899 | 8298.9 | 9488 | 0.0569922 | 0.0615435 | 1.42062 | 1.19716 | 1.31556 | 1.15069 | 0 | 0 |
| days_16_30 | 8661623 | 492238 | 0.0602507 | 0.0456733 | 18135.5 | 19977 | 8778.37 | 9628 | 0.0648981 | 0.0650992 | 0.703769 | 0.638894 | 0.701595 | 0.639683 | 0 | 0 |
| days_16_30 | 18291872 | 202201 | 0.0247497 | 0.0125223 | 8275.23 | 6992 | 3609.71 | 3052 | 0.0296131 | 0.0267692 | 0.422863 | 0.50047 | 0.467788 | 0.55327 | 0 | 0 |
| days_16_30 | 16022563 | 55867 | 0.00683821 | 0.0245289 | 2196.77 | 2733 | 1281.24 | 1537 | 0.00786118 | 0.00950152 | 3.12026 | 2.50804 | 2.58158 | 2.152 | 0 | 0 |
| days_16_30 | 15351053 | 59859 | 0.00732684 | 0.0234306 | 2275.02 | 2740 | 1272.53 | 1484 | 0.00814121 | 0.00943691 | 2.87803 | 2.38963 | 2.48287 | 2.12906 | 0 | 0 |
| days_16_30 | 29520629 | 342618 | 0.041937 | 0.113096 | 13048.6 | 15892 | 7200.52 | 8527 | 0.0466946 | 0.0533981 | 2.42205 | 1.98869 | 2.11798 | 1.78851 | 0 | 0 |
| days_1_15 | 18291872 | 220069 | 0.0265201 | 0.0135988 | 3673.86 | 3336 | 2283.8 | 2077 | 0.0234954 | 0.0225039 | 0.578784 | 0.637401 | 0.604286 | 0.664454 | 0 | 0 |
| days_1_15 | 16022563 | 53202 | 0.00641127 | 0.0235437 | 1429.64 | 1798 | 1010.25 | 1226 | 0.00914294 | 0.00995465 | 2.57507 | 2.04751 | 2.3651 | 1.94889 | 0 | 0 |
| days_1_15 | 21091111 | 439023 | 0.0529058 | 0.0558418 | 9198.61 | 9580 | 5848.87 | 6072 | 0.0588278 | 0.0576329 | 0.949243 | 0.911452 | 0.968923 | 0.933318 | 0 | 0 |
| days_1_15 | 29520626 | 212497 | 0.0256076 | 0.0515071 | 4968.7 | 5563 | 3249.41 | 3585 | 0.0317763 | 0.0320186 | 1.62093 | 1.44776 | 1.60866 | 1.45808 | 0 | 0 |
| days_1_15 | 9491354 | 93271 | 0.0112399 | 0.0343682 | 2306.52 | 2767 | 1551.78 | 1807 | 0.0147509 | 0.0152907 | 2.32991 | 1.94217 | 2.24765 | 1.93019 | 0 | 0 |
| days_1_15 | 29520629 | 334311 | 0.0402872 | 0.105705 | 7863.94 | 9100 | 5250.12 | 6027 | 0.0502922 | 0.051733 | 2.10181 | 1.81632 | 2.04328 | 1.7799 | 0 | 0 |
| days_1_15 | 15351053 | 56752 | 0.00683908 | 0.0213608 | 1417.33 | 1703 | 966.153 | 1144 | 0.00906426 | 0.00952015 | 2.35659 | 1.96129 | 2.24374 | 1.89493 | 0 | 0 |
| days_1_15 | 18291877 | 472460 | 0.0569353 | 0.0319273 | 8429.42 | 7438 | 5396.79 | 4786 | 0.0539086 | 0.0531782 | 0.592248 | 0.67119 | 0.600383 | 0.677004 | 0 | 0 |
| days_1_15 | 8661620 | 494772 | 0.059624 | 0.03753 | 9637.29 | 8656 | 6041.85 | 5459 | 0.0616333 | 0.0595344 | 0.608925 | 0.677956 | 0.630392 | 0.697699 | 0 | 0 |
| days_16_30 | 29196072 | 4.38368e+06 | 0.536569 | 0.239657 | 135574 | 118106 | 61787.7 | 53443 | 0.485156 | 0.458209 | 0.493979 | 0.567041 | 0.52303 | 0.604697 | 0 | 0 |
| days_16_30 | other | 478970 | 0.0586267 | 0.206926 | 18527.4 | 24142 | 10618.6 | 13543 | 0.0663007 | 0.0787463 | 3.12103 | 2.39518 | 2.62776 | 2.06034 | 0 | 0 |
| days_1_15 | 29196072 | 4.38714e+06 | 0.528686 | 0.255453 | 72498 | 66708 | 46587.7 | 42966 | 0.463646 | 0.45906 | 0.550966 | 0.598787 | 0.556469 | 0.603376 | 0 | 0 |
| days_1_15 | other | 454175 | 0.0547318 | 0.196377 | 11815.2 | 15473 | 8377.59 | 10717 | 0.0755616 | 0.08255 | 2.5989 | 1.98452 | 2.37888 | 1.8596 | 0 | 0 |
| days_16_30 | 18291877 | 430528 | 0.0526973 | 0.0282309 | 16837.1 | 15445 | 7366.63 | 6829 | 0.060252 | 0.0546299 | 0.468548 | 0.51078 | 0.516767 | 0.55745 | 0 | 0 |
| days_16_30 | 8661620 | 451939 | 0.055318 | 0.0335377 | 17002.3 | 17454 | 7728.48 | 7987 | 0.060843 | 0.0573133 | 0.551217 | 0.536951 | 0.585164 | 0.566223 | 0 | 0 |
| days_1_15 | 9491351 | 56716 | 0.00683474 | 0.0207727 | 1387 | 1695 | 971.317 | 1158 | 0.00887028 | 0.00957104 | 2.34183 | 1.9163 | 2.17037 | 1.82048 | 0 | 0 |
| days_16_30 | 29520626 | 206564 | 0.0252838 | 0.0521845 | 7858.14 | 9271 | 4259.97 | 4866 | 0.0281205 | 0.0315914 | 1.85575 | 1.57294 | 1.65186 | 1.44613 | 0 | 0 |
| days_16_30 | 9491354 | 100051 | 0.0122464 | 0.0386976 | 3750.58 | 4598 | 2141.13 | 2568 | 0.0134215 | 0.0158783 | 2.88325 | 2.35186 | 2.43714 | 2.03202 | 0 | 0 |
| days_1_15 | 15351056 | 52526 | 0.00632981 | 0.0205374 | 1289.89 | 1579 | 870.965 | 1056 | 0.00824925 | 0.0085822 | 2.48961 | 2.03378 | 2.39302 | 1.97371 | 0 | 0 |
| days_16_30 | 9491351 | 61448 | 0.00752133 | 0.0236953 | 2376.6 | 2863 | 1372.06 | 1635 | 0.00850473 | 0.010175 | 2.78613 | 2.3128 | 2.32878 | 1.95426 | 0 | 0 |
| full | other | 933145 | 0.056664 | 0.201959 | 30342.6 | 39615 | 18996.2 | 24260 | 0.0696234 | 0.0803797 | 2.90073 | 2.22178 | 2.51256 | 1.9674 | 0 | 0 |
| full | 8661623 | 1.02079e+06 | 0.0619863 | 0.0475969 | 28788.4 | 30320 | 15505.6 | 16204 | 0.0660572 | 0.0656099 | 0.72054 | 0.684142 | 0.725453 | 0.694187 | 0 | 0 |
| full | 16022563 | 109069 | 0.00662308 | 0.024065 | 3626.4 | 4531 | 2291.49 | 2763 | 0.00832106 | 0.00969611 | 2.89206 | 2.31467 | 2.48193 | 2.05838 | 0 | 0 |
| full | 18291877 | 902988 | 0.0548328 | 0.0299714 | 25266.5 | 22883 | 12763.4 | 11615 | 0.057976 | 0.0540065 | 0.516962 | 0.570809 | 0.554959 | 0.609829 | 0 | 0 |
| full | 21091108 | 870721 | 0.0528734 | 0.0813199 | 25722.9 | 29525 | 14650 | 16317 | 0.0590232 | 0.0619894 | 1.37776 | 1.20034 | 1.31183 | 1.17781 | 0 | 0 |
| full | 18291872 | 422270 | 0.0256418 | 0.0130291 | 11949.1 | 10328 | 5893.52 | 5129 | 0.0274181 | 0.0249376 | 0.475202 | 0.54979 | 0.522471 | 0.600349 | 0 | 0 |
| full | 15351053 | 116611 | 0.00708105 | 0.022456 | 3692.35 | 4443 | 2238.68 | 2628 | 0.00847239 | 0.00947266 | 2.6505 | 2.20269 | 2.37062 | 2.01943 | 0 | 0 |
| full | 29520629 | 676929 | 0.0411057 | 0.109616 | 20912.5 | 24992 | 12450.6 | 14554 | 0.0479854 | 0.0526831 | 2.28436 | 1.91148 | 2.08067 | 1.77997 | 0 | 0 |
| full | 29520626 | 419061 | 0.0254469 | 0.0518656 | 12826.8 | 14834 | 7509.38 | 8451 | 0.0294322 | 0.0317748 | 1.76221 | 1.52377 | 1.63228 | 1.45041 | 0 | 0 |
| full | 9491354 | 193322 | 0.0117392 | 0.0366591 | 6057.1 | 7365 | 3692.91 | 4375 | 0.0138985 | 0.015626 | 2.63763 | 2.16923 | 2.34603 | 1.98027 | 0 | 0 |
| full | 8661620 | 946711 | 0.0574878 | 0.0354175 | 26639.6 | 26110 | 13770.3 | 13446 | 0.0611266 | 0.0582671 | 0.579413 | 0.591165 | 0.607848 | 0.622509 | 0 | 0 |
| full | 21091111 | 858380 | 0.052124 | 0.0546117 | 24713.2 | 27276 | 13787.8 | 14928 | 0.0567064 | 0.058341 | 0.96306 | 0.872573 | 0.936076 | 0.864579 | 0 | 0 |
| full | 29196072 | 8.77082e+06 | 0.532597 | 0.247095 | 208072 | 184814 | 108375 | 96409 | 0.477438 | 0.458575 | 0.517543 | 0.582674 | 0.538832 | 0.605712 | 0 | 0 |
| full | 15351056 | 109044 | 0.00662156 | 0.022019 | 3436.5 | 4216 | 2062.2 | 2459 | 0.00788532 | 0.00872591 | 2.7924 | 2.27611 | 2.5234 | 2.11621 | 0 | 0 |
| full | 9491351 | 118164 | 0.00717536 | 0.0223192 | 3763.6 | 4558 | 2343.37 | 2793 | 0.00863588 | 0.00991564 | 2.58447 | 2.13403 | 2.25091 | 1.88855 | 0 | 0 |


## Phase 1e — out-of-sample reallocation

### reallocation_headline

| outcome | chosen_x | dr | recv_cap | donor_cap | allow_other_donor | oos_uplift | insample_uplift | n_donors | n_receivers | donors | receivers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| adv_linear_PRIMARY | 0.2 | 1.25 | 0.5 | 0.5 | True | 0.182496 | 0.181015 | 7 | 6 | 15351056,other,16022563,9491354,15351053,9491351,29520629 | 29196072,18291877,18291872,8661620,8661623,21091111 |
| adv_linear_NO_DONOR_CAP_SENSITIVITY | 0.2 | 1.25 | 0.5 | 1 | True | 0.188958 | 0.185047 | 2 | 6 | 15351056,other | 29196072,18291877,18291872,8661620,8661623,21091111 |
| adv_linear_NO_OTHER_SENSITIVITY | 0.15 | 1.25 | 0.5 | 0.5 | False | 0.137303 | 0.136411 | 8 | 3 | 15351056,16022563,9491354,15351053,9491351,29520629,29520626,21091108 | 29196072,18291877,18291872 |
| all_linear | 0.2 | 1.25 | 0.5 | 0.5 | True | 0.210674 | 0.190695 | 7 | 6 | 15351056,other,16022563,9491354,15351053,9491351,29520629 | 29196072,18291877,18291872,8661620,8661623,21091111 |
| adv_last_SENSITIVITY | 0.2 | 1.25 | 0.5 | 0.5 | True | 0.138569 | 0.141248 | 7 | 6 | 15351056,other,16022563,9491354,15351053,9491351,29520629 | 29196072,18291877,18291872,8661620,8661623,21091111 |


### reallocation_plan

| unit | role | chosen_x | recv_cap | donor_cap | spend_frac_change |
| --- | --- | --- | --- | --- | --- |
| 15351056 | donor | 0.2 | 0.5 | 0.5 | 0.5 |
| other | donor | 0.2 | 0.5 | 0.5 | 0.5 |
| 16022563 | donor | 0.2 | 0.5 | 0.5 | 0.5 |
| 9491354 | donor | 0.2 | 0.5 | 0.5 | 0.5 |
| 15351053 | donor | 0.2 | 0.5 | 0.5 | 0.5 |
| 9491351 | donor | 0.2 | 0.5 | 0.5 | 0.5 |
| 29520629 | donor | 0.2 | 0.5 | 0.5 | 0.392794 |
| 29196072 | receiver | 0.2 | 0.5 | 0.5 | 0.5 |
| 18291877 | receiver | 0.2 | 0.5 | 0.5 | 0.5 |
| 18291872 | receiver | 0.2 | 0.5 | 0.5 | 0.5 |
| 8661620 | receiver | 0.2 | 0.5 | 0.5 | 0.5 |
| 8661623 | receiver | 0.2 | 0.5 | 0.5 | 0.5 |
| 21091111 | receiver | 0.2 | 0.5 | 0.5 | 0.105052 |


### reallocation_scenarios

| x | dr | recv_cap | donor_cap | chosen | oos_uplift | insample_uplift |
| --- | --- | --- | --- | --- | --- | --- |
| 0.05 | 1.25 | 0.5 | 0.5 | False | 0.0513994 | 0.050889 |
| 0.1 | 1.25 | 0.5 | 0.5 | False | 0.103098 | 0.101752 |
| 0.15 | 1.25 | 0.5 | 0.5 | False | 0.15294 | 0.149422 |
| 0.2 | 1.25 | 0.5 | 0.5 | True | 0.182496 | 0.181015 |


### reallocation_sensitivity

| x | dr | recv_cap | donor_cap | fits_first_half | is_primary_choice | oos_uplift_adv_linear | insample_uplift_adv_linear | oos_uplift_all_linear |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.05 | 1 | 0.25 | 0.5 | True | False | 0.0693365 | 0.0688594 | 0.0777051 |
| 0.05 | 1 | 0.5 | 0.5 | True | False | 0.0693365 | 0.0688594 | 0.0777051 |
| 0.05 | 1 | 1 | 0.5 | True | False | 0.0693365 | 0.0688594 | 0.0777051 |
| 0.05 | 1.25 | 0.25 | 0.5 | True | False | 0.0513994 | 0.050889 | 0.0587131 |
| 0.05 | 1.25 | 0.5 | 0.5 | True | False | 0.0513994 | 0.050889 | 0.0587131 |
| 0.05 | 1.25 | 1 | 0.5 | True | False | 0.0513994 | 0.050889 | 0.0587131 |
| 0.05 | 1.5 | 0.25 | 0.5 | True | False | 0.0394413 | 0.0389087 | 0.0460517 |
| 0.05 | 1.5 | 0.5 | 0.5 | True | False | 0.0394413 | 0.0389087 | 0.0460517 |
| 0.05 | 1.5 | 1 | 0.5 | True | False | 0.0394413 | 0.0389087 | 0.0460517 |
| 0.1 | 1 | 0.25 | 0.5 | True | False | 0.128199 | 0.126157 | 0.143971 |
| 0.1 | 1 | 0.5 | 0.5 | True | False | 0.138972 | 0.137693 | 0.155784 |
| 0.1 | 1 | 1 | 0.5 | True | False | 0.138972 | 0.137693 | 0.155784 |
| 0.1 | 1.25 | 0.25 | 0.5 | True | False | 0.0944792 | 0.0925237 | 0.10835 |
| 0.1 | 1.25 | 0.5 | 0.5 | True | False | 0.103098 | 0.101752 | 0.1178 |
| 0.1 | 1.25 | 1 | 0.5 | True | False | 0.103098 | 0.101752 | 0.1178 |
| 0.1 | 1.5 | 0.25 | 0.5 | True | False | 0.0719995 | 0.0701012 | 0.084602 |
| 0.1 | 1.5 | 0.5 | 0.5 | True | False | 0.0791819 | 0.0777919 | 0.0924774 |
| 0.1 | 1.5 | 1 | 0.5 | True | False | 0.0791819 | 0.0777919 | 0.0924774 |
| 0.15 | 1 | 0.25 | 0.5 | True | False | 0.144237 | 0.142145 | 0.160368 |
| 0.15 | 1 | 0.5 | 0.5 | True | False | 0.206708 | 0.202734 | 0.233961 |
| 0.15 | 1 | 1 | 0.5 | True | False | 0.206925 | 0.205729 | 0.232396 |
| 0.15 | 1.25 | 0.25 | 0.5 | True | False | 0.102963 | 0.100951 | 0.117798 |
| 0.15 | 1.25 | 0.5 | 0.5 | True | False | 0.15294 | 0.149422 | 0.176672 |
| 0.15 | 1.25 | 1 | 0.5 | True | False | 0.153113 | 0.151818 | 0.17542 |
| 0.15 | 1.5 | 0.25 | 0.5 | True | False | 0.0754474 | 0.0734878 | 0.0894173 |
| 0.15 | 1.5 | 0.5 | 0.5 | True | False | 0.117095 | 0.11388 | 0.138479 |
| 0.15 | 1.5 | 1 | 0.5 | True | False | 0.117239 | 0.115877 | 0.137436 |
| 0.2 | 1 | 0.25 | 0.5 | False | False | nan | nan | nan |
| 0.2 | 1 | 0.5 | 0.5 | True | False | 0.249935 | 0.248282 | 0.281917 |
| 0.2 | 1 | 1 | 0.5 | True | False | 0.271482 | 0.271354 | 0.305543 |
| 0.2 | 1.25 | 0.25 | 0.5 | False | False | nan | nan | nan |
| 0.2 | 1.25 | 0.5 | 0.5 | True | True | 0.182496 | 0.181015 | 0.210674 |
| 0.2 | 1.25 | 1 | 0.5 | True | False | 0.199734 | 0.199472 | 0.229575 |
| 0.2 | 1.5 | 0.25 | 0.5 | False | False | nan | nan | nan |
| 0.2 | 1.5 | 0.5 | 0.5 | True | False | 0.137536 | 0.13617 | 0.163179 |
| 0.2 | 1.5 | 1 | 0.5 | True | False | 0.151901 | 0.151551 | 0.17893 |


## Placeholder tracker

| ID | Placeholder | Value | Produced by |
| --- | --- | --- | --- |
| P1.1 | distinct campaigns | 675 (full `profile_kpis.n_campaigns`) | `sql/01_profile.sql` |
| P1.2 | user journeys (K) | 7.9M (435810 converting + 7482922 non-converting) | `sql/02b_journey_counts_full.sql` (full counts); `sql/02_journeys.sql` (sample table) |
| P1.3 | last-touch over-credits named **contextual segments** | named contextual segments; multi-touch: 10 over-credited by up to 36.1%; all conversions: 9 over-credited by up to 24.9% (`other` kept in tables, excluded from this headline) | `sql/07_attr_compare.sql` |
| P1.4 | spend shifted | 20% of spend (chosen on days 1–15; receiver cap +50%, donor cap −50%) | `attribution/reallocate.py` (X chosen on days 1–15) |
| P1.5 | conversion uplift (primary = OOS advertiser-credited linear) | primary OOS (days 16–30, advertiser-credited linear) +18.25%; in-sample comparison +18.10% | `attribution/reallocate.py` |
| P1.6 | Power BI pages | NOT COMPUTED | built manually after `POWERBI_SPEC.md` |
| P1.7 | advertiser-credited share + max gap across contextual segments | 54.23% (236331 / 435810); contextual-segment credited share ranges 49.7%–61.3% (max gap 11.6 pp) | `sql/07_attr_compare.sql` |
| P1.8 | last-touch under-credits largest upper-funnel segment | last-touch under-credits the largest upper-funnel contextual segment by 95.1% on multi-touch (spend share 24.7%; first-touch share 97.2% vs last 2.0%) | `sql/07_attr_compare.sql` (`upper_funnel_check`) |
| P2.1 | LLM API | GPT-4o-mini (primary, config D). Comparison: GPT-4o (config F, same graph as E) | `.env` `LLM_MODEL=gpt-4o-mini`; F forced `gpt-4o` |
| P2.2 | eval set size | 50 verified | `eval/questions.yaml` |
| P2.3 | execution accuracy | A 42.0% → D 52.0% (after `key_columns` rescore; no LLM re-run) | `eval/run_eval.py` 3× temp 0; `eval/rescore.py` |
| P2.4 | failure cases | 24 majority-fail items on primary config D | `eval/results/summary.md` taxonomy (`other` = 0) |
| P2.5 | median latency | 3029 ms (config D) | `eval/results/eval.jsonl` |
| P2.6 | cost per query | INR 0.0461 (config D, gpt-4o-mini $0.15/$0.60 per 1M, USDINR 96.33) | `eval/pricing.yaml` × logged tokens |
| P2.F | comparison (not the resume primary) | F accuracy 61.3%; INR 1.1691 / query (gpt-4o $2.50/$10.00) | `eval/results/eval.jsonl` |

## Final resume bullets

Numbers below are the same values as the tracker. Do not round a second time.

- Modelled 16.5M Criteo impressions across **675** campaigns and **7.9M** user journeys (436K converting). Last-touch over-credits **9** named contextual segments by up to **24.9%** vs linear (10 / 36.1% on multi-touch only).
- Shifted **20%** of spend from high-CPA to low-CPA segments (caps ±50%, chosen on days 1–15). Projects **+18.25%** advertiser-credited linear conversions out-of-sample at flat budget (diminishing-returns factor 1.25).
- Built a read-only LangGraph text-to-SQL agent (GPT-4o-mini). On a **50**-question eval, execution accuracy **42.0% → 52.0%** (schema-only → calibrated config D); median **3.0s**, **₹0.046**/query. GPT-4o comparison: 61.3% at ₹1.17/query.
