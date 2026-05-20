# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.550468`
- Best source Q1 OOF: `0.571601`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.571601 | outputs/q1_temporal_state_manifold_on_v49/oof_q1_sleep_retrieval_meta.csv | outputs/q1_temporal_state_manifold_on_v49/submission_q1_sleep_retrieval_meta.csv |
| q1_temporal_state_transition_knn_resid | 0.582370 | outputs/q1_temporal_state_manifold_on_v49/oof_q1_temporal_state_transition_knn_resid.csv | outputs/q1_temporal_state_manifold_on_v49/submission_q1_temporal_state_transition_knn_resid.csv |
| q1_temporal_state_recurrence_knn_resid | 0.584052 | outputs/q1_temporal_state_manifold_on_v49/oof_q1_temporal_state_recurrence_knn_resid.csv | outputs/q1_temporal_state_manifold_on_v49/submission_q1_temporal_state_recurrence_knn_resid.csv |
| q1_temporal_state_transition_knn_logitresid | 0.661356 | outputs/q1_temporal_state_manifold_on_v49/oof_q1_temporal_state_transition_knn_logitresid.csv | outputs/q1_temporal_state_manifold_on_v49/submission_q1_temporal_state_transition_knn_logitresid.csv |
| q1_temporal_state_recurrence_knn_logitresid | 0.668054 | outputs/q1_temporal_state_manifold_on_v49/oof_q1_temporal_state_recurrence_knn_logitresid.csv | outputs/q1_temporal_state_manifold_on_v49/submission_q1_temporal_state_recurrence_knn_logitresid.csv |
| q1_temporal_state_transition_extra | 0.693417 | outputs/q1_temporal_state_manifold_on_v49/oof_q1_temporal_state_transition_extra.csv | outputs/q1_temporal_state_manifold_on_v49/submission_q1_temporal_state_transition_extra.csv |
| q1_temporal_state_recurrence_extra | 0.695729 | outputs/q1_temporal_state_manifold_on_v49/oof_q1_temporal_state_recurrence_extra.csv | outputs/q1_temporal_state_manifold_on_v49/submission_q1_temporal_state_recurrence_extra.csv |
| q1_temporal_state_transition_knn_label | 0.697169 | outputs/q1_temporal_state_manifold_on_v49/oof_q1_temporal_state_transition_knn_label.csv | outputs/q1_temporal_state_manifold_on_v49/submission_q1_temporal_state_transition_knn_label.csv |
| q1_temporal_state_recurrence_knn_label | 0.706701 | outputs/q1_temporal_state_manifold_on_v49/oof_q1_temporal_state_recurrence_knn_label.csv | outputs/q1_temporal_state_manifold_on_v49/submission_q1_temporal_state_recurrence_knn_label.csv |
| q1_temporal_state_transition_hgb | 0.711977 | outputs/q1_temporal_state_manifold_on_v49/oof_q1_temporal_state_transition_hgb.csv | outputs/q1_temporal_state_manifold_on_v49/submission_q1_temporal_state_transition_hgb.csv |
| q1_temporal_state_recurrence_hgb | 0.727879 | outputs/q1_temporal_state_manifold_on_v49/oof_q1_temporal_state_recurrence_hgb.csv | outputs/q1_temporal_state_manifold_on_v49/submission_q1_temporal_state_recurrence_hgb.csv |
| q1_temporal_state_transition_proto | 0.769903 | outputs/q1_temporal_state_manifold_on_v49/oof_q1_temporal_state_transition_proto.csv | outputs/q1_temporal_state_manifold_on_v49/submission_q1_temporal_state_transition_proto.csv |
| q1_temporal_state_recurrence_proto | 0.786320 | outputs/q1_temporal_state_manifold_on_v49/oof_q1_temporal_state_recurrence_proto.csv | outputs/q1_temporal_state_manifold_on_v49/submission_q1_temporal_state_recurrence_proto.csv |
| q1_temporal_state_recurrence_logreg | 0.915251 | outputs/q1_temporal_state_manifold_on_v49/oof_q1_temporal_state_recurrence_logreg.csv | outputs/q1_temporal_state_manifold_on_v49/submission_q1_temporal_state_recurrence_logreg.csv |
| q1_temporal_state_transition_logreg | 0.944887 | outputs/q1_temporal_state_manifold_on_v49/oof_q1_temporal_state_transition_logreg.csv | outputs/q1_temporal_state_manifold_on_v49/submission_q1_temporal_state_transition_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_transition | 35 |
| temporal_state_recurrence | 26 |
