# v82 Public LB failure diagnosis

New ground truth: **v82 = 0.6629, worse than the global-mean baseline 0.6619.** The v80/v81 latent-decoder branch is quarantined. Public LB is treated as stronger evidence than local OOF.

## Public LB results (lower is better)

| submission | public_lb |
| --- | --- |
| v76_anchor_0.5999 | 0.5999627447 |
| v18_0.6058 | 0.6057860899 |
| sample_supp_0.6104 | 0.6104310794 |
| global_mean_baseline | 0.6619461447 |
| v82_FAILED_0.6629 | 0.6629409456 |

## 1. Per-target distribution (mean / std / min / max)

Means:
| file | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v76_anchor_0.5999 | 0.511 | 0.570 | 0.614 | 0.687 | 0.650 | 0.663 | 0.554 |
| v18_0.6058 | 0.504 | 0.565 | 0.633 | 0.700 | 0.645 | 0.691 | 0.549 |
| sample_supp_0.6104 | 0.500 | 0.546 | 0.598 | 0.694 | 0.611 | 0.676 | 0.551 |
| v80_base | 0.517 | 0.572 | 0.614 | 0.642 | 0.630 | 0.614 | 0.558 |
| v81_routed | 0.558 | 0.577 | 0.611 | 0.648 | 0.656 | 0.622 | 0.554 |
| v82_FAILED_0.6629 | 0.558 | 0.572 | 0.614 | 0.642 | 0.630 | 0.622 | 0.558 |

Stds:
| file | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v76_anchor_0.5999 | 0.144 | 0.135 | 0.124 | 0.147 | 0.177 | 0.182 | 0.158 |
| v18_0.6058 | 0.154 | 0.138 | 0.186 | 0.149 | 0.226 | 0.230 | 0.189 |
| sample_supp_0.6104 | 0.157 | 0.080 | 0.112 | 0.150 | 0.212 | 0.220 | 0.179 |
| v80_base | 0.146 | 0.173 | 0.223 | 0.194 | 0.210 | 0.218 | 0.183 |
| v81_routed | 0.148 | 0.176 | 0.225 | 0.203 | 0.212 | 0.225 | 0.188 |
| v82_FAILED_0.6629 | 0.148 | 0.173 | 0.223 | 0.194 | 0.210 | 0.225 | 0.183 |

## 2. Mean absolute drift vs known-good anchors

How far each suspect submission sits from each public anchor (mean |Δp| per target, and overall).

### vs v76_anchor_0.5999
| suspect | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | overall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v80_base | 0.1194 | 0.1455 | 0.1572 | 0.1138 | 0.1088 | 0.1137 | 0.1339 | 0.1275 |
| v81_routed | 0.1248 | 0.1450 | 0.1587 | 0.1181 | 0.1164 | 0.1149 | 0.1380 | 0.1308 |
| v82_FAILED_0.6629 | 0.1248 | 0.1455 | 0.1572 | 0.1138 | 0.1088 | 0.1149 | 0.1339 | 0.1284 |

### vs v18_0.6058
| suspect | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | overall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v80_base | 0.1106 | 0.1049 | 0.1218 | 0.1145 | 0.0868 | 0.1110 | 0.1277 | 0.1110 |
| v81_routed | 0.1149 | 0.1058 | 0.1233 | 0.1158 | 0.0944 | 0.1056 | 0.1261 | 0.1123 |
| v82_FAILED_0.6629 | 0.1149 | 0.1049 | 0.1218 | 0.1145 | 0.0868 | 0.1056 | 0.1277 | 0.1109 |

### vs sample_supp_0.6104
| suspect | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | overall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v80_base | 0.1160 | 0.1271 | 0.1494 | 0.1140 | 0.1223 | 0.1153 | 0.1364 | 0.1258 |
| v81_routed | 0.1204 | 0.1307 | 0.1508 | 0.1157 | 0.1342 | 0.1144 | 0.1379 | 0.1291 |
| v82_FAILED_0.6629 | 0.1204 | 0.1271 | 0.1494 | 0.1140 | 0.1223 | 0.1144 | 0.1364 | 0.1263 |

### Critical: v80 base vs v76 BEFORE the v82 Q1/S3 edit

| target | v80_base mean_shift vs v76 | v80 mean_abs vs v76 | v82 mean_shift vs v76 | v82 mean_abs vs v76 |
| --- | --- | --- | --- | --- |
| Q1 | +0.0069 | 0.1194 | +0.0471 | 0.1248 |
| Q2 | +0.0020 | 0.1455 | +0.0020 | 0.1455 |
| Q3 | -0.0000 | 0.1572 | -0.0000 | 0.1572 |
| S1 | -0.0454 | 0.1138 | -0.0454 | 0.1138 |
| S2 | -0.0200 | 0.1088 | -0.0200 | 0.1088 |
| S3 | -0.0488 | 0.1137 | -0.0404 | 0.1149 |
| S4 | +0.0040 | 0.1339 | +0.0040 | 0.1339 |

- v80 base overall mean-abs drift vs v76: **0.1275**
- v82 overall mean-abs drift vs v76: **0.1284**
- Interpretation: if v80 base is already far from v76 on S1/S3, the v82 failure is not only the Q1 edit — the whole v80 base is public-misaligned.

## 3. Row-wise max drift (v82 vs v76)

- mean row-max |Δ|: 0.2819; p90: 0.3964; max: 0.5995
| subject | sleep_date | row_max_drift |
| --- | --- | --- |
| id05 | 2024-11-13 | 0.5995 |
| id02 | 2024-10-10 | 0.5522 |
| id09 | 2024-09-13 | 0.5421 |
| id10 | 2024-09-26 | 0.5018 |
| id04 | 2024-10-15 | 0.4894 |
| id06 | 2024-08-10 | 0.4713 |
| id08 | 2024-09-11 | 0.4657 |
| id01 | 2024-08-13 | 0.4640 |

## 4. Subject-wise mean drift (v82 vs v76)

| subject | mean_drift | Q1 mean_shift | rows |
| --- | --- | --- | --- |
| id08 | 0.1537 | +0.0858 | 19 |
| id03 | 0.1518 | -0.1004 | 21 |
| id05 | 0.1412 | -0.0328 | 21 |
| id01 | 0.1380 | -0.0446 | 27 |
| id09 | 0.1324 | +0.0166 | 27 |
| id04 | 0.1248 | +0.0933 | 27 |
| id06 | 0.1176 | +0.1932 | 24 |
| id07 | 0.1170 | +0.0874 | 30 |
| id02 | 0.1145 | +0.0893 | 32 |
| id10 | 0.1072 | +0.0487 | 22 |

## 5. Panel-position drift (v82 vs v76)

| panel | rows | mean_abs_drift | Q1 shift | S3 shift |
| --- | --- | --- | --- | --- |
| early | 83 | 0.1276 | +0.0742 | -0.0809 |
| mid | 82 | 0.1232 | +0.0100 | -0.0158 |
| late | 85 | 0.1342 | +0.0565 | -0.0244 |

## 6. Does the v82 edit (Q1/S3 only) explain the damage, or is v80 the problem?

- v82 differs from v80 base ONLY on Q1 (mean_abs 0.0443) and S3 (mean_abs 0.0142); other targets identical.
- But v80 base itself drifts from v76 by mean_abs 0.1275 overall, with S1 0.1138, S3 0.1137, Q1 0.1194.
- Conclusion: both effects are real. The Q1 upshift is the proximate trigger, but the v80 base is the deeper misalignment.

## 7. Ranked component harm (most → least likely Public LB harm)

| component | evidence | harm |
| --- | --- | --- |
| Q1 upward mean shift | v82 Q1 mean 0.558 vs v76 0.511 (+0.047); Q1 is per-subject-relative (~0.5), so a systematic upshift inflates log loss directly. | HIGH |
| v80 base S1/S3 under-prediction | v80 S1 0.642 vs v76 0.687 (-0.045); S3 0.614 vs v76 0.663 (-0.049). The base is structurally below the good family on sleep targets. | HIGH |
| conditional router selected on full OOF | router move selection is optimistic on OOF and does not transfer; it pushed targets toward OOF-fit directions unrelated to public alignment. | HIGH |
| late-behavior residual + v81 HGB residual magnitude | the residual decoder amplified Q1/S3 moves that the stress test already showed were mostly selection bias on Q3/S1/S4. | MEDIUM |
| S3 upward shift in v82 | small (+0.008) and in the direction of the good family (v76 S3 0.66), so likely low harm or mildly helpful. | LOW |
| panel_position bins / test-time subject-date extrapolation | bins are derived from observed panels and the same 10 subjects appear in train/test, so extrapolation risk is structural but not the proximate cause. | LOW |
