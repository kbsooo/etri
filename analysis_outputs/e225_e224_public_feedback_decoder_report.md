# E225 E224 Public Feedback Decoder

## Question

Before E224 is submitted, how should its future public LB be decoded without post-hoc q3-scale tuning?

## Locked Candidate

- candidate: `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`
- current public frontier: `0.5762913298` from `submission_e95_hardtail_541e3973.csv`
- E101 public reference: `0.5763003660`
- mixmin public reference: `0.5763066405`
- bad JEPA reference E216: `0.5772865088`

## E224 Metrics

| candidate_id | pair_kind | q3_scale | s4_mode | anchor | local_delta | geometry_delta | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected | q3_top1_over_abs_expected | submission_file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e224_q3s0p625_s4closer_e154_a0p5 | graft_vs_anchor | 0.625000000 | closer | e154 | -0.001098893 | -0.000505582 | -0.000623352 | 0.003400775 | 0.465984132 | 0.157757659 | 0.875120489 | submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv |
| e224_q3s0p625_s4closer_e154_a0p5 | actual_vs_e95 | 0.625000000 | closer | e154 | -0.001098893 | -0.000505582 | -0.000653189 | 0.004094069 | 0.465789507 | 0.150551319 | 0.875120489 | submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv |

## Routebook

| outcome | public_lb_lo_exclusive | public_lb_hi_inclusive | world_update_class | next_action | candidate_to_test |
| --- | --- | --- | --- | --- | --- |
| capped_jepa_breakthrough | -inf | 0.576261330 | strong_support | Do not immediately increase Q3. First decompose the win into S4 body, Q3 residual, and E154 inherited body using an E224-vs-E95-anchor attribution audit. | conditional:e224_component_decomposition_or_e224_e95_anchor |
| clean_win | 0.576261330 | 0.576276019 | support | Promote E224 as the JEPA-family anchor. Use the E224 E95-anchor sibling only if the next public slot is a clean attribution sensor. | analysis_outputs/submission_e224_e224_q3s0p625_s4toward_e95_a0p5_9c52abe2.csv |
| micro_win | 0.576276019 | 0.576288330 | weak_support | Keep E224 as the preferred JEPA sensor, but do not submit a sibling until an exact-score attribution audit identifies whether Q3 or S4 carried the win. | conditional:e224_exact_score_attribution |
| tie | 0.576288330 | 0.576294330 | underresolved | Keep E95 practical. Treat E224 as an unresolved diagnostic and run a target/component attribution audit before any JEPA sibling. |  |
| small_loss | 0.576294330 | 0.576300366 | weak_rejection | Do not submit another amplitude sibling. Audit whether E154 inherited body or E224 Q3/S4 residual caused the loss, then decide between E154 branch and new JEPA target design. | conditional:e224_loss_attribution_then_e154_or_new_jepa |
| mixmin_safe_loss | 0.576300366 | 0.576306641 | rejection | Demote E211/E223/E224 as expected-score followups. Keep JEPA axes as diagnostics and move to a new representation or support-tail target. | conditional:new_jepa_support_tail_objective |
| branch_loss | 0.576306641 | 0.576341330 | strong_rejection | Close current E211-family expected-score lane. Search for non-collinear hidden structure or build a JEPA objective with support/tail regularization baked in. | conditional:non_collinear_search_or_support_regularized_jepa |
| hard_fail | 0.576341330 | 0.576591330 | hard_rejection | Keep E208/E211 axes only as diagnostics. Rebuild target representation or return to block/sequence hidden-world search. |  |
| e216_like_fail | 0.576591330 | inf | translator_collapse | Do a root-cause miss anatomy like E219 before any further JEPA submission. Treat current JEPA probability movement as unsafe. | conditional:e224_public_miss_anatomy |

## Example Scores

| score | outcome | world_update_class | delta_vs_e95 | next_action | candidate_to_test |
| --- | --- | --- | --- | --- | --- |
| 0.576251330 | capped_jepa_breakthrough | strong_support | -0.000040000 | Do not immediately increase Q3. First decompose the win into S4 body, Q3 residual, and E154 inherited body using an E224-vs-E95-anchor attribution audit. | conditional:e224_component_decomposition_or_e224_e95_anchor |
| 0.576271330 | clean_win | support | -0.000020000 | Promote E224 as the JEPA-family anchor. Use the E224 E95-anchor sibling only if the next public slot is a clean attribution sensor. | analysis_outputs/submission_e224_e224_q3s0p625_s4toward_e95_a0p5_9c52abe2.csv |
| 0.576283330 | micro_win | weak_support | -0.000008000 | Keep E224 as the preferred JEPA sensor, but do not submit a sibling until an exact-score attribution audit identifies whether Q3 or S4 carried the win. | conditional:e224_exact_score_attribution |
| 0.576291330 | tie | underresolved | 0.000000000 | Keep E95 practical. Treat E224 as an unresolved diagnostic and run a target/component attribution audit before any JEPA sibling. |  |
| 0.576300366 | small_loss | weak_rejection | 0.000009036 | Do not submit another amplitude sibling. Audit whether E154 inherited body or E224 Q3/S4 residual caused the loss, then decide between E154 branch and new JEPA target design. | conditional:e224_loss_attribution_then_e154_or_new_jepa |
| 0.576306641 | mixmin_safe_loss | rejection | 0.000015311 | Demote E211/E223/E224 as expected-score followups. Keep JEPA axes as diagnostics and move to a new representation or support-tail target. | conditional:new_jepa_support_tail_objective |
| 0.576316330 | branch_loss | strong_rejection | 0.000025000 | Close current E211-family expected-score lane. Search for non-collinear hidden structure or build a JEPA objective with support/tail regularization baked in. | conditional:non_collinear_search_or_support_regularized_jepa |
| 0.576391330 | hard_fail | hard_rejection | 0.000100000 | Keep E208/E211 axes only as diagnostics. Rebuild target representation or return to block/sequence hidden-world search. |  |
| 0.577286509 | e216_like_fail | translator_collapse | 0.000995179 | Do a root-cause miss anatomy like E219 before any further JEPA submission. Treat current JEPA probability movement as unsafe. | conditional:e224_public_miss_anatomy |

## Movement Anatomy

| pair | moved_cells | moved_rows | mean_abs_logit_delta | max_abs_logit_delta | top1_share | target_abs_share | cosine_vs_e154_from_e95 | cosine_vs_e211_full_e154_from_e95 | cosine_vs_e223_q3s0p75_e154_from_e95 | cosine_vs_e216_s2_miss_from_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e224_q3s0p625_e154_vs_e95 | 534 | 250 | 0.010191854 | 0.172092355 | 0.009648734 | Q3:0.533416;S4:0.363619;Q1:0.046219;S3:0.030179;S2:0.026567;S1:0.000000;Q2:0.000000 | 0.316350240 | 0.975464053 | 0.996077734 | 0.043542250 |
| e224_q3s0p625_e154_vs_e154 | 355 | 250 | 0.008635758 | 0.172092355 | 0.011387360 | Q3:0.591856;S4:0.408144;Q1:0.000000;S3:0.000000;Q2:0.000000;S1:0.000000;S2:0.000000 | 0.316350240 | 0.975464053 | 0.996077734 | 0.043542250 |
| e224_q3s0p625_e154_vs_e223_q3s0p75_e154 | 250 | 250 | 0.001022226 | 0.034418471 | 0.019240071 | Q3:1.000000;Q1:0.000000;Q2:0.000000;S1:0.000000;S2:0.000000;S3:0.000000;S4:0.000000 | 0.316350240 | 0.975464053 | 0.996077734 | 0.043542250 |
| e224_q3s0p625_e154_vs_e211_full_e154 | 250 | 250 | 0.003066678 | 0.103255413 | 0.019240071 | Q3:1.000000;Q1:0.000000;Q2:0.000000;S1:0.000000;S2:0.000000;S3:0.000000;S4:0.000000 | 0.316350240 | 0.975464053 | 0.996077734 | 0.043542250 |
| e224_q3s0p625_e154_vs_e216_s2_miss | 605 | 250 | 0.022006074 | 0.229949291 | 0.005971060 | S2:0.607574;Q3:0.232260;S4:0.160166;Q1:0.000000;Q2:0.000000;S1:0.000000;S3:0.000000 | 0.316350240 | 0.975464053 | 0.996077734 | 0.043542250 |
| e224_q3s0p625_e95_vs_e95 | 358 | 250 | 0.008752556 | 0.172092355 | 0.011235402 | Q3:0.583958;S4:0.416042;S1:0.000000;Q1:0.000000;S2:0.000000;S3:0.000000;Q2:0.000000 | 0.086311413 | 0.953782885 | 0.966619324 | 0.012461027 |
| e223_q3s0p75_e154_vs_e95 | 534 | 250 | 0.011188463 | 0.206510826 | 0.010547131 | Q3:0.574977;S4:0.331230;Q1:0.042102;S3:0.027491;S2:0.024200;S1:0.000000;Q2:0.000000 | 0.295604631 | 0.991118215 | 1.000000000 | 0.040747266 |
| e211_full_e154_vs_e95 | 534 | 250 | 0.013194288 | 0.275347768 | 0.011924977 | Q3:0.639590;S4:0.280876;Q1:0.035702;S3:0.023312;S2:0.020521;S1:0.000000;Q2:0.000000 | 0.260057176 | 1.000000000 | 0.991118215 | 0.035944464 |
| e216_s2_miss_vs_e95 | 505 | 250 | 0.015109305 | 0.249981125 | 0.009454198 | S2:0.884384;Q3:0.047569;Q1:0.031177;S3:0.020357;S4:0.016514;S1:0.000000;Q2:0.000000 | 0.135253079 | 0.035944464 | 0.040747266 | 1.000000000 |

## Target Anatomy

| pair | target | moved_cells | abs_logit_sum | abs_logit_share | mean_signed_logit_delta | max_abs_logit_delta |
| --- | --- | --- | --- | --- | --- | --- |
| e224_q3s0p625_e154_vs_e211_full_e154 | Q3 | 250 | 5.366685683 | 1.000000000 | 0.006900359 | 0.103255413 |
| e224_q3s0p625_e154_vs_e211_full_e154 | Q1 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e224_q3s0p625_e154_vs_e211_full_e154 | Q2 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e224_q3s0p625_e154_vs_e211_full_e154 | S1 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e224_q3s0p625_e154_vs_e211_full_e154 | S2 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e224_q3s0p625_e154_vs_e211_full_e154 | S3 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e224_q3s0p625_e154_vs_e211_full_e154 | S4 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e224_q3s0p625_e154_vs_e223_q3s0p75_e154 | Q3 | 250 | 1.788895228 | 1.000000000 | 0.002300120 | 0.034418471 |
| e224_q3s0p625_e154_vs_e223_q3s0p75_e154 | Q1 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e224_q3s0p625_e154_vs_e223_q3s0p75_e154 | Q2 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e224_q3s0p625_e154_vs_e223_q3s0p75_e154 | S1 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e224_q3s0p625_e154_vs_e223_q3s0p75_e154 | S2 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e224_q3s0p625_e154_vs_e223_q3s0p75_e154 | S3 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e224_q3s0p625_e154_vs_e223_q3s0p75_e154 | S4 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e224_q3s0p625_e154_vs_e95 | Q3 | 250 | 9.513875533 | 0.533416245 | -0.012707394 | 0.172092355 |
| e224_q3s0p625_e154_vs_e95 | S4 | 119 | 6.485419561 | 0.363619236 | 0.003149099 | 0.169294968 |
| e224_q3s0p625_e154_vs_e95 | Q1 | 70 | 0.824348264 | 0.046218889 | 0.001680756 | 0.023459002 |
| e224_q3s0p625_e154_vs_e95 | S3 | 56 | 0.538264500 | 0.030178977 | -0.001248791 | 0.022007768 |
| e224_q3s0p625_e154_vs_e95 | S2 | 39 | 0.473836036 | 0.026566654 | 0.000285552 | 0.021358850 |
| e224_q3s0p625_e154_vs_e95 | S1 | 0 | 0.000000000 | 0.000000000 | -0.000000000 | 0.000000000 |
| e224_q3s0p625_e154_vs_e95 | Q2 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |

## Decision Rules

- A win strengthens capped-Q3/S4-body translation; it does not justify raising Q3 to `0.75` or `1.0`.
- A tie or small loss requires exact attribution before any sibling. Do not tune q3_scale from one scalar score.
- A loss worse than mixmin demotes the current E211 probability translator. Keep JEPA axes as diagnostics and rebuild the support/tail target.
- An E216-like miss triggers a miss-anatomy audit before any further JEPA submission.

## Outputs

- routebook: `analysis_outputs/e225_e224_public_feedback_decoder_routebook.csv`
- examples: `analysis_outputs/e225_e224_public_feedback_decoder_examples.csv`
- pairwise anatomy: `analysis_outputs/e225_e224_public_feedback_decoder_pairwise.csv`
- target anatomy: `analysis_outputs/e225_e224_public_feedback_decoder_target_anatomy.csv`
