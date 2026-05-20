# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.554687`
- Best source Q2 OOF: `0.587500`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_sleep_retrieval_meta | 0.587500 | outputs/q2_temporal_state_novelty_recovery_on_v51/oof_q2_sleep_retrieval_meta.csv | outputs/q2_temporal_state_novelty_recovery_on_v51/submission_q2_sleep_retrieval_meta.csv |
| q2_temporal_state_novelty_recovery_knn_resid | 0.692196 | outputs/q2_temporal_state_novelty_recovery_on_v51/oof_q2_temporal_state_novelty_recovery_knn_resid.csv | outputs/q2_temporal_state_novelty_recovery_on_v51/submission_q2_temporal_state_novelty_recovery_knn_resid.csv |
| q2_temporal_state_novelty_recovery_extra | 0.709302 | outputs/q2_temporal_state_novelty_recovery_on_v51/oof_q2_temporal_state_novelty_recovery_extra.csv | outputs/q2_temporal_state_novelty_recovery_on_v51/submission_q2_temporal_state_novelty_recovery_extra.csv |
| q2_temporal_state_novelty_recovery_hgb | 0.716326 | outputs/q2_temporal_state_novelty_recovery_on_v51/oof_q2_temporal_state_novelty_recovery_hgb.csv | outputs/q2_temporal_state_novelty_recovery_on_v51/submission_q2_temporal_state_novelty_recovery_hgb.csv |
| q2_temporal_state_novelty_recovery_knn_label | 0.732460 | outputs/q2_temporal_state_novelty_recovery_on_v51/oof_q2_temporal_state_novelty_recovery_knn_label.csv | outputs/q2_temporal_state_novelty_recovery_on_v51/submission_q2_temporal_state_novelty_recovery_knn_label.csv |
| q2_temporal_state_novelty_recovery_knn_logitresid | 0.765146 | outputs/q2_temporal_state_novelty_recovery_on_v51/oof_q2_temporal_state_novelty_recovery_knn_logitresid.csv | outputs/q2_temporal_state_novelty_recovery_on_v51/submission_q2_temporal_state_novelty_recovery_knn_logitresid.csv |
| q2_temporal_state_novelty_recovery_proto | 0.780649 | outputs/q2_temporal_state_novelty_recovery_on_v51/oof_q2_temporal_state_novelty_recovery_proto.csv | outputs/q2_temporal_state_novelty_recovery_on_v51/submission_q2_temporal_state_novelty_recovery_proto.csv |
| q2_temporal_state_novelty_recovery_logreg | 0.920127 | outputs/q2_temporal_state_novelty_recovery_on_v51/oof_q2_temporal_state_novelty_recovery_logreg.csv | outputs/q2_temporal_state_novelty_recovery_on_v51/submission_q2_temporal_state_novelty_recovery_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty_recovery | 385 |
