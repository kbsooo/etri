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

- `submission_h019_row_subset_hardworld_gain_all_r240_a1_uploadsafe.csv`
- Public LB: not submitted
- Interpretation: H019 forces the public-equation latent into sampled row-level public masks. It beats `300` permuted-public-delta nulls and supports a broad row-subset interpretation, but the row-exclusion action is internally slightly weaker than H018.

- `submission_h020_joint_vector_world_combined_all_k1750_a1_uploadsafe.csv`
- Public LB: not submitted
- Interpretation: H020 forces each row to live as one 7-target label vector, instead of treating every row-target cell independently. Its joint-vector world beats `300` permuted-public-delta nulls and predicts a larger internal move than H018/H019 (`-0.001105` vs H012 under its rowweighted sensor). The caveat is important: weak train co-occurrence priors help sampled world search, but the selected posterior uses `beta=0`, so the proven part is row-level joint-vector consistency, not yet train co-occurrence as an action prior.

- `submission_h021_agree_h020_k1200_a1_e1546ba9_uploadsafe.csv`
- Public LB: not submitted
- Interpretation: H021 is the first post-H012 candidate that directly bridges raw human-state context to the H020 row-vector branch. Human-state vector priors beat the global train-vector prior in train-only validation (`0.617585` vs `0.664614` BCE), but direct q_hs replacement is rejected. The promoted action uses q_hs only as a gate, applying H020 on `1200` agreement cells and retaining `0.618866` of H020's internal gain while beating a row-permuted q_hs null by `0.005549`.

- H022 produced no promoted root submission.
- Interpretation: H022 injected H021's `q_hs` into the H020 vector-world posterior. Weak human-state prior helped sampled-world search (`hs_b0.1` best config), but final posterior selection reverted to `none_b0`. This records a useful architecture boundary: human-state context is a proposal/gate/action-health latent, not yet a calibrated final probability prior.

- H023 produced no promoted root submission.
- Interpretation: H023 tested the weaker and more useful role for `q_hs`: proposal/Pareto energy after public-compatible vector worlds are found. Public-error top1000 worlds are strongly human-state-aligned (`4.877889` real energy vs `5.234523` row-permutation null median), but q_hs-Pareto posterior selection does not improve public fit against row-permuted controls (`rowperm_public_p=0.754098`). This is architecture evidence, not an upload candidate.

- H024 produced no promoted root submission.
- Interpretation: H024 learned an action-health decoder over known public observations and H015-H023 candidate movement anatomy. It reconstructs known public ordering well in leave-one-out (`geometry` alpha `100`, MAE `0.000773`, Spearman `0.970`, pairwise `0.947`), but post-H012 unknown candidates are not stable: the best unknown diagnostic is an H015 `k100` move with median predicted public `0.570054`, wide p10/p90 `0.559653-0.580761`, support-better-than-H012 only `0.15`, and permutation p `0.841`. This confirms the current bottleneck: posterior generators are ahead of the action-health decoder.

- H025 produced no promoted root submission.
- Interpretation: H025 created independent train-side counterfactual action-health supervision instead of regressing public LB. It generated probability actions from subject/time/KNN/human-state proposals and learned which moves reduce train logloss. The action-health signal is learnable inside proposal families, but row/time transfer is weak (`Spearman 0.021091`, top10 lift `0.004426`) and the selected test candidate fails row-permuted placement stress (`p=0.576667`). The important negative result is that train-visible action health likes known public-bad Q2/residual shortcuts, so the remaining HS-JEPA gap is public/private calibration, not another train counterfactual ranker.

- H026 produced no promoted root submission.
- Interpretation: H026 tested the obvious repair to H025: combine train action-health with a public/private calibration veto against known public-bad Q2/residual shortcut axes. The source-level veto works as a diagnostic: H012 ranks first while known-bad JEPA/Q2/residual anchors are pushed down. But generated post-H012 veto variants are still not public-safe. The selected diagnostic has H025 row-permutation p `0.000000`, yet H024 predicts public `0.574388` and public-score permutation p `0.898000`, far worse than H012 `0.568123`. This means the bottleneck is deeper than a scalar bad-axis veto: the next breakthrough must change the public/private calibration target or candidate generator, not merely trim H025-selected moves.

Public LB operating rule:

- Public LB is not an iteration loop. A file is promotable only when it beats the current priority under public-free stress, including fresh nulls that were not used to build the candidate.
- Local-interesting files stay diagnostic if they only improve old selector p90, semantic attribution, or a single stress view.
- The next public slot should answer a predeclared worldview question, not rescue a local tweak after the fact.
- After H012, the main public question is no longer "can we find a tiny E247-safe movement?" It is "which parts of the public-equation posterior are real hidden-state signal versus public-subset overfit, and how do subject/time memory and raw human-state context explain them?"
- H014 says same-subject sleep-state memory does not explain most of H012's gain. H015 says the public-equation system itself still wants to sharpen H012. H016/H017/H018 split that question into cell weights, continuous posterior-completion, and binary hard-world posterior-completion. H019 adds the stricter row-subset constraint and finds broad row-level compatibility, but not a better action than H018. H020 raises the constraint again from independent cells to whole-row 7-label vectors. H021 adds the missing human-state bridge: raw lifestyle context can gate the H020 vector action, but is not yet calibrated enough to replace public-equation probabilities. H022 confirms that split by rejecting q_hs as final posterior prior while keeping it alive as proposal/search/gate signal. H023 shows the bridge is not imaginary: public-compatible worlds are human-state-aligned. H024 then confirms that public-axis action-health is learnable but unstable on unseen candidates. H025 adds the sharper falsification: train-side action-health is also not enough, because it transfers weakly across row/time folds and prefers known public-bad Q2/residual anatomy. H026 shows that a scalar public-bad veto can fix known-anchor ranking but still cannot make post-H012 actions public-safe. The missing piece is now a richer public/private calibration target or a new generator whose actions are born public-private-aware.

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
