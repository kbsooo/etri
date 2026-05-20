# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.491178`
- Best source S2 OOF: `0.542241`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_sleep_retrieval_meta | 0.542241 | outputs/s2_temporal_persist_regime_on_v32/oof_s2_sleep_retrieval_meta.csv | outputs/s2_temporal_persist_regime_on_v32/submission_s2_sleep_retrieval_meta.csv |
| s2_temporal_persistence_knn_resid | 0.585949 | outputs/s2_temporal_persist_regime_on_v32/oof_s2_temporal_persistence_knn_resid.csv | outputs/s2_temporal_persist_regime_on_v32/submission_s2_temporal_persistence_knn_resid.csv |
| s2_temporal_persistence_knn_logitresid | 0.607681 | outputs/s2_temporal_persist_regime_on_v32/oof_s2_temporal_persistence_knn_logitresid.csv | outputs/s2_temporal_persist_regime_on_v32/submission_s2_temporal_persistence_knn_logitresid.csv |
| s2_temporal_persistence_hgb | 0.638620 | outputs/s2_temporal_persist_regime_on_v32/oof_s2_temporal_persistence_hgb.csv | outputs/s2_temporal_persist_regime_on_v32/submission_s2_temporal_persistence_hgb.csv |
| s2_temporal_regime_knn_resid | 0.669533 | outputs/s2_temporal_persist_regime_on_v32/oof_s2_temporal_regime_knn_resid.csv | outputs/s2_temporal_persist_regime_on_v32/submission_s2_temporal_regime_knn_resid.csv |
| s2_temporal_persistence_extra | 0.675829 | outputs/s2_temporal_persist_regime_on_v32/oof_s2_temporal_persistence_extra.csv | outputs/s2_temporal_persist_regime_on_v32/submission_s2_temporal_persistence_extra.csv |
| s2_temporal_regime_hgb | 0.681522 | outputs/s2_temporal_persist_regime_on_v32/oof_s2_temporal_regime_hgb.csv | outputs/s2_temporal_persist_regime_on_v32/submission_s2_temporal_regime_hgb.csv |
| s2_temporal_regime_extra | 0.683142 | outputs/s2_temporal_persist_regime_on_v32/oof_s2_temporal_regime_extra.csv | outputs/s2_temporal_persist_regime_on_v32/submission_s2_temporal_regime_extra.csv |
| s2_temporal_regime_knn_logitresid | 0.690140 | outputs/s2_temporal_persist_regime_on_v32/oof_s2_temporal_regime_knn_logitresid.csv | outputs/s2_temporal_persist_regime_on_v32/submission_s2_temporal_regime_knn_logitresid.csv |
| s2_temporal_persistence_knn_label | 0.691590 | outputs/s2_temporal_persist_regime_on_v32/oof_s2_temporal_persistence_knn_label.csv | outputs/s2_temporal_persist_regime_on_v32/submission_s2_temporal_persistence_knn_label.csv |
| s2_temporal_regime_proto | 0.699691 | outputs/s2_temporal_persist_regime_on_v32/oof_s2_temporal_regime_proto.csv | outputs/s2_temporal_persist_regime_on_v32/submission_s2_temporal_regime_proto.csv |
| s2_temporal_regime_knn_label | 0.706751 | outputs/s2_temporal_persist_regime_on_v32/oof_s2_temporal_regime_knn_label.csv | outputs/s2_temporal_persist_regime_on_v32/submission_s2_temporal_regime_knn_label.csv |
| s2_temporal_persistence_proto | 0.716333 | outputs/s2_temporal_persist_regime_on_v32/oof_s2_temporal_persistence_proto.csv | outputs/s2_temporal_persist_regime_on_v32/submission_s2_temporal_persistence_proto.csv |
| s2_temporal_regime_logreg | 0.746100 | outputs/s2_temporal_persist_regime_on_v32/oof_s2_temporal_regime_logreg.csv | outputs/s2_temporal_persist_regime_on_v32/submission_s2_temporal_regime_logreg.csv |
| s2_temporal_persistence_logreg | 0.847515 | outputs/s2_temporal_persist_regime_on_v32/oof_s2_temporal_persistence_logreg.csv | outputs/s2_temporal_persist_regime_on_v32/submission_s2_temporal_persistence_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_persistence | 616 |
| temporal_regime | 308 |
