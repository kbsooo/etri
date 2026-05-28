# Graph Field JEPA Inpainting

Treat each train/submission row as a node in a JEPA-friendly joint embedding space, clamp known train labels, keep hidden rows on the stage2 prior, and inpaint a smooth 7-target logit field over the graph.

- repeats: 3
- iterations: 55
- base full OOF loss: 0.567531
- best emitted OOF loss: 0.566914

## Top candidates

```
                                                              candidate                    config group  scale  oof_loss  oof_delta_vs_stage2  bad_axis_projection_ratio  good_axis_projection_ratio
 submission_graph_field_jepa_00_gk6_t1_sw0p25_pw0p75_lw20_all_sc0p5.csv gk6_t1_sw0p25_pw0p75_lw20   all   0.50  0.566914            -0.000617                   0.075426                   -0.069182
  submission_graph_field_jepa_01_gk6_t1_sw0p1_pw0p25_lw20_all_sc0p5.csv  gk6_t1_sw0p1_pw0p25_lw20   all   0.50  0.566917            -0.000614                   0.088497                   -0.077442
   submission_graph_field_jepa_02_gk6_t1_sw0p1_pw0p25_lw8_all_sc0p5.csv   gk6_t1_sw0p1_pw0p25_lw8   all   0.50  0.566925            -0.000606                   0.087022                   -0.078695
  submission_graph_field_jepa_03_gk6_t1_sw0p25_pw0p75_lw8_all_sc0p5.csv  gk6_t1_sw0p25_pw0p75_lw8   all   0.50  0.566938            -0.000593                   0.072075                   -0.071986
submission_graph_field_jepa_04_gk6_t1_sw0p25_pw0p75_lw20_all_sc0p75.csv gk6_t1_sw0p25_pw0p75_lw20   all   0.75  0.566944            -0.000587                   0.113139                   -0.103773
 submission_graph_field_jepa_05_gk6_t1_sw0p1_pw0p75_lw20_all_sc0p75.csv  gk6_t1_sw0p1_pw0p75_lw20   all   0.75  0.566949            -0.000582                   0.052535                   -0.048911
 submission_graph_field_jepa_06_gk6_t1_sw0p25_pw0p75_lw8_all_sc0p75.csv  gk6_t1_sw0p25_pw0p75_lw8   all   0.75  0.566950            -0.000581                   0.108112                   -0.107979
  submission_graph_field_jepa_07_gk6_t1_sw0p1_pw0p75_lw8_all_sc0p75.csv   gk6_t1_sw0p1_pw0p75_lw8   all   0.75  0.566969            -0.000562                   0.050463                   -0.050574
 submission_graph_field_jepa_08_gk6_t1_sw0p1_pw0p25_lw20_all_sc0p35.csv  gk6_t1_sw0p1_pw0p25_lw20   all   0.35  0.566971            -0.000560                   0.061948                   -0.054210
  submission_graph_field_jepa_09_gk6_t1_sw0p1_pw0p25_lw8_all_sc0p35.csv   gk6_t1_sw0p1_pw0p25_lw8   all   0.35  0.566981            -0.000550                   0.060916                   -0.055087
```

## Interpretation

This is a stronger JEPA usage than direct residual blending: the latent space defines which rows should agree, while the task labels are only anchors for visible context. If it helps, the gain should come from hidden-block consistency rather than from a single residual feature.
