# Breakthrough Bets Toward 0.53

Last updated: 2026-06-02

## Current Gap

Current frontier:
`submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv`,
public LB `0.5677475939`.

Target: `0.53`.

Required improvement: `0.0377475939`.

The H012 jump from E247 to H012 was `0.0080354663`. Reaching 0.53 requires
about `4.70` H012-sized breakthroughs, or one much larger hidden-state
discovery. Therefore H057-neighborhood top-k, alpha, damp, and smoothing
experiments are not 0.53-capable unless they are attached to a new hidden-state
world model.

## Big-Bet Gate

A candidate is a real breakthrough bet only if all of these are true:

- it changes a data-generating-world assumption;
- expected public movement can plausibly be `0.001` or larger;
- failure kills or sharply weakens a named hypothesis;
- it touches hidden state, target route, public/private factorization,
  action-health, row-target assignment, or human-social state;
- it is not just a small blend or local parameter sweep.

## Bet 1: Public/Private Hidden-State Factorization

### Hypothesis

H012 recovered a public-readable hidden state, but part of that state is
public-specific. To reach 0.53, we need to separate:

```text
public listener state = invariant human state + public subset bias + shortcut
```

### Why It Can Be Large

H012 alone moved public by `0.0080354663`. If public/private factorization can
keep the H012-scale signal while removing shortcut movement, it is the most
plausible path to another H012-sized jump.

### Minimal Experiment

Build H069:

- use H012/H042/H057/H068 public equations as the public-state view;
- use train labels, human-state context, and row/subject blocks as invariant
  views;
- use H010, E216, E323, bad JEPA, and H050-null as shortcut views;
- solve for three correction fields: invariant, public-only, shortcut;
- materialize only invariant-positive and shortcut-negative cells.

### Success Criteria

- public-free decoder predicts at least `-0.002` versus H057;
- H050-null and bad-axis overlap remain low;
- selected cells are not just H012/H057 copies;
- public LB improves by at least `0.001`.

### Kill Criteria

- invariant and public-only factors are numerically inseparable;
- selected cells collapse to H057 support or H012 support;
- null anchors score as healthy;
- public result is worse than H057 by more than `0.001`.

### H069 Update

H069 was built and generated
`submission_h069_public_private_factor_4ffd6cd6_uploadsafe.csv`. It selects
`268` cells on `97` rows, has public-action predicted delta `-0.000586` versus
H057, and overlaps H068 on `250/268` cells. The experiment supports the
existence of a factorized public/private/action-health field, but it also shows
that strict private-safe filtering does not preserve H068's full expected
movement.

This weakens the narrow "H068 plus cleaner thresholds" route. Bet 1 remains
alive as an architecture component, but the next `0.001`-scale attempt should
feed the factors into Bet 2 or Bet 3: a joint HS-JEPA correction-field decoder
or a discrete row-target assignment solver.

## Bet 2: Full HS-JEPA v1 Correction-Field Model

### Hypothesis

The current H-series already contains the pieces of HS-JEPA, but they are
hand-wired. A learned HS-JEPA v1 can combine human/social context, public
actions, row-state seeds, and action-health into a correction field.

### Why It Can Be Large

H063/H064 suggest H057 row-state can be approached from context, while H068
suggests action-health can be learned from known submissions. The missing
piece may be joint decoding rather than a new raw feature.

### Minimal Experiment

Build H070:

- encoder input: H013/E262/E268/E328/deep raw context, row/subject/episode
  context, target route context, and known-action context;
- masked target: H012 posterior cells, H057 seed rows, H064 boundary rows,
  H068 action-health cells;
- decoder output: row-target correction field, not probabilities;
- train with positive targets and explicit null/bad-anchor negatives.

### Success Criteria

- recovers H057 seeds above null in leave-seed-out;
- demotes H050-null rows;
- predicts known action sign with pairwise accuracy above `0.90`;
- generates a candidate with expected movement above `0.001` and clean upload
  audit.

### Kill Criteria

- human context does not recover H057 seeds above random;
- action decoder ranks known bad anchors as healthy;
- generated candidates are H057 clones or broad all-target moves.

### H070 Update

H070 was built as the first full HS-JEPA v1 joint decoder and generated
`submission_h070_full_hsjepa_9e4a9602_uploadsafe.csv`.

Result:

- masked context-to-public OOF Spearman: `0.819270`;
- context-to-private OOF Spearman: `0.941669`;
- context-to-action OOF Spearman: `0.928469`;
- selected candidate changes `360` cells on `144` rows;
- `323/360` changed cells are outside H069;
- public-action predicted delta versus H057: `-0.000826`;
- posterior delta versus H057: `-0.000637`;
- bad-anchor positive cosine: `0.0`.

This keeps Bet 2 alive as architecture evidence: visible context/route/story
views can predict the hidden action representations. But it misses the
`0.001` expected-movement gate and its H068/H069 selection AUC is weak, so it
does not prove that smooth latent scoring solves the action problem. H071 is
now the sharper next bet: use H070 as one energy term inside a discrete
row-target assignment solver, not as a plain top-score selector.

## Bet 3: Discrete Row-Target Assignment Solver

### Hypothesis

The real problem is not probability calibration. It is exact row-target
placement. H029 showed target-wise row permutation collapses toward `0.581`,
and H032 recovered H012 as a phase point while siblings failed.

### Why It Can Be Large

If row-target identity is the locked invariant, smooth correction fields will
always miss. A discrete assignment solver can jump to a different support basin.

### Minimal Experiment

Build H071:

- candidates are row-target assignments, not continuous deltas;
- score assignments with H012 equation fit, H030 identity priors, H034 route
  failure contrast, H057 row-state, H068 action-health, and human-context
  support;
- use beam search or integer-style constrained selection;
- materialize only support changes that improve assignment energy and pass
  negative controls.

### Success Criteria

- finds support sets not reachable by alpha/top-k sweeps;
- preserves H012/H057 positive invariants;
- avoids H010/E216/E323 bad supports;
- public move expected at least `0.001`.

### Kill Criteria

- best assignments are just H012 or H057 support;
- assignment energy prefers known public-bad files;
- row/target permutation controls look equally good.

### H071 Update

H071 was built and generated
`submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv`.

Result:

- promoted candidate:
  `h071_assignment_big_outside_h069_c820_r185_q272_a52b6b57`;
- changed cells / rows versus H057: `736` / `158`;
- cells outside H070 / H069: `385` / `642`;
- Q2 changed cells: `72`;
- selected route mix: `full_state:63`, `nonq2_full:47`, `q3_s_stage:13`,
  `s_stage:16`, `q2_hardtail:8`, `q2_s3_tail:2`, `q_subjective:2`,
  `recovery_route:7`;
- public-action predicted delta versus H057: `-0.000983`;
- posterior delta versus H057: `-0.000744`;
- responsibility-weighted delta versus H057: `-0.000976`;
- bad-anchor positive cosine: `0.0`.

This is the first post-H070 file that nearly reaches the `0.001` big-bet gate
while changing the hidden-state assumption itself. It does not prove H071 until
public feedback arrives, but it gives a clean falsification rule: if the file
wins meaningfully, exact route assignment becomes the main decoder; if it loses
badly, H070's smooth representation is real but the current route templates are
not action-grade.

## Bet 4: Human-Social State Engine

### Hypothesis

The 1000 human-state hypotheses are not direct rules. They are a vocabulary of
latent states. HS-JEPA should learn which story family explains a row-target
correction route.

### Why It Can Be Large

The user-provided domain intuition is likely most useful before decoding:
sleep inertia, nocturnal phone use, social arousal, work pressure, weekend
recovery, cashflow stress, measurement confidence, and subject-specific sign
flips can define human-state masks that models cannot infer from target labels
alone.

### Minimal Experiment

Build H072:

- cluster the 1000 hypotheses by hidden state and prediction role;
- map each story family to available raw/context features;
- train story-family latent views to recover H057/H064/H068 target
  representations;
- only then let the decoder change probabilities.

### Success Criteria

- at least one story family recovers H057 seeds or H068 healthy cells above
  null;
- family-level negative controls fail;
- materialized candidate is not a broad story-rule shift;
- public movement is at least `0.001`.

### Kill Criteria

- story families predict subject/date only;
- direct story rules beat latent version locally but fail controls;
- all high-priority stories collapse into the same row mask.

### H072 Update

H072 was built and generated
`submission_h072_humansocial_route_bae1edae_uploadsafe.csv`.

Result:

- promoted candidate:
  `h072_fullvector_social_state_outside_h069_c980_r220_q290_bae1edae`;
- changed cells / rows versus H057: `704` / `148`;
- cells outside H070 / H069: `383` / `613`;
- selected routes outside H071 promoted route set: `97/148`;
- Q2 changed cells: `75`;
- route mix: `full_state:117`, `q3_s_stage:25`, `nonq2_full:3`,
  `q_subjective:2`, `s_stage:1`;
- human family mix: `routine_pressure:66`, `weekend_rhythm:45`,
  `social_load:19`, `bedtime_arousal:10`, `badnight_aftereffect:8`;
- public-action predicted delta versus H057: `-0.000922`;
- responsibility-weighted delta versus H057: `-0.000935`;
- bad-anchor positive cosine: `0.0`.

The architecture caveat is decisive: subject-preserving null stress did not
show that story-family route support rediscovered H071 routes. Mean H071-route
support was `0.776796` real versus `0.783463` null, z `-1.326523`, p
`0.903333`. H072 therefore keeps Bet 4 alive only in a narrower form:
human-social stories look useful as action-health/context views, but direct
story-to-route assignment is not yet validated. The next large follow-up should
either move story families upstream into action-health prediction or invert
known bad story/route shortcuts, not merely strengthen the same route prior.

### H073 Update

H073 tested the narrower follow-up and generated
`submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv`.

Result:

- promoted candidate:
  `h073_fullvector_action_state_outside_h069_c980_r225_q288_7a2cbf07`;
- changed cells / rows versus H057: `657` / `141`;
- cells outside H070 / H069: `343` / `557`;
- Q2 changed cells: `17`;
- route mix: `s_stage:55`, `nonq2_full:34`, `q3_s_stage:21`,
  `full_state:15`, `recovery_route:14`, `q_subjective:2`;
- public-action predicted delta versus H057: `-0.000618`;
- responsibility-weighted delta versus H057: `-0.000628`;
- bad-anchor positive cosine: `0.0`.

H073 does not meet the `0.001` movement gate. The architecture finding is more
important than the file: hard selected-cell prediction is weak under
subject-group OOF (`story_to_h068_selected` AUC `0.513105`), but continuous
action-health with route context is strong (`story_route_to_h068_health` OOF
Spearman `0.890901`, H071-selected-cell AUC `0.860064`). This keeps Bet 4 alive
only as a continuous action-health/shortcut view. It weakens any further
attempt to use human stories as direct hard row-target assignment labels.

## Bet 5: Anti-Shortcut State Inversion

### Hypothesis

Public-bad submissions encode what the hidden state is not. H010, E216, E323,
bad JEPA, and H050-null are negative views. A contrastive model that learns the
opposite of these shortcuts may produce a cleaner large move than positive
posterior extension.

### Minimal Experiment

Build H074:

- treat known bad submissions as negative action worlds;
- learn null/shortcut state directions at row-target level;
- search for cells with high H012/H057/H068 positive energy and low shortcut
  energy;
- materialize a deliberately anti-shortcut correction field.

### Success Criteria

- public-free scorer predicts less bad-anchor exposure than H057 and H068;
- selected cells are not only existing H057 support;
- the candidate tests a new negative-space world model.

### Kill Criteria

- anti-shortcut scoring simply returns no-move or H057;
- bad anchors are not separable from good anchors;
- public result is neutral or worse without clear falsification value.

### H074 Update

H074 was built and generated
`submission_h074_antishortcut_inversion_816703df_uploadsafe.csv`.

Result:

- promoted candidate:
  `h074_row_broad_outside_h069_c1100_r250_q290_816703df`;
- changed cells / rows versus H057: `597` / `152`;
- cells outside H070 / H069: `278` / `519`;
- Q2 changed cells: `42`;
- route mix: `s_stage:46`, `recovery_route:23`, `q2_hardtail:23`,
  `nonq2_full:20`, `q3_s_stage:20`, `full_state:15`,
  `q2_s3_tail:4`, `q_subjective:1`;
- public-action predicted delta versus H057: `-0.000840`;
- responsibility-weighted delta versus H057: `-0.000949`;
- bad-anchor positive cosine: `0.0`;
- top-520 bad-opposition null z: `9.270846`.

The hypothesis survives the representation test. Target-stratified bad-axis
nulls show that cells selected by H074 are genuinely opposite to known bad
worlds and have lower shortcut energy than shuffled controls. The action claim
is weaker: the best broad sensor still misses the `0.001` movement gate. Bet 5
therefore stays alive as a target-representation layer, but it is not yet a
standalone 0.53 breakthrough decoder.

### H075 Update

H075 tested the natural follow-up and generated
`submission_h075_antibad_transport_f6863945_uploadsafe.csv`.

Hypothesis:

```text
bad submissions define not only support, but the value transport field itself
```

Result:

- promoted diagnostic:
  `h075_transport_broad_conservative_outside_h069_c1120_r250_q295_f6863945`;
- changed cells / rows versus H057: `524` / `152`;
- cells outside H070 / H069: `220` / `458`;
- Q2 changed cells: `46`;
- transport mode: `conservative` inverse-bad/q061 hybrid;
- route mix: `s_stage:41`, `recovery_route:27`, `q2_hardtail:27`,
  `q3_s_stage:20`, `nonq2_full:15`, `full_state:10`,
  `q2_s3_tail:9`, `q_subjective:3`;
- public-action predicted delta versus H057: `-0.000766`;
- responsibility-weighted delta versus H057: `-0.000912`;
- generated candidates at `<= -0.000800` public-action delta: `0`;
- generated candidates at `<= -0.001000` public-action delta: `0`;
- bad-anchor positive cosine: `0.0`.

This weakens the value-transport version of Bet 5. The negative representation
is real, but directly reflecting bad-anchor movements does not create a
larger action than H074. Bet 5 remains alive as a support/energy layer and is
weaker as a standalone decoder. The next big bet should not be another
anti-bad amplitude sweep; it needs a different value source.

## Priority

Current order:

1. Submit or observe H071 if a public slot is available for the row-target
   assignment claim.
2. Submit H074 only if the next public slot is meant to test whether failed
   public worlds are positive contrastive target representations.
3. Do not prioritize H075 as a public slot unless the goal is specifically to
   falsify inverse-bad value transport; it is weaker than H074 internally.
4. H072/H073 are now architecture evidence unless the next public question is
   specifically about human-social action-health.
5. Build the next solver that combines H071 assignment with H074
   anti-shortcut targets, but uses a new value source rather than inverse-bad
   transport.
6. H070/H069 follow-ups only if public feedback specifically supports smooth
   latent scoring or strict factorization.

H069 has answered the first public-free factorization question: the factors
are useful, but the standalone gated variant is unlikely to be the whole 0.53
route. H070 says smooth joint latent scoring is useful but not enough. H071
materializes exact assignment. H073 says human-social context is better as
continuous health/shortcut representation than direct assignment. H074 now says
known bad worlds carry a real inverse target representation, but also that this
inverse layer still needs a stronger action solver. H075 says the missing
solver is not simply "move by the inverse bad vector".

### H076 Update

H076 tested Bet 5's next version:

```text
anti-shortcut/action-health support is known,
but values must be decoded by route-specific human-state laws
```

Result:

- promoted sensor:
  `submission_h076_route_value_decoder_a91b64c7_uploadsafe.csv`;
- selected candidate:
  `h076_route_value_big_anti_shortcut_q061_baseline_outside_h069_c1040_r250_q295_a91b64c7`;
- changed cells / rows: `471` / `153`;
- outside H069 cells: `411`;
- Q2 changed cells: `58`;
- public-action predicted delta: `-0.001009`;
- responsibility-weighted delta: `-0.001002`;
- max positive bad-anchor cosine: `0.0`;
- winning value policy: plain `q061`, not a handcrafted route-specific policy.

This partly revives Bet 5 as an action solver: support selection cleared the
`0.001` sensor threshold. But it weakens the handcrafted value-decoder
subclaim. The data currently says "find better support; q061 is still the
safest value materializer."

### H077 Update

H077 is a new big-bet contradiction, not a safety improvement:

```text
public-action sensor says some sparse tail cells should overshoot q061;
q061 posterior and bad-anchor geometry say that overshoot is dangerous.
```

Promoted diagnostic:
`submission_h077_hardtail_conflict_123f6665_uploadsafe.csv`.

- changed cells / rows: `16` / `15`;
- Q2 changed cells: `7`;
- public-action predicted delta: `-0.004677`;
- posterior delta: `+0.000105`;
- q061 value gain sum: `-0.182922`;
- max positive bad-anchor cosine: `0.003282`;
- route mix: `q2_hardtail:7`, `q2_s3_tail:3`, `recovery_route:3`,
  `s_stage:2`.

This is a true high-upside / high-falsification sensor. If it wins, q061 is too
soft on a sparse hard-tail route and HS-JEPA needs an explicit tail-law target
representation. If it loses, do not keep chasing monster-route conflicts; use
q061 and bad-anchor cosine as hard guardrails.

### H078-H079 Update

H078 asked whether H077 hard-tail cells naturally expand into same-row route
companions. They mostly did not: the promoted H078 file changed only `14` cells
on `13` rows and found just `1` companion cell. That weakens the passive
same-row cascade story.

H079 therefore turns the question into a real big bet:

```text
H077 hard-tail anchors are visible cells of an acute same-subject episode.
Force a full row plus adjacent-day correction field and let public LB decide
whether the hidden state is episode-level or cell-local.
```

The promoted H079 file,
`submission_h079_forced_episode_8a546735_uploadsafe.csv`, changes `294` cells
on `42` rows, moves all seven targets on the selected episode rows, has
public-action predicted delta `-0.004704`, and keeps max positive bad-anchor
cosine at `0.0`.

This is currently the sharpest 0.53-style bet because it can change the
worldview by more than local tuning:

- win: HS-JEPA needs an episode-state target representation;
- neutral: episode support exists but the decoder is too broad;
- loss: H077 hard-tail state is cell-local or public-sensor overfit.

### H080-H082 Update

These experiments tested whether the next hidden state is an intersection or an
action field.

| Experiment | File | Cells | Public-action | Posterior | Bad cosine | Reading |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| H080 | `submission_h080_invariant_core_dc4f2613_uploadsafe.csv` | 392 | -0.000656 | -0.000457 | 0.0 | safe but weak |
| H081 | `submission_h081_conflict_ridge_3ace5fca_uploadsafe.csv` | 16 | -0.004365 | +0.000099 | 0.003283 | real but sparse |
| H082 | `submission_h082_source_action_0e565967_uploadsafe.csv` | 725 | -0.005078 | -0.000616 | 0.0 | broad, strongest |

Current best big-bet reading:

```text
The hidden correction target is the broad source-action field,
not the high-consensus intersection.
```

H082 is now the strongest post-H079 public sensor. A win promotes action-field
decoding as HS-JEPA's main module. A loss means the public-action sensor is too
broad and must be constrained by H080-style consensus or new hidden-state
evidence.

### H083-H084 Update

H083 and H084 split the route question into two falsifiable claims.

| Experiment | File | Core claim | Changed vs H057 | Extra relation | Public-action delta |
| --- | --- | --- | --- | --- | --- |
| H083 | `submission_h083_route_action_ef73ae51_uploadsafe.csv` | H082 cells are row-route fragments | 731 cells / 146 rows | 87 H083-only cells, 81 H082-only cells | -0.005530 vs H057 |
| H084 | `submission_h084_dark_route_58b9e6de_uploadsafe.csv` | H082 needs dark route completion | 793 cells / 149 rows | H082 + 68 new dark cells | -0.000357 vs H082 |

H083 is the larger 0.53-style bet because it changes the decoder unit from
cell action to route transport. H084 is conditional: it becomes strong only if
H082/H083 public feedback says the visible source-action route is real.

Current route-action decision tree:

1. H082 wins: broad source-action field is real.
2. H083 beats H082: action field should be decoded as row-route transport.
3. H084 beats H082 after H082 wins: visible route fragments need dark
   completion.
4. H083/H084 both fail while H082 wins: route structure is over-imposed and
   HS-JEPA should keep the action field cell-local.

### H085 Update

H085 tests a different 0.53 route: public-sensor inversion after the frontier
has moved.

```text
Known public submissions are equations over the hidden public subset.
After H057 becomes the base, H042/H050/H057 should refit the public posterior
rather than merely confirm the old H012 direction.
```

The promoted file,
`submission_h085_aug_public_equation_f154e2bb_uploadsafe.csv`, changes `299`
cells on `134` rows versus H057. It uses the `h061_h057_feedback__ridge_1`
posterior and selects only source-agree cells:

- posterior delta versus H057: `-0.000607`;
- source-agree rate: `1.0`;
- H082 ratio: `0.986622`;
- max positive bad-anchor cosine: `0.0`;
- target mix: Q1 `29`, Q2 `47`, Q3 `24`, S1 `50`, S2 `55`, S3 `44`,
  S4 `50`.

This is a high-information bet because it can falsify the core public sensor
loop itself:

- win: HS-JEPA should learn an iterative public-posterior refit stage;
- loss: the next big jump will not come from simply adding public equations;
  it needs a new hidden-state unit or a private-safe decoder.

### H086 Update

H086 tested the stronger inversion:

```text
public LB is not just a label/action posterior sensor; it has a hidden
row-target responsibility vector that decides which cells matter.
```

The result is a useful negative/weak signal. The best responsibility field was
almost uniform:

- best config: `uniform__ridge_0.0001`;
- LOO MAE: `0.000034734`;
- effective cells: `1733.49 / 1750`;
- top-50 / top-200 mass: `0.038317` / `0.131502`;
- max weight: `0.001207`;
- target mass nearly flat across Q/S labels.

The promoted diagnostic file,
`submission_h086_public_resp_df95467d_uploadsafe.csv`, is upload-safe and moves
`251` cells, but its expected edge is only `-0.000628` responsibility-weighted
and `-0.000494` posterior-weighted versus H057. Forced H082/source-action
non-uniform priors were weaker than the uniform fit.

Breakthrough reading:

```text
The next 0.53-scale bet should not be "find the public subset and weight it
harder" under the current sensor set. It should change the hidden value law:
target route, action-health, hard label world, or private-safe posterior
translation.
```

H086 therefore downgrades public-subset responsibility as a jackpot route and
raises the priority of row-target assignment/value-law solvers.

### H087-H088 Update

H087/H088 moved the next big bet from "which rows matter" to "which hidden
value law should decode a route."

| Experiment | File | Core claim | Changed vs H057 | Posterior delta | Hard-world delta | Status |
| --- | --- | --- | --- | --- | --- | --- |
| H087 | `submission_h087_route_value_law_f5aa327b_uploadsafe.csv` | each row-target route needs a route-conditioned value law | `866` cells / `139` rows | `-0.000693` | `+0.000044` | posterior-friendly, hard-world conflict |
| H088 | `submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv` | public posterior and hard-world are dual latent heads, decode only Pareto-safe actions | `980` cells / `168` rows | `-0.000540` | `-0.000187` | cleaner research bet |

Breakthrough reading:

```text
The 0.53 path is unlikely to be a sharper public subset mask. The live big bet
is a hidden value-law problem: a row route can be correct while its probability
translation is wrong.
```

H087 is the stronger public-posterior move, but it damages the hard-world head.
H088 is the stronger HS-JEPA architecture claim because it treats H085 and H018
as separate latent heads and only accepts Pareto-safe route-actions.

Submission interpretation:

- H087 win: route-conditioned value-law decoding is enough; hard-world conflict
  is not a public action blocker.
- H088 win: HS-JEPA needs explicit public/private dual-head gating.
- both lose: the route/value support is plausible internally but not yet
  public-action grade; the next big bet must recover a stronger private-state
  target, not just combine H085/H018/H082.

Current big-bet priority:

1. H088 if the goal is to test the paper-level HS-JEPA dual-state contribution.
2. H087 if the goal is to maximize public-posterior movement and accept
   hard-world conflict risk.
3. H082/H071 remain the older broad-action and assignment sensors for comparing
   whether value-law gating added anything beyond support selection.

### H089-H090 Update

H089/H090 tested the next assumption:

```text
Maybe the missing factor is not another public/private equation, but the
human lifestyle transition state that decides which value head to trust.
```

| Experiment | File | Core claim | Changed vs H057 | Posterior delta | Hard-world delta | H088 overlap | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H089 | `submission_h089_lifestyle_transition_gate_a9598fc3_uploadsafe.csv` | lifestyle transition chooses public/private decoder head | `888` cells / `156` rows | `-0.000605` | `+0.000035` | `0.917318` root-cell overlap | explains H088 but mostly rediscovered it |
| H090 | `submission_h090_lifestyle_white_space_6748b5dc_uploadsafe.csv` | lifestyle context opens new action space outside H087/H088 | `49` cells / `17` rows | `-0.000079` | `+0.000141` | `0.099160` action overlap | white-space action is locally unsafe |

Breakthrough reading:

```text
Human/social state is real enough to organize decoder heads, but current direct
lifestyle features are not enough to create the next H012-scale action support.
The next 0.53-scale bet needs a learned latent target for lifestyle state,
not a hand-scored story gate.
```

The big-bet queue changes:

1. Keep H088 as the clean architecture probe.
2. Treat H089 as a "does lifestyle context explain decoder choice?" probe, not
   a likely best submission.
3. Do not submit H090 unless we explicitly want a high-risk falsification of
   unseen lifestyle white-space actions.
4. Next jackpot attempt should learn a latent target from lifestyle context:
   predict route/action/value-head assignment under a masked context objective,
   then decode only where the learned state agrees with public/private heads.

### H091 Update

H091 executed that next attempt:

```text
context = lifestyle state + row/route structure
target = action/value-head quality inferred from H085/H018/H082/H071 agreement
prediction = subject-held-out learned latent, not direct labels
```

| Experiment | File | Core claim | Changed vs H057 | Posterior delta | Hard-world delta | H088 overlap | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H091 | `submission_h091_learned_lifestyle_latent_452b5828_uploadsafe.csv` | lifestyle context can learn hidden action/value-head quality before decoding | `820` cells / `119` rows | `-0.000552` | `-0.000108` | `0.929972` action overlap | learned latent is healthy but support is not novel |

OOF latent diagnostics were strong, with overall Spearman `0.977807` and
top-10 AUC `0.990365`. The caution is that the target is a pseudo hidden
action target derived from existing route/value sensors; this proves
representation alignment, not true label discovery.

Breakthrough reading:

```text
The learned-latent HS-JEPA module is now real, but the 0.53 path still requires
new support, not just a better predictor of the H087/H088 basin.
```

Next jackpot candidate:

- learn context from raw sequence/log blocks rather than H072 story aggregates;
- mask full row/subject/date blocks and predict action-grade route support;
- require the latent to improve low-overlap support without hard-world damage.

### H092 Update

H092 executed the raw sequence/log-block version of the H091 idea:

```text
context = raw day-block logs + within-subject transition/novelty
target = action/value-head quality inferred from H085/H018/H082/H071
prediction = subject-held-out raw latent, not direct labels
```

| Experiment | File | Core claim | Changed vs H057 | Posterior delta | Hard-world delta | H088 overlap | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H092 | `submission_h092_raw_dayblock_latent_67a84cd8_uploadsafe.csv` | raw daily behavior can predict hidden action/value-head quality before decoding | `629` cells / `113` rows | `-0.000501` | `-0.000045` | `0.888748` action overlap | raw latent is real, but new support remains too small |

OOF diagnostics were meaningful but weaker than H091:

- overall Spearman `0.849724`, top-10 AUC `0.959135`;
- Q2 Spearman `0.886433`;
- private Spearman only `0.650449`.

The decisive negative result is the low-overlap branch:

- `raw_transition_white` had H088 overlap `0.547619` and H087 overlap
  `0.452381`;
- it changed only `32` cells and only `6` rows;
- posterior delta was only `-0.000021`.

Breakthrough reading:

```text
Raw day-block context is not the missing jackpot by itself. It can learn known
action quality, but low-overlap action support does not scale. The next 0.53
bet must change the target or solver, not merely improve the context encoder.
```

Next jackpot direction:

- global row-target assignment with constraints over the full 250x7 grid;
- masked route-support prediction where the target is low-overlap support, not
  the existing H087/H088 action-quality target;
- value-law discovery from public/private equations rather than another
  context feature family.

### H093 Update

H093 executed the masked route-support target:

```text
context = raw day-block logs + route/value-law structure
target = low-overlap action support outside H087/H088/H091/H092 roots
```

| Experiment | File | Core claim | Changed vs H057 | Posterior delta | Hard-world delta | Known-root overlap | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H093 | `submission_h093_masked_lowoverlap_5f023312_uploadsafe.csv` | raw context can predict new low-overlap route support | `21` cells / `3` rows | `-0.000008` | `+0.000000123` | max selected overlap `0.476190` | latent real but support too sparse |

OOF evidence is not collapse: white-public Spearman `0.700088`,
white-objective Spearman `0.704811`, and white-Q2 Spearman `0.658097`.

The scale test is the decisive negative:

- only `14` top route actions satisfy
  `max_known_overlap <= 0.88` and `masked_latent_score >= 0.55`;
- only `2` top route actions satisfy
  `max_known_overlap <= 0.78` and `masked_latent_score >= 0.55`;
- the promoted root file moves only `21` cells.

Breakthrough reading:

```text
Low-overlap support discovery is not the next 0.53 mechanism under the current
decoder. The search should move from "new support" to "new value law": infer
how the known public/private row-target basin should be translated into
probabilities.
```

Next 0.53-scale big bet:

- public-equation/value-law inversion from the H057 base;
- whole-row or route-level value law, not cell top-k;
- use H093/H092 only as a diagnostic gate, not as the main action support.

### H094 Update

H094 tested the next value-law idea directly:

```text
context = raw day-block + human/social state + route/action metadata
target = sparse H057-vs-H042 value-law teacher
decoder = transfer to non-H057 cells inside known public/private support
```

| Experiment | File | Core claim | Changed vs H057 | Posterior delta | Hard-world delta | H057 overlap | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H094 | `submission_h094_value_law_transfer_73f40c93_uploadsafe.csv` | H057 is a transferable sparse value-law teacher | `134` cells / `23` rows | `-0.000053` | `-0.000014` | selected mean `0.000000` | teacher learnable, transfer weak |

OOF diagnostics look strong:

- H057 echo Spearman `0.778954`, top-10 AUC `0.998971`;
- known-public/private/Q2 heads all exceed Spearman `0.98`;
- overall head Spearman `0.978088`.

The decisive negative result is transfer scale:

- forbidding direct H057 cell replay leaves only a weak transfer tail;
- promoted mean H057 transfer score is only `0.011098`;
- the candidate moves only `134` cells despite using the known support basin.

Breakthrough reading:

```text
H057 is very easy to recognize but hard to generalize. It behaves more like a
local row-target assignment event than a broad value law.
```

Updated 0.53 big-bet priority:

1. global row-target assignment solver with public/private constraints;
2. direct public-equation inversion at row/route level, not H057 echo transfer;
3. multi-world private/public factorization that can explain H057 without
   replaying it;
4. only after that, another context encoder.

### H095/H096 Update

H095 and H096 executed the first solver version of that priority.

| Experiment | File | Core claim | Changed vs H057 | Posterior delta | H088 relation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| H095 | `submission_h095_assignment_solver_948e8840_uploadsafe.csv` | H088-toxic directions can be vetoed to reveal safe assignment | `48` cells / `32` rows | `-0.000248` | only `2` cell overlap with H088 | too small; mostly Q2 hardtail repair |
| H096 | `submission_h096_conflict_inversion_af7e60fd_uploadsafe.csv` | H088 failed by reversing H057-positive conflict cells; use H088 as a signed inverse sensor | `83` cells / `28` rows | `+0.000011` | anti-H088 direction rate `1.000000` | high-information big bet |

The major discovery is the H057/H088 conflict geometry:

```text
H057-positive cells = 343
H088-toxic cells = 980
overlap = 105
opposite-direction overlap = 83
```

Breakthrough reading:

```text
The missing 0.53 mechanism is probably not "find a better public/private head".
It is "infer the signed action equation from failed public actions". H088 is
useful because it tells us which direction public punished.
```

Current top big bet:

`submission_h096_conflict_inversion_af7e60fd_uploadsafe.csv`

Why it is worth a scarce public slot:

- it is not a micro-blend;
- it tests a new signed counterfactual use of public LB failures;
- if it wins, HS-JEPA v2 has a publishable decoder idea:
  failed-action inversion as a row-target assignment equation.

Failure interpretation:

```text
If H096 loses, the signed conflict field is not reusable and the solver must
move from cell-level inversion to row/route-level constrained assignment.
```

### H097/H098 Update

H097 generalized the idea from H088-only to all public observations:

| Experiment | File | Core claim | Model stress | Candidate scale | Status |
| --- | --- | --- | --- | --- | --- |
| H097 | `submission_h097_signed_equation_062bff8e_uploadsafe.csv` | all public submissions train a signed action-response equation | global LOO MAE `0.000423`, Spearman `0.978474`, but H088 LOO wrong-sign | `9` cells / `5` rows | broad response alive, frontier law failed |
| H098 | `submission_h098_frontier_equation_a748e477_uploadsafe.csv` | frontier-weighted public response with H088 as high-weight sensor trains the signed equation | H088 LOO `+0.000757` vs actual `+0.000747` | `46` cells / `20` rows | current best information-value candidate |

Breakthrough reading:

```text
The action-equation idea is real enough to fit public response, but the
equation must be frontier-weighted. Old 0.576-0.581 submissions dominate a
global fit and hide the H057/H088 law.
```

Current submission priority:

1. `submission_h098_frontier_equation_a748e477_uploadsafe.csv`
   - best current test of HS-JEPA v2 as a signed public action-equation decoder;
   - fixes H097's H088 LOO failure;
   - lower amplitude than H096, so it is the cleaner equation-solver bet.

2. `submission_h096_conflict_inversion_af7e60fd_uploadsafe.csv`
   - more radical local counterfactual bet;
   - useful if we want to test the unsmoothed H057/H088 conflict field.

If H098 loses, the next big bet should not be another cell gradient. It should
be a row/route assignment solver that preserves H098's frontier weighting but
chooses whole route templates under constraints.

### H099 Update

H099 executed that next bet.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H099 | `submission_h099_route_equation_1cbff4af_uploadsafe.csv` | H098 signed conflict cells are safe only as coherent row-route assignments | `15` routes / `26` cells / `15` rows | H088-opposite `1.0`, H057-align `1.0`, model delta `-0.000244` | clean route-assignment sensor |

Breakthrough reading:

```text
The route-constrained solver can make the H098 conflict field cleaner and more
interpretable, but it does not yet reveal a high-assignment H071 law. It is a
test of assignment discreteness, not a proven 0.53 mechanism.
```

Current high-information submission order:

1. `submission_h099_route_equation_1cbff4af_uploadsafe.csv`
   - if we want to test the new active goal directly: row-target assignment
     equation vs sparse cell equation.

2. `submission_h098_frontier_equation_a748e477_uploadsafe.csv`
   - if we want the cleaner H088-weighted cell-equation test with slightly
     broader support.

Decision rule:

- H099 better than H098: assignment constraints matter; build HS-JEPA v3 around
  row-route solver.
- H098 better than H099: the useful hidden law is sparse signed toxicity, and
  H071 route templates are too rigid.

### H100 Update

H100 turns the row-route idea into an explicit public equation basis.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H100 | `submission_h100_route_basis_6c8e0c6b_uploadsafe.csv` | known public submissions are best explained by signed overlap with route-action basis vectors | `24` actions / `28` cells / `24` rows | route-basis delta `-0.001031`, H098 cell delta only `-0.000045` | high-risk equation-space bet |

Breakthrough reading:

```text
H100 is the strongest current "worldview-changing" submission candidate. It
does not merely constrain H098; it claims the public/private equation has a
different coordinate system: route-action overlap. The main evidence is
frontier-weighted route-basis LOO MAE 0.000217 and correct H088 sign, but the
main risk is disagreement with H098's cell-equation decoder.
```

Current high-information submission order:

1. `submission_h100_route_basis_6c8e0c6b_uploadsafe.csv`
   - biggest equation-space bet; if it wins, HS-JEPA's decoder becomes
     route-action basis public/private equation.

2. `submission_h099_route_equation_1cbff4af_uploadsafe.csv`
   - cleaner assignment-discreteness test with lower model disagreement.

3. `submission_h098_frontier_equation_a748e477_uploadsafe.csv`
   - safest H088-weighted sparse signed cell-equation test.

Decision rule:

- H100 wins materially: pursue route-basis equation and interaction decoding.
- H099 wins but H100 loses: assignment constraints help, direct route-basis
  response is overfit.
- H098 wins over both: route templates are too rigid; sparse signed cells are
  the live representation.

### H101 Update

H101 asks whether H100 needs a disagreement-toxicity gate.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H101 | `submission_h101_disagreement_toxicity_9e088156_uploadsafe.csv` | safe route-basis actions are only the subset that survive H098 cell-equation caution | `5` actions / `6` cells / `5` rows | route-basis delta `-0.000641`, cell-equation delta `-0.000014`, H057/H088 alignment `0.833333` | diagnostic toxicity-boundary bet |

Breakthrough reading:

```text
The broad H100 route-basis action field is not stable across equation variants.
The stable public/private disagreement field is tiny. That is useful evidence:
the next 0.53-scale breakthrough probably needs to discover a larger safe
assignment law, not just prune H100 harder.
```

Current high-information submission order:

1. `submission_h100_route_basis_6c8e0c6b_uploadsafe.csv`
   - best one-slot test if we want a world-changing route-equation bet.

2. `submission_h099_route_equation_1cbff4af_uploadsafe.csv`
   - best cleaner test if we want assignment discreteness with less H100-style
     regression risk.

3. `submission_h101_disagreement_toxicity_9e088156_uploadsafe.csv`
   - best diagnostic test if we specifically want to know whether H100 must be
     filtered through H098 toxicity caution.

Decision rule:

- H101 better than H100: toxicity-boundary/gating is real.
- H100 better than H101: H101 over-pruned the useful route-basis field.
- both weak: route-basis is a sensor space, not yet an action decoder.

### H102 Update

H102 changes the toxicity definition from local cell agreement to global
bad-axis projection.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H102 | `submission_h102_badnull_e775939d_uploadsafe.csv` | safe assignment is H100 route-action gain in the nullspace of bad public submission axes | `5` actions / `7` cells / `5` rows | route-basis delta `-0.001162`, bad-axis positive projection `0.0`, H088-axis cosine `-0.002161` | sharp public-sensitive nullspace bet |

Breakthrough reading:

```text
H102 is the cleanest equation-solver version of the current goal. It does not
ask whether H100 action is stable across models; it asks whether action
toxicity is projection onto known bad public directions. The selected action is
small but very concentrated on a suspected public-sensitive id06/id07 block.
```

Current high-information submission order:

1. `submission_h100_route_basis_6c8e0c6b_uploadsafe.csv`
   - biggest route-equation worldview bet.

2. `submission_h102_badnull_e775939d_uploadsafe.csv`
   - best test of action toxicity as bad-axis nullspace; smaller but cleaner
     than H100 in public/private safety geometry.

3. `submission_h099_route_equation_1cbff4af_uploadsafe.csv`
   - cleaner assignment-discreteness test.

4. `submission_h101_disagreement_toxicity_9e088156_uploadsafe.csv`
   - diagnostic test for H098 cell-equation gating.

Decision rule:

- H102 beats H100: build HS-JEPA v3 around global toxicity subspace and
  constrained route-action assignment.
- H100 beats H102: route-basis public response should not be constrained by
  old bad-axis geometry.
- H102 moves little: 7-cell nullspace is too small; test the broader
  `h102_strict_null_conflict` alternate or learn a denser safe route family.

### H103 Update

H103 tests whether the safe nullspace can be expanded by toxic-shadow
cancellation.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H103 | `submission_h103_shadowcancel_89496ed5_uploadsafe.csv` | dense conflict route-actions can cancel toxic bad-axis shadows while keeping route-basis gain | `23` actions / `28` cells / `23` rows | route-basis delta `-0.002438`, bad-axis positive projection `0.0`, H088-axis cosine `-0.008946` | strongest current equation-solver bet |

Breakthrough reading:

```text
H103 is the first candidate that is both larger than the tiny H102 nullspace
and safer than H100 under bad-axis geometry. If public confirms it, the
action-grade HS-JEPA decoder is not a gate but a constrained portfolio solver.
```

Current high-information submission order:

1. `submission_h103_shadowcancel_89496ed5_uploadsafe.csv`
   - strongest current direct test of public/private row-target equation
     solving; dense enough to matter, still bad-axis safe.

2. `submission_h100_route_basis_6c8e0c6b_uploadsafe.csv`
   - biggest unconstrained route-equation worldview bet.

3. `submission_h102_badnull_e775939d_uploadsafe.csv`
   - smaller strict bad-axis nullspace bet.

4. `submission_h099_route_equation_1cbff4af_uploadsafe.csv`
   - route assignment discreteness test.

Decision rule:

- H103 wins: pursue HS-JEPA v3 as a toxic-shadow cancellation portfolio solver.
- H102 wins but H103 loses: the nullspace is real but must stay sparse.
- H100 wins while H102/H103 lose: bad-axis constraints are over-constraining
  the true positive route-basis law.

### H104 Update

H104 tests whether the route-action law should be residualized before
submission.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H104 | `submission_h104_toxicresid_52f826e6_uploadsafe.csv` | raw route-actions contain a toxic public-axis component; safe action is the residual transported back to row-target cells | `47` source actions / `87` cells / `64` rows | route-basis delta `-0.001758`, bad-axis positive projection `0.0`, H088-axis cosine `-0.033173` | high-risk residual-decoder bet |

Breakthrough reading:

```text
H104 changes the decoder class. H103 chooses route-actions that are safe as a
portfolio; H104 first creates a desired route field, projects away the positive
component along bad public axes, then decodes the residual vector. If public
confirms H104, HS-JEPA should become a residual route-field transport model
rather than a discrete route-action selector.
```

Current high-information submission order:

1. `submission_h103_shadowcancel_89496ed5_uploadsafe.csv`
   - cleanest current equation-solver candidate.

2. `submission_h104_toxicresid_52f826e6_uploadsafe.csv`
   - bigger worldview test: toxic action might be a removable public-axis
     component.

3. `submission_h100_route_basis_6c8e0c6b_uploadsafe.csv`
   - unconstrained route-equation stress test.

Decision rule:

- H104 beats H103/H100: decode residualized route fields; toxic action is a
  removable public-axis component.
- H103 beats H104: projection destroys row-target semantics; keep route-actions
  discrete and solve constrained portfolios.
- H100 beats both: bad-axis constraints are over-constraining the real route
  law and should become soft diagnostics only.

### H105 Update

H105 tests whether route-actions should be solved as signed coefficient basis
functions.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H105 | `submission_h105_signedcoef_8f0e502e_uploadsafe.csv` | route-action coefficients collapse into a tiny safe id06/id07 row-target kernel | `29` coefficient terms / `8` cells / `4` rows | route-basis delta `-0.002727`, bad-axis positive projection `0.0`, H088-axis cosine `-0.007302` | sparse kernel bet |

Breakthrough reading:

```text
The expected signed coefficient solution did not use counter terms. The
selected H105 candidate used 29 positive route terms but decoded to only 8
cells on rows 144, 146, 151, and 164. This suggests a route-consensus kernel:
many semantic route-actions agree on the same small public/private assignment.
```

Current high-information submission order:

1. `submission_h103_shadowcancel_89496ed5_uploadsafe.csv`
   - cleanest broad discrete portfolio-solver test.

2. `submission_h104_toxicresid_52f826e6_uploadsafe.csv`
   - broad residual transport decoder test.

3. `submission_h105_signedcoef_8f0e502e_uploadsafe.csv`
   - tiny route-consensus kernel test.

4. `submission_h100_route_basis_6c8e0c6b_uploadsafe.csv`
   - unconstrained route-equation stress test.

Decision rule:

- H105 wins: exploit and expand the id06/id07 route-consensus kernel.
- H103/H104 win over H105: the kernel is real but too narrow; action safety is
  portfolio/residual-field level.
- H105 loses badly: route-basis predicted gain can be overconcentrated, and the
  decoder needs diversity constraints.

### H106 Update

H106 tests whether the H105 tiny kernel is expandable by route-consensus votes.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H106 | `submission_h106_routeconsensus_f315d99a_uploadsafe.csv` | H105's tiny id06/id07 kernel is a seed of a broader route-consensus field | `220` source actions / `48` cells / `22` rows | route-basis delta `-0.000796`, bad-axis positive projection `0.0`, mean vote consensus `1.0` | kernel-transfer bet |

Breakthrough reading:

```text
H106 is the cleanest expansion test after H105. It gives up some route-basis
predicted gain versus H105 but expands from 8 cells to 48 cells while preserving
bad-axis silence. The decisive question is whether public rewards the density
or punishes leaving the exact id06/id07 kernel.
```

Current high-information submission order:

1. `submission_h103_shadowcancel_89496ed5_uploadsafe.csv`
   - broad discrete portfolio-solver test.

2. `submission_h104_toxicresid_52f826e6_uploadsafe.csv`
   - broad residual transport decoder test.

3. `submission_h105_signedcoef_8f0e502e_uploadsafe.csv`
   - tiny route-consensus kernel test.

4. `submission_h106_routeconsensus_f315d99a_uploadsafe.csv`
   - kernel expansion/transfer test.

Decision rule:

- H106 beats H105: expand the kernel by consensus-vote fields.
- H105 beats H106: keep the kernel sharp; do not spread it by route votes.
- H103/H104 beat both: route-consensus cells are subordinate diagnostics, and
  the action-grade decoder should stay portfolio/residual based.

### H107 Update

H107 tests whether the H088 negative public sensor can be inverted into an
action field.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H107 | `submission_h107_antipode_a0ea1eec_uploadsafe.csv` | H088's toxic action vector has a constrained safe antipode | `26` cells / `19` rows | H088-axis cosine `-0.022682`, H106 alignment `1.0`, route-basis delta `-0.000079` | antipode-decoder bet |

Breakthrough reading:

```text
H107 does not merely avoid H088. It asks whether H088's failure defines a
signed toxic field whose opposite direction becomes useful when H106 consensus
and H057-positive support agree. The surviving candidate is small and non-Q2;
blanket H088 reversal did not survive internal stress.
```

Current high-information submission order:

1. `submission_h103_shadowcancel_89496ed5_uploadsafe.csv`
   - broad discrete portfolio-solver test.

2. `submission_h104_toxicresid_52f826e6_uploadsafe.csv`
   - broad residual transport decoder test.

3. `submission_h105_signedcoef_8f0e502e_uploadsafe.csv`
   - tiny route-consensus kernel test.

4. `submission_h106_routeconsensus_f315d99a_uploadsafe.csv`
   - kernel expansion/transfer test.

5. `submission_h107_antipode_a0ea1eec_uploadsafe.csv`
   - negative-sensor antipode decoder test.

Decision rule:

- H107 wins: negative public sensors are action-generating signed constraints.
- H107 loses while H103/H104/H105/H106 win: negative sensors should stay as
  toxicity vetoes.
- H107 loses badly: public toxicity is not sign-symmetric, so antipode
  decoding is a dead branch.

### H108 Update

H108 tests whether independent HS-JEPA decoders agree on the action-grade
row-target field.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H108 | `submission_h108_jury_610a26a0_uploadsafe.csv` | safe assignment is the signed intersection of H103-H107 decoder families | `19` source candidates / `47` cells / `27` rows | route-basis delta `-0.001528`, bad-axis positive projection `0.0`, mean family count `3.85` | decoder-jury bet |

Breakthrough reading:

```text
H108 is the first solver that treats previous HS-JEPA branches as witnesses
rather than as mutually exclusive submissions. The promoted field is non-Q2,
bad-axis silent, and has perfect family sign consensus. It tests whether public
safety comes from decoder-family agreement instead of branch-specific score.
```

Current high-information submission order:

1. `submission_h108_jury_610a26a0_uploadsafe.csv`
   - best test of the system-level row-target assignment equation.

2. `submission_h103_shadowcancel_89496ed5_uploadsafe.csv`
   - broad discrete portfolio-solver branch.

3. `submission_h104_toxicresid_52f826e6_uploadsafe.csv`
   - broad residual transport branch.

4. `submission_h105_signedcoef_8f0e502e_uploadsafe.csv`
   - tiny route-consensus kernel branch.

5. `submission_h106_routeconsensus_f315d99a_uploadsafe.csv`
   - kernel expansion/transfer branch.

6. `submission_h107_antipode_a0ea1eec_uploadsafe.csv`
   - negative-sensor antipode branch.

Decision rule:

- H108 wins: build HS-JEPA v3 around decoder-family jury intersection.
- H108 loses to one branch: action-grade structure is branch-specific, not
  consensus-based.
- H108 and all branches lose: H103-H108 are diagnostics, and a new public
  sensor/factor must be found.

### H109 Update

H109 tests whether whole HS-JEPA decoder submissions form a coefficient basis
for the hidden public/private equation.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H109 | `submission_h109_coeff_54147083_uploadsafe.csv` | safe assignment is a coefficient-decoded kernel from H103-H108 decoder basis vectors | `20` source candidates / `4` cells / `2` rows | route-basis delta `-0.001862`, full-field route delta `-0.004404`, bad-axis positive projection `0.0` | coefficient-kernel bet |

Breakthrough reading:

```text
H109 is a negative/positive hybrid.  It failed to produce a broad
coefficient-composed action field, but that failure is informative: the solver
collapsed to H105-derived id06/id07 cells under public/private stress.  The
live question is whether the hidden action unit is this tiny coefficient kernel
or whether the collapse is too sharp for public.
```

Current high-information submission order:

1. `submission_h108_jury_610a26a0_uploadsafe.csv`
   - best test of decoder-family intersection as the action equation.

2. `submission_h109_coeff_54147083_uploadsafe.csv`
   - sharpest test of coefficient-decoded id06/id07 kernel.

3. `submission_h103_shadowcancel_89496ed5_uploadsafe.csv`
   - broad discrete portfolio-solver branch.

4. `submission_h104_toxicresid_52f826e6_uploadsafe.csv`
   - broad residual transport branch.

5. `submission_h105_signedcoef_8f0e502e_uploadsafe.csv`
   - original tiny route-consensus kernel branch.

Decision rule:

- H109 beats H108/H105: build HS-JEPA v3 around coefficient-decoded sparse
  kernels.
- H108 beats H109: decoder-family intersection is the safer assignment law.
- H105 beats H109: coefficient decoding removed useful H105 cells.
- Broad branches beat H108/H109/H105: kernel solvers are too narrow, and the
  next big bet must return to public/private portfolio or residual transport.

### H110 Update

H110 tests whether row-target assignment should be performed after separating
benefit from public toxicity.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H110 | `submission_h110_toxgap_7b02f196_uploadsafe.csv` | safe assignment is positive benefit-toxicity gap under H102 bad-axis stress | `21` source candidates / `37` cells / `23` rows | route-basis delta `-0.001037`, H098 delta `-0.000037`, bad-axis positive projection `0.0`, H088 cosine `-0.008961` | benefit-toxicity solver bet |

Breakthrough reading:

```text
H110 is the first explicit action-toxicity factorization after H088. It
explains H108 as too broad and H109 as too sharp. The promoted field keeps 29
H108 cells but only 1 H109 cell, so it is a new low-toxicity kernel-release
assignment rather than a H109 replay.
```

Current high-information submission order:

1. `submission_h110_toxgap_7b02f196_uploadsafe.csv`
   - direct test of the active goal: benefit-toxicity factorization.

2. `submission_h108_jury_610a26a0_uploadsafe.csv`
   - decoder-family intersection without explicit local toxicity separation.

3. `submission_h109_coeff_54147083_uploadsafe.csv`
   - coefficient-decoded micro-kernel.

4. `submission_h103_shadowcancel_89496ed5_uploadsafe.csv`
   - broad toxic-shadow portfolio.

5. `submission_h104_toxicresid_52f826e6_uploadsafe.csv`
   - broad residual transport.

Decision rule:

- H110 wins: prioritize explicit toxicity field and assignment field
  factorization in HS-JEPA v3.
- H108 wins: family agreement is more robust than local toxicity scoring.
- H109 wins: public-safe action is much sharper than H110's release field.
- Broad H103/H104 win: the action unit is not sparse cell assignment; return to
  portfolio/residual public/private transport.

### H111 Update

H111 tests whether H110's local benefit/toxicity representation needs a global
boundary solver.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H111 | `submission_h111_boundary_7cbf5e9d_uploadsafe.csv` | safe assignment is a global beam/knapsack boundary over H110 benefit/toxicity cells | `53` cells / `28` rows / `14` rescued H108-rejected cells | route-basis delta `-0.000680`, H098 delta `-0.000020`, bad-axis positive projection `0.0`, H088 cosine `-0.015318` | global-boundary bet |

Breakthrough reading:

```text
The surprise is that H108-rejected cells had better local gap than H108-kept
cells.  H110's problem was not the benefit/toxicity representation itself; it
was the greedy assignment boundary.  H111 promotes a broader H108-like field
while keeping H102 bad-axis silence.
```

Current high-information submission order:

1. `submission_h111_boundary_7cbf5e9d_uploadsafe.csv`
   - direct test of global assignment over the toxicity field.

2. `submission_h110_toxgap_7b02f196_uploadsafe.csv`
   - local benefit-toxicity gap solver.

3. `submission_h108_jury_610a26a0_uploadsafe.csv`
   - family-intersection baseline for H111.

4. `submission_h109_coeff_54147083_uploadsafe.csv`
   - tiny coefficient-kernel counter-world.

Decision rule:

- H111 wins: build HS-JEPA v3 around a global action-boundary solver.
- H110 wins: local toxicity-gap filtering is enough; H111 over-rescued H108.
- H108 wins: explicit toxicity modeling is unnecessary or harmful.
- H109 wins: the real assignment is a small kernel, not a broad boundary.

### H112 Update

H112 tests whether the global boundary must be filtered by a public-residual
toxicity field.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H112 | `submission_h112_residualtox_68b26f11_uploadsafe.csv` | safe assignment is H111 global boundary pruned by H098 LOO public-residual toxicity | `40` cells / `23` rows / `37` H111-overlap cells | route-basis delta `-0.000980`, H098 delta `-0.000018`, bad-axis positive projection `0.0`, H088 cosine `-0.011878` | residual-toxicity assignment bet |

Breakthrough reading:

```text
H112 turns known public LB residuals into a row-target action toxicity field.
The strongest effective bad residual sources are H010, LeJEPA strict, and
E216.  H112 keeps the H111 worldview but prunes the boundary from 53 cells to
40 cells using this residual field.  This is a different claim from H110/H111:
the action-grade decoder is not local toxicity or global boundary alone, but
public-residual toxicity over that boundary.
```

Current high-information submission order:

1. `submission_h112_residualtox_68b26f11_uploadsafe.csv`
   - tests public-residual toxicity projection over H111.

2. `submission_h111_boundary_7cbf5e9d_uploadsafe.csv`
   - tests global boundary without residual projection.

3. `submission_h110_toxgap_7b02f196_uploadsafe.csv`
   - local benefit-toxicity gap solver.

4. `submission_h109_coeff_54147083_uploadsafe.csv`
   - tiny coefficient-kernel counter-world.

Decision rule:

- H112 wins: HS-JEPA needs a residual-toxicity projection layer before final
  assignment.
- H111 wins: global boundary is the right layer and H112 over-pruned it.
- H110 wins: LOO residuals are too underidentified; local benefit/toxicity is
  safer.
- H109 wins: all broad assignment solvers are too diffuse.

### H113 Update

H113 tests whether the assignment unit is a row-target route bundle rather
than an individual residual-toxic cell.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H113 | `submission_h113_rowroute_04369be5_uploadsafe.csv` | public-safe action is a row-route equation: one bundle per row under residual-toxicity and bad-axis constraints | `37` cells / `14` rows / `14` bundles | route-basis delta `-0.000597`, H098 delta `-0.000019`, bad-axis positive projection `0.0`, H088 cosine `-0.001766` | row-route assignment bet |

Breakthrough reading:

```text
H113 did not create a far-away action direction.  It is H112 compressed into
row-level target bundles: H112 cosine 0.851031, but only 14 rows and 14
bundles.  This is still useful because it directly asks whether public safety
is attached to row-target routes rather than isolated cells.
```

Current high-information submission order:

1. `submission_h113_rowroute_04369be5_uploadsafe.csv`
   - tests row-route action assignment over residual toxicity.

2. `submission_h112_residualtox_68b26f11_uploadsafe.csv`
   - cell-level residual-toxicity projection.

3. `submission_h111_boundary_7cbf5e9d_uploadsafe.csv`
   - global boundary without residual projection.

4. `submission_h110_toxgap_7b02f196_uploadsafe.csv`
   - local benefit-toxicity gap solver.

Decision rule:

- H113 wins: promote row-route equation solver as HS-JEPA's action decoder.
- H112 wins: keep residual toxicity at cell level; row bundles are too rigid.
- H111 wins: public residuals are not reliable enough for action decoding.
- H110/H109 win: return to smaller local/kernel action fields.

### H114 Update

H114 is the first explicit toxic-subspace nullspace decoder.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H114 | `submission_h114_nullspace_73fe7866_uploadsafe.csv` | safe action is obtained by projecting candidate human-state moves into the nullspace of known toxic public directions before assignment | `27` cells / `25` rows / H112 cosine `0.033494` | toxic projection ratio `0.047395`, H088 cosine `-0.010421`, bad-axis positive projection `0.0` | high-risk nullspace bet |

Breakthrough reading:

```text
H114 deliberately violates the conservative local proxy ranking: H098 and
route-basis predict tiny worsening, but the action is almost orthogonal to
H112/H113 and removes 95% of the restricted toxic projection.  If it works,
the current public-equation proxies are part of the plateau rather than the
solution.
```

Current high-information submission order:

1. `submission_h114_nullspace_73fe7866_uploadsafe.csv`
   - world-changing test of toxic-subspace null decoding.

2. `hitl/h114_toxic_subspace_null_solver_hsjepa/submission_h114_null_h010_e216_antidote_c72_a060_4232eefa.csv`
   - safer H114 sibling: named H010/E216/LeJEPA toxic-axis antidote.

3. `submission_h113_rowroute_04369be5_uploadsafe.csv`
   - row-route assignment compression of H112.

4. `submission_h112_residualtox_68b26f11_uploadsafe.csv`
   - cell-level public-residual toxicity.

Decision rule:

- H114 wins: promote toxic-subspace projection as HS-JEPA's action decoder.
- H114 fails but H112/H113 survive: projection is too aggressive; keep
  toxicity as a selector/stress field.
- H114 fails badly: public bad vectors do not define a stable linear subspace.
- Safer H114 sibling wins if tested: nullspace is real but must be anchored to
  named residual-bad axes, not novelty.

### H115 Update

H115 tests whether the public/private action equation is nonlinear in
row-target space.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H115 | `submission_h115_curvature_23748467_uploadsafe.csv` | safe assignment requires a second-order row-target curvature equation; Q2 can re-enter only as a companion route | `20` cells / `16` rows / `8` Q2 cells | curvature delta `-0.000251`, H088 LOO sign ok, H088 cosine `-0.003903`, H112 cosine `0.247554` | nonlinear action-equation bet |

Breakthrough reading:

```text
H115 is not a safer H112/H113/H114 sibling.  It uses known public actions to
learn which row-target interactions are punished after first-order public
response is accounted for.  Its most important claim is that Q2 is not always
toxic; Q2 may be safe only when assigned as a low-curvature companion route.
```

Current high-information submission order:

1. `submission_h115_curvature_23748467_uploadsafe.csv`
   - tests second-order row-target action equation and Q2 companion reopening.

2. `submission_h114_nullspace_73fe7866_uploadsafe.csv`
   - tests toxic-subspace null decoding as a stronger break from linear
     public equations.

3. `submission_h112_residualtox_68b26f11_uploadsafe.csv`
   - tests cell-level public-residual toxicity.

4. `submission_h113_rowroute_04369be5_uploadsafe.csv`
   - tests row-route compression of residual toxicity.

Decision rule:

- H115 wins: build HS-JEPA v5 around nonlinear row-target equation decoding.
- H115 loses but H114 wins: toxic nullspace is the stronger plateau breaker.
- H115 loses but H112/H113 win: second-order public fit over-reintroduced Q2;
  keep residual toxicity as selector and leave Q2 mostly blocked.
- H115 loses badly: H088-like negative sensors predict real Q2/action toxicity
  and curvature should remain diagnostic only.

### H116-H117 Update

H116 and H117 are negative breakthrough probes.  They did not produce a
submission, but they substantially changed the live worldview.

| Experiment | Core claim | Result | Status |
| --- | --- | --- | --- |
| H116 | Q2 companion rescue is safe if same-row companions cancel curvature toxicity | rescue exists, but every positive-rescue bundle is H088-positive | Q2 companion safety mostly rejected |
| H117 | the forbidden Q2 companion sector can be inverted into non-Q2 safe assignments | only `4/2192` proposal cells have positive antipode gap; no candidate survives stress | simple forbidden-sector inversion rejected |

Breakthrough reading:

```text
The Q2 companion sector is real but toxic.  It is not a safe assignment field
under current equations, and its opposite direction is nearly absent from the
current proposal space.
```

Updated high-information submission order:

1. `submission_h115_curvature_23748467_uploadsafe.csv`
   - high-risk sensor only: tests whether public contradicts the H116/H117
     local toxicity diagnosis.

2. `submission_h114_nullspace_73fe7866_uploadsafe.csv`
   - tests toxic-subspace null decoding, now more attractive because Q2
     companion conservation failed as safe action.

3. `submission_h112_residualtox_68b26f11_uploadsafe.csv`
   - tests non-Q2 residual toxicity assignment.

Decision rule:

- H115 wins: public accepts a narrow Q2 exception that local H116/H117 could
  not certify.
- H115 loses: lock Q2 companion sector as toxic/veto representation.
- H114 or H112 wins: proceed with non-Q2 toxicity/nullspace decoders as the
  main HS-JEPA action layer.

### H118 Update

H118 is the first big bet after the goal moved from hidden-state discovery to
row-target action toxicity and safe assignment.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H118 | `submission_h118_forbiddenveto_e81167a8_uploadsafe.csv` | H116/H117's Q2 companion sector is useful as a veto, not as an action target; safe assignment is non-Q2 residual/nullspace/antidote under that veto | `52` cells / `34` rows / `0` Q2 cells | forbidden exposure `0`, bad-axis positive projection `0`, H088 cosine `-0.003628`, route-basis delta `-0.000568` | forbidden-sector veto bet |

Breakthrough reading:

```text
The important move is not another encoder or another blend.  H118 separates
three objects: a real hidden representation, a public-toxic action sector, and
a safe assignment field.  This is the action-grade version of HS-JEPA.
```

Updated high-information submission order:

1. `submission_h118_forbiddenveto_e81167a8_uploadsafe.csv`
   - tests forbidden-sector veto plus non-Q2 safe assignment.

2. `submission_h115_curvature_23748467_uploadsafe.csv`
   - high-risk sensor for the narrow Q2 companion exception.

3. `submission_h114_nullspace_73fe7866_uploadsafe.csv`
   - tests toxic-subspace null decoding.

4. `submission_h112_residualtox_68b26f11_uploadsafe.csv`
   - tests cell-level residual public-toxicity assignment.

Decision rule:

- H118 wins: HS-JEPA v5.2 should make toxic hidden sectors first-class veto
  representations before row-target assignment;
- H118 loses but H114/H112 win: the forbidden sector diagnosis is right, but
  H118's selected antidote assignment is too broad or the veto removed useful
  cells;
- H115 wins while H118 loses: Q2 companion remains a narrow public-safe
  exception and cannot be globally vetoed;
- all lose: the public/private equation is not captured by current toxicity,
  nullspace, curvature, or forbidden-sector variables.

### H119-H120 Update

H119 and H120 test the next decoder split after H118.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H119 | none | H085 public posterior can be action-grade only if it passes forbidden-sector, H088, and curvature stress | no promoted candidate | strong local H085 pools existed, but direct posterior actions failed cumulative H088/good-margin gates | direct H085 action rejected |
| H120 | `submission_h120_toxrow_0b84c821_uploadsafe.csv` | H085 should be used as public-sensitive row sensor; action comes from Q/S residual stage assignment | `18` cells / `15` rows / `0` Q2 cells | bad-axis positive projection `0`, H088 cosine `-0.000003`, route-basis delta `-0.000229`, model delta `-0.000015` | row-sensor/action-solver split bet |

Breakthrough reading:

```text
The next HS-JEPA object is not a stronger posterior. It is a decoder that asks
which latent posterior signals are safe to materialize as row-target actions.
H119 rejects direct posterior action; H120 keeps H085 as context and lets the
stage residual solver act.
```

Updated high-information submission order:

1. `submission_h120_toxrow_0b84c821_uploadsafe.csv`
   - tests the new H085-as-row-sensor / residual-stage-action split.

2. `submission_h118_forbiddenveto_e81167a8_uploadsafe.csv`
   - tests forbidden-sector veto plus non-Q2 safe assignment without H085 row
     localization.

3. `submission_h114_nullspace_73fe7866_uploadsafe.csv`
   - tests toxic-subspace null decoding.

4. `submission_h112_residualtox_68b26f11_uploadsafe.csv`
   - tests cell-level residual public-toxicity assignment.

Decision rule:

- H120 wins: promote HS-JEPA v5.3, where predicted representation and safe
  action are separate heads;
- H118 wins but H120 loses: H085 row sensor is contaminated; action solver
  should stay residual/nullspace based;
- H120 and H118 both lose: current toxic-sector/veto view is diagnostic but
  not yet action-grade;
- H120 loses badly while direct posterior candidates win: H119's action veto
  was too strict and H085 posterior needs a softer decoder.

### H121 Update

H121 is the first row-regime partition solver after H120.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H121 | `submission_h121_rowsensorpart_d03abb5b_uploadsafe.csv` | H085 toxic-posterior row sensor selects decoder regime: high-sensor rows override H118 with H120 stage actions | `44` cells / `31` rows / `0` Q2 cells | route-basis delta `-0.000580`, model delta `-0.000038`, H088 cosine `-0.039209`, good-bad margin `0.113396` | row-regime partition bet |

Breakthrough reading:

```text
The live 0.53 path is not "better H118" or "better H120" separately.  It is a
row-target equation that decides which decoder is allowed to act in which
hidden regime.
```

Updated high-information submission order:

1. `submission_h121_rowsensorpart_d03abb5b_uploadsafe.csv`
   - tests regime-partitioned action decoding.

2. `submission_h118_forbiddenveto_e81167a8_uploadsafe.csv`
   - tests the same forbidden-veto action field without H085 partition.

3. `submission_h120_toxrow_0b84c821_uploadsafe.csv`
   - tests the H085 row sensor as a standalone stage-action branch.

Decision rule:

- H121 wins: HS-JEPA's action decoder should be a mixture of solvers gated by
  hidden row-state/posterior sensors;
- H118 wins more: H085 toxic-posterior row partition is over-removing good
  H118 action;
- H120 wins more: high-sensor rows should dominate more aggressively;
- all three lose: the H085 row sensor is a coherent local diagnostic but not a
  public-safe assignment variable.

### H122 Update

H122 asks whether H121's improvement is caused by adding H120 replacement cells
or by deleting public-toxic H118 cells.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H122 | `submission_h122_pruneeq_0a9edcce_uploadsafe.csv` | safe assignment is the sparse residue after pruning public-toxic objective Q/S stage actions from H118 | `24` remaining cells / `19` rows; `28` H118 cells removed | route-basis delta `-0.000605`, model delta `-0.000029`, H088 cosine `-0.066158`, good-bad margin `0.125854` | subtractive action-equation bet |

Breakthrough reading:

```text
The next 0.53-scale object may not be a better hidden-state encoder or a
replacement branch. It may be an action-toxicity equation that knows which
locally plausible row-target corrections must be deleted before public/private
observation.
```

Updated high-information submission order:

1. `submission_h122_pruneeq_0a9edcce_uploadsafe.csv`
   - tests subtractive action-toxicity pruning.

2. `submission_h121_rowsensorpart_d03abb5b_uploadsafe.csv`
   - tests row-sensor partition with replacement.

3. `submission_h118_forbiddenveto_e81167a8_uploadsafe.csv`
   - tests the unpruned forbidden-sector action field.

Decision rule:

- H122 wins: promote HS-JEPA v5.5, where action safety starts with pruning
  public-toxic row-target cells before replacement/generation;
- H121 wins more: pruning must be followed by positive replacement in
  high-sensor rows;
- H118 wins more: pruning overfit stress axes and deleted useful cells;
- all lose: H118-derived action support is a diagnostic family, not the hidden
  assignment field.

### H123 Update

H123 tests whether H122 should stop after pruning or refill a tiny route-safe
complement.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H123 | `submission_h123_refilleq_8958f688_uploadsafe.csv` | H122 prune core is incomplete; refill only the route-safe complement | `26` cells / `20` rows; `2` refill cells | route-basis delta `-0.000732`, model delta `-0.000027`, H088 cosine `-0.065510`, good-bad margin `0.124697` | prune-then-refill bet |

Breakthrough reading:

```text
The current most precise HS-JEPA decoder is not "generate actions" but
"propose, prune public-toxic cells, then refill only a tiny route-complement
if the public/private equation remains stable."
```

Updated high-information submission order:

1. `submission_h123_refilleq_8958f688_uploadsafe.csv`
   - tests prune-then-route-refill.

2. `submission_h122_pruneeq_0a9edcce_uploadsafe.csv`
   - tests prune-only sparse core.

3. `submission_h121_rowsensorpart_d03abb5b_uploadsafe.csv`
   - tests row-sensor partition with replacement.

Decision rule:

- H123 wins: HS-JEPA v5.6 needs a route-complement refill stage after pruning;
- H122 wins more: pruning is enough and refill overfits route stress;
- H121 wins more: replacement should be controlled by row regime, not route
  complement;
- all lose: H118-derived proposal support is the wrong action family.

### H124 Update

H124 separates route-only refill from dual-sensor-safe refill.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H124 | `submission_h124_dualsensor_b8e822c0_uploadsafe.csv` | refill only cells that improve both route-basis and H098/frontier caution from H122 | `27` cells / `22` rows; `3` refill cells | route-basis delta `-0.000703`, model delta `-0.000031`, H088 cosine `-0.060942`, good-bad margin `0.144874` | dual-sensor refill bet |

Breakthrough reading:

```text
H123 and H124 are now a clean architecture fork.  H123 asks whether route
completion is the hidden public equation.  H124 asks whether route completion
must be certified by H098/model caution before the action is safe.
```

Updated high-information submission order:

1. `submission_h124_dualsensor_b8e822c0_uploadsafe.csv`
   - tests dual-sensor-safe refill.

2. `submission_h123_refilleq_8958f688_uploadsafe.csv`
   - tests route-first refill.

3. `submission_h122_pruneeq_0a9edcce_uploadsafe.csv`
   - tests prune-only sparse core.

Decision rule:

- H124 wins: HS-JEPA v5.7 should require route/H098 agreement before refill;
- H123 wins more: route-basis completion matters more than H098 caution;
- H122 wins more: no refill is safe;
- H121 wins more: row-regime replacement is the right second stage.

### H125 Update

H125 asks whether H124's refill should be closed at a subject-target bundle
level.

| Experiment | File | Core claim | Candidate scale | Main stress | Status |
| --- | --- | --- | --- | --- | --- |
| H125 | `submission_h125_rowbundle_f3990392_uploadsafe.csv` | id04/S1 is a hidden row bundle; H124 left one safe S1 closure cell | `28` cells / `23` rows; `1` bundle-closure cell | route-basis delta `-0.000702`, model delta `-0.000031`, H088 cosine `-0.054369`, good-bad margin `0.154855` | narrow bundle-closure bet |

Breakthrough reading:

```text
Subject-target bundle completion is not broadly supported.  Only id04/S1
survived.  This weakens the idea that the next 0.53 jump is a generic row-bundle
solver, but it keeps a small bundle-closure stage alive after H124.
```

Updated high-information submission order:

1. `submission_h124_dualsensor_b8e822c0_uploadsafe.csv`
   - tests the main dual-sensor refill architecture.

2. `submission_h123_refilleq_8958f688_uploadsafe.csv`
   - tests route-first refill.

3. `submission_h125_rowbundle_f3990392_uploadsafe.csv`
   - tests narrow id04/S1 bundle closure.

Decision rule:

- H125 wins: add a subject-target closure phase after H124;
- H124 wins more: bundle closure is over-completion;
- H123 wins more: route completion matters more than bundle/H098 caution;
- H122 wins more: no refill stage is safe.

### H126 Update

H126 turns H122-H125 from discrete submissions into a coefficient equation over
action components:

```text
core = H122 prune residue
q3_refill = H123 single Q3 complement
s3_tail = H123 route tail beyond Q3
s1_margin = H124 dual-sensor S1 margin
id04_closure = H125 bundle closure
```

| Experiment | File | Core claim | Support | Equation diagnostics | Status |
| --- | --- | --- | --- | --- | --- |
| H126 | `submission_h126_coeffeq_3fe3eee4_uploadsafe.csv` | H125 closure is real but should be half-amplitude, not binary | `28` cells / `23` rows | route-basis `-0.000702`, model `-0.000031`, H088 cosine `-0.057670`, margin `0.149911` | coefficient-sensitive closure bet |

The exact H125 replay had the highest local score, so H126 explicitly avoids
promoting duplicate baseline hashes.  The only novel survivor is
`closure=0.5`; S3-tail and broad coefficient variants fail the cumulative
public/private gates.  This means coefficient solving is alive but narrow.

0.53 implication:

H126 is not a new 0.53-scale basin.  It strengthens the broader bet that the
breakthrough must be an action equation, but it also shows the current H122-H125
component basis is too small.  The next larger bet should discover a new basis
component, not keep tuning H126 coefficients.

Public interpretation:

- H126 win: add coefficient decoding after row-target assignment;
- H125 win more: full closure is correct and coefficient damping was too
  conservative;
- H124 win more: closure is toxic even when softened;
- H122/H123 win more: the later S1 margin/closure branch is the wrong action
  family.

### H127 Update

H127 asks whether H126 failed because the component coefficients were wrong, or
because the component basis itself was missing a residual action.

| Experiment | File | Core claim | Support | Equation diagnostics | Status |
| --- | --- | --- | --- | --- | --- |
| H127 | `submission_h127_residbasis_9b7f8d9a_uploadsafe.csv` | a single episode-neighbor S2 residual stabilizes public/private margin after H126 | `29` cells / `24` rows; added row `144` S2 | route delta from H126 `+0.000001`, H098 delta `-0.000000360`, H088 `-0.051158`, margin `0.160434` | narrow residual-margin bet |

The key diagnostic is that objective/Q/anti-H088/null-antidote residual pools
did not promote a component.  Only the episode-neighbor residual pool survived,
and only by adding one S2 cell.  H127 therefore does not open the 0.53 basin.
It says the known basis is still almost closed, with one possible margin
stabilizer.

Next big-bet implication:

Do not keep sweeping residual pools.  If H127 does not win publicly, the next
large move must change the proposal generator or the public/private equation
itself, not add one more residual cell.

### H128 Update

H128 executes that next proposal-generator bet.

| Experiment | File | Core claim | Support | Equation diagnostics | Status |
| --- | --- | --- | --- | --- | --- |
| H128 | `submission_h128_frontiervalue_a6a6e648_uploadsafe.csv` | H098 frontier value can regenerate action only inside H057/H088 conflict regions admitted by H127 toxicity gates | `32` cells / `27` rows; added S1 `2`, S4 `1` | route delta from H127 `+0.000004`, H098 delta `-0.000000258`, H088 `-0.046361`, margin `0.199979` | conflict-value regenerator bet |

Important negative result:

```text
pure H098 frontier descent did not produce an accepted multi-cell candidate.
```

So the next 0.53-scale hypothesis is not "make H098 a stronger action head".
It is:

```text
separate value regeneration from action assignment.
value may be visible in H057/H088/H098 conflict geometry,
but public safety is decided by a sparse row-target toxicity equation.
```

If H128 wins publicly, the next breakthrough path is to build a larger
row-target assignment/equation solver around conflict-value proposals.  If it
loses, H128 kills the current value-regenerator branch and pushes the search
toward deleting toxic actions or solving public subset equations instead of
adding cells.

### H129 Update

H129 tests the deleting-toxic-actions branch directly.

| Experiment | File | Core claim | Support | Equation diagnostics | Status |
| --- | --- | --- | --- | --- | --- |
| H129 | `submission_h129_toxiceraser_ce1ebc19_uploadsafe.csv` | H122's sparse core still contains Q1/Q3 toxic amplitude; public/private safety needs a post-assignment eraser | `20` cells / `17` rows; removed Q1 `2`, Q3 `2`, damped Q1 `1` | route delta from H122 `-0.000005`, H098 delta `+0.000006`, H088 `-0.077331`, margin `0.130968` | core-toxicity eraser bet |

Why this is a bigger bet than H128:

```text
H128 asks whether we can add safe value after H127.
H129 asks whether the "safe" H122 core itself still contains toxic amplitude.
```

The positive local signal is not broad score tuning.  It specifically says
that Q1/Q3 actions inside the sparse core may be public-punished even when the
overall support has passed H122 toxicity pruning.

Decision rule:

- H129 win: HS-JEPA needs a toxicity/amplitude decoder after support selection;
- H122 win more: the eraser destroys real core signal and toxicity should be
  handled only before support selection;
- H128 win more: conflict-value generation is the higher-upside branch;
- all lose to H057: the post-H057 action-equation family is probably a local
  public-sensor overfit and the next 0.53 bet must leave this support manifold.

### H130 Update

H130 turns the previous branch choice into a single row-target lattice problem.

| Experiment | File | Core claim | Support | Equation diagnostics | Status |
| --- | --- | --- | --- | --- | --- |
| H130 | `submission_h130_lattice_69da8d10_uploadsafe.csv` | public/private safety is an off/damp/keep/add state assignment over discovered cells | `27` cells / `23` rows; off `3`, damp `5`, add `6` | route delta from H122 `-0.000034`, H098 delta `+0.000009`, H088 `-0.086159`, margin `0.271542` | full lattice decoder bet |

Why this is a bigger bet than H129:

```text
H129 says toxic amplitude exists inside the core.
H130 says toxicity and value are simultaneous cell-state assignments.
```

The selected H130 candidate starts from H122, removes/damps Q1/Q3 core cells,
and adds S1/S2/S4 value cells from later branches.  That is the first candidate
that expresses the full HS-JEPA row-target equation as a state lattice rather
than a sequence of handcrafted stages.

Decision rule:

- H130 win: prioritize row-target lattice decoding as the main HS-JEPA
  architecture;
- H129 win more: keep the eraser, but value-addition overfit local stress;
- H128 win more: conflict-value generation matters, but lattice erasure is too
  destructive;
- H122 win more: the current lattice score is over-optimistic and support
  assignment should stay sparse/core-first.

### H131 Update

H131 stress-tests the H130 lattice by applying sensor dropout to each proposed
cell-state transition.

| Experiment | File | Core claim | Support | Equation diagnostics | Status |
| --- | --- | --- | --- | --- | --- |
| H131 | `submission_h131_dropout_18a917f0_uploadsafe.csv` | H130's safe part is the value-add subset that survives without H088/margin as the main reward | `29` cells / `24` rows; add `5`, off/damp `0` | route delta from H122 `-0.000096`, H098 delta `-0.0000026`, H088 `-0.052815`, margin `0.161152`, mean dropout passes `3.8/4` | sensor-dropout value-add bet |

Why this matters:

```text
H130 says off/damp/add are all parts of one lattice.
H131 says only the add states are robust when H088/margin is not trusted.
```

That is not a small tune.  It separates the row-target equation into a
dropout-robust value field and an H088-dependent eraser field.  The 0.53 path
now has a sharper branch:

```text
If H131 wins: build HS-JEPA action decoder with sensor-dropout validation.
If H130 wins: public-specific H088/margin information is real, not shortcut.
If H129 wins: toxicity erasure is real but needs a better non-H088 proof.
```

Next big-bet implication:

The next experiment should not keep sweeping H131 thresholds.  It should build
a larger action-toxicity field that predicts erase/damp safety from held-out
sensor families, then compare that with the H131 value-add-only branch.

### H132 Update

H132 tests exactly that toxicity-field branch, but the result is narrower than
the initial bet.

| Experiment | File | Core claim | Support | Equation diagnostics | Status |
| --- | --- | --- | --- | --- | --- |
| H132 | `submission_h132_bundletox_ee252845_uploadsafe.csv` | H131's robust value additions need a small Q1 toxicity witness eraser from H129/H130 | `26` cells / `21` rows; Q1 off `3` | route delta from H131 `-0.000004`, H098 delta `-0.0000008`, H088 delta `-0.016821`, margin delta `+0.014924`, route-basis `-0.000705` | Q1 witness-toxicity bet |

Negative result:

```text
broad row-bundle toxicity did not promote.
H122 bundle-toxicity alone did not promote.
H131 + broad Q/S bundle erasure did not promote.
```

Positive result:

```text
H131 + Q1 witness erasure promoted.
```

0.53 implication:

The toxicity field is probably not a broad human-state bundle rule yet.  The
alive branch is smaller and sharper:

```text
H131 safe value field
  + Q1 witness toxicity field
```

If H132 wins publicly, expand from Q1 witness rows by learning their row-state
signature.  If H131 wins more, keep Q1 erasure as diagnostic only.  If H130
wins more, H132 was too conservative and public-specific H088/margin erasure
is real.
