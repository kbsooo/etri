# Human-State Hypotheses

Last updated: 2026-06-02

## Source

Main source file:
`hitl/human_state_route_hypotheses_1000.csv`

The file contains `1000` human-social route hypotheses with these columns:

- `hypothesis_id`
- `human_story`
- `observable_log_pattern`
- `hidden_human_state`
- `expected_target_route`
- `likely_row_condition`
- `why_plausible`
- `what_would_falsify_it`
- `minimal_experiment`
- `prediction_role`
- `risk_of_being_spurious_leakage_public_overfit`
- `priority`

Priority distribution:

| Priority | Count |
| --- | ---: |
| high | 319 |
| medium | 478 |
| low | 203 |

## Important Rule

These hypotheses must not be applied as direct label rules.

Correct use:

```text
human story -> story family latent -> HS-JEPA target representation
             -> row-target correction field
```

Incorrect use:

```text
human story -> directly push Q/S probabilities
```

H010 already showed that a plausible direct objective route can fail badly. The
human layer is a context encoder, not a hand-written label oracle.

## Condensed Human-State Families

The 1000 rows compress into reusable state families. Top observed families
include:

| Hidden state family | Count or role |
| --- | --- |
| `badnight_aftereffect` | 20 |
| `sleep_inertia_after_badnight` | 10 |
| `compensatory_recovery_after_badnight` | 10 |
| `daytime_fatigue_after_badnight` | 10 |
| `irritability_after_badnight` | 10 |
| `cognitive_slump_after_badnight` | 10 |
| `rebound_recovery_after_badnight` | 10 |
| `withdrawal_after_badnight` | 10 |
| `forced_commute_after_badnight` | 10 |
| `nocturnal_awake_trace` | 10 |
| `masked_badnight_aftereffect` | 10 |
| `home_recovery` and related home-rest states | multiple |
| `bedtime_social_arousal` and arousal states | multiple |
| `financial_rumination_arousal` / cashflow states | multiple |

The dominant prediction roles are gates, not direct routes:

- subject/weekend gate before direct action;
- subject-specific gate plus sparse direct route;
- confidence gate unless app evidence is strong;
- calendar gate plus sparse route, never broad move;
- calibration gate until block-stable;
- subject-specific sign gate.

This supports the HS-JEPA interpretation: human stories define conditional
contexts and latent states, not global probability shifts.

## Story Families to Encode

## H070 Story-Route Encoding

H070 used the 1000 hypotheses for the first time inside the full HS-JEPA
decoder. The stories were still not used as direct label rules. They were
compressed into target-route priors:

```text
story_route_up[target]
story_route_down[target]
story_route_no_direct[target]
story_route_direct[target]
story_route_balance[target]
```

These priors were merged into each row-target cell and used as one masked view
inside the joint decoder. The result is useful but incomplete: context/story
views can predict public/private/action representations with high rank
correlation, but smooth latent scoring still stops at public-action predicted
delta `-0.000826` versus H057. The next human-state step should therefore be
assignment-aware: story families should constrain which row-target route can
exist, not merely add a continuous score.

## H071 Route-Assignment Use

H071 is the first assignment-aware decoder. It still does not let stories push
labels directly. Instead, H070's story-route priors are one part of the latent
context used to choose a row route such as `full_state`, `nonq2_full`,
`q3_s_stage`, `s_stage`, `q2_hardtail`, or `recovery_route`.

The promoted H071 candidate is intentionally broad: `736` changed cells on
`158` rows, with most changes outside H069. That means the next human-social
work should focus on route dictionary quality. The key question is no longer
"which story changes Q3?" but "which story makes a row eligible for a
full-state, objective-stage, subjective-Q, or recovery route?"

### 1. Bad-Night Aftereffect

Story:
bad sleep leaves a morning trace: early phone use, search, social apps, delayed
or stressed start.

Likely target route:
Q3 up, Q1 down, Q2 weakly up only if strongly gated, S targets usually
secondary.

HS-JEPA use:
context view for `z_human_context`, not direct Q3 correction unless it recovers
H057/H068 action-health.

### 2. Nocturnal Awake Trace

Story:
the person wakes during the night and uses the phone in bed.

Likely target route:
Q3 up, S3 down, Q1 down. S-stage route is possible but risky.

HS-JEPA use:
high-value context for action-health because it is semantically close to sleep
quality, but must be guarded against night-shift and charging-habit shortcuts.

### 3. Masked Routine Pressure

Story:
the day looks like a normal weekday, but tiny residuals reveal bad sleep under
a rigid routine.

Likely target route:
small Q3 hardtail, usually no broad S route.

HS-JEPA use:
candidate source for row-target assignment, because signal may appear only in
small residual cells.

### 4. Social/Arousal State

Story:
late messages, calls, social browsing, short-form media, or emotionally loaded
apps delay sleep or fragment it.

Likely target route:
Q3 up, Q1 down, sometimes Q2 up; S targets only under nocturnal evidence.

HS-JEPA use:
story-family latent for bedtime arousal, compared against H050-null and bad
JEPA axes.

### 5. Recovery/Home-Rest State

Story:
home rest, lower stimulation, regular bed anchor, and reduced movement can
represent recovery rather than bad sleep.

Likely target route:
Q1 up, Q3 down, S route subject-specific.

HS-JEPA use:
negative or sign-flip counterpart to bad-night states.

### 6. Work/Commute Pressure

Story:
workday/commute pressure forces activity despite poor sleep.

Likely target route:
Q3 up with possible Q2 change; S objective route is risky.

HS-JEPA use:
subject and weekday conditioning. Must not become a subject/date shortcut.

### 7. Weekend/Social Jetlag

Story:
weekend changes sleep timing and social behavior, sometimes improving recovery
and sometimes worsening rhythm.

Likely target route:
sign may flip by subject. Global action is unsafe.

HS-JEPA use:
public/private stress gate and subject-specific latent view.

### 8. Cashflow/Month Boundary

Story:
payday, month-end, month-start, or financial rumination can change stress,
late browsing, purchase/search behavior, and sleep.

Likely target route:
only valid when calendar timing is paired with behavioral corroboration.

HS-JEPA use:
calendar is never sufficient. It can be a weak interaction feature inside
human-state latent discovery.

### 9. Measurement Confidence

Story:
missingness, device carrying, watch wear, GPS/sensor sparsity, or charge
patterns may be behavior, not only noise.

Likely target route:
confidence/gate first; direct action only when paired with semantic evidence.

HS-JEPA use:
LeJEPA-style health control. A latent that only works in sparse measurement
rows may be a shortcut.

## Conversion Plan

For each story family:

1. map observable patterns to existing raw/context feature files;
2. create subject-normalized, day-type-normalized, and confidence-aware views;
3. test whether the view recovers H057 seed rows, H064 boundary rows, or H068
   healthy cells better than null;
4. use only surviving story families as HS-JEPA context;
5. materialize corrections only through action-health or row-target assignment.

## Minimal H072 Experiment

H072 should not create another direct story submission. It should produce:

- `story_family_features.parquet`;
- `story_to_h057_seed_scores.csv`;
- `story_to_h068_action_health_scores.csv`;
- `story_family_null_stress.csv`;
- one candidate only if a story family survives leave-subject, leave-block, and
  public-negative controls.

Success requires a story family to explain an already public-confirmed latent
state. A nice story with no latent recovery is not evidence.

## H072 Result

H072 was implemented as `hitl/h072_human_social_state_engine_jepa.py`.

Generated artifacts:

- `hitl/h072_human_social_state_engine_jepa/h072_story_family_features.csv`
- `hitl/h072_human_social_state_engine_jepa/h072_hypothesis_family_routes.csv`
- `hitl/h072_human_social_state_engine_jepa/h072_story_route_preferences.csv`
- `hitl/h072_human_social_state_engine_jepa/h072_story_route_diagnostics.csv`
- `hitl/h072_human_social_state_engine_jepa/h072_story_family_null_stress.csv`
- `hitl/h072_human_social_state_engine_jepa/h072_candidate_scores.csv`
- `submission_h072_humansocial_route_bae1edae_uploadsafe.csv`

The promoted file is a sensor, not a clean architecture proof:

| Item | Value |
| --- | ---: |
| Changed cells vs H057 | 704 |
| Changed rows vs H057 | 148 |
| Cells outside H069 | 613 |
| Routes outside H071 promoted set | 97 |
| Q2 changed cells | 75 |
| Public-action predicted delta vs H057 | -0.000922 |
| Responsibility-weighted delta vs H057 | -0.000935 |
| Bad-anchor positive cosine | 0.0 |

Route/family anatomy:

- route mix: `full_state:117`, `q3_s_stage:25`, `nonq2_full:3`,
  `q_subjective:2`, `s_stage:1`;
- family mix: `routine_pressure:66`, `weekend_rhythm:45`,
  `social_load:19`, `bedtime_arousal:10`, `badnight_aftereffect:8`.

### What Survived

Story families do recover action-health-like rows:

| Family | H068 row AUC |
| --- | ---: |
| bedtime_arousal | 0.719577 |
| cashflow_stress | 0.715461 |
| nocturnal_awake | 0.713110 |
| badnight_aftereffect | 0.697237 |

This supports the weaker but useful hypothesis:

```text
human story -> action-health / calibration-risk context
```

### What Failed

Story-family route support did not beat subject-preserving nulls for H071
route rediscovery:

| Metric | Real | Null mean | z | p(null >= real) |
| --- | ---: | ---: | ---: | ---: |
| mean H071-route support | 0.776796 | 0.783463 | -1.326523 | 0.903333 |
| H071-route AUC | 0.769787 | 0.777508 | -2.447290 | 0.986667 |

So the stronger route is weakened:

```text
human story -> route assignment
```

The next human-state experiment should not just add more stories. It should
make stories predict `z_action_health` or `z_shortcut` first, then let a
separate assignment decoder write row-target routes.

## H073 Result

H073 was implemented as `hitl/h073_human_action_health_bridge_jepa.py`.

Generated artifacts:

- `hitl/h073_human_action_health_bridge_jepa/h073_cell_scores.csv`
- `hitl/h073_human_action_health_bridge_jepa/h073_route_candidates.csv`
- `hitl/h073_human_action_health_bridge_jepa/h073_model_metrics.csv`
- `hitl/h073_human_action_health_bridge_jepa/h073_story_action_null_stress.csv`
- `hitl/h073_human_action_health_bridge_jepa/h073_story_action_null_summary.csv`
- `hitl/h073_human_action_health_bridge_jepa/h073_candidate_scores.csv`
- `submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv`

H073 tested the narrower claim suggested by H072:

```text
human story -> action-health / shortcut representation -> assignment
```

instead of:

```text
human story -> hard row-target assignment
```

The promoted file is again a sensor rather than the strongest public slot:

| Item | Value |
| --- | ---: |
| Changed cells vs H057 | 657 |
| Changed rows vs H057 | 141 |
| Cells outside H069 | 557 |
| Cells outside H070 | 343 |
| Q2 changed cells | 17 |
| Public-action predicted delta vs H057 | -0.000618 |
| Responsibility-weighted delta vs H057 | -0.000628 |
| Bad-anchor positive cosine | 0.0 |

### What Survived

Human-social context becomes much more useful when route context is included
and the target is continuous action-health:

| Bridge target | Subject-group OOF metric | Value |
| --- | --- | ---: |
| `story_to_h068_selected` | AUC on H068 selected cells | 0.513105 |
| `story_route_to_h068_health` | Spearman on H068 cell health | 0.890901 |
| `story_route_to_h068_health` | AUC on H071 selected cells | 0.860064 |
| `story_route_to_shortcut` | Spearman on shortcut energy | 0.801446 |

This supports the current HS-JEPA human layer:

```text
C_human + C_route -> z_human_action / z_shortcut
```

### What Still Fails

Hard selected-cell prediction does not generalize cleanly across subjects.
The story-only hard selector has subject-group OOF AUC `0.513105`, even though
the full-fit null-placement diagnostic is very strong. That means the model can
memorize story placement in the observed table, but this is not enough evidence
for a private-safe hard assignment rule.

The next human-state experiment should therefore avoid another direct
story-route selector. The useful direction is a stronger assignment solver that
uses `z_human_action` as a regularized energy term, or an anti-shortcut model
that learns which story/route combinations are public-bad.
