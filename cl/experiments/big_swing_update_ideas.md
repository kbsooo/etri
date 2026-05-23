# Big-swing update ideas for one-shot score jumps

Goal: stop doing tiny anchor-polish updates. These are high-variance ideas meant to change the structure of the solution enough that a large public/private improvement is possible if the core assumption is right.

## Current premise

Known live score region is around the temporal-smoothing anchor, but that family is mostly exploitation. S2-only sparse updates are too small to be a 0.5x path. A true jump likely requires changing the prediction regime for multiple targets at once or introducing a new representation family.

## Big bet 1 — Treat the task as semi-supervised graph label propagation, not tabular prediction

### Hypothesis
Train/test are same-subject interleaved state-completion. Sensor features are weaker than the graph structure: subject, date proximity, weekday/routine similarity, and behavioral-state similarity.

### Update
Build a graph over all subject-days, including test days. Edges:
- same subject temporal distance;
- same subject same weekday/rank-in-month;
- feature-space kNN using existing no-flat/hourly features;
- sleep-window/routine-state kNN.

Run label propagation / harmonic function / graph Laplacian smoothing per target, with target-specific edge mixtures.

### Why this is big
It abandons per-row classifier thinking. If the public split is mostly missing labels in a subject-day graph, this can beat logistic/trees by a lot.

### Risk
If public/private is more future/tail than interleaved, graph edges leak the wrong state and over-smooth.

### First implementation
No deep learning needed. Build sparse graph and solve:

```text
p_test = weighted average of known labels via graph diffusion
final = blend(base_model, graph_diffusion)
```

Start target groups:
- Q1/S1/S2/S3/S4 aggressive graph;
- Q2 conservative graph;
- Q3 base/frozen.

## Big bet 2 — Multi-target label-structure model / label imputation

### Hypothesis
Targets are not independent. Some labels co-occur as latent daily condition: poor recovery, irregular routine, high stress, sleep disturbance.

### Update
Use train labels to learn a low-dimensional label-state model, then infer missing test labels jointly from available feature predictions + temporal smoothers.

Options:
- Gaussian/copula over logits;
- Ising-like binary label model;
- matrix factorization over subject-day x target with temporal regularization;
- EM where base predictions are noisy observations and label-state latent variables couple targets.

### Why this is big
All current methods predict each target mostly separately. A correct joint label prior can move many targets coherently.

### Risk
Small labels make correlation estimates noisy; Q3 may poison the latent state.

### First implementation
OOF/base logits + temporal smoother logits -> fit rank-2 or rank-3 label factor model. Generate candidates:
- all-target joint except Q3;
- S-only joint;
- Q1/S4/Q2 hard-target joint with Q2 capped.

## Big bet 3 — Cross-night episode reconstruction, not calendar-day features

### Hypothesis
The current feature tables still misalign important evidence. Labels correspond to a sleep episode crossing lifelog_date evening and next morning, not a calendar day.

### Update
Rebuild raw/event-derived features around inferred sleep episode windows:
- evening pre-sleep 18-03;
- inactive/screen-off/dark longest block;
- wake fragmentation/interruption counts;
- next-morning activation after sleep;
- mismatch between intended sleep window and actual device silence.

### Why this is big
If alignment is wrong, no amount of model tweaking fixes it. Correct episode alignment can move Q/S targets together.

### Risk
Requires raw-ish event tables and careful implementation. If existing prior_sleep_window already captured most of it, incremental gain may be limited.

### First implementation
Mine available feature/raw files for timestamped screen/light/steps/app/HR. Build 3 candidate episode definitions and evaluate Q1/Q2/S4/S1 separately.

## Big bet 4 — Subject-day retrieval / nearest-neighbor analog forecasting

### Hypothesis
For each test day, the best predictor is not a parametric model but similar past days of the same subject or similar subjects.

### Update
For each test day, retrieve nearest labeled days using:
- same subject date proximity;
- same subject behavioral similarity;
- cross-subject normalized routine similarity;
- same weekday/month phase.

Prediction = calibrated weighted label average from retrieved days + base model.

### Why this is big
It directly uses the tiny-data structure. Can outperform global models if individual routines dominate.

### Risk
Nearest neighbors overfit if feature distance is subject identity or missingness artifact.

### First implementation
Create several retrieval spaces:
- S-family routine features;
- Q2 fatigue/recovery features;
- sleep-window features.
Then build target-specific KNN smoothers, not one global smoother.

## Big bet 5 — Public-LB reverse-engineering via target-family tournament

### Hypothesis
The public score feedback can identify which target family changes matter, even without target-level labels, if candidates are designed as orthogonal interventions.

### Update
Stop making mixed candidates. Submit a small tournament of large orthogonal candidates:
1. S-family only aggressive;
2. Q-family only aggressive except Q3;
3. Q1/S4 hard-target calibrator only;
4. full state-completion except Q3;
5. same as 4 but Q2 frozen.

### Why this is big
This converts scarce public submissions into routing information. It can reveal which family carries the score jump.

### Risk
Consumes submissions. Needs discipline not to overinterpret one scalar.

### First implementation
Use existing breakout files, but order them as an experiment rather than “best candidate”.

## Big bet 6 — Real sequence SSL over hourly tokens, not PCA/hand axes

### Hypothesis
Previous latent compression failed because it was linear/day-level. A temporal encoder with crops and modality dropout may discover behavioral states not present in aggregates.

### Update
Build subject-day x 24h x channels tensor. Train BYOL/DiNO-style encoder:
- teacher full-day/cross-night view;
- student morning/evening/night crops;
- modality dropout: screen/steps/light/app/wifi/ble;
- missingness masks included.

Then use prototypes/clusters, not raw embeddings, as features.

### Why this is big
Can create a new representation family independent of existing engineered features.

### Risk
Tiny data and implementation time. Raw latent probes may fail; prototypes may be fragile.

### First implementation
Do not train huge model. Use tiny TCN/GRU encoder, 16-d embedding, KMeans k=4/8/12 prototypes. Evaluate cluster-only and late-blend candidates for Q3/S2/S4.

## Big bet 7 — Prediction distribution surgery / prevalence matching

### Hypothesis
Public failure may be due less to ranking and more to probability calibration/prevalence mismatch. Existing models are too conservative or too over-smoothed for some targets.

### Update
Create targetwise logit transforms:
- shift prevalence up/down;
- temperature sharpen/soften;
- monotone rank-preserving mapping to plausible target rates;
- separate transforms for early/mid/late test positions.

### Why this is big
If AUC/ranking is decent but logloss is bad, calibration surgery can move score more than features.

### Risk
Without target-level public info, this is blind. Can destroy logloss if prevalence guess wrong.

### First implementation
Generate a small set of bold calibration candidates:
- sharpen confident S-family;
- soften Q2/Q3;
- prevalence-lower S2 if sparse/DL both shift lower;
- prevalence-higher Q2 only if public evidence supports smoothing.

## Big bet 8 — Per-subject latent regime classifier

### Hypothesis
Different subjects need different prediction regimes. Some are temporal-smoothing dominated, others feature-model dominated, others prior-dominated.

### Update
Classify subject regimes using train history:
- label autocorrelation strength;
- feature-label predictability;
- routine regularity;
- train/test temporal gap pattern;
- missingness stability.

Apply different candidate families per subject:
- high-autocorr subjects: aggressive graph/temporal smoothing;
- low-autocorr: base/logistic;
- irregular routine: S2 sparse/context;
- Q2 unstable: conservative.

### Why this is big
Current global smoothing weights are blunt. Regime-specific routing can substantially reduce over-smoothing damage.

### Risk
Very small per-subject labels. Regime classifier itself can overfit.

### First implementation
Use unsupervised regime rules, not trained meta-model:
- split subjects by label flip-rate and routine entropy;
- generate two or three routing candidates.

## My recommended big-swing order

### If using public submissions
1. `submission_breakout_state_w03_noq2_noq3_prob.csv` — big state-completion excluding Q2/Q3 risk.
2. `submission_breakout_state_w03_noq3_q2w02_prob.csv` — more direct full temporal-state bet with Q2 capped.
3. `submission_breakout_s_targets_plus_q1dl_prob.csv` — S-family/routine bet.

### If doing more offline work first
1. Graph label propagation / retrieval smoother. This is the highest upside per implementation time.
2. Subject-regime routing over temporal smoother vs base vs sparse S2.
3. Cross-night episode reconstruction if raw timestamp tables are accessible.
4. Sequence SSL only after the graph/retrieval experiments, because it costs more time.

## Bottom line

Small S2 sparse anchor blends are not the 0.5x path. The plausible 0.5x paths are:

- graph/label-propagation state completion;
- target-family breakout candidates;
- subject-regime routing;
- corrected cross-night episode features;
- real temporal SSL prototypes.

The fastest big one to implement next is graph label propagation / retrieval smoothing.
