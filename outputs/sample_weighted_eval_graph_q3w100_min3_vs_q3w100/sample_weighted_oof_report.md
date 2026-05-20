# Sample-weighted OOF diagnostics

- Baseline: `q3w100`
- Weights match train rows to the submission sample panel-position distribution.

## Position bins

| bin | train_frac | sample_frac | weight_ratio |
| --- | --- | --- | --- |
| [0.000,0.333) | 0.520000 | 0.000000 | 0.000000 |
| [0.333,0.667) | 0.226667 | 0.520000 | 2.294118 |
| [0.667,0.800) | 0.204444 | 0.000000 | 0.000000 |
| [0.800,1.000) | 0.048889 | 0.480000 | 9.818182 |

## Candidate summary

| name | uniform_avg_log_loss | weighted_avg_log_loss | weighted_delta_vs_baseline | weighted_p025 | weighted_p500 | weighted_p975 | promote_weighted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| q3w100 | 0.575682 | 0.544735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| graph_q3w100_min3 | 0.575567 | 0.544997 | -0.000262 | -0.000893 | -0.000262 | 0.000366 | False |

## Target scores

| name | target | uniform_log_loss | weighted_log_loss | weighted_delta_vs_baseline |
| --- | --- | --- | --- | --- |
| q3w100 | Q1 | 0.632767 | 0.617350 | 0.000000 |
| q3w100 | Q2 | 0.631830 | 0.582987 | 0.000000 |
| q3w100 | Q3 | 0.607743 | 0.510501 | 0.000000 |
| q3w100 | S1 | 0.552444 | 0.568887 | 0.000000 |
| q3w100 | S2 | 0.524347 | 0.500922 | 0.000000 |
| q3w100 | S3 | 0.494675 | 0.453861 | 0.000000 |
| q3w100 | S4 | 0.585965 | 0.578635 | 0.000000 |
| graph_q3w100_min3 | Q1 | 0.632767 | 0.617350 | 0.000000 |
| graph_q3w100_min3 | Q2 | 0.631830 | 0.582987 | 0.000000 |
| graph_q3w100_min3 | Q3 | 0.607743 | 0.510501 | 0.000000 |
| graph_q3w100_min3 | S1 | 0.552366 | 0.566760 | 0.002126 |
| graph_q3w100_min3 | S2 | 0.524347 | 0.500922 | 0.000000 |
| graph_q3w100_min3 | S3 | 0.494506 | 0.452609 | 0.001252 |
| graph_q3w100_min3 | S4 | 0.585411 | 0.583847 | -0.005212 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| q3w100 | mid | 100 | 0.000000 |
| q3w100 | late | 116 | 0.000000 |
| q3w100 | tail_20pct | 22 | 0.000000 |
| graph_q3w100_min3 | mid | 100 | -0.000381 |
| graph_q3w100_min3 | late | 116 | 0.000996 |
| graph_q3w100_min3 | tail_20pct | 22 | -0.000159 |
