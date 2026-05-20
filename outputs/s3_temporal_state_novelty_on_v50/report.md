# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.432507`
- Best source S3 OOF: `0.517523`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_sleep_retrieval_meta | 0.517523 | outputs/s3_temporal_state_novelty_on_v50/oof_s3_sleep_retrieval_meta.csv | outputs/s3_temporal_state_novelty_on_v50/submission_s3_sleep_retrieval_meta.csv |
| s3_temporal_state_novelty_knn_resid | 0.520890 | outputs/s3_temporal_state_novelty_on_v50/oof_s3_temporal_state_novelty_knn_resid.csv | outputs/s3_temporal_state_novelty_on_v50/submission_s3_temporal_state_novelty_knn_resid.csv |
| s3_temporal_state_novelty_knn_logitresid | 0.552571 | outputs/s3_temporal_state_novelty_on_v50/oof_s3_temporal_state_novelty_knn_logitresid.csv | outputs/s3_temporal_state_novelty_on_v50/submission_s3_temporal_state_novelty_knn_logitresid.csv |
| s3_temporal_state_novelty_hgb | 0.612820 | outputs/s3_temporal_state_novelty_on_v50/oof_s3_temporal_state_novelty_hgb.csv | outputs/s3_temporal_state_novelty_on_v50/submission_s3_temporal_state_novelty_hgb.csv |
| s3_temporal_state_novelty_extra | 0.628724 | outputs/s3_temporal_state_novelty_on_v50/oof_s3_temporal_state_novelty_extra.csv | outputs/s3_temporal_state_novelty_on_v50/submission_s3_temporal_state_novelty_extra.csv |
| s3_temporal_state_novelty_knn_label | 0.727839 | outputs/s3_temporal_state_novelty_on_v50/oof_s3_temporal_state_novelty_knn_label.csv | outputs/s3_temporal_state_novelty_on_v50/submission_s3_temporal_state_novelty_knn_label.csv |
| s3_temporal_state_novelty_proto | 0.745358 | outputs/s3_temporal_state_novelty_on_v50/oof_s3_temporal_state_novelty_proto.csv | outputs/s3_temporal_state_novelty_on_v50/submission_s3_temporal_state_novelty_proto.csv |
| s3_temporal_state_novelty_logreg | 1.077089 | outputs/s3_temporal_state_novelty_on_v50/oof_s3_temporal_state_novelty_logreg.csv | outputs/s3_temporal_state_novelty_on_v50/submission_s3_temporal_state_novelty_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty | 148 |
