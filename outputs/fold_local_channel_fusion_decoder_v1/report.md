# Fold-Local Channel Fusion Decoder v1

## Goal

Re-evaluate the selected channel-latent experts with subject-relative centering computed inside each outer fold. This removes the optimistic train-wide subject mean used in the first fusion decoder.

## Result

- Best source: `fold_local_all_logreg`
- OOF avg logloss: `0.625016`
- Drift vs v83 reference: `0.066576`

## Candidate Scores

| source | avg_log_loss | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fold_local_all_logreg | 0.625016 | 0.066576 | 0.672261 | 0.691967 | 0.675157 | 0.574531 | 0.577010 | 0.535007 | 0.649181 |
| fold_local_selected | 0.625343 | 0.065478 | 0.672868 | 0.691967 | 0.677679 | 0.575195 | 0.577010 | 0.535007 | 0.647676 |
| fold_local_all_ridge | 0.625761 | 0.062629 | 0.672868 | 0.695118 | 0.677679 | 0.575195 | 0.577605 | 0.534186 | 0.647676 |
| fold_local_all_hgb | 0.627120 | 0.061957 | 0.673403 | 0.703589 | 0.678032 | 0.574751 | 0.578663 | 0.535022 | 0.646380 |

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
| 1 | Q1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.663547 |
| 1 | Q2 | only_cross_modal__cls_plus_all_groups__subrel_train | logreg | 0.722265 |
| 1 | Q3 | full__cls_plus_all_groups__subrel_train | ridge | 0.690749 |
| 1 | S1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.568481 |
| 1 | S2 | full__cls_plus_body | logreg | 0.594732 |
| 1 | S3 | full__cls_plus_all_groups__abs_plus_subrel_train | logreg | 0.493489 |
| 1 | S4 | only_event__cls__abs_plus_subrel_train | ridge | 0.681807 |
| 2 | Q1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.679261 |
| 2 | Q2 | only_cross_modal__cls_plus_all_groups__subrel_train | logreg | 0.649827 |
| 2 | Q3 | full__cls_plus_all_groups__subrel_train | ridge | 0.703360 |
| 2 | S1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.571955 |
| 2 | S2 | full__cls_plus_body | logreg | 0.536794 |
| 2 | S3 | full__cls_plus_all_groups__abs_plus_subrel_train | logreg | 0.534573 |
| 2 | S4 | only_event__cls__abs_plus_subrel_train | ridge | 0.600968 |
| 3 | Q1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.678164 |
| 3 | Q2 | only_cross_modal__cls_plus_all_groups__subrel_train | logreg | 0.739207 |
| 3 | Q3 | full__cls_plus_all_groups__subrel_train | ridge | 0.664806 |
| 3 | S1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.589885 |
| 3 | S2 | full__cls_plus_body | logreg | 0.541556 |
| 3 | S3 | full__cls_plus_all_groups__abs_plus_subrel_train | logreg | 0.558968 |
| 3 | S4 | only_event__cls__abs_plus_subrel_train | ridge | 0.631708 |
| 4 | Q1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.667023 |
| 4 | Q2 | only_cross_modal__cls_plus_all_groups__subrel_train | logreg | 0.665261 |
| 4 | Q3 | full__cls_plus_all_groups__subrel_train | ridge | 0.617455 |
| 4 | S1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.612605 |
| 4 | S2 | full__cls_plus_body | logreg | 0.580749 |
| 4 | S3 | full__cls_plus_all_groups__abs_plus_subrel_train | logreg | 0.495952 |
| 4 | S4 | only_event__cls__abs_plus_subrel_train | ridge | 0.678885 |
| 5 | Q1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.676681 |
| 5 | Q2 | only_cross_modal__cls_plus_all_groups__subrel_train | logreg | 0.680473 |
| 5 | Q3 | full__cls_plus_all_groups__subrel_train | ridge | 0.710699 |
| 5 | S1 | full__cls_plus_physio__abs_plus_subrel_train | ridge | 0.532188 |
| 5 | S2 | full__cls_plus_body | logreg | 0.634863 |
| 5 | S3 | full__cls_plus_all_groups__abs_plus_subrel_train | logreg | 0.596202 |
| 5 | S4 | only_event__cls__abs_plus_subrel_train | ridge | 0.645239 |

## Decision

If this remains close to the train-centered fusion result, the subject-relative decoder signal is not only an artifact of train-wide centering. A large drop means the previous fusion score was optimistic and the next decoder should use fold-local/transductive centering explicitly.