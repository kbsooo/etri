# E145 E144 Public Feedback Decoder

## Question

E144 is the current next public sensor:

- file: `submission_e144_activeboundary_d7b4b331.csv`
- intent: test whether E143's active/Q2S3 repair boundary is fine rather than a full-rollback cliff.
- current public frontier: `submission_e95_hardtail_541e3973.csv` at `0.5762913298`
- resolved negative comparison: `submission_e101_q2s3tail_177569bc.csv` at `0.5763003660`
- previous frontier comparison: `submission_mixmin_0c916bb4.csv` at `0.5763066405`

E145 pre-registers how to interpret the future E144 public LB before seeing it.

## Local Context

| item | value |
| --- | --- |
| selected tag | `e143_top_q2s3_weighted_24_d7b4b331` |
| selected mask | `top_q2s3_weighted_24` |
| keep factor | `0.150000` |
| rollback cells | `24` |
| changed cells vs E95 | `185` |
| E144 local all-minus-E95 | `-0.000009725930` |
| E143 local all-minus-E95 | `-0.000009551358` |
| E144 minus E143 local | `-0.000000174572` |
| E144 post-E101 p95 | `-0.000003430489` |
| E143 post-E101 p95 | `-0.000003368915` |

## Decoder Bands

| outcome | public_lb_lo_exclusive | public_lb_hi_inclusive | beats_e95 | beats_e101 | beats_mixmin | next_action | candidate_to_test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| breakthrough_win | -inf | 0.576271330 | True | True | True | Add E144 as the new public anchor, rerun exact-delta residual-branch audits, then consider whether E142 or a less-pruned neighbor is the next information sensor. | submission_e142_transferclip_09a92236.csv |
| clean_win | 0.576271330 | 0.576284330 | True | True | True | Promote E144 to frontier and rerun branch audits with E144 as the anchor before testing any less-pruned successor. |  |
| micro_win | 0.576284330 | 0.576289330 | True | True | True | Promote E144, but use the next experiment to find an independent representation signal rather than another tiny same-family boundary tweak. |  |
| tie | 0.576289330 | 0.576293330 | False | True | True | Keep E95 as the practical frontier; use E143 only as a deliberate boundary contrast, not an automatic next submission. |  |
| fine_loss_branch_alive | 0.576293330 | 0.576300366 | False | False | True | If spending another public slot on this branch, submit E143 as the clean contrast; otherwise pause same-family refinements and inspect the exact E144-minus-E143 retained cells. | submission_e143_activeq2s3repair_68ca656f.csv |
| branch_loss | 0.576300366 | 0.576306641 | False | False | False | Do not auto-submit E143/E142. Re-audit whether E101-conditioned transfer gates have become public-overfit selectors. |  |
| hard_fail | 0.576306641 | inf | False | False | False | Close E142/E143/E144 as public-sensor overfit and return to hidden representation search rather than local boundary repair. |  |

## World Updates And Guardrails

| outcome | world_update | forbidden_action |
| --- | --- | --- |
| breakthrough_win | E144 wins by more than the current E95-over-mixmin edge scale. The residual decoder is public-real and local stress likely underestimates its upside. | Do not jump to broad model/blend escalation; first check whether the same transfer-budget law explains the larger-than-expected win. |
| clean_win | E144 beats E95 at a readable frontier scale. The fine active/Q2S3 boundary is likely public-real. | Do not submit E142 immediately; E144's win would validate pruning, not unpruned residual movement. |
| micro_win | E144 beats E95 but only at a micro-edge scale. The fine boundary is alive, but the branch remains a narrow calibration/tail repair. | Do not interpret a micro-win as evidence for 0.54 progress or for relaxing the active/Q2S3 veto. |
| tie | E144 is indistinguishable from E95 at the current sensor scale. The residual branch is neither validated nor killed. | Do not post-hoc claim the fine boundary worked; the observation is too close to zero. |
| fine_loss_branch_alive | E144 loses to E95 but stays no worse than the resolved E101 negative sensor. The retained keep0.15 active tail may be too optimistic, while the conservative boundary remains testable. | Do not submit E142 before E143; the first question after this loss is fine-tail retention, not unpruned residual upside. |
| branch_loss | E144 is worse than E101 but still no worse than mixmin. The transfer-budget branch is weaker than the earlier negative Q2/S3 rollback sensor. | Do not rescue the branch with a nearby same-family file before explaining why it underperformed E101. |
| hard_fail | E144 gives back all E95 gain and more. The transfer-budget residual branch is not public-safe as a selector. | Do not tune top counts, keep factors, or active/Q2S3 masks on this branch. |

## Decision Rules

- Win by more than `7e-6`: E144 becomes a meaningful new public anchor; rerun exact-delta audits before testing less-pruned variants.
- Micro-win: promote E144 but do not claim a structural breakthrough or relax the active/Q2S3 veto.
- Tie: keep E95 as practical frontier; E144 did not give enough public information to justify post-hoc claims.
- Loss that stays no worse than E101: E143 is the only same-family contrast worth considering, because it removes the retained fine active tail.
- Worse than E101: do not auto-submit E143 or E142; first explain why E144 underperformed a resolved negative sensor.
- Worse than mixmin: close the E142/E143/E144 branch as selector overfit.

## Submission Status

No submission is created by E145. It is a public-feedback interpretation artifact for `submission_e144_activeboundary_d7b4b331.csv`.
