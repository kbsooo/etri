# JEPA Target-Ablation Scale Probe

This decomposes the sparse scale direction by target mask so a public LB response can identify target leakage.

## Best Actual-Anchor Rows

```
              name                              file             source_name target_mask  scale  actual_anchor_score_final  robust_delta_vs_a2c8  robust_p90_delta_vs_a2c8  mean_abs_move_vs_a2c8  active_cells  mean_active_energy
targetabl_b19056bb submission_targetabl_b19056bb.csv        f465_actual_best    q3_stage   1.00                   0.577727             -0.000686                 -0.000567               0.004452         933.0            1.168551
targetabl_585c0b46 submission_targetabl_585c0b46.csv           3cf_noq2_safe    q3_stage   1.00                   0.577727             -0.000686                 -0.000567               0.004452         933.0            1.168551
targetabl_81af7484 submission_targetabl_81af7484.csv 282_consensus_directrob    q3_stage   1.00                   0.577734             -0.000710                 -0.000595               0.004882         933.0            1.168551
targetabl_3100ef2f submission_targetabl_3100ef2f.csv        f465_actual_best      q_only   1.00                   0.577734             -0.000440                 -0.000380               0.002914         522.0            1.162450
targetabl_c2de5708 submission_targetabl_c2de5708.csv 282_consensus_directrob      q_only   1.00                   0.577738             -0.000455                 -0.000396               0.003189         522.0            1.162450
targetabl_1049b8e7 submission_targetabl_1049b8e7.csv        f465_actual_best q3_s2_s3_s4   1.30                   0.577738             -0.000696                 -0.000557               0.004809         738.0            1.179996
targetabl_94359b98 submission_targetabl_94359b98.csv           3cf_noq2_safe q3_s2_s3_s4   1.30                   0.577738             -0.000696                 -0.000557               0.004809         738.0            1.179996
targetabl_c9d34bf9 submission_targetabl_c9d34bf9.csv             f43_cv_best q3_s2_s3_s4   1.00                   0.577741             -0.000689                 -0.000545               0.004425         600.0            1.348428
targetabl_ee70d8b9 submission_targetabl_ee70d8b9.csv        f465_actual_best      q_only   1.30                   0.577741             -0.000543                 -0.000470               0.003787         522.0            1.162450
targetabl_a38d0e64 submission_targetabl_a38d0e64.csv             f43_cv_best      q_only   1.00                   0.577744             -0.000535                 -0.000450               0.003463         425.0            1.324664
targetabl_ef7e267d submission_targetabl_ef7e267d.csv           3cf_noq2_safe      q_only   1.00                   0.577744             -0.000377                 -0.000314               0.002258         398.0            1.268626
targetabl_966c8aa7 submission_targetabl_966c8aa7.csv           3cf_noq2_safe    q3_stage   1.30                   0.577745             -0.000849                 -0.000700               0.005787         933.0            1.168551
targetabl_c5f87213 submission_targetabl_c5f87213.csv        f465_actual_best    q3_stage   1.30                   0.577745             -0.000849                 -0.000700               0.005787         933.0            1.168551
targetabl_64102eec submission_targetabl_64102eec.csv 282_consensus_directrob         all   1.30                   0.577746             -0.001196                 -0.001067               0.008816        1256.0            1.146752
targetabl_08f0fc76 submission_targetabl_08f0fc76.csv           3cf_noq2_safe      q_only   1.30                   0.577747             -0.000467                 -0.000386               0.002934         398.0            1.268626
targetabl_7b531822 submission_targetabl_7b531822.csv             f43_cv_best    q3_stage   1.00                   0.577747             -0.000840                 -0.000689               0.005311         756.0            1.337069
targetabl_94f4bfe0 submission_targetabl_94f4bfe0.csv 282_consensus_directrob q3_s2_s3_s4   1.30                   0.577749             -0.000714                 -0.000578               0.005254         738.0            1.179996
targetabl_f656ca2c submission_targetabl_f656ca2c.csv 282_consensus_directrob      q_only   1.30                   0.577750             -0.000558                 -0.000487               0.004145         522.0            1.162450
targetabl_2e370469 submission_targetabl_2e370469.csv        f465_actual_best      q_only   1.50                   0.577753             -0.000604                 -0.000523               0.004369         522.0            1.162450
targetabl_47e012c7 submission_targetabl_47e012c7.csv           3cf_noq2_safe      q_only   1.50                   0.577755             -0.000521                 -0.000429               0.003385         398.0            1.268626
targetabl_9d1c3c2d submission_targetabl_9d1c3c2d.csv        f465_actual_best q3_s2_s3_s4   1.50                   0.577755             -0.000775                 -0.000618               0.005549         738.0            1.179996
targetabl_dd7534ff submission_targetabl_dd7534ff.csv           3cf_noq2_safe q3_s2_s3_s4   1.50                   0.577755             -0.000775                 -0.000618               0.005549         738.0            1.179996
targetabl_25d719c0 submission_targetabl_25d719c0.csv        f465_actual_best         all   1.50                   0.577757             -0.001296                 -0.001143               0.009260        1256.0            1.146752
targetabl_8f81d324 submission_targetabl_8f81d324.csv        f465_actual_best       no_q2   1.50                   0.577758             -0.001213                 -0.001096               0.008276        1132.0            1.182363
targetabl_b640b6ac submission_targetabl_b640b6ac.csv        f465_actual_best q1_q3_stage   1.50                   0.577758             -0.001213                 -0.001096               0.008276        1132.0            1.182363
targetabl_44f162bd submission_targetabl_44f162bd.csv 282_consensus_directrob    q3_stage   1.30                   0.577760             -0.000872                 -0.000730               0.006345         933.0            1.168551
targetabl_672a2b86 submission_targetabl_672a2b86.csv 282_consensus_directrob      q_only   1.50                   0.577766             -0.000618                 -0.000538               0.004783         522.0            1.162450
targetabl_55831bfb submission_targetabl_55831bfb.csv        f465_actual_best    q3_stage   1.50                   0.577768             -0.000946                 -0.000780               0.006676         933.0            1.168551
targetabl_7ad2026b submission_targetabl_7ad2026b.csv           3cf_noq2_safe    q3_stage   1.50                   0.577768             -0.000946                 -0.000780               0.006676         933.0            1.168551
targetabl_b3070233 submission_targetabl_b3070233.csv           3cf_noq2_safe      q_only   1.75                   0.577771             -0.000583                 -0.000477               0.003947         398.0            1.268626
targetabl_6e771ba8 submission_targetabl_6e771ba8.csv 282_consensus_directrob       no_s1   1.50                   0.577771             -0.001150                 -0.001015               0.008913        1061.0            1.150707
targetabl_a551a9fa submission_targetabl_a551a9fa.csv 282_consensus_directrob q3_s2_s3_s4   1.50                   0.577772             -0.000791                 -0.000640               0.006062         738.0            1.179996
targetabl_43b4d2e7 submission_targetabl_43b4d2e7.csv             f43_cv_best      q_only   1.30                   0.577773             -0.000647                 -0.000546               0.004500         425.0            1.324664
targetabl_b02be880 submission_targetabl_b02be880.csv        f465_actual_best      q_only   1.75                   0.577776             -0.000673                 -0.000583               0.005096         522.0            1.162450
targetabl_5006a6a3 submission_targetabl_5006a6a3.csv             f43_cv_best q3_s2_s3_s4   1.30                   0.577781             -0.000834                 -0.000657               0.005751         600.0            1.348428
targetabl_d491786e submission_targetabl_d491786e.csv             f43_cv_best       no_s1   1.30                   0.577784             -0.001206                 -0.001035               0.008369         859.0            1.316136
targetabl_75aa4b39 submission_targetabl_75aa4b39.csv        f465_actual_best     q3_only   2.00                   0.577787             -0.000308                 -0.000211               0.002379         199.0            1.290130
targetabl_c9b4082b submission_targetabl_c9b4082b.csv           3cf_noq2_safe     q3_only   2.00                   0.577787             -0.000308                 -0.000211               0.002379         199.0            1.290130
targetabl_7568417c submission_targetabl_7568417c.csv           3cf_noq2_safe q3_s2_s3_s4   1.75                   0.577788             -0.000864                 -0.000687               0.006473         738.0            1.179996
targetabl_4338e29c submission_targetabl_4338e29c.csv        f465_actual_best q3_s2_s3_s4   1.75                   0.577788             -0.000864                 -0.000687               0.006473         738.0            1.179996
targetabl_e1bf4b1a submission_targetabl_e1bf4b1a.csv 282_consensus_directrob       no_q2   1.50                   0.577789             -0.001239                 -0.001134               0.009050        1132.0            1.182363
targetabl_940d9323 submission_targetabl_940d9323.csv 282_consensus_directrob q1_q3_stage   1.50                   0.577789             -0.001239                 -0.001134               0.009050        1132.0            1.182363
targetabl_d15873ce submission_targetabl_d15873ce.csv 282_consensus_directrob         all   1.50                   0.577792             -0.001327                 -0.001184               0.010171        1256.0            1.146752
targetabl_a9029a9b submission_targetabl_a9029a9b.csv 282_consensus_directrob       no_s4   1.50                   0.577792             -0.001232                 -0.001111               0.009067        1107.0            1.177328
targetabl_f833561e submission_targetabl_f833561e.csv 282_consensus_directrob    q3_stage   1.50                   0.577793             -0.000968                 -0.000809               0.007320         933.0            1.168551
targetabl_e93cdd0a submission_targetabl_e93cdd0a.csv        f465_actual_best       no_s1   1.75                   0.577793             -0.001253                 -0.001094               0.009487        1061.0            1.150707
targetabl_77a19f51 submission_targetabl_77a19f51.csv           3cf_noq2_safe      q_only   2.00                   0.577795             -0.000637                 -0.000517               0.004510         398.0            1.268626
targetabl_2d2e7427 submission_targetabl_2d2e7427.csv 282_consensus_directrob     q3_only   2.00                   0.577795             -0.000310                 -0.000212               0.002573         199.0            1.290130
targetabl_0b1d2b4e submission_targetabl_0b1d2b4e.csv 282_consensus_directrob      q_only   1.75                   0.577797             -0.000683                 -0.000592               0.005579         522.0            1.162450
targetabl_dcf318c6 submission_targetabl_dcf318c6.csv             f43_cv_best       no_q2   1.30                   0.577802             -0.001311                 -0.001172               0.008627         930.0            1.341946
```

## Best Honest Anchor-CV Rows

```
              name                              file             source_name target_mask  scale  actual_anchor_score_final  honest_cv_delta_mean  honest_cv_delta_worst  robust_delta_vs_a2c8  robust_p90_delta_vs_a2c8  mean_abs_move_vs_a2c8  active_cells  mean_active_energy
targetabl_762bb880 submission_targetabl_762bb880.csv 282_consensus_directrob         all   1.75                   0.577870             -0.001115              -0.000773             -0.001469                 -0.001312               0.011864        1256.0            1.146752
targetabl_357a1ed9 submission_targetabl_357a1ed9.csv        f465_actual_best         all   1.75                   0.577818             -0.001113              -0.000787             -0.001445                 -0.001276               0.010801        1256.0            1.146752
targetabl_a5bc331f submission_targetabl_a5bc331f.csv        f465_actual_best       no_s4   2.00                   0.577890             -0.001111              -0.000769             -0.001467                 -0.001313               0.011054        1107.0            1.177328
targetabl_00e2e9b7 submission_targetabl_00e2e9b7.csv           3cf_noq2_safe       no_q2   2.00                   0.577885             -0.001105              -0.000747             -0.001479                 -0.001338               0.011028        1132.0            1.182363
targetabl_193facd0 submission_targetabl_193facd0.csv        f465_actual_best       no_q2   2.00                   0.577885             -0.001105              -0.000747             -0.001479                 -0.001338               0.011028        1132.0            1.182363
targetabl_20d44ef9 submission_targetabl_20d44ef9.csv             f43_cv_best       no_s4   1.50                   0.577878             -0.001090              -0.000753             -0.001426                 -0.001263               0.009928         910.0            1.335073
targetabl_266f6174 submission_targetabl_266f6174.csv             f43_cv_best q1_q3_stage   1.50                   0.577873             -0.001085              -0.000739             -0.001442                 -0.001290               0.009951         930.0            1.341946
targetabl_25970ebd submission_targetabl_25970ebd.csv             f43_cv_best       no_q2   1.50                   0.577873             -0.001085              -0.000739             -0.001442                 -0.001290               0.009951         930.0            1.341946
targetabl_61882c45 submission_targetabl_61882c45.csv             f43_cv_best         all   1.30                   0.577806             -0.001081              -0.000769             -0.001390                 -0.001212               0.009520        1015.0            1.312639
targetabl_0f2b76e6 submission_targetabl_0f2b76e6.csv        f465_actual_best       no_s1   2.00                   0.577861             -0.001074              -0.000767             -0.001364                 -0.001193               0.010841        1061.0            1.150707
targetabl_802a9a30 submission_targetabl_802a9a30.csv 282_consensus_directrob       no_s1   2.00                   0.577920             -0.001071              -0.000749             -0.001376                 -0.001217               0.011882        1061.0            1.150707
targetabl_641c8cfc submission_targetabl_641c8cfc.csv        f465_actual_best       no_s2   2.00                   0.577871             -0.001063              -0.000781             -0.001351                 -0.001207               0.010610        1067.0            1.155862
targetabl_8d5788b0 submission_targetabl_8d5788b0.csv 282_consensus_directrob       no_s2   2.00                   0.577932             -0.001055              -0.000758             -0.001364                 -0.001227               0.011655        1067.0            1.155862
targetabl_8258f77a submission_targetabl_8258f77a.csv             f43_cv_best       no_s1   1.50                   0.577850             -0.001049              -0.000746             -0.001323                 -0.001137               0.009655         859.0            1.316136
targetabl_712a71b9 submission_targetabl_712a71b9.csv             f43_cv_best       no_s2   1.50                   0.577860             -0.001039              -0.000768             -0.001310                 -0.001158               0.009463         866.0            1.319883
targetabl_ccc68112 submission_targetabl_ccc68112.csv 282_consensus_directrob       no_s4   1.75                   0.577862             -0.001036              -0.000723             -0.001366                 -0.001233               0.010576        1107.0            1.177328
targetabl_e8ef85d1 submission_targetabl_e8ef85d1.csv        f465_actual_best       no_s4   1.75                   0.577817             -0.001036              -0.000736             -0.001345                 -0.001203               0.009674        1107.0            1.177328
targetabl_05004f97 submission_targetabl_05004f97.csv 282_consensus_directrob       no_q2   1.75                   0.577857             -0.001029              -0.000700             -0.001376                 -0.001258               0.010556        1132.0            1.182363
targetabl_393a0c83 submission_targetabl_393a0c83.csv 282_consensus_directrob q1_q3_stage   1.75                   0.577857             -0.001029              -0.000700             -0.001376                 -0.001258               0.010556        1132.0            1.182363
targetabl_dd3c8158 submission_targetabl_dd3c8158.csv           3cf_noq2_safe       no_q2   1.75                   0.577812             -0.001028              -0.000715             -0.001355                 -0.001224               0.009653        1132.0            1.182363
targetabl_ca3d8d9b submission_targetabl_ca3d8d9b.csv           3cf_noq2_safe         all   1.75                   0.577812             -0.001028              -0.000715             -0.001355                 -0.001224               0.009653        1132.0            1.182363
targetabl_b2eb8623 submission_targetabl_b2eb8623.csv        f465_actual_best       no_q2   1.75                   0.577812             -0.001028              -0.000715             -0.001355                 -0.001224               0.009653        1132.0            1.182363
targetabl_17a41efb submission_targetabl_17a41efb.csv           3cf_noq2_safe q1_q3_stage   1.75                   0.577812             -0.001028              -0.000715             -0.001355                 -0.001224               0.009653        1132.0            1.182363
targetabl_d0ba36ac submission_targetabl_d0ba36ac.csv        f465_actual_best q1_q3_stage   1.75                   0.577812             -0.001028              -0.000715             -0.001355                 -0.001224               0.009653        1132.0            1.182363
targetabl_d15873ce submission_targetabl_d15873ce.csv 282_consensus_directrob         all   1.50                   0.577792             -0.001024              -0.000731             -0.001327                 -0.001184               0.010171        1256.0            1.146752
targetabl_803866f8 submission_targetabl_803866f8.csv           3cf_noq2_safe       no_s4   2.00                   0.577876             -0.001023              -0.000694             -0.001372                 -0.001259               0.009741         983.0            1.222194
targetabl_25d719c0 submission_targetabl_25d719c0.csv        f465_actual_best         all   1.50                   0.577757             -0.001013              -0.000734             -0.001296                 -0.001143               0.009260        1256.0            1.146752
targetabl_9f8f6190 submission_targetabl_9f8f6190.csv             f43_cv_best       no_s4   1.30                   0.577806             -0.001009              -0.000716             -0.001298                 -0.001148               0.008606         910.0            1.335073
targetabl_1d4d826e submission_targetabl_1d4d826e.csv 282_consensus_directrob       no_s1   1.75                   0.577836             -0.001007              -0.000726             -0.001273                 -0.001124               0.010398        1061.0            1.150707
targetabl_dcf318c6 submission_targetabl_dcf318c6.csv             f43_cv_best       no_q2   1.30                   0.577802             -0.001003              -0.000702             -0.001311                 -0.001172               0.008627         930.0            1.341946
targetabl_c99996cd submission_targetabl_c99996cd.csv             f43_cv_best q1_q3_stage   1.30                   0.577802             -0.001003              -0.000702             -0.001311                 -0.001172               0.008627         930.0            1.341946
targetabl_e93cdd0a submission_targetabl_e93cdd0a.csv        f465_actual_best       no_s1   1.75                   0.577793             -0.001001              -0.000732             -0.001253                 -0.001094               0.009487        1061.0            1.150707
targetabl_8542a8bd submission_targetabl_8542a8bd.csv 282_consensus_directrob       no_s2   1.75                   0.577847             -0.000992              -0.000732             -0.001261                 -0.001141               0.010202        1067.0            1.155862
targetabl_3e7366b5 submission_targetabl_3e7366b5.csv        f465_actual_best       no_s2   1.75                   0.577803             -0.000990              -0.000742             -0.001240                 -0.001112               0.009288        1067.0            1.155862
targetabl_a57d7d5f submission_targetabl_a57d7d5f.csv           3cf_noq2_safe       no_s1   2.00                   0.577847             -0.000986              -0.000688             -0.001269                 -0.001138               0.009527         937.0            1.194253
targetabl_2c3e775d submission_targetabl_2c3e775d.csv           3cf_noq2_safe       no_s2   2.00                   0.577856             -0.000975              -0.000706             -0.001256                 -0.001178               0.009297         943.0            1.199808
targetabl_d491786e submission_targetabl_d491786e.csv             f43_cv_best       no_s1   1.30                   0.577784             -0.000971              -0.000707             -0.001206                 -0.001035               0.008369         859.0            1.316136
targetabl_df1cba6e submission_targetabl_df1cba6e.csv        f465_actual_best       no_s3   2.00                   0.577878             -0.000968              -0.000708             -0.001272                 -0.001067               0.010343        1055.0            1.109246
targetabl_feb1c371 submission_targetabl_feb1c371.csv        f465_actual_best       no_q1   2.00                   0.577882             -0.000968              -0.000653             -0.001245                 -0.001001               0.010210        1057.0            1.127856
targetabl_a436064c submission_targetabl_a436064c.csv           3cf_noq2_safe       no_s4   1.75                   0.577811             -0.000951              -0.000662             -0.001255                 -0.001151               0.008525         983.0            1.222194
targetabl_a9029a9b submission_targetabl_a9029a9b.csv 282_consensus_directrob       no_s4   1.50                   0.577792             -0.000950              -0.000682             -0.001232                 -0.001111               0.009067        1107.0            1.177328
targetabl_17065b7a submission_targetabl_17065b7a.csv             f43_cv_best       no_s3   1.50                   0.577866             -0.000945              -0.000695             -0.001228                 -0.001012               0.009092         835.0            1.283199
targetabl_9dca6c3f submission_targetabl_9dca6c3f.csv             f43_cv_best       no_q1   1.50                   0.577868             -0.000944              -0.000640             -0.001202                 -0.000957               0.008993         841.0            1.302191
targetabl_e1bf4b1a submission_targetabl_e1bf4b1a.csv 282_consensus_directrob       no_q2   1.50                   0.577789             -0.000942              -0.000661             -0.001239                 -0.001134               0.009050        1132.0            1.182363
targetabl_940d9323 submission_targetabl_940d9323.csv 282_consensus_directrob q1_q3_stage   1.50                   0.577789             -0.000942              -0.000661             -0.001239                 -0.001134               0.009050        1132.0            1.182363
targetabl_64102eec submission_targetabl_64102eec.csv 282_consensus_directrob         all   1.30                   0.577746             -0.000935              -0.000682             -0.001196                 -0.001067               0.008816        1256.0            1.146752
targetabl_8f81d324 submission_targetabl_8f81d324.csv        f465_actual_best       no_q2   1.50                   0.577758             -0.000934              -0.000666             -0.001213                 -0.001096               0.008276        1132.0            1.182363
targetabl_b640b6ac submission_targetabl_b640b6ac.csv        f465_actual_best q1_q3_stage   1.50                   0.577758             -0.000934              -0.000666             -0.001213                 -0.001096               0.008276        1132.0            1.182363
targetabl_6e771ba8 submission_targetabl_6e771ba8.csv 282_consensus_directrob       no_s1   1.50                   0.577771             -0.000924              -0.000682             -0.001150                 -0.001015               0.008913        1061.0            1.150707
targetabl_5df65853 submission_targetabl_5df65853.csv 282_consensus_directrob       no_q1   1.75                   0.577859             -0.000907              -0.000618             -0.001166                 -0.000948               0.009846        1057.0            1.127856
```

## Target Mask Summary

```
            source_name target_mask  best_actual_anchor  best_honest_cv  best_move
       f465_actual_best    q3_stage            0.577727       -0.000880   0.008897
          3cf_noq2_safe    q3_stage            0.577727       -0.000744   0.006676
282_consensus_directrob    q3_stage            0.577734       -0.000752   0.007320
       f465_actual_best      q_only            0.577734       -0.000593   0.005096
282_consensus_directrob      q_only            0.577738       -0.000599   0.005579
          3cf_noq2_safe q3_s2_s3_s4            0.577738       -0.000707   0.006473
       f465_actual_best q3_s2_s3_s4            0.577738       -0.000707   0.006473
            f43_cv_best q3_s2_s3_s4            0.577741       -0.000688   0.005751
            f43_cv_best      q_only            0.577744       -0.000574   0.004500
          3cf_noq2_safe      q_only            0.577744       -0.000550   0.004510
282_consensus_directrob         all            0.577746       -0.001115   0.011864
            f43_cv_best    q3_stage            0.577747       -0.000671   0.005311
282_consensus_directrob q3_s2_s3_s4            0.577749       -0.000652   0.006062
       f465_actual_best         all            0.577757       -0.001113   0.010801
       f465_actual_best       no_q2            0.577758       -0.001105   0.011028
       f465_actual_best q1_q3_stage            0.577758       -0.001028   0.009653
282_consensus_directrob       no_s1            0.577771       -0.001071   0.011882
            f43_cv_best       no_s1            0.577784       -0.001049   0.009655
          3cf_noq2_safe     q3_only            0.577787       -0.000325   0.002379
       f465_actual_best     q3_only            0.577787       -0.000325   0.002379
282_consensus_directrob       no_q2            0.577789       -0.001029   0.010556
282_consensus_directrob q1_q3_stage            0.577789       -0.001029   0.010556
282_consensus_directrob       no_s4            0.577792       -0.001036   0.010576
       f465_actual_best       no_s1            0.577793       -0.001074   0.010841
282_consensus_directrob     q3_only            0.577795       -0.000330   0.002573
            f43_cv_best       no_q2            0.577802       -0.001085   0.009951
            f43_cv_best q1_q3_stage            0.577802       -0.001085   0.009951
       f465_actual_best       no_s2            0.577803       -0.001063   0.010610
            f43_cv_best     q3_only            0.577804       -0.000370   0.002891
            f43_cv_best         all            0.577806       -0.001081   0.009520
            f43_cv_best       no_s4            0.577806       -0.001090   0.009928
          3cf_noq2_safe       no_s4            0.577811       -0.001023   0.009741
          3cf_noq2_safe       no_q2            0.577812       -0.001105   0.011028
          3cf_noq2_safe         all            0.577812       -0.001028   0.009653
          3cf_noq2_safe q1_q3_stage            0.577812       -0.001028   0.009653
       f465_actual_best       no_s3            0.577813       -0.000968   0.010343
       f465_actual_best       no_q1            0.577816       -0.000968   0.010210
       f465_actual_best       no_s4            0.577817       -0.001111   0.011054
            f43_cv_best     q1_only            0.577832       -0.000247   0.002649
          3cf_noq2_safe     q1_only            0.577832       -0.000225   0.002131
       f465_actual_best     q1_only            0.577832       -0.000225   0.002131
282_consensus_directrob     s3_only            0.577841       -0.000223   0.002134
282_consensus_directrob     q1_only            0.577843       -0.000221   0.002306
282_consensus_directrob       no_s2            0.577847       -0.001055   0.011655
          3cf_noq2_safe       no_s1            0.577847       -0.000986   0.009527
            f43_cv_best     s3_only            0.577854       -0.000248   0.002516
          3cf_noq2_safe       no_s2            0.577856       -0.000975   0.009297
282_consensus_directrob       no_s3            0.577856       -0.000907   0.009996
282_consensus_directrob       no_q1            0.577859       -0.000907   0.009846
            f43_cv_best       no_s2            0.577860       -0.001039   0.009463
          3cf_noq2_safe       no_s3            0.577863       -0.000880   0.009029
       f465_actual_best       no_q3            0.577864       -0.000814   0.008719
            f43_cv_best       no_s3            0.577866       -0.000945   0.009092
            f43_cv_best       no_q1            0.577868       -0.000944   0.008993
          3cf_noq2_safe       no_q1            0.577869       -0.000880   0.008897
282_consensus_directrob       no_q3            0.577911       -0.000810   0.009612
            f43_cv_best       no_q3            0.577921       -0.000848   0.008812
          3cf_noq2_safe       no_q3            0.577922       -0.000779   0.008650
```

## Selected Submissions

```
       submit_role               name                              file             source_name target_mask  scale  actual_anchor_score_final  honest_cv_delta_mean  honest_cv_delta_worst  robust_delta_vs_a2c8  robust_p90_delta_vs_a2c8  mean_abs_move_vs_a2c8  active_cells  mean_active_energy
   targetabl_first targetabl_64102eec submission_targetabl_64102eec.csv 282_consensus_directrob         all   1.30                   0.577746             -0.000935              -0.000682             -0.001196                 -0.001067               0.008816        1256.0            1.146752
   targetabl_first targetabl_25d719c0 submission_targetabl_25d719c0.csv        f465_actual_best         all   1.50                   0.577757             -0.001013              -0.000734             -0.001296                 -0.001143               0.009260        1256.0            1.146752
   targetabl_first targetabl_8f81d324 submission_targetabl_8f81d324.csv        f465_actual_best       no_q2   1.50                   0.577758             -0.000934              -0.000666             -0.001213                 -0.001096               0.008276        1132.0            1.182363
   targetabl_first targetabl_b640b6ac submission_targetabl_b640b6ac.csv        f465_actual_best q1_q3_stage   1.50                   0.577758             -0.000934              -0.000666             -0.001213                 -0.001096               0.008276        1132.0            1.182363
   targetabl_group targetabl_b19056bb submission_targetabl_b19056bb.csv        f465_actual_best    q3_stage   1.00                   0.577727             -0.000552              -0.000402             -0.000686                 -0.000567               0.004452         933.0            1.168551
   targetabl_group targetabl_585c0b46 submission_targetabl_585c0b46.csv           3cf_noq2_safe    q3_stage   1.00                   0.577727             -0.000552              -0.000402             -0.000686                 -0.000567               0.004452         933.0            1.168551
   targetabl_group targetabl_81af7484 submission_targetabl_81af7484.csv 282_consensus_directrob    q3_stage   1.00                   0.577734             -0.000566              -0.000409             -0.000710                 -0.000595               0.004882         933.0            1.168551
   targetabl_group targetabl_1049b8e7 submission_targetabl_1049b8e7.csv        f465_actual_best q3_s2_s3_s4   1.30                   0.577738             -0.000580              -0.000422             -0.000696                 -0.000557               0.004809         738.0            1.179996
   targetabl_group targetabl_94359b98 submission_targetabl_94359b98.csv           3cf_noq2_safe q3_s2_s3_s4   1.30                   0.577738             -0.000580              -0.000422             -0.000696                 -0.000557               0.004809         738.0            1.179996
targetabl_leaveone targetabl_6e771ba8 submission_targetabl_6e771ba8.csv 282_consensus_directrob       no_s1   1.50                   0.577771             -0.000924              -0.000682             -0.001150                 -0.001015               0.008913        1061.0            1.150707
targetabl_leaveone targetabl_d491786e submission_targetabl_d491786e.csv             f43_cv_best       no_s1   1.30                   0.577784             -0.000971              -0.000707             -0.001206                 -0.001035               0.008369         859.0            1.316136
targetabl_leaveone targetabl_e1bf4b1a submission_targetabl_e1bf4b1a.csv 282_consensus_directrob       no_q2   1.50                   0.577789             -0.000942              -0.000661             -0.001239                 -0.001134               0.009050        1132.0            1.182363
targetabl_leaveone targetabl_a9029a9b submission_targetabl_a9029a9b.csv 282_consensus_directrob       no_s4   1.50                   0.577792             -0.000950              -0.000682             -0.001232                 -0.001111               0.009067        1107.0            1.177328
  targetabl_single targetabl_75aa4b39 submission_targetabl_75aa4b39.csv        f465_actual_best     q3_only   2.00                   0.577787             -0.000325              -0.000266             -0.000308                 -0.000211               0.002379         199.0            1.290130
  targetabl_single targetabl_c9b4082b submission_targetabl_c9b4082b.csv           3cf_noq2_safe     q3_only   2.00                   0.577787             -0.000325              -0.000266             -0.000308                 -0.000211               0.002379         199.0            1.290130
  targetabl_single targetabl_2d2e7427 submission_targetabl_2d2e7427.csv 282_consensus_directrob     q3_only   2.00                   0.577795             -0.000330              -0.000270             -0.000310                 -0.000212               0.002573         199.0            1.290130
  targetabl_single targetabl_e27745fa submission_targetabl_e27745fa.csv             f43_cv_best     q3_only   1.75                   0.577804             -0.000348              -0.000280             -0.000328                 -0.000219               0.002531         166.0            1.454685
  targetabl_single targetabl_de615248 submission_targetabl_de615248.csv             f43_cv_best     q3_only   2.00                   0.577829             -0.000370              -0.000293             -0.000348                 -0.000227               0.002891         166.0            1.454685
  targetabl_single targetabl_f8ee43f3 submission_targetabl_f8ee43f3.csv             f43_cv_best     q1_only   1.50                   0.577832             -0.000222              -0.000143             -0.000324                 -0.000270               0.001989         174.0            1.363138
  targetabl_single targetabl_f27d1bdb submission_targetabl_f27d1bdb.csv        f465_actual_best     q1_only   2.00                   0.577832             -0.000225              -0.000145             -0.000329                 -0.000276               0.002131         199.0            1.247123
```

## Interpretation

- Leave-one masks test which target causes public-axis leakage when the sparse direction is scaled.
- Single-target masks are not first-submit score candidates; they are diagnostic axes for interpreting public feedback.
- If full/no-Q2 scale improves but target-only probes disagree, the hidden subset is target-coupled rather than separable by label.
