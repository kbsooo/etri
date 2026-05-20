# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.566755`
- Best source Q2 OOF: `0.594948`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_sleep_retrieval_meta | 0.594948 | outputs/q2_temporal_dynamics_on_v46/oof_q2_sleep_retrieval_meta.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_sleep_retrieval_meta.csv |
| q2_temporal_motif_knn_resid | 0.633733 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_motif_knn_resid.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_motif_knn_resid.csv |
| q2_temporal_leadlag_knn_resid | 0.651039 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_leadlag_knn_resid.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_leadlag_knn_resid.csv |
| q2_temporal_synchrony_knn_resid | 0.658940 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_synchrony_knn_resid.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_synchrony_knn_resid.csv |
| q2_temporal_motif_knn_logitresid | 0.667061 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_motif_knn_logitresid.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_motif_knn_logitresid.csv |
| q2_temporal_leadlag_extra | 0.686224 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_leadlag_extra.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_leadlag_extra.csv |
| q2_temporal_motif_extra | 0.686614 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_motif_extra.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_motif_extra.csv |
| q2_temporal_synchrony_extra | 0.695648 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_synchrony_extra.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_synchrony_extra.csv |
| q2_temporal_motif_knn_label | 0.716159 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_motif_knn_label.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_motif_knn_label.csv |
| q2_temporal_motif_hgb | 0.717032 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_motif_hgb.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_motif_hgb.csv |
| q2_temporal_synchrony_knn_logitresid | 0.721751 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_synchrony_knn_logitresid.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_synchrony_knn_logitresid.csv |
| q2_temporal_leadlag_hgb | 0.729686 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_leadlag_hgb.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_leadlag_hgb.csv |
| q2_temporal_leadlag_knn_label | 0.735547 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_leadlag_knn_label.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_leadlag_knn_label.csv |
| q2_temporal_synchrony_hgb | 0.736879 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_synchrony_hgb.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_synchrony_hgb.csv |
| q2_temporal_synchrony_knn_label | 0.737225 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_synchrony_knn_label.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_synchrony_knn_label.csv |
| q2_temporal_leadlag_knn_logitresid | 0.746565 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_leadlag_knn_logitresid.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_leadlag_knn_logitresid.csv |
| q2_temporal_motif_proto | 0.753840 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_motif_proto.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_motif_proto.csv |
| q2_temporal_leadlag_proto | 0.802571 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_leadlag_proto.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_leadlag_proto.csv |
| q2_temporal_synchrony_proto | 0.812497 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_synchrony_proto.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_synchrony_proto.csv |
| q2_temporal_synchrony_logreg | 0.882286 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_synchrony_logreg.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_synchrony_logreg.csv |
| q2_temporal_motif_logreg | 0.909723 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_motif_logreg.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_motif_logreg.csv |
| q2_temporal_leadlag_logreg | 1.015245 | outputs/q2_temporal_dynamics_on_v46/oof_q2_temporal_leadlag_logreg.csv | outputs/q2_temporal_dynamics_on_v46/submission_q2_temporal_leadlag_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_synchrony | 43 |
| temporal_leadlag | 144 |
| temporal_motif | 315 |
