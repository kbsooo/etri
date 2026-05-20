# S2 sleep/missingness retrieval encoder

- Base S2 OOF: `0.509835`
- Best source S2 OOF: `0.540370`

## Sources

| name | S2_log_loss | oof | submission |
| --- | --- | --- | --- |
| s2_volatility_shift_knn_resid | 0.540370 | outputs/s2_special_retrieval_on_v20/oof_s2_volatility_shift_knn_resid.csv | outputs/s2_special_retrieval_on_v20/submission_s2_volatility_shift_knn_resid.csv |
| s2_social_environment_knn_resid | 0.584736 | outputs/s2_special_retrieval_on_v20/oof_s2_social_environment_knn_resid.csv | outputs/s2_special_retrieval_on_v20/submission_s2_social_environment_knn_resid.csv |
| s2_social_environment_knn_label | 0.597993 | outputs/s2_special_retrieval_on_v20/oof_s2_social_environment_knn_label.csv | outputs/s2_special_retrieval_on_v20/submission_s2_social_environment_knn_label.csv |
| s2_sleep_retrieval_meta | 0.600183 | outputs/s2_special_retrieval_on_v20/oof_s2_sleep_retrieval_meta.csv | outputs/s2_special_retrieval_on_v20/submission_s2_sleep_retrieval_meta.csv |
| s2_circadian_disruption_knn_resid | 0.601455 | outputs/s2_special_retrieval_on_v20/oof_s2_circadian_disruption_knn_resid.csv | outputs/s2_special_retrieval_on_v20/submission_s2_circadian_disruption_knn_resid.csv |
| s2_social_environment_extra | 0.615962 | outputs/s2_special_retrieval_on_v20/oof_s2_social_environment_extra.csv | outputs/s2_special_retrieval_on_v20/submission_s2_social_environment_extra.csv |
| s2_social_environment_knn_logitresid | 0.616413 | outputs/s2_special_retrieval_on_v20/oof_s2_social_environment_knn_logitresid.csv | outputs/s2_special_retrieval_on_v20/submission_s2_social_environment_knn_logitresid.csv |
| s2_volatility_shift_extra | 0.618684 | outputs/s2_special_retrieval_on_v20/oof_s2_volatility_shift_extra.csv | outputs/s2_special_retrieval_on_v20/submission_s2_volatility_shift_extra.csv |
| s2_social_environment_proto | 0.618835 | outputs/s2_special_retrieval_on_v20/oof_s2_social_environment_proto.csv | outputs/s2_special_retrieval_on_v20/submission_s2_social_environment_proto.csv |
| s2_q1_s2_residual_extra | 0.620108 | outputs/s2_special_retrieval_on_v20/oof_s2_q1_s2_residual_extra.csv | outputs/s2_special_retrieval_on_v20/submission_s2_q1_s2_residual_extra.csv |
| s2_social_environment_hgb | 0.621550 | outputs/s2_special_retrieval_on_v20/oof_s2_social_environment_hgb.csv | outputs/s2_special_retrieval_on_v20/submission_s2_social_environment_hgb.csv |
| s2_q1_s2_residual_proto | 0.623391 | outputs/s2_special_retrieval_on_v20/oof_s2_q1_s2_residual_proto.csv | outputs/s2_special_retrieval_on_v20/submission_s2_q1_s2_residual_proto.csv |
| s2_volatility_shift_hgb | 0.624230 | outputs/s2_special_retrieval_on_v20/oof_s2_volatility_shift_hgb.csv | outputs/s2_special_retrieval_on_v20/submission_s2_volatility_shift_hgb.csv |
| s2_q1_s2_residual_knn_resid | 0.629624 | outputs/s2_special_retrieval_on_v20/oof_s2_q1_s2_residual_knn_resid.csv | outputs/s2_special_retrieval_on_v20/submission_s2_q1_s2_residual_knn_resid.csv |
| s2_volatility_shift_knn_logitresid | 0.632691 | outputs/s2_special_retrieval_on_v20/oof_s2_volatility_shift_knn_logitresid.csv | outputs/s2_special_retrieval_on_v20/submission_s2_volatility_shift_knn_logitresid.csv |
| s2_circadian_disruption_hgb | 0.632812 | outputs/s2_special_retrieval_on_v20/oof_s2_circadian_disruption_hgb.csv | outputs/s2_special_retrieval_on_v20/submission_s2_circadian_disruption_hgb.csv |
| s2_q1_s2_residual_hgb | 0.637210 | outputs/s2_special_retrieval_on_v20/oof_s2_q1_s2_residual_hgb.csv | outputs/s2_special_retrieval_on_v20/submission_s2_q1_s2_residual_hgb.csv |
| s2_circadian_disruption_extra | 0.642444 | outputs/s2_special_retrieval_on_v20/oof_s2_circadian_disruption_extra.csv | outputs/s2_special_retrieval_on_v20/submission_s2_circadian_disruption_extra.csv |
| s2_volatility_shift_knn_label | 0.644073 | outputs/s2_special_retrieval_on_v20/oof_s2_volatility_shift_knn_label.csv | outputs/s2_special_retrieval_on_v20/submission_s2_volatility_shift_knn_label.csv |
| s2_circadian_disruption_knn_label | 0.644097 | outputs/s2_special_retrieval_on_v20/oof_s2_circadian_disruption_knn_label.csv | outputs/s2_special_retrieval_on_v20/submission_s2_circadian_disruption_knn_label.csv |
| s2_volatility_shift_proto | 0.644466 | outputs/s2_special_retrieval_on_v20/oof_s2_volatility_shift_proto.csv | outputs/s2_special_retrieval_on_v20/submission_s2_volatility_shift_proto.csv |
| s2_q1_s2_residual_knn_label | 0.647382 | outputs/s2_special_retrieval_on_v20/oof_s2_q1_s2_residual_knn_label.csv | outputs/s2_special_retrieval_on_v20/submission_s2_q1_s2_residual_knn_label.csv |
| s2_circadian_disruption_proto | 0.665634 | outputs/s2_special_retrieval_on_v20/oof_s2_circadian_disruption_proto.csv | outputs/s2_special_retrieval_on_v20/submission_s2_circadian_disruption_proto.csv |
| s2_circadian_disruption_knn_logitresid | 0.670418 | outputs/s2_special_retrieval_on_v20/oof_s2_circadian_disruption_knn_logitresid.csv | outputs/s2_special_retrieval_on_v20/submission_s2_circadian_disruption_knn_logitresid.csv |
| s2_q1_s2_residual_knn_logitresid | 0.686694 | outputs/s2_special_retrieval_on_v20/oof_s2_q1_s2_residual_knn_logitresid.csv | outputs/s2_special_retrieval_on_v20/submission_s2_q1_s2_residual_knn_logitresid.csv |
| s2_volatility_shift_logreg | 0.735414 | outputs/s2_special_retrieval_on_v20/oof_s2_volatility_shift_logreg.csv | outputs/s2_special_retrieval_on_v20/submission_s2_volatility_shift_logreg.csv |
| s2_social_environment_logreg | 0.744835 | outputs/s2_special_retrieval_on_v20/oof_s2_social_environment_logreg.csv | outputs/s2_special_retrieval_on_v20/submission_s2_social_environment_logreg.csv |
| s2_q1_s2_residual_logreg | 0.761014 | outputs/s2_special_retrieval_on_v20/oof_s2_q1_s2_residual_logreg.csv | outputs/s2_special_retrieval_on_v20/submission_s2_q1_s2_residual_logreg.csv |
| s2_circadian_disruption_logreg | 0.764389 | outputs/s2_special_retrieval_on_v20/oof_s2_circadian_disruption_logreg.csv | outputs/s2_special_retrieval_on_v20/submission_s2_circadian_disruption_logreg.csv |

## Feature Groups

| group | n_features |
| --- | --- |
| volatility_shift | 906 |
| circadian_disruption | 652 |
| social_environment | 867 |
| q1_s2_residual | 1596 |
