# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.558669`
- Best source Q1 OOF: `0.565949`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.565949 | outputs/q1_temporal_synchrony_on_v38/oof_q1_sleep_retrieval_meta.csv | outputs/q1_temporal_synchrony_on_v38/submission_q1_sleep_retrieval_meta.csv |
| q1_temporal_synchrony_knn_resid | 0.598180 | outputs/q1_temporal_synchrony_on_v38/oof_q1_temporal_synchrony_knn_resid.csv | outputs/q1_temporal_synchrony_on_v38/submission_q1_temporal_synchrony_knn_resid.csv |
| q1_temporal_synchrony_knn_logitresid | 0.649338 | outputs/q1_temporal_synchrony_on_v38/oof_q1_temporal_synchrony_knn_logitresid.csv | outputs/q1_temporal_synchrony_on_v38/submission_q1_temporal_synchrony_knn_logitresid.csv |
| q1_temporal_synchrony_extra | 0.700622 | outputs/q1_temporal_synchrony_on_v38/oof_q1_temporal_synchrony_extra.csv | outputs/q1_temporal_synchrony_on_v38/submission_q1_temporal_synchrony_extra.csv |
| q1_temporal_synchrony_hgb | 0.719611 | outputs/q1_temporal_synchrony_on_v38/oof_q1_temporal_synchrony_hgb.csv | outputs/q1_temporal_synchrony_on_v38/submission_q1_temporal_synchrony_hgb.csv |
| q1_temporal_synchrony_knn_label | 0.740502 | outputs/q1_temporal_synchrony_on_v38/oof_q1_temporal_synchrony_knn_label.csv | outputs/q1_temporal_synchrony_on_v38/submission_q1_temporal_synchrony_knn_label.csv |
| q1_temporal_synchrony_proto | 0.794764 | outputs/q1_temporal_synchrony_on_v38/oof_q1_temporal_synchrony_proto.csv | outputs/q1_temporal_synchrony_on_v38/submission_q1_temporal_synchrony_proto.csv |
| q1_temporal_synchrony_logreg | 0.854943 | outputs/q1_temporal_synchrony_on_v38/oof_q1_temporal_synchrony_logreg.csv | outputs/q1_temporal_synchrony_on_v38/submission_q1_temporal_synchrony_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_synchrony | 43 |
