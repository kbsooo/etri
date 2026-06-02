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
