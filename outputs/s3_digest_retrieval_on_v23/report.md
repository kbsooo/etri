# S3 sleep/missingness retrieval encoder

- Base S3 OOF: `0.480275`
- Best source S3 OOF: `0.517103`

## Sources

| name | S3_log_loss | oof | submission |
| --- | --- | --- | --- |
| s3_modality_desync_knn_resid | 0.517103 | outputs/s3_digest_retrieval_on_v23/oof_s3_modality_desync_knn_resid.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_modality_desync_knn_resid.csv |
| s3_social_rhythm_knn_resid | 0.541669 | outputs/s3_digest_retrieval_on_v23/oof_s3_social_rhythm_knn_resid.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_social_rhythm_knn_resid.csv |
| s3_sleep_retrieval_meta | 0.560465 | outputs/s3_digest_retrieval_on_v23/oof_s3_sleep_retrieval_meta.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_sleep_retrieval_meta.csv |
| s3_body_recovery_knn_resid | 0.568164 | outputs/s3_digest_retrieval_on_v23/oof_s3_body_recovery_knn_resid.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_body_recovery_knn_resid.csv |
| s3_modality_desync_hgb | 0.570094 | outputs/s3_digest_retrieval_on_v23/oof_s3_modality_desync_hgb.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_modality_desync_hgb.csv |
| s3_phone_recovery_knn_resid | 0.573201 | outputs/s3_digest_retrieval_on_v23/oof_s3_phone_recovery_knn_resid.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_phone_recovery_knn_resid.csv |
| s3_modality_desync_extra | 0.578804 | outputs/s3_digest_retrieval_on_v23/oof_s3_modality_desync_extra.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_modality_desync_extra.csv |
| s3_body_recovery_hgb | 0.580592 | outputs/s3_digest_retrieval_on_v23/oof_s3_body_recovery_hgb.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_body_recovery_hgb.csv |
| s3_social_rhythm_hgb | 0.582184 | outputs/s3_digest_retrieval_on_v23/oof_s3_social_rhythm_hgb.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_social_rhythm_hgb.csv |
| s3_social_rhythm_extra | 0.584366 | outputs/s3_digest_retrieval_on_v23/oof_s3_social_rhythm_extra.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_social_rhythm_extra.csv |
| s3_modality_desync_knn_label | 0.586056 | outputs/s3_digest_retrieval_on_v23/oof_s3_modality_desync_knn_label.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_modality_desync_knn_label.csv |
| s3_modality_desync_proto | 0.586060 | outputs/s3_digest_retrieval_on_v23/oof_s3_modality_desync_proto.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_modality_desync_proto.csv |
| s3_phone_recovery_hgb | 0.591283 | outputs/s3_digest_retrieval_on_v23/oof_s3_phone_recovery_hgb.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_phone_recovery_hgb.csv |
| s3_body_recovery_knn_logitresid | 0.598899 | outputs/s3_digest_retrieval_on_v23/oof_s3_body_recovery_knn_logitresid.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_body_recovery_knn_logitresid.csv |
| s3_social_rhythm_knn_logitresid | 0.600845 | outputs/s3_digest_retrieval_on_v23/oof_s3_social_rhythm_knn_logitresid.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_social_rhythm_knn_logitresid.csv |
| s3_phone_recovery_extra | 0.604068 | outputs/s3_digest_retrieval_on_v23/oof_s3_phone_recovery_extra.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_phone_recovery_extra.csv |
| s3_phone_recovery_knn_label | 0.604687 | outputs/s3_digest_retrieval_on_v23/oof_s3_phone_recovery_knn_label.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_phone_recovery_knn_label.csv |
| s3_phone_recovery_knn_logitresid | 0.606460 | outputs/s3_digest_retrieval_on_v23/oof_s3_phone_recovery_knn_logitresid.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_phone_recovery_knn_logitresid.csv |
| s3_social_rhythm_proto | 0.606701 | outputs/s3_digest_retrieval_on_v23/oof_s3_social_rhythm_proto.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_social_rhythm_proto.csv |
| s3_modality_desync_knn_logitresid | 0.609239 | outputs/s3_digest_retrieval_on_v23/oof_s3_modality_desync_knn_logitresid.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_modality_desync_knn_logitresid.csv |
| s3_phone_recovery_proto | 0.618383 | outputs/s3_digest_retrieval_on_v23/oof_s3_phone_recovery_proto.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_phone_recovery_proto.csv |
| s3_body_recovery_knn_label | 0.620401 | outputs/s3_digest_retrieval_on_v23/oof_s3_body_recovery_knn_label.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_body_recovery_knn_label.csv |
| s3_social_rhythm_knn_label | 0.635124 | outputs/s3_digest_retrieval_on_v23/oof_s3_social_rhythm_knn_label.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_social_rhythm_knn_label.csv |
| s3_body_recovery_extra | 0.635346 | outputs/s3_digest_retrieval_on_v23/oof_s3_body_recovery_extra.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_body_recovery_extra.csv |
| s3_body_recovery_proto | 0.653596 | outputs/s3_digest_retrieval_on_v23/oof_s3_body_recovery_proto.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_body_recovery_proto.csv |
| s3_modality_desync_logreg | 0.695763 | outputs/s3_digest_retrieval_on_v23/oof_s3_modality_desync_logreg.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_modality_desync_logreg.csv |
| s3_social_rhythm_logreg | 0.699260 | outputs/s3_digest_retrieval_on_v23/oof_s3_social_rhythm_logreg.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_social_rhythm_logreg.csv |
| s3_phone_recovery_logreg | 0.772546 | outputs/s3_digest_retrieval_on_v23/oof_s3_phone_recovery_logreg.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_phone_recovery_logreg.csv |
| s3_body_recovery_logreg | 0.809133 | outputs/s3_digest_retrieval_on_v23/oof_s3_body_recovery_logreg.csv | outputs/s3_digest_retrieval_on_v23/submission_s3_body_recovery_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| phone_recovery | 473 |
| social_rhythm | 638 |
| body_recovery | 840 |
| modality_desync | 1011 |
