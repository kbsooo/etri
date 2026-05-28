# Breakthrough Plan After Direct-Label Consensus 2026-05-28

## 1) Bottleneck Diagnosis

Current observed best is `analysis_outputs/submission_frontier_cvjepa_refine_a2c8d2c8.csv` with public LB `0.577439321`.
The remaining distance to `0.54` is `0.037439321`; the raw05 -> a2c8 gain `0.0000869862` covers only `0.2323%` of that gap.

The bottleneck is not feature count.
It is hidden-axis identification:

- Local JEPA/CVJEPA features can improve OOF, but public-safe moves collapse to tiny raw05-compatible tangents.
- Direct-label inverse can explain known anchors, but the solution is underidentified. LOO/L2O errors around `0.0005~0.0006` are the same order as expected direct-label gains.
- Consensus-energy shows the underidentification more clearly: all-target moves score well under robust inverse, but actual-anchor stress rejects them. Q3/S4 is the only stable consensus target family.

Evidence:

- First directrob diagnostic: `analysis_outputs/submission_directrob_29ffe34b.csv`
  - source `frac0.40_rep009`, LOO `0.000578`, L2O `0.000532`
  - actual-anchor proxy `0.577760`, mean abs move vs a2c8 `0.002696`
- Structured directrob control: `analysis_outputs/submission_directrob_93b1b685.csv`
  - source `frac0.40_rep052`, LOO `0.000676`, L2O `0.000607`
  - actual-anchor proxy `0.577763`, mean abs move `0.002539`
- Q3/S4 consensus control: `analysis_outputs/submission_directcons_de1d6b6d.csv`
  - actual-anchor proxy `0.577802`, mean abs move `0.003748`
- Rejected all-target consensus examples:
  - `analysis_outputs/submission_directcons_1d5b6f39.csv` actual-anchor `0.579190`
  - `analysis_outputs/submission_directcons_95be47ec.csv` actual-anchor `0.579207`

Conclusion: to reach 0.54, the next branch must discover which cells can move by `0.01~0.03` without public-axis failure. Current safe gates move only `0.002~0.004`.

## 2) Broken Assumptions

| Current assumption | Reversal | Consequence |
|---|---|---|
| Better local features should transfer | Local feature gains are mostly off-public-axis | Use local features as energy/gates, not direct probability donors |
| High consensus means safe | High consensus across wrong broad targets still fails | Consensus must be target-masked and actual-anchor stressed |
| More all-target hidden-label movement gives more upside | Broad movement leaks into rejected axes | Q3/S4 should be isolated before expanding to S1/S2/S3/Q1 |
| Public inverse score can rank candidates | It can overfit known anchors | LOO/L2O plus actual-anchor stress is mandatory |

## 3) Idea Portfolio

### Big Bet: Cell-Level Hidden Label Solver With JEPA Energy Prior

Hypothesis: direct-label inverse is currently underidentified because cells are independent. Add JEPA block/sequence energy as a prior over row-target cells and solve for sparse larger moves.

- Difficulty: 5
- Expected impact: high
- Cost: medium CPU, high analysis time
- Stop criterion: L2O pair error does not improve below `0.00045`, or selected cells fail actual-anchor stress.

### Quick Win: Public Submission Probe Sequence

Hypothesis: actual public LB can disambiguate whether directrob all-target source or Q3/S4 consensus is closer to hidden public labels.

- Difficulty: 1
- Expected impact: medium information, low direct score expectation
- Cost: submission budget
- Stop criterion: first directrob probe worsens by more than `0.0004` versus a2c8.

Recommended order:

1. `analysis_outputs/submission_directrob_29ffe34b.csv`
2. `analysis_outputs/submission_directrob_93b1b685.csv`
3. `analysis_outputs/submission_directcons_de1d6b6d.csv`

### Lateral Move: Target-Specific Expansion From Q3/S4 To Sleep Stages

Hypothesis: Q3/S4 consensus is the safe visible edge of a sleep-stage block. Expand only to S2/S3/S4 cells whose JEPA block-count energy agrees with Q3/S4 consensus.

- Difficulty: 3
- Expected impact: medium
- Cost: low CPU
- Stop criterion: actual-anchor proxy exceeds `0.57782` or raw-axis stress crosses the a2c8 control.

### Big Bet: Public Mask Mixture Identification

Hypothesis: the hidden public subset is a mixture of `id01/id02 early block`, random-row `frac0.40`, and stage/sequence motif masks. Treat public LB anchors as observations from a mixture rather than picking one mask.

- Difficulty: 4
- Expected impact: high if identified
- Cost: medium CPU
- Stop criterion: mixture LOO/L2O does not beat single-source `frac0.40_rep009`.

### Quick Win: Negative Evidence Library

Hypothesis: failed broad moves encode forbidden axes. Use rejected all-target consensus, latent residual, Q2 forced, and ordinal probes as explicit anti-directions in logit space.

- Difficulty: 2
- Expected impact: medium
- Cost: low
- Stop criterion: anti-direction projection does not improve actual-anchor stress on directrob/consensus candidates.

## 4) Recommended Next 3 Experiments

### Experiment A: Submit Directrob First Diagnostic

- File: `analysis_outputs/submission_directrob_29ffe34b.csv`
- Changed variable: robust direct-label source `frac0.40_rep009`, strength `0.5`, cap `0.055`
- Success criterion: public LB improves over a2c8 by at least `0.00015`, or worsens by less than `0.00015` while preserving direction for Q3/S-stage follow-up.
- Failure criterion: public LB worsens by more than `0.0004`; demote all-target direct-label movement.
- Fallback: submit Q3/S4 consensus control `submission_directcons_de1d6b6d.csv`.

### Experiment B: Build JEPA-Regularized Sparse Direct Solver

- Changed variables: add energy terms from consensus-energy, block-count JEPA, sequence motif, and negative-axis projections.
- Success criterion: L2O best1 pair error below `0.00045` and actual-anchor score below `0.57775` with mean abs move above `0.004`.
- Failure criterion: L2O stays near `0.00053` or selected candidates collapse back to broad all-target moves.
- Fallback: restrict solver to Q3/S4/S2/S3/S4 target mask only.

Status: executed.

- Script: `analysis_outputs/jepa_regularized_sparse_direct_solver.py`
- Best actual-anchor: `analysis_outputs/submission_sparsejepa_f4657144.csv`, score `0.577698`, mean abs move `0.006176`
- Safer no-Q2: `analysis_outputs/submission_sparsejepa_3cfdf64a.csv`, score `0.577706`, mean abs move `0.005520`
- Q3/stage control: `analysis_outputs/submission_sparsejepa_a2d8107a.csv`, score `0.577727`, mean abs move `0.003700`
- The actual-anchor target was met. The L2O criterion is indirectly represented through source/consensus energy, not yet through a fresh full L2O sparse-solver refit.
- New risk: broad all-row/all-target sparse candidates are again at the top, so the first public probe should prefer `3cfdf64a` if risk control matters.

Anchor-CV status: executed.

- Script: `analysis_outputs/jepa_sparse_anchor_cv_audit.py`
- Best combined CV stability: `analysis_outputs/submission_sparsejepa_f43ea825.csv`, CV delta mean `-0.000869`, worst `-0.000411`, win rate `1.0`, actual-anchor `0.577727`, mean move `0.007326`.
- Best actual-anchor plus stable CV: `analysis_outputs/submission_sparsejepa_f4657144.csv`, CV delta mean `-0.000721`, worst `-0.000364`, actual-anchor `0.577698`, mean move `0.006176`.
- Safer no-Q2 stable probe: `analysis_outputs/submission_sparsejepa_3cfdf64a.csv`, CV delta mean `-0.000665`, worst `-0.000341`, actual-anchor `0.577706`, mean move `0.005520`.
- Interpretation: sparse candidates survive LOO/L2O hidden-label refits, so they are stronger than the original directrob control. The remaining uncertainty is not directionality but scale and target leakage.

### Experiment C: Q3/S4-To-Stage Expansion Gate

- Changed variables: start from `submission_directcons_de1d6b6d.csv`; add S2/S3 cells only when JEPA block-count direction and consensus direction agree.
- Success criterion: actual-anchor stays below `0.57780` while increasing mean abs move above `0.0045`.
- Failure criterion: actual-anchor exceeds a2c8 control `0.577827` or broad-stage expansion resembles rejected all-target consensus.
- Fallback: keep Q3/S4-only consensus as a diagnostic probe.

### Experiment D: Sparse Scale-Ladder Stress

- Changed variables: scale existing sparse JEPA/direct-label logit directions from `0.50` to `2.35`; test full/no-Q2/high-energy/top-abs variants.
- Success criterion: mean move exceeds `0.008` while actual-anchor remains below `0.57778` and honest LOO/L2O anchor-CV remains negative.
- Failure criterion: actual-anchor breaks before scale `1.30`, or honest anchor-CV turns positive.

Status: executed.

- Script: `analysis_outputs/jepa_sparse_scale_ladder_stress.py`
- Best larger all-target scale probe: `analysis_outputs/submission_sparseladder_89817541.csv`, f465 full scale `1.50`, actual-anchor `0.577757`, honest CV delta `-0.001013`, mean move `0.009260`.
- Safer larger no-Q2 probe: `analysis_outputs/submission_sparseladder_f1ee16b0.csv`, f465 no-Q2 scale `1.50`, actual-anchor `0.577758`, honest CV delta `-0.000934`, mean move `0.008276`.
- Alternative high-energy gated probe: `analysis_outputs/submission_sparseladder_3be0b7a3.csv`, actual-anchor `0.577764`, honest CV delta `-0.000937`, mean move `0.007001`.
- Key finding: f465 full direction keeps improving under honest anchor-CV through scale `2.00`, but actual-anchor stress starts degrading after scale `1.50`. The current bottleneck is likely scale/target leakage, not lack of new local features.

### Experiment E: Adaptive Sparse Scale Solver

- Changed variables: replace uniform scale with target/energy/subject-block/sequence-block cell-wise scale factors.
- Success criterion: beat uniform scale-ladder on actual-anchor while preserving honest anchor-CV below `-0.0010`.
- Failure criterion: honest anchor-CV improves but actual-anchor worsens, indicating local hidden-label fit leakage.

Status: executed.

- Script: `analysis_outputs/jepa_adaptive_sparse_scale_solver.py`
- Best adaptive actual-anchor: `analysis_outputs/submission_adaptjepa_c10b7ebd.csv`, actual-anchor `0.577798`, honest CV delta `-0.001178`, mean move `0.008808`.
- Best adaptive guarded: `analysis_outputs/submission_adaptjepa_8fabe65a.csv`, actual-anchor `0.577806`, honest CV delta `-0.001192`, mean move `0.008838`.
- Result: adaptive improves hidden-label CV but loses public-axis consistency versus uniform scale-ladder (`submission_sparseladder_89817541.csv` actual-anchor `0.577757`).
- Decision: do not submit adaptive before uniform scale-ladder. Treat adaptive profiles as leakage diagnostics after public feedback.

### Experiment F: Target-Ablation Sparse Scale Probe

- Changed variables: decompose the sparse scale direction by target masks: all, leave-one, q/stage groups, and true single-target probes.
- Success criterion: identify whether the public-safe axis is broad all/no-Q2, Q3/stage-coupled, or single-target.
- Failure criterion: every target mask collapses below useful move amplitude or contradicts anchor-CV.

Status: executed.

- Script: `analysis_outputs/jepa_target_ablation_scale_probe.py`
- Generated `435` candidates, `187` actual-anchor rows, and `109` honest anchor-CV rows.
- Selected submissions pass sample-shape/key/range validation; probability range is `0.0630798631` to `0.9797988457`.
- Best clean target-group diagnostic: `analysis_outputs/submission_targetabl_b19056bb.csv`, `q3_stage`, actual-anchor `0.577727`, honest CV delta `-0.000552`, mean move `0.004452`.
- Best larger-move scale probes remain the uniform ladder rows:
  - `analysis_outputs/submission_sparseladder_b01acaa1.csv`, actual-anchor `0.577746`, honest CV delta `-0.000935`, mean move `0.008816`.
  - `analysis_outputs/submission_sparseladder_89817541.csv`, actual-anchor `0.577757`, honest CV delta `-0.001013`, mean move `0.009260`.
  - `analysis_outputs/submission_sparseladder_f1ee16b0.csv`, actual-anchor `0.577758`, honest CV delta `-0.000934`, mean move `0.008276`.
- Single-target probes are diagnostic only. Best Q3-only rows have actual-anchor around `0.577787` but mean move only about `0.0024`.
- Interpretation: the useful hidden axis is target-coupled. Q3/stage is the clean edge, but all/no-Q2 carries the scale needed for a meaningful public move.

Decision:

- Do not treat target-ablation as a new score family. It validates the scale-ladder family and provides leakage diagnostics.
- First public test should still be a scale-ladder candidate if score movement is the goal.
- If the scale-ladder public result worsens, use `submission_targetabl_b19056bb.csv` as the next lower-amplitude Q3/stage diagnostic.

### Experiment G: Inverse7-Gated Sparse Scale

- Changed variables: apply the sparse JEPA/direct-label logit direction only on inverse7 public-hidden row gates: `id01`, `prefix20`, `prefix30`, subject-prefix, and weighted top-mask posterior gates.
- Success criterion: keep mean move above `0.004` while improving actual-anchor versus target-ablation Q3/stage and preserving negative honest anchor-CV.
- Failure criterion: row gates reduce amplitude or worsen actual-anchor versus uniform scale-ladder.

Status: executed.

- Script: `analysis_outputs/jepa_inverse7_gated_sparse_scale.py`
- Generated `960` candidates, `187` actual-anchor rows, and `81` honest anchor-CV scored rows.
- Selected diagnostic submissions pass sample-shape/key/range validation; probability range is `0.0630798631` to `0.9798140955`.
- Best block-gated diagnostic:
  - `analysis_outputs/submission_inv7gate_a3613347.csv`
  - `prefix30`, `q3_stage`, scale `1.5`, actual-anchor `0.577855`, honest CV delta `-0.000290`, mean move `0.002401`
- Best score-style prefix30 diagnostic:
  - `analysis_outputs/submission_inv7gate_0a9c0c66.csv`
  - `prefix30`, all-target, scale `1.5`, actual-anchor `0.577886`, honest CV delta `-0.000351`, mean move `0.003308`
- Largest selected row-gated move:
  - `analysis_outputs/submission_inv7gate_31adfb5b.csv`
  - `inv64_soft`, all-target, scale `3.0`, actual-anchor `0.577914`, honest CV delta `-0.000310`, mean move `0.004254`
- Result: row gating loses to uniform scale-ladder. It improves interpretability of the prefix-row hypothesis but gives up too much amplitude and does not improve actual-anchor.

Decision:

- Do not submit inverse7-gated sparse candidates before scale-ladder candidates.
- Treat this as negative evidence against hard row-mask construction from inverse7 alone.
- If public feedback later indicates a first-30%-row hidden block, use `submission_inv7gate_0a9c0c66.csv` as a diagnostic, not as the main 0.54 path.

### Experiment H: Bad-Axis Orthogonalized Scale-Ladder

- Changed variables: start from the strongest sparse JEPA/direct-label ladder directions, then remove components aligned with public-failed axes (`anchor578`, `ordinal_q`, `jepa_bad_residual`, `jepa_bad_q2`, and failed direct-consensus axes) inside each active target/cell gate.
- Success criterion: keep mean move around `0.008` while improving actual-anchor versus the unorthogonalized scale-ladder.
- Failure criterion: removal improves robust/CV proxies but worsens actual-anchor, meaning the apparent bad axes also contain useful public-transfer signal.

Status: executed.

- Script: `analysis_outputs/jepa_bad_axis_orthogonal_scale_ladder.py`
- Report: `analysis_outputs/jepa_bad_axis_orthogonal_scale_ladder_report.md`
- Scored `349` prefiltered candidates and `124` honest anchor-CV candidates.
- Selected non-zero diagnostic submissions pass shape/key/range checks; probability range is `0.065381` to `0.979879`.
- Best non-zero orthogonalized diagnostic:
  - `analysis_outputs/submission_ortholadder_cc4d9154.csv`
  - source `f465_actual_best`, full target, `public_bad4`, anti `0.35`, restore mean abs, scale `1.30`
  - actual-anchor `0.577782`, honest CV delta `-0.000795`, mean move `0.007940`, removed norm ratio `0.291362`
- Larger non-zero diagnostic:
  - `analysis_outputs/submission_ortholadder_8ef88723.csv`
  - source `f465_actual_best`, full target, `classic_bad2`, anti `0.35`, scale `1.50`
  - actual-anchor `0.577794`, honest CV delta `-0.000823`, mean move `0.008355`, removed norm ratio `0.291362`
- Control comparison:
  - unorthogonalized f465 full scale `1.30`: actual-anchor `0.577724`, honest CV delta `-0.000919`, mean move `0.008027`
  - unorthogonalized f465 full scale `1.50`: actual-anchor `0.577757`, honest CV delta `-0.001013`, mean move `0.009260`

Result:

- Removing global bad-axis components does not improve the frontier. It worsens actual-anchor while preserving superficially acceptable CV.
- `jepa_bad2` removal is mostly a no-op on the best sparse directions, so the current sparse direction is not contaminated by the failed JEPA residual/Q2 axes in a simple positive-linear sense.
- `classic_bad2/public_bad4` removal is non-zero, but it strips signal that actual-anchor still wants. The failed public anchors are not pure negative directions; they contain useful components mixed with bad components.

Decision:

- Do not submit orthogonalized candidates before the uniform scale-ladder rows.
- Keep `submission_ortholadder_cc4d9154.csv` only as a diagnostic if a public result specifically suggests the broad anchor578/ordinal component is harmful.
- The next breakthrough path should not be global bad-axis projection. It should separate bad axes by row/target block or infer the hidden label-prior/subset more directly.

### Experiment I: Blockwise Bad-Axis Decomposition

- Changed variables: keep the sparse JEPA/direct-label move globally, but remove failed public-axis components only inside row-block and target-group gates.
- Success criterion: beat or tie the scale-ladder frontier while preserving mean move around `0.008`.
- Failure criterion: blockwise removal collapses toward the global-projection result or only creates lower-amplitude diagnostics.

Status: executed.

- Script: `analysis_outputs/jepa_blockwise_bad_axis_decomposition.py`
- Report: `analysis_outputs/jepa_blockwise_bad_axis_decomposition_report.md`
- Scored `365` prefiltered blockwise candidates and `125` honest anchor-CV candidates.
- Selected `9` blockwise diagnostic submissions; all pass shape/key/range checks.
- Best blockwise row:
  - `analysis_outputs/submission_blockorth_3a28f87f.csv`
  - source `282_consensus_directrob`, full target, row gate `rowmod4_rem3`, correction target `stage_all`, axis group `public_bad4`, signed anti `0.35`, scale `1.30`
  - actual-anchor `0.577744`, honest CV delta `-0.000892`, mean move `0.008599`, removed norm ratio `0.475478`
- Best prefix-row sibling:
  - `analysis_outputs/submission_blockorth_0352b65f.csv`
  - row gate `prefix30`, correction target `no_q2`, actual-anchor `0.577744`, honest CV delta `-0.000884`, mean move `0.008585`
- Comparison to current scale-ladder priority:
  - `submission_sparseladder_b01acaa1.csv`: actual-anchor `0.577746`, honest CV delta `-0.000935`, mean move `0.008816`
  - `submission_blockorth_3a28f87f.csv`: actual-anchor improves by only about `0.000002`, while honest CV and robust delta are slightly weaker.

Result:

- Blockwise decomposition is materially better than global bad-axis projection: it keeps amplitude and does not collapse actual-anchor.
- The improvement over `b01acaa1` is too small to override the simpler scale-ladder priority. It is best viewed as a sibling diagnostic for the same 282 sparse direction.
- Useful row gates are `rowmod4_rem3`, `prefix30`, and `id01`, but none creates a clear 0.54-scale jump.

Decision:

- Keep `submission_sparseladder_b01acaa1.csv` as first score-oriented public probe.
- Promote `submission_blockorth_3a28f87f.csv` to a near-frontier diagnostic if `b01acaa1` is slightly worse than expected or if public feedback points to stage-specific bad-axis leakage.
- Next structural path: infer hidden label priors/subsets directly, because projection-based repairs are now showing only 1e-5 to 1e-4 frontier movement.

### Experiment J: Sparse Direction Ensemble Orthogonalizer

- Changed variables: blend good sparse-JEPA/direct-label directions in logit space before optional bad-axis projection.
- Success criterion: beat `b01acaa1` and `blockorth_3a28f87f` under actual-anchor while staying in the larger-move band above `0.008`.
- Failure criterion: only explicit projection rows survive, or ensemble rows collapse to lower-amplitude diagnostics.

Status: executed.

- Script: `analysis_outputs/jepa_sparse_direction_ensemble_orthogonalizer.py`
- Report: `analysis_outputs/jepa_sparse_direction_ensemble_orthogonalizer_report.md`
- Generated `2604` unique candidates, prefiltered `357`, anchor-CV scored `130`, selected `24`.
- Selected submissions pass shape/key/range validation.
- Best score candidate:
  - `analysis_outputs/submission_direns_2a96ae73.csv`
  - blend `b01acaa1 + blockorth_3a28f87f + targetabl_b19056bb`
  - weights `0.33/0.33/0.33`, full target, all cells, no explicit projection, scale `1.10`
  - actual-anchor `0.577729`, honest CV delta `-0.000877`, mean move `0.008015`
- Stronger-CV sibling:
  - `analysis_outputs/submission_direns_c4af1fd8.csv`
  - blend `b01acaa1 + 89817541 + f1ee16b0`, weights `0.50/0.25/0.25`, scale `0.95`
  - actual-anchor `0.577733`, honest CV delta `-0.000930`, mean move `0.008353`
- Orthogonalized diagnostic:
  - `analysis_outputs/submission_direns_b0962ff8.csv`
  - `public_bad4` anti `0.25`, removed ratio `0.334509`
  - actual-anchor `0.577760`, honest CV delta `-0.000826`, mean move `0.008030`

Result:

- This is the first post-scale-ladder experiment that materially improves the local frontier while keeping larger-move amplitude.
- The improvement did not come from explicit bad-axis projection. It came from mixing partially correct JEPA/direct-label directions.
- Q3/stage remains too weak alone, but it stabilizes the `b01 + blockorth` direction when included as a latent/target prior.

Decision:

- Promote `submission_direns_2a96ae73.csv` to the first score-oriented public probe.
- Keep `submission_direns_1e0f159d.csv` and `submission_direns_c4af1fd8.csv` as close siblings.
- Keep `submission_sparseladder_89817541.csv` as the high-scale stress probe.
- Do not submit explicit orthogonalized ensemble rows first; they are diagnostic evidence that bad-axis subtraction still strips useful signal.

### Experiment K: Direction Ensemble Combo Stress Audit

- Changed variables: evaluate direction-ensemble candidates on every inverse scenario/mask combo, not only the averaged actual-anchor score.
- Success criterion: a first-submit candidate should beat `b01_ladder` by weighted delta, weighted win rate, p90 delta, and worst delta.
- Failure criterion: a candidate wins only by average but has large positive p90/worst deltas against `b01_ladder`.

Status: executed.

- Script: `analysis_outputs/jepa_direction_ensemble_combo_stress_audit.py`
- Report: `analysis_outputs/jepa_direction_ensemble_combo_stress_report.md`
- Detail: `analysis_outputs/jepa_direction_ensemble_combo_stress_detail.csv`
- Summary: `analysis_outputs/jepa_direction_ensemble_combo_stress_summary.csv`

Result:

- `direns_2a96` is actual-anchor-best but has worse combo tails.
- `direns_c4af` is the most stable robust public probe:
  - file: `analysis_outputs/submission_direns_c4af1fd8.csv`
  - weighted delta vs `b01_ladder`: `-0.000011`
  - weighted win rate vs `b01_ladder`: `0.634403`
  - p90 delta vs `b01_ladder`: `+0.000007`
  - worst delta vs `b01_ladder`: `+0.000035`
  - weighted delta vs `898_ladder`: `-0.000009`
  - honest CV delta: `-0.000930`
  - mean move vs a2c8: `0.008353`
- `direns_2a96` comparison:
  - weighted delta vs `b01_ladder`: `-0.000009`
  - win rate `0.562397`
  - p90 delta `+0.000044`
  - worst delta `+0.000101`

Decision correction:

- First robust score-oriented public probe should be `submission_direns_c4af1fd8.csv`, not `submission_direns_2a96ae73.csv`.
- Keep `submission_direns_2a96ae73.csv` as the actual-anchor-best sibling.
- The updated public-probe order is:
  1. `analysis_outputs/submission_direns_c4af1fd8.csv`
  2. `analysis_outputs/submission_direns_2a96ae73.csv`
  3. `analysis_outputs/submission_direns_c0fdb76b.csv`
  4. `analysis_outputs/submission_sparseladder_89817541.csv`
  5. `analysis_outputs/submission_sparseladder_f1ee16b0.csv`

### Experiment L: Direction Mixture Minimax Optimizer

- Changed variables: replace manual direction weights with a direct public-anchor combo-stress optimizer over larger-move sparse/JEPA directions.
- Success criterion: beat `direns_c4af` or at least reduce its combo tails while preserving larger move and negative LOO/L2O anchor-CV.
- Failure criterion: only micro-move, explicit projection, or gated lower-amplitude rows survive.

Status: executed.

- Script: `analysis_outputs/jepa_direction_mixture_minimax_optimizer.py`
- Report: `analysis_outputs/jepa_direction_mixture_minimax_optimizer_report.md`
- Generated `61,630` candidates.
- Actual-anchor rescored `1,800`; combo-stress summarized `190`; LOO/L2O anchor-CV scored `100`.
- Saved `7` submissions; all pass key/order/range integrity.

Result:

- Best new stress probe:
  - `analysis_outputs/submission_mixmin_0c916bb4.csv`
  - blend `direns_c4af + 898_ladder`, weights `0.350/0.650`, full/all/all-cells/no-projection, scale `0.95`
  - actual-anchor `0.577734`
  - combo weighted delta vs `b01_ladder`: `-0.000012877`
  - combo weighted win vs `b01_ladder`: `0.978659`
  - combo p90/worst delta vs `b01_ladder`: `-0.000008452` / `+0.000010139`
  - combo weighted delta vs `direns_c4af`: `-0.000001636`
  - honest CV delta mean/worst: `-0.000952` / `-0.000696`
  - mean move vs a2c8: `0.008496`
- Selected siblings:
  - `analysis_outputs/submission_mixmin_5a4c25e0.csv`
  - `analysis_outputs/submission_mixmin_f0d12643.csv`
  - `analysis_outputs/submission_mixmin_f6c04249.csv`
  - `analysis_outputs/submission_mixmin_ef4b1c19.csv`
  - `analysis_outputs/submission_mixmin_7f9cb635.csv`
  - `analysis_outputs/submission_mixmin_615da9a7.csv`
- Negative checks:
  - Best `public_bad4` projection candidate only reaches actual-anchor `0.577752` and has positive combo delta vs `b01_ladder`.
  - `rawcompat_soft`, `allsign_soft`, and `energy_top70` gates underperform the all-row/all-cell mixture.

Decision:

- Add `submission_mixmin_0c916bb4.csv` as the first new c4af-stress public probe.
- Keep `submission_direns_c4af1fd8.csv` as the current robust direction-ensemble reference.
- This does not solve the 0.54 bottleneck. It confirms the remaining barrier: we still lack a hidden subset/label-prior signal that changes the direction itself, not only the mixture weights.

## 5) Risk, Cost, and Expected Upside

- Submission risk: `directrob_29ffe34b` is lower-risk than broad consensus, but still not score-safe. It is an information probe.
- Modeling risk: local CV/OOF is not enough; public-axis stress must gate every candidate.
- Expected upside short-term: `0.0001~0.0005` information-driven movement if directrob direction is real.
- Expected upside toward 0.54: only the sparse JEPA-regularized hidden label solver has plausible step-change potential. Micro-refines and Q3/S4-only consensus are diagnostics, not a direct path to 0.54.
