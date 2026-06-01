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
