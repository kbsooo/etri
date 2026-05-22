# S2 Opportunity-State Decoder

## Purpose

Test whether the new S2 PSG opportunity signal can be promoted from source selection into an explicit intermediate-state decoder. Each outer fold first clusters opportunity/Q-state latent rows without labels, then maps those states to S2 with small state-rate or state-logistic decoders selected by inner folds.

## Result

- Nested S2 logloss: `0.582496`
- Fold-safe subject-prior S2 logloss: `0.579856`
- Current protected fixed-map S2 logloss: `0.567195`
- Projected fixed-map avg if only S2 is replaced: `0.612430`
- Current fixed-map avg reference: `0.610244`

## Selection Counts

| selected | outer_count |
| --- | --- |
| psg_qrel__absolute__k5__state_rate__b25 | 3 |
| psg_qrel__absolute__k4__state_rate__b25 | 2 |

## Best Full-OOF Candidates

| candidate | full_oof_s2_log_loss |
| --- | --- |
| psg_qrel__absolute__k4__state_rate__b25 | 0.582151 |
| psg_qrel__absolute__k5__state_rate__b25 | 0.582310 |
| psg_opp_mob__deviation__k5__state_rate__b25 | 0.584513 |
| psg_opp__absolute_plus_deviation__k4__soft_state_rate__b25 | 0.584702 |
| psg_opp__deviation__k4__soft_state_rate__b25 | 0.584778 |
| psg_opp__deviation__k3__state_rate__b25 | 0.584803 |
| psg_opp__deviation__k5__soft_state_rate__b25 | 0.584813 |
| psg_opp__deviation__k3__soft_state_rate__b25 | 0.584816 |
| psg_opp__deviation__k4__state_rate__b25 | 0.584866 |
| psg_opp__absolute_plus_deviation__k4__state_rate__b25 | 0.585058 |
| psg_opp_mob__deviation__k4__state_rate__b25 | 0.585328 |
| cc_opp__absolute_plus_deviation__k4__state_rate__b25 | 0.585349 |
| psg_opp__deviation__k5__state_rate__b25 | 0.585869 |
| psg_qrel__absolute__k4__state_rate__b40 | 0.587573 |
| psg_qrel__absolute__k5__state_rate__b40 | 0.587819 |
| psg_opp_mob__deviation__k5__state_rate__b40 | 0.591092 |
| psg_opp__deviation__k4__soft_state_rate__b40 | 0.591407 |
| psg_opp__deviation__k3__state_rate__b40 | 0.591415 |
| psg_opp__deviation__k5__soft_state_rate__b40 | 0.591460 |
| psg_opp__deviation__k3__soft_state_rate__b40 | 0.591514 |

## Inner Candidate Scores

| outer_fold | candidate | inner_s2_log_loss |
| --- | --- | --- |
| 1 | psg_qrel__absolute__k5__state_rate__b25 | 0.578260 |
| 1 | psg_qrel__absolute__k4__state_rate__b25 | 0.578702 |
| 1 | psg_opp__deviation__k5__soft_state_rate__b25 | 0.579462 |
| 1 | psg_opp__deviation__k3__soft_state_rate__b25 | 0.579506 |
| 1 | psg_opp__deviation__k3__state_rate__b25 | 0.579520 |
| 1 | psg_opp_mob__deviation__k4__state_rate__b25 | 0.579542 |
| 1 | psg_opp__deviation__k4__soft_state_rate__b25 | 0.579593 |
| 1 | psg_opp__absolute_plus_deviation__k4__soft_state_rate__b25 | 0.579694 |
| 1 | psg_opp_mob__deviation__k5__state_rate__b25 | 0.579736 |
| 1 | psg_opp__absolute_plus_deviation__k4__state_rate__b25 | 0.580142 |
| 1 | psg_opp__deviation__k4__state_rate__b25 | 0.580378 |
| 1 | cc_opp__absolute_plus_deviation__k4__state_rate__b25 | 0.581383 |
| 1 | psg_opp__deviation__k5__state_rate__b25 | 0.581492 |
| 1 | psg_qrel__absolute__k5__state_rate__b40 | 0.585905 |
| 1 | psg_qrel__absolute__k4__state_rate__b40 | 0.586603 |
| 1 | psg_opp__deviation__k5__soft_state_rate__b40 | 0.587574 |
| 1 | psg_opp__deviation__k3__soft_state_rate__b40 | 0.587641 |
| 1 | psg_opp__deviation__k3__state_rate__b40 | 0.587696 |
| 1 | psg_opp_mob__deviation__k4__state_rate__b40 | 0.587715 |
| 1 | psg_opp__deviation__k4__soft_state_rate__b40 | 0.587778 |
| 1 | psg_opp_mob__deviation__k5__state_rate__b40 | 0.588051 |
| 1 | psg_opp__deviation__k4__state_rate__b40 | 0.589119 |
| 1 | cc_opp__absolute_plus_deviation__k4__state_rate__b40 | 0.590874 |
| 1 | psg_opp__deviation__k5__state_rate__b40 | 0.590989 |
| 2 | psg_qrel__absolute__k4__state_rate__b25 | 0.596171 |
| 2 | psg_qrel__absolute__k5__state_rate__b25 | 0.596728 |
| 2 | psg_opp_mob__deviation__k5__state_rate__b25 | 0.599477 |
| 2 | psg_qrel__absolute__k4__state_rate__b40 | 0.599556 |
| 2 | psg_qrel__absolute__k5__state_rate__b40 | 0.600315 |
| 2 | psg_opp__deviation__k5__soft_state_rate__b25 | 0.600495 |
| 2 | psg_opp__absolute_plus_deviation__k4__soft_state_rate__b25 | 0.600516 |
| 2 | psg_opp_mob__deviation__k4__state_rate__b25 | 0.600601 |
| 2 | psg_opp__deviation__k4__soft_state_rate__b25 | 0.600615 |
| 2 | psg_opp__deviation__k3__soft_state_rate__b25 | 0.600721 |
| 2 | psg_opp__deviation__k3__state_rate__b25 | 0.601040 |
| 2 | psg_opp__absolute_plus_deviation__k4__state_rate__b25 | 0.601098 |
| 2 | psg_opp__deviation__k5__state_rate__b25 | 0.601245 |
| 2 | cc_opp__absolute_plus_deviation__k4__state_rate__b25 | 0.601416 |
| 2 | psg_opp__deviation__k4__state_rate__b25 | 0.601528 |
| 2 | psg_opp_mob__deviation__k5__state_rate__b40 | 0.604498 |
| 2 | psg_opp__deviation__k5__soft_state_rate__b40 | 0.605864 |
| 2 | psg_opp__deviation__k4__soft_state_rate__b40 | 0.606055 |
| 2 | psg_opp_mob__deviation__k4__state_rate__b40 | 0.606180 |
| 2 | psg_opp__deviation__k3__soft_state_rate__b40 | 0.606242 |
| 2 | psg_opp__deviation__k3__state_rate__b40 | 0.606694 |
| 2 | psg_opp__deviation__k5__state_rate__b40 | 0.607250 |
| 2 | psg_opp__deviation__k4__state_rate__b40 | 0.607641 |
| 2 | cc_opp__absolute_plus_deviation__k4__state_rate__b40 | 0.607782 |
| 3 | psg_qrel__absolute__k5__state_rate__b25 | 0.599079 |
| 3 | psg_qrel__absolute__k4__state_rate__b25 | 0.599906 |
| 3 | psg_opp_mob__deviation__k5__state_rate__b25 | 0.600032 |
| 3 | psg_opp__deviation__k3__soft_state_rate__b25 | 0.601173 |
| 3 | psg_opp_mob__deviation__k4__state_rate__b25 | 0.601303 |
| 3 | psg_opp__deviation__k4__soft_state_rate__b25 | 0.601350 |
| 3 | psg_opp__deviation__k5__soft_state_rate__b25 | 0.601355 |
| 3 | psg_opp__absolute_plus_deviation__k4__soft_state_rate__b25 | 0.601383 |
| 3 | psg_opp__deviation__k3__state_rate__b25 | 0.601600 |
| 3 | psg_opp__absolute_plus_deviation__k4__state_rate__b25 | 0.601805 |
| 3 | psg_opp__deviation__k4__state_rate__b25 | 0.602071 |
| 3 | psg_opp__deviation__k5__state_rate__b25 | 0.602442 |
| 3 | cc_opp__absolute_plus_deviation__k4__state_rate__b25 | 0.602762 |
| 3 | psg_qrel__absolute__k5__state_rate__b40 | 0.602908 |
| 3 | psg_qrel__absolute__k4__state_rate__b40 | 0.604151 |
| 3 | psg_opp_mob__deviation__k5__state_rate__b40 | 0.604277 |
| 3 | psg_opp__deviation__k3__soft_state_rate__b40 | 0.605993 |
| 3 | psg_opp__deviation__k5__soft_state_rate__b40 | 0.606224 |
| 3 | psg_opp__deviation__k4__soft_state_rate__b40 | 0.606230 |
| 3 | psg_opp_mob__deviation__k4__state_rate__b40 | 0.606269 |
| 3 | psg_opp__deviation__k3__state_rate__b40 | 0.606578 |
| 3 | psg_opp__deviation__k4__state_rate__b40 | 0.607387 |
| 3 | psg_opp__deviation__k5__state_rate__b40 | 0.607932 |
| 3 | cc_opp__absolute_plus_deviation__k4__state_rate__b40 | 0.608741 |
| 4 | psg_qrel__absolute__k4__state_rate__b25 | 0.586313 |
| 4 | cc_opp__absolute_plus_deviation__k4__state_rate__b25 | 0.586626 |
| 4 | psg_opp__absolute_plus_deviation__k4__state_rate__b25 | 0.587123 |
| 4 | psg_opp__deviation__k4__state_rate__b25 | 0.587292 |
| 4 | psg_opp__deviation__k5__soft_state_rate__b25 | 0.587305 |
| 4 | psg_opp__deviation__k4__soft_state_rate__b25 | 0.587327 |
| 4 | psg_opp__deviation__k5__state_rate__b25 | 0.587363 |
| 4 | psg_qrel__absolute__k5__state_rate__b25 | 0.587410 |

## Read

- This is stricter than the previous fixed-map scout because the selected S2 state decoder is chosen inside each outer fold.
- A useful result should beat the protected fixed-map S2 loss or at least approach the direct `psg_opp` probe while using state-mediated decoding.
- If it fails, the opportunity clue is still real but likely needs a richer encoder objective rather than KMeans state bins.

## Sample Drift vs v83

| mean_abs_s2_drift | max_abs_s2_drift | pred_s2_mean | ref_s2_mean |
| --- | --- | --- | --- |
| 0.074416 | 0.286572 | 0.660113 | 0.643925 |
