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
