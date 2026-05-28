# Hidden Subset Selector Stress Harness

This is a selector-resolution test, not a new public-LB claim. It asks whether the current anchor geometry can choose among raw05/a2c8/JEPA candidates with enough margin to justify another submission.

## Selector Gate

Gate definition: LOO MAE <= `0.00040`, L2O MAE <= `0.00040`, both rank accuracies > `0.90`, a2c8 predicted better than raw05, and stage2 predicted better than known bad JEPA anchors.

- Passing selector families: `0` / `7`.
- Best LOO model: `a2c8_distance_badload` MAE `0.000536411`, rank accuracy `0.786`.
- Best L2O model: `a2c8_distance_badload` MAE `0.000565765`, pair accuracy `0.857`.
- Raw05 selector mean delta versus a2c8 public: `0.000276693`.
- A2C8 own stress spread: `0.001418568`.
- Candidates clearing resolved-better gate: `0` / `213`.

## Model Stress Scores

```csv
model,loo_mae,loo_rank_accuracy,loo_p90_abs_error,l2o_mae,l2o_rank_accuracy,l2o_p90_abs_error,top1_is_a2c8,a2c8_beats_raw05,stage2_beats_bad_anchors,a2c8_raw05_pred_margin,min_bad_minus_a2c8,selector_gate_pass
a2c8_distance_badload,0.000536411,0.785714286,0.000807589,0.000565765,0.857142857,0.000995883,False,False,True,-6.8331e-05,0.002016553,False
raw05_distance_badload,0.000541064,0.785714286,0.000808511,0.000572092,0.857142857,0.000999039,False,False,True,-7.9501e-05,0.001994954,False
raw05_a2c8_compat,0.000546739,0.821428571,0.000807504,0.000580841,0.892857143,0.000996314,False,False,True,-6.2119e-05,0.002015703,False
good_bad_axes,0.000553668,0.785714286,0.000892916,0.000646435,0.821428571,0.00094987,False,False,True,-2.691e-05,0.002447899,False
bad_axes_only,0.000891613,0.785714286,0.001808372,0.00087787,0.785714286,0.002714774,False,False,True,-4.4343e-05,0.002370193,False
target_move_core,0.001100864,0.714285714,0.002243221,0.0011565,0.75,0.002372241,False,False,True,-0.000102259,0.000843317,False
compact_axis_energy,0.005212144,0.714285714,0.011621348,0.005590113,0.821428571,0.028963775,False,False,True,-8.5239e-05,0.000495541,False
```

## Candidate Stress Top

```csv
file,is_known_public,known_public_lb,selector_stress_mean,selector_delta_vs_a2c8_public,selector_stress_p90,selector_p90_delta_vs_a2c8_public,selector_stress_spread,beats_a2c8_scenario_rate,resolved_better_than_a2c8_gate,candidate_selector_risk,bad_axis_abs_load,mean_abs_move_vs_a2c8,mean_abs_move_vs_raw05
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,True,0.577526307,0.577716014,0.000276693,0.577978603,0.000539282,0.001256328,0.787644788,False,0.577970998,0.02479001,0.008530873,0.0
submission_raw05_jepa_axisbridge_9d6e707c.csv,False,,0.577726089,0.000286768,0.578015644,0.000576323,0.001390007,0.436293436,False,0.578010551,0.034284298,0.001025472,0.007816951
submission_raw05_jepa_axisbridge_0edfd32b.csv,False,,0.577726096,0.000286775,0.578015646,0.000576325,0.001390009,0.436293436,False,0.578010559,0.034289949,0.001026402,0.007813249
submission_raw05_jepa_axisbridge_705367e9.csv,False,,0.577726344,0.000287023,0.578015569,0.000576248,0.001388758,0.436293436,False,0.578010564,0.034200827,0.001058844,0.00777545
submission_raw05_jepa_axisbridge_f411b287.csv,False,,0.577726106,0.000286785,0.578015707,0.000576386,0.001390134,0.432432432,False,0.5780106,0.034332474,0.001022781,0.007819716
submission_raw05_jepa_axisbridge_04a3de62.csv,False,,0.577726174,0.000286853,0.578015763,0.000576442,0.00139016,0.432432432,False,0.578010695,0.034377325,0.001039753,0.007801262
submission_raw05_jepa_axisbridge_e34b4795.csv,False,,0.5777265,0.000287179,0.578015947,0.000576626,0.001389075,0.436293436,False,0.578010799,0.034447851,0.001047409,0.007752085
submission_raw05_jepa_axisbridge_2f6bc887.csv,False,,0.577726503,0.000287182,0.578015951,0.00057663,0.001389075,0.436293436,False,0.578010802,0.03445042,0.00104732,0.007751892
submission_raw05_jepa_axisbridge_2574f23d.csv,False,,0.577726503,0.000287182,0.578015951,0.00057663,0.001389075,0.436293436,False,0.578010802,0.034450473,0.001047324,0.007751927
submission_raw05_jepa_axisbridge_45f2ba5a.csv,False,,0.577726504,0.000287183,0.578015952,0.000576631,0.001389075,0.436293436,False,0.578010804,0.034451482,0.001047277,0.007751905
submission_raw05_jepa_axisbridge_4bb109a4.csv,False,,0.577726514,0.000287193,0.578015969,0.000576648,0.00138908,0.436293436,False,0.578010817,0.034461953,0.001047088,0.007752647
submission_raw05_jepa_axisbridge_7217d193.csv,False,,0.577726634,0.000287313,0.578016128,0.000576807,0.001389081,0.428571429,False,0.578010967,0.034564728,0.001057327,0.007760619
submission_jepa_public_minimax_bridge_a46c5492.csv,False,,0.577734222,0.000294901,0.578016755,0.000577434,0.001346772,0.22007722,False,0.57801175,0.031056819,0.003180183,0.007567965
submission_jepa_public_minimax_bridge_f9862e58.csv,False,,0.577733916,0.000294595,0.578016471,0.00057715,0.001349186,0.231660232,False,0.578011878,0.031642722,0.003126528,0.00755577
submission_jepa_public_minimax_bridge_ba14c999.csv,False,,0.577733835,0.000294514,0.578015418,0.000576097,0.001350491,0.247104247,False,0.578012025,0.032091036,0.003118836,0.007453602
submission_jepa_public_minimax_bridge_d07085ae.csv,False,,0.577733994,0.000294673,0.57801652,0.000577199,0.001349614,0.231660232,False,0.578012051,0.03184183,0.003113108,0.007566663
submission_jepa_public_minimax_bridge_a45028dc.csv,False,,0.577735068,0.000295747,0.578015365,0.000576044,0.001344154,0.250965251,False,0.578012206,0.03225258,0.003211358,0.007382205
submission_frontier_cvjepa_refine_a2c8d2c8.csv,True,0.577439321,0.577722982,0.000283661,0.578019258,0.000579937,0.001418568,0.0,False,0.578012232,0.036905767,0.0,0.008530873
submission_jepa_public_minimax_bridge_ac3fc249.csv,False,,0.577733978,0.000294657,0.578016928,0.000577607,0.001350628,0.227799228,False,0.578012244,0.031973264,0.00307523,0.007626171
submission_jepa_public_minimax_bridge_8482dcee.csv,False,,0.577735056,0.000295735,0.578015311,0.00057599,0.001344379,0.254826255,False,0.578012248,0.032317842,0.003206103,0.00737664
submission_jepa_public_minimax_bridge_e5b2a6d3.csv,False,,0.577733941,0.00029462,0.578015457,0.000576136,0.001351095,0.250965251,False,0.578012262,0.032321265,0.003100327,0.007465187
submission_jepa_public_minimax_bridge_264be431.csv,False,,0.577735134,0.000295813,0.578015487,0.000576166,0.001344606,0.250965251,False,0.578012365,0.032470928,0.003190572,0.007384175
submission_jepa_public_minimax_bridge_f2fee160.csv,False,,0.577733992,0.000294671,0.578016113,0.000576792,0.001351432,0.235521236,False,0.578012398,0.031993404,0.003104436,0.007538754
submission_jepa_public_minimax_bridge_14a0fbc6.csv,False,,0.57773618,0.000296859,0.578015559,0.000576238,0.001339177,0.227799228,False,0.578012399,0.032428511,0.003264619,0.007344438
```

## Direct Inverse Selector Stress

```csv
source,stress,policy,n,mae,p90_abs_error,max_abs_error
direct_inverse,l2o,oracle_pair_best1,15,0.000344458,0.000765367,0.001288728
direct_inverse,l2o,l2o_best1,15,0.000532341,0.001112468,0.001306958
direct_inverse,l2o,l2o_best5_mean,15,0.000555685,0.001106912,0.001352566
direct_inverse,l2o,subject_best3_mean,15,0.000575137,0.00112267,0.001443994
direct_inverse,l2o,l2o_best12_mean,15,0.000597972,0.001248891,0.001448793
direct_inverse,l2o,structured_best1,15,0.000607155,0.001204901,0.001373028
direct_inverse,loo,oracle_best1,6,0.000362682,0.001005504,0.001293826
direct_inverse,loo,train_best1,6,0.000598722,0.001281109,0.001576285
direct_inverse,loo,train_best5_mean,6,0.000927513,0.001904266,0.002501583
direct_inverse,loo,train_best12_mean,6,0.000966955,0.002023576,0.002810014
direct_inverse,loo,structured_best1,6,0.001008715,0.002208641,0.003211498
direct_inverse,loo,nonrandom_best5_mean,6,0.001095317,0.002234014,0.003149463
```

## Mask Stability

```csv
policy,top_mask_kind,top_mask_name,top_prior_name,count,source
l2o_best1,random_rows,frac0.40_rep009,entropy_g075,15,l2o_policy_mask_prior
l2o_best12_mean,random_rows,frac0.40_rep009,entropy_g075,15,l2o_policy_mask_prior
l2o_best5_mean,random_rows,frac0.40_rep009,entropy_g075,15,l2o_policy_mask_prior
structured_best1,subject_contiguous,frac0.40_rep052,entropy_g075,15,l2o_policy_mask_prior
subject_best3_mean,subject_contiguous,frac0.40_rep052,entropy_g075,15,l2o_policy_mask_prior
oracle_pair_best1,random_rows,frac0.30_rep056,entropy_g075,2,l2o_policy_mask_prior
oracle_pair_best1,random_rows,frac0.40_rep002,a2c8,2,l2o_policy_mask_prior
oracle_pair_best1,random_rows,frac0.60_rep001,raw05,2,l2o_policy_mask_prior
oracle_pair_best1,subject_contiguous,frac0.25_rep099,entropy_g075,2,l2o_policy_mask_prior
oracle_pair_best1,subject_order,per_subject_prefix_frac0.25,entropy_g075,2,l2o_policy_mask_prior
oracle_pair_best1,global_order,rowmod4_rem3,raw05,1,l2o_policy_mask_prior
oracle_pair_best1,random_rows,frac0.40_rep002,entropy_g075,1,l2o_policy_mask_prior
oracle_pair_best1,random_rows,frac0.40_rep009,entropy_g075,1,l2o_policy_mask_prior
oracle_pair_best1,random_rows,frac0.40_rep009,raw05,1,l2o_policy_mask_prior
oracle_pair_best1,subject_contiguous,frac0.25_rep099,entropy_g050,1,l2o_policy_mask_prior
,random_rows,frac0.40_rep009,entropy_g075,12,loo_mask_prior
,global_order,rowmod4_rem3,entropy_g075,10,loo_mask_prior
,subject_contiguous,frac0.40_rep052,entropy_g075,7,loo_mask_prior
,subject_contiguous,frac0.25_rep099,raw05,2,loo_mask_prior
,subject_contiguous,frac0.25_rep150,a2c8,2,loo_mask_prior
,global_order,rowmod4_rem3,raw05,1,loo_mask_prior
,random_rows,frac0.60_rep001,raw05,1,loo_mask_prior
,subject_contiguous,frac0.25_rep099,entropy_g050,1,loo_mask_prior
train_best1,random_rows,frac0.40_rep009,entropy_g075,4,loo_policy_mask_prior
```

## Read

- The current selector family still fails the promised gate. It can separate clearly bad JEPA axes, but not enough to robustly rank a2c8/raw05-scale movements.
- L2O stress is the real bottleneck: when two anchors are removed, the learned public-subset geometry has too few constraints and the candidate ordering spreads wider than the public gap we are trying to exploit.
- The direct inverse branch confirms the same failure mode: oracle masks can fit anchors better than train-selected masks, so the hidden subset exists in the hypothesis class but is not being selected reliably.
- This means a 0.54 path is unlikely from more tiny raw05-compatible blends alone. The next useful experiments must create a movement large enough to exceed selector uncertainty, or improve the selector before trusting post-hoc blends.

## Next Decision

Run targetwise safe multi-block LeJEPA only if its candidate movement exceeds this harness uncertainty while keeping bad-axis load low. Otherwise, continue selector work before producing more submissions.

## Files

- `hidden_subset_selector_stress_anchor_predictions.csv`
- `hidden_subset_selector_stress_model_scores.csv`
- `hidden_subset_selector_stress_candidate_scores.csv`
- `hidden_subset_selector_stress_inverse_summary.csv`
- `hidden_subset_selector_stress_mask_stability.csv`
