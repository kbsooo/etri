# H058 Private-Tail Ejection HS-JEPA

## Question

Does the broad H012/H042 public-equation posterior contain private/noisy tail
cells outside the H042 Q2-support rows?

## Design

- base: H042 public frontier;
- historical anchor: E247;
- protected state: all targets on the `45` rows where H042 changed Q2 versus H012;
- eligible rollback cells: H042-vs-E247 support outside protected rows;
- target representation: H055 post-feedback public-listener posterior;
- action: roll back the lowest-listener tail cells from H042 toward E247 in logit space.

## Tail Geometry

- H042/E247 support cells: `1200`;
- eligible unprotected tail cells: `943`;
- protected H042 Q2-support rows: `45`;
- selected rollback cells: `500`;
- selected rollback rows: `197`;
- selected per-target cells: `{'Q1': 83, 'Q2': 42, 'Q3': 76, 'S1': 66, 'S2': 69, 'S3': 85, 'S4': 79}`;
- H055-posterior delta vs H042: `0.000175884`;
- protected-row changed cells: `0`;
- upload validation: `True`.

## Candidate Sweep

| candidate_id | rollback_k | alpha | changed_cells_vs_h042 | changed_rows_vs_h042 | protected_h042_q2row_changed_cells | h055_posterior_delta_vs_h042 |
| --- | --- | --- | --- | --- | --- | --- |
| h058_private_tail_eject_k120_a0p55_ae06dc80 | 120 | 0.550000000 | 120 | 95 | 0 | -0.000020193 |
| h058_private_tail_eject_k120_a0p75_afa97a30 | 120 | 0.750000000 | 120 | 95 | 0 | -0.000019084 |
| h058_private_tail_eject_k120_a0p85_a5012b04 | 120 | 0.850000000 | 120 | 95 | 0 | -0.000016831 |
| h058_private_tail_eject_k120_a1p0_3b53537d | 120 | 1.000000000 | 120 | 95 | 0 | -0.000011327 |
| h058_private_tail_eject_k240_a0p55_8fa65ab2 | 240 | 0.550000000 | 240 | 148 | 0 | 0.000006221 |
| h058_private_tail_eject_k240_a0p75_5bc5126b | 240 | 0.750000000 | 240 | 148 | 0 | 0.000025276 |
| h058_private_tail_eject_k240_a0p85_12ca986d | 240 | 0.850000000 | 240 | 148 | 0 | 0.000038164 |
| h058_private_tail_eject_k240_a1p0_0aeaf0d9 | 240 | 1.000000000 | 240 | 148 | 0 | 0.000061700 |
| h058_private_tail_eject_k360_a0p55_baa131f0 | 360 | 0.550000000 | 360 | 177 | 0 | 0.000062881 |
| h058_private_tail_eject_k360_a0p75_b7809181 | 360 | 0.750000000 | 360 | 177 | 0 | 0.000115125 |
| h058_private_tail_eject_k360_a0p85_dfe0ca0a | 360 | 0.850000000 | 360 | 177 | 0 | 0.000147139 |
| h058_private_tail_eject_k360_a1p0_4d094f0e | 360 | 1.000000000 | 360 | 177 | 0 | 0.000202537 |
| h058_private_tail_eject_k500_a0p55_138bba8f | 500 | 0.550000000 | 500 | 197 | 0 | 0.000175884 |
| h058_private_tail_eject_k500_a0p75_14dcf867 | 500 | 0.750000000 | 500 | 197 | 0 | 0.000289816 |
| h058_private_tail_eject_k500_a0p85_5bf05a14 | 500 | 0.850000000 | 500 | 197 | 0 | 0.000356808 |
| h058_private_tail_eject_k500_a1p0_2ae341b8 | 500 | 1.000000000 | 500 | 197 | 0 | 0.000469845 |
| h058_private_tail_eject_k650_a0p55_3fab1717 | 650 | 0.550000000 | 650 | 203 | 0 | 0.000389593 |
| h058_private_tail_eject_k650_a0p75_d6bf8794 | 650 | 0.750000000 | 650 | 203 | 0 | 0.000619700 |
| h058_private_tail_eject_k650_a0p85_ebc2e41b | 650 | 0.850000000 | 650 | 203 | 0 | 0.000752548 |
| h058_private_tail_eject_k650_a1p0_5764d8d8 | 650 | 1.000000000 | 650 | 203 | 0 | 0.000974134 |
| h058_private_tail_eject_k800_a0p55_b1bbe862 | 800 | 0.550000000 | 800 | 205 | 0 | 0.000788115 |
| h058_private_tail_eject_k800_a0p75_e1fd2dd1 | 800 | 0.750000000 | 800 | 205 | 0 | 0.001232181 |
| h058_private_tail_eject_k800_a0p85_9f40f41c | 800 | 0.850000000 | 800 | 205 | 0 | 0.001487006 |
| h058_private_tail_eject_k800_a1p0_dd30ff65 | 800 | 1.000000000 | 800 | 205 | 0 | 0.001913470 |
| h058_private_tail_eject_k943_a0p55_1853ea5b | 943 | 0.550000000 | 943 | 205 | 0 | 0.001801458 |
| h058_private_tail_eject_k943_a0p75_c790a3ed | 943 | 0.750000000 | 943 | 205 | 0 | 0.002937749 |
| h058_private_tail_eject_k943_a0p85_e129dc83 | 943 | 0.850000000 | 943 | 205 | 0 | 0.003716732 |
| h058_private_tail_eject_k943_a1p0_e41dad87 | 943 | 1.000000000 | 943 | 205 | 0 | 0.005489353 |

## Promoted Submission

`submission_h058_private_tail_eject_138bba8f_uploadsafe.csv`

## Interpretation

If this improves over H042/H050, the current HS-JEPA bottleneck is not another
target route; it is public/private tail separation inside the broad H012/H042
posterior. If it fails, the broad H012/H042 posterior outside H042 rows should
not be collapsed using H055 low-listener score alone.
