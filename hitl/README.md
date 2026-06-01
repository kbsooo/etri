# HITL Experiment Log

Human-in-the-loop experiments live here. New runs use the `hNNN_...` prefix so
we can distinguish user-steered tests from the earlier autonomous `eNNN_...`
search.

## Current Baseline

- Public best: `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv`
- Public LB: `0.5681234831`
- Current promoted post-H012 sensor: none.
- Current H033 conclusion: H032 sibling failures are learnable as phase-lock contrast, but the first independent-cell negative-cost translator does not produce an H012-beating action.

## H033: Phase-Lock Contrastive HS-JEPA

- Script: `hitl/h033_phase_lock_contrast_jepa.py`
- Report: `hitl/h033_phase_lock_contrast_jepa/h033_report.md`
- Decision: diagnostic only, no submission promoted.

### Question

H032 found that H012 is recoverable as a phase point but nearby siblings fail.
Which row-target operations make those siblings fail, and can the learned
phase-lock law reveal a negative-cost move away from H012?

### Main Finding

The phase-lock contrast is learnable, but it is not directly actionable.

- Phase siblings used as contrastive interventions: `4262`.
- Best all-OOF alpha: `100.0`.
- All-OOF MAE/Spearman/pairwise accuracy: `0.000814682` / `0.954416119` /
  `0.912785497`.
- H012-support cells with negative rollback cost: `538/1200`.
- Outside-support cells with negative add cost: `247/550`.
- Generated candidate actions: `83`.
- Best diagnostic candidate: `negative_add_add_k10_a0.1`.
- Best diagnostic pre-state margin versus H012 prediction: `+0.016275125`.
- Public-score permutation p(lower margin): `0.861333333`.
- H025 row-permutation p(higher top1200 gain): `0.710000000`.

### Interpretation

H033 is useful because it separates two claims. The H012-vs-sibling difference
is not random: the contrastive model can predict which generated phase actions
are bad. But the first-order cell coefficients do not translate into safe
probability edits. Even a tiny 10-cell outside-support action is priced much
worse than H012 by the public-free state decoder.

The next high-upside direction should therefore model the translator at the
row-vector/route level, or learn an H012-vs-sibling classifier before
materialization. Do not submit H033 variants.

## H032: H012 Phase-Translator HS-JEPA

- Script: `hitl/h032_h012_phase_translator_jepa.py`
- Report: `hitl/h032_h012_phase_translator_jepa/h032_report.md`
- Decision: diagnostic only, no submission promoted.

### Question

H012 may be a phase point, not only a set of public-core cells. Can a public-free
state/action decoder recover H012 from a dense E247-to-public-posterior phase
diagram, and does that diagram contain a stronger sibling?

### Main Finding

The decoder recovered the existing H012 anchor as the best point.

- Generated phase candidates including anchor: `4263`.
- Best pre-H012 decoder: `geometry` alpha `10.0`, LOO MAE `0.000295413`,
  Spearman `0.950877193`, pairwise `0.923976608`.
- H012 pre-state prediction: `0.563377063`.
- Best non-anchor sibling: `identity_phase_score_all_k120_a0.7_uniform`,
  pre-state prediction `0.573188862`, `+0.009811799` worse than H012 prediction.
- Best non-anchor changed `1080` cells away from H012.

### Interpretation

This is good HS-JEPA evidence but not a new upload. H012 is visible to the
state/action representation without using its public LB as a training label,
so it is unlikely to be arbitrary leaderboard luck. But the phase map did not
find a stronger local continuation. The next useful experiment is a
H012-vs-sibling discriminator or discrete row-target translation law, not
another dense alpha/k/top-k sweep.

## H001: E247-Locked Q2/S1 Transplant

- Script: `hitl/h001_e247locked_q2s1_transplant.py`
- Report: `hitl/h001_e247locked_q2s1_transplant/h001_report.md`
- Decision: diagnostic only, no submission promoted.

### Question

GPT Pro argued that E368 was not a clean Q2/S1 test because its public file
moved a large E365-like body away from E247. H001 froze the E247 body and
transplanted only `logit(E368) - logit(E365)` on Q2 and S1.

### Main Finding

The body-confound diagnosis is strong.

- E368 public file vs E247 moved non-Q2/S1 cells by `1.452454` L1, dominated by
  Q1 `1.312944`.
- Pure E247-locked Q2/S1 transplant moved only Q2/S1, with non-Q2/S1 L1 near
  zero.
- The Q2 action is dangerous in the E365 frame but close to neutral in the E247
  frame: `q2_cos_e323_bad_vs_e365 = 0.591735`, while
  `q2_cos_e323_bad_vs_e247 = -0.014661` for the full all-row transplant.

### Submission Decision

No H001 file was promoted. All 140 generated H001 variants failed the current
conservative stress-ready gate:

- `e363_submission_gate`: 0 / 140
- `top1_rate`: 0 for H001 candidates
- `top10_rate`: 0 for H001 candidates
- Scenario-gated support rows: none

Best diagnostic row by H001 score:

- `h001_e247locked_transfer_top20_q20p0_s10p5`
- It is an S1-only tiny edit on E247.
- It is useful as a signal probe, not as a submission candidate.

### Interpretation

H001 does not kill the Q2/S1 hidden-state idea. It kills the previous way of
materializing it: transplanting row/state action without an action-benefit
target. The next useful test should learn when this E247-locked action helps,
not just sweep action amplitude.

### Next Experiment

H002 should build an action-benefit selector:

- Base body remains E247.
- Candidate action remains Q2/S1-only.
- Learn or approximate which rows should receive the action using OOF/local
  action-health, public-free row states, and bad-axis avoidance.
- The pass condition should be action-specific, not inherited wholesale from
  broad E363 submission gates.

## H002: E247-Locked Q2/S1 Action-Benefit Selector

- Script: `hitl/h002_e247locked_q2s1_action_benefit_selector.py`
- Report: `hitl/h002_e247locked_q2s1_action_benefit_selector/h002_report.md`
- Decision: diagnostic only, no submission promoted.

### Question

If H001's failure was caused by applying Q2/S1 action to the wrong rows, can an
action-benefit latent select safer rows while keeping the E247 public-best body
fixed?

### Main Finding

Row selection works as a risk filter but not as a submission signal.

- Generated `289` E247-locked candidates.
- `99` candidates passed the local action-context sanity check.
- `0` candidates passed the conservative stress-ready gate.
- No `_uploadsafe.csv` was created.
- The top diagnostic candidate is
  `h002_e368_minus_e365_benefit_top25_q20p25_s11p0`.

Top diagnostic movement:

- Q2 movement is very small: `l1_Q2 = 0.003477`.
- S1 movement is moderate-small: `l1_S1 = 0.042622`.
- Q2 E323-axis exposure in the E247 frame is favorable:
  `q2_cos_e323_bad_vs_e247 = -0.068400`.
- Action is concentrated on the intended latent rows:
  `q2_benefit_minus_danger = 0.440324`,
  `s1_benefit_minus_danger = 0.402223`.

### Interpretation

H002 weakens the specific hypothesis that the current Q2/S1 hidden lifestyle
state can beat E247 by row selection alone. The selector can identify
high-benefit / low-risk rows, but the resulting safe edits are too small and do
not activate the existing local stress sensors.

The useful next question is not "which Q2/S1 rows?" anymore. It is whether the
hidden lifestyle state must be translated through a broader target interaction
or calibration layer, especially Q2 with S1/S3 or Q-group priors, while keeping
the E247 body protected.

## H003: HS-JEPA Prototype

- Script: `hitl/h003_hs_jepa_prototype.py`
- Report: `hitl/h003_hs_jepa_prototype/h003_report.md`
- Decision: diagnostic only, no submission promoted.

### Question

Can HS-JEPA, Human-State Joint Embedding Predictive Architecture, turn the
human/social lifestyle stories into a context-predictable hidden state and then
translate that state safely on top of the E247 public-best body?

### Main Finding

HS-JEPA produced a meaningful hidden-state representation, but the first
probability translator is not safe enough to submit.

- Context views reconstruct several human-state targets strongly:
  `measurement_wear_confidence` R2 `0.694487`,
  `social_overload` R2 `0.625023`,
  `badnight_aftereffect` R2 `0.624071`,
  `commute_pressure` R2 `0.621365`.
- The latent is alive but not clean: 8 PCA dims explain `0.758982` variance,
  participation ratio is `5.344604`, anisotropy is `2.681719`, and projection
  kurtosis is high.
- Full-latent target translation failed the gate: `target_gate_count = 0`.
- Sparse episode-to-target routes did survive: `route_gate_count = 20`.

Strongest gated routes:

- `home_recovery -> S3`: subject5 delta `-0.013044173`
- `bedtime_arousal -> S3`: subject5 delta `-0.010444948`
- `social_overload -> S3`: subject5 delta `-0.009121835`
- `routine_anchor_recovery -> S2`: dateblock5 delta `-0.005921853`
- `badnight_aftereffect -> Q3`: subject5 delta `-0.004585621`
- `routine_anchor_recovery -> Q2`: subject5 delta `-0.003137053`

### Submission Decision

No H003 file was promoted.

Generated diagnostic candidates:

- `submission_h003_semantic_tiny_11e7aa3b.csv`
- `submission_h003_semantic_micro_ebeebefd.csv`
- `submission_h003_semantic_tail_micro_fbdd9c4f.csv`

The best diagnostic candidate was `submission_h003_semantic_tiny_11e7aa3b.csv`,
but the selector marked it `below_selector_resolution`. It moved all 7 labels
across `1750` cells, so it is too broad for a safe HITL submission.

The diagnostic file was still submitted as a public sensor:

- `submission_h003_semantic_tiny_11e7aa3b.csv`: public LB `0.5763763885`
- Delta versus E247 best `0.5761589494`: `+0.0002174391`

This confirms the local decision. HS-JEPA found state signal, but the first
all-target translator was too broad and lost public score.

### Interpretation

H003 supports the core HS-JEPA idea: human/social episode states can be learned
as a latent world model, and some episode-to-target routes contain real signal
beyond matched nulls. It rejects the first naive materialization: using one
monolithic latent translator over all targets.

The next useful test is H004: keep E247 fixed and materialize only sparse,
route-specific actions, especially S3-only routes from
`home_recovery`, `bedtime_arousal`, and `social_overload`, with optional
separate Q2/Q3 micro-routes.

## H004: HS-JEPA Sparse Routes

- Script: `hitl/h004_hsjepa_sparse_routes.py`
- Report: `hitl/h004_hsjepa_sparse_routes/h004_report.md`
- Decision: information sensor only, no submission promoted.

### Question

After H003 showed that broad all-target HS-JEPA translation loses public score,
can we keep E247 fixed and translate only the strongest sparse
human-state-to-target routes?

### Main Finding

Sparse routing fixed the H003 shape problem but did not yet produce a strict
submission candidate.

- H003 broad move: `1750` changed cells, public LB `0.5763763885`.
- H004 candidates: at most `48` changed cells and at most `2` active targets.
- Best selected file:
  `submission_h004_s3_q3_micro_e221f794.csv`.
- Selector decision: `information_sensor_only`.
- Strict promote count: `0`.
- Information sensor count: `4`.

Strongest bundle stress:

- `q3_badnight -> Q3`: subject5 delta `-0.011851961`, dominance `0.933333`.
- `s3_core -> S3`: subject5 delta `-0.003676805`, dominance `1.000000`.

### Interpretation

H004 supports the sparse-route version of HS-JEPA more than the monolithic
latent version. The best candidate combines `S3` and `Q3` micro-actions and is
locally mean-favorable, but its selector p90 is only `-0.000002924`, far weaker
than the strict public-free threshold. It is not a score submission yet.

The next useful test is not to enlarge all routes. It is to improve the
row/action translator for the two surviving routes:

- `badnight_aftereffect -> Q3`
- `home_recovery + bedtime_arousal + social_overload -> S3`

## H021: Human-State Conditional Vector-Prior Gate

- Script: `hitl/h021_human_state_vector_prior_jepa.py`
- Report: `hitl/h021_human_state_vector_prior_jepa/h021_report.md`
- Selected upload-safe file:
  `submission_h021_agree_h020_k1200_a1_e1546ba9_uploadsafe.csv`

### Question

Can raw human-state context predict the hidden row-level 7-target vector and
use that prior to decide where H020's public-equation vector action is healthy?

### Main Finding

Human-state context is predictive, but not calibrated enough to replace the
public-equation posterior.

- Best train-only human-state vector prior:
  `subject_all_k10`, marginal BCE `0.617584875`.
- Global vector prior marginal BCE: `0.664614445`.
- Direct q_hs regularization is diagnostic-only because it worsens H020
  compatibility.
- The selected H021 action gates H020 by human/H020 direction agreement:
  `1200` changed cells on `248` rows.
- H020-equation delta vs H012: `-0.000684129`.
- H020 gain retained: `0.618866184`.
- Row-permuted human-prior null median is worse by `0.005549353`.

### Interpretation

This is the first clean HS-JEPA bridge from raw human-state context into the
validated public-equation row-vector branch. The latent is useful as an
action-health gate. It is not yet a standalone probability target.

## H022: Human-State Conditioned Vector-World Posterior

- Script: `hitl/h022_hs_conditioned_vector_world_jepa.py`
- Report: `hitl/h022_hs_conditioned_vector_world_jepa/h022_report.md`
- Decision: diagnostic only, no root upload-safe submission promoted.

### Question

Can the H021 human-state vector prior `q_hs` become the actual H020
row-vector posterior prior, rather than only gating H020 after the fact?

### Main Finding

Human-state conditioning helps proposal/search, but not final posterior
selection.

- Best sampled-world config: `hs_b0.1`, config score `0.000277410`.
- `none_b0` config score: `0.000310758`.
- Selected posterior/action: `none_b0_top250_t0.0005`.
- Selected posterior MAE/p90/Spearman:
  `0.000014073` / `0.000026312` / `0.990977444`.
- Best positive human-state posterior in the top group:
  `hs_b0.1_top250_t0.00012`, MAE `0.000024950`.
- All `92` materialized files are `diagnostic_only`.

### Interpretation

H022 rejects the clean but too-strong claim that q_hs is the calibrated
posterior prior. The current HS-JEPA role split is:

- public-equation posterior: calibrated probability/action target;
- human-state q_hs: proposal distribution, gate, and action-health diagnostic.

## H023: Human-State Proposal/Pareto Vector-World Posterior

- Script: `hitl/h023_hs_pareto_proposal_vector_jepa.py`
- Report: `hitl/h023_hs_pareto_proposal_vector_jepa/h023_report.md`
- Decision: diagnostic only, no root upload-safe submission promoted.

### Question

Can q_hs choose among public-compatible vector worlds as a proposal/Pareto
energy, after H022 rejected q_hs as the final posterior prior?

### Main Finding

Public-compatible worlds are human-state-aligned, but q_hs still cannot safely
select the final action posterior.

- Public-error top1000 worlds:
  real human-state energy `4.877889323`, row-permutation null median
  `5.234522555`, p `0.012345679`.
- Selected Pareto posterior:
  `pareto_top1000_lam0.2_t0.00012`.
- Posterior MAE/p90/Spearman:
  `0.000031100` / `0.000059357` / `0.989473684`.
- Human-state KL row-permutation p: `0.016393443`.
- Public-fit row-permutation p: `0.754098361`.
- Root upload-safe H023 files: none.

### Interpretation

H023 is positive representation evidence and negative materialization evidence.
The public-equation vector-world manifold is coupled to human-state geometry,
but the current q_hs energy is not an action-health decoder. The next HS-JEPA
step should learn public/private action health or calibration, using H023
energy as an input rather than as the final selector.

## H024: Action-Health Decoder over Public Sensors

- Script: `hitl/h024_action_health_decoder_jepa.py`
- Report: `hitl/h024_action_health_decoder_jepa/h024_report.md`
- Decision: diagnostic only, no root upload-safe submission promoted.

### Question

Can known public outcomes, good/bad movement axes, and H015-H023 latent sensors
decode which post-H012 action is healthy enough to submit?

### Main Finding

Known public ordering is learnable, but unknown post-H012 actions are not
stable enough to promote.

- Known public sensors used: `20`.
- Best leave-one-out decoder: `geometry`, alpha `100`, MAE `0.000773`,
  Spearman `0.969925`, pairwise accuracy `0.947368`.
- State-only decoder predicts H012 more conservatively:
  `0.567631` vs actual `0.568123`.
- Top unknown diagnostic file:
  `hitl/h015_public_equation_self_feedback/submission_h015_top_all_k100_a0.7_a3e35d5c.csv`.
- Its predicted public median/p10/p90:
  `0.570054` / `0.559653` / `0.580761`.
- Support below H012: `0.15`.
- Permutation p for selected-vs-H012 margin: `0.841`.

### Interpretation

H024 rejects the tempting claim that H015-H023 posterior-completion candidates
can be promoted by a simple public-axis/action-health decoder. The decoder is
good enough to explain known scores, but not stable enough to select a new
post-H012 file. The architecture diagnosis becomes sharper: HS-JEPA already
has public-state posterior generators and human-state geometry; it lacks a
calibrated action-health decoder that transfers to unseen candidate actions.

## H025: Train-Counterfactual Action-Health HS-JEPA

- Script: `hitl/h025_train_counterfactual_action_health_jepa.py`
- Report: `hitl/h025_train_counterfactual_action_health_jepa/h025_report.md`
- Decision: diagnostic only, no submission promoted.

### Question

Can HS-JEPA learn action health without public-LB regression by generating many
train-label counterfactual probability moves, then use that independent
supervision to choose post-H012 test actions?

### Main Finding

Train-side action health exists, but it is not the missing public-safe decoder.

- Row/time OOF action-health Spearman: `0.021090879`.
- Row/time OOF top10 lift: `0.004425758`.
- Leave-proposal-family stress looks strong, but this mostly says the model can
  distinguish proposal families.
- The top H025-ranked files include known public-bad anchors:
  `submission_jepa_latent_q2_w0p45.csv` and
  `submission_jepa_latent_residual_probe.csv`.
- Best unknown selected diagnostic:
  `hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_gain_all_k1750_a1.2_a639be88.csv`.
- That selected diagnostic fails row-placement stress:
  real top1200 gain `19.183437103`, row-permutation p `0.576666667`.

### Interpretation

H025 is an important negative materialization. It rejects the tempting idea that
we can solve action health purely from train labels and then transfer it to the
public-equation world. Train counterfactual supervision learns some local action
geometry, but it also rewards the same Q2/residual shortcut anatomy that public
LB has already punished.

The next HS-JEPA target should be public/private calibration of action health:
train action-health evidence must be combined with a veto or domain-shift term
that recognizes public-bad Q2/residual shortcuts before materialization.

## H026: Public/Private Calibration-Veto HS-JEPA

- Script: `hitl/h026_public_private_calibration_veto_jepa.py`
- Report: `hitl/h026_public_private_calibration_veto_jepa/h026_report.md`
- Decision: diagnostic only, no root upload-safe submission promoted.

### Question

Can we keep the train-side action-health signal from H025 while vetoing the
public-bad Q2/residual shortcut axes that caused H025 to rank known bad files
too highly?

### Main Finding

The veto fixes source-level known-bad ranking, but it does not make a safe
post-H012 action.

- H012 ranks first under the H026 source score: `9.777520`.
- Known public-bad anchors are demoted: E216 `-4.679053`, JEPA Q2
  `-5.856040`, hybrid strict `-7.595414`, JEPA residual `-9.029536`.
- Generated variants: `272`.
- Best diagnostic file:
  `hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k240_a0p35_v0p35_h015_direct_all_a0.1_35c68bc9.csv`.
- It passes the train-action placement stress strongly:
  H025 row-permutation p `0.000000`.
- It fails the public-transfer stress:
  predicted public median `0.574388`, support below H012 `0.166667`,
  and public-score permutation p `0.898000`.

### Interpretation

H026 is a useful negative result. A scalar public-bad shortcut veto can repair
H025's known-anchor sanity problem, but post-H012 action generation still moves
in a public-bad region. The next large experiment should not be another
H025-style cutter. It should define a richer public/private calibration target
or generate actions that are public/private-aware before scoring.

## H027: Born Public/Private-Aware Generator HS-JEPA

- Script: `hitl/h027_public_private_aware_generator_jepa.py`
- Report: `hitl/h027_public_private_aware_generator_jepa/h027_report.md`
- Decision: diagnostic only, no root upload-safe submission promoted.

### Question

Can we repair H026 by making the generator public/private-aware before it
creates candidate cells, using public posterior targets, same-subject
sleep-state memory, human-state agreement, train-action health, and
public-good/bad axes together?

### Main Finding

No. H027 is a stronger negative result than H026.

- Generated variants: `1648`.
- Best diagnostic file:
  `hitl/h027_public_private_aware_generator_jepa/submission_h027_h015_public_feedback_bad_axis_escape_S1S2S3_k80_a0p25.csv`.
- H024 predicted public median: `0.569712`.
- Support below H012: `0.150000`.
- H025 row-permutation p: `0.383333`.
- H024 public-score permutation p: `0.822000`.
- Promoted root submission: none.

### Interpretation

The external V106 memory document supports the repeated-subject hidden-state
story, but H014 and H027 show it is not the main carrier of H012's large public
gain. H027 also rejects the idea that existing H015/H020/H023 posterior targets
can be made H012-beating by adding memory/private-safety constraints at cell
birth.

The next HS-JEPA target should change what is predicted. We need a public/private
calibration representation or a new proposal generator, not another scalar gate
around the same posterior-completion cells.

## H028: Public/Private Action-Gradient HS-JEPA

- Script: `hitl/h028_public_private_gradient_jepa.py`
- Report: `hitl/h028_public_private_gradient_jepa/h028_report.md`
- Decision: diagnostic only, no root upload-safe submission promoted.

### Question

Can HS-JEPA stop predicting posterior probabilities and instead predict the
hidden public/private response field itself: which row-target cell movement from
H012 should lower public LogLoss?

### Main Finding

The response field is learnable on known public interventions, but it does not
extrapolate into a safe H012-improving action.

- Known public sensors used: `20`.
- Selected public-gradient fit: `all`, alpha `100.0`, `88` features.
- LOO MAE: `0.001204883`.
- Permutation p for selected LOO MAE: `0.000000`.
- Generated variants: `820`.
- Best diagnostic file:
  `hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_all_k1200_a0p36_all_3a28ff89.csv`.
- Gradient model expected this move to improve H012 by `-0.004909`.
- H024 predicted public median: `0.576388`, far worse than H012 `0.568123`.
- Support below H012: `0.083333`.
- H025 row-permutation p: `0.710000`.
- H024 public-score permutation p: `0.918000`.

### Interpretation

H028 kills the smooth-gradient version of the post-H012 story. Public outcomes
are not random; the known interventions contain a real coarse geometry. But the
geometry mostly separates the singular H012 point from the rest of the
submission cloud. Moving away from H012 along the learned gradient looks
attractive to the public-gradient model itself, yet the independent H024/H025
stress sees it as ordinary 0.576-level movement.

The next HS-JEPA target should treat H012 as a narrow basin or phase-change
solution. A useful next experiment should ask which invariant made the original
H012 public-equation move special, not how to continue it by a local gradient.

## H029: H012 Needle-Basin Invariant HS-JEPA

- Script: `hitl/h029_h012_needle_basin_invariant_jepa.py`
- Report: `hitl/h029_h012_needle_basin_invariant_jepa/h029_report.md`
- Decision: diagnostic only, no root upload-safe submission promoted.

### Question

If H012 is a narrow basin rather than a smooth local optimum, which invariant is
doing the work: exact support, movement amplitude, target/subject block,
same-subject memory agreement, or exact row-target placement?

### Main Finding

H029 strengthens the needle-basin interpretation.

- Generated variants: `102`.
- Best H024 decoder in this pool: `geometry`, alpha `100.0`, MAE `0.000772855`,
  Spearman `0.969924812`, pairwise `0.947368421`.
- Best diagnostic by the local selector:
  `hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_target_S1_d403217e.csv`.
- H024 predicted public median/p10/p90:
  `0.570494744` / `0.567600462` / `0.573561727`.
- Margin versus real H012: `+0.002371261`.
- Support better than H012: `0.116666667`.
- H024 public-score permutation p: `0.858000000`.
- H025 row-permutation p: `0.613333333`.
- Target-wise row permutation collapses hard: best target-wise row-permuted
  median `0.581149687`.

### Interpretation

The attached V106 document supports same-subject state-conditioned memory as a
real signal, but H029 confirms it is not the main H012 carrier. Memory rollback
and memory-only variants remain far above H012 under stress.

The strongest new clue is row identity. Preserving target-level move
distributions while permuting rows destroys the action. That means H012 is not
just "move S targets this much" or "apply a target prior"; its public-equation
state depends on exact row-target placement.

The next useful big experiment should reconstruct the row-target basin directly,
for example by solving public equations with row identity/subject-state
constraints as first-class variables rather than by continuing or pruning H012.

## H030: Row-Target Identity Public-Equation HS-JEPA

- Script: `hitl/h030_rowtarget_identity_equation_jepa.py`
- Report: `hitl/h030_rowtarget_identity_equation_jepa/h030_report.md`
- Decision: diagnostic only, no root upload-safe submission promoted.

### Question

Can the row-target identity signals found by H016/H019/H020/H029 be moved inside
the public-equation solver itself, as cell-wise allowance priors, instead of
being used as post-hoc gates?

### Main Finding

The row-target identity latent is real enough to anticipate much of H012, but it
is not yet an action-safe translator.

- Fit configs tested: `6528`.
- Generated candidates: `756`.
- Independent H012 held-out check, excluding H012 as equation and excluding
  direct H012/H012-containing priors:
  best `identity_combo` prior predicts H012's E247-relative public delta as
  `-0.007550142` versus actual `-0.008035466`, error `0.000485324`.
- The stronger self-feedback controls using `h012` prior reach about
  `0.000181687` error, but those are not independent evidence.
- Best generated diagnostic by H024:
  `hitl/h030_rowtarget_identity_equation_jepa/submission_h030_e247_post_h012_joint_vector_cell_h012_k1200_a0.55_05a1cf87.csv`.
- H024 predicted public median/p10/p90:
  `0.572160346` / `0.568130288` / `0.575654672`.
- Support better than H012: `0.100000000`.
- H024 public-score permutation p: `0.923333333`.
- H025 row-permutation p: `0.670000000`.

### Interpretation

H030 is the first positive answer to "could we have known H012 was coming?" from
row-target identity priors. The answer is partially yes: exact support, public
cell weights, row subset, and joint-vector state together forecast most of the
H012 public jump.

But the action layer still fails. When those priors are materialized as new
probability moves, H024/H025 price them far above real H012. The bottleneck is
therefore not latent discovery alone. It is the translation law that turns a
valid row-target identity posterior into the exact probability action without
breaking the H012 basin.

## H031: Memory-Conflict Public-Core HS-JEPA

- Script: `hitl/h031_memory_conflict_public_core_jepa.py`
- Report: `hitl/h031_memory_conflict_public_core_jepa/h031_report.md`
- Decision: diagnostic only, no root upload-safe submission promoted.

### Question

The V106 document argues for same-subject sleep-state conditioned memory. H014
showed that H012's gain is mostly in cells where that memory disagrees. Does
that conflict identify an amplifiable public core, or only explain why H012 is
hard to reproduce?

### Main Finding

Memory conflict explains H012 better than memory agreement, but it is not a
safe action by itself.

- H012 changed cells audited: `1200`.
- Memory-disagree cells: `714`.
- H012 gain share in memory-disagree cells: `0.720328567`.
- H012 gain share in memory-agree cells: `0.279671433`.
- Generated H031 candidates: `482`.
- Best diagnostic:
  `hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_swap_S124_core120_a0.28_rb60_r0.35_h012_07347231.csv`.
- H024 predicted public median/p10/p90:
  `0.569809630` / `0.561924630` / `0.581936465`.
- Support better than H012: `0.150000000`.
- H024 public-score permutation p: `0.800666667`.
- H025 row-permutation p: `0.183333333`.

### Interpretation

V106-style memory is a real human-state signal, but H012 is not simply
same-subject continuity. H012's public-equation move lives mostly in cells that
the memory route would not choose.

That is a useful paper-level result: HS-JEPA benefits from a contrastive human
memory view because it reveals where the public-equation posterior is doing
something non-obvious. It is not yet a submission-level result. The current
translator from memory-conflict core to probability action leaves the H012
basin, so the next work should learn the action translator rather than push the
same conflict cells harder.
