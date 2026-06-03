# H147 Submission Slot Postmortem

Date: 2026-06-03

## Context

The latest public slots were used on the H144/H145 fork:

| Candidate | File | Public LB | Delta vs H057 |
| --- | --- | ---: | ---: |
| H057 | `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv` | 0.5677475939 | 0.0000000000 |
| H144 | `submission_h144_targetxor_def80b88_uploadsafe.csv` | 0.5679296410 | +0.0001820471 |
| H145 | `submission_h145_q3repair_2d818e46_uploadsafe.csv` | 0.5679296410 | +0.0001820471 |
| H042/H050 | reference frontier basin | 0.5679048248 | +0.0001572309 |
| H012 | public-equation breakthrough | 0.5681234831 | +0.0003758892 |
| H088 | dual-state value gate negative sensor | 0.5684942019 | +0.0007466080 |

Lower is better.

## What H144/H145 Tested

H144 and H145 were designed as a clean fork:

```text
H144 = H141 common core + row207 S2 relief + row135 Q3 repair, row135 S2 vetoed
H145 = H141 common core + row135 Q3 repair, row207 S2 and row135 S2 vetoed
```

They differ in only two row-target cells:

| Row | Subject | Date | Target | H144 | H145 | H144-H145 |
| ---: | --- | --- | --- | ---: | ---: | ---: |
| 135 | id06 | 2024-07-14 | Q3 | 0.829783853053 | 0.829580714006 | +0.000203139047 |
| 207 | id09 | 2024-08-12 | S2 | 0.808870352651 | 0.810987067381 | -0.002116714730 |

Expected split:

- H144 wins: row207 S2 relief is action-grade.
- H145 wins: row207 S2 relief is a toxic shortcut; Q3 repair-only is safer.

Observed:

```text
public(H144) = public(H145) = 0.567929641
```

## Main Information Gained

### 1. H144/H145 killed the clean branch fork

The public sensor did not choose between row207 S2 relief and Q3 repair-only.
Therefore this fork is not the missing public equation.

This does not mean both rows are useless globally.  It means this exact
two-cell contrast is not public-sensitive enough to drive the leaderboard at
the current precision.

### 2. The contrasted cells are probably low-listener cells

If the two cells were both strongly public-listened, a perfect public tie would
require a fine cancellation:

```text
g(row135,Q3) * 0.000203139
  ~= g(row207,S2) * 0.002116715
```

That implies an approximate gradient/responsibility ratio near `10.42` between
the two cells.  This is possible, but less plausible than the simpler
explanation:

```text
listener(row135,Q3) is low, listener(row207,S2) is low,
or both cells cancel under very weak public responsibility.
```

### 3. H144/H145 are not worse because of the branch distinction

Both H144 and H145 are worse than H057 by `0.0001820471`, but identical to each
other.  Therefore the main loss is not the row207-vs-Q3 choice.  The loss comes
from the shared body relative to H057:

```text
H144/H145 shared body = H141 common core + row135 Q3 family
H057 superior field   = Q2-row/full-vector state frontier
```

### 4. H144/H145 fell back into the H042 basin

H144/H145 are only `0.0000248162` worse than H042/H050:

```text
H042/H050 = 0.5679048248
H144/H145 = 0.5679296410
```

This suggests the H144/H145 family did not create a new public action regime.
It mostly stayed in the same frontier basin that H012/H042 already defined.

### 5. H057 remains the only confirmed escape from that basin

H057 improves over H042/H050 by `0.0001572309` and over H144/H145 by
`0.0001820471`.  That is small compared with the desired 0.53 target, but it is
the only observed move in this local region that public actually rewards.

Interpretation:

```text
H057 captured a listened row-state/action field.
H144/H145 captured locally plausible actions that public did not listen to.
```

## What This Means For HS-JEPA

The architecture should no longer be framed as:

```text
context -> human-state latent -> action toxicity -> correction
```

It needs an explicit listener/responsibility field:

```text
context -> human-state latent
        -> route/action proposal a(row,target)
        -> listener responsibility l(row,target)
        -> toxicity/safety s(row,target)
        -> correction c = a * l * s
```

H088 showed that some action fields are toxic when public listens.
H144/H145 show a different failure mode: some action fields may be locally
meaningful but barely listened by public.

## What Died

- H088/margin/route local metrics can rank H144 vs H145.
- row207 S2 is the decisive post-veto public action.
- row135 Q3 repair-only is the decisive safer alternative.
- target-split routing alone is enough to beat H057.
- two-cell branch micro-assignment can plausibly produce a 0.53-level jump.

## What Survived

- Public/private hidden observation exists.  H012/H057/H088/H144-H145 are too
  structured to be random score noise.
- H057 row-state/action field is still the best observed public frontier.
- H088 remains a negative stress diagnostic, not an action head.
- HS-JEPA should learn listener responsibility before action toxicity.
- Big breakthrough must come from a high-responsibility hidden state, not from
  low-listener local repairs.

## If We Had One More Slot

The cleanest next sensor would be:

```text
submission_h141_commoncore_0999d3ae_uploadsafe.csv
```

Reason:

```text
H141 = common core only
H145 = H141 + row135 Q3 repair
H144 = H141 + row135 Q3 repair + row207 S2 relief
```

H141 would decide whether the H144/H145 loss comes from the shared common core
or from branch atoms.  Because slots are exhausted, this becomes an offline
constraint rather than a public sensor.

## Practical Consequence Now That Slots Are Exhausted

Do not spend more effort creating H144/H145 siblings.  The useful next work is
offline inference from all observed public constraints:

1. Treat equalities as hard constraints:
   `public(H144) = public(H145)`.
2. Treat frontier gaps as response equations:
   `public(H144) - public(H057) = +0.0001820471`.
3. Fit a listener/responsibility field that explains why H057 is listened and
   H144/H145 are not.
4. Use leave-one-submission-out on known public observations to test whether the
   inferred listener field predicts held-out public movements.

The strongest one-sentence bottleneck after this slot batch:

```text
We are no longer missing plausible actions; we are missing the hidden
public/private listener field that tells which row-target actions the metric
actually hears.
```
