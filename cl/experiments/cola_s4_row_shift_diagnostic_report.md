# CoLa S4 row-shift diagnostic

Goal: intersect CoLa latent S4 movement, target action map permission, and sparse S4 context-token evidence.

## Model/probe info

- anchor_train_logloss: `0.6089`
- cola_train_logloss: `0.5884`
- cola_says_move threshold abs shift: `0.0818`

## Counts

| condition                                   |   n |
|:--------------------------------------------|----:|
| all_test_rows                               | 250 |
| cola_says_move                              |  50 |
| action_allows_move                          |  40 |
| context_token_evidence                      |  40 |
| three_way_intersection                      |   5 |
| candidate_safe_intersection_direction_agree |   4 |

## Safe intersection rows

|   row_id | subject_id   | lifelog_date        | regime   |   s4_anchor_p |   s4_cola_p |   cola_shift | cola_direction   | action    | direction   |   strength |   s4_context_token_count | neighbor_agree_S4   |   candidate_hint_p |   candidate_delta | reason                                          |
|---------:|:-------------|:--------------------|:---------|--------------:|------------:|-------------:|:-----------------|:----------|:------------|-----------:|-------------------------:|:--------------------|-------------------:|------------------:|:------------------------------------------------|
|      222 | id09         | 2024-09-13 00:00:00 | tail     |        0.4405 |      0.8450 |       0.4045 | UP               | TINY_MOVE | UP          |     0.3500 |                        5 | False               |             0.6445 |            0.0591 | multiple S4 context tokens present; capped only |
|      225 | id09         | 2024-09-19 00:00:00 | tail     |        0.5197 |      0.6742 |       0.1545 | UP               | TINY_MOVE | UP          |     0.3500 |                        5 | False               |             0.6445 |            0.0591 | multiple S4 context tokens present; capped only |
|      248 | id10         | 2024-09-25 00:00:00 | tail     |        0.4977 |      0.6442 |       0.1465 | UP               | TINY_MOVE | UP          |     0.3500 |                        5 | False               |             0.7197 |            0.0531 | multiple S4 context tokens present; capped only |
|      221 | id09         | 2024-09-12 00:00:00 | tail     |        0.5262 |      0.6414 |       0.1152 | UP               | TINY_MOVE | UP          |     0.3500 |                        6 | False               |             0.6445 |            0.0591 | multiple S4 context tokens present; capped only |

## Three-way rows with direction conflict/weakness

|   row_id | subject_id   | lifelog_date        | regime   |   s4_anchor_p |   s4_cola_p |   cola_shift | cola_direction   | action    | direction   |   strength |   s4_context_token_count | neighbor_agree_S4   |   candidate_hint_p |   candidate_delta | reason                                          |
|---------:|:-------------|:--------------------|:---------|--------------:|------------:|-------------:|:-----------------|:----------|:------------|-----------:|-------------------------:|:--------------------|-------------------:|------------------:|:------------------------------------------------|
|      247 | id10         | 2024-09-24 00:00:00 | tail     |        0.5023 |      0.4007 |      -0.1016 | DOWN             | TINY_MOVE | UP          |     0.3500 |                        4 | False               |             0.7197 |            0.0531 | multiple S4 context tokens present; capped only |

## Top CoLa S4 shifts overall

|   row_id | subject_id   | lifelog_date        | regime   |   s4_anchor_p |   s4_cola_p |   cola_shift | cola_direction   | action    | direction   |   strength |   s4_context_token_count | neighbor_agree_S4   |   candidate_hint_p |   candidate_delta | reason                                          | cola_says_move   | action_allows_move   | context_token_evidence   | direction_agree   |
|---------:|:-------------|:--------------------|:---------|--------------:|------------:|-------------:|:-----------------|:----------|:------------|-----------:|-------------------------:|:--------------------|-------------------:|------------------:|:------------------------------------------------|:-----------------|:---------------------|:-------------------------|:------------------|
|       22 | id01         | 2024-09-10 00:00:00 | tail     |        0.3699 |      0.7847 |       0.4148 | UP               | FREEZE    | HOLD        |     0.0000 |                        0 | False               |             0.4878 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|      222 | id09         | 2024-09-13 00:00:00 | tail     |        0.4405 |      0.8450 |       0.4045 | UP               | TINY_MOVE | UP          |     0.3500 |                        5 | False               |             0.6445 |            0.0591 | multiple S4 context tokens present; capped only | True             | True                 | True                     | True              |
|        6 | id01         | 2024-08-06 00:00:00 | hole     |        0.4146 |      0.8119 |       0.3973 | UP               | FREEZE    | HOLD        |     0.0000 |                        0 | False               |             0.4878 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|       12 | id01         | 2024-08-14 00:00:00 | hole     |        0.4027 |      0.7242 |       0.3215 | UP               | FREEZE    | HOLD        |     0.0000 |                        0 | False               |             0.4878 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|       13 | id01         | 2024-08-16 00:00:00 | hole     |        0.3970 |      0.6973 |       0.3003 | UP               | FREEZE    | HOLD        |     0.0000 |                        0 | False               |             0.4878 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|      113 | id05         | 2024-10-06 00:00:00 | hole     |        0.5213 |      0.8215 |       0.3002 | UP               | FREEZE    | HOLD        |     0.0000 |                        0 | False               |             0.4091 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|      126 | id05         | 2024-11-18 00:00:00 | tail     |        0.4607 |      0.7039 |       0.2432 | UP               | FREEZE    | HOLD        |     0.0000 |                        0 | False               |             0.4091 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|      125 | id05         | 2024-11-17 00:00:00 | tail     |        0.4706 |      0.6907 |       0.2201 | UP               | FREEZE    | HOLD        |     0.0000 |                        0 | False               |             0.4091 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|      111 | id05         | 2024-10-04 00:00:00 | hole     |        0.3605 |      0.5726 |       0.2121 | UP               | FREEZE    | HOLD        |     0.0000 |                        0 | False               |             0.4091 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|       54 | id02         | 2024-10-11 00:00:00 | tail     |        0.5811 |      0.7806 |       0.1995 | UP               | FREEZE    | HOLD        |     0.0000 |                        0 | False               |             0.7500 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|      121 | id05         | 2024-11-12 00:00:00 | hole     |        0.3256 |      0.1444 |      -0.1812 | DOWN             | FREEZE    | HOLD        |     0.0000 |                        0 | False               |             0.4091 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|        8 | id01         | 2024-08-09 00:00:00 | hole     |        0.4048 |      0.5834 |       0.1786 | UP               | FREEZE    | HOLD        |     0.0000 |                        0 | False               |             0.4878 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|      127 | id05         | 2024-11-19 00:00:00 | tail     |        0.3153 |      0.4778 |       0.1625 | UP               | FREEZE    | HOLD        |     0.0000 |                        0 | False               |             0.4091 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|      225 | id09         | 2024-09-19 00:00:00 | tail     |        0.5197 |      0.6742 |       0.1545 | UP               | TINY_MOVE | UP          |     0.3500 |                        5 | False               |             0.6445 |            0.0591 | multiple S4 context tokens present; capped only | True             | True                 | True                     | True              |
|      122 | id05         | 2024-11-13 00:00:00 | hole     |        0.3218 |      0.4704 |       0.1486 | UP               | FREEZE    | HOLD        |     0.0000 |                        0 | False               |             0.4091 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|      248 | id10         | 2024-09-25 00:00:00 | tail     |        0.4977 |      0.6442 |       0.1465 | UP               | TINY_MOVE | UP          |     0.3500 |                        5 | False               |             0.7197 |            0.0531 | multiple S4 context tokens present; capped only | True             | True                 | True                     | True              |
|      120 | id05         | 2024-11-07 00:00:00 | hole     |        0.4034 |      0.5480 |       0.1447 | UP               | FREEZE    | HOLD        |     0.0000 |                        0 | True                |             0.4091 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|      161 | id07         | 2024-07-22 00:00:00 | hole     |        0.5481 |      0.6864 |       0.1383 | UP               | FREEZE    | HOLD        |     0.0000 |                        0 | True                |             0.4694 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|      102 | id04         | 2024-10-24 00:00:00 | hole     |        0.4653 |      0.3317 |      -0.1336 | DOWN             | FREEZE    | HOLD        |     0.0000 |                        0 | True                |             0.5088 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |
|      223 | id09         | 2024-09-15 00:00:00 | tail     |        0.6050 |      0.7369 |       0.1319 | UP               | FREEZE    | HOLD        |     0.0000 |                        0 | False               |             0.5854 |            0.0000 | no strong S4 context event                      | True             | False                | False                    | False             |

## Candidate

- wrote diagnostic capped candidate: `/Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_cola_s4_context_capped_diag_prob.csv`
- wrote shift file: `/Users/kbsoo/Downloads/dacon/etri/cl/experiments/submission_cola_s4_context_capped_diag_prob_shift.csv`
- This is not an automatic submit recommendation. It only nudges direction-agreeing intersection rows by `0.35 * cola_shift`, capped at ±0.04.

## Verdict

PARTIAL: 4 row(s) pass strict intersection with direction agreement. Worth inspecting as S4-only capped diagnostic, not broad DL evidence.