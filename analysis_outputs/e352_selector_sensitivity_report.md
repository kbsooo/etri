# E352 Selector Sensitivity Audit

## Question

Did E351 win because of one hand-picked maximin selector, or is it the stable representative of the E350 compact lifestyle-state basin?

## Method

- Input: E351-ranked E350 plateau only; no public LB tuning.
- Random selector worlds: `2500` generated, `1118` non-empty.
- Perturbed gates: p90 gain, public-analog risk delta, bad-axis margin, Q1 specificity delta, support, distance from E349, micro-scale size, and hard public-bad positive cosine veto.
- Perturbed scores: Dirichlet weights over p90/risk/bad-margin/Q1-specificity/support/E349-compatibility/micro-scale plus a random worst-axis penalty and tiny S3-tail preference.
- Fixed stress profiles: balanced, public_skeptic, p90_hungry, state_specific, e349_conservative, and s3_tail_tolerant.

## Decision

- stability verdict: `stable`
- selector-sensitivity winner: `compact_t75_s1.005_s3a0.25`
- E351 robust top1/top3 rate: `0.224508` / `0.277281`
- E350 rank winner top1/top3 rate: `0.000000` / `0.004472`

## Top Selector-Stable Candidates

| selection_rank | variant | profile_role | top1_count | top3_count | top1_rate | top3_rate | p90_gain_vs_e349 | public_analog_risk_score | risk_delta_vs_e349 | bad_axis_margin | q1_specificity_margin | plateau_support_score | prob_l1_delta_vs_e349 | scale_abs_delta | e351_compat_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | compact_t75_s1.005_s3a0.25 | e351_robust | 251 | 310 | 0.224508050 | 0.277280859 | 0.000000156 | 0.044765398 | 0.000029189 | 0.000258764 | 0.324250876 | 35 | 0.006241299 | 0.005000000 | True |
| 2 | compact_t45_s1.005_s3a0.50 |  | 151 | 267 | 0.135062612 | 0.238819320 | 0.000000148 | 0.044735746 | -0.000000463 | 0.000261282 | 0.318473759 | 36 | 0.008591893 | 0.005000000 | True |
| 3 | compact_t40_s1.000_s3a0.50 |  | 141 | 198 | 0.126118068 | 0.177101968 | 0.000000082 | 0.044773183 | 0.000036974 | 0.000331318 | 0.324786991 | 34 | 0.004319603 | 0.000000000 | True |
| 4 | compact_t45_s1.000_s3a1.00 |  | 128 | 225 | 0.114490161 | 0.201252236 | 0.000000072 | 0.044771126 | 0.000034917 | 0.000330437 | 0.315325243 | 37 | 0.007026847 | 0.000000000 | True |
| 5 | compact_t45_s1.000_s3a0.75 |  | 78 | 191 | 0.069767442 | 0.170840787 | 0.000000047 | 0.044753597 | 0.000017388 | 0.000332512 | 0.313808915 | 37 | 0.005603150 | 0.000000000 | False |
| 6 | compact_t45_s1.005_s3a0.75 |  | 57 | 152 | 0.050983900 | 0.135957066 | 0.000000173 | 0.044753335 | 0.000017126 | 0.000259206 | 0.320544323 | 37 | 0.010015609 | 0.005000000 | False |
| 7 | compact_t35_s1.000_s3a0.50 |  | 52 | 115 | 0.046511628 | 0.102862254 | 0.000000106 | 0.044767880 | 0.000031671 | 0.000320051 | 0.336750292 | 31 | 0.004829853 | 0.000000000 | True |
| 8 | compact_t55_s1.000_s3a1.00 |  | 36 | 153 | 0.032200358 | 0.136851521 | 0.000000060 | 0.044763515 | 0.000027306 | 0.000324147 | 0.321088977 | 35 | 0.006342755 | 0.000000000 | True |
| 9 | compact_t40_s1.005_s3a0.50 | e351_p90 | 31 | 46 | 0.027728086 | 0.041144902 | 0.000000208 | 0.044772875 | 0.000036666 | 0.000257999 | 0.320011037 | 34 | 0.008730182 | 0.005000000 | True |
| 10 | compact_t50_s1.005_s3a0.50 |  | 28 | 98 | 0.025044723 | 0.087656530 | 0.000000125 | 0.044711549 | -0.000024660 | 0.000260941 | 0.327019248 | 35 | 0.008193396 | 0.005000000 | True |
| 11 | compact_t85_s1.005_s3a0.00 |  | 25 | 59 | 0.022361360 | 0.052772809 | 0.000000139 | 0.044751419 | 0.000015210 | 0.000260609 | 0.329736360 | 32 | 0.004772012 | 0.005000000 | True |
| 12 | compact_t60_s1.005_s3a0.50 |  | 20 | 87 | 0.017889088 | 0.077817531 | 0.000000163 | 0.044771920 | 0.000035711 | 0.000255591 | 0.327722638 | 35 | 0.007627800 | 0.005000000 | True |
| 13 | compact_t60_s1.005_s3a0.25 |  | 18 | 140 | 0.016100179 | 0.125223614 | 0.000000145 | 0.044756674 | 0.000020465 | 0.000257203 | 0.320131726 | 35 | 0.006085180 | 0.005000000 | True |
| 14 | compact_t45_s1.005_s3a0.00 |  | 15 | 36 | 0.013416816 | 0.032200358 | 0.000000100 | 0.044700134 | -0.000036075 | 0.000265433 | 0.321157466 | 34 | 0.005744402 | 0.005000000 | True |
| 15 | compact_t45_s1.005_s3a0.25 |  | 12 | 25 | 0.010733453 | 0.022361360 | 0.000000124 | 0.044718012 | -0.000018196 | 0.000263357 | 0.313901444 | 35 | 0.007168157 | 0.005000000 | True |
| 16 | compact_t75_s1.000_s3a0.50 |  | 11 | 39 | 0.009838998 | 0.034883721 | 0.000000049 | 0.044783673 | 0.000047464 | 0.000330801 | 0.333178502 | 35 | 0.003440801 | 0.000000000 | False |
| 17 | compact_t55_s1.005_s3a0.50 |  | 10 | 84 | 0.008944544 | 0.075134168 | 0.000000147 | 0.044734536 | -0.000001673 | 0.000254455 | 0.316132359 | 35 | 0.007771699 | 0.005000000 | True |
| 18 | compact_t35_s1.005_s3a0.25 |  | 10 | 33 | 0.008944544 | 0.029516995 | 0.000000183 | 0.044725105 | -0.000011103 | 0.000250818 | 0.338330916 | 30 | 0.008033577 | 0.005000000 | True |
| 19 | compact_t50_s1.000_s3a0.75 |  | 8 | 33 | 0.007155635 | 0.029516995 | 0.000000018 | 0.044724130 | -0.000012079 | 0.000332534 | 0.324946044 | 35 | 0.005247449 | 0.000000000 | False |
| 20 | compact_t75_s1.005_s3a0.50 |  | 8 | 28 | 0.007155635 | 0.025044723 | 0.000000174 | 0.044783493 | 0.000047284 | 0.000257468 | 0.328721937 | 35 | 0.007860927 | 0.005000000 | True |
| 21 | compact_t70_s1.005_s3a0.25 |  | 4 | 143 | 0.003577818 | 0.127906977 | 0.000000153 | 0.044763418 | 0.000027209 | 0.000258381 | 0.315186743 | 35 | 0.006140106 | 0.005000000 | True |
| 22 | compact_t35_s1.000_s3a0.25 | e351_e349_nearest | 4 | 20 | 0.003577818 | 0.017889088 | 0.000000058 | 0.044725317 | -0.000010891 | 0.000324177 | 0.319787471 | 30 | 0.003626575 | 0.000000000 | True |
| 23 | compact_t35_s1.005_s3a0.50 |  | 4 | 12 | 0.003577818 | 0.010733453 | 0.000000231 | 0.044767457 | 0.000031248 | 0.000246693 | 0.311575910 | 31 | 0.009236854 | 0.005000000 | False |
| 24 | compact_t45_s1.000_s3a0.50 |  | 3 | 42 | 0.002683363 | 0.037567084 | 0.000000023 | 0.044735922 | -0.000000286 | 0.000334588 | 0.311148508 | 36 | 0.004179435 | 0.000000000 | False |
| 25 | compact_t75_s1.000_s3a0.25 |  | 3 | 19 | 0.002683363 | 0.016994633 | 0.000000031 | 0.044765489 | 0.000029280 | 0.000332097 | 0.332974384 | 35 | 0.001821173 | 0.000000000 | False |

## Scenario Profile Winners

| scenario | count | winner | winner_count | mean_pool_size |
| --- | --- | --- | --- | --- |
| balanced | 1 | compact_t75_s1.005_s3a0.25 | 1 | 36.000000 |
| e349_conservative | 1 | compact_t75_s1.005_s3a0.25 | 1 | 36.000000 |
| p90_hungry | 1 | compact_t45_s1.005_s3a0.50 | 1 | 36.000000 |
| public_skeptic | 1 | compact_t75_s1.005_s3a0.25 | 1 | 29.000000 |
| random | 1112 | compact_t75_s1.005_s3a0.25 | 246 | 9.197842 |
| s3_tail_tolerant | 1 | compact_t75_s1.005_s3a0.25 | 1 | 40.000000 |
| state_specific | 1 | compact_t75_s1.005_s3a0.25 | 1 | 12.000000 |

## Interpretation

E351 remains the most stable representative after selector perturbation.
The useful hidden lifestyle-state basin is not centered on the original E350 rank winner; the robust center is the high-threshold, small-S3-tail candidate.
This supports the current practical ordering: submit E351 before E350 if public slots are scarce. E350 remains the more aggressive sensor if we specifically want to test full S3-tail restoration.

## Files

- `analysis_outputs/e352_selector_sensitivity_scenarios.csv`
- `analysis_outputs/e352_selector_sensitivity_summary.csv`
- `analysis_outputs/e352_selector_sensitivity_report.md`
