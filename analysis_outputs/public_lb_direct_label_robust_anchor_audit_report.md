# Robust Direct-Label Actual-Anchor Audit

This applies the existing actual-anchor scenario/mask proxy to robust direct-label selected submissions.

## Best Robust Candidates

```
                             file         submit_role  actual_anchor_score_final  mean_actual_anchor  min_set_score  max_set_score source_mask_name  source_loocv_mae  source_l2o_mae target_mask  strength   cap  robust_delta_vs_a2c8  mean_abs_move_vs_a2c8
submission_directrob_29ffe34b.csv robust_first_submit                   0.577760            0.577679       0.577674       0.577820  frac0.40_rep009          0.000578        0.000532         all       0.5 0.055             -0.000548               0.002696
submission_directrob_93b1b685.csv   robust_structured                   0.577763            0.577671       0.577703       0.577811  frac0.40_rep052          0.000676        0.000607         all       0.5 0.055             -0.000551               0.002539
submission_directrob_13826633.csv robust_first_submit                   0.577763            0.577674       0.577687       0.577820  frac0.40_rep002          0.000645        0.000569         all       0.5 0.055             -0.000543               0.002670
submission_directrob_e1865441.csv   robust_structured                   0.577767            0.577679       0.577721       0.577807  frac0.40_rep052          0.000676        0.000607       no_q2       0.5 0.055             -0.000527               0.002291
submission_directrob_93de02d3.csv  robust_large_probe                   0.577773            0.577642       0.577515       0.577938  frac0.50_rep142          0.000751        0.000671         all       0.7 0.055             -0.000912               0.004557
submission_directrob_81846704.csv  robust_large_probe                   0.577777            0.577652       0.577544       0.577928  frac0.50_rep142          0.000751        0.000671       no_q2       0.7 0.055             -0.000875               0.004127
submission_directrob_2df97699.csv   robust_structured                   0.577781            0.577688       0.577734       0.577825  frac0.40_rep052          0.000676        0.000607 q3_s2_s3_s4       0.7 0.055             -0.000412               0.002115
submission_directrob_3610ed7a.csv  robust_large_probe                   0.577787            0.577694       0.577674       0.577869  frac0.40_rep040          0.000716        0.000622         all       0.7 0.055             -0.000629               0.003394
submission_directrob_1e28f54c.csv  robust_large_probe                   0.577789            0.577675       0.577635       0.577894  frac0.40_rep052          0.000676        0.000607         all       0.7 0.040             -0.000709               0.003528
submission_directrob_e047b80b.csv   robust_structured                   0.577789            0.577673       0.577632       0.577897  frac0.40_rep052          0.000676        0.000607         all       0.7 0.055             -0.000716               0.003543
submission_directrob_ec6961cb.csv  robust_large_probe                   0.577790            0.577690       0.577617       0.577901  frac0.40_rep009          0.000578        0.000532         all       0.7 0.040             -0.000682               0.003692
submission_directrob_f144c037.csv robust_first_submit                   0.577791            0.577685       0.577602       0.577911  frac0.40_rep009          0.000578        0.000532         all       0.7 0.055             -0.000708               0.003760
```

## Controls

```
                                                   file submit_role  actual_anchor_score_final  mean_actual_anchor  min_set_score  max_set_score source_mask_name  source_loocv_mae  source_l2o_mae target_mask  strength  cap  robust_delta_vs_a2c8  mean_abs_move_vs_a2c8
         submission_frontier_cvjepa_refine_a2c8d2c8.csv         NaN                   0.577827            0.577784       0.577721       0.577999              NaN               NaN             NaN         NaN       NaN  NaN                   NaN                    NaN
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv         NaN                   0.577906            0.577850       0.577730       0.578136              NaN               NaN             NaN         NaN       NaN  NaN                   NaN                    NaN
```

## Interpretation

- This proxy is calibrated only as a consistency filter over known public-anchor scenario/mask families.
- Robust candidates beating a2c8 on this proxy means they remain compatible with previous public anchor geometry, not that their public LB is proven.
