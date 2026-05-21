# Domain Temporal Order Encoder

## Purpose

Train a target-free direction encoder by predicting whether two adjacent same-subject days are in chronological order or reversed.

## Config

- Device: `mps`
- Views: `event+cross_modal, event+missingness`
- Normalizations: `subject_channel_token`
- Seeds: `2026, 2027`
- d_model: `24`
- Epochs: `12`

## Summary

| normalization | view | seed | best_val_loss | best_val_accuracy | final_val_accuracy | subject_centroid_leakage | train_sample_mean_l2 | temporal_locality_gap | embedding_effective_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| subject_channel_token | event+cross_modal | 2027 | 0.693200 | 0.508065 | 0.500000 | 0.240000 | 0.032329 | 0.001888 | 4.729704 |
| subject_channel_token | event+missingness | 2027 | 0.693218 | 0.504032 | 0.495968 | 0.151429 | 0.077050 | 0.008862 | 2.204483 |
| subject_channel_token | event+cross_modal | 2026 | 0.693392 | 0.520161 | 0.491935 | 0.280000 | 0.039117 | 0.004768 | 4.662208 |
| subject_channel_token | event+missingness | 2026 | 0.693969 | 0.500000 | 0.411290 | 0.232857 | 0.117859 | 0.021324 | 1.912612 |

## Selection Rule

Promote this branch only if late-fusing it with the current reconstruction branch beats the contrastive event+cross_modal branch.