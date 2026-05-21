# Causal Chain Pruned Variants

| variant | output | rows | feature_count | patterns |
| --- | --- | --- | --- | --- |
| load | artifacts/domain_causal_chain_load_v1.parquet | 700 | 32 | ['physical_load', 'mobility_context', 'high_load', 'load_after'] |
| arousal | artifacts/domain_causal_chain_arousal_v1.parquet | 700 | 28 | ['evening_arousal', 'arousal', 'late_arousal', 'onset_late'] |
| opportunity | artifacts/domain_causal_chain_opportunity_v1.parquet | 700 | 32 | ['sleep_opportunity', 'opportunity', 'phase_compression', 'wake_late', 'onset_late'] |
| continuity | artifacts/domain_causal_chain_continuity_v1.parquet | 700 | 40 | ['sleep_friction', 'continuity', 'fragmented', 'sleep_quality'] |
| recovery | artifacts/domain_causal_chain_recovery_v1.parquet | 700 | 40 | ['morning_recovery', 'recovery', 'fatigue'] |
| chain_interactions | artifacts/domain_causal_chain_chain_interactions_v1.parquet | 700 | 92 | ['chain_score', 'gap', 'deficit', 'high_load_low', 'load_after_bad', 'arousal_to'] |