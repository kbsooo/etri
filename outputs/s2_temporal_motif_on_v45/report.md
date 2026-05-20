# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.486476`
- Best source S2 OOF: `0.529352`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_temporal_motif_knn_resid | 0.529352 | outputs/s2_temporal_motif_on_v45/oof_s2_temporal_motif_knn_resid.csv | outputs/s2_temporal_motif_on_v45/submission_s2_temporal_motif_knn_resid.csv |
| s2_sleep_retrieval_meta | 0.536497 | outputs/s2_temporal_motif_on_v45/oof_s2_sleep_retrieval_meta.csv | outputs/s2_temporal_motif_on_v45/submission_s2_sleep_retrieval_meta.csv |
| s2_temporal_motif_knn_logitresid | 0.587500 | outputs/s2_temporal_motif_on_v45/oof_s2_temporal_motif_knn_logitresid.csv | outputs/s2_temporal_motif_on_v45/submission_s2_temporal_motif_knn_logitresid.csv |
| s2_temporal_motif_hgb | 0.656436 | outputs/s2_temporal_motif_on_v45/oof_s2_temporal_motif_hgb.csv | outputs/s2_temporal_motif_on_v45/submission_s2_temporal_motif_hgb.csv |
| s2_temporal_motif_knn_label | 0.686249 | outputs/s2_temporal_motif_on_v45/oof_s2_temporal_motif_knn_label.csv | outputs/s2_temporal_motif_on_v45/submission_s2_temporal_motif_knn_label.csv |
| s2_temporal_motif_extra | 0.692227 | outputs/s2_temporal_motif_on_v45/oof_s2_temporal_motif_extra.csv | outputs/s2_temporal_motif_on_v45/submission_s2_temporal_motif_extra.csv |
| s2_temporal_motif_proto | 0.742613 | outputs/s2_temporal_motif_on_v45/oof_s2_temporal_motif_proto.csv | outputs/s2_temporal_motif_on_v45/submission_s2_temporal_motif_proto.csv |
| s2_temporal_motif_logreg | 1.093734 | outputs/s2_temporal_motif_on_v45/oof_s2_temporal_motif_logreg.csv | outputs/s2_temporal_motif_on_v45/submission_s2_temporal_motif_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_motif | 315 |
