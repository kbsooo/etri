# Domain Idea Bank Experiment Log

## 2026-05-21 - v1 Registry And Encoder-First Diagnostics

### Scope

Imported `idea_gpt.md`, `idea_claude.md`, and `idea_gemini.md` as a traceable experiment registry. The parser found 340 numbered items because the source files include extra numbered sections beyond the requested 300 ideas.

### Artifacts

- Manifest: `experiments/domain_idea_bank/domain_idea_manifest.csv`
- Day-state feature bank: `artifacts/domain_state_features_v1.parquet`
- Encoder token tensor: `artifacts/domain_encoder_tokens_v1.npz`
- Label-free diagnostics: `outputs/domain_idea_encoder_diagnostics_v1/report.md`

### Registry Status

| status | count |
| --- | ---: |
| ready | 280 |
| queued_encoder_ssl | 43 |
| gated | 17 |

The gated items mention labels, pseudo labels, target means, or other target-adjacent signals and must not be used before nested validation.

### Encoder-First Result

The first label-free diagnostic used PCA as a tiny unsupervised encoder over value/mask token views. No label decoder was used.

| view | channels | train/sample shift | subject leakage | note |
| --- | ---: | ---: | ---: | --- |
| only_event | 11 | 0.817682 | 0.611429 | Best low-drift view; good first SSL candidate. |
| only_cross_modal | 2 | 1.326479 | 0.537143 | Low subject leakage; compact but narrow. |
| only_phone | 13 | 1.527232 | 0.818571 | Useful temporal signal but identity-heavy. |
| only_missingness | 21 | 2.991721 | 0.461429 | Very compact, low identity leakage, but higher split shift. |
| full | 110 | 9.164953 | 0.882857 | Too much identity/panel structure; unsafe as the default encoder input. |

### Working Interpretation

The current evidence supports feature-family pruning before decoder work. Full multimodal tokens are too subject-identifying. Event, cross-modal, and missingness views look more like reusable day-state signals and should be used as the first Transformer/Diffusion SSL inputs.

### Next Experiments

1. Train a masked patch Transformer on `only_event + only_cross_modal + only_missingness` with subject embedding disabled or adversarially reduced.
2. Add subject-relative normalization inside the token tensor, not only in day-level aggregates.
3. Run family ablation with label probes only after the encoder passes low-drift/low-leakage diagnostics.
