# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.493611`
- Best source S1 OOF: `0.580546`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_temporal_state_novelty_knn_resid | 0.580546 | outputs/s1_temporal_state_novelty_phase_on_v52/oof_s1_temporal_state_novelty_knn_resid.csv | outputs/s1_temporal_state_novelty_phase_on_v52/submission_s1_temporal_state_novelty_knn_resid.csv |
| s1_temporal_state_novelty_recovery_knn_resid | 0.581976 | outputs/s1_temporal_state_novelty_phase_on_v52/oof_s1_temporal_state_novelty_recovery_knn_resid.csv | outputs/s1_temporal_state_novelty_phase_on_v52/submission_s1_temporal_state_novelty_recovery_knn_resid.csv |
| s1_sleep_retrieval_meta | 0.587140 | outputs/s1_temporal_state_novelty_phase_on_v52/oof_s1_sleep_retrieval_meta.csv | outputs/s1_temporal_state_novelty_phase_on_v52/submission_s1_sleep_retrieval_meta.csv |
| s1_temporal_state_novelty_hgb | 0.609393 | outputs/s1_temporal_state_novelty_phase_on_v52/oof_s1_temporal_state_novelty_hgb.csv | outputs/s1_temporal_state_novelty_phase_on_v52/submission_s1_temporal_state_novelty_hgb.csv |
| s1_temporal_state_novelty_recovery_hgb | 0.620083 | outputs/s1_temporal_state_novelty_phase_on_v52/oof_s1_temporal_state_novelty_recovery_hgb.csv | outputs/s1_temporal_state_novelty_phase_on_v52/submission_s1_temporal_state_novelty_recovery_hgb.csv |
| s1_temporal_state_novelty_recovery_knn_logitresid | 0.636210 | outputs/s1_temporal_state_novelty_phase_on_v52/oof_s1_temporal_state_novelty_recovery_knn_logitresid.csv | outputs/s1_temporal_state_novelty_phase_on_v52/submission_s1_temporal_state_novelty_recovery_knn_logitresid.csv |
| s1_temporal_state_novelty_knn_logitresid | 0.641460 | outputs/s1_temporal_state_novelty_phase_on_v52/oof_s1_temporal_state_novelty_knn_logitresid.csv | outputs/s1_temporal_state_novelty_phase_on_v52/submission_s1_temporal_state_novelty_knn_logitresid.csv |
| s1_temporal_state_novelty_recovery_knn_label | 0.664979 | outputs/s1_temporal_state_novelty_phase_on_v52/oof_s1_temporal_state_novelty_recovery_knn_label.csv | outputs/s1_temporal_state_novelty_phase_on_v52/submission_s1_temporal_state_novelty_recovery_knn_label.csv |
| s1_temporal_state_novelty_knn_label | 0.676489 | outputs/s1_temporal_state_novelty_phase_on_v52/oof_s1_temporal_state_novelty_knn_label.csv | outputs/s1_temporal_state_novelty_phase_on_v52/submission_s1_temporal_state_novelty_knn_label.csv |
| s1_temporal_state_novelty_recovery_extra | 0.682396 | outputs/s1_temporal_state_novelty_phase_on_v52/oof_s1_temporal_state_novelty_recovery_extra.csv | outputs/s1_temporal_state_novelty_phase_on_v52/submission_s1_temporal_state_novelty_recovery_extra.csv |
| s1_temporal_state_novelty_extra | 0.688246 | outputs/s1_temporal_state_novelty_phase_on_v52/oof_s1_temporal_state_novelty_extra.csv | outputs/s1_temporal_state_novelty_phase_on_v52/submission_s1_temporal_state_novelty_extra.csv |
| s1_temporal_state_novelty_recovery_proto | 0.726643 | outputs/s1_temporal_state_novelty_phase_on_v52/oof_s1_temporal_state_novelty_recovery_proto.csv | outputs/s1_temporal_state_novelty_phase_on_v52/submission_s1_temporal_state_novelty_recovery_proto.csv |
| s1_temporal_state_novelty_proto | 0.786984 | outputs/s1_temporal_state_novelty_phase_on_v52/oof_s1_temporal_state_novelty_proto.csv | outputs/s1_temporal_state_novelty_phase_on_v52/submission_s1_temporal_state_novelty_proto.csv |
| s1_temporal_state_novelty_recovery_logreg | 0.933244 | outputs/s1_temporal_state_novelty_phase_on_v52/oof_s1_temporal_state_novelty_recovery_logreg.csv | outputs/s1_temporal_state_novelty_phase_on_v52/submission_s1_temporal_state_novelty_recovery_logreg.csv |
| s1_temporal_state_novelty_logreg | 1.080738 | outputs/s1_temporal_state_novelty_phase_on_v52/oof_s1_temporal_state_novelty_logreg.csv | outputs/s1_temporal_state_novelty_phase_on_v52/submission_s1_temporal_state_novelty_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty | 533 |
| temporal_state_novelty_recovery | 385 |
