# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.500456`
- Best source S1 OOF: `0.552991`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_temporal_motif_knn_resid | 0.552991 | outputs/s1_temporal_motif_on_v45/oof_s1_temporal_motif_knn_resid.csv | outputs/s1_temporal_motif_on_v45/submission_s1_temporal_motif_knn_resid.csv |
| s1_sleep_retrieval_meta | 0.578091 | outputs/s1_temporal_motif_on_v45/oof_s1_sleep_retrieval_meta.csv | outputs/s1_temporal_motif_on_v45/submission_s1_sleep_retrieval_meta.csv |
| s1_temporal_motif_knn_logitresid | 0.618953 | outputs/s1_temporal_motif_on_v45/oof_s1_temporal_motif_knn_logitresid.csv | outputs/s1_temporal_motif_on_v45/submission_s1_temporal_motif_knn_logitresid.csv |
| s1_temporal_motif_hgb | 0.631243 | outputs/s1_temporal_motif_on_v45/oof_s1_temporal_motif_hgb.csv | outputs/s1_temporal_motif_on_v45/submission_s1_temporal_motif_hgb.csv |
| s1_temporal_motif_extra | 0.671431 | outputs/s1_temporal_motif_on_v45/oof_s1_temporal_motif_extra.csv | outputs/s1_temporal_motif_on_v45/submission_s1_temporal_motif_extra.csv |
| s1_temporal_motif_proto | 0.677112 | outputs/s1_temporal_motif_on_v45/oof_s1_temporal_motif_proto.csv | outputs/s1_temporal_motif_on_v45/submission_s1_temporal_motif_proto.csv |
| s1_temporal_motif_knn_label | 0.677882 | outputs/s1_temporal_motif_on_v45/oof_s1_temporal_motif_knn_label.csv | outputs/s1_temporal_motif_on_v45/submission_s1_temporal_motif_knn_label.csv |
| s1_temporal_motif_logreg | 1.056279 | outputs/s1_temporal_motif_on_v45/oof_s1_temporal_motif_logreg.csv | outputs/s1_temporal_motif_on_v45/submission_s1_temporal_motif_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_motif | 315 |
