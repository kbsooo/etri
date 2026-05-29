# E123 transition-motif S3 sensor audit

## Question

E101 lost to E95 by `+0.0000090362` public logloss. E122 says the loss is
roughly one high-impact S3 boundary cell, but the existing direct flank and
subject-prior sensors keep the rank-23 cell in the E101-support branch. This
experiment asks whether the *full Q/S neighbor-state motif* contains an
independent, train-only signal that can separate that cell.

No submission is created here. The output is a gate decision.

## Local stress result

Temporal tail-by-subject validation:

| sensor | logloss | delta_vs_subject_prior | auc | mean_pred | y_rate |
| --- | --- | --- | --- | --- | --- |
| subject_prior | 0.635191 | 0.000000 | 0.686905 | 0.672522 | 0.631579 |
| s3_flank_beta | 0.649302 | 0.014110 | 0.682381 | 0.685495 | 0.631579 |
| motif_no_s3 | 0.770374 | 0.135183 | 0.578571 | 0.681679 | 0.631579 |
| motif_full | 0.881431 | 0.246239 | 0.578571 | 0.738767 | 0.631579 |
| motif_plus_subject | 0.984257 | 0.349065 | 0.656190 | 0.783221 | 0.631579 |

Interleaved within-subject validation:

| sensor | logloss | delta_vs_subject_prior | auc | mean_pred | y_rate |
| --- | --- | --- | --- | --- | --- |
| subject_prior | 0.530353 | 0.000000 | 0.764545 | 0.646116 | 0.725275 |
| s3_flank_beta | 0.594655 | 0.064302 | 0.725152 | 0.629682 | 0.725275 |
| motif_no_s3 | 0.583962 | 0.053609 | 0.676970 | 0.624236 | 0.725275 |
| motif_full | 0.609456 | 0.079103 | 0.684848 | 0.613837 | 0.725275 |
| motif_plus_subject | 0.569415 | 0.039062 | 0.745455 | 0.619475 | 0.725275 |

## E101 boundary sensor fit

Sorted by absolute error to the observed E101 public delta:

| sensor | expected_active_delta_sum | expected_public_delta_vs_e95 | actual_e101_public_delta_vs_e95 | abs_error_to_actual_e101_delta | mean_support_probability | top10_support_probability | rank22_support_probability | rank23_support_probability | temporal_logloss_delta_vs_subject |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s3_flank_beta | 0.012598740 | 0.000007199 | 0.000009036 | 0.000001837 | 0.594239354 | 0.829096366 | 0.098039216 | 0.966666667 | 0.014110494 |
| subject | 0.010051940 | 0.000005744 | 0.000009036 | 0.000003292 | 0.604450426 | 0.815377864 | 0.104166667 | 0.958333333 |  |
| motif_plus_subject | 0.035640366 | 0.000020366 | 0.000009036 | 0.000011330 | 0.556724085 | 0.766191500 | 0.216335997 | 0.984326110 | 0.349065351 |
| motif_no_s3 | 0.048446365 | 0.000027684 | 0.000009036 | 0.000018647 | 0.546588168 | 0.705047736 | 0.722548497 | 0.943564322 | 0.135182563 |
| motif_full | 0.049696545 | 0.000028398 | 0.000009036 | 0.000019362 | 0.537420706 | 0.718060883 | 0.625089125 | 0.956190730 | 0.246239355 |

Best aggregate explanatory sensor: `s3_flank_beta` with expected
public delta `0.000007199`.

## Critical S3 cells

| rank | sub_idx | hidden_block_id | sleep_date | support_label | prev_y | next_y | p_y1_subject | p_y1_both_distance_beta | p_y1_motif_no_s3 | p_y1_motif_full | p_y1_motif_plus_subject | support_probability_subject | support_probability_both_distance_beta | support_probability_motif_no_s3 | support_probability_motif_full | support_probability_motif_plus_subject | support_delta | adverse_delta | flip_benefit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 18 | 115 | id05_b4 | 2024-10-14 00:00:00 | 0 | 0.000000 | 0.000000 | 0.136364 | 0.111317 | 0.133304 | 0.126214 | 0.126326 | 0.863636 | 0.888683 | 0.866696 | 0.873786 | 0.873674 | -0.001519 | 0.012695 | 0.014214 |
| 19 | 47 | id02_b4 | 2024-10-04 00:00:00 | 1 | 1.000000 |  | 0.895833 | 0.903846 | 0.446215 | 0.534125 | 0.880019 | 0.895833 | 0.903846 | 0.446215 | 0.534125 | 0.880019 | -0.001312 | 0.012601 | 0.013913 |
| 20 | 22 | id01_b4 | 2024-09-11 00:00:00 | 0 | 1.000000 |  | 0.853659 | 0.860627 | 0.552597 | 0.691537 | 0.842372 | 0.146341 | 0.139373 | 0.447403 | 0.308463 | 0.157628 | -0.011131 | 0.002613 | 0.013743 |
| 21 | 158 | id07_b2 | 2024-07-20 00:00:00 | 1 | 1.000000 | 1.000000 | 0.795918 | 0.818913 | 0.894418 | 0.887538 | 0.878343 | 0.795918 | 0.818913 | 0.894418 | 0.887538 | 0.878343 | -0.002209 | 0.011019 | 0.013228 |
| 22 | 49 | id02_b4 | 2024-10-06 00:00:00 | 0 | 1.000000 |  | 0.895833 | 0.901961 | 0.277452 | 0.374911 | 0.783664 | 0.104167 | 0.098039 | 0.722548 | 0.625089 | 0.216336 | -0.010471 | 0.002617 | 0.013089 |
| 23 | 147 | id06_b10 | 2024-08-21 00:00:00 | 1 | 1.000000 |  | 0.958333 | 0.966667 | 0.943564 | 0.956191 | 0.984326 | 0.958333 | 0.966667 | 0.943564 | 0.956191 | 0.984326 | -0.000598 | 0.012470 | 0.013068 |
| 24 | 91 | id04_b6 | 2024-09-25 00:00:00 | 0 | 1.000000 | 0.000000 | 0.543860 | 0.496964 | 0.705515 | 0.708650 | 0.787740 | 0.456140 | 0.503036 | 0.294485 | 0.291350 | 0.212260 | -0.006359 | 0.006693 | 0.013052 |
| 25 | 103 | id04_b12 | 2024-10-26 00:00:00 | 1 | 0.000000 | 0.000000 | 0.543860 | 0.326316 | 0.150526 | 0.101543 | 0.441293 | 0.543860 | 0.326316 | 0.150526 | 0.101543 | 0.441293 | -0.005318 | 0.007065 | 0.012383 |
| 26 | 27 | id02_b2 | 2024-08-26 00:00:00 | 1 | 1.000000 | 1.000000 | 0.895833 | 0.931973 | 0.772602 | 0.826409 | 0.921305 | 0.895833 | 0.931973 | 0.772602 | 0.826409 | 0.921305 | -0.001074 | 0.010051 | 0.011125 |
| 27 | 70 | id03_b4 | 2024-09-16 00:00:00 | 0 | 1.000000 |  | 0.484848 | 0.558442 | 0.623183 | 0.692560 | 0.363857 | 0.515152 | 0.441558 | 0.376817 | 0.307440 | 0.636143 | -0.003659 | 0.005756 | 0.009415 |

## Interpretation

- The no-S3 transition motif is the cleanest independence test: it excludes the
  direct previous/next S3 labels and asks whether Q1/Q2/Q3/S1/S2/S4 neighbor
  state predicts S3.
- If this sensor lowered rank 23 support while surviving temporal validation,
  it would justify a new E101/E95 gate branch.
- Observed rank-23 support under motif_no_s3 is
  `0.943564`; under motif_plus_subject it
  is `0.984326`.
- Therefore this experiment does not open a new same-line gate for E101.

## Decision

Do not build a submission from this sensor unless a later public-independent
test contradicts the rank-23 reading. The current bottleneck remains a narrow
S3 hard-tail boundary whose aggregate branch is explainable but whose decisive
cell is not resolved by visible transition motifs.
