# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.477055`
- Best source S3 OOF: `0.492004`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_temporal_extreme_knn_resid | 0.492004 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_extreme_knn_resid.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_extreme_knn_resid.csv |
| s3_temporal_extreme_knn_logitresid | 0.510869 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_extreme_knn_logitresid.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_extreme_knn_logitresid.csv |
| s3_sleep_retrieval_meta | 0.516370 | outputs/s3_temporal_shape_on_v29/oof_s3_sleep_retrieval_meta.csv | outputs/s3_temporal_shape_on_v29/submission_s3_sleep_retrieval_meta.csv |
| s3_temporal_momentum_knn_resid | 0.518586 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_momentum_knn_resid.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_momentum_knn_resid.csv |
| s3_temporal_acceleration_knn_resid | 0.524537 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_acceleration_knn_resid.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_acceleration_knn_resid.csv |
| s3_temporal_acceleration_knn_logitresid | 0.532683 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_acceleration_knn_logitresid.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_acceleration_knn_logitresid.csv |
| s3_temporal_momentum_knn_logitresid | 0.539968 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_momentum_knn_logitresid.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_momentum_knn_logitresid.csv |
| s3_temporal_extreme_hgb | 0.581985 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_extreme_hgb.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_extreme_hgb.csv |
| s3_temporal_momentum_hgb | 0.616327 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_momentum_hgb.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_momentum_hgb.csv |
| s3_temporal_acceleration_hgb | 0.641067 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_acceleration_hgb.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_acceleration_hgb.csv |
| s3_temporal_acceleration_knn_label | 0.642758 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_acceleration_knn_label.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_acceleration_knn_label.csv |
| s3_temporal_momentum_knn_label | 0.661220 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_momentum_knn_label.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_momentum_knn_label.csv |
| s3_temporal_extreme_knn_label | 0.667216 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_extreme_knn_label.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_extreme_knn_label.csv |
| s3_temporal_acceleration_extra | 0.670168 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_acceleration_extra.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_acceleration_extra.csv |
| s3_temporal_extreme_extra | 0.673112 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_extreme_extra.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_extreme_extra.csv |
| s3_temporal_momentum_extra | 0.676516 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_momentum_extra.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_momentum_extra.csv |
| s3_temporal_acceleration_proto | 0.677174 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_acceleration_proto.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_acceleration_proto.csv |
| s3_temporal_extreme_proto | 0.717111 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_extreme_proto.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_extreme_proto.csv |
| s3_temporal_momentum_proto | 0.769890 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_momentum_proto.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_momentum_proto.csv |
| s3_temporal_extreme_logreg | 0.793806 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_extreme_logreg.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_extreme_logreg.csv |
| s3_temporal_acceleration_logreg | 0.842343 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_acceleration_logreg.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_acceleration_logreg.csv |
| s3_temporal_momentum_logreg | 0.874528 | outputs/s3_temporal_shape_on_v29/oof_s3_temporal_momentum_logreg.csv | outputs/s3_temporal_shape_on_v29/submission_s3_temporal_momentum_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_acceleration | 616 |
| temporal_momentum | 308 |
| temporal_extreme | 616 |
