# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.526272`
- Best source Q3 OOF: `0.549684`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_sleep_retrieval_meta | 0.549684 | outputs/q3_temporal_state_novelty_on_v50/oof_q3_sleep_retrieval_meta.csv | outputs/q3_temporal_state_novelty_on_v50/submission_q3_sleep_retrieval_meta.csv |
| q3_temporal_state_novelty_knn_resid | 0.555966 | outputs/q3_temporal_state_novelty_on_v50/oof_q3_temporal_state_novelty_knn_resid.csv | outputs/q3_temporal_state_novelty_on_v50/submission_q3_temporal_state_novelty_knn_resid.csv |
| q3_temporal_state_novelty_knn_logitresid | 0.636208 | outputs/q3_temporal_state_novelty_on_v50/oof_q3_temporal_state_novelty_knn_logitresid.csv | outputs/q3_temporal_state_novelty_on_v50/submission_q3_temporal_state_novelty_knn_logitresid.csv |
| q3_temporal_state_novelty_extra | 0.703528 | outputs/q3_temporal_state_novelty_on_v50/oof_q3_temporal_state_novelty_extra.csv | outputs/q3_temporal_state_novelty_on_v50/submission_q3_temporal_state_novelty_extra.csv |
| q3_temporal_state_novelty_knn_label | 0.733805 | outputs/q3_temporal_state_novelty_on_v50/oof_q3_temporal_state_novelty_knn_label.csv | outputs/q3_temporal_state_novelty_on_v50/submission_q3_temporal_state_novelty_knn_label.csv |
| q3_temporal_state_novelty_hgb | 0.754805 | outputs/q3_temporal_state_novelty_on_v50/oof_q3_temporal_state_novelty_hgb.csv | outputs/q3_temporal_state_novelty_on_v50/submission_q3_temporal_state_novelty_hgb.csv |
| q3_temporal_state_novelty_proto | 0.788017 | outputs/q3_temporal_state_novelty_on_v50/oof_q3_temporal_state_novelty_proto.csv | outputs/q3_temporal_state_novelty_on_v50/submission_q3_temporal_state_novelty_proto.csv |
| q3_temporal_state_novelty_logreg | 1.020406 | outputs/q3_temporal_state_novelty_on_v50/oof_q3_temporal_state_novelty_logreg.csv | outputs/q3_temporal_state_novelty_on_v50/submission_q3_temporal_state_novelty_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty | 148 |
