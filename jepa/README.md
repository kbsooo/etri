# JEPA Experiment Notes

Created from the I-JEPA idea: predict abstract target-block representations from context, then use the learned predictability/residual structure as features for the sleep/lifelog multilabel task.

## Paper Notes

- `ijepa.pdf`: original I-JEPA reference.
- `lejepa.pdf`: LeJEPA/SIGReg reference.
- `whendoeslejepa.pdf`: identifiability reference. Main practical update: do not trust a JEPA-style latent just because it is isotropic or locally predictive. First audit whether positive-pair transitions have near-Gaussian marginals/increments, useful non-trivial autocorrelation, stable rank, and low alignment gap. See `whendoeslejepa_reading_notes.md`.

## What Was Built

- `run_jepa_experiments.py`: builds JEPA-style features and scans them against the current stage2 OOF baseline.
- `jepa_guardrail_audit.py`: nested geometry-fold audit plus public-axis movement audit.
- `jepa_nested_q2_probe.py`: isolates the only target with positive nested-audit evidence and writes a Q2-only probe.
- `jepa_axis_cap_variants.py`: removes or caps movement along the known failed stage2-to-ordinal direction.
- `jepa_neural_grid_probe.py`: trains a masked sensor-time grid prediction network and scans its latent/residual features.
- `jepa_neural_guardrail_audit.py`: nested geometry-fold audit for the neural masked-grid probe.
- `jepa_candidate_summary.csv`: compact decision table for the main JEPA submission candidates.
- `train_jepa_features.parquet`, `submission_jepa_features.parquet`: 1,542 JEPA-derived features.
- `submission_jepa_selected.csv`: high-OOF-gain but guardrail-risky candidate.

Feature families:

- modality block prediction
- time block prediction
- sensor-time cell prediction
- prefix block prediction
- image-like sensor/time grid prediction
- subject temporal-neighbor prediction

## Main OOF Result

Baseline: `final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy`

Selected JEPA candidate:

- mean OOF `0.567530925 -> 0.562487995`
- delta `-0.005042930`
- strongest single signals are mostly `prectx` / `presleep` grid prediction features.

Target deltas:

- Q1 `-0.005219`
- Q2 `0.000000`
- Q3 `-0.010637`
- S1 `-0.003076`
- S2 `-0.004963`
- S3 `-0.003990`
- S4 `-0.007416`

## Guardrail Result

Nested geometry-fold selection reverses the gain:

- fold deltas: `+0.007748`, `+0.007418`, `+0.007142`, `+0.008714`
- mean nested delta: `+0.007756`

Interpretation: current JEPA features are real OOF residual explainers, but the selected correction is not fold-geometry stable. It should not be treated as a safe public submission candidate.

## Public Direction Risk

`submission_jepa_selected.csv` moves only weakly along the known good anchor-to-stage2 axis:

- good-axis cosine: `0.012929`
- good-axis projection ratio: `0.008419`

It overlaps materially with the failed stage2-to-ordinal direction:

- bad-axis cosine: `0.180455`
- bad-axis projection ratio: `0.146991`
- especially Q3 bad-axis cosine `0.442971`
- especially S4 bad-axis cosine `0.560956`

This matches the earlier diagnosis: strong presleep/prectx OOF gains tend to share public-fragile structure.

## Current Decision

Do not promote `submission_jepa_selected.csv` as a safe candidate. The useful discovery is methodological:

- JEPA framing finds strong latent residual structure.
- The best blocks are pre-sleep context, HR/light, and activity-grid predictability.
- The current supervised residual-selection layer overfits geometry/public split.

Next useful direction: use the JEPA features as a representation pool, but select only features that survive nested geometry folds or project away from the known stage2-to-ordinal bad axis before submission.

## Axis-Capped Variants

`jepa_axis_cap_variants.py` also writes logit-space variants that remove or cap the known bad-axis projection before producing a submission.

Best OOF among these capped variants:

- `submission_jepa_axiscap_cap0p1_scale1p0.csv`
- OOF `0.562844`
- OOF delta vs stage2 `-0.004687`
- submission bad-axis projection capped to `0.100`

Most conservative zero-bad-axis full-scale variant:

- `submission_jepa_axiscap_cap0p0_scale1p0.csv`
- OOF `0.563765`
- OOF delta vs stage2 `-0.003766`
- submission bad-axis projection `0.000`

These are still not proven safe by nested geometry folds, but they are better public-risk probes than the raw `submission_jepa_selected.csv`.

## Nested Q2 Probe

The nested audit found Q2 as the only target with mean holdout improvement, so it was tested separately in `jepa_nested_q2_probe.py`.

Best Q2-only full-OOF probe:

- `submission_jepa_nested_q2_probe.csv`
- feature: `jepa_sensor_time__prectx_usage__pre3h__pred_pc2`
- mode: `subject_center`
- weight: `0.45`
- Q2 OOF `0.642999 -> 0.639517`
- Q2 delta `-0.003482`
- mean multilabel delta about `-0.000497` because only Q2 changes.

Guardrail caveat:

- nested selected count: `2`
- nested holdout delta mean: `-0.012240`
- repeated-subject guardrail mean delta: `+0.001089`
- repeated-subject win rate: `0.400`

Decision: keep the Q2 probe as a low-amplitude exploratory candidate, not as a strong standalone recommendation.

## Neural Masked-Grid JEPA

`jepa_neural_grid_probe.py` treats the sensor/time grid values as an image-like vector and trains a masked prediction network on train+submission rows without labels. Generated features include the full latent state, masked-block prediction residuals, cosine agreement, and latent shift.

Full OOF result:

- `submission_neural_jepa_selected.csv`
- mean OOF `0.567531 -> 0.564161`
- delta `-0.003370`
- strongest targets: S1, S2, S4, Q3
- public bad-axis projection ratio `0.039597`, much lower than raw JEPA `0.146991`

Nested geometry result:

- fold deltas: `+0.005258`, `+0.007961`, `+0.011671`, `+0.005348`
- mean nested delta: `+0.007560`

Decision: neural JEPA found a cleaner public direction than raw JEPA, but it still fails the geometry-stability test. Hold as representation evidence, not as a safe submission.

## Candidate Summary

See `jepa_candidate_summary.csv`.

- Best raw OOF: `submission_jepa_selected.csv`, OOF delta `-0.005043`, but nested delta `+0.007756`.
- Cleaner nonlinear direction: `submission_neural_jepa_selected.csv`, OOF delta `-0.003370`, bad-axis ratio `0.039597`, but nested delta `+0.007560`.
- Best axis-capped probe: `submission_jepa_axiscap_cap0p1_scale1p0.csv`, OOF delta `-0.004687`, bad-axis ratio `0.100000`.
- Most conservative axis-capped probe: `submission_jepa_axiscap_cap0p0_scale1p0.csv`, OOF delta `-0.003766`, bad-axis ratio approximately `0`.
- Weak Q2-only probe: `submission_jepa_nested_q2_probe.csv`, OOF delta `-0.000497`, bad-axis ratio `0.000188`.
