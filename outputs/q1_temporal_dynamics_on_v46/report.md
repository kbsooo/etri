# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.552688`
- Best source Q1 OOF: `0.572517`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.572517 | outputs/q1_temporal_dynamics_on_v46/oof_q1_sleep_retrieval_meta.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_sleep_retrieval_meta.csv |
| q1_temporal_leadlag_knn_resid | 0.602101 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_leadlag_knn_resid.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_leadlag_knn_resid.csv |
| q1_temporal_synchrony_knn_resid | 0.604175 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_synchrony_knn_resid.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_synchrony_knn_resid.csv |
| q1_temporal_leadlag_knn_logitresid | 0.639431 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_leadlag_knn_logitresid.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_leadlag_knn_logitresid.csv |
| q1_temporal_synchrony_knn_logitresid | 0.657752 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_synchrony_knn_logitresid.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_synchrony_knn_logitresid.csv |
| q1_temporal_motif_knn_resid | 0.686924 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_motif_knn_resid.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_motif_knn_resid.csv |
| q1_temporal_leadlag_extra | 0.687258 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_leadlag_extra.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_leadlag_extra.csv |
| q1_temporal_motif_extra | 0.690853 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_motif_extra.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_motif_extra.csv |
| q1_temporal_synchrony_extra | 0.700622 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_synchrony_extra.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_synchrony_extra.csv |
| q1_temporal_leadlag_knn_label | 0.711383 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_leadlag_knn_label.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_leadlag_knn_label.csv |
| q1_temporal_motif_hgb | 0.712816 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_motif_hgb.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_motif_hgb.csv |
| q1_temporal_synchrony_hgb | 0.719611 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_synchrony_hgb.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_synchrony_hgb.csv |
| q1_temporal_leadlag_hgb | 0.726112 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_leadlag_hgb.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_leadlag_hgb.csv |
| q1_temporal_motif_knn_label | 0.731875 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_motif_knn_label.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_motif_knn_label.csv |
| q1_temporal_synchrony_knn_label | 0.740502 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_synchrony_knn_label.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_synchrony_knn_label.csv |
| q1_temporal_leadlag_proto | 0.758872 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_leadlag_proto.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_leadlag_proto.csv |
| q1_temporal_motif_proto | 0.762297 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_motif_proto.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_motif_proto.csv |
| q1_temporal_motif_knn_logitresid | 0.774094 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_motif_knn_logitresid.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_motif_knn_logitresid.csv |
| q1_temporal_synchrony_proto | 0.794764 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_synchrony_proto.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_synchrony_proto.csv |
| q1_temporal_leadlag_logreg | 0.839986 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_leadlag_logreg.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_leadlag_logreg.csv |
| q1_temporal_synchrony_logreg | 0.854943 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_synchrony_logreg.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_synchrony_logreg.csv |
| q1_temporal_motif_logreg | 1.152333 | outputs/q1_temporal_dynamics_on_v46/oof_q1_temporal_motif_logreg.csv | outputs/q1_temporal_dynamics_on_v46/submission_q1_temporal_motif_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_synchrony | 43 |
| temporal_leadlag | 144 |
| temporal_motif | 315 |
