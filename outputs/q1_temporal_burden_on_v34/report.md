# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.568535`
- Best source Q1 OOF: `0.582740`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.582740 | outputs/q1_temporal_burden_on_v34/oof_q1_sleep_retrieval_meta.csv | outputs/q1_temporal_burden_on_v34/submission_q1_sleep_retrieval_meta.csv |
| q1_temporal_burden_knn_resid | 0.661651 | outputs/q1_temporal_burden_on_v34/oof_q1_temporal_burden_knn_resid.csv | outputs/q1_temporal_burden_on_v34/submission_q1_temporal_burden_knn_resid.csv |
| q1_temporal_burden_extra | 0.700882 | outputs/q1_temporal_burden_on_v34/oof_q1_temporal_burden_extra.csv | outputs/q1_temporal_burden_on_v34/submission_q1_temporal_burden_extra.csv |
| q1_temporal_burden_hgb | 0.701834 | outputs/q1_temporal_burden_on_v34/oof_q1_temporal_burden_hgb.csv | outputs/q1_temporal_burden_on_v34/submission_q1_temporal_burden_hgb.csv |
| q1_temporal_burden_knn_label | 0.731433 | outputs/q1_temporal_burden_on_v34/oof_q1_temporal_burden_knn_label.csv | outputs/q1_temporal_burden_on_v34/submission_q1_temporal_burden_knn_label.csv |
| q1_temporal_burden_proto | 0.759619 | outputs/q1_temporal_burden_on_v34/oof_q1_temporal_burden_proto.csv | outputs/q1_temporal_burden_on_v34/submission_q1_temporal_burden_proto.csv |
| q1_temporal_burden_knn_logitresid | 0.791413 | outputs/q1_temporal_burden_on_v34/oof_q1_temporal_burden_knn_logitresid.csv | outputs/q1_temporal_burden_on_v34/submission_q1_temporal_burden_knn_logitresid.csv |
| q1_temporal_burden_logreg | 0.952561 | outputs/q1_temporal_burden_on_v34/oof_q1_temporal_burden_logreg.csv | outputs/q1_temporal_burden_on_v34/submission_q1_temporal_burden_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_burden | 1232 |
