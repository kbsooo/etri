# Learned Permission Gate Decoder

This experiment replaces fixed target permission rules with nested row-level meta decoders. The models use only independent branch predictions (stable, extended, fixed policy), fold-safe subject prior, signed-margin features, and panel position; v83 is used only as a drift diagnostic.

## Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | drift_vs_reference | corr_vs_reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_permission_policy | 0.615095 | 0.663133 | 0.685743 | 0.665606 | 0.565500 | 0.572205 | 0.528019 | 0.625461 | 0.070382 | 0.858505 |
| learned_gate_hgb_fixed | 0.615610 | 0.663548 | 0.685743 | 0.665606 | 0.566857 | 0.573691 | 0.528850 | 0.624976 | 0.068406 | 0.868856 |
| learned_gate_hgb_ext | 0.616086 | 0.665589 | 0.685467 | 0.665606 | 0.566857 | 0.573691 | 0.530414 | 0.624976 | 0.068034 | 0.870668 |
| learned_gate_logreg_ext | 0.616187 | 0.665909 | 0.685980 | 0.665606 | 0.565998 | 0.573551 | 0.530993 | 0.625276 | 0.068401 | 0.869867 |
| extended_full_oof_winners | 0.616766 | 0.664980 | 0.689098 | 0.665606 | 0.565500 | 0.572205 | 0.534513 | 0.625461 | 0.069892 | 0.860714 |
| learned_residual_hgb_c030 | 0.619359 | 0.670190 | 0.678672 | 0.657893 | 0.584424 | 0.581266 | 0.533337 | 0.629731 | 0.074898 | 0.848396 |
| stable_signal_s4_temporal | 0.620281 | 0.670652 | 0.685743 | 0.665606 | 0.572511 | 0.577195 | 0.529419 | 0.640842 | 0.068726 | 0.871113 |
| learned_stack_hgb | 0.623708 | 0.673016 | 0.678636 | 0.656726 | 0.585841 | 0.580399 | 0.558590 | 0.632747 | 0.093932 | 0.766377 |
| learned_residual_hgb_c050 | 0.626386 | 0.678049 | 0.682915 | 0.662633 | 0.597763 | 0.591032 | 0.541258 | 0.631048 | 0.089557 | 0.821744 |
| learned_residual_ridge_c030 | 0.629275 | 0.680692 | 0.711165 | 0.681981 | 0.582034 | 0.581750 | 0.532772 | 0.634531 | 0.076164 | 0.844592 |
| learned_stack_logreg | 0.638543 | 0.688828 | 0.736782 | 0.676232 | 0.594539 | 0.596801 | 0.539950 | 0.636666 | 0.082503 | 0.804039 |
