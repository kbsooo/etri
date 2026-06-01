# H032 H012 Phase-Translator HS-JEPA

## Question

H012 may be a phase point, not just a set of public-core cells. Can a state/action decoder that withholds H012's public score recover H012 or a stronger sibling from a dense E247-to-posterior phase diagram?

## H012 Reproduction Check

- top-1200 H012-score cells reproduction max logit error: `0.000000000`
- generated phase candidates including anchor: `4263`
- anchor H012 phase loss delta vs E247: `-0.007163306`
- anchor pre-H012 state mean prediction: `0.563377063`
- anchor pre-H012 geometry mean prediction: `0.554914250`

## Decoder Health

- best pre-H012 decoder: `geometry` alpha `10.0`, LOO MAE `0.000295413`, Spearman `0.950877193`, pairwise `0.923976608`
- pre-H012 state decoder rows:

| feature_set | alpha | loo_mae | loo_spearman | loo_pair_acc |
| --- | --- | --- | --- | --- |
| state | 10.000000000 | 0.000462279 | 0.714035088 | 0.865497076 |
| state | 100.000000000 | 0.000505698 | 0.961403509 | 0.935672515 |
| state | 1.000000000 | 0.001484389 | 0.585964912 | 0.777777778 |

## Selected Phase Point

| candidate_id | score_name | target_group | k | alpha | curve | pre_state_mean | pre_state_margin_vs_h012_pred | pre_geometry_mean | phase_loss_margin_vs_h012 | changed_cells_vs_h012 | max_abs_prob_vs_h012 | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| anchor_h012_actual | anchor | all | 1200 | 0.700000000 | actual | 0.563377063 | 0.000000000 | 0.554914250 | 0.000000000 | 0 | 0.000000000 | submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv |
| identity_phase_score_all_k120_a0.7_uniform | identity_phase_score | all | 120 | 0.700000000 | uniform | 0.573188862 | 0.009811799 | 0.573553797 | 0.004348955 | 1080 | 0.188906013 | hitl/h032_h012_phase_translator_jepa/submission_h032_identity_phase_score_all_k120_a0.7_uniform_f40f6bb2.csv |
| identity_phase_score_all_k120_a0.7_consistency | identity_phase_score | all | 120 | 0.700000000 | consistency | 0.573209893 | 0.009832830 | 0.573577194 | 0.004353302 | 1104 | 0.188906013 | hitl/h032_h012_phase_translator_jepa/submission_h032_identity_phase_score_all_k120_a0.7_consistency_aa371375.csv |
| identity_phase_score_all_k120_a0.8_score_soft | identity_phase_score | all | 120 | 0.800000000 | score_soft | 0.573392426 | 0.010015363 | 0.574011967 | 0.004416025 | 1200 | 0.188906013 | hitl/h032_h012_phase_translator_jepa/submission_h032_identity_phase_score_all_k120_a0.8_score_soft_06458470.csv |
| identity_phase_score_all_k120_a0.7_target_route | identity_phase_score | all | 120 | 0.700000000 | target_route | 0.573474110 | 0.010097047 | 0.573737158 | 0.004383535 | 1200 | 0.188906013 | hitl/h032_h012_phase_translator_jepa/submission_h032_identity_phase_score_all_k120_a0.7_target_route_eda005e8.csv |
| cell_score_all_k1200_a0.6_uniform | cell_score | all | 1200 | 0.600000000 | uniform | 0.576413418 | 0.013036355 | 0.558812161 | 0.000391310 | 1200 | 0.039905747 | hitl/h032_h012_phase_translator_jepa/submission_h032_cell_score_all_k1200_a0.6_uniform_f91b26d7.csv |
| identity_phase_score_all_k120_a0.7_score_soft | identity_phase_score | all | 120 | 0.700000000 | score_soft | 0.573459432 | 0.010082368 | 0.574166474 | 0.004553678 | 1199 | 0.188906013 | hitl/h032_h012_phase_translator_jepa/submission_h032_identity_phase_score_all_k120_a0.7_score_soft_7a9458d4.csv |
| cell_score_all_k1200_a0.6_consistency | cell_score | all | 1200 | 0.600000000 | consistency | 0.576603582 | 0.013226519 | 0.558892338 | 0.000406342 | 1200 | 0.039905747 | hitl/h032_h012_phase_translator_jepa/submission_h032_cell_score_all_k1200_a0.6_consistency_32a229c3.csv |
| identity_phase_score_all_k120_a0.6_uniform | identity_phase_score | all | 120 | 0.600000000 | uniform | 0.573736657 | 0.010359594 | 0.573881813 | 0.004510464 | 1200 | 0.188906013 | hitl/h032_h012_phase_translator_jepa/submission_h032_identity_phase_score_all_k120_a0.6_uniform_412a9dd1.csv |
| identity_phase_score_all_k120_a0.6_target_route | identity_phase_score | all | 120 | 0.600000000 | target_route | 0.573748705 | 0.010371642 | 0.573842773 | 0.004547548 | 1200 | 0.188906013 | hitl/h032_h012_phase_translator_jepa/submission_h032_identity_phase_score_all_k120_a0.6_target_route_75361376.csv |
| identity_phase_score_all_k120_a0.6_consistency | identity_phase_score | all | 120 | 0.600000000 | consistency | 0.573753749 | 0.010376686 | 0.573884907 | 0.004515435 | 1200 | 0.188906013 | hitl/h032_h012_phase_translator_jepa/submission_h032_identity_phase_score_all_k120_a0.6_consistency_d4c375d5.csv |
| identity_phase_score_all_k120_a0.8_consistency | identity_phase_score | all | 120 | 0.800000000 | consistency | 0.573821096 | 0.010444033 | 0.573860512 | 0.004240920 | 1200 | 0.188906013 | hitl/h032_h012_phase_translator_jepa/submission_h032_identity_phase_score_all_k120_a0.8_consistency_ce638dfe.csv |
| identity_phase_score_all_k120_a0.8_uniform | identity_phase_score | all | 120 | 0.800000000 | uniform | 0.573843946 | 0.010466882 | 0.573866483 | 0.004237566 | 1200 | 0.188906013 | hitl/h032_h012_phase_translator_jepa/submission_h032_identity_phase_score_all_k120_a0.8_uniform_12af64f6.csv |
| identity_phase_score_all_k120_a0.8_target_route | identity_phase_score | all | 120 | 0.800000000 | target_route | 0.573866888 | 0.010489825 | 0.573885727 | 0.004267863 | 1200 | 0.188906013 | hitl/h032_h012_phase_translator_jepa/submission_h032_identity_phase_score_all_k120_a0.8_target_route_14b83676.csv |
| cell_score_Q3S_k1000_a0.7_uniform | cell_score | Q3S | 1000 | 0.700000000 | uniform | 0.576394011 | 0.013016948 | 0.560494105 | 0.001231933 | 344 | 0.189622758 | hitl/h032_h012_phase_translator_jepa/submission_h032_cell_score_Q3S_k1000_a0.7_uniform_6b14229e.csv |
| cell_score_all_k1200_a0.95_score_soft | cell_score | all | 1200 | 0.950000000 | score_soft | 0.575731892 | 0.012354829 | 0.562510926 | -0.000319199 | 1200 | 0.083215059 | hitl/h032_h012_phase_translator_jepa/submission_h032_cell_score_all_k1200_a0.95_score_soft_f4486471.csv |
| route_translator_score_Q3S_k1000_a0.7_uniform | route_translator_score | Q3S | 1000 | 0.700000000 | uniform | 0.576455002 | 0.013077939 | 0.560518173 | 0.001238540 | 360 | 0.189622758 | hitl/h032_h012_phase_translator_jepa/submission_h032_route_translator_score_Q3S_k1000_a0.7_uniform_1fd98d8f.csv |
| identity_phase_score_all_k120_a0.6_score_soft | identity_phase_score | all | 120 | 0.600000000 | score_soft | 0.573926672 | 0.010549609 | 0.574390231 | 0.004731263 | 1200 | 0.188906013 | hitl/h032_h012_phase_translator_jepa/submission_h032_identity_phase_score_all_k120_a0.6_score_soft_921e500c.csv |
| cell_score_all_k1200_a0.5_uniform | cell_score | all | 1200 | 0.500000000 | uniform | 0.576413418 | 0.013036355 | 0.561715957 | 0.000906254 | 1200 | 0.081501075 | hitl/h032_h012_phase_translator_jepa/submission_h032_cell_score_all_k1200_a0.5_uniform_73d6fcf2.csv |
| identity_phase_score_all_k120_a0.95_score_soft | identity_phase_score | all | 120 | 0.950000000 | score_soft | 0.574005540 | 0.010628476 | 0.573947614 | 0.004277174 | 1200 | 0.188906013 | hitl/h032_h012_phase_translator_jepa/submission_h032_identity_phase_score_all_k120_a0.95_score_soft_3ecebc26.csv |
| cell_score_all_k1200_a0.5_consistency | cell_score | all | 1200 | 0.500000000 | consistency | 0.576494244 | 0.013117180 | 0.561781209 | 0.000921983 | 1200 | 0.081501075 | hitl/h032_h012_phase_translator_jepa/submission_h032_cell_score_all_k1200_a0.5_consistency_0be75a2f.csv |
| cell_score_Q3S_k1000_a0.7_consistency | cell_score | Q3S | 1000 | 0.700000000 | consistency | 0.576655656 | 0.013278593 | 0.560799203 | 0.001242901 | 599 | 0.189622758 | hitl/h032_h012_phase_translator_jepa/submission_h032_cell_score_Q3S_k1000_a0.7_consistency_def61111.csv |
| identity_phase_score_Q3S_k120_a0.8_score_soft | identity_phase_score | Q3S | 120 | 0.800000000 | score_soft | 0.574427238 | 0.011050174 | 0.572970320 | 0.004578746 | 1200 | 0.189622758 | hitl/h032_h012_phase_translator_jepa/submission_h032_identity_phase_score_Q3S_k120_a0.8_score_soft_08ddad5b.csv |
| identity_phase_score_Q3S_k120_a0.7_score_soft | identity_phase_score | Q3S | 120 | 0.700000000 | score_soft | 0.574390253 | 0.011013190 | 0.573215823 | 0.004705315 | 1199 | 0.189622758 | hitl/h032_h012_phase_translator_jepa/submission_h032_identity_phase_score_Q3S_k120_a0.7_score_soft_6afddab6.csv |

## Family Summary

| score_name | target_group | curve | n | best_candidate_id | best_pre_state_mean | best_pre_state_margin_vs_h012_pred | best_phase_loss_margin_vs_h012 | best_changed_cells_vs_h012 | best_max_abs_prob_vs_h012 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| anchor | all | actual | 1 | anchor_h012_actual | 0.563377063 | 0.000000000 | 0.000000000 | 0 | 0.000000000 |
| identity_phase_score | all | uniform | 63 | identity_phase_score_all_k120_a0.7_uniform | 0.573188862 | 0.009811799 | 0.004348955 | 1080 | 0.188906013 |
| identity_phase_score | all | consistency | 63 | identity_phase_score_all_k120_a0.7_consistency | 0.573209893 | 0.009832830 | 0.004353302 | 1104 | 0.188906013 |
| identity_phase_score | all | score_soft | 70 | identity_phase_score_all_k120_a0.8_score_soft | 0.573392426 | 0.010015363 | 0.004416025 | 1200 | 0.188906013 |
| identity_phase_score | all | target_route | 63 | identity_phase_score_all_k120_a0.7_target_route | 0.573474110 | 0.010097047 | 0.004383535 | 1200 | 0.188906013 |
| identity_phase_score | Q3S | score_soft | 56 | identity_phase_score_Q3S_k120_a0.8_score_soft | 0.574427238 | 0.011050174 | 0.004578746 | 1200 | 0.189622758 |
| identity_phase_score | Q3S | uniform | 49 | identity_phase_score_Q3S_k120_a0.7_uniform | 0.574595428 | 0.011218365 | 0.004527048 | 1080 | 0.189622758 |
| identity_phase_score | Q3S | consistency | 49 | identity_phase_score_Q3S_k120_a0.7_consistency | 0.574613419 | 0.011236356 | 0.004530163 | 1099 | 0.189622758 |
| identity_phase_score | Q3S | target_route | 49 | identity_phase_score_Q3S_k120_a0.7_target_route | 0.574798843 | 0.011421780 | 0.004527957 | 1200 | 0.189622758 |
| cell_score | S2S4 | uniform | 28 | cell_score_S2S4_k400_a0.7_uniform | 0.575151077 | 0.011774013 | 0.004658660 | 802 | 0.294110279 |
| cell_score | S2S4 | consistency | 28 | cell_score_S2S4_k400_a0.7_consistency | 0.575201410 | 0.011824346 | 0.004663916 | 940 | 0.294110279 |
| route_translator_score | S2S4 | uniform | 21 | route_translator_score_S2S4_k400_a0.7_uniform | 0.575257825 | 0.011880761 | 0.004661261 | 824 | 0.294110279 |
| route_translator_score | S2S4 | consistency | 21 | route_translator_score_S2S4_k400_a0.7_consistency | 0.575305817 | 0.011928753 | 0.004666523 | 955 | 0.294110279 |
| memory_conflict_phase_score | S2S4 | uniform | 21 | memory_conflict_phase_score_S2S4_k400_a0.7_uniform | 0.575326895 | 0.011949831 | 0.004664016 | 844 | 0.294110279 |
| cell_score | S2S4 | target_route | 28 | cell_score_S2S4_k400_a0.6_target_route | 0.575330847 | 0.011953783 | 0.004737628 | 1201 | 0.294110279 |
| identity_phase_score | S2S4 | uniform | 21 | identity_phase_score_S2S4_k400_a0.7_uniform | 0.575341702 | 0.011964638 | 0.004664627 | 838 | 0.294110279 |
| memory_conflict_phase_score | S2S4 | consistency | 21 | memory_conflict_phase_score_S2S4_k400_a0.7_consistency | 0.575373662 | 0.011996598 | 0.004669282 | 971 | 0.294110279 |
| identity_phase_score | S2S4 | consistency | 21 | identity_phase_score_S2S4_k400_a0.7_consistency | 0.575388290 | 0.012011227 | 0.004669865 | 965 | 0.294110279 |
| route_translator_score | S2S4 | target_route | 21 | route_translator_score_S2S4_k400_a0.6_target_route | 0.575422710 | 0.012045646 | 0.004740107 | 1212 | 0.294110279 |
| cell_score | S2S4 | score_soft | 28 | cell_score_S2S4_k400_a0.8_score_soft | 0.575445881 | 0.012068818 | 0.004670083 | 1201 | 0.294110279 |
| memory_conflict_phase_score | S2S4 | target_route | 21 | memory_conflict_phase_score_S2S4_k400_a0.6_target_route | 0.575482095 | 0.012105031 | 0.004742730 | 1222 | 0.294110279 |
| identity_phase_score | S2S4 | target_route | 21 | identity_phase_score_S2S4_k400_a0.6_target_route | 0.575495014 | 0.012117950 | 0.004743317 | 1219 | 0.294110279 |
| route_translator_score | S2S4 | score_soft | 28 | route_translator_score_S2S4_k600_a0.8_score_soft | 0.575606389 | 0.012229326 | 0.004639920 | 1301 | 0.294110279 |
| memory_conflict_phase_score | S2S4 | score_soft | 28 | memory_conflict_phase_score_S2S4_k600_a0.8_score_soft | 0.575626102 | 0.012249038 | 0.004656590 | 1301 | 0.294110279 |

## Stress

- decision: `diagnostic_only_translator_recovers_h012_anchor`
- promoted path: `none`
- pre-H012 public-score permutation p(lower margin): `1.000000000`
- H025 row-permutation stress: `{'skipped': 'selected_is_existing_h012_anchor'}`

## Interpretation

The phase translator recovers the existing H012 anchor as the best point. That is positive architecture evidence: the H012 action is not arbitrary under the state/action view. It is negative submission evidence: the dense phase map did not find a stronger sibling.

## Files

- `hitl/h032_h012_phase_translator_jepa/h032_cell_phase_state.csv`
- `hitl/h032_h012_phase_translator_jepa/h032_generated_phase_candidates.csv`
- `hitl/h032_h012_phase_translator_jepa/h032_phase_candidate_scores.csv`
- `hitl/h032_h012_phase_translator_jepa/h032_family_summary.csv`
- `hitl/h032_h012_phase_translator_jepa/h032_pre_h012_h024_model_scores.csv`
- `hitl/h032_h012_phase_translator_jepa/h032_direct_decoder_predictions.csv`
- `hitl/h032_h012_phase_translator_jepa/h032_selected_pre_h012_public_perm_stress.csv`
- `hitl/h032_h012_phase_translator_jepa/h032_selected_h025_rowperm_stress.csv`
