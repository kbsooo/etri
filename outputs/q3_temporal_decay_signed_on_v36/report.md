# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.549837`
- Best source Q3 OOF: `0.575672`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_sleep_retrieval_meta | 0.575672 | outputs/q3_temporal_decay_signed_on_v36/oof_q3_sleep_retrieval_meta.csv | outputs/q3_temporal_decay_signed_on_v36/submission_q3_sleep_retrieval_meta.csv |
| q3_temporal_decay_knn_resid | 0.591917 | outputs/q3_temporal_decay_signed_on_v36/oof_q3_temporal_decay_knn_resid.csv | outputs/q3_temporal_decay_signed_on_v36/submission_q3_temporal_decay_knn_resid.csv |
| q3_temporal_signed_burden_knn_resid | 0.596900 | outputs/q3_temporal_decay_signed_on_v36/oof_q3_temporal_signed_burden_knn_resid.csv | outputs/q3_temporal_decay_signed_on_v36/submission_q3_temporal_signed_burden_knn_resid.csv |
| q3_temporal_decay_knn_logitresid | 0.635104 | outputs/q3_temporal_decay_signed_on_v36/oof_q3_temporal_decay_knn_logitresid.csv | outputs/q3_temporal_decay_signed_on_v36/submission_q3_temporal_decay_knn_logitresid.csv |
| q3_temporal_signed_burden_knn_logitresid | 0.645279 | outputs/q3_temporal_decay_signed_on_v36/oof_q3_temporal_signed_burden_knn_logitresid.csv | outputs/q3_temporal_decay_signed_on_v36/submission_q3_temporal_signed_burden_knn_logitresid.csv |
| q3_temporal_signed_burden_extra | 0.679489 | outputs/q3_temporal_decay_signed_on_v36/oof_q3_temporal_signed_burden_extra.csv | outputs/q3_temporal_decay_signed_on_v36/submission_q3_temporal_signed_burden_extra.csv |
| q3_temporal_signed_burden_hgb | 0.695179 | outputs/q3_temporal_decay_signed_on_v36/oof_q3_temporal_signed_burden_hgb.csv | outputs/q3_temporal_decay_signed_on_v36/submission_q3_temporal_signed_burden_hgb.csv |
| q3_temporal_decay_knn_label | 0.695269 | outputs/q3_temporal_decay_signed_on_v36/oof_q3_temporal_decay_knn_label.csv | outputs/q3_temporal_decay_signed_on_v36/submission_q3_temporal_decay_knn_label.csv |
| q3_temporal_decay_extra | 0.698830 | outputs/q3_temporal_decay_signed_on_v36/oof_q3_temporal_decay_extra.csv | outputs/q3_temporal_decay_signed_on_v36/submission_q3_temporal_decay_extra.csv |
| q3_temporal_decay_hgb | 0.717049 | outputs/q3_temporal_decay_signed_on_v36/oof_q3_temporal_decay_hgb.csv | outputs/q3_temporal_decay_signed_on_v36/submission_q3_temporal_decay_hgb.csv |
| q3_temporal_decay_proto | 0.766629 | outputs/q3_temporal_decay_signed_on_v36/oof_q3_temporal_decay_proto.csv | outputs/q3_temporal_decay_signed_on_v36/submission_q3_temporal_decay_proto.csv |
| q3_temporal_signed_burden_proto | 0.780752 | outputs/q3_temporal_decay_signed_on_v36/oof_q3_temporal_signed_burden_proto.csv | outputs/q3_temporal_decay_signed_on_v36/submission_q3_temporal_signed_burden_proto.csv |
| q3_temporal_signed_burden_knn_label | 0.781896 | outputs/q3_temporal_decay_signed_on_v36/oof_q3_temporal_signed_burden_knn_label.csv | outputs/q3_temporal_decay_signed_on_v36/submission_q3_temporal_signed_burden_knn_label.csv |
| q3_temporal_decay_logreg | 1.002950 | outputs/q3_temporal_decay_signed_on_v36/oof_q3_temporal_decay_logreg.csv | outputs/q3_temporal_decay_signed_on_v36/submission_q3_temporal_decay_logreg.csv |
| q3_temporal_signed_burden_logreg | 1.106115 | outputs/q3_temporal_decay_signed_on_v36/oof_q3_temporal_signed_burden_logreg.csv | outputs/q3_temporal_decay_signed_on_v36/submission_q3_temporal_signed_burden_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_signed_burden | 924 |
| temporal_decay | 1232 |
