# ETRI Sleep Lifestyle Competition Workspace

This repository snapshot is rooted at the former local `cl2/` workspace.

Current public frontier:

- `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`
- Public LB: `0.5761589494`
- Previous frontier: `analysis_outputs/submission_e95_hardtail_541e3973.csv`
- Improvement over previous frontier: `0.0001323804`
- Latest resolved public sensor: `analysis_outputs/submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv` public LB `0.5762805676`, which rejects the amplitude-constrained E247 follow-up while keeping feature-NN1 Q3 smoothing positive versus E95.
- Latest public-free diagnostic: E322 E321-guided adversarial preselector. E319/E320 showed that fresh mode-specialized tensors are visible but fail row/subject/dateblock placement nulls. E321 made that failure learnable: full-pair geometry predicts actual-vs-null p90 wins with AUC row `0.821035`, subject `0.930077`, dateblock `0.915720`; candidate-level adversarial-health Spearman is `0.508146`. E322 then used that learner to preselect previously unevaluated E319 candidates for fresh null governance. It selected `36` old-strict files, but fresh public-free ready remained `0`; best fresh p90 was `-0.001452588`, best null strict rate was `0.136364`, and the best worst-mode dominance was `1.000000`. Current policy is no public submission until action-health is used during generation, not only post-hoc ranking.

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
