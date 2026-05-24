# Q5 — Anomaly row taxonomy

Each train row is classified into one of four buckets based on three
axes (anchor logloss, neighbor disagreement, sensor coverage z-score).
Goal: distinguish label noise/transition vs sensor failure vs unexplained
anomalies so they can be treated differently.


Thresholds (top-quartile by each axis):

- `ll_mean` ≥ 0.688

- `neighbor_disagreement_rate` ≥ 0.143

- `coverage_anomaly_score` ≥ 2.419


## 1. Bucket sizes

| bucket | n | pct |
|---|---|---|
| normal | 337.0000 | 0.7490 |
| a_label_noise_or_transition | 49.0000 | 0.1090 |
| c_unexplained | 36.0000 | 0.0800 |
| a_or_b_mixed | 14.0000 | 0.0310 |
| b_sensor_failure | 14.0000 | 0.0310 |


## 2. Bucket contribution to anchor logloss

| bucket | mean | sum | count | total_share |
|---|---|---|---|---|
| a_label_noise_or_transition | 0.8030 | 39.3470 | 49.0000 | 0.1450 |
| a_or_b_mixed | 0.7806 | 10.9285 | 14.0000 | 0.0400 |
| b_sensor_failure | 0.8179 | 11.4503 | 14.0000 | 0.0420 |
| c_unexplained | 0.7623 | 27.4427 | 36.0000 | 0.1010 |
| normal | 0.5398 | 181.9211 | 337.0000 | 0.6710 |


## 3. Share of each target's logloss coming from non-normal rows

|  | anomaly_rows_share_of_target_logloss |
|---|---|
| Q1 | 0.2750 |
| Q2 | 0.2900 |
| Q3 | 0.2910 |
| S1 | 0.3720 |
| S2 | 0.4210 |
| S3 | 0.3880 |
| S4 | 0.2950 |


## 4. Interpretation

- normal rows mean anchor logloss: 0.5398
- (a) label noise / transition mean: 0.8030
- (b) sensor failure mean: 0.8179
- (c) unexplained anomaly mean: 0.7623
- mixed (both a & b) mean: 0.7806


### Decision implications
- If bucket (a) dominates the high-residual total, anomaly shrinkage will
  not help — those rows are *informationally* anomalous and any anchor
  prediction will be wrong. Best treatment: accept the loss; do not waste
  features on them.
- If bucket (b) dominates, coverage-based shrinkage toward anchor will
  reduce average loss (we already trust anchor; sensor evidence is bad).
- If bucket (c) is large, there is signal we are not capturing — these
  rows are anomalous *and* coverage is normal *and* neighbors don't help.
  This is where new feature families could matter.
