# E125 E101 survivor anatomy

## Question

E124 left only `57` E101-plausible worlds out of `3452` broad-plausible
E99 worlds. If the old Q2/S3 diffuse-tail story is still the residual law,
the survivor set should be enriched for the `q2s3` mask. If the survivor set is
instead broad/all-tail and transfer-shrunk, the same-family line is not missing
only a better Q2/S3 selector.

## Key Observations

- E101-plausible survival rate: `0.016512`.
- `all` or `e72_top50_hard` masks account for `43/57` survivors.
- `q2s3` mask has `0/368` survivors.
- deterministic or `gamma=0` worlds account for `40/57` survivors.
- Broad median alpha is `3.310470`; E101-plausible median alpha is `0.791985`.
- Broad median `tail_e101 - tail_e95` is `-0.000012634`; E101-plausible median is `-0.000000000`.

## Category Enrichment

| category | value | broad_count | e101_count | e101_rate | enrichment_vs_base | pred_vs_e95_e101_mean |
| --- | --- | --- | --- | --- | --- | --- |
| e101_tail_relation | tail_equal | 37 | 37 | 1.000000 | 60.561404 | 0.000001 |
| gamma_group | gamma_0 | 870 | 35 | 0.040230 | 2.436378 | -0.000010 |
| mask_name | all | 475 | 23 | 0.048421 | 2.932447 | -0.000010 |
| alpha_group | alpha_0p5_1 | 249 | 22 | 0.088353 | 5.350807 | -0.000004 |
| mask_name | e72_top50_hard | 475 | 20 | 0.042105 | 2.549954 | -0.000011 |
| e101_tail_relation | e101_lower_tail_than_e95 | 3415 | 20 | 0.005857 | 0.354679 | -0.000016 |
| alpha_group | alpha_1_2 | 662 | 15 | 0.022659 | 1.372237 | -0.000007 |
| alpha_group | alpha_le_0p5 | 124 | 13 | 0.104839 | 6.349179 | -0.000003 |
| gamma_group | gamma_0.5 | 902 | 11 | 0.012195 | 0.738554 | -0.000013 |
| alpha_group | alpha_2_4 | 1028 | 6 | 0.005837 | 0.353471 | -0.000013 |
| gamma_group | deterministic | 28 | 5 | 0.178571 | 10.814536 | -0.000004 |
| gamma_group | gamma_1 | 908 | 5 | 0.005507 | 0.333488 | -0.000017 |
| mask_name | s1 | 3 | 3 | 1.000000 | 60.561404 | 0.000002 |
| mask_name | e95_fallback_cells | 324 | 2 | 0.006173 | 0.373836 | -0.000020 |
| mask_name | s1s2s3 | 435 | 2 | 0.004598 | 0.278443 | -0.000018 |
| mask_name | e95_moved_vs_mixmin | 441 | 2 | 0.004535 | 0.274655 | -0.000018 |
| mask_name | e86_moved_vs_mixmin | 454 | 2 | 0.004405 | 0.266790 | -0.000014 |
| mask_name | s2 | 1 | 1 | 1.000000 | 60.561404 | 0.000001 |

## Numeric Contrast

| metric | broad_mean | broad_median | e101_mean | e101_median | mean_shift | median_shift | std_shift |
| --- | --- | --- | --- | --- | --- | --- | --- |
| alpha | 3.578745595 | 3.310469910 | 1.119205927 | 0.791985050 | -2.459539668 | -2.518484860 | -1.153245770 |
| lambda | 1.373165580 | 1.345191741 | 1.116702660 | 1.082582445 | -0.256462920 | -0.262609297 | -1.153245770 |
| selected_full_cells | 22.540266512 | 20.000000000 | 33.228070175 | 30.000000000 | 10.687803663 | 10.000000000 | 0.970282103 |
| tail_e101 | 0.000039057 | 0.000039864 | 0.000010320 | 0.000005030 | -0.000028737 | -0.000034834 | -1.105453537 |
| tail_e95 | 0.000052077 | 0.000053114 | 0.000010595 | 0.000005030 | -0.000041482 | -0.000048084 | -1.309137253 |
| pred_vs_e95_e101 | -0.000016205 | -0.000014288 | 0.000000592 | 0.000000466 | 0.000016798 | 0.000014755 | 1.548186969 |
| tail_e101_minus_e95 | -0.000013020 | -0.000012634 | -0.000000274 | -0.000000000 | 0.000012745 | 0.000012634 |  |

## Mask Contrast

| mask_name | broad_count | e101_count | e101_rate | order_match_rate | close10_rate | pred_vs_e95_e101_mean | tail_e101_minus_e95_mean | alpha_median | selected_full_median |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | 475 | 23 | 0.048421053 | 0.048421053 | 0.113684211 | -0.000009771 | -0.000008648 | 1.846849638 | 26.000000000 |
| e72_top50_hard | 475 | 20 | 0.042105263 | 0.042105263 | 0.061052632 | -0.000010639 | -0.000009351 | 2.049492201 | 21.000000000 |
| e95_fallback_cells | 324 | 2 | 0.006172840 | 0.006172840 | 0.012345679 | -0.000019940 | -0.000015025 | 6.507152040 | 16.000000000 |
| s1s2s3 | 435 | 2 | 0.004597701 | 0.004597701 | 0.013793103 | -0.000017621 | -0.000014159 | 3.293049683 | 25.000000000 |
| live_q2s1s2s3 | 465 | 1 | 0.002150538 | 0.002150538 | 0.010752688 | -0.000014836 | -0.000012435 | 2.915036969 | 21.000000000 |
| q2s3 | 368 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | -0.000028957 | -0.000020808 | 5.755757463 | 14.000000000 |

## Interpretation

The survivor set is not a Q2/S3 diffuse-tail subset. The `q2s3` mask has zero
E101-plausible scenarios and predicts E101 far too favorable relative to E95.
E101-plausible worlds mostly come from broad/all or high-hard-tail budget
allocations, with much lower alpha and almost no E101-vs-E95 tail advantage.

That means E101's small loss is not explained by simply finding a better Q2/S3
cell gate. The missing variable looks like public transfer shrinkage plus
tail-budget allocation outside the active Q2/S3 cells. This strengthens the
decision to leave the same-family line unless a genuinely new S3-specific
sensor appears.

## Decision

No submission. E125 turns E124's negative result into a sharper rule: do not
use Q2/S3-mask E99 worlds, full E89, or same-line rollback variants as default
successors. The next experiment should test a different hidden structure, or a
new sensor that explains why public transfer alpha collapses near the
E95/E101 boundary.
