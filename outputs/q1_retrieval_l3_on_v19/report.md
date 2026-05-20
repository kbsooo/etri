# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.607223`
- Best source Q1 OOF: `0.646082`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.646082 | outputs/q1_retrieval_l3_on_v19/oof_q1_sleep_retrieval_meta.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_sleep_retrieval_meta.csv |
| q1_sleep_missing_knn_resid | 0.663362 | outputs/q1_retrieval_l3_on_v19/oof_q1_sleep_missing_knn_resid.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_sleep_missing_knn_resid.csv |
| q1_s2_broad_extra | 0.668341 | outputs/q1_retrieval_l3_on_v19/oof_q1_s2_broad_extra.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_s2_broad_extra.csv |
| q1_connectivity_context_knn_label | 0.670055 | outputs/q1_retrieval_l3_on_v19/oof_q1_connectivity_context_knn_label.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_connectivity_context_knn_label.csv |
| q1_connectivity_context_extra | 0.670597 | outputs/q1_retrieval_l3_on_v19/oof_q1_connectivity_context_extra.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_connectivity_context_extra.csv |
| q1_night_events_extra | 0.673402 | outputs/q1_retrieval_l3_on_v19/oof_q1_night_events_extra.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_night_events_extra.csv |
| q1_sleep_missing_extra | 0.674368 | outputs/q1_retrieval_l3_on_v19/oof_q1_sleep_missing_extra.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_sleep_missing_extra.csv |
| q1_connectivity_context_proto | 0.679719 | outputs/q1_retrieval_l3_on_v19/oof_q1_connectivity_context_proto.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_connectivity_context_proto.csv |
| q1_connectivity_context_knn_resid | 0.681119 | outputs/q1_retrieval_l3_on_v19/oof_q1_connectivity_context_knn_resid.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_connectivity_context_knn_resid.csv |
| q1_night_events_knn_resid | 0.683819 | outputs/q1_retrieval_l3_on_v19/oof_q1_night_events_knn_resid.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_night_events_knn_resid.csv |
| q1_connectivity_context_hgb | 0.684648 | outputs/q1_retrieval_l3_on_v19/oof_q1_connectivity_context_hgb.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_connectivity_context_hgb.csv |
| q1_s2_broad_knn_label | 0.686261 | outputs/q1_retrieval_l3_on_v19/oof_q1_s2_broad_knn_label.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_s2_broad_knn_label.csv |
| q1_s2_broad_knn_resid | 0.692478 | outputs/q1_retrieval_l3_on_v19/oof_q1_s2_broad_knn_resid.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_s2_broad_knn_resid.csv |
| q1_s2_broad_proto | 0.696819 | outputs/q1_retrieval_l3_on_v19/oof_q1_s2_broad_proto.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_s2_broad_proto.csv |
| q1_s2_broad_hgb | 0.699156 | outputs/q1_retrieval_l3_on_v19/oof_q1_s2_broad_hgb.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_s2_broad_hgb.csv |
| q1_sleep_missing_knn_label | 0.703338 | outputs/q1_retrieval_l3_on_v19/oof_q1_sleep_missing_knn_label.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_sleep_missing_knn_label.csv |
| q1_night_events_hgb | 0.703807 | outputs/q1_retrieval_l3_on_v19/oof_q1_night_events_hgb.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_night_events_hgb.csv |
| q1_night_events_knn_label | 0.704337 | outputs/q1_retrieval_l3_on_v19/oof_q1_night_events_knn_label.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_night_events_knn_label.csv |
| q1_connectivity_context_logreg | 0.708245 | outputs/q1_retrieval_l3_on_v19/oof_q1_connectivity_context_logreg.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_connectivity_context_logreg.csv |
| q1_s2_broad_logreg | 0.723542 | outputs/q1_retrieval_l3_on_v19/oof_q1_s2_broad_logreg.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_s2_broad_logreg.csv |
| q1_sleep_missing_hgb | 0.733596 | outputs/q1_retrieval_l3_on_v19/oof_q1_sleep_missing_hgb.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_sleep_missing_hgb.csv |
| q1_sleep_missing_proto | 0.735900 | outputs/q1_retrieval_l3_on_v19/oof_q1_sleep_missing_proto.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_sleep_missing_proto.csv |
| q1_night_events_knn_logitresid | 0.736041 | outputs/q1_retrieval_l3_on_v19/oof_q1_night_events_knn_logitresid.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_night_events_knn_logitresid.csv |
| q1_connectivity_context_knn_logitresid | 0.763062 | outputs/q1_retrieval_l3_on_v19/oof_q1_connectivity_context_knn_logitresid.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_connectivity_context_knn_logitresid.csv |
| q1_sleep_missing_knn_logitresid | 0.770386 | outputs/q1_retrieval_l3_on_v19/oof_q1_sleep_missing_knn_logitresid.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_sleep_missing_knn_logitresid.csv |
| q1_s2_broad_knn_logitresid | 0.788066 | outputs/q1_retrieval_l3_on_v19/oof_q1_s2_broad_knn_logitresid.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_s2_broad_knn_logitresid.csv |
| q1_night_events_proto | 0.803350 | outputs/q1_retrieval_l3_on_v19/oof_q1_night_events_proto.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_night_events_proto.csv |
| q1_sleep_missing_logreg | 0.873784 | outputs/q1_retrieval_l3_on_v19/oof_q1_sleep_missing_logreg.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_sleep_missing_logreg.csv |
| q1_night_events_logreg | 0.880985 | outputs/q1_retrieval_l3_on_v19/oof_q1_night_events_logreg.csv | outputs/q1_retrieval_l3_on_v19/submission_q1_night_events_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| sleep_missing | 911 |
| connectivity_context | 1104 |
| night_events | 238 |
| s2_broad | 1598 |
