# HITL Experiment Log

Human-in-the-loop experiments live here. New runs use the `hNNN_...` prefix so
we can distinguish user-steered tests from the earlier autonomous `eNNN_...`
search.

## Current Baseline

- Public best: `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv`
- Public LB: `0.5681234831`
- Current high-risk post-H012 sensor: `submission_h020_joint_vector_world_combined_all_k1750_a1_uploadsafe.csv`
- H020 question: whether the public-equation posterior should be completed as a row-level 7-target hidden state rather than independent cells.

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
