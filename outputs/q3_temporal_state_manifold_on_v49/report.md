# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.529737`
- Best source Q3 OOF: `0.537993`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_sleep_retrieval_meta | 0.537993 | outputs/q3_temporal_state_manifold_on_v49/oof_q3_sleep_retrieval_meta.csv | outputs/q3_temporal_state_manifold_on_v49/submission_q3_sleep_retrieval_meta.csv |
| q3_temporal_state_transition_knn_resid | 0.561750 | outputs/q3_temporal_state_manifold_on_v49/oof_q3_temporal_state_transition_knn_resid.csv | outputs/q3_temporal_state_manifold_on_v49/submission_q3_temporal_state_transition_knn_resid.csv |
| q3_temporal_state_recurrence_knn_resid | 0.586409 | outputs/q3_temporal_state_manifold_on_v49/oof_q3_temporal_state_recurrence_knn_resid.csv | outputs/q3_temporal_state_manifold_on_v49/submission_q3_temporal_state_recurrence_knn_resid.csv |
| q3_temporal_state_transition_knn_logitresid | 0.634670 | outputs/q3_temporal_state_manifold_on_v49/oof_q3_temporal_state_transition_knn_logitresid.csv | outputs/q3_temporal_state_manifold_on_v49/submission_q3_temporal_state_transition_knn_logitresid.csv |
| q3_temporal_state_recurrence_knn_logitresid | 0.693188 | outputs/q3_temporal_state_manifold_on_v49/oof_q3_temporal_state_recurrence_knn_logitresid.csv | outputs/q3_temporal_state_manifold_on_v49/submission_q3_temporal_state_recurrence_knn_logitresid.csv |
| q3_temporal_state_transition_hgb | 0.698513 | outputs/q3_temporal_state_manifold_on_v49/oof_q3_temporal_state_transition_hgb.csv | outputs/q3_temporal_state_manifold_on_v49/submission_q3_temporal_state_transition_hgb.csv |
| q3_temporal_state_recurrence_hgb | 0.698823 | outputs/q3_temporal_state_manifold_on_v49/oof_q3_temporal_state_recurrence_hgb.csv | outputs/q3_temporal_state_manifold_on_v49/submission_q3_temporal_state_recurrence_hgb.csv |
| q3_temporal_state_recurrence_extra | 0.700456 | outputs/q3_temporal_state_manifold_on_v49/oof_q3_temporal_state_recurrence_extra.csv | outputs/q3_temporal_state_manifold_on_v49/submission_q3_temporal_state_recurrence_extra.csv |
| q3_temporal_state_transition_extra | 0.700652 | outputs/q3_temporal_state_manifold_on_v49/oof_q3_temporal_state_transition_extra.csv | outputs/q3_temporal_state_manifold_on_v49/submission_q3_temporal_state_transition_extra.csv |
| q3_temporal_state_transition_knn_label | 0.715301 | outputs/q3_temporal_state_manifold_on_v49/oof_q3_temporal_state_transition_knn_label.csv | outputs/q3_temporal_state_manifold_on_v49/submission_q3_temporal_state_transition_knn_label.csv |
| q3_temporal_state_recurrence_knn_label | 0.726892 | outputs/q3_temporal_state_manifold_on_v49/oof_q3_temporal_state_recurrence_knn_label.csv | outputs/q3_temporal_state_manifold_on_v49/submission_q3_temporal_state_recurrence_knn_label.csv |
| q3_temporal_state_recurrence_proto | 0.731022 | outputs/q3_temporal_state_manifold_on_v49/oof_q3_temporal_state_recurrence_proto.csv | outputs/q3_temporal_state_manifold_on_v49/submission_q3_temporal_state_recurrence_proto.csv |
| q3_temporal_state_transition_proto | 0.789024 | outputs/q3_temporal_state_manifold_on_v49/oof_q3_temporal_state_transition_proto.csv | outputs/q3_temporal_state_manifold_on_v49/submission_q3_temporal_state_transition_proto.csv |
| q3_temporal_state_recurrence_logreg | 0.918783 | outputs/q3_temporal_state_manifold_on_v49/oof_q3_temporal_state_recurrence_logreg.csv | outputs/q3_temporal_state_manifold_on_v49/submission_q3_temporal_state_recurrence_logreg.csv |
| q3_temporal_state_transition_logreg | 0.933328 | outputs/q3_temporal_state_manifold_on_v49/oof_q3_temporal_state_transition_logreg.csv | outputs/q3_temporal_state_manifold_on_v49/submission_q3_temporal_state_transition_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_transition | 35 |
| temporal_state_recurrence | 26 |
