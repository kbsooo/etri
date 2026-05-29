# E169 E166 Context/Safety Mask Materializer

## Question

Do the E168 context-high safety masks remain healthy after turning them into actual E95-relative prediction tensors and rerunning breadth plus bad-axis geometry?

## Summary

- policies scored: `11`.
- stress-gate policies: `2`.
- materialized files: `2`.

## Stress Summary

| policy | expected_delta_focus_mean | moved_cells | moved_rows | cells_to_flip_expected | top1_over_abs_expected | bad_span_energy | max_bad_axis | max_bad_cos | mean_abs_logit_move_vs_e95 | max_abs_logit_move_vs_e95 | q2s3_share_vs_e95 | cos_e154_axis | cos_e101_axis | e168_decoupling_pass | stress_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| context_high__veto | -0.000120457 | 904 | 193 | 32 | 0.048415375 | 0.295326361 | q2_bad | 0.222381361 | 0.001095928 | 0.010205926 | 0.347774767 | 0.087179503 | -0.021895958 | True | True |
| context_high__high_density_p50 | -0.000119080 | 894 | 193 | 32 | 0.048975175 | 0.295856452 | q2_bad | 0.222464074 | 0.001085851 | 0.010205926 | 0.341722038 | 0.087508921 | -0.000000000 | True | True |
| all_e166 | -0.000332077 | 1750 | 250 | 74 | 0.023369627 | 0.450742441 | q2_bad | 0.268538582 | 0.002243986 | 0.013580886 | 0.250718585 | 0.061661852 | -0.099145675 | False | False |
| context_high | -0.000271072 | 1351 | 193 | 58 | 0.028628967 | 0.415439138 | q2_bad | 0.252707628 | 0.001788957 | 0.013580886 | 0.256386842 | 0.070669551 | -0.107487828 |  | False |
| safety_veto_null | -0.000153945 | 1175 | 250 | 41 | 0.037883419 | 0.308191792 | q2_bad | 0.225635049 | 0.001397643 | 0.010205926 | 0.336788670 | 0.074177780 | -0.022148866 | False | False |
| safety_high_density_p50 | -0.000152607 | 1164 | 250 | 41 | 0.038215507 | 0.309090630 | q2_bad | 0.225456969 | 0.001386865 | 0.010205926 | 0.331634583 | 0.074439072 | -0.000000000 | False | False |
| safety_not_e72_active | -0.000111568 | 857 | 250 | 31 | 0.052272604 | 0.316963505 | q2_bad | 0.274938361 | 0.000997566 | 0.010205926 | 0.461054652 | 0.118273185 | -0.000000000 | False | False |
| context_high__veto_not_e72 | -0.000088834 | 661 | 193 | 25 | 0.065649763 | 0.315791937 | q2_bad | 0.272761645 | 0.000785318 | 0.010205926 | 0.472495568 | 0.120641357 | -0.000000000 | False | False |
| context_high__veto__s_only | -0.000079565 | 501 | 192 | 22 | 0.073298103 | 0.172722610 | resid_bad | 0.119984845 | 0.000625874 | 0.010205926 | 0.290399184 | 0.111858999 | -0.029618367 | False | False |
| context_high__veto__no_q2s3 | -0.000078649 | 571 | 191 | 20 | 0.074151547 | 0.218983086 | stage2 | 0.098357443 | 0.000714792 | 0.010205926 | 0.000000000 | 0.070530741 | -0.000000000 | False | False |
| context_high__high_density_p75 | -0.000074316 | 549 | 191 | 19 | 0.078475648 | 0.215055968 | stage2 | 0.103711411 | 0.000685447 | 0.010205926 | 0.000000000 | 0.070349658 | -0.000000000 | False | False |

## Materialized Shortlist

| policy | materialized_file | expected_delta_focus_mean | moved_cells | cells_to_flip_expected | top1_over_abs_expected | bad_span_energy | max_bad_cos | q2s3_share_vs_e95 | e168_top_benefit_focus_cells_kept | e168_edge_like_rate | e168_between_train_runs_rate | e168_all_veto_null_rate | e168_all_safe_density_mean | e168_e72_active_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| context_high__veto | submission_e169_ctx_veto_c5e806e3.csv | -0.000120457 | 904 | 32 | 0.048415375 | 0.295326361 | 0.222381361 | 0.347774767 | 19.000000000 | 0.610619469 | 0.819690265 | 1.000000000 | 0.346150416 | 0.268805310 |
| context_high__high_density_p50 | submission_e169_ctx_high_density_p50_51110c7e.csv | -0.000119080 | 894 | 32 | 0.048975175 | 0.295856452 | 0.222464074 | 0.341722038 | 19.000000000 | 0.610738255 | 0.817673378 | 1.000000000 | 0.349218243 | 0.260626398 |

## Decision

E169 promotes the E168 result from a cell-mask diagnostic to actual candidate tensors. If a masked policy passes, it is not an E166 scale-up: it is a lower-amplitude context/safety repair that keeps only the E166 cells where hidden context and veto-density comfort overlap. It should be treated as a safer broad-branch follow-up than raw E166, but still needs public framing because the broad branch has no positive public anchor yet.
