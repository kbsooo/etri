# Digital Boundary Latents

## Purpose

Encode phone/app behavior at sleep boundaries: last phone before sleep, phone intrusions during sleep, first phone/move after wake, prebed stimulation, and phone-stillness pressure.

- Output: `artifacts/domain_digital_boundary_v1.parquet`
- Rows: `700`
- Feature count: `405`

## Feature Coverage

| feature | non_null_rate | mean | std |
| --- | --- | --- | --- |
| z_db_app_entropy | 1.000000 | 1.551494 | 0.317503 |
| z_db_app_entropy_subdev | 1.000000 | -0.038505 | 0.252753 |
| z_db_app_entropy_subpct | 1.000000 | 0.507143 | 0.288814 |
| z_db_app_entropy_subrz | 1.000000 | -0.398204 | 2.613589 |
| z_db_app_social_sec | 1.000000 | 5909087.805714 | 4959067.616949 |
| z_db_app_social_sec_subdev | 1.000000 | 306843.724286 | 3542581.827022 |
| z_db_app_social_sec_subpct | 1.000000 | 0.507143 | 0.288814 |
| z_db_app_social_sec_subrz | 1.000000 | 0.137121 | 1.512139 |
| z_db_app_stim_sec | 1.000000 | 4836699.682857 | 3695323.043762 |
| z_db_app_stim_sec_subdev | 1.000000 | 267243.457143 | 2836810.238932 |
| z_db_app_stim_sec_subpct | 1.000000 | 0.507143 | 0.288813 |
| z_db_app_stim_sec_subrz | 1.000000 | 0.122794 | 1.557577 |
| z_db_app_total_sec | 1.000000 | 29849101.607143 | 11975404.905480 |
| z_db_app_total_sec_subdev | 1.000000 | -189952.120000 | 9826327.631035 |
| z_db_app_total_sec_subpct | 1.000000 | 0.507143 | 0.288814 |
| z_db_app_total_sec_subrz | 1.000000 | -0.031923 | 1.525416 |
| z_db_boundary_disruption_score | 1.000000 | 0.797500 | 0.478445 |
| z_db_boundary_disruption_score_past14_delta | 1.000000 | -0.004249 | 0.466555 |
| z_db_boundary_disruption_score_past14_ratio | 1.000000 | 25876.420052 | 167390.513890 |
| z_db_boundary_disruption_score_past28_delta | 1.000000 | -0.005956 | 0.463419 |
| z_db_boundary_disruption_score_past28_ratio | 1.000000 | 25876.408353 | 167390.515701 |
| z_db_boundary_disruption_score_past3_delta | 1.000000 | -0.007613 | 0.512098 |
| z_db_boundary_disruption_score_past3_ratio | 1.000000 | 25876.532376 | 167390.496504 |
| z_db_boundary_disruption_score_past7_delta | 1.000000 | -0.007595 | 0.476130 |
| z_db_boundary_disruption_score_past7_ratio | 1.000000 | 25876.443866 | 167390.510204 |
| z_db_boundary_disruption_score_subdev | 1.000000 | -0.019842 | 0.460973 |
| z_db_boundary_disruption_score_subpct | 1.000000 | 0.507143 | 0.288397 |
| z_db_boundary_disruption_score_subrz | 1.000000 | -0.076355 | 1.530877 |
| z_db_first_move_after_wake_min | 1.000000 | 170.680000 | 328.745864 |
| z_db_first_move_after_wake_min_subdev | 1.000000 | 137.218571 | 327.645212 |
| z_db_first_move_after_wake_min_subpct | 1.000000 | 0.507143 | 0.287626 |
| z_db_first_move_after_wake_min_subrz | 1.000000 | 5.818722 | 16.776895 |
| z_db_first_phone_after_wake_min | 1.000000 | 75.318571 | 231.636876 |
| z_db_first_phone_after_wake_min_past14_delta | 1.000000 | 8.656214 | 236.164778 |
| z_db_first_phone_after_wake_min_past14_ratio | 1.000000 | 638574.013785 | 5345509.561815 |
| z_db_first_phone_after_wake_min_past28_delta | 1.000000 | 8.831272 | 235.175189 |
| z_db_first_phone_after_wake_min_past28_ratio | 1.000000 | 638573.530188 | 5345509.619664 |
| z_db_first_phone_after_wake_min_past3_delta | 1.000000 | 7.195476 | 264.340085 |
| z_db_first_phone_after_wake_min_past3_ratio | 1.000000 | 2095725.177612 | 38117853.446302 |
| z_db_first_phone_after_wake_min_past7_delta | 1.000000 | 8.510561 | 246.136272 |