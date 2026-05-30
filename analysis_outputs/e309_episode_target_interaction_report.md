# E309 Episode Target-Interaction Probe

Public LB는 사용하지 않았다. E297의 단일 target materialization 실패를 반대로 해석해, 인간 episode state가 target pair의 joint pattern을 설명하는지 검증했다.

## Settings

- quick scan: all episode/pair actual deltas only; no nulls
- strict null reps per mode: `12`
- null modes: row, subject, dateblock
- target object: 4-class joint label for each target pair

## Counts

- quick scanned rows: `426`
- strict rerun rows: `32`
- strict gates: `29`
- robust gates: `13`
- pair gates: `12`

## Pair-Family Read

| pair_family | rows | strict | robust | best_delta | mean_delta |
| --- | --- | --- | --- | --- | --- |
| QS | 18 | 16 | 8 | -0.046023 | -0.013514 |
| SS | 12 | 12 | 5 | -0.019841 | -0.011321 |
| QQ | 2 | 1 | 0 | -0.016790 | -0.012878 |

## Strong Pair Gates

| episode | pair | pair_family | instances | strict_instances | robust_instances | best_delta | best_p_value | worst_mode_dom | best_state_corr | interaction_story |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cashflow_stress | Q1_S1 | QS | 3 | 3 | 2 | -0.046023 | 0.027027 | 1.000000 | 0.578043 | money rumination affecting subjective satisfaction and stage stress |
| cashflow_stress | S1_S4 | SS | 2 | 2 | 1 | -0.019841 | 0.027027 | 0.916667 | 0.537775 | money rumination affecting subjective satisfaction and stage stress |
| cashflow_stress | S1_S2 | SS | 2 | 2 | 1 | -0.018624 | 0.027027 | 1.000000 | 0.537775 | money rumination affecting subjective satisfaction and stage stress |
| cashflow_stress | S1_S3 | SS | 2 | 2 | 1 | -0.010444 | 0.027027 | 0.916667 | 0.537775 | money rumination affecting subjective satisfaction and stage stress |
| bedtime_arousal | Q1_S1 | QS | 1 | 1 | 1 | -0.016509 | 0.027027 | 1.000000 | 0.532194 | bright screen, messages, search spiral, media/game and phone-in-bed before sleep -> subjective-objective sleep translation |
| bedtime_arousal | Q3_S3 | QS | 1 | 1 | 1 | -0.013663 | 0.027027 | 1.000000 | 0.584732 | bright screen, messages, search spiral, media/game and phone-in-bed before sleep -> subjective-objective sleep translation |
| bedtime_arousal | Q1_S3 | QS | 1 | 1 | 1 | -0.012994 | 0.027027 | 1.000000 | 0.584732 | bright screen, messages, search spiral, media/game and phone-in-bed before sleep -> subjective-objective sleep translation |
| bedtime_arousal | Q2_S3 | QS | 1 | 1 | 1 | -0.012893 | 0.027027 | 1.000000 | 0.584732 | bright screen, messages, search spiral, media/game and phone-in-bed before sleep -> subjective-objective sleep translation |
| bedtime_arousal | S1_S2 | SS | 1 | 1 | 1 | -0.012755 | 0.027027 | 1.000000 | 0.532194 | late screen/message arousal changing sleep-stage composition |
| home_recovery | Q1_S3 | QS | 1 | 1 | 1 | -0.012004 | 0.027027 | 1.000000 | 0.419068 | home recovery linking physiological calm with sleep-stage consistency |
| badnight_aftereffect | Q3_S3 | QS | 1 | 1 | 1 | -0.011592 | 0.027027 | 1.000000 | 0.358701 | previous bad night carrying into next-day subjective/objective mismatch |
| home_recovery | S3_S4 | SS | 1 | 1 | 1 | -0.010824 | 0.027027 | 1.000000 | 0.419068 | home recovery linking physiological calm with sleep-stage consistency |

## Strongest Strict Rows

| view_id | split | episode | pair | pair_family | delta_logloss | strict_null_q05 | strict_dominance | strict_min_mode_dominance | p_value_lower | margin_to_null_q05 | strict_gate | robust_gate | state_corr | interaction_story |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| raw_human_context | subject5 | cashflow_stress | Q1_S1 | QS | -0.046023 | -0.016272 | 1.000000 | 1.000000 | 0.027027 | 0.029751 | True | True | 0.298140 | money rumination affecting subjective satisfaction and stage stress |
| hybrid_context | subject5 | cashflow_stress | Q1_S1 | QS | -0.022072 | -0.005874 | 1.000000 | 1.000000 | 0.027027 | 0.016198 | True | True | 0.537775 | money rumination affecting subjective satisfaction and stage stress |
| raw_human_context | subject5 | cashflow_stress | S1_S2 | SS | -0.018624 | -0.002319 | 1.000000 | 1.000000 | 0.027027 | 0.016305 | True | True | 0.298140 | money rumination affecting subjective satisfaction and stage stress |
| raw_human_context | subject5 | bedtime_arousal | Q1_S1 | QS | -0.016509 | -0.012083 | 1.000000 | 1.000000 | 0.027027 | 0.004425 | True | True | 0.532194 | bright screen, messages, search spiral, media/game and phone-in-bed before sleep -> subjective-objective sleep translation |
| hybrid_context | subject5 | bedtime_arousal | Q3_S3 | QS | -0.013663 | -0.004716 | 1.000000 | 1.000000 | 0.027027 | 0.008947 | True | True | 0.584732 | bright screen, messages, search spiral, media/game and phone-in-bed before sleep -> subjective-objective sleep translation |
| hybrid_context | subject5 | bedtime_arousal | Q1_S3 | QS | -0.012994 | -0.006991 | 1.000000 | 1.000000 | 0.027027 | 0.006003 | True | True | 0.584732 | bright screen, messages, search spiral, media/game and phone-in-bed before sleep -> subjective-objective sleep translation |
| hybrid_context | subject5 | bedtime_arousal | Q2_S3 | QS | -0.012893 | -0.006847 | 1.000000 | 1.000000 | 0.027027 | 0.006046 | True | True | 0.584732 | bright screen, messages, search spiral, media/game and phone-in-bed before sleep -> subjective-objective sleep translation |
| raw_human_context | subject5 | bedtime_arousal | S1_S2 | SS | -0.012755 | -0.003862 | 1.000000 | 1.000000 | 0.027027 | 0.008893 | True | True | 0.532194 | late screen/message arousal changing sleep-stage composition |
| hybrid_context | dateblock5 | home_recovery | Q1_S3 | QS | -0.012004 | -0.004869 | 1.000000 | 1.000000 | 0.027027 | 0.007135 | True | True | 0.419068 | home recovery linking physiological calm with sleep-stage consistency |
| raw_human_context | subject5 | badnight_aftereffect | Q3_S3 | QS | -0.011592 | -0.009411 | 1.000000 | 1.000000 | 0.027027 | 0.002181 | True | True | 0.358701 | previous bad night carrying into next-day subjective/objective mismatch |
| hybrid_context | dateblock5 | home_recovery | S3_S4 | SS | -0.010824 | -0.005358 | 1.000000 | 1.000000 | 0.027027 | 0.005466 | True | True | 0.419068 | home recovery linking physiological calm with sleep-stage consistency |
| hybrid_context | subject5 | cashflow_stress | S1_S4 | SS | -0.010398 | -0.004153 | 1.000000 | 1.000000 | 0.027027 | 0.006245 | True | True | 0.537775 | money rumination affecting subjective satisfaction and stage stress |
| hybrid_context | subject5 | cashflow_stress | S1_S3 | SS | -0.010389 | -0.002905 | 1.000000 | 1.000000 | 0.027027 | 0.007484 | True | True | 0.537775 | money rumination affecting subjective satisfaction and stage stress |
| raw_human_context | subject5 | cashflow_stress | S1_S4 | SS | -0.019841 | -0.018534 | 0.972222 | 0.916667 | 0.054054 | 0.001307 | True | False | 0.298140 | money rumination affecting subjective satisfaction and stage stress |
| hybrid_context | subject5 | bedtime_arousal | S1_S3 | SS | -0.011850 | -0.011478 | 0.972222 | 0.916667 | 0.054054 | 0.000372 | True | False | 0.584732 | late screen/message arousal changing sleep-stage composition |
| raw_human_context | subject5 | badnight_aftereffect | Q3_S2 | QS | -0.011157 | -0.007804 | 0.972222 | 0.916667 | 0.054054 | 0.003353 | True | False | 0.358701 | previous bad night carrying into next-day subjective/objective mismatch |
| raw_human_context | subject5 | cashflow_stress | S1_S3 | SS | -0.010444 | -0.009233 | 0.972222 | 0.916667 | 0.054054 | 0.001211 | True | False | 0.298140 | money rumination affecting subjective satisfaction and stage stress |
| hybrid_context | subject5 | cashflow_stress | S1_S2 | SS | -0.009764 | -0.000883 | 1.000000 | 1.000000 | 0.027027 | 0.008881 | True | False | 0.537775 | money rumination affecting subjective satisfaction and stage stress |
| hybrid_context | dateblock5 | cashflow_stress | Q3_S1 | QS | -0.009365 | -0.002562 | 1.000000 | 1.000000 | 0.027027 | 0.006803 | True | False | 0.578043 | money rumination affecting subjective satisfaction and stage stress |
| raw_human_context | dateblock5 | cashflow_stress | Q1_Q2 | QQ | -0.008967 | 0.000371 | 1.000000 | 1.000000 | 0.027027 | 0.009337 | True | False | 0.349852 | money rumination affecting subjective satisfaction and stage stress |
| raw_human_context | dateblock5 | cashflow_stress | Q1_S3 | QS | -0.008908 | -0.003995 | 1.000000 | 1.000000 | 0.027027 | 0.004913 | True | False | 0.349852 | money rumination affecting subjective satisfaction and stage stress |
| raw_human_context | dateblock5 | routine_fragmentation | Q3_S1 | QS | -0.008551 | -0.001296 | 0.972222 | 0.916667 | 0.054054 | 0.007255 | True | False | 0.340042 | scattered routine changing stage stability and subjective-objective alignment |
| hybrid_context | dateblock5 | cashflow_stress | Q1_S1 | QS | -0.008045 | -0.005103 | 1.000000 | 1.000000 | 0.027027 | 0.002942 | True | False | 0.578043 | money rumination affecting subjective satisfaction and stage stress |
| raw_human_context | dateblock5 | bedtime_arousal | Q2_S1 | QS | -0.007514 | -0.002786 | 0.972222 | 0.916667 | 0.054054 | 0.004728 | True | False | 0.729085 | bright screen, messages, search spiral, media/game and phone-in-bed before sleep -> subjective-objective sleep translation |
| family_jepa_context | subject5 | routine_anchor_recovery | Q2_S2 | QS | -0.007140 | -0.000860 | 1.000000 | 1.000000 | 0.027027 | 0.006280 | True | False | 0.327976 | stable bedtime/home routine restoring stage and quality consistency |
| hybrid_context | dateblock5 | home_recovery | S2_S3 | SS | -0.007079 | -0.002001 | 1.000000 | 1.000000 | 0.027027 | 0.005077 | True | False | 0.419068 | home recovery linking physiological calm with sleep-stage consistency |
| raw_human_context | dateblock5 | bedtime_arousal | S1_S4 | SS | -0.007024 | -0.000315 | 0.972222 | 0.916667 | 0.054054 | 0.006709 | True | False | 0.729085 | late screen/message arousal changing sleep-stage composition |
| hybrid_context | dateblock5 | home_recovery | Q2_S3 | QS | -0.006974 | -0.005313 | 0.972222 | 0.916667 | 0.054054 | 0.001661 | True | False | 0.419068 | home recovery linking physiological calm with sleep-stage consistency |
| hybrid_context | dateblock5 | social_overload | S1_S3 | SS | -0.006856 | -0.002343 | 1.000000 | 1.000000 | 0.027027 | 0.004513 | True | False | 0.804829 | late social load changing objective-stage and subjective quality translation |
| raw_human_context | subject5 | badnight_aftereffect | Q1_Q3 | QQ | -0.016790 | -0.019022 | 0.944444 | 0.833333 | 0.081081 | -0.002232 | False | False | 0.358701 | previous bad night carrying into next-day subjective/objective mismatch |
| raw_human_context | subject5 | badnight_aftereffect | Q3_S1 | QS | -0.016427 | -0.020408 | 0.861111 | 0.583333 | 0.162162 | -0.003981 | False | False | 0.358701 | previous bad night carrying into next-day subjective/objective mismatch |
| raw_human_context | subject5 | badnight_aftereffect | Q1_S1 | QS | -0.011422 | -0.014573 | 0.916667 | 0.750000 | 0.108108 | -0.003151 | False | False | 0.358701 | previous bad night carrying into next-day subjective/objective mismatch |

## Decision

- Human episode state does survive as a target-interaction representation.
- This does not justify public submission yet. E297 already showed that single-target transfer collapses into null-common current-tensor movement.
- Next experiment should materialize only the gated pair interaction: coupled target deltas with wrong-pair and shuffled-state controls, then E308-style governor.

## Outputs

- `analysis_outputs/e309_episode_target_interaction_scan.csv`
- `analysis_outputs/e309_episode_target_interaction_strict.csv`
- `analysis_outputs/e309_episode_target_interaction_pair_summary.csv`
- `analysis_outputs/e309_episode_target_interaction_nulls.csv`
- `analysis_outputs/e309_episode_target_interaction_report.md`
