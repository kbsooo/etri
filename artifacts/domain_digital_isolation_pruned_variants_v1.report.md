# Digital Isolation Pruned Variants

| variant | output | rows | feature_count | patterns |
| --- | --- | --- | --- | --- |
| social_isolation | artifacts/domain_digital_isolation_social_isolation_v1.parquet | 700 | 96 | ['social', 'passive_over_social', 'isolation', 'passive_share', 'social_share'] |
| app_diversity_shift | artifacts/domain_digital_isolation_app_diversity_shift_v1.parquet | 700 | 42 | ['entropy', 'hhi', 'top1', 'profile_jsd'] |
| phone_fragmentation | artifacts/domain_digital_isolation_phone_fragmentation_v1.parquet | 700 | 37 | ['phone_start', 'phone_burst', 'short_check', 'screen_without_usage', 'phone_still', 'phone_move'] |
| prebed_consumption | artifacts/domain_digital_isolation_prebed_consumption_v1.parquet | 700 | 60 | ['prebed'] |
| digital_rhythm | artifacts/domain_digital_isolation_digital_rhythm_v1.parquet | 700 | 88 | ['night', 'evening', 'past7', 'past14', 'burstiness'] |