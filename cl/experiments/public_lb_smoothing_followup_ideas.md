# Public LB smoothing follow-up ideas

Observed public LB:

- `submission_temporal_state_smoothing_wcap01_prob.csv`: `0.6394201335`
- `submission_temporal_state_smoothing_wcap02_prob.csv`: `0.6311869686`

## Interpretation

The result is disappointing in absolute score, but informative:

1. `w=0.2` improved public by `0.0082331649` versus `w=0.1`.
2. This means the temporal-state smoothing direction is not obviously wrong; stronger smoothing helped public.
3. The score is still far from 0.5x, so the family alone is not a breakthrough yet.
4. Since both submissions changed many targets at once, the scalar LB cannot identify which target(s) drove the improvement.
5. The monotonic improvement from `w=0.1` to `w=0.2` suggests public test may indeed be closer to interleaved same-subject completion than pure future forecasting.

Linear extrapolation is only a heuristic, not evidence:

- implied `w=0` around `0.64765`
- implied `w=0.3` around `0.62295`
- implied `w=0.4` around `0.61472`

Do not trust this blindly; target interactions and clipping can break monotonicity.

## Created LB diagnostic candidates

These are for controlled diagnostics if more submissions are available, not guaranteed improvement files.

1. `outputs/submission_lbdiag_w02_q1q2s4_only_prob.csv`
   - base except Q1/Q2/S4 from `wcap02`.
   - Purpose: test whether improvement came mostly from the suspected hard targets.

2. `outputs/submission_lbdiag_w02_all_except_q3_prob.csv`
   - `wcap02` but Q3 reverted to base.
   - Purpose: Q3 smoothing has relatively large correlation drop; remove possible harm.

3. `outputs/submission_lbdiag_mid_w025_noq3_q2w02_prob.csv`
   - halfway between `wcap02` and `wcap03` for most targets, Q3 base, Q2 kept at `wcap02`.
   - Purpose: cautiously test whether stronger-than-0.2 smoothing continues helping without Q3 risk.

4. `outputs/submission_lbdiag_w03_noq3_q2w02_prob.csv`
   - stronger smoothing for most targets, Q3 base, Q2 kept at `wcap02`.
   - Purpose: more aggressive monotonicity test.

## Next idea directions

### A. Target isolation before more blind strengthening

Because `wcap02` improved public versus `wcap01`, the next useful information is not just a bigger `w`; it is which target family helped.

Recommended diagnostic order if submissions are available:

1. `submission_lbdiag_w02_all_except_q3_prob.csv`
2. `submission_lbdiag_w02_q1q2s4_only_prob.csv`
3. `submission_lbdiag_mid_w025_noq3_q2w02_prob.csv`

### B. Learn a better smoother than fixed exponential smoothing

The current smoother is very crude: same-subject nearby labels with one `tau/alpha/w`. Improve it by using:

- nearest previous and nearest next known label separately;
- run-length / streak state per target;
- distance to nearest known train date;
- calendar gap and weekday;
- base prediction confidence;
- sensor reliability/missingness.

Then fit a tiny calibration model on test-pattern masked validation:

`final_logit = a*base_logit + b*prev_label + c*next_label + d*local_mean + e*distance + bias`

Constrain coefficients/regularize strongly to avoid another psw-style overfit.

### C. Public-LB-calibrated validation selection

The fact that `w=0.2` public > `w=0.1` public should be injected as a constraint. Validation schemes that rank `w=0.2` above `w=0.1` are more credible; schemes that prefer `w=0` or reject Q2 too strongly are less credible.

### D. Deep learning direction

Supervised DL is still risky with 450 labels. But SSL/latent can be combined with temporal smoothing:

- train SSL daily/cross-night embeddings as before;
- cluster into behavioral states;
- smooth state-conditioned label probabilities, not raw labels only;
- use tiny calibrated head, not big end-to-end classifier.

## Current stance

No candidate yet deserves confident 0.5x. But this LB result is useful: the temporal-state/interleaved-completion hypothesis gained support, and the next work should diagnose target contributions and replace crude smoothing with a small learned state calibrator.
