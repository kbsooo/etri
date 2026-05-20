# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.477738`
- Best source S2 OOF: `0.563956`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_sleep_retrieval_meta | 0.563956 | outputs/s2_temporal_state_novelty_phase_on_v52/oof_s2_sleep_retrieval_meta.csv | outputs/s2_temporal_state_novelty_phase_on_v52/submission_s2_sleep_retrieval_meta.csv |
| s2_temporal_state_novelty_knn_resid | 0.571175 | outputs/s2_temporal_state_novelty_phase_on_v52/oof_s2_temporal_state_novelty_knn_resid.csv | outputs/s2_temporal_state_novelty_phase_on_v52/submission_s2_temporal_state_novelty_knn_resid.csv |
| s2_temporal_state_novelty_knn_logitresid | 0.603321 | outputs/s2_temporal_state_novelty_phase_on_v52/oof_s2_temporal_state_novelty_knn_logitresid.csv | outputs/s2_temporal_state_novelty_phase_on_v52/submission_s2_temporal_state_novelty_knn_logitresid.csv |
| s2_temporal_state_novelty_recovery_knn_resid | 0.635371 | outputs/s2_temporal_state_novelty_phase_on_v52/oof_s2_temporal_state_novelty_recovery_knn_resid.csv | outputs/s2_temporal_state_novelty_phase_on_v52/submission_s2_temporal_state_novelty_recovery_knn_resid.csv |
| s2_temporal_state_novelty_recovery_hgb | 0.640276 | outputs/s2_temporal_state_novelty_phase_on_v52/oof_s2_temporal_state_novelty_recovery_hgb.csv | outputs/s2_temporal_state_novelty_phase_on_v52/submission_s2_temporal_state_novelty_recovery_hgb.csv |
| s2_temporal_state_novelty_hgb | 0.651513 | outputs/s2_temporal_state_novelty_phase_on_v52/oof_s2_temporal_state_novelty_hgb.csv | outputs/s2_temporal_state_novelty_phase_on_v52/submission_s2_temporal_state_novelty_hgb.csv |
| s2_temporal_state_novelty_recovery_knn_logitresid | 0.653970 | outputs/s2_temporal_state_novelty_phase_on_v52/oof_s2_temporal_state_novelty_recovery_knn_logitresid.csv | outputs/s2_temporal_state_novelty_phase_on_v52/submission_s2_temporal_state_novelty_recovery_knn_logitresid.csv |
| s2_temporal_state_novelty_extra | 0.654613 | outputs/s2_temporal_state_novelty_phase_on_v52/oof_s2_temporal_state_novelty_extra.csv | outputs/s2_temporal_state_novelty_phase_on_v52/submission_s2_temporal_state_novelty_extra.csv |
| s2_temporal_state_novelty_recovery_extra | 0.662807 | outputs/s2_temporal_state_novelty_phase_on_v52/oof_s2_temporal_state_novelty_recovery_extra.csv | outputs/s2_temporal_state_novelty_phase_on_v52/submission_s2_temporal_state_novelty_recovery_extra.csv |
| s2_temporal_state_novelty_knn_label | 0.725763 | outputs/s2_temporal_state_novelty_phase_on_v52/oof_s2_temporal_state_novelty_knn_label.csv | outputs/s2_temporal_state_novelty_phase_on_v52/submission_s2_temporal_state_novelty_knn_label.csv |
| s2_temporal_state_novelty_proto | 0.726600 | outputs/s2_temporal_state_novelty_phase_on_v52/oof_s2_temporal_state_novelty_proto.csv | outputs/s2_temporal_state_novelty_phase_on_v52/submission_s2_temporal_state_novelty_proto.csv |
| s2_temporal_state_novelty_recovery_proto | 0.737286 | outputs/s2_temporal_state_novelty_phase_on_v52/oof_s2_temporal_state_novelty_recovery_proto.csv | outputs/s2_temporal_state_novelty_phase_on_v52/submission_s2_temporal_state_novelty_recovery_proto.csv |
| s2_temporal_state_novelty_recovery_knn_label | 0.749480 | outputs/s2_temporal_state_novelty_phase_on_v52/oof_s2_temporal_state_novelty_recovery_knn_label.csv | outputs/s2_temporal_state_novelty_phase_on_v52/submission_s2_temporal_state_novelty_recovery_knn_label.csv |
| s2_temporal_state_novelty_recovery_logreg | 0.900553 | outputs/s2_temporal_state_novelty_phase_on_v52/oof_s2_temporal_state_novelty_recovery_logreg.csv | outputs/s2_temporal_state_novelty_phase_on_v52/submission_s2_temporal_state_novelty_recovery_logreg.csv |
| s2_temporal_state_novelty_logreg | 1.063396 | outputs/s2_temporal_state_novelty_phase_on_v52/oof_s2_temporal_state_novelty_logreg.csv | outputs/s2_temporal_state_novelty_phase_on_v52/submission_s2_temporal_state_novelty_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty | 533 |
| temporal_state_novelty_recovery | 385 |
