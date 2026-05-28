# JEPA 0.54 Push Experiment Summary

## Public Anchors

- Stage2 anchor: `submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv` public `0.5779449757`.
- Raw Timeline JEPA rescue: `submission_raw_timeline_jepa_rescue_strict_scale0p5.csv` public `0.5775263072`.
- Prior JEPA residual probes were harmful:
  - `submission_jepa_latent_residual_probe.csv` public `0.5812273278`.
  - `submission_jepa_latent_q2_w0p45.csv` public `0.5798012862`.

The useful public axis is therefore not "more JEPA movement"; it is small JEPA movement that stays close to the raw rescue direction and avoids the previously harmful latent residual direction.

## New Experiments

### 1. Transductive Episode Count JEPA

File: `jepa/transductive_episode_count_jepa.py`

Idea: predict each hidden submission-like episode's 7-target block rate first, then solve row-level probabilities so the block matches that latent rate. This is more JEPA-like than row residual features because the target is an unobserved block-level latent object.

Results:

- Subject-chunk CV best: `0.566993`, delta `-0.000537`.
- Geometry CV best: `0.558392`, delta `-0.002350`.
- Submission candidates emitted in `jepa/submission_transductive_episode_count_jepa_*.csv`.

Conclusion: direct count/rate latent prediction is real but small. It is not the missing 0.54 jump.

### 2. Graph Field JEPA Inpainting

File: `jepa/graph_field_jepa_inpainting.py`

Idea: treat every train/submission row as a node in a JEPA-friendly joint embedding graph. Known train labels are clamped, hidden/submission rows keep only the stage2 prior, and a smooth 7-target logit field is inpainted over the graph.

Results:

- Best full OOF: `0.566914`, delta `-0.000617`.
- Best candidate: `submission_graph_field_jepa_00_gk6_t1_sw0p25_pw0p75_lw20_all_sc0p5.csv`.
- Public-axis audit is risky: best candidates have positive harmful-axis projection around `0.05` to `0.11`.

Conclusion: this is the strongest conceptual JEPA usage in the run, but the measured gain is still small and public-risky.

### 3. Public-Safe JEPA Blender

File: `jepa/jepa_public_safe_blender.py`

Idea: blend JEPA-family logit moves around the stage2 base, but explicitly penalize directions aligned with known harmful public submissions.

Best conservative emitted candidates:

- `submission_jepa_public_safe_blend_00.csv`: raw rescue + tiny SEGJ + tiny neural.
- `submission_jepa_public_safe_blend_06.csv`: raw rescue + tiny SEGJ + tiny block-canvas + tiny neural.
- `submission_jepa_public_safe_blend_04.csv`: slightly lower raw dose, tiny SEGJ/neural.

Conclusion: these are the best practical submission candidates from this round because they use JEPA signal while staying close to the only public-positive anchor.

### 4. Targetwise Public Blends

File: `jepa/jepa_targetwise_public_blends.py`

Idea: apply JEPA movement by target, not globally. Q targets get shallow movement; S2/S3 get deeper movement because repeated JEPA probes showed their block-rate signal is strongest.

Notable candidates:

- `submission_jepa_targetwise_public_blend_00_tw_raw1_qsegj_light_s23_mid.csv`: conservative raw + shallow SEGJ.
- `submission_jepa_targetwise_public_blend_04_tw_bc_stage_q_light.csv`: more stage-focused, harmful-axis negative, but less anchored to known public-positive raw rescue.
- `submission_jepa_targetwise_public_blend_02_tw_segj_noq2_stage.csv`: high-upside stage-only SEGJ, but larger distribution shift.

Conclusion: useful as exploratory submissions after the public-safe blend candidates.

## Validation

Validated submission format for:

- 28 transductive episode count JEPA files.
- 37 public-safe blend files.
- 8 targetwise public blend files.
- 24 graph-field inpainting files.
- Core SEGJ strict/raw-rescue files.

All checked files match the sample submission keys, have 250 rows, contain no NaN/inf, and keep target probabilities strictly inside `(0, 1)`.

## Submission Priority

1. `jepa/submission_jepa_public_safe_blend_00.csv`
   - Most conservative new candidate.
   - Expected public range: roughly `0.5768` to `0.5783`.

2. `jepa/submission_jepa_public_safe_blend_06.csv`
   - Similar to blend 00 but adds a tiny block-canvas component.
   - Expected public range: roughly `0.5769` to `0.5785`.

3. `jepa/submission_jepa_targetwise_public_blend_00_tw_raw1_qsegj_light_s23_mid.csv`
   - Targetwise version of the same idea.
   - Expected public range: roughly `0.5770` to `0.5790`.

4. `jepa/submission_jepa_targetwise_public_blend_04_tw_bc_stage_q_light.csv`
   - More exploratory. It avoids the known bad axis but is less tied to the raw rescue public-positive direction.
   - Expected public range: roughly `0.5775` to `0.5810`.

5. `jepa/submission_subject_episode_graph_jepa_strict_scale0p75.csv`
   - High-upside local candidate. Local OOF looked very strong, but public risk is high.
   - Expected public range: wide, roughly `0.576` to `0.583`.

## Bottom Line

The new JEPA-heavy experiments did not produce evidence strong enough to honestly expect public `0.54`. The best credible public expectation is still around the high `0.576` to low `0.578` band unless a new structural leak/geometry rule is discovered. The experiments did clarify that the public-positive JEPA signal is narrow: raw-timeline rescue helps slightly, while large latent residual or aggressive graph/episode moves are unstable.
