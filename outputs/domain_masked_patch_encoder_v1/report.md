# Domain Masked Patch Encoder v1

## Purpose

Train repeatable label-free masked patch encoders on the domain idea token views. This is an encoder experiment only; it does not train a label decoder.

## Config

- Device: `mps`
- Views: `only_event, only_cross_modal, only_missingness, event_cross_missing, event_cross_phone_missing, no_body, full`
- Seeds: `2026, 2027`
- Patch length: `4` 30-minute tokens = `120` minutes
- d_model: `24`
- Epochs: `8`

## Summary

| view | seed | channels_selected | best_val_loss | final_val_loss | subject_centroid_leakage | train_sample_mean_l2 | temporal_locality_gap | embedding_effective_rank | embedding_axis_std_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_missingness | 2026 | 21 | 0.685039 | 0.776165 | 0.261429 | 0.093213 | 0.009517 | 1.947405 | 0.133550 |
| only_event | 2026 | 11 | 0.711309 | 0.720739 | 0.195714 | 0.019296 | 0.001742 | 3.242006 | 0.073812 |
| event_cross_missing | 2026 | 34 | 0.733806 | 0.737286 | 0.267143 | 0.027370 | 0.002963 | 3.008471 | 0.074732 |
| only_event | 2027 | 11 | 0.735255 | 0.755684 | 0.221429 | 0.032798 | 0.002973 | 3.970053 | 0.114002 |
| only_missingness | 2027 | 21 | 0.761911 | 0.940137 | 0.268571 | 0.061807 | 0.009789 | 2.452990 | 0.120049 |
| no_body | 2026 | 79 | 0.766989 | 0.786607 | 0.362857 | 0.038707 | 0.004136 | 1.541697 | 0.073169 |
| event_cross_missing | 2027 | 34 | 0.776879 | 0.827523 | 0.237143 | 0.022880 | 0.001145 | 3.239276 | 0.052248 |
| no_body | 2027 | 79 | 0.822688 | 0.834846 | 0.370000 | 0.014610 | 0.000780 | 3.712136 | 0.038618 |
| event_cross_phone_missing | 2026 | 47 | 0.832225 | 0.832225 | 0.297143 | 0.040921 | 0.005040 | 1.598886 | 0.089395 |
| full | 2026 | 110 | 0.843762 | 0.849734 | 0.327143 | 0.051527 | 0.002447 | 3.144162 | 0.064479 |
| full | 2027 | 110 | 0.851600 | 0.896844 | 0.328571 | 0.040843 | 0.002103 | 2.318825 | 0.051508 |
| event_cross_phone_missing | 2027 | 47 | 0.858178 | 0.881702 | 0.288571 | 0.026294 | 0.001448 | 2.085002 | 0.051410 |
| only_cross_modal | 2027 | 2 | 0.976176 | 0.976176 | 0.211429 | 0.039403 | 0.004930 | 2.244171 | 0.097840 |
| only_cross_modal | 2026 | 2 | 0.992916 | 0.992916 | 0.204286 | 0.053737 | 0.029981 | 2.010811 | 0.256797 |

## Selection Rule

Carry forward views that combine low validation reconstruction loss with low train/sample shift and low subject-centroid leakage. Do not promote a view just because it reconstructs well if it mostly identifies the subject.