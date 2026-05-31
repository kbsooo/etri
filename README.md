# ETRI Sleep Lifestyle Competition Workspace

This repository snapshot is rooted at the former local `cl2/` workspace.

Current public frontier:

- `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`
- Public LB: `0.5761589494`
- Previous frontier: `analysis_outputs/submission_e95_hardtail_541e3973.csv`
- Improvement over previous frontier: `0.0001323804`
- Latest resolved public sensor: `analysis_outputs/submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv` public LB `0.5762805676`, which rejects the amplitude-constrained E247 follow-up while keeping feature-NN1 Q3 smoothing positive versus E95.
- Latest public-free diagnostic: E326 semantic residual censor on top of the E323/E324 null-common residual branch. E326 generated `252` semantic/anti-semantic variants and stress-tested `36` selected candidates against `6984` null rows. Semantic variants beat anti-controls (`2/24` ready vs `0/12`), but no file beat the E324 priority locally. E324 still selects `analysis_outputs/submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv` as the current priority candidate, with high-rep p90 `-0.000053747`, null strict `0.050388`, and worst-mode dominance `0.859375`.

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
