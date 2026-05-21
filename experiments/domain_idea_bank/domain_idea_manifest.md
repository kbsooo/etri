# Domain Idea Manifest

- Source files: `idea_gpt.md, idea_claude.md, idea_gemini.md`
- Parsed ideas: `340`

## Family Counts

| name | count |
| --- | ---: |
| day_slicing | 135 |
| episode | 88 |
| cross_modal | 80 |
| subject_deviation | 76 |
| target_view | 65 |
| rolling_memory | 49 |
| token_ssl | 45 |
| missingness | 38 |
| misc_domain | 32 |
| motif_retrieval | 31 |

## Implementation Batches

| name | count |
| --- | ---: |
| domain_state_v1 | 280 |
| encoder_pretrain_later | 43 |
| hold_until_stress_test | 17 |

## Notes

- `domain_state_v1` ideas are represented by sleep/routine/debt/episode/missingness/cross-modal/motif feature families in `artifacts/domain_state_features_v1.parquet`.
- `encoder_pretrain_later` ideas need a separate SSL/token pretraining run after the feature bank is validated.
- `hold_until_stress_test` ideas mention labels/pseudo labels/target means and are intentionally gated behind nested validation.
- Each row has an `experiment_id`, `experiment_stage`, `status`, `expected_artifact`, and `validation_gate` so it can be routed into repeatable experiment runners.