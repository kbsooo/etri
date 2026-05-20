# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.509373`
- Best source S4 OOF: `0.545934`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_sleep_retrieval_meta | 0.545934 | outputs/s4_temporal_dynamics_on_v46/oof_s4_sleep_retrieval_meta.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_sleep_retrieval_meta.csv |
| s4_temporal_leadlag_knn_resid | 0.591349 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_leadlag_knn_resid.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_leadlag_knn_resid.csv |
| s4_temporal_synchrony_knn_logitresid | 0.615168 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_synchrony_knn_logitresid.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_synchrony_knn_logitresid.csv |
| s4_temporal_motif_knn_resid | 0.626299 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_motif_knn_resid.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_motif_knn_resid.csv |
| s4_temporal_synchrony_knn_resid | 0.626872 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_synchrony_knn_resid.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_synchrony_knn_resid.csv |
| s4_temporal_leadlag_knn_logitresid | 0.633700 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_leadlag_knn_logitresid.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_leadlag_knn_logitresid.csv |
| s4_temporal_synchrony_hgb | 0.682158 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_synchrony_hgb.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_synchrony_hgb.csv |
| s4_temporal_motif_knn_logitresid | 0.683623 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_motif_knn_logitresid.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_motif_knn_logitresid.csv |
| s4_temporal_leadlag_extra | 0.685004 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_leadlag_extra.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_leadlag_extra.csv |
| s4_temporal_synchrony_extra | 0.687779 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_synchrony_extra.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_synchrony_extra.csv |
| s4_temporal_leadlag_hgb | 0.688728 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_leadlag_hgb.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_leadlag_hgb.csv |
| s4_temporal_motif_extra | 0.689953 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_motif_extra.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_motif_extra.csv |
| s4_temporal_motif_hgb | 0.700732 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_motif_hgb.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_motif_hgb.csv |
| s4_temporal_synchrony_knn_label | 0.706466 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_synchrony_knn_label.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_synchrony_knn_label.csv |
| s4_temporal_motif_knn_label | 0.712609 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_motif_knn_label.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_motif_knn_label.csv |
| s4_temporal_leadlag_knn_label | 0.726639 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_leadlag_knn_label.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_leadlag_knn_label.csv |
| s4_temporal_synchrony_proto | 0.727779 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_synchrony_proto.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_synchrony_proto.csv |
| s4_temporal_leadlag_proto | 0.756143 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_leadlag_proto.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_leadlag_proto.csv |
| s4_temporal_motif_proto | 0.757067 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_motif_proto.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_motif_proto.csv |
| s4_temporal_synchrony_logreg | 0.800729 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_synchrony_logreg.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_synchrony_logreg.csv |
| s4_temporal_leadlag_logreg | 0.899603 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_leadlag_logreg.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_leadlag_logreg.csv |
| s4_temporal_motif_logreg | 1.017819 | outputs/s4_temporal_dynamics_on_v46/oof_s4_temporal_motif_logreg.csv | outputs/s4_temporal_dynamics_on_v46/submission_s4_temporal_motif_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_synchrony | 43 |
| temporal_leadlag | 144 |
| temporal_motif | 315 |
