# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.555379`
- Best source Q1 OOF: `0.567123`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.567123 | outputs/q1_temporal_leadlag_on_v40/oof_q1_sleep_retrieval_meta.csv | outputs/q1_temporal_leadlag_on_v40/submission_q1_sleep_retrieval_meta.csv |
| q1_temporal_leadlag_knn_resid | 0.570666 | outputs/q1_temporal_leadlag_on_v40/oof_q1_temporal_leadlag_knn_resid.csv | outputs/q1_temporal_leadlag_on_v40/submission_q1_temporal_leadlag_knn_resid.csv |
| q1_temporal_leadlag_knn_logitresid | 0.622161 | outputs/q1_temporal_leadlag_on_v40/oof_q1_temporal_leadlag_knn_logitresid.csv | outputs/q1_temporal_leadlag_on_v40/submission_q1_temporal_leadlag_knn_logitresid.csv |
| q1_temporal_leadlag_extra | 0.687258 | outputs/q1_temporal_leadlag_on_v40/oof_q1_temporal_leadlag_extra.csv | outputs/q1_temporal_leadlag_on_v40/submission_q1_temporal_leadlag_extra.csv |
| q1_temporal_leadlag_knn_label | 0.711383 | outputs/q1_temporal_leadlag_on_v40/oof_q1_temporal_leadlag_knn_label.csv | outputs/q1_temporal_leadlag_on_v40/submission_q1_temporal_leadlag_knn_label.csv |
| q1_temporal_leadlag_hgb | 0.726112 | outputs/q1_temporal_leadlag_on_v40/oof_q1_temporal_leadlag_hgb.csv | outputs/q1_temporal_leadlag_on_v40/submission_q1_temporal_leadlag_hgb.csv |
| q1_temporal_leadlag_proto | 0.758872 | outputs/q1_temporal_leadlag_on_v40/oof_q1_temporal_leadlag_proto.csv | outputs/q1_temporal_leadlag_on_v40/submission_q1_temporal_leadlag_proto.csv |
| q1_temporal_leadlag_logreg | 0.839986 | outputs/q1_temporal_leadlag_on_v40/oof_q1_temporal_leadlag_logreg.csv | outputs/q1_temporal_leadlag_on_v40/submission_q1_temporal_leadlag_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_leadlag | 144 |
