# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.438515`
- Best source S3 OOF: `0.481701`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_temporal_leadlag_knn_resid | 0.481701 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_leadlag_knn_resid.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_leadlag_knn_resid.csv |
| s3_sleep_retrieval_meta | 0.494169 | outputs/s3_temporal_dynamics_on_v46/oof_s3_sleep_retrieval_meta.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_sleep_retrieval_meta.csv |
| s3_temporal_synchrony_knn_resid | 0.496315 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_synchrony_knn_resid.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_synchrony_knn_resid.csv |
| s3_temporal_motif_knn_resid | 0.498947 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_motif_knn_resid.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_motif_knn_resid.csv |
| s3_temporal_motif_knn_logitresid | 0.506531 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_motif_knn_logitresid.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_motif_knn_logitresid.csv |
| s3_temporal_synchrony_knn_logitresid | 0.507058 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_synchrony_knn_logitresid.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_synchrony_knn_logitresid.csv |
| s3_temporal_leadlag_knn_logitresid | 0.515998 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_leadlag_knn_logitresid.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_leadlag_knn_logitresid.csv |
| s3_temporal_leadlag_hgb | 0.603064 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_leadlag_hgb.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_leadlag_hgb.csv |
| s3_temporal_synchrony_hgb | 0.609896 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_synchrony_hgb.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_synchrony_hgb.csv |
| s3_temporal_motif_hgb | 0.620401 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_motif_hgb.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_motif_hgb.csv |
| s3_temporal_synchrony_knn_label | 0.631941 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_synchrony_knn_label.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_synchrony_knn_label.csv |
| s3_temporal_leadlag_knn_label | 0.660705 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_leadlag_knn_label.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_leadlag_knn_label.csv |
| s3_temporal_leadlag_extra | 0.667238 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_leadlag_extra.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_leadlag_extra.csv |
| s3_temporal_synchrony_extra | 0.673682 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_synchrony_extra.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_synchrony_extra.csv |
| s3_temporal_motif_extra | 0.679734 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_motif_extra.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_motif_extra.csv |
| s3_temporal_motif_knn_label | 0.681543 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_motif_knn_label.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_motif_knn_label.csv |
| s3_temporal_motif_proto | 0.690991 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_motif_proto.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_motif_proto.csv |
| s3_temporal_leadlag_proto | 0.704234 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_leadlag_proto.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_leadlag_proto.csv |
| s3_temporal_synchrony_proto | 0.705180 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_synchrony_proto.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_synchrony_proto.csv |
| s3_temporal_synchrony_logreg | 0.778033 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_synchrony_logreg.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_synchrony_logreg.csv |
| s3_temporal_leadlag_logreg | 0.842047 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_leadlag_logreg.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_leadlag_logreg.csv |
| s3_temporal_motif_logreg | 0.888116 | outputs/s3_temporal_dynamics_on_v46/oof_s3_temporal_motif_logreg.csv | outputs/s3_temporal_dynamics_on_v46/submission_s3_temporal_motif_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_synchrony | 43 |
| temporal_leadlag | 144 |
| temporal_motif | 315 |
