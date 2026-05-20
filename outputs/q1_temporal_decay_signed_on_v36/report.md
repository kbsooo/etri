# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.565555`
- Best source Q1 OOF: `0.570058`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.570058 | outputs/q1_temporal_decay_signed_on_v36/oof_q1_sleep_retrieval_meta.csv | outputs/q1_temporal_decay_signed_on_v36/submission_q1_sleep_retrieval_meta.csv |
| q1_temporal_signed_burden_knn_resid | 0.689117 | outputs/q1_temporal_decay_signed_on_v36/oof_q1_temporal_signed_burden_knn_resid.csv | outputs/q1_temporal_decay_signed_on_v36/submission_q1_temporal_signed_burden_knn_resid.csv |
| q1_temporal_decay_extra | 0.692780 | outputs/q1_temporal_decay_signed_on_v36/oof_q1_temporal_decay_extra.csv | outputs/q1_temporal_decay_signed_on_v36/submission_q1_temporal_decay_extra.csv |
| q1_temporal_signed_burden_extra | 0.696553 | outputs/q1_temporal_decay_signed_on_v36/oof_q1_temporal_signed_burden_extra.csv | outputs/q1_temporal_decay_signed_on_v36/submission_q1_temporal_signed_burden_extra.csv |
| q1_temporal_decay_hgb | 0.710607 | outputs/q1_temporal_decay_signed_on_v36/oof_q1_temporal_decay_hgb.csv | outputs/q1_temporal_decay_signed_on_v36/submission_q1_temporal_decay_hgb.csv |
| q1_temporal_decay_knn_resid | 0.719033 | outputs/q1_temporal_decay_signed_on_v36/oof_q1_temporal_decay_knn_resid.csv | outputs/q1_temporal_decay_signed_on_v36/submission_q1_temporal_decay_knn_resid.csv |
| q1_temporal_signed_burden_hgb | 0.721323 | outputs/q1_temporal_decay_signed_on_v36/oof_q1_temporal_signed_burden_hgb.csv | outputs/q1_temporal_decay_signed_on_v36/submission_q1_temporal_signed_burden_hgb.csv |
| q1_temporal_signed_burden_knn_label | 0.765778 | outputs/q1_temporal_decay_signed_on_v36/oof_q1_temporal_signed_burden_knn_label.csv | outputs/q1_temporal_decay_signed_on_v36/submission_q1_temporal_signed_burden_knn_label.csv |
| q1_temporal_signed_burden_proto | 0.767031 | outputs/q1_temporal_decay_signed_on_v36/oof_q1_temporal_signed_burden_proto.csv | outputs/q1_temporal_decay_signed_on_v36/submission_q1_temporal_signed_burden_proto.csv |
| q1_temporal_decay_proto | 0.772005 | outputs/q1_temporal_decay_signed_on_v36/oof_q1_temporal_decay_proto.csv | outputs/q1_temporal_decay_signed_on_v36/submission_q1_temporal_decay_proto.csv |
| q1_temporal_decay_knn_label | 0.789963 | outputs/q1_temporal_decay_signed_on_v36/oof_q1_temporal_decay_knn_label.csv | outputs/q1_temporal_decay_signed_on_v36/submission_q1_temporal_decay_knn_label.csv |
| q1_temporal_signed_burden_knn_logitresid | 0.855926 | outputs/q1_temporal_decay_signed_on_v36/oof_q1_temporal_signed_burden_knn_logitresid.csv | outputs/q1_temporal_decay_signed_on_v36/submission_q1_temporal_signed_burden_knn_logitresid.csv |
| q1_temporal_decay_knn_logitresid | 0.883715 | outputs/q1_temporal_decay_signed_on_v36/oof_q1_temporal_decay_knn_logitresid.csv | outputs/q1_temporal_decay_signed_on_v36/submission_q1_temporal_decay_knn_logitresid.csv |
| q1_temporal_signed_burden_logreg | 1.023508 | outputs/q1_temporal_decay_signed_on_v36/oof_q1_temporal_signed_burden_logreg.csv | outputs/q1_temporal_decay_signed_on_v36/submission_q1_temporal_signed_burden_logreg.csv |
| q1_temporal_decay_logreg | 1.191036 | outputs/q1_temporal_decay_signed_on_v36/oof_q1_temporal_decay_logreg.csv | outputs/q1_temporal_decay_signed_on_v36/submission_q1_temporal_decay_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_signed_burden | 924 |
| temporal_decay | 1232 |
