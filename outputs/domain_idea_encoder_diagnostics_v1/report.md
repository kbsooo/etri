# Domain Idea Encoder Diagnostics v1

## Purpose

Run label-free encoder-first diagnostics over the token views implied by the 300+ data-engineering ideas. This is deliberately not a decoder experiment.

## Coverage

- Ideas in manifest: `340`
- Ideas touched by at least one view diagnostic: `340`
- Coverage rate: `1.000`

## View Summary

| view | channels_selected | channel_groups_selected | include_mask | latent_dim | input_dim | pca_reconstruction_mse | pca_explained_variance | subject_leakage_acc | train_sample_mean_l2 | train_sample_std_l2 | adjacent_cosine_mean | random_cosine_mean | temporal_locality_gap | same_subject_nn_rate | mean_neighbor_day_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_event | 11 | ['event'] | True | 24 | 1056 | 0.224814 | 0.381763 | 0.611429 | 0.817682 | 0.712412 | 0.191096 | -0.006687 | 0.197784 | 0.528571 | 33.387143 |
| only_cross_modal | 2 | ['cross_modal'] | True | 24 | 192 | 0.271921 | 0.728079 | 0.537143 | 1.326479 | 6.332947 | 0.251514 | 0.016014 | 0.235500 | 0.470000 | 34.977143 |
| only_phone | 13 | ['phone'] | True | 24 | 1248 | 0.465888 | 0.473344 | 0.818571 | 1.527232 | 2.799868 | 0.383407 | 0.017939 | 0.365468 | 0.744286 | 30.367143 |
| only_gps_radio | 18 | ['gps_radio'] | True | 24 | 1728 | 0.376601 | 0.576324 | 0.922857 | 2.215099 | 1.828513 | 0.540858 | 0.031599 | 0.509258 | 0.898571 | 23.787143 |
| only_missingness | 21 | ['missingness'] | True | 24 | 2016 | 0.115956 | 0.770816 | 0.461429 | 2.991721 | 10.003801 | 0.461706 | 0.241868 | 0.219839 | 0.470000 | 35.681429 |
| no_body | 79 | ['ambience', 'cross_modal', 'event', 'gps_radio', 'light', 'missingness', 'phone'] | True | 24 | 7584 | 0.328274 | 0.520857 | 0.922857 | 5.449757 | 8.219391 | 0.521765 | 0.052434 | 0.469331 | 0.871429 | 27.227143 |
| only_body | 31 | ['body'] | True | 24 | 2976 | 0.335758 | 0.599672 | 0.651429 | 7.459419 | 9.697648 | 0.282047 | 0.021723 | 0.260324 | 0.548571 | 33.160000 |
| no_missingness | 89 | ['ambience', 'body', 'cross_modal', 'event', 'gps_radio', 'light', 'phone'] | True | 24 | 8544 | 0.390079 | 0.500474 | 0.894286 | 8.726875 | 9.213254 | 0.417355 | 0.028324 | 0.389030 | 0.815714 | 28.347143 |
| no_gps_radio | 92 | ['ambience', 'body', 'cross_modal', 'event', 'light', 'missingness', 'phone'] | True | 24 | 8832 | 0.323326 | 0.536124 | 0.781429 | 9.043903 | 13.163691 | 0.342876 | 0.048337 | 0.294539 | 0.701429 | 30.574286 |
| no_phone | 97 | ['ambience', 'body', 'cross_modal', 'event', 'gps_radio', 'light', 'missingness'] | True | 24 | 9312 | 0.323532 | 0.542694 | 0.872857 | 9.079223 | 11.728731 | 0.401219 | 0.040736 | 0.360483 | 0.772857 | 29.397143 |
| no_cross_modal | 108 | ['ambience', 'body', 'event', 'gps_radio', 'light', 'missingness', 'phone'] | True | 24 | 10368 | 0.347740 | 0.519284 | 0.880000 | 9.089667 | 11.039724 | 0.417415 | 0.037749 | 0.379666 | 0.815714 | 29.147143 |
| no_event | 99 | ['ambience', 'body', 'cross_modal', 'gps_radio', 'light', 'missingness', 'phone'] | True | 24 | 9504 | 0.356095 | 0.536901 | 0.894286 | 9.138947 | 11.801581 | 0.421931 | 0.042108 | 0.379823 | 0.807143 | 28.671429 |
| full | 110 | ['ambience', 'body', 'cross_modal', 'event', 'gps_radio', 'light', 'missingness', 'phone'] | True | 24 | 10560 | 0.350665 | 0.518588 | 0.882857 | 9.164953 | 11.726662 | 0.420117 | 0.039929 | 0.380188 | 0.808571 | 28.597143 |

## How To Read

- Lower `pca_reconstruction_mse` means the view has a compact reconstructable structure.
- Lower `train_sample_mean_l2` means less train/sample coordinate drift.
- `subject_leakage_acc` is a warning signal: very high values mean the latent may memorize identity instead of day state.
- `temporal_locality_gap` checks whether adjacent days are closer than random days without using labels.