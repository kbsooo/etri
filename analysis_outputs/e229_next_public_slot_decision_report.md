# E229 Next Public Slot Decision

This is a no-submission audit. It folds the E216 public miss into the reusable
public-observation ledger, then decides which live file is the next most
informative public sensor.

## Core Decision

- Forced one-slot decision under the current JEPA-first question:
  `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
- First independent follow-up if E224 ties or loses:
  `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv`.
- Conservative branch only after attribution or after JEPA/broad questions are
  demoted:
  `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.

The reason is not a reliable score forecast. `raw05_a2c8_compat proxy MAE=0.000496259, p90=0.000695363; this is larger than the E95/E101/mixmin frontier gaps, so it is a geometry descriptor, not a score selector.` E224 is selected only
because it asks the live JEPA question directly and is nearly orthogonal to the
failed E216 S2 translator (`cos_vs_e216=0.043542`).

## Decision Table

| candidate | forced_one_slot_decision | jepa_first_rank | independent_world_rank | expected_focus_vs_e95 | expected_edge_over_proxy_mae | adverse_delta | cos_vs_e216 | cos_vs_e224 | routebook_outcomes | primary_question |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e224 | yes_current_goal | 1 | 2 | -0.000653189 | 1.316225245 | 0.004094069 | 0.043542250 | 1.000000000 | 9 | Was E216 a narrow S2-rank JEPA failure, or does public reject the current JEPA translator family? |
| e166 | no_first_followup_if_e224_loses_or_ties | 2 | 1 | -0.000332077 | 0.669159320 | 0.000713053 | 0.055998599 | 0.074348354 | 10 | Is the safety atlas overconservative on broad survivor context outside the JEPA/E154 body? |
| e154 | no_conditional | 3 | 3 | -0.000029838 | 0.060124922 | 0.000924070 | 0.135253079 | 0.316350240 | 7 | Does the repaired E144/E154 branch transfer after broad/JEPA losses? |

## Geometry And Risk

| candidate | moved_cells_vs_e95 | moved_rows_vs_e95 | abs_share_Q3 | abs_share_S2 | abs_share_S4 | one_minus_abs_cos_vs_e216 | e154_inherited_penalty_if_any | recommended_when | not_recommended_when |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e224 | 534 | 250 | 0.533416245 | 0.026566654 | 0.363619236 | 0.956457750 | 0.000000000 | The active question is JEPA-first: test Q3/S4 capped context-to-target translation directly. | The next slot must minimize downside rather than maximize JEPA information. |
| e166 | 1750 | 250 | 0.116408335 | 0.170756390 | 0.124022903 | 0.944001401 | 0.000000000 | The active question is escaping the JEPA lane with a non-collinear hidden-world sensor. | The next slot is explicitly reserved for testing JEPA after E216. |
| e154 | 294 | 139 | 0.356221481 | 0.134197635 | 0.123668043 | 0.864746921 | 0.885621410 | Both the JEPA and independent broad questions have been demoted or a low-movement conservative sensor is required. | We need maximum new information from the very next slot. |

## What The Public Score Would Mean

| candidate | outcome | public_lb_lo_exclusive | public_lb_hi_inclusive | world_update_class | branch_status | next_action | allowed_next | candidate_to_test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e224 | capped_jepa_breakthrough | -inf | 0.576261330 | strong_support |  | Do not immediately increase Q3. First decompose the win into S4 body, Q3 residual, and E154 inherited body using an E224-vs-E95-anchor attribution audit. |  | conditional:e224_component_decomposition_or_e224_e95_anchor |
| e224 | clean_win | 0.576261330 | 0.576276019 | support |  | Promote E224 as the JEPA-family anchor. Use the E224 E95-anchor sibling only if the next public slot is a clean attribution sensor. |  | analysis_outputs/submission_e224_e224_q3s0p625_s4toward_e95_a0p5_9c52abe2.csv |
| e224 | micro_win | 0.576276019 | 0.576288330 | weak_support |  | Keep E224 as the preferred JEPA sensor, but do not submit a sibling until an exact-score attribution audit identifies whether Q3 or S4 carried the win. |  | conditional:e224_exact_score_attribution |
| e224 | tie | 0.576288330 | 0.576294330 | underresolved |  | Keep E95 practical. Treat E224 as an unresolved diagnostic and run a target/component attribution audit before any JEPA sibling. |  |  |
| e224 | small_loss | 0.576294330 | 0.576300366 | weak_rejection |  | Do not submit another amplitude sibling. Audit whether E154 inherited body or E224 Q3/S4 residual caused the loss, then decide between E154 branch and new JEPA target design. |  | conditional:e224_loss_attribution_then_e154_or_new_jepa |
| e224 | mixmin_safe_loss | 0.576300366 | 0.576306641 | rejection |  | Demote E211/E223/E224 as expected-score followups. Keep JEPA axes as diagnostics and move to a new representation or support-tail target. |  | conditional:new_jepa_support_tail_objective |
| e224 | branch_loss | 0.576306641 | 0.576341330 | strong_rejection |  | Close current E211-family expected-score lane. Search for non-collinear hidden structure or build a JEPA objective with support/tail regularization baked in. |  | conditional:non_collinear_search_or_support_regularized_jepa |
| e224 | hard_fail | 0.576341330 | 0.576591330 | hard_rejection |  | Keep E208/E211 axes only as diagnostics. Rebuild target representation or return to block/sequence hidden-world search. |  |  |
| e224 | e216_like_fail | 0.576591330 | inf | translator_collapse |  | Do a root-cause miss anatomy like E219 before any further JEPA submission. Treat current JEPA probability movement as unsafe. |  | conditional:e224_public_miss_anatomy |
| e166 | broad_breakthrough | -inf | 0.576261330 | strong_support |  | Promote broad survivor structure as a live hidden-world target. Do an exact E166 component/block attribution before scaling or submitting any E166-family sibling. |  | conditional:e166_component_block_attribution |
| e166 | clean_win | 0.576261330 | 0.576276019 | support |  | Use E166 as the new broad-world anchor and audit whether the top benefit cells are between-train-runs or S-stage driven. |  | conditional:e166_context_component_attribution |
| e166 | micro_win | 0.576276019 | 0.576288330 | weak_support |  | Keep E166 alive. Decode exact cells and compare against E167 top-benefit context before any same-family file. |  | conditional:e166_exact_cell_decoder |
| e166 | tie | 0.576288330 | 0.576294330 | underresolved |  | Keep E95 practical. Prefer E224 if the next question is JEPA, or E154 if the next question is the conservative branch. |  | conditional:e224_or_e154_by_question |
| e166 | small_loss | 0.576294330 | 0.576300366 | weak_rejection |  | Do not rescue by scaling. Compare loss cells to E72-active and low-veto-null warnings, then choose E154 or new representation search. |  | conditional:e166_loss_cell_attribution_then_e154_or_search |
| e166 | mixmin_safe_loss | 0.576300366 | 0.576306641 | rejection |  | Route away from broad survivor as an expected-score lane. Use E154 for conservative branch test or E224 for the distinct JEPA test. |  | conditional:e154_or_e224_by_question |
| e166 | broad_branch_loss | 0.576306641 | 0.576311831 | strong_rejection |  | Treat E166 like E176: broad survivor body is public-misaligned at frontier resolution. Route to E154 or a non-collinear representation. |  | analysis_outputs/submission_e154_s3repair_9f2e2e73.csv |
| e166 | broad_fail | 0.576311831 | 0.576341330 | hard_rejection |  | Close E166-family expected-score followups. Use E154 if testing existing files; otherwise search for a new block/sequence target. |  | analysis_outputs/submission_e154_s3repair_9f2e2e73.csv |
| e166 | e72_like_fail | 0.576341330 | 0.576407777 | very_hard_rejection |  | Run an E166 miss anatomy before any broad candidate. Treat E72-active broad survivor structure as public-dangerous. |  | conditional:e166_public_miss_anatomy |
| e166 | s2_jepa_like_fail_or_worse | 0.576407777 | inf | collapse |  | Do a root-cause miss anatomy and stop broad survivor submissions until a public-tail target is rebuilt. |  | conditional:e166_public_miss_anatomy |
| e154 | breakthrough_win | -inf | 0.576271330 |  | validated_large |  | Promote E154 as a new public anchor and rerun exact-delta audits before spending any slot on sibling controls. |  |
| e154 | clean_win | 0.576271330 | 0.576284330 |  | validated_readable |  | Promote E154. Use E155 only as a private-risk amplitude audit, not as the next automatic public file. |  |
| e154 | micro_win | 0.576284330 | 0.576289330 |  | validated_micro |  | Promote E154 cautiously; next local work should seek a non-collinear representation rather than sibling micro-controls. |  |
| e154 | tie | 0.576289330 | 0.576293330 |  | ambiguous |  | Keep E95 as practical frontier. E155 is allowed only as an information-only amplitude contrast if attribution blames E154-added body. | conditional:submission_e155_bodytemp_d27e7965.csv |
| e154 | small_loss | 0.576293330 | 0.576300366 |  | conditional_alive |  | Use component attribution first. E155 is the clean follow-up only if added-body overextension is the culprit; otherwise use E144 as unrepaired contrast or pause. | conditional:submission_e155_bodytemp_d27e7965.csv |
| e154 | branch_loss | 0.576300366 | 0.576306641 |  | weak_rejected |  | Default to no same-family rescue. Use E144 only as an explicit unrepaired-branch contrast if that question is worth a public slot. | information_only:submission_e144_activeboundary_d7b4b331.csv |
| e154 | hard_fail | 0.576306641 | inf |  | rejected |  | Close repaired-branch siblings and return to representation search or, at most, use E144 as a final information-only branch contrast. |  |

## Interpretation

- E216 does not kill every JEPA idea. It kills the masked-family S2/rank
  translator as a public-safe submission family. E224 is mostly Q3/S4 movement,
  with low E216 cosine, so it remains a separate JEPA test.
- E224/E166 are genuinely different sensors (`cosine=0.074348`, top50 overlap
  `1`). A blind blend would erase the value of the next public observation.
- E154 is useful, but not first-slot maximal information: E224 covers `0.885621`
  of E154 mass same-sign, so E154 is partly an inherited-body counterfactual.
- The public-anchor proxy still cannot choose frontier files by score. Its
  best LOOCV MAE is larger than the public gaps that separate E95, E101,
  mixmin, and E176.

## Beliefs Killed

- Killed: "E216 means all JEPA-family probes are dead." It only resolves the S2
  support-tail translator.
- Killed: "A scalar public-anchor proxy can rank the next frontier candidate."
  The proxy is useful for geometry and failure-class detection, not for
  post-E95 one-cell ordering.
- Killed for now: "Submit an E224/E166/E154 blend." E228 shows E224 and E166
  are separate high-information sensors; blending before feedback destroys the
  experiment.

## Next Action

Submit E224 only if the next public slot is meant to answer the JEPA question.
After its public score, decode it with:

```bash
python3 analysis_outputs/e225_e224_public_feedback_decoder.py --score <PUBLIC_LB>
```

If the next slot is instead meant to escape JEPA and test an independent
counter-world, submit E166 and decode with:

```bash
python3 analysis_outputs/e227_e166_public_feedback_decoder.py --score <PUBLIC_LB>
```
