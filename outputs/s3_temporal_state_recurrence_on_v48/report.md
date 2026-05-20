# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.435259`
- Best source S3 OOF: `0.494051`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_temporal_state_recurrence_knn_logitresid | 0.494051 | outputs/s3_temporal_state_recurrence_on_v48/oof_s3_temporal_state_recurrence_knn_logitresid.csv | outputs/s3_temporal_state_recurrence_on_v48/submission_s3_temporal_state_recurrence_knn_logitresid.csv |
| s3_temporal_state_recurrence_knn_resid | 0.498636 | outputs/s3_temporal_state_recurrence_on_v48/oof_s3_temporal_state_recurrence_knn_resid.csv | outputs/s3_temporal_state_recurrence_on_v48/submission_s3_temporal_state_recurrence_knn_resid.csv |
| s3_sleep_retrieval_meta | 0.501369 | outputs/s3_temporal_state_recurrence_on_v48/oof_s3_sleep_retrieval_meta.csv | outputs/s3_temporal_state_recurrence_on_v48/submission_s3_sleep_retrieval_meta.csv |
| s3_temporal_state_recurrence_knn_label | 0.602382 | outputs/s3_temporal_state_recurrence_on_v48/oof_s3_temporal_state_recurrence_knn_label.csv | outputs/s3_temporal_state_recurrence_on_v48/submission_s3_temporal_state_recurrence_knn_label.csv |
| s3_temporal_state_recurrence_hgb | 0.616652 | outputs/s3_temporal_state_recurrence_on_v48/oof_s3_temporal_state_recurrence_hgb.csv | outputs/s3_temporal_state_recurrence_on_v48/submission_s3_temporal_state_recurrence_hgb.csv |
| s3_temporal_state_recurrence_proto | 0.667780 | outputs/s3_temporal_state_recurrence_on_v48/oof_s3_temporal_state_recurrence_proto.csv | outputs/s3_temporal_state_recurrence_on_v48/submission_s3_temporal_state_recurrence_proto.csv |
| s3_temporal_state_recurrence_extra | 0.671969 | outputs/s3_temporal_state_recurrence_on_v48/oof_s3_temporal_state_recurrence_extra.csv | outputs/s3_temporal_state_recurrence_on_v48/submission_s3_temporal_state_recurrence_extra.csv |
| s3_temporal_state_recurrence_logreg | 0.806971 | outputs/s3_temporal_state_recurrence_on_v48/oof_s3_temporal_state_recurrence_logreg.csv | outputs/s3_temporal_state_recurrence_on_v48/submission_s3_temporal_state_recurrence_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_recurrence | 26 |
