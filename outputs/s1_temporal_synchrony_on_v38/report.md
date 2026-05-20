# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.505435`
- Best source S1 OOF: `0.552661`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_temporal_synchrony_knn_resid | 0.552661 | outputs/s1_temporal_synchrony_on_v38/oof_s1_temporal_synchrony_knn_resid.csv | outputs/s1_temporal_synchrony_on_v38/submission_s1_temporal_synchrony_knn_resid.csv |
| s1_sleep_retrieval_meta | 0.553123 | outputs/s1_temporal_synchrony_on_v38/oof_s1_sleep_retrieval_meta.csv | outputs/s1_temporal_synchrony_on_v38/submission_s1_sleep_retrieval_meta.csv |
| s1_temporal_synchrony_knn_logitresid | 0.572543 | outputs/s1_temporal_synchrony_on_v38/oof_s1_temporal_synchrony_knn_logitresid.csv | outputs/s1_temporal_synchrony_on_v38/submission_s1_temporal_synchrony_knn_logitresid.csv |
| s1_temporal_synchrony_hgb | 0.640459 | outputs/s1_temporal_synchrony_on_v38/oof_s1_temporal_synchrony_hgb.csv | outputs/s1_temporal_synchrony_on_v38/submission_s1_temporal_synchrony_hgb.csv |
| s1_temporal_synchrony_knn_label | 0.659686 | outputs/s1_temporal_synchrony_on_v38/oof_s1_temporal_synchrony_knn_label.csv | outputs/s1_temporal_synchrony_on_v38/submission_s1_temporal_synchrony_knn_label.csv |
| s1_temporal_synchrony_extra | 0.682848 | outputs/s1_temporal_synchrony_on_v38/oof_s1_temporal_synchrony_extra.csv | outputs/s1_temporal_synchrony_on_v38/submission_s1_temporal_synchrony_extra.csv |
| s1_temporal_synchrony_proto | 0.720309 | outputs/s1_temporal_synchrony_on_v38/oof_s1_temporal_synchrony_proto.csv | outputs/s1_temporal_synchrony_on_v38/submission_s1_temporal_synchrony_proto.csv |
| s1_temporal_synchrony_logreg | 0.840281 | outputs/s1_temporal_synchrony_on_v38/oof_s1_temporal_synchrony_logreg.csv | outputs/s1_temporal_synchrony_on_v38/submission_s1_temporal_synchrony_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_synchrony | 43 |
