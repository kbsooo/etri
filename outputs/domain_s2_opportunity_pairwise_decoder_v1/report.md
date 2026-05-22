# S2 Opportunity Pairwise Decoder

## Purpose

Test the same opportunity/Q-state S2 signal with decoders that expand the 450 labels into pairwise ranking comparisons or prototype-to-label distances. This keeps the input family narrow while avoiding the coarse KMeans state bin failure.

## Result

- Nested S2 logloss: `0.567981`
- Current protected fixed-map S2 logloss: `0.567195`
- Direct full-fold `psg_opp` probe S2 logloss: `0.562387`
- Projected fixed-map avg if only S2 is replaced: `0.610357`
- Current fixed-map avg reference: `0.610244`
- Best fixed candidate: `psg_qrel__absolute__logreg_c0p1__b20`
- Best fixed candidate S2 logloss: `0.558302`
- Best fixed candidate projected fixed-map avg: `0.608974`

## Selection Counts

| selected | outer_count |
| --- | --- |
| psg_opp__absolute_plus_deviation__logreg_c0p1__b20 | 2 |
| psg_opp__deviation__rank_pairwise__b10 | 1 |
| psg_opp_mob__deviation__logreg_c0p1__b20 | 1 |
| psg_qrel__absolute__logreg_c0p1__b20 | 1 |

## Best Full-OOF Candidates

| candidate | full_oof_s2_log_loss |
| --- | --- |
| psg_qrel__absolute__logreg_c0p1__b20 | 0.558302 |
| psg_opp__deviation__rank_pairwise__b20 | 0.560485 |
| psg_opp_mob__deviation__logreg_c0p1__b20 | 0.560638 |
| psg_qrel__absolute__logreg_c0p03__b20 | 0.562342 |
| psg_opp__absolute_plus_deviation__logreg_c0p1__b20 | 0.562344 |
| psg_opp__deviation__rank_pairwise__b10 | 0.563465 |
| psg_opp_mob__deviation__logreg_c0p03__b20 | 0.564745 |
| psg_opp__deviation__logreg_c0p1__b20 | 0.564758 |
| psg_opp__absolute_plus_deviation__rank_pairwise__b10 | 0.566481 |
| psg_opp__absolute_plus_deviation__logreg_c0p03__b20 | 0.567596 |
| psg_opp__absolute_plus_deviation__rank_pairwise__b20 | 0.567957 |
| psg_opp__deviation__logreg_c0p03__b20 | 0.570201 |
| psg_opp_mob__deviation__rank_pairwise__b10 | 0.572619 |
| psg_opp__deviation__rank_pairwise__b35 | 0.574672 |
| psg_opp_mob__deviation__prototype__b10 | 0.580769 |
| psg_opp__absolute_plus_deviation__prototype__b10 | 0.580839 |
| psg_qrel__absolute__prototype__b10 | 0.580873 |
| psg_opp__deviation__prototype__b10 | 0.580946 |
| psg_qrel__absolute__rank_pairwise__b10 | 0.581814 |
| psg_opp__absolute_plus_deviation__rank_pairwise__b35 | 0.590848 |

## Inner Candidate Scores

| outer_fold | candidate | inner_s2_log_loss |
| --- | --- | --- |
| 1 | psg_opp_mob__deviation__logreg_c0p1__b20 | 0.554864 |
| 1 | psg_opp__absolute_plus_deviation__logreg_c0p1__b20 | 0.558436 |
| 1 | psg_opp_mob__deviation__logreg_c0p03__b20 | 0.559207 |
| 1 | psg_opp__deviation__logreg_c0p1__b20 | 0.561049 |
| 1 | psg_opp__absolute_plus_deviation__logreg_c0p03__b20 | 0.563537 |
| 1 | psg_opp__deviation__rank_pairwise__b10 | 0.564604 |
| 1 | psg_opp__deviation__logreg_c0p03__b20 | 0.566003 |
| 1 | psg_opp__absolute_plus_deviation__rank_pairwise__b10 | 0.568005 |
| 1 | psg_qrel__absolute__logreg_c0p03__b20 | 0.569074 |
| 1 | psg_qrel__absolute__logreg_c0p1__b20 | 0.571932 |
| 1 | psg_qrel__absolute__prototype__b10 | 0.573989 |
| 1 | psg_opp_mob__deviation__prototype__b10 | 0.574069 |
| 1 | psg_opp__absolute_plus_deviation__prototype__b10 | 0.574172 |
| 1 | psg_opp__deviation__prototype__b10 | 0.574194 |
| 1 | psg_opp_mob__deviation__rank_pairwise__b10 | 0.579485 |
| 1 | psg_opp__deviation__rank_pairwise__b20 | 0.581223 |
| 1 | psg_opp__absolute_plus_deviation__rank_pairwise__b20 | 0.593435 |
| 1 | psg_qrel__absolute__rank_pairwise__b10 | 0.597500 |
| 1 | psg_opp__deviation__rank_pairwise__b35 | 0.633490 |
| 1 | psg_opp_mob__deviation__rank_pairwise__b20 | 0.663255 |
| 1 | psg_opp__absolute_plus_deviation__rank_pairwise__b35 | 0.664524 |
| 1 | psg_qrel__absolute__rank_pairwise__b20 | 0.710505 |
| 1 | psg_opp_mob__deviation__rank_pairwise__b35 | 0.864466 |
| 1 | psg_qrel__absolute__rank_pairwise__b35 | 0.967204 |
| 2 | psg_opp__absolute_plus_deviation__logreg_c0p1__b20 | 0.578611 |
| 2 | psg_opp__deviation__logreg_c0p1__b20 | 0.581088 |
| 2 | psg_opp__absolute_plus_deviation__logreg_c0p03__b20 | 0.583715 |
| 2 | psg_opp__deviation__rank_pairwise__b10 | 0.585104 |
| 2 | psg_opp_mob__deviation__logreg_c0p1__b20 | 0.586546 |
| 2 | psg_opp__deviation__logreg_c0p03__b20 | 0.586715 |
| 2 | psg_opp__absolute_plus_deviation__rank_pairwise__b10 | 0.588692 |
| 2 | psg_opp_mob__deviation__logreg_c0p03__b20 | 0.589968 |
| 2 | psg_opp__deviation__rank_pairwise__b20 | 0.592586 |
| 2 | psg_qrel__absolute__logreg_c0p03__b20 | 0.595105 |
| 2 | psg_qrel__absolute__logreg_c0p1__b20 | 0.596146 |
| 2 | psg_opp_mob__deviation__prototype__b10 | 0.597455 |
| 2 | psg_opp__absolute_plus_deviation__prototype__b10 | 0.597503 |
| 2 | psg_opp__deviation__prototype__b10 | 0.597697 |
| 2 | psg_qrel__absolute__prototype__b10 | 0.597698 |
| 2 | psg_qrel__absolute__rank_pairwise__b10 | 0.605478 |
| 2 | psg_opp__absolute_plus_deviation__rank_pairwise__b20 | 0.606152 |
| 2 | psg_opp_mob__deviation__rank_pairwise__b10 | 0.615319 |
| 2 | psg_opp__deviation__rank_pairwise__b35 | 0.629351 |
| 2 | psg_opp__absolute_plus_deviation__rank_pairwise__b35 | 0.664908 |
| 2 | psg_qrel__absolute__rank_pairwise__b20 | 0.706432 |
| 2 | psg_opp_mob__deviation__rank_pairwise__b20 | 0.720186 |
| 2 | psg_qrel__absolute__rank_pairwise__b35 | 0.949050 |
| 2 | psg_opp_mob__deviation__rank_pairwise__b35 | 0.963212 |
| 3 | psg_qrel__absolute__logreg_c0p1__b20 | 0.577950 |
| 3 | psg_qrel__absolute__logreg_c0p03__b20 | 0.579531 |
| 3 | psg_opp_mob__deviation__logreg_c0p1__b20 | 0.580766 |
| 3 | psg_opp__absolute_plus_deviation__logreg_c0p1__b20 | 0.586322 |
| 3 | psg_opp__deviation__rank_pairwise__b10 | 0.586545 |
| 3 | psg_opp__absolute_plus_deviation__rank_pairwise__b10 | 0.587465 |
| 3 | psg_opp__deviation__logreg_c0p1__b20 | 0.587673 |
| 3 | psg_opp_mob__deviation__logreg_c0p03__b20 | 0.588059 |
| 3 | psg_opp__absolute_plus_deviation__logreg_c0p03__b20 | 0.590340 |
| 3 | psg_opp_mob__deviation__rank_pairwise__b10 | 0.591779 |
| 3 | psg_opp__deviation__logreg_c0p03__b20 | 0.591992 |
| 3 | psg_opp__deviation__rank_pairwise__b20 | 0.595383 |
| 3 | psg_qrel__absolute__rank_pairwise__b10 | 0.596904 |
| 3 | psg_opp_mob__deviation__prototype__b10 | 0.598715 |
| 3 | psg_qrel__absolute__prototype__b10 | 0.598855 |
| 3 | psg_opp__absolute_plus_deviation__prototype__b10 | 0.598933 |
| 3 | psg_opp__deviation__prototype__b10 | 0.599005 |
| 3 | psg_opp__absolute_plus_deviation__rank_pairwise__b20 | 0.600158 |
| 3 | psg_opp__deviation__rank_pairwise__b35 | 0.638590 |
| 3 | psg_opp__absolute_plus_deviation__rank_pairwise__b35 | 0.652113 |
| 3 | psg_opp_mob__deviation__rank_pairwise__b20 | 0.670614 |
| 3 | psg_qrel__absolute__rank_pairwise__b20 | 0.689713 |
| 3 | psg_opp_mob__deviation__rank_pairwise__b35 | 0.873865 |
| 3 | psg_qrel__absolute__rank_pairwise__b35 | 0.925132 |
| 4 | psg_opp__deviation__rank_pairwise__b10 | 0.566940 |
| 4 | psg_opp__absolute_plus_deviation__logreg_c0p1__b20 | 0.569236 |
| 4 | psg_opp__deviation__rank_pairwise__b20 | 0.570499 |
| 4 | psg_opp__deviation__logreg_c0p1__b20 | 0.571791 |
| 4 | psg_opp__absolute_plus_deviation__rank_pairwise__b10 | 0.571811 |
| 4 | psg_opp__absolute_plus_deviation__logreg_c0p03__b20 | 0.573490 |
| 4 | psg_opp__deviation__logreg_c0p03__b20 | 0.575506 |
| 4 | psg_opp_mob__deviation__logreg_c0p1__b20 | 0.579375 |

## Sample Drift vs v83

| mean_abs_s2_drift | max_abs_s2_drift | pred_s2_mean | ref_s2_mean |
| --- | --- | --- | --- |
| 0.070556 | 0.353653 | 0.671458 | 0.643925 |

## Fixed Best Candidate Drift vs v83

| mean_abs_s2_drift | max_abs_s2_drift | pred_s2_mean | ref_s2_mean |
| --- | --- | --- | --- |
| 0.084029 | 0.429558 | 0.678904 | 0.643925 |

## Fixed Candidate Stress

| candidate | s2_log_loss | projected_fixed_map_avg | mean_abs_s2_drift | max_abs_s2_drift | pred_s2_mean | ref_s2_mean |
| --- | --- | --- | --- | --- | --- | --- |
| psg_qrel__absolute__logreg_c0p1__b20 | 0.558302 | 0.608974 | 0.084029 | 0.429558 | 0.678904 | 0.643925 |
| psg_opp__deviation__rank_pairwise__b20 | 0.560485 | 0.609286 | 0.084054 | 0.378805 | 0.677204 | 0.643925 |
| psg_opp_mob__deviation__logreg_c0p1__b20 | 0.560638 | 0.609308 | 0.076404 | 0.406830 | 0.674212 | 0.643925 |
| psg_qrel__absolute__logreg_c0p03__b20 | 0.562342 | 0.609551 | 0.073460 | 0.382583 | 0.670976 | 0.643925 |
| psg_opp__absolute_plus_deviation__logreg_c0p1__b20 | 0.562344 | 0.609551 | 0.069635 | 0.337646 | 0.667531 | 0.643925 |
| psg_opp__deviation__rank_pairwise__b10 | 0.563465 | 0.609712 | 0.068243 | 0.326242 | 0.669030 | 0.643925 |
| psg_opp_mob__deviation__logreg_c0p03__b20 | 0.564745 | 0.609894 | 0.071339 | 0.377546 | 0.669708 | 0.643925 |
| psg_opp__deviation__logreg_c0p1__b20 | 0.564758 | 0.609896 | 0.072287 | 0.323332 | 0.665419 | 0.643925 |

## Read

- If pairwise ranking beats the protected S2 scout, the label bottleneck is helped by relative-day comparisons.
- If a fixed candidate beats nested selection, the signal is real but model-selection over the candidate grid is unstable. Treat the fixed candidate as a hypothesis to stress-test, not an automatically safe submission rule.
