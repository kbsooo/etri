# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.560445`
- Best source Q2 OOF: `0.573346`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_sleep_retrieval_meta | 0.573346 | outputs/q2_temporal_state_manifold_on_v49/oof_q2_sleep_retrieval_meta.csv | outputs/q2_temporal_state_manifold_on_v49/submission_q2_sleep_retrieval_meta.csv |
| q2_temporal_state_transition_knn_resid | 0.629091 | outputs/q2_temporal_state_manifold_on_v49/oof_q2_temporal_state_transition_knn_resid.csv | outputs/q2_temporal_state_manifold_on_v49/submission_q2_temporal_state_transition_knn_resid.csv |
| q2_temporal_state_recurrence_knn_resid | 0.667938 | outputs/q2_temporal_state_manifold_on_v49/oof_q2_temporal_state_recurrence_knn_resid.csv | outputs/q2_temporal_state_manifold_on_v49/submission_q2_temporal_state_recurrence_knn_resid.csv |
| q2_temporal_state_recurrence_extra | 0.695327 | outputs/q2_temporal_state_manifold_on_v49/oof_q2_temporal_state_recurrence_extra.csv | outputs/q2_temporal_state_manifold_on_v49/submission_q2_temporal_state_recurrence_extra.csv |
| q2_temporal_state_transition_knn_logitresid | 0.703857 | outputs/q2_temporal_state_manifold_on_v49/oof_q2_temporal_state_transition_knn_logitresid.csv | outputs/q2_temporal_state_manifold_on_v49/submission_q2_temporal_state_transition_knn_logitresid.csv |
| q2_temporal_state_transition_extra | 0.707934 | outputs/q2_temporal_state_manifold_on_v49/oof_q2_temporal_state_transition_extra.csv | outputs/q2_temporal_state_manifold_on_v49/submission_q2_temporal_state_transition_extra.csv |
| q2_temporal_state_recurrence_knn_label | 0.718713 | outputs/q2_temporal_state_manifold_on_v49/oof_q2_temporal_state_recurrence_knn_label.csv | outputs/q2_temporal_state_manifold_on_v49/submission_q2_temporal_state_recurrence_knn_label.csv |
| q2_temporal_state_transition_knn_label | 0.719800 | outputs/q2_temporal_state_manifold_on_v49/oof_q2_temporal_state_transition_knn_label.csv | outputs/q2_temporal_state_manifold_on_v49/submission_q2_temporal_state_transition_knn_label.csv |
| q2_temporal_state_recurrence_hgb | 0.734829 | outputs/q2_temporal_state_manifold_on_v49/oof_q2_temporal_state_recurrence_hgb.csv | outputs/q2_temporal_state_manifold_on_v49/submission_q2_temporal_state_recurrence_hgb.csv |
| q2_temporal_state_recurrence_proto | 0.742322 | outputs/q2_temporal_state_manifold_on_v49/oof_q2_temporal_state_recurrence_proto.csv | outputs/q2_temporal_state_manifold_on_v49/submission_q2_temporal_state_recurrence_proto.csv |
| q2_temporal_state_recurrence_knn_logitresid | 0.743143 | outputs/q2_temporal_state_manifold_on_v49/oof_q2_temporal_state_recurrence_knn_logitresid.csv | outputs/q2_temporal_state_manifold_on_v49/submission_q2_temporal_state_recurrence_knn_logitresid.csv |
| q2_temporal_state_transition_hgb | 0.771703 | outputs/q2_temporal_state_manifold_on_v49/oof_q2_temporal_state_transition_hgb.csv | outputs/q2_temporal_state_manifold_on_v49/submission_q2_temporal_state_transition_hgb.csv |
| q2_temporal_state_transition_proto | 0.808084 | outputs/q2_temporal_state_manifold_on_v49/oof_q2_temporal_state_transition_proto.csv | outputs/q2_temporal_state_manifold_on_v49/submission_q2_temporal_state_transition_proto.csv |
| q2_temporal_state_recurrence_logreg | 0.856729 | outputs/q2_temporal_state_manifold_on_v49/oof_q2_temporal_state_recurrence_logreg.csv | outputs/q2_temporal_state_manifold_on_v49/submission_q2_temporal_state_recurrence_logreg.csv |
| q2_temporal_state_transition_logreg | 0.996364 | outputs/q2_temporal_state_manifold_on_v49/oof_q2_temporal_state_transition_logreg.csv | outputs/q2_temporal_state_manifold_on_v49/submission_q2_temporal_state_transition_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_transition | 35 |
| temporal_state_recurrence | 26 |
