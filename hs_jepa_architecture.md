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
