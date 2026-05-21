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

## 2026-05-21 - v1 Masked Patch SSL Encoder

### Scope

Trained a repeatable label-free masked patch Transformer over the domain encoder tokens. This is still encoder-first: no label decoder, no teacher submission, and no target columns are used.

### Artifacts

- Script: `scripts/train_domain_masked_patch_encoder.py`
- Report: `outputs/domain_masked_patch_encoder_v1/report.md`
- Machine-readable report: `outputs/domain_masked_patch_encoder_v1/report.json`
- Summary table: `outputs/domain_masked_patch_encoder_v1/ssl_summary.csv`

### Environment Note

The first smoke test exposed a local OpenMP conflict when importing `numpy` before `torch`. The runner now imports `torch` first and does not use the unsafe `KMP_DUPLICATE_LIB_OK` workaround.

### Result

| view | mean best val loss | subject leakage | train/sample shift | effective rank | read |
| --- | ---: | ---: | ---: | ---: | --- |
| only_event | 0.723282 | 0.208571 | 0.026047 | 3.606030 | Best balanced SSL view. |
| only_missingness | 0.723475 | 0.265000 | 0.077510 | 2.200197 | Reconstructs well but shifts more. |
| event_cross_missing | 0.755342 | 0.252143 | 0.025125 | 3.123873 | Best combined candidate. |
| no_body | 0.794839 | 0.366429 | 0.026659 | 2.626916 | Body removal helps less than expected; identity still present. |
| event_cross_phone_missing | 0.845202 | 0.292857 | 0.033608 | 1.841944 | Adding phone hurts reconstruction and rank. |
| full | 0.847681 | 0.327857 | 0.046185 | 2.731493 | Full feature mix remains inferior. |
| only_cross_modal | 0.984546 | 0.207857 | 0.046570 | 2.127491 | Too narrow alone; useful as a supplement. |

### Working Interpretation

This confirms the earlier PCA diagnostic with an actual SSL encoder: event tokens are the cleanest primary representation. Missingness is strong but unstable across seeds and split shift. Cross-modal signals are not enough alone, but combining them with event/missingness is plausible. Full multimodal input is not the best encoder input despite having more data.

### Next Experiments

1. Train `only_event` and `event_cross_missing` longer with smaller mask-prob sweeps.
2. Add subject-relative token normalization for event/missingness before SSL.
3. Only after those label-free gates, run a frozen linear probe to test whether the new latent is label-readable.

## 2026-05-21 - v2 Subject-Normalized Token SSL

### Scope

Tested whether subject-relative normalization should happen inside the encoder token tensor rather than only in day-level aggregate features. The run compares `global`, `subject_channel`, and `subject_channel_token` normalization on the three strongest v1 views.

### Artifacts

- Script: `scripts/train_domain_masked_patch_encoder.py`
- Report: `outputs/domain_masked_patch_encoder_v2_subject_norm/report.md`
- Summary table: `outputs/domain_masked_patch_encoder_v2_subject_norm/ssl_summary.csv`

### Metric Note

Raw reconstruction loss is not comparable across normalization modes because MAD scaling changes target magnitude. v2 therefore adds `target_observed_mse` and `best_val_loss_relative = best_val_loss / target_observed_mse`.

### Result

| normalization | view | relative loss | subject leakage | train/sample shift | effective rank | read |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| subject_channel | only_event | 0.781888 | 0.321429 | 0.103562 | 3.476967 | Reconstructs relative deviations best, but leaks subject/shift. |
| subject_channel | event_cross_missing | 0.814315 | 0.386429 | 0.091605 | 2.914474 | Good pretext fit but too identity-heavy. |
| subject_channel_token | only_missingness | 0.869389 | 0.185714 | 0.161883 | 2.352296 | Lowest leakage, but split shift is large. |
| subject_channel_token | event_cross_missing | 0.911686 | 0.195000 | 0.049841 | 3.636794 | Best low-leakage combined normalized candidate. |
| global | only_missingness | 0.924400 | 0.265000 | 0.077510 | 2.200197 | Solid but seed-sensitive. |
| global | only_event | 0.994513 | 0.208571 | 0.026047 | 3.606030 | Still the most stable low-shift coordinate. |

### Working Interpretation

Subject-relative normalization is not a free win. It makes the SSL task easier in relative-loss terms, but `subject_channel` increases subject leakage and train/sample shift. The most useful lesson is narrower: keep global `only_event` as the stable coordinate, and test `subject_channel_token + event_cross_missing` as a low-leakage auxiliary branch.

### Next Experiments

1. Add a frozen label probe only for `global only_event`, `global event_cross_missing`, and `subject_channel_token event_cross_missing`.
2. Test lighter normalization such as subject mean subtraction without MAD division.
3. Test mask-prob sweep on `global only_event` because it remains the cleanest encoder input.
