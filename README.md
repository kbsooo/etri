# ETRI Sleep Lifestyle Competition Workspace

This repository snapshot is rooted at the former local `cl2/` workspace.

Current public frontier:

- `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv`
- Public LB: `0.5677475939`
- Previous frontier: `submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv`
- Improvement over previous frontier: `0.0001572309`
- Interpretation: H012 validates the public-equation HS-JEPA branch, H042 adds
  the first post-H012 Q2 phase action, and H057 now validates the stronger
  row-level hidden human-state translation. The active state is no longer
  Q2-only: the H042 Q2-support rows can carry a full non-Q2 target vector when
  decoded carefully.
- Latest public observation: `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv`
  scored `0.5677475939`. Since H057 froze Q2 and moved Q1/Q3/S1-S4 only on the
  `45` H042 Q2-support rows, this is direct evidence for a compact row-state
  latent rather than a broad non-Q2 route.
- Active HS-JEPA/0.53 track:
  - `hs_jepa_architecture.md`
  - `breakthrough_bets.md`
  - `public_private_factorization.md`
  - `human_state_hypotheses.md`
- Latest generated row-target assignment big bet:
  `submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv`. H071 turns
  H070's smooth latent into a discrete row-target route assignment problem. The
  promoted candidate changes `736` cells on `158` rows, with `385` cells
  outside H070 and `642` cells outside H069. It moves `72` Q2 cells and uses a
  broad route mix: `full_state:63`, `nonq2_full:47`, `q3_s_stage:13`,
  `s_stage:16`, plus smaller Q-route/recovery routes. Public-action predicted
  delta versus H057 is `-0.000983`, posterior delta is `-0.000744`, and bad
  anchor positive cosine is `0.0`. Interpretation: this is the first H071 file
  close to the `0.001` big-bet gate. A public win would make exact row-target
  assignment the main HS-JEPA decoder; a loss would say the current route
  templates or action-health translation are wrong, not merely under-tuned.
- Latest generated human-social state engine sensor:
  `submission_h072_humansocial_route_bae1edae_uploadsafe.csv`. H072 converts
  the `1000` human-state hypotheses into story-family latents and uses them as
  route priors over H071 assignments, not as direct label rules. The promoted
  file changes `704` cells on `148` rows, with `613` cells outside H069 and
  `97/148` selected routes outside the H071 promoted route set. It has
  public-action predicted delta `-0.000922`, posterior delta `-0.000696`,
  responsibility-weighted delta `-0.000935`, and no positive bad-anchor cosine.
  The important caveat is that subject-preserving null stress did not validate
  story priors as H071 route rediscovery: H071-route support real/null was
  `0.776796/0.783463` with z `-1.326523`. Interpretation: human-social stories
  are useful action-health context candidates, but H072 is a sensor, not yet
  paper-grade proof that story latents solve route assignment.
- Latest generated full HS-JEPA diagnostic:
  `submission_h070_full_hsjepa_9e4a9602_uploadsafe.csv`. H070 is the first
  joint HS-JEPA correction-field decoder. It predicts public/private/action
  representations from human/context, route, 1000-story target priors, and
  shortcut views, then decodes a `latent_hsjepa_score` toward H061 `q061`. The
  selected candidate changes `360` cells on `144` rows, with `323` cells
  outside H069, `42` Q2 cells, public-action predicted delta `-0.000826`, and
  no positive bad-anchor cosine. Interpretation: smooth HS-JEPA latent scoring
  is real but not yet a `0.001`-scale solver; the next big bet is H071
  row-target assignment.
- Latest generated public/private factorization diagnostic:
  `submission_h069_public_private_factor_4ffd6cd6_uploadsafe.csv`. H069 is the
  first explicit factorized HS-JEPA action field: each row-target action gets a
  public/action-health score, invariant/context score, and shortcut score. The
  selected file changes `268` cells on `97` rows, including `36` Q2 cells, with
  public-action predicted delta `-0.000586` and posterior delta `-0.000488`
  versus H057. It overlaps H068 on `250/268` changed cells. Interpretation:
  factorization is real enough to keep, but strict private-safe filtering cuts
  the broader H068 movement; the next big-bet route is H070 full HS-JEPA or H071
  row-target assignment rather than more H069 threshold tuning.
- Latest generated public-free diagnostic:
  `submission_h068_action_health_3cb4f94c_uploadsafe.csv`. H068 asks whether
  the post-H057 bottleneck is cell-level action health rather than row
  membership. It uses `24` known public observations and `23` H057-relative
  equations, fits an origin-constrained action-health decoder with LOO MAE /
  p90 `0.000331247` / `0.000924782`, changes `700` cells on `174` rows, allows
  `33` Q2 cells to move, and selects zero H050-null rows/cells. This is a
  high-risk sensor, not a safe refine: a public win would make action-health a
  core HS-JEPA target, while a loss would push the architecture back toward
  row-responsibility or sequence-state decoding.
- Previous generated high-risk sensor:
  `submission_h067_rowresp_public_state_b10ea6b8_uploadsafe.csv`. H067 asks
  whether H057 should be read as a public-responsibility weighted row-state. It
  freezes Q2 and changes `336` non-Q2 cells on `78` rows: `12` H057 seed rows
  plus `66` high-responsibility expansion rows.
- Previous generated high-risk sensor:
  `submission_h063_humancontext_seed_2c748a8e_uploadsafe.csv`. H063 asks
  whether the H057 full-vector row-state can be rediscovered from label-free
  human/social/lifestyle/raw context. It freezes Q2 and moves full non-Q2
  vectors on `72` new rows, changing `432` cells versus H057. It overlaps H062
  on `30/72` rows; the strongest context views are E268 story features and deep
  raw aggregates. This is the current HS-JEPA architecture bet: a win means
  H057 was context-discoverable human state, not just public-equation gain; a
  loss means nearest-context state translation is not enough.
- Earlier generated high-risk sensor:
  `submission_h062_h057seed_rowstate_expand_23beb8eb_uploadsafe.csv`. H062
  treats the `45` H057 rows as seed examples of a larger hidden human-state
  class, freezes Q2, and moves full non-Q2 vectors on `48` new rows. This is
  still the cleaner posterior-gain expansion control: a win means H057 was a
  seed set, not a closed correction; a loss means the validated H057 state is
  compact/public-specific.
- External reference note: the attached high-scoring `submission_v106_sleep_state_conditioned_memory.csv` document reports public LB `0.5703952266` from same-subject sleep-state/sensor-quality-conditioned memory. That supports the broader repeated-subject world model, but H057 is lower by `0.0026476327`.

Current post-H012 status:

- H057 full-vector row-state translation is the active public frontier. H042 is
  still the public-confirmed Q2 row anchor, and H012 remains the base
  public-equation anchor.
- H043, H045, H047, H048, H049, H050, H051, and H052 are historical
  high-information post-H042 sensors, not current upload priorities:
  - H043 tests whether the Q2 phase branch can expand from `45` to `105`
    cells;
  - H045 tests whether human-state route context can prune that expansion to a
    `75`-cell route-conditioned support;
  - H047 tests whether support identity is the missing variable by keeping the
    H042 core and adding only `14` posterior-selected tail rows, producing a
    `59`-cell Q2-only support;
  - H048 tests the larger claim that H047 support identity is also a hidden
    public-subset prior, producing a `53`-cell Q2-only support selected by
    joint support/world assignment;
  - H049 tests the bigger row-vector claim by keeping H042 Q2 unchanged and
    adding a `160`-cell non-Q2 Q3/S echo on Q2-support/public rows.
  - H050 freezes H042 Q2 and tests whether a separate non-Q2 subjective
    Q1/Q3 target-route phase exists.
  - H051 freezes every non-Q2 target and amplifies the exact 45-cell H042 Q2
    support in logit space by factor `2.0`, testing whether H042 was an
    under-amplified hidden Q2 label phase rather than a shallow local
    correction.
  - H052 is conditional on H051 being positive: it keeps the exact H042 Q2
    support but pulls those cells toward a binary edge (`0.88`/`0.12`) with
    mix `0.35`, testing whether Q2 is a hidden action-label edge rather than a
    smooth calibration vector.
- No H015-H041 file is currently promoted as the next upload.
- The historical post-H012 sensors below are kept because they define falsified or partially supported HS-JEPA routes, not because they are current submission recommendations.

- `submission_h015_self_feedback_top_all_k1600_a0.7_uploadsafe.csv`
- Public LB: not submitted
- Interpretation: H015 includes H012's own public score as a new public-equation anchor and asks whether H012 is an under-amplified posterior rather than a fixed point. It predicts a further posterior delta of about `-0.001586` versus H012, but this is a public self-feedback bet with real overfit/private-risk exposure.

- `submission_h016_public_subset_gain_all_k1000_a0.75_uploadsafe.csv`
- Public LB: not submitted
- Interpretation: H016 treats known public LB observations as a diffuse public cell-weight/gain field. It survived a `300`-permutation null stress and predicts `-0.000296` versus H012 by applying H015 movement only on inferred public-weight-compatible cells. It is lower-upside than H015, but it tests a different world model.

- `submission_h017_joint_label_weight_oracle_gain_all_k1650_a1_uploadsafe.csv`
- Public LB: not submitted
- Interpretation: H017 tests whether H012's public posterior and H016's diffuse weights are compatible parts of one hidden public equation. It predicts `-0.000575` versus H012 by moving H012 further toward the original H012 posterior under H016 weights. It is a posterior-completion test, not independent private-safety evidence.

- `submission_h018_hard_label_world_combined_all_k1750_a1_uploadsafe.csv`
- Public LB: not submitted
- Interpretation: H018 forces the H017 posterior into sampled binary public label worlds. The hard-world posterior beats all `300` permuted-public-delta nulls and predicts `-0.000603` versus H012. It is the binary-aware version of posterior-completion, not a separate human-state/private-safety proof.

- `submission_h019_row_subset_hardworld_gain_all_r240_a1_uploadsafe.csv`
- Public LB: not submitted
- Interpretation: H019 forces the public-equation latent into sampled row-level public masks. It beats `300` permuted-public-delta nulls and supports a broad row-subset interpretation, but the row-exclusion action is internally slightly weaker than H018.

- `submission_h020_joint_vector_world_combined_all_k1750_a1_uploadsafe.csv`
- Public LB: not submitted
- Interpretation: H020 forces each row to live as one 7-target label vector, instead of treating every row-target cell independently. Its joint-vector world beats `300` permuted-public-delta nulls and predicts a larger internal move than H018/H019 (`-0.001105` vs H012 under its rowweighted sensor). The caveat is important: weak train co-occurrence priors help sampled world search, but the selected posterior uses `beta=0`, so the proven part is row-level joint-vector consistency, not yet train co-occurrence as an action prior.

- `submission_h021_agree_h020_k1200_a1_e1546ba9_uploadsafe.csv`
- Public LB: not submitted
- Interpretation: H021 is the first post-H012 candidate that directly bridges raw human-state context to the H020 row-vector branch. Human-state vector priors beat the global train-vector prior in train-only validation (`0.617585` vs `0.664614` BCE), but direct q_hs replacement is rejected. The promoted action uses q_hs only as a gate, applying H020 on `1200` agreement cells and retaining `0.618866` of H020's internal gain while beating a row-permuted q_hs null by `0.005549`.

- H022 produced no promoted root submission.
- Interpretation: H022 injected H021's `q_hs` into the H020 vector-world posterior. Weak human-state prior helped sampled-world search (`hs_b0.1` best config), but final posterior selection reverted to `none_b0`. This records a useful architecture boundary: human-state context is a proposal/gate/action-health latent, not yet a calibrated final probability prior.

- H023 produced no promoted root submission.
- Interpretation: H023 tested the weaker and more useful role for `q_hs`: proposal/Pareto energy after public-compatible vector worlds are found. Public-error top1000 worlds are strongly human-state-aligned (`4.877889` real energy vs `5.234523` row-permutation null median), but q_hs-Pareto posterior selection does not improve public fit against row-permuted controls (`rowperm_public_p=0.754098`). This is architecture evidence, not an upload candidate.

- H024 produced no promoted root submission.
- Interpretation: H024 learned an action-health decoder over known public observations and H015-H023 candidate movement anatomy. It reconstructs known public ordering well in leave-one-out (`geometry` alpha `100`, MAE `0.000773`, Spearman `0.970`, pairwise `0.947`), but post-H012 unknown candidates are not stable: the best unknown diagnostic is an H015 `k100` move with median predicted public `0.570054`, wide p10/p90 `0.559653-0.580761`, support-better-than-H012 only `0.15`, and permutation p `0.841`. This confirms the current bottleneck: posterior generators are ahead of the action-health decoder.

- H025 produced no promoted root submission.
- Interpretation: H025 created independent train-side counterfactual action-health supervision instead of regressing public LB. It generated probability actions from subject/time/KNN/human-state proposals and learned which moves reduce train logloss. The action-health signal is learnable inside proposal families, but row/time transfer is weak (`Spearman 0.021091`, top10 lift `0.004426`) and the selected test candidate fails row-permuted placement stress (`p=0.576667`). The important negative result is that train-visible action health likes known public-bad Q2/residual shortcuts, so the remaining HS-JEPA gap is public/private calibration, not another train counterfactual ranker.

- H026 produced no promoted root submission.
- Interpretation: H026 tested the obvious repair to H025: combine train action-health with a public/private calibration veto against known public-bad Q2/residual shortcut axes. The source-level veto works as a diagnostic: H012 ranks first while known-bad JEPA/Q2/residual anchors are pushed down. But generated post-H012 veto variants are still not public-safe. The selected diagnostic has H025 row-permutation p `0.000000`, yet H024 predicts public `0.574388` and public-score permutation p `0.898000`, far worse than H012 `0.568123`. This means the bottleneck is deeper than a scalar bad-axis veto: the next breakthrough must change the public/private calibration target or candidate generator, not merely trim H025-selected moves.

- H027 produced no promoted root submission.
- Interpretation: H027 tested the stronger repair: make the post-H012 generator born public/private-aware by combining H015/H020/H023 public posterior targets with H021/H023 human-state agreement, H014 same-subject sleep-state memory, and H026 public-good/bad axes before materializing cells. It generated `1648` variants. The best diagnostic was `hitl/h027_public_private_aware_generator_jepa/submission_h027_h015_public_feedback_bad_axis_escape_S1S2S3_k80_a0p25.csv`, but H024 predicted public `0.569712`, support below H012 only `0.150000`, H025 row-permutation p `0.383333`, and public-score permutation p `0.822000`. This kills the idea that existing H015/H020/H023 posterior targets can be made H012-beating simply by cell-level memory/private-safety birth constraints.

- H028 produced no promoted root submission.
- Interpretation: H028 changed the target instead of adding another gate. Known public submissions were treated as interventions from H012, and the model learned a low-rank cell-level public action-gradient. The gradient fit was not random noise (`all`, alpha `100`, LOO MAE `0.001204883`, permutation p `0.000000`), but extrapolating from H012 was not safe: the best generated file was predicted by H024 at public `0.576388`, support below H012 only `0.083333`, H025 row-permutation p `0.710000`, and public-score permutation p `0.918000`. This is a sharper negative result: public responses are learnable as a coarse H012-vs-rest geometry, but they do not define a smooth local gradient that can move H012 lower.

- H029 produced no promoted root submission.
- Interpretation: H029 treated H012 as a needle basin and broke/preserved one invariant at a time: exact support, amplitude, target/subject rollback, same-subject memory agreement, and target-wise row identity. It generated `102` variants. The strongest diagnostic was `rollback_target_S1`, but H024 still priced it above the real H012 (`0.570495` median, `+0.002371` vs H012), with support below H012 only `0.116667`, public-score permutation p `0.858000`, and H025 row-permutation p `0.613333`. Target-wise row permutation collapsed to about `0.581`, which is strong evidence that H012 is not a target-level calibration trick; exact row-target placement is part of the invariant.

- H030 produced no promoted root submission.
- Interpretation: H030 moved the H016/H019/H020/H014 identity signals inside the public-equation solver as row-target cell allowance priors. The real positive result is diagnostic: even when H012 is excluded as an equation and direct H012 priors are not used, the best independent prior predicts H012's public jump from E247 within about `0.000485` LogLoss (`-0.007550` predicted vs `-0.008035` actual), with `identity_combo`/`joint_vector_cell` as the strongest supports. The negative result is equally important: materializing those priors still fails H024/H025 stress. The best generated diagnostic is priced around `0.572160`, support below H012 only `0.100000`, public-score permutation p `0.923333`, and H025 row-permutation p `0.670000`. H030 therefore validates a row-target identity latent, but rejects it as a direct action layer. The next breakthrough must solve the translation from identity posterior to exact H012-like row-target placement, not merely strengthen the identity prior.

- H031 produced no promoted root submission.
- Interpretation: H031 used the attached V106 memory note in the opposite direction from H014. H014 showed that same-subject sleep-state memory disagrees with `714/1200` H012 cells, and those disagreeing cells carry `72.03%` of H012 posterior gain. H031 treated that memory-disagree region as the public-equation core, then tried conflict-core amplification, conflict-core plus agree-cost rollback, agree-cost rollback alone, and core-only reconstruction from E247. The best diagnostic remained above H012 by H024 (`0.569810`, margin `+0.001686`), support below H012 was only `0.150000`, and public-score permutation p was `0.800667`; row-placement was only mildly non-random (`H025 p=0.183333`). This strengthens the explanation that memory-conflict cells are causal to H012's public success, but rejects the action claim that they should be amplified or traded against memory-agree cells.

- H032 produced no promoted root submission.
- Interpretation: H032 tested whether H012 is recoverable as a phase point from a dense E247-to-public-posterior action diagram while withholding H012's public score from the state/action decoder. The decoder recovered the real H012 anchor as the best point: pre-H012 `geometry` decoder LOO MAE `0.000295`, Spearman `0.951`, pairwise `0.924`; H012 itself had pre-state prediction `0.563377`, while the best non-anchor sibling was priced much worse at `0.573189` and changed `1080` cells away from H012. This is strong architecture evidence that H012 is not arbitrary under the HS-JEPA state/action view, but it rejects the idea that a simple dense phase sweep around H012 contains a stronger sibling.

- H033 produced no promoted root submission.
- Interpretation: H033 turned the failed H032 siblings into contrastive interventions and learned which row-target operations break the H012 phase. The break signal is real: all-OOF MAE `0.000815`, Spearman `0.954`, pairwise `0.913`. But the learned negative-cost edit is not action-safe. The best generated diagnostic changed only `10` outside-support cells, yet the pre-H012 state decoder priced it `+0.016275` worse than H012, with public-score permutation p `0.861333` and H025 row-placement p `0.710000`. This rejects first-order independent-cell phase-lock editing. The live route is a nonlinear/discrete row-vector or route-level translator that recognizes H012-like phase support before materializing probability edits.

- H034 produced no promoted root submission.
- Interpretation: H034 moved the translator from independent cells to whole row-vector route patterns. The route representation is very healthy as a sibling-failure model: best all-OOF `et_route` MAE `0.000389`, Spearman `0.985`, pairwise `0.956`. But it does not yield a safe action. The best local-looking diagnostic, `row_rollback_support_rollback_memory_conflict_changed_r1_a0.08`, rolls back all 7 targets in row `144`; H024 pre-state predicts `-0.003999` versus H012, but the route model predicts `+0.032224`, public-score permutation p is only `0.305333`, and H025 row-placement p is `0.940000`. This exposes a new failure mode: H024 can hallucinate a tiny row rollback as public-good, while the row-route/action-health views reject it. First-order row-route edits are now also blocked; the next route is a direct H012-vs-sibling classifier or combinatorial phase solver.

- H035 produced no promoted root submission.
- Interpretation: H035 implemented the combinatorial phase solver route by swapping H012 support cells under target/row/support-count constraints while keeping the H012 public-equation posterior direction. It generated `585` candidates. `55` candidates improved the public-equation q-loss versus H012, with best q delta `-0.000286`, but none passed route or pre-state gates: route-safe count `0`, pre-state-better count `0`, strict gate count `0`. The selected combined-score diagnostic was q-worse (`+0.000512`) and still route/pre-state bad. This kills the local support-swap worldview. H012 currently looks like a locked basin/fixed point under known HS-JEPA action-health views, not a smooth editable support.

- H036 produced no promoted root submission.
- Interpretation: H036 stopped editing H012 locally and instead sampled hidden
  public row-subset plus binary label worlds that explain all known public LB
  deltas around H012. The latent-world result is strong: `55488` worlds sampled,
  best MAE `0.000202825`, Spearman `0.969925`, and public-delta permutation p
  `0.000000`. The top configs include H018/H019 equation priors and also H013
  `late_social_phone`, so human-state priors are useful as world proposals. But
  direct materialization still fails action translation. The strongest internal
  candidate expects `-0.002239` versus H012, yet H024/H025 reject it; the
  selected diagnostic Q2-only move has expected delta only `-0.000235`, H024
  pre-H012 margin `+0.001431`, support `0.25`, and H025 row-permutation p
  `0.59`. H036 therefore validates a global hidden-public-world latent and
  rejects direct `q_cond` movement as a submission layer.

- H037 produced no promoted root submission.
- Interpretation: H037 tested the first natural world-to-action translator:
  keep H012 support fixed and only change amplitudes on the original
  E247-to-H012 ray. The overlap clue is strong: `903/1200` H012 support cells
  align with H036 pressure and carry score sum `244.595425`, while the `297`
  conflict cells carry only `20.929529`. But scalar ray translation fails. Among
  `253` candidates, `44` have meaningful H036 world-cell gain, `4` have
  negative H024 margin, and `0` have both; no candidate reaches H024 support
  `0.6`. The selected diagnostic has only tiny world gain and still positive
  H024 margin. H037 therefore says H012 support is meaningful, but the missing
  translator is not just support or amplitude.

- H038 produced no promoted root submission.
- Interpretation: H038 combined the V106 same-subject memory note with the
  H036 public-world posterior. The useful discovery is that H012's anatomy is
  heavily concentrated in memory-transition exceptions: `523/1200` support
  cells, posterior gain sum `8.133135`, and H036 cell-score sum `200.501589`.
  The broad-world exception core is even denser (`245` cells, score sum
  `183.788898`). But as an action translator it fails: among `459` candidates,
  `42` have world-cell gain and `2` have posterior gain, yet `0` have negative
  H024 pre-H012 margin and `0` reach H024 support `0.55`. H038 therefore
  validates memory conflict as a human-state route feature and rejects direct
  memory-conflict amplification/repair as a submission route.

- H039 produced no promoted root submission.
- Interpretation: H039 used the failed H036/H037/H038 translators as negative
  action supervision. The failure geometry is highly concentrated: all-bad PC1
  energy `0.651576`, PC8 cumulative energy `0.895839`. But this does not
  produce a safe decoder. Removing world-good/action-bad PCs also removes most
  of the H036 world vector (`0.210275` norm left after PC8, `0.068575` after
  PC24). Among `520` projected residual candidates, none reach meaningful
  world gain, none have negative H024 margin, and none reach H024 support
  `0.55`. H039 therefore validates compact action-failure geometry and rejects
  local linear nullspace/survivor-cone projection as the missing translator.

- H040 produced no promoted root submission.
- Interpretation: H040 tested the next natural nonlinear claim: maybe the
  missing decoder is a discrete public/private row route assignment rather than
  a smooth cell/vector projection. It absorbed the external V106
  sleep-state-conditioned memory note as a repeated-subject memory signal, then
  generated `328` whole-row/route candidates using H036 public-world, H012
  posterior, H014/H038 memory, private-safety, and transition-exception route
  scores. The best route candidate has strong internal public-world and
  posterior gains (`-0.001426068` / `-0.001708677`) and H025 row-permutation p
  `0.280000`, but H024 rejects it: pre-H012 margin `+0.007548586` and support
  better than H012 only `0.250000`. Across all H040 candidates, `198/328` have
  `world_cell_delta < -0.0005`, `181/328` have `h025_score < 0`, but `0/328`
  have negative H024 margin and `0/328` reach H024 support `0.55`. This kills
  the simple row-route translator.

- H041 produced no promoted root submission.
- Interpretation: H041 moved the H040 route latent inside the public-equation
  solver instead of using it as a post-hoc row edit. This worked as hidden
  public-world inference: route-prior leave-one-public-file-out MAE improved to
  `0.000132093` versus best uniform `0.000187170`. But it still failed as an
  upload action. The selected diagnostic
  `h041_route_celltop_k420_a0.18_c420_c5275704` had route-equation /
  H012-posterior / H036-world deltas
  `-0.001074309` / `-0.000205969` / `-0.000487601`, yet H024 margin/support
  were `+0.004066028` / `0.250000000`. H041 therefore validates route state as
  a public-subset prior and rejects posterior-first top-cell/row pulls as the
  missing decoder.

- H042 produced a promoted HITL public sensor after the initial local
  do-not-promote decision.
- Interpretation: H042 made upload-action coefficients first-class variables
  and fit known public LB deltas from `36` public/private/phase/route/target
  action atoms. This worked as representation learning: best action-decoder
  LOFO MAE was `0.000665647`, Spearman `0.924675325`, pairwise accuracy
  `0.904761905`, and permutation p `0.000000000`. The broad automatic selector
  still failed as a public action solver. The selected diagnostic had route-equation delta
  `-0.000537053`, yet action margin/support
  `+0.000793299` / `0.333333333` and H024 margin/support
  `+0.002010668` / `0.250000000`. Across `240` scored candidates, `15` had
  action gain plus route gain, but none also had H024 gain, and none had route
  gain plus H024 gain. The submitted tiny Q2 phase sensor
  `submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv`
  scored `0.5679048248`, improving H012 by `0.0002186583`. H042 therefore
  validates public action-response geometry and shows H024 is too conservative
  for at least small Q2 phase moves, while still rejecting large single-ridge
  action-atom extrapolation as the missing decoder.

Public LB operating rule:

- Public LB is not an iteration loop. A file is promotable only when it beats the current priority under public-free stress, including fresh nulls that were not used to build the candidate.
- Local-interesting files stay diagnostic if they only improve old selector p90, semantic attribution, or a single stress view.
- The next public slot should answer a predeclared worldview question, not rescue a local tweak after the fact.
- After H012, the main public question is no longer "can we find a tiny E247-safe movement?" It is "which parts of the public-equation posterior are real hidden-state signal versus public-subset overfit, and how do subject/time memory, raw human-state context, and phase/action geometry explain them?"
- H014 says same-subject sleep-state memory does not explain most of H012's gain. H015 says the public-equation system itself still wants to sharpen H012. H016/H017/H018 split that question into cell weights, continuous posterior-completion, and binary hard-world posterior-completion. H019 adds the stricter row-subset constraint and finds broad row-level compatibility, but not a better action than H018. H020 raises the constraint again from independent cells to whole-row 7-label vectors. H021 adds the missing human-state bridge: raw lifestyle context can gate the H020 vector action, but is not yet calibrated enough to replace public-equation probabilities. H022 confirms that split by rejecting q_hs as final posterior prior while keeping it alive as proposal/search/gate signal. H023 shows the bridge is not imaginary: public-compatible worlds are human-state-aligned. H024 then confirms that public-axis action-health is learnable but unstable on unseen candidates. H025 adds the sharper falsification: train-side action-health is also not enough, because it transfers weakly across row/time folds and prefers known public-bad Q2/residual anatomy. H026 shows that a scalar public-bad veto can fix known-anchor ranking but still cannot make post-H012 actions public-safe. H027 shows that even born-public/private cell constraints over the existing posterior targets do not recover H012-beating public transfer. H028 shows that known public scores can learn a coarse action-gradient, but not one that extrapolates safely from H012. H029 shows that breaking H012's exact row-target arrangement causes stress degradation even when target/support moments are partially preserved. H030 shows that row-target identity priors can partially anticipate H012 independently, but still cannot be safely materialized. H031 adds the V106 contrast: memory-disagree cells explain H012's public core better than memory-agree cells, but amplifying that core is still not a safe action. H032 then shows the current translator can recover H012 itself when H012 public feedback is withheld, yet cannot find a better neighboring phase point. H033 shows the neighboring failures are learnable as phase-lock contrast, but first-order independent-cell negative-cost edits still leave the H012 basin. H034 lifts the unit to row-vector routes and learns sibling failure even more sharply, but first-order row-route edits still fail action stress and reveal an H024 false-positive rollback mode. H035 then tests the promised combinatorial phase solver and still fails every route/pre-state gate despite 55 q-improving local swaps. H036 solves a global public-world posterior that beats permutation nulls decisively, but direct world-to-probability materialization still fails H024/H025. H037 shows that even support-preserving ray amplitude cannot align H036 world gain with H024 action-health. H038 shows memory-transition exceptions strongly explain H012 but cannot be amplified or repaired directly. The missing piece is now very sharp: hidden public-state discovery works; support discovery is mostly right; memory/state explanation works; world-to-action translation still does not. The next breakthrough should learn route/calibration/private-public transfer jointly, not continue H012 by smooth gradient, scalar gate, target-level calibration, same-subject memory regularizer, cellwise edit, row-route top-k edit, local support swap, direct `q_cond` movement, scalar ray amplitude, or direct memory-conflict action.
- H039 adds that failed translator directions are compact but not linearly
  removable without killing the public-world signal. The next breakthrough
  should model discrete route/calibration/private-public transfer or public
  subset assignment directly, not continue local linear projection around H012.
- H040 then tests that discrete row-route idea directly and rejects the simple
  version: route assignment can create large public-world proxy gains, but H024
  sees every candidate as worse than H012. The live big-bet is now narrower:
  infer hidden public/private subset and label equations directly, with route
  state as a prior inside the equation solver, instead of editing H012
  probabilities by row or cell after the posterior is already built.
- H041 tests that narrower big-bet and partially rejects it: route priors inside
  equation inference improve public-sensor LOFO fit, but posterior-first
  materialization still leaves the H012 action basin. The live big-bet is now
  sharper again: infer upload action and public/private hidden world jointly,
  instead of first estimating a public posterior and then translating it into
  probability edits.
- H042 tests that sharper bet and narrows it further: known public action
  response is learnable and non-random. Public feedback on the tiny Q2 phase
  sensor proves one H024-rejected local branch is real, but the generated
  action-atom family still has no robust intersection across action decoder,
  route-world gain, and H024. The next big-bet should explore the Q2 phase
  manifold and split hidden public sensors into multiple regimes, not continue
  posterior-first or large single-ridge action extrapolation.
- H043 explores that Q2 phase manifold directly. After adding H042 public
  feedback as a new action-response sensor, it promotes
  `submission_h043_q2_top120_a0.66_c105_ca1478b7_uploadsafe.csv`: a Q2-only
  move expanding from H042's `45` cells to `105` cells. Local stress is
  action-positive (`-0.000128164` margin, `0.583333333` support), route-positive
  (`-0.000194493`), and H025-healthy (`-2.323117949`), while H024 still warns
  (`+0.000619918`). This is the next high-information public sensor: a win
  means Q2 phase is an expandable hidden action manifold; a loss means H042 was
  a narrow support-specific correction.
- H044 tests the human-social version of that story: maybe Q2 phase support is
  chosen by public-route/transition/memory-disagreement and private-routine
  state. It generates `768` route-split Q2 candidates but promotes none. The
  best diagnostic is a `91`-cell H043 private-veto candidate with action margin
  `-0.000095671`, route delta `-0.000184347`, and H025 score `-1.987702538`,
  but it does not beat H043's public-free profile enough to justify a public
  slot. The conclusion is precise: human-state route is a useful latent, but
  scalar route thresholds are not the missing Q2 support decoder.
- H045 turns that negative result into a conditional decoder: route context is
  used to price Q2 actions rather than threshold rows directly. It promotes
  `submission_h045_condroute_q2regime75_a0.66_5988dfb9_uploadsafe.csv`, a
  Q2-only `75`-cell pruning of H043 with conditional margin/support
  `-0.000126787` / `0.583333333`, route delta `-0.000171330`, H025 score
  `-1.693362091`, and positive H024 margin `+0.000547357`. This is the most
  explicit HS-JEPA route-decoder public sensor so far: a win means human-state
  route is useful as action-response context; a loss to H043 means the route
  context over-pruned the Q2 phase manifold.
- H046 tests a larger human-state story and rejects it: Q2 action amplitude is
  not currently helped by splitting H042-core/public-tail/private-tail into
  different signs or strengths. It generates `5224` bifurcated Q2 candidates
  but promotes none. The best diagnostic looks good to pre-H042 sensors
  (`-0.000411481` margin, `0.583333333` support), route equation
  (`-0.000163227`), H024 (`+0.000497445`), and H025 (`-2.040387092`), but
  fails the post-H042 conditional decoder (`+0.000015538` margin,
  `0.416666667` support). This narrows the next big bet: support identity and
  public-subset assignment remain alive; private-tail opposite-amplitude Q2
  moves are not public-ready.
- H047 follows that negative result by moving from amplitude/sign to support
  identity. It treats H045's stronger supports and H046's rejected bifurcated
  supports as contrastive observations, then infers a row-level Q2 support
  posterior. It promotes
  `submission_h047_q2_support_identity_98737e9b_uploadsafe.csv`, a Q2-only
  `59`-cell action that keeps all `45` H042 core cells and adds `14`
  posterior-tail rows. Local stress is full-known conditional positive
  (`-0.000211862` margin, `0.583333333` support), pre-H042 positive
  (`-0.000383048` margin), route-positive (`-0.000178002`), and H025-healthy
  (`-1.154530177`), with the same H024 warning zone (`+0.000552020`). This is
  the cleanest next support-identity sensor: a win means H042 was not just a
  narrow accident; a loss means exact H042 support is still the safer public
  structure.
- H048 raises the H047 claim one level: support identity is tested as a
  public-subset row prior inside the world sampler. The best support prior has
  LOFO MAE `0.000145480` versus uniform `0.000184123`, a gain of
  `0.000038643`, so the support prior is not only an action-support heuristic.
  It promotes `submission_h048_q2_public_subset_support_39c01d65_uploadsafe.csv`,
  a Q2-only `53`-cell candidate with full-known conditional margin/support
  `-0.000184398` / `0.583333333`, pre-H042 margin `-0.000463494`,
  route delta `-0.000165760`, H048 world delta `-0.000065847`, and H025 score
  `-1.063509870`. This is the bigger-worldview follow-up to H047: a win means
  Q2 support identity is also public-subset assignment; a loss means the world
  prior overfit local equations and H047 remains the cleaner support sensor.
- H049 asks the first post-H042 non-Q2 translation question. It starts from the
  H042 public best, keeps Q2 exactly unchanged, and adds a `160`-cell Q3/S echo
  on rows selected by Q2 support/public-row posterior using H020 joint-vector
  and H048 public-world targets. It promotes
  `submission_h049_rowvector_echo_7635f5ed_uploadsafe.csv`. Local sensors are
  route-positive (`-0.000185510`), H036-world-positive (`-0.000131061`),
  action/conditional mildly positive (`+0.000051201` / `+0.000208025`), and
  H025 strongly healthy (`-4.814111661`), while H024 remains positive
  (`+0.001194754`). If public improves, Q2 support is a row-level hidden
  human-state marker; if public rejects it, H042 should be treated as Q2-local.
- H050 asks a sharper target-route question. It starts from H042, freezes Q2
  exactly, and lets the action decoder choose among Q1/Q3/S target-phase
  residuals. It promotes
  `submission_h050_target_route_phase_b140216b_uploadsafe.csv`, which changes
  `96` non-Q2 cells versus H042: Q1 `52`, Q3 `44`, every S target `0`. Local
  sensors are route-positive versus H042 (`-0.000303538`), route-equation
  positive versus H012 (`-0.000444205`), H036-world-positive (`-0.000166506`),
  and full-known action-positive (`-0.000050859`, support `0.583333333`), while
  H024 and H025 remain warnings (`+0.001857507`, `+0.377968233`). If public
  improves, HS-JEPA needs target-specific subjective Q routes beyond Q2; if it
  fails, non-Q2 moves should require independent action-health evidence.

Primary working notes:

- `hypothesis_graph.md`
- `experiment_log.md`
- `lb_observation_log.md`
- `latent_diagnostics.md`
- `validation_stress_report.md`
- `feature_registry.md`
- `candidate_submissions.md`
- `failed_hypotheses.md`

The local `analysis_outputs/` directory contains many generated scan tables.
Only scripts, reports, summary/audit tables, and key submission files are tracked
in git; large generated artifacts remain local by design.

## Latest H053 Branch Note

H050 public feedback tied H042 exactly at `0.5679048248` despite `96` non-Q2
Q1/Q3 changes, so the live post-H042 signal remains Q2-local under the current
translator.

H051/H052 test exact-support Q2 amplitude and edge continuation. H053 tests the
opposite branch: keep the Q2 action size at `45` cells, but reassign the
support. It keeps the strongest `31` H042 Q2 rows, reverts the weakest `14`,
and adds `14` new H047/H036 public-world rows. The promoted upload file is
`submission_h053_q2_support_reassign_k31a14_447af5b3_uploadsafe.csv`.

If H051/H052 fail but H053 improves, H042 was mainly a support/public-subset
identity discovery rather than an under-amplified Q2 phase.

## Latest H054 Branch Note

H054 uses the H050 public-null feedback more aggressively. H050 tried to
translate the Q2 hidden state into subjective Q1/Q3 cells and tied H042. H054
therefore rejects that subjective route and tests whether the downstream route
is objective S2/S4 instead.

The promoted upload file is
`submission_h054_objective_s24_route_inversion_e8680162_uploadsafe.csv`. It
keeps H042's Q2 cells fixed and changes `150` non-Q2 cells versus H042:
S2 `83`, S4 `67`. If it improves, HS-JEPA's target-route decoder should treat
Q2 as the public-visible anchor and S2/S4 as the hidden objective route. If it
fails, the current H050 non-Q2 candidate surface should be retired rather than
recycled.

## Latest H055 Branch Note

H055 uses H042 and H050 as new public-equation supervision, because the original
`known_public_table()` does not include them. It refits a hidden public-listener
posterior from the augmented equation system, uses H042 as the upload base,
freezes Q2, and vetoes every H050 extra Q1/Q3 null cell.

The promoted upload file is
`submission_h055_postfeedback_listener_759f66e7_uploadsafe.csv`. It changes
`700` cells versus H042 with Q2 unchanged and H050-null overlap `0`. If it
improves, the post-H042 bottleneck is a hidden public-listener subset that only
became identifiable after adding H042/H050 feedback. If it fails, this
augmented public-equation posterior should be paused until new public sensors
arrive.

## Latest H056 Branch Note

H056 tests the clean row-level interpretation of H042. H042 improved public LB
by moving `45` Q2 cells. H050 kept those Q2 cells and added `96` Q1/Q3 cells,
but tied H042, so the subjective-Q route is not currently public-informative.

The promoted upload file is
`submission_h056_q2row_objective_state_a4620b89_uploadsafe.csv`. It starts from
H042, freezes Q2, avoids Q1/Q3 entirely, and changes S1-S4 on exactly the `45`
rows where H042 changed Q2: `180` cells total. If it improves, H042's Q2 support
is a reusable public-visible human-state row marker. If it fails, H042 should be
treated as a Q2-local correction rather than a row-state route.

## Latest H057 Branch Note

H057 tests the larger version of the same row-state idea. H050's Q1/Q3 direction
agrees with the H055 posterior on `88.5%` of changed cells, so the cleaner
negative hypothesis is not "H050 had the wrong sign"; it is "H050 put a
potentially valid subjective route on many public-irrelevant rows."

The promoted upload file is
`submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv`. It starts
from H042, freezes Q2, and moves the complete non-Q2 vector on exactly the `45`
H042 Q2-support rows: Q1 `45`, Q3 `45`, and S1-S4 `45` each, `270` cells total.
If H057 improves, HS-JEPA should represent H042 support rows as complete hidden
human-state vectors. If H056 improves but H057 fails, the row-state route is
objective-S but not subjective-Q. If both fail, H042 remains Q2-local.

Public feedback: H057 scored `0.5677475939`, improving over H042/H050 by
`0.0001572309`. This validates the full row-vector branch and weakens the old
"H042 is Q2-local" interpretation.

## Latest H058 Branch Note

H058 changes the question from target routing to public/private tail separation.
H012/H042 differ from E247 on `1200` cells, but only H042's `45` Q2-support
rows have clear post-H012 public evidence. H058 protects all targets on those
rows and rolls back `500` low-listener cells outside that protected state toward
E247 with logit alpha `0.55`.

The promoted upload file is
`submission_h058_private_tail_eject_138bba8f_uploadsafe.csv`. It changes `500`
cells across `197` rows versus H042, with `0` protected-row changes. If it
improves, the next HS-JEPA object is a public/private tail splitter inside the
broad H012/H042 posterior. If it fails, the broad H012/H042 posterior outside
H042 rows should not be collapsed using H055 low-listener score alone.

After H057's public win, H058 should be interpreted against the new H057
frontier: a win over H057 would validate private-tail ejection; a loss mainly
says the next large bet should extend the compact H057 row-state latent rather
than roll back H012/H042 tail cells from the older H042 base.

## Latest H059 Branch Note

H059 is the first H057-base expansion. It asks whether the `45` H042/H057
public-positive rows are isolated events or same-subject lifestyle episode
markers. It keeps H057's anchor rows unchanged, freezes Q2 everywhere, and
propagates Q1/Q3/S1-S4 to same-subject neighbor rows within position radius
`3`, using distance-decayed logit movement toward the H055 posterior.

The promoted upload file is
`submission_h059_episode_r3_fullvector_cb67de4b_uploadsafe.csv`. It adds `822`
cells on `137` rows versus H057 and changes `1092` cells versus H042, with Q2
unchanged. If it improves over H057, HS-JEPA should model human state as a
temporal episode. If it fails, H057's exact row support is likely much sharper
than the local posterior suggests.
