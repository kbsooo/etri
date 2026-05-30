# E233 Target-Specific Soft Energy Heads

## Question

Can target-specific support probabilities be used as soft JEPA amplitude/energy heads after E232 rejected one shared support gate?

## Observed Read

- Learned policies promoted to tail audit: `0`.
- Best Q3 overlap with E230 risk-top21 inside learned low-amp top25 rows: `0` rows.

Interpretation rule: a healthy soft head should beat the full target movement in OOF, keep subject stability, and for Q3 should downweight E230's fragile rows without being hand-coded from E230.

## Task Summary

| task | best_learned_delta | best_loss_vs_full | best_subject_win | best_support_auc | promote_count | full_target_delta | full_subject_win_rate | oracle_target_delta | oracle_subject_win_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q3_e224 | -0.002548953 | 0.001713160 | 0.600000000 | 0.622392541 | 0 | -0.004262113 | 0.600000000 | -0.018690502 | 1.000000000 |
| s2_e216 | -0.002769599 | 0.001600825 | 0.700000000 | 0.747494810 | 0 | -0.004370425 | 0.600000000 | -0.026050179 | 1.000000000 |
| s4_e224 | -0.002931629 | 0.000498506 | 0.700000000 | 0.800879648 | 0 | -0.003430136 | 0.700000000 | -0.015019255 | 1.000000000 |

## Best Learned Soft Policies

| task | view | model | split | policy | support_auc | corr_benefit | target_delta | full_target_delta | loss_vs_full | subject_win_rate | mean_amp | promote_to_tail_audit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q3_e224 | movement | lr_l2_c0p10 | stratified5 | soft_center_x2p0 | 0.622392541 | 0.015678729 | -0.002548953 | -0.004262113 | 0.001713160 | 0.600000000 | 0.500313486 | False |
| q3_e224 | movement | lr_l2_c0p10 | stratified5 | soft_center_x1p5 | 0.622392541 | 0.015678729 | -0.002512214 | -0.004262113 | 0.001749899 | 0.600000000 | 0.499719473 | False |
| q3_e224 | movement | lr_l2_c0p10 | stratified5 | soft_prob | 0.622392541 | 0.015678729 | -0.002480983 | -0.004262113 | 0.001781130 | 0.600000000 | 0.499812982 | False |
| q3_e224 | movement | lr_l2_c0p10 | subject5 | soft_prob | 0.602243995 | -0.003439603 | -0.002383525 | -0.004262113 | 0.001878588 | 0.600000000 | 0.503358314 | False |
| q3_e224 | movement | lr_l2_c0p10 | subject5 | soft_center_x1p5 | 0.602243995 | -0.003439603 | -0.002365499 | -0.004262113 | 0.001896614 | 0.600000000 | 0.505037471 | False |
| s2_e216 | movement | hgb_shallow | subject5 | soft_prob | 0.747494810 | -0.008037191 | -0.002769599 | -0.004370425 | 0.001600825 | 0.600000000 | 0.558368693 | False |
| s2_e216 | latent_no_targetid | hgb_shallow | subject5 | soft_prob | 0.673806292 | -0.018047037 | -0.002730139 | -0.004370425 | 0.001640286 | 0.700000000 | 0.561303112 | False |
| s2_e216 | latent_with_targetid | hgb_shallow | subject5 | soft_prob | 0.673806292 | -0.018047037 | -0.002730139 | -0.004370425 | 0.001640286 | 0.700000000 | 0.561303112 | False |
| s2_e216 | movement | hgb_shallow | subject5 | soft_center_x2p0 | 0.747494810 | -0.008037191 | -0.002726906 | -0.004370425 | 0.001643519 | 0.600000000 | 0.586506710 | False |
| s2_e216 | latent_no_targetid | hgb_shallow | subject5 | soft_center_x1p5 | 0.673806292 | -0.018047037 | -0.002687947 | -0.004370425 | 0.001682478 | 0.700000000 | 0.591700488 | False |
| s4_e224 | movement | lr_l2_c0p10 | subject5 | soft_center_x2p0 | 0.800879648 | 0.074996926 | -0.002931629 | -0.003430136 | 0.000498506 | 0.600000000 | 0.394043279 | False |
| s4_e224 | movement | lr_l2_c0p10 | subject5 | soft_center_x1p5 | 0.800879648 | 0.074996926 | -0.002902385 | -0.003430136 | 0.000527751 | 0.600000000 | 0.410577323 | False |
| s4_e224 | latent_with_targetid | lr_l2_c0p10 | stratified5 | soft_center_x1p5 | 0.773165734 | 0.078780303 | -0.002812871 | -0.003430136 | 0.000617264 | 0.700000000 | 0.353253014 | False |
| s4_e224 | latent_no_targetid | lr_l2_c0p10 | stratified5 | soft_center_x1p5 | 0.773165734 | 0.078780303 | -0.002812871 | -0.003430136 | 0.000617264 | 0.700000000 | 0.353253014 | False |
| s4_e224 | latent_no_targetid | lr_l2_c0p10 | stratified5 | soft_center_x2p0 | 0.773165734 | 0.078780303 | -0.002774597 | -0.003430136 | 0.000655538 | 0.700000000 | 0.351226397 | False |

## Selected Test Alignment Probes

| task | view | model | policy | sub_mean_prob | sub_mean_amp | sub_p10_amp | sub_p50_amp | sub_p90_amp | e230_q3_risk_top21_low13_overlap | e230_q3_risk_top21_low13_jaccard | e230_q3_risk_top21_low21_overlap | e230_q3_risk_top21_low21_jaccard | e230_q3_risk_top21_low25_overlap | e230_q3_risk_top21_low25_jaccard | e230_q3_risk_top21_low50_overlap | e230_q3_risk_top21_low50_jaccard | e230_q3_swing_top25_low13_overlap | e230_q3_swing_top25_low13_jaccard | e230_q3_swing_top25_low21_overlap | e230_q3_swing_top25_low21_jaccard | e230_q3_swing_top25_low25_overlap | e230_q3_swing_top25_low25_jaccard | e230_q3_swing_top25_low50_overlap | e230_q3_swing_top25_low50_jaccard | e230_q3_expected_positive_low13_overlap | e230_q3_expected_positive_low13_jaccard | e230_q3_expected_positive_low21_overlap | e230_q3_expected_positive_low21_jaccard | e230_q3_expected_positive_low25_overlap | e230_q3_expected_positive_low25_jaccard | e230_q3_expected_positive_low50_overlap | e230_q3_expected_positive_low50_jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q3_e224 | movement | lr_l2_c0p10 | soft_center_x2p0 | 0.574291561 | 0.648109999 | 0.362169209 | 0.639440956 | 0.941095712 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 2.000000000 | 0.028985507 | 0.000000000 | 0.000000000 | 1.000000000 | 0.022222222 | 1.000000000 | 0.020408163 | 3.000000000 | 0.041666667 | 2.000000000 | 0.016393443 | 3.000000000 | 0.023255814 | 4.000000000 | 0.030303030 | 14.000000000 | 0.095238095 |
| q3_e224 | movement | lr_l2_c0p10 | soft_center_x1p5 | 0.574291561 | 0.611437341 | 0.396626907 | 0.604580717 | 0.830821784 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 2.000000000 | 0.028985507 | 0.000000000 | 0.000000000 | 1.000000000 | 0.022222222 | 1.000000000 | 0.020408163 | 3.000000000 | 0.041666667 | 2.000000000 | 0.016393443 | 3.000000000 | 0.023255814 | 4.000000000 | 0.030303030 | 14.000000000 | 0.095238095 |
| q3_e224 | movement | lr_l2_c0p10 | soft_prob | 0.574291561 | 0.574291561 | 0.431084605 | 0.569720478 | 0.720547856 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 2.000000000 | 0.028985507 | 0.000000000 | 0.000000000 | 1.000000000 | 0.022222222 | 1.000000000 | 0.020408163 | 3.000000000 | 0.041666667 | 2.000000000 | 0.016393443 | 3.000000000 | 0.023255814 | 4.000000000 | 0.030303030 | 14.000000000 | 0.095238095 |
| s2_e216 | movement | hgb_shallow | soft_prob | 0.522782472 | 0.522782472 | 0.206875128 | 0.559921112 | 0.896937898 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| s2_e216 | latent_no_targetid | hgb_shallow | soft_prob | 0.541137512 | 0.541137512 | 0.288271729 | 0.539996490 | 0.783434373 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| s2_e216 | latent_with_targetid | hgb_shallow | soft_prob | 0.541137512 | 0.541137512 | 0.288271729 | 0.539996490 | 0.783434373 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| s4_e224 | movement | lr_l2_c0p10 | soft_center_x2p0 | 0.275126834 | 0.204008470 | 0.000000000 | 0.000000000 | 0.765595812 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| s4_e224 | movement | lr_l2_c0p10 | soft_center_x1p5 | 0.275126834 | 0.201692657 | 0.000000000 | 0.000000000 | 0.699196859 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| s4_e224 | latent_with_targetid | lr_l2_c0p10 | soft_center_x1p5 | 0.269890834 | 0.233177821 | 0.000000000 | 0.000000000 | 0.934236238 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

## Decision

- No learned soft support-energy policy beat the full movement while preserving signal and subject stability.
- This blocks the cheap target-specific support-head rescue. The next JEPA step should change the target representation/loss, not only soften the existing support classifiers.
