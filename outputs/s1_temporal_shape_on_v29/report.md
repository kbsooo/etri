# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.523509`
- Best source S1 OOF: `0.544982`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_temporal_momentum_knn_resid | 0.544982 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_momentum_knn_resid.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_momentum_knn_resid.csv |
| s1_temporal_extreme_knn_resid | 0.563437 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_extreme_knn_resid.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_extreme_knn_resid.csv |
| s1_temporal_acceleration_knn_resid | 0.581625 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_acceleration_knn_resid.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_acceleration_knn_resid.csv |
| s1_temporal_extreme_knn_logitresid | 0.594874 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_extreme_knn_logitresid.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_extreme_knn_logitresid.csv |
| s1_temporal_momentum_knn_logitresid | 0.598970 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_momentum_knn_logitresid.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_momentum_knn_logitresid.csv |
| s1_sleep_retrieval_meta | 0.600485 | outputs/s1_temporal_shape_on_v29/oof_s1_sleep_retrieval_meta.csv | outputs/s1_temporal_shape_on_v29/submission_s1_sleep_retrieval_meta.csv |
| s1_temporal_momentum_knn_label | 0.638866 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_momentum_knn_label.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_momentum_knn_label.csv |
| s1_temporal_extreme_hgb | 0.639361 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_extreme_hgb.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_extreme_hgb.csv |
| s1_temporal_acceleration_knn_logitresid | 0.644813 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_acceleration_knn_logitresid.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_acceleration_knn_logitresid.csv |
| s1_temporal_momentum_hgb | 0.651944 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_momentum_hgb.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_momentum_hgb.csv |
| s1_temporal_extreme_knn_label | 0.661760 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_extreme_knn_label.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_extreme_knn_label.csv |
| s1_temporal_acceleration_knn_label | 0.667407 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_acceleration_knn_label.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_acceleration_knn_label.csv |
| s1_temporal_momentum_extra | 0.675217 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_momentum_extra.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_momentum_extra.csv |
| s1_temporal_acceleration_hgb | 0.675725 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_acceleration_hgb.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_acceleration_hgb.csv |
| s1_temporal_momentum_proto | 0.676743 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_momentum_proto.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_momentum_proto.csv |
| s1_temporal_extreme_extra | 0.679400 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_extreme_extra.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_extreme_extra.csv |
| s1_temporal_acceleration_extra | 0.694420 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_acceleration_extra.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_acceleration_extra.csv |
| s1_temporal_acceleration_proto | 0.721336 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_acceleration_proto.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_acceleration_proto.csv |
| s1_temporal_extreme_proto | 0.731381 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_extreme_proto.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_extreme_proto.csv |
| s1_temporal_extreme_logreg | 0.835485 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_extreme_logreg.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_extreme_logreg.csv |
| s1_temporal_momentum_logreg | 0.930605 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_momentum_logreg.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_momentum_logreg.csv |
| s1_temporal_acceleration_logreg | 0.992179 | outputs/s1_temporal_shape_on_v29/oof_s1_temporal_acceleration_logreg.csv | outputs/s1_temporal_shape_on_v29/submission_s1_temporal_acceleration_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_acceleration | 616 |
| temporal_momentum | 308 |
| temporal_extreme | 616 |
