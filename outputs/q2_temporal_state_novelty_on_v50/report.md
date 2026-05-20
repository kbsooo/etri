# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.559150`
- Best source Q2 OOF: `0.581000`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_sleep_retrieval_meta | 0.581000 | outputs/q2_temporal_state_novelty_on_v50/oof_q2_sleep_retrieval_meta.csv | outputs/q2_temporal_state_novelty_on_v50/submission_q2_sleep_retrieval_meta.csv |
| q2_temporal_state_novelty_knn_resid | 0.639201 | outputs/q2_temporal_state_novelty_on_v50/oof_q2_temporal_state_novelty_knn_resid.csv | outputs/q2_temporal_state_novelty_on_v50/submission_q2_temporal_state_novelty_knn_resid.csv |
| q2_temporal_state_novelty_extra | 0.694942 | outputs/q2_temporal_state_novelty_on_v50/oof_q2_temporal_state_novelty_extra.csv | outputs/q2_temporal_state_novelty_on_v50/submission_q2_temporal_state_novelty_extra.csv |
| q2_temporal_state_novelty_knn_label | 0.710662 | outputs/q2_temporal_state_novelty_on_v50/oof_q2_temporal_state_novelty_knn_label.csv | outputs/q2_temporal_state_novelty_on_v50/submission_q2_temporal_state_novelty_knn_label.csv |
| q2_temporal_state_novelty_knn_logitresid | 0.741499 | outputs/q2_temporal_state_novelty_on_v50/oof_q2_temporal_state_novelty_knn_logitresid.csv | outputs/q2_temporal_state_novelty_on_v50/submission_q2_temporal_state_novelty_knn_logitresid.csv |
| q2_temporal_state_novelty_hgb | 0.746303 | outputs/q2_temporal_state_novelty_on_v50/oof_q2_temporal_state_novelty_hgb.csv | outputs/q2_temporal_state_novelty_on_v50/submission_q2_temporal_state_novelty_hgb.csv |
| q2_temporal_state_novelty_proto | 0.787262 | outputs/q2_temporal_state_novelty_on_v50/oof_q2_temporal_state_novelty_proto.csv | outputs/q2_temporal_state_novelty_on_v50/submission_q2_temporal_state_novelty_proto.csv |
| q2_temporal_state_novelty_logreg | 0.974312 | outputs/q2_temporal_state_novelty_on_v50/oof_q2_temporal_state_novelty_logreg.csv | outputs/q2_temporal_state_novelty_on_v50/submission_q2_temporal_state_novelty_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty | 148 |
