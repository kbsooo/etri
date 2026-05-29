# E133 Local-Safety Co-location Atlas

## Question

After E132 rejected donor-free E95 tangent moves, where do local combo-gradient reward and transfer-tail safety separate at the cell level?

## Method

- Compute E95 combo-set gradients for all, leave-one-combo, and single-combo contexts.
- Convert squared gradient into a local-reward field.
- Build a transfer-safe field from veto-null direction, low-adverse hard-tail exposure, and E127/E130 density rank.
- Measure whether local reward mass lies inside safe density and whether hidden-block-heldout categorical views can predict the co-located field.
- No submission is generated.

## Gradient Diagnostics

| context | grad_mean_abs | grad_max_abs | veto_null_frac | low_adverse75_frac | co_nonzero |
| --- | --- | --- | --- | --- | --- |
| all | 0.000003874 | 0.000081125 | 0.671428571 | 0.749714286 | 1174 |
| loo_inverse_top | 0.000003856 | 0.000040285 | 0.732000000 | 0.771428571 | 1280 |
| loo_raw05_compatible | 0.000004302 | 0.000081730 | 0.664571429 | 0.749714286 | 1163 |
| loo_all_sign | 0.000005682 | 0.000121361 | 0.659428571 | 0.749714286 | 1154 |
| inverse_top | 0.000009372 | 0.000162806 | 0.654857143 | 0.749714286 | 1146 |
| raw05_compatible | 0.000004250 | 0.000079916 | 0.704000000 | 0.749714286 | 1231 |
| all_sign | 0.000004645 | 0.000020304 | 0.772000000 | 0.802285714 | 1350 |

## Co-location Summary

| context | local_safe_cosine | local_mass_in_vetonull_density70 | local_top50_veto_null_frac | local_top50_density70_frac | local_top50_q2s3_frac | local_top50_e101_active_frac | co_top50_q2s3_frac | co_top50_e101_active_frac | co_nonzero_cells | co_total_raw |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_sign | 0.473431108 | 0.161830365 | 0.920000000 | 0.200000000 | 0.440000000 | 0.040000000 | 0.020000000 | 0.000000000 | 1350 | 0.000000018 |
| loo_inverse_top | 0.341372012 | 0.132611158 | 0.740000000 | 0.360000000 | 0.180000000 | 0.000000000 | 0.060000000 | 0.000000000 | 1280 | 0.000000013 |
| raw05_compatible | 0.184346689 | 0.122907017 | 0.620000000 | 0.400000000 | 0.120000000 | 0.020000000 | 0.080000000 | 0.000000000 | 1231 | 0.000000020 |
| loo_all_sign | 0.152126971 | 0.082161239 | 0.560000000 | 0.360000000 | 0.160000000 | 0.080000000 | 0.080000000 | 0.000000000 | 1154 | 0.000000034 |
| inverse_top | 0.187171140 | 0.081766247 | 0.640000000 | 0.300000000 | 0.180000000 | 0.040000000 | 0.120000000 | 0.000000000 | 1146 | 0.000000087 |
| all | 0.150317733 | 0.077078915 | 0.620000000 | 0.340000000 | 0.100000000 | 0.040000000 | 0.040000000 | 0.000000000 | 1174 | 0.000000015 |
| loo_raw05_compatible | 0.164443067 | 0.072270756 | 0.640000000 | 0.320000000 | 0.100000000 | 0.020000000 | 0.020000000 | 0.000000000 | 1163 | 0.000000019 |

## Best Hidden-Block CV Category Views

| context | view | cosine | spearman | js_divergence | truth_mass_in_pred_top50 | top50_overlap |
| --- | --- | --- | --- | --- | --- | --- |
| all_sign | subject_target | 0.532639198 | 0.305902284 | 0.240700319 | 0.048280367 | 0.100000000 |
| all_sign | target_tail | 0.534039644 | 0.265543224 | 0.244939975 | 0.048969335 | 0.060000000 |
| all_sign | target_context_tail_e72bin | 0.519052291 | 0.345556838 | 0.246508719 | 0.063958968 | 0.040000000 |
| loo_inverse_top | target_tail | 0.338701372 | 0.223950575 | 0.286884781 | 0.042529998 | 0.060000000 |
| loo_inverse_top | target_context_tail | 0.335271962 | 0.231794898 | 0.290487726 | 0.046597826 | 0.060000000 |
| loo_inverse_top | target_context_tail_e72bin | 0.310905252 | 0.372832813 | 0.290897086 | 0.069445369 | 0.100000000 |
| inverse_top | target_context_tail_e72bin | 0.160525989 | 0.430169853 | 0.368289879 | 0.076095991 | 0.120000000 |
| loo_raw05_compatible | target_context_tail_e72bin | 0.111120726 | 0.468892103 | 0.380966551 | 0.055260423 | 0.100000000 |
| raw05_compatible | subject_context_target | 0.150237187 | 0.094482997 | 0.381912003 | 0.139804215 | 0.220000000 |
| raw05_compatible | target_tail | 0.158565147 | 0.104436577 | 0.382055987 | 0.026154656 | 0.020000000 |
| inverse_top | target_tail | 0.169748268 | 0.104701055 | 0.382897331 | 0.039377308 | 0.100000000 |
| all | target_context_tail_e72bin | 0.093314883 | 0.466855299 | 0.384686285 | 0.037565198 | 0.080000000 |
| inverse_top | target | 0.169380417 | 0.069133869 | 0.385158230 | 0.057834182 | 0.120000000 |
| raw05_compatible | target | 0.157249980 | 0.019968447 | 0.386971673 | 0.025684254 | 0.020000000 |
| loo_all_sign | target_context_tail_e72bin | 0.105034423 | 0.454033141 | 0.387291790 | 0.050500203 | 0.080000000 |
| all | target_tail | 0.109508329 | 0.140215564 | 0.390278084 | 0.024997965 | 0.020000000 |
| all | target | 0.108900867 | 0.093496013 | 0.393285606 | 0.026119386 | 0.020000000 |
| loo_raw05_compatible | target_tail | 0.125218712 | 0.130194084 | 0.393971712 | 0.039127373 | 0.060000000 |
| loo_raw05_compatible | target | 0.124717874 | 0.087176899 | 0.396501356 | 0.036155659 | 0.040000000 |
| loo_all_sign | target_tail | 0.120546653 | 0.124009727 | 0.396561126 | 0.027676406 | 0.080000000 |
| loo_all_sign | target | 0.120234253 | 0.089540861 | 0.398222678 | 0.034961225 | 0.120000000 |

## Top Co-located Cells

| context | field | rank | score | target | subject_id | hidden_block_id | context_type | pos_bin | e101_active | target_is_q2s3 | density_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | co_vetonull_density | 1 | 0.000000003 | Q3 | id01 | id01_b2 | between_train_runs | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 2 | 0.000000001 | S2 | id01 | id01_b4 | after_train_run | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 3 | 0.000000001 | S2 | id01 | id01_b4 | after_train_run | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 4 | 0.000000000 | S3 | id01 | id01_b2 | between_train_runs | interior | False | True | 0.184815876 |
| all | co_vetonull_density | 5 | 0.000000000 | Q1 | id05 | id05_b2 | between_train_runs | right_edge | False | False | 0.421013653 |
| all | co_vetonull_density | 6 | 0.000000000 | S2 | id01 | id01_b4 | after_train_run | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 7 | 0.000000000 | Q3 | id10 | id10_b4 | after_train_run | interior | False | False | 0.420098730 |
| all | co_vetonull_density | 8 | 0.000000000 | Q3 | id03 | id03_b2 | between_train_runs | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 9 | 0.000000000 | Q1 | id07 | id07_b2 | between_train_runs | right_edge | False | False | 0.436729674 |
| all | co_vetonull_density | 10 | 0.000000000 | Q3 | id02 | id02_b4 | after_train_run | near_edge | False | False | 0.439978925 |
| all | co_vetonull_density | 11 | 0.000000000 | S1 | id09 | id09_b4 | after_train_run | near_edge | False | False | 0.482290217 |
| all | co_vetonull_density | 12 | 0.000000000 | Q1 | id08 | id08_b10 | between_train_runs | near_edge | False | False | 0.421013653 |
| all | co_vetonull_density | 13 | 0.000000000 | Q1 | id08 | id08_b4 | between_train_runs | near_edge | False | False | 0.428766271 |
| all | co_vetonull_density | 14 | 0.000000000 | Q3 | id01 | id01_b4 | after_train_run | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 15 | 0.000000000 | Q3 | id02 | id02_b2 | between_train_runs | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 16 | 0.000000000 | Q3 | id07 | id07_b4 | after_train_run | near_edge | False | False | 0.421013653 |
| all | co_vetonull_density | 17 | 0.000000000 | Q3 | id01 | id01_b2 | between_train_runs | near_edge | False | False | 0.516738540 |
| all | co_vetonull_density | 18 | 0.000000000 | Q3 | id09 | id09_b2 | between_train_runs | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 19 | 0.000000000 | Q3 | id02 | id02_b4 | after_train_run | interior | False | False | 0.485027667 |
| all | co_vetonull_density | 20 | 0.000000000 | S2 | id10 | id10_b4 | after_train_run | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 21 | 0.000000000 | Q1 | id01 | id01_b4 | after_train_run | left_edge | False | False | 0.421013653 |
| all | co_vetonull_density | 22 | 0.000000000 | S1 | id09 | id09_b2 | between_train_runs | interior | False | False | 0.423413006 |
| all | co_vetonull_density | 23 | 0.000000000 | Q3 | id09 | id09_b2 | between_train_runs | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 24 | 0.000000000 | Q1 | id01 | id01_b2 | between_train_runs | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 25 | 0.000000000 | Q3 | id02 | id02_b4 | after_train_run | interior | False | False | 0.515168518 |
| all | co_vetonull_density | 26 | 0.000000000 | Q1 | id09 | id09_b2 | between_train_runs | interior | False | False | 0.431883311 |
| all | co_vetonull_density | 27 | 0.000000000 | Q1 | id06 | id06_b4 | between_train_runs | left_edge | False | False | 0.421479360 |
| all | co_vetonull_density | 28 | 0.000000000 | Q3 | id01 | id01_b2 | between_train_runs | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 29 | 0.000000000 | Q3 | id01 | id01_b4 | after_train_run | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 30 | 0.000000000 | Q1 | id02 | id02_b2 | between_train_runs | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 31 | 0.000000000 | Q1 | id01 | id01_b2 | between_train_runs | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 32 | 0.000000000 | S2 | id10 | id10_b4 | after_train_run | left_edge | False | False | 0.528187113 |
| all | co_vetonull_density | 33 | 0.000000000 | Q1 | id10 | id10_b2 | between_train_runs | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 34 | 0.000000000 | S4 | id10 | id10_b4 | after_train_run | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 35 | 0.000000000 | Q1 | id05 | id05_b4 | between_train_runs | left_edge | False | False | 0.421013653 |
| all | co_vetonull_density | 36 | 0.000000000 | Q3 | id04 | id04_b6 | between_train_runs | near_edge | False | False | 0.421013653 |
| all | co_vetonull_density | 37 | 0.000000000 | S4 | id07 | id07_b2 | between_train_runs | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 38 | 0.000000000 | S4 | id03 | id03_b4 | after_train_run | left_edge | False | False | 0.421013653 |
| all | co_vetonull_density | 39 | 0.000000000 | Q3 | id07 | id07_b2 | between_train_runs | interior | False | False | 0.421013653 |
| all | co_vetonull_density | 40 | 0.000000000 | S1 | id05 | id05_b4 | between_train_runs | near_edge | False | False | 0.430204883 |

## Decision

No submission. This is an atlas for the next latent target, not a probability movement.
