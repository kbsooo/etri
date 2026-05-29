# E138 Block-Target x Veto-Null Overlap Probe

## Question

E137 showed that block-target state alone cannot make the current E95 gradient safe. E138 asks whether the missing piece is simply co-location with the E132 transfer-safe veto-null / low-adverse masks.

## Counts

- candidate rows: `1322`
- overlap variants: `1314`
- evaluated variants: `698`
- local strict variants: `0`
- transfer-veto-actionable variants: `373`
- local-strict plus transfer-veto-actionable variants: `0`
- final submit-gate variants: `0`
- transfer rows: `2264`
- materialized submission: `none`

## Gradient / Mask Diagnostics

| context | grad_mean_abs | grad_max_abs | safety_masks | overlap_masks | risk_scalar_raw_unit |
| --- | --- | --- | --- | --- | --- |
| all | 0.000003874 | 0.000081125 | 12 | 70 | 0.000001528 |
| raw05_compatible | 0.000004250 | 0.000079916 | 12 | 76 | 0.000001478 |

## Mask Summary

| context | mask_name | overlap_kind | state_mask | state_kind | state_scope | state_frac | safety_mask | safety_scope | safety_top_q | selected_cells | selected_rows | selected_q2s3_cells | selected_s_cells | mean_state | mean_weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | state_top30_all_hard__low_adverse75_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | low_adverse75_top50 | low_adverse75 | 0.500000000 | 233 | 129 | 45 | 103 | 0.792779702 | 1.000000000 |
| all | state_top30_all_hard__low_adverse75_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | low_adverse75_top50 | low_adverse75 | 0.500000000 | 233 | 129 | 45 | 103 | 0.792779702 | 0.792779702 |
| all | state_top30_all_hard__low_adverse75_nonactive_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | low_adverse75_nonactive_top50 | low_adverse75_nonactive | 0.500000000 | 231 | 128 | 44 | 102 | 0.792862195 | 1.000000000 |
| all | state_top30_all_hard__low_adverse75_nonactive_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | low_adverse75_nonactive_top50 | low_adverse75_nonactive | 0.500000000 | 231 | 128 | 44 | 102 | 0.792862195 | 0.792862195 |
| all | state_top30_all_hard__veto_null_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 217 | 125 | 42 | 91 | 0.794935717 | 1.000000000 |
| all | state_top30_all_hard__veto_null_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 217 | 125 | 42 | 91 | 0.794935717 | 0.794935717 |
| all | state_top30_all_hard__veto_null_nonactive_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 216 | 125 | 41 | 90 | 0.795179436 | 1.000000000 |
| all | state_top30_all_hard__veto_null_nonactive_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 216 | 125 | 41 | 90 | 0.795179436 | 0.795179436 |
| raw05_compatible | state_top30_all_hard__low_adverse75_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | low_adverse75_top50 | low_adverse75 | 0.500000000 | 207 | 124 | 33 | 76 | 0.799881556 | 1.000000000 |
| raw05_compatible | state_top30_all_hard__low_adverse75_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | low_adverse75_top50 | low_adverse75 | 0.500000000 | 207 | 124 | 33 | 76 | 0.799881556 | 0.799881556 |
| raw05_compatible | state_top30_q1q3_sall_hard__low_adverse75_top50__hard | hard | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | low_adverse75_top50 | low_adverse75 | 0.500000000 | 206 | 124 | 32 | 76 | 0.800467864 | 1.000000000 |
| raw05_compatible | state_top30_q1q3_sall_hard__low_adverse75_top50__state_soft | state_soft | state_top30_q1q3_sall_hard | hard | q1q3_sall | 0.300000000 | low_adverse75_top50 | low_adverse75 | 0.500000000 | 206 | 124 | 32 | 76 | 0.800467864 | 0.800467864 |
| raw05_compatible | state_top30_all_hard__low_adverse75_nonactive_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | low_adverse75_nonactive_top50 | low_adverse75_nonactive | 0.500000000 | 204 | 123 | 31 | 75 | 0.801073642 | 1.000000000 |
| raw05_compatible | state_top30_all_hard__low_adverse75_nonactive_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | low_adverse75_nonactive_top50 | low_adverse75_nonactive | 0.500000000 | 204 | 123 | 31 | 75 | 0.801073642 | 0.801073642 |
| raw05_compatible | state_top30_all_hard__veto_null_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 198 | 122 | 31 | 73 | 0.799023874 | 1.000000000 |
| raw05_compatible | state_top30_all_hard__veto_null_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | veto_null_top50 | veto_null | 0.500000000 | 198 | 122 | 31 | 73 | 0.799023874 | 0.799023874 |
| raw05_compatible | state_top30_all_hard__veto_null_nonactive_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 197 | 122 | 31 | 73 | 0.798582054 | 1.000000000 |
| raw05_compatible | state_top30_all_hard__veto_null_nonactive_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | veto_null_nonactive_top50 | veto_null_nonactive | 0.500000000 | 197 | 122 | 31 | 73 | 0.798582054 | 0.798582054 |
| all | state_top30_non_q2s3_hard__low_adverse75_top50__hard | hard | state_top30_non_q2s3_hard | hard | non_q2s3 | 0.300000000 | low_adverse75_top50 | low_adverse75 | 0.500000000 | 188 | 125 | 0 | 58 | 0.806731351 | 1.000000000 |
| all | state_top30_non_q2s3_hard__low_adverse75_top50__state_soft | state_soft | state_top30_non_q2s3_hard | hard | non_q2s3 | 0.300000000 | low_adverse75_top50 | low_adverse75 | 0.500000000 | 188 | 125 | 0 | 58 | 0.806731351 | 0.806731351 |
| all | state_top30_non_q2s3_hard__low_adverse75_nonactive_top50__hard | hard | state_top30_non_q2s3_hard | hard | non_q2s3 | 0.300000000 | low_adverse75_nonactive_top50 | low_adverse75_nonactive | 0.500000000 | 187 | 124 | 0 | 58 | 0.806802955 | 1.000000000 |
| all | state_top30_non_q2s3_hard__low_adverse75_nonactive_top50__state_soft | state_soft | state_top30_non_q2s3_hard | hard | non_q2s3 | 0.300000000 | low_adverse75_nonactive_top50 | low_adverse75_nonactive | 0.500000000 | 187 | 124 | 0 | 58 | 0.806802955 | 0.806802955 |
| all | state_top30_all_hard__low_adverse75_nonq2s3_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | low_adverse75_nonq2s3_top50 | low_adverse75_nonq2s3 | 0.500000000 | 175 | 120 | 0 | 49 | 0.809824753 | 1.000000000 |
| all | state_top30_all_hard__low_adverse75_nonq2s3_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | low_adverse75_nonq2s3_top50 | low_adverse75_nonq2s3 | 0.500000000 | 175 | 120 | 0 | 49 | 0.809824753 | 0.809824753 |
| raw05_compatible | state_top30_non_q2s3_hard__low_adverse75_top50__hard | hard | state_top30_non_q2s3_hard | hard | non_q2s3 | 0.300000000 | low_adverse75_top50 | low_adverse75 | 0.500000000 | 174 | 118 | 0 | 44 | 0.812814808 | 1.000000000 |
| raw05_compatible | state_top30_non_q2s3_hard__low_adverse75_top50__state_soft | state_soft | state_top30_non_q2s3_hard | hard | non_q2s3 | 0.300000000 | low_adverse75_top50 | low_adverse75 | 0.500000000 | 174 | 118 | 0 | 44 | 0.812814808 | 0.812814808 |
| raw05_compatible | state_top30_non_q2s3_hard__low_adverse75_nonactive_top50__hard | hard | state_top30_non_q2s3_hard | hard | non_q2s3 | 0.300000000 | low_adverse75_nonactive_top50 | low_adverse75_nonactive | 0.500000000 | 173 | 117 | 0 | 44 | 0.813337703 | 1.000000000 |
| raw05_compatible | state_top30_non_q2s3_hard__low_adverse75_nonactive_top50__state_soft | state_soft | state_top30_non_q2s3_hard | hard | non_q2s3 | 0.300000000 | low_adverse75_nonactive_top50 | low_adverse75_nonactive | 0.500000000 | 173 | 117 | 0 | 44 | 0.813337703 | 0.813337703 |
| raw05_compatible | state_top30_all_hard__low_adverse75_nonq2s3_top50__hard | hard | state_top30_all_hard | hard | all | 0.300000000 | low_adverse75_nonq2s3_top50 | low_adverse75_nonq2s3 | 0.500000000 | 170 | 116 | 0 | 43 | 0.812503873 | 1.000000000 |
| raw05_compatible | state_top30_all_hard__low_adverse75_nonq2s3_top50__state_soft | state_soft | state_top30_all_hard | hard | all | 0.300000000 | low_adverse75_nonq2s3_top50 | low_adverse75_nonq2s3 | 0.500000000 | 170 | 116 | 0 | 43 | 0.812503873 | 0.812503873 |

## Summary

| context | state_scope | safety_scope | overlap_kind | shape | rows | evaluated | strict | veto_actionable | local_and_veto | submit_gate | best_all_minus_e95 | best_sensor_mean_vs_e95 | best_sensor_p95_vs_e95 | best_tail_exposure | best_changed_cells |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | all | veto_null_nonq2s3 | hard | sqrt | 12 | 4 | 0 | 5 | 0 | 0 | -0.000023756 | -0.000043113 | -0.000011516 | 0.000785335 | 154 |
| all | all | veto_null_nonq2s3 | state_soft | sqrt | 12 | 3 | 0 | 5 | 0 | 0 | -0.000020460 | -0.000032615 | -0.000008156 | 0.000788914 | 98 |
| all | all | veto_null_nonq2s3 | hard | raw | 12 | 1 | 0 | 5 | 0 | 0 | -0.000019166 | -0.000029536 | -0.000007539 | 0.000785810 | 154 |
| all | all | veto_null_nonq2s3 | hard | sign | 12 | 1 | 0 | 5 | 0 | 0 | -0.000018004 | -0.000029449 | -0.000007177 | 0.000788914 | 98 |
| all | all | veto_null_nonq2s3 | state_soft | sign | 12 | 1 | 0 | 5 | 0 | 0 | -0.000018004 | -0.000029449 | -0.000007177 | 0.000788914 | 98 |
| all | all | low_adverse75 | hard | sqrt | 12 | 5 | 0 | 4 | 0 | 0 | -0.000030467 | -0.000055772 | -0.000015691 | 0.000772209 | 233 |
| all | all | low_adverse75_nonactive | hard | sqrt | 12 | 5 | 0 | 4 | 0 | 0 | -0.000030423 | -0.000055650 | -0.000015663 | 0.000778937 | 231 |
| all | all | low_adverse75 | state_soft | sqrt | 12 | 5 | 0 | 4 | 0 | 0 | -0.000030154 | -0.000055467 | -0.000015527 | 0.000772305 | 233 |
| all | all | low_adverse75_nonactive | state_soft | sqrt | 12 | 5 | 0 | 4 | 0 | 0 | -0.000030111 | -0.000055345 | -0.000015500 | 0.000778937 | 231 |
| all | all | veto_null | hard | sqrt | 12 | 5 | 0 | 4 | 0 | 0 | -0.000029801 | -0.000054008 | -0.000015337 | 0.000778937 | 217 |
| all | all | veto_null | state_soft | sqrt | 12 | 4 | 0 | 4 | 0 | 0 | -0.000029480 | -0.000053678 | -0.000015168 | 0.000778937 | 217 |
| all | all | low_adverse75 | hard | sign | 12 | 5 | 0 | 4 | 0 | 0 | -0.000025065 | -0.000050224 | -0.000013263 | 0.000767898 | 233 |
| all | all | low_adverse75 | state_soft | sign | 12 | 5 | 0 | 4 | 0 | 0 | -0.000025065 | -0.000050224 | -0.000013263 | 0.000767898 | 233 |
| all | all | low_adverse75_nonactive | hard | sign | 12 | 5 | 0 | 4 | 0 | 0 | -0.000025047 | -0.000050203 | -0.000013260 | 0.000778937 | 231 |
| all | all | low_adverse75_nonactive | state_soft | sign | 12 | 5 | 0 | 4 | 0 | 0 | -0.000025047 | -0.000050203 | -0.000013260 | 0.000778937 | 231 |
| all | all | veto_null | hard | sign | 12 | 5 | 0 | 4 | 0 | 0 | -0.000024517 | -0.000048879 | -0.000013194 | 0.000778937 | 217 |
| all | all | veto_null | state_soft | sign | 12 | 5 | 0 | 4 | 0 | 0 | -0.000024517 | -0.000048879 | -0.000013194 | 0.000778937 | 217 |
| all | non_q2s3 | low_adverse75 | hard | sqrt | 12 | 3 | 0 | 4 | 0 | 0 | -0.000023173 | -0.000039046 | -0.000010367 | 0.000788914 | 127 |
| all | non_q2s3 | low_adverse75 | state_soft | sqrt | 12 | 3 | 0 | 4 | 0 | 0 | -0.000023059 | -0.000038985 | -0.000010271 | 0.000788914 | 127 |
| all | all | low_adverse75 | state_soft | raw | 12 | 3 | 0 | 4 | 0 | 0 | -0.000024883 | -0.000038810 | -0.000010087 | 0.000780691 | 233 |
| all | all | low_adverse75 | hard | raw | 12 | 3 | 0 | 4 | 0 | 0 | -0.000025050 | -0.000038699 | -0.000010139 | 0.000780145 | 233 |
| all | all | low_adverse75_nonactive | state_soft | raw | 12 | 3 | 0 | 4 | 0 | 0 | -0.000024802 | -0.000038656 | -0.000010051 | 0.000782483 | 231 |
| all | all | low_adverse75_nonactive | hard | raw | 12 | 3 | 0 | 4 | 0 | 0 | -0.000024968 | -0.000038546 | -0.000010102 | 0.000781992 | 231 |
| all | non_q2s3 | low_adverse75_nonactive | hard | sqrt | 12 | 3 | 0 | 4 | 0 | 0 | -0.000022829 | -0.000037909 | -0.000008826 | 0.000788914 | 123 |
| all | non_q2s3 | low_adverse75_nonactive | state_soft | sqrt | 12 | 3 | 0 | 4 | 0 | 0 | -0.000022712 | -0.000037879 | -0.000009054 | 0.000788914 | 123 |
| all | all | veto_null | state_soft | raw | 12 | 3 | 0 | 4 | 0 | 0 | -0.000024149 | -0.000037361 | -0.000009378 | 0.000782743 | 217 |
| all | all | veto_null | hard | raw | 12 | 3 | 0 | 4 | 0 | 0 | -0.000024341 | -0.000037301 | -0.000009459 | 0.000782200 | 217 |
| all | non_q2s3 | low_adverse75 | hard | sign | 12 | 1 | 0 | 4 | 0 | 0 | -0.000019990 | -0.000035511 | -0.000009452 | 0.000788914 | 127 |
| all | non_q2s3 | low_adverse75 | state_soft | sign | 12 | 1 | 0 | 4 | 0 | 0 | -0.000019990 | -0.000035511 | -0.000009452 | 0.000788914 | 127 |
| all | all | low_adverse75_nonq2s3 | state_soft | sqrt | 12 | 3 | 0 | 4 | 0 | 0 | -0.000021519 | -0.000035482 | -0.000008578 | 0.000788914 | 111 |
| all | all | low_adverse75_nonq2s3 | hard | sqrt | 12 | 4 | 0 | 4 | 0 | 0 | -0.000021613 | -0.000035472 | -0.000008459 | 0.000788914 | 111 |
| all | non_q2s3 | low_adverse75_nonactive | hard | sign | 12 | 1 | 0 | 4 | 0 | 0 | -0.000019781 | -0.000034378 | -0.000007886 | 0.000788914 | 123 |
| all | non_q2s3 | low_adverse75_nonactive | state_soft | sign | 12 | 1 | 0 | 4 | 0 | 0 | -0.000019781 | -0.000034378 | -0.000007886 | 0.000788914 | 123 |
| all | non_q2s3 | low_adverse75 | hard | raw | 12 | 1 | 0 | 4 | 0 | 0 | -0.000021097 | -0.000033850 | -0.000009005 | 0.000782165 | 188 |
| all | non_q2s3 | low_adverse75 | state_soft | raw | 12 | 1 | 0 | 4 | 0 | 0 | -0.000020950 | -0.000033800 | -0.000008924 | 0.000782804 | 188 |
| all | non_q2s3 | low_adverse75_nonactive | hard | raw | 12 | 1 | 0 | 4 | 0 | 0 | -0.000021032 | -0.000033740 | -0.000008974 | 0.000782189 | 187 |
| all | non_q2s3 | low_adverse75_nonactive | state_soft | raw | 12 | 1 | 0 | 4 | 0 | 0 | -0.000020892 | -0.000033697 | -0.000008895 | 0.000782826 | 187 |
| all | all | low_adverse75_nonq2s3 | hard | raw | 12 | 1 | 0 | 4 | 0 | 0 | -0.000020442 | -0.000032524 | -0.000008060 | 0.000782474 | 175 |
| all | all | low_adverse75_nonq2s3 | state_soft | raw | 12 | 1 | 0 | 4 | 0 | 0 | -0.000020311 | -0.000032478 | -0.000007964 | 0.000783093 | 175 |
| all | all | low_adverse75_nonq2s3 | hard | sign | 12 | 1 | 0 | 4 | 0 | 0 | -0.000018705 | -0.000032164 | -0.000007457 | 0.000788914 | 111 |
| all | all | low_adverse75_nonq2s3 | state_soft | sign | 12 | 1 | 0 | 4 | 0 | 0 | -0.000018705 | -0.000032164 | -0.000007457 | 0.000788914 | 111 |
| all | all | veto_null_nonq2s3 | state_soft | raw | 12 | 1 | 0 | 4 | 0 | 0 | -0.000019107 | -0.000029651 | -0.000006855 | 0.000786109 | 154 |
| all | all | veto_null_nonactive | hard | sqrt | 9 | 4 | 0 | 3 | 0 | 0 | -0.000029693 | -0.000053853 | -0.000015286 | 0.000778937 | 216 |
| all | all | veto_null_nonactive | state_soft | sqrt | 9 | 4 | 0 | 3 | 0 | 0 | -0.000029360 | -0.000053508 | -0.000015112 | 0.000778937 | 216 |
| raw05_compatible | all | low_adverse75 | hard | sqrt | 12 | 11 | 0 | 3 | 0 | 0 | -0.000020194 | -0.000051090 | -0.000015247 | 0.000788914 | 145 |
| raw05_compatible | all | low_adverse75_nonactive | hard | sqrt | 12 | 11 | 0 | 3 | 0 | 0 | -0.000020073 | -0.000050966 | -0.000015227 | 0.000788914 | 143 |
| raw05_compatible | all | low_adverse75 | state_soft | sqrt | 12 | 11 | 0 | 3 | 0 | 0 | -0.000020246 | -0.000050721 | -0.000015464 | 0.000788914 | 145 |
| raw05_compatible | all | low_adverse75_nonactive | state_soft | sqrt | 12 | 11 | 0 | 3 | 0 | 0 | -0.000020135 | -0.000050579 | -0.000015436 | 0.000788914 | 143 |
| raw05_compatible | all | veto_null | hard | sqrt | 12 | 11 | 0 | 3 | 0 | 0 | -0.000019919 | -0.000049646 | -0.000015376 | 0.000782444 | 198 |
| raw05_compatible | all | veto_null_nonactive | hard | sqrt | 12 | 11 | 0 | 3 | 0 | 0 | -0.000019987 | -0.000049512 | -0.000015331 | 0.000788914 | 136 |
| raw05_compatible | all | veto_null | state_soft | sqrt | 12 | 11 | 0 | 3 | 0 | 0 | -0.000019926 | -0.000049261 | -0.000015600 | 0.000788914 | 138 |
| raw05_compatible | all | veto_null_nonactive | state_soft | sqrt | 12 | 11 | 0 | 3 | 0 | 0 | -0.000020000 | -0.000049125 | -0.000015553 | 0.000788914 | 136 |
| all | all | veto_null_nonactive | hard | sign | 9 | 5 | 0 | 3 | 0 | 0 | -0.000024375 | -0.000048720 | -0.000013180 | 0.000778937 | 216 |
| all | all | veto_null_nonactive | state_soft | sign | 9 | 5 | 0 | 3 | 0 | 0 | -0.000024375 | -0.000048720 | -0.000013180 | 0.000778937 | 216 |
| raw05_compatible | non_q2s3 | low_adverse75 | hard | sqrt | 12 | 11 | 0 | 3 | 0 | 0 | -0.000016136 | -0.000046808 | -0.000013565 | 0.000788914 | 120 |
| raw05_compatible | all | low_adverse75_nonactive | hard | sign | 12 | 12 | 0 | 3 | 0 | 0 | -0.000017641 | -0.000046652 | -0.000013351 | 0.000788914 | 143 |
| raw05_compatible | all | low_adverse75_nonactive | state_soft | sign | 12 | 12 | 0 | 3 | 0 | 0 | -0.000017641 | -0.000046652 | -0.000013351 | 0.000788914 | 143 |
| raw05_compatible | all | low_adverse75_nonq2s3 | hard | sqrt | 12 | 11 | 0 | 3 | 0 | 0 | -0.000016014 | -0.000046626 | -0.000013648 | 0.000782444 | 170 |
| raw05_compatible | all | low_adverse75 | hard | sign | 12 | 12 | 0 | 3 | 0 | 0 | -0.000017722 | -0.000046472 | -0.000013302 | 0.000788914 | 145 |
| raw05_compatible | all | low_adverse75 | state_soft | sign | 12 | 12 | 0 | 3 | 0 | 0 | -0.000017722 | -0.000046472 | -0.000013302 | 0.000788914 | 145 |
| raw05_compatible | non_q2s3 | low_adverse75 | state_soft | sqrt | 12 | 10 | 0 | 3 | 0 | 0 | -0.000016236 | -0.000046412 | -0.000013807 | 0.000788914 | 120 |
| raw05_compatible | all | low_adverse75_nonq2s3 | state_soft | sqrt | 12 | 11 | 0 | 3 | 0 | 0 | -0.000015920 | -0.000046189 | -0.000013876 | 0.000782444 | 170 |
| raw05_compatible | non_q2s3 | veto_null_nonactive | hard | sqrt | 12 | 11 | 0 | 3 | 0 | 0 | -0.000015936 | -0.000045019 | -0.000013557 | 0.000782444 | 166 |
| raw05_compatible | all | veto_null | hard | sign | 12 | 12 | 0 | 3 | 0 | 0 | -0.000017689 | -0.000044917 | -0.000013555 | 0.000788914 | 138 |
| raw05_compatible | all | veto_null | state_soft | sign | 12 | 12 | 0 | 3 | 0 | 0 | -0.000017689 | -0.000044917 | -0.000013555 | 0.000788914 | 138 |
| raw05_compatible | all | veto_null_nonactive | hard | sign | 12 | 12 | 0 | 3 | 0 | 0 | -0.000017915 | -0.000044763 | -0.000013513 | 0.000788914 | 136 |
| raw05_compatible | all | veto_null_nonactive | state_soft | sign | 12 | 12 | 0 | 3 | 0 | 0 | -0.000017915 | -0.000044763 | -0.000013513 | 0.000788914 | 136 |
| raw05_compatible | non_q2s3 | veto_null_nonactive | state_soft | sqrt | 12 | 11 | 0 | 3 | 0 | 0 | -0.000015975 | -0.000044716 | -0.000013841 | 0.000788914 | 111 |
| raw05_compatible | all | veto_null_nonq2s3 | hard | sqrt | 12 | 11 | 0 | 3 | 0 | 0 | -0.000015822 | -0.000043627 | -0.000013409 | 0.000782516 | 159 |
| raw05_compatible | all | veto_null_nonq2s3 | state_soft | sqrt | 12 | 11 | 0 | 3 | 0 | 0 | -0.000015851 | -0.000043352 | -0.000013686 | 0.000782516 | 159 |
| raw05_compatible | all | low_adverse75_nonq2s3 | hard | sign | 12 | 12 | 0 | 3 | 0 | 0 | -0.000013543 | -0.000042193 | -0.000012357 | 0.000788914 | 113 |
| raw05_compatible | all | low_adverse75_nonq2s3 | state_soft | sign | 12 | 12 | 0 | 3 | 0 | 0 | -0.000013543 | -0.000042193 | -0.000012357 | 0.000788914 | 113 |
| raw05_compatible | non_q2s3 | low_adverse75 | hard | sign | 12 | 12 | 0 | 3 | 0 | 0 | -0.000013558 | -0.000041960 | -0.000012281 | 0.000788914 | 120 |
| raw05_compatible | non_q2s3 | low_adverse75 | state_soft | sign | 12 | 12 | 0 | 3 | 0 | 0 | -0.000013558 | -0.000041960 | -0.000012281 | 0.000788914 | 120 |
| raw05_compatible | all | veto_null | hard | raw | 12 | 7 | 0 | 3 | 0 | 0 | -0.000018522 | -0.000040951 | -0.000012852 | 0.000788914 | 138 |
| raw05_compatible | all | veto_null_nonactive | hard | raw | 12 | 7 | 0 | 3 | 0 | 0 | -0.000018440 | -0.000040711 | -0.000012780 | 0.000788914 | 136 |
| raw05_compatible | all | veto_null | state_soft | raw | 12 | 7 | 0 | 3 | 0 | 0 | -0.000017919 | -0.000040319 | -0.000013067 | 0.000788914 | 138 |
| raw05_compatible | non_q2s3 | veto_null_nonactive | hard | sign | 12 | 12 | 0 | 3 | 0 | 0 | -0.000013609 | -0.000040097 | -0.000012350 | 0.000788914 | 111 |
| raw05_compatible | non_q2s3 | veto_null_nonactive | state_soft | sign | 12 | 12 | 0 | 3 | 0 | 0 | -0.000013609 | -0.000040097 | -0.000012350 | 0.000788914 | 111 |
| raw05_compatible | all | veto_null_nonactive | state_soft | raw | 12 | 7 | 0 | 3 | 0 | 0 | -0.000017839 | -0.000040079 | -0.000012992 | 0.000788914 | 136 |

## Best Local Evaluated Candidates

| context | state_mask | safety_mask | overlap_kind | shape | scale | selected_cells | selected_q2s3_cells | all_minus_base | sets_beating_base | sets_tail_neutral | hidden_q2s3_mean_minus_base | world_support_minus_base | e72_adverse_positive_exposure_all | mean_abs_logit_move_vs_e95 | tail_equal_law_cosine | tail_equal_law_resid_ratio | gate_strict_actionable | post101_mean_vs_e95_e101_sensor | post101_p95_vs_e95_e101_sensor | post101_beat_e95_rate_e101_sensor | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | state_top30_all_hard | low_adverse75_top50 | hard | sqrt | 0.040000000 | 233.000000000 | 45.000000000 | -0.000030467 | 2 | 1 | 0.000084793 | 0.001092051 | 0.000772209 | 0.005325714 | 0.750413959 | 0.907792661 | False | -0.000055772 | -0.000015691 | 1.000000000 | e138_blocktarget_vetonull_overlap_8eca8d2c |
| all | state_top30_all_hard | low_adverse75_nonactive_top50 | hard | sqrt | 0.040000000 | 231.000000000 | 44.000000000 | -0.000030423 | 2 | 1 | 0.000086294 | 0.001091234 | 0.000778937 | 0.005280000 | 0.751483220 | 0.904744659 | False | -0.000055650 | -0.000015663 | 1.000000000 | e138_blocktarget_vetonull_overlap_9e3a5d8d |
| all | state_top30_all_hard | low_adverse75_top50 | state_soft | sqrt | 0.040000000 | 233.000000000 | 45.000000000 | -0.000030154 | 2 | 1 | 0.000079330 | 0.001099269 | 0.000772305 | 0.005325714 | 0.749734203 | 0.907959971 | False | -0.000055467 | -0.000015527 | 1.000000000 | e138_blocktarget_vetonull_overlap_44d71d03 |
| all | state_top30_all_hard | low_adverse75_nonactive_top50 | state_soft | sqrt | 0.040000000 | 231.000000000 | 44.000000000 | -0.000030111 | 2 | 1 | 0.000080825 | 0.001098951 | 0.000778937 | 0.005280000 | 0.750820388 | 0.904873216 | False | -0.000055345 | -0.000015500 | 1.000000000 | e138_blocktarget_vetonull_overlap_46382460 |
| all | state_top30_all_hard | veto_null_top50 | hard | sqrt | 0.040000000 | 217.000000000 | 42.000000000 | -0.000029801 | 2 | 1 | 0.000081817 | 0.001038754 | 0.000778937 | 0.004960000 | 0.759953917 | 0.878824907 | False | -0.000054008 | -0.000015337 | 1.000000000 | e138_blocktarget_vetonull_overlap_9e3a1791 |
| all | state_top30_all_hard | veto_null_nonactive_top50 | hard | sqrt | 0.040000000 | 216.000000000 | 41.000000000 | -0.000029693 | 2 | 1 | 0.000082786 | 0.001034828 | 0.000778937 | 0.004937143 | 0.760477459 | 0.877353465 | False | -0.000053853 | -0.000015286 | 1.000000000 | e138_blocktarget_vetonull_overlap_19f01659 |
| all | state_top30_all_hard | veto_null_top50 | state_soft | sqrt | 0.040000000 | 217.000000000 | 42.000000000 | -0.000029480 | 2 | 1 | 0.000076494 | 0.001044089 | 0.000778937 | 0.004960000 | 0.759608061 | 0.878205394 | False | -0.000053678 | -0.000015168 | 1.000000000 | e138_blocktarget_vetonull_overlap_a1b50678 |
| all | state_top30_all_hard | veto_null_nonactive_top50 | state_soft | sqrt | 0.040000000 | 216.000000000 | 41.000000000 | -0.000029360 | 2 | 1 | 0.000077427 | 0.001040120 | 0.000778937 | 0.004937143 | 0.760165426 | 0.876643941 | False | -0.000053508 | -0.000015112 | 1.000000000 | e138_blocktarget_vetonull_overlap_1fa9b255 |
| all | state_top30_all_hard | low_adverse75_top70 | hard | sqrt | 0.040000000 | 152.000000000 | 25.000000000 | -0.000027104 | 2 | 1 | 0.000048297 | 0.000726279 | 0.000788914 | 0.003474286 | 0.828122956 | 0.701640700 | False | -0.000043555 | -0.000011433 | 1.000000000 | e138_blocktarget_vetonull_overlap_1009fcae |
| all | state_top30_all_hard | low_adverse75_top70 | state_soft | sqrt | 0.040000000 | 152.000000000 | 25.000000000 | -0.000026852 | 2 | 1 | 0.000044828 | 0.000730166 | 0.000788914 | 0.003474286 | 0.826189105 | 0.705359001 | False | -0.000043447 | -0.000011335 | 1.000000000 | e138_blocktarget_vetonull_overlap_02d30c7d |
| all | state_top30_all_hard | low_adverse75_nonactive_top70 | hard | sqrt | 0.040000000 | 148.000000000 | 25.000000000 | -0.000026662 | 2 | 1 | 0.000047857 | 0.000717688 | 0.000788914 | 0.003382857 | 0.836675786 | 0.678378565 | False | -0.000042325 | -0.000009733 | 1.000000000 | e138_blocktarget_vetonull_overlap_36b09f34 |
| all | state_top30_all_hard | low_adverse75_nonactive_top70 | state_soft | sqrt | 0.040000000 | 148.000000000 | 25.000000000 | -0.000026453 | 2 | 1 | 0.000044379 | 0.000721581 | 0.000788914 | 0.003382857 | 0.834121109 | 0.683814880 | False | -0.000042297 | -0.000009956 | 1.000000000 | e138_blocktarget_vetonull_overlap_4df5582b |
| all | state_top30_all_hard | veto_null_top70 | hard | sqrt | 0.040000000 | 139.000000000 | 24.000000000 | -0.000026061 | 2 | 1 | 0.000046282 | 0.000682553 | 0.000788914 | 0.003177143 | 0.843607463 | 0.647797481 | False | -0.000040839 | -0.000009518 | 1.000000000 | e138_blocktarget_vetonull_overlap_0aee7116 |
| all | state_top30_all_hard | veto_null_nonactive_top70 | hard | sqrt | 0.040000000 | 138.000000000 | 24.000000000 | -0.000025964 | 2 | 1 | 0.000046172 | 0.000668869 | 0.000788914 | 0.003154286 | 0.846272038 | 0.640677372 | False | -0.000040571 | -0.000009485 | 1.000000000 | e138_blocktarget_vetonull_overlap_6327a967 |
| all | state_top30_all_hard | veto_null_top70 | state_soft | sqrt | 0.040000000 | 139.000000000 | 24.000000000 | -0.000025866 | 2 | 1 | 0.000042816 | 0.000684249 | 0.000788914 | 0.003177143 | 0.840837061 | 0.654718605 | False | -0.000040845 | -0.000009746 | 1.000000000 | e138_blocktarget_vetonull_overlap_c04699c9 |
| all | state_top30_all_hard | veto_null_nonactive_top70 | state_soft | sqrt | 0.040000000 | 138.000000000 | 24.000000000 | -0.000025770 | 2 | 1 | 0.000042726 | 0.000671313 | 0.000788914 | 0.003154286 | 0.843618189 | 0.647306810 | False | -0.000040576 | -0.000009719 | 1.000000000 | e138_blocktarget_vetonull_overlap_659fb9e1 |
| all | state_top30_all_hard | low_adverse75_top50 | hard | sign | 0.040000000 | 233.000000000 | 45.000000000 | -0.000025065 | 2 | 1 | 0.000081290 | 0.001001763 | 0.000767898 | 0.005325714 | 0.742005186 | 0.926322972 | False | -0.000050224 | -0.000013263 | 1.000000000 | e138_blocktarget_vetonull_overlap_46305920 |
| all | state_top30_all_hard | low_adverse75_top50 | state_soft | sign | 0.040000000 | 233.000000000 | 45.000000000 | -0.000025065 | 2 | 1 | 0.000081290 | 0.001001763 | 0.000767898 | 0.005325714 | 0.742005186 | 0.926322972 | False | -0.000050224 | -0.000013263 | 1.000000000 | e138_blocktarget_vetonull_overlap_46305920 |
| all | state_top30_all_hard | low_adverse75_top50 | hard | raw | 0.020000000 | 233.000000000 | 45.000000000 | -0.000025050 | 2 | 1 | 0.000039663 | 0.000603455 | 0.000780145 | 0.002662857 | 0.908101902 | 0.469084925 | False | -0.000038699 | -0.000010139 | 1.000000000 | e138_blocktarget_vetonull_overlap_fa60a8ba |
| all | state_top30_all_hard | low_adverse75_nonactive_top50 | hard | sign | 0.040000000 | 231.000000000 | 44.000000000 | -0.000025047 | 2 | 1 | 0.000084155 | 0.001006741 | 0.000778937 | 0.005280000 | 0.742005186 | 0.926322972 | False | -0.000050203 | -0.000013260 | 1.000000000 | e138_blocktarget_vetonull_overlap_4dcaa173 |
| all | state_top30_all_hard | low_adverse75_nonactive_top50 | state_soft | sign | 0.040000000 | 231.000000000 | 44.000000000 | -0.000025047 | 2 | 1 | 0.000084155 | 0.001006741 | 0.000778937 | 0.005280000 | 0.742005186 | 0.926322972 | False | -0.000050203 | -0.000013260 | 1.000000000 | e138_blocktarget_vetonull_overlap_4dcaa173 |
| all | state_top30_all_hard | low_adverse75_nonactive_top50 | hard | raw | 0.020000000 | 231.000000000 | 44.000000000 | -0.000024968 | 2 | 1 | 0.000039939 | 0.000600764 | 0.000781992 | 0.002640000 | 0.909000747 | 0.466389692 | False | -0.000038546 | -0.000010102 | 1.000000000 | e138_blocktarget_vetonull_overlap_c65b97ae |
| all | state_top30_all_hard | low_adverse75_top50 | state_soft | raw | 0.020000000 | 233.000000000 | 45.000000000 | -0.000024883 | 2 | 1 | 0.000034390 | 0.000608091 | 0.000780691 | 0.002662857 | 0.901695814 | 0.486804748 | False | -0.000038810 | -0.000010087 | 1.000000000 | e138_blocktarget_vetonull_overlap_7f70f22f |
| all | state_top30_all_hard | low_adverse75_nonactive_top50 | state_soft | raw | 0.020000000 | 231.000000000 | 44.000000000 | -0.000024802 | 2 | 1 | 0.000034676 | 0.000605366 | 0.000782483 | 0.002640000 | 0.902661895 | 0.483970304 | False | -0.000038656 | -0.000010051 | 1.000000000 | e138_blocktarget_vetonull_overlap_c975a0f9 |
| all | state_top30_all_hard | veto_null_top50 | hard | sign | 0.040000000 | 217.000000000 | 42.000000000 | -0.000024517 | 2 | 1 | 0.000080404 | 0.000965987 | 0.000778937 | 0.004960000 | 0.745362882 | 0.913633643 | False | -0.000048879 | -0.000013194 | 1.000000000 | e138_blocktarget_vetonull_overlap_821a0fbd |
| all | state_top30_all_hard | veto_null_top50 | state_soft | sign | 0.040000000 | 217.000000000 | 42.000000000 | -0.000024517 | 2 | 1 | 0.000080404 | 0.000965987 | 0.000778937 | 0.004960000 | 0.745362882 | 0.913633643 | False | -0.000048879 | -0.000013194 | 1.000000000 | e138_blocktarget_vetonull_overlap_821a0fbd |
| all | state_top30_all_hard | veto_null_nonactive_top50 | hard | sign | 0.040000000 | 216.000000000 | 41.000000000 | -0.000024375 | 2 | 1 | 0.000082116 | 0.000962588 | 0.000778937 | 0.004937143 | 0.745362882 | 0.913633643 | False | -0.000048720 | -0.000013180 | 1.000000000 | e138_blocktarget_vetonull_overlap_b93d213c |
| all | state_top30_all_hard | veto_null_nonactive_top50 | state_soft | sign | 0.040000000 | 216.000000000 | 41.000000000 | -0.000024375 | 2 | 1 | 0.000082116 | 0.000962588 | 0.000778937 | 0.004937143 | 0.745362882 | 0.913633643 | False | -0.000048720 | -0.000013180 | 1.000000000 | e138_blocktarget_vetonull_overlap_b93d213c |
| all | state_top30_all_hard | veto_null_top50 | hard | raw | 0.020000000 | 217.000000000 | 42.000000000 | -0.000024341 | 2 | 1 | 0.000037651 | 0.000568809 | 0.000782200 | 0.002480000 | 0.915272876 | 0.447099361 | False | -0.000037301 | -0.000009459 | 1.000000000 | e138_blocktarget_vetonull_overlap_f1280a6c |
| all | state_top30_all_hard | veto_null_nonactive_top50 | hard | raw | 0.020000000 | 216.000000000 | 41.000000000 | -0.000024292 | 2 | 1 | 0.000037866 | 0.000566458 | 0.000782220 | 0.002468571 | 0.915701422 | 0.445788740 | False | -0.000037216 | -0.000009439 | 1.000000000 | e138_blocktarget_vetonull_overlap_70c5015e |

## Local Strict Plus Transfer-Veto-Actionable Candidates

None.

## Submit-Gate Candidates

None.

## Decision

No submission. Intersecting E136 block-target state with E132 veto-null/low-adverse masks still did not produce a candidate that passes local strict plus transfer-veto plus post-E101 gates.
