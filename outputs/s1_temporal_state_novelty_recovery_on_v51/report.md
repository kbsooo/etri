# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.494487`
- Best source S1 OOF: `0.575397`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_sleep_retrieval_meta | 0.575397 | outputs/s1_temporal_state_novelty_recovery_on_v51/oof_s1_sleep_retrieval_meta.csv | outputs/s1_temporal_state_novelty_recovery_on_v51/submission_s1_sleep_retrieval_meta.csv |
| s1_temporal_state_novelty_recovery_knn_resid | 0.580275 | outputs/s1_temporal_state_novelty_recovery_on_v51/oof_s1_temporal_state_novelty_recovery_knn_resid.csv | outputs/s1_temporal_state_novelty_recovery_on_v51/submission_s1_temporal_state_novelty_recovery_knn_resid.csv |
| s1_temporal_state_novelty_recovery_hgb | 0.620083 | outputs/s1_temporal_state_novelty_recovery_on_v51/oof_s1_temporal_state_novelty_recovery_hgb.csv | outputs/s1_temporal_state_novelty_recovery_on_v51/submission_s1_temporal_state_novelty_recovery_hgb.csv |
| s1_temporal_state_novelty_recovery_knn_logitresid | 0.633732 | outputs/s1_temporal_state_novelty_recovery_on_v51/oof_s1_temporal_state_novelty_recovery_knn_logitresid.csv | outputs/s1_temporal_state_novelty_recovery_on_v51/submission_s1_temporal_state_novelty_recovery_knn_logitresid.csv |
| s1_temporal_state_novelty_recovery_knn_label | 0.664979 | outputs/s1_temporal_state_novelty_recovery_on_v51/oof_s1_temporal_state_novelty_recovery_knn_label.csv | outputs/s1_temporal_state_novelty_recovery_on_v51/submission_s1_temporal_state_novelty_recovery_knn_label.csv |
| s1_temporal_state_novelty_recovery_extra | 0.682396 | outputs/s1_temporal_state_novelty_recovery_on_v51/oof_s1_temporal_state_novelty_recovery_extra.csv | outputs/s1_temporal_state_novelty_recovery_on_v51/submission_s1_temporal_state_novelty_recovery_extra.csv |
| s1_temporal_state_novelty_recovery_proto | 0.726643 | outputs/s1_temporal_state_novelty_recovery_on_v51/oof_s1_temporal_state_novelty_recovery_proto.csv | outputs/s1_temporal_state_novelty_recovery_on_v51/submission_s1_temporal_state_novelty_recovery_proto.csv |
| s1_temporal_state_novelty_recovery_logreg | 0.933244 | outputs/s1_temporal_state_novelty_recovery_on_v51/oof_s1_temporal_state_novelty_recovery_logreg.csv | outputs/s1_temporal_state_novelty_recovery_on_v51/submission_s1_temporal_state_novelty_recovery_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty_recovery | 385 |
