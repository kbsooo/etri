# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.502215`
- Best source S2 OOF: `0.541228`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_sleep_retrieval_meta | 0.541228 | outputs/s2_temporal_digest_on_v26/oof_s2_sleep_retrieval_meta.csv | outputs/s2_temporal_digest_on_v26/submission_s2_sleep_retrieval_meta.csv |
| s2_temporal_deviation_knn_resid | 0.543505 | outputs/s2_temporal_digest_on_v26/oof_s2_temporal_deviation_knn_resid.csv | outputs/s2_temporal_digest_on_v26/submission_s2_temporal_deviation_knn_resid.csv |
| s2_temporal_deviation_knn_logitresid | 0.578145 | outputs/s2_temporal_digest_on_v26/oof_s2_temporal_deviation_knn_logitresid.csv | outputs/s2_temporal_digest_on_v26/submission_s2_temporal_deviation_knn_logitresid.csv |
| s2_temporal_recovery_knn_resid | 0.621091 | outputs/s2_temporal_digest_on_v26/oof_s2_temporal_recovery_knn_resid.csv | outputs/s2_temporal_digest_on_v26/submission_s2_temporal_recovery_knn_resid.csv |
| s2_temporal_recovery_hgb | 0.624865 | outputs/s2_temporal_digest_on_v26/oof_s2_temporal_recovery_hgb.csv | outputs/s2_temporal_digest_on_v26/submission_s2_temporal_recovery_hgb.csv |
| s2_temporal_recovery_knn_logitresid | 0.628599 | outputs/s2_temporal_digest_on_v26/oof_s2_temporal_recovery_knn_logitresid.csv | outputs/s2_temporal_digest_on_v26/submission_s2_temporal_recovery_knn_logitresid.csv |
| s2_temporal_deviation_hgb | 0.637990 | outputs/s2_temporal_digest_on_v26/oof_s2_temporal_deviation_hgb.csv | outputs/s2_temporal_digest_on_v26/submission_s2_temporal_deviation_hgb.csv |
| s2_temporal_deviation_extra | 0.674201 | outputs/s2_temporal_digest_on_v26/oof_s2_temporal_deviation_extra.csv | outputs/s2_temporal_digest_on_v26/submission_s2_temporal_deviation_extra.csv |
| s2_temporal_recovery_extra | 0.685476 | outputs/s2_temporal_digest_on_v26/oof_s2_temporal_recovery_extra.csv | outputs/s2_temporal_digest_on_v26/submission_s2_temporal_recovery_extra.csv |
| s2_temporal_deviation_knn_label | 0.688178 | outputs/s2_temporal_digest_on_v26/oof_s2_temporal_deviation_knn_label.csv | outputs/s2_temporal_digest_on_v26/submission_s2_temporal_deviation_knn_label.csv |
| s2_temporal_deviation_proto | 0.688199 | outputs/s2_temporal_digest_on_v26/oof_s2_temporal_deviation_proto.csv | outputs/s2_temporal_digest_on_v26/submission_s2_temporal_deviation_proto.csv |
| s2_temporal_recovery_knn_label | 0.699718 | outputs/s2_temporal_digest_on_v26/oof_s2_temporal_recovery_knn_label.csv | outputs/s2_temporal_digest_on_v26/submission_s2_temporal_recovery_knn_label.csv |
| s2_temporal_recovery_proto | 0.803926 | outputs/s2_temporal_digest_on_v26/oof_s2_temporal_recovery_proto.csv | outputs/s2_temporal_digest_on_v26/submission_s2_temporal_recovery_proto.csv |
| s2_temporal_deviation_logreg | 0.963807 | outputs/s2_temporal_digest_on_v26/oof_s2_temporal_deviation_logreg.csv | outputs/s2_temporal_digest_on_v26/submission_s2_temporal_deviation_logreg.csv |
| s2_temporal_recovery_logreg | 1.030052 | outputs/s2_temporal_digest_on_v26/oof_s2_temporal_recovery_logreg.csv | outputs/s2_temporal_digest_on_v26/submission_s2_temporal_recovery_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_deviation | 1232 |
| temporal_recovery | 132 |
