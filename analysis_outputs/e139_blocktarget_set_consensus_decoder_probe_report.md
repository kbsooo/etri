# E139 Block-Target Set-Consensus Decoder Probe

## Question

E138 showed state-veto co-location but failed strict all-set/world health. E139 asks whether the missing decoder is just combo-set sign conflict: keep only movements whose combo-set gradients agree before applying the block-target state and veto masks.

## Counts

- candidate rows: `1196`
- set-consensus variants: `1188`
- evaluated variants: `698`
- local strict variants: `0`
- transfer-veto-actionable variants: `190`
- local-strict plus transfer-veto-actionable variants: `0`
- final submit-gate variants: `0`
- transfer rows: `2312`
- materialized submission: `none`

## Decoder Summary

| decoder | source_sets | agreement_cells | agreement_rows | agreement_q2s3_cells | agreement_s_cells | unit_mean_abs | unit_active_mean_abs | unit_max_abs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all3_min | all3 | 592 | 233 | 120 | 411 | 0.000000818 | 0.000002418 | 0.000015911 |
| all3_mean | all3 | 592 | 233 | 120 | 411 | 0.000001873 | 0.000005538 | 0.000081125 |
| pair_inverse_top__raw05_compatible_min | inverse_top,raw05_compatible | 1032 | 249 | 211 | 674 | 0.000002292 | 0.000003887 | 0.000079916 |
| pair_inverse_top__all_sign_min | inverse_top,all_sign | 690 | 234 | 166 | 463 | 0.000000971 | 0.000002462 | 0.000015911 |
| pair_raw05_compatible__all_sign_min | raw05_compatible,all_sign | 1212 | 249 | 363 | 685 | 0.000002065 | 0.000002982 | 0.000015911 |

## Gate Blockers Among Evaluated

- `all_margin_vs_mixmin`: `0/698`
- `all_beats_base`: `0/698`
- `structural_all_sets_beat_base`: `463/698`
- `structural_all_sets_tail_neutral`: `698/698`
- `structural_hidden_core_beats_base`: `207/698`
- `structural_world_nonworse`: `698/698`
- `structural_raw_energy_nonworse`: `698/698`

## Mask Summary

| decoder | mask_name | overlap_kind | state_mask | state_kind | state_scope | state_frac | safety_mask | safety_scope | safety_top_q | selected_cells | selected_rows | selected_q2s3_cells | selected_s_cells | mean_state | mean_weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all3_min | state_top30_all_hard__veto_null_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 471 | 172 | 77 | 186 | 0.794331499 | 1.000000000 |
| all3_min | state_top30_all_hard__veto_null_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 471 | 172 | 77 | 186 | 0.794331499 | 0.794331499 |
| all3_mean | state_top30_all_hard__veto_null_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 471 | 172 | 77 | 186 | 0.794331499 | 1.000000000 |
| all3_mean | state_top30_all_hard__veto_null_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 471 | 172 | 77 | 186 | 0.794331499 | 0.794331499 |
| all3_min | state_top30_all_hard__veto_null_nonactive_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 463 | 172 | 69 | 179 | 0.795301812 | 1.000000000 |
| all3_min | state_top30_all_hard__veto_null_nonactive_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 463 | 172 | 69 | 179 | 0.795301812 | 0.795301812 |
| all3_mean | state_top30_all_hard__veto_null_nonactive_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 463 | 172 | 69 | 179 | 0.795301812 | 1.000000000 |
| all3_mean | state_top30_all_hard__veto_null_nonactive_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 463 | 172 | 69 | 179 | 0.795301812 | 0.795301812 |
| pair_inverse_top__all_sign_min | state_top30_all_hard__veto_null_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 462 | 172 | 76 | 183 | 0.793688169 | 1.000000000 |
| pair_inverse_top__all_sign_min | state_top30_all_hard__veto_null_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 462 | 172 | 76 | 183 | 0.793688169 | 0.793688169 |
| all3_min | state_top30_q1q3_sall_hard__veto_null_top50__hard | hard | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 461 | 172 | 67 | 186 | 0.796831050 | 1.000000000 |
| all3_min | state_top30_q1q3_sall_hard__veto_null_top50__state_soft | state_soft | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 461 | 172 | 67 | 186 | 0.796831050 | 0.796831050 |
| all3_mean | state_top30_q1q3_sall_hard__veto_null_top50__hard | hard | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 461 | 172 | 67 | 186 | 0.796831050 | 1.000000000 |
| all3_mean | state_top30_q1q3_sall_hard__veto_null_top50__state_soft | state_soft | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 461 | 172 | 67 | 186 | 0.796831050 | 0.796831050 |
| pair_inverse_top__all_sign_min | state_top30_all_hard__veto_null_nonactive_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 455 | 172 | 69 | 177 | 0.794454125 | 1.000000000 |
| pair_inverse_top__all_sign_min | state_top30_all_hard__veto_null_nonactive_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 455 | 172 | 69 | 177 | 0.794454125 | 0.794454125 |
| all3_min | state_top30_q1q3_sall_hard__veto_null_nonactive_top50__hard | hard | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 454 | 172 | 60 | 179 | 0.797605329 | 1.000000000 |
| all3_min | state_top30_q1q3_sall_hard__veto_null_nonactive_top50__state_soft | state_soft | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 454 | 172 | 60 | 179 | 0.797605329 | 0.797605329 |
| all3_mean | state_top30_q1q3_sall_hard__veto_null_nonactive_top50__hard | hard | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 454 | 172 | 60 | 179 | 0.797605329 | 1.000000000 |
| all3_mean | state_top30_q1q3_sall_hard__veto_null_nonactive_top50__state_soft | state_soft | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 454 | 172 | 60 | 179 | 0.797605329 | 0.797605329 |
| pair_inverse_top__all_sign_min | state_top30_q1q3_sall_hard__veto_null_top50__hard | hard | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 452 | 172 | 66 | 183 | 0.796223257 | 1.000000000 |
| pair_inverse_top__all_sign_min | state_top30_q1q3_sall_hard__veto_null_top50__state_soft | state_soft | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 452 | 172 | 66 | 183 | 0.796223257 | 0.796223257 |
| pair_inverse_top__all_sign_min | state_top30_q1q3_sall_hard__veto_null_nonactive_top50__hard | hard | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 446 | 172 | 60 | 177 | 0.796781855 | 1.000000000 |
| pair_inverse_top__all_sign_min | state_top30_q1q3_sall_hard__veto_null_nonactive_top50__state_soft | state_soft | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 446 | 172 | 60 | 177 | 0.796781855 | 0.796781855 |
| pair_inverse_top__raw05_compatible_min | state_top30_all_hard__veto_null_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 405 | 163 | 73 | 162 | 0.792908002 | 1.000000000 |
| pair_inverse_top__raw05_compatible_min | state_top30_all_hard__veto_null_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 405 | 163 | 73 | 162 | 0.792908002 | 0.792908002 |
| pair_inverse_top__raw05_compatible_min | state_top30_all_hard__veto_null_nonactive_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 401 | 163 | 69 | 159 | 0.793572029 | 1.000000000 |
| pair_inverse_top__raw05_compatible_min | state_top30_all_hard__veto_null_nonactive_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 401 | 163 | 69 | 159 | 0.793572029 | 0.793572029 |
| pair_inverse_top__raw05_compatible_min | state_top30_q1q3_sall_hard__veto_null_top50__hard | hard | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 395 | 163 | 63 | 162 | 0.795789162 | 1.000000000 |
| pair_inverse_top__raw05_compatible_min | state_top30_q1q3_sall_hard__veto_null_top50__state_soft | state_soft | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 395 | 163 | 63 | 162 | 0.795789162 | 0.795789162 |

## Summary

| decoder | state_scope | safety_scope | overlap_kind | shape | rows | evaluated | strict | veto_actionable | local_and_veto | submit_gate | best_all_minus_e95 | best_sensor_mean_vs_e95 | best_sensor_p95_vs_e95 | best_tail_exposure | best_changed_cells |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pair_inverse_top__raw05_compatible_min | all | veto_null_nonq2s3 | hard | sqrt | 12 | 10 | 0 | 4 | 0 | 0 | -0.000018633 | -0.000035174 | -0.000007428 | 0.000779924 | 108 |
| pair_inverse_top__raw05_compatible_min | all | veto_null_nonq2s3 | state_soft | sqrt | 12 | 10 | 0 | 4 | 0 | 0 | -0.000018447 | -0.000035023 | -0.000007354 | 0.000779924 | 108 |
| pair_inverse_top__raw05_compatible_min | all | veto_null_nonq2s3 | hard | sign | 12 | 6 | 0 | 4 | 0 | 0 | -0.000015227 | -0.000031825 | -0.000006070 | 0.000779924 | 108 |
| pair_inverse_top__raw05_compatible_min | all | veto_null_nonq2s3 | state_soft | sign | 12 | 6 | 0 | 4 | 0 | 0 | -0.000015227 | -0.000031825 | -0.000006070 | 0.000779924 | 108 |
| pair_inverse_top__all_sign_min | all | veto_null | hard | sign | 12 | 10 | 0 | 3 | 0 | 0 | -0.000016350 | -0.000041506 | -0.000005926 | 0.000788842 | 142 |
| pair_inverse_top__all_sign_min | all | veto_null | state_soft | sign | 12 | 10 | 0 | 3 | 0 | 0 | -0.000016350 | -0.000041506 | -0.000005926 | 0.000788842 | 142 |
| pair_raw05_compatible__all_sign_min | all | veto_null | hard | sqrt | 12 | 9 | 0 | 3 | 0 | 0 | -0.000012787 | -0.000036785 | -0.000009561 | 0.000788914 | 127 |
| pair_raw05_compatible__all_sign_min | all | veto_null_nonactive | hard | sqrt | 12 | 9 | 0 | 3 | 0 | 0 | -0.000012771 | -0.000036727 | -0.000009646 | 0.000788914 | 124 |
| pair_raw05_compatible__all_sign_min | all | veto_null | state_soft | sqrt | 12 | 9 | 0 | 3 | 0 | 0 | -0.000012628 | -0.000036271 | -0.000009340 | 0.000788914 | 127 |
| pair_raw05_compatible__all_sign_min | all | veto_null_nonactive | state_soft | sqrt | 12 | 9 | 0 | 3 | 0 | 0 | -0.000012623 | -0.000036211 | -0.000009424 | 0.000788914 | 124 |
| pair_raw05_compatible__all_sign_min | all | veto_null_nonactive | hard | sign | 12 | 6 | 0 | 3 | 0 | 0 | -0.000011217 | -0.000036062 | -0.000010520 | 0.000788914 | 124 |
| pair_raw05_compatible__all_sign_min | all | veto_null_nonactive | state_soft | sign | 12 | 6 | 0 | 3 | 0 | 0 | -0.000011217 | -0.000036062 | -0.000010520 | 0.000788914 | 124 |
| pair_raw05_compatible__all_sign_min | all | veto_null | hard | sign | 12 | 6 | 0 | 3 | 0 | 0 | -0.000011121 | -0.000035861 | -0.000010404 | 0.000788914 | 127 |
| pair_raw05_compatible__all_sign_min | all | veto_null | state_soft | sign | 12 | 6 | 0 | 3 | 0 | 0 | -0.000011121 | -0.000035861 | -0.000010404 | 0.000788914 | 127 |
| pair_inverse_top__all_sign_min | all | veto_null | hard | sqrt | 12 | 10 | 0 | 3 | 0 | 0 | -0.000019014 | -0.000034231 | -0.000005590 | 0.000788842 | 142 |
| pair_inverse_top__all_sign_min | all | veto_null | state_soft | sqrt | 12 | 10 | 0 | 3 | 0 | 0 | -0.000019037 | -0.000033722 | -0.000005583 | 0.000788842 | 142 |
| pair_raw05_compatible__all_sign_min | all | veto_null_nonq2s3 | hard | sqrt | 12 | 8 | 0 | 3 | 0 | 0 | -0.000009713 | -0.000033539 | -0.000008733 | 0.000788914 | 115 |
| pair_raw05_compatible__all_sign_min | all | veto_null_nonactive | hard | raw | 12 | 10 | 0 | 3 | 0 | 0 | -0.000013180 | -0.000032994 | -0.000008139 | 0.000788711 | 195 |
| pair_raw05_compatible__all_sign_min | all | veto_null | hard | raw | 12 | 10 | 0 | 3 | 0 | 0 | -0.000013228 | -0.000032989 | -0.000007950 | 0.000787807 | 198 |
| pair_raw05_compatible__all_sign_min | all | veto_null_nonq2s3 | state_soft | sqrt | 12 | 8 | 0 | 3 | 0 | 0 | -0.000009627 | -0.000032934 | -0.000008319 | 0.000788914 | 115 |
| pair_raw05_compatible__all_sign_min | non_q2s3 | veto_null | hard | sqrt | 12 | 7 | 0 | 3 | 0 | 0 | -0.000009307 | -0.000032465 | -0.000008574 | 0.000788914 | 106 |
| pair_raw05_compatible__all_sign_min | all | veto_null_nonactive | state_soft | raw | 12 | 10 | 0 | 3 | 0 | 0 | -0.000012968 | -0.000032237 | -0.000007967 | 0.000788711 | 195 |
| pair_raw05_compatible__all_sign_min | all | veto_null | state_soft | raw | 12 | 9 | 0 | 3 | 0 | 0 | -0.000013016 | -0.000032209 | -0.000007765 | 0.000787851 | 198 |
| pair_raw05_compatible__all_sign_min | non_q2s3 | veto_null | state_soft | sqrt | 12 | 7 | 0 | 3 | 0 | 0 | -0.000009207 | -0.000031855 | -0.000008166 | 0.000788914 | 106 |
| pair_inverse_top__all_sign_min | non_q2s3 | veto_null | hard | sign | 6 | 6 | 0 | 3 | 0 | 0 | -0.000013129 | -0.000030464 | -0.000005442 | 0.000788842 | 116 |
| pair_inverse_top__all_sign_min | non_q2s3 | veto_null | state_soft | sign | 6 | 6 | 0 | 3 | 0 | 0 | -0.000013129 | -0.000030464 | -0.000005442 | 0.000788842 | 116 |
| pair_inverse_top__raw05_compatible_min | all | veto_null_nonq2s3 | state_soft | raw | 12 | 8 | 0 | 3 | 0 | 0 | -0.000016486 | -0.000028911 | -0.000005928 | 0.000778388 | 162 |
| pair_inverse_top__raw05_compatible_min | all | veto_null_nonq2s3 | hard | raw | 12 | 8 | 0 | 3 | 0 | 0 | -0.000016532 | -0.000028695 | -0.000005982 | 0.000777388 | 162 |
| pair_inverse_top__all_sign_min | non_q2s3 | veto_null | hard | sqrt | 6 | 6 | 0 | 3 | 0 | 0 | -0.000015187 | -0.000028606 | -0.000006296 | 0.000788842 | 116 |
| pair_inverse_top__all_sign_min | non_q2s3 | veto_null | state_soft | sqrt | 6 | 6 | 0 | 3 | 0 | 0 | -0.000015259 | -0.000028319 | -0.000006325 | 0.000788842 | 116 |
| pair_raw05_compatible__all_sign_min | all | veto_null_nonq2s3 | hard | raw | 12 | 8 | 0 | 3 | 0 | 0 | -0.000010247 | -0.000024586 | -0.000005490 | 0.000788711 | 169 |
| pair_inverse_top__all_sign_min | all | veto_null | hard | raw | 12 | 8 | 0 | 3 | 0 | 0 | -0.000016018 | -0.000024520 | -0.000006386 | 0.000788842 | 142 |
| pair_inverse_top__all_sign_min | all | veto_null | state_soft | raw | 12 | 8 | 0 | 3 | 0 | 0 | -0.000015930 | -0.000024080 | -0.000006350 | 0.000788842 | 142 |
| pair_raw05_compatible__all_sign_min | all | veto_null_nonq2s3 | state_soft | raw | 12 | 7 | 0 | 3 | 0 | 0 | -0.000010174 | -0.000023963 | -0.000005452 | 0.000788711 | 169 |
| pair_raw05_compatible__all_sign_min | non_q2s3 | veto_null | hard | raw | 12 | 8 | 0 | 3 | 0 | 0 | -0.000010058 | -0.000023553 | -0.000005027 | 0.000788711 | 165 |
| pair_raw05_compatible__all_sign_min | non_q2s3 | veto_null | state_soft | raw | 12 | 7 | 0 | 3 | 0 | 0 | -0.000009983 | -0.000022968 | -0.000005021 | 0.000788711 | 165 |
| pair_raw05_compatible__all_sign_min | all | veto_null_nonq2s3 | hard | sign | 12 | 5 | 0 | 3 | 0 | 0 | -0.000008505 | -0.000022650 | -0.000004925 | 0.000788914 | 115 |
| pair_raw05_compatible__all_sign_min | all | veto_null_nonq2s3 | state_soft | sign | 12 | 5 | 0 | 3 | 0 | 0 | -0.000008505 | -0.000022650 | -0.000004925 | 0.000788914 | 115 |
| pair_raw05_compatible__all_sign_min | non_q2s3 | veto_null | hard | sign | 12 | 3 | 0 | 3 | 0 | 0 | -0.000008028 | -0.000021401 | -0.000004296 | 0.000788914 | 106 |
| pair_raw05_compatible__all_sign_min | non_q2s3 | veto_null | state_soft | sign | 12 | 3 | 0 | 3 | 0 | 0 | -0.000008028 | -0.000021401 | -0.000004296 | 0.000788914 | 106 |
| pair_inverse_top__all_sign_min | non_q2s3 | veto_null | hard | raw | 6 | 6 | 0 | 3 | 0 | 0 | -0.000011662 | -0.000020472 | -0.000004643 | 0.000788842 | 116 |
| pair_inverse_top__all_sign_min | non_q2s3 | veto_null | state_soft | raw | 6 | 6 | 0 | 3 | 0 | 0 | -0.000011746 | -0.000019942 | -0.000004636 | 0.000788842 | 116 |
| pair_inverse_top__raw05_compatible_min | all | veto_null | hard | sqrt | 12 | 8 | 0 | 2 | 0 | 0 | -0.000022029 | -0.000040610 | -0.000008782 | 0.000775168 | 143 |
| pair_inverse_top__raw05_compatible_min | all | veto_null | state_soft | sqrt | 12 | 7 | 0 | 2 | 0 | 0 | -0.000021824 | -0.000040506 | -0.000008700 | 0.000775168 | 143 |
| pair_inverse_top__raw05_compatible_min | all | veto_null_nonactive | hard | sqrt | 12 | 8 | 0 | 2 | 0 | 0 | -0.000021751 | -0.000040093 | -0.000008671 | 0.000775168 | 139 |
| pair_inverse_top__raw05_compatible_min | all | veto_null_nonactive | state_soft | sqrt | 12 | 7 | 0 | 2 | 0 | 0 | -0.000021515 | -0.000039950 | -0.000008577 | 0.000775168 | 139 |
| pair_inverse_top__raw05_compatible_min | non_q2s3 | veto_null | hard | sqrt | 12 | 8 | 0 | 2 | 0 | 0 | -0.000018949 | -0.000037025 | -0.000007554 | 0.000775168 | 122 |
| pair_inverse_top__raw05_compatible_min | non_q2s3 | veto_null | state_soft | sqrt | 12 | 8 | 0 | 2 | 0 | 0 | -0.000018817 | -0.000036902 | -0.000007501 | 0.000775168 | 122 |
| pair_inverse_top__raw05_compatible_min | non_q2s3 | veto_null_nonactive | hard | sqrt | 6 | 5 | 0 | 2 | 0 | 0 | -0.000018761 | -0.000036635 | -0.000007479 | 0.000775168 | 119 |
| pair_inverse_top__raw05_compatible_min | non_q2s3 | veto_null_nonactive | state_soft | sqrt | 6 | 5 | 0 | 2 | 0 | 0 | -0.000018614 | -0.000036491 | -0.000007420 | 0.000775168 | 119 |
| pair_inverse_top__raw05_compatible_min | all | veto_null | hard | sign | 12 | 7 | 0 | 2 | 0 | 0 | -0.000017758 | -0.000035887 | -0.000007079 | 0.000775168 | 143 |
| pair_inverse_top__raw05_compatible_min | all | veto_null | state_soft | sign | 12 | 7 | 0 | 2 | 0 | 0 | -0.000017758 | -0.000035887 | -0.000007079 | 0.000775168 | 143 |
| pair_inverse_top__raw05_compatible_min | all | veto_null_nonactive | hard | sign | 12 | 7 | 0 | 2 | 0 | 0 | -0.000017680 | -0.000035800 | -0.000007048 | 0.000775168 | 139 |
| pair_inverse_top__raw05_compatible_min | all | veto_null_nonactive | state_soft | sign | 12 | 6 | 0 | 2 | 0 | 0 | -0.000017680 | -0.000035800 | -0.000007048 | 0.000775168 | 139 |
| pair_inverse_top__raw05_compatible_min | non_q2s3 | veto_null_nonactive | hard | sign | 6 | 4 | 0 | 2 | 0 | 0 | -0.000014740 | -0.000032509 | -0.000005876 | 0.000775168 | 119 |
| pair_inverse_top__raw05_compatible_min | non_q2s3 | veto_null_nonactive | state_soft | sign | 6 | 4 | 0 | 2 | 0 | 0 | -0.000014740 | -0.000032509 | -0.000005876 | 0.000775168 | 119 |
| pair_inverse_top__raw05_compatible_min | all | veto_null | hard | raw | 12 | 6 | 0 | 2 | 0 | 0 | -0.000019074 | -0.000032463 | -0.000006844 | 0.000775348 | 198 |
| pair_inverse_top__raw05_compatible_min | all | veto_null_nonactive | hard | raw | 12 | 6 | 0 | 2 | 0 | 0 | -0.000019101 | -0.000032402 | -0.000006843 | 0.000777110 | 197 |
| pair_inverse_top__raw05_compatible_min | all | veto_null | state_soft | raw | 12 | 6 | 0 | 2 | 0 | 0 | -0.000018623 | -0.000032391 | -0.000006675 | 0.000775981 | 198 |
| pair_inverse_top__raw05_compatible_min | all | veto_null_nonactive | state_soft | raw | 12 | 6 | 0 | 2 | 0 | 0 | -0.000018659 | -0.000032335 | -0.000006678 | 0.000777697 | 197 |
| pair_inverse_top__raw05_compatible_min | non_q2s3 | veto_null | state_soft | raw | 12 | 6 | 0 | 2 | 0 | 0 | -0.000016442 | -0.000029116 | -0.000005936 | 0.000778133 | 166 |
| pair_inverse_top__raw05_compatible_min | non_q2s3 | veto_null | hard | raw | 12 | 6 | 0 | 2 | 0 | 0 | -0.000016515 | -0.000028924 | -0.000005999 | 0.000777265 | 166 |
| pair_inverse_top__raw05_compatible_min | non_q2s3 | veto_null_nonactive | state_soft | raw | 6 | 4 | 0 | 2 | 0 | 0 | -0.000015120 | -0.000024692 | -0.000005306 | 0.000780814 | 119 |
| pair_inverse_top__raw05_compatible_min | non_q2s3 | veto_null | hard | sign | 12 | 5 | 0 | 2 | 0 | 0 | -0.000013512 | -0.000024494 | -0.000006143 | 0.000788914 | 93 |
| pair_inverse_top__raw05_compatible_min | non_q2s3 | veto_null | state_soft | sign | 12 | 5 | 0 | 2 | 0 | 0 | -0.000013512 | -0.000024494 | -0.000006143 | 0.000788914 | 93 |
| pair_inverse_top__raw05_compatible_min | non_q2s3 | veto_null_nonactive | hard | raw | 6 | 4 | 0 | 2 | 0 | 0 | -0.000015070 | -0.000024435 | -0.000005321 | 0.000779789 | 119 |
| pair_raw05_compatible__all_sign_min | non_q2s3 | veto_null_nonactive | hard | raw | 6 | 5 | 0 | 2 | 0 | 0 | -0.000009402 | -0.000023335 | -0.000005031 | 0.000788914 | 103 |
| pair_raw05_compatible__all_sign_min | non_q2s3 | veto_null_nonactive | hard | sqrt | 6 | 3 | 0 | 2 | 0 | 0 | -0.000009272 | -0.000022997 | -0.000004961 | 0.000788914 | 103 |
| pair_raw05_compatible__all_sign_min | non_q2s3 | veto_null_nonactive | state_soft | raw | 6 | 5 | 0 | 2 | 0 | 0 | -0.000009388 | -0.000022760 | -0.000005023 | 0.000788914 | 103 |
| pair_raw05_compatible__all_sign_min | non_q2s3 | veto_null_nonactive | state_soft | sqrt | 6 | 3 | 0 | 2 | 0 | 0 | -0.000009234 | -0.000022703 | -0.000004941 | 0.000788914 | 103 |
| pair_raw05_compatible__all_sign_min | non_q2s3 | veto_null_nonactive | hard | sign | 6 | 2 | 0 | 2 | 0 | 0 | -0.000008095 | -0.000021476 | -0.000004331 | 0.000788914 | 103 |
| pair_raw05_compatible__all_sign_min | non_q2s3 | veto_null_nonactive | state_soft | sign | 6 | 2 | 0 | 2 | 0 | 0 | -0.000008095 | -0.000021476 | -0.000004331 | 0.000788914 | 103 |
| pair_inverse_top__all_sign_min | all | veto_null_nonactive | hard | sign | 6 | 4 | 0 | 0 | 0 | 0 | -0.000015111 | -0.000041402 | -0.000006028 | 0.000788842 | 142 |
| pair_inverse_top__all_sign_min | all | veto_null_nonactive | state_soft | sign | 6 | 4 | 0 | 0 | 0 | 0 | -0.000015111 | -0.000041402 | -0.000006028 | 0.000788842 | 142 |
| pair_inverse_top__all_sign_min | q1q3_sall | veto_null | hard | sign | 3 | 2 | 0 | 0 | 0 | 0 | -0.000015063 | -0.000041352 | -0.000006070 | 0.000788842 | 142 |
| pair_inverse_top__all_sign_min | q1q3_sall | veto_null | state_soft | sign | 3 | 2 | 0 | 0 | 0 | 0 | -0.000015063 | -0.000041352 | -0.000006070 | 0.000788842 | 142 |
| pair_inverse_top__all_sign_min | q1q3_sall | veto_null_nonactive | hard | sign | 3 | 2 | 0 | 0 | 0 | 0 | -0.000014966 | -0.000041243 | -0.000006151 | 0.000788842 | 142 |
| pair_inverse_top__all_sign_min | q1q3_sall | veto_null_nonactive | state_soft | sign | 3 | 2 | 0 | 0 | 0 | 0 | -0.000014966 | -0.000041243 | -0.000006151 | 0.000788842 | 142 |
| pair_inverse_top__all_sign_min | all | veto_null_nonq2s3 | hard | sign | 6 | 4 | 0 | 0 | 0 | 0 | -0.000012455 | -0.000037904 | -0.000004380 | 0.000788842 | 116 |
| pair_inverse_top__all_sign_min | all | veto_null_nonq2s3 | state_soft | sign | 6 | 4 | 0 | 0 | 0 | 0 | -0.000012455 | -0.000037904 | -0.000004380 | 0.000788842 | 116 |

## Best Local Evaluated Candidates

| decoder | state_mask | safety_mask | overlap_kind | shape | scale | selected_cells | selected_q2s3_cells | all_minus_base | sets_beating_base | sets_tail_neutral | hidden_q2s3_mean_minus_base | world_support_minus_base | raw_energy_q_p90_minus_base | e72_adverse_positive_exposure_all | tail_equal_law_cosine | tail_equal_law_resid_ratio | gate_strict_actionable | post101_mean_vs_e95_e101_sensor | post101_p95_vs_e95_e101_sensor | post101_beat_e95_rate_e101_sensor | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pair_inverse_top__raw05_compatible_min | state_top30_all_hard | veto_null_top70 | hard | sqrt | 0.040000000 | 143.000000000 | 21.000000000 | -0.000022029 | 2 | 1 | 0.000014935 | 0.000810686 | 0.000614176 | 0.000775168 | 0.793026988 | 0.792166702 | False | -0.000040610 | -0.000008782 | 1.000000000 | e138_blocktarget_set_consensus_decoder_3bc79b8c |
| pair_inverse_top__raw05_compatible_min | state_top30_all_hard | veto_null_top70 | state_soft | sqrt | 0.040000000 | 143.000000000 | 21.000000000 | -0.000021824 | 2 | 1 | 0.000013392 | 0.000810285 | 0.000611242 | 0.000775168 | 0.790823688 | 0.796880321 | False | -0.000040506 | -0.000008700 | 1.000000000 | e138_blocktarget_set_consensus_decoder_06e4cb6e |
| pair_inverse_top__raw05_compatible_min | state_top30_all_hard | veto_null_nonactive_top70 | hard | sqrt | 0.040000000 | 139.000000000 | 20.000000000 | -0.000021751 | 2 | 1 | 0.000016217 | 0.000795424 | 0.000601706 | 0.000775168 | 0.796740714 | 0.781876862 | False | -0.000040093 | -0.000008671 | 1.000000000 | e138_blocktarget_set_consensus_decoder_3c25d4be |
| pair_inverse_top__raw05_compatible_min | state_top30_all_hard | veto_null_nonactive_top70 | state_soft | sqrt | 0.040000000 | 139.000000000 | 20.000000000 | -0.000021515 | 2 | 1 | 0.000014678 | 0.000795776 | 0.000599411 | 0.000775168 | 0.794627003 | 0.786365000 | False | -0.000039950 | -0.000008577 | 1.000000000 | e138_blocktarget_set_consensus_decoder_13629d17 |
| all3_mean | state_top30_all_hard | veto_null_top50 | state_soft | sqrt | 0.010000000 | 471.000000000 | 77.000000000 | -0.000019990 | 3 | 1 | 0.000052139 | 0.000849055 | 0.000642865 | 0.000788842 | 0.839988926 | 0.673345901 | False | -0.000032334 | -0.000007969 | 1.000000000 | e138_blocktarget_set_consensus_decoder_b1db95cd |
| all3_mean | state_top30_all_hard | veto_null_top50 | hard | sqrt | 0.010000000 | 471.000000000 | 77.000000000 | -0.000019934 | 3 | 1 | 0.000054746 | 0.000850862 | 0.000647936 | 0.000788842 | 0.834128033 | 0.690581444 | False | -0.000032576 | -0.000007946 | 1.000000000 | e138_blocktarget_set_consensus_decoder_bc02c721 |
| all3_mean | state_top30_all_hard | veto_null_nonactive_top50 | state_soft | sqrt | 0.010000000 | 463.000000000 | 69.000000000 | -0.000019840 | 3 | 1 | 0.000051163 | 0.000834122 | 0.000631714 | 0.000788842 | 0.844024566 | 0.661909028 | False | -0.000031999 | -0.000007909 | 1.000000000 | e138_blocktarget_set_consensus_decoder_f8461d4e |
| all3_mean | state_top30_all_hard | veto_null_nonactive_top50 | hard | sqrt | 0.010000000 | 463.000000000 | 69.000000000 | -0.000019812 | 3 | 1 | 0.000053718 | 0.000836164 | 0.000636703 | 0.000788842 | 0.838262715 | 0.678851823 | False | -0.000032267 | -0.000007898 | 1.000000000 | e138_blocktarget_set_consensus_decoder_49c5e734 |
| all3_mean | state_top30_q1q3_sall_hard | veto_null_top50 | state_soft | sqrt | 0.010000000 | 461.000000000 | 67.000000000 | -0.000019807 | 3 | 1 | 0.000050919 | 0.000830390 | 0.000628928 | 0.000788842 | 0.845032932 | 0.659049810 | False | -0.000031919 | -0.000007896 | 1.000000000 | e138_blocktarget_set_consensus_decoder_8024ba79 |
| all3_mean | state_top30_q1q3_sall_hard | veto_null_top50 | hard | sqrt | 0.010000000 | 461.000000000 | 67.000000000 | -0.000019781 | 3 | 1 | 0.000053461 | 0.000832490 | 0.000633895 | 0.000788842 | 0.839296181 | 0.675919418 | False | -0.000032188 | -0.000007885 | 1.000000000 | e138_blocktarget_set_consensus_decoder_169e0bff |
| all3_mean | state_top30_q1q3_sall_hard | veto_null_nonactive_top50 | state_soft | sqrt | 0.010000000 | 454.000000000 | 60.000000000 | -0.000019686 | 3 | 1 | 0.000050068 | 0.000817447 | 0.000619179 | 0.000788842 | 0.848559970 | 0.649042546 | False | -0.000031637 | -0.000007848 | 1.000000000 | e138_blocktarget_set_consensus_decoder_dccaf6c0 |
| all3_mean | state_top30_q1q3_sall_hard | veto_null_nonactive_top50 | hard | sqrt | 0.010000000 | 454.000000000 | 60.000000000 | -0.000019680 | 3 | 1 | 0.000052566 | 0.000819640 | 0.000624074 | 0.000788842 | 0.842912122 | 0.665655999 | False | -0.000031925 | -0.000007845 | 1.000000000 | e138_blocktarget_set_consensus_decoder_00282dc0 |
| pair_inverse_top__raw05_compatible_min | state_top30_all_hard | veto_null_top50 | state_soft | sqrt | 0.010000000 | 405.000000000 | 73.000000000 | -0.000019320 | 2 | 1 | 0.000006177 | 0.000558633 | 0.000420786 | 0.000771610 | 0.892792822 | 0.514068147 | False | -0.000032860 | -0.000007393 | 1.000000000 | e138_blocktarget_set_consensus_decoder_77d9de28 |
| pair_inverse_top__raw05_compatible_min | state_top30_all_hard | veto_null_top50 | hard | sqrt | 0.010000000 | 405.000000000 | 73.000000000 | -0.000019314 | 2 | 1 | 0.000006995 | 0.000556870 | 0.000421200 | 0.000771567 | 0.894489900 | 0.509744958 | False | -0.000032768 | -0.000007436 | 1.000000000 | e138_blocktarget_set_consensus_decoder_95ac5203 |
| pair_inverse_top__raw05_compatible_min | state_top30_all_hard | veto_null_nonactive_top50 | state_soft | sqrt | 0.010000000 | 401.000000000 | 69.000000000 | -0.000019231 | 2 | 1 | 0.000007118 | 0.000559035 | 0.000421441 | 0.000775168 | 0.893989970 | 0.510605244 | False | -0.000032685 | -0.000007349 | 1.000000000 | e138_blocktarget_set_consensus_decoder_d6eb5eb2 |
| pair_inverse_top__raw05_compatible_min | state_top30_all_hard | veto_null_nonactive_top50 | hard | sqrt | 0.010000000 | 401.000000000 | 69.000000000 | -0.000019217 | 2 | 1 | 0.000007941 | 0.000557654 | 0.000421911 | 0.000775168 | 0.895663673 | 0.506330472 | False | -0.000032585 | -0.000007391 | 1.000000000 | e138_blocktarget_set_consensus_decoder_5a86943f |
| pair_inverse_top__raw05_compatible_min | state_top30_q1q3_sall_hard | veto_null_nonactive_top50 | hard | raw | 0.010000000 | 392.000000000 | 60.000000000 | -0.000019149 | 2 | 1 | 0.000011698 | 0.000652214 | 0.000504313 | 0.000777173 | 0.882698867 | 0.542830183 | False | -0.000032211 | -0.000006836 | 1.000000000 | e138_blocktarget_set_consensus_decoder_8e6b6523 |
| pair_inverse_top__raw05_compatible_min | state_top30_q1q3_sall_hard | veto_null_top50 | hard | raw | 0.010000000 | 395.000000000 | 63.000000000 | -0.000019141 | 2 | 1 | 0.000011298 | 0.000654344 | 0.000505787 | 0.000775460 | 0.881531052 | 0.546140929 | False | -0.000032266 | -0.000006839 | 1.000000000 | e138_blocktarget_set_consensus_decoder_107ff795 |
| pair_inverse_top__raw05_compatible_min | state_top30_all_hard | veto_null_nonactive_top50 | hard | raw | 0.010000000 | 401.000000000 | 69.000000000 | -0.000019101 | 2 | 1 | 0.000012030 | 0.000667897 | 0.000516252 | 0.000777110 | 0.878292317 | 0.555293121 | False | -0.000032402 | -0.000006843 | 1.000000000 | e138_blocktarget_set_consensus_decoder_f3f54666 |
| pair_inverse_top__raw05_compatible_min | state_top30_all_hard | veto_null_top50 | hard | raw | 0.010000000 | 405.000000000 | 73.000000000 | -0.000019074 | 2 | 1 | 0.000011655 | 0.000671632 | 0.000518995 | 0.000775348 | 0.876632601 | 0.559967282 | False | -0.000032463 | -0.000006844 | 1.000000000 | e138_blocktarget_set_consensus_decoder_f6547fe2 |
| pair_inverse_top__all_sign_min | state_top30_all_hard | veto_null_top70 | state_soft | sqrt | 0.040000000 | 142.000000000 | 26.000000000 | -0.000019037 | 3 | 1 | 0.000062237 | 0.001035375 | 0.000791857 | 0.000788842 | 0.846733406 | 0.675784270 | False | -0.000032835 | -0.000007891 | 1.000000000 | e138_blocktarget_set_consensus_decoder_361230d2 |
| pair_inverse_top__raw05_compatible_min | state_top30_q1q3_sall_hard | veto_null_top50 | state_soft | sqrt | 0.010000000 | 395.000000000 | 63.000000000 | -0.000019024 | 2 | 1 | 0.000005968 | 0.000544320 | 0.000410231 | 0.000771697 | 0.897166643 | 0.501375107 | False | -0.000032252 | -0.000007234 | 1.000000000 | e138_blocktarget_set_consensus_decoder_db6689cd |
| pair_inverse_top__raw05_compatible_min | state_top20_all_hard | veto_null_nonactive_top50 | hard | sqrt | 0.020000000 | 260.000000000 | 23.000000000 | -0.000019017 | 2 | 1 | -0.000010412 | 0.000789474 | 0.000613293 | 0.000788914 | 0.809485805 | 0.742175251 | False | -0.000032888 | -0.000004184 | 1.000000000 | e138_blocktarget_set_consensus_decoder_f69d87df |
| pair_inverse_top__all_sign_min | state_top30_all_hard | veto_null_top70 | hard | sqrt | 0.040000000 | 142.000000000 | 26.000000000 | -0.000019014 | 3 | 1 | 0.000065259 | 0.001036692 | 0.000797854 | 0.000788842 | 0.843291206 | 0.687468671 | False | -0.000033113 | -0.000007882 | 1.000000000 | e138_blocktarget_set_consensus_decoder_e7e7a7a7 |
| pair_inverse_top__raw05_compatible_min | state_top20_all_hard | veto_null_top50 | hard | sqrt | 0.020000000 | 262.000000000 | 25.000000000 | -0.000018995 | 2 | 1 | -0.000012246 | 0.000784376 | 0.000608606 | 0.000782279 | 0.808643388 | 0.744466990 | False | -0.000032898 | -0.000004180 | 1.000000000 | e138_blocktarget_set_consensus_decoder_063864ba |
| pair_inverse_top__raw05_compatible_min | state_top30_q1q3_sall_hard | veto_null_nonactive_top50 | state_soft | sqrt | 0.010000000 | 392.000000000 | 60.000000000 | -0.000018962 | 2 | 1 | 0.000006908 | 0.000546354 | 0.000411833 | 0.000775169 | 0.897930860 | 0.499145276 | False | -0.000032134 | -0.000007205 | 1.000000000 | e138_blocktarget_set_consensus_decoder_d98304ad |
| pair_inverse_top__raw05_compatible_min | state_top30_q1q3_sall_hard | veto_null_top50 | hard | sqrt | 0.010000000 | 395.000000000 | 63.000000000 | -0.000018961 | 2 | 1 | 0.000006761 | 0.000542604 | 0.000410637 | 0.000771656 | 0.898802261 | 0.497158663 | False | -0.000032099 | -0.000007269 | 1.000000000 | e138_blocktarget_set_consensus_decoder_9b12ddf7 |
| pair_inverse_top__raw05_compatible_min | state_top30_non_q2s3_hard | veto_null_top70 | hard | sqrt | 0.040000000 | 122.000000000 | 0.000000000 | -0.000018949 | 2 | 1 | 0.000000000 | 0.000716017 | 0.000542785 | 0.000775168 | 0.795519171 | 0.785259099 | False | -0.000037025 | -0.000007554 | 1.000000000 | e138_blocktarget_set_consensus_decoder_d0935cd1 |
| pair_inverse_top__raw05_compatible_min | state_top30_q1q3_sall_hard | veto_null_nonactive_top50 | hard | sqrt | 0.010000000 | 392.000000000 | 60.000000000 | -0.000018899 | 2 | 1 | 0.000007709 | 0.000544842 | 0.000412296 | 0.000775168 | 0.899549243 | 0.494966447 | False | -0.000031982 | -0.000007240 | 1.000000000 | e138_blocktarget_set_consensus_decoder_4f678789 |
| pair_inverse_top__raw05_compatible_min | state_top30_non_q2s3_hard | veto_null_top70 | state_soft | sqrt | 0.040000000 | 122.000000000 | 0.000000000 | -0.000018817 | 2 | 1 | 0.000000000 | 0.000714567 | 0.000538759 | 0.000775168 | 0.795130080 | 0.784975820 | False | -0.000036902 | -0.000007501 | 1.000000000 | e138_blocktarget_set_consensus_decoder_81e85942 |

## Local Strict Plus Transfer-Veto-Actionable Candidates

None.

## Submit-Gate Candidates

None.

## Decision

No submission. Combo-set consensus did not produce a candidate that passes local strict plus transfer-veto plus post-E101 gates.
