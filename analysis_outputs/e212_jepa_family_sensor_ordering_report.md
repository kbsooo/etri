# E212 JEPA Family Sensor Ordering

## Purpose

E212 freezes the next JEPA-family submission order before public feedback. It does not train a model and does not write a new submission tensor.

The key distinction is now operational:

- E209 is the raw feature-neighbor JEPA control.
- E210 is the blunt dependency-gated hard-tail sensor.
- E211 is the target-specific JEPA translation: Q3 raw body, S4 dependency-consistent movement.

## Main Decision

If using one slot for maximum structured JEPA survival, submit `analysis_outputs/submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv`.

If using one slot for the clean current-frontier JEPA sensor, submit `analysis_outputs/submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv`.

E209 remains the raw-JEPA control. E210 is demoted behind E211 because it has strong hard-tail anatomy but loses the local JEPA body and geometry that E211 preserves.

## Structured Survival Ranking

| survival_rank | clean_sensor_rank | family | anchor | hypothesis_name | structured_survival_score | clean_sensor_score | local_delta | local_vs_parent_delta | geometry_delta | geometry_win_rate | survival_score | vs_e95_expected_delta_focus_mean | vs_e95_top1_over_abs_expected | max_bad_cos | submission_file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 5 | E211 | e154 | target_specific_q3raw_s4closer | 0.831942147559 | 0.898557109757 | -0.00131506397312 | -4.23401133944e-05 | -0.000619840063434 | 0.875 | 0.036910484723 | -0.00068511481246 | 0.229657246648 | 0.184276224111 | submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv |
| 2 | 4 | E211 | e154 | target_specific_q3raw_s4toward | 0.83178065131 | 0.899050473829 | -0.00131798437809 | -4.52605183622e-05 | -0.000659023923106 | 0.875 | 0.0367537823735 | -0.000680355002983 | 0.231263944231 | 0.185846211417 | submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e154_a0p5_50e6b7ec.csv |
| 3 | 1 | E211 | e95 | target_specific_q3raw_s4toward | 0.830444854643 | 0.962262285409 | -0.00131798437809 | -4.52605183622e-05 | -0.000659023923106 | 0.875 | 0.0354525109606 | -0.000654329574727 | 0.240462280087 | 0.158077637908 | submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv |
| 4 | 2 | E211 | e95 | target_specific_q3raw_s4closer | 0.82868427636 | 0.961722483317 | -0.00131506397312 | -4.23401133944e-05 | -0.000619840063434 | 0.875 | 0.0350240936802 | -0.000647386991604 | 0.243040999445 | 0.157218228676 | submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e95_a0p5_8e3dc02d.csv |
| 5 | 6 | E209 | e154 | raw_jepa_q3_s4_translation | 0.733690380495 | 0.855334996703 | -0.00127272385973 | 0 | -0.000794598083125 | 0.75 | 0.0138531889108 | -0.000217865472228 | 0.361098020394 | 0.202004726541 | submission_e209_jepa_q3_center_c010_s4_rank_e154_s0p25_1e4591ca.csv |
| 6 | 3 | E209 | e95 | raw_jepa_q3_s4_translation | 0.731930456213 | 0.920017338867 | -0.00127272385973 | 0 | -0.000794598083125 | 0.75 | 0.0124452882413 | -0.000189667364307 | 0.41478295974 | 0.155737509075 | submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv |
| 7 | 7 | E209 | e95 | raw_jepa_s4_only | 0.590647825481 | 0.756320103004 | -0.000447679261111 | 0 | -0.000639975306464 | 0.875 | 0.0111751119218 | -0.000188668478948 | 0.67188379932 | 0.060514994942 | submission_e209_jepa_s4_rank_e95_s0p75_0ed14a13.csv |
| 8 | 8 | E209 | e154 | raw_jepa_s4_only | 0.58974018206 | 0.690725050678 | -0.000447679261111 | 0 | -0.000639975306464 | 0.875 | 0.0126602265524 | -0.00021802703353 | 0.637509996172 | 0.0907853374129 | submission_e209_jepa_s4_rank_e154_s0p75_030e88de.csv |
| 9 | 11 | E210 | e154 | blunt_dependency_gate | 0.531386277348 | 0.447504529747 | -0.000549773120096 | 0.000722950739631 | -2.5798438442e-05 | 0.5 | 0.0686535004398 | -0.0013636087295 | 0.173079247071 | 0.123250340544 | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e154_s0p75_67d1b011.csv |
| 10 | 9 | E210 | e95 | blunt_dependency_gate | 0.530695576415 | 0.509691249358 | -0.000549773120096 | 0.000722950739631 | -2.5798438442e-05 | 0.5 | 0.0678506847732 | -0.00134755241617 | 0.175141515365 | 0.111610204042 | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e95_s0p75_35e6b0a9.csv |
| 11 | 12 | E210 | e154 | blunt_dependency_gate | 0.519967297241 | 0.431619900869 | -0.000482103294315 | 0.000790620565412 | -9.60356056601e-05 | 0.5 | 0.0695000908637 | -0.00137873326197 | 0.171180589249 | 0.1229264839 | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e154_s1p0_2f69729d.csv |
| 12 | 10 | E210 | e95 | blunt_dependency_gate | 0.519676018833 | 0.493360441798 | -0.000482103294315 | 0.000790620565412 | -9.60356056601e-05 | 0.5 | 0.0690164444445 | -0.00136906033358 | 0.172390044771 | 0.114954830805 | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv |

## Clean Sensor Ranking

| survival_rank | clean_sensor_rank | family | anchor | hypothesis_name | structured_survival_score | clean_sensor_score | local_delta | local_vs_parent_delta | geometry_delta | geometry_win_rate | survival_score | vs_e95_expected_delta_focus_mean | vs_e95_top1_over_abs_expected | max_bad_cos | submission_file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 1 | E211 | e95 | target_specific_q3raw_s4toward | 0.830444854643 | 0.962262285409 | -0.00131798437809 | -4.52605183622e-05 | -0.000659023923106 | 0.875 | 0.0354525109606 | -0.000654329574727 | 0.240462280087 | 0.158077637908 | submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv |
| 4 | 2 | E211 | e95 | target_specific_q3raw_s4closer | 0.82868427636 | 0.961722483317 | -0.00131506397312 | -4.23401133944e-05 | -0.000619840063434 | 0.875 | 0.0350240936802 | -0.000647386991604 | 0.243040999445 | 0.157218228676 | submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e95_a0p5_8e3dc02d.csv |
| 6 | 3 | E209 | e95 | raw_jepa_q3_s4_translation | 0.731930456213 | 0.920017338867 | -0.00127272385973 | 0 | -0.000794598083125 | 0.75 | 0.0124452882413 | -0.000189667364307 | 0.41478295974 | 0.155737509075 | submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv |
| 2 | 4 | E211 | e154 | target_specific_q3raw_s4toward | 0.83178065131 | 0.899050473829 | -0.00131798437809 | -4.52605183622e-05 | -0.000659023923106 | 0.875 | 0.0367537823735 | -0.000680355002983 | 0.231263944231 | 0.185846211417 | submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e154_a0p5_50e6b7ec.csv |
| 1 | 5 | E211 | e154 | target_specific_q3raw_s4closer | 0.831942147559 | 0.898557109757 | -0.00131506397312 | -4.23401133944e-05 | -0.000619840063434 | 0.875 | 0.036910484723 | -0.00068511481246 | 0.229657246648 | 0.184276224111 | submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv |
| 5 | 6 | E209 | e154 | raw_jepa_q3_s4_translation | 0.733690380495 | 0.855334996703 | -0.00127272385973 | 0 | -0.000794598083125 | 0.75 | 0.0138531889108 | -0.000217865472228 | 0.361098020394 | 0.202004726541 | submission_e209_jepa_q3_center_c010_s4_rank_e154_s0p25_1e4591ca.csv |
| 7 | 7 | E209 | e95 | raw_jepa_s4_only | 0.590647825481 | 0.756320103004 | -0.000447679261111 | 0 | -0.000639975306464 | 0.875 | 0.0111751119218 | -0.000188668478948 | 0.67188379932 | 0.060514994942 | submission_e209_jepa_s4_rank_e95_s0p75_0ed14a13.csv |
| 8 | 8 | E209 | e154 | raw_jepa_s4_only | 0.58974018206 | 0.690725050678 | -0.000447679261111 | 0 | -0.000639975306464 | 0.875 | 0.0126602265524 | -0.00021802703353 | 0.637509996172 | 0.0907853374129 | submission_e209_jepa_s4_rank_e154_s0p75_030e88de.csv |
| 10 | 9 | E210 | e95 | blunt_dependency_gate | 0.530695576415 | 0.509691249358 | -0.000549773120096 | 0.000722950739631 | -2.5798438442e-05 | 0.5 | 0.0678506847732 | -0.00134755241617 | 0.175141515365 | 0.111610204042 | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e95_s0p75_35e6b0a9.csv |
| 12 | 10 | E210 | e95 | blunt_dependency_gate | 0.519676018833 | 0.493360441798 | -0.000482103294315 | 0.000790620565412 | -9.60356056601e-05 | 0.5 | 0.0690164444445 | -0.00136906033358 | 0.172390044771 | 0.114954830805 | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv |
| 9 | 11 | E210 | e154 | blunt_dependency_gate | 0.531386277348 | 0.447504529747 | -0.000549773120096 | 0.000722950739631 | -2.5798438442e-05 | 0.5 | 0.0686535004398 | -0.0013636087295 | 0.173079247071 | 0.123250340544 | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e154_s0p75_67d1b011.csv |
| 11 | 12 | E210 | e154 | blunt_dependency_gate | 0.519967297241 | 0.431619900869 | -0.000482103294315 | 0.000790620565412 | -9.60356056601e-05 | 0.5 | 0.0695000908637 | -0.00137873326197 | 0.171180589249 | 0.1229264839 | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e154_s1p0_2f69729d.csv |

## Control / Falsification Value

| control_rank | family | anchor | hypothesis_name | control_value_score | anchor_purity_note | sensor_role | submission_file |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | E209 | e95 | raw_jepa_q3_s4_translation | 0.955 | clean current-frontier sensor | raw JEPA control; cleanest falsifier for actual JEPA usefulness | submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv |
| 2 | E209 | e95 | raw_jepa_s4_only | 0.93 | clean current-frontier sensor | raw JEPA control; narrow target test | submission_e209_jepa_s4_rank_e95_s0p75_0ed14a13.csv |
| 3 | E209 | e154 | raw_jepa_q3_s4_translation | 0.822 | survival-oriented but E154-confounded | raw JEPA control; cleanest falsifier for actual JEPA usefulness | submission_e209_jepa_q3_center_c010_s4_rank_e154_s0p25_1e4591ca.csv |
| 4 | E211 | e95 | target_specific_q3raw_s4toward | 0.8 | clean current-frontier sensor | current strongest clean E95-frontier JEPA sensor | submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv |
| 5 | E211 | e95 | target_specific_q3raw_s4closer | 0.8 | clean current-frontier sensor | current strongest clean E95-frontier JEPA sensor | submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e95_a0p5_8e3dc02d.csv |
| 6 | E209 | e154 | raw_jepa_s4_only | 0.797 | survival-oriented but E154-confounded | raw JEPA control; narrow target test | submission_e209_jepa_s4_rank_e154_s0p75_030e88de.csv |
| 7 | E211 | e154 | target_specific_q3raw_s4closer | 0.667 | survival-oriented but E154-confounded | current strongest JEPA worldview; E154 anchor adds survival but confounds attribution | submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv |
| 8 | E211 | e154 | target_specific_q3raw_s4toward | 0.667 | survival-oriented but E154-confounded | current strongest JEPA worldview; E154 anchor adds survival but confounds attribution | submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e154_a0p5_50e6b7ec.csv |
| 9 | E210 | e95 | blunt_dependency_gate | 0.467884711144 | clean current-frontier sensor | high hard-tail sensor, but it loses the E209 local body | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e95_s0p75_35e6b0a9.csv |
| 10 | E210 | e95 | blunt_dependency_gate | 0.466339010072 | clean current-frontier sensor | high hard-tail sensor, but it loses the E209 local body | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv |
| 11 | E210 | e154 | blunt_dependency_gate | 0.334884711144 | survival-oriented but E154-confounded | high hard-tail sensor, but it loses the E209 local body | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e154_s0p75_67d1b011.csv |
| 12 | E210 | e154 | blunt_dependency_gate | 0.333339010072 | survival-oriented but E154-confounded | high hard-tail sensor, but it loses the E209 local body | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e154_s1p0_2f69729d.csv |

## Pairwise Movement Similarity

| file_a | file_b | cosine_vs_e95_movement | mean_abs_logit_gap | max_abs_logit_gap |
| --- | --- | --- | --- | --- |
| submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv | submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e154_a0p5_50e6b7ec.csv | 0.996351024291 | 0.000116798129903 | 0.100896999295 |
| submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv | submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e95_a0p5_8e3dc02d.csv | 0.994943050012 | 0.000156038380012 | 0.100896999295 |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e154_s0p75_67d1b011.csv | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e95_s0p75_35e6b0a9.csv | 0.988705291362 | 0.00204098901564 | 0.0613621548418 |
| submission_e209_jepa_s4_rank_e154_s0p75_030e88de.csv | submission_e209_jepa_s4_rank_e95_s0p75_0ed14a13.csv | 0.98586284409 | 0.00201764694775 | 0.0268443588924 |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e154_s1p0_2f69729d.csv | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv | 0.984763101316 | 0.00210159270016 | 0.146905066716 |
| submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e154_a0p5_50e6b7ec.csv | submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv | 0.984706429293 | 0.00201764694775 | 0.0268443588924 |
| submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv | submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e95_a0p5_8e3dc02d.csv | 0.984096703197 | 0.00203536434193 | 0.049837938751 |
| submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv | submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv | 0.980771539458 | 0.00213444507765 | 0.100896999295 |
| submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e154_a0p5_50e6b7ec.csv | submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e95_a0p5_8e3dc02d.csv | 0.980505758232 | 0.00215216247183 | 0.100896999295 |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e95_s0p75_35e6b0a9.csv | 0.969196536909 | 0.00040968640185 | 0.370228761389 |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e154_s1p0_2f69729d.csv | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e154_s0p75_67d1b011.csv | 0.967854760835 | 0.000446846045191 | 0.370228761389 |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e154_s0p75_67d1b011.csv | 0.962632609852 | 0.0023608495194 | 0.352993255394 |
| submission_e209_jepa_q3_center_c010_s4_rank_e154_s0p25_1e4591ca.csv | submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv | 0.953216922336 | 0.00201764694775 | 0.0268443588924 |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e154_s1p0_2f69729d.csv | submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e95_s0p75_35e6b0a9.csv | 0.952816104383 | 0.00248783506084 | 0.387464267384 |
| submission_e209_jepa_q3_center_c010_s4_rank_e154_s0p25_1e4591ca.csv | submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e154_a0p5_50e6b7ec.csv | 0.902336940963 | 0.0078736789852 | 0.137673883784 |
| submission_e209_jepa_q3_center_c010_s4_rank_e154_s0p25_1e4591ca.csv | submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv | 0.899310945126 | 0.0078736789852 | 0.137673883784 |
| submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv | submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv | 0.89810184911 | 0.0078736789852 | 0.137673883784 |
| submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv | submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e95_a0p5_8e3dc02d.csv | 0.893560192974 | 0.0078736789852 | 0.137673883784 |
| submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv | submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e154_a0p5_50e6b7ec.csv | 0.881402760919 | 0.00942907443748 | 0.137673883784 |
| submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv | submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv | 0.877857974259 | 0.00942907443748 | 0.137673883784 |

## Feedback Routebook

| submission_file | family | anchor | outcome | public_lb_lo_exclusive | public_lb_hi_inclusive | worldview_if_observed | weakened_if_observed | pre_registered_next_action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv | E211 | e154 | clean_win | -inf | 0.5762843298 | target-specific JEPA plus E154 repaired-branch survival | raw E209-only and blunt E210-first ordering | submit the E211 E95 clean twin to separate JEPA from E154 confounding |
| submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv | E211 | e154 | micro_win | 0.5762843298 | 0.5762893298 | target-specific JEPA plus E154 repaired-branch survival | raw E209-only and blunt E210-first ordering | submit the E211 E95 clean twin to separate JEPA from E154 confounding |
| submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv | E211 | e154 | tie | 0.5762893298 | 0.5762933298 | hard-label resolution bottleneck; signal may be real but under public-cell noise | large JEPA frontier break | do not tune amplitude; use the paired clean/E154 or raw-control contrast |
| submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv | E211 | e154 | small_loss_branch_alive | 0.5762933298 | 0.576300366 | hard-label resolution bottleneck; signal may be real but under public-cell noise | large JEPA frontier break | do not tune amplitude; use the paired clean/E154 or raw-control contrast |
| submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv | E211 | e154 | mixmin_safe_loss | 0.576300366 | 0.5763066405 | same plateau law as E101/E176: local signal exists but public tail rejects the translation | current probability-graft JEPA path | try the raw E209 control only if E211 failed; otherwise rebuild representation before submission |
| submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv | E211 | e154 | branch_loss | 0.5763066405 | 0.5763416405 | JEPA probability graft is misaligned with public hidden cells | E209/E210/E211 family as expected-score lane | close this JEPA graft family and return to representation/objective design |
| submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv | E211 | e154 | hard_fail | 0.5763416405 | inf | JEPA probability graft is misaligned with public hidden cells | E209/E210/E211 family as expected-score lane | close this JEPA graft family and return to representation/objective design |
| submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv | E211 | e95 | clean_win | -inf | 0.5762843298 | clean target-specific JEPA translation | JEPA-is-only-E154-confounding | test the E211 E154 twin only if chasing survival, otherwise search a second non-collinear JEPA axis |
| submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv | E211 | e95 | micro_win | 0.5762843298 | 0.5762893298 | clean target-specific JEPA translation | JEPA-is-only-E154-confounding | test the E211 E154 twin only if chasing survival, otherwise search a second non-collinear JEPA axis |
| submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv | E211 | e95 | tie | 0.5762893298 | 0.5762933298 | hard-label resolution bottleneck; signal may be real but under public-cell noise | large JEPA frontier break | do not tune amplitude; use the paired clean/E154 or raw-control contrast |
| submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv | E211 | e95 | small_loss_branch_alive | 0.5762933298 | 0.576300366 | hard-label resolution bottleneck; signal may be real but under public-cell noise | large JEPA frontier break | do not tune amplitude; use the paired clean/E154 or raw-control contrast |
| submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv | E211 | e95 | mixmin_safe_loss | 0.576300366 | 0.5763066405 | same plateau law as E101/E176: local signal exists but public tail rejects the translation | current probability-graft JEPA path | try the raw E209 control only if E211 failed; otherwise rebuild representation before submission |
| submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv | E211 | e95 | branch_loss | 0.5763066405 | 0.5763416405 | JEPA probability graft is misaligned with public hidden cells | E209/E210/E211 family as expected-score lane | close this JEPA graft family and return to representation/objective design |
| submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv | E211 | e95 | hard_fail | 0.5763416405 | inf | JEPA probability graft is misaligned with public hidden cells | E209/E210/E211 family as expected-score lane | close this JEPA graft family and return to representation/objective design |
| submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv | E209 | e95 | clean_win | -inf | 0.5762843298 | raw feature-neighbor JEPA translation | dependency gate necessity | promote E211 only if needing S4 safety; otherwise search new raw JEPA target axes |
| submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv | E209 | e95 | micro_win | 0.5762843298 | 0.5762893298 | raw feature-neighbor JEPA translation | dependency gate necessity | promote E211 only if needing S4 safety; otherwise search new raw JEPA target axes |
| submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv | E209 | e95 | tie | 0.5762893298 | 0.5762933298 | hard-label resolution bottleneck; signal may be real but under public-cell noise | large JEPA frontier break | do not tune amplitude; use the paired clean/E154 or raw-control contrast |
| submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv | E209 | e95 | small_loss_branch_alive | 0.5762933298 | 0.576300366 | hard-label resolution bottleneck; signal may be real but under public-cell noise | large JEPA frontier break | do not tune amplitude; use the paired clean/E154 or raw-control contrast |
| submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv | E209 | e95 | mixmin_safe_loss | 0.576300366 | 0.5763066405 | same plateau law as E101/E176: local signal exists but public tail rejects the translation | current probability-graft JEPA path | try the raw E209 control only if E211 failed; otherwise rebuild representation before submission |
| submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv | E209 | e95 | branch_loss | 0.5763066405 | 0.5763416405 | JEPA probability graft is misaligned with public hidden cells | E209/E210/E211 family as expected-score lane | close this JEPA graft family and return to representation/objective design |
| submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv | E209 | e95 | hard_fail | 0.5763416405 | inf | JEPA probability graft is misaligned with public hidden cells | E209/E210/E211 family as expected-score lane | close this JEPA graft family and return to representation/objective design |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv | E210 | e95 | clean_win | -inf | 0.5762843298 | dependency-tail localization | raw JEPA body sufficiency | compare against E211 before another blunt dependency gate |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv | E210 | e95 | micro_win | 0.5762843298 | 0.5762893298 | dependency-tail localization | raw JEPA body sufficiency | compare against E211 before another blunt dependency gate |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv | E210 | e95 | tie | 0.5762893298 | 0.5762933298 | hard-label resolution bottleneck; signal may be real but under public-cell noise | large JEPA frontier break | do not tune amplitude; use the paired clean/E154 or raw-control contrast |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv | E210 | e95 | small_loss_branch_alive | 0.5762933298 | 0.576300366 | hard-label resolution bottleneck; signal may be real but under public-cell noise | large JEPA frontier break | do not tune amplitude; use the paired clean/E154 or raw-control contrast |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv | E210 | e95 | mixmin_safe_loss | 0.576300366 | 0.5763066405 | same plateau law as E101/E176: local signal exists but public tail rejects the translation | current probability-graft JEPA path | try the raw E209 control only if E211 failed; otherwise rebuild representation before submission |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv | E210 | e95 | branch_loss | 0.5763066405 | 0.5763416405 | JEPA probability graft is misaligned with public hidden cells | E209/E210/E211 family as expected-score lane | close this JEPA graft family and return to representation/objective design |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv | E210 | e95 | hard_fail | 0.5763416405 | inf | JEPA probability graft is misaligned with public hidden cells | E209/E210/E211 family as expected-score lane | close this JEPA graft family and return to representation/objective design |

## Interpretation

- If the E211 E95 clean sensor wins, actual JEPA is useful beyond E154 branch confounding.
- If only the E211 E154 file wins, the signal is mixed: JEPA may help, but the repaired-branch anchor is doing nontrivial work.
- If E211 loses but E209 later wins, the S4 dependency gate is overfit and raw JEPA body should be restored.
- If E211 and E209 both lose, the current JEPA probability-graft path is not the 0.54 route; the next JEPA attempt must change the target representation, not the blend amplitude.
