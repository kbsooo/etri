# All follow-up experiments after smoothing public LB

Public LB provided by user:

- `submission_temporal_state_smoothing_wcap01_prob.csv`: `0.6394201335`
- `submission_temporal_state_smoothing_wcap02_prob.csv`: `0.6311869686`

## Takeaway

`w=0.2` beat `w=0.1` by `0.008233`, so temporal-state smoothing has real signal, but absolute score is still high. The next experiments were:

1. target-isolation LB diagnostic candidates;
2. remove suspicious Q3 smoothing;
3. slightly stronger smoothing candidates;
4. learned temporal calibrator using prev/next/local label-state features.

## Created diagnostic submission files

### Existing/simple smoothing diagnostics

1. `outputs/submission_lbdiag_w02_all_except_q3_prob.csv`
   - `w=0.2` smoothing except Q3 reverted to base.
   - Best first diagnostic: checks whether Q3 smoothing hurt the `0.63118` file.

2. `outputs/submission_lbdiag_w02_q1q2s4_only_prob.csv`
   - only Q1/Q2/S4 use `w=0.2`; other targets base.
   - Checks whether improvement mostly came from hard targets.

3. `outputs/submission_lbdiag_mid_w025_noq3_q2w02_prob.csv`
   - halfway between w=0.2 and w=0.3 for most targets; Q3 base; Q2 stays w=0.2.
   - Tests mild strengthening while avoiding Q3 risk.

4. `outputs/submission_lbdiag_w03_noq3_q2w02_prob.csv`
   - stronger w=0.3-like smoothing, Q3 base, Q2 stays w=0.2.
   - More aggressive monotonicity test.

### Learned calibrator diagnostics

Script: `scripts/53_eval_learned_temporal_calibrator.py`

The learned calibrator uses:

- base probability/logit;
- subject local mean;
- previous/next labels;
- previous/next distance;
- nearest known label;
- local exponential label means at tau 3/7/14/30;
- streak features.

Masked test-pattern validation results:

| target | best learned/calibrated delta vs base |
|---|---:|
| Q1 | -0.0564 |
| Q2 | -0.0638 |
| Q3 | -0.0171 |
| S1 | -0.0101 |
| S2 | -0.0263 |
| S3 | -0.0034 |
| S4 | -0.0359 |

But tail validation is poor for Q1/Q2/Q3, so this family is high-risk. It is useful as a diagnostic, not a confident submission.

Generated candidates:

5. `outputs/submission_learned_calibrator_q1q2s4_blend30_prob.csv`
   - Q1/Q2/S4 only, 30% learned calibrator + 70% base.
   - Shift vs base: Q1 mean 0.0383, Q2 mean 0.0508, S4 mean 0.0184.

6. `outputs/submission_learned_calibrator_q1q2s4_blend50_prob.csv`
   - Q1/Q2/S4 only, 50% learned calibrator.
   - Riskier: Q2 mean shift 0.0849.

7. `outputs/submission_learned_calibrator_q1q2s4_pure_prob.csv`
   - pure learned calibrator for Q1/Q2/S4.
   - Too aggressive: Q1 mean shift 0.128, Q2 mean shift 0.170. Not recommended except as a one-off diagnostic if many submissions remain.

## Recommended public diagnostic order

If only a few submissions remain:

1. `submission_lbdiag_w02_all_except_q3_prob.csv`
2. `submission_lbdiag_w02_q1q2s4_only_prob.csv`
3. `submission_lbdiag_mid_w025_noq3_q2w02_prob.csv`
4. `submission_learned_calibrator_q1q2s4_blend30_prob.csv`

Avoid `learned_calibrator_q1q2s4_pure` unless using it as a risky diagnostic.

## Interpretation matrix

- If `w02_all_except_q3` improves over `0.63118`: Q3 smoothing was hurting; continue with Q3 base.
- If `w02_q1q2s4_only` is close to or better than `0.63118`: improvement is concentrated in Q1/Q2/S4; stop touching S1/S2/S3/Q3.
- If `mid_w025_noq3` improves: stronger smoothing helps; try a more controlled w=0.3 without Q3.
- If `learned_blend30` improves: replace crude exponential smoothing with a learned state calibrator, but keep blend small.

## Current honest stance

The temporal-state hypothesis is now stronger than the sensor-feature hypothesis. However, the public scores are still 0.63x, so no 0.5x-confidence candidate exists yet. The best next move is controlled public diagnostics rather than blind feature expansion.
