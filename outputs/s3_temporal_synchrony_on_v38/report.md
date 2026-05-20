# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.447148`
- Best source S3 OOF: `0.480938`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_temporal_synchrony_knn_resid | 0.480938 | outputs/s3_temporal_synchrony_on_v38/oof_s3_temporal_synchrony_knn_resid.csv | outputs/s3_temporal_synchrony_on_v38/submission_s3_temporal_synchrony_knn_resid.csv |
| s3_sleep_retrieval_meta | 0.505978 | outputs/s3_temporal_synchrony_on_v38/oof_s3_sleep_retrieval_meta.csv | outputs/s3_temporal_synchrony_on_v38/submission_s3_sleep_retrieval_meta.csv |
| s3_temporal_synchrony_knn_logitresid | 0.510601 | outputs/s3_temporal_synchrony_on_v38/oof_s3_temporal_synchrony_knn_logitresid.csv | outputs/s3_temporal_synchrony_on_v38/submission_s3_temporal_synchrony_knn_logitresid.csv |
| s3_temporal_synchrony_hgb | 0.609896 | outputs/s3_temporal_synchrony_on_v38/oof_s3_temporal_synchrony_hgb.csv | outputs/s3_temporal_synchrony_on_v38/submission_s3_temporal_synchrony_hgb.csv |
| s3_temporal_synchrony_knn_label | 0.631941 | outputs/s3_temporal_synchrony_on_v38/oof_s3_temporal_synchrony_knn_label.csv | outputs/s3_temporal_synchrony_on_v38/submission_s3_temporal_synchrony_knn_label.csv |
| s3_temporal_synchrony_extra | 0.673682 | outputs/s3_temporal_synchrony_on_v38/oof_s3_temporal_synchrony_extra.csv | outputs/s3_temporal_synchrony_on_v38/submission_s3_temporal_synchrony_extra.csv |
| s3_temporal_synchrony_proto | 0.705180 | outputs/s3_temporal_synchrony_on_v38/oof_s3_temporal_synchrony_proto.csv | outputs/s3_temporal_synchrony_on_v38/submission_s3_temporal_synchrony_proto.csv |
| s3_temporal_synchrony_logreg | 0.778033 | outputs/s3_temporal_synchrony_on_v38/oof_s3_temporal_synchrony_logreg.csv | outputs/s3_temporal_synchrony_on_v38/submission_s3_temporal_synchrony_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_synchrony | 43 |
