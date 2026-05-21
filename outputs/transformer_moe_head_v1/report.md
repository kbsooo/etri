# Transformer Expert MoE Head v1

## Result

- Best source: `nested_moe_logreg_c0p3`
- OOF avg logloss: `0.611527`
- Drift vs v83 reference: `0.086812`
- Experts: `32`

## MoE Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nested_moe_logreg_c0p3 | 0.611527 | 0.673399 | 0.634506 | 0.665114 | 0.569656 | 0.579358 | 0.521375 | 0.637282 |
| targetwise_best_source | 0.614175 | 0.661873 | 0.662907 | 0.666235 | 0.571500 | 0.571930 | 0.521082 | 0.643698 |
| nested_moe_logreg_c0p1 | 0.614425 | 0.668904 | 0.639470 | 0.663694 | 0.576619 | 0.586072 | 0.524353 | 0.641861 |
| nested_moe_logreg_c0p03 | 0.620126 | 0.669121 | 0.659970 | 0.665738 | 0.582218 | 0.589339 | 0.528373 | 0.646125 |
| nested_moe_logreg_c0p01 | 0.624483 | 0.670619 | 0.681956 | 0.669321 | 0.582499 | 0.587164 | 0.531017 | 0.648806 |

## Full-OOF Targetwise Expert Diagnostic

| target | source | loss |
| --- | --- | --- |
| Q1 | multires10_transformer_encoder_v1__only_rhythm__targetwise | 0.661873 |
| Q2 | multires30_transformer_encoder_v1__no_sleep__targetwise | 0.662907 |
| Q3 | hourly_transformer_encoder_v1_extra__only_rhythm__targetwise | 0.666235 |
| S1 | multires30_transformer_encoder_v1__only_cross_modal__targetwise | 0.571500 |
| S2 | multires30_transformer_encoder_v1__only_cross_modal__targetwise | 0.571930 |
| S3 | hourly_transformer_encoder_v1_extra__only_cross_modal__targetwise | 0.521082 |
| S4 | multires30_transformer_encoder_v1__only_cross_modal__targetwise | 0.643698 |

## Top Expert Sources

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

The nested MoE head is intentionally small: it sees only Transformer expert logits, their dispersion, panel position, and a fold-safe subject prior. If this does not beat source selection, the bottleneck is token representation rather than head capacity.