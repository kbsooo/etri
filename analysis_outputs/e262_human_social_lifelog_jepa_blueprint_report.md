# E262 Human/Social Lifelog JEPA Blueprint

## Question

Can the raw lifelog be translated into human lifestyle states before we ask a model to predict sleep labels?

The goal is not to add generic aggregates. The goal is to build JEPA-ready context/target variables that represent social stimulation, routine, commute rhythm, late cognitive load, physical fatigue, and sleep-onset risk.

## Raw Evidence

- Rows covered: `700` (`450` train, `250` test).
- Subjects: `10`.
- Generated lifestyle/raw context features: `790`.
- Raw app usage includes real social/routine apps such as KakaoTalk, calls/messages, search/browser, finance/shopping, health-walk, and religion/routine apps.

## Top App Categories

| app_name | category | event_count | total_time |
| --- | --- | --- | --- |
| one ui 홈 | home_utility | 29114 | 4655575663.000000 |
| 시스템 ui | home_utility | 16388 | 2598865909.000000 |
| 카카오톡 | social_msg | 17548 | 2408771919.000000 |
| naver | search_browser | 7361 | 1156302340.000000 |
| youtube | media | 4566 | 806269206.000000 |
| ✝️성경일독q | religion_routine | 4615 | 778709744.000000 |
| 캐시워크 | health_walk | 5042 | 555842806.000000 |
| instagram | social_msg | 3440 | 554532193.000000 |
| 통화 | call | 4364 | 448883450.000000 |
| microsoft launcher | home_utility | 2990 | 440910412.000000 |
| 당근 | other_app | 2277 | 427517814.000000 |
| 타임스프레드 | other_app | 3504 | 397217115.000000 |
| 메시지 | social_msg | 3845 | 274838836.000000 |
| 토스 | finance | 2086 | 246748715.000000 |
| 네이버 웹툰 | other_app | 1274 | 220448137.000000 |
| 전화 | call | 2997 | 219716447.000000 |
| 갤러리 | home_utility | 1750 | 203261000.000000 |
| threads | other_app | 998 | 202475470.000000 |
| 클래시 로얄 | other_app | 872 | 188082621.000000 |
| 쿠팡 | shopping | 1736 | 182035200.000000 |
| chrome | search_browser | 1958 | 165331729.000000 |
| 카메라 | home_utility | 1931 | 147397806.000000 |
| tiktok | other_app | 648 | 136872436.000000 |
| 네이트 | other_app | 981 | 127632070.000000 |
| number match | other_app | 474 | 122506738.000000 |
| 시계 | home_utility | 1489 | 116626178.000000 |
| x | other_app | 620 | 100214367.000000 |
| youtube music | media | 739 | 94625270.000000 |
| help-cnuh24 | other_app | 1235 | 88441526.000000 |
| 재난문자 | social_msg | 1403 | 88194849.000000 |

## Strongest Label-Lift Probes

These are not submission features yet. They are cheap falsification signals for human hypotheses.

| feature | target | label_mean_low_q | label_mean_high_q | high_minus_low | subject_z_corr | abs_effect | hypothesis_family |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ambience_music_late | S3 | 0.522124 | 0.769912 | 0.247788 | 0.054973 | 0.247788 | other_lifestyle |
| gps_speed_mean_deepnight | S4 | 0.460177 | 0.699115 | 0.238938 | 0.112167 | 0.238938 | workday_commute |
| gps_speed_mean_evening | S1 | 0.522124 | 0.761062 | 0.238938 | 0.042277 | 0.238938 | workday_commute |
| gps_speed_mean_deepnight | S2 | 0.575221 | 0.805310 | 0.230088 | 0.077116 | 0.230088 | workday_commute |
| gps_speed_mean_deepnight | S3 | 0.610619 | 0.840708 | 0.230088 | 0.000621 | 0.230088 | workday_commute |
| ambience_music_evening | S3 | 0.504425 | 0.725664 | 0.221239 | -0.044159 | 0.221239 | other_lifestyle |
| charge_m_charging_mean_presleep | Q3 | 0.469027 | 0.681416 | 0.212389 | 0.112921 | 0.212389 | routine_stability |
| human_late_cognitive_load | S3 | 0.535088 | 0.743363 | 0.208275 | 0.074979 | 0.208275 | late_cognitive_load |
| human_sleep_onset_risk | Q3 | 0.707965 | 0.504425 | -0.203540 | -0.040687 | 0.203540 | sleep_onset_fragmentation |
| ambience_music_deepnight | S3 | 0.504425 | 0.699115 | 0.194690 | 0.014737 | 0.194690 | other_lifestyle |
| gps_speed_mean_morning | S3 | 0.557522 | 0.743363 | 0.185841 | 0.057152 | 0.185841 | workday_commute |
| ambience_music_afternoon | S3 | 0.530973 | 0.716814 | 0.185841 | -0.021997 | 0.185841 | other_lifestyle |
| gps_speed_mean_presleep | S1 | 0.566372 | 0.752212 | 0.185841 | 0.023535 | 0.185841 | workday_commute |
| usage_presleep_other_app_time | S1 | 0.769912 | 0.584071 | -0.185841 | -0.064925 | 0.185841 | other_lifestyle |
| usage_late_call_time | S3 | 0.617910 | 0.796460 | 0.178550 | 0.038150 | 0.178550 | social_overstimulation |
| usage_presleep_home_utility_time | Q2 | 0.477876 | 0.654867 | 0.176991 | 0.027353 | 0.176991 | other_lifestyle |
| usage_presleep_search_browser_time | Q1 | 0.389381 | 0.566372 | 0.176991 | 0.083603 | 0.176991 | late_cognitive_load |
| usage_late_call_time | Q1 | 0.537313 | 0.362832 | -0.174482 | -0.053723 | 0.174482 | social_overstimulation |
| usage_late_search_browser_time | S3 | 0.613636 | 0.787611 | 0.173974 | 0.082193 | 0.173974 | late_cognitive_load |
| ambience_music_afternoon | Q1 | 0.584071 | 0.415929 | -0.168142 | -0.076358 | 0.168142 | other_lifestyle |
| ambience_music_morning | S3 | 0.557522 | 0.725664 | 0.168142 | 0.021348 | 0.168142 | other_lifestyle |
| ambience_speech_morning | S1 | 0.557522 | 0.725664 | 0.168142 | -0.003181 | 0.168142 | social_overstimulation |
| human_late_cognitive_load_subj_z | S1 | 0.796460 | 0.628319 | -0.168142 | -0.112122 | 0.168142 | late_cognitive_load |
| gps_speed_mean_late | S1 | 0.601770 | 0.769912 | 0.168142 | -0.032483 | 0.168142 | workday_commute |
| human_late_cognitive_load_subj_z | S3 | 0.601770 | 0.769912 | 0.168142 | 0.074979 | 0.168142 | late_cognitive_load |
| ambience_inside_public_afternoon | Q1 | 0.526132 | 0.362832 | -0.163301 | -0.085202 | 0.163301 | other_lifestyle |
| screen_m_screen_use_mean_late | S2 | 0.711864 | 0.548673 | -0.163192 | -0.044690 | 0.163192 | sleep_onset_fragmentation |
| charge_m_charging_mean_presleep | Q1 | 0.433628 | 0.592920 | 0.159292 | 0.073960 | 0.159292 | routine_stability |
| gps_speed_mean_deepnight | S1 | 0.610619 | 0.769912 | 0.159292 | -0.029076 | 0.159292 | workday_commute |
| pedo_step_sum_presleep | Q1 | 0.404110 | 0.557522 | 0.153413 | -0.005622 | 0.153413 | physical_fatigue |

## Hypothesis Family Signal

| hypothesis_family | max_abs_effect | mean_abs_effect_top10 |
| --- | --- | --- |
| other_lifestyle | 0.247788 | 0.186242 |
| workday_commute | 0.238938 | 0.193805 |
| routine_stability | 0.212389 | 0.133628 |
| late_cognitive_load | 0.208275 | 0.146206 |
| sleep_onset_fragmentation | 0.203540 | 0.124419 |
| social_overstimulation | 0.178550 | 0.143945 |
| physical_fatigue | 0.153413 | 0.114154 |

## Largest Train/Test Shift Features

These are potential domain/block signatures and leakage-risk diagnostics.

| feature | non_null_rate | train_mean | test_mean | abs_train_test_gap_z |
| --- | --- | --- | --- | --- |
| hr_heart_rate_min_mean_day | 1.000000 | 71.402415 | 81.193036 | 0.378081 |
| hr_heart_rate_mean_mean_day | 1.000000 | 76.800039 | 87.005392 | 0.371823 |
| hr_heart_rate_max_mean_day | 1.000000 | 82.444025 | 93.059627 | 0.364285 |
| hr_heart_rate_max_std_day | 1.000000 | 11.546319 | 14.056524 | 0.362939 |
| hr_heart_rate_mean_std_day | 1.000000 | 10.891473 | 13.285992 | 0.353316 |
| hr_heart_rate_min_std_day | 1.000000 | 10.745651 | 13.101278 | 0.350115 |
| hr_heart_rate_std_std_day | 1.000000 | 1.936130 | 2.258147 | 0.331896 |
| pedo_burned_calories_count_day | 1.000000 | 1020.595556 | 1155.328000 | 0.329812 |
| pedo_distance_count_day | 1.000000 | 1020.595556 | 1155.328000 | 0.329812 |
| pedo_speed_count_day | 1.000000 | 1020.595556 | 1155.328000 | 0.329812 |
| pedo_step_count_day | 1.000000 | 1020.595556 | 1155.328000 | 0.329812 |
| pedo_burned_calories_count_afternoon | 1.000000 | 294.251111 | 328.560000 | 0.325083 |
| pedo_distance_count_afternoon | 1.000000 | 294.251111 | 328.560000 | 0.325083 |
| pedo_speed_count_afternoon | 1.000000 | 294.251111 | 328.560000 | 0.325083 |
| pedo_step_count_afternoon | 1.000000 | 294.251111 | 328.560000 | 0.325083 |
| hr_heart_rate_max_max_day | 1.000000 | 125.246667 | 139.444000 | 0.307019 |
| hr_heart_rate_min_max_day | 1.000000 | 113.393333 | 126.132000 | 0.299645 |
| hr_heart_rate_mean_max_day | 1.000000 | 118.489270 | 131.582823 | 0.298277 |
| hr_heart_rate_std_max_day | 1.000000 | 14.848892 | 17.245193 | 0.297277 |
| pedo_burned_calories_count_morning | 1.000000 | 255.046667 | 290.176000 | 0.285130 |

## JEPA Translation

Good JEPA target design here should avoid raw reconstruction. Candidate context-target pairs:

1. Social-night JEPA:
   - context: non-app sensors, weekday, prior/next day lifestyle state.
   - target: late social/call/speech latent.
   - question: can the world model infer social overstimulation from surrounding behavior?

2. Routine-stability JEPA:
   - context: subject history and day-of-week.
   - target: religion/routine app timing, charging regularity, screen-off stability.
   - question: is sleep quality tied to stable ritual rather than raw phone time?

3. Commute/workday JEPA:
   - context: morning/evening GPS/WiFi/BLE/pedo signatures.
   - target: workday/home-away/commute latent.
   - question: do Q/S labels depend on lifestyle block state more than row features?

4. Sleep-onset JEPA:
   - context: daytime activity and evening app categories.
   - target: late screen/light/movement/charging latent.
   - question: can we predict a hidden bedtime-fragmentation representation?

5. Target-state JEPA:
   - context: all human diary features with block masks.
   - target: Q/S co-occurrence state or E247-like Q3 public-tail energy.
   - question: can social lifestyle state explain the Q3 hard-tail cells that current numeric models only patch?

## Next Validation Gate

- Build OOF folds by subject/date block, not random rows.
- Test whether human lifestyle composites improve Q/S target LogLoss under blockwise CV.
- Test whether latent lifestyle states explain E247/E256 disagreement cells, especially Q3 rows `188`, `96`, `87`, and `138`.
- Reject any feature family that only predicts train/test split or subject identity without target lift inside subject.
