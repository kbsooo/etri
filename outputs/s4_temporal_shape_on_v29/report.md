# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.553348`
- Best source S4 OOF: `0.557171`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_sleep_retrieval_meta | 0.557171 | outputs/s4_temporal_shape_on_v29/oof_s4_sleep_retrieval_meta.csv | outputs/s4_temporal_shape_on_v29/submission_s4_sleep_retrieval_meta.csv |
| s4_temporal_extreme_knn_resid | 0.619062 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_extreme_knn_resid.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_extreme_knn_resid.csv |
| s4_temporal_momentum_knn_resid | 0.631520 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_momentum_knn_resid.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_momentum_knn_resid.csv |
| s4_temporal_extreme_knn_logitresid | 0.666502 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_extreme_knn_logitresid.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_extreme_knn_logitresid.csv |
| s4_temporal_extreme_hgb | 0.670271 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_extreme_hgb.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_extreme_hgb.csv |
| s4_temporal_momentum_extra | 0.684383 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_momentum_extra.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_momentum_extra.csv |
| s4_temporal_extreme_extra | 0.686550 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_extreme_extra.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_extreme_extra.csv |
| s4_temporal_momentum_knn_logitresid | 0.691208 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_momentum_knn_logitresid.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_momentum_knn_logitresid.csv |
| s4_temporal_extreme_knn_label | 0.692990 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_extreme_knn_label.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_extreme_knn_label.csv |
| s4_temporal_acceleration_extra | 0.694514 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_acceleration_extra.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_acceleration_extra.csv |
| s4_temporal_acceleration_hgb | 0.697397 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_acceleration_hgb.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_acceleration_hgb.csv |
| s4_temporal_extreme_proto | 0.706521 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_extreme_proto.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_extreme_proto.csv |
| s4_temporal_momentum_hgb | 0.710840 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_momentum_hgb.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_momentum_hgb.csv |
| s4_temporal_acceleration_knn_resid | 0.712779 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_acceleration_knn_resid.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_acceleration_knn_resid.csv |
| s4_temporal_momentum_knn_label | 0.727417 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_momentum_knn_label.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_momentum_knn_label.csv |
| s4_temporal_acceleration_knn_label | 0.753124 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_acceleration_knn_label.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_acceleration_knn_label.csv |
| s4_temporal_acceleration_proto | 0.779467 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_acceleration_proto.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_acceleration_proto.csv |
| s4_temporal_extreme_logreg | 0.780062 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_extreme_logreg.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_extreme_logreg.csv |
| s4_temporal_momentum_proto | 0.783209 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_momentum_proto.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_momentum_proto.csv |
| s4_temporal_acceleration_knn_logitresid | 0.847629 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_acceleration_knn_logitresid.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_acceleration_knn_logitresid.csv |
| s4_temporal_momentum_logreg | 0.918805 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_momentum_logreg.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_momentum_logreg.csv |
| s4_temporal_acceleration_logreg | 0.926532 | outputs/s4_temporal_shape_on_v29/oof_s4_temporal_acceleration_logreg.csv | outputs/s4_temporal_shape_on_v29/submission_s4_temporal_acceleration_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_acceleration | 616 |
| temporal_momentum | 308 |
| temporal_extreme | 616 |
