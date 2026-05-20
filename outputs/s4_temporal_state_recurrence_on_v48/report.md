# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.507634`
- Best source S4 OOF: `0.534304`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_temporal_state_recurrence_knn_resid | 0.534304 | outputs/s4_temporal_state_recurrence_on_v48/oof_s4_temporal_state_recurrence_knn_resid.csv | outputs/s4_temporal_state_recurrence_on_v48/submission_s4_temporal_state_recurrence_knn_resid.csv |
| s4_sleep_retrieval_meta | 0.542587 | outputs/s4_temporal_state_recurrence_on_v48/oof_s4_sleep_retrieval_meta.csv | outputs/s4_temporal_state_recurrence_on_v48/submission_s4_sleep_retrieval_meta.csv |
| s4_temporal_state_recurrence_knn_logitresid | 0.617462 | outputs/s4_temporal_state_recurrence_on_v48/oof_s4_temporal_state_recurrence_knn_logitresid.csv | outputs/s4_temporal_state_recurrence_on_v48/submission_s4_temporal_state_recurrence_knn_logitresid.csv |
| s4_temporal_state_recurrence_extra | 0.690102 | outputs/s4_temporal_state_recurrence_on_v48/oof_s4_temporal_state_recurrence_extra.csv | outputs/s4_temporal_state_recurrence_on_v48/submission_s4_temporal_state_recurrence_extra.csv |
| s4_temporal_state_recurrence_knn_label | 0.708052 | outputs/s4_temporal_state_recurrence_on_v48/oof_s4_temporal_state_recurrence_knn_label.csv | outputs/s4_temporal_state_recurrence_on_v48/submission_s4_temporal_state_recurrence_knn_label.csv |
| s4_temporal_state_recurrence_hgb | 0.729630 | outputs/s4_temporal_state_recurrence_on_v48/oof_s4_temporal_state_recurrence_hgb.csv | outputs/s4_temporal_state_recurrence_on_v48/submission_s4_temporal_state_recurrence_hgb.csv |
| s4_temporal_state_recurrence_proto | 0.754532 | outputs/s4_temporal_state_recurrence_on_v48/oof_s4_temporal_state_recurrence_proto.csv | outputs/s4_temporal_state_recurrence_on_v48/submission_s4_temporal_state_recurrence_proto.csv |
| s4_temporal_state_recurrence_logreg | 0.869933 | outputs/s4_temporal_state_recurrence_on_v48/oof_s4_temporal_state_recurrence_logreg.csv | outputs/s4_temporal_state_recurrence_on_v48/submission_s4_temporal_state_recurrence_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_recurrence | 26 |
