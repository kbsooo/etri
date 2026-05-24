# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

DACON 236690 / ETRI 2026 lifelog sleep-state competition. Predict 7 binary self-report labels (`Q1,Q2,Q3,S1,S2,S3,S4`) per `(subject_id, sleep_date, lifelog_date)` row. Metric: average log-loss. Data: 450 train / 250 test rows over **10 same subjects** plus 12 raw sensor parquet files (mACStatus/mActivity/mAmbience/mBle/mGps/mLight/mScreenStatus/mUsageStats/mWifi/wHr/wLight/wPedo).

The user (강병수) treats this as a **data-engineering / feature-mechanism / measurement-theory problem, not a modeling problem**. Big supervised Transformers / random KFold leaderboard chasing are deferred; SSL latent + small calibrated heads + hand-engineered mechanism features are the agreed path.

## How the working tree is organized (only the parts you need to know)

- `data/ch2026_metrics_train.csv` — 450 labeled rows, columns `subject_id, sleep_date, lifelog_date, Q1..S4`.
  - **Important date relation:** `sleep_date = lifelog_date + 1 day`. The plausible sleep episode for an `S*` label is the **evening of `lifelog_date` + morning of `sleep_date`** (cross-night). Same-day 00–05 + 20–23 aggregation mixes the wrong night and was a real bug fixed in `scripts/23_…` / `26_…`.
- `data/ch2026_submission_sample.csv` — 250 rows, defines the test (subject, date) pairs and the required submission schema.
- `data/ch2025_data_items/*.parquet` — raw sensor streams. Read with `pyarrow`/`pandas`/`polars`; subject and timestamp columns are inside each parquet.
- `src/cl_common.py` — shared paths (`ROOT/DATA_DIR/FEATURE_DIR/EXPERIMENT_DIR/OUT_DIR`), constants `LABELS` and `ID_COLS`, and `logloss()` / `clip_prob()` helpers. **Always import from here, do not hardcode paths.**
- `scripts/NN_*.py` — numbered, append-only experiment log. Numbers are chronological; the latest number is the most recent thinking. Scripts are *not* a clean pipeline — each is a self-contained experiment. Treat earlier scripts as documentation of failed/partial paths.
- `features/*.parquet` — outputs of feature builders, keyed on `(subject_id, sleep_date|lifelog_date)`. Many files; the canonical model-input is `features/model_features_v0.parquet` (700 rows × 258 cols).
- `experiments/` — markdown reports + CSV artifacts of diagnostic runs. **Read the latest few `.md` files (sorted by mtime) before doing anything new — they encode active hypotheses and what already failed.**
- `outputs/submission_*.csv` — historical submission candidates. Each has a sibling `*_notes.json` documenting weights/caps and a `*_shift.csv` describing per-target shift vs base.

## Key results / numbers to anchor against

- Subject-prior baseline (alpha=20, chrono_last_25): **mean logloss 0.6344**.
- Best feature-only clean target-specific (3-fold chrono avg): **0.6020**, per-target {Q1 0.634, Q2 0.634, Q3 0.650, S1 0.540, S2 0.570, S3 0.578, S4 0.609}.
- Public LB measured on one submission: **0.6421** vs local CV 0.5933 → **large CV↔LB gap; chrono-tail CV is over-optimistic for this competition split**.
- Label measurement model (low-rank Bernoulli) loadings split labels into two opposing axes: **Q2/Q3 (+)**, **S2/S3/S4 (−)**, S1 ~ neutral. The labels are not one severity dimension.

## Common commands

```bash
# venv
source .venv312/bin/activate                # 3.12 venv used by recent scripts
# (older .venv is python 3.13; check shebangs)

# install deps
pip install -r requirements.txt              # core (numpy/pandas/sklearn/pyarrow/etc.)
pip install -r requirements_ssl.txt          # SSL / embedding extras (torch, transformers, …)

# run any experiment script
python scripts/NN_<name>.py                  # most scripts hardcode their own input/output paths

# quick reproducible baseline / fold sanity
python scripts/01_make_folds.py              # writes outputs/validation/folds_chrono.json
python scripts/02_subject_prior_baseline.py  # writes experiments/subject_prior_results.{json,csv}
```

There is **no test suite, no linter, no Makefile, no CI**. Scripts are run individually.

## Conventions and protocols agreed with the user

- **Reply in Korean.** Practical tone. The user is a Korean ML competitor.
- **Default mode is diagnostic, not submission generation.** Do not generate a new `outputs/submission_*.csv` unless the user explicitly asks; instead write a markdown report under `experiments/` and a `features/*.parquet` if needed.
- **Numbered append-only scripts.** Pick the next free number (currently 77+) when adding a new experiment; do not edit old numbered scripts unless fixing a known bug.
- **Validation is the modeling problem.** Trust chronological folds over random KFold, but recognize that **test is hybrid: ~50% of test rows fall *inside* each subject's train date range (hole-filling), ~50% are *after* (forecast tail)**. Pure chrono-tail CV under-tests the hole-filling regime — it likely explains the CV↔LB gap. Random KFold over-tests it. For new validation work, build *both* and report separately.
- **`sleep_date = lifelog_date + 1`** — when building sleep-episode features for any `S*` target, always cross the night boundary (evening of `lifelog_date` + morning of `sleep_date`).
- **Subject prior:** used as a diagnostic anchor (baseline 0.634), not as a final-stage smoothing crutch. The user explicitly does not want anchored blends to push CV down.
- **Don't chase third-decimal CV differences.** With 450 rows / 10 subjects / 7 binary targets, fold-to-fold std easily exceeds 0.01.
- **Public LB scalar is a hard constraint, not a per-target diagnosis.** One scalar cannot decompose blame per target. Treat it as a robustness check, not a feedback signal for tuning.
- **Treat target families differently** (justified by `experiments/problem_definition_q_temporal_s_context_measurement.md`):
  - **Q2/Q3:** temporal label grammar (own-lag + Q1-lag are strong, +0.04 AUC over subject-only).
  - **Q1:** weak temporal precursor, mixed signal.
  - **S2/S3:** dominated by subject + static context fingerprint — coverage_plus_subject and subject_label_shuffle controls match real model AUC. Aggressive day-level modeling here is mostly repackaging subject prevalence; be conservative.
  - **S4:** raw WiFi/BLE/app context-event target (specific BSSIDs lift S4 rate from 0.56 to 0.80+). Use as capped event features, not unlimited drivers — sparse tokens are public/private brittle.
  - **S1:** mixed / less clearly defined.

## Reading order for a new session

1. `experiment_plan.md` — agreed stage plan and status.
2. The most recent `experiments/*_report.md` (sort by mtime). The current head is `experiments/problem_definition_q_temporal_s_context_measurement.md` and `experiments/advanced76_data_science_report.md`.
3. `experiments/public_lb_failure_next_ideas.md` — the public LB calibration constraint.
4. `experiments/results.md` (if present) — running ledger.
5. Only after that, read the numbered scripts in the area you're touching.
