# I-JEPA and LeJEPA Reading Notes

Source PDFs:

- `jepa/ijepa.pdf`: Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture.
- `jepa/lejepa.pdf`: LeJEPA: Provable and Scalable Self-Supervised Learning Without the Heuristics.

This note focuses on what changes for our sleep/lifelog multilabel task, not on generic paper summary.

## I-JEPA Core Mechanics

I-JEPA trains a context encoder, target encoder, and predictor.

- The target encoder embeds the full image first.
- Target blocks are then sampled from the target encoder output.
- The context encoder only receives the context view.
- The predictor receives context representations plus target-position mask tokens.
- The loss is L2 distance between predicted target representations and target encoder representations.
- The target encoder is an EMA copy of the context encoder.

Important design choices from the ablations:

- Predicting target encoder output beats predicting pixels by a large margin.
- Masking target blocks after the target encoder output is much better than masking input patches before the target encoder.
- Multiple target blocks matter: 4 target blocks strongly beat 1 or 2 in the reported low-shot probe.
- Context must be large and informative; shrinking context hurts.
- Target blocks must be semantic-scale blocks, not tiny random cells.
- The predictor needs enough capacity; deeper predictor helped in the reported ablation.

Implication for our work:

- Raw timeline reconstruction is closer to MAE than I-JEPA if the model predicts raw sensor values.
- Our target should be a latent hidden-block state, not raw rows, raw bins, or direct probabilities.
- The target should be built at block level after an encoder sees the whole target block.
- Context should be the surrounding subject timeline with target block removed, plus position/block tokens.
- Several hidden-block-shaped target masks per subject should be sampled during training.

## LeJEPA Core Mechanics

LeJEPA argues that JEPA embeddings should follow an isotropic Gaussian distribution.

The core claim is practical for our setting:

- Anisotropic embeddings amplify linear-probe bias and variance.
- Low-rank or collapsed shortcut embeddings can look useful in training but become brittle downstream.
- Matching only mean/std/covariance is insufficient because finite moment matching can miss degenerate structures.
- LeJEPA uses SIGReg, a sliced characteristic-function test, to push embeddings toward isotropic Gaussian.
- It combines prediction/invariance loss with SIGReg using one trade-off hyperparameter.
- It removes reliance on stop-gradient, teacher-student, prototypes, and complicated schedules.

SIGReg mechanics:

- Project embeddings onto many random 1D directions.
- For each projected slice, compare the empirical characteristic function against standard normal.
- Average the slice losses.
- Resample directions across steps.
- The paper recommends Epps-Pulley style characteristic-function statistics because gradients are bounded and distributed training is simple.

Useful defaults from the paper:

- Start with `lambda = 0.05` for the SIGReg/prediction trade-off.
- 17 integration points and range `[-5, 5]` are robust defaults.
- Hundreds to low-thousands of random slices are enough in their vision experiments.
- Batch sizes as low as 128 were workable in their ImageNet-1K ablation, but our tabular/block setting may need grouped mini-batches by subject/block.

Implication for our work:

- Our JEPA latent features may have failed public guardrails because they were predictive but anisotropic or shortcut-heavy.
- The right diagnostic is not only OOF log loss. We need covariance spectrum, effective rank, Gaussianity/slice tests, and nested geometry survival.
- A post-hoc residual scan over JEPA latents is a high-overfit layer. LeJEPA suggests training the representation itself to be probe-friendly.

## What Prior Experiments Underused

Prior JEPA-style work in this directory already found real residual signal, but it was unstable:

- Raw feature JEPA reduced full OOF but failed nested geometry.
- Neural masked-grid JEPA learned something useful but was closer to raw reconstruction than latent-target prediction.
- Residual probes selected row-level corrections and overfit public geometry.
- Axis capping reduced obvious public-bad movement but did not solve representation brittleness.

From I-JEPA and LeJEPA, the missing pieces are:

- true output-level target masking;
- hidden-block-shaped semantic targets;
- target-position conditioning;
- multiple target blocks per subject;
- latent distribution control with SIGReg;
- validation based on representation stability, not only row log-loss deltas.

## Recommended Reframe

For this competition, the image analogue is a subject timeline canvas.

- Image: one subject timeline.
- Patches: day/time/modality/measurement-process tokens.
- Semantic target: a real submission-like hidden block.
- Context: the same subject timeline with hidden block removed, including known train labels outside the target.
- Target latent: encoded hidden-block label/sensor/rhythm state.
- Predictor input: context latent plus block-position tokens.
- Probe target: 7 target probabilities or block-rate/count distributions.

The JEPA target should not be the final probability vector itself. It should be a latent state that makes downstream target prediction easy.

## Next Experiment Ideas

### 1. LeJEPA Block-Canvas

Train on subject-level block canvases.

- Target blocks use actual geometry-fold hidden-block shapes.
- Target encoder sees target block canvas and produces target latent.
- Context encoder sees the subject canvas with target block removed.
- Predictor predicts the target latent from context latent and block-position tokens.
- Loss: latent MSE plus SIGReg on context, target, and predicted latents.
- Probe: frozen latent plus existing stage2/rhythm/measurement-process features.

Success gate:

- nested geometry mean delta below `-0.003`;
- at least 5 of 7 targets non-positive in nested geometry;
- public-bad-axis projection below `0.05`;
- effective-rank collapse avoided.

### 2. SIGReg Retrofit Audit

Before training a full LeJEPA, audit existing JEPA latent files.

- Compute covariance eigenvalue spectrum, effective rank, condition number.
- Compute random-slice normality loss approximating SIGReg.
- Compare stable vs failed JEPA candidates.
- Try post-hoc whitening/Gaussianization before residual probes.

Purpose:

- Verify whether public-failed JEPA latents are indeed anisotropic/shortcut-heavy.
- Cheaply test LeJEPA's diagnosis before expensive training.

### 3. Output-Masked Raw Timeline I-JEPA

Rebuild raw timeline JEPA so target masking happens after target encoding.

- Encoder processes full raw timeline canvas into patch tokens.
- Target block tokens are selected from encoded output.
- Context encoder processes non-target patches only.
- Predictor uses mask/position tokens to predict target encoded tokens.
- Add SIGReg to the patch/block latents.

This differs from earlier raw reconstruction by making the prediction target latent, not raw sensor values.

### 4. Count/Rank LeJEPA for Q Targets

For Q1/Q2/Q3, train target block latent to represent count/rank distribution.

- Target latent encodes block positive count, entropy, boundary states, and subject-relative rank.
- Context predicts this latent from surrounding known labels and behavior proxies.
- SIGReg prevents the count latent from degenerating into a few brittle axes.

This is better aligned with the old ordinal/count insight than post-hoc probability correction.

### 5. Axis-Adversarial LeJEPA

Combine SIGReg with an explicit penalty against the known failed public direction.

- Main loss: target latent prediction.
- Regularizer: SIGReg.
- Guardrail: projection penalty or gradient reversal against the stage2-to-ordinal bad axis.

This should be applied only after the representation proves useful in nested geometry, because axis penalties can hide real signal.

## Immediate Takeaway

The next big JEPA attempt should not be another residual feature scan.

The target should be a learned hidden-block latent, and the latent must be made probe-friendly by design. I-JEPA supplies the masking/semantic-target recipe; LeJEPA supplies the anti-collapse and anti-anisotropy recipe.
