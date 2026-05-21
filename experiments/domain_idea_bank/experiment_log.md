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

## 2026-05-21 - Frozen Label Probe for Domain SSL Latents

### Scope

Tested whether the label-free domain SSL encoder latents are readable by a small supervised decoder. The encoder remains frozen. The probe uses fold-safe subject-time folds, subject-prior shrinkage, and no target-wise source cherry-picking.

### Artifacts

- Script: `scripts/probe_domain_ssl_latents.py`
- Report: `outputs/domain_ssl_latent_frozen_probe_v1/report.md`
- Machine-readable report: `outputs/domain_ssl_latent_frozen_probe_v1/report.json`
- Score table: `outputs/domain_ssl_latent_frozen_probe_v1/probe_scores.csv`

### Result

| source | avg logloss | delta vs subject prior | read |
| --- | ---: | ---: | --- |
| subject_token_event_cross_missing + absolute_plus_deviation | 0.626064 | -0.001590 | Best frozen probe; weak but real label-readability. |
| subject_token_event_cross_missing + absolute | 0.626183 | -0.001471 | Almost tied; absolute latent still carries useful state. |
| global_event_cross_missing + absolute | 0.626550 | -0.001104 | Stable global coordinate also has small signal. |
| subject prior | 0.627654 | 0.000000 | Baseline. |
| global_only_event family | ~0.6281-0.6282 | positive | Stable for SSL, but too narrow for label probing alone. |

### Working Interpretation

The 300-idea pipeline is producing measurable but still small supervised signal. The strongest current representation is not "all data" or pure event tokens; it is the normalized `event + cross-modal + missingness` branch, especially when the decoder sees both absolute state and subject-relative deviation. This supports the user's hypothesis that feature family pruning matters: adding more raw/modal channels can make the latent easier to reconstruct but less useful for labels.

The effect size is not yet a breakthrough. A frozen logistic probe improves the subject prior by only `0.00159`, so the next encoder iteration should change the pretext task and tokenization rather than simply adding decoder capacity.

### Next Experiments

1. Train SSL with event/cross/missing tokens but a label-relevant pretext: temporal order, subject-relative future/past deviation, or same-subject contrastive day discrimination.
2. Run a token-family dropout sweep inside SSL so the encoder cannot solve reconstruction from missingness coverage alone.
3. Add target-agnostic behavioral state prototypes from the 300 idea families, then probe whether prototype coordinates improve over the current frozen latent.

## 2026-05-21 - v1 Temporal Contrastive Encoder

### Scope

Replaced pure reconstruction SSL with a target-free temporal contrastive pretext. The model uses the same 30-minute domain token tensor but trains day embeddings with same-day or adjacent-day positives, token/channel augmentation, and subject-centered projection loss. This directly tests whether the 300-idea token families can produce behavioral-state latents rather than value-reconstruction latents.

### Artifacts

- Script: `scripts/train_domain_temporal_contrastive_encoder.py`
- Latent combiner: `scripts/combine_latent_tables.py`
- Contrastive report: `outputs/domain_temporal_contrastive_encoder_v1/report.md`
- Standalone frozen probe: `outputs/domain_temporal_contrastive_probe_v1/report.md`
- Combined frozen probe: `outputs/domain_temporal_contrastive_combined_probe_v1/report.md`

### Encoder Result

| positive mode | normalization | view | read |
| --- | --- | --- | --- |
| same_day | subject_channel_token | only_event | Best contrastive loss and low leakage, but train/sample shift is high. |
| adjacent_day | subject_channel_token | event_cross_missing | Worse contrastive loss but lower shift; best standalone label probe. |
| adjacent_day | global | only_event | Very low shift but weak temporal/local label signal. |

### Frozen Probe Result

| latent source | avg logloss | delta vs subject prior | read |
| --- | ---: | ---: | --- |
| reconstruction SSL best | 0.626064 | -0.001590 | Previous best frozen probe. |
| contrastive standalone best | 0.626525 | -0.001129 | Standalone contrastive is weaker than reconstruction. |
| reconstruction + adjacent contrastive only_event | 0.624798 | -0.002856 | New best diagnostic probe; contrastive adds orthogonal signal. |
| reconstruction + adjacent contrastive event_cross_missing | 0.625735 | -0.001919 | Positive but weaker than adding contrastive only_event. |

### Working Interpretation

Temporal contrastive learning is not strong enough as a replacement encoder yet. The useful signal appears when the reconstruction latent (`subject_channel_token + event_cross_missing`) is concatenated with an adjacent-day contrastive `only_event` latent. This is important: the contrastive branch does not win by itself, but it contributes a different axis that improves frozen label readability beyond reconstruction SSL.

The current best diagnostic probe is now `0.624798`, improving the prior by `0.002856` and improving the previous frozen-probe best by `0.001266`. This still misses the `0.005` breakthrough threshold, but it validates the next direction: multi-objective encoders or late-fusion latent families are more promising than single-pretext encoders.

### Next Experiments

1. Train a joint reconstruction + adjacent-event contrastive encoder instead of concatenating two separately trained latents after the fact.
2. Add a future/past ordering head on top of adjacent-day positives to force temporal direction, not only temporal closeness.
3. Run family dropout on the contrastive branch: `only_event`, `event+missingness`, `event+cross`, and `missingness-blocked`, then promote only branches that improve the combined frozen probe.

## 2026-05-21 - Joint Encoder and Contrastive Family Dropout

### Scope

Tested whether the separate reconstruction and adjacent-day contrastive branches should be merged into one shared multi-objective encoder, then ran contrastive token-family dropout to identify which family should be paired with the reconstruction latent.

### Artifacts

- Joint runner: `scripts/train_domain_joint_encoder.py`
- Joint report: `outputs/domain_joint_encoder_v1/report.md`
- Joint probe: `outputs/domain_joint_encoder_probe_v1/report.md`
- Family dropout report: `outputs/domain_temporal_contrastive_family_dropout_v1/report.md`
- Family dropout standalone probe: `outputs/domain_temporal_contrastive_family_dropout_probe_v1/report.md`
- Family dropout combined probe: `outputs/domain_temporal_contrastive_family_dropout_combined_probe_v1/report.md`

### Result

| experiment | best avg logloss | read |
| --- | ---: | --- |
| reconstruction SSL best | 0.626064 | Baseline frozen probe before temporal contrast. |
| previous reconstruction + adjacent only_event contrastive | 0.624798 | Previous best diagnostic. |
| shared joint reconstruction+contrastive encoder | 0.627167 | Failed as standalone; objective sharing weakened the latent. |
| reconstruction + adjacent event+cross_modal contrastive | 0.622961 | New best diagnostic. |

### Working Interpretation

The shared joint encoder is a negative result. For this dataset, reconstruction and temporal contrast should not be forced through one small CLS bottleneck. Late fusion of specialized branches is better.

The family-dropout result is more useful. `event+cross_modal` contrastive is better than `only_event`, `event+missingness`, `event+cross+missingness`, and broad no-family views once fused with the reconstruction latent. This says the contrastive branch should avoid missingness-heavy shortcuts; missingness is useful in the reconstruction branch, but it blurs the temporal contrastive branch.

The current best diagnostic is now `0.622961`, which improves the subject prior by `0.004693` and is close to the `0.005` breakthrough threshold. The next practical direction is a two-branch encoder family: reconstruction over `event+cross+missingness`, contrastive over `event+cross_modal`, with late-fusion/frozen-probe selection.

### Next Experiments

1. Add a third branch for temporal-order prediction on `event+cross_modal` and test whether it complements the current contrastive branch.
2. Train the contrastive `event+cross_modal` branch for a small sweep of epochs/temperature/reconstruction-free augment strength to see whether `0.622961` is stable.
3. Build a fixed late-fusion representation artifact from the current best branches so downstream decoders can consume it without reassembling parquet paths manually.

## 2026-05-21 - Temporal Order Branch and Best Late Fusion Artifact

### Scope

Tested a target-free temporal direction branch. The encoder sees two adjacent same-subject days and predicts whether the pair is chronological or reversed. This was intended to expose recovery/decline direction rather than only adjacent-day similarity.

### Artifacts

- Script: `scripts/train_domain_temporal_order_encoder.py`
- Temporal order report: `outputs/domain_temporal_order_encoder_v1/report.md`
- Temporal order probe: `outputs/domain_temporal_order_probe_v1/report.md`
- Stable best latent artifact: `artifacts/domain_best_late_fusion_v1.parquet`
- Best latent probe: `outputs/domain_best_late_fusion_v1_probe/report.md`

### Result

| branch | result | read |
| --- | ---: | --- |
| temporal order `event+cross_modal` val accuracy | ~0.50-0.52 | Direction task is near-random. |
| temporal order `event+missingness` val accuracy | ~0.41-0.50 | Worse; missingness does not encode chronological direction. |
| current best late fusion probe | 0.622961 | Still best. |
| best late fusion artifact reprobe | 0.622961 | Artifact faithfully reproduces best diagnostic. |

### Working Interpretation

Temporal direction is not a strong unsupervised axis in the current 30-minute token tensor. Adjacent-day similarity helps, but chronological order does not. This is a useful negative result: recovery/decline direction probably needs explicit label/residual/prototype supervision or richer multi-day windows, not only pair-order classification.

The stable late-fusion artifact now gives downstream decoders one path with 48 latent dimensions: reconstruction `event_cross_missing` plus contrastive `event+cross_modal`. This is the strongest data-engineering representation found so far.

### Next Experiments

1. Use `artifacts/domain_best_late_fusion_v1.parquet` as the canonical encoder representation for nonlinear decoder probes.
2. Try multi-day window objectives such as "today vs previous 3/7-day centroid" instead of pair order.
3. Search for target-agnostic prototypes over the best latent artifact and test whether prototype distances improve the frozen probe.

## 2026-05-21 - Multi-Day Temporal Deviation Diagnostics

### Scope

Built target-free temporal deviation features from the current best late-fusion latent. For each subject/day, the feature builder compares today's latent to subject center plus 3/7/14/28-day past and future centroids, then derives novelty, recovery, and trajectory statistics.

### Artifacts

- Builder: `scripts/build_temporal_deviation_latents.py`
- Column selector: `scripts/select_latent_columns.py`
- Temporal deviation artifact: `artifacts/domain_temporal_deviation_v1.parquet`
- Artifact report: `artifacts/domain_temporal_deviation_v1.report.md`
- Full probe: `outputs/domain_temporal_deviation_probe_v1/report.md`
- Subset probe: `outputs/domain_temporal_deviation_subset_probe_v1/report.md`
- Target diagnostics: `outputs/domain_temporal_deviation_target_diagnostics/report.md`

### Result

| experiment | best avg logloss | read |
| --- | ---: | --- |
| current best late-fusion latent | 0.622961 | Still the best global diagnostic representation. |
| best + all temporal-deviation features | 0.624923 | Worse as a global replacement/addition. |
| temporal-deviation subsets | 0.622961 | No global average improvement, but useful target-specific axes. |

Target-level diagnostics show that the global failure hides specific useful structure:

| target | best new family | delta vs current best target loss | read |
| --- | --- | ---: | --- |
| Q1 | future | -0.002033 | After-effect/recovery context helps. |
| Q2 | trajectory | -0.009833 | Multi-day latent movement is a strong axis. |
| Q3 | trajectory | -0.006959 | Same trajectory signal, slightly weaker than Q2. |
| S2 | future | -0.003536 | Future/recovery context helps more than absolute day state. |
| S3 | current best latent | 0.000000 | Temporal-deviation features do not help. |

### Working Interpretation

This is not a submission-ready decoder and should not be target-wise cherry-picked. But it is a useful data-engineering signal: temporal deviation is harmful when flattened into one global feature block, yet it exposes target-specific latent axes that the current encoder does not present cleanly to a decoder.

The strongest clue is Q2/Q3 trajectory. This suggests that some labels are not only "what was today like?" but "where is today inside the subject's recent state path?" Q1/S2 responding to future context is also interesting; it may be picking up recovery or delayed effects around the label day.

### Next Experiments

1. Build a nested/fold-safe target-specific decoder that can choose between current late-fusion, trajectory, future, and recovery families without full-train source selection bias.
2. Convert trajectory/future features into encoder objectives, not only post-hoc features: predict today's relation to recent/future centroids from masked channel patches.
3. Test prototype/state distances over the late-fusion latent and temporal-deviation latent together, especially for Q2/Q3.

## 2026-05-21 - Nested Temporal-Deviation Source Selection

### Scope

Stress-tested the target-specific temporal-deviation signal with nested fold-safe source selection. For each held fold and target, source selection sees only the other folds' losses, then the selected source is scored on the hidden fold.

### Artifacts

- Script: `scripts/nested_source_selection_diagnostics.py`
- Broad-family nested report: `outputs/domain_temporal_deviation_nested_selection_v1_margin_0p003/report.md`
- Trajectory-only nested report: `outputs/domain_temporal_deviation_nested_selection_trajectory_only_margin_0p003/report.md`

### Result

| selector | base avg fold loss | nested selected avg fold loss | delta | read |
| --- | ---: | ---: | ---: | --- |
| broad temporal families, margin 0.003 | 0.623192 | 0.622182 | -0.001010 | Q2/Q3 survive, but S2 still unstable. |
| trajectory-only, margin 0.003 | 0.623192 | 0.621507 | -0.001685 | Q2/Q3 select trajectory in all folds; other targets stay on base. |

For the trajectory-only selector, target-level held-fold deltas are:

| target | selected family | delta vs base |
| --- | --- | ---: |
| Q2 | trajectory | -0.005938 |
| Q3 | trajectory | -0.005854 |
| all other targets | current best latent | 0.000000 |

### Working Interpretation

This is the cleanest signal in the 300-idea data-engineering track so far. The temporal-deviation features should not be treated as a global feature block. But `trajectory` is a credible Q2/Q3-specific state path: it survives fold-held source selection and is selected consistently across all folds once noisy future/recovery candidates are removed.

The next high-value experiment is to stop computing trajectory as a post-hoc feature and train an encoder objective that makes the latent itself predict or preserve recent/future centroid movement. That is closer to the user's encoder-decoder hypothesis: the encoder should summarize "where this day sits inside the subject's state path," and the decoder should use that path coordinate mostly for Q2/Q3.

## 2026-05-21 - Nested Temporal Decoder Materialization

### Scope

Converted the trajectory-only nested selection diagnostic into actual OOF and test prediction files. The decoder retrains the same fold-safe logistic probes used in the latent diagnostics, then applies the nested held-fold source choices for OOF and an all-train fold-loss selector for test-time source choice.

### Artifacts

- Script: `scripts/build_nested_temporal_decoder.py`
- Report: `outputs/domain_nested_temporal_decoder_v1/report.md`
- OOF predictions: `outputs/domain_nested_temporal_decoder_v1/oof_nested_temporal_decoder.csv`
- Test predictions: `outputs/domain_nested_temporal_decoder_v1/submission_nested_temporal_decoder.csv`
- Test source selection: `outputs/domain_nested_temporal_decoder_v1/test_source_selection.csv`

### Result

| decoder | avg OOF logloss | delta vs current late-fusion best | read |
| --- | ---: | ---: | --- |
| current late-fusion best | 0.622961 | 0.000000 | Baseline diagnostic artifact. |
| nested temporal decoder v1 | 0.621238 | -0.001723 | Q2/Q3 trajectory path materialized as predictions. |

Per-target movement:

| target | current best | nested temporal decoder | delta |
| --- | ---: | ---: | ---: |
| Q2 | 0.702098 | 0.696142 | -0.005956 |
| Q3 | 0.674157 | 0.668048 | -0.006109 |
| Q1/S1/S2/S3/S4 | unchanged | unchanged | 0.000000 |

### Working Interpretation

This is the first concrete decoder artifact from the 300-idea track that improves the current best diagnostic representation without broad feature dumping. It is still not a public-LB claim, but it proves the Q2/Q3 trajectory path can be represented as a reproducible OOF/test decoder.

The gain is too small for the final 0.55 target by itself. The value is directional: Q2/Q3 need a state-path representation. The next encoder experiment should train trajectory preservation directly from the 30-minute token tensor rather than deriving it after the latent is already frozen.
