# E88 Frontier Movement Attribution

## Observe

E86/E87 are locally healthy, but public feedback is pending. The unresolved question is whether these moves are aligned with the validated mixmin hidden-world movement or whether they resemble the failed E72 all-target contamination.

## Candidate Movement Table

| candidate | active_cells | active_rows | mean_abs_logit_move | high_mixmin_cell_mass_frac | high_e72_failed_cell_mass_frac | e72_failed_contamination_index | mixmin_reversal_index | weighted_cell_corr_with_mixmin_move | weighted_cell_corr_with_e72_failed_move | ce_subject_prior_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mixmin_vs_a2c8 | 1256 | 250 | 0.0456142 | 0.361041 | 0.198493 | 0.273056 | 0 | 1 | -0.0871189 | 0.000445159 |
| e72_failed_vs_mixmin | 893 | 249 | 0.00668422 | 0.206888 | 0.541271 | 1 | 0.137956 | -0.240749 | 1 | -0.000753013 |
| e85_vs_mixmin | 539 | 250 | 0.00474808 | 0.315393 | 0.425025 | 0.734771 | 0.624779 | -0.715206 | 0.781103 | -0.000177833 |
| e86_vs_mixmin | 579 | 250 | 0.00606415 | 0.298511 | 0.443457 | 0.772379 | 0.627063 | -0.758417 | 0.724524 | -0.000278301 |
| e87_noq2_vs_mixmin | 539 | 250 | 0.0058271 | 0.316044 | 0.420702 | 0.730408 | 0.636951 | -0.727638 | 0.772063 | -0.00022556 |
| e87_nooverstep_vs_mixmin | 579 | 250 | 0.00485132 | 0.298511 | 0.443457 | 0.772379 | 0.627063 | -0.758417 | 0.724524 | -0.000224778 |
| e87_inverse_top_vs_mixmin | 329 | 250 | 0.00392033 | 0.284085 | 0.602577 | 0.928415 | 0.563952 | -0.716722 | 0.862743 | -0.00031864 |

## Strongest Context Concentrations

### mixmin_vs_a2c8
- `calendar_context=gap_adjacent` rows `168` mass `0.666353`, mean abs logit `0.0452309`, high-mix row rate `0.178571`, high-E72 row rate `0.178571`.
- `train_span_zone=inside_train_calendar` rows `156` mass `0.626618`, mean abs logit `0.0458056`, high-mix row rate `0.211538`, high-E72 row rate `0.179487`.
- `test_run_length_bin=len4_7` rows `99` mass `0.404701`, mean abs logit `0.0466164`, high-mix row rate `0.272727`, high-E72 row rate `0.262626`.
- `train_span_zone=after_train_end` rows `94` mass `0.373382`, mean abs logit `0.0452966`, high-mix row rate `0.180851`, high-E72 row rate `0.234043`.

### e72_failed_vs_mixmin
- `calendar_context=gap_adjacent` rows `168` mass `0.674065`, mean abs logit `0.00670476`, high-mix row rate `0.178571`, high-E72 row rate `0.178571`.
- `train_span_zone=inside_train_calendar` rows `156` mass `0.60736`, mean abs logit `0.00650598`, high-mix row rate `0.211538`, high-E72 row rate `0.179487`.
- `test_run_length_bin=len4_7` rows `99` mass `0.432967`, mean abs logit `0.00730821`, high-mix row rate `0.272727`, high-E72 row rate `0.262626`.
- `train_span_zone=after_train_end` rows `94` mass `0.39264`, mean abs logit `0.00698003`, high-mix row rate `0.180851`, high-E72 row rate `0.234043`.

### e86_vs_mixmin
- `calendar_context=gap_adjacent` rows `168` mass `0.65432`, mean abs logit `0.0059046`, high-mix row rate `0.178571`, high-E72 row rate `0.178571`.
- `train_span_zone=inside_train_calendar` rows `156` mass `0.612823`, mean abs logit `0.00595553`, high-mix row rate `0.211538`, high-E72 row rate `0.179487`.
- `test_run_length_bin=len4_7` rows `99` mass `0.403278`, mean abs logit `0.0061756`, high-mix row rate `0.272727`, high-E72 row rate `0.262626`.
- `train_span_zone=after_train_end` rows `94` mass `0.387177`, mean abs logit `0.0062444`, high-mix row rate `0.180851`, high-E72 row rate `0.234043`.

### e87_inverse_top_vs_mixmin
- `calendar_context=gap_adjacent` rows `168` mass `0.642835`, mean abs logit `0.00375019`, high-mix row rate `0.178571`, high-E72 row rate `0.178571`.
- `train_span_zone=inside_train_calendar` rows `156` mass `0.618543`, mean abs logit `0.00388605`, high-mix row rate `0.211538`, high-E72 row rate `0.179487`.
- `test_run_length_bin=len4_7` rows `99` mass `0.419244`, mean abs logit `0.00415044`, high-mix row rate `0.272727`, high-E72 row rate `0.262626`.
- `train_span_zone=after_train_end` rows `94` mass `0.381457`, mean abs logit `0.00397723`, high-mix row rate `0.180851`, high-E72 row rate `0.234043`.

## Target Axis Notes

- `e85_vs_mixmin` dominant targets: S1 abs `0.0132276` subjCE `-0.00127868`, S2 abs `0.0120874` subjCE `0.000219114`, S3 abs `0.00792157` subjCE `-0.000185266`, Q1 abs `6.29496e-17` subjCE `1.79023e-17`.
- `e86_vs_mixmin` dominant targets: S1 abs `0.0164188` subjCE `-0.00163166`, S2 abs `0.0149174` subjCE `0.000266321`, S3 abs `0.00856107` subjCE `-0.000197574`, Q2 abs `0.00255171` subjCE `-0.000385187`.
- `e87_noq2_vs_mixmin` dominant targets: S1 abs `0.0164213` subjCE `-0.00163139`, S2 abs `0.0149203` subjCE `0.00026646`, S3 abs `0.00944812` subjCE `-0.000213988`, Q1 abs `6.53921e-17` subjCE `1.79023e-17`.
- `e87_nooverstep_vs_mixmin` dominant targets: S1 abs `0.0131351` subjCE `-0.00130938`, S2 abs `0.0119339` subjCE `0.000208589`, S3 abs `0.00684886` subjCE `-0.000163727`, Q2 abs `0.00204137` subjCE `-0.00030893`.
- `e87_inverse_top_vs_mixmin` dominant targets: S1 abs `0.0163671` subjCE `-0.00165063`, S3 abs `0.00854044` subjCE `-0.000197183`, Q2 abs `0.00253481` subjCE `-0.000382669`, Q1 abs `6.53921e-17` subjCE `1.79023e-17`.

## Feature Correlation Notes

- `e86_vs_mixmin` strongest row-move correlations: e72_failed_row_abs `0.725471`, mixmin_vs_a2c8_row_abs `0.282944`, raw_domain_prob `0.131014`, raw_density_radius `0.127376`.
- `e87_noq2_vs_mixmin` strongest row-move correlations: e72_failed_row_abs `0.683567`, mixmin_vs_a2c8_row_abs `0.257653`, raw_density_radius `0.1441`, raw_domain_prob `0.142842`.
- `e87_nooverstep_vs_mixmin` strongest row-move correlations: e72_failed_row_abs `0.725471`, mixmin_vs_a2c8_row_abs `0.282944`, raw_domain_prob `0.131014`, raw_density_radius `0.127376`.
- `e87_inverse_top_vs_mixmin` strongest row-move correlations: e72_failed_row_abs `0.743567`, mixmin_vs_a2c8_row_abs `0.18614`, raw_domain_prob `0.133046`, test_day_index `0.116307`.

## Interpretation

- E86 is not an all-target replay of E72, but it is still E72-contamination-proximate: cell overlap ratio `0.819288` and row correlation `0.725471` versus E72 self-reference `1`.
- All E85/E86/E87 variants have negative signed correlation with the original mixmin-vs-a2c8 move, so this branch is better described as a second-order rollback/refinement of mixmin, not continuation of mixmin's first-order law.
- The no-Q2 contrast is the cleanest public-risk split among E87 variants: contamination index `0.730408` versus E86 `0.772379`. The no-overstep contrast lowers amplitude but keeps the same moved-cell geometry.
- The inverse-top-prior contrast has the largest E72 contamination index `0.928415`, so E88 demotes it from a safety candidate to a high-information diagnostic only.
- Negative subject-prior CE proxies suggest the moves are not ordinary prevalence/prior correction; they are more likely hidden-world or combo-set corrections with public contamination risk.

## Decision

E88 does not create a new submission. It supplies a risk lens for E86/E87 public feedback: compare whether the public winner follows mixmin-overlap, avoids E72-overlap, or concentrates in raw-domain/calendar blocks.
