# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.576137`
- Best source Q1 OOF: `0.598796`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.598796 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_sleep_retrieval_meta.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_sleep_retrieval_meta.csv |
| q1_temporal_momentum_knn_resid | 0.639485 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_momentum_knn_resid.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_momentum_knn_resid.csv |
| q1_temporal_extreme_knn_resid | 0.651841 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_extreme_knn_resid.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_extreme_knn_resid.csv |
| q1_temporal_acceleration_knn_resid | 0.659972 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_acceleration_knn_resid.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_acceleration_knn_resid.csv |
| q1_temporal_acceleration_extra | 0.682364 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_acceleration_extra.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_acceleration_extra.csv |
| q1_temporal_extreme_extra | 0.699537 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_extreme_extra.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_extreme_extra.csv |
| q1_temporal_momentum_extra | 0.701679 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_momentum_extra.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_momentum_extra.csv |
| q1_temporal_acceleration_hgb | 0.713846 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_acceleration_hgb.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_acceleration_hgb.csv |
| q1_temporal_extreme_hgb | 0.723390 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_extreme_hgb.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_extreme_hgb.csv |
| q1_temporal_momentum_hgb | 0.735347 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_momentum_hgb.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_momentum_hgb.csv |
| q1_temporal_acceleration_proto | 0.751111 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_acceleration_proto.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_acceleration_proto.csv |
| q1_temporal_acceleration_knn_label | 0.751877 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_acceleration_knn_label.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_acceleration_knn_label.csv |
| q1_temporal_momentum_knn_logitresid | 0.775133 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_momentum_knn_logitresid.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_momentum_knn_logitresid.csv |
| q1_temporal_momentum_proto | 0.779044 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_momentum_proto.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_momentum_proto.csv |
| q1_temporal_extreme_proto | 0.796646 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_extreme_proto.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_extreme_proto.csv |
| q1_temporal_acceleration_knn_logitresid | 0.800135 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_acceleration_knn_logitresid.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_acceleration_knn_logitresid.csv |
| q1_temporal_extreme_knn_logitresid | 0.806341 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_extreme_knn_logitresid.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_extreme_knn_logitresid.csv |
| q1_temporal_momentum_knn_label | 0.810871 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_momentum_knn_label.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_momentum_knn_label.csv |
| q1_temporal_extreme_knn_label | 0.839357 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_extreme_knn_label.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_extreme_knn_label.csv |
| q1_temporal_momentum_logreg | 0.866395 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_momentum_logreg.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_momentum_logreg.csv |
| q1_temporal_extreme_logreg | 0.870826 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_extreme_logreg.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_extreme_logreg.csv |
| q1_temporal_acceleration_logreg | 0.948134 | outputs/q1_temporal_shape_l2_on_v30/oof_q1_temporal_acceleration_logreg.csv | outputs/q1_temporal_shape_l2_on_v30/submission_q1_temporal_acceleration_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_momentum | 308 |
| temporal_extreme | 616 |
| temporal_acceleration | 616 |
