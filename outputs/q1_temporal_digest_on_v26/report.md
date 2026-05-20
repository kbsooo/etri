# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.591282`
- Best source Q1 OOF: `0.605562`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.605562 | outputs/q1_temporal_digest_on_v26/oof_q1_sleep_retrieval_meta.csv | outputs/q1_temporal_digest_on_v26/submission_q1_sleep_retrieval_meta.csv |
| q1_temporal_deviation_knn_resid | 0.616352 | outputs/q1_temporal_digest_on_v26/oof_q1_temporal_deviation_knn_resid.csv | outputs/q1_temporal_digest_on_v26/submission_q1_temporal_deviation_knn_resid.csv |
| q1_temporal_recovery_extra | 0.683693 | outputs/q1_temporal_digest_on_v26/oof_q1_temporal_recovery_extra.csv | outputs/q1_temporal_digest_on_v26/submission_q1_temporal_recovery_extra.csv |
| q1_temporal_recovery_knn_resid | 0.691317 | outputs/q1_temporal_digest_on_v26/oof_q1_temporal_recovery_knn_resid.csv | outputs/q1_temporal_digest_on_v26/submission_q1_temporal_recovery_knn_resid.csv |
| q1_temporal_deviation_extra | 0.699161 | outputs/q1_temporal_digest_on_v26/oof_q1_temporal_deviation_extra.csv | outputs/q1_temporal_digest_on_v26/submission_q1_temporal_deviation_extra.csv |
| q1_temporal_recovery_hgb | 0.704264 | outputs/q1_temporal_digest_on_v26/oof_q1_temporal_recovery_hgb.csv | outputs/q1_temporal_digest_on_v26/submission_q1_temporal_recovery_hgb.csv |
| q1_temporal_deviation_hgb | 0.721460 | outputs/q1_temporal_digest_on_v26/oof_q1_temporal_deviation_hgb.csv | outputs/q1_temporal_digest_on_v26/submission_q1_temporal_deviation_hgb.csv |
| q1_temporal_deviation_knn_logitresid | 0.764348 | outputs/q1_temporal_digest_on_v26/oof_q1_temporal_deviation_knn_logitresid.csv | outputs/q1_temporal_digest_on_v26/submission_q1_temporal_deviation_knn_logitresid.csv |
| q1_temporal_deviation_proto | 0.767246 | outputs/q1_temporal_digest_on_v26/oof_q1_temporal_deviation_proto.csv | outputs/q1_temporal_digest_on_v26/submission_q1_temporal_deviation_proto.csv |
| q1_temporal_deviation_knn_label | 0.769286 | outputs/q1_temporal_digest_on_v26/oof_q1_temporal_deviation_knn_label.csv | outputs/q1_temporal_digest_on_v26/submission_q1_temporal_deviation_knn_label.csv |
| q1_temporal_recovery_knn_label | 0.781143 | outputs/q1_temporal_digest_on_v26/oof_q1_temporal_recovery_knn_label.csv | outputs/q1_temporal_digest_on_v26/submission_q1_temporal_recovery_knn_label.csv |
| q1_temporal_recovery_proto | 0.830018 | outputs/q1_temporal_digest_on_v26/oof_q1_temporal_recovery_proto.csv | outputs/q1_temporal_digest_on_v26/submission_q1_temporal_recovery_proto.csv |
| q1_temporal_recovery_knn_logitresid | 0.860924 | outputs/q1_temporal_digest_on_v26/oof_q1_temporal_recovery_knn_logitresid.csv | outputs/q1_temporal_digest_on_v26/submission_q1_temporal_recovery_knn_logitresid.csv |
| q1_temporal_recovery_logreg | 0.880730 | outputs/q1_temporal_digest_on_v26/oof_q1_temporal_recovery_logreg.csv | outputs/q1_temporal_digest_on_v26/submission_q1_temporal_recovery_logreg.csv |
| q1_temporal_deviation_logreg | 1.098009 | outputs/q1_temporal_digest_on_v26/oof_q1_temporal_deviation_logreg.csv | outputs/q1_temporal_digest_on_v26/submission_q1_temporal_deviation_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_deviation | 1232 |
| temporal_recovery | 132 |
