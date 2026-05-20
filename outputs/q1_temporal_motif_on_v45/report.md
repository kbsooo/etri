# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.552688`
- Best source Q1 OOF: `0.573478`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.573478 | outputs/q1_temporal_motif_on_v45/oof_q1_sleep_retrieval_meta.csv | outputs/q1_temporal_motif_on_v45/submission_q1_sleep_retrieval_meta.csv |
| q1_temporal_motif_knn_resid | 0.686924 | outputs/q1_temporal_motif_on_v45/oof_q1_temporal_motif_knn_resid.csv | outputs/q1_temporal_motif_on_v45/submission_q1_temporal_motif_knn_resid.csv |
| q1_temporal_motif_extra | 0.690853 | outputs/q1_temporal_motif_on_v45/oof_q1_temporal_motif_extra.csv | outputs/q1_temporal_motif_on_v45/submission_q1_temporal_motif_extra.csv |
| q1_temporal_motif_hgb | 0.712816 | outputs/q1_temporal_motif_on_v45/oof_q1_temporal_motif_hgb.csv | outputs/q1_temporal_motif_on_v45/submission_q1_temporal_motif_hgb.csv |
| q1_temporal_motif_knn_label | 0.731875 | outputs/q1_temporal_motif_on_v45/oof_q1_temporal_motif_knn_label.csv | outputs/q1_temporal_motif_on_v45/submission_q1_temporal_motif_knn_label.csv |
| q1_temporal_motif_proto | 0.762297 | outputs/q1_temporal_motif_on_v45/oof_q1_temporal_motif_proto.csv | outputs/q1_temporal_motif_on_v45/submission_q1_temporal_motif_proto.csv |
| q1_temporal_motif_knn_logitresid | 0.774094 | outputs/q1_temporal_motif_on_v45/oof_q1_temporal_motif_knn_logitresid.csv | outputs/q1_temporal_motif_on_v45/submission_q1_temporal_motif_knn_logitresid.csv |
| q1_temporal_motif_logreg | 1.152333 | outputs/q1_temporal_motif_on_v45/oof_q1_temporal_motif_logreg.csv | outputs/q1_temporal_motif_on_v45/submission_q1_temporal_motif_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_motif | 315 |
