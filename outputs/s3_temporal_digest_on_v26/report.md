# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.478716`
- Best source S3 OOF: `0.505727`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_temporal_recovery_knn_resid | 0.505727 | outputs/s3_temporal_digest_on_v26/oof_s3_temporal_recovery_knn_resid.csv | outputs/s3_temporal_digest_on_v26/submission_s3_temporal_recovery_knn_resid.csv |
| s3_sleep_retrieval_meta | 0.530216 | outputs/s3_temporal_digest_on_v26/oof_s3_sleep_retrieval_meta.csv | outputs/s3_temporal_digest_on_v26/submission_s3_sleep_retrieval_meta.csv |
| s3_temporal_deviation_knn_resid | 0.531308 | outputs/s3_temporal_digest_on_v26/oof_s3_temporal_deviation_knn_resid.csv | outputs/s3_temporal_digest_on_v26/submission_s3_temporal_deviation_knn_resid.csv |
| s3_temporal_deviation_knn_logitresid | 0.545033 | outputs/s3_temporal_digest_on_v26/oof_s3_temporal_deviation_knn_logitresid.csv | outputs/s3_temporal_digest_on_v26/submission_s3_temporal_deviation_knn_logitresid.csv |
| s3_temporal_recovery_knn_logitresid | 0.546201 | outputs/s3_temporal_digest_on_v26/oof_s3_temporal_recovery_knn_logitresid.csv | outputs/s3_temporal_digest_on_v26/submission_s3_temporal_recovery_knn_logitresid.csv |
| s3_temporal_recovery_hgb | 0.590966 | outputs/s3_temporal_digest_on_v26/oof_s3_temporal_recovery_hgb.csv | outputs/s3_temporal_digest_on_v26/submission_s3_temporal_recovery_hgb.csv |
| s3_temporal_deviation_hgb | 0.637357 | outputs/s3_temporal_digest_on_v26/oof_s3_temporal_deviation_hgb.csv | outputs/s3_temporal_digest_on_v26/submission_s3_temporal_deviation_hgb.csv |
| s3_temporal_deviation_knn_label | 0.647846 | outputs/s3_temporal_digest_on_v26/oof_s3_temporal_deviation_knn_label.csv | outputs/s3_temporal_digest_on_v26/submission_s3_temporal_deviation_knn_label.csv |
| s3_temporal_recovery_knn_label | 0.652253 | outputs/s3_temporal_digest_on_v26/oof_s3_temporal_recovery_knn_label.csv | outputs/s3_temporal_digest_on_v26/submission_s3_temporal_recovery_knn_label.csv |
| s3_temporal_recovery_extra | 0.672956 | outputs/s3_temporal_digest_on_v26/oof_s3_temporal_recovery_extra.csv | outputs/s3_temporal_digest_on_v26/submission_s3_temporal_recovery_extra.csv |
| s3_temporal_deviation_extra | 0.675721 | outputs/s3_temporal_digest_on_v26/oof_s3_temporal_deviation_extra.csv | outputs/s3_temporal_digest_on_v26/submission_s3_temporal_deviation_extra.csv |
| s3_temporal_deviation_proto | 0.696344 | outputs/s3_temporal_digest_on_v26/oof_s3_temporal_deviation_proto.csv | outputs/s3_temporal_digest_on_v26/submission_s3_temporal_deviation_proto.csv |
| s3_temporal_recovery_proto | 0.754637 | outputs/s3_temporal_digest_on_v26/oof_s3_temporal_recovery_proto.csv | outputs/s3_temporal_digest_on_v26/submission_s3_temporal_recovery_proto.csv |
| s3_temporal_recovery_logreg | 0.766402 | outputs/s3_temporal_digest_on_v26/oof_s3_temporal_recovery_logreg.csv | outputs/s3_temporal_digest_on_v26/submission_s3_temporal_recovery_logreg.csv |
| s3_temporal_deviation_logreg | 0.870977 | outputs/s3_temporal_digest_on_v26/oof_s3_temporal_deviation_logreg.csv | outputs/s3_temporal_digest_on_v26/submission_s3_temporal_deviation_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_deviation | 1232 |
| temporal_recovery | 132 |
