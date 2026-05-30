# E304 Hidden Block-State JEPA Probe

Public LB는 사용하지 않았다. 목표는 raw human diary context에서 hidden subject/dateblock target state가 복원되는지 확인하는 것이다.

## Question

S4 mask-surgery가 실패한 이유가 placement 문제라면, 좋은 placement는 subject/dateblock 단위의 Q/S residual state로 먼저 복원되어야 한다. E304는 context=생활로그 diary block, target=subject prior를 제거한 block target-rate representation으로 둔 JEPA-style 실험이다.

## Summary

| view_id | split | mean_spearman | mean_mae | mean_r2 | mean_sign_hit_rate | positive_spearman_targets | S4_spearman | S4_mae | S4_sign_hit_rate | null_mean_spearman_median | null_mean_spearman_p90 | null_dominance | representation_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| family_jepa | subject_holdout | 0.143141 | 0.629558 | -0.860568 | 0.553156 | 7 | 0.124633 | 0.543668 | 0.558140 | -0.009295 | 0.060745 | 0.986111 | True |
| story_episode | subject_holdout | 0.083326 | 0.526046 | -0.171127 | 0.538206 | 6 | 0.108933 | 0.508302 | 0.546512 | -0.026925 | 0.051120 | 0.958333 | True |
| story_episode | block_random5 | 0.050014 | 0.543035 | -0.223110 | 0.528239 | 5 | 0.024844 | 0.530962 | 0.511628 | -0.014527 | 0.062724 | 0.875000 | True |
| calendar | subject_holdout | 0.047842 | 0.504932 | -0.038184 | 0.526578 | 5 | 0.001604 | 0.507239 | 0.488372 | -0.013421 | 0.055076 | 0.875000 | False |
| family_jepa | block_random5 | -0.009150 | 0.565567 | -0.361557 | 0.503322 | 3 | -0.113009 | 0.580268 | 0.476744 | -0.056534 | 0.018925 | 0.750000 | False |
| human_full | subject_holdout | 0.049098 | 24.650085 | -35596.404781 | 0.513289 | 4 | 0.177604 | 18.401602 | 0.534884 | 0.001166 | 0.073099 | 0.736111 | False |
| calendar | block_random5 | -0.037531 | 0.514063 | -0.088886 | 0.490033 | 3 | -0.276988 | 0.539627 | 0.430233 | -0.068566 | 0.002298 | 0.736111 | False |
| human_full | block_random5 | -0.042529 | 0.642270 | -0.793782 | 0.470100 | 3 | -0.136635 | 0.639667 | 0.476744 | -0.057934 | 0.015239 | 0.652778 | False |
| raw_top120 | subject_holdout | -0.058506 | 36.280592 | -77871.445899 | 0.465116 | 3 | 0.110725 | 45.298332 | 0.476744 | -0.005670 | 0.061682 | 0.138889 | False |
| raw_top120 | block_random5 | -0.147760 | 0.692709 | -1.154297 | 0.446844 | 1 | -0.094827 | 0.646673 | 0.430233 | -0.053180 | 0.017984 | 0.069444 | False |

## S4 Target Metrics

| view_id | split | target | spearman | mae | r2 | sign_hit_rate | target_std |
| --- | --- | --- | --- | --- | --- | --- | --- |
| human_full | subject_holdout | S4 | 0.177604 | 18.401602 | -12815.037643 | 0.534884 | 0.600683 |
| family_jepa | subject_holdout | S4 | 0.124633 | 0.543668 | -0.237314 | 0.558140 | 0.600683 |
| raw_top120 | subject_holdout | S4 | 0.110725 | 45.298332 | -80324.929984 | 0.476744 | 0.600683 |
| story_episode | subject_holdout | S4 | 0.108933 | 0.508302 | -0.109333 | 0.546512 | 0.600683 |
| story_episode | block_random5 | S4 | 0.024844 | 0.530962 | -0.217882 | 0.511628 | 0.600683 |
| calendar | subject_holdout | S4 | 0.001604 | 0.507239 | -0.051216 | 0.488372 | 0.600683 |
| raw_top120 | block_random5 | S4 | -0.094827 | 0.646673 | -0.679962 | 0.430233 | 0.600683 |
| family_jepa | block_random5 | S4 | -0.113009 | 0.580268 | -0.519072 | 0.476744 | 0.600683 |
| human_full | block_random5 | S4 | -0.136635 | 0.639667 | -0.706310 | 0.476744 | 0.600683 |
| calendar | block_random5 | S4 | -0.276988 | 0.539627 | -0.195337 | 0.430233 | 0.600683 |

## Candidate Alignment With Predicted S4 Block State

| source | path | n_active_blocks | n_active_rows | signed_alignment_spearman | abs_alignment_spearman | active_pred_S4_mean | inactive_pred_S4_mean | active_minus_inactive_pred_S4 | id07_b9_pred_S4 | id07_b9_s4_signed_sum |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E300_ready_rejected | analysis_outputs/submission_e300_s4mean_drop_dateblock_id07_b9_raw_m1p16_d285ff4a.csv | 17 | 47 | -0.027759 | -0.122670 | -0.120389 | 0.003428 | -0.123817 | -0.415169 | 0.000000 |
| E299_parent | analysis_outputs/submission_e299_bridge_visible_low_null_near_e292_contrastlife_S4_family_jepa_context_dateblock5_cluste_m0p970_66cc85cf.csv | 18 | 50 | -0.080016 | -0.070847 | -0.136765 | 0.014742 | -0.151507 | -0.415169 | 0.116400 |
| E303_best_rejected | analysis_outputs/submission_e303_s4meanprior_drop_prior_bestdrop12_raw_m1p16_bd3f44a6.csv | 15 | 38 | -0.215301 | -0.174006 | -0.150330 | 0.008465 | -0.158795 | -0.415169 | 0.135024 |

## Top Positive Predicted S4 Blocks

| dateblock_group | subject_id | sleep_start | sleep_end | pred_S4_logit_residual | pred_Q3_logit_residual | top_human_story_scores |
| --- | --- | --- | --- | --- | --- | --- |
| id05_b3 | id05 | 2024-09-29 | 2024-09-30 | 0.827748 | -0.140376 | story__weekend_ritual_rest:0.98; episode__home_recovery:0.76; episode__routine_anchor_recovery:0.73 |
| id06_b4 | id06 | 2024-07-07 | 2024-07-11 | 0.745619 | 0.120033 | story__paymonth_start_post7_spend_outing:2.25; story__monthstart_spending_reset:1.47; episode__cashflow_stress:1.32 |
| id06_b8 | id06 | 2024-08-10 | 2024-08-14 | 0.593789 | 0.592808 | episode__routine_fragmentation:1.20; story__vehicle_noise_day:1.16; episode__cashflow_stress:1.11 |
| id06_b10 | id06 | 2024-08-24 | 2024-08-25 | 0.417140 | 0.432696 | story__pay25_pre3_cash_stress:6.00; story__pay20_post3_relief_home:3.21; episode__bedtime_arousal:1.40 |
| id07_b4 | id07 | 2024-07-14 | 2024-07-15 | 0.388831 | -0.282807 | story__weekend_ritual_rest:1.11; episode__cashflow_stress:1.10; story__deepnight_phone_awake:0.84 |
| id08_b5 | id08 | 2024-08-06 | 2024-08-11 | 0.386747 | -0.869624 | story__paymonth_start_post7_spend_outing:2.75; story__monthstart_spending_reset:1.86; story__pay20_post3_relief_home:1.15 |
| id10_b3 | id10 | 2024-08-05 | 2024-08-14 | 0.352125 | -0.346187 | story__pay25_pre3_cash_stress:3.53; story__paymonth_start_post7_spend_outing:2.19; story__pay20_post3_relief_home:1.75 |
| id04_b7 | id04 | 2024-09-26 | 2024-09-27 | 0.308877 | 0.462683 | story__paymonth_start_post7_spend_outing:2.24; story__monthstart_spending_reset:1.00; story__screen_fragmentation:0.84 |
| id04_b6 | id04 | 2024-09-19 | 2024-09-25 | 0.270107 | 0.122875 | story__pay25_pre3_cash_stress:3.10; story__pay20_post3_relief_home:2.78; story__paymonth_start_post7_spend_outing:2.24 |
| id05_b4 | id05 | 2024-10-01 | 2024-10-11 | 0.225167 | 0.241102 | story__paymonth_start_post7_spend_outing:3.49; story__paymonth_start_post3_late_shopping:2.43; story__payeom_post3_late_shopping:2.31 |
| id06_b6 | id06 | 2024-07-19 | 2024-07-21 | 0.196112 | -0.162448 | episode__cashflow_stress:1.47; story__bright_light_late:0.69; story__paymonth_start_post7_spend_outing:0.66 |
| id01_b7 | id01 | 2024-09-02 | 2024-09-02 | 0.187580 | 0.105065 | story__payeom_post3_late_shopping:6.00; story__paymonth_start_post3_late_shopping:6.00; story__paymonth_start_post7_spend_outing:4.30 |

## Top Negative Predicted S4 Blocks

| dateblock_group | subject_id | sleep_start | sleep_end | pred_S4_logit_residual | pred_Q3_logit_residual | top_human_story_scores |
| --- | --- | --- | --- | --- | --- | --- |
| id05_b7 | id05 | 2024-11-07 | 2024-11-08 | -0.657206 | -0.694941 | story__paymonth_start_post7_spend_outing:5.27; story__monthstart_spending_reset:3.25; episode__measurement_wear_confidence:1.76 |
| id10_b7 | id10 | 2024-09-21 | 2024-09-27 | -0.557041 | -0.014285 | story__pay25_pre3_cash_stress:4.35; story__pay20_post3_relief_home:1.88; story__vehicle_noise_day:0.72 |
| id04_b11 | id04 | 2024-10-24 | 2024-10-30 | -0.459066 | 0.001199 | story__paymonth_start_post7_spend_outing:2.24; story__pay25_pre3_cash_stress:2.13; story__monthstart_spending_reset:1.00 |
| id07_b9 | id07 | 2024-08-15 | 2024-08-21 | -0.415169 | -0.051183 | story__pay20_post3_relief_home:1.31; episode__cashflow_stress:0.60; story__vehicle_noise_day:0.36 |
| id04_b9 | id04 | 2024-10-15 | 2024-10-16 | -0.410806 | -0.378109 | story__paymonth_start_post7_spend_outing:2.24; story__monthstart_spending_reset:1.00; episode__physiology_strain:0.63 |
| id03_b3 | id03 | 2024-08-17 | 2024-08-23 | -0.374469 | -0.066878 | story__pay20_post3_relief_home:2.00; episode__cashflow_stress:1.29; episode__social_overload:0.91 |
| id03_b4 | id03 | 2024-08-24 | 2024-08-29 | -0.361092 | -0.068230 | story__pay25_pre3_cash_stress:1.91; story__pay20_post3_relief_home:1.20; story__single_app_monotony:0.78 |
| id02_b10 | id02 | 2024-10-06 | 2024-10-13 | -0.327881 | 0.327950 | story__paymonth_start_post3_late_shopping:2.15; story__payeom_post3_late_shopping:1.23; story__deepnight_phone_awake:0.54 |
| id01_b5 | id01 | 2024-08-09 | 2024-08-17 | -0.327239 | 0.045576 | episode__physiology_strain:1.21; story__heart_stress_late:1.20; story__single_app_monotony:1.16 |
| id09_b9 | id09 | 2024-09-16 | 2024-09-22 | -0.312963 | -0.421436 | story__pay20_post3_relief_home:1.93; story__pay25_pre3_cash_stress:1.18; story__media_binge_late:1.13 |
| id01_b4 | id01 | 2024-07-31 | 2024-08-07 | -0.302036 | -0.006817 | story__payeom_post3_late_shopping:3.46; story__paymonth_start_post7_spend_outing:3.08; story__paymonth_start_post3_late_shopping:2.90 |
| id05_b9 | id05 | 2024-11-19 | 2024-11-20 | -0.266317 | 0.244668 | episode__cashflow_stress:2.44; story__night_out_mobility:1.16; story__ritual_anchor:1.03 |

## Decision

- At least one block-state representation passes the null dominance gate.
- This is not a submission by itself. The next step would be a tiny block-prior materializer with E301-style large-null confirmation.
- Best deployment view for test block annotation: `family_jepa/subject_holdout`.
- Candidate alignment columns should be read as diagnostics only. Positive alignment would support a placement story; weak or negative alignment explains why S4 mask edits fail matched nulls.

## Outputs

- `analysis_outputs/e304_hidden_block_state_summary.csv`
- `analysis_outputs/e304_hidden_block_state_target_metrics.csv`
- `analysis_outputs/e304_hidden_block_state_nulls.csv`
- `analysis_outputs/e304_hidden_block_state_test_blocks.csv`
- `analysis_outputs/e304_hidden_block_state_alignment.csv`
- `analysis_outputs/e304_hidden_block_state_report.md`
