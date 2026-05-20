# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.552061`
- Best source Q1 OOF: `0.574924`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.574924 | outputs/q1_temporal_state_transition_on_v47/oof_q1_sleep_retrieval_meta.csv | outputs/q1_temporal_state_transition_on_v47/submission_q1_sleep_retrieval_meta.csv |
| q1_temporal_state_transition_knn_resid | 0.581456 | outputs/q1_temporal_state_transition_on_v47/oof_q1_temporal_state_transition_knn_resid.csv | outputs/q1_temporal_state_transition_on_v47/submission_q1_temporal_state_transition_knn_resid.csv |
| q1_temporal_state_transition_knn_logitresid | 0.659922 | outputs/q1_temporal_state_transition_on_v47/oof_q1_temporal_state_transition_knn_logitresid.csv | outputs/q1_temporal_state_transition_on_v47/submission_q1_temporal_state_transition_knn_logitresid.csv |
| q1_temporal_state_transition_extra | 0.693417 | outputs/q1_temporal_state_transition_on_v47/oof_q1_temporal_state_transition_extra.csv | outputs/q1_temporal_state_transition_on_v47/submission_q1_temporal_state_transition_extra.csv |
| q1_temporal_state_transition_knn_label | 0.697169 | outputs/q1_temporal_state_transition_on_v47/oof_q1_temporal_state_transition_knn_label.csv | outputs/q1_temporal_state_transition_on_v47/submission_q1_temporal_state_transition_knn_label.csv |
| q1_temporal_state_transition_hgb | 0.711977 | outputs/q1_temporal_state_transition_on_v47/oof_q1_temporal_state_transition_hgb.csv | outputs/q1_temporal_state_transition_on_v47/submission_q1_temporal_state_transition_hgb.csv |
| q1_temporal_state_transition_proto | 0.769903 | outputs/q1_temporal_state_transition_on_v47/oof_q1_temporal_state_transition_proto.csv | outputs/q1_temporal_state_transition_on_v47/submission_q1_temporal_state_transition_proto.csv |
| q1_temporal_state_transition_logreg | 0.944887 | outputs/q1_temporal_state_transition_on_v47/oof_q1_temporal_state_transition_logreg.csv | outputs/q1_temporal_state_transition_on_v47/submission_q1_temporal_state_transition_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_transition | 35 |
