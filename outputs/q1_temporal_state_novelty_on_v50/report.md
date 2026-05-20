# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.550023`
- Best source Q1 OOF: `0.561938`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.561938 | outputs/q1_temporal_state_novelty_on_v50/oof_q1_sleep_retrieval_meta.csv | outputs/q1_temporal_state_novelty_on_v50/submission_q1_sleep_retrieval_meta.csv |
| q1_temporal_state_novelty_knn_resid | 0.578458 | outputs/q1_temporal_state_novelty_on_v50/oof_q1_temporal_state_novelty_knn_resid.csv | outputs/q1_temporal_state_novelty_on_v50/submission_q1_temporal_state_novelty_knn_resid.csv |
| q1_temporal_state_novelty_knn_logitresid | 0.658731 | outputs/q1_temporal_state_novelty_on_v50/oof_q1_temporal_state_novelty_knn_logitresid.csv | outputs/q1_temporal_state_novelty_on_v50/submission_q1_temporal_state_novelty_knn_logitresid.csv |
| q1_temporal_state_novelty_extra | 0.708769 | outputs/q1_temporal_state_novelty_on_v50/oof_q1_temporal_state_novelty_extra.csv | outputs/q1_temporal_state_novelty_on_v50/submission_q1_temporal_state_novelty_extra.csv |
| q1_temporal_state_novelty_knn_label | 0.738800 | outputs/q1_temporal_state_novelty_on_v50/oof_q1_temporal_state_novelty_knn_label.csv | outputs/q1_temporal_state_novelty_on_v50/submission_q1_temporal_state_novelty_knn_label.csv |
| q1_temporal_state_novelty_hgb | 0.749215 | outputs/q1_temporal_state_novelty_on_v50/oof_q1_temporal_state_novelty_hgb.csv | outputs/q1_temporal_state_novelty_on_v50/submission_q1_temporal_state_novelty_hgb.csv |
| q1_temporal_state_novelty_proto | 0.820817 | outputs/q1_temporal_state_novelty_on_v50/oof_q1_temporal_state_novelty_proto.csv | outputs/q1_temporal_state_novelty_on_v50/submission_q1_temporal_state_novelty_proto.csv |
| q1_temporal_state_novelty_logreg | 1.035945 | outputs/q1_temporal_state_novelty_on_v50/oof_q1_temporal_state_novelty_logreg.csv | outputs/q1_temporal_state_novelty_on_v50/submission_q1_temporal_state_novelty_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty | 148 |
