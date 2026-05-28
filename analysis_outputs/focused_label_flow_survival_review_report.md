# Focused Label-Flow Survival Review

Purpose: test whether the E14 S4+Q3 label-flow candidates still look plausible under an independent hidden-subset selector stress, rather than only the pairwise selector used to choose them.

## Stress Setup

- selected label-flow candidates: `163`
- pair-submit candidates inside review set: `61`
- independent survival candidates: `0`
- strict independent survival candidates: `0`
- known a2c8 selector p90 delta vs a2c8 public: `0.000579937`
- known raw05 selector p90 delta vs a2c8 public: `0.000539282`
- corr(pairwise p90 delta, old-selector p90 delta): `-0.881`
- corr(move vs a2c8, old-selector p90 delta): `0.905`
- corr(bad-axis load, old-selector p90 delta): `-0.647`

Independent survival requires pair submit/control/probe gates, no pairwise conflict, hidden-subset scenario majority beating a2c8, low bad-axis load <= 0.025, and >=90% of movement concentrated in Q3+S4. Strict survival additionally requires the old selector p90 to beat a2c8.

The failure is not random noise: in this focused family, improving the pairwise p90 score is strongly anti-aligned with the older hidden-subset selector. Pair-submit candidates have old-selector p90 deltas around `0.000675879` median, while non-pair-submit label-flow sensors sit around `0.000577697` median.

## Top Review Candidates

source_path,pairwise_source,pair_delta_vs_a2c8_p90,selector_p90_delta_vs_a2c8_public,selector_delta_vs_a2c8_public,beats_a2c8_scenario_rate,bad_axis_abs_load,q3_s4_move_share,dominant_target,mean_abs_move_vs_a2c8,independent_survival_flag,strict_independent_survival_flag,review_priority_score
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.4316e-05,0.000638679,0.000339632,0.277992278,0.020667527,1.0,S4,0.006047604,False,False,0.000176411
analysis_outputs/submission_label_flow_focused_b572eb03.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.4235e-05,0.000639346,0.000339642,0.277992278,0.020074528,1.0,S4,0.006082257,False,False,0.000176637
analysis_outputs/submission_label_flow_focused_2c0943fb.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.4181e-05,0.000639849,0.000339667,0.277992278,0.019682665,1.0,S4,0.006105157,False,False,0.000176811
analysis_outputs/submission_label_flow_focused_668ec379.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.4148e-05,0.000640686,0.000339729,0.277992278,0.01909991,1.0,S4,0.006139216,False,False,0.000177056
analysis_outputs/submission_label_flow_focused_8554a347.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.3825e-05,0.000641389,0.000339214,0.277992278,0.017576274,1.0,S4,0.006254868,False,False,0.000177346
analysis_outputs/submission_label_flow_focused_e79480ab.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.4128e-05,0.000641949,0.000339856,0.277992278,0.018331989,1.0,S4,0.006184101,False,False,0.000177416
analysis_outputs/submission_label_flow_focused_6f3a5547.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.3811e-05,0.00064223,0.000339278,0.277992278,0.016995518,1.0,S4,0.00628881,False,False,0.000177573
analysis_outputs/submission_label_flow_focused_b1f1334b.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.3802e-05,0.000642841,0.000339335,0.281853282,0.016611579,1.0,S4,0.006311251,False,False,0.000177744
analysis_outputs/submission_label_flow_focused_d26d933b.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.3786e-05,0.00064383,0.000339444,0.281853282,0.016040369,1.0,S4,0.00634464,False,False,0.000178031
analysis_outputs/submission_label_flow_focused_1a84bfe0.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.4094e-05,0.000644124,0.000340133,0.277992278,0.017198623,1.0,S4,0.006250355,False,False,0.000178069
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-6.5217e-05,0.000675515,0.000346654,0.277992278,0.017246827,1.0,S4,0.007233505,False,False,0.000178598
analysis_outputs/submission_label_flow_focused_784b33b0.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.3576e-05,0.00064527,0.000339627,0.281853282,0.015287231,1.0,S4,0.006388668,False,False,0.000178651
analysis_outputs/submission_label_flow_focused_bcb4777d.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-6.5084e-05,0.000676129,0.000346706,0.277992278,0.016113461,1.0,S4,0.007299758,False,False,0.000178782
analysis_outputs/submission_label_flow_focused_c87aaa14.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-6.4818e-05,0.000675114,0.000346664,0.277992278,0.018014748,1.0,S4,0.00718862,False,False,0.000178973
analysis_outputs/submission_label_flow_focused_f7699bdc.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-6.4818e-05,0.000675958,0.000345994,0.277992278,0.016491112,1.0,S4,0.007304271,False,False,0.000178974
analysis_outputs/submission_label_flow_focused_fe7cc64f.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-6.4742e-05,0.000676253,0.000345964,0.277992278,0.015910356,1.0,S4,0.007338214,False,False,0.000179063
analysis_outputs/submission_label_flow_focused_04d507ca.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-6.4736e-05,0.000676453,0.000345956,0.277992278,0.015526416,1.0,S4,0.007360655,False,False,0.000179081
analysis_outputs/submission_label_flow_focused_ab52c283.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-6.4725e-05,0.000676755,0.000345961,0.277992278,0.014955207,1.0,S4,0.007394044,False,False,0.000179111
analysis_outputs/submission_label_flow_focused_70601867.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-6.471e-05,0.000677163,0.000345995,0.277992278,0.014202069,1.0,S4,0.007438071,False,False,0.00017916
analysis_outputs/submission_label_flow_focused_8a5e8191.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-6.4685e-05,0.000677786,0.000346104,0.281853282,0.013089646,1.0,S4,0.00750311,False,False,0.000179247
analysis_outputs/submission_label_flow_focused_bfe4ee38.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-6.4519e-05,0.000674818,0.000346696,0.277992278,0.018597503,1.0,S4,0.007154561,False,False,0.000179259
analysis_outputs/submission_label_flow_focused_87affbd1.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-6.4321e-05,0.000674623,0.00034673,0.277992278,0.018989366,1.0,S4,0.00713166,False,False,0.000179452
analysis_outputs/submission_label_flow_focused_87a2d03f.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.2889e-05,0.00064665,0.000339073,0.281853282,0.013314516,1.0,S4,0.006540768,False,False,0.000179469
analysis_outputs/submission_label_flow_focused_ff8273a8.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.3311e-05,0.000647669,0.000339974,0.281853282,0.014174808,1.0,S4,0.006453706,False,False,0.000179623
analysis_outputs/submission_label_flow_focused_e3dbc41f.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-6.4024e-05,0.000674335,0.000346801,0.277992278,0.019582364,1.0,S4,0.007097008,False,False,0.000179744
analysis_outputs/submission_label_flow_focused_5cd7f4fe.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.2831e-05,0.00064767,0.000339193,0.277992278,0.012749518,1.0,S4,0.006573797,False,False,0.000179811
analysis_outputs/submission_label_flow_focused_68e4f54e.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-6.4002e-05,0.000678337,0.000345547,0.281853282,0.012614492,1.0,S4,0.007590172,False,False,0.000179996
analysis_outputs/submission_label_flow_focused_50f1e6b3.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.2614e-05,0.000648682,0.000339543,0.277992278,0.012667927,1.0,S4,0.006595646,False,False,0.000180406
analysis_outputs/submission_label_flow_focused_d317c71f.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-6.3584e-05,0.000678686,0.000346079,0.281853282,0.012634719,1.0,S4,0.0076232,False,False,0.000180592
analysis_outputs/submission_label_flow_focused_a4fc7c4f.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.2775e-05,0.000650395,0.000340208,0.277992278,0.012687894,1.0,S4,0.006628171,False,False,0.000180914


## Pinned Frontier/Sensor Candidates

source_path,pairwise_source,pair_delta_vs_a2c8_p90,selector_p90_delta_vs_a2c8_public,selector_delta_vs_a2c8_public,beats_a2c8_scenario_rate,bad_axis_abs_load,q3_s4_move_share,dominant_target,mean_abs_move_vs_a2c8,independent_survival_flag,strict_independent_survival_flag,review_priority_score
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-5.4316e-05,0.000638679,0.000339632,0.277992278,0.020667527,1.0,S4,0.006047604,False,False,0.000176411
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,label_flow_combo_focused_submit_pairwise_scored.csv,-6.5217e-05,0.000675515,0.000346654,0.277992278,0.017246827,1.0,S4,0.007233505,False,False,0.000178598
analysis_outputs/submission_label_flow_combo_3d536109.csv,label_flow_combo_gate_pairwise_scored.csv,-3.5162e-05,0.000581412,0.000323277,0.266409266,0.01529804,1.0,S4,0.004155555,False,False,0.000173069
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,label_flow_targetwise_amplified_gate_pairwise_scored.csv,-5.997e-06,0.000569397,0.000291657,0.277992278,0.036080105,1.0,S4,0.000728815,False,False,0.000197983
analysis_outputs/submission_label_flow_gated_ff8df011.csv,label_flow_gated_candidate_pairwise_scored.csv,-6.87e-07,0.00057827,0.000292535,0.277992278,0.032287448,0.793117611,Q3,0.0003702,False,False,0.000235918
analysis_outputs/submission_label_flow_gated_f1046674.csv,label_flow_gated_candidate_pairwise_scored.csv,-2.9e-08,0.000578952,0.000285351,0.266409266,0.036137517,0.778498313,Q3,6.3406e-05,False,False,0.000236673


## Interpretation

- Pairwise-positive label-flow does not survive independent hidden-subset geometry. Treat E14 as a sensor, not a submission.
- The likely failure mode is selector overfit to the public-order surrogate or target-local movement that the older anchor geometry does not price as public-positive.
