# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.564253`
- Best source Q3 OOF: `0.596027`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_temporal_acceleration_knn_resid | 0.596027 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_acceleration_knn_resid.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_acceleration_knn_resid.csv |
| q3_temporal_momentum_knn_resid | 0.607636 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_momentum_knn_resid.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_momentum_knn_resid.csv |
| q3_temporal_extreme_knn_resid | 0.611679 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_extreme_knn_resid.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_extreme_knn_resid.csv |
| q3_sleep_retrieval_meta | 0.613220 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_sleep_retrieval_meta.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_sleep_retrieval_meta.csv |
| q3_temporal_extreme_knn_logitresid | 0.662831 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_extreme_knn_logitresid.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_extreme_knn_logitresid.csv |
| q3_temporal_momentum_knn_logitresid | 0.672901 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_momentum_knn_logitresid.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_momentum_knn_logitresid.csv |
| q3_temporal_extreme_extra | 0.674377 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_extreme_extra.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_extreme_extra.csv |
| q3_temporal_extreme_hgb | 0.689001 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_extreme_hgb.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_extreme_hgb.csv |
| q3_temporal_acceleration_extra | 0.692803 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_acceleration_extra.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_acceleration_extra.csv |
| q3_temporal_acceleration_knn_logitresid | 0.696680 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_acceleration_knn_logitresid.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_acceleration_knn_logitresid.csv |
| q3_temporal_momentum_extra | 0.699236 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_momentum_extra.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_momentum_extra.csv |
| q3_temporal_extreme_knn_label | 0.711424 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_extreme_knn_label.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_extreme_knn_label.csv |
| q3_temporal_momentum_knn_label | 0.712606 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_momentum_knn_label.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_momentum_knn_label.csv |
| q3_temporal_extreme_proto | 0.730326 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_extreme_proto.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_extreme_proto.csv |
| q3_temporal_acceleration_hgb | 0.731204 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_acceleration_hgb.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_acceleration_hgb.csv |
| q3_temporal_acceleration_knn_label | 0.744869 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_acceleration_knn_label.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_acceleration_knn_label.csv |
| q3_temporal_momentum_hgb | 0.746621 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_momentum_hgb.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_momentum_hgb.csv |
| q3_temporal_acceleration_proto | 0.752090 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_acceleration_proto.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_acceleration_proto.csv |
| q3_temporal_momentum_proto | 0.794875 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_momentum_proto.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_momentum_proto.csv |
| q3_temporal_extreme_logreg | 0.795111 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_extreme_logreg.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_extreme_logreg.csv |
| q3_temporal_momentum_logreg | 0.892390 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_momentum_logreg.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_momentum_logreg.csv |
| q3_temporal_acceleration_logreg | 0.903222 | outputs/q3_temporal_shape_l2_on_v30/oof_q3_temporal_acceleration_logreg.csv | outputs/q3_temporal_shape_l2_on_v30/submission_q3_temporal_acceleration_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_momentum | 308 |
| temporal_extreme | 616 |
| temporal_acceleration | 616 |
