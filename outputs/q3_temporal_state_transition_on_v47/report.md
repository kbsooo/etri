# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.536765`
- Best source Q3 OOF: `0.561024`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_sleep_retrieval_meta | 0.561024 | outputs/q3_temporal_state_transition_on_v47/oof_q3_sleep_retrieval_meta.csv | outputs/q3_temporal_state_transition_on_v47/submission_q3_sleep_retrieval_meta.csv |
| q3_temporal_state_transition_knn_resid | 0.562279 | outputs/q3_temporal_state_transition_on_v47/oof_q3_temporal_state_transition_knn_resid.csv | outputs/q3_temporal_state_transition_on_v47/submission_q3_temporal_state_transition_knn_resid.csv |
| q3_temporal_state_transition_knn_logitresid | 0.632751 | outputs/q3_temporal_state_transition_on_v47/oof_q3_temporal_state_transition_knn_logitresid.csv | outputs/q3_temporal_state_transition_on_v47/submission_q3_temporal_state_transition_knn_logitresid.csv |
| q3_temporal_state_transition_hgb | 0.698513 | outputs/q3_temporal_state_transition_on_v47/oof_q3_temporal_state_transition_hgb.csv | outputs/q3_temporal_state_transition_on_v47/submission_q3_temporal_state_transition_hgb.csv |
| q3_temporal_state_transition_extra | 0.700652 | outputs/q3_temporal_state_transition_on_v47/oof_q3_temporal_state_transition_extra.csv | outputs/q3_temporal_state_transition_on_v47/submission_q3_temporal_state_transition_extra.csv |
| q3_temporal_state_transition_knn_label | 0.715301 | outputs/q3_temporal_state_transition_on_v47/oof_q3_temporal_state_transition_knn_label.csv | outputs/q3_temporal_state_transition_on_v47/submission_q3_temporal_state_transition_knn_label.csv |
| q3_temporal_state_transition_proto | 0.789024 | outputs/q3_temporal_state_transition_on_v47/oof_q3_temporal_state_transition_proto.csv | outputs/q3_temporal_state_transition_on_v47/submission_q3_temporal_state_transition_proto.csv |
| q3_temporal_state_transition_logreg | 0.933328 | outputs/q3_temporal_state_transition_on_v47/oof_q3_temporal_state_transition_logreg.csv | outputs/q3_temporal_state_transition_on_v47/submission_q3_temporal_state_transition_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_transition | 35 |
