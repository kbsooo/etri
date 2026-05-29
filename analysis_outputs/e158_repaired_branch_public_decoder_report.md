# E158 Repaired Branch Public Decoder

## Question

The current next public file is `submission_e154_s3repair_9f2e2e73.csv`, but
E155/E157/E156/E144 now form a sensor stack around it. The question is not
"which tiny local edge is largest?" It is:

`If public feedback arrives for E154 or its controls, which hidden-world belief
dies, and which follow-up remains justified?`

## Strangest Point

The repaired controls are highly collinear and their local separations are much
smaller than the known public-sensor uncertainty. E157 beats E155 locally by
only `-0.000000041955` when
read as E157-minus-E155, while E154 beats E155 by
`-0.000001795559` and E156
is only `0.000000358921`
away from E155. These are branch controls, not independent 0.54-path models.

## Live Candidate Geometry

| tag | role | all_minus_base | post101_p95_vs_e95_e101_sensor | e72_plausible_gap_vs_e95 | body_norm_ratio | changed_cells_vs_e95_computed | cos_vs_e144 | cos_vs_e154 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e154 | full repaired S3 active-boundary body | -0.000012158 | -0.000004653 | -0.000002860 |  | 294 | 0.983569299 | 1.000000000 |
| e155 | 25% repaired body amplitude control | -0.000010362 | -0.000003746 | -0.000001077 | 0.250000000 | 294 | 0.998962769 | 0.990769489 |
| e157 | Q1+Q3+S2+S4 low-body Pareto control | -0.000010404 | -0.000003807 | -0.000001671 | 0.240336139 | 285 | 0.999041566 | 0.989192911 |
| e156 | minimum-body Q1/S2/S4 decomposition control | -0.000010004 | -0.000003712 | -0.000002266 | 0.171266667 | 246 | 0.999515751 | 0.985122955 |
| e144 | unrepaired residual-branch contrast | -0.000009726 | -0.000003430 | 0.000000000 |  | 185 | 1.000000000 | 0.983569299 |

## Pairwise Distinguishability

| left | right | cos_left_right_vs_e95 | changed_cells_left_minus_right | local_all_minus_delta_left_minus_right | local_delta_readable |
| --- | --- | --- | --- | --- | --- |
| e154 | e155 | 0.990769489 | 294 | -0.000001796 | False |
| e154 | e157 | 0.989192911 | 294 | -0.000001754 | False |
| e154 | e156 | 0.985122955 | 294 | -0.000002154 | True |
| e154 | e144 | 0.983569299 | 294 | -0.000002432 | True |
| e155 | e157 | 0.999661514 | 129 | 0.000000042 | False |
| e155 | e156 | 0.998991027 | 190 | -0.000000359 | False |
| e155 | e144 | 0.998962769 | 294 | -0.000000637 | False |
| e157 | e155 | 0.999661514 | 129 | -0.000000042 | False |
| e157 | e156 | 0.999354655 | 168 | -0.000000401 | False |
| e157 | e144 | 0.999041566 | 238 | -0.000000679 | False |
| e156 | e155 | 0.998991027 | 190 | 0.000000359 | False |
| e156 | e157 | 0.999354655 | 168 | 0.000000401 | False |
| e156 | e144 | 0.999515751 | 143 | -0.000000278 | False |

## Public Score Bands

| outcome | public_lb_lo_exclusive | public_lb_hi_inclusive | world_update | next_action_e154 |
| --- | --- | --- | --- | --- |
| breakthrough_win | -inf | 0.576271330 | The repaired branch is larger than the current E95-over-mixmin edge. Add the observed file as a new anchor before testing siblings. | Promote E154 and rerun exact-delta audits. Do not spend the next slot on E155/E157/E156 until the new anchor geometry is rebuilt. |
| clean_win | 0.576271330 | 0.576284330 | The branch is public-real at readable frontier scale. | Promote E154; use E155 only as a private-risk amplitude audit, not as the next automatic public file. |
| micro_win | 0.576284330 | 0.576289330 | The branch is alive but remains calibration-scale. | Promote E154 cautiously; next local work should seek non-collinear representation, not target-axis micro-tuning. |
| tie | 0.576289330 | 0.576293330 | The public sensor cannot distinguish the branch from E95. | Keep E95 practical frontier; E155 is allowed only if deliberately testing lower amplitude, not expected improvement. |
| small_loss | 0.576293330 | 0.576300366 | The branch loses but not worse than the resolved E101 negative sensor. | If spending another slot on this branch, E155 is the only clean same-family follow-up; do not jump to E157/E156 before E155. |
| branch_loss | 0.576300366 | 0.576306641 | The branch is weaker than E101 but still preserves some E95 gain over mixmin. | Treat E155 as an explicit overextension test only. If E155 is skipped or loses, use E144 as the unrepaired contrast or close the branch. |
| hard_fail | 0.576306641 | inf | The branch gives back the E95 gain. Nearby repaired controls are suspect. | Do not submit E157/E156. E155 is only an information-only amplitude salvage; otherwise fall back to E144 or representation search. |

## Decision

- Submit order remains `E154 -> E155 -> E157 -> E156 -> E144`.
- E154 is the only first sensor because it asks the full repaired all-four
  question and is readable against unrepaired E144; its separation from E155 is
  not public-readable by the `2e-6` guardrail.
- E155 is the clean amplitude-control if E154 loses or ties.
- E157 and E156 should not be used before E155; their local separation from
  E155 is below the `2e-6` public-readable guardrail.
- If E154 hard-fails above mixmin, do not rescue with target-axis micro-controls.
  Either test E144 as the unrepaired contrast or return to representation search.

## Files

- candidate table: `analysis_outputs/e158_repaired_branch_public_decoder_candidates.csv`
- pairwise table: `analysis_outputs/e158_repaired_branch_public_decoder_pairwise.csv`
- score bands: `analysis_outputs/e158_repaired_branch_public_decoder_bands.csv`
