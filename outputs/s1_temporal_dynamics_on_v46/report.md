# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.499528`
- Best source S1 OOF: `0.564903`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_temporal_synchrony_knn_resid | 0.564903 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_synchrony_knn_resid.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_synchrony_knn_resid.csv |
| s1_sleep_retrieval_meta | 0.571017 | outputs/s1_temporal_dynamics_on_v46/oof_s1_sleep_retrieval_meta.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_sleep_retrieval_meta.csv |
| s1_temporal_leadlag_knn_resid | 0.577530 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_leadlag_knn_resid.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_leadlag_knn_resid.csv |
| s1_temporal_motif_knn_resid | 0.578601 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_motif_knn_resid.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_motif_knn_resid.csv |
| s1_temporal_synchrony_knn_logitresid | 0.587706 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_synchrony_knn_logitresid.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_synchrony_knn_logitresid.csv |
| s1_temporal_leadlag_knn_logitresid | 0.620519 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_leadlag_knn_logitresid.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_leadlag_knn_logitresid.csv |
| s1_temporal_motif_knn_logitresid | 0.624586 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_motif_knn_logitresid.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_motif_knn_logitresid.csv |
| s1_temporal_leadlag_hgb | 0.627344 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_leadlag_hgb.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_leadlag_hgb.csv |
| s1_temporal_motif_hgb | 0.631243 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_motif_hgb.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_motif_hgb.csv |
| s1_temporal_synchrony_hgb | 0.640459 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_synchrony_hgb.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_synchrony_hgb.csv |
| s1_temporal_leadlag_knn_label | 0.652695 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_leadlag_knn_label.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_leadlag_knn_label.csv |
| s1_temporal_synchrony_knn_label | 0.659686 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_synchrony_knn_label.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_synchrony_knn_label.csv |
| s1_temporal_motif_extra | 0.671431 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_motif_extra.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_motif_extra.csv |
| s1_temporal_leadlag_extra | 0.672612 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_leadlag_extra.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_leadlag_extra.csv |
| s1_temporal_motif_proto | 0.677112 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_motif_proto.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_motif_proto.csv |
| s1_temporal_motif_knn_label | 0.677882 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_motif_knn_label.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_motif_knn_label.csv |
| s1_temporal_synchrony_extra | 0.682848 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_synchrony_extra.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_synchrony_extra.csv |
| s1_temporal_leadlag_proto | 0.713997 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_leadlag_proto.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_leadlag_proto.csv |
| s1_temporal_synchrony_proto | 0.720309 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_synchrony_proto.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_synchrony_proto.csv |
| s1_temporal_synchrony_logreg | 0.840281 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_synchrony_logreg.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_synchrony_logreg.csv |
| s1_temporal_leadlag_logreg | 0.989525 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_leadlag_logreg.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_leadlag_logreg.csv |
| s1_temporal_motif_logreg | 1.056279 | outputs/s1_temporal_dynamics_on_v46/oof_s1_temporal_motif_logreg.csv | outputs/s1_temporal_dynamics_on_v46/submission_s1_temporal_motif_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_synchrony | 43 |
| temporal_leadlag | 144 |
| temporal_motif | 315 |
