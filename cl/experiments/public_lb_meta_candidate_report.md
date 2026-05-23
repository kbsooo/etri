# Public-LB-informed meta candidate experiments

## Context

Known public LB feedback from user/report:

- `submission_temporal_state_smoothing_wcap01_prob.csv`: `0.6394201335`
- `submission_temporal_state_smoothing_wcap02_prob.csv`: `0.6311869686`

So the strongest live hypothesis is not “more raw sensor features”; it is same-subject temporal state completion/interpolation.  This report builds more serious candidates by treating `w=0.2` temporal smoothing as the public-supported anchor and applying only controlled residuals from locally validated side tracks.

## Local evidence used

### Temporal smoothing masked validation

Targetwise best smoothing deltas vs base under test-pattern masks:

| target | best delta |
|---|---:|
| Q1 | -0.0435 |
| Q2 | -0.0615 |
| Q3 | -0.0243 |
| S1 | -0.0269 |
| S2 | -0.0429 |
| S3 | -0.0072 |
| S4 | -0.0431 |

But public LB absolute score is still `0.631`, so we should not blindly increase smoothing; use target-isolation diagnostics.

### Learned temporal calibrator

Test-pattern masks show large gains, especially Q1/Q2/S4, but tail split says Q2/Q3 are risky:

- Q1 test-pattern delta `-0.0564`, tail near flat at small blend.
- Q2 test-pattern delta `-0.0638`, but tail worsens `+0.0179` even at small blend.
- S4 test-pattern delta `-0.0359`, tail improves around `-0.0047` at small blend.

Therefore learned calibrator should be a small diagnostic, not a pure replacement.

### Tiny-DL golf

Tiny DL has the cleanest robust signal on S2:

- S2 test-pattern best delta around `-0.0306`.
- S2 chrono best delta around `-0.0301`.
- S2 tail best delta around `-0.0108`.

Q1 has some signal but tail is mixed, so Q1 DL should be tiny/diagnostic only.

## Generated candidates

Script: `scripts/58_make_public_lb_meta_candidates.py`

Anchor and candidates written under `outputs/`; shift reports and notes under `experiments/`.

Recommended order:

1. `outputs/submission_meta_anchor_w02_noq3_prob.csv`
   - `w=0.2` temporal smoothing but Q3 reverted to base.
   - First diagnostic: checks if Q3 smoothing hurt the known `0.6311869686` file.

2. `outputs/submission_meta_anchor_plus_s2dl20_prob.csv`
   - Anchor + small S2 tiny-DL residual.
   - Best “real improvement” candidate if only one extra signal is added.

3. `outputs/submission_meta_anchor_plus_q1s2dl10_prob.csv`
   - Anchor + very small Q1/S2 DL residual.
   - Safer than full Q1/S2 DL blend because Q1 tail was not clean.

4. `outputs/submission_meta_anchor_plus_s2dl20_q1s4calib10_prob.csv`
   - Anchor + S2 DL + tiny Q1/S4 learned-calibrator residual.
   - More ambitious but still avoids Q2 calibrator risk.

5. `outputs/submission_meta_anchor_plus_calib15_q1q2s4_prob.csv`
   - Most aggressive hard-target diagnostic.
   - Includes Q2 calibrator despite tail risk; use only after safer files or if submissions are plentiful.

## Honest expectation

These are still not guaranteed `0.5x` files.  The strongest defensible path is controlled public probing:

- If candidate 1 beats `0.63118`, keep Q3 base permanently.
- If candidate 2 beats candidate 1, S2 DL residual is real and can be increased cautiously.
- If candidate 4 beats candidate 2, learned Q1/S4 state calibration is useful.
- If candidate 5 fails, especially vs candidate 4, Q2 learned calibration is likely harmful on public/private distribution.
