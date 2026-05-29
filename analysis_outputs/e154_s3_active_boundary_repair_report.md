# E154 S3 Active-Boundary Repair Probe

## Question

E153 showed that E152's near misses mostly fail actionability through S3 active-boundary exposure. E154 asks whether S3-only rollback can make those rows pass all-four gates without destroying relaxed/E72/post-E101 health.

## Counts

- source missing-actionable controls: `102`.
- generated S3 repair rows: `7458`.
- all-four repairs: `10`.
- materialized submission rows: `10`.

## Repair Summary

| mask_name | ranker | rows | all_four | e154_submit | actionable | relaxed | budget_ok | post101_ok | best_all_minus_base | best_all_four_all_minus_base | best_post101_p95 | best_e72_gap | min_q2s3_l1 | min_tail_equal_resid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| top_s3_e101_3 | s3_e101 | 408 | 4 | 4 | 183 | 25 | 408 | 108 | -0.000012747 | -0.000012158 | -0.000005645 | -0.000010715 | 0.000975999 | 0.240400587 |
| s3_e101_active | full | 306 | 3 | 3 | 139 | 28 | 306 | 81 | -0.000012745 | -0.000012154 | -0.000005644 | -0.000010715 | 0.000970394 | 0.240400587 |
| top_s3_e101_2 | s3_e101 | 408 | 2 | 2 | 175 | 29 | 408 | 114 | -0.000012753 | -0.000012145 | -0.000005647 | -0.000010715 | 0.000981605 | 0.240400587 |
| top_s3_e101_1 | s3_e101 | 408 | 1 | 1 | 83 | 99 | 408 | 132 | -0.000012775 | -0.000012139 | -0.000005654 | -0.000010715 | 0.001018976 | 0.240400587 |
| top_s3_abs_1 | s3_abs | 408 | 0 | 0 | 104 | 80 | 408 | 80 | -0.000012690 |  | -0.000005627 | -0.000010715 | 0.001009892 | 0.240400587 |
| top_s3_composite_5 | s3_composite | 408 | 0 | 0 | 206 | 28 | 408 | 45 | -0.000012631 |  | -0.000005609 | -0.000010715 | 0.000923939 | 0.240400587 |
| top_s3_abs_2 | s3_abs | 408 | 0 | 0 | 192 | 36 | 408 | 36 | -0.000012583 |  | -0.000005594 | -0.000010715 | 0.000966367 | 0.240400587 |
| top_s3_abs_3 | s3_abs | 408 | 0 | 0 | 206 | 23 | 408 | 23 | -0.000012509 |  | -0.000005571 | -0.000010715 | 0.000924589 | 0.240400587 |
| top_s3_abs_5 | s3_abs | 408 | 0 | 0 | 208 | 11 | 408 | 11 | -0.000012446 |  | -0.000005551 | -0.000010715 | 0.000849847 | 0.240400587 |
| top_s3_composite_8 | s3_composite | 408 | 0 | 0 | 208 | 8 | 408 | 8 | -0.000012409 |  | -0.000005540 | -0.000010715 | 0.000801265 | 0.240400587 |
| top_s3_abs_8 | s3_abs | 408 | 0 | 0 | 208 | 7 | 408 | 7 | -0.000012399 |  | -0.000005537 | -0.000010715 | 0.000737735 | 0.240400587 |
| top_s3_composite_13 | s3_composite | 408 | 0 | 0 | 208 | 4 | 408 | 4 | -0.000012339 |  | -0.000005518 | -0.000010715 | 0.000614412 | 0.240400587 |
| top_s3_abs_13 | s3_abs | 408 | 0 | 0 | 208 | 4 | 408 | 4 | -0.000012202 |  | -0.000005475 | -0.000010715 | 0.000550882 | 0.240400587 |
| top_s3_composite_3 | s3_composite | 12 | 0 | 0 | 0 | 0 | 12 | 3 | -0.000012165 |  | -0.000004513 | -0.000000483 | 0.000975999 | 0.251560905 |
| top_s3_composite_21 | s3_composite | 408 | 0 | 0 | 208 | 0 | 408 | 0 | -0.000012064 |  |  | -0.000010715 | 0.000315446 | 0.240400587 |
| top_s3_abs_21 | s3_abs | 408 | 0 | 0 | 208 | 0 | 408 | 0 | -0.000012007 |  |  | -0.000010715 | 0.000248000 | 0.240400587 |
| top_s3_composite_34 | s3_composite | 408 | 0 | 0 | 208 | 0 | 408 | 0 | -0.000011829 |  |  | -0.000010715 | 0.000089040 | 0.240400587 |
| top_s3_abs_34 | s3_abs | 408 | 0 | 0 | 208 | 0 | 408 | 0 | -0.000011811 |  |  | -0.000010715 | 0.000089040 | 0.240400587 |
| s3_non_e101 | full | 306 | 0 | 0 | 156 | 0 | 306 | 0 | -0.000011778 |  |  | -0.000010715 | 0.000085953 | 0.240400587 |
| s3_all | full | 306 | 0 | 0 | 156 | 0 | 306 | 0 | -0.000011730 |  |  | -0.000010715 | 0.000000000 | 0.240400587 |

## Blockers

| gate_class | component | fail_count | rows | fail_rate |
| --- | --- | --- | --- | --- |
| all_four | fail_action_cos | 0 | 10 | 0.000000000 |
| all_four | fail_action_active_q2s3 | 0 | 10 | 0.000000000 |
| all_four | fail_action_e72 | 0 | 10 | 0.000000000 |
| all_four | fail_action_material | 0 | 10 | 0.000000000 |
| all_four | fail_relaxed | 0 | 10 | 0.000000000 |
| all_four | fail_budget | 0 | 10 | 0.000000000 |
| all_four | fail_post101 | 0 | 10 | 0.000000000 |
| missing_actionable | fail_action_cos | 316 | 372 | 0.849462366 |
| missing_actionable | fail_action_active_q2s3 | 293 | 372 | 0.787634409 |
| missing_actionable | fail_action_e72 | 0 | 372 | 0.000000000 |
| missing_actionable | fail_action_material | 0 | 372 | 0.000000000 |
| missing_actionable | fail_relaxed | 0 | 372 | 0.000000000 |
| missing_actionable | fail_budget | 0 | 372 | 0.000000000 |
| missing_actionable | fail_post101 | 0 | 372 | 0.000000000 |
| missing_relaxed | fail_relaxed | 37 | 37 | 1.000000000 |
| missing_relaxed | fail_action_cos | 0 | 37 | 0.000000000 |
| missing_relaxed | fail_action_active_q2s3 | 0 | 37 | 0.000000000 |
| missing_relaxed | fail_action_e72 | 0 | 37 | 0.000000000 |
| missing_relaxed | fail_action_material | 0 | 37 | 0.000000000 |
| missing_relaxed | fail_budget | 0 | 37 | 0.000000000 |
| missing_relaxed | fail_post101 | 0 | 37 | 0.000000000 |
| other | fail_relaxed | 7039 | 7039 | 1.000000000 |
| other | fail_post101 | 6802 | 7039 | 0.966330445 |
| other | fail_action_cos | 3346 | 7039 | 0.475351612 |
| other | fail_action_active_q2s3 | 796 | 7039 | 0.113084245 |
| other | fail_action_e72 | 0 | 7039 | 0.000000000 |
| other | fail_action_material | 0 | 7039 | 0.000000000 |
| other | fail_budget | 0 | 7039 | 0.000000000 |

## Frontier Rows

| strategy | gate_class | mask_name | ranker | top_n | keep_factor | rollback_s3_cells | source_tag | all_minus_base | all_four | e154_submit | beats_e144_local | relaxed_structural_tol1e12 | budget_ok | post101_ok | gate_strict_actionable | gate_cos95_resid025 | gate_active_q2s3_not_more_than_e101 | q2s3_delta95_l1 | tail_equal_law_resid_ratio | post101_p95_vs_e95_e101_sensor | e72_plausible_gap_vs_e95 | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s3_active_boundary_repair | all_four | top_s3_e101_3 | s3_e101 | 3 | 0.250000000 | 3 | e152_efe33e46 | -0.000012158 | True | True | True | True | True | True | True | True | True | 0.001076529 | 0.240817737 | -0.000004653 | -0.000002860 | e154_9f2e2e73 |
| s3_active_boundary_repair | all_four | s3_e101_active | full | 5 | 0.250000000 | 5 | e152_efe33e46 | -0.000012154 | True | True | True | True | True | True | True | True | True | 0.001071346 | 0.240817737 | -0.000004652 | -0.000002860 | e154_145ca297 |
| s3_active_boundary_repair | all_four | top_s3_e101_2 | s3_e101 | 2 | 0.100000000 | 2 | e152_efe33e46 | -0.000012145 | True | True | True | True | True | True | True | True | True | 0.001069467 | 0.240817737 | -0.000004648 | -0.000002860 | e154_5f3e8c76 |
| s3_active_boundary_repair | all_four | top_s3_e101_3 | s3_e101 | 3 | 0.250000000 | 3 | e152_50b3194b | -0.000012143 | True | True | True | True | True | True | True | True | True | 0.001075031 | 0.240854524 | -0.000004646 | -0.000002846 | e154_d4039203 |
| s3_active_boundary_repair | all_four | s3_e101_active | full | 4 | 0.250000000 | 4 | e152_50b3194b | -0.000012139 | True | True | True | True | True | True | True | True | True | 0.001070791 | 0.240854524 | -0.000004644 | -0.000002846 | e154_c7204c7c |
| s3_active_boundary_repair | all_four | top_s3_e101_1 | s3_e101 | 1 | 0.000000000 | 1 | e152_83890456 | -0.000012139 | True | True | True | True | True | True | True | True | True | 0.001078406 | 0.246108711 | -0.000004626 | -0.000001826 | e154_4fe9b135 |
| s3_active_boundary_repair | all_four | top_s3_e101_3 | s3_e101 | 3 | 0.100000000 | 3 | e152_efe33e46 | -0.000012134 | True | True | True | True | True | True | True | True | True | 0.001064382 | 0.240817737 | -0.000004645 | -0.000002860 | e154_7dda52b2 |
| s3_active_boundary_repair | all_four | top_s3_e101_2 | s3_e101 | 2 | 0.100000000 | 2 | e152_50b3194b | -0.000012130 | True | True | True | True | True | True | True | True | True | 0.001067965 | 0.240854524 | -0.000004641 | -0.000002846 | e154_93e04b8a |
| s3_active_boundary_repair | all_four | top_s3_e101_3 | s3_e101 | 3 | 0.100000000 | 3 | e152_50b3194b | -0.000012119 | True | True | True | True | True | True | True | True | True | 0.001062877 | 0.240854524 | -0.000004637 | -0.000002846 | e154_6183cc59 |
| s3_active_boundary_repair | all_four | s3_e101_active | full | 5 | 0.000000000 | 5 | e152_efe33e46 | -0.000012112 | True | True | True | True | True | True | True | True | True | 0.001049373 | 0.240817737 | -0.000004637 | -0.000002860 | e154_a37b00e0 |
| control_nearmiss | missing_actionable | none |  | 0 | 1.000000000 | 0 | e152_14f03eec | -0.000012803 | False | False | True | True | True | True | False | False | False | 0.001172251 | 0.256281889 | -0.000005662 | 0.000000000 | e154_14f03eec |
| control_nearmiss | missing_actionable | none |  | 0 | 1.000000000 | 0 | e152_c7c68547 | -0.000012794 | False | False | True | True | True | True | False | False | False | 0.001171910 | 0.256198387 | -0.000005654 | 0.000000000 | e154_c7c68547 |
| control_nearmiss | missing_actionable | none |  | 0 | 1.000000000 | 0 | e152_4acbdc73 | -0.000012761 | False | False | True | True | True | True | False | False | False | 0.001175323 | 0.255619774 | -0.000005604 | 0.000000000 | e154_4acbdc73 |
| control_nearmiss | missing_actionable | none |  | 0 | 1.000000000 | 0 | e152_2ac8771f | -0.000012756 | False | False | True | True | True | True | False | False | False | 0.001175134 | 0.255578314 | -0.000005599 | 0.000000000 | e154_2ac8771f |
| s3_active_boundary_repair | missing_actionable | top_s3_e101_1 | s3_e101 | 1 | 0.500000000 | 1 | e152_2ac8771f | -0.000012728 | False | False | True | True | True | True | False | False | False | 0.001155134 | 0.255578314 | -0.000005591 | 0.000000000 | e154_590d5ff3 |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.500000000 | 1 | e152_14f03eec | -0.000012690 | False | False | True | True | True | True | False | False | False | 0.001152251 | 0.256281889 | -0.000005627 | 0.000000000 | e154_2b78660e |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.500000000 | 1 | e152_c7c68547 | -0.000012681 | False | False | True | True | True | True | False | False | False | 0.001151910 | 0.256198387 | -0.000005619 | 0.000000000 | e154_2c7c3917 |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.500000000 | 1 | e152_4acbdc73 | -0.000012647 | False | False | True | True | True | True | False | False | False | 0.001152422 | 0.255619774 | -0.000005568 | 0.000000000 | e154_b1b5483b |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.500000000 | 1 | e152_2ac8771f | -0.000012642 | False | False | True | True | True | True | False | False | False | 0.001152235 | 0.255578314 | -0.000005564 | 0.000000000 | e154_23f1db9e |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.250000000 | 1 | e152_14f03eec | -0.000012627 | False | False | True | True | True | True | False | False | False | 0.001142251 | 0.256281889 | -0.000005608 | 0.000000000 | e154_3b95be6e |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.250000000 | 1 | e152_c7c68547 | -0.000012618 | False | False | True | True | True | True | False | False | False | 0.001141910 | 0.256198387 | -0.000005599 | 0.000000000 | e154_88622038 |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.100000000 | 1 | e152_14f03eec | -0.000012588 | False | False | True | True | True | True | False | False | False | 0.001136251 | 0.256281889 | -0.000005595 | 0.000000000 | e154_13c0dc1e |
| s3_active_boundary_repair | missing_actionable | top_s3_composite_5 | s3_composite | 5 | 0.500000000 | 5 | e152_4acbdc73 | -0.000012588 | False | False | True | True | True | True | False | False | False | 0.001106422 | 0.255619774 | -0.000005550 | 0.000000000 | e154_6cddbe9c |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_2 | s3_abs | 2 | 0.500000000 | 2 | e152_14f03eec | -0.000012583 | False | False | True | True | True | True | False | False | False | 0.001132251 | 0.256281889 | -0.000005594 | 0.000000000 | e154_696cae53 |
| s3_active_boundary_repair | missing_actionable | top_s3_composite_5 | s3_composite | 5 | 0.500000000 | 5 | e152_2ac8771f | -0.000012583 | False | False | True | True | True | True | False | False | False | 0.001106235 | 0.255578314 | -0.000005545 | 0.000000000 | e154_39338dbe |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.250000000 | 1 | e152_4acbdc73 | -0.000012581 | False | False | True | True | True | True | False | False | False | 0.001140971 | 0.255619774 | -0.000005548 | 0.000000000 | e154_94ac660a |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.100000000 | 1 | e152_c7c68547 | -0.000012579 | False | False | True | True | True | True | False | False | False | 0.001135910 | 0.256198387 | -0.000005587 | 0.000000000 | e154_855a3ab4 |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.250000000 | 1 | e152_2ac8771f | -0.000012576 | False | False | True | True | True | True | False | False | False | 0.001140786 | 0.255578314 | -0.000005543 | 0.000000000 | e154_7dcb1e1a |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_2 | s3_abs | 2 | 0.500000000 | 2 | e152_c7c68547 | -0.000012574 | False | False | True | True | True | True | False | False | False | 0.001131910 | 0.256198387 | -0.000005585 | 0.000000000 | e154_2110cabd |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.000000000 | 1 | e152_14f03eec | -0.000012561 | False | False | True | True | True | True | False | False | False | 0.001132251 | 0.256281889 | -0.000005587 | 0.000000000 | e154_36d2b1ee |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.000000000 | 1 | e152_c7c68547 | -0.000012552 | False | False | True | True | True | True | False | False | False | 0.001131910 | 0.256198387 | -0.000005579 | 0.000000000 | e154_eb4f4531 |
| control_nearmiss | missing_actionable | none |  | 0 | 1.000000000 | 0 | e152_f1bf70c9 | -0.000012537 | False | False | True | True | True | True | False | False | False | 0.001175294 | 0.253113087 | -0.000005240 | 0.000000000 | e154_f1bf70c9 |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.100000000 | 1 | e152_4acbdc73 | -0.000012536 | False | False | True | True | True | True | False | False | False | 0.001134101 | 0.255619774 | -0.000005534 | 0.000000000 | e154_82537a1c |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_2 | s3_abs | 2 | 0.500000000 | 2 | e152_4acbdc73 | -0.000012533 | False | False | True | True | True | True | False | False | False | 0.001132422 | 0.255619774 | -0.000005533 | 0.000000000 | e154_aeb526cf |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.100000000 | 1 | e152_2ac8771f | -0.000012531 | False | False | True | True | True | True | False | False | False | 0.001133917 | 0.255578314 | -0.000005529 | 0.000000000 | e154_420de9de |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_2 | s3_abs | 2 | 0.500000000 | 2 | e152_2ac8771f | -0.000012528 | False | False | True | True | True | True | False | False | False | 0.001132235 | 0.255578314 | -0.000005528 | 0.000000000 | e154_6b8b0244 |
| control_nearmiss | missing_actionable | none |  | 0 | 1.000000000 | 0 | e152_9d5d8200 | -0.000012524 | False | False | True | True | True | True | False | False | False | 0.001174594 | 0.252641148 | -0.000005020 | 0.000000000 | e154_9d5d8200 |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_3 | s3_abs | 3 | 0.500000000 | 3 | e152_14f03eec | -0.000012509 | False | False | True | True | True | True | False | False | False | 0.001112251 | 0.256281889 | -0.000005571 | 0.000000000 | e154_c670cd0f |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.000000000 | 1 | e152_4acbdc73 | -0.000012509 | False | False | True | True | True | True | False | False | False | 0.001129521 | 0.255619774 | -0.000005525 | 0.000000000 | e154_38fc3fc2 |
| control_nearmiss | missing_actionable | none |  | 0 | 1.000000000 | 0 | e152_0a49b46b | -0.000012509 | False | False | True | True | True | True | False | False | False | 0.001185187 | 0.252196698 | -0.000004726 | 0.000000000 | e154_0a49b46b |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_1 | s3_abs | 1 | 0.000000000 | 1 | e152_2ac8771f | -0.000012504 | False | False | True | True | True | True | False | False | False | 0.001129337 | 0.255578314 | -0.000005521 | 0.000000000 | e154_cf329528 |
| s3_active_boundary_repair | missing_actionable | top_s3_e101_1 | s3_e101 | 1 | 0.500000000 | 1 | e152_f1bf70c9 | -0.000012503 | False | False | True | True | True | True | False | False | False | 0.001155294 | 0.253113087 | -0.000005229 | 0.000000000 | e154_9a2af714 |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_3 | s3_abs | 3 | 0.500000000 | 3 | e152_c7c68547 | -0.000012500 | False | False | True | True | True | True | False | False | False | 0.001111910 | 0.256198387 | -0.000005562 | 0.000000000 | e154_5a46d8e8 |
| control_nearmiss | missing_actionable | none |  | 0 | 1.000000000 | 0 | e152_3cc21d18 | -0.000012497 | False | False | True | True | True | True | False | False | False | 0.001188083 | 0.251417944 | -0.000004624 | 0.000000000 | e154_3cc21d18 |
| s3_active_boundary_repair | missing_actionable | top_s3_e101_1 | s3_e101 | 1 | 0.500000000 | 1 | e152_9d5d8200 | -0.000012491 | False | False | True | True | True | True | False | False | False | 0.001154594 | 0.252641148 | -0.000005013 | 0.000000000 | e154_2026d520 |
| control_nearmiss | missing_actionable | none |  | 0 | 1.000000000 | 0 | e152_63dfca26 | -0.000012488 | False | False | True | True | True | True | False | False | False | 0.001172895 | 0.251902109 | -0.000004594 | 0.000000000 | e154_63dfca26 |
| s3_active_boundary_repair | missing_actionable | top_s3_e101_1 | s3_e101 | 1 | 0.250000000 | 1 | e152_f1bf70c9 | -0.000012485 | False | False | True | True | True | True | False | False | False | 0.001145294 | 0.253113087 | -0.000005223 | 0.000000000 | e154_a8e50b17 |
| control_nearmiss | missing_actionable | none |  | 0 | 1.000000000 | 0 | e152_cacfe566 | -0.000012479 | False | False | True | True | True | True | False | False | False | 0.001187829 | 0.251238371 | -0.000004617 | 0.000000000 | e154_cacfe566 |
| s3_active_boundary_repair | missing_actionable | top_s3_composite_5 | s3_composite | 5 | 0.250000000 | 5 | e152_4acbdc73 | -0.000012477 | False | False | True | True | True | True | False | False | True | 0.001071971 | 0.255619774 | -0.000005515 | 0.000000000 | e154_66eb5e62 |
| s3_active_boundary_repair | missing_actionable | top_s3_composite_5 | s3_composite | 5 | 0.250000000 | 5 | e152_2ac8771f | -0.000012472 | False | False | True | True | True | True | False | False | True | 0.001071786 | 0.255578314 | -0.000005511 | 0.000000000 | e154_f03604f1 |
| s3_active_boundary_repair | missing_actionable | top_s3_e101_1 | s3_e101 | 1 | 0.100000000 | 1 | e152_f1bf70c9 | -0.000012471 | False | False | True | True | True | True | False | False | False | 0.001139294 | 0.253113087 | -0.000005219 | 0.000000000 | e154_b52e2e0e |
| control_nearmiss | missing_actionable | none |  | 0 | 1.000000000 | 0 | e152_c0838df9 | -0.000012470 | False | False | True | True | True | True | False | False | False | 0.001172695 | 0.251712562 | -0.000004588 | 0.000000000 | e154_c0838df9 |
| s3_active_boundary_repair | missing_actionable | top_s3_e101_1 | s3_e101 | 1 | 0.500000000 | 1 | e152_3cc21d18 | -0.000012463 | False | False | True | True | True | True | False | False | False | 0.001168083 | 0.251417944 | -0.000004614 | 0.000000000 | e154_06617a00 |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_3 | s3_abs | 3 | 0.500000000 | 3 | e152_4acbdc73 | -0.000012463 | False | False | True | True | True | True | False | False | False | 0.001112422 | 0.255619774 | -0.000005511 | 0.000000000 | e154_dbf1cb0a |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_3 | s3_abs | 3 | 0.500000000 | 3 | e152_2ac8771f | -0.000012458 | False | False | True | True | True | True | False | False | False | 0.001112235 | 0.255578314 | -0.000005506 | 0.000000000 | e154_e72ef1db |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_2 | s3_abs | 2 | 0.250000000 | 2 | e152_14f03eec | -0.000012457 | False | False | True | True | True | True | False | False | False | 0.001112251 | 0.256281889 | -0.000005555 | 0.000000000 | e154_884b2c80 |
| s3_active_boundary_repair | missing_actionable | top_s3_e101_1 | s3_e101 | 1 | 0.500000000 | 1 | e152_63dfca26 | -0.000012455 | False | False | True | True | True | True | False | False | False | 0.001152895 | 0.251902109 | -0.000004584 | 0.000000000 | e154_f34fcfe6 |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_2 | s3_abs | 2 | 0.250000000 | 2 | e152_c7c68547 | -0.000012448 | False | False | True | True | True | True | False | False | False | 0.001111910 | 0.256198387 | -0.000005546 | 0.000000000 | e154_9758b00b |
| s3_active_boundary_repair | missing_actionable | top_s3_abs_5 | s3_abs | 5 | 0.500000000 | 5 | e152_14f03eec | -0.000012446 | False | False | True | True | True | True | False | False | True | 0.001072251 | 0.256281889 | -0.000005551 | 0.000000000 | e154_31dd95a9 |
| s3_active_boundary_repair | missing_actionable | top_s3_e101_1 | s3_e101 | 1 | 0.500000000 | 1 | e152_cacfe566 | -0.000012444 | False | False | True | True | True | True | False | False | False | 0.001167829 | 0.251238371 | -0.000004607 | 0.000000000 | e154_cb5ca9de |

## Decision

Materialized `submission_e154_s3repair_9f2e2e73.csv`. This is a repaired E152 near-miss that passes all-four gates and beats E144 locally.
