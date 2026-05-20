# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.464365`
- Best source S3 OOF: `0.506279`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_sleep_retrieval_meta | 0.506279 | outputs/s3_temporal_persist_regime_on_v32/oof_s3_sleep_retrieval_meta.csv | outputs/s3_temporal_persist_regime_on_v32/submission_s3_sleep_retrieval_meta.csv |
| s3_temporal_regime_knn_logitresid | 0.522064 | outputs/s3_temporal_persist_regime_on_v32/oof_s3_temporal_regime_knn_logitresid.csv | outputs/s3_temporal_persist_regime_on_v32/submission_s3_temporal_regime_knn_logitresid.csv |
| s3_temporal_regime_knn_resid | 0.524495 | outputs/s3_temporal_persist_regime_on_v32/oof_s3_temporal_regime_knn_resid.csv | outputs/s3_temporal_persist_regime_on_v32/submission_s3_temporal_regime_knn_resid.csv |
| s3_temporal_persistence_knn_logitresid | 0.564467 | outputs/s3_temporal_persist_regime_on_v32/oof_s3_temporal_persistence_knn_logitresid.csv | outputs/s3_temporal_persist_regime_on_v32/submission_s3_temporal_persistence_knn_logitresid.csv |
| s3_temporal_persistence_knn_resid | 0.569579 | outputs/s3_temporal_persist_regime_on_v32/oof_s3_temporal_persistence_knn_resid.csv | outputs/s3_temporal_persist_regime_on_v32/submission_s3_temporal_persistence_knn_resid.csv |
| s3_temporal_persistence_hgb | 0.614661 | outputs/s3_temporal_persist_regime_on_v32/oof_s3_temporal_persistence_hgb.csv | outputs/s3_temporal_persist_regime_on_v32/submission_s3_temporal_persistence_hgb.csv |
| s3_temporal_regime_knn_label | 0.642824 | outputs/s3_temporal_persist_regime_on_v32/oof_s3_temporal_regime_knn_label.csv | outputs/s3_temporal_persist_regime_on_v32/submission_s3_temporal_regime_knn_label.csv |
| s3_temporal_persistence_extra | 0.651273 | outputs/s3_temporal_persist_regime_on_v32/oof_s3_temporal_persistence_extra.csv | outputs/s3_temporal_persist_regime_on_v32/submission_s3_temporal_persistence_extra.csv |
| s3_temporal_regime_hgb | 0.671079 | outputs/s3_temporal_persist_regime_on_v32/oof_s3_temporal_regime_hgb.csv | outputs/s3_temporal_persist_regime_on_v32/submission_s3_temporal_regime_hgb.csv |
| s3_temporal_regime_extra | 0.689260 | outputs/s3_temporal_persist_regime_on_v32/oof_s3_temporal_regime_extra.csv | outputs/s3_temporal_persist_regime_on_v32/submission_s3_temporal_regime_extra.csv |
| s3_temporal_persistence_proto | 0.715791 | outputs/s3_temporal_persist_regime_on_v32/oof_s3_temporal_persistence_proto.csv | outputs/s3_temporal_persist_regime_on_v32/submission_s3_temporal_persistence_proto.csv |
| s3_temporal_regime_proto | 0.724870 | outputs/s3_temporal_persist_regime_on_v32/oof_s3_temporal_regime_proto.csv | outputs/s3_temporal_persist_regime_on_v32/submission_s3_temporal_regime_proto.csv |
| s3_temporal_persistence_knn_label | 0.756114 | outputs/s3_temporal_persist_regime_on_v32/oof_s3_temporal_persistence_knn_label.csv | outputs/s3_temporal_persist_regime_on_v32/submission_s3_temporal_persistence_knn_label.csv |
| s3_temporal_regime_logreg | 0.777465 | outputs/s3_temporal_persist_regime_on_v32/oof_s3_temporal_regime_logreg.csv | outputs/s3_temporal_persist_regime_on_v32/submission_s3_temporal_regime_logreg.csv |
| s3_temporal_persistence_logreg | 0.867948 | outputs/s3_temporal_persist_regime_on_v32/oof_s3_temporal_persistence_logreg.csv | outputs/s3_temporal_persist_regime_on_v32/submission_s3_temporal_persistence_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_persistence | 616 |
| temporal_regime | 308 |
