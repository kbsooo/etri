# E342 Sign-Transfer Hidden Lifestyle-State Latent

## Question

Are the weak Q2 residual intervention tail and the weak Q1/Q3 human-social microstate coalition two projections of one hidden lifestyle state?

## Source Selection

### Q2 Residual-Tail Sources

| basename | tail_mask | topk | variant | scale | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top34_inv_s0_55_787b726b.csv | posdelta | 34 | inv | 0.550000000 | -0.000150576 | -0.000017477 | 0.902777778 | 0.008568346 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top34_inv_bad_veto_s0_55_836c3ab3.csv | posdelta | 34 | inv_bad_veto | 0.550000000 | -0.000140976 | -0.000015473 | 0.902777778 | 0.008406965 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top20_inv_bad_veto_s0_55_1b03343e.csv | posdelta | 20 | inv_bad_veto | 0.550000000 | -0.000093885 | -0.000006556 | 0.902777778 | 0.008860784 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top20_inv_s0_55_2bbb8ef5.csv | posdelta | 20 | inv | 0.550000000 | -0.000097266 | -0.000006079 | 0.902777778 | 0.009123864 |

### Q1/Q3 Microstate Sources

| basename | recipe | variant | q1_weight | q3_weight | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e340_q1_E335_submission_e335_q1__q3_E339_submission_e339_q3__w1_25_1_00_bad_veto_38d229fd.csv | q1_q3_microstate_pair | bad_veto | 1.250000000 | 1.000000000 | -0.000167692 | -0.000027905 | 0.944444444 | 0.014379498 |
| submission_e340_q1_E335_submission_e335_q1__q3_E339_submission_e339_q3__w1_25_2_60_bad_veto_dde6afdc.csv | q1_q3_microstate_pair | bad_veto | 1.250000000 | 2.600000000 | -0.000195591 | -0.000027259 | 0.916666667 | 0.012073014 |
| submission_e340_q1_E335_submission_e335_q1__q3_E339_submission_e339_q3__w1_25_2_60_bad_veto_e620b452.csv | q1_q3_microstate_pair | bad_veto | 1.250000000 | 2.600000000 | -0.000194954 | -0.000027022 | 0.916666667 | 0.012025089 |
| submission_e340_q1_E335_submission_e335_q1__q3_E339_submission_e339_q3__w1_25_1_00_bad_veto_65300541.csv | q1_q3_microstate_pair | bad_veto | 1.250000000 | 1.000000000 | -0.000147583 | -0.000026838 | 0.944444444 | 0.012027035 |
| submission_e340_q1_E335_submission_e335_q1__q3_E339_submission_e339_q3__w1_00_1_00_bad_veto_3ed7c6c8.csv | q1_q3_microstate_pair | bad_veto | 1.000000000 | 1.000000000 | -0.000146428 | -0.000026831 | 0.944444444 | 0.011554822 |
| submission_e340_q1_E335_submission_e335_q1__q3_E339_submission_e339_q3__w1_00_1_00_bad_veto_83e27554.csv | q1_q3_microstate_pair | bad_veto | 1.000000000 | 1.000000000 | -0.000145871 | -0.000026730 | 0.944444444 | 0.011516482 |
| submission_e340_q1_E335_submission_e335_q1__q3_E339_submission_e339_q3__w1_25_1_00_bad_veto_565de047.csv | q1_q3_microstate_pair | bad_veto | 1.250000000 | 1.000000000 | -0.000167052 | -0.000026636 | 0.944444444 | 0.014331573 |
| submission_e340_q1_E335_submission_e335_q1__q3_E339_submission_e339_q3__w1_00_1_00_bad_veto_105ca98e.csv | q1_q3_microstate_pair | bad_veto | 1.000000000 | 1.000000000 | -0.000142464 | -0.000026583 | 0.944444444 | 0.011696433 |

## Generated Candidates

- generated candidates: `1314`
- selector-promoted candidates: `0`
- information-sensor candidates: `1019`
- movement-null-safe promoted candidates: `0`

### Best Selector Scores

| basename | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_07fbe22a.csv | information_sensor_only | -0.000247534 | -0.000504612 | -0.000054865 | 0.986111111 | 0.017961838 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_41cdeb7c.csv | information_sensor_only | -0.000258375 | -0.000598642 | -0.000054385 | 0.972222222 | 0.023117920 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_f664f537.csv | information_sensor_only | -0.000245112 | -0.000503774 | -0.000054328 | 0.986111111 | 0.017919476 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_15ec9ae3.csv | information_sensor_only | -0.000257594 | -0.000595816 | -0.000054278 | 0.972222222 | 0.023079922 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_8a33e1f8.csv | information_sensor_only | -0.000233638 | -0.000493659 | -0.000054107 | 0.972222222 | 0.020451954 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_3a5f943b.csv | information_sensor_only | -0.000259494 | -0.000597349 | -0.000053894 | 0.972222222 | 0.023209998 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_370e809e.csv | information_sensor_only | -0.000251497 | -0.000509955 | -0.000053799 | 0.986111111 | 0.017820228 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_de2ae5c9.csv | information_sensor_only | -0.000258713 | -0.000594705 | -0.000053786 | 0.972222222 | 0.023172000 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_0d8dccb1.csv | information_sensor_only | -0.000250834 | -0.000508808 | -0.000053785 | 0.986111111 | 0.017789829 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_58cbcea2.csv | information_sensor_only | -0.000234758 | -0.000493551 | -0.000053532 | 0.972222222 | 0.020544032 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_11959ac7.csv | information_sensor_only | -0.000252772 | -0.000519468 | -0.000053329 | 0.986111111 | 0.018283929 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_ed0067a5.csv | information_sensor_only | -0.000237599 | -0.000501524 | -0.000053325 | 0.986111111 | 0.020310343 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_6fff5452.csv | information_sensor_only | -0.000238867 | -0.000510104 | -0.000053323 | 0.986111111 | 0.020774044 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_cb597ee7.csv | information_sensor_only | -0.000236936 | -0.000500472 | -0.000053309 | 0.986111111 | 0.020279945 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_4ef4890a.csv | information_sensor_only | -0.000249075 | -0.000510098 | -0.000053239 | 0.986111111 | 0.017777865 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_04d63a06.csv | information_sensor_only | -0.000248412 | -0.000508951 | -0.000053225 | 0.986111111 | 0.017747467 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_9ba63390.csv | information_sensor_only | -0.000272306 | -0.000618138 | -0.000053076 | 0.986111111 | 0.020627805 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_3ee22224.csv | information_sensor_only | -0.000271524 | -0.000616955 | -0.000052958 | 0.986111111 | 0.020589807 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_1aa4c3f2.csv | information_sensor_only | -0.000239986 | -0.000509996 | -0.000052793 | 0.986111111 | 0.020866122 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_d8bcd529.csv | information_sensor_only | -0.000238719 | -0.000501416 | -0.000052784 | 0.986111111 | 0.020402421 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_b720b161.csv | information_sensor_only | -0.000238055 | -0.000500364 | -0.000052768 | 0.986111111 | 0.020372023 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_26936bff.csv | information_sensor_only | -0.000250349 | -0.000519611 | -0.000052768 | 0.986111111 | 0.018241566 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_f66da4f4.csv | information_sensor_only | -0.000283025 | -0.000552272 | -0.000052721 | 0.972222222 | 0.020071145 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_25_sum_bad_veto_09d26fe3.csv | information_sensor_only | -0.000254766 | -0.000596070 | -0.000052706 | 0.972222222 | 0.023360434 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_4b1336bf.csv | information_sensor_only | -0.000269882 | -0.000617332 | -0.000052632 | 0.986111111 | 0.020585442 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_da20cb9d.csv | information_sensor_only | -0.000269100 | -0.000616148 | -0.000052513 | 0.986111111 | 0.020547444 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_25_sum_bad_veto_ca759605.csv | information_sensor_only | -0.000255886 | -0.000594777 | -0.000052166 | 0.972222222 | 0.023452512 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_b91f5cab.csv | information_sensor_only | -0.000211292 | -0.000488459 | -0.000051954 | 0.986111111 | 0.018316504 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_25_sum_bad_veto_429828db.csv | information_sensor_only | -0.000268698 | -0.000613567 | -0.000051951 | 0.986111111 | 0.020870319 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_c53ea5c6.csv | information_sensor_only | -0.000279773 | -0.000542430 | -0.000051948 | 0.972222222 | 0.020014661 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_1c9b0ea3.csv | information_sensor_only | -0.000210459 | -0.000489541 | -0.000051912 | 0.986111111 | 0.018247445 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_88c18b2e.csv | information_sensor_only | -0.000307774 | -0.000629620 | -0.000051828 | 0.972222222 | 0.022737111 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_1390375f.csv | information_sensor_only | -0.000286987 | -0.000564391 | -0.000051816 | 0.986111111 | 0.019929534 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_cd340e9c.csv | information_sensor_only | -0.000306993 | -0.000625882 | -0.000051798 | 0.972222222 | 0.022699113 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_692a505e.csv | information_sensor_only | -0.000286323 | -0.000563654 | -0.000051792 | 0.986111111 | 0.019899136 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_e4a2847a.csv | information_sensor_only | -0.000214422 | -0.000495759 | -0.000051650 | 0.986111111 | 0.018105835 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_b9f6799f.csv | information_sensor_only | -0.000213758 | -0.000493542 | -0.000051635 | 0.986111111 | 0.018075436 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_b4890b33.csv | information_sensor_only | -0.000288257 | -0.000562732 | -0.000051373 | 0.972222222 | 0.020393235 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_25_sum_bad_veto_d35cfb60.csv | information_sensor_only | -0.000259760 | -0.000603571 | -0.000051341 | 0.986111111 | 0.023183421 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_25_sum_bad_veto_a48dd10e.csv | information_sensor_only | -0.000266274 | -0.000611033 | -0.000051275 | 0.986111111 | 0.020827956 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_b5712f95.csv | information_sensor_only | -0.000215255 | -0.000494677 | -0.000051234 | 0.986111111 | 0.018174893 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_25_sum_bad_veto_92dec973.csv | information_sensor_only | -0.000258979 | -0.000601033 | -0.000051230 | 0.986111111 | 0.023145423 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_19e27f29.csv | information_sensor_only | -0.000214591 | -0.000492539 | -0.000051220 | 0.986111111 | 0.018144495 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_9484bc28.csv | information_sensor_only | -0.000215693 | -0.000505511 | -0.000051140 | 0.986111111 | 0.018569536 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_25_sum_bad_veto_4b47577b.csv | information_sensor_only | -0.000304166 | -0.000626917 | -0.000051123 | 0.972222222 | 0.022979625 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_da47265a.csv | information_sensor_only | -0.000283734 | -0.000554550 | -0.000051042 | 0.986111111 | 0.019873051 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_d14f8871.csv | information_sensor_only | -0.000283071 | -0.000553813 | -0.000051018 | 0.972222222 | 0.019842652 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_2342e4de.csv | information_sensor_only | -0.000304520 | -0.000627253 | -0.000050915 | 0.972222222 | 0.022680628 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_dd58772f.csv | information_sensor_only | -0.000303738 | -0.000623515 | -0.000050886 | 0.972222222 | 0.022642630 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_25_sum_bad_veto_f12680af.csv | information_sensor_only | -0.000260879 | -0.000602526 | -0.000050802 | 0.986111111 | 0.023275499 |

### Candidate Anatomy

| basename | variant | q2_weight | micro_weight | q2_source_mean | q2_source_p90 | micro_source_mean | micro_source_p90 | source_overlap_rows | changed_rows | share_Q1 | share_Q2 | share_Q3 | cos_with_e323_bad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_55_1_25_q2tail_joint_centered_277e23ef.csv | q2tail_joint_centered | 0.550000000 | 1.250000000 | -0.000150576 | -0.000017477 | -0.000167052 | -0.000026636 | 34 | 34 | 0.877852735 | 0.081981070 | 0.026872282 | -0.114312701 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_55_1_00_q2tail_joint_centered_1f3404c8.csv | q2tail_joint_centered | 0.550000000 | 1.000000000 | -0.000150576 | -0.000017477 | -0.000167052 | -0.000026636 | 34 | 34 | 0.860919796 | 0.100499667 | 0.025543051 | -0.113798030 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_55_1_25_q2tail_joint_centered_4402d690.csv | q2tail_joint_centered | 0.550000000 | 1.250000000 | -0.000150576 | -0.000017477 | -0.000145871 | -0.000026730 | 34 | 34 | 0.855457050 | 0.099861972 | 0.031726218 | -0.113638786 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_25_q2tail_joint_centered_39c86492.csv | q2tail_joint_centered | 0.750000000 | 1.250000000 | -0.000150576 | -0.000017477 | -0.000167052 | -0.000026636 | 34 | 34 | 0.852440380 | 0.108556167 | 0.026094375 | -0.113515407 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_55_1_25_q2tail_joint_centered_46aedfee.csv | q2tail_joint_centered | 0.550000000 | 1.250000000 | -0.000140976 | -0.000015473 | -0.000167052 | -0.000026636 | 34 | 34 | 0.847908898 | 0.113294988 | 0.025955660 | -0.113343596 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_55_1_00_q2tail_joint_centered_baf0d4a4.csv | q2tail_joint_centered | 0.550000000 | 1.000000000 | -0.000150576 | -0.000017477 | -0.000145871 | -0.000026730 | 34 | 34 | 0.837500735 | 0.122207297 | 0.027609133 | -0.112885964 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_55_0_75_q2tail_joint_centered_f70abd18.csv | q2tail_joint_centered | 0.550000000 | 0.750000000 | -0.000150576 | -0.000017477 | -0.000167052 | -0.000026636 | 34 | 34 | 0.836459451 | 0.130192377 | 0.020681104 | -0.112736450 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_q2tail_joint_centered_4a76eac6.csv | q2tail_joint_centered | 0.750000000 | 1.000000000 | -0.000150576 | -0.000017477 | -0.000167052 | -0.000026636 | 34 | 34 | 0.830566467 | 0.132213224 | 0.024642484 | -0.112576000 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_25_q2tail_joint_centered_baf7a413.csv | q2tail_joint_centered | 0.750000000 | 1.250000000 | -0.000150576 | -0.000017477 | -0.000145871 | -0.000026730 | 34 | 34 | 0.825480992 | 0.131403695 | 0.030614500 | -0.112421824 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_55_1_00_q2tail_joint_centered_3d67acfe.csv | q2tail_joint_centered | 0.550000000 | 1.000000000 | -0.000140976 | -0.000015473 | -0.000167052 | -0.000026636 | 34 | 34 | 0.825195305 | 0.137825084 | 0.024483124 | -0.112314473 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_25_q2tail_joint_centered_ee846d3a.csv | q2tail_joint_centered | 1.000000000 | 1.250000000 | -0.000150576 | -0.000017477 | -0.000167052 | -0.000026636 | 34 | 34 | 0.822671685 | 0.139686931 | 0.025183114 | -0.112210654 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_55_1_25_q2tail_joint_centered_2cb7cd83.csv | q2tail_joint_centered | 0.550000000 | 1.250000000 | -0.000140976 | -0.000015473 | -0.000145871 | -0.000026730 | 34 | 34 | 0.820175192 | 0.136986619 | 0.030417725 | -0.112161368 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_25_q2tail_joint_centered_59ec7634.csv | q2tail_joint_centered | 0.750000000 | 1.250000000 | -0.000140976 | -0.000015473 | -0.000167052 | -0.000026636 | 34 | 34 | 0.814358799 | 0.148380173 | 0.024928646 | -0.111769233 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_55_0_75_q2tail_joint_centered_a26c6c87.csv | q2tail_joint_centered | 0.550000000 | 0.750000000 | -0.000150576 | -0.000017477 | -0.000145871 | -0.000026730 | 34 | 34 | 0.826649609 | 0.160831881 | 0.000000000 | -0.111579411 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_q2tail_joint_centered_b795ddef.csv | q2tail_joint_centered | 0.750000000 | 1.000000000 | -0.000150576 | -0.000017477 | -0.000145871 | -0.000026730 | 34 | 34 | 0.801866572 | 0.159555810 | 0.026434414 | -0.111038014 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_0_75_q2tail_joint_centered_d59e2c15.csv | q2tail_joint_centered | 0.750000000 | 0.750000000 | -0.000150576 | -0.000017477 | -0.000167052 | -0.000026636 | 34 | 34 | 0.798649253 | 0.169510001 | 0.019746263 | -0.110649104 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_55_1_00_q2tail_joint_centered_5d16bce4.csv | q2tail_joint_centered | 0.550000000 | 1.000000000 | -0.000140976 | -0.000015473 | -0.000145871 | -0.000026730 | 34 | 34 | 0.795616957 | 0.166106093 | 0.026228388 | -0.110646608 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_q2tail_joint_centered_a8dc3bc0.csv | q2tail_joint_centered | 1.000000000 | 1.000000000 | -0.000150576 | -0.000017477 | -0.000167052 | -0.000026636 | 34 | 34 | 0.795507593 | 0.168843197 | 0.023602305 | -0.110605665 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_25_q2tail_joint_centered_3f213cd9.csv | q2tail_joint_centered | 1.000000000 | 1.250000000 | -0.000150576 | -0.000017477 | -0.000145871 | -0.000026730 | 34 | 34 | 0.790841174 | 0.167852769 | 0.029329818 | -0.110459434 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_55_0_75_q2tail_joint_centered_cdfde8b5.csv | q2tail_joint_centered | 0.550000000 | 0.750000000 | -0.000140976 | -0.000015473 | -0.000167052 | -0.000026636 | 34 | 34 | 0.792039598 | 0.176383173 | 0.019582842 | -0.110208735 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_q2tail_joint_centered_ff3ab56f.csv | q2tail_joint_centered | 0.750000000 | 1.000000000 | -0.000140976 | -0.000015473 | -0.000167052 | -0.000026636 | 34 | 34 | 0.785811821 | 0.178973467 | 0.023314636 | -0.109947128 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_25_q2tail_joint_centered_a99cd587.csv | q2tail_joint_centered | 0.750000000 | 1.250000000 | -0.000140976 | -0.000015473 | -0.000145871 | -0.000026730 | 34 | 34 | 0.781258134 | 0.177936337 | 0.028974413 | -0.109803490 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_25_q2tail_joint_centered_c2d4b149.csv | q2tail_joint_centered | 1.000000000 | 1.250000000 | -0.000140976 | -0.000015473 | -0.000167052 | -0.000026636 | 34 | 34 | 0.775978841 | 0.188516208 | 0.023753782 | -0.109261967 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_0_75_q2tail_joint_centered_f0730b5e.csv | q2tail_joint_centered | 0.750000000 | 0.750000000 | -0.000150576 | -0.000017477 | -0.000145871 | -0.000026730 | 34 | 34 | 0.780974827 | 0.207198347 | 0.000000000 | -0.108462896 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_q2tail_joint_centered_40ec2160.csv | q2tail_joint_centered | 1.000000000 | 1.000000000 | -0.000150576 | -0.000017477 | -0.000145871 | -0.000026730 | 34 | 34 | 0.761372757 | 0.201997774 | 0.025099490 | -0.108123337 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_55_0_75_q2tail_joint_centered_cbc1bc05.csv | q2tail_joint_centered | 0.550000000 | 0.750000000 | -0.000140976 | -0.000015473 | -0.000145871 | -0.000026730 | 34 | 34 | 0.773088907 | 0.215203688 | 0.000000000 | -0.107816735 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_0_75_q2tail_joint_centered_9fda5ff8.csv | q2tail_joint_centered | 1.000000000 | 0.750000000 | -0.000150576 | -0.000017477 | -0.000167052 | -0.000026636 | 34 | 34 | 0.755936330 | 0.213925814 | 0.018690205 | -0.107384107 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_q2tail_joint_centered_c1722f7c.csv | q2tail_joint_centered | 0.750000000 | 1.000000000 | -0.000140976 | -0.000015473 | -0.000145871 | -0.000026730 | 34 | 34 | 0.750297336 | 0.213606031 | 0.024734377 | -0.107166314 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_0_75_q2tail_joint_centered_6cb74efc.csv | q2tail_joint_centered | 0.750000000 | 0.750000000 | -0.000140976 | -0.000015473 | -0.000167052 | -0.000026636 | 34 | 34 | 0.744300649 | 0.226025390 | 0.018402517 | -0.106319133 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_q2tail_joint_centered_0b3db4a7.csv | q2tail_joint_centered | 1.000000000 | 1.000000000 | -0.000140976 | -0.000015473 | -0.000167052 | -0.000026636 | 34 | 34 | 0.741571293 | 0.225196553 | 0.022002042 | -0.106280594 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_25_q2tail_joint_centered_c33ab2f5.csv | q2tail_joint_centered | 1.000000000 | 1.250000000 | -0.000140976 | -0.000015473 | -0.000145871 | -0.000026730 | 34 | 34 | 0.737514586 | 0.223964633 | 0.027352102 | -0.106150836 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_0_75_q2tail_joint_centered_0e96aa10.csv | q2tail_joint_centered | 1.000000000 | 0.750000000 | -0.000150576 | -0.000017477 | -0.000145871 | -0.000026730 | 34 | 34 | 0.730520606 | 0.258416630 | 0.000000000 | -0.103760867 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_0_75_q2tail_joint_centered_fef4e596.csv | q2tail_joint_centered | 0.750000000 | 0.750000000 | -0.000140976 | -0.000015473 | -0.000145871 | -0.000026730 | 34 | 34 | 0.716980929 | 0.272161347 | 0.000000000 | -0.102269799 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_q2tail_joint_centered_eb6b06c2.csv | q2tail_joint_centered | 1.000000000 | 1.000000000 | -0.000140976 | -0.000015473 | -0.000145871 | -0.000026730 | 34 | 34 | 0.700425623 | 0.265877060 | 0.023090301 | -0.101984999 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_0_75_q2tail_joint_centered_5109feae.csv | q2tail_joint_centered | 1.000000000 | 0.750000000 | -0.000140976 | -0.000015473 | -0.000167052 | -0.000026636 | 34 | 34 | 0.692152626 | 0.280252462 | 0.017113180 | -0.100611426 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_0_75_q2tail_joint_centered_2a5773b0.csv | q2tail_joint_centered | 1.000000000 | 0.750000000 | -0.000140976 | -0.000015473 | -0.000145871 | -0.000026730 | 34 | 34 | 0.657346188 | 0.332699178 | 0.000000000 | -0.094601528 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_55_1_25_q2tail_joint_centered_59b106bb.csv | q2tail_joint_centered | 0.550000000 | 1.250000000 | -0.000150576 | -0.000017477 | -0.000194954 | -0.000027022 | 34 | 34 | 0.668279121 | 0.062409371 | 0.259191308 | -0.092158265 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_55_1_00_q2tail_joint_centered_b2e37411.csv | q2tail_joint_centered | 0.550000000 | 1.000000000 | -0.000150576 | -0.000017477 | -0.000194954 | -0.000027022 | 34 | 34 | 0.663751839 | 0.077483221 | 0.248713301 | -0.092024136 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_25_q2tail_joint_centered_ead524dd.csv | q2tail_joint_centered | 0.750000000 | 1.250000000 | -0.000150576 | -0.000017477 | -0.000194954 | -0.000027022 | 34 | 34 | 0.653449531 | 0.083215176 | 0.253439668 | -0.091738961 |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_55_0_75_q2tail_joint_centered_4d2b8c5a.csv | q2tail_joint_centered | 0.550000000 | 0.750000000 | -0.000150576 | -0.000017477 | -0.000194954 | -0.000027022 | 34 | 34 | 0.658233518 | 0.102452051 | 0.229346358 | -0.091713889 |

## Movement-Null Stress

| basename | null_count | actual_mean | actual_p90 | actual_beats_rate | actual_strict_promote | null_mean_best | null_mean_median | null_p90_best | null_p90_median | actual_mean_dominance | actual_p90_dominance | null_strict_promote_rate | mode_count | strict_null_modes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_ed0067a5.csv | 28 | -0.000237599 | -0.000053325 | 0.986111111 | False | -0.000231104 | -0.000053363 | -0.000052852 | 0.000030926 | 1.000000000 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_4ef4890a.csv | 28 | -0.000249075 | -0.000053239 | 0.986111111 | False | -0.000232445 | -0.000071483 | -0.000048937 | 0.000044795 | 1.000000000 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_1aa4c3f2.csv | 28 | -0.000239986 | -0.000052793 | 0.986111111 | False | -0.000230923 | -0.000053268 | -0.000052496 | 0.000035873 | 1.000000000 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_41cdeb7c.csv | 28 | -0.000258375 | -0.000054385 | 0.972222222 | False | -0.000261464 | -0.000096706 | -0.000049297 | 0.000042794 | 0.964285714 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_11959ac7.csv | 28 | -0.000252772 | -0.000053329 | 0.986111111 | False | -0.000280557 | -0.000121374 | -0.000045839 | 0.000022390 | 0.964285714 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_cb597ee7.csv | 28 | -0.000236936 | -0.000053309 | 0.986111111 | False | -0.000237996 | -0.000141505 | -0.000045044 | 0.000020192 | 0.964285714 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_b91f5cab.csv | 28 | -0.000211292 | -0.000051954 | 0.986111111 | False | -0.000247690 | -0.000126681 | -0.000040849 | 0.000034152 | 0.892857143 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_07fbe22a.csv | 28 | -0.000247534 | -0.000054865 | 0.986111111 | False | -0.000243640 | -0.000066594 | -0.000062161 | 0.000036633 | 1.000000000 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_1c9b0ea3.csv | 28 | -0.000210459 | -0.000051912 | 0.986111111 | False | -0.000206856 | -0.000104753 | -0.000053000 | 0.000028783 | 1.000000000 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_15ec9ae3.csv | 28 | -0.000257594 | -0.000054278 | 0.972222222 | False | -0.000268834 | -0.000063424 | -0.000058387 | 0.000037188 | 0.964285714 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_8a33e1f8.csv | 28 | -0.000233638 | -0.000054107 | 0.972222222 | False | -0.000244514 | -0.000120230 | -0.000058703 | 0.000022121 | 0.964285714 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_de2ae5c9.csv | 28 | -0.000258713 | -0.000053786 | 0.972222222 | False | -0.000269501 | -0.000140157 | -0.000064645 | 0.000052433 | 0.964285714 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_9ba63390.csv | 28 | -0.000272306 | -0.000053076 | 0.986111111 | False | -0.000306194 | -0.000034096 | -0.000072779 | 0.000059235 | 0.964285714 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_d8bcd529.csv | 28 | -0.000238719 | -0.000052784 | 0.986111111 | False | -0.000339170 | -0.000159165 | -0.000060737 | 0.000031717 | 0.964285714 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_da20cb9d.csv | 28 | -0.000269100 | -0.000052513 | 0.986111111 | False | -0.000277808 | -0.000111563 | -0.000076005 | 0.000027284 | 0.928571429 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_88c18b2e.csv | 28 | -0.000307774 | -0.000051828 | 0.972222222 | False | -0.000336180 | -0.000211141 | -0.000080054 | 0.000030750 | 0.892857143 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_0d8dccb1.csv | 28 | -0.000250834 | -0.000053785 | 0.986111111 | False | -0.000241624 | -0.000058141 | -0.000060465 | 0.000037983 | 1.000000000 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_58cbcea2.csv | 28 | -0.000234758 | -0.000053532 | 0.972222222 | False | -0.000224091 | -0.000087099 | -0.000062132 | 0.000024234 | 1.000000000 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_b720b161.csv | 28 | -0.000238055 | -0.000052768 | 0.986111111 | False | -0.000229743 | -0.000063376 | -0.000057820 | 0.000034422 | 1.000000000 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_26936bff.csv | 28 | -0.000250349 | -0.000052768 | 0.986111111 | False | -0.000248449 | -0.000078483 | -0.000065090 | 0.000033710 | 1.000000000 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_f66da4f4.csv | 28 | -0.000283025 | -0.000052721 | 0.972222222 | False | -0.000274352 | -0.000155073 | -0.000065754 | 0.000032810 | 1.000000000 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_4b1336bf.csv | 28 | -0.000269882 | -0.000052632 | 0.986111111 | False | -0.000300308 | -0.000039988 | -0.000077187 | 0.000062851 | 0.964285714 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_25_sum_bad_veto_ca759605.csv | 28 | -0.000255886 | -0.000052166 | 0.972222222 | False | -0.000269659 | -0.000151870 | -0.000078116 | 0.000039269 | 0.964285714 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_25_sum_bad_veto_429828db.csv | 28 | -0.000268698 | -0.000051951 | 0.986111111 | False | -0.000279672 | -0.000158318 | -0.000060413 | 0.000041657 | 0.964285714 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_f664f537.csv | 28 | -0.000245112 | -0.000054328 | 0.986111111 | False | -0.000329977 | -0.000071938 | -0.000067967 | 0.000035243 | 0.928571429 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_370e809e.csv | 28 | -0.000251497 | -0.000053799 | 0.986111111 | False | -0.000269439 | -0.000114865 | -0.000064325 | 0.000035412 | 0.928571429 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_3ee22224.csv | 28 | -0.000271524 | -0.000052958 | 0.986111111 | False | -0.000315289 | -0.000211426 | -0.000056731 | 0.000036157 | 0.928571429 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_3a5f943b.csv | 28 | -0.000259494 | -0.000053894 | 0.972222222 | False | -0.000267404 | -0.000070473 | -0.000058435 | 0.000043424 | 0.892857143 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_25_sum_bad_veto_09d26fe3.csv | 28 | -0.000254766 | -0.000052706 | 0.972222222 | False | -0.000269379 | -0.000147750 | -0.000077572 | 0.000032220 | 0.892857143 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_04d63a06.csv | 28 | -0.000248412 | -0.000053225 | 0.986111111 | False | -0.000257891 | -0.000143968 | -0.000060395 | 0.000038983 | 0.928571429 | 0.892857143 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_6fff5452.csv | 28 | -0.000238867 | -0.000053323 | 0.986111111 | False | -0.000231406 | -0.000063556 | -0.000082485 | 0.000047005 | 1.000000000 | 0.857142857 | 0.000000000 | 7 |  |
| submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w1_00_1_00_sum_bad_veto_c53ea5c6.csv | 28 | -0.000279773 | -0.000051948 | 0.972222222 | False | -0.000364855 | -0.000065444 | -0.000074038 | 0.000031543 | 0.964285714 | 0.821428571 | 0.000000000 | 7 |  |

## Decision

Sign-transfer crosses the strict p90 visibility threshold (`-0.000054865`), but remains an information sensor because incremental bad-axis is `0.017961838` above the `0.015` cap.

## Files

- `e342_signtransfer_q2_sources.csv`
- `e342_signtransfer_micro_sources.csv`
- `e342_signtransfer_candidates.csv`
- `e342_signtransfer_scores.csv`
- `e342_signtransfer_anatomy.csv`
- `e342_signtransfer_movement_nulls.csv`
