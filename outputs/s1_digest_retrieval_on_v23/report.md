# S1 sleep/missingness retrieval encoder

- Base S1 OOF: `0.532737`
- Best source S1 OOF: `0.587985`

## Sources

| name | S1_log_loss | oof | submission |
| --- | --- | --- | --- |
| s1_modality_desync_hgb | 0.587985 | outputs/s1_digest_retrieval_on_v23/oof_s1_modality_desync_hgb.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_modality_desync_hgb.csv |
| s1_phone_recovery_hgb | 0.589843 | outputs/s1_digest_retrieval_on_v23/oof_s1_phone_recovery_hgb.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_phone_recovery_hgb.csv |
| s1_modality_desync_proto | 0.597903 | outputs/s1_digest_retrieval_on_v23/oof_s1_modality_desync_proto.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_modality_desync_proto.csv |
| s1_body_recovery_hgb | 0.603643 | outputs/s1_digest_retrieval_on_v23/oof_s1_body_recovery_hgb.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_body_recovery_hgb.csv |
| s1_phone_recovery_knn_label | 0.609207 | outputs/s1_digest_retrieval_on_v23/oof_s1_phone_recovery_knn_label.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_phone_recovery_knn_label.csv |
| s1_phone_recovery_extra | 0.618753 | outputs/s1_digest_retrieval_on_v23/oof_s1_phone_recovery_extra.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_phone_recovery_extra.csv |
| s1_phone_recovery_proto | 0.619946 | outputs/s1_digest_retrieval_on_v23/oof_s1_phone_recovery_proto.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_phone_recovery_proto.csv |
| s1_social_rhythm_hgb | 0.620064 | outputs/s1_digest_retrieval_on_v23/oof_s1_social_rhythm_hgb.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_social_rhythm_hgb.csv |
| s1_modality_desync_extra | 0.625675 | outputs/s1_digest_retrieval_on_v23/oof_s1_modality_desync_extra.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_modality_desync_extra.csv |
| s1_social_rhythm_extra | 0.630560 | outputs/s1_digest_retrieval_on_v23/oof_s1_social_rhythm_extra.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_social_rhythm_extra.csv |
| s1_body_recovery_proto | 0.631552 | outputs/s1_digest_retrieval_on_v23/oof_s1_body_recovery_proto.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_body_recovery_proto.csv |
| s1_social_rhythm_knn_resid | 0.634993 | outputs/s1_digest_retrieval_on_v23/oof_s1_social_rhythm_knn_resid.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_social_rhythm_knn_resid.csv |
| s1_sleep_retrieval_meta | 0.637068 | outputs/s1_digest_retrieval_on_v23/oof_s1_sleep_retrieval_meta.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_sleep_retrieval_meta.csv |
| s1_body_recovery_extra | 0.641505 | outputs/s1_digest_retrieval_on_v23/oof_s1_body_recovery_extra.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_body_recovery_extra.csv |
| s1_body_recovery_knn_resid | 0.641919 | outputs/s1_digest_retrieval_on_v23/oof_s1_body_recovery_knn_resid.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_body_recovery_knn_resid.csv |
| s1_body_recovery_knn_label | 0.644741 | outputs/s1_digest_retrieval_on_v23/oof_s1_body_recovery_knn_label.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_body_recovery_knn_label.csv |
| s1_modality_desync_knn_resid | 0.646271 | outputs/s1_digest_retrieval_on_v23/oof_s1_modality_desync_knn_resid.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_modality_desync_knn_resid.csv |
| s1_social_rhythm_proto | 0.649390 | outputs/s1_digest_retrieval_on_v23/oof_s1_social_rhythm_proto.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_social_rhythm_proto.csv |
| s1_modality_desync_knn_label | 0.649879 | outputs/s1_digest_retrieval_on_v23/oof_s1_modality_desync_knn_label.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_modality_desync_knn_label.csv |
| s1_social_rhythm_knn_label | 0.662880 | outputs/s1_digest_retrieval_on_v23/oof_s1_social_rhythm_knn_label.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_social_rhythm_knn_label.csv |
| s1_social_rhythm_knn_logitresid | 0.674571 | outputs/s1_digest_retrieval_on_v23/oof_s1_social_rhythm_knn_logitresid.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_social_rhythm_knn_logitresid.csv |
| s1_phone_recovery_knn_resid | 0.684912 | outputs/s1_digest_retrieval_on_v23/oof_s1_phone_recovery_knn_resid.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_phone_recovery_knn_resid.csv |
| s1_phone_recovery_knn_logitresid | 0.697147 | outputs/s1_digest_retrieval_on_v23/oof_s1_phone_recovery_knn_logitresid.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_phone_recovery_knn_logitresid.csv |
| s1_modality_desync_knn_logitresid | 0.705294 | outputs/s1_digest_retrieval_on_v23/oof_s1_modality_desync_knn_logitresid.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_modality_desync_knn_logitresid.csv |
| s1_body_recovery_knn_logitresid | 0.708556 | outputs/s1_digest_retrieval_on_v23/oof_s1_body_recovery_knn_logitresid.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_body_recovery_knn_logitresid.csv |
| s1_modality_desync_logreg | 0.716121 | outputs/s1_digest_retrieval_on_v23/oof_s1_modality_desync_logreg.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_modality_desync_logreg.csv |
| s1_social_rhythm_logreg | 0.761042 | outputs/s1_digest_retrieval_on_v23/oof_s1_social_rhythm_logreg.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_social_rhythm_logreg.csv |
| s1_body_recovery_logreg | 0.780325 | outputs/s1_digest_retrieval_on_v23/oof_s1_body_recovery_logreg.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_body_recovery_logreg.csv |
| s1_phone_recovery_logreg | 0.819238 | outputs/s1_digest_retrieval_on_v23/oof_s1_phone_recovery_logreg.csv | outputs/s1_digest_retrieval_on_v23/submission_s1_phone_recovery_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| phone_recovery | 473 |
| social_rhythm | 638 |
| body_recovery | 840 |
| modality_desync | 1011 |
