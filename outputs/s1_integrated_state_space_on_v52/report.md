# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.493611`
- Best source S1 OOF: `0.559635`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_sleep_retrieval_meta | 0.559635 | outputs/s1_integrated_state_space_on_v52/oof_s1_sleep_retrieval_meta.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_sleep_retrieval_meta.csv |
| s1_temporal_state_transition_knn_resid | 0.573610 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_transition_knn_resid.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_transition_knn_resid.csv |
| s1_temporal_state_recurrence_knn_resid | 0.578904 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_recurrence_knn_resid.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_recurrence_knn_resid.csv |
| s1_temporal_state_novelty_knn_resid | 0.580546 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_novelty_knn_resid.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_novelty_knn_resid.csv |
| s1_temporal_state_novelty_recovery_knn_resid | 0.581976 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_novelty_recovery_knn_resid.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_novelty_recovery_knn_resid.csv |
| s1_temporal_state_recurrence_hgb | 0.602090 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_recurrence_hgb.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_recurrence_hgb.csv |
| s1_temporal_state_recurrence_knn_logitresid | 0.608799 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_recurrence_knn_logitresid.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_recurrence_knn_logitresid.csv |
| s1_temporal_state_novelty_hgb | 0.609393 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_novelty_hgb.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_novelty_hgb.csv |
| s1_temporal_state_novelty_recovery_hgb | 0.620083 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_novelty_recovery_hgb.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_novelty_recovery_hgb.csv |
| s1_temporal_state_transition_knn_logitresid | 0.621272 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_transition_knn_logitresid.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_transition_knn_logitresid.csv |
| s1_temporal_state_transition_hgb | 0.631181 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_transition_hgb.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_transition_hgb.csv |
| s1_temporal_state_novelty_recovery_knn_logitresid | 0.636210 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_novelty_recovery_knn_logitresid.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_novelty_recovery_knn_logitresid.csv |
| s1_temporal_state_novelty_knn_logitresid | 0.641460 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_novelty_knn_logitresid.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_novelty_knn_logitresid.csv |
| s1_temporal_state_recurrence_knn_label | 0.641696 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_recurrence_knn_label.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_recurrence_knn_label.csv |
| s1_temporal_state_novelty_recovery_knn_label | 0.664979 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_novelty_recovery_knn_label.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_novelty_recovery_knn_label.csv |
| s1_temporal_state_novelty_knn_label | 0.676489 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_novelty_knn_label.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_novelty_knn_label.csv |
| s1_temporal_state_transition_extra | 0.679294 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_transition_extra.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_transition_extra.csv |
| s1_temporal_state_recurrence_extra | 0.679529 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_recurrence_extra.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_recurrence_extra.csv |
| s1_temporal_state_novelty_recovery_extra | 0.682396 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_novelty_recovery_extra.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_novelty_recovery_extra.csv |
| s1_temporal_state_transition_knn_label | 0.683137 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_transition_knn_label.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_transition_knn_label.csv |
| s1_temporal_state_novelty_extra | 0.688246 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_novelty_extra.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_novelty_extra.csv |
| s1_temporal_state_recurrence_proto | 0.689360 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_recurrence_proto.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_recurrence_proto.csv |
| s1_temporal_state_transition_proto | 0.715866 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_transition_proto.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_transition_proto.csv |
| s1_temporal_state_novelty_recovery_proto | 0.726643 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_novelty_recovery_proto.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_novelty_recovery_proto.csv |
| s1_temporal_state_novelty_proto | 0.786984 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_novelty_proto.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_novelty_proto.csv |
| s1_temporal_state_recurrence_logreg | 0.807344 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_recurrence_logreg.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_recurrence_logreg.csv |
| s1_temporal_state_transition_logreg | 0.872877 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_transition_logreg.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_transition_logreg.csv |
| s1_temporal_state_novelty_recovery_logreg | 0.933244 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_novelty_recovery_logreg.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_novelty_recovery_logreg.csv |
| s1_temporal_state_novelty_logreg | 1.080738 | outputs/s1_integrated_state_space_on_v52/oof_s1_temporal_state_novelty_logreg.csv | outputs/s1_integrated_state_space_on_v52/submission_s1_temporal_state_novelty_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_transition | 35 |
| temporal_state_recurrence | 26 |
| temporal_state_novelty | 533 |
| temporal_state_novelty_recovery | 385 |
