# E93 Target-Manifold Counter-Energy Audit

## Question

E92 showed that hidden-block posterior alignment ranks the known public-negative E72 file first. E93 asks whether the train target-dependency manifold supplies the missing counter-energy.

## Method

- Fit seven logistic conditional models `target_j ~ other six targets` on the train labels.
- Score each submission by conditional self-consistency, empirical label-pattern mixture NLL, nearest-pattern NLL, and pair-correlation gap to train.
- Compare known public anchors and live E85/E86/noQ2/E90/E89 candidates against mixmin.
- Use public LB only as a sanity check for known anchors, not as a fitted objective.

## Decision

Target-manifold energy does not reject E72; H11 cannot be promoted to a public-safe selector.

## Known Public Anchor Snapshot

| role | public_lb | target_manifold_delta_mean | conditional_logit_resid_rms_delta_vs_mixmin | pattern_mixture_nll_delta_vs_mixmin | pair_corr_l1_gap_delta_vs_mixmin |
| --- | --- | --- | --- | --- | --- |
| frontier_mixmin | 0.576306641 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| failed_e72 | 0.576407777 | -0.001468687 | -0.004361566 | -0.000213752 | 0.000169258 |
| previous_a2c8 | 0.577439321 | 0.000160559 | -0.001508996 | 0.002081834 | -0.000091160 |
| raw05 | 0.577526307 | 0.001590705 | 0.002601071 | 0.002538093 | -0.000367049 |
| stage2 | 0.577944976 | -0.001093162 | -0.003328575 | 0.000607174 | -0.000558086 |
| ordinal_q | 0.578303365 | 0.008391598 | 0.024785940 | -0.000009996 | 0.000398851 |
| final9 | 0.578427353 | -0.020801364 | -0.053129683 | -0.012770404 | 0.003495995 |
| bad_q2_jepa | 0.579801286 | -0.002958703 | -0.006352633 | -0.005077836 | 0.002554359 |
| bad_lejepa | 0.580246819 | 0.008571197 | -0.011793590 | 0.036575697 | 0.000931483 |
| bad_residual_jepa | 0.581227328 | 0.004859288 | 0.005546233 | 0.008905695 | 0.000125934 |

## Live Candidate Snapshot

| role | target_manifold_delta_mean | conditional_logit_resid_rms_delta_vs_mixmin | pattern_mixture_nll_delta_vs_mixmin | pair_corr_l1_gap_delta_vs_mixmin | posterior_ce_delta_all_vs_mixmin | e72_direction_mass_agree |
| --- | --- | --- | --- | --- | --- | --- |
| max_upside_e86 | -0.000921783 | -0.002120737 | -0.000490985 | -0.000153625 | -0.000255621 | 0.668166079 |
| noq2_contrast | -0.000914184 | -0.002059208 | -0.000542923 | -0.000140422 | -0.000257196 | 0.650503232 |
| balanced_e90 | -0.000877945 | -0.001989446 | -0.000508513 | -0.000135877 | -0.000250767 | 0.657990030 |
| min_contam_e89 | -0.000806467 | -0.001765840 | -0.000518915 | -0.000134645 | -0.000235903 | 0.635838115 |
| conservative_e85 | -0.000742113 | -0.001677615 | -0.000432322 | -0.000116402 | -0.000207023 | 0.649469377 |

## E72 Target-Level Drivers

| target | mean_prob_delta_vs_mixmin | conditional_bce_delta_vs_mixmin | conditional_logit_resid_rms_delta_vs_mixmin | movement_abs_logit_vs_mixmin |
| --- | --- | --- | --- | --- |
| Q2 | 0.000012963 | -0.000378492 | -0.003009649 | 0.004326074 |
| S2 | 0.000767567 | -0.000135226 | -0.003386151 | 0.006127646 |
| S4 | -0.000285541 | -0.000622332 | -0.003788628 | 0.006635952 |
| Q1 | -0.000028138 | -0.000587817 | -0.004318647 | 0.007474068 |
| S3 | 0.000096652 | -0.000816786 | -0.004410437 | 0.005281046 |
| Q3 | 0.000192445 | -0.000613362 | -0.004905500 | 0.007189308 |
| S1 | 0.000499636 | -0.001268863 | -0.006393236 | 0.009755459 |

## Public-LB Sanity Correlation

| metric | spearman_public_lb |
| --- | --- |
| conditional_logit_resid_rms | -0.163636 |
| pattern_mixture_nll | 0.224242 |
| pair_corr_l1_gap | 0.503030 |
| target_manifold_delta_mean | 0.260606 |

## Interpretation

- If E72 is better than mixmin on these energies, target dependency is another E72-tainted representation and must not gate submissions.
- If E72 is worse while decontaminated candidates improve, target-manifold energy is a useful LeJEPA-style health check.
- Either way, this audit should not create a submission by itself; it only decides whether H11 gets promoted or demoted.

## Outputs

- `e93_target_manifold_counterenergy_scores.csv`
- `e93_target_manifold_counterenergy_target_detail.csv`
- `e93_target_manifold_counterenergy_pair_detail.csv`
