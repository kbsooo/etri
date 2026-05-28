# Raw05 JEPA Block-Count Regularized Refine

Mix raw05-compatible A-family residuals with JEPA block-count residuals. The count direction is tested as a small additive residual, centered hidden-block residual, pull-to-count prior, and sign-flipped control.

## Counts

- generated candidates: `157497`
- actual-anchor scored candidates: `1598`
- saved shortlist: `24`

## Mode Summary

```csv
mode,profile,n,best_actual,best_selection,best_bad_abs,best_raw
center_add,q3_sblock_tiny,206,0.577839683,0.5778399281,8.19e-08,8.36e-08
anti_count,q3_only,80,0.5778399515,0.5778399515,1.5903e-06,9.3e-08
anti_count,q3_s4_tiny,93,0.5778399749,0.5778399749,1.0728e-06,8.63e-08
anti_count,q3_sblock_tiny,134,0.5778399889,0.5778399889,2.394e-07,8e-08
center_add,q3_s4_tiny,131,0.5778400916,0.5778400916,2.3231e-06,8.22e-08
center_add,q3_only,81,0.5778400588,0.5778403633,1.1246e-06,8.75e-08
add_count,q3_s4_tiny,30,0.5778401109,0.5778403795,2.8094e-06,9.93e-08
add_count,q3_sblock_tiny,42,0.577840114,0.5778405865,1.6545e-06,9.36e-08
add_count,q3_only,15,0.5778403705,0.5778405895,7.8252e-06,1.008e-07
pull_count,q3_sblock_tiny,343,0.5778406358,0.5778406358,9.779e-07,-6.559e-07
pull_count,q3_only,189,0.5778409459,0.5778409459,1.58491e-05,-5.97e-07
pull_count,q3_s4_tiny,254,0.5778409866,0.5778409866,8.6766e-06,-6.487e-07
```

## Shortlist

```csv
file,bucket,base_file,block_file,mode,profile,gate,strength,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,mean_abs_move_vs_base,mean_abs_move_vs_raw05,selection_score,rank_score
submission_raw05_jepa_blockcountreg_effc86de.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_780f8874.csv,submission_jepa_block_countshift_57eb123e.csv,center_add,q3_s4_tiny,disagree_floor20,0.22,0.5778408142,0.576885484,9.31e-08,5.0216e-06,2.19011e-05,0.0015020048,0.5778408142,450.42
submission_raw05_jepa_blockcountreg_78c6c099.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_780f8874.csv,submission_jepa_block_countshift_57eb123e.csv,center_add,q3_sblock_tiny,disagree_floor20,0.22,0.5778408437,0.5768841001,9.53e-08,1.14239e-05,2.44655e-05,0.0015034829,0.5778408437,461.22
submission_raw05_jepa_blockcountreg_50b1cf4a.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_780f8874.csv,submission_jepa_block_countshift_57eb123e.csv,anti_count,q3_sblock_tiny,disagree_floor20,-0.18,0.577840724,0.5768860585,9e-08,9.1893e-06,2.00171e-05,0.0015012791,0.577840724,461.8
submission_raw05_jepa_blockcountreg_11801b21.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_986d2791.csv,submission_jepa_block_countshift_57eb123e.csv,anti_count,q3_sblock_tiny,disagree_floor20,-0.18,0.5778407428,0.5768858155,9.15e-08,1.37416e-05,2.00171e-05,0.0015010733,0.5778407428,464.56
submission_raw05_jepa_blockcountreg_6aea2352.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_986d2791.csv,submission_jepa_block_countshift_57eb123e.csv,center_add,q3_s4_tiny,disagree_floor20,0.22,0.577840833,0.576885241,9.47e-08,9.574e-06,2.19011e-05,0.0015017972,0.577840833,476.64
submission_raw05_jepa_blockcountreg_ea5cccf1.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_986d2791.csv,submission_jepa_block_countshift_57eb123e.csv,center_add,q3_sblock_tiny,disagree_floor20,0.22,0.5778408625,0.5768838572,9.68e-08,1.59762e-05,2.44655e-05,0.0015032767,0.5778408625,479.94
submission_raw05_jepa_blockcountreg_af8b5e47.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_6d681440.csv,submission_jepa_block_countshift_57eb123e.csv,anti_count,q3_sblock_tiny,disagree_floor20,-0.18,0.5778407155,0.5768851933,1.087e-07,1.66506e-05,2.00172e-05,0.0015006127,0.5778432474,482.62
submission_raw05_jepa_blockcountreg_ead49223.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_fd0e9622.csv,submission_jepa_block_countshift_57eb123e.csv,anti_count,q3_sblock_tiny,disagree_floor20,-0.18,0.5778405991,0.5768858072,1.104e-07,3.16819e-05,2.00337e-05,0.0015012294,0.5778436232,489.48
submission_raw05_jepa_blockcountreg_236410c1.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_986d2791.csv,submission_jepa_block_countshift_57eb123e.csv,center_add,q3_only,disagree_floor20,0.22,0.5778407815,0.5768863387,1.028e-07,1.1246e-06,1.87575e-05,0.0014995719,0.5778415952,500.06
submission_raw05_jepa_blockcountreg_5b37b47d.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_78179445.csv,submission_jepa_block_countshift_57eb123e.csv,add_count,q3_sblock_tiny,disagree_floor20,0.14,0.5778407719,0.5768858313,1.108e-07,-1.6545e-06,1.56037e-05,0.0014975071,0.5778439132,505.46
submission_raw05_jepa_blockcountreg_2bff1b8c.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_780f8874.csv,submission_jepa_block_countshift_57eb123e.csv,center_add,q3_only,disagree_floor20,0.22,0.5778407627,0.5768865817,1.012e-07,-3.4278e-06,1.87575e-05,0.0014997798,0.577841125,507.18
submission_raw05_jepa_blockcountreg_69e744f6.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_6d681440.csv,submission_jepa_block_countshift_57eb123e.csv,center_add,q3_s4_tiny,disagree_floor20,0.22,0.5778408058,0.5768846189,1.12e-07,1.24834e-05,2.19012e-05,0.0015013336,0.5778442793,507.72
submission_raw05_jepa_blockcountreg_2555a247.csv,blockreg_rank_fallback,submission_raw05_jepa_efback_9c50051c.csv,submission_jepa_block_countshift_57eb123e.csv,add_count,q3_sblock_tiny,disagree_floor20,0.14,0.5778407583,0.5768860948,1.083e-07,4.1882e-06,1.56037e-05,0.0014976671,0.5778431794,509.64
submission_raw05_jepa_blockcountreg_e9ef3b34.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_64220cc6.csv,submission_jepa_block_countshift_57eb123e.csv,anti_count,q3_sblock_tiny,disagree_floor20,-0.18,0.5778407139,0.5768851181,1.073e-07,3.50961e-05,2.00172e-05,0.0015006611,0.5778428309,510.02
submission_raw05_jepa_blockcountreg_3bbbf347.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_6d681440.csv,submission_jepa_block_countshift_57eb123e.csv,center_add,q3_sblock_tiny,disagree_floor20,0.14,0.5778405967,0.5768871525,1.043e-07,1.44167e-05,1.55689e-05,0.0014985359,0.5778418294,511.4
submission_raw05_jepa_blockcountreg_eab183ca.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_6d681440.csv,submission_jepa_block_countshift_57eb123e.csv,anti_count,q3_s4_tiny,disagree_floor20,-0.18,0.5778406914,0.5768863255,1.07e-07,1.14126e-05,1.79191e-05,0.0014994049,0.5778427097,514.04
submission_raw05_jepa_blockcountreg_ae57c927.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_780f8874.csv,submission_jepa_block_countshift_57eb123e.csv,anti_count,q3_s4_tiny,disagree_floor20,-0.18,0.5778406999,0.5768871907,8.82e-08,3.9511e-06,1.7919e-05,0.001500074,0.5778406999,514.8
submission_raw05_jepa_blockcountreg_995c5b77.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_fd0e9622.csv,submission_jepa_block_countshift_57eb123e.csv,center_add,q3_sblock_tiny,disagree_floor20,0.22,0.577840719,0.5768838431,1.158e-07,3.39114e-05,2.44857e-05,0.0015034347,0.5778452982,517.34
submission_raw05_jepa_blockcountreg_7c6871a6.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_780f8874.csv,submission_jepa_block_countshift_57eb123e.csv,center_add,q3_s4_tiny,disagree_floor20,0.14,0.5778405865,0.5768888984,8.42e-08,2.8814e-06,1.3937e-05,0.0014982738,0.5778405865,517.54
submission_raw05_jepa_blockcountreg_0792baba.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_780f8874.csv,submission_jepa_block_countshift_57eb123e.csv,center_add,q3_sblock_tiny,disagree_floor20,0.14,0.5778406052,0.5768880178,8.56e-08,6.9556e-06,1.55688e-05,0.0014992085,0.5778406052,519.2
submission_raw05_jepa_blockcountreg_99450805.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_fd0e9622.csv,submission_jepa_block_countshift_57eb123e.csv,center_add,q3_s4_tiny,disagree_floor20,0.22,0.577840689,0.5768852591,1.14e-07,2.75385e-05,2.19012e-05,0.0015019451,0.577844736,521.0
submission_raw05_jepa_blockcountreg_45d79347.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_986d2791.csv,submission_jepa_block_countshift_57eb123e.csv,anti_count,q3_s4_tiny,disagree_floor20,-0.18,0.5778407187,0.5768869478,8.97e-08,8.5034e-06,1.7919e-05,0.0014998667,0.5778407187,524.1
submission_raw05_jepa_blockcountreg_68d23883.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_6d681440.csv,submission_jepa_block_countshift_57eb123e.csv,anti_count,q3_sblock_tiny,disagree_floor20,-0.1,0.5778404787,0.5768891126,1.007e-07,1.21836e-05,1.11206e-05,0.0014966003,0.5778406862,524.36
submission_raw05_jepa_blockcountreg_263ddc2f.csv,blockreg_rank_fallback,submission_raw05_jepa_siggate_986d2791.csv,submission_jepa_block_countshift_57eb123e.csv,center_add,q3_only,disagree_floor20,0.14,0.5778405726,0.5768893541,9.1e-08,2.0568e-06,1.19365e-05,0.0014966792,0.5778405726,526.06
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_jepa_blockcountreg_effc86de.csv,250,True,0,0,0.0631656533,0.9798268724
submission_raw05_jepa_blockcountreg_78c6c099.csv,250,True,0,0,0.0631656533,0.9798255358
submission_raw05_jepa_blockcountreg_50b1cf4a.csv,250,True,0,0,0.0631656533,0.9798257789
submission_raw05_jepa_blockcountreg_11801b21.csv,250,True,0,0,0.0631645236,0.9798257313
submission_raw05_jepa_blockcountreg_6aea2352.csv,250,True,0,0,0.0631645236,0.9798268248
submission_raw05_jepa_blockcountreg_ea5cccf1.csv,250,True,0,0,0.0631645236,0.9798254883
submission_raw05_jepa_blockcountreg_af8b5e47.csv,250,True,0,0,0.0631621992,0.9798258887
submission_raw05_jepa_blockcountreg_ead49223.csv,250,True,0,0,0.0631638509,0.9798260304
submission_raw05_jepa_blockcountreg_236410c1.csv,250,True,0,0,0.0631645236,0.9798268248
submission_raw05_jepa_blockcountreg_5b37b47d.csv,250,True,0,0,0.0631581181,0.9798255992
submission_raw05_jepa_blockcountreg_2bff1b8c.csv,250,True,0,0,0.0631656533,0.9798268724
submission_raw05_jepa_blockcountreg_69e744f6.csv,250,True,0,0,0.0631621992,0.9798269822
submission_raw05_jepa_blockcountreg_2555a247.csv,250,True,0,0,0.0631574553,0.9798256625
submission_raw05_jepa_blockcountreg_e9ef3b34.csv,250,True,0,0,0.063161515,0.9798258208
submission_raw05_jepa_blockcountreg_3bbbf347.csv,250,True,0,0,0.0631621992,0.9798261317
submission_raw05_jepa_blockcountreg_eab183ca.csv,250,True,0,0,0.0631621992,0.9798269822
submission_raw05_jepa_blockcountreg_ae57c927.csv,250,True,0,0,0.0631656533,0.9798268724
submission_raw05_jepa_blockcountreg_995c5b77.csv,250,True,0,0,0.0631638509,0.9798257874
submission_raw05_jepa_blockcountreg_7c6871a6.csv,250,True,0,0,0.0631656533,0.9798268724
submission_raw05_jepa_blockcountreg_0792baba.csv,250,True,0,0,0.0631656533,0.9798260219
submission_raw05_jepa_blockcountreg_99450805.csv,250,True,0,0,0.0631638509,0.9798271239
submission_raw05_jepa_blockcountreg_45d79347.csv,250,True,0,0,0.0631645236,0.9798268248
submission_raw05_jepa_blockcountreg_68d23883.csv,250,True,0,0,0.0631621992,0.9798263747
submission_raw05_jepa_blockcountreg_263ddc2f.csv,250,True,0,0,0.0631645236,0.9798268248
```
