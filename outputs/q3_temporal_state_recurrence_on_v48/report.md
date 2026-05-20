# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.532111`
- Best source Q3 OOF: `0.551841`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_sleep_retrieval_meta | 0.551841 | outputs/q3_temporal_state_recurrence_on_v48/oof_q3_sleep_retrieval_meta.csv | outputs/q3_temporal_state_recurrence_on_v48/submission_q3_sleep_retrieval_meta.csv |
| q3_temporal_state_recurrence_knn_resid | 0.610264 | outputs/q3_temporal_state_recurrence_on_v48/oof_q3_temporal_state_recurrence_knn_resid.csv | outputs/q3_temporal_state_recurrence_on_v48/submission_q3_temporal_state_recurrence_knn_resid.csv |
| q3_temporal_state_recurrence_hgb | 0.698823 | outputs/q3_temporal_state_recurrence_on_v48/oof_q3_temporal_state_recurrence_hgb.csv | outputs/q3_temporal_state_recurrence_on_v48/submission_q3_temporal_state_recurrence_hgb.csv |
| q3_temporal_state_recurrence_knn_logitresid | 0.700071 | outputs/q3_temporal_state_recurrence_on_v48/oof_q3_temporal_state_recurrence_knn_logitresid.csv | outputs/q3_temporal_state_recurrence_on_v48/submission_q3_temporal_state_recurrence_knn_logitresid.csv |
| q3_temporal_state_recurrence_extra | 0.700456 | outputs/q3_temporal_state_recurrence_on_v48/oof_q3_temporal_state_recurrence_extra.csv | outputs/q3_temporal_state_recurrence_on_v48/submission_q3_temporal_state_recurrence_extra.csv |
| q3_temporal_state_recurrence_knn_label | 0.726892 | outputs/q3_temporal_state_recurrence_on_v48/oof_q3_temporal_state_recurrence_knn_label.csv | outputs/q3_temporal_state_recurrence_on_v48/submission_q3_temporal_state_recurrence_knn_label.csv |
| q3_temporal_state_recurrence_proto | 0.731022 | outputs/q3_temporal_state_recurrence_on_v48/oof_q3_temporal_state_recurrence_proto.csv | outputs/q3_temporal_state_recurrence_on_v48/submission_q3_temporal_state_recurrence_proto.csv |
| q3_temporal_state_recurrence_logreg | 0.918783 | outputs/q3_temporal_state_recurrence_on_v48/oof_q3_temporal_state_recurrence_logreg.csv | outputs/q3_temporal_state_recurrence_on_v48/submission_q3_temporal_state_recurrence_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_recurrence | 26 |
