# HS-JEPA Final Big Bet Ideas

Last updated: 2026-06-09

This document keeps only two end-to-end ideas. The goal is not to propose small
adjustments. Each idea is a complete world model: if it wins, it explains why
the current score barrier existed; if it fails, it kills a major hypothesis.

Current strongest public result:

- `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv`
- public LB: `0.5677475939`

## Current Bottleneck

We have evidence for hidden row-state structure. The hard part is not finding
another plausible latent. The hard part is deciding which hidden state should
be translated into a probability correction.

The main bottleneck is:

> hidden-state discovery is ahead of action decoding.

Several signals are useful as context:

- public-equation state;
- compact row-state correction;
- human-social/routine context;
- personal anomaly;
- cohort-relative anomaly;
- action-health and shortcut diagnostics.

But direct translation into row-target corrections often becomes toxic. The
final ideas below both attack this translation problem.

---

# Big Bet 1: Public-Private Equation HS-JEPA Solver

## One-Line Idea

Treat every submitted file and public LB score as a noisy equation, then solve
for the hidden public listener, row-target responsibility, and safe correction
field jointly.

## World Hypothesis

Public LB is not just a score. It is a sensor measuring a hidden subset and a
hidden row-target weighting system.

The current best improved because it accidentally moved cells that have high
public responsibility and low action toxicity. To break the barrier, we should
not make another candidate by intuition. We should reconstruct the hidden
equation that public LB has been evaluating.

## End-to-End Pipeline

```text
all historical submissions
  + known public LB scores
  + current best probabilities
  + raw human-state / cohort / social context
  -> public listener equation inversion
  -> row-target responsibility field
  -> route-constrained action solver
  -> upload-safe candidate
```

## Model Components

### 1. Submission Delta Matrix

For every known submission, compute:

```text
delta_logit[submission, row, target]
delta_prob[submission, row, target]
```

Use the public LB deltas as observations:

```text
observed_lb_delta(submission)
  ~= sum(row_target_weight * loss_change(row, target, submission))
```

Unknowns:

- public row-target weight;
- pseudo-public label/posterior;
- action toxicity;
- route assignment.

### 2. JEPA Context Encoder

Context views:

- raw daily human-state features;
- personal anomaly;
- cohort anomaly;
- target route features;
- submission disagreement;
- public-bad and public-good action history.

Target representation:

- hidden public responsibility;
- safe action value;
- row-target route.

Masking task:

- mask a subset of public observations;
- predict their LB response from the hidden equation;
- mask candidate families and predict whether their movement is toxic.

### 3. Equation-Constrained Decoder

The decoder chooses actions under constraints:

- row-route sparsity;
- target-route consistency;
- no uncontrolled full-table movement;
- public-good direction must survive leave-one-public-observation-out;
- public-bad directions get negative penalty;
- actions must not collapse into a single target prior shift.

Candidate generation becomes an optimization problem:

```text
maximize expected equation gain
minus action toxicity
minus shortcut risk
minus private-overfit penalty
```

## Why This Could Be First-Place Level

The largest jump came from public-equation style information, not from normal
CV. If the hidden public listener can be reconstructed even partially, this is
one of the few paths that can move public LB by more than small tuning amounts.

This idea uses all existing work:

- public score history;
- row-state correction;
- action-health failures;
- human/social context;
- cohort context;
- target route constraints.

## Success Criteria

Before submitting:

- leave-one-public-observation-out sign accuracy above `70%`;
- predicted LB delta scale roughly matches known deltas;
- null-permuted submissions fail the equation fit;
- selected actions are not dominated by one target or one subject;
- selected route support overlaps current best positives but also discovers new
  rows with positive expected gain.

Submission-level expected result:

- a meaningful public movement, not `0.0001`;
- if right, should plausibly beat current best by `0.001+`;
- if wrong, likely reveals that public equation inversion is overfit.

## What Failure Means

If this fails cleanly, it means public LB observations are too few or too noisy
to identify a stable row-target responsibility field. Then public scores should
remain sensors, not direct solver targets.

---

# Big Bet 2: Personal-Cohort Human-State Atlas JEPA

## One-Line Idea

Build an interpretable atlas of hidden human day-states from raw lifelog data,
then predict labels by state route and personal/cohort memory rather than by
direct feature-to-label modeling.

## World Hypothesis

The labels are generated by a small number of hidden human states:

- normal routine day;
- fragmented sleep / recovery day;
- night-phone arousal day;
- low-activity fatigue day;
- high-social or late-interaction day;
- measurement-noise day;
- subjective-good but objective-bad mismatch day;
- objective-stage disruption day.

The current best found one compact row-state. To reach a larger improvement,
we need a fuller atlas of these states and a decoder that knows which target
route each state uses.

## End-to-End Pipeline

```text
raw lifelog by subject-day
  -> open-source daily feature encoder
  -> personal baseline state
  -> peer-cohort baseline state
  -> human-state atlas assignment
  -> target route posterior
  -> safe correction field
  -> upload-safe candidate
```

## Model Components

### 1. Daily Human-State Encoder

Use only reproducible/open-source computation.

Inputs:

- phone usage and app categories;
- activity and step rhythm;
- heart-rate and wearable light;
- screen/charging timing;
- GPS/Wi-Fi/BLE proximity;
- ambience labels;
- calendar and routine timing.

Represent each subject-day as several context views:

- personal-normal coordinate;
- cohort-normal coordinate;
- raw sensor coordinate;
- social/routine coordinate;
- measurement-confidence coordinate.

### 2. Atlas Construction

Build a small dictionary of latent day-states.

Do not cluster only by raw features. Cluster by multi-view consistency:

```text
state = f(
  raw sensor latent,
  personal deviation,
  cohort deviation,
  sequence neighborhood,
  target-route compatibility,
  action-health diagnostic
)
```

Each atlas state has:

- state centroid;
- subject-specific offset;
- cohort offset;
- target route distribution;
- confidence/measurement quality;
- action toxicity profile.

### 3. JEPA Masked Prediction

Prediction tasks:

- mask raw sensor family and predict atlas state;
- mask personal history and predict current state from cohort;
- mask cohort and predict personal deviation;
- mask Q labels and predict S-route representation;
- mask S labels and predict Q-route representation;
- mask action response and predict toxicity from state.

This is the actual HS-JEPA part: visible context predicts hidden human-state
representations, not raw values.

### 4. Route-Aware Label Decoder

For each test row, produce:

```text
P(state | context)
P(route | state, subject, cohort)
P(action_safe | state, route)
```

Then apply only route-consistent corrections:

- state says "subjective route": mostly Q labels;
- state says "objective route": mostly S labels;
- state says "mismatch route": Q/S move in opposite directions;
- state says "measurement-noise route": reduce confidence, do not overcorrect;
- state says "known public row-state": use current best route unless toxicity
  blocks it.

## Why This Could Be First-Place Level

The current best is probably one discovered piece of the hidden atlas. This
idea tries to recover the broader state dictionary, including states that are
private-safe because they are grounded in raw lifelog and subject/cohort
structure rather than only public feedback.

This is the strongest paper-grade version of HS-JEPA:

- human meaning exists at the latent state level;
- target labels are projections of hidden human states;
- public LB feedback is used only as one action-health sensor;
- cohort-relative reasoning is included but not directly trusted.

## Success Criteria

Before submitting:

- atlas states have stable train/test distributions;
- each state has nontrivial target-route prior;
- personal anomaly improves state assignment more than peer anomaly alone;
- cohort feature helps explain unseen-subject or held-out-subject behavior;
- masked-view state prediction survives permutation/null tests;
- generated correction field changes route-consistent row-target groups, not
  isolated random cells.

Submission-level expected result:

- if atlas recovers a new real state, public LB should move by `0.001+`;
- if it only rediscovers current best rows, upside is small and the idea is not
  worth a submission slot.

## What Failure Means

If this fails, the human-social/cohort theory is probably good for narrative
and diagnostics but not strong enough to drive final probability actions. Then
the winning path should prioritize the equation solver, not richer human-state
semantics.

---

# Final Recommendation

Run both ideas, but do not give them equal roles.

## Submission-Winning Candidate

Primary bet:

> Public-Private Equation HS-JEPA Solver

Reason:

It directly attacks the largest known jump source: public-score sensor
inversion and row-target responsibility.

## Paper-Grade Architecture Candidate

Primary architecture:

> Personal-Cohort Human-State Atlas JEPA

Reason:

It turns HS-JEPA into a reusable model of human lifestyle states instead of a
leaderboard-only solver.

## How They Combine

The final system should be:

```text
Human-State Atlas
  -> proposes state and route candidates

Public-Private Equation Solver
  -> decides which proposed actions are safe enough to materialize
```

The atlas is the generator. The equation solver is the judge.

If the judge acts without the atlas, it overfits public. If the atlas acts
without the judge, it produces plausible but unsafe corrections. The combined
HS-JEPA system needs both.
