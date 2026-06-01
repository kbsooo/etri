# H017 Joint Label x Public-Weight HS-JEPA

## Question

Can H012's hidden label posterior and H016's public cell-weight field be solved as one joint latent state?

## Selected Joint Configs

| q_prior_name | w_prior_name | ridge_mult | cap_mult |
| --- | --- | --- | --- |
| h012_public_posterior | h016_mean_weight | 0.100000000 | 8.000000000 |
| h012_public_posterior | h016_mean_weight | 0.100000000 | 12.000000000 |
| h012_public_posterior | h016_mean_weight | 0.100000000 | 25.000000000 |
| h012_public_posterior | h016_mean_weight | 0.100000000 | 50.000000000 |
| h012_public_posterior | h016_mean_weight | 0.100000000 | 0.000000000 |
| h012_public_posterior | h016_mean_weight | 0.300000000 | 8.000000000 |
| h012_public_posterior | h016_mean_weight | 0.300000000 | 12.000000000 |
| h012_public_posterior | h016_mean_weight | 0.300000000 | 25.000000000 |
| h012_public_posterior | h016_mean_weight | 0.300000000 | 50.000000000 |
| h012_public_posterior | h016_mean_weight | 0.300000000 | 0.000000000 |
| h012_public_posterior | h016_mean_weight | 1.000000000 | 8.000000000 |
| h012_public_posterior | h016_mean_weight | 1.000000000 | 12.000000000 |

## Top Joint Diagnostics

| q_prior_name | w_prior_name | ridge_mult | cap_mult | loo_mae | loo_p90_abs | loo_spearman | uniform_prior_mae | weight_eff_n | weight_top50_mass | q_prior_abs_move | w_prior_l1_move |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h012_public_posterior | h016_mean_weight | 0.100000000 | 8.000000000 | 0.000001044 | 0.000002071 | 1.000000000 | 0.000885430 | 1747.314135892 | 0.036267650 | 0.000000677 | 0.000000293 |
| h012_public_posterior | h016_mean_weight | 0.100000000 | 12.000000000 | 0.000001044 | 0.000002071 | 1.000000000 | 0.000885430 | 1747.314135892 | 0.036267650 | 0.000000677 | 0.000000293 |
| h012_public_posterior | h016_mean_weight | 0.100000000 | 25.000000000 | 0.000001044 | 0.000002071 | 1.000000000 | 0.000885430 | 1747.314135892 | 0.036267650 | 0.000000677 | 0.000000293 |
| h012_public_posterior | h016_mean_weight | 0.100000000 | 50.000000000 | 0.000001044 | 0.000002071 | 1.000000000 | 0.000885430 | 1747.314135892 | 0.036267650 | 0.000000677 | 0.000000293 |
| h012_public_posterior | h016_mean_weight | 0.100000000 | 0.000000000 | 0.000001044 | 0.000002071 | 1.000000000 | 0.000885430 | 1747.314135892 | 0.036267650 | 0.000000677 | 0.000000293 |
| h012_public_posterior | h016_mean_weight | 0.300000000 | 8.000000000 | 0.000001039 | 0.000002132 | 1.000000000 | 0.000885430 | 1747.314134441 | 0.036267652 | 0.000000245 | 0.000000108 |
| h012_public_posterior | h016_mean_weight | 0.300000000 | 12.000000000 | 0.000001039 | 0.000002132 | 1.000000000 | 0.000885430 | 1747.314134441 | 0.036267652 | 0.000000245 | 0.000000108 |
| h012_public_posterior | h016_mean_weight | 0.300000000 | 25.000000000 | 0.000001039 | 0.000002132 | 1.000000000 | 0.000885430 | 1747.314134441 | 0.036267652 | 0.000000245 | 0.000000108 |
| h012_public_posterior | h016_mean_weight | 0.300000000 | 50.000000000 | 0.000001039 | 0.000002132 | 1.000000000 | 0.000885430 | 1747.314134441 | 0.036267652 | 0.000000245 | 0.000000108 |
| h012_public_posterior | h016_mean_weight | 0.300000000 | 0.000000000 | 0.000001039 | 0.000002132 | 1.000000000 | 0.000885430 | 1747.314134441 | 0.036267652 | 0.000000245 | 0.000000108 |
| h012_public_posterior | h016_mean_weight | 1.000000000 | 8.000000000 | 0.000001040 | 0.000002151 | 1.000000000 | 0.000885430 | 1747.314133804 | 0.036267653 | 0.000000075 | 0.000000036 |
| h012_public_posterior | h016_mean_weight | 1.000000000 | 12.000000000 | 0.000001040 | 0.000002151 | 1.000000000 | 0.000885430 | 1747.314133804 | 0.036267653 | 0.000000075 | 0.000000036 |
| h012_public_posterior | h016_mean_weight | 1.000000000 | 25.000000000 | 0.000001040 | 0.000002151 | 1.000000000 | 0.000885430 | 1747.314133804 | 0.036267653 | 0.000000075 | 0.000000036 |
| h012_public_posterior | h016_mean_weight | 1.000000000 | 50.000000000 | 0.000001040 | 0.000002151 | 1.000000000 | 0.000885430 | 1747.314133804 | 0.036267653 | 0.000000075 | 0.000000036 |
| h012_public_posterior | h016_mean_weight | 1.000000000 | 0.000000000 | 0.000001040 | 0.000002151 | 1.000000000 | 0.000885430 | 1747.314133804 | 0.036267653 | 0.000000075 | 0.000000036 |
| h012_public_posterior | h016_mean_weight | 3.000000000 | 8.000000000 | 0.000001039 | 0.000002156 | 1.000000000 | 0.000885430 | 1747.314133470 | 0.036267653 | 0.000000024 | 0.000000015 |
| h012_public_posterior | h016_mean_weight | 3.000000000 | 12.000000000 | 0.000001039 | 0.000002156 | 1.000000000 | 0.000885430 | 1747.314133470 | 0.036267653 | 0.000000024 | 0.000000015 |
| h012_public_posterior | h016_mean_weight | 3.000000000 | 25.000000000 | 0.000001039 | 0.000002156 | 1.000000000 | 0.000885430 | 1747.314133470 | 0.036267653 | 0.000000024 | 0.000000015 |
| h012_public_posterior | h016_mean_weight | 3.000000000 | 50.000000000 | 0.000001039 | 0.000002156 | 1.000000000 | 0.000885430 | 1747.314133470 | 0.036267653 | 0.000000024 | 0.000000015 |
| h012_public_posterior | h016_mean_weight | 3.000000000 | 0.000000000 | 0.000001039 | 0.000002156 | 1.000000000 | 0.000885430 | 1747.314133470 | 0.036267653 | 0.000000024 | 0.000000015 |
| h012_public_posterior | h016_mean_weight | 0.030000000 | 8.000000000 | 0.000001119 | 0.000001873 | 1.000000000 | 0.000885430 | 1747.314139554 | 0.036267644 | 0.000001872 | 0.000000807 |
| h012_public_posterior | h016_mean_weight | 0.030000000 | 12.000000000 | 0.000001119 | 0.000001873 | 1.000000000 | 0.000885430 | 1747.314139554 | 0.036267644 | 0.000001872 | 0.000000807 |
| h012_public_posterior | h016_mean_weight | 0.030000000 | 25.000000000 | 0.000001119 | 0.000001873 | 1.000000000 | 0.000885430 | 1747.314139554 | 0.036267644 | 0.000001872 | 0.000000807 |
| h012_public_posterior | h016_mean_weight | 0.030000000 | 50.000000000 | 0.000001119 | 0.000001873 | 1.000000000 | 0.000885430 | 1747.314139554 | 0.036267644 | 0.000001872 | 0.000000807 |
| h012_public_posterior | h016_mean_weight | 0.030000000 | 0.000000000 | 0.000001119 | 0.000001873 | 1.000000000 | 0.000885430 | 1747.314139554 | 0.036267644 | 0.000001872 | 0.000000807 |

## Null Stress

Public deltas are permuted while the same submission loss-delta tensor is kept fixed.

| metric | direction | real | null_mean | null_p10 | null_p50 | null_p90 | real_percentile_vs_null | one_sided_p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| loo_mae | lower | 0.000001044 | 0.001678726 | 0.001411885 | 0.001672425 | 0.001949831 | 0.000000000 | 0.003322259 |
| loo_p90_abs | lower | 0.000002071 | 0.003578198 | 0.002739236 | 0.003553281 | 0.004328873 | 0.000000000 | 0.003322259 |
| loo_spearman | higher | 1.000000000 | -0.067042607 | -0.350375940 | -0.059398496 | 0.200902256 | 1.000000000 | 0.003322259 |
| loo_pearson | higher | 0.999999216 | -0.026087582 | -0.295160196 | -0.035841611 | 0.240832065 | 1.000000000 | 0.003322259 |
| known_fit_mae | lower | 0.000001024 | 0.001565503 | 0.001313123 | 0.001563529 | 0.001818391 | 0.000000000 | 0.003322259 |
| weight_eff_n | higher | 1747.314135892 | 1747.325155364 | 1747.319978753 | 1747.325420700 | 1747.329644202 | 0.003333333 | 0.996677741 |
| weight_top50_mass | lower | 0.036267650 | 0.036260496 | 0.036249301 | 0.036260948 | 0.036270679 | 0.786666667 | 0.787375415 |
| q_prior_abs_move | lower | 0.000000677 | 0.004130080 | 0.003144513 | 0.004179872 | 0.005083628 | 0.000000000 | 0.003322259 |

## Critical Read

- The top configs barely move `q` or `w` away from the priors. This is not evidence that a brand-new joint latent was discovered.
- The useful evidence is compatibility: `H012 public posterior + H016 diffuse public weights` already explains known public deltas almost exactly and far outside permutation nulls.
- Therefore H017 is best read as a posterior-completion test: H012 may not have moved far enough toward its own public posterior under the H016 public-weight field.

## Target Summary

| target | mean_weight | mean_q | mean_abs_logit_delta | mean_gain | h015_agree_rate | h016_agree_rate |
| --- | --- | --- | --- | --- | --- | --- |
| Q3 | 0.000565306 | 0.606364463 | 0.070726440 | 0.000000439 | 0.564000000 | 0.516000000 |
| S2 | 0.000580134 | 0.639981860 | 0.260524428 | 0.000000391 | 0.636000000 | 0.480000000 |
| S1 | 0.000581314 | 0.658566120 | 0.340704975 | 0.000000367 | 0.644000000 | 0.496000000 |
| S4 | 0.000575261 | 0.567064905 | 0.106395427 | 0.000000335 | 0.724000000 | 0.624000000 |
| S3 | 0.000563439 | 0.673788260 | 0.110609112 | 0.000000305 | 0.712000000 | 0.456000000 |
| Q1 | 0.000569972 | 0.493527969 | 0.123279819 | 0.000000284 | 0.624000000 | 0.556000000 |
| Q2 | 0.000564574 | 0.549236349 | 0.043822449 | 0.000000178 | 0.596000000 | 0.560000000 |

## Candidate Selection

| candidate_id | h017_decision | mode | target_subset | changed_cells | joint_delta_mean_vs_h012 | joint_delta_p90_vs_h012 | h015_joint_delta_mean | h016_joint_delta_mean | gain_vs_h015_under_joint | gain_vs_h016_under_joint | max_abs_prob_delta_vs_h012 | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| oracle_gain_all_k1650_a1 | joint_world_sensor | oracle_gain | all | 1650 | -0.000574501 | -0.000574481 | 0.000164654 | -0.000296289 | -0.000739155 | -0.000278212 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_oracle_gain_all_k1650_a1_53487040.csv |
| consensus_all_k1650_a1 | joint_world_sensor | consensus | all | 1650 | -0.000574297 | -0.000574279 | 0.000164654 | -0.000296289 | -0.000738951 | -0.000278008 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_consensus_all_k1650_a1_fa1c1ba2.csv |
| h016_gain_all_k1650_a1 | joint_world_sensor | h016_gain | all | 1650 | -0.000567898 | -0.000567879 | 0.000164654 | -0.000296289 | -0.000732552 | -0.000271609 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_h016_gain_all_k1650_a1_4b0c2462.csv |
| oracle_gain_all_k1400_a1 | joint_world_sensor | oracle_gain | all | 1400 | -0.000567729 | -0.000567715 | 0.000164654 | -0.000296289 | -0.000732383 | -0.000271440 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_oracle_gain_all_k1400_a1_001f63f1.csv |
| consensus_all_k1400_a1 | joint_world_sensor | consensus | all | 1400 | -0.000563608 | -0.000563595 | 0.000164654 | -0.000296289 | -0.000728262 | -0.000267319 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_consensus_all_k1400_a1_43b6c9f0.csv |
| oracle_gain_all_k1100_a1 | joint_world_sensor | oracle_gain | all | 1100 | -0.000548419 | -0.000548407 | 0.000164654 | -0.000296289 | -0.000713074 | -0.000252131 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_oracle_gain_all_k1100_a1_d95be141.csv |
| weight_shift_all_k1650_a1 | joint_world_sensor | weight_shift | all | 1650 | -0.000547779 | -0.000547762 | 0.000164654 | -0.000296289 | -0.000712433 | -0.000251490 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_weight_shift_all_k1650_a1_1b313da1.csv |
| oracle_gain_all_k1650_a1.25 | joint_world_sensor | oracle_gain | all | 1650 | -0.000539913 | -0.000539890 | 0.000164654 | -0.000296289 | -0.000704567 | -0.000243624 | 0.133128560 | hitl/h017_joint_label_weight_jepa/submission_h017_oracle_gain_all_k1650_a1.25_c65a7401.csv |
| consensus_all_k1650_a1.25 | joint_world_sensor | consensus | all | 1650 | -0.000539714 | -0.000539692 | 0.000164654 | -0.000296289 | -0.000704368 | -0.000243425 | 0.133128560 | hitl/h017_joint_label_weight_jepa/submission_h017_consensus_all_k1650_a1.25_1ff4a608.csv |
| oracle_gain_all_k1650_a0.75 | joint_world_sensor | oracle_gain | all | 1650 | -0.000539429 | -0.000539415 | 0.000164654 | -0.000296289 | -0.000704083 | -0.000243140 | 0.081420804 | hitl/h017_joint_label_weight_jepa/submission_h017_oracle_gain_all_k1650_a0.75_80c82e5a.csv |
| consensus_all_k1650_a0.75 | joint_world_sensor | consensus | all | 1650 | -0.000539233 | -0.000539219 | 0.000164654 | -0.000296289 | -0.000703887 | -0.000242944 | 0.081420804 | hitl/h017_joint_label_weight_jepa/submission_h017_consensus_all_k1650_a0.75_41b05b21.csv |
| h016_gain_all_k1650_a1.25 | joint_world_sensor | h016_gain | all | 1650 | -0.000533727 | -0.000533705 | 0.000164654 | -0.000296289 | -0.000698381 | -0.000237438 | 0.133128560 | hitl/h017_joint_label_weight_jepa/submission_h017_h016_gain_all_k1650_a1.25_8708e171.csv |
| oracle_gain_all_k1400_a1.25 | joint_world_sensor | oracle_gain | all | 1400 | -0.000533521 | -0.000533504 | 0.000164654 | -0.000296289 | -0.000698175 | -0.000237232 | 0.133128560 | hitl/h017_joint_label_weight_jepa/submission_h017_oracle_gain_all_k1400_a1.25_1b90cc5b.csv |
| h016_gain_all_k1650_a0.75 | joint_world_sensor | h016_gain | all | 1650 | -0.000533242 | -0.000533228 | 0.000164654 | -0.000296289 | -0.000697896 | -0.000236953 | 0.081420804 | hitl/h017_joint_label_weight_jepa/submission_h017_h016_gain_all_k1650_a0.75_9ae594b0.csv |
| oracle_gain_all_k1400_a0.75 | joint_world_sensor | oracle_gain | all | 1400 | -0.000533050 | -0.000533040 | 0.000164654 | -0.000296289 | -0.000697704 | -0.000236761 | 0.081420804 | hitl/h017_joint_label_weight_jepa/submission_h017_oracle_gain_all_k1400_a0.75_05873160.csv |
| h015_gain_all_k1650_a1 | joint_world_sensor | h015_gain | all | 1650 | -0.000530886 | -0.000530869 | 0.000164654 | -0.000296289 | -0.000695541 | -0.000234598 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_h015_gain_all_k1650_a1_13fd5e90.csv |
| consensus_all_k1400_a1.25 | joint_world_sensor | consensus | all | 1400 | -0.000529689 | -0.000529673 | 0.000164654 | -0.000296289 | -0.000694343 | -0.000233400 | 0.133128560 | hitl/h017_joint_label_weight_jepa/submission_h017_consensus_all_k1400_a1.25_526ebd5e.csv |
| consensus_all_k1400_a0.75 | joint_world_sensor | consensus | all | 1400 | -0.000529208 | -0.000529198 | 0.000164654 | -0.000296289 | -0.000693862 | -0.000232919 | 0.081420804 | hitl/h017_joint_label_weight_jepa/submission_h017_consensus_all_k1400_a0.75_43657549.csv |
| consensus_all_k1100_a1 | joint_world_sensor | consensus | all | 1100 | -0.000527242 | -0.000527230 | 0.000164654 | -0.000296289 | -0.000691896 | -0.000230953 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_consensus_all_k1100_a1_d597dd75.csv |
| h016_gain_all_k1400_a1 | joint_world_sensor | h016_gain | all | 1400 | -0.000518092 | -0.000518077 | 0.000164654 | -0.000296289 | -0.000682746 | -0.000221803 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_h016_gain_all_k1400_a1_fff2a763.csv |
| oracle_gain_all_k1100_a1.25 | joint_world_sensor | oracle_gain | all | 1100 | -0.000515418 | -0.000515402 | 0.000164654 | -0.000296289 | -0.000680072 | -0.000219129 | 0.133128560 | hitl/h017_joint_label_weight_jepa/submission_h017_oracle_gain_all_k1100_a1.25_34bd402f.csv |
| oracle_gain_all_k1100_a0.75 | joint_world_sensor | oracle_gain | all | 1100 | -0.000514947 | -0.000514937 | 0.000164654 | -0.000296289 | -0.000679601 | -0.000218658 | 0.081420804 | hitl/h017_joint_label_weight_jepa/submission_h017_oracle_gain_all_k1100_a0.75_cb3e2596.csv |
| weight_shift_all_k1650_a1.25 | joint_world_sensor | weight_shift | all | 1650 | -0.000514861 | -0.000514841 | 0.000164654 | -0.000296289 | -0.000679515 | -0.000218572 | 0.133128560 | hitl/h017_joint_label_weight_jepa/submission_h017_weight_shift_all_k1650_a1.25_1664ec2c.csv |
| weight_shift_all_k1650_a0.75 | joint_world_sensor | weight_shift | all | 1650 | -0.000514377 | -0.000514364 | 0.000164654 | -0.000296289 | -0.000679031 | -0.000218088 | 0.081420804 | hitl/h017_joint_label_weight_jepa/submission_h017_weight_shift_all_k1650_a0.75_e00bfa7c.csv |
| oracle_gain_all_k800_a1 | joint_world_sensor | oracle_gain | all | 800 | -0.000511435 | -0.000511423 | 0.000164654 | -0.000296289 | -0.000676089 | -0.000215146 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_oracle_gain_all_k800_a1_bf640d79.csv |
| conflict_all_k1650_a1 | joint_world_sensor | conflict | all | 1650 | -0.000508813 | -0.000508795 | 0.000164654 | -0.000296289 | -0.000673467 | -0.000212524 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_conflict_all_k1650_a1_554ddb0c.csv |
| weight_shift_all_k1400_a1 | joint_world_sensor | weight_shift | all | 1400 | -0.000504266 | -0.000504252 | 0.000164654 | -0.000296289 | -0.000668920 | -0.000207977 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_weight_shift_all_k1400_a1_46178aa3.csv |
| h015_gain_all_k1650_a1.25 | joint_world_sensor | h015_gain | all | 1650 | -0.000498750 | -0.000498729 | 0.000164654 | -0.000296289 | -0.000663404 | -0.000202461 | 0.133128560 | hitl/h017_joint_label_weight_jepa/submission_h017_h015_gain_all_k1650_a1.25_20859cde.csv |
| h015_gain_all_k1650_a0.75 | joint_world_sensor | h015_gain | all | 1650 | -0.000498355 | -0.000498342 | 0.000164654 | -0.000296289 | -0.000663009 | -0.000202066 | 0.081420804 | hitl/h017_joint_label_weight_jepa/submission_h017_h015_gain_all_k1650_a0.75_cd691d83.csv |
| consensus_all_k1100_a1.25 | joint_world_sensor | consensus | all | 1100 | -0.000495585 | -0.000495570 | 0.000164654 | -0.000296289 | -0.000660239 | -0.000199296 | 0.133128560 | hitl/h017_joint_label_weight_jepa/submission_h017_consensus_all_k1100_a1.25_60e9146a.csv |
| consensus_all_k1100_a0.75 | joint_world_sensor | consensus | all | 1100 | -0.000495106 | -0.000495097 | 0.000164654 | -0.000296289 | -0.000659760 | -0.000198817 | 0.081420804 | hitl/h017_joint_label_weight_jepa/submission_h017_consensus_all_k1100_a0.75_07976f07.csv |
| h016_gain_all_k1400_a1.25 | joint_world_sensor | h016_gain | all | 1400 | -0.000487026 | -0.000487008 | 0.000164654 | -0.000296289 | -0.000651680 | -0.000190737 | 0.133128560 | hitl/h017_joint_label_weight_jepa/submission_h017_h016_gain_all_k1400_a1.25_055248fc.csv |
| h016_gain_all_k1400_a0.75 | joint_world_sensor | h016_gain | all | 1400 | -0.000486539 | -0.000486528 | 0.000164654 | -0.000296289 | -0.000651193 | -0.000190250 | 0.081420804 | hitl/h017_joint_label_weight_jepa/submission_h017_h016_gain_all_k1400_a0.75_6c37e2a8.csv |
| oracle_gain_all_k800_a1.25 | joint_world_sensor | oracle_gain | all | 800 | -0.000480738 | -0.000480724 | 0.000164654 | -0.000296289 | -0.000645392 | -0.000184449 | 0.133128560 | hitl/h017_joint_label_weight_jepa/submission_h017_oracle_gain_all_k800_a1.25_9a762498.csv |
| oracle_gain_all_k800_a0.75 | joint_world_sensor | oracle_gain | all | 800 | -0.000480269 | -0.000480261 | 0.000164654 | -0.000296289 | -0.000644924 | -0.000183980 | 0.081420804 | hitl/h017_joint_label_weight_jepa/submission_h017_oracle_gain_all_k800_a0.75_7ff05e1b.csv |
| conflict_all_k1650_a1.25 | joint_world_sensor | conflict | all | 1650 | -0.000478105 | -0.000478084 | 0.000164654 | -0.000296289 | -0.000642759 | -0.000181816 | 0.133128560 | hitl/h017_joint_label_weight_jepa/submission_h017_conflict_all_k1650_a1.25_c59222e7.csv |
| conflict_all_k1650_a0.75 | joint_world_sensor | conflict | all | 1650 | -0.000477701 | -0.000477688 | 0.000164654 | -0.000296289 | -0.000642355 | -0.000181412 | 0.081420804 | hitl/h017_joint_label_weight_jepa/submission_h017_conflict_all_k1650_a0.75_5b7bc4b9.csv |
| h015_gain_all_k1400_a1 | joint_world_sensor | h015_gain | all | 1400 | -0.000477315 | -0.000477304 | 0.000164654 | -0.000296289 | -0.000641969 | -0.000181026 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_h015_gain_all_k1400_a1_14d73c37.csv |
| weight_shift_all_k1400_a1.25 | joint_world_sensor | weight_shift | all | 1400 | -0.000474067 | -0.000474050 | 0.000164654 | -0.000296289 | -0.000638721 | -0.000177778 | 0.133128560 | hitl/h017_joint_label_weight_jepa/submission_h017_weight_shift_all_k1400_a1.25_2cc6a9ce.csv |
| consensus_all_k800_a1 | joint_world_sensor | consensus | all | 800 | -0.000473630 | -0.000473619 | 0.000164654 | -0.000296289 | -0.000638284 | -0.000177341 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_consensus_all_k800_a1_0c6e620c.csv |
| weight_shift_all_k1400_a0.75 | joint_world_sensor | weight_shift | all | 1400 | -0.000473583 | -0.000473572 | 0.000164654 | -0.000296289 | -0.000638237 | -0.000177294 | 0.081420804 | hitl/h017_joint_label_weight_jepa/submission_h017_weight_shift_all_k1400_a0.75_411b93c0.csv |
| weight_shift_all_k1100_a1 | joint_world_sensor | weight_shift | all | 1100 | -0.000464515 | -0.000464502 | 0.000164654 | -0.000296289 | -0.000629169 | -0.000168226 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_weight_shift_all_k1100_a1_be635e5a.csv |
| oracle_gain_all_k1650_a0.55 | joint_world_sensor | oracle_gain | all | 1650 | -0.000460196 | -0.000460186 | 0.000164654 | -0.000296289 | -0.000624850 | -0.000163907 | 0.060982345 | hitl/h017_joint_label_weight_jepa/submission_h017_oracle_gain_all_k1650_a0.55_b75584a6.csv |
| consensus_all_k1650_a0.55 | joint_world_sensor | consensus | all | 1650 | -0.000460019 | -0.000460009 | 0.000164654 | -0.000296289 | -0.000624673 | -0.000163730 | 0.060982345 | hitl/h017_joint_label_weight_jepa/submission_h017_consensus_all_k1650_a0.55_b2b89477.csv |
| h016_gain_all_k1100_a1 | joint_world_sensor | h016_gain | all | 1100 | -0.000455961 | -0.000455950 | 0.000164654 | -0.000296289 | -0.000620615 | -0.000159672 | 0.107121197 | hitl/h017_joint_label_weight_jepa/submission_h017_h016_gain_all_k1100_a1_d28b11a0.csv |

## Decision

- Primary upload-safe candidate: `submission_h017_joint_label_weight_oracle_gain_all_k1650_a1_uploadsafe.csv`.
- Interpretation: this file bets that public labels and public cell weights must be solved jointly, not as separate H012/H016 projections.

## Files

- `hitl/h017_joint_label_weight_jepa/h017_joint_configs.csv`
- `hitl/h017_joint_label_weight_jepa/h017_null_stress.csv`
- `hitl/h017_joint_label_weight_jepa/h017_cell_joint_state.csv`
- `hitl/h017_joint_label_weight_jepa/h017_candidates.csv`
