# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.600614`
- Best source Q1 OOF: `0.612899`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.612899 | outputs/q1_digest_retrieval_on_v21/oof_q1_sleep_retrieval_meta.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_sleep_retrieval_meta.csv |
| q1_social_rhythm_extra | 0.666359 | outputs/q1_digest_retrieval_on_v21/oof_q1_social_rhythm_extra.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_social_rhythm_extra.csv |
| q1_social_rhythm_proto | 0.667706 | outputs/q1_digest_retrieval_on_v21/oof_q1_social_rhythm_proto.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_social_rhythm_proto.csv |
| q1_body_recovery_extra | 0.672723 | outputs/q1_digest_retrieval_on_v21/oof_q1_body_recovery_extra.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_body_recovery_extra.csv |
| q1_modality_desync_extra | 0.673141 | outputs/q1_digest_retrieval_on_v21/oof_q1_modality_desync_extra.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_modality_desync_extra.csv |
| q1_modality_desync_knn_resid | 0.673829 | outputs/q1_digest_retrieval_on_v21/oof_q1_modality_desync_knn_resid.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_modality_desync_knn_resid.csv |
| q1_social_rhythm_logreg | 0.673866 | outputs/q1_digest_retrieval_on_v21/oof_q1_social_rhythm_logreg.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_social_rhythm_logreg.csv |
| q1_phone_recovery_knn_resid | 0.673883 | outputs/q1_digest_retrieval_on_v21/oof_q1_phone_recovery_knn_resid.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_phone_recovery_knn_resid.csv |
| q1_body_recovery_knn_resid | 0.675378 | outputs/q1_digest_retrieval_on_v21/oof_q1_body_recovery_knn_resid.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_body_recovery_knn_resid.csv |
| q1_social_rhythm_knn_resid | 0.677891 | outputs/q1_digest_retrieval_on_v21/oof_q1_social_rhythm_knn_resid.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_social_rhythm_knn_resid.csv |
| q1_social_rhythm_hgb | 0.680126 | outputs/q1_digest_retrieval_on_v21/oof_q1_social_rhythm_hgb.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_social_rhythm_hgb.csv |
| q1_phone_recovery_extra | 0.683208 | outputs/q1_digest_retrieval_on_v21/oof_q1_phone_recovery_extra.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_phone_recovery_extra.csv |
| q1_modality_desync_proto | 0.690498 | outputs/q1_digest_retrieval_on_v21/oof_q1_modality_desync_proto.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_modality_desync_proto.csv |
| q1_modality_desync_hgb | 0.699024 | outputs/q1_digest_retrieval_on_v21/oof_q1_modality_desync_hgb.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_modality_desync_hgb.csv |
| q1_social_rhythm_knn_label | 0.699115 | outputs/q1_digest_retrieval_on_v21/oof_q1_social_rhythm_knn_label.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_social_rhythm_knn_label.csv |
| q1_modality_desync_knn_label | 0.702262 | outputs/q1_digest_retrieval_on_v21/oof_q1_modality_desync_knn_label.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_modality_desync_knn_label.csv |
| q1_body_recovery_hgb | 0.710214 | outputs/q1_digest_retrieval_on_v21/oof_q1_body_recovery_hgb.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_body_recovery_hgb.csv |
| q1_body_recovery_proto | 0.712087 | outputs/q1_digest_retrieval_on_v21/oof_q1_body_recovery_proto.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_body_recovery_proto.csv |
| q1_body_recovery_knn_label | 0.712230 | outputs/q1_digest_retrieval_on_v21/oof_q1_body_recovery_knn_label.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_body_recovery_knn_label.csv |
| q1_phone_recovery_knn_label | 0.717327 | outputs/q1_digest_retrieval_on_v21/oof_q1_phone_recovery_knn_label.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_phone_recovery_knn_label.csv |
| q1_social_rhythm_knn_logitresid | 0.717879 | outputs/q1_digest_retrieval_on_v21/oof_q1_social_rhythm_knn_logitresid.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_social_rhythm_knn_logitresid.csv |
| q1_phone_recovery_hgb | 0.723498 | outputs/q1_digest_retrieval_on_v21/oof_q1_phone_recovery_hgb.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_phone_recovery_hgb.csv |
| q1_modality_desync_knn_logitresid | 0.742984 | outputs/q1_digest_retrieval_on_v21/oof_q1_modality_desync_knn_logitresid.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_modality_desync_knn_logitresid.csv |
| q1_phone_recovery_knn_logitresid | 0.765869 | outputs/q1_digest_retrieval_on_v21/oof_q1_phone_recovery_knn_logitresid.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_phone_recovery_knn_logitresid.csv |
| q1_body_recovery_knn_logitresid | 0.770674 | outputs/q1_digest_retrieval_on_v21/oof_q1_body_recovery_knn_logitresid.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_body_recovery_knn_logitresid.csv |
| q1_phone_recovery_proto | 0.809387 | outputs/q1_digest_retrieval_on_v21/oof_q1_phone_recovery_proto.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_phone_recovery_proto.csv |
| q1_modality_desync_logreg | 0.824125 | outputs/q1_digest_retrieval_on_v21/oof_q1_modality_desync_logreg.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_modality_desync_logreg.csv |
| q1_body_recovery_logreg | 0.889858 | outputs/q1_digest_retrieval_on_v21/oof_q1_body_recovery_logreg.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_body_recovery_logreg.csv |
| q1_phone_recovery_logreg | 0.951414 | outputs/q1_digest_retrieval_on_v21/oof_q1_phone_recovery_logreg.csv | outputs/q1_digest_retrieval_on_v21/submission_q1_phone_recovery_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| phone_recovery | 473 |
| social_rhythm | 638 |
| body_recovery | 840 |
| modality_desync | 1011 |
