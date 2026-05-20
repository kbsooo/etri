# Breakthrough Signal Report

## Current Signal

The strongest signal so far is not a safer blend. It is a subject-relative temporal dynamics encoder pattern:

1. Build a strong latent/conditional base.
2. Encode today relative to the subject's recent history.
3. Preserve temporal shape: momentum, acceleration, persistence, burden, and signed decay.
4. Preserve cross-modal structure: same-day synchrony plus previous-day lead-lag transitions.
5. Use the encoder only where it creates target/bin residual improvement.
6. Repeat only while the residual layer still produces fresh signal.

This keeps producing new OOF signal after earlier layers are already strong, and the latest lead-lag layer suggests the useful latent is closer to a small "life-system transition state" than to a generic daily embedding.

## OOF Progression

| Stage | OOF |
| --- | ---: |
| public-feedback anchor | 0.576217 |
| targetwise latent portfolio | 0.575554 |
| conditional routing v2 | 0.574675 |
| conditional routing v4 | 0.574159 |
| conditional routing v7 overlap Q1 | 0.572842 |
| conditional routing v10 focused targets | 0.572533 |
| conditional routing v11 S2 sleep retrieval | 0.571821 |
| conditional routing v12 S2 fine-bin retrieval | 0.571454 |
| conditional routing v13 S2 min40 retrieval | 0.571515 |
| conditional routing v14 S-family retrieval | 0.564962 |
| conditional routing v15 constrained S-family retrieval | 0.567100 |
| conditional routing v17 Q-only on bold S-family | 0.559770 |
| conditional routing v18 Q retrieval layer 2 | 0.558760 |
| conditional routing v19 S retrieval layer 2 | 0.557955 |
| conditional routing v20 retrieval layer 3 | 0.557163 |
| conditional routing v21 Q1/S2 special representation | 0.555880 |
| conditional routing v22 Q1/S2 digest representation | 0.554381 |
| conditional routing v23 joint Q1/S2 digest | 0.554218 |
| conditional routing v24 all-target digest layer | 0.551046 |
| conditional routing v25 joint all-target digest | 0.550644 |
| digest label-aligned encoder targetwise probe | 0.550558 |
| conditional routing v27 temporal digest | 0.545176 |
| conditional routing v29 temporal digest deeper | 0.544772 |
| conditional routing v30 temporal shape on v29 | 0.535694 |
| conditional routing v31 temporal shape constrained | 0.538054 |
| conditional routing v32 temporal shape L2 on v30 | 0.533214 |
| conditional routing v33 temporal shape L2 constrained | 0.534348 |
| conditional routing v34 persistence/regime on v32 | 0.529944 |
| conditional routing v35 persistence/regime constrained | 0.531332 |
| conditional routing v36 burden/streak on v34 | 0.526081 |
| conditional routing v37 burden/streak constrained | 0.526931 |
| conditional routing v38 signed/decay on v36 | 0.521168 |
| conditional routing v39 signed/decay constrained | 0.523087 |
| conditional routing v40 cross-modal synchrony | 0.516460 |
| conditional routing v41 synchrony constrained | 0.517632 |
| conditional routing v42 cross-modal lead-lag | 0.513510 |
| conditional routing v43 lead-lag constrained | 0.514945 |
| conditional routing v44 lead-lag L2 on v42 | 0.513329 |
| conditional routing v45 lead-lag L2 on v43 constrained | 0.514658 |
| conditional routing v46 within-modality temporal motif | 0.512673 |
| conditional routing v47 integrated temporal dynamics | 0.511600 |
| conditional routing v48 state-transition latent | 0.509456 |
| conditional routing v49 state-recurrence novelty | 0.507926 |
| conditional routing v50 state-manifold latent | 0.506657 |
| conditional routing v51 novelty-burden latent | 0.504393 |
| conditional routing v52 novelty-recovery latent | 0.502679 |
| conditional routing v53 integrated state-space latent | 0.500979 |
| conditional routing v54 common PCA/PLS state-space residual | 0.500162 |
| conditional routing v55 local decoder residual | 0.499526 |
| conditional routing v56 metric-attention retrieval residual | 0.498945 |
| conditional routing v57 subject/time-aware attention residual | 0.498600 |
| conditional routing v58 learned neighbor scorer residual | 0.498265 |
| conditional routing v59 residual-contrastive metric residual | 0.497895 |
| conditional routing v60 residual PLS latent objective | 0.497145 |
| conditional routing v61 family/target residual PLS objective | 0.496127 |
| conditional routing v62 cross-family residual PLS objective | 0.495010 |

## Why This Looks Like A Real Direction

- The v7 improvement is not a tiny calibration change: Q1 alone moves from 0.632106 to 0.625482.
- The biggest move is a layer-3 GRU residual encoder applied to Q1 over all rows.
- A Q1-focused encoder adds a second Q1 mid-window correction.
- Overlap routing improves because global and local corrections capture different parts of the same target.
- Subject-level delta vs v4 improves on 8 of 10 subjects.
- Q1 improves on 7 of 10 subjects, with mean Q1 delta -0.006736.
- Q2 also responds to target-only residual encoders: Q2 moves from 0.629741 to 0.628549 in the v10 focused-target router.
- S4 has a smaller but repeatable late-window signal: S4 moves from 0.585298 to 0.584738 in v10.
- S2 does not respond to the same target-only GRU/Transformer residual encoder idea, but it does respond strongly to a different representation: sleep/missingness retrieval residual latent.
- The S2 sleep/missingness retrieval source is bad as a standalone full-day predictor, but becomes useful when routed to the second half / late / tail panel positions. In v11, S2 moves from 0.520188 to 0.515206.
- Fine-bin routing strengthens the S2 signal. In v12, S2 moves from 0.520188 to 0.512639. In the less tiny-bin v13 variant, S2 moves to 0.513065.
- The S2 improvement is not only a single-row artifact: v11 improves 9 of 10 subjects, while v13 improves 8 of 10 subjects with min_train_rows=40.
- The same retrieval residual latent family extends beyond S2. In v14, S1/S3/S4 routed retrieval sources move the OOF from 0.571454 to 0.564962.
- A constrained S-family run with min_train_rows=50, max two moves per target, and min_improvement=0.001 still moves 0.571515 to 0.567100.
- Q targets also respond. With target-filtered Q-only routing, Q1/Q2/Q3 move the bold S-family base from 0.564962 to 0.559770.
- The retrieval residual idea is iterative. A second Q layer moves 0.559770 to 0.558760, then a second S layer moves 0.558760 to 0.557955.
- The second layer is smaller but still target-broad: Q1/Q2/Q3 all improve in the Q layer, and S1/S2/S3/S4 all improve in the S layer.
- A third prefix-matched layer still moves 0.557955 to 0.557163, but Q2 and S3 are now exhausted. The largest remaining third-layer residual is Q1, followed by S2.
- After layer 3, simply adding another generic residual layer is less attractive than creating new target-specific feature families. A Q1/S2 special representation moves 0.557163 to 0.555880.
- The v21 move is concentrated in interpretable target-specific latent families: Q1 responds to social/environment prototype features in the mid panel window, and S2 responds to volatility/circadian residual retrieval features.
- The strongest new jump comes from label-free daily digest features that summarize phone recovery, social rhythm, body recovery, and modality desynchronization. These features move the solution from 0.555880 to 0.550644 after joint routing.
- The digest representation is not isolated to Q1/S2. In v25, every target improves versus the v20 base: Q1 -0.012999, Q2 -0.005490, Q3 -0.008468, S1 -0.001500, S2 -0.007620, S3 -0.001279, S4 -0.008281.
- The broadest subject-level signal is Q3, improving on 8 of 10 subjects; Q1, Q2, S1, and S4 improve on 7 of 10 subjects.
- A shared digest label-aligned encoder-decoder does not beat v25 as a full replacement, but target-wise selection gives a tiny Q2/S3 improvement: 0.550644 to 0.550558. This suggests shared latent is a weak auxiliary, not the main breakthrough path.
- The strongest new signal is subject-relative temporal deviation. Comparing today against each subject's previous 1/3/7-day digest state moves 0.550558 to 0.544772.
- The temporal layer improves every target. The biggest deltas are Q3, S1, Q2, and Q1; S2 also improves on 8 of 10 subjects, which directly supports the “today versus recent self” hypothesis.
- Applying temporal routing after the digest/shared auxiliary base is stronger than attaching it earlier from the older v20 base: v29 reaches 0.544772, while the v28 joint-from-v20 path reaches 0.546506. Ordering matters.
- The next breakthrough is temporal shape. Adding acceleration, short-vs-long momentum, and rolling rank-extreme features on top of v29 moves 0.544772 to 0.535694. A constrained version with fewer/larger moves still reaches 0.538054.
- Temporal shape improves every target in v30. Q3 and S4 are the clearest responders, improving on 9 of 10 subjects; Q1/Q2/S1/S2/S3 improve on 7 of 10 subjects.
- A second temporal-shape residual layer still improves the v30 base: v32 moves 0.535694 to 0.533214, with a constrained confirmation at 0.534348. The remaining signal is concentrated in Q3, S3, Q1, and S4; S2 is close to saturated.
- Persistence/regime features add another independent-looking jump after v32: v34 moves 0.533214 to 0.529944, and a constrained version reaches 0.531332. This captures whether deviation is persisting, recovering, or entering a different short-vs-long volatility regime.
- Burden/streak features add another strong layer: v36 moves 0.529944 to 0.526081, with constrained confirmation at 0.526931. The clearest effects are Q3 and S3, suggesting accumulated shock load is a separate label-predictive axis.
- Signed-burden/decay features add the biggest recent jump after v36: v38 moves 0.526081 to 0.521168, with constrained confirmation at 0.523087. S3 improves on 10 of 10 subjects, which is one of the cleanest target-level signals so far.
- Cross-modal synchrony adds another strong low-dimensional layer: v40 moves 0.521168 to 0.516460, with constrained confirmation at 0.517632. The feature group has only 43 columns, so this is a high signal-to-complexity discovery. S4 is the clearest responder.
- Cross-modal lead-lag adds a new direction after synchrony: v42 moves 0.516460 to 0.513510. This is not just same-day co-movement; it uses only previous-subject-day modality shocks and asks whether they connect to today's shocks in another modality. A stricter sample-applicable version reaches 0.514945, and a second lead-lag residual layer on that constrained base still moves to 0.514658.
- Within-modality temporal motif features add another clean jump after the constrained lead-lag path: v46 moves 0.514658 to 0.512673. The strongest moves are Q2 all-panel motif residual, S2 second-half motif residual, and Q3/S3 residual corrections, so the encoder should preserve whether each modality is worsening, recovering, or reversing, not only cross-modal coupling.
- Re-training a combined temporal dynamics source on top of v46 still improves to 0.511600. This uses synchrony, lead-lag, and motif groups in one target-specific source family, then routes only target/bin slices that improve. The remaining signal is broad but strongest for S2, Q3, and S3, which supports treating these feature families as one encoder state space rather than only independent add-ons.
- State-transition features create the strongest recent jump after v47: 0.511600 to 0.509456. These features compress the current and previous cross-modal shock vector into transition distance, cosine direction, speed/acceleration ratio, dominance, entropy, and modality share shifts. Q3, Q2, S2, S3, and S4 all respond, which is strong evidence that the useful latent should encode movement through a low-dimensional subject-relative state space.
- State-recurrence/novelty features add another strong layer after state-transition: 0.509456 to 0.507926. These features ask whether today's state is close to the subject's own previous 7/14/28-day states or unusual relative to the personal history. S4, Q3, Q2, and S3 respond most clearly, suggesting the label depends not only on transition direction but also on whether that transition is familiar or rare for the subject.
- A combined state-manifold source, trained with both transition and recurrence features after v49, still improves to 0.506657. The main residual is Q3, but every target improves. This suggests the transition and recurrence axes should be learned together in the final encoder rather than kept as completely separate feature blocks.
- Novelty-burden/streak features create another large jump after the state manifold: 0.506657 to 0.504393. The feature asks whether novelty is a one-day event or accumulating over rolling 3/7-day windows. Q2, S4, S1, Q1, and Q3 all respond strongly, which suggests the label-predictive state is not just current novelty but sustained novelty load.
- Novelty-recovery/regime features add signal after novelty burden: 0.504393 to 0.502679. These features distinguish novelty that is worsening, recovering, or changing regime. S4 and Q1 respond most strongly, with every target still improving. This suggests the final encoder should not only measure novelty load, but also whether the subject is entering or leaving that unusual state.
- Integrated state-space features still add signal after novelty recovery: 0.502679 to 0.500979. This run trains transition, recurrence, novelty, and novelty-recovery sources together on the v52 residual. Every target improves again, with the strongest residuals in Q3, S4, Q2, and Q1. The key signal is that the useful latent should not treat transition, recurrence, novelty load, and recovery as separate side features; it should learn them as one personal state-space representation.
- A first explicit common PCA/PLS state-space encoder does not work as a direct full replacement: its standalone sources are much worse than the v53 base. However, when used only as low-weight residual corrections, it still improves v53 from 0.500979 to 0.500162, with a stricter one-move-per-target confirmation at 0.500259. The strongest common-latent residual is S4 all rows, followed by S1 second-half, S2 mid, and Q2 late. This says the common latent is real but the decoder is still too blunt; the next breakthrough is likely a better decoder/objective, not more raw state features.
- Adding local/retrieval-aware decoder features on top of the common latent pushes the internal OOF below 0.50 for the first time: 0.500162 to 0.499526, with a constrained confirmation at 0.499860. The new local decoder is still weak as a full direct predictor, but it exposes another residual layer in S4, S1, S2, S3, Q2, and Q3. The important signal is not the standalone decoder score; it is that local neighbor structure in the common latent keeps explaining residual after v54.
- A target-aware metric retrieval decoder adds another layer after v55: 0.499526 to 0.498945, with constrained confirmation at 0.499183. The metric decoder upweights latent dimensions that separate each target inside the fold, then uses that target-specific distance for KNN residuals. It is selected directly for Q3, S1, S2, and S4 in the bold route, and for Q3/S1 in the constrained route. This strengthens the decoder hypothesis: different labels need different notions of "similar day" in the same common state space.
- A subject/time-aware attention decoder adds another routed residual after v56: 0.498945 to 0.498600, with constrained confirmation at 0.498805. The standalone attention sources are still weak as full replacements, but the router selects same-subject/recency-aware neighbor corrections for Q3 first-half and S1 mid/late, while the strict route keeps the S4 mid residual. This says the neighbor relation should include "same person and nearby day" context, not only geometric distance in the common latent.
- A learned neighbor scorer adds another routed residual after v57: 0.498600 to 0.498265, with constrained confirmation at 0.498450. It builds fold-safe decoder features from latent distance, target-specific metric distance, same-subject mass, temporal recency, and neighbor residual summaries. The important new signal is S3 second-half: `joint_metric_neighbor_hgb` is selected in both bold and constrained routes. This is the first evidence that a learned neighbor relation, not only hand-weighted KNN, can expose new residual structure in the common latent.
- A residual-contrastive metric layer adds another routed residual after v58: 0.498265 to 0.497895. A residual-only route reaches 0.498031, so the new source family is not just piggybacking on older sources. The selected residual metric KNN corrections are broad: Q1/Q2/S1/S2/S3/S4 all use mid-panel residual-aware distance, with the clearest gains in S2 and S3. The strictest constrained route is weaker and keeps only S4 KNN, so this is a breakthrough-signal result rather than an upload-stability result.
- A fold-safe residual PLS latent creates the strongest recent jump after v59: 0.497895 to 0.497145. The residual-PLS-only route reaches 0.497271, so the signal is mostly from the new latent family itself. The strict constrained route reaches 0.497379 and keeps Q1 mid, Q2 all rows, and Q3 late from `joint_residual_pls_knn_resid`. This is the first strong evidence that the residual relation should be a training objective for the latent, not only a post-hoc metric.
- Splitting the residual PLS objective into Q-family, S-family, and per-target latent objectives creates another large internal jump after v60: 0.497145 to 0.496127. A residual-PLS-only route reaches 0.496175 and a stricter one-move constrained route reaches 0.496312, so the new signal is not mainly from older non-PLS sources. The strongest selected moves are S3 all rows from `joint_q_residual_pls_knn_resid`, S4 all rows from `joint_target_residual_pls_knn_resid`, S2 second-half from `joint_q_residual_pls_knn_logitresid`, and Q3 first-half from `joint_s_residual_pls_knn_resid`. This is an important cross-family signal: the latent that explains Q residuals is also useful for S2/S3, and the S-family latent is useful for Q3.
- Explicit cross-family and Q+S combined residual PLS objectives create another large internal jump after v61: 0.496127 to 0.495010. The residual-PLS-only route reaches 0.495018, a new-source-only route reaches 0.495174, and the stricter constrained route reaches 0.495269. The strongest new moves are Q1 first-half from `joint_qs_residual_pls_knn_resid`, Q3 all rows from `joint_cross_family_residual_pls_knn_resid`, Q2 first-half from the same cross-family source, and S4 second-half/late from cross-family residual PLS. This repeats the v61 lesson with a sharper objective: the useful residual latent should mix family-specific subspaces, not isolate them.

## Best Current Breakthrough Candidate

- Bold/best OOF submission: `outputs/conditional_latent_routing_v62_cross_family_residual_pls_on_v61/submission_conditional_latent_routing.csv`
- Bold/best OOF: `0.495010`
- Bold/best report: `outputs/conditional_latent_routing_v62_cross_family_residual_pls_on_v61/report.md`
- Cleaner/constrained OOF candidate: `outputs/conditional_latent_routing_v62_cross_family_residual_pls_constrained_on_v61/submission_conditional_latent_routing.csv`
- Cleaner/constrained OOF: `0.495269`
- Best single-layer lead-lag breakthrough report: `outputs/conditional_latent_routing_v42_leadlag_on_v40/report.md`

Important caveat: v42/v44 are useful as breakthrough-signal probes, but some selected OOF bins have no sample rows. For an upload-style candidate, v43/v45/v46 are cleaner because they require meaningful sample coverage.

## Interpretation

The likely high-potential direction is not a single encoder-decoder trained once.
It is closer to residual boosting in latent space:

- general day latent
- target-specific residual latent
- sequence/history residual latent
- target-only sequence residual latent
- target-specific retrieval residual latent
- label-free daily digest latent: phone recovery, social rhythm, body recovery, modality desynchronization
- target-filtered routing so a source only claims the target it was trained to correct
- iterative residual layers, with expected diminishing returns
- target/bin router that composes multiple latent corrections
- weak shared digest encoder-decoder auxiliary for Q2/S3 only
- subject-relative temporal deviation latent: previous-day delta, rolling 3/7-day delta, absolute delta, and z-score shifts
- temporal-shape latent: second-difference acceleration, short-vs-long momentum, and rolling 7/14-day rank extremeness
- persistence/regime latent: deviation persistence, recovery toward baseline, and short-vs-long volatility regime change
- burden/streak latent: accumulated absolute shock load, rolling shock counts, and consecutive abnormal streak length
- signed-burden/decay latent: positive-vs-negative shock load, exponentially decayed shock memory, and age since last shock
- cross-modal synchrony latent: whether phone, social, body, mobility, missingness, and sleep-proxy shocks co-occur or diverge
- cross-modal lead-lag latent: whether previous 1-2 day phone/social/mobility/missing/sleep shocks lead into today's body/sleep/social shocks
- within-modality motif latent: whether a modality's recent shock trajectory is rising, falling, volatile, or reversing
- state-transition latent: how the cross-modal shock vector moves from yesterday to today, including direction, speed, concentration, and modality-share shift
- state-recurrence latent: whether today's state resembles the subject's own recent history or is a rare/novel state
- state-manifold latent: transition and recurrence jointly trained as one target-specific source family
- novelty-burden latent: whether rare states are isolated or accumulating over short rolling windows
- novelty-recovery latent: whether novelty load is worsening, recovering, or changing short-vs-long regime
- integrated state-space latent: transition, recurrence, novelty burden, and novelty recovery trained as one residual source family
- common PCA/PLS state-space latent: one fold-safe label-aligned latent shared by all seven targets; direct decoder is weak, residual retrieval from the common latent is useful
- local decoder residual: nearest-neighbor labels/residuals, prototype distance, and local density decoded from the common latent; not good as a replacement, useful as target/bin residual
- metric-attention retrieval residual: target-specific diagonal distance metric over the shared latent, making "similar day" label-dependent
- subject/time-aware attention residual: neighbor weights over the shared latent biased toward same-subject and temporally nearby days
- learned neighbor scorer residual: a small fold-safe decoder over neighbor distance, same-subject/time context, and residual summaries
- residual-contrastive metric residual: target-specific latent dimensions weighted by where the current base over- or under-predicts, then used for residual KNN
- residual PLS latent objective: a fold-safe latent trained directly to predict current-base residual vectors before retrieval decoding
- family/target residual PLS objective: fold-safe Q-family, S-family, and per-target residual latents; the surprising signal is cross-family, with Q residual latent helping S2/S3 and S residual latent helping Q3
- cross-family residual PLS objective: fold-safe opposite-family and Q+S combined residual latents; the repeated signal is that residual axes are shared across questionnaire and sleep labels

This is the first run where the encoder route creates a large enough target-level jump to look like a possible main solution path rather than just a marginal add-on.

## Updated S2 Signal

S2 is no longer simply a dead target. It is a representation mismatch target.

- Bad path: more S2-only GRU/Transformer sequence residual. The router found no useful S2 move there.
- Good path: sleep/missingness retrieval residual latent. The useful source is `sleep_missing_knn_resid`, especially around panel position 0.5-0.666, plus a low-weight global `s2_sleep_retrieval_meta` correction.
- Interpretation: S2 may be closer to "how today's sleep/missingness state differs from similar historical days" than to a generic daily sequence embedding.

## Current Breakthrough Hypothesis

The best current hypothesis is now stronger than "S2 needs special handling":

> Label-predictive latent should be trained as target-specific retrieval residuals, not only as a single daily sequence embedding.

The pattern repeats across target families:

- S1: broad sleep/context prototype + sleep_missing mid-window correction.
- S2: sleep_missing residual KNN + retrieval meta correction.
- S3: sleep retrieval meta + connectivity context correction.
- S4: connectivity prototype + broad sleep/context logit residual.
- Q1/Q2: retrieval meta works globally, especially Q2.
- Q3: broad sleep/context residual works in mid/late panel windows.
- Layer 2: smaller but real remaining residual, especially Q1 and S2/S3.
- Layer 3: still positive, but residual is close to saturation; Q1 and S2 are the main remaining targets.
- v21 update: Q1/S2 improve again when the representation changes rather than when the same residual layer is repeated. The current strongest interpretation is Q1 = social/environment/circadian context, S2 = volatility/circadian disruption plus sleep retrieval residual.
- v25 update: the best current hypothesis is broader. The model needs an encoder that compresses a day into a small number of cross-modal deviation axes. Useful axes are phone recovery, social rhythm, body recovery, sleep/recovery meta, and modality desynchronization. This looks more promising than stacking more generic sequence residual layers.
- Shared encoder-decoder update: a single shared PLS/PCA digest latent is too weak as a full replacement, but it improves Q2 and S3 slightly when used target-wise. So the likely main solution is still compositional: target-specific digest/retrieval encoders first, shared label-aligned encoder only as a small auxiliary correction.
- Temporal-deviation update: the best current latent is no longer only “what kind of day is this?” It is “what kind of day is this compared with this subject's recent baseline?” That representation is the first one to push internal OOF below 0.55 and down to 0.544772.
- Temporal-shape update: the newest strongest representation is “how is the deviation moving?” Momentum, acceleration, and recent-rank extremeness push the internal OOF to 0.535694, with a constrained confirmation at 0.538054. This is now the strongest evidence that the label-predictive encoder should model recent self-relative dynamics, not only daily state.
- Temporal-shape L2 update: the same family still explains residual after v30, reaching 0.533214. The gain is smaller, so this looks like diminishing-return residual boosting rather than a new independent jump, but it confirms the direction.
- Persistence/regime update: the latest improvement to 0.529944 suggests the label is not only sensitive to today's anomaly size. It also reacts to whether the anomaly is continuing, resolving, or happening under a changed volatility regime. This is a new interpretable axis, not just another copy of the same temporal-deviation feature.
- Burden/streak update: the newest best score is 0.526081. The strongest targets are Q3 and S3, where rolling shock burden and consecutive abnormal streaks explain residual left after deviation, shape, and regime layers. The current best interpretation is now dynamic state + accumulated stress load.
- Signed/decay update: the newest best score is 0.521168. Directional shock load and decayed memory are not redundant with raw burden. S3 improves on every subject, making this the cleanest evidence yet that the encoder should preserve signed recovery/decay dynamics.
- Synchrony update: the newest best score is 0.516460. A compact 43-column cross-modal shock-synchrony latent improves all targets, with S4 showing a large response. This suggests the encoder should preserve not only per-modality dynamics but also whether multiple life/sensor systems move together.
- Lead-lag update: the newest best breakthrough probe is 0.513329, and the cleaner sample-covered path is 0.514658. This strengthens the hypothesis from "multiple systems move together" to "one system's shock can precede another system's shock." The cleanest targets are Q1, Q2, S2, and S3; S2 specifically still improves in the second lead-lag layer, which suggests it is not fully saturated.
- Motif update: the newest best cleaner score is 0.512673. This is an important signal because it comes after synchrony and lead-lag are already in the base. Q2 improves by 0.004094, S2 by 0.003020, Q3 by 0.003490, and S3 by 0.001973 versus v45. The likely breakthrough shape is now: subject-relative dynamic state, cross-modal system coupling, and per-modality trajectory motif.
- Integrated dynamics update: the newest best score is 0.511600. Re-fitting synchrony, lead-lag, and motif together after v46 improves every target, with the clearest residuals in S2 (-0.002232), Q3 (-0.001628), and S3 (-0.001334). This is the best evidence so far that the encoder should learn a compact temporal dynamics manifold rather than a pile of isolated daily aggregate features.
- State-transition update: the newest best score is 0.509456. The state-transition layer improves every target versus v47, especially Q3 (-0.004654), Q2 (-0.003533), S2 (-0.002043), S3 (-0.001922), and S4 (-0.001566). This is the strongest evidence yet that the encoder should represent "where the subject is moving in latent life-state space" rather than only "what today looked like."
- State-recurrence update: the newest best score is 0.507926. It improves every target versus v48, especially S4 (-0.003545), Q3 (-0.002374), Q2 (-0.001780), and S3 (-0.001492). The current breakthrough hypothesis is now sharper: encode the subject's life-state transition plus whether that transition is recurrent or novel for that subject.
- State-manifold update: the newest best score is 0.506657. It improves every target versus v49, especially Q3 (-0.003466), Q2 (-0.001294), S3 (-0.001260), and S1 (-0.001197). This supports building the final Encoder around a joint personal state-space manifold, not a sequence of unrelated handcrafted corrections.
- Novelty-burden update: the newest best score is 0.504393. It improves every target versus v50, especially Q2 (-0.004463), S4 (-0.003069), S1 (-0.002526), Q1 (-0.002453), and Q3 (-0.002239). The best current Encoder hypothesis is now a personal state-space model with transition, recurrence, and accumulated novelty load.
- Novelty-recovery update: the newest best score is 0.502679. It improves every target versus v51, especially S4 (-0.003796), Q1 (-0.002853), Q2 (-0.001419), Q3 (-0.001307), and S3 (-0.001291). The strongest current hypothesis is a personal state-space encoder that models transition, recurrence, novelty burden, and novelty recovery/regime.
- Integrated state-space update: the newest best score is 0.500979. It improves every target versus v52: Q1 (-0.001326), Q2 (-0.002229), Q3 (-0.003335), S1 (-0.001207), S2 (-0.000469), S3 (-0.000642), and S4 (-0.002690). This is the strongest evidence so far that the final encoder should learn one joint personal state-space latent rather than sequentially bolting on separate transition, recurrence, novelty, and recovery features.
- Common encoder update: the newest best score is 0.500162. The first explicit common `PCA+PLS` state-space latent is not good as a direct multi-head predictor, but it improves v53 when routed as residual correction: Q1 (-0.000110), Q2 (-0.000656), Q3 (-0.000234), S1 (-0.001060), S2 (-0.000753), S3 (-0.000378), and S4 (-0.002531). A stricter confirmation keeps Q2/S1/S2/S4 and reaches 0.500259. The emerging lesson is precise: the shared latent exists, but the decoder must be local/retrieval-aware or target/bin-aware.
- Local decoder update: the newest best score is 0.499526. It improves every target versus v54: Q1 (-0.000054), Q2 (-0.000332), Q3 (-0.000237), S1 (-0.000741), S2 (-0.000528), S3 (-0.000515), and S4 (-0.002043). The constrained confirmation reaches 0.499860 using only S1 second-half and S4 mid moves. The current breakthrough thesis is now sharper: learn a common personal state-space, then decode with local similar-day retrieval/prototype structure rather than a global head.
- Metric-attention update: the newest best score is 0.498945. It improves all non-Q1 targets versus v55: Q2 (-0.000320), Q3 (-0.000892), S1 (-0.000980), S2 (-0.000363), S3 (-0.000256), and S4 (-0.001259). The constrained confirmation reaches 0.499183 using only Q3/S1/S4 moves. The current best thesis is now: common personal state-space encoder plus target-specific learned similarity metric plus local residual decoder.
- Subject/time-attention update: the newest best score is 0.498600. The raw attention sources do not beat the base directly, but routed residuals still improve Q2, Q3, S1, S2, S3, and S4. The constrained confirmation reaches 0.498805 using only S4 mid. The current best thesis is now: common personal state-space encoder plus target-specific metric/local decoder, with neighbor attention that knows whether a candidate day is from the same subject and temporally nearby.
- Learned-neighbor update: the newest best score is 0.498265. The raw learned-neighbor sources still do not beat the base directly, but routed residuals improve Q2, Q3, S1, S2, S3, and S4 again. The constrained confirmation reaches 0.498450 using S3 second-half from `joint_metric_neighbor_hgb` plus S4 mid from KNN. The current best thesis is now: common personal state-space encoder plus a decoder that learns which neighbor evidence matters for each target and panel region, rather than using only fixed KNN weights.
- Residual-contrastive update: the newest best score is 0.497895. The residual-only route reaches 0.498031 and selects `joint_residual_metric_knn_resid` for Q1, Q2, Q3, S1, S2, S3, and S4, concentrated in the mid panel. The current best thesis is now: common personal state-space encoder plus target-specific residual metric learning, where "similar day" means similar latent state and similar current-model error direction.
- Residual-PLS update: the newest best score is 0.497145. A fold-safe residual PLS latent trained on the current-base residual vector improves the v59 base by 0.000750 after routing, and the residual-PLS-only route still reaches 0.497271. Q2 all-row residual PLS is the largest single move, followed by Q1 mid and Q3 late. The current best thesis is now: the encoder should explicitly learn the structure of the current model's residual errors, then decode by retrieval in that residual-aware latent space.
- Family/target residual-PLS update: the newest best score is 0.496127. Splitting the residual objective into Q-family, S-family, and per-target PLS latents improves the v60 base by 0.001018 after routing; the residual-PLS-only route still reaches 0.496175 and the constrained route reaches 0.496312. The strongest signal is not cleanly family-local: Q residual latent improves S2 and S3, S residual latent improves Q3, and target residual latent improves S4. The current best thesis is now: the encoder should learn several residual subspaces and let the decoder mix them, because the latent axes behind questionnaire and sleep targets overlap.
- Cross-family residual-PLS update: the newest best score is 0.495010. Opposite-family and Q+S combined residual latent sources improve the v61 base by 0.001117 after routing; new v62 sources alone reach 0.495174 and the constrained route reaches 0.495269. Q1 is best explained by the combined Q+S residual latent, while Q2/Q3/S4 are best explained by the opposite-family residual latent. The current best thesis is now: train a residual-subspace encoder with shared, family, cross-family, and target heads, then use retrieval in that learned space.
