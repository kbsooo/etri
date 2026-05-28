# JEPA Plateau Bottleneck Action Plan

## Current Public Anchor

- Best submitted anchor: `analysis_outputs/submission_frontier_cvjepa_refine_a2c8d2c8.csv`
- Public LB: `0.577439321`
- Important near-control: `jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv`
- Public LB: `0.5775263072`

## Hard Finding

The current bottleneck is not lack of JEPA-style representations. It is that the local/public selector cannot reliably identify which representation movement is aligned with the hidden public subset.

Evidence from `jepa_selector_frontier_audit.py`:

- JEPA-related submissions scanned: `7318`
- Strict resolved-better-than-a2c8 candidates: `0`
- Frontier escape candidates: `86`
- Novel frontier candidates, also moved away from raw05: `15`
- Low-bad-axis plus movement-over-uncertainty candidates: `4013`

This means many candidates move predictions meaningfully, but almost none can be trusted as public-improving under the current stress geometry.

## Why 0.54 Is Not Happening Yet

The current search is mostly producing three kinds of moves:

1. Raw05-compatible micro-moves.
   - They often look safe.
   - They do not create enough new information.
   - They are plateau-preserving, not plateau-breaking.

2. High-OOF JEPA moves.
   - Families like `neural_episode_rawstack`, `blockorth`, and `mixmin` moved a lot.
   - They load heavily on known public-bad axes.
   - These are likely overfitting or misaligned latent directions.

3. Public-repair / cvjepa graft moves.
   - These are the only current novel frontier branch worth keeping.
   - They still fail the strict submission gate.
   - They are useful as representation/gate seeds, not as direct submissions.

## Family-Level Diagnosis

| family | useful read |
| --- | --- |
| `cvjepa` | Best current research branch. Low bad-axis rate is high (`0.966`), and `9` novel escape candidates exist. Still not strict-submit safe. |
| `raw05_jepa` | Many safe-looking candidates, but `0` novel escapes. This branch is mostly rediscovering raw05. |
| `axis_repair` | Small but informative. It can move away from raw05, but strict gate still fails. Useful for bad-axis penalty design. |
| `lejepa` | Current implementation is not working for public. Low-bad-axis rate is only `0.111`, majority-beats rate is `0`. |
| `neural_episode_rawstack` | Strong local/OOF signal but public-risk geometry is bad. Best bad-axis load is `0.116`, above the `0.050` limit. |
| `blockorth` / `mixmin` | Too aligned with known bad public axes. Do not submit directly. |

## Do Not Submit Yet

No current candidate clears the strict gate.

The highest-ranked novel research candidates are:

- `analysis_outputs/submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv`
- `analysis_outputs/submission_public6entropy_raw05_ctx_g030_adcc5520.csv`
- `analysis_outputs/submission_raw05_cvjepa_surprise_graft_b0ba9eec.csv`
- `analysis_outputs/submission_public_repair_rawaxis_s0.875_4bfcf007.csv`
- `analysis_outputs/submission_public_repair_rawaxis_s1.125_45affdb6.csv`

They are research probes, not safe submissions.

## Next Experiments

The next useful JEPA work should be constrained by public-axis geometry from the start.

Required gate for a new candidate family:

- `bad_axis_abs_load <= 0.050`
- `selector_p90_delta_vs_a2c8_public <= 0.00040`
- `beats_a2c8_scenario_rate >= 0.65`
- `mean_abs_move_vs_raw05 >= 0.0014`
- strict resolved-better-than-a2c8 gate should be nonzero before any serious submit.

Priority order:

1. CVJEPA-public6entropy teacher gate.
   - Use the 15 novel frontier candidates as teacher directions.
   - Distill only the directions that are low bad-axis and raw05-novel.
   - Penalize projection onto the known bad axes during candidate construction.

2. LeJEPA targetwise safe rebuild.
   - Do not reuse the current broad LeJEPA submission behavior.
   - Train/apply target-specific blocks, especially Q1/Q3/S3/S4, with an explicit bad-axis penalty.
   - Reject candidates before CSV generation if they violate the gate above.

3. Raw05-compatible output mask only as baseline control.
   - Keep raw05-compatible candidates as calibration controls.
   - Do not spend more search budget on tiny raw05 microblends unless they improve selector reliability.

4. Selector improvement before model expansion.
   - Current direct inverse experiments show hidden subset structure exists, but train-selected inverses underperform oracle inverses.
   - The highest ROI is better subset/axis selection, not simply adding more model families.

## Operational Rule

Future candidate generation should produce fewer CSVs but attach these diagnostics immediately:

- family name
- target movement vector
- bad-axis load
- raw05 distance
- a2c8 distance
- selector stress mean/p90
- scenario beat rate
- strict gate result

Candidates failing the gate should be used only as teachers or ablation evidence.

## Addendum: Universe + Low-Energy Ensemble Audit

After expanding from JEPA-named submissions to the full `submission*.csv` universe:

- Universe candidates scored: `15871`
- Strict resolved-better candidates: `0`
- Frontier escape candidates: `91`
- Novel frontier candidates: `19`

The earlier JEPA-only audit was not missing a hidden strict winner. It did miss one useful teacher family: `hiddenblock_seqmotif` contributed `4` novel frontier candidates.

The next constrained generation pass used `public6entropy`, `cvjepa`, `hiddenblock_seqmotif`, and `axis_repair` novel donors as low-energy JEPA teacher directions:

- Generated candidates: `52722`
- Strict resolved-better candidates: `0`
- Novel frontier candidates: `30392`
- Saved research probes: `24`
- Best generated p90 delta versus a2c8 public: about `+0.000527`
- Best generated bad-axis load: `0.0`
- Best generated movement versus raw05: about `0.00636`

This is a useful negative result. Removing the known public-bad axes and enforcing cross-family low-energy agreement creates many safe/novel candidates, but it still does not move the stress p90 below a2c8. Therefore the next bottleneck is not only bad-axis contamination. The missing piece is the sign and localization of the hidden-public improvement direction.

Updated priority:

1. Stop treating bad-axis removal as sufficient.
2. Use `hiddenblock_seqmotif` as a teacher family, but only for localization/gating.
3. Build the next selector around row/cell localization: which subset of the 250 test rows can explain the a2c8/raw05 gap while rejecting the known bad anchors.
4. Require any future generated candidate to improve `selector_p90_delta_vs_a2c8_public`, not just bad-axis load or raw05 distance.

## Addendum: Hidden-Public Localization and Bridge Audit

I added a row/cell localization selector:

- Script: `hidden_public_localization_selector.py`
- Selected inverse teacher solutions: `41`
- Active cells: `1750 / 1750`
- Scored candidates: `368`
- Submit gate pass: `0`
- Research probe gate pass: `0`
- Localization/stress conflicts: `120`

The target-level inverse signal is interpretable:

- Q1 wants lower probability on average: mean delta versus a2c8 `-0.00949`
- S3 wants higher probability on average: mean delta versus a2c8 `+0.01880`
- Q3 has high energy but near-zero global mean, implying row/cell-specific sign changes

But every candidate that strongly improves the localization objective is a bad-axis/stress conflict. The top public6/directrob directions have large negative localization scores, but their `selector_p90_delta_vs_a2c8_public` is about `+0.0008 .. +0.0011` and bad-axis load is too high.

I then tested a constrained bridge:

- Script: `hidden_public_local_bridge.py`
- Generated bridge candidates: `1530`
- Stress-scored candidates including anchors: `580`
- Submit gate pass: `0`
- Probe gate pass: `399`

Best probe examples:

- `submission_hiddenloc_bridge_6ad3e8b6.csv`
  - local score `-0.000504`
  - selector p90 delta `+0.000601`
  - bad-axis load `0.046679`
  - scenario beat rate `0.169884`
- `submission_hiddenloc_bridge_5a195c2f.csv`
  - local score `-0.000344`
  - selector p90 delta `+0.000583`
  - bad-axis load `0.039119`
  - scenario beat rate `0.235521`
- `submission_hiddenloc_bridge_18ea6b83.csv`
  - local score `-0.000209`
  - selector p90 delta `+0.000578`
  - bad-axis load `0.037158`
  - scenario beat rate `0.324324`

These are diagnostic probes, not submit-safe candidates. The key blocker is no longer just bad-axis load. Even when the bridge keeps stress p90 near the a2c8 baseline and bad-axis load under about `0.04`, the stress scenarios rarely prefer it over a2c8. Among probe-gated candidates, all pass the localization checks, `370 / 399` pass the p90 threshold, `209 / 399` pass the bad-axis threshold, but `0 / 399` pass the scenario-beat threshold.

Current bottleneck statement:

The data contains a plausible hidden-public row/cell signal, but the public-anchor geometry cannot yet distinguish "real hidden-public improvement" from "direct-inverse overfit direction." This is why small raw05/cvjepa/localization bridges look promising under one lens and fail under another. The next useful work is selector identification, not larger model capacity.

## Addendum: Inverse8 With LeJEPA Bad Anchor

I tested whether adding the omitted LeJEPA failed-public anchor improves selector identification:

- New anchor: `submission_lejepa_targetwise_strict_best_scale0p5.csv`, public `0.5802468192`
- Scripts:
  - `public_lb_direct_label_inverse8.py`
  - `public_lb_direct_label_inverse8_loocv.py`
  - `public_lb_direct_label_inverse8_l2ocv.py`
  - `public_lb_direct_label_robust_selector8.py`
  - `public_lb_inverse8_selected_stress_audit.py`

Selector CV improved:

- LOO `train_best1` MAE improved from about `0.000578` to `0.000521`
- L2O `l2o_best1` MAE improved from about `0.000532` to `0.000470`
- L2O oracle is `0.000315`, so useful masks still exist but selection remains underidentified

But generated inverse8 submissions failed the public-anchor stress audit:

- selected inverse8 candidates: `42`
- submit gate pass: `0`
- probe gate pass: `0`
- best stress p90 delta versus a2c8 public: about `+0.000743`
- best bad-axis load among top candidates: about `0.099`
- scenario beat rates are mostly `0.07 .. 0.27`

Interpretation:

The extra LeJEPA anchor helps identify which inverse masks are less brittle, but it pushes the solved labels toward a larger anti-bad correction that is still geometrically bad under stable public stress. The failure mode changed from "selector too weak" to "selector picks a stronger but wrong large-move correction." This confirms that more failed-public anchors alone are not enough. The next selector must be pairwise/order-aware around the actual `a2c8 < raw05 < bad anchors` ordering, not only absolute-anchor fit.
