# JEPA Context-Target Compatibility Audit

This audit fits a train-label context->target block model: context = Q1/Q2/S1/S2/S3, target block = Q3/S4. Candidate submissions are scored by how compatible their Q3/S4 probabilities are with their own context block.

## Train CV

```csv
fold_type,folds,mean_model_loss,mean_baseline_loss,mean_delta,max_delta
date_interleave_5fold,5,0.6015007689,0.6812936003,-0.0797928314,-0.0471163722
leave_subject_out,10,0.6334993553,0.6910540832,-0.0575547279,0.0866467712
```

## Public-Anchor LOOCV With Compatibility Features

```csv
model,features,mae,rmse,max_abs_error,bias,spearman,kendall
axes_baseline,"abs_delta_vs_raw05_rawaxis,abs_bad_residual_axis_ratio,mean_abs_move_vs_raw05",0.0003184931,0.0004029881,0.0006141185,9.31358e-05,0.9428571429,0.8666666667
axes_plus_compat_abs,"abs_delta_vs_raw05_rawaxis,abs_bad_residual_axis_ratio,mean_abs_move_vs_raw05,abs_compat_kl_mean_delta_vs_raw05,abs_compat_abslogit_mean_delta_vs_raw05,abs_compat_block_kl_p90_mean_delta_vs_raw05",0.0003886953,0.0004499404,0.0007533589,8.77921e-05,0.7714285714,0.6
axes_plus_compat,"abs_delta_vs_raw05_rawaxis,abs_bad_residual_axis_ratio,mean_abs_move_vs_raw05,compat_kl_mean_delta_vs_raw05,compat_abslogit_mean_delta_vs_raw05,compat_block_kl_p90_mean_delta_vs_raw05",0.0010284398,0.0015208349,0.003249136,0.0008023112,0.6571428571,0.4666666667
compat_abs_only,"abs_compat_kl_mean_delta_vs_raw05,abs_compat_abslogit_mean_delta_vs_raw05,abs_compat_block_kl_p90_mean_delta_vs_raw05",0.0013070819,0.0016054307,0.0028024246,6.75194e-05,-0.9428571429,-0.8666666667
compat_only,"compat_kl_mean_delta_vs_raw05,compat_abslogit_mean_delta_vs_raw05,compat_block_kl_p90_mean_delta_vs_raw05",0.0013732485,0.0015380058,0.0027636462,0.0001253404,-0.6571428571,-0.6
```

## Known Public Predictions

```csv
file,known_public,axes_baseline,axes_baseline_error,compat_only,compat_only_error,compat_abs_only,compat_abs_only_error,axes_plus_compat,axes_plus_compat_error,axes_plus_compat_abs,axes_plus_compat_abs_error
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.5775263072,0.5781404257,0.0006141185,0.5790820684,0.0015557612,0.5796285859,0.0021022787,0.5781190033,0.0005926961,0.5780934362,0.000567129
submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,0.5779449757,0.5779489565,3.9808e-06,0.5790522042,0.0011072285,0.5793618198,0.0014168441,0.577934185,-1.07907e-05,0.5780539501,0.0001089744
submission_jepa_latent_q2_w0p45.csv,0.5798012862,0.5795593249,-0.0002419613,0.5788212081,-0.0009800781,0.5788850232,-0.000916263,0.5795738176,-0.0002274686,0.5796262684,-0.0001750178
submission_jepa_latent_residual_probe.csv,0.5812273278,0.5807932173,-0.0004341105,0.5784636816,-0.0027636462,0.5784249032,-0.0028024246,0.5807872011,-0.0004401267,0.5807680385,-0.0004592893
submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,0.5783033652,0.5783288911,2.55259e-05,0.5788532878,0.0005499226,0.5788898564,0.0005864912,0.5799537863,0.0016504211,0.5780349626,-0.0002684026
submission_hybrid_0p578_logit_after_subject_final9_strict.csv,0.5784273528,0.5790186143,0.0005912615,0.5797102072,0.0012828544,0.5784455426,1.81898e-05,0.5816764888,0.003249136,0.5791807117,0.0007533589
```

## Current Candidate Compatibility Ranking

```csv
file,rank,tier,compat_kl_mean_delta_vs_raw05,compat_abslogit_mean_delta_vs_raw05,compat_block_kl_p90_mean_delta_vs_raw05,raw05_relative_lb_proxy_mean,actual_anchor_score_final,bad_residual_axis_ratio,lejepa_residual_health
submission_jepa_block_consensus_rawcorr_micro_9ec2b75e.csv,22.0,A-balanced,-0.000890228,-0.0058356732,-0.001521527,0.5775296738,0.5778425462,0.0020110237,10.1388826218
submission_jepa_block_consensus_rawcorr_micro_fea06910.csv,23.0,A-strict,-0.000883129,-0.0057929565,-0.0015099201,0.5775296684,0.577842874,0.0020232423,9.4567074851
submission_jepa_block_consensus_rawcorr_4fd8bab2.csv,24.0,B-stable,-0.000871475,-0.0057530504,-0.0014870547,0.5775295094,0.577843875,0.001843945,9.5582824046
submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv,25.0,B-refine,-0.0008597221,-0.005651509,-0.0014753604,0.577529474,0.5778431742,0.0020438107,9.9924139753
submission_jepa_micro_bridge_ensemble_5ffa44a8.csv,21.0,A-aggressive,-0.0008093838,-0.0053118193,-0.0014003449,0.5775291389,0.5778425183,0.002379415,9.5914024333
submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,32.0,known-public-control,-0.0007553183,-0.0011942574,-0.0012344061,0.5776262549,0.5779449757,0.0,6.6661026595
submission_raw05_jepa_efgate_ac60a2e6.csv,16.0,A-gate-posterior-lowbad,-0.0007327066,-0.0050172547,-0.0012624383,0.5775236659,0.5778402624,0.0002444987,10.1095782243
submission_raw05_jepa_siggate_78179445.csv,14.0,A-siggate-health,-0.0007324489,-0.0050148949,-0.0012617405,0.5775231707,0.5778403527,2.64961e-05,10.0187457008
submission_raw05_jepa_efgate_d592970e.csv,17.0,A-gate-ultralowbad,-0.0007324124,-0.0050143011,-0.0012622073,0.577523201,0.5778403876,5.05423e-05,10.0522245081
submission_raw05_jepa_siggate_fd0e9622.csv,12.0,A-siggate-stable-best,-0.0007324014,-0.0050144371,-0.0012612289,0.5775231268,0.5778400704,2.16597e-05,9.8712455935
submission_raw05_jepa_siggate_6d681440.csv,15.0,A-siggate-ultralowbad,-0.000732399,-0.0050147043,-0.0012614388,0.5775231116,0.5778401881,6.6045e-06,11.5145093631
submission_raw05_jepa_efback_9c50051c.csv,11.0,A-backoff-ultralowbad,-0.0007323697,-0.0050141272,-0.0012615945,0.5775231819,0.5778403391,3.23388e-05,10.794055807
submission_raw05_jepa_siggate_64220cc6.csv,13.0,A-siggate-health-lowbad,-0.0007323476,-0.0050142074,-0.0012612952,0.5775231487,0.5778401865,2.505e-05,10.4400843385
submission_raw05_jepa_efback_cc265f32.csv,10.0,A-backoff-risknone,-0.0007317976,-0.0050082833,-0.0012604452,0.5775239227,0.5778396907,0.0004185961,10.4704764053
submission_raw05_jepa_efmicro_3eece507.csv,2.0,A-micro,-0.0007315595,-0.0050034816,-0.001259591,0.577523804,0.5778387644,0.0004950061,9.8573923652
submission_raw05_jepa_energyfront_a190aa25.csv,1.0,A-frontier,-0.0007314558,-0.0050022775,-0.0012588901,0.5775244922,0.5778387145,0.0008568227,10.8535798753
submission_raw05_jepa_siganchor_3644a42f.csv,8.0,A-siganchor-health-lowbad,-0.0007309179,-0.0050016624,-0.0012584034,0.5775237681,0.5778390951,0.0003999823,9.6842205537
submission_raw05_jepa_efmicro_9f19106d.csv,6.0,A-micro-lowbad,-0.0007308971,-0.0049994771,-0.0012577259,0.5775237176,0.5778389482,0.0004203752,9.4663681336
submission_raw05_jepa_siganchor_882fa552.csv,9.0,A-siganchor-compromise,-0.0007308327,-0.0050005686,-0.0012583488,0.5775238191,0.5778390518,0.0004298864,10.5242869958
submission_raw05_jepa_efmicro_9e631d75.csv,7.0,A-micro-health,-0.000730797,-0.0049993409,-0.001258241,0.5775238482,0.5778389358,0.000452394,10.0068919524
submission_raw05_jepa_efmicro_f88f2cec.csv,4.0,A-micro-posterior,-0.0007307877,-0.004999321,-0.0012581309,0.577523844,0.5778389013,0.0004482097,10.6054920367
submission_raw05_jepa_efmicro_5d2d2af0.csv,5.0,A-micro-sigreg-best,-0.0007306921,-0.0049987579,-0.0012580303,0.5775238839,0.5778388931,0.0004650958,9.8721137927
submission_raw05_jepa_energyfront_0f7e85a0.csv,20.0,A-strict,-0.0007305506,-0.0049956204,-0.0012571218,0.5775244571,0.5778398077,0.000815186,10.420331605
submission_raw05_jepa_energyfront_ea665780.csv,19.0,A-lowbad,-0.0007304414,-0.0049954104,-0.0012564677,0.5775243802,0.577839486,0.000762406,10.9021164046
```
