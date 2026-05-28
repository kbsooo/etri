# Raw Timeline JEPA Rescue Summary

## Public Feedback Reframe

Observed public LB:

```text
submission_jepa_latent_residual_probe.csv  0.5812273278
submission_jepa_latent_q2_w0p45.csv        0.5798012862
stage2 reference                           0.5779449757
```

This means the previous JEPA latent residual direction is a bad public axis despite strong OOF. I used those two failed submission moves as a `jepa_bad_axis` diagnostic for the next raw-timeline experiments.

## Why Original Raw I-JEPA Failed

Original Raw Timeline I-JEPA learned a same-day patch reconstruction objective:

```text
epoch 1    loss 1.387846
epoch 220  loss 0.380304
```

But its best residual feature did not pass guardrail:

```text
Q1 rawijepa__z21 subject_rank
OOF delta       -0.001094
guardrail mean  +0.000372
win-rate         0.431
```

Interpretation: the model learned raw canvas identity/coverage structure, but not a stable hidden sleep-state latent.

## Rescue Objective

I changed the target semantics from same-day patch prediction to three JEPA-style prediction problems:

1. **Subject-neighbor Day JEPA**: predict current day PCA latent from previous/next days of the same subject; use prediction errors and predicted state as features.
2. **Mobile↔Wearable Bridge JEPA**: predict wearable latent from mobile latent and mobile latent from wearable latent; use cross-modality mismatch as features.
3. **Window Bridge JEPA**: predict night rectangle latent from day/evening/morning summaries; use night residuals as features.

Files:

```text
jepa/raw_timeline_jepa_rescue.py
jepa/raw_timeline_jepa_rescue_train_features.parquet
jepa/raw_timeline_jepa_rescue_submission_features.parquet
jepa/raw_timeline_jepa_rescue_scan.csv
```

## Result

Strict/loose both selected the same 6 operations:

```text
submission_raw_timeline_jepa_rescue_strict.csv
OOF loss             0.564672
delta vs stage2     -0.002859
ops                 6
jepa_bad_axis_ratio  0.002845
jepa_bad_axis_cos    0.004474
```

Selected operations:

```text
Q3  rtday_both_err_13        subject_z      weight 0.45
S2  rtday_both_pred_02       subject_rank   weight 0.45
S4  rtday_next_abserr_10     subject_center weight 0.45
S3  rtmod_w2m_abserr_09      subject_rank   weight 0.45
Q1  rtday_next_pred_09       subject_center weight 0.45
S1  rtday_prev_pred_09       subject_rank   weight 0.45
```

Scaled candidates:

```text
candidate                                                OOF       delta      jepa_bad_ratio
submission_raw_timeline_jepa_rescue_strict_scale0p25.csv 0.566447 -0.001084  0.005133
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv  0.565609 -0.001922  0.007366
submission_raw_timeline_jepa_rescue_strict_scale0p75.csv 0.565017 -0.002514  0.006662
submission_raw_timeline_jepa_rescue_strict_scale1p0.csv  0.564672 -0.002859  0.002845
```

## Submit Recommendation

Given the two fresh public failures, I would not submit the strongest OOF candidate first. Better probe order:

```text
1. jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv
2. jepa/submission_raw_timeline_jepa_rescue_strict_scale1p0.csv
3. jepa/submission_raw_timeline_jepa_rescue_strict_scale0p25.csv
```

Rationale:

- `scale0p5` keeps most OOF gain but halves the logit move.
- `scale1p0` has the best OOF and very low alignment with the new JEPA-bad public axis.
- `scale0p25` is the safest movement probe if public volatility is the priority.

## Next Ideas

1. **Block-Canvas JEPA**: predict a whole submission-like hidden block canvas from surrounding train blocks, then use block-level raw anomaly to gate only S-targets.
2. **Label-Conditioned JEPA Without Direct Labels**: context includes known neighboring label rates, target is raw canvas latent; feature is disagreement between label-implied state and raw-implied state.
3. **JEPA Bad-Axis Orthogonalization**: all future postprocess candidates should report projection against the two failed public JEPA moves, not just ordinal bad axis.
4. **Raw Sensor Token Dropout JEPA**: train with entire sensor-family dropout, not random small rectangles, to force mobile/wearable complementarity.
5. **Subject Episode JEPA**: represent not a day but a train/submission episode; predict episode latent from previous episode, with target = within-episode slope/volatility of raw rhythm.
