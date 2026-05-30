# E255 E247 Public Feedback Decoder

## Public Observation

- submitted file: `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`
- public LB: `0.5761589494`
- improvement vs E95: `-0.0001323804`
- improvement vs mixmin: `-0.0001476911`
- improvement is `8.646x` the E95-over-mixmin edge.

## Anchor Deltas

| anchor_id | file_name | public_lb | delta_vs_e247 | delta_vs_e95 | role |
| --- | --- | --- | --- | --- | --- |
| e247 | submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0.576158949 | 0.000000000 | -0.000132380 | new_public_frontier |
| e95 | submission_e95_hardtail_541e3973.csv | 0.576291330 | 0.000132380 | 0.000000000 | previous_frontier |
| e101 | submission_e101_q2s3tail_177569bc.csv | 0.576300366 | 0.000141417 | 0.000009036 | small_loss_q2s3_tail |
| mixmin | submission_mixmin_0c916bb4.csv | 0.576306641 | 0.000147691 | 0.000015311 | anchor_loss_binary_world |
| e176 | submission_e176_abl_q2_to0p75_91e49725.csv | 0.576311831 | 0.000152882 | 0.000020501 | broad_q2_damped |
| e216 | submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | 0.577286509 | 0.001127559 | 0.000995179 | bad_s2_maskfam_jepa |

## Interpretation

- E247 is now the public frontier, not merely a diagnostic sensor.
- This is a strong positive update for the E207/E246 feature-neighbor Q3 smoothing worldview.
- It also directly weakens the use of ordinary OOF smoothing invariance as a hard veto: E248 rejected the train analogue, but public rewarded the test-side smoothing rule.
- The unresolved attribution is E224 body versus E247 smoothing. E247 proves the combined E224-body + feature-NN1 Q3 rollback branch, not the isolated rollback effect.

## Follow-Up Family Ranking

| candidate_id | role | pruned_cells | e237_like_score | expected_loss_vs_e224 | adverse_reduction_vs_e224 | support_gain_vs_e224 | q3_top1_over_abs_expected | overlap_e247 | jaccard_e247 | symmetric_diff_vs_e247 | overlap_e237 | overlap_e230_swing25 | information_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| top50_amp_then_smooth25 | amplitude_constrained_smoothing_sensor | 25 | 0.068441797 | -0.000047418 | 0.000615602 | 0.003037928 | 0.615425803 | 21 | 0.552631579 | 17 | 14 | 14 | 0.077389165 |
| source_smooth_top25 | source_pair_mechanism_sensor | 25 | 0.063611509 | -0.000059824 | 0.000546458 | 0.007379409 | 0.571087980 | 21 | 0.552631579 | 17 | 13 | 11 | 0.072558877 |
| nn_smooth_mean_top25 | same_family_variant | 25 | 0.065029568 | -0.000064576 | 0.000555825 | 0.005080235 | 0.555749811 | 24 | 0.685714286 | 11 | 13 | 10 | 0.071315282 |
| amp_smooth_mean_top25 | same_family_variant | 25 | 0.063123833 | -0.000038519 | 0.000573783 | 0.004411129 | 0.651720804 | 23 | 0.638888889 | 13 | 14 | 12 | 0.070346056 |
| nn_amp_smooth_top25 | same_family_variant | 25 | 0.064791510 | -0.000067371 | 0.000548616 | 0.006223698 | 0.547106580 | 25 | 0.735294118 | 9 | 13 | 10 | 0.070085628 |
| nn_smooth_sum_top25 | breadth_ablation_same_score_axis | 25 | 0.062715798 | -0.000071315 | 0.000521959 | 0.006697792 | 0.535362090 | 25 | 0.735294118 | 9 | 10 | 10 | 0.068009916 |
| nn_smooth_mean_top21 | same_family_variant | 21 | 0.060211814 | -0.000068286 | 0.000502431 | 0.005107963 | 0.544335733 | 21 | 0.617647059 | 13 | 13 | 10 | 0.067858872 |
| nn_amp_smooth_top21 | same_family_variant | 21 | 0.059905878 | -0.000072640 | 0.000492133 | 0.006537654 | 0.531527856 | 21 | 0.617647059 | 13 | 11 | 10 | 0.067552937 |
| nn_smooth_sum_top21 | same_family_variant | 21 | 0.053376656 | -0.000062743 | 0.000440002 | 0.007404427 | 0.561565653 | 21 | 0.617647059 | 13 | 8 | 10 | 0.061023715 |
| nn_smooth_mean_top13 | same_family_variant | 13 | 0.044197693 | -0.000062798 | 0.000348553 | 0.006882450 | 0.561389614 | 13 | 0.382352941 | 21 | 8 | 10 | 0.056550634 |
| incoming_smooth_top25 | incoming_pair_mechanism_sensor | 25 | 0.044188976 | -0.000044640 | 0.000378591 | 0.001003359 | 0.626315550 | 19 | 0.475000000 | 21 | 2 | 4 | 0.054688976 |
| smooth_dist_top25 | same_family_variant | 25 | 0.047117772 | -0.000038357 | 0.000414284 | 0.003991877 | 0.652420338 | 23 | 0.638888889 | 13 | 5 | 6 | 0.054339994 |
| nn_amp_smooth_top13 | same_family_variant | 13 | 0.040553871 | -0.000049028 | 0.000332014 | 0.006106905 | 0.609286488 | 13 | 0.382352941 | 21 | 7 | 9 | 0.052906812 |
| nn_smooth_sum_top13 | same_family_variant | 13 | 0.036659752 | -0.000045794 | 0.000296990 | 0.006870126 | 0.621746227 | 13 | 0.382352941 | 21 | 5 | 6 | 0.049012693 |
| nn_smooth_sum_top10 | same_family_variant | 10 | 0.032711872 | -0.000045253 | 0.000258946 | 0.006023985 | 0.623880118 | 10 | 0.294117647 | 24 | 5 | 6 | 0.046829519 |
| nn_smooth_sum_top34 | submitted_winner | 34 | 0.073034939 | -0.000066519 | 0.000632592 | 0.005788959 | 0.549713494 | 34 | 1.000000000 | 0 | 13 | 10 |  |
| control_e230_swing25 | reference_or_negative_control | 25 | 0.060843558 | 0.000023308 | 0.000633168 | 0.009873471 | 0.490395991 | 10 | 0.204081633 | 39 | 13 | 25 |  |
| control_e237_learned_cell25 | reference_or_negative_control | 25 | 0.058941606 | -0.000005612 | 0.000576400 | 0.006450259 | 0.747139811 | 13 | 0.282608696 | 33 | 25 | 13 |  |
| control_e230_risk21 | reference_or_negative_control | 21 | 0.055664125 | -0.000067892 | 0.000444730 | 0.021076971 | 0.469524979 | 7 | 0.145833333 | 41 | 11 | 11 |  |

## Decision

- Promote feature-NN1 smoothing from `public sensor` to `current public-positive JEPA mechanism`.
- Do not treat E248 as a failed experiment to ignore. It explains the bottleneck: train OOF harmful-row labels and public test-side feature-neighbor geometry are misaligned.
- Do not immediately sweep every E247 sibling. The best next information candidate inside this family is `top50_amp_then_smooth25`, because it asks whether public liked broad smoothness or only high-amplitude smoothing cells.
- If the next goal is attribution rather than score, submit/observe E224 clean body. If the next goal is score-plus-information, materialize `top50_amp_then_smooth25` as the first E247-family follow-up.
- The next modeling target should be a public-contrastive JEPA head: learn the difference between OOF-adverse smoothing labels and public-positive feature-neighbor cells.
