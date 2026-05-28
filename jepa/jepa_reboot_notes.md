# JEPA Reboot Notes

## Geometry Nested Definition

Geometry nested validation is a submission-shape nested holdout.

The real submission is not a single future segment. For each subject, hidden rows appear as interleaved blocks surrounded by train rows, for example `T28 S14 T13 S13` or fragmented variants. Geometry folds recreate this inside train by masking subject-local contiguous validation blocks with lengths sampled from the actual submission block lengths.

The nested part means feature/model selection happens on the inner train rows, then the chosen operation is evaluated only on the geometry-masked holdout rows. This catches selection bias that ordinary OOF and repeated subject-half checks miss.

It is stricter than random CV because it tests the exact question we care about: if a same-subject hidden block is removed, can the model infer its local state/rate from the remaining context?

## What Prior Work Says

The most important old result is still the block-rate oracle:

- temporal/subject models are in the low `0.62` range early in the project;
- a full subject-rate oracle is only around `0.5936`;
- a validation block-rate oracle reaches about `0.5179`.

So the missing information is not mainly row-level calibration. It is hidden block state/rate reconstruction.

Strong feature families already found:

- sleep interval / quiet-window reconstruction;
- rhythm regularization and subject-relative deviations;
- measurement-process / wear-compliance / coverage and gap features;
- broad residuals such as Q1 late call usage, Q2 activity transitions, Q3 BLE/HR/presleep context, S-target light/activity/ambience signals;
- public-LB inverse posterior families.

Main failure mode:

- many strong OOF directions are not public stable;
- presleep and JEPA feature gains often align with the observed failed `stage2 -> ordinal` public-bad axis;
- row-level residual feature selection overfits even when subject-half guardrails look good.

## What I-JEPA Says That We Underused

The paper's useful design constraints:

- predict in representation space, not input/value space;
- target blocks are obtained from the target encoder output, not by masking the raw input;
- target encoder is an EMA copy of the context encoder;
- target blocks should be large enough to be semantic;
- context should be large and spatially distributed;
- use several target blocks per sample;
- predictor is conditioned on target-block position/mask tokens and is narrower than the encoder.

Our first JEPA pass violated or weakened several of these:

- PCA/Ridge feature prediction is not an EMA target-encoder JEPA;
- neural grid probe predicted masked grid values, closer to MAE than JEPA;
- target blocks were feature cells/time cells, not subject hidden blocks;
- downstream selection was a greedy residual scan, which is exactly where this dataset overfits;
- validation selected row features instead of learning a block-state representation.

## Reframed JEPA Target

For this competition, the semantic object is not a row. The semantic object is a same-subject contiguous hidden block with a target-rate/state vector.

The JEPA analogue should be:

- image = one subject timeline canvas;
- patches = day x time-window x modality tokens, plus label-context tokens for known train rows;
- target blocks = contiguous day blocks shaped like the real hidden submission blocks;
- target representation = latent block state/rate, not raw sensor values;
- context = distributed surrounding days and non-overlapping sensor/time patches;
- predictor = context latent + positional block tokens -> target block latent;
- decoder/probe = target block latent -> row-target probabilities and block target rates.

This aims at the `0.5179` oracle gap directly.

## Idea Portfolio

### 1. BlockRate-JEPA

Hypothesis: The hidden score wall is block-rate inference. Train a JEPA where the target encoder embeds label blocks from train, while the context encoder sees surrounding sensors, calendar, subject, and adjacent known-label context. The predictor learns to infer the latent label-block representation. At inference, apply it to actual submission blocks.

Implementation:

- construct geometry blocks exactly as `geometry_folds` does;
- target encoder input during training: block labels plus optional same-block sensor summaries;
- context encoder input: all non-target same-subject timeline patches, boundary labels, sensor/rhythm/measurement-process features, block position tokens;
- predictor outputs a latent block vector;
- decoder outputs block target rates plus row-level logits;
- use BCE plus block-rate loss, but put the main loss in latent space.

Why it is JEPA-like:

- context predicts target representation;
- target is block-level semantic representation;
- several target blocks per subject can be sampled per batch.

Validation:

- nested geometry folds only;
- compare to stage2 and public-safe bases;
- reject if nested mean delta is positive or if public-bad-axis projection exceeds a cap.

### 2. True Raw-Timeline I-JEPA

Hypothesis: The raw sensor stream has latent sleep/lifestyle state that aggregated features do not preserve. The model should learn from the subject's full day x time x modality canvas.

Representation:

- per subject, build a `days x time_bins x modalities x channels` tensor;
- channels include value stats, observation count, coverage fraction, first/last observed time, longest gap, missingness;
- include quiet-window/presleep alignment as positional channels.

Masking:

- target blocks: 4 large contiguous day-time rectangles, scale about 15-20% of the subject canvas;
- context: 85-100% of canvas with target rectangles removed;
- targets masked at target-encoder output, not raw input.

Architecture:

- small transformer or Perceiver-style encoder;
- EMA target encoder;
- narrow predictor conditioned on target mask tokens;
- frozen encoder features feed a small target residual head.

Validation:

- pretrain train+submission unlabeled canvases;
- train probe only on train;
- evaluate with geometry nested and axis audit.

### 3. Measurement-Process Teacher JEPA

Hypothesis: Rhythm and measurement-process features are the strongest stable non-label signals, but direct feature scans overfit. Use them as semantic target embeddings instead of direct residual features.

Target encoder:

- embeds rhythm/measurement-process feature families and their subject-relative deviations;
- optionally includes top validated teacher predictions: rhythm combo, measurement-process combo, stage2, public2d/minimax posterior.

Context encoder:

- sees raw/aggregate sensors with some modality/time blocks removed.

Goal:

- learn a compact latent lifestyle/wear-compliance state;
- downstream head predicts labels from this latent, not from thousands of scanned features.

Why this may beat previous MP/Rhythm:

- avoids choosing one top feature per target;
- learns shared state across Q1/Q3/S targets;
- can be regularized with axis-adversarial loss.

### 4. Q-Rank Count JEPA

Hypothesis: Q labels are thresholded individual-average questionnaire values, so the hidden structure is a latent continuous within-subject rank, not a binary row event.

Target representation:

- for Q1/Q2/Q3 blocks, encode block-level positive count, within-subject rank distribution, local trend, and entropy;
- do not force hard 50/50 totals;
- use soft count/rank constraints.

Context:

- known Q labels before/after the hidden block;
- presleep app/activity/stress proxies;
- quiet-window and sleep proxy features;
- subject phase/weekend tokens.

Decoder:

- predicts row logits constrained by a predicted block count distribution.

This is the JEPA version of the old ordinal/count idea, but it predicts counts from context instead of projecting probabilities after the fact.

### 5. Axis-Adversarial JEPA

Hypothesis: JEPA finds real residual structure, but the easiest structure aligns with the public-bad axis. Force the learned representation to keep predictive power while removing the failed direction.

Training:

- add an adversarial head that tries to predict projection onto the `stage2 -> ordinal` bad direction;
- gradient reversal or orthogonal penalty suppresses that component;
- keep target prediction and block-rate losses.

Use:

- combine with BlockRate-JEPA or Measurement-Process Teacher JEPA;
- select candidates under explicit projection caps.

## Recommended Next 3 Experiments

### Experiment A: BlockRate-JEPA Minimal

Build the smallest possible block-level JEPA:

- input features: existing stage2/rhythm/measurement-process/JEPAs plus known adjacent labels;
- target blocks: geometry-fold contiguous blocks;
- target latent: 7 target rates + entropy + first/last label indicators from the target block;
- model: MLP/Transformer set encoder with EMA target projection;
- output: block-rate prediction and row logits.

Success:

- geometry nested mean delta below `-0.002` on stage2;
- at least 5/7 target non-positive nested deltas;
- bad-axis projection below `0.05` for submission variant.

Stop:

- nested mean delta positive in two architecture settings.

### Experiment B: Raw Timeline Masked-Output JEPA

Build true I-JEPA mechanics over raw sensor canvases:

- use 30-min bins over 12:00-36:00;
- channels: count, value mean/min/max/std, coverage, gaps, missingness;
- target masking after target encoder output;
- 4 large target blocks, context 85-100%;
- freeze encoder and train residual head.

Success:

- frozen representation improves at least 3 targets in geometry nested;
- target blocks with large scale beat random/small masks.

Stop:

- representation collapses or only reconstructs missingness without improving labels.

### Experiment C: Q-Rank Count JEPA

Attack Q2/Q3 separately:

- target latent: block Q count, local Q rank, adjacent-label state;
- context: app/activity/presleep/quiet features and known labels around the hidden block;
- decoder predicts row probabilities with soft block-count calibration.

Success:

- Q2 or Q3 geometry delta below `-0.003`;
- no public-bad-axis increase versus stage2.

Stop:

- it behaves like the failed ordinal Q2/Q3 direction.

## Practical Priority

Start with Experiment A. It is the most aligned with the actual oracle gap and can reuse existing parquet features. If A fails, the answer is probably not "more JEPA residual features"; it is that we need a better raw timeline encoder from Experiment B.

