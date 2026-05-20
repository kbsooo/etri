# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.490182`
- Best source S2 OOF: `0.557792`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_sleep_retrieval_meta | 0.557792 | outputs/s2_temporal_burden_on_v34/oof_s2_sleep_retrieval_meta.csv | outputs/s2_temporal_burden_on_v34/submission_s2_sleep_retrieval_meta.csv |
| s2_temporal_burden_hgb | 0.630849 | outputs/s2_temporal_burden_on_v34/oof_s2_temporal_burden_hgb.csv | outputs/s2_temporal_burden_on_v34/submission_s2_temporal_burden_hgb.csv |
| s2_temporal_burden_extra | 0.646002 | outputs/s2_temporal_burden_on_v34/oof_s2_temporal_burden_extra.csv | outputs/s2_temporal_burden_on_v34/submission_s2_temporal_burden_extra.csv |
| s2_temporal_burden_knn_resid | 0.696174 | outputs/s2_temporal_burden_on_v34/oof_s2_temporal_burden_knn_resid.csv | outputs/s2_temporal_burden_on_v34/submission_s2_temporal_burden_knn_resid.csv |
| s2_temporal_burden_knn_logitresid | 0.737734 | outputs/s2_temporal_burden_on_v34/oof_s2_temporal_burden_knn_logitresid.csv | outputs/s2_temporal_burden_on_v34/submission_s2_temporal_burden_knn_logitresid.csv |
| s2_temporal_burden_knn_label | 0.739962 | outputs/s2_temporal_burden_on_v34/oof_s2_temporal_burden_knn_label.csv | outputs/s2_temporal_burden_on_v34/submission_s2_temporal_burden_knn_label.csv |
| s2_temporal_burden_proto | 0.742371 | outputs/s2_temporal_burden_on_v34/oof_s2_temporal_burden_proto.csv | outputs/s2_temporal_burden_on_v34/submission_s2_temporal_burden_proto.csv |
| s2_temporal_burden_logreg | 0.845021 | outputs/s2_temporal_burden_on_v34/oof_s2_temporal_burden_logreg.csv | outputs/s2_temporal_burden_on_v34/submission_s2_temporal_burden_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_burden | 1232 |
