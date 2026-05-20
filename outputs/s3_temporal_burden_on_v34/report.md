# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.461741`
- Best source S3 OOF: `0.467871`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_temporal_burden_knn_resid | 0.467871 | outputs/s3_temporal_burden_on_v34/oof_s3_temporal_burden_knn_resid.csv | outputs/s3_temporal_burden_on_v34/submission_s3_temporal_burden_knn_resid.csv |
| s3_temporal_burden_knn_logitresid | 0.499261 | outputs/s3_temporal_burden_on_v34/oof_s3_temporal_burden_knn_logitresid.csv | outputs/s3_temporal_burden_on_v34/submission_s3_temporal_burden_knn_logitresid.csv |
| s3_sleep_retrieval_meta | 0.539700 | outputs/s3_temporal_burden_on_v34/oof_s3_sleep_retrieval_meta.csv | outputs/s3_temporal_burden_on_v34/submission_s3_sleep_retrieval_meta.csv |
| s3_temporal_burden_hgb | 0.577145 | outputs/s3_temporal_burden_on_v34/oof_s3_temporal_burden_hgb.csv | outputs/s3_temporal_burden_on_v34/submission_s3_temporal_burden_hgb.csv |
| s3_temporal_burden_knn_label | 0.635031 | outputs/s3_temporal_burden_on_v34/oof_s3_temporal_burden_knn_label.csv | outputs/s3_temporal_burden_on_v34/submission_s3_temporal_burden_knn_label.csv |
| s3_temporal_burden_extra | 0.653539 | outputs/s3_temporal_burden_on_v34/oof_s3_temporal_burden_extra.csv | outputs/s3_temporal_burden_on_v34/submission_s3_temporal_burden_extra.csv |
| s3_temporal_burden_proto | 0.686991 | outputs/s3_temporal_burden_on_v34/oof_s3_temporal_burden_proto.csv | outputs/s3_temporal_burden_on_v34/submission_s3_temporal_burden_proto.csv |
| s3_temporal_burden_logreg | 0.900063 | outputs/s3_temporal_burden_on_v34/oof_s3_temporal_burden_logreg.csv | outputs/s3_temporal_burden_on_v34/submission_s3_temporal_burden_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_burden | 1232 |
