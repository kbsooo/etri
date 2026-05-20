# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.538393`
- Best source Q3 OOF: `0.566314`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_sleep_retrieval_meta | 0.566314 | outputs/q3_temporal_dynamics_on_v46/oof_q3_sleep_retrieval_meta.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_sleep_retrieval_meta.csv |
| q3_temporal_leadlag_knn_resid | 0.570944 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_leadlag_knn_resid.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_leadlag_knn_resid.csv |
| q3_temporal_motif_knn_resid | 0.600881 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_motif_knn_resid.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_motif_knn_resid.csv |
| q3_temporal_motif_knn_logitresid | 0.625149 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_motif_knn_logitresid.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_motif_knn_logitresid.csv |
| q3_temporal_leadlag_knn_logitresid | 0.633527 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_leadlag_knn_logitresid.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_leadlag_knn_logitresid.csv |
| q3_temporal_synchrony_knn_resid | 0.657910 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_synchrony_knn_resid.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_synchrony_knn_resid.csv |
| q3_temporal_synchrony_knn_logitresid | 0.664242 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_synchrony_knn_logitresid.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_synchrony_knn_logitresid.csv |
| q3_temporal_leadlag_extra | 0.688991 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_leadlag_extra.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_leadlag_extra.csv |
| q3_temporal_synchrony_extra | 0.691709 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_synchrony_extra.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_synchrony_extra.csv |
| q3_temporal_motif_extra | 0.698019 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_motif_extra.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_motif_extra.csv |
| q3_temporal_leadlag_hgb | 0.698751 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_leadlag_hgb.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_leadlag_hgb.csv |
| q3_temporal_synchrony_hgb | 0.699725 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_synchrony_hgb.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_synchrony_hgb.csv |
| q3_temporal_leadlag_knn_label | 0.701500 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_leadlag_knn_label.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_leadlag_knn_label.csv |
| q3_temporal_synchrony_knn_label | 0.703577 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_synchrony_knn_label.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_synchrony_knn_label.csv |
| q3_temporal_motif_knn_label | 0.711796 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_motif_knn_label.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_motif_knn_label.csv |
| q3_temporal_motif_hgb | 0.734807 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_motif_hgb.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_motif_hgb.csv |
| q3_temporal_leadlag_proto | 0.749756 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_leadlag_proto.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_leadlag_proto.csv |
| q3_temporal_synchrony_proto | 0.785495 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_synchrony_proto.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_synchrony_proto.csv |
| q3_temporal_motif_proto | 0.790437 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_motif_proto.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_motif_proto.csv |
| q3_temporal_synchrony_logreg | 0.871819 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_synchrony_logreg.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_synchrony_logreg.csv |
| q3_temporal_leadlag_logreg | 0.901718 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_leadlag_logreg.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_leadlag_logreg.csv |
| q3_temporal_motif_logreg | 1.008999 | outputs/q3_temporal_dynamics_on_v46/oof_q3_temporal_motif_logreg.csv | outputs/q3_temporal_dynamics_on_v46/submission_q3_temporal_motif_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_synchrony | 43 |
| temporal_leadlag | 144 |
| temporal_motif | 315 |
