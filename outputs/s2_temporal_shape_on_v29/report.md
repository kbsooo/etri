# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.497488`
- Best source S2 OOF: `0.545243`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_sleep_retrieval_meta | 0.545243 | outputs/s2_temporal_shape_on_v29/oof_s2_sleep_retrieval_meta.csv | outputs/s2_temporal_shape_on_v29/submission_s2_sleep_retrieval_meta.csv |
| s2_temporal_momentum_knn_resid | 0.545313 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_momentum_knn_resid.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_momentum_knn_resid.csv |
| s2_temporal_momentum_knn_logitresid | 0.551682 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_momentum_knn_logitresid.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_momentum_knn_logitresid.csv |
| s2_temporal_extreme_knn_resid | 0.588854 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_extreme_knn_resid.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_extreme_knn_resid.csv |
| s2_temporal_acceleration_knn_resid | 0.589601 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_acceleration_knn_resid.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_acceleration_knn_resid.csv |
| s2_temporal_extreme_knn_logitresid | 0.606582 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_extreme_knn_logitresid.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_extreme_knn_logitresid.csv |
| s2_temporal_momentum_hgb | 0.626015 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_momentum_hgb.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_momentum_hgb.csv |
| s2_temporal_extreme_hgb | 0.650304 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_extreme_hgb.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_extreme_hgb.csv |
| s2_temporal_acceleration_hgb | 0.668838 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_acceleration_hgb.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_acceleration_hgb.csv |
| s2_temporal_momentum_knn_label | 0.671449 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_momentum_knn_label.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_momentum_knn_label.csv |
| s2_temporal_momentum_extra | 0.673341 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_momentum_extra.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_momentum_extra.csv |
| s2_temporal_acceleration_knn_logitresid | 0.673713 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_acceleration_knn_logitresid.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_acceleration_knn_logitresid.csv |
| s2_temporal_acceleration_extra | 0.682755 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_acceleration_extra.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_acceleration_extra.csv |
| s2_temporal_momentum_proto | 0.696067 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_momentum_proto.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_momentum_proto.csv |
| s2_temporal_extreme_extra | 0.701692 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_extreme_extra.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_extreme_extra.csv |
| s2_temporal_acceleration_knn_label | 0.704167 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_acceleration_knn_label.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_acceleration_knn_label.csv |
| s2_temporal_extreme_knn_label | 0.723672 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_extreme_knn_label.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_extreme_knn_label.csv |
| s2_temporal_acceleration_proto | 0.737613 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_acceleration_proto.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_acceleration_proto.csv |
| s2_temporal_extreme_proto | 0.774722 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_extreme_proto.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_extreme_proto.csv |
| s2_temporal_momentum_logreg | 0.797662 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_momentum_logreg.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_momentum_logreg.csv |
| s2_temporal_extreme_logreg | 0.883618 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_extreme_logreg.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_extreme_logreg.csv |
| s2_temporal_acceleration_logreg | 0.904620 | outputs/s2_temporal_shape_on_v29/oof_s2_temporal_acceleration_logreg.csv | outputs/s2_temporal_shape_on_v29/submission_s2_temporal_acceleration_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_acceleration | 616 |
| temporal_momentum | 308 |
| temporal_extreme | 616 |
