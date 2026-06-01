# H014 Sleep-State Memory Synthesis

## Source

- external text attachment: `/Users/kbsoo/.codex/attachments/be9e4ae4-640b-43fd-8202-0d19915988af/pasted-text.txt`
- reported file: `submission_v106_sleep_state_conditioned_memory.csv`
- reported public LB: `0.5703952266`

## What The External Method Claims

The method treats the competition as repeated observations of the same subjects over time. Its strongest object is not a new tabular model; it is same-subject label memory.

The upgrade over simple date memory is:

```text
memory_weight =
  date_weight
  * sleep_state_similarity
  * sensor_quality_similarity
```

The important claim is that the useful neighbor is not simply the nearest date. It is a past day from the same subject that is close in time, similar in sleep episode state, and similar in sensor coverage/quality.

## Relation To H012

H012 is stronger publicly:

```text
H012 public LB: 0.5681234831
V106 public LB: 0.5703952266
H012 edge:     0.0022717435
```

But the external method is still valuable because it is an independent view of the hidden world. It says the labels are not independent rows. They are repeated-subject time traces with state continuity and observation-quality noise.

H012 says public scores can be inverted into a hidden public posterior. V106 says within-subject state-conditioned memory is a strong non-public structure. A private-safer HS-JEPA should make these two views agree.

## New World Model

The current strongest world model is:

```text
hidden state =
  public-equation posterior
  constrained by within-subject temporal continuity
  and moderated by sleep-state / sensor-quality reliability
```

This explains three observations together:

- H012 breaks the plateau because it directly reconstructs the hidden public label/subset state.
- V106 is strong because same-subject history is a direct label memory source.
- Raw human-state gates before H012 were weaker because they tried to translate lifestyle state into output actions without first solving the public label/subset geometry.

## H014 Experiment Sketch

Question: are H012's high-impact cells compatible with same-subject sleep-state memory?

Build memory features per test row/target:

- nearest same-subject train label by date;
- exponentially weighted same-subject label memory;
- sleep-state similarity weighted memory;
- sensor-quality similarity weighted memory;
- effective neighbor count;
- memory entropy / disagreement;
- H012 posterior agreement with memory;
- H012 posterior disagreement with memory;
- target-specific memory reliability.

Stress tests:

- leave-H012-out public-equation posterior;
- leave-one-public-anchor posterior stability;
- target-wise H012 posterior concentration;
- subject/dateblock concentration;
- memory-compatible versus memory-incompatible posterior delta;
- upload-safe variant only if memory-compatible cells keep a large share of H012 predicted gain.

## Submission Rule

Do not make a tiny "safer H012" just because it sounds safer.

Only materialize H014 if it answers a real question:

- If memory-compatible H012 cells preserve most of the posterior gain, submit a regularized H012 variant to test whether private-safe continuity beats raw public-equation materialization.
- If memory-compatible cells are low-impact, keep H012 as the frontier and treat subject-memory as a paper explanation / diagnostic rather than a submission route.
