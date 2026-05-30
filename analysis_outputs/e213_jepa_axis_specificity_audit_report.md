# E213 JEPA Axis Specificity Audit

## Purpose

Test whether the live E208/E211 JEPA axes are specific representation signals or likely latent-axis cherry-picks. This creates no submission.

## Summary

| axis_id | target | feature | delta | half_mean_delta | half_win_rate | geometry_delta_mean | geometry_win_rate | scan_exact_rank | scan_exact_percentile | global_perm_p_delta | subject_perm_p_delta | pool_rank_delta | pool_p_delta | pool_best_feature | pool_best_delta | axis_specificity_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q3_resid_self_pc10 | Q3 | e208_resid_self_pc10 | -0.00577531219031 | -0.00611290265517 | 0.95 | -0.000109448522669 | 0.625 | 3 | 0.962264150943 | 0.0204081632653 | 0.0204081632653 | 1 | 0.0625 | e208_resid_self_pc04 | -0.00219975894795 | specific |
| s4_pred_pc14 | S4 | e208_pred_pc14 | -0.00313375482778 | -0.00274253576984 | 0.733333333333 | -0.000499176975613 | 0.875 | 1 | 1 | 0.0204081632653 | 0.0204081632653 | 1 | 0.0625 | e208_pred_pc04 | 0.00137668939283 | specific |

## Null Distribution Snapshot

| axis_id | null_kind | n | delta_min | delta_p05 | delta_median | half_mean_min | half_mean_median |
| --- | --- | --- | --- | --- | --- | --- | --- |
| q3_resid_self_pc10 | global_perm | 48 | 0.000706310648046 | 0.00178412746048 | 0.00353631823232 | 0.000705826972748 | 0.00346859288625 |
| q3_resid_self_pc10 | subject_perm | 48 | 0.00135329068339 | 0.00218612665303 | 0.00350672770293 | 0.00127868854533 | 0.00345710095835 |
| s4_pred_pc14 | global_perm | 48 | 0.000874197457604 | 0.00230416004899 | 0.00429243762438 | 0.00073119004066 | 0.00429982768667 |
| s4_pred_pc14 | subject_perm | 48 | 0.00174216037629 | 0.00212125657586 | 0.00421678405419 | 0.0017563628007 | 0.00422967188955 |

## Same-Family Pool Top Rows

| axis_id | pool_feature | delta | half_mean_delta | half_win_rate |
| --- | --- | --- | --- | --- |
| q3_resid_self_pc10 | e208_resid_self_pc04 | -0.00219975894795 | -0.00239829365981 | 0.775 |
| q3_resid_self_pc10 | e208_resid_self_pc07 | 0.000466521672676 | 0.000210689404845 | 0.441666666667 |
| q3_resid_self_pc10 | e208_resid_self_pc01 | 0.00197109512116 | 0.00191930316384 | 0.108333333333 |
| q3_resid_self_pc10 | e208_resid_self_pc13 | 0.00269917702368 | 0.00265374417588 | 0 |
| q3_resid_self_pc10 | e208_resid_self_pc09 | 0.00310792789346 | 0.00305158554194 | 0 |
| q3_resid_self_pc10 | e208_resid_self_pc02 | 0.00312329759204 | 0.0030210726554 | 0 |
| q3_resid_self_pc10 | e208_resid_self_pc14 | 0.00329489607511 | 0.0032904371901 | 0 |
| q3_resid_self_pc10 | e208_resid_self_pc03 | 0.00362745833842 | 0.00356754543823 | 0 |
| q3_resid_self_pc10 | e208_resid_self_pc15 | 0.00363466468571 | 0.00367995462929 | 0 |
| q3_resid_self_pc10 | e208_resid_self_pc00 | 0.00367654462598 | 0.00356755985788 | 0 |
| q3_resid_self_pc10 | e208_resid_self_pc08 | 0.00399523434133 | 0.0039186360335 | 0 |
| q3_resid_self_pc10 | e208_resid_self_pc11 | 0.00416602468331 | 0.00423657797652 | 0 |
| q3_resid_self_pc10 | e208_resid_self_pc05 | 0.00428914760691 | 0.00424663799597 | 0 |
| q3_resid_self_pc10 | e208_resid_self_pc12 | 0.00578544401598 | 0.0058768952508 | 0.00833333333333 |
| q3_resid_self_pc10 | e208_resid_self_pc06 | 0.00629427813108 | 0.00629457158587 | 0 |
| s4_pred_pc14 | e208_pred_pc04 | 0.00137668939283 | 0.00170619710283 | 0.15 |
| s4_pred_pc14 | e208_pred_pc12 | 0.00152986426455 | 0.0011699819551 | 0.283333333333 |
| s4_pred_pc14 | e208_pred_pc09 | 0.00193011774946 | 0.00220643122172 | 0.075 |
| s4_pred_pc14 | e208_pred_pc01 | 0.0019306381708 | 0.00218825036624 | 0.108333333333 |
| s4_pred_pc14 | e208_pred_pc05 | 0.00266406575526 | 0.00263568021221 | 0.0916666666667 |
| s4_pred_pc14 | e208_pred_pc15 | 0.00352962461238 | 0.00357902367359 | 0 |
| s4_pred_pc14 | e208_pred_pc07 | 0.00377133161696 | 0.00369327559924 | 0.0166666666667 |
| s4_pred_pc14 | e208_pred_pc03 | 0.00389487739604 | 0.00394200456135 | 0 |
| s4_pred_pc14 | e208_pred_pc08 | 0.00435166512056 | 0.00419881684042 | 0 |
| s4_pred_pc14 | e208_pred_pc10 | 0.00436868097156 | 0.00418946844513 | 0 |
| s4_pred_pc14 | e208_pred_pc06 | 0.00451740698428 | 0.00467081154141 | 0 |
| s4_pred_pc14 | e208_pred_pc02 | 0.00455895940941 | 0.00466413793165 | 0 |
| s4_pred_pc14 | e208_pred_pc13 | 0.00515785155875 | 0.0050013802432 | 0 |
| s4_pred_pc14 | e208_pred_pc11 | 0.00560897723 | 0.00574756413457 | 0 |
| s4_pred_pc14 | e208_pred_pc00 | 0.00775503247413 | 0.00775280515547 | 0 |

## Decision

- `specific` means the axis beats permutation nulls, is near the top of its same-family coordinate pool, keeps subject-half support, and had nonpositive E208 geometry.
- `weak_or_underidentified` means the current axis may still be useful, but it should be treated as a fragile probability translator rather than a representation law.
