# E96 Public-Miss Budget Tail Scenarios

## Question

E72 public miss `+0.0001011367`를 하나의 LogLoss budget으로 고정했을 때, 그 budget이 가능한 E72-adverse hard-label tail 어디에서 발생했느냐에 따라 E95/E89/E90/E86의 상대 risk가 어떻게 바뀌는가?

이 실험은 public label을 맞추지 않는다. 관측값은 E72의 public miss 크기 하나뿐이고, 각 scenario는 그 miss를 설명할 수 있는 hard-tail cell 집합을 다르게 배치한다.

## Method

- base: `submission_mixmin_0c916bb4.csv`
- failed sensor: `submission_e72_topabs50_q2s3_gate_4e48cba2.csv`
- budget: `E72 - mixmin = 0.0001011367`
- evaluated cells: `1750` test-target cells (`rows x 7 targets`)
- candidates scored per scenario: `8`
- max full selected cells in a complete budget scenario: `203`
- scenarios: `3894` total, `3894` complete-budget
- deterministic orders: top, bottom, median E72-adverse hard-tail cells
- random orders: weighted permutations with gamma `0, 0.5, 1, 2`

Each candidate score is candidate-minus-mixmin LogLoss on the same selected E72-adverse hard labels. For complete scenarios, failed E72 reconstructs the observed public miss by construction.

## Candidate Summary

Sorted by p95 conditional tail delta.

| candidate | mean_delta | median_delta | p90_delta | p95_delta | max_delta | improve_vs_mixmin_rate | beat_failed_e72_rate | beat_e89_rate | beat_e90_rate | beat_e86_rate | win_rate_live |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e85 | 0.000058977 | 0.000058909 | 0.000105450 | 0.000115304 | 0.000190592 | 0.035439137 | 0.866718028 | 0.570107858 | 0.956343092 | 0.981766821 | 0.368772470 |
| e95 | 0.000057874 | 0.000058004 | 0.000106465 | 0.000115644 | 0.000190592 | 0.051874679 | 0.863893169 | 0.712378017 | 0.999486389 | 0.998972779 | 0.527478172 |
| e89 | 0.000059964 | 0.000060018 | 0.000107457 | 0.000117735 | 0.000218223 | 0.039034412 | 0.847457627 | 0.000000000 | 0.960451977 | 0.984591680 | 0.101951721 |
| e90 | 0.000069295 | 0.000069326 | 0.000120343 | 0.000129152 | 0.000225633 | 0.026194145 | 0.740112994 | 0.039548023 | 0.000000000 | 0.914483821 | 0.000000000 |
| e86 | 0.000076162 | 0.000075426 | 0.000130517 | 0.000138751 | 0.000231182 | 0.021828454 | 0.670261941 | 0.015408320 | 0.063687725 | 0.000000000 | 0.000256805 |
| noq2 | 0.000071237 | 0.000071219 | 0.000126761 | 0.000138876 | 0.000235672 | 0.034155110 | 0.717000514 | 0.030303030 | 0.389060092 | 0.642783770 | 0.001540832 |

## Mask / Family Summary

Lowest E95 rank families first.

| mask_name | family | complete_scenarios | winner_mode | e95_win_rate | e95_rank_mean | e95_minus_e89_mean | e95_minus_e90_mean | e95_minus_e86_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s2 | deterministic | 3 | e95 | 1.000000000 | 1.000000000 | -0.000012434 | -0.000009361 | -0.000009394 |
| e95_fallback_s1s2s3 | deterministic | 3 | e85 | 0.333333333 | 1.000000000 | -0.000011745 | -0.000020725 | -0.000025464 |
| e95_fallback_cells | deterministic | 3 | e85 | 0.333333333 | 1.000000000 | -0.000011488 | -0.000020288 | -0.000026935 |
| e90_moved_vs_mixmin | deterministic | 3 | e95 | 0.666666667 | 1.000000000 | -0.000005979 | -0.000009791 | -0.000012954 |
| e86_moved_vs_mixmin | deterministic | 3 | e95 | 0.666666667 | 1.000000000 | -0.000005764 | -0.000008618 | -0.000014037 |
| live_q2s1s2s3 | deterministic | 3 | e95 | 0.666666667 | 1.000000000 | -0.000005764 | -0.000008618 | -0.000014037 |
| e95_moved_vs_mixmin | deterministic | 3 | e95 | 0.666666667 | 1.000000000 | -0.000005038 | -0.000008591 | -0.000011754 |
| e89_moved_vs_mixmin | deterministic | 3 | e95 | 0.666666667 | 1.000000000 | -0.000004655 | -0.000008143 | -0.000011392 |
| s1s2s3 | deterministic | 3 | e95 | 0.666666667 | 1.000000000 | -0.000004655 | -0.000008143 | -0.000011392 |
| e95_fallback_cells | random_weighted | 480 | e85 | 0.072916667 | 1.000000000 | -0.000004383 | -0.000018927 | -0.000030657 |
| all | deterministic | 3 | e95 | 0.666666667 | 1.000000000 | -0.000002245 | -0.000005005 | -0.000009092 |
| e95_fallback_q2s3 | deterministic | 3 | e85 | 0.000000000 | 1.000000000 | 0.000000000 | -0.000016762 | -0.000033392 |
| s1s2s3 | random_weighted | 480 | e95 | 0.954166667 | 1.052083333 | -0.000005389 | -0.000008631 | -0.000010576 |
| e95_moved_vs_mixmin | random_weighted | 480 | e95 | 0.729166667 | 1.408333333 | -0.000003089 | -0.000008321 | -0.000010412 |
| e86_moved_vs_mixmin | random_weighted | 480 | e95 | 0.666666667 | 1.466666667 | -0.000002433 | -0.000012711 | -0.000020045 |
| live_q2s1s2s3 | random_weighted | 480 | e95 | 0.668750000 | 1.508333333 | -0.000002468 | -0.000012098 | -0.000019893 |
| e72_top50_hard | random_weighted | 480 | e95 | 0.593750000 | 1.608333333 | -0.000001579 | -0.000008374 | -0.000013406 |
| s1 | deterministic | 3 | e85 | 0.333333333 | 1.666666667 | -0.000005142 | -0.000009356 | -0.000011597 |

## Where E95 Loses Most To E89

| scenario_id | family | mask_name | order_name | gamma | selected_fractional_cells | e95 | e89 | e90 | e86 | e95_minus_e89 | e95_minus_e90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| d0017 | deterministic | q2s3 | bottom |  | 32.142053736 | 0.000111401 | 0.000082971 | 0.000114456 | 0.000117001 | 0.000028431 | -0.000003054 |
| d0005 | deterministic | q2 | bottom |  | 21.087254698 | 0.000027179 | -0.000000000 | 0.000037058 | 0.000059466 | 0.000027179 | -0.000009879 |
| r0626 | random_weighted | q2s3 | weighted_gamma_0_rep_091 | 0.000000000 | 21.733302876 | 0.000060220 | 0.000043540 | 0.000074931 | 0.000089606 | 0.000016680 | -0.000014711 |
| r0590 | random_weighted | q2s3 | weighted_gamma_0_rep_055 | 0.000000000 | 21.171518299 | 0.000081245 | 0.000065355 | 0.000088500 | 0.000104674 | 0.000015890 | -0.000007255 |
| r0578 | random_weighted | q2s3 | weighted_gamma_0_rep_043 | 0.000000000 | 16.369663745 | 0.000077655 | 0.000064099 | 0.000096235 | 0.000103828 | 0.000013556 | -0.000018580 |
| r0649 | random_weighted | q2s3 | weighted_gamma_0_rep_114 | 0.000000000 | 18.497287619 | 0.000073212 | 0.000059773 | 0.000089933 | 0.000100870 | 0.000013438 | -0.000016721 |
| r0570 | random_weighted | q2s3 | weighted_gamma_0_rep_035 | 0.000000000 | 16.871886604 | 0.000072746 | 0.000059397 | 0.000087614 | 0.000100539 | 0.000013349 | -0.000014868 |
| r0644 | random_weighted | q2s3 | weighted_gamma_0_rep_109 | 0.000000000 | 19.226367566 | 0.000055662 | 0.000042815 | 0.000072396 | 0.000089036 | 0.000012847 | -0.000016734 |
| r0732 | random_weighted | q2s3 | weighted_gamma_0.5_rep_077 | 0.500000000 | 12.940662316 | 0.000102028 | 0.000089204 | 0.000113982 | 0.000121105 | 0.000012824 | -0.000011954 |
| r0610 | random_weighted | q2s3 | weighted_gamma_0_rep_075 | 0.000000000 | 20.545289403 | 0.000083725 | 0.000070967 | 0.000091682 | 0.000108626 | 0.000012758 | -0.000007957 |
| r0678 | random_weighted | q2s3 | weighted_gamma_0.5_rep_023 | 0.500000000 | 14.312832628 | 0.000066180 | 0.000053539 | 0.000076048 | 0.000096441 | 0.000012641 | -0.000009868 |
| r0705 | random_weighted | q2s3 | weighted_gamma_0.5_rep_050 | 0.500000000 | 16.114834925 | 0.000102122 | 0.000089631 | 0.000118200 | 0.000121408 | 0.000012491 | -0.000016078 |

## Interpretation

- E95는 E89보다 평균과 p95 tail-risk가 낮다. hard-tail fallback이 E89의 단순 E72-cell fallback보다 넓은 조건부 세계에서 더 낫다는 쪽이다.
- E95는 E86의 tail-risk를 줄이지만 평균 구조 edge도 일부 포기한다. 이는 E95의 제출 의도가 upside가 아니라 downside 센서임을 재확인한다.
- E90 remains the row-coherent middle hypothesis: summary mean `0.000069295`, p95 `0.000129152`.
- E89 remains the direct E72-cell fallback baseline: summary mean `0.000059964`, p95 `0.000117735`.

## Decision

E96 does not create a new submission file. It is a conditional sensor audit for the post-E72 queue.

Submission reading:

- If the next public slot should minimize E72-style hard-tail downside, prefer whichever of E95/E89 has the lower p95 and mean in this report.
- If the next public slot should test whether hard-tail gating is over-penalizing useful structure, E86 is still the maximum-upside contrast.
- If public later rejects E95 but accepts E90/E86, H90 weakens: the hard-tail proxy was over-localized or public tail was not E72-adverse.
- If public accepts E95 while rejecting E86/E90, H90 strengthens: public loss is dominated by localized E72-adverse hard-tail cells rather than broad soft representation health.

## Post-E97 Public Update

E95 was submitted after this stress and scored public `0.5762913298`, improving over mixmin by `0.0000153107`. That validates the E95 side of the E96 ranking as public-positive, while the small gain means this is still a localized hard-tail repair rather than hidden block-rate recovery.
