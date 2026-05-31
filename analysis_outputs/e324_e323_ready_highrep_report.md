# E324 E323 Ready High-Rep Stress

Public LB was not used.

## Summary

| slice | rows | ready | best_p90 | best_null_strict | best_worst_mode | null_rows |
| --- | --- | --- | --- | --- | --- | --- |
| e323_ready_highrep | 3 | 3 | -0.000109221 | 0.050387597 | 0.859375000 | 774 |

## High-Rep Governor

| basename | base_variant | highrep_actual_p90 | highrep_null_strict_rate | highrep_p90_dominance | highrep_mean_dominance | highrep_worst_mode_p90_dominance | highrep_row_null_strict_rate | highrep_subject_null_strict_rate | highrep_dateblock_null_strict_rate | highrep_public_free_submission_ready | highrep_final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv | meanresid_l1.50 | -0.000053747 | 0.050387597 | 0.926356589 | 0.914728682 | 0.859375000 | 0.062500000 | 0.031250000 | 0.015625000 | True | public_free_submission_ready |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_de5d9c5d.csv | meanresid_l1.50 | -0.000075609 | 0.081395349 | 0.918604651 | 0.903100775 | 0.796875000 | 0.078125000 | 0.015625000 | 0.062500000 | True | public_free_submission_ready |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____orth_nullmean__kall__51ed84b0.csv | orth_nullmean | -0.000109221 | 0.093023256 | 0.926356589 | 0.903100775 | 0.812500000 | 0.046875000 | 0.046875000 | 0.109375000 | True | public_free_submission_ready |

## Decision

- `submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv` survives high-repetition local null stress.

## Outputs

- `analysis_outputs/e324_e323_ready_highrep_governor_audit.csv`
- `analysis_outputs/e324_e323_ready_highrep_summary.csv`
- `analysis_outputs/e324_e323_ready_highrep_report.md`
