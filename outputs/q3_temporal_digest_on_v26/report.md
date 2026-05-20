# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.588775`
- Best source Q3 OOF: `0.617144`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_temporal_deviation_knn_resid | 0.617144 | outputs/q3_temporal_digest_on_v26/oof_q3_temporal_deviation_knn_resid.csv | outputs/q3_temporal_digest_on_v26/submission_q3_temporal_deviation_knn_resid.csv |
| q3_sleep_retrieval_meta | 0.622279 | outputs/q3_temporal_digest_on_v26/oof_q3_sleep_retrieval_meta.csv | outputs/q3_temporal_digest_on_v26/submission_q3_sleep_retrieval_meta.csv |
| q3_temporal_recovery_knn_resid | 0.625795 | outputs/q3_temporal_digest_on_v26/oof_q3_temporal_recovery_knn_resid.csv | outputs/q3_temporal_digest_on_v26/submission_q3_temporal_recovery_knn_resid.csv |
| q3_temporal_recovery_knn_logitresid | 0.683169 | outputs/q3_temporal_digest_on_v26/oof_q3_temporal_recovery_knn_logitresid.csv | outputs/q3_temporal_digest_on_v26/submission_q3_temporal_recovery_knn_logitresid.csv |
| q3_temporal_recovery_extra | 0.683705 | outputs/q3_temporal_digest_on_v26/oof_q3_temporal_recovery_extra.csv | outputs/q3_temporal_digest_on_v26/submission_q3_temporal_recovery_extra.csv |
| q3_temporal_deviation_extra | 0.684201 | outputs/q3_temporal_digest_on_v26/oof_q3_temporal_deviation_extra.csv | outputs/q3_temporal_digest_on_v26/submission_q3_temporal_deviation_extra.csv |
| q3_temporal_deviation_knn_logitresid | 0.685462 | outputs/q3_temporal_digest_on_v26/oof_q3_temporal_deviation_knn_logitresid.csv | outputs/q3_temporal_digest_on_v26/submission_q3_temporal_deviation_knn_logitresid.csv |
| q3_temporal_recovery_hgb | 0.691447 | outputs/q3_temporal_digest_on_v26/oof_q3_temporal_recovery_hgb.csv | outputs/q3_temporal_digest_on_v26/submission_q3_temporal_recovery_hgb.csv |
| q3_temporal_deviation_hgb | 0.698575 | outputs/q3_temporal_digest_on_v26/oof_q3_temporal_deviation_hgb.csv | outputs/q3_temporal_digest_on_v26/submission_q3_temporal_deviation_hgb.csv |
| q3_temporal_deviation_knn_label | 0.702403 | outputs/q3_temporal_digest_on_v26/oof_q3_temporal_deviation_knn_label.csv | outputs/q3_temporal_digest_on_v26/submission_q3_temporal_deviation_knn_label.csv |
| q3_temporal_recovery_knn_label | 0.705060 | outputs/q3_temporal_digest_on_v26/oof_q3_temporal_recovery_knn_label.csv | outputs/q3_temporal_digest_on_v26/submission_q3_temporal_recovery_knn_label.csv |
| q3_temporal_recovery_proto | 0.731461 | outputs/q3_temporal_digest_on_v26/oof_q3_temporal_recovery_proto.csv | outputs/q3_temporal_digest_on_v26/submission_q3_temporal_recovery_proto.csv |
| q3_temporal_deviation_proto | 0.736854 | outputs/q3_temporal_digest_on_v26/oof_q3_temporal_deviation_proto.csv | outputs/q3_temporal_digest_on_v26/submission_q3_temporal_deviation_proto.csv |
| q3_temporal_deviation_logreg | 0.855198 | outputs/q3_temporal_digest_on_v26/oof_q3_temporal_deviation_logreg.csv | outputs/q3_temporal_digest_on_v26/submission_q3_temporal_deviation_logreg.csv |
| q3_temporal_recovery_logreg | 0.868286 | outputs/q3_temporal_digest_on_v26/oof_q3_temporal_recovery_logreg.csv | outputs/q3_temporal_digest_on_v26/submission_q3_temporal_recovery_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_deviation | 1232 |
| temporal_recovery | 132 |
