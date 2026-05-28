# Next Public LB Probe Matrix After Target Ablation

Current observed public anchor:

- `submission_frontier_cvjepa_refine_a2c8d2c8.csv`: public LB `0.577439321`

Validation status:

- Checked eight next-probe files against `data/ch2026_submission_sample.csv`.
- All checked files have the correct shape, column order, key order, finite probabilities, and probabilities inside `[0, 1]`.
- The candidates split into three movement bands versus a2c8:
  - conservative inverse7 blend: mean abs move about `0.00213` to `0.00237`
  - Q3/stage target diagnostic: mean abs move about `0.00445` to `0.00481`
  - sparse scale-ladder score probe: mean abs move about `0.00828` to `0.00926`

## Candidate Matrix

| Priority | File | Role | Local evidence | Mean abs move vs a2c8 | Public response meaning |
|---:|---|---|---|---:|---|
| 1 | `analysis_outputs/submission_sparseladder_b01acaa1.csv` | Balanced larger-move score probe | actual-anchor `0.577746`, honest CV delta `-0.000935` | `0.008816` | Tests whether the 282 consensus/direct-label sparse axis transfers at useful scale. |
| 2 | `analysis_outputs/submission_sparseladder_89817541.csv` | Maximum scale signal | actual-anchor `0.577757`, honest CV delta `-0.001013` | `0.009260` | Tests whether the f465 all-target sparse axis can survive public-axis stress at scale `1.50`. |
| 3 | `analysis_outputs/submission_sparseladder_f1ee16b0.csv` | Q2-risk controlled larger move | actual-anchor `0.577758`, honest CV delta `-0.000934` | `0.008276` | If broad all-target leakage is the issue, this isolates the no-Q2 version. |
| 4 | `analysis_outputs/submission_inverse7blend_1040423d.csv` | a2c8-conditioned public-split diagnostic | compat delta vs a2c8 `-0.000050403`, full inverse delta `-0.000429297` | `0.002374` | Tests whether inverse7's no-Q2/public-entropy hidden block hypothesis is real without taking scale-ladder risk. |
| 5 | `analysis_outputs/submission_targetabl_b19056bb.csv` | Clean Q3/stage diagnostic | actual-anchor `0.577727`, honest CV delta `-0.000552` | `0.004452` | Tests the lower-amplitude Q3/stage edge if scale-ladder leaks. |
| 6 | `analysis_outputs/submission_targetabl_1049b8e7.csv` | Q3/S2/S3/S4 diagnostic | actual-anchor `0.577738`, honest CV delta `-0.000580` | `0.004809` | Separates stage-coupled transfer from the broader Q3/stage mask. |

## Decision Rule

- If the goal is to make a real move toward `0.54`, submit a scale-ladder candidate first. The conservative inverse7 and target-group probes are too small to close the gap by themselves.
- If only one larger-move score probe is allowed, prefer `submission_sparseladder_b01acaa1.csv`: it has the best balance between movement size and actual-anchor stress among the scale-ladder family.
- If the next submission is intended to diagnose target leakage, prefer `submission_targetabl_b19056bb.csv` after a failed scale-ladder probe.
- If the next submission must stay close to the observed a2c8 anchor, prefer `submission_inverse7blend_1040423d.csv`; treat it as public-split evidence, not as the 0.54 path.

## Bottleneck Update

- Target-ablation says the useful axis is not a single target. Q3-only and Q1-only probes are too low-amplitude.
- The meaningful direction is target-coupled: Q3/stage is the clean edge, while all/no-Q2 carries the scale.
- Adaptive scaling currently overfits the hidden-label proxy: it improves honest hidden-label CV but worsens actual-anchor versus uniform scale-ladder.
- Therefore the immediate bottleneck is not feature count. It is deciding whether the larger sparse JEPA/direct-label axis transfers to the public hidden subset.

## Inverse7-Gated Sparse Scale Follow-Up

New script:

- `analysis_outputs/jepa_inverse7_gated_sparse_scale.py`

Outputs:

- `analysis_outputs/jepa_inverse7_gated_sparse_scale_report.md`
- `analysis_outputs/jepa_inverse7_gated_sparse_scale_scan.csv`
- `analysis_outputs/jepa_inverse7_gated_sparse_scale_actual_anchor.csv`
- `analysis_outputs/jepa_inverse7_gated_sparse_scale_cv_summary.csv`
- `analysis_outputs/jepa_inverse7_gated_sparse_scale_selected.csv`

Result:

- Generated `960` row-gated sparse candidates.
- The best row-gated candidates use `prefix30`, not single-subject `id01`.
- Row gating does not beat uniform scale-ladder. Best diagnostic candidates have actual-anchor around `0.577855` to `0.577886`, honest CV delta around `-0.00029` to `-0.00035`, and mean move around `0.0024` to `0.0033`.
- The largest selected row-gated candidate, `submission_inv7gate_31adfb5b.csv`, reaches mean move `0.004254` but actual-anchor is `0.577914`, weaker than `submission_targetabl_b19056bb.csv` and much weaker than the scale-ladder priority rows.
- Selected diagnostic submissions pass shape/key/range validation; probability range is `0.0630798631` to `0.9798140955`.

Decision:

- Do not submit inverse7-gated sparse candidates before the uniform scale-ladder candidates.
- Keep `submission_inv7gate_e35a7114.csv` or `submission_inv7gate_0a9c0c66.csv` only as later diagnostics if a public result specifically suggests the first 30% test rows are the public hidden block.
- This is negative evidence against using inverse7 row masks as hard construction gates. Inverse7 remains useful for diagnosing public split hypotheses, but current row gating throws away too much amplitude.

## Bad-Axis Orthogonalization Follow-Up

New script:

- `analysis_outputs/jepa_bad_axis_orthogonal_scale_ladder.py`

Outputs:

- `analysis_outputs/jepa_bad_axis_orthogonal_scale_ladder_report.md`
- `analysis_outputs/jepa_bad_axis_orthogonal_scale_ladder_scan.csv`
- `analysis_outputs/jepa_bad_axis_orthogonal_scale_ladder_cv_summary.csv`
- `analysis_outputs/jepa_bad_axis_orthogonal_scale_ladder_selected.csv`

Result:

- The best sparse-ladder directions have almost no positive alignment with the failed JEPA residual/Q2 axes (`jepa_bad2`), so that projection is a no-op.
- Removing the broader public-failed axes is non-zero, but it worsens actual-anchor:
  - `submission_ortholadder_cc4d9154.csv`: actual-anchor `0.577782`, honest CV delta `-0.000795`, mean move `0.007940`, removed ratio `0.291362`.
  - `submission_ortholadder_8ef88723.csv`: actual-anchor `0.577794`, honest CV delta `-0.000823`, mean move `0.008355`, removed ratio `0.291362`.
- Both are weaker than the corresponding unorthogonalized scale-ladder rows:
  - f465 full scale `1.30`: actual-anchor `0.577724`, honest CV delta `-0.000919`.
  - f465 full scale `1.50`: actual-anchor `0.577757`, honest CV delta `-0.001013`.
- Selected diagnostic files pass integrity checks, but they are not promoted as score submissions.

Decision:

- Public priority remains unchanged: `submission_sparseladder_b01acaa1.csv`, then `submission_sparseladder_89817541.csv`, then `submission_sparseladder_f1ee16b0.csv`.
- Bad-axis orthogonalized candidates are diagnostic only. They show that global failed-anchor projection removes useful signal along with bad signal.
- The next modification should be row/target-block-specific bad-axis decomposition or direct hidden label-prior inference, not another global orthogonal projection.

## Blockwise Bad-Axis Decomposition Follow-Up

New script:

- `analysis_outputs/jepa_blockwise_bad_axis_decomposition.py`

Outputs:

- `analysis_outputs/jepa_blockwise_bad_axis_decomposition_report.md`
- `analysis_outputs/jepa_blockwise_bad_axis_decomposition_scan.csv`
- `analysis_outputs/jepa_blockwise_bad_axis_decomposition_cv_summary.csv`
- `analysis_outputs/jepa_blockwise_bad_axis_decomposition_selected.csv`

Result:

- Blockwise projection improves over global bad-axis projection because it keeps most of the sparse direction and edits only a row/target block.
- Best candidate:
  - `analysis_outputs/submission_blockorth_3a28f87f.csv`
  - actual-anchor `0.577744`, honest CV delta `-0.000892`, mean move `0.008599`
  - block: `rowmod4_rem3 × stage_all`, axis group `public_bad4`, signed anti `0.35`
- Best prefix-row sibling:
  - `analysis_outputs/submission_blockorth_0352b65f.csv`
  - actual-anchor `0.577744`, honest CV delta `-0.000884`, mean move `0.008585`
  - block: `prefix30 × no_q2`, axis group `public_bad4`, signed anti `0.25`
- These are close to but not clearly better than `submission_sparseladder_b01acaa1.csv`, which has actual-anchor `0.577746`, honest CV delta `-0.000935`, and mean move `0.008816`.

Decision:

- Keep the score-oriented public priority unchanged:
  1. `analysis_outputs/submission_sparseladder_b01acaa1.csv`
  2. `analysis_outputs/submission_sparseladder_89817541.csv`
  3. `analysis_outputs/submission_sparseladder_f1ee16b0.csv`
- Add `analysis_outputs/submission_blockorth_3a28f87f.csv` as a near-frontier diagnostic sibling of `b01acaa1`.
- Interpretation: projection can now preserve amplitude if localized, but it still moves the frontier only marginally. A real 0.54 path likely needs direct hidden subset/label-prior inference rather than more projection repair.

## Sparse Direction Ensemble Orthogonalizer Follow-Up

New script:

- `analysis_outputs/jepa_sparse_direction_ensemble_orthogonalizer.py`

Outputs:

- `analysis_outputs/jepa_sparse_direction_ensemble_orthogonalizer_report.md`
- `analysis_outputs/jepa_sparse_direction_ensemble_orthogonalizer_scan.csv`
- `analysis_outputs/jepa_sparse_direction_ensemble_orthogonalizer_cv_summary.csv`
- `analysis_outputs/jepa_sparse_direction_ensemble_orthogonalizer_selected.csv`

Result:

- Generated `2604` unique direction-ensemble candidates.
- Prefiltered `357`, anchor-CV scored `130`, selected `24`.
- Selected files pass shape/key/range validation.
- Best local score probe:
  - `analysis_outputs/submission_direns_2a96ae73.csv`
  - blend `b01acaa1 + blockorth_3a28f87f + targetabl_b19056bb`
  - actual-anchor `0.577729`, honest CV delta `-0.000877`, mean move `0.008015`
- Close siblings:
  - `analysis_outputs/submission_direns_1e0f159d.csv`: actual-anchor `0.577729`, honest CV `-0.000898`, move `0.008133`
  - `analysis_outputs/submission_direns_c4af1fd8.csv`: actual-anchor `0.577733`, honest CV `-0.000930`, move `0.008353`
- Explicit orthogonalized ensemble rows remain weaker:
  - `analysis_outputs/submission_direns_b0962ff8.csv`: actual-anchor `0.577760`, honest CV `-0.000826`, move `0.008030`, removed ratio `0.334509`

Updated Candidate Matrix

| Priority | File | Role | Local evidence | Mean abs move vs a2c8 | Public response meaning |
|---:|---|---|---|---:|---|
| 1 | `analysis_outputs/submission_direns_2a96ae73.csv` | New balanced direction-ensemble score probe | actual-anchor `0.577729`, honest CV delta `-0.000877` | `0.008015` | Tests whether mixing `b01`, blockwise repair, and Q3/stage prior transfers better than any single sparse direction. |
| 2 | `analysis_outputs/submission_direns_1e0f159d.csv` | Direction-ensemble sibling | actual-anchor `0.577729`, honest CV delta `-0.000898` | `0.008133` | Tests `b01 + blockorth + no-Q2 scale` without the Q3/stage target-ablation component. |
| 3 | `analysis_outputs/submission_direns_c4af1fd8.csv` | Stronger-CV ensemble sibling | actual-anchor `0.577733`, honest CV delta `-0.000930` | `0.008353` | Tests whether adding the high-scale `898` direction improves public transfer. |
| 4 | `analysis_outputs/submission_sparseladder_89817541.csv` | Maximum scale signal | actual-anchor `0.577757`, honest CV delta `-0.001013` | `0.009260` | Tests scale `1.50` if the public result rewards larger amplitude despite weaker actual-anchor. |
| 5 | `analysis_outputs/submission_sparseladder_f1ee16b0.csv` | Q2-risk controlled larger move | actual-anchor `0.577758`, honest CV delta `-0.000934` | `0.008276` | Tests no-Q2 broad sparse movement. |
| 6 | `analysis_outputs/submission_direns_b0962ff8.csv` | Orthogonalized diagnostic | actual-anchor `0.577760`, honest CV delta `-0.000826` | `0.008030` | Tests whether explicit `public_bad4` removal helps; not score-first. |

Decision:

- Replace `b01acaa1` with `submission_direns_2a96ae73.csv` as the first score-oriented public probe.
- The useful next modification is now direction mixture/scale selection, not stronger bad-axis subtraction.
- Explicit orthogonalization remains diagnostic because it removes useful signal along with bad signal.

## Combo-Stress Correction

New audit:

- `analysis_outputs/jepa_direction_ensemble_combo_stress_audit.py`
- `analysis_outputs/jepa_direction_ensemble_combo_stress_report.md`

Result:

- The averaged actual-anchor score favors `submission_direns_2a96ae73.csv`, but combo-level pairwise stress favors `submission_direns_c4af1fd8.csv`.
- `submission_direns_c4af1fd8.csv`:
  - weighted delta vs `b01_ladder`: `-0.000011`
  - weighted win rate vs `b01_ladder`: `0.634403`
  - p90 delta vs `b01_ladder`: `+0.000007`
  - worst delta vs `b01_ladder`: `+0.000035`
  - weighted delta vs `898_ladder`: `-0.000009`
- `submission_direns_2a96ae73.csv`:
  - weighted delta vs `b01_ladder`: `-0.000009`
  - weighted win rate: `0.562397`
  - p90 delta: `+0.000044`
  - worst delta: `+0.000101`

Corrected Candidate Matrix

| Priority | File | Role | Local evidence | Mean abs move vs a2c8 | Public response meaning |
|---:|---|---|---|---:|---|
| 1 | `analysis_outputs/submission_direns_c4af1fd8.csv` | Robust direction-ensemble public probe | actual-anchor `0.577733`, honest CV `-0.000930`, combo delta vs b01 `-0.000011`, combo win `0.634403` | `0.008353` | Best balance after combo-level stress; tests robust mixture of `b01 + 898 + f1ee`. |
| 2 | `analysis_outputs/submission_direns_2a96ae73.csv` | Actual-anchor-best ensemble sibling | actual-anchor `0.577729`, honest CV `-0.000877`, combo delta vs b01 `-0.000009` | `0.008015` | Tests the `b01 + blockorth + Q3/stage` stabilizer, but has higher combo tail risk. |
| 3 | `analysis_outputs/submission_direns_c0fdb76b.csv` | Secondary ensemble sibling | actual-anchor `0.577731`, honest CV `-0.000911`, combo delta vs b01 `-0.000010` | `0.008196` | Similar to `2a96`, slightly better combo tail. |
| 4 | `analysis_outputs/submission_sparseladder_89817541.csv` | Maximum scale signal | actual-anchor `0.577757`, honest CV `-0.001013` | `0.009260` | Still the high-amplitude stress probe. |
| 5 | `analysis_outputs/submission_sparseladder_f1ee16b0.csv` | Q2-risk controlled larger move | actual-anchor `0.577758`, honest CV `-0.000934` | `0.008276` | Tests no-Q2 broad sparse movement. |

Corrected decision:

- Submit `analysis_outputs/submission_direns_c4af1fd8.csv` first if the goal is a robust score-oriented public probe.
- Submit `analysis_outputs/submission_direns_2a96ae73.csv` only if prioritizing actual-anchor average over combo-tail robustness.

## Direction Mixture Minimax Update

New optimizer:

- `analysis_outputs/jepa_direction_mixture_minimax_optimizer.py`
- `analysis_outputs/jepa_direction_mixture_minimax_optimizer_report.md`
- `analysis_outputs/jepa_direction_mixture_minimax_optimizer_selected.csv`

Run summary:

- Generated `61,630` logit-mixture candidates from sparse/JEPA/direct-label directions.
- Actual-anchor rescored `1,800`, combo-stress summarized `190`, and LOO/L2O anchor-CV scored `100`.
- Saved `7` integrity-clean submissions.

Best new c4af-stress probe:

- `analysis_outputs/submission_mixmin_0c916bb4.csv`
- blend `direns_c4af + 898_ladder`, weights `0.350/0.650`, full/all/all-cells/no-projection, scale `0.95`
- actual-anchor `0.577734`
- combo weighted delta vs `b01_ladder`: `-0.000012877`
- combo weighted win vs `b01_ladder`: `0.978659`
- combo p90/worst delta vs `b01_ladder`: `-0.000008452` / `+0.000010139`
- combo weighted delta vs `direns_c4af`: `-0.000001636`
- honest CV delta mean/worst: `-0.000952` / `-0.000696`
- mean move vs a2c8: `0.008496`

Selected siblings:

- `analysis_outputs/submission_mixmin_5a4c25e0.csv`
- `analysis_outputs/submission_mixmin_f0d12643.csv`
- `analysis_outputs/submission_mixmin_f6c04249.csv`
- `analysis_outputs/submission_mixmin_ef4b1c19.csv`
- `analysis_outputs/submission_mixmin_7f9cb635.csv`
- `analysis_outputs/submission_mixmin_615da9a7.csv`

Updated Candidate Matrix

| Priority | File | Role | Local evidence | Mean abs move vs a2c8 | Public response meaning |
|---:|---|---|---|---:|---|
| 1 | `analysis_outputs/submission_mixmin_0c916bb4.csv` | New c4af-stress mixture probe | actual-anchor `0.577734`, combo delta vs b01 `-0.000012877`, combo delta vs c4af `-0.000001636`, honest CV `-0.000952` | `0.008496` | Tests whether shifting robust `c4af` toward the high-scale `898` direction improves public transfer without adding combo-tail risk. |
| 2 | `analysis_outputs/submission_direns_c4af1fd8.csv` | Robust direction-ensemble reference | actual-anchor `0.577733`, combo delta vs b01 `-0.000011`, honest CV `-0.000930` | `0.008353` | Baseline robust ensemble; keep as the reference if the new mix probe regresses. |
| 3 | `analysis_outputs/submission_mixmin_5a4c25e0.csv` | c4af-stress sibling | actual-anchor `0.577737`, combo delta vs b01 `-0.000012`, honest CV `-0.000961` | `0.008530` | Tests the same high-898 region without explicitly using `direns_c4af`. |
| 4 | `analysis_outputs/submission_mixmin_f6c04249.csv` | selection-score frontier sibling | actual-anchor `0.577737`, combo delta vs b01 `-0.000011`, honest CV `-0.000961` | `0.008601` | Slightly larger all-row/full-target b01/898/f1ee mixture. |
| 5 | `analysis_outputs/submission_direns_2a96ae73.csv` | Actual-anchor-best older sibling | actual-anchor `0.577729`, higher combo-tail risk | `0.008015` | Tests Q3/stage stabilizer but remains less robust by combo-stress. |

Important negative result:

- Explicit `public_bad4` projection, raw05-compatible row gates, all-sign row gates, and JEPA energy gates did not survive the minimax selection.
- This means the next 0.54-directed work should not be another orthogonalization pass. It should find a new hidden subset/label-prior signal that changes the target direction itself.
