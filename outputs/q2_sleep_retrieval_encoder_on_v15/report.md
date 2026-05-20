# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.628549`
- Best source Q2 OOF: `0.631647`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_sleep_retrieval_meta | 0.631647 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_sleep_retrieval_meta.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_sleep_retrieval_meta.csv |
| q2_sleep_missing_knn_resid | 0.683748 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_sleep_missing_knn_resid.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_sleep_missing_knn_resid.csv |
| q2_night_events_knn_resid | 0.683924 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_night_events_knn_resid.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_night_events_knn_resid.csv |
| q2_sleep_missing_extra | 0.693584 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_sleep_missing_extra.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_sleep_missing_extra.csv |
| q2_night_events_extra | 0.696869 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_night_events_extra.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_night_events_extra.csv |
| q2_connectivity_context_extra | 0.699070 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_connectivity_context_extra.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_connectivity_context_extra.csv |
| q2_s2_broad_extra | 0.703597 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_s2_broad_extra.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_s2_broad_extra.csv |
| q2_connectivity_context_knn_resid | 0.710943 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_connectivity_context_knn_resid.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_connectivity_context_knn_resid.csv |
| q2_sleep_missing_knn_label | 0.717047 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_sleep_missing_knn_label.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_sleep_missing_knn_label.csv |
| q2_connectivity_context_hgb | 0.726650 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_connectivity_context_hgb.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_connectivity_context_hgb.csv |
| q2_night_events_hgb | 0.729310 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_night_events_hgb.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_night_events_hgb.csv |
| q2_night_events_knn_label | 0.733258 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_night_events_knn_label.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_night_events_knn_label.csv |
| q2_s2_broad_knn_resid | 0.737898 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_s2_broad_knn_resid.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_s2_broad_knn_resid.csv |
| q2_s2_broad_hgb | 0.741242 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_s2_broad_hgb.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_s2_broad_hgb.csv |
| q2_sleep_missing_hgb | 0.749843 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_sleep_missing_hgb.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_sleep_missing_hgb.csv |
| q2_connectivity_context_knn_label | 0.750520 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_connectivity_context_knn_label.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_connectivity_context_knn_label.csv |
| q2_s2_broad_knn_label | 0.750863 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_s2_broad_knn_label.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_s2_broad_knn_label.csv |
| q2_night_events_proto | 0.755347 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_night_events_proto.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_night_events_proto.csv |
| q2_connectivity_context_proto | 0.761840 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_connectivity_context_proto.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_connectivity_context_proto.csv |
| q2_sleep_missing_proto | 0.771949 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_sleep_missing_proto.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_sleep_missing_proto.csv |
| q2_s2_broad_proto | 0.782854 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_s2_broad_proto.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_s2_broad_proto.csv |
| q2_sleep_missing_knn_logitresid | 0.805478 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_sleep_missing_knn_logitresid.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_sleep_missing_knn_logitresid.csv |
| q2_night_events_knn_logitresid | 0.808081 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_night_events_knn_logitresid.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_night_events_knn_logitresid.csv |
| q2_night_events_logreg | 0.811839 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_night_events_logreg.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_night_events_logreg.csv |
| q2_s2_broad_logreg | 0.827890 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_s2_broad_logreg.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_s2_broad_logreg.csv |
| q2_sleep_missing_logreg | 0.828345 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_sleep_missing_logreg.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_sleep_missing_logreg.csv |
| q2_connectivity_context_logreg | 0.832840 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_connectivity_context_logreg.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_connectivity_context_logreg.csv |
| q2_connectivity_context_knn_logitresid | 0.866049 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_connectivity_context_knn_logitresid.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_connectivity_context_knn_logitresid.csv |
| q2_s2_broad_knn_logitresid | 0.876286 | outputs/q2_sleep_retrieval_encoder_on_v15/oof_q2_s2_broad_knn_logitresid.csv | outputs/q2_sleep_retrieval_encoder_on_v15/submission_q2_s2_broad_knn_logitresid.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| sleep_missing | 911 |
| connectivity_context | 1104 |
| night_events | 238 |
| s2_broad | 1598 |
