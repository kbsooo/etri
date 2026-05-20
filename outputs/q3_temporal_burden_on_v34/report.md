# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.557756`
- Best source Q3 OOF: `0.582697`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_temporal_burden_knn_resid | 0.582697 | outputs/q3_temporal_burden_on_v34/oof_q3_temporal_burden_knn_resid.csv | outputs/q3_temporal_burden_on_v34/submission_q3_temporal_burden_knn_resid.csv |
| q3_temporal_burden_knn_logitresid | 0.614682 | outputs/q3_temporal_burden_on_v34/oof_q3_temporal_burden_knn_logitresid.csv | outputs/q3_temporal_burden_on_v34/submission_q3_temporal_burden_knn_logitresid.csv |
| q3_sleep_retrieval_meta | 0.616084 | outputs/q3_temporal_burden_on_v34/oof_q3_sleep_retrieval_meta.csv | outputs/q3_temporal_burden_on_v34/submission_q3_sleep_retrieval_meta.csv |
| q3_temporal_burden_extra | 0.674137 | outputs/q3_temporal_burden_on_v34/oof_q3_temporal_burden_extra.csv | outputs/q3_temporal_burden_on_v34/submission_q3_temporal_burden_extra.csv |
| q3_temporal_burden_knn_label | 0.705527 | outputs/q3_temporal_burden_on_v34/oof_q3_temporal_burden_knn_label.csv | outputs/q3_temporal_burden_on_v34/submission_q3_temporal_burden_knn_label.csv |
| q3_temporal_burden_hgb | 0.729848 | outputs/q3_temporal_burden_on_v34/oof_q3_temporal_burden_hgb.csv | outputs/q3_temporal_burden_on_v34/submission_q3_temporal_burden_hgb.csv |
| q3_temporal_burden_proto | 0.759352 | outputs/q3_temporal_burden_on_v34/oof_q3_temporal_burden_proto.csv | outputs/q3_temporal_burden_on_v34/submission_q3_temporal_burden_proto.csv |
| q3_temporal_burden_logreg | 0.922321 | outputs/q3_temporal_burden_on_v34/oof_q3_temporal_burden_logreg.csv | outputs/q3_temporal_burden_on_v34/submission_q3_temporal_burden_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_burden | 1232 |
