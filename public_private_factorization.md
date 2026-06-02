# Public/Private Hidden-State Factorization

Last updated: 2026-06-02

## Problem

The current best public score, `0.5677475939`, is far from 0.53. H012 proved
that known public LB observations can be inverted into an action-grade hidden
public state, but H012 does not prove that the same state is private-safe.

The core question:

```text
What part of the public-equation latent is invariant human state,
what part is public subset bias,
and what part is shortcut or calibration luck?
```

## Evidence That Public State Exists

1. H012 moved from E247 `0.5761589494` to `0.5681234831`, an improvement of
   `0.0080354663`.
2. H012 was designed as public-equation latent reconstruction, not as a normal
   tabular model improvement.
3. H032 withheld H012's public score from the decoder and still recovered H012
   as the best phase point, with strong pre-H012 geometry diagnostics.
4. H057 showed that a Q2 support row can carry a full non-Q2 row-state vector,
   improving H042 by `0.0001572309`.

Interpretation: public LB is a sensor for hidden state. The signal is not just
noise or a leaderboard accident.

## Evidence That Direct Public State Is Not Enough

1. H015-H020 posterior-completion variants looked internally strong but were
   not promoted as public-safe.
2. H026-H027 showed that train action-health and public-bad vetoes did not make
   existing posterior targets safe.
3. H028 learned a public action-gradient, but extrapolating around H012 was
   unsafe.
4. H029 showed that H012 support and row-target placement are locked; target
   permutation can collapse toward bad-public territory.
5. H033/H034 learned sibling failure structure well, but first-order cell and
   row-route edits were not action-safe.

Interpretation: public-equation latent is real, but translating it into a new
submission requires a separate public/private and action-health layer.

## Working Decomposition

For each row-target cell:

```text
delta_logit =
  invariant_human_state
  + public_listener_state
  - shortcut_state
  + calibration_residual
```

Where:

- `invariant_human_state`: should be visible from raw/human context, subject
  episode, target dependency, and train-side behavior.
- `public_listener_state`: explains known public LB response but may not
  generalize.
- `shortcut_state`: aligns with known public-bad anchors or null moves.
- `calibration_residual`: small log-loss sensitive correction, not a large
  hidden-state discovery.

0.53 requires increasing `invariant_human_state`, not just amplifying
`public_listener_state`.

## Current Factor Status

| Factor | Evidence | Status |
| --- | --- | --- |
| Public listener state | H012, H032, H068 fit | Strong |
| Compact row-state | H042, H057 | Strong but small |
| Human-context invariant | H063/H064 pending | Unconfirmed |
| Sequence/episode invariant | H065/H066 pending | Unconfirmed |
| Action-health field | H068 pending | Promising but high-risk |
| Shortcut state | H010, E216, E323, bad JEPA, H050-null | Strong negatives |
| Anti-shortcut inverse | H074 bad-opposition null z `9.270846` | Real representation, action not solved |
| Anti-bad value transport | H075 inverse movement field | Weak as direct decoder |
| Private-safe state | Needed for 0.53 | Not solved |
| Human-social state | H072 story families recover H068 rows but not H071 routes | Context/action-health layer, not direct route layer |
| Human-action bridge | H073 story+route context predicts continuous health/shortcut | Useful representation, not yet 0.001 action solver |

## H069 Result

H069 materialized the first explicit public/private factorization layer:

```text
action_score =
  public_score
  + invariant_score
  - shortcut_score
```

It used H068 as the public/action-health view, H063/H064/H067 as invariant
context and row-state views, and `8` known bad anchors as shortcut views. The
selected file is:

```text
submission_h069_public_private_factor_4ffd6cd6_uploadsafe.csv
```

Observed public-free facts:

- selected profile: `anti_shortcut_all_k360_a1p0_logit_mp0p54_mi0p48_xs0p72`;
- changed cells versus H057: `268`;
- changed rows versus H057: `97`;
- Q2 changed cells: `36`;
- public-action predicted delta versus H057: `-0.000586`;
- posterior delta versus H057: `-0.000488`;
- mean invariant score: `0.654291`;
- mean shortcut score: `0.108668`;
- overlap with H068 changed cells: `250/268`;
- new cells outside H068: `18`.

Interpretation: public/private factorization is implementable and produces a
cleaner action field, but the strict invariant-plus-anti-shortcut gate prunes
the H068-scale movement. This does not kill public/private factorization. It
does kill the simpler sub-hypothesis that "filter H068 harder and keep
`0.001`-scale upside" is enough. The next route should use these factors inside
a joint decoder or assignment solver instead of another H069 threshold sweep.

## H071 Factorization Use

H071 used H069 as a factor view rather than as a hard gate. This matters
because the promoted H071 candidate changes `642` cells outside H069 while
still keeping bad-anchor positive cosine at `0.0`.

Interpretation: H069's public/private/shortcut scores are useful as energy
terms, but if H071 wins, the factorization layer should be subordinated to a
route-assignment decoder. If H071 loses badly, the H069 factors may be
descriptive but not action-grade outside the strict H069 support.

## H072 Human-Social Factor Use

H072 tested whether human-social story families can act as a direct route prior
for H071 assignments. The answer is currently mixed:

- positive: bedtime arousal, cashflow stress, nocturnal awake, and bad-night
  aftereffect recover H068 action-health rows with AUC around `0.697-0.720`;
- negative: story-family route support does not rediscover H071 routes above
  subject-preserving nulls (`0.776796` real vs `0.783463` null, z
  `-1.326523`).

This narrows the factorization:

```text
human-social state -> action-health / shortcut risk -> assignment
```

is more defensible than:

```text
human-social state -> assignment
```

The next private-safe route should therefore use stories as an intermediate
health/shortcut view, not as a direct public/private row-route separator.

## H073 Human-Action Bridge Factor Use

H073 implemented the H072 follow-up by making the human-social layer predict an
intermediate action-health representation before assignment:

```text
C_human + C_route
  -> z_action_health / z_shortcut
  -> z_assignment
  -> correction field
```

The selected candidate,
`submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv`, is upload-safe
and changes `657` cells on `141` rows, but its predicted public-action movement
is only `-0.000618` versus H057. That is below the current `0.001` big-bet
threshold.

The factorization evidence is still useful:

- story-only hard selected-cell prediction is weak under subject-group OOF
  (`0.513105` AUC on H068 selected cells);
- story plus route context predicts continuous H068 action-health with OOF
  Spearman `0.890901`;
- the same continuous bridge scores H071 selected cells at AUC `0.860064`;
- story plus route context also predicts shortcut energy with OOF Spearman
  `0.801446`.

Interpretation: the human-social factor is not a reliable public/private
separator by itself. It is better modeled as a continuous action-health and
shortcut-risk view. In HS-JEPA terms, this means `z_human_action` should feed
the assignment solver as an energy term, not replace the assignment solver.

This weakens another direct human-story route sweep. It strengthens H074-style
anti-shortcut inversion or a future assignment solver that treats human context
as a regularized bridge between public listener state and private-safe action
state.

## H074 Anti-Shortcut Factor Use

H074 tests whether shortcut state can be inverted into a positive target, not
just subtracted as a veto:

```text
public-bad movement vectors
  -> same-direction shortcut energy
  -> opposite-direction anti-shortcut energy
  -> row-target route assignment
```

The selected candidate,
`submission_h074_antishortcut_inversion_816703df_uploadsafe.csv`, changes
`597` cells on `152` rows. It is deliberately broader than the top pure
negative-space candidate because the goal is to test a world model, not preserve
a local threshold. The cleanest evidence is not the file score estimate but the
negative-control result:

- top-520 `mean_true_opp_rank`: real `0.724689`, null `0.650047`, z
  `9.270846`;
- top-520 `mean_true_same_rank`: real `0.279030`, null `0.360904`, z
  `-10.261358`;
- top-520 `mean_shortcut_energy`: real `0.188419`, null `0.250843`, z
  `-12.247887`;
- top-520 `mean_cell_gain`: real `0.002331`, null `0.001996`, z `3.050342`.

Interpretation: bad submissions expose a real public/private boundary. They
are not merely "files to avoid"; they define a contrastive HS-JEPA target
representation. The unsolved part is action translation. H074's broad sensor
has public-action predicted delta `-0.000840`, below the `0.001` gate, so
`z_anti_shortcut` should feed the next assignment solver rather than be treated
as a finished public/private solution.

## H075 Anti-Bad Value-Transport Result

H075 tested a stronger claim:

```text
if a bad submission moves in a shortcut direction,
then the inverse of that movement is the correct probability transport field
```

This is not supported by the current evidence. The selected diagnostic,
`submission_h075_antibad_transport_f6863945_uploadsafe.csv`, is upload-safe
and broad enough to be a real sensor (`524` changed cells on `152` rows), but
its public-action predicted delta is only `-0.000766`. Across all generated
H075 candidates, none reached `-0.000800` predicted public-action delta.

Interpretation: bad-anchor geometry is useful for separating public/private
support, but not for assigning final values. The factorization should be:

```text
bad worlds -> shortcut / anti-shortcut energy
not
bad worlds -> final probability movement
```

This narrows the next private-safe route. Keep `z_anti_shortcut` as a support
constraint or energy term; find the value decoder from route-specific
public-action response, label-world constraints, or another latent target.

## H069 Candidate Design

The next public/private factorization experiment should not produce another
H057 local variant. It should produce a factorized correction field.

### Context

- positive public state: H012, H042, H057, H068 q/action-health;
- positive invariant context: H063 story/raw context, H064 contrastive graph,
  H065/H066 episode/transition maps;
- negative shortcut context: H010 objective-route failure, E216 mask-family
  failure, E323 null-common failure, bad JEPA latent residuals, H050-null rows;
- calibration context: target priors and Q/S dependency only as low-weight
  health checks.

### Target

Predict three scores per row-target cell:

```text
public_score
invariant_score
shortcut_score
```

Then materialize:

```text
action_score = public_score + invariant_score - shortcut_score
```

Only cells with positive `public_score`, positive `invariant_score`, and low
`shortcut_score` should move.

### Stress Tests

- leave-one-public-observation out;
- leave-one-submission-family out;
- H050-null exclusion;
- bad-anchor cosine;
- row permutation;
- target permutation;
- H057 support preservation;
- H012 support non-collapse;
- no broad all-target move.

## Public Interpretation Rules

If a factorized candidate improves by at least `0.001`:

- public/private factorization becomes the primary HS-JEPA route;
- human/context or action-health factors used in the winner become paper-grade
  evidence.

If it is neutral:

- public state may already be close to a fixed point;
- factorization helped risk but not score;
- next step should be row-target assignment, not more factor weighting.

If it loses badly:

- current public-state inversion is not private-safe enough;
- do not amplify H012/H057/H068 public factors until a stronger invariant view
  is found.

## Open Questions

- Is H057 a public-specific compact state or a seed for a larger private-safe
  state?
- Does H068 action-health identify invariant action quality or only public
  anchor response?
- Are human-social story features strong enough to recover a public-confirmed
  latent without seeing public LB?
- Is the key hidden variable row membership, target route, or exact
  row-target assignment?

## H076-H077 Update: Value Decoder Split

H076 and H077 sharpen the public/private interpretation.

H076 cleared a `-0.001009` public-action predicted delta while keeping
bad-anchor positive cosine at `0.0`, but the winning value policy was plain
q061. This suggests the safer public/private factorization is currently in the
support and route assignment layer, not in handcrafted route-specific values.

H077 then exposed the opposite extreme: only `16` hard-tail conflict cells
produce a public-action predicted delta of `-0.004677`, but they violate q061
posterior (`+0.000105`) and have small positive bad-anchor cosine (`0.003282`).

Current factorization rule:

- q061-compatible route support is public/private-safe enough to test;
- sparse hard-tail conflicts are high-information sensors, not safe evidence;
- if H077 wins publicly, the private/public split must include a hard-tail
  route latent;
- if H077 loses, public-action spikes without q061 support should be treated as
  sensor overfit.

## H078-H079 Episode-State Factorization

H078 weakens passive row-state factorization from H077: same-row companion cells
did not naturally survive the gate. The promoted H078 candidate changed only
`14` cells on `13` rows, with `1` companion cell. This says H077 support is not
obviously a broad row factor under the current local gate.

H079 tests the opposite possibility: the local gate is too conservative, and
the true hidden variable is an episode factor. The promoted H079 file changes
`294` cells on `42` rows:

- `15` seed rows from H077 hard-tail anchors;
- `27` adjacent same-subject neighbor rows;
- all `7` targets moved on each selected row;
- public-action predicted delta versus H057: `-0.004704`;
- max positive bad-anchor cosine: `0.0`.

Factorization reading:

- if H079 improves, public/private state is not only a cell assignment problem;
  it includes episode-level human-state membership;
- if H079 is neutral, episode membership may exist but target decoding should
  be narrower than all-target q061 propagation;
- if H079 loses badly, the safe public/private factor remains row-target local,
  and H077-style hard-tail spikes should not be propagated across rows.

## H080-H082 Source-Action Factorization

H080-H082 tested three public/private factor forms:

- intersection factor: cells where all source views agree;
- conflict factor: cells where public-action and q061 posterior disagree;
- action-field factor: all cells with negative source-action contribution.

| Experiment | Cells | Public-action delta | Posterior delta | Bad cosine | Reading |
| --- | ---: | ---: | ---: | ---: | --- |
| H080 invariant core | 392 | -0.000656 | -0.000457 | 0.0 | safe but weak |
| H081 conflict ridge | 16 | -0.004365 | +0.000099 | 0.003283 | real but sparse |
| H082 source-action field | 725 | -0.005078 | -0.000616 | 0.0 | broad, strongest |

Current factorization rule:

```text
public/private factor is more likely an action field than a strict consensus
intersection.
```

This does not prove H082 will win public LB. It does show that the 0.001
movement bottleneck was not action capacity; it was the gate being too
conservative.

## H083-H084 Route Factorization

H083/H084 test whether the public/private factor should be represented at the
route level rather than at the individual cell level.

| Factor form | File | New claim | Evidence | Risk |
| --- | --- | --- | --- | --- |
| Route-action transport | `submission_h083_route_action_ef73ae51_uploadsafe.csv` | H082 cells are row-route fragments | `731` changed cells, `-0.005530` public-action delta vs H057 | high H082 overlap, route over-structure |
| Dark route completion | `submission_h084_dark_route_58b9e6de_uploadsafe.csv` | H082 misses route companion cells | H082 + `68` dark cells, `-0.000357` public-action delta vs H082 | conditional on H082 being real |

Public/private reading:

- H083 asks whether private-safe structure lives in the route assignment, not
  the public-action cell score.
- H084 asks whether H082 is a partial public view of a larger route state.

The main caution is that H083 still has high support overlap with H082
(`0.793103` Jaccard). It is a different decoder, but not yet independent
evidence for a new public/private subset. H084 is more orthogonal in support
because it only adds cells outside H082, but its expected delta is smaller.

## H085 Posterior-Refit Factorization

H085 reframes public/private factorization as an iterative estimation problem:

```text
public LB observations -> hidden public equation -> updated row-target
posterior -> private-safe action gate
```

Unlike H083/H084, H085 does not mainly ask whether the action unit is route or
cell. It asks whether the hidden public posterior changes after the H057 sensor
reading is included. The promoted candidate stayed cell-local because the row
and route prototype variants scored lower internally.

Evidence from H085:

- selected posterior: `h061_h057_feedback__ridge_1`;
- changed cells / rows vs H057: `299` / `134`;
- posterior delta vs H057: `-0.000607`;
- source-agree rate: `1.0`;
- H082 action-field ratio: `0.986622`;
- all tracked bad-anchor cosines are negative, with max positive cosine `0.0`;
- upload-safe validation passed.

Factorization reading:

- if H085 improves public LB, public/private state should be updated by an
  equation-refit module whenever a new informative public observation arrives;
- if H085 loses, H057's public state is already close enough and further
  inversion from sparse public readings is underdetermined.

## H086 Responsibility Factorization

H086 separated two possible hidden factors:

1. label/action posterior: what the hidden label state should be;
2. row-target responsibility: which cells public LB effectively listens to.

The experiment fit nonnegative responsibility weights from known public
submission deltas under the H085 posterior. If public/private factorization
were strongly subset-weighted, the fitted field should be concentrated by row,
target, subject, H082 support, or human-state prior.

Observed factorization:

- the best field is `uniform__ridge_0.0001`;
- effective cell count is `1733.49 / 1750`;
- top-200 cells explain only `0.131502` of mass;
- target mass is essentially flat, with Q2 only slightly highest at `0.1458`;
- non-uniform H082/source-action priors concentrate more mass, but lose LOO
  fit and produce weaker candidate deltas.

Current conclusion:

```text
public/private factorization is not currently a sharply concentrated
responsibility mask. It is more likely a diffuse public label/action posterior
plus a value decoder problem.
```

This downgrades "public subset localization" as the main 0.53 route. It does
not downgrade public/private factorization overall; it redirects it toward
private-safe value translation, target-route assignment, and action-health
decoding.

## H087-H088 Value-Law Factorization

H087/H088 tested a stronger public/private interpretation:

```text
public/private is not mainly a row-weight mask.
It is a value-law split: the same row-target route can require different
translation under public-posterior and hard/private heads.
```

H087 used H071 routes and let each route choose among H085 posterior, H082
source-action, H018 hard-world, or bridge value laws. The promoted H087 file
changed `866` cells and had:

- posterior delta vs H057: `-0.000693`;
- hard-world delta vs H057: `+0.000044`;
- responsibility-weighted delta: `-0.000810`;
- max positive bad-anchor cosine: `0.0`.

This means H087 is public-posterior friendly but not hard/private friendly.

H088 then imposed a dual-head Pareto gate. It accepts only route-actions that
improve both H085 posterior and H018 hard-world locally. The promoted H088 file
changed `980` cells and had:

- posterior delta vs H057: `-0.000540`;
- hard-world delta vs H057: `-0.000187`;
- responsibility-weighted delta: `-0.000565`;
- max positive bad-anchor cosine: `0.0`.

Current factorization rule:

```text
public/private hidden state is better modeled as two value heads than as a
concentrated listener subset. H088 is the cleanest current test of that rule.
```

Important caution:

H088 is more coherent but less aggressive on public-posterior gain than H087.
So this factorization is not yet proven as a leaderboard move. It is a
paper-level hypothesis: public and private state may share route support but
disagree on the value law used to move probabilities.

Public LB update:

- H088 public LB: `0.5684942019`;
- delta vs H057: `+0.0007466080`;
- delta vs H012: `+0.0003707188`.

Updated factorization rule:

```text
Public/private factorization is real as a diagnostic geometry, but H018
hard-world is not the private head that should select public actions.
```

What changed:

- `q_hard` can still veto collapse or identify unstable tails;
- `q_hard` should not be given equal action authority with `q_public`;
- H089/H091/H092's high overlap with H088 now becomes a liability for public
  submission priority;
- the next factorization should be equation-level: which row-target cells
  satisfy the public observations, not which routes are locally Pareto-safe.

## H089-H090 Lifestyle Context Factorization

H089 asked whether the public/private value-head split is controlled by
human lifestyle transition state.

Observed H089 factorization:

- posterior delta vs H057: `-0.000605`;
- hard-world delta vs H057: `+0.000035`;
- selected route cells: `895`;
- H088 root-cell overlap: `0.917318`.

This means lifestyle context can reconstruct much of the H088 action geometry,
but it did not cleanly improve the private/hard head. It mostly explains the
existing public/private support rather than discovering new support.

H090 forced the opposite test: act only in low-overlap lifestyle-supported
white space.

Observed H090 factorization:

- selected route cells: `76`;
- posterior delta vs H057: `-0.000079`;
- hard-world delta vs H057: `+0.000141`;
- mean H088 action overlap: `0.099160`.

Current factorization rule:

```text
Lifestyle context is a useful explanatory factor for public/private decoder
choice, but direct lifestyle white-space actions are not private-safe under
current proxies.
```

So public/private factorization currently has this hierarchy:

1. action-grade: H085/H018/H082 value heads and route assignment;
2. explanatory/gating: H072/H089 lifestyle transition state;
3. not action-grade yet: lifestyle white-space generation without posterior
   support.

## H091 Learned Factorization

H091 converted the explanatory lifestyle factor into a learned latent target.
This is the current public/private factorization stack:

```text
lifestyle context -> learned action-quality heads -> public/private value gate
```

Observed H091 factorization:

- selected route cells: `820`;
- posterior delta vs H057: `-0.000552`;
- hard-world delta vs H057: `-0.000108`;
- H088 action overlap: `0.929972`;
- OOF overall latent Spearman: `0.977807`.

Current rule:

```text
The learned lifestyle factor can predict public/private value-head quality,
but public/private action support is still dominated by the H087/H088 basin.
```

So the factorization problem has moved again:

- solved enough: context can learn known value-head quality;
- unsolved: context does not yet find low-overlap, private-safe support;
- next target: raw sequence/block JEPA or masked route-support prediction.

## H092 Raw Context Factorization

H092 replaced semantic story aggregates with raw day-block context. The
factorization question became:

```text
Can raw phone/body/mobility/environment behavior predict public/private
value-head quality, and can it find support outside H087/H088?
```

Observed H092 factorization:

- selected route cells: `629`;
- posterior delta vs H057: `-0.000501`;
- hard-world delta vs H057: `-0.000045`;
- H088 action overlap: `0.888748`;
- H087 action overlap: `0.922882`;
- OOF overall latent Spearman: `0.849724`;
- OOF private latent Spearman: `0.650449`.

Current rule:

```text
Raw behavior context improves the legitimacy of the context encoder, but the
public/private action split is still controlled by known value-law support.
Private-safe low-overlap actions do not emerge just by replacing story
features with raw logs.
```

The factorization problem is now sharper:

- context learning: alive;
- public/private head prediction: partially alive, especially public/Q2;
- private head from raw context: weak;
- low-overlap action discovery: not action-grade yet.

## H093 Masked Low-Overlap Factorization

H093 asked whether the public/private factorization can escape the known
H087/H088/H091/H092 support basin by changing the latent target itself:

```text
raw context -> masked low-overlap support heads -> route value-law decoder
```

Observed factorization:

- white-public OOF Spearman: `0.700088`;
- white-objective OOF Spearman: `0.704811`;
- white-Q2 OOF Spearman: `0.658097`;
- selected cells / rows: `21` / `3`;
- posterior delta vs H057: `-0.000008`;
- hard-world delta vs H057: `+0.000000123`;
- max selected-cell overlap with known roots: `0.476190`;
- selected-cell overlap with H091/H092 roots: `0.000000` / `0.000000`.

Current rule:

```text
The low-overlap factor is learnable but too sparse. Public/private state is not
blocked because the encoder cannot see it; it is blocked because the decoder
cannot scale a new support region safely.
```

Updated hierarchy:

1. action-grade support: still concentrated in H057/H087/H088/H091/H092 basin;
2. context-to-head prediction: healthy, especially public/objective/Q2;
3. low-overlap support: visible but too small;
4. next live factor: value-law inversion over the known support basin.

## H094 H057 Teacher Factorization

H094 asked whether H057 is a public/private value law that can be transferred,
or a local assignment event:

```text
H057-vs-H042 event -> sparse teacher heads -> context-predicted value law ->
non-H057 known-basin transfer
```

Observed factorization:

- H057 echo OOF Spearman: `0.778954`;
- known-public OOF Spearman: `0.984925`;
- known-private OOF Spearman: `0.984580`;
- known-Q2 OOF Spearman: `0.981512`;
- selected candidate overlap with H057 cells: `0.000000`;
- selected overlap with H087/H088/H091/H092 roots: `0.904412` /
  `0.889706` / `0.823529` / `0.433824`;
- selected cells / rows: `134` / `23`.

Current rule:

```text
Public/private heads can recognize the H057 event, but recognition does not
equal scalable transfer. The H057 event should be modeled as a local sensor in
the public/private factorization, not as a broad public head by itself.
```

Updated hierarchy:

1. public/private known support: still the dense action basin;
2. H057 echo: highly recognizable, weakly transferable;
3. low-overlap support: learnable, too sparse;
4. next live factor: global assignment/equation solver across known support.

## H095/H096 Assignment Equation Factorization

H095 executed the next factorization target:

```text
H057 base + updated public equations + H088 negative sensor
-> row-target toxicity field
-> safe assignment solver
```

The direct toxic-veto solver was coherent but small:

- H095 selected `48` cells / `32` rows;
- posterior delta vs H057: `-0.000248`;
- H088 selected-cell overlap: `2`;
- the surviving actions were mostly Q2 hardtail.

This means:

```text
Avoiding H088-toxic directions is not enough to recover a broad public/private
action field. The veto collapses the field to a small Q2 repair basin.
```

The stronger factorization signal came from the conflict table:

- H057-positive cells: `343`;
- H088-toxic cells: `980`;
- overlap: `105`;
- same-direction conflict: `22`;
- opposite-direction conflict: `83`.

Updated rule:

```text
H088 toxicity is signed. Many H088-toxic cells are not bad support; they are
bad because H088 moved against the H057-positive direction.
```

H096 tests that signed factorization:

```text
context/teacher = H057-positive route event
negative sensor = H088 toxic action
target = conflict cells where positive and toxic directions are opposite
decoder = move further along H057-positive direction
```

Observed H096 candidate:

- file: `submission_h096_conflict_inversion_af7e60fd_uploadsafe.csv`;
- changed cells / rows: `83` / `28`;
- anti-H088 direction rate: `1.000000`;
- cosine with H057-vs-H042 direction: `0.527502`;
- cosine with H088 direction: `-0.086648`.

Current factorization hierarchy:

1. H088 hard/Pareto head as action target: rejected by public;
2. H088 as unsigned toxic veto: partially alive but too small;
3. H088 as signed counterfactual sensor: live and now represented by H096;
4. next 0.53 route: learn a signed public/private action equation, not just a
   better context encoder.

## H097/H098 Signed Public-Response Factorization

H097 tested the broadest version:

```text
all known public submissions -> signed action-response equation -> candidate
```

It fit the global leaderboard response well:

- LOO MAE: `0.000423`;
- LOO Spearman: `0.978474`;
- pair accuracy: `0.952727`;
- permutation p: `0.0`.

But it failed the important factorization stress:

```text
H088 actual delta = +0.000747
H097 H088 LOO prediction = -0.000642
```

So H097 learned the old-public-vs-frontier separation, not the H057/H088
frontier action law.

H098 changed the factorization weights:

```text
frontier public observations + high-weight H088
-> signed action equation
-> low-amplitude H096-style conflict decoder
```

Observed H098 factorization:

- weighted LOO MAE: `0.000417`;
- H088 LOO prediction: `+0.000757`;
- H088 LOO error: `+0.000010`;
- selected candidate: `submission_h098_frontier_equation_a748e477_uploadsafe.csv`;
- changed cells / rows: `46` / `20`;
- model-predicted delta: `-0.000134`;
- anti-H088 direction rate: `1.000000`.

Updated hierarchy:

1. broad public-response model: alive, but not sufficient;
2. frontier-weighted signed response model: alive and better aligned with H088;
3. H096 raw conflict inversion: still useful as the unsmoothed local sensor;
4. next if H098 fails: row/route-constrained signed assignment, not more
   cell-level gradient smoothing.

## H099 Route-Constrained Signed Assignment

H099 implements the next branch:

```text
frontier-weighted signed action equation
+ H071 row-target route templates
-> route-constrained action assignment
-> low-amplitude H057-positive / H088-opposite conflict decoder
```

Observed H099 factorization:

- selected file: `submission_h099_route_equation_1cbff4af_uploadsafe.csv`;
- selected routes / cells / rows: `15` / `26` / `15`;
- model-predicted delta vs H057: `-0.000244`;
- posterior delta vs H057: `+0.000079`;
- hard diagnostic delta vs H057: `+0.000109`;
- anti-H088 direction rate: `1.000000`;
- H057-positive alignment rate: `1.000000`;
- selected conflict rate: `1.000000`;
- cosine with H088 direction: `-0.042448`;
- mean assignment route score: `0.439801`.

Interpretation:

The H057/H088 conflict field can be represented as route actions, but the best
route-constrained candidate does not rely on the highest H071 full-state routes.
It selects conflict-heavy route fragments. This keeps the signed public/private
factor alive, but weakens the claim that H071 assignment score alone identifies
the hidden public/private law.

Current hierarchy:

1. H088 as private/action target: rejected;
2. H088 as signed negative sensor: alive;
3. H098 frontier-weighted cell equation: alive;
4. H099 route-constrained equation: live sensor for whether assignment should be
   discrete route-level or sparse cell-level.

## H100 Route-Action Basis Equation

H100 moves from route constraints to route equation space:

```text
known public submission action vectors
-> signed overlap with route-action basis
-> frontier-weighted route-basis public response
-> route assignment decoder
```

Observed H100 factorization:

- selected file: `submission_h100_route_basis_6c8e0c6b_uploadsafe.csv`;
- selected route-basis model: `signed_meta`, `k_basis=40`, ridge `0.1`;
- weighted LOO MAE: `0.000217`;
- H088 LOO prediction: `+0.000853`;
- selected actions / cells / rows: `24` / `28` / `24`;
- route-basis predicted delta vs H057: `-0.001031`;
- H098 cell-equation predicted delta vs H057: `-0.000045`;
- anti-H088 direction rate: `1.000000`;
- H057-positive alignment rate: `1.000000`;
- selected conflict rate: `1.000000`.

Interpretation:

H100 creates a new split in the world model. H098 and H099 ask whether signed
cells and route constraints are safe. H100 asks whether public feedback itself
is best represented in route-action coordinates. The huge gap between
route-basis predicted delta (`-0.001031`) and H098 cell predicted delta
(`-0.000045`) is not a bug to smooth away; it is the sensor.

If H100 wins, the public/private factorization should move toward route-action
basis equations. If it loses, route basis remains explanatory but not
action-grade.

## H101 Disagreement-Toxicity Boundary

H101 tests whether the route-action basis equation needs a toxicity boundary:

```text
route-basis public response says action is useful
+ H098 sparse cell equation says action is not clearly toxic
-> stable safe-assignment field
```

Observed H101 factorization:

- selected file: `submission_h101_disagreement_toxicity_9e088156_uploadsafe.csv`;
- selected actions / cells / rows: `5` / `6` / `5`;
- route-basis predicted delta vs H057: `-0.000641`;
- H098 cell-equation predicted delta vs H057: `-0.000014`;
- posterior delta vs H057: `+0.000003`;
- anti-H088 direction rate: `0.833333`;
- H057-positive alignment rate: `0.833333`;
- selected conflict rate: `1.000000`.

Interpretation:

The stable disagreement-filtered field is much smaller than H100's full
route-basis field. This weakens the claim that every H100 route action is
safe, but it does not kill the route-basis worldview. It separates two claims:

1. route-basis coordinates explain public observations;
2. route-basis coordinates alone are sufficient to choose safe actions.

H101 says claim 1 is still alive, while claim 2 needs public validation. If
H101 improves and H100 does not, the public/private factorization should add a
toxicity gate. If H100 improves and H101 does not, the toxicity gate is too
conservative.

## H102 Bad-Axis Nullspace Factorization

H102 tests a different public/private factorization:

```text
bad public submissions are observations of toxic action axes
good frontier anchors are observations of H057-positive axes
safe assignment = route-basis gain outside the positive bad-axis span
```

Observed H102 factorization:

- selected file: `submission_h102_badnull_e775939d_uploadsafe.csv`;
- selected actions / cells / rows: `5` / `7` / `5`;
- route-basis predicted delta vs H057: `-0.001162`;
- H098 cell-equation predicted delta vs H057: `-0.000023`;
- cumulative bad-axis weighted positive projection: `0.000000`;
- cumulative bad-axis max positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.002161`;
- cumulative good-minus-bad margin: `+0.013258`;
- selected conflict rate: `1.000000`.

Interpretation:

This is the cleanest current version of the active public/private equation
goal. It explains H057 as a positive row-state anchor, H088 as a negative
action axis, and older bad submissions as a broader toxic subspace. The
selected action is small, so H102 does not yet prove a 0.53-scale mechanism.
It does prove that HS-JEPA can express "safe action" as an assignment equation
rather than only as a latent representation or blend.

## H103 Toxic-Shadow Cancellation Factorization

H103 keeps H102's factorization but changes the unit of safety:

```text
single route safety -> portfolio safety
```

Observed H103 factorization:

- selected file: `submission_h103_shadowcancel_89496ed5_uploadsafe.csv`;
- selected actions / cells / rows: `23` / `28` / `23`;
- route-basis predicted delta vs H057: `-0.002438`;
- H098 cell-equation predicted delta vs H057: `-0.000063`;
- cumulative bad-axis weighted positive projection: `0.000000`;
- cumulative bad-axis max positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.008946`;
- cumulative good-minus-bad margin: `+0.036728`;
- selected conflict rate: `1.000000`.

Interpretation:

H103 strengthens the current public/private equation hypothesis. H102 proved a
small safe nullspace exists; H103 shows a denser 28-cell conflict portfolio can
remain in that nullspace while increasing route-basis predicted gain. If public
confirms this direction, the hidden factor is not simply public-like rows or
target-wise calibration. It is a constrained action equation over the whole
submission vector.

## H104 Toxic-Axis Residual Transport Factorization

H104 changes the factorization from selection to transport:

```text
H100 route-basis desired field
  = useful human-state route intent + toxic public-axis component

safe submitted field
  = desired field - positive projection onto bad public axes
```

Observed H104 factorization:

- selected file: `submission_h104_toxicresid_52f826e6_uploadsafe.csv`;
- source route-actions / submitted cells / rows: `47` / `87` / `64`;
- route-basis predicted delta vs H057: `-0.001758`;
- desired route-basis predicted delta before residualization: `-0.001800`;
- residual vector route-basis prediction before sparsifying: `+0.000220`;
- H098 cell-equation predicted delta vs H057: `-0.000086`;
- cumulative bad-axis weighted positive projection: `0.000000`;
- cumulative bad-axis max positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.033173`;
- cumulative good-minus-bad margin: `+0.191825`.

Interpretation:

H104 is not just a wider H103.  It separates route intent from action toxicity.
The surprising diagnostic is that the full residual vector loses route-basis
score, but the sparsified row-target assignment regains a strong route-basis
prediction while staying bad-axis silent.  If public confirms this, the hidden
public/private law is not "which route is good" but "which part of a route
intent survives toxic-axis transport."

Failure interpretation:

- if H103 beats H104, row-target semantics are discrete and projection damages
  the human-state route meaning;
- if H100 beats H103/H104, bad public axes are not a reliable constraint
  because they overlap the positive route-basis law;
- if H104 beats H103/H100, public/private factorization should be modeled as a
  route-intent plus toxic-axis residual equation.

## H105 Sparse Route-Consensus Kernel Factorization

H105 starts with a signed coefficient factorization:

```text
route-action basis functions
  -> positive/counter coefficient search
  -> public/private constrained coefficient field
```

The observed factorization collapses:

```text
29 positive coefficient terms
  -> 8 row-target cells
  -> rows 144,146,151,164
```

Observed H105 factorization:

- selected file: `submission_h105_signedcoef_8f0e502e_uploadsafe.csv`;
- selected terms: `29`;
- positive terms / counter terms: `29` / `0`;
- submitted cells / rows: `8` / `4`;
- route-basis predicted delta vs H057: `-0.002727`;
- H098 cell-equation predicted delta vs H057: `-0.000018`;
- cumulative bad-axis weighted positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.007302`;
- cumulative good-minus-bad margin: `+0.025287`;
- anti-H088, H057-positive, and conflict rates: all `1.000000`.

Interpretation:

This weakens the hypothesis that broad signed counter-coefficients are
necessary.  It strengthens a sparse route-consensus kernel hypothesis: many
route-action routes, including subjective and objective route variants, point
to the same small hidden assignment.  The active public/private state may be
localized in a few row-target cells rather than spread as a smooth latent
field.

Failure interpretation:

- if H105 loses while H103/H104 improve, the kernel is a route-basis overfit and
  needs diversity or density;
- if H105 improves, the next factorization should expand the id06/id07 kernel
  by nearest-route motifs rather than broaden all actions;
- if all H100-H105 lose, route-action equations remain diagnostic but are not
  action-grade without a new public subset sensor.

## H106 Route-Consensus Expansion Factorization

H106 tests whether the sparse H105 kernel is an isolated public-safe object or
the seed of a transferable assignment field.

The factorization is:

```text
many route-action basis functions
  -> per-cell signed vote consensus
  -> H105-seed and seed-neighbor expansion
  -> bad-axis silent row-target assignment
```

Observed H106 factorization:

- selected file: `submission_h106_routeconsensus_f315d99a_uploadsafe.csv`;
- source route-actions: `220`;
- submitted cells / rows: `48` / `22`;
- H105 seed-row cells: `10`;
- H105 seed-neighbor cells: `15`;
- H105 seed-subject cells: `20`;
- route-basis predicted delta vs H057: `-0.000796`;
- H098 cell-equation predicted delta vs H057: `-0.000040`;
- cumulative bad-axis weighted positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.016900`;
- cumulative good-minus-bad margin: `+0.064203`;
- anti-H088 / H057-align / conflict rates: `0.979167` / `0.979167` /
  `0.958333`.

Interpretation:

H106 deliberately gives up much of H105's route-basis gain in exchange for
transfer.  It is therefore not a safe-score maximizer.  It is a public/private
sensor for whether the hidden assignment is a tiny cell kernel or an expandable
route-consensus field.

Failure interpretation:

- if H106 beats H105, route-consensus transfer is real and HS-JEPA should build
  kernel propagation around row/subject neighborhoods;
- if H105 beats H106, the safe public action is sharper than the route
  representation and expansion creates toxic or noisy cells;
- if both lose, route-consensus is still a diagnostic but needs a stronger
  public subset equation before becoming action-grade.

## H107 Negative-Sensor Antipode Factorization

H107 treats H088 as a signed negative observation instead of only a bad axis.

The factorization is:

```text
H088 failed action
  -> H088-active toxic cells
  -> antipode move
  -> H106/H057-supported subset
  -> bad-axis constrained assignment
```

Observed H107 factorization:

- selected file: `submission_h107_antipode_a0ea1eec_uploadsafe.csv`;
- submitted cells / rows: `26` / `19`;
- Q2 cells: `0`;
- H098 cell-equation predicted delta vs H057: `+0.000004`;
- route-basis predicted delta vs H057: `-0.000079`;
- cumulative bad-axis weighted positive projection: `0.000808`;
- cumulative H088-axis cosine: `-0.022682`;
- cumulative good-minus-bad margin: `+0.034484`;
- anti-H088 / H106-align / H057-align / conflict rates:
  `1.000000` / `1.000000` / `0.961538` / `0.961538`.

Interpretation:

H107 is intentionally not a blanket reversal of H088.  Broad reversal did not
survive internal stress; the surviving field is a narrow non-Q2 core where
H088 toxicity, H106 consensus, and H057-positive direction agree.

Failure interpretation:

- if H107 improves, negative public sensors can be converted into signed
  antidote actions;
- if H107 loses while H103-H106 improve, H088 is only a toxic veto and should
  not generate action;
- if H107 loses badly, the public/private action equation is not sign-symmetric
  around bad public sensors.

## H108 Decoder-Jury Factorization

H108 treats previous HS-JEPA decoders as independent witnesses of the hidden
public/private equation.

The factorization is:

```text
H103-H107 candidate action vectors
  -> per-cell signed family votes
  -> decoder-family intersection field
  -> H102 bad-axis constrained assignment
```

Observed H108 factorization:

- selected file: `submission_h108_jury_610a26a0_uploadsafe.csv`;
- source candidates / families: `19` / `5`;
- submitted cells / rows: `47` / `27`;
- Q2 cells: `0`;
- H098 cell-equation predicted delta vs H057: `-0.000050`;
- route-basis predicted delta vs H057: `-0.001528`;
- cumulative bad-axis weighted positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.009025`;
- cumulative good-minus-bad margin: `+0.107886`;
- mean decoder-family count: `3.851064`;
- mean family consensus: `1.000000`;
- anti-H088 / H057-align rates: `0.914894` / `0.914894`.

Interpretation:

H108 is the strongest current statement that row-target action safety is an
agreement property.  It keeps the assignment sparse, excludes Q2, and requires
multiple decoder families to point in the same direction before a cell is
trusted.

Failure interpretation:

- if H108 improves, public/private safety should be modeled as decoder-family
  consensus;
- if H108 loses to H103/H104, broad branch-specific action fields are more
  faithful than intersection;
- if H108 loses to H105/H106, the true assignment is a sharper kernel than the
  jury can represent;
- if H108 loses to H107, negative-sensor antipode carries the live information.

## H109 Decoder-Coefficient Factorization

H109 treats entire decoder submissions as coefficient terms in the hidden
public/private row-target equation.

The factorization is:

```text
H103-H108 decoder action vectors
  -> coefficient-composed field
  -> H108 support manifold
  -> bad-axis constrained sparse assignment
```

Observed H109 factorization:

- selected file: `submission_h109_coeff_54147083_uploadsafe.csv`;
- selected candidate: `h109_kernel_coeff_focus_c48_t7_54147083`;
- source candidates / families: `20` / `6`;
- selected coefficient terms: `4`;
- selected term families: `h105`;
- submitted cells / rows: `4` / `2`;
- Q2 cells: `0`;
- H098 cell-equation predicted delta vs H057: `+0.000015`;
- route-basis predicted delta vs H057: `-0.001862`;
- full field H098 predicted delta vs H057: `-0.000029`;
- full field route-basis predicted delta vs H057: `-0.004404`;
- cumulative bad-axis weighted positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.005077`;
- cumulative good-minus-bad margin: `+0.021017`;
- mean decoder-family count: `4.250000`;
- mean family consensus: `1.000000`.

Interpretation:

The coefficient field can look strong before decoding, but the action-grade
assignment survives only as a very small H105-derived kernel.  This strengthens
the view that public/private safety is not just a smooth latent direction.  It
may be a sparse row-target assignment object with hard toxicity boundaries.

Failure interpretation:

- if H109 improves, coefficient-decoded sparse kernels are the right
  public/private action unit;
- if H108 improves more, agreement across decoder families matters more than
  coefficient composition;
- if H105 improves more, coefficient decoding over-pruned the original kernel;
- if broad branches improve more, the kernel view is too narrow and public
  rewards a wider action field.

## H110 Benefit/Toxicity Factorization

H110 explicitly separates two hidden fields that previous solvers mixed:

```text
benefit field:
  decoder-family support, H057 alignment, H088 opposition, H098 frontier score

toxicity field:
  H102 bad-axis local projection, H088 local same-direction pressure,
  shortcut/null/bad-pressure indicators

assignment field:
  cells where benefit - toxicity survives cumulative public/private stress
```

Observed H110 factorization:

- selected file: `submission_h110_toxgap_7b02f196_uploadsafe.csv`;
- selected candidate: `h110_toxgap_kernel_release_c64_a085_7b02f196`;
- source candidates / families: `21` / `7`;
- submitted cells / rows: `37` / `23`;
- Q2 cells: `0`;
- H098 cell-equation predicted delta vs H057: `-0.000037`;
- route-basis predicted delta vs H057: `-0.001037`;
- cumulative bad-axis weighted positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.008961`;
- cumulative good-minus-bad margin: `+0.066098`;
- selected mean benefit: `0.918943`;
- selected mean toxicity: `0.517838`;
- selected mean benefit-toxicity gap: `0.401106`;
- selected mean family count: `4.324324`;
- H108/H109 overlap: `29` / `1` cells.

Interpretation:

H110 is a middle path between H108 and H109.  It accepts H108's premise that
independent decoder families matter, but it rejects raw family agreement as an
action rule unless the local toxicity field is lower than the benefit field.
It also rejects H109's four-cell collapse by releasing nearby H105/H106 kernel
support when the toxicity gap stays positive.

Failure interpretation:

- if H110 improves, public/private safety is a benefit-toxicity factorization
  problem and HS-JEPA needs an explicit toxicity head;
- if H108 improves more, toxicity was already handled by family consensus and
  H110 over-filtered;
- if H109 improves more, assignment is sharper than the local toxicity model;
- if all fail, toxicity/benefit features are still diagnostic but not
  action-grade without a new public subset sensor.

## H111 Global Boundary Factorization

H111 adds a boundary solver above H110's benefit/toxicity fields.

The factorization is:

```text
H110 benefit field + H110 toxicity field
  -> H108 kept/rejected/added boundary audit
  -> global beam/knapsack assignment
  -> cumulative public bad-axis safe action
```

Observed H111 factorization:

- selected file: `submission_h111_boundary_7cbf5e9d_uploadsafe.csv`;
- selected candidate: `h111_boundary_broad_null_c150_a048_7cbf5e9d`;
- submitted cells / rows: `53` / `28`;
- Q2 cells: `0`;
- H098 cell-equation predicted delta vs H057: `-0.000020`;
- route-basis predicted delta vs H057: `-0.000680`;
- cumulative bad-axis weighted positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.015318`;
- cumulative good-minus-bad margin: `+0.132168`;
- selected H108 kept / rejected / H110-added cells: `27` / `14` / `5`;
- selected H109 cells: `3`;
- H111/H108 cosine: `0.923553`;
- H111/H110 cosine: `0.691689`.

Interpretation:

H111 shows that toxicity is not purely local.  H108-rejected cells had higher
local gap than H108-kept cells, but also higher shortcut and bad-pressure
scores.  The action-grade solver must therefore handle both local benefit and
global interaction constraints.

Failure interpretation:

- if H111 improves, public/private safety is a global boundary over
  benefit/toxicity representations;
- if H110 improves more, global rescue adds cells whose shortcut/bad-pressure
  risk is real;
- if H108 improves more, family consensus already captured the safe boundary;
- if H109 improves more, global boundary solvers are too broad and the kernel
  view survives.

## H112 Public-Residual Toxicity Factorization

H112 adds an observed-public residual layer above the H111 boundary solver.

The factorization is:

```text
known public submissions
  -> H098 leave-one-out public equation
  -> actual minus predicted LB residual
  -> signed residual projection onto row-target actions
  -> residual toxicity / residual safety fields
  -> H111 boundary pruning
  -> public/private safe action
```

Observed H112 factorization:

- selected file: `submission_h112_residualtox_68b26f11_uploadsafe.csv`;
- selected candidate: `h112_residual_h111_pruned_boundary_c86_a056_68b26f11`;
- known public observations: `24`;
- largest effective bad residual: H010 objective S1/S4 `+0.001450`;
- other bad residuals: LeJEPA strict `+0.001350`, E216 masked-family
  `+0.000974`;
- selected cells / rows: `40` / `23`;
- Q2 cells: `0`;
- H098 cell-equation predicted delta vs H057: `-0.000018`;
- route-basis predicted delta vs H057: `-0.000980`;
- cumulative bad-axis weighted positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.011878`;
- cumulative good-minus-bad margin: `+0.118414`;
- selected residual toxicity / safety / gap:
  `0.489754` / `0.681667` / `0.191912`;
- H112/H111 cosine: `0.855260`;
- H112/H110 cosine: `0.633342`.

Interpretation:

H112 keeps H111's global-boundary state but tests whether known public
residuals can be used as an action toxicity sensor.  The key structural claim
is that H088 is not the only negative sensor.  H010, LeJEPA strict, and E216
are residual-bad directions after H098 already explains the broad public
response.  HS-JEPA should therefore distinguish first-order public response
from unexplained public residual toxicity.

Failure interpretation:

- if H112 improves, public/private safety is a residual-toxicity factorization
  over the boundary field;
- if H111 improves more, public residual projection is too noisy or
  underidentified;
- if H110 improves more, local toxicity-gap is cleaner than LOO residual
  toxicity;
- if H109 improves more, residual and boundary fields are both too broad.

## H113 Row-Route Factorization

H113 lifts H112's residual toxicity from cell assignment to row-route
assignment.

The factorization is:

```text
H112 residual toxicity / safety field
  -> row-wise target route candidates
  -> one-route-per-row beam assignment
  -> cumulative public bad-axis stress test
  -> row-route public/private safe action
```

Observed H113 factorization:

- selected file: `submission_h113_rowroute_04369be5_uploadsafe.csv`;
- selected candidate: `h113_rowroute_global_state_c92_a042_04369be5`;
- selected cells / rows / bundles: `37` / `14` / `14`;
- mean targets per bundle: `2.642857`;
- Q2 cells: `0`;
- H098 cell-equation predicted delta vs H057: `-0.000019`;
- route-basis predicted delta vs H057: `-0.000597`;
- cumulative bad-axis weighted positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.001766`;
- selected residual toxicity / safety / gap:
  `0.499907` / `0.682719` / `0.182812`;
- H113/H112 cosine: `0.851031`;
- H113/H111 cosine: `0.762718`;
- H113/H110 cosine: `0.440345`.

Interpretation:

H113 is not an independent public/private factor.  It is a route-structured
compression of H112.  That makes the public result highly diagnostic:
improvement means public rewards row-level target-route coherence; degradation
means the extra route constraint discards useful cell-level assignments.

Failure interpretation:

- if H113 improves, action safety is row-route factored;
- if H112 improves more, residual toxicity is cell-factored;
- if H111 improves more, residual toxicity itself is weak;
- if H110/H109 improve more, route and residual fields are both too broad.

## H114 Toxic-Subspace Null Factorization

H114 changes the order of the public/private decoder.

Previous factorization:

```text
candidate row-target action
  -> public bad-axis / residual-toxicity stress
  -> keep or reject
```

H114 factorization:

```text
known bad public actions
  -> toxic subspace
candidate human-state action
  -> projection into toxic nullspace
  -> sparse row-target assignment
  -> public/private stress validation
```

Observed H114 factorization:

- selected file: `submission_h114_nullspace_73fe7866_uploadsafe.csv`;
- selected candidate: `h114_null_novel_lowoverlap_c64_a058_73fe7866`;
- selected cells / rows: `27` / `25`;
- Q2 cells: `0`;
- H098 cell-equation predicted delta vs H057: `+0.000005`;
- route-basis predicted delta vs H057: `+0.000028`;
- cumulative bad-axis weighted positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.010421`;
- selected residual toxicity / safety / gap:
  `0.442060` / `0.602047` / `0.159986`;
- toxic projection before / after:
  `13.057908` / `0.618885`;
- toxic projection ratio: `0.047395`;
- H114/H112 cosine: `0.033494`;
- H114/H113 cosine: `0.057487`.

Interpretation:

H114 is the strongest current negative/positive discriminator.  It asks whether
public/private safety is attached to a linear toxic subspace rather than to
locally scored cells.  Its selected vector is intentionally novel, so the
public result should be read as a structural sensor, not as a conservative
attempt to edge the best score.

Failure interpretation:

- if H114 improves, hidden public toxicity is subspace-like and should be
  removed before assignment;
- if H114 fails mildly, a named residual-bad-axis version may still survive;
- if H114 fails badly, toxic vectors are not a stable projection space and the
  model should return to H112/H113 selectors.

## H115 Second-Order Action-Equation Factorization

H115 adds a nonlinear public/private action-equation layer.

The factorization is:

```text
known public submissions
  -> signed action features
  -> first-order target/route features
  -> second-order row-target curvature features
  -> LOO public response equation
  -> sparse assignment under curvature, residual-toxicity, and H088 stress
```

Observed H115 factorization:

- selected file: `submission_h115_curvature_23748467_uploadsafe.csv`;
- selected candidate: `h115_curv_q2_companion_c22_a035_23748467`;
- selected cells / rows: `20` / `16`;
- Q2 cells: `8`;
- curvature model: `route_curvature`, alpha `30`;
- weighted LOO MAE / RMSE: `0.000433509` / `0.000627976`;
- H088 LOO prediction / abs error: `+0.000658162` / `0.000088446`;
- H115 curvature predicted delta vs H057: `-0.000251384`;
- H098 cell-equation predicted delta vs H057: `-0.000001`;
- route-basis predicted delta vs H057: `-0.000032`;
- H088-axis cosine: `-0.003903`;
- bad-axis weighted positive projection: `0.000000`;
- H115/H114 cosine: `0.015212`;
- H115/H112 cosine: `0.247554`.

Interpretation:

H115 makes H088 a negative sensor, not a private-action teacher.  The dual-head
Pareto gate is treated as evidence that an action can be punished by row-target
interaction even when simpler axes look acceptable.  H115's selected action is
therefore a test of nonlinear toxicity: Q2 is reopened only as a small
companion route, not as a broad Q2 correction.

Failure interpretation:

- if H115 improves, public/private safety is partly second-order and HS-JEPA
  needs a row-target equation solver;
- if H115 loses while H112/H113 improve, residual toxicity is more stable than
  the curvature fit;
- if H115 loses while H114 improves, nullspace projection is a better
  pre-assignment transformation;
- if H115 loses badly, H088-like negative sensors should continue to veto Q2
  companion reopening.

## H116-H117 Forbidden Companion-Sector Factorization

H116/H117 update the Q2 factorization.

H116 factorization:

```text
Q2-only action
Q2 + same-row companions
  -> second-order curvature comparison
  -> H088 toxicity stress
  -> anti-H088 guard attempt
```

Observed H116 result:

- positive Q2-rescue bundles exist in every spec;
- every positive-rescue bundle is H088-positive;
- anti-H088 guards cannot make the final action safe without adding bad-axis
  pressure;
- no upload-safe assignment was promoted.

H117 factorization:

```text
H116 positive-rescue / H088-positive bundles
  -> forbidden companion-sector representation
proposal cell action
  -> same-sector toxicity / opposite-sector antidote score
  -> H102/H112/H115 stress
```

Observed H117 result:

- forbidden axes: `264`;
- scored proposal cells: `2192`;
- positive forbidden-antipode cells: `4`;
- no upload-safe assignment was promoted.

Interpretation:

The public/private factorization now has a sharper rule:

```text
Q2 companion curvature may be a real latent structure,
but it is not yet a safe action structure.
```

H116 says the Q2 companion structure belongs to the H088-positive toxic sector.
H117 says that sector is not easily inverted into a safe non-Q2 action.  So Q2
should remain behind a hard veto unless public evidence from H115 contradicts
the local equation diagnostics.

## H118 Forbidden-Sector Veto Assignment Factorization

H118 changes the role of H116/H117 from failed action generator to decoder
constraint.

The factorization is:

```text
H116 positive-rescue / H088-positive Q2 bundles
  -> forbidden companion-sector representation
candidate non-Q2 residual/nullspace/antidote action
  -> same-sector exposure veto
  -> residual safety/toxicity scoring
  -> H102/H115 public-response stress
  -> sparse safe assignment
```

Observed H118 factorization:

- selected file: `submission_h118_forbiddenveto_e81167a8_uploadsafe.csv`;
- selected candidate: `h118_veto_antidote_c52_a046_e81167a8`;
- forbidden axes: `264`;
- selected cells / rows: `52` / `34`;
- Q2 cells: `0`;
- forbidden same-sector exposure: mean `0.000000`, max `0.000000`;
- forbidden pressure: mean `0.000000`;
- H102 bad-axis weighted positive projection: `0.000000`;
- H102 H088-axis cosine: `-0.003628`;
- route-basis predicted delta vs H057: `-0.000568`;
- model predicted delta vs H057: `-0.000009`;
- curvature marginal vs zero: `+0.000047`;
- residual toxicity / safety / gap:
  `0.397824` / `0.648287` / `0.250463`.

Interpretation:

H118 directly implements the current public/private equation hypothesis:

```text
real hidden state can be public-toxic when materialized as an action.
```

The safe object is therefore not the strongest hidden representation.  The
safe object is the row-target assignment that avoids the toxic sector while
still carrying residual human-state signal.  This makes H118 more than a
candidate submission: it is the current architecture test for whether HS-JEPA
needs an action-to-observation equation solver.

Failure interpretation:

- if H118 improves, forbidden-sector veto is promoted into the decoder;
- if H118 loses while H112/H114 improve, the veto is useful but this branch
  picked the wrong safe assignment;
- if H115 improves while H118 loses, Q2 companion is not globally forbidden
  and needs a narrower exception solver;
- if H118 loses badly, the forbidden sector is only diagnostic and should not
  constrain public/private assignment directly.

## H119-H120 Posterior/Action Factorization

H119 asks whether the H085 posterior itself can be promoted to an action-grade
target after adding H118 forbidden-sector veto and H088/curvature stress.

Observed H119 factorization:

- no candidate was promoted;
- strong local H085 pools existed:
  - source-agree non-Q2: `190` cells after local filters;
  - stage: `140` cells;
  - high-gain: `95` cells;
- direct H085-posterior actions failed cumulative action stress.

Interpretation:

```text
hidden public posterior != public-safe action field
```

H119 therefore changes the role of H085.  It should be treated as a sensor over
public-sensitive row/target context, not as a decoder target.

H120 implements that split:

```text
H085 posterior gain
  -> toxic/public-sensitive row sensor
H118/H112 residual stage proposals
  -> forbidden-sector veto
  -> H088 non-positive action stress
  -> Q/S row-target assignment
```

Observed H120 factorization:

- selected file: `submission_h120_toxrow_0b84c821_uploadsafe.csv`;
- selected candidate: `h120_toxrow_stage_bridge_c56_a046_0b84c821`;
- selected cells / rows: `18` / `15`;
- Q2 cells: `0`;
- target route: Q3 `6`, S1 `1`, S2 `1`, S3 `6`, S4 `4`;
- H085 posterior delta vs H057: `+0.0000035`;
- model predicted delta vs H057: `-0.0000151`;
- route-basis predicted delta vs H057: `-0.0002291`;
- bad-axis positive projection: `0.000000`;
- H088-axis cosine: `-0.000003`;
- good-bad margin: `0.106932`;
- residual toxicity / safety / gap:
  `0.425667` / `0.603213` / `0.177546`.

The important part is the sign conflict: H120 gets worse against H085's own
posterior target, but improves under public-response route/model sensors.  The
factorization should therefore keep two variables:

```text
representation posterior: what hidden state appears plausible?
action safety equation: should this row-target correction be materialized?
```

Failure interpretation:

- H120 improves: H085 is a useful row/context sensor and HS-JEPA needs separate
  representation and action heads;
- H120 loses while H118 improves: H085 row localization is contaminated by the
  public posterior and should not constrain action selection;
- H120 and H118 both lose: the current public-private toxicity equation is
  diagnostic but still not the safe assignment field.

## H121 Row-Regime Assignment Factorization

H121 uses the H120 row sensor as a partition over H118's assignment field:

```text
H085 toxic-posterior row sensor
  -> low-sensor row regime: keep H118 forbidden-veto action
  -> high-sensor row regime: remove H118 action, use H120 stage bridge
  -> public/private stress equation
  -> row-target assignment
```

Observed H121 factorization:

- selected file: `submission_h121_rowsensorpart_d03abb5b_uploadsafe.csv`;
- selected candidate: `h121_partition_sensor_ge070_d03abb5b`;
- selected cells / rows: `44` / `31`;
- Q2 cells: `0`;
- threshold: H120 row sensor rank `>= 0.70`;
- active H118 rows/cells removed: `15` / `20`;
- H118 cells kept / H120 cells used: `32` / `18`;
- route-basis predicted delta vs H057: `-0.0005801`;
- model predicted delta vs H057: `-0.0000378`;
- bad-axis positive projection: `0.000000`;
- H088-axis cosine: `-0.039209`;
- good-bad margin: `0.113396`;
- residual toxicity / safety / gap:
  `0.425874` / `0.652365` / `0.226491`.

Interpretation:

H121 turns the posterior/action split into a public-private equation:

```text
same action proposal can be safe or unsafe depending on hidden row regime.
```

The factorization no longer treats H118, H120, or H085 as globally right.
Instead:

- H118 supplies a default forbidden-veto residual assignment;
- H085/H120 identifies a high-sensitivity row regime;
- H120 stage bridge overrides H118 only in that regime.

Failure interpretation:

- H121 improves: public/private safety is regime-partitioned and HS-JEPA needs
  a mixture-of-action-solvers decoder;
- H118 improves more: H085 row sensor should not override the default
  forbidden-veto solver;
- H120 improves more: high-sensor rows need a more aggressive replacement rule;
- all lose: the row-sensor partition is a diagnostic but still not the hidden
  private-safe assignment variable.

## H122 Subtractive Action-Safety Factorization

H122 tests whether H121's row-regime improvement came from replacement or from
deletion.  The result favors a subtractive interpretation:

```text
H118 forbidden-veto assignment
  -> H085/H120 row/context sensor
  -> identify public-toxic objective Q/S stage actions
  -> remove unsafe row-target cells
  -> submit sparse residual assignment
```

Observed H122 factorization:

- selected file: `submission_h122_pruneeq_0a9edcce_uploadsafe.csv`;
- selected candidate: `h122_prune_stage_public_toxic_0a9edcce`;
- remaining selected cells / rows: `24` / `19`;
- removed H118 cells / rows: `28` / `22`;
- removed targets: S4 `8`, S3 `8`, S2 `7`, Q3 `3`, S1 `2`;
- Q2 cells: `0`;
- route-basis predicted delta vs H057: `-0.0006052`;
- model predicted delta vs H057: `-0.0000287`;
- bad-axis positive projection: `0.000000`;
- H088-axis cosine: `-0.066158`;
- good-bad margin: `0.125854`;
- residual toxicity / safety / gap:
  `0.412932` / `0.674085` / `0.261153`.

Interpretation:

H122 suggests that the public/private hidden state is not just a selector among
multiple action heads.  It also acts as an equation over existing actions:

```text
some locally plausible row-target corrections become toxic only after the
public/private observation equation sees the full action vector.
```

The action decoder should therefore run in two phases:

1. prune public-toxic actions from a candidate field;
2. only then consider whether missing cells need replacement.

Failure interpretation:

- H122 improves: public/private safety is primarily a toxicity-pruning
  equation, and HS-JEPA should separate representation, proposal, prune, and
  optional replacement stages;
- H121 improves more: pruning alone is insufficient and high-sensor rows need
  positive replacement actions;
- H118 improves more: the apparent toxic stage sector was a local diagnostic
  artifact;
- all lose: the current row-target action proposal family is not the real
  public/private assignment field.

## H123 Prune-Then-Refill Factorization

H123 tests the second phase that H122 left open:

```text
proposal field -> toxicity prune -> sparse core -> route-safe refill
```

Observed H123 factorization:

- selected file: `submission_h123_refilleq_8958f688_uploadsafe.csv`;
- selected candidate: `h123_sparse_route_refill_8958f688`;
- start from H122 cells: `24`;
- added cells: `2`;
- added targets: Q3 `1`, S3 `1`;
- final selected cells / rows: `26` / `20`;
- Q2 cells: `0`;
- route-basis predicted delta vs H057: `-0.0007325`;
- model predicted delta vs H057: `-0.0000266`;
- bad-axis positive projection: `0.000000`;
- H088-axis cosine: `-0.065510`;
- good-bad margin: `0.124697`;
- residual toxicity / safety / gap:
  `0.414871` / `0.665769` / `0.250899`.

Interpretation:

The public/private equation may have three separate variables:

```text
toxicity field: which proposal cells must be removed?
core assignment: what remains safely active after pruning?
route complement: which tiny cells restore missing route structure?
```

The key tension is H123 versus H122.  H123 is more route-consistent, but H122
is slightly more anti-toxic and more conservative under H098/model caution.
Their public LB comparison will say whether the hidden public equation rewards
route completion or punishes refill risk more.

Failure interpretation:

- H123 improves: prune-only was incomplete and HS-JEPA needs a refill stage;
- H122 improves more: sparse pruned core is the safer public-private action;
- H121 improves more: refill must be controlled by row-regime sensor rather
  than route complement;
- H118 improves more: the whole prune/refill layer is overfitting stress axes.
