# Local LB Anchor Robustness Probe

This probe retrains the local public-LB proxy after dropping each known public anchor in turn, then evaluates each candidate relative to raw05 under every leave-one-anchor scenario.

## Leave-One-Anchor Model Errors

```csv
model,features,alpha,mae,rmse,max_abs,bias
abs_axes,"abs_delta_vs_raw05_rawaxis,abs_bad_residual_axis_ratio,mean_abs_move_vs_raw05",1.0,0.0003184931,0.0004029881,0.0006141185,9.31358e-05
anchor_abs_axes,"actual_anchor_score_final,abs_delta_vs_raw05_rawaxis,abs_bad_residual_axis_ratio,mean_abs_move_vs_raw05",1.0,0.0003588898,0.0004480914,0.0007086613,8.3334e-05
public_shape,"actual_anchor_score_final,abs_delta_vs_raw05_rawaxis,abs_bad_residual_axis_ratio,abs_ordinal_axis_ratio,prob_span",1.0,0.0004513379,0.000519643,0.0007581175,-0.0002407484
signed_axes,"delta_vs_raw05_rawaxis,bad_residual_axis_ratio,ordinal_axis_ratio,mean_abs_move_vs_raw05",1.0,0.0005823885,0.0007040258,0.0011182262,-9.0223e-06
```

## Main Read

- Scenarios per candidate: `4 models x 6 held-out anchors = 24`.
- `anchor_robust_delta_p90` and `anchor_robust_delta_max` are pessimistic raw05-relative diagnostics; lower is better.
- This still cannot prove a public gain, but it separates candidates that only win under one anchor fit from candidates whose local edge survives anchor removal.

## Raw Robust Top

```csv
file,rank,tier,anchor_robust_mean,anchor_robust_delta_mean,anchor_robust_delta_p90,anchor_robust_delta_max,anchor_robust_std,anchor_robust_spread,anchor_robust_beat_raw05_rate,anchor_robust_selection_score,available_raw05_relative_delta_vs_raw05_public,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,q3s4_motif_cos,q3s4_motif_orth_ratio,lejepa_residual_health
submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv,,,0.5775109084,-1.53988e-05,-4.7045e-06,-1.616e-06,1.31564e-05,5.20772e-05,1.0,-1.1688e-06,-5.4203e-06,0.5774590201,-8.67e-08,0.0004937317,,,
submission_raw05_jepa_public6drift_raw05_q1_s2_s3_follow_ones_prob_bad_raw_ortho_g00800_5534de7c.csv,,,0.5775248439,-1.4633e-06,-6.309e-07,-2.349e-07,8.408e-07,3.0209e-06,1.0,-4.141e-07,-7.358e-07,0.5775198693,-2.6e-09,0.0042935601,,,
submission_raw05_jepa_public6drift_raw05_q1_s3_follow_ones_prob_bad_raw_ortho_g01200_0c4050bf.csv,,,0.5775247269,-1.5803e-06,-5.952e-07,-2.21e-07,1.0051e-06,3.5292e-06,1.0,-3.385e-07,-6.953e-07,0.5775184858,2e-10,0.004275517,,,
submission_raw05_jepa_public6drift_raw05_q1_follow_ones_prob_bad_raw_ortho_g01200_470f4e4c.csv,,,0.577525559,-7.482e-07,-3.654e-07,-1.175e-07,3.801e-07,1.456e-06,1.0,-2.647e-07,-4.331e-07,0.5775194213,-1.9e-09,0.0045318523,,,
submission_raw05_jepa_public6drift_raw05_s3_follow_ones_prob_bad_raw_ortho_g01200_348b390d.csv,,,0.5775256309,-6.763e-07,-1.016e-07,8.22e-08,5.861e-07,2.0095e-06,0.9583333333,4.66e-08,-1.398e-07,0.5775244692,1.4e-09,0.0046495277,,,
submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_raw_ortho_g00075_0bbf9d04.csv,,,0.5775262565,-5.07e-08,2.5e-08,3.57e-08,1.147e-07,4.932e-07,0.5416666667,5.69e-08,2.31e-08,0.5775259879,0.0,0.0048444989,,,
submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_strength_prob_bad_raw_ortho_g00075_662099aa.csv,,,0.577526256,-5.12e-08,2.6e-08,3.76e-08,1.157e-07,4.966e-07,0.5416666667,5.83e-08,2.41e-08,0.5775259677,1e-10,0.0048442418,,,
submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_entropy_prob_bad_raw_ortho_g00100_acf7638d.csv,,,0.5775262408,-6.64e-08,3.15e-08,4.57e-08,1.5e-07,6.463e-07,0.5416666667,7.33e-08,2.93e-08,0.5775258878,1e-10,0.0048440665,,,
submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_raw_ortho_g00100_a6ce392e.csv,,,0.5775262395,-6.77e-08,3.33e-08,4.76e-08,1.529e-07,6.576e-07,0.5416666667,7.59e-08,3.07e-08,0.5775258815,0.0,0.0048446187,,,
submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_strength_prob_bad_raw_ortho_g00100_306226f5.csv,,,0.5775262718,-3.54e-08,6.93e-08,8.03e-08,1.577e-07,6.799e-07,0.3333333333,1.133e-07,6.63e-08,0.577525885,-1e-10,0.0048589137,,,
submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_raw_ortho_g00150_c968b72d.csv,,,0.5775262057,-1.015e-07,4.99e-08,7.14e-08,2.293e-07,9.864e-07,0.5416666667,1.139e-07,4.61e-08,0.5775256687,2e-10,0.0048448583,,,
submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_entropy_mid_prob_bad_raw_ortho_g00100_f22e587f.csv,,,0.5775262534,-5.38e-08,6.84e-08,8.2e-08,1.968e-07,8.563e-07,0.3333333333,1.236e-07,6.62e-08,0.577525873,-2e-10,0.0048567366,,,
submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_ones_prob_bad_raw_ortho_g00075_894a53ad.csv,,,0.577526241,-6.62e-08,6.52e-08,7.79e-08,2.212e-07,9.676e-07,0.2916666667,1.274e-07,6.33e-08,0.5775258627,-1e-10,0.0048563536,,,
submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_entropy_prob_bad_raw_ortho_g00150_76bed8db.csv,,,0.5775262506,-5.66e-08,9.03e-08,1.053e-07,2.277e-07,9.862e-07,0.3333333333,1.54e-07,8.66e-08,0.5775257629,-2e-10,0.0048628742,,,
submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_ones_prob_bad_raw_ortho_g00100_f3f65865.csv,,,0.5775262189,-8.83e-08,8.69e-08,1.039e-07,2.949e-07,1.2902e-06,0.2916666667,1.699e-07,8.44e-08,0.5775257147,-1e-10,0.004860425,,,
submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_strength_prob_bad_raw_ortho_g00150_033ab59a.csv,,,0.5775262541,-5.31e-08,1.039e-07,1.205e-07,2.366e-07,1.0198e-06,0.3333333333,1.7e-07,9.95e-08,0.5775256741,-1e-10,0.0048663008,,,
submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_entropy_mid_prob_bad_raw_ortho_g00150_c105c2bf.csv,,,0.5775262265,-8.07e-08,1.026e-07,1.231e-07,2.951e-07,1.2844e-06,0.3333333333,1.854e-07,9.94e-08,0.577525656,-1e-10,0.0048630352,,,
submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_entropy_prob_bad_raw_ortho_g00200_1e74fe02.csv,,,0.5775262318,-7.54e-08,1.203e-07,1.405e-07,3.036e-07,1.3149e-06,0.3333333333,2.053e-07,1.154e-07,0.5775255815,-1e-10,0.0048691191,,,
```

## Strict Structural Robust Top

```csv
file,rank,tier,constraint_family,shortlist_bucket,anchor_robust_mean,anchor_robust_delta_mean,anchor_robust_delta_p90,anchor_robust_delta_max,anchor_robust_std,anchor_robust_spread,anchor_robust_beat_raw05_rate,anchor_robust_selection_score,available_raw05_relative_delta_vs_raw05_public,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,q3s4_motif_cos,q3s4_motif_orth_ratio,lejepa_residual_health
submission_raw05_jepa_directcon_758a9f32.csv,,,other,strict_structural_robust,0.5775135242,-1.2783e-05,1.80838e-05,3.12551e-05,3.63301e-05,0.0001425996,0.5416666667,2.78113e-05,-3.9893e-06,0.576904911,9.84e-08,-9.96091e-05,1.0,0.0,
submission_raw05_jepa_directcon_6780a595.csv,,,other,strict_structural_robust,0.5775135245,-1.27827e-05,1.80876e-05,3.12591e-05,3.6329e-05,0.000142597,0.5416666667,2.78148e-05,-3.99e-06,0.5769048607,9.83e-08,-9.83262e-05,1.0,0.0,
submission_raw05_jepa_directcon_93aef33a.csv,,,other,strict_structural_robust,0.5775135246,-1.27826e-05,1.80878e-05,3.12599e-05,3.63299e-05,0.0001426011,0.5416666667,2.78153e-05,-3.9896e-06,0.5769048267,9.9e-08,-9.85415e-05,1.0,0.0,
submission_raw05_jepa_directcon_db07e01a.csv,,,other,strict_structural_robust,0.5775135257,-1.27815e-05,1.80901e-05,3.1264e-05,3.63295e-05,0.0001426038,0.5416666667,2.78177e-05,-3.9884e-06,0.5769049073,9.76e-08,-9.80074e-05,0.9999999624,0.0003750174,
submission_raw05_jepa_directcon_497545ea.csv,,,other,strict_structural_robust,0.577513526,-1.27812e-05,1.80939e-05,3.1268e-05,3.63284e-05,0.0001426012,0.5416666667,2.78212e-05,-3.9891e-06,0.5769048572,9.75e-08,-9.6739e-05,0.9999999624,0.0003748917,
submission_raw05_jepa_directcon_3cfd76d7.csv,,,other,strict_structural_robust,0.5775135261,-1.27811e-05,1.80941e-05,3.12688e-05,3.63293e-05,0.0001426053,0.5416666667,2.78216e-05,-3.9887e-06,0.5769048232,9.82e-08,-9.69545e-05,0.9999999624,0.0003746971,
submission_raw05_jepa_directcon_733e4345.csv,,,other,strict_structural_robust,0.5775135277,-1.27795e-05,1.8099e-05,3.12765e-05,3.63286e-05,0.0001426097,0.5416666667,2.78266e-05,-3.9872e-06,0.5769049022,9.66e-08,-9.5765e-05,0.9999997831,0.0008999389,
submission_raw05_jepa_directcon_ef209256.csv,,,other,strict_structural_robust,0.5775135285,-1.27787e-05,1.81002e-05,3.12802e-05,3.6332e-05,0.0001426257,0.5416666667,2.78288e-05,-3.9857e-06,0.5769047479,9.93e-08,-9.64895e-05,0.999999781,0.0009044205,
submission_raw05_jepa_directcon_4eaa2c45.csv,,,other,strict_structural_robust,0.5775135281,-1.27791e-05,1.81027e-05,3.12805e-05,3.63275e-05,0.000142607,0.5416666667,2.78301e-05,-3.9878e-06,0.5769048522,9.65e-08,-9.45169e-05,0.9999997833,0.0008996375,
submission_raw05_jepa_directcon_721f5393.csv,,,other,strict_structural_robust,0.5775135282,-1.2779e-05,1.81029e-05,3.12812e-05,3.63285e-05,0.0001426111,0.5416666667,2.78305e-05,-3.9874e-06,0.5769048183,9.72e-08,-9.47326e-05,0.9999997835,0.0008991705,
submission_raw05_jepa_directcon_48409823.csv,,,other,strict_structural_robust,0.5775135045,-1.28027e-05,1.81327e-05,3.13104e-05,3.63678e-05,0.0001428124,0.5416666667,2.78722e-05,-3.9913e-06,0.5769049214,9.96e-08,-8.52584e-05,0.9999997822,0.0009019093,
submission_raw05_jepa_directcon_2e7cbbfa.csv,,,other,strict_structural_robust,0.5775134821,-1.28251e-05,1.81244e-05,3.13006e-05,3.64098e-05,0.000143013,0.5416666667,2.78763e-05,-3.9891e-06,0.5769049284,9.74e-08,-8.80779e-05,1.0,0.0,
submission_raw05_jepa_directcon_4e3a83cd.csv,,,other,strict_structural_robust,0.5775134839,-1.28233e-05,1.8132e-05,3.13113e-05,3.6409e-05,0.0001430179,0.5416666667,2.78839e-05,-3.9882e-06,0.5769049158,9.66e-08,-8.61252e-05,0.9999999449,0.0004537348,
submission_raw05_jepa_directcon_2f880ea2.csv,,,other,strict_structural_robust,0.5775134934,-1.28138e-05,1.81426e-05,3.13246e-05,3.63972e-05,0.0001429701,0.5416666667,2.78912e-05,-3.9875e-06,0.5769049864,8.74e-08,-8.36141e-05,0.9999996852,0.0010843371,
submission_raw05_jepa_directcon_25495bdc.csv,,,other,strict_structural_robust,0.5775134856,-1.28216e-05,1.81414e-05,3.13166e-05,3.64059e-05,0.0001429907,0.5416666667,2.7892e-05,-3.9929e-06,0.5769049697,8.8e-08,-8.36231e-05,1.0,0.0,
submission_raw05_jepa_directcon_3d297f8a.csv,,,other,strict_structural_robust,0.5775134863,-1.28209e-05,1.81427e-05,3.13263e-05,3.64079e-05,0.0001430249,0.5416666667,2.78946e-05,-3.9869e-06,0.5769048982,9.56e-08,-8.33914e-05,0.9999996825,0.0010888294,
submission_raw05_jepa_directcon_1d7f766f.csv,,,other,strict_structural_robust,0.5775134869,-1.28203e-05,1.81483e-05,3.13259e-05,3.64045e-05,0.0001429929,0.5416666667,2.78988e-05,-3.9923e-06,0.5769049992,8.65e-08,-8.15819e-05,0.9999999449,0.0004537348,
submission_raw05_jepa_directcon_0871c1ed.csv,,,other,strict_structural_robust,0.5775134873,-1.28199e-05,1.8149e-05,3.13273e-05,3.64051e-05,0.0001429957,0.5416666667,2.78996e-05,-3.992e-06,0.5769049571,8.73e-08,-8.16704e-05,0.9999999449,0.0004537348,
```
