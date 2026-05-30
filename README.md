# ETRI Sleep Lifestyle Competition Workspace

This repository snapshot is rooted at the former local `cl2/` workspace.

Current public frontier:

- `analysis_outputs/submission_e95_hardtail_541e3973.csv`
- Public LB: `0.5762913298`
- Previous frontier: `analysis_outputs/submission_mixmin_0c916bb4.csv`
- Improvement over previous frontier: `0.0000153107`
- Current best next sensor: `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`
- Latest diagnostic: E203 adds component knockout stress on top of E201/E202. E176 remains first; its body is broad S-stage / between-train-runs, while top33 is a compact cancellation layer rather than the whole signal.

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
