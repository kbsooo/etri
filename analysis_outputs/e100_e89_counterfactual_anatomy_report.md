# E100 E89 Counterfactual Anatomy

## Question

E99 made E89 the only unresolved nontrivial E95 counterfactual. This audit identifies which E95-conditioned tail worlds make E89 better than E95.

## Broad-Plausible Overview

Broad-plausible scenarios: `3452`. E89 beat-E95 rate: `0.195829`. E89 live win-rate: `0.188876`. E95 live win-rate: `0.800406`.
Mean E89-minus-E95 public delta: `0.000003833`. Mean E89 tail advantage over E95: `-0.000002109`. Mean required tail advantage: `0.000000755`.

## Case Split

| filter | case | n | share | mean_e89_minus_e95 | median_e89_minus_e95 | mean_tail_advantage | mean_needed_tail_advantage | mean_tail_surplus | alpha_median | lambda_median | selected_fractional_cells_mean | winner_mode | top_mask | top_order |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| broad_plausible | e89_beats_e95 | 676 | 0.195828505 | -0.000004251 | -0.000002637 | 0.000003737 | 0.000000821 | 0.000002916 | 3.985270401 | 1.415555032 | 20.386207304 | e89 | q2s3 | weighted_gamma_0.5_rep_055 |
| broad_plausible | e89_not_beats_e95 | 2776 | 0.804171495 | 0.000005802 | 0.000005191 | -0.000003533 | 0.000000739 | -0.000004272 | 3.150786018 | 1.328541066 | 23.683465330 | e95 | s1s2s3 | bottom |

## Top E89-Favorable Slices By Beat-Rate Lift

| slice_type | slice_value | n | share | e89_beat_rate | e89_win_rate | beat_rate_lift | mean_e89_minus_e95 | mean_tail_surplus | alpha_median | lambda_median |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| order_name | weighted_gamma_0.5_rep_055 | 7 | 0.002027810 | 0.857142857 | 0.857142857 | 0.661314352 | -0.000002026 | 0.000001673 | 2.472170115 | 1.257779931 |
| mask_name | q2s3 | 368 | 0.106604867 | 0.779891304 | 0.779891304 | 0.584062799 | -0.000005030 | 0.000003262 | 5.755757463 | 1.600168555 |
| family_mask | random_weighted / q2s3 | 367 | 0.106315180 | 0.779291553 | 0.779291553 | 0.583463048 | -0.000005036 | 0.000003265 | 5.768247608 | 1.601470936 |
| order_name | weighted_gamma_0.5_rep_022 | 8 | 0.002317497 | 0.625000000 | 0.625000000 | 0.429171495 | 0.000000406 | -0.000000092 | 3.905016581 | 1.407186747 |
| order_name | weighted_gamma_0.5_rep_024 | 8 | 0.002317497 | 0.625000000 | 0.625000000 | 0.429171495 | 0.000000502 | -0.000000205 | 2.446939406 | 1.255149057 |
| order_name | weighted_gamma_0.5_rep_117 | 7 | 0.002027810 | 0.571428571 | 0.571428571 | 0.375600066 | 0.000000011 | -0.000000042 | 2.339021682 | 1.243896181 |
| order_name | weighted_gamma_0.5_rep_059 | 8 | 0.002317497 | 0.500000000 | 0.500000000 | 0.304171495 | 0.000002525 | -0.000001664 | 3.133642885 | 1.326753504 |
| order_name | weighted_gamma_0.5_rep_063 | 8 | 0.002317497 | 0.500000000 | 0.500000000 | 0.304171495 | 0.000004239 | -0.000002940 | 1.898535659 | 1.197965500 |
| order_name | weighted_gamma_1_rep_000 | 8 | 0.002317497 | 0.500000000 | 0.500000000 | 0.304171495 | 0.000001084 | -0.000001086 | 2.424872366 | 1.252848066 |
| order_name | weighted_gamma_0.5_rep_095 | 6 | 0.001738123 | 0.500000000 | 0.500000000 | 0.304171495 | 0.000001409 | -0.000001391 | 2.011617996 | 1.209756904 |
| order_name | weighted_gamma_0_rep_073 | 6 | 0.001738123 | 0.500000000 | 0.500000000 | 0.304171495 | 0.000000724 | -0.000000672 | 1.785461349 | 1.186174933 |
| order_name | weighted_gamma_1_rep_076 | 6 | 0.001738123 | 0.500000000 | 0.500000000 | 0.304171495 | 0.000000931 | -0.000000331 | 3.547735744 | 1.369932098 |
| order_name | weighted_gamma_2_rep_038 | 6 | 0.001738123 | 0.500000000 | 0.500000000 | 0.304171495 | 0.000001629 | -0.000001282 | 5.417551325 | 1.564902877 |
| order_name | weighted_gamma_2_rep_075 | 6 | 0.001738123 | 0.500000000 | 0.500000000 | 0.304171495 | -0.000000781 | 0.000000429 | 4.817506630 | 1.502334577 |
| order_name | weighted_gamma_0.5_rep_001 | 7 | 0.002027810 | 0.428571429 | 0.428571429 | 0.232742923 | 0.000001108 | -0.000001479 | 1.130665416 | 1.117897572 |

## Top E89-Favorable Slices By Mean Delta

| slice_type | slice_value | n | share | e89_beat_rate | e89_win_rate | mean_e89_minus_e95 | p10_e89_minus_e95 | p90_e89_minus_e95 | mean_tail_surplus |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| family_mask | random_weighted / q2s3 | 367 | 0.106315180 | 0.779291553 | 0.779291553 | -0.000005036 | -0.000012158 | 0.000002065 | 0.000003265 |
| mask_name | q2s3 | 368 | 0.106604867 | 0.779891304 | 0.779891304 | -0.000005030 | -0.000012147 | 0.000002064 | 0.000003262 |
| order_name | weighted_gamma_0.5_rep_055 | 7 | 0.002027810 | 0.857142857 | 0.857142857 | -0.000002026 | -0.000005890 | 0.000003132 | 0.000001673 |
| order_name | weighted_gamma_0_rep_114 | 5 | 0.001448436 | 0.400000000 | 0.200000000 | -0.000002003 | -0.000013266 | 0.000005770 | 0.000001126 |
| order_name | weighted_gamma_0_rep_091 | 7 | 0.002027810 | 0.428571429 | 0.428571429 | -0.000000951 | -0.000010999 | 0.000007677 | 0.000000566 |
| order_name | weighted_gamma_2_rep_075 | 6 | 0.001738123 | 0.500000000 | 0.500000000 | -0.000000781 | -0.000004257 | 0.000003130 | 0.000000429 |
| order_name | weighted_gamma_0.5_rep_077 | 7 | 0.002027810 | 0.428571429 | 0.428571429 | -0.000000305 | -0.000008823 | 0.000007494 | -0.000000457 |
| order_name | weighted_gamma_0.5_rep_117 | 7 | 0.002027810 | 0.571428571 | 0.571428571 | 0.000000011 | -0.000004495 | 0.000006153 | -0.000000042 |
| order_name | weighted_gamma_0_rep_037 | 8 | 0.002317497 | 0.375000000 | 0.375000000 | 0.000000249 | -0.000007481 | 0.000007513 | -0.000000393 |
| order_name | weighted_gamma_0.5_rep_083 | 7 | 0.002027810 | 0.285714286 | 0.285714286 | 0.000000343 | -0.000006504 | 0.000005125 | -0.000000164 |
| order_name | weighted_gamma_0.5_rep_022 | 8 | 0.002317497 | 0.625000000 | 0.625000000 | 0.000000406 | -0.000006463 | 0.000010586 | -0.000000092 |
| order_name | weighted_gamma_0_rep_110 | 7 | 0.002027810 | 0.285714286 | 0.285714286 | 0.000000471 | -0.000007088 | 0.000007321 | -0.000000686 |
| order_name | weighted_gamma_0.5_rep_024 | 8 | 0.002317497 | 0.625000000 | 0.625000000 | 0.000000502 | -0.000006356 | 0.000008788 | -0.000000205 |
| order_name | weighted_gamma_0.5_rep_089 | 8 | 0.002317497 | 0.375000000 | 0.375000000 | 0.000000708 | -0.000006516 | 0.000005073 | -0.000000883 |
| order_name | weighted_gamma_0_rep_073 | 6 | 0.001738123 | 0.500000000 | 0.500000000 | 0.000000724 | -0.000003517 | 0.000004069 | -0.000000672 |

## Interpretation

E89 is not the mean-optimal file, but its win pocket is large enough to be the sharpest E95 counterfactual. A public E89 improvement would imply the public tail is closer to diffuse E72-cell fallback than to E95's selected hard-tail cells.
The decisive quantity is tail advantage surplus: E89 is locally slightly worse than E95, so it must gain enough E96-tail advantage to overcome that local disadvantage.

## Outputs

- Slice summary: `e100_e89_counterfactual_anatomy_slices.csv`
- Case summary: `e100_e89_counterfactual_anatomy_cases.csv`
