# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.605005`
- Best source Q2 OOF: `0.618786`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_sleep_retrieval_meta | 0.618786 | outputs/q2_temporal_digest_on_v26/oof_q2_sleep_retrieval_meta.csv | outputs/q2_temporal_digest_on_v26/submission_q2_sleep_retrieval_meta.csv |
| q2_temporal_deviation_knn_resid | 0.629492 | outputs/q2_temporal_digest_on_v26/oof_q2_temporal_deviation_knn_resid.csv | outputs/q2_temporal_digest_on_v26/submission_q2_temporal_deviation_knn_resid.csv |
| q2_temporal_recovery_knn_resid | 0.659259 | outputs/q2_temporal_digest_on_v26/oof_q2_temporal_recovery_knn_resid.csv | outputs/q2_temporal_digest_on_v26/submission_q2_temporal_recovery_knn_resid.csv |
| q2_temporal_deviation_extra | 0.699671 | outputs/q2_temporal_digest_on_v26/oof_q2_temporal_deviation_extra.csv | outputs/q2_temporal_digest_on_v26/submission_q2_temporal_deviation_extra.csv |
| q2_temporal_recovery_extra | 0.701796 | outputs/q2_temporal_digest_on_v26/oof_q2_temporal_recovery_extra.csv | outputs/q2_temporal_digest_on_v26/submission_q2_temporal_recovery_extra.csv |
| q2_temporal_deviation_knn_logitresid | 0.712724 | outputs/q2_temporal_digest_on_v26/oof_q2_temporal_deviation_knn_logitresid.csv | outputs/q2_temporal_digest_on_v26/submission_q2_temporal_deviation_knn_logitresid.csv |
| q2_temporal_recovery_knn_logitresid | 0.734292 | outputs/q2_temporal_digest_on_v26/oof_q2_temporal_recovery_knn_logitresid.csv | outputs/q2_temporal_digest_on_v26/submission_q2_temporal_recovery_knn_logitresid.csv |
| q2_temporal_deviation_knn_label | 0.735863 | outputs/q2_temporal_digest_on_v26/oof_q2_temporal_deviation_knn_label.csv | outputs/q2_temporal_digest_on_v26/submission_q2_temporal_deviation_knn_label.csv |
| q2_temporal_recovery_knn_label | 0.742728 | outputs/q2_temporal_digest_on_v26/oof_q2_temporal_recovery_knn_label.csv | outputs/q2_temporal_digest_on_v26/submission_q2_temporal_recovery_knn_label.csv |
| q2_temporal_recovery_hgb | 0.764700 | outputs/q2_temporal_digest_on_v26/oof_q2_temporal_recovery_hgb.csv | outputs/q2_temporal_digest_on_v26/submission_q2_temporal_recovery_hgb.csv |
| q2_temporal_deviation_hgb | 0.774541 | outputs/q2_temporal_digest_on_v26/oof_q2_temporal_deviation_hgb.csv | outputs/q2_temporal_digest_on_v26/submission_q2_temporal_deviation_hgb.csv |
| q2_temporal_deviation_proto | 0.781231 | outputs/q2_temporal_digest_on_v26/oof_q2_temporal_deviation_proto.csv | outputs/q2_temporal_digest_on_v26/submission_q2_temporal_deviation_proto.csv |
| q2_temporal_recovery_proto | 0.815397 | outputs/q2_temporal_digest_on_v26/oof_q2_temporal_recovery_proto.csv | outputs/q2_temporal_digest_on_v26/submission_q2_temporal_recovery_proto.csv |
| q2_temporal_recovery_logreg | 0.924743 | outputs/q2_temporal_digest_on_v26/oof_q2_temporal_recovery_logreg.csv | outputs/q2_temporal_digest_on_v26/submission_q2_temporal_recovery_logreg.csv |
| q2_temporal_deviation_logreg | 0.980199 | outputs/q2_temporal_digest_on_v26/oof_q2_temporal_deviation_logreg.csv | outputs/q2_temporal_digest_on_v26/submission_q2_temporal_deviation_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_deviation | 1232 |
| temporal_recovery | 132 |
