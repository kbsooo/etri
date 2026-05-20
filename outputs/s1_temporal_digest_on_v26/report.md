# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.531237`
- Best source S1 OOF: `0.560307`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_temporal_deviation_knn_resid | 0.560307 | outputs/s1_temporal_digest_on_v26/oof_s1_temporal_deviation_knn_resid.csv | outputs/s1_temporal_digest_on_v26/submission_s1_temporal_deviation_knn_resid.csv |
| s1_temporal_recovery_knn_resid | 0.576749 | outputs/s1_temporal_digest_on_v26/oof_s1_temporal_recovery_knn_resid.csv | outputs/s1_temporal_digest_on_v26/submission_s1_temporal_recovery_knn_resid.csv |
| s1_temporal_recovery_knn_logitresid | 0.587233 | outputs/s1_temporal_digest_on_v26/oof_s1_temporal_recovery_knn_logitresid.csv | outputs/s1_temporal_digest_on_v26/submission_s1_temporal_recovery_knn_logitresid.csv |
| s1_sleep_retrieval_meta | 0.587921 | outputs/s1_temporal_digest_on_v26/oof_s1_sleep_retrieval_meta.csv | outputs/s1_temporal_digest_on_v26/submission_s1_sleep_retrieval_meta.csv |
| s1_temporal_deviation_knn_logitresid | 0.609109 | outputs/s1_temporal_digest_on_v26/oof_s1_temporal_deviation_knn_logitresid.csv | outputs/s1_temporal_digest_on_v26/submission_s1_temporal_deviation_knn_logitresid.csv |
| s1_temporal_recovery_hgb | 0.618192 | outputs/s1_temporal_digest_on_v26/oof_s1_temporal_recovery_hgb.csv | outputs/s1_temporal_digest_on_v26/submission_s1_temporal_recovery_hgb.csv |
| s1_temporal_deviation_hgb | 0.644766 | outputs/s1_temporal_digest_on_v26/oof_s1_temporal_deviation_hgb.csv | outputs/s1_temporal_digest_on_v26/submission_s1_temporal_deviation_hgb.csv |
| s1_temporal_recovery_knn_label | 0.663589 | outputs/s1_temporal_digest_on_v26/oof_s1_temporal_recovery_knn_label.csv | outputs/s1_temporal_digest_on_v26/submission_s1_temporal_recovery_knn_label.csv |
| s1_temporal_recovery_extra | 0.667685 | outputs/s1_temporal_digest_on_v26/oof_s1_temporal_recovery_extra.csv | outputs/s1_temporal_digest_on_v26/submission_s1_temporal_recovery_extra.csv |
| s1_temporal_deviation_extra | 0.672412 | outputs/s1_temporal_digest_on_v26/oof_s1_temporal_deviation_extra.csv | outputs/s1_temporal_digest_on_v26/submission_s1_temporal_deviation_extra.csv |
| s1_temporal_deviation_knn_label | 0.674737 | outputs/s1_temporal_digest_on_v26/oof_s1_temporal_deviation_knn_label.csv | outputs/s1_temporal_digest_on_v26/submission_s1_temporal_deviation_knn_label.csv |
| s1_temporal_recovery_proto | 0.677261 | outputs/s1_temporal_digest_on_v26/oof_s1_temporal_recovery_proto.csv | outputs/s1_temporal_digest_on_v26/submission_s1_temporal_recovery_proto.csv |
| s1_temporal_deviation_proto | 0.692615 | outputs/s1_temporal_digest_on_v26/oof_s1_temporal_deviation_proto.csv | outputs/s1_temporal_digest_on_v26/submission_s1_temporal_deviation_proto.csv |
| s1_temporal_recovery_logreg | 0.774015 | outputs/s1_temporal_digest_on_v26/oof_s1_temporal_recovery_logreg.csv | outputs/s1_temporal_digest_on_v26/submission_s1_temporal_recovery_logreg.csv |
| s1_temporal_deviation_logreg | 0.997136 | outputs/s1_temporal_digest_on_v26/oof_s1_temporal_deviation_logreg.csv | outputs/s1_temporal_digest_on_v26/submission_s1_temporal_deviation_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_deviation | 1232 |
| temporal_recovery | 132 |
