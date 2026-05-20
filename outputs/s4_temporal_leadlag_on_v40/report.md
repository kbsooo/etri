# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.510161`
- Best source S4 OOF: `0.538597`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_sleep_retrieval_meta | 0.538597 | outputs/s4_temporal_leadlag_on_v40/oof_s4_sleep_retrieval_meta.csv | outputs/s4_temporal_leadlag_on_v40/submission_s4_sleep_retrieval_meta.csv |
| s4_temporal_leadlag_knn_resid | 0.571721 | outputs/s4_temporal_leadlag_on_v40/oof_s4_temporal_leadlag_knn_resid.csv | outputs/s4_temporal_leadlag_on_v40/submission_s4_temporal_leadlag_knn_resid.csv |
| s4_temporal_leadlag_knn_logitresid | 0.626389 | outputs/s4_temporal_leadlag_on_v40/oof_s4_temporal_leadlag_knn_logitresid.csv | outputs/s4_temporal_leadlag_on_v40/submission_s4_temporal_leadlag_knn_logitresid.csv |
| s4_temporal_leadlag_extra | 0.685004 | outputs/s4_temporal_leadlag_on_v40/oof_s4_temporal_leadlag_extra.csv | outputs/s4_temporal_leadlag_on_v40/submission_s4_temporal_leadlag_extra.csv |
| s4_temporal_leadlag_hgb | 0.688728 | outputs/s4_temporal_leadlag_on_v40/oof_s4_temporal_leadlag_hgb.csv | outputs/s4_temporal_leadlag_on_v40/submission_s4_temporal_leadlag_hgb.csv |
| s4_temporal_leadlag_knn_label | 0.726639 | outputs/s4_temporal_leadlag_on_v40/oof_s4_temporal_leadlag_knn_label.csv | outputs/s4_temporal_leadlag_on_v40/submission_s4_temporal_leadlag_knn_label.csv |
| s4_temporal_leadlag_proto | 0.756143 | outputs/s4_temporal_leadlag_on_v40/oof_s4_temporal_leadlag_proto.csv | outputs/s4_temporal_leadlag_on_v40/submission_s4_temporal_leadlag_proto.csv |
| s4_temporal_leadlag_logreg | 0.899603 | outputs/s4_temporal_leadlag_on_v40/oof_s4_temporal_leadlag_logreg.csv | outputs/s4_temporal_leadlag_on_v40/submission_s4_temporal_leadlag_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_leadlag | 144 |
