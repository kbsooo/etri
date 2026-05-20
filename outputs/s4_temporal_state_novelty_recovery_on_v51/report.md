# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.500054`
- Best source S4 OOF: `0.543912`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_sleep_retrieval_meta | 0.543912 | outputs/s4_temporal_state_novelty_recovery_on_v51/oof_s4_sleep_retrieval_meta.csv | outputs/s4_temporal_state_novelty_recovery_on_v51/submission_s4_sleep_retrieval_meta.csv |
| s4_temporal_state_novelty_recovery_knn_resid | 0.546532 | outputs/s4_temporal_state_novelty_recovery_on_v51/oof_s4_temporal_state_novelty_recovery_knn_resid.csv | outputs/s4_temporal_state_novelty_recovery_on_v51/submission_s4_temporal_state_novelty_recovery_knn_resid.csv |
| s4_temporal_state_novelty_recovery_knn_logitresid | 0.605902 | outputs/s4_temporal_state_novelty_recovery_on_v51/oof_s4_temporal_state_novelty_recovery_knn_logitresid.csv | outputs/s4_temporal_state_novelty_recovery_on_v51/submission_s4_temporal_state_novelty_recovery_knn_logitresid.csv |
| s4_temporal_state_novelty_recovery_hgb | 0.673758 | outputs/s4_temporal_state_novelty_recovery_on_v51/oof_s4_temporal_state_novelty_recovery_hgb.csv | outputs/s4_temporal_state_novelty_recovery_on_v51/submission_s4_temporal_state_novelty_recovery_hgb.csv |
| s4_temporal_state_novelty_recovery_extra | 0.677735 | outputs/s4_temporal_state_novelty_recovery_on_v51/oof_s4_temporal_state_novelty_recovery_extra.csv | outputs/s4_temporal_state_novelty_recovery_on_v51/submission_s4_temporal_state_novelty_recovery_extra.csv |
| s4_temporal_state_novelty_recovery_knn_label | 0.734402 | outputs/s4_temporal_state_novelty_recovery_on_v51/oof_s4_temporal_state_novelty_recovery_knn_label.csv | outputs/s4_temporal_state_novelty_recovery_on_v51/submission_s4_temporal_state_novelty_recovery_knn_label.csv |
| s4_temporal_state_novelty_recovery_proto | 0.751092 | outputs/s4_temporal_state_novelty_recovery_on_v51/oof_s4_temporal_state_novelty_recovery_proto.csv | outputs/s4_temporal_state_novelty_recovery_on_v51/submission_s4_temporal_state_novelty_recovery_proto.csv |
| s4_temporal_state_novelty_recovery_logreg | 0.949116 | outputs/s4_temporal_state_novelty_recovery_on_v51/oof_s4_temporal_state_novelty_recovery_logreg.csv | outputs/s4_temporal_state_novelty_recovery_on_v51/submission_s4_temporal_state_novelty_recovery_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty_recovery | 385 |
