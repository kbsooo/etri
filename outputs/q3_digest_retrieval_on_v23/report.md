# Q3 sleep/missingness retrieval encoder

- Base Q3 OOF: `0.597243`
- Best source Q3 OOF: `0.633028`

## Sources

| name | Q3_log_loss | oof | submission |
| --- | --- | --- | --- |
| q3_social_rhythm_knn_resid | 0.633028 | outputs/q3_digest_retrieval_on_v23/oof_q3_social_rhythm_knn_resid.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_social_rhythm_knn_resid.csv |
| q3_modality_desync_knn_resid | 0.633240 | outputs/q3_digest_retrieval_on_v23/oof_q3_modality_desync_knn_resid.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_modality_desync_knn_resid.csv |
| q3_sleep_retrieval_meta | 0.634280 | outputs/q3_digest_retrieval_on_v23/oof_q3_sleep_retrieval_meta.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_sleep_retrieval_meta.csv |
| q3_body_recovery_knn_resid | 0.661020 | outputs/q3_digest_retrieval_on_v23/oof_q3_body_recovery_knn_resid.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_body_recovery_knn_resid.csv |
| q3_phone_recovery_knn_resid | 0.666176 | outputs/q3_digest_retrieval_on_v23/oof_q3_phone_recovery_knn_resid.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_phone_recovery_knn_resid.csv |
| q3_body_recovery_knn_label | 0.671516 | outputs/q3_digest_retrieval_on_v23/oof_q3_body_recovery_knn_label.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_body_recovery_knn_label.csv |
| q3_modality_desync_extra | 0.673142 | outputs/q3_digest_retrieval_on_v23/oof_q3_modality_desync_extra.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_modality_desync_extra.csv |
| q3_social_rhythm_knn_label | 0.673404 | outputs/q3_digest_retrieval_on_v23/oof_q3_social_rhythm_knn_label.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_social_rhythm_knn_label.csv |
| q3_social_rhythm_extra | 0.675187 | outputs/q3_digest_retrieval_on_v23/oof_q3_social_rhythm_extra.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_social_rhythm_extra.csv |
| q3_body_recovery_extra | 0.676687 | outputs/q3_digest_retrieval_on_v23/oof_q3_body_recovery_extra.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_body_recovery_extra.csv |
| q3_phone_recovery_extra | 0.678708 | outputs/q3_digest_retrieval_on_v23/oof_q3_phone_recovery_extra.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_phone_recovery_extra.csv |
| q3_modality_desync_knn_label | 0.678877 | outputs/q3_digest_retrieval_on_v23/oof_q3_modality_desync_knn_label.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_modality_desync_knn_label.csv |
| q3_modality_desync_hgb | 0.682210 | outputs/q3_digest_retrieval_on_v23/oof_q3_modality_desync_hgb.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_modality_desync_hgb.csv |
| q3_body_recovery_hgb | 0.682662 | outputs/q3_digest_retrieval_on_v23/oof_q3_body_recovery_hgb.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_body_recovery_hgb.csv |
| q3_phone_recovery_knn_label | 0.682870 | outputs/q3_digest_retrieval_on_v23/oof_q3_phone_recovery_knn_label.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_phone_recovery_knn_label.csv |
| q3_phone_recovery_hgb | 0.683734 | outputs/q3_digest_retrieval_on_v23/oof_q3_phone_recovery_hgb.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_phone_recovery_hgb.csv |
| q3_body_recovery_proto | 0.688446 | outputs/q3_digest_retrieval_on_v23/oof_q3_body_recovery_proto.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_body_recovery_proto.csv |
| q3_phone_recovery_proto | 0.688977 | outputs/q3_digest_retrieval_on_v23/oof_q3_phone_recovery_proto.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_phone_recovery_proto.csv |
| q3_modality_desync_proto | 0.695675 | outputs/q3_digest_retrieval_on_v23/oof_q3_modality_desync_proto.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_modality_desync_proto.csv |
| q3_social_rhythm_hgb | 0.697193 | outputs/q3_digest_retrieval_on_v23/oof_q3_social_rhythm_hgb.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_social_rhythm_hgb.csv |
| q3_social_rhythm_proto | 0.728606 | outputs/q3_digest_retrieval_on_v23/oof_q3_social_rhythm_proto.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_social_rhythm_proto.csv |
| q3_modality_desync_knn_logitresid | 0.744501 | outputs/q3_digest_retrieval_on_v23/oof_q3_modality_desync_knn_logitresid.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_modality_desync_knn_logitresid.csv |
| q3_social_rhythm_knn_logitresid | 0.750858 | outputs/q3_digest_retrieval_on_v23/oof_q3_social_rhythm_knn_logitresid.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_social_rhythm_knn_logitresid.csv |
| q3_body_recovery_knn_logitresid | 0.758577 | outputs/q3_digest_retrieval_on_v23/oof_q3_body_recovery_knn_logitresid.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_body_recovery_knn_logitresid.csv |
| q3_modality_desync_logreg | 0.775353 | outputs/q3_digest_retrieval_on_v23/oof_q3_modality_desync_logreg.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_modality_desync_logreg.csv |
| q3_phone_recovery_knn_logitresid | 0.792136 | outputs/q3_digest_retrieval_on_v23/oof_q3_phone_recovery_knn_logitresid.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_phone_recovery_knn_logitresid.csv |
| q3_social_rhythm_logreg | 0.798586 | outputs/q3_digest_retrieval_on_v23/oof_q3_social_rhythm_logreg.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_social_rhythm_logreg.csv |
| q3_phone_recovery_logreg | 0.806879 | outputs/q3_digest_retrieval_on_v23/oof_q3_phone_recovery_logreg.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_phone_recovery_logreg.csv |
| q3_body_recovery_logreg | 0.843432 | outputs/q3_digest_retrieval_on_v23/oof_q3_body_recovery_logreg.csv | outputs/q3_digest_retrieval_on_v23/submission_q3_body_recovery_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| phone_recovery | 473 |
| social_rhythm | 638 |
| body_recovery | 840 |
| modality_desync | 1011 |
