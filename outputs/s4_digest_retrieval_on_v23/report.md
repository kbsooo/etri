# S4 sleep/missingness retrieval encoder

- Base S4 OOF: `0.564959`
- Best source S4 OOF: `0.582661`

## Sources

| name | S4_log_loss | oof | submission |
| --- | --- | --- | --- |
| s4_sleep_retrieval_meta | 0.582661 | outputs/s4_digest_retrieval_on_v23/oof_s4_sleep_retrieval_meta.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_sleep_retrieval_meta.csv |
| s4_phone_recovery_knn_resid | 0.622210 | outputs/s4_digest_retrieval_on_v23/oof_s4_phone_recovery_knn_resid.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_phone_recovery_knn_resid.csv |
| s4_modality_desync_knn_resid | 0.633789 | outputs/s4_digest_retrieval_on_v23/oof_s4_modality_desync_knn_resid.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_modality_desync_knn_resid.csv |
| s4_modality_desync_hgb | 0.643826 | outputs/s4_digest_retrieval_on_v23/oof_s4_modality_desync_hgb.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_modality_desync_hgb.csv |
| s4_body_recovery_knn_resid | 0.643909 | outputs/s4_digest_retrieval_on_v23/oof_s4_body_recovery_knn_resid.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_body_recovery_knn_resid.csv |
| s4_social_rhythm_knn_resid | 0.653339 | outputs/s4_digest_retrieval_on_v23/oof_s4_social_rhythm_knn_resid.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_social_rhythm_knn_resid.csv |
| s4_modality_desync_extra | 0.659881 | outputs/s4_digest_retrieval_on_v23/oof_s4_modality_desync_extra.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_modality_desync_extra.csv |
| s4_social_rhythm_extra | 0.660817 | outputs/s4_digest_retrieval_on_v23/oof_s4_social_rhythm_extra.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_social_rhythm_extra.csv |
| s4_modality_desync_knn_label | 0.662398 | outputs/s4_digest_retrieval_on_v23/oof_s4_modality_desync_knn_label.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_modality_desync_knn_label.csv |
| s4_body_recovery_hgb | 0.663449 | outputs/s4_digest_retrieval_on_v23/oof_s4_body_recovery_hgb.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_body_recovery_hgb.csv |
| s4_modality_desync_proto | 0.664943 | outputs/s4_digest_retrieval_on_v23/oof_s4_modality_desync_proto.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_modality_desync_proto.csv |
| s4_social_rhythm_knn_label | 0.666800 | outputs/s4_digest_retrieval_on_v23/oof_s4_social_rhythm_knn_label.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_social_rhythm_knn_label.csv |
| s4_social_rhythm_hgb | 0.668329 | outputs/s4_digest_retrieval_on_v23/oof_s4_social_rhythm_hgb.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_social_rhythm_hgb.csv |
| s4_modality_desync_knn_logitresid | 0.673016 | outputs/s4_digest_retrieval_on_v23/oof_s4_modality_desync_knn_logitresid.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_modality_desync_knn_logitresid.csv |
| s4_body_recovery_extra | 0.673369 | outputs/s4_digest_retrieval_on_v23/oof_s4_body_recovery_extra.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_body_recovery_extra.csv |
| s4_phone_recovery_hgb | 0.674803 | outputs/s4_digest_retrieval_on_v23/oof_s4_phone_recovery_hgb.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_phone_recovery_hgb.csv |
| s4_phone_recovery_extra | 0.678835 | outputs/s4_digest_retrieval_on_v23/oof_s4_phone_recovery_extra.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_phone_recovery_extra.csv |
| s4_body_recovery_knn_label | 0.691487 | outputs/s4_digest_retrieval_on_v23/oof_s4_body_recovery_knn_label.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_body_recovery_knn_label.csv |
| s4_phone_recovery_proto | 0.694293 | outputs/s4_digest_retrieval_on_v23/oof_s4_phone_recovery_proto.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_phone_recovery_proto.csv |
| s4_body_recovery_proto | 0.694758 | outputs/s4_digest_retrieval_on_v23/oof_s4_body_recovery_proto.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_body_recovery_proto.csv |
| s4_phone_recovery_knn_label | 0.696069 | outputs/s4_digest_retrieval_on_v23/oof_s4_phone_recovery_knn_label.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_phone_recovery_knn_label.csv |
| s4_phone_recovery_knn_logitresid | 0.698796 | outputs/s4_digest_retrieval_on_v23/oof_s4_phone_recovery_knn_logitresid.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_phone_recovery_knn_logitresid.csv |
| s4_social_rhythm_proto | 0.700672 | outputs/s4_digest_retrieval_on_v23/oof_s4_social_rhythm_proto.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_social_rhythm_proto.csv |
| s4_social_rhythm_knn_logitresid | 0.712139 | outputs/s4_digest_retrieval_on_v23/oof_s4_social_rhythm_knn_logitresid.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_social_rhythm_knn_logitresid.csv |
| s4_body_recovery_knn_logitresid | 0.716031 | outputs/s4_digest_retrieval_on_v23/oof_s4_body_recovery_knn_logitresid.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_body_recovery_knn_logitresid.csv |
| s4_social_rhythm_logreg | 0.771160 | outputs/s4_digest_retrieval_on_v23/oof_s4_social_rhythm_logreg.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_social_rhythm_logreg.csv |
| s4_modality_desync_logreg | 0.786740 | outputs/s4_digest_retrieval_on_v23/oof_s4_modality_desync_logreg.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_modality_desync_logreg.csv |
| s4_body_recovery_logreg | 0.806686 | outputs/s4_digest_retrieval_on_v23/oof_s4_body_recovery_logreg.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_body_recovery_logreg.csv |
| s4_phone_recovery_logreg | 0.842683 | outputs/s4_digest_retrieval_on_v23/oof_s4_phone_recovery_logreg.csv | outputs/s4_digest_retrieval_on_v23/submission_s4_phone_recovery_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| phone_recovery | 473 |
| social_rhythm | 638 |
| body_recovery | 840 |
| modality_desync | 1011 |
