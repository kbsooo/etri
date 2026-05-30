# E203 E176 Component Knockout Stress

## Question

If E176's public score is a sensor, which internal component must be alive for the sensor to matter, and which component mostly explains tail risk?

## Result

E176 has a necessary broad body, but its public fragility is concentrated in a much smaller critical-cell layer.

- Full E176 moved-cell focus delta is `-7.80419549249e-05` in the E179 cell prior.
- S-only carries `0.644881` of that focus delta; Q2-only carries only `0.093922`.
- Primary S-stage body S3/S1/S4 carries `0.573289`.
- Between-train-runs rows carry `0.774524`; dropping them leaves only `0.225476` of the body.
- Top33 swing cells carry `0.226424` of the expected body but have visible support `0.245771`.
- Dropping top33 still leaves `0.773576` of focus body, so top33 is a tail-resolution layer rather than the whole signal.

Interpretation: if E176 wins, the result primarily validates a broad S-stage / between-train-runs body. If it ties or loses, the most plausible failure is not that the body is absent; it is that the compact hard-tail layer cancelled the body.

## Component Knockouts

| component | role | n_cells | n_rows | targets | expected_focus_share | drop_remaining_focus_share | expected_visible_share | swing_share | top33_coverage | top8_coverage | cells_to_cover_e95_edge_focus | support_visible_swing_weighted | e72_active_rate | between_train_runs_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full | necessary_body | 904 | 193 | Q1,Q2,Q3,S1,S2,S3,S4 | 1 | -0 | 1 | 1 | 1 | 1 | 18 | 0.373623438754 | 0.268805309735 | 0.819690265487 |
| drop_Q | necessary_body | 501 | 192 | S1,S2,S3,S4 | 0.644880632909 | 0.355119367091 | 0.577321908781 | 0.596094833386 | 0.666666666667 | 0.5 | 21 | 0.307453768266 | 0.295409181637 | 0.814371257485 |
| drop_Q2 | necessary_body | 739 | 193 | Q1,Q3,S1,S2,S3,S4 | 0.906078425707 | 0.093921574293 | 0.910962697932 | 0.836400367988 | 0.939393939394 | 1 | 18 | 0.35686279744 | 0.327469553451 | 0.818673883627 |
| drop_S | mixed_component | 403 | 184 | Q1,Q2,Q3 | 0.355119367091 | 0.644880632909 | 0.422678091219 | 0.403905166614 | 0.333333333333 | 0.5 | 31 | 0.471278536943 | 0.235732009926 | 0.826302729529 |
| drop_S1 | necessary_body | 809 | 192 | Q1,Q2,Q3,S2,S3,S4 | 0.791370441749 | 0.208629558251 | 0.775529962788 | 0.839347875665 | 0.606060606061 | 0.625 | 21 | 0.393932312652 | 0.237330037083 | 0.818294190358 |
| drop_S3 | necessary_body | 736 | 193 | Q1,Q2,Q3,S1,S2,S4 | 0.851117512555 | 0.148882487445 | 0.920899484179 | 0.828846839413 | 0.909090909091 | 1 | 19 | 0.40606817578 | 0.317934782609 | 0.815217391304 |
| drop_S4 | necessary_body | 788 | 193 | Q1,Q2,Q3,S1,S2,S3 | 0.784223160592 | 0.215776839408 | 0.760802513189 | 0.867435824137 | 0.909090909091 | 0.875 | 22 | 0.364262799373 | 0.257614213198 | 0.817258883249 |
| drop_between_train_runs | mixed_component | 163 | 37 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.22547553456 | 0.77452446544 | 0.24073267766 | 0.185218918667 | 0.212121212121 | 0 | 41 | 0.396691350201 | 0.276073619632 | 0 |
| drop_id06_id07 | necessary_body | 723 | 152 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.705896256482 | 0.294103743518 | 0.797434150028 | 0.686891973486 | 0.545454545455 | 0.625 | 19 | 0.426941003433 | 0.254495159059 | 0.813278008299 |
| drop_primary_S | mixed_component | 525 | 188 | Q1,Q2,Q3,S2 | 0.426711114896 | 0.573288885104 | 0.457231960156 | 0.535630539215 | 0.424242424242 | 0.5 | 30 | 0.440494483898 | 0.272380952381 | 0.807619047619 |
| drop_top33 | necessary_body | 871 | 193 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.773576019605 | 0.226423980395 | 0.794018196934 | 0.848184962155 | 0 | 0 | 26 | 0.396507482908 | 0.265212399541 | 0.820895522388 |
| drop_top8 | necessary_body | 896 | 193 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.931285522775 | 0.0687144772255 | 0.941999334408 | 0.956328817766 | 0.757575757576 | 0 | 20 | 0.378757819691 | 0.265625 | 0.818080357143 |
| only_Q | mixed_component | 403 | 184 | Q1,Q2,Q3 | 0.355119367091 | 0.644880632909 | 0.422678091219 | 0.403905166614 | 0.333333333333 | 0.5 | 31 | 0.471278536943 | 0.235732009926 | 0.826302729529 |
| only_Q2 | secondary_or_guard | 165 | 165 | Q2 | 0.093921574293 | 0.906078425707 | 0.0890373020677 | 0.163599632012 | 0.0606060606061 | 0 | -1 | 0.459311935665 | 0.00606060606061 | 0.824242424242 |
| only_S | necessary_body | 501 | 192 | S1,S2,S3,S4 | 0.644880632909 | 0.355119367091 | 0.577321908781 | 0.596094833386 | 0.666666666667 | 0.5 | 21 | 0.307453768266 | 0.295409181637 | 0.814371257485 |
| only_S1 | hard_tail_uncertain | 95 | 95 | S1 | 0.208629558251 | 0.791370441749 | 0.224470037212 | 0.160652124335 | 0.393939393939 | 0.375 | 41 | 0.26751709105 | 0.536842105263 | 0.831578947368 |
| only_S3 | secondary_or_guard | 168 | 168 | S3 | 0.148882487445 | 0.851117512555 | 0.0791005158207 | 0.171153160587 | 0.0909090909091 | 0 | -1 | 0.216502660804 | 0.0535714285714 | 0.839285714286 |
| only_S4 | mixed_component | 116 | 116 | S4 | 0.215776839408 | 0.784223160592 | 0.239197486811 | 0.132564175863 | 0.0909090909091 | 0.125 | 38 | 0.434874933607 | 0.344827586207 | 0.836206896552 |
| only_between_train_runs | necessary_body | 741 | 156 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.77452446544 | 0.22547553456 | 0.75926732234 | 0.814781081333 | 0.787878787879 | 1 | 22 | 0.368379559493 | 0.267206477733 | 1 |
| only_id06_id07 | hard_tail_uncertain | 181 | 41 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.294103743518 | 0.705896256482 | 0.202565849972 | 0.313108026514 | 0.454545454545 | 0.375 | 37 | 0.256656117181 | 0.325966850829 | 0.845303867403 |
| only_primary_S | necessary_body | 379 | 190 | S1,S3,S4 | 0.573288885104 | 0.426711114896 | 0.542768039844 | 0.464369460785 | 0.575757575758 | 0.5 | 21 | 0.296490515525 | 0.263852242744 | 0.836411609499 |
| only_top33 | hard_tail_uncertain | 33 | 30 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.226423980395 | 0.773576019605 | 0.205981803066 | 0.151815037845 | 1 | 1 | 23 | 0.24577113637 | 0.363636363636 | 0.787878787879 |
| only_top8 | e72_tail_risk | 8 | 8 | Q3,S1,S4 | 0.0687144772255 | 0.931285522775 | 0.0580006655919 | 0.0436711822337 | 0.242424242424 | 1 | -1 | 0.261188734673 | 0.625 | 1 |
| only_visible_high | mixed_component | 299 | 158 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.415318304393 | 0.584681695607 | 0.652464711021 | 0.315732190224 | 0.0606060606061 | 0.125 | 31 | 0.639093647716 | 0.277591973244 | 0.846153846154 |
| only_visible_low | hard_tail_uncertain | 291 | 154 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.345856026522 | 0.654143973478 | 0.101944730559 | 0.417076751102 | 0.636363636364 | 0.5 | 40 | 0.166653409304 | 0.230240549828 | 0.817869415808 |

## Target Knockouts

| component | role | n_cells | n_rows | expected_focus_share | drop_remaining_focus_share | top33_coverage | top8_coverage | cells_to_cover_e95_edge_focus | support_visible_swing_weighted | e72_active_rate | between_train_runs_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | mixed_component | 116 | 116 | 0.215776839408 | 0.784223160592 | 0.0909090909091 | 0.125 | 38 | 0.434874933607 | 0.344827586207 | 0.836206896552 |
| S1 | hard_tail_uncertain | 95 | 95 | 0.208629558251 | 0.791370441749 | 0.393939393939 | 0.375 | 41 | 0.26751709105 | 0.536842105263 | 0.831578947368 |
| Q1 | mixed_component | 121 | 121 | 0.166575714505 | 0.833424285495 | 0.151515151515 | 0 | -1 | 0.406551508984 | 0.388429752066 | 0.818181818182 |
| S3 | secondary_or_guard | 168 | 168 | 0.148882487445 | 0.851117512555 | 0.0909090909091 | 0 | -1 | 0.216502660804 | 0.0535714285714 | 0.839285714286 |
| Q3 | mixed_component | 117 | 117 | 0.0946220782935 | 0.905377921706 | 0.121212121212 | 0.5 | -1 | 0.556798444678 | 0.401709401709 | 0.837606837607 |
| Q2 | secondary_or_guard | 165 | 165 | 0.093921574293 | 0.906078425707 | 0.0606060606061 | 0 | -1 | 0.459311935665 | 0.00606060606061 | 0.824242424242 |
| S2 | secondary_or_guard | 122 | 122 | 0.0715917478049 | 0.928408252195 | 0.0909090909091 | 0 | -1 | 0.346102357093 | 0.393442622951 | 0.745901639344 |

## Role Counts

| role | n_components |
| --- | --- |
| necessary_body | 12 |
| mixed_component | 6 |
| hard_tail_uncertain | 4 |
| secondary_or_guard | 2 |
| e72_tail_risk | 1 |

## Decision

No submission is created. E203 strengthens the rule that E176 feedback must be read as a body-vs-tail observation. Post-E176 follow-up should only ask Q2 amplitude if E176 wins cleanly enough to first validate the broad S-stage body.
