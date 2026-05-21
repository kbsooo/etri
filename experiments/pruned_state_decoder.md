# Pruned State Decoder Experiments

Last updated: 2026-05-21

## Goal

Use v83 (`0.5997645835` Public LB) as the current score reference, but do not use v76/v83/v85 submissions as teachers. The experiment tests whether an independent Encoder-Decoder route can find breakthrough signal by:

- pruning encoder input feature families instead of adding everything,
- converting the day into subject-normalized latent state features,
- decoding through intermediate state mechanisms: deviation/rank/prototype/residual,
- using v83 only as a drift diagnostic reference.

## Implemented

Script: `scripts/train_pruned_state_decoder.py`

Outputs:

- `outputs/pruned_state_decoder_v1/`
- `outputs/pruned_state_decoder_v2_prior_residual/`
- `outputs/pruned_state_decoder_v3_cap160/`

The script evaluates these encoder input presets:

- `full`
- `no_raw`
- `no_derivative`
- `no_ratio`
- `no_rank`
- `no_missingness`
- `no_temporal_delta`
- `no_gps`
- `no_phone`
- `no_sleep`
- `no_late_pool`
- `only_deviation`
- `only_missingness`
- `only_rhythm`
- `only_cross_modal`

For each preset, it builds a PCA latent, subject-relative deviation, rank-extreme state, and prototype membership. Decoders include logistic, HGB, pairwise ranking, prototype label mixture, residual ridge, and logit residual blends over a fold-safe subject prior.

## Results

### v1: direct state decoder

- Best global: `only_missingness__prototype`
- OOF avg: `0.667821`
- Target-wise OOF avg: `0.649217`
- Drift vs v83 reference: `0.138587` best global, `0.119236` target-wise

Interpretation: independent state decoder without a strong intermediate prior is too weak. It confirms the 450-label bottleneck: direct label decoding from state latents overfits or collapses toward weak prototypes.

### v2: fold-safe subject prior + state residual decoder

- Subject-prior baseline OOF: `0.627413`
- Best global: `only_rhythm__prior_logit_blend_hgb_w20`
- OOF avg: `0.625801`
- Gain vs subject prior: `-0.001612`
- Target-wise OOF avg: `0.617441`
- Drift vs v83 reference: `0.068234` best global, `0.067860` target-wise

Interpretation: the state decoder becomes useful only as a small residual over a strong intermediate state prior. This supports the Decoder redesign hypothesis: the decoder should not predict labels directly; it should transform subject-normalized state into bounded residual corrections.

Feature insight:

- `only_rhythm` is the best global preset.
- `no_derivative`, `no_ratio`, `no_temporal_delta`, and `only_cross_modal` are close.
- Target-wise selection uses different feature families:
  - Q1: `only_missingness`
  - Q2: `no_ratio`
  - Q3: `no_sleep`
  - S1: `only_rhythm`
  - S2: `no_missingness`
  - S3: `only_missingness`
  - S4: `no_rank`

This supports feature-family pruning: useful signal is target-specific, and "full feature" is not the best global preset.

### v3: stronger pruning cap (`max_features=160`)

- Best global: `only_cross_modal__prior_logit_blend_logreg_w03`
- OOF avg: `0.626764`
- Target-wise OOF avg: `0.619789`

Interpretation: pruning too aggressively loses signal. The current best cap is `520`, not `160`. The promising direction is not tiny feature sets; it is removing/isolating harmful families while preserving enough rhythm/deviation/cross-modal coverage.

## Current Decision

Adopt the v2 design as the next Decoder scaffold:

```text
feature-family-pruned Encoder
→ subject-normalized state latent
→ fold-safe subject-state prior
→ small logit residual Decoder
```

Hold off on direct submission from this family. The best OOF is still far behind v83-style public-best candidates, and the target-wise selection is likely optimistic. But the experiment gives a real architectural signal:

- Direct decoder is weak.
- Prior-residual decoder is much stronger.
- `only_rhythm` / `only_cross_modal` / missingness-related families deserve focused encoders.
- Feature pruning should be target-aware, not one global feature set.

## Next Experiment

Train a target-aware pruned residual encoder:

- separate feature-family presets per target based on v2 target-wise selection,
- no submission-teacher inputs,
- same fold-safe subject prior,
- residual decoder with nested target-wise selection to reduce selection bias,
- compare against v2 target-wise `0.617441` and subject-prior `0.627413`.

## Nested target-aware follow-up

Script: `scripts/train_nested_pruned_state_decoder.py`

Output: `outputs/nested_pruned_state_decoder_v1/`

This follow-up uses v2's target-aware candidate families but performs nested selection:

```text
outer fold:
  inner folds select the best source for each target
  selected source is trained on outer-train
  score is measured on outer-val
```

Results:

- Nested target-wise OOF avg: `0.624729`
- Subject-prior baseline from v2: `0.627413`
- Gain vs subject prior: `-0.002684`
- v2 full-OOF target-wise selection: `0.617441`
- Estimated selection optimism in v2 target-wise selection: about `+0.007288`
- Drift vs v83 diagnostic reference: `0.066660`

Per-target nested OOF:

- Q1: `0.670340`
- Q2: `0.685659`
- Q3: `0.672727`
- S1: `0.576165`
- S2: `0.585703`
- S3: `0.537058`
- S4: `0.645454`

Selection stability:

- Q2 is the most stable target: `no_ratio__prior_logit_blend_state_mean_w35` selected in 4/5 outer folds.
- Q1 and S1 often select `only_rhythm__prior_logit_blend_hgb_w20`.
- S2 and S3 frequently fall back to `subject_prior`, so their apparent v2 target-wise gains were partly selection noise.
- S4 has split support between `no_temporal_delta` and `only_cross_modal`.

Decision:

- Keep the target-aware residual decoder direction. It survives nested selection and beats subject prior.
- Do not trust the raw v2 target-wise `0.617441` as a true score; it is a search/selection artifact.
- Next useful experiment is a consensus/frequency-stabilized target decoder:
  - Q2 fixed to `no_ratio + state_mean`.
  - Q1/S1 fixed to `only_rhythm + HGB`.
  - S2/S3 should use a conservative subject-prior gate unless their residual source wins consistently.
  - S4 should compare `no_temporal_delta` vs `only_cross_modal` under fixed selection.

## Hourly Transformer Encoder reset

Script: `scripts/train_hourly_transformer_encoder.py`

Outputs:

- `outputs/hourly_transformer_encoder_v1/`
- `outputs/hourly_transformer_encoder_v1_extra/`
- `outputs/hourly_transformer_cross_view_diagnostic_v1/`

This branch resets the encoder representation around a true sequence shape:

```text
subject-day -> 24 hourly tokens -> masked-token Transformer SSL -> day embedding -> fold-safe label probe
```

The Transformer uses all 700 provided train/sample days without labels for masked reconstruction, then evaluates the resulting day embedding on the 450 labeled rows. MPS is used when available.

Results:

- Best initial single view: `no_sleep`, OOF `0.620859`.
- Best extra single view: `only_rhythm`, OOF `0.619825`.
- Full-OOF cross-view target diagnostic: `0.617372`, with drift vs v83 `0.075561`.

Feature-family signal:

- `only_rhythm` is the best single Transformer latent, suggesting the sequence model reads daily rhythm better than the full mixed feature space.
- `only_cross_modal` is clearly target-specific: it gives the best S3 loss (`0.521082`) even though its global score is weaker.
- `no_sleep` is useful for Q2 (`0.669603`) and beats the full view globally.
- `full` still wins Q1/S1 inside the optimistic cross-view selector, so not all raw breadth is harmful.
- `no_gps` gives the best S4 in the cross-view diagnostic.

Decision:

- Do not treat `0.617372` as honest validation because the cross-view target selector is full-OOF and therefore optimistic.
- Keep the Transformer encoder branch alive. It independently reaches the same range as the pruned-state decoder scaffold and exposes clearer modality/target specialization than the flat tabular encoder.
- Next step should be nested view selection or a multi-view Transformer decoder that learns target-specific attention over rhythm/cross-modal/no-sleep/full views without using v76/v83/v85 as teachers.

## Multires Transformer tokenization and MoE follow-up

Detailed log: `experiments/transformer_tokenization.md`

New scripts:

- `scripts/build_multires_token_grid.py`
- `scripts/train_transformer_moe_head.py`

Outputs:

- `outputs/multires10_transformer_encoder_v1/`
- `outputs/multires30_transformer_encoder_v1/`
- `outputs/transformer_moe_head_v1/`

Results:

- 10-minute raw-derived grid + subject-token deviation: best view `only_cross_modal`, OOF `0.621938`.
- 30-minute raw-derived grid + subject-token deviation: best view `no_sleep`, OOF `0.618590`.
- Nested Transformer expert MoE head: best `nested_moe_logreg_c0p3`, OOF `0.611527`, drift vs v83 `0.086812`.
- Embedding-level MoE head: negative, best OOF `0.636678`.
- Nested targetwise expert selection: full-OOF `0.614175` becomes nested `0.617817`, implying about `0.003642` selection optimism.

Interpretation:

- Finer is not automatically better. The 10-minute grid appears too sparse/noisy as a global day representation.
- 30-minute tokens are currently the best fixed-bin raw-derived tokenization.
- The strongest signal comes from MoE over tokenization/view experts, not from one global Transformer view.
- Directly reading SSL embeddings with a supervised head does not work yet; the useful signal appears after each Transformer view is decoded into target probabilities.
- This is now the best independent Transformer branch, but drift is larger than previous pruned-state branches, so it should be treated as breakthrough evidence before submission packaging.

## Fixed consensus target-map follow-up

Script: `scripts/train_consensus_pruned_state_decoder.py`

Output: `outputs/fixed_consensus_pruned_state_decoder_v1/`

This follow-up freezes target-specific decoder maps from nested selection frequencies. Unlike the nested run, it does not search for the best source inside each fold. The goal is to test whether the pruned state decoder can become a stable model definition rather than a fold-dependent selector.

Results:

- Best fixed map: `consensus_signal`
- OOF avg: `0.620577`
- Subject-prior baseline from v2: `0.627413`
- Gain vs subject prior: `-0.006836`
- Gain vs nested target-aware selection: `-0.004152`
- Drift vs v83 diagnostic reference: `0.068282`
- Corr vs v83 diagnostic reference: `0.871897`

Fixed `consensus_signal` map:

- Q1: `only_rhythm__prior_logit_blend_hgb_w20`
- Q2: `no_ratio__prior_logit_blend_state_mean_w35`
- Q3: `no_sleep__prior_logit_blend_hgb_w35`
- S1: `only_rhythm__prior_logit_blend_hgb_w20`
- S2: `no_missingness__prior_logit_blend_residual_ridge_w05`
- S3: `only_missingness__prior_logit_blend_rank_pairwise_w05`
- S4: `only_cross_modal__prior_logit_blend_hgb_w10`

Comparison:

- `consensus_signal`: `0.620577`
- `consensus_s4_temporal`: `0.621674`
- `consensus_conservative`: `0.622785`
- nested target-aware: `0.624729`
- subject prior: `0.627413`
- optimistic v2 target-wise full OOF: `0.617441`

Interpretation:

- The independent Encoder-Decoder route now has a stable scaffold:

```text
feature-family-pruned Encoder
→ subject-normalized state latent
→ fixed target-specific prior-residual Decoder
```

- This is a meaningful breakthrough-search signal because the fixed map beats both the subject prior and nested fold-selection result without using v76/v83/v85 as teachers.
- It is not a strong Public LB submission candidate yet. The OOF level is still far from the public-best v83 family, and row-wise drift vs v83 is about `0.068`.
- The next decoder work should not add more feature families blindly. It should improve the weak links inside this scaffold:
  - S2/S3 gating, because nested selection often fell back to subject prior but the fixed signal map still gains there.
  - Q-family calibration, because Q1/Q2/Q3 remain high-loss targets.
  - public-coordinate calibration, because v82/v85 showed that local OOF gains can be destroyed by panel/test distribution mismatch.

## Joint label-state bottleneck tests

Script: `scripts/train_joint_label_state_decoder.py`

Output: `outputs/joint_label_state_decoder_v1/`

This branch tests the decoder-bottleneck idea directly: instead of predicting seven labels independently, first predict a coarse label-state from the pruned latent and then map that state back to seven label probabilities.

Results:

- Best global: `no_temporal_delta__joint_label_cluster8_w10`
- OOF avg: `0.625946`
- Target-wise OOF avg: `0.621371`
- Best global drift vs v83 diagnostic reference: `0.063679`
- Target-wise drift vs v83 diagnostic reference: `0.073087`

Interpretation:

- Coarse label clusters work better than exact 7-label patterns or KNN state lookup.
- Exact 7-label patterns are too sparse: fold train splits still contain around `87` to `91` distinct full patterns.
- The branch does not beat the stable fixed scaffold (`stable_signal_s4_temporal`, `0.620281`), so a single full-label-state bottleneck is not enough.

## Q/S-family label-state follow-up

Script: `scripts/train_family_label_state_decoder.py`

Output: `outputs/family_label_state_decoder_v1/`

This follow-up splits the sparse 7-label state into Q-family (`Q1,Q2,Q3`) and S-family (`S1,S2,S3,S4`) intermediate states. Each family is decoded separately from the same pruned state latent, recombined into seven probabilities, then blended with the fold-safe subject prior.

Results:

- Best global: `drop_ratio_temporal_delta__family_q_pattern_s_pattern_w10`
- OOF avg: `0.626385`
- Target-wise OOF avg: `0.621171`
- Best global drift vs v83 diagnostic reference: `0.065777`
- Target-wise drift vs v83 diagnostic reference: `0.070116`

Target-wise selected sources:

- Q1: `only_missingness__family_q_cluster4_s_cluster6_w20`
- Q2: `no_ratio__family_q_state_mean_s_state_mean_w35`
- Q3: `only_rhythm__family_q_cluster4_s_cluster6_w35`
- S1: `no_temporal_delta__family_q_cluster4_s_cluster6_w10`
- S2: `no_ratio__family_q_knn25_s_knn25_w10`
- S3: `only_missingness__family_q_cluster4_s_cluster8_w05`
- S4: `no_sleep__family_q_state_mean_s_state_mean_w20`

Interpretation:

- Splitting the label-state does reduce sparsity: Q patterns are stable at `8`, S patterns are around `14` to `15`, while full 7-label patterns remain around `87` to `91`.
- That sparsity reduction is not sufficient. Best global is weaker than the full joint label-cluster run (`0.626385` vs `0.625946`), and target-wise improves only marginally (`0.621171` vs `0.621371`).
- The useful part is not the discrete Q/S pattern itself; it is still the bounded target-specific residual over a subject-normalized prior. Carry forward the selected feature-family clues, but do not promote family label-state as the primary decoder.

## Residual cap-gate decoder

Script: `scripts/train_residual_cap_gate_decoder.py`

Output: `outputs/residual_cap_gate_decoder_v1/`

This experiment keeps the stable fixed scaffold as the coordinate system and injects only a capped/gated logit residual from the optimistic extended full-OOF winner map:

```text
stable_logit + gate(sample, target) * clip(extended_logit - stable_logit, -cap, cap) * scale
```

The tested gates are:

- `all`: always use the capped residual.
- `agreement_with_prior`: use the residual only when stable and extended are on the same side of the fold-safe subject prior.
- `top_abs_50` / `top_abs_35`: use residuals only on large-disagreement rows.
- `signed_margin`: use the residual only when extended is farther from the subject prior than stable.

Results:

- Best global: `capgate_signed_margin_s100_c050`
- OOF avg: `0.616528`
- Target-wise OOF avg: `0.614731`
- Best global drift vs v83 diagnostic reference: `0.071953`
- Target-wise drift vs v83 diagnostic reference: `0.071092`

Comparison:

- `stable_signal_s4_temporal`: `0.620281`
- `extended_full_oof_winners`: `0.616766`
- residual cap-gate best global: `0.616528`
- residual cap-gate target-wise: `0.614731`

Target-wise selected sources:

- Q1: `capgate_signed_margin_s125_c030`
- Q2: `capgate_signed_margin_s125_c015`
- Q3: `stable_signal_s4_temporal`
- S1: `extended_full_oof_winners`
- S2: `extended_full_oof_winners`
- S3: `capgate_signed_margin_s100_c030`
- S4: `extended_full_oof_winners`

Interpretation:

- This is the strongest independent Encoder-Decoder OOF branch in the pruned-state family so far.
- The useful breakthrough signal is not a new discrete state label. It is a **sample-conditional residual permission rule**: use the bolder extended residual only when it has enough margin away from the subject prior, and cap its logit amplitude.
- Q1/Q2/S3 improve from cap-gating, while Q3 should stay on the stable scaffold. S1/S2/S4 still prefer the bolder extended map under full-OOF scoring.
- Public robustness is not proven. Drift vs v83 rises from the stable scaffold's roughly `0.069` to `0.072`, and the best variants come from a grid over full OOF. This should be nested/stress-tested before treating it as a submission-quality model.

## Nested residual cap-gate stress test

Script: `scripts/train_nested_residual_cap_gate_decoder.py`

Output: `outputs/nested_residual_cap_gate_decoder_v1/`

This stress test selects cap/gate parameters only on each outer fold's train rows and scores the selected source on held-out outer rows. It also records a target-wise nested selection variant.

Results:

- `extended_full_oof_winners`: `0.616766`
- `nested_global_capgate`: `0.618578`
- `nested_target_capgate`: `0.618979`
- `stable_signal_s4_temporal`: `0.620281`

Selection counts:

- Global selection picked `capgate_signed_margin_s100_c050` in 2/5 folds, `extended_full_oof_winners` in 2/5 folds, and `capgate_signed_margin_s075_c050` in 1/5 fold.
- Q1 mostly selected `capgate_signed_margin_s125_c030` (3/5).
- Q2 selected several high-scale cap-gates, with no single stable source.
- Q3 selected `stable_signal_s4_temporal` in 4/5 folds.
- S2 selected `extended_full_oof_winners` in 5/5 folds.
- S3 mostly selected `capgate_signed_margin_s125_c030` (3/5).
- S4 is unstable across extended and cap-gate variants.

Interpretation:

- The full-OOF cap-gate result was optimistic: full-OOF best global `0.616528` becomes nested global `0.618578`, and full-OOF target-wise `0.614731` becomes nested target-wise `0.618979`.
- The signal is still real enough to beat the stable scaffold under nested validation (`0.618578` vs `0.620281`).
- The cleanest carry-forward rule is global `signed_margin` cap-gating, not full target-wise selection. Target-wise selection adds optimism and instability, especially Q2/S4.
- The next step should turn `signed_margin` into a fixed decoder rule or learn a small fold-safe permission model, while keeping Q3 on the stable scaffold and treating S2's aggressive extended residual as a separate risk.

## Fixed permission policy decoder

Scripts:

- `scripts/train_fixed_permission_policy_decoder.py`
- `scripts/train_nested_fixed_permission_policy_decoder.py`

Outputs:

- `outputs/fixed_permission_policy_decoder_v1/`
- `outputs/nested_fixed_permission_policy_decoder_v1/`

This experiment converts the nested cap-gate lessons into fixed target policies instead of allowing target-wise grid search:

- Q1: signed-margin cap-gate (`s=1.25`, `cap=0.30`)
- Q2: stable scaffold
- Q3: stable scaffold
- S1: aggressive extended residual
- S2: aggressive extended residual
- S3: signed-margin cap-gate (`s=1.00`, `cap=0.30`)
- S4: aggressive extended residual

Results:

- `q1s3_signed_s1s2s4_extended_q3_stable`: `0.615095`
- `nested_majority_policy`: `0.615110`
- `global_signed_s100_c050`: `0.616528`
- `extended_full_oof_winners`: `0.616766`
- `stable_signal_s4_temporal`: `0.620281`

Nested policy stress test:

- `fixed_policy_best`: `0.615095`
- `nested_global_policy`: `0.615224`
- `extended_full_oof_winners`: `0.616766`
- `nested_target_policy`: `0.617663`
- `stable_signal_s4_temporal`: `0.620281`

Selection counts:

- Global nested policy selection picked `nested_majority_policy` in 3/5 folds and `q1s3_signed_s1s2s4_extended_q3_stable` in 2/5 folds.
- Q3 stayed stable in 4/5 folds.
- S2 picked extended in 5/5 folds.
- S4 picked extended in 4/5 folds.
- Q1 mostly picked the Q1/S3 signed policy family.
- S3 mostly picked `nested_majority_policy`.

Interpretation:

- This is the strongest independent pruned-state Encoder-Decoder branch so far.
- More importantly, policy-search optimism is small: `0.615095` becomes `0.615224` under nested global policy selection.
- The breakthrough shape is now clearer:

```text
stable subject-normalized residual scaffold
+ Q1/S3 signed-margin permission gate
+ S1/S2/S4 aggressive extended residual
+ Q2/Q3 stable guard
```

- This still does not prove Public LB quality, and drift vs v83 remains around `0.070` with lower correlation than the stable scaffold. But compared with the previous `0.620281` independent scaffold, this is a meaningful decoder-level improvement.

## Learned row-level permission gate

Script: `scripts/train_learned_permission_gate_decoder.py`

Output: `outputs/learned_permission_gate_decoder_v1/`

This experiment replaces fixed target rules with nested row-level meta decoders. The models use only independent branch predictions (`stable`, `extended`, `fixed_permission_policy`), the fold-safe subject prior, signed-margin features, residual magnitudes, and panel position. v83 is still used only as a drift diagnostic.

Tested variants:

- direct stackers: `stack_logreg`, `stack_hgb`
- residual regressors: `residual_ridge_c030`, `residual_hgb_c030`, `residual_hgb_c050`
- learned permission gates: `gate_hgb_ext`, `gate_logreg_ext`, `gate_hgb_fixed`

Results:

- `fixed_permission_policy`: `0.615095`, drift `0.070382`
- `learned_gate_hgb_fixed`: `0.615610`, drift `0.068406`
- `learned_gate_hgb_ext`: `0.616086`, drift `0.068034`
- `learned_gate_logreg_ext`: `0.616187`, drift `0.068401`
- `extended_full_oof_winners`: `0.616766`
- `stable_signal_s4_temporal`: `0.620281`

Interpretation:

- Learned gates do not beat the fixed permission policy on OOF. The hand-derived target policy remains the strongest independent pruned-state branch.
- The best learned gate is still useful: `learned_gate_hgb_fixed` gives up about `0.0005` OOF but reduces drift below the stable scaffold (`0.068406` vs `0.068726`) while keeping most of the fixed-policy gain.
- Direct stackers and unconstrained residual regressors overfit or distort the coordinate system. `learned_stack_hgb`, `learned_stack_logreg`, and residual regressors are rejected for now.
- Carry forward two branches:
  - score-seeking branch: `fixed_permission_policy`
  - robustness-seeking branch: `learned_gate_hgb_fixed`

## Meta-gated consensus follow-up

Script: `scripts/train_meta_gated_consensus_decoder.py`

Output: `outputs/meta_gated_consensus_decoder_v1/`

This experiment kept the fixed `consensus_signal` sources but tested whether a small fold-safe meta gate could learn how much to trust the state source over the subject prior. The meta models were trained only from inner-OOF source predictions inside each outer fold.

Results:

- `shrink_w100`: `0.620577`
- `shrink_w75`: `0.621354`
- `shrink_w50`: `0.622751`
- `shrink_w25`: `0.624771`
- `meta_logreg`: `0.632022`
- `meta_residual_ridge`: `0.687088`

Interpretation:

- The learned gate is a negative result. With only about 450 labels, a second-stage meta decoder over source/base deltas overfits badly.
- Simple shrinkage is also not helpful; the original fixed consensus source (`w100`) remains best.
- This argues against spending more effort on tiny supervised gates at this stage. The stronger path is better encoder family pruning and better intermediate state definitions, not a learned meta gate on top of weak source predictions.

## Extended feature-family combination pruning

Script: `scripts/train_extended_family_pruning_decoder.py`

Output: `outputs/extended_family_pruning_decoder_v1/`

This experiment tested family combinations beyond one-family-only/drop ablations, including `rhythm+deviation`, `rhythm+missingness`, `drop_ratio+drop_rank`, `drop_ratio+drop_temporal_delta`, and related recipes.

Results:

- Best global: `drop_ratio_temporal_delta__prior_logit_blend_hgb_w20`
- Best global OOF avg: `0.624650`
- Target-wise full-OOF avg: `0.616766`
- Target-wise drift vs v83 diagnostic reference: `0.068461`

Target-wise full-OOF winners:

- Q1: `drop_ratio_temporal_delta__prior_logit_blend_hgb_w35`
- Q2: `drop_raw_ratio__prior_logit_blend_hgb_w35`
- Q3: `drop_sleep_late__prior_logit_blend_hgb_w35`
- S1: `drop_raw_rank__prior_logit_blend_residual_ridge_w10`
- S2: `only_rhythm_deviation_cross_modal__prior_logit_blend_residual_ridge_w05`
- S3: `drop_ratio_temporal_delta__prior_logit_blend_hgb_w20`
- S4: `only_missingness_cross_modal__prior_logit_blend_rank_pairwise_w10`

Interpretation:

- The full-OOF target-wise score improves over v2 target-wise (`0.617441` to `0.616766`), so feature-family combination pruning does expose new label-aligned latent signal.
- The global score is not better than `consensus_signal`, meaning the new signal is target-specific and selection-sensitive rather than a broad replacement.
- This needs nested validation before adoption.

## Nested extended-family validation

Script: `scripts/train_nested_extended_family_decoder.py`

Output: `outputs/nested_extended_family_decoder_v1/`

This nested run uses the extended-family winners as a compact candidate pool:

```text
outer fold:
  inner folds select one source per target
  selected source is trained on outer-train
  outer-val receives the score
```

Results:

- Nested extended-family OOF avg: `0.625206`
- Previous nested target-aware OOF avg: `0.624729`
- Fixed `consensus_signal` OOF avg: `0.620577`
- Drift vs v83 diagnostic reference: `0.065883`

Selection stability:

- Q1: `only_rhythm__prior_logit_blend_hgb_w20` selected 4/5.
- S4: `no_temporal_delta__prior_logit_blend_hgb_w20` selected 3/5.
- S1: `subject_prior` selected 3/5.
- S3: `subject_prior` selected 3/5.
- Q2/Q3/S2 remain unstable.

Decision:

- Do not adopt the full target-wise extended-family map as a submission-shaped model; most of its gain is selection-sensitive.
- Keep two stable insights:
  - Q1 should stay close to `only_rhythm + HGB`.
  - S4 prefers `no_temporal_delta + HGB` more reliably than the `only_cross_modal` branch.
- Treat S1/S3 residual decoders as suspect unless a new state objective makes them beat subject prior under nested validation.

## Stable extended consensus maps

Script: `scripts/train_stable_extended_consensus_decoder.py`

Output: `outputs/stable_extended_consensus_decoder_v1/`

This experiment converts the nested extended-family lessons into fixed maps. No source search is performed inside this run. It compares:

- `extended_full_oof_winners`: the optimistic full-OOF target-wise winners from the extended-family run.
- `stable_signal_s4_temporal`: previous `consensus_signal`, but with S4 switched to nested-stable `no_temporal_delta + HGB`.
- `stable_prior_guarded`: Q1/Q2/Q3/S4 state sources with S1/S2/S3 guarded by subject prior.
- `stable_nested_vote`: majority nested votes per target.
- `q1_s4_only`: only the two most stable repeated signals, Q1 and S4.

Results:

- `extended_full_oof_winners`: `0.616766`, drift `0.069892`.
- `stable_signal_s4_temporal`: `0.620281`, drift `0.068726`.
- `stable_prior_guarded`: `0.622146`, drift `0.066633`.
- `stable_nested_vote`: `0.622837`, drift `0.066150`.
- `q1_s4_only`: `0.626191`, drift `0.064413`.

Decision:

- The best trustworthy fixed scaffold is now `stable_signal_s4_temporal` (`0.620281`), slightly improving `consensus_signal` (`0.620577`) through one nested-supported structural edit: S4 uses `no_temporal_delta + HGB` instead of `only_cross_modal + HGB`.
- `extended_full_oof_winners` remains an optimism upper bound, not a trusted model. It reproduces the full-OOF `0.616766`, but nested validation already showed that this family falls back to `0.625206`.
- Guarding S1/S2/S3 with subject prior improves drift but loses too much OOF signal, so the current useful decoder is not a pure conservative prior guard.
- The next improvement should preserve the `stable_signal_s4_temporal` map and attack the remaining weak targets through better state objectives, not through meta gates or full-OOF source selection.

## Residual state objective decoder

Script: `scripts/train_residual_state_objective_decoder.py`

Output: `outputs/residual_state_objective_decoder_v1/`

This experiment reframes the decoder target from direct label probability to logit residual over the fold-safe subject prior. It tests residual prototypes, residual nearest-neighbor, residual ridge, and their mean over subject-normalized state latents.

Results:

- Best global: `no_ratio__residual_ridge_w03`
- Best global OOF avg: `0.626331`
- Target-wise full-OOF avg: `0.620437`
- Best global drift vs v83 diagnostic reference: `0.063475`
- Target-wise drift vs v83 diagnostic reference: `0.066478`

Best decoder family by global OOF:

- `residual_ridge`: `0.626331`
- `residual_mean`: `0.626461`
- `residual_knn`: `0.626783`
- `residual_proto`: `0.627603`

Interpretation:

- Residual prototypes and residual nearest-neighbor are not stronger than the existing prior-residual ridge route.
- The experiment lowers drift but does not beat the fixed `stable_signal_s4_temporal` scaffold (`0.620281`).
- Target-wise full-OOF shows possible Q1/S1/S2/S4 improvements, but this needs nested validation before any adoption.

## Nested residual hybrid validation

Script: `scripts/train_nested_residual_hybrid_decoder.py`

Output: `outputs/nested_residual_hybrid_decoder_v1/`

This nested run combines stable consensus sources with residual-state and extended-family candidates in a compact target-specific candidate pool.

Results:

- Nested residual hybrid OOF avg: `0.624176`
- Previous nested target-aware OOF avg: `0.624729`
- Nested extended-family OOF avg: `0.625206`
- Fixed `stable_signal_s4_temporal` OOF avg: `0.620281`
- Drift vs v83 diagnostic reference: `0.065379`

Selection stability:

- Q1: `only_rhythm + HGB` selected 4/5, residual missingness selected 1/5.
- Q2 remains unstable: `drop_raw_ratio`, `no_ratio residual`, `no_ratio state_mean`, and subject prior all appear.
- Q3 splits between `no_sleep + HGB`, `only_rhythm + state_mean`, and subject prior.
- S1 and S3 mostly fall back to subject prior.
- S4 again favors `no_temporal_delta + HGB` in 3/5 folds.

Decision:

- Residual-state candidates add a small nested-search signal (`0.624176` beats `0.624729`), so the idea is not dead.
- They do not yet improve the best fixed scaffold. Most target-wise residual gains are still selection-sensitive.
- Keep the current fixed scaffold as `stable_signal_s4_temporal`; carry forward only the evidence that Q1 has a weak residual-missingness alternative worth revisiting with a stronger state objective.

## Multiscale subject-state decoder

Script: `scripts/train_multiscale_subject_state_decoder.py`

Output: `outputs/multiscale_subject_state_decoder_v1/`

This experiment changes the encoder state definition rather than adding a larger decoder. The state representation includes:

- PCA position from a pruned feature family.
- Global z-score.
- Subject-relative deviation/rank using all same-subject fit days.
- Past-only subject deviation/rank using dates earlier than the query day.
- Recent 7/14 same-subject deviation/rank.
- Distance/novelty summaries to each of those pools.
- Soft prototype membership over the expanded state.

The first full grid was too slow because it recomputed the same state per source. The script was revised to cache state per `(preset, fold)` and then evaluate all decoder/weight variants on that shared state.

Results:

- Best global: `only_rhythm__multiscale_state_mean_w10`
- Best global OOF avg: `0.626267`
- Target-wise full-OOF avg: `0.620484`
- Best global drift vs v83 diagnostic reference: `0.063039`
- Target-wise drift vs v83 diagnostic reference: `0.064398`

Decoder/preset summary:

- Best decoder family: `state_mean` at `0.626267`, followed closely by `hgb` at `0.626288`.
- `residual_ridge` is weaker in this multiscale state (`0.628123` best).
- Best presets: `only_rhythm` (`0.626267`) and `drop_ratio_temporal_delta` (`0.626288`).

Decision:

- This is a useful negative result. Adding past-only/recent subject-history geometry lowers drift but does not improve the independent fixed scaffold.
- The gain is not in making the state vector larger. The current bottleneck is likely the objective or target-specific calibration, not missing simple subject-history geometry.
- Keep `stable_signal_s4_temporal` as the current scaffold. Do not promote multiscale state candidates unless nested validation later shows target-specific stability.

## Joint label-state decoder

Script: `scripts/train_joint_label_state_decoder.py`

Output: `outputs/joint_label_state_decoder_v1/`

This experiment attacks the 450-label bottleneck from the decoder side. Instead of predicting the seven labels independently, it first predicts a joint label state and then maps that state back into the seven target probabilities. The tested intermediate states are:

- label clusters over the 7-dimensional label vector,
- exact observed label patterns,
- nearest-neighbor label-state retrieval in encoder state space,
- a mean of the joint label-state decoders.

All predictions are fold-safe: label states and label-pattern classifiers are fit only on the fold train split, then blended with the fold-safe subject prior.

Results:

- Best global: `no_temporal_delta__joint_label_cluster8_w10`
- Best global OOF avg: `0.625946`
- Target-wise full-OOF avg: `0.621371`
- Best global drift vs v83 diagnostic reference: `0.066050`
- Target-wise drift vs v83 diagnostic reference: `0.073087`

Decoder/preset summary:

- Best joint decoder: `label_cluster8` at `0.625946`.
- `label_knn25` and `label_state_mean` are close but weaker.
- Exact `label_pattern` is weaker, likely because 95 observed patterns are too many for 450 rows.
- Best preset is `no_temporal_delta`, matching prior evidence that this family is useful for S4-like temporal stability.

Decision:

- Joint label-state decoding is a useful idea, but this implementation does not beat the fixed scaffold.
- The high target-wise drift means the label-state decoder changes the row distribution too aggressively for the amount of label data.
- Do not promote this branch. Keep only the insight that coarse label clusters are better than exact label-pattern prediction under the 450-label constraint.
