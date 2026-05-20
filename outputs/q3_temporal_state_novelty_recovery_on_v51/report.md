# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.524033`
- Best source Q3 OOF: `0.558772`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_temporal_state_novelty_recovery_knn_resid | 0.558772 | outputs/q3_temporal_state_novelty_recovery_on_v51/oof_q3_temporal_state_novelty_recovery_knn_resid.csv | outputs/q3_temporal_state_novelty_recovery_on_v51/submission_q3_temporal_state_novelty_recovery_knn_resid.csv |
| q3_sleep_retrieval_meta | 0.564064 | outputs/q3_temporal_state_novelty_recovery_on_v51/oof_q3_sleep_retrieval_meta.csv | outputs/q3_temporal_state_novelty_recovery_on_v51/submission_q3_sleep_retrieval_meta.csv |
| q3_temporal_state_novelty_recovery_knn_logitresid | 0.629269 | outputs/q3_temporal_state_novelty_recovery_on_v51/oof_q3_temporal_state_novelty_recovery_knn_logitresid.csv | outputs/q3_temporal_state_novelty_recovery_on_v51/submission_q3_temporal_state_novelty_recovery_knn_logitresid.csv |
| q3_temporal_state_novelty_recovery_knn_label | 0.692597 | outputs/q3_temporal_state_novelty_recovery_on_v51/oof_q3_temporal_state_novelty_recovery_knn_label.csv | outputs/q3_temporal_state_novelty_recovery_on_v51/submission_q3_temporal_state_novelty_recovery_knn_label.csv |
| q3_temporal_state_novelty_recovery_extra | 0.710903 | outputs/q3_temporal_state_novelty_recovery_on_v51/oof_q3_temporal_state_novelty_recovery_extra.csv | outputs/q3_temporal_state_novelty_recovery_on_v51/submission_q3_temporal_state_novelty_recovery_extra.csv |
| q3_temporal_state_novelty_recovery_hgb | 0.741631 | outputs/q3_temporal_state_novelty_recovery_on_v51/oof_q3_temporal_state_novelty_recovery_hgb.csv | outputs/q3_temporal_state_novelty_recovery_on_v51/submission_q3_temporal_state_novelty_recovery_hgb.csv |
| q3_temporal_state_novelty_recovery_proto | 0.745186 | outputs/q3_temporal_state_novelty_recovery_on_v51/oof_q3_temporal_state_novelty_recovery_proto.csv | outputs/q3_temporal_state_novelty_recovery_on_v51/submission_q3_temporal_state_novelty_recovery_proto.csv |
| q3_temporal_state_novelty_recovery_logreg | 1.002497 | outputs/q3_temporal_state_novelty_recovery_on_v51/oof_q3_temporal_state_novelty_recovery_logreg.csv | outputs/q3_temporal_state_novelty_recovery_on_v51/submission_q3_temporal_state_novelty_recovery_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty_recovery | 385 |
