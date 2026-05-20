# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.553268`
- Best source Q2 OOF: `0.572892`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_sleep_retrieval_meta | 0.572892 | outputs/q2_integrated_state_space_on_v52/oof_q2_sleep_retrieval_meta.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_sleep_retrieval_meta.csv |
| q2_temporal_state_novelty_knn_resid | 0.615679 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_novelty_knn_resid.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_novelty_knn_resid.csv |
| q2_temporal_state_transition_knn_resid | 0.621978 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_transition_knn_resid.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_transition_knn_resid.csv |
| q2_temporal_state_recurrence_knn_resid | 0.661660 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_recurrence_knn_resid.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_recurrence_knn_resid.csv |
| q2_temporal_state_transition_knn_logitresid | 0.693348 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_transition_knn_logitresid.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_transition_knn_logitresid.csv |
| q2_temporal_state_recurrence_extra | 0.695327 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_recurrence_extra.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_recurrence_extra.csv |
| q2_temporal_state_novelty_recovery_knn_resid | 0.695516 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_novelty_recovery_knn_resid.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_novelty_recovery_knn_resid.csv |
| q2_temporal_state_novelty_extra | 0.701145 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_novelty_extra.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_novelty_extra.csv |
| q2_temporal_state_transition_extra | 0.707934 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_transition_extra.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_transition_extra.csv |
| q2_temporal_state_novelty_recovery_extra | 0.709302 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_novelty_recovery_extra.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_novelty_recovery_extra.csv |
| q2_temporal_state_novelty_knn_logitresid | 0.715831 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_novelty_knn_logitresid.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_novelty_knn_logitresid.csv |
| q2_temporal_state_novelty_recovery_hgb | 0.716326 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_novelty_recovery_hgb.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_novelty_recovery_hgb.csv |
| q2_temporal_state_recurrence_knn_label | 0.718713 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_recurrence_knn_label.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_recurrence_knn_label.csv |
| q2_temporal_state_transition_knn_label | 0.719800 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_transition_knn_label.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_transition_knn_label.csv |
| q2_temporal_state_novelty_knn_label | 0.724941 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_novelty_knn_label.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_novelty_knn_label.csv |
| q2_temporal_state_novelty_recovery_knn_label | 0.732460 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_novelty_recovery_knn_label.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_novelty_recovery_knn_label.csv |
| q2_temporal_state_recurrence_knn_logitresid | 0.733587 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_recurrence_knn_logitresid.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_recurrence_knn_logitresid.csv |
| q2_temporal_state_recurrence_hgb | 0.734829 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_recurrence_hgb.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_recurrence_hgb.csv |
| q2_temporal_state_recurrence_proto | 0.742322 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_recurrence_proto.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_recurrence_proto.csv |
| q2_temporal_state_novelty_hgb | 0.748453 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_novelty_hgb.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_novelty_hgb.csv |
| q2_temporal_state_novelty_recovery_knn_logitresid | 0.768232 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_novelty_recovery_knn_logitresid.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_novelty_recovery_knn_logitresid.csv |
| q2_temporal_state_transition_hgb | 0.771703 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_transition_hgb.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_transition_hgb.csv |
| q2_temporal_state_novelty_recovery_proto | 0.780649 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_novelty_recovery_proto.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_novelty_recovery_proto.csv |
| q2_temporal_state_novelty_proto | 0.801438 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_novelty_proto.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_novelty_proto.csv |
| q2_temporal_state_transition_proto | 0.808084 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_transition_proto.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_transition_proto.csv |
| q2_temporal_state_recurrence_logreg | 0.856729 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_recurrence_logreg.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_recurrence_logreg.csv |
| q2_temporal_state_novelty_recovery_logreg | 0.920127 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_novelty_recovery_logreg.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_novelty_recovery_logreg.csv |
| q2_temporal_state_transition_logreg | 0.996364 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_transition_logreg.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_transition_logreg.csv |
| q2_temporal_state_novelty_logreg | 1.044089 | outputs/q2_integrated_state_space_on_v52/oof_q2_temporal_state_novelty_logreg.csv | outputs/q2_integrated_state_space_on_v52/submission_q2_temporal_state_novelty_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_transition | 35 |
| temporal_state_recurrence | 26 |
| temporal_state_novelty | 533 |
| temporal_state_novelty_recovery | 385 |
