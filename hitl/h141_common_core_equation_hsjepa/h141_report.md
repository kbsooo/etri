# H141 Common-Core Public/Private Equation HS-JEPA

Question: what happens if we keep only the row-target assignment that H139 and
H140 both implicitly agree on?

Selected common core:

| candidate_id | atoms | rows | changed_cells_vs_h136 | delta_h088 | delta_margin | delta_h098 | delta_route | h140_passes_dropout_gate | h141_common_core_pass | h141_h098_tight_pass | h141_core_survival | resolved_path | h141_root_uploadsafe_path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h139_0999d3ae | anti05_r70_Q3_f0p5|forward_r131_S2_f0p25 | 70,131 | 2 | -0.001425939 | 0.000266163 | 0.000001000 | 0.000001193 | True | True | True | 0.043319340 | /Users/kbsoo/Downloads/cl2/hitl/h139_role_atom_assignment_equation_hsjepa/submission_h139_0999d3ae.csv | /Users/kbsoo/Downloads/cl2/submission_h141_commoncore_0999d3ae_uploadsafe.csv |

Common-core frontier:

| candidate_id | atoms | rows | changed_cells_vs_h136 | delta_h088 | delta_margin | delta_h098 | delta_route | h140_passes_dropout_gate | h141_common_core_pass | h141_h098_tight_pass | h141_core_survival | resolved_path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h139_0999d3ae | anti05_r70_Q3_f0p5|forward_r131_S2_f0p25 | 70,131 | 2 | -0.001425939 | 0.000266163 | 0.000001000 | 0.000001193 | True | True | True | 0.043319340 | /Users/kbsoo/Downloads/cl2/hitl/h139_role_atom_assignment_equation_hsjepa/submission_h139_0999d3ae.csv |
| h139_19c37fd6 | anti1_r70_Q3_f0p25|forward_r131_S2_f0p25 | 70,131 | 2 | -0.001466906 | 0.000307714 | 0.000001149 | 0.000001184 | True | True | False | 0.042072179 | /Users/kbsoo/Downloads/cl2/hitl/h139_role_atom_assignment_equation_hsjepa/submission_h139_19c37fd6.csv |
| h139_da90ca1f | anti05_r70_Q3_f0p25|forward_r131_S2_f0p25 | 70,131 | 2 | -0.001302278 | 0.000108410 | 0.000000628 | 0.000001215 | False | False | False | 0.023981170 | /Users/kbsoo/Downloads/cl2/hitl/h139_role_atom_assignment_equation_hsjepa/submission_h139_da90ca1f.csv |
| h139_b320b228 | anti025_r70_Q3_f0p5|forward_r131_S2_f0p25 | 70,131 | 2 | -0.001273944 | 0.000067709 | 0.000000554 | 0.000001219 | False | False | False | 0.022381383 | /Users/kbsoo/Downloads/cl2/hitl/h139_role_atom_assignment_equation_hsjepa/submission_h139_b320b228.csv |

Interpretation:

```text
row70 Q3  = margin repair
row131 S2 = toxicity relief
row207 S2 = held out H088-heavy optional tail
row135 Q3/S2 = held out sensor-dropout repair add-on
```

Public sensor reading:

- H141 > H139 and H140: row70+row131 is the action-grade equation core; row207
  and row135 were over-corrections.
- H139 > H141: row207 S2 H088 relief is not just diagnostic, it is action-grade.
- H140 > H141: row135 repair is needed for public/private safety, and the
  two-cell common core underfits the boundary.
- H136 > H141: even the shared role atoms are diagnostics rather than safe
  submission actions.
