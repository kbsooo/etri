# External model/data experiment report

Date: 2026-05-22

## Generated external feature families

- `features/external_context_features_v1.parquet` via `scripts/36_build_external_context_features.py`
  - calendar / Korean holiday / weekend / solar-daylight / Open-Meteo-style historical weather context.
- `features/external_app_semantic_features_v1.parquet` via `scripts/37_build_external_app_semantic_features.py`
  - public Korean/English app-category prototype priors with local char n-gram semantic clusters.
- `features/external_hf_app_embedding_features_v1.parquet` via `scripts/42_build_hf_app_embedding_features.py`
  - HuggingFace `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` app-name embeddings and semantic clusters.
- `features/external_tsfm_proxy_features_v1.parquet` via `scripts/38_build_external_tsfm_proxy_features.py`
  - forecasting-inspired routine residuals, day-token PCA, and prototype clusters.
- `features/external_chronos_bolt_features_v1.parquet` via `scripts/41_build_chronos_bolt_features.py`
  - Amazon Chronos-Bolt tiny one-step daily summary forecasts; residual / uncertainty features.
- TabPFN ablation in Python 3.12 env `.venv312` via `scripts/40_eval_tabpfn_external.py`.

## Main CV results

Baseline previous best replicate:

| model | mean logloss |
|---|---:|
| `base_v4_replicate` | 0.601643 |

Best single external-only probes:

| family | best config | mean logloss |
|---|---|---:|
| calendar/weather/daylight | `ext_context_only_k5_C0.01` | 0.688060 |
| char-ngram app semantics | `ext_appsem_only_k5_C0.01` | 0.685623 |
| HF app embeddings | `ext_hfapp_only_k5_C0.01` | 0.679775 |
| TSFM proxy residuals | `ext_tsfm_only_k5_C0.01` | 0.679032 |
| Chronos-Bolt residuals | `ext_chronos_only_k5_C0.03` | 0.681572 |
| all external | `ext_all_only_k5_C0.01` | 0.680991 |

Best simple “add external to base” probes did not beat baseline:

| model | mean logloss |
|---|---:|
| `base_v4_replicate` | 0.601643 |
| `base_v4_plus_ext_context_ks1_cm1` | 0.615641 |
| `base_v4_plus_ext_chronos_ks1_cm1` | 0.617436 |
| `base_v4_plus_ext_tsfm_ks2_cm0.3` | 0.628026 |
| `base_v4_plus_ext_hfapp_ks1_cm0.3` | 0.646818 |

Targetwise sweep oracle, selecting per-label best among all external/base variants:

| fold | mean | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| chrono_last_20 | 0.590715 | 0.612975 | 0.624561 | 0.650316 | 0.522203 | 0.562957 | 0.593665 | 0.568326 |
| chrono_last_25 | 0.596173 | 0.647400 | 0.621693 | 0.648794 | 0.527715 | 0.565430 | 0.570621 | 0.591560 |
| chrono_last_30 | 0.609037 | 0.640831 | 0.640999 | 0.638807 | 0.569033 | 0.580264 | 0.570529 | 0.622798 |
| **avg** | **0.598642** | | | | | | | |

Oracle config:

```python
{
  'Q1': ('semantic_only', 50, 0.03),
  'Q2': ('day_flat+ext_appsem', 80, 0.01),
  'Q3': ('ext_chronos', 5, 0.3),
  'S1': ('no_flat_hourly', 20, 0.1),
  'S2': ('no_flat_hourly', 20, 0.001),
  'S3': ('semantic_only', 20, 0.01),
  'S4': ('sleep_plus_s4x+ext_tsfm', 200, 0.009),
}
```

TabPFN ablation:

| model | mean logloss |
|---|---:|
| `tabpfn_base_v4_subsets` | 0.628881 |
| `tabpfn_external_targetwise_subsets` | 0.625667 |

## Interpretation

- External features contain signal, but as direct feature additions they overfit the small train set and worsen the previous robust target-specific baseline.
- Best external-only signals are TSFM-style residuals, HF app embeddings, and Chronos residuals (~0.679–0.682), which is meaningful but far below the base feature stack.
- The only apparent improvement is targetwise: Q2 benefits from app semantics, Q3 from Chronos, S4 from TSFM residuals. That oracle average is 0.598642 vs 0.601643 baseline, but the gain is small and likely optimistic because it picks per-label configs from the same CV sweep.
- TabPFN did not beat logistic target-specific models on this small, noisy, high-missingness setup.

## Recommendation

Do not blindly submit a full external-feature fusion. If submitting another candidate, use a conservative targetwise blend or only replace Q2/S4 with external-assisted models after validating on a fresh split/seed. Keep `base_v4_replicate` as the safest current candidate.
