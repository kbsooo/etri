# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.597428`
- Best source Q2 OOF: `0.612174`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_sleep_retrieval_meta | 0.612174 | outputs/q2_temporal_shape_on_v29/oof_q2_sleep_retrieval_meta.csv | outputs/q2_temporal_shape_on_v29/submission_q2_sleep_retrieval_meta.csv |
| q2_temporal_extreme_knn_resid | 0.618423 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_extreme_knn_resid.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_extreme_knn_resid.csv |
| q2_temporal_momentum_knn_resid | 0.672079 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_momentum_knn_resid.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_momentum_knn_resid.csv |
| q2_temporal_extreme_knn_logitresid | 0.689797 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_extreme_knn_logitresid.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_extreme_knn_logitresid.csv |
| q2_temporal_momentum_extra | 0.699202 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_momentum_extra.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_momentum_extra.csv |
| q2_temporal_acceleration_knn_resid | 0.705992 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_acceleration_knn_resid.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_acceleration_knn_resid.csv |
| q2_temporal_extreme_knn_label | 0.706247 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_extreme_knn_label.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_extreme_knn_label.csv |
| q2_temporal_acceleration_extra | 0.707279 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_acceleration_extra.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_acceleration_extra.csv |
| q2_temporal_extreme_extra | 0.723244 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_extreme_extra.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_extreme_extra.csv |
| q2_temporal_momentum_knn_logitresid | 0.731532 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_momentum_knn_logitresid.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_momentum_knn_logitresid.csv |
| q2_temporal_momentum_hgb | 0.738896 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_momentum_hgb.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_momentum_hgb.csv |
| q2_temporal_momentum_knn_label | 0.739639 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_momentum_knn_label.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_momentum_knn_label.csv |
| q2_temporal_acceleration_hgb | 0.753605 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_acceleration_hgb.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_acceleration_hgb.csv |
| q2_temporal_acceleration_knn_label | 0.766041 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_acceleration_knn_label.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_acceleration_knn_label.csv |
| q2_temporal_extreme_hgb | 0.772664 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_extreme_hgb.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_extreme_hgb.csv |
| q2_temporal_acceleration_knn_logitresid | 0.783205 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_acceleration_knn_logitresid.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_acceleration_knn_logitresid.csv |
| q2_temporal_extreme_proto | 0.794609 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_extreme_proto.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_extreme_proto.csv |
| q2_temporal_momentum_proto | 0.814934 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_momentum_proto.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_momentum_proto.csv |
| q2_temporal_extreme_logreg | 0.829304 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_extreme_logreg.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_extreme_logreg.csv |
| q2_temporal_acceleration_proto | 0.885288 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_acceleration_proto.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_acceleration_proto.csv |
| q2_temporal_momentum_logreg | 0.962428 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_momentum_logreg.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_momentum_logreg.csv |
| q2_temporal_acceleration_logreg | 1.087620 | outputs/q2_temporal_shape_on_v29/oof_q2_temporal_acceleration_logreg.csv | outputs/q2_temporal_shape_on_v29/submission_q2_temporal_acceleration_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_acceleration | 616 |
| temporal_momentum | 308 |
| temporal_extreme | 616 |
