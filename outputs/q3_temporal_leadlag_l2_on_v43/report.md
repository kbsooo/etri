# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.541882`
- Best source Q3 OOF: `0.570080`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_sleep_retrieval_meta | 0.570080 | outputs/q3_temporal_leadlag_l2_on_v43/oof_q3_sleep_retrieval_meta.csv | outputs/q3_temporal_leadlag_l2_on_v43/submission_q3_sleep_retrieval_meta.csv |
| q3_temporal_leadlag_knn_resid | 0.582025 | outputs/q3_temporal_leadlag_l2_on_v43/oof_q3_temporal_leadlag_knn_resid.csv | outputs/q3_temporal_leadlag_l2_on_v43/submission_q3_temporal_leadlag_knn_resid.csv |
| q3_temporal_leadlag_knn_logitresid | 0.643611 | outputs/q3_temporal_leadlag_l2_on_v43/oof_q3_temporal_leadlag_knn_logitresid.csv | outputs/q3_temporal_leadlag_l2_on_v43/submission_q3_temporal_leadlag_knn_logitresid.csv |
| q3_temporal_leadlag_extra | 0.688991 | outputs/q3_temporal_leadlag_l2_on_v43/oof_q3_temporal_leadlag_extra.csv | outputs/q3_temporal_leadlag_l2_on_v43/submission_q3_temporal_leadlag_extra.csv |
| q3_temporal_leadlag_hgb | 0.698751 | outputs/q3_temporal_leadlag_l2_on_v43/oof_q3_temporal_leadlag_hgb.csv | outputs/q3_temporal_leadlag_l2_on_v43/submission_q3_temporal_leadlag_hgb.csv |
| q3_temporal_leadlag_knn_label | 0.701500 | outputs/q3_temporal_leadlag_l2_on_v43/oof_q3_temporal_leadlag_knn_label.csv | outputs/q3_temporal_leadlag_l2_on_v43/submission_q3_temporal_leadlag_knn_label.csv |
| q3_temporal_leadlag_proto | 0.749756 | outputs/q3_temporal_leadlag_l2_on_v43/oof_q3_temporal_leadlag_proto.csv | outputs/q3_temporal_leadlag_l2_on_v43/submission_q3_temporal_leadlag_proto.csv |
| q3_temporal_leadlag_logreg | 0.901718 | outputs/q3_temporal_leadlag_l2_on_v43/oof_q3_temporal_leadlag_logreg.csv | outputs/q3_temporal_leadlag_l2_on_v43/submission_q3_temporal_leadlag_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_leadlag | 144 |
