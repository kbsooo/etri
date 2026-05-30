# E238 E237 Public Feedback Decoder

## Question

If the E237 learned cell-level JEPA Q3-tail candidate is submitted, how should its public LB be read without post-hoc top-k or sibling tuning?

## Locked Candidate

- candidate: `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`
- current public frontier: `0.5762913298` from `submission_e95_hardtail_541e3973.csv`
- E101 reference: `0.5763003660`
- mixmin reference: `0.5763066405`
- bad JEPA reference E216: `0.5772865088`

## Candidate Metrics

| candidate | role | expected_loss_vs_e224 | adverse_reduction_vs_e224 | support_gain_vs_e224 | actual_adverse_reduction_vs_e224 | q3_top1_over_abs_expected | q3_cells_changed_vs_e224 | e230_q3_risk_top21_overlap | submission_file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e224_clean | clean_unpruned_jepa | 0.000000000 | 0.000000000 | 0.000000000 |  | 0.875120489 | 0 |  | submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv |
| e230_q3_swingtop25_drop | hand_q3_prune | 0.000023308 | 0.000633168 | 0.009873471 |  | 0.490395991 | 25 |  | submission_e230_q3_swingtop25_drop_e0918606.csv |
| e230_q3_risktop21_drop | hand_q3_prune | -0.000067892 | 0.000444730 | 0.021076971 |  | 0.469524979 | 21 |  | submission_e230_q3_risktop21_drop_7d95c14a.csv |
| e230_q3_risktop13_drop | hand_q3_prune | -0.000051180 | 0.000326867 | 0.014719432 |  | 0.517502818 | 13 |  | submission_e230_q3_risktop13_drop_9704f7c9.csv |
| e237_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25 | learned_cell_q3_prune | -0.000005612 | 0.000576400 | 0.006450259 | 0.000553281 | 0.747139811 | 25 | 11.000000000 | submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv |
| e237_all3_latent_with_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top13 | learned_cell_q3_prune | -0.000002012 | 0.000320210 | 0.006005051 | 0.000318614 | 0.770654346 | 13 | 8.000000000 | submission_e237_cell_decisive_all3_latent_with_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top13_ef0a90e1.csv |
| e237_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_p05 | learned_cell_q3_prune | 0.000001833 | 0.000305494 | 0.005360060 | 0.000303898 | 0.797460985 | 12 | 7.000000000 | submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_p05_3f356850.csv |
| e237_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top10 | learned_cell_q3_prune | -0.000009860 | 0.000264407 | 0.003705431 | 0.000262811 | 0.804528302 | 10 | 5.000000000 | submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top10_290b1835.csv |
| e237_all3_latent_no_targetid_hgb_shallow_row5_risk_q0p10_drop_q3_top10 | learned_cell_q3_prune | -0.000009860 | 0.000264407 | 0.003705431 | 0.000262811 | 0.804528302 | 10 | 5.000000000 | submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_row5_risk_q0p10_drop_q3_top10_290b1835.csv |
| e237_all3_latent_with_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top10 | learned_cell_q3_prune | 0.000008794 | 0.000262078 | 0.005867017 | 0.000262078 | 0.851055535 | 10 | 7.000000000 | submission_e237_cell_decisive_all3_latent_with_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top10_4f11397a.csv |
| e237_all3_latent_with_targetid_hgb_shallow_subject5_risk_q0p20_drop_q3_top10 | learned_cell_q3_prune | -0.000005414 | 0.000237356 | 0.005859231 | 0.000237356 | 0.834896764 | 10 | 6.000000000 | submission_e237_cell_decisive_all3_latent_with_targetid_hgb_shallow_subject5_risk_q0p20_drop_q3_top10_1abccfd1.csv |

## Public Routebook

| outcome | public_lb_lo_exclusive | public_lb_hi_inclusive | world_update_class | next_action | candidate_to_test |
| --- | --- | --- | --- | --- | --- |
| cell_tail_breakthrough | -inf | 0.576261330 | strong_support | Do not tune a lower-ranked E237 sibling. First compare against E224 if available, then audit which Q3 cells carried the gain. | conditional:e237_component_attribution_or_e224_contrast |
| clean_win | 0.576261330 | 0.576276019 | support | Promote E237 as the learned-Q3-tail anchor. Submit E224 only if the explicit next question is how much the learned prune contributed. | analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv |
| micro_win | 0.576276019 | 0.576288330 | weak_support | Keep E237 as preferred learned-JEPA sensor, but wait for E224/E230 contrast or exact-score cell attribution before siblings. | conditional:e237_exact_cell_attribution |
| tie | 0.576288330 | 0.576294330 | underresolved | Do not submit lower-ranked E237 files. If E224 is untested, E224 becomes the cleaner contrast; otherwise compare E237-E224. | analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv |
| small_loss | 0.576294330 | 0.576300366 | weak_rejection | Use E224-vs-E237 contrast if E224 is known. If E224 is unknown, do not choose E230/E237 siblings until the loss is attributed. | conditional:e224_or_loss_attribution |
| mixmin_safe_loss | 0.576300366 | 0.576306641 | rejection | Demote E237 siblings. Keep E224 only as a clean diagnostic or move to E166/E154 branch depending on the next hidden-world question. | conditional:e166_or_e154_or_e224_diagnostic |
| branch_loss | 0.576306641 | 0.576341330 | strong_rejection | Close E237 siblings as expected-score candidates. Use E166 for independent broad-world testing or E154 for repaired-branch testing. | conditional:e166_or_e154 |
| hard_fail | 0.576341330 | 0.576591330 | hard_rejection | Run miss anatomy before any further E224/E230/E237 family submission. | conditional:e237_public_miss_anatomy |
| e216_like_fail | 0.576591330 | inf | translator_collapse | Treat E237 as a root-cause failure. Rebuild the target representation rather than tuning a cell threshold. | conditional:root_cause_rebuild |

## E237-vs-E224 Contrast Routebook

| outcome | delta_lo_exclusive | delta_hi_inclusive | contrast_update | next_action |
| --- | --- | --- | --- | --- |
| e237_beats_e224_readably | -inf | -0.000010000 | The learned Q3 cell-prune adds public value beyond the clean E224 body. | Promote E237 over E224; use E230 only as a hand-prune control. |
| e237_beats_e224_micro | -0.000010000 | -0.000003000 | The learned prune helps, but only at hard-label-resolution scale. | Keep E237 as preferred learned sensor; do not tune top-k without attribution. |
| e237_e224_tie | -0.000003000 | 0.000003000 | The learned prune is not public-readable versus E224. | Prefer the cleaner E224 for worldview reading; E237 remains diagnostic. |
| e237_worse_than_e224 | 0.000003000 | inf | The learned Q3 cell-prune removed public-useful Q3 movement or selected wrong cells. | Demote E237 siblings; compare E224 against E230 hand-prune only if Q3 tail blame remains. |

## Example Scores

| score | outcome | world_update_class | delta_vs_e95 | next_action | candidate_to_test |
| --- | --- | --- | --- | --- | --- |
| 0.576251330 | cell_tail_breakthrough | strong_support | -0.000040000 | Do not tune a lower-ranked E237 sibling. First compare against E224 if available, then audit which Q3 cells carried the gain. | conditional:e237_component_attribution_or_e224_contrast |
| 0.576271330 | clean_win | support | -0.000020000 | Promote E237 as the learned-Q3-tail anchor. Submit E224 only if the explicit next question is how much the learned prune contributed. | analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv |
| 0.576283330 | micro_win | weak_support | -0.000008000 | Keep E237 as preferred learned-JEPA sensor, but wait for E224/E230 contrast or exact-score cell attribution before siblings. | conditional:e237_exact_cell_attribution |
| 0.576291330 | tie | underresolved | 0.000000000 | Do not submit lower-ranked E237 files. If E224 is untested, E224 becomes the cleaner contrast; otherwise compare E237-E224. | analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv |
| 0.576300366 | small_loss | weak_rejection | 0.000009036 | Use E224-vs-E237 contrast if E224 is known. If E224 is unknown, do not choose E230/E237 siblings until the loss is attributed. | conditional:e224_or_loss_attribution |
| 0.576306641 | mixmin_safe_loss | rejection | 0.000015311 | Demote E237 siblings. Keep E224 only as a clean diagnostic or move to E166/E154 branch depending on the next hidden-world question. | conditional:e166_or_e154_or_e224_diagnostic |
| 0.576316330 | branch_loss | strong_rejection | 0.000025000 | Close E237 siblings as expected-score candidates. Use E166 for independent broad-world testing or E154 for repaired-branch testing. | conditional:e166_or_e154 |
| 0.576391330 | hard_fail | hard_rejection | 0.000100000 | Run miss anatomy before any further E224/E230/E237 family submission. | conditional:e237_public_miss_anatomy |
| 0.577286509 | e216_like_fail | translator_collapse | 0.000995179 | Treat E237 as a root-cause failure. Rebuild the target representation rather than tuning a cell threshold. | conditional:root_cause_rebuild |

## Pairwise Movement Anatomy

| pair | moved_cells | moved_rows | mean_abs_logit_delta | max_abs_logit_delta | top1_share | target_abs_share | cosine_vs_e154_from_e95 | cosine_vs_e224_clean_from_e95 | cosine_vs_e230_swing25_from_e95 | cosine_vs_e230_risk21_from_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e237_cell25_vs_e95 | 522 | 245 | 0.008912000 | 0.169294968 | 0.010855025 | Q3:0.466410;S4:0.415839;Q1:0.052856;S3:0.034513;S2:0.030382;S1:0.000000;Q2:0.000000 | 0.336926218 | 0.891500789 | 0.905125293 | 0.906865995 |
| e237_cell25_vs_e224_clean | 25 | 25 | 0.001326091 | 0.172092355 | 0.074156654 | Q3:1.000000;S4:0.000000;Q1:0.000000;Q2:0.000000;S1:0.000000;S2:0.000000;S3:0.000000 | 0.336926218 | 0.891500789 | 0.905125293 | 0.906865995 |
| e237_cell25_vs_e154 | 330 | 235 | 0.007309667 | 0.154261984 | 0.012059333 | Q3:0.517813;S4:0.482187;Q1:0.000000;S3:0.000000;Q2:0.000000;S1:0.000000;S2:0.000000 | 0.336926218 | 0.891500789 | 0.905125293 | 0.906865995 |
| e237_cell25_vs_e230_swing25 | 24 | 24 | 0.001122001 | 0.154261984 | 0.078564713 | Q3:1.000000;Q1:0.000000;Q2:0.000000;S1:0.000000;S2:0.000000;S3:0.000000;S4:0.000000 | 0.336926218 | 0.891500789 | 0.905125293 | 0.906865995 |
| e237_cell25_vs_e230_risk21 | 24 | 24 | 0.001102801 | 0.154261984 | 0.079932592 | Q3:1.000000;Q1:0.000000;Q2:0.000000;S1:0.000000;S2:0.000000;S3:0.000000;S4:0.000000 | 0.336926218 | 0.891500789 | 0.905125293 | 0.906865995 |
| e224_clean_vs_e95 | 534 | 250 | 0.010191854 | 0.172092355 | 0.009648734 | Q3:0.533416;S4:0.363619;Q1:0.046219;S3:0.030179;S2:0.026567;S1:0.000000;Q2:0.000000 | 0.316350240 | 1.000000000 | 0.857114887 | 0.902241598 |
| e224_clean_vs_e154 | 355 | 250 | 0.008635758 | 0.172092355 | 0.011387360 | Q3:0.591856;S4:0.408144;Q1:0.000000;S3:0.000000;Q2:0.000000;S1:0.000000;S2:0.000000 | 0.316350240 | 1.000000000 | 0.857114887 | 0.902241598 |
| e230_swing25_vs_e224_clean | 25 | 25 | 0.001558746 | 0.172092355 | 0.063088223 | Q3:1.000000;S4:0.000000;Q1:0.000000;Q2:0.000000;S1:0.000000;S2:0.000000;S3:0.000000 | 0.366401448 | 0.857114887 | 1.000000000 | 0.905831094 |
| e230_risk21_vs_e224_clean | 21 | 21 | 0.001147400 | 0.172092355 | 0.085705531 | Q3:1.000000;S4:0.000000;Q1:0.000000;Q2:0.000000;S1:0.000000;S2:0.000000;S3:0.000000 | 0.315697262 | 0.902241598 | 0.905831094 | 1.000000000 |
| e230_risk13_vs_e224_clean | 13 | 13 | 0.000837939 | 0.172092355 | 0.117357621 | Q3:1.000000;S4:0.000000;Q1:0.000000;Q2:0.000000;S1:0.000000;S2:0.000000;S3:0.000000 | 0.320711480 | 0.921075486 | 0.914270629 | 0.979265538 |

## Cell Overlap Against E224

| candidate | moved_cells_vs_e224 | q3_cells_vs_e224 | overlap_with_e237_cells | jaccard_with_e237_cells | q3_overlap_with_e237 | q3_jaccard_with_e237 | same_as_e237 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e237_cell25 | 25 | 25 | 25 | 1.000000000 | 25 | 1.000000000 | True |
| e230_swing25 | 25 | 25 | 13 | 0.351351351 | 13 | 0.351351351 | False |
| e230_risk21 | 21 | 21 | 11 | 0.314285714 | 11 | 0.314285714 | False |
| e230_risk13 | 13 | 13 | 7 | 0.225806452 | 7 | 0.225806452 | False |

## Target Anatomy

| pair | target | moved_cells | abs_logit_sum | abs_logit_share | mean_signed_logit_delta | max_abs_logit_delta |
| --- | --- | --- | --- | --- | --- | --- |
| e224_clean_vs_e95 | Q3 | 250 | 9.513875533 | 0.533416245 | -0.012707394 | 0.172092355 |
| e224_clean_vs_e95 | S4 | 119 | 6.485419561 | 0.363619236 | 0.003149099 | 0.169294968 |
| e224_clean_vs_e95 | Q1 | 70 | 0.824348264 | 0.046218889 | 0.001680756 | 0.023459002 |
| e224_clean_vs_e95 | S3 | 56 | 0.538264500 | 0.030178977 | -0.001248791 | 0.022007768 |
| e224_clean_vs_e95 | S2 | 39 | 0.473836036 | 0.026566654 | 0.000285552 | 0.021358850 |
| e224_clean_vs_e95 | S1 | 0 | 0.000000000 | 0.000000000 | -0.000000000 | 0.000000000 |
| e224_clean_vs_e95 | Q2 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e230_risk21_vs_e224_clean | Q3 | 21 | 2.007949219 | 1.000000000 | 0.008031797 | 0.172092355 |
| e230_risk21_vs_e224_clean | S4 | 0 | 0.000000000 | 0.000000000 | -0.000000000 | 0.000000000 |
| e230_risk21_vs_e224_clean | Q1 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e230_risk21_vs_e224_clean | Q2 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e230_risk21_vs_e224_clean | S1 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e230_risk21_vs_e224_clean | S2 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e230_risk21_vs_e224_clean | S3 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e230_swing25_vs_e224_clean | Q3 | 25 | 2.727804764 | 1.000000000 | 0.005678151 | 0.172092355 |
| e230_swing25_vs_e224_clean | S4 | 0 | 0.000000000 | 0.000000000 | -0.000000000 | 0.000000000 |
| e230_swing25_vs_e224_clean | Q1 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e230_swing25_vs_e224_clean | Q2 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e230_swing25_vs_e224_clean | S1 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e230_swing25_vs_e224_clean | S2 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e230_swing25_vs_e224_clean | S3 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e237_cell25_vs_e224_clean | Q3 | 25 | 2.320659661 | 1.000000000 | 0.004265480 | 0.172092355 |
| e237_cell25_vs_e224_clean | S4 | 0 | 0.000000000 | 0.000000000 | -0.000000000 | 0.000000000 |
| e237_cell25_vs_e224_clean | Q1 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e237_cell25_vs_e224_clean | Q2 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e237_cell25_vs_e224_clean | S1 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e237_cell25_vs_e224_clean | S2 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e237_cell25_vs_e224_clean | S3 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e237_cell25_vs_e95 | Q3 | 238 | 7.274131931 | 0.466410092 | -0.008441915 | 0.137026478 |
| e237_cell25_vs_e95 | S4 | 119 | 6.485419561 | 0.415838641 | 0.003149099 | 0.169294968 |
| e237_cell25_vs_e95 | Q1 | 70 | 0.824348264 | 0.052856389 | 0.001680756 | 0.023459002 |
| e237_cell25_vs_e95 | S3 | 56 | 0.538264500 | 0.034512983 | -0.001248791 | 0.022007768 |
| e237_cell25_vs_e95 | S2 | 39 | 0.473836036 | 0.030381895 | 0.000285552 | 0.021358850 |
| e237_cell25_vs_e95 | S1 | 0 | 0.000000000 | 0.000000000 | -0.000000000 | 0.000000000 |
| e237_cell25_vs_e95 | Q2 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |

## Decision Rules

- A clean win validates the learned Q3 decisive-cell world, not a generic larger JEPA model.
- If E224 is unsubmitted, E237 public feedback cannot fully separate the clean E224 body from the learned Q3 prune.
- If both E237 and E224 are known, the E237-E224 delta decides whether the learned cell prune adds public value.
- A tie or small loss blocks lower-ranked E237 siblings until exact cell attribution is done.
- A branch loss routes away from same-family Q3 top-k tuning toward E166, E154, or a new target representation.

## Outputs

- routebook: `analysis_outputs/e238_e237_public_feedback_decoder_routebook.csv`
- E224 contrast routebook: `analysis_outputs/e238_e237_public_feedback_decoder_e224_contrast_routebook.csv`
- examples: `analysis_outputs/e238_e237_public_feedback_decoder_examples.csv`
- pairwise anatomy: `analysis_outputs/e238_e237_public_feedback_decoder_pairwise.csv`
- target anatomy: `analysis_outputs/e238_e237_public_feedback_decoder_target_anatomy.csv`
- cell overlap: `analysis_outputs/e238_e237_public_feedback_decoder_cell_overlap.csv`
- candidate metrics: `analysis_outputs/e238_e237_public_feedback_decoder_candidate_metrics.csv`
