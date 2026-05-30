# E296 Episode Target Strict Null Audit

## Question

Do the E295 human episode-target wins survive a stricter public-free matched-null audit?

## Settings

- Null reps per mode: `64`
- Modes: row, subject, dateblock
- Selection: E295 multi-view/split consensus pairs plus large single-view all-null wins
- Public LB: not used

## Pair Gates

| episode | target | instances | strict_instances | robust_instances | best_delta | mean_delta | best_p_value | worst_min_mode_dominance | mean_margin_q05 | best_state_corr | pair_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bedtime_arousal | S1 | 2 | 2 | 1 | -0.017000 | -0.011958 | 0.010363 | 0.906250 | 0.005434 | 0.729085 | True |
| bedtime_arousal | S3 | 1 | 1 | 1 | -0.016376 | -0.016376 | 0.010363 | 0.984375 | 0.007563 | 0.584732 | True |

## Top Candidate Instances

| candidate_id | view_id | split | episode | target | delta_logloss | null_q01 | null_q05 | null_best | dominance | min_mode_dominance | p_value_lower | strict_gate | robust_gate | state_corr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e296_009 | hybrid_context | subject5 | bedtime_arousal | S3 | -0.016376 | -0.014663 | -0.008813 | -0.016839 | 0.994792 | 0.984375 | 0.010363 | True | True | 0.584732 |
| e296_025 | raw_human_context | dateblock5 | routine_fragmentation | S1 | -0.009804 | -0.004737 | -0.002576 | -0.011243 | 0.994792 | 0.984375 | 0.010363 | True | True | 0.340042 |
| e296_021 | family_jepa_context | subject5 | routine_anchor_recovery | S2 | -0.009187 | -0.008294 | -0.005565 | -0.009475 | 0.994792 | 0.984375 | 0.010363 | True | True | 0.327976 |
| e296_028 | hybrid_context | subject5 | routine_fragmentation | S3 | -0.007785 | -0.006925 | -0.004306 | -0.009584 | 0.994792 | 0.984375 | 0.010363 | True | True | 0.442913 |
| e296_007 | raw_human_context | dateblock5 | bedtime_arousal | S1 | -0.006915 | -0.005113 | -0.001896 | -0.007591 | 0.994792 | 0.984375 | 0.010363 | True | True | 0.729085 |
| e296_014 | raw_human_context | subject5 | cashflow_stress | S1 | -0.017244 | -0.022117 | -0.016007 | -0.029319 | 0.958333 | 0.937500 | 0.046632 | True | False | 0.298140 |
| e296_008 | raw_human_context | subject5 | bedtime_arousal | S1 | -0.017000 | -0.021306 | -0.011150 | -0.026045 | 0.968750 | 0.906250 | 0.036269 | True | False | 0.532194 |
| e296_013 | hybrid_context | subject5 | cashflow_stress | S1 | -0.013144 | -0.012901 | -0.008268 | -0.015989 | 0.989583 | 0.968750 | 0.015544 | True | False | 0.537775 |
| e296_016 | hybrid_context | dateblock5 | home_recovery | S3 | -0.009509 | -0.008532 | -0.003634 | -0.010501 | 0.989583 | 0.984375 | 0.015544 | True | False | 0.419068 |
| e296_017 | hybrid_context | subject5 | home_recovery | S3 | -0.009217 | -0.012098 | -0.008992 | -0.015426 | 0.953125 | 0.906250 | 0.051813 | True | False | 0.336032 |
| e296_012 | hybrid_context | dateblock5 | cashflow_stress | S1 | -0.007484 | -0.005759 | -0.002246 | -0.010895 | 0.989583 | 0.968750 | 0.015544 | True | False | 0.578043 |
| e296_023 | hybrid_context | dateblock5 | routine_anchor_recovery | S3 | -0.004538 | -0.004864 | -0.002658 | -0.008553 | 0.979167 | 0.968750 | 0.025907 | True | False | 0.638318 |
| e296_027 | hybrid_context | dateblock5 | routine_fragmentation | S3 | -0.004319 | -0.004849 | -0.002713 | -0.007872 | 0.973958 | 0.937500 | 0.031088 | True | False | 0.555281 |
| e296_030 | hybrid_context | dateblock5 | social_overload | S3 | -0.004202 | -0.008994 | -0.004028 | -0.013040 | 0.953125 | 0.875000 | 0.051813 | True | False | 0.804829 |
| e296_015 | family_jepa_context | dateblock5 | home_recovery | S3 | -0.004116 | -0.008200 | -0.002568 | -0.011074 | 0.973958 | 0.937500 | 0.031088 | True | False | 0.487861 |
| e296_029 | family_jepa_context | dateblock5 | social_overload | S3 | -0.004046 | -0.007054 | -0.003287 | -0.009981 | 0.958333 | 0.906250 | 0.046632 | True | False | 0.789346 |
| e296_024 | hybrid_context | subject5 | routine_anchor_recovery | S3 | -0.003611 | -0.005927 | -0.003089 | -0.008878 | 0.963542 | 0.953125 | 0.041451 | True | False | 0.454773 |
| e296_022 | hybrid_context | dateblock5 | routine_anchor_recovery | S2 | -0.003513 | -0.006028 | -0.003355 | -0.007527 | 0.953125 | 0.875000 | 0.051813 | True | False | 0.638318 |
| e296_010 | hybrid_context | dateblock5 | cashflow_stress | Q1 | -0.003050 | -0.003633 | -0.001966 | -0.005529 | 0.973958 | 0.953125 | 0.031088 | True | False | 0.578043 |
| e296_002 | raw_human_context | subject5 | badnight_aftereffect | Q3 | -0.015000 | -0.022278 | -0.019855 | -0.023268 | 0.890625 | 0.671875 | 0.113990 | False | False | 0.358701 |
| e296_026 | raw_human_context | subject5 | routine_fragmentation | S1 | -0.011595 | -0.020397 | -0.011591 | -0.027674 | 0.947917 | 0.890625 | 0.056995 | False | False | 0.278195 |
| e296_031 | hybrid_context | subject5 | social_overload | S3 | -0.011343 | -0.017672 | -0.014608 | -0.020639 | 0.890625 | 0.734375 | 0.113990 | False | False | 0.559079 |
| e296_019 | raw_human_context | subject5 | routine_anchor_recovery | S1 | -0.010700 | -0.021158 | -0.017157 | -0.022554 | 0.880208 | 0.703125 | 0.124352 | False | False | 0.190003 |
| e296_001 | family_jepa_context | subject5 | badnight_aftereffect | Q1 | -0.006496 | -0.011422 | -0.006426 | -0.018048 | 0.947917 | 0.843750 | 0.056995 | False | False | 0.759422 |
| e296_005 | family_jepa_context | dateblock5 | badnight_aftereffect | S4 | -0.003668 | -0.007387 | -0.005546 | -0.008778 | 0.885417 | 0.796875 | 0.119171 | False | False | 0.799740 |
| e296_032 | raw_human_context | subject5 | social_overload | S3 | -0.002353 | -0.005315 | -0.002471 | -0.005830 | 0.942708 | 0.890625 | 0.062176 | False | False | 0.369413 |
| e296_020 | family_jepa_context | dateblock5 | routine_anchor_recovery | S2 | -0.002030 | -0.006773 | -0.003479 | -0.008487 | 0.916667 | 0.890625 | 0.088083 | False | False | 0.621748 |
| e296_006 | hybrid_context | dateblock5 | badnight_aftereffect | S4 | -0.001795 | -0.007323 | -0.003084 | -0.015803 | 0.906250 | 0.890625 | 0.098446 | False | False | 0.734727 |
| e296_011 | raw_human_context | dateblock5 | cashflow_stress | Q1 | -0.001676 | -0.006611 | -0.003070 | -0.008610 | 0.869792 | 0.859375 | 0.134715 | False | False | 0.349852 |
| e296_018 | family_jepa_context | subject5 | routine_anchor_recovery | S1 | -0.001645 | -0.004866 | -0.002913 | -0.006654 | 0.895833 | 0.859375 | 0.108808 | False | False | 0.327976 |
| e296_004 | hybrid_context | dateblock5 | badnight_aftereffect | S2 | -0.001634 | -0.007135 | -0.004841 | -0.012512 | 0.848958 | 0.781250 | 0.155440 | False | False | 0.734727 |
| e296_003 | family_jepa_context | subject5 | badnight_aftereffect | S2 | -0.001608 | -0.002943 | -0.001594 | -0.004091 | 0.953125 | 0.906250 | 0.051813 | False | False | 0.759422 |
| e296_000 | family_jepa_context | dateblock5 | badnight_aftereffect | Q1 | -0.001545 | -0.008022 | -0.003718 | -0.013375 | 0.859375 | 0.796875 | 0.145078 | False | False | 0.799740 |

## Robust Instances

| candidate_id | view_id | split | episode | target | delta_logloss | null_q01 | null_q05 | dominance | min_mode_dominance | p_value_lower | state_corr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e296_009 | hybrid_context | subject5 | bedtime_arousal | S3 | -0.016376 | -0.014663 | -0.008813 | 0.994792 | 0.984375 | 0.010363 | 0.584732 |
| e296_025 | raw_human_context | dateblock5 | routine_fragmentation | S1 | -0.009804 | -0.004737 | -0.002576 | 0.994792 | 0.984375 | 0.010363 | 0.340042 |
| e296_021 | family_jepa_context | subject5 | routine_anchor_recovery | S2 | -0.009187 | -0.008294 | -0.005565 | 0.994792 | 0.984375 | 0.010363 | 0.327976 |
| e296_028 | hybrid_context | subject5 | routine_fragmentation | S3 | -0.007785 | -0.006925 | -0.004306 | 0.994792 | 0.984375 | 0.010363 | 0.442913 |
| e296_007 | raw_human_context | dateblock5 | bedtime_arousal | S1 | -0.006915 | -0.005113 | -0.001896 | 0.994792 | 0.984375 | 0.010363 | 0.729085 |

## Target Read

| target | candidates | strict | robust | best_delta | mean_delta |
| --- | --- | --- | --- | --- | --- |
| S3 | 12 | 10 | 2 | -0.016376 | -0.006784 |
| S1 | 9 | 6 | 2 | -0.017244 | -0.010614 |
| S2 | 5 | 2 | 1 | -0.009187 | -0.003594 |
| Q1 | 4 | 1 | 0 | -0.006496 | -0.003192 |
| Q3 | 1 | 0 | 0 | -0.015000 | -0.015000 |
| S4 | 2 | 0 | 0 | -0.003668 | -0.002732 |

## Decision

Some E295 episode-target states survive strict local nulls. They are still not submissions; the next step is target-limited materialization with a current-best anchor and the same matched-null governor.

## Files

- `e296_episode_target_strict_candidates.csv`
- `e296_episode_target_pair_summary.csv`
- `e296_episode_target_strict_nulls.csv`
