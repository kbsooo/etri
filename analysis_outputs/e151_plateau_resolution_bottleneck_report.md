# E151 Plateau Resolution Bottleneck Audit

## Question

Is the `0.5762913298` plateau mainly an ordinary candidate-selection/modeling
problem, or is it a resolution/decoder bottleneck where public-tail-safe
directions and local-upside directions only intersect on a tiny branch?

## Strangest Observed Point

The current public frontier is separated from mixmin by only
`0.0000153107`, while the best known-LB selector p90
error is `0.0008164966`.
That is `53.33x`
the frontier edge. At the same time, E144's improvement over E143 locally is
only `0.0000001746`.

## Current Strongest World Model

`E95 is a real S-heavy hardtail/calibration law. The next residual structure is
visible, but current validation/proxy selectors cannot resolve frontier-scale
edges, and most decoders turn visible state into either local reward or
public-tail safety, not both. E142/E143/E144 are the only current intersection,
and E144 is a branch-pruned sensor rather than a broad new representation.`

## What This World Predicts

- Old-file universe search should keep returning no novel strict successor.
- Local-gradient/state-aware probes can show impressive mean/local reward but
  fail strict/actionable gates or p95/tail budget.
- Any public-improving successor before a new representation decoder should be
  E95-relative, small, and heavily constrained by E72/E101 tail geometry.
- E144 public feedback will be informative, but even a win is a branch validation,
  not a 0.54-scale breakthrough.

## Smallest Experiment That Can Kill It

Two options can kill this model:

1. Public: submit `submission_e144_activeboundary_d7b4b331.csv` and interpret
   with `analysis_outputs/e150_e144_postfeedback_interpreter.py --score <LB>`.
2. Local: produce a new representation-to-probability decoder that passes
   strict structure, E72 budget, post-E101 p95, and independent geometry with a
   local edge comfortably above `1e-5` without being E142/E143/E144-collinear.

## Public Edge Scales

| edge | delta_logloss | abs_scale | read |
| --- | --- | --- | --- |
| mixmin_gain_vs_a2c8 | -0.0011326805 | 0.0011326805 | large anchor-loss/binary-world jump; not the current plateau scale |
| e95_gain_vs_mixmin | -0.0000153107 | 0.0000153107 | current frontier edge; hardtail localization is real but tiny |
| e101_loss_vs_e95 | 0.0000090362 | 0.0000090362 | resolved negative sensor; one small S3-scale boundary can erase most expected gain |
| e72_loss_vs_mixmin | 0.0001011367 | 0.0001011367 | failed broad movement scale; large enough for public to clearly reject |

## Resolution Evidence

| evidence | value | reference | ratio_vs_e95_edge | ratio_vs_e101_edge | ratio_vs_e144_local_edge | interpretation |
| --- | --- | --- | --- | --- | --- | --- |
| best_known_lb_selector_p90_error | 0.0008164966 | e98_e95_updated_selector_model_scores.csv | 53.3284984940 | 90.3584075044 | 83.9504985881 | movement-fingerprint selectors are far too coarse for frontier-scale ranking |
| e101_actual_minus_local_mean | 0.0000252415 | e120_post_e101_public_observation_summary.csv | 1.6486177478 | 2.7933746210 | 2.5952780561 | local stress was optimistic by more than the entire E95 gain over mixmin |
| e144_vs_e95_local_edge | -0.0000097259 | e144_e143_active_boundary_refine_frontier.csv | 0.6352374243 | 1.0763296112 | 1.0000000000 | E144 is a readable hypothesis sensor but not a 0.54-scale movement |
| e144_vs_e143_local_tiebreak | -0.0000001746 | e144_e143_active_boundary_refine_frontier.csv | 0.0114019518 | 0.0193191677 | 0.0179491184 | the E144-over-E143 local edge is far below selector/public resolution |
| e144_cosine_with_e143 | 0.9919187188 | e149_e144_anchor_geometry_summary.csv |  |  |  | E144 is branch-pruned geometry, not independent representation |

## Family Evidence

| family | best_local_edge | best_tail_p95 | strict_or_submit_count | failure_mode | belief_update |
| --- | --- | --- | --- | --- | --- |
| old_submission_universe |  |  | 0 | strict_novel_actionable=0 | candidate selection among old files is not the main missing lever |
| density_synthesis | -0.0000015120 | 0.0000004911 | 0 | submit_gate=0; local reward and public-tail safety do not meet under the family gates | use as representation diagnostic, not as submission source |
| atom_combo_density | -0.0000018128 | 0.0000082046 | 0 | submit_gate=0; local reward and public-tail safety do not meet under the family gates | use as representation diagnostic, not as submission source |
| veto_nullspace_gradient | -0.0001127725 | -0.0000601849 | 0 | submit_gate=0; local reward and public-tail safety do not meet under the family gates | use as representation diagnostic, not as submission source |
| blocktarget_state_gradient | -0.0000435918 | 0.0000028058 | 0 | submit_gate=0; local reward and public-tail safety do not meet under the family gates | use as representation diagnostic, not as submission source |
| blocktarget_vetonull_overlap | -0.0000304675 | -0.0000156907 | 0 | submit_gate=0; local reward and public-tail safety do not meet under the family gates | use as representation diagnostic, not as submission source |
| set_consensus_decoder | -0.0000220289 | -0.0000105204 | 0 | submit_gate=0; local reward and public-tail safety do not meet under the family gates | use as representation diagnostic, not as submission source |
| tailworld_primitive_decoder_before_clip | -0.0000139733 | 0.0000001415 | 0 | relaxed structure exists but e72 budget/post101 p95 fail | the blocker is transfer-tail budget, not exact-tail arithmetic |
| transfer_budget_clip_e142 | -0.0000140137 | -0.0000037623 | 35 | not final until public feedback | first live residual branch opens, but still fails active/Q2S3 strictness |
| active_q2s3_repair_e143 | -0.0000106546 | -0.0000037581 | 15 | not final until public feedback | strict branch opens, but public value is frontier-scale small |
| fine_boundary_e144 | -0.0000101828 | -0.0000035916 | 9 | survives as live sensor | E144 is the current sensor, but only a tiny same-branch refinement |

## Bottleneck Category Status

| category | status | evidence | kill_condition |
| --- | --- | --- | --- |
| A_data_signal_shortage | evidence_weak_partial | E142-E144 and blocktarget states still produce local/post101 signal; the issue is safe decoding, not absence of all signal. | If independent representation creates no local/post101 signal after E144, upgrade toward data-signal shortage. |
| B_validation_mismatch | evidence_strong | best known-LB selector p90 is 53.33x the E95 edge; E101 local optimism is 1.65x the E95 edge. | A new validation object must rank E95/E101/E144 correctly with error below 5e-6. |
| C_public_subset_mismatch | evidence_strong_but_underidentified | E101 public feedback invalidated broad-plausible local transfer while preserving part of mixmin gain; E144 requires score+attribution+geometry. | E144 clean win with attribution dominated by inherited body would reduce subset-mismatch emphasis. |
| D_target_prior_calibration_tail | evidence_strong | E95 hardtail survives, E101 one-cell-scale S3 boundary misses, and E144 is mostly Q3/S3/S2/Q1/S4 tail calibration. | A broad all-target move beats E95 without hardtail pruning. |
| E_representation_decoder_problem | evidence_strong | E137/E138 show state/safety visibility, but submit gates stay zero until E142-E144 hand-built decoder branch. | A representation-to-probability decoder passes strict, budget, post101 p95, and independent geometry without manual clipping. |
| F_candidate_selection_problem | mostly_rejected_for_existing_files | E129 strict novel actionable count is 0; E144 branch count is 9 but cos(E144,E143)=0.991919. | A forgotten old candidate passes E129 plus E120/E149-style stress without being same-family. |

## Experiment Result

E151 does not create a submission. It falsifies the easy explanation that the
plateau is mainly a missed old candidate or a generic model-capacity problem.
The stronger explanation is a decoder/resolution bottleneck: the signal is
visible enough to form E142-E144, but public-safe probability movement is only
certified on a very narrow, E143-collinear branch.

## Belief Update

- Strengthen: validation mismatch, public subset/tail calibration, and
  representation-decoder bottleneck.
- Weaken: old-candidate selection failure and same-family Q2/S3 amplitude
  tweaking.
- Keep alive: E144 as the next public sensor.

## Next Highest-Information Action

Submit `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` if a
single public slot is available. If waiting, the next local experiment should
not be a blend/top-count sweep. It should build an independent decoder target:
predict the transfer-budget-neutral residual representation, then prove it can
move probabilities with strict/actionable gates and non-collinearity to E143.

## Submission Candidate

- File: `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`
- Intent: test whether E95 can accept a branch-pruned, transfer-budget-neutral
  residual movement after active/Q2S3 pruning.
- Expected public reaction: a clean or micro win strengthens the residual branch;
  a tie keeps E95 as practical frontier; a fine loss is conditional and does not
  automatically justify E143; branch loss/hard fail closes same-family rescue.
- Failure interpretation: public hidden S3/Q3/body tail is more adverse than the
  visible priors, or the whole E142/E143/E144 branch is public-sensor overfit.
