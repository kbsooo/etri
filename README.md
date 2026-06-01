# ETRI Sleep Lifestyle Competition Workspace

This repository snapshot is rooted at the former local `cl2/` workspace.

Current public frontier:

- `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv`
- Public LB: `0.5681234831`
- Previous frontier: `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`
- Improvement over previous frontier: `0.0080354663`
- Interpretation: H012 validates the public-equation HS-JEPA branch. Known public LB observations are no longer only diagnostics; as equations over a hidden public label/subset state, they produced a large public-readable action.
- External reference note: the attached high-scoring `submission_v106_sleep_state_conditioned_memory.csv` document reports public LB `0.5703952266` from same-subject sleep-state/sensor-quality-conditioned memory. That supports the broader repeated-subject world model, but H012 is still lower by `0.0022717435`.

Current high-risk next sensor:

- `submission_h015_self_feedback_top_all_k1600_a0.7_uploadsafe.csv`
- Public LB: not submitted
- Interpretation: H015 includes H012's own public score as a new public-equation anchor and asks whether H012 is an under-amplified posterior rather than a fixed point. It predicts a further posterior delta of about `-0.001586` versus H012, but this is a public self-feedback bet with real overfit/private-risk exposure.

Public LB operating rule:

- Public LB is not an iteration loop. A file is promotable only when it beats the current priority under public-free stress, including fresh nulls that were not used to build the candidate.
- Local-interesting files stay diagnostic if they only improve old selector p90, semantic attribution, or a single stress view.
- The next public slot should answer a predeclared worldview question, not rescue a local tweak after the fact.
- After H012, the main public question is no longer "can we find a tiny E247-safe movement?" It is "which parts of the public-equation posterior are real hidden-state signal versus public-subset overfit, and how do subject/time memory and raw human-state context explain them?"
- H014 says same-subject sleep-state memory does not explain most of H012's gain. H015 says the public-equation system itself still wants to sharpen H012. That is the next worldview-changing submission question.

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
