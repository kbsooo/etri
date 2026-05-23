# Tiny DL Golf / Latent-MoE experiments

Motivation: after extensive feature engineering and temporal smoothing, test whether very small neural latent heads can exploit engineered feature space better than SelectK + logistic, without jumping to large supervised models.

Script:

- `scripts/55_eval_tiny_dl_golf_latent_moe.py`
- blend candidates: `scripts/56_make_tiny_dl_blends.py`

## Models tested

Fold-local `SelectK + impute + scale` on target-specific feature subsets, then:

- `torch_linear`: one linear head, logistic-equivalent sanity check;
- `bottleneck_z2/z4/z8`: tiny latent bottleneck MLP;
- `micro_moe_z2_e2`, `micro_moe_z4_e2`, `micro_moe_z4_e3`: tiny gated expert heads.

Validation groups:

- existing chronological folds;
- test-pattern masked splits;
- tail split.

## Key results vs same-K logistic

### Q1

- Best chrono: `micro_moe_z4_e2`, delta `-0.0098`.
- Best test-pattern: `micro_moe_z2_e2`, delta `-0.0096`.
- Selected gate chose `bottleneck_z8`: test-pattern `-0.0072`, chrono `-0.0091`, tail `+0.0051`.
- Signal exists but tail is slightly worse and full pure submission shift is too large.

### Q2

- Test-pattern had a small `bottleneck_z2` win `-0.0115`, but chrono and tail are worse.
- Do not use DL for Q2 yet.

### Q3/S1/S3/S4

- Mostly logistic remains better or neural gains are tiny/unstable.
- S4 did not benefit meaningfully from tiny DL despite being sleep-mechanism plausible.

### S2

- Strongest and most robust DL signal.
- `bottleneck_z2`: test-pattern `-0.0282`, chrono `-0.0181`, tail `-0.0108`.
- This is the cleanest DL-golf result.

## Generated candidates

Pure selected neural outputs had too much shift:

- `outputs/submission_tiny_dl_golf_selected_prob.csv`: changes Q1/S2 pure neural; Q1 mean delta `0.074`, S2 mean delta `0.088`.
- `outputs/submission_tiny_dl_golf_hardtargets_prob.csv`: Q1 pure neural only; Q1 mean delta `0.074`.

These are not recommended as first submissions.

Safer blend candidates:

1. `outputs/submission_tiny_dl_golf_s2_blend30_prob.csv`
   - only S2, 30% neural bottleneck + 70% base.
   - S2 mean abs delta `0.0265`, max `0.0552`.
   - Best DL-specific candidate.

2. `outputs/submission_tiny_dl_golf_q1s2_blend20_prob.csv`
   - Q1/S2, 20% neural blend.
   - Q1 mean delta `0.0149`; S2 mean delta `0.0177`.
   - Safer Q1+S2 diagnostic.

3. `outputs/submission_tiny_dl_golf_q1s2_blend30_prob.csv`
   - Q1/S2, 30% neural blend.
   - Q1 mean delta `0.0223`; S2 mean delta `0.0265`.

## Interpretation

The user's intuition is partially supported:

- small latent neural heads can extract extra signal from engineered features;
- the cleanest gain is S2, not Q1/Q2/S4;
- MoE is not obviously better than bottleneck MLP in this tiny setting;
- pure neural heads are too aggressive, so blend with base is necessary.

## Recommended use

Do not replace the smoothing diagnostics with DL yet. If using public submissions for DL diagnostics, order:

1. `submission_tiny_dl_golf_s2_blend30_prob.csv`
2. `submission_tiny_dl_golf_q1s2_blend20_prob.csv`
3. `submission_tiny_dl_golf_q1s2_blend30_prob.csv`

But if the immediate objective is improving the 0.631 smoothing result, still prioritize:

1. `submission_lbdiag_w02_all_except_q3_prob.csv`
2. `submission_lbdiag_w02_q1q2s4_only_prob.csv`
3. `submission_lbdiag_mid_w025_noq3_q2w02_prob.csv`

Tiny DL is a promising side track, mainly for S2/Q1, not yet a 0.5x breakthrough.
