# Public Entropy Projection Report
Public LB scores are treated as aggregate linear constraints on the hidden binary labels.

## Constraint Scores
- `submission_hybrid_0p578_logit_after_subject_final9_strict.csv`: public `0.5784273528`, train OOF analogue `0.578303670`
- `submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv`: public `0.5779449757`, train OOF analogue `0.567530925`
- `submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv`: public `0.5783033652`, train OOF analogue `0.561903817`

## Best Generated Rows
```
                                            file     prior  gamma  oof_loss  oof_delta_vs_stage2  public_self_expected_loss  public_crossentropy_gap  submission_abs_delta_mean_vs_prior  submission_min  submission_max  public_fit_max_abs_residual
submission_public_entropyproj_public2d0_g100.csv public2d0   1.00  0.553679            -0.013852                   0.575734                 0.000000                            0.017658        0.081256        0.976610                          0.0
    submission_public_entropyproj_proj0_g100.csv     proj0   1.00  0.553904            -0.013627                   0.575799                 0.000000                            0.018062        0.081792        0.976619                          0.0
submission_public_entropyproj_public2d0_g075.csv public2d0   0.75  0.554156            -0.013375                   0.575826                 0.000092                            0.013218        0.074965        0.977021                          0.0
    submission_public_entropyproj_proj0_g075.csv     proj0   0.75  0.554394            -0.013137                   0.575895                 0.000096                            0.013520        0.075364        0.977031                          0.0
submission_public_entropyproj_public2d0_g050.csv public2d0   0.50  0.555625            -0.011906                   0.576100                 0.000366                            0.008793        0.069124        0.977425                          0.0
    submission_public_entropyproj_proj0_g050.csv     proj0   0.50  0.555904            -0.011627                   0.576183                 0.000385                            0.008993        0.069404        0.977435                          0.0
   submission_public_entropyproj_stage2_g100.csv    stage2   1.00  0.557993            -0.009538                   0.576576                 0.000000                            0.017025        0.089365        0.977934                          0.0
   submission_public_entropyproj_anchor_g100.csv    anchor   1.00  0.557993            -0.009538                   0.576576                 0.000000                            0.019968        0.089365        0.977934                          0.0
submission_public_entropyproj_public2d0_g025.csv public2d0   0.25  0.558133            -0.009398                   0.576556                 0.000822                            0.004386        0.063708        0.977822                          0.0
    submission_public_entropyproj_proj0_g025.csv     proj0   0.25  0.558480            -0.009051                   0.576662                 0.000864                            0.004486        0.063882        0.977832                          0.0
   submission_public_entropyproj_stage2_g075.csv    stage2   0.75  0.558562            -0.008969                   0.576662                 0.000086                            0.012745        0.082886        0.978258                          0.0
   submission_public_entropyproj_anchor_g075.csv    anchor   0.75  0.559201            -0.008329                   0.576692                 0.000116                            0.014969        0.096124        0.977702                          0.0
```

## Geometry Analogue
```
    prior  folds  mean_base_loss  mean_projected_loss  mean_delta  win_rate  max_constraint_residual
   anchor      8        0.566641             0.544364   -0.022277       1.0                      0.0
    proj0      8        0.551602             0.540499   -0.011103       1.0                      0.0
public2d0      8        0.551285             0.540412   -0.010874       1.0                      0.0
   stage2      8        0.557348             0.544364   -0.012984       1.0                      0.0
```
