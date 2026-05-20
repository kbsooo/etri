# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.497013`
- Best source S1 OOF: `0.576181`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_sleep_retrieval_meta | 0.576181 | outputs/s1_temporal_state_novelty_on_v50/oof_s1_sleep_retrieval_meta.csv | outputs/s1_temporal_state_novelty_on_v50/submission_s1_sleep_retrieval_meta.csv |
| s1_temporal_state_novelty_knn_resid | 0.594016 | outputs/s1_temporal_state_novelty_on_v50/oof_s1_temporal_state_novelty_knn_resid.csv | outputs/s1_temporal_state_novelty_on_v50/submission_s1_temporal_state_novelty_knn_resid.csv |
| s1_temporal_state_novelty_hgb | 0.627274 | outputs/s1_temporal_state_novelty_on_v50/oof_s1_temporal_state_novelty_hgb.csv | outputs/s1_temporal_state_novelty_on_v50/submission_s1_temporal_state_novelty_hgb.csv |
| s1_temporal_state_novelty_knn_logitresid | 0.646447 | outputs/s1_temporal_state_novelty_on_v50/oof_s1_temporal_state_novelty_knn_logitresid.csv | outputs/s1_temporal_state_novelty_on_v50/submission_s1_temporal_state_novelty_knn_logitresid.csv |
| s1_temporal_state_novelty_extra | 0.655482 | outputs/s1_temporal_state_novelty_on_v50/oof_s1_temporal_state_novelty_extra.csv | outputs/s1_temporal_state_novelty_on_v50/submission_s1_temporal_state_novelty_extra.csv |
| s1_temporal_state_novelty_knn_label | 0.696649 | outputs/s1_temporal_state_novelty_on_v50/oof_s1_temporal_state_novelty_knn_label.csv | outputs/s1_temporal_state_novelty_on_v50/submission_s1_temporal_state_novelty_knn_label.csv |
| s1_temporal_state_novelty_proto | 0.705307 | outputs/s1_temporal_state_novelty_on_v50/oof_s1_temporal_state_novelty_proto.csv | outputs/s1_temporal_state_novelty_on_v50/submission_s1_temporal_state_novelty_proto.csv |
| s1_temporal_state_novelty_logreg | 0.936642 | outputs/s1_temporal_state_novelty_on_v50/oof_s1_temporal_state_novelty_logreg.csv | outputs/s1_temporal_state_novelty_on_v50/submission_s1_temporal_state_novelty_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty | 148 |
