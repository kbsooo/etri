# GPT Pro Pack: Q2/S1 Hidden-State Translation

This pack is for asking another model to diagnose why the Q2/S1 hidden lifestyle state is locally real but not yet public-safe.

## First Upload Set

Upload these files first:

1. `PROMPT_FOR_GPT_PRO.md`
2. `compact_metrics/known_public_lb_observations_compact.csv`
3. `compact_metrics/label_signal_summary_compact.csv`
4. `compact_metrics/e368_q2s1_predictability_diagnostics.csv`
5. `compact_metrics/e369_q2s1_local_residual_best.csv`
6. `compact_metrics/e372_q2_calibration_residual_latents.csv`
7. `compact_metrics/key_submission_movement_by_target.csv`
8. `compact_metrics/target_read_interpretation_compact.csv`
9. `reports/e368_q2s1_rowmask_cellaction_report.md`
10. `reports/e369_q2s1_lifestyle_transfer_report.md`
11. `reports/e370_q2s1_risk_constrained_report.md`
12. `reports/e371_q2_rowwise_safety_report.md`
13. `reports/e372_q2_calibration_residual_report.md`

## Optional Upload Set

Use these only if GPT Pro asks for broader history:

- `optional_full_context/lb_observation_log.md`
- `optional_full_context/candidate_submissions.md`
- `optional_full_context/validation_stress_report.md`
- `optional_full_context/latent_diagnostics.md`

## Submission Tensors

Upload these if it wants to compute prediction deltas directly:

- `submissions/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`
- `submissions/submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv`
- `submissions/submission_e323_5508f966_uploadsafe.csv`
- `submissions/submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv`
- `submissions/submission_e95_hardtail_541e3973.csv`

## Core Question

The core question is not "how do we improve public LB by a tiny amount?"

The core question is:

> Q2/S1 hidden state is locally real. Why did translating it into E368 not beat E247, and what invariant would make a Q2/S1 action public-safe?

## Known Hard Facts

- Current public best: E247, `0.5761589494`.
- E368 Q2/S1 rowmask: `0.576290429`, locally strong but not public-best.
- E323 social/human direct gate: `0.5770355016`, public-bad anchor.
- E216 S2 JEPA translator: `0.5772865088`, severe public miss.
- E372 Q2 residual latent: local Q2 delta `-0.030210616`, but no safer replacement selected.

## What We Need Back

Ask GPT Pro for:

- one most likely failure mechanism;
- a falsifiable hypothesis;
- the smallest next diagnostic experiment;
- one concrete candidate-generation rule, if and only if it can preserve E247 and avoid E323-like bad-axis leakage.
