# HITL Experiment Log

Human-in-the-loop experiments live here. New runs use the `hNNN_...` prefix so
we can distinguish user-steered tests from the earlier autonomous `eNNN_...`
search.

## Current Baseline

- Public best: `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`
- Public LB: `0.5761589494`

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
