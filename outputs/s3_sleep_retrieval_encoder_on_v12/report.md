# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.494019`
- Best source S3 OOF: `0.531905`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_sleep_retrieval_meta | 0.531905 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_sleep_retrieval_meta.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_sleep_retrieval_meta.csv |
| s3_s2_broad_knn_resid | 0.534315 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_s2_broad_knn_resid.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_s2_broad_knn_resid.csv |
| s3_sleep_missing_knn_resid | 0.559144 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_sleep_missing_knn_resid.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_sleep_missing_knn_resid.csv |
| s3_night_events_hgb | 0.566561 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_night_events_hgb.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_night_events_hgb.csv |
| s3_connectivity_context_knn_resid | 0.578603 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_connectivity_context_knn_resid.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_connectivity_context_knn_resid.csv |
| s3_s2_broad_knn_label | 0.579012 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_s2_broad_knn_label.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_s2_broad_knn_label.csv |
| s3_connectivity_context_hgb | 0.579761 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_connectivity_context_hgb.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_connectivity_context_hgb.csv |
| s3_sleep_missing_hgb | 0.582778 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_sleep_missing_hgb.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_sleep_missing_hgb.csv |
| s3_connectivity_context_extra | 0.584118 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_connectivity_context_extra.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_connectivity_context_extra.csv |
| s3_s2_broad_hgb | 0.586191 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_s2_broad_hgb.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_s2_broad_hgb.csv |
| s3_s2_broad_extra | 0.588869 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_s2_broad_extra.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_s2_broad_extra.csv |
| s3_connectivity_context_proto | 0.600939 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_connectivity_context_proto.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_connectivity_context_proto.csv |
| s3_sleep_missing_knn_logitresid | 0.602304 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_sleep_missing_knn_logitresid.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_sleep_missing_knn_logitresid.csv |
| s3_sleep_missing_extra | 0.604680 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_sleep_missing_extra.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_sleep_missing_extra.csv |
| s3_s2_broad_knn_logitresid | 0.610319 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_s2_broad_knn_logitresid.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_s2_broad_knn_logitresid.csv |
| s3_s2_broad_proto | 0.611371 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_s2_broad_proto.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_s2_broad_proto.csv |
| s3_night_events_knn_resid | 0.618411 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_night_events_knn_resid.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_night_events_knn_resid.csv |
| s3_night_events_extra | 0.621488 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_night_events_extra.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_night_events_extra.csv |
| s3_sleep_missing_knn_label | 0.621868 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_sleep_missing_knn_label.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_sleep_missing_knn_label.csv |
| s3_connectivity_context_knn_logitresid | 0.622393 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_connectivity_context_knn_logitresid.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_connectivity_context_knn_logitresid.csv |
| s3_night_events_knn_logitresid | 0.635396 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_night_events_knn_logitresid.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_night_events_knn_logitresid.csv |
| s3_sleep_missing_proto | 0.653712 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_sleep_missing_proto.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_sleep_missing_proto.csv |
| s3_night_events_knn_label | 0.654850 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_night_events_knn_label.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_night_events_knn_label.csv |
| s3_night_events_proto | 0.660365 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_night_events_proto.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_night_events_proto.csv |
| s3_connectivity_context_knn_label | 0.678433 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_connectivity_context_knn_label.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_connectivity_context_knn_label.csv |
| s3_connectivity_context_logreg | 0.718393 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_connectivity_context_logreg.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_connectivity_context_logreg.csv |
| s3_s2_broad_logreg | 0.735398 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_s2_broad_logreg.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_s2_broad_logreg.csv |
| s3_night_events_logreg | 0.787293 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_night_events_logreg.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_night_events_logreg.csv |
| s3_sleep_missing_logreg | 0.804358 | outputs/s3_sleep_retrieval_encoder_on_v12/oof_s3_sleep_missing_logreg.csv | outputs/s3_sleep_retrieval_encoder_on_v12/submission_s3_sleep_missing_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| sleep_missing | 911 |
| connectivity_context | 1104 |
| night_events | 238 |
| s2_broad | 1598 |
