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

## 2026-05-21 - Trajectory Prototype State Probe

### Scope

Built unsupervised prototype/state distances over the trajectory latent. The feature builder fits global and subject-centered KMeans states on all 700 unlabeled subject-days, then emits distances, soft cluster probabilities, margins, and entropy features.

### Artifacts

- Builder: `scripts/build_prototype_state_latents.py`
- Prototype artifact: `artifacts/domain_trajectory_prototypes_v1.parquet`
- Prototype probe: `outputs/domain_trajectory_prototype_probe_v1/report.md`
- Prototype nested reports:
  - `outputs/domain_trajectory_prototype_nested_selection_v1/report.md`
  - `outputs/domain_trajectory_prototype_nested_selection_q2_proto_v1/report.md`
- Hybrid decoder: `outputs/domain_hybrid_q2_proto_q3_trajectory_decoder_v1/report.md`

### Result

| experiment | avg OOF logloss | read |
| --- | ---: | --- |
| current late-fusion best | 0.622961 | Baseline diagnostic artifact. |
| Q2/Q3 trajectory decoder | 0.621238 | Q2/Q3 use trajectory; other targets unchanged. |
| Q2 prototype + Q3 trajectory hybrid | 0.621107 | New best diagnostic decoder in this track. |

Prototype target diagnostics:

| target | prototype effect | read |
| --- | ---: | --- |
| Q2 | about -0.011 target-only, -0.0064 nested | Prototype state is useful. |
| Q3 | negative under nested selection | Raw trajectory is better than prototype state. |
| S4 | unstable/harmful if allowed | Keep S targets on base. |

### Working Interpretation

Q2 and Q3 are not identical even though both respond to the temporal trajectory family. Q2 benefits from coarser prototype/state membership over trajectory space, while Q3 needs the continuous trajectory deviation coordinates. This is useful because it suggests the decoder should not merely share one trajectory head across all Q targets; it likely needs target-specific state readouts.

The improvement is still incremental, not a 0.55 breakthrough. But the pattern is now sharper: target-specific path/state decomposition is a real signal, while broad prototype features are not safe globally.

## 2026-05-21 - Event Rhythm and S4 Decoder Path

### Scope

Built sensor-level event rhythm features from the 30-minute event-hybrid grid. This implements a cluster of manifest ideas around activity burstiness, circadian phase, modality coverage rhythm, and cross-modal rhythm gaps.

### Artifacts

- Builder: `scripts/build_event_rhythm_latents.py`
- Event rhythm artifact: `artifacts/domain_event_rhythm_v1.parquet`
- Probe: `outputs/domain_event_rhythm_probe_v1/report.md`
- Nested rhythm report: `outputs/domain_event_rhythm_nested_selection_v1/report.md`
- Hybrid decoder: `outputs/domain_hybrid_q2_proto_q3_trajectory_s4_rhythm_decoder_v1/report.md`

### Result

| experiment | avg OOF logloss | read |
| --- | ---: | --- |
| current late-fusion best | 0.622961 | Baseline diagnostic artifact. |
| Q2 prototype + Q3 trajectory hybrid | 0.621107 | Previous best diagnostic decoder. |
| Q2 prototype + Q3 trajectory + S4 event rhythm | 0.620777 | New best diagnostic decoder in this track. |

Nested rhythm selection:

| target | rhythm effect | read |
| --- | ---: | --- |
| S4 | -0.002392 nested | Event rhythm survives all five folds for S4. |
| Q3 | harmful/unstable | Keep Q3 on continuous trajectory instead. |
| other targets | no stable gain | Keep on base. |

### Working Interpretation

The useful signal is becoming target-factorized:

- Q2 wants coarse trajectory prototype/state membership.
- Q3 wants continuous trajectory deviation.
- S4 wants daily event rhythm/circadian/burstiness structure.

This still is not a 0.55 breakthrough. But it is no longer just one vague "trajectory" clue. The decoder now has three distinct target-specific data-engineering paths, each grounded in a nested diagnostic.

## 2026-05-21 - Sleep Intrusion and S2 Decoder Path

### Scope

Built sleep-window intrusion features around each subject-day's observed sleep onset and wake time. This implements the manifest ideas around pre-bed phone usage, sleep-time sensor interruptions, no-wear/low-coverage episodes, charging/screen bursts, and subject-relative sleep metric drift.

### Artifacts

- Builder: `scripts/build_sleep_intrusion_latents.py`
- Sleep intrusion artifact: `artifacts/domain_sleep_intrusion_v1.parquet`
- Probe: `outputs/domain_sleep_intrusion_probe_v1/report.md`
- Nested sleep report: `outputs/domain_sleep_intrusion_nested_selection_v1/report.md`
- Hybrid decoder: `outputs/domain_hybrid_q2_proto_q3_trajectory_s2_sleep_s4_rhythm_decoder_v1/report.md`

### Result

| experiment | avg OOF logloss | read |
| --- | ---: | --- |
| current late-fusion best | 0.622961 | Baseline diagnostic artifact. |
| Q2 prototype + Q3 trajectory + S4 event rhythm | 0.620777 | Previous best diagnostic decoder. |
| Q2 prototype + Q3 trajectory + S2 sleep intrusion + S4 event rhythm | 0.620668 | New best diagnostic decoder in this track. |

Nested sleep selection:

| target | sleep effect | read |
| --- | ---: | --- |
| S2 | -0.000976 nested vs base | Weak but fold-surviving signal. |
| Q1 | +0.001753 nested vs base | Apparent probe gain is unstable/harmful. |
| S4 | +0.000959 nested vs base | Event rhythm remains the better S4 path. |
| S1/S3 | no stable gain | Keep on base. |

### Working Interpretation

Sleep intrusion is not a broad sleep decoder. Its only useful role in this run is a narrow S2 correction, mostly from pre-bed/sleep-window coverage and interruption structure. This is useful as evidence for target-factorization, but it is not a 0.55 breakthrough.

The current target map is now:

- Q2: trajectory prototype/state membership.
- Q3: continuous trajectory deviation.
- S2: sleep intrusion/coverage episodes.
- S4: event rhythm/circadian/burstiness.
- Q1/S1/S3: still no new domain path that survives nested selection.

## 2026-05-21 - Digital Sleep and Routine Regularity

### Scope

Built two new feature families from the 300-idea manifest:

- `routine_regularity`: personal routine residuals, weekday-specific routine distance, circadian phase shift, sleep regularity breaks, and multi-scale volatility.
- `digital_sleep`: phone/screen/app/prebed usage isolated as a first-class sleep feature family, motivated by the observation that digital behavior can dominate classic biosignals for sleep targets.

### Artifacts

- Routine builder: `scripts/build_routine_regularity_latents.py`
- Routine artifact: `artifacts/domain_routine_regularity_v1.parquet`
- Routine probe/nested reports:
  - `outputs/domain_routine_regularity_probe_v1/report.md`
  - `outputs/domain_routine_regularity_nested_selection_v1/report.md`
- Digital builder: `scripts/build_digital_sleep_latents.py`
- Digital artifact: `artifacts/domain_digital_sleep_v1.parquet`
- Digital probe/nested reports:
  - `outputs/domain_digital_sleep_probe_v1/report.md`
  - `outputs/domain_digital_sleep_nested_selection_v1/report.md`
- Combined probe/nested reports:
  - `outputs/domain_routine_digital_combined_probe_v1/report.md`
  - `outputs/domain_routine_digital_combined_nested_selection_v1/report.md`
- Hybrid decoder: `outputs/domain_hybrid_q2_proto_q3_trajectory_s2_sleep_s4_routine_decoder_v1/report.md`

### Result

| experiment | avg OOF logloss | read |
| --- | ---: | --- |
| current late-fusion best | 0.622961 | Baseline diagnostic artifact. |
| digital_sleep global probe | 0.621977 | Strong raw digital signal, but S3 harm prevents global append. |
| routine+digital global probe | 0.622618 | Some Q1/S1/S2/S4 raw signal, but not stable enough globally. |
| previous hybrid: Q2 proto + Q3 trajectory + S2 sleep + S4 rhythm | 0.620668 | Previous best diagnostic decoder in this track. |
| new hybrid: Q2 proto + Q3 trajectory + S2 sleep + S4 routine | 0.620093 | New best diagnostic decoder in this track. |

Nested target reads:

| family | useful nested target | read |
| --- | --- | --- |
| digital_sleep | Q2, Q3 | Real signal, but weaker than existing trajectory/prototype paths for the current hybrid. |
| digital_sleep | S2 | Raw probe is very strong, but nested selection is weaker than sleep intrusion. |
| routine_regularity | S4 | Strongest clean gain in this cycle, replacing event rhythm for S4. |
| routine_regularity | S1/S2/Q3 | Probe gains are mostly unstable or harmful under nested selection. |
| routine+digital | Q1/S2 small | Interesting but not enough to beat the target-specific current paths. |

### Working Interpretation

The user's digital-behavior hypothesis is supported: phone/screen/app features are among the strongest raw probe signals in this cycle. The important nuance is decoder placement. Digital features should not be broadly appended because they damage S3 and are partially redundant with trajectory/sleep-intrusion paths. Their value is as a target-specific expert or as an encoder input family to preserve, not as an undifferentiated feature dump.

The current best diagnostic target map is now:

- Q2: trajectory prototype/state membership.
- Q3: continuous trajectory deviation.
- S2: sleep intrusion/coverage episodes.
- S4: routine regularity/circadian phase break.
- Q1/S1/S3: still no strong stable domain path.

## 2026-05-21 - Fatigue Carryover and Mobility Constriction

### Scope

Built two additional 300-idea feature families:

- `fatigue_carryover`: wake-anchored recovery, wake+12h fatigue accumulation, sleep debt ledger, screen fatigue trend, and weekend transition carry-over.
- `mobility_constriction`: home-stay deviation, location entropy, novelty, passive/active mobility balance, stationary-home load, and constrained-day markers.

### Artifacts

- Fatigue builder: `scripts/build_fatigue_carryover_latents.py`
- Fatigue artifact: `artifacts/domain_fatigue_carryover_v1.parquet`
- Fatigue probe/nested reports:
  - `outputs/domain_fatigue_carryover_probe_v1/report.md`
  - `outputs/domain_fatigue_carryover_nested_selection_v1/report.md`
- Mobility builder: `scripts/build_mobility_constriction_latents.py`
- Mobility artifact: `artifacts/domain_mobility_constriction_v1.parquet`
- Mobility probe/nested reports:
  - `outputs/domain_mobility_constriction_probe_v1/report.md`
  - `outputs/domain_mobility_constriction_nested_selection_v1/report.md`
- Hybrid decoder: `outputs/domain_hybrid_q2_proto_q3_mobility_s2_sleep_s4_routine_decoder_v1/report.md`

### Result

| experiment | avg OOF logloss | read |
| --- | ---: | --- |
| previous hybrid: Q2 proto + Q3 trajectory + S2 sleep + S4 routine | 0.620093 | Previous best diagnostic decoder. |
| fatigue_carryover global probe | 0.622961 best remained base | Raw Q1/S1/S4 hints did not survive nested selection. |
| mobility_constriction global probe | 0.622961 best remained base | Global append hurts, but Q3 is strong target-wise. |
| new hybrid: Q2 proto + Q3 mobility + S2 sleep + S4 routine | 0.619947 | New best diagnostic decoder in this track. |

Nested target reads:

| family | useful nested target | read |
| --- | --- | --- |
| fatigue_carryover | none | Q1 raw gain was selection noise; held-fold Q1 worsened by +0.0063. |
| mobility_constriction | Q3 | Selected in all five folds; nested Q3 improves by -0.0075 vs base and beats trajectory Q3 in the hybrid. |
| mobility_constriction | Q1/S2/S3/S4 | Apparent switches are unstable or harmful; keep base/current specialists. |

### Working Interpretation

The mobility result changes the target map. Q3 is no longer best represented as generic latent trajectory; it is better read as a location/mobility constriction state: home-stay, place entropy, novelty, passive/active movement, and constrained-day markers. This fits the domain interpretation of Q3-like stress/subjective state better than pure temporal trajectory.

The current best diagnostic target map is now:

- Q2: trajectory prototype/state membership.
- Q3: mobility constriction/location entropy state.
- S2: sleep intrusion/coverage episodes.
- S4: routine regularity/circadian phase break.
- Q1/S1/S3: still no strong stable domain path.

## 2026-05-22 - Digital Boundary Pruning

### Scope

Followed up on the domain observation that smartphone/app usage can dominate traditional biosignals for sleep-related targets. Instead of adding broad phone totals, this cycle built sleep-boundary digital features:

- Last phone activity before sleep onset.
- Phone/screen bouts during the sleep window.
- First phone and first movement after wake.
- Pre-bed stimulation/social app pressure.
- Phone-while-still and morning sluggishness proxies.

The full feature family was then pruned into compact variants because the 405-feature broad family was too noisy.

### Artifacts

- Full digital-boundary builder: `scripts/build_digital_boundary_latents.py`
- Full artifact: `artifacts/domain_digital_boundary_v1.parquet`
- Pruned variant builder: `scripts/build_digital_boundary_pruned_variants.py`
- Pruned artifacts:
  - `artifacts/domain_digital_boundary_core_v1.parquet`
  - `artifacts/domain_digital_boundary_prebed_v1.parquet`
  - `artifacts/domain_digital_boundary_sleep_phone_v1.parquet`
  - `artifacts/domain_digital_boundary_postwake_v1.parquet`
  - `artifacts/domain_digital_boundary_app_stim_v1.parquet`
- Probe reports:
  - `outputs/domain_best_plus_digital_boundary_probe_v1/report.md`
  - `outputs/domain_digital_boundary_pruned_probe_v1/report.md`
- Nested selection report: `outputs/domain_all_specialists_plus_digital_boundary_pruned_nested_selection_v1/report.md`
- Hybrid decoder: `outputs/domain_hybrid_q1_prebed_q2_proto_q3_mobility_s2_sleep_s4_routine_decoder_v1/report.md`

### Result

| experiment | avg OOF logloss | read |
| --- | ---: | --- |
| previous hybrid: Q2 proto + Q3 mobility + S2 sleep + S4 routine | 0.619947 | Previous best diagnostic decoder. |
| full digital-boundary global append | 0.622961 best remained base | Broad phone-boundary feature dump did not help globally. |
| pruned `db_prebed` Q1 probe | Q1 0.662702 | Strongest Q1 feature-family signal so far. |
| nested all-specialist selection with pruned digital boundary | 0.623532 | Global nested selection still over-switches weak targets. |
| new fixed hybrid: Q1 prebed + Q2 proto + Q3 mobility + S2 sleep + S4 routine | 0.619106 | New best diagnostic decoder in this 300-idea track. |

Nested target reads:

| family | useful nested target | read |
| --- | --- | --- |
| digital_boundary_prebed | Q1 | Selected in all five folds; Q1 improves by -0.0058 vs base under held-fold source selection. |
| digital_boundary_full | none | Too broad; the phone-boundary family needs pruning before decoding. |
| digital_boundary_sleep_phone/postwake/app_stim | none yet | Some raw target hints, but weaker than `db_prebed` and not selected in the fixed hybrid. |

### Working Interpretation

The digital hypothesis is now more precise: the useful Q1 signal is not total app usage, and not generic screen pressure. It is a narrow pre-sleep digital behavior axis, especially subject-relative pre-bed phone/stimulation deviation. This is the first stable new Q1 path in the domain idea-bank track.

The current best diagnostic target map is now:

- Q1: pre-bed digital boundary behavior.
- Q2: trajectory prototype/state membership.
- Q3: mobility constriction/location entropy state.
- S2: sleep intrusion/coverage episodes.
- S4: routine regularity/circadian phase break.
- S1/S3: still no strong stable domain path.

## 2026-05-22 - Sleep Fragment / Recovery And Digital Sleep Probe

### Scope

Tested the hypothesis that digital usage can dominate traditional biosignals for sleep-related labels. Instead of trusting the broad statement directly, this cycle split the sleep family into probeable subfamilies:

- Awakening/fragmentation and sleep-block structure.
- Sleep-window sensor arousal: phone-active, screen, usage, light, HR, movement, no-wear/coverage.
- Post-wake recovery and sluggishness windows.
- Digital-only slices from sleep-window and post-wake phone/screen/usage.
- Compact core fragmentation markers.

### Artifacts

- Builder: `scripts/build_sleep_fragment_recovery_latents.py`
- Pruned variant builder: `scripts/build_sleep_fragment_recovery_pruned_variants.py`
- Full artifact: `artifacts/domain_sleep_fragment_recovery_v1.parquet`
- Pruned artifacts:
  - `artifacts/domain_sleep_fragment_recovery_awakening_v1.parquet`
  - `artifacts/domain_sleep_fragment_recovery_sleep_sensor_v1.parquet`
  - `artifacts/domain_sleep_fragment_recovery_postwake_recovery_v1.parquet`
  - `artifacts/domain_sleep_fragment_recovery_sleep_digital_v1.parquet`
  - `artifacts/domain_sleep_fragment_recovery_postwake_digital_v1.parquet`
  - `artifacts/domain_sleep_fragment_recovery_sleep_wake_digital_v1.parquet`
  - `artifacts/domain_sleep_fragment_recovery_fragment_core_v1.parquet`
- Probe reports:
  - `outputs/domain_sleep_fragment_recovery_probe_v1/report.md`
  - `outputs/domain_sleep_fragment_recovery_pruned_probe_v1/report.md`
  - `outputs/domain_sleep_fragment_recovery_pruned_digital_probe_v1/report.md`
- Nested selection report: `outputs/domain_all_specialists_plus_sfr_pruned_digital_nested_selection_v1/report.md`
- Hybrid check: `outputs/domain_hybrid_q1_sfr_sensor_q2_proto_q3_mobility_s2_sleep_s4_routine_decoder_v1/report.md`

### Result

| experiment | avg OOF logloss | read |
| --- | ---: | --- |
| previous best domain hybrid: Q1 prebed + Q2 proto + Q3 mobility + S2 sleep + S4 routine | 0.619106 | Current best diagnostic decoder. |
| broad sleep fragment/recovery family | 0.633305 best SFR raw avg | Too broad; useful S1 hints are drowned by noisy recovery features. |
| pruned `sfr_sleep_sensor` standalone probe | 0.622631 | Beats the frozen base diagnostic (`0.622961`) narrowly and improves Q1/S1/S2/S4 raw. |
| digital-only sleep/postwake variants | about 0.627 best avg | Digital-only slices are weak alone; the useful sleep signal is mixed sensor/digital context, not only phone totals. |
| nested all-specialist selection with pruned SFR/digital variants | 0.625410 | Global nested selector over-switches and is worse than base. |
| fixed hybrid replacing Q1 prebed with `sfr_sleep_sensor` | 0.619428 | Worse than the previous best hybrid; keep Q1 prebed digital boundary. |

Nested target reads:

| family | useful nested target | read |
| --- | --- | --- |
| sleep_fragment_recovery_sleep_sensor | Q1 only | Selected in 4/5 folds and improves Q1 by -0.0034 vs base under nested selection, but it is weaker than the already discovered `db_prebed` Q1 path. |
| sleep_fragment_recovery_sleep_sensor | S1 raw only | Raw S1 probe reaches about 0.5657, but nested held-fold selection worsens S1 by +0.0045, so it is not stable. |
| sleep_fragment_recovery_core | weak Q3 raw/nested hint | Appears in 2/5 Q3 folds, but the established mobility-constriction Q3 path remains better. |
| digital-only sleep/postwake | none | Does not survive as a standalone sleep decoder family. |

### Working Interpretation

The imported claim is directionally useful but too broad. In this data, digital behavior matters most when placed at a specific behavioral boundary:

- Pre-bed phone/stimulation remains the stable Q1 path.
- Sleep-window phone/screen/usage by itself is not enough for S labels.
- S1 and S3 still need a different hypothesis; current sleep fragmentation, recovery, and digital-only variants do not survive fold-safe selection.

The target map stays:

- Q1: pre-bed digital boundary behavior.
- Q2: trajectory prototype/state membership.
- Q3: mobility constriction/location entropy state.
- S2: sleep intrusion/coverage episodes.
- S4: routine regularity/circadian phase break.
- S1/S3: still open.

## 2026-05-22 - Digital Isolation / App Profile Shift Probe

### Scope

Tested the digital-mental-state hypothesis suggested by the idea bank and the "phone/app signals dominate sleep metrics" observation:

- Social communication density deviation: call, messenger, SNS.
- Passive consumption imbalance: video, music, news, game, reading versus social communication.
- App diversity/profile shift: entropy, HHI, top-1 concentration, Jensen-Shannon distance from subject's usual app mix.
- Phone-check fragmentation: frequent starts, short checks, phone while still, night/evening usage share.
- Pre-bed passive/social consumption as a sleep-adjacent digital arousal view.

### Artifacts

- Builder: `scripts/build_digital_isolation_latents.py`
- Pruned variant builder: `scripts/build_digital_isolation_pruned_variants.py`
- Full artifact: `artifacts/domain_digital_isolation_v1.parquet`
- Pruned artifacts:
  - `artifacts/domain_digital_isolation_social_isolation_v1.parquet`
  - `artifacts/domain_digital_isolation_app_diversity_shift_v1.parquet`
  - `artifacts/domain_digital_isolation_phone_fragmentation_v1.parquet`
  - `artifacts/domain_digital_isolation_prebed_consumption_v1.parquet`
  - `artifacts/domain_digital_isolation_digital_rhythm_v1.parquet`
- Probe reports:
  - `outputs/domain_digital_isolation_probe_v1/report.md`
  - `outputs/domain_digital_isolation_pruned_probe_v1/report.md`
  - `outputs/domain_digital_isolation_plus_best_probe_v1/report.md`
- Nested selection reports:
  - `outputs/domain_all_specialists_plus_digital_isolation_pruned_nested_selection_v1/report.md`
  - `outputs/domain_all_specialists_plus_digital_isolation_additive_nested_selection_v1/report.md`
- Fixed hybrid decoder: `outputs/domain_hybrid_q1_prebed_q2_energy_q3_mobility_s2_di_phone_s4_routine_decoder_v1/report.md`

### Result

| experiment | avg OOF logloss | read |
| --- | ---: | --- |
| broad digital-isolation family | 0.623192 best remained base | Full family has local S2 signal but no global win. |
| pruned DI families | 0.623192 best remained base | `di_social_isolation` has raw Q1/Q2/Q3 signal; `di_digital_rhythm` has tiny S1 signal. |
| `best + DI` additive probe | 0.622760 | `best_plus_di_prebed_consumption` becomes a stronger global raw candidate than base. |
| all-specialist nested selector with DI additive candidates | 0.624597 | Fully automatic selector over-switches and is worse than base. |
| fixed target-map hybrid replacing only S2 with `best_plus_di_phone_fragmentation` | 0.617333 | New best diagnostic hybrid in this 300-idea track, improving prior `0.618005`. |

Target-specific reads:

| family | useful target | read |
| --- | --- | --- |
| `di_social_isolation` | Q1/Q2/Q3 raw | Social/passive imbalance is a real mental-state proxy, but energy recovery and mobility still beat it in the fixed target map. |
| `best_plus_di_phone_fragmentation` | S2 | Strongest new stable use: S2 improves from `0.576741` in the prior hybrid to `0.572031`. |
| `best_plus_di_prebed_consumption` | S4 raw | Raw S4 is strong around `0.6402`, but routine regularity remains better in the fixed hybrid (`0.636763`). |
| app diversity/profile shift | none yet | App entropy/JSD alone is not enough. |

### Working Interpretation

This is the first digital-app experiment after `db_prebed` that improves the fixed target map. The important nuance is that digital isolation is not a replacement for the Q-family experts; it is an additive sleep-context correction. S2 appears to benefit from phone-check fragmentation added on top of the best latent, suggesting that sleep duration/efficiency-related labels need "how fragmented the phone interaction pattern was" more than pure sleep-intrusion or coverage counts.

The target map is updated:

- Q1: pre-bed digital boundary behavior.
- Q2: energy recovery slope / daytime restoration.
- Q3: mobility constriction/location entropy state.
- S2: best latent plus digital phone fragmentation.
- S4: routine regularity/circadian phase break.
- S1/S3: still open.

## 2026-05-22 - Causal Chain / Sleep Opportunity Bottleneck Probe

### Scope

Tested the idea-bank "day causal sketch" hypothesis: a subject-day should be encoded as a chain rather than independent feature totals.

The chain representation is:

1. physical/mobility load
2. evening arousal
3. sleep opportunity
4. continuity loss
5. morning recovery

Then it adds bottleneck interactions such as high-load/low-opportunity, arousal/opportunity gap, fragmented-recovery gap, stress-chain score, sleep-quality-chain score, and fatigue-chain score.

### Artifacts

- Builder: `scripts/build_causal_chain_latents.py`
- Pruned variant builder: `scripts/build_causal_chain_pruned_variants.py`
- Full artifact: `artifacts/domain_causal_chain_v1.parquet`
- Pruned artifacts:
  - `artifacts/domain_causal_chain_load_v1.parquet`
  - `artifacts/domain_causal_chain_arousal_v1.parquet`
  - `artifacts/domain_causal_chain_opportunity_v1.parquet`
  - `artifacts/domain_causal_chain_continuity_v1.parquet`
  - `artifacts/domain_causal_chain_recovery_v1.parquet`
  - `artifacts/domain_causal_chain_chain_interactions_v1.parquet`
- Probe reports:
  - `outputs/domain_causal_chain_probe_v1/report.md`
  - `outputs/domain_causal_chain_pruned_probe_v1/report.md`
  - `outputs/domain_causal_chain_plus_best_probe_v1/report.md`
- Nested all-specialist stress: `outputs/domain_all_specialists_plus_causal_chain_additive_nested_selection_v1/report.md`
- Fixed-map decoders:
  - conservative: `outputs/domain_hybrid_causal_chain_fixed_maps_v1/conservative/report.md`
  - bold Q3 recovery: `outputs/domain_hybrid_causal_chain_fixed_maps_v1/bold_q3_recovery/report.md`

### Result

| experiment | avg OOF logloss | read |
| --- | ---: | --- |
| full causal-chain family | 0.623192 best remained base | Full chain is target-specific, not a global replacement. |
| pruned chain families | 0.623192 best remained base | `cc_opportunity` is the strongest pruned family. |
| `best + cc_opportunity` additive probe | 0.619652 | Strong global raw candidate; improves Q1/S1/S2 together. |
| all-specialist nested selector with chain candidates | 0.623695 | Automatic selector over-switches; not a global adoption rule. |
| fixed conservative map: Q1/S1/S2 opportunity + S4 chain interactions | 0.614468 | Large diagnostic improvement over prior `0.617333`. |
| fixed bold map: conservative + Q3 recovery | 0.614213 | Best diagnostic decoder in this 300-idea track so far. |

Target-specific reads:

| family | useful target | read |
| --- | --- | --- |
| `best_plus_cc_opportunity` | Q1/S1/S2 | The same sleep-opportunity bottleneck improves sleep quality, S1, and S2 together. This is stronger than treating each sleep target as unrelated. |
| `best_plus_cc_recovery` | Q3 raw | Q3 recovery replacement improves raw OOF, but nested selector did not fully confirm it. Treat bold Q3 as a breakthrough candidate, not a stable conclusion. |
| `best_plus_cc_chain_interactions` | S4 | Chain interactions slightly beat routine regularity for S4 in the fixed map. |
| S3 | none | S3 still resists every chain variant; keep it on the base late-fusion source. |

### Working Interpretation

This is the clearest support so far for the user's Encoder-Decoder framing. The useful latent is not "more features"; it is a structured daily state vector. A compact causal chain over load, arousal, sleep opportunity, continuity, and recovery gives the decoder a better intermediate state than flat sensor totals.

The target map is updated:

- Q1: best latent plus sleep-opportunity causal chain.
- Q2: energy recovery slope / daytime restoration.
- Q3: bold candidate uses causal-chain recovery; conservative map keeps mobility constriction.
- S1: best latent plus sleep-opportunity causal chain.
- S2: best latent plus sleep-opportunity causal chain, replacing digital phone fragmentation.
- S3: base late-fusion source.
- S4: best latent plus causal-chain interactions.

## 2026-05-22 - Ambient / Coverage / Day-State Motif Probe

### Scope

Tested the next S1/S3-oriented data-engineering hypothesis after sleep timing and recovery features were not enough:

- Ambient and light stability as sleep-environment/context signals.
- Sensor coverage, no-wear, low-coverage, and missing-run semantics as intentional behavior rather than simple NaN noise.
- Unsupervised day-state motifs built from 30-minute light, ambience, coverage, phone, and movement states.
- Subject-relative motif distance and rolling changes over 3/7/14/28-day windows.

### Artifacts

- Builder: `scripts/build_ambient_coverage_motif_latents.py`
- Pruned variant builder: `scripts/build_ambient_coverage_motif_pruned_variants.py`
- Full artifact: `artifacts/domain_ambient_coverage_motif_v1.parquet`
- Pruned artifacts:
  - `artifacts/domain_ambient_coverage_motif_ambient_light_v1.parquet`
  - `artifacts/domain_ambient_coverage_motif_coverage_no_wear_v1.parquet`
  - `artifacts/domain_ambient_coverage_motif_motif_distance_v1.parquet`
  - `artifacts/domain_ambient_coverage_motif_night_environment_v1.parquet`
  - `artifacts/domain_ambient_coverage_motif_coverage_rhythm_v1.parquet`
- Probe reports:
  - `outputs/domain_ambient_coverage_motif_probe_v1/report.md`
  - `outputs/domain_ambient_coverage_motif_pruned_probe_v1/report.md`
- Nested selection report: `outputs/domain_all_specialists_plus_ambient_coverage_motif_pruned_nested_selection_v1/report.md`
- Materialized decoder stress: `outputs/domain_hybrid_plus_ambient_coverage_motif_decoder_v1/report.md`

### Result

| experiment | avg OOF logloss | read |
| --- | ---: | --- |
| broad ambient/coverage/motif family | 0.623192 best remained base | Broad 1,707-feature block is too noisy as a global latent. |
| pruned ACM family probe | 0.623192 best remained base | Mean probe finds local target signal but no global win. |
| nested all-specialist selection with pruned ACM | 0.623246 | No stable overall gain; ACM mostly rejected by fold-safe selection. |
| materialized decoder with ACM candidates included | 0.623065 | Worse than the prior fixed hybrid `0.618005`; do not promote. |

Target-specific reads:

| family | raw/local signal | nested read |
| --- | --- | --- |
| `acm_coverage_no_wear` | Q1 improves to about `0.6660`; S4 improves to about `0.6392` in mean probe. | Not selected consistently once stronger digital-boundary/routine candidates are present. |
| `acm_night_environment` | Q3 improves to about `0.6655` in mean probe. | Mobility constriction remains the stable Q3 family. |
| `acm_ambient_light` | Tiny S2 raw signal around `0.5781`. | Too small and unstable versus sleep-intrusion/routine branches. |
| motif distance | Some Q1 local signal. | Not stable enough to enter the decoder. |
| S1/S3 | No material improvement. | Still open; current best remains base/best-late-fusion for S3 and weak routine/base behavior for S1. |

### Working Interpretation

This closes one tempting branch: missingness/coverage is useful context, but in the current formulation it behaves more like an auxiliary regularity signal than the missing S1/S3 key. The broad ACM block also reinforces the feature-pruning lesson: adding all context features makes the latent noisier, while only a few narrow feature families carry target-specific information.

The target map stays unchanged:

- Q1: pre-bed digital boundary behavior.
- Q2: energy recovery slope / daytime restoration.
- Q3: mobility constriction/location entropy state.
- S2: sleep intrusion/coverage episodes.
- S4: routine regularity/circadian phase break.
- S1/S3: still open.

## 2026-05-22 - Chronotype / Sleep Debt / Social Jetlag Probe

### Scope

Tested the next S1/S3-oriented sleep-domain hypothesis set from the 300-idea manifest:

- Sleep-to-sleep interval instead of calendar-day alignment.
- Social jetlag and chronotype drift.
- Rolling sleep debt and irregularity debt.
- Post-wake energy recovery after the sleep episode.
- Pre-bed arousal and post-wake digital behavior as separated controls.

### Artifacts

- Builder: `scripts/build_chronotype_sleep_debt_latents.py`
- Pruned variant builder: `scripts/build_chronotype_sleep_debt_pruned_variants.py`
- Full artifact: `artifacts/domain_chronotype_sleep_debt_v1.parquet`
- Pruned artifacts:
  - `artifacts/domain_chronotype_sleep_debt_sleep_to_sleep_v1.parquet`
  - `artifacts/domain_chronotype_sleep_debt_phase_social_jetlag_v1.parquet`
  - `artifacts/domain_chronotype_sleep_debt_debt_ledger_v1.parquet`
  - `artifacts/domain_chronotype_sleep_debt_postwake_energy_v1.parquet`
  - `artifacts/domain_chronotype_sleep_debt_postwake_digital_v1.parquet`
  - `artifacts/domain_chronotype_sleep_debt_prebed_arousal_v1.parquet`
- Probe reports:
  - `outputs/domain_chronotype_sleep_debt_probe_v1/report.md`
  - `outputs/domain_chronotype_sleep_debt_pruned_probe_v1/report.md`
- Nested selection reports:
  - `outputs/domain_all_specialists_plus_chronotype_sleep_debt_nested_selection_v1/report.md`
  - `outputs/domain_all_specialists_plus_chronotype_pruned_nested_selection_v1/report.md`

### Result

| experiment | avg OOF logloss | read |
| --- | ---: | --- |
| broad chronotype/sleep-debt family | 0.625974 best family avg | Raw S2/S4 hints, but global block is weaker than the current best latent. |
| pruned `cs_debt_ledger` Q2 raw | Q2 0.690408 | Strong raw Q2 signal, but not stable enough to beat trajectory prototype under nested selection. |
| pruned `cs_phase_social_jetlag` S4 raw | S4 0.642169 | Weak raw S4 signal, but routine regularity remains the more stable S4 expert. |
| nested all-specialist selection with broad chronotype | 0.624955 | Worse than base; S2 over-switching is harmful. |
| nested all-specialist selection with pruned chronotype | 0.623746 | Better than broad, but still worse than the established fixed target map. |

Nested target reads:

| family | useful nested target | read |
| --- | --- | --- |
| chronotype_debt_ledger | Q2 raw only | Selected in 3/5 folds but held-fold Q2 worsens by +0.0027; do not replace trajectory prototype. |
| chronotype_phase_social_jetlag | S4 raw only | Raw S4 is close to base, but nested selector keeps routine regularity. |
| sleep_to_sleep / postwake_energy / postwake_digital / prebed_arousal | none | No stable S1/S3 breakthrough. |

### Working Interpretation

This experiment falsifies a tempting assumption: sleep-to-sleep alignment and debt ledgers are domain-plausible, but in this dataset they do not solve S1/S3. The useful part is narrower:

- Rolling sleep debt may be useful as an auxiliary Q2 context, but current Q2 is still better represented by trajectory prototype/state membership.
- Social jetlag/phase drift overlaps with routine regularity and does not replace it.
- S1/S3 likely need a different kind of signal than sleep timing, sleep debt, or post-wake recovery.

The target map stays unchanged:

- Q1: pre-bed digital boundary behavior.
- Q2: trajectory prototype/state membership.
- Q3: mobility constriction/location entropy state.
- S2: sleep intrusion/coverage episodes.
- S4: routine regularity/circadian phase break.
- S1/S3: still open.

## 2026-05-22 - Energy Fragmentation / Recovery Slope Probe

### Scope

Moved away from sleep timing after chronotype/debt failed to solve S1/S3. This cycle tested non-sleep-timing daytime hypotheses:

- Physical energy phase and peak timing.
- Daytime activity fragmentation and micro-bouts.
- Commute stress and stop-go passive movement.
- Previous-day load followed by low morning recovery.
- Digital-energy coupling: phone/screen phase versus physical energy phase.

### Artifacts

- Builder: `scripts/build_energy_fragmentation_latents.py`
- Pruned variant builder: `scripts/build_energy_fragmentation_pruned_variants.py`
- Full artifact: `artifacts/domain_energy_fragmentation_v1.parquet`
- Pruned artifacts:
  - `artifacts/domain_energy_fragmentation_energy_phase_v1.parquet`
  - `artifacts/domain_energy_fragmentation_daytime_fragmentation_v1.parquet`
  - `artifacts/domain_energy_fragmentation_commute_stress_v1.parquet`
  - `artifacts/domain_energy_fragmentation_recovery_slope_v1.parquet`
  - `artifacts/domain_energy_fragmentation_digital_energy_coupling_v1.parquet`
- Probe reports:
  - `outputs/domain_energy_fragmentation_probe_v1/report.md`
  - `outputs/domain_energy_fragmentation_pruned_probe_v1/report.md`
- Nested selection report: `outputs/domain_all_specialists_plus_energy_fragmentation_pruned_nested_selection_v1/report.md`
- Hybrid decoder: `outputs/domain_hybrid_q1_prebed_q2_energy_recovery_q3_mobility_s2_sleep_s4_routine_decoder_v1/report.md`

### Result

| experiment | avg OOF logloss | read |
| --- | ---: | --- |
| previous best domain hybrid: Q1 prebed + Q2 proto + Q3 mobility + S2 sleep + S4 routine | 0.619106 | Previous best diagnostic decoder. |
| broad energy-fragmentation family | 0.622961 best remained base | Broad block has target-specific signal but is not globally better. |
| pruned `ef_recovery_slope` standalone | 0.624117 | Strong target-specific Q2/Q3/S2 raw signal but global average is hurt by S1/S3. |
| nested all-specialist selection with pruned energy family | 0.622029 | Positive nested result driven by Q2 recovery slope. |
| new fixed hybrid: Q1 prebed + Q2 energy recovery + Q3 mobility + S2 sleep + S4 routine | 0.618005 | New best diagnostic decoder in this 300-idea track. |

Nested target reads:

| family | useful nested target | read |
| --- | --- | --- |
| energy_recovery_slope | Q2 | Selected in all five folds; Q2 improves by -0.0145 vs base and beats trajectory prototype in the fixed hybrid. |
| energy_recovery_slope | Q3/S2 raw only | Raw Q3/S2 probes are strong, but established mobility and sleep-intrusion paths remain better under fixed target mapping. |
| digital_energy_coupling | S4 raw only | Raw S4 improves to about 0.6400, but nested selection keeps routine regularity. |
| energy_phase/daytime_fragmentation/commute_stress | none yet | No stable S1/S3 breakthrough. |

### Working Interpretation

This is the strongest new signal since the Q1 pre-bed digital boundary result. Q2 is not only a trajectory/prototype state; it is even better explained by the day-after/daytime recovery axis: previous load, morning recovery, workday energy, and physical/digital energy slope. The breakthrough is target-specific, not global.

The target map is updated:

- Q1: pre-bed digital boundary behavior.
- Q2: energy recovery slope / daytime restoration.
- Q3: mobility constriction/location entropy state.
- S2: sleep intrusion/coverage episodes.
- S4: routine regularity/circadian phase break.
- S1/S3: still open.

## 2026-05-22 - Sleep-Onset Transition / Charging-Settle Probe

### Scope

Targeted the remaining S3 gap by moving from coarse sleep totals to the behavioral transition immediately before sleep onset. The hypothesis was that S3 is sensitive to whether the day cleanly settles into sleep: last phone/movement/bright-light timing, shutdown slope, prebed fragmentation, and charging/dark/still consensus.

### Artifacts

- Builder: `scripts/build_sleep_onset_transition_latents.py`
- Pruned variant builder: `scripts/build_sleep_onset_transition_pruned_variants.py`
- Best-additive builder: `scripts/build_sleep_onset_transition_plus_best_latents.py`
- Full artifact: `artifacts/domain_sleep_onset_transition_v1.parquet`
- Pruned artifacts:
  - `artifacts/domain_sleep_onset_transition_last_event_latency_v1.parquet`
  - `artifacts/domain_sleep_onset_transition_shutdown_slope_v1.parquet`
  - `artifacts/domain_sleep_onset_transition_prebed_fragmentation_v1.parquet`
  - `artifacts/domain_sleep_onset_transition_light_environment_transition_v1.parquet`
  - `artifacts/domain_sleep_onset_transition_charging_settle_v1.parquet`
  - `artifacts/domain_sleep_onset_transition_onset_consensus_v1.parquet`
- Additive artifacts:
  - `artifacts/domain_best_plus_sleep_onset_transition_charging_settle_v1.parquet`
  - `artifacts/domain_best_plus_sleep_onset_transition_onset_consensus_v1.parquet`
  - other `domain_best_plus_sleep_onset_transition_*_v1.parquet` slices
- Probe reports:
  - `outputs/domain_sleep_onset_transition_probe_v1/report.md`
  - `outputs/domain_sleep_onset_transition_pruned_probe_v1/report.md`
  - `outputs/domain_sleep_onset_transition_plus_best_probe_v1/report.md`
- Nested/all-specialist diagnostics:
  - `outputs/domain_all_specialists_plus_sleep_onset_transition_additive_probe_v1/report.json`
  - `outputs/domain_all_specialists_plus_sleep_onset_transition_additive_nested_selection_v1/report.md`
- Fixed hybrid decoder:
  - `outputs/domain_hybrid_causal_chain_plus_s3_onset_transition_v1/report.md`

### Result

| experiment | avg OOF logloss | read |
| --- | ---: | --- |
| previous causal-chain fixed hybrid, with S3 on base | 0.614213 | Previous best broad diagnostic decoder. |
| full sleep-onset-transition family | 0.623192 best remained base | Too broad; full block blurs the useful S3/S4 axes. |
| pruned `sot_charging_settle` standalone | 0.624+ avg, S3 0.524789 | Narrow S3 hint beats base S3 0.525120. |
| additive `best_plus_sot_charging_settle` | 0.621+ avg, S3 0.515386 | Strong S3 complement once attached to the best late-fusion latent. |
| all-specialist nested selection | 0.619637 vs base 0.623192 | S3 selects sleep-onset charging in 4/5 folds; S4 onset-consensus is less stable. |
| fixed hybrid with S3 replaced by charging-settle | 0.612828 | New best diagnostic decoder in this 300-idea/domain track. |

Per-target change in the fixed hybrid:

| target | previous | new | read |
| --- | ---: | ---: | --- |
| Q1 | 0.654835 | 0.654835 | unchanged causal-chain opportunity |
| Q2 | 0.687527 | 0.687527 | unchanged energy recovery slope |
| Q3 | 0.665238 | 0.665238 | unchanged causal-chain recovery |
| S1 | 0.563862 | 0.563862 | unchanged causal-chain opportunity |
| S2 | 0.568897 | 0.568897 | unchanged causal-chain opportunity |
| S3 | 0.523927 | 0.514231 | new charging-settle transition signal |
| S4 | 0.635204 | 0.635204 | unchanged causal-chain interactions |

### Working Interpretation

This is the first S3 signal that survives the "add to best latent, then fixed target map" test. The useful feature is not total prebed phone usage. It is narrower: whether the final pre-sleep state becomes dark/still/not-phone/charging, and whether that transition is fragmented.

The target map is updated:

- Q1: causal-chain sleep opportunity / pre-bed boundary state.
- Q2: energy recovery slope / daytime restoration.
- Q3: causal-chain recovery or mobility constriction state.
- S1: causal-chain sleep opportunity.
- S2: causal-chain sleep opportunity.
- S3: sleep-onset charging/settling transition.
- S4: causal-chain interactions, with onset-consensus as a secondary raw candidate.

## 2026-05-22 - S3 Sleep-Onset Micro Ablation

### Scope

The previous cycle showed that `charging_settle` is the first S3-positive sleep-onset family. This cycle split that 126-feature family into smaller units to identify whether the signal is absolute charging, final-hour settling, phone/charging conflict, rolling readiness, or subject-relative deviation.

### Artifacts

- Micro variant builder: `scripts/build_sleep_onset_transition_micro_variants.py`
- Micro artifacts:
  - `artifacts/domain_sleep_onset_transition_micro_charging_timing_v1.parquet`
  - `artifacts/domain_sleep_onset_transition_micro_charging_windows_v1.parquet`
  - `artifacts/domain_sleep_onset_transition_micro_settled_no_phone_v1.parquet`
  - `artifacts/domain_sleep_onset_transition_micro_settled_charging_v1.parquet`
  - `artifacts/domain_sleep_onset_transition_micro_phone_charging_conflict_v1.parquet`
  - `artifacts/domain_sleep_onset_transition_micro_readiness_rolling_v1.parquet`
  - `artifacts/domain_sleep_onset_transition_micro_base_values_only_v1.parquet`
  - `artifacts/domain_sleep_onset_transition_micro_subject_relative_only_v1.parquet`
  - `artifacts/domain_sleep_onset_transition_micro_rolling_context_only_v1.parquet`
  - `artifacts/domain_sleep_onset_transition_micro_s3_core_timing_settle_conflict_v1.parquet`
  - `artifacts/domain_sleep_onset_transition_micro_s3_final_hour_core_v1.parquet`
- Probe reports:
  - `outputs/domain_sleep_onset_transition_micro_probe_v1/report.md`
  - `outputs/domain_sleep_onset_transition_micro_plus_best_probe_v2/report.md`
- Nested/all-specialist report:
  - `outputs/domain_all_specialists_plus_sleep_onset_micro_nested_selection_v1/report.md`
- Fixed hybrid decoder:
  - `outputs/domain_hybrid_causal_chain_plus_s3_onset_subject_relative_v1/report.md`

### Result

| experiment | S3 OOF logloss | avg OOF logloss | read |
| --- | ---: | ---: | --- |
| previous base S3 inside fixed hybrid | 0.523927 | 0.614213 | Causal-chain fixed hybrid before SOT replacement. |
| coarse `charging_settle` replacement | 0.514231 | 0.612828 | Strong first S3 path. |
| micro `subject_relative_only` replacement | 0.512376 | 0.612563 | New best; S3 signal is mostly subject-relative settling deviation. |

Micro probe reads:

| family | S3 read |
| --- | --- |
| `subject_relative_only` | Best S3 probe, `0.513590`; selected in 4/5 nested folds. |
| `base_values_only` | Also strong, `0.514613`, but slightly weaker than subject-relative. |
| `s3_core_timing_settle_conflict` | Recovers most of the signal at `0.515094`. |
| `charging_timing` | Useful but incomplete, `0.518959`. |
| `phone_charging_conflict` | Useful but incomplete, `0.519923`. |
| `settled_no_phone` | Useful but incomplete, `0.520589`. |

### Working Interpretation

S3 is not just "phone was charging" or "phone stopped." The sharper statement is:

> S3 responds to whether the sleep-onset settling pattern is unusual for that subject.

The best micro slice is made from subject-relative versions of charging/settling/readiness/conflict features, which aligns with the label definition: labels are relative to the person's own average state. This makes S3 a clean example of the broader lesson from the 300-idea track: the right data engineering is often not more sensors, but the right coordinate system.

The current best diagnostic decoder is now:

- Q1: causal-chain opportunity.
- Q2: energy recovery slope.
- Q3: causal-chain recovery.
- S1: causal-chain opportunity.
- S2: causal-chain opportunity.
- S3: subject-relative sleep-onset settling.
- S4: causal-chain interactions.

## 2026-05-22 - S1 Wake Activation/Inertia Ablation

### Scope

The next unresolved sleep target was S1. Earlier postwake totals, broad sleep-debt ledgers, and fatigue carry-over features produced raw hints but did not survive nested selection. This cycle tested a narrower wake-anchored hypothesis: S1 may respond to whether a person's sleep amount/efficiency/fragmentation is followed by unusually fast or slow morning activation.

### Artifacts

- Feature builder: `scripts/build_wake_activation_inertia_latents.py`
- Variant builder: `scripts/build_wake_activation_inertia_variants.py`
- Main latent:
  - `artifacts/domain_wake_activation_inertia_v1.parquet`
- Additive/pruned latents:
  - `artifacts/domain_best_plus_wake_activation_inertia_activation_latency_v1.parquet`
  - `artifacts/domain_best_plus_wake_activation_inertia_activation_slope_v1.parquet`
  - `artifacts/domain_best_plus_wake_activation_inertia_phone_inertia_v1.parquet`
  - `artifacts/domain_best_plus_wake_activation_inertia_light_hr_entrainment_v1.parquet`
  - `artifacts/domain_best_plus_wake_activation_inertia_sleep_recovery_interaction_v1.parquet`
  - `artifacts/domain_best_plus_wake_activation_inertia_subject_relative_only_v1.parquet`
  - `artifacts/domain_best_plus_wake_activation_inertia_rolling_context_only_v1.parquet`
  - `artifacts/domain_best_plus_wake_activation_inertia_base_values_only_v1.parquet`
- Probe reports:
  - `outputs/domain_wake_activation_inertia_probe_v1/report.md`
  - `outputs/domain_wake_activation_inertia_plus_best_probe_v1/report.md`
- Nested/all-specialist diagnostics:
  - `outputs/domain_all_specialists_plus_wake_activation_inertia_probe_v1/report.md`
  - `outputs/domain_all_specialists_plus_wake_activation_inertia_nested_selection_v1/report.md`
- Fixed hybrid decoder:
  - `outputs/domain_hybrid_plus_s1_wake_activation_s3_onset_subject_relative_v1/report.md`

### Result

| experiment | S1 OOF logloss | avg OOF logloss | read |
| --- | ---: | ---: | --- |
| previous fixed hybrid S1 | 0.563862 | 0.612563 | S1 still used causal-chain opportunity. |
| additive `sleep_recovery_interaction` probe | 0.557111 | 0.618903 | Best WAI probe; global avg still weak, but S1 is clean. |
| nested all-specialist selection | 0.564710 | 0.617810 | S1 selects wake sleep-recovery interaction in 4/5 folds and improves base by `-0.006186`. |
| fixed hybrid with S1 replaced by WAI sleep-recovery interaction | 0.557111 | 0.611598 | New best diagnostic decoder in this track. |

Per-target fixed hybrid read:

| target | OOF logloss | source |
| --- | ---: | --- |
| Q1 | 0.654835 | causal-chain opportunity |
| Q2 | 0.687527 | energy recovery slope |
| Q3 | 0.665238 | causal-chain recovery |
| S1 | 0.557111 | wake activation sleep-recovery interaction |
| S2 | 0.568897 | causal-chain opportunity |
| S3 | 0.512376 | subject-relative sleep-onset settling |
| S4 | 0.635204 | causal-chain interactions |

### Working Interpretation

This is different from the failed postwake-total features. The positive S1 slice is an interaction family: short/long sleep, efficiency, and fragmentation are multiplied by wake latency, early phone/move/light/HR activation, and subject-relative morning inertia. The model is not rewarded for "more morning activity"; it is rewarded for the mismatch between recovery quality and the next waking activation pattern.

The current target map is updated:

- Q1: causal-chain sleep opportunity / pre-bed boundary state.
- Q2: energy recovery slope / daytime restoration.
- Q3: causal-chain recovery or mobility constriction state.
- S1: wake activation relative to sleep recovery state.
- S2: causal-chain sleep opportunity.
- S3: subject-relative final transition into sleep.
- S4: causal-chain interactions.

## 2026-05-22 - S2/S4 Sleep Consensus Purity Scout

### Scope

Ambient/coverage features were too broad and produced unstable S2/S4 moves. This cycle narrowed the hypothesis to sleep-window internal structure: cross-modal quiet-sleep consensus, micro-awakening conflicts, and whether missingness looks like real sleep quietness or device-off conflict.

### Artifacts

- Feature builder: `scripts/build_sleep_consensus_purity_latents.py`
- Variant builder: `scripts/build_sleep_consensus_purity_variants.py`
- Main latent:
  - `artifacts/domain_sleep_consensus_purity_v1.parquet`
- Pruned latent variants:
  - `artifacts/domain_sleep_consensus_purity_consensus_purity_v1.parquet`
  - `artifacts/domain_sleep_consensus_purity_micro_awakenings_v1.parquet`
  - `artifacts/domain_sleep_consensus_purity_missingness_semantics_v1.parquet`
  - `artifacts/domain_sleep_consensus_purity_final_sleep_quality_v1.parquet`
  - `artifacts/domain_sleep_consensus_purity_prebed_conflict_v1.parquet`
  - `artifacts/domain_sleep_consensus_purity_sleep_metric_interaction_v1.parquet`
  - `artifacts/domain_sleep_consensus_purity_subject_relative_only_v1.parquet`
  - `artifacts/domain_sleep_consensus_purity_rolling_context_only_v1.parquet`
  - `artifacts/domain_sleep_consensus_purity_base_values_only_v1.parquet`
- Probe reports:
  - `outputs/domain_sleep_consensus_purity_probe_v1/report.md`
  - `outputs/domain_all_specialists_plus_sleep_consensus_purity_probe_v1/report.md`
  - `outputs/domain_all_specialists_plus_sleep_consensus_purity_nested_selection_v1/report.md`
- Fixed scout decoder:
  - `outputs/domain_hybrid_probe_s2s4_sleep_consensus_purity_v1/report.md`

### Result

| experiment | S2 OOF logloss | S4 OOF logloss | avg OOF logloss | read |
| --- | ---: | ---: | ---: | --- |
| previous protected hybrid | 0.568897 | 0.635204 | 0.611598 | S2/S4 still used causal-chain sources. |
| raw SCP target-wise best | 0.567195 | 0.633287 | n/a | Subject-relative sleep-consensus variants beat the protected S2/S4 sources on full OOF. |
| nested all-specialist selection | 0.574130 | 0.640534 | 0.617662 | Beats late-fusion base, but not the current protected hybrid reliably. |
| fixed scout replacing S2/S4 with SCP subject-relative sources | 0.566343 | 0.633149 | 0.610940 | New best diagnostic OOF, but marked as scout because S2/S4 source selection is less nested-stable than S1/S3. |

### Working Interpretation

S2/S4 do contain sleep-window consensus signal, but the stable unit is not yet as clean as S1 wake activation or S3 onset settling. The promising coordinate is subject-relative sleep purity/micro-conflict: whether the sleep interval has unusual quiet consensus, short phone/motion/bright interruptions, and missingness that behaves like real sleep rather than device-off conflict.

This should not be treated as a submission-stable replacement yet. It is a strong encoder-objective clue: train a sleep-window encoder to reconstruct/contrast `quiet consensus -> micro-conflict -> final purity` rather than appending thousands of raw SCP columns to a logistic probe.

## 2026-05-22 - Compact Sleep Consensus Objective Scout

### Scope

The first SCP scout used 1,588 raw/derived columns and improved S2/S4 full-OOF, but nested selection showed instability. This cycle compressed SCP into a compact objective view: only consensus purity, micro-awakening, missingness semantics, device-off conflict, final-vs-first sleep phase shifts, subject-relative coordinates, and 7/14-day rolling deltas.

### Artifacts

- Compact builder: `scripts/build_sleep_consensus_compact_latents.py`
- Compact artifacts:
  - `artifacts/domain_sleep_consensus_compact_core_v1.parquet`
  - `artifacts/domain_sleep_consensus_compact_subject_relative_v1.parquet`
  - `artifacts/domain_sleep_consensus_compact_rolling_v1.parquet`
  - `artifacts/domain_sleep_consensus_compact_all_v1.parquet`
  - matching `domain_best_plus_sleep_consensus_compact_*_v1.parquet` additive variants
- Probe reports:
  - `outputs/domain_sleep_consensus_compact_probe_v1/report.md`
  - `outputs/domain_sleep_consensus_compact_plus_best_probe_v1/report.md`
  - `outputs/domain_all_specialists_plus_sleep_consensus_compact_probe_v1/report.md`
  - `outputs/domain_all_specialists_plus_sleep_consensus_compact_nested_selection_v1/report.md`
- Fixed scout decoder:
  - `outputs/domain_hybrid_probe_q2_compact_s2s4_sleep_consensus_v1/report.md`

### Result

| experiment | Q2 OOF logloss | S2 OOF logloss | S4 OOF logloss | avg OOF logloss | read |
| --- | ---: | ---: | ---: | ---: | --- |
| previous SCP scout hybrid | 0.687527 | 0.566343 | 0.633149 | 0.610940 | S2/S4 from high-dimensional SCP subject-relative sources. |
| compact additive probe best | 0.682062 | 0.571382 | 0.639865 | 0.620983 | Compact rolling is globally stronger than late-fusion and exposes a Q2 path. |
| nested all-specialist selection | 0.699626 | 0.574130 | 0.640534 | 0.617784 | Q2 selects compact rolling in 3/5 folds; still not stable enough as a final rule. |
| fixed scout replacing Q2 with compact rolling | 0.682902 | 0.566343 | 0.633149 | 0.610279 | New best diagnostic OOF, but marked as scout due Q2 nested instability. |

### Working Interpretation

Compressing SCP did not stabilize S2/S4, but it revealed a different signal: Q2 responds to rolling sleep-consensus change. This is behaviorally plausible because Q2 is close to fatigue/restoration before sleep; the compact rolling view captures whether recent sleep-window purity and micro-conflict are improving or worsening.

The current scout target map is:

- Q1: causal-chain opportunity.
- Q2: compact rolling sleep-consensus.
- Q3: causal-chain recovery.
- S1: wake activation relative to sleep recovery.
- S2: subject-relative sleep-consensus purity scout.
- S3: subject-relative sleep-onset settling.
- S4: subject-relative sleep-consensus purity scout.

The stable lesson is now sharper: the encoder should learn boundary-specific state transitions, but each target wants a different boundary coordinate. S1 wants wake-start recovery mismatch, S3 wants final sleep-onset settling, and Q2 may want rolling sleep-consensus trajectory.

## 2026-05-22 - Boundary Objective Target-Map Scout

### Scope

Combined the current specialist target map into one encoder-ready latent objective. The goal was not to append more raw columns, but to test whether the encoder should preserve a shared set of biologically meaningful boundary coordinates: Q1 sleep opportunity, Q2 rolling sleep-consensus, Q3 recovery/mobility, S1 wake activation after sleep recovery, S3 sleep-onset settling, and compact sleep-consensus coordinates.

### Artifacts

- Combined latent: `artifacts/domain_boundary_objective_target_map_v1.parquet`
- Frozen probe: `outputs/domain_boundary_objective_probe_v1/report.md`
- All-specialist merge: `outputs/domain_all_specialists_plus_boundary_objective_probe_v1/fold_target_losses.csv`
- Nested diagnostic: `outputs/domain_all_specialists_plus_boundary_objective_nested_selection_v1/report.md`
- Full nested materialization: `outputs/domain_hybrid_boundary_objective_nested_decoder_v1/report.md`
- Protected Q1-only swap: `outputs/domain_hybrid_q1_boundary_swap_decoder_v1/report.md`

### Result

| experiment | Q1 OOF logloss | avg OOF logloss | read |
| --- | ---: | ---: | --- |
| previous fixed scout hybrid | 0.654835 | 0.610279 | Q1 still used causal-chain opportunity. |
| boundary target-map frozen probe | 0.655171 | 0.617752 | Better than `best` inside the same probe, but worse than the target-specialist hybrid. |
| nested all-specialist + boundary selector | 0.654854 | 0.618892 | Boundary is selected for Q1 in 5/5 held folds, but unrestricted selection destabilizes Q2/S2/S4. |
| materialized unrestricted nested decoder | 0.654680 | 0.618663 | Confirms broad re-selection is too noisy. |
| protected Q1 boundary swap | 0.654680 | 0.610257 | Small new best diagnostic OOF by replacing only Q1 while keeping the protected scout map. |

### Working Interpretation

This is a narrow but useful encoder-objective signal. The unified boundary latent is not a better global feature block; it washes out target specialization. However, its Q1 coordinate is cleaner than the prior causal-chain opportunity readout and survives 5/5 nested folds. Carry it forward as a Q1 objective, not as a monolithic replacement for the specialist map.

The updated scout target map is:

- Q1: boundary target-map absolute coordinate.
- Q2: compact rolling sleep-consensus.
- Q3: causal-chain recovery.
- S1: wake activation relative to sleep recovery.
- S2: subject-relative sleep-consensus purity scout.
- S3: subject-relative sleep-onset settling.
- S4: subject-relative sleep-consensus purity scout.

## 2026-05-22 - Sleep Consensus Stability PCA

### Scope

Tested whether the unstable high-dimensional S2/S4 sleep-consensus scout could be stabilized by label-free compression. The source pool concatenates SCP subject-relative purity, compact subject-relative consensus, and compact rolling consensus into a 1,188-dimensional unlabeled sleep-consensus table, then compresses it with PCA to 16/32/64 dimensions before probing.

### Artifacts

- PCA compressor: `scripts/compress_latent_pca.py`
- Stability pool: `artifacts/domain_sleep_consensus_stability_pool_v1.parquet`
- PCA artifacts:
  - `artifacts/domain_sleep_consensus_stability_pca16_v1.parquet`
  - `artifacts/domain_sleep_consensus_stability_pca32_v1.parquet`
  - `artifacts/domain_sleep_consensus_stability_pca64_v1.parquet`
  - matching `domain_best_plus_sleep_consensus_stability_pca*_v1.parquet` additive variants
- Probe report: `outputs/domain_sleep_consensus_stability_pca_probe_v1/report.md`
- Nested report: `outputs/domain_all_specialists_plus_sleep_consensus_stability_pca_nested_selection_v1/report.md`

### Result

| experiment | S2 OOF logloss | S4 OOF logloss | avg OOF logloss | read |
| --- | ---: | ---: | ---: | --- |
| current fixed scout hybrid | 0.566343 | 0.633149 | 0.610257 | Protected target map after Q1 boundary swap. |
| best PCA global probe | 0.569041 | 0.643920 | 0.622164 | PCA32 additive improves over `best` globally, but loses most S4 signal. |
| best PCA S2 source | 0.567009 | n/a | 0.623724 | PCA64 deviation is close to raw SCP S2, but not better. |
| best PCA S4 source | n/a | 0.634510 | 0.623389 | PCA64 additive is close to raw SCP S4, but still worse than current scout S4. |
| nested all-specialist + PCA | 0.574130 | 0.645007 | 0.617892 | PCA is selected for S4 in only 1/5 folds and harms held-fold S4. |

### Working Interpretation

Label-free PCA compression reduces dimensionality but does not solve the S2/S4 stability problem. The S2 signal is not just "low-rank sleep consensus"; nested selection still prefers raw micro-awakening and subject-relative purity slices. S4 remains the harder target: raw SCP is strong in full OOF, PCA is close, but neither survives protected/nested selection cleanly.

Carry forward:

- S2: split sleep consensus into micro-awakening vs subject-relative purity objectives rather than compressing them together.
- S4: look beyond sleep-consensus PCA; the target likely needs routine/circadian phase break or night-fragmentation episode structure, not a generic low-rank sleep-purity coordinate.

## 2026-05-22 - S4 Routine Fragment Interaction Scout

### Scope

After PCA failed to stabilize S4, tested a more explicit S4 hypothesis: routine/circadian disruption should matter most when the night also contains sleep-window fragmentation or pre-bed conflict. The builder combines routine regularity, event rhythm, sleep fragmentation/recovery, and pre-bed fragmentation sources, then emits block summaries plus label-free interaction products.

### Artifacts

- Builder: `scripts/build_s4_routine_fragment_latents.py`
- Interaction latent: `artifacts/domain_s4_routine_fragment_v1.parquet`
- Additive latent: `artifacts/domain_best_plus_s4_routine_fragment_v1.parquet`
- Probe report: `outputs/domain_s4_routine_fragment_probe_v1/report.md`
- Nested report: `outputs/domain_all_specialists_plus_s4_routine_fragment_nested_selection_v1/report.md`

### Result

| experiment | S2 OOF logloss | S4 OOF logloss | avg OOF logloss | read |
| --- | ---: | ---: | ---: | --- |
| routine regularity standalone best S4 | n/a | 0.634259 | n/a | Prior strongest clean S4 family. |
| event rhythm best S4 | n/a | 0.638321 | n/a | Stable but weaker S4 path. |
| S4 routine-fragment raw best S4 | n/a | 0.636226 | 0.630103 | Does not beat routine regularity or current SCP S4 scout. |
| S4 routine-fragment raw best S2 | 0.565782 | n/a | 0.632337 | Raw S2 looks better than the current scout, but global fit is poor. |
| nested all-specialist + S4RF | 0.579170 | 0.645007 | 0.618675 | S2 flips harmful out-of-fold; S4 remains unstable. |

### Working Interpretation

This is a negative S4 result. The interaction hypothesis is plausible but not enough: routine break multiplied by night fragmentation does not beat the simpler routine-regularity S4 signal and does not stabilize the current SCP S4 scout. The surprising raw S2 improvement is also not trustworthy because nested held-fold S2 becomes worse than base.

Carry forward only a narrow side clue: the interaction latent is selected for Q3 in 3/5 nested folds with a small held-fold gain, but it is still weaker than the existing mobility/recovery Q3 path. Do not promote this source into the protected target map.

## 2026-05-22 - Routine Regularity Pruned Variant Scout

### Scope

After the broad routine-fragment interaction failed for S4, split the older 252-column routine-regularity latent into compact, domain-readable subfamilies. This tests the user's feature-pruning hypothesis directly: S4 may need a smaller routine/phase coordinate, not more features.

### Variants

| variant | feature count | hypothesis |
| --- | ---: | --- |
| `profile_distance` | 8 | Whole-day profile distance from subject and weekday routine. |
| `phase_shift` | 38 | Circadian and sleep/wake phase displacement. |
| `sleep_regular_break` | 76 | Sleep timing, duration, efficiency, awakening, and rolling sleep-regularity breaks. |
| `routine_state` | 28 | Daily state entropy and transition-count instability. |
| `short_rolling_volatility` | 66 | 3/7-day local routine volatility. |
| `long_rolling_volatility` | 66 | 14/28-day longer routine volatility. |
| `phone_rhythm` | 34 | Phone routine residuals. |
| `mobility_body_rhythm` | 68 | Mobility/body routine residuals. |
| `coverage_rhythm` | 34 | Coverage/no-wear/missingness rhythm residuals. |
| `night_evening_balance` | 16 | Night/evening allocation imbalance. |

### Artifacts

- Builder: `scripts/build_routine_regularity_pruned_variants.py`
- Variant report: `artifacts/domain_routine_regularity_pruned_variants_v1.report.md`
- Probe report: `outputs/domain_routine_regularity_pruned_probe_v1/report.md`
- Merged all-specialist fold losses: `outputs/domain_all_specialists_plus_routine_pruned_probe_v1/fold_target_losses.csv`
- Nested report: `outputs/domain_all_specialists_plus_routine_pruned_nested_selection_v1/report.md`
- Fixed S4-only scout: `outputs/domain_routine_pruned_fixed_map_scout_v1/report.md`

### Result

| experiment | S1 | S2 | S3 | S4 | avg | read |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| best pruned global probe | 0.568087 | 0.574366 | 0.526621 | 0.643253 | 0.620696 | `best_plus_rr_routine_state` is globally best, but S4 is not its strength. |
| best pruned S4 source | n/a | n/a | n/a | 0.632894 | n/a | `best_plus_rr_coverage_rhythm` is the best S4 slice. |
| fixed scout current S4 | 0.557172 | 0.567195 | 0.513590 | 0.633287 | 0.610301 | Current protected scout with SCP S4. |
| fixed scout coverage S4 | 0.557172 | 0.567195 | 0.513590 | 0.632894 | 0.610244 | Replacing only S4 with coverage rhythm gives a tiny full-fold gain. |
| nested all-specialist + pruned routine | 0.569862 | 0.584091 | 0.514926 | 0.642292 | 0.620072 | S4 nested gain is tiny; S2 remains harmful. |

### Working Interpretation

This is not a large breakthrough, but it is a useful pruning result. Broad routine regularity was not one thing: the best S4 clue is specifically coverage/no-wear rhythm, not phone rhythm, mobility/body rhythm, profile distance, or broad interaction products. Sleep-regularity breaks are close for S4 and raw S2, but S2 fails nested validation.

Carry forward:

- S4: build a cleaner coverage/no-wear routine objective around missingness rhythm, sleep boundary coverage, and wearable-off episodes.
- S2: do not reuse the S4 coverage branch as a proxy. Continue with a separate micro-awakening / sleep-fragment objective.
- S1/S3: long rolling volatility and night/evening balance show raw hints, but existing wake-recovery and sleep-onset transition branches remain stronger.

## 2026-05-22 - Sleep Boundary Coverage / No-Wear Objective

### Scope

Followed the routine-pruning clue that S4 might be about coverage/no-wear rhythm. Instead of using the broad daily routine slice, built an explicit sleep-boundary coverage objective around onset/wake windows, no-wear and low-coverage episodes, body-sensor missingness, re-coverage after wake, and subject-relative rolling deltas.

### Artifacts

- Builder: `scripts/build_sleep_boundary_coverage_latents.py`
- Pruned variant builder: `scripts/build_sleep_boundary_coverage_pruned_variants.py`
- Full artifact: `artifacts/domain_sleep_boundary_coverage_v1.parquet`
- Focused probe report: `outputs/domain_sleep_boundary_coverage_focused_probe_v1/report.md`
- Nested report: `outputs/domain_all_specialists_plus_sleep_boundary_coverage_nested_selection_v1/report.md`

### Result

| experiment | S2 | S4 | avg | read |
| --- | ---: | ---: | ---: | --- |
| best focused global probe | 0.577751 | 0.645541 | 0.623313 | No-wear episode append helps global probe slightly, mostly outside S4. |
| best focused S2 source | 0.575801 | n/a | n/a | Boundary re-coverage has a weak S2 hint, still worse than current S2 scout. |
| best focused S4 source | n/a | 0.642681 | n/a | Boundary re-coverage is far worse than routine-pruned coverage rhythm S4 `0.632894`. |
| nested all-specialist + SBC | 0.584091 | 0.642292 | 0.620072 | No SBC source is selected; result is unchanged from the routine-pruned nested run. |

### Working Interpretation

This is a negative but informative follow-up. The S4 coverage clue does not become stronger when expressed as detailed sleep-boundary no-wear/re-coverage episodes. The stronger signal was the coarser daily coverage rhythm residual from routine regularity pruning. This suggests S4 is more about the person's whole-day sensing/coverage rhythm or adherence pattern than about a specific missingness event around sleep onset or wake.

Carry forward:

- S4: keep `rr_coverage_rhythm` as the current narrow clue; next attempt should compress daily coverage rhythm or build weekday/chronotype-normalized coverage prototypes, not add more boundary episode products.
- S2: boundary re-coverage is too weak; continue with micro-awakening / quiet-sleep consensus rather than coverage-only features.
