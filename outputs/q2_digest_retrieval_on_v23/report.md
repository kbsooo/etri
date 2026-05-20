# Q2 sleep/missingness retrieval encoder

- Base Q2 OOF: `0.610811`
- Best source Q2 OOF: `0.634555`

## Sources

| name | Q2_log_loss | oof | submission |
| --- | --- | --- | --- |
| q2_sleep_retrieval_meta | 0.634555 | outputs/q2_digest_retrieval_on_v23/oof_q2_sleep_retrieval_meta.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_sleep_retrieval_meta.csv |
| q2_social_rhythm_knn_resid | 0.644688 | outputs/q2_digest_retrieval_on_v23/oof_q2_social_rhythm_knn_resid.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_social_rhythm_knn_resid.csv |
| q2_phone_recovery_knn_resid | 0.661811 | outputs/q2_digest_retrieval_on_v23/oof_q2_phone_recovery_knn_resid.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_phone_recovery_knn_resid.csv |
| q2_body_recovery_knn_resid | 0.667666 | outputs/q2_digest_retrieval_on_v23/oof_q2_body_recovery_knn_resid.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_body_recovery_knn_resid.csv |
| q2_modality_desync_knn_resid | 0.683621 | outputs/q2_digest_retrieval_on_v23/oof_q2_modality_desync_knn_resid.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_modality_desync_knn_resid.csv |
| q2_phone_recovery_extra | 0.686895 | outputs/q2_digest_retrieval_on_v23/oof_q2_phone_recovery_extra.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_phone_recovery_extra.csv |
| q2_body_recovery_extra | 0.699815 | outputs/q2_digest_retrieval_on_v23/oof_q2_body_recovery_extra.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_body_recovery_extra.csv |
| q2_phone_recovery_knn_label | 0.706955 | outputs/q2_digest_retrieval_on_v23/oof_q2_phone_recovery_knn_label.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_phone_recovery_knn_label.csv |
| q2_social_rhythm_extra | 0.709117 | outputs/q2_digest_retrieval_on_v23/oof_q2_social_rhythm_extra.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_social_rhythm_extra.csv |
| q2_modality_desync_extra | 0.715054 | outputs/q2_digest_retrieval_on_v23/oof_q2_modality_desync_extra.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_modality_desync_extra.csv |
| q2_phone_recovery_hgb | 0.728596 | outputs/q2_digest_retrieval_on_v23/oof_q2_phone_recovery_hgb.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_phone_recovery_hgb.csv |
| q2_body_recovery_knn_label | 0.729777 | outputs/q2_digest_retrieval_on_v23/oof_q2_body_recovery_knn_label.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_body_recovery_knn_label.csv |
| q2_social_rhythm_hgb | 0.732853 | outputs/q2_digest_retrieval_on_v23/oof_q2_social_rhythm_hgb.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_social_rhythm_hgb.csv |
| q2_modality_desync_knn_label | 0.742197 | outputs/q2_digest_retrieval_on_v23/oof_q2_modality_desync_knn_label.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_modality_desync_knn_label.csv |
| q2_modality_desync_hgb | 0.748080 | outputs/q2_digest_retrieval_on_v23/oof_q2_modality_desync_hgb.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_modality_desync_hgb.csv |
| q2_social_rhythm_knn_label | 0.749697 | outputs/q2_digest_retrieval_on_v23/oof_q2_social_rhythm_knn_label.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_social_rhythm_knn_label.csv |
| q2_body_recovery_hgb | 0.749995 | outputs/q2_digest_retrieval_on_v23/oof_q2_body_recovery_hgb.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_body_recovery_hgb.csv |
| q2_phone_recovery_proto | 0.753592 | outputs/q2_digest_retrieval_on_v23/oof_q2_phone_recovery_proto.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_phone_recovery_proto.csv |
| q2_phone_recovery_knn_logitresid | 0.753720 | outputs/q2_digest_retrieval_on_v23/oof_q2_phone_recovery_knn_logitresid.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_phone_recovery_knn_logitresid.csv |
| q2_social_rhythm_knn_logitresid | 0.754566 | outputs/q2_digest_retrieval_on_v23/oof_q2_social_rhythm_knn_logitresid.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_social_rhythm_knn_logitresid.csv |
| q2_body_recovery_proto | 0.762174 | outputs/q2_digest_retrieval_on_v23/oof_q2_body_recovery_proto.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_body_recovery_proto.csv |
| q2_modality_desync_proto | 0.771468 | outputs/q2_digest_retrieval_on_v23/oof_q2_modality_desync_proto.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_modality_desync_proto.csv |
| q2_body_recovery_knn_logitresid | 0.790605 | outputs/q2_digest_retrieval_on_v23/oof_q2_body_recovery_knn_logitresid.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_body_recovery_knn_logitresid.csv |
| q2_modality_desync_knn_logitresid | 0.793392 | outputs/q2_digest_retrieval_on_v23/oof_q2_modality_desync_knn_logitresid.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_modality_desync_knn_logitresid.csv |
| q2_social_rhythm_proto | 0.798134 | outputs/q2_digest_retrieval_on_v23/oof_q2_social_rhythm_proto.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_social_rhythm_proto.csv |
| q2_modality_desync_logreg | 0.822821 | outputs/q2_digest_retrieval_on_v23/oof_q2_modality_desync_logreg.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_modality_desync_logreg.csv |
| q2_social_rhythm_logreg | 0.837319 | outputs/q2_digest_retrieval_on_v23/oof_q2_social_rhythm_logreg.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_social_rhythm_logreg.csv |
| q2_body_recovery_logreg | 0.877883 | outputs/q2_digest_retrieval_on_v23/oof_q2_body_recovery_logreg.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_body_recovery_logreg.csv |
| q2_phone_recovery_logreg | 0.880362 | outputs/q2_digest_retrieval_on_v23/oof_q2_phone_recovery_logreg.csv | outputs/q2_digest_retrieval_on_v23/submission_q2_phone_recovery_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| phone_recovery | 473 |
| social_rhythm | 638 |
| body_recovery | 840 |
| modality_desync | 1011 |
