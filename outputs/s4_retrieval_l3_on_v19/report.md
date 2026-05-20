# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.565284`
- Best source S4 OOF: `0.590551`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_sleep_retrieval_meta | 0.590551 | outputs/s4_retrieval_l3_on_v19/oof_s4_sleep_retrieval_meta.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_sleep_retrieval_meta.csv |
| s4_sleep_missing_knn_resid | 0.624280 | outputs/s4_retrieval_l3_on_v19/oof_s4_sleep_missing_knn_resid.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_sleep_missing_knn_resid.csv |
| s4_night_events_knn_resid | 0.630414 | outputs/s4_retrieval_l3_on_v19/oof_s4_night_events_knn_resid.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_night_events_knn_resid.csv |
| s4_s2_broad_hgb | 0.637505 | outputs/s4_retrieval_l3_on_v19/oof_s4_s2_broad_hgb.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_s2_broad_hgb.csv |
| s4_s2_broad_knn_resid | 0.641323 | outputs/s4_retrieval_l3_on_v19/oof_s4_s2_broad_knn_resid.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_s2_broad_knn_resid.csv |
| s4_connectivity_context_knn_resid | 0.649926 | outputs/s4_retrieval_l3_on_v19/oof_s4_connectivity_context_knn_resid.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_connectivity_context_knn_resid.csv |
| s4_connectivity_context_hgb | 0.657823 | outputs/s4_retrieval_l3_on_v19/oof_s4_connectivity_context_hgb.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_connectivity_context_hgb.csv |
| s4_s2_broad_knn_label | 0.663093 | outputs/s4_retrieval_l3_on_v19/oof_s4_s2_broad_knn_label.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_s2_broad_knn_label.csv |
| s4_s2_broad_extra | 0.664192 | outputs/s4_retrieval_l3_on_v19/oof_s4_s2_broad_extra.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_s2_broad_extra.csv |
| s4_sleep_missing_hgb | 0.665868 | outputs/s4_retrieval_l3_on_v19/oof_s4_sleep_missing_hgb.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_sleep_missing_hgb.csv |
| s4_connectivity_context_extra | 0.666720 | outputs/s4_retrieval_l3_on_v19/oof_s4_connectivity_context_extra.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_connectivity_context_extra.csv |
| s4_sleep_missing_extra | 0.675227 | outputs/s4_retrieval_l3_on_v19/oof_s4_sleep_missing_extra.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_sleep_missing_extra.csv |
| s4_night_events_knn_label | 0.676473 | outputs/s4_retrieval_l3_on_v19/oof_s4_night_events_knn_label.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_night_events_knn_label.csv |
| s4_connectivity_context_knn_label | 0.676540 | outputs/s4_retrieval_l3_on_v19/oof_s4_connectivity_context_knn_label.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_connectivity_context_knn_label.csv |
| s4_sleep_missing_knn_label | 0.676736 | outputs/s4_retrieval_l3_on_v19/oof_s4_sleep_missing_knn_label.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_sleep_missing_knn_label.csv |
| s4_night_events_extra | 0.678434 | outputs/s4_retrieval_l3_on_v19/oof_s4_night_events_extra.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_night_events_extra.csv |
| s4_night_events_knn_logitresid | 0.678891 | outputs/s4_retrieval_l3_on_v19/oof_s4_night_events_knn_logitresid.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_night_events_knn_logitresid.csv |
| s4_s2_broad_proto | 0.681545 | outputs/s4_retrieval_l3_on_v19/oof_s4_s2_broad_proto.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_s2_broad_proto.csv |
| s4_night_events_hgb | 0.683739 | outputs/s4_retrieval_l3_on_v19/oof_s4_night_events_hgb.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_night_events_hgb.csv |
| s4_sleep_missing_knn_logitresid | 0.685255 | outputs/s4_retrieval_l3_on_v19/oof_s4_sleep_missing_knn_logitresid.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_sleep_missing_knn_logitresid.csv |
| s4_sleep_missing_proto | 0.686705 | outputs/s4_retrieval_l3_on_v19/oof_s4_sleep_missing_proto.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_sleep_missing_proto.csv |
| s4_connectivity_context_proto | 0.691228 | outputs/s4_retrieval_l3_on_v19/oof_s4_connectivity_context_proto.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_connectivity_context_proto.csv |
| s4_s2_broad_knn_logitresid | 0.691495 | outputs/s4_retrieval_l3_on_v19/oof_s4_s2_broad_knn_logitresid.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_s2_broad_knn_logitresid.csv |
| s4_night_events_proto | 0.692748 | outputs/s4_retrieval_l3_on_v19/oof_s4_night_events_proto.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_night_events_proto.csv |
| s4_connectivity_context_knn_logitresid | 0.712289 | outputs/s4_retrieval_l3_on_v19/oof_s4_connectivity_context_knn_logitresid.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_connectivity_context_knn_logitresid.csv |
| s4_connectivity_context_logreg | 0.735042 | outputs/s4_retrieval_l3_on_v19/oof_s4_connectivity_context_logreg.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_connectivity_context_logreg.csv |
| s4_s2_broad_logreg | 0.759390 | outputs/s4_retrieval_l3_on_v19/oof_s4_s2_broad_logreg.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_s2_broad_logreg.csv |
| s4_night_events_logreg | 0.800307 | outputs/s4_retrieval_l3_on_v19/oof_s4_night_events_logreg.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_night_events_logreg.csv |
| s4_sleep_missing_logreg | 0.802686 | outputs/s4_retrieval_l3_on_v19/oof_s4_sleep_missing_logreg.csv | outputs/s4_retrieval_l3_on_v19/submission_s4_sleep_missing_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| sleep_missing | 911 |
| connectivity_context | 1104 |
| night_events | 238 |
| s2_broad | 1598 |
