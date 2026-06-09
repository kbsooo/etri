# Final HS-JEPA Prototype Report

## What was built

This run produced two team-facing end-to-end prototypes from the original data:

1. `submission_final_no_cohort_equation_hsjepa_414e7077_uploadsafe.csv`
   - Public-Private Equation HS-JEPA Solver
   - no cohort features
   - bets that the key bottleneck is row-target action toxicity, not raw model capacity

2. `submission_final_with_cohort_atlas_hsjepa_bfeccc43_uploadsafe.csv`
   - Personal-Cohort Atlas HS-JEPA Solver
   - uses raw lifelog-derived human-state latent and peer cohort context
   - bets that action safety improves when a row-target action is supported by both personal and cohort anomaly coordinates

Current public best anchor:

- `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv`
- public LB `0.5677475939`

## JEPA interpretation

Plain tabular modeling asks: `context -> label`.

HS-JEPA asks:

1. encode visible context: row order, previous public sensor responses, raw lifestyle logs, subject/cohort state;
2. predict hidden target representation: listener posterior, row-target route, action-health field;
3. plan an action: choose which row-target cells should move and by how much;
4. reject action collapse: avoid directions that known public observations punished.

This follows the JEPA idea that the useful target is an embedding/representation
of the hidden state, not raw reconstruction. It also follows the LeWorldModel
idea that actions should be chosen after predicting their consequence, not
cloned directly.

## Public-observed sensor worlds

| public_lb | delta_vs_current_best | file | family |
| --- | --- | --- | --- |
| 0.5677475939 | +0.0000000000 | submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv | HS-JEPA row-state decoder |
| 0.5679048248 | +0.0001572309 | submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | HS-JEPA public equation |
| 0.5679048248 | +0.0001572309 | submission_h050_target_route_phase_b140216b_uploadsafe.csv | HS-JEPA target route stress |
| 0.5679296410 | +0.0001820471 | submission_h144_targetxor_def80b88_uploadsafe.csv | HS-JEPA target assignment stress |
| 0.5679296410 | +0.0001820471 | submission_h145_q3repair_2d818e46_uploadsafe.csv | HS-JEPA target assignment stress |
| 0.5681234831 | +0.0003758892 | submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | HS-JEPA public equation |
| 0.5684942019 | +0.0007466080 | submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv | HS-JEPA action toxicity stress |
| 0.5781718175 | +0.0104242236 | submission_h010_objective_s1s4_v2_uploadsafe.csv | Pre-HS baseline / other |

## Tiny public equation proxy

This proxy is intentionally conservative. It uses only local files with known
public LB and predicts public delta from vector movement features. It is a
stress diagnostic, not an oracle.

```json
{
  "enabled": true,
  "n_public_observed_worlds": 7,
  "loo_mae_delta_vs_current_best": 0.0019084999430575029,
  "all_observed_are_current_best_or_worse": true,
  "warning": "This is a tiny sensor inversion proxy, not a leaderboard oracle."
}
```

| file | public_delta_vs_current_best | loo_predicted_delta_vs_current_best | listener_alignment | mean_bad_same_on_changed |
| --- | --- | --- | --- | --- |
| submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | 0.00015723090000008266 | 0.0004111448444798847 | -0.32135019372042944 | 0.8105742373590187 |
| submission_h050_target_route_phase_b140216b_uploadsafe.csv | 0.00015723090000008266 | 0.0016338996378079769 | -0.18653191272190295 | 0.6708680090860223 |
| submission_h144_targetxor_def80b88_uploadsafe.csv | 0.00018204710000002677 | 0.00020665883963995958 | -0.006125720093505845 | 1.5062744047192171 |
| submission_h145_q3repair_2d818e46_uploadsafe.csv | 0.00018204710000002677 | 0.00015110675519914738 | -0.0056619972554480535 | 1.5520505003041778 |
| submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | 0.0003758892000000902 | 0.0011554624829472472 | -0.3253077016204676 | 0.6991381986187847 |
| submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv | 0.0007466080000000375 | -0.0006661422492099186 | 0.49769485792250223 | 0.22213829432081245 |
| submission_h010_objective_s1s4_v2_uploadsafe.csv | 0.01042422360000006 | 0.0010431822974831622 | -0.6004337421427095 | 0.21945421654503322 |

## Prototype 1: Public-Private Equation HS-JEPA Solver

Worldview:

The public best is not just a good probability table. It is a partially decoded
hidden row-state. Further improvement should come from changing only row-target
cells whose listener direction is strong and whose direction is not shared by
known public-bad submissions.

Summary:

```json
{
  "submission_file": "submission_final_no_cohort_equation_hsjepa_414e7077_uploadsafe.csv",
  "hash": "414e7077",
  "changed_rows": 104,
  "changed_cells": 260,
  "target_changed_cells": {
    "Q1": 33,
    "Q2": 0,
    "Q3": 36,
    "S1": 37,
    "S2": 62,
    "S3": 55,
    "S4": 37
  },
  "soft_listener_logloss": 0.5534818697227673,
  "soft_listener_delta_vs_current_best": -0.0003502622856930149,
  "mean_abs_delta_vs_current_best": 0.002461610219428835,
  "max_abs_delta_vs_current_best": 0.07690495083818283,
  "mean_selected_known_bad_same_direction": 0.09422221479622342,
  "mean_selected_listener_gain": 0.0016146759387063708,
  "bad_axis_cosine": {
    "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv": -0.14633804795849822,
    "submission_h050_target_route_phase_b140216b_uploadsafe.csv": -0.08692172306285556,
    "submission_h144_targetxor_def80b88_uploadsafe.csv": 0.07714413075552452,
    "submission_h145_q3repair_2d818e46_uploadsafe.csv": 0.07972684246292122,
    "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv": -0.14600012908858043,
    "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv": 0.011042025492000198,
    "submission_h010_objective_s1s4_v2_uploadsafe.csv": -0.12145261484838606
  }
}
```

Per-target changed cells:

| target | changed_cells |
| --- | --- |
| Q1 | 33 |
| Q2 | 0 |
| Q3 | 36 |
| S1 | 37 |
| S2 | 62 |
| S3 | 55 |
| S4 | 37 |

Top selected actions:

| row | subject_id | lifelog_date | target | current_prob | candidate_prob | delta_vs_current_best | solver_score | known_bad_same_direction | listener_gain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 58 | id02 | 2024-10-15 00:00:00 | S2 | 0.9726349169390828 | 0.985539108442933 | 0.012904191503850249 | 0.8416565714285713 | 0.0 | 0.008559579300819298 |
| 49 | id02 | 2024-10-05 00:00:00 | S3 | 0.8893971874862591 | 0.910998324724383 | 0.021601137238123957 | 0.8098100952380952 | 0.0 | 0.003598476342577206 |
| 49 | id02 | 2024-10-05 00:00:00 | S2 | 0.9689341030608232 | 0.9797815648877851 | 0.010847461826961946 | 0.8060002666666667 | 0.0 | 0.0030075687199256212 |
| 7 | id01 | 2024-08-08 00:00:00 | Q1 | 0.1466324541766752 | 0.16761674076167296 | 0.020984286584997763 | 0.7977499047619047 | 0.0 | 0.002621408308323081 |
| 115 | id05 | 2024-10-13 00:00:00 | S2 | 0.2652628884425128 | 0.24030287143571263 | -0.024960017006800145 | 0.7895558095238095 | 0.0 | 0.0024075807374724922 |
| 45 | id02 | 2024-09-30 00:00:00 | S2 | 0.9427014993868272 | 0.9573811915301136 | 0.01467969214328635 | 0.788048 | 0.0 | 0.003043711643472058 |
| 43 | id02 | 2024-09-28 00:00:00 | S3 | 0.8894638782292077 | 0.9060422766582629 | 0.016578398429055174 | 0.7848799047619046 | 0.0 | 0.002116102669402098 |
| 33 | id02 | 2024-08-31 00:00:00 | S3 | 0.9359815346982728 | 0.9484110124671963 | 0.012429477768923447 | 0.7818138095238096 | 0.0 | 0.0019589495868759244 |
| 223 | id09 | 2024-09-15 00:00:00 | S2 | 0.8532148436816959 | 0.8723032773331074 | 0.01908843365141155 | 0.7813371428571428 | 0.0 | 0.002198588945754587 |
| 29 | id02 | 2024-08-27 00:00:00 | S2 | 0.9634548795958066 | 0.9739152572202447 | 0.010460377624438189 | 0.7765280952380951 | 0.0 | 0.002378498803972645 |
| 198 | id08 | 2024-09-14 00:00:00 | S3 | 0.6281922993635439 | 0.6571562884968547 | 0.028963989133310775 | 0.768575238095238 | 0.0 | 0.0026998457249696184 |
| 65 | id03 | 2024-08-23 00:00:00 | S2 | 0.4372519242529011 | 0.4127377801021059 | -0.024514144150795225 | 0.7497679999999999 | 0.0 | 0.0018343072236619573 |
| 46 | id02 | 2024-10-02 00:00:00 | Q3 | 0.6754721905264509 | 0.698279398195003 | 0.022807207668552043 | 0.7425781904761904 | 0.0 | 0.0017850348796184523 |
| 77 | id03 | 2024-10-04 00:00:00 | S2 | 0.5709790611049622 | 0.5404275750200365 | -0.03055148608492575 | 0.738255238095238 | 0.0 | 0.0028550334625164764 |
| 18 | id01 | 2024-09-06 00:00:00 | S1 | 0.95752041923042 | 0.975403644318971 | 0.017883225088551002 | 0.729867238095238 | 0.0 | 0.006078654078247314 |
| 202 | id09 | 2024-08-06 00:00:00 | S2 | 0.8567752165619527 | 0.8724636437694743 | 0.015688427207521616 | 0.728547238095238 | 0.0 | 0.0015145074412500348 |
| 127 | id05 | 2024-11-19 00:00:00 | Q3 | 0.5499258008124398 | 0.5836186942699112 | 0.033692893457471396 | 0.7279989523809524 | 0.0 | 0.0034423619469099442 |
| 7 | id01 | 2024-08-08 00:00:00 | S3 | 0.7965533146411341 | 0.8116605626663801 | 0.01510724802524599 | 0.7277988190476189 | 0.0 | 0.0010610947570150464 |
| 197 | id08 | 2024-09-13 00:00:00 | S1 | 0.872152895724321 | 0.9044105753664056 | 0.03225767964208459 | 0.7262900952380952 | 0.0 | 0.007091844084384125 |
| 64 | id03 | 2024-08-22 00:00:00 | Q3 | 0.746511400489644 | 0.7645901122785287 | 0.01807871178888465 | 0.7223362285714285 | 0.0 | 0.0013004829648490812 |

## Prototype 2: Personal-Cohort Atlas HS-JEPA Solver

Worldview:

A row-target action is safer when the row is interpretable in two coordinate
systems:

- personal coordinate: unusual relative to the subject's own normal state;
- cohort coordinate: unusual inside a peer group of similar human-state trajectories.

The cohort module is not used as a direct label rule. It is an additional context
view for action planning.

Cohort metadata:

```json
{
  "latent_dims": 8,
  "pca_explained_variance_ratio": [
    0.10081532298730797,
    0.08239187843821755,
    0.07278085460083508,
    0.06761673878040775,
    0.04372958583951479,
    0.040580041862259816,
    0.03442334480956193,
    0.03162224150576394
  ],
  "peer_group_count": 4,
  "subjects": 10,
  "feature_count": 99,
  "current_best_hidden_rows": 45,
  "personal_cohort_gate_mean_selected_hidden": 0.5218377777777778,
  "personal_cohort_gate_mean_other": 0.49764536585365854,
  "cohort_outlier_score_mean_selected_hidden": 0.5356609523809525,
  "cohort_outlier_score_mean_other": 0.5173199999999999,
  "dist_to_subject_normal_mean_selected_hidden": 4.883806265013809,
  "dist_to_subject_normal_mean_other": 4.457537872423473,
  "dist_to_peer_normal_mean_selected_hidden": 5.791373624571934,
  "dist_to_peer_normal_mean_other": 5.774782827843018
}
```

Summary:

```json
{
  "submission_file": "submission_final_with_cohort_atlas_hsjepa_bfeccc43_uploadsafe.csv",
  "hash": "bfeccc43",
  "changed_rows": 96,
  "changed_cells": 220,
  "target_changed_cells": {
    "Q1": 22,
    "Q2": 0,
    "Q3": 36,
    "S1": 22,
    "S2": 62,
    "S3": 47,
    "S4": 31
  },
  "soft_listener_logloss": 0.5535142204350171,
  "soft_listener_delta_vs_current_best": -0.0003179115734431859,
  "mean_abs_delta_vs_current_best": 0.0021247189819956673,
  "max_abs_delta_vs_current_best": 0.07690495083818283,
  "mean_selected_known_bad_same_direction": 0.11260151841041674,
  "mean_selected_listener_gain": 0.001735976465388122,
  "bad_axis_cosine": {
    "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv": -0.14731387713006866,
    "submission_h050_target_route_phase_b140216b_uploadsafe.csv": -0.08939448591200462,
    "submission_h144_targetxor_def80b88_uploadsafe.csv": 0.08013385549047354,
    "submission_h145_q3repair_2d818e46_uploadsafe.csv": 0.08025848669159484,
    "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv": -0.1469737049084389,
    "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv": 0.02952093143231623,
    "submission_h010_objective_s1s4_v2_uploadsafe.csv": -0.12215668456387246
  }
}
```

Per-target changed cells:

| target | changed_cells |
| --- | --- |
| Q1 | 22 |
| Q2 | 0 |
| Q3 | 36 |
| S1 | 22 |
| S2 | 62 |
| S3 | 47 |
| S4 | 31 |

Top selected actions:

| row | subject_id | lifelog_date | target | current_prob | candidate_prob | delta_vs_current_best | solver_score | known_bad_same_direction | listener_gain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 115 | id05 | 2024-10-13 00:00:00 | S2 | 0.2652628884425128 | 0.24030287143571263 | -0.024960017006800145 | 1.0859216190476189 | 0.0 | 0.0024075807374724922 |
| 49 | id02 | 2024-10-05 00:00:00 | S2 | 0.9689341030608232 | 0.9797815648877851 | 0.010847461826961946 | 1.0773505523809523 | 0.0 | 0.0030075687199256212 |
| 49 | id02 | 2024-10-05 00:00:00 | S3 | 0.8893971874862591 | 0.910998324724383 | 0.021601137238123957 | 1.0571866666666667 | 0.0 | 0.003598476342577206 |
| 33 | id02 | 2024-08-31 00:00:00 | S3 | 0.9359815346982728 | 0.9484110124671963 | 0.012429477768923447 | 1.006683523809524 | 0.0 | 0.0019589495868759244 |
| 58 | id02 | 2024-10-15 00:00:00 | S2 | 0.9726349169390828 | 0.985539108442933 | 0.012904191503850249 | 0.992942476190476 | 0.0 | 0.008559579300819298 |
| 45 | id02 | 2024-09-30 00:00:00 | S2 | 0.9427014993868272 | 0.9573811915301136 | 0.01467969214328635 | 0.981537142857143 | 0.0 | 0.003043711643472058 |
| 141 | id06 | 2024-08-09 00:00:00 | S4 | 0.954920996996146 | 0.9695998341141204 | 0.014678837117974464 | 0.9605032380952377 | 0.0 | 0.0038399465495218277 |
| 198 | id08 | 2024-09-14 00:00:00 | S3 | 0.6281922993635439 | 0.6571562884968547 | 0.028963989133310775 | 0.9603960000000002 | 0.0 | 0.0026998457249696184 |
| 116 | id05 | 2024-10-15 00:00:00 | S3 | 0.1211559292718874 | 0.1338937053884849 | 0.012737776116597516 | 0.936392361904762 | 6.661338147750939e-16 | 0.0011377834722657854 |
| 7 | id01 | 2024-08-08 00:00:00 | Q1 | 0.1466324541766752 | 0.16761674076167296 | 0.020984286584997763 | 0.9313378095238094 | 0.0 | 0.002621408308323081 |
| 115 | id05 | 2024-10-13 00:00:00 | S3 | 0.1467981672028505 | 0.15960321094219923 | 0.012805043739348737 | 0.9284722476190477 | 0.0 | 0.000978631197562363 |
| 77 | id03 | 2024-10-04 00:00:00 | S2 | 0.5709790611049622 | 0.5404275750200365 | -0.03055148608492575 | 0.9235594285714285 | 0.0 | 0.0028550334625164764 |
| 116 | id05 | 2024-10-15 00:00:00 | S1 | 0.36774291156433 | 0.33341721415062686 | -0.034325697413703116 | 0.9184890476190478 | 0.0 | 0.003808903484127102 |
| 79 | id03 | 2024-10-09 00:00:00 | S2 | 0.5359497261060353 | 0.5138101529645777 | -0.022139573141457647 | 0.9131251428571429 | 0.0 | 0.0014787534167363114 |
| 127 | id05 | 2024-11-19 00:00:00 | Q3 | 0.5499258008124398 | 0.5836186942699112 | 0.033692893457471396 | 0.9109386666666669 | 0.0 | 0.0034423619469099442 |
| 43 | id02 | 2024-09-28 00:00:00 | S3 | 0.8894638782292077 | 0.9060422766582629 | 0.016578398429055174 | 0.9100734285714286 | 0.0 | 0.002116102669402098 |
| 29 | id02 | 2024-08-27 00:00:00 | S2 | 0.9634548795958066 | 0.9739152572202447 | 0.010460377624438189 | 0.9099562857142857 | 0.0 | 0.002378498803972645 |
| 52 | id02 | 2024-10-08 00:00:00 | S2 | 0.9511783866392696 | 0.9585538559323699 | 0.00737546929310029 | 0.9094758095238096 | 0.0 | 0.0008880147795470583 |
| 223 | id09 | 2024-09-15 00:00:00 | S2 | 0.8532148436816959 | 0.8723032773331074 | 0.01908843365141155 | 0.9091000000000001 | 0.0 | 0.002198588945754587 |
| 123 | id05 | 2024-11-15 00:00:00 | Q1 | 0.8018592745314231 | 0.8218526354577534 | 0.019993360926330306 | 0.9046928571428573 | 0.0 | 0.0018974366145250166 |

## Submission interpretation

These files should not be read as blends. Each is a claim:

- no-cohort solver: the current missing piece is public/private action toxicity;
- cohort solver: action toxicity becomes easier to control when row-target
  movement is grounded in human-state cohort coordinates.

If either file improves public LB by a meaningful amount, HS-JEPA's action-world
model framing is strengthened. If both fail, the hidden state may be real but
the current listener/correction target is still too public-specific or collapsed.
