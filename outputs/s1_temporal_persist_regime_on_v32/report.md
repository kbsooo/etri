# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.519394`
- Best source S1 OOF: `0.563552`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_temporal_persistence_knn_resid | 0.563552 | outputs/s1_temporal_persist_regime_on_v32/oof_s1_temporal_persistence_knn_resid.csv | outputs/s1_temporal_persist_regime_on_v32/submission_s1_temporal_persistence_knn_resid.csv |
| s1_sleep_retrieval_meta | 0.578722 | outputs/s1_temporal_persist_regime_on_v32/oof_s1_sleep_retrieval_meta.csv | outputs/s1_temporal_persist_regime_on_v32/submission_s1_sleep_retrieval_meta.csv |
| s1_temporal_regime_knn_resid | 0.582507 | outputs/s1_temporal_persist_regime_on_v32/oof_s1_temporal_regime_knn_resid.csv | outputs/s1_temporal_persist_regime_on_v32/submission_s1_temporal_regime_knn_resid.csv |
| s1_temporal_regime_knn_logitresid | 0.636651 | outputs/s1_temporal_persist_regime_on_v32/oof_s1_temporal_regime_knn_logitresid.csv | outputs/s1_temporal_persist_regime_on_v32/submission_s1_temporal_regime_knn_logitresid.csv |
| s1_temporal_persistence_knn_logitresid | 0.646434 | outputs/s1_temporal_persist_regime_on_v32/oof_s1_temporal_persistence_knn_logitresid.csv | outputs/s1_temporal_persist_regime_on_v32/submission_s1_temporal_persistence_knn_logitresid.csv |
| s1_temporal_persistence_hgb | 0.651945 | outputs/s1_temporal_persist_regime_on_v32/oof_s1_temporal_persistence_hgb.csv | outputs/s1_temporal_persist_regime_on_v32/submission_s1_temporal_persistence_hgb.csv |
| s1_temporal_persistence_knn_label | 0.653799 | outputs/s1_temporal_persist_regime_on_v32/oof_s1_temporal_persistence_knn_label.csv | outputs/s1_temporal_persist_regime_on_v32/submission_s1_temporal_persistence_knn_label.csv |
| s1_temporal_regime_hgb | 0.659955 | outputs/s1_temporal_persist_regime_on_v32/oof_s1_temporal_regime_hgb.csv | outputs/s1_temporal_persist_regime_on_v32/submission_s1_temporal_regime_hgb.csv |
| s1_temporal_persistence_extra | 0.666612 | outputs/s1_temporal_persist_regime_on_v32/oof_s1_temporal_persistence_extra.csv | outputs/s1_temporal_persist_regime_on_v32/submission_s1_temporal_persistence_extra.csv |
| s1_temporal_regime_knn_label | 0.671425 | outputs/s1_temporal_persist_regime_on_v32/oof_s1_temporal_regime_knn_label.csv | outputs/s1_temporal_persist_regime_on_v32/submission_s1_temporal_regime_knn_label.csv |
| s1_temporal_regime_extra | 0.691734 | outputs/s1_temporal_persist_regime_on_v32/oof_s1_temporal_regime_extra.csv | outputs/s1_temporal_persist_regime_on_v32/submission_s1_temporal_regime_extra.csv |
| s1_temporal_regime_proto | 0.698443 | outputs/s1_temporal_persist_regime_on_v32/oof_s1_temporal_regime_proto.csv | outputs/s1_temporal_persist_regime_on_v32/submission_s1_temporal_regime_proto.csv |
| s1_temporal_persistence_proto | 0.737081 | outputs/s1_temporal_persist_regime_on_v32/oof_s1_temporal_persistence_proto.csv | outputs/s1_temporal_persist_regime_on_v32/submission_s1_temporal_persistence_proto.csv |
| s1_temporal_regime_logreg | 0.768337 | outputs/s1_temporal_persist_regime_on_v32/oof_s1_temporal_regime_logreg.csv | outputs/s1_temporal_persist_regime_on_v32/submission_s1_temporal_regime_logreg.csv |
| s1_temporal_persistence_logreg | 0.869674 | outputs/s1_temporal_persist_regime_on_v32/oof_s1_temporal_persistence_logreg.csv | outputs/s1_temporal_persist_regime_on_v32/submission_s1_temporal_persistence_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_persistence | 616 |
| temporal_regime | 308 |
