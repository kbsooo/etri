# E113 Sauna Raw Context Visibility Audit

## Question

E112 says Q targets have temporal persistence, but label adjacency is sparse in test. The next I-JEPA-style question is whether visible raw lifelog context can stand in for the missing temporal labels. This is a diagnostic context-visibility head, not a submission model.

## Raw Coverage

- Raw daily feature count: `114`.
- Train rows with any raw coverage: `1.000000`.
- Test rows with any raw coverage: `1.000000`.

## Temporal Holdout Result

Negative deltas mean raw coverage improved over subject prior.

- Q targets raw+prior delta vs subject prior: `+0.038804`.
- S targets raw+prior delta vs subject prior: `+0.058534`.
- E95-active axes raw+prior delta: `+0.059881` vs inactive `+0.037008`.
- Random within-subject Q delta: `+0.007833`.
- Random within-subject S delta: `+0.016497`.

## Best Temporal Targets

| target | axis | e95_axis | subject_prior_logloss | raw_plus_prior_logloss | raw_plus_prior_delta_vs_subject_prior | raw_plus_prior_auc |
| --- | --- | --- | --- | --- | --- | --- |
| S3 | S | True | 0.624003 | 0.619361 | -0.004643 | 0.716999 |
| Q3 | Q | False | 0.700406 | 0.722712 | 0.022306 | 0.575974 |
| S4 | S | False | 0.653446 | 0.678238 | 0.024792 | 0.661593 |

## Worst Temporal Targets

| target | axis | e95_axis | subject_prior_logloss | raw_plus_prior_logloss | raw_plus_prior_delta_vs_subject_prior | raw_plus_prior_auc |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | Q | False | 0.678345 | 0.742269 | 0.063925 | 0.616162 |
| S2 | S | True | 0.617668 | 0.709903 | 0.092235 | 0.649240 |
| S1 | S | True | 0.557653 | 0.679402 | 0.121749 | 0.627875 |

## Group Summary

| split | group | mean_subject_prior_logloss | mean_raw_plus_prior_logloss | mean_raw_plus_prior_delta_vs_subject_prior | mean_raw_plus_prior_auc |
| --- | --- | --- | --- | --- | --- |
| temporal_last25_by_subject | Q_targets | 0.683507 | 0.722312 | 0.038804 | 0.594739 |
| temporal_last25_by_subject | S_targets | 0.613193 | 0.671726 | 0.058534 | 0.663926 |
| temporal_last25_by_subject | E95_active_axis | 0.617774 | 0.677655 | 0.059881 | 0.646548 |
| temporal_last25_by_subject | E95_inactive_axis | 0.677399 | 0.714406 | 0.037008 | 0.617909 |
| random_within_subject | Q_targets | 0.639167 | 0.647000 | 0.007833 | 0.665191 |
| random_within_subject | S_targets | 0.582199 | 0.598696 | 0.016497 | 0.695355 |
| random_within_subject | E95_active_axis | 0.585065 | 0.599249 | 0.014184 | 0.688698 |
| random_within_subject | E95_inactive_axis | 0.635346 | 0.646263 | 0.010917 | 0.674066 |

## Sauna Interpretation

The result weakens the visible-context rescue route. Raw coverage is present for every train/test row and has some ranking signal, but it worsens temporal LogLoss after subject prior on both Q and S groups. Q2 even improves slightly in random split while worsening in temporal holdout, which is a shortcut/collapse warning. The only temporal target with a small gain is S3, matching the E95/S-subject-state story. For now, E112's Q temporal signal remains mostly unobservable in a submission-safe way, explaining why broad Q/Q3 movement is dangerous and why LogLoss calibration, not AUC, is the bottleneck.

## Outputs

- `e113_sauna_raw_context_visibility_results.csv`
- `e113_sauna_raw_context_visibility_group_summary.csv`
- `e113_sauna_raw_context_visibility_coverage.csv`
- `e113_sauna_raw_context_daily_features.csv`
