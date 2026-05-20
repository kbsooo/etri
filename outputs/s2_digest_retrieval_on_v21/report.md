# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.504521`
- Best source S2 OOF: `0.555741`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_modality_desync_knn_resid | 0.555741 | outputs/s2_digest_retrieval_on_v21/oof_s2_modality_desync_knn_resid.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_modality_desync_knn_resid.csv |
| s2_phone_recovery_knn_resid | 0.567528 | outputs/s2_digest_retrieval_on_v21/oof_s2_phone_recovery_knn_resid.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_phone_recovery_knn_resid.csv |
| s2_sleep_retrieval_meta | 0.567535 | outputs/s2_digest_retrieval_on_v21/oof_s2_sleep_retrieval_meta.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_sleep_retrieval_meta.csv |
| s2_social_rhythm_knn_resid | 0.578755 | outputs/s2_digest_retrieval_on_v21/oof_s2_social_rhythm_knn_resid.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_social_rhythm_knn_resid.csv |
| s2_modality_desync_hgb | 0.603345 | outputs/s2_digest_retrieval_on_v21/oof_s2_modality_desync_hgb.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_modality_desync_hgb.csv |
| s2_phone_recovery_hgb | 0.605894 | outputs/s2_digest_retrieval_on_v21/oof_s2_phone_recovery_hgb.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_phone_recovery_hgb.csv |
| s2_modality_desync_extra | 0.606693 | outputs/s2_digest_retrieval_on_v21/oof_s2_modality_desync_extra.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_modality_desync_extra.csv |
| s2_phone_recovery_knn_logitresid | 0.614232 | outputs/s2_digest_retrieval_on_v21/oof_s2_phone_recovery_knn_logitresid.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_phone_recovery_knn_logitresid.csv |
| s2_social_rhythm_knn_label | 0.615026 | outputs/s2_digest_retrieval_on_v21/oof_s2_social_rhythm_knn_label.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_social_rhythm_knn_label.csv |
| s2_social_rhythm_extra | 0.617319 | outputs/s2_digest_retrieval_on_v21/oof_s2_social_rhythm_extra.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_social_rhythm_extra.csv |
| s2_body_recovery_knn_resid | 0.619183 | outputs/s2_digest_retrieval_on_v21/oof_s2_body_recovery_knn_resid.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_body_recovery_knn_resid.csv |
| s2_modality_desync_knn_label | 0.626096 | outputs/s2_digest_retrieval_on_v21/oof_s2_modality_desync_knn_label.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_modality_desync_knn_label.csv |
| s2_phone_recovery_extra | 0.626114 | outputs/s2_digest_retrieval_on_v21/oof_s2_phone_recovery_extra.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_phone_recovery_extra.csv |
| s2_modality_desync_knn_logitresid | 0.626168 | outputs/s2_digest_retrieval_on_v21/oof_s2_modality_desync_knn_logitresid.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_modality_desync_knn_logitresid.csv |
| s2_social_rhythm_hgb | 0.627777 | outputs/s2_digest_retrieval_on_v21/oof_s2_social_rhythm_hgb.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_social_rhythm_hgb.csv |
| s2_body_recovery_knn_logitresid | 0.632238 | outputs/s2_digest_retrieval_on_v21/oof_s2_body_recovery_knn_logitresid.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_body_recovery_knn_logitresid.csv |
| s2_phone_recovery_proto | 0.637035 | outputs/s2_digest_retrieval_on_v21/oof_s2_phone_recovery_proto.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_phone_recovery_proto.csv |
| s2_modality_desync_proto | 0.637716 | outputs/s2_digest_retrieval_on_v21/oof_s2_modality_desync_proto.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_modality_desync_proto.csv |
| s2_social_rhythm_proto | 0.642123 | outputs/s2_digest_retrieval_on_v21/oof_s2_social_rhythm_proto.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_social_rhythm_proto.csv |
| s2_phone_recovery_knn_label | 0.643209 | outputs/s2_digest_retrieval_on_v21/oof_s2_phone_recovery_knn_label.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_phone_recovery_knn_label.csv |
| s2_body_recovery_hgb | 0.643719 | outputs/s2_digest_retrieval_on_v21/oof_s2_body_recovery_hgb.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_body_recovery_hgb.csv |
| s2_social_rhythm_knn_logitresid | 0.643890 | outputs/s2_digest_retrieval_on_v21/oof_s2_social_rhythm_knn_logitresid.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_social_rhythm_knn_logitresid.csv |
| s2_body_recovery_extra | 0.647248 | outputs/s2_digest_retrieval_on_v21/oof_s2_body_recovery_extra.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_body_recovery_extra.csv |
| s2_body_recovery_knn_label | 0.654684 | outputs/s2_digest_retrieval_on_v21/oof_s2_body_recovery_knn_label.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_body_recovery_knn_label.csv |
| s2_body_recovery_proto | 0.662442 | outputs/s2_digest_retrieval_on_v21/oof_s2_body_recovery_proto.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_body_recovery_proto.csv |
| s2_modality_desync_logreg | 0.733509 | outputs/s2_digest_retrieval_on_v21/oof_s2_modality_desync_logreg.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_modality_desync_logreg.csv |
| s2_body_recovery_logreg | 0.764704 | outputs/s2_digest_retrieval_on_v21/oof_s2_body_recovery_logreg.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_body_recovery_logreg.csv |
| s2_phone_recovery_logreg | 0.780788 | outputs/s2_digest_retrieval_on_v21/oof_s2_phone_recovery_logreg.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_phone_recovery_logreg.csv |
| s2_social_rhythm_logreg | 0.803944 | outputs/s2_digest_retrieval_on_v21/oof_s2_social_rhythm_logreg.csv | outputs/s2_digest_retrieval_on_v21/submission_s2_social_rhythm_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| phone_recovery | 473 |
| social_rhythm | 638 |
| body_recovery | 840 |
| modality_desync | 1011 |
