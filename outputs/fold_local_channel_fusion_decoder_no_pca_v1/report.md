# Fold-Local Channel Fusion Decoder v1

## Goal

Re-evaluate the selected channel-latent experts with subject-relative centering computed inside each outer fold. This removes the optimistic train-wide subject mean used in the first fusion decoder.

## Result

- Best source: `fold_local_selected`
- OOF avg logloss: `0.617748`
- Drift vs v83 reference: `0.076986`

## Candidate Scores

| source | avg_log_loss | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fold_local_selected | 0.617748 | 0.076986 | 0.662785 | 0.687463 | 0.663960 | 0.564505 | 0.575859 | 0.525808 | 0.643854 |
| fold_local_all_ridge | 0.619029 | 0.080031 | 0.662785 | 0.696035 | 0.663960 | 0.564505 | 0.578367 | 0.523699 | 0.643854 |
| fold_local_all_logreg | 0.620572 | 0.067496 | 0.667327 | 0.687463 | 0.669234 | 0.571340 | 0.575859 | 0.525808 | 0.646974 |
| fold_local_all_hgb | 0.627124 | 0.061812 | 0.673068 | 0.704024 | 0.677716 | 0.574760 | 0.579443 | 0.534232 | 0.646628 |

## Expert Specs

| target | feature | model_family |
| --- | --- | --- |
| Q1 | full__cls_plus_physio__abs_plus_subrel_train | ridge |
| Q2 | only_cross_modal__cls_plus_all_groups__subrel_train | logreg |
| Q3 | full__cls_plus_all_groups__subrel_train | ridge |
| S1 | full__cls_plus_physio__abs_plus_subrel_train | ridge |
| S2 | full__cls_plus_body | logreg |
| S3 | full__cls_plus_all_groups__abs_plus_subrel_train | logreg |
| S4 | only_event__cls__abs_plus_subrel_train | ridge |

## Fold Target Losses

| fold | target | feature | family | loss |
| --- | --- | --- | --- | --- |
| 1 | Q1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.661769 |
| 1 | Q2 | only_cross_modal__cls_plus_all_groups__subrel_train | logreg | 0.713661 |
| 1 | Q3 | full__cls_plus_all_groups__subrel_train | ridge | 0.680772 |
| 1 | S1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.565695 |
| 1 | S2 | full__cls_plus_body | logreg | 0.588736 |
| 1 | S3 | full__cls_plus_all_groups__abs_plus_subrel_train | logreg | 0.488022 |
| 1 | S4 | only_event__cls__abs_plus_subrel_train | ridge | 0.676221 |
| 2 | Q1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.662446 |
| 2 | Q2 | only_cross_modal__cls_plus_all_groups__subrel_train | logreg | 0.640716 |
| 2 | Q3 | full__cls_plus_all_groups__subrel_train | ridge | 0.686883 |
| 2 | S1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.559806 |
| 2 | S2 | full__cls_plus_body | logreg | 0.534678 |
| 2 | S3 | full__cls_plus_all_groups__abs_plus_subrel_train | logreg | 0.519837 |
| 2 | S4 | only_event__cls__abs_plus_subrel_train | ridge | 0.595986 |
| 3 | Q1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.657676 |
| 3 | Q2 | only_cross_modal__cls_plus_all_groups__subrel_train | logreg | 0.744679 |
| 3 | Q3 | full__cls_plus_all_groups__subrel_train | ridge | 0.667582 |
| 3 | S1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.589907 |
| 3 | S2 | full__cls_plus_body | logreg | 0.539659 |
| 3 | S3 | full__cls_plus_all_groups__abs_plus_subrel_train | logreg | 0.546964 |
| 3 | S4 | only_event__cls__abs_plus_subrel_train | ridge | 0.631066 |
| 4 | Q1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.669754 |
| 4 | Q2 | only_cross_modal__cls_plus_all_groups__subrel_train | logreg | 0.653614 |
| 4 | Q3 | full__cls_plus_all_groups__subrel_train | ridge | 0.583444 |
| 4 | S1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.598878 |
| 4 | S2 | full__cls_plus_body | logreg | 0.584988 |
| 4 | S3 | full__cls_plus_all_groups__abs_plus_subrel_train | logreg | 0.491937 |
| 4 | S4 | only_event__cls__abs_plus_subrel_train | ridge | 0.676593 |
| 5 | Q1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.662626 |
| 5 | Q2 | only_cross_modal__cls_plus_all_groups__subrel_train | logreg | 0.682172 |
| 5 | Q3 | full__cls_plus_all_groups__subrel_train | ridge | 0.698894 |
| 5 | S1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.505883 |
| 5 | S2 | full__cls_plus_body | logreg | 0.635450 |
| 5 | S3 | full__cls_plus_all_groups__abs_plus_subrel_train | logreg | 0.586520 |
| 5 | S4 | only_event__cls__abs_plus_subrel_train | ridge | 0.639674 |

## Decision

If this remains close to the train-centered fusion result, the subject-relative decoder signal is not only an artifact of train-wide centering. A large drop means the previous fusion score was optimistic and the next decoder should use fold-local/transductive centering explicitly.