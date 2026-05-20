# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.558924`
- Best source Q3 OOF: `0.580951`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_temporal_regime_knn_resid | 0.580951 | outputs/q3_temporal_persist_regime_on_v32/oof_q3_temporal_regime_knn_resid.csv | outputs/q3_temporal_persist_regime_on_v32/submission_q3_temporal_regime_knn_resid.csv |
| q3_sleep_retrieval_meta | 0.613103 | outputs/q3_temporal_persist_regime_on_v32/oof_q3_sleep_retrieval_meta.csv | outputs/q3_temporal_persist_regime_on_v32/submission_q3_sleep_retrieval_meta.csv |
| q3_temporal_persistence_knn_resid | 0.630142 | outputs/q3_temporal_persist_regime_on_v32/oof_q3_temporal_persistence_knn_resid.csv | outputs/q3_temporal_persist_regime_on_v32/submission_q3_temporal_persistence_knn_resid.csv |
| q3_temporal_regime_knn_logitresid | 0.641342 | outputs/q3_temporal_persist_regime_on_v32/oof_q3_temporal_regime_knn_logitresid.csv | outputs/q3_temporal_persist_regime_on_v32/submission_q3_temporal_regime_knn_logitresid.csv |
| q3_temporal_persistence_extra | 0.682365 | outputs/q3_temporal_persist_regime_on_v32/oof_q3_temporal_persistence_extra.csv | outputs/q3_temporal_persist_regime_on_v32/submission_q3_temporal_persistence_extra.csv |
| q3_temporal_persistence_hgb | 0.688238 | outputs/q3_temporal_persist_regime_on_v32/oof_q3_temporal_persistence_hgb.csv | outputs/q3_temporal_persist_regime_on_v32/submission_q3_temporal_persistence_hgb.csv |
| q3_temporal_regime_knn_label | 0.690022 | outputs/q3_temporal_persist_regime_on_v32/oof_q3_temporal_regime_knn_label.csv | outputs/q3_temporal_persist_regime_on_v32/submission_q3_temporal_regime_knn_label.csv |
| q3_temporal_regime_extra | 0.690928 | outputs/q3_temporal_persist_regime_on_v32/oof_q3_temporal_regime_extra.csv | outputs/q3_temporal_persist_regime_on_v32/submission_q3_temporal_regime_extra.csv |
| q3_temporal_persistence_knn_logitresid | 0.699724 | outputs/q3_temporal_persist_regime_on_v32/oof_q3_temporal_persistence_knn_logitresid.csv | outputs/q3_temporal_persist_regime_on_v32/submission_q3_temporal_persistence_knn_logitresid.csv |
| q3_temporal_regime_hgb | 0.701354 | outputs/q3_temporal_persist_regime_on_v32/oof_q3_temporal_regime_hgb.csv | outputs/q3_temporal_persist_regime_on_v32/submission_q3_temporal_regime_hgb.csv |
| q3_temporal_persistence_knn_label | 0.754876 | outputs/q3_temporal_persist_regime_on_v32/oof_q3_temporal_persistence_knn_label.csv | outputs/q3_temporal_persist_regime_on_v32/submission_q3_temporal_persistence_knn_label.csv |
| q3_temporal_regime_proto | 0.761048 | outputs/q3_temporal_persist_regime_on_v32/oof_q3_temporal_regime_proto.csv | outputs/q3_temporal_persist_regime_on_v32/submission_q3_temporal_regime_proto.csv |
| q3_temporal_persistence_proto | 0.781539 | outputs/q3_temporal_persist_regime_on_v32/oof_q3_temporal_persistence_proto.csv | outputs/q3_temporal_persist_regime_on_v32/submission_q3_temporal_persistence_proto.csv |
| q3_temporal_regime_logreg | 0.804269 | outputs/q3_temporal_persist_regime_on_v32/oof_q3_temporal_regime_logreg.csv | outputs/q3_temporal_persist_regime_on_v32/submission_q3_temporal_regime_logreg.csv |
| q3_temporal_persistence_logreg | 1.090861 | outputs/q3_temporal_persist_regime_on_v32/oof_q3_temporal_persistence_logreg.csv | outputs/q3_temporal_persist_regime_on_v32/submission_q3_temporal_persistence_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_persistence | 616 |
| temporal_regime | 308 |
