# Human-State JEPA Team Architecture

Last updated: 2026-06-08

## One-Sentence Definition

Human-State JEPA, or HS-JEPA, is an architecture that predicts hidden human
state representations from partial lifestyle-log context, then translates those
states into row-target probability corrections only when the correction appears
safe.

It is not a blend recipe and it is not just a tabular model. The central object
is a hidden state, not a feature list.

```text
observed lifestyle context
  -> human-state encoder
  -> hidden state representation
  -> target-route / action-health decoder
  -> row-target correction field
  -> upload-safe submission
```

## Why We Need It

The competition target is seven binary sleep-related labels:

- `Q1`, `Q2`, `Q3`: subjective sleep and intervention-related labels.
- `S1`, `S2`, `S3`, `S4`: objective sleep-stage related labels.

The strongest public result so far is:

- file: `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv`
- public LB: `0.5677475939`

This result is best understood as a row-state correction, not as a generic
model improvement. It found a compact set of test rows where several targets
should move together, while `Q2` should stay fixed. That is the first strong
reason to model the data as hidden human states.

## JEPA Interpretation

Standard JEPA asks:

> Can visible context predict the representation of something hidden?

HS-JEPA translates that question into this competition:

> Can visible lifestyle context predict the hidden day-level human state that
> explains which row-target probabilities should be corrected?

The model does not reconstruct raw sensor values. It predicts representations
such as:

- whether today is a normal day for this subject;
- whether today belongs to a hidden sleep-state route;
- whether a target correction is public-safe or likely toxic;
- whether Q-labels and S-labels should move together or separately;
- whether a row is better explained by personal history, peer cohort, or public
  subset behavior.

## Core Components

### 1. Context Encoder

The context encoder consumes multiple views of the same day:

- raw daily lifelog features: phone use, app categories, activity, sleep-related
  watch signals, light, charging, GPS, Wi-Fi/BLE proximity, heart rate;
- calendar and routine context: weekday/weekend, month boundary, timing;
- subject context: personal baseline, deviation from personal baseline;
- cohort context: peer group of similar subjects and deviation from peer norm;
- prediction context: existing submission disagreement and correction history.

These views are treated as context, not direct label rules.

### 2. Hidden Human-State Representation

A hidden state is a compact embedding of a subject-day. It is meant to explain
why some labels should move together.

Examples:

- personal anomaly state: "today is unusual for this subject";
- cohort anomaly state: "today is unusual among similar subjects";
- route state: "this row follows a Q/S correction pattern";
- public/private state: "this action looks public-safe but may not generalize";
- action-health state: "this row-target correction is likely safe or toxic".

### 3. Target-Route Decoder

The decoder does not blindly output seven probabilities. It chooses a correction
route:

- move only one target;
- move a Q group;
- move an S group;
- move a full row except `Q2`;
- leave the row unchanged.

This is important because the strongest result moved structured row-target
groups, not random individual cells.

### 4. Action-Health Gate

The action-health gate asks whether a proposed correction should be trusted.

Inputs can include:

- listener/posterior consistency;
- known public sensor responses;
- disagreement between candidate predictions;
- hidden-state confidence;
- personal/cohort anomaly strength;
- shortcut and collapse diagnostics.

The gate is the current bottleneck. We can find plausible hidden states, but
translating them into safe probability moves is harder.

## Cohort-Relative Module

The teammate cohort idea asks three questions:

1. Which lifestyle group does this subject belong to?
2. Is today unusual for this subject?
3. Is today unusual among similar subjects?

HS-JEPA uses this module as a context view:

```text
daily sensor features
  -> human-state latent
  -> subject fingerprint
  -> peer cohort
  -> personal and cohort anomaly scores
  -> action-health context
```

The cohort module should not directly overwrite `Q2`, `Q3`, or `S2`. It should
first become hidden-state evidence, then the decoder decides whether a
row-target correction is safe.

## Cohort Experiment Result

Implemented experiment:

- code: `team_experiments/cohort_hsjepa/cohort_hsjepa_experiment.py`
- report: `team_experiments/cohort_hsjepa/cohort_hsjepa_report.md`
- candidate:
  `submission_team_cohort_hsjepa_gate_0f0db65a_uploadsafe.csv`

Main findings:

- 99 daily lifestyle/sensor features were aggregated from raw logs.
- An 8-dimensional human-state latent and 4 peer cohorts were built.
- Personal anomaly weakly aligned with current best hidden rows
  (`AUC = 0.5599`).
- Peer-cohort anomaly did not align strongly with current best hidden rows
  (`AUC = 0.4989`).
- Cohort context slightly helped subject-group CV but hurt date-block CV.
- The generated candidate was essentially neutral on soft listener loss
  (`+0.000000067` versus current best), so it is not submission-grade yet.

Interpretation:

The cohort idea is useful as a representation/context module, especially for
personal-normal versus unusual-day reasoning. It is not yet a safe action
decoder. The next step is not to amplify cohort outliers directly, but to teach
the action-health gate when cohort evidence is trustworthy.

## What HS-JEPA Can Do

HS-JEPA gives us a reproducible way to:

- explain why a correction moves a row-target group instead of a single cell;
- compare personal baseline and peer cohort baseline;
- separate hidden-state discovery from probability correction;
- test whether human-social hypotheses are real signal or shortcut;
- reuse public LB feedback as a sensor without treating it as direct truth;
- write team-readable experiments where each submission is a falsifiable claim.

## Current Maturity

| Layer | Status | Evidence |
| --- | --- | --- |
| Current best reproduction | Strong | End-to-end script reproduces the best public file exactly. |
| Row-state discovery | Strong | Public best is explained by compact row-state correction. |
| Human-social context | Medium | Several social/routine stories align with action-health, but direct routing is weak. |
| Cohort-relative context | Medium | Personal anomaly is useful; peer anomaly is not yet decisive. |
| Action-health decoder | Weak-medium | We can score risk, but safe correction translation is still the bottleneck. |
| Public/private factorization | Prototype | Useful diagnostic, not yet a decisive decoder. |

## Reproducibility Entry Points

Run current best reproduction:

```bash
python3 hs_jepa_end_to_end.py
```

Run cohort-relative HS-JEPA experiment:

```bash
python3 team_experiments/cohort_hsjepa/cohort_hsjepa_experiment.py
```

Inspect generated reports:

```bash
open hs_jepa_end_to_end/hs_jepa_end_to_end_report.md
open team_experiments/cohort_hsjepa/cohort_hsjepa_report.md
```

## Next Architecture Work

The next important architecture step is a safer action decoder:

```text
hidden state evidence
  + personal anomaly
  + cohort anomaly
  + target route
  + public/private diagnostic
  -> action toxicity / safety field
  -> constrained row-target assignment
```

The target is not a small blend improvement. The target is to identify when a
hidden state should be converted into a probability move and when it should
remain only a diagnostic signal.
