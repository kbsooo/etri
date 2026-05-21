# Domain Joint Reconstruction Contrastive Encoder

## Purpose

Train a target-free multi-objective encoder that keeps reconstruction information while adding adjacent-day behavioral contrast.

## Config

- Device: `mps`
- Views: `event_cross_missing, only_event`
- Normalizations: `subject_channel_token`
- Positive modes: `adjacent_day`
- Subject-centered projection loss: `True`
- Reconstruction weight: `0.2`
- Seeds: `2026, 2027`
- d_model: `24`
- Epochs: `8`

## Summary

| positive_mode | normalization | view | seed | best_val_loss | final_val_contrastive_loss | final_val_reconstruction_loss | subject_centroid_leakage | train_sample_mean_l2 | temporal_locality_gap | embedding_effective_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| adjacent_day | subject_channel_token | event_cross_missing | 2026 | 9.758047 | 8.693340 | 5.323532 | 0.181429 | 0.158897 | 0.021766 | 1.847258 |
| adjacent_day | subject_channel_token | only_event | 2026 | 10.160549 | 9.015247 | 7.478684 | 0.212857 | 0.042155 | 0.014653 | 3.864851 |
| adjacent_day | subject_channel_token | event_cross_missing | 2027 | 10.878060 | 9.816675 | 5.306926 | 0.224286 | 0.116870 | 0.007526 | 2.773781 |
| adjacent_day | subject_channel_token | only_event | 2027 | 10.988378 | 9.422586 | 7.828954 | 0.201429 | 0.035997 | 0.009056 | 4.745333 |

## Selection Rule

Promote this joint latent only if its frozen probe beats the separate reconstruction+contrastive concatenation baseline.