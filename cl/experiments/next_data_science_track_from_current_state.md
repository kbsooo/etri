# Next data-science track from current state

Scope: use `/Users/kbsoo/Downloads/dacon/etri/cl` as the active workspace. Ignore the older top-level `/Users/kbsoo/Downloads/dacon/etri` modeling artifacts for this track unless explicitly requested.

## Current reliable base

Read these as the current head of the `cl` data-science line:

1. `experiments/deep_ds_synthesis_v1_report.md`
2. `experiments/problem_definition_q_temporal_s_context_measurement.md`
3. `experiments/advanced76_data_science_report.md`
4. `experiments/q2q3_event_residual_diagnostic_report.md`

Latest diagnostic implementation:

- `scripts/88_q2q3_event_residual_diagnostic.py`

Latest diagnostic artifacts:

- `experiments/q2q3_event_residual_diagnostic_results.csv`
- `experiments/q2q3_event_residual_diagnostic_summary.csv`
- `experiments/q2q3_event_residual_diagnostic_shifts.csv`
- `experiments/q2q3_event_residual_diagnostic_selected_features.csv`

## Working interpretation

The task should be treated as a measurement/context/temporal-completion problem, not a generic sleep-quality prediction problem.

Target routing:

- Q2: strongest real day-varying signal. Coverage + temporal neighbor + small event/deviation residual are worth investigating.
- Q3: sticky temporal grammar; weaker day-feature signal than Q2.
- Q1: weak/noisy; coverage can be actively misleading. Do not push large residuals.
- S1: mostly subject prior/static.
- S2/S3: mostly subject/static fingerprint; freeze or use very conservative calibration only.
- S4: possible capped context-event signal, but sparse tokens are brittle.

## Next concrete phase

Do an insight-first, no-submission analysis that turns the previous diagnostics into row/subject-level evidence:

1. Build subject profile cards:
   - label prevalence and entropy by subject
   - Q2/Q3 transition/stickiness by subject
   - coverage reliability by subject/modality
   - token/context fingerprint strength by subject

2. Build test-regime map:
   - for each test row, classify as train-range hole vs forecast-tail
   - distance to nearest labeled days before/after
   - available neighbor grammar strength
   - coverage/context availability

3. Build target-specific action map:
   - Q2 rows where residual signal is credible
   - Q3 rows where temporal completion is credible
   - S4 rows with capped context-event evidence
   - rows/targets to freeze because only subject/static evidence exists

4. Output only reports/CSVs under `experiments/`; no submission CSV unless explicitly requested.

Suggested next script name:

- `scripts/89_subject_test_regime_field_notes.py`

Suggested outputs:

- `experiments/subject_test_regime_field_notes_report.md`
- `experiments/subject_profile_cards.csv`
- `experiments/test_regime_map.csv`
- `experiments/target_action_map.csv`
