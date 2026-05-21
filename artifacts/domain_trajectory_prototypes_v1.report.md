# Prototype State Latents

## Purpose

Build unsupervised global and subject-centered prototype distances over a latent state space.

- Input: `outputs/domain_temporal_deviation_probe_v1/subsets/trajectory.parquet`
- Output: `artifacts/domain_trajectory_prototypes_v1.parquet`
- Rows: `700`
- Feature count: `94`
- K values: `3, 5, 8`

## Feature Coverage

| feature | non_null_rate | mean | std |
| --- | --- | --- | --- |
| z_proto_abs_k3_label | 1.000000 | 0.801429 | 0.654465 |
| z_proto_abs_k3_min_dist | 1.000000 | 2.373177 | 0.963954 |
| z_proto_abs_k3_second_dist | 1.000000 | 3.622759 | 1.185730 |
| z_proto_abs_k3_dist_margin | 1.000000 | 1.249582 | 0.768078 |
| z_proto_abs_k3_soft_entropy | 1.000000 | 0.984242 | 0.065289 |
| z_proto_abs_k3_dist_c0 | 1.000000 | 3.444962 | 1.350300 |
| z_proto_abs_k3_prob_c0 | 1.000000 | 0.350273 | 0.143133 |
| z_proto_abs_k3_dist_c1 | 1.000000 | 2.970446 | 1.547321 |
| z_proto_abs_k3_prob_c1 | 1.000000 | 0.419582 | 0.130038 |
| z_proto_abs_k3_dist_c2 | 1.000000 | 4.504590 | 1.169409 |
| z_proto_abs_k3_prob_c2 | 1.000000 | 0.230145 | 0.141393 |
| z_proto_abs_k5_label | 1.000000 | 1.568571 | 1.149553 |
| z_proto_abs_k5_min_dist | 1.000000 | 2.164237 | 0.757414 |
| z_proto_abs_k5_second_dist | 1.000000 | 3.215060 | 1.030361 |
| z_proto_abs_k5_dist_margin | 1.000000 | 1.050823 | 0.844195 |
| z_proto_abs_k5_soft_entropy | 1.000000 | 1.328058 | 0.115797 |
| z_proto_abs_k5_dist_c0 | 1.000000 | 3.537251 | 1.316197 |
| z_proto_abs_k5_prob_c0 | 1.000000 | 0.238020 | 0.110071 |
| z_proto_abs_k5_dist_c1 | 1.000000 | 3.584548 | 1.443111 |
| z_proto_abs_k5_prob_c1 | 1.000000 | 0.240221 | 0.123158 |