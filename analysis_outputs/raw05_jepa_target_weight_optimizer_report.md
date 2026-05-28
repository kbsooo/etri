# Raw05 JEPA Target Weight Optimizer

This pass treats JEPA donor deltas as target-block representation confidence rather than binary target grafts.
Each candidate is logit(raw05) + target_weight * (logit(donor) - logit(raw05)).

## Counts

- scored candidates: 8520
- saved candidates: 112

## Top Saved

```csv
file,bucket,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,mean_abs_move_vs_raw05,w_Q2,w_S1,w_Q3,w_S4,label
submission_raw05_jepa_targetw_050ca305.csv,balanced,0.5778425183,0.5768797129,-1.005e-07,0.002379415,0.0015476814,1.0,1.0,1.0,1.0,jepa_micro_bridge_ensemble_5ffa44a8|q2s1_plane|q21.00|s11.00
submission_raw05_jepa_targetw_7844a2ad.csv,balanced,0.577842594,0.5768791937,-1.1e-07,0.0023838908,0.0015442059,1.0,1.0,1.0,1.0,jepa_micro_bridge_ensemble_a06a8e5b|q2s1_plane|q21.00|s11.00
submission_raw05_jepa_targetw_5ba629ca.csv,balanced,0.5778426047,0.5768670669,9.81e-08,0.0020188433,0.0016522207,1.0,1.0,1.0,1.0,jepa_micro_bridge_ensemble_22063df5|q2s1_plane|q21.00|s11.00
submission_raw05_jepa_targetw_d17e3b46.csv,balanced,0.5778426194,0.5768669485,9.28e-08,0.0020207985,0.0016507967,1.0,1.0,1.0,1.0,jepa_micro_bridge_ensemble_940b779e|q2s1_plane|q21.00|s11.00
submission_raw05_jepa_targetw_5dea9732.csv,balanced,0.5778426343,0.5768668301,8.75e-08,0.0020227538,0.0016493726,1.0,1.0,1.0,1.0,jepa_micro_bridge_ensemble_bf074240|q2s1_plane|q21.00|s11.00
submission_raw05_jepa_targetw_03db4bdd.csv,balanced,0.5778426492,0.5768667118,8.23e-08,0.0020247093,0.0016479503,1.0,1.0,1.0,1.0,jepa_micro_bridge_ensemble_c90dd76f|q2s1_plane|q21.00|s11.00
submission_raw05_jepa_targetw_adddad42.csv,balanced,0.5778426594,0.5768745484,-6.18e-08,0.0022955081,0.0015668252,1.0,1.0,1.0,1.0,jepa_micro_bridge_ensemble_eb296a12|q2s1_plane|q21.00|s11.00
submission_raw05_jepa_targetw_9b31204f.csv,balanced,0.5778426702,0.576878675,-1.192e-07,0.0023883674,0.0015407351,1.0,1.0,1.0,1.0,jepa_micro_bridge_ensemble_9a83e05d|q2s1_plane|q21.00|s11.00
submission_raw05_jepa_targetw_2be435f9.csv,balanced,0.5778426954,0.5768811779,-1.338e-07,0.0020581405,0.0015335751,0.75,1.0,1.0,1.0,jepa_micro_bridge_ensemble_5ffa44a8|q2s1_plane|q20.75|s11.00
submission_raw05_jepa_targetw_2b596731.csv,balanced,0.57784271,0.5768792813,-1.846e-07,0.0023683403,0.0015395035,1.0,1.0,1.0,1.0,jepa_micro_bridge_ensemble_9692910f|q2s1_plane|q21.00|s11.00
submission_raw05_jepa_targetw_3b729db5.csv,balanced,0.5778427436,0.5768689784,8.82e-08,0.0016996704,0.001644151,0.75,1.0,1.0,1.0,jepa_block_consensus_rawcorr_micro_9ec2b75e|q2s1_plane|q20.75|s11.00
submission_raw05_jepa_targetw_80a2087b.csv,balanced,0.5778427445,0.5768739674,-7.32e-08,0.0023005103,0.0015629261,1.0,1.0,1.0,1.0,jepa_micro_bridge_ensemble_7e335eb7|q2s1_plane|q21.00|s11.00
submission_raw05_jepa_targetw_568ca80c.csv,balanced,0.5778427471,0.5768781565,-1.281e-07,0.0023928449,0.0015372677,1.0,1.0,1.0,1.0,jepa_micro_bridge_ensemble_6e15f03a|q2s1_plane|q21.00|s11.00
submission_raw05_jepa_targetw_6638c870.csv,balanced,0.5778427705,0.5768806522,-1.431e-07,0.0020630171,0.0015301467,0.75,1.0,1.0,1.0,jepa_micro_bridge_ensemble_a06a8e5b|q2s1_plane|q20.75|s11.00
submission_raw05_jepa_targetw_c29606e9.csv,balanced,0.5778428011,0.5768684957,6.66e-08,0.0017077622,0.0016385049,0.75,1.0,1.0,1.0,jepa_micro_bridge_ensemble_22063df5|q2s1_plane|q20.75|s11.00
submission_raw05_jepa_targetw_bff0d673.csv,balanced,0.5778428157,0.5768683751,6.14e-08,0.0017097854,0.0016370953,0.75,1.0,1.0,1.0,jepa_micro_bridge_ensemble_940b779e|q2s1_plane|q20.75|s11.00
submission_raw05_jepa_targetw_266f0228.csv,balanced,0.5778428303,0.5768682546,5.62e-08,0.0017118088,0.0016356856,0.75,1.0,1.0,1.0,jepa_micro_bridge_ensemble_bf074240|q2s1_plane|q20.75|s11.00
submission_raw05_jepa_targetw_5e768f64.csv,balanced,0.5778428321,0.5768759897,-9.41e-08,0.0019779043,0.001552925,0.75,1.0,1.0,1.0,jepa_micro_bridge_ensemble_eb296a12|q2s1_plane|q20.75|s11.00
submission_raw05_jepa_targetw_24027114.csv,balanced,0.5778428449,0.5768681342,5.1e-08,0.0017138324,0.0016342776,0.75,1.0,1.0,1.0,jepa_micro_bridge_ensemble_c90dd76f|q2s1_plane|q20.75|s11.00
submission_raw05_jepa_targetw_87a11594.csv,balanced,0.577842846,0.5768801268,-1.521e-07,0.0020678946,0.001526723,0.75,1.0,1.0,1.0,jepa_micro_bridge_ensemble_9a83e05d|q2s1_plane|q20.75|s11.00
submission_raw05_jepa_targetw_5a4ab9c6.csv,balanced,0.577842874,0.576868543,-3.1e-09,0.0020232423,0.0016504277,1.0,1.0,1.0,1.0,jepa_block_consensus_rawcorr_micro_fea06910|q2s1_plane|q21.00|s11.00
submission_raw05_jepa_targetw_3dc3d1af.csv,balanced,0.5778428819,0.5768807144,-2.169e-07,0.0020478771,0.0015256052,0.75,1.0,1.0,1.0,jepa_micro_bridge_ensemble_9692910f|q2s1_plane|q20.75|s11.00
submission_raw05_jepa_targetw_e2cdf19d.csv,balanced,0.5778428831,0.5768826524,-1.575e-07,0.0017369685,0.0015194707,0.5,1.0,1.0,1.0,jepa_micro_bridge_ensemble_5ffa44a8|q2s1_plane|q20.50|s11.00
submission_raw05_jepa_targetw_28a9d1c7.csv,balanced,0.5778429164,0.5768754014,-1.053e-07,0.0019833545,0.0015490786,0.75,1.0,1.0,1.0,jepa_micro_bridge_ensemble_7e335eb7|q2s1_plane|q20.75|s11.00
submission_raw05_jepa_targetw_27cb0fc2.csv,balanced,0.577842922,0.5768796018,-1.607e-07,0.0020727729,0.0015233027,0.75,1.0,1.0,1.0,jepa_micro_bridge_ensemble_6e15f03a|q2s1_plane|q20.75|s11.00
submission_raw05_jepa_targetw_decbd3a5.csv,balanced,0.5778429503,0.5768704249,6.56e-08,0.0013884143,0.0016303795,0.5,1.0,1.0,1.0,jepa_block_consensus_rawcorr_micro_9ec2b75e|q2s1_plane|q20.50|s11.00
submission_raw05_jepa_targetw_7a0f3136.csv,balanced,0.5778429575,0.5768821201,-1.667e-07,0.0017422455,0.0015160894,0.5,1.0,1.0,1.0,jepa_micro_bridge_ensemble_a06a8e5b|q2s1_plane|q20.50|s11.00
submission_raw05_jepa_targetw_f8c12205.csv,balanced,0.577842971,0.576898901,6.82e-08,0.0023021246,0.001427277,0.7,0.7,1.22,1.0,jepa_bridge_ensemble_c42fbf1e|q2s1q3_refine2|q20.70|s10.70|q31.22
submission_raw05_jepa_targetw_038f70cc.csv,balanced,0.5778429996,0.5768991124,6.48e-08,0.0022423003,0.0014249846,0.65,0.7,1.22,1.0,jepa_bridge_ensemble_c42fbf1e|q2s1q3_refine2|q20.65|s10.70|q31.22
submission_raw05_jepa_targetw_f2dc24be.csv,balanced,0.5778430068,0.5768699335,4.42e-08,0.0013967777,0.001624791,0.5,1.0,1.0,1.0,jepa_micro_bridge_ensemble_22063df5|q2s1_plane|q20.50|s11.00
submission_raw05_jepa_targetw_bded1257.csv,balanced,0.5778430211,0.5768698108,3.9e-08,0.0013988689,0.0016233957,0.5,1.0,1.0,1.0,jepa_micro_bridge_ensemble_940b779e|q2s1_plane|q20.50|s11.00
submission_raw05_jepa_targetw_f4a4677e.csv,balanced,0.5778430262,0.5768774404,-1.172e-07,0.0016604004,0.0015390267,0.5,1.0,1.0,1.0,jepa_micro_bridge_ensemble_eb296a12|q2s1_plane|q20.50|s11.00
submission_raw05_jepa_targetw_23629fbf.csv,balanced,0.5778430284,0.5768993241,6.17e-08,0.0021824791,0.0014226922,0.6,0.7,1.22,1.0,jepa_bridge_ensemble_c42fbf1e|q2s1q3_refine2|q20.60|s10.70|q31.22
submission_raw05_jepa_targetw_efffcf11.csv,balanced,0.5778430323,0.5768815881,-1.755e-07,0.0017475232,0.0015127128,0.5,1.0,1.0,1.0,jepa_micro_bridge_ensemble_9a83e05d|q2s1_plane|q20.50|s11.00
submission_raw05_jepa_targetw_18683ac4.csv,balanced,0.5778430354,0.5768696881,3.38e-08,0.0014009602,0.0016220005,0.5,1.0,1.0,1.0,jepa_micro_bridge_ensemble_bf074240|q2s1_plane|q20.50|s11.00
```

## Best By Template Family

```csv
template_family,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,w_Q2,w_S1,w_Q3,w_S4,label
q2s1q3_stress,0.577838094,0.5769237918,5.16e-07,0.0025278306,0.8,0.7,1.4,1.0,jepa_micro_bridge_ensemble_5ffa44a8|q2s1q3_stress|q20.80|s10.70|q31.40
q2s1q3_refine2,0.5778397108,0.576944174,-1.624e-07,0.0023409606,0.7,0.65,1.25,1.0,jepa_micro_bridge_ensemble_5ffa44a8|q2s1q3_refine2|q20.70|s10.65|q31.25
q2s1q3_refine,0.5778406835,0.5769509315,-3.153e-07,0.0018402071,0.6,0.6,1.16,1.0,jepa_block_consensus_rawcorr_micro_9ec2b75e|q2s1q3_refine|q20.60|s10.60|q31.16
q2s1q3,0.5778413893,0.577034459,-7.909e-07,0.0018804576,0.5,0.25,1.1,1.0,jepa_block_consensus_rawcorr_micro_9ec2b75e|q2s1q3|q20.50|s10.25|q31.10
q2s1_plane,0.5778421171,0.5769805161,-8.736e-07,0.0022993482,1.0,0.5,1.0,1.0,jepa_block_consensus_rawcorr_micro_9ec2b75e|q2s1_plane|q21.00|s10.50
q2s1s4,0.5778423289,0.5769935908,-9.587e-07,0.0019544601,0.7,0.45,1.0,1.0,jepa_block_consensus_rawcorr_micro_9ec2b75e|q2s1s4|q20.70|s10.45|s41.00
q2sblock,0.5778425265,0.577040237,-1.0752e-06,0.0018201629,0.5,0.25,1.0,1.0,jepa_block_consensus_rawcorr_micro_9ec2b75e|q2sblock|q20.50|s10.25|s21.00|s31.00
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_jepa_targetw_050ca305.csv,250,True,0,0,0.0632254238,0.9797320058
submission_raw05_jepa_targetw_7844a2ad.csv,250,True,0,0,0.0632243828,0.9797319587
submission_raw05_jepa_targetw_5ba629ca.csv,250,True,0,0,0.0632159126,0.9797309797
submission_raw05_jepa_targetw_d17e3b46.csv,250,True,0,0,0.0632151609,0.9797309451
submission_raw05_jepa_targetw_5dea9732.csv,250,True,0,0,0.0632144092,0.9797309105
submission_raw05_jepa_targetw_03db4bdd.csv,250,True,0,0,0.0632136576,0.979730876
submission_raw05_jepa_targetw_adddad42.csv,250,True,0,0,0.0632246757,0.9797314094
submission_raw05_jepa_targetw_9b31204f.csv,250,True,0,0,0.0632233417,0.9797319117
submission_raw05_jepa_targetw_2be435f9.csv,250,True,0,0,0.0632254238,0.9797320058
submission_raw05_jepa_targetw_2b596731.csv,250,True,0,0,0.0631988161,0.979731721
submission_raw05_jepa_targetw_3b729db5.csv,250,True,0,0,0.0632189194,0.9797311179
submission_raw05_jepa_targetw_80a2087b.csv,250,True,0,0,0.0632235122,0.9797313568
submission_raw05_jepa_targetw_568ca80c.csv,250,True,0,0,0.0632223007,0.9797318647
submission_raw05_jepa_targetw_6638c870.csv,250,True,0,0,0.0632243828,0.9797319587
submission_raw05_jepa_targetw_c29606e9.csv,250,True,0,0,0.0632159126,0.9797309797
submission_raw05_jepa_targetw_bff0d673.csv,250,True,0,0,0.0632151609,0.9797309451
submission_raw05_jepa_targetw_266f0228.csv,250,True,0,0,0.0632144092,0.9797309105
submission_raw05_jepa_targetw_5e768f64.csv,250,True,0,0,0.0632246757,0.9797314094
submission_raw05_jepa_targetw_24027114.csv,250,True,0,0,0.0632136576,0.979730876
submission_raw05_jepa_targetw_87a11594.csv,250,True,0,0,0.0632233417,0.9797319117
submission_raw05_jepa_targetw_5a4ab9c6.csv,250,True,0,0,0.0632105794,0.979732199
submission_raw05_jepa_targetw_3dc3d1af.csv,250,True,0,0,0.0631988161,0.979731721
submission_raw05_jepa_targetw_e2cdf19d.csv,250,True,0,0,0.0632254238,0.9797320058
submission_raw05_jepa_targetw_28a9d1c7.csv,250,True,0,0,0.0632235122,0.9797313568
submission_raw05_jepa_targetw_27cb0fc2.csv,250,True,0,0,0.0632223007,0.9797318647
submission_raw05_jepa_targetw_decbd3a5.csv,250,True,0,0,0.0632189194,0.9797311179
submission_raw05_jepa_targetw_7a0f3136.csv,250,True,0,0,0.0632243828,0.9797319587
submission_raw05_jepa_targetw_f8c12205.csv,250,True,0,0,0.0630844955,0.9798245202
submission_raw05_jepa_targetw_038f70cc.csv,250,True,0,0,0.0630844955,0.9798245202
submission_raw05_jepa_targetw_f2dc24be.csv,250,True,0,0,0.0632159126,0.9797309797
submission_raw05_jepa_targetw_bded1257.csv,250,True,0,0,0.0632151609,0.9797309451
submission_raw05_jepa_targetw_f4a4677e.csv,250,True,0,0,0.0632246757,0.9797314094
submission_raw05_jepa_targetw_23629fbf.csv,250,True,0,0,0.0630844955,0.9798245202
submission_raw05_jepa_targetw_efffcf11.csv,250,True,0,0,0.0632233417,0.9797319117
submission_raw05_jepa_targetw_18683ac4.csv,250,True,0,0,0.0632144092,0.9797309105
```
