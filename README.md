# ETRI Sleep Lifestyle Competition Workspace

This repository snapshot is rooted at the former local `cl2/` workspace.

Current public frontier:

- `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`
- Public LB: `0.5761589494`
- Previous frontier: `analysis_outputs/submission_e95_hardtail_541e3973.csv`
- Improvement over previous frontier: `0.0001323804`
- Latest resolved public sensor: `analysis_outputs/submission_e323_5508f966_uploadsafe.csv` public LB `0.5770355016`, which is worse than E247 by `0.0008765522`. This rejects the E323/E324 null-common residual branch as a public-transfer candidate, despite its strong local null stress.
- Latest public-free diagnostic before that public result: E327 null-fail risk censor on top of the E323/E324 branch. E327 generated `540` build-null-risk variants and stress-tested `40` selected candidates against `7760` fresh null rows. Nullfail-censor variants beat anti-controls (`2/33` ready vs `0/7`), but no file beat the E324 priority locally. The later E323 public result shows that this whole local matched-null family was missing a public/private calibration or subset axis.

Public LB operating rule:

- Public LB is not an iteration loop. A file is promotable only when it beats the current priority under public-free stress, including fresh nulls that were not used to build the candidate.
- Local-interesting files stay diagnostic if they only improve old selector p90, semantic attribution, or a single stress view.
- The next public slot should answer a predeclared worldview question, not rescue a local tweak after the fact.

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
