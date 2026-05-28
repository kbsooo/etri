# Raw05 JEPA Structural Constrained Refine

Micro-refines the unique structural constraint hit `submission_raw05_jepa_axistrade_931a03a1.csv` by combining raw05 shrinkage, posterior-safe donor offsets, and Q3/S4 motif re-anchoring.

## Counts

- generated candidates: `1600`
- prefilter candidates: `1600`
- saved shortlist: `72`
- scan structural hits: `196`
- scored structural hits: `196`

## Pair Summary

```csv
base_file,donor_file,n,struct_hits,best_actual,best_posterior,best_bad_abs,best_raw_abs,best_orth,best_selection
submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siggate_fd0e9622.csv,425,52,0.5778281587,0.5769032852,1.112e-05,2e-10,0.0075049265,0.5778281587
submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,336,48,0.5778280168,0.5769039252,8.2103e-06,1e-10,0.0075050018,0.5778280168
submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_efback_9c50051c.csv,408,48,0.5778281991,0.5769030597,1.04267e-05,1e-10,0.0075049265,0.5778281991
submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_axisrepair_78029f2c.csv,431,48,0.5778282266,0.5769028575,3.56e-08,0.0,0.0075049265,0.5778282266
```

## Shortlist

```csv
file,bucket,base_file,donor_file,raw_mask,donor_mask,motif_mask,raw_alpha,donor_alpha,motif_alpha,cap,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,q3s4_motif_proj,q3s4_motif_cos,q3s4_motif_orth_ratio,mean_abs_move_vs_base,selection_score,rank_score
submission_raw05_jepa_structrefine_90e28f7d.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_axisrepair_78029f2c.csv,ctx,ctx,q3s4,0.0,0.065,0.04,0.024,0.5778283753,0.5769037626,3.17e-08,-1.6071e-06,0.9957347472,0.9999848747,0.0075050771,6.1121e-06,0.5778283753,280.78
submission_raw05_jepa_structrefine_d0fad70b.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.0,0.065,0.04,0.024,0.5778282779,0.5769042627,3.64e-08,8.2103e-06,0.9957347472,0.9999848747,0.0075050771,6.2587e-06,0.5778282779,280.92
submission_raw05_jepa_structrefine_959293c3.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siggate_fd0e9622.csv,ctx,ctx,q3s4,0.0,0.035,0.04,0.024,0.577828418,0.576904234,1.25e-08,1.84862e-05,0.9957347472,0.9999848747,0.0075050771,3.7255e-06,0.577828418,289.98
submission_raw05_jepa_structrefine_4869923a.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_efback_9c50051c.csv,ctx,ctx,q3s4,0.0,0.035,0.04,0.024,0.5778284281,0.5769041777,1.21e-08,1.88595e-05,0.9957347472,0.9999848747,0.0075050771,3.7658e-06,0.5778284281,293.34
submission_raw05_jepa_structrefine_1c1cff28.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_axisrepair_78029f2c.csv,ctx,ctx,q3s4,0.0,0.065,0.024,0.024,0.5778283817,0.5769037729,3.09e-08,-1.0829e-06,0.9956636596,0.9999843641,0.0076304973,6.0355e-06,0.5778283817,298.6
submission_raw05_jepa_structrefine_8171850d.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.0,0.065,0.024,0.024,0.5778282843,0.5769042729,3.55e-08,8.7345e-06,0.9956636596,0.9999843641,0.0076304973,6.1821e-06,0.5778282843,302.52
submission_raw05_jepa_structrefine_10df401d.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siggate_fd0e9622.csv,ctx,ctx,q3s4,0.0,0.035,0.024,0.024,0.5778284244,0.5769042443,1.17e-08,1.90104e-05,0.9956636596,0.9999843641,0.0076304973,3.6489e-06,0.5778284244,311.96
submission_raw05_jepa_structrefine_b76963a8.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.0,0.035,0.04,0.024,0.5778283826,0.5769043941,1.28e-08,3.17301e-05,0.9957347472,0.9999848747,0.0075050771,3.4585e-06,0.5778283826,312.08
submission_raw05_jepa_structrefine_669071ec.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_efback_9c50051c.csv,ctx,ctx,q3s4,0.0,0.035,0.024,0.024,0.5778284345,0.5769041879,1.13e-08,1.93837e-05,0.9956636596,0.9999843641,0.0076304973,3.6892e-06,0.5778284345,316.06
submission_raw05_jepa_structrefine_ebae0f58.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_axisrepair_78029f2c.csv,ctx,ctx,q3s4,0.0,0.065,0.012,0.024,0.5778283865,0.5769037805,3.02e-08,-6.898e-07,0.9956103439,0.9999839755,0.0077245696,5.978e-06,0.5778283865,316.5
submission_raw05_jepa_structrefine_f0956d83.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_axisrepair_78029f2c.csv,ctx,ctx,q3s4,0.0,0.035,0.04,0.024,0.577828435,0.5769041248,1.03e-08,2.64438e-05,0.9957347472,0.9999848747,0.0075050771,3.3795e-06,0.577828435,316.94
submission_raw05_jepa_structrefine_73c441ff.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.0,0.065,0.012,0.024,0.5778282891,0.5769042806,3.49e-08,9.1276e-06,0.9956103439,0.9999839755,0.0077245696,6.1247e-06,0.5778282891,322.54
submission_raw05_jepa_structrefine_325d1e51.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_axisrepair_78029f2c.csv,ctx,ctx,q3s4,0.0,0.065,0.0,0.024,0.5778283913,0.5769037882,2.96e-08,-2.966e-07,0.9955570283,0.9999835822,0.0078186482,5.9205e-06,0.5778283913,329.58
submission_raw05_jepa_structrefine_b7f47aa1.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.0,0.035,0.024,0.024,0.577828389,0.5769044043,1.2e-08,3.22543e-05,0.9956636596,0.9999843641,0.0076304973,3.3819e-06,0.577828389,333.7
submission_raw05_jepa_structrefine_95c7a9d1.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siggate_fd0e9622.csv,ctx,ctx,q3s4,0.0,0.035,0.012,0.024,0.5778284292,0.576904252,1.11e-08,1.94035e-05,0.9956103439,0.9999839755,0.0077245696,3.5915e-06,0.5778284292,333.92
submission_raw05_jepa_structrefine_b418676d.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.0,0.065,0.0,0.024,0.5778282939,0.5769042883,3.43e-08,9.5208e-06,0.9955570283,0.9999835822,0.0078186482,6.0672e-06,0.5778282939,336.96
submission_raw05_jepa_structrefine_20eb9ac1.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_axisrepair_78029f2c.csv,ctx,ctx,q3s4,0.0,0.035,0.024,0.024,0.5778284414,0.5769041351,9.5e-09,2.6968e-05,0.9956636596,0.9999843641,0.0076304973,3.3029e-06,0.5778284414,338.42
submission_raw05_jepa_structrefine_abf6bddd.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_efback_9c50051c.csv,ctx,ctx,q3s4,0.0,0.035,0.012,0.024,0.5778284393,0.5769041956,1.07e-08,1.97768e-05,0.9956103439,0.9999839755,0.0077245696,3.6317e-06,0.5778284393,340.74
submission_raw05_jepa_structrefine_04ad10f8.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.0,0.095,0.04,0.024,0.5778281734,0.5769041314,6e-08,-1.53093e-05,0.9957347472,0.9999848747,0.0075050771,9.059e-06,0.5778281734,341.7
submission_raw05_jepa_structrefine_bef87cd7.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siggate_fd0e9622.csv,ctx,ctx,q3s4,0.0,0.065,0.04,0.024,0.5778283438,0.5769039655,3.58e-08,-1.63853e-05,0.9957347472,0.9999848747,0.0075050771,6.7547e-06,0.5778283438,344.04
submission_raw05_jepa_structrefine_5fd7ffd5.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_efback_9c50051c.csv,ctx,ctx,q3s4,0.0,0.065,0.04,0.024,0.5778283625,0.5769038608,3.51e-08,-1.56921e-05,0.9957347472,0.9999848747,0.0075050771,6.8294e-06,0.5778283625,344.9
submission_raw05_jepa_structrefine_66a90676.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_axisrepair_78029f2c.csv,ctx,ctx_q3light,q3s4,0.0,0.065,0.04,0.024,0.5778283946,0.5769037669,2.92e-08,5.269e-07,0.9954501608,0.9999834333,0.0078543771,6.1588e-06,0.5778283946,349.1
submission_raw05_jepa_structrefine_c8dd7c1f.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_axisrepair_78029f2c.csv,ctx,ctx_q3light,q3s4,0.0,0.035,0.04,0.024,0.5778284454,0.5769041271,8.9e-09,2.75929e-05,0.9955815083,0.9999841222,0.0076894202,3.34e-06,0.5778284454,351.3
submission_raw05_jepa_structrefine_832cc482.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.0,0.095,0.024,0.024,0.5778281798,0.5769041416,5.92e-08,-1.47851e-05,0.9956636596,0.9999843641,0.0076304973,8.9823e-06,0.5778281798,352.42
submission_raw05_jepa_structrefine_84111a02.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siggate_fd0e9622.csv,ctx,ctx,q3s4,0.0,0.035,0.0,0.024,0.577828434,0.5769042597,1.04e-08,1.97967e-05,0.9955570283,0.9999835822,0.0078186482,3.534e-06,0.577828434,353.66
submission_raw05_jepa_structrefine_d605bc5c.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siggate_fd0e9622.csv,ctx,ctx_s4light,q3s4,0.0,0.035,0.04,0.024,0.5778284321,0.5769042562,9.7e-09,2.06157e-05,0.9954257981,0.9999836945,0.0077922816,3.8526e-06,0.5778284321,354.2
submission_raw05_jepa_structrefine_c79ddd5e.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.0,0.035,0.012,0.024,0.5778283938,0.576904412,1.14e-08,3.26474e-05,0.9956103439,0.9999839755,0.0077245696,3.3244e-06,0.5778283938,354.96
submission_raw05_jepa_structrefine_f9d65d61.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_axisrepair_78029f2c.csv,ctx,ctx_s4light,q3s4,0.0,0.065,0.04,0.024,0.5778283963,0.5769037933,2.75e-08,1.5892e-06,0.9952755971,0.9999830022,0.0079559388,6.3672e-06,0.5778283963,356.94
submission_raw05_jepa_structrefine_8ffabf91.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_efback_9c50051c.csv,ctx,ctx,q3s4,0.0,0.065,0.024,0.024,0.5778283689,0.576903871,3.43e-08,-1.51679e-05,0.9956636596,0.9999843641,0.0076304973,6.7528e-06,0.5778283689,357.7
submission_raw05_jepa_structrefine_6d75e10d.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_axisrepair_78029f2c.csv,ctx,ctx,q3s4,0.0,0.035,0.012,0.024,0.5778284462,0.5769041427,8.8e-09,2.73611e-05,0.9956103439,0.9999839755,0.0077245696,3.2454e-06,0.5778284462,360.32
submission_raw05_jepa_structrefine_7e8637db.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siggate_fd0e9622.csv,ctx,ctx,q3s4,0.0,0.065,0.024,0.024,0.5778283502,0.5769039757,3.5e-08,-1.58611e-05,0.9956636596,0.9999843641,0.0076304973,6.678e-06,0.5778283502,360.82
submission_raw05_jepa_structrefine_b797cb04.csv,struct_rank_fallback,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_efback_9c50051c.csv,ctx,ctx,q3s4,0.0,0.035,0.0,0.024,0.5778284441,0.5769042033,1e-08,2.017e-05,0.9955570283,0.9999835822,0.0078186482,3.5743e-06,0.5778284441,362.28
submission_raw05_jepa_structrefine_3bf97d82.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.0,0.095,0.012,0.024,0.5778281846,0.5769041493,5.86e-08,-1.43919e-05,0.9956103439,0.9999839755,0.0077245696,8.9249e-06,0.5778281846,365.46
submission_raw05_jepa_structrefine_4b29b2d2.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.0,0.095,0.0,0.024,0.5778281894,0.576904157,5.79e-08,-1.39988e-05,0.9955570283,0.9999835822,0.0078186482,8.8674e-06,0.5778281894,375.16
submission_raw05_jepa_structrefine_97d8972b.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx_s4light,q3s4,0.0,0.095,0.04,0.024,0.5778282117,0.5769041915,5.24e-08,-9.5291e-06,0.9948961712,0.9999809701,0.0084179209,9.6314e-06,0.5778282117,416.5
submission_raw05_jepa_structrefine_e17ff178.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx_q3light,q3s4,0.0,0.095,0.04,0.024,0.5778282232,0.576904125,5.47e-08,-1.10395e-05,0.9951090142,0.9999810729,0.0083949187,9.4628e-06,0.5778282232,418.56
submission_raw05_jepa_structrefine_f00823b1.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx_s4light,q3s4,0.0,0.095,0.024,0.024,0.5778282181,0.5769042017,5.16e-08,-9.0049e-06,0.9948250837,0.9999804119,0.0085402708,9.6103e-06,0.5778282181,422.68
submission_raw05_jepa_structrefine_a4ce40c1.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx_s4light,q3s4,0.0,0.095,0.012,0.024,0.5778282229,0.5769042094,5.1e-08,-8.6118e-06,0.994771768,0.9999799876,0.0086321006,9.5948e-06,0.5778282229,429.2
submission_raw05_jepa_structrefine_02f03cca.csv,struct_lowbad,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx_q3light,q3s4,0.0,0.095,0.024,0.024,0.5778282296,0.5769041352,5.39e-08,-1.05153e-05,0.9950379266,0.9999805053,0.0085196324,9.5074e-06,0.5778282296,431.38
submission_raw05_jepa_structrefine_60252531.csv,struct_lowbad,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx_s4light,q3s4,0.0,0.095,0.0,0.024,0.5778282277,0.5769042171,5.03e-08,-8.2186e-06,0.9947184523,0.9999795584,0.0087239865,9.5796e-06,0.5778282277,433.64
submission_raw05_jepa_structrefine_0261abc4.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.0,0.14,0.04,0.024,0.5778280168,0.5769039346,9.57e-08,-5.0588e-05,0.9957347472,0.9999848747,0.0075050771,1.32593e-05,0.5778280168,498.3
submission_raw05_jepa_structrefine_41eafdf2.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.0,0.14,0.024,0.024,0.5778280232,0.5769039449,9.49e-08,-5.00638e-05,0.9956636596,0.9999843641,0.0076304973,1.31827e-05,0.5778280232,510.66
submission_raw05_jepa_structrefine_6ee04bfa.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.0,0.14,0.012,0.024,0.577828028,0.5769039525,9.42e-08,-4.96707e-05,0.9956103439,0.9999839755,0.0077245696,1.31252e-05,0.577828028,525.66
submission_raw05_jepa_structrefine_ff046a1e.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.0,0.14,0.0,0.024,0.5778280328,0.5769039602,9.36e-08,-4.92775e-05,0.9955570283,0.9999835822,0.0078186482,1.30678e-05,0.5778280328,536.92
submission_raw05_jepa_structrefine_2ab9818c.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_axisrepair_78029f2c.csv,ctx,ctx,q3s4,0.0,0.14,0.04,0.024,0.5778282266,0.5769028575,8.57e-08,-7.17331e-05,0.9957347472,0.9999848747,0.0075050771,1.29434e-05,0.5778282266,551.16
submission_raw05_jepa_structrefine_2a770fa9.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siggate_fd0e9622.csv,ctx,ctx,q3s4,0.0,0.14,0.04,0.024,0.5778281587,0.5769032946,9.47e-08,-0.0001035624,0.9957347472,0.9999848747,0.0075050771,1.43274e-05,0.5778281587,563.14
submission_raw05_jepa_structrefine_5d94b630.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_efback_9c50051c.csv,ctx,ctx,q3s4,0.0,0.14,0.04,0.024,0.5778281991,0.5769030692,9.31e-08,-0.000102069,0.9957347472,0.9999848747,0.0075050771,1.44885e-05,0.5778281991,564.04
submission_raw05_jepa_structrefine_973bcf56.csv,struct_lowbad,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_axisrepair_78029f2c.csv,ctx,ctx,q3s4,0.0,0.14,0.024,0.024,0.577828233,0.5769028678,8.48e-08,-7.12089e-05,0.9956636596,0.9999843641,0.0076304973,1.28668e-05,0.577828233,568.0
submission_raw05_jepa_structrefine_46c0e0d8.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siggate_fd0e9622.csv,ctx,ctx,q3s4,0.0,0.14,0.024,0.024,0.5778281651,0.5769033049,9.39e-08,-0.0001030382,0.9956636596,0.9999843641,0.0076304973,1.42508e-05,0.5778281651,580.38
submission_raw05_jepa_structrefine_58e8e127.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_efback_9c50051c.csv,ctx,ctx,q3s4,0.0,0.14,0.024,0.024,0.5778282055,0.5769030794,9.23e-08,-0.0001015448,0.9956636596,0.9999843641,0.0076304973,1.44119e-05,0.5778282055,581.88
submission_raw05_jepa_structrefine_e2947c5b.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siggate_fd0e9622.csv,ctx,ctx,q3s4,0.0,0.14,0.012,0.024,0.5778281699,0.5769033126,9.32e-08,-0.000102645,0.9956103439,0.9999839755,0.0077245696,1.41933e-05,0.5778281699,598.36
submission_raw05_jepa_structrefine_95da02b2.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_efback_9c50051c.csv,ctx,ctx,q3s4,0.0,0.14,0.012,0.024,0.5778282103,0.5769030871,9.17e-08,-0.0001011517,0.9956103439,0.9999839755,0.0077245696,1.43544e-05,0.5778282103,600.42
submission_raw05_jepa_structrefine_82937d75.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siggate_fd0e9622.csv,ctx,ctx,q3s4,0.0,0.14,0.0,0.024,0.5778281747,0.5769033203,9.26e-08,-0.0001022519,0.9955570283,0.9999835822,0.0078186482,1.41359e-05,0.5778281747,612.5
submission_raw05_jepa_structrefine_dd98c58a.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_efback_9c50051c.csv,ctx,ctx,q3s4,0.0,0.14,0.0,0.024,0.5778282151,0.5769030948,9.11e-08,-0.0001007585,0.9955570283,0.9999835822,0.0078186482,1.42969e-05,0.5778282151,615.12
submission_raw05_jepa_structrefine_5e75f84e.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx_s4light,q3s4,0.0,0.14,0.04,0.024,0.5778280733,0.5769040232,8.45e-08,-4.207e-05,0.994498951,0.9999783443,0.008979779,1.41686e-05,0.5778280733,628.4
submission_raw05_jepa_structrefine_1023cd8f.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx_q3light,q3s4,0.0,0.14,0.04,0.024,0.5778280902,0.5769039252,8.79e-08,-4.42958e-05,0.9948126144,0.9999789651,0.0088497376,1.3997e-05,0.5778280902,629.2
submission_raw05_jepa_structrefine_a2892b08.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx_s4light,q3s4,0.0,0.14,0.024,0.024,0.5778280797,0.5769040335,8.37e-08,-4.15458e-05,0.9944278635,0.9999777633,0.0090991941,1.41477e-05,0.5778280797,632.22
submission_raw05_jepa_structrefine_9669037f.csv,struct_local,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.006,0.14,0.04,0.024,0.5778281092,0.5769065684,6.73e-08,-2.07327e-05,0.9957347472,0.9999848747,0.0075050771,1.38234e-05,0.5778295992,632.36
submission_raw05_jepa_structrefine_fc2f0b8e.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx_q3light,q3s4,0.0,0.14,0.024,0.024,0.5778280966,0.5769039354,8.71e-08,-4.37716e-05,0.9947415268,0.9999783704,0.0089737184,1.40458e-05,0.5778280966,633.7
submission_raw05_jepa_structrefine_c13b7418.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx_s4light,q3s4,0.0,0.14,0.012,0.024,0.5778280845,0.5769040412,8.31e-08,-4.11526e-05,0.9943745478,0.9999773219,0.0091888708,1.41324e-05,0.5778280845,636.38
submission_raw05_jepa_structrefine_1388b6d5.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx_s4light,q3s4,0.0,0.14,0.0,0.024,0.5778280893,0.5769040488,8.24e-08,-4.07595e-05,0.9943212322,0.9999768757,0.0092786434,1.41173e-05,0.5778280893,638.04
submission_raw05_jepa_structrefine_0d4b9362.csv,struct_local,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx_q3light,ctx,q3s4,0.006,0.14,0.04,0.024,0.5778281165,0.5769066068,6.53e-08,-2.07588e-05,0.9954958135,0.999984875,0.0075050018,1.38097e-05,0.5778296429,639.96
submission_raw05_jepa_structrefine_cdc8a4b0.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx_q3light,q3s4,0.0,0.14,0.012,0.024,0.5778281014,0.5769039431,8.65e-08,-4.33785e-05,0.9946882111,0.9999779188,0.0090667401,1.40839e-05,0.5778281014,640.34
submission_raw05_jepa_structrefine_6f7eaed6.csv,struct_hit,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx_q3light,q3s4,0.0,0.14,0.0,0.024,0.5778281062,0.5769039508,8.59e-08,-4.29853e-05,0.9946348955,0.9999774623,0.0091597918,1.4123e-05,0.5778281062,646.82
submission_raw05_jepa_structrefine_01f8ecbf.csv,struct_local,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.006,0.14,0.024,0.024,0.5778281156,0.5769065786,6.65e-08,-2.02085e-05,0.9956636596,0.9999843641,0.0076304973,1.37467e-05,0.5778296153,648.24
submission_raw05_jepa_structrefine_4f6ce192.csv,struct_local,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx_q3light,ctx,q3s4,0.006,0.14,0.024,0.024,0.5778281229,0.576906617,6.45e-08,-2.02346e-05,0.9954247259,0.9999843643,0.0076304521,1.37782e-05,0.577829659,655.8
submission_raw05_jepa_structrefine_10144124.csv,struct_local,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.006,0.14,0.04,0.04,0.5778281305,0.5769066147,6.57e-08,-2.13935e-05,0.9957347472,0.9999848747,0.0075050771,1.3795e-05,0.5778296644,658.1
submission_raw05_jepa_structrefine_6a7fec4d.csv,struct_local,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.006,0.14,0.04,0.065,0.5778281342,0.5769066249,6.52e-08,-2.12984e-05,0.9957347472,0.9999848747,0.0075050771,1.37802e-05,0.5778296778,662.38
submission_raw05_jepa_structrefine_5dc9b178.csv,struct_local,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.006,0.14,0.012,0.024,0.5778281204,0.5769065863,6.59e-08,-1.98154e-05,0.9956103439,0.9999839755,0.0077245696,1.36893e-05,0.5778296274,665.48
submission_raw05_jepa_structrefine_e8aca262.csv,struct_local,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx_q3light,ctx,q3s4,0.006,0.14,0.04,0.04,0.5778281378,0.5769066531,6.37e-08,-2.14196e-05,0.9954958135,0.999984875,0.0075050018,1.37813e-05,0.5778297082,667.62
submission_raw05_jepa_structrefine_4734d036.csv,struct_local,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx_q3light,ctx,q3s4,0.006,0.14,0.012,0.024,0.5778281277,0.5769066247,6.39e-08,-1.98415e-05,0.9953714103,0.9999839756,0.0077245471,1.37804e-05,0.5778296711,672.8
submission_raw05_jepa_structrefine_52ab3760.csv,struct_local,submission_raw05_jepa_axistrade_931a03a1.csv,submission_raw05_jepa_siganchor_3644a42f.csv,ctx,ctx,q3s4,0.006,0.14,0.024,0.04,0.5778281369,0.5769066249,6.48e-08,-2.08693e-05,0.9956636596,0.9999843641,0.0076304973,1.37184e-05,0.5778296806,675.52
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_jepa_structrefine_90e28f7d.csv,250,True,0,0,0.0630759627,0.979797496
submission_raw05_jepa_structrefine_d0fad70b.csv,250,True,0,0,0.0630770473,0.9797980581
submission_raw05_jepa_structrefine_959293c3.csv,250,True,0,0,0.0630741962,0.9797974294
submission_raw05_jepa_structrefine_4869923a.csv,250,True,0,0,0.0630739726,0.9797974083
submission_raw05_jepa_structrefine_1c1cff28.csv,250,True,0,0,0.0630759627,0.979797496
submission_raw05_jepa_structrefine_8171850d.csv,250,True,0,0,0.0630770473,0.9797980581
submission_raw05_jepa_structrefine_10df401d.csv,250,True,0,0,0.0630741962,0.9797974294
submission_raw05_jepa_structrefine_b76963a8.csv,250,True,0,0,0.0630742316,0.9797972705
submission_raw05_jepa_structrefine_669071ec.csv,250,True,0,0,0.0630739726,0.9797974083
submission_raw05_jepa_structrefine_ebae0f58.csv,250,True,0,0,0.0630759627,0.979797496
submission_raw05_jepa_structrefine_f0956d83.csv,250,True,0,0,0.0630736476,0.9797969678
submission_raw05_jepa_structrefine_73c441ff.csv,250,True,0,0,0.0630770473,0.9797980581
submission_raw05_jepa_structrefine_325d1e51.csv,250,True,0,0,0.0630759627,0.979797496
submission_raw05_jepa_structrefine_b7f47aa1.csv,250,True,0,0,0.0630742316,0.9797972705
submission_raw05_jepa_structrefine_95c7a9d1.csv,250,True,0,0,0.0630741962,0.9797974294
submission_raw05_jepa_structrefine_b418676d.csv,250,True,0,0,0.0630770473,0.9797980581
submission_raw05_jepa_structrefine_20eb9ac1.csv,250,True,0,0,0.0630736476,0.9797969678
submission_raw05_jepa_structrefine_abf6bddd.csv,250,True,0,0,0.0630739726,0.9797974083
submission_raw05_jepa_structrefine_04ad10f8.csv,250,True,0,0,0.0630798631,0.9797988457
submission_raw05_jepa_structrefine_bef87cd7.csv,250,True,0,0,0.0630769816,0.9797983531
submission_raw05_jepa_structrefine_5fd7ffd5.csv,250,True,0,0,0.0630765664,0.9797983141
submission_raw05_jepa_structrefine_66a90676.csv,250,True,0,0,0.0630759627,0.979797496
submission_raw05_jepa_structrefine_c8dd7c1f.csv,250,True,0,0,0.0630736476,0.9797969678
submission_raw05_jepa_structrefine_832cc482.csv,250,True,0,0,0.0630798631,0.9797988457
submission_raw05_jepa_structrefine_84111a02.csv,250,True,0,0,0.0630741962,0.9797974294
submission_raw05_jepa_structrefine_d605bc5c.csv,250,True,0,0,0.0630741962,0.9797974294
submission_raw05_jepa_structrefine_c79ddd5e.csv,250,True,0,0,0.0630742316,0.9797972705
submission_raw05_jepa_structrefine_f9d65d61.csv,250,True,0,0,0.0630759627,0.979797496
submission_raw05_jepa_structrefine_8ffabf91.csv,250,True,0,0,0.0630765664,0.9797983141
submission_raw05_jepa_structrefine_6d75e10d.csv,250,True,0,0,0.0630736476,0.9797969678
submission_raw05_jepa_structrefine_7e8637db.csv,250,True,0,0,0.0630769816,0.9797983531
submission_raw05_jepa_structrefine_b797cb04.csv,250,True,0,0,0.0630739726,0.9797974083
submission_raw05_jepa_structrefine_3bf97d82.csv,250,True,0,0,0.0630798631,0.9797988457
submission_raw05_jepa_structrefine_4b29b2d2.csv,250,True,0,0,0.0630798631,0.9797988457
submission_raw05_jepa_structrefine_97d8972b.csv,250,True,0,0,0.0630798631,0.9797988457
submission_raw05_jepa_structrefine_e17ff178.csv,250,True,0,0,0.0630798631,0.9797988457
submission_raw05_jepa_structrefine_f00823b1.csv,250,True,0,0,0.0630798631,0.9797988457
submission_raw05_jepa_structrefine_a4ce40c1.csv,250,True,0,0,0.0630798631,0.9797988457
submission_raw05_jepa_structrefine_02f03cca.csv,250,True,0,0,0.0630798631,0.9797988457
submission_raw05_jepa_structrefine_60252531.csv,250,True,0,0,0.0630798631,0.9797988457
submission_raw05_jepa_structrefine_0261abc4.csv,250,True,0,0,0.0630840871,0.9798000271
submission_raw05_jepa_structrefine_41eafdf2.csv,250,True,0,0,0.0630840871,0.9798000271
submission_raw05_jepa_structrefine_6ee04bfa.csv,250,True,0,0,0.0630840871,0.9798000271
submission_raw05_jepa_structrefine_ff046a1e.csv,250,True,0,0,0.0630840871,0.9798000271
submission_raw05_jepa_structrefine_2ab9818c.csv,250,True,0,0,0.0630817509,0.9797988163
submission_raw05_jepa_structrefine_2a770fa9.csv,250,True,0,0,0.0630839456,0.9798006624
submission_raw05_jepa_structrefine_5d94b630.csv,250,True,0,0,0.0630830513,0.9798005783
submission_raw05_jepa_structrefine_973bcf56.csv,250,True,0,0,0.0630817509,0.9797988163
submission_raw05_jepa_structrefine_46c0e0d8.csv,250,True,0,0,0.0630839456,0.9798006624
submission_raw05_jepa_structrefine_58e8e127.csv,250,True,0,0,0.0630830513,0.9798005783
submission_raw05_jepa_structrefine_e2947c5b.csv,250,True,0,0,0.0630839456,0.9798006624
submission_raw05_jepa_structrefine_95da02b2.csv,250,True,0,0,0.0630830513,0.9798005783
submission_raw05_jepa_structrefine_82937d75.csv,250,True,0,0,0.0630839456,0.9798006624
submission_raw05_jepa_structrefine_dd98c58a.csv,250,True,0,0,0.0630830513,0.9798005783
submission_raw05_jepa_structrefine_5e75f84e.csv,250,True,0,0,0.0630840871,0.9798000271
submission_raw05_jepa_structrefine_1023cd8f.csv,250,True,0,0,0.0630840871,0.9798000271
submission_raw05_jepa_structrefine_a2892b08.csv,250,True,0,0,0.0630840871,0.9798000271
submission_raw05_jepa_structrefine_9669037f.csv,250,True,0,0,0.0630772355,0.9798015887
submission_raw05_jepa_structrefine_fc2f0b8e.csv,250,True,0,0,0.0630840871,0.9798000271
submission_raw05_jepa_structrefine_c13b7418.csv,250,True,0,0,0.0630840871,0.9798000271
submission_raw05_jepa_structrefine_1388b6d5.csv,250,True,0,0,0.0630840871,0.9798000271
submission_raw05_jepa_structrefine_0d4b9362.csv,250,True,0,0,0.0630772355,0.9798015887
submission_raw05_jepa_structrefine_cdc8a4b0.csv,250,True,0,0,0.0630840871,0.9798000271
submission_raw05_jepa_structrefine_6f7eaed6.csv,250,True,0,0,0.0630840871,0.9798000271
submission_raw05_jepa_structrefine_01f8ecbf.csv,250,True,0,0,0.0630772355,0.9798015887
submission_raw05_jepa_structrefine_4f6ce192.csv,250,True,0,0,0.0630772355,0.9798015887
submission_raw05_jepa_structrefine_10144124.csv,250,True,0,0,0.0630772355,0.9798015887
submission_raw05_jepa_structrefine_6a7fec4d.csv,250,True,0,0,0.0630772355,0.9798015887
submission_raw05_jepa_structrefine_5dc9b178.csv,250,True,0,0,0.0630772355,0.9798015887
submission_raw05_jepa_structrefine_e8aca262.csv,250,True,0,0,0.0630772355,0.9798015887
submission_raw05_jepa_structrefine_4734d036.csv,250,True,0,0,0.0630772355,0.9798015887
submission_raw05_jepa_structrefine_52ab3760.csv,250,True,0,0,0.0630772355,0.9798015887
```