# Domain Masked Patch Encoder

## Purpose

Train repeatable label-free masked patch encoders on the domain idea token views. This is an encoder experiment only; it does not train a label decoder.

## Config

- Device: `mps`
- Views: `only_event, only_missingness, event_cross_missing`
- Normalizations: `global, subject_channel, subject_channel_token`
- Seeds: `2026, 2027`
- Patch length: `4` 30-minute tokens = `120` minutes
- d_model: `24`
- Epochs: `8`

## Summary

| view | normalization | seed | channels_selected | best_val_loss | best_val_loss_relative | final_val_loss | subject_centroid_leakage | train_sample_mean_l2 | temporal_locality_gap | embedding_effective_rank | embedding_axis_std_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_event | subject_channel | 2026 | 11 | 7.124410 | 0.761032 | 7.124410 | 0.340000 | 0.125154 | 0.038936 | 3.401674 | 0.249514 |
| event_cross_missing | subject_channel | 2026 | 34 | 3.917066 | 0.773376 | 3.917066 | 0.387143 | 0.110357 | 0.039004 | 2.345716 | 0.211085 |
| only_missingness | subject_channel_token | 2026 | 21 | 2.814267 | 0.774321 | 2.814267 | 0.185714 | 0.190157 | 0.027845 | 1.976891 | 0.325312 |
| only_event | subject_channel | 2027 | 11 | 7.514889 | 0.802743 | 7.514889 | 0.302857 | 0.081970 | 0.020715 | 3.552260 | 0.184407 |
| only_missingness | subject_channel | 2026 | 21 | 2.479405 | 0.848121 | 2.540620 | 0.385714 | 0.128347 | 0.055400 | 2.613273 | 0.272383 |
| event_cross_missing | subject_channel | 2027 | 34 | 4.331774 | 0.855255 | 4.331774 | 0.385714 | 0.072852 | 0.017210 | 3.483231 | 0.166017 |
| event_cross_missing | subject_channel_token | 2026 | 34 | 4.632670 | 0.859153 | 4.632670 | 0.187143 | 0.039807 | 0.007999 | 3.694767 | 0.152578 |
| only_missingness | global | 2026 | 21 | 0.685039 | 0.875289 | 0.776165 | 0.261429 | 0.093213 | 0.009517 | 1.947405 | 0.133550 |
| only_event | subject_channel_token | 2026 | 11 | 7.218871 | 0.908845 | 7.218871 | 0.250000 | 0.064422 | 0.012607 | 4.597455 | 0.222668 |
| only_missingness | subject_channel | 2027 | 21 | 2.722510 | 0.931279 | 2.722510 | 0.358571 | 0.104848 | 0.026323 | 3.356508 | 0.197751 |
| event_cross_missing | global | 2026 | 34 | 0.733806 | 0.943142 | 0.737286 | 0.267143 | 0.027370 | 0.002963 | 3.008471 | 0.074732 |
| only_event | subject_channel_token | 2027 | 11 | 7.632809 | 0.960960 | 7.907701 | 0.181429 | 0.077438 | 0.012199 | 3.597076 | 0.247539 |
| event_cross_missing | subject_channel_token | 2027 | 34 | 5.199206 | 0.964220 | 5.244191 | 0.202857 | 0.059875 | 0.012905 | 3.578821 | 0.206367 |
| only_missingness | subject_channel_token | 2027 | 21 | 3.505312 | 0.964456 | 3.586403 | 0.185714 | 0.133608 | 0.023467 | 2.727702 | 0.266847 |
| only_missingness | global | 2027 | 21 | 0.761911 | 0.973510 | 0.940137 | 0.268571 | 0.061807 | 0.009789 | 2.452990 | 0.120049 |
| only_event | global | 2026 | 11 | 0.711309 | 0.978049 | 0.720739 | 0.195714 | 0.019296 | 0.001742 | 3.242006 | 0.073812 |
| event_cross_missing | global | 2027 | 34 | 0.776879 | 0.998504 | 0.827523 | 0.237143 | 0.022880 | 0.001145 | 3.239276 | 0.052248 |
| only_event | global | 2027 | 11 | 0.735255 | 1.010976 | 0.755684 | 0.221429 | 0.032798 | 0.002973 | 3.970053 | 0.114002 |

## Selection Rule

Carry forward views that combine low validation reconstruction loss with low train/sample shift and low subject-centroid leakage. Do not promote a view just because it reconstructs well if it mostly identifies the subject.