# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.562225`
- Best source Q2 OOF: `0.597969`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_sleep_retrieval_meta | 0.597969 | outputs/q2_temporal_state_recurrence_on_v48/oof_q2_sleep_retrieval_meta.csv | outputs/q2_temporal_state_recurrence_on_v48/submission_q2_sleep_retrieval_meta.csv |
| q2_temporal_state_recurrence_knn_resid | 0.665663 | outputs/q2_temporal_state_recurrence_on_v48/oof_q2_temporal_state_recurrence_knn_resid.csv | outputs/q2_temporal_state_recurrence_on_v48/submission_q2_temporal_state_recurrence_knn_resid.csv |
| q2_temporal_state_recurrence_extra | 0.695327 | outputs/q2_temporal_state_recurrence_on_v48/oof_q2_temporal_state_recurrence_extra.csv | outputs/q2_temporal_state_recurrence_on_v48/submission_q2_temporal_state_recurrence_extra.csv |
| q2_temporal_state_recurrence_knn_label | 0.718713 | outputs/q2_temporal_state_recurrence_on_v48/oof_q2_temporal_state_recurrence_knn_label.csv | outputs/q2_temporal_state_recurrence_on_v48/submission_q2_temporal_state_recurrence_knn_label.csv |
| q2_temporal_state_recurrence_knn_logitresid | 0.731435 | outputs/q2_temporal_state_recurrence_on_v48/oof_q2_temporal_state_recurrence_knn_logitresid.csv | outputs/q2_temporal_state_recurrence_on_v48/submission_q2_temporal_state_recurrence_knn_logitresid.csv |
| q2_temporal_state_recurrence_hgb | 0.734829 | outputs/q2_temporal_state_recurrence_on_v48/oof_q2_temporal_state_recurrence_hgb.csv | outputs/q2_temporal_state_recurrence_on_v48/submission_q2_temporal_state_recurrence_hgb.csv |
| q2_temporal_state_recurrence_proto | 0.742322 | outputs/q2_temporal_state_recurrence_on_v48/oof_q2_temporal_state_recurrence_proto.csv | outputs/q2_temporal_state_recurrence_on_v48/submission_q2_temporal_state_recurrence_proto.csv |
| q2_temporal_state_recurrence_logreg | 0.856729 | outputs/q2_temporal_state_recurrence_on_v48/oof_q2_temporal_state_recurrence_logreg.csv | outputs/q2_temporal_state_recurrence_on_v48/submission_q2_temporal_state_recurrence_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_recurrence | 26 |
