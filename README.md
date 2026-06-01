# ETRI Sleep Lifestyle Competition Workspace

This repository snapshot is rooted at the former local `cl2/` workspace.

Current public frontier:

- `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv`
- Public LB: `0.5681234831`
- Previous frontier: `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`
- Improvement over previous frontier: `0.0080354663`
- Interpretation: H012 validates the public-equation HS-JEPA branch. Known public LB observations are no longer only diagnostics; as equations over a hidden public label/subset state, they produced a large public-readable action.
- External reference note: the attached high-scoring `submission_v106_sleep_state_conditioned_memory.csv` document reports public LB `0.5703952266` from same-subject sleep-state/sensor-quality-conditioned memory. That supports the broader repeated-subject world model, but H012 is still lower by `0.0022717435`.

Current post-H012 status:

- No H015-H034 file is currently promoted as the next upload. H012 remains the active submission anchor.
- The historical post-H012 sensors below are kept because they define falsified or partially supported HS-JEPA routes, not because they are current submission recommendations.

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

- H027 produced no promoted root submission.
- Interpretation: H027 tested the stronger repair: make the post-H012 generator born public/private-aware by combining H015/H020/H023 public posterior targets with H021/H023 human-state agreement, H014 same-subject sleep-state memory, and H026 public-good/bad axes before materializing cells. It generated `1648` variants. The best diagnostic was `hitl/h027_public_private_aware_generator_jepa/submission_h027_h015_public_feedback_bad_axis_escape_S1S2S3_k80_a0p25.csv`, but H024 predicted public `0.569712`, support below H012 only `0.150000`, H025 row-permutation p `0.383333`, and public-score permutation p `0.822000`. This kills the idea that existing H015/H020/H023 posterior targets can be made H012-beating simply by cell-level memory/private-safety birth constraints.

- H028 produced no promoted root submission.
- Interpretation: H028 changed the target instead of adding another gate. Known public submissions were treated as interventions from H012, and the model learned a low-rank cell-level public action-gradient. The gradient fit was not random noise (`all`, alpha `100`, LOO MAE `0.001204883`, permutation p `0.000000`), but extrapolating from H012 was not safe: the best generated file was predicted by H024 at public `0.576388`, support below H012 only `0.083333`, H025 row-permutation p `0.710000`, and public-score permutation p `0.918000`. This is a sharper negative result: public responses are learnable as a coarse H012-vs-rest geometry, but they do not define a smooth local gradient that can move H012 lower.

- H029 produced no promoted root submission.
- Interpretation: H029 treated H012 as a needle basin and broke/preserved one invariant at a time: exact support, amplitude, target/subject rollback, same-subject memory agreement, and target-wise row identity. It generated `102` variants. The strongest diagnostic was `rollback_target_S1`, but H024 still priced it above the real H012 (`0.570495` median, `+0.002371` vs H012), with support below H012 only `0.116667`, public-score permutation p `0.858000`, and H025 row-permutation p `0.613333`. Target-wise row permutation collapsed to about `0.581`, which is strong evidence that H012 is not a target-level calibration trick; exact row-target placement is part of the invariant.

- H030 produced no promoted root submission.
- Interpretation: H030 moved the H016/H019/H020/H014 identity signals inside the public-equation solver as row-target cell allowance priors. The real positive result is diagnostic: even when H012 is excluded as an equation and direct H012 priors are not used, the best independent prior predicts H012's public jump from E247 within about `0.000485` LogLoss (`-0.007550` predicted vs `-0.008035` actual), with `identity_combo`/`joint_vector_cell` as the strongest supports. The negative result is equally important: materializing those priors still fails H024/H025 stress. The best generated diagnostic is priced around `0.572160`, support below H012 only `0.100000`, public-score permutation p `0.923333`, and H025 row-permutation p `0.670000`. H030 therefore validates a row-target identity latent, but rejects it as a direct action layer. The next breakthrough must solve the translation from identity posterior to exact H012-like row-target placement, not merely strengthen the identity prior.

- H031 produced no promoted root submission.
- Interpretation: H031 used the attached V106 memory note in the opposite direction from H014. H014 showed that same-subject sleep-state memory disagrees with `714/1200` H012 cells, and those disagreeing cells carry `72.03%` of H012 posterior gain. H031 treated that memory-disagree region as the public-equation core, then tried conflict-core amplification, conflict-core plus agree-cost rollback, agree-cost rollback alone, and core-only reconstruction from E247. The best diagnostic remained above H012 by H024 (`0.569810`, margin `+0.001686`), support below H012 was only `0.150000`, and public-score permutation p was `0.800667`; row-placement was only mildly non-random (`H025 p=0.183333`). This strengthens the explanation that memory-conflict cells are causal to H012's public success, but rejects the action claim that they should be amplified or traded against memory-agree cells.

- H032 produced no promoted root submission.
- Interpretation: H032 tested whether H012 is recoverable as a phase point from a dense E247-to-public-posterior action diagram while withholding H012's public score from the state/action decoder. The decoder recovered the real H012 anchor as the best point: pre-H012 `geometry` decoder LOO MAE `0.000295`, Spearman `0.951`, pairwise `0.924`; H012 itself had pre-state prediction `0.563377`, while the best non-anchor sibling was priced much worse at `0.573189` and changed `1080` cells away from H012. This is strong architecture evidence that H012 is not arbitrary under the HS-JEPA state/action view, but it rejects the idea that a simple dense phase sweep around H012 contains a stronger sibling.

- H033 produced no promoted root submission.
- Interpretation: H033 turned the failed H032 siblings into contrastive interventions and learned which row-target operations break the H012 phase. The break signal is real: all-OOF MAE `0.000815`, Spearman `0.954`, pairwise `0.913`. But the learned negative-cost edit is not action-safe. The best generated diagnostic changed only `10` outside-support cells, yet the pre-H012 state decoder priced it `+0.016275` worse than H012, with public-score permutation p `0.861333` and H025 row-placement p `0.710000`. This rejects first-order independent-cell phase-lock editing. The live route is a nonlinear/discrete row-vector or route-level translator that recognizes H012-like phase support before materializing probability edits.

- H034 produced no promoted root submission.
- Interpretation: H034 moved the translator from independent cells to whole row-vector route patterns. The route representation is very healthy as a sibling-failure model: best all-OOF `et_route` MAE `0.000389`, Spearman `0.985`, pairwise `0.956`. But it does not yield a safe action. The best local-looking diagnostic, `row_rollback_support_rollback_memory_conflict_changed_r1_a0.08`, rolls back all 7 targets in row `144`; H024 pre-state predicts `-0.003999` versus H012, but the route model predicts `+0.032224`, public-score permutation p is only `0.305333`, and H025 row-placement p is `0.940000`. This exposes a new failure mode: H024 can hallucinate a tiny row rollback as public-good, while the row-route/action-health views reject it. First-order row-route edits are now also blocked; the next route is a direct H012-vs-sibling classifier or combinatorial phase solver.

Public LB operating rule:

- Public LB is not an iteration loop. A file is promotable only when it beats the current priority under public-free stress, including fresh nulls that were not used to build the candidate.
- Local-interesting files stay diagnostic if they only improve old selector p90, semantic attribution, or a single stress view.
- The next public slot should answer a predeclared worldview question, not rescue a local tweak after the fact.
- After H012, the main public question is no longer "can we find a tiny E247-safe movement?" It is "which parts of the public-equation posterior are real hidden-state signal versus public-subset overfit, and how do subject/time memory, raw human-state context, and phase/action geometry explain them?"
- H014 says same-subject sleep-state memory does not explain most of H012's gain. H015 says the public-equation system itself still wants to sharpen H012. H016/H017/H018 split that question into cell weights, continuous posterior-completion, and binary hard-world posterior-completion. H019 adds the stricter row-subset constraint and finds broad row-level compatibility, but not a better action than H018. H020 raises the constraint again from independent cells to whole-row 7-label vectors. H021 adds the missing human-state bridge: raw lifestyle context can gate the H020 vector action, but is not yet calibrated enough to replace public-equation probabilities. H022 confirms that split by rejecting q_hs as final posterior prior while keeping it alive as proposal/search/gate signal. H023 shows the bridge is not imaginary: public-compatible worlds are human-state-aligned. H024 then confirms that public-axis action-health is learnable but unstable on unseen candidates. H025 adds the sharper falsification: train-side action-health is also not enough, because it transfers weakly across row/time folds and prefers known public-bad Q2/residual anatomy. H026 shows that a scalar public-bad veto can fix known-anchor ranking but still cannot make post-H012 actions public-safe. H027 shows that even born-public/private cell constraints over the existing posterior targets do not recover H012-beating public transfer. H028 shows that known public scores can learn a coarse action-gradient, but not one that extrapolates safely from H012. H029 shows that breaking H012's exact row-target arrangement causes stress degradation even when target/support moments are partially preserved. H030 shows that row-target identity priors can partially anticipate H012 independently, but still cannot be safely materialized. H031 adds the V106 contrast: memory-disagree cells explain H012's public core better than memory-agree cells, but amplifying that core is still not a safe action. H032 then shows the current translator can recover H012 itself when H012 public feedback is withheld, yet cannot find a better neighboring phase point. H033 shows the neighboring failures are learnable as phase-lock contrast, but first-order independent-cell negative-cost edits still leave the H012 basin. H034 lifts the unit to row-vector routes and learns sibling failure even more sharply, but first-order row-route edits still fail action stress and reveal an H024 false-positive rollback mode. The missing piece is now why the exact H012 phase is state-visible but not locally improvable: the next breakthrough must learn a direct H012-vs-sibling classifier or combinatorial phase solver, not another smooth continuation, scalar gate, target-level calibration wrapper, same-subject memory regularizer, cellwise edit, or row-route top-k edit.

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
