# HS-JEPA Architecture

Last updated: 2026-06-02

## Purpose

Human-State JEPA, or HS-JEPA, is the working architecture for this competition.
It is not a name for a blend. It is a way to turn sleep lifestyle logs, public
LB observations, row order, target dependency, and human-social hypotheses into
latent human-state representations before writing probability corrections.

The current public frontier is
`submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv` with public LB
`0.5677475939`. The target 0.53 requires another `0.0377475939` improvement,
so local H057 tuning is not enough. HS-JEPA is only useful if it can expose a
new hidden-state law at H012 scale or larger.

## Core Definition

HS-JEPA predicts hidden human-state representations from partial context, then
decodes those representations into row-target correction fields.

```text
observed context C
  -> context encoder f(C)
  -> hidden human-state representation z
  -> action/route decoder g(z, base prediction)
  -> correction field delta_logit[row, target]
  -> submission probabilities
```

The model does not try to reconstruct raw feature values. It tries to answer:

- which rows belong to the same hidden human state;
- which target route is active on that row;
- which row-target actions are public-healthy;
- which public-equation state is likely public-only, private-safe, or invalid;
- which human-social story is a useful context view instead of a direct rule.

## Inputs

### Context Views

1. `C_row`: subject, row order, date, block, seed-neighbor, episode, transition
   phase, and row-responsibility signals.
2. `C_human`: human/social/lifestyle story features from raw logs and the
   1000 hypothesis pool, including morning aftereffect, nocturnal phone use,
   routine pressure, weekend rhythm, cashflow/month boundary, recovery, and
   measurement confidence.
3. `C_action`: existing submission disagreements, known public interventions,
   movement tensors, bad-anchor axes, and H057-relative action features.
4. `C_target`: Q/S target dependency, Q2 phase, S-stage routes, full-vector row
   route, and target-specific residual geometry.
5. `C_public`: known public LB equations treated as a sensor of public subset,
   not as the final truth.

### Target Representations

HS-JEPA currently has these target representations:

| Target representation | Evidence | Status |
| --- | --- | --- |
| Public-equation latent `z_public` | H012 improved E247 by `0.0080354663` | Strong, public-confirmed |
| Q2 phase `z_q2_phase` | H042 improved H012 by `0.0002186583` | Public-confirmed, small |
| Full row-state `z_row_state` | H057 improved H042 by `0.0001572309` | Public-confirmed, compact |
| Human-context seed state `z_human_context` | H063 selected 72 context-nearest rows, pending public | Public-free, not confirmed |
| Contrastive state boundary `z_state_boundary` | H064 used H050-null hard negatives, pending public | Public-free, not confirmed |
| Transition/episode state `z_sequence` | H065/H066 decode pre/post/episode routes, pending public | Public-free, not confirmed |
| Row responsibility `z_row_resp` | H067 fits public-weighted rows, pending public | Public-free, not confirmed |
| Cell action-health `z_action_health` | H068 fits H057-relative public actions with LOO MAE `0.000331247` | Public-free, high-risk |
| Private-safe invariant `z_private` | H069 factorized public/invariant/shortcut scores | Implemented, weak standalone upside |
| Joint correction-field latent `z_hsjepa` | H070 masked-view decoder predicts public/private/action representations | Implemented v1, not yet 0.001-grade |
| Discrete route assignment `z_assignment` | H071 assigns row-target route templates before materializing cells | Implemented, first near-0.001 big bet |
| Human-social route prior `z_human_social` | H072 maps 1000 stories to route priors and E268 row-family latents | Implemented as sensor; action-health useful, route proof failed null |
| Human action-health bridge `z_human_action` | H073 predicts H068 action-health/shortcut from story+route context | Implemented; continuous health works, hard cell generalization weak |
| Anti-shortcut inverse `z_anti_shortcut` | H074 uses known public-bad movements as contrastive targets and inverts their row-target direction | Implemented; negative latent is real under null, action still below 0.001 gate |
| Anti-bad value transport `z_bad_transport` | H075 uses inverse bad-anchor movement as the probability transport field | Tested; support survives, value decoder weak |
| Route-conditioned value law `z_route_value` | H087 decodes each H071 route with H085/H082/H018 value laws | Implemented; posterior and hard-world heads conflict |
| Dual public/private value gate `z_dual_value` | H088 accepts only route-actions that improve H085 posterior and H018 hard-world simultaneously | Implemented; cleaner dual-head decoder, lower posterior edge |

## Objective

HS-JEPA v1 uses representation prediction and action-health validation rather
than direct label loss only.

```text
L_total =
  L_repr(context_mask -> target_repr)
  + L_action(decoder(z) -> known action response)
  + L_route(row-target route consistency)
  + L_health(negative-anchor and null-action penalties)
  + L_geometry(non-collapse / non-shortcut diagnostics)
```

The concrete implementation can use ridge, tree, neural, graph, assignment, or
solver components. The required property is not the model class. The required
property is that the model predicts a hidden representation and survives
counterfactual stress.

## Masking Strategy

Random column masking is not the main task. HS-JEPA masks meaningful structure:

- mask public LB observation and recover the public-equation phase;
- mask Q2 and recover full non-Q2 row-state route;
- mask H057 seed rows and recover seed-neighbor state rows;
- mask H050-null rows and learn a positive/null state boundary;
- mask subject episodes and recover pre/bridge/post transition route;
- mask action outcomes and recover cell-level action-health;
- mask human-story families and recover row-target correction fields.

## Decoder

The decoder never directly emits "better probabilities" without a target
representation. It emits:

- row membership score;
- target route score;
- action-health score;
- public/private responsibility;
- correction field in logit space.

Final probabilities are produced only after upload-safety checks:

- exact key order;
- shape `(250, 10)`;
- no duplicate keys;
- no NaN;
- clipped probability range;
- target movement audit versus current frontier.

## LeJEPA-Style Health Checks

A latent is not accepted because it looks good once. It must survive at least
two independent checks:

- leave-one-public-observation out;
- leave-family or leave-branch out;
- H050-null or known-failed-anchor rejection;
- row permutation or target permutation negative control;
- bad-axis cosine check;
- public/private-like stress;
- q posterior consistency;
- action-health sign accuracy;
- row-target identity preservation;
- no collapse into all-row, all-target, or prior-only moves.

## Current Architecture Maturity

| Layer | Maturity | Notes |
| --- | --- | --- |
| Public-equation target | Strong | H012 is the first large proof |
| Row-state target | Medium-strong | H057 confirms compact row-state |
| Human-context encoder | Medium | H063 has coherent features, public pending |
| Contrastive boundary encoder | Medium | H064 is structurally clean, public pending |
| Action-health decoder | Medium | H068 has strong LOO sign, public pending |
| Private-safe factorization | Weak-medium | H069 works, but strict filtering shrinks expected movement |
| End-to-end HS-JEPA v1 | Prototype | H070 builds a joint latent decoder, but not yet a decisive action solver |
| Row-target assignment decoder | Prototype | H071 converts H070/H069/H068 energies into route templates and support |

## H070 v1 Implementation

H070 is the first concrete full HS-JEPA joint decoder:

```text
context / route / story / shortcut views
  -> masked-view prediction of public_score, private_safe_score,
     factor_action_score, invariant_score, shortcut_score
  -> latent_hsjepa_score
  -> row-target correction field toward H061 q061
```

Key diagnostics:

- `ctx_to_public` subject-group OOF Spearman: `0.819270`;
- `ctx_to_private` subject-group OOF Spearman: `0.941669`;
- `ctx_to_action` subject-group OOF Spearman: `0.928469`;
- `linear_ctx_private` OOF Spearman: `0.964882`;
- H068/H069 selected-cell AUC is weak (`~0.43-0.47`), meaning H070 is not just
  reconstructing existing threshold selections;
- top-200 latent cells are `90%` outside H069 and only `30.5%` overlapping
  H068;
- selected candidate changes `360` cells on `144` rows, with `323` cells
  outside H069 and public-action predicted delta `-0.000826` versus H057.

Interpretation: HS-JEPA can now predict hidden action representations from
visible context/route/story views, but this latent is not yet an action solver.
The next missing component is exact row-target assignment, not another smooth
latent score threshold.

## H071 Assignment Decoder

H071 adds the first discrete decoder:

```text
H070 latent + H069 factors + H068 action-health
  -> row-route template assignment
  -> row-target support
  -> logit correction toward H061 q061
```

It treats the action unit as a route on a row, not an independent cell. Route
templates include `full_state`, `nonq2_full`, `q3_s_stage`, `s_stage`,
`q2_hardtail`, `q2_s3_tail`, Q-only routes, and `recovery_route`.

The promoted H071 file changes `736` cells on `158` rows, with `642` cells
outside H069 and public-action predicted delta `-0.000983` versus H057. This
is not yet proof. Its role is to test whether assignment is the missing
decoder. A win means HS-JEPA should be written as context-to-state-to-route
prediction. A bad loss means the current route dictionary or action-health
translation is not valid, even if representation prediction remains useful.

## H072 Human-Social State Engine

H072 adds the first explicit human-social route-prior layer:

```text
1000 human stories + E268 story features
  -> story-family row latents
  -> route-template support
  -> H071 assignment candidate rescoring
  -> correction field toward H061 q061
```

This layer preserves the main HS-JEPA rule: stories do not directly push labels.
They only decide whether a row is eligible for a route such as `full_state`,
`q3_s_stage`, `q_subjective`, `s_stage`, or `recovery_route`.

Key diagnostics:

- promoted file:
  `submission_h072_humansocial_route_bae1edae_uploadsafe.csv`;
- changed cells / rows: `704` / `148`;
- route mix: `full_state:117`, `q3_s_stage:25`, plus small other routes;
- public-action predicted delta versus H057: `-0.000922`;
- responsibility-weighted delta versus H057: `-0.000935`;
- no positive bad-anchor cosine.

The important LeJEPA-style finding is negative: subject-preserving null
permutation did not validate story priors as H071-route rediscovery. Mean
H071-route support was `0.776796` real versus `0.783463` null. Therefore H072
is not paper-grade proof that human stories solve route assignment.

What it does prove is more specific: human-social families are not useless.
Bedtime arousal, cashflow stress, nocturnal awake, and bad-night aftereffect
showed strong row-level AUC against H068 action-health rows (`~0.697-0.720`).
So the next architecture version should route:

```text
C_human -> z_action_health / z_shortcut
```

before routing:

```text
z_action_health -> z_assignment
```

Direct `C_human -> z_assignment` is currently too weak.

## H073 Human Action-Health Bridge

H073 changes the human target representation:

```text
C_human + C_route
  -> z_action_health / z_shortcut
  -> z_assignment
  -> correction field toward H061 q061
```

The promoted file,
`submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv`, changes `657`
cells on `141` rows, with `557` cells outside H069, only `17` Q2 cells, and
public-action predicted delta `-0.000618` versus H057. It is a valid sensor but
not a `0.001`-scale public candidate.

The architecture result is the useful part:

- hard selected-cell prediction from stories is weak under subject-group OOF:
  `story_to_h068_selected` AUC `0.513105`;
- adding route context makes continuous action-health predictable:
  `story_route_to_h068_health` OOF Spearman `0.890901`;
- the same continuous health score has H071 selected-cell AUC `0.860064`.

This refines HS-JEPA:

```text
stories should predict continuous action-health / shortcut risk,
not hard row-target assignment labels.
```

The next version should use `z_human_action` as a regularized target
representation in the assignment solver, or build an anti-shortcut contrastive
view from known failed story/route combinations.

## H074 Anti-Shortcut State Inversion

H074 tests the negative side of HS-JEPA:

```text
known public-bad submissions
  -> z_shortcut
  -> cells where bad worlds move opposite to q061
  -> z_anti_shortcut
  -> row-route assignment
  -> correction field toward H061 q061
```

The promoted sensor,
`submission_h074_antishortcut_inversion_816703df_uploadsafe.csv`, changes
`597` cells on `152` rows, with `519` cells outside H069 and `278` outside
H070. It moves `42` Q2 cells, selects all `10` subjects, selects zero
H050-null cells, and keeps every tracked bad-anchor cosine non-positive.

Key diagnostics:

- target-stratified top-520 bad-axis shuffle:
  - `mean_true_opp_rank` z `9.270846`;
  - `mean_true_same_rank` z `-10.261358`;
  - `mean_shortcut_energy` z `-12.247887`;
  - `mean_cell_gain` z `3.050342`;
- public-action predicted delta versus H057: `-0.000840`;
- responsibility-weighted delta versus H057: `-0.000949`;
- route mix:
  `s_stage:46`, `recovery_route:23`, `q2_hardtail:23`,
  `nonq2_full:20`, `q3_s_stage:20`, `full_state:15`.

This is useful architecture evidence. Failed submissions are not only
"do-not-copy" examples; their opposite row-target direction is a structured
latent target. The limitation is just as important: the selected action does
not clear the `0.001` expected-movement gate. HS-JEPA should keep
`z_anti_shortcut` as a target representation, but the next 0.53-grade decoder
still needs a sharper public/private or route-assignment solver.

## H075 Anti-Bad Transport Decoder

H075 tests whether the H074 negative representation can also define values:

```text
known public-bad submission movement
  -> inverse movement vector
  -> z_bad_transport
  -> row-route assignment
  -> probabilities by anti-bad transport, not q061 movement
```

This is the direct follow-up to H074. H074 chose support from bad-opposition
but still moved selected cells toward q061. H075 asks whether the movement
itself should be the inverse of the bad-anchor vector.

The promoted diagnostic,
`submission_h075_antibad_transport_f6863945_uploadsafe.csv`, changes `524`
cells on `152` rows, with `458` cells outside H069 and `220` outside H070. It
moves `46` Q2 cells, selects all `10` subjects, selects zero H050-null cells,
and keeps every tracked bad-anchor cosine non-positive.

Key diagnostics:

- best selected candidate public-action predicted delta: `-0.000766`;
- responsibility-weighted delta: `-0.000912`;
- generated H075 candidates with public-action delta `<= -0.000800`: `0`;
- generated H075 candidates with public-action delta `<= -0.001000`: `0`;
- the top action candidate has transport alignment `0.711857` and transport
  gain rank `0.592239`, but still loses action scale versus H074.

Interpretation: `z_anti_shortcut` is a real support/energy representation, but
direct inverse-bad movement is not the value decoder under the current
geometry. HS-JEPA should not materialize bad-anchor inverse vectors directly.
The next decoder should use anti-shortcut as a constraint or energy term, then
learn values from public/private action response or route-specific label
worlds.

## What Would Prove HS-JEPA

HS-JEPA becomes paper-grade if we can show:

1. hidden human-state representations predict action-grade row-target routes;
2. public-equation latent is not merely public overfit;
3. human/social context can recover at least part of H057/H012 state;
4. action-health or assignment decoding produces a public move of at least
   `0.001` without relying on top-k micro tuning;
5. negative controls fail in the predicted way.

## What Would Falsify HS-JEPA

The current HS-JEPA route weakens if:

- H063/H064/H065/H066/H067/H068 all lose badly against H057;
- every context-discoverable human state fails public;
- only public-equation inversion works, and no private-safe or context-safe
  representation can translate it;
- action-health decoders fit known public anchors but repeatedly choose bad
  materializations.

In that case, H012/H057 remain useful contest discoveries, but HS-JEPA as a
general human-state architecture would need a new target representation.

## H076 Route-Specific Value Decoder

H076 separated support and value explicitly:

```text
z_anti_shortcut / z_action_health -> route support
route_name + human-state policy -> value decoder
```

The strongest promoted sensor was
`submission_h076_route_value_decoder_a91b64c7_uploadsafe.csv`.

- changed cells / rows versus H057: `471` / `153`;
- outside H069 cells: `411`;
- Q2 changed cells: `58`;
- public-action predicted delta versus H057: `-0.001009`;
- responsibility-weighted delta: `-0.001002`;
- max positive bad-anchor cosine: `0.0`;
- selected policy: `anti_shortcut_q061_baseline`;
- decoder templates: `q061:471`.

This is a useful architectural result, but not the one originally hoped for.
Route-specific semantic value policies did not beat the simple q061 decoder.
The current best interpretation is:

```text
support discovery is improving,
but route-specific values are not yet learned;
q061 remains the best safe value target once support is chosen.
```

HS-JEPA should therefore keep route-specific decoders as a research direction,
but the immediate breakthrough path is still support/assignment or a sharper
public/private factor, not handcrafted route value laws.

## H077 Hard-Tail Conflict Route

H077 tested the contradiction exposed by H076: some tiny route cells have huge
positive public-action gain only when they overshoot q061. This creates a new
latent target question:

```text
Is q061 too soft for a sparse public hard-tail route,
or is the public-action sensor overfitting a sparse conflict?
```

The promoted diagnostic is
`submission_h077_hardtail_conflict_123f6665_uploadsafe.csv`.

- changed cells / rows versus H057: `16` / `15`;
- Q2 changed cells: `7`;
- route mix: `q2_hardtail:7`, `q2_s3_tail:3`, `recovery_route:3`,
  `s_stage:2`;
- public-action predicted delta versus H057: `-0.004677`;
- posterior delta versus H057: `+0.000105`;
- responsibility-weighted delta: `+0.000069`;
- q061 value gain sum: `-0.182922`;
- max positive bad-anchor cosine: `0.003282`.

This is not safe. It is a high-information contradiction test. A public win
would mean HS-JEPA needs a hard-tail route decoder beyond q061. A public loss
would strengthen q061/posterior and bad-anchor cosine as guardrails, killing
the sparse monster-route sensor.

## H078-H079 Episode-State Decoder

H078 and H079 add a new decoder branch:

```text
z_hardtail_cell
  -> z_row_episode
  -> full row / adjacent-day correction field
```

H078 tried the conservative version: use H077 hard-tail cells as context and
let route evidence select same-row companions. This produced only `14` changed
cells and `1` companion cell, so it did not prove a row-state cascade.

H079 implements the forced version. It treats the H077 seeds as episode
anchors, then decodes:

- seed hard-tail cells are preserved;
- same-row companions move toward q061-style values;
- adjacent same-subject days receive a damped all-target field;
- bad-anchor cosine is checked as a LeJEPA-style shortcut/collapse guard.

The promoted H079 candidate changes `294` cells on `42` rows with all seven
targets moved on each selected episode row. It is the first post-H057 branch
that directly tests this architectural claim:

```text
HS-JEPA should predict hidden human episodes,
not only isolated row-target corrections.
```

If H079 wins publicly, `z_row_episode` becomes a first-class HS-JEPA target
representation. If it loses badly, the architecture should keep hard-tail
state as a sparse cell-level route and avoid forced temporal propagation from
public-action spikes.

## H080-H082 Action-Field Decoder

H080-H082 add another decoder branch:

```text
{assignment, anti-shortcut, route-value, episode} views
  -> source-action field
  -> consensus / conflict / broad-field decoder
```

Findings:

1. `z_invariant_core` is safe but weak. H080 changed `392` cells with
   `-0.000656` predicted public-action delta.
2. `z_conflict_ridge` is sparse. H081 changed only `16` cells, essentially the
   H077 hard-tail state.
3. `z_source_action_field` is the strongest decoder. H082 changed `725` cells
   with predicted public-action delta `-0.005078`, posterior delta `-0.000616`,
   and max positive bad-anchor cosine `0.0`.

Architectural implication:

```text
HS-JEPA should predict an action field over row-target cells,
not only hidden state support.
```

If H082 wins publicly, this becomes the main HS-JEPA v1 decoder head. If it
fails badly, the action-field head is over-broad and must be regularized by
H080-style consensus or new private-safe context.

## H083-H084 Route-Action Decoder

H083/H084 add a route layer above the H082 source-action field.

```text
context(row, target, source views)
  -> source-action cell field
  -> row route assignment
  -> route-action transport or dark-route completion
  -> probability correction field
```

The architectural distinction is important:

- H082 decoder: independent row-target action cells.
- H083 decoder: one hidden route per row, then coherent route target
  materialization.
- H084 decoder: H082-visible route fragments are preserved, and only the
  missing dark route companion cells are completed.

This gives HS-JEPA two new target representations:

1. `z_route_action`: a route-level state that predicts which target subset
   should move together.
2. `z_dark_route`: a completion state that predicts cells not directly visible
   in H082 but implied by the same row route.

Diagnostics from the first implementation:

- H083 changes `731` cells / `146` rows versus H057 and differs from H082 on
  `807` probability cells. Its support Jaccard with H082 is `0.793103`, so it
  is a route reinterpretation of the action field rather than a totally new
  public equation.
- H084 preserves all `725` H082 cells and adds `68` dark companion cells on
  `36` rows. It is a conditional completion head, not a replacement head.

Decision rule:

- H083 public win: promote route-action transport as the main HS-JEPA v1
  decoder.
- H082 win but H083 loss: source-action should stay cell-local.
- H084 win after H082/H083: add dark-route completion as a second-stage head.

## H085 Public-Equation Refit Module

H085 adds a sensor-inversion branch to HS-JEPA:

```text
known public LB observations
  -> public-equation posterior fit
  -> updated hidden public-state representation
  -> source-agree / row-prototype / route-prototype decoders
  -> correction field
```

The module treats submitted files and their public LB values as context. The
target representation is not a raw label and not a hand-written feature; it is
the posterior row-target action field implied by the public sensor equations.

The first H085 run tested nine decoders. The promoted file used the
source-agree cell decoder:

- `299` cells / `134` rows changed versus H057;
- `source_agree_rate = 1.0`;
- `h082_ratio = 0.986622`;
- `posterior_delta_vs_h057 = -0.000607`;
- bad-anchor max positive cosine `0.0`.

Architectural implication:

```text
HS-JEPA needs a public-posterior memory, but the stable decoder is still
cell-action-first unless public feedback proves row/route prototypes.
```

If H085 wins publicly, this branch becomes an iterative update step in HS-JEPA
v1. If it loses, public-equation refit remains a diagnostic tool and not a
submission decoder until more sensor observations are available.

## H086 Responsibility Head

H086 adds a responsibility head to HS-JEPA:

```text
known public LB equations + hidden posterior q
  -> row-target loss-delta signatures
  -> nonnegative responsibility weights w(row, target)
  -> responsibility-aware correction decoder
```

This head asks a different JEPA question from H085. H085 predicts hidden label
or action representations. H086 predicts which row-target cells are likely to
be heard by the public sensor.

Current diagnostic result:

- the best `w(row, target)` is almost uniform;
- concentrated priors based on H082, source-action, row-public, and
  human-private state do not beat the uniform responsibility fit;
- the promoted diagnostic changes `251` cells but remains below the
  0.001-scale big-bet threshold internally.

Architectural implication:

```text
Keep responsibility as a diagnostic head, not the main HS-JEPA decoder.
HS-JEPA v1 should prioritize predicting the hidden correction/value field,
while responsibility weights act as a collapse/shortcut check.
```

Failure mode guarded by H086:

- if a future candidate claims public-subset localization, it must beat the
  uniform-responsibility baseline and show meaningful concentration;
- otherwise it is likely re-labeling a diffuse public-posterior effect as a
  subset story.

## H087 Route-Conditioned Value-Law Decoder

H087 adds a value-law layer above route assignment:

```text
H071 row-target route
  + H085 posterior q_public
  + H082 source-action movement
  + H018 hard-world q_hard
  -> route-specific value law
  -> correction field
```

The key architectural shift is that a route is no longer decoded with one
global movement target. Each route can choose a value law:

- posterior law: move toward H085 public posterior;
- source-action law: move along H082 action-health direction;
- hard-world law: move toward H018 binary public-world posterior;
- bridge laws: combine these only when their signs agree.

The promoted H087 candidate is
`submission_h087_route_value_law_f5aa327b_uploadsafe.csv`.

Diagnostics:

- changed cells / rows versus H057: `866` / `139`;
- posterior delta versus H057: `-0.000693`;
- hard-world delta versus H057: `+0.000044`;
- responsibility-weighted delta: `-0.000810`;
- source-agree rate: `0.862587`;
- H082 support ratio: `0.804850`;
- max positive bad-anchor cosine: `0.0`;
- upload-safe validation passed.

Architectural implication:

```text
Route support is not enough. HS-JEPA needs a value-law decoder, but H087 shows
that posterior-friendly decoding can damage the hard-world head.
```

H087 therefore turns `z_route_value` into a live module but not a solved one.
It exposes the next bottleneck: public-posterior and hard-world targets are
not always the same hidden state.

## H088 Dual Public/Private Value Gate

H088 reacts to H087's conflict by adding a dual-head gate:

```text
route-action candidate
  -> evaluate under q_public and q_hard
  -> accept only Pareto-safe actions
  -> decode correction field
```

This changes HS-JEPA from a single hidden-state decoder to a public/private
dual-head decoder. The promoted H088 file is
`submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv`.

Diagnostics:

- changed cells / rows versus H057: `980` / `168`;
- posterior delta versus H057: `-0.000540`;
- hard-world delta versus H057: `-0.000187`;
- responsibility-weighted delta: `-0.000565`;
- source-agree rate: `0.802041`;
- H082 support ratio: `0.707143`;
- max positive bad-anchor cosine: `0.0`;
- upload-safe validation passed.

Architectural implication:

```text
HS-JEPA v1 should include two value heads:
q_public for public-equation actionability and q_hard/private for binary-state
stability. The decoder should know when an action is Pareto-safe across both.
```

H088 is less aggressive than H087 on posterior score, but it is more coherent
as a research claim. If H088 wins public LB, the paper-level architecture
should present dual-state value gating as a central HS-JEPA contribution. If it
loses while H087/H071 survive, hard-world should remain a diagnostic health
check rather than an action-grade private target.

Public LB update: H088 scored `0.5684942019`, worse than H057 by
`0.0007466080`.

Architectural correction:

```text
Dual-head representations remain useful, but local Pareto gating is not a
valid decoder. The hard-world head should be retained as a LeJEPA-style
geometry/stress diagnostic, not as an action-grade private target.
```

This moves HS-JEPA v1 away from:

```text
accept action if q_public and q_hard both improve
```

and toward:

```text
infer the row-target assignment/equation field directly, then use hard/private
heads only to detect collapse, shortcut, and overconfident action tails.
```

## H089-H090 Lifestyle-State Context Gate

H089/H090 added the missing human-state context layer:

```text
raw-log-derived human/social story features
  -> within-subject lifestyle transition energy
  -> decoder-head assignment
  -> route-specific value law
  -> correction field
```

The context is not used as a direct label rule. It predicts which hidden
decoder head should be trusted:

- public-transition head for volatile social/arousal rows;
- private-stable head for recovery/routine rows;
- objective-body head for sensor/body rows;
- calendar-Q2 head for cashflow/month-boundary/routine-pressure rows.

H089 promoted
`submission_h089_lifestyle_transition_gate_a9598fc3_uploadsafe.csv`.

Diagnostics:

- changed cells / rows versus H057: `888` / `156`;
- selected route cells: `895`;
- posterior delta versus H057: `-0.000605`;
- hard-world delta versus H057: `+0.000035`;
- responsibility-weighted delta: `-0.000696`;
- H088 root cell overlap: `0.917318`;
- upload-safe validation passed.

Architectural implication:

```text
Lifestyle-state context can explain the H088 decoder choice, but H089 mostly
rediscovered H088 support instead of opening a new action space.
```

H090 then forced a white-space test outside H087/H088 support and promoted
`submission_h090_lifestyle_white_space_6748b5dc_uploadsafe.csv`.

Diagnostics:

- changed cells / rows versus H057: `49` / `17`;
- selected route cells: `76`;
- posterior delta versus H057: `-0.000079`;
- hard-world delta versus H057: `+0.000141`;
- mean H088 action overlap: `0.099160`;
- upload-safe validation passed.

Architectural implication:

```text
Direct lifestyle context is not yet strong enough to authorize new row-target
white-space actions. It should be a context/gate feature under public/private
value heads, not an independent action generator.
```

HS-JEPA v1 should therefore separate three levels:

1. route support from row-target assignment;
2. value-head safety from public/private posterior and hard-world targets;
3. human lifestyle context as a gate/regularizer that explains or prioritizes
   value-head choice, but does not override action-grade posterior support
   without an additional learned latent target.

## H091 Learned Lifestyle-Action Latent

H091 implemented that additional learned latent target:

```text
human/social lifestyle context + row/route structure
  -> subject-held-out predictor
  -> hidden action/value-head quality representation
  -> route-action selection
  -> probability decoder
```

The target representation is not the final Q/S label. It is a five-head
action-quality latent inferred from H085/H018/H082/H071 agreement:

- public action quality;
- private/hard action quality;
- objective/body action quality;
- Q2/calendar action quality;
- overall action-grade quality.

Subject-group OOF diagnostics:

- public head Spearman: `0.944619`;
- private head Spearman: `0.961465`;
- objective head Spearman: `0.939852`;
- Q2 head Spearman: `0.968847`;
- overall head Spearman: `0.977807`.

Promoted H091 file:
`submission_h091_learned_lifestyle_latent_452b5828_uploadsafe.csv`.

Diagnostics:

- changed cells / rows versus H057: `820` / `119`;
- posterior delta versus H057: `-0.000552`;
- hard-world delta versus H057: `-0.000108`;
- responsibility-weighted delta: `-0.000576`;
- H088 action overlap: `0.929972`;
- H087 action overlap: `0.914366`;
- upload-safe validation passed.

Architectural implication:

```text
HS-JEPA can learn a stable context-to-hidden-action representation, but the
current learned latent still chooses the known H087/H088 support basin. The
next architecture step is not another hand story; it is a raw sequence/block
context encoder that can produce action-grade support outside the public
equation basin.
```

## H092 Raw Day-Block Action Latent

H092 replaced the H072/H089 hand-story context with raw day-block context:

```text
raw app/screen/charge/activity/GPS/Wi-Fi/BLE/light/heart/pedometer day state
  -> within-subject transition and novelty coordinates
  -> subject-held-out predictor
  -> hidden action/value-head quality representation
  -> route-action selection
```

Promoted H092 file:
`submission_h092_raw_dayblock_latent_67a84cd8_uploadsafe.csv`.

Subject-group OOF diagnostics:

- public head Spearman: `0.873401`;
- private head Spearman: `0.650449`;
- objective head Spearman: `0.828828`;
- Q2 head Spearman: `0.886433`;
- overall head Spearman: `0.849724`.

Candidate diagnostics:

- changed cells / rows versus H057: `629` / `113`;
- Q2 changed cells: `68`;
- posterior delta versus H057: `-0.000501`;
- hard-world delta versus H057: `-0.000045`;
- responsibility-weighted delta: `-0.000546`;
- H088 action overlap: `0.888748`;
- H087 action overlap: `0.922882`;
- upload-safe validation passed.

Architectural implication:

```text
Raw day-block context is a valid HS-JEPA context encoder, but it still mostly
predicts the known H087/H088 action basin. The low-overlap raw-transition
candidate had only 32 changed cells, so raw context alone did not yet open a
new action-grade support region.
```

This updates the architecture boundary:

1. learned context-to-action latent is real;
2. raw logs are stronger and less hand-wavy than story features;
3. the current blocker is not finding a context representation, but translating
   that representation into low-overlap, private-safe row-target actions.

## H093 Masked Low-Overlap Support Target

H093 changed the JEPA target instead of the context:

```text
context = raw day-block logs + row/route/value-law structure
target = action-grade route support outside H087/H088/H091/H092 root supports
decoder = route-conditioned value law with explicit novelty gates
```

This is the first HS-JEPA module where novelty is inside the target
representation, not just a post-selection bonus.

Promoted diagnostic file:
`submission_h093_masked_lowoverlap_5f023312_uploadsafe.csv`.

Subject-group OOF masked latent diagnostics:

- white head Spearman: `0.586722`;
- white-private Spearman: `0.591539`;
- white-public Spearman: `0.700088`;
- white-objective Spearman: `0.704811`;
- white-Q2 Spearman: `0.658097`;
- overall Spearman: `0.512311`.

Candidate diagnostics:

- changed cells / rows versus H057: `21` / `3`;
- Q2 changed cells: `3`;
- posterior delta versus H057: `-0.000008`;
- hard-world delta versus H057: `+0.000000123`;
- max selected-cell known overlap: `0.476190`;
- selected-cell overlap with H091/H092 roots: `0.000000` / `0.000000`;
- upload-safe validation passed.

The key stress result is scale:

```text
top 5000 route actions with max-known-overlap <= 0.88 and latent score >= 0.55:
only 14 actions

top 5000 route actions with max-known-overlap <= 0.78 and latent score >= 0.55:
only 2 actions
```

Architectural implication:

```text
Masked low-overlap support is learnable, so the latent does not collapse. But
it is too sparse to create a public-readable submission under the current value
law. The next HS-JEPA bottleneck is value-law/public-equation inversion, not
more support discovery or another context encoder.
```

## H094 H057 Value-Law Teacher Target

H094 added a new HS-JEPA target type: public-feedback-as-teacher.

```text
context = raw day-block + human/social state + route/action metadata
teacher = H057-vs-H042 sparse row-target value event
target representation = H057 echo + known public/private/objective/Q2 heads
decoder = route-conditioned value law transferred to non-H057 cells
```

This makes HS-JEPA more precise:

- labels are not the only supervision;
- public LB observations can define a sparse hidden-state teacher;
- the model must predict that teacher from context, then decode it under
  anti-replay gates.

H094 diagnostic result:

- H057 echo is learnable: subject-held-out Spearman `0.778954`, top-10 AUC
  `0.998971`;
- known public/private/Q2 value heads are very learnable;
- direct replay is not allowed in the promoted candidate;
- transfer scale is weak: only `134` changed cells, mean H057 transfer score
  `0.011098`.

Architectural implication:

```text
HS-JEPA v1 should include public-feedback teacher heads, but H057 echo should
be treated as a diagnostic representation, not as the main decoder target.
The next decoder should solve row-target assignment and public/private value
equations directly.
```

## HS-JEPA v2: Signed Action-Equation Decoder

H088 changed the architecture boundary. The failed dual-head gate showed:

```text
public-equation posterior + hard-world posterior Pareto safety
!= action-grade safety
```

HS-JEPA v2 therefore adds a signed action-equation decoder.

### Context

- H057 current-best row-state event;
- H042/H050 pre-H057 public observations;
- H088 failed public action;
- H085/H095 public-equation posterior;
- route/action metadata from H071/H087;
- H018 hard-world only as a stress diagnostic.

### Target Representation

The target is no longer only a hidden human-state probability. It is a signed
row-target action field:

```text
safe_action(row, target)
toxic_action(row, target)
counterfactual_direction(row, target)
assignment_route(row)
```

H095 estimated the unsigned toxic-veto version. H096 estimated the signed
counterfactual version.

### New Decoder Rule

```text
If a failed public action moved against a previously positive public event,
do not simply avoid the cell. Treat that failed action as a signed sensor and
test the opposite direction.
```

This is the current HS-JEPA v2 proposition:

```text
HS-JEPA learns hidden human-state representations, but the final action layer
must solve a signed public/private row-target equation. Public LB failures are
not discarded; they become counterfactual supervision for the action decoder.
```

### Current Evidence

- H095 toxic-veto candidate:
  `submission_h095_assignment_solver_948e8840_uploadsafe.csv`;
- H095 changed cells / rows: `48` / `32`;
- H095 conclusion: unsigned veto is too small.

- H096 conflict-inversion candidate:
  `submission_h096_conflict_inversion_af7e60fd_uploadsafe.csv`;
- H096 changed cells / rows: `83` / `28`;
- H096 anti-H088 direction rate: `1.000000`;
- H096 cosine with H057-vs-H042 direction: `0.527502`;
- H096 conclusion before public check: the next architectural test is signed
  failed-action inversion.

## HS-JEPA v2.1: Frontier-Weighted Public Feedback

H097/H098 refine the signed action-equation decoder.

H097 showed that a public-response predictor can fit the overall submission
landscape:

```text
all public submissions -> action-response latent
LOO Spearman = 0.978474
```

But it failed the key frontier diagnostic:

```text
H088 actual public delta = +0.000747
H097 H088 LOO prediction = -0.000642
```

So HS-JEPA v2 cannot treat all public observations equally. Old bad
submissions mostly teach a coarse "far from frontier" direction.

H098 adds the current architectural rule:

```text
Public feedback is weighted by frontier relevance.
H057/H042/H050/H012/H088 define the local action equation.
Older bad submissions are background constraints.
```

H098 evidence:

- selected response model: `state_core`, ridge `0.1`;
- weighted LOO MAE: `0.000417`;
- H088 LOO prediction: `+0.000757`;
- H088 LOO error: `+0.000010`;
- candidate: `submission_h098_frontier_equation_a748e477_uploadsafe.csv`;
- changed cells / rows: `46` / `20`;
- anti-H088 direction rate: `1.000000`.

Current architecture:

```text
context encoder
  -> human-state / route-state representation
  -> frontier-weighted signed action equation
  -> row-target assignment decoder
  -> submission action
```

Open architectural gap:

The current signed equation is still cell-level. If H098 loses, the missing
module is probably a row/route-constrained assignment decoder that keeps the
frontier-weighted response model but selects coherent route actions instead of
independent cells.

## HS-JEPA v2.2: Route-Constrained Action Assignment

H099 adds the missing discrete decoder:

```text
context encoder
  -> human-state / route-state representation
  -> frontier-weighted signed action equation
  -> H071 route-template assignment
  -> H057-positive / H088-opposite route action
```

The important architectural change is not another encoder. It is an action
validity layer:

```text
cell action score + signed toxicity direction + route membership
-> action is safe only if the route assignment is coherent
```

H099 evidence:

- candidate: `submission_h099_route_equation_1cbff4af_uploadsafe.csv`;
- selected routes / cells / rows: `15` / `26` / `15`;
- model-predicted delta vs H057: `-0.000244`;
- anti-H088 direction rate: `1.000000`;
- H057-positive alignment rate: `1.000000`;
- selected conflict rate: `1.000000`;
- mean assignment route score: `0.439801`.

Architectural implication:

H099 turns HS-JEPA's final stage into an equation/assignment solver:

```text
representation predicts candidate action field
public/private equation estimates action toxicity
route assignment decides which row-target actions are legal
```

The unresolved point is whether the correct assignment basis is H071-style route
templates or a new route system learned directly from H057/H088 public sensors.

## HS-JEPA v2.3: Route-Action Basis Public Equation

H100 adds an explicit equation-space layer:

```text
known public actions
  -> projection into route-action basis
  -> frontier-weighted public response equation
  -> route assignment decoder
```

This is different from H099. H099 asks whether a cell action is legal inside a
route. H100 asks whether the public/private observation equation itself is
written in route-action coordinates.

H100 evidence:

- candidate: `submission_h100_route_basis_6c8e0c6b_uploadsafe.csv`;
- selected route-basis model: `signed_meta`, `k_basis=40`, ridge `0.1`;
- weighted LOO MAE: `0.000217`;
- H088 LOO prediction: `+0.000853`;
- selected actions / cells / rows: `24` / `28` / `24`;
- route-basis predicted delta vs H057: `-0.001031`;
- H098 cell-equation predicted delta vs H057: `-0.000045`;
- H057/H088 conflict geometry preserved exactly:
  anti-H088 `1.0`, H057-align `1.0`, conflict-rate `1.0`.

Architectural implication:

HS-JEPA now has two competing action decoders:

```text
sparse signed cell decoder     = H098
route-constrained cell decoder = H099
route-action basis equation    = H100
```

The next public result should decide whether the final decoder should be local
cell toxicity or route-action equation space. H100 is riskier but more
architecture-defining than H099.

## HS-JEPA v2.4: Disagreement-Toxicity Gate

H101 adds a safety gate between the route-action equation and the final
assignment:

```text
route-action basis equation
  -> candidate route actions
  -> stability across route-basis models
  -> H098 cell-equation toxicity check
  -> small safe-assignment field
```

This version makes the active goal explicit. HS-JEPA is no longer only a
hidden-state representation model. It is an equation solver that asks whether a
row-target action is safe under two public/private views:

```text
route-level view: does this action overlap with routes that public feedback
                  rewards?
cell-level view:  does this action look like a locally toxic H088-style move?
```

H101 evidence:

- candidate: `submission_h101_disagreement_toxicity_9e088156_uploadsafe.csv`;
- selected actions / cells / rows: `5` / `6` / `5`;
- route-basis predicted delta vs H057: `-0.000641`;
- H098 cell-equation predicted delta vs H057: `-0.000014`;
- anti-H088 direction rate: `0.833333`;
- H057-positive alignment rate: `0.833333`;
- selected conflict rate: `1.000000`.

Architectural implication:

The current HS-JEPA decoder stack is:

```text
H098 = sparse signed cell equation
H099 = route-constrained assignment
H100 = route-action basis equation
H101 = route-basis stability + H098 toxicity gate
```

H101 does not replace H100 yet. It exposes the next architectural problem:
the model can detect route-basis public response, but it cannot yet determine
which broad route actions are private-safe. The next HS-JEPA step should learn
a larger public/private action-toxicity field instead of only pruning route
actions by stability.

## HS-JEPA v2.5: Bad-Axis Nullspace Assignment

H102 changes the definition of toxicity:

```text
bad public submissions
  -> action vectors from H057
  -> bad-axis subspace
  -> route-action assignment constrained to the nullspace or positive-anchor
     margin of that subspace
```

This is closer to the active HS-JEPA objective. The representation does not
only say "this row-target looks like a state." It asks whether the action
created by that state is safe under public/private observation equations.

H102 evidence:

- candidate: `submission_h102_badnull_e775939d_uploadsafe.csv`;
- selected actions / cells / rows: `5` / `7` / `5`;
- selected rows: `144,146,149,151,164`;
- route-basis predicted delta vs H057: `-0.001162`;
- H098 cell-equation predicted delta vs H057: `-0.000023`;
- cumulative bad-axis positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.002161`;
- cumulative H057-positive anchor margin: `+0.013258`.

Architectural implication:

The decoder stack now has three safety views:

```text
H100 route-basis equation      = which route-actions public feedback rewards
H101 disagreement gate         = which route-actions survive model agreement
H102 bad-axis nullspace solver = which route-actions avoid known toxic action
                                 subspaces
```

H102 suggests that the next full HS-JEPA should represent action toxicity as a
subspace or field, not a scalar per cell. The remaining problem is density: the
current nullspace solver finds a very sharp 7-cell action. A 0.53-scale
breakthrough would require discovering a much larger safe nullspace with the
same public/private constraints.

## HS-JEPA v2.6: Toxic-Shadow Cancellation Portfolio

H103 expands the H102 nullspace into a portfolio solver:

```text
route-action candidates
  -> bad-axis and good-anchor projections
  -> cumulative toxic-shadow constraints
  -> dense route-action portfolio whose combined vector is bad-axis safe
```

This changes the decoder again. H102 asks whether each chosen assignment stays
near the bad-axis nullspace. H103 asks whether several assignments can be safe
as a group even if individual routes cast small toxic shadows.

H103 evidence:

- candidate: `submission_h103_shadowcancel_89496ed5_uploadsafe.csv`;
- selected actions / cells / rows: `23` / `28` / `23`;
- route-basis predicted delta vs H057: `-0.002438`;
- H098 cell-equation predicted delta vs H057: `-0.000063`;
- cumulative bad-axis positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.008946`;
- cumulative H057-positive anchor margin: `+0.036728`.

Architectural implication:

The latest HS-JEPA decoder stack is:

```text
context / human-state representation
  -> route-action basis equation
  -> bad public-axis toxicity field
  -> toxic-shadow cancellation portfolio
  -> row-target action assignment
```

The key distinction is that action safety is now evaluated on the combined
submission vector, not on individual cells or routes. This is closer to the
goal of reconstructing a public/private row-target equation rather than adding
another latent context encoder.

## HS-JEPA v2.7: Toxic-Axis Residual Transport Decoder

H104 changes the decoder class again:

```text
route-action basis equation
  -> desired route field
  -> remove positive toxic-axis component
  -> add small H057-positive anchor component
  -> residualize again
  -> sparsify residual into row-target action assignment
```

This asks a sharper question than H103.  H103 assumes the route-action units
must remain discrete and safe as a portfolio.  H104 assumes the route-action
field may be correct in representation space but contaminated in action space;
the submitted action is therefore the residual field after projecting away
known toxic public directions.

H104 evidence:

- candidate: `submission_h104_toxicresid_52f826e6_uploadsafe.csv`;
- source route-actions / submitted cells / rows: `47` / `87` / `64`;
- route-basis predicted delta vs H057: `-0.001758`;
- H098 cell-equation predicted delta vs H057: `-0.000086`;
- cumulative bad-axis positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.033173`;
- cumulative H057-positive anchor margin: `+0.191825`.

Architectural implication:

The HS-JEPA decoder now has two live forms:

```text
Discrete solver: route-action portfolio with toxic-shadow cancellation.
Residual solver: route-field transport through a bad-axis projection operator.
```

Public LB will decide which representation is action-grade.  If H104 wins, the
paper-worthy HS-JEPA contribution is not only human-state representation; it is
an action-safety operator that maps latent route intent into a public-safe
correction field.

## HS-JEPA v2.8: Signed Route-Coefficient Solver

H105 opens the route-action decoder into signed coefficients:

```text
route-action basis
  -> positive and counter-route coefficient terms
  -> greedy public/private Lagrangian solver
  -> sparse row-target kernel
```

The intended test was broad: can HS-JEPA solve a signed coefficient equation
instead of selecting route-actions?  The observed result was narrower and more
interesting.  The promoted candidate used no counter terms:

- `29` selected coefficient terms;
- `29` positive terms, `0` counter terms;
- `8` submitted cells on `4` rows;
- rows: `144,146,151,164`;
- route-basis predicted delta vs H057: `-0.002727`;
- bad-axis positive projection: `0.000000`;
- H088-axis cosine: `-0.007302`.

Architectural implication:

H105 does not prove that signed coefficient mixing is the final decoder.  It
suggests a new object inside HS-JEPA:

```text
route-consensus kernel =
  a small row-target set where many route-action basis functions agree under
  public/private toxicity constraints
```

This kernel is different from H103/H104.  H103 is a broad route-action
portfolio; H104 is a residualized field.  H105 is a tiny consensus object.  If
public confirms it, the next architecture should include a kernel expansion or
kernel-transfer module.

## HS-JEPA v2.9: Route-Consensus Kernel Expansion

H106 adds the kernel-transfer module implied by H105:

```text
route-action basis
  -> per-cell consensus vote field
  -> bad-axis constrained expansion around the H105 kernel
  -> public-safe row-target assignment
```

The question changes from "which route-action is good?" to "which row-target
cells are repeatedly named by independent route-actions while staying silent on
known bad public axes?"  This is closer to a row-target equation solver than a
context encoder or feature model.

H106 evidence:

- candidate: `submission_h106_routeconsensus_f315d99a_uploadsafe.csv`;
- source route-actions / submitted cells / rows: `220` / `48` / `22`;
- H105 seed-row cells / seed-neighbor cells / seed-subject cells: `10` / `15` /
  `20`;
- route-basis predicted delta vs H057: `-0.000796`;
- H098 cell-equation predicted delta vs H057: `-0.000040`;
- cumulative bad-axis positive projection: `0.000000`;
- cumulative H088-axis cosine: `-0.016900`;
- cumulative good-minus-bad margin: `+0.064203`.

Architectural implication:

H106 separates two possible meanings of H105:

```text
H105 as sharp kernel:
  the safe assignment is very sparse and should not be expanded.

H105 as seed kernel:
  the safe assignment can be transferred to nearby route-consensus cells.
```

If H106 beats H105, HS-JEPA needs an explicit kernel propagation step.  If H105
beats H106, the architecture should keep the route-consensus kernel sharp and
use expansion only as a diagnostic.

## HS-JEPA v3.0: Negative-Sensor Antipode Decoder

H107 adds a new decoder class:

```text
negative public sensor action
  -> toxic cell field
  -> constrained antipode proposal
  -> consensus/anchor-supported row-target assignment
```

This is different from H102-H106.  Those decoders use H088 as an axis to avoid.
H107 asks whether H088 can also generate corrective action by reversing only
the toxic cells that have independent H106 route-consensus or H057-positive
support.

H107 evidence:

- candidate: `submission_h107_antipode_a0ea1eec_uploadsafe.csv`;
- submitted cells / rows: `26` / `19`;
- target changes: Q1 `4`, Q2 `0`, Q3 `7`, S1 `4`, S2 `3`, S3 `1`,
  S4 `7`;
- H088-axis cosine: `-0.022682`;
- H106 alignment rate: `1.000000`;
- H057-positive alignment rate: `0.961538`;
- route-basis predicted delta vs H057: `-0.000079`.

Architectural implication:

HS-JEPA now has two interpretations of negative public sensors:

```text
veto view:
  negative sensors define forbidden directions only.

antipode view:
  negative sensors define a signed toxic field whose constrained opposite may
  be action-grade.
```

H107 is the first direct test of the antipode view.  If it fails, H088 should
remain a veto/stress diagnostic.  If it works, HS-JEPA should learn signed
sensor equations from both positive and negative public observations.

## HS-JEPA v3.1: Decoder-Jury Assignment Solver

H108 changes HS-JEPA from choosing one decoder to asking for agreement among
decoders:

```text
H103 portfolio decoder
H104 residual transport decoder
H105 sparse kernel decoder
H106 kernel expansion decoder
H107 negative-sensor antipode decoder
  -> signed row-target witness field
  -> decoder-family consensus
  -> bad-axis constrained assignment
```

This is not probability blending.  The candidate is built by converting every
source decoder into logit action vectors, aggregating signed row-target votes,
and selecting only cells with independent family agreement.

H108 evidence:

- candidate: `submission_h108_jury_610a26a0_uploadsafe.csv`;
- source candidates / families: `19` / `5`;
- submitted cells / rows: `47` / `27`;
- Q2 cells: `0`;
- H098 cell-equation predicted delta vs H057: `-0.000050`;
- route-basis predicted delta vs H057: `-0.001528`;
- bad-axis positive projection: `0.000000`;
- H088-axis cosine: `-0.009025`;
- mean decoder-family count: `3.851064`;
- mean family consensus: `1.000000`.

Architectural implication:

HS-JEPA now has a meta-decoder:

```text
single branch view:
  one decoder family is the true action law.

jury view:
  the true action law is the intersection where independent decoder families
  agree and public toxicity constraints remain silent.
```

If H108 works, the paper architecture should present HS-JEPA as a
multi-decoder predictive system with an assignment jury, not as a single latent
encoder plus one decoder.

## HS-JEPA v3.2: Decoder-Coefficient Equation Solver

H109 adds one more level above the decoder jury:

```text
H103-H108 decoder submissions
  -> coefficient basis vectors
  -> public/private action field
  -> sparse row-target assignment decoder
```

This asks whether previous HS-JEPA branches are not alternatives or voters, but
terms in one equation.  In that view, a safe action can be produced by mixing
whole decoder vectors and then decoding only the cells that remain public-safe.

H109 evidence:

- candidate: `submission_h109_coeff_54147083_uploadsafe.csv`;
- source candidates / families: `20` / `6`;
- selected coefficient terms: `4`;
- selected term families: `h105`;
- submitted cells / rows: `4` / `2`;
- target changes: Q1 `1`, Q2 `0`, Q3 `0`, S1 `2`, S2 `0`, S3 `0`,
  S4 `1`;
- route-basis predicted delta vs H057: `-0.001862`;
- full field route-basis predicted delta vs H057: `-0.004404`;
- H098 cell-equation predicted delta vs H057: `+0.000015`;
- bad-axis positive projection: `0.000000`;
- H088-axis cosine: `-0.005077`;
- mean decoder-family count: `4.250000`.

Architectural implication:

H109 did not produce a broad coefficient-composed field.  The solver collapsed
to an H105-derived id06/id07 micro-kernel.  That means HS-JEPA should separate
two objects:

```text
latent coefficient field:
  useful for scoring where action might exist.

action-grade assignment:
  a much sharper sparse kernel that must survive toxicity constraints.
```

If H109 works, HS-JEPA v3 should include coefficient solving as a kernel
sharpening module.  If H108 works better, the architecture should keep the jury
intersection as the action decoder and use coefficient fields only as
diagnostics.

## HS-JEPA v3.3: Toxicity-Gap Assignment Solver

H110 adds the first explicit public-action toxicity head:

```text
context and decoder witnesses
  -> benefit representation
  -> toxicity representation
  -> benefit-toxicity gap
  -> sparse row-target assignment
```

This is closer to the current goal than H108/H109.  H108 had assignment but no
local toxicity decomposition.  H109 had coefficient solving but collapsed into
a tiny kernel.  H110 keeps the assignment view while making toxicity a separate
representation.

H110 evidence:

- candidate: `submission_h110_toxgap_7b02f196_uploadsafe.csv`;
- source candidates / families: `21` / `7`;
- selected cells / rows: `37` / `23`;
- Q2 cells: `0`;
- H098 cell-equation predicted delta vs H057: `-0.000037`;
- route-basis predicted delta vs H057: `-0.001037`;
- bad-axis positive projection: `0.000000`;
- H088-axis cosine: `-0.008961`;
- selected mean benefit / toxicity / gap:
  `0.918943` / `0.517838` / `0.401106`;
- H108/H109 overlap: `29` / `1` cells.

Architectural implication:

HS-JEPA should now be described as a predictive architecture with three
decoder layers:

```text
representation decoder:
  predicts hidden human/public state.

witness decoder:
  converts latent state into candidate row-target action witnesses.

toxicity-gap assignment decoder:
  separates benefit and public-action toxicity, then assigns only safe cells.
```

If H110 works, the paper-level contribution is not just "JEPA for tabular
sleep logs."  It is a human-state JEPA with an action-toxicity head that checks
whether a predicted intervention is safe under hidden public/private
observation equations.

## HS-JEPA v3.4: Global Boundary Assignment Solver

H111 adds a final layer above the toxicity head:

```text
benefit representation
toxicity representation
shortcut / bad-pressure diagnostics
decoder-family witness field
  -> global boundary solver
  -> public/private safe row-target action
```

The trigger was an architectural contradiction in H110.  The H108 cells that
H110 rejected had better local benefit-toxicity gap than many cells H110 kept.
So the local toxicity head is not the final decoder.  It is an input to a
global assignment layer.

H111 evidence:

- candidate: `submission_h111_boundary_7cbf5e9d_uploadsafe.csv`;
- selected cells / rows: `53` / `28`;
- selected H108 kept / rejected / H110-added cells: `27` / `14` / `5`;
- H098 cell-equation predicted delta vs H057: `-0.000020`;
- route-basis predicted delta vs H057: `-0.000680`;
- bad-axis positive projection: `0.000000`;
- H088-axis cosine: `-0.015318`;
- H111/H108 cosine: `0.923553`;
- H111/H110 cosine: `0.691689`.

Architectural implication:

HS-JEPA now has a cleaner paper-level structure:

```text
1. Human-state encoder:
   learns row/subject/sequence/social/state context.

2. JEPA witness decoders:
   produce candidate row-target action fields from hidden representations.

3. Toxicity head:
   estimates whether an action direction is public/private unsafe.

4. Global boundary assignment solver:
   chooses a sparse action set whose cumulative public bad-axis projection is
   safe.
```

If H111 works, the architecture's novelty is the last two stages: predicted
human-state actions are not used directly; they must pass through a
public/private toxicity field and a global boundary solver.

## HS-JEPA v3.5: Public-Residual Toxicity Solver

H112 adds one more action-grade check after H111:

```text
known public submissions
  -> leave-one-out public response equation
  -> residual public loss field
  -> signed row-target residual toxicity / safety projection
  -> boundary-pruned assignment
```

The architectural distinction is important.  H098/H100 estimate first-order
public response.  H102-H111 estimate bad-axis, benefit/toxicity, and global
boundary safety.  H112 asks whether the remaining public residual itself is a
learnable representation.

H112 evidence:

- candidate: `submission_h112_residualtox_68b26f11_uploadsafe.csv`;
- selected cells / rows: `40` / `23`;
- selected H111-overlap cells: `37`;
- selected H108-rejected cells: `14`;
- H098 cell-equation predicted delta vs H057: `-0.000018`;
- route-basis predicted delta vs H057: `-0.000980`;
- bad-axis positive projection: `0.000000`;
- H088-axis cosine: `-0.011878`;
- residual toxicity / safety / gap:
  `0.489754` / `0.681667` / `0.191912`;
- H112/H111 cosine: `0.855260`;
- H112/H110 cosine: `0.633342`.

Updated HS-JEPA decoder stack:

```text
1. Human-state context encoder
   row order, subject-like blocks, social/lifestyle hypotheses, target routes.

2. Witness decoders
   propose row-target action fields from hidden state representations.

3. Public response equation
   predicts first-order public action response from signed action features.

4. Toxicity and bad-axis diagnostics
   detect H088-like, H010/E216/LeJEPA-like, shortcut, and collapse directions.

5. Global boundary assignment solver
   chooses a sparse action set under cumulative public/private constraints.

6. Public-residual toxicity solver
   uses LOO public-response residuals as a final action-safety field.
```

If H112 works, HS-JEPA should be written as a predictive architecture for
hidden human state plus action safety, not merely hidden human state.  The
final output is a row-target assignment whose action is safe under both the
first-order public equation and the residual public toxicity equation.

## HS-JEPA v4: Row-Route Equation Solver

H113 adds a route-structured action decoder:

```text
row context / hidden human state
  -> candidate target-route bundles inside each row
  -> residual toxicity and safety scoring for each bundle
  -> one-route-per-row assignment solver
  -> cumulative public/private stress validation
```

This changes the final decoder unit:

- v3.5 action unit: signed row-target cell;
- v4 action unit: signed row-target bundle inside one row.

H113 evidence:

- candidate: `submission_h113_rowroute_04369be5_uploadsafe.csv`;
- selected cells / rows / bundles: `37` / `14` / `14`;
- mean targets per bundle: `2.642857`;
- target route: Q1 `7`, Q2 `0`, Q3 `9`, S1 `8`, S2 `4`, S3 `3`,
  S4 `6`;
- H098 cell-equation predicted delta vs H057: `-0.000019`;
- route-basis predicted delta vs H057: `-0.000597`;
- bad-axis positive projection: `0.000000`;
- H088-axis cosine: `-0.001766`;
- residual toxicity / safety / gap:
  `0.499907` / `0.682719` / `0.182812`;
- H113/H112 cosine: `0.851031`.

Architecture interpretation:

H113 should not yet be presented as a new independent representation.  It is a
candidate action decoder layer.  If public LB improves over H112, HS-JEPA v4
has evidence that human-state correction should be route-factored.  If not,
the architecture should keep row-route bundles as diagnostics while the actual
decoder remains cell-level residual toxicity.

## HS-JEPA v4.5: Toxic-Subspace Null Decoder

H114 adds a stronger decoder hypothesis:

```text
public-failed submissions and residual-bad moves
  -> toxic action subspace
human-state candidate action
  -> nullspace projection
  -> sparse row-target assignment
  -> public/private stress validation
```

This is different from H102-H113.  Earlier versions selected or scored actions
and then checked whether the resulting vector was public-safe.  H114 makes
public safety a pre-assignment transformation.

H114 evidence:

- candidate: `submission_h114_nullspace_73fe7866_uploadsafe.csv`;
- selected cells / rows: `27` / `25`;
- target route: Q1 `1`, Q2 `0`, Q3 `6`, S1 `6`, S2 `2`, S3 `7`,
  S4 `5`;
- toxic projection ratio: `0.047395`;
- H112 cosine: `0.033494`;
- H113 cosine: `0.057487`;
- H088-axis cosine: `-0.010421`;
- bad-axis positive projection: `0.000000`.

Architecture interpretation:

If H114 works, HS-JEPA's decoder is not:

```text
representation -> action
```

It is:

```text
representation -> proposed action -> toxic-subspace null action -> assignment
```

If H114 fails, the toxic-subspace layer should remain a diagnostic for collapse
and public overfit, not the action decoder.

## HS-JEPA v5: Second-Order Row-Target Equation Solver

H115 adds a nonlinear action decoder above the previous public/private layers:

```text
known public action observations
  -> signed row-target action features
  -> first-order public response equation
  -> second-order route/target curvature equation
  -> curvature-safe sparse assignment
```

The architectural reason is H088.  H088's public failure shows that a
representation can be plausible as a latent state and still fail as an
action-grade decoder.  H115 therefore treats H088 as a negative action sensor,
not as a teacher for private action.

H115 evidence:

- candidate: `submission_h115_curvature_23748467_uploadsafe.csv`;
- selected cells / rows: `20` / `16`;
- target route: Q1 `3`, Q2 `8`, Q3 `4`, S1 `4`, S2 `0`, S3 `1`,
  S4 `0`;
- selected curvature model: `route_curvature`, alpha `30`;
- weighted LOO MAE / RMSE: `0.000433509` / `0.000627976`;
- LOO Spearman / pair accuracy: `0.927593` / `0.894545`;
- H088 LOO prediction / abs error: `+0.000658162` / `0.000088446`;
- curvature predicted delta vs H057: `-0.000251384`;
- H098 predicted delta vs H057: `-0.000001`;
- route-basis predicted delta vs H057: `-0.000032`;
- H088-axis cosine: `-0.003903`;
- H112 cosine: `0.247554`;
- H114 cosine: `0.015212`.

Architecture interpretation:

HS-JEPA has now moved from representation learning to action-equation solving.
The final object is no longer:

```text
hidden human state -> label probability
```

It is:

```text
hidden human state
  -> proposed row-target action
  -> public/private toxicity and curvature equations
  -> safe assignment field
```

H115's key structural claim is that Q2 is not a global yes/no target.  Q2 may
only be action-safe as a companion inside a low-curvature row-target route.
If the public result supports H115, the paper-level HS-JEPA contribution should
emphasize "human-state predictive representation plus row-target
action-equation solver."  If H115 fails, second-order curvature remains a
diagnostic and the architecture should keep H112/H114 toxicity/nullspace as
the live decoder branch.

## HS-JEPA v5.1: Forbidden Sector Diagnostics

H116 and H117 add a negative layer to the v5 action-equation solver.

```text
candidate Q2 companion route
  -> Q2-only / companion-only / full-route ablation
  -> H088 toxicity check
  -> optional anti-H088 guard field
  -> promote only if the full assignment is safe
```

H116 result:

- Q2 companion rescue exists;
- all positive-rescue Q2 companion bundles are H088-positive;
- guard cells cannot neutralize the H088 direction without introducing
  unacceptable bad-axis pressure;
- no candidate is promoted.

H117 then tries:

```text
forbidden Q2 companion sector
  -> contrastive target representation
  -> non-Q2 antipode assignment
```

H117 result:

- only `4/2192` proposal cells point opposite the forbidden sector;
- none become an upload-safe candidate.

Architecture implication:

HS-JEPA should distinguish three objects:

```text
latent structure:      Q2 companion curvature exists.
toxic action sector:   that curvature is H088-positive.
safe assignment field: not found by direct companion or antipode decoding.
```

This is important for the paper framing.  HS-JEPA is not just a model that
predicts hidden human state.  It is a model that refuses to act when a real
hidden state lives in a public-toxic action sector.  H116/H117 therefore
strengthen the row-target action-equation story even though they produce no
submission.

## HS-JEPA v5.2: Forbidden-Sector Veto Assignment

H118 turns the v5.1 negative diagnostics into an explicit decoder layer.

```text
context encoder
  -> hidden human-state proposals
  -> forbidden-sector recognizer
  -> veto public-toxic action sectors
  -> residual/nullspace/antidote proposal scoring
  -> row-target safe assignment
```

The key architectural distinction is:

```text
representation quality != action safety
```

H116/H117 found a real Q2 companion representation, but H088-style public
response says that representation is action-toxic.  H118 keeps the
representation, but changes its role from action target to veto target.

H118 evidence:

- candidate: `submission_h118_forbiddenveto_e81167a8_uploadsafe.csv`;
- selected cells / rows: `52` / `34`;
- target route: Q1 `8`, Q2 `0`, Q3 `7`, S1 `8`, S2 `11`,
  S3 `8`, S4 `10`;
- forbidden axes: `264`;
- forbidden same-sector exposure / pressure: `0.000000` / `0.000000`;
- H102 bad-axis weighted positive projection: `0.000000`;
- H088-axis cosine: `-0.003628`;
- route-basis predicted delta vs H057: `-0.000568`;
- residual toxicity / safety / gap:
  `0.397824` / `0.648287` / `0.250463`.

Architecture implication:

HS-JEPA should now be written as a two-stage system:

```text
Stage A: Predict hidden human-state representations.
Stage B: Solve whether acting on each row-target representation is safe under
         the public/private observation equation.
```

This is the cleanest distinction from a normal tabular/blend approach.  A
standard model asks which probability is better.  HS-JEPA asks whether a
candidate correction belongs to a safe assignment field or a public-toxic
action field.  H118 is the first concrete prototype of that distinction.

## HS-JEPA v5.3: Posterior Sensor / Action Solver Split

H119 and H120 refine v5.2.  The previous architecture still left one ambiguity:
if HS-JEPA predicts a hidden posterior well, should that posterior be decoded
directly into probability actions?

H119 says no for H085:

```text
H085 public posterior
  -> direct row-target action
  -> forbidden-sector veto
  -> H088/curvature stress
  -> no safe candidate
```

This is an architectural negative result.  A representation can be real and
still unsafe as an action target.

H120 introduces the v5.3 split:

```text
context encoder
  -> hidden human-state / public-posterior representation
  -> row-level public sensitivity sensor
  -> action solver over residual stage proposals
  -> forbidden-sector veto
  -> public/private stress gates
  -> sparse row-target assignment
```

The new distinction is:

```text
representation posterior: where does the hidden public state appear?
action solver: which row-target correction is safe to materialize?
```

H120 evidence:

- candidate: `submission_h120_toxrow_0b84c821_uploadsafe.csv`;
- selected cells / rows: `18` / `15`;
- target route: Q1 `0`, Q2 `0`, Q3 `6`, S1 `1`, S2 `1`,
  S3 `6`, S4 `4`;
- posterior delta vs H057: `+0.0000035`;
- model predicted delta vs H057: `-0.0000151`;
- route-basis predicted delta vs H057: `-0.0002291`;
- bad-axis weighted positive projection: `0.000000`;
- H088-axis cosine: `-0.000003`;
- good-bad margin: `0.106932`.

Architecture implication:

HS-JEPA is no longer just:

```text
context -> latent -> label
```

It is:

```text
context -> latent human/public state -> action safety equation -> label action
```

This is the paper-level contribution that distinguishes HS-JEPA from a normal
stacked tabular model or blend.  The model predicts hidden state, but it also
learns when predicted hidden state should not be acted on directly.

## HS-JEPA v5.4: Row-Regime Mixture Of Action Solvers

H121 extends v5.3 from "posterior sensor plus action solver" to a partitioned
decoder.

```text
context encoder
  -> hidden human/public state representations
  -> row-regime sensor
  -> choose action solver
       low toxic-posterior regime: H118 forbidden-veto residual assignment
       high toxic-posterior regime: H120 stage-bridge assignment
  -> public/private stress equation
  -> sparse row-target action
```

The architecture claim is:

```text
action safety is conditional on hidden row regime.
```

This is stronger than a gate over final probabilities.  The gate decides which
decoder is allowed to create the row-target action in the first place.

H121 evidence:

- candidate: `submission_h121_rowsensorpart_d03abb5b_uploadsafe.csv`;
- selected cells / rows: `44` / `31`;
- target route: Q1 `6`, Q2 `0`, Q3 `11`, S1 `6`, S2 `4`,
  S3 `9`, S4 `8`;
- active H118 rows/cells removed: `15` / `20`;
- H118 cells kept / H120 cells used: `32` / `18`;
- route-basis predicted delta vs H057: `-0.0005801`;
- model predicted delta vs H057: `-0.0000378`;
- H088-axis cosine: `-0.039209`;
- good-bad margin: `0.113396`.

Compared with v5.2 H118, v5.4 keeps the strong forbidden-sector veto but
removes H118 actions in high H085 toxic-posterior rows.  Compared with v5.3
H120, it does not throw away the larger H118 assignment field.  It composes
both through a regime equation.

This is the current cleanest HS-JEPA formulation:

```text
Predict hidden human state.
Infer the row regime.
Select the action solver for that regime.
Materialize only actions that survive the public/private toxicity equation.
```

## HS-JEPA v5.5: Action-Prune Equation Solver

H122 refines v5.4.  The row-regime branch is useful, but the first action-grade
operation may be deletion rather than replacement.

```text
context encoder
  -> hidden human/public state representations
  -> row/action toxicity sensor
  -> generate candidate action field
       H118 forbidden-veto residual assignment
  -> prune public-toxic row-target actions
       objective Q/S stage toxicity sector
  -> optional replacement branch
       only if pruning leaves missing safe support
  -> public/private stress equation
  -> sparse row-target action
```

The architecture claim is:

```text
HS-JEPA should predict not only a hidden state and an action proposal, but also
an action-toxicity field that can veto locally plausible corrections.
```

H122 evidence:

- candidate: `submission_h122_pruneeq_0a9edcce_uploadsafe.csv`;
- selected solver: `h122_prune_stage_public_toxic_0a9edcce`;
- remaining cells / rows: `24` / `19`;
- removed H118 cells / rows: `28` / `22`;
- removed target sector: S4 `8`, S3 `8`, S2 `7`, Q3 `3`, S1 `2`;
- route-basis predicted delta vs H057: `-0.0006052`;
- model predicted delta vs H057: `-0.0000287`;
- H088-axis cosine: `-0.066158`;
- good-bad margin: `0.125854`.

Compared with v5.4 H121, v5.5 is sparser and more anti-toxic.  It improves the
route-basis equation, H088-axis stress, and good-bad margin, while accepting a
slightly weaker H098/model delta.  That tradeoff makes it a clean test of
whether public LB is punishing action toxicity more than missing replacement
signal.

The current HS-JEPA stack is therefore:

```text
context -> hidden human state
        -> row/action sensor
        -> proposal field
        -> toxicity-prune equation
        -> optional replacement
        -> calibrated submission
```

## HS-JEPA v5.6: Prune-Then-Route-Refill Decoder

H123 turns the optional replacement branch into a falsifiable route-complement
module.

```text
context encoder
  -> hidden human/public state representations
  -> candidate action proposal
  -> public-toxic action pruning
  -> sparse safe core
  -> route-complement refill
       add only cells that improve route equation
       while staying outside H088 toxicity
  -> calibrated submission
```

H123 evidence:

- candidate: `submission_h123_refilleq_8958f688_uploadsafe.csv`;
- selected solver: `h123_sparse_route_refill_8958f688`;
- start from H122 cells: `24`;
- added cells: `2`;
- added targets: Q3 `1`, S3 `1`;
- final cells / rows: `26` / `20`;
- route-basis predicted delta vs H057: `-0.0007325`;
- model predicted delta vs H057: `-0.0000266`;
- H088-axis cosine: `-0.065510`;
- good-bad margin: `0.124697`.

The architectural distinction is:

```text
v5.5 asks whether unsafe proposal cells should be deleted.
v5.6 asks whether the deleted field leaves a missing route equation that a tiny
safe complement can repair.
```

The H122/H123 public comparison is now a direct architecture test:

- H122 win: action safety is mostly subtractive;
- H123 win: action safety is subtractive first, then constructive only at the
  route-complement residue.

## HS-JEPA v5.7: Dual-Sensor Refill Envelope

H124 adds a stricter safety rule to the refill module.

```text
context encoder
  -> hidden human/public state representations
  -> action proposal
  -> toxicity prune
  -> sparse core
  -> dual-sensor refill envelope
       route-basis must improve
       H098/frontier caution must also improve
       H088 and bad-axis constraints must remain safe
  -> calibrated submission
```

H124 evidence:

- candidate: `submission_h124_dualsensor_b8e822c0_uploadsafe.csv`;
- selected solver: `h124_strict_route_h098_refill_b8e822c0`;
- start from H122 cells: `24`;
- added cells: `3`;
- added targets: S1 `2`, Q3 `1`;
- final cells / rows: `27` / `22`;
- route-basis predicted delta vs H057: `-0.0007035`;
- model predicted delta vs H057: `-0.0000308`;
- H088-axis cosine: `-0.060942`;
- good-bad margin: `0.144874`.

The H123/H124 fork is now the cleanest architecture test:

```text
H123 = route-first refill.
H124 = route refill only when H098/model caution agrees.
```

## HS-JEPA v5.8: Optional Subject-Target Bundle Closure

H125 tests whether the dual-sensor refill cells should be closed as a
subject-target episode.

```text
context encoder
  -> action proposal
  -> toxicity prune
  -> dual-sensor refill
  -> optional subject-target bundle closure
       only if a remaining cell improves H098/margin
       and stays within H088/bad-axis constraints
  -> calibrated submission
```

H125 evidence:

- candidate: `submission_h125_rowbundle_f3990392_uploadsafe.csv`;
- selected solver: `h125_id04_s1_bundle_closure_f3990392`;
- start from H124 cells: `27`;
- added cells: `1`;
- added target: S1 `1`;
- final cells / rows: `28` / `23`;
- route-basis predicted delta vs H057: `-0.0007022`;
- model predicted delta vs H057: `-0.0000311`;
- H088-axis cosine: `-0.054369`;
- good-bad margin: `0.154855`.

The evidence is narrow.  HS-JEPA should not promote generic row-bundle
generation yet.  The safer architecture is:

```text
bundle closure is optional and only after prune/refill safety has already been
established.
```

## HS-JEPA v5.9: Component-Coefficient Action Equation

H126 adds one more layer after row-target assignment: coefficient solving over
the discovered action components.

```text
context encoder
  -> hidden human/public state
  -> action proposal
  -> toxicity prune
  -> dual-sensor refill
  -> optional bundle closure
  -> component coefficient solver
       core, Q3 refill, S3 tail, S1 margin, closure
       are scored as basis vectors, not independent cells
  -> calibrated submission
```

H126 evidence:

- candidate: `submission_h126_coeffeq_3fe3eee4_uploadsafe.csv`;
- selected solver: `h126_h125_closure_soft_3fe3eee4`;
- coefficient vector:
  `core=1.0;q3=1.0;s3=0.0;s1=1.0;closure=0.5`;
- final cells / rows: `28` / `23`;
- route-basis predicted delta vs H057: `-0.000702`;
- model predicted delta vs H057: `-0.000031`;
- H088-axis cosine: `-0.057670`;
- good-bad margin: `0.149911`.

The architecture claim is limited but useful:

```text
safe action support and safe action amplitude are separate decoder problems.
```

The strongest local equation still replays H125 exactly, so v5.9 is not a
standalone breakthrough.  Its value is architectural: after HS-JEPA predicts a
row-target action representation, a final equation solver should be allowed to
attenuate components that look structurally real but public/private
amplitude-sensitive.

## HS-JEPA v5.10: Residual Margin Basis Probe

H127 adds a narrow residual-basis probe after coefficient solving.

```text
context encoder
  -> hidden human/public state
  -> action proposal
  -> toxicity prune
  -> dual-sensor refill
  -> coefficient solver
  -> residual basis probe
       search outside active support
       exclude previously pruned toxic cells
       allow only route-preserving margin/toxicity improvements
  -> calibrated submission
```

H127 evidence:

- candidate: `submission_h127_residbasis_9b7f8d9a_uploadsafe.csv`;
- selected solver: `h127_episode_neighbor_residual_newbasis_9b7f8d9a`;
- added component: row `144` S2, `id06`;
- final cells / rows: `29` / `24`;
- route-basis predicted delta vs H057: `-0.000701`;
- model predicted delta vs H057: `-0.000031`;
- H088-axis cosine: `-0.051158`;
- good-bad margin: `0.160434`.

The architecture claim is:

```text
new residual components should be admitted only as toxicity/margin stabilizers
after the route equation is already preserved.
```

H127 is not a broad new HS-JEPA decoder.  It is a guardrail: residual mining
should not be allowed to chase route-basis unless the cell also survives
public/private toxicity stress.

## HS-JEPA v5.11: Frontier-Value Regenerator

H128 changes the proposal generator instead of mining one more residual cell.

```text
context encoder
  -> hidden human/public state
  -> H057 positive row-state sensor
  -> H088 toxicity/collapse sensor
  -> H098 frontier response equation
  -> regenerated value field
  -> H127 toxicity/margin assignment gate
  -> sparse row-target action field
  -> calibrated submission
```

H128 evidence:

- candidate: `submission_h128_frontiervalue_a6a6e648_uploadsafe.csv`;
- selected solver: `h128_conflict_bridge_margin_a6a6e648`;
- start field: H127;
- added component: S1 `2`, S4 `1`;
- final cells / rows: `32` / `27`;
- route-basis predicted delta vs H057: `-0.000697`;
- model predicted delta vs H057: `-0.000032`;
- H088-axis cosine: `-0.046361`;
- good-bad margin: `0.199979`.

The architecture claim is:

```text
HS-JEPA should not decode action directly from one latent head.
It should split the decoder into value generation and toxicity-aware assignment.
```

H088 remains a negative stress sensor, not a private action head.  H098 remains
dangerous as a direct proposal generator.  H128's only multi-cell survivor is a
conflict bridge, which means value appears where positive row-state and
negative action-state disagree, but it still needs a row-target safety gate.

## HS-JEPA v5.12: Toxic-Action Eraser

H129 adds a post-assignment eraser after support selection.

```text
context encoder
  -> hidden human/public state
  -> sparse support assignment
  -> optional conflict-value regeneration
  -> toxicity/amplitude field
       classify active actions by local public/private toxicity
       remove, damp, or keep each row-target action
  -> calibrated submission
```

H129 evidence:

- candidate: `submission_h129_toxiceraser_ce1ebc19_uploadsafe.csv`;
- selected solver: `h129_h122_core_toxicity_ce1ebc19`;
- start field: H122 sparse core;
- operations: remove Q1 `2`, remove Q3 `2`, damp Q1 `1`;
- final cells / rows: `20` / `17`;
- route-basis predicted delta vs H057: `-0.000610`;
- model predicted delta vs H057: `-0.000023`;
- H088-axis cosine: `-0.077331`;
- good-bad margin: `0.130968`.

The architecture claim is:

```text
safe support is not identical to safe action amplitude.
```

This is the first explicit HS-JEPA eraser stage.  It treats H088/H018 not as
action heads, but as collapse/toxicity stress sensors that help decide whether
an already-selected action should be removed or attenuated.  If H129 wins
publicly, HS-JEPA's decoder should be written as a row-target equation solver:

```text
support assignment + value regeneration + toxicity/amplitude erasure
```

rather than as a single latent-to-probability predictor.

## HS-JEPA v5.13: Row-Target Lattice Decoder

H130 replaces the stage sequence with a lattice over action states.

```text
context encoder
  -> hidden human/public state
  -> candidate row-target support
  -> value proposals from conflict/route sensors
  -> toxicity and amplitude sensors
  -> lattice decoder
       each cell chooses one state:
       off, damped, kept, or added
  -> calibrated submission
```

H130 evidence:

- candidate: `submission_h130_lattice_69da8d10_uploadsafe.csv`;
- selected solver: `h130_h122_full_lattice_69da8d10`;
- start field: H122;
- lattice cells: `32`;
- operations: off `3`, damp `5`, add `6`;
- final cells / rows: `27` / `23`;
- route-basis predicted delta vs H057: `-0.000640`;
- model predicted delta vs H057: `-0.000020`;
- H088-axis cosine: `-0.086159`;
- good-bad margin: `0.271542`.

Architecture implication:

```text
support, value, and toxicity are not sequential hacks.
They are simultaneous coordinates in a row-target action equation.
```

This is the cleanest current formulation of HS-JEPA as an action-grade solver.
The latent representation does not directly output labels.  It defines a
structured action lattice, and the decoder chooses which row-target actions are
safe under public/private stress equations.

## HS-JEPA v5.14: Sensor-Dropout Action Decoder

H131 adds a LeJEPA-style health check to the lattice decoder.  Instead of
trusting the full sensor bundle, each candidate row-target transition must
survive several partial observation equations:

```text
candidate row-target transition
  -> route/H098 view
  -> no-H088 view
  -> no-route view
  -> bad-axis/margin view
  -> accept only if multiple views agree
```

H131 evidence:

- candidate: `submission_h131_dropout_18a917f0_uploadsafe.csv`;
- selected solver: `h131_h122_dropout_robust_lattice_18a917f0`;
- start field: H122;
- operations: add `5`, off `0`, damp `0`;
- added targets: S1 `3`, Q3 `1`, S2 `1`;
- final cells / rows: `29` / `24`;
- mean dropout passes: `3.8` / `4`;
- route-basis predicted delta vs H057: `-0.000701`;
- model predicted delta vs H057: `-0.000031`;
- H088-axis cosine: `-0.052815`;
- good-bad margin: `0.161152`.

Architecture implication:

```text
HS-JEPA should distinguish:

1. representation that proposes action,
2. lattice state that materializes action,
3. sensor-dropout validator that decides whether the action is robust.
```

This reframes H088 and H018 again.  They are not action heads.  They are stress
sensors inside a dropout validator.  The current H131 result says that value
addition can be made robust under this validator, while the H130 delete/damp
toxicity field still needs a stronger non-H088 proof.

## HS-JEPA v5.15: Witness-Rescued Q1 Toxicity Field

H132 adds a narrower toxicity layer after H131.  The original hypothesis was
that erase/damp toxicity might be a row-bundle contradiction.  The experiment
partly rejects that:

```text
broad row bundle toxicity -> not action-grade
mixed Q/S bundle toxicity -> not action-grade
H122-only bundle toxicity -> not action-grade
small Q1 witness toxicity -> action-grade candidate
```

H132 evidence:

- candidate: `submission_h132_bundletox_ee252845_uploadsafe.csv`;
- selected solver: `h132_h131_plus_witness_q1_eraser_ee252845`;
- start field: H131;
- operations: Q1 off on rows `207`, `131`, `196`;
- final cells / rows: `26` / `21`;
- route-basis predicted delta vs H057: `-0.000705`;
- model predicted delta vs H057: `-0.000032`;
- H088-axis cosine: `-0.069636`;
- good-bad margin: `0.176076`.

Architecture implication:

```text
context/representation
  -> sensor-dropout safe value assignment
  -> witness-rescued target-specific toxicity eraser
  -> calibrated action field
```

This makes the HS-JEPA decoder more target-specific.  Q1 toxicity cannot yet be
generalized to all Q/S row bundles.  The next architecture question is why
these Q1 witness rows are toxic: row-state, subject block, target dependency,
or public-specific calibration.

## HS-JEPA v5.16: Intra-Row Target Assignment Decoder

H133 extends H132 by splitting a human-state row into target routes before
applying toxicity.  The core idea is:

```text
same row / same human-state context
  -> Q1 can be toxic
  -> Q3/S routes can remain safe or valuable
  -> action decoder must assign per target, not erase the row bundle
```

H133 evidence:

- candidate: `submission_h133_targetsplit_0cb376b8_uploadsafe.csv`;
- selected solver: `h133_h132_q1_only_signature_0cb376b8`;
- start field: H132;
- operations: Q1 off on rows `70`, `59`, `79`; Q1 half on row `135`;
- final cells / rows: `23` / `19`;
- route-basis predicted delta vs H057: `-0.000709`;
- model predicted delta vs H057: `-0.000031`;
- H088-axis cosine: `-0.072246`;
- good-bad margin: `0.164343`.

Rejected architecture variants:

```text
broad Q1/Q3 target split -> rejected by weak component gain
H088-shadow target split -> diagnostic only, not promoted
```

Architecture implication:

```text
context encoder
  -> safe value assignment field
  -> Q1 toxicity signature field
  -> per-row-target state assignment: keep / half / off
  -> H088/H018 stress diagnostics, never direct action heads
```

This moves HS-JEPA closer to the active objective: the hidden representation is
not enough.  The architecture must decide whether the action created from that
representation is public/private safe for each row-target route.

### H134: Companion-Route Conservation Decoder

H134 adds a conservation hypothesis to the row-target equation.  A Q1
subjective residue may be toxic if simply deleted or expanded, but safe if the
same row-state mass is reassigned into a companion Q3/S route.

Architecture role:

```text
context:
  H132/H133 Q1 witness rows
  row conversion pressure
  residual safety/toxicity
  route/H098/curvature equation

target representation:
  companion route assignment field over Q3/S1/S2/S4

decoder:
  propose add/toward-proposal states for companion cells
  reject actions by public/private stress sensors
  do not use H088/H018 as action heads
```

H134 evidence:

- candidate: `submission_h134_q1companion_ac53dd2e_uploadsafe.csv`;
- selected solver: `h134_h132_precompanion_q1state_ac53dd2e`;
- start field: H132, not H133;
- promoted operations: row `164` S4, row `207` Q3, row `135` S4;
- route-basis predicted delta vs H057: `-0.000721183`;
- H088-axis cosine: `-0.065490160`;
- good-bad margin: `0.170049532`;
- H133-start companion branches were rejected.

Architectural implication:

H134 splits the next HS-JEPA branch into two competing decoders:

```text
toxicity decoder:
  Q1-only target deletion/half-off after H132

conservation decoder:
  keep H132 Q1 witness field, then reassign hidden state into Q3/S4 companions
```

This is useful for the paper because it turns public LB tweaking into a
testable representation claim: HS-JEPA actions are not just probability
corrections; they are route assignments whose safety depends on whether hidden
human-state mass is conserved or destroyed.

### H135: Atomic Row-Vector Action Decoder

H135 extends H134 by changing the action unit.

```text
H134 action unit:
  one row-target cell

H135 action unit:
  one same-row target vector bundle
```

The architectural claim is that HS-JEPA should not decode human-state residue
into independent target probabilities.  It should predict an assignment field
over row-target vectors, then check whether the whole vector is safe under
public/private observation equations.

H135 evidence:

- candidate: `submission_h135_rowvector_c86ff9aa_uploadsafe.csv`;
- selected solver: `h135_h132_rowvector_route_heavy_c86ff9aa`;
- selected bundles:
  - row `164` S1/S4;
  - row `135` S4/Q3;
  - row `207` Q3;
- route-basis predicted delta vs H057: `-0.000760260`;
- H088-axis cosine: `-0.059761952`;
- good-bad margin: `0.157167089`.

Architecture implication:

```text
HS-JEPA context encoder
  -> hidden human-state residue
  -> row-vector assignment proposal
  -> equation solver chooses atomic bundles
  -> H088/H018 remain stress diagnostics
```

This is the first version where the "action" is no longer a cell correction.
It is a row-target vector route.  That is closer to the active thesis: the
breakthrough is not a better context encoder, but a decoder that separates
public-punished action toxicity from safe assignment fields.

### H136: Benefit-Toxicity Factorized Assignment Decoder

H136 turns the H135 row-vector decoder into an equation solver with two
explicit latent fields:

```text
benefit field:
  expected improvement under route / H098 / curvature equations

toxicity shadow field:
  expected damage under H088 / good-bad margin / forbidden-axis stress

assignment field:
  choose row-target vector actions only when benefit survives toxicity
```

The action is still a row-target vector, but the decoder no longer treats
larger route gain as automatically action-grade.  It asks whether the route
gain is safe under public/private observation equations.

H136 evidence:

- candidate: `submission_h136_factorized_dc9dd2c5_uploadsafe.csv`;
- selected solver: `h136_h132_factorized_route_pareto_dc9dd2c5`;
- selected bundle: row `164` S1/S4;
- pruned H135 completion tail: row `135` S4/Q3 and row `207` Q3;
- route-basis predicted delta vs H057: `-0.000762294`;
- H088-axis cosine: `-0.062132664`;
- good-bad margin: `0.159441050`;
- benefit/toxicity ratio: `1.340889784`.

Architecture implication:

```text
HS-JEPA context encoder
  -> hidden human-state residue
  -> row-vector route proposal
  -> benefit/toxicity factorization
  -> assignment solver emits only action-grade vectors
  -> H088/H018 stay stress diagnostics, not private action heads
```

This is the current formal direction for HS-JEPA: the breakthrough component
is not a stronger encoder, but an action decoder that can distinguish safe
assignment from toxic completion.

### H137: Counterfield Diagnostic Decoder

H137 adds a diagnostic branch after H136:

```text
if a completion tail is toxic:
  first test pruning
  then test whether a tiny opposite-direction counterfield is needed
```

The full anti-tail vector failed the local stability check, so HS-JEPA should
not model toxicity as a simple reversible vector.  The only promoted
counterfield is a tiny row `207` S2 move from the H136 field.

H137 evidence:

- candidate: `submission_h137_tailtox_2bea533f_uploadsafe.csv`;
- selected solver: `h137_counter_r207_S2_f0p25_g0p25_2bea533f`;
- start field: H136;
- changed action: row `207` S2 `-0.0021167147`;
- H088 delta vs H136: `-0.000988686`;
- margin delta vs H136: `-0.000145272`;
- route-basis predicted delta vs H057: `-0.000761060`.

Architecture implication:

```text
HS-JEPA action decoder
  -> row-vector proposal
  -> benefit/toxicity factorization
  -> prune toxic completion
  -> optional tiny counterfield only if route/margin gates survive
```

This clarifies the decoder hierarchy: counterfields are subordinate diagnostic
actions, not primary H088-driven heads.

### H138: Role-Aware Boundary Decoder

H138 adds the missing role assignment layer.  A counterfield is not accepted
because it improves H088; it is accepted only when another action repairs the
public/private boundary it damages.

H138 evidence:

- candidate: `submission_h138_boundary_52b26210_uploadsafe.csv`;
- selected solver: `h138_boundary_pair_g025_52b26210`;
- start field: H136;
- toxicity-relief role: row `207` S2;
- margin-repair role: row `135` Q3/S2;
- changed cells vs H136: `3`;
- H088 delta vs H136: `-0.001088214`;
- margin delta vs H136: `+0.000064141`;
- route delta vs H136: `+0.000002453`;
- H098/model delta vs H136: `+0.000001352`.

Architecture implication:

```text
HS-JEPA context encoder
  -> hidden human-state residue
  -> row-target action atoms
  -> role classifier:
       route-benefit
       toxicity-relief
       margin-repair
       stress-decoy
  -> public/private equation solver
  -> emit only role-compatible assignments
```

The important update is that "safe action" is not a scalar.  H138 makes it a
small equation over roles.  This is closer to the intended HS-JEPA formulation:
predict hidden human-state representation, then solve which row-target action
roles are compatible under the observation equation.

### H139: Automatic Role-Atom Solver

H139 turns H138's hand-built role pair into an automatic solver.

The decoder builds candidate atoms around H136, classifies them, and searches
for role-compatible combinations.  The row `164` H136 core is locked so the
solver cannot fake margin repair by undoing the positive route-state signal.

H139 evidence:

- candidate: `submission_h139_roleatoms_bf2b3e77_uploadsafe.csv`;
- selected solver: `h139_bf2b3e77`;
- locked core: row `164`;
- toxicity-relief atoms: row `207` S2 and row `131` S2;
- margin-repair atom: row `70` Q3;
- changed cells vs H136: `3`;
- H088 delta vs H136: `-0.002418045`;
- margin delta vs H136: `+0.000119165`;
- route delta vs H136: `+0.000002427`;
- H098/model delta vs H136: `+0.000001653`.

Architecture implication:

```text
context/state encoder
  -> H136 route core
  -> atom generator
  -> role classifier
       locked_core_unwind
       toxicity_relief
       margin_repair
       stress_decoy
  -> constrained role equation solver
  -> submission action field
```

This is the current strongest HS-JEPA formulation.  The main learnable object is
no longer a better feature embedding; it is the row-target action-role equation
that decides which representation-induced actions are public/private safe.

### H140: Sensor-Dropout Selector

H140 adds a validation layer to the H139 role-atom solver.

Since H088 is only a stress diagnostic, a role equation that wins only by
maximizing H088 relief may be a shortcut.  H140 reranks the H139 candidate
frontier under multiple sensor-dropout views and promotes the candidate that
survives without row `207`.

H140 evidence:

- candidate: `submission_h140_roledrop_a5d0258f_uploadsafe.csv`;
- selected source: `h139_a5d0258f`;
- row `207`: absent by design;
- toxicity-relief atom: row `131` S2;
- margin-repair atoms: row `70` Q3 and row `135` Q3/S2;
- changed cells vs H136: `4`;
- H088 delta vs H136: `-0.001529738`;
- margin delta vs H136: `+0.000482990`;
- route delta vs H136: `+0.000002412`;
- H098/model delta vs H136: `+0.000001699`.

Architecture implication:

```text
role atom solver
  -> candidate frontier
  -> sensor-dropout selector:
       H088-heavy view
       no-H088 view
       H098-tight view
       route-tight view
       simplicity / row207 dropout view
  -> public sensor submission pair
```

H140 does not replace H139.  Together they define the decoder's next critical
uncertainty:

```text
Is row207 H088 relief action-grade, or is robust H088-dropout survival safer?
```

### H141: Common-Core Equation Probe

H141 adds a third point to the H139/H140 public sensor pair.

Instead of choosing the H088-heavy branch or the sensor-dropout branch, H141
keeps only their overlap:

```text
row70 Q3  -> margin repair
row131 S2 -> toxicity relief
```

H141 evidence:

- candidate: `submission_h141_commoncore_0999d3ae_uploadsafe.csv`;
- selected source: `h139_0999d3ae`;
- row `207`: absent by design;
- row `135`: absent by design;
- changed cells vs H136: `2`;
- H088 delta vs H136: `-0.001425939`;
- margin delta vs H136: `+0.000266163`;
- route delta vs H136: `+0.000001193`;
- H098/model delta vs H136: `+0.000001000`.

Architecture implication:

```text
role atom solver
  -> branch decomposition:
       common core
       H088-heavy optional tail
       sensor-dropout repair add-on
  -> public/private equation sensor submissions
```

This makes the HS-JEPA decoder less like a single learned correction vector and
more like an assignment/equation solver.  The representation proposes row-target
actions; the solver separates the common action-grade field from optional
branches that may be public-sensor shortcuts.

### H142: Branch Co-Activation Barrier Probe

H142 changes the decoder question again.

After H141, the row-target equation has three pieces:

```text
common core = row70 Q3 + row131 S2
row207 branch = H139 - H141
row135 branch = H140 - H141
```

The natural JEPA-style question is whether hidden human state predicts an
additive action field or a branch assignment:

```text
additive: H141 + alpha * row207 + beta * row135
assignment: choose row207 branch or row135 branch, but not both
```

H142 evidence:

- candidate: `submission_h142_branchbarrier_338bb491_uploadsafe.csv`;
- alpha row207 branch: `0.50`;
- beta row135 branch: `0.50`;
- changed cells vs H136: `5`;
- H088 delta vs H136: `-0.001999657`;
- margin delta vs H136: `+0.000361794`;
- route delta vs H136: `+0.000003610`;
- H098/model delta vs H136: `+0.000001727`;
- balanced barrier probe pass: `True`;
- clean saddle pass: `False`.

Architecture implication:

```text
HS-JEPA decoder vNext
  -> common action core predictor
  -> optional branch predictors
  -> co-activation toxicity detector
  -> XOR-style assignment solver if branch co-activation is public-toxic
```

The key update is that "safe action" may not mean "blend the best actions."
The decoder may need to infer which hidden world a row-target belongs to and
activate only that branch.

### H143: XOR Branch Assignment Decoder

H143 implements the architecture implied by H142.

The decoder no longer assumes optional branches are additive.  It evaluates
branch-exclusive paths:

```text
common core + gamma * row207 branch
common core + gamma * row135 branch
```

Known endpoints are references:

```text
H139 = row207 gamma 1.00
H140 = row135 gamma 1.00
```

H143 evidence:

- candidate: `submission_h143_xorbranch_4894032a_uploadsafe.csv`;
- selected branch: row `207`;
- gamma: `0.80`;
- row `135`: absent by design;
- changed cells vs H136: `3`;
- H088 delta vs H136: `-0.002229244`;
- margin delta vs H136: `+0.000172037`;
- route delta vs H136: `+0.000002418`;
- H098/model delta vs H136: `+0.000001533`;
- XOR branch pass: `True`.

Architecture implication:

```text
HS-JEPA decoder
  -> common action core
  -> branch classifier: none / row207 / row135
  -> branch amplitude predictor
  -> co-activation veto
```

H143 is important because it gives HS-JEPA a concrete next decoder form:
assignment first, amplitude second.  This is different from both a tabular
model and a linear blend.

### H144: Target-Split XOR Assignment

H144 refines the H143 decoder.

H143 asks which row-level branch should be active.  H144 asks whether a row
branch should be split into target-level components:

```text
row135 branch
  -> row135 Q3 repair
  -> row135 S2 route-toxic component
```

H144 evidence:

- candidate: `submission_h144_targetxor_def80b88_uploadsafe.csv`;
- row `207` S2: full branch on;
- row `135` Q3: on;
- row `135` S2: off;
- changed cells vs H136: `4`;
- H088 delta vs H136: `-0.002642643`;
- margin delta vs H136: `+0.000506952`;
- route delta vs H136: `+0.000002420`;
- H098/model delta vs H136: `+0.000002113`;
- target-split pass: `True`.

Architecture implication:

```text
HS-JEPA decoder
  -> common action core
  -> row branch proposal
  -> target component splitter
  -> target-level veto mask
  -> public/private equation check
```

This is a more specific architecture than H143.  A "human-state" does not just
choose a row branch; it may select which target routes inside that row are safe
actions.

### H145: Q3 Repair-Only Veto Decoder

H145 adds a counterfactual decoder path to H144.

H144 keeps row207 S2 and row135 Q3.  H145 vetoes row207 S2 as well:

```text
H144 decoder:
  common core + row207 S2 + row135 Q3 - row135 S2

H145 decoder:
  common core + row135 Q3 - row207 S2 - row135 S2
```

H145 evidence:

- candidate: `submission_h145_q3repair_2d818e46_uploadsafe.csv`;
- row `135` Q3 amplitude: `1.15`;
- row `207` S2: off;
- row `135` S2: off;
- changed cells vs H136: `3`;
- H088 delta vs H136: `-0.001674775`;
- margin delta vs H136: `+0.000702228`;
- route delta vs H136: `+0.000001185`;
- H098/model delta vs H136: `+0.000001530`;
- Q3 repair pass: `True`.

Architecture implication:

```text
HS-JEPA decoder
  -> target-level action proposals
  -> stress-diagnostic veto for H088-heavy components
  -> repair-first branch when route/H098 are stable
```

This is a deliberate challenge to the current H088-relief branch.  It tests
whether "action-grade" should be defined by repair/margin stability rather than
H088-axis movement.
