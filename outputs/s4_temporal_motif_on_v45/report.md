# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.509768`
- Best source S4 OOF: `0.538803`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_sleep_retrieval_meta | 0.538803 | outputs/s4_temporal_motif_on_v45/oof_s4_sleep_retrieval_meta.csv | outputs/s4_temporal_motif_on_v45/submission_s4_sleep_retrieval_meta.csv |
| s4_temporal_motif_knn_resid | 0.622481 | outputs/s4_temporal_motif_on_v45/oof_s4_temporal_motif_knn_resid.csv | outputs/s4_temporal_motif_on_v45/submission_s4_temporal_motif_knn_resid.csv |
| s4_temporal_motif_knn_logitresid | 0.679868 | outputs/s4_temporal_motif_on_v45/oof_s4_temporal_motif_knn_logitresid.csv | outputs/s4_temporal_motif_on_v45/submission_s4_temporal_motif_knn_logitresid.csv |
| s4_temporal_motif_extra | 0.689953 | outputs/s4_temporal_motif_on_v45/oof_s4_temporal_motif_extra.csv | outputs/s4_temporal_motif_on_v45/submission_s4_temporal_motif_extra.csv |
| s4_temporal_motif_hgb | 0.700732 | outputs/s4_temporal_motif_on_v45/oof_s4_temporal_motif_hgb.csv | outputs/s4_temporal_motif_on_v45/submission_s4_temporal_motif_hgb.csv |
| s4_temporal_motif_knn_label | 0.712609 | outputs/s4_temporal_motif_on_v45/oof_s4_temporal_motif_knn_label.csv | outputs/s4_temporal_motif_on_v45/submission_s4_temporal_motif_knn_label.csv |
| s4_temporal_motif_proto | 0.757067 | outputs/s4_temporal_motif_on_v45/oof_s4_temporal_motif_proto.csv | outputs/s4_temporal_motif_on_v45/submission_s4_temporal_motif_proto.csv |
| s4_temporal_motif_logreg | 1.017819 | outputs/s4_temporal_motif_on_v45/oof_s4_temporal_motif_logreg.csv | outputs/s4_temporal_motif_on_v45/submission_s4_temporal_motif_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_motif | 315 |
