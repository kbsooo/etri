# E275 Q-Sleep Diary Energy Amplitude Audit

## Question

Is E274's near-promoted Q1/Q2/Q3 diary-energy movement robust across amplitude, or just a selector-threshold accident?

## Robustness Rule

A candidate is not submission-worthy unless at least two adjacent amplitude settings pass `strict_promote_gate`, the best p90 delta is <= `-0.000065`, and all strict settings beat current in at least `75%` of scenarios.

## Selector Reliability

- selected E272-style selector models: `1`
- strict ladder rows: `4`
- adjacent strict pass: `True`
- robust amplitude gate: `True`

## Ladder Scores

| basename | amp_mult | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e275_q_sleep_amp_m060_519b3f22.csv | 0.600000000 | too_small_to_submit | -0.000052634 | -0.000095066 | -0.000026136 | 0.941176471 | -0.001502918 |
| submission_e275_q_sleep_amp_m080_f6617ef0.csv | 0.800000000 | too_small_to_submit | -0.000074590 | -0.000134711 | -0.000037762 | 0.970588235 | -0.002003891 |
| submission_e275_q_sleep_amp_m100_8e391007.csv | 1.000000000 | too_small_to_submit | -0.000098347 | -0.000177534 | -0.000048780 | 0.970588235 | -0.002504864 |
| submission_e275_q_sleep_amp_m114_c3771d1c.csv | 1.150000000 | promote_candidate | -0.000118990 | -0.000214319 | -0.000057493 | 0.970588235 | -0.002880594 |
| submission_e275_q_sleep_amp_m130_27722489.csv | 1.300000000 | promote_candidate | -0.000141975 | -0.000251895 | -0.000064075 | 0.970588235 | -0.003256323 |
| submission_e275_q_sleep_amp_m145_3a3aff10.csv | 1.450000000 | promote_candidate | -0.000164916 | -0.000286859 | -0.000070089 | 0.970588235 | -0.003632053 |
| submission_e275_q_sleep_amp_m160_86528b2f.csv | 1.600000000 | promote_candidate | -0.000190473 | -0.000323817 | -0.000084726 | 0.970588235 | -0.004007782 |

## Movement Anatomy

| basename | changed_cells_vs_current | changed_rows_vs_current | l1_logit_delta_vs_current | max_abs_prob_delta_vs_current |
| --- | --- | --- | --- | --- |
| submission_e275_q_sleep_amp_m060_519b3f22.csv | 185 | 143 | 3.731903282 | 0.008247224 |
| submission_e275_q_sleep_amp_m080_f6617ef0.csv | 185 | 143 | 4.975871043 | 0.010994951 |
| submission_e275_q_sleep_amp_m100_8e391007.csv | 185 | 143 | 6.219838803 | 0.013741727 |
| submission_e275_q_sleep_amp_m114_c3771d1c.csv | 185 | 143 | 7.152814624 | 0.015801086 |
| submission_e275_q_sleep_amp_m130_27722489.csv | 185 | 143 | 8.085790444 | 0.017859747 |
| submission_e275_q_sleep_amp_m145_3a3aff10.csv | 185 | 143 | 9.018766265 | 0.019917641 |
| submission_e275_q_sleep_amp_m160_86528b2f.csv | 185 | 143 | 9.951742085 | 0.021974698 |

## Decision

`submission_e275_q_sleep_amp_m160_86528b2f.csv` is promoted by the E275 robustness rule, pending manual review of target/axis anatomy.

## Files

- `e275_q_sleep_diary_energy_amplitude_scan.csv`
- `e275_q_sleep_diary_energy_amplitude_scores.csv`
- `e275_q_sleep_diary_energy_amplitude_anatomy.csv`
- `e275_q_sleep_diary_energy_amplitude_cells.csv`
