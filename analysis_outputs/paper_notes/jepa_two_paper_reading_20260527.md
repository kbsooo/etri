# JEPA Two-Paper Reading Notes 2026-05-27

Scope: read `jepa/ijepa.pdf` and `jepa/lejepa.pdf`, then translate the usable ideas into the current sleep-lifelog multi-label LogLoss work.

## 1) I-JEPA: What Matters

Paper identity:

- File: `jepa/ijepa.pdf`
- Title: *Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture*
- Pages: 17

Core mechanism:

- I-JEPA predicts target representations from a context representation, not pixels/tokens.
- The target encoder produces patch-level representations for the full image. Target blocks are selected from the target encoder output.
- A context encoder sees the visible context patches. A lightweight predictor receives the context output plus positional/mask tokens and predicts each target block representation.
- The loss is average L2 distance between predicted target-block representations and target-encoder target-block representations.
- The target encoder is an EMA copy of the context encoder.

Design details that matter:

- Multi-block target prediction is important: several relatively large target blocks are better than small/local targets.
- Context must be informative and spatially distributed, not a tiny local crop.
- Masking the target encoder output, rather than masking the input before target encoding, produces more semantic targets.
- Predictor bottleneck matters. A predictor can be deep enough to solve the relation, but narrow enough not to become a decoder that reconstructs low-level noise.
- The paper’s energy view is compatible/incompatible pair scoring: low energy for compatible context-target pairs.

Translation to this competition:

- Do not treat individual targets as independent pixels. The useful target blocks are hidden semantic blocks:
  - stress/quality target block: `Q3/S4`
  - subjective-intervention/counter-context block: `Q1/Q2/S1/S2/S3`
  - Q-only and S-only blocks are secondary, not primary.
- Existing evidence agrees: single-target grafts were weak, while Q3/S4 preservation plus context-only row correction worked.
- The I-JEPA lesson is not "inject latent residuals directly." It is "predict or constrain target-block representations from context-block representations."
- For this dataset, "position tokens" should map to row/subject/time/mask metadata:
  - public-mask membership
  - raw05-compatible row risk
  - subject/date neighborhood
  - pseudo-sequence/episode bucket
- Target masking at the encoder output maps to using candidate/logit residual representations after model/candidate encoding, not raw input feature imputation.

Immediate I-JEPA action:

- Keep using context-to-target ridge energy as a compatibility score.
- Make the target blocks larger and more semantic: Q3/S4 as a unit, not Q3 alone.
- Keep row gates as position-conditioned predictors: public-risk/bad-axis gates decide where the context-to-target move applies.

## 2) LeJEPA: What Is New Versus I-JEPA

Paper identity:

- File: `jepa/lejepa.pdf`
- Title: *LeJEPA: Provable and Scalable Self-Supervised Learning Without the Heuristics*
- Pages: 50

Core mechanism:

- LeJEPA defines JEPA by two conditions:
  - one view's embedding should predict another view's embedding
  - embeddings must be non-degenerate.
- The paper argues that the desirable embedding distribution is isotropic Gaussian.
- It introduces SIGReg, a sketched isotropic Gaussian regularizer.
- SIGReg projects embeddings onto random 1D directions and applies a statistical goodness-of-fit test against the standard Gaussian.
- The recommended statistic is Epps-Pulley because it uses characteristic functions, is differentiable, bounded, scalable, and friendly to distributed averaging.
- The full LeJEPA loss is prediction loss plus `lambda * SIGReg`.
- The training loss is reported as informative for model selection, unlike many SSL losses.

Important implementation details:

- Random projection directions are resampled; SGD accumulates directional coverage over time.
- A modest number of directions can work because neural embeddings are smooth and directions accumulate across steps.
- Default-like guidance from the paper: `lambda` around `0.05`, multiple views, Epps-Pulley with a small quadrature grid.
- It avoids teacher-student/stop-gradient as collapse-prevention heuristics because SIGReg handles non-degeneracy.

Translation to this competition:

- Our previous JEPA branch had prediction energy, but weak explicit non-degeneracy control.
- Direct latent residual/Q2 variants probably failed because they made public-risk axes anisotropic or collapsed into a bad low-dimensional residual direction.
- LeJEPA says a candidate residual representation should be judged by two terms:
  - prediction/compatibility: context block predicts target block
  - distribution health: residual embeddings are not collapsed, anisotropic, or concentrated on one public-risk axis.
- The relevant "embedding" here is not a neural hidden vector. It can be:
  - row-level logit residual versus raw05
  - context residual block `Q1/Q2/S1/S2/S3`
  - target residual block `Q3/S4`
  - public-axis projected residual features
  - subject/episode prototype residual vector
- LeJEPA also gives a better unsupervised model-selection proxy:
  - current score: actual-anchor ranker + posterior + raw-axis + bad-axis
  - LeJEPA-style score: current score + small SIGReg penalty on row residual embeddings.

## 3) Key Difference Between I-JEPA and LeJEPA for Our Work

I-JEPA gave us the block design:

- context block predicts target block
- target should be semantic and multi-cell
- prediction should happen in representation/logit space, not raw feature reconstruction
- row gates behave like positional conditioning

LeJEPA gives us the missing regularizer:

- prediction compatibility alone is not enough
- candidate residual embeddings should be isotropic/healthy
- random-projection Gaussian tests are a cheap way to detect collapsed or one-axis candidate moves
- the loss itself can be used as a model-selection signal

Current interpretation:

- `energyfront_a190aa25` is strong on actual-anchor but not necessarily LeJEPA-healthy.
- `efmicro` and `efback` candidates improve bad-axis/posterior, but should now be checked for residual isotropy.
- If a candidate improves context-target energy while making residual embeddings more Gaussian/isotropic, it deserves higher priority than a candidate that only wins one axis.

## 4) Concrete Next Experiments

Experiment A: LeJEPA SIGReg candidate audit

- Treat each candidate's row-level logit residual versus raw05 as an embedding matrix `Z`.
- Standardize/whiten lightly per target block.
- Compute random-projection Epps-Pulley SIGReg scores for:
  - all seven targets
  - context block `Q1/Q2/S1/S2/S3`
  - target block `Q3/S4`
  - public-axis features, if available.
- Join SIGReg with existing priority metrics.
- Success criterion: find candidates with similar actual-anchor but lower SIGReg/bad-axis/posterior.

Experiment B: SIGReg-gated row moves

- During logit-space stitch, apply a row move only when it improves both:
  - row-level bad-axis contribution
  - local SIGReg projection discrepancy.
- This is the LeJEPA version of the existing bad-axis gate.

Experiment C: Isotropic residual backoff

- For top candidates, interpolate/backoff toward raw05 or low-bad donors only along directions that reduce anisotropy.
- This is likely safer than direct residual injection.

Experiment D: Multi-view episode LeJEPA score

- Define views as subject-neighbor, date-neighbor, public-mask-neighbor, and candidate-family-neighbor predictions.
- Score a candidate by whether these views predict a shared global center and whether the view embeddings remain isotropic.
- This maps directly to the LeJEPA "views predict global center + SIGReg" formulation.

## 5) Updated Rule for Candidate Ranking

Do not use JEPA energy alone as a submission criterion.

Preferred ranking should now be:

1. raw05-compatible actual-anchor and posterior guardrails
2. hidden-block compatibility energy
3. bad-axis / public-axis safety
4. LeJEPA SIGReg residual health
5. integrity and submission format checks

Expected practical effect:

- Some high-actual candidates may be demoted if they are anisotropic or collapsed into one residual direction.
- Some risk-none middle candidates may be promoted if their residual distribution is healthier.
- This should reduce overfitting to our public-LB inverse ranker and make the JEPA branch less brittle.
