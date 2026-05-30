# E222 E211 Support/Tail Audit

## Question

After E216 failed publicly, does the live E211 Q3/S4 JEPA movement show the same low-support hard-label tail pattern?

## Live Graft vs Anchor

| candidate_id | pair_kind | base_file | moved_cells | targets_moved | expected_focus | adverse_delta | adverse_over_e216_miss | support_prob_focus_swing_weighted | top1_over_abs_expected | cells_to_flip_expected_focus | support_tail_gate | e222_decision | e222_tail_survival_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e211_e154_closer | graft_vs_anchor | submission_e154_s3repair_9f2e2e73.csv | 355 | Q3,S4 | -0.000655277 | 0.004765654 | 4.788740409 | 0.463231022 | 0.240114517 | 5 | False | expected_good_but_low_support | 0.657529089 |
| e211_e95_toward | graft_vs_anchor | submission_e95_hardtail_541e3973.csv | 358 | Q3,S4 | -0.000654330 | 0.004824911 | 4.848284981 | 0.463586825 | 0.240462280 | 5 | False | expected_good_but_low_support | 0.656622797 |
| e211_e95_closer | graft_vs_anchor | submission_e95_hardtail_541e3973.csv | 354 | Q3,S4 | -0.000647387 | 0.004753401 | 4.776427985 | 0.463062456 | 0.243040999 | 5 | False | expected_good_but_low_support | 0.649611269 |

## Live Actual vs E95

| candidate_id | pair_kind | base_file | moved_cells | targets_moved | expected_focus | adverse_delta | adverse_over_e216_miss | support_prob_focus_swing_weighted | top1_over_abs_expected | cells_to_flip_expected_focus | support_tail_gate | e222_decision | e222_tail_survival_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e211_e154_closer | actual_vs_e95 | submission_e95_hardtail_541e3973.csv | 534 | Q1,Q3,S2,S3,S4 | -0.000685115 | 0.005426827 | 5.453116534 | 0.463226350 | 0.229657247 | 5 | False | expected_good_but_low_support | 0.687033524 |
| e211_e95_toward | actual_vs_e95 | submission_e95_hardtail_541e3973.csv | 358 | Q3,S4 | -0.000654330 | 0.004824911 | 4.848284981 | 0.463586825 | 0.240462280 | 5 | False | expected_good_but_low_support | 0.656622797 |
| e211_e95_closer | actual_vs_e95 | submission_e95_hardtail_541e3973.csv | 354 | Q3,S4 | -0.000647387 | 0.004753401 | 4.776427985 | 0.463062456 | 0.243040999 | 5 | False | expected_good_but_low_support | 0.649611269 |

## Negative Controls

| candidate_id | pair_kind | base_file | moved_cells | targets_moved | expected_focus | adverse_delta | adverse_over_e216_miss | support_prob_focus_swing_weighted | top1_over_abs_expected | cells_to_flip_expected_focus | support_tail_gate | e222_decision | e222_tail_survival_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e216_e154_s2_negative | actual_vs_e95 | submission_e95_hardtail_541e3973.csv | 505 | Q1,Q3,S2,S3,S4 | -0.000318150 | 0.006833222 | 6.866324624 | 0.473309107 | 0.448991031 | 3 | False | expected_good_but_low_support | 0.319398529 |
| e216_e95_s2_negative | actual_vs_e95 | submission_e95_hardtail_541e3973.csv | 250 | S2 | -0.000287798 | 0.006048995 | 6.078297978 | 0.473944871 | 0.456568722 | 3 | False | expected_good_but_low_support | 0.289416516 |
| e216_e154_s2_negative | graft_vs_anchor | submission_e154_s3repair_9f2e2e73.csv | 250 | S2 | -0.000288312 | 0.006048480 | 6.077781421 | 0.473944871 | 0.455754650 | 3 | False | expected_good_but_low_support | 0.289947122 |
| e216_e95_s2_negative | graft_vs_anchor | submission_e95_hardtail_541e3973.csv | 250 | S2 | -0.000287798 | 0.006048995 | 6.078297978 | 0.473944871 | 0.456568722 | 3 | False | expected_good_but_low_support | 0.289416516 |

## Target Breakdown For Live Grafts

| candidate_id | pair_kind | target | moved_cells | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected | support_tail_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e211_e154_closer | graft_vs_anchor | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 | False |
| e211_e154_closer | graft_vs_anchor | Q3 | 250 | -0.000144297 | 0.003580516 | 0.455478271 | 1.090400695 | False |
| e211_e95_closer | graft_vs_anchor | S4 | 104 | -0.000500095 | 0.001175880 | 0.480857314 | 0.168985725 | False |
| e211_e95_closer | graft_vs_anchor | Q3 | 250 | -0.000147292 | 0.003577521 | 0.455478271 | 1.068226753 | False |
| e211_e95_toward | graft_vs_anchor | S4 | 108 | -0.000507037 | 0.001247390 | 0.481796770 | 0.166671896 | False |
| e211_e95_toward | graft_vs_anchor | Q3 | 250 | -0.000147292 | 0.003577521 | 0.455478271 | 1.068226753 | False |

## Top Swing Cells

| candidate_id | pair_kind | target | row_idx | subject_id | p_base | p_new | logit_delta | swing | expected_focus | support_prob_focus |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e210_e95_dependency_gate | actual_vs_e95 | Q3 | 140 | id06 | 0.802114677 | 0.728404411 | -0.413021651 | 0.000236012 | -0.000039322 | 0.400000000 |
| e210_e95_dependency_gate | graft_vs_anchor | Q3 | 140 | id06 | 0.802114677 | 0.728404411 | -0.413021651 | 0.000236012 | -0.000039322 | 0.400000000 |
| e210_e95_dependency_gate | graft_vs_anchor | Q3 | 188 | id08 | 0.336274855 | 0.419589593 | 0.355480903 | 0.000203132 | -0.000051761 | 0.632142857 |
| e210_e95_dependency_gate | actual_vs_e95 | Q3 | 188 | id08 | 0.336274855 | 0.419589593 | 0.355480903 | 0.000203132 | -0.000051761 | 0.632142857 |
| e210_e95_dependency_gate | graft_vs_anchor | Q3 | 195 | id08 | 0.221899903 | 0.282450659 | 0.322290948 | 0.000184166 | -0.000064206 | 0.600000000 |
| e210_e95_dependency_gate | actual_vs_e95 | Q3 | 195 | id08 | 0.221899903 | 0.282450659 | 0.322290948 | 0.000184166 | -0.000064206 | 0.600000000 |
| e210_e95_dependency_gate | graft_vs_anchor | Q3 | 150 | id06 | 0.734463629 | 0.668961212 | -0.313898127 | 0.000179370 | -0.000018368 | 0.400000000 |
| e210_e95_dependency_gate | actual_vs_e95 | Q3 | 150 | id06 | 0.734463629 | 0.668961212 | -0.313898127 | 0.000179370 | -0.000018368 | 0.400000000 |
| e210_e95_dependency_gate | graft_vs_anchor | Q3 | 235 | id10 | 0.705286628 | 0.638272181 | -0.304728262 | 0.000174130 | -0.000012601 | 0.400000000 |
| e210_e95_dependency_gate | actual_vs_e95 | Q3 | 235 | id10 | 0.705286628 | 0.638272181 | -0.304728262 | 0.000174130 | -0.000012601 | 0.400000000 |
| e211_e95_toward | actual_vs_e95 | Q3 | 140 | id06 | 0.802114677 | 0.754769928 | -0.275347768 | 0.000157342 | -0.000028172 | 0.400000000 |
| e211_e154_closer | graft_vs_anchor | Q3 | 140 | id06 | 0.802114677 | 0.754769928 | -0.275347768 | 0.000157342 | -0.000028172 | 0.400000000 |
| e211_e95_toward | graft_vs_anchor | Q3 | 140 | id06 | 0.802114677 | 0.754769928 | -0.275347768 | 0.000157342 | -0.000028172 | 0.400000000 |
| e211_e95_closer | graft_vs_anchor | Q3 | 140 | id06 | 0.802114677 | 0.754769928 | -0.275347768 | 0.000157342 | -0.000028172 | 0.400000000 |
| e211_e95_closer | actual_vs_e95 | Q3 | 140 | id06 | 0.802114677 | 0.754769928 | -0.275347768 | 0.000157342 | -0.000028172 | 0.400000000 |
| e211_e154_closer | actual_vs_e95 | Q3 | 140 | id06 | 0.802114677 | 0.754769928 | -0.275347768 | 0.000157342 | -0.000028172 | 0.400000000 |
| e211_e154_closer | actual_vs_e95 | Q3 | 223 | id09 | 0.513260380 | 0.447048682 | -0.265656427 | 0.000151804 | 0.000022707 | 0.370325203 |
| e211_e95_toward | actual_vs_e95 | Q3 | 223 | id09 | 0.513260380 | 0.447634130 | -0.263288369 | 0.000150450 | 0.000022460 | 0.370325203 |
| e211_e95_closer | actual_vs_e95 | Q3 | 223 | id09 | 0.513260380 | 0.447634130 | -0.263288369 | 0.000150450 | 0.000022460 | 0.370325203 |
| e211_e154_closer | graft_vs_anchor | Q3 | 223 | id09 | 0.512668763 | 0.447048682 | -0.263288369 | 0.000150450 | 0.000022549 | 0.370325203 |

## Decision

- Best live graft by E222 tail score: `e211_e154_closer` with expected focus `-0.000655277`, support probability `0.463231`, and decision `expected_good_but_low_support`.
- E211 is not automatically cleared by the E216 lesson: the live Q3/S4 grafts still have sub-0.5 swing-weighted support under focus priors, so public feedback should be read as a tail-support sensor rather than a safe improvement claim.
