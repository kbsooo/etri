# E305 Block-Prior S4 Materializer

Public LB는 사용하지 않았다. E304가 복원한 hidden S4 block prior를 S4-only probability edit으로 바꾸고 matched-null governor로 검증했다.

## Summary

| generated_candidates | old_strict | null_evaluated | ready_32rep | best_null_strict_rate | best_mean_dominance | best_actual_p90 |
| --- | --- | --- | --- | --- | --- | --- |
| 111 | 14 | 14 | 0 | 0.648437500 | 0.562500000 | -0.000127522 |

## Best Prefilter Rows

| basename | family | nonzero_rows | active_minus_inactive_pred_S4 | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | strict_promote_gate | pred_beats_current_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e305_blockprior_s4_top16_up_amp0_0520_a7a03c0f.csv | top_up | 65 | 0.512522603 | -0.000510247 | -0.000127522 | True | 0.941176471 |
| submission_e305_blockprior_s4_top12_up_amp0_0520_ae631e32.csv | top_up | 44 | 0.565519937 | -0.000340371 | -0.000088710 | True | 0.941176471 |
| submission_e305_blockprior_s4_top16_up_amp0_0388_ec40f7c0.csv | top_up | 65 | 0.512522603 | -0.000388718 | -0.000085069 | True | 0.941176471 |
| submission_e305_blockprior_s4_top10_up_amp0_0520_78b29ed2.csv | top_up | 41 | 0.576238828 | -0.000320615 | -0.000083733 | True | 0.941176471 |
| submission_e305_blockprior_s4_redistribute_toprows_n47_m1_16_8af21c01.csv | redistribute_toprows | 47 | 0.555216359 | -0.000304475 | -0.000074434 | True | 0.941176471 |
| submission_e305_blockprior_s4_redistribute_toprows_n50_m1_16_9cb367c8.csv | redistribute_toprows | 50 | 0.546498914 | -0.000308531 | -0.000074261 | True | 0.941176471 |
| submission_e305_blockprior_s4_redistribute_toprows_n38_m1_16_0bf83c6f.csv | redistribute_toprows | 38 | 0.586616688 | -0.000253640 | -0.000064463 | True | 0.941176471 |
| submission_e305_blockprior_s4_redistribute_toprows_n47_m1_00_289dc52f.csv | redistribute_toprows | 47 | 0.555216359 | -0.000266060 | -0.000059546 | True | 0.941176471 |
| submission_e305_blockprior_s4_redistribute_toprows_n50_m1_00_58e33742.csv | redistribute_toprows | 50 | 0.546498914 | -0.000269557 | -0.000059398 | True | 0.941176471 |
| submission_e305_blockprior_s4_top12_up_amp0_0388_5d8d6b37.csv | top_up | 44 | 0.565519937 | -0.000260704 | -0.000058917 | True | 0.941176471 |
| submission_e305_blockprior_s4_top8_up_amp0_0520_dedf6c7a.csv | top_up | 29 | 0.627610280 | -0.000194583 | -0.000056231 | True | 0.941176471 |
| submission_e305_blockprior_s4_top10_up_amp0_0388_76edc62b.csv | top_up | 41 | 0.576238828 | -0.000245806 | -0.000055405 | True | 0.941176471 |
| submission_e305_blockprior_s4_redistribute_toprows_n32_m1_16_b40540cd.csv | redistribute_toprows | 32 | 0.611821376 | -0.000197155 | -0.000053815 | True | 0.941176471 |
| submission_e305_blockprior_s4_redistribute_toprows_n38_m1_00_4701c2f9.csv | redistribute_toprows | 38 | 0.586616688 | -0.000221588 | -0.000051807 | True | 0.941176471 |
| submission_e305_blockprior_s4_top16_up_amp0_0250_f62150dd.csv | top_up | 65 | 0.512522603 | -0.000256629 | -0.000046968 | False | 0.941176471 |
| submission_e305_blockprior_s4_redistribute_toprows_n32_m1_00_b7199766.csv | redistribute_toprows | 32 | 0.611821376 | -0.000172386 | -0.000045180 | False | 0.941176471 |
| submission_e305_blockprior_s4_top6_up_amp0_0520_50b0cdf6.csv | top_up | 21 | 0.670557572 | -0.000132232 | -0.000039892 | False | 0.911764706 |
| submission_e305_blockprior_s4_top8_up_amp0_0388_41a5219b.csv | top_up | 29 | 0.627610280 | -0.000149791 | -0.000039678 | False | 0.941176471 |
| submission_e305_blockprior_s4_redistribute_toprows_n47_m0_75_9353d0b9.csv | redistribute_toprows | 47 | 0.555216359 | -0.000204012 | -0.000038880 | False | 0.941176471 |
| submission_e305_blockprior_s4_redistribute_toprows_n50_m0_75_e6fd9595.csv | redistribute_toprows | 50 | 0.546498914 | -0.000206636 | -0.000038769 | False | 0.941176471 |
| submission_e305_blockprior_s4_redistribute_toprows_n24_m1_16_8852d43d.csv | redistribute_toprows | 24 | 0.651168217 | -0.000137910 | -0.000037221 | False | 0.941176471 |
| submission_e305_blockprior_s4_redistribute_toprows_n38_m0_75_a0f514ac.csv | redistribute_toprows | 38 | 0.586616688 | -0.000169648 | -0.000034416 | False | 0.941176471 |
| submission_e305_blockprior_s4_redistribute_toprows_n32_m0_75_2a13ff1c.csv | redistribute_toprows | 32 | 0.611821376 | -0.000131819 | -0.000031594 | False | 0.941176471 |
| submission_e305_blockprior_s4_top12_up_amp0_0250_4d4cc030.csv | top_up | 44 | 0.565519937 | -0.000173163 | -0.000031272 | False | 0.941176471 |
| submission_e305_blockprior_s4_redistribute_toprows_n24_m1_00_ebf51b37.csv | redistribute_toprows | 24 | 0.651168217 | -0.000121298 | -0.000030772 | False | 0.941176471 |

## Governor Rows

| basename | family | nonzero_rows | actual_mean | actual_p90 | null_strict_rate | p90_dominance | mean_dominance | worst_mode_p90_dominance | worst_mode_mean_dominance | public_free_ready | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e305_blockprior_s4_redistribute_toprows_n38_m1_00_4701c2f9.csv | redistribute_toprows | 38 | -0.000221588 | -0.000051807 | 0.648437500 | 0.421875000 | 0.539062500 | 0.093750000 | 0.093750000 | False | do_not_submit |
| submission_e305_blockprior_s4_top8_up_amp0_0520_dedf6c7a.csv | top_up | 29 | -0.000194583 | -0.000056231 | 0.679687500 | 0.445312500 | 0.281250000 | 0.000000000 | 0.000000000 | False | do_not_submit |
| submission_e305_blockprior_s4_redistribute_toprows_n32_m1_16_b40540cd.csv | redistribute_toprows | 32 | -0.000197155 | -0.000053815 | 0.703125000 | 0.515625000 | 0.351562500 | 0.093750000 | 0.000000000 | False | do_not_submit |
| submission_e305_blockprior_s4_redistribute_toprows_n47_m1_00_289dc52f.csv | redistribute_toprows | 47 | -0.000266060 | -0.000059546 | 0.718750000 | 0.476562500 | 0.562500000 | 0.000000000 | 0.187500000 | False | do_not_submit |
| submission_e305_blockprior_s4_redistribute_toprows_n50_m1_00_58e33742.csv | redistribute_toprows | 50 | -0.000269557 | -0.000059398 | 0.726562500 | 0.546875000 | 0.523437500 | 0.093750000 | 0.125000000 | False | do_not_submit |
| submission_e305_blockprior_s4_top12_up_amp0_0388_5d8d6b37.csv | top_up | 44 | -0.000260704 | -0.000058917 | 0.726562500 | 0.304687500 | 0.437500000 | 0.000000000 | 0.000000000 | False | do_not_submit |
| submission_e305_blockprior_s4_top10_up_amp0_0388_76edc62b.csv | top_up | 41 | -0.000245806 | -0.000055405 | 0.734375000 | 0.335937500 | 0.421875000 | 0.000000000 | 0.000000000 | False | do_not_submit |
| submission_e305_blockprior_s4_redistribute_toprows_n38_m1_16_0bf83c6f.csv | redistribute_toprows | 38 | -0.000253640 | -0.000064463 | 0.750000000 | 0.437500000 | 0.531250000 | 0.125000000 | 0.156250000 | False | do_not_submit |
| submission_e305_blockprior_s4_redistribute_toprows_n47_m1_16_8af21c01.csv | redistribute_toprows | 47 | -0.000304475 | -0.000074434 | 0.750000000 | 0.539062500 | 0.507812500 | 0.156250000 | 0.093750000 | False | do_not_submit |
| submission_e305_blockprior_s4_top16_up_amp0_0520_a7a03c0f.csv | top_up | 65 | -0.000510247 | -0.000127522 | 0.750000000 | 0.296875000 | 0.500000000 | 0.000000000 | 0.000000000 | False | do_not_submit |
| submission_e305_blockprior_s4_top16_up_amp0_0388_ec40f7c0.csv | top_up | 65 | -0.000388718 | -0.000085069 | 0.750000000 | 0.273437500 | 0.492187500 | 0.000000000 | 0.000000000 | False | do_not_submit |
| submission_e305_blockprior_s4_redistribute_toprows_n50_m1_16_9cb367c8.csv | redistribute_toprows | 50 | -0.000308531 | -0.000074261 | 0.750000000 | 0.570312500 | 0.468750000 | 0.125000000 | 0.062500000 | False | do_not_submit |
| submission_e305_blockprior_s4_top10_up_amp0_0520_78b29ed2.csv | top_up | 41 | -0.000320615 | -0.000083733 | 0.750000000 | 0.382812500 | 0.406250000 | 0.000000000 | 0.000000000 | False | do_not_submit |
| submission_e305_blockprior_s4_top12_up_amp0_0520_ae631e32.csv | top_up | 44 | -0.000340371 | -0.000088710 | 0.750000000 | 0.390625000 | 0.382812500 | 0.000000000 | 0.000000000 | False | do_not_submit |

## Decision

- No E305 candidate survives the local governor.
- E304's block prior is a strong diagnostic, but the simple S4 materializer is not yet a submission path.

## Outputs

- `analysis_outputs/e305_block_prior_s4_candidates.csv`
- `analysis_outputs/e305_block_prior_s4_prefilter.csv`
- `analysis_outputs/e305_block_prior_s4_governor.csv`
- `analysis_outputs/e305_block_prior_s4_summary.csv`
- `analysis_outputs/e305_block_prior_s4_report.md`
