# E219 E216 Public Miss Anatomy

## Question

E216 selected a masked-family JEPA S2-only graft, but public LB was `0.5772865088`, `+0.0009951790` worse than E95. This audit asks whether that scalar is explainable by the E154 anchor body, the S2 graft, or their interaction.

## Pair-Level Hard-Label Capacity

| new | base | moved_cells | moved_rows | targets | expected_focus_mean | all_support_delta | all_adverse_delta | total_swing | obs_over_adverse | obs_over_swing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e216_e154 | e95 | 505 | 250 | Q1,Q3,S2,S3,S4 | -0.000318150 | -0.008276083 | 0.006833222 | 0.015109305 | 0.145638323 | 0.065865305 |
| e216_e154 | e154 | 250 | 250 | S2 | -0.000288312 | -0.007321835 | 0.006048480 | 0.013370316 |  |  |
| e216_e95 | e95 | 250 | 250 | S2 | -0.000287798 | -0.007321321 | 0.006048995 | 0.013370316 | 0.164519740 | 0.074431974 |
| e216_e154_s05 | e95 | 505 | 250 | Q1,Q3,S2,S3,S4 | -0.000257716 | -0.005873702 | 0.004783952 | 0.010657654 | 0.208024461 | 0.093376933 |
| e216_e154_s05 | e154 | 250 | 250 | S2 | -0.000227878 | -0.004916894 | 0.003996650 | 0.008913544 |  |  |
| e216_e95_s05 | e95 | 250 | 250 | S2 | -0.000227532 | -0.004916547 | 0.003996996 | 0.008913544 | 0.248981707 | 0.111647962 |
| e154 | e95 | 294 | 139 | Q1,Q3,S2,S3,S4 | -0.000029838 | -0.001093577 | 0.000924070 | 0.002017647 | 1.076951520 | 0.493237432 |
| e101 | e95 | 50 | 48 | Q2,S3 | 0.000046398 | -0.000096679 | 0.000211677 | 0.000308355 | 4.701409756 | 3.227376486 |
| mixmin | e95 | 550 | 250 | Q2,S1,S2,S3 | 0.000144543 | -0.002701750 | 0.002846528 | 0.005548278 | 0.349611472 | 0.179367170 |

## E216-vs-E95 Segment Decomposition

| group_type | group | segments | unique_cells | expected_focus_mean | support_delta | adverse_delta | total_swing | support_prob_focus_mean_swing_weighted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| component | e154_to_e216_s2_graft | 250 | 250 | -0.000288312 | -0.007321835 | 0.006048480 | 0.013370316 | 0.473944871 |
| component | e95_to_e154_body | 294 | 294 | -0.000029838 | -0.001093577 | 0.000924070 | 0.002017647 | 0.472782386 |
| component_target | e154_to_e216_s2_graft:S2 | 250 | 250 | -0.000288312 | -0.007321835 | 0.006048480 | 0.013370316 | 0.473944871 |
| component_target | e95_to_e154_body:Q1 | 70 | 70 | -0.000017548 | -0.000245415 | 0.000225641 | 0.000471056 | 0.516263266 |
| component_target | e95_to_e154_body:Q3 | 95 | 95 | -0.000001468 | -0.000385266 | 0.000333463 | 0.000718729 | 0.466003422 |
| component_target | e95_to_e154_body:S2 | 39 | 39 | 0.000001380 | -0.000115229 | 0.000155534 | 0.000270763 | 0.569334514 |
| component_target | e95_to_e154_body:S3 | 56 | 56 | 0.000010579 | -0.000186779 | 0.000120801 | 0.000307580 | 0.358352446 |
| component_target | e95_to_e154_body:S4 | 34 | 34 | -0.000022780 | -0.000160887 | 0.000088632 | 0.000249518 | 0.446507150 |
| target | Q1 | 70 | 70 | -0.000017548 | -0.000245415 | 0.000225641 | 0.000471056 | 0.516263266 |
| target | Q3 | 95 | 95 | -0.000001468 | -0.000385266 | 0.000333463 | 0.000718729 | 0.466003422 |
| target | S2 | 289 | 250 | -0.000286933 | -0.007437064 | 0.006204015 | 0.013641079 | 0.475838271 |
| target | S3 | 56 | 56 | 0.000010579 | -0.000186779 | 0.000120801 | 0.000307580 | 0.358352446 |
| target | S4 | 34 | 34 | -0.000022780 | -0.000160887 | 0.000088632 | 0.000249518 | 0.446507150 |

## Hidden-Label Simulation

| prior | mean_delta | std_delta | prob_win_delta_lt0 | prob_loss_delta_gt0 | prob_ge_half_observed | prob_ge_observed | near_observed_count | near_observed_mean_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global | -0.000431819 | 0.000482505 | 0.814695000 | 0.185305000 | 0.026600000 | 0.001215000 | 2000 | 0.000830655 |
| subject | -0.000268347 | 0.000472731 | 0.715185000 | 0.284815000 | 0.052845000 | 0.003395000 | 2000 | 0.000935633 |
| nearest_hard085 | -0.000252946 | 0.000466701 | 0.704235000 | 0.295765000 | 0.052650000 | 0.003370000 | 2000 | 0.000931014 |
| focus_mean | -0.000318228 | 0.000479120 | 0.746180000 | 0.253820000 | 0.043915000 | 0.002920000 | 2000 | 0.000916165 |

## Near-Observed Component Attribution

| prior | condition | group | mean_component_delta | share_of_total_mean |
| --- | --- | --- | --- | --- |
| global | near_observed_1pct | e154_to_e216_s2_graft | 0.000849985 | 1.023270538 |
| global | near_observed_1pct | e95_to_e154_body | -0.000019330 | -0.023270538 |
| subject | near_observed_1pct | e154_to_e216_s2_graft | 0.000932866 | 0.997042738 |
| subject | near_observed_1pct | e95_to_e154_body | 0.000002767 | 0.002957262 |
| nearest_hard085 | near_observed_1pct | e154_to_e216_s2_graft | 0.000940743 | 1.010450288 |
| nearest_hard085 | near_observed_1pct | e95_to_e154_body | -0.000009729 | -0.010450288 |
| focus_mean | near_observed_1pct | e154_to_e216_s2_graft | 0.000920169 | 1.004370217 |
| focus_mean | near_observed_1pct | e95_to_e154_body | -0.000004004 | -0.004370217 |

## Near-Observed Target Attribution

| prior | condition | target | mean_target_delta | share_of_total_mean |
| --- | --- | --- | --- | --- |
| global | near_observed_1pct | Q1 | -0.000001482 | -0.001784103 |
| global | near_observed_1pct | Q3 | 0.000003131 | 0.003769640 |
| global | near_observed_1pct | S2 | 0.000864500 | 1.040744748 |
| global | near_observed_1pct | S3 | -0.000001045 | -0.001257637 |
| global | near_observed_1pct | S4 | -0.000034449 | -0.041472649 |
| subject | near_observed_1pct | Q1 | -0.000001086 | -0.001160641 |
| subject | near_observed_1pct | Q3 | 0.000000269 | 0.000287214 |
| subject | near_observed_1pct | S2 | 0.000933448 | 0.997664595 |
| subject | near_observed_1pct | S3 | 0.000005182 | 0.005537993 |
| subject | near_observed_1pct | S4 | -0.000002179 | -0.002329160 |
| nearest_hard085 | near_observed_1pct | Q1 | -0.000032706 | -0.035129471 |
| nearest_hard085 | near_observed_1pct | Q3 | 0.000019035 | 0.020445845 |
| nearest_hard085 | near_observed_1pct | S2 | 0.000931280 | 1.000286123 |
| nearest_hard085 | near_observed_1pct | S3 | 0.000036022 | 0.038690699 |
| nearest_hard085 | near_observed_1pct | S4 | -0.000022617 | -0.024293196 |
| focus_mean | near_observed_1pct | Q1 | -0.000011765 | -0.012841734 |
| focus_mean | near_observed_1pct | Q3 | 0.000008986 | 0.009808426 |
| focus_mean | near_observed_1pct | S2 | 0.000923485 | 1.007989466 |
| focus_mean | near_observed_1pct | S3 | 0.000014214 | 0.015514791 |
| focus_mean | near_observed_1pct | S4 | -0.000018755 | -0.020470948 |

## Focus-Prior Cells That Move Most Under Near-Observed Worlds

| cell_id | subject_id | sleep_date | target | component | delta_prob | support_label | p_y1_focus_mean | posterior_y1_near_observed | posterior_shift_x_swing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 32:S2 | id02 | 2024-08-31 00:00:00 | S2 | e154_to_e216_s2_graft | -0.022462217 | 0 | 0.651111111 | 0.805500000 | 0.000019751 |
| 141:S2 | id06 | 2024-08-10 00:00:00 | S2 | e154_to_e216_s2_graft | -0.013251294 | 0 | 0.651111111 | 0.801500000 | 0.000018921 |
| 31:S2 | id02 | 2024-08-30 00:00:00 | S2 | e154_to_e216_s2_graft | -0.022516693 | 0 | 0.651111111 | 0.789500000 | 0.000017716 |
| 144:S2 | id06 | 2024-08-14 00:00:00 | S2 | e154_to_e216_s2_graft | -0.012303213 | 0 | 0.651111111 | 0.797000000 | 0.000017458 |
| 205:S2 | id09 | 2024-08-10 00:00:00 | S2 | e154_to_e216_s2_graft | -0.036025337 | 0 | 0.651111111 | 0.790500000 | 0.000016627 |
| 207:S2 | id09 | 2024-08-12 00:00:00 | S2 | e154_to_e216_s2_graft | -0.041588990 | 0 | 0.651111111 | 0.792000000 | 0.000016451 |
| 221:S2 | id09 | 2024-09-13 00:00:00 | S2 | e154_to_e216_s2_graft | -0.035320534 | 0 | 0.651111111 | 0.786000000 | 0.000016418 |
| 223:S2 | id09 | 2024-09-16 00:00:00 | S2 | e154_to_e216_s2_graft | -0.038015682 | 0 | 0.651111111 | 0.784000000 | 0.000016090 |
| 206:S2 | id09 | 2024-08-11 00:00:00 | S2 | e154_to_e216_s2_graft | -0.040339097 | 0 | 0.651111111 | 0.780000000 | 0.000015322 |
| 0:S2 | id01 | 2024-07-31 00:00:00 | S2 | e154_to_e216_s2_graft | 0.043765467 | 1 | 0.651111111 | 0.508500000 | 0.000014419 |
| 53:S2 | id02 | 2024-10-10 00:00:00 | S2 | e154_to_e216_s2_graft | -0.016590983 | 0 | 0.805925926 | 0.904500000 | 0.000013835 |
| 43:S2 | id02 | 2024-09-29 00:00:00 | S2 | e95_to_e154_body | -0.000930731 | 0 | 0.805925926 | 0.900500000 | 0.000013510 |
| 84:S2 | id04 | 2024-09-15 00:00:00 | S2 | e154_to_e216_s2_graft | -0.043191009 | 0 | 0.651111111 | 0.781500000 | 0.000013440 |
| 112:S2 | id05 | 2024-10-06 00:00:00 | S2 | e154_to_e216_s2_graft | 0.028605075 | 1 | 0.651111111 | 0.509000000 | 0.000013411 |
| 169:S2 | id07 | 2024-08-17 00:00:00 | S2 | e154_to_e216_s2_graft | 0.045828936 | 1 | 0.651111111 | 0.523500000 | 0.000013409 |
| 74:S2 | id03 | 2024-09-21 00:00:00 | S2 | e154_to_e216_s2_graft | 0.044968256 | 1 | 0.651111111 | 0.522500000 | 0.000013345 |
| 246:S2 | id10 | 2024-09-23 00:00:00 | S2 | e95_to_e154_body | -0.000580502 | 0 | 0.388249158 | 0.524500000 | 0.000013212 |
| 238:S2 | id10 | 2024-08-23 00:00:00 | S2 | e154_to_e216_s2_graft | 0.037189665 | 1 | 0.651111111 | 0.504000000 | 0.000013091 |
| 85:S2 | id04 | 2024-09-16 00:00:00 | S2 | e154_to_e216_s2_graft | 0.033594525 | 1 | 0.651111111 | 0.511500000 | 0.000013038 |
| 162:S2 | id07 | 2024-07-24 00:00:00 | S2 | e154_to_e216_s2_graft | -0.038346528 | 0 | 0.651111111 | 0.772000000 | 0.000013004 |

## Interpretation

- The observed miss is larger than the full adverse capacity of the E154 body alone, so E154 body cannot be the only explanation under the current 250x7 public-cell normalization.
- The pure S2 graft has enough adverse capacity to explain the miss; the failed public feedback is therefore a real S2-tail warning, not just an E154-anchor warning.
- The focus prior expects the S2 graft to help slightly, but its support probability is below 0.5. That is the missing gate signature: E216 selected a movement whose expected sign was favorable only by a small margin while the hidden-label support was intrinsically fragile.
- Remaining E216 siblings should stay demoted. A new masked-family JEPA submission needs an S2-tail gate that conditions on the cells listed above or a translator that avoids low-support S2 moves.
