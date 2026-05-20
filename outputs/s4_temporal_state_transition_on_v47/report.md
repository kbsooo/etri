# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.509200`
- Best source S4 OOF: `0.540794`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_sleep_retrieval_meta | 0.540794 | outputs/s4_temporal_state_transition_on_v47/oof_s4_sleep_retrieval_meta.csv | outputs/s4_temporal_state_transition_on_v47/submission_s4_sleep_retrieval_meta.csv |
| s4_temporal_state_transition_knn_resid | 0.572991 | outputs/s4_temporal_state_transition_on_v47/oof_s4_temporal_state_transition_knn_resid.csv | outputs/s4_temporal_state_transition_on_v47/submission_s4_temporal_state_transition_knn_resid.csv |
| s4_temporal_state_transition_knn_logitresid | 0.618292 | outputs/s4_temporal_state_transition_on_v47/oof_s4_temporal_state_transition_knn_logitresid.csv | outputs/s4_temporal_state_transition_on_v47/submission_s4_temporal_state_transition_knn_logitresid.csv |
| s4_temporal_state_transition_extra | 0.689819 | outputs/s4_temporal_state_transition_on_v47/oof_s4_temporal_state_transition_extra.csv | outputs/s4_temporal_state_transition_on_v47/submission_s4_temporal_state_transition_extra.csv |
| s4_temporal_state_transition_hgb | 0.692277 | outputs/s4_temporal_state_transition_on_v47/oof_s4_temporal_state_transition_hgb.csv | outputs/s4_temporal_state_transition_on_v47/submission_s4_temporal_state_transition_hgb.csv |
| s4_temporal_state_transition_knn_label | 0.708233 | outputs/s4_temporal_state_transition_on_v47/oof_s4_temporal_state_transition_knn_label.csv | outputs/s4_temporal_state_transition_on_v47/submission_s4_temporal_state_transition_knn_label.csv |
| s4_temporal_state_transition_proto | 0.771160 | outputs/s4_temporal_state_transition_on_v47/oof_s4_temporal_state_transition_proto.csv | outputs/s4_temporal_state_transition_on_v47/submission_s4_temporal_state_transition_proto.csv |
| s4_temporal_state_transition_logreg | 0.883235 | outputs/s4_temporal_state_transition_on_v47/oof_s4_temporal_state_transition_logreg.csv | outputs/s4_temporal_state_transition_on_v47/submission_s4_temporal_state_transition_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_transition | 35 |
