# Domain Temporal Contrastive Encoder

## Purpose

Train target-free contrastive encoders that force day latents to represent behavioral state relations rather than only reconstruct observed token values.

## Config

- Device: `mps`
- Views: `event_cross_missing, only_event`
- Normalizations: `global, subject_channel_token`
- Positive modes: `same_day, adjacent_day`
- Subject-centered projection loss: `True`
- Seeds: `2026, 2027`
- Patch length: `4` 30-minute tokens = `120` minutes
- d_model: `24`
- Epochs: `8`

## Summary

| positive_mode | normalization | view | seed | channels_selected | best_val_loss | final_val_loss | subject_centroid_leakage | train_sample_mean_l2 | temporal_locality_gap | embedding_effective_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| same_day | subject_channel_token | only_event | 2027 | 11 | 1.312677 | 1.312677 | 0.184286 | 0.201156 | 0.088634 | 5.392921 |
| same_day | subject_channel_token | only_event | 2026 | 11 | 1.488287 | 1.528489 | 0.188571 | 0.146535 | 0.060120 | 4.361850 |
| same_day | global | only_event | 2027 | 11 | 1.533297 | 2.100916 | 0.178571 | 0.069023 | 0.013539 | 2.964929 |
| same_day | global | only_event | 2026 | 11 | 1.663221 | 2.019481 | 0.192857 | 0.107517 | 0.027970 | 2.407314 |
| same_day | global | event_cross_missing | 2027 | 34 | 1.701425 | 2.156844 | 0.264286 | 0.065680 | 0.010790 | 2.151392 |
| same_day | subject_channel_token | event_cross_missing | 2027 | 34 | 1.785918 | 2.420122 | 0.212857 | 0.566072 | 0.121074 | 3.258528 |
| same_day | global | event_cross_missing | 2026 | 34 | 2.147742 | 2.952192 | 0.240000 | 0.247160 | 0.138414 | 1.465207 |
| same_day | subject_channel_token | event_cross_missing | 2026 | 34 | 2.151309 | 2.798125 | 0.172857 | 0.473545 | 0.122843 | 2.278896 |
| adjacent_day | subject_channel_token | only_event | 2026 | 11 | 8.610536 | 8.926455 | 0.212857 | 0.065601 | 0.022548 | 3.649711 |
| adjacent_day | subject_channel_token | only_event | 2027 | 11 | 8.993405 | 8.993405 | 0.242857 | 0.044279 | 0.008277 | 5.124864 |
| adjacent_day | global | only_event | 2026 | 11 | 9.082972 | 9.199846 | 0.201429 | 0.021880 | 0.000963 | 3.357422 |
| adjacent_day | subject_channel_token | event_cross_missing | 2026 | 34 | 9.107542 | 9.114258 | 0.188571 | 0.041888 | 0.009285 | 2.455218 |
| adjacent_day | global | only_event | 2027 | 11 | 9.797018 | 9.797018 | 0.220000 | 0.017772 | 0.000667 | 4.517974 |
| adjacent_day | global | event_cross_missing | 2026 | 34 | 9.896505 | 9.935759 | 0.251429 | 0.061952 | 0.004296 | 1.755568 |
| adjacent_day | global | event_cross_missing | 2027 | 34 | 9.901540 | 9.901540 | 0.247143 | 0.027071 | 0.001060 | 2.619382 |
| adjacent_day | subject_channel_token | event_cross_missing | 2027 | 34 | 10.082499 | 10.135557 | 0.191429 | 0.107773 | 0.006086 | 2.637775 |

## Selection Rule

Promote a contrastive latent only if its frozen label probe beats the reconstruction-SSL probe, not merely because the contrastive validation loss is low.