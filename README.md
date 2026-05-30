# ETRI Sleep Lifestyle Competition Workspace

This repository snapshot is rooted at the former local `cl2/` workspace.

Current public frontier:

- `analysis_outputs/submission_e95_hardtail_541e3973.csv`
- Public LB: `0.5762913298`
- Previous frontier: `analysis_outputs/submission_mixmin_0c916bb4.csv`
- Improvement over previous frontier: `0.0000153107`
- Current best next sensor: `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`
- Latest diagnostic: E202 adds component responsibility on top of the E201 file/hash router. E176 remains first, but its score should be read as broad S-stage / between-train-runs body with Q2 as a guard, not as Q2-only amplitude feedback.

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
