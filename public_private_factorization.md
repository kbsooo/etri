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
| Private-safe state | Needed for 0.53 | Not solved |

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
