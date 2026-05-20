# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.581046`
- Best source Q2 OOF: `0.599762`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_sleep_retrieval_meta | 0.599762 | outputs/q2_temporal_burden_on_v34/oof_q2_sleep_retrieval_meta.csv | outputs/q2_temporal_burden_on_v34/submission_q2_sleep_retrieval_meta.csv |
| q2_temporal_burden_knn_resid | 0.654075 | outputs/q2_temporal_burden_on_v34/oof_q2_temporal_burden_knn_resid.csv | outputs/q2_temporal_burden_on_v34/submission_q2_temporal_burden_knn_resid.csv |
| q2_temporal_burden_extra | 0.712591 | outputs/q2_temporal_burden_on_v34/oof_q2_temporal_burden_extra.csv | outputs/q2_temporal_burden_on_v34/submission_q2_temporal_burden_extra.csv |
| q2_temporal_burden_knn_logitresid | 0.718672 | outputs/q2_temporal_burden_on_v34/oof_q2_temporal_burden_knn_logitresid.csv | outputs/q2_temporal_burden_on_v34/submission_q2_temporal_burden_knn_logitresid.csv |
| q2_temporal_burden_knn_label | 0.733591 | outputs/q2_temporal_burden_on_v34/oof_q2_temporal_burden_knn_label.csv | outputs/q2_temporal_burden_on_v34/submission_q2_temporal_burden_knn_label.csv |
| q2_temporal_burden_hgb | 0.752518 | outputs/q2_temporal_burden_on_v34/oof_q2_temporal_burden_hgb.csv | outputs/q2_temporal_burden_on_v34/submission_q2_temporal_burden_hgb.csv |
| q2_temporal_burden_proto | 0.829047 | outputs/q2_temporal_burden_on_v34/oof_q2_temporal_burden_proto.csv | outputs/q2_temporal_burden_on_v34/submission_q2_temporal_burden_proto.csv |
| q2_temporal_burden_logreg | 1.061607 | outputs/q2_temporal_burden_on_v34/oof_q2_temporal_burden_logreg.csv | outputs/q2_temporal_burden_on_v34/submission_q2_temporal_burden_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_burden | 1232 |
