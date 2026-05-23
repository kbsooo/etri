# Improved moonshot graph candidates

These refine raw-all-noQ3 by removing graph from validation-negative targets Q1/S4 and/or sharpening validation-positive S2/S3.

## Movement summary
                                              file  mean_abs_vs_anchor  max_target_mean_abs_vs_anchor  mean_abs_vs_raw_all_noq3  max_target_mean_abs_vs_raw_all_noq3  mean_abs_vs_w03  max_target_mean_abs_vs_w03
   submission_moonshot_graph_raw_all_noq3_prob.csv            0.093012                       0.134712                  0.000000                             0.000000         0.088381                    0.129879
submission_moonshot_graph_raw_noq3_q2half_prob.csv            0.086735                       0.134712                  0.006277                             0.043941         0.082104                    0.129879
  submission_moonshot_graph_raw_sharpened_prob.csv            0.083532                       0.131414                  0.027471                             0.046780         0.079233                    0.120280
 submission_moonshot_optimized_keep_s4raw_prob.csv            0.076155                       0.131804                  0.024087                             0.108170         0.070329                    0.121374
 submission_moonshot_raw_all_antifix_q1s4_prob.csv            0.074422                       0.125172                  0.025030                             0.060687         0.069386                    0.119749
submission_moonshot_validated_block_sharp_prob.csv            0.061427                       0.133033                  0.058505                             0.121374         0.055088                    0.125944
 submission_moonshot_optimized_targetwise_prob.csv            0.059369                       0.125172                  0.041426                             0.121374         0.052990                    0.119749
      submission_moonshot_validated_block_prob.csv            0.055158                       0.125172                  0.044117                             0.131804         0.057201                    0.119749

## Recommendation logic
- If pure 0.5-or-bust: raw_all_noq3 or optimized_keep_s4raw.
- If using masked validation literally: optimized_targetwise.
- If risk-adjusted: validated_block_sharp or validated_block.