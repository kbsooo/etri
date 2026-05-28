# E37 Inverse7 Raw-Anchor Bridge Scale Scan

## Observe

E36 split the probe family: mixmin is stronger under anchor-loss/binary-world geometry, while inverse7 is stronger under train-derived raw observed structure.

## Wonder

Can a scaled inverse7 or inverse7/mixmin blend preserve raw-structure support and anchor-loss support while reducing the pairwise/old selector veto?

## Hypothesis

H36: inverse7 is a bridge direction between raw observed structure and anchor-loss worlds. If true, some scale/blend variant should keep raw pseudo-label support, keep low-anchor-energy binary-world support, and have weaker selector veto than the original inverse7/mixmin files. If false, raw support and anchor-loss support remain separated by selector conflict.

## Method

- Generated logit-space variants from A2C8 toward inverse7, mixmin, and inverse7/mixmin blended directions.
- Scored all variants against the same 10 raw-structure pseudo-label sources from E36.
- Scored all variants against E32 binary anchor-loss worlds and low-energy bands.
- Scored all variants with the old hidden-subset selector and the pairwise public-order selector.

## Result

- variants scanned: `22`.
- raw support gates: `14`.
- anchor low-half+quarter gates: `22`.
- two-selector majority variants: `0`.
- strict bridge gates: `0`.

## Top Variants

| role | family | scale | mix_weight | support_rate | raw_mean_delta | raw_worst_delta | anchor_low_anchor_energy_half_better_rate | anchor_low_anchor_energy_half_max_delta | anchor_low_anchor_energy_quarter_better_rate | pair_delta_vs_a2c8_p90 | pair_beats_a2c8_rate | selector_p90_delta_vs_a2c8_public | beats_a2c8_scenario_rate | bad_axis_abs_load | two_selector_majority | selector_hard_veto | bridge_gate | bridge_rank_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inv7_s0p25 | pure_inv7 | 0.25 | 0 | 1 | -0.000181991 | -0.000132515 | 1 | -1.17136e-05 | 1 | 3.54231e-05 | 0.0621622 | 0.000587512 | 0.00772201 | 0.0400513 | False | True | False | -0.000498935 | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv |
| inv7_s0p50 | pure_inv7 | 0.5 | 0 | 1 | -0.000360277 | -0.000261326 | 1 | -1.97224e-05 | 1 | 6.43721e-05 | 0.0567568 | 0.000607068 | 0.00772201 | 0.0431968 | False | True | False | -0.000462355 | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p50.csv |
| inv7_s0p75 | pure_inv7 | 0.75 | 0 | 1 | -0.000534856 | -0.00038643 | 1 | -2.40246e-05 | 1 | 9.4018e-05 | 0.0513514 | 0.000611414 | 0.003861 | 0.0478267 | False | True | False | -0.000430031 | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p75.csv |
| inv7_s1p00 | pure_inv7 | 1 | 0 | 1 | -0.000705727 | -0.000507826 | 1 | -2.46186e-05 | 1 | 0.000122038 | 0.0459459 | 0.000617292 | 0.003861 | 0.0524804 | False | True | False | -0.00039879 | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s1p00.csv |
| blend_m0p25_s0p50 | inv7_mixmin_blend | 0.5 | 0.25 | 1 | -0.000289936 | -0.000168217 | 1 | -0.000111161 | 1 | 0.000116208 | 0.027027 | 0.000640247 | 0.003861 | 0.0602971 | False | True | False | -0.000394631 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p25_s0p50.csv |
| inv7_s1p25 | pure_inv7 | 1.25 | 0 | 1 | -0.000872888 | -0.000625512 | 1 | -2.15027e-05 | 1 | 0.000151016 | 0.0378378 | 0.000628025 | 0.003861 | 0.0571342 | False | True | False | -0.000364892 | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s1p25.csv |
| inv7_s1p50 | pure_inv7 | 1.5 | 0 | 1 | -0.00103634 | -0.000739486 | 1 | -1.46753e-05 | 1 | 0.000180513 | 0.0378378 | 0.00065111 | 0.003861 | 0.0617879 | False | True | False | -0.000326152 | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s1p50.csv |
| blend_m0p25_s0p75 | inv7_mixmin_blend | 0.75 | 0.25 | 1 | -0.000424337 | -0.000241758 | 1 | -0.000156175 | 1 | 0.000171414 | 0.0162162 | 0.000679863 | 0.003861 | 0.0743984 | False | True | False | -0.000322035 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p25_s0p75.csv |
| blend_m0p50_s0p50 | inv7_mixmin_blend | 0.5 | 0.5 | 1 | -0.000213141 | -6.86529e-05 | 1 | -0.000196145 | 1 | 0.00021843 | 0.0135135 | 0.000677366 | 0.003861 | 0.0791922 | False | True | False | -0.000274694 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s0p50.csv |
| blend_m0p25_s1p00 | inv7_mixmin_blend | 1 | 0.25 | 1 | -0.000551692 | -0.000308253 | 1 | -0.000194141 | 1 | 0.000226558 | 0.0135135 | 0.000696657 | 0.003861 | 0.0884997 | False | True | False | -0.000257487 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p25_s1p00.csv |
| blend_m0p25_s1p25 | inv7_mixmin_blend | 1.25 | 0.25 | 1 | -0.000671997 | -0.000367698 | 1 | -0.000225059 | 1 | 0.000279825 | 0.0135135 | 0.000736258 | 0.003861 | 0.102601 | False | True | False | -0.000186835 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p25_s1p25.csv |
| blend_m0p50_s0p75 | inv7_mixmin_blend | 0.75 | 0.5 | 1 | -0.000299299 | -8.25669e-05 | 1 | -0.000273805 | 1 | 0.000323816 | 0.00540541 | 0.000729006 | 0.003861 | 0.102741 | False | True | False | -0.000145347 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s0p75.csv |
| blend_m0p50_s1p00 | inv7_mixmin_blend | 1 | 0.5 | 1 | -0.000371848 | -8.28716e-05 | 1 | -0.000337856 | 1 | 0.000432363 | 0.0027027 | 0.000801849 | 0.003861 | 0.12629 | False | True | False | -5.41755e-06 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s1p00.csv |
| blend_m0p50_s1p25 | inv7_mixmin_blend | 1.25 | 0.5 | 1 | -0.000430788 | -6.95671e-05 | 1 | -0.000388298 | 1 | 0.000539786 | 0 | 0.0008796 | 0.003861 | 0.149839 | False | True | False | 0.000135105 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s1p25.csv |
| mixmin_s0p25 | pure_mixmin | 0.25 | 1 | 0.5 | -3.83052e-05 | 7.00617e-05 | 1 | -0.000188856 | 1 | 0.00021635 | 0.0135135 | 0.000660578 | 0.00772201 | 0.0745384 | False | True | False | -8.38135e-05 | analysis_outputs/bridge_scan_candidates/submission_bridge_mixmin_s0p25.csv |
| blend_m0p75_s0p50 | inv7_mixmin_blend | 0.5 | 0.75 | 0.6 | -0.000129897 | 3.73601e-05 | 1 | -0.00027468 | 1 | 0.000324707 | 0.00540541 | 0.000719318 | 0.00772201 | 0.0980872 | False | True | False | 1.09906e-05 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s0p50.csv |
| mixmin_s0p50 | pure_mixmin | 0.5 | 1 | 0.5 | -4.02082e-05 | 0.000176526 | 1 | -0.00034131 | 1 | 0.000431661 | 0.0027027 | 0.000763773 | 0.00772201 | 0.116982 | False | True | False | 0.000178227 | analysis_outputs/bridge_scan_candidates/submission_bridge_mixmin_s0p50.csv |
| blend_m0p75_s0p75 | inv7_mixmin_blend | 0.75 | 0.75 | 0.5 | -0.000159758 | 9.11277e-05 | 1 | -0.000376933 | 1 | 0.000486586 | 0 | 0.000806156 | 0.00772201 | 0.131083 | False | True | False | 0.000251512 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s0p75.csv |

## Decision

No variant resolves the full bridge gate. Best-ranked diagnostic is `analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv`, but it remains a sensor, not a certified improvement. This means E36's inverse7 support and E32/E33's mixmin anchor support are still not reconciled locally.

## Outputs

- `analysis_outputs/inverse7_raw_anchor_bridge_scale_scan_scores.csv`
- `analysis_outputs/inverse7_raw_anchor_bridge_scale_scan_raw_scores.csv`
- `analysis_outputs/inverse7_raw_anchor_bridge_scale_scan_anchor_bands.csv`
- `analysis_outputs/inverse7_raw_anchor_bridge_scale_scan_selector_scores.csv`
