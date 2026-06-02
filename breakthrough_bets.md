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

## Priority

Current order:

1. Submit or observe H071 if a public slot is available for the row-target
   assignment claim.
2. Submit H074 only if the next public slot is meant to test whether failed
   public worlds are positive contrastive target representations.
3. H072/H073 are now architecture evidence unless the next public question is
   specifically about human-social action-health.
4. Build the next solver that combines H071 assignment with H074
   anti-shortcut targets, rather than another threshold sweep.
5. H070/H069 follow-ups only if public feedback specifically supports smooth
   latent scoring or strict factorization.

H069 has answered the first public-free factorization question: the factors
are useful, but the standalone gated variant is unlikely to be the whole 0.53
route. H070 says smooth joint latent scoring is useful but not enough. H071
materializes exact assignment. H073 says human-social context is better as
continuous health/shortcut representation than direct assignment. H074 now says
known bad worlds carry a real inverse target representation, but also that this
inverse layer still needs a stronger action solver.
