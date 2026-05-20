# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.504089`
- Best source S4 OOF: `0.535292`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_sleep_retrieval_meta | 0.535292 | outputs/s4_temporal_state_manifold_on_v49/oof_s4_sleep_retrieval_meta.csv | outputs/s4_temporal_state_manifold_on_v49/submission_s4_sleep_retrieval_meta.csv |
| s4_temporal_state_recurrence_knn_resid | 0.563209 | outputs/s4_temporal_state_manifold_on_v49/oof_s4_temporal_state_recurrence_knn_resid.csv | outputs/s4_temporal_state_manifold_on_v49/submission_s4_temporal_state_recurrence_knn_resid.csv |
| s4_temporal_state_transition_knn_resid | 0.575623 | outputs/s4_temporal_state_manifold_on_v49/oof_s4_temporal_state_transition_knn_resid.csv | outputs/s4_temporal_state_manifold_on_v49/submission_s4_temporal_state_transition_knn_resid.csv |
| s4_temporal_state_transition_knn_logitresid | 0.611585 | outputs/s4_temporal_state_manifold_on_v49/oof_s4_temporal_state_transition_knn_logitresid.csv | outputs/s4_temporal_state_manifold_on_v49/submission_s4_temporal_state_transition_knn_logitresid.csv |
| s4_temporal_state_recurrence_knn_logitresid | 0.626748 | outputs/s4_temporal_state_manifold_on_v49/oof_s4_temporal_state_recurrence_knn_logitresid.csv | outputs/s4_temporal_state_manifold_on_v49/submission_s4_temporal_state_recurrence_knn_logitresid.csv |
| s4_temporal_state_transition_extra | 0.689819 | outputs/s4_temporal_state_manifold_on_v49/oof_s4_temporal_state_transition_extra.csv | outputs/s4_temporal_state_manifold_on_v49/submission_s4_temporal_state_transition_extra.csv |
| s4_temporal_state_recurrence_extra | 0.690102 | outputs/s4_temporal_state_manifold_on_v49/oof_s4_temporal_state_recurrence_extra.csv | outputs/s4_temporal_state_manifold_on_v49/submission_s4_temporal_state_recurrence_extra.csv |
| s4_temporal_state_transition_hgb | 0.692277 | outputs/s4_temporal_state_manifold_on_v49/oof_s4_temporal_state_transition_hgb.csv | outputs/s4_temporal_state_manifold_on_v49/submission_s4_temporal_state_transition_hgb.csv |
| s4_temporal_state_recurrence_knn_label | 0.708052 | outputs/s4_temporal_state_manifold_on_v49/oof_s4_temporal_state_recurrence_knn_label.csv | outputs/s4_temporal_state_manifold_on_v49/submission_s4_temporal_state_recurrence_knn_label.csv |
| s4_temporal_state_transition_knn_label | 0.708233 | outputs/s4_temporal_state_manifold_on_v49/oof_s4_temporal_state_transition_knn_label.csv | outputs/s4_temporal_state_manifold_on_v49/submission_s4_temporal_state_transition_knn_label.csv |
| s4_temporal_state_recurrence_hgb | 0.729630 | outputs/s4_temporal_state_manifold_on_v49/oof_s4_temporal_state_recurrence_hgb.csv | outputs/s4_temporal_state_manifold_on_v49/submission_s4_temporal_state_recurrence_hgb.csv |
| s4_temporal_state_recurrence_proto | 0.754532 | outputs/s4_temporal_state_manifold_on_v49/oof_s4_temporal_state_recurrence_proto.csv | outputs/s4_temporal_state_manifold_on_v49/submission_s4_temporal_state_recurrence_proto.csv |
| s4_temporal_state_transition_proto | 0.771160 | outputs/s4_temporal_state_manifold_on_v49/oof_s4_temporal_state_transition_proto.csv | outputs/s4_temporal_state_manifold_on_v49/submission_s4_temporal_state_transition_proto.csv |
| s4_temporal_state_recurrence_logreg | 0.869933 | outputs/s4_temporal_state_manifold_on_v49/oof_s4_temporal_state_recurrence_logreg.csv | outputs/s4_temporal_state_manifold_on_v49/submission_s4_temporal_state_recurrence_logreg.csv |
| s4_temporal_state_transition_logreg | 0.883235 | outputs/s4_temporal_state_manifold_on_v49/oof_s4_temporal_state_transition_logreg.csv | outputs/s4_temporal_state_manifold_on_v49/submission_s4_temporal_state_transition_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| temporal_state_transition | 35 |
| temporal_state_recurrence | 26 |
