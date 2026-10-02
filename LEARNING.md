# Learning log

Numbers in this file come from `sql/00_load.sql` and `sql/01_profile.sql`, written into `warehouse.duckdb` and dumped in `RESULTS.md` on 2026-10-02. If a claim has no query behind it, it is not a number.

---

## `sql/00_load.sql` — what it does and why

**What.** Reads `data/raw/criteo_attribution_dataset.tsv.gz` into table `impressions`, then copies every row for a deterministic 10% of users into `impressions_sample` (`hash(uid) % 10 = 0`).

**Why.** The raw file is one row per display. We need the full table for final resume numbers, and a stable sample so development is fast and repeatable. Hashing the user id (not the row) keeps a user's whole history together.

**What we found when we inspected the file.** The TSV **has a header row**. The first line is `timestamp uid campaign ... cat9`. Load uses `header = true` and explicit types so DuckDB does not guess.

**Measured load facts** (`profile_kpis`):

| scope | impressions | campaigns | users |
| --- | --- | --- | --- |
| full | 16,468,027 | 675 | 6,142,256 |
| sample | 1,650,244 | 675 | 615,245 |

The sample is 10.02% of impressions and 10.02% of users. All 675 campaigns still appear in the sample.

Criteo's page says "16.5M impressions, 45K conversions, 700 campaigns". We matched the impression count. We measured **675 campaigns**, not 700. We measured **435,810 distinct `conversion_id`s**, not 45K. We do not overwrite our query with their marketing numbers. Possible reasons for 45K: a different filter in the paper, a rounded figure from an older dump, or a different definition of "conversion". `NOT USED` for resume until we define journeys in Phase 1.

### Interview questions

1. **Why hash the user, not a random 10% of rows?**  
   A user journey is several rows. Row sampling would split journeys and bias touch counts. User-level hashing keeps journeys intact and is deterministic.

2. **Why keep types explicit instead of `read_csv_auto`?**  
   Auto-detect can promote ids to strings or floats. Attribution joins break if `campaign` or `conversion_id` types drift. Explicit `BIGINT` / `INTEGER` / `DOUBLE` matches the file we peeked.

3. **What does `hash(uid) % 10 = 0` assume?**  
   That DuckDB's hash is stable for a given build and that user ids are well distributed. We checked after the fact: sample share ≈ 10%, so the hash is not collapsing onto a few users.

---

## `sql/01_profile.sql` — what it does and why

**What.** Inspects schema, volume, conversion/click/attribution rates, journey length, whether one `conversion_id` spans many campaigns, and whether a converting journey mixes `cat1` or recency.

**Why.** The resume claims "N campaigns" and later "last-touch over-credits N campaigns/segments". If almost every journey is a single campaign, comparing attribution **across campaigns** is a no-op: first, last, linear, and position-based all give that campaign 100%.

### Schema

All expected columns are present, types as loaded:

`timestamp, uid, campaign, conversion, conversion_timestamp, conversion_id, attribution, click, click_pos, click_nb, cost, cpo, time_since_last_click, cat1 … cat9`.

### Rates (full table)

- `conversion = 1` on **4.896%** of impressions (806,196 rows).
- `click = 1` on **36.116%**.
- `attribution = 1` on **2.687%** (442,424 rows).

`profile_flag_cross` is the important one:

| click | conversion | has conversion_id | rows |
| --- | --- | --- | --- |
| 0 | 0 | no | 10,520,464 |
| 1 | 0 | no | 5,141,367 |
| 1 | 1 | yes | 806,196 |

There is **no other combination**. In this dump:

- Views never convert and never carry a `conversion_id`.
- `conversion = 1` if and only if `conversion_id <> -1`.
- Every converting touch is a click.

So a "converting journey" is a sequence of **clicked** impressions that share a `conversion_id`, not a mix of views and clicks.

`attribution` is Criteo's flag for "the advertiser gave Criteo the last-touch (or their rule) on this conversion". **236,331 / 435,810 = 54.23%** of conversion ids have at least one row with `attribution = 1`. That is a preview of the Phase 1 bonus: Criteo "touched" every conversion in this file (every converting row is a Criteo impression); the advertiser credited Criteo on about half of those conversion ids.

### Journey length (impressions with the same `conversion_id`, `timestamp <= conversion_timestamp`)

| stat | full |
| --- | --- |
| converting journeys | 435,810 |
| min / median / mean / p95 / max touches | 1 / 1 / 1.850 / 5 / 164 |
| single-touch | 294,992 (67.7%) |
| multi-touch | 140,818 (32.3%) |

Attribution models only disagree on the 32.3% that have two or more touches.

### Critical check: do journeys span campaigns?

| | count | share |
| --- | --- | --- |
| converting journeys with **>1 campaign** | 2,859 | **0.656%** |
| max campaigns on one conversion_id | 3 | |

Same result with or without the timestamp filter. **Campaign-level last-touch vs linear is meaningless for 99.34% of conversions.** I recommend we do **not** use campaign as the attribution unit for P1.3.

The 10% user sample only saw 22 multi-campaign journeys (0.05%). Rare events are under-represented in a user sample; the decision uses the **full** table.

### Candidate segments

`cat1` has **9** distinct values on the sample (already ≤ 15; no `other` bucket needed). `cat8` has 11, `cat4` has 17. `cat7` has 25,554 — too wide.

Recency of converting touches on the sample:

| bucket | share of converting sample touches |
| --- | --- |
| <1h | 22.8% |
| 1–24h | 11.2% |
| 1–7d | 28.5% |
| 7–30d | 37.6% |
| 30d+ | 0 |

Within-journey mix on the **full** converting set (`profile_unit_mix`):

- Of 140,818 multi-touch journeys, **11,699 (8.3%)** mix more than one `cat1`.
- **77,387 (55.0%)** mix more than one recency bucket.

Recency actually changes along a journey. `cat1` usually does not. Touch type cannot change: converting rows are 100% clicks.

### Spend problem if the unit is recency

`08_segment_economics.sql` wants `spend = SUM(cost)` on **all** impressions of a unit, converting and not. Recency-to-conversion is **undefined** for the 15.66M rows with `conversion_id = -1`. So recency is a good unit for *credit*, a bad unit for *budget* unless we invent a second recency definition for non-converters.

`cat1` and click/view exist on every row. Campaign does too, but we already know models will not disagree there.

### Interview questions

1. **What is an attribution window?**  
   The time after an impression during which a conversion can still be linked to it. Criteo states 30 days. We used `timestamp <= conversion_timestamp` and saw no converting sample touches beyond 30 days.

2. **Why can last-touch and linear agree even when both are implemented correctly?**  
   If a conversion has one touch, both give that touch 100%. If every touch belongs to the same campaign, campaign totals match even when touch-level credit differs.

3. **Criteo published 45K conversions. You counted 435,810 conversion ids. Who is right?**  
   For the resume we only use a number we can reproduce. 435,810 is `COUNT(DISTINCT conversion_id) WHERE conversion_id <> -1` on this file. 45K is not reproducible from the public TSV under that definition. We should say "435,810 converting journeys" or wait for the Phase 1 journey definition — not "45K".

---

## Unit choice (rule, not recency)

Campaign is still rejected (0.66% multi-campaign). Recency is now also rejected — see the interview Q&A below.

Rule applied on the full table (`sql/01c_cat_unit_screen.sql`):

- If any `cat` has ≥25% within-journey mixing on multi-touch converting journeys **and** is non-null on every non-converting row, use it as the **single** unit (bucket rare values to `other`, ≤15 levels).
- Else use `cat1`.

Qualifying features: **cat9, cat7, cat8, cat6**. Highest mixing is **cat9 at 97.1%** (30 raw levels, 100% present). After keeping the 14 most common values and folding the rest into `other`, mixing remains far above 25% (`profile_unit_choice`). Chosen unit: **`cat9_bucketed`** (`unit` column on `impressions_unit`).

P1.3 wording is **segments**, not campaigns. Recency stays a descriptive chart only (credit share by time-to-conversion), never a credit unit or resume claim.

P1.3 will later show last vs linear on **multi-touch journeys only** and on **all conversions**, so single-touch dilution is visible.

P1.7 (new): advertiser-credited share of Criteo-touched conversions, plus the max gap across segments. Baseline overall is 236,331 / 435,810 = 54.23%.

### Interview questions (recency rejected)

4. **Recency mixes more than cat1. Why isn't time-to-conversion the attribution unit?**  
   Last-touch **assigns 100% to the last impression by construction**. Grouping touches by how close they are to the conversion makes that tautological: the most recent bucket *must* win last-touch. The "finding" would not be an empirical bias; it would be the model definition restated as a chart. A context feature (`cat9`) can differ along a journey for reasons in the log, not because we sorted time.

5. **Why one unit for credit, spend, CPA and reallocation?**  
   If credit uses recency and spend uses `cat1`, an over-credited recency bucket cannot be the thing we move budget away from. The resume claim has to be one sentence: we found a segment last-touch over-credits, then we moved spend **on that same segment**. `cat9` (bucketed) exists on converting and non-converting rows, so spend and credit share a grain.

6. **Why not click vs view as the unit?**  
   Converting journeys in this file are 100% clicks. Views have cost and zero conversion credit. That is a useful descriptive fact, not a last-vs-linear comparison.

---

## `sql/02_journeys.sql` — what it does and why

**What.** Builds `journeys` with `touch_index`, `touch_count`, `is_first`, `is_last`.

**Converting journey.** All impressions that share a `conversion_id`, ordered by `timestamp`, kept if `timestamp <= conversion_timestamp`. **These rows are clicks only** — views never have a `conversion_id` in this dump.

**Non-converting journey.** Impressions of one `uid` × `campaign` that never convert (`MAX(conversion) = 0`). Window = 30 days (2,592,000 seconds) from that pair's first timestamp, matching Criteo's conversion window. The public file is itself ~30 days, so almost every pair is one window.

**Why `<=` not `<`.** A click can share the conversion second. Dropping ties would delete the last touch and break last-touch.

P1.2 is `n_converting_journeys + n_non_converting_journeys` from `journey_headline` (`sql/02b_journey_counts_full.sql` on the full table), formatted as **7.9M** on the resume. The sample `journeys` table is only for development. Attribution uses `journeys_converting` on the **full** converting set (~806K click rows). Segment spend is `SUM(cost)` on `impressions_unit`, including views.

---

## Unit validity (`attribution/validate_unit.py`)

Mixing is not enough. A feature can mix along a journey and still be noise or a disguised clock.

Checks on bucketed **cat9** (15 contextual segments):

| check | result |
| --- | --- |
| Spearman CPA (advertiser-credited), days 1–15 vs 16–30 | **0.993** (threshold 0.6) |
| CPA spread max/min, days 1–15 / 16–30 | 3.04 / 3.50 |
| CPA spread observed vs shuffled labels | **3.31 vs 1.56** |
| Within-journey mixing observed vs shuffled | 0.962 vs 0.920 |
| Mean total-variation of segment mix by day / hour | 0.019 / 0.026 — **not time-explained** |

Decision: keep cat9. cat8 and cat6 were not needed.

CPA = spend / advertiser-credited conversions. Half-cut is `timestamp < 15 * 86400`. Shuffle permutes raw cat9 across impressions (seed 42) then reapplies the same 14+`other` map.

### Interview questions (stability and leakage)

7. **How do you know your reallocation isn't fitting noise?**  
   Two guards. First, **split-half stability**: a contextual segment that is "expensive" in days 1–15 should still be expensive in days 16–30 (Spearman of CPA ≥ 0.6). Cat9's 0.993 means the ranking is a property of the segment, not of one fortnight. Second, **out-of-sample reallocation**: pick donors and receivers from days 1–15 CPA, then score uplift with days 16–30 CPA. The in-sample number is kept only as a comparison. If we picked and scored on the same days, a noisy high-CPA segment would look like a free lunch.

8. **Why compare CPA spread to a shuffle?**  
   Even random labels produce some max/min CPA because volume is uneven. If observed spread is not clearly larger than the shuffled spread, the feature is not an economic segment. Cat9's 3.31 vs 1.56 clears that.

9. **Could cat9 just be hour-of-day?**  
   If one segment owned a daypart, hourly mix would be far from the overall mix (high total variation) or one segment would pile into a few hours. Mean hourly TV is 0.026 and no segment has more than ~10% of its impressions in a single hour. Call them **contextual segments**, not dayparts. Raw ids stay anonymised on the resume.

---

## `sql/03`–`07` attribution

Credit only converting journeys. Each model writes `(conversion_id, unit, credit)` summing to 1.0 per conversion (`attr_credit_check`).

- First-touch: `is_first`
- Last-touch: `is_last`
- Linear: `1 / touch_count`
- Position: 40/20/40; 1 touch = 100%; 2 touches = 50/50

P1.3 uses **contextual segments**. Last vs linear is shown on multi-touch journeys and on all conversions so single-touch dilution is visible. Recency credit share is a chart only.

Advertiser gap: every converting journey is Criteo-touched; `MAX(attribution)=1` is advertiser-credited. P1.7 is that share overall and the range across contextual segments.

**Not a finding:** advertiser-credited CPA is always higher than CPA on all Criteo-touched conversions if spend is held fixed, because the denominator is smaller. That is arithmetic, not economics. We do not put it on the resume.

**Not currency:** `cost` is a scaled anonymised field. Report spend *share* and CPA *index* (`spend_share / conversion_share`). Never ₹, $, or "CPA = 0.012".

P1.3 headline excludes the `other` bucket (rare cat9 values). `other` stays in the tables.

---

## `sql/08` economics and `reallocate.py`

Economics are computed for `full`, `days_1_15`, and `days_16_30`. Spend follows the impression timestamp; a conversion is assigned to the half of its `conversion_timestamp`. Confidence floor = 30 attributed conversions. `other` may donate budget and may not receive it.

Primary outcome = advertiser-credited conversions split by **linear** credit. All conversions (linear split) is the second outcome. Last-touch split is sensitivity only.

### Interview questions (reallocation design)

10. **Why a supply cap on receivers (and a donor cap)?**  
    Low-CPA segments cannot absorb an arbitrary transfer. A +50% spend cap (parameter) stops us from dumping the whole pool onto the cheapest unit and pretending CPA stays put. The symmetric **donor cap (−50%)** stops us from zeroing a line item to fund the pool. X is valid only if the first-half pool fits under both caps. `other` is a long-tail bucket, not one buyable line; a sensitivity run excludes it from both roles.

11. **Why is X chosen on days 1–15, before looking at days 16–30?**  
    If we pick the shift size that looks best on the same days we score, we are tuning to noise. We take the **largest** X in {5, 10, 15, 20}% that fits the first-half cap rule, freeze donors/receivers/X, and only then apply those spend *fractions* to days 16–30. The in-sample uplift is a comparison, not the claim.

12. **Why do donors lose conversions at average CPA, not a better marginal CPA?**  
    Cutting spend on a high-CPA segment might drop their *worst* impressions first, so true lost conversions could be *fewer* than spend / average CPA. Using the average is conservative: we assume we lose typical conversions, which makes the uplift harder to earn. Receivers buy new conversions at CPA × 1.25 (diminishing returns).

13. **Why linear as the reference model?**  
    Linear does not privilege the last click. Last-touch is what we are diagnosing. Reallocation uses linear-attributed (and advertiser-credited linear) conversions so we are not "fixing" last-touch by using last-touch as the objective.

14. **Your OOS test validates CPA stability, not incrementality — how would you prove the uplift is causal?**  
    The split-half check only shows that expensive segments stay expensive. The +X% is a **projection** under stated assumptions (linear credit, diminishing-returns factor, donor/receiver caps, average-CPA donor losses). It is not a causal estimate of what would happen if we moved budget. To prove incrementality: run a **geo or holdout budget experiment** — treat some markets or a random slice of traffic, shift spend on the same plan, and measure advertiser-credited conversions versus a holdout that keeps the old mix. Until that exists, the resume number is a simulation, not a lift test.

15. **Why does your plan move 97% of budget into segments the advertiser credits less often?**  
    Credit rate uses **last-touch** allocation (P1.7): a journey is credited or not, then assigned to the last-click unit. Upper-funnel segments rarely get that last click, so their credited *rate* looks weak even when they sit on converting paths. Under even-split (default CPA) those same units are the cheapest. The 97% figure is the last-touch bias already measured in P1.8, not a plan that prefers segments the advertiser rejects. Switch the credit-rate allocation to linear and the “below-average credit” set changes.

**CPA ranking robustness.** On named segments, default CPA rank (advertiser-credited × linear) and last-click CPA rank are **identical**. Switching attribution model moves the index (largest |Δ| is segment 16022563, about 17%) but not the order. Ranking is therefore robust to last-click vs even-split; the dollar-index is not.

16. **Why did metric views (config E) lose accuracy versus calibrated prompts alone (D)?**  
    The views are correct at book grain. The model treated them as join keys for path-length and last-click slices, so it selected a pre-aggregate and then filtered the wrong table. A plan node that lists `v_*` first increases that temptation. Views help when the question matches the view; they hurt when the question needs a subset. Config D (rules only) beat E on both the 15-q dev set and the 50-q eval. F (same graph as E, gpt-4o) recovered some of that by following the grain rule more often — at ~25× rupee cost versus D.

---

## Final interview set (15)

These are the questions I should be able to answer without opening a laptop.

1. **Why linear as the reference model?**  
   Last-touch is the bias we are measuring. Using last-touch as the objective would “fix” last-touch with last-touch. Linear splits 1/n so no position is privileged. Reallocation and default CPA use advertiser-credited × linear.

2. **What is an attribution window?**  
   The time after a display during which a conversion can still be joined to that display. Criteo’s dump uses 30 days (`conversion_timestamp − timestamp`). Touches after the conversion timestamp are dropped.

3. **What is last-touch bias here?**  
   Last-click gets 100% of the conversion. Upper-funnel segments sit on the path but rarely take the last click, so last-touch under-credits them (largest named segment: −95.1% vs linear on multi-touch) and over-credits a handful of closer segments (up to +24.9% on all conversions).

4. **Why can execution accuracy mislead?**  
   A query can match gold and still be the wrong business metric, or fail gold because it returned the right label plus an extra column. After the grader audit we score “which segment” on `unit` only. Accuracy is also a 50-question set, not production traffic.

5. **Why read-only execution?**  
   The warehouse is the portfolio artifact. A generated `DELETE` or `DROP` would destroy the only copy of 16.5M rows. sqlglot rejects non-SELECT; DuckDB opens `read_only=True`; the agent returns `REFUSE` for mutations.

6. **How did you prevent eval leakage?**  
   Few-shot pairs are hand-written, not copied from the eval set. Jaccard token-overlap of every eval question vs the pool maxes at 0.444 (threshold 0.85). A pytest fails if an eval/dev question appears in few-shot or smoke. Tuning used a 15-q **dev** set; we did not peek at per-item eval failures while changing prompts.

7. **What would you do with more time?**  
   Markov or data-driven attribution if we need path-level incrementality; a larger eval with human raters; semantic caching of repeated metric SQL; a geo/holdout budget test so P1.5 is causal; Power BI pages so P1.6 is a real count.

8. **Why hash users for the 10% sample?**  
   Row sampling splits journeys. `hash(uid) % 10 = 0` keeps a user’s history together and is repeatable.

9. **Why contextual segments instead of campaigns?**  
   Only 0.66% of converting journeys touch more than one campaign, so campaign-level last vs linear is almost identical. cat9 has 15 buckets, stable half-month CPA ranks (Spearman 0.993), and CPA spread above a label shuffle.

10. **Why not average CPA across segments?**  
    CPA is a ratio. The mean of ratios ≠ the ratio of sums. “Average” in this warehouse is the pooled book figure (`spend_share / conversion_share`).

11. **Why split-half then OOS reallocation?**  
    Choosing X on the same days you score fits noise. X, donors, and receivers are locked on days 1–15; days 16–30 only score the frozen plan.

12. **What does the 1.25 diminishing-returns factor mean?**  
    New spend on a receiver buys conversions at 1.25 × its current CPA. It is a parameter, not estimated. Sensitivity is in `reallocation_scenarios.csv`.

13. **Advertiser credit vs conversion flag?**  
    `impressions.conversion` is “a conversion followed within 30 days.” `attribution` / `is_advertiser_credited` is “the advertiser paid Criteo for that conversion.” 54.23% of Criteo-touched converting journeys are credited.

14. **Why refuse delete but not “ROAS in rupees”?**  
    Delete is a write. ROAS in rupees is a read we cannot answer (no currency, cost is scaled) → `NOT_IN_DATA`. Config D still over-refuses A03/A07; that is a known `wrong_status` failure.

15. **Config D vs F — which number goes on the resume?**  
    D is the primary: cheap, same provider, 52.0%, ₹0.046/query. F shows the accuracy/cost trade-off (61.3%, ₹1.17). We do not report F as the production model.

