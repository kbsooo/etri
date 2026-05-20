# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.511588`
- Best source S1 OOF: `0.574257`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_sleep_retrieval_meta | 0.574257 | outputs/s1_temporal_decay_signed_on_v36/oof_s1_sleep_retrieval_meta.csv | outputs/s1_temporal_decay_signed_on_v36/submission_s1_sleep_retrieval_meta.csv |
| s1_temporal_signed_burden_knn_resid | 0.607627 | outputs/s1_temporal_decay_signed_on_v36/oof_s1_temporal_signed_burden_knn_resid.csv | outputs/s1_temporal_decay_signed_on_v36/submission_s1_temporal_signed_burden_knn_resid.csv |
| s1_temporal_decay_knn_resid | 0.617560 | outputs/s1_temporal_decay_signed_on_v36/oof_s1_temporal_decay_knn_resid.csv | outputs/s1_temporal_decay_signed_on_v36/submission_s1_temporal_decay_knn_resid.csv |
| s1_temporal_decay_hgb | 0.663452 | outputs/s1_temporal_decay_signed_on_v36/oof_s1_temporal_decay_hgb.csv | outputs/s1_temporal_decay_signed_on_v36/submission_s1_temporal_decay_hgb.csv |
| s1_temporal_decay_extra | 0.678433 | outputs/s1_temporal_decay_signed_on_v36/oof_s1_temporal_decay_extra.csv | outputs/s1_temporal_decay_signed_on_v36/submission_s1_temporal_decay_extra.csv |
| s1_temporal_signed_burden_extra | 0.687686 | outputs/s1_temporal_decay_signed_on_v36/oof_s1_temporal_signed_burden_extra.csv | outputs/s1_temporal_decay_signed_on_v36/submission_s1_temporal_signed_burden_extra.csv |
| s1_temporal_signed_burden_hgb | 0.700204 | outputs/s1_temporal_decay_signed_on_v36/oof_s1_temporal_signed_burden_hgb.csv | outputs/s1_temporal_decay_signed_on_v36/submission_s1_temporal_signed_burden_hgb.csv |
| s1_temporal_signed_burden_knn_logitresid | 0.712775 | outputs/s1_temporal_decay_signed_on_v36/oof_s1_temporal_signed_burden_knn_logitresid.csv | outputs/s1_temporal_decay_signed_on_v36/submission_s1_temporal_signed_burden_knn_logitresid.csv |
| s1_temporal_signed_burden_proto | 0.727076 | outputs/s1_temporal_decay_signed_on_v36/oof_s1_temporal_signed_burden_proto.csv | outputs/s1_temporal_decay_signed_on_v36/submission_s1_temporal_signed_burden_proto.csv |
| s1_temporal_decay_knn_logitresid | 0.730430 | outputs/s1_temporal_decay_signed_on_v36/oof_s1_temporal_decay_knn_logitresid.csv | outputs/s1_temporal_decay_signed_on_v36/submission_s1_temporal_decay_knn_logitresid.csv |
| s1_temporal_decay_proto | 0.734838 | outputs/s1_temporal_decay_signed_on_v36/oof_s1_temporal_decay_proto.csv | outputs/s1_temporal_decay_signed_on_v36/submission_s1_temporal_decay_proto.csv |
| s1_temporal_decay_knn_label | 0.771243 | outputs/s1_temporal_decay_signed_on_v36/oof_s1_temporal_decay_knn_label.csv | outputs/s1_temporal_decay_signed_on_v36/submission_s1_temporal_decay_knn_label.csv |
| s1_temporal_signed_burden_knn_label | 0.775289 | outputs/s1_temporal_decay_signed_on_v36/oof_s1_temporal_signed_burden_knn_label.csv | outputs/s1_temporal_decay_signed_on_v36/submission_s1_temporal_signed_burden_knn_label.csv |
| s1_temporal_decay_logreg | 1.083781 | outputs/s1_temporal_decay_signed_on_v36/oof_s1_temporal_decay_logreg.csv | outputs/s1_temporal_decay_signed_on_v36/submission_s1_temporal_decay_logreg.csv |
| s1_temporal_signed_burden_logreg | 1.185445 | outputs/s1_temporal_decay_signed_on_v36/oof_s1_temporal_signed_burden_logreg.csv | outputs/s1_temporal_decay_signed_on_v36/submission_s1_temporal_signed_burden_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_signed_burden | 924 |
| temporal_decay | 1232 |
