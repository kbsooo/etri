# Raw05 Cross-View JEPA Surprise Micro Graft

Starts from the observed raw05 public-best submission and injects capped `cvjepa - stage2` logit residuals.
This tests whether the strong cross-view JEPA OOF signal can survive under raw05-axis and bad-axis constraints.

## Counts

- generated candidates: 80897
- actual-anchor rescored candidates: 698
- saved candidates: 81

## Top Saved By Graft Score

```csv
file,bucket,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,mean_abs_move_vs_raw05,graft_score,label
submission_raw05_cvjepa_surprise_graft_3d82599f.csv,strict_raw,0.5779227714,0.577515002,-8.913e-07,0.002435627,0.0004637173,0.5781345137,full_nonq2_w020|q1_s2|ones|anti_raw|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_0b1455a5.csv,posterior_probe,0.5779245366,0.5775125429,-8.859e-07,0.0024064308,0.0004938257,0.5781345238,full_nonq2_w030|q1_s2|ones|anti_raw|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_43ff27ed.csv,posterior_probe,0.5779256591,0.5775122915,-8.988e-07,0.0024400802,0.000511749,0.5781361263,full_nonq2|q1_s2|ones|anti_raw|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_f5e33602.csv,strict_raw,0.5779153023,0.5775259996,-5.507e-07,0.0028638909,0.000259903,0.5781402521,full_nonq2|s2_only|ones|anti_raw|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_c6ebadda.csv,strict_raw,0.5779145408,0.5775268977,-5.364e-07,0.0028866207,0.0002500047,0.5781403488,full_nonq2_w030|s2_only|ones|anti_raw|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_9cbdda72.csv,strict_raw,0.5779150138,0.5775237956,-1.0918e-06,0.0027270117,0.000350108,0.5781405308,full_nonq2_w020|q3_s2_s4|ones|anti_raw_q65|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_5529b9fd.csv,strict_raw,0.5779131783,0.5775279136,-5.475e-07,0.0029633246,0.0002326438,0.578140875,full_nonq2_w020|s2_only|ones|anti_raw|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_8b2f4c54.csv,strict_raw,0.5779151816,0.5775248739,-1.0864e-06,0.0027674145,0.000348235,0.5781417199,full_nonq2|q3_s2_s4|ones|anti_raw_q65|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_393db5df.csv,strict_raw,0.5779135654,0.5775263112,-7.159e-07,0.0030630012,0.0002274889,0.578142255,full_nonq2_w020|s2_only|ones|anti_raw|dir-1|w0.78|c0.024
submission_raw05_cvjepa_surprise_graft_b4fc32c7.csv,strict_raw,0.5779142651,0.5775255963,-7.329e-07,0.0030761152,0.0002359606,0.5781428333,full_nonq2_w030|s2_only|ones|anti_raw|dir-1|w0.78|c0.024
submission_raw05_cvjepa_surprise_graft_5b3bc5a1.csv,strict_raw,0.5779122595,0.5775289667,-9.871e-07,0.0031040282,0.0002616727,0.5781430153,full_nonq2_w020|q3_s2_s4|surprise_top50|anti_raw_q65|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_fb7e2fe1.csv,strict_raw,0.5779146331,0.5775250324,-7.428e-07,0.0031379269,0.0002424713,0.578144032,full_nonq2|s2_only|ones|anti_raw|dir-1|w0.78|c0.024
submission_raw05_cvjepa_surprise_graft_ae21539f.csv,strict_raw,0.5779123496,0.5775297632,-9.867e-07,0.0031480443,0.0002592277,0.578144296,full_nonq2|q3_s2_s4|surprise_top50|anti_raw_q65|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_99343e48.csv,posterior_probe,0.5779151431,0.5775145594,-9.987e-07,0.0035526183,0.0003961098,0.5781467699,full_nonq2_w020|s_targets|ones|anti_raw_q65|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_c3d9cd3d.csv,actual_probe,0.5779067907,0.5775284552,-1.397e-07,0.0036690745,9.69388e-05,0.5781474616,full_nonq2_w020|s2_only|surprise_top50|anti_raw_q65|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_86cb6f05.csv,rank_fallback,0.5779148593,0.5775225209,1.71e-08,0.003391012,0.0002593132,0.578147558,full_nonq2_w020|q3_s2_s4|surprise_top70|anti_raw_q65|dir-1|w0.78|c0.040
submission_raw05_cvjepa_surprise_graft_0dd10fa8.csv,actual_probe,0.5779084418,0.5775287974,-1.132e-07,0.0035887615,0.0001138379,0.5781478382,full_nonq2_w020|s2_only|ones|anti_raw_q65|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_f4eac11a.csv,actual_probe,0.5779068219,0.5775282703,-1.505e-07,0.0037230079,9.21939e-05,0.5781483712,full_nonq2|s2_only|surprise_top50|anti_raw_q65|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_f052d4b5.csv,strict_raw,0.5779224005,0.5775131622,-1.2598e-06,0.0026471476,0.0004490593,0.5781487201,full_nonq2_w020|q1_s2|ones|anti_raw|dir-1|w0.78|c0.024
submission_raw05_cvjepa_surprise_graft_916734bd.csv,actual_probe,0.5779083915,0.5775288943,-1.189e-07,0.0036390817,0.0001096649,0.5781487421,full_nonq2|s2_only|ones|anti_raw_q65|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_10f52c0d.csv,posterior_probe,0.5779151446,0.5775153789,-1.0102e-06,0.0036139863,0.0003933373,0.5781487439,full_nonq2_w030|s_targets|ones|anti_raw_q65|dir-1|w0.52|c0.040
submission_raw05_cvjepa_surprise_graft_88f9bb0a.csv,actual_probe,0.577906577,0.5775281496,-2.165e-07,0.0037864543,8.72414e-05,0.578149208,full_nonq2_w020|s2_only|surprise_top50|anti_raw_q65|dir-1|w0.78|c0.024
submission_raw05_cvjepa_surprise_graft_a9f915d2.csv,actual_probe,0.5779080425,0.5775284418,-2.085e-07,0.0037140822,0.0001024481,0.5781495169,full_nonq2_w020|s2_only|ones|anti_raw_q65|dir-1|w0.78|c0.024
submission_raw05_cvjepa_surprise_graft_b0bbfc8e.csv,actual_probe,0.577906603,0.5775279877,-2.218e-07,0.0038350155,8.29706e-05,0.5781500271,full_nonq2|s2_only|surprise_top50|anti_raw_q65|dir-1|w0.78|c0.024
submission_raw05_cvjepa_surprise_graft_12e31828.csv,actual_probe,0.5779080019,0.5775285329,-2.097e-07,0.0037593945,9.86915e-05,0.5781503374,full_nonq2|s2_only|ones|anti_raw_q65|dir-1|w0.78|c0.024
submission_raw05_cvjepa_surprise_graft_c0590734.csv,strict_raw,0.5779233187,0.5775134375,-1.2762e-06,0.0027128775,0.0004639188,0.5781516994,full_nonq2_w030|q1_s2|ones|anti_raw|dir-1|w0.78|c0.024
submission_raw05_cvjepa_surprise_graft_e7e973d3.csv,actual_probe,0.5779093055,0.5775309858,-6.097e-07,0.0037362937,0.0001593143,0.5781524517,core_q1_q3_s2_s4|s_targets|surprise_top50|anti_raw_q65|dir-1|w0.78|c0.024
submission_raw05_cvjepa_surprise_graft_9e024d5b.csv,strict_raw,0.5779138203,0.577523719,-1.3104e-06,0.0029381567,0.0003150897,0.5781529339,full_nonq2_w020|q3_s2_s4|ones|anti_raw_q65|dir-1|w0.78|c0.024
submission_raw05_cvjepa_surprise_graft_00bd151f.csv,actual_probe,0.5779074877,0.5775276002,-2.56e-07,0.0039622936,7.88222e-05,0.5781530091,full_nonq2_w020|s2_only|all64|anti_raw_q65|dir-1|w0.78|c0.040
submission_raw05_cvjepa_surprise_graft_619416a4.csv,actual_probe,0.5779087472,0.5775265823,-6.333e-07,0.0039415211,0.0001483706,0.5781533857,core_q1_q3_s2_s4|s_targets|raw64|anti_raw_q65|dir-1|w0.78|c0.040
submission_raw05_cvjepa_surprise_graft_6ba29f43.csv,actual_probe,0.5779073569,0.5775284326,-2.375e-07,0.0039727479,7.98206e-05,0.5781534827,full_nonq2_w020|s2_only|raw64|anti_raw_q65|dir-1|w0.78|c0.040
submission_raw05_cvjepa_surprise_graft_2ec25162.csv,actual_probe,0.5779091872,0.5775291212,-2.798e-07,0.0038593892,0.0001414539,0.5781536169,full_nonq2_w020|s2_only|surprise_top50|anti_raw|dir-1|w0.52|c0.040
```

## Local LB Proxy

```csv
file,available_raw05_relative_lb_proxy_mean,available_raw05_relative_delta_vs_raw05_public,available_raw05_relative_model_spread,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,mean_abs_move_vs_raw05
submission_raw05_cvjepa_surprise_graft_c3d9cd3d.csv,0.5775252844,-1.0228e-06,2.4367e-06,0.5779067907,0.5775284552,-1.397e-07,0.0036690745,9.69388e-05
submission_raw05_cvjepa_surprise_graft_f4eac11a.csv,0.577525334,-9.732e-07,2.3506e-06,0.5779068219,0.5775282703,-1.505e-07,0.0037230079,9.21939e-05
submission_raw05_cvjepa_surprise_graft_88f9bb0a.csv,0.5775253673,-9.399e-07,2.1626e-06,0.577906577,0.5775281496,-2.165e-07,0.0037864543,8.72414e-05
submission_raw05_cvjepa_surprise_graft_b0bbfc8e.csv,0.5775254127,-8.945e-07,2.0878e-06,0.577906603,0.5775279877,-2.218e-07,0.0038350155,8.29706e-05
submission_raw05_cvjepa_surprise_graft_0dd10fa8.csv,0.5775255094,-7.978e-07,2.7069e-06,0.5779084418,0.5775287974,-1.132e-07,0.0035887615,0.0001138379
submission_raw05_cvjepa_surprise_graft_916734bd.csv,0.5775255516,-7.556e-07,2.6141e-06,0.5779083915,0.5775288943,-1.189e-07,0.0036390817,0.0001096649
submission_raw05_cvjepa_surprise_graft_a9f915d2.csv,0.5775255658,-7.414e-07,2.3987e-06,0.5779080425,0.5775284418,-2.085e-07,0.0037140822,0.0001024481
submission_raw05_cvjepa_surprise_graft_12e31828.csv,0.5775256045,-7.027e-07,2.3163e-06,0.5779080019,0.5775285329,-2.097e-07,0.0037593945,9.86915e-05
submission_raw05_cvjepa_surprise_graft_6ba29f43.csv,0.5775256865,-6.207e-07,1.7082e-06,0.5779073569,0.5775284326,-2.375e-07,0.0039727479,7.98206e-05
submission_raw05_cvjepa_surprise_graft_80768e62.csv,0.5775257082,-5.99e-07,1.6707e-06,0.5779073551,0.5775286433,-2.31e-07,0.0039970291,7.76064e-05
submission_raw05_cvjepa_surprise_graft_00bd151f.csv,0.5775257147,-5.925e-07,1.8813e-06,0.5779074877,0.5775276002,-2.56e-07,0.0039622936,7.88222e-05
submission_raw05_cvjepa_surprise_graft_4f6bd5bf.csv,0.5775257409,-5.663e-07,1.8462e-06,0.5779074792,0.5775277876,-2.545e-07,0.0039916309,7.60198e-05
submission_raw05_cvjepa_surprise_graft_5529b9fd.csv,0.5775264315,1.243e-07,4.5454e-06,0.5779131783,0.5775279136,-5.475e-07,0.0029633246,0.0002326438
submission_raw05_cvjepa_surprise_graft_e7e973d3.csv,0.5775265054,1.982e-07,2.1515e-06,0.5779093055,0.5775309858,-6.097e-07,0.0037362937,0.0001593143
submission_raw05_cvjepa_surprise_graft_10c411e1.csv,0.5775265134,2.062e-07,1.6999e-06,0.5779085198,0.5775270248,-1.1969e-06,0.003929144,0.0001373509
submission_raw05_cvjepa_surprise_graft_fda4cee4.csv,0.5775265501,2.429e-07,1.6523e-06,0.5779086188,0.5775274493,-1.1903e-06,0.0039523231,0.0001360635
submission_raw05_cvjepa_surprise_graft_13a17ee7.csv,0.5775265678,2.606e-07,1.9925e-06,0.5779089904,0.5775272497,-1.2454e-06,0.0037986887,0.0001569775
submission_raw05_cvjepa_surprise_graft_2ec25162.csv,0.5775265705,2.633e-07,2.1865e-06,0.5779091872,0.5775291212,-2.798e-07,0.0038593892,0.0001414539
submission_raw05_cvjepa_surprise_graft_323e8b88.csv,0.5775265793,2.721e-07,2.0095e-06,0.577909147,0.577528088,-4.05e-07,0.0039314531,0.0001326207
submission_raw05_cvjepa_surprise_graft_393db5df.csv,0.5775265847,2.775e-07,4.3931e-06,0.5779135654,0.5775263112,-7.159e-07,0.0030630012,0.0002274889
submission_raw05_cvjepa_surprise_graft_ba58605c.csv,0.577526595,2.878e-07,1.9709e-06,0.5779091169,0.5775280394,-3.973e-07,0.0039466996,0.0001317418
submission_raw05_cvjepa_surprise_graft_e307fc4f.csv,0.5775266025,2.953e-07,1.9995e-06,0.5779091748,0.5775281521,-4.104e-07,0.0039358883,0.0001334293
submission_raw05_cvjepa_surprise_graft_4f89f1f1.csv,0.5775266096,3.024e-07,1.9372e-06,0.5779091066,0.5775277337,-1.2391e-06,0.0038251664,0.0001555069
submission_raw05_cvjepa_surprise_graft_ae5e7cb0.csv,0.577526644,3.368e-07,1.632e-06,0.5779090135,0.5775272966,-8.298e-07,0.0039428776,0.000141966
submission_raw05_cvjepa_surprise_graft_c6ebadda.csv,0.5775266514,3.442e-07,4.9493e-06,0.5779145408,0.5775268977,-5.364e-07,0.0028866207,0.0002500047
submission_raw05_cvjepa_surprise_graft_619416a4.csv,0.5775266555,3.483e-07,1.7008e-06,0.5779087472,0.5775265823,-6.333e-07,0.0039415211,0.0001483706
submission_raw05_cvjepa_surprise_graft_d865222a.csv,0.5775267212,4.14e-07,1.5662e-06,0.577908942,0.5775243559,-1.3507e-06,0.0039468997,0.0001481012
submission_raw05_cvjepa_surprise_graft_e06a4da9.csv,0.5775267475,4.403e-07,1.5588e-06,0.5779089932,0.5775248168,-1.3436e-06,0.0039640706,0.0001473038
submission_raw05_cvjepa_surprise_graft_7da3c5e5.csv,0.5775267655,4.583e-07,1.8062e-06,0.5779092734,0.5775255132,-1.2156e-06,0.0039072869,0.0001519308
submission_raw05_cvjepa_surprise_graft_a99b6518.csv,0.5775267684,4.612e-07,1.5857e-06,0.577908077,0.5775238253,-1.2251e-06,0.0039813965,0.0001563719
submission_raw05_cvjepa_surprise_graft_5ba5a755.csv,0.5775267908,4.836e-07,1.6457e-06,0.577908128,0.5775244466,-1.2187e-06,0.0039927208,0.0001560267
submission_raw05_cvjepa_surprise_graft_b4fc32c7.csv,0.5775268012,4.94e-07,4.4807e-06,0.5779142651,0.5775255963,-7.329e-07,0.0030761152,0.0002359606
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_cvjepa_surprise_graft_3d82599f.csv,250,True,0,0,0.0607411901,0.9800550384
submission_raw05_cvjepa_surprise_graft_0b1455a5.csv,250,True,0,0,0.0607411901,0.9800550384
submission_raw05_cvjepa_surprise_graft_43ff27ed.csv,250,True,0,0,0.0607411901,0.9800550384
submission_raw05_cvjepa_surprise_graft_f5e33602.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_c6ebadda.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_9cbdda72.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_5529b9fd.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_8b2f4c54.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_393db5df.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_b4fc32c7.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_5b3bc5a1.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_fb7e2fe1.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_ae21539f.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_99343e48.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_c3d9cd3d.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_86cb6f05.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_0dd10fa8.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_f4eac11a.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_f052d4b5.csv,250,True,0,0,0.0608599661,0.9800550384
submission_raw05_cvjepa_surprise_graft_916734bd.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_10f52c0d.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_88f9bb0a.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_a9f915d2.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_b0bbfc8e.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_12e31828.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_c0590734.csv,250,True,0,0,0.0608599661,0.9800550384
submission_raw05_cvjepa_surprise_graft_e7e973d3.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_9e024d5b.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_00bd151f.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_619416a4.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_6ba29f43.csv,250,True,0,0,0.0619387639,0.9800550384
submission_raw05_cvjepa_surprise_graft_2ec25162.csv,250,True,0,0,0.0619387639,0.9800550384
```
