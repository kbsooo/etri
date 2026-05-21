# Domain Temporal Contrastive Encoder

## Purpose

Train target-free contrastive encoders that force day latents to represent behavioral state relations rather than only reconstruct observed token values.

## Config

- Device: `mps`
- Views: `only_event, event+missingness, event+cross_modal, event_cross_missing, no_missingness, no_phone, no_gps_radio`
- Normalizations: `subject_channel_token`
- Positive modes: `adjacent_day`
- Subject-centered projection loss: `True`
- Seeds: `2026, 2027`
- Patch length: `4` 30-minute tokens = `120` minutes
- d_model: `24`
- Epochs: `6`

## Summary

| positive_mode | normalization | view | seed | channels_selected | best_val_loss | final_val_loss | subject_centroid_leakage | train_sample_mean_l2 | temporal_locality_gap | embedding_effective_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| adjacent_day | subject_channel_token | event+cross_modal | 2026 | 13 | 8.165171 | 8.165171 | 0.258571 | 0.055979 | 0.015363 | 4.864884 |
| adjacent_day | subject_channel_token | only_event | 2026 | 11 | 8.610536 | 8.992828 | 0.207143 | 0.053302 | 0.016194 | 3.730410 |
| adjacent_day | subject_channel_token | no_missingness | 2026 | 89 | 8.762659 | 9.148273 | 0.310000 | 0.084677 | 0.006222 | 3.989593 |
| adjacent_day | subject_channel_token | event+missingness | 2026 | 32 | 8.928014 | 8.938474 | 0.245714 | 0.106235 | 0.024298 | 2.708769 |
| adjacent_day | subject_channel_token | no_gps_radio | 2026 | 92 | 8.935101 | 8.935101 | 0.248571 | 0.133602 | 0.009531 | 4.539477 |
| adjacent_day | subject_channel_token | event+cross_modal | 2027 | 13 | 8.948887 | 9.309874 | 0.232857 | 0.065174 | 0.018870 | 3.045382 |
| adjacent_day | subject_channel_token | no_phone | 2026 | 97 | 8.949938 | 8.949938 | 0.222857 | 0.095907 | 0.014286 | 2.739801 |
| adjacent_day | subject_channel_token | only_event | 2027 | 11 | 9.097092 | 9.101513 | 0.212857 | 0.039674 | 0.007200 | 4.892412 |
| adjacent_day | subject_channel_token | event_cross_missing | 2026 | 34 | 9.107542 | 9.209277 | 0.190000 | 0.045064 | 0.008094 | 2.530005 |
| adjacent_day | subject_channel_token | no_missingness | 2027 | 89 | 9.352222 | 9.390749 | 0.264286 | 0.090235 | 0.011194 | 3.578194 |
| adjacent_day | subject_channel_token | no_gps_radio | 2027 | 92 | 9.388178 | 9.469278 | 0.268571 | 0.049216 | 0.002819 | 3.973447 |
| adjacent_day | subject_channel_token | no_phone | 2027 | 97 | 9.508200 | 9.533869 | 0.208571 | 0.130623 | 0.009451 | 3.130689 |
| adjacent_day | subject_channel_token | event+missingness | 2027 | 32 | 9.721124 | 9.721124 | 0.140000 | 0.124497 | 0.025317 | 2.210676 |
| adjacent_day | subject_channel_token | event_cross_missing | 2027 | 34 | 10.082499 | 10.082499 | 0.194286 | 0.089859 | 0.004920 | 2.810839 |

## Selection Rule

Promote a contrastive latent only if its frozen label probe beats the reconstruction-SSL probe, not merely because the contrastive validation loss is low.