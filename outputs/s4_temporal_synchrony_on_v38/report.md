# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.526575`
- Best source S4 OOF: `0.544424`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_temporal_synchrony_knn_resid | 0.544424 | outputs/s4_temporal_synchrony_on_v38/oof_s4_temporal_synchrony_knn_resid.csv | outputs/s4_temporal_synchrony_on_v38/submission_s4_temporal_synchrony_knn_resid.csv |
| s4_sleep_retrieval_meta | 0.547296 | outputs/s4_temporal_synchrony_on_v38/oof_s4_sleep_retrieval_meta.csv | outputs/s4_temporal_synchrony_on_v38/submission_s4_sleep_retrieval_meta.csv |
| s4_temporal_synchrony_knn_logitresid | 0.573209 | outputs/s4_temporal_synchrony_on_v38/oof_s4_temporal_synchrony_knn_logitresid.csv | outputs/s4_temporal_synchrony_on_v38/submission_s4_temporal_synchrony_knn_logitresid.csv |
| s4_temporal_synchrony_hgb | 0.682158 | outputs/s4_temporal_synchrony_on_v38/oof_s4_temporal_synchrony_hgb.csv | outputs/s4_temporal_synchrony_on_v38/submission_s4_temporal_synchrony_hgb.csv |
| s4_temporal_synchrony_extra | 0.687779 | outputs/s4_temporal_synchrony_on_v38/oof_s4_temporal_synchrony_extra.csv | outputs/s4_temporal_synchrony_on_v38/submission_s4_temporal_synchrony_extra.csv |
| s4_temporal_synchrony_knn_label | 0.706466 | outputs/s4_temporal_synchrony_on_v38/oof_s4_temporal_synchrony_knn_label.csv | outputs/s4_temporal_synchrony_on_v38/submission_s4_temporal_synchrony_knn_label.csv |
| s4_temporal_synchrony_proto | 0.727779 | outputs/s4_temporal_synchrony_on_v38/oof_s4_temporal_synchrony_proto.csv | outputs/s4_temporal_synchrony_on_v38/submission_s4_temporal_synchrony_proto.csv |
| s4_temporal_synchrony_logreg | 0.800729 | outputs/s4_temporal_synchrony_on_v38/oof_s4_temporal_synchrony_logreg.csv | outputs/s4_temporal_synchrony_on_v38/submission_s4_temporal_synchrony_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_synchrony | 43 |
