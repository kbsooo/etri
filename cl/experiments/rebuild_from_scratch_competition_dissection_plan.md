# Competition Dissection Rebuild Plan

Goal: stop optimizing submissions locally and re-open the problem as a data-science investigation. The core question is not "which model?" but "what is the hidden structure of the rows, labels, split, dates, subjects, and targets?"

## Working thesis

This competition is likely a subject-state reconstruction problem more than a generic sensor-to-label prediction problem. The fastest route to a 0.5x jump is to identify the hidden split/label mechanism and route predictions by target family.

## Phase 0 — Freeze current assets

Outputs to keep as references:
- `outputs/submission_meta_anchor_w02_noq3_prob.csv`
- `outputs/submission_moonshot_raw_all_antifix_q1s4_prob.csv`
- `outputs/submission_moonshot_validated_block_prob.csv`
- `experiments/moonshot_masked_validation_report.md`

Do not delete current scripts. New work should go under scripts 70+.

## Phase 1 — Row/split forensics

Question: What are the train/test rows structurally?

Tasks:
1. Build per-subject timelines of train and test rows.
2. Mark gaps, test clusters, overlap between train and test periods, weekday positions, and rank positions.
3. Compare whether test is mostly future tail, interleaved holes, late block, or calendar-patterned missingness.
4. For each test row, compute nearest train before/after by date and nearest train by feature similarity.
5. Summarize by subject and globally.

Expected output:
- `experiments/rebuild_split_forensics_subject_timeline.csv`
- `experiments/rebuild_split_forensics_report.md`

Decision:
- If test rows have close train neighbors on both sides, graph completion should dominate.
- If test is mostly future tail, graph should be constrained to previous-only / regime forecasting.

## Phase 2 — Label semantics and target family map

Question: Which targets behave like temporal state, which like noisy subjective reports, and which like sensor-detectable events?

Tasks:
1. Per-target prevalence by subject, weekday, rank, and month.
2. Per-target autocorrelation / flip-rate / run-length.
3. Cross-target co-occurrence and conditional probabilities.
4. Train-only leave-one-block-out tests for same-subject mean, prev/next label, graph, and feature model.
5. Target family assignment.

Expected families to verify:
- Graph/state targets: Q2/S1/S2/S3 maybe.
- Alignment/mechanism targets: Q1/S4 maybe.
- Freeze/noise target: Q3 likely.

Expected output:
- `experiments/rebuild_label_semantics_summary.csv`
- `experiments/rebuild_target_family_map.json`
- `experiments/rebuild_label_semantics_report.md`

## Phase 3 — Build split-matched validation, not generic CV

Question: Which validation scheme predicts public-LB behavior?

Known public facts:
- `wcap01`: 0.6394201335
- `wcap02`: 0.6311869686

Tasks:
1. Generate multiple validation schemes:
   - interleaved-hole mask
   - tail-only mask
   - public-like rank mask
   - per-subject cluster mask
   - weekday/calendar mask
   - nearest-neighbor-distance matched mask
2. Replay known public submissions/components in each validation.
3. Score each validation scheme by whether it ranks wcap02 better than wcap01 and prefers no-Q3 smoothing.
4. Use only credible validation schemes for future selection.

Expected output:
- `experiments/rebuild_validation_scheme_ranking.csv`
- `experiments/rebuild_validation_scheme_report.md`

Decision:
- If only interleaved-hole validation matches public, trust graph completion.
- If tail validation matches public, switch to previous-only temporal forecasting.

## Phase 4 — Component zoo with targetwise diagnostics

Question: Which primitive predictor wins per target under credible validation?

Components to build:
1. Base feature model.
2. Subject prior.
3. Previous label / next label / local mean smoother.
4. Same-subject temporal kernel.
5. Same-subject feature-KNN graph.
6. Cross-subject normalized routine KNN graph.
7. Cross-night episode mechanism head.
8. SSL/prototype head.
9. Joint label-state correction.
10. Calibration transforms.

For every component:
- Produce OOF predictions on credible validation schemes.
- Produce test predictions.
- Save targetwise logloss, prevalence, movement, rank correlation.

Expected output:
- `experiments/rebuild_component_zoo_oof.parquet`
- `experiments/rebuild_component_zoo_test.parquet`
- `experiments/rebuild_component_zoo_scoreboard.csv`

## Phase 5 — Targetwise router instead of global model

Question: What should each target use?

Candidate routing based on current evidence:
- Q1: conservative w03/base or episode-aligned head; avoid raw graph unless new evidence reverses it.
- Q2: raw graph, maybe sharpened only if prevalence stable.
- Q3: base/freeze unless a specific Q3 representation wins.
- S1: raw graph.
- S2: graph + SSL/S2 sparse if both agree.
- S3: graph/sharpened graph.
- S4: conservative w03/episode; raw graph only if validation scheme says yes.

Tasks:
1. Create targetwise candidate generator from component zoo.
2. Search small discrete combinations, not continuous overfit.
3. Enforce public-informed constraints.
4. Produce 5 candidate tiers:
   - safest
   - public-likely
   - 0.5-or-bust
   - Q/S family diagnostic
   - calibration diagnostic

Expected output:
- `outputs/submission_rebuild_*.csv`
- `experiments/rebuild_router_search_summary.csv`

## Phase 6 — 0.5-or-bust criteria

A candidate deserves submission as a 0.5 attempt only if:
1. It beats anchor by at least 0.010 in credible local validation.
2. It changes enough mass: mean_abs_vs_anchor >= 0.06 globally or >= 0.12 on key targets.
3. It has a clear mechanism story, not just blend golf.
4. It does not rely on Q3 improvement unless Q3-specific evidence exists.
5. It has targetwise diagnostics showing where the gain comes from.

## Immediate next scripts

1. `scripts/70_rebuild_split_forensics.py`
   - timeline and train/test structure.
2. `scripts/71_rebuild_label_semantics.py`
   - target behavior and family map.
3. `scripts/72_rebuild_validation_scheme_selection.py`
   - decide which local validation to trust.
4. `scripts/73_rebuild_component_zoo.py`
   - generate OOF/test predictions for primitives.
5. `scripts/74_rebuild_router_search.py`
   - targetwise candidate construction.

## Key mindset

Do not ask "what model scores best?" first.
Ask:
- What are test rows?
- What does each target mean operationally?
- Which local validation mirrors public behavior?
- Which targets are state-completion vs mechanism-prediction?
- Which components win by target under the credible validation?

Only after those answers, build submissions.
