# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.513798`
- Best source S1 OOF: `0.571128`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_sleep_retrieval_meta | 0.571128 | outputs/s1_temporal_burden_on_v34/oof_s1_sleep_retrieval_meta.csv | outputs/s1_temporal_burden_on_v34/submission_s1_sleep_retrieval_meta.csv |
| s1_temporal_burden_knn_resid | 0.614797 | outputs/s1_temporal_burden_on_v34/oof_s1_temporal_burden_knn_resid.csv | outputs/s1_temporal_burden_on_v34/submission_s1_temporal_burden_knn_resid.csv |
| s1_temporal_burden_hgb | 0.677444 | outputs/s1_temporal_burden_on_v34/oof_s1_temporal_burden_hgb.csv | outputs/s1_temporal_burden_on_v34/submission_s1_temporal_burden_hgb.csv |
| s1_temporal_burden_extra | 0.680315 | outputs/s1_temporal_burden_on_v34/oof_s1_temporal_burden_extra.csv | outputs/s1_temporal_burden_on_v34/submission_s1_temporal_burden_extra.csv |
| s1_temporal_burden_knn_label | 0.702480 | outputs/s1_temporal_burden_on_v34/oof_s1_temporal_burden_knn_label.csv | outputs/s1_temporal_burden_on_v34/submission_s1_temporal_burden_knn_label.csv |
| s1_temporal_burden_knn_logitresid | 0.707668 | outputs/s1_temporal_burden_on_v34/oof_s1_temporal_burden_knn_logitresid.csv | outputs/s1_temporal_burden_on_v34/submission_s1_temporal_burden_knn_logitresid.csv |
| s1_temporal_burden_proto | 0.731255 | outputs/s1_temporal_burden_on_v34/oof_s1_temporal_burden_proto.csv | outputs/s1_temporal_burden_on_v34/submission_s1_temporal_burden_proto.csv |
| s1_temporal_burden_logreg | 1.047476 | outputs/s1_temporal_burden_on_v34/oof_s1_temporal_burden_logreg.csv | outputs/s1_temporal_burden_on_v34/submission_s1_temporal_burden_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_burden | 1232 |
