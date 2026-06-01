# H031 Memory-Conflict Public-Core HS-JEPA

## Question

V106-style same-subject memory is strong, but H014 showed that H012's public-equation gain mostly lives where that memory disagrees. H031 asks whether those memory-conflict cells are the real public core that should be amplified or protected, rather than pruned.

## Observation

- H012 changed cells: `1200`
- memory-disagree cells: `714` with gain share `0.720328567`
- memory-agree cells: `486` with gain share `0.279671433`
- target conflict summary:

| target | changed_cells | posterior_gain | disagree_cells | agree_cells | disagree_gain_share | total_gain_share |
| --- | --- | --- | --- | --- | --- | --- |
| S2 | 207 | 2.732940594 | 120 | 87 | 0.798765279 | 0.218011107 |
| S1 | 194 | 2.546570998 | 133 | 61 | 0.782523072 | 0.203144102 |
| Q3 | 141 | 1.931075098 | 63 | 78 | 0.450135953 | 0.154044995 |
| Q1 | 167 | 1.716407641 | 92 | 75 | 0.739922106 | 0.136920623 |
| S4 | 192 | 1.649612252 | 131 | 61 | 0.840262496 | 0.131592247 |
| S3 | 194 | 1.486705555 | 111 | 83 | 0.682140244 | 0.118596915 |
| Q2 | 105 | 0.472473930 | 64 | 41 | 0.665968851 | 0.037690012 |

## Experiment

Generated candidate routes around H012: conflict-core amplification, conflict-core plus agree-cost rollback, agree-cost rollback alone, and core-only reconstruction from E247. The route score combines posterior gain, memory disagreement, anti-memory alignment, row-target identity, and joint-vector support.

## Result

- generated candidates: `482`
- decision: `diagnostic_only_memory_conflict_core_not_action_safe`
- promoted path: `none`

## Family Summary

| family | target_group | n | best_candidate_id | best_pred_public_median | best_margin_vs_h012 | best_support_better_than_h012 | best_risk_width | median_pred_public |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conflict_amp | S | 25 | conflict_amp_S_core120_a0.4_rb0_r0_h012 | 0.569663678 | 0.001540195 | 0.150000000 | 0.020957625 | 0.570676212 |
| conflict_amp | Q3S | 30 | conflict_amp_Q3S_core120_a0.4_rb0_r0_h012 | 0.569718203 | 0.001594720 | 0.150000000 | 0.021074194 | 0.572052805 |
| conflict_amp | all | 30 | conflict_amp_all_core120_a0.4_rb0_r0_h012 | 0.569746461 | 0.001622978 | 0.150000000 | 0.021220570 | 0.571919123 |
| conflict_swap | S124 | 72 | conflict_swap_S124_core120_a0.28_rb60_r0.35_h012 | 0.569809630 | 0.001686147 | 0.150000000 | 0.020011835 | 0.572337499 |
| conflict_amp | S12 | 20 | conflict_amp_S12_core240_a0.4_rb0_r0_h012 | 0.570020417 | 0.001896934 | 0.150000000 | 0.019918108 | 0.569759561 |
| conflict_swap | all | 96 | conflict_swap_all_core120_a0.28_rb60_r0.35_h012 | 0.570088517 | 0.001965034 | 0.133333333 | 0.020957337 | 0.572189660 |
| conflict_swap | Q3S | 96 | conflict_swap_Q3S_core120_a0.28_rb60_r0.35_h012 | 0.570342499 | 0.002219016 | 0.133333333 | 0.020528443 | 0.572356893 |
| conflict_amp | S2S4 | 20 | conflict_amp_S2S4_core60_a0.4_rb0_r0_h012 | 0.570487744 | 0.002364260 | 0.133333333 | 0.022133106 | 0.572453224 |
| conflict_amp | S124 | 10 | conflict_amp_S124_core360_a0.4_rb0_r0_h012 | 0.571600016 | 0.003476533 | 0.133333333 | 0.018604509 | 0.571625602 |
| agree_cost_rollback | Q3S3 | 12 | agree_cost_rollback_Q3S3_core0_a0_rb60_r0.4_h012 | 0.572601743 | 0.004478260 | 0.083333333 | 0.025270306 | 0.572948200 |
| agree_cost_rollback | Q | 12 | agree_cost_rollback_Q_core0_a0_rb120_r0.2_h012 | 0.572782290 | 0.004658807 | 0.083333333 | 0.025114358 | 0.572944375 |
| agree_cost_rollback | all | 20 | agree_cost_rollback_all_core0_a0_rb60_r0.2_h012 | 0.573374825 | 0.005251342 | 0.100000000 | 0.028639019 | 0.573712256 |
| agree_cost_rollback | S124 | 12 | agree_cost_rollback_S124_core0_a0_rb60_r1_h012 | 0.574086792 | 0.005963309 | 0.083333333 | 0.034164406 | 0.574312778 |
| core_only_from_e247 | S124 | 4 | core_only_from_e247_S124_core520_a1_rb0_r0_e247 | 0.574265153 | 0.006141670 | 0.066666667 | 0.016327695 | 0.574381538 |
| core_over_from_e247 | Q3S | 5 | core_over_from_e247_Q3S_core120_a1.15_rb0_r0_e247 | 0.574282982 | 0.006159499 | 0.066666667 | 0.013001463 | 0.573995597 |
| core_only_from_e247 | Q3S | 5 | core_only_from_e247_Q3S_core120_a1_rb0_r0_e247 | 0.574345204 | 0.006221721 | 0.066666667 | 0.016142170 | 0.573918677 |
| core_over_from_e247 | all | 5 | core_over_from_e247_all_core120_a1.15_rb0_r0_e247 | 0.574364857 | 0.006241373 | 0.066666667 | 0.013750634 | 0.573954866 |
| core_over_from_e247 | S124 | 4 | core_over_from_e247_S124_core520_a1.15_rb0_r0_e247 | 0.574407211 | 0.006283728 | 0.066666667 | 0.013274282 | 0.574460516 |
| core_only_from_e247 | all | 4 | core_only_from_e247_all_core120_a1_rb0_r0_e247 | 0.574425496 | 0.006302013 | 0.066666667 | 0.017409813 | 0.574527837 |

## Top Candidates

| candidate_id | family | target_group | pred_public_median | pred_public_p10 | pred_public_p90 | margin_vs_h012_pred | support_better_than_h012 | risk_width | changed_cells_vs_h012 | max_abs_prob_vs_h012 | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conflict_swap_S124_core120_a0.28_rb60_r0.35_h012 | conflict_swap | S124 | 0.569809630 | 0.561924630 | 0.581936465 | 0.001686147 | 0.150000000 | 0.020011835 | 180 | 0.030153881 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_swap_S124_core120_a0.28_rb60_r0.35_h012_07347231.csv |
| conflict_amp_S12_core240_a0.4_rb0_r0_h012 | conflict_amp | S12 | 0.570020417 | 0.562204412 | 0.582122520 | 0.001896934 | 0.150000000 | 0.019918108 | 240 | 0.037481847 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S12_core240_a0.4_rb0_r0_h012_a9eb084c.csv |
| conflict_amp_S12_core360_a0.4_rb0_r0_h012 | conflict_amp | S12 | 0.570131985 | 0.562328123 | 0.582143028 | 0.002008502 | 0.133333333 | 0.019814906 | 253 | 0.037481847 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S12_core360_a0.4_rb0_r0_h012_d59a63df.csv |
| conflict_amp_S12_core240_a0.28_rb0_r0_h012 | conflict_amp | S12 | 0.569979213 | 0.561941640 | 0.582140723 | 0.001855730 | 0.150000000 | 0.020199083 | 240 | 0.027418125 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S12_core240_a0.28_rb0_r0_h012_aa2bf6c0.csv |
| conflict_amp_S_core120_a0.4_rb0_r0_h012 | conflict_amp | S | 0.569663678 | 0.560853638 | 0.581811262 | 0.001540195 | 0.150000000 | 0.020957625 | 120 | 0.037481847 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S_core120_a0.4_rb0_r0_h012_e0f2edf5.csv |
| conflict_amp_S12_core360_a0.28_rb0_r0_h012 | conflict_amp | S12 | 0.570099003 | 0.562065257 | 0.582161007 | 0.001975520 | 0.133333333 | 0.020095750 | 253 | 0.027418125 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S12_core360_a0.28_rb0_r0_h012_bdd0b841.csv |
| conflict_amp_S12_core240_a0.18_rb0_r0_h012 | conflict_amp | S12 | 0.569948728 | 0.561720584 | 0.582157557 | 0.001825245 | 0.150000000 | 0.020436973 | 240 | 0.018283244 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S12_core240_a0.18_rb0_r0_h012_f8acccb7.csv |
| conflict_amp_S_core120_a0.28_rb0_r0_h012 | conflict_amp | S | 0.569597933 | 0.560581786 | 0.581833581 | 0.001474450 | 0.150000000 | 0.021251795 | 120 | 0.027418125 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S_core120_a0.28_rb0_r0_h012_2fed1d01.csv |
| conflict_amp_S12_core120_a0.4_rb0_r0_h012 | conflict_amp | S12 | 0.569614885 | 0.560547678 | 0.581789737 | 0.001491402 | 0.150000000 | 0.021242059 | 120 | 0.037481847 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S12_core120_a0.4_rb0_r0_h012_83aaab39.csv |
| conflict_amp_S12_core360_a0.18_rb0_r0_h012 | conflict_amp | S12 | 0.570068495 | 0.561844137 | 0.582177636 | 0.001945012 | 0.133333333 | 0.020333499 | 253 | 0.018283244 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S12_core360_a0.18_rb0_r0_h012_d057b472.csv |
| conflict_swap_S124_core120_a0.28_rb60_r0.65_h012 | conflict_swap | S124 | 0.570726670 | 0.562999310 | 0.582018376 | 0.002603187 | 0.133333333 | 0.019019066 | 180 | 0.055714800 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_swap_S124_core120_a0.28_rb60_r0.65_h012_f23ca9aa.csv |
| conflict_amp_Q3S_core120_a0.4_rb0_r0_h012 | conflict_amp | Q3S | 0.569718203 | 0.561116853 | 0.582191047 | 0.001594720 | 0.150000000 | 0.021074194 | 120 | 0.045028466 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_Q3S_core120_a0.4_rb0_r0_h012_0758f877.csv |
| conflict_amp_S_core120_a0.18_rb0_r0_h012 | conflict_amp | S | 0.569525721 | 0.560352596 | 0.581854271 | 0.001402238 | 0.150000000 | 0.021501675 | 120 | 0.018283244 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S_core120_a0.18_rb0_r0_h012_ef040858.csv |
| conflict_amp_S12_core120_a0.28_rb0_r0_h012 | conflict_amp | S12 | 0.569550054 | 0.560286959 | 0.581811570 | 0.001426571 | 0.150000000 | 0.021524612 | 120 | 0.027418125 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S12_core120_a0.28_rb0_r0_h012_3b9746d6.csv |
| conflict_amp_Q3S_core120_a0.28_rb0_r0_h012 | conflict_amp | Q3S | 0.569634921 | 0.560856042 | 0.582212794 | 0.001511437 | 0.150000000 | 0.021356751 | 120 | 0.031792741 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_Q3S_core120_a0.28_rb0_r0_h012_5e32eab9.csv |
| conflict_amp_S_core120_a0.1_rb0_r0_h012 | conflict_amp | S | 0.569482584 | 0.560167244 | 0.581872411 | 0.001359101 | 0.150000000 | 0.021705167 | 120 | 0.010458284 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S_core120_a0.1_rb0_r0_h012_e2e1ae3a.csv |
| conflict_amp_S12_core240_a0.1_rb0_r0_h012 | conflict_amp | S12 | 0.569922059 | 0.561333569 | 0.582172282 | 0.001798576 | 0.150000000 | 0.020838714 | 240 | 0.010458284 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S12_core240_a0.1_rb0_r0_h012_f6a56c4f.csv |
| conflict_amp_Q3S_core120_a0.18_rb0_r0_h012 | conflict_amp | Q3S | 0.569556668 | 0.560636485 | 0.582232978 | 0.001433185 | 0.150000000 | 0.021596493 | 120 | 0.020577678 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_Q3S_core120_a0.18_rb0_r0_h012_f2f83a96.csv |
| conflict_amp_all_core120_a0.4_rb0_r0_h012 | conflict_amp | all | 0.569746461 | 0.560921931 | 0.582142501 | 0.001622978 | 0.150000000 | 0.021220570 | 120 | 0.045028466 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_all_core120_a0.4_rb0_r0_h012_c5978cb1.csv |
| conflict_amp_S_core60_a0.4_rb0_r0_h012 | conflict_amp | S | 0.569583790 | 0.560985124 | 0.582538362 | 0.001460307 | 0.150000000 | 0.021553238 | 60 | 0.037481847 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S_core60_a0.4_rb0_r0_h012_2f3dc2d2.csv |
| conflict_amp_S_core120_a0.05_rb0_r0_h012 | conflict_amp | S | 0.569455126 | 0.560050388 | 0.581884556 | 0.001331643 | 0.150000000 | 0.021834169 | 120 | 0.005325117 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S_core120_a0.05_rb0_r0_h012_b497742b.csv |
| conflict_amp_S12_core120_a0.18_rb0_r0_h012 | conflict_amp | S12 | 0.569491140 | 0.560067429 | 0.581831663 | 0.001367657 | 0.150000000 | 0.021764233 | 120 | 0.018283244 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S12_core120_a0.18_rb0_r0_h012_42e473a9.csv |
| conflict_amp_Q3S_core120_a0.1_rb0_r0_h012 | conflict_amp | Q3S | 0.569509285 | 0.560459162 | 0.582250695 | 0.001385802 | 0.150000000 | 0.021791533 | 120 | 0.011491494 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_Q3S_core120_a0.1_rb0_r0_h012_3ea7ef73.csv |
| conflict_amp_S_core60_a0.28_rb0_r0_h012 | conflict_amp | S | 0.569544689 | 0.560807234 | 0.582551350 | 0.001421205 | 0.150000000 | 0.021744116 | 60 | 0.027418125 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_S_core60_a0.28_rb0_r0_h012_adca4b16.csv |
| conflict_amp_all_core120_a0.28_rb0_r0_h012 | conflict_amp | all | 0.569666084 | 0.560659498 | 0.582167150 | 0.001542600 | 0.150000000 | 0.021507651 | 120 | 0.031792741 | hitl/h031_memory_conflict_public_core_jepa/submission_h031_conflict_amp_all_core120_a0.28_rb0_r0_h012_209f5a6d.csv |

## H024/H025 Stress

- best H024 decoder: `geometry` alpha `100.0`, LOO MAE `0.000772855`, Spearman `0.969924812`, pairwise `0.947368421`
- selected diagnostic: `conflict_swap_S124_core120_a0.28_rb60_r0.35_h012`
- selected predicted margin vs H012: `0.001686147`
- H024 public-score permutation p(lower margin): `0.800666667`
- H025 row-permutation p(higher top1200 gain): `0.183333333`
- real H025 top1200 gain: `4.614344174`

## Interpretation

Conflict-core amplification did not survive the action-health stresses. The memory-disagree observation remains an explanation of H012, not a safe post-H012 action. V106 memory is therefore positioned as a contrastive view: useful to expose H012's public-core cells, but not a replacement or mechanical amplifier for them.

## Files

- `hitl/h031_memory_conflict_public_core_jepa/h031_cell_state.csv`
- `hitl/h031_memory_conflict_public_core_jepa/h031_target_conflict_summary.csv`
- `hitl/h031_memory_conflict_public_core_jepa/h031_generated_candidates.csv`
- `hitl/h031_memory_conflict_public_core_jepa/h031_candidate_scores.csv`
- `hitl/h031_memory_conflict_public_core_jepa/h031_family_summary.csv`
- `hitl/h031_memory_conflict_public_core_jepa/h031_h024_model_scores.csv`
- `hitl/h031_memory_conflict_public_core_jepa/h031_selected_h024_public_perm_stress.csv`
- `hitl/h031_memory_conflict_public_core_jepa/h031_selected_h025_rowperm_stress.csv`
