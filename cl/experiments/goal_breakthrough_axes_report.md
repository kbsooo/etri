# Goal breakthrough axes

All three requested axes are evaluated as v83-anchored centered residual-rank signals, not direct probability submissions.

Axes:
- Axis 1: S1/S3 BCG proxy state decoder from sleep-window, boundary/rest, mechanism, and tiny-AE residual features.
- Axis 2: Q/S two-factor measurement model using subjective Q factors separately from sensor-S/BCG factors.
- Axis 3: same-subject lag/nearest-label transition rule.

Formula: `candidate_t = sigmoid(logit(v83_t) + gamma * rank_center(axis_signal_t))`.

## OOF stress summary

| candidate | delta_mean | delta_worst | move_mean |
| --- | --- | --- | --- |
| axis1_bcg_s1s3_g100_stress | -0.004595 | -0.004336 | 0.016144 |
| axis1_bcg_s1s3_g050 | -0.002530 | -0.002398 | 0.008119 |
| axis1_bcg_s1s3_g030 | -0.001574 | -0.001494 | 0.004882 |
| combo_bcg_lag_core_g030 | -0.001227 | -0.000475 | 0.005364 |
| combo_twofactor_bcg_lag_g030 | -0.001247 | -0.000467 | 0.005495 |
| axis2_twofactor_qs_g050 | -0.001574 | -0.000281 | 0.009176 |
| axis2_twofactor_qs_g030 | -0.001008 | -0.000231 | 0.005515 |
| axis3_lag_all_g030 | -0.000782 | -0.000083 | 0.005301 |
| axis3_lag_core_g030 | -0.000816 | 0.000004 | 0.005272 |
| axis3_lag_core_g050 | -0.001254 | 0.000114 | 0.008777 |
| axis2_twofactor_qonly_g030 | -0.000630 | 0.000611 | 0.005937 |
| axis3_lag_core_g100_stress | -0.001982 | 0.000764 | 0.017496 |

## Target-level OOF details

| candidate | fold_family | target | base_logloss | new_logloss | delta | move |
| --- | --- | --- | --- | --- | --- | --- |
| axis1_bcg_s1s3_g030 | chrono_tail | S1 | 0.534822 | 0.531526 | -0.003296 | 0.004978 |
| axis1_bcg_s1s3_g030 | chrono_tail | S3 | 0.596011 | 0.595908 | -0.000103 | 0.004910 |
| axis1_bcg_s1s3_g030 | hole_v1 | S1 | 0.577664 | 0.574783 | -0.002881 | 0.004594 |
| axis1_bcg_s1s3_g030 | hole_v1 | S3 | 0.530375 | 0.530199 | -0.000176 | 0.005144 |
| axis1_bcg_s1s3_g030 | mirror_v1 | S1 | 0.565440 | 0.563144 | -0.002295 | 0.004675 |
| axis1_bcg_s1s3_g030 | mirror_v1 | S3 | 0.575662 | 0.574969 | -0.000693 | 0.004992 |
| axis1_bcg_s1s3_g050 | chrono_tail | S1 | 0.534822 | 0.529425 | -0.005397 | 0.008287 |
| axis1_bcg_s1s3_g050 | chrono_tail | S3 | 0.596011 | 0.595932 | -0.000079 | 0.008157 |
| axis1_bcg_s1s3_g050 | hole_v1 | S1 | 0.577664 | 0.572951 | -0.004714 | 0.007642 |
| axis1_bcg_s1s3_g050 | hole_v1 | S3 | 0.530375 | 0.530181 | -0.000194 | 0.008550 |
| axis1_bcg_s1s3_g050 | mirror_v1 | S1 | 0.565440 | 0.561704 | -0.003735 | 0.007780 |
| axis1_bcg_s1s3_g050 | mirror_v1 | S3 | 0.575662 | 0.574602 | -0.001060 | 0.008296 |
| axis1_bcg_s1s3_g100_stress | chrono_tail | S1 | 0.534822 | 0.524507 | -0.010315 | 0.016523 |
| axis1_bcg_s1s3_g100_stress | chrono_tail | S3 | 0.596011 | 0.596312 | 0.000301 | 0.016182 |
| axis1_bcg_s1s3_g100_stress | hole_v1 | S1 | 0.577664 | 0.568676 | -0.008988 | 0.015211 |
| axis1_bcg_s1s3_g100_stress | hole_v1 | S3 | 0.530375 | 0.530475 | 0.000100 | 0.016985 |
| axis1_bcg_s1s3_g100_stress | mirror_v1 | S1 | 0.565440 | 0.558415 | -0.007025 | 0.015493 |
| axis1_bcg_s1s3_g100_stress | mirror_v1 | S3 | 0.575662 | 0.574015 | -0.001647 | 0.016471 |
| axis2_twofactor_qonly_g030 | chrono_tail | Q1 | 0.670467 | 0.668836 | -0.001631 | 0.006208 |
| axis2_twofactor_qonly_g030 | chrono_tail | Q2 | 0.673651 | 0.673073 | -0.000578 | 0.006162 |
| axis2_twofactor_qonly_g030 | chrono_tail | Q3 | 0.671906 | 0.671863 | -0.000043 | 0.005583 |
| axis2_twofactor_qonly_g030 | hole_v1 | Q1 | 0.686252 | 0.684698 | -0.001554 | 0.006191 |
| axis2_twofactor_qonly_g030 | hole_v1 | Q2 | 0.674212 | 0.671887 | -0.002325 | 0.006117 |
| axis2_twofactor_qonly_g030 | hole_v1 | Q3 | 0.650345 | 0.648976 | -0.001370 | 0.005622 |
| axis2_twofactor_qonly_g030 | mirror_v1 | Q1 | 0.685953 | 0.685546 | -0.000407 | 0.006126 |
| axis2_twofactor_qonly_g030 | mirror_v1 | Q2 | 0.705909 | 0.707377 | 0.001468 | 0.006049 |
| axis2_twofactor_qonly_g030 | mirror_v1 | Q3 | 0.691838 | 0.692610 | 0.000771 | 0.005372 |
| axis2_twofactor_qs_g030 | chrono_tail | Q1 | 0.670467 | 0.668836 | -0.001631 | 0.006208 |
| axis2_twofactor_qs_g030 | chrono_tail | Q2 | 0.673651 | 0.673073 | -0.000578 | 0.006162 |
| axis2_twofactor_qs_g030 | chrono_tail | Q3 | 0.671906 | 0.671863 | -0.000043 | 0.005583 |
| axis2_twofactor_qs_g030 | chrono_tail | S1 | 0.534822 | 0.531526 | -0.003296 | 0.004978 |
| axis2_twofactor_qs_g030 | chrono_tail | S3 | 0.596011 | 0.595908 | -0.000103 | 0.004910 |
| axis2_twofactor_qs_g030 | hole_v1 | Q1 | 0.686252 | 0.684698 | -0.001554 | 0.006191 |
| axis2_twofactor_qs_g030 | hole_v1 | Q2 | 0.674212 | 0.671887 | -0.002325 | 0.006117 |
| axis2_twofactor_qs_g030 | hole_v1 | Q3 | 0.650345 | 0.648976 | -0.001370 | 0.005622 |
| axis2_twofactor_qs_g030 | hole_v1 | S1 | 0.577664 | 0.574783 | -0.002881 | 0.004594 |
| axis2_twofactor_qs_g030 | hole_v1 | S3 | 0.530375 | 0.530199 | -0.000176 | 0.005144 |
| axis2_twofactor_qs_g030 | mirror_v1 | Q1 | 0.685953 | 0.685546 | -0.000407 | 0.006126 |
| axis2_twofactor_qs_g030 | mirror_v1 | Q2 | 0.705909 | 0.707377 | 0.001468 | 0.006049 |
| axis2_twofactor_qs_g030 | mirror_v1 | Q3 | 0.691838 | 0.692610 | 0.000771 | 0.005372 |
| axis2_twofactor_qs_g030 | mirror_v1 | S1 | 0.565440 | 0.563144 | -0.002295 | 0.004675 |
| axis2_twofactor_qs_g030 | mirror_v1 | S3 | 0.575662 | 0.574969 | -0.000693 | 0.004992 |
| axis2_twofactor_qs_g050 | chrono_tail | Q1 | 0.670467 | 0.667868 | -0.002600 | 0.010338 |
| axis2_twofactor_qs_g050 | chrono_tail | Q2 | 0.673651 | 0.672806 | -0.000845 | 0.010259 |
| axis2_twofactor_qs_g050 | chrono_tail | Q3 | 0.671906 | 0.671941 | 0.000035 | 0.009287 |
| axis2_twofactor_qs_g050 | chrono_tail | S1 | 0.534822 | 0.529425 | -0.005397 | 0.008287 |
| axis2_twofactor_qs_g050 | chrono_tail | S3 | 0.596011 | 0.595932 | -0.000079 | 0.008157 |
| axis2_twofactor_qs_g050 | hole_v1 | Q1 | 0.686252 | 0.683780 | -0.002472 | 0.010308 |
| axis2_twofactor_qs_g050 | hole_v1 | Q2 | 0.674212 | 0.670455 | -0.003757 | 0.010187 |
| axis2_twofactor_qs_g050 | hole_v1 | Q3 | 0.650345 | 0.648170 | -0.002175 | 0.009357 |
| axis2_twofactor_qs_g050 | hole_v1 | S1 | 0.577664 | 0.572951 | -0.004714 | 0.007642 |
| axis2_twofactor_qs_g050 | hole_v1 | S3 | 0.530375 | 0.530181 | -0.000194 | 0.008550 |
| axis2_twofactor_qs_g050 | mirror_v1 | Q1 | 0.685953 | 0.685392 | -0.000561 | 0.010197 |
| axis2_twofactor_qs_g050 | mirror_v1 | Q2 | 0.705909 | 0.708471 | 0.002562 | 0.010064 |
| axis2_twofactor_qs_g050 | mirror_v1 | Q3 | 0.691838 | 0.693226 | 0.001388 | 0.008931 |
| axis2_twofactor_qs_g050 | mirror_v1 | S1 | 0.565440 | 0.561704 | -0.003735 | 0.007780 |
| axis2_twofactor_qs_g050 | mirror_v1 | S3 | 0.575662 | 0.574602 | -0.001060 | 0.008296 |
| axis3_lag_all_g030 | chrono_tail | Q1 | 0.670467 | 0.671171 | 0.000704 | 0.005537 |
| axis3_lag_all_g030 | chrono_tail | Q2 | 0.673651 | 0.672761 | -0.000890 | 0.005142 |
| axis3_lag_all_g030 | chrono_tail | Q3 | 0.671906 | 0.672702 | 0.000796 | 0.005162 |
| axis3_lag_all_g030 | chrono_tail | S1 | 0.534822 | 0.534618 | -0.000204 | 0.004078 |
| axis3_lag_all_g030 | chrono_tail | S2 | 0.663445 | 0.662770 | -0.000675 | 0.004702 |
| axis3_lag_all_g030 | chrono_tail | S3 | 0.596011 | 0.595623 | -0.000388 | 0.004616 |
| axis3_lag_all_g030 | chrono_tail | S4 | 0.655181 | 0.655253 | 0.000072 | 0.005768 |
| axis3_lag_all_g030 | hole_v1 | Q1 | 0.686252 | 0.684383 | -0.001869 | 0.006176 |
| axis3_lag_all_g030 | hole_v1 | Q2 | 0.674212 | 0.669901 | -0.004310 | 0.006143 |
| axis3_lag_all_g030 | hole_v1 | Q3 | 0.650345 | 0.648387 | -0.001958 | 0.005656 |
| axis3_lag_all_g030 | hole_v1 | S1 | 0.577664 | 0.577653 | -0.000012 | 0.004552 |
| axis3_lag_all_g030 | hole_v1 | S2 | 0.569914 | 0.568746 | -0.001169 | 0.004852 |
| axis3_lag_all_g030 | hole_v1 | S3 | 0.530375 | 0.529176 | -0.001199 | 0.004971 |
| axis3_lag_all_g030 | hole_v1 | S4 | 0.646873 | 0.646783 | -0.000091 | 0.005971 |
| axis3_lag_all_g030 | mirror_v1 | Q1 | 0.685953 | 0.685658 | -0.000295 | 0.006096 |
| axis3_lag_all_g030 | mirror_v1 | Q2 | 0.705909 | 0.703809 | -0.002100 | 0.006029 |
| axis3_lag_all_g030 | mirror_v1 | Q3 | 0.691838 | 0.691949 | 0.000111 | 0.005411 |
| axis3_lag_all_g030 | mirror_v1 | S1 | 0.565440 | 0.565217 | -0.000222 | 0.004660 |
| axis3_lag_all_g030 | mirror_v1 | S2 | 0.593937 | 0.592842 | -0.001095 | 0.004889 |
| axis3_lag_all_g030 | mirror_v1 | S3 | 0.575662 | 0.575261 | -0.000401 | 0.004859 |
| axis3_lag_all_g030 | mirror_v1 | S4 | 0.643229 | 0.642004 | -0.001225 | 0.006049 |
| axis3_lag_core_g030 | chrono_tail | Q1 | 0.670467 | 0.671171 | 0.000704 | 0.005537 |
| axis3_lag_core_g030 | chrono_tail | Q2 | 0.673651 | 0.672761 | -0.000890 | 0.005142 |
| axis3_lag_core_g030 | chrono_tail | Q3 | 0.671906 | 0.672702 | 0.000796 | 0.005162 |
| axis3_lag_core_g030 | chrono_tail | S1 | 0.534822 | 0.534618 | -0.000204 | 0.004078 |
| axis3_lag_core_g030 | chrono_tail | S3 | 0.596011 | 0.595623 | -0.000388 | 0.004616 |
| axis3_lag_core_g030 | hole_v1 | Q1 | 0.686252 | 0.684383 | -0.001869 | 0.006176 |
| axis3_lag_core_g030 | hole_v1 | Q2 | 0.674212 | 0.669901 | -0.004310 | 0.006143 |
| axis3_lag_core_g030 | hole_v1 | Q3 | 0.650345 | 0.648387 | -0.001958 | 0.005656 |
| axis3_lag_core_g030 | hole_v1 | S1 | 0.577664 | 0.577653 | -0.000012 | 0.004552 |
| axis3_lag_core_g030 | hole_v1 | S3 | 0.530375 | 0.529176 | -0.001199 | 0.004971 |
| axis3_lag_core_g030 | mirror_v1 | Q1 | 0.685953 | 0.685658 | -0.000295 | 0.006096 |
| axis3_lag_core_g030 | mirror_v1 | Q2 | 0.705909 | 0.703809 | -0.002100 | 0.006029 |
| axis3_lag_core_g030 | mirror_v1 | Q3 | 0.691838 | 0.691949 | 0.000111 | 0.005411 |
| axis3_lag_core_g030 | mirror_v1 | S1 | 0.565440 | 0.565217 | -0.000222 | 0.004660 |
| axis3_lag_core_g030 | mirror_v1 | S3 | 0.575662 | 0.575261 | -0.000401 | 0.004859 |
| axis3_lag_core_g050 | chrono_tail | Q1 | 0.670467 | 0.671759 | 0.001292 | 0.009213 |
| axis3_lag_core_g050 | chrono_tail | Q2 | 0.673651 | 0.672287 | -0.001364 | 0.008559 |
| axis3_lag_core_g050 | chrono_tail | Q3 | 0.671906 | 0.673342 | 0.001436 | 0.008585 |
| axis3_lag_core_g050 | chrono_tail | S1 | 0.534822 | 0.534577 | -0.000244 | 0.006792 |
| axis3_lag_core_g050 | chrono_tail | S3 | 0.596011 | 0.595461 | -0.000550 | 0.007676 |
| axis3_lag_core_g050 | hole_v1 | Q1 | 0.686252 | 0.683255 | -0.002997 | 0.010290 |
| axis3_lag_core_g050 | hole_v1 | Q2 | 0.674212 | 0.667146 | -0.007066 | 0.010234 |
| axis3_lag_core_g050 | hole_v1 | Q3 | 0.650345 | 0.647191 | -0.003154 | 0.009414 |
| axis3_lag_core_g050 | hole_v1 | S1 | 0.577664 | 0.577731 | 0.000067 | 0.007580 |
| axis3_lag_core_g050 | hole_v1 | S3 | 0.530375 | 0.528470 | -0.001905 | 0.008271 |
| axis3_lag_core_g050 | mirror_v1 | Q1 | 0.685953 | 0.685579 | -0.000374 | 0.010151 |
| axis3_lag_core_g050 | mirror_v1 | Q2 | 0.705909 | 0.702525 | -0.003384 | 0.010043 |
| axis3_lag_core_g050 | mirror_v1 | Q3 | 0.691838 | 0.692127 | 0.000288 | 0.009001 |
| axis3_lag_core_g050 | mirror_v1 | S1 | 0.565440 | 0.565158 | -0.000281 | 0.007760 |
| axis3_lag_core_g050 | mirror_v1 | S3 | 0.575662 | 0.575087 | -0.000575 | 0.008084 |
| axis3_lag_core_g100_stress | chrono_tail | Q1 | 0.670467 | 0.673641 | 0.003174 | 0.018339 |
| axis3_lag_core_g100_stress | chrono_tail | Q2 | 0.673651 | 0.671517 | -0.002133 | 0.017052 |
| axis3_lag_core_g100_stress | chrono_tail | Q3 | 0.671906 | 0.675317 | 0.003411 | 0.017076 |
| axis3_lag_core_g100_stress | chrono_tail | S1 | 0.534822 | 0.534809 | -0.000013 | 0.013556 |
| axis3_lag_core_g100_stress | chrono_tail | S3 | 0.596011 | 0.595391 | -0.000620 | 0.015263 |
| axis3_lag_core_g100_stress | hole_v1 | Q1 | 0.686252 | 0.680853 | -0.005399 | 0.020557 |
| axis3_lag_core_g100_stress | hole_v1 | Q2 | 0.674212 | 0.660670 | -0.013542 | 0.020440 |
| axis3_lag_core_g100_stress | hole_v1 | Q3 | 0.650345 | 0.644580 | -0.005765 | 0.018758 |
| axis3_lag_core_g100_stress | hole_v1 | S1 | 0.577664 | 0.578227 | 0.000563 | 0.015131 |
| axis3_lag_core_g100_stress | hole_v1 | S3 | 0.530375 | 0.527030 | -0.003345 | 0.016467 |
| axis3_lag_core_g100_stress | mirror_v1 | Q1 | 0.685953 | 0.685791 | -0.000162 | 0.020251 |
| axis3_lag_core_g100_stress | mirror_v1 | Q2 | 0.705909 | 0.699724 | -0.006185 | 0.020056 |
| axis3_lag_core_g100_stress | mirror_v1 | Q3 | 0.691838 | 0.692928 | 0.001090 | 0.017907 |
| axis3_lag_core_g100_stress | mirror_v1 | S1 | 0.565440 | 0.565322 | -0.000117 | 0.015485 |
| axis3_lag_core_g100_stress | mirror_v1 | S3 | 0.575662 | 0.574978 | -0.000684 | 0.016098 |
| combo_bcg_lag_core_g030 | chrono_tail | Q1 | 0.670467 | 0.671171 | 0.000704 | 0.005537 |
| combo_bcg_lag_core_g030 | chrono_tail | Q2 | 0.673651 | 0.672761 | -0.000890 | 0.005142 |
| combo_bcg_lag_core_g030 | chrono_tail | Q3 | 0.671906 | 0.672702 | 0.000796 | 0.005162 |
| combo_bcg_lag_core_g030 | chrono_tail | S1 | 0.534822 | 0.531999 | -0.002822 | 0.004960 |
| combo_bcg_lag_core_g030 | chrono_tail | S3 | 0.596011 | 0.595846 | -0.000165 | 0.004935 |
| combo_bcg_lag_core_g030 | hole_v1 | Q1 | 0.686252 | 0.684383 | -0.001869 | 0.006176 |
| combo_bcg_lag_core_g030 | hole_v1 | Q2 | 0.674212 | 0.669901 | -0.004310 | 0.006143 |
| combo_bcg_lag_core_g030 | hole_v1 | Q3 | 0.650345 | 0.648387 | -0.001958 | 0.005656 |
| combo_bcg_lag_core_g030 | hole_v1 | S1 | 0.577664 | 0.575469 | -0.002196 | 0.004585 |
| combo_bcg_lag_core_g030 | hole_v1 | S3 | 0.530375 | 0.529563 | -0.000812 | 0.005050 |
| combo_bcg_lag_core_g030 | mirror_v1 | Q1 | 0.685953 | 0.685658 | -0.000295 | 0.006096 |
| combo_bcg_lag_core_g030 | mirror_v1 | Q2 | 0.705909 | 0.703809 | -0.002100 | 0.006029 |
| combo_bcg_lag_core_g030 | mirror_v1 | Q3 | 0.691838 | 0.691949 | 0.000111 | 0.005411 |
| combo_bcg_lag_core_g030 | mirror_v1 | S1 | 0.565440 | 0.563558 | -0.001881 | 0.004650 |
| combo_bcg_lag_core_g030 | mirror_v1 | S3 | 0.575662 | 0.574941 | -0.000721 | 0.004927 |
| combo_twofactor_bcg_lag_g030 | chrono_tail | Q1 | 0.670467 | 0.669585 | -0.000882 | 0.006196 |
| combo_twofactor_bcg_lag_g030 | chrono_tail | Q2 | 0.673651 | 0.672761 | -0.000890 | 0.006169 |
| combo_twofactor_bcg_lag_g030 | chrono_tail | Q3 | 0.671906 | 0.672169 | 0.000263 | 0.005540 |
| combo_twofactor_bcg_lag_g030 | chrono_tail | S1 | 0.534822 | 0.531999 | -0.002822 | 0.004960 |
| combo_twofactor_bcg_lag_g030 | chrono_tail | S3 | 0.596011 | 0.595846 | -0.000165 | 0.004935 |
| combo_twofactor_bcg_lag_g030 | hole_v1 | Q1 | 0.686252 | 0.683866 | -0.002386 | 0.006181 |
| combo_twofactor_bcg_lag_g030 | hole_v1 | Q2 | 0.674212 | 0.670068 | -0.004143 | 0.006081 |
| combo_twofactor_bcg_lag_g030 | hole_v1 | Q3 | 0.650345 | 0.648004 | -0.002341 | 0.005633 |
| combo_twofactor_bcg_lag_g030 | hole_v1 | S1 | 0.577664 | 0.575469 | -0.002196 | 0.004585 |
| combo_twofactor_bcg_lag_g030 | hole_v1 | S3 | 0.530375 | 0.529563 | -0.000812 | 0.005050 |
| combo_twofactor_bcg_lag_g030 | mirror_v1 | Q1 | 0.685953 | 0.685473 | -0.000480 | 0.006085 |
| combo_twofactor_bcg_lag_g030 | mirror_v1 | Q2 | 0.705909 | 0.706019 | 0.000110 | 0.006051 |
| combo_twofactor_bcg_lag_g030 | mirror_v1 | Q3 | 0.691838 | 0.692475 | 0.000637 | 0.005378 |
| combo_twofactor_bcg_lag_g030 | mirror_v1 | S1 | 0.565440 | 0.563558 | -0.001881 | 0.004650 |
| combo_twofactor_bcg_lag_g030 | mirror_v1 | S3 | 0.575662 | 0.574941 | -0.000721 | 0.004927 |

## Candidate files

| candidate | file | gamma | mean_abs_move_v83 | max_abs_move_v83 | dmean_Q1 | dmean_Q2 | dmean_Q3 | dmean_S1 | dmean_S2 | dmean_S3 | dmean_S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| axis1_bcg_s1s3_g030 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_goal_breakthrough_axis1_bcg_s1s3_g030_prob.csv | 0.030000 | 0.001380 | 0.012776 | 0.000000 | 0.000000 | 0.000000 | -0.000747 | 0.000000 | -0.000842 | 0.000000 |
| axis1_bcg_s1s3_g050 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_goal_breakthrough_axis1_bcg_s1s3_g050_prob.csv | 0.050000 | 0.002294 | 0.021249 | 0.000000 | 0.000000 | 0.000000 | -0.001269 | 0.000000 | -0.001417 | 0.000000 |
| axis2_twofactor_qonly_g030 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_goal_breakthrough_axis2_twofactor_qonly_g030_prob.csv | 0.030000 | 0.002463 | 0.012895 | -0.000044 | -0.000181 | -0.000168 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| axis3_lag_core_g030 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_goal_breakthrough_axis3_lag_core_g030_prob.csv | 0.030000 | 0.003685 | 0.012965 | -0.000174 | -0.000371 | -0.000149 | -0.000752 | 0.000000 | -0.000634 | 0.000000 |
| combo_bcg_lag_core_g030 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_goal_breakthrough_combo_bcg_lag_core_g030_prob.csv | 0.030000 | 0.003701 | 0.012965 | -0.000174 | -0.000371 | -0.000149 | -0.000970 | 0.000000 | -0.000998 | 0.000000 |
| combo_twofactor_bcg_lag_g030 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_goal_breakthrough_combo_twofactor_bcg_lag_g030_prob.csv | 0.030000 | 0.003804 | 0.012870 | -0.000122 | -0.000324 | -0.000199 | -0.000970 | 0.000000 | -0.000998 | 0.000000 |
| axis2_twofactor_qs_g030 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_goal_breakthrough_axis2_twofactor_qs_g030_prob.csv | 0.030000 | 0.003843 | 0.012895 | -0.000044 | -0.000181 | -0.000168 | -0.000747 | 0.000000 | -0.000842 | 0.000000 |
| axis1_bcg_s1s3_g100_stress | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_goal_breakthrough_axis1_bcg_s1s3_g100_stress_prob.csv | 0.100000 | 0.004563 | 0.042414 | 0.000000 | 0.000000 | 0.000000 | -0.002652 | 0.000000 | -0.002901 | 0.000000 |
| axis3_lag_all_g030 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_goal_breakthrough_axis3_lag_all_g030_prob.csv | 0.030000 | 0.005119 | 0.012965 | -0.000174 | -0.000371 | -0.000149 | -0.000752 | -0.001073 | -0.000634 | -0.000207 |
| axis3_lag_core_g050 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_goal_breakthrough_axis3_lag_core_g050_prob.csv | 0.050000 | 0.006130 | 0.021581 | -0.000287 | -0.000627 | -0.000264 | -0.001274 | 0.000000 | -0.001074 | 0.000000 |
| axis2_twofactor_qs_g050 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_goal_breakthrough_axis2_twofactor_qs_g050_prob.csv | 0.050000 | 0.006396 | 0.021509 | -0.000077 | -0.000316 | -0.000299 | -0.001269 | 0.000000 | -0.001417 | 0.000000 |
| axis3_lag_core_g100_stress | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_goal_breakthrough_axis3_lag_core_g100_stress_prob.csv | 0.100000 | 0.012200 | 0.042985 | -0.000560 | -0.001294 | -0.000608 | -0.002653 | 0.000000 | -0.002234 | 0.000000 |

## Public-posterior diagnostics

| posterior | candidate | posterior_bce | vs_v83 |
| --- | --- | --- | --- |
| old_public_anchor | axis2_twofactor_qs_g050 | 0.597671 | -0.000143 |
| old_public_anchor | axis2_twofactor_qonly_g030 | 0.597676 | -0.000137 |
| old_public_anchor | axis2_twofactor_qs_g030 | 0.597684 | -0.000130 |
| old_public_anchor | combo_twofactor_bcg_lag_g030 | 0.597741 | -0.000072 |
| old_public_anchor | v83_base | 0.597813 | 0.000000 |
| old_public_anchor | axis1_bcg_s1s3_g030 | 0.597821 | 0.000008 |
| old_public_anchor | axis1_bcg_s1s3_g050 | 0.597852 | 0.000039 |
| old_public_anchor | combo_bcg_lag_core_g030 | 0.597863 | 0.000049 |
| old_public_anchor | axis3_lag_core_g030 | 0.597901 | 0.000088 |
| old_public_anchor | axis3_lag_all_g030 | 0.597910 | 0.000097 |
| old_public_anchor | axis1_bcg_s1s3_g100_stress | 0.598022 | 0.000209 |
| old_public_anchor | axis3_lag_core_g050 | 0.598031 | 0.000218 |
| old_public_anchor | axis3_lag_core_g100_stress | 0.598608 | 0.000795 |
| refit_public_anchor | axis2_twofactor_qs_g050 | 0.599265 | -0.000500 |
| refit_public_anchor | axis2_twofactor_qs_g030 | 0.599421 | -0.000344 |
| refit_public_anchor | axis2_twofactor_qonly_g030 | 0.599496 | -0.000268 |
| refit_public_anchor | combo_twofactor_bcg_lag_g030 | 0.599546 | -0.000218 |
| refit_public_anchor | axis1_bcg_s1s3_g050 | 0.599665 | -0.000100 |
| refit_public_anchor | axis1_bcg_s1s3_g030 | 0.599689 | -0.000076 |
| refit_public_anchor | axis1_bcg_s1s3_g100_stress | 0.599695 | -0.000069 |
| refit_public_anchor | combo_bcg_lag_core_g030 | 0.599730 | -0.000034 |
| refit_public_anchor | v83_base | 0.599765 | 0.000000 |
| refit_public_anchor | axis3_lag_core_g030 | 0.599879 | 0.000115 |
| refit_public_anchor | axis3_lag_all_g030 | 0.599899 | 0.000135 |
| refit_public_anchor | axis3_lag_core_g050 | 0.600028 | 0.000263 |
| refit_public_anchor | axis3_lag_core_g100_stress | 0.600650 | 0.000885 |

Decision rule: carry forward candidates that improve every fold-family, stay close to v83, and avoid broad target mean drift.
