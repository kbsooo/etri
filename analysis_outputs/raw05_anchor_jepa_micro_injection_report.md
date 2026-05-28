# Raw05 Anchor JEPA Micro Injection

Raw05 is the observed public best, so this pass starts at raw05 logits and injects only small JEPA hidden-structure deltas.
Generation uses donor/median JEPA deltas, target masks, public-inverse row gates, sign/agreement gates, and logit caps.

## Counts

- generated candidates: 59031
- actual-anchor rescored candidates: 1000
- saved candidates: 48

## Top Saved

```csv
file,bucket,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,mean_abs_move_vs_raw05,label
submission_raw05_anchor_jepa_micro_1b9ebb50.csv,balanced,0.5778425183,0.5768797129,-1.005e-07,0.002379415,0.0015476814,jepa_micro_bridge_ensemble_5ffa44a8|all|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_b021591b.csv,balanced,0.5778425224,0.5768802598,-1.14e-07,0.0023870831,0.0015464715,jepa_micro_bridge_ensemble_5ffa44a8|all|ones|agree|w1.00|c0.070
submission_raw05_anchor_jepa_micro_fe4faee5.csv,balanced,0.577842594,0.5768791937,-1.1e-07,0.0023838908,0.0015442059,jepa_micro_bridge_ensemble_a06a8e5b|all|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_d9fdc7e2.csv,balanced,0.5778425952,0.5768797936,-1.226e-07,0.0023920767,0.0015428861,jepa_micro_bridge_ensemble_a06a8e5b|all|ones|agree|w1.00|c0.070
submission_raw05_anchor_jepa_micro_a5efe1d8.csv,balanced,0.5778426047,0.5768670669,9.81e-08,0.0020188433,0.0016522207,jepa_micro_bridge_ensemble_22063df5|all|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_5175341d.csv,balanced,0.5778426153,0.576879082,-1.184e-07,0.0023726286,0.0015457292,median_strict_raw_top16|all|ones|agree|w1.00|c0.070
submission_raw05_anchor_jepa_micro_c90d5913.csv,balanced,0.5778426194,0.5768669485,9.28e-08,0.0020207985,0.0016507967,jepa_micro_bridge_ensemble_940b779e|all|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_c1e1f59d.csv,balanced,0.5778426205,0.5768785244,-1.117e-07,0.0023657222,0.0015469398,median_strict_raw_top16|all|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_c29aa418.csv,balanced,0.5778426226,0.5768669536,8.74e-08,0.0020244543,0.0016493387,median_balanced_top20|all|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_617df316.csv,balanced,0.5778426343,0.5768668301,8.75e-08,0.0020227538,0.0016493726,jepa_micro_bridge_ensemble_bf074240|all|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_49a84ea0.csv,balanced,0.5778426516,0.5768749633,-6.49e-08,0.0022990239,0.0015659651,jepa_micro_bridge_ensemble_eb296a12|all|ones|agree|w1.00|c0.070
submission_raw05_anchor_jepa_micro_510d6163.csv,balanced,0.5778426594,0.5768745484,-6.18e-08,0.0022955081,0.0015668252,jepa_micro_bridge_ensemble_eb296a12|all|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_5264bb61.csv,balanced,0.5778426683,0.5768793283,-1.308e-07,0.0023970901,0.0015393031,jepa_micro_bridge_ensemble_9a83e05d|all|ones|agree|w1.00|c0.070
submission_raw05_anchor_jepa_micro_a0cdca44.csv,balanced,0.5778426702,0.576878675,-1.192e-07,0.0023883674,0.0015407351,jepa_micro_bridge_ensemble_9a83e05d|all|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_5b6d7d35.csv,balanced,0.5778426911,0.5768799996,-1.879e-07,0.0023755635,0.0015379782,jepa_micro_bridge_ensemble_9692910f|all|ones|agree|w1.00|c0.070
submission_raw05_anchor_jepa_micro_ea445126.csv,balanced,0.57784271,0.5768792813,-1.846e-07,0.0023683403,0.0015395035,jepa_micro_bridge_ensemble_9692910f|all|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_5de1d404.csv,balanced,0.5778427322,0.5768744405,-7.52e-08,0.002304669,0.0015619505,jepa_micro_bridge_ensemble_7e335eb7|all|ones|agree|w1.00|c0.070
submission_raw05_anchor_jepa_micro_c9f8578b.csv,balanced,0.5778427445,0.5768739674,-7.32e-08,0.0023005103,0.0015629261,jepa_micro_bridge_ensemble_7e335eb7|all|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_21e44358.csv,balanced,0.5778427471,0.5768781565,-1.281e-07,0.0023928449,0.0015372677,jepa_micro_bridge_ensemble_6e15f03a|all|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_0e48980c.csv,balanced,0.5778427418,0.5768788639,-1.386e-07,0.0024021119,0.0015357219,jepa_micro_bridge_ensemble_6e15f03a|all|ones|agree|w1.00|c0.070
submission_raw05_anchor_jepa_micro_f389264f.csv,balanced,0.577842874,0.576868543,-3.1e-09,0.0020232423,0.0016504277,jepa_block_consensus_rawcorr_micro_fea06910|all|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_82cd6d38.csv,balanced,0.5778431626,0.5768593134,8.6e-08,0.0020432996,0.001625042,jepa_block_consensus_rawcorr_refine_d9aefe69|all|ones|agree|w1.00|c0.070
submission_raw05_anchor_jepa_micro_acc81891.csv,balanced,0.5778431742,0.5768590876,8.7e-08,0.0020438107,0.0016254436,jepa_block_consensus_rawcorr_refine_d9aefe69|all|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_7143bfaa.csv,balanced,0.5778433226,0.57688563,-1.765e-07,0.0010949326,0.0014912678,jepa_micro_bridge_ensemble_5ffa44a8|no_q2|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_1e0ffbec.csv,balanced,0.5778433317,0.5768861774,-1.9e-07,0.001102624,0.0014900583,jepa_micro_bridge_ensemble_5ffa44a8|no_q2|ones|agree|w1.00|c0.070
submission_raw05_anchor_jepa_micro_9d2077f7.csv,balanced,0.5778433911,0.5768733458,4.74e-08,0.0007663386,0.0016028382,jepa_block_consensus_rawcorr_micro_9ec2b75e|no_q2|ones|agree|w1.00|c0.070
submission_raw05_anchor_jepa_micro_8fadff60.csv,balanced,0.5778433915,0.5768733449,4.75e-08,0.0007661942,0.0016028419,jepa_block_consensus_rawcorr_micro_9ec2b75e|no_q2|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_3c91279c.csv,balanced,0.5778433949,0.5768850842,-1.856e-07,0.0011010085,0.0014879806,jepa_micro_bridge_ensemble_a06a8e5b|no_q2|ones|all|w1.00|c0.070
submission_raw05_anchor_jepa_micro_e558e0a8.csv,balanced,0.577843401,0.5768856847,-1.981e-07,0.0011092385,0.0014866617,jepa_micro_bridge_ensemble_a06a8e5b|no_q2|ones|agree|w1.00|c0.070
submission_raw05_anchor_jepa_micro_4ef24934.csv,balanced,0.5778434161,0.5768849142,-1.928e-07,0.0010952537,0.0014899421,median_strict_raw_top16|no_q2|ones|agree|w1.00|c0.070
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_anchor_jepa_micro_1b9ebb50.csv,250,True,0,0,0.0632254238,0.9797320058
submission_raw05_anchor_jepa_micro_b021591b.csv,250,True,0,0,0.0632254238,0.9797320058
submission_raw05_anchor_jepa_micro_fe4faee5.csv,250,True,0,0,0.0632243828,0.9797319587
submission_raw05_anchor_jepa_micro_d9fdc7e2.csv,250,True,0,0,0.0632243828,0.9797319587
submission_raw05_anchor_jepa_micro_a5efe1d8.csv,250,True,0,0,0.0632159126,0.9797309797
submission_raw05_anchor_jepa_micro_5175341d.csv,250,True,0,0,0.063223427,0.9797318882
submission_raw05_anchor_jepa_micro_c90d5913.csv,250,True,0,0,0.0632151609,0.9797309451
submission_raw05_anchor_jepa_micro_c1e1f59d.csv,250,True,0,0,0.063223427,0.9797318882
submission_raw05_anchor_jepa_micro_c29aa418.csv,250,True,0,0,0.0632159126,0.9797309797
submission_raw05_anchor_jepa_micro_617df316.csv,250,True,0,0,0.0632144092,0.9797309105
submission_raw05_anchor_jepa_micro_49a84ea0.csv,250,True,0,0,0.0632246757,0.9797314094
submission_raw05_anchor_jepa_micro_510d6163.csv,250,True,0,0,0.0632246757,0.9797314094
submission_raw05_anchor_jepa_micro_5264bb61.csv,250,True,0,0,0.0632233417,0.9797319117
submission_raw05_anchor_jepa_micro_a0cdca44.csv,250,True,0,0,0.0632233417,0.9797319117
submission_raw05_anchor_jepa_micro_5b6d7d35.csv,250,True,0,0,0.0631988161,0.979731721
submission_raw05_anchor_jepa_micro_ea445126.csv,250,True,0,0,0.0631988161,0.979731721
submission_raw05_anchor_jepa_micro_5de1d404.csv,250,True,0,0,0.0632235122,0.9797313568
submission_raw05_anchor_jepa_micro_c9f8578b.csv,250,True,0,0,0.0632235122,0.9797313568
submission_raw05_anchor_jepa_micro_21e44358.csv,250,True,0,0,0.0632223007,0.9797318647
submission_raw05_anchor_jepa_micro_0e48980c.csv,250,True,0,0,0.0632223007,0.9797318647
submission_raw05_anchor_jepa_micro_f389264f.csv,250,True,0,0,0.0632105794,0.979732199
submission_raw05_anchor_jepa_micro_82cd6d38.csv,250,True,0,0,0.0632224313,0.9797296202
submission_raw05_anchor_jepa_micro_acc81891.csv,250,True,0,0,0.0632224313,0.9797296202
submission_raw05_anchor_jepa_micro_7143bfaa.csv,250,True,0,0,0.0632254238,0.9797320058
submission_raw05_anchor_jepa_micro_1e0ffbec.csv,250,True,0,0,0.0632254238,0.9797320058
submission_raw05_anchor_jepa_micro_9d2077f7.csv,250,True,0,0,0.0632189194,0.9797311179
submission_raw05_anchor_jepa_micro_8fadff60.csv,250,True,0,0,0.0632189194,0.9797311179
submission_raw05_anchor_jepa_micro_3c91279c.csv,250,True,0,0,0.0632243828,0.9797319587
submission_raw05_anchor_jepa_micro_e558e0a8.csv,250,True,0,0,0.0632243828,0.9797319587
submission_raw05_anchor_jepa_micro_4ef24934.csv,250,True,0,0,0.063223427,0.9797318882
```
