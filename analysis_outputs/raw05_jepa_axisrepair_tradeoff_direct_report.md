# Raw05 JEPA Axisrepair Direct Tradeoff Search

Directly optimizes the posterior-safe versus target-motif-retention tradeoff. The main goal is `target_motif_retention >= 0.70`, `posterior <= 0.57691`, and raw-axis drift at or below the raw05 boundary.

## Counts

- generated candidates: `15622`
- actual-anchor scored candidates: `2424`
- saved shortlist: `84`
- pre-score goal hits: `n/a`
- scored goal hits: `1200`

## Profile Summary

```csv
mode,profile,n,goal_hits,best_actual,best_posterior,max_retention,best_selection,best_raw_abs,best_bad_abs
compensated_inject,q3s4+ctx_q1q2s123,709,421,0.5778296612,0.5766832498,0.96,0.5778394715,2.1e-09,1.72224e-05
compensated_inject,q3_s4half+ctx_q1q2s123,465,362,0.5778346347,0.5766846659,0.8708755829,0.5778393166,6.5e-09,3.872e-07
highret_inject,q3s4,340,117,0.5778276446,0.5766706841,1.18,0.5778728681,4.8e-09,1.2888e-06
soft_axis_repair,soft_sblock_q3_08,113,83,0.5778294356,0.5768262476,2.5514187188,0.5778294356,1.71e-08,1.7532e-05
highret_inject,q3_s4half,229,72,0.5778667044,0.5766765,1.0704512373,0.5778725387,5.8e-09,0.0002102246
highret_inject,q3_sblockmicro,218,48,0.5778320458,0.5766786599,1.0375866084,0.5778416011,1.77e-08,0.0002928012
soft_axis_repair,soft_ctx_q3s4_12,129,47,0.5778272369,0.5768004573,2.5507875294,0.57782893,3.58e-08,7.6365e-06
soft_axis_repair,soft_ctx_q3s4_05,99,30,0.5778250251,0.57680629,2.6357239006,0.577828341,1.66e-08,3.5079e-06
highret_inject,q3_only,122,20,0.5778654827,0.5766710083,0.9609024745,0.5778747908,4.62e-08,0.0003255801
```

## Shortlist

```csv
file,bucket,mode,axis_file,donor_file,comp_file,profile,gate_mode,beta,alpha,max_step,target_motif_retention,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,mean_abs_move_vs_donor,mean_abs_move_vs_raw05,selection_score,rank_score
submission_raw05_jepa_axistrade_931a03a1.csv,tradeoff_goal_hit,soft_axis_repair,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_block_consensus_rawcorr_4fd8bab2.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,1.0976474117,0.5778285208,0.5769045731,-1.66e-08,6.04807e-05,0.0003606046,0.001598228,0.5778285208,671.2
submission_raw05_jepa_axistrade_b8172c33.csv,tradeoff_goal_hit,soft_axis_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_block_consensus_rawcorr_4fd8bab2.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,1.0948970226,0.577828341,0.5769043977,4.08e-08,6.25522e-05,0.0003619124,0.0015996531,0.577828341,690.68
submission_raw05_jepa_axistrade_183834e5.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,submission_jepa_bridge_ensemble_c42fbf1e.csv,q3s4+ctx_q1q2s123,none,0.96,0.32,0.055,0.96,0.5778702517,0.5766948912,2.87e-08,0.0005592783,0.0002843809,0.0015607086,0.5778702517,693.04
submission_raw05_jepa_axistrade_329350af.csv,tradeoff_goal_hit,soft_axis_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_block_consensus_rawcorr_4fd8bab2.csv,,soft_ctx_q3s4_12,none,,0.45,0.055,1.0596138961,0.57782893,0.5769053303,-3.58e-08,0.0001035955,0.0003550482,0.0015966077,0.57782893,700.5
submission_raw05_jepa_axistrade_4556271c.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,submission_jepa_bridge_posteriorreg_9c5e225e.csv,q3s4+ctx_q1q2s123,none,0.96,0.32,0.055,0.96,0.5778705155,0.5766897856,7.1e-08,0.0005408538,0.0002825805,0.0015650157,0.5778705155,701.7
submission_raw05_jepa_axistrade_c4caf7e5.csv,tradeoff_rank_fallback,soft_axis_repair,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,soft_ctx_q3s4_05,none,,0.62,0.055,2.6128045623,0.5778427806,0.5768473916,4.57e-08,3.07052e-05,0.0006754077,0.0015262631,0.5778427806,715.08
submission_raw05_jepa_axistrade_ecf60728.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv,submission_jepa_bridge_posteriorreg_9c5e225e.csv,q3s4+ctx_q1q2s123,none,0.96,0.32,0.055,0.96,0.577870385,0.5767415216,5.4e-09,0.0003385506,0.0002825752,0.0014466061,0.577870385,716.92
submission_raw05_jepa_axistrade_f83b5cdf.csv,tradeoff_rank_fallback,soft_axis_repair,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_block_countshift_a58efeff.csv,,soft_ctx_q3s4_05,none,,0.62,0.055,2.4742368586,0.5778429257,0.5768498566,4.26e-08,-5.5615e-06,0.000652746,0.0015219825,0.5778429257,725.92
submission_raw05_jepa_axistrade_80fd659c.csv,tradeoff_goal_hit,soft_axis_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_block_consensus_rawcorr_4fd8bab2.csv,,soft_sblock_q3_08,none,,0.62,0.055,1.0427573657,0.5778294356,0.5769039373,-9.13e-08,-1.7532e-05,0.0003484718,0.0015999971,0.5778294356,736.88
submission_raw05_jepa_axistrade_b4552109.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,submission_jepa_bridge_ensemble_c42fbf1e.csv,q3s4+ctx_q1q2s123,none,0.96,0.32,0.055,0.96,0.5778699736,0.5766946972,6.33e-08,0.0005612558,0.0002858741,0.0015618917,0.5778699736,737.82
submission_raw05_jepa_axistrade_e3f34aa0.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv,submission_jepa_bridge_ensemble_c42fbf1e.csv,q3s4+ctx_q1q2s123,none,0.96,0.32,0.055,0.96,0.5778698165,0.5767464308,-4.6e-09,0.0003589865,0.0002858664,0.0014436211,0.5778698165,745.66
submission_raw05_jepa_axistrade_3149ef2f.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_5a189d26.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,submission_jepa_bridge_posteriorreg_9c5e225e.csv,q3s4+ctx_q1q2s123,none,0.96,0.18,0.055,0.96,0.5778681352,0.5766927803,-3.29e-08,0.0008630043,0.0002851812,0.0015691278,0.5778681352,747.56
submission_raw05_jepa_axistrade_b07b9c0b.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv,submission_jepa_bridge_posteriorreg_9c5e225e.csv,q3s4+ctx_q1q2s123,none,0.96,0.32,0.055,0.96,0.5778700717,0.5767413252,3.77e-08,0.0003405619,0.0002840659,0.0014479283,0.5778700717,748.04
submission_raw05_jepa_axistrade_de8af050.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_5a189d26.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,submission_jepa_public_minimax_bridge_84b71a03.csv,q3s4+ctx_q1q2s123,none,0.96,0.18,0.055,0.96,0.5778688222,0.5766921113,-1.59e-08,0.0008477182,0.000273828,0.0015691567,0.5778688222,748.16
submission_raw05_jepa_axistrade_2ca496b2.csv,tradeoff_rank_fallback,soft_axis_repair,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv,,soft_ctx_q3s4_05,none,,0.62,0.055,2.3815399868,0.5778427767,0.5768490198,6.81e-08,2.44572e-05,0.0006357743,0.0015233462,0.5778427767,748.52
submission_raw05_jepa_axistrade_cacbb1a3.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,submission_jepa_bridge_posteriorreg_9c5e225e.csv,q3s4+ctx_q1q2s123,none,0.96,0.32,0.055,0.96,0.5778702374,0.5766895916,1.056e-07,0.0005428313,0.0002840737,0.0015661988,0.5778716929,753.2
submission_raw05_jepa_axistrade_e7ac76f4.csv,tradeoff_rank_fallback,soft_axis_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,soft_ctx_q3s4_05,none,,0.62,0.055,2.5991770428,0.5778425709,0.5768472169,1.018e-07,3.27575e-05,0.000677173,0.0015276737,0.5778430455,758.56
submission_raw05_jepa_axistrade_ddf04ed5.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv,submission_jepa_public_minimax_bridge_84b71a03.csv,q3s4+ctx_q1q2s123,none,0.96,0.32,0.055,0.96,0.5778715764,0.5767403206,2.4e-08,0.0003113414,0.0002623898,0.0014462289,0.5778715764,759.64
submission_raw05_jepa_axistrade_ef480390.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,submission_jepa_public_minimax_bridge_84b71a03.csv,q3s4+ctx_q1q2s123,none,0.96,0.32,0.055,0.96,0.5778717849,0.5766885846,8.96e-08,0.0005136446,0.0002623951,0.0015646385,0.5778717849,761.48
submission_raw05_jepa_axistrade_e8eda878.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_5a189d26.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,submission_jepa_bridge_ensemble_c42fbf1e.csv,q3s4+ctx_q1q2s123,none,0.96,0.18,0.055,0.96,0.5778679871,0.5766956506,-5.83e-08,0.0008733578,0.0002861944,0.0015666867,0.5778679871,766.02
submission_raw05_jepa_axistrade_bc0a829d.csv,tradeoff_lowbad,soft_axis_repair,submission_raw05_jepa_axisbridge_8c9a99c0.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,2.3033955527,0.5778365265,0.5768870625,8.14e-08,0.0002002882,0.0007984635,0.0015197087,0.5778365265,766.76
submission_raw05_jepa_axistrade_1dca7e97.csv,tradeoff_lowbad,soft_axis_repair,submission_raw05_jepa_axisbridge_5bce22bc.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,2.3033302527,0.5778365232,0.5768870568,8.18e-08,0.0002015007,0.0007984733,0.0015197227,0.5778365232,766.94
submission_raw05_jepa_axistrade_5280ba62.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv,submission_jepa_bridge_ensemble_c42fbf1e.csv,q3s4+ctx_q1q2s123,none,0.96,0.32,0.055,0.96,0.5778701298,0.5767466272,-3.69e-08,0.0003569751,0.0002843756,0.001442299,0.5778701298,767.46
submission_raw05_jepa_axistrade_7abcc33a.csv,tradeoff_lowbad,soft_axis_repair,submission_raw05_jepa_axisbridge_9e61b879.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,2.3033606662,0.5778365267,0.5768870634,8.15e-08,0.0002000813,0.0007984684,0.0015197144,0.5778365267,767.48
submission_raw05_jepa_axistrade_0c56aefe.csv,tradeoff_lowbad,soft_axis_repair,submission_raw05_jepa_axisbridge_18aad556.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,2.3031136984,0.57783653,0.5768870685,8.17e-08,0.0001972917,0.0007984938,0.0015197408,0.57783653,768.24
submission_raw05_jepa_axistrade_23178f1c.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_35fe4935.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,submission_jepa_bridge_posteriorreg_9c5e225e.csv,q3s4+ctx_q1q2s123,none,0.96,0.18,0.055,0.96,0.5778681315,0.5766927738,-3.27e-08,0.0008644076,0.0002851867,0.0015691371,0.5778681315,770.1
submission_raw05_jepa_axistrade_d612d0ea.csv,tradeoff_goal_hit,soft_axis_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_bridge_posteriorreg_9c5e225e.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,1.116046022,0.5778308956,0.5769031821,-3.17e-08,0.0003934322,0.0003872041,0.0015388099,0.5778308956,770.44
submission_raw05_jepa_axistrade_fc4eddd6.csv,tradeoff_lowbad,soft_axis_repair,submission_raw05_jepa_axisbridge_74a95f7b.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,2.3023365047,0.5778365006,0.5768870375,8.41e-08,0.0002062782,0.0007986241,0.0015199026,0.5778365006,770.64
submission_raw05_jepa_axistrade_c243e3de.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_18aad556.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,submission_jepa_public_minimax_bridge_84b71a03.csv,q3s4+ctx_q1q2s123,none,0.96,0.18,0.055,0.96,0.5778691791,0.5766920006,-3.52e-08,0.0008228917,0.0002727761,0.0015682214,0.5778691791,770.8
submission_raw05_jepa_axistrade_a6a7e658.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_35fe4935.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,submission_jepa_public_minimax_bridge_84b71a03.csv,q3s4+ctx_q1q2s123,none,0.96,0.18,0.055,0.96,0.5778688186,0.5766921048,-1.57e-08,0.0008491214,0.0002738334,0.001569166,0.5778688186,770.94
submission_raw05_jepa_axistrade_2e0e70da.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_18aad556.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,submission_jepa_bridge_posteriorreg_9c5e225e.csv,q3s4+ctx_q1q2s123,none,0.96,0.18,0.055,0.96,0.5778684919,0.5766926696,-5.22e-08,0.0008381778,0.0002841293,0.0015681925,0.5778684919,771.28
submission_raw05_jepa_axistrade_6f719d2c.csv,tradeoff_rank_fallback,soft_axis_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_block_countshift_a58efeff.csv,,soft_ctx_q3s4_05,none,,0.62,0.055,2.4609002785,0.5778427156,0.5768496817,9.85e-08,-3.5079e-06,0.0006543539,0.001523393,0.5778427156,772.04
submission_raw05_jepa_axistrade_6b7bc6a5.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_970e949f.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,submission_jepa_public_minimax_bridge_84b71a03.csv,q3s4+ctx_q1q2s123,none,0.96,0.18,0.055,0.96,0.5778688253,0.5766921162,-1.58e-08,0.0008449729,0.0002738627,0.0015691803,0.5778688253,781.16
submission_raw05_jepa_axistrade_a25f36cc.csv,tradeoff_rank_fallback,compensated_inject,submission_raw05_jepa_axisbridge_970e949f.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,submission_jepa_bridge_posteriorreg_9c5e225e.csv,q3s4+ctx_q1q2s123,none,0.96,0.18,0.055,0.96,0.5778681383,0.5766927853,-3.28e-08,0.000860259,0.0002852159,0.0015691514,0.5778681383,781.56
submission_raw05_jepa_axistrade_e4dd5c17.csv,tradeoff_goal_hit,soft_axis_repair,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_block_consensus_rawcorr_4fd8bab2.csv,,soft_sblock_q3_08,none,,0.62,0.055,1.04541714,0.5778295999,0.5769040984,-1.448e-07,-1.97903e-05,0.0003472363,0.0015986523,0.5778295999,782.12
submission_raw05_jepa_axistrade_07d6643e.csv,tradeoff_lowbad,soft_axis_repair,submission_raw05_jepa_axisbridge_8c9a99c0.csv,submission_jepa_block_countshift_a58efeff.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,2.1118167951,0.5778366446,0.5768888544,8.2e-08,0.0001739274,0.0007572494,0.0015163759,0.5778366446,782.96
submission_raw05_jepa_axistrade_844ba175.csv,tradeoff_lowbad,soft_axis_repair,submission_raw05_jepa_axisbridge_5bce22bc.csv,submission_jepa_block_countshift_a58efeff.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,2.1117937652,0.5778366414,0.5768888487,8.23e-08,0.0001751398,0.0007572672,0.0015163899,0.5778366414,783.24
submission_raw05_jepa_axistrade_e9dbbff5.csv,tradeoff_lowbad,soft_axis_repair,submission_raw05_jepa_axisbridge_9e61b879.csv,submission_jepa_block_countshift_a58efeff.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,2.1117882927,0.5778366448,0.5768888553,8.2e-08,0.0001737204,0.0007572548,0.0015163816,0.5778366448,783.86
submission_raw05_jepa_axistrade_1a28133a.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_74a95f7b.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3_s4half,none,1.18,,0.055,1.0698264331,0.577867239,0.5766793752,7.129e-07,0.0005348068,0.0002564557,0.0015992465,0.5780265832,786.4
submission_raw05_jepa_axistrade_892042e5.csv,tradeoff_lowbad,soft_axis_repair,submission_raw05_jepa_axisbridge_74a95f7b.csv,submission_jepa_block_countshift_a58efeff.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,2.1111551584,0.5778366186,0.5768888294,8.46e-08,0.0001799172,0.0007574709,0.0015165698,0.5778366186,786.5
submission_raw05_jepa_axistrade_17e8aadf.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_5bce22bc.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3_s4half,none,1.18,,0.055,1.0697486123,0.5778672719,0.5766793998,7.113e-07,0.000529044,0.0002562541,0.0015990561,0.578026202,789.6
submission_raw05_jepa_axistrade_3f6cc0ec.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_9e61b879.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3_s4half,none,1.18,,0.055,1.0697465065,0.5778672764,0.5766794077,7.109e-07,0.000527332,0.000256247,0.0015990461,0.5780261186,789.82
submission_raw05_jepa_axistrade_b47497fd.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_8c9a99c0.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3_s4half,none,1.18,,0.055,1.0697437645,0.5778672764,0.5766794066,7.109e-07,0.0005275816,0.0002562403,0.0015990406,0.578026123,789.96
submission_raw05_jepa_axistrade_880a1bb6.csv,tradeoff_lowbad,soft_axis_repair,submission_raw05_jepa_axisbridge_8c9a99c0.csv,submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,2.0954265873,0.5778365253,0.5768882449,9.83e-08,0.0001957379,0.0007539643,0.0015174268,0.5778365253,801.94
submission_raw05_jepa_axistrade_9bbcd481.csv,tradeoff_lowbad,soft_axis_repair,submission_raw05_jepa_axisbridge_9e61b879.csv,submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,2.0954003077,0.5778365254,0.5768882458,9.83e-08,0.000195531,0.0007539701,0.0015174325,0.5778365254,802.66
submission_raw05_jepa_axistrade_1de9e3db.csv,tradeoff_lowbad,soft_axis_repair,submission_raw05_jepa_axisbridge_5bce22bc.csv,submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,2.0953862299,0.577836522,0.5768882392,9.86e-08,0.0001969504,0.0007539779,0.0015174408,0.577836522,803.36
submission_raw05_jepa_axistrade_562815da.csv,tradeoff_lowbad,soft_axis_repair,submission_raw05_jepa_axisbridge_18aad556.csv,submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,2.0951872061,0.5778365288,0.5768882509,9.86e-08,0.0001927414,0.0007539959,0.0015174589,0.5778365288,804.64
submission_raw05_jepa_axistrade_57940743.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_970e949f.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3_only,none,1.18,,0.055,0.9607755245,0.5778656839,0.5766711929,1.0031e-06,0.0005776478,0.0002328738,0.0016076424,0.5781156635,805.52
submission_raw05_jepa_axistrade_69b04094.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_35fe4935.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3_only,none,1.18,,0.055,0.9607447728,0.5778656756,0.5766711788,1.0032e-06,0.0005827479,0.0002328378,0.0016076218,0.578115701,806.1
submission_raw05_jepa_axistrade_6a2c4782.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_1968b38c.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3_only,none,1.18,,0.055,0.9609024745,0.5778656419,0.576671154,1.0049e-06,0.0005885737,0.0002330438,0.0016078173,0.5781162104,806.12
submission_raw05_jepa_axistrade_c921ac12.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_5a189d26.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3_only,none,1.18,,0.055,0.9607410273,0.57786568,0.5766711867,1.0029e-06,0.0005810227,0.0002328311,0.0016076121,0.5781155991,806.36
submission_raw05_jepa_axistrade_f8c02215.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_c99ee489.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3_only,none,1.18,,0.055,0.960735362,0.57786568,0.5766711856,1.0029e-06,0.0005812733,0.0002328242,0.0016076064,0.5781156031,806.46
submission_raw05_jepa_axistrade_566fd4af.csv,tradeoff_goal_hit,soft_axis_repair,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_bridge_posteriorreg_9c5e225e.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,1.1171597763,0.5778310996,0.5769033576,-8.9e-08,0.0003913608,0.0003856434,0.0015373849,0.5778310996,818.22
submission_raw05_jepa_axistrade_abd3efe7.csv,tradeoff_goal_hit,soft_axis_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_public_minimax_bridge_84b71a03.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,1.2559819068,0.5778324445,0.5769010665,-1.27e-07,0.0003527216,0.0004348542,0.0015329078,0.5778324445,843.14
submission_raw05_jepa_axistrade_7391e580.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3s4,none,1.18,,0.055,1.18,0.5778743562,0.5766771018,7.092e-07,-4.76805e-05,0.0002279117,0.0015801496,0.5780327364,853.34
submission_raw05_jepa_axistrade_54a5248f.csv,tradeoff_goal_hit,soft_axis_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_bridge_posteriorreg_9c5e225e.csv,,soft_ctx_q3s4_12,none,,0.45,0.055,1.0800813676,0.5778314353,0.5769036434,-1.112e-07,0.0004250777,0.0003802395,0.0015335972,0.5778314353,857.78
submission_raw05_jepa_axistrade_1df93f48.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3s4,none,1.18,,0.055,1.18,0.5778747039,0.5766773362,6.624e-07,-5.00879e-05,0.0002260735,0.0015786192,0.5780209391,860.76
submission_raw05_jepa_axistrade_9f6fb74c.csv,tradeoff_goal_hit,soft_axis_repair,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_public_minimax_bridge_84b71a03.csv,,soft_ctx_q3s4_05,none,,0.45,0.055,1.2580615316,0.577832652,0.576901242,-1.843e-07,0.0003506504,0.0004332403,0.0015314828,0.577832652,884.06
submission_raw05_jepa_axistrade_5e26bb75.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_18aad556.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3_only,none,1.18,,0.055,0.9595273477,0.5778660851,0.5766710468,9.754e-07,0.0005505286,0.000231534,0.0016064398,0.5781072074,899.7
submission_raw05_jepa_axistrade_f643854e.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_74a95f7b.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3_only,none,1.18,,0.055,0.9596528662,0.5778660431,0.5766710083,9.771e-07,0.0005613672,0.0002317006,0.0016066102,0.5781077252,901.04
submission_raw05_jepa_axistrade_176c4c6e.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_9e61b879.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3_only,none,1.18,,0.055,0.9594930131,0.577866081,0.5766710408,9.752e-07,0.0005538925,0.0002314918,0.0016064097,0.5781071453,901.24
submission_raw05_jepa_axistrade_290443e0.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_5bce22bc.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3_only,none,1.18,,0.055,0.9594972246,0.5778660765,0.5766710328,9.755e-07,0.0005556044,0.000231499,0.0016064197,0.578107249,901.3
submission_raw05_jepa_axistrade_2cdc2f14.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_8c9a99c0.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3_only,none,1.18,,0.055,0.9594875291,0.577866081,0.5766710397,9.752e-07,0.000554142,0.0002314852,0.0016064043,0.5781071508,901.38
submission_raw05_jepa_axistrade_80a340ad.csv,tradeoff_goal_hit,soft_axis_repair,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_bridge_posteriorreg_9c5e225e.csv,,soft_ctx_q3s4_12,none,,0.45,0.055,1.0811592311,0.5778316456,0.5769038139,-1.661e-07,0.0004230703,0.0003787295,0.0015322185,0.5778316456,901.82
submission_raw05_jepa_axistrade_4e3c06b7.csv,tradeoff_goal_hit,soft_axis_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_public_minimax_bridge_84b71a03.csv,,soft_ctx_q3s4_12,none,,0.45,0.055,1.2155078096,0.5778330376,0.576901098,-2.089e-07,0.0003812404,0.0004270382,0.001527503,0.5778330376,911.86
submission_raw05_jepa_axistrade_f55b03bd.csv,tradeoff_goal_hit,soft_axis_repair,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_public_minimax_bridge_84b71a03.csv,,soft_ctx_q3s4_12,none,,0.45,0.055,1.2175204183,0.5778332588,0.5769012686,-2.636e-07,0.0003792334,0.0004254767,0.0015261243,0.5778332588,941.42
submission_raw05_jepa_axistrade_32959211.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3s4,none,0.96,,0.055,0.96,0.5778779486,0.57667711,3.451e-07,0.000203592,0.000183901,0.0015580089,0.5779416837,947.94
submission_raw05_jepa_axistrade_3509d5f0.csv,tradeoff_highret,highret_inject,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,,q3s4,none,0.96,,0.055,0.96,0.5778776641,0.576676916,3.797e-07,0.0002055695,0.0001853942,0.001559192,0.5779503917,979.3
submission_raw05_jepa_axistrade_531cc13d.csv,tradeoff_goal_hit,soft_axis_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_bridge_posteriorreg_9c5e225e.csv,,soft_sblock_q3_08,none,,0.62,0.055,1.0628593076,0.5778312262,0.5768955852,-1.348e-07,0.0009430576,0.0003744738,0.0015388715,0.5778312262,1024.92
submission_raw05_jepa_axistrade_70613b0c.csv,tradeoff_goal_hit,soft_axis_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_jepa_bridge_ensemble_c42fbf1e.csv,,soft_sblock_q3_08,none,,0.62,0.055,1.0573297027,0.5778307285,0.5769002736,-1.404e-07,0.0009581784,0.0003756602,0.0015361785,0.5778307285,1029.22
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_jepa_axistrade_931a03a1.csv,250,True,0,0,0.0630709467,0.9797963515
submission_raw05_jepa_axistrade_b8172c33.csv,250,True,0,0,0.0630709467,0.9797963515
submission_raw05_jepa_axistrade_183834e5.csv,250,True,0,0,0.0628745262,0.9796885476
submission_raw05_jepa_axistrade_329350af.csv,250,True,0,0,0.0630709467,0.9797963515
submission_raw05_jepa_axistrade_4556271c.csv,250,True,0,0,0.0628999686,0.9796892085
submission_raw05_jepa_axistrade_c4caf7e5.csv,250,True,0,0,0.0628556758,0.9797403064
submission_raw05_jepa_axistrade_ecf60728.csv,250,True,0,0,0.0628999686,0.9796892085
submission_raw05_jepa_axistrade_f83b5cdf.csv,250,True,0,0,0.0628556758,0.9797403064
submission_raw05_jepa_axistrade_80fd659c.csv,250,True,0,0,0.0629859692,0.9797752006
submission_raw05_jepa_axistrade_b4552109.csv,250,True,0,0,0.0628745262,0.9796885476
submission_raw05_jepa_axistrade_e3f34aa0.csv,250,True,0,0,0.0628745262,0.9796885476
submission_raw05_jepa_axistrade_3149ef2f.csv,250,True,0,0,0.0628456792,0.9796814211
submission_raw05_jepa_axistrade_b07b9c0b.csv,250,True,0,0,0.0628999686,0.9796892085
submission_raw05_jepa_axistrade_de8af050.csv,250,True,0,0,0.0628195331,0.9796795607
submission_raw05_jepa_axistrade_2ca496b2.csv,250,True,0,0,0.0628556758,0.9797403064
submission_raw05_jepa_axistrade_cacbb1a3.csv,250,True,0,0,0.0628999686,0.9796892085
submission_raw05_jepa_axistrade_e7ac76f4.csv,250,True,0,0,0.0628556758,0.9797403064
submission_raw05_jepa_axistrade_ddf04ed5.csv,250,True,0,0,0.0628534561,0.9796859022
submission_raw05_jepa_axistrade_ef480390.csv,250,True,0,0,0.0628534561,0.9796859022
submission_raw05_jepa_axistrade_e8eda878.csv,250,True,0,0,0.0628313782,0.9796810492
submission_raw05_jepa_axistrade_bc0a829d.csv,250,True,0,0,0.0628878277,0.9797658913
submission_raw05_jepa_axistrade_1dca7e97.csv,250,True,0,0,0.0628878277,0.9797658913
submission_raw05_jepa_axistrade_5280ba62.csv,250,True,0,0,0.0628745262,0.9796885476
submission_raw05_jepa_axistrade_7abcc33a.csv,250,True,0,0,0.0628878277,0.9797658913
submission_raw05_jepa_axistrade_0c56aefe.csv,250,True,0,0,0.0628878277,0.9797658913
submission_raw05_jepa_axistrade_23178f1c.csv,250,True,0,0,0.0628456792,0.9796814211
submission_raw05_jepa_axistrade_d612d0ea.csv,250,True,0,0,0.063066152,0.9797959694
submission_raw05_jepa_axistrade_fc4eddd6.csv,250,True,0,0,0.0628878277,0.9797658913
submission_raw05_jepa_axistrade_c243e3de.csv,250,True,0,0,0.0628195331,0.9796795607
submission_raw05_jepa_axistrade_a6a7e658.csv,250,True,0,0,0.0628195331,0.9796795607
submission_raw05_jepa_axistrade_2e0e70da.csv,250,True,0,0,0.0628456792,0.9796814211
submission_raw05_jepa_axistrade_6f719d2c.csv,250,True,0,0,0.0628556758,0.9797403064
submission_raw05_jepa_axistrade_6b7bc6a5.csv,250,True,0,0,0.0628195331,0.9796795607
submission_raw05_jepa_axistrade_a25f36cc.csv,250,True,0,0,0.0628456792,0.9796814211
submission_raw05_jepa_axistrade_e4dd5c17.csv,250,True,0,0,0.0629859692,0.9797752006
submission_raw05_jepa_axistrade_07d6643e.csv,250,True,0,0,0.0628878277,0.9797658913
submission_raw05_jepa_axistrade_844ba175.csv,250,True,0,0,0.0628878277,0.9797658913
submission_raw05_jepa_axistrade_e9dbbff5.csv,250,True,0,0,0.0628878277,0.9797658913
submission_raw05_jepa_axistrade_1a28133a.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_892042e5.csv,250,True,0,0,0.0628878277,0.9797658913
submission_raw05_jepa_axistrade_17e8aadf.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_3f6cc0ec.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_b47497fd.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_880a1bb6.csv,250,True,0,0,0.0628878277,0.9797658913
submission_raw05_jepa_axistrade_9bbcd481.csv,250,True,0,0,0.0628878277,0.9797658913
submission_raw05_jepa_axistrade_1de9e3db.csv,250,True,0,0,0.0628878277,0.9797658913
submission_raw05_jepa_axistrade_562815da.csv,250,True,0,0,0.0628878277,0.9797658913
submission_raw05_jepa_axistrade_57940743.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_69b04094.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_6a2c4782.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_c921ac12.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_f8c02215.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_566fd4af.csv,250,True,0,0,0.063066152,0.9797959694
submission_raw05_jepa_axistrade_abd3efe7.csv,250,True,0,0,0.0630005919,0.9797913436
submission_raw05_jepa_axistrade_7391e580.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_54a5248f.csv,250,True,0,0,0.063066152,0.9797959694
submission_raw05_jepa_axistrade_1df93f48.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_9f6fb74c.csv,250,True,0,0,0.0630005919,0.9797913436
submission_raw05_jepa_axistrade_5e26bb75.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_f643854e.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_176c4c6e.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_290443e0.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_2cdc2f14.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_80a340ad.csv,250,True,0,0,0.063066152,0.9797959694
submission_raw05_jepa_axistrade_4e3c06b7.csv,250,True,0,0,0.0630005919,0.9797913436
submission_raw05_jepa_axistrade_f55b03bd.csv,250,True,0,0,0.0630005919,0.9797913436
submission_raw05_jepa_axistrade_32959211.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_3509d5f0.csv,250,True,0,0,0.0627759429,0.9796714044
submission_raw05_jepa_axistrade_531cc13d.csv,250,True,0,0,0.0629859692,0.9797746736
submission_raw05_jepa_axistrade_70613b0c.csv,250,True,0,0,0.0629859692,0.9797733982
submission_raw05_jepa_axistrade_57a439fb.csv,250,True,0,0,0.0629795082,0.9797658913
submission_raw05_jepa_axistrade_1bed2eca.csv,250,True,0,0,0.0629795082,0.9797658913
submission_raw05_jepa_axistrade_9a37e039.csv,250,True,0,0,0.0629795082,0.9797658913
submission_raw05_jepa_axistrade_81d5f3e2.csv,250,True,0,0,0.0629795082,0.9797658913
submission_raw05_jepa_axistrade_22b6312a.csv,250,True,0,0,0.0629795082,0.9797658913
submission_raw05_jepa_axistrade_c90d87b2.csv,250,True,0,0,0.0629859692,0.9797411426
submission_raw05_jepa_axistrade_de6e55ec.csv,250,True,0,0,0.0629795082,0.9797658913
submission_raw05_jepa_axistrade_49128b93.csv,250,True,0,0,0.0629795082,0.9797658913
submission_raw05_jepa_axistrade_41042502.csv,250,True,0,0,0.0629795082,0.9797658913
submission_raw05_jepa_axistrade_098bdea5.csv,250,True,0,0,0.0629795082,0.9797658913
submission_raw05_jepa_axistrade_3e96ce44.csv,250,True,0,0,0.0629795082,0.9797658913
submission_raw05_jepa_axistrade_43361677.csv,250,True,0,0,0.0629795082,0.9797658913
submission_raw05_jepa_axistrade_1e5df20e.csv,250,True,0,0,0.0629795082,0.9797658913
submission_raw05_jepa_axistrade_a8e0b4c9.csv,250,True,0,0,0.0629795082,0.9797658913
```