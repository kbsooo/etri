# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.545006`
- Best source Q3 OOF: `0.587058`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_sleep_retrieval_meta | 0.587058 | outputs/q3_temporal_synchrony_on_v38/oof_q3_sleep_retrieval_meta.csv | outputs/q3_temporal_synchrony_on_v38/submission_q3_sleep_retrieval_meta.csv |
| q3_temporal_synchrony_knn_resid | 0.638592 | outputs/q3_temporal_synchrony_on_v38/oof_q3_temporal_synchrony_knn_resid.csv | outputs/q3_temporal_synchrony_on_v38/submission_q3_temporal_synchrony_knn_resid.csv |
| q3_temporal_synchrony_knn_logitresid | 0.665559 | outputs/q3_temporal_synchrony_on_v38/oof_q3_temporal_synchrony_knn_logitresid.csv | outputs/q3_temporal_synchrony_on_v38/submission_q3_temporal_synchrony_knn_logitresid.csv |
| q3_temporal_synchrony_extra | 0.691709 | outputs/q3_temporal_synchrony_on_v38/oof_q3_temporal_synchrony_extra.csv | outputs/q3_temporal_synchrony_on_v38/submission_q3_temporal_synchrony_extra.csv |
| q3_temporal_synchrony_hgb | 0.699725 | outputs/q3_temporal_synchrony_on_v38/oof_q3_temporal_synchrony_hgb.csv | outputs/q3_temporal_synchrony_on_v38/submission_q3_temporal_synchrony_hgb.csv |
| q3_temporal_synchrony_knn_label | 0.703577 | outputs/q3_temporal_synchrony_on_v38/oof_q3_temporal_synchrony_knn_label.csv | outputs/q3_temporal_synchrony_on_v38/submission_q3_temporal_synchrony_knn_label.csv |
| q3_temporal_synchrony_proto | 0.785495 | outputs/q3_temporal_synchrony_on_v38/oof_q3_temporal_synchrony_proto.csv | outputs/q3_temporal_synchrony_on_v38/submission_q3_temporal_synchrony_proto.csv |
| q3_temporal_synchrony_logreg | 0.871819 | outputs/q3_temporal_synchrony_on_v38/oof_q3_temporal_synchrony_logreg.csv | outputs/q3_temporal_synchrony_on_v38/submission_q3_temporal_synchrony_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_synchrony | 43 |
