# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.454595`
- Best source S3 OOF: `0.463662`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_temporal_decay_knn_resid | 0.463662 | outputs/s3_temporal_decay_signed_on_v36/oof_s3_temporal_decay_knn_resid.csv | outputs/s3_temporal_decay_signed_on_v36/submission_s3_temporal_decay_knn_resid.csv |
| s3_temporal_signed_burden_knn_resid | 0.476754 | outputs/s3_temporal_decay_signed_on_v36/oof_s3_temporal_signed_burden_knn_resid.csv | outputs/s3_temporal_decay_signed_on_v36/submission_s3_temporal_signed_burden_knn_resid.csv |
| s3_temporal_decay_knn_logitresid | 0.487749 | outputs/s3_temporal_decay_signed_on_v36/oof_s3_temporal_decay_knn_logitresid.csv | outputs/s3_temporal_decay_signed_on_v36/submission_s3_temporal_decay_knn_logitresid.csv |
| s3_temporal_signed_burden_knn_logitresid | 0.498245 | outputs/s3_temporal_decay_signed_on_v36/oof_s3_temporal_signed_burden_knn_logitresid.csv | outputs/s3_temporal_decay_signed_on_v36/submission_s3_temporal_signed_burden_knn_logitresid.csv |
| s3_sleep_retrieval_meta | 0.518545 | outputs/s3_temporal_decay_signed_on_v36/oof_s3_sleep_retrieval_meta.csv | outputs/s3_temporal_decay_signed_on_v36/submission_s3_sleep_retrieval_meta.csv |
| s3_temporal_decay_hgb | 0.616851 | outputs/s3_temporal_decay_signed_on_v36/oof_s3_temporal_decay_hgb.csv | outputs/s3_temporal_decay_signed_on_v36/submission_s3_temporal_decay_hgb.csv |
| s3_temporal_decay_knn_label | 0.641737 | outputs/s3_temporal_decay_signed_on_v36/oof_s3_temporal_decay_knn_label.csv | outputs/s3_temporal_decay_signed_on_v36/submission_s3_temporal_decay_knn_label.csv |
| s3_temporal_decay_proto | 0.658519 | outputs/s3_temporal_decay_signed_on_v36/oof_s3_temporal_decay_proto.csv | outputs/s3_temporal_decay_signed_on_v36/submission_s3_temporal_decay_proto.csv |
| s3_temporal_signed_burden_hgb | 0.659586 | outputs/s3_temporal_decay_signed_on_v36/oof_s3_temporal_signed_burden_hgb.csv | outputs/s3_temporal_decay_signed_on_v36/submission_s3_temporal_signed_burden_hgb.csv |
| s3_temporal_signed_burden_knn_label | 0.660941 | outputs/s3_temporal_decay_signed_on_v36/oof_s3_temporal_signed_burden_knn_label.csv | outputs/s3_temporal_decay_signed_on_v36/submission_s3_temporal_signed_burden_knn_label.csv |
| s3_temporal_decay_extra | 0.682990 | outputs/s3_temporal_decay_signed_on_v36/oof_s3_temporal_decay_extra.csv | outputs/s3_temporal_decay_signed_on_v36/submission_s3_temporal_decay_extra.csv |
| s3_temporal_signed_burden_extra | 0.686274 | outputs/s3_temporal_decay_signed_on_v36/oof_s3_temporal_signed_burden_extra.csv | outputs/s3_temporal_decay_signed_on_v36/submission_s3_temporal_signed_burden_extra.csv |
| s3_temporal_signed_burden_proto | 0.694501 | outputs/s3_temporal_decay_signed_on_v36/oof_s3_temporal_signed_burden_proto.csv | outputs/s3_temporal_decay_signed_on_v36/submission_s3_temporal_signed_burden_proto.csv |
| s3_temporal_signed_burden_logreg | 0.836585 | outputs/s3_temporal_decay_signed_on_v36/oof_s3_temporal_signed_burden_logreg.csv | outputs/s3_temporal_decay_signed_on_v36/submission_s3_temporal_signed_burden_logreg.csv |
| s3_temporal_decay_logreg | 0.843495 | outputs/s3_temporal_decay_signed_on_v36/oof_s3_temporal_decay_logreg.csv | outputs/s3_temporal_decay_signed_on_v36/submission_s3_temporal_decay_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_signed_burden | 924 |
| temporal_decay | 1232 |
