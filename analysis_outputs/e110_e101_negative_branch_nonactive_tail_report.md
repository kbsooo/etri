# E110 E101-Negative Branch Non-Active Tail Audit

## Question

E109 says an E101 tie/loss should not be rescued by amplifying the same active
Q2/S3 rollback cells. E110 asks whether the remaining E89 diffuse-tail
hypothesis can be isolated outside those cells.

## Result

- total unique candidates: `45`
- active-loss-safe non-control rows: `36`
- sensor candidates: `8`
- strict candidates: `0`
- materialized submission: `none`

## Summary By Family

| strategy | fallback | target_scope | rows | active_loss_safe | sensor_candidates | strict_candidates | best_broad_mean_vs_e95 | best_broad_p95_vs_e95 | best_small_loss_active_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nonactive_tail_graft | e86 | s1s2s3 | 4 | 4 | 4 | 0 | 0.000000714 | 0.000002798 | -0.000011158 |
| nonactive_tail_graft | e90 | s1s2s3 | 4 | 4 | 4 | 0 | 0.000001034 | 0.000003024 | -0.000011158 |
| control |  |  | 9 | 3 | 0 | 0 | -0.000029942 | -0.000002497 | -0.000014129 |
| nonactive_tail_graft | e90 | q2s3 | 4 | 4 | 0 | 0 | 0.000001108 | 0.000004923 | -0.000011158 |
| nonactive_tail_graft | e89 | s1s2s3 | 3 | 3 | 0 | 0 | 0.000001268 | 0.000002980 | -0.000011158 |
| nonactive_tail_graft | e90 | all | 4 | 4 | 0 | 0 | 0.000002142 | 0.000006087 | -0.000011158 |
| nonactive_tail_graft | e86 | q2s3 | 4 | 4 | 0 | 0 | 0.000002446 | 0.000008752 | -0.000011158 |
| nonactive_tail_graft | e85 | s1s2s3 | 3 | 3 | 0 | 0 | 0.000002578 | 0.000004053 | -0.000011158 |
| nonactive_tail_graft | e86 | all | 4 | 4 | 0 | 0 | 0.000003162 | 0.000009399 | -0.000011158 |
| active_restored_tail | e95 | active_q2s3 | 2 | 2 | 0 | 0 | 0.000005267 | 0.000012213 | -0.000011158 |
| active_restored_tail | e90 | active_q2s3 | 2 | 2 | 0 | 0 | 0.000008992 | 0.000016948 | -0.000013527 |
| active_restored_tail | e86 | active_q2s3 | 2 | 2 | 0 | 0 | 0.000010969 | 0.000019406 | -0.000014129 |

## Controls

| tag | base | selected_cells | all_delta_vs_mixmin | mean_vs_e95_broad_plausible | p95_vs_e95_broad_plausible | beat_e95_rate_broad_plausible | active_mean_vs_e101_small_loss | active_p95_vs_e101_small_loss | active_mean_vs_e101_large_loss | active_p95_vs_e101_large_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e110_control_541e3973 | e95 | 0 | -0.000026207 | 0.000000000 | 0.000000000 | 0.000000000 | -0.000011158 | -0.000003830 | -0.000031103 | -0.000020712 |
| e110_control_28925de5 | e90 | 162 | -0.000026932 | 0.000013372 | 0.000031244 | 0.002607184 | -0.000013527 | -0.000002847 | -0.000036451 | -0.000021878 |
| e110_control_a3f7c96f | e86 | 134 | -0.000027706 | 0.000020345 | 0.000046606 | 0.000289687 | -0.000014129 | -0.000004347 | -0.000039544 | -0.000025665 |
| e110_control_079aab57 | e108_amp050 | 50 | -0.000023875 | -0.000029942 | -0.000002497 | 0.977983778 | 0.000011723 | 0.000019546 | 0.000031668 | 0.000050083 |
| e110_control_64514c53 | e108_strict_amp038 | 50 | -0.000024687 | -0.000023695 | -0.000002181 | 0.980880649 | 0.000006026 | 0.000010093 | 0.000016397 | 0.000025973 |
| e110_control_177569bc | e101 | 50 | -0.000025372 | -0.000016205 | -0.000001564 | 0.983487833 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e110_control_00d7807f | e89 | 158 | -0.000025896 | 0.000003833 | 0.000012552 | 0.195828505 | -0.000002370 | 0.000017766 | -0.000019645 | 0.000002584 |
| e110_control_58b23ed1 | e85 | 445 | -0.000023876 | 0.000009659 | 0.000018271 | 0.031865585 | -0.000002370 | 0.000017766 | -0.000019645 | 0.000002584 |
| e110_control_0c916bb4 | mixmin | 550 | 0.000000000 | 0.000015311 | 0.000015311 | 0.000000000 | 0.000036857 | 0.000060324 | 0.000096693 | 0.000151937 |

## Best Decision Rows

| tag | strategy | base | fallback | selector | target_scope | graft_alpha | selected_cells | e110_active_loss_safe | e110_sensor_candidate | e110_strict_candidate | all_delta_vs_mixmin | mean_vs_e95_broad_plausible | p95_vs_e95_broad_plausible | beat_e95_rate_broad_plausible | mean_vs_e95_broad_q2s3 | beat_e95_rate_broad_q2s3 | active_mean_vs_e101_small_loss | active_p95_vs_e101_small_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e110_nonactive_tail_graft_9f4abae0 | nonactive_tail_graft | e95 | e86 | nonactive_s1s2s3_e86 | s1s2s3 | 0.250000000 | 74 | True | True | False | -0.000026403 | 0.000000714 | 0.000002798 | 0.274913094 | -0.000001115 | 1.000000000 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_179a2efb | nonactive_tail_graft | e95 | e90 | nonactive_s1s2s3_e90 | s1s2s3 | 0.250000000 | 118 | True | True | False | -0.000026305 | 0.000001034 | 0.000003024 | 0.181344148 | -0.000000552 | 1.000000000 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_90101bfc | nonactive_tail_graft | e95 | e86 | nonactive_s1s2s3_e86 | s1s2s3 | 0.500000000 | 74 | True | True | False | -0.000026591 | 0.000001459 | 0.000005638 | 0.272305910 | -0.000002181 | 1.000000000 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_94f1dcbf | nonactive_tail_graft | e95 | e90 | nonactive_s1s2s3_e90 | s1s2s3 | 0.500000000 | 118 | True | True | False | -0.000026391 | 0.000002106 | 0.000006080 | 0.177578216 | -0.000001046 | 1.000000000 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_c87102e2 | nonactive_tail_graft | e95 | e86 | nonactive_s1s2s3_e86 | s1s2s3 | 0.750000000 | 74 | True | True | False | -0.000026770 | 0.000002233 | 0.000008503 | 0.267960603 | -0.000003201 | 1.000000000 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_d4a64af7 | nonactive_tail_graft | e95 | e86 | nonactive_s1s2s3_e86 | s1s2s3 | 1.000000000 | 74 | True | True | False | -0.000026942 | 0.000003037 | 0.000011415 | 0.263904983 | -0.000004177 | 1.000000000 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_084ff57b | nonactive_tail_graft | e95 | e90 | nonactive_s1s2s3_e90 | s1s2s3 | 0.750000000 | 118 | True | True | False | -0.000026468 | 0.000003215 | 0.000009169 | 0.173232908 | -0.000001482 | 1.000000000 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_bb22020e | nonactive_tail_graft | e95 | e90 | nonactive_s1s2s3_e90 | s1s2s3 | 1.000000000 | 118 | True | True | False | -0.000026534 | 0.000004362 | 0.000012307 | 0.170046350 | -0.000001859 | 1.000000000 | -0.000011158 | -0.000003830 |
| e110_control_541e3973 | control | e95 |  |  |  |  | 0 | True | False | False | -0.000026207 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_6b092a86 | nonactive_tail_graft | e95 | e90 | nonactive_q2s3_e90 | q2s3 | 0.250000000 | 15 | True | False | False | -0.000026373 | 0.000001108 | 0.000004923 | 0.424391657 | 0.000003814 | 0.019021739 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_dee1389d | nonactive_tail_graft | e95 | e89 | nonactive_s1s2s3_e89 | s1s2s3 | 0.250000000 | 139 | True | False | False | -0.000026194 | 0.000001268 | 0.000002980 | 0.014194670 | 0.000000075 | 0.000000000 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_5cb93e6b | nonactive_tail_graft | e95 | e90 | nonactive_all_e90 | all | 0.250000000 | 133 | True | False | False | -0.000026471 | 0.000002142 | 0.000006087 | 0.102259560 | 0.000003261 | 0.062500000 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_6772c3c6 | nonactive_tail_graft | e95 | e90 | nonactive_q2s3_e90 | q2s3 | 0.500000000 | 15 | True | False | False | -0.000026497 | 0.000002371 | 0.000010045 | 0.423812283 | 0.000007878 | 0.019021739 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_5a814d61 | nonactive_tail_graft | e95 | e86 | nonactive_q2s3_e86 | q2s3 | 0.250000000 | 29 | True | False | False | -0.000026503 | 0.000002446 | 0.000008752 | 0.327925840 | 0.000007919 | 0.000000000 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_b6764610 | nonactive_tail_graft | e95 | e89 | nonactive_s1s2s3_e89 | s1s2s3 | 0.500000000 | 139 | True | False | False | -0.000026172 | 0.000002566 | 0.000006012 | 0.011877173 | 0.000000199 | 0.000000000 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_30bdc74b | nonactive_tail_graft | e95 | e85 | nonactive_s1s2s3_e85 | s1s2s3 | 0.250000000 | 426 | True | False | False | -0.000025730 | 0.000002578 | 0.000004053 | 0.000289687 | 0.000002715 | 0.000000000 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_adb8654a | nonactive_tail_graft | e95 | e86 | nonactive_all_e86 | all | 0.250000000 | 103 | True | False | False | -0.000026698 | 0.000003162 | 0.000009399 | 0.138760139 | 0.000006807 | 0.000000000 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_8dbe9c65 | nonactive_tail_graft | e95 | e90 | nonactive_q2s3_e90 | q2s3 | 0.750000000 | 15 | True | False | False | -0.000026578 | 0.000003793 | 0.000015389 | 0.423522596 | 0.000012201 | 0.019021739 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_5998eeab | nonactive_tail_graft | e95 | e89 | nonactive_s1s2s3_e89 | s1s2s3 | 0.750000000 | 139 | True | False | False | -0.000026141 | 0.000003899 | 0.000009078 | 0.010428737 | 0.000000376 | 0.000000000 | -0.000011158 | -0.000003830 |
| e110_nonactive_tail_graft_74642a2c | nonactive_tail_graft | e95 | e90 | nonactive_all_e90 | all | 0.500000000 | 133 | True | False | False | -0.000026682 | 0.000004476 | 0.000012471 | 0.088064890 | 0.000006830 | 0.046195652 | -0.000011158 | -0.000003830 |

## Active-World Behavior

| outcome | tag | strategy | base | fallback | selector | active_mean_vs_e101 | active_p95_vs_e101 | active_beat_e101_rate | active_mean_vs_e95 | active_p95_vs_e95 | rank_vs_e101 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| large_loss | e110_control_a3f7c96f | control | e86 |  |  | -0.000039544 | -0.000025665 | 1.000000000 | -0.000008441 | -0.000003254 | 1.000000000 |
| large_loss | e110_active_restored_tail_cdd3201e | active_restored_tail | e89 | e86 | restore_e101_active | -0.000039544 | -0.000025665 | 1.000000000 | -0.000008441 | -0.000003254 | 2.000000000 |
| large_loss | e110_active_restored_tail_01492072 | active_restored_tail | e85 | e86 | restore_e101_active | -0.000039544 | -0.000025665 | 1.000000000 | -0.000008441 | -0.000003254 | 3.000000000 |
| large_loss | e110_control_28925de5 | control | e90 |  |  | -0.000036451 | -0.000021878 | 1.000000000 | -0.000005348 | 0.000002453 | 4.000000000 |
| large_loss | e110_active_restored_tail_4f647a1a | active_restored_tail | e89 | e90 | restore_e101_active | -0.000036451 | -0.000021878 | 1.000000000 | -0.000005348 | 0.000002453 | 5.000000000 |
| large_loss | e110_active_restored_tail_1c9a7148 | active_restored_tail | e85 | e90 | restore_e101_active | -0.000036451 | -0.000021878 | 1.000000000 | -0.000005348 | 0.000002453 | 6.000000000 |
| large_loss | e110_nonactive_tail_graft_dee1389d | nonactive_tail_graft | e95 | e89 | nonactive_s1s2s3_e89 | -0.000031103 | -0.000020712 | 1.000000000 | -0.000000000 | 0.000000000 | 7.000000000 |
| large_loss | e110_nonactive_tail_graft_b6764610 | nonactive_tail_graft | e95 | e89 | nonactive_s1s2s3_e89 | -0.000031103 | -0.000020712 | 1.000000000 | -0.000000000 | 0.000000000 | 8.000000000 |
| large_loss | e110_nonactive_tail_graft_5998eeab | nonactive_tail_graft | e95 | e89 | nonactive_s1s2s3_e89 | -0.000031103 | -0.000020712 | 1.000000000 | -0.000000000 | 0.000000000 | 9.000000000 |
| large_loss | e110_nonactive_tail_graft_30bdc74b | nonactive_tail_graft | e95 | e85 | nonactive_s1s2s3_e85 | -0.000031103 | -0.000020712 | 1.000000000 | -0.000000000 | 0.000000000 | 10.000000000 |
| large_loss | e110_nonactive_tail_graft_095f2e90 | nonactive_tail_graft | e95 | e85 | nonactive_s1s2s3_e85 | -0.000031103 | -0.000020712 | 1.000000000 | -0.000000000 | 0.000000000 | 11.000000000 |
| large_loss | e110_nonactive_tail_graft_4b1b91b5 | nonactive_tail_graft | e95 | e85 | nonactive_s1s2s3_e85 | -0.000031103 | -0.000020712 | 1.000000000 | -0.000000000 | 0.000000000 | 12.000000000 |
| small_loss | e110_control_a3f7c96f | control | e86 |  |  | -0.000014129 | -0.000004347 | 0.997889405 | -0.000002971 | 0.000001181 | 1.000000000 |
| small_loss | e110_active_restored_tail_cdd3201e | active_restored_tail | e89 | e86 | restore_e101_active | -0.000014129 | -0.000004347 | 0.997889405 | -0.000002971 | 0.000001181 | 2.000000000 |
| small_loss | e110_active_restored_tail_01492072 | active_restored_tail | e85 | e86 | restore_e101_active | -0.000014129 | -0.000004347 | 0.997889405 | -0.000002971 | 0.000001181 | 3.000000000 |
| small_loss | e110_control_28925de5 | control | e90 |  |  | -0.000013527 | -0.000002847 | 0.983889123 | -0.000002369 | 0.000004371 | 4.000000000 |
| small_loss | e110_active_restored_tail_4f647a1a | active_restored_tail | e89 | e90 | restore_e101_active | -0.000013527 | -0.000002847 | 0.983889123 | -0.000002369 | 0.000004371 | 5.000000000 |
| small_loss | e110_active_restored_tail_1c9a7148 | active_restored_tail | e85 | e90 | restore_e101_active | -0.000013527 | -0.000002847 | 0.983889123 | -0.000002369 | 0.000004371 | 6.000000000 |
| small_loss | e110_control_541e3973 | control | e95 |  |  | -0.000011158 | -0.000003830 | 1.000000000 | 0.000000000 | 0.000000000 | 7.000000000 |
| small_loss | e110_active_restored_tail_aa8e2df0 | active_restored_tail | e89 | e95 | restore_e101_active | -0.000011158 | -0.000003830 | 1.000000000 | 0.000000000 | 0.000000000 | 8.000000000 |
| small_loss | e110_active_restored_tail_34cdae23 | active_restored_tail | e85 | e95 | restore_e101_active | -0.000011158 | -0.000003830 | 1.000000000 | 0.000000000 | 0.000000000 | 9.000000000 |
| small_loss | e110_nonactive_tail_graft_dee1389d | nonactive_tail_graft | e95 | e89 | nonactive_s1s2s3_e89 | -0.000011158 | -0.000003830 | 1.000000000 | 0.000000000 | 0.000000000 | 11.000000000 |
| small_loss | e110_nonactive_tail_graft_b6764610 | nonactive_tail_graft | e95 | e89 | nonactive_s1s2s3_e89 | -0.000011158 | -0.000003830 | 1.000000000 | 0.000000000 | 0.000000000 | 12.000000000 |
| small_loss | e110_nonactive_tail_graft_5998eeab | nonactive_tail_graft | e95 | e89 | nonactive_s1s2s3_e89 | -0.000011158 | -0.000003830 | 1.000000000 | 0.000000000 | 0.000000000 | 13.000000000 |
| tie | e110_control_28925de5 | control | e90 |  |  | -0.000000586 | 0.000006197 | 0.575827590 | -0.000000518 | 0.000005574 | 1.000000000 |
| tie | e110_active_restored_tail_4f647a1a | active_restored_tail | e89 | e90 | restore_e101_active | -0.000000586 | 0.000006197 | 0.575827590 | -0.000000518 | 0.000005574 | 2.000000000 |
| tie | e110_active_restored_tail_1c9a7148 | active_restored_tail | e85 | e90 | restore_e101_active | -0.000000586 | 0.000006197 | 0.575827590 | -0.000000518 | 0.000005574 | 3.000000000 |
| tie | e110_control_541e3973 | control | e95 |  |  | -0.000000069 | 0.000002675 | 0.516591642 | 0.000000000 | 0.000000000 | 4.000000000 |
| tie | e110_active_restored_tail_aa8e2df0 | active_restored_tail | e89 | e95 | restore_e101_active | -0.000000069 | 0.000002675 | 0.516591642 | 0.000000000 | 0.000000000 | 5.000000000 |
| tie | e110_active_restored_tail_34cdae23 | active_restored_tail | e85 | e95 | restore_e101_active | -0.000000069 | 0.000002675 | 0.516591642 | 0.000000000 | 0.000000000 | 6.000000000 |
| tie | e110_nonactive_tail_graft_dee1389d | nonactive_tail_graft | e95 | e89 | nonactive_s1s2s3_e89 | -0.000000069 | 0.000002675 | 0.516591642 | 0.000000000 | 0.000000000 | 8.000000000 |
| tie | e110_nonactive_tail_graft_b6764610 | nonactive_tail_graft | e95 | e89 | nonactive_s1s2s3_e89 | -0.000000069 | 0.000002675 | 0.516591642 | 0.000000000 | 0.000000000 | 9.000000000 |
| tie | e110_nonactive_tail_graft_5998eeab | nonactive_tail_graft | e95 | e89 | nonactive_s1s2s3_e89 | -0.000000069 | 0.000002675 | 0.516591642 | 0.000000000 | 0.000000000 | 10.000000000 |
| tie | e110_nonactive_tail_graft_30bdc74b | nonactive_tail_graft | e95 | e85 | nonactive_s1s2s3_e85 | -0.000000069 | 0.000002675 | 0.516591642 | 0.000000000 | 0.000000000 | 11.000000000 |
| tie | e110_nonactive_tail_graft_095f2e90 | nonactive_tail_graft | e95 | e85 | nonactive_s1s2s3_e85 | -0.000000069 | 0.000002675 | 0.516591642 | 0.000000000 | 0.000000000 | 12.000000000 |
| tie | e110_nonactive_tail_graft_4b1b91b5 | nonactive_tail_graft | e95 | e85 | nonactive_s1s2s3_e85 | -0.000000069 | 0.000002675 | 0.516591642 | 0.000000000 | 0.000000000 | 13.000000000 |

## Interpretation

If strict candidates are zero, then a negative E101 public result should not
automatically route to full E89 or a non-active E89 graft. The active-cell
failure can be separated diagnostically, but the remaining diffuse-tail movement
does not yet clear E95-conditioned downside stress.

If a strict candidate is materialized, it should be used only after E101
tie/loss and only as a test of non-active diffuse-tail allocation, not as a
general successor to E95.
