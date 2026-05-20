# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.522725`
- Best source Q3 OOF: `0.552136`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_sleep_retrieval_meta | 0.552136 | outputs/q3_temporal_state_novelty_phase_on_v52/oof_q3_sleep_retrieval_meta.csv | outputs/q3_temporal_state_novelty_phase_on_v52/submission_q3_sleep_retrieval_meta.csv |
| q3_temporal_state_novelty_recovery_knn_resid | 0.563272 | outputs/q3_temporal_state_novelty_phase_on_v52/oof_q3_temporal_state_novelty_recovery_knn_resid.csv | outputs/q3_temporal_state_novelty_phase_on_v52/submission_q3_temporal_state_novelty_recovery_knn_resid.csv |
| q3_temporal_state_novelty_knn_resid | 0.574927 | outputs/q3_temporal_state_novelty_phase_on_v52/oof_q3_temporal_state_novelty_knn_resid.csv | outputs/q3_temporal_state_novelty_phase_on_v52/submission_q3_temporal_state_novelty_knn_resid.csv |
| q3_temporal_state_novelty_recovery_knn_logitresid | 0.634894 | outputs/q3_temporal_state_novelty_phase_on_v52/oof_q3_temporal_state_novelty_recovery_knn_logitresid.csv | outputs/q3_temporal_state_novelty_phase_on_v52/submission_q3_temporal_state_novelty_recovery_knn_logitresid.csv |
| q3_temporal_state_novelty_knn_logitresid | 0.659852 | outputs/q3_temporal_state_novelty_phase_on_v52/oof_q3_temporal_state_novelty_knn_logitresid.csv | outputs/q3_temporal_state_novelty_phase_on_v52/submission_q3_temporal_state_novelty_knn_logitresid.csv |
| q3_temporal_state_novelty_recovery_knn_label | 0.692597 | outputs/q3_temporal_state_novelty_phase_on_v52/oof_q3_temporal_state_novelty_recovery_knn_label.csv | outputs/q3_temporal_state_novelty_phase_on_v52/submission_q3_temporal_state_novelty_recovery_knn_label.csv |
| q3_temporal_state_novelty_recovery_extra | 0.710903 | outputs/q3_temporal_state_novelty_phase_on_v52/oof_q3_temporal_state_novelty_recovery_extra.csv | outputs/q3_temporal_state_novelty_phase_on_v52/submission_q3_temporal_state_novelty_recovery_extra.csv |
| q3_temporal_state_novelty_extra | 0.714915 | outputs/q3_temporal_state_novelty_phase_on_v52/oof_q3_temporal_state_novelty_extra.csv | outputs/q3_temporal_state_novelty_phase_on_v52/submission_q3_temporal_state_novelty_extra.csv |
| q3_temporal_state_novelty_knn_label | 0.717739 | outputs/q3_temporal_state_novelty_phase_on_v52/oof_q3_temporal_state_novelty_knn_label.csv | outputs/q3_temporal_state_novelty_phase_on_v52/submission_q3_temporal_state_novelty_knn_label.csv |
| q3_temporal_state_novelty_hgb | 0.725304 | outputs/q3_temporal_state_novelty_phase_on_v52/oof_q3_temporal_state_novelty_hgb.csv | outputs/q3_temporal_state_novelty_phase_on_v52/submission_q3_temporal_state_novelty_hgb.csv |
| q3_temporal_state_novelty_recovery_hgb | 0.741631 | outputs/q3_temporal_state_novelty_phase_on_v52/oof_q3_temporal_state_novelty_recovery_hgb.csv | outputs/q3_temporal_state_novelty_phase_on_v52/submission_q3_temporal_state_novelty_recovery_hgb.csv |
| q3_temporal_state_novelty_recovery_proto | 0.745186 | outputs/q3_temporal_state_novelty_phase_on_v52/oof_q3_temporal_state_novelty_recovery_proto.csv | outputs/q3_temporal_state_novelty_phase_on_v52/submission_q3_temporal_state_novelty_recovery_proto.csv |
| q3_temporal_state_novelty_proto | 0.773903 | outputs/q3_temporal_state_novelty_phase_on_v52/oof_q3_temporal_state_novelty_proto.csv | outputs/q3_temporal_state_novelty_phase_on_v52/submission_q3_temporal_state_novelty_proto.csv |
| q3_temporal_state_novelty_recovery_logreg | 1.002497 | outputs/q3_temporal_state_novelty_phase_on_v52/oof_q3_temporal_state_novelty_recovery_logreg.csv | outputs/q3_temporal_state_novelty_phase_on_v52/submission_q3_temporal_state_novelty_recovery_logreg.csv |
| q3_temporal_state_novelty_logreg | 1.142157 | outputs/q3_temporal_state_novelty_phase_on_v52/oof_q3_temporal_state_novelty_logreg.csv | outputs/q3_temporal_state_novelty_phase_on_v52/submission_q3_temporal_state_novelty_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty | 533 |
| temporal_state_novelty_recovery | 385 |
