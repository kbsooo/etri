# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.443108`
- Best source S3 OOF: `0.455477`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_temporal_leadlag_knn_resid | 0.455477 | outputs/s3_temporal_leadlag_on_v40/oof_s3_temporal_leadlag_knn_resid.csv | outputs/s3_temporal_leadlag_on_v40/submission_s3_temporal_leadlag_knn_resid.csv |
| s3_temporal_leadlag_knn_logitresid | 0.505527 | outputs/s3_temporal_leadlag_on_v40/oof_s3_temporal_leadlag_knn_logitresid.csv | outputs/s3_temporal_leadlag_on_v40/submission_s3_temporal_leadlag_knn_logitresid.csv |
| s3_sleep_retrieval_meta | 0.510658 | outputs/s3_temporal_leadlag_on_v40/oof_s3_sleep_retrieval_meta.csv | outputs/s3_temporal_leadlag_on_v40/submission_s3_sleep_retrieval_meta.csv |
| s3_temporal_leadlag_hgb | 0.603064 | outputs/s3_temporal_leadlag_on_v40/oof_s3_temporal_leadlag_hgb.csv | outputs/s3_temporal_leadlag_on_v40/submission_s3_temporal_leadlag_hgb.csv |
| s3_temporal_leadlag_knn_label | 0.660705 | outputs/s3_temporal_leadlag_on_v40/oof_s3_temporal_leadlag_knn_label.csv | outputs/s3_temporal_leadlag_on_v40/submission_s3_temporal_leadlag_knn_label.csv |
| s3_temporal_leadlag_extra | 0.667238 | outputs/s3_temporal_leadlag_on_v40/oof_s3_temporal_leadlag_extra.csv | outputs/s3_temporal_leadlag_on_v40/submission_s3_temporal_leadlag_extra.csv |
| s3_temporal_leadlag_proto | 0.704234 | outputs/s3_temporal_leadlag_on_v40/oof_s3_temporal_leadlag_proto.csv | outputs/s3_temporal_leadlag_on_v40/submission_s3_temporal_leadlag_proto.csv |
| s3_temporal_leadlag_logreg | 0.842047 | outputs/s3_temporal_leadlag_on_v40/oof_s3_temporal_leadlag_logreg.csv | outputs/s3_temporal_leadlag_on_v40/submission_s3_temporal_leadlag_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_leadlag | 144 |
