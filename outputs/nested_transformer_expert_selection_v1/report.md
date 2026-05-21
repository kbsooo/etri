# Nested Transformer Expert Selection

## Result

- Full-OOF targetwise expert selection: `0.614175`
- Nested targetwise expert selection: `0.617817`
- Estimated selection optimism: `0.003642`
- Full-selection submission drift vs v83: `0.089719`

## Nested Selection Counts

| target | source | count |
| --- | --- | --- |
| Q1 | multires10_transformer_encoder_v1__only_rhythm__targetwise | 5 |
| Q2 | multires30_transformer_encoder_v1__no_sleep__targetwise | 5 |
| Q3 | hourly_transformer_encoder_v1_extra__only_rhythm__targetwise | 4 |
| Q3 | hourly_transformer_encoder_v1_extra__only_rhythm__best_global | 1 |
| S1 | multires30_transformer_encoder_v1__only_cross_modal__best_global | 3 |
| S1 | hourly_transformer_encoder_v1_extra__only_rhythm__targetwise | 1 |
| S1 | multires30_transformer_encoder_v1__only_cross_modal__targetwise | 1 |
| S2 | multires30_transformer_encoder_v1__only_cross_modal__targetwise | 3 |
| S2 | multires30_transformer_encoder_v1__only_cross_modal__best_global | 2 |
| S3 | hourly_transformer_encoder_v1_extra__only_cross_modal__targetwise | 3 |
| S3 | multires30_transformer_encoder_v1__no_sleep__targetwise | 2 |
| S4 | multires30_transformer_encoder_v1__only_cross_modal__targetwise | 4 |
| S4 | multires10_transformer_encoder_v1__only_cross_modal__targetwise | 1 |

## Full-Train Target Selection

| target | source | loss |
| --- | --- | --- |
| Q1 | multires10_transformer_encoder_v1__only_rhythm__targetwise | 0.661873 |
| Q2 | multires30_transformer_encoder_v1__no_sleep__targetwise | 0.662907 |
| Q3 | hourly_transformer_encoder_v1_extra__only_rhythm__targetwise | 0.666235 |
| S1 | multires30_transformer_encoder_v1__only_cross_modal__targetwise | 0.571500 |
| S2 | multires30_transformer_encoder_v1__only_cross_modal__targetwise | 0.571930 |
| S3 | hourly_transformer_encoder_v1_extra__only_cross_modal__targetwise | 0.521082 |
| S4 | multires30_transformer_encoder_v1__only_cross_modal__targetwise | 0.643698 |

## Top Sources

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| multires30_transformer_encoder_v1__no_sleep__targetwise | 0.618590 | 0.669906 | 0.662907 | 0.673823 | 0.575702 | 0.578962 | 0.522255 | 0.646574 |
| hourly_transformer_encoder_v1_extra__only_rhythm__targetwise | 0.619825 | 0.668831 | 0.671803 | 0.666235 | 0.573140 | 0.578532 | 0.533031 | 0.647202 |
| multires30_transformer_encoder_v1__only_cross_modal__targetwise | 0.620658 | 0.670290 | 0.683894 | 0.673823 | 0.571500 | 0.571930 | 0.529470 | 0.643698 |
| hourly_transformer_encoder_v1_extra__only_cross_modal__targetwise | 0.620680 | 0.670683 | 0.678873 | 0.673789 | 0.573474 | 0.579856 | 0.521082 | 0.647001 |
| hourly_transformer_encoder_v1__no_sleep__targetwise | 0.620859 | 0.669511 | 0.669603 | 0.673412 | 0.575158 | 0.579856 | 0.531848 | 0.646622 |
| multires10_transformer_encoder_v1__only_cross_modal__targetwise | 0.621938 | 0.669456 | 0.684676 | 0.673823 | 0.574907 | 0.575695 | 0.530039 | 0.644971 |
| multires10_transformer_encoder_v1__no_sleep__targetwise | 0.622058 | 0.672177 | 0.674271 | 0.673823 | 0.575571 | 0.579552 | 0.531740 | 0.647272 |
| hourly_transformer_encoder_v1__full__targetwise | 0.622449 | 0.668064 | 0.684871 | 0.671984 | 0.572181 | 0.579739 | 0.533031 | 0.647272 |
| hourly_transformer_encoder_v1_extra__no_missingness__targetwise | 0.622597 | 0.671627 | 0.682902 | 0.668653 | 0.575072 | 0.579749 | 0.533031 | 0.647144 |
| multires30_transformer_encoder_v1__only_rhythm__targetwise | 0.622599 | 0.667699 | 0.682704 | 0.673823 | 0.575702 | 0.578677 | 0.532316 | 0.647272 |
| multires10_transformer_encoder_v1__only_rhythm__targetwise | 0.623055 | 0.661873 | 0.693313 | 0.673823 | 0.575547 | 0.576523 | 0.533031 | 0.647272 |
| hourly_transformer_encoder_v1__only_core__targetwise | 0.623360 | 0.671664 | 0.683420 | 0.672697 | 0.575702 | 0.579856 | 0.533031 | 0.647150 |

This diagnostic isolates source-selection optimism. It does not retrain Transformer encoders inside folds; it only asks whether selecting the best expert per target on full OOF labels was overly optimistic.