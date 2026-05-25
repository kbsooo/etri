# Subject/test-regime field notes

No submission generated. This is a row/target action map for deciding what is allowed to move.

## Easy glossary

- **MOVE**: prediction may be changed meaningfully from the subject prior, because the row has specific evidence.

- **TINY_MOVE**: prediction may move only a little; useful as a capped correction, not a new belief.

- **FREEZE**: keep close to the stable subject/base prediction. This does **not** mean impossible to improve; it means current evidence says changing it is more likely to overfit than help.


## Target rule in plain words

- **Q2**: most movable. It is the best target for day-level clues like nearby labels, coverage, and deviation.

- **Q3**: move only when neighbor-label grammar is clear, especially close prev/next labels agreeing.

- **Q1**: mostly keep stable. Our current signals for Q1 are weak and coverage can mislead.

- **S1**: mostly keep stable. Only tiny neighbor-based correction if very close evidence agrees.

- **S2/S3**: freeze. These behave like subject/static-response targets more than day-behavior targets.

- **S4**: tiny capped move only when strong context tokens appear.


## Test regime counts

| regime   |   n_rows |
|:---------|---------:|
| hole     |      156 |
| tail     |       94 |


## Action counts by target

| target   |   FREEZE |   MOVE |   TINY_MOVE |
|:---------|---------:|-------:|------------:|
| Q1       |      187 |      0 |          63 |
| Q2       |      108 |    108 |          34 |
| Q3       |       58 |     79 |         113 |
| S1       |      179 |      0 |          71 |
| S2       |      250 |      0 |           0 |
| S3       |      250 |      0 |           0 |
| S4       |      210 |      0 |          40 |


## Top non-freeze row/target candidates

|   row_id | subject_id   | lifelog_date   | regime   | target   | action   | direction   |   strength |   candidate_delta | reason                                                                                       |
|---------:|:-------------|:---------------|:---------|:---------|:---------|:------------|-----------:|------------------:|:---------------------------------------------------------------------------------------------|
|        2 | id01         | 2024-08-01     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.1889 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|       27 | id02         | 2024-08-25     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.1457 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|       31 | id02         | 2024-08-29     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.1457 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|       32 | id02         | 2024-08-30     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.1457 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|       33 | id02         | 2024-08-31     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.1457 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|       38 | id02         | 2024-09-05     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.1457 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|       59 | id03         | 2024-08-16     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.0811 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|       64 | id03         | 2024-08-22     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.0811 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|       65 | id03         | 2024-08-23     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.0811 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|       67 | id03         | 2024-08-26     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.0811 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|       69 | id03         | 2024-08-28     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.0811 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      109 | id05         | 2024-09-30     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.2397 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      110 | id05         | 2024-10-01     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.2397 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      111 | id05         | 2024-10-04     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.2397 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      112 | id05         | 2024-10-05     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.2397 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      121 | id05         | 2024-11-12     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.2397 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      141 | id06         | 2024-08-09     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.2535 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      153 | id07         | 2024-07-14     | hole     | Q2       | MOVE     | DOWN        |        0.9 |           -0.1375 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      154 | id07         | 2024-07-15     | hole     | Q2       | MOVE     | DOWN        |        0.9 |           -0.1375 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      156 | id07         | 2024-07-17     | hole     | Q2       | MOVE     | DOWN        |        0.9 |           -0.1375 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      158 | id07         | 2024-07-19     | hole     | Q2       | MOVE     | DOWN        |        0.9 |           -0.1375 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      162 | id07         | 2024-07-23     | hole     | Q2       | MOVE     | DOWN        |        0.9 |           -0.1375 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      166 | id07         | 2024-07-27     | hole     | Q2       | MOVE     | DOWN        |        0.9 |           -0.1375 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      183 | id08         | 2024-08-02     | hole     | Q2       | MOVE     | DOWN        |        0.9 |           -0.2302 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      184 | id08         | 2024-08-05     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.0952 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      185 | id08         | 2024-08-06     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.0952 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      189 | id08         | 2024-08-10     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.0952 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      193 | id08         | 2024-09-06     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.0952 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      194 | id08         | 2024-09-08     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.0952 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      196 | id08         | 2024-09-10     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.0952 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      197 | id08         | 2024-09-13     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.0952 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      198 | id08         | 2024-09-14     | hole     | Q2       | MOVE     | UP          |        0.9 |            0.0952 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      203 | id09         | 2024-08-07     | hole     | Q2       | MOVE     | DOWN        |        0.9 |           -0.1156 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      204 | id09         | 2024-08-08     | hole     | Q2       | MOVE     | DOWN        |        0.9 |           -0.1156 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      205 | id09         | 2024-08-09     | hole     | Q2       | MOVE     | DOWN        |        0.9 |           -0.1156 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|      210 | id09         | 2024-08-14     | hole     | Q2       | MOVE     | DOWN        |        0.9 |           -0.1156 | hole row with close labeled neighbor; prev/next Q2 agree; coverage/deviation anomaly present |
|        0 | id01         | 2024-07-30     | hole     | Q2       | MOVE     | UP          |        0.7 |            0.1537 | hole row with close labeled neighbor; prev/next Q2 agree                                     |
|        1 | id01         | 2024-07-31     | hole     | Q2       | MOVE     | UP          |        0.7 |            0.1537 | hole row with close labeled neighbor; prev/next Q2 agree                                     |
|        3 | id01         | 2024-08-02     | hole     | Q2       | MOVE     | UP          |        0.7 |            0.1537 | hole row with close labeled neighbor; prev/next Q2 agree                                     |
|        4 | id01         | 2024-08-03     | hole     | Q2       | MOVE     | UP          |        0.7 |            0.1537 | hole row with close labeled neighbor; prev/next Q2 agree                                     |


## Outputs

- `experiments/subject_profile_cards.csv`

- `experiments/test_regime_map.csv`

- `experiments/target_action_map.csv`
