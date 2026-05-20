# Sample-weighted OOF diagnostics

- Baseline: `hgb_tail_decoder_v8`
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
| v12_final | 0.576672 | 0.558987 | 0.009187 | 0.006125 | 0.009185 | 0.012432 | True |
| v12_step3_s2q2q3 | 0.576763 | 0.559878 | 0.008296 | 0.005242 | 0.008294 | 0.011570 | True |
| v12_step2_s2q2 | 0.577413 | 0.561370 | 0.006804 | 0.003836 | 0.006807 | 0.009902 | True |
| v12_step1_s2 | 0.577690 | 0.564088 | 0.004086 | 0.001988 | 0.004072 | 0.006335 | True |
| hgb_tail_decoder_v8 | 0.578106 | 0.568174 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target scores

| name | target | uniform_log_loss | weighted_log_loss | weighted_delta_vs_baseline |
| --- | --- | --- | --- | --- |
| hgb_tail_decoder_v8 | Q1 | 0.632767 | 0.617350 | 0.000000 |
| hgb_tail_decoder_v8 | Q2 | 0.635787 | 0.621843 | 0.000000 |
| hgb_tail_decoder_v8 | Q3 | 0.608771 | 0.520594 | 0.000000 |
| hgb_tail_decoder_v8 | S1 | 0.552632 | 0.570736 | 0.000000 |
| hgb_tail_decoder_v8 | S2 | 0.527620 | 0.531631 | 0.000000 |
| hgb_tail_decoder_v8 | S3 | 0.497139 | 0.476906 | 0.000000 |
| hgb_tail_decoder_v8 | S4 | 0.592027 | 0.638157 | 0.000000 |
| v12_step1_s2 | Q1 | 0.632767 | 0.617350 | 0.000000 |
| v12_step1_s2 | Q2 | 0.635787 | 0.621843 | 0.000000 |
| v12_step1_s2 | Q3 | 0.608771 | 0.520594 | 0.000000 |
| v12_step1_s2 | S1 | 0.552632 | 0.570736 | 0.000000 |
| v12_step1_s2 | S2 | 0.524707 | 0.503027 | 0.028603 |
| v12_step1_s2 | S3 | 0.497139 | 0.476906 | 0.000000 |
| v12_step1_s2 | S4 | 0.592027 | 0.638157 | 0.000000 |
| v12_step2_s2q2 | Q1 | 0.632767 | 0.617350 | 0.000000 |
| v12_step2_s2q2 | Q2 | 0.633849 | 0.602819 | 0.019025 |
| v12_step2_s2q2 | Q3 | 0.608771 | 0.520594 | 0.000000 |
| v12_step2_s2q2 | S1 | 0.552632 | 0.570736 | 0.000000 |
| v12_step2_s2q2 | S2 | 0.524707 | 0.503027 | 0.028603 |
| v12_step2_s2q2 | S3 | 0.497139 | 0.476906 | 0.000000 |
| v12_step2_s2q2 | S4 | 0.592027 | 0.638157 | 0.000000 |
| v12_step3_s2q2q3 | Q1 | 0.632767 | 0.617350 | 0.000000 |
| v12_step3_s2q2q3 | Q2 | 0.633849 | 0.602819 | 0.019025 |
| v12_step3_s2q2q3 | Q3 | 0.604219 | 0.510149 | 0.010444 |
| v12_step3_s2q2q3 | S1 | 0.552632 | 0.570736 | 0.000000 |
| v12_step3_s2q2q3 | S2 | 0.524707 | 0.503027 | 0.028603 |
| v12_step3_s2q2q3 | S3 | 0.497139 | 0.476906 | 0.000000 |
| v12_step3_s2q2q3 | S4 | 0.592027 | 0.638157 | 0.000000 |
| v12_final | Q1 | 0.632767 | 0.617350 | 0.000000 |
| v12_final | Q2 | 0.633849 | 0.602819 | 0.019025 |
| v12_final | Q3 | 0.604219 | 0.510149 | 0.010444 |
| v12_final | S1 | 0.552632 | 0.570736 | 0.000000 |
| v12_final | S2 | 0.524707 | 0.503027 | 0.028603 |
| v12_final | S3 | 0.497139 | 0.476906 | 0.000000 |
| v12_final | S4 | 0.591392 | 0.631920 | 0.006237 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| hgb_tail_decoder_v8 | mid | 100 | 0.000000 |
| hgb_tail_decoder_v8 | late | 116 | 0.000000 |
| hgb_tail_decoder_v8 | tail_20pct | 22 | 0.000000 |
| v12_step1_s2 | mid | 100 | 0.000000 |
| v12_step1_s2 | late | 116 | 0.001615 |
| v12_step1_s2 | tail_20pct | 22 | 0.008513 |
| v12_step2_s2q2 | mid | 100 | 0.000000 |
| v12_step2_s2q2 | late | 116 | 0.002688 |
| v12_step2_s2q2 | tail_20pct | 22 | 0.014175 |
| v12_step3_s2q2q3 | mid | 100 | 0.002783 |
| v12_step3_s2q2q3 | late | 116 | 0.002813 |
| v12_step3_s2q2q3 | tail_20pct | 22 | 0.014175 |
| v12_final | mid | 100 | 0.002783 |
| v12_final | late | 116 | 0.003165 |
| v12_final | tail_20pct | 22 | 0.016031 |
