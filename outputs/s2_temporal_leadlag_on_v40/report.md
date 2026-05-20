# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.488554`
- Best source S2 OOF: `0.524490`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_temporal_leadlag_knn_resid | 0.524490 | outputs/s2_temporal_leadlag_on_v40/oof_s2_temporal_leadlag_knn_resid.csv | outputs/s2_temporal_leadlag_on_v40/submission_s2_temporal_leadlag_knn_resid.csv |
| s2_sleep_retrieval_meta | 0.527357 | outputs/s2_temporal_leadlag_on_v40/oof_s2_sleep_retrieval_meta.csv | outputs/s2_temporal_leadlag_on_v40/submission_s2_sleep_retrieval_meta.csv |
| s2_temporal_leadlag_knn_logitresid | 0.593689 | outputs/s2_temporal_leadlag_on_v40/oof_s2_temporal_leadlag_knn_logitresid.csv | outputs/s2_temporal_leadlag_on_v40/submission_s2_temporal_leadlag_knn_logitresid.csv |
| s2_temporal_leadlag_hgb | 0.675028 | outputs/s2_temporal_leadlag_on_v40/oof_s2_temporal_leadlag_hgb.csv | outputs/s2_temporal_leadlag_on_v40/submission_s2_temporal_leadlag_hgb.csv |
| s2_temporal_leadlag_extra | 0.678409 | outputs/s2_temporal_leadlag_on_v40/oof_s2_temporal_leadlag_extra.csv | outputs/s2_temporal_leadlag_on_v40/submission_s2_temporal_leadlag_extra.csv |
| s2_temporal_leadlag_knn_label | 0.703782 | outputs/s2_temporal_leadlag_on_v40/oof_s2_temporal_leadlag_knn_label.csv | outputs/s2_temporal_leadlag_on_v40/submission_s2_temporal_leadlag_knn_label.csv |
| s2_temporal_leadlag_proto | 0.719562 | outputs/s2_temporal_leadlag_on_v40/oof_s2_temporal_leadlag_proto.csv | outputs/s2_temporal_leadlag_on_v40/submission_s2_temporal_leadlag_proto.csv |
| s2_temporal_leadlag_logreg | 0.924481 | outputs/s2_temporal_leadlag_on_v40/oof_s2_temporal_leadlag_logreg.csv | outputs/s2_temporal_leadlag_on_v40/submission_s2_temporal_leadlag_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_leadlag | 144 |
