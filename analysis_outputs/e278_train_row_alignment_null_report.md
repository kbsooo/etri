# E278 Train Row-Alignment Null Audit

## Question

Do q-sleep diary-energy policies pick labeled train rows better than matched row/subject/dateblock shuffle nulls when applied on top of OOF calendar/subject baselines?

## Method

- Baselines: OOF logistic calendar/subject models for Q1/Q2/Q3.
- Splits: subject-group OOF and dateblock-group OOF.
- Policies: same E275/E276 q-sleep semantic variants.
- Nulls: `200` per row/subject/dateblock mode per candidate/split.
- Metric: mean Q1/Q2/Q3 logloss delta versus OOF baseline; lower is better.

## Summary

- candidate/split rows: `40`
- train-align gate rows: `27`
- candidates passing both subject and dateblock gates: `13`

## Candidate Results

| candidate_id | variant_type | family | split | axis_count | changed_cells | actual_delta | null_q20 | null_median | dominance | row_dominance | subject_dominance | dateblock_dominance | placebo_adjusted_vs_median | placebo_adjusted_vs_best | train_align_gate | Q1_delta | Q2_delta | Q3_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_bedtime_phone | family_only | bedtime_phone | subject_oof | 1 | 24 | -0.000378295 | -0.000204210 | -0.000114701 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | -0.000263594 | -0.000011242 | True | 0.000000000 | 0.000000000 | -0.001134886 |
| only_bedtime_phone | family_only | bedtime_phone | dateblock_oof | 1 | 24 | -0.000276001 | -0.000115000 | -0.000031998 | 0.998333333 | 0.995000000 | 1.000000000 | 1.000000000 | -0.000244003 | 0.000002401 | True | -0.000000000 | 0.000000000 | -0.000828003 |
| no_media_game | leave_one_family | media_game | subject_oof | 11 | 179 | -0.001841266 | -0.001431992 | -0.000578202 | 0.990000000 | 1.000000000 | 1.000000000 | 0.970000000 | -0.001263064 | 0.000231226 | True | -0.000845903 | -0.000588885 | -0.004089009 |
| no_media_game | leave_one_family | media_game | dateblock_oof | 11 | 179 | -0.001276270 | -0.000841514 | -0.000163096 | 0.988333333 | 1.000000000 | 1.000000000 | 0.965000000 | -0.001113174 | 0.000129011 | True | -0.000640876 | -0.000550803 | -0.002637132 |
| q3_only | target_ablation |  | subject_oof | 9 | 131 | -0.001363003 | -0.001076806 | -0.000504897 | 0.980000000 | 1.000000000 | 1.000000000 | 0.940000000 | -0.000858106 | 0.000152198 | True | 0.000000000 | 0.000000000 | -0.004089009 |
| q3_only | target_ablation |  | dateblock_oof | 9 | 131 | -0.000879044 | -0.000609619 | -0.000140928 | 0.973333333 | 1.000000000 | 1.000000000 | 0.920000000 | -0.000738116 | 0.000181954 | True | -0.000000000 | 0.000000000 | -0.002637132 |
| no_cognitive_money | leave_one_family | cognitive_money | dateblock_oof | 11 | 188 | -0.001321820 | -0.001029807 | -0.000161509 | 0.966666667 | 1.000000000 | 1.000000000 | 0.900000000 | -0.001160310 | 0.000096114 | True | -0.000640876 | -0.000810051 | -0.002514531 |
| no_cognitive_money | leave_one_family | cognitive_money | subject_oof | 11 | 188 | -0.001925357 | -0.001592657 | -0.000581748 | 0.960000000 | 1.000000000 | 1.000000000 | 0.880000000 | -0.001343609 | 0.000276440 | True | -0.000845903 | -0.001061952 | -0.003868215 |
| jepa_only | axis_kind |  | dateblock_oof | 6 | 112 | -0.000802362 | -0.000561822 | -0.000149009 | 0.960000000 | 1.000000000 | 1.000000000 | 0.880000000 | -0.000653353 | 0.000230828 | True | -0.000640876 | 0.000000000 | -0.001766210 |
| no_social_comm | leave_one_family | social_comm | subject_oof | 11 | 190 | -0.001852610 | -0.001604638 | -0.000579978 | 0.958333333 | 1.000000000 | 1.000000000 | 0.875000000 | -0.001272632 | 0.000299981 | True | -0.000845903 | -0.001061952 | -0.003649973 |
| no_routine_calendar | leave_one_family | routine_calendar | subject_oof | 11 | 188 | -0.001811509 | -0.001534002 | -0.000564033 | 0.956666667 | 1.000000000 | 1.000000000 | 0.870000000 | -0.001247475 | 0.000553556 | True | -0.000845903 | -0.001061952 | -0.003526670 |
| no_routine_calendar | leave_one_family | routine_calendar | dateblock_oof | 11 | 188 | -0.001233480 | -0.000959225 | -0.000147367 | 0.955000000 | 1.000000000 | 1.000000000 | 0.865000000 | -0.001086114 | 0.000304257 | True | -0.000640876 | -0.000810051 | -0.002249513 |
| full_qsleep | primary |  | subject_oof | 12 | 201 | -0.001998955 | -0.001699961 | -0.000622277 | 0.953333333 | 1.000000000 | 1.000000000 | 0.860000000 | -0.001376678 | 0.000302617 | True | -0.000845903 | -0.001061952 | -0.004089009 |
| full_qsleep | primary |  | dateblock_oof | 12 | 201 | -0.001362687 | -0.001068527 | -0.000124571 | 0.951666667 | 1.000000000 | 1.000000000 | 0.855000000 | -0.001238115 | 0.000425493 | True | -0.000640876 | -0.000810051 | -0.002637132 |
| no_social_comm | leave_one_family | social_comm | dateblock_oof | 11 | 190 | -0.001248707 | -0.000977382 | -0.000161353 | 0.951666667 | 1.000000000 | 1.000000000 | 0.855000000 | -0.001087354 | 0.000399591 | True | -0.000640876 | -0.000810051 | -0.002295193 |
| jepa_only | axis_kind |  | subject_oof | 6 | 112 | -0.001263774 | -0.001057421 | -0.000512856 | 0.938333333 | 1.000000000 | 1.000000000 | 0.815000000 | -0.000750919 | 0.000294711 | True | -0.000845903 | 0.000000000 | -0.002945420 |
| no_bedtime_phone | leave_one_family | bedtime_phone | dateblock_oof | 11 | 189 | -0.001257694 | -0.001077393 | -0.000200698 | 0.928333333 | 1.000000000 | 1.000000000 | 0.785000000 | -0.001056996 | 0.000369556 | True | -0.000640876 | -0.000810051 | -0.002322154 |
| only_mobility_context | family_only | mobility_context | subject_oof | 4 | 72 | -0.000783386 | -0.000665975 | -0.000318961 | 0.920000000 | 1.000000000 | 1.000000000 | 0.760000000 | -0.000464425 | 0.000250979 | True | -0.000845903 | 0.000000000 | -0.001504254 |
| only_diary_global | family_only | diary_global | subject_oof | 3 | 62 | -0.000500702 | -0.000380583 | -0.000183977 | 0.918333333 | 1.000000000 | 0.980000000 | 0.775000000 | -0.000316726 | 0.000374927 | True | 0.000000000 | -0.000588885 | -0.000913222 |
| no_bedtime_phone | leave_one_family | bedtime_phone | subject_oof | 11 | 189 | -0.001869677 | -0.001634851 | -0.000602399 | 0.916666667 | 1.000000000 | 1.000000000 | 0.750000000 | -0.001267279 | 0.000361220 | True | -0.000845903 | -0.001061952 | -0.003701176 |
| no_mobility_context | leave_one_family | mobility_context | subject_oof | 8 | 150 | -0.001460560 | -0.001324506 | -0.000503803 | 0.916666667 | 1.000000000 | 1.000000000 | 0.750000000 | -0.000956758 | 0.000349689 | True | 0.000000000 | -0.001061952 | -0.003319729 |
| no_mobility_context | leave_one_family | mobility_context | dateblock_oof | 8 | 150 | -0.000971154 | -0.000810419 | -0.000151676 | 0.913333333 | 1.000000000 | 1.000000000 | 0.740000000 | -0.000819478 | 0.000530108 | True | -0.000000000 | -0.000810051 | -0.002103412 |
| only_mobility_context | family_only | mobility_context | dateblock_oof | 4 | 72 | -0.000453362 | -0.000343303 | -0.000108411 | 0.895000000 | 0.990000000 | 0.995000000 | 0.700000000 | -0.000344951 | 0.000283323 | True | -0.000640876 | 0.000000000 | -0.000719210 |
| nonjepa_only | axis_kind |  | subject_oof | 6 | 122 | -0.001214746 | -0.001103329 | -0.000360401 | 0.893333333 | 1.000000000 | 1.000000000 | 0.680000000 | -0.000854345 | 0.000304857 | True | 0.000000000 | -0.001061952 | -0.002582287 |
| only_diary_global | family_only | diary_global | dateblock_oof | 3 | 62 | -0.000327521 | -0.000237844 | -0.000076757 | 0.888333333 | 0.965000000 | 0.960000000 | 0.740000000 | -0.000250764 | 0.000276109 | True | -0.000000000 | -0.000550803 | -0.000431761 |
| nonjepa_only | axis_kind |  | dateblock_oof | 6 | 122 | -0.000801586 | -0.000677255 | -0.000163987 | 0.873333333 | 1.000000000 | 1.000000000 | 0.620000000 | -0.000637598 | 0.000325185 | True | -0.000000000 | -0.000810051 | -0.001594706 |
| no_diary_global | leave_one_family | diary_global | subject_oof | 9 | 158 | -0.001694655 | -0.001594223 | -0.000634605 | 0.871666667 | 1.000000000 | 1.000000000 | 0.615000000 | -0.001060050 | 0.000557914 | True | -0.000845903 | -0.000584999 | -0.003653064 |
| no_diary_global | leave_one_family | diary_global | dateblock_oof | 9 | 158 | -0.001086246 | -0.001006074 | -0.000149277 | 0.853333333 | 1.000000000 | 1.000000000 | 0.560000000 | -0.000936969 | 0.000432706 | False | -0.000640876 | -0.000343132 | -0.002274729 |
| only_social_comm | family_only | social_comm | dateblock_oof | 1 | 24 | -0.000200674 | -0.000182512 | -0.000043523 | 0.853333333 | 1.000000000 | 1.000000000 | 0.560000000 | -0.000157151 | 0.000085163 | False | -0.000000000 | 0.000000000 | -0.000602022 |
| only_routine_calendar | family_only | routine_calendar | subject_oof | 1 | 24 | -0.000322375 | -0.000303410 | -0.000121868 | 0.843333333 | 1.000000000 | 0.990000000 | 0.540000000 | -0.000200507 | 0.000144189 | False | 0.000000000 | 0.000000000 | -0.000967125 |
| q12_only | target_ablation |  | dateblock_oof | 3 | 70 | -0.000483643 | -0.000441849 | -0.000101817 | 0.840000000 | 0.990000000 | 0.995000000 | 0.535000000 | -0.000381825 | 0.000304361 | False | -0.000640876 | -0.000810051 | 0.000000000 |
| q12_only | target_ablation |  | subject_oof | 3 | 70 | -0.000635952 | -0.000589532 | -0.000192051 | 0.838333333 | 1.000000000 | 0.990000000 | 0.525000000 | -0.000443901 | 0.000442937 | False | -0.000845903 | -0.001061952 | 0.000000000 |
| only_social_comm | family_only | social_comm | subject_oof | 1 | 24 | -0.000259427 | -0.000252034 | -0.000085585 | 0.826666667 | 1.000000000 | 1.000000000 | 0.480000000 | -0.000173842 | 0.000089218 | False | 0.000000000 | 0.000000000 | -0.000778281 |
| only_routine_calendar | family_only | routine_calendar | dateblock_oof | 1 | 24 | -0.000234101 | -0.000223255 | -0.000074028 | 0.821666667 | 0.995000000 | 0.980000000 | 0.490000000 | -0.000160073 | 0.000148693 | False | -0.000000000 | 0.000000000 | -0.000702304 |
| only_media_game | family_only | media_game | subject_oof | 1 | 24 | -0.000195000 | -0.000310740 | -0.000113253 | 0.616666667 | 0.950000000 | 0.885000000 | 0.015000000 | -0.000081746 | 0.000323540 | False | 0.000000000 | -0.000584999 | 0.000000000 |
| only_cognitive_money | family_only | cognitive_money | subject_oof | 1 | 24 | -0.000148897 | -0.000216268 | -0.000105973 | 0.603333333 | 0.935000000 | 0.675000000 | 0.200000000 | -0.000042924 | 0.000253216 | False | 0.000000000 | 0.000000000 | -0.000446691 |
| only_media_game | family_only | media_game | dateblock_oof | 1 | 24 | -0.000114377 | -0.000239399 | -0.000071515 | 0.573333333 | 0.855000000 | 0.855000000 | 0.010000000 | -0.000042862 | 0.000336312 | False | -0.000000000 | -0.000343132 | 0.000000000 |
| only_cognitive_money | family_only | cognitive_money | dateblock_oof | 1 | 24 | -0.000037996 | -0.000108683 | -0.000033574 | 0.521666667 | 0.695000000 | 0.690000000 | 0.180000000 | -0.000004422 | 0.000284752 | False | -0.000000000 | 0.000000000 | -0.000113989 |
| inverse_full_qsleep_m080 | inverse_control |  | dateblock_oof | 12 | 201 | 0.001176547 | -0.000041670 | 0.000224053 | 0.046666667 | 0.000000000 | 0.000000000 | 0.140000000 | 0.000952494 | 0.001809842 | False | 0.000540670 | 0.000720627 | 0.002268343 |
| inverse_full_qsleep_m080 | inverse_control |  | subject_oof | 12 | 201 | 0.001682720 | 0.000106912 | 0.000607473 | 0.036666667 | 0.000000000 | 0.000000000 | 0.110000000 | 0.001075247 | 0.002385707 | False | 0.000706687 | 0.000923524 | 0.003417949 |

## Target Detail

| candidate_id | variant_type | split | target | target_delta |
| --- | --- | --- | --- | --- |
| full_qsleep | primary | dateblock_oof | Q1 | -0.000640876 |
| full_qsleep | primary | dateblock_oof | Q2 | -0.000810051 |
| full_qsleep | primary | dateblock_oof | Q3 | -0.002637132 |
| full_qsleep | primary | subject_oof | Q1 | -0.000845903 |
| full_qsleep | primary | subject_oof | Q2 | -0.001061952 |
| full_qsleep | primary | subject_oof | Q3 | -0.004089009 |
| inverse_full_qsleep_m080 | inverse_control | dateblock_oof | Q1 | 0.000540670 |
| inverse_full_qsleep_m080 | inverse_control | dateblock_oof | Q2 | 0.000720627 |
| inverse_full_qsleep_m080 | inverse_control | dateblock_oof | Q3 | 0.002268343 |
| inverse_full_qsleep_m080 | inverse_control | subject_oof | Q1 | 0.000706687 |
| inverse_full_qsleep_m080 | inverse_control | subject_oof | Q2 | 0.000923524 |
| inverse_full_qsleep_m080 | inverse_control | subject_oof | Q3 | 0.003417949 |
| jepa_only | axis_kind | dateblock_oof | Q1 | -0.000640876 |
| jepa_only | axis_kind | dateblock_oof | Q2 | 0.000000000 |
| jepa_only | axis_kind | dateblock_oof | Q3 | -0.001766210 |
| jepa_only | axis_kind | subject_oof | Q1 | -0.000845903 |
| jepa_only | axis_kind | subject_oof | Q2 | 0.000000000 |
| jepa_only | axis_kind | subject_oof | Q3 | -0.002945420 |
| no_bedtime_phone | leave_one_family | dateblock_oof | Q1 | -0.000640876 |
| no_bedtime_phone | leave_one_family | dateblock_oof | Q2 | -0.000810051 |
| no_bedtime_phone | leave_one_family | dateblock_oof | Q3 | -0.002322154 |
| no_bedtime_phone | leave_one_family | subject_oof | Q1 | -0.000845903 |
| no_bedtime_phone | leave_one_family | subject_oof | Q2 | -0.001061952 |
| no_bedtime_phone | leave_one_family | subject_oof | Q3 | -0.003701176 |
| no_cognitive_money | leave_one_family | dateblock_oof | Q1 | -0.000640876 |
| no_cognitive_money | leave_one_family | dateblock_oof | Q2 | -0.000810051 |
| no_cognitive_money | leave_one_family | dateblock_oof | Q3 | -0.002514531 |
| no_cognitive_money | leave_one_family | subject_oof | Q1 | -0.000845903 |
| no_cognitive_money | leave_one_family | subject_oof | Q2 | -0.001061952 |
| no_cognitive_money | leave_one_family | subject_oof | Q3 | -0.003868215 |
| no_diary_global | leave_one_family | dateblock_oof | Q1 | -0.000640876 |
| no_diary_global | leave_one_family | dateblock_oof | Q2 | -0.000343132 |
| no_diary_global | leave_one_family | dateblock_oof | Q3 | -0.002274729 |
| no_diary_global | leave_one_family | subject_oof | Q1 | -0.000845903 |
| no_diary_global | leave_one_family | subject_oof | Q2 | -0.000584999 |
| no_diary_global | leave_one_family | subject_oof | Q3 | -0.003653064 |
| no_media_game | leave_one_family | dateblock_oof | Q1 | -0.000640876 |
| no_media_game | leave_one_family | dateblock_oof | Q2 | -0.000550803 |
| no_media_game | leave_one_family | dateblock_oof | Q3 | -0.002637132 |
| no_media_game | leave_one_family | subject_oof | Q1 | -0.000845903 |
| no_media_game | leave_one_family | subject_oof | Q2 | -0.000588885 |
| no_media_game | leave_one_family | subject_oof | Q3 | -0.004089009 |
| no_mobility_context | leave_one_family | dateblock_oof | Q1 | -0.000000000 |
| no_mobility_context | leave_one_family | dateblock_oof | Q2 | -0.000810051 |
| no_mobility_context | leave_one_family | dateblock_oof | Q3 | -0.002103412 |
| no_mobility_context | leave_one_family | subject_oof | Q1 | 0.000000000 |
| no_mobility_context | leave_one_family | subject_oof | Q2 | -0.001061952 |
| no_mobility_context | leave_one_family | subject_oof | Q3 | -0.003319729 |
| no_routine_calendar | leave_one_family | dateblock_oof | Q1 | -0.000640876 |
| no_routine_calendar | leave_one_family | dateblock_oof | Q2 | -0.000810051 |
| no_routine_calendar | leave_one_family | dateblock_oof | Q3 | -0.002249513 |
| no_routine_calendar | leave_one_family | subject_oof | Q1 | -0.000845903 |
| no_routine_calendar | leave_one_family | subject_oof | Q2 | -0.001061952 |
| no_routine_calendar | leave_one_family | subject_oof | Q3 | -0.003526670 |
| no_social_comm | leave_one_family | dateblock_oof | Q1 | -0.000640876 |
| no_social_comm | leave_one_family | dateblock_oof | Q2 | -0.000810051 |
| no_social_comm | leave_one_family | dateblock_oof | Q3 | -0.002295193 |
| no_social_comm | leave_one_family | subject_oof | Q1 | -0.000845903 |
| no_social_comm | leave_one_family | subject_oof | Q2 | -0.001061952 |
| no_social_comm | leave_one_family | subject_oof | Q3 | -0.003649973 |
| nonjepa_only | axis_kind | dateblock_oof | Q1 | -0.000000000 |
| nonjepa_only | axis_kind | dateblock_oof | Q2 | -0.000810051 |
| nonjepa_only | axis_kind | dateblock_oof | Q3 | -0.001594706 |
| nonjepa_only | axis_kind | subject_oof | Q1 | 0.000000000 |
| nonjepa_only | axis_kind | subject_oof | Q2 | -0.001061952 |
| nonjepa_only | axis_kind | subject_oof | Q3 | -0.002582287 |
| only_bedtime_phone | family_only | dateblock_oof | Q1 | -0.000000000 |
| only_bedtime_phone | family_only | dateblock_oof | Q2 | 0.000000000 |
| only_bedtime_phone | family_only | dateblock_oof | Q3 | -0.000828003 |
| only_bedtime_phone | family_only | subject_oof | Q1 | 0.000000000 |
| only_bedtime_phone | family_only | subject_oof | Q2 | 0.000000000 |
| only_bedtime_phone | family_only | subject_oof | Q3 | -0.001134886 |
| only_cognitive_money | family_only | dateblock_oof | Q1 | -0.000000000 |
| only_cognitive_money | family_only | dateblock_oof | Q2 | 0.000000000 |
| only_cognitive_money | family_only | dateblock_oof | Q3 | -0.000113989 |
| only_cognitive_money | family_only | subject_oof | Q1 | 0.000000000 |
| only_cognitive_money | family_only | subject_oof | Q2 | 0.000000000 |
| only_cognitive_money | family_only | subject_oof | Q3 | -0.000446691 |
| only_diary_global | family_only | dateblock_oof | Q1 | -0.000000000 |
| only_diary_global | family_only | dateblock_oof | Q2 | -0.000550803 |

## Null Mode Summary

| candidate_id | split | mode | n | best | q20 | median |
| --- | --- | --- | --- | --- | --- | --- |
| full_qsleep | dateblock_oof | dateblock | 200 | -0.001788179 | -0.001317691 | -0.001124702 |
| full_qsleep | dateblock_oof | row | 200 | -0.000772869 | -0.000128680 | 0.000096074 |
| full_qsleep | dateblock_oof | subject | 200 | -0.000800577 | -0.000229764 | 0.000021942 |
| full_qsleep | subject_oof | dateblock | 200 | -0.002301571 | -0.001928038 | -0.001750807 |
| full_qsleep | subject_oof | row | 200 | -0.000852671 | -0.000127491 | 0.000084310 |
| full_qsleep | subject_oof | subject | 200 | -0.001607896 | -0.000878238 | -0.000606002 |
| inverse_full_qsleep_m080 | dateblock_oof | dateblock | 200 | 0.000585720 | 0.000862991 | 0.001003371 |
| inverse_full_qsleep_m080 | dateblock_oof | row | 200 | -0.000603697 | -0.000112881 | 0.000078149 |
| inverse_full_qsleep_m080 | dateblock_oof | subject | 200 | -0.000633296 | -0.000096454 | 0.000100478 |
| inverse_full_qsleep_m080 | subject_oof | dateblock | 200 | 0.000986570 | 0.001354462 | 0.001477896 |
| inverse_full_qsleep_m080 | subject_oof | row | 200 | -0.000702987 | -0.000148758 | 0.000070313 |
| inverse_full_qsleep_m080 | subject_oof | subject | 200 | 0.000039854 | 0.000341968 | 0.000605607 |
| jepa_only | dateblock_oof | dateblock | 200 | -0.001033190 | -0.000754039 | -0.000610910 |
| jepa_only | dateblock_oof | row | 200 | -0.000440088 | -0.000165034 | 0.000020638 |
| jepa_only | dateblock_oof | subject | 200 | -0.000531369 | -0.000187027 | -0.000018371 |
| jepa_only | subject_oof | dateblock | 200 | -0.001558485 | -0.001250859 | -0.001093661 |
| jepa_only | subject_oof | row | 200 | -0.000547382 | -0.000207033 | 0.000004375 |
| jepa_only | subject_oof | subject | 200 | -0.001062345 | -0.000683264 | -0.000511331 |
| no_bedtime_phone | dateblock_oof | dateblock | 200 | -0.001627250 | -0.001259471 | -0.001127888 |
| no_bedtime_phone | dateblock_oof | row | 200 | -0.001242026 | -0.000205085 | 0.000016280 |
| no_bedtime_phone | dateblock_oof | subject | 200 | -0.000785165 | -0.000258025 | 0.000009577 |
| no_bedtime_phone | subject_oof | dateblock | 200 | -0.002230897 | -0.001900311 | -0.001713692 |
| no_bedtime_phone | subject_oof | row | 200 | -0.000672832 | -0.000191712 | 0.000033641 |
| no_bedtime_phone | subject_oof | subject | 200 | -0.001360483 | -0.000826445 | -0.000590993 |
| no_cognitive_money | dateblock_oof | dateblock | 200 | -0.001417934 | -0.001241564 | -0.001083649 |
| no_cognitive_money | dateblock_oof | row | 200 | -0.000983343 | -0.000232486 | 0.000072612 |
| no_cognitive_money | dateblock_oof | subject | 200 | -0.000646726 | -0.000220811 | -0.000034391 |
| no_cognitive_money | subject_oof | dateblock | 200 | -0.002201797 | -0.001833307 | -0.001661940 |
| no_cognitive_money | subject_oof | row | 200 | -0.000797505 | -0.000211334 | 0.000055136 |
| no_cognitive_money | subject_oof | subject | 200 | -0.001402833 | -0.000816147 | -0.000572537 |
| no_diary_global | dateblock_oof | dateblock | 200 | -0.001518952 | -0.001211972 | -0.001054383 |
| no_diary_global | dateblock_oof | row | 200 | -0.000910793 | -0.000174458 | 0.000065150 |
| no_diary_global | dateblock_oof | subject | 200 | -0.000686179 | -0.000230932 | 0.000009044 |
| no_diary_global | subject_oof | dateblock | 200 | -0.002252570 | -0.001816872 | -0.001650182 |
| no_diary_global | subject_oof | row | 200 | -0.000798490 | -0.000239523 | -0.000012370 |
| no_diary_global | subject_oof | subject | 200 | -0.001262563 | -0.000843496 | -0.000618145 |
| no_media_game | dateblock_oof | dateblock | 200 | -0.001405281 | -0.001049004 | -0.000888809 |
| no_media_game | dateblock_oof | row | 200 | -0.000629494 | -0.000152921 | 0.000083719 |
| no_media_game | dateblock_oof | subject | 200 | -0.000762873 | -0.000243255 | 0.000001366 |
| no_media_game | subject_oof | dateblock | 200 | -0.002072491 | -0.001638476 | -0.001486685 |
| no_media_game | subject_oof | row | 200 | -0.000641273 | -0.000145911 | 0.000107484 |
| no_media_game | subject_oof | subject | 200 | -0.001276667 | -0.000782156 | -0.000572100 |
| no_mobility_context | dateblock_oof | dateblock | 200 | -0.001501262 | -0.001003768 | -0.000857366 |
| no_mobility_context | dateblock_oof | row | 200 | -0.000789522 | -0.000219889 | 0.000045590 |
| no_mobility_context | dateblock_oof | subject | 200 | -0.000602032 | -0.000168171 | 0.000003369 |
| no_mobility_context | subject_oof | dateblock | 200 | -0.001810249 | -0.001503781 | -0.001361200 |
| no_mobility_context | subject_oof | row | 200 | -0.000787864 | -0.000250274 | -0.000020859 |
| no_mobility_context | subject_oof | subject | 200 | -0.001170401 | -0.000663103 | -0.000488583 |
| no_routine_calendar | dateblock_oof | dateblock | 200 | -0.001537737 | -0.001172879 | -0.001019803 |
| no_routine_calendar | dateblock_oof | row | 200 | -0.000768523 | -0.000189287 | 0.000026235 |
| no_routine_calendar | dateblock_oof | subject | 200 | -0.000584670 | -0.000158999 | 0.000029069 |
| no_routine_calendar | subject_oof | dateblock | 200 | -0.002365064 | -0.001741499 | -0.001577969 |
| no_routine_calendar | subject_oof | row | 200 | -0.000695608 | -0.000135589 | 0.000106146 |
| no_routine_calendar | subject_oof | subject | 200 | -0.001168682 | -0.000808547 | -0.000562756 |
| no_social_comm | dateblock_oof | dateblock | 200 | -0.001648298 | -0.001183179 | -0.001021303 |
| no_social_comm | dateblock_oof | row | 200 | -0.000748462 | -0.000211979 | 0.000048229 |
| no_social_comm | dateblock_oof | subject | 200 | -0.000744979 | -0.000183704 | 0.000040503 |
| no_social_comm | subject_oof | dateblock | 200 | -0.002152591 | -0.001824274 | -0.001657792 |
| no_social_comm | subject_oof | row | 200 | -0.000697584 | -0.000118752 | 0.000122212 |
| no_social_comm | subject_oof | subject | 200 | -0.001219411 | -0.000783161 | -0.000577846 |
| nonjepa_only | dateblock_oof | dateblock | 200 | -0.001126771 | -0.000868254 | -0.000731955 |
| nonjepa_only | dateblock_oof | row | 200 | -0.000589998 | -0.000218321 | -0.000017088 |
| nonjepa_only | dateblock_oof | subject | 200 | -0.000468427 | -0.000177980 | -0.000018864 |
| nonjepa_only | subject_oof | dateblock | 200 | -0.001519604 | -0.001260833 | -0.001142879 |
| nonjepa_only | subject_oof | row | 200 | -0.000815224 | -0.000181735 | 0.000018794 |
| nonjepa_only | subject_oof | subject | 200 | -0.000984122 | -0.000540888 | -0.000326490 |
| only_bedtime_phone | dateblock_oof | dateblock | 200 | -0.000254967 | -0.000138414 | -0.000076501 |
| only_bedtime_phone | dateblock_oof | row | 200 | -0.000278402 | -0.000096707 | 0.000012644 |
| only_bedtime_phone | dateblock_oof | subject | 200 | -0.000218661 | -0.000089524 | -0.000010387 |
| only_bedtime_phone | subject_oof | dateblock | 200 | -0.000355462 | -0.000238225 | -0.000171234 |
| only_bedtime_phone | subject_oof | row | 200 | -0.000279622 | -0.000098604 | 0.000001187 |
| only_bedtime_phone | subject_oof | subject | 200 | -0.000367053 | -0.000205863 | -0.000121696 |
| only_cognitive_money | dateblock_oof | dateblock | 200 | -0.000288138 | -0.000148720 | -0.000092550 |
| only_cognitive_money | dateblock_oof | row | 200 | -0.000322748 | -0.000063437 | 0.000016336 |
| only_cognitive_money | dateblock_oof | subject | 200 | -0.000241580 | -0.000072894 | -0.000000411 |
| only_cognitive_money | subject_oof | dateblock | 200 | -0.000402113 | -0.000271563 | -0.000211077 |
| only_cognitive_money | subject_oof | row | 200 | -0.000246482 | -0.000067462 | -0.000003482 |
| only_cognitive_money | subject_oof | subject | 200 | -0.000316357 | -0.000186780 | -0.000100829 |
| only_diary_global | dateblock_oof | dateblock | 200 | -0.000603630 | -0.000361430 | -0.000226292 |
| only_diary_global | dateblock_oof | row | 200 | -0.000496953 | -0.000126896 | 0.000002955 |
| only_diary_global | dateblock_oof | subject | 200 | -0.000536633 | -0.000150390 | 0.000006836 |
| only_diary_global | subject_oof | dateblock | 200 | -0.000875629 | -0.000506102 | -0.000390492 |
| only_diary_global | subject_oof | row | 200 | -0.000470313 | -0.000185275 | 0.000001572 |
| only_diary_global | subject_oof | subject | 200 | -0.000615561 | -0.000247450 | -0.000115473 |
| only_media_game | dateblock_oof | dateblock | 200 | -0.000450690 | -0.000309304 | -0.000257069 |
| only_media_game | dateblock_oof | row | 200 | -0.000419925 | -0.000091122 | 0.000002771 |
| only_media_game | dateblock_oof | subject | 200 | -0.000268875 | -0.000086679 | -0.000006376 |
| only_media_game | subject_oof | dateblock | 200 | -0.000518540 | -0.000384659 | -0.000329498 |
| only_media_game | subject_oof | row | 200 | -0.000425882 | -0.000105707 | 0.000001113 |
| only_media_game | subject_oof | subject | 200 | -0.000365195 | -0.000159101 | -0.000058740 |
| only_mobility_context | dateblock_oof | dateblock | 200 | -0.000736685 | -0.000490777 | -0.000359986 |
| only_mobility_context | dateblock_oof | row | 200 | -0.000577925 | -0.000169104 | 0.000003896 |
| only_mobility_context | dateblock_oof | subject | 200 | -0.000493158 | -0.000161355 | -0.000005524 |
| only_mobility_context | subject_oof | dateblock | 200 | -0.001034364 | -0.000803765 | -0.000676345 |
| only_mobility_context | subject_oof | row | 200 | -0.000602506 | -0.000112376 | 0.000034066 |
| only_mobility_context | subject_oof | subject | 200 | -0.000760933 | -0.000469746 | -0.000293107 |
| only_routine_calendar | dateblock_oof | dateblock | 200 | -0.000382794 | -0.000286433 | -0.000236809 |
| only_routine_calendar | dateblock_oof | row | 200 | -0.000261623 | -0.000072676 | -0.000005280 |
| only_routine_calendar | dateblock_oof | subject | 200 | -0.000324427 | -0.000103499 | -0.000015244 |
| only_routine_calendar | subject_oof | dateblock | 200 | -0.000466564 | -0.000375590 | -0.000314189 |

## Decision

At least one policy beats train matched nulls on both split views. It should be cross-checked against E277 test matched-placebo failure before materialization.

## Next Action

Do not make another q-sleep submission. Train a target that directly predicts row-alignment or candidate-vs-shuffle benefit, especially for JEPA/mobility/Q3, then rerun E277.

## Files

- `e278_train_row_alignment_null_summary.csv`
- `e278_train_row_alignment_null_target_detail.csv`
- `e278_train_row_alignment_null_distribution.csv`
