# Cohort-Relative HS-JEPA Experiment

## One-line Summary

This experiment combines the cohort-relative human-state outlier idea with
HS-JEPA by treating peer-cohort anomaly as a **context view** and
**action-health gate**, not as a direct label rule.

## Why This Exists

The teammate idea asks:

- Is this day unusual for this subject?
- Is this day unusual inside a peer cohort of similar subjects?
- If yes, does that anomaly help Q2/Q3/S2 or row-target correction?

HS-JEPA adds one constraint:

> Cohort anomaly should not directly overwrite labels. It should first become a
> hidden state representation and only then decide whether a row-target action is
> safe.

## Data and Representation

- Raw sensor/date rows reviewed through local daily aggregation.
- Numeric daily features: `99`
- Latent dimensions: `8`
- Peer groups: `4`
- Subjects: `10`
- PCA explained variance ratio: `[0.10081532298730797, 0.08239187843821755, 0.07278085460083508, 0.06761673878040775, 0.04372958583951479, 0.040580041862259816, 0.03442334480956193, 0.03162224150576394]`

## Local CV Performance

Lower logloss is better. These are not public LB estimates; they test whether
cohort context carries train-side target signal.

| split | feature_set | fold | mean_logloss | Q1_logloss | Q2_logloss | Q3_logloss | S1_logloss | S2_logloss | S3_logloss | S4_logloss | std_logloss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| date_block | sensor_calendar_only | mean | 0.831101263651159 | 0.8780727487604073 | 0.9208082695031548 | 0.9063579741806749 | 0.7662128485257045 | 0.8157445217480653 | 0.7281696410838391 | 0.8023428417562675 | 0.09907866270043736 |
| date_block | sensor_plus_cohort_context | mean | 0.8423254000963046 | 0.890648032816947 | 0.9384034994775101 | 0.9062755407322836 | 0.7721986517599401 | 0.8230894655959965 | 0.7553508165499917 | 0.8103117937414632 | 0.09071515307773895 |
| date_block | sensor_plus_cohort_and_peer_margin | mean | 0.855243813252476 | 0.9327147347370147 | 0.9666295456944249 | 0.9273588594950418 | 0.7906330858727423 | 0.8224551297677476 | 0.7028673559203188 | 0.8440479812800419 | 0.08141757548455701 |
| subject_group | sensor_plus_cohort_context | mean | 1.5821007186799692 | 1.6905393183441153 | 1.4582344949285577 | 1.4723429902950618 | 1.2287646407928976 | 1.4526025320037346 | 2.216585785047787 | 1.5556352693476307 | 1.0953696676482418 |
| subject_group | sensor_calendar_only | mean | 1.588880280441142 | 1.702299614232766 | 1.461603509687095 | 1.4766796730107525 | 1.2549794087251829 | 1.4854820460981006 | 2.200780361073522 | 1.5403373502605757 | 1.1016330272386732 |
| subject_group | sensor_plus_cohort_and_peer_margin | mean | 1.6605111055844841 | 1.8820281901578155 | 1.524579736185326 | 1.548631934265112 | 1.2650087661707718 | 1.551984392176117 | 2.2795915247096947 | 1.5717531954265513 | 1.077977221965421 |

## Current-Best Action Alignment

This checks whether cohort anomaly independently identifies the rows used by
the current HS-JEPA best action field.

| signal | auc_for_current_best_hidden_rows | mean_selected | mean_not_selected | selected_rows | total_rows |
| --- | --- | --- | --- | --- | --- |
| cohort_outlier_score | 0.5243360433604336 | 0.5356609523809525 | 0.5173199999999999 | 45 | 250 |
| dist_to_subject_normal | 0.5598915989159892 | 4.883806265013809 | 4.457537872423473 | 45 | 250 |
| dist_to_peer_normal | 0.49886178861788616 | 5.791373624571934 | 5.774782827843018 | 45 | 250 |
| target_route_margin_q2q3s2 | 0.4199457994579946 | 0.45451015873015876 | 0.48942885017421606 | 45 | 250 |

## Diagnostic Candidate

The generated candidate starts from the current best and changes only the
strength of already-known current-best row-target actions:

- high cohort action-health rows get a small amplification;
- low cohort action-health rows get a small dampening;
- no new broad target route is introduced.

| model | soft_listener_logloss | delta_vs_current_best | submission_file |
| --- | --- | --- | --- |
| baseline_before_row_state_correction | 0.5540262606782045 | 0.00019412866974422016 | submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv |
| current_public_best | 0.5538321320084603 | 0.0 | submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv |
| cohort_relative_hsjepa_gate | 0.5538321991061005 | 6.709764022172493e-08 | submission_team_cohort_hsjepa_gate_0f0db65a_uploadsafe.csv |

Changed cells by target:

| target | changed_cells |
| --- | --- |
| Q1 | 45 |
| Q3 | 45 |
| S1 | 45 |
| S2 | 45 |
| S3 | 45 |
| S4 | 45 |

## Interpretation

This is a useful architecture experiment if cohort features improve local CV or
if cohort action-health aligns with the current-best hidden rows. It is not a
proof that the candidate should be submitted. The candidate is diagnostic
because it asks whether peer-relative state can safely tune an already validated
HS-JEPA action field.

## Decision

- If `sensor_plus_cohort_context` or `sensor_plus_cohort_and_peer_margin`
  improves date-block CV without damaging subject-group CV, the cohort module is
  worth adding to the formal HS-JEPA architecture.
- If current-best hidden-row AUC is weak, cohort anomaly is probably a paper
  context view, not a submission-grade action gate yet.
- If the diagnostic candidate worsens soft listener loss versus current best,
  do not submit it before a stronger solver is built.
