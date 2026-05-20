# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.503123`
- Best source S4 OOF: `0.533092`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_sleep_retrieval_meta | 0.533092 | outputs/s4_temporal_state_novelty_on_v50/oof_s4_sleep_retrieval_meta.csv | outputs/s4_temporal_state_novelty_on_v50/submission_s4_sleep_retrieval_meta.csv |
| s4_temporal_state_novelty_knn_resid | 0.565823 | outputs/s4_temporal_state_novelty_on_v50/oof_s4_temporal_state_novelty_knn_resid.csv | outputs/s4_temporal_state_novelty_on_v50/submission_s4_temporal_state_novelty_knn_resid.csv |
| s4_temporal_state_novelty_hgb | 0.667469 | outputs/s4_temporal_state_novelty_on_v50/oof_s4_temporal_state_novelty_hgb.csv | outputs/s4_temporal_state_novelty_on_v50/submission_s4_temporal_state_novelty_hgb.csv |
| s4_temporal_state_novelty_knn_logitresid | 0.671396 | outputs/s4_temporal_state_novelty_on_v50/oof_s4_temporal_state_novelty_knn_logitresid.csv | outputs/s4_temporal_state_novelty_on_v50/submission_s4_temporal_state_novelty_knn_logitresid.csv |
| s4_temporal_state_novelty_extra | 0.675150 | outputs/s4_temporal_state_novelty_on_v50/oof_s4_temporal_state_novelty_extra.csv | outputs/s4_temporal_state_novelty_on_v50/submission_s4_temporal_state_novelty_extra.csv |
| s4_temporal_state_novelty_proto | 0.742649 | outputs/s4_temporal_state_novelty_on_v50/oof_s4_temporal_state_novelty_proto.csv | outputs/s4_temporal_state_novelty_on_v50/submission_s4_temporal_state_novelty_proto.csv |
| s4_temporal_state_novelty_knn_label | 0.749968 | outputs/s4_temporal_state_novelty_on_v50/oof_s4_temporal_state_novelty_knn_label.csv | outputs/s4_temporal_state_novelty_on_v50/submission_s4_temporal_state_novelty_knn_label.csv |
| s4_temporal_state_novelty_logreg | 0.912351 | outputs/s4_temporal_state_novelty_on_v50/oof_s4_temporal_state_novelty_logreg.csv | outputs/s4_temporal_state_novelty_on_v50/submission_s4_temporal_state_novelty_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty | 148 |
