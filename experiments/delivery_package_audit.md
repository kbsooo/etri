# Delivery Package Audit

Date: 2026-05-21

## Summary

`delivery_package/` implements the same broad direction as the active channel-patch goal:

- value/mask tensors `[B,C,T]`
- channel-independent patch Transformer
- 2-hour patches
- self-supervised masked reconstruction
- subject-relative deviation decoder
- MPS support

The architecture is aligned with our current direction, but the reported `Macro F1 = 0.5734` is not directly comparable to the DACON Public LB scores we have been tracking. Our submissions are judged like a probability/logloss task, while this package tunes hard thresholds and writes binary `0/1` predictions.

## Useful Ideas

1. **2-hour patch prior**
   - Package uses 15-minute bins and `patch_len=8`, which is also a 2-hour patch.
   - Our independent sweep found the same behavioral scale: 30-minute bins and `patch_len=4` was best.

2. **Subject-relative latent**
   - Package computes `z_dev = z - z_subject_baseline`.
   - Our channel-latent fusion experiment supports this: drift dropped from `0.100180` to `0.075584` in relative-only mode and curated fusion reached OOF `0.616980`.

3. **Value/mask paired sequence**
   - Package keeps value and mask tensors separate before patch embedding.
   - This matches the active goal and should remain core to the encoder.

## Main Risks

### 1. Metric mismatch

`train.py` optimizes Macro F1 with validation-threshold search:

```text
for candidate_t in np.linspace(0.1, 0.9, 17):
    pred_binary = (val_preds[:, t_idx] >= candidate_t)
```

`predict.py` then applies averaged thresholds and writes binary labels:

```text
final_binary_preds[:, t_idx] = averaged_probs[:, t_idx] >= mean_thresholds[t_idx]
df_submission[target_cols] = final_binary_preds
```

This is dangerous for logloss-style leaderboard scoring. A binary submission gets very large penalty on confident wrong labels. For our competition pipeline, `predict.py` should save calibrated probabilities, not thresholded classes.

### 2. Validation optimism from threshold selection

The fold score is the best threshold selected on that same fold's validation predictions. This is useful as a classification diagnostic but optimistic as a model-selection metric. It does not prove leaderboard quality.

### 3. Fold leakage / transductive baseline ambiguity

`compute_subject_baselines(model, X, M, subjects_all, device)` averages latent vectors over the full aligned tensor timeline, not only the outer training fold.

That is label-free, so it is not direct target leakage, and it may be acceptable for a transductive test-time setup where all raw test days are available. But it makes OOF validation easier than a fold-local baseline and should be reported separately.

### 4. Baseline/model mismatch

In `train.py`, subject baselines are computed at the start of each epoch, then the model is updated during the epoch, and the checkpoint saves the post-update model with the pre-update baselines. This can make inference baselines slightly stale relative to the stored model weights.

### 5. Feature simplification

The package uses only 10 channels:

```text
heart_rate, steps, screen_use, charging, app_usage,
gps_speed, ble_count, wifi_count, m_light, w_light
```

This is clean, but it drops many event/missingness and engineered state features we found useful in the channel-patch branch.

## Decision

Do not treat `Macro F1 = 0.5734` as a leaderboard breakthrough.

Do adopt the core design confirmation:

```text
2-hour channel patches + value/mask pairs + subject-relative latent decoding
```

The next implementation step should be:

1. Keep our richer 30-minute event-hybrid grid and channel latents.
2. Make subject-relative centering fold-local for honest OOF.
3. Train/evaluate with logloss and probability submissions, not thresholded F1.
4. Optionally add a compact neural head inspired by `delivery_package/src/model.py`, but keep output probabilities calibrated.
