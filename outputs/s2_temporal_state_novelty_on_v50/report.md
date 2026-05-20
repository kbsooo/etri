# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.478511`
- Best source S2 OOF: `0.539457`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_temporal_state_novelty_knn_resid | 0.539457 | outputs/s2_temporal_state_novelty_on_v50/oof_s2_temporal_state_novelty_knn_resid.csv | outputs/s2_temporal_state_novelty_on_v50/submission_s2_temporal_state_novelty_knn_resid.csv |
| s2_sleep_retrieval_meta | 0.541577 | outputs/s2_temporal_state_novelty_on_v50/oof_s2_sleep_retrieval_meta.csv | outputs/s2_temporal_state_novelty_on_v50/submission_s2_sleep_retrieval_meta.csv |
| s2_temporal_state_novelty_knn_logitresid | 0.607377 | outputs/s2_temporal_state_novelty_on_v50/oof_s2_temporal_state_novelty_knn_logitresid.csv | outputs/s2_temporal_state_novelty_on_v50/submission_s2_temporal_state_novelty_knn_logitresid.csv |
| s2_temporal_state_novelty_hgb | 0.635217 | outputs/s2_temporal_state_novelty_on_v50/oof_s2_temporal_state_novelty_hgb.csv | outputs/s2_temporal_state_novelty_on_v50/submission_s2_temporal_state_novelty_hgb.csv |
| s2_temporal_state_novelty_extra | 0.641442 | outputs/s2_temporal_state_novelty_on_v50/oof_s2_temporal_state_novelty_extra.csv | outputs/s2_temporal_state_novelty_on_v50/submission_s2_temporal_state_novelty_extra.csv |
| s2_temporal_state_novelty_knn_label | 0.671454 | outputs/s2_temporal_state_novelty_on_v50/oof_s2_temporal_state_novelty_knn_label.csv | outputs/s2_temporal_state_novelty_on_v50/submission_s2_temporal_state_novelty_knn_label.csv |
| s2_temporal_state_novelty_proto | 0.729032 | outputs/s2_temporal_state_novelty_on_v50/oof_s2_temporal_state_novelty_proto.csv | outputs/s2_temporal_state_novelty_on_v50/submission_s2_temporal_state_novelty_proto.csv |
| s2_temporal_state_novelty_logreg | 0.906671 | outputs/s2_temporal_state_novelty_on_v50/oof_s2_temporal_state_novelty_logreg.csv | outputs/s2_temporal_state_novelty_on_v50/submission_s2_temporal_state_novelty_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_novelty | 148 |
