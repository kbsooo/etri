# Validation Stress Report

작성일: 2026-05-29

현재 목표는 CV 평균이 아니라 hidden-public transfer 가능성을 stress로 판정하는 것이다.

## Stress Families

| stress | current evidence | interpretation | status |
|---|---|---|---|
| random / foldsafe CV | stage2 and JEPA variants can look strong locally | local signal exists but ranking is insufficient | necessary, not sufficient |
| repeated-subject / strict-subject | some MP and cross-view features pass guarded scans | subject identity is not the whole story | useful |
| blockwise / pseudo-hidden block | motif and endpoint methods beat subject mean | hidden block rate latent exists | supported |
| row-order boundary copy | prev/next/both label copy bad | direct label leakage/copy is false | falsified |
| anchor LOO/L2O public proxy | MAE around `0.0005`, oracle lower but selector unstable | public subset underidentified | bottleneck |
| hard selector falsification | `0/36` pairwise models satisfy LOO/L2O MAE `<= 0.00040` plus rank/order constraints | current selector cannot support tiny a2c8-scale deltas | failed |
| hidden subset selector stress | passing selector families `0/7` | selector not reliable enough | failed |
| universe audit | strict resolved-better `0` over broad candidate universe | generation not enough | failed for submit |
| raw05 compatibility | raw05 is strong public anchor, a2c8 tiny better | stay near manifold unless strong evidence | supported |
| bad-axis stress | JEPA direct bad anchors repeated | aggressive latent moves unsafe | supported |
| targetwise calibration stress | Q/S correlations exist, hard constraints can hurt | use soft energy, not hard rules | partially supported |
| label-flow block-rate JEPA stress | semantic pass 1/60, geometry delta `-0.003334`, subject_chunk delta `-0.000537`, but 556 submissions have pair_submit/probe gate 0 | semantic latent exists but direct public-risk translation fails | mixed: keep as gate |
| gated label-flow candidate stress | 7240 dependency/raw05-gated candidates: submit 0, control 50, probe 3263, conflict 0 | gating can create clean information sensors but not a strong submit edge | mixed: probe only |
| targetwise/combo label-flow stress | E12 submit 0; E13 submit 0; E14 focused pair-submit 61/180, conflict 0 | S4+Q3 targetwise gate creates first strict pairwise candidate | supported locally, superseded by E15 for submission |
| focused label-flow independent survival | E15 selected 163 candidates; pair-submit 61; independent survival 0; strict independent survival 0; corr(pair p90, old-selector p90) `-0.881` | S4+Q3 pairwise direction conflicts with independent hidden-subset geometry | failed for submit, useful as sensor |
| selector conflict decomposition | E16 pinned candidates: focused files old hidden-subset better_rate `0.285714`, pairwise full-fit better_rate `0.500000`; tiny E11 sensors pairwise `0.666667` but too small | E14 relied on favorable pairwise tail, not unanimous selector evidence | underidentified |
| S4/Q3 anchor gap audit | E17 pairwise universe has 21 Q3/S4-shaped candidates but none with old-majority support; focused family has 163 pairwise-positive Q3/S4 candidates with old-majority 0; old-positive rescore has 97 old-majority candidates but Q3/S4-shaped 0 | current artifacts lack an independent S4/Q3 positive anchor | failed for submit; redirects next stress |
| S4/Q3 OOF anchor audit | E18 scanned 5167 OOF files; 1578 were local-Q3/S4 strong but OOF anchor-like 0; E19 directly rescored top 399 local OOF candidates and found pair p90 negative 0, pair majority 0, old majority 0, submit/control/probe 0 | local OOF strength is not the missing public anchor | failed as validation source |
| block/measurement selector rescore | E20 scored 3800 non-anchor block/hidden-block/presleep/raw05-block candidates: pair p90 negative 0, pair majority 52, old-majority 3, two-selector majority 0, submit/control/probe 0/0/63, large-lowbad 2505 but large-lowbad two-selector 0 | existing block/measurement universe is not the missing large safe movement | failed for submit; useful as negative evidence |
| selector support topology | E21 merged scored universes: pair-only 465, old-only 97, pair-probe-not-majority 56, two-selector majority 0, strict candidate shape 0 | pairwise and old selectors favor structurally different manifolds; intersection is empty | primary current bottleneck |
| selector disambiguation sensor design | E22: pairwise public-order selector pass 33/36 and raw05 direction correct 0.916667; old hidden-subset selector pass 0/7 and raw05 direction correct 0.0 | old-only support is weakened by the known raw05/A2C8 public order; next public sensor should be pair-only S4/Q3 if any | diagnostic priority only, not improvement evidence |
| label-flow sensor scale curve | E23 scored 108 A2C8-to-S4/Q3 scale/mask variants; pair p90 negative in all mask families, two-selector majority 0 everywhere | scaling reduces old p90 but does not fix old majority; conflict is directional | failed for submit, useful for sensor risk level |
| label-flow localized sensor audit | E24 scored 960 subject/date/block/phase/energy/sign localized variants; pair p90 negative 807, old-majority 0, two-selector majority 0; only 8 loose tiny `id02_b02` sensors with pair p90 around `-2e-7` | simple row localization does not reconcile selectors; the conflict is not just amplitude or coverage | failed for submit; weak diagnostic only |
| direction probe selector reconciliation | E25 scored 22 mixmin/direns/sparseladder/targetabl/inverse7 probes; pair p90 negative 0, pair majority 0, old-majority 0, two-selector majority 0 | newer large-movement score probes do not pass the same hidden-public selector gate | failed for strict submit; high-risk public-probe lane only |
| public LB inverse feasibility | E26 matched 8 known public LBs exactly with all-test soft labels and cell-mixture weights; all 8 unobserved candidate ranges crossed zero even with train-prior bands `±0.05/0.10/0.20` | public LB observations alone do not identify target prior, row subset, or candidate sign | underidentified; selector worldview required |
| public LB structural-prior stress | E27 added global target and subject-target prior bands to all-test inverse LPs; all 7 scenarios fit known LBs with slack 0, but unobserved candidate cells crossed zero `56/56` and one-sided improvement cells were 0 | plausible train/subject priors do not resolve candidate signs | underidentified; subject prior is diagnostic only |
| binary hidden-label inverse stress | E28 binary MILP incumbents: tight subject-prior max residual `0.000061242` below raw05-a2c8 gap, but range MILPs found no one-sided improvement; `6b9335b1` crossed zero under no-prior incumbents | binary exactness can improve anchor realism but does not rank current candidates | incomplete/inconclusive as exact reconstruction; failed as submit gate |
| binary world-pool sign audit | E29 found 15 unique tight-prior binary incumbents but only 1 frontier-scale world; all-world better_rate favored mixmin `0.8667` and inverse7 `0.7333`, while pair sensors were `0.2667-0.3333`; the only frontier-scale world favored mixmin/inverse7 and rejected S4/Q3 pair sensors | binary worlds may prefer the high-risk score-probe lane, but frontier-scale evidence is too sparse | weak diagnostic; failed as submit gate |
| binary frontier-box pool | E30 forced each known-public residual slack <= raw05-a2c8 gap and found 29 frontier-scale incumbents, 28 unique worlds. Non-candidate objectives favored mixmin `19/19` and inverse7 `18/19`, but candidate-max objectives still made both worse | frontier-scale exact-label worlds exist and mostly support score-probe over pair S4/Q3, but signs are not one-sided | stronger diagnostic; still failed as submit gate |
| binary world plausibility geometry | E31 scored E30 worlds by train-only target prior, subject prior, co-occurrence, correlation, cardinality, temporal flip, run-length, and edge-continuity geometry. Mixmin adverse worlds were plausibility ranks 1 and 2 | generic train-label geometry cannot reject adverse score-probe worlds | failed as certification gate; useful for diagnosis |
| binary anchor loss geometry | E32 scored E30 worlds by known-anchor per-target loss decomposition, cancellation, and moved-target/loss alignment. Low-anchor-energy half supported mixmin `15/15` and inverse7 `15/15`; low quarter supported both `7/7`; adverse mixmin worlds were high-energy ranks `26` and `28` | known public anchors prefer the random/fit binary worldview over candidate-adverse worlds, unlike generic train geometry | strongest probe-family diagnostic so far; still not strict certification |
| binary anchor loss LOO stability | E33 recomputed anchor geometry after omitting each known public anchor. Mixmin low-energy half and quarter support stayed `7/7` LOO runs with better_rate `1.0`; no mixmin-adverse world entered any LOO low-energy half | E32 is not driven by one anomalous known anchor | strengthens high-risk mixmin probe; still anchor-derived |
| binary anchor loss family/null audit | E34 family holdout: mixmin survives no-raw05/no-medium/no-bad and only-medium scenarios, but fails under only-bad-JEPA anchors. Target-axis permutation null keeps mixmin one-sided in `500/500` permutations | anchor-loss gate is broad medium-anchor loss/cancellation geometry, not exact target-axis semantics | strengthens probe priority but weakens JEPA-axis semantic interpretation |
| public probe independent evidence audit | E35 joined local direction, label-flow, selector, combo, actual-anchor, anchor-loss, LOO, and family/null evidence for 5 candidate sensors. normal submit gates passing `0`; mixmin has honest CV support and strong anchor-derived support but pair/old selector hard veto remains | no current candidate has certification-grade out-of-anchor evidence; mixmin is the highest-information public sensor, not a validated improvement | strict gate closed; updates diagnostic submission priority |
| raw-structure pseudo-label stress | E36 built 10 train-derived pseudo-label sources from raw features and subject/date structure. inverse7 support `10/10`, mean delta `-0.000705727`; mixmin support `5/10`, mean delta `+0.000065107`; raw sensor train/test AUC `0.607876` | observed raw structure does not independently certify mixmin; inverse7 is a new bridge between raw structure and anchor-loss worlds | strict gate closed; creates inverse7/blend follow-up |
| inverse7 raw-anchor bridge scale scan | E37 generated 22 inverse7/mixmin logit scale/blend variants. raw support gates `14`, anchor low-half+quarter gates `22`, two-selector majority `0`, strict bridge gates `0`; best `inv7_s0p25` still had pair p90 `+0.000035423` and old p90 `+0.000587512` | raw+anchor support can coexist, but selector veto is not amplitude-only and not fixed by simple mixmin blending | strict gate closed; bridge branch remains diagnostic only |
| worldview sensor discriminability audit | E38 joined E32/E33 anchor bands, E35 independent evidence, E36 raw-structure stress, and E37 bridge scan for 10 candidates. normal-submit candidates `0`, public-sensor candidates `10`; top information sensor `mixmin_0c916` score `3.355110` | current decision surface is sensor/worldview ranking, not improvement ranking | strict gate closed; if spending public slot, predeclare sensor question |
| mixmin public sensor observation | E48 public LB for `analysis_outputs/submission_mixmin_0c916bb4.csv` was `0.5763066405`, improving over previous best a2c8 by `0.0011326805` and over raw05 by `0.0012196667` | E38 sensor ranking was public-relevant; pairwise/old selector veto is not a valid hard gate | new frontier; recalibrate selectors with mixmin as known anchor |
| OOF selector calibration audit | E39 scored `4172` OOF rows over label-free future-tail/domain/density/missingness/subject/date/random stresses. strict OOF gates `1311`, conservative gates `1115`; known-public sign match `1.0`, but stage2/ordinal pairwise rank agreement `0.0` | OOF stress is a local stability/overfit screen, not a public worldview selector | strict gate closed; do not rank submissions by OOF gate |
| test-movement fingerprint selector | E40 used target/subject/order/raw-domain/combined movement fingerprints versus A2C8. strict selector views `0`, loose views `4`; combined MAE `0.000781461`, rank accuracy `0.821429`, permutation-null p `0.004`, stage2/ordinal order correct | movement anatomy is informative but underpredicts bad JEPA severity and cannot prove A2C8 best in LOO | strict gate closed; loose prior favors conservative inverse7 bridge over mixmin |
| movement + bad-axis geometry selector | E41 added LOO-safe logit-space axis-group/named cosine and projection features against raw/medium/bad public-anchor movements. strict views `0`, loose views `0`; best `axis_group` MAE `0.000854918`, rank `0.785714`, null p `0.014`, bad-anchor mean underprediction `0.000898399` | bad-axis geometry repairs severity partly, but still fails A2C8-best and cannot become a selector | strict gate closed; do not use axis priors as forecasts |
| fixed-zero anchor selector calibration | E42 kept A2C8 fixed at zero and held out each nonbaseline public anchor. fixed gates `0`, usable gates `0`; best `axis_group` nonbaseline MAE `0.000766262`, rank `0.857143`, null p `0.006`, raw05 gap/MAE `0.113520`, best unobserved advantage/MAE `0.065408` | fixed current-best anchoring improves coarse nonbaseline rank but still cannot resolve frontier-scale candidate edges | strict gate closed; do not submit fixed-zero ranked pair sensors |
| selector resolution boundary audit | E43 compared selector errors and candidate edges against raw05-A2C8 gap `0.0000869862` | frontier-resolution gates `0`; certified better-than-A2C8 `0`; certified better-than-raw05 `0`; best selector error `0.000218288` | current selectors cannot certify micro-edge near-frontier candidates | strict gate closed; require sub-gap selector or larger movement |
| block-state bottleneck audit | E46 joined oracle, Markov, threshold, hidden-block, split-topology, lag, and structured-mask evidence | block-rate oracle `0.517878`; temporal-to-oracle gap `0.106888`; subject identity explains fraction `0.291286`; best Markov `+0.002998`, nested threshold `+0.044275`, endpoint gain only `0.003252`; two-flank hidden blocks `26/36` | 0.54 is structurally possible, but current observed context does not identify hidden block-rate states | supports block-rate JEPA target; no direct submission |
| post-mixmin observation audit | E49 compared mixmin/a2c8/raw05 movement, simple prior CE stress, subject concentration, and train/test calendar masks | train/test is interleaved subject-calendar masking; top movements `Q3/Q1/S3`; `Q1/S1` are adverse under simple priors; high-movement blocks often `gap_adjacent` or `between_train_runs` | mixmin is not ordinary prevalence correction; next selector should model hidden subject-calendar block restoration | no direct submission; build mixmin-relative calendar-block selector |
| post-mixmin calendar selector | E50 added mixmin as a known anchor and tested target/prior, calendar, subject, and subject-calendar movement views | strict views `0`, loose views `0`; best `subject_calendar` MAE `0.000884106`, rank `0.833333`, Spearman `0.833333`, but held-out mixmin predicted delta `0.00135162` and `mixmin_predicted_best=False` | subject-calendar topology is real but not a standalone selector; calendar movement alone does not explain mixmin's public-best edge | no submission; combine calendar context with anchor-loss/binary-world or block-rate target evidence |
| post-mixmin anchor-calendar selector | E51 combined LOO-safe E32-style binary-world anchor-loss aggregates with compact E50 calendar fingerprints | strict views `0`, loose views `0`; best `anchor_residual` MAE `0.000835516`, rank `0.750000`, bad-tail correct, but held-out mixmin predicted delta `0.00241739` and a2c8/raw05 order failed | anchor-loss was public-relevant as a worldview sensor, but the tested aggregate/kNN translation is not a reusable selector | no submission; move to block-rate/count target or mixmin-constrained world stress |
| post-mixmin binary-world sign stress | E52 conditioned E30/E32 binary worlds on actual mixmin public delta and scored 158 candidates versus mixmin | strict better-than-mixmin `0`, loose `0`, near-tie `1`; best near-tie `bridge_blend_m0p75_s1p25` had mixmin-fit-gap better_rate `0.2`, median `+0.000034`, max `+0.000048` | current binary-world family treats mixmin as a local frontier; existing bridge/inverse/pair/JEPA candidates do not replace it | no submission; next needs block-rate/count target or fresh mixmin-hard world generation |
| calendar-flank block count-state probe | E53 predicted pseudo-hidden block count/rate state from labeled flanks and donor signatures, then scored real hidden-block mixmin deltas | local pseudo-hidden delta `-0.005266`, strict subject-excluded delta `+0.001434`; strict hidden mixmin delta `-0.000179`, local `+0.000250`; strict target alignment S3/S2/Q2 favorable but S1/Q1/Q3/S4 adverse | calendar flanks carry local subject signal but not a private-safe target recovery latent; simple count posterior is energy, not a candidate source | no submission; next needs richer raw context, target-dependency count manifold, or mixmin-hard worlds |
| raw overnight block context probe | E54 predicted pseudo-hidden block count/rate state from raw overnight feature-family PCA block embeddings plus flank context | best strict `night_phone_rawctx_strict_k8_a24` pseudo-hidden delta `-0.007733`; S3 target delta `+0.007802`; actual hidden mixmin delta for same method `+0.000311`; best hidden alignment still `calendar_count_strict` `-0.000179` | raw overnight context is a real strict representation, but it is not the public/mixmin latent and fails target-sign stress | no submission; use as energy/private-risk stress, then resolve S3 or regenerate mixmin-hard worlds |
| raw block target-dependency projection | E55 projected E54 raw block rates through strict donor Q/S target-rate manifolds | `225` methods, joint gates `0`; S3 subject replacement raw delta `-0.001115` but hidden mixmin `+0.000319`; best hidden-sign Ridge `-0.000414` but pseudo-hidden LogLoss `0.727319` | target-rate projection cannot jointly preserve raw recovery, fix S3, and align mixmin sign | no submission; move to mixmin-hard world generation or structural target representation |
| mixmin-hard raw world generation | E56 regenerated binary worlds with mixmin as a hard public observation and E54 raw hidden block rates as feasibility energy | `45` worlds, `44` unique; existing candidate strict gates `0`; posterior world-LOO strict gates `12`; best internal posterior median delta `-0.154291`, p90 `-0.069887`, max `-0.069103` | hard-world family can create coherent posterior structure, but internal world consistency is not public safety | require independent anchor stress before submission |
| mixmin-hard posterior safety stress | E57 reconstructed posterior variants and scored them with actual-anchor/public-shape proxy plus movement guard | `15` variants; joint safety gates `0`; mixmin anchor score `0.577734`; best posterior delta `+0.000123`; E56 selected diagnostic delta `+0.020381`, mean abs logit move `0.381359` | direct E56 posterior movement is public-anchor adverse | no submission; use E56 posterior only as teacher/energy |
| mixmin-hard posterior distillation stress | E58 gated E56 teacher by band/target/cell/row/cap/weight and actual-anchor scored prefiltered candidates; E61 repaired candidate/prediction identity with stable `pred_index` | `104727` generated, `1200` scored; toward eligible gates `0`; corrected toward sign beats `126/900`; best toward anchor delta `-0.000004081`; reverse best `-0.0000000126`; world guard true for top toward candidates | simple distillation can make E56 non-adverse but not selector-scale useful; rejection survives the scoring-index audit | no submission; need structural block target or independent validation |
| structural block target representation | E59 predicted 128-state block joint label-pattern distributions from strict raw/calendar/subject contexts | `219` methods, joint gates `0`; pattern NLL beats raw in `139/216`; own-margin joint gain in `198/216`; row LogLoss beats raw in `0/216`; best pattern delta `-0.062594` but row delta `+0.003678` and hidden mixmin `+0.000304`; best hidden sign `-0.000367` but row delta `+0.042230` and S3 `+0.078145` | joint target structure is learnable, but within-block pattern prediction is not the public-aligned probability translation | no submission; use as diagnostic energy only |
| transition-residual block-state stress | E60 predicted strict subject-excluded logit-rate residuals from endpoints/raw/subject baselines and topology/raw contexts | `438` methods, joint gates `0`; row beats raw `1` and it is raw baseline; residual MSE beats raw `227`; hidden mixmin negative `217`; best hidden sign `-0.001569` but row delta vs raw `+1.519232` and S3 `+1.331880` | transition residual can sense hidden mixmin direction but only by collapsing pseudo-hidden calibration | no submission; use as teacher-risk diagnostic only |
| transition-gated posterior distillation stress | E62 used E60 transition residual views only as gates for E56 posterior teacher cells, then E56-world and actual-anchor stressed candidates | `363258` generated, `1300` scored; eligible gates `0`; best toward anchor delta `-0.000002716`; reverse best `-0.00000000547`; best gate was balanced transition sign plus raw agreement and no S3 | transition residual gating is weaker than corrected E58 and does not validate E56 at selector-scale margin | no submission; transition residual stays diagnostic, not a standalone validator |
| gradient-consensus posterior stress | E63 used subject/calendar/raw/transition hidden-rate views as BCE-gradient guards for E56 teacher cells, then E56-world and actual-anchor stressed candidates | `404671` generated, `1300` scored; toward hidden guard `1000/1000`, world guard `1000/1000`, anchor beats `932/1000`; reverse hidden/world guards `0/300`; best toward anchor delta `-0.000003650`; eligible gates `0` | E56 direction is real-looking under independent hidden-rate views, but selector-scale amplitude is still missing | no submission; use gradient consensus as direction validator, not as a submit gate |
| gradient-amplitude translation stress | E64 expanded scale/cap on E63 gradient-consensus cells, then stressed world/hidden/movement/actual-anchor | `12096` generated, `1796` scored; toward hidden/world/movement guards `1346/1346`; toward anchor beats `0/1346`; best toward anchor delta `+0.000003024`; reverse best `+0.000000154` | scalar amplitude makes validated E56 direction public-anchor adverse | no submission; amplitude must be learned/targetwise or replaced by structural target |
| near-zero amplitude response stress | E65 ran small targetwise line search around E63 gradient-consensus cells | `27384` generated, `2400` scored; toward hidden/world/movement guards `2290/2290`; anchor beats `1753/2290`; best toward delta `-0.000005995`; margin gates `0`; best target mask `no_q2_s3` | near-zero targetwise pocket exists but is still below selector margin | no submission; target-conflict translator needed |
| Q2/S3 conflict add-back stress | E66 held E65/E63 cells fixed and decomposed matched target-mask add-backs against `no_q2_s3` | `3000` generated/scored; `no_q2_s3` best `-0.000005995`; `all` add-back robust-anchor adverse `432/432`; mean-anchor improves `288/432`; max-set tail worsens `432/432`; hidden core improves `432/432`; `q2` and `q2_s3` anchor beats `0` | Q2/S3 are hidden/mean-favorable but public-tail risky, so target exclusion is not a semantic solution | no submission; require tail-neutral Q2/S3 translator before another E56 teacher file |
| tail-neutral Q2/S3 translator stress | E67 added Q2/S3 back by first-order anchor-scenario tail gates while preserving E65 non-Q2/S3 movement | `7632` generated/scored; best delta `-0.000006933`; strict p90-tail gate best `-0.000006587`; matched-base beats `4207/7200`; max-set-tail-neutral matched beats `2241/7200`; margin gates `0` | tail gates improve over masks but remain sub-margin and anchor-derived | no submission; next stress must independently validate tail-gated cells |
| Q2/S3 tail-gate independence stress | E68 rebuilt selected E67 tail configs with each combo set held out from gate construction, then added hidden/world/block Q2/S3 stress | selected `180`; unique scored predictions `762`; matched pairs `540`; independent gates `155`; strict gates `155`; `tail_soft_max_m1.00` strict `44`; `tail_p90_nonpos_m1.00` strict `41`; best strict heldout `-0.000001261`; strongest heldout `tail_max_nonpos_m1.00` `-0.000001630` but block gate `0` | E67 is not purely same-anchor arithmetic, but the validated edge remains below selector-scale margin | no submission; next stress is calibrated amplitude or structural use of strict E68 cells |
| Q2/S3 strict-cell amplitude stress | E69 scaled only the Q2/S3 logit delta of E68 strict cells over alpha while fixing non-Q2/S3 at matched `no_q2_s3` base | strict pairs `155`; rows `2170`; unique predictions `2061`; strict amplitude gates `0`; full-combo margin gates `0`; best all delta `-0.000009178`; heldout tail-neutral falls from `155/155` at alpha `1` to `22/155` at alpha `24` | E68 cells are valid-looking but simple alpha amplification still does not clear selector margin and degrades heldout/tail stability | no submission; next stress must be rowwise/cellwise amplitude or structural target |
| Q2/S3 strict-cell consensus stress | E70 aggregated the `155` E68 strict cells into pooled bases and Q2/S3 consensus deltas, then combo-scored and hidden/world/block stressed the promising rows | candidate rows `2688`; unique predictions `2576`; strict consensus gates `6`; loose gates `502`; best all delta `-0.0000102775`; all strict rows used `gate=none` and all `3/3` combo sets beat base/tail-neutral | consensus accumulation is live and reaches local margin, but conservative agreement gates do not produce strict rows and the construction is not yet a unified test-time rule | no submission; next stress is unified-rule consensus or consensus-energy gating |
| Unified Q2/S3 strict-cell consensus stress | E71 rebuilt each unique E68 strict cell once with the full combo family, then rescored consensus rows under the same E70 strict/loose diagnostics and a deployable `gate != none` requirement | strict rows `155`; unique cells `104`; support-2 cells `51`; candidate rows `3136`; unique predictions `2842`; strict unified gates `1`; deployable gates `0`; loose gates `475`; best all delta `-0.0000108217`; only strict row used `gate=none` | unified consensus is a real diagnostic signal, but still not a conservative deployable probability rule | no submission; require non-`none` gate or rowwise/cellwise amplitude before file generation |
| Sparse-magnitude unified Q2/S3 gate geometry | E72 swept sparse magnitude, soft agreement, sign agreement, Q2-only, S3-only, and target-agreement gates over E71 unified cells; E73 materialized the best deployable row | rows `4752`; unique predictions `4752`; strict rows `21`; deployable non-`none` rows `10`; loose rows `655`; `top_abs50` deployable `7`, `s3_only` deployable `3`, Q2-only deployable `0`; best deployable all delta `-0.0000105458`; selected file `submission_e72_topabs50_q2s3_gate_4e48cba2.csv`; later public LB `0.5764077772` | E71's non-`none` failure was too broad locally, but E80/E81 show the materialized combined file is public-adverse and pure Q2/S3 is sub-margin | no direct follow-up; use sparse magnitude as latent energy only |
| Sparse Q2/S3 gate stability and amplitude ridge | E74 stressed the E73 13-cell full pool with leave-one-cell-out, group/rank subsets, and 60 deterministic bootstrap8 subsets; then materialized the full-pool alpha20 reference row | rows `470`; variants `94`; strict/deployable `141`; loose `470`; jackknife alpha16 deployable `13/13`; bootstrap8 alpha16 deployable `48/60`; reference alpha20 all delta `-0.0000107261`, hidden Q2/S3 `-0.000484506`, world support `-0.000351115`; reference alpha24 fails strict | E73 is not single-cell fragile; alpha20 is a plausible but riskier amplitude ridge, not an unlimited scale direction | keep E73 as first public sensor; use `submission_e74_fullpool_a20_q2s3_gate_55455b60.csv` only as second amplitude diagnostic |
| Target-specific Q2/S3 sparse amplitude ridge | E75 fixed the E74 full pool/gate and crossed Q2/S3 target alphas, then materialized the best deployable asymmetric row | rows `120`; strict/deployable `37`; loose `109`; `s3_higher` deployable `23`; `s3_only` `6`; `q2_only` `0`; best deployable `q2=8`, `s3=28`, all delta `-0.0000123676`, hidden Q2/S3 `-0.000372692`, world `-0.000200351`, block win `0.722222`; selected file `submission_e75_q2a8_s3a28_sparse_amp_f07219b4.csv` | symmetric alpha20 is not locally optimal; S3-heavy/Q2-low amplitude is a live public-readable hypothesis | use after E73 if testing target-asymmetric amplitude; keep E74 as symmetric control |
| Target-specific Q2/S3 amplitude subset stability | E76 crossed the E75 target-alpha pairs over the same 94 reference/jackknife/group/rank/bootstrap source-pool variants used by E74 | rows `1974`; variants `94`; strict/deployable `1138`; loose `1894`; exact `asym8_28_e75` beats sym16/sym20 in `94/94`; exact `asym8_28_e75` deployable `49/94`; jackknife `8/13`; bootstrap8 `28/60`; best deployable axis S3-heavy `94/94` | target asymmetry is direction-stable, but exact `q2=8/s3=28` is only partially stable and riskier than E73's alpha16 sign | E75 remains high-information target-asymmetry sensor; E73 stays first; E74 stays symmetric-control fallback |
| Q2/S3 amplitude posterior aggregation stress | E77 aggregated E76 source-subset predictions as logit-space posterior movements from mixmin/E73/E74 across robust aggregators, scopes, and shrink values | rows `6840`; strict/deployable `0`; loose `3099`; rows beating E75 local all-combo `62`; best all `-0.0000126541` but hidden/world adverse; mixmin/q2s3 best `-0.00000809547` with safe tail/hidden/world/block; mixmin/full best `-0.0000125991` but only `1/3` combo sets beat base and `1/3` tails neutral | generic source-subset posterior averaging does not repair exact-amplitude instability; safe Q2/S3 movement is sub-margin and full movement is tail/set unsafe | no submission; next amplitude stress must condition on combo-set/tail/row-block risk rather than average E76 variants |
| Q2/S3 localized amplitude gate stress | E78 converted E76 exact/deployable/S3-heavy/deployable-vs-failed source distributions into reliability masks over E75 sparse unit movement | rows `4452`; masks `36`; strict/deployable `1806`; loose `3934`; deployable rows beating E75 `0`; best all equals E75 `-0.0000123676`; strong sign masks remain deployable but weaker; excess/veto masks shrink too much | source-subset reliability masks do not repair exact-amplitude instability; deployability without E75 upside is not a candidate | no submission; wait for public sensor or use richer public-like row/block/tail localization |
| Public-like row/block Q2/S3 amplitude gate stress | E79 applied topology, topology x positive unit-energy, subject-prior, subject-id, nearest train-label flank, and target-specific flank masks over E75 sparse movement | rows `6516`; masks `61`; strict/deployable `1318`; loose `3403`; deployable rows beating E75 `0`; best all equals E75 `-0.0000123676`; E75 active movement covers `72/250` rows/cells; positive-energy top30/top50 cuts active rows to `22`/`36` without improving edge | handcrafted row/block/flank masks do not repair exact-amplitude instability; full active sparse movement remains local optimum | no submission; keep row/block context for structural target design, not direct masks |
| E73 public observation assimilation | E80 treated public LB `0.5764077772` for `submission_e72_topabs50_q2s3_gate_4e48cba2.csv` as a sensor and decomposed moved cells versus mixmin | public delta `+0.0001011367`; local expected delta `-0.0000105458`; public/local edge ratio `9.590x`; moved cells `893`; active rows `249`; active targets all `7`; Q2/S3 cells `79`; non-Q2/S3 cells `814` | the submitted E73 file is a failed combined all-target sensor, not a clean isolated Q2/S3 public-sign test | pause E74/E75 direct follow-ups; split pure Q2/S3 before another sparse-gate file |
| Pure E73 Q2/S3 graft split | E81 grafted only E73 Q2/S3, Q2-only, S3-only, non-Q2/S3-only, and inverse-sign controls onto mixmin, then applied existing combo/hidden/world/block stress | rows `8`; strict/deployable `0`; loose `3`; pure Q2/S3 all delta `-0.000005954` with `3/3` combo-set wins and `3/3` tail-neutral; pure S3 `-0.000005665`; inverse Q2/S3 `+0.000014747` and local guards fail | isolated Q2/S3 latent is locally real but below submission margin; public-sign inversion is not justified | no submission; next work needs combo-set/tail-calibrated or structural target gate |
| Pure Q2/S3 source-graft scan | E82 reconstructed E72/E75/E76 source predictions, grafted only Q2/S3/Q2/S3-only values or source-base deltas onto mixmin, combo-filtered, and non-anchor stressed the promising rows | rows `8402`; non-anchor evaluated `700`; strict/deployable `0`; loose `700`; best evaluated all delta `-0.000007903`; non-margin guards passed `700/700`, but all-margin passed `0/700` | pure Q2/S3 source universe is directionally coherent and tail-safe but too small for submission-scale margin | no submission; use Q2/S3 as latent energy inside broader structural/block-state movement |
| Q2/S3-energy structural gate scan | E83 used E82 top-20 Q2/S3 energy as row gates over broad structural submission deltas from block consensus/rawcorrector families | rows `3716`; non-anchor evaluated `700`; strict/deployable `0`; loose `40`; structural-loose `189`; best evaluated all delta `-0.000035052`; broad best rows beat only `2/3` sets and worsened Q2/S3 hidden/world; E72-safe rows pass loose but stay sub-margin | structural margin and Q2/S3 safety are separable but not yet co-resident | no deployable submission; recombine target groups |
| Structural margin plus Q2/S3 safety recombination | E84 added E83 non-Q2S3 structural deltas and only Q2/S3 components from E72-safe rows | rows `1728`; non-anchor evaluated `700`; strict/deployable `0`; loose `700`; structural-loose `700`; best evaluated all delta `-0.000032150`; margin/hidden/world/block pass `700/700`; raw-energy pass `672/700`; all failures are `2/3` combo sets/tails because inverse-top rejects `700/700` | additive target-group recombination solves Q2/S3 safety but exposes a public-observation set conflict | no safe submission; materialized diagnostic `submission_e84_inverse_sensor_1c74da00.csv` only if testing inverse-top public relevance |
| Inverse-top conflict target-prune | E85 applied target subsets to E84 movement and rescored the same all-combo, inverse-top, raw05-compatible, all-sign, hidden/world/block, and tail diagnostics | rows `10135`; non-anchor evaluated `700`; strict/deployable `535`; loose `588`; best materialized `S1,S2,S3` file has all delta `-0.000023876`, inverse-top `-0.000008167`, raw05-compatible `-0.000029555`, all-sign `-0.000033906`, hidden core `-0.000161`, hidden Q2/S3 `-0.000216`, world `-0.000130`, block win `0.666667`, block tail safe `0.944444` | E84 inverse-top failure is target-axis contamination first: Q1/Q3/S4 movement is adverse, while S1/S2/S3 structural movement survives all stress families | promote `submission_e85_inverse_conflict_pruned_58b23ed1.csv` as the next public candidate |
| E85 target-prune source-consensus robustness | E86 averaged source-diverse strict E85 logit-delta rows by target mask, source-file/seed-rank/top-row selection, and shrink stress | rows `1485`; non-anchor evaluated `700`; strict/deployable/loose `700/700`; selected `Q2,S1,S2,S3` mean top-40 shrink `1.25`; all delta `-0.000027706`, inverse-top `-0.00000691`, raw05-compatible `-0.000035339`, all-sign `-0.000040869`, hidden core `-0.000239`, hidden Q2/S3 `-0.000378`, world `-0.000307`, block win `0.833333`, block tail safe `1.0` | the E85 target-prune law is source-stable and can gain margin by consensus, not a single-row/source artifact | promote `submission_e86_e85_consensus_a3f7c96f.csv` as the highest-upside next public sensor; keep E85 as conservative fallback |
| E86 risk decomposition contrasts | E87 rebuilt the E86 consensus pool and selected no-Q2, no-overstep, and inverse-top-prior variants under the same strict/deployable stress | rows `1485`; strict/deployable universe `700`; no-Q2 all delta `-0.000026946`; no-overstep all delta `-0.000024255`; inverse-top-prior inverse-top delta `-0.000020643`; all three submissions valid and non-NA | E86's public risk is no longer underidentified: Q2 add-back, shrink overstep, and inverse-top geometry can be separated by one contrast after E86 feedback | do not promote above E86; use as follow-up public sensors only |
| Frontier movement attribution | E88 compared mixmin-vs-a2c8, E72-vs-mixmin, and E85/E86/E87-vs-mixmin movement in target-cell, row, calendar/raw-domain, and prior-proxy geometry | E86 E72 overlap ratio `0.819288`, contamination index `0.772379`, E72 row corr `0.725471`, mixmin signed cell corr `-0.758417`; no-Q2 contamination index `0.730408`; no-overstep same geometry as E86; inverse-top-prior contamination index `0.928415` | E86 is a high-upside target-pruned rollback, not a safe continuation of mixmin; no-Q2 is the cleanest contrast, while inverse-top-prior is high-information but E72-contamination-proximate | use E88 as a risk lens before another public slot; if E86 fails, test no-Q2 before inverse-top-prior unless the goal is pure public-world geometry |
| E86/E72 decontamination scan | E89 built controlled mixmin-relative E86 repairs: E86/no-Q2 blends, high-E72 row/cell fallback to E85/no-Q2/mixmin, rowwise Q2 removal, and projection away from E72 failed movement | rows `52`; evaluated `52`; strict/deployable `37/37`; selected `submission_e89_e72decontam_00d7807f.csv` uses E86 with E85 fallback on top-20% E72 cells; all delta `-0.000025896`, inverse-top `-0.000005554`, raw05-compatible `-0.000033315`, hidden Q2/S3 `-0.000216060`, world `-0.000140452`, block tail safe `0.944444`, contamination index `0.676361` | E72 proximity can be lowered below E86/no-Q2/E85 without collapsing strict stress, but the repair sacrifices E86's stronger hidden/world/block edge | use as risk-adjusted public sensor if downside control is preferred over E86 maximum local margin |
| E89 Pareto-knee selector | E90 rescored strict E89 rows for the tradeoff between E72 decontamination and E86 structural retention | eligible strict rows `13/37`; selected `submission_e90_e72pareto_28925de5.csv`, E86 with E85 fallback on top-10% E72 rows; all delta `-0.000026932`, contamination `0.715784`, world `-0.000250999`, hidden Q2/S3 `-0.000299838`, block win `0.777778`, tail safe `1.0` | minimum contamination is not the only local optimum; a row-coherent balanced point preserves more hidden/world/block energy while staying cleaner than E85/no-Q2 | use when the public question is structural retention vs contamination removal |
| E72-updated selector collapse audit | E91 added E72 as a known public anchor to the movement-fingerprint proxy and scored only post-mixmin candidates | known anchors `10`; best LOOCV proxy `raw05_a2c8_compat` MAE `0.000543412`, p90 error `0.001010234`; mixmin LOO error `+0.001142722`; E72 actual delta vs mixmin `+0.0001011367` but predicted E72-minus-mixmin `-0.0000460726` | known-LB movement regression still cannot resolve the frontier/E72 distinction; it is not a selector for E86/E90/E89 | no E91 submission; keep E86/E90/E89 as predeclared sensors rather than proxy-ranked candidates |
| Hidden-block posterior alignment audit | E92 scored E72/E85/E86/no-Q2/E90/E89 against hidden-block posterior rates, endpoint rates, block-target R2, high-posterior-shift block focus, and E72 failed-direction agreement | known public-negative E72 is the hidden-block alignment leader; posterior CE delta E72 `-0.000287300`, no-Q2 `-0.000257196`, E86 `-0.000255621`, E90 `-0.000250767`, E89 `-0.000235903`; E89 has highest block-target R2 `0.356204` and lowest E72 mass agreement among E86/E90/E89 `0.635838` | hidden-block posterior is E72-tainted as a public selector. It is useful representation diagnostic, not submission ranker | no E92 submission; keep posterior CE, block R2, and E72 contamination as separate stress axes |
| Target-manifold counter-energy audit | E93 fitted train-label target-conditional models and empirical pattern/correlation energies to test whether Q/S dependency rejects E72 | E72 target-manifold delta mean `-0.001468687` vs mixmin; live candidates also favorable but smaller (E86 `-0.000921783`, E90 `-0.000877945`, E89 `-0.000806467`); older public-bad anchors can score very well (`final9` `-0.020801364`, bad-Q2 JEPA `-0.002958703`) | train target dependency is also E72-tainted as a public selector. E72 failure is not explained by obvious Q/S manifold violation | no E93 submission; use dependency/manifold metrics as diagnostics only, not candidate ranking |
| Soft-health / hard-label tail audit | E94 measured candidate LogLoss exposure under the hard labels that would make E72's active cells wrong | E72 full adverse exposure `0.002330945`; actual miss is only `4.3389%` of that scale; live tail exposure E85 `0.000739201`, E89 `0.000799109`, E90 `0.000934031`, E86 `0.001010242`; hard-tail known-public Spearman up to `0.866667` vs soft-health `0.081935` | soft representation health can hide a small but public-relevant hard-label LogLoss tail | no E94 submission; every future soft JEPA-style health metric needs a hard-label tail check |
| Hard-tail localized gate scan | E95 converted E94 hard-tail exposure into controlled E86/E90 row/cell fallback gates and separated raw tail minimization from strict structural survival | rows/evaluated/strict `178/178/112`; strict non-dominated `19`; selected `submission_e95_hardtail_541e3973.csv`; all delta `-0.0000262074`, E72-adverse tail `0.000788914`, hidden Q2/S3 `-0.000251140`, world `-0.000132931`, block win `0.750000`, tail safe `0.972222`; active targets `Q2,S1,S2,S3` | hard-tail exposure is not only a diagnostic lens; it can localize a new strict candidate that beats E89 on tail and margin. Non-strict raw tail minimization remains a rollback trap | submit E95 if the next public slot should test hard-tail bottleneck directly |
| Public-miss budget tail scenarios | E96 fixed E72 public miss as a total LogLoss budget and allocated it across deterministic/random E72-adverse hard-tail worlds | complete scenarios `3894/3894`; failed E72 reconstructs `0.0001011367`; E95 mean `0.000057874`, p95 `0.000115644`, live win-rate `0.527478`; E85 p95 `0.000115304`; E89 mean `0.000059964`, p95 `0.000117735`; E95 beats E89 `0.712378`, E90 `0.999486`, E86 `0.998973` | E95 is robust as a mean/win-rate hard-tail sensor, but the most conservative p95 floor is still E85. Diffuse Q2/Q2S3-bottom tails are the main E95-vs-E89 failure modes | no new submission; keep E95 top for information-rich hard-tail localization, E85 for pure downside-floor testing |
| E95 public observation | `submission_e95_hardtail_541e3973.csv` was submitted after E96 selected it as the top information-rich hard-tail sensor | public LB `0.5762913298`; delta vs mixmin `-0.0000153107`; delta vs failed E72 `-0.0001164474`; realized gain is `58.42%` of E95 local all-combo margin | hard-tail localization is public-positive, but the small edge shows this is a localized calibration/tail repair rather than hidden block-rate recovery | promote E95 to current frontier; next stress should be E95-relative |
| E95-updated known-LB proxy stress | E98 added E95 as the 11th known public anchor and reran fixed LOOCV movement proxies over E95/mixmin/E72 and post-E95 candidates | best proxy `raw05_a2c8_compat` p90 abs error `0.000816497`; p90 is `53.33x` E95 edge and `8.07x` E72 miss; E72-minus-mixmin sign remains wrong; future proxy spread `0.000015142` | E95 is valuable as a public anchor, but known-LB regression still cannot resolve the frontier scale | reject H92; do not rank E90/E86/E85 by proxy-predicted LB |
| E95-conditioned tail transfer stress | E99 solved `public_delta = alpha * local_delta + lambda * E96_tail_delta` per E96 scenario using the observed E72 miss and E95 gain | solved `3894/3894`; broad-plausible scenarios `3452`; broad alpha/lambda median `3.310470/1.345192`; best mean/best p95/winner mode all E95; beat-E95 rates E89 `0.195829`, E85 `0.031866`, E90 `0.002607`, E86 `0.000290` | once E95 is conditioned in, more E86 structure is not the leading expected-improvement explanation. The remaining counterfactual is whether E95 over-localized the tail versus E89's diffuse cell fallback | no E99 submission; E89 becomes the sharper E95 counterfactual, while E90/E86 remain explicit structure-retention/upside sensors only |
| E89 counterfactual anatomy | E100 decomposed the E99 broad-plausible worlds by mask/order/family and tail surplus | broad-plausible `3452`; E89 beat-E95 `0.195829`; mean E89-minus-E95 `+0.000003833`; E89-beating cases `676`, top mask `q2s3`; `q2s3` slice beat rate `0.779891`; E89-not-beating cases top mask `s1s2s3` | E89 is a Q2/S3 diffuse-tail sensor, not a broad successor to E95 | submit E89 only to test Q2/S3 over-localization. If it fails, close E89 as a near-term improvement branch |
| E101 Q2/S3 tail graft probe | E100's Q2/S3 diffuse-tail pocket isolated as E95-relative rollback/graft candidates | rows/grafts/strict-like/pass `618/612/581/54`; selected `submission_e101_q2s3tail_177569bc.csv`; only `50` active cells vs E95; all delta `-0.0000253724`; E72-adverse exposure `0.000692235`; broad mean vs E95 `-0.0000162053`; beat-E95 `0.983488`; broad p95 vs E95 `-0.000001564`; Q2/S3-slice beat `1.0` | a smaller E95-relative Q2/S3 rollback tests the E100 hypothesis more cleanly than full E89. It keeps E95's structural law but reduces Q2/S3 tail amplitude | next public sensor should be E101 before E89 if the question is E95 Q2/S3 over-amplification |
| E102 E101 active-cell structure audit | E101's `50` active Q2/S3 cells converted into a row/cell atlas and tested with target-count-preserving permutation nulls | active cells/rows/blocks/subjects `50/48/26/10`; max cells per block `4`; edge-or-near-edge rate `0.620` vs null `0.471289`, p `0.016999`; mean edge distance `1.680` vs null `2.138444`, p `0.040848`; max cells per block p `0.997300`, subjects touched p `1.0` | E101 is mainly target-axis amplitude/edge-local calibration, not a hidden subject/block-local selector | no E102 submission; use E102 only to decide the branch after E101 public feedback |
| E103 edge-local Q2/S3 amplitude probe | E102 edge/active/interior/top-gap masks scanned as E95-to-mixmin rollback variants under the inherited E101 stress frame | variants `180`; E103 pass `12`; E101-dominating rows `0`; best passing active-all alpha `0.375` mean/p95/beat vs E95 `-0.000023425`/`-0.000002159`/`0.980881`; E101 reference `-0.000016205`/`-0.000001564`/`0.983488`; edge-only p95 positive | edge proximity is diagnostic but not a stronger selector than E101. Higher-amplitude active-all variants buy mean/p95 at the cost of beat-rate, while edge-only masks fail p95/strict safety | no E103 submission; keep E101 as next sensor and use edge energy only for post-E101 branching |
| E104 E101 amplitude Pareto-cliff audit | E101/E103 active masks fine-scanned over alphas `0.000-0.500` by `0.005` under the same E95-conditioned transfer frame | variants `505`; E101-pass rows `228`; E101-dominating rows `0`; active-all first alpha above E101 with beat loss `0.255`; alpha `0.255` mean/p95 gains vs E101 only `~3.02e-7`/`~2.6e-8` with beat gap `-0.000289687`; best passing active-all alpha `0.380` mean/p95/beat vs E95 `-0.000023695`/`-0.000002181`/`0.980881`; edge/interior pass rows `0` | E101 alpha `0.25` is a local Pareto point, not a grid accident. Higher rollback amplitude is a risk tradeoff, not a clean successor | no E104 submission; keep E101 as next sensor |
| E105 E101 public-label break-even anatomy | E101-minus-E95 hard-label deltas computed on the `50` active cells, then simulated under global and subject train priors | active cells Q2/S3 `11/39`; all-support/all-adverse deltas `-0.000096679`/`+0.000211677`; minimum high-impact support cells to beat E95 `23/50`; S3 flip-benefit share `0.935862`; global-prior expected delta/beat probability `+0.000048971`/`0.016610`; subject-prior `+0.000007854`/`0.335360` | E101 is not a global-prior improvement. It is a subject/block-local S3-heavy hard-label sensor | no E105 submission; use it to interpret E101 public feedback |
| E106 E101 subject-prior gate audit | E105's subject/S3 label clue converted into subject-support, subject-expected, flip-benefit, S3-only, and prior-ranked E95-to-mixmin rollback variants over alphas `0.25/0.50/0.75/1.00` | variants `268`; E101-pass `12`; prior-healthier `56`; interesting non-replacements `6`; replacement rows `0`; dominating rows `0`; `active_s3_all` alpha `0.25` mean/p95/beat `-0.000015728`/`-0.000001195`/`0.973349` vs E101 `-0.000016205`/`-0.000001564`/`0.983488` | subject prior is an interpretation/risk energy, not a pre-feedback replacement selector | no E106 submission; keep E101 as next sensor |
| E107 E101 feedback decision map | E104 amplitude and E106 subject-prior candidates conditioned on six hypothetical E101-vs-E95 public deltas inside E99 broad-plausible tail worlds | candidates `292`; outcomes `6`; summary rows `1752`; edge win/small win/tie within-tolerance; strong win/loss outcomes nearest/tension; edge/small wins rank E104 active-all high-alpha first, while strict E101-pass follow-ups are lower-alpha; E106 masks do not outrank E104 | E101 win -> amplitude-up branch; E101 loss -> E99/E101 world-model tension, not subject-prior rescue | no E107 submission; use after E101 LB |
| E120 post-E101 public observation audit | actual E101 public LB applied to E116 decoder and loss-side stress records | E101 public `0.5763003660`; delta vs E95 `+0.0000090362`; delta vs mixmin `-0.0000062745`; E116 `small_loss`; actual public was `+0.0000252415` worse than local E101 mean and `+0.0000106001` worse than local p95; E110 non-control strict candidates `0`; E119 E101-dominating rows `0` | E95 remains standing law; E101 is a resolved negative sensor and the local transfer model underestimated loss-side public tail | no same-family submission; rebuild public-world model around E95/E101 boundary |
| E121 exact E101 small-loss inverse posterior | observed E101-vs-E95 public delta converted into hard-label support budget over the `50` active Q2/S3 cells; `300000` label worlds per prior | observed delta requires `0.657165` of active flip benefit; greedy top-flip support first beats mixmin at `21`, matches observation near `22`, and first beats E95 at `23`; local/flank exact-observed world rates `~0.044-0.047`, global `0.007963`; exact worlds have top10 support `~0.81-0.86` and S3 support `~0.58-0.60` | E101 small loss is a knife-edge S3-heavy hard-label boundary, not a broad invalidation or an amplitude tuning invitation | no E121 submission; require an independent non-public sensor for missing high-impact S3 cells before any same-line file |
| E124 E101-conditioned tail transfer audit | E99 two-term transfer solved from E72/E95 only, with E101 used as held-out public sensor and future candidates rescored inside E101-plausible worlds | broad-plausible `3452`; predicted E101 mean `-0.000031516` vs actual `-0.000006275`; E101 order-match `57`; E101-plausible `57`; E95 live win rate `0.929825`; future E95-beat rates E89 `0.052632`, E85 `0.017544`, E90/E86 `0` | E99 hard-tail attribution is real but incomplete; E101 exposes a boundary variable not captured by local+E72-tail transfer | no submission; do not inherit pre-E101 candidate order |
| E125 E101 survivor anatomy | E124 E101-plausible worlds contrasted against all E99 broad worlds by scenario family, mask, gamma, alpha, and E101-vs-E95 tail relation | E101 survivors `57/3452`; `all`/`e72_top50_hard` `43/57`; `q2s3` `0/368`; deterministic or gamma0 `40/57`; median alpha `3.310470 -> 0.791985`; median `tail_e101-tail_e95` `-0.000012634 -> ~0` | E101-compatible worlds are broad transfer-shrink/tail-neutral worlds, not Q2/S3 diffuse-tail worlds | no submission; leave same-line Q2/S3 rollback unless a new independent sensor appears |
| E126 E101 survivor cell-budget anatomy | E124/E125 survivor scenarios expanded to selected E72-adverse cells and joined to target, E101-active, fallback, hidden-block, row-position, and context metadata | E101-plausible q2s3 mass share `0.180513`; E101-active mass share `0.011234`; E95-fallback mass share `0.356179`; between-train-runs mass share `0.621562`; broad-q2s3 E101-active share `0.584840` | E101-compatible public loss budget is mostly outside the cells E101 changed; the residual is low-alpha broad transfer-shrinkage, not hidden active-cell Q2/S3 allocation | no submission; close E101/E89/Q2S3 same-line variants by default |
| E127 transfer-shrinkage predictability | E126 E101-plausible cell budget treated as teacher; public-free scenario proxies and hidden-block-heldout metadata views scored against it | `broad_tail_equal` JS `0.038002`, cosine `0.945388`, top50 truth-mass `0.293969`; `broad_q2s3` JS `0.508660`; best metadata view `target_context_tail_e72bin` CV JS `0.073253`, top50 truth-mass `0.252521`; target-only JS `0.316796` | transfer-shrinkage is visible in tail-neutral/low-alpha geometry and weak metadata, but simple metadata is not a direct action gate | no submission; use tail-neutral density as representation target/negative gate |
| E128 transfer-shrinkage energy candidate audit | known public anchors and live E85/E86/E89/E90/noQ2 candidates scored by tail-equal E95-law alignment, active/Q2S3 rollback, E72-adverse exposure, and a composite risk index | component Spearman with public delta: `q2s3_delta95_l1` `0.958042`, `tail_equal_law_resid_ratio` `0.888112`, `e72_adverse_exposure_e101_plausible` `0.881119`, `e101_active_delta95_l1` `0.874126`; composite risk Spearman only `0.440559`; low-risk live ranking E85/E89/noQ2/E90/E86 | transfer-shrinkage energy is useful as a veto/decomposition, but the scalar ranker conflicts with post-E101 world stress | no submission; keep energy components separate and require E124/E126-style stress plus selector-scale movement |
| E129 transfer-shrinkage Pareto universe audit | full local/report-referenced `submission*.csv` universe deduped and filtered by separated E128 veto components plus E101-scale material movement | paths `116044`; unique tensors `65865`; strict veto `3`, all same-family; strict actionable `2` = E85 and E101; relaxed material adds E89; novel strict actionable `0` | existing files do not hide a novel transfer-shrinkage-safe successor. Low-energy region is the already-known post-E101 same-family line | no submission; stop old-file rank search and build new representation/movement |
| E130 tail-density synthesis probe | E95-relative donor interpolation under E127 tail-equal/low-alpha/density masks, scored by local E95 strictness, E129 separated vetoes, and post-E101 sensor stress | variants `1792`, evaluated `698`; local strict `25`; E129-veto-actionable before local strict `19`; local-strict plus veto-actionable `0`; submit gate `0`; best local strict `-0.000001512` vs E95 but post-E101 sensor-adverse; safest rows were immaterial micro-moves | transfer-shrinkage density is not a direct probability translator. Local upside and veto-safe geometry currently occupy different regions | no submission; use density as representation/veto target, not as an E95 blend rule |

## Bottleneck Categories

### A. 데이터 신호 부족

- 상태: 증거 약함.
- 이유: hidden block motif, measurement-process residuals, cross-view JEPA surprise all show real signal. E46 makes this sharper: validation block-rate oracle reaches `0.517878`, so the label table contains a 0.5x path if hidden block rates are inferred.
- 제한: row-level direct signal is weak; much of the signal is block/calibration/measurement-process, not direct deterministic labels.
- 결론: signal is not absent, but signal-to-public-transfer is low.

### B. Validation mismatch

- 상태: 강한 증거 있음.
- 이유: local OOF/CV improvements repeatedly fail public LB, especially JEPA latent residuals and ordinal/subject corrections. E39 makes this sharper: many OOF-stable candidates pass strict local gates, but OOF reverses the known public ordering between stage2 and ordinal. E40 shows test-movement fingerprints improve that specific ordering but still miss bad-JEPA severity. E41 adds bad-axis geometry and improves severity, but still fails A2C8-best and all gates. E42 then fixes A2C8 as a known zero anchor and still cannot reach frontier resolution. E43 confirms that even the best selector error is larger than the raw05-A2C8 edge, so no local selector was reliable at previous-frontier scale. E48 sharpens the mismatch: the local strict gate vetoed mixmin, but mixmin improved public by `0.0011326805`.
- 결론: primary plateau component.

### C. Public subset mismatch

- 상태: 강한 증거 있음.
- 이유: inverse public masks can fit anchors, but LOO/L2O-selected masks fail to produce submit-gate candidates. E26 shows known public LBs can be fit exactly by many hidden worlds, and important candidate deltas still cross zero even with train-prior bands. E27 shows this remains true after adding global target and subject-target prior bands. E28 shows binary hidden labels can fit anchors more realistically under tight priors, but still do not provide stable candidate signs. E29 shows a small binary world pool gives only one frontier-scale world; E30 fixes that by forcing a frontier residual box and still finds adverse candidate worlds. E31 shows those adverse worlds are plausible under train-label dynamics. E32 then shows known-anchor loss decomposition, unlike generic train geometry, assigns those adverse worlds high energy. E33 shows this is stable under leave-one-anchor-out. E34 shows the signal is medium-anchor/broad-cancellation driven rather than target-axis semantic. E35 says this was not enough for normal certification, but E48 validates it as public-relevant: mixmin became the best public anchor. E45 directly tests simple subject/order/date/raw-domain public subset recovery and finds zero selector-scale masks, with feasible ranges far too wide.
- 결론: primary plateau component.

### D. Target prior mismatch

- 상태: 증거 있음, direct action unsafe.
- 이유: subject target prior differences are large; target correlations exist. But ordinal/count/prior corrections hurt public, and E27 shows subject-target prior constraints do not identify current candidate signs.
- 결론: use target prior as energy/gate, not hard correction.

### E. Representation/capacity problem

- 상태: 증거 있음, 그러나 0.54급 돌파는 미확인.
- 이유: JEPA/cross-view latents show local gains. Label-flow/block-rate has one semantic stress pass and downstream OOF gains, but direct probability translations fail public pairwise gates. Gated translation first produced clean probes, then S4+Q3 focused gate produced strict pairwise candidates, but E15 failed independent survival. E20 shows many block/measurement movements exist, including 2505 large low-bad moves, but none get two-selector support. E25 shows even newer large sparse/minimax probes with strong honest-CV/combo metadata do not pass pairwise/old strict stress. E44 extends this from individual archives to 29 scored tables and finds zero normal large-safe candidates. E45 says even if public subset is masked, simple mask recovery does not rescue those representations. E46 reframes the useful representation target: not raw reconstruction or row logits, but held-out block-rate vectors, because subject identity, Markov transitions, endpoints, and one-feature thresholds recover only a small part of the oracle gap. E47 shows the current block-summary views do not solve that target either: best row-blend delta `-0.001505`, but block-rate loss is worse than temporal and oracle-gap recovery is only `0.014083`. E54 then shows capacity is not absent: raw overnight context recovers strict pseudo-hidden block state by `-0.007733`, but its actual hidden mixmin sign is adverse (`+0.000311`) and S3 regresses. E55 shows a simple target-rate manifold does not translate this latent: joint gates `0/225`. E56 shows hard-world generation capacity is also not absent because posterior world-LOO gates open, but E57 shows direct public-safe translation still fails. E58 shows even simple anchor-constrained distillation only reaches sub-`1e-5` anchor movement. E59 shows an even richer 128-state joint pattern target is learnable, but row calibration and hidden mixmin sign still separate. E60 shows transition residuals can create a much stronger hidden-sign signal, but only by destroying pseudo-hidden row calibration and S3.
- 결론: not simply capacity. Useful representations and world posteriors exist, and E63 shows E56 direction survives independent hidden-rate gradient checks. E64 then shows scalar amplitude expansion breaks actual-anchor sign, E65 finds only a sub-margin near-zero targetwise pocket, E66 shows Q2/S3 add-back can improve hidden/mean terms while worsening public-anchor tails, E67 shows first-order tail gates can improve the translator but still stay below submission margin, E68 shows many of those tail-gated cells survive held-out combo plus hidden/world/block stress, E69 shows simple alpha amplification still stays below margin while eroding tail stability, E70 shows consensus aggregation can barely cross local margin, E71 shows the same branch is not purely heldout arithmetic but sign/agreement gates fail, and E72 shows sparse-magnitude gates can be deployable. Public-aligned translation is deeper than simple target-rate dependency, unconstrained posterior averaging, simple teacher slicing, joint-pattern prediction, transition-residual hidden-sign moves, transition-only gating, direction-only gradient consensus, larger scalar movement, small targetwise line search, target masking without tail-risk control, anchor-derived tail gating alone, independently validated micro-edges without amplitude, global alpha over validated cells, heldout-specific consensus averaging, unified disagreement-permissive consensus, or sign-agreement-only consensus.

### F. Candidate selection problem

- 상태: 강한 증거 있음.
- 이유: many candidates exist, and pre-E48 strict submit-gate was 0. E20 adds 3800 block/measurement candidates and still finds pair p90 negative 0 and two-selector majority 0. E21 shows the merged support topology has pair-only 465 and old-only 97 but two-selector majority 0. E22 shows the old-only branch is not the next best sensor because it fails the known raw05/A2C8 public direction. E25 shows the larger score-oriented probe branch also lacks pairwise/old support. E29-E30 favor mixmin/inverse7 more than pair-only S4/Q3 inside binary-world diagnostics, E31 shows generic geometry cannot remove adverse worlds, E32 shows known-anchor geometry can downweight those adverse worlds, E33 shows the downweighting is LOO-stable, E34 shows it is not target-axis-semantic enough to be certification, E35 shows the missing independent evidence still has not been found for mixmin, E38 ranks mixmin as the maximum-information sensor, and E48 validates that ranking on public LB.
- 결론: candidate selection was both the bottleneck and the breakthrough. The old strict gate was too conservative; the next selector must explain mixmin rather than merely veto it.

## Current Submission Gate

Strict gate requires:

- public-observation consistency;
- anchor LOO and L2O order preservation;
- blockwise stress survival;
- targetwise calibration neutrality or improvement;
- raw05 compatibility or justified deviation;
- low bad-axis energy;
- seed/model-family stability;
- prediction diversity without instability.

Current result after E126: `analysis_outputs/submission_e95_hardtail_541e3973.csv` is the active public frontier with LB `0.5762913298`, and `analysis_outputs/submission_e101_q2s3tail_177569bc.csv` is a resolved negative E95-relative sensor with public `0.5763003660`. E101 generated `618` rows, `581` strict-like grafts, and `54` pass rows; the materialized file changes only `50` effective cells vs E95, but the actual public result is E116 `small_loss`: worse than E95 by `0.0000090362` while still beating mixmin by `0.0000062745`. E121 shows that this boundary requires `0.657165` of active flip benefit and sits between greedy top-flip support counts `22` and `23`: one high-impact S3-scale cell separates "beats mixmin" from "beats E95". E122 then separates explanation from action: simple subject/flank/raw priors forecast the observed small-loss branch almost exactly (`raw_full_subject_prior_y1` expected `+0.000008889`), while E119 local transfer predicted the wrong sign (`-0.000016205`). E123 rejects the obvious Q/S transition-motif rescue. E124 rejects inheriting the old E99 broad order. E125 rejects the narrower E100 residual story: `q2s3` worlds have `0/368` E101 survivors, while E101-plausible worlds are broad/all-tail, low-alpha, and E101-vs-E95 tail-neutral. E126 closes the active-cell loophole: only `0.011234` of E101-plausible selected budget mass lands on E101-active cells. The revised gate blocks E108/amplitude-up, subject-prior masks, flank-gated replacement, full E89, non-active grafts, E121/E122 posterior-fitted gates, E123 transition-motif gates, pre-E101 E99-ranked successors, Q2/S3-mask residual worlds, and E101-active cell masks unless a genuinely independent S3-cell sensor or different hidden-structure hypothesis appears.

Update after E123: cross-target transition motif is not that independent sensor. The clean no-S3 motif failed temporal-tail S3 validation by `+0.135183` logloss versus subject prior, and full/plus-subject motif heads failed by `+0.246239` and `+0.349065`. Interleaved validation was also worse. The decisive rank-23 S3 cell stayed support-like (`0.943564` no-S3, `0.984326` plus-subject), while motif aggregate expected deltas overshot the actual E101 small-loss branch (`~+0.000028` vs `+0.0000090362`). The same-line gate remains closed, and transition motifs are now a LeJEPA-style collapse/shortcut warning rather than a submission feature.

E46 adds that the next normal-submission path is unlikely to be another row-level candidate at all. The block-rate oracle is `0.517878`, but most tested context translations do not recover it: full subject identity leaves `0.075753` mean logloss gap to the oracle, Markov is worse than temporal, nested thresholds are worse, and endpoint reconstruction only gains `0.003252` over subject mean. E47 then tests the direct fold-safe block-summary target head and also fails the representation gate: best 25% row blend is `-0.001505`, but block-rate loss is worse than temporal by `0.012440` and oracle-gap recovery is only `0.014083`. E49 changes the next representation context: train/test calendar masks show hidden subject-calendar blocks. E50 then says those masks alone are not a selector, E51 says anchor-loss aggregates plus those masks are not a selector, E52 says existing candidates do not beat mixmin after conditioning binary worlds on mixmin, and E53 says simple calendar-flank count posterior is not strict-safe. E54 says richer raw overnight context can recover a strict block-state latent, E55 says target-dependency rate projection does not fix its mixmin/S3 conflict, E56/E57 say mixmin-hard posterior generation is real but must be constrained, E58 says simple constraints are too small, E59 says within-block joint label-pattern structure is real but not public-aligned, E60 says transition residual hidden-sign is not calibration-safe, E62 says transition residual is not the simple E56 gate, E63 says hidden-rate gradient agreement is direction evidence but not amplitude evidence, E64 says scalar amplitude is actively adverse, E65 says near-zero targetwise amplitude remains sub-margin, E66 says Q2/S3 mean/hidden gains can still be public-tail adverse, E67 says first-order tail gates are directionally useful but anchor-derived and sub-margin, E68 says many of those gates survive independent held-out/non-anchor stress, E69 says global alpha amplification still fails, E70 says consensus can produce a small margin, E71 says unified consensus remains diagnostic but not deployable under sign gates, and E72 says sparse magnitude can be deployable. Future block-rate work should use calendar flanks, hidden run topology, raw overnight context, transition/topology risk, E56 posterior energy, E68 strict Q2/S3 cells, E70/E71 consensus energy, and E72 sparse-gate energy, but the target/evaluation must include rowwise/cellwise margin-scale amplitude, not submission-file similarity, current-candidate sign rescoring, simple local donor counts, raw-context gains alone, target-rate smoothing, raw posterior averaging, sub-margin distillation, joint-label kNN alone, aggressive endpoint-residual moves, transition-only masks, gradient agreement alone, larger scalar scale, tiny line-search tweaks, target masking without tail-risk accounting, first-order anchor-tail gates alone, independent micro-edges alone, global alpha over validated cells, heldout-specific consensus averaging, unified `gate=none` consensus, or sign-agreement-only consensus gates.

E94 adds a final post-E72 gate separation: soft-health metrics and hard-label LogLoss tails are different claims. A latent can improve posterior CE or target-manifold consistency while still carrying enough adverse hard-label exposure to lose public. E95 then turns that warning into a controlled candidate: hard-tail cells can be locally de-risked without fully abandoning E86, but raw tail minimization alone creates non-strict rollback traps. E96 adds the missing conditional-budget stress: the total E72 public miss does not identify the realized cells, so the correct robustness check is a family of complete-budget tail worlds. E97 validates this sequence on public: E95 becomes the new frontier, but only by `0.0000153107`. E98 adds the negative selector check: one more public-positive anchor is still not enough for known-LB regression to rank the next file. E99 adds the positive/negative transfer check: a simple local+tail model can coherently explain E72 and E95, but it keeps E95 on top and makes E89 the only nontrivial E95 counterfactual. E100 makes that counterfactual narrower: E89 is mainly a Q2/S3 diffuse-tail test, not a general candidate. E102 then removes the simplest block-mask follow-up to E101: the active cells are too spread across subjects/blocks for a handcrafted subject/block mask to be justified, but their edge proximity is a weak calibration-risk signal. E103 closes the direct edge-selector shortcut: edge-only masks do not dominate E101 and should remain a stress energy. Future stress should report soft representation health, hard-tail exposure, strict structural survival, conditional budget robustness, actual public-anchor reaction, E95-conditioned transfer, Q2/S3 diffuse-tail concentration, E101 edge-localization, E103 edge-selector failure, and selector-resolution sanity before a file is promoted.

## Next Stress Design

1. Post-E101 high-impact S3-cell sensor search: E121 already modeled the two-point hard-tail boundary, and E122 shows that existing simple subject/flank/raw priors explain the small loss but do not identify a deployable stop cell. The next diagnostic is not another E95-to-E101 amplitude variant. It should ask whether a genuinely different non-public signal identifies the missing high-impact S3 support/adverse cells that keep E101 below E95. Without that evidence, same-line submissions are closed by E120-E122.
2. Full E89 diffuse-tail test: `analysis_outputs/submission_e89_e72decontam_00d7807f.csv` should be used only after E101 if the goal remains broader E72-cell fallback rather than small E95-relative rollback, and only as an explicit sensor because E110 rejected it as an automatic loss-side rescue.
3. Conservative same-hypothesis fallback: `analysis_outputs/submission_e85_inverse_conflict_pruned_58b23ed1.csv` should be used if the goal is to isolate lower-amplitude `S1,S2,S3` target-prune without E86's Q2 add-back and shrink `1.25` overstep, or to test pure downside floor.
4. E95-relative row-coherent structure test: `analysis_outputs/submission_e90_e72pareto_28925de5.csv` should be used only if the explicit question is whether public accepts more retained E86 row-level hidden/world/block structure than E95 after the worst E72 rows are removed. E99/E101 make it a weak expected-improvement file.
5. E95-relative max-upside structure test: `analysis_outputs/submission_e86_e85_consensus_a3f7c96f.csv` remains the highest-upside file, but E99 makes it high-risk as an E95-beat bet. It tests whether public accepts a source-stable `Q2,S1,S2,S3` structural consensus despite higher hard-tail exposure than E95.
6. Current public frontier: `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv` is now the active anchor with public `0.5761589494`. Future stress should compare against E247, not E95/mixmin, unless the question is historical attribution or body attribution.
7. E95-updated selector sanity: E98 rejected the proxy-ranked path, E99 keeps E95 best after conditioning tail worlds on E95, E101 shows that a small rollback can be better than full E89, E102 rejects a strong block/subject-local interpretation of that rollback, E103 rejects direct edge-only replacement, E104 rejects fine-grid higher-alpha replacement before public feedback, E106 rejects subject-prior-gated replacement before public feedback, E107 maps the post-E101 branch rather than creating a new file, E109 closes same-line rescue after a tie/loss, E110 closes simple non-active-tail rescue after a tie/loss, E111 shows the frontier movement is S-heavy target-axis surgery rather than broad all-target movement, E112 explains why Q temporal signal should not be blindly copied into test, E113 shows visible raw context does not safely replace that missing Q temporal context, E114 shows raw context does not pre-validate E101 active-cell support labels, E115 shows E101 remains the highest-actionability sensor among pending controls, E116 pre-registers the exact public LB decoder, E117 shows the documented submission universe has no untested lower-tail E95-like replacement, E118 shows visible train flanks support but do not certify the E101 transition-state world, and E119 shows flank/support gates cannot replace the full E101 active-set rollback before public feedback. Do not use predicted LB from the known-LB movement regression, unconditioned E96 tail means, handcrafted active-cell block/edge/subject-prior/flank masks, active-restored/non-active grafts, broad Q/Q3/S4 movement, direct Q1/Q3 temporal propagation, raw-coverage heads, E101 raw-support scores, E101 flank-support scores without negative expected delta, loss-heavy raw split information, old-submission universe search, conditional E108 files, or post-hoc reinterpretation outside the E116 bands to choose E90/E86/E85 before E101.
8. E87 contrast queue after E86 feedback: `analysis_outputs/submission_e87_noq2_source_consensus_a85c4e39.csv`, `analysis_outputs/submission_e87_q2_nooverstep_consensus_acd7add0.csv`, or `analysis_outputs/submission_e87_inverse_top_prior_consensus_5445ec28.csv`, chosen by which risk axis needs falsification.
9. Public sensor for E72/E75 sparse-magnitude Q2/S3 consensus is now resolved negatively for the submitted combined file: `analysis_outputs/submission_e72_topabs50_q2s3_gate_4e48cba2.csv` scored `0.5764077772`, worse than mixmin by `+0.0001011367`. E80 shows that file moved all targets, E81 shows the isolated E73 Q2/S3 graft is only loose/sub-margin, and E82 shows the broader pure Q2/S3 source universe is still margin-limited. Do not submit E75/E74 or pure Q2/S3 grafts as direct follow-ups.
10. Rowwise/cellwise amplitude or latent use of E68/E70/E71/E72/E74/E75/E76/E77/E78/E79/E82 Q2/S3 cells: E63 validates direction, E64 rejects scalar scale, E65 says the best local pocket excludes Q2/S3 but remains sub-margin, E66 says Q2/S3 add-back is hidden/mean-favorable while worst-tail adverse, E67 says first-order tail gates improve but remain below margin, E68 says selected Q2/S3 cells survive held-out/non-anchor stress, E69 says global alpha amplification still fails, E70 says consensus aggregation can barely clear local margin, E71 says unified reconstruction keeps one strict row but no sign-gate, E72 says sparse magnitude can open deployable rows, E74 says that sparse gate is cell-subset stable but amplitude has an upper boundary, E75 says the boundary is target-asymmetric rather than symmetric, E76 says the S3-heavy direction is subset-stable while exact `8/28` is only partially deployable, E77 says generic source-subset posterior averaging cannot reconcile margin with tail/set consistency, E78 says source-subset reliability masks do not improve over E75, E79 says handcrafted row/block/flank masks also do not improve over E75, and E82 says pure Q2/S3 grafts pass non-margin stress but cannot reach margin. The next stress should use Q2/S3 as energy inside a broader learned structural state, not as the sole movement.
11. Structural block target redesign v2: E59's within-block joint pattern target is learnable but target-mismatched, and E60's transition residual target is sign-informative but unsafe. The next target must include block transition/topology, calendar hidden-run context, and mixmin/raw disagreement energy while explicitly constraining row calibration and S3.
12. Post-mixmin attribution: decompose `mixmin - a2c8` by target, row-order band, subject-like block, raw-domain, probability-confidence bucket, and prior-contradiction class, then ask which cells E50/E51 failed to price.
13. Gate separation: split the old strict gate into public-sign evidence, private-risk warning, and information-sensor value. E48 proves these cannot be one boolean; E50/E51 prove calendar/anchor kNN cannot be the replacement boolean.
14. Raw-structure bridge retest: revisit inverse7 only as a mixmin-relative bridge, not as a replacement chosen by pre-E48 selector veto.
15. Block-state JEPA work remains the only visible 0.54 path. Future block-context targets must beat temporal block weighted LogLoss directly, not just produce a row-level blend gain.

## Update After E131

E131 adds a sharp stress verdict to the current submission gate. The post-E101 transfer-shrinkage branch now has three closed shortcuts:

- E129: existing submission universe has no novel strict actionable survivor.
- E130: direct tail-density donor interpolation has local-strict rows and veto-safe rows, but no overlap.
- E131: even local+safe atom combinations and hard-tail clipped local variants keep the same disjointness.

The stress result is numerically strong: `6384` candidates, `651` local-strict, `208` veto-actionable, `0` in the intersection, and `0` with negative post-E101 sensor mean. The current gate therefore blocks any E95 successor whose only rationale is "local E86/E90 low-alpha upside plus transfer-shrinkage-safe correction." A future candidate must pass the separated vetoes before correction, not after blend surgery.

## Update After E132

E132 closes the donor-free tangent shortcut. The tested branch no longer depends on E86/E90/E85/E89 donor files; it computes direct E95 combo-set gradients and masks them into transfer-veto regions.

The result is again disjoint:

- gradient candidates: `4590`.
- evaluated candidates: `698`.
- gradient local-strict rows: `0`.
- gradient veto-actionable rows: `843`.
- local-strict plus veto-actionable rows: `0`.
- submit-gate rows: `0`.

The strongest local gradient move is large enough to matter locally (`-0.000112772` versus E95), but it fails hidden/block/Q2S3/world support and has positive post-E101 p95 exposure. The best post-E101 sensor rows improve the sensor mean but do not become local-strict. Therefore the gate now blocks both old-donor correction and current E95 tangent-gradient movement. The next stress target should be a new structural latent, not another E95-neighborhood probability perturbation.

## Update After E133

E133 maps the cell-level reason E132 failed. The best context is `all_sign`, but even there only `16.1830%` of local reward mass lies inside veto-null+density70. The target mix changes sharply after safety filtering: `all_sign` local top50 is `44%` Q2/S3 and `42%` S3, while co-located top50 is only `2%` Q2/S3 and `0%` E101-active, with `40%` Q3 and `34%` Q1.

The hidden-block CV stress also rejects a simple metadata target. The best category view is `subject_target` with JS `0.240700` and top50 truth-mass capture `0.048280`, only weakly above a flat top50 baseline. Thus E133 does not create a submission gate. It changes the next stress design: the live latent target is now a Q3/Q1-heavy safe remainder that simple metadata cannot recover, not a Q2/S3 rollback or a direct E95 gradient.

## Update After E134

E134 tests the obvious next context for that E133 remainder: raw overnight/run/block structure. The result is only weakly positive.

- best predictor: `night_all_blockknn` / `target_knn8`.
- top50 truth-mass capture: `0.073497`.
- best metadata-only top50 truth-mass capture: `0.063040`.
- best top50 target mix: `Q1:37,Q3:4,S4:9`.
- Q2/S3 fraction in best predicted top50: `0.000000`.

This is useful as a stress result, not as a submission gate. Raw/block context does suppress Q2/S3 and slightly improves top-cell recovery, but it does not materially recover the safe-remainder field. The current validation gate therefore blocks direct raw-block co-location submissions. The next candidate needs a different target or movement source, not another ranking over the E133 field.

## Update After E135

E135 tests the other cheap context for the E133 remainder: the existing prediction manifold.

- best prediction-manifold predictor: `row_prediction_pca_meta` / `ridge`.
- top50 truth-mass capture: `0.063430`.
- best metadata-only top50 truth-mass capture: `0.063040`.
- E134 raw/block reference top50 truth-mass capture: `0.073497`.
- best top50 target mix: `Q1:11,Q3:38,S4:1`.
- Q2/S3 fraction in best predicted top50: `0.000000`.

This blocks a second direct submission path. Existing submissions and their disagreements do not recover the safe remainder better than raw/block context and barely exceed metadata. The validation gate therefore rejects old-prediction-manifold ranking, old-submission disagreement gates, and E133/E134/E135 score translation unless a future target representation materially increases hidden-block-heldout recovery.

## Update After E136

E136 changes the status of the representation branch. The cell-level safe-remainder target was weak under both raw/block and old-prediction contexts, but the same teacher becomes much more visible after block-target compression.

- best compressed predictor: `block_target` / `all_raw_views_raw_pred` / `ridge`.
- top10 truth-mass capture: `0.332698`.
- top10 enrichment over random: `3.326980`.
- oracle top10 capture ratio: `0.709652`.
- best pure raw block-target predictor: `night_all_raw` / `ridge`, enrichment `3.236095`.
- row-total best enrichment: `1.181643`.
- cell references: E134 raw/block enrichment `2.572395`, E135 prediction-manifold enrichment `2.220050`.

This reopens a narrow JEPA-style target-redesign path. The current stress gate still blocks a submission because E136 has not produced a calibrated probability movement, but it changes the next validation target: do not try to rank individual E133 cells; test whether block-target state can generate cell movement that survives transfer-shrinkage, hardtail, and post-E101 stress.

## Update After E137

E137 applies the first movement stress to the E136 branch. It uses the visible block-target state only as a gate on donor-free E95 combo gradients.

- block-target gradient variants: `1980`.
- evaluated variants: `698`.
- local strict variants: `0`.
- transfer-veto-actionable variants: `0`.
- local-strict plus transfer-veto-actionable variants: `0`.
- submit-gate variants: `0`.
- best local delta vs E95: `-0.000043592`.
- best post-E101 mean vs E95: `-0.000040388`, but p95 is still positive at about `0.000026`.

The validation meaning is narrow but important: E136's representation visibility is real enough to concentrate mean improvements, but the existing E95 gradient still points into structurally unsafe/tail-adverse movement. Future validation should keep block-target state as context, but require a new direction/amplitude translator before any file is considered.

## Update After E138

E138 tests the last cheap rescue of the E136/E137 branch: force the visible block-target state to overlap with transfer-safe veto-null / low-adverse masks before applying the E95 gradient.

- overlap variants: `1314`.
- evaluated variants: `698`.
- local strict variants: `0`.
- transfer-veto-actionable variants: `373`.
- local-strict plus transfer-veto-actionable variants: `0`.
- submit-gate variants: `0`.
- best local all delta vs E95: `-0.000030467`.
- best post-E101 mean/p95 vs E95: `-0.000055772` / `-0.000015691`.

This is an asymmetric result. The overlap can satisfy the transfer/post-E101 side, but no evaluated row satisfies strict structural health. The best rows still have at most `2/3` combo-set wins and `1/3` tail-neutral sets, with world/raw-style support universally adverse in the evaluated rows. Therefore the validation gate blocks "block-target state plus veto-null overlap" as a submission path. The next validator should not ask for another mask intersection; it should ask whether a new decoder can preserve all-set tail neutrality and world/raw hidden structure while using the block-target state.

## Update After E139

E139 tests whether E138's decoder failure is only combo-set sign conflict. It is not.

- set-consensus variants: `1188`.
- evaluated variants: `698`.
- local strict variants: `0`.
- transfer-veto-actionable variants: `190`.
- local-strict plus transfer-veto-actionable variants: `0`.
- submit-gate variants: `0`.
- best local all delta vs E95: `-0.000022029`.
- best post-E101 sensor mean/p95 vs E95: `-0.000041506` / `-0.000010520`.

The useful stress detail is the gate pattern: `all_margin_vs_mixmin` and `all_beats_base` pass for every evaluated row, and some all-three consensus rows make all `3/3` combo-set means beat base. But `structural_all_sets_tail_neutral`, `structural_world_nonworse`, and `structural_raw_energy_nonworse` fail for every evaluated row. This blocks combo-set consensus as a submission path. The next validation target should treat tail-neutral/world/raw support as primary decoder constraints, not as screens after a BCE-style mean-gradient move.

## Update After E140

E140 turns tail/world/raw health into the primitive objective rather than a post-hoc screen.

- support cells: `471`.
- micro rows: `942`.
- local-reward primitives: `373`.
- tail/world/local primitives: `119`.
- tolerance-level strict primitives: `3`.
- combined variants: `168`.
- local strict variants: `0`.
- transfer-veto-actionable variants: `0`.
- submit-gate variants: `0`.
- best combined all-minus-E95: `-0.000017556`.
- best post-E101 mean vs E95: `-0.000007182`.

The stress result is asymmetric in the opposite direction from E139. In E140, all combined variants pass hidden-core, world-nonworse, and raw-energy-nonworse, so world/raw is no longer the immediate blocker under primitive decoding. The blocker is exact all-set tail neutrality: every combined row fails it and the best tail-neutral count remains `1/3`. The next validation target should isolate which combo-set worst-tail axis cannot be neutralized and whether a tail-balancing decoder can trade a little mean reward for all-set tail survival.

## Update After E141

E141 corrects the E140 tail reading. The exact tail gate was too brittle.

- tail pass at exact `0`: `0`.
- tail pass at tolerance `1e-12`: `129`.
- relaxed structural pass at tolerance `1e-12`: `84`.
- relaxed structural pass at tolerance `1e-6`: `91`.
- relaxed plus E72 exposure pass: `0`.
- relaxed plus post-E101 p95 pass: `0`.
- relaxed actionable: `0`.
- E95 E72-plausible exposure threshold: `0.001557335020`.
- minimum relaxed E72 exposure: `0.001560524555`, gap `+0.000003189534`.
- best relaxed post-E101 p95: `+0.000000141478`.

The validation meaning changes. E140 did not prove that combo-set worst-tail is the main remaining law; it proved that exact-zero tail accounting was over-conservative. Once numerical zero is tolerated, structural rows open, but transfer-tail budget remains closed. The next stress target should be E72-plausible exposure and post-E101 p95 reduction, not another tail-axis balancing sweep.

## Update After E142

E142 tests that exact stress target by clipping only high excess E72-plausible cells from E140 relaxed structural moves.

- parent relaxed structural material rows: `11`.
- clipped variants: `1844`.
- relaxed structural variants: `670`.
- relaxed plus E72-budget variants: `35`.
- relaxed plus budget plus post-E101 variants: `35`.
- submit-relaxed variants: `35`.
- materialized candidate: `analysis_outputs/submission_e142_transferclip_09a92236.csv`.
- selected local all-minus-E95: `-0.000010666782`.
- selected E72-plausible gap versus E95: `~0`.
- selected post-E101 mean/p95/beat versus E95: `-0.000014379591` / `-0.000003762343` / `1.0`.
- selected movement versus E95: `185` cells, `108` rows, no Q2 movement.

This is the first post-E101 candidate that passes relaxed structural health, E72-budget health, and post-E101 p95 health together. It should be treated as a public sensor on whether E101-conditioned transfer-tail gates generalize, not as proof of a larger 0.54 path.

## Update After E143

E143 tests whether E142's remaining active/Q2S3 veto failure is a real blocker or a repairable risk.

- repair variants: `80`.
- relaxed-submit repair variants: `80`.
- original-strict-submit repair variants: `15`.
- materialized candidate: `analysis_outputs/submission_e143_activeq2s3repair_68ca656f.csv`.
- selected mask: `top_q2s3_weighted_21`, keep factor `0.0`.
- selected rollback cells: `21`.
- selected changed cells versus E95: `164`.
- selected local all-minus-E95: `-0.000009551358`.
- selected E72-plausible gap versus E95: `~0`.
- selected post-E101 mean/p95/beat versus E95: `-0.000013131201` / `-0.000003368915` / `1.0`.
- active/Q2S3, original strict actionability, relaxed structural, E72-budget, and post-E101 gates all pass.

This changes the next public choice. E142 opened the transfer-budget-neutral residual branch, but E143 is the cleaner stress survivor: it keeps most of E142's residual movement while explicitly applying the E101 small-loss lesson as an active/Q2S3 pruning constraint. The current validation ranking is therefore E143 first, E142 second as the higher-upside/higher-risk fallback.

## Update After E144

E144 tests whether E143's repair boundary was only a coarse-grid artifact.

- repair variants: `206`.
- original-strict repair variants: `32`.
- E144-submit variants: `9`.
- materialized candidate: `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`.
- selected mask: `top_q2s3_weighted_24`, keep factor `0.15`.
- selected rollback cells: `24`.
- selected changed cells versus E95: `185`.
- selected local all-minus-E95: `-0.000009725930`.
- selected E72-plausible gap versus E95: `~0`.
- selected post-E101 mean/p95/beat versus E95: `-0.000013326583` / `-0.000003430489` / `1.0`.
- active/Q2S3, original strict actionability, relaxed structural, E72-budget, and post-E101 gates all pass.

This supersedes E143 as the next public file. The validation edge is very small, but it is directionally clean: E144 beats E143 locally and on post-E101 p95 while preserving the same strict gates. The current validation ranking is E144 first, E143 conservative fallback, E142 higher-upside/higher-risk fallback.

## Update After E145

E145 registers the public-feedback stress for E144 before the score is known.

- decoder rows: `7`.
- breakthrough win: `<=0.576271330`.
- clean win: `(0.576271330, 0.576284330]`.
- micro win: `(0.576284330, 0.576289330]`.
- tie: `(0.576289330, 0.576293330]`.
- fine-loss branch alive: `(0.576293330, 0.576300366]`.
- branch loss: `(0.576300366, 0.576306641]`.
- hard fail: `>0.576306641`.

This is not a model stress; it is an interpretation stress. The key validation rule is that a loss no worse than E101 may justify E143 as a clean boundary contrast, while worse-than-E101 blocks automatic same-family rescue. Worse than mixmin closes the E142/E143/E144 branch as public-sensor overfit.

## Update After E146

E146 stress-tests the E144-over-E143 edge without using public feedback.

- differing E144-vs-E143 cells: `24`.
- targets: all `24` are `S3`.
- rows/subjects touched: `24` / `4`.
- movement direction: `21` cells move away from E95 versus E143, `3` move toward E95.
- edge-like cells: `7`.
- flank-conflict cells: `0`.
- public-free priors preferring E144: `10/10`.
- best expected prior delta E144-minus-E143: `nearest_hard085` at `-0.000010294767`.
- weakest expected prior delta: `subject` at `-0.000001097289`.
- simulated `p(E144 beats E143)`: `0.540545` under subject prior to `0.925720` under nearest-hard prior.

This does not create a new submission, but it changes the fallback logic. E144's retained `S3` fine tail is not merely local-gate arithmetic; visible global/subject/flank priors all lean E144 over E143. Therefore a future narrow E144 public loss should be interpreted as hidden public S3-tail adversity, not as public-free evidence that E143 was the better expectation candidate. E143 remains a clean contrast only for the specific question "did keep0.15 retention fail?", not as an automatic rescue.

## Update After E147

E147 expands the prior stress from the E144/E143 fine-tail edge to the whole E144-vs-E95 movement.

- E144-vs-E95 moved cells: `185`.
- touched rows/subjects: `108` / `9`.
- target mix: Q3 `56`, S3 `47`, Q1 `38`, S2 `23`, S4 `21`, Q2/S1 `0`.
- component mix: inherited E143 body `161`, E144 fine-tail delta `24`.
- edge-like cells: `62`.
- flank-conflict cells: `26`.
- public-free priors preferring E144 over E95: `10/10`.
- expected E144-minus-E95 delta range: `-0.000049865515` to `-0.000012197928`.
- simulated `p(E144 beats E95)`: `0.583850` to `0.762700`.
- nearest-hard target stress: Q1/S4/S2 favorable, Q3/S3 adverse.
- nearest-hard component stress: inherited body favorable, fine-tail delta mildly adverse.

This strengthens E144 as the next public sensor because visible priors support the whole file, not only the E144-over-E143 edge. It also narrows the failure mode. If E144 underperforms, the first stress read should be target/component decomposition, especially S3 and Q3, rather than broad rollback to E143 or E142. The expected improvement remains frontier-scale small, so E144 is still a calibrated sensor, not a 0.54-path breakthrough.

## Update After E148

E148 pre-registers how to attribute each possible E144 public outcome before feedback is known.

- simulations per prior: `250000`.
- simulated cells: the `185` E144-vs-E95 moved cells from E147.
- global prior: win-rate mass `0.745560`, non-win mass `0.254440`, branch-or-worse `0.204972`.
- subject prior: win-rate mass `0.599760`, non-win mass `0.400240`, branch-or-worse `0.333832`.
- nearest-hard prior: win-rate mass `0.635616`, non-win mass `0.364384`, branch-or-worse `0.284852`.
- fine-loss-alive is only `0.027696..0.033340` across global/subject/nearest-hard priors.
- nearest-hard clean/micro wins are credited mostly to Q1/S4; nearest-hard fine-loss/branch/hard-fail blame is mostly S3/Q3.
- global fine-loss/branch/hard-fail blame is more inherited-body/Q3/S2, while subject prior points to inherited-body/Q3/S3.

This tightens the post-E144 rule. A fine loss is not automatically an E144-only fine-tail failure. It may instead mean the inherited E143 body or Q3/S2/S3 target slices failed. Therefore E143 should not be submitted mechanically after a fine-loss band; it is justified only if the E148 attribution read is consistent with fine-tail/S3 retention being the actual public problem.

## Update After E149

E149 stress-tests E144's geometry against known public anchor directions before feedback.

- E144 changed cells versus E95: `185`.
- cosine with E101 public-negative axis: `-0.019625796`.
- cosine with E72 public-negative axis: `-0.024358970`.
- cosine with E142 branch axis: `0.952146833`.
- cosine with E143 branch axis: `0.991918719`.
- residual ratio versus E142 axis: `0.305640978`.
- residual ratio versus E143 axis: `0.126874959`.
- E144 Q2/S3 L1 share: `0.161603888`, far below E101's `1.000000000`.
- E144 target L1 is Q3/Q1/S3/S2/S4, with Q2/S1 at zero.

This makes the validation read less euphoric and more precise. E144 survives the E72/E101 known-negative direction check, but it is not an independent new latent. It is almost the same branch as E143, with a smaller residual correction. Therefore E144 remains the next public file, but the public result should be interpreted as a test of the E142/E143 residual branch plus fine active-boundary pruning, not as evidence for or against a broad new representation family.

## Update After E150

E150 turns the E145/E148/E149 interpretation stack into an executable post-feedback stress.

- interpreter rows: `7`.
- input bands: E145 public LB ranges.
- attribution source: E148 target/component responsibility across global, subject, and nearest-hard priors.
- geometry source: E149 branch/negative-axis audit.
- fine-loss branch status: `conditional_alive`, not automatic E143.
- branch-loss status: `weak_rejected`; E143/E142 automatic rescue blocked.
- hard-fail status: `rejected`; close E142/E143/E144 local boundary repair.

The important validation change is that E143 is no longer justified by E144 fine-loss alone. It is allowed only if the attribution read points to fine-tail/S3 retention. Otherwise, fine loss can be inherited-body/Q3/S2 or broad branch stress, and same-family fallback would be post-hoc overfit. The command to apply after public feedback is `python3 analysis_outputs/e150_e144_postfeedback_interpreter.py --score <PUBLIC_LB>`.

## Update After E151

E151 audits the plateau itself rather than a new candidate.

- E95 edge over mixmin: `0.0000153107`.
- best E98 known-LB selector p90 error: `0.0008164966`, or `53.33x` the E95 edge.
- E101 actual-minus-local-mean optimism: `0.0000252415`, or `1.65x` the E95 edge.
- E144 local edge vs E95: `-0.0000097259`.
- E144-over-E143 local tiebreak: `-0.0000001746`.
- old-universe strict novel actionable count from E129: `0`.
- E130/E131/E132/E137/E138/E139 decoder families: all `submit_gate=0`.
- live branch counts: E142 relaxed `35`, E143 strict `15`, E144 submit `9`.

The validation implication is strong: the plateau is not mostly an old-candidate ranking failure. Existing validators cannot resolve the frontier edge, and the representation/decoder probes find either local reward or public-tail safety without submit-safe overlap. The only current overlap is the E142/E143/E144 branch, which is nearly E143-collinear. The next validation object must prove sub-`5e-6` ordering on E95/E101/E144 or produce a non-collinear decoder passing strict/E72/post101 p95 gates.

## Update After E152

E152 tests E151's non-collinear escape hatch directly.

- source rows: `4650`.
- candidate-interest source rows: `3953`.
- source rows non-collinear to E144: `4650`.
- projected rows: `2880`.
- relaxed structural rows: `349`.
- E72-budget rows: `1208`.
- post-E101 rows: `564`.
- active-veto actionable rows: `122`.
- strict/E72/post101/actionable all-four intersection: `0`.
- best local projected move: `-0.0000455468`.
- best `relaxed_budget_post101` row: `-0.0000128032`, but actionability is false.
- only `budget_post101_actionable` row: `-0.0000106142`, but relaxed structural is false.

The validation implication is narrower and harsher than E151. Non-collinear signal is present, so the latent has not collapsed into the E142/E143/E144 branch. But the current decoder cannot make the necessary gates coincide. The next validation object should explain the gate-intersection failure itself, not repeat orthogonal projection/top-k/alpha scans.

## Update After E153

E153 explains the E152 gate-intersection failure instead of creating another candidate.

- projected rows: `2880`.
- three-of-four near misses: `103`.
- all-four intersection: `0`.
- `missing_actionable`: `102`; `missing_relaxed`: `1`.
- missing-actionable active/Q2S3 blocker: `101/102`.
- missing-actionable action-cos blocker: `50/102`.
- missing-actionable E72/material blockers: `0/102`.
- missing-actionable relaxed blockers: `0/102`.
- missing-relaxed raw/world blockers: `1/1`.
- missing-actionable target lift versus rest: S3 `+0.022774`, S4 `+0.020949`, S2 `+0.018800`; Q2 is effectively absent.

The validation implication is now target-specific. The near misses are not failing because the transfer-budget or post-E101 p95 gates are too strict. Almost all of them pass those gates and die on S3 active-boundary actionability. The only actionability-safe escape dies on raw/world relaxed health. A new local decoder must therefore make S3 active-boundary safety and raw/world health co-occur; relaxing one global scalar gate is not a valid stress fix.

## Update After E154

E154 tests whether the E153 S3 actionability blocker is repairable rather than terminal.

- source missing-actionable controls: `102`.
- S3 repair rows: `7458`.
- all-four repairs: `10`.
- materialized rows: `10`.
- selected file: `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.
- selected repair: `top_s3_e101_3`, keep `0.25`, `3` S3 rollback cells.
- selected all-minus-E95: `-0.000012158050`.
- E154 changed cells versus E95: `294`.
- overlap with E144 cells: `185/185`.
- cosine with E144/E143/E142: `0.983569299` / `0.975091856` / `0.939950819`.
- cosine with E72/E101 public-negative axes: `-0.031628728` / `-0.005523655`.

The validation implication changes the live branch. The E152 all-four failure was not an irreversible gate incompatibility: a very small S3 E101-active rollback can open it. But the successful row remains E144-branch geometry, so this is not a broad escape from the plateau. E154 is now the sharpest public sensor for the current hypothesis; E144 becomes the conservative contrast for the unrepaired branch.

## Update After E155

E155 tests whether E154's added E144->E154 branch body is an exact tuned point.

- rows: `44`.
- variant rows: `40`.
- all-four variants: `34`.
- E155-submit variants: `27`.
- reduced-body submit variants: `22`.
- materialized lower-body file: `analysis_outputs/submission_e155_bodytemp_d27e7965.csv`.
- selected row: `branch_body_alpha`, alpha `0.25`.
- selected all-minus-E95: `-0.000010362491`.
- selected body-norm ratio: `0.25`.
- post-E101 p95: about `-0.00000377`.
- E72 plausible gap: about `-0.00000108`.
- target-drop all-four rate: `12/12`.

The validation implication is better than expected. E154 is not a single brittle all-four point; a 25% body interpolation from E144 to E154 still clears the health gates and beats E144 locally. That strengthens the repaired-branch worldview, but it also lowers the urgency to trust full E154 amplitude. Use E154 as the highest-information public sensor and E155 as the conservative amplitude-control contrast.

## Update After E156

E156 tests whether the E155 diagonal is the minimum coherent repaired body or whether target-axis pieces can carry the gate health with even less movement.

- active lattice axes: `Q1,Q3,S2,S3,S4`.
- lattice variants: `3125`.
- full non-anchor evaluated rows: all lattice rows.
- all-four lattice rows: `3125`.
- strict candidates: `2984`.
- minbody rows below E155 body ratio `0.25`: `85`.
- materialized low-body file: `analysis_outputs/submission_e156_targetaxis_757546d2.csv`.
- selected axes: `Q1+S2+S4`.
- selected alphas: `Q1=0.25`, `S2=0.75`, `S4=0.25`.
- selected body-norm ratio: `0.171266667`.
- selected all-minus-E95: `-0.000010004`.
- selected post-E101 p95: `-0.000003712`.
- selected E72 plausible gap: `-0.000002266`.
- cosine vs E144/E155/E154: `0.999515751` / `0.998991027` / `0.985122955`.
- cosine vs E101/E72: `-0.019678524` / `-0.027413915`.

The validation implication is narrow but important. The repaired branch is even less brittle than E155 implied: full target-axis diagonal movement is not required. However, the minimum-body survivor is almost pure E144 geometry plus a tiny Q1/S2/S4 add-on, and its local edge is weaker than E155 and E154. E156 is therefore a target-decomposition control, not the first public sensor.

## Update After E157

E157 tests whether E156's minimum-body target-axis choice is itself meaningful.

- lattice variants audited: `3125`.
- all-four variants: `3125`.
- strict candidates: `2984`.
- all-minus-E95 span across lattice: `0.000002432120`.
- strongest local finite-difference axis: Q3, mean all-minus delta `-0.000000383335`.
- strongest post-E101 p95 finite-difference axis: Q3, mean delta `-0.000000132956`.
- E72 budget finite-difference axis: S2, mean gap delta `-0.000000714955`; other axes are near zero.
- E155-dominating low-body rows: `3`.
- materialized tuned low-body file: `analysis_outputs/submission_e157_lowbodypareto_bd67930d.csv`.
- selected axes: `Q1+Q3+S2+S4`.
- selected body ratio: `0.240336139` vs E155 `0.25`.
- selected all-minus-E95: `-0.000010404446` vs E155 `-0.000010362491`.
- selected post-E101 p95: `-0.000003807382`.
- selected E72 gap: `-0.000001671496`.

The validation implication is a warning. E156's Q1/S2/S4 minimum-body row does not mean Q3 is a bad axis; Q3 is the strongest local and post-E101 finite-difference axis. The branch is gate-saturated and smoothly favorable across many axes, so target-axis rows are controls. E157 is a tuned Pareto control and should not outrank E154 or the cleaner E155 amplitude-control on interpretation quality.

## Update After E158

E158 turns the repaired branch stack into a public-feedback decoder rather than another candidate generator.

- script: `analysis_outputs/e158_repaired_branch_public_decoder.py`.
- candidate table: `analysis_outputs/e158_repaired_branch_public_decoder_candidates.csv`.
- pairwise table: `analysis_outputs/e158_repaired_branch_public_decoder_pairwise.csv`.
- band table: `analysis_outputs/e158_repaired_branch_public_decoder_bands.csv`.
- report: `analysis_outputs/e158_repaired_branch_public_decoder_report.md`.
- E154 vs E155 local all-minus gap: `-0.000001795559`, below the `2e-6` public-readable guardrail.
- E154 vs E144 local all-minus gap: `-0.000002432120`, above the guardrail.
- E157 vs E155 local all-minus gap: `-0.000000041955`.
- E156 vs E155 local all-minus gap: `+0.000000358921`.
- E155/E157/E156 cosine vs E144: `0.998962769` / `0.999041566` / `0.999515751`.

The stress implication is that the repaired branch controls are not independent expected-improvement bets. E154 remains the first sensor because it asks the full repaired all-four question and is distinguishable from unrepaired E144, not because its separation from E155 is public-readable. If E154 loses or ties, E155 is the clean amplitude-control; E157/E156 should be treated as target-axis controls only after E155, not as pre-feedback score maximizers.

## Update After E159

E159 adds the attribution stress that E158 deliberately left open.

- script: `analysis_outputs/e159_e154_public_outcome_attribution.py`.
- segment table: `analysis_outputs/e159_e154_public_outcome_attribution_cells.csv`.
- outcome rates: `analysis_outputs/e159_e154_public_outcome_attribution_rates.csv`.
- responsibility tables: `analysis_outputs/e159_e154_public_outcome_group_attribution.csv`, `analysis_outputs/e159_e154_public_outcome_top_responsibility.csv`.
- unique moved cells: `294`; additive segments: `479`.
- decomposition verification: max y=1/y=0 hard-delta error `1.75e-16` / `1.93e-16`.
- component flip-benefit: inherited E144 body `3.292000000`, E154 extra body `0.255975083`, E154 adjustment on E144 body `0.203843941`.
- focus-prior win mass: global `0.728550`, subject `0.601575`, nearest-hard `0.666680`.
- branch-or-worse mass: global `0.222590`, subject `0.336125`, nearest-hard `0.259610`.

The stress implication is that E154's public result must be interpreted by component responsibility, not by score band alone. The loss-side stress is dominated by the inherited E144 body under all focus priors; the E154 added body is much smaller. Therefore E155 is a valid follow-up only when the realized E154 band and attribution specifically point to added-body overextension. If E154 fails because the inherited body is adverse, the lower-amplitude E155 control cannot logically rescue the branch.

## Update After E160

E160 makes the E154 post-feedback rule executable.

- script: `analysis_outputs/e160_e154_postfeedback_interpreter.py`.
- summary: `analysis_outputs/e160_e154_postfeedback_interpreter_summary.csv`.
- report: `analysis_outputs/e160_e154_postfeedback_interpreter_report.md`.
- decision rows: `7`.
- E155 gate by band: `not_needed` for win bands, `information_only` for tie and small_loss, `not_recommended` for branch_loss and hard_fail.
- score probe check: `0.5763003660` maps to `small_loss`; `0.5762880000` maps to `micro_win`.

The stress implication is now operational: after E154 public feedback, run the E160 interpreter before selecting E155/E157/E156/E144. The current pre-feedback attribution makes E155 an information-only amplitude contrast at best unless the realized score lands in a tie/small-loss band and the component read points to E154-added body.

## Update After E161

E161 tests the most obvious E159 follow-up: prune the cells that public-free priors call risky.

- script: `analysis_outputs/e161_e154_inherited_body_pruning_audit.py`.
- pruning variants: `1608`.
- all-four health variants: `631`.
- control-grade variants: `299`.
- submission-grade variants: `0`.
- public-free safer-than-E154 variants: `1226`.
- locally better-than-E154 variants: `180`.
- public-readably better-than-E154 variants under the `2e-6` guardrail: `0`.
- best local delta versus E154: `-0.000000045921`.
- best focus expected-risk delta versus E154: `-0.000104369145`, but those high-risk prunes give up local health/edge.

The stress implication is that attribution-risk pruning is real but not submission-grade before feedback. It can create safer controls inside the branch, especially by reverting a few S4/Q3/S3 cells, but it does not create an independent readable successor. This keeps the live validation object unchanged: E154 must be used as the public sensor, and E161-style pruning can only become useful if E154 feedback specifically says the branch is alive but a small component is overextended.

## Update After E162

E162 translates the repaired-branch resolution problem into hard-label flip units.

- script: `analysis_outputs/e162_branch_readability_flip_thresholds.py`.
- pairwise rows: `13`.
- E154 vs E155 top1 swing: `0.000010815`.
- E154 vs E144 top1 swing: `0.000014420`.
- E157 vs E155 top1 swing: `0.000002185`.
- E154 vs E95 top1 swing: `0.000015340`, about the whole E95-over-mixmin edge.
- cells needed to reach the `2e-6` public-readable guardrail: `1` for every live sibling/control pair.
- E154 vs E155 focus expected delta: `+0.000000505`; E154 vs E144 focus expected delta: `+0.000000638`.

The stress implication is stronger than "these files are close." The sibling order is cell-fragile: one high-swing hidden row-target label can move public LogLoss more than the intended local gap. Therefore local CV or public-free priors cannot rank E154/E155/E157/E156/E161 pruning rows as expected-score candidates before public feedback. The only defensible use is as predeclared instruments after E154 reveals which hidden-label world is active.

## Update After E163

E163 tests whether E162 was local to the repaired sibling stack or a broader post-E95 plateau property.

- script: `analysis_outputs/e163_candidate_edge_breadth_audit.py`.
- report: `analysis_outputs/e163_candidate_edge_breadth_report.md`.
- audited pairs: `22`.
- known public transitions: `7`.
- known transitions whose actual public delta can be moved by one top hard-label cell: `3/7`.
- known transitions whose actual public delta can be moved by five top hard-label cells: `5/7`.
- live post-E95 candidates with one-cell `2e-6` readability fragility: `7/7`.
- mixmin vs a2c8: actual delta `-0.0011326805`, top1 swing `0.000046919`, cells for actual delta `25`.
- E95 vs mixmin: actual delta `-0.0000153107`, top1 swing `0.000046477`, cells for actual delta `1`.
- E101 vs E95: actual delta `+0.0000090362`, top1 swing `0.000011619`, cells for actual delta `1`.
- E72 vs mixmin/E95: cells for actual delta `4`/`6`, despite the local focus-prior direction being wrong.

The stress implication is now split cleanly. Mixmin was a broad public-relevant move, not a one-cell artifact. The plateau after E95 is different: refinements are real enough to move public LB, but their deltas sit inside a few high-leverage hard-label cells. This is why E101 could be locally coherent and still lose to E95, and why E154/E155/E157/E156 cannot be pre-feedback ranked by micro-edges. E154 remains the next public sensor because it asks the most informative repaired-branch question, not because E163 certifies it as the highest expected-score file.

## Update After E164-E166

E164-E166 reopen the broad-signal lane that E163 demanded.

- E164 script: `analysis_outputs/e164_universe_broad_edge_screen.py`.
- E165 script: `analysis_outputs/e165_broad_edge_bad_axis_geometry.py`.
- E166 script: `analysis_outputs/e166_broad_survivor_scale_probe.py`.
- E164 unique tensors scanned: `1977`; broad-edge rows: `198`; candidate-gate rows: `192`.
- E164 caveat: known public-bad rows can pass broadness, including E72 and LeJEPA controls.
- E165 bad axes: `a2c8,raw05,stage2,ordinal,final9,e72,q2_bad,lejepa_bad,resid_bad`.
- E165 geometry-health survivors: `90`; known public-bad broad controls rejected by geometry health.
- E166 scaled rows: `198`; scaled sensor-gate rows: `112`; material rows at scale `<=0.03`: `51`; negative-control sensor gates: `0`.
- E166 materialized file: `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv`.
- E166 selected scale/source: `0.01` toward `submission_block_canvas_multifeature_k8_c0p02_all_scale1p0.csv`.
- E166 selected focus expected delta vs E95: `-0.000332077`.
- E166 selected hard-label breadth: cells-to-flip expected `74`, top1/expected `0.023369627`.
- E166 selected geometry: bad-span energy `0.450742441`, max bad-axis `q2_bad`, cosine `0.268538582`.
- E166 selected amplitude: mean/max abs logit move `0.002243986` / `0.013580886`.

The validation implication changes the next-decision menu. E154 is still the cleaner repaired-branch sensor, but it is narrow. E166 is the first post-E95 candidate that directly addresses the E163 requirement: it is broad, small-amplitude, non-collinear with E154, and rejects scaled known-bad controls. It is therefore a legitimate broad-escape sensor, not a CV/blend tweak. Its risk is that the broad survivor family has no public-positive anchor yet; a loss would specifically falsify the current bad-axis geometry as incomplete.

## Update After E167

E167 stress-tests whether E166's broad cells are hidden-context-real and safety-atlas-compatible.

- script: `analysis_outputs/e167_broad_survivor_context_alignment.py`.
- E166 focus cells: `74`.
- permutation nulls per focus set: `3000`.
- top-benefit expected delta: `-0.000115303`.
- top-benefit context enrichment: edge-like rate `0.689189` vs null `0.470842`; between-train-runs rate `0.797297` vs `0.624658`; top-subject share `0.243243` vs `0.164563`.
- top-benefit safety divergence: all-veto-null rate `0.297297` vs null `0.574158`; all-safe-density mean `0.117097` vs `0.243966`; broad-low-alpha mass `1.321365` vs `3.199735`; E101-plausible mass `0.238204` vs `0.533727`.
- E72-active rate: `0.837838` vs null `0.670369`.

The stress implication is mixed and useful. E166 survives the "random broad noise" stress: its focus cells are genuinely concentrated in hidden calendar/block contexts. It fails the "safety-atlas certified" stress: the same focus cells are unusually low on veto-null/safe-density/low-alpha/E101-plausible support and unusually high on E72-active support. So E166 remains a high-information broad-escape public sensor, but it is not a safer expected-score candidate and should not be scaled before feedback.

## Update After E168-E169

E168-E169 test whether E167's context-real/safety-divergent split can be repaired before public feedback.

- E168 script: `analysis_outputs/e168_e166_safety_context_decoupling.py`.
- E169 script: `analysis_outputs/e169_e166_context_safety_mask_materializer.py`.
- E168 decoupling-pass policies: `2`.
- `context_high__veto`: expected delta `-0.000120457`, moved cells `904`, cells-to-flip `32`, top1/expected `0.048415`, edge-like `0.610619`, between-train-runs `0.819690`, veto `1.0`, safe-density `0.346150`, E72-active `0.268805`.
- `context_high__high_density_p50`: expected delta `-0.000119080`, moved cells `894`, cells-to-flip `32`, top1/expected `0.048975`, edge-like `0.610738`, between-train-runs `0.817673`, veto `1.0`, safe-density `0.349218`, E72-active `0.260626`.
- E169 stress-gate policies: `2/11`.
- materialized files: `analysis_outputs/submission_e169_ctx_veto_c5e806e3.csv`, `analysis_outputs/submission_e169_ctx_high_density_p50_51110c7e.csv`.
- `submission_e169_ctx_veto_c5e806e3.csv`: moved cells/rows `904/193`, bad-span energy `0.295326`, max bad axis `q2_bad`, max bad cosine `0.222381`, mean/max abs logit `0.001096`/`0.010206`, Q2/S3 share `0.347775`.
- raw E166 comparator: expected delta `-0.000332077`, moved cells `1750`, cells-to-flip `74`, bad-span energy `0.450742`, mean abs logit `0.002244`.

The stress implication is that E166's broad hidden-context signal is repairable in local geometry. The repaired version gives up expected edge but lowers amplitude, bad-axis energy, and safety-atlas conflict. This makes `submission_e169_ctx_veto_c5e806e3.csv` the balanced broad-branch public sensor. Raw E166 remains the sharper safety-atlas falsification test, and E154 remains the conservative repaired-branch contrast.

## Update After E170

E170 pre-registers how to interpret `submission_e169_ctx_veto_c5e806e3.csv` before any public feedback arrives.

- script: `analysis_outputs/e170_e169_public_feedback_decoder.py`.
- report: `analysis_outputs/e170_e169_public_feedback_decoder_report.md`.
- E169-vs-E95 hard-label readability: moved cells/rows `904/193`, expected delta `-0.000120457`, cells-to-flip expected `32`, top1 swing `0.000005832`, top5 swing `0.000023823`, cells for `2e-6` guard `1`, cells for E95-over-mixmin edge `4`.
- raw E166-vs-E95 comparator: expected delta `-0.000332077`, cells-to-flip `74`, cells for E95 edge `3`.
- E169-vs-raw E166: expected delta `+0.000211620`, so ctx-veto deliberately gives up a large prior-favorable raw-E166 region in exchange for safer context/veto geometry.
- E169 group attribution: between-train-runs carries `81.1%` of expected edge, not-E72-active carries `73.7%`; target shares are S1 `19.8%`, S3 `19.1%`, Q2 `15.6%`, S4 `15.6%`, Q1 `11.9%`, S2 `11.6%`, Q3 `6.4%`.
- near-duplicate control: `submission_e169_ctx_high_density_p50_51110c7e.csv` differs from ctx-veto by only `10` Q2/S3 cells and `-0.000001377` expected delta.

Stress implication: E169 is a valid balanced broad-branch sensor, but it has not escaped public hard-label-resolution limits. A win below E95 promotes context-high/veto broad latent. Tie/small loss keeps E95 practical and makes raw E166 information-only. Worse than E101 demotes the E169 repair; worse than mixmin closes same-family E169 threshold variants.

## Update After E171

E171 stress-tests the exact E170 weak point: the critical high-swing cells.

- script: `analysis_outputs/e171_e169_critical_cell_prior_audit.py`.
- full moved body under `visible_mean`: mean delta `-0.000022659`, win rate `0.868840`, E95-edge-or-better rate `0.638120`.
- subject prior: mean delta `-0.000021115`, win `0.853520`.
- focus_mean: mean delta `-0.000053678`, win `0.994460`.
- flank-only priors are weak/adverse: `nearest_beta` mean `+0.000005364`, win `0.388080`; `edge_endpoint_beta` mean `+0.000005106`, win `0.389420`; `flank_mean` mean `+0.000000790`, win `0.480740`.
- top critical support under visible_mean: top1 `0.098648`, top4 `0.330699`, top16 `0.266074`, top32 `0.247434`.
- target-matched null: top32 support `0.247434` vs null mean `0.353573`, `z=-2.703`, `p_low=0.001667`.

Stress implication: E169's full body is not random and remains favorable under broad visible priors, but the exact cells that can decide public LB are visible-prior adverse. This keeps E169 as the best broad public sensor, while weakening any claim that it is a stable expected-score improvement. A narrow E169 loss should be interpreted through critical-cell tail adversity before closing the whole broad branch.

## Update After E172

E172 tests whether the E171 critical-tail warning can be turned into a healthier tensor.

- script: `analysis_outputs/e172_e169_critical_tail_rollback_probe.py`.
- report: `analysis_outputs/e172_e169_critical_tail_rollback_probe_report.md`.
- variants scored: `67`.
- stress-gate variants: `7`.
- materialized file: `analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv`.
- selected rollback: `visible_positive_all_keep0p25`.
- rollback cells: `410`, with `25%` of their E169-vs-E95 logit movement retained.
- focus expected delta vs E95: `-0.000112695`.
- breadth: moved cells/rows `904/193`, cells-to-flip expected `30`, top1/expected `0.051750`.
- visible-prior tail: mean delta `-0.000052853`, p95 `-0.000026683`, worse-than-E101 probability `0.000050`.
- geometry: bad-span energy `0.257874`, max bad-axis `q2_bad`, max bad cosine `0.142927`, Q2/S3 share `0.315866`.
- E169 comparator: expected delta `-0.000120457`, visible p95 `+0.000010607`, visible worse-than-E101 `0.058545`, bad-span energy `0.295326`, max bad cosine `0.222381`.

Stress implication: E171's critical-tail warning is not just a post-hoc objection. A broad-body-preserving rollback exists and improves the exact visible-tail risk metrics that made E169 unstable. E172 is therefore the stronger expected-score broad candidate, while E169 remains the cleaner unrolled body-vs-tail sensor.

## Update After E173

E173 pre-registers how to read E172 public feedback.

- script: `analysis_outputs/e173_e172_public_feedback_decoder.py`.
- report: `analysis_outputs/e173_e172_public_feedback_decoder_report.md`.
- E172-vs-E95: moved cells/rows `904/193`, expected delta `-0.000112695`, cells-to-flip expected `30`.
- E172-vs-E95 hard-label readability: top1 swing `0.000005832`, top5 swing `0.000023823`, cells for `2e-6` guard `1`, cells for E95-over-mixmin edge `4`.
- E172-vs-E169 rollback: `410` cells over `178` rows, expected delta `+0.000007762` under E162 focus priors, cells-to-flip `3`.
- prior-tail repair: visible p95 `+0.000010607 -> -0.000026683`; visible worse-than-E101 `0.058545 -> 0.000050`; flank_mean mean `+0.000000777 -> -0.000035296`.
- attribution: between-train-runs cells carry `80.6%` of E172-vs-E95 expected edge; not-E72-active cells carry `71.6%`.

Stress implication: E172 fixes the visible/flank prior-tail problem, but not the hidden hard-label resolution problem. It is the better expected-score broad candidate than E169, but it still needs public interpretation by bands before any same-family follow-up.

## Update After E174

E174 tests whether E172's keep `0.25` rollback is overconservative.

- script: `analysis_outputs/e174_e172_rollback_overcorrection_probe.py`.
- report: `analysis_outputs/e174_e172_rollback_overcorrection_probe_report.md`.
- variants scored: `80`.
- E174-gate variants: `46`.
- materialized file: `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv`.
- selected policy: `reopen_focus_cost_top75_to1p0`.
- expected focus delta vs E95: `-0.000124367`, versus E172 `-0.000112695`.
- focus recovery vs E172: `-0.000011672`.
- breadth: moved cells/rows `904/193`, cells-to-flip expected `33`, top1/expected `0.046893`.
- visible-tail: mean `-0.000050633`, p95 `-0.000022709`, worse-than-E101 `0.000220`.
- geometry: bad-span energy `0.263996`, max bad-axis `q2_bad`, max bad cosine `0.163229`, Q2/S3 share `0.339597`.
- direct recovery vs E172 by target: S3 `-0.000003234`, Q2 `-0.000002953`, S2 `-0.000002682`, S1 `-0.000001471`, Q1/Q3/S4 smaller.

Stress implication: E172's visible-tail rollback is not uniquely optimal. A partial reopening can recover a public-readable amount of focus-prior edge while preserving E172's visible-tail guard. The remaining risk is not visible-tail collapse; it is that E174 sits close to the Q2/S3 guard and spends more bad-axis margin than E172. Treat E174 as the sharper expected-score candidate and E172 as the safer contrast.

## Update After E175

E175 pre-registers how to interpret E174 public feedback before seeing it.

- script: `analysis_outputs/e175_e174_public_feedback_decoder.py`.
- report: `analysis_outputs/e175_e174_public_feedback_decoder_report.md`.
- E174-vs-E95 readability: moved cells/rows `904/193`, expected focus delta `-0.000124367`, cells-to-flip expected `33`, top1 swing `0.000005832`, cells for E95-over-mixmin edge `4`.
- E174-vs-E172 readability: changed cells/rows `75/65`, expected focus recovery `-0.000011672`, cells-to-flip `5`, top1 swing `0.000002996`, cells for E95-over-mixmin edge `7`.
- prior-tail tradeoff versus E172: focus mean improves by `-0.000001861`; visible mean worsens by `+0.000002220`, visible p95 by `+0.000003974`, and worse-than-E101 probability by `+0.000169869`.
- responsibility map: direct E174-vs-E172 recovery is mainly S3 `27.7%`, Q2 `25.3%`, S2 `23.0%`, and S1 `12.6%`; not-E72-active cells carry `88.6%`.
- score bands: `<=0.576276019` validates E174 as a broad anchor, `0.576276019..0.576288330` is micro-win/underresolved, `0.576288330..0.576300366` keeps E95 practical and points to E172 as contrast, `>0.576300366` demotes E174, and `>0.576306641` closes same-family reopening as expected-score follow-up.

Stress implication: E175 does not make E174 safer; it makes the interpretation falsifiable. The main stress risk is still thin public hard-label resolution around a small number of S3/Q2/S2 cells. The next public score should be treated as a banded observation, not as permission to retune reopening counts.

## Update After E176

E176 tests whether E174 is component-Pareto before public feedback.

- script: `analysis_outputs/e176_e174_component_ablation_probe.py`.
- report: `analysis_outputs/e176_e174_component_ablation_probe_report.md`.
- variants scored: `162`.
- E176 gate variants: `12`.
- materialized file: `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`.
- selected component: damp only the E174 reopened Q2 cells from keep `1.0` to `0.75`.
- edge tradeoff: E174 focus `-0.000124367`; E176 focus `-0.000123384`; E176 gives up `+0.000000983` versus E174 while staying `-0.000010689` better than E172.
- breadth: moved cells/rows `904/193`, cells-to-flip `33`, top1/expected `0.047267`.
- risk improvements versus E174: bad-span energy `0.263996 -> 0.261687`, max bad cosine `0.163229 -> 0.158126`, Q2/S3 share `0.339597 -> 0.334753`, visible p95 `-0.000022709 -> -0.000023096`, worse-than-E101 `0.000220 -> 0.000192`.

Stress implication: E174 was not strictly Pareto. A simple Q2 damping keeps the partial-reopen body while shaving the exact risk axes that made E174 thin. This makes E176 the risk-adjusted broad candidate; E174 remains the max-edge contrast and E172 the safer tail-repair contrast.

## Update After E177

E177 pre-registers how to interpret E176 public feedback before seeing it.

- script: `analysis_outputs/e177_e176_public_feedback_decoder.py`.
- report: `analysis_outputs/e177_e176_public_feedback_decoder_report.md`.
- E176-vs-E95 readability: moved cells/rows `904/193`, expected focus delta `-0.000123384`, cells-to-flip `33`, top1 swing `0.000005832`, cells for `2e-6` guard `1`, cells for E95-over-mixmin edge `4`.
- E176-vs-E174 Q2 damping: `21` Q2 cells over `21` rows, expected focus cost `+0.000000983`, cells-to-flip `2`, top1 swing `0.000000832`.
- E176-vs-E172 recovery: `75` cells over `65` rows, expected focus recovery `-0.000010689`, cells-to-flip `5`; target recovery is S3 `-0.000003234`, S2 `-0.000002682`, Q2 `-0.000001970`, S1 `-0.000001471`, plus smaller Q1/Q3/S4.
- score bands: `<=0.576276019` validates E176 as a broad/Q2-underopen anchor, `0.576276019..0.576288330` is micro-win/underresolved, `0.576288330..0.576300366` keeps E95 practical and limits E172/E174 to contrast sensors, `>0.576300366` demotes E176, and `>0.576306641` closes same-family reopening as expected-score follow-up.

Stress implication: E176 is now a locked public sensor rather than an adjustable Q2 amplitude knob. The Q2 damping contrast is too small to justify post-hoc keep-factor tuning from one score; only a later E174-vs-E176 contrast can revive full Q2 reopening.

## Update After E178

E178 compresses the current E95/E101/E166-E176 evidence into one plateau law.

- script: `analysis_outputs/e178_current_plateau_law_audit.py`.
- report: `analysis_outputs/e178_current_plateau_law_report.md`.
- E101 public remains the resolved negative sensor: `0.5763003660`, or `+0.0000090362` versus E95 and `-0.0000062745` versus mixmin.
- broad signal is real but unsafe by itself: E166 focus-prior edge is `-0.000332077`, `21.689x` the E95-over-mixmin edge.
- repaired broad candidates remain material but cell-fragile: E169 `-0.000120457`, E172 `-0.000112695`, E174 `-0.000124367`, E176 `-0.000123384`; E176 needs only `4` top hard-label cells to swing the whole E95 edge.
- selector/proxy ranking is too coarse: E98 best known-LB selector p90 is `53.33x` the E95 edge and MAE is `33.97x`.
- bottleneck statuses: validation mismatch, public-subset mismatch, and target-prior calibration tail have strong evidence; data signal shortage is mixed; representation capacity is weak evidence; candidate selection is partial.

Stress implication: the plateau is not "no hidden structure" and not "just train a bigger model." The hidden body exists, but current validation cannot rank the final public-tail hard-label cells at frontier scale. E176 remains the next single public sensor; do not generate more same-family Q2 keep-factor siblings before feedback.

## Update After E179

E179 asks whether E176's fragile public-decisive cells are actually visible before public feedback.

- script: `analysis_outputs/e179_e176_critical_cell_visibility_audit.py`.
- report: `analysis_outputs/e179_e176_critical_cell_visibility_report.md`.
- full-body visible-mean expected delta vs E95: `-0.000050824`.
- visible-mean simulated E176 win rate: `0.999080`; focus-mean win rate: `1.000000`.
- top4 E95-edge cells visible swing-weighted support: `0.330699`.
- top33 expected-flip support: `0.245771` vs target-matched null mean `0.335713`, `z=-1.983811`, `p_low=0.014667`.
- E176-vs-E174 Q2 damping visible-mean delta: `-0.000000191`; swing-weighted support `0.690495`; hard support rate `0.904762`.

Stress implication: E176 is body-supported and Q2-damping-supported, but not decisive-cell-certified. That keeps it as the single best next public sensor while preserving the plateau warning: the public result can still hinge on a few hidden labels that train-derived visible priors do not resolve.

## Update After E180

E180 calibrates E179's warning against known public anchors.

- script: `analysis_outputs/e180_known_anchor_decisive_cell_visibility.py`.
- report: `analysis_outputs/e180_known_anchor_decisive_cell_visibility_report.md`.
- E95-vs-mixmin public-positive top4 visible support: `0.100896`.
- E101-vs-mixmin public-positive top4 visible support: `0.100896`.
- mixmin-vs-a2c8 public-positive top4 visible support: `0.310904`.
- E176 pending top4 visible support: `0.330699`, above known-winner mean `0.170898` and known-winner max `0.310904`.
- failed E72 has strong observed-adverse top4 support (`0.793304` vs mixmin, `0.696441` vs E95), but E101-vs-E95 near loss has only `0.100896` observed-adverse top4 support.
- all-moved visible-prior sign accuracy across known anchors: `0.5`.

Stress implication: E179's weak top-cell support is not a hard veto. The more important finding is that visible priors are too weak as a decisive-cell selector at frontier scale. E176 remains the next sensor because it is body-supported and Q2-damping-supported, but it is still not locally certified.

## Update After E181

E181 adds the binary-world counterprior stress.

- script: `analysis_outputs/e181_e176_binary_world_counterprior_audit.py`.
- report: `analysis_outputs/e181_e176_binary_world_counterprior_report.md`.
- inherited binary worlds were reranked by all current known public anchors.
- best current-anchor residual world: sum abs residual `0.000518340`, max abs residual `0.000194476`.
- E176 in best-5 residual worlds: mean delta versus E95 `+0.000003920`, negative rate `0.400`.
- E176 in best-10 residual worlds: mean delta `+0.000007442`, negative rate `0.300`.
- E154 and E144 in best-5 worlds: mean deltas `-0.000051451` and `-0.000051445`, negative rate `1.000` each.
- E176 cell support under best-5 worlds: top4 `0.433633`, top16 `0.221275`; under best-10, top4 `0.262881`.

Stress implication: the live candidate order is now representation-conditional. Visible/body stress keeps E176 alive, but current-anchor binary-world stress points away from E176 and toward E154/E144. Because the binary pool is inherited and residuals are not frontier-precision, E181 is not a submission selector. It is a kill-test for the stronger claim that E176 is supported across all latent views.

## Update After E182

E182 refreshes the binary-world stress using current public anchors and explicit E176/E154/E144 objectives.

- script: `analysis_outputs/e182_current_anchor_binary_world_refresh.py`.
- report: `analysis_outputs/e182_current_anchor_binary_world_refresh_report.md`.
- current anchors include E101 public `0.5763003660` as a resolved small-loss observation against E95.
- scenario max residuals: global target prior `0.0000784319`, weak subject-target prior `0.0000513148`, tight subject-target prior `0.0000762925`.
- strict residual-budget range incumbent rate: `0.233`.
- objective-pressure E176/E154/E144 zero-crossing rates: `1.000` / `1.000` / `1.000`.
- representative pressure spans versus E95: E176 `-0.000421216..+0.000254123`, E154 `-0.00109286..+0.000923535`, E144 `-0.000992245..+0.000838041`.

Stress implication: E181's inherited counterprior is not strong enough to reorder submissions by itself. The refreshed current-anchor problem can make all three live branches look favorable or adverse depending on objective pressure. This strengthens the plateau diagnosis: known public anchors constrain the hidden world, but they do not identify the next frontier-scale candidate sign. The next submission remains a worldview sensor, not a local expected-score certificate.

## Update After E183

E183 asks whether the favorable E182 pressure branches are visible from train-derived priors.

- script: `analysis_outputs/e183_pressure_world_branch_anatomy.py`.
- report: `analysis_outputs/e183_pressure_world_branch_anatomy_report.md`.
- favorable-branch preference under visible-mean priors: E176/E154/E144 = `0.000` / `0.000` / `0.000`.
- favorable-branch preference under subject priors: `0.000` for all three.
- favorable-branch preference under flank-mean priors: `0.000` for all three.
- support-gap coefficient-weighted means: E176 `0.797945`, E154 `0.973558`, E144 `0.888923`.
- average differing moved cells: E176 `601.7`, E154 `282.7`, E144 `164.0`.
- E176 global prior prefers the favorable branch in `1.000` of scenarios, but all local/visible priors prefer the adverse branch.

Stress implication: E183 turns visible priors from candidate selectors into anti-selector diagnostics for the current pressure-world problem. They can still explain bodies and risks, but they cannot choose the favorable hidden branch for E176/E154/E144. Any next submission must be framed as a worldview sensor or backed by a new decisive-cell representation.

## Update After E184

E184 tests the first non-visible pressure-branch selector: a known-public metadata motif learned from public-positive and public-negative transitions.

- script: `analysis_outputs/e184_public_anchor_motif_pressure_selector.py`.
- report: `analysis_outputs/e184_public_anchor_motif_pressure_selector_report.md`.
- best direct pair-LOO model: `meta_public_axis_plus_swing`, sign accuracy `0.333`, AUC `0.425`.
- best direct family-level accuracy/AUC: `0.600` / `0.178`.
- polarity inversion looks tempting but unstable: pair best-polarity accuracy can reach `1.000`, while family best-polarity accuracy stays `0.600`.
- live branch preferences are feature-set unstable: `meta_core=0.000`, `meta_public_axis=1.000`, `meta_public_axis_plus_support_label=1.000`, `meta_public_axis_plus_swing=0.000`.

Stress implication: a shallow public-anchor metadata motif is not a branch selector. It may encode public-response residue, but the polarity is not stable enough to act on, and adding public-axis flags can flip all live branch decisions without passing the held-out stress. E184 keeps the plateau diagnosis at hidden-label/cell-resolution underidentification.

## Update After E185

E185 moves from cell-level public motifs to pair-level known-LB structural decoding.

- script: `analysis_outputs/e185_known_lb_pair_structural_decoder.py`.
- report: `analysis_outputs/e185_known_lb_pair_structural_decoder_report.md`.
- best leave-one-file decoder: `shape_support_public_axis`, accuracy `0.811`, frontier accuracy `0.833`, E95-edge accuracy `0.714`.
- best leave-one-pair E95-edge accuracy: `0.786`.
- reciprocity is unhealthy: best public-axis E95-edge reciprocity MAE is `0.081` under file-LOO and `0.146` under pair-LOO.
- live branch scoring is unstable: `shape_only` favors E144/E154 and rejects E176, while support/public-axis features favor E176.

Stress implication: known-LB pair movement contains real public-response signal, but unconstrained orientation geometry is not healthy enough for action. E185 is a LeJEPA failure: accuracy without reciprocal consistency is a shortcut.

## Update After E186

E186 repairs the E185 geometry by enforcing antisymmetric pair scores.

- script: `analysis_outputs/e186_antisymmetric_pair_decoder.py`.
- report: `analysis_outputs/e186_antisymmetric_pair_decoder_report.md`.
- best file-LOO: `shape_support`, accuracy `0.795`, frontier accuracy `0.867`, micro accuracy `0.8125`, E95-edge accuracy `0.857`, reciprocity MAE `0`.
- best pair-LOO E95-edge stress: `shape_only` accuracy `1.000`.
- pressure branch scores stabilize: E176 favorable branch selected in `3/3` scenarios across all feature sets; E144/E154 favorable branches rejected in `3/3`.
- caveat: the support-based antisymmetric model still misreads E95 versus E101, assigning E101 the win over E95 with high confidence when either file is held out.

Stress implication: the next most informative public sensor is still E176, now for a stronger reason. It is not just visible-body/Q2-underopen; it is also the only live pressure branch selected by a reciprocity-healthy known-LB pair decoder. The E95/E101 miss keeps it below certification.

## Update After E187

E187 stress-tests the exact E95/E101 miss instead of averaging it away.

- script: `analysis_outputs/e187_e95_e101_boundary_miss_anatomy.py`.
- report: `analysis_outputs/e187_e95_e101_boundary_miss_anatomy_report.md`.
- exact E95/E101 file-LOO:
  - `shape_only`: correct, E95 mean probability `0.762677`.
  - `shape_axis_no_support`: correct, same behavior.
  - all support-containing ablations: incorrect, E95 mean probability roughly `0.002..0.050`.
- wider file-LOO E95-edge:
  - shape-only `0.785714`.
  - support variants often `0.857143`.
- branch stress:
  - shape-only and most support variants still select E176 favorable branch in `3/3`.
  - `shape_support_keep_mean_only` loses E176 branch selection.

Stress implication: exact frontier boundary and wider edge-band stress are different validation targets. The support family improves one while breaking the other, so it cannot be the submission selector.

## Update After E188

E188 tests whether low-alpha shape/support logit blending repairs the conflict.

- script: `analysis_outputs/e188_shape_support_logit_blend_stress.py`.
- report: `analysis_outputs/e188_shape_support_logit_blend_stress_report.md`.
- action-grade rows: `0`.
- first exact E95/E101 failure alpha:
  - support variants fail at `0.170..0.285`.
- no positive alpha raises edge accuracy above shape-only while preserving exact E95/E101.

Stress implication: support is not a tunable calibration layer on top of shape geometry. The selector must either use shape-only with lower edge stress or wait for a new representation; support-heavy selection needs an external boundary veto.

## Update After E189

E189 audits where shape-only and support actually disagree.

- script: `analysis_outputs/e189_shape_support_disagreement_atlas.py`.
- report: `analysis_outputs/e189_shape_support_disagreement_atlas_report.md`.
- primary file-LOO E95-edge disagreements:
  - support rescues: `6`.
  - shape-only wins: `4`.
  - both wrong: `0`.
- support rescue concentration:
  - E72-frontier-neighbor share: `1.000`.
  - exact E95/E101 share: `0.000`.
- shape-only win concentration:
  - exact E95/E101 share: `1.000`.
  - E72-frontier-neighbor share: `0.000`.
- file-identity gate:
  - support only on E72-neighbor rows gives E95-edge accuracy `1.000`, frontier accuracy `0.933333`, micro accuracy `0.937500`.
  - not deployable because it depends on known filenames rather than live structural signals.

Stress implication: the support-vs-shape conflict is not a smooth calibration tradeoff. It is two different hidden sensors: support repairs E72-neighbor contamination, shape preserves the tight E95/E101 hardtail boundary. Future validation must include both axes separately.

## Update After E190

E190 tests the first filename-free version of the E72-contamination detector.

- script: `analysis_outputs/e190_e72_contamination_detector.py`.
- report: `analysis_outputs/e190_e72_contamination_detector_report.md`.
- best pair-LOO E72-neighbor detector:
  - view: `shape_target_context_abs`.
  - AUC `0.978836`.
  - average precision `0.809524`.
  - top-k recall `0.666667`.
- any-file LOO:
  - AUC `0.974576` for `shape_target_context_abs`.
  - skipped positive rows `6` because holding out E72 removes all positive training examples.
- exact E95/E101 false positive:
  - `shape_target_context_abs`: mean contamination probability `0.161306`.
  - support/all views: mean contamination probability `0.957369..0.975040`.
- live pressure branches:
  - E176 contamination probability is near zero in every view and never crosses non-E72 p95 or min-positive thresholds.
  - E144 is partially flagged only by the cleaner shape/target/context view, not by support/all views.

Stress implication: movement anatomy can recognize some E72-neighbor structure, but the support-heavy detector is not healthy because it calls exact E95/E101 contamination. The E176 branch does not look E72-contaminated; support should not be used to gate it.

## Update After E191

E191 tests whether explicit exact-boundary hard negatives can make the E72 detector support-safe.

- script: `analysis_outputs/e191_boundary_aware_e72_score.py`.
- report: `analysis_outputs/e191_boundary_aware_e72_score_report.md`.
- best clean pair-LOO row:
  - view/spec: `shape_target_context_abs` / `plain_logit_c025`.
  - AUC `0.978836`.
  - average precision `0.809524`.
  - top-k recall `0.666667`.
  - exact E95/E101 mean probability `0.057658`.
- support-containing clean rows:
  - count `0`.
  - support-only exact E95/E101 probability remains `~0.785758..0.839112`.
  - shape+support/all exact E95/E101 probability remains `~0.766102..0.824223`.
- any-file LOO:
  - clean shape rows still skip `6` E72-positive rows when E72 is held out.
- live pressure branches:
  - E176 remains near zero contamination, max around `0.000008` for the best clean shape row.
  - E144 still has partial shape contamination pressure, but not a support-safe gate.

Stress implication: the support failure is not repaired by hard-negative weighting or prototype contrast. Exact-boundary safety currently belongs to the shape/target/context view only, so support remains a diagnostic latent, not a submission selector.

## Update After E192

E192 decomposes the only E191-clean score instead of creating a new model.

- script: `analysis_outputs/e192_shape_e72_score_anatomy.py`.
- report: `analysis_outputs/e192_shape_e72_score_anatomy_report.md`.
- exact E95/E101:
  - shape E72 probability `0.031016`, below non-E72 p99.
- known thresholds from full-data anatomy:
  - non-E72 p95 `0.020815`.
  - non-E72 p99 `0.044812`.
  - known positive floor `0.804849`.
- live branches:
  - E144 max `0.038723`, crosses p95 in `1/3` but not p99 or positive floor.
  - E154 max `0.007973`, never crosses p95.
  - E176 max `0.000008`, never crosses p95.
- nearest-neighbor stress:
  - E144 top-3 nearest known rows are all non-E72.
  - E176 top-3 nearest known rows are all non-E72 low-score contexts.

Stress implication: clean-shape E72 score is not an action-grade live contamination selector. It is a tail-risk diagnostic. E176 remains the lowest-contamination next sensor; E144's partial alarm should be interpreted as shape-tail risk, not as proof of E72 contamination.

## Update After E193

E193 converts the live E176/E154/E144 dispute into a fixed multi-sensor stress ledger.

- script: `analysis_outputs/e193_live_candidate_evidence_ledger.py`.
- report: `analysis_outputs/e193_live_candidate_evidence_ledger_report.md`.
- signals included:
  - E179 visible full-body and Q2-damping priors.
  - E180 known-winner top-cell calibration.
  - E181 inherited binary-world counterprior.
  - E182/E183 refreshed pressure-range and local-prior branch anatomy.
  - E186 antisymmetric pair geometry.
  - E192 clean-shape E72/tail-risk diagnostics.
- evidence balance:
  - E176: `3.100`.
  - E154: `-0.225`.
  - E144: `-1.725`.

Stress implication: E176 is the best next public sensor by cross-sensor balance, not by certified expected LogLoss. The unresolved stress remains explicit: inherited binary worlds and local pressure-branch priors still warn against E176. This means E176 feedback should be treated as a world-model observation, not as permission for post-hoc keep-factor tuning.

## Update After E194

E194 stress-tests the E193 ledger itself.

- script: `analysis_outputs/e194_evidence_ledger_robustness.py`.
- report: `analysis_outputs/e194_evidence_ledger_robustness_report.md`.
- single-source leaveout:
  - E176 win rate `1.000`.
- Monte Carlo family-weight stress:
  - loguniform `0.25..4`: E176 win rate `0.771300`.
  - loguniform `0.5..2`: E176 win rate `0.905950`.
  - 20% family dropout: E176 win rate `0.896500`.
- adversarial threshold:
  - binary-world weight `>1.760x` flips E176 versus E154.
  - after removing non-comparable visible/top-cell evidence, pair geometry must stay above `0.725x` for E176 to remain above E154.

Stress implication: E176 priority is not a trivial weight artifact, but it depends on trusting pair/shape/broad-body evidence over inherited binary worlds. The next public feedback should explicitly test that worldview conflict.

## Update After E195

E195 stress-tests the next-slot choice after E194 identified E154 as the explicit counter-world.

- script: `analysis_outputs/e195_next_sensor_information_value.py`.
- report: `analysis_outputs/e195_next_sensor_information_value_report.md`.
- E176 rank: `1`.
- E154 rank: `2`.
- E176-vs-E154:
  - moved cells `1027`.
  - moved rows `238`.
  - focus expected delta `-0.000093546`.
  - public-readable but hard-label fragile.
- E154-vs-E144:
  - moved cells `294`.
  - moved rows `139`.
  - local all-minus delta `-0.000002432`.
  - barely readable.
- E154-vs-E155:
  - local all-minus delta `-0.000001796`.
  - not readable by the E158 guard.
- decoder action stress:
  - E176 has `3` adverse bands that route to E154/search.
  - E154 has `0` bands that resolve the E176 broad/Q2-underopen worldview.

Stress implication: E154 is the live counter-world, not the first sensor. E176 first gives a two-sided decision tree: promotion if broad/Q2-underopen wins, and a pre-registered route to E154/search if it loses. Submitting E154 first is coherent only when the binary-world counterprior is intentionally promoted above the E194 flip condition.

## Update After E196

E196 tests a structural motif selector for E176 decisive cells.

- script: `analysis_outputs/e196_e176_motif_nearest_anchor.py`.
- report: `analysis_outputs/e196_e176_motif_nearest_anchor_report.md`.
- views tested:
  - `sequence_only`.
  - `sequence_axis`.
  - `sequence_axis_flank`.
- top sets tested:
  - top4.
  - top16.
  - top33.
- action-grade views: `0/9`.
- best view:
  - `top4 / sequence_axis_flank`.
  - known-pair LOO accuracy `0.833333`.
  - exact E101/E95 boundary correctness `0`.
  - mixmin broad-success correctness `1`.
- E176 read:
  - best-view nearest anchor `e72_vs_e95`, direction `new_lost`.
  - inverse-distance vote new_won `0.505761`.
  - top33 nearest winner `mixmin_vs_a2c8`, but top33 LOO accuracy only `0.333333`.

Stress implication: row/order/block motif has signal but fails the frontier-boundary requirement. It is a warning/anatomy layer, not a submission selector and not enough to demote E176 before public feedback.

## Update After E197

E197 tests a public-score inverse support-mass decoder.

- script: `analysis_outputs/e197_public_support_mass_inverse.py`.
- report: `analysis_outputs/e197_public_support_mass_report.md`.
- equation: `delta = adverse_sum - q * swing_sum`.
- known-pair slippage versus visible prior:
  - E72-vs-E95: `-0.071348`.
  - E72-vs-mixmin: `-0.120707`.
  - E95-vs-mixmin: `-0.031934`.
  - mixmin-vs-a2c8: `+0.025458`.
- E176 profile:
  - visible surplus to tie `0.061761`.
  - focus surplus to tie `0.094836`.
  - visible stress clean-or-better `4/6`, win `4/6`, branch/hard fail `1/6`.
  - focus stress clean-or-better `4/6`, win `5/6`, branch/hard fail `1/6`.
- E172 profile:
  - visible surplus to tie `0.070613`; slightly safer than E176 in this lens.
- E154/E144/E155:
  - visible surplus to tie only `0.010284`/`0.011545`/`0.011227`.
  - visible stress branch/hard fail `4/6`.

Stress implication: E176 is not certified, but its failure mode is now narrower. It loses only if the next public observation behaves like E72-like adverse slippage. E154 remains a counter-world, not the first stress survivor.

## Update After E198

E198 joins E197 slippage stress with the E191/E192 boundary-clean E72 shape diagnostic.

- script: `analysis_outputs/e198_e72_slippage_exposure.py`.
- report: `analysis_outputs/e198_e72_slippage_exposure_report.md`.
- detector health:
  - clean detector `shape_target_context_abs / plain_logit_c025 / loo_pair_id`.
  - AUC `0.978836`.
  - AP `0.809524`.
  - top-k recall `0.666667`.
  - exact E95/E101 mean probability `0.057658`.
- thresholds:
  - non-E72 p95 `0.020815`.
  - non-E72 p99 `0.044812`.
  - E72-positive floor `0.804849`.
- E176:
  - visible E72-vs-E95 stress: `small_loss`.
  - visible E72-vs-mixmin stress: `branch_loss`.
  - focus E72-vs-E95 stress: `micro_win`.
  - focus E72-vs-mixmin stress: `branch_loss`.
  - max clean E72 probability `0.000008`, below non-E72 p95.
- E154:
  - thin margin, hard-fails under E72 analogues.
  - max clean E72 probability `0.007973`, below non-E72 p95.
- E144:
  - thin margin, hard-fails under E72 analogues.
  - max clean E72 probability `0.038723`, above p95 but below p99 and far below positive floor.

Stress implication: E176's failure mode remains real but is not structurally E72-like under the clean shape detector. The loss condition is public hidden-label slippage, not a pre-visible E72 contamination signature. This strengthens E176 as the next sensor but does not certify expected LB.

## Update After E199

E199 fills the E198 missing-score gap by scoring direct candidate-vs-E95 movements for all E197 candidates.

- script: `analysis_outputs/e199_candidate_shape_e72_exposure.py`.
- report: `analysis_outputs/e199_candidate_shape_e72_exposure_report.md`.
- direct clean-shape E72 probabilities:
  - E144: `0.054385`, `non_e72_p99_tail`.
  - E155: `0.009284`, below p95.
  - E154: `0.007860`, below p95.
  - E166: `0.000677`, below p95.
  - E176: `0.000097`, below p95.
  - E174: `0.000097`, below p95.
  - E172: `0.000087`, below p95.
- thresholds:
  - non-E72 p95 `0.020815`.
  - non-E72 p99 `0.044812`.
  - E72-positive floor `0.804849`.
- nearest-known check:
  - E144 top-3 nearest known rows are still all non-E72.
  - E172/E174/E176 nearest contexts are low-score a2c8/jepa-latent/raw-jepa contexts, not E72 positives.

Stress implication: the post-E176 route is cleaner than E198 could prove. E172 is not an E72-shaped same-family fallback; E154/E155 are not E72-shaped repaired branches; E144 carries the only direct p99 tail alarm and should remain a control rather than first counter-world.

## Update After E200

E200 stress-tests the practical ordering question created by E199: should the cleaner E172 fallback replace E176 as the first public sensor?

- script: `analysis_outputs/e200_e176_vs_e172_first_sensor_resolution.py`.
- report: `analysis_outputs/e200_e176_vs_e172_first_sensor_resolution_report.md`.
- candidate comparison:
  - E172 focus expected delta vs E95: `-0.000112695`.
  - E176 focus expected delta vs E95: `-0.000123384`.
  - E174 focus expected delta vs E95: `-0.000124367`.
- E176 over E172:
  - expected edge `0.0000106885`.
  - `0.698x` of E95-over-mixmin public edge.
  - E176-vs-E172 changed cells `75`.
- E172 over E176:
  - visible surplus advantage `0.008852`.
  - focus surplus advantage `0.007054`.
  - direct clean-shape E72 probability advantage `0.00000972`.
- information stress:
  - E176-vs-E172 is only `0.114x` of E176-vs-E154 by expected-delta magnitude.
  - E176-vs-E154 moves `1027` cells and resolves the main broad-vs-repaired-branch conflict.

Stress implication: E172 passes as a clean safety fallback, but not as a first-slot replacement. The ordering is robust to the E199 cleanliness update: E176 first, E172 after tie/small-loss, E154 after branch/hard-loss.

## Update After E201

E201 stress-tests the process risk: the next E176 public score must not be interpreted after the fact by whichever story fits the number.

- script: `analysis_outputs/e201_e176_public_sensor_packet.py`.
- report: `analysis_outputs/e201_e176_public_sensor_packet_report.md`.
- audited E176 SHA256: `34d38587b04640327824b972f4cbc18ae03cab2f92802ac7c144f94b96184206`.
- file audit:
  - rows/columns: `250/10`.
  - sample columns and key order: exact match.
  - duplicate keys: `0`.
  - probability range: `0.068110176672..0.979776651464`.
  - changed cells vs E95: `904` over `193` rows.
- route stress:
  - E176 better than `0.5762883298`: broad/Q2-underopen branch remains useful, but no same-family sibling is justified immediately.
  - E176 from `0.5762883298` to `0.576300366`: the same-family branch is underresolved or slightly bad; E172 is the only coherent same-family safety test.
  - E176 worse than `0.576300366`: the partial-reopen branch is demoted; E154/search becomes the next branch.
  - E176 worse than `0.5763413298`: same-family expected-score lane closes.

Stress implication: the next public observation is now a fixed decision-tree test. This does not make E176 safer, but it makes the feedback interpretable and prevents post-score Q2 keep-factor tuning.

## Update After E202

E202 stress-tests component-responsibility risk: even with the E201 route table, E176 could still be misread as a scalar Q2 keep-factor test because of the file name.

- script: `analysis_outputs/e202_e176_component_responsibility_router.py`.
- report: `analysis_outputs/e202_e176_component_responsibility_report.md`.
- component stress:
  - S-target expected-share: `0.651098`.
  - Q-target expected-share: `0.348902`.
  - between-train-runs expected-share: `0.807772`.
  - Q2 raw movement share: `0.209702`.
  - Q2 expected-share: `0.121416`.
  - top33 visible-support `p_low`: `0.014667`.
- target responsibility:
  - primary S-stage body: S3 `0.203515`, S1 `0.189679`, S4 `0.146985`.
  - Q2 is a name-mismatch target: biggest raw movement, mid expected gain.
  - Q3 is visibly supported but low expected share.
- outcome stress:
  - clean win or breakthrough: credit broad S-stage / between-train-runs body first.
  - micro win: sign is right but hard-label resolution is thin.
  - tie/small-loss: read tail/cancellation failure before Q2 amplitude failure.
  - branch/hard loss: demote same-family partial-reopen and route to E154/search.

Stress implication: E176's next public score has two layers of interpretation. E201 chooses the route by score band; E202 assigns component responsibility inside that route. This prevents a Q2-only post-hoc read.

## Update After E203

E203 stress-tests whether E176 is a broad body or only a compact critical-cell bet.

- script: `analysis_outputs/e203_e176_component_knockout_stress.py`.
- report: `analysis_outputs/e203_e176_component_knockout_stress_report.md`.
- broad-body stress:
  - S-only focus share `0.644881`.
  - primary S-stage S3/S1/S4 share `0.573289`.
  - between-train-runs share `0.774524`.
  - dropping between-train-runs leaves `0.225476`.
- target-amplitude stress:
  - Q2-only share `0.093922`.
  - dropping Q2 leaves `0.906078`.
- hard-tail stress:
  - top33 share `0.226424`.
  - dropping top33 still leaves `0.773576`.
  - top33 visible support `0.245771`.
  - only top8 has E72-tail-risk role with E72 active rate `0.625`.

Stress implication: E176 should not be demoted merely because top critical cells are weakly visible; those cells are not the whole signal. But if public rejects E176, the most coherent blame is compact hard-tail cancellation rather than absence of the broad S/body structure.

## Update After E204

E204 stress-tests follow-up interchangeability after E176 feedback.

- script: `analysis_outputs/e204_e176_followup_correction_map.py`.
- report: `analysis_outputs/e204_e176_followup_correction_map_report.md`.
- E172:
  - changed cells vs E176 `75`.
  - off-E176 abs share `0.000000`.
  - rollback share in overlap `1.000000`.
  - body rollback fraction `0.089780`.
  - metric focus delta on E176 cells `+0.000001778`; visible delta `-0.000002029`.
- E154:
  - changed cells vs E176 `1027`.
  - off-E176 abs share `0.292501`.
  - body rollback fraction `0.877576`.
  - metric focus delta on E176 cells `+0.000082018`.
- E174:
  - changed cells vs E176 `21`.
  - off-E176 abs share `0.000000`.
  - rollback share `0.000000`.
  - metric focus delta `-0.000000082`; visible delta `+0.000000191`.

Stress implication: E172, E154, and E174 do not form a scalar ladder. They ask different hidden-world questions. E172 is same-family safety, E154 is body-exit counter-world, and E174 is Q2 amplitude probe only after broad-body validation.

## Update After E205

E205 stress-tests the feedback process itself.

- script: `analysis_outputs/e205_e176_public_feedback_executable_decoder.py`.
- report: `analysis_outputs/e205_e176_public_feedback_executable_decoder_report.md`.
- routebook: `analysis_outputs/e205_e176_public_feedback_executable_decoder_routebook.csv`.
- examples: `analysis_outputs/e205_e176_public_feedback_executable_decoder_examples.csv`.

Process stress:

- every public score band maps to exactly one outcome.
- every outcome carries a component interpretation inherited from E202.
- every outcome carries body/tail constants inherited from E203.
- every outcome carries a follow-up role inherited from E204.
- optional `--score` writes a selected JSON record for the actual E176 public LB.

Stress implication: post-E176 public feedback is no longer a free-form interpretation step. If a score near `0.576291` arrives, the decoder routes to E172 safety; if a score near `0.576303` arrives, it routes to E154 counter-world. Clean wins do not authorize immediate sibling sweeps.

## Update After E206

E176 public feedback was observed and decoded.

- submission: `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`.
- public LB: `0.576311831`.
- E205 outcome: `branch_loss`.
- score band: `(0.5763066405, 0.5763413298]`.
- worldview update: `close_same_family_expected_score_lane`.
- coherent existing follow-up: `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.

Stress implication: E176 failed exactly in the branch-loss band, not the tie/small-loss safety band. This weakens same-family expected-score follow-ups and makes E154/search the next valid question. E172 remains a safety contrast, but not the immediate response to this score.

## Update After E207

E207 stress-tests JEPA positive-pair regimes before training a new JEPA.

- script: `analysis_outputs/e207_lejepa_identifiability_conditions_audit.py`.
- report: `analysis_outputs/e207_lejepa_identifiability_conditions_audit_report.md`.
- summary: `analysis_outputs/e207_lejepa_identifiability_conditions_audit_summary.csv`.

Stress dimensions:

- random-projection marginal Gaussianity.
- positive-pair increment Gaussianity.
- coordinate autocorrelation and anisotropy.
- positive-pair distance versus random-pair distance.
- effective rank / covariance health.
- train-label consistency when both endpoints are train rows.
- known frontier-movement smoothness for E101/E154/E176 versus E95 when both endpoints are submission rows.
- split-distance CV for regimes containing train/submission/mixed pairs.

Result:

- `true_jepa_candidate`: `1/77`.
- best certified regime: `broad_stage2_pca64 + feature_nn1_all`.
- strongest rejected-as-auxiliary regime: `lejepa_l0p2_d32_pca48 + subject_lag2_all`, because increment Gaussianity is low and split stationarity is weak.

Stress implication: true JEPA training should not begin with subject-order pairs or an all-regime average. The next JEPA experiment must start from feature-neighbor positive pairs and keep subject/order/block-canvas latents as auxiliary gates until they pass increment/stationarity stress.

## Update After E208

E208 stress-tests an actually trained JEPA representation, not just a JEPA-style diagnostic.

- script: `analysis_outputs/e208_feature_neighbor_jepa_probe.py`.
- report: `analysis_outputs/e208_feature_neighbor_jepa_probe_report.md`.
- training controls:
  - seed `261002`: validation MSE `0.588331`, copy-self `0.812629`, mean-target `0.639551`.
  - seed `261020`: validation MSE `0.555652`, copy-self `0.885360`, mean-target `0.613004`.
  - seed `261038`: validation MSE `0.550826`, copy-self `0.815146`, mean-target `0.630471`.
- geometry stress:
  - prediction mean is compressed/anistropic: rank fraction `0.287411`, condition `1365.92`.
  - hidden mean is healthier: rank fraction `0.611836`, condition `44.0311`.
  - Q3 `e208_resid_self_pc10` has multiple OOF/subject/geometry passing rows.
  - S4 `e208_pred_pc14` passes one geometry-stressed row.
  - S2 has strong local/subject deltas but geometry delta is positive, so it fails the E208 gate.

Stress implication: JEPA is not a dead idea here. The bottleneck is translation. A trained feature-neighbor JEPA finds real target-specific residual structure, but the full latent is too anisotropic and only Q3/S4 survive stress. E209 should materialize Q3/S4 only, with E95/E154 geometry comparison before public submission.

## Update After E209

E209 stress-tests the probability translation of the trained E208 JEPA signal.

- script: `analysis_outputs/e209_feature_neighbor_jepa_materialization_stress.py`.
- report: `analysis_outputs/e209_feature_neighbor_jepa_materialization_report.md`.
- summary: `analysis_outputs/e209_feature_neighbor_jepa_materialization_summary.csv`.
- frontier stress: `analysis_outputs/e209_feature_neighbor_jepa_materialization_frontier_stress.csv`.

Stress dimensions:

- stage2 OOF delta for the learned Q3/S4 movement.
- repeated subject-half delta and win rate.
- geometry-fold delta and win rate.
- E95/E154/mixmin graft safety.
- known bad-axis cosine and bad-span energy.
- hard-label top-cell concentration under focus priors.
- schema audit for each selected submission.

Result:

- `q3_center_c010_s4_rank` passes OOF, subject-half, and geometry stress: delta `-0.001272724`, subject-half win rate `0.900000`, geometry delta `-0.000794598`.
- the best survival candidate is `submission_e209_jepa_q3_center_c010_s4_rank_e154_s0p25_1e4591ca.csv`, survival score `0.013853189`.
- the cleanest current-frontier JEPA sensor is `submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv`, survival score `0.012445288`.
- high-scale Q3/S4 grafts fail the E209 frontier gate despite larger local expected deltas.

Stress implication: actual JEPA now produces submission-grade candidates, but only as a narrow Q3/S4 low-scale graft. The full-latent and high-scale interpretations remain rejected. Public feedback should be decoded as a test of JEPA probability translation, not as proof that JEPA has solved the 0.54 gap.

## Update After E210

E210 stress-tests a target-dependency gate for the E209 JEPA movement.

- script: `analysis_outputs/e210_jepa_target_dependency_gate.py`.
- report: `analysis_outputs/e210_jepa_target_dependency_gate_report.md`.
- selected: `analysis_outputs/e210_jepa_target_dependency_gate_selected.csv`.

Stress dimensions:

- OOF target-conditional dependency alignment.
- repeated subject-half stability.
- geometry-fold stability.
- anti-toward negative control.
- E95/E154/mixmin frontier graft stress.
- hard-label top-cell concentration and bad-axis energy.

Result:

- Q3/S4 closer-gated files have much better public-prior hard-tail anatomy than E209: top selected e154 file has focus delta `-0.001379` and top1/abs `0.171181`.
- the same selected files lose local evidence versus ungated E209: OOF `-0.000482` versus `-0.001273`, geometry `-0.000096` versus `-0.000939`.
- S4 dependency alignment is meaningful locally; Q3 dependency alignment is not clean because Q3 not-closer/not-toward cells carry larger local gains.
- anti-toward controls do not pass frontier gates, so the public-prior side is not completely polarity-free.

Stress implication: E210 is a hard-tail localization sensor, not an E209 replacement. It strengthens the diagnosis that the remaining JEPA bottleneck is target-specific probability translation, especially Q3 versus S4 dependency conflict.

## Update After E211

E211 stress-tests the target-specific fix implied by E210: keep Q3 raw, dependency-gate only S4.

- script: `analysis_outputs/e211_target_specific_jepa_gate.py`.
- report: `analysis_outputs/e211_target_specific_jepa_gate_report.md`.
- selected: `analysis_outputs/e211_target_specific_jepa_gate_selected.csv`.

Stress dimensions:

- OOF and targetwise deltas versus stage2 and ungated E209.
- repeated subject-half stability.
- geometry-fold stability.
- raw/toward/closer/soft/anti/zero S4 gate controls.
- E95/E154/mixmin frontier graft stress.

Result:

- Q3 raw + S4 toward improves OOF over ungated E209: `-0.001318` versus `-0.001273`.
- Q3 raw + S4 closer is nearly tied locally: `-0.001315`.
- both keep subject-half win rates above `0.96` and geometry win rate `0.875`.
- geometry delta is weaker than raw E209 under the E211 geometry seed but remains clearly negative: toward `-0.000659`, closer `-0.000620`.
- selected E154 closer candidate has focus delta `-0.000685`, top1/abs `0.229657`, and bad-span energy `0.348576`.

Stress implication: E211 is a real improvement over the blunt E210 gate. It supports target-specific translation: Q3 should preserve JEPA body, while S4 can be dependency-gated. This is currently the best structured JEPA follow-up family.

## Update After E212

E212 converts the E209/E210/E211 validation evidence into a submission-order stress report.

- script: `analysis_outputs/e212_jepa_family_sensor_ordering.py`.
- report: `analysis_outputs/e212_jepa_family_sensor_ordering_report.md`.
- summary: `analysis_outputs/e212_jepa_family_sensor_ordering_summary.csv`.
- routebook: `analysis_outputs/e212_jepa_family_sensor_ordering_routebook.csv`.
- pairwise movement: `analysis_outputs/e212_jepa_family_sensor_ordering_pairwise.csv`.

Stress dimensions:

- local OOF delta and parent-integrity versus the previous JEPA family member.
- geometry delta and geometry win rate.
- public-prior hard-tail survival, top1/abs concentration, and bad-axis cosine.
- anchor purity: E95 clean sensor versus E154-confounded survival.
- pairwise movement similarity against E95.
- routebook interpretability of future public feedback.

Result:

- structured survival rank 1 is E211 E154 closer, score `0.831942`.
- clean sensor rank 1 is E211 E95 toward, score `0.962262`.
- E209 E95 Q3/S4 is the raw-JEPA control, clean sensor rank 3.
- E210 closer files have high hard-tail survival but weak parent integrity (`~0.019..0.027`) because their local delta is much worse than ungated E209.
- E211 E154 closer and E211 E154 toward are near twins (`cosine=0.996351`), while E211 E95 toward and closer are also near twins (`cosine=0.994943`).

Stress implication: the next JEPA public slot should be E211, not E210. The maximum-survival version uses the E154 anchor; the cleanest hypothesis test uses the E95 anchor. E212 adds no new performance claim, but it prevents post-hoc interpretation of whichever JEPA sensor is submitted.

## Update After E213

E213 adds a specificity stress test for the actual JEPA axes used by E209/E211.

- script: `analysis_outputs/e213_jepa_axis_specificity_audit.py`.
- report: `analysis_outputs/e213_jepa_axis_specificity_audit_report.md`.
- summary: `analysis_outputs/e213_jepa_axis_specificity_audit_summary.csv`.
- nulls: `analysis_outputs/e213_jepa_axis_specificity_audit_nulls.csv`.
- pool audit: `analysis_outputs/e213_jepa_axis_specificity_audit_pool.csv`.

Stress dimensions:

- global row permutation null.
- within-subject permutation null.
- same-family PC coordinate pool.
- original E208 scan rank and geometry pass status.
- subject-half fixed-weight stability.

Result:

- Q3 `e208_resid_self_pc10` is specific: delta `-0.005775`, subject-half win `0.95`, permutation p-values `0.020408`, and pool rank `1/16`.
- S4 `e208_pred_pc14` is also specific: delta `-0.003134`, subject-half win `0.733333`, permutation p-values `0.020408`, and pool rank `1/16`.
- All permutation null medians are adverse, and the best same-family S4 alternative is still adverse.

Stress implication: E211 is not mainly a latent-coordinate cherry-pick. The live bottleneck remains public-tail probability translation, not whether JEPA found a real narrow representation.

## Update After E214

E214 stress-tests a direct translation repair: learn subject-CV benefit gates for the E209/E211 Q3/S4 JEPA step.

- script: `analysis_outputs/e214_jepa_benefit_gate_translation.py`.
- report: `analysis_outputs/e214_jepa_benefit_gate_translation_report.md`.
- gate audit: `analysis_outputs/e214_jepa_benefit_gate_translation_gate_audit.csv`.
- summary: `analysis_outputs/e214_jepa_benefit_gate_translation_summary.csv`.
- frontier stress: `analysis_outputs/e214_jepa_benefit_gate_translation_frontier_summary.csv`.

Stress dimensions:

- subject-CV gate OOF.
- subject-half stability.
- geometry-fold refit.
- raw probability, rank-normalized, margin, and dependency-composed gate variants.
- E95/E154 frontier hard-tail stress.

Result:

- Q3 benefit gate AUC is `0.552169`; S4 benefit gate AUC is `0.568968`.
- E211-style baseline remains best locally: `baseline_q3raw_s4toward` delta `-0.001318`.
- Best benefit-gated local policy is only `q3raw_s4benefit_rank` at `-0.000918`.
- Benefit gates can improve geometry in one case (`q3raw_s4benefit_rank` geometry `-0.000987`), but the local loss is too large.
- No benefit-gated policy passes the E214 frontier gate; no submission is selected.

Stress implication: simple learned benefit gating is not the missing JEPA translator. E211 remains the stronger public sensor.

## Update After E215/E216

E215 and E216 test a different JEPA target representation: masked feature-family blocks.

- E215 script: `analysis_outputs/e215_masked_family_jepa_probe.py`.
- E215 report: `analysis_outputs/e215_masked_family_jepa_report.md`.
- E216 script: `analysis_outputs/e216_masked_family_jepa_materialization.py`.
- E216 report: `analysis_outputs/e216_masked_family_jepa_materialization_report.md`.

E215 stress result:

- Training val MSE `0.585-0.604` versus mean-block MSE around `1.000`.
- Geometry-stressed pass count: `10`.
- Best downstream target deltas:
  - Q1 `e215_pred_pc06`: `-0.004965`.
  - S2 `e215_resid_pc10`: `-0.004370`.
  - S4 `e215_deep_resid_abs_mean`: `-0.003313`.

E216 frontier result before public feedback:

- Strongest local combo `q1_s2_s4_rank`: delta `-0.001807`, subject-half win `1.000`, geometry `-0.001628`.
- Frontier stress rejects that broad combo at useful scales.
- S2-only survives:
  - `submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv`.
  - `submission_e216_maskfam_jepa_s2_rank_e95_s0p75_4f8dc44d.csv`.
  - `submission_e216_maskfam_jepa_s2_rank_e154_s0p5_0ca3d931.csv`.
  - `submission_e216_maskfam_jepa_s2_rank_e95_s0p5_4516fb93.csv`.

Stress implication before public feedback: changing the JEPA target representation is useful. But the public-safe translation appeared narrower than the locally strongest representation signal; for E215, S2 was the clean survivor.

Public feedback update:

- `submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv`: public LB `0.5772865088`.
- Delta vs E95: `+0.0009951790`.
- Delta vs mixmin: `+0.0009798683`.
- Delta vs E101: `+0.0009861428`.

Stress implication after public feedback: E216 is a stress false positive. The local/subject/geometry/frontier stack rejected the broad Q1/S2/S4 combo but still failed to detect a public-adverse S2-only tail. Remaining E216 siblings are demoted to negative controls; the stress design needs an S2-specific public-tail audit before another masked-family S2 submission.

E219 root-cause audit:

- script: `analysis_outputs/e219_e216_public_miss_anatomy.py`.
- report: `analysis_outputs/e219_e216_public_miss_anatomy_report.md`.
- E154 body all-adverse capacity vs E95 is `0.000924070`, which is smaller than the observed E216 miss of `0.0009951790`.
- Pure S2 graft all-adverse capacity vs E95 is `0.006048995`, enough to explain the public miss without invoking the E154 body.
- Focus-prior S2 graft support probability is only `0.473945` swing-weighted. This is the missing stress condition: expected delta was slightly favorable, but the support side of the move was below `0.5`.
- Near-observed focus-prior worlds attribute `0.000920169` mean delta to the S2 graft and `-0.000004004` to E154 body.

Stress implication after E219: the old gate over-weighted expected focus delta and under-weighted support probability. Future S2 JEPA materialization needs a `support_prob_swing_weighted > 0.5` or equivalent low-support-tail guard, plus top-cell pruning, before it can be public-safe.

E220 support-gate audit:

- script: `analysis_outputs/e220_s2_support_tail_gate_audit.py`.
- report: `analysis_outputs/e220_s2_support_tail_gate_report.md`.
- no simple support/tail gate passes full criteria.
- High support is not enough: `focus_support_ge_0p7` keeps only `7` cells and has adverse capacity `0.000209735`, but expected focus movement is bad (`+0.000018940`).
- Expected-negative is not enough: `focus_support_ge_0p6_expected_neg` keeps `61` cells with expected `-0.000578857`, but adverse capacity `0.001402108` is still above the observed E216 miss.
- Pure expected-negative is larger but also unsafe: `expected_neg_only` expected `-0.001204825`, adverse `0.002118163`.

Stress implication after E220: add a support-probability metric to future stress reports, but do not treat thresholding as a rescue. S2 JEPA needs a train/OOF-reproducible support model before any new submission file is actionable.

E221 OOF support-classifier audit:

- script: `analysis_outputs/e221_s2_oof_support_classifier.py`.
- report: `analysis_outputs/e221_s2_oof_support_classifier_report.md`.
- support-label rate: `0.551111`.
- full E216 S2 target OOF delta versus stage2: `-0.004370425`.
- best local support AUCs: stratified `0.748104`, row-contiguous `0.717482`, subject-LOO `0.713730`, subject-fold `0.696682`.
- OOF gates can look strong; `hgb_shallow__subject_loo/top250` gives support precision `0.704000`, S2 delta `-0.004050232`, subject win `0.700000`.
- no joint gate passes OOF support reproduction plus submission-side tail stress.

Stress implication after E221: S2 support is learnable locally, but the learned support boundary is not invariant to the public-facing test tail. This closes ordinary OOF support classifiers as an E216 rescue. A future S2 JEPA submission must change the representation/loss target rather than learn a gate on the same E215 features.

E222 E211 support-tail audit:

- script: `analysis_outputs/e222_e211_support_tail_audit.py`.
- report: `analysis_outputs/e222_e211_support_tail_audit_report.md`.
- E211 E154 closer graft vs anchor: expected focus `-0.000655277`, adverse `0.004765654`, support probability `0.463231`, top1/expected `0.240115`.
- E211 E95 toward graft vs anchor: expected focus `-0.000654330`, adverse `0.004824911`, support probability `0.463587`, top1/expected `0.240462`.
- E216 S2 negative control vs anchor: expected focus `-0.000288312`, adverse `0.006048480`, support probability `0.473945`.
- Target breakdown: E211 S4 has expected focus about `-0.00051` and low top-cell concentration (`~0.166x`), while Q3 has expected focus only `-0.000144..-0.000147` and top1/expected above `1.0x`.

Stress implication after E222: E211 is a live JEPA lane but not a support-safe lane. Its hidden-world bet should be narrowed: preserve S4, reduce Q3 tail exposure, and interpret public feedback as a Q3/S4 support sensor.

E223 Q3-tail rebalance:

- script: `analysis_outputs/e223_e211_q3_tail_rebalance.py`.
- report: `analysis_outputs/e223_e211_q3_tail_rebalance_report.md`.
- selected risk-rebalanced file: `analysis_outputs/submission_e223_jepa_q3s0p75_s4closer_e154_a0p5_794b0349.csv`.
- graft vs E154: expected focus `-0.000636968`, adverse `0.003852760`, support probability `0.464872`, geometry delta `-0.000556139`.
- actual vs E95: expected focus `-0.000666805`, adverse `0.004533247`, top1/expected `0.176972`.
- Relative to original E211 E154 closer actual-vs-E95, E223 reduces adverse capacity by about `0.00089358` while sacrificing only about `0.00001831` expected focus.

Stress implication after E223: E223 is the preferred JEPA-family public sensor if using one JEPA slot now. It does not solve the sub-0.5 support-probability problem, but it materially reduces the specific Q3 tail failure exposed by E222.

E224 Q3-scale Pareto stress:

- script: `analysis_outputs/e224_e211_q3_scale_pareto.py`.
- report: `analysis_outputs/e224_e211_q3_scale_pareto_report.md`.
- selected file: `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
- selected graft-vs-anchor metrics: local delta `-0.001098893`, geometry delta `-0.000505582`, expected focus `-0.000623352`, adverse capacity `0.003400775`, support probability `0.465984`, Q3 top1/expected `0.875120`.
- q3_scale `0.75` keeps more local body but fails the E224 gate because Q3 top1/expected remains too high (`~0.92..0.94`) and adverse capacity is larger.
- q3_scale `0.50` is safer but gives up too much local body for the current JEPA sensor role.

Stress implication after E224: the current JEPA stress stack favors a capped-Q3 knee at `0.625`, not full-Q3 E211 and not E223 `0.75`. The remaining risk is still support probability below `0.5`, so E224 is a public sensor rather than a safe expected-score certificate.

E225 E224 public-feedback decoder:

- script: `analysis_outputs/e225_e224_public_feedback_decoder.py`.
- report: `analysis_outputs/e225_e224_public_feedback_decoder_report.md`.
- routebook: `analysis_outputs/e225_e224_public_feedback_decoder_routebook.csv`.
- E224 public score bands are locked before feedback: clean win `<=0.576276019`, micro win up to `0.576288330`, tie up to `0.576294330`, small loss up to E101 `0.576300366`, mixmin-safe loss up to mixmin `0.576306641`, branch loss up to `0.576341330`, hard fail above.
- movement anatomy: E224 vs E95 moves `534` cells and remains E211-line collinear (`cos=0.975464` vs full E211, `0.996078` vs E223) while staying far from E216 S2 miss (`cos=0.043542`).

Stress implication after E225: the E224 public score must be read as a capped-Q3 translator test. A win does not authorize bigger Q3; a loss worse than mixmin closes the current E211-family expected-score lane until a new support/tail representation is built.

E226 non-collinear candidate scan:

- script: `analysis_outputs/e226_noncollinear_candidate_scan.py`.
- report: `analysis_outputs/e226_noncollinear_candidate_scan_report.md`.
- evaluated `73` documented/materialized files and skipped `2` duplicate references.
- stress dimensions:
  - cosine distance from E224/E223/E211/E216/E176/E72/E154/E101/mixmin.
  - E222 support-tail anatomy: expected focus movement, adverse capacity, swing-weighted support, top-cell concentration.
  - explicit vetoes for known public-negative anchors, same-Q3/S4 JEPA siblings, S2 bad-axis neighbors, E72/E176 bad-axis neighbors, hardtail parent diagnostics, high adverse capacity, and E52 local near-tie.
- top actionable independent row: `submission_e166_broadsurv_s0p01_d8bfa94b.csv` with score `1.686847`, cos(E224) `0.074348`, cos(E216) `0.055999`, cos(E72) `0.108706`, expected focus `-0.000332077`, adverse `0.000713053`, support `0.465747`.
- repaired-branch cluster remains live but not independent from itself: E144/E156/E157/E155/E143/E142/E154 form one family, with E154 retained as the conservative counter-world.

Stress implication after E226: E224-neighbor files are not escape routes; they are amplitude variants of the same Q3/S4 translator. If a non-E224 public sensor is needed, E166 is the information-rich broad counter-world and E154 is the conservative repaired-branch counter-world. E216-style S2 and E52 bridge near-tie are closed until a new stress dimension is built.

E227 E166 public-feedback decoder:

- script: `analysis_outputs/e227_e166_public_feedback_decoder.py`.
- report: `analysis_outputs/e227_e166_public_feedback_decoder_report.md`.
- routebook: `analysis_outputs/e227_e166_public_feedback_decoder_routebook.csv`.
- stress dimensions:
  - pre-registered score bands relative to E95, E101, mixmin, E176, E72, and E216.
  - movement geometry between E166, E224, E154, E176, E216, E101, mixmin, and E72.
  - E167 context evidence: edge-like, between-train-runs, E72-active, all-veto-null, safe-density, and E101-plausible mass.
- key E166 anatomy: `1750` moved cells, `250` rows, all `7` targets, cos(E224) `0.074348`, expected focus `-0.000332077`, adverse `0.000713053`, support `0.465747`.
- top-benefit context warning: edge-like `0.689189` and between-train-runs `0.797297` are high, but E72-active is also high at `0.837838` and all-veto-null is low at `0.297297`.

Stress implication after E227: E166 is valid only as a broad hidden-world public sensor. A win strengthens broad survivor context and weakens hard safety-atlas vetoes; a loss strengthens the E72-active/low-veto-null warning. No E166 sibling or scale change should be used before score decoding.

E228 tri-world conflict atlas:

- script: `analysis_outputs/e228_triworld_conflict_atlas.py`.
- report: `analysis_outputs/e228_triworld_conflict_atlas_report.md`.
- outputs: `analysis_outputs/e228_triworld_conflict_atlas_summary.csv`, `analysis_outputs/e228_triworld_conflict_atlas_pairwise.csv`, `analysis_outputs/e228_triworld_conflict_atlas_targets.csv`, `analysis_outputs/e228_triworld_conflict_atlas_blocks.csv`, `analysis_outputs/e228_triworld_conflict_atlas_cells.csv`.
- stress dimensions:
  - pairwise cosine and top-k active-cell overlap.
  - same-sign shared movement mass versus sign-conflict mass.
  - target-level conflict rates.
  - subject/block concentration of live movement and conflicts.
- key results:
  - E224/E166 cosine `0.074348`; same-sign E166 covers only `0.035638` of E224 mass; top50 overlap `1` cell.
  - E166/E154 cosine `0.061662`; top50 overlap `0`.
  - E224/E154 cosine `0.316350`; E154 active cells are fully inside E224 active cells, and same-sign shared movement covers `0.885621` of E154 mass.
  - E224/E166 target conflict is concentrated in Q3/S4, with Q3 conflict rate `0.536444`.

Stress implication after E228: E224 and E166 should remain separate high-information public sensors. E154 is a conservative branch counter-world, but not a clean independent alternative to E224 because E224 already includes most of the E154 repaired body. A blind tri-world blend is rejected before feedback.

E229 next public-slot decision audit:

- script: `analysis_outputs/e229_next_public_slot_decision.py`.
- report: `analysis_outputs/e229_next_public_slot_decision_report.md`.
- summary: `analysis_outputs/e229_next_public_slot_decision_summary.csv`.
- route summary: `analysis_outputs/e229_next_public_slot_decision_route_summary.csv`.
- stress dimensions:
  - E216 and E176 inserted into `analysis_outputs/public_probe_observations.csv`.
  - 14-anchor public bottleneck proxy rerun after E216.
  - E225/E227/E160 routebook outcome coverage.
  - E228 pairwise conflict/overlap evidence.
  - expected edge compared to proxy error floor.
- key results:
  - best public-anchor proxy remains `raw05_a2c8_compat`, MAE `0.000496259`, p90 `0.000695363`.
  - this error floor is still larger than E95/E101/mixmin/E176 gaps, so proxy score ranking is invalid for the next frontier file.
  - E224 remains the JEPA-first public sensor because it is Q3/S4-dominant and nearly orthogonal to the failed E216 S2 translator (`cos_vs_e216=0.043542`).
  - E166 remains the independent broad sensor (`cos_vs_e224=0.074348`).
  - E154 remains conditional because its body is mostly contained in E224 (`0.885621` same-sign E154 mass coverage).

Stress implication after E229: the next slot is not a universal "best expected LB" file. It is an observation choice. Use E224 for the JEPA question, E166 for the independent broad-world question, and E154 only after attribution or after those questions are demoted.

E230 E224 support-tail prune stress:

- script: `analysis_outputs/e230_e224_support_tail_prune_audit.py`.
- report: `analysis_outputs/e230_e224_support_tail_prune_audit_report.md`.
- selected files:
  - `analysis_outputs/submission_e230_q3_swingtop25_drop_e0918606.csv`.
  - `analysis_outputs/submission_e230_q3_risktop21_drop_7d95c14a.csv`.
  - `analysis_outputs/submission_e230_q3_risktop13_drop_9704f7c9.csv`.
- stress dimensions:
  - E224 vs E154 graft anatomy.
  - actual E224 vs E95 movement anatomy.
  - public-free focus/subject/nearest support probabilities from E222/E224.
  - adverse-capacity reduction versus E224.
  - Q3 top-cell concentration and selected-cell count cap.
- key selected result:
  - `q3_swingtop25_drop`: expected focus `-0.000600044`, expected loss vs E224 `+0.000023308`, adverse reduction `0.000633168`, support gain `0.009873471`, Q3 top1/expected `0.490396`.
  - `q3_risktop21_drop`: expected focus `-0.000691244`, expected loss vs E224 `-0.000067892`, adverse reduction `0.000444730`, support gain `0.021076971`, Q3 top1/expected `0.469525`.

Stress implication after E230: the Q3 tail can be pruned without destroying the E224 body under public-free priors, but the prune rule is not OOF-learned. E230 should be a post-E224 conditional sibling, not the first public JEPA sensor.

E231 E224 Q3 OOF support-prune stress:

- script: `analysis_outputs/e231_e224_q3_oof_support_prune.py`.
- report: `analysis_outputs/e231_e224_q3_oof_support_prune_report.md`.
- selected files: none.
- stress dimensions:
  - Q3 support label = whether E224-like Q3 improves OOF loss versus stage2.
  - stratified, row-contiguous, subject-kfold, and subject-LOO support-model folds.
  - OOF prune-gate preservation of Q3 delta.
  - submission-side E222/E224 tail audit after rolling low-support Q3 cells back to E154.
- key results:
  - support-label rate `0.502222`.
  - full E224-like Q3 OOF delta `-0.004262113`.
  - best support-model AUC `0.588101` (`hgb_shallow`, subject5), with weaker row-contiguous and subject-LOO evidence.
  - best OOF gates can improve Q3 loss versus full E224, but no gate jointly passes OOF stability and public-free tail stress.

Stress implication after E231: E224's Q3 tail is not yet an invariant learned support object. The hand-prune diagnosis from E230 remains useful only after E224 feedback; it should not be upgraded into a learned submission lane.

E232 cross-target support-invariance stress:

- script: `analysis_outputs/e232_cross_target_support_invariance.py`.
- report: `analysis_outputs/e232_cross_target_support_invariance_report.md`.
- selected files: none.
- stress dimensions:
  - row-label and benefit overlap between E216 S2, E224-like Q3, and E224-like S4 support labels.
  - subject-level support-rate correlation.
  - within-target OOF support predictability under stratified and subject folds.
  - held-out target transfer where the target task is excluded from the source set.
  - test-side low-support overlap across targets.
- key results:
  - max row-label correlation `0.057278`; max benefit correlation `0.090611`.
  - subject support correlations are Q3/S2 `-0.442384`, Q3/S4 `0.128085`, and S2/S4 `-0.491326`.
  - within-target support is target-specific: best AUC Q3 `0.602244`, S2 `0.747495`, S4 `0.865816`.
  - best true cross-target transfer comes from movement shape (`AUC=0.745452`), while best latent-context transfer is lower (`0.707003`).
  - test low-support overlap is small: Q3/S2 top25 `1`, Q3/S4 top25 `2`, S2/S4 top25 `4`.

Stress implication after E232: reject a single shared S2/Q3/S4 row-support regularizer. The live support signal is target-specific plus a generic movement-shape calibration risk. Future JEPA stress should train separate S2/Q3/S4 support or energy heads and use movement-shape transfer only as a diagnostic.

E233 target-specific soft-energy stress:

- script: `analysis_outputs/e233_target_specific_soft_energy_heads.py`.
- report: `analysis_outputs/e233_target_specific_soft_energy_heads_report.md`.
- selected files: none.
- stress dimensions:
  - target-specific OOF support classifiers for E216 S2, E224 Q3, and E224 S4.
  - soft probability-to-amplitude policies instead of hard keep/drop gates.
  - stratified and subject-fold target LogLoss deltas versus both base and full movement.
  - Q3 test low-amplitude overlap with E230 public-free risk/swing/expected-positive rows.
- key results:
  - promoted soft policies: `0`.
  - best learned Q3 soft policy delta `-0.002548953` versus full Q3 delta `-0.004262113`.
  - best learned S2 soft policy delta `-0.002769599` versus full S2 delta `-0.004370425`.
  - best learned S4 soft policy delta `-0.002931629` versus full S4 delta `-0.003430136`.
  - Q3 low-amplitude top25 overlap with E230 risk-top21: `0` rows.

Stress implication after E233: softening the existing support classifiers does not fix the JEPA translation bottleneck. The support probabilities are diagnostic scores, not usable amplitude heads. The next target-specific JEPA experiment should change the training target/loss, not just the post-hoc gate shape.

E234 tail-contrastive JEPA target stress:

- script: `analysis_outputs/e234_tail_contrastive_jepa_target.py`.
- report: `analysis_outputs/e234_tail_contrastive_jepa_target_report.md`.
- selected files: none; diagnostic CSVs only.
- stress dimensions:
  - high-adverse `risk` and high-positive-vs-high-adverse `contrast` target representations.
  - E216 S2 and E224-like Q3/S4 target-specific movement tensors.
  - stratified and subject folds.
  - target LogLoss versus both base and full movement.
  - subject win-rate and dropped-row mean benefit.
  - Q3 test alignment against E230 public-free risk/swing/expected-positive rows.
- key results:
  - promoted tail-contrastive policies: `323`.
  - best S2 loss versus full movement: `-0.002653627`.
  - best Q3 loss versus full movement: `-0.000870181`.
  - best S4 loss versus full movement: `-0.000833194`.
  - Q3 best selected drop has weak public-tail alignment: E230 risk-top21 overlap `2` rows for the top25 contrast policy, while a Q3 risk p20 variant reaches only `5` rows.

Stress implication after E234: changing the JEPA target/loss revives local target-specific signal, unlike E233's soft support heads. This is a real representation clue, but not a public candidate by itself because Q3 alignment is weak and S2 must survive the stricter post-E216 materialization gate.

E235 S2 tail-contrastive materialization stress:

- script: `analysis_outputs/e235_s2_tail_contrastive_materialization.py`.
- report: `analysis_outputs/e235_s2_tail_contrastive_materialization_report.md`.
- selected files: none.
- stress dimensions:
  - promoted E234 S2 risk/contrast policies.
  - E216 S2 submission tensor on E95 anchor.
  - scales `0.35`, `0.50`, and `0.75`.
  - E221 submission-side tail-capacity gate: expected focus, adverse capacity versus observed E216 miss, support probability, and top-cell dominance.
- key results:
  - scanned policies: `240`.
  - submission gate pass: `0`.
  - joint gate pass: `0`.
  - materialized submission files: `0`.
  - best support remains below threshold (`0.497582` max support), and best expected rows still carry adverse capacity above the observed E216 miss.

Stress implication after E235: the OOF tail-contrastive S2 signal is not public-safe under current tensors. E216 S2 remains closed; future JEPA work should not use S2 as the next public lane without a different target definition and a stronger submission-side support proof.

E236 Q3/S4 tail-contrastive materialization stress:

- script: `analysis_outputs/e236_q3s4_tail_contrastive_materialization.py`.
- report: `analysis_outputs/e236_q3s4_tail_contrastive_materialization_report.md`.
- selected files: none.
- stress dimensions:
  - promoted E234 Q3/S4 high-impact tail policies.
  - E224 capped-Q3/S4 submission tensor relative to E154.
  - Q3-only, S4-only, and Q3+S4 learned-mask materializations.
  - E222/E230-style public-free expected focus, adverse capacity, support probability, Q3 top-cell concentration, and actual-vs-E95 duplicate checks.
- key results:
  - graft rows: `92`.
  - graft gate pass: `0`.
  - materialized submission files: `0`.
  - best Q3 adverse reduction: `0.000329753`, but support gain is `-0.004017252` and Q3 top1/expected rises to `3.054720`.
  - best S4 support gain: `0.006519636`, but expected focus weakens by `0.000166178` and Q3 tail risk is unchanged.

Stress implication after E236: E234's Q3/S4 tail labels are useful local diagnostics but not a submission-safe learned replacement for E230's hand-pruned Q3 tail. The Q3 learned masks select the wrong public-free support rows, while S4 learned masks remove too much healthy E224 body.

E237 cell-level decisive JEPA target stress:

- script: `analysis_outputs/e237_cell_decisive_jepa_target.py`.
- report: `analysis_outputs/e237_cell_decisive_jepa_target_report.md`.
- selected files: `7`.
- stress dimensions:
  - OOF decisive-cell labels over Q3/S4 cells, with S2/Q3/S4 `all3` source labels as a control.
  - latent-with-target, latent-without-target, and movement views.
  - shallow HGB and linear models under subject and row folds.
  - materialized E224-to-E154 rollback policies by Q3-only, S4-only, and joint drops.
  - graft-vs-E154 and actual-vs-E95 public-free audits.
  - Q3 top-cell concentration and E230 risk/swing overlap.
- key results:
  - OOF policy rows: `3744`; stress-promoted rows: `441`.
  - materialized scan rows: `240`.
  - selected rows/files: `7`.
  - top selected file: `submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`.
  - top selected stress: expected loss vs E224 `-0.000005612`, adverse reduction `0.000576400`, support gain `0.006450259`, actual-vs-E95 adverse reduction `0.000553281`, Q3 top1/expected `0.747139811`, E230 risk-top21 overlap `11`.

Stress implication after E237: the failed E236 target was too coarse. Cell-level decisive-label prediction recovers a learned Q3-only tail intervention that survives stricter public-free stress. This is now the leading learned-JEPA candidate if the next submission is meant to test a JEPA-derived Q3-tail translator.

E238 E237 public-feedback decoder stress:

- script: `analysis_outputs/e238_e237_public_feedback_decoder.py`.
- report: `analysis_outputs/e238_e237_public_feedback_decoder_report.md`.
- selected files: none; this is a pre-public routebook.
- stress dimensions:
  - fixed E237 top file versus E224/E230/E154/E95.
  - public score bands anchored to E95, E101, mixmin, and E216.
  - E237-vs-E224 contrast bands.
  - pairwise movement anatomy, target anatomy, and exact Q3 cell overlap.
- key results:
  - clean E237 public support requires `<=0.576276019`; branch loss starts above mixmin `0.576306641`; E216-like translator collapse starts above `0.576591330`.
  - E237-vs-E224 readable win requires delta `<= -0.000010`; `+/-0.000003` is treated as unresolved.
  - E237 changes exactly `25` Q3 cells versus E224, overlaps E230 swing25 by `13` and E230 risk21 by `11`, and touches no S4 cells in the prune.
  - E237 movement from E95 is still mostly Q3/S4: Q3 abs share `0.466410`, S4 `0.415839`.

Stress implication after E238: the E237 public score is now interpretable as a falsification test. A win supports learned Q3 decisive-cell structure; a tie or small loss calls for E224 contrast; a branch loss closes same-family top-k tuning; an E216-like loss means the cell translator collapsed.

E239 E237 cell motif atlas stress:

- script: `analysis_outputs/e239_e237_cell_motif_atlas.py`.
- report: `analysis_outputs/e239_e237_cell_motif_atlas_report.md`.
- selected files: none; this is a read-only motif/stress audit.
- stress dimensions:
  - E237 selected Q3 cells versus E224/E154/E95 movement magnitude.
  - exact overlap/disagreement with E230 swing/risk hand-prunes.
  - subject/date/test-edge/train-adjacency motifs.
  - E208/E215 latent residual and nearest-neighbor context.
  - permutation enrichment rather than fitted submission scoring.
- key results:
  - E237 overlaps E230 swing25 by `13/25` and risk21 by `11/21`.
  - E237 is only `0.520` top-25 amplitude but `0.960` top-50 amplitude, so it is amplitude-filtered but not pure top-k.
  - edge/date shortcuts weaken: near-test-edge-2 rate `0.120` vs population `0.240`; gap-adjacent-2 rate `0.240` vs population `0.344`.
  - latent residual energy is enriched: `e208_resid_self_abs_mean` lift `1.366`, `e208_nn_target_dist` lift `1.310`, `e208_resid_self_pc10` lift `6.734`.

Stress implication after E239: E237's local signal is not just a calendar edge or top-k amplitude artifact. It is best described as high-Q3-movement cells under high E208 residual/NN-distance energy. This strengthens the learned-cell motif as an interpretable hidden-world bet, but it does not create a new submission or justify tuning E237 siblings before public feedback.

E240 E237 residual-rule ablation stress:

- script: `analysis_outputs/e240_e237_residual_rule_ablation.py`.
- report: `analysis_outputs/e240_e237_residual_rule_ablation_report.md`.
- selected files: none; this is a diagnostic ablation and creates no submission.
- stress dimensions:
  - deterministic Q3 rollback rules from amplitude, E208 residual abs mean, E208 NN distance, E208 residual PC10, E215 residual, and top50-amplitude filters.
  - same graft-vs-E154 and actual-vs-E95 E237-like gate used for E237 interpretation.
  - overlap against E237, E230 swing25, and E230 risk21.
- key results:
  - all `9/9` non-control simple selectors pass the E237-like gate and E230 gate.
  - `simple_pc10_top25` is best by E237-like score: expected loss vs E224 `-0.000062119`, adverse reduction `0.000594489`, support gain `0.016747154`, actual adverse reduction `0.000573879`.
  - `simple_pc10_top25` overlaps E237 only `14/25`, so it is not merely copying E237, but it overlaps E230 swing25 by `18/25`.
  - E237 control remains valid but no longer uniquely strong under local stress.

Stress implication after E240: the current E237/E230 public-free stress is not sufficient to prove learned-selector uniqueness. It supports a broader Q3 residual-energy cell-tail world. A simple-rule submission is not justified because the rule is post-hoc and not train/OOF-validated, but future JEPA work should validate residual PC10-like target cells directly.

E241 residual PC10 OOF benefit validation stress:

- script: `analysis_outputs/e241_residual_pc10_oof_benefit_validation.py`.
- report: `analysis_outputs/e241_residual_pc10_oof_benefit_validation_report.md`.
- selected files: none; this is a train/OOF falsification of E240 simple residual rules.
- stress dimensions:
  - full-train top-k Q3 OOF benefit for E224-like Q3 movement.
  - random stratified, row-contiguous, and subject-LOO stress.
  - residual/amplitude/margin scores including E208 residual PC10, residual abs mean, NN target distance, E215/E208 combo, and negative-PC10 control.
  - test-context overlap against E237, E230 swing25, and E230 risk21.
- key results:
  - no full-train top-k score has negative selected-benefit delta.
  - best top-10% full-train score is `score_low_margin`, still adverse at `+0.000345376`.
  - `score_pc10` is adverse: full top-10% `+0.001867628`, split-stress top-10% `+0.002633171`, win rate `0.30`.
  - best split-stress top-10% score is `score_nn_dist`, but it remains non-negative at `+0.000270542` with win rate `0.50`.
  - test `score_pc10` top25 still overlaps E237 `14/25` and E230 swing25 `18/25`.

Stress implication after E241: the residual-energy motif exists in the test Q3 cell atlas, but it is not an OOF-valid harmful-row selector under the current train label construction. E240 simple residual rules are closed as submissions. E237 remains a learned-cell public sensor, but not because scalar PC10 top-k is validated.

E242 E237 OOF-to-test transfer audit:

- script: `analysis_outputs/e242_e237_oof_to_test_transfer_audit.py`.
- report: `analysis_outputs/e242_e237_oof_to_test_transfer_report.md`.
- selected files: none; this audits E237 ranking and transfer logic.
- stress dimensions:
  - `120` graft-side E237 materialization rows.
  - average OOF policy gain versus E237 gate and E237 score.
  - OOF tail-AUC versus E237 gate and E237 score.
  - public-free test materialization metrics: expected/actual gain, adverse reduction, support gain, Q3 top-cell safety.
  - conflict examples between OOF-strong rows and test-gate-strong rows.
- key results:
  - E237 gate pass rows: `7/120`.
  - top E237 file rank by OOF gain: `71/120`; OOF gain gate AUC `0.426043`.
  - top E237 file rank by OOF tail-AUC: `1/120`; OOF tail-AUC gate AUC `0.958913`.
  - top E237 file ranks `1/120` by support gain and Q3 top-cell safety, and `3/120` by expected/actual gain versus E224.
  - OOF gain versus E237 score Spearman is only `0.108953`.

Stress implication after E242: E237 is not an average-OOF-gain translator. Its valid local claim is narrower: high-impact Q3 risk-tail discrimination transfers to the public-free gate, while mean OOF loss rank does not. Future E237 siblings should not be selected by OOF delta alone.

E243 next public-slot governance:

- script: `analysis_outputs/e243_next_public_slot_after_e242.py`.
- report: `analysis_outputs/e243_next_public_slot_after_e242_report.md`.
- selected files: none; this is a decision protocol over existing candidates.
- stress dimensions:
  - E237-vs-E224: learned Q3 decisive-cell tail versus clean capped-Q3/S4 body.
  - E237-vs-E230: learned cell-tail target versus hand Q3 prune.
  - E237-vs-simple-PC10: OOF-trained tail target versus post-hoc residual-energy motif.
  - E224-vs-E166 and E224-vs-E154: public-question separability and blend risk.
- key results:
  - E237 is ranked first only for an improvement-biased JEPA-as-solution public slot.
  - E224 remains first for clean JEPA body ablation.
  - E166 remains first for a non-JEPA independent broad-world slot.
  - E154 remains conservative and conditional.

Stress implication after E243: the live JEPA branch has two distinct experimental roles. E237 is the closest deployable JEPA-tail attempt, but it does not universally supersede E224 because it pre-prunes Q3 and would obscure the clean body question. Public-slot choice must be tied to the question, not to one scalar "best candidate" label.

E244 E237 pre-submission integrity audit:

- script: `analysis_outputs/e244_e237_presubmission_audit.py`.
- report: `analysis_outputs/e244_e237_presubmission_audit_report.md`.
- selected file: `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`.
- stress dimensions:
  - exact schema and key-order match against `data/ch2026_submission_sample.csv`.
  - duplicate key, missing value, finite probability, and `[0,1]` probability checks.
  - E237-vs-E224 targetwise movement audit.
  - E237-vs-E95 movement context check.
  - checksum lock for the public candidate.
- key results:
  - status `READY`.
  - SHA256 `6521b0e26622713eb9391c804af03b20eba84b924c4157bcc4ef50941b053915`.
  - exact `250 x 10` sample schema and sample key order.
  - E237 changes exactly `25` cells versus E224, all on Q3.
  - no material Q1/Q2/S1/S2/S3/S4 movement versus E224.

Stress implication after E244: the E237 public score, if submitted, is attributable to the intended learned Q3 decisive-cell rollback rather than artifact drift. E244 adds no new local-score evidence, but it closes submission-file ambiguity.

E245 feature-NN1 JEPA compatibility audit:

- script: `analysis_outputs/e245_feature_nn1_jepa_compat_audit.py`.
- report: `analysis_outputs/e245_feature_nn1_jepa_compat_report.md`.
- selected files: none; this is a representation-health audit for E237.
- stress dimensions:
  - E207 true-JEPA pair regime: `broad_stage2_pca64 / feature_nn1_all`.
  - submission-side feature-nearest-neighbor Q3 logit roughness.
  - actual E237 25-row rollback from E224 to E154.
  - random rollback nulls from all rows and top50 Q3-amplitude rows.
  - candidate movement geometry for E95/E101/E154/E166/E176/E216/E224/E237.
- key results:
  - verdict `supportive`, not decisive.
  - E237 reduces global Q3 NN-pair roughness by `-0.000802649`.
  - E237 reduces affected-pair roughness by `-0.006472972` across `31` affected directed pairs.
  - all-row null percentile is `0.1754` global and `0.1080` affected.
  - top50-amplitude null percentile is `0.3132` global and `0.2896` affected.
  - E237 is not globally smoother than E224 by movement pair ratio (`1.213392` vs `1.124777`), so the signal is local to the Q3 rollback.

Stress implication after E245: E237 is compatible with the only LeJEPA-identifiable feature-neighbor regime, but the evidence is not strong enough to create a new candidate or override public feedback. This strengthens E237 as the next JEPA-as-solution sensor but does not certify the branch.

## Update After E247

E246/E247 adds a sharper stress result.

- E246 tests `16` feature-NN1 smoothing selectors. All `16/16` pass the E237-like gate.
- Best selector `nn_smooth_sum_top34` is non-clone: E237 overlap `13`, E230 swing25 overlap `10`, amp top25 overlap `10`.
- It passes the E237-like graft plus actual-vs-E95 gate with:
  - expected loss vs E224 `-0.000066519`.
  - adverse reduction vs E224 `0.000632592`.
  - support gain vs E224 `0.005788959`.
  - actual adverse reduction vs E224 `0.000596176`.
  - Q3 top1/expected `0.549713494`.
- It fails the older E230 gate only because it prunes `34` Q3 cells, above E230's `<=25` cell-count guard.
- E247 artifact check passes exact schema/key/probability integrity and changes only Q3 versus E224.

Stress implication after E247: feature-NN1 smoothing is now a live selector, not only a diagnostic. The main unresolved risk is not local stress but invariance: the top selector is public-free and test-geometry-based, but not OOF-trained. Public feedback should decide whether this is a true JEPA manifold law or a local calibration-smoothing shortcut.

## Update After E248

E248 directly tests that unresolved invariance risk and finds it adverse.

- E247 train-only PCA smooth-sum analogue at the `34/250` selection rate:
  - full-train rollback delta `+0.002829987`.
  - split-stress mean `+0.002638697`.
  - split-stress win rate `0.30`.
- E247 all-PCA smooth-sum analogue:
  - full-train rollback delta `+0.002922728`.
  - split-stress mean `+0.002950123`.
  - split-stress win rate `0.15`.
- Best full-train score at that fraction is the reversed smoothness direction, but it is still non-negative: `+0.000489209`.

Stress implication after E248: E247 passes test-side materialization stress but fails OOF invariance. It should not be ranked above E237 for likely score. Its role is a public sensor for whether hidden public labels prefer feature-neighbor smoothing despite OOF evidence saying the rule is adverse.

## Update After E250

E249/E250 splits feature-NN1 into two different stress outcomes.

- Direct feature-NN1 smoothing remains OOF-adverse from E248.
- Feature-NN1 as context inside the E237 decisive-cell target is partially stress-positive:
  - E249 scans `2496` OOF rows and promotes `276`.
  - Paired `latent_no_targetid/hgb_shallow` rows improve tail-AUC at rate `0.625000`, but median loss delta is adverse at `+0.000053880`.
  - E250 materializes `120` rows and finds `4` E237-gate passes.
  - best selected E250 top21 row has expected loss vs E224 `-0.000000845`, adverse reduction `0.000524271`, support gain `0.005790882`, actual adverse reduction `0.000502064`, and Q3 top1/abs-expected `0.660128`.
- The strongest E249 OOF-loss row is rejected by materialization: broad `drop_q3_top50` keeps high OOF gain but fails support/top-cell stress.

Stress implication after E250: feature-NN1 is not a submit-safe scalar criterion. It can survive as a context feature for high-impact Q3 decisive-cell prediction, but the gate must remain tail-AUC/support/top-cell based. E237 remains the better score-biased candidate; E250 top21 is the sharper feature-NN1-context sensor.

## Update After E252

E251/E252 adds a cross-candidate cell-set stress.

- E237 and E250 overlap on `15` Q3 cells, but are not clones:
  - E237-only `10`.
  - E250-only `6`.
  - union `31`.
- Materialization gate pass count is `5/7` cell-set variants.
- Best materialization anatomy is the union:
  - expected loss vs E224 `-0.000035272`.
  - adverse reduction `0.000721005`.
  - support gain `0.010353010`.
  - actual adverse reduction `0.000688037`.
  - Q3 top1/abs-expected `0.506203451`.
  - no-OOF score `0.077866812`.
- Negative controls are informative:
  - shared intersection fails with expected loss `+0.000028815` and Q3 top1/abs-expected `1.054975`.
  - E250-only fails because adverse reduction is just below the gate.

Stress implication after E252: the current strongest materialization object is E237/E250 complementarity, not simple consensus. However, E252 is weaker than E237 on validation provenance because the union has no direct OOF policy identity. Rank it as a public sensor, not a certified score candidate.

## Update After E253

E253 adds the missing train-OOF analogue for E252.

- E252-style union is OOF stress-promoted, but weak:
  - union loss_vs_full `-0.000080010`.
  - E237 parent `-0.000271441`.
  - E250 parent `-0.000185023`.
  - union minus E237 `+0.000191431`.
- OOF shared intersection is strongest:
  - loss_vs_full `-0.000376454`.
  - dropped mean benefit `-0.028234084`.
  - stress_promote `True`.
- Parent-specific cells are OOF-adverse:
  - E237-only `+0.000105013`.
  - E250-only `+0.000191431`.
  - symmetric difference `+0.000296444`.
- This directly conflicts with E251 materialization, where shared intersection failed and union was best.

Stress implication after E253: E252 is not OOF-certified. The stronger finding is validation mismatch: OOF consensus cells and public-free materialization support cells disagree. This strengthens the diagnosis that frontier movement is limited by target-specific public-tail translation, not by absence of JEPA latent signal.

## Update After E254

E254 localizes the E253 mismatch.

- Train OOF shared cells are the strongest group: benefit mean `-0.028234084`, while the union is only `-0.002117914`.
- Test hard-tail anatomy says the shared set is not deployable by itself: expected focus is favorable at `-0.000028815`, but Q3 top1/abs is `3.412733926`.
- Test union has the opposite E224-vs-E154 cell risk shape: expected focus `+0.000035272`, adverse sum `0.000721005`, and support-delta sum `-0.000906285`.
- The selected train/test groups are not geometrically stationary:
  - `prob_gap` shifts by `-1.517107` std for shared, `-1.544628` for E237-only, and `-1.804342` for E250-only.
  - `logit_step` shifts by `-1.468916` std for shared and `-1.665033` for E250-only.
  - feature-NN1 smooth-gain flips sign for shared and E250-only groups.

Stress implication after E254: the next target cannot be "consensus cells" or "union cells." It must predict a contrastive representation: OOF-harmful consensus versus test hard-tail-adverse parent-specific cells. Until that exists, E237 remains the best expected-score JEPA file and E252 remains only a public sensor.

## Update After E255/E256

E247 public feedback changes the stress hierarchy.

- E247 public LB is `0.5761589494`, a new best.
- It beats E95 by `0.0001323804` and mixmin by `0.0001476911`.
- This is `8.646x` the E95-over-mixmin edge, so the result is not a frontier-scale tie.
- E248's OOF rejection is now interpreted as validation mismatch, not as a valid veto: the train OOF smoothing analogue is adverse, but public rewards the test-side feature-NN1 Q3 smoothing geometry.
- E255 ranks `top50_amp_then_smooth25` as the highest-information same-family follow-up.
- E256 materializes that file as `analysis_outputs/submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv`, changing `25` Q3 cells only.

Stress implication after E256: E247 is the current public-positive JEPA mechanism. The next stress is not "does smoothing work?" but "which part of smoothing works?" E256 tests broad top34 smoothness versus high-amplitude constrained smoothness.

## Update After E257

E257 decomposes the E247/E256 stress question into exact cell groups.

- Common E247/E256 cells: `21`.
- E247-only cells: `13`, low amplitude (`0.039125051` mean) but broad smoothness mass (`1.002858981`).
- E256-only cells: `4`, high amplitude (`0.110316918` mean), low smoothness mass (`0.049289874`), and E230 swing overlap `4/4`.
- E247-all has more smoothness mass and lower top1/abs expected.
- E256-all has stronger affected-pair roughness reduction (`-0.070332985` vs E247 `-0.057353058`) and higher support probability (`0.448321681` vs `0.433489917`).

Stress implication after E257: E256 is a clean public sensor, not a sibling sweep. It asks whether public prefers broad low-amplitude feature-neighbor smoothing or a smaller high-amplitude/E230-swing-aligned subset. A win promotes amplitude-constrained smoothing; a close loss promotes E247-only broad smoothness; a hard loss points to exact E247 top34 or E224-body interaction.

## Update After E258

E258 adds attribution stress for the E247 win.

- E224 body is large and low-support: `534` cells, expected focus `-0.000653189`, support probability `0.465789507`.
- E247 rollback is small but support-positive: `34` Q3 cells, expected focus `-0.000066519`, support probability `0.566510083`.
- The rollback is not an independent same-sign feature. It is a near-complete trim of the E224 body on selected cells:
  - selected cosine `-0.992683110`.
  - opposite-sign share `1.000000`.
  - rollback abs over selected body abs `0.984581403`.
- E247 total preserves the body while reducing Q3 hard-tail concentration: Q3 top1/abs expected changes from E224 body `0.863839051` to E247 total `0.545240602`.

Stress implication after E258: the next public decision splits into two valid routes. E256 tests whether the Q3 tail correction can be improved without leaving the E247 mechanism. E224 tests whether the body alone was already enough. A blend would blur the only clean attribution axes left.

## Update After E259

E259 turns the E247/E256/E224 stress split into a pre-registered observation routebook.

- Script: `analysis_outputs/e259_post_e247_observation_routebook.py`.
- Report: `analysis_outputs/e259_post_e247_observation_routebook_report.md`.
- E256 is decoded as broad-vs-amplitude smoothing:
  - clean win `<=0.576155949`.
  - tie `0.576155949..0.576161949`.
  - same-family loss starts above `0.576188949`.
- E224 is decoded as body attribution:
  - body tie/micro-win `<=0.576161949`.
  - rollback-helped up to E95 `0.576291330`.
  - body-only loss beyond mixmin `0.576306641`.

Stress implication after E259: public feedback must be read through the declared routebook. A same-family blend before E256/E224 feedback is now explicitly blocked because it would remove attribution resolution.

## Update After E260

E260 adds a hard-label sensitivity layer to the E259 routebook.

- Pair summary: E256-vs-E247 expected focus `+0.000019101`; E224-vs-E247 expected focus `+0.000066519`.
- E256 is lower expected downside than E224, but its top-cell fragility is higher relative to the tiny expected gap: top1/abs expected `4.431072193`.
- E224 is less ratio-fragile but more broadly adverse because removing the common rollback core contributes `+0.000068286`.
- E256's E247-only broad-smoothness deletion is not the adverse part under current priors (`-0.000001767`). Its adverse part is the E256-only high-amplitude cell insertion (`+0.000020868`).

Stress implication after E260: E256 remains the right next score-plus-information stress, but the pre-registered read is narrower. A bad E256 score means the high-amplitude added cells failed first. It does not automatically mean E247-only broad smoothing was the causal public signal.

## Update After E261

E256 public returned `0.5762805676`.

- E259 outcome: `same_family_loss`.
- Public delta versus E247: `+0.0001216182`.
- Public delta versus E95: `-0.0000107622`.
- E260 expected delta versus E247: `+0.000019101`.
- Actual over expected: `+0.000102517`.
- Minimum top swing cells needed to explain actual delta: `2`.

Stress implication after E261: the E256 stress did its job and rejects high-amplitude constrained smoothing as an improvement path. It does not reject feature-NN1 smoothing as a mechanism because E256 remains better than E95. The stress stack should now block E247-family scalar sweeps and route either to E224 attribution or to a non-collinear branch.

## Update After E217

E217 stress-tests a closer teacher-student tabular JEPA.

- script: `analysis_outputs/e217_teacher_student_tabular_jepa_probe.py`.
- report: `analysis_outputs/e217_teacher_student_tabular_jepa_report.md`.
- downstream scan: `analysis_outputs/e217_teacher_student_tabular_jepa_downstream_scan_summary.csv`.
- geometry stress: `analysis_outputs/e217_teacher_student_tabular_jepa_downstream_geometry_summary.csv`.

Stress dimensions:

- EMA teacher-student validation against mean-teacher and shuffled-teacher baselines.
- random mask specs over feature families.
- same-subject row-neighborhood context.
- downstream OOF correction over stage2 probabilities.
- repeated subject-half guardrail.
- row-order/geometry folds.
- latent covariance/rank diagnostics.

Result:

- Training passes the nontriviality check: val loss `0.001853..0.001914`, mean-teacher loss `0.026019..0.026827`.
- Best local S2 row: `e217_teacher_pc07`, delta `-0.002853`, mean subject-half delta `-0.001629`, win rate `0.757692`.
- That same S2 row fails geometry with delta `+0.000410` and win rate `0.375`.
- Q3 residual rows have small negative geometry in some modes but fail win-rate/local thresholds.
- E217 materialization gate pass count is `0`.

Stress implication: teacher-student JEPA learned a latent but did not create a geometry-stable submission source. Keep it as an energy/diagnostic branch; do not create an E217 submission before a separate target-specific materialization test.

## Update After E262/E263

E262/E263 open a new validation branch: human/social lifestyle state as JEPA context for public-tail prediction.

- E262 generated `790` raw lifestyle/context features over `700` rows.
- E262's strongest cheap signals are not enough for submission because HR/pedometer coverage also shows train/test shift.
- E263 links E262 context to E247/E256 Q3 tail cells, but the critical E256-only set has only `4` rows.

Required stress before any submission:

- subject/date-block OOF, not random row CV.
- within-subject lift check for lifestyle features.
- train/test adversarial check to reject pure domain signatures.
- OOF analogue of Q3 smoothing-validity/tail-risk, not test-only E247/E256 cell labels.
- LeJEPA geometry check: no subject collapse, no high anisotropy, no public-anchor-only shortcut.

Current status: diagnostic only. E263 is useful because it defines the next target representation, not because it certifies a gate.

## Update After E264/E265

E264 performed the required OOF analogue for the human/social branch.

- `human_late` survives both `subject5` and `dateblock5` stress.
- best human-only OOF loss_vs_full is `-0.001689622`.
- dateblock LR best is `-0.000690449`, so this is not only a subject-heldout HGB artifact.
- latent+human views add some strict rows, but median improvements are mixed.

E265 adds the negative control.

- random cell noise strict gate rate is `0.290909`.
- best random loss_vs_full is `-0.000723735`.
- human_late still beats random clearly, but the strict gate itself is too permissive.

Stress implication: lifestyle state is a real local representation, but broad OOF rollback policy is not a submission gate. The next validation layer must include top-cell ranking, overlap with public-free risk cells, and E224/E154 materialization-side stress.

## Update After E266/E267

E266 adds the missing materialization-side stress for the human/social branch.

- sharp E264 pool rows: `80`.
- materialized rows: `160`.
- E237 gate passes / selected files: `22`.
- best expected_loss_vs_e224: `-0.000027985`.
- best adverse_reduction_vs_e224: `0.000589659`.
- best support_gain_vs_e224: `0.005063832`.

Stress read:

- The branch passes the harder "can this become a tensor?" check.
- However, the highest E237-score file is broad (`75` dropped cells) and expected-positive (`+0.000010956`), so the E265 broad-gate warning still matters.
- E267 re-ranks by a stricter survival score and chooses `submission_e267_humansocial_tail_balanced_2936100f.csv`.

E267 stress summary:

- expected_loss_vs_e224 `-0.000004014`.
- adverse_reduction_vs_e224 `0.000418519`.
- support_gain_vs_e224 `0.004541355`.
- actual_expected_delta_vs_e224 `-0.000004014`.
- actual_adverse_reduction_vs_e224 `0.000383531`.
- actual_support_gain_vs_e224 `0.003984398`.
- movement versus E247: `60` cells, mostly Q3 (`51`) and S4 (`9`).

Stress implication: this is submission-eligible as a public sensor, not as a certified replacement for E247. Its result will decide whether human/social hidden state is a score-relevant Q3/S4 tail law or only a local/E224-family diagnostic.
## E272 Public-Free Promotion Gate

Question: can the social/cash-flow candidates be checked locally instead of spending public LB?

Method: `analysis_outputs/e272_public_free_candidate_audit.py`.

- Current anchor: `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`.
- Known public observations used as old calibration sensors: `17`.
- Local selector stress: pairwise known-LB order models with LOO, L2O, and current-anchor-held-out scenarios.
- Promotion bar: p90 predicted delta vs E247 < `-0.00005`, beats-current scenario rate >= `0.75`, and incremental bad-axis change vs E247 <= `0.015`.

Result:

- strict promote candidates: `0`.
- E271 cash-flow preferred: mean `-0.000005422`, p10/p90 `-0.000007555 / -0.000001953`, decision `too_small_to_submit`.
- E269 social preferred: mean `-0.000011178`, p10/p90 `-0.000015892 / -0.000003311`, decision `too_small_to_submit`.
- E269 anti-E256 top-half: mean `-0.000017223`, p90 `-0.000008141`, locally best but still sub-threshold.
- E256 known fail is correctly scored positive/adverse versus E247: mean `+0.000051379`.
- E267 known fail is also positive/adverse: mean `+0.000030913`.

Decision:

- E269/E271 are blocked as score submissions.
- They remain useful as evidence that the boundary has social/cash-flow structure, but the materialized moves are too small relative to local selector uncertainty.
- Next validation work should demand either larger safe movement or better hidden-state selector reliability before producing another CSV.

## E273 Human Diary State JEPA Audit

Question: can a broad human/social/cash-flow diary state be used locally instead of spending public LB?

Method: `analysis_outputs/e273_human_diary_state_jepa_audit.py`.

- Input features: E262 day-level lifelog, E268 social stories, E270 cash-flow stories.
- Hidden views: eight family PC blocks plus JEPA-style residual/prediction energy for held-out family prediction under subject and dateblock grouping.
- Stress: calendar/subject baseline vs baseline+diary-state features under `subject5` and `dateblock5`.

Result:

- strict submit evidence: none.
- blocked CV deltas are all adverse:
  - dateblock mean delta `+0.047561770`.
  - subject mean delta `+0.149546366`.
  - best target/split is Q3 dateblock at `+0.014363799`, still worse than baseline.
- latent is not empty:
  - sensor dateblock OOF R2 `0.976587`;
  - physiology dateblock OOF R2 `0.891374`;
  - mobility dateblock OOF R2 `0.746016`;
  - social dateblock OOF R2 `0.642126`.
- boundary diagnostics are strong:
  - `jepa_prednorm_subject_social_comm` E247-vs-E256 d `-1.332902`;
  - `diary_state_pc6` d `-1.239802`;
  - `jepa_resid_dateblock_cognitive_money` d `1.199200`.

Decision:

- Do not submit a broad diary-state or broad social latent file.
- Treat E273 as a LeJEPA failure mode: representation is real but not invariant enough for direct probability movement.
- Surviving local work should be target-specific and energy-gated, especially Q3/Q1/S3 mobility-context, Q1/Q3 bedtime-phone residual, and S1/E247-boundary cognitive-money residual.

## E274/E275 Target-Specific Diary Energy Stress

Question: after rejecting broad diary-state modeling, can target-specific diary energy pass local and public-free stress?

Methods:

- E274: `analysis_outputs/e274_target_specific_diary_energy_audit.py`.
- E275: `analysis_outputs/e275_q_sleep_diary_energy_amplitude_audit.py`.

Local axis stress:

- E274 scanned `581` target-feature axes.
- `44` action-gate axes survived subject/dateblock single-feature stress.
- The strongest axes are Q3/Q-side:
  - `jepa_prednorm_dateblock_mobility_context` Q3: dateblock delta `-0.013697360`, subject delta `-0.035301799`.
  - `jepa_prednorm_subject_mobility_context` Q3: dateblock `-0.012267053`, subject `-0.036501166`.
  - `jepa_resid_subject_bedtime_phone` Q3: dateblock `-0.018941832`, subject `-0.014521025`.
  - `jepa_prednorm_subject_cognitive_money` Q3: dateblock `-0.015051731`, subject `-0.015188610`.

Candidate stress:

- E274 q-sleep top12 candidate was near-promotion: mean `-0.000098347`, p90 `-0.000048780`, beats-current `0.970588`.
- E275 amplitude ladder gives `4` adjacent strict rows from m1.15 through m1.60.
- E275 m1.60: mean/p90 `-0.000190473 / -0.000084726`, beats-current `0.970588`, incremental bad-axis `-0.004007782`.
- Movement remains Q-only: Q1 `24`, Q2 `47`, Q3 `114`; S1-S4 untouched.

Decision:

- `submission_e275_q_sleep_amp_m160_86528b2f.csv` passes the current public-free promotion rule and the E275 amplitude robustness rule.
- Risk caveat: selected E272-style selector model count is `1`, so this is not a guaranteed LB improvement. It is the best locally certified human/social diary candidate so far.

## E276 Matched-Placebo Stress For E275

Question: does E275 pass because it preserves human lifestyle row alignment, or because the selector likes any Q-side movement with the same magnitude?

Method: `analysis_outputs/e276_q_sleep_story_ablation_placebo_audit.py`.

- Rebuilt semantic variants: family-only, leave-one-family-out, JEPA-only, non-JEPA-only, Q3-only, Q1/Q2-only.
- Built matched nulls from the real E275 logit delta:
  - row shuffle;
  - subject-within-target shuffle;
  - dateblock-within-target shuffle.
- Added inverse control.

Result:

- primary E275 remains strict-promoted by old E272 gate: p90 `-0.000084726`.
- shuffled placebo strict promotes: `13 / 15`.
- dateblock shuffled placebos: `5 / 5` strict, best p90 `-0.000132538`.
- subject shuffled placebos: `4 / 5` strict, best p90 `-0.000123510`.
- row shuffled placebos: `4 / 5` strict, best p90 `-0.000091288`.
- inverse control does not promote: p90 `+0.000207722`.

Decision:

- E275 fails placebo-resistant validation. It should be held, not submitted.
- The old E272 gate is useful for detecting target/movement-family direction, but insufficient for row-level lifestyle-state certification.
- New promotion rule: a candidate must beat matched row/subject/dateblock shuffle nulls. Passing E272 alone is no longer enough.

Surviving signal:

- `only_mobility_context_m160` strict-promotes with p90 `-0.000095305`.
- `jepa_only_m160` strict-promotes with p90 `-0.000093390`.
- `nonjepa_only_m160` fails with p90 `+0.000183796`.

This says JEPA/mobility Q3 signal is still alive, but the current row placement is not proven.

## E277 Placebo-Resistant Q-Sleep Gate

Question: can any q-sleep diary-energy candidate beat its own matched shuffle null distribution?

Method: `analysis_outputs/e277_placebo_resistant_qsleep_gate.py`.

- Candidate set: `21` semantic/control E275/E276 variants.
- Nulls: `441` matched shuffle files.
- Null modes: row, subject, dateblock.
- Promotion rule:
  - old strict gate must pass;
  - p90 dominance over all nulls >= `0.80`;
  - mean dominance over all nulls >= `0.70`;
  - worst per-mode p90 dominance >= `0.60`;
  - null strict-promote rate <= `0.20`;
  - inverse controls cannot promote.

Result:

- old strict-promote candidates: `10`.
- E277 placebo-resistant promotes: `0`.
- all old strict candidates are blocked by placebo-promote rate.
- E275 primary: p90 `-0.000084726`, null strict rate `0.952381`, p90 dominance `0.571429`.
- `jepa_only_m160`: p90 `-0.000093390`, null strict rate `0.904762`, p90 dominance `0.761905`.
- `no_media_game_m160`: p90 `-0.000129314`, null strict rate `0.904762`, p90 dominance `0.666667`.

Decision:

- Passing E272/E275 is no longer a valid submission certificate.
- No q-sleep diary file is submission-ready.
- The next validation target is row-alignment: real JEPA/mobility/Q3 rows must separate from their matched shuffle nulls before any public LB use.

## E278 Train Row-Alignment Null Audit

Question: is the q-sleep row-alignment signal absent, or does it exist on train but fail to transfer to test/public-free selector geometry?

Method: `analysis_outputs/e278_train_row_alignment_null_audit.py`.

- Baselines: OOF calendar/subject logistic models for Q1/Q2/Q3.
- Splits: subject-group OOF and dateblock-group OOF.
- Policies: the same E275/E276 q-sleep semantic variants.
- Nulls: `200` matched row/subject/dateblock shuffles per candidate/split/mode.
- Metric: mean Q-target logloss delta versus OOF baseline.

Result:

- candidate/split rows: `40`.
- train-align gate rows: `27`.
- candidates passing both subject and dateblock gates: `13`.
- strongest broad policy:
  - `full_qsleep` subject/dateblock deltas `-0.001998955 / -0.001362687`.
- strongest clean target policy:
  - `q3_only` subject/dateblock deltas `-0.001363003 / -0.000879044`.
- JEPA policy:
  - `jepa_only` subject/dateblock deltas `-0.001263774 / -0.000802362`.
- single-family row alignment:
  - `only_bedtime_phone` passes both gates with small but highly null-dominant Q3 deltas.
  - `only_mobility_context` passes both gates.
- inverse control is adverse: subject/dateblock deltas `+0.001682720 / +0.001176547`.

Decision:

- Row alignment exists on labeled train data.
- E277's failure is not evidence of no signal. It is evidence of train-to-test/public selector transfer failure.
- Future validation must require both:
  - train row-alignment null dominance, and
  - test/public-free matched-placebo resistance.

## E279 Public-Free Submission Governor

Question: can we stop using public LB as the candidate filter?

Method: `analysis_outputs/e279_public_free_submission_governor.py`.

- Candidate pool: `66` active E247+ files and known public anchors.
- Nulls: `1365` matched row/subject/dateblock shuffle files.
- Local score: E272 current-anchor selector.
- Extra gates:
  - actual movement must beat its own matched nulls;
  - null strict-promote rate must be `<= 0.10`;
  - q-sleep candidates must have E278 train row-alignment support;
  - known-public files worse than E247 are blocked.

Result:

- old strict-promote candidates: `13`.
- matched-placebo gate passes: `0`.
- final public-free submission-ready candidates: `0`.
- strongest old strict rows are all blocked:
  - `submission_e276_no_media_game_m160_72fc6fa6.csv`: p90 `-0.000129314`, null strict `0.952381`;
  - `submission_e276_jepa_only_m160_75d0e9cf.csv`: p90 `-0.000093390`, null strict `0.857143`;
  - `submission_e275_q_sleep_amp_m160_86528b2f.csv`: p90 `-0.000084726`, null strict `0.952381`.

Decision:

- E279 is now the default pre-public gate for q-sleep/social-style candidate files.
- A candidate may be interesting as a hypothesis sensor, but it should not be recommended as score-seeking submission unless `public_free_submission_ready=True`.

## E280 Story Transfer Atlas

Question: can human/social and payday stories be ranked without using more public LB?

Method: `analysis_outputs/e280_story_transfer_alignment_atlas.py`.

- Inputs: E268/E270 story verdicts/features, E273 JEPA family diagnostics, E275 q-sleep row overlap, E278 train row-alignment support, E279 public-free governor context.
- Stress dimensions: label lift, blocked CV delta, train/test story-score z-gap, E278 family support, E273 context-to-family R2, and E275 q-sleep selected-row alignment.

Result:

- stories audited: `86`.
- alive for story-state gate: `3`.
- alive but needs transfer test: `23`.
- blocked transfer gap: `6`.
- public-anchor diagnostic only: `6`.
- top rows: `commute_workday` `0.791906`, `bright_light_late` `0.781993`, `single_app_monotony` `0.716179`, `app_entropy_scattered_day` `0.649240`.

Decision:

- E280 is a ranking/triage layer, not a submission validator.
- Public-anchor alignment is not enough. Stories with high public alignment but weak local CV are diagnostic only.

## E281 Story-State JEPA Row Selector Stress

Question: can a social story become a target-free JEPA state whose row placement beats matched nulls?

Method: `analysis_outputs/e281_story_state_jepa_row_selector_audit.py`.

- Top E280 stories tested: `6`.
- Hidden target: subject-normalized story score.
- Context: other numeric diary-state columns, excluding the mapped family and story column.
- Splits: subject5 and dateblock5.
- Downstream stress: predicted story state added to calendar/subject label baseline for all 7 targets.
- Nulls: `25` row, `25` subject, and `25` dateblock shuffles per story/split.

Result:

- story/split rows: `12`.
- JEPA story gate rows: `3`.
- both-split gate stories: `1`.
- `app_entropy_scattered_day` passes both:
  - subject5: state R2 `0.419010`, mean delta `-0.001949852`, dominance `1.000000`.
  - dateblock5: state R2 `0.728347`, mean delta `-0.000108720`, dominance `0.920000`.
- `single_app_monotony` passes subject5 only; dateblock mean delta is `+0.000025`.
- `commute_workday`, `bright_light_late`, `vehicle_noise_day`, and `heart_stress_late` fail as overall row selectors despite some target-specific wins.

Decision:

- `app_entropy_scattered_day` is the current strongest public-free human/social JEPA state.
- It is not submission-ready until materialized and passed through an E279-style matched-placebo governor.

## E282 App-Entropy Materialization Governor

Question: can the strongest E281 story-state become an actual E247-relative submission tensor without public LB?

Method: `analysis_outputs/e282_appentropy_story_materializer.py`.

- Story state: predict `app_entropy_scattered_day_subj_z` from all other numeric context families, excluding the routine-calendar/story columns.
- Materialization: small logit edits on E247 for Q3, Q2/Q3, and Q2/Q3/S2; Q3 linear amplitudes were swept around the old-selector threshold.
- Nulls: `726` matched row/subject/dateblock shuffles preserving each candidate's target-wise logit-delta distribution.
- Local selector: E272 current-anchor pairwise selector plus E279-style matched-placebo gates.

Result:

- candidates audited: `22`.
- matched null files: `726`.
- old strict-promote candidates: `6`.
- matched-placebo gate passes: `0`.
- final `public_free_submission_ready=True`: `0`.
- Q3-only linear is the only viable shape, but:
  - amp `0.022` is too small: p90 `-0.000048005`;
  - amp `0.023` barely crosses old strict but null strict rate is `0.121212`;
  - amp `0.030` looks strong by old selector but null strict rate is `0.939394`.

Decision:

- Do not submit any E282 app-entropy file.
- The hidden story-state is locally real, but the current probability edit is not row-placement-certified.
- Public LB is preserved. This is exactly the intended use of the local governor: block a plausible story when it becomes indistinguishable from matched placebo movement at submit-scale.

## E283 App-Entropy Q3 Smoothing Context Governor

Question: can app-entropy decide which E247-style Q3 feature-neighbor smoothing cells should be trusted?

Method: `analysis_outputs/e283_appentropy_q3_smooth_context_audit.py`.

- Inputs: E246 feature-NN1 Q3 smoothing selector rows, E247/E256 selected cell sets, and E282 app-entropy story-state scores.
- Candidate family: app-state/app-story score perturbations, app-state bands, E247 refill variants, and high state-by-amplitude penalties.
- Public-free stress: E246/E237 local geometry, E272 current-anchor scoring, and matched row/subject/dateblock placebo nulls.

Result:

- selectors audited: `28`.
- local E246/E237-like passes: `27`.
- materialized candidates: `27`.
- old strict-promote candidates: `0`.
- matched-placebo gate passes: `0`.
- public-free submission-ready candidates: `0`.
- E247/E256 anatomy:
  - E247-only cells are lower amplitude and moderately high app-entropy story;
  - E256-only cells are high amplitude and very high app-entropy story/state;
  - this explains why amplitude-constrained smoothing was risky, but it does not produce a stronger selector.

Decision:

- Do not submit any E283 file.
- App-entropy is useful as a diagnostic axis around Q3 smoothing, but not yet a local-governed selector.
- The next valid experiment should learn a sharper cell-tail target or row-alignment transfer objective; another scalar app-entropy rank tweak is blocked.

## E284 App-Entropy Decisive-Cell JEPA Governor

Question: can app-entropy become useful when it is moved from scalar selector logic into the E237/E249 decisive-cell JEPA target?

Method: `analysis_outputs/e284_appentropy_decisive_cell_jepa_audit.py`.

- Context views: app-state, app-state interactions, and app-story interactions added to the feature-NN1 decisive-cell latent.
- Local OOF stress: row5/subject5, risk/contrast targets, Q3/S4/all3 source scopes.
- Materialization stress: E237 gates versus E224/E154/E95.
- Current-frontier stress: E247-current matched row/subject/dateblock placebo governor.

Result:

- OOF rows: `3744`.
- OOF stress-promoted rows: `409`.
- E237 gate passes: `9`.
- selected materialized files: `9`.
- matched-placebo gate passes: `0`.
- public-free submission-ready files: `0`.
- best OOF paired improvement came from app-state interaction LR:
  - median delta loss `-0.000080361`;
  - mean tail-AUC delta `+0.003713380`;
  - app better loss rate `0.650641`.
- top materialized file dropped `25` Q3 cells and had E237 score `0.056990432`, but E247-current p90 was adverse/below resolution at `+0.000027736`.
- strongest E247-current row was still not usable: top21 file p90 `+0.000025223`, p90 dominance `0.037037`, matched-placebo gate `False`.

Decision:

- E284 is locally informative but blocked for submission.
- App-entropy improves the learned decisive-cell representation, but the selected cells miss most of the E247 public-positive set.
- Future validation must target E247 residual/preserve/undo labels directly; E224/E154 rollback gates are now too stale for current-frontier promotion.

## E285 E247-Residual Human-State Governor

Question: can the human/social/payday diary state repair E247 directly by choosing Q3 cells to preserve, undo, or extend?

Method: `analysis_outputs/e285_e247_residual_human_state_audit.py`.

- Anchor: current public-best E247 Q3 smoothing body.
- Candidate actions: partially undo selected E247 cells toward E224, or add selected outside-E247 cells toward E154/E247-like smoothing.
- Context: app-entropy state, diary-state JEPA features, human-social stories, cash-flow/payday stories, E280 story registry columns, and E284 decisive-cell summaries.
- Nulls: matched row, subject, and dateblock shuffles preserving movement shape.
- Local selector: E272/E279 current-anchor matched-placebo governor.

Result:

- boundary features: `51`.
- materialized candidates: `158`.
- matched nulls: `3318`.
- old strict-promote candidates: `0`.
- matched-placebo gate passes: `0`.
- public-free submission-ready candidates: `0`.
- best add p90: `-0.000003481`.
- best undo p90: `-0.000000902`.

Boundary anatomy:

- E247-only cells differ strongly from E256-only cells on amplitude, state-amplitude, month-start shopping/money-rumination, diary PCs, social communication, bedtime-phone, mobility, and bright-light features.
- This is a real diagnostic signal, not a submission certificate.

Decision:

- Do not submit any E285 file.
- Public LB is preserved.
- E285 raises the confidence that human/social state is useful as E247 boundary context, but blocks direct hand-built E247 residual edits.

## E286 E247 Preserve/Avoid Contrastive Governor

Question: can a learned contrastive E247 preserve/avoid latent turn human/social boundary anatomy into a locally certified E247-current Q3 tensor?

Method: `analysis_outputs/e286_e247_preserve_avoid_contrastive_latent.py`.

- Context families: human/social story state, app-entropy/diary/cash-flow context, cell geometry, human+geometry, and human+oldlaw context.
- Latent stress: stratified, subject, dateblock, permutation AUC p95, and source-transfer from E247-common-vs-E284-extra to E247-only-vs-E256-only.
- Materialization stress: E247-current Q3 add/undo/swap/control actions versus matched row/subject/dateblock nulls.

Result:

- latent rows: `128`.
- selected latents: `12`.
- materialized candidates: `533`.
- matched nulls: `11193`.
- old strict-promote candidates: `0`.
- matched-placebo gate passes: `0`.
- public-free submission-ready candidates: `0`.
- best broad identity latent is geometry-driven:
  - `e247_body_vs_clean_neither / cell_geometry / lr_l2`;
  - min AUC `0.998917`;
  - mean AUC `0.999399`.
- best human/social sibling-boundary latent is local but fragile:
  - `e247_only_vs_e256_only / human_social / lr_l1`;
  - min AUC `0.857143`;
  - mean AUC `0.872711`;
  - source-transfer AUC `0.403846`.
- best source-transfer AUC overall is only `0.519231`.
- best candidate p90 values are around `-0.000004`, below submission resolution.

Decision:

- Do not submit any E286 file.
- Public LB is preserved.
- E286 blocks "learn E247 cell identity from current pseudo-labels" as a breakthrough route.
- The next valid stress target is train/OOF-grounded social residual or row-alignment transfer, where the latent is supervised by labels/residuals rather than by test-side submission cell membership.

## E287 Train-Supervised Row-Alignment Transfer Governor

Question: can train OOF row-action benefit provide a label-grounded gate that transfers to E247-current test rows without public LB?

Method: `analysis_outputs/e287_train_supervised_row_alignment_transfer.py`.

- Train target: whether a q-sleep policy cell lowers OOF Q1/Q2/Q3 row logloss.
- Context: diary-state JEPA features, human/social/app-entropy context, action metadata, target/family/kind dummies, and base probability/logit.
- Train stress: subject and dateblock OOF baselines, row/subject/dateblock shuffled score nulls.
- Test stress: current E247 tensor movement versus matched row/subject/dateblock null candidates.

Result:

- latent rows: `36`.
- train policy rows: `180`.
- train-gated policies: `3`.
- materialized candidates: `3`.
- matched nulls: `63`.
- public-free ready candidates: `0`.
- best train-gated policy by loss: `q3_only/subject_oof/lr_l1`, train delta `-0.000978542`, dominance `0.900000`.
- best test transfer: `submission_e287_rowalign_q3_only_subject_oof_lr_l1_tf70_5fc12bc2.csv`, actual mean `-0.000051070`, actual p90 `-0.000034973`, final decision `too_small_to_submit`.
- mobility Q3 policies pass train gates but are adverse on current test tensor.

Decision:

- Do not submit any E287 file.
- Public LB is preserved.
- E287 separates signal from translator: train row-action placement has signal, but current train-to-test materialization is too small or unstable to spend a public slot.

## E288 Lifestyle-Bundle JEPA Governor

Question: can a broad bundle of human/social/cash-flow stories become a stable hidden lifestyle state that improves labels beyond matched nulls?

Method: `analysis_outputs/e288_lifestyle_bundle_jepa_audit.py`.

- Hidden target: top `28` E280 story scores, including commute/workday, bright-light, routine/app-entropy, heart-stress, and payday/month-start cash-flow stories.
- Context views: E273 family JEPA context, E262 raw human/day context, and a hybrid view.
- Latent stress: subject/dateblock OOF reconstruction, PCA geometry, k4/k6/k8 cluster train/test JS, subject NMI, self-transition.
- Label stress: subject/dateblock CV with PC or cluster latent added to subject/calendar baseline, compared to row/subject/dateblock shuffles.

Result:

- label stress rows: `12`.
- label-gate rows: `0`.
- best mean label delta: `+0.002092612`.
- strongest reconstruction: `family_jepa_context/dateblock5`, mean story R2 `0.385944`, positive R2 rate `0.928571`.
- strongest story reconstructions include `heart_stress_late` R2 `0.852864`, `paymonth_start_post3_late_shopping` R2 `0.813342`, and `app_entropy_scattered_day` R2 `0.739960`.
- best label-stress row: `raw_human_context/dateblock5/cluster6`, dominance `0.972222` versus nulls but actual mean `+0.002093`, so it fails because it worsens the average target loss.

Decision:

- Do not submit any E288 file.
- Public LB is preserved.
- The broad human lifestyle state is real as representation but unsafe as a shared label feature. Future validation should be target-specific and must not average useful S4/Q3/S2 slices with adverse Q/S axes.

## E289 Target-Specific Lifestyle Slice Governor

Question: can E288's broad lifestyle state become useful when split into per-target Q/S slices and materialized as tiny E247-current edits?

Method: `analysis_outputs/e289_target_specific_lifestyle_slice_audit.py`.

- Hidden target: the same E288 lifestyle-story bundle, but evaluated per downstream target.
- Context views: family JEPA context, raw human context, and hybrid context.
- Train stress: per-target subject/dateblock CV versus row/subject/dateblock shuffled lifestyle reps.
- Test stress: E247-current target-only logit edits versus matched row/subject/dateblock null submissions.

Result:

- target-slice rows: `84`.
- target-gate rows: `7`.
- materialized candidates: `28`.
- matched nulls: `420`.
- public-free ready candidates: `0`.
- strongest target slices:
  - `Q3_raw_human_context_subject5_pc`, delta `-0.014465898`;
  - `S4_family_jepa_context_dateblock5_cluster6`, delta `-0.011131`;
  - `S4_raw_human_context_dateblock5_cluster6`, delta `-0.009936`.
- best-looking local candidate has mean `-0.000674` and p90 `-0.000417`, but null strict rate `1.000000` and worst-mode p90 dominance `0.000000`.

Decision:

- Do not submit any E289 file.
- Public LB is preserved.
- Target-specific lifestyle signal is real, especially Q3/S4, but current materialization is not row-placement certified.

## E290 Lifestyle Row-Placement Law Governor

Question: can E289's Q3/S4 lifestyle slices learn where they should be applied from train OOF row benefit?

Method: `analysis_outputs/e290_lifestyle_row_placement_law_audit.py`.

- Hidden target: whether the E289 slice improves a train row under OOF base-vs-augmented target prediction.
- Train stress: subject/dateblock placement gates versus row/subject/dateblock score shuffles.
- Test stress: E247-current target-only edits selected by the learned gate versus matched row/subject/dateblock null submissions.

Result:

- placement rows: `420`.
- train placement gates: `59`.
- materialized candidates: `48`.
- matched nulls: `720`.
- public-free ready candidates: `0`.
- best train gate: Q3 raw-human subject5 PC, strong35/dateblock5/HGB, top_frac `0.35`, actual delta `-0.024399167`.
- best candidate-level movement: mean `-0.000495`, p90 `-0.000308`, but null strict rate `1.000000`.

Decision:

- Do not submit any E290 file.
- Public LB is preserved.
- Train row-placement exists, but test transfer is still not matched-null certified.

## E291 Lifestyle Block-State Assignment Governor

Question: can the failed row-placement problem be lifted to hidden subject/calendar/lifestyle block states?

Method: `analysis_outputs/e291_lifestyle_block_state_assignment_audit.py`.

- Hidden target: block-level benefit for E289/E290 target-specific lifestyle slices.
- Block schemes: dateblock, subject-weekday, subject-weekend, subject-month/payday phase, and subject-lifestyle-bin.
- Train stress: subject/dateblock CV block predictors versus row/subject/dateblock block-score shuffles.
- Test stress: E247-current block-gated target edits versus matched null submissions.

Result:

- block policy rows: `560`.
- train block gates: `39`.
- materialized candidates: `40`.
- matched nulls: `600`.
- public-free ready candidates: `0`.
- strongest train block: S4 lifestyle-bin mean-good subject-CV, block fraction `0.50`, actual delta `-0.017607`, null median `-0.011219`, dominance `0.979167`.
- strongest Q3 block family: weekday/weekend policies from family-JEPA/dateblock PC state, with train deltas around `-0.013683` to `-0.016741`.
- best submitted-scale local candidates have negative mean/p90 but fail matched-null governance; all promote-scale rows end as `blocked_by_matched_nulls`.

Decision:

- Do not submit any E291 file.
- Public LB is preserved.
- Coarser social block state is real on train, but block assignment alone does not solve test placement transfer.

## E292 Contrastive Lifestyle Placement Governor

Question: can real lifestyle block placement be separated from matched-null placement before probability materialization?

Method: `analysis_outputs/e292_contrastive_lifestyle_placement_invariant.py`.

- Input: E291 train block policies and E247-current base tensor.
- Hidden target: blocks that are high-score under the real lifestyle placement model but comparatively rare under row/subject/dateblock score shuffles.
- Train stress: selected contrast blocks versus shuffled contrast scores.
- Test stress: E247-current contrast-gated edits versus matched row/subject/dateblock null submissions.

Result:

- contrast rows: `98`.
- train contrast gates: `34`.
- materialized candidates: `56`.
- matched nulls: `840`.
- public-free ready candidates: `0`.
- best train contrast delta: `-0.014723076`.
- old strict-promote candidates: `18`.
- lowest old-strict null strict rate: `0.133333` on an S4 lifestyle-bin `base_lowmax35/raw/0.50` candidate.
- Q3 contrast candidates remain mostly null-reproducible; best Q3 p90 candidates have null strict rate `1.000000`.

Decision:

- Do not submit any E292 file.
- Public LB is preserved.
- Anti-null filtering is a partial diagnostic success for S4 but not yet a promotion rule.

## E293 S4 Low-Null Lifestyle Candidate Governor

Question: can the E292 S4 near-miss become public-free ready by refining scale and low-null block selection?

Method: `analysis_outputs/e293_s4_lownull_lifestyle_candidate_refiner.py`.

- Scope: only S4 `family_jepa_context/dateblock5/cluster6/subject_lifestyle_bin` parent policies.
- Candidate filters: low-null max-rate thresholds, rarity/contrast top-k, and hybrid low-null top-k rules.
- Candidate scales: `0.30` to `0.60`.
- Stress: old local selector prefilter plus matched row/subject/dateblock null submissions.

Result:

- generated candidates: `840`.
- old strict candidates: `554`.
- null-evaluated candidates: `64`.
- matched null evaluations: `1344`.
- public-free ready candidates: `0`.
- null strict rate `0.000000` appears only for `too_small_to_submit` candidates.
- old-strict versions of the same pocket start at null strict rate `0.476190`; broad p90-strong candidates go to `1.000000`.

Decision:

- Do not submit any E293 file.
- Public LB is preserved.
- The S4 low-null pocket has a resolution cliff: null-safe movement is too small, and selector-visible movement is placebo-reproducible.

## E294 S4 Candidate-Level Invariant Governor

Question: can output-space candidate geometry distinguish real S4 lifestyle placement from matched null placement?

Method: `analysis_outputs/e294_s4_candidate_invariant_audit.py`.

- Input: E293 candidate scores and matched row/subject/dateblock null scores.
- Stress: leave-one-source-out actual-vs-null classification.
- Feature sets: selector, anchor geometry, S4-local, and all output-space features.
- Submission health check: correlation between realness and null strict rate / mean dominance / p90 dominance.

Result:

- source candidates: `64`.
- matched null rows: `1344`.
- best actual-vs-null AUC: `0.883498`.
- best top3 actual rank rate: `0.671875`.
- S4-local-only AUC: `0.619617`.
- realness vs null strict rate: positive, not negative.
- public-free ready candidates: `0`.

Decision:

- Do not submit any E294/E293 file.
- Public LB is preserved.
- Candidate identity is learnable, but it is not a safe promotion invariant.

## E295 Human Episode-State JEPA Audit

Question: can broader human social episode states be predicted from context and help labels without public LB?

Method: `analysis_outputs/e295_episode_state_jepa_audit.py`.

- Episode states: commute pressure, bedtime arousal, routine fragmentation, routine anchor recovery, cash-flow stress, cash-flow relief/spend, physiology strain, home recovery, social overload, measurement wear confidence, and bad-night aftereffect.
- Context views: `family_jepa_context`, `raw_human_context`, `hybrid_context`.
- Stress: subject5/dateblock5 OOF reconstruction, target label CV, row/subject/dateblock shuffled state nulls.

Result:

- episode states: `11`.
- reconstruction rows: `66`.
- broad label gates: `0`.
- target-specific gates: `51`.
- best context reconstruction: `family_jepa_context/dateblock5`, mean R2 `0.438241`.
- best target instance: `cashflow_stress/S1`, delta `-0.017243504`.

Decision:

- No public submission.
- E295 is a discovery atlas only.
- Target-specific episode states are worth stricter null testing; the broad episode bundle is not.

## E296 Episode-Target Strict Null Governor

Question: which E295 episode-target signals survive a stricter null budget?

Method: `analysis_outputs/e296_episode_target_strict_null_audit.py`.

- Candidate set: E295 multi-view/split consensus pairs plus large single-view all-null wins.
- Null budget: `64` row, `64` subject, `64` dateblock reps per candidate instance.
- Stress target: target-specific label CV delta versus matched shuffled state.

Result:

- candidate instances: `33`.
- strict gates: `19`.
- robust gates: `5`.
- pair gates: `2`.
- robust signals:
  - `bedtime_arousal/S3`;
  - `routine_fragmentation/S1`;
  - `routine_anchor_recovery/S2`;
  - `routine_fragmentation/S3`;
  - `bedtime_arousal/S1`.
- pair-gated signals: `bedtime_arousal/S1` and `bedtime_arousal/S3`.

Decision:

- No public submission.
- Use only E296 robust states for materialization.
- Cash-flow/payday remains a diagnostic but not the strongest strict signal.

## E297 Episode-State Materialization Governor

Question: can E296 robust states produce current-best E247 edits that beat matched null submissions?

Method: `analysis_outputs/e297_episode_state_materializer.py`.

- Source states: the `5` E296 robust episode-target instances.
- Materialization: target-specific logistic state delta on top of `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`.
- Candidates: `150` scale/top-k variants.
- Prefilter: E272 current-anchor selector.
- Stress: `39` selected candidates against row/subject/dateblock null submissions.

Result:

- old strict candidates: `25`.
- public-free ready candidates: `0`.
- best actual p90: `-0.000565475`.
- lowest null strict rate: `0.000000`, but those rows are `too_small_to_submit`.
- selector-visible bedtime/routine S1 candidates are blocked by null strict rates around `0.714286` to `1.000000`.

Decision:

- Do not submit any `submission_e297_epstate_*.csv` file.
- Public LB is preserved.
- The next governor must target candidate outcome health, not only human episode label delta.

## E298 Materialization Outcome Atlas

Question: does the existing governed archive already contain a public-free candidate worth submitting?

Method: `analysis_outputs/e298_materialization_outcome_atlas.py`.

- Inputs: `11` current-anchor governor summaries.
- Candidate rows: `1044`.
- Public LB: not used.

Result:

- ready-like candidates: `0`.
- selector-visible candidates: `162`.
- null-rare candidates: `867`.
- selector-visible and null-rare candidates: `0`.
- null-rare and edge-ok candidates: `0`.
- selector-visible and null-common candidates: `160`.

Decision:

- No public submission from the E279/E284-E297 archive.
- The local gate is now explicit: future candidates must satisfy `selector-visible + null-rare`, not only negative p90 or story plausibility.

## E299 Visibility/Null Bridge Scan

Question: did E298 miss a ready candidate because the scale grid was too coarse?

Method: `analysis_outputs/e299_visibility_null_bridge_scan.py`.

- Base near-misses: `14`.
- Generated rescaled candidates: `102`.
- Old strict prefilter candidates: `81`.
- Null-evaluated candidates: `71`.
- Public LB: not used.

Result:

- public-free ready candidates: `0`.
- `null_rare_edge_near`: strict `2/12`, but best strict null rate `0.428571`.
- `visible_common_scale_down`: strict `45/45`, but minimum null strict rate `0.952381`.
- `visible_low_null_near`: best S4 row has old strict true, null strict `0.095238`, p90 dominance `0.952381`, worst-mode `0.857143`, but mean dominance only `0.476190`.

Decision:

- No E299 public submission.
- Plain amplitude rescaling is now deprioritized.
- The next stress should target S4 mean-dominance/within-subject placement, not visibility.

## E300-E301 S4 Large-Null Confirmation Gate

Question: can the closest E299 S4 near-miss be rescued locally without spending public LB?

Method:

- `analysis_outputs/e300_s4_mean_dominance_rescue.py` generated mask/sign/dateblock variants from the closest E299 S4 candidate and used a small matched-null governor.
- `analysis_outputs/e301_s4_ready_strict_confirm.py` then took the single E300 ready file and reran it against a larger independent null set.

E300 result:

- generated candidates: `1305`.
- old strict prefilter candidates: `199`.
- null-evaluated candidates: `120`.
- small-governor ready candidates: `1`.
- ready file: `analysis_outputs/submission_e300_s4mean_drop_dateblock_id07_b9_raw_m1p16_d285ff4a.csv`.

E301 strict confirmation:

- null submissions: `256`.
- null modes: row, subject, dateblock, sign.
- actual p90: `-0.000051307`.
- actual mean: `-0.000161310`.
- null strict rate: `0.164062`.
- p90 dominance: `0.937500`.
- mean dominance: `0.691406`.
- worst-mode mean dominance: `0.328125`.
- decision: `do_not_submit`.

Failure mode:

- sign nulls do not threaten the file, so the S4 direction is not arbitrary.
- row nulls also do not threaten it.
- subject/dateblock nulls do threaten it: subject strict rate `0.250000`, dateblock strict rate `0.406250`.
- The file's p90 edge is real-looking, but the mean edge is reproducible by matched block placement.

Decision:

- Do not submit E300.
- Future public candidates must pass this large-null confirmation layer before being recommended.
- The current public-free validator is now stricter than the old E272 selector: old strict promotion is treated as prefilter only.

## E302 Placement-Health Decoder Stress

Question: after E301, can raw human diary context predict which S4 placements are healthy?

Method: `analysis_outputs/e302_s4_placement_health_decoder.py`.

- Placement lab: E301 actual candidate plus `256` null placements.
- Features: topology, story/episode states, all diary JEPA/human features, and diary plus topology.
- Evaluation: leave-mode-out over row/subject/dateblock/sign null modes, plus random 5-fold diagnostics.
- Public LB: not used.

Result:

- `human_all` leave-mode-out mean Spearman: `0.400962`.
- `human_all_plus_topology` leave-mode-out mean Spearman: `0.325973`.
- `story_episode` strict AUC: `0.629383`, but mean Spearman only `0.139057`.
- p90 Spearman is weak or negative for human feature sets.
- E300 actual candidate:
  - predicted mean rank pct `0.433594` under `human_all_plus_topology`;
  - predicted p90 rank pct `0.000000`.

Decision:

- E302 does not produce a submission candidate.
- It supports a narrower next validator: optimize and confirm the mean-placement axis, not p90/tail visibility.
- Human/social context has enough signal to justify one constrained S4 placement-prior experiment, but not enough to override E301 rejection.

## E303 S4 Mean-Placement Prior Stress

Question: can the E302 mean-placement prior become a public-free S4 candidate generator?

Method: `analysis_outputs/e303_s4_mean_prior_materializer.py`.

- Generated S4-only candidates: `260`.
- Old strict prefilter candidates: `183`.
- Null-evaluated candidates: `12`.
- Null stress: `32` row, `32` subject, `32` dateblock, and `32` sign nulls per selected candidate.
- Public LB: not used.

Result:

- public-free ready candidates: `0`.
- best null strict rate: `0.187500`.
- best mean dominance: `0.695312`.
- best actual p90: `-0.000074119`.
- the best-looking rows still fail conservative gates because null strict rate remains above the `0.10` scarce-public line and worst-mode mean dominance is weak.

Decision:

- No E303 file should be submitted.
- E302's human placement prior remains a diagnostic feature, not an action-layer feature.
- Future S4 work needs a new hidden block-placement target; another mask or multiplier sweep is low value.

## E304 Hidden Block-State JEPA Stress

Question: can raw human diary context predict hidden subject/dateblock target residual state?

Method: `analysis_outputs/e304_hidden_block_state_jepa_probe.py`.

- Target representation: shrunken block-level Q/S logit residual after subtracting subject prior.
- Context views: calendar, family-JEPA diary state, story/episode state, raw top features, full human diary.
- Stress: subject-held OOF, block-random OOF, and shuffled block-target nulls.
- Public LB: not used.

Result:

- representation gates: `3`.
- best view: `family_jepa/subject_holdout`.
- best mean Spearman: `0.143141`.
- null dominance: `0.986111`.
- positive Spearman targets: `7/7`.
- S4 Spearman: `0.124633`.
- candidate alignment diagnostic:
  - E299 active blocks are anti-aligned with predicted S4 state: active minus inactive predicted S4 `-0.151507`;
  - E300 improves by removing `id07_b9`, which E304 predicts as S4-low (`-0.415169`), but still remains anti-aligned overall.

Decision:

- Hidden block-state recovery is alive.
- This is not enough for public submission, but it explains why previous S4 placement edits failed.
- The next materializer should test whether E304-positive S4 blocks can move probabilities while beating matched nulls.

## E305 Block-Prior S4 Materializer Stress

Question: does the E304 block prior directly create a public-free S4 candidate?

Method: `analysis_outputs/e305_block_prior_s4_materializer.py`.

- Generated candidates: `111`.
- Old strict candidates: `14`.
- Null-evaluated candidates: `14`.
- Null stress: `32` row, `32` subject, `32` dateblock, and `32` sign nulls per selected candidate.
- Public LB: not used.

Result:

- public-free ready candidates: `0`.
- best null strict rate: `0.648438`.
- best mean dominance: `0.562500`.
- best actual p90: `-0.000127522`.

Decision:

- No E305 file should be submitted.
- The block prior is a real diagnostic state, but direct top-block S4 lifting is null-common.
- Future action-layer work must predict `selector-visible + null-rare` movement, not only high predicted S4 blocks.

## E306 Within-Dateblock S4 Row-Placement Stress

Question: can the E304 block prior be repaired by choosing the right row inside each dateblock?

Method: `analysis_outputs/e306_within_block_s4_row_placement.py`.

- Row-placement diagnostic:
  - best view: `family_jepa_dbdelta/row_stratified5`;
  - best within-dateblock AUC: `0.585020`;
  - dateblock-held family-JEPA-delta within AUC: `0.574899`;
  - row-placement gates: `6/15`;
  - mixed train dateblocks: `60`.
- Candidate stress:
  - generated candidates: `272`;
  - old strict candidates: `22`;
  - null-evaluated candidates: `20`;
  - null stress: `32` row, `32` subject, `32` dateblock, and `32` sign nulls per selected candidate.
- Public LB: not used.

Result:

- public-free ready candidates: `0`.
- best null strict rate: `0.625000`.
- best dateblock p90 dominance: `0.875000`.
- best mean dominance: `0.671875`.
- controls using wrong rows can still look selector-visible, which means the current selector is not yet reading row identity cleanly.

Decision:

- No E306 file should be submitted.
- The row-placement latent is live, but materialization remains unhealthy.
- Future public-free checks should keep dateblock-shuffle nulls as mandatory; otherwise a candidate can look good by block or target movement alone.

## E307 S4 Latent Censor Stress

Question: can hidden S4 block/row state be used as a calibration-risk censor instead of a positive S4 generator?

Method: `analysis_outputs/e307_s4_latent_censor_materializer.py`.

- Current/latent diagnostics:
  - latent-current S4 logit correlation: `0.302062`;
  - block-row latent correlation: approximately `0.000000`;
  - top-24 mismatch rows have current S4 mean `0.615838`.
- Candidate stress:
  - generated candidates: `765`;
  - old strict candidates: `106`;
  - null-evaluated candidates: `22`;
  - null stress: `32` row, `32` subject, `32` dateblock, and `32` sign nulls per selected candidate.
- Public LB: not used.

Result:

- public-free ready candidates: `0`.
- best null strict rate: `0.750000`.
- best mean dominance: `0.546875`.
- best dateblock p90 dominance: `0.656250`.
- best actual p90: `-0.000197843`.
- sign nulls are beaten, but row/subject/dateblock nulls are essentially too competitive; the selected censor actions do not certify row/block identity.

Decision:

- No E307 file should be submitted.
- Simple latent-current mismatch censoring is rejected as a direct action layer.
- The S4 branch now has repeated evidence that old strict visibility is cheap and not enough.

## E308 Action-Outcome Governor Atlas

Question: can public LB be replaced by a stricter local promotion rule built from all governed candidate outcomes?

Method: `analysis_outputs/e308_action_outcome_atlas.py`.

- Sources: `18` governor files from E279-E307.
- Rows: `1304` governed candidates.
- Labels:
  - `selector_visible`: old/local selector sees a negative edge;
  - `null_rare`: matched row/subject/dateblock/sign nulls rarely reproduce the edge;
  - `visible_null_rare`: both conditions;
  - `certified_public_free_ready`: visible/null-rare plus edge and dominance gates, excluding E300 small-governor rows superseded by E301.
- Public LB: not used.

Result:

- selector-visible: `367/1304`.
- null-rare: `918/1304`.
- visible/null-rare: `2/1304`.
- certified public-free ready: `0/1304`.
- post-E303 S4 action rows: `68`; null-rare `0`.
- leave-experiment-out diagnostic AUC:
  - selector-visible `0.998857`;
  - null-rare `0.982794`;
  - null-common `0.986466`;
  - visible-null-common `0.989142`.

Decision:

- No current archive file should be submitted only because it is old-strict or has attractive p90.
- The local promotion rule is now stricter: old visibility is only a prefilter; a candidate needs null rarity and mode-wise dominance before public LB.
- The latest hand-built S4 family should be paused. It repeatedly creates visible/null-common actions, not public-free actions.

## E309 Episode Target-Interaction Stress

Question: did E297 fail because human episode states were translated as single-target movements even though the true signal is target dependency?

Method: `analysis_outputs/e309_episode_target_interaction_probe.py`.

- Input states: E295/E296 human episode states.
- Target object: 4-class joint label for E296-neighborhood target pairs.
- Quick scan: actual pair-logloss delta only.
- Strict stress: top `32` rows, row/subject/dateblock nulls, `12` reps per mode.
- Public LB: not used.

Result:

- quick scanned rows: `426`.
- strict rerun rows: `32`.
- strict gates: `29`.
- robust gates: `13`.
- pair gates: `12`.
- pair-family read:
  - QS rows: `18`, strict `16`, robust `8`, best delta `-0.046023`;
  - SS rows: `12`, strict `12`, robust `5`, best delta `-0.019841`;
  - QQ rows: `2`, strict `1`, robust `0`, best delta `-0.016790`.
- strongest pair gates:
  - `cashflow_stress/Q1_S1`: best delta `-0.046023`, strict instances `3`, robust instances `2`;
  - `cashflow_stress/S1_S4`, `S1_S2`, `S1_S3`;
  - `bedtime_arousal/Q1_S1`, `Q3_S3`, `Q1_S3`, `Q2_S3`, `S1_S2`;
  - `home_recovery/Q1_S3`, `S3_S4`;
  - `badnight_aftereffect/Q3_S3`.

Decision:

- Human/social state survives as a target-interaction representation.
- This is not yet a submission certificate. It must be translated into coupled target deltas and then pass wrong-pair plus shuffled-state materialization nulls.
- E309 makes the next public-free branch clear: target-pair dependency correction, especially cashflow/Q1-S1 and bedtime-arousal/Q-S/S-stage pairs.

## E310 Pair-Interaction Materialization Governor

Question: can E309's robust target-pair states be converted into public-free current-tensor probability movement?

Method: `analysis_outputs/e310_pair_interaction_materializer.py`.

- Source: E309 robust/strict episode-pair rows.
- Candidate actions: coupled pair deltas on current E247, using `joint_centered`, sparse top-abs, same-sign, opposite-sign, and difference masks across scales.
- Null stress: row, subject, dateblock, swap-targets, wrong-pair, and sign-flip controls.
- Public LB: not used.

Result:

- generated candidates: `455`.
- old strict candidates: `77`.
- null-evaluated candidates: `42`.
- public-free ready candidates: `0`.
- strongest old-strict source family:
  - `cashflow_stress/Q1_S1`: `29/70` old strict, best p90 `-0.000379563`;
  - `home_recovery/Q1_S3`: `17/35` old strict;
  - `cashflow_stress/S1_S2`: `15/35` old strict;
  - `cashflow_stress/S1_S3`: `13/35` old strict.
- best old-strict candidates are rejected because null strict rates are usually `0.55` to `0.83`.
- too-small candidates can be null-rare, but their old strict gate is false and their edge is below submission resolution.

Decision:

- No E310 file should be submitted.
- This locally enforces the user's constraint: public LB is not the checker; matched controls are the checker.
- Pair state remains a valid diagnostic, but direct coupled delta translation is rejected until an action-health or energy-gated translator makes the intended pair beat wrong-pair and shuffled-state controls.

## E311 Pair Micro-Action Combiner Stress

Question: can E310's null-rare too-small pair actions be stacked into a visible candidate without becoming null-common, or can matched-null residualization rescue old-strict pair actions?

Method: `analysis_outputs/e311_pair_micro_action_combiner.py`.

- Candidate actions:
  - stack top null-rare E310 micro actions;
  - stack one null-rare action per pair;
  - stack cashflow-only micro actions;
  - subtract E310 row/subject/dateblock/wrong/swap null means from old-strict actions.
- Null stress: row, subject, dateblock, swap-targets, wrong-pair, and sign-flip controls.
- Public LB: not used.

Result:

- generated candidates: `512`.
- old strict candidates: `489`.
- null-evaluated candidates: `37`.
- public-free ready candidates: `0`.
- `microstack` creates the strongest local edge, best p90 `-0.000807827`, but null strict rate is at least `0.611111`.
- `microdiverse` and `microcash` also become old-strict, but null strict rates are at least `0.722222`.
- `residualized_visible` can make null-safe too-small rows, but visible residuals still fail the governor.

Decision:

- No E311 file should be submitted.
- The E310/E311 pair branch is now locally falsified as direct probability movement.
- The next target should be a learned action-health representation, not scale, stacking, or average-null subtraction.

## E312 Action-Health Leave-Experiment-Out Stress

Question: can local governors replace public LB as the checker for new candidate actions?

Method: `analysis_outputs/e312_action_health_world_model.py`.

- Inputs: `20` governed experiment families from E279-E311.
- Rows: `1383` candidate/action summaries.
- Feature views:
  - `semantic_only`: story, target, episode, family labels and human/social summary columns;
  - `geometry_only`: action recipe, movement, current-anchor, and materializer geometry;
  - `full_safe`: all non-outcome, non-leaking safe fields.
- Split: leave-one-experiment-family-out.
- Public LB: not used.

Result:

- visible/null-rare rows: `2`.
- strict-health rows: `1`.
- `geometry_only` predicts null-common with AUC `0.984890`.
- `semantic_only` predicts null-common with AUC `0.713484`.
- `full_safe` predicts null-common with AUC `0.982065`.
- `full_safe` readiness-distance Spearman is only `0.102712`.

Decision:

- E312 is strong enough as a public-free blocker: if a new action is predicted as null-common by geometry, it should not be submitted.
- E312 is not yet a submission selector: the archive has too few visible/null-rare positives and readiness ranking does not transfer well.
- Promotion rule update: a future file must pass matched-null governance directly; action-health predictions can veto but cannot certify by themselves.

## E313 Human-Diary Action Signature Stress

Question: does the raw lifestyle context of touched rows add public-free action-health signal beyond geometry?

Method: `analysis_outputs/e313_human_action_signature.py`.

- Inputs: E312 governed rows plus candidate submission files, E247 current frontier, and test-side E268/E270/E273 human diary features.
- Rows: `1383` governed candidates; candidate files found `1379`.
- Feature views:
  - `human_signature`: delta-weighted human/social/cashflow/diary features of touched rows;
  - `shape_signature`: candidate delta shape only;
  - `geometry_only`: E312 non-leaking action geometry;
  - combined geometry/shape/human blocks.
- Split: leave-one-experiment-family-out.
- Public LB: not used.

Result:

- `human_signature` null-common AUC: `0.866674`.
- `geometry_only` null-common AUC: `0.982733`.
- `geometry_plus_shape` null-common AUC: `0.987170`.
- `geometry_shape_human` null-common AUC: `0.956459`.
- `human_signature` readiness-distance Spearman: `0.700161`.
- `geometry_only` readiness-distance Spearman: `0.031522`.
- In selector-visible rows, `human_signature` null-common AUC is `0.745343`, but positive rate is `0.976077`, so this is a rare-negative diagnostic, not a certificate.

Decision:

- Human diary row placement is a real diagnostic, especially for readiness distance.
- It does not improve the global null-common blocker over action geometry and therefore cannot certify a submission.
- Promotion rule update: human-readiness energy can rank or guide new materializers, but every resulting file still needs direct matched-null passage.

## E314 Human-Readiness Lift Materializer Stress

Question: can E313 human-ready safe-but-too-small seeds be made visible without becoming null-common?

Method: `analysis_outputs/e314_human_ready_lift_materializer.py`.

- Inputs: E313 readiness readout, E247 current frontier, candidate submission files from previous governed experiments.
- Candidate actions: individual human-ready seed lifts with scale and sparsity variants.
- Null stress: row, subject, dateblock, target permutation, Q/S swap, and sign flip.
- Public LB: not used.

Result:

- safe human-ready seeds: `180`.
- generated candidates: `360`.
- old strict candidates: `33`.
- info candidates: `134`.
- null-evaluated candidates: `40`.
- public-free ready candidates: `0`.
- best actual p90: `-0.000087616`.
- visible candidates are null-common; null-rare candidates are below submission resolution.
- The first E314 run did not test consensus/negative-stack candidates because the single-lift family saturated the generation budget.

Decision:

- No E314 file should be submitted.
- This is the local check the user asked for: public LB is not the checker; matched null governance blocks these files.
- The remaining live path is not more scalar amplitude. It is either an E314b materializer with quota-reserved consensus/orthogonal stacks, or a new target-level action layer that changes the geometry before visibility.
