# ETRI Sleep Lifestyle Competition Workspace

This repository snapshot is rooted at the former local `cl2/` workspace.

Current public frontier:

- `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`
- Public LB: `0.5761589494`
- Previous frontier: `analysis_outputs/submission_e95_hardtail_541e3973.csv`
- Improvement over previous frontier: `0.0001323804`
- Latest resolved public sensor: `analysis_outputs/submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv` public LB `0.5762805676`, which rejects the amplitude-constrained E247 follow-up while keeping feature-NN1 Q3 smoothing positive versus E95.
- Latest public-free diagnostic: E323/E324 null-common residual branch. E322 preselection found no ready file, so E323 changed the action layer by subtracting/censoring row/subject/dateblock-null-common movement from E322 near misses. It generated `420` candidates, `291` old-strict, and `3` public-free ready files. E324 then stress-tested those `3` with `774` high-repetition null rows; all `3` survived. Current priority candidate is `analysis_outputs/submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv`, with high-rep p90 `-0.000053747`, null strict `0.050388`, and worst-mode dominance `0.859375`.

Primary working notes:

- `hypothesis_graph.md`
- `experiment_log.md`
- `lb_observation_log.md`
- `latent_diagnostics.md`
- `validation_stress_report.md`
- `feature_registry.md`
- `candidate_submissions.md`
- `failed_hypotheses.md`

The local `analysis_outputs/` directory contains many generated scan tables.
Only scripts, reports, summary/audit tables, and key submission files are tracked
in git; large generated artifacts remain local by design.
