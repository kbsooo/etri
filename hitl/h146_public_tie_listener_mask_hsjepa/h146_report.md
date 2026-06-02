# H146 Public-Tie Listener Mask Diagnostic

Date: 2026-06-03

## Sensor Observation

`submission_h144_targetxor_def80b88_uploadsafe.csv` public LB:
`0.567929641`

`submission_h145_q3repair_2d818e46_uploadsafe.csv` public LB:
`0.567929641`

Both are worse than H057 by `0.0001820471`.

## H144 vs H145 Cell Difference

| comparison | left | right | row | subject_id | sleep_date | lifelog_date | target | p_left | p_right | diff_left_minus_right | absdiff |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h144_minus_h145 | h144 | h145 | 135 | id06 | 2024-07-14 | 2024-07-13 | Q3 | 0.829783853053 | 0.829580714006 | 0.000203139046525 | 0.000203139046525 |
| h144_minus_h145 | h144 | h145 | 207 | id09 | 2024-08-12 | 2024-08-11 | S2 | 0.808870352651 | 0.810987067381 | -0.00211671472971 | 0.00211671472971 |

## Pairwise Summary

| comparison | changed_cells | changed_rows | targets | l1_absdiff | max_absdiff | public_left | public_right | public_delta_left_minus_right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h144_minus_h145 | 2 | 2 | Q3,S2 | 0.00231985377623 | 0.00211671472971 | 0.567929641 | 0.567929641 | 0 |
| h145_minus_h141 | 1 | 1 | Q3 | 0.0015524825942 | 0.0015524825942 | 0.567929641 | nan | nan |
| h144_minus_h139 | 1 | 1 | Q3 | 0.00134934354767 | 0.00134934354767 | 0.567929641 | nan | nan |
| h145_minus_h057 | 27 | 22 | S2,S1,Q1,Q3,S4 | 0.151478377983 | 0.0370614656525 | 0.567929641 | 0.5677475939 | 0.0001820471 |
| h144_minus_h057 | 28 | 23 | S2,S1,Q1,Q3,S4 | 0.15379823176 | 0.0370614656525 | 0.567929641 | 0.5677475939 | 0.0001820471 |
| h141_minus_h057 | 27 | 22 | S2,S1,Q1,Q3,S4 | 0.153030860577 | 0.0370614656525 | nan | 0.5677475939 | nan |

## Interpretation

| finding | evidence | interpretation | hs_jepa_update |
| --- | --- | --- | --- |
| H144/H145 public tie | displayed public LB equal=True; delta=0.000000000000 | The public sensor did not distinguish the two-cell difference between H144 and H145 at displayed precision. | Add public-listener responsibility before action-grade decoding. |
| Two-cell branch contrast | H144-H145 changed_cells=2, rows=[135, 207], targets=['Q3', 'S2'] | row207 S2 and the row135 Q3 amplitude distinction are probably non-listened, low-responsibility, or label-cancelling public cells. | Do not trust local route/H088/margin metrics without listener masking. |
| Shared body is below frontier | H144/H145 worse than H057 by 0.0001820471 | The common H141-plus-repair body is public-misaligned relative to the H057 frontier; the row207-vs-Q3 fork is not the main loss source. | Separate public-listener mask from action-toxicity field. |

## What This Kills

- H144 vs H145 was expected to let public choose between row207 S2 relief and
  Q3 repair-only.  It did not.
- Local route/H088/margin gains are not sufficient to rank these two actions.
- Row-target assignment without a public-listener/responsibility head is
  under-specified.

## What Survives

- H057 remains the best public action frontier.
- H141/H144/H145 still matter as structural probes, but not as frontier
  submissions until the listener mask is learned.
- The next HS-JEPA decoder should predict two fields:

```text
listener(row,target)  = how much public/private sensor listens to this cell
toxicity(row,target)  = whether the proposed action is punished when listened
safe_action = action * listener * (1 - toxicity)
```

## Next High-Information Public Sensor

Submit H141 common core if not already observed publicly:

```text
H141 = common core only
H145 = H141 + row135 Q3 repair
H144 = H141 + row135 Q3 repair + row207 S2 relief
```

Public readings:

- H141 near H144/H145: the common core/body is the public-misaligned part.
- H141 better than H144/H145: row135 Q3/row207 branch cells are toxic or
  non-listened noise.
- H141 worse than H144/H145: the branch cells help, but H057's broader state
  field is still superior.
