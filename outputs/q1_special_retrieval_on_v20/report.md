# Q1 sleep/missingness retrieval encoder

- Base Q1 OOF: `0.604281`
- Best source Q1 OOF: `0.634565`

## Sources

| name | Q1_log_loss | oof | submission |
| --- | --- | --- | --- |
| q1_sleep_retrieval_meta | 0.634565 | outputs/q1_special_retrieval_on_v20/oof_q1_sleep_retrieval_meta.csv | outputs/q1_special_retrieval_on_v20/submission_q1_sleep_retrieval_meta.csv |
| q1_social_environment_proto | 0.653352 | outputs/q1_special_retrieval_on_v20/oof_q1_social_environment_proto.csv | outputs/q1_special_retrieval_on_v20/submission_q1_social_environment_proto.csv |
| q1_circadian_disruption_knn_resid | 0.657959 | outputs/q1_special_retrieval_on_v20/oof_q1_circadian_disruption_knn_resid.csv | outputs/q1_special_retrieval_on_v20/submission_q1_circadian_disruption_knn_resid.csv |
| q1_q1_s2_residual_extra | 0.669623 | outputs/q1_special_retrieval_on_v20/oof_q1_q1_s2_residual_extra.csv | outputs/q1_special_retrieval_on_v20/submission_q1_q1_s2_residual_extra.csv |
| q1_circadian_disruption_extra | 0.670925 | outputs/q1_special_retrieval_on_v20/oof_q1_circadian_disruption_extra.csv | outputs/q1_special_retrieval_on_v20/submission_q1_circadian_disruption_extra.csv |
| q1_social_environment_extra | 0.671257 | outputs/q1_special_retrieval_on_v20/oof_q1_social_environment_extra.csv | outputs/q1_special_retrieval_on_v20/submission_q1_social_environment_extra.csv |
| q1_volatility_shift_extra | 0.679041 | outputs/q1_special_retrieval_on_v20/oof_q1_volatility_shift_extra.csv | outputs/q1_special_retrieval_on_v20/submission_q1_volatility_shift_extra.csv |
| q1_q1_s2_residual_knn_label | 0.679983 | outputs/q1_special_retrieval_on_v20/oof_q1_q1_s2_residual_knn_label.csv | outputs/q1_special_retrieval_on_v20/submission_q1_q1_s2_residual_knn_label.csv |
| q1_social_environment_knn_label | 0.682866 | outputs/q1_special_retrieval_on_v20/oof_q1_social_environment_knn_label.csv | outputs/q1_special_retrieval_on_v20/submission_q1_social_environment_knn_label.csv |
| q1_social_environment_hgb | 0.687925 | outputs/q1_special_retrieval_on_v20/oof_q1_social_environment_hgb.csv | outputs/q1_special_retrieval_on_v20/submission_q1_social_environment_hgb.csv |
| q1_social_environment_logreg | 0.688189 | outputs/q1_special_retrieval_on_v20/oof_q1_social_environment_logreg.csv | outputs/q1_special_retrieval_on_v20/submission_q1_social_environment_logreg.csv |
| q1_social_environment_knn_resid | 0.689142 | outputs/q1_special_retrieval_on_v20/oof_q1_social_environment_knn_resid.csv | outputs/q1_special_retrieval_on_v20/submission_q1_social_environment_knn_resid.csv |
| q1_q1_s2_residual_hgb | 0.689703 | outputs/q1_special_retrieval_on_v20/oof_q1_q1_s2_residual_hgb.csv | outputs/q1_special_retrieval_on_v20/submission_q1_q1_s2_residual_hgb.csv |
| q1_q1_s2_residual_proto | 0.696011 | outputs/q1_special_retrieval_on_v20/oof_q1_q1_s2_residual_proto.csv | outputs/q1_special_retrieval_on_v20/submission_q1_q1_s2_residual_proto.csv |
| q1_q1_s2_residual_knn_resid | 0.698125 | outputs/q1_special_retrieval_on_v20/oof_q1_q1_s2_residual_knn_resid.csv | outputs/q1_special_retrieval_on_v20/submission_q1_q1_s2_residual_knn_resid.csv |
| q1_volatility_shift_hgb | 0.703137 | outputs/q1_special_retrieval_on_v20/oof_q1_volatility_shift_hgb.csv | outputs/q1_special_retrieval_on_v20/submission_q1_volatility_shift_hgb.csv |
| q1_circadian_disruption_knn_label | 0.707107 | outputs/q1_special_retrieval_on_v20/oof_q1_circadian_disruption_knn_label.csv | outputs/q1_special_retrieval_on_v20/submission_q1_circadian_disruption_knn_label.csv |
| q1_volatility_shift_knn_resid | 0.708707 | outputs/q1_special_retrieval_on_v20/oof_q1_volatility_shift_knn_resid.csv | outputs/q1_special_retrieval_on_v20/submission_q1_volatility_shift_knn_resid.csv |
| q1_volatility_shift_proto | 0.712561 | outputs/q1_special_retrieval_on_v20/oof_q1_volatility_shift_proto.csv | outputs/q1_special_retrieval_on_v20/submission_q1_volatility_shift_proto.csv |
| q1_q1_s2_residual_logreg | 0.721646 | outputs/q1_special_retrieval_on_v20/oof_q1_q1_s2_residual_logreg.csv | outputs/q1_special_retrieval_on_v20/submission_q1_q1_s2_residual_logreg.csv |
| q1_volatility_shift_knn_label | 0.724206 | outputs/q1_special_retrieval_on_v20/oof_q1_volatility_shift_knn_label.csv | outputs/q1_special_retrieval_on_v20/submission_q1_volatility_shift_knn_label.csv |
| q1_circadian_disruption_hgb | 0.729691 | outputs/q1_special_retrieval_on_v20/oof_q1_circadian_disruption_hgb.csv | outputs/q1_special_retrieval_on_v20/submission_q1_circadian_disruption_hgb.csv |
| q1_circadian_disruption_knn_logitresid | 0.746537 | outputs/q1_special_retrieval_on_v20/oof_q1_circadian_disruption_knn_logitresid.csv | outputs/q1_special_retrieval_on_v20/submission_q1_circadian_disruption_knn_logitresid.csv |
| q1_circadian_disruption_proto | 0.756386 | outputs/q1_special_retrieval_on_v20/oof_q1_circadian_disruption_proto.csv | outputs/q1_special_retrieval_on_v20/submission_q1_circadian_disruption_proto.csv |
| q1_volatility_shift_logreg | 0.757493 | outputs/q1_special_retrieval_on_v20/oof_q1_volatility_shift_logreg.csv | outputs/q1_special_retrieval_on_v20/submission_q1_volatility_shift_logreg.csv |
| q1_social_environment_knn_logitresid | 0.767395 | outputs/q1_special_retrieval_on_v20/oof_q1_social_environment_knn_logitresid.csv | outputs/q1_special_retrieval_on_v20/submission_q1_social_environment_knn_logitresid.csv |
| q1_volatility_shift_knn_logitresid | 0.776057 | outputs/q1_special_retrieval_on_v20/oof_q1_volatility_shift_knn_logitresid.csv | outputs/q1_special_retrieval_on_v20/submission_q1_volatility_shift_knn_logitresid.csv |
| q1_q1_s2_residual_knn_logitresid | 0.780596 | outputs/q1_special_retrieval_on_v20/oof_q1_q1_s2_residual_knn_logitresid.csv | outputs/q1_special_retrieval_on_v20/submission_q1_q1_s2_residual_knn_logitresid.csv |
| q1_circadian_disruption_logreg | 0.908431 | outputs/q1_special_retrieval_on_v20/oof_q1_circadian_disruption_logreg.csv | outputs/q1_special_retrieval_on_v20/submission_q1_circadian_disruption_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| volatility_shift | 906 |
| circadian_disruption | 652 |
| social_environment | 867 |
| q1_s2_residual | 1596 |
