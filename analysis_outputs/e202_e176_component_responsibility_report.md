# E202 E176 Component Responsibility Router

## Question

If E176's public score arrives, which hidden component should be credited or blamed before creating any follow-up file?

## Result

E176 should not be read as a Q2-only experiment. The name is misleading at component level.

- S-target group carries `0.651098` of focus-prior expected movement versus `0.348902` for Q targets.
- Between-train-runs rows carry `0.807772` of the expected movement.
- Q2 is the largest raw probability movement share (`0.209702`) but only `0.121416` of expected focus contribution.
- The top33 hard-label cells remain weakly visible: target-matched visible-support `p_low=0.014667`.

Therefore a good E176 score mainly supports the broad S-stage / between-train-runs body with Q2 damping as a guard. A weak or bad score mainly says the hard-label tail/cancellation layer was unresolved; it should not trigger Q2 keep-factor tuning.

## Target Components

| target | q_or_s | n_cells | expected_delta_focus_mean | expected_abs_share | prob_abs_delta_share | expected_rank | abs_movement_rank | support_swing_weighted_visible_mean | e72_active_rate | mean_safe_density | role_read |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | S | 168 | -2.51104068262e-05 | 0.20351472515 | 0.126307006829 | 1 | 6 | 0.216502660804 | 0.0535714285714 | 0.178804234887 | primary_s_stage_body |
| S1 | S | 95 | -2.34033150104e-05 | 0.189679094206 | 0.118164461974 | 2 | 7 | 0.26751709105 | 0.536842105263 | 0.455104170008 | primary_s_stage_body |
| S4 | S | 116 | -1.81356089189e-05 | 0.146985410874 | 0.145284965046 | 3 | 2 | 0.434874933607 | 0.344827586207 | 0.43511440511 | primary_s_stage_body |
| Q1 | Q | 121 | -1.79638409665e-05 | 0.145593266658 | 0.128746156183 | 4 | 5 | 0.406551508984 | 0.388429752066 | 0.433137832989 | secondary_body_component |
| Q2 | Q | 165 | -1.49807504933e-05 | 0.121415926882 | 0.209701511912 | 5 | 1 | 0.459311935665 | 0.00606060606061 | 0.184092629883 | name_mismatch_large_movement_mid_expected_gain |
| S2 | S | 122 | -1.36855697141e-05 | 0.110918750865 | 0.130103099609 | 6 | 4 | 0.346102357093 | 0.393442622951 | 0.45301461327 | secondary_body_component |
| Q3 | Q | 117 | -1.0104242627e-05 | 0.0818928253654 | 0.141692798447 | 7 | 3 | 0.556798444678 | 0.401709401709 | 0.436922677715 | visible_supported_low_expected_share |

## Subject Concentration

| subject_id | n_cells | n_rows | swing_share | expected_delta_focus_sum | top33_cells | top8_cells | between_train_runs_rate | e72_active_rate | support_visible_swing_weighted | top_target_by_swing | top_target_swing_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id07 | 98 | 19 | 0.160857467709 | -8.87930620329e-06 | 5 | 0 | 0.84693877551 | 0.295918367347 | 0.345498017875 | S1 | 0.226011448761 |
| id06 | 83 | 22 | 0.152250558805 | -1.40731248915e-05 | 10 | 3 | 0.843373493976 | 0.361445783133 | 0.162791875997 | S3 | 0.331280709491 |
| id04 | 126 | 27 | 0.099560959341 | -6.67821639062e-06 | 0 | 0 | 0.912698412698 | 0.253968253968 | 0.547853826567 | Q2 | 0.349082360861 |
| id05 | 107 | 20 | 0.0931251250036 | -9.74611536991e-06 | 1 | 0 | 0.803738317757 | 0.299065420561 | 0.471644802375 | Q2 | 0.265803768849 |
| id03 | 72 | 15 | 0.0928174374676 | -1.12510659754e-05 | 7 | 1 | 0.680555555556 | 0.194444444444 | 0.320389872105 | S4 | 0.406912800903 |
| id02 | 98 | 20 | 0.0875789843642 | -5.19707878288e-06 | 1 | 0 | 0.826530612245 | 0.224489795918 | 0.365614144727 | Q3 | 0.299913288177 |
| id09 | 89 | 18 | 0.0861224939685 | -4.5033079634e-06 | 2 | 0 | 0.786516853933 | 0.303370786517 | 0.352127859542 | S2 | 0.283076370602 |
| id01 | 77 | 18 | 0.0820051107784 | -5.39487891362e-06 | 2 | 0 | 0.805194805195 | 0.25974025974 | 0.399089134998 | S3 | 0.363227836205 |
| id08 | 84 | 19 | 0.0801050275641 | -7.91973769748e-06 | 5 | 4 | 0.880952380952 | 0.261904761905 | 0.454404541152 | Q3 | 0.358391940553 |
| id10 | 70 | 15 | 0.0655768349982 | -4.39912273673e-06 | 0 | 0 | 0.728571428571 | 0.214285714286 | 0.512133069821 | S2 | 0.274574208272 |

## Outcome Component Router

| outcome | public_lb_lo_exclusive | public_lb_hi_inclusive | component_interpretation | next_component_probe | do_not_infer |
| --- | --- | --- | --- | --- | --- |
| q2_underopen_breakthrough | -inf | 0.5762613298 | Credit broad S-stage/between-train-runs body first; Q2 damping is a secondary guard, not the whole explanation. | Decompose S3/S1/S4 body and then test Q2 amplitude only as a paired contrast. | Do not infer Q2-only causality from the scalar score. |
| clean_win | 0.5762613298 | 0.5762760191 | Treat E176 as a broad-body anchor; the win supports Q/S asymmetry but does not prove Q2 keep=0.75 is optimal. | Run component responsibility audit before E174 or another sibling. | Do not infer Q2-only causality from the scalar score. |
| micro_win | 0.5762760191 | 0.5762883298 | The sign is right but hard-label resolution is still thin; body and tail probably nearly cancel. | Only E174-vs-E176 is coherent if deliberately asking the Q2 amplitude question. | Do not infer Q2-only causality from the scalar score. |
| tie | 0.5762883298 | 0.5762943298 | The broad body exists but top critical cells are underresolved; the top33 visible support p_low is the warning. | Use E172 only as same-family safety; no Q2 keep sweep. | Do not infer Q2-only causality from the scalar score. |
| small_loss | 0.5762943298 | 0.576300366 | Read as tail/cancellation failure, not as proof that Q2 alone is wrong. | E172 if testing same-family safety; otherwise E154. | Do not infer Q2-only causality from the scalar score. |
| e101_worse_mixmin_safe | 0.576300366 | 0.5763066405 | Partial-reopen is public-misaligned despite Q2 damping. | Demote E176/E174; prefer E154 repaired-branch counter-world. | Do not infer Q2-only causality from the scalar score. |
| branch_loss | 0.5763066405 | 0.5763413298 | The broad partial-reopen body gives back the frontier edge. | Close same-family expected-score followups and use E154/search. | Do not infer Q2-only causality from the scalar score. |
| hard_fail | 0.5763413298 | inf | Dominant negative axis is outside this component family. | Return to non-collinear latent/hidden-block search. | Do not infer Q2-only causality from the scalar score. |

## Decision

No submission is created. E202 is a pre-public interpretation guard layered on top of E201. If E176 wins, start by decomposing S3/S1/S4 and between-train-runs body. If it ties or loses, read the result through hard-tail/cancellation and the E201 route table before any E172/E154/E174 choice.
