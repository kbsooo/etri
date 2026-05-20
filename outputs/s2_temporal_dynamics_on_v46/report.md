# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.483456`
- Best source S2 OOF: `0.516233`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_temporal_synchrony_knn_resid | 0.516233 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_synchrony_knn_resid.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_synchrony_knn_resid.csv |
| s2_sleep_retrieval_meta | 0.530099 | outputs/s2_temporal_dynamics_on_v46/oof_s2_sleep_retrieval_meta.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_sleep_retrieval_meta.csv |
| s2_temporal_motif_knn_resid | 0.534081 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_motif_knn_resid.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_motif_knn_resid.csv |
| s2_temporal_leadlag_knn_resid | 0.539363 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_leadlag_knn_resid.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_leadlag_knn_resid.csv |
| s2_temporal_synchrony_knn_logitresid | 0.578942 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_synchrony_knn_logitresid.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_synchrony_knn_logitresid.csv |
| s2_temporal_motif_knn_logitresid | 0.592029 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_motif_knn_logitresid.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_motif_knn_logitresid.csv |
| s2_temporal_leadlag_knn_logitresid | 0.592776 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_leadlag_knn_logitresid.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_leadlag_knn_logitresid.csv |
| s2_temporal_synchrony_hgb | 0.638045 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_synchrony_hgb.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_synchrony_hgb.csv |
| s2_temporal_motif_hgb | 0.656436 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_motif_hgb.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_motif_hgb.csv |
| s2_temporal_leadlag_hgb | 0.675028 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_leadlag_hgb.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_leadlag_hgb.csv |
| s2_temporal_leadlag_extra | 0.678409 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_leadlag_extra.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_leadlag_extra.csv |
| s2_temporal_synchrony_extra | 0.680087 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_synchrony_extra.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_synchrony_extra.csv |
| s2_temporal_motif_knn_label | 0.686249 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_motif_knn_label.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_motif_knn_label.csv |
| s2_temporal_motif_extra | 0.692227 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_motif_extra.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_motif_extra.csv |
| s2_temporal_synchrony_knn_label | 0.703153 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_synchrony_knn_label.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_synchrony_knn_label.csv |
| s2_temporal_leadlag_knn_label | 0.703782 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_leadlag_knn_label.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_leadlag_knn_label.csv |
| s2_temporal_leadlag_proto | 0.719562 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_leadlag_proto.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_leadlag_proto.csv |
| s2_temporal_synchrony_proto | 0.736717 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_synchrony_proto.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_synchrony_proto.csv |
| s2_temporal_motif_proto | 0.742613 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_motif_proto.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_motif_proto.csv |
| s2_temporal_synchrony_logreg | 0.827866 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_synchrony_logreg.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_synchrony_logreg.csv |
| s2_temporal_leadlag_logreg | 0.924481 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_leadlag_logreg.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_leadlag_logreg.csv |
| s2_temporal_motif_logreg | 1.093734 | outputs/s2_temporal_dynamics_on_v46/oof_s2_temporal_motif_logreg.csv | outputs/s2_temporal_dynamics_on_v46/submission_s2_temporal_motif_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_synchrony | 43 |
| temporal_leadlag | 144 |
| temporal_motif | 315 |
