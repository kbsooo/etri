# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.534280`
- Best source S1 OOF: `0.571458`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_s2_broad_hgb | 0.571458 | outputs/s1_retrieval_l2_on_v18/oof_s1_s2_broad_hgb.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_s2_broad_hgb.csv |
| s1_s2_broad_proto | 0.572298 | outputs/s1_retrieval_l2_on_v18/oof_s1_s2_broad_proto.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_s2_broad_proto.csv |
| s1_sleep_missing_hgb | 0.583702 | outputs/s1_retrieval_l2_on_v18/oof_s1_sleep_missing_hgb.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_sleep_missing_hgb.csv |
| s1_connectivity_context_hgb | 0.588843 | outputs/s1_retrieval_l2_on_v18/oof_s1_connectivity_context_hgb.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_connectivity_context_hgb.csv |
| s1_sleep_missing_proto | 0.591338 | outputs/s1_retrieval_l2_on_v18/oof_s1_sleep_missing_proto.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_sleep_missing_proto.csv |
| s1_connectivity_context_proto | 0.606440 | outputs/s1_retrieval_l2_on_v18/oof_s1_connectivity_context_proto.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_connectivity_context_proto.csv |
| s1_night_events_hgb | 0.609656 | outputs/s1_retrieval_l2_on_v18/oof_s1_night_events_hgb.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_night_events_hgb.csv |
| s1_connectivity_context_knn_label | 0.614801 | outputs/s1_retrieval_l2_on_v18/oof_s1_connectivity_context_knn_label.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_connectivity_context_knn_label.csv |
| s1_sleep_missing_extra | 0.618776 | outputs/s1_retrieval_l2_on_v18/oof_s1_sleep_missing_extra.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_sleep_missing_extra.csv |
| s1_s2_broad_extra | 0.621403 | outputs/s1_retrieval_l2_on_v18/oof_s1_s2_broad_extra.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_s2_broad_extra.csv |
| s1_connectivity_context_extra | 0.626215 | outputs/s1_retrieval_l2_on_v18/oof_s1_connectivity_context_extra.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_connectivity_context_extra.csv |
| s1_night_events_proto | 0.628375 | outputs/s1_retrieval_l2_on_v18/oof_s1_night_events_proto.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_night_events_proto.csv |
| s1_night_events_extra | 0.629768 | outputs/s1_retrieval_l2_on_v18/oof_s1_night_events_extra.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_night_events_extra.csv |
| s1_sleep_missing_knn_resid | 0.631280 | outputs/s1_retrieval_l2_on_v18/oof_s1_sleep_missing_knn_resid.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_sleep_missing_knn_resid.csv |
| s1_night_events_knn_resid | 0.633346 | outputs/s1_retrieval_l2_on_v18/oof_s1_night_events_knn_resid.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_night_events_knn_resid.csv |
| s1_s2_broad_knn_label | 0.644157 | outputs/s1_retrieval_l2_on_v18/oof_s1_s2_broad_knn_label.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_s2_broad_knn_label.csv |
| s1_sleep_missing_knn_label | 0.646921 | outputs/s1_retrieval_l2_on_v18/oof_s1_sleep_missing_knn_label.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_sleep_missing_knn_label.csv |
| s1_s2_broad_logreg | 0.659767 | outputs/s1_retrieval_l2_on_v18/oof_s1_s2_broad_logreg.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_s2_broad_logreg.csv |
| s1_s2_broad_knn_resid | 0.661972 | outputs/s1_retrieval_l2_on_v18/oof_s1_s2_broad_knn_resid.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_s2_broad_knn_resid.csv |
| s1_sleep_retrieval_meta | 0.663669 | outputs/s1_retrieval_l2_on_v18/oof_s1_sleep_retrieval_meta.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_sleep_retrieval_meta.csv |
| s1_sleep_missing_knn_logitresid | 0.684427 | outputs/s1_retrieval_l2_on_v18/oof_s1_sleep_missing_knn_logitresid.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_sleep_missing_knn_logitresid.csv |
| s1_night_events_knn_label | 0.685454 | outputs/s1_retrieval_l2_on_v18/oof_s1_night_events_knn_label.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_night_events_knn_label.csv |
| s1_night_events_knn_logitresid | 0.688346 | outputs/s1_retrieval_l2_on_v18/oof_s1_night_events_knn_logitresid.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_night_events_knn_logitresid.csv |
| s1_connectivity_context_knn_resid | 0.690165 | outputs/s1_retrieval_l2_on_v18/oof_s1_connectivity_context_knn_resid.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_connectivity_context_knn_resid.csv |
| s1_s2_broad_knn_logitresid | 0.703997 | outputs/s1_retrieval_l2_on_v18/oof_s1_s2_broad_knn_logitresid.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_s2_broad_knn_logitresid.csv |
| s1_connectivity_context_logreg | 0.711194 | outputs/s1_retrieval_l2_on_v18/oof_s1_connectivity_context_logreg.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_connectivity_context_logreg.csv |
| s1_sleep_missing_logreg | 0.719285 | outputs/s1_retrieval_l2_on_v18/oof_s1_sleep_missing_logreg.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_sleep_missing_logreg.csv |
| s1_connectivity_context_knn_logitresid | 0.733116 | outputs/s1_retrieval_l2_on_v18/oof_s1_connectivity_context_knn_logitresid.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_connectivity_context_knn_logitresid.csv |
| s1_night_events_logreg | 0.803124 | outputs/s1_retrieval_l2_on_v18/oof_s1_night_events_logreg.csv | outputs/s1_retrieval_l2_on_v18/submission_s1_night_events_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| sleep_missing | 911 |
| connectivity_context | 1104 |
| night_events | 238 |
| s2_broad | 1598 |
