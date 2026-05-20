# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A solution workspace for **DACON 236690 — 제5회 ETRI 휴먼이해 AI 논문경진대회 (ETRI Lifelog 2026)**. Goal: from raw wearable/phone lifelog, predict **7 binary labels** `Q1,Q2,Q3,S1,S2,S3,S4` per `(subject_id, sleep_date)`. Metric is **mean binary log loss across the 7 targets (lower is better)**. There are exactly **10 subjects, 700 subject-days** = 450 labeled (train) + 250 (test) — the same people on different dates. No extra unlabeled days exist.

Read `FINDINGS.md` (data-engineering report, Korean) and `experiments/summary.md` (modeling ledger) before doing modeling work — they encode hard-won, non-obvious facts that override naive intuition.

## Non-negotiable domain constraints (these change what is worth trying)

- **S1–S4 ground truth is a Withings mattress BCG sensor that is NOT in the dataset.** Every S prediction is proxy reconstruction with a real ceiling (~0.65 AUC). Don't promise sleep-stage accuracy.
- **Q1–Q3 are per-subject *relative* labels** (each subject's mean ≈ 0.5 by construction). Subject ID and any subject-constant feature carry **zero** information for Q. You must use **within-subject deviation features**.
- **Internal OOF does NOT transfer cleanly to Public LB.** OOF lives in a ~0.50 band; reliable Public LB is ~0.60–0.61. Treat OOF as *signal discovery*, not a score estimate. Aggressive calibration / pseudo-label anchoring / cross-project blending has scored catastrophically (0.70–0.91) on LB. See `experiments/public_lb_feedback.md` for the rules before packaging any submission.
- Best known Public LB anchor: `submission_01_v76_balanced_hedge_best.csv` @ `0.5999`. A new candidate must pass robustness checks (prediction distance, per-target/panel/subject drift, source simplicity) vs this anchor before it's worth submitting.

## Data → artifacts → outputs pipeline

The whole repo is a three-stage funnel. All paths are relative to repo root; scripts default to these.

1. **Raw lifelog** — `data/ch2025_data_items/*.parquet` (12 modalities, 6.12M rows) + labels `data/ch2026_metrics_train.csv` (450) and `data/ch2026_submission_sample.csv` (250). `data/` is gitignored.
2. **Derived features** — `artifacts/NN_*.parquet`, numbered by phase (`01_` coverage → `10_master_daily.parquet`, the 700×232 master table). Built by `scripts/build_*` from raw modalities. `artifacts/` is gitignored. The hourly grid + per-subject hour-of-day deviation tables (`03_`, `04_`) are the deviation backbone for Q labels.
3. **Model runs** — `scripts/{train,build,search,postprocess}_*.py` read feature tables and emit a self-contained run dir `outputs/<run_name>/` containing **paired** `oof_*.csv` (with `pred_<TARGET>` columns) + `submission_*.csv` (with raw `<TARGET>` columns), plus `report.md`/`report.json` and `score.csv`. `outputs/` keeps `.md`/`.json` in git but ignores all data artifacts (csv/parquet/npy/pt/png/...).

Submissions chain: a `train_*` source model produces OOF+submission → `build_*`/`search_*` blend or route multiple sources → `postprocess_*` applies label-prior/smoothing/calibration → final `submission_*.csv` uploaded to DACON.

## Conventions every script follows

- `TARGET_COLUMNS = ["Q1","Q2","Q3","S1","S2","S3","S4"]`, `KEY_COLUMNS = ["subject_id","sleep_date","lifelog_date"]`, `EPS = 1e-5` (predictions clipped to `[EPS, 1-EPS]`).
- **OOF files** carry `pred_<TARGET>` columns; **submission files** carry bare `<TARGET>` columns. Routing/blending scripts take sources as `--source name=oof_path,submission_path`.
- **Cross-validation is subject-time folds, not random**: `make_subject_time_folds` orders each subject by date and splits into contiguous time chunks per fold (see `scripts/train_targetwise_residual_latent_encoder.py`). This prevents temporal leakage within a subject. Use the same scheme for any new source model; never random-shuffle across a subject's timeline.
- Metric helper `average_log_loss(y_true, pred)` returns `(mean, per_target_dict)` — match it exactly so scores are comparable across runs.
- Latent feature tables expose `z_*` columns; feature tables are joined `validate="one_to_one"` on `KEY_COLUMNS` and a row failing the join is an error, not a silent NaN.
- Scripts are plain `argparse` CLIs with sensible path defaults; run with `python scripts/<name>.py [--output-dir outputs/<run_name>] ...`. No build/test framework — verification = re-running a script and reading its `report.md`/`score.csv`.

## Modeling state (read `experiments/summary.md` for the full ledger)

Current architecture is **common label-free features + per-target source models, composed by a conditional target/bin router** (`build_conditional_latent_routing.py`) — *not yet* one unified neural encoder with 7 heads. The active research thread is **iterative residual routing** (versions `v25`→`v80`, each shaving internal OOF): encode each subject-day as position + movement in a personal latent state space (deviation from own recent baseline, momentum, novelty, recovery, cross-modal synchrony, residual-behavior neighborhoods). Best internal OOF ≈ `0.4776` (`outputs/conditional_latent_routing_v80_late_behavior_on_v79/`). Each new idea is probed as a *standalone source* first, then as a *routed residual*; "source-only is weak but routes useful corrections" is the common, expected pattern.

When extending: add a new `train_*`/`build_*` source, generate paired OOF+submission with subject-time folds, route it via the conditional router, and log the result as a new `vNN` row in `experiments/summary.md` with its evidence path.

## Environment

Python (system `python3` is 3.14). `.venv_tabpfn/` is a dedicated venv for the TabPFN meta-model path (`train_tabpfn_external_meta.py`). Core stack: numpy, pandas, scikit-learn, pyarrow; torch for the neural encoder/diffusion scripts under `src/etri_diffusion/`. There is no requirements file or test suite — dependencies are inferred from imports.
