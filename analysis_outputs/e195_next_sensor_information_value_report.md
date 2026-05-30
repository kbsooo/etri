# E195 Next Sensor Information Value

## Question

After E194, should the next public slot still be E176, or is E154 the better sensor because it represents the strongest counter-world?

## Result

E176 remains the better first sensor. It is not just the higher-balance file; it gives the cleaner decision tree. If E176 wins, it validates the current broad/Q2-underopen worldview. If E176 loses badly, the decoder already routes to E154 or representation search and forbids same-family keep-factor tuning. E154 is valuable, but it tests only the repaired E144-collinear branch and leaves the E176 broad worldview mostly unobserved.

Recommended first sensor: `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`.

## Sensor Summary

| sensor | file | primary_question | validated_world_if_win | main_counterworld_if_loss | bands | win_bands | adverse_bands | counterworld_route_bands | same_family_forbidden_bands | readable_counterworld_contrast | contrast_cells | contrast_expected_delta | information_value_read | decision_condition | sensor_rank | family_alone_context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e176 | analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv | Does broad/Q2-underopen pair/shape/body evidence beat the binary-world counterprior? | broad_q2_underopen | e154_repaired_branch | 8 | 3 | 3 | 3 | 8 | yes | 1027 | -9.35461765e-05 | dominant first sensor because win validates current top worldview and loss routes to explicit E154 counterworld | prefer unless binary-world is trusted >1.760x or pair geometry <0.725x after removing non-comparable visible evidence | 1 | antisymmetric_pair:e176; binary_world:e154; clean_e72_tail:e176; known_winner_topcell:e176; pressure_branch:e176; visible_body_q2:e176 |
| e154 | analysis_outputs/submission_e154_s3repair_9f2e2e73.csv | Is the repaired E144-collinear S3 active-boundary branch public-real? | repaired_branch | e144_or_representation_search | 7 | 3 | 2 | 0 | 7 | partial | 294 | -2.43212003e-06 | good alternate-world sensor but does not directly resolve the current E176 broad/Q2-underopen worldview | prefer first only under high-binary/low-pair worldview; e154-vs-e155 is not readable (-1.79555915e-06) | 2 | antisymmetric_pair:e176; binary_world:e154; clean_e72_tail:e176; known_winner_topcell:e176; pressure_branch:e176; visible_body_q2:e176 |

## Pairwise Resolution

| contrast | question | moved_cells | moved_rows | focus_expected_delta | top1_swing | cells_for_2e6_guard | cells_for_e95_edge | readability |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e176_vs_e154 | broad/Q2-underopen vs repaired-branch counterworld | 1027 | 238 | -9.35461765e-05 | 1.59574962e-05 | 1 | 1 | public-readable but hard-label fragile |
| e154_vs_e144 | full repaired branch vs unrepaired residual branch | 294 | 139 | -2.43212003e-06 | NA | NA | NA | barely readable against E144 |
| e154_vs_e155 | full repaired branch vs lower-amplitude sibling | 294 | 139 | -1.79555915e-06 | NA | NA | NA | not public-readable by E158 guard |

## Band Action Map

| sensor | outcome | public_lb_range | validates | kills_or_weakens | action_class | routes_to_e154 | forbids_same_family_tuning | next_action | routes_to_branch_control | routes_to_e176 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e176 | q2_underopen_breakthrough | (-inf, 0.57626133] | broad_q2_underopen | binary_world_counterprior_as_first_choice | promote_e176 | 0 | 1 | Promote E176 as the broad anchor. Next experiment should decompose S3/S2/S1-heavy reopening, not increase Q2. | 0 | NA |
| e176 | clean_win | (0.57626133, 0.576276019] | broad_q2_underopen | binary_world_counterprior_as_first_choice | promote_e176 | 0 | 1 | Use E176 as the expected-score anchor and treat E174 as a max-edge contrast only. | 0 | NA |
| e176 | micro_win | (0.576276019, 0.57628833] | broad_q2_underopen | binary_world_counterprior_as_first_choice | promote_e176 | 0 | 1 | Promote cautiously. Compare E176 against E174 only if a second public slot is explicitly a Q2-amplitude test. | 0 | NA |
| e176 | tie | (0.57628833, 0.57629433] | hidden_label_resolution_bottleneck | expected_score_certification_for_e176 | ambiguous_or_shift_to_e154_by_question | 0 | 1 | Keep E95 practical. If testing the same family again, use E172 only as the safer contrast or E174 only as the deliberate Q2 full-reopen contrast. | 0 | NA |
| e176 | small_loss | (0.57629433, 0.576300366] | hidden_label_resolution_bottleneck | expected_score_certification_for_e176 | ambiguous_or_shift_to_e154_by_question | 1 | 1 | Use E172 as the cleaner same-family contrast only if the next question is broad-tail repair; otherwise shift to E154/conservative branch. | 0 | NA |
| e176 | e101_worse_mixmin_safe | (0.576300366, 0.576306641] | binary_world_or_other_counterworld | partial_reopen_expected_score_lane | demote_e176_route_e154_or_search | 1 | 1 | Demote the E174/E176 partial-reopen branch. Prefer E154 if another expected-score file is needed. | 0 | NA |
| e176 | branch_loss | (0.576306641, 0.57634133] | binary_world_or_other_counterworld | partial_reopen_expected_score_lane | demote_e176_route_e154_or_search | 1 | 1 | Close E176/E174/E172/E169 as expected-score followups and rebuild the bad-axis model. | 0 | NA |
| e176 | hard_fail | (0.57634133, inf] | binary_world_or_other_counterworld | partial_reopen_expected_score_lane | demote_e176_route_e154_or_search | 0 | 1 | Close the same-family broad reopen expected-score lane and search for a new non-collinear latent. | 0 | NA |
| e154 | breakthrough_win | (-inf, 0.57627133] | repaired_branch | e176_first_priority_but_not_e176_worldview | promote_e154 | 0 | 1 | Promote E154 and rerun exact-delta audits. Do not spend the next slot on E155/E157/E156 until the new anchor geometry is rebuilt. | 0 | 0 |
| e154 | clean_win | (0.57627133, 0.57628433] | repaired_branch | e176_first_priority_but_not_e176_worldview | promote_e154 | 0 | 1 | Promote E154; use E155 only as a private-risk amplitude audit, not as the next automatic public file. | 1 | 0 |
| e154 | micro_win | (0.57628433, 0.57628933] | repaired_branch | e176_first_priority_but_not_e176_worldview | promote_e154 | 0 | 1 | Promote E154 cautiously; next local work should seek non-collinear representation, not target-axis micro-tuning. | 0 | 0 |
| e154 | tie | (0.57628933, 0.57629333] | repaired_branch_underresolved_or_added_body_question | full_e154_expected_score_certification | e155_or_e144_component_branch | 0 | 1 | Keep E95 practical frontier; E155 is allowed only if deliberately testing lower amplitude, not expected improvement. | 1 | 0 |
| e154 | small_loss | (0.57629333, 0.576300366] | repaired_branch_underresolved_or_added_body_question | full_e154_expected_score_certification | e155_or_e144_component_branch | 0 | 1 | If spending another slot on this branch, E155 is the only clean same-family follow-up; do not jump to E157/E156 before E155. | 1 | 0 |
| e154 | branch_loss | (0.576300366, 0.576306641] | repaired_branch_failure | repaired_branch_siblings | e144_or_representation_search | 0 | 1 | Treat E155 as an explicit overextension test only. If E155 is skipped or loses, use E144 as the unrepaired contrast or close the branch. | 1 | 0 |
| e154 | hard_fail | (0.576306641, inf] | repaired_branch_failure | repaired_branch_siblings | e144_or_representation_search | 0 | 1 | Do not submit E157/E156. E155 is only an information-only amplitude salvage; otherwise fall back to E144 or representation search. | 1 | 0 |

## Interpretation

- E176-vs-E154 is public-readable but hard-label fragile: `1027` cells over `238` rows, focus expected delta `-9.35461765e-05`, and only `1` cell for the `2e-6` guard.
- E154-vs-E144 is barely readable; E154-vs-E155 is not readable by the E158 guard. That makes E154 useful as a repaired-branch public question, but less efficient as the first slot after E194.
- E176 first is a directional bet: pair/shape/broad-body evidence should be trusted more than the inherited binary-world counterprior. E154 first is coherent only if the binary-world view is intentionally promoted above the E194 flip condition.

## Decision

No new submission is created. Keep `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` as the next single public sensor. If its public LB lands in an adverse E177 band, switch to E154 or representation search according to the pre-registered decoder instead of tuning another E176 sibling.
