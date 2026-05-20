# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.573486`
- Best source Q1 OOF: `0.598538`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.598538 | outputs/q1_temporal_persist_regime_on_v32/oof_q1_sleep_retrieval_meta.csv | outputs/q1_temporal_persist_regime_on_v32/submission_q1_sleep_retrieval_meta.csv |
| q1_temporal_regime_knn_resid | 0.608595 | outputs/q1_temporal_persist_regime_on_v32/oof_q1_temporal_regime_knn_resid.csv | outputs/q1_temporal_persist_regime_on_v32/submission_q1_temporal_regime_knn_resid.csv |
| q1_temporal_persistence_knn_resid | 0.625773 | outputs/q1_temporal_persist_regime_on_v32/oof_q1_temporal_persistence_knn_resid.csv | outputs/q1_temporal_persist_regime_on_v32/submission_q1_temporal_persistence_knn_resid.csv |
| q1_temporal_persistence_extra | 0.688034 | outputs/q1_temporal_persist_regime_on_v32/oof_q1_temporal_persistence_extra.csv | outputs/q1_temporal_persist_regime_on_v32/submission_q1_temporal_persistence_extra.csv |
| q1_temporal_regime_knn_logitresid | 0.695474 | outputs/q1_temporal_persist_regime_on_v32/oof_q1_temporal_regime_knn_logitresid.csv | outputs/q1_temporal_persist_regime_on_v32/submission_q1_temporal_regime_knn_logitresid.csv |
| q1_temporal_persistence_knn_logitresid | 0.702590 | outputs/q1_temporal_persist_regime_on_v32/oof_q1_temporal_persistence_knn_logitresid.csv | outputs/q1_temporal_persist_regime_on_v32/submission_q1_temporal_persistence_knn_logitresid.csv |
| q1_temporal_regime_extra | 0.712744 | outputs/q1_temporal_persist_regime_on_v32/oof_q1_temporal_regime_extra.csv | outputs/q1_temporal_persist_regime_on_v32/submission_q1_temporal_regime_extra.csv |
| q1_temporal_persistence_hgb | 0.714160 | outputs/q1_temporal_persist_regime_on_v32/oof_q1_temporal_persistence_hgb.csv | outputs/q1_temporal_persist_regime_on_v32/submission_q1_temporal_persistence_hgb.csv |
| q1_temporal_regime_knn_label | 0.732471 | outputs/q1_temporal_persist_regime_on_v32/oof_q1_temporal_regime_knn_label.csv | outputs/q1_temporal_persist_regime_on_v32/submission_q1_temporal_regime_knn_label.csv |
| q1_temporal_regime_hgb | 0.737411 | outputs/q1_temporal_persist_regime_on_v32/oof_q1_temporal_regime_hgb.csv | outputs/q1_temporal_persist_regime_on_v32/submission_q1_temporal_regime_hgb.csv |
| q1_temporal_persistence_knn_label | 0.756739 | outputs/q1_temporal_persist_regime_on_v32/oof_q1_temporal_persistence_knn_label.csv | outputs/q1_temporal_persist_regime_on_v32/submission_q1_temporal_persistence_knn_label.csv |
| q1_temporal_regime_logreg | 0.792009 | outputs/q1_temporal_persist_regime_on_v32/oof_q1_temporal_regime_logreg.csv | outputs/q1_temporal_persist_regime_on_v32/submission_q1_temporal_regime_logreg.csv |
| q1_temporal_persistence_proto | 0.793957 | outputs/q1_temporal_persist_regime_on_v32/oof_q1_temporal_persistence_proto.csv | outputs/q1_temporal_persist_regime_on_v32/submission_q1_temporal_persistence_proto.csv |
| q1_temporal_regime_proto | 0.799427 | outputs/q1_temporal_persist_regime_on_v32/oof_q1_temporal_regime_proto.csv | outputs/q1_temporal_persist_regime_on_v32/submission_q1_temporal_regime_proto.csv |
| q1_temporal_persistence_logreg | 0.986444 | outputs/q1_temporal_persist_regime_on_v32/oof_q1_temporal_persistence_logreg.csv | outputs/q1_temporal_persist_regime_on_v32/submission_q1_temporal_persistence_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_persistence | 616 |
| temporal_regime | 308 |
