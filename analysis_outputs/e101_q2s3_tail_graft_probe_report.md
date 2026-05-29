# E101 Q2/S3 Tail Graft Probe

## Question

E100 says E89 is only live when the public hard-label tail is Q2/S3-diffuse.
This probe tests whether that pocket can be separated from full E89 by grafting
selected Q2/S3 cells from E89/E85/mixmin onto E95.

## Result

- total rows: `618`
- graft rows: `612`
- strict-like graft rows: `581`
- E101 pass rows: `54`
- materialized submission: `submission_e101_q2s3tail_177569bc.csv`

## Controls

| source | all_delta_vs_mixmin | e72_adverse_positive_exposure_all | hidden_q2s3_mean_minus_base | world_support_minus_base | block_q2s3_beats_base_rate | mean_vs_e95_broad_plausible | beat_e95_rate_broad_plausible | mean_vs_e95_broad_q2s3 | beat_e95_rate_broad_q2s3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e86 | -0.000027706 | 0.001010242 | -0.000377585 | -0.000307439 | 0.750000000 | 0.000020345 | 0.000289687 | 0.000040186 | 0.000000000 |
| noq2 | -0.000026946 | 0.000906798 | -0.000254206 | -0.000171638 | 0.611111111 | 0.000015290 | 0.023174971 | 0.000013780 | 0.073369565 |
| e90 | -0.000026932 | 0.000934031 | -0.000299838 | -0.000250999 | 0.750000000 | 0.000013372 | 0.002607184 | 0.000021154 | 0.002717391 |
| e95 | -0.000026207 | 0.000788914 | -0.000251140 | -0.000132931 | 0.722222222 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e89 | -0.000025896 | 0.000799109 | -0.000216060 | -0.000140452 | 0.611111111 | 0.000003833 | 0.195828505 | -0.000005030 | 0.779891304 |
| e85 | -0.000023876 | 0.000739201 | -0.000216060 | -0.000130361 | 0.583333333 | 0.000009659 | 0.031865585 | 0.000006460 | 0.163043478 |

## Best Local Grafts

| tag | fallback | selector | graft_alpha | selected_cells | strict_gate | e101_pass | all_delta_vs_mixmin | e72_adverse_positive_exposure_all | hidden_q2s3_mean_minus_base | world_support_minus_base | block_q2s3_beats_base_rate | mean_vs_e95_broad_plausible | beat_e95_rate_broad_plausible |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e101_e95_q2s3_tail_graft_28f34e5c | e89 | q2_e72_pos_q0.25 | 0.750000000 | 30.000000000 | True | True | -0.000026223 | 0.000786761 | -0.000247657 | -0.000133730 | 0.750000000 | -0.000000259 | 1.000000000 |
| e101_e95_q2s3_tail_graft_28f34e5c | e85 | q2_e72_pos_q0.25 | 0.750000000 | 30.000000000 | True | True | -0.000026223 | 0.000786761 | -0.000247657 | -0.000133730 | 0.750000000 | -0.000000259 | 1.000000000 |
| e101_e95_q2s3_tail_graft_28f34e5c | mixmin | q2_e72_pos_q0.25 | 0.750000000 | 30.000000000 | True | True | -0.000026223 | 0.000786761 | -0.000247657 | -0.000133730 | 0.750000000 | -0.000000259 | 1.000000000 |
| e101_e95_q2s3_tail_graft_2afc359a | e89 | q2_e72_pos_q0.25 | 1.000000000 | 30.000000000 | True | True | -0.000026222 | 0.000786046 | -0.000246485 | -0.000133992 | 0.750000000 | -0.000000324 | 1.000000000 |
| e101_e95_q2s3_tail_graft_2afc359a | e85 | q2_e72_pos_q0.25 | 1.000000000 | 30.000000000 | True | True | -0.000026222 | 0.000786046 | -0.000246485 | -0.000133992 | 0.750000000 | -0.000000324 | 1.000000000 |
| e101_e95_q2s3_tail_graft_2afc359a | mixmin | q2_e72_pos_q0.25 | 1.000000000 | 30.000000000 | True | True | -0.000026222 | 0.000786046 | -0.000246485 | -0.000133992 | 0.750000000 | -0.000000324 | 1.000000000 |
| e101_e95_q2s3_tail_graft_0fb124d5 | e85 | q2_e72_pos_q0.25 | 0.500000000 | 30.000000000 | True | True | -0.000026221 | 0.000787477 | -0.000248824 | -0.000133466 | 0.750000000 | -0.000000184 | 1.000000000 |
| e101_e95_q2s3_tail_graft_0fb124d5 | mixmin | q2_e72_pos_q0.25 | 0.500000000 | 30.000000000 | True | True | -0.000026221 | 0.000787477 | -0.000248824 | -0.000133466 | 0.750000000 | -0.000000184 | 1.000000000 |
| e101_e95_q2s3_tail_graft_0fb124d5 | e89 | q2_e72_pos_q0.25 | 0.500000000 | 30.000000000 | True | True | -0.000026221 | 0.000787477 | -0.000248824 | -0.000133466 | 0.750000000 | -0.000000184 | 1.000000000 |
| e101_e95_q2s3_tail_graft_79e0f957 | e89 | q2_e72_pos_q0.25 | 0.250000000 | 30.000000000 | True | True | -0.000026216 | 0.000788195 | -0.000249984 | -0.000133200 | 0.750000000 | -0.000000098 | 1.000000000 |

## Best Broad Transfer Grafts

| tag | fallback | selector | graft_alpha | selected_cells | strict_gate | e101_pass | all_delta_vs_mixmin | mean_vs_e95_broad_plausible | beat_e95_rate_broad_plausible | p95_vs_e95_broad_plausible | mean_vs_e95_broad_q2s3 | beat_e95_rate_broad_q2s3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e101_e95_q2s3_tail_graft_e3b30077 | mixmin | q2s3_e72_pos_q0.25 | 1.000000000 | 59.000000000 | False | False | -0.000022038 | -0.000056711 | 0.952780997 | -0.000000600 | -0.000098413 | 1.000000000 |
| e101_e95_q2s3_tail_graft_6553e642 | mixmin | s3_e72_pos_q0.50 | 1.000000000 | 20.000000000 | False | False | -0.000022543 | -0.000055293 | 0.935399768 | 0.000001700 | -0.000093299 | 1.000000000 |
| e101_e95_q2s3_tail_graft_65058cb8 | mixmin | s3_e72_pos_q0.25 | 1.000000000 | 29.000000000 | False | False | -0.000020937 | -0.000053955 | 0.953070684 | -0.000000737 | -0.000093576 | 1.000000000 |
| e101_e95_q2s3_tail_graft_875a1c84 | mixmin | q2s3_e72_pos_q0.50 | 1.000000000 | 40.000000000 | False | False | -0.000022920 | -0.000053849 | 0.913383546 | 0.000002707 | -0.000089907 | 0.997282609 |
| e101_e95_q2s3_tail_graft_76faaf92 | mixmin | q2s3_e95_fallback | 1.000000000 | 60.000000000 | False | False | -0.000020720 | -0.000053631 | 0.956836616 | -0.000000959 | -0.000093377 | 1.000000000 |
| e101_e95_q2s3_tail_graft_76faaf92 | mixmin | s3_e95_fallback | 1.000000000 | 31.000000000 | False | False | -0.000020720 | -0.000053631 | 0.956836616 | -0.000000959 | -0.000093377 | 1.000000000 |
| e101_e95_q2s3_tail_graft_8f6c15c6 | mixmin | q2s3_all | 1.000000000 | 500.000000000 | False | False | -0.000019111 | -0.000050801 | 0.962630359 | -0.000002021 | -0.000093399 | 1.000000000 |
| e101_e95_q2s3_tail_graft_8f6c15c6 | mixmin | q2s3_e72_pos_q0.00 | 1.000000000 | 79.000000000 | False | False | -0.000019111 | -0.000050801 | 0.962630359 | -0.000002021 | -0.000093399 | 1.000000000 |
| e101_e95_q2s3_tail_graft_48283e7f | mixmin | q2s3_e72_pos_q0.75 | 1.000000000 | 20.000000000 | False | False | -0.000023196 | -0.000049999 | 0.876593279 | 0.000003556 | -0.000081930 | 0.991847826 |
| e101_e95_q2s3_tail_graft_5314bcc4 | mixmin | s3_all | 1.000000000 | 250.000000000 | False | False | -0.000019314 | -0.000049423 | 0.951042874 | -0.000000142 | -0.000087947 | 1.000000000 |

## Best Q2/S3-Slice Transfer Grafts

| tag | fallback | selector | graft_alpha | selected_cells | strict_gate | e101_pass | all_delta_vs_mixmin | mean_vs_e95_broad_q2s3 | beat_e95_rate_broad_q2s3 | mean_vs_e95_broad_plausible | beat_e95_rate_broad_plausible |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e101_e95_q2s3_tail_graft_e3b30077 | mixmin | q2s3_e72_pos_q0.25 | 1.000000000 | 59.000000000 | False | False | -0.000022038 | -0.000098413 | 1.000000000 | -0.000056711 | 0.952780997 |
| e101_e95_q2s3_tail_graft_65058cb8 | mixmin | s3_e72_pos_q0.25 | 1.000000000 | 29.000000000 | False | False | -0.000020937 | -0.000093576 | 1.000000000 | -0.000053955 | 0.953070684 |
| e101_e95_q2s3_tail_graft_8f6c15c6 | mixmin | q2s3_all | 1.000000000 | 500.000000000 | False | False | -0.000019111 | -0.000093399 | 1.000000000 | -0.000050801 | 0.962630359 |
| e101_e95_q2s3_tail_graft_8f6c15c6 | mixmin | q2s3_e72_pos_q0.00 | 1.000000000 | 79.000000000 | False | False | -0.000019111 | -0.000093399 | 1.000000000 | -0.000050801 | 0.962630359 |
| e101_e95_q2s3_tail_graft_76faaf92 | mixmin | q2s3_e95_fallback | 1.000000000 | 60.000000000 | False | False | -0.000020720 | -0.000093377 | 1.000000000 | -0.000053631 | 0.956836616 |
| e101_e95_q2s3_tail_graft_76faaf92 | mixmin | s3_e95_fallback | 1.000000000 | 31.000000000 | False | False | -0.000020720 | -0.000093377 | 1.000000000 | -0.000053631 | 0.956836616 |
| e101_e95_q2s3_tail_graft_6553e642 | mixmin | s3_e72_pos_q0.50 | 1.000000000 | 20.000000000 | False | False | -0.000022543 | -0.000093299 | 1.000000000 | -0.000055293 | 0.935399768 |
| e101_e95_q2s3_tail_graft_875a1c84 | mixmin | q2s3_e72_pos_q0.50 | 1.000000000 | 40.000000000 | False | False | -0.000022920 | -0.000089907 | 0.997282609 | -0.000053849 | 0.913383546 |
| e101_e95_q2s3_tail_graft_5314bcc4 | mixmin | s3_all | 1.000000000 | 250.000000000 | False | False | -0.000019314 | -0.000087947 | 1.000000000 | -0.000049423 | 0.951042874 |
| e101_e95_q2s3_tail_graft_5314bcc4 | mixmin | s3_e72_pos_q0.00 | 1.000000000 | 39.000000000 | False | False | -0.000019314 | -0.000087947 | 1.000000000 | -0.000049423 | 0.951042874 |

## Transfer Detail Sample

| filter | tag | fallback | selector | graft_alpha | n_scenarios | local_delta | mean_vs_e95 | beat_e95_rate | p95_vs_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| broad_plausible | e101_e95_q2s3_tail_graft_e3b30077 | mixmin | q2s3_e72_pos_q0.25 | 1.000000000 | 3452 | -0.000022038 | -0.000056711 | 0.952780997 | -0.000000600 |
| broad_plausible | e101_e95_q2s3_tail_graft_6553e642 | mixmin | s3_e72_pos_q0.50 | 1.000000000 | 3452 | -0.000022543 | -0.000055293 | 0.935399768 | 0.000001700 |
| broad_plausible | e101_e95_q2s3_tail_graft_65058cb8 | mixmin | s3_e72_pos_q0.25 | 1.000000000 | 3452 | -0.000020937 | -0.000053955 | 0.953070684 | -0.000000737 |
| broad_plausible | e101_e95_q2s3_tail_graft_875a1c84 | mixmin | q2s3_e72_pos_q0.50 | 1.000000000 | 3452 | -0.000022920 | -0.000053849 | 0.913383546 | 0.000002707 |
| broad_plausible | e101_e95_q2s3_tail_graft_76faaf92 | mixmin | q2s3_e95_fallback | 1.000000000 | 3452 | -0.000020720 | -0.000053631 | 0.956836616 | -0.000000959 |
| broad_plausible | e101_e95_q2s3_tail_graft_8f6c15c6 | mixmin | q2s3_all | 1.000000000 | 3452 | -0.000019111 | -0.000050801 | 0.962630359 | -0.000002021 |
| broad_plausible | e101_e95_q2s3_tail_graft_48283e7f | mixmin | q2s3_e72_pos_q0.75 | 1.000000000 | 3452 | -0.000023196 | -0.000049999 | 0.876593279 | 0.000003556 |
| broad_plausible | e101_e95_q2s3_tail_graft_5314bcc4 | mixmin | s3_all | 1.000000000 | 3452 | -0.000019314 | -0.000049423 | 0.951042874 | -0.000000142 |
| broad_plausible | e101_e95_q2s3_tail_graft_32c5cb5b | mixmin | s3_e72_pos_q0.75 | 1.000000000 | 3452 | -0.000023649 | -0.000045439 | 0.828505214 | 0.000004256 |
| broad_plausible | e101_e95_q2s3_tail_graft_c6e4a22e | mixmin | q2s3_e72_pos_q0.25 | 0.750000000 | 3452 | -0.000023648 | -0.000044687 | 0.956257242 | -0.000001043 |
| broad_plausible | e101_e95_q2s3_tail_graft_b3662458 | mixmin | s3_e72_pos_q0.50 | 0.750000000 | 3452 | -0.000023980 | -0.000043450 | 0.937137891 | 0.000001015 |
| broad_plausible | e101_e95_q2s3_tail_graft_6df38924 | mixmin | s3_e72_pos_q0.25 | 0.750000000 | 3452 | -0.000022918 | -0.000042974 | 0.957995365 | -0.000001278 |
| broad_plausible | e101_e95_q2s3_tail_graft_2a79025a | mixmin | q2s3_e95_fallback | 0.750000000 | 3452 | -0.000022778 | -0.000042819 | 0.962340672 | -0.000001631 |
| broad_plausible | e101_e95_q2s3_tail_graft_e6d0e247 | mixmin | q2s3_e72_pos_q0.50 | 0.750000000 | 3452 | -0.000024236 | -0.000042269 | 0.914542294 | 0.000001573 |
| broad_plausible | e101_e95_q2s3_tail_graft_77ef8de2 | mixmin | q2s3_all | 0.750000000 | 3452 | -0.000021764 | -0.000041388 | 0.972479722 | -0.000002723 |
| broad_plausible | e101_e95_q2s3_tail_graft_067a054a | mixmin | s3_all | 0.750000000 | 3452 | -0.000021894 | -0.000040277 | 0.962920046 | -0.000001414 |
| broad_plausible | e101_e95_q2s3_tail_graft_1349fb8f | mixmin | q2s3_e72_pos_q0.75 | 0.750000000 | 3452 | -0.000024418 | -0.000039286 | 0.876882966 | 0.000002113 |
| broad_plausible | e101_e95_q2s3_tail_graft_5a3a6086 | mixmin | q2s3_e72_pos_q0.90 | 1.000000000 | 3452 | -0.000024143 | -0.000038819 | 0.749420626 | 0.000005100 |
| broad_plausible | e101_e95_q2s3_tail_graft_8ab84439 | mixmin | s3_e72_pos_q0.75 | 0.750000000 | 3452 | -0.000024636 | -0.000035414 | 0.828794902 | 0.000002614 |
| broad_plausible | e101_e95_q2s3_tail_graft_482378f4 | mixmin | q2s3_e72_pos_q0.25 | 0.500000000 | 3452 | -0.000024913 | -0.000031350 | 0.961181924 | -0.000001147 |

## Interpretation

If E101 pass is empty, the E89 Q2/S3 pocket is not locally separable as a
cleaner E95 graft under the current local+tail abstraction. In that case the
full E89 file remains a public sensor for diffuse Q2/S3 tail allocation, but it
should not be converted into a new claimed-improvement candidate.

If E101 pass is non-empty, submit the materialized file before full E89 because
it would test the same hidden-world hypothesis with less non-Q2/S3 movement.
