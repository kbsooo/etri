# E112 Sauna Q/S Temporal Axis Audit

## Question

E111 says E95 survives as target-axis surgery: mostly S-side movement plus a tiny Q2 component. If that is a real data-generating clue, the train label/order structure should show S or E95-active targets carrying more subject/temporal state than the inactive Q/Q3/S4 axes.

## Key Results

- S-target mean subject-LOO logloss gain: `0.068724` vs Q-target `0.020146`.
- S-target mean subject-rate variance: `0.040376` vs Q-target `0.020313`.
- S-target mean temporal persistence lift: `0.087255` vs Q-target `0.135700`.
- E95-active targets mean subject-LOO gain: `0.062393` vs inactive axes `0.028587`.
- E95-active targets mean temporal persistence lift: `0.103398` vs inactive axes `0.114176`.
- Test rows with nearby train context: prev<=3 days `0.340000`, next<=3 days `0.228000`, bracketed by both `0.080000`.

## Strongest Subject-Prior Targets

| target | axis | e95_axis | subject_loo_logloss_gain | subject_rate_var | icc_proxy |
| --- | --- | --- | --- | --- | --- |
| S3 | S | True | 0.107004 | 0.055126 | 0.246448 |
| S2 | S | True | 0.073599 | 0.043005 | 0.189310 |
| S1 | S | True | 0.050606 | 0.029238 | 0.134865 |

## Strongest Temporal-Persistence Targets

| target | axis | e95_axis | same_label_rate_gap_le7 | expected_same_by_prevalence | persistence_lift_gap_le7 | transition_contrast |
| --- | --- | --- | --- | --- | --- | --- |
| Q2 | Q | True | 0.658140 | 0.507743 | 0.150396 | 0.306360 |
| Q3 | Q | False | 0.655814 | 0.520000 | 0.135814 | 0.281569 |
| Q1 | Q | False | 0.620930 | 0.500040 | 0.120891 | 0.242037 |

## Pairwise Axis Correlations

| axis_pair | mean | max | min | count |
| --- | --- | --- | --- | --- |
| QQ | 0.187934 | 0.340129 | 0.101612 | 3 |
| QS | 0.030038 | 0.361444 | -0.119120 | 12 |
| SS | 0.260803 | 0.478282 | 0.086327 | 6 |

## Sauna Interpretation

This is a kill-test for H105, and the result is asymmetric rather than uniformly favorable. S/E95-active axes show stronger subject-state structure, while Q axes show stronger short temporal persistence. Because only a small fraction of test rows are tightly bracketed by nearby train labels, the Q temporal signal is difficult to transfer safely. This makes E95's S-heavy surgery more plausible as restricted subject/block-state translation, and it explains why broad Q/Q3 movement remains dangerous.

## Outputs

- `e112_sauna_qs_temporal_axis_target_stats.csv`
- `e112_sauna_qs_temporal_axis_pairwise_corr.csv`
- `e112_sauna_qs_temporal_axis_test_calendar.csv`
- `e112_sauna_qs_temporal_axis_group_summary.csv`
