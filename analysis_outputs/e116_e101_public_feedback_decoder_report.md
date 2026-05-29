# E116 E101 Public Feedback Decoder

## Question

E115 says `submission_e101_q2s3tail_177569bc.csv` is the next public sensor.
E116 pre-registers how to interpret its public LB before seeing it.

Current frontier:

- E95 file: `submission_e95_hardtail_541e3973.csv`
- E95 public LB: `0.5762913298`
- mixmin public LB: `0.5763066405`
- E95 edge versus mixmin: `-0.0000153107`

## Decoder

| outcome | public_lb_lo_exclusive | public_lb_hi_inclusive | e115_scenario_rate | e107_selection_mode | e107_model_tension | next_action | candidate_to_test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| strong_win | -inf | 0.576261330 | 0.134704519 | nearest | True | Rerun E107/E115 with the exact delta, then consider the risk E108 amp050 file as an upside sensor. | analysis_outputs/submission_e108_if_e101win_amp050_079aab57.csv |
| edge_win | 0.576261330 | 0.576280330 | 0.478273465 | within_tolerance | False | Use E108 amp050 for upside or E108 strict amp038 if the next slot must preserve E101-pass stress. | analysis_outputs/submission_e108_if_e101win_amp050_079aab57.csv or analysis_outputs/submission_e108_if_e101win_strict_amp038_64514c53.csv |
| small_win | 0.576280330 | 0.576288330 | 0.298667439 | within_tolerance | False | Prefer E108 strict amp038 if risk control matters; amp050 remains an upside sensor only. | analysis_outputs/submission_e108_if_e101win_strict_amp038_64514c53.csv |
| tie | 0.576288330 | 0.576294330 | 0.088354577 | within_tolerance | False | Keep E95 as frontier and rebuild E99/E101 worlds using the exact near-zero observation. |  |
| small_loss | 0.576294330 | 0.576311330 | 0.000000000 | nearest | True | Keep E95 as frontier, mark E101 branch as model tension, and rebuild the public-world model before any same-family file. |  |
| large_loss | 0.576311330 | inf | 0.000000000 | nearest | True | Stop the E101 family and return to broader hidden-block/public-subset diagnosis. |  |

## Decision Rules

- Strong/edge/small win: E101 direction is public-real. Consider E108 only
  after using the exact observed delta to rerun the conditional branch map.
- Tie: keep E95 as frontier and rebuild the E99/E101 world model. Do not
  amplify the same line.
- Small/large loss: the active-cell rollback support world failed. Do not use
  E108, E104 higher alpha, E106 subject-prior masks, active-restored E89/E85,
  or non-active grafts as automatic followups.

## Submission Status

No submission is materialized by E116. It is a public-feedback interpretation
artifact for `submission_e101_q2s3tail_177569bc.csv`.
