# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.431725`
- Best source S3 OOF: `0.474983`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_temporal_state_novelty_recovery_knn_resid | 0.474983 | outputs/s3_temporal_state_novelty_recovery_on_v51/oof_s3_temporal_state_novelty_recovery_knn_resid.csv | outputs/s3_temporal_state_novelty_recovery_on_v51/submission_s3_temporal_state_novelty_recovery_knn_resid.csv |
| s3_sleep_retrieval_meta | 0.533763 | outputs/s3_temporal_state_novelty_recovery_on_v51/oof_s3_sleep_retrieval_meta.csv | outputs/s3_temporal_state_novelty_recovery_on_v51/submission_s3_sleep_retrieval_meta.csv |
| s3_temporal_state_novelty_recovery_knn_logitresid | 0.540676 | outputs/s3_temporal_state_novelty_recovery_on_v51/oof_s3_temporal_state_novelty_recovery_knn_logitresid.csv | outputs/s3_temporal_state_novelty_recovery_on_v51/submission_s3_temporal_state_novelty_recovery_knn_logitresid.csv |
| s3_temporal_state_novelty_recovery_hgb | 0.606733 | outputs/s3_temporal_state_novelty_recovery_on_v51/oof_s3_temporal_state_novelty_recovery_hgb.csv | outputs/s3_temporal_state_novelty_recovery_on_v51/submission_s3_temporal_state_novelty_recovery_hgb.csv |
| s3_temporal_state_novelty_recovery_extra | 0.634084 | outputs/s3_temporal_state_novelty_recovery_on_v51/oof_s3_temporal_state_novelty_recovery_extra.csv | outputs/s3_temporal_state_novelty_recovery_on_v51/submission_s3_temporal_state_novelty_recovery_extra.csv |
| s3_temporal_state_novelty_recovery_knn_label | 0.689149 | outputs/s3_temporal_state_novelty_recovery_on_v51/oof_s3_temporal_state_novelty_recovery_knn_label.csv | outputs/s3_temporal_state_novelty_recovery_on_v51/submission_s3_temporal_state_novelty_recovery_knn_label.csv |
| s3_temporal_state_novelty_recovery_proto | 0.714535 | outputs/s3_temporal_state_novelty_recovery_on_v51/oof_s3_temporal_state_novelty_recovery_proto.csv | outputs/s3_temporal_state_novelty_recovery_on_v51/submission_s3_temporal_state_novelty_recovery_proto.csv |
| s3_temporal_state_novelty_recovery_logreg | 0.945765 | outputs/s3_temporal_state_novelty_recovery_on_v51/oof_s3_temporal_state_novelty_recovery_logreg.csv | outputs/s3_temporal_state_novelty_recovery_on_v51/submission_s3_temporal_state_novelty_recovery_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty_recovery | 385 |
