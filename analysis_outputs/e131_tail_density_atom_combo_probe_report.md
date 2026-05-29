# E131 Tail-Density Atom-Combo Probe

## Question

E130 found local-upside density atoms and public-veto-safe atoms in separate regions. Is this just a linear-combination problem, or is the E95 successor direction itself missing?

## Method

- Select the strongest E130 E95-relative local-strict atoms.
- Select E130 atoms that pass separated transfer-shrinkage vetoes, prioritizing material veto-actionable rows and near-null safe local-negative rows.
- Build logit-space local+safe combinations from E95.
- Independently clip the worst hard-tail-risk cells from each local atom.
- Score only against E95-relative local stress, separated E128/E129 vetoes, and E124 post-E101 transfer filters.

## Counts

- local atoms: `14`
- safe atoms: `22`
- candidate rows: `6384`
- evaluated candidates: `700`
- local strict candidates: `651`
- veto-actionable candidates: `208`
- local-strict plus veto-actionable candidates: `0`
- final submit-gate candidates: `0`
- transfer rows: `1348`
- materialized submission: `none`

## Local Atoms

| pred_index | source | mask_name | alpha | all_minus_base | strict_gate | gate_strict_actionable | mean_abs_logit_move_vs_e95 | e72_adverse_positive_exposure_all | tail_equal_law_cosine | post101_mean_vs_e95_e101_sensor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 115 | e86 | low_alpha_all_q0.70_raw | 1.000000000 | -0.000001512 | True | False | 0.000498321 | 0.001003993 | 0.830745622 | 0.000016158 |
| 127 | e86 | low_alpha_all_q0.85_raw | 1.000000000 | -0.000001344 | True | False | 0.000449714 | 0.000987016 | 0.827381326 | 0.000014763 |
| 114 | e86 | low_alpha_all_q0.70_raw | 0.750000000 | -0.000001272 | True | False | 0.000373741 | 0.000950096 | 0.890020304 | 0.000011952 |
| 126 | e86 | low_alpha_all_q0.85_raw | 0.750000000 | -0.000001143 | True | False | 0.000337285 | 0.000937367 | 0.888248722 | 0.000010910 |
| 383 | e90 | low_alpha_all_q0.70_raw | 1.000000000 | -0.000001023 | True | False | 0.000368034 | 0.000928162 | 0.903963946 | 0.000010158 |
| 113 | e86 | low_alpha_all_q0.70_raw | 0.500000000 | -0.000000950 | True | False | 0.000249160 | 0.000896284 | 0.944376787 | 0.000007846 |
| 395 | e90 | low_alpha_all_q0.85_raw | 1.000000000 | -0.000000946 | True | False | 0.000291439 | 0.000916709 | 0.903140393 | 0.000009200 |
| 125 | e86 | low_alpha_all_q0.85_raw | 0.500000000 | -0.000000857 | True | False | 0.000224857 | 0.000887801 | 0.943768737 | 0.000007159 |
| 382 | e90 | low_alpha_all_q0.70_raw | 0.750000000 | -0.000000842 | True | False | 0.000276026 | 0.000893281 | 0.940814351 | 0.000007529 |
| 135 | e86 | low_alpha_s_all_q0.70_raw | 1.000000000 | -0.000000839 | True | False | 0.000189840 | 0.000877565 | 0.994049046 | 0.000004666 |
| 394 | e90 | low_alpha_all_q0.85_raw | 0.750000000 | -0.000000784 | True | False | 0.000218579 | 0.000884695 | 0.940562658 | 0.000006811 |
| 134 | e86 | low_alpha_s_all_q0.70_raw | 0.750000000 | -0.000000643 | True | False | 0.000142380 | 0.000855388 | 0.996520438 | 0.000003483 |
| 381 | e90 | low_alpha_all_q0.70_raw | 0.500000000 | -0.000000613 | True | False | 0.000184017 | 0.000858446 | 0.971516375 | 0.000004957 |
| 393 | e90 | low_alpha_all_q0.85_raw | 0.500000000 | -0.000000568 | True | False | 0.000145719 | 0.000852725 | 0.971537694 | 0.000004485 |

## Safe Atoms

| pred_index | source | mask_name | alpha | all_minus_base | strict_gate | gate_strict_actionable | mean_abs_logit_move_vs_e95 | e72_adverse_positive_exposure_all | tail_equal_law_cosine | post101_mean_vs_e95_e101_sensor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1620 | mixmin | density_score_all_q0.70_raw | 0.250000000 | 0.000001976 | False | True | 0.000525699 | 0.000698111 | 0.998631749 |  |
| 1412 | mixmin | tail_equal_all_q0.70_raw | 0.250000000 | 0.000001858 | False | True | 0.000445126 | 0.000707078 | 0.998395011 |  |
| 1436 | mixmin | tail_equal_s_all_q0.70_raw | 0.250000000 | 0.000001792 | False | True | 0.000427892 | 0.000708870 | 0.998077757 |  |
| 1644 | mixmin | density_score_s_all_q0.70_raw | 0.250000000 | 0.000001763 | False | True | 0.000435248 | 0.000704277 | 0.997342314 |  |
| 1668 | mixmin | density_score_non_q2s3_q0.70_raw | 0.250000000 | 0.000001557 | False | True | 0.000380657 | 0.000709820 | 0.995748947 |  |
| 1460 | mixmin | tail_equal_non_q2s3_q0.70_raw | 0.250000000 | 0.000001475 | False | True | 0.000326174 | 0.000716021 | 0.995114664 |  |
| 1568 | mixmin | low_alpha_non_q2s3_q0.70_raw | 0.250000000 | 0.000001350 | False | True | 0.000357824 | 0.000718969 | 0.993563520 |  |
| 1529 | mixmin | low_alpha_all_q0.70_nonactive_low_e72 | 0.500000000 | 0.000001620 | False | True | 0.000334692 | 0.000750622 | 0.980568200 |  |
| 1649 | mixmin | density_score_s_all_q0.70_nonactive_low_e72 | 0.500000000 | 0.000001626 | False | True | 0.000309682 | 0.000753757 | 0.979453167 |  |
| 939 | e85 | low_alpha_all_q0.70_raw | 1.000000000 | 0.000000900 | False | True | 0.000346578 | 0.000746057 | 0.994395664 |  |
| 1441 | mixmin | tail_equal_s_all_q0.70_nonactive_low_e72 | 0.500000000 | 0.000001661 | False | True | 0.000357419 | 0.000752025 | 0.977686428 |  |
| 1417 | mixmin | tail_equal_all_q0.70_nonactive_low_e72 | 0.500000000 | 0.000001781 | False | True | 0.000391887 | 0.000748447 | 0.976961144 |  |
| 1625 | mixmin | density_score_all_q0.70_nonactive_low_e72 | 0.500000000 | 0.000002201 | False | True | 0.000475134 | 0.000741450 | 0.976434046 |  |
| 1560 | mixmin | low_alpha_s_all_q0.85_raw | 0.250000000 | 0.000001117 | False | True | 0.000353565 | 0.000669801 | 0.990190113 |  |
| 1588 | mixmin | low_alpha_e95_moved_q0.70_raw | 0.250000000 | 0.000001214 | False | True | 0.000384691 | 0.000658650 | 0.990414571 |  |
| 1536 | mixmin | low_alpha_all_q0.85_raw | 0.250000000 | 0.000001336 | False | True | 0.000457254 | 0.000642259 | 0.990962007 |  |
| 1548 | mixmin | low_alpha_s_all_q0.70_raw | 0.250000000 | 0.000002056 | False | True | 0.000616669 | 0.000630402 | 0.993782582 |  |
| 1524 | mixmin | low_alpha_all_q0.70_raw | 0.250000000 | 0.000002493 | False | True | 0.000752079 | 0.000606714 | 0.996903299 |  |
| 1503 | mixmin | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | -0.000000148 | False | False | 0.000017972 | 0.000784034 | 0.994619280 |  |
| 1502 | mixmin | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 0.750000000 | -0.000000116 | False | False | 0.000013479 | 0.000785248 | 0.996978970 |  |
| 1501 | mixmin | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 0.500000000 | -0.000000080 | False | False | 0.000008986 | 0.000786466 | 0.998661172 |  |
| 1500 | mixmin | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 0.250000000 | -0.000000041 | False | False | 0.000004493 | 0.000787688 | 0.999666588 |  |

## Summary

| strategy | local_source | safe_source | rows | evaluated | strict | veto_actionable | local_and_veto | submit_gate | best_all_minus_e95 | best_sensor_mean_vs_e95 | best_sensor_p95_vs_e95 | best_tail_exposure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| atom_combo | e86 | mixmin | 3360 | 487 | 445 | 125 | 0 | 0 | -0.000001813 | 0.000002326 | 0.000008205 | 0.000998187 |
| atom_combo | e90 | mixmin | 2520 | 159 | 155 | 83 | 0 | 0 | -0.000001274 | 0.000003321 | 0.000010421 | 0.000922356 |
| risk_clipped_local | e86 |  | 128 | 37 | 34 | 0 | 0 | 0 | -0.000001442 | 0.000004400 | 0.000011143 | 0.001017127 |
| atom_combo | e86 | e85 | 160 | 11 | 11 | 0 | 0 | 0 | -0.000001343 | 0.000008502 | 0.000020797 | 0.000993143 |
| risk_clipped_local | e90 |  | 96 | 4 | 4 | 0 | 0 | 0 | -0.000000868 | 0.000006771 | 0.000016639 | 0.000922349 |
| atom_combo | e90 | e85 | 120 | 2 | 2 | 0 | 0 | 0 | -0.000000846 | 0.000009846 | 0.000021870 | 0.000917315 |

## Best Local Evaluated Candidates

| strategy | source | local_mask | safe_mask | local_scale | safe_scale | clip_quantile | all_minus_base | sets_beating_base | sets_tail_neutral | hidden_q2s3_mean_minus_base | world_support_minus_base | e72_adverse_positive_exposure_all | mean_abs_logit_move_vs_e95 | tail_equal_law_cosine | tail_equal_law_resid_ratio | gate_strict_actionable | post101_mean_vs_e95_e101_sensor | post101_p95_vs_e95_e101_sensor | post101_beat_e95_rate_e101_sensor | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 1.500000000 |  | -0.000001813 | 3 | 3 | -0.000126446 | -0.000178528 | 0.000998187 | 0.000519343 | 0.821727577 | 0.742192908 | False | 0.000014889 | 0.000040374 | 0.035087719 | e131_atom_combo_dacbf4e8 |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 1.500000000 |  | -0.000001727 | 3 | 3 | -0.000126446 | -0.000178761 | 0.000998637 | 0.000512603 | 0.825096212 | 0.736013464 | False | 0.000015216 | 0.000040682 | 0.035087719 | e131_atom_combo_d317887e |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 1.000000000 |  | -0.000001701 | 3 | 3 | -0.000126446 | -0.000178807 | 0.000999099 | 0.000510356 | 0.826054827 | 0.734398917 | False | 0.000015323 | 0.000040776 | 0.017543860 | e131_atom_combo_bece8254 |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 0.750000000 |  | -0.000001658 | 3 | 3 | -0.000126446 | -0.000178802 | 0.001000317 | 0.000505863 | 0.827724103 | 0.731846868 | False | 0.000015526 | 0.000040930 | 0.017543860 | e131_atom_combo_2b49b7f3 |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 1.000000000 |  | -0.000001658 | 3 | 3 | -0.000126446 | -0.000178802 | 0.001000317 | 0.000505863 | 0.827724103 | 0.731846868 | False | 0.000015526 | 0.000040930 | 0.017543860 | e131_atom_combo_2b49b7f3 |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 1.500000000 |  | -0.000001658 | 3 | 3 | -0.000126446 | -0.000178802 | 0.001000317 | 0.000505863 | 0.827724103 | 0.731846868 | False | 0.000015526 | 0.000040930 | 0.017543860 | e131_atom_combo_2b49b7f3 |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 0.750000000 |  | -0.000001624 | 3 | 3 | -0.000126446 | -0.000178794 | 0.001001232 | 0.000502493 | 0.828758626 | 0.730529801 | False | 0.000015681 | 0.000041052 | 0.017543860 | e131_atom_combo_65f08dc3 |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 0.500000000 |  | -0.000001612 | 3 | 3 | -0.000126446 | -0.000178791 | 0.001001538 | 0.000501370 | 0.829062033 | 0.730205087 | False | 0.000015733 | 0.000041095 | 0.017543860 | e131_atom_combo_0eaf2d0b |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 1.000000000 |  | -0.000001612 | 3 | 3 | -0.000126446 | -0.000178791 | 0.001001538 | 0.000501370 | 0.829062033 | 0.730205087 | False | 0.000015733 | 0.000041095 | 0.017543860 | e131_atom_combo_0eaf2d0b |
| atom_combo | e86+mixmin | low_alpha_all_q0.85_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 1.500000000 |  | -0.000001608 | 3 | 3 | -0.000124976 | -0.000160471 | 0.000982136 | 0.000476672 | 0.816871830 | 0.743304558 | False | 0.000013539 | 0.000035956 | 0.070175439 | e131_atom_combo_97e744ad |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 0.500000000 |  | -0.000001588 | 3 | 3 | -0.000126446 | -0.000178783 | 0.001002150 | 0.000499123 | 0.829606743 | 0.729727600 | False | 0.000015838 | 0.000041181 | 0.017543860 | e131_atom_combo_3865d46a |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 0.750000000 |  | -0.000001588 | 3 | 3 | -0.000126446 | -0.000178783 | 0.001002150 | 0.000499123 | 0.829606743 | 0.729727600 | False | 0.000015838 | 0.000041181 | 0.017543860 | e131_atom_combo_3865d46a |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 1.500000000 |  | -0.000001588 | 3 | 3 | -0.000126446 | -0.000178783 | 0.001002150 | 0.000499123 | 0.829606743 | 0.729727600 | False | 0.000015838 | 0.000041181 | 0.017543860 | e131_atom_combo_3865d46a |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 0.250000000 |  | -0.000001564 | 3 | 3 | -0.000126446 | -0.000178774 | 0.001002763 | 0.000496877 | 0.830068765 | 0.729479720 | False | 0.000015943 | 0.000041269 | 0.017543860 | e131_atom_combo_ce4cd5b9 |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 0.500000000 |  | -0.000001564 | 3 | 3 | -0.000126446 | -0.000178774 | 0.001002763 | 0.000496877 | 0.830068765 | 0.729479720 | False | 0.000015943 | 0.000041269 | 0.017543860 | e131_atom_combo_ce4cd5b9 |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 1.000000000 |  | -0.000001564 | 3 | 3 | -0.000126446 | -0.000178774 | 0.001002763 | 0.000496877 | 0.830068765 | 0.729479720 | False | 0.000015943 | 0.000041269 | 0.017543860 | e131_atom_combo_ce4cd5b9 |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 0.250000000 |  | -0.000001551 | 3 | 3 | -0.000126446 | -0.000178769 | 0.001003070 | 0.000497184 | 0.830268827 | 0.729441964 | False | 0.000015997 | 0.000041315 | 0.000000000 | e131_atom_combo_974d7e6f |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 0.750000000 |  | -0.000001551 | 3 | 3 | -0.000126446 | -0.000178769 | 0.001003070 | 0.000497184 | 0.830268827 | 0.729441964 | False | 0.000015997 | 0.000041315 | 0.000000000 | e131_atom_combo_974d7e6f |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 0.250000000 |  | -0.000001538 | 3 | 3 | -0.000126446 | -0.000178764 | 0.001003378 | 0.000497563 | 0.830448299 | 0.729461680 | False | 0.000016050 | 0.000041361 | 0.000000000 | e131_atom_combo_63697c36 |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 0.500000000 |  | -0.000001538 | 3 | 3 | -0.000126446 | -0.000178764 | 0.001003378 | 0.000497563 | 0.830448299 | 0.729461680 | False | 0.000016050 | 0.000041361 | 0.000000000 | e131_atom_combo_63697c36 |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 0.750000000 | 1.500000000 |  | -0.000001537 | 3 | 3 | -0.000095236 | -0.000131858 | 0.000944522 | 0.000396247 | 0.880349426 | 0.565106511 | False | 0.000010724 | 0.000029615 | 0.070175439 | e131_atom_combo_28cd8d38 |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 1.500000000 |  | -0.000001537 | 3 | 3 | -0.000095236 | -0.000131858 | 0.000944522 | 0.000396247 | 0.880349426 | 0.565106511 | False | 0.000010724 | 0.000029615 | 0.070175439 | e131_atom_combo_28cd8d38 |
| atom_combo | e86+mixmin | low_alpha_all_q0.85_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 1.500000000 |  | -0.000001531 | 3 | 3 | -0.000124976 | -0.000160484 | 0.000982136 | 0.000469933 | 0.820626858 | 0.736163619 | False | 0.000013855 | 0.000036567 | 0.035087719 | e131_atom_combo_0d6862ed |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 0.250000000 |  | -0.000001525 | 3 | 3 | -0.000126446 | -0.000178758 | 0.001003685 | 0.000497942 | 0.830607217 | 0.729538865 | False | 0.000016104 | 0.000041407 | 0.000000000 | e131_atom_combo_1084152a |
| atom_combo | e86+mixmin | low_alpha_all_q0.85_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 1.000000000 |  | -0.000001514 | 3 | 3 | -0.000124976 | -0.000160485 | 0.000982136 | 0.000467686 | 0.821712863 | 0.734224800 | False | 0.000013951 | 0.000036748 | 0.035087719 | e131_atom_combo_6dbfbb00 |
| atom_combo | e86+mixmin | low_alpha_all_q0.85_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 0.750000000 |  | -0.000001484 | 3 | 3 | -0.000124976 | -0.000160484 | 0.000983350 | 0.000463193 | 0.823634116 | 0.731020241 | False | 0.000014140 | 0.000037102 | 0.035087719 | e131_atom_combo_39d3fdf2 |
| atom_combo | e86+mixmin | low_alpha_all_q0.85_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 1.000000000 |  | -0.000001484 | 3 | 3 | -0.000124976 | -0.000160484 | 0.000983350 | 0.000463193 | 0.823634116 | 0.731020241 | False | 0.000014140 | 0.000037102 | 0.035087719 | e131_atom_combo_39d3fdf2 |
| atom_combo | e86+mixmin | low_alpha_all_q0.85_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 1.500000000 |  | -0.000001484 | 3 | 3 | -0.000124976 | -0.000160484 | 0.000983350 | 0.000463193 | 0.823634116 | 0.731020241 | False | 0.000014140 | 0.000037102 | 0.035087719 | e131_atom_combo_39d3fdf2 |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 0.750000000 | 1.500000000 |  | -0.000001475 | 3 | 3 | -0.000095236 | -0.000132092 | 0.000944744 | 0.000389507 | 0.884190935 | 0.556644681 | False | 0.000011025 | 0.000029837 | 0.035087719 | e131_atom_combo_6f0efb6e |
| atom_combo | e86+mixmin | low_alpha_all_q0.70_raw | tail_equal_e95_moved_q0.85_nonactive_low_e72 | 1.000000000 | 1.500000000 |  | -0.000001475 | 3 | 3 | -0.000095236 | -0.000132092 | 0.000944744 | 0.000389507 | 0.884190935 | 0.556644681 | False | 0.000011025 | 0.000029837 | 0.035087719 | e131_atom_combo_6f0efb6e |

## Local Strict Plus Veto-Actionable Candidates

None.

## Submit-Gate Candidates

None.

## Decision

No submission. Local-upside atoms and veto-safe atoms still do not overlap after linear combination or hard-tail risk clipping.
