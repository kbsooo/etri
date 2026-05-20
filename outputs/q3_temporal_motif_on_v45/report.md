# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.541882`
- Best source Q3 OOF: `0.557308`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_sleep_retrieval_meta | 0.557308 | outputs/q3_temporal_motif_on_v45/oof_q3_sleep_retrieval_meta.csv | outputs/q3_temporal_motif_on_v45/submission_q3_sleep_retrieval_meta.csv |
| q3_temporal_motif_knn_resid | 0.587872 | outputs/q3_temporal_motif_on_v45/oof_q3_temporal_motif_knn_resid.csv | outputs/q3_temporal_motif_on_v45/submission_q3_temporal_motif_knn_resid.csv |
| q3_temporal_motif_knn_logitresid | 0.627179 | outputs/q3_temporal_motif_on_v45/oof_q3_temporal_motif_knn_logitresid.csv | outputs/q3_temporal_motif_on_v45/submission_q3_temporal_motif_knn_logitresid.csv |
| q3_temporal_motif_extra | 0.698019 | outputs/q3_temporal_motif_on_v45/oof_q3_temporal_motif_extra.csv | outputs/q3_temporal_motif_on_v45/submission_q3_temporal_motif_extra.csv |
| q3_temporal_motif_knn_label | 0.711796 | outputs/q3_temporal_motif_on_v45/oof_q3_temporal_motif_knn_label.csv | outputs/q3_temporal_motif_on_v45/submission_q3_temporal_motif_knn_label.csv |
| q3_temporal_motif_hgb | 0.734807 | outputs/q3_temporal_motif_on_v45/oof_q3_temporal_motif_hgb.csv | outputs/q3_temporal_motif_on_v45/submission_q3_temporal_motif_hgb.csv |
| q3_temporal_motif_proto | 0.790437 | outputs/q3_temporal_motif_on_v45/oof_q3_temporal_motif_proto.csv | outputs/q3_temporal_motif_on_v45/submission_q3_temporal_motif_proto.csv |
| q3_temporal_motif_logreg | 1.008999 | outputs/q3_temporal_motif_on_v45/oof_q3_temporal_motif_logreg.csv | outputs/q3_temporal_motif_on_v45/submission_q3_temporal_motif_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_motif | 315 |
