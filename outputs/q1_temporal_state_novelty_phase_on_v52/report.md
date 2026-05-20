# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.544717`
- Best source Q1 OOF: `0.570263`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.570263 | outputs/q1_temporal_state_novelty_phase_on_v52/oof_q1_sleep_retrieval_meta.csv | outputs/q1_temporal_state_novelty_phase_on_v52/submission_q1_sleep_retrieval_meta.csv |
| q1_temporal_state_novelty_knn_resid | 0.600705 | outputs/q1_temporal_state_novelty_phase_on_v52/oof_q1_temporal_state_novelty_knn_resid.csv | outputs/q1_temporal_state_novelty_phase_on_v52/submission_q1_temporal_state_novelty_knn_resid.csv |
| q1_temporal_state_novelty_recovery_knn_resid | 0.651310 | outputs/q1_temporal_state_novelty_phase_on_v52/oof_q1_temporal_state_novelty_recovery_knn_resid.csv | outputs/q1_temporal_state_novelty_phase_on_v52/submission_q1_temporal_state_novelty_recovery_knn_resid.csv |
| q1_temporal_state_novelty_recovery_extra | 0.694197 | outputs/q1_temporal_state_novelty_phase_on_v52/oof_q1_temporal_state_novelty_recovery_extra.csv | outputs/q1_temporal_state_novelty_phase_on_v52/submission_q1_temporal_state_novelty_recovery_extra.csv |
| q1_temporal_state_novelty_knn_logitresid | 0.700727 | outputs/q1_temporal_state_novelty_phase_on_v52/oof_q1_temporal_state_novelty_knn_logitresid.csv | outputs/q1_temporal_state_novelty_phase_on_v52/submission_q1_temporal_state_novelty_knn_logitresid.csv |
| q1_temporal_state_novelty_extra | 0.702118 | outputs/q1_temporal_state_novelty_phase_on_v52/oof_q1_temporal_state_novelty_extra.csv | outputs/q1_temporal_state_novelty_phase_on_v52/submission_q1_temporal_state_novelty_extra.csv |
| q1_temporal_state_novelty_hgb | 0.737737 | outputs/q1_temporal_state_novelty_phase_on_v52/oof_q1_temporal_state_novelty_hgb.csv | outputs/q1_temporal_state_novelty_phase_on_v52/submission_q1_temporal_state_novelty_hgb.csv |
| q1_temporal_state_novelty_knn_label | 0.741996 | outputs/q1_temporal_state_novelty_phase_on_v52/oof_q1_temporal_state_novelty_knn_label.csv | outputs/q1_temporal_state_novelty_phase_on_v52/submission_q1_temporal_state_novelty_knn_label.csv |
| q1_temporal_state_novelty_recovery_hgb | 0.743979 | outputs/q1_temporal_state_novelty_phase_on_v52/oof_q1_temporal_state_novelty_recovery_hgb.csv | outputs/q1_temporal_state_novelty_phase_on_v52/submission_q1_temporal_state_novelty_recovery_hgb.csv |
| q1_temporal_state_novelty_recovery_knn_logitresid | 0.757097 | outputs/q1_temporal_state_novelty_phase_on_v52/oof_q1_temporal_state_novelty_recovery_knn_logitresid.csv | outputs/q1_temporal_state_novelty_phase_on_v52/submission_q1_temporal_state_novelty_recovery_knn_logitresid.csv |
| q1_temporal_state_novelty_recovery_knn_label | 0.770668 | outputs/q1_temporal_state_novelty_phase_on_v52/oof_q1_temporal_state_novelty_recovery_knn_label.csv | outputs/q1_temporal_state_novelty_phase_on_v52/submission_q1_temporal_state_novelty_recovery_knn_label.csv |
| q1_temporal_state_novelty_recovery_proto | 0.770828 | outputs/q1_temporal_state_novelty_phase_on_v52/oof_q1_temporal_state_novelty_recovery_proto.csv | outputs/q1_temporal_state_novelty_phase_on_v52/submission_q1_temporal_state_novelty_recovery_proto.csv |
| q1_temporal_state_novelty_proto | 0.778665 | outputs/q1_temporal_state_novelty_phase_on_v52/oof_q1_temporal_state_novelty_proto.csv | outputs/q1_temporal_state_novelty_phase_on_v52/submission_q1_temporal_state_novelty_proto.csv |
| q1_temporal_state_novelty_recovery_logreg | 1.006190 | outputs/q1_temporal_state_novelty_phase_on_v52/oof_q1_temporal_state_novelty_recovery_logreg.csv | outputs/q1_temporal_state_novelty_phase_on_v52/submission_q1_temporal_state_novelty_recovery_logreg.csv |
| q1_temporal_state_novelty_logreg | 1.146655 | outputs/q1_temporal_state_novelty_phase_on_v52/oof_q1_temporal_state_novelty_logreg.csv | outputs/q1_temporal_state_novelty_phase_on_v52/submission_q1_temporal_state_novelty_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty | 533 |
| temporal_state_novelty_recovery | 385 |
