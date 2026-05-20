# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.565758`
- Best source Q2 OOF: `0.565805`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_sleep_retrieval_meta | 0.565805 | outputs/q2_temporal_state_transition_on_v47/oof_q2_sleep_retrieval_meta.csv | outputs/q2_temporal_state_transition_on_v47/submission_q2_sleep_retrieval_meta.csv |
| q2_temporal_state_transition_knn_resid | 0.634995 | outputs/q2_temporal_state_transition_on_v47/oof_q2_temporal_state_transition_knn_resid.csv | outputs/q2_temporal_state_transition_on_v47/submission_q2_temporal_state_transition_knn_resid.csv |
| q2_temporal_state_transition_extra | 0.707934 | outputs/q2_temporal_state_transition_on_v47/oof_q2_temporal_state_transition_extra.csv | outputs/q2_temporal_state_transition_on_v47/submission_q2_temporal_state_transition_extra.csv |
| q2_temporal_state_transition_knn_logitresid | 0.716366 | outputs/q2_temporal_state_transition_on_v47/oof_q2_temporal_state_transition_knn_logitresid.csv | outputs/q2_temporal_state_transition_on_v47/submission_q2_temporal_state_transition_knn_logitresid.csv |
| q2_temporal_state_transition_knn_label | 0.719800 | outputs/q2_temporal_state_transition_on_v47/oof_q2_temporal_state_transition_knn_label.csv | outputs/q2_temporal_state_transition_on_v47/submission_q2_temporal_state_transition_knn_label.csv |
| q2_temporal_state_transition_hgb | 0.771703 | outputs/q2_temporal_state_transition_on_v47/oof_q2_temporal_state_transition_hgb.csv | outputs/q2_temporal_state_transition_on_v47/submission_q2_temporal_state_transition_hgb.csv |
| q2_temporal_state_transition_proto | 0.808084 | outputs/q2_temporal_state_transition_on_v47/oof_q2_temporal_state_transition_proto.csv | outputs/q2_temporal_state_transition_on_v47/submission_q2_temporal_state_transition_proto.csv |
| q2_temporal_state_transition_logreg | 0.996364 | outputs/q2_temporal_state_transition_on_v47/oof_q2_temporal_state_transition_logreg.csv | outputs/q2_temporal_state_transition_on_v47/submission_q2_temporal_state_transition_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_transition | 35 |
