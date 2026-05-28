# Direction Probe Selector Reconciliation

Question: do the newer score-oriented sparse/target-ablation/direction-ensemble/minimax probes survive the same pairwise-vs-old selector stress used to reject S4/Q3 label-flow sensors?

## Summary

- probes scored: `22`.
- pair p90 negative: `0`.
- pair majority: `0`.
- old majority: `0`.
- two-selector majority: `0`.
- submit-shape candidates: `0`.

## By Family

| probe_family | n | pair_p90_negative | pair_majority | old_majority | two_selector_majority | submit_shape | best_file | best_pair_p90 | best_pair_rate | best_old_p90 | best_old_rate | best_bad_axis | best_move | best_q3s4_share | best_stage_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inverse7blend | 1 | 0 | 0 | 0 | 0 | 0 | analysis_outputs/submission_inverse7blend_1040423d.csv | 0.000122038 | 0.0459459 | 0.000617292 | 0.003861 | 0.0524804 | 0.0124131 | 0.378465 | 0.580783 |
| targetabl | 2 | 0 | 0 | 0 | 0 | 0 | analysis_outputs/submission_targetabl_1049b8e7.csv | 0.000293056 | 0.589189 | 0.000801965 | 0.011583 | 0.128569 | 0.0254551 | 0.449874 | 0.718929 |
| inv7gate | 2 | 0 | 0 | 0 | 0 | 0 | analysis_outputs/submission_inv7gate_0a9c0c66.csv | 0.000377346 | 0.167568 | 0.000796012 | 0.030888 | 0.101393 | 0.0189631 | 0.241058 | 0.567494 |
| direns | 5 | 0 | 0 | 0 | 0 | 0 | analysis_outputs/submission_direns_1e0f159d.csv | 0.000834814 | 0 | 0.000969928 | 0.00772201 | 0.195767 | 0.0437182 | 0.277017 | 0.597128 |
| blockorth | 2 | 0 | 0 | 0 | 0 | 0 | analysis_outputs/submission_blockorth_3a28f87f.csv | 0.00085209 | 0 | 0.00103685 | 0.00772201 | 0.197546 | 0.0457511 | 0.273067 | 0.571583 |
| mixmin | 7 | 0 | 0 | 0 | 0 | 0 | analysis_outputs/submission_mixmin_0c916bb4.csv | 0.0008792 | 0 | 0.00104193 | 0.00772201 | 0.213626 | 0.0456142 | 0.268162 | 0.587465 |
| sparseladder | 3 | 0 | 0 | 0 | 0 | 0 | analysis_outputs/submission_sparseladder_f1ee16b0.csv | 0.000893371 | 0.0027027 | 0.000979619 | 0.011583 | 0.208852 | 0.045408 | 0.290993 | 0.638428 |

## Top Reconciliation Rows

| source_path | probe_family | probe_role | pair_delta_vs_a2c8_p90 | pair_beats_a2c8_rate | selector_p90_delta_vs_a2c8_public | beats_a2c8_scenario_rate | bad_axis_abs_load | mean_abs_move_vs_a2c8 | q3s4_move_share | stage_move_share | actual_anchor_score_final | honest_cv_delta_mean | combo_weighted_delta_vs_b01_ladder | combo_p90_delta_vs_b01_ladder | old_majority | pair_majority | two_selector_majority | submit_shape |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_outputs/submission_inverse7blend_1040423d.csv | inverse7blend | best | 0.000122038 | 0.0459459 | 0.000617292 | 0.003861 | 0.0524804 | 0.0124131 | 0.378465 | 0.580783 |  |  |  |  | False | False | False | False |
| analysis_outputs/submission_targetabl_1049b8e7.csv | targetabl | q3_s234 | 0.000293056 | 0.589189 | 0.000801965 | 0.011583 | 0.128569 | 0.0254551 | 0.449874 | 0.718929 | 0.577738 | -0.000580118 |  |  | False | False | False | False |
| analysis_outputs/submission_inv7gate_0a9c0c66.csv | inv7gate | sibling | 0.000377346 | 0.167568 | 0.000796012 | 0.030888 | 0.101393 | 0.0189631 | 0.241058 | 0.567494 | 0.577886 | -0.000350653 |  |  | False | False | False | False |
| analysis_outputs/submission_inv7gate_e35a7114.csv | inv7gate | prefix_best | 0.000392576 | 0.175676 | 0.000754034 | 0.030888 | 0.0960013 | 0.0187054 | 0.267272 | 0.62549 | 0.577882 | -0.000335753 |  |  | False | False | False | False |
| analysis_outputs/submission_targetabl_b19056bb.csv | targetabl | q3_stage | 0.000678061 | 0.0135135 | 0.000759908 | 0.00772201 | 0.125471 | 0.0248301 | 0.354768 | 0.778349 | 0.577727 | -0.000551818 |  |  | False | False | False | False |
| analysis_outputs/submission_direns_1e0f159d.csv | direns | sibling | 0.000834814 | 0 | 0.000969928 | 0.00772201 | 0.195767 | 0.0437182 | 0.277017 | 0.597128 | 0.577729 | -0.000898492 |  |  | False | False | False | False |
| analysis_outputs/submission_direns_c0fdb76b.csv | direns | secondary | 0.000847297 | 0 | 0.000974851 | 0.00772201 | 0.200574 | 0.0440801 | 0.275809 | 0.601579 | 0.577731 | -0.00091133 |  |  | False | False | False | False |
| analysis_outputs/submission_direns_b0962ff8.csv | direns | orth_diag | 0.000864995 | 0 | 0.00096133 | 0.011583 | 0.162351 | 0.0436733 | 0.286148 | 0.600071 | 0.57776 | -0.000826163 |  |  | False | False | False | False |
| analysis_outputs/submission_blockorth_3a28f87f.csv | blockorth | best | 0.00085209 | 0 | 0.00103685 | 0.00772201 | 0.197546 | 0.0457511 | 0.273067 | 0.571583 | 0.577744 | -0.000891591 |  |  | False | False | False | False |
| analysis_outputs/submission_blockorth_0352b65f.csv | blockorth | prefix | 0.00085431 | 0 | 0.00103082 | 0.00772201 | 0.19618 | 0.0456052 | 0.273896 | 0.579993 | 0.577744 | -0.000883603 |  |  | False | False | False | False |
| analysis_outputs/submission_direns_c4af1fd8.csv | direns | combo_best | 0.000865534 | 0 | 0.00100021 | 0.00772201 | 0.206263 | 0.0448824 | 0.27291 | 0.596084 | 0.577733 | -0.000929529 |  |  | False | False | False | False |
| analysis_outputs/submission_direns_2a96ae73.csv | direns | anchor_best | 0.000885859 | 0 | 0.000996515 | 0.00772201 | 0.195543 | 0.0430758 | 0.288048 | 0.619468 | 0.577729 | -0.000876501 |  |  | False | False | False | False |
| analysis_outputs/submission_mixmin_0c916bb4.csv | mixmin | rank1 | 0.0008792 | 0 | 0.00104193 | 0.00772201 | 0.213626 | 0.0456142 | 0.268162 | 0.587465 | 0.577734 | -0.000951963 | -1.28772e-05 | -8.45163e-06 | False | False | False | False |
| analysis_outputs/submission_sparseladder_f1ee16b0.csv | sparseladder | no_q2 | 0.000893371 | 0.0027027 | 0.000979619 | 0.011583 | 0.208852 | 0.045408 | 0.290993 | 0.638428 |  |  |  |  | False | False | False | False |
| analysis_outputs/submission_mixmin_5a4c25e0.csv | mixmin | rank2 | 0.000891627 | 0 | 0.00101577 | 0.00772201 | 0.214892 | 0.0459893 | 0.271898 | 0.596121 | 0.577737 | -0.000961288 | -1.23737e-05 | -2.87124e-06 | False | False | False | False |
| analysis_outputs/submission_mixmin_ef4b1c19.csv | mixmin | frontier2 | 0.000890931 | 0 | 0.00103704 | 0.00772201 | 0.215669 | 0.0461563 | 0.269857 | 0.591227 | 0.577737 | -0.000960573 | -1.17175e-05 | -2.48101e-06 | False | False | False | False |
| analysis_outputs/submission_mixmin_f6c04249.csv | mixmin | frontier1 | 0.000891549 | 0 | 0.00104419 | 0.00772201 | 0.216024 | 0.0462203 | 0.269286 | 0.589897 | 0.577737 | -0.000960783 | -1.1453e-05 | -1.97332e-06 | False | False | False | False |
| analysis_outputs/submission_mixmin_7f9cb635.csv | mixmin | frontier3 | 0.000893886 | 0 | 0.00104538 | 0.00772201 | 0.216805 | 0.0463203 | 0.269208 | 0.589926 | 0.577738 | -0.000963607 | -1.15077e-05 | -5.00731e-07 | False | False | False | False |
| analysis_outputs/submission_mixmin_615da9a7.csv | mixmin | frontier4 | 0.000892644 | 0 | 0.00105228 | 0.00772201 | 0.217664 | 0.046301 | 0.267153 | 0.585633 | 0.577738 | -0.000964008 | -1.16608e-05 | -4.92637e-07 | False | False | False | False |
| analysis_outputs/submission_sparseladder_b01acaa1.csv | sparseladder | balanced | 0.000895665 | 0 | 0.00106181 | 0.00772201 | 0.213023 | 0.0469343 | 0.267899 | 0.582383 |  |  |  |  | False | False | False | False |

## Decision

- No newer score-oriented probe becomes submit-safe under the old+pairwise combined gate.
- The minimax/direns family is still more public-actionable than the S4/Q3 label-flow sensor because it carries much larger movement and strong combo/honest-CV evidence, but it is not validated by the old hidden-subset selector.
- Treat the current mixmin/direns files as score-oriented public probes, not as evidence that the 0.54 bottleneck is solved.
