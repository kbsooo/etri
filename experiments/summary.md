# ETRI Latent Encoder Experiments

Last updated: 2026-05-20

## Current Best

- Best internal OOF candidate: `outputs/conditional_latent_routing_v79_s23_behavior_on_v78/submission_conditional_latent_routing.csv`
- Best internal OOF: `0.478230`
- Main report: `outputs/breakthrough_signal_report.md`
- Public LB feedback: `experiments/public_lb_feedback.md`
- Candidate report: `outputs/conditional_latent_routing_v79_s23_behavior_on_v78/report.md`
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
| v57 subject/time-aware attention residual | 0.498600 | neighbor attention with same-subject and recency bias | `outputs/breakthrough_signal_report.md` |
| v58 learned neighbor scorer residual | 0.498265 | learned decoder over distance, subject, recency, and residual-neighbor summaries | `outputs/breakthrough_signal_report.md` |
| v59 residual-contrastive metric residual | 0.497895 | metric weighted by current base residual direction; residual-only route reaches 0.498031 | `outputs/breakthrough_signal_report.md` |
| v60 residual PLS latent objective | 0.497145 | fold-safe latent trained to predict current-base residuals; residual-PLS-only route reaches 0.497271 | `outputs/breakthrough_signal_report.md` |
| v61 family/target residual PLS objective | 0.496127 | Q/S-family and per-target residual latent objectives; residual-PLS-only route reaches 0.496175 and constrained reaches 0.496312 | `outputs/breakthrough_signal_report.md` |
| v62 cross-family residual PLS objective | 0.495010 | opposite-family and Q+S combined residual latent objectives; new-source-only route reaches 0.495174 and constrained reaches 0.495269 | `outputs/breakthrough_signal_report.md` |
| v63 neural residual bottleneck objective | 0.493630 | fold-safe MLP bottleneck residual latent; neural-only route reaches 0.493996 and constrained reaches 0.494207 | `outputs/breakthrough_signal_report.md` |
| v64 neural multi-view residual bottleneck | 0.492249 | MLP bottleneck trained on residual labels plus PLS residual subspaces; neural-only reaches 0.492401 and constrained reaches 0.492763 | `outputs/breakthrough_signal_report.md` |
| v65 target-wise neural residual bottleneck | 0.490915 | target-wise neural residual probes are weak alone, but add useful routed S2/S3 residuals; neural-only reaches 0.491035 and target-neural-only reaches 0.491846 | `outputs/breakthrough_signal_report.md` |
| v66 panel-aware residual encoder | 0.489729 | panel position/basis features and panel-weighted residual targets make neural residual views more readable; neural-only reaches 0.489882 while panel-only is weak at 0.490907 | `outputs/breakthrough_signal_report.md` |
| v67 residual prototype objective | 0.488680 | fold-safe residual+panel residual prototypes add an independent S2 regime signal; prototype-only reaches 0.489493 and neural-only reaches 0.489030 | `outputs/breakthrough_signal_report.md` |
| v68 prototype-metric retrieval | 0.486989 | target residual metric weighting on prototype latents is weak alone, but the neural residual family reaches 0.487081 and improves every target | `outputs/breakthrough_signal_report.md` |
| v69 neural mixture concat probe | 0.486152 | all-source improves slightly, but mixture-only does not improve at all; naive concat loses target/panel specialization | `outputs/breakthrough_signal_report.md` |
| v70 gated residual-view mixture | 0.485258 | fold-safe target residual gate over neural views improves the all-source route; gated-only is nearly neutral at 0.486144, so selection helps but a learned gate is still needed | `outputs/breakthrough_signal_report.md` |
| v71 learned view-gate probe | 0.484026 | learned-gate source is neutral, but retrained neural residual views still create a large new residual layer after v70; neural-only reaches 0.484048 | `outputs/breakthrough_signal_report.md` |
| v72 bin-aware view-gate probe | 0.483657 | bin-gate-only is still neutral, but v71 residual still responds to cross-family neural views plus neighbor/PLS decoders | `outputs/breakthrough_signal_report.md` |
| v73 sample-conditioned context gate | 0.483097 | context-gate-only finally gives a tiny S3 mid signal, while all-source gain still comes mostly from cross-family/panel neural and PLS/neighbor views | `outputs/breakthrough_signal_report.md` |
| v74 panel-bin context gate | 0.482206 | bin-local context gate gives the first multi-target gate-only signal, while neural residual views still drive the largest S1/S2/S3 gains | `outputs/breakthrough_signal_report.md` |
| v75 second-half context gate | 0.481505 | second-half-only gate is weaker than v74's panel-bin gate, but another neural residual refit layer produces a new best | `outputs/breakthrough_signal_report.md` |
| v76 context-attention residual probe | 0.480978 | local attention over view-context features fails alone, but residual refit keeps finding S4/S3 and broad small target/bin gains | `outputs/breakthrough_signal_report.md` |
| v77 residual-behavior neighborhood objective | 0.480038 | residual-neighborhood latent gives standalone Q2/S2/S3 signal and all-source reaches a new best | `outputs/breakthrough_signal_report.md` |
| v78 family/target residual-neighborhood objective | 0.479449 | splitting residual-behavior neighborhoods by family and target gives stronger standalone behavior-only signal, led by target-local S3 late | `outputs/breakthrough_signal_report.md` |
| v79 S23/late residual-neighborhood objective | 0.478230 | late-panel target residual-neighborhood latent creates a larger direct breakthrough signal; new S23-only route reaches 0.478445 | `outputs/breakthrough_signal_report.md` |

## What Worked

- Subject-relative temporal features worked better than generic daily aggregates.
- Label-free digest axes became useful once they represented recovery, rhythm, and cross-modal mismatch.
- Iterative residual routing kept finding signal, but gains shrank as the base improved.
- The most consistent current signal is personal state-space dynamics: transition, recurrence, novelty burden, and novelty recovery.
- Target/bin routing is useful because not every latent source helps every label or every panel position.
- The first explicit common `PCA+PLS` latent is too blunt as a direct multi-head predictor, but still contains residual signal when decoded with local/retrieval-style corrections.
- The first local decoder over the common latent pushes internal OOF below 0.50, mainly through S4/S1 and smaller broad residuals.
- Target-specific metric weighting improves retrieval residuals again, so each label appears to need its own notion of "similar day" in the shared state-space.
- Adding same-subject and temporal recency bias to neighbor attention improves the routed residual again, mainly around S4 mid and smaller Q3/S1 residuals.
- Learning a small neighbor scorer over latent-distance, same-subject mass, temporal recency, and residual-neighbor summaries adds a new constrained S3 second-half signal.
- Residual-contrastive metric weighting creates a broad mid-panel residual signal across Q1/Q2/S1/S2/S3/S4, especially S2 and S3, although the strictest constrained route still keeps only the strongest S4 KNN move.
- Training a fold-safe PLS latent directly on current-base residuals creates the strongest recent jump, especially Q2 all rows, Q1 mid, and Q3 late; the constrained route keeps Q1/Q2/Q3 residual PLS moves.
- Splitting the residual latent objective into Q-family, S-family, and per-target residual PLS creates another large routed jump. The strongest new signal is cross-family: Q residual latent improves S2/S3, S residual latent improves Q3, and target residual latent improves S4.
- Explicit cross-family and Q+S combined residual PLS objectives reproduce the signal after v61. The new-source-only route nearly matches the full route, which supports modeling residual subspaces as shared and cross-predictive rather than label-family-local.
- A fold-safe MLP bottleneck residual encoder beats the linear residual subspace route when decoded by retrieval. The neural-only route is strong, especially for S1 all rows, Q3 all rows, and S2 late, so the next breakthrough direction is a real residual-subspace encoder rather than only linear PLS.
- Multi-view neural bottlenecks trained on both residual labels and PLS residual subspaces keep improving the same route. The strongest current residual is now S-family, especially S4 late, S2 second-half, and S3 first/second-half.
- Target-wise neural residual probes are not good as standalone predictors, but they expose useful late-panel S2 and S3 corrections when combined with the shared/family neural residual sources. This supports a mixture-of-residual-subspaces encoder rather than one target-only encoder per label.
- Panel position is not just a post-hoc routing variable. Adding panel position/basis to the encoder input makes the neural residual sources stronger, especially S3 all rows, Q3 late/mid, S2 late, S1 first-half, and S4 late/first-half. The panel-only latent is weak, so the useful signal is panel-conditioned residual representation, not a standalone time-index shortcut.
- Residual prototype targets add a small but independent regime signal, mostly for S2. The stronger all-source gain comes from combining prototype residual regimes with the existing panel-aware neural family, which supports training the encoder on residual behavior clusters instead of only exact residual values.
- The neural residual family is now the dominant repeated signal. v68 improves every target after v67, with large S2 first-half, Q3 late, S1 mid, S4 first-half/late, and Q1 second-half moves. Prototype metric weighting alone is weak, but adding it confirms the next breakthrough should strengthen target/panel neural residual views rather than return to pure linear PLS.
- A naive concat mixture of all neural residual views is a useful negative result: mixture-only produces no selected improvements. The all-source route still improves through individual neural/prototype/PLS sources, so the views should be selected by target/panel gates rather than collapsed by unweighted concatenation.
- Fold-safe residual-view gating gives a new best all-source route at 0.485258 and neural-only reaches 0.485308. The direct gated-only source is only marginally positive, which means the useful signal is still distributed across individual target/panel/prototype neural views; the next encoder needs a learned attention/gate rather than a hard top-k stacked latent.
- Re-fitting the neural residual-view family after v70 creates another large OOF layer to 0.484026. The strongest moves are Q1 first-half/second-half, S1 late/mid, S2 first-half, S3 late/mid, and smaller Q2/Q3/S4 corrections, which says the residual-view family is not saturated yet.
- A v72 bin-aware gate attempt still creates a new all-source best at 0.483657, but the selected improvements come from source-wise routing: Q2 late cross-family neural, S3 mid neighbor, S4 mid/late neighbor+PLS, and smaller Q1/Q3/S2 moves. This confirms repeated residual signal, not a successful unified gate.
- A sample-conditioned context gate gives the first nonzero gate-only routed move after the failed global/bin gates: S3 mid from `joint_neural_context_gate_hgb_resid`. It is tiny, but it points to local/contextual gating as the right consolidation direction.
- Training context gates separately inside panel bins gives the first useful multi-target gate-only signal: Q1/Q2 second-half, S3 second-half, and S4 second-half. This supports local context gating as a real auxiliary, not only a failed consolidation attempt.
- A narrower second-half-only context gate is weaker than the v74 panel-bin gate: gate-only reaches only 0.482181 and keeps Q1/S3 late moves. The new best still comes from source-wise neural/prototype/neighbor residuals, especially S4 late, Q1/S2/S3 first-half, and Q3 late.
- A local attention decoder over residual-view context features creates a new all-source best at 0.480978 and neural-only reaches 0.481166. The important positive signal is still source-wise residual refitting: S4 late cross-family/Q-neural residual is strong, S3 mid neighbor is strong, and Q2/Q3/S1/S2 add smaller target/bin corrections.
- Training the encoder to predict residual-neighborhood behavior gives the first useful standalone neighborhood-objective signal after v76. Residual-behavior-only improves to 0.480863 using Q2 first-half, S2 mid, and S3 mid moves, while all-source reaches 0.480038 and neural-only reaches 0.480134.
- Splitting residual-neighborhood behavior by family, cross-family, and target sharpens v77. New-behavior-only reaches 0.479863 and behavior-only reaches 0.479835, led by target-local S3 late plus cross-family S2/S3/S4 moves; all-source reaches 0.479449.
- Late-panel target residual-neighborhood is a stronger objective than the generic S23 focus alone. The new v79-only route reaches 0.478445 from the v78 base, with large Q1 late and Q3 mid gains plus S1 second-half, S2 first-half, and S3 late moves. This suggests the useful encoder axis is "late residual behavior state" rather than only "S2/S3 residual behavior."

## What Failed Or Was Weaker

- A single shared digest encoder-decoder was too weak as a full replacement.
- Generic sequence residual layers saturated quickly.
- S2 did not respond well to generic S2-only GRU/Transformer style sequence residuals, but did respond to sleep/missingness retrieval and later temporal-state features.
- Public LB feedback on older candidates was worse than internal OOF, so OOF gains must be treated as signal discovery rather than guaranteed leaderboard gain.
- Per-target neural residual encoders are too unstable as direct source models. The useful part is the multi-view target residual bottleneck as a small routed correction, not a full replacement for shared/family latent spaces.
- A pure panel-only residual target barely improves the v65 base. Panel context needs to be fused into the broader shared/family/target neural residual views.
- Residual prototype objectives are not broad enough alone. They are useful as one view in the residual mixture, not as a replacement for shared/family/target neural residual targets.
- Prototype metric weighting is too narrow by itself. It gives a small S2 second-half correction, but most of the gain still comes from target, panel, and family neural residual sources.
- Unweighted neural-view concatenation washes out the useful specialization. This argues against a single flat latent unless it has learned gates or attention over residual views.
- The first hand-built gated mixture is too weak as a standalone source. It improves only S3 mid by a tiny amount in gated-only routing, so static residual-alignment top-k is not expressive enough to replace source-wise routing.
- The first learned positive ridge gate is also too weak as a standalone source. It selects no routed moves after v70, so a useful unified gate probably needs sample-specific context or an explicit target/bin objective rather than one fold-level coefficient vector.
- Splitting the learned gate by panel bin is also not enough. The bin-gate-only route selects no moves after v71, so the next consolidation attempt should learn a local/sample-conditioned neighbor relation rather than fixed bin coefficients.
- The first context gate is still much weaker than source-wise routing. Gate-only reaches only 0.483645 versus all-source 0.483097 and neural-only 0.483267, so it is a direction signal, not a replacement.
- Even the stronger panel-bin context gate remains secondary. Neural-only reaches 0.482220, almost identical to all-source 0.482206, so the main discovery scaffold is still source-wise neural residual routing.
- Over-focusing the context gate on one broad second-half window loses the multi-target Q1/Q2/S3/S4 signal from v74. Panel-bin local context is better than second-half-only context.
- The first nonparametric context-attention decoder is a negative result as a standalone source: context-attention-only makes no selected move from the v75 base, and its best candidates are still worse than base. Local attention over view-disagreement features is not enough without a stronger residual objective.

## Current Architecture Status

- Current implementation: common label-free features plus target-specific source models for `Q1`, `Q2`, `Q3`, `S1`, `S2`, `S3`, `S4`, composed by a conditional target/bin router.
- Not yet final: one unified neural encoder with seven heads.
- Strong next direction: target-local late residual-neighborhood latent is now the clearest encoder signal. The next step should make a dedicated late-behavior objective that is target-aware but not S23-only, then test whether the Q1/Q3/S1 jumps survive stricter block/sample diagnostics.

## Next 3

1. Build a dedicated target-late residual-neighborhood objective with Q/S/S23 variants and stricter block/sample weighting.
   - Success criterion: new-source-only should preserve v79's Q1 late and Q3 mid gains while keeping S2/S3 positive.

2. Turn the neighbor scorer from a post-hoc feature decoder into the latent objective itself: pull together days that have similar target residual behavior while preserving subject/time context.
   - Success criterion: improve S3/S4/S1 residuals with fewer routed moves and avoid standalone decoder collapse.

3. Add a regime-aware decoder that treats early/late panel positions as different latent manifolds instead of only routing after prediction.
   - Success criterion: preserve v65 first-half Q1/S1 and late S2/S4 gains while reducing reliance on two-move target routing.
