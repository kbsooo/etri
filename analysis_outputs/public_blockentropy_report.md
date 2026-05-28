# Public Block Entropy Projection
This variant solves the three observed public-score constraints with one latent probability per actual submission block and target, rather than one independent probability per row-target cell.

## Analogue Top Rows
```
    prior      target_mask  gamma  analogue_loss  prior_loss  analogue_delta  fold_max_residual  fold_converged_rate
  minimax              all   0.35       0.570921    0.554332        0.016588                0.0                  1.0
  minimax core_q1_q3_s3_s4   0.35       0.571709    0.554332        0.017377                0.0                  1.0
  minimax            no_q2   0.35       0.573386    0.554332        0.019054                0.0                  1.0
public2d0              all   0.35       0.573676    0.561702        0.011974                0.0                  1.0
    proj0              all   0.35       0.573923    0.562144        0.011780                0.0                  1.0
  minimax           q_only   0.35       0.574637    0.554332        0.020305                0.0                  1.0
public2d0            no_q2   0.35       0.576678    0.561702        0.014976                0.0                  1.0
    proj0            no_q2   0.35       0.576843    0.562144        0.014699                0.0                  1.0
   stage2              all   0.35       0.577868    0.567531        0.010337                0.0                  1.0
   stage2            no_q2   0.35       0.580975    0.567531        0.013444                0.0                  1.0
  minimax              all   0.50       0.583890    0.554332        0.029558                0.0                  1.0
  minimax core_q1_q3_s3_s4   0.50       0.584919    0.554332        0.030587                0.0                  1.0
public2d0              all   0.50       0.585575    0.561702        0.023873                0.0                  1.0
    proj0              all   0.50       0.585766    0.562144        0.023622                0.0                  1.0
public2d0 core_q1_q3_s3_s4   0.35       0.586188    0.561702        0.024487                0.0                  1.0
  minimax           s_only   0.35       0.586586    0.554332        0.032253                0.0                  1.0
    proj0 core_q1_q3_s3_s4   0.35       0.586603    0.562144        0.024459                0.0                  1.0
  minimax            no_q2   0.50       0.588723    0.554332        0.034390                0.0                  1.0
   stage2              all   0.50       0.589404    0.567531        0.021873                0.0                  1.0
  minimax           q_only   0.50       0.591721    0.554332        0.037388                0.0                  1.0
```

## Saved Candidates
```
                                                                       file     prior      target_mask  gamma  analogue_loss  analogue_delta  mean_abs_move  max_abs_move  max_abs_constraint_residual
               submission_public_blockentropy_minimax_all_g035_fd4765c6.csv   minimax              all   0.35       0.570921        0.016588       0.028945      0.256719                          0.0
  submission_public_blockentropy_minimax_core_q1_q3_s3_s4_g035_614d4a86.csv   minimax core_q1_q3_s3_s4   0.35       0.571709        0.017377       0.016991      0.150278                          0.0
             submission_public_blockentropy_minimax_no_q2_g035_ecc0175f.csv   minimax            no_q2   0.35       0.573386        0.019054       0.026599      0.258439                          0.0
             submission_public_blockentropy_public2d0_all_g035_c599e7df.csv public2d0              all   0.35       0.573676        0.011974       0.029400      0.254013                          0.0
                 submission_public_blockentropy_proj0_all_g035_3fba7c9d.csv     proj0              all   0.35       0.573923        0.011780       0.029389      0.253990                          0.0
           submission_public_blockentropy_public2d0_no_q2_g035_48794a6c.csv public2d0            no_q2   0.35       0.576678        0.014976       0.026943      0.255461                          0.0
               submission_public_blockentropy_proj0_no_q2_g035_6b6bf82f.csv     proj0            no_q2   0.35       0.576843        0.014699       0.026931      0.255430                          0.0
                submission_public_blockentropy_stage2_all_g035_41ab0015.csv    stage2              all   0.35       0.577868        0.010337       0.028896      0.258278                          0.0
              submission_public_blockentropy_stage2_no_q2_g035_9b62d58f.csv    stage2            no_q2   0.35       0.580975        0.013444       0.026520      0.259963                          0.0
  submission_public_blockentropy_minimax_core_q1_q3_s3_s4_g050_b9664752.csv   minimax core_q1_q3_s3_s4   0.50       0.584919        0.030587       0.024211      0.222113                          0.0
             submission_public_blockentropy_public2d0_all_g050_26cd2ad1.csv public2d0              all   0.50       0.585575        0.023873       0.041864      0.332925                          0.0
                 submission_public_blockentropy_proj0_all_g050_56c917d7.csv     proj0              all   0.50       0.585766        0.023622       0.041847      0.332916                          0.0
             submission_public_blockentropy_minimax_no_q2_g050_0528938a.csv   minimax            no_q2   0.50       0.588723        0.034390       0.037813      0.338405                          0.0
                submission_public_blockentropy_stage2_all_g050_bdde345c.csv    stage2              all   0.50       0.589404        0.021873       0.041126      0.338873                          0.0
           submission_public_blockentropy_public2d0_no_q2_g050_eb688870.csv public2d0            no_q2   0.50       0.591891        0.030189       0.038353      0.334492                          0.0
           submission_public_blockentropy_public2d0_no_q2_g065_cf9f1ff6.csv public2d0            no_q2   0.65       0.610994        0.049292       0.049608      0.392305                          0.0
submission_public_blockentropy_public2d0_core_q1_q3_s3_s4_g065_698abc38.csv public2d0 core_q1_q3_s3_s4   0.65       0.634821        0.073119       0.032171      0.292961                          0.0
```

## Integrity
```
                                                                       file  rows  key_match  duplicate_keys  null_predictions  min_prob  max_prob
               submission_public_blockentropy_minimax_all_g035_fd4765c6.csv   250       True               0                 0  0.064056  0.974823
  submission_public_blockentropy_minimax_core_q1_q3_s3_s4_g035_614d4a86.csv   250       True               0                 0  0.067162  0.977367
             submission_public_blockentropy_minimax_no_q2_g035_ecc0175f.csv   250       True               0                 0  0.064514  0.974954
             submission_public_blockentropy_public2d0_all_g035_c599e7df.csv   250       True               0                 0  0.053148  0.975450
                 submission_public_blockentropy_proj0_all_g035_3fba7c9d.csv   250       True               0                 0  0.053298  0.975441
           submission_public_blockentropy_public2d0_no_q2_g035_48794a6c.csv   250       True               0                 0  0.053813  0.975508
               submission_public_blockentropy_proj0_no_q2_g035_6b6bf82f.csv   250       True               0                 0  0.053970  0.975498
                submission_public_blockentropy_stage2_all_g035_41ab0015.csv   250       True               0                 0  0.060369  0.976154
              submission_public_blockentropy_stage2_no_q2_g035_9b62d58f.csv   250       True               0                 0  0.060982  0.976251
  submission_public_blockentropy_minimax_core_q1_q3_s3_s4_g050_b9664752.csv   250       True               0                 0  0.062194  0.977367
             submission_public_blockentropy_public2d0_all_g050_26cd2ad1.csv   250       True               0                 0  0.050272  0.977580
                 submission_public_blockentropy_proj0_all_g050_56c917d7.csv   250       True               0                 0  0.050426  0.977564
             submission_public_blockentropy_minimax_no_q2_g050_0528938a.csv   250       True               0                 0  0.058701  0.977314
                submission_public_blockentropy_stage2_all_g050_bdde345c.csv   250       True               0                 0  0.055775  0.978134
           submission_public_blockentropy_public2d0_no_q2_g050_eb688870.csv   250       True               0                 0  0.051175  0.977656
           submission_public_blockentropy_public2d0_no_q2_g065_cf9f1ff6.csv   250       True               0                 0  0.048661  0.979620
submission_public_blockentropy_public2d0_core_q1_q3_s3_s4_g065_698abc38.csv   250       True               0                 0  0.056134  0.978212
```