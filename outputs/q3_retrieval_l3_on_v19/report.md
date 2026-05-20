# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.597617`
- Best source Q3 OOF: `0.660637`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_sleep_retrieval_meta | 0.660637 | outputs/q3_retrieval_l3_on_v19/oof_q3_sleep_retrieval_meta.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_sleep_retrieval_meta.csv |
| q3_connectivity_context_extra | 0.675360 | outputs/q3_retrieval_l3_on_v19/oof_q3_connectivity_context_extra.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_connectivity_context_extra.csv |
| q3_s2_broad_extra | 0.675784 | outputs/q3_retrieval_l3_on_v19/oof_q3_s2_broad_extra.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_s2_broad_extra.csv |
| q3_connectivity_context_knn_resid | 0.676636 | outputs/q3_retrieval_l3_on_v19/oof_q3_connectivity_context_knn_resid.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_connectivity_context_knn_resid.csv |
| q3_night_events_extra | 0.676799 | outputs/q3_retrieval_l3_on_v19/oof_q3_night_events_extra.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_night_events_extra.csv |
| q3_sleep_missing_extra | 0.677468 | outputs/q3_retrieval_l3_on_v19/oof_q3_sleep_missing_extra.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_sleep_missing_extra.csv |
| q3_sleep_missing_knn_resid | 0.679498 | outputs/q3_retrieval_l3_on_v19/oof_q3_sleep_missing_knn_resid.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_sleep_missing_knn_resid.csv |
| q3_s2_broad_hgb | 0.695415 | outputs/q3_retrieval_l3_on_v19/oof_q3_s2_broad_hgb.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_s2_broad_hgb.csv |
| q3_sleep_missing_hgb | 0.697007 | outputs/q3_retrieval_l3_on_v19/oof_q3_sleep_missing_hgb.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_sleep_missing_hgb.csv |
| q3_sleep_missing_proto | 0.697662 | outputs/q3_retrieval_l3_on_v19/oof_q3_sleep_missing_proto.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_sleep_missing_proto.csv |
| q3_night_events_knn_resid | 0.700744 | outputs/q3_retrieval_l3_on_v19/oof_q3_night_events_knn_resid.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_night_events_knn_resid.csv |
| q3_connectivity_context_knn_label | 0.702418 | outputs/q3_retrieval_l3_on_v19/oof_q3_connectivity_context_knn_label.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_connectivity_context_knn_label.csv |
| q3_sleep_missing_knn_label | 0.705279 | outputs/q3_retrieval_l3_on_v19/oof_q3_sleep_missing_knn_label.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_sleep_missing_knn_label.csv |
| q3_night_events_hgb | 0.705778 | outputs/q3_retrieval_l3_on_v19/oof_q3_night_events_hgb.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_night_events_hgb.csv |
| q3_night_events_knn_label | 0.706483 | outputs/q3_retrieval_l3_on_v19/oof_q3_night_events_knn_label.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_night_events_knn_label.csv |
| q3_connectivity_context_hgb | 0.714665 | outputs/q3_retrieval_l3_on_v19/oof_q3_connectivity_context_hgb.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_connectivity_context_hgb.csv |
| q3_s2_broad_proto | 0.720935 | outputs/q3_retrieval_l3_on_v19/oof_q3_s2_broad_proto.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_s2_broad_proto.csv |
| q3_connectivity_context_proto | 0.722799 | outputs/q3_retrieval_l3_on_v19/oof_q3_connectivity_context_proto.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_connectivity_context_proto.csv |
| q3_s2_broad_knn_label | 0.731574 | outputs/q3_retrieval_l3_on_v19/oof_q3_s2_broad_knn_label.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_s2_broad_knn_label.csv |
| q3_s2_broad_knn_resid | 0.735168 | outputs/q3_retrieval_l3_on_v19/oof_q3_s2_broad_knn_resid.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_s2_broad_knn_resid.csv |
| q3_connectivity_context_knn_logitresid | 0.754414 | outputs/q3_retrieval_l3_on_v19/oof_q3_connectivity_context_knn_logitresid.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_connectivity_context_knn_logitresid.csv |
| q3_night_events_proto | 0.759372 | outputs/q3_retrieval_l3_on_v19/oof_q3_night_events_proto.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_night_events_proto.csv |
| q3_night_events_knn_logitresid | 0.774041 | outputs/q3_retrieval_l3_on_v19/oof_q3_night_events_knn_logitresid.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_night_events_knn_logitresid.csv |
| q3_s2_broad_knn_logitresid | 0.779935 | outputs/q3_retrieval_l3_on_v19/oof_q3_s2_broad_knn_logitresid.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_s2_broad_knn_logitresid.csv |
| q3_sleep_missing_knn_logitresid | 0.794711 | outputs/q3_retrieval_l3_on_v19/oof_q3_sleep_missing_knn_logitresid.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_sleep_missing_knn_logitresid.csv |
| q3_s2_broad_logreg | 0.802217 | outputs/q3_retrieval_l3_on_v19/oof_q3_s2_broad_logreg.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_s2_broad_logreg.csv |
| q3_sleep_missing_logreg | 0.821756 | outputs/q3_retrieval_l3_on_v19/oof_q3_sleep_missing_logreg.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_sleep_missing_logreg.csv |
| q3_connectivity_context_logreg | 0.834332 | outputs/q3_retrieval_l3_on_v19/oof_q3_connectivity_context_logreg.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_connectivity_context_logreg.csv |
| q3_night_events_logreg | 0.864590 | outputs/q3_retrieval_l3_on_v19/oof_q3_night_events_logreg.csv | outputs/q3_retrieval_l3_on_v19/submission_q3_night_events_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| sleep_missing | 911 |
| connectivity_context | 1104 |
| night_events | 238 |
| s2_broad | 1598 |
