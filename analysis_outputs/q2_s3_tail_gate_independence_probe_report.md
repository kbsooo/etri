# E68 Q2/S3 Tail-Gate Independence Probe

## Observe

E67 found a better Q2/S3 add-back rule, but that rule was still known-anchor-tail-derived and below margin.

## Wonder

If each combo set is held out from tail-gate construction, do the selected E67 Q2/S3 cells still beat matched `no_q2_s3` and survive non-anchor hidden/world/block stress?

## Method

- Selected E67 matched configs: `180`.
- Rebuilt unique predictions: `762` scored non-anchor, plus references.
- Matched held-out comparisons: `540`.
- For each held-out combo set, gates were rebuilt from the other combo sets only.
- Independent gate requires held-out beat, held-out worst-tail neutrality, hidden Q2/S3 improvement, non-worse world support, and hidden-block Q2/S3 majority beat.
- Strict gate additionally requires train-set beat, non-worse raw-energy p90, and hidden-block tail-safe rate at least `0.75`.

## Summary

| translator | pairs | heldout_beats_base | heldout_tail_neutral_beats | train_beats_base | hidden_q2s3_beats_base | world_nonworse | block_majority_beats | independent_gate | strict_independent_gate | best_heldout_minus_base | median_heldout_minus_base | best_heldout_set | best_block_win_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tail_soft_max_m1.00 | 69 | 46 | 44 | 69 | 69 | 69 | 69 | 44 | 44 | -6.6465e-07 | -3.61345e-07 | raw05_compatible | 0.944444 |
| tail_p90_nonpos_m1.00 | 222 | 141 | 141 | 222 | 222 | 222 | 118 | 41 | 41 | -1.26082e-06 | -4.0387e-07 | raw05_compatible | 0.861111 |
| tail_soft_p90_m1.00 | 75 | 50 | 34 | 75 | 75 | 75 | 75 | 34 | 34 | -6.54689e-07 | -2.74166e-07 | inverse_top | 0.944444 |
| tail_soft_p90_m0.50 | 39 | 26 | 19 | 39 | 39 | 39 | 39 | 19 | 19 | -3.40217e-07 | -1.68539e-07 | inverse_top | 0.944444 |
| tail_p90_nonpos_m0.50 | 75 | 48 | 48 | 75 | 75 | 75 | 43 | 17 | 17 | -7.54268e-07 | -3.84577e-07 | inverse_top | 0.861111 |
| tail_max_nonpos_m1.00 | 57 | 57 | 57 | 57 | 57 | 35 | 0 | 0 | 0 | -1.62959e-06 | -8.29077e-07 | raw05_compatible | 0.472222 |
| tail_max_nonpos_m0.50 | 3 | 3 | 3 | 3 | 3 | 3 | 0 | 0 | 0 | -7.75306e-07 | -6.24748e-07 | raw05_compatible | 0.388889 |

## Best Comparisons

| heldout_set | translator | heldout_minus_base | heldout_worst_minus_base | train_minus_base | world_support_minus_base | hidden_q2s3_mean_minus_base | block_q2s3_beats_base_rate | independent_gate | strict_independent_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| raw05_compatible | tail_p90_nonpos_m1.00 | -1.26082e-06 | -1.65349e-06 | -2.02044e-06 | -9.34742e-05 | -0.000109229 | 0.555556 | True | True |
| inverse_top | tail_p90_nonpos_m1.00 | -1.22192e-06 | -1.37878e-06 | -3.22488e-06 | -0.000108486 | -0.000107485 | 0.583333 | True | True |
| raw05_compatible | tail_p90_nonpos_m1.00 | -1.00792e-06 | -1.27905e-06 | -1.46213e-06 | -6.84274e-05 | -8.01305e-05 | 0.555556 | True | True |
| raw05_compatible | tail_p90_nonpos_m1.00 | -9.2865e-07 | -1.18221e-06 | -1.36294e-06 | -6.21477e-05 | -7.34636e-05 | 0.555556 | True | True |
| inverse_top | tail_p90_nonpos_m1.00 | -8.88987e-07 | -1.05885e-06 | -2.52841e-06 | -7.9433e-05 | -7.89477e-05 | 0.583333 | True | True |
| inverse_top | tail_p90_nonpos_m1.00 | -8.37429e-07 | -9.77102e-07 | -2.33342e-06 | -7.14294e-05 | -7.24552e-05 | 0.583333 | True | True |
| raw05_compatible | tail_p90_nonpos_m1.00 | -8.03057e-07 | -9.79646e-07 | -1.17177e-06 | -5.04829e-05 | -5.92062e-05 | 0.555556 | True | True |
| inverse_top | tail_p90_nonpos_m1.00 | -7.833e-07 | -8.40677e-07 | -1.90385e-06 | -7.60219e-05 | -7.03769e-05 | 0.583333 | True | True |
| inverse_top | tail_p90_nonpos_m0.50 | -7.54268e-07 | -7.5452e-07 | -1.80564e-06 | -5.42301e-05 | -5.42519e-05 | 0.583333 | True | True |
| raw05_compatible | tail_p90_nonpos_m0.50 | -7.51572e-07 | -9.16573e-07 | -1.11543e-06 | -4.68243e-05 | -5.50074e-05 | 0.555556 | True | True |
| raw05_compatible | tail_p90_nonpos_m1.00 | -7.3734e-07 | -8.95313e-07 | -1.0786e-06 | -4.5469e-05 | -5.38232e-05 | 0.555556 | True | True |
| inverse_top | tail_p90_nonpos_m1.00 | -7.14744e-07 | -8.0717e-07 | -1.91891e-06 | -5.8611e-05 | -5.8383e-05 | 0.583333 | True | True |
| raw05_compatible | tail_p90_nonpos_m1.00 | -6.75348e-07 | -9.3333e-07 | -1.24726e-06 | -6.94544e-05 | -7.43673e-05 | 0.555556 | True | True |
| inverse_top | tail_p90_nonpos_m1.00 | -6.67481e-07 | -7.36799e-07 | -1.72983e-06 | -5.22676e-05 | -5.31274e-05 | 0.583333 | True | True |
| raw05_compatible | tail_soft_max_m1.00 | -6.6465e-07 | -3.13491e-07 | -1.39219e-06 | -6.06414e-05 | -7.45648e-05 | 0.888889 | True | True |
| inverse_top | tail_p90_nonpos_m1.00 | -6.56446e-07 | -6.30985e-07 | -1.41168e-06 | -5.56125e-05 | -5.15797e-05 | 0.583333 | True | True |
| inverse_top | tail_soft_p90_m1.00 | -6.54689e-07 | -4.1574e-07 | -1.07813e-06 | -4.12578e-05 | -4.05141e-05 | 0.722222 | True | True |
| inverse_top | tail_soft_p90_m1.00 | -6.35001e-07 | -3.9135e-07 | -1.06217e-06 | -3.93772e-05 | -3.92353e-05 | 0.666667 | True | True |
| raw05_compatible | tail_soft_max_m1.00 | -6.28908e-07 | -1.52991e-07 | -1.31425e-06 | -5.9765e-05 | -7.27719e-05 | 0.861111 | True | True |
| inverse_top | tail_soft_max_m1.00 | -6.24887e-07 | -3.47267e-07 | -5.21635e-07 | -1.9434e-05 | -2.1555e-05 | 0.722222 | True | True |
| inverse_top | tail_soft_max_m1.00 | -6.16878e-07 | -3.22876e-07 | -5.20857e-07 | -1.86546e-05 | -2.11315e-05 | 0.666667 | True | True |
| inverse_top | tail_p90_nonpos_m1.00 | -6.09683e-07 | -5.79249e-07 | -1.3038e-06 | -5.07893e-05 | -4.72259e-05 | 0.583333 | True | True |
| raw05_compatible | tail_p90_nonpos_m0.50 | -5.68698e-07 | -6.87449e-07 | -7.6683e-07 | -3.42475e-05 | -4.0275e-05 | 0.555556 | True | True |
| raw05_compatible | tail_soft_max_m1.00 | -5.61617e-07 | -1.81769e-07 | -1.38485e-06 | -5.87015e-05 | -6.70815e-05 | 0.888889 | True | True |
| raw05_compatible | tail_p90_nonpos_m1.00 | -5.56193e-07 | -6.76214e-07 | -8.14247e-07 | -3.35315e-05 | -3.9732e-05 | 0.555556 | True | True |

## Decision

- Strict independent gates exist: `155`. Tail-gated Q2/S3 cells are no longer just an E67 anchor-tail artifact, but they still need selector-scale public margin before submission.
- No submission file is produced.

## Outputs

- `analysis_outputs/q2_s3_tail_gate_independence_probe_scan.csv`
- `analysis_outputs/q2_s3_tail_gate_independence_probe_pair.csv`
- `analysis_outputs/q2_s3_tail_gate_independence_probe_summary.csv`
