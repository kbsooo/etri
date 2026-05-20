# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.579150`
- Best source Q2 OOF: `0.596680`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_temporal_signed_burden_knn_resid | 0.596680 | outputs/q2_temporal_decay_signed_on_v36/oof_q2_temporal_signed_burden_knn_resid.csv | outputs/q2_temporal_decay_signed_on_v36/submission_q2_temporal_signed_burden_knn_resid.csv |
| q2_sleep_retrieval_meta | 0.616956 | outputs/q2_temporal_decay_signed_on_v36/oof_q2_sleep_retrieval_meta.csv | outputs/q2_temporal_decay_signed_on_v36/submission_q2_sleep_retrieval_meta.csv |
| q2_temporal_decay_knn_resid | 0.662225 | outputs/q2_temporal_decay_signed_on_v36/oof_q2_temporal_decay_knn_resid.csv | outputs/q2_temporal_decay_signed_on_v36/submission_q2_temporal_decay_knn_resid.csv |
| q2_temporal_signed_burden_knn_logitresid | 0.663604 | outputs/q2_temporal_decay_signed_on_v36/oof_q2_temporal_signed_burden_knn_logitresid.csv | outputs/q2_temporal_decay_signed_on_v36/submission_q2_temporal_signed_burden_knn_logitresid.csv |
| q2_temporal_signed_burden_extra | 0.696932 | outputs/q2_temporal_decay_signed_on_v36/oof_q2_temporal_signed_burden_extra.csv | outputs/q2_temporal_decay_signed_on_v36/submission_q2_temporal_signed_burden_extra.csv |
| q2_temporal_decay_extra | 0.704403 | outputs/q2_temporal_decay_signed_on_v36/oof_q2_temporal_decay_extra.csv | outputs/q2_temporal_decay_signed_on_v36/submission_q2_temporal_decay_extra.csv |
| q2_temporal_signed_burden_knn_label | 0.726534 | outputs/q2_temporal_decay_signed_on_v36/oof_q2_temporal_signed_burden_knn_label.csv | outputs/q2_temporal_decay_signed_on_v36/submission_q2_temporal_signed_burden_knn_label.csv |
| q2_temporal_decay_knn_logitresid | 0.736651 | outputs/q2_temporal_decay_signed_on_v36/oof_q2_temporal_decay_knn_logitresid.csv | outputs/q2_temporal_decay_signed_on_v36/submission_q2_temporal_decay_knn_logitresid.csv |
| q2_temporal_signed_burden_hgb | 0.747868 | outputs/q2_temporal_decay_signed_on_v36/oof_q2_temporal_signed_burden_hgb.csv | outputs/q2_temporal_decay_signed_on_v36/submission_q2_temporal_signed_burden_hgb.csv |
| q2_temporal_decay_knn_label | 0.750806 | outputs/q2_temporal_decay_signed_on_v36/oof_q2_temporal_decay_knn_label.csv | outputs/q2_temporal_decay_signed_on_v36/submission_q2_temporal_decay_knn_label.csv |
| q2_temporal_decay_hgb | 0.764362 | outputs/q2_temporal_decay_signed_on_v36/oof_q2_temporal_decay_hgb.csv | outputs/q2_temporal_decay_signed_on_v36/submission_q2_temporal_decay_hgb.csv |
| q2_temporal_decay_proto | 0.777535 | outputs/q2_temporal_decay_signed_on_v36/oof_q2_temporal_decay_proto.csv | outputs/q2_temporal_decay_signed_on_v36/submission_q2_temporal_decay_proto.csv |
| q2_temporal_signed_burden_proto | 0.819644 | outputs/q2_temporal_decay_signed_on_v36/oof_q2_temporal_signed_burden_proto.csv | outputs/q2_temporal_decay_signed_on_v36/submission_q2_temporal_signed_burden_proto.csv |
| q2_temporal_decay_logreg | 1.103127 | outputs/q2_temporal_decay_signed_on_v36/oof_q2_temporal_decay_logreg.csv | outputs/q2_temporal_decay_signed_on_v36/submission_q2_temporal_decay_logreg.csv |
| q2_temporal_signed_burden_logreg | 1.211997 | outputs/q2_temporal_decay_signed_on_v36/oof_q2_temporal_signed_burden_logreg.csv | outputs/q2_temporal_decay_signed_on_v36/submission_q2_temporal_signed_burden_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_signed_burden | 924 |
| temporal_decay | 1232 |
