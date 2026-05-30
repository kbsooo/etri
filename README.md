# ETRI Sleep Lifestyle Competition Workspace

This repository snapshot is rooted at the former local `cl2/` workspace.

Current public frontier:

- `analysis_outputs/submission_e95_hardtail_541e3973.csv`
- Public LB: `0.5762913298`
- Previous frontier: `analysis_outputs/submission_mixmin_0c916bb4.csv`
- Improvement over previous frontier: `0.0000153107`
- Latest resolved sensor: `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` public LB `0.576311831`
- Latest diagnostic: E206 applies the E205 decoder and classifies E176 as `branch_loss`. Same-family broad partial-reopen expected-score follow-ups are weakened; the coherent existing follow-up is E154 body-exit counter-world, or non-collinear latent search.

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
