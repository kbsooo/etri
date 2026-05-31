# ETRI Sleep Lifestyle Competition Workspace

This repository snapshot is rooted at the former local `cl2/` workspace.

Current public frontier:

- `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`
- Public LB: `0.5761589494`
- Previous frontier: `analysis_outputs/submission_e95_hardtail_541e3973.csv`
- Improvement over previous frontier: `0.0001323804`
- Latest resolved public sensor: `analysis_outputs/submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv` public LB `0.5762805676`, which rejects the amplitude-constrained E247 follow-up while keeping feature-NN1 Q3 smoothing positive versus E95.
- Latest public-free diagnostic: E319/E320 mode-specialized generator and failure anatomy. E319 converts E318 route policies into fresh consensus/blend/residual tensors and creates no public submission. It generated `540` candidates and `403` old-strict candidates, but `0` public-free ready files. E320 shows the failure is not target/sign/QS; target permutation and sign controls have mean dominance `1.0`, Q/S swap `0.978723`, while row/subject/dateblock are the blockers. Current policy is no public submission until a generator learns mode-specific action geometry that beats row/subject/dateblock adversarial controls locally.

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
