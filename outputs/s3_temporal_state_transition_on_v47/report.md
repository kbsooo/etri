# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.437181`
- Best source S3 OOF: `0.450615`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_temporal_state_transition_knn_resid | 0.450615 | outputs/s3_temporal_state_transition_on_v47/oof_s3_temporal_state_transition_knn_resid.csv | outputs/s3_temporal_state_transition_on_v47/submission_s3_temporal_state_transition_knn_resid.csv |
| s3_temporal_state_transition_knn_logitresid | 0.487211 | outputs/s3_temporal_state_transition_on_v47/oof_s3_temporal_state_transition_knn_logitresid.csv | outputs/s3_temporal_state_transition_on_v47/submission_s3_temporal_state_transition_knn_logitresid.csv |
| s3_sleep_retrieval_meta | 0.488715 | outputs/s3_temporal_state_transition_on_v47/oof_s3_sleep_retrieval_meta.csv | outputs/s3_temporal_state_transition_on_v47/submission_s3_sleep_retrieval_meta.csv |
| s3_temporal_state_transition_hgb | 0.599399 | outputs/s3_temporal_state_transition_on_v47/oof_s3_temporal_state_transition_hgb.csv | outputs/s3_temporal_state_transition_on_v47/submission_s3_temporal_state_transition_hgb.csv |
| s3_temporal_state_transition_knn_label | 0.674203 | outputs/s3_temporal_state_transition_on_v47/oof_s3_temporal_state_transition_knn_label.csv | outputs/s3_temporal_state_transition_on_v47/submission_s3_temporal_state_transition_knn_label.csv |
| s3_temporal_state_transition_extra | 0.684393 | outputs/s3_temporal_state_transition_on_v47/oof_s3_temporal_state_transition_extra.csv | outputs/s3_temporal_state_transition_on_v47/submission_s3_temporal_state_transition_extra.csv |
| s3_temporal_state_transition_proto | 0.750153 | outputs/s3_temporal_state_transition_on_v47/oof_s3_temporal_state_transition_proto.csv | outputs/s3_temporal_state_transition_on_v47/submission_s3_temporal_state_transition_proto.csv |
| s3_temporal_state_transition_logreg | 0.904894 | outputs/s3_temporal_state_transition_on_v47/oof_s3_temporal_state_transition_logreg.csv | outputs/s3_temporal_state_transition_on_v47/submission_s3_temporal_state_transition_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_transition | 35 |
