# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.570849`
- Best source Q2 OOF: `0.583327`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_temporal_motif_knn_resid | 0.583327 | outputs/q2_temporal_motif_on_v45/oof_q2_temporal_motif_knn_resid.csv | outputs/q2_temporal_motif_on_v45/submission_q2_temporal_motif_knn_resid.csv |
| q2_sleep_retrieval_meta | 0.590964 | outputs/q2_temporal_motif_on_v45/oof_q2_sleep_retrieval_meta.csv | outputs/q2_temporal_motif_on_v45/submission_q2_sleep_retrieval_meta.csv |
| q2_temporal_motif_knn_logitresid | 0.647270 | outputs/q2_temporal_motif_on_v45/oof_q2_temporal_motif_knn_logitresid.csv | outputs/q2_temporal_motif_on_v45/submission_q2_temporal_motif_knn_logitresid.csv |
| q2_temporal_motif_extra | 0.686614 | outputs/q2_temporal_motif_on_v45/oof_q2_temporal_motif_extra.csv | outputs/q2_temporal_motif_on_v45/submission_q2_temporal_motif_extra.csv |
| q2_temporal_motif_knn_label | 0.716159 | outputs/q2_temporal_motif_on_v45/oof_q2_temporal_motif_knn_label.csv | outputs/q2_temporal_motif_on_v45/submission_q2_temporal_motif_knn_label.csv |
| q2_temporal_motif_hgb | 0.717032 | outputs/q2_temporal_motif_on_v45/oof_q2_temporal_motif_hgb.csv | outputs/q2_temporal_motif_on_v45/submission_q2_temporal_motif_hgb.csv |
| q2_temporal_motif_proto | 0.753840 | outputs/q2_temporal_motif_on_v45/oof_q2_temporal_motif_proto.csv | outputs/q2_temporal_motif_on_v45/submission_q2_temporal_motif_proto.csv |
| q2_temporal_motif_logreg | 0.909723 | outputs/q2_temporal_motif_on_v45/oof_q2_temporal_motif_logreg.csv | outputs/q2_temporal_motif_on_v45/submission_q2_temporal_motif_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_motif | 315 |
