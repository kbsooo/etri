# Raw05 JEPA Public6 Drift Microperturb

This keeps the six-anchor public-LB posterior as a direction oracle only. Most direct posterior candidates are unsafe because of held-out-anchor error or bad-axis movement, so the generated candidates use very small row-gated moves around raw05-compatible JEPA bases.

## Projection Fit

```csv
prior,prior_file,projection_converged,projection_max_abs_residual,projection_mean_abs_move,expected_anchor578,expected_stage2,expected_ordinal,expected_raw05,expected_latent_q2,expected_latent_resid
compatband,submission_raw05_jepa_compatband_e065e98e.csv,True,0.0,0.0172103669,0.5784273528,0.5779449757,0.5783033652,0.5775263072,0.5798012862,0.5812273278
efmicro5,submission_raw05_jepa_efmicro_5d2d2af0.csv,True,0.0,0.0172104622,0.5784273528,0.5779449757,0.5783033652,0.5775263072,0.5798012862,0.5812273278
efmicro3,submission_raw05_jepa_efmicro_3eece507.csv,True,0.0,0.0172109717,0.5784273528,0.5779449757,0.5783033652,0.5775263072,0.5798012862,0.5812273278
energyfront,submission_raw05_jepa_energyfront_a190aa25.csv,True,0.0,0.017216935,0.5784273528,0.5779449757,0.5783033652,0.5775263072,0.5798012862,0.5812273278
siggate,submission_raw05_jepa_siggate_6d681440.csv,True,0.0,0.0172194533,0.5784273528,0.5779449757,0.5783033652,0.5775263072,0.5798012862,0.5812273278
raw05,submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,True,0.0,0.0181051323,0.5784273528,0.5779449757,0.5783033652,0.5775263072,0.5798012862,0.5812273278
```

## Orientation Summary

```csv
orientation,n,best_posterior,best_abs_raw,best_abs_bad,strict_count
anti,4968,0.5768861748,0.0,2.64e-08,3809
follow,5400,0.5768817945,2e-10,5.792e-07,3400
```

## Top Strict Shortlist

```csv
file,prior,target_mask,orientation,gamma,gate,mode,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,mean_abs_move_vs_raw05,candidate_mean_abs_move_vs_prior,mean_target_delta_Q1,mean_target_delta_S3
submission_raw05_jepa_public6drift_siggate_q1_follow_entropy_mid_prob_bad_raw_ortho_g00300_4d723b2a.csv,siggate,q1,follow,0.003,entropy_mid,prob_bad_raw_ortho,0.5768930562,9.72e-08,-5.55437e-05,0.0014941379,4.4592e-06,-3.12143e-05,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_entropy_mid_prob_bad_raw_ortho_g00400_d6157e7e.csv,siggate,q1,follow,0.004,entropy_mid,prob_bad_raw_ortho,0.5768927362,9.8e-08,-7.62597e-05,0.0014946991,5.9456e-06,-4.1619e-05,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_entropy_mid_prob_bad_raw_ortho_g00200_fb9a3966.csv,siggate,q1,follow,0.002,entropy_mid,prob_bad_raw_ortho,0.5768933763,9.67e-08,-3.48276e-05,0.0014935799,2.9728e-06,-2.08095e-05,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_entropy_mid_prob_bad_raw_ortho_g00150_ad251077.csv,siggate,q1,follow,0.0015,entropy_mid,prob_bad_raw_ortho,0.5768935364,9.64e-08,-2.44696e-05,0.0014933146,2.2296e-06,-1.56071e-05,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_ones_prob_bad_raw_ortho_g00200_abed577b.csv,siggate,q1,follow,0.002,ones,prob_bad_raw_ortho,0.576893266,9.72e-08,-3.97265e-05,0.0014938417,3.6938e-06,-2.58564e-05,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_ones_prob_bad_raw_ortho_g00150_90e167c8.csv,siggate,q1,follow,0.0015,ones,prob_bad_raw_ortho,0.5768934537,9.68e-08,-2.81438e-05,0.0014935108,2.7703e-06,-1.93923e-05,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_ones_prob_bad_raw_ortho_g00300_88a7a70e.csv,siggate,q1,follow,0.003,ones,prob_bad_raw_ortho,0.576892891,9.81e-08,-6.2892e-05,0.001494536,5.5406e-06,-3.87845e-05,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_entropy_mid_prob_bad_raw_ortho_g00100_5e9abec0.csv,siggate,q1,follow,0.001,entropy_mid,prob_bad_raw_ortho,0.5768936966,9.62e-08,-1.41115e-05,0.0014930695,1.4864e-06,-1.04048e-05,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_ones_prob_bad_raw_ortho_g00100_75fa7695.csv,siggate,q1,follow,0.001,ones,prob_bad_raw_ortho,0.5768936414,9.65e-08,-1.6561e-05,0.0014932003,1.8469e-06,-1.29282e-05,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_entropy_mid_prob_bad_raw_ortho_g00075_95238b56.csv,siggate,q1,follow,0.00075,entropy_mid,prob_bad_raw_ortho,0.5768937767,9.62e-08,-8.9325e-06,0.001492947,1.1148e-06,-7.8036e-06,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_entropy_mid_prob_bad_raw_ortho_g00600_cb961548.csv,siggate,q1,follow,0.006,entropy_mid,prob_bad_raw_ortho,0.576892097,1.001e-07,-0.0001176918,0.0014958592,8.9184e-06,-6.24286e-05,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_ones_prob_bad_raw_ortho_g00075_893ab57f.csv,siggate,q1,follow,0.00075,ones,prob_bad_raw_ortho,0.5768937353,9.63e-08,-1.07696e-05,0.0014930451,1.3852e-06,-9.6961e-06,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_ones_prob_bad_raw_ortho_g00400_c19c0b57.csv,siggate,q1,follow,0.004,ones,prob_bad_raw_ortho,0.5768925162,9.93e-08,-8.60575e-05,0.0014952333,7.3875e-06,-5.17127e-05,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_signed_entropy_prob_bad_raw_ortho_g00150_3e0f1c63.csv,siggate,q1,follow,0.0015,signed_entropy,prob_bad_raw_ortho,0.5768935958,9.68e-08,-2.49893e-05,0.0014931772,1.8632e-06,-1.30422e-05,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_signed_entropy_prob_bad_raw_ortho_g00200_c9829313.csv,siggate,q1,follow,0.002,signed_entropy,prob_bad_raw_ortho,0.5768934554,9.71e-08,-3.55206e-05,0.0014933972,2.4842e-06,-1.73897e-05,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_signed_entropy_prob_bad_raw_ortho_g00100_d8f5a8b7.csv,siggate,q1,follow,0.001,signed_entropy,prob_bad_raw_ortho,0.5768937362,9.65e-08,-1.4458e-05,0.0014929779,1.2421e-06,-8.6948e-06,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_signed_entropy_prob_bad_raw_ortho_g00075_bec40169.csv,siggate,q1,follow,0.00075,signed_entropy,prob_bad_raw_ortho,0.5768938064,9.64e-08,-9.1924e-06,0.0014928783,9.316e-07,-6.5211e-06,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_signed_strength_prob_bad_raw_ortho_g00075_62d3a3df.csv,siggate,q1,follow,0.00075,signed_strength,prob_bad_raw_ortho,0.5768937884,9.65e-08,-1.01296e-05,0.0014928965,1.0034e-06,-7.0236e-06,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_signed_strength_prob_bad_raw_ortho_g00100_c0e50dd2.csv,siggate,q1,follow,0.001,signed_strength,prob_bad_raw_ortho,0.5768937121,9.67e-08,-1.57077e-05,0.0014930022,1.3378e-06,-9.3648e-06,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_signed_strength_prob_bad_raw_ortho_g00150_cf244190.csv,siggate,q1,follow,0.0015,signed_strength,prob_bad_raw_ortho,0.5768935597,9.71e-08,-2.68638e-05,0.0014932136,2.0067e-06,-1.40471e-05,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_signed_entropy_prob_bad_raw_ortho_g00300_1f16122f.csv,siggate,q1,follow,0.003,signed_entropy,prob_bad_raw_ortho,0.5768931748,9.79e-08,-5.65831e-05,0.0014938638,3.7264e-06,-2.60845e-05,0.0
submission_raw05_jepa_public6drift_siggate_q1_follow_signed_top40_prob_bad_raw_ortho_g00075_89d3bdea.csv,siggate,q1,follow,0.00075,signed_top40,prob_bad_raw_ortho,0.576893787,9.66e-08,-1.07311e-05,0.0014928886,9.85e-07,-6.8948e-06,0.0
submission_raw05_jepa_public6drift_energyfront_q1_follow_entropy_mid_prob_bad_raw_ortho_g00400_822dcfe6.csv,energyfront,q1,follow,0.004,entropy_mid,prob_bad_raw_ortho,0.5769022749,7.34e-08,0.0007735931,0.0014886136,5.944e-06,-4.16078e-05,0.0
submission_raw05_jepa_public6drift_siggate_s3_anti_signed_entropy_prob_bad_raw_ortho_g00075_0ac6f42c.csv,siggate,s3,anti,0.00075,signed_entropy,prob_bad_raw_ortho,0.5768939977,9.61e-08,6.9145e-06,0.0014926468,1.429e-07,0.0,-1.0001e-06
submission_raw05_jepa_public6drift_siggate_s3_anti_signed_entropy_prob_bad_raw_ortho_g00100_98fa9a30.csv,siggate,s3,anti,0.001,signed_entropy,prob_bad_raw_ortho,0.5768939912,9.61e-08,7.0178e-06,0.0014926693,1.905e-07,0.0,-1.3334e-06
submission_raw05_jepa_public6drift_siggate_s3_anti_entropy_mid_prob_bad_raw_ortho_g00075_44a6b7b2.csv,siggate,s3,anti,0.00075,entropy_mid,prob_bad_raw_ortho,0.5768939969,9.61e-08,6.9374e-06,0.0014926524,1.669e-07,0.0,-1.1685e-06
submission_raw05_jepa_public6drift_siggate_s3_anti_signed_entropy_prob_bad_raw_ortho_g00150_f0c9e649.csv,siggate,s3,anti,0.0015,signed_entropy,prob_bad_raw_ortho,0.5768939782,9.61e-08,7.2244e-06,0.0014927143,2.857e-07,0.0,-2.0001e-06
submission_raw05_jepa_public6drift_siggate_s3_anti_entropy_mid_prob_bad_raw_ortho_g00100_e0018490.csv,siggate,s3,anti,0.001,entropy_mid,prob_bad_raw_ortho,0.5768939902,9.61e-08,7.0483e-06,0.0014926767,2.226e-07,0.0,-1.5581e-06
submission_raw05_jepa_public6drift_siggate_s3_anti_signed_entropy_prob_bad_raw_ortho_g00200_a74501fe.csv,siggate,s3,anti,0.002,signed_entropy,prob_bad_raw_ortho,0.5768939653,9.61e-08,7.4311e-06,0.0014927593,3.81e-07,0.0,-2.6668e-06
submission_raw05_jepa_public6drift_siggate_s3_anti_entropy_mid_prob_bad_raw_ortho_g00150_53f1fd14.csv,siggate,s3,anti,0.0015,entropy_mid,prob_bad_raw_ortho,0.5768939767,9.61e-08,7.2702e-06,0.0014927255,3.339e-07,0.0,-2.3371e-06
```

## Decision Rule

- Treat `follow` as the public6 drift hypothesis: Q1/Q3 down, S2/S3 up.
- Treat `anti` as a local-proxy falsification control.
- Candidates are only worth submitting if the local LB proxy keeps them raw05-relative competitive after the separate validation script reruns.
