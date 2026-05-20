# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.499009`
- Best source S1 OOF: `0.562340`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_sleep_retrieval_meta | 0.562340 | outputs/s1_temporal_state_transition_on_v47/oof_s1_sleep_retrieval_meta.csv | outputs/s1_temporal_state_transition_on_v47/submission_s1_sleep_retrieval_meta.csv |
| s1_temporal_state_transition_knn_resid | 0.563709 | outputs/s1_temporal_state_transition_on_v47/oof_s1_temporal_state_transition_knn_resid.csv | outputs/s1_temporal_state_transition_on_v47/submission_s1_temporal_state_transition_knn_resid.csv |
| s1_temporal_state_transition_hgb | 0.631181 | outputs/s1_temporal_state_transition_on_v47/oof_s1_temporal_state_transition_hgb.csv | outputs/s1_temporal_state_transition_on_v47/submission_s1_temporal_state_transition_hgb.csv |
| s1_temporal_state_transition_knn_logitresid | 0.637659 | outputs/s1_temporal_state_transition_on_v47/oof_s1_temporal_state_transition_knn_logitresid.csv | outputs/s1_temporal_state_transition_on_v47/submission_s1_temporal_state_transition_knn_logitresid.csv |
| s1_temporal_state_transition_extra | 0.679294 | outputs/s1_temporal_state_transition_on_v47/oof_s1_temporal_state_transition_extra.csv | outputs/s1_temporal_state_transition_on_v47/submission_s1_temporal_state_transition_extra.csv |
| s1_temporal_state_transition_knn_label | 0.683137 | outputs/s1_temporal_state_transition_on_v47/oof_s1_temporal_state_transition_knn_label.csv | outputs/s1_temporal_state_transition_on_v47/submission_s1_temporal_state_transition_knn_label.csv |
| s1_temporal_state_transition_proto | 0.715866 | outputs/s1_temporal_state_transition_on_v47/oof_s1_temporal_state_transition_proto.csv | outputs/s1_temporal_state_transition_on_v47/submission_s1_temporal_state_transition_proto.csv |
| s1_temporal_state_transition_logreg | 0.872877 | outputs/s1_temporal_state_transition_on_v47/oof_s1_temporal_state_transition_logreg.csv | outputs/s1_temporal_state_transition_on_v47/submission_s1_temporal_state_transition_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_transition | 35 |
