# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.481224`
- Best source S2 OOF: `0.510208`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_temporal_state_transition_knn_resid | 0.510208 | outputs/s2_temporal_state_transition_on_v47/oof_s2_temporal_state_transition_knn_resid.csv | outputs/s2_temporal_state_transition_on_v47/submission_s2_temporal_state_transition_knn_resid.csv |
| s2_sleep_retrieval_meta | 0.534603 | outputs/s2_temporal_state_transition_on_v47/oof_s2_sleep_retrieval_meta.csv | outputs/s2_temporal_state_transition_on_v47/submission_s2_sleep_retrieval_meta.csv |
| s2_temporal_state_transition_knn_logitresid | 0.579365 | outputs/s2_temporal_state_transition_on_v47/oof_s2_temporal_state_transition_knn_logitresid.csv | outputs/s2_temporal_state_transition_on_v47/submission_s2_temporal_state_transition_knn_logitresid.csv |
| s2_temporal_state_transition_hgb | 0.623200 | outputs/s2_temporal_state_transition_on_v47/oof_s2_temporal_state_transition_hgb.csv | outputs/s2_temporal_state_transition_on_v47/submission_s2_temporal_state_transition_hgb.csv |
| s2_temporal_state_transition_extra | 0.685543 | outputs/s2_temporal_state_transition_on_v47/oof_s2_temporal_state_transition_extra.csv | outputs/s2_temporal_state_transition_on_v47/submission_s2_temporal_state_transition_extra.csv |
| s2_temporal_state_transition_knn_label | 0.687827 | outputs/s2_temporal_state_transition_on_v47/oof_s2_temporal_state_transition_knn_label.csv | outputs/s2_temporal_state_transition_on_v47/submission_s2_temporal_state_transition_knn_label.csv |
| s2_temporal_state_transition_proto | 0.730513 | outputs/s2_temporal_state_transition_on_v47/oof_s2_temporal_state_transition_proto.csv | outputs/s2_temporal_state_transition_on_v47/submission_s2_temporal_state_transition_proto.csv |
| s2_temporal_state_transition_logreg | 0.841165 | outputs/s2_temporal_state_transition_on_v47/oof_s2_temporal_state_transition_logreg.csv | outputs/s2_temporal_state_transition_on_v47/submission_s2_temporal_state_transition_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_transition | 35 |
