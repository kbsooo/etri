# S2 sparse gated meta diagnostics

Diagnostic candidate files were written; no automatic submission recommendation.

## Shift summary
                                                          file                                                                                      description  gate_rows  S2_changed_rows  S2_mean_abs_delta_vs_anchor  S2_p95_abs_delta_vs_anchor  S2_max_abs_delta_vs_anchor  S2_corr_vs_anchor  S2_candidate_mean_prob  S2_anchor_mean_prob  S2_mean_prob_shift
   submission_meta_anchor_s2sparse_gate_top50_blend50_prob.csv               Only rows in top 50% sparse-vs-anchor S2 disagreement move 50% toward sparse head.        125              125                     0.010960                    0.033572                    0.037533           0.996432                0.595541             0.596454           -0.000913
   submission_meta_anchor_s2sparse_gate_top30_blend50_prob.csv               Only rows in top 30% sparse-vs-anchor S2 disagreement move 50% toward sparse head.         75               75                     0.007841                    0.033572                    0.037533           0.997103                0.594575             0.596454           -0.001879
      submission_meta_anchor_s2sparse_agreeDL_blend30_prob.csv Rows where sparse S2 and previous S2-DL residual move in same direction; move 30% toward sparse.        173              173                     0.006167                    0.020143                    0.022520           0.998993                0.593541             0.596454           -0.002913
      submission_meta_anchor_s2sparse_agreeDL_blend50_prob.csv Rows where sparse S2 and previous S2-DL residual move in same direction; move 50% toward sparse.        173              173                     0.010278                    0.033572                    0.037533           0.997271                0.591599             0.596454           -0.004855
submission_meta_anchor_s2sparse_agreeDL_top50_blend50_prob.csv     Only same-direction sparse/DL rows among top 50% sparse disagreement move 50% toward sparse.         94               94                     0.008574                    0.033572                    0.037533           0.997395                0.593155             0.596454           -0.003299

## Interpretation
Gated candidates reduce changed-row count or require agreement between sparse S2 and previous S2-DL residual. If public probing is scarce, these are safer than full replacement/residual variants, but the plain 30% all-row interpolation remains the cleanest single diagnostic.