# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.585996`
- Best source Q2 OOF: `0.601764`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_sleep_retrieval_meta | 0.601764 | outputs/q2_temporal_persist_regime_on_v32/oof_q2_sleep_retrieval_meta.csv | outputs/q2_temporal_persist_regime_on_v32/submission_q2_sleep_retrieval_meta.csv |
| q2_temporal_regime_knn_resid | 0.615211 | outputs/q2_temporal_persist_regime_on_v32/oof_q2_temporal_regime_knn_resid.csv | outputs/q2_temporal_persist_regime_on_v32/submission_q2_temporal_regime_knn_resid.csv |
| q2_temporal_regime_knn_logitresid | 0.669017 | outputs/q2_temporal_persist_regime_on_v32/oof_q2_temporal_regime_knn_logitresid.csv | outputs/q2_temporal_persist_regime_on_v32/submission_q2_temporal_regime_knn_logitresid.csv |
| q2_temporal_persistence_knn_resid | 0.678556 | outputs/q2_temporal_persist_regime_on_v32/oof_q2_temporal_persistence_knn_resid.csv | outputs/q2_temporal_persist_regime_on_v32/submission_q2_temporal_persistence_knn_resid.csv |
| q2_temporal_regime_extra | 0.695906 | outputs/q2_temporal_persist_regime_on_v32/oof_q2_temporal_regime_extra.csv | outputs/q2_temporal_persist_regime_on_v32/submission_q2_temporal_regime_extra.csv |
| q2_temporal_regime_knn_label | 0.709998 | outputs/q2_temporal_persist_regime_on_v32/oof_q2_temporal_regime_knn_label.csv | outputs/q2_temporal_persist_regime_on_v32/submission_q2_temporal_regime_knn_label.csv |
| q2_temporal_persistence_extra | 0.710851 | outputs/q2_temporal_persist_regime_on_v32/oof_q2_temporal_persistence_extra.csv | outputs/q2_temporal_persist_regime_on_v32/submission_q2_temporal_persistence_extra.csv |
| q2_temporal_regime_hgb | 0.746874 | outputs/q2_temporal_persist_regime_on_v32/oof_q2_temporal_regime_hgb.csv | outputs/q2_temporal_persist_regime_on_v32/submission_q2_temporal_regime_hgb.csv |
| q2_temporal_persistence_hgb | 0.756128 | outputs/q2_temporal_persist_regime_on_v32/oof_q2_temporal_persistence_hgb.csv | outputs/q2_temporal_persist_regime_on_v32/submission_q2_temporal_persistence_hgb.csv |
| q2_temporal_regime_logreg | 0.768388 | outputs/q2_temporal_persist_regime_on_v32/oof_q2_temporal_regime_logreg.csv | outputs/q2_temporal_persist_regime_on_v32/submission_q2_temporal_regime_logreg.csv |
| q2_temporal_persistence_knn_label | 0.778092 | outputs/q2_temporal_persist_regime_on_v32/oof_q2_temporal_persistence_knn_label.csv | outputs/q2_temporal_persist_regime_on_v32/submission_q2_temporal_persistence_knn_label.csv |
| q2_temporal_persistence_knn_logitresid | 0.794315 | outputs/q2_temporal_persist_regime_on_v32/oof_q2_temporal_persistence_knn_logitresid.csv | outputs/q2_temporal_persist_regime_on_v32/submission_q2_temporal_persistence_knn_logitresid.csv |
| q2_temporal_persistence_proto | 0.805246 | outputs/q2_temporal_persist_regime_on_v32/oof_q2_temporal_persistence_proto.csv | outputs/q2_temporal_persist_regime_on_v32/submission_q2_temporal_persistence_proto.csv |
| q2_temporal_regime_proto | 0.816790 | outputs/q2_temporal_persist_regime_on_v32/oof_q2_temporal_regime_proto.csv | outputs/q2_temporal_persist_regime_on_v32/submission_q2_temporal_regime_proto.csv |
| q2_temporal_persistence_logreg | 1.037368 | outputs/q2_temporal_persist_regime_on_v32/oof_q2_temporal_persistence_logreg.csv | outputs/q2_temporal_persist_regime_on_v32/submission_q2_temporal_persistence_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_persistence | 616 |
| temporal_regime | 308 |
