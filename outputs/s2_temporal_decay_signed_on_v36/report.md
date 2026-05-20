# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.490029`
- Best source S2 OOF: `0.537029`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_sleep_retrieval_meta | 0.537029 | outputs/s2_temporal_decay_signed_on_v36/oof_s2_sleep_retrieval_meta.csv | outputs/s2_temporal_decay_signed_on_v36/submission_s2_sleep_retrieval_meta.csv |
| s2_temporal_decay_hgb | 0.638819 | outputs/s2_temporal_decay_signed_on_v36/oof_s2_temporal_decay_hgb.csv | outputs/s2_temporal_decay_signed_on_v36/submission_s2_temporal_decay_hgb.csv |
| s2_temporal_signed_burden_hgb | 0.652314 | outputs/s2_temporal_decay_signed_on_v36/oof_s2_temporal_signed_burden_hgb.csv | outputs/s2_temporal_decay_signed_on_v36/submission_s2_temporal_signed_burden_hgb.csv |
| s2_temporal_decay_extra | 0.670733 | outputs/s2_temporal_decay_signed_on_v36/oof_s2_temporal_decay_extra.csv | outputs/s2_temporal_decay_signed_on_v36/submission_s2_temporal_decay_extra.csv |
| s2_temporal_signed_burden_extra | 0.687866 | outputs/s2_temporal_decay_signed_on_v36/oof_s2_temporal_signed_burden_extra.csv | outputs/s2_temporal_decay_signed_on_v36/submission_s2_temporal_signed_burden_extra.csv |
| s2_temporal_decay_proto | 0.694625 | outputs/s2_temporal_decay_signed_on_v36/oof_s2_temporal_decay_proto.csv | outputs/s2_temporal_decay_signed_on_v36/submission_s2_temporal_decay_proto.csv |
| s2_temporal_signed_burden_knn_resid | 0.725399 | outputs/s2_temporal_decay_signed_on_v36/oof_s2_temporal_signed_burden_knn_resid.csv | outputs/s2_temporal_decay_signed_on_v36/submission_s2_temporal_signed_burden_knn_resid.csv |
| s2_temporal_decay_knn_logitresid | 0.728433 | outputs/s2_temporal_decay_signed_on_v36/oof_s2_temporal_decay_knn_logitresid.csv | outputs/s2_temporal_decay_signed_on_v36/submission_s2_temporal_decay_knn_logitresid.csv |
| s2_temporal_signed_burden_knn_logitresid | 0.746975 | outputs/s2_temporal_decay_signed_on_v36/oof_s2_temporal_signed_burden_knn_logitresid.csv | outputs/s2_temporal_decay_signed_on_v36/submission_s2_temporal_signed_burden_knn_logitresid.csv |
| s2_temporal_decay_knn_resid | 0.747117 | outputs/s2_temporal_decay_signed_on_v36/oof_s2_temporal_decay_knn_resid.csv | outputs/s2_temporal_decay_signed_on_v36/submission_s2_temporal_decay_knn_resid.csv |
| s2_temporal_signed_burden_proto | 0.748549 | outputs/s2_temporal_decay_signed_on_v36/oof_s2_temporal_signed_burden_proto.csv | outputs/s2_temporal_decay_signed_on_v36/submission_s2_temporal_signed_burden_proto.csv |
| s2_temporal_decay_knn_label | 0.754999 | outputs/s2_temporal_decay_signed_on_v36/oof_s2_temporal_decay_knn_label.csv | outputs/s2_temporal_decay_signed_on_v36/submission_s2_temporal_decay_knn_label.csv |
| s2_temporal_signed_burden_knn_label | 0.773592 | outputs/s2_temporal_decay_signed_on_v36/oof_s2_temporal_signed_burden_knn_label.csv | outputs/s2_temporal_decay_signed_on_v36/submission_s2_temporal_signed_burden_knn_label.csv |
| s2_temporal_decay_logreg | 0.916410 | outputs/s2_temporal_decay_signed_on_v36/oof_s2_temporal_decay_logreg.csv | outputs/s2_temporal_decay_signed_on_v36/submission_s2_temporal_decay_logreg.csv |
| s2_temporal_signed_burden_logreg | 0.982837 | outputs/s2_temporal_decay_signed_on_v36/oof_s2_temporal_signed_burden_logreg.csv | outputs/s2_temporal_decay_signed_on_v36/submission_s2_temporal_signed_burden_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_signed_burden | 924 |
| temporal_decay | 1232 |
