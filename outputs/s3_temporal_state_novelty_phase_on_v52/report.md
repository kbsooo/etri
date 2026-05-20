# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.430434`
- Best source S3 OOF: `0.462709`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_temporal_state_novelty_knn_resid | 0.462709 | outputs/s3_temporal_state_novelty_phase_on_v52/oof_s3_temporal_state_novelty_knn_resid.csv | outputs/s3_temporal_state_novelty_phase_on_v52/submission_s3_temporal_state_novelty_knn_resid.csv |
| s3_temporal_state_novelty_recovery_knn_resid | 0.479047 | outputs/s3_temporal_state_novelty_phase_on_v52/oof_s3_temporal_state_novelty_recovery_knn_resid.csv | outputs/s3_temporal_state_novelty_phase_on_v52/submission_s3_temporal_state_novelty_recovery_knn_resid.csv |
| s3_temporal_state_novelty_knn_logitresid | 0.514125 | outputs/s3_temporal_state_novelty_phase_on_v52/oof_s3_temporal_state_novelty_knn_logitresid.csv | outputs/s3_temporal_state_novelty_phase_on_v52/submission_s3_temporal_state_novelty_knn_logitresid.csv |
| s3_sleep_retrieval_meta | 0.528606 | outputs/s3_temporal_state_novelty_phase_on_v52/oof_s3_sleep_retrieval_meta.csv | outputs/s3_temporal_state_novelty_phase_on_v52/submission_s3_sleep_retrieval_meta.csv |
| s3_temporal_state_novelty_recovery_knn_logitresid | 0.543431 | outputs/s3_temporal_state_novelty_phase_on_v52/oof_s3_temporal_state_novelty_recovery_knn_logitresid.csv | outputs/s3_temporal_state_novelty_phase_on_v52/submission_s3_temporal_state_novelty_recovery_knn_logitresid.csv |
| s3_temporal_state_novelty_recovery_hgb | 0.606733 | outputs/s3_temporal_state_novelty_phase_on_v52/oof_s3_temporal_state_novelty_recovery_hgb.csv | outputs/s3_temporal_state_novelty_phase_on_v52/submission_s3_temporal_state_novelty_recovery_hgb.csv |
| s3_temporal_state_novelty_hgb | 0.629775 | outputs/s3_temporal_state_novelty_phase_on_v52/oof_s3_temporal_state_novelty_hgb.csv | outputs/s3_temporal_state_novelty_phase_on_v52/submission_s3_temporal_state_novelty_hgb.csv |
| s3_temporal_state_novelty_recovery_extra | 0.634084 | outputs/s3_temporal_state_novelty_phase_on_v52/oof_s3_temporal_state_novelty_recovery_extra.csv | outputs/s3_temporal_state_novelty_phase_on_v52/submission_s3_temporal_state_novelty_recovery_extra.csv |
| s3_temporal_state_novelty_extra | 0.653327 | outputs/s3_temporal_state_novelty_phase_on_v52/oof_s3_temporal_state_novelty_extra.csv | outputs/s3_temporal_state_novelty_phase_on_v52/submission_s3_temporal_state_novelty_extra.csv |
| s3_temporal_state_novelty_knn_label | 0.672492 | outputs/s3_temporal_state_novelty_phase_on_v52/oof_s3_temporal_state_novelty_knn_label.csv | outputs/s3_temporal_state_novelty_phase_on_v52/submission_s3_temporal_state_novelty_knn_label.csv |
| s3_temporal_state_novelty_recovery_knn_label | 0.689149 | outputs/s3_temporal_state_novelty_phase_on_v52/oof_s3_temporal_state_novelty_recovery_knn_label.csv | outputs/s3_temporal_state_novelty_phase_on_v52/submission_s3_temporal_state_novelty_recovery_knn_label.csv |
| s3_temporal_state_novelty_recovery_proto | 0.714535 | outputs/s3_temporal_state_novelty_phase_on_v52/oof_s3_temporal_state_novelty_recovery_proto.csv | outputs/s3_temporal_state_novelty_phase_on_v52/submission_s3_temporal_state_novelty_recovery_proto.csv |
| s3_temporal_state_novelty_proto | 0.736432 | outputs/s3_temporal_state_novelty_phase_on_v52/oof_s3_temporal_state_novelty_proto.csv | outputs/s3_temporal_state_novelty_phase_on_v52/submission_s3_temporal_state_novelty_proto.csv |
| s3_temporal_state_novelty_recovery_logreg | 0.945765 | outputs/s3_temporal_state_novelty_phase_on_v52/oof_s3_temporal_state_novelty_recovery_logreg.csv | outputs/s3_temporal_state_novelty_phase_on_v52/submission_s3_temporal_state_novelty_recovery_logreg.csv |
| s3_temporal_state_novelty_logreg | 0.988067 | outputs/s3_temporal_state_novelty_phase_on_v52/oof_s3_temporal_state_novelty_logreg.csv | outputs/s3_temporal_state_novelty_phase_on_v52/submission_s3_temporal_state_novelty_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty | 533 |
| temporal_state_novelty_recovery | 385 |
