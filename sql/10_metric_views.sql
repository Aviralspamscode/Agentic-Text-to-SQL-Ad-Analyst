-- Default metric views. Select these; do not re-derive the definitions.

CREATE OR REPLACE VIEW v_segment_cpa_default AS
SELECT
    period,
    CAST(unit AS VARCHAR) AS unit,
    cpa_index_adv_linear AS cpa,
    spend_share,
    adv_linear_conv_share,
    low_confidence_adv_linear
FROM segment_economics;

CREATE OR REPLACE VIEW v_credit_rate_last_touch AS
WITH last_unit AS (
    SELECT conversion_id, CAST(unit AS VARCHAR) AS unit
    FROM journeys_converting
    WHERE is_last = 1
),
flags AS (
    SELECT conversion_id, MAX(attribution) AS is_advertiser_credited
    FROM journeys_converting
    GROUP BY conversion_id
)
SELECT
    u.unit,
    AVG(CAST(f.is_advertiser_credited AS DOUBLE)) AS credit_rate,
    COUNT(*) AS n_journeys
FROM last_unit u
JOIN flags f USING (conversion_id)
GROUP BY u.unit;

CREATE OR REPLACE VIEW v_linear_last_by_unit AS
SELECT
    CAST(unit AS VARCHAR) AS unit,
    SUM(1.0 / touch_count) AS linear_credit,
    SUM(is_last) AS last_credit
FROM journeys_converting
GROUP BY 1;

CREATE OR REPLACE VIEW v_view_click_spend AS
SELECT
    CAST(unit AS VARCHAR) AS unit,
    SUM(CASE WHEN click = 0 THEN cost ELSE 0 END) AS view_spend,
    SUM(CASE WHEN click = 1 THEN cost ELSE 0 END) AS click_spend,
    SUM(cost) AS spend,
    SUM(CASE WHEN click = 0 THEN cost ELSE 0 END) / NULLIF(SUM(cost), 0) AS view_spend_share
FROM impressions_unit
GROUP BY 1;
