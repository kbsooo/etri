# Sleep Fragment Recovery fragment_core Variant

## Purpose

Compact S-family probe view split from the broad sleep-fragment/recovery latent family.

- Output: `artifacts/domain_sleep_fragment_recovery_fragment_core_v1.parquet`
- Rows: `700`
- Feature count: `68`

## Pattern Rules

`awaken_density`, `awaken_late_load`, `awaken_cluster`, `sleep_sensor_fragment_score`, `sleep_arousal_transition`, `sleep_late_minus`, `longest_block_share`

## Feature Coverage

| feature | mean | std |
| --- | --- | --- |
| z_sfr_awaken_cluster_score | 9.766843 | 11.066398 |
| z_sfr_awaken_cluster_score_subdev | 1.348428 | 10.146770 |
| z_sfr_awaken_cluster_score_subpct | 0.507143 | 0.268502 |
| z_sfr_awaken_cluster_score_subrz | 0.210815 | 1.474660 |
| z_sfr_awaken_density | 0.106858 | 0.116603 |
| z_sfr_awaken_density_past14_abs_delta | 0.078730 | 0.080598 |
| z_sfr_awaken_density_past14_delta | 0.001567 | 0.112698 |
| z_sfr_awaken_density_past14_volatility | 0.103846 | 0.047680 |
| z_sfr_awaken_density_past28_abs_delta | 0.077341 | 0.078758 |
| z_sfr_awaken_density_past28_delta | 0.001398 | 0.110413 |
| z_sfr_awaken_density_past28_volatility | 0.104161 | 0.041085 |
| z_sfr_awaken_density_past3_abs_delta | 0.081854 | 0.089226 |
| z_sfr_awaken_density_past3_delta | 0.000658 | 0.121122 |
| z_sfr_awaken_density_past3_volatility | 0.082892 | 0.070870 |
| z_sfr_awaken_density_past7_abs_delta | 0.080934 | 0.084160 |
| z_sfr_awaken_density_past7_delta | 0.000932 | 0.116797 |
| z_sfr_awaken_density_past7_volatility | 0.099375 | 0.055587 |
| z_sfr_awaken_density_subdev | 0.018034 | 0.109020 |
| z_sfr_awaken_density_subpct | 0.507143 | 0.270606 |
| z_sfr_awaken_density_subrz | 0.257655 | 1.549974 |
| z_sfr_awaken_late_load | 0.196651 | 0.280535 |
| z_sfr_awaken_late_load_past14_abs_delta | 0.203002 | 0.185797 |
| z_sfr_awaken_late_load_past14_delta | 0.001224 | 0.275296 |
| z_sfr_awaken_late_load_past14_volatility | 0.255494 | 0.099405 |
| z_sfr_awaken_late_load_past28_abs_delta | 0.202835 | 0.182921 |
| z_sfr_awaken_late_load_past28_delta | -0.002128 | 0.273234 |
| z_sfr_awaken_late_load_past28_volatility | 0.261504 | 0.086667 |
| z_sfr_awaken_late_load_past3_abs_delta | 0.217766 | 0.223031 |
| z_sfr_awaken_late_load_past3_delta | 0.002086 | 0.311814 |
| z_sfr_awaken_late_load_past3_volatility | 0.207584 | 0.174538 |
| z_sfr_awaken_late_load_past7_abs_delta | 0.208814 | 0.195307 |
| z_sfr_awaken_late_load_past7_delta | 0.000299 | 0.286025 |
| z_sfr_awaken_late_load_past7_volatility | 0.246905 | 0.122177 |
| z_sfr_awaken_late_load_subdev | 0.112964 | 0.272639 |
| z_sfr_awaken_late_load_subpct | 0.507143 | 0.255821 |
| z_sfr_awaken_late_load_subrz | 49361.300189 | 165217.238424 |
| z_sfr_longest_block_share | 0.475593 | 0.309625 |
| z_sfr_longest_block_share_past14_abs_delta | 0.198998 | 0.171210 |
| z_sfr_longest_block_share_past14_delta | 0.002375 | 0.262610 |
| z_sfr_longest_block_share_past14_volatility | 0.254750 | 0.081090 |