# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.498491`
- Best source S1 OOF: `0.547834`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_temporal_leadlag_knn_resid | 0.547834 | outputs/s1_temporal_leadlag_l2_on_v42/oof_s1_temporal_leadlag_knn_resid.csv | outputs/s1_temporal_leadlag_l2_on_v42/submission_s1_temporal_leadlag_knn_resid.csv |
| s1_sleep_retrieval_meta | 0.571492 | outputs/s1_temporal_leadlag_l2_on_v42/oof_s1_sleep_retrieval_meta.csv | outputs/s1_temporal_leadlag_l2_on_v42/submission_s1_sleep_retrieval_meta.csv |
| s1_temporal_leadlag_knn_logitresid | 0.622062 | outputs/s1_temporal_leadlag_l2_on_v42/oof_s1_temporal_leadlag_knn_logitresid.csv | outputs/s1_temporal_leadlag_l2_on_v42/submission_s1_temporal_leadlag_knn_logitresid.csv |
| s1_temporal_leadlag_hgb | 0.627344 | outputs/s1_temporal_leadlag_l2_on_v42/oof_s1_temporal_leadlag_hgb.csv | outputs/s1_temporal_leadlag_l2_on_v42/submission_s1_temporal_leadlag_hgb.csv |
| s1_temporal_leadlag_knn_label | 0.652695 | outputs/s1_temporal_leadlag_l2_on_v42/oof_s1_temporal_leadlag_knn_label.csv | outputs/s1_temporal_leadlag_l2_on_v42/submission_s1_temporal_leadlag_knn_label.csv |
| s1_temporal_leadlag_extra | 0.672612 | outputs/s1_temporal_leadlag_l2_on_v42/oof_s1_temporal_leadlag_extra.csv | outputs/s1_temporal_leadlag_l2_on_v42/submission_s1_temporal_leadlag_extra.csv |
| s1_temporal_leadlag_proto | 0.713997 | outputs/s1_temporal_leadlag_l2_on_v42/oof_s1_temporal_leadlag_proto.csv | outputs/s1_temporal_leadlag_l2_on_v42/submission_s1_temporal_leadlag_proto.csv |
| s1_temporal_leadlag_logreg | 0.989525 | outputs/s1_temporal_leadlag_l2_on_v42/oof_s1_temporal_leadlag_logreg.csv | outputs/s1_temporal_leadlag_l2_on_v42/submission_s1_temporal_leadlag_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_leadlag | 144 |
