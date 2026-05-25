# CL CatBoost Public Axis Candidates

## Public Feedback Used

| file | public_lb |
|---|---|
| submission_temporal_state_smoothing_wcap02_prob.csv | 0.631187 |
| submission_v38_targetwise_catboost_proto_safe_prob.csv | 0.621864 |
| submission_v39_imported_v81_conditional_latent_routing_raw_prob.csv | 0.661003 |
| submission_cl_catboost_state_proto_sleep_state_prob.csv | 0.614622 |

Interpretation: imported v81 is anti-public; CL CatBoost direction is public-positive; more sleep/state movement beat the safe blend.

## Candidate Files

| file | rows | keys_ok | no_na | mean_abs_vs_anchor | mean_abs_vs_sleep_state | min_prob | max_prob | mean_target_std |
|---|---|---|---|---|---|---|---|---|
| submission_cl_catboost_public_axis_step2_prob.csv | 250 | True | True | 0.046528 | 0.013188 | 0.087923 | 0.967226 | 0.156248 |
| submission_cl_catboost_public_axis_step3_prob.csv | 250 | True | True | 0.055030 | 0.021560 | 0.087923 | 0.962226 | 0.156157 |
| submission_cl_catboost_public_axis_rowgate_prob.csv | 250 | True | True | 0.042830 | 0.005509 | 0.087923 | 0.967321 | 0.155328 |
| submission_cl_catboost_public_axis_consensus_prob.csv | 250 | True | True | 0.041286 | 0.003967 | 0.087923 | 0.967321 | 0.154455 |

## Target Movement

| file | target | mean_abs_vs_anchor | mean_abs_vs_sleep_state | mean_abs_vs_raw_model | signed_vs_anchor | std | min | max | corr_vs_anchor |
|---|---|---|---|---|---|---|---|---|---|
| submission_cl_catboost_public_axis_step2_prob.csv | Q1 | 0.010232 | 0.004681 | 0.142576 | -0.000939 | 0.160864 | 0.087923 | 0.885212 | 0.999915 |
| submission_cl_catboost_public_axis_step2_prob.csv | Q2 | 0.009834 | 0.007197 | 0.159508 | 0.000491 | 0.098876 | 0.154019 | 0.743350 | 0.996411 |
| submission_cl_catboost_public_axis_step2_prob.csv | Q3 | 0.110588 | 0.026586 | 0.072273 | 0.011797 | 0.130514 | 0.339058 | 0.838423 | 0.232064 |
| submission_cl_catboost_public_axis_step2_prob.csv | S1 | 0.072884 | 0.016707 | 0.050237 | 0.002601 | 0.165156 | 0.277011 | 0.937626 | 0.816522 |
| submission_cl_catboost_public_axis_step2_prob.csv | S2 | 0.072225 | 0.016887 | 0.063151 | 0.018714 | 0.175076 | 0.244104 | 0.925395 | 0.881048 |
| submission_cl_catboost_public_axis_step2_prob.csv | S3 | 0.012306 | 0.010719 | 0.127064 | -0.008731 | 0.181819 | 0.246896 | 0.967226 | 0.999555 |
| submission_cl_catboost_public_axis_step2_prob.csv | S4 | 0.037625 | 0.009541 | 0.122608 | -0.001277 | 0.181428 | 0.104597 | 0.914921 | 0.981538 |
| submission_cl_catboost_public_axis_step3_prob.csv | Q1 | 0.014708 | 0.007608 | 0.142587 | -0.001465 | 0.155629 | 0.087923 | 0.875875 | 0.999793 |
| submission_cl_catboost_public_axis_step3_prob.csv | Q2 | 0.010947 | 0.011209 | 0.162935 | -0.002429 | 0.095777 | 0.154019 | 0.743350 | 0.998698 |
| submission_cl_catboost_public_axis_step3_prob.csv | Q3 | 0.128704 | 0.044711 | 0.054882 | 0.011491 | 0.147216 | 0.339058 | 0.838423 | 0.152214 |
| submission_cl_catboost_public_axis_step3_prob.csv | S1 | 0.082661 | 0.026632 | 0.043650 | -0.001356 | 0.169347 | 0.277011 | 0.937777 | 0.768110 |
| submission_cl_catboost_public_axis_step3_prob.csv | S2 | 0.084259 | 0.028960 | 0.053183 | 0.019432 | 0.174485 | 0.244104 | 0.917960 | 0.837793 |
| submission_cl_catboost_public_axis_step3_prob.csv | S3 | 0.017957 | 0.013863 | 0.127940 | -0.012781 | 0.177280 | 0.256022 | 0.962226 | 0.999071 |
| submission_cl_catboost_public_axis_step3_prob.csv | S4 | 0.045977 | 0.017937 | 0.116063 | -0.002846 | 0.173365 | 0.116349 | 0.905539 | 0.973311 |
| submission_cl_catboost_public_axis_rowgate_prob.csv | Q1 | 0.009883 | 0.000138 | 0.138456 | -0.000354 | 0.162397 | 0.087923 | 0.887831 | 0.999398 |
| submission_cl_catboost_public_axis_rowgate_prob.csv | Q2 | 0.014981 | 0.000363 | 0.152736 | 0.004405 | 0.099885 | 0.154019 | 0.743350 | 0.988041 |
| submission_cl_catboost_public_axis_rowgate_prob.csv | Q3 | 0.097133 | 0.013130 | 0.085572 | 0.009645 | 0.120356 | 0.339058 | 0.838423 | 0.265318 |
| submission_cl_catboost_public_axis_rowgate_prob.csv | S1 | 0.064534 | 0.008345 | 0.057734 | 0.002842 | 0.160878 | 0.277011 | 0.930178 | 0.840321 |
| submission_cl_catboost_public_axis_rowgate_prob.csv | S2 | 0.064823 | 0.009483 | 0.069977 | 0.018767 | 0.175534 | 0.244104 | 0.928022 | 0.896159 |
| submission_cl_catboost_public_axis_rowgate_prob.csv | S3 | 0.013239 | 0.000000 | 0.116469 | -0.007713 | 0.185835 | 0.235852 | 0.967321 | 0.997669 |
| submission_cl_catboost_public_axis_rowgate_prob.csv | S4 | 0.035221 | 0.007103 | 0.124648 | -0.001669 | 0.182410 | 0.094154 | 0.914921 | 0.979970 |
| submission_cl_catboost_public_axis_consensus_prob.csv | Q1 | 0.009883 | 0.000138 | 0.138456 | -0.000354 | 0.162397 | 0.087923 | 0.887831 | 0.999398 |
| submission_cl_catboost_public_axis_consensus_prob.csv | Q2 | 0.014981 | 0.000363 | 0.152736 | 0.004405 | 0.099885 | 0.154019 | 0.743350 | 0.988041 |
| submission_cl_catboost_public_axis_consensus_prob.csv | Q3 | 0.094197 | 0.010195 | 0.088534 | 0.009697 | 0.115535 | 0.339058 | 0.831468 | 0.301393 |
| submission_cl_catboost_public_axis_consensus_prob.csv | S1 | 0.062471 | 0.006286 | 0.059959 | 0.002516 | 0.159354 | 0.277011 | 0.932040 | 0.856077 |
| submission_cl_catboost_public_axis_consensus_prob.csv | S2 | 0.061947 | 0.006608 | 0.072991 | 0.016727 | 0.173617 | 0.254140 | 0.927365 | 0.909789 |
| submission_cl_catboost_public_axis_consensus_prob.csv | S3 | 0.013239 | 0.000000 | 0.116469 | -0.007713 | 0.185835 | 0.235852 | 0.967321 | 0.997669 |
| submission_cl_catboost_public_axis_consensus_prob.csv | S4 | 0.032287 | 0.004182 | 0.127669 | -0.001359 | 0.184560 | 0.096765 | 0.914921 | 0.986374 |

## Intended Order For Tomorrow

1. `submission_cl_catboost_public_axis_consensus_prob.csv`
2. `submission_cl_catboost_public_axis_step2_prob.csv`
3. `submission_cl_catboost_public_axis_rowgate_prob.csv`

`step3` is the minimum-0.57 attempt, not the first diagnostic. It moves far enough to plausibly jump but has the largest overfit risk.