# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.556678`
- Best source S4 OOF: `0.581322`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_sleep_retrieval_meta | 0.581322 | outputs/s4_temporal_digest_on_v26/oof_s4_sleep_retrieval_meta.csv | outputs/s4_temporal_digest_on_v26/submission_s4_sleep_retrieval_meta.csv |
| s4_temporal_recovery_hgb | 0.647040 | outputs/s4_temporal_digest_on_v26/oof_s4_temporal_recovery_hgb.csv | outputs/s4_temporal_digest_on_v26/submission_s4_temporal_recovery_hgb.csv |
| s4_temporal_deviation_knn_resid | 0.663121 | outputs/s4_temporal_digest_on_v26/oof_s4_temporal_deviation_knn_resid.csv | outputs/s4_temporal_digest_on_v26/submission_s4_temporal_deviation_knn_resid.csv |
| s4_temporal_deviation_knn_logitresid | 0.668976 | outputs/s4_temporal_digest_on_v26/oof_s4_temporal_deviation_knn_logitresid.csv | outputs/s4_temporal_digest_on_v26/submission_s4_temporal_deviation_knn_logitresid.csv |
| s4_temporal_recovery_extra | 0.677047 | outputs/s4_temporal_digest_on_v26/oof_s4_temporal_recovery_extra.csv | outputs/s4_temporal_digest_on_v26/submission_s4_temporal_recovery_extra.csv |
| s4_temporal_recovery_knn_resid | 0.684786 | outputs/s4_temporal_digest_on_v26/oof_s4_temporal_recovery_knn_resid.csv | outputs/s4_temporal_digest_on_v26/submission_s4_temporal_recovery_knn_resid.csv |
| s4_temporal_deviation_extra | 0.687481 | outputs/s4_temporal_digest_on_v26/oof_s4_temporal_deviation_extra.csv | outputs/s4_temporal_digest_on_v26/submission_s4_temporal_deviation_extra.csv |
| s4_temporal_deviation_knn_label | 0.699535 | outputs/s4_temporal_digest_on_v26/oof_s4_temporal_deviation_knn_label.csv | outputs/s4_temporal_digest_on_v26/submission_s4_temporal_deviation_knn_label.csv |
| s4_temporal_deviation_hgb | 0.709467 | outputs/s4_temporal_digest_on_v26/oof_s4_temporal_deviation_hgb.csv | outputs/s4_temporal_digest_on_v26/submission_s4_temporal_deviation_hgb.csv |
| s4_temporal_recovery_proto | 0.720622 | outputs/s4_temporal_digest_on_v26/oof_s4_temporal_recovery_proto.csv | outputs/s4_temporal_digest_on_v26/submission_s4_temporal_recovery_proto.csv |
| s4_temporal_recovery_knn_logitresid | 0.723067 | outputs/s4_temporal_digest_on_v26/oof_s4_temporal_recovery_knn_logitresid.csv | outputs/s4_temporal_digest_on_v26/submission_s4_temporal_recovery_knn_logitresid.csv |
| s4_temporal_recovery_knn_label | 0.734321 | outputs/s4_temporal_digest_on_v26/oof_s4_temporal_recovery_knn_label.csv | outputs/s4_temporal_digest_on_v26/submission_s4_temporal_recovery_knn_label.csv |
| s4_temporal_deviation_proto | 0.747734 | outputs/s4_temporal_digest_on_v26/oof_s4_temporal_deviation_proto.csv | outputs/s4_temporal_digest_on_v26/submission_s4_temporal_deviation_proto.csv |
| s4_temporal_recovery_logreg | 0.828654 | outputs/s4_temporal_digest_on_v26/oof_s4_temporal_recovery_logreg.csv | outputs/s4_temporal_digest_on_v26/submission_s4_temporal_recovery_logreg.csv |
| s4_temporal_deviation_logreg | 0.907616 | outputs/s4_temporal_digest_on_v26/oof_s4_temporal_deviation_logreg.csv | outputs/s4_temporal_digest_on_v26/submission_s4_temporal_deviation_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_deviation | 1232 |
| temporal_recovery | 132 |
