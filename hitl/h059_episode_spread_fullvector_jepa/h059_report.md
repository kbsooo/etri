# H059 Episode-Spread Full-Vector HS-JEPA

## Question

Are H042/H057's public-positive rows isolated events, or visible markers of a
same-subject lifestyle episode that spills into nearby days?

## Design

- base: H057 public frontier (`0.5677475939`);
- anchor rows: the `45` H042 Q2-support rows;
- protected behavior: leave anchor rows exactly as H057 and freeze Q2
  everywhere;
- target representation: H055 post-feedback public-listener posterior;
- action: decode Q1/Q3/S1-S4 on same-subject neighbor rows around the anchor;
- promoted mask: same-subject position radius `3`;
- promoted alpha: `1.10` with distance decay `1.0/0.55/0.35` for distance
  `1/2/3`.

## Candidate Sweep

| candidate_id | row_mask | family | alpha | changed_cells_vs_h057 | changed_rows_vs_h057 | changed_cells_vs_h042 | posterior_delta_vs_h057 | dist1_rows | dist2_rows | dist3_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h059_episode_pos_r3_full_nonq2_a1p1_cb67de4b | pos_r3 | full_nonq2 | 1.100000000 | 822 | 137 | 1092 | -0.000456867 | 62 | 43 | 32 |
| h059_episode_pos_r3_full_nonq2_a0p9_d1922b49 | pos_r3 | full_nonq2 | 0.900000000 | 822 | 137 | 1092 | -0.000428297 | 62 | 43 | 32 |
| h059_episode_pos_r3_q3s_a1p1_2eb6cb4d | pos_r3 | q3s | 1.100000000 | 685 | 137 | 955 | -0.000397589 | 62 | 43 | 32 |
| h059_episode_pos_r3_full_nonq2_a0p75_e501e5f7 | pos_r3 | full_nonq2 | 0.750000000 | 822 | 137 | 1092 | -0.000391386 | 62 | 43 | 32 |
| h059_episode_pos_r3_q1s_a1p1_d37b1c08 | pos_r3 | q1s | 1.100000000 | 685 | 137 | 955 | -0.000376661 | 62 | 43 | 32 |
| h059_episode_pos_r2_full_nonq2_a1p1_5a98916a | pos_r2 | full_nonq2 | 1.100000000 | 630 | 105 | 900 | -0.000374093 | 62 | 43 | 0 |
| h059_episode_pos_r3_q3s_a0p9_c14382e2 | pos_r3 | q3s | 0.900000000 | 685 | 137 | 955 | -0.000373255 | 62 | 43 | 32 |
| h059_episode_pos_r2_full_nonq2_a0p9_ec341f23 | pos_r2 | full_nonq2 | 0.900000000 | 630 | 105 | 900 | -0.000357565 | 62 | 43 | 0 |
| h059_episode_pos_r3_q1s_a0p9_20a54cc0 | pos_r3 | q1s | 0.900000000 | 685 | 137 | 955 | -0.000352436 | 62 | 43 | 32 |
| h059_episode_pos_r3_q3s_a0p75_677c0f4f | pos_r3 | q3s | 0.750000000 | 685 | 137 | 955 | -0.000341419 | 62 | 43 | 32 |
| h059_episode_pos_r3_full_nonq2_a0p6_e3101f07 | pos_r3 | full_nonq2 | 0.600000000 | 822 | 137 | 1092 | -0.000340988 | 62 | 43 | 32 |
| h059_episode_pos_r2_q3s_a1p1_5a6fb091 | pos_r2 | q3s | 1.100000000 | 525 | 105 | 795 | -0.000330985 | 62 | 43 | 0 |
| h059_episode_pos_r2_full_nonq2_a0p75_6d6c27ba | pos_r2 | full_nonq2 | 0.750000000 | 630 | 105 | 900 | -0.000330557 | 62 | 43 | 0 |
| h059_episode_pos_r3_q1s_a0p75_377627ab | pos_r3 | q1s | 0.750000000 | 685 | 137 | 955 | -0.000321735 | 62 | 43 | 32 |
| h059_episode_pos_r3_s_all_a1p1_a595db82 | pos_r3 | s_all | 1.100000000 | 548 | 137 | 818 | -0.000317382 | 62 | 43 | 32 |
| h059_episode_pos_r2_q3s_a0p9_29f1cd56 | pos_r2 | q3s | 0.900000000 | 525 | 105 | 795 | -0.000316337 | 62 | 43 | 0 |
| h059_episode_date_d2_full_nonq2_a1p1_369943d3 | date_d2 | full_nonq2 | 1.100000000 | 504 | 84 | 774 | -0.000304583 | 56 | 28 | 0 |
| h059_episode_pos_r2_q1s_a1p1_5f7e38f7 | pos_r2 | q1s | 1.100000000 | 525 | 105 | 795 | -0.000302861 | 62 | 43 | 0 |
| h059_episode_pos_r3_q3s_a0p6_a7e0ecff | pos_r3 | q3s | 0.600000000 | 685 | 137 | 955 | -0.000297728 | 62 | 43 | 32 |
| h059_episode_pos_r3_s_all_a0p9_ee3d0b3f | pos_r3 | s_all | 0.900000000 | 548 | 137 | 818 | -0.000297394 | 62 | 43 | 32 |
| h059_episode_date_d2_full_nonq2_a0p9_8df395be | date_d2 | full_nonq2 | 0.900000000 | 504 | 84 | 774 | -0.000293971 | 56 | 28 | 0 |
| h059_episode_pos_r2_q3s_a0p75_68518bf6 | pos_r2 | q3s | 0.750000000 | 525 | 105 | 795 | -0.000292466 | 62 | 43 | 0 |
| h059_episode_pos_r2_full_nonq2_a0p6_d5a9d5ca | pos_r2 | full_nonq2 | 0.600000000 | 630 | 105 | 900 | -0.000290812 | 62 | 43 | 0 |
| h059_episode_pos_r2_q1s_a0p9_ed551194 | pos_r2 | q1s | 0.900000000 | 525 | 105 | 795 | -0.000289365 | 62 | 43 | 0 |
| h059_episode_pos_r3_q1s_a0p6_a856f58b | pos_r3 | q1s | 0.600000000 | 685 | 137 | 955 | -0.000280097 | 62 | 43 | 32 |
| h059_episode_pos_r3_full_nonq2_a0p45_bae69228 | pos_r3 | full_nonq2 | 0.450000000 | 822 | 137 | 1092 | -0.000276891 | 62 | 43 | 32 |
| h059_episode_date_d2_full_nonq2_a0p75_64ebb102 | date_d2 | full_nonq2 | 0.750000000 | 504 | 84 | 774 | -0.000273309 | 56 | 28 | 0 |
| h059_episode_pos_r3_s_all_a0p75_f6d0d432 | pos_r3 | s_all | 0.750000000 | 548 | 137 | 818 | -0.000271768 | 62 | 43 | 32 |
| h059_episode_date_d2_q3s_a1p1_0e3e0e42 | date_d2 | q3s | 1.100000000 | 420 | 84 | 690 | -0.000270857 | 56 | 28 | 0 |
| h059_episode_pos_r2_q1s_a0p75_776e2af5 | pos_r2 | q1s | 0.750000000 | 525 | 105 | 795 | -0.000267490 | 62 | 43 | 0 |

## Promoted Candidate

`submission_h059_episode_r3_fullvector_cb67de4b_uploadsafe.csv`

## Anatomy

- anchor rows: `45`;
- selected added rows vs H057: `137`;
- selected added cells vs H057: `822`;
- total changed cells vs H042: `1092`;
- Q2 changed vs H057: `0`;
- distance rows: d1 `62`, d2 `43`, d3 `32`;
- posterior delta vs H057: `-0.000456867`;
- upload validation: `True`.

## Public Interpretation

If H059 improves over H057, HS-JEPA should model hidden human state as a
same-subject temporal episode, not a single-row marker. If H059 fails, H057's
45 anchor rows are likely a precise public-positive support and episode spread
should be killed or made much more selective.
