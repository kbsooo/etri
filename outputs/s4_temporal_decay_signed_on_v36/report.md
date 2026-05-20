# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.531811`
- Best source S4 OOF: `0.564940`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_sleep_retrieval_meta | 0.564940 | outputs/s4_temporal_decay_signed_on_v36/oof_s4_sleep_retrieval_meta.csv | outputs/s4_temporal_decay_signed_on_v36/submission_s4_sleep_retrieval_meta.csv |
| s4_temporal_decay_hgb | 0.668868 | outputs/s4_temporal_decay_signed_on_v36/oof_s4_temporal_decay_hgb.csv | outputs/s4_temporal_decay_signed_on_v36/submission_s4_temporal_decay_hgb.csv |
| s4_temporal_decay_extra | 0.670134 | outputs/s4_temporal_decay_signed_on_v36/oof_s4_temporal_decay_extra.csv | outputs/s4_temporal_decay_signed_on_v36/submission_s4_temporal_decay_extra.csv |
| s4_temporal_signed_burden_extra | 0.687534 | outputs/s4_temporal_decay_signed_on_v36/oof_s4_temporal_signed_burden_extra.csv | outputs/s4_temporal_decay_signed_on_v36/submission_s4_temporal_signed_burden_extra.csv |
| s4_temporal_signed_burden_hgb | 0.715980 | outputs/s4_temporal_decay_signed_on_v36/oof_s4_temporal_signed_burden_hgb.csv | outputs/s4_temporal_decay_signed_on_v36/submission_s4_temporal_signed_burden_hgb.csv |
| s4_temporal_decay_knn_resid | 0.718303 | outputs/s4_temporal_decay_signed_on_v36/oof_s4_temporal_decay_knn_resid.csv | outputs/s4_temporal_decay_signed_on_v36/submission_s4_temporal_decay_knn_resid.csv |
| s4_temporal_decay_knn_label | 0.738808 | outputs/s4_temporal_decay_signed_on_v36/oof_s4_temporal_decay_knn_label.csv | outputs/s4_temporal_decay_signed_on_v36/submission_s4_temporal_decay_knn_label.csv |
| s4_temporal_decay_proto | 0.740708 | outputs/s4_temporal_decay_signed_on_v36/oof_s4_temporal_decay_proto.csv | outputs/s4_temporal_decay_signed_on_v36/submission_s4_temporal_decay_proto.csv |
| s4_temporal_signed_burden_knn_label | 0.762728 | outputs/s4_temporal_decay_signed_on_v36/oof_s4_temporal_signed_burden_knn_label.csv | outputs/s4_temporal_decay_signed_on_v36/submission_s4_temporal_signed_burden_knn_label.csv |
| s4_temporal_signed_burden_proto | 0.767972 | outputs/s4_temporal_decay_signed_on_v36/oof_s4_temporal_signed_burden_proto.csv | outputs/s4_temporal_decay_signed_on_v36/submission_s4_temporal_signed_burden_proto.csv |
| s4_temporal_signed_burden_knn_resid | 0.784102 | outputs/s4_temporal_decay_signed_on_v36/oof_s4_temporal_signed_burden_knn_resid.csv | outputs/s4_temporal_decay_signed_on_v36/submission_s4_temporal_signed_burden_knn_resid.csv |
| s4_temporal_decay_knn_logitresid | 0.828078 | outputs/s4_temporal_decay_signed_on_v36/oof_s4_temporal_decay_knn_logitresid.csv | outputs/s4_temporal_decay_signed_on_v36/submission_s4_temporal_decay_knn_logitresid.csv |
| s4_temporal_signed_burden_knn_logitresid | 0.868575 | outputs/s4_temporal_decay_signed_on_v36/oof_s4_temporal_signed_burden_knn_logitresid.csv | outputs/s4_temporal_decay_signed_on_v36/submission_s4_temporal_signed_burden_knn_logitresid.csv |
| s4_temporal_signed_burden_logreg | 0.974191 | outputs/s4_temporal_decay_signed_on_v36/oof_s4_temporal_signed_burden_logreg.csv | outputs/s4_temporal_decay_signed_on_v36/submission_s4_temporal_signed_burden_logreg.csv |
| s4_temporal_decay_logreg | 0.999407 | outputs/s4_temporal_decay_signed_on_v36/oof_s4_temporal_decay_logreg.csv | outputs/s4_temporal_decay_signed_on_v36/submission_s4_temporal_decay_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_signed_burden | 924 |
| temporal_decay | 1232 |
