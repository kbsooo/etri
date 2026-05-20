# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.489683`
- Best source S2 OOF: `0.510660`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_temporal_synchrony_knn_resid | 0.510660 | outputs/s2_temporal_synchrony_on_v38/oof_s2_temporal_synchrony_knn_resid.csv | outputs/s2_temporal_synchrony_on_v38/submission_s2_temporal_synchrony_knn_resid.csv |
| s2_sleep_retrieval_meta | 0.538289 | outputs/s2_temporal_synchrony_on_v38/oof_s2_sleep_retrieval_meta.csv | outputs/s2_temporal_synchrony_on_v38/submission_s2_sleep_retrieval_meta.csv |
| s2_temporal_synchrony_knn_logitresid | 0.573215 | outputs/s2_temporal_synchrony_on_v38/oof_s2_temporal_synchrony_knn_logitresid.csv | outputs/s2_temporal_synchrony_on_v38/submission_s2_temporal_synchrony_knn_logitresid.csv |
| s2_temporal_synchrony_hgb | 0.638045 | outputs/s2_temporal_synchrony_on_v38/oof_s2_temporal_synchrony_hgb.csv | outputs/s2_temporal_synchrony_on_v38/submission_s2_temporal_synchrony_hgb.csv |
| s2_temporal_synchrony_extra | 0.680087 | outputs/s2_temporal_synchrony_on_v38/oof_s2_temporal_synchrony_extra.csv | outputs/s2_temporal_synchrony_on_v38/submission_s2_temporal_synchrony_extra.csv |
| s2_temporal_synchrony_knn_label | 0.703153 | outputs/s2_temporal_synchrony_on_v38/oof_s2_temporal_synchrony_knn_label.csv | outputs/s2_temporal_synchrony_on_v38/submission_s2_temporal_synchrony_knn_label.csv |
| s2_temporal_synchrony_proto | 0.736717 | outputs/s2_temporal_synchrony_on_v38/oof_s2_temporal_synchrony_proto.csv | outputs/s2_temporal_synchrony_on_v38/submission_s2_temporal_synchrony_proto.csv |
| s2_temporal_synchrony_logreg | 0.827866 | outputs/s2_temporal_synchrony_on_v38/oof_s2_temporal_synchrony_logreg.csv | outputs/s2_temporal_synchrony_on_v38/submission_s2_temporal_synchrony_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_synchrony | 43 |
