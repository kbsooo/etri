# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.440488`
- Best source S3 OOF: `0.479807`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_temporal_motif_knn_resid | 0.479807 | outputs/s3_temporal_motif_on_v45/oof_s3_temporal_motif_knn_resid.csv | outputs/s3_temporal_motif_on_v45/submission_s3_temporal_motif_knn_resid.csv |
| s3_temporal_motif_knn_logitresid | 0.498522 | outputs/s3_temporal_motif_on_v45/oof_s3_temporal_motif_knn_logitresid.csv | outputs/s3_temporal_motif_on_v45/submission_s3_temporal_motif_knn_logitresid.csv |
| s3_sleep_retrieval_meta | 0.502127 | outputs/s3_temporal_motif_on_v45/oof_s3_sleep_retrieval_meta.csv | outputs/s3_temporal_motif_on_v45/submission_s3_sleep_retrieval_meta.csv |
| s3_temporal_motif_hgb | 0.620401 | outputs/s3_temporal_motif_on_v45/oof_s3_temporal_motif_hgb.csv | outputs/s3_temporal_motif_on_v45/submission_s3_temporal_motif_hgb.csv |
| s3_temporal_motif_extra | 0.679734 | outputs/s3_temporal_motif_on_v45/oof_s3_temporal_motif_extra.csv | outputs/s3_temporal_motif_on_v45/submission_s3_temporal_motif_extra.csv |
| s3_temporal_motif_knn_label | 0.681543 | outputs/s3_temporal_motif_on_v45/oof_s3_temporal_motif_knn_label.csv | outputs/s3_temporal_motif_on_v45/submission_s3_temporal_motif_knn_label.csv |
| s3_temporal_motif_proto | 0.690991 | outputs/s3_temporal_motif_on_v45/oof_s3_temporal_motif_proto.csv | outputs/s3_temporal_motif_on_v45/submission_s3_temporal_motif_proto.csv |
| s3_temporal_motif_logreg | 0.888116 | outputs/s3_temporal_motif_on_v45/oof_s3_temporal_motif_logreg.csv | outputs/s3_temporal_motif_on_v45/submission_s3_temporal_motif_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_motif | 315 |
