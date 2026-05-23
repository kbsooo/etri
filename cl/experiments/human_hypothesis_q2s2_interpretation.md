# Human-behavior hypothesis experiment — Q2/S2

No public submission was created. This is a data/feature experiment.

## Human hypotheses encoded

### Q2 — fatigue / tired-but-wired state

Assumption: Q2 is not just “today had many steps”; it is closer to how a person feels before sleep:

1. **Accumulated load**: recent 3/7/14/30-day daytime steps, distance, calories-like load.
2. **Recovery failure**: high evening/late screen, late movement, late light, HR not dropping relative to day.
3. **Tired but wired**: high day load plus late screen/light/arousal.
4. **Routine shock**: sudden deviation from personal recent baseline.

### S2 — broad sleep/routine state

Assumption: S2 is broader than one-night sleep; it reflects a multi-day routine state:

1. **Chronic rhythm lateness**: late screen/movement pattern over 14/30 days.
2. **Sleep debt proxy**: night screen/steps/light and low quiet-efficiency history.
3. **Fragmentation**: night activity/screen transitions and irregularity.
4. **Personal rhythm break**: deviation from own 30-day pattern.

## Artifacts

Feature table:

```text
features/human_hypothesis_q2s2_features_v1.parquet
```

Script:

```text
scripts/60_human_hypothesis_q2s2_features_eval.py
```

Evaluation:

```text
experiments/human_hypothesis_q2s2_eval_results.csv
experiments/human_hypothesis_q2s2_eval_summary.csv
experiments/human_hypothesis_q2s2_selected_features_sample.csv
experiments/human_hypothesis_q2s2_report.md
```

## Results, interpreted coarsely

### Q2

Human Q2 features are meaningful in interleaved/gap-like settings:

- testpattern: human Q2 features beat existing base by a large coarse margin.
- random_gap: human Q2 features also beat existing base.
- tail: human Q2 features do **not** beat existing base; existing/day-flat is roughly best.

Interpretation:

Q2 looks like a **same-person interpolation/state-completion target**, not a stable future-forecast target. The human fatigue/recovery hypothesis is useful, but it is dangerous if the private/public split is tail-like.

Selected human features repeatedly include:

- daytime steps/distance;
- late light/screen;
- `tired_but_wired` rolling variability;
- light-screen arousal rolling mean/std;
- physical load 14/30-day mean;
- evening no-recovery variability.

This is a real behavioral story, but not yet submission-grade because tail rejects it.

### S2

S2 is robustly predictable, but mostly from existing no-flat-hourly features rather than my new human composites.

- testpattern: existing no-flat-hourly / plus-human both strong.
- random_gap: existing no-flat-hourly / plus-human strong.
- tail: existing no-flat-hourly also strong.

Adding human features is not clearly better than existing features. Some configs improve slightly, some degrade. Do not over-interpret small deltas.

Interpretation:

S2 is a broad routine/rhythm target, but the current existing hourly feature set already captures most of the signal. The next useful work is not “more composites”; it is extracting a cleaner low-dimensional routine state from existing hourly patterns.

Selected S2 human features include:

- evening screen/light history;
- 7/14/30-day late rhythm means;
- sleep-debt rolling std;
- fragmentation proxy;
- chronic irregular sleep / broad bad state composites.

These are directionally plausible, but not a clear additive breakthrough.

## Decision

No submission.

What survived structurally:

1. **Q2 human fatigue/recovery features**: useful for interleaved/gap validation, tail-unsafe.
2. **S2 routine/rhythm signal**: robust, but already captured by existing no-flat-hourly features.
3. **S1/S3/Q3 should stay deprioritized for now.**

## Next experiment

The most human-plausible next step is:

### Q2 split-robust fatigue state model

Build a Q2-only model that explicitly distinguishes:

- stable subject tendency;
- recent fatigue/recovery state;
- tail-safe components only;
- interleaved-only components separately.

It should report two heads:

1. **interleaved Q2 state head** — for diagnosis only;
2. **tail-safe Q2 head** — only this can ever become submission candidate.

### S2 low-dimensional routine-state extraction

Instead of adding more hand composites, compress hourly behavior into a few interpretable axes:

- late-phone axis;
- night-movement axis;
- routine-regularity axis;
- recovery/quiet axis;
- week-level stability axis.

Then test whether these axes match or replace the existing no-flat-hourly S2 model without overfitting.
