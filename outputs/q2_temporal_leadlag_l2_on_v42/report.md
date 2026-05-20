# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.570440`
- Best source Q2 OOF: `0.594127`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_sleep_retrieval_meta | 0.594127 | outputs/q2_temporal_leadlag_l2_on_v42/oof_q2_sleep_retrieval_meta.csv | outputs/q2_temporal_leadlag_l2_on_v42/submission_q2_sleep_retrieval_meta.csv |
| q2_temporal_leadlag_knn_resid | 0.667434 | outputs/q2_temporal_leadlag_l2_on_v42/oof_q2_temporal_leadlag_knn_resid.csv | outputs/q2_temporal_leadlag_l2_on_v42/submission_q2_temporal_leadlag_knn_resid.csv |
| q2_temporal_leadlag_extra | 0.686224 | outputs/q2_temporal_leadlag_l2_on_v42/oof_q2_temporal_leadlag_extra.csv | outputs/q2_temporal_leadlag_l2_on_v42/submission_q2_temporal_leadlag_extra.csv |
| q2_temporal_leadlag_hgb | 0.729686 | outputs/q2_temporal_leadlag_l2_on_v42/oof_q2_temporal_leadlag_hgb.csv | outputs/q2_temporal_leadlag_l2_on_v42/submission_q2_temporal_leadlag_hgb.csv |
| q2_temporal_leadlag_knn_label | 0.735547 | outputs/q2_temporal_leadlag_l2_on_v42/oof_q2_temporal_leadlag_knn_label.csv | outputs/q2_temporal_leadlag_l2_on_v42/submission_q2_temporal_leadlag_knn_label.csv |
| q2_temporal_leadlag_knn_logitresid | 0.746196 | outputs/q2_temporal_leadlag_l2_on_v42/oof_q2_temporal_leadlag_knn_logitresid.csv | outputs/q2_temporal_leadlag_l2_on_v42/submission_q2_temporal_leadlag_knn_logitresid.csv |
| q2_temporal_leadlag_proto | 0.802571 | outputs/q2_temporal_leadlag_l2_on_v42/oof_q2_temporal_leadlag_proto.csv | outputs/q2_temporal_leadlag_l2_on_v42/submission_q2_temporal_leadlag_proto.csv |
| q2_temporal_leadlag_logreg | 1.015245 | outputs/q2_temporal_leadlag_l2_on_v42/oof_q2_temporal_leadlag_logreg.csv | outputs/q2_temporal_leadlag_l2_on_v42/submission_q2_temporal_leadlag_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_leadlag | 144 |
