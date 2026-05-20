# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.536553`
- Best source S4 OOF: `0.547337`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_sleep_retrieval_meta | 0.547337 | outputs/s4_temporal_burden_on_v34/oof_s4_sleep_retrieval_meta.csv | outputs/s4_temporal_burden_on_v34/submission_s4_sleep_retrieval_meta.csv |
| s4_temporal_burden_extra | 0.692877 | outputs/s4_temporal_burden_on_v34/oof_s4_temporal_burden_extra.csv | outputs/s4_temporal_burden_on_v34/submission_s4_temporal_burden_extra.csv |
| s4_temporal_burden_hgb | 0.696344 | outputs/s4_temporal_burden_on_v34/oof_s4_temporal_burden_hgb.csv | outputs/s4_temporal_burden_on_v34/submission_s4_temporal_burden_hgb.csv |
| s4_temporal_burden_knn_label | 0.726156 | outputs/s4_temporal_burden_on_v34/oof_s4_temporal_burden_knn_label.csv | outputs/s4_temporal_burden_on_v34/submission_s4_temporal_burden_knn_label.csv |
| s4_temporal_burden_proto | 0.733495 | outputs/s4_temporal_burden_on_v34/oof_s4_temporal_burden_proto.csv | outputs/s4_temporal_burden_on_v34/submission_s4_temporal_burden_proto.csv |
| s4_temporal_burden_knn_resid | 0.766815 | outputs/s4_temporal_burden_on_v34/oof_s4_temporal_burden_knn_resid.csv | outputs/s4_temporal_burden_on_v34/submission_s4_temporal_burden_knn_resid.csv |
| s4_temporal_burden_logreg | 0.819528 | outputs/s4_temporal_burden_on_v34/oof_s4_temporal_burden_logreg.csv | outputs/s4_temporal_burden_on_v34/submission_s4_temporal_burden_logreg.csv |
| s4_temporal_burden_knn_logitresid | 0.860736 | outputs/s4_temporal_burden_on_v34/oof_s4_temporal_burden_knn_logitresid.csv | outputs/s4_temporal_burden_on_v34/submission_s4_temporal_burden_knn_logitresid.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_burden | 1232 |
