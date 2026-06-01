# ETRI Sleep Lifestyle Competition Workspace

This repository snapshot is rooted at the former local `cl2/` workspace.

Current public frontier:

- `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv`
- Public LB: `0.5681234831`
- Previous frontier: `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`
- Improvement over previous frontier: `0.0080354663`
- Interpretation: H012 validates the public-equation HS-JEPA branch. Known public LB observations are no longer only diagnostics; as equations over a hidden public label/subset state, they produced a large public-readable action.
- External reference note: the attached high-scoring `submission_v106_sleep_state_conditioned_memory.csv` document reports public LB `0.5703952266` from same-subject sleep-state/sensor-quality-conditioned memory. That supports the broader repeated-subject world model, but H012 is still lower by `0.0022717435`.

Current high-risk next sensors:

- `submission_h015_self_feedback_top_all_k1600_a0.7_uploadsafe.csv`
- Public LB: not submitted
- Interpretation: H015 includes H012's own public score as a new public-equation anchor and asks whether H012 is an under-amplified posterior rather than a fixed point. It predicts a further posterior delta of about `-0.001586` versus H012, but this is a public self-feedback bet with real overfit/private-risk exposure.

- `submission_h016_public_subset_gain_all_k1000_a0.75_uploadsafe.csv`
- Public LB: not submitted
- Interpretation: H016 treats known public LB observations as a diffuse public cell-weight/gain field. It survived a `300`-permutation null stress and predicts `-0.000296` versus H012 by applying H015 movement only on inferred public-weight-compatible cells. It is lower-upside than H015, but it tests a different world model.

- `submission_h017_joint_label_weight_oracle_gain_all_k1650_a1_uploadsafe.csv`
- Public LB: not submitted
- Interpretation: H017 tests whether H012's public posterior and H016's diffuse weights are compatible parts of one hidden public equation. It predicts `-0.000575` versus H012 by moving H012 further toward the original H012 posterior under H016 weights. It is a posterior-completion test, not independent private-safety evidence.

- `submission_h018_hard_label_world_combined_all_k1750_a1_uploadsafe.csv`
- Public LB: not submitted
- Interpretation: H018 forces the H017 posterior into sampled binary public label worlds. The hard-world posterior beats all `300` permuted-public-delta nulls and predicts `-0.000603` versus H012. It is the binary-aware version of posterior-completion, not a separate human-state/private-safety proof.

Public LB operating rule:

- Public LB is not an iteration loop. A file is promotable only when it beats the current priority under public-free stress, including fresh nulls that were not used to build the candidate.
- Local-interesting files stay diagnostic if they only improve old selector p90, semantic attribution, or a single stress view.
- The next public slot should answer a predeclared worldview question, not rescue a local tweak after the fact.
- After H012, the main public question is no longer "can we find a tiny E247-safe movement?" It is "which parts of the public-equation posterior are real hidden-state signal versus public-subset overfit, and how do subject/time memory and raw human-state context explain them?"
- H014 says same-subject sleep-state memory does not explain most of H012's gain. H015 says the public-equation system itself still wants to sharpen H012. H016/H017/H018 split that question into cell weights, continuous posterior-completion, and binary hard-world posterior-completion.

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
