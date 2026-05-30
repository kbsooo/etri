# E205 E176 Public-Feedback Executable Decoder

## Question

Can the pending E176 public score be decoded without post-hoc scalar intuition?

## Result

E205 turns E201-E204 into an executable routebook. A future score maps to exactly one score band, one component interpretation, one forbidden-action set, and one follow-up role.

Core invariants baked into the decoder:

- E176 is broad S-stage / between-train-runs body first.
- Q2-only share is small relative to S/body, so Q2 amplitude is never the first post-score explanation.
- Top33 is a compact cancellation layer, not the whole signal.
- E172, E154, and E174 are different route probes: safety rollback, body-exit counter-world, and Q2 amplitude.

## Example Decodes

| score | outcome | worldview_update_class | followup_candidate | followup_role | component_interpretation |
| --- | --- | --- | --- | --- | --- |
| 0.57625 | q2_underopen_breakthrough | promote_broad_q2_underopen | none | no_immediate_submission | Credit broad S-stage/between-train-runs body first; Q2 damping is a secondary guard, not the whole explanation. |
| 0.57627 | clean_win | anchor_e176_as_current_world | none | no_immediate_submission | Treat E176 as a broad-body anchor; the win supports Q/S asymmetry but does not prove Q2 keep=0.75 is optimal. |
| 0.576282 | micro_win | weakly_promote_e176_but_keep_resolution_doubt | e174_q2_reopen | optional_q2_amplitude_probe | The sign is right but hard-label resolution is still thin; body and tail probably nearly cancel. |
| 0.576291 | tie | underresolved_same_family | e172_safety | same_family_safety | The broad body exists but top critical cells are underresolved; the top33 visible support p_low is the warning. |
| 0.576297 | small_loss | demote_e176_but_not_family | e172_safety | same_family_safety_or_e154 | Read as tail/cancellation failure, not as proof that Q2 alone is wrong. |
| 0.576303 | e101_worse_mixmin_safe | demote_partial_reopen_branch | e154_counterworld | body_exit_counterworld | Partial-reopen is public-misaligned despite Q2 damping. |
| 0.57632 | branch_loss | close_same_family_expected_score_lane | e154_counterworld | body_exit_counterworld | The broad partial-reopen body gives back the frontier edge. |
| 0.57635 | hard_fail | search_non_collinear_latent | search | non_collinear_search | Dominant negative axis is outside this component family. |

## Full Routebook

| outcome | public_lb_lo_exclusive | public_lb_hi_inclusive | worldview_update_class | component_interpretation | followup_candidate | followup_role | followup_condition | forbidden_action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q2_underopen_breakthrough | -inf | 0.5762613298 | promote_broad_q2_underopen | Credit broad S-stage/between-train-runs body first; Q2 damping is a secondary guard, not the whole explanation. | none | no_immediate_submission | First decompose broad S-stage / between-train-runs body; E174 only after an explicit Q2 amplitude question. | Do not submit E174 merely because it has a slightly stronger focus prior edge; the observed win says the Q2 risk cut mattered.; Do not infer Q2-only causality from the scalar score. |
| clean_win | 0.5762613298 | 0.5762760191 | anchor_e176_as_current_world | Treat E176 as a broad-body anchor; the win supports Q/S asymmetry but does not prove Q2 keep=0.75 is optimal. | none | no_immediate_submission | First decompose broad S-stage / between-train-runs body; E174 only after an explicit Q2 amplitude question. | Do not reopen Q2 back to E174 without an independent reason.; Do not infer Q2-only causality from the scalar score. |
| micro_win | 0.5762760191 | 0.5762883298 | weakly_promote_e176_but_keep_resolution_doubt | The sign is right but hard-label resolution is still thin; body and tail probably nearly cancel. | e174_q2_reopen | optional_q2_amplitude_probe | Use only if deliberately spending a slot on Q2 amplitude after weak broad-body validation. | Do not infer a broad 0.54 path from a micro-win; the edge can still be one-cell driven.; Do not infer Q2-only causality from the scalar score. |
| tie | 0.5762883298 | 0.5762943298 | underresolved_same_family | The broad body exists but top critical cells are underresolved; the top33 visible support p_low is the warning. | e172_safety | same_family_safety | Use only if continuing the same family; no Q2 keep sweep. | Do not tune Q2 keep factors from a tie.; Do not infer Q2-only causality from the scalar score. |
| small_loss | 0.5762943298 | 0.576300366 | demote_e176_but_not_family | Read as tail/cancellation failure, not as proof that Q2 alone is wrong. | e172_safety | same_family_safety_or_e154 | E172 if asking safety; E154 if asking whether to exit the E176 body. | Do not make another E176 sibling by moving the Q2 keep factor.; Do not infer Q2-only causality from the scalar score. |
| e101_worse_mixmin_safe | 0.576300366 | 0.5763066405 | demote_partial_reopen_branch | Partial-reopen is public-misaligned despite Q2 damping. | e154_counterworld | body_exit_counterworld | Demote partial-reopen; test repaired-branch counter-world or search. | Do not submit E174 next unless the sole goal is proving full Q2 reopening, not score improvement.; Do not infer Q2-only causality from the scalar score. |
| branch_loss | 0.5763066405 | 0.5763413298 | close_same_family_expected_score_lane | The broad partial-reopen body gives back the frontier edge. | e154_counterworld | body_exit_counterworld | Demote partial-reopen; test repaired-branch counter-world or search. | Do not submit E169 or E166 unless explicitly spending a falsification slot.; Do not infer Q2-only causality from the scalar score. |
| hard_fail | 0.5763413298 | inf | search_non_collinear_latent | Dominant negative axis is outside this component family. | search | non_collinear_search | Close same-family expected-score lane and return to hidden-block/sequence/target-dependency search. | Do not create threshold, keep-factor, or target-drop siblings.; Do not infer Q2-only causality from the scalar score. |

## Body/Tail Constants

| outcome | s_only_focus_share | primary_s_focus_share | between_train_runs_focus_share | q2_only_focus_share | top33_focus_share | drop_top33_remaining_focus_share | top33_visible_support |
| --- | --- | --- | --- | --- | --- | --- | --- |
| q2_underopen_breakthrough | 0.644880632909 | 0.573288885104 | 0.77452446544 | 0.093921574293 | 0.226423980395 | 0.773576019605 | 0.24577113637 |

## Selected Score Decode

```json
{
  "between_train_runs_focus_share": 0.7745244654395543,
  "component_interpretation": "The broad partial-reopen body gives back the frontier edge.",
  "drop_top33_remaining_focus_share": 0.7735760196046824,
  "followup_body_rollback_fraction": 0.8775761177039181,
  "followup_candidate": "e154_counterworld",
  "followup_changed_cells": 1027.0,
  "followup_condition": "Demote partial-reopen; test repaired-branch counter-world or search.",
  "followup_file": "analysis_outputs/submission_e154_s3repair_9f2e2e73.csv",
  "followup_off_e176_abs_share": 0.2925009591938516,
  "followup_role": "body_exit_counterworld",
  "followup_rollback_abs_share": 0.6268578548662456,
  "followup_top33_rollback_count": 31.0,
  "forbidden_action": "Do not submit E169 or E166 unless explicitly spending a falsification slot.; Do not infer Q2-only causality from the scalar score.",
  "kill_switch": "Close same-family followups unless explicitly spending a falsification slot.",
  "outcome": "branch_loss",
  "primary_s_focus_share": 0.573288885103777,
  "public_lb_hi_inclusive": 0.5763413298,
  "public_lb_lo_exclusive": 0.5763066405,
  "q2_only_focus_share": 0.0939215742930403,
  "required_next_evidence": "Non-collinear latent or repaired-branch counter-world.",
  "s_only_focus_share": 0.6448806329086503,
  "score": 0.576311831,
  "strengthened": "Current broad partial-reopen axis gives back frontier edge",
  "top33_focus_share": 0.2264239803953178,
  "top33_visible_support": 0.2457711363703791,
  "weakened": "E176/E174/E172/E169 as expected-score follow-ups",
  "worldview_update_class": "close_same_family_expected_score_lane"
}
```

## Decision

No submission is created. After E176 public feedback, run this decoder with `--score` before choosing any follow-up file.
