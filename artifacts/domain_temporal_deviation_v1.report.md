# Temporal Deviation Latents

## Purpose

Build target-free multi-day novelty, recovery, and trajectory features from the current best day latent.

- Input: `artifacts/domain_best_late_fusion_v1.parquet`
- Output: `artifacts/domain_temporal_deviation_v1.parquet`
- Rows: `700`
- Feature count: `58`
- Windows: `3, 7, 14, 28`

## Lowest Coverage Features

| feature | non_null_rate | mean | std |
| --- | --- | --- | --- |
| z_td_recovery3_abs_delta | 0.951429 | -0.001178 | 0.053528 |
| z_td_recovery3_l2_delta | 0.951429 | -0.011121 | 0.459411 |
| z_td_trajectory3_alignment | 0.951429 | 0.403576 | 0.375219 |
| z_td_trajectory3_center_l2 | 0.951429 | 0.973086 | 0.369366 |
| z_td_recovery7_abs_delta | 0.968571 | -0.001522 | 0.038396 |
| z_td_recovery7_l2_delta | 0.968571 | -0.015248 | 0.329021 |
| z_td_trajectory7_alignment | 0.968571 | 0.319953 | 0.383329 |
| z_td_trajectory7_center_l2 | 0.968571 | 0.696005 | 0.291414 |
| z_td_recovery14_abs_delta | 0.971429 | -0.001396 | 0.031542 |
| z_td_recovery14_l2_delta | 0.971429 | -0.015970 | 0.268152 |
| z_td_recovery28_abs_delta | 0.971429 | -0.001439 | 0.029522 |
| z_td_recovery28_l2_delta | 0.971429 | -0.016174 | 0.256366 |
| z_td_trajectory14_alignment | 0.971429 | 0.268061 | 0.385826 |
| z_td_trajectory14_center_l2 | 0.971429 | 0.558610 | 0.252051 |
| z_td_trajectory28_alignment | 0.971429 | 0.239647 | 0.406349 |
| z_td_trajectory28_center_l2 | 0.971429 | 0.487691 | 0.252457 |
| z_td_future3_abs_mean | 0.974286 | 0.126709 | 0.046155 |
| z_td_future3_cosine | 0.974286 | 0.965456 | 0.025784 |
| z_td_future3_l2 | 0.974286 | 1.115453 | 0.396894 |
| z_td_future3_signed_mean | 0.974286 | 0.000081 | 0.003916 |