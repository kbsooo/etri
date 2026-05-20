# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.575663`
- Best source Q2 OOF: `0.601754`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_sleep_retrieval_meta | 0.601754 | outputs/q2_temporal_synchrony_on_v38/oof_q2_sleep_retrieval_meta.csv | outputs/q2_temporal_synchrony_on_v38/submission_q2_sleep_retrieval_meta.csv |
| q2_temporal_synchrony_knn_resid | 0.678212 | outputs/q2_temporal_synchrony_on_v38/oof_q2_temporal_synchrony_knn_resid.csv | outputs/q2_temporal_synchrony_on_v38/submission_q2_temporal_synchrony_knn_resid.csv |
| q2_temporal_synchrony_extra | 0.695648 | outputs/q2_temporal_synchrony_on_v38/oof_q2_temporal_synchrony_extra.csv | outputs/q2_temporal_synchrony_on_v38/submission_q2_temporal_synchrony_extra.csv |
| q2_temporal_synchrony_knn_logitresid | 0.723453 | outputs/q2_temporal_synchrony_on_v38/oof_q2_temporal_synchrony_knn_logitresid.csv | outputs/q2_temporal_synchrony_on_v38/submission_q2_temporal_synchrony_knn_logitresid.csv |
| q2_temporal_synchrony_hgb | 0.736879 | outputs/q2_temporal_synchrony_on_v38/oof_q2_temporal_synchrony_hgb.csv | outputs/q2_temporal_synchrony_on_v38/submission_q2_temporal_synchrony_hgb.csv |
| q2_temporal_synchrony_knn_label | 0.737225 | outputs/q2_temporal_synchrony_on_v38/oof_q2_temporal_synchrony_knn_label.csv | outputs/q2_temporal_synchrony_on_v38/submission_q2_temporal_synchrony_knn_label.csv |
| q2_temporal_synchrony_proto | 0.812497 | outputs/q2_temporal_synchrony_on_v38/oof_q2_temporal_synchrony_proto.csv | outputs/q2_temporal_synchrony_on_v38/submission_q2_temporal_synchrony_proto.csv |
| q2_temporal_synchrony_logreg | 0.882286 | outputs/q2_temporal_synchrony_on_v38/oof_q2_temporal_synchrony_logreg.csv | outputs/q2_temporal_synchrony_on_v38/submission_q2_temporal_synchrony_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_synchrony | 43 |
