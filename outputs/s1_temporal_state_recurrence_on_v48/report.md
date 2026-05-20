# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.498505`
- Best source S1 OOF: `0.547540`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_sleep_retrieval_meta | 0.547540 | outputs/s1_temporal_state_recurrence_on_v48/oof_s1_sleep_retrieval_meta.csv | outputs/s1_temporal_state_recurrence_on_v48/submission_s1_sleep_retrieval_meta.csv |
| s1_temporal_state_recurrence_knn_resid | 0.583095 | outputs/s1_temporal_state_recurrence_on_v48/oof_s1_temporal_state_recurrence_knn_resid.csv | outputs/s1_temporal_state_recurrence_on_v48/submission_s1_temporal_state_recurrence_knn_resid.csv |
| s1_temporal_state_recurrence_hgb | 0.602090 | outputs/s1_temporal_state_recurrence_on_v48/oof_s1_temporal_state_recurrence_hgb.csv | outputs/s1_temporal_state_recurrence_on_v48/submission_s1_temporal_state_recurrence_hgb.csv |
| s1_temporal_state_recurrence_knn_logitresid | 0.621978 | outputs/s1_temporal_state_recurrence_on_v48/oof_s1_temporal_state_recurrence_knn_logitresid.csv | outputs/s1_temporal_state_recurrence_on_v48/submission_s1_temporal_state_recurrence_knn_logitresid.csv |
| s1_temporal_state_recurrence_knn_label | 0.641696 | outputs/s1_temporal_state_recurrence_on_v48/oof_s1_temporal_state_recurrence_knn_label.csv | outputs/s1_temporal_state_recurrence_on_v48/submission_s1_temporal_state_recurrence_knn_label.csv |
| s1_temporal_state_recurrence_extra | 0.679529 | outputs/s1_temporal_state_recurrence_on_v48/oof_s1_temporal_state_recurrence_extra.csv | outputs/s1_temporal_state_recurrence_on_v48/submission_s1_temporal_state_recurrence_extra.csv |
| s1_temporal_state_recurrence_proto | 0.689360 | outputs/s1_temporal_state_recurrence_on_v48/oof_s1_temporal_state_recurrence_proto.csv | outputs/s1_temporal_state_recurrence_on_v48/submission_s1_temporal_state_recurrence_proto.csv |
| s1_temporal_state_recurrence_logreg | 0.807344 | outputs/s1_temporal_state_recurrence_on_v48/oof_s1_temporal_state_recurrence_logreg.csv | outputs/s1_temporal_state_recurrence_on_v48/submission_s1_temporal_state_recurrence_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_recurrence | 26 |
