# LeJEPA Block-Canvas Experiment Report

Date: 2026-05-28

## Objective

Use JEPA more literally for the sleep-lifelog task by making the hidden submission-like block itself the prediction target. The main goal was not to blend another arbitrary feature into probabilities, but to learn a context-to-target representation:

- context: same-subject outside-block labels, outside-block raw canvas summaries, outside-block base predictions, block position/calendar
- target: hidden-block raw canvas latent summary
- predictor: context-only latent prediction
- regularizer: LeJEPA-style SIGReg to reduce collapsed or highly anisotropic embeddings

This is intentionally stricter than the previous Block-Canvas experiments. The predictor does not receive target-block raw latent, target-block base prediction, or target-block labels as context.

## New Artifacts

- `jepa/lejepa_block_canvas.py`
- `jepa/lejepa_block_canvas_l0p05_d32_candidate_summary.csv`
- `jepa/lejepa_block_canvas_l0p2_d32_candidate_summary.csv`
- `jepa/lejepa_targetwise_blend_summary.csv`
- `jepa/lejepa_targetwise_geometry_holdout_summary.csv`
- `jepa/lejepa_targetwise_context_compatibility.csv`
- `jepa/lejepa_targetwise_sigreg_residual_health.csv`
- `jepa/submission_lejepa_targetwise_strict_best_scale0p5.csv`
- `jepa/submission_lejepa_targetwise_safe_l005_q2l02_scale0p5.csv`

## Architecture

The implemented model has three parts:

1. Context encoder
   - consumes only information outside the hidden target block
   - learns a compact subject/block context state

2. Target encoder
   - consumes the hidden block's raw-canvas summary
   - produces the target latent to be predicted

3. Predictor
   - maps context latent to target latent
   - trained with MSE plus SIGReg

SIGReg diagnostics were computed for context, target, and predicted embeddings. This was added because the LeJEPA paper argues that useful JEPA latents should be closer to isotropic Gaussian structure instead of narrow collapsed manifolds.

## Main Runs

### `sig_lambda=0.05`, `emb_dim=32`

Best direct candidate:

- `submission_lejepa_block_canvas_l0p05_d32_top_scale1p0.csv`
- full OOF: `0.563788`
- delta vs stage2 base: `-0.003743`
- bad-axis projection ratio: `0.0618`
- raw-good ratio: `0.2039`

Latent health:

- context effective rank: `2.83`
- target effective rank: `14.33`
- predicted effective rank: `5.58`

Interpretation: target latent is meaningfully rich, but context and predicted latents remain compressed.

### `sig_lambda=0.20`, `emb_dim=32`

Best direct candidate:

- `submission_lejepa_block_canvas_l0p2_d32_top_scale1p0.csv`
- full OOF: `0.563566`
- delta vs stage2 base: `-0.003965`
- bad-axis projection ratio: `0.0208`
- raw-good ratio: `0.1610`

Latent health:

- context effective rank: `3.32`
- target effective rank: `9.52`
- predicted effective rank: `5.39`

Interpretation: stronger SIGReg slightly improves OOF and bad-axis projection, but increases some candidate-level JEPA bad-ratio risk.

## Target-Wise Blend

The strongest practical candidate was made by selecting target-wise JEPA residual operations instead of applying one global JEPA correction to all targets.

Selected operations for `submission_lejepa_targetwise_strict_best_scale0p5.csv`:

- Q1: `l0p2 pred_emb_12`
- Q2: `l0p2 target_emb_12`
- Q3: `l0p2 target_norm`
- S1: `l0p05 pred_rate_S1`
- S2: `l0p05 pred_rate_S1`
- S3: unchanged
- S4: `l0p2 absresid_emb_06`

Full OOF:

- base stage2: `0.567531`
- candidate: `0.564420`
- delta: `-0.003111`

Target deltas:

- Q1: `-0.002181`
- Q2: `-0.003410`
- Q3: `-0.006622`
- S1: `-0.003458`
- S2: `-0.003171`
- S3: `0.000000`
- S4: `-0.002934`

## Guardrail Results

### Geometry Holdout

`submission_lejepa_targetwise_strict_best_scale0p5.csv`

- folds: `8`
- mean base: `0.553739`
- mean candidate: `0.550913`
- mean delta: `-0.002825`
- median delta: `-0.002890`
- win rate: `1.000`

Target holdout deltas:

- Q1: `-0.003171`
- Q2: `-0.004936`
- Q3: `-0.007883`
- S1: `-0.002067`
- S2: `-0.000544`
- S3: `0.000000`
- S4: `-0.001173`

### Context-Target Compatibility

Compared against the known public-tested raw timeline rescue submission:

- raw timeline rescue KL mean: `0.056247`
- LeJEPA strict scale0.5 KL mean: `0.054684`
- delta: `-0.001563`

Other compatibility improvements:

- abs-logit compatibility delta: `-0.027873`
- Q3 KL delta: `-0.003275`
- block p90 KL delta: `-0.002296`

Scale 0.75 and 1.0 had lower OOF but worse compatibility, so scale 0.5 is the safer submission.

### Residual Health

Best residual-health candidate among the target-wise submissions:

- `submission_lejepa_targetwise_strict_best_scale0p5.csv`
- LeJEPA residual health: `7.199348`
- all-target SIGReg global: `7.919171`
- Q3/S4 SIGReg global: `2.899469`
- public-axis SIGReg global: `13.266953`
- all-target covariance eigen CV: `0.967435`

## Submission Integrity

`jepa/submission_lejepa_targetwise_strict_best_scale0p5.csv`

- shape: `(250, 10)`
- keys match sample submission
- no NaN
- min probability: `0.060040`
- max probability: `0.980737`

Mean probability movement vs stage2:

- Q1: `-0.006649`
- Q2: `-0.014112`
- Q3: `-0.059122`
- S1: `-0.003358`
- S2: `-0.003423`
- S3: `0.000000`
- S4: `+0.011415`

## Current Best Submission Candidate

Primary candidate:

`jepa/submission_lejepa_targetwise_strict_best_scale0p5.csv`

Why this one:

- lower full OOF than raw timeline rescue
- wins all 8 geometry holdout folds
- improves context-target compatibility vs the known public-tested raw timeline rescue
- has the best residual health among the LeJEPA target-wise candidates
- avoids the higher scale 0.75/1.0 over-movement that looked better in OOF but weaker under guardrails

Expected public LB:

- conservative range: `0.5765 - 0.5780`
- optimistic range if compatibility transfers: `0.5758 - 0.5768`

This is not credible evidence for `0.54`. The experiments show a real JEPA signal, especially Q3/Q2 and some S targets, but the signal size is still in the small-residual regime. To reach `0.54`, the bottleneck is likely not "more blending"; it requires either a stronger hidden-block generator, a discovered target construction rule, or a materially better public/private geometry model.
