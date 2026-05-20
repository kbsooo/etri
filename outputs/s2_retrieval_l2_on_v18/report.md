# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.512639`
- Best source S2 OOF: `0.561057`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_sleep_missing_knn_resid | 0.561057 | outputs/s2_retrieval_l2_on_v18/oof_s2_sleep_missing_knn_resid.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_sleep_missing_knn_resid.csv |
| s2_sleep_retrieval_meta | 0.577320 | outputs/s2_retrieval_l2_on_v18/oof_s2_sleep_retrieval_meta.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_sleep_retrieval_meta.csv |
| s2_night_events_knn_resid | 0.598684 | outputs/s2_retrieval_l2_on_v18/oof_s2_night_events_knn_resid.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_night_events_knn_resid.csv |
| s2_s2_broad_knn_resid | 0.601605 | outputs/s2_retrieval_l2_on_v18/oof_s2_s2_broad_knn_resid.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_s2_broad_knn_resid.csv |
| s2_connectivity_context_knn_resid | 0.606737 | outputs/s2_retrieval_l2_on_v18/oof_s2_connectivity_context_knn_resid.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_connectivity_context_knn_resid.csv |
| s2_connectivity_context_extra | 0.615788 | outputs/s2_retrieval_l2_on_v18/oof_s2_connectivity_context_extra.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_connectivity_context_extra.csv |
| s2_night_events_knn_logitresid | 0.617244 | outputs/s2_retrieval_l2_on_v18/oof_s2_night_events_knn_logitresid.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_night_events_knn_logitresid.csv |
| s2_s2_broad_extra | 0.619619 | outputs/s2_retrieval_l2_on_v18/oof_s2_s2_broad_extra.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_s2_broad_extra.csv |
| s2_night_events_hgb | 0.621226 | outputs/s2_retrieval_l2_on_v18/oof_s2_night_events_hgb.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_night_events_hgb.csv |
| s2_connectivity_context_proto | 0.624711 | outputs/s2_retrieval_l2_on_v18/oof_s2_connectivity_context_proto.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_connectivity_context_proto.csv |
| s2_s2_broad_proto | 0.625108 | outputs/s2_retrieval_l2_on_v18/oof_s2_s2_broad_proto.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_s2_broad_proto.csv |
| s2_connectivity_context_hgb | 0.630607 | outputs/s2_retrieval_l2_on_v18/oof_s2_connectivity_context_hgb.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_connectivity_context_hgb.csv |
| s2_s2_broad_hgb | 0.632536 | outputs/s2_retrieval_l2_on_v18/oof_s2_s2_broad_hgb.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_s2_broad_hgb.csv |
| s2_sleep_missing_hgb | 0.632594 | outputs/s2_retrieval_l2_on_v18/oof_s2_sleep_missing_hgb.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_sleep_missing_hgb.csv |
| s2_sleep_missing_extra | 0.634065 | outputs/s2_retrieval_l2_on_v18/oof_s2_sleep_missing_extra.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_sleep_missing_extra.csv |
| s2_connectivity_context_knn_label | 0.634102 | outputs/s2_retrieval_l2_on_v18/oof_s2_connectivity_context_knn_label.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_connectivity_context_knn_label.csv |
| s2_s2_broad_knn_label | 0.641861 | outputs/s2_retrieval_l2_on_v18/oof_s2_s2_broad_knn_label.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_s2_broad_knn_label.csv |
| s2_night_events_extra | 0.649108 | outputs/s2_retrieval_l2_on_v18/oof_s2_night_events_extra.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_night_events_extra.csv |
| s2_night_events_knn_label | 0.662249 | outputs/s2_retrieval_l2_on_v18/oof_s2_night_events_knn_label.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_night_events_knn_label.csv |
| s2_sleep_missing_proto | 0.664874 | outputs/s2_retrieval_l2_on_v18/oof_s2_sleep_missing_proto.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_sleep_missing_proto.csv |
| s2_sleep_missing_knn_logitresid | 0.664958 | outputs/s2_retrieval_l2_on_v18/oof_s2_sleep_missing_knn_logitresid.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_sleep_missing_knn_logitresid.csv |
| s2_connectivity_context_knn_logitresid | 0.673000 | outputs/s2_retrieval_l2_on_v18/oof_s2_connectivity_context_knn_logitresid.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_connectivity_context_knn_logitresid.csv |
| s2_s2_broad_knn_logitresid | 0.678682 | outputs/s2_retrieval_l2_on_v18/oof_s2_s2_broad_knn_logitresid.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_s2_broad_knn_logitresid.csv |
| s2_night_events_proto | 0.683930 | outputs/s2_retrieval_l2_on_v18/oof_s2_night_events_proto.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_night_events_proto.csv |
| s2_sleep_missing_knn_label | 0.686897 | outputs/s2_retrieval_l2_on_v18/oof_s2_sleep_missing_knn_label.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_sleep_missing_knn_label.csv |
| s2_s2_broad_logreg | 0.743572 | outputs/s2_retrieval_l2_on_v18/oof_s2_s2_broad_logreg.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_s2_broad_logreg.csv |
| s2_sleep_missing_logreg | 0.749880 | outputs/s2_retrieval_l2_on_v18/oof_s2_sleep_missing_logreg.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_sleep_missing_logreg.csv |
| s2_night_events_logreg | 0.754936 | outputs/s2_retrieval_l2_on_v18/oof_s2_night_events_logreg.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_night_events_logreg.csv |
| s2_connectivity_context_logreg | 0.773047 | outputs/s2_retrieval_l2_on_v18/oof_s2_connectivity_context_logreg.csv | outputs/s2_retrieval_l2_on_v18/submission_s2_connectivity_context_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| sleep_missing | 911 |
| connectivity_context | 1104 |
| night_events | 238 |
| s2_broad | 1598 |
