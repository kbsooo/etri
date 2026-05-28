# Raw05 JEPA Q3 Stress Counterweight Optimizer

This pass keeps the Q3-stress JEPA base signal and blends only selected target blocks toward low-bad/strict counter candidates.
The intent is JEPA-style representation agreement: Q3 carries the hidden target-block signal, while Q2/S1/S-blocks serve as raw05/public-axis counterweights.

## Counts

- generated candidates: 373818
- actual-anchor rescored candidates: 1835
- saved candidates: 93

## Top Saved

```csv
file,bucket,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,mean_abs_move_vs_raw05,target_mask,cell_gate,alpha,base_file,counter_file
submission_raw05_jepa_q3cw_7bb6b32f.csv,low_bad,0.5778395975,0.5768995034,3.58e-08,0.0015968139,0.0014701157,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_ce178c95.csv
submission_raw05_jepa_q3cw_102b3662.csv,low_bad,0.5778396005,0.5768935683,8.05e-08,0.0016069095,0.0014775134,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_q3cw_7dd0dee7.csv,low_bad,0.5778396152,0.5768936704,7.95e-08,0.0015782013,0.0014764132,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_q3cw_5191c267.csv,low_bad,0.5778396299,0.5768937726,7.86e-08,0.0015494938,0.001475313,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_q3cw_eb566388.csv,low_bad,0.5778396545,0.5768999054,3.3e-08,0.0015247944,0.0014666322,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_f883e40c.csv
submission_raw05_jepa_q3cw_8b80cfd5.csv,low_bad,0.5778396694,0.5769000078,3.22e-08,0.0014960887,0.0014655321,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_f883e40c.csv
submission_raw05_jepa_q3cw_abc1c8ea.csv,low_bad,0.577839677,0.5768995159,3.3e-08,0.001604329,0.0014685635,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_5f4882be.csv
submission_raw05_jepa_q3cw_5782e96a.csv,low_bad,0.5778396844,0.5769001102,3.15e-08,0.0014673838,0.0014644319,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_f883e40c.csv
submission_raw05_jepa_q3cw_6550b7e5.csv,low_bad,0.5778396955,0.5768936837,7.66e-08,0.0015857659,0.0014748525,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_d7470f9d.csv
submission_raw05_jepa_q3cw_b994521a.csv,low_bad,0.5778396969,0.576899519,3.23e-08,0.0016062078,0.0014681841,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_339ccb2f.csv
submission_raw05_jepa_q3cw_54ac9a55.csv,low_bad,0.5778397102,0.5768937859,7.56e-08,0.0015570584,0.0014737523,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_d7470f9d.csv
submission_raw05_jepa_q3cw_551805f0.csv,low_bad,0.5778397156,0.5768936871,7.59e-08,0.0015876571,0.001474471,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_05274703.csv
submission_raw05_jepa_q3cw_339ab5c3.csv,low_bad,0.5778397168,0.5768995222,3.16e-08,0.0016080867,0.0014678047,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_eca8ad07.csv
submission_raw05_jepa_q3cw_1d5ea860.csv,low_bad,0.5778397303,0.5768937892,7.49e-08,0.0015589496,0.0014733708,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_05274703.csv
submission_raw05_jepa_q3cw_6446727c.csv,low_bad,0.5778397357,0.5768936904,7.52e-08,0.0015895483,0.0014740895,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_83b273ba.csv
submission_raw05_jepa_q3cw_88bcd5ec.csv,low_bad,0.5778397368,0.5768995254,3.09e-08,0.0016099656,0.0014674253,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_e164c924.csv
submission_raw05_jepa_q3cw_ec6b6771.csv,low_bad,0.5778397504,0.5768937926,7.42e-08,0.0015608408,0.0014729893,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_83b273ba.csv
submission_raw05_jepa_q3cw_16f296ab.csv,strict_raw,0.5778404619,0.5769156751,-6e-08,0.0017561196,0.0015745627,all,all,0.52,submission_raw05_jepa_targetw_48b7aa98.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_q3cw_bc276882.csv,strict_raw,0.5778404762,0.5769206942,-1.135e-07,0.0017721172,0.0015669421,all,all,0.52,submission_raw05_jepa_targetw_9be9c11e.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_q3cw_99af0cd6.csv,strict_raw,0.5778404502,0.57692099,-1.078e-07,0.0017699559,0.0015686922,all,all,0.52,submission_raw05_jepa_targetw_905fa678.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_q3cw_cc071bf7.csv,strict_raw,0.5778404687,0.5769211322,-1.095e-07,0.0017391303,0.0015673383,all,all,0.52,submission_raw05_jepa_targetw_5759afa9.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_q3cw_4b52687a.csv,actual_probe,0.5778389213,0.5769236899,9.29e-08,0.0017760658,0.0015628849,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_05ec9908.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_q3cw_9650d825.csv,actual_probe,0.5778389924,0.5769236989,8.57e-08,0.0017836113,0.0015611167,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_05ec9908.csv,submission_raw05_jepa_targetw_d7470f9d.csv
submission_raw05_jepa_q3cw_c98b3f15.csv,actual_probe,0.5778390102,0.5769237012,8.39e-08,0.0017854978,0.0015606746,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_05ec9908.csv,submission_raw05_jepa_targetw_05274703.csv
submission_raw05_jepa_q3cw_013cdb3e.csv,actual_probe,0.5778390281,0.5769237035,8.21e-08,0.0017873843,0.0015602361,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_05ec9908.csv,submission_raw05_jepa_targetw_83b273ba.csv
submission_raw05_jepa_q3cw_1854b49d.csv,actual_probe,0.5778389398,0.576923829,9.13e-08,0.0017453177,0.0015615511,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_24d8df9e.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_q3cw_6023184b.csv,actual_probe,0.577839011,0.576923838,8.41e-08,0.0017528633,0.0015597828,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_24d8df9e.csv,submission_raw05_jepa_targetw_d7470f9d.csv
submission_raw05_jepa_q3cw_99d2e2af.csv,actual_probe,0.5778390288,0.5769238403,8.23e-08,0.0017547498,0.0015593407,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_24d8df9e.csv,submission_raw05_jepa_targetw_05274703.csv
submission_raw05_jepa_q3cw_96763236.csv,raw_boundary,0.5778390466,0.5769238426,8.06e-08,0.0017566363,0.0015589022,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_24d8df9e.csv,submission_raw05_jepa_targetw_83b273ba.csv
submission_raw05_jepa_q3cw_c6d8a9f5.csv,actual_probe,0.5778389183,0.5769242632,8.96e-08,0.0017788428,0.0015621725,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_d611b72b.csv,submission_raw05_jepa_targetw_ce178c95.csv
submission_raw05_jepa_q3cw_d5995367.csv,actual_probe,0.5778389886,0.5769242714,8.25e-08,0.0017863391,0.0015604126,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_d611b72b.csv,submission_raw05_jepa_targetw_5f4882be.csv
submission_raw05_jepa_q3cw_be07a5cb.csv,actual_probe,0.5778390062,0.5769242735,8.07e-08,0.0017882132,0.0015599732,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_d611b72b.csv,submission_raw05_jepa_targetw_339ccb2f.csv
submission_raw05_jepa_q3cw_ce32f7e6.csv,actual_probe,0.5778390238,0.5769242755,7.89e-08,0.0017900874,0.0015595371,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_d611b72b.csv,submission_raw05_jepa_targetw_eca8ad07.csv
submission_raw05_jepa_q3cw_9751e65e.csv,actual_probe,0.5778390415,0.5769242776,7.72e-08,0.0017919617,0.0015591035,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_d611b72b.csv,submission_raw05_jepa_targetw_e164c924.csv
submission_raw05_jepa_q3cw_66fa5642.csv,actual_probe,0.5778389804,0.5769247287,8.47e-08,0.0016801389,0.0015577807,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_d5c8a524.csv,submission_raw05_jepa_targetw_f883e40c.csv
submission_raw05_jepa_q3cw_47dadfc1.csv,actual_probe,0.5778389992,0.5769248681,8.34e-08,0.0016493939,0.0015564469,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_d611b72b.csv,submission_raw05_jepa_targetw_f883e40c.csv
submission_raw05_jepa_q3cw_b8579efe.csv,raw_boundary,0.5778390688,0.5769253708,9.97e-08,0.0017828514,0.0015668949,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_62a509a1.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
submission_raw05_jepa_q3cw_67e80af7.csv,raw_boundary,0.5778390723,0.5769253974,9.94e-08,0.001778236,0.0015666603,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_c9b9fff4.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_q3cw_7917789f.csv,raw_boundary,0.5778390696,0.576925437,9.13e-08,0.001780898,0.0015636041,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_ba0357ce.csv,submission_raw05_jepa_targetw_ce178c95.csv
submission_raw05_jepa_q3cw_85595d47.csv,raw_boundary,0.5778390908,0.5769255396,9.77e-08,0.0017474105,0.0015653064,non_q3_s4,all,0.52,submission_raw05_jepa_targetw_1e8220d5.csv,submission_raw05_jepa_targetw_3263040f.csv
```

## Best By Target Mask / Cell Gate

```csv
target_mask,cell_gate,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,alpha,base_file,counter_file
non_q3_s4,all,0.5778389152,0.5769295601,4.89e-08,0.0017926575,0.52,submission_raw05_jepa_targetw_24d8df9e.csv,submission_raw05_jepa_targetw_ce178c95.csv
non_q3,all,0.5778389983,0.5769295725,8.61e-08,0.0017689908,0.52,submission_raw05_jepa_targetw_05ec9908.csv,submission_raw05_jepa_targetw_f883e40c.csv
q1_q2_s1,all,0.5778401432,0.5768911722,9.65e-08,0.0023872928,0.52,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_f883e40c.csv
all,all,0.5778404325,0.5769268586,-1.566e-07,0.0017864815,0.52,submission_raw05_jepa_targetw_5759afa9.csv,submission_raw05_jepa_targetw_ce178c95.csv
q2_s1_s4,all,0.5778411807,0.5768903709,5.36e-08,0.0021253669,0.28,submission_raw05_jepa_targetw_05ec9908.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv
all,opposing,0.5778417637,0.5768876438,8.07e-08,0.0021941222,0.38,submission_raw05_jepa_targetw_3af15cc3.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv
s_all,all,0.5778419591,0.5769219086,-1.001e-07,0.0016592532,0.52,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_95e362f3.csv
q2_s1,all,0.5778426999,0.5768994949,2.37e-08,0.0017964245,0.52,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_f883e40c.csv
q1_q2_s1,closer,0.577843672,0.5769063903,-7.9e-09,0.0017909273,0.52,submission_raw05_jepa_targetw_f8c12205.csv,submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv
q2_s1_s4,closer,0.5778440377,0.5768983281,-1.58e-08,0.0017893766,0.52,submission_raw05_jepa_targetw_23629fbf.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv
all,closer,0.5778449501,0.5769329508,-6.046e-07,0.0017818065,0.52,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_f883e40c.csv
all,closer_or_opposing,0.577852389,0.576888694,-1.1626e-06,0.0023647868,0.38,submission_raw05_jepa_targetw_48b7aa98.csv,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_jepa_q3cw_7bb6b32f.csv,250,True,0,0,0.0631543626,0.9798267621
submission_raw05_jepa_q3cw_102b3662.csv,250,True,0,0,0.0631543626,0.9798183111
submission_raw05_jepa_q3cw_7dd0dee7.csv,250,True,0,0,0.0631543626,0.9798183111
submission_raw05_jepa_q3cw_5191c267.csv,250,True,0,0,0.0631543626,0.9798183111
submission_raw05_jepa_q3cw_eb566388.csv,250,True,0,0,0.0631543626,0.9798267621
submission_raw05_jepa_q3cw_8b80cfd5.csv,250,True,0,0,0.0631543626,0.9798267621
submission_raw05_jepa_q3cw_abc1c8ea.csv,250,True,0,0,0.0631528005,0.979826712
submission_raw05_jepa_q3cw_5782e96a.csv,250,True,0,0,0.0631543626,0.9798267621
submission_raw05_jepa_q3cw_6550b7e5.csv,250,True,0,0,0.0631528005,0.9798182574
submission_raw05_jepa_q3cw_b994521a.csv,250,True,0,0,0.06315241,0.9798266995
submission_raw05_jepa_q3cw_54ac9a55.csv,250,True,0,0,0.0631528005,0.9798182574
submission_raw05_jepa_q3cw_551805f0.csv,250,True,0,0,0.06315241,0.9798182439
submission_raw05_jepa_q3cw_339ab5c3.csv,250,True,0,0,0.0631520195,0.979826687
submission_raw05_jepa_q3cw_1d5ea860.csv,250,True,0,0,0.06315241,0.9798182439
submission_raw05_jepa_q3cw_6446727c.csv,250,True,0,0,0.0631520195,0.9798182305
submission_raw05_jepa_q3cw_88bcd5ec.csv,250,True,0,0,0.063151629,0.9798266744
submission_raw05_jepa_q3cw_ec6b6771.csv,250,True,0,0,0.0631520195,0.9798182305
submission_raw05_jepa_q3cw_16f296ab.csv,250,True,0,0,0.0632220414,0.9798051113
submission_raw05_jepa_q3cw_bc276882.csv,250,True,0,0,0.0632215417,0.9798128793
submission_raw05_jepa_q3cw_99af0cd6.csv,250,True,0,0,0.0632220414,0.9798128962
submission_raw05_jepa_q3cw_cc071bf7.csv,250,True,0,0,0.0632220414,0.9798128962
submission_raw05_jepa_q3cw_4b52687a.csv,250,True,0,0,0.063209269,0.9798283687
submission_raw05_jepa_q3cw_9650d825.csv,250,True,0,0,0.0632077057,0.979828315
submission_raw05_jepa_q3cw_c98b3f15.csv,250,True,0,0,0.0632073149,0.9798283016
submission_raw05_jepa_q3cw_013cdb3e.csv,250,True,0,0,0.0632069241,0.9798282882
submission_raw05_jepa_q3cw_1854b49d.csv,250,True,0,0,0.063209269,0.9798283687
submission_raw05_jepa_q3cw_6023184b.csv,250,True,0,0,0.0632077057,0.979828315
submission_raw05_jepa_q3cw_99d2e2af.csv,250,True,0,0,0.0632073149,0.9798283016
submission_raw05_jepa_q3cw_96763236.csv,250,True,0,0,0.0632069241,0.9798282882
submission_raw05_jepa_q3cw_c6d8a9f5.csv,250,True,0,0,0.063209269,0.979829033
submission_raw05_jepa_q3cw_d5995367.csv,250,True,0,0,0.0632077057,0.9798289829
submission_raw05_jepa_q3cw_be07a5cb.csv,250,True,0,0,0.0632073149,0.9798289704
submission_raw05_jepa_q3cw_ce32f7e6.csv,250,True,0,0,0.0632069241,0.9798289578
submission_raw05_jepa_q3cw_9751e65e.csv,250,True,0,0,0.0632065332,0.9798289453
submission_raw05_jepa_q3cw_66fa5642.csv,250,True,0,0,0.063209269,0.979829033
submission_raw05_jepa_q3cw_47dadfc1.csv,250,True,0,0,0.063209269,0.979829033
submission_raw05_jepa_q3cw_b8579efe.csv,250,True,0,0,0.0632220414,0.9798284571
submission_raw05_jepa_q3cw_67e80af7.csv,250,True,0,0,0.0632220414,0.9798284571
submission_raw05_jepa_q3cw_7917789f.csv,250,True,0,0,0.0632215417,0.9798291125
submission_raw05_jepa_q3cw_85595d47.csv,250,True,0,0,0.0632220414,0.9798284571
```
