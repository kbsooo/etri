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
