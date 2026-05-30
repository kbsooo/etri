# E201 E176 Public Sensor Packet

## Question

Before submitting E176, can we freeze the file identity and the score-to-worldview router so the next public LB observation is interpreted as evidence rather than post-hoc tuning fuel?

## Result

E176 remains the first public sensor, and this packet fixes how to read its public score before that score is known.

- File: `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`
- SHA256: `34d38587b04640327824b972f4cbc18ae03cab2f92802ac7c144f94b96184206`
- Ready for submission: `True`
- Changed cells vs E95: `904` over `193` rows
- Target delta share vs E95: `Q2:0.209702;S4:0.145285;Q3:0.141693;S2:0.130103;Q1:0.128746;S3:0.126307;S1:0.118164`

The important rule is negative: do not interpret the E176 public score with scalar intuition after seeing it. Use the pre-registered route below.

## File Audit

| candidate | ready_for_submission | n_rows | columns_match_sample | key_order_match_sample | duplicate_key_rows | target_min | target_max | changed_cells_vs_e95 | changed_rows_vs_e95 | mean_abs_delta_vs_e95 | max_abs_delta_vs_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e95 | True | 250 | True | True | 0 | 0.0681101766719 | 0.979776651464 | 0 | 0 | 0 | 0 |
| e176 | True | 250 | True | True | 0 | 0.0681101766719 | 0.979776651464 | 904 | 193 | 0.000146564732264 | 0.00170350008373 |
| e172 | True | 250 | True | True | 0 | 0.0681101766719 | 0.979776651464 | 904 | 193 | 0.000133406126859 | 0.00170350008373 |
| e174 | True | 250 | True | True | 0 | 0.0681101766719 | 0.979776651464 | 904 | 193 | 0.000147839888038 | 0.00170350008373 |
| e154 | True | 250 | True | True | 0 | 0.0681101766719 | 0.979776651464 | 294 | 139 | 0.000391751114779 | 0.00605114808924 |

## Score Router

| outcome | public_lb_lo_exclusive | public_lb_hi_inclusive | worldview_update_class | next_candidate_role | strengthened | weakened | kill_switch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| q2_underopen_breakthrough | -inf | 0.5762613298 | promote_broad_q2_underopen | no_immediate_sibling; decompose non-Q2/S-stage responsibility | H176 broad partial-reopen body + Q2 under-opening is public-real | E172-first safety priority; E174 full-Q2 reopen as score file | If the gain is driven only by a single public-cell illusion in later contrast, demote amplitude tuning. |
| clean_win | 0.5762613298 | 0.5762760191 | anchor_e176_as_current_world | conditional component responsibility audit | Q/S-asymmetric partial reopening is readable beyond the E95-mixmin edge | Conservative E154-first branch; E172-first private-risk branch | A later E174 loss would confirm Q2 damping, not invalidate E176 body. |
| micro_win | 0.5762760191 | 0.5762883298 | weakly_promote_e176_but_keep_resolution_doubt | E174 only as deliberate Q2-amplitude sensor | E176 direction is plausible under public hard labels | Large-margin broad-body worldview | If E174 does not improve in the next contrast, stop Q2 amplitude siblings. |
| tie | 0.5762883298 | 0.5762943298 | underresolved_same_family | E172 same-family safety if continuing this branch | Hard-label resolution/cancellation explains plateau | E176 as decisive broad-body signal | Do not tune Q2 keep from a tie; it is below resolution. |
| small_loss | 0.5762943298 | 0.576300366 | demote_e176_but_not_family | E172 if testing broad-tail repair, otherwise E154 | Q2 damping did not fully neutralize broad partial-reopen risk | E176-first expected-score dominance | Another E176 sibling by Q2 keep-factor is disallowed. |
| e101_worse_mixmin_safe | 0.576300366 | 0.5763066405 | demote_partial_reopen_branch | E154 repaired-branch counter-world | Partial-reopen public misalignment survived Q2 damping | E174/E176/E172 as score-improving line | Do not submit E174 next except as falsification, not score improvement. |
| branch_loss | 0.5763066405 | 0.5763413298 | close_same_family_expected_score_lane | E154 or rebuild bad-axis model | Current broad partial-reopen axis gives back frontier edge | E176/E174/E172/E169 as expected-score follow-ups | Close same-family followups unless explicitly spending a falsification slot. |
| hard_fail | 0.5763413298 | inf | search_non_collinear_latent | no same-family submission; return to structure discovery | Dominant negative axis is outside Q2 damping and partial-reopen family | All current same-family frontier challenge assumptions | Stop threshold/keep-factor/target-drop siblings. |

## Minimal Decision Rule

- Better than `0.5762883298`: E176 is useful; decompose responsibility, do not rush another sibling.
- `0.5762883298` to `0.576300366`: same-family signal is underresolved or slightly bad; E172 is the only coherent same-family follow-up.
- Worse than `0.576300366`: demote partial-reopen branch; prefer E154 or a non-collinear latent search.
- Worse than `0.5763413298`: close same-family expected-score lane.

## Summary Keys

| key | value |
| --- | --- |
| recommended_submission | analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv |
| recommended_sha256 | 34d38587b04640327824b972f4cbc18ae03cab2f92802ac7c144f94b96184206 |
| recommended_ready_for_submission | True |
| recommended_changed_cells_vs_e95 | 904 |
| recommended_changed_rows_vs_e95 | 193 |
| e176_vs_e172_changed_cells | 75 |
| e172_ready_for_submission | True |
| current_frontier_file | analysis_outputs/submission_e95_hardtail_541e3973.csv |
| current_frontier_public_lb | 0.5762913298 |
| mixmin_public_lb | 0.5763066405 |
| e101_public_lb | 0.576300366 |
| clean_win_hi_public_lb | 0.5762760191 |
| router_rule | Use route_summary outcome matching observed E176 public LB before making another file. |
| decoder_command | python3 analysis_outputs/e177_e176_public_feedback_decoder.py --score <E176_PUBLIC_LB> |

## Interpretation

E201 does not add score. It removes degrees of freedom. The next E176 public LB should resolve a worldview branch, not invite another Q2 keep-factor sweep.
