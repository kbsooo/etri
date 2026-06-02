# H138 One-Sided Toxicity Boundary HS-JEPA

Question: can H137's H088 relief become action-grade only when paired with a
separate margin-repair assignment?

Start field: H136.

Start equation values:

- route: `-0.000762293598`
- H098/model: `-0.000027358028`
- H088: `-0.062132664419`
- margin: `0.159441050448`

Action atoms:

| name | role | worldview | changed_cells_vs_h136 | delta_route | delta_h098 | delta_h088 | delta_margin | route | h098 | h088 | margin | h138_action_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| r135_q3s2_margin_repair_g05 | margin_repair | stronger row135 Q3/S2 repair; better margin but larger H098 cost | 2 | 0.000001248 | 0.000001347 | -0.000115412 | 0.000227733 | -0.000761046 | -0.000026011 | -0.062248077 | 0.159668783 | 0.003565339 |
| r135_q3s2_margin_repair_g025 | margin_repair | row135 Q3/S2 repairs margin with small H088 relief | 2 | 0.000001219 | 0.000000699 | -0.000095477 | 0.000210901 | -0.000761074 | -0.000026659 | -0.062228141 | 0.159651952 | 0.003545886 |
| r135_q3s2_soft_repair | soft_margin_repair | weaker row135 Q3/S2 repair used as low-cost boundary control | 2 | 0.000001222 | 0.000000507 | -0.000014053 | 0.000068355 | -0.000761071 | -0.000026851 | -0.062146718 | 0.159509405 | 0.000492818 |
| r207_s2_toxicity_relief | toxicity_relief | row207 S2 lowers H088 but is unsafe alone because it spends margin | 1 | 0.000001234 | 0.000000653 | -0.000988686 | -0.000145272 | -0.000761060 | -0.000026705 | -0.063121350 | 0.159295778 | -0.001385539 |
| r131_s1s2_stress_decoy | stress_decoy | stress decoy: should be rejected if H088-only shortcuts are toxic | 2 | 0.000002412 | 0.000000350 | 0.000202548 | -0.000036801 | -0.000759881 | -0.000027008 | -0.061930117 | 0.159404249 | -0.002344811 |

Candidates:

| candidate_id | spec | actions | changed_cells_vs_h136 | delta_route | delta_h098 | delta_h088 | delta_margin | h102_cum_h088_axis_cos | h102_cum_good_bad_margin | passes_one_sided_boundary | h138_candidate_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h138_boundary_pair_g025_52b26210 | boundary_pair_g025 | r207_s2_toxicity_relief|r135_q3s2_margin_repair_g025 | 3 | 0.000002453 | 0.000001352 | -0.001088214 | 0.000064141 | -0.063220879 | 0.159505191 | True | 0.012307219 | submission_h138_boundary_pair_g025_52b26210.csv |
| h138_boundary_pair_g05_ab809ab5 | boundary_pair_g05 | r207_s2_toxicity_relief|r135_q3s2_margin_repair_g05 | 3 | 0.000002482 | 0.000002000 | -0.001111155 | 0.000080005 | -0.063243820 | 0.159521056 | False | 0.011631816 | submission_h138_boundary_pair_g05_ab809ab5.csv |
| h138_margin_only_g05_09427c97 | margin_only_g05 | r135_q3s2_margin_repair_g05 | 2 | 0.000001248 | 0.000001347 | -0.000115412 | 0.000227733 | -0.062248077 | 0.159668783 | False | 0.005465339 | submission_h138_margin_only_g05_09427c97.csv |
| h138_margin_only_g025_baeb4807 | margin_only_g025 | r135_q3s2_margin_repair_g025 | 2 | 0.000001219 | 0.000000699 | -0.000095477 | 0.000210901 | -0.062228141 | 0.159651952 | False | 0.005445886 | submission_h138_margin_only_g025_baeb4807.csv |
| h138_boundary_pair_soft_1421f5dd | boundary_pair_soft | r207_s2_toxicity_relief|r135_q3s2_soft_repair | 3 | 0.000002456 | 0.000001160 | -0.001005169 | -0.000077744 | -0.063137833 | 0.159363307 | False | -0.002179010 | submission_h138_boundary_pair_soft_1421f5dd.csv |
| h138_toxicity_relief_only_2bea533f | toxicity_relief_only | r207_s2_toxicity_relief | 1 | 0.000001234 | 0.000000653 | -0.000988686 | -0.000145272 | -0.063121350 | 0.159295778 | False | -0.003485539 | submission_h138_toxicity_relief_only_2bea533f.csv |
| h138_stress_decoy_pair_a1098373 | stress_decoy_pair | r207_s2_toxicity_relief|r131_s1s2_stress_decoy | 3 | 0.000003646 | 0.000001003 | -0.000786108 | -0.000181973 | -0.062918772 | 0.159259077 | False | -0.008046672 | submission_h138_stress_decoy_pair_a1098373.csv |

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | candidate_id | spec | actions | worldview | changed_cells_vs_h136 | changed_cells_vs_h136_prob | delta_route | delta_h098 | delta_h088 | delta_margin | route | h098 | h088 | margin | h102_cum_h088_axis_cos | h102_cum_good_bad_margin | h138_candidate_score | passes_one_sided_boundary | file | resolved_path | validation_path | validation_rows | validation_keys_match | validation_duplicate_keys | validation_nan_cells | validation_min_prob | validation_max_prob | validation_changed_cells_vs_h057_validation | validation_upload_safe | root_path | root_rows | root_keys_match | root_duplicate_keys | root_nan_cells | root_min_prob | root_max_prob | root_changed_cells_vs_h057_validation | root_upload_safe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote_h138_one_sided_boundary_assignment | h138_boundary_pair_g025_52b26210 | /Users/kbsoo/Downloads/cl2/submission_h138_boundary_52b26210_uploadsafe.csv | h138_boundary_pair_g025_52b26210 | boundary_pair_g025 | r207_s2_toxicity_relief|r135_q3s2_margin_repair_g025 | toxicity relief plus low-cost margin repair should be the safest assignment field | 3 | 3 | 0.000002453 | 0.000001352 | -0.001088214 | 0.000064141 | -0.000759840 | -0.000026006 | -0.063220879 | 0.159505191 | -0.063220879 | 0.159505191 | 0.012307219 | True | submission_h138_boundary_pair_g025_52b26210.csv | /Users/kbsoo/Downloads/cl2/hitl/h138_one_sided_toxicity_boundary_hsjepa/submission_h138_boundary_pair_g025_52b26210.csv | /Users/kbsoo/Downloads/cl2/hitl/h138_one_sided_toxicity_boundary_hsjepa/submission_h138_boundary_pair_g025_52b26210.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 28 | True | /Users/kbsoo/Downloads/cl2/submission_h138_boundary_52b26210_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 28 | True |

Interpretation:

H138 is not an H088-minimizer.  It promotes only a one-sided boundary action
whose H088 relief survives after margin, route, and H098 constraints.  The
selected field should be read as:

```text
H136 safe row-state core
+ row207 S2 toxicity relief
+ row135 Q3/S2 margin repair
= boundary-safe row-target assignment hypothesis
```

Public interpretation:

- H138 > H137 and H136: toxicity relief is real but needs a repair head.
- H137 > H138: row135 repair is false and H088 relief should remain local.
- H136 > H138: counterfields are stress diagnostics, not action-grade.
