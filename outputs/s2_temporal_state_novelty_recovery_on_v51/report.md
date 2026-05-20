# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.478194`
- Best source S2 OOF: `0.558409`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_sleep_retrieval_meta | 0.558409 | outputs/s2_temporal_state_novelty_recovery_on_v51/oof_s2_sleep_retrieval_meta.csv | outputs/s2_temporal_state_novelty_recovery_on_v51/submission_s2_sleep_retrieval_meta.csv |
| s2_temporal_state_novelty_recovery_knn_resid | 0.618861 | outputs/s2_temporal_state_novelty_recovery_on_v51/oof_s2_temporal_state_novelty_recovery_knn_resid.csv | outputs/s2_temporal_state_novelty_recovery_on_v51/submission_s2_temporal_state_novelty_recovery_knn_resid.csv |
| s2_temporal_state_novelty_recovery_hgb | 0.640276 | outputs/s2_temporal_state_novelty_recovery_on_v51/oof_s2_temporal_state_novelty_recovery_hgb.csv | outputs/s2_temporal_state_novelty_recovery_on_v51/submission_s2_temporal_state_novelty_recovery_hgb.csv |
| s2_temporal_state_novelty_recovery_knn_logitresid | 0.653764 | outputs/s2_temporal_state_novelty_recovery_on_v51/oof_s2_temporal_state_novelty_recovery_knn_logitresid.csv | outputs/s2_temporal_state_novelty_recovery_on_v51/submission_s2_temporal_state_novelty_recovery_knn_logitresid.csv |
| s2_temporal_state_novelty_recovery_extra | 0.662807 | outputs/s2_temporal_state_novelty_recovery_on_v51/oof_s2_temporal_state_novelty_recovery_extra.csv | outputs/s2_temporal_state_novelty_recovery_on_v51/submission_s2_temporal_state_novelty_recovery_extra.csv |
| s2_temporal_state_novelty_recovery_proto | 0.737286 | outputs/s2_temporal_state_novelty_recovery_on_v51/oof_s2_temporal_state_novelty_recovery_proto.csv | outputs/s2_temporal_state_novelty_recovery_on_v51/submission_s2_temporal_state_novelty_recovery_proto.csv |
| s2_temporal_state_novelty_recovery_knn_label | 0.749480 | outputs/s2_temporal_state_novelty_recovery_on_v51/oof_s2_temporal_state_novelty_recovery_knn_label.csv | outputs/s2_temporal_state_novelty_recovery_on_v51/submission_s2_temporal_state_novelty_recovery_knn_label.csv |
| s2_temporal_state_novelty_recovery_logreg | 0.900553 | outputs/s2_temporal_state_novelty_recovery_on_v51/oof_s2_temporal_state_novelty_recovery_logreg.csv | outputs/s2_temporal_state_novelty_recovery_on_v51/submission_s2_temporal_state_novelty_recovery_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty_recovery | 385 |
