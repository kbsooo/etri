You are an elite ML competition scientist and representation-learning researcher.

I need you to help diagnose a very specific bottleneck in a tabular sleep/lifelog competition.

## Task

Multi-label binary classification with 7 targets:

- Q1: subjective sleep satisfaction-ish signal
- Q2: sleep intervention / disturbance-ish signal; lower is better conceptually
- Q3: sleep quality-ish signal
- S1-S4: objective sleep-stage ratio-ish signals

Metric: mean binary Log Loss across Q1/Q2/Q3/S1/S2/S3/S4.

Current public best:

- `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`
- public LB: `0.5761589494`

Important public observations:

- `submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv`
  - public LB: `0.576290429`
  - This was a Q2/S1 hidden-lifestyle rowmask translation.
  - It was locally very strong but did not beat E247.
- `submission_e323_5508f966_uploadsafe.csv`
  - public LB: `0.5770355016`
  - This is a public-bad human/social direct-gate anchor.
- `submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv`
  - public LB: `0.5772865088`
  - This is a severe public miss from an S2 JEPA-style translator.
- `submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv`
  - public LB: `0.5762805676`
  - Broader/high-amplitude Q3 follow-up; worse than E247.

## The specific bottleneck

We believe this statement is currently true:

> The Q2/S1 hidden state is real locally, but we have not translated it into a public-safe probability edit that beats E247.

I want you to challenge this statement and help us find the next sharp experiment.

## What "JEPA" means here

Do not assume we need a literal I-JEPA implementation. We are using the JEPA idea as:

- context = feature family, row neighborhood, subject/dateblock, lifestyle/social/app/activity context, residual context
- target representation = hidden state, target residual, public-good support, public-bad support, row/cell action benefit
- prediction = predict the representation, not raw feature reconstruction
- LeJEPA-style skepticism = reject collapse/shortcut/prior memorization/calibration luck using nulls, split stress, public-bad axis, and action-health tests

## Key local evidence

Q2 residual latent:

- `Q2_jepa_resid_subject`
- base logloss: `0.765899724`
- augmented logloss: `0.735689108`
- delta: `-0.030210616`
- dominance: `1.0`
- placebo-adjusted vs median: about `-0.030765`

S1 transfer latent:

- best local delta: about `-0.009128`

E368 Q2/S1 rowmask diagnostics:

- Q2 validity KFold Spearman: `0.426940`
- Q2 null p95: `0.102237`
- S1 validity KFold Spearman: `0.157989`
- S1 null p95: `0.102777`
- The selected E368 candidate beat local/null/direct-public controls under many stress scenarios.

But:

- E368 public LB was `0.576290429`, worse than E247 by about `+0.00013148`.
- E370/E371/E372 tried Q2/S1 risk-constrained recalibration, rowwise Q2 safety gates, and Q2 calibration residual latents.
- They could not find a safer replacement that preserved the local Q2/S1 support while reducing E323-like Q2 bad-axis risk.

## Files I am attaching

Start with these:

1. `compact_metrics/known_public_lb_observations_compact.csv`
2. `compact_metrics/label_signal_summary_compact.csv`
3. `compact_metrics/e368_q2s1_predictability_diagnostics.csv`
4. `compact_metrics/e369_q2s1_local_residual_best.csv`
5. `compact_metrics/e372_q2_calibration_residual_latents.csv`
6. `compact_metrics/key_submission_movement_by_target.csv`
7. `compact_metrics/target_read_interpretation_compact.csv`
8. Reports:
   - `reports/e368_q2s1_rowmask_cellaction_report.md`
   - `reports/e369_q2s1_lifestyle_transfer_report.md`
   - `reports/e370_q2s1_risk_constrained_report.md`
   - `reports/e371_q2_rowwise_safety_report.md`
   - `reports/e372_q2_calibration_residual_report.md`

Use these only if needed:

- `optional_full_context/lb_observation_log.md`
- `optional_full_context/candidate_submissions.md`
- `optional_full_context/validation_stress_report.md`
- `optional_full_context/latent_diagnostics.md`

Submission tensors are included in `submissions/`:

- E247 current public best
- E368 Q2/S1 rowmask candidate
- E323 public-bad anchor
- E256 Q3 broad follow-up
- E95 older hardtail anchor

## What I want from you

Please do not give generic advice like "try LightGBM", "stack more models", or "add features".

I want a diagnosis and a next experiment.

Answer these questions:

1. Is the Q2/S1 hidden state likely real, or is it an artifact of the local stress design?
2. If it is real, why did E368 fail to beat E247?
3. Is the problem:
   - Q2 signal/action sign error?
   - Q2 public-subset mismatch?
   - Q2/S1 interaction mismatch?
   - target-wise calibration mismatch?
   - row-gate over-selection?
   - E247 body incompatibility?
   - public-bad axis leakage?
   - something else?
4. What invariant should a public-safe Q2/S1 action satisfy that E368/E370/E371/E372 failed to satisfy?
5. What is the smallest next experiment that could kill or validate your diagnosis?
6. If you had to propose one concrete candidate-generation rule, what exactly would it do to the probability tensor?

## Desired answer format

Please structure your answer like this:

1. **Most likely failure mechanism**
   - One compressed sentence.
   - Then evidence from the attached files.

2. **What is real vs fake**
   - Q2 signal
   - S1 signal
   - Q2/S1 joint gate
   - E323 bad-axis warning
   - E247 incompatibility

3. **A falsifiable hypothesis**
   - Name it.
   - What would be true if it is right?
   - What would be true if it is wrong?

4. **One next experiment**
   - Data used
   - Split/stress design
   - Exact target to predict
   - Exact action on submission probabilities
   - Stop condition / reject condition

5. **Candidate-generation recipe**
   - Pseudocode is preferred.
   - It must be public-LB-scarce: no blind leaderboard tuning.
   - It must preserve E247 unless a strong invariant says otherwise.

6. **Risk note**
   - What would make this idea fail publicly?

Be skeptical. If the correct conclusion is "do not submit another Q2/S1 file yet", say that clearly and tell me what diagnostic must come first.
