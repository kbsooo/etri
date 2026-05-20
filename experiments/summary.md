# ETRI Latent Encoder Experiments

Last updated: 2026-05-20

## Current Best

- Best internal OOF candidate: `outputs/conditional_latent_routing_v56_metric_attention_on_v55/submission_conditional_latent_routing.csv`
- Best internal OOF: `0.498945`
- Main report: `outputs/breakthrough_signal_report.md`
- Public LB feedback: `experiments/public_lb_feedback.md`
- Candidate report: `outputs/conditional_latent_routing_v56_metric_attention_on_v55/report.md`
- Important caveat: this is an internal OOF proxy, not Public LB. Recent Public LB feedback for older submissions was weaker than OOF suggested.

## What We Are Testing

The central hypothesis is that each subject-day should be encoded as a point and movement in a personal latent state space:

- How today differs from the subject's own recent baseline.
- Whether the difference is growing, reversing, persisting, or recovering.
- Whether multiple data streams move together or one stream leads another.
- Whether today's state is familiar or novel relative to that subject's past days.
- Whether novelty is isolated, accumulating, or resolving.

This is not yet one final monolithic deep encoder. The current work is feature/representation discovery for the latent axes that a final common encoder should preserve.

## Best Runs

| Stage | Internal OOF | Main idea | Evidence path |
| --- | ---: | --- | --- |
| public-feedback anchor | 0.576217 | stronger anchor after Public LB feedback | `outputs/breakthrough_signal_report.md` |
| v25 joint all-target digest | 0.550644 | label-free daily digest: phone/social/body/recovery/desync | `outputs/breakthrough_signal_report.md` |
| digest label-aligned probe | 0.550558 | weak shared latent auxiliary | `outputs/breakthrough_signal_report.md` |
| v29 temporal digest deeper | 0.544772 | today vs subject recent baseline | `outputs/breakthrough_signal_report.md` |
| v30 temporal shape | 0.535694 | momentum, acceleration, rank-extreme | `outputs/breakthrough_signal_report.md` |
| v32 temporal shape L2 | 0.533214 | second temporal-shape residual layer | `outputs/breakthrough_signal_report.md` |
| v34 persistence/regime | 0.529944 | persisting/recovering/regime-shift deviations | `outputs/breakthrough_signal_report.md` |
| v36 burden/streak | 0.526081 | accumulated shock load and abnormal streaks | `outputs/breakthrough_signal_report.md` |
| v38 signed/decay | 0.521168 | positive/negative shock memory and decay | `outputs/breakthrough_signal_report.md` |
| v40 cross-modal synchrony | 0.516460 | simultaneous shocks across modalities | `outputs/breakthrough_signal_report.md` |
| v42 lead-lag probe | 0.513510 | previous-day shocks leading today's shocks | `outputs/breakthrough_signal_report.md` |
| v46 motif | 0.512673 | within-modality trajectory motifs | `outputs/breakthrough_signal_report.md` |
| v47 integrated dynamics | 0.511600 | synchrony + lead-lag + motif together | `outputs/breakthrough_signal_report.md` |
| v48 state-transition latent | 0.509456 | movement through cross-modal shock state space | `outputs/breakthrough_signal_report.md` |
| v49 state-recurrence novelty | 0.507926 | familiar vs rare personal state | `outputs/breakthrough_signal_report.md` |
| v50 state-manifold latent | 0.506657 | transition + recurrence jointly | `outputs/breakthrough_signal_report.md` |
| v51 novelty-burden latent | 0.504393 | sustained novelty load | `outputs/breakthrough_signal_report.md` |
| v52 novelty-recovery latent | 0.502679 | entering/leaving novelty regimes | `outputs/breakthrough_signal_report.md` |
| v53 integrated state-space latent | 0.500979 | transition + recurrence + novelty + recovery jointly | `outputs/breakthrough_signal_report.md` |
| v54 common PCA/PLS state-space residual | 0.500162 | shared label-aligned latent works only as local residual | `outputs/breakthrough_signal_report.md` |
| v55 local decoder residual | 0.499526 | similar-day/prototype decoder over common latent | `outputs/breakthrough_signal_report.md` |
| v56 metric-attention retrieval residual | 0.498945 | target-specific learned similarity metric | `outputs/breakthrough_signal_report.md` |

## What Worked

- Subject-relative temporal features worked better than generic daily aggregates.
- Label-free digest axes became useful once they represented recovery, rhythm, and cross-modal mismatch.
- Iterative residual routing kept finding signal, but gains shrank as the base improved.
- The most consistent current signal is personal state-space dynamics: transition, recurrence, novelty burden, and novelty recovery.
- Target/bin routing is useful because not every latent source helps every label or every panel position.
- The first explicit common `PCA+PLS` latent is too blunt as a direct multi-head predictor, but still contains residual signal when decoded with local/retrieval-style corrections.
- The first local decoder over the common latent pushes internal OOF below 0.50, mainly through S4/S1 and smaller broad residuals.
- Target-specific metric weighting improves retrieval residuals again, so each label appears to need its own notion of "similar day" in the shared state-space.

## What Failed Or Was Weaker

- A single shared digest encoder-decoder was too weak as a full replacement.
- Generic sequence residual layers saturated quickly.
- S2 did not respond well to generic S2-only GRU/Transformer style sequence residuals, but did respond to sleep/missingness retrieval and later temporal-state features.
- Public LB feedback on older candidates was worse than internal OOF, so OOF gains must be treated as signal discovery rather than guaranteed leaderboard gain.

## Current Architecture Status

- Current implementation: common label-free features plus target-specific source models for `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, `S4`, composed by a conditional target/bin router.
- Not yet final: one unified neural encoder with seven heads.
- Strong next direction: keep the common personal state-space encoder and make the decoder explicitly local/retrieval-aware with target-specific learned similarity.

## Next 3

1. Replace diagonal metric weighting with learned neighbor attention or a small metric network over the common latent.
   - Success criterion: beat v56 and keep the constrained signal below 0.50.

2. Add a contrastive/retrieval objective to the common latent so that similar personal state transitions are close.
   - Success criterion: improve S4/S1/S2 residuals without making direct multi-head predictions collapse toward poor global calibration.

3. Prototype the actual common encoder + seven-head decoder using the discovered latent axes as inputs and/or reconstruction targets.
   - Success criterion: not necessarily immediate best OOF, but should reproduce the same target-level signals with less hand-routed composition.
