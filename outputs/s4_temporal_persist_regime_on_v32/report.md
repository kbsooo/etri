# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.539153`
- Best source S4 OOF: `0.551878`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_sleep_retrieval_meta | 0.551878 | outputs/s4_temporal_persist_regime_on_v32/oof_s4_sleep_retrieval_meta.csv | outputs/s4_temporal_persist_regime_on_v32/submission_s4_sleep_retrieval_meta.csv |
| s4_temporal_persistence_knn_resid | 0.637618 | outputs/s4_temporal_persist_regime_on_v32/oof_s4_temporal_persistence_knn_resid.csv | outputs/s4_temporal_persist_regime_on_v32/submission_s4_temporal_persistence_knn_resid.csv |
| s4_temporal_persistence_hgb | 0.667831 | outputs/s4_temporal_persist_regime_on_v32/oof_s4_temporal_persistence_hgb.csv | outputs/s4_temporal_persist_regime_on_v32/submission_s4_temporal_persistence_hgb.csv |
| s4_temporal_persistence_extra | 0.675538 | outputs/s4_temporal_persist_regime_on_v32/oof_s4_temporal_persistence_extra.csv | outputs/s4_temporal_persist_regime_on_v32/submission_s4_temporal_persistence_extra.csv |
| s4_temporal_persistence_knn_logitresid | 0.702731 | outputs/s4_temporal_persist_regime_on_v32/oof_s4_temporal_persistence_knn_logitresid.csv | outputs/s4_temporal_persist_regime_on_v32/submission_s4_temporal_persistence_knn_logitresid.csv |
| s4_temporal_regime_extra | 0.704171 | outputs/s4_temporal_persist_regime_on_v32/oof_s4_temporal_regime_extra.csv | outputs/s4_temporal_persist_regime_on_v32/submission_s4_temporal_regime_extra.csv |
| s4_temporal_regime_hgb | 0.727490 | outputs/s4_temporal_persist_regime_on_v32/oof_s4_temporal_regime_hgb.csv | outputs/s4_temporal_persist_regime_on_v32/submission_s4_temporal_regime_hgb.csv |
| s4_temporal_regime_knn_resid | 0.731882 | outputs/s4_temporal_persist_regime_on_v32/oof_s4_temporal_regime_knn_resid.csv | outputs/s4_temporal_persist_regime_on_v32/submission_s4_temporal_regime_knn_resid.csv |
| s4_temporal_persistence_knn_label | 0.734555 | outputs/s4_temporal_persist_regime_on_v32/oof_s4_temporal_persistence_knn_label.csv | outputs/s4_temporal_persist_regime_on_v32/submission_s4_temporal_persistence_knn_label.csv |
| s4_temporal_regime_knn_label | 0.737007 | outputs/s4_temporal_persist_regime_on_v32/oof_s4_temporal_regime_knn_label.csv | outputs/s4_temporal_persist_regime_on_v32/submission_s4_temporal_regime_knn_label.csv |
| s4_temporal_regime_logreg | 0.767741 | outputs/s4_temporal_persist_regime_on_v32/oof_s4_temporal_regime_logreg.csv | outputs/s4_temporal_persist_regime_on_v32/submission_s4_temporal_regime_logreg.csv |
| s4_temporal_regime_proto | 0.777616 | outputs/s4_temporal_persist_regime_on_v32/oof_s4_temporal_regime_proto.csv | outputs/s4_temporal_persist_regime_on_v32/submission_s4_temporal_regime_proto.csv |
| s4_temporal_regime_knn_logitresid | 0.807797 | outputs/s4_temporal_persist_regime_on_v32/oof_s4_temporal_regime_knn_logitresid.csv | outputs/s4_temporal_persist_regime_on_v32/submission_s4_temporal_regime_knn_logitresid.csv |
| s4_temporal_persistence_proto | 0.826437 | outputs/s4_temporal_persist_regime_on_v32/oof_s4_temporal_persistence_proto.csv | outputs/s4_temporal_persist_regime_on_v32/submission_s4_temporal_persistence_proto.csv |
| s4_temporal_persistence_logreg | 0.999943 | outputs/s4_temporal_persist_regime_on_v32/oof_s4_temporal_persistence_logreg.csv | outputs/s4_temporal_persist_regime_on_v32/submission_s4_temporal_persistence_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_persistence | 616 |
| temporal_regime | 308 |
