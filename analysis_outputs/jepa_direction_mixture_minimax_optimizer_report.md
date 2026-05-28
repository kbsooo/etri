# JEPA Direction Mixture Minimax Optimizer

Purpose: optimize larger sparse-JEPA/direct-label direction mixtures against public-anchor combo stress, not just local CV or raw05 micro calibration.

## Counts

- generated candidates: 61630
- actual-anchor rescored pool: 1800
- combo-stress summarized candidates including references: 190
- saved submissions: 7

## Reference Combo Stress

```csv
name,file,combo_weighted_delta_vs_b01_ladder,combo_weighted_win_vs_b01_ladder,combo_p90_delta_vs_b01_ladder,combo_worst_delta_vs_b01_ladder,combo_weighted_delta_vs_direns_c4af,combo_weighted_delta_vs_898_ladder
a2c8,submission_frontier_cvjepa_refine_a2c8d2c8.csv,0.0001705483,0.5347516393,0.0008193013,0.0011084214,0.0001817893,0.0001724454
raw05,submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.0002365374,0.5347516393,0.0009807239,0.0013447995,0.0002477784,0.0002384345
b01_ladder,submission_sparseladder_b01acaa1.csv,0.0,0.0,0.0,0.0,1.1241e-05,1.8971e-06
898_ladder,submission_sparseladder_89817541.csv,-1.8971e-06,0.4615516301,4.79508e-05,5.56469e-05,9.3439e-06,0.0
f1ee_noq2,submission_sparseladder_f1ee16b0.csv,8.9835e-06,0.1541370138,1.97142e-05,9.67746e-05,2.02244e-05,1.08805e-05
blockorth_3a28,submission_blockorth_3a28f87f.csv,5.5724e-06,0.5444044768,3.90347e-05,0.0001029013,1.68133e-05,7.4694e-06
target_q3stage,submission_targetabl_b19056bb.csv,2.42666e-05,0.5347516393,0.0003199776,0.0005134317,3.55076e-05,2.61637e-05
direns_c4af,submission_direns_c4af1fd8.csv,-1.1241e-05,0.6344034753,6.8048e-06,3.48645e-05,0.0,-9.3439e-06
direns_2a96,submission_direns_2a96ae73.csv,-8.9268e-06,0.5623969207,4.39514e-05,0.0001013082,2.3142e-06,-7.0297e-06
direns_c0fd,submission_direns_c0fdb76b.csv,-1.0389e-05,0.5732726205,2.17311e-05,5.85162e-05,8.52e-07,-8.4919e-06
```

## Selected Candidates

```csv
submit_role,name,file,selection_score,actual_anchor_score_final,combo_weighted_delta_vs_b01_ladder,combo_weighted_win_vs_b01_ladder,combo_p90_delta_vs_b01_ladder,combo_worst_delta_vs_b01_ladder,combo_weighted_delta_vs_direns_c4af,honest_cv_delta_mean,honest_cv_delta_worst,mean_abs_move_vs_a2c8,source_name,source_weights,variant,scale
mixmin_c4af_stress,mixmin_caff74ac1e,submission_mixmin_0c916bb4.csv,0.5777436616,0.5777344877,-1.28772e-05,0.9786586563,-8.4516e-06,1.01388e-05,-1.6362e-06,-0.0009519635,-0.0006959663,0.0084958244,direns_c4af+s898,direns_c4af:0.350+s898:0.650,full/all/all_cells/none,0.95
mixmin_c4af_stress,mixmin_aa50fa9af2,submission_mixmin_5a4c25e0.csv,0.5777443453,0.5777365184,-1.23737e-05,0.9660512627,-2.8712e-06,9.4354e-06,-1.1327e-06,-0.0009612877,-0.0007001819,0.0085302926,b01+s898+f1ee,b01:0.079+s898:0.671+f1ee:0.250,full/all/all_cells/none,0.95
mixmin_c4af_stress,mixmin_45edc36de2,submission_mixmin_f0d12643.csv,0.5777466304,0.577736298,-1.25478e-05,0.9487188994,-3.9229e-06,2.08456e-05,-1.3068e-06,-0.0009546235,-0.0006954091,0.0085239061,b01+s898+f1ee+block3a28+target_q3,b01:0.070+s898:0.630+f1ee:0.040+block3a28:0.043+target_q3:0.217,full/all/all_cells/none,1.05
mixmin_frontier,mixmin_06e2c51f33,submission_mixmin_f6c04249.csv,0.5777422626,0.5777374113,-1.1453e-05,0.9652530486,-1.9733e-06,6.8667e-06,-2.12e-07,-0.0009607828,-0.0007008396,0.0086006298,b01+s898+f1ee,b01:0.175+s898:0.694+f1ee:0.132,full/all/all_cells/none,0.95
mixmin_frontier,mixmin_9e7a38f4c6,submission_mixmin_ef4b1c19.csv,0.5777423725,0.5777370744,-1.17175e-05,0.9697035891,-2.481e-06,6.0524e-06,-4.765e-07,-0.0009605732,-0.0007005123,0.0085832132,b01+s898+f1ee,b01:0.160+s898:0.683+f1ee:0.157,full/all/all_cells/none,0.95
mixmin_frontier,mixmin_7b3e32d8d0,submission_mixmin_7f9cb635.csv,0.5777424998,0.5777378315,-1.15077e-05,0.920569701,-5.007e-07,8.7481e-06,-2.667e-07,-0.0009636074,-0.0007027229,0.0086166102,b01+s898+f1ee,b01:0.136+s898:0.732+f1ee:0.132,full/all/all_cells/none,0.95
mixmin_frontier,mixmin_7d50ee24c9,submission_mixmin_615da9a7.csv,0.5777426438,0.5777377618,-1.16608e-05,0.9286071104,-4.926e-07,1.13087e-05,-4.198e-07,-0.0009640084,-0.0007039325,0.0086251377,direns_c4af+s898,direns_c4af:0.200+s898:0.800,full/all/all_cells/none,0.95
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob,mean_prob
submission_mixmin_0c916bb4.csv,250,True,0,0,0.0681101767,0.9797988457,0.594372307
submission_mixmin_5a4c25e0.csv,250,True,0,0,0.0682681061,0.9797988457,0.5943896201
submission_mixmin_f0d12643.csv,250,True,0,0,0.06750754,0.9797988457,0.5944553683
submission_mixmin_f6c04249.csv,250,True,0,0,0.0681989976,0.9797988457,0.5943776419
submission_mixmin_ef4b1c19.csv,250,True,0,0,0.0682098878,0.9797988457,0.5943794915
submission_mixmin_7f9cb635.csv,250,True,0,0,0.0682267945,0.9797988457,0.5943827925
submission_mixmin_615da9a7.csv,250,True,0,0,0.06820249,0.9797988457,0.5943850143
```

## Interpretation

- This run treats `direns_c4af` as the current robust frontier. A new candidate must either beat it on combo-stress or create a larger controlled move with acceptable LOO/L2O anchor-CV.
- Positive `combo_p90_delta_vs_b01_ladder` or `combo_worst_delta_vs_b01_ladder` means the candidate still has a hidden public bad-axis tail even if the weighted mean improves.
- Projection variants are kept only if the public-anchor stress objective rewards them; previous global orthogonalization was too blunt.

