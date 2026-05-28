from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

TRAIN_PATH = ROOT / "data" / "ch2026_metrics_train.csv"
SAMPLE_PATH = ROOT / "data" / "ch2026_submission_sample.csv"
MIXMIN_PATH = OUT / "submission_mixmin_0c916bb4.csv"
A2C8_PATH = OUT / "submission_frontier_cvjepa_refine_a2c8d2c8.csv"
RAW05_PATH = ROOT / "jepa" / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-15


def read_frame(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["sleep_date", "lifelog_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


def logloss_delta(new_p: np.ndarray, old_p: np.ndarray, y: np.ndarray | float) -> np.ndarray:
    new_p = np.clip(new_p, EPS, 1 - EPS)
    old_p = np.clip(old_p, EPS, 1 - EPS)
    return -y * np.log(new_p) - (1 - y) * np.log(1 - new_p) + y * np.log(old_p) + (1 - y) * np.log(1 - old_p)


def implied_threshold(new_p: np.ndarray, old_p: np.ndarray) -> np.ndarray:
    new_p = np.clip(new_p, EPS, 1 - EPS)
    old_p = np.clip(old_p, EPS, 1 - EPS)
    a = np.log(old_p / new_p)
    b = np.log((1 - old_p) / (1 - new_p))
    den = a - b
    out = np.full_like(new_p, np.nan, dtype=float)
    ok = np.abs(den) > 1e-15
    out[ok] = -b[ok] / den[ok]
    return out


def weighted_corr(x: np.ndarray, y: np.ndarray, w: np.ndarray | None = None) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = np.isfinite(x) & np.isfinite(y)
    if w is None:
        w = np.ones_like(x, dtype=float)
    else:
        w = np.asarray(w, dtype=float)
        ok &= np.isfinite(w)
    x = x[ok]
    y = y[ok]
    w = w[ok]
    if len(x) < 2 or w.sum() <= 0:
        return float("nan")
    wx = np.average(x, weights=w)
    wy = np.average(y, weights=w)
    cov = np.average((x - wx) * (y - wy), weights=w)
    vx = np.average((x - wx) ** 2, weights=w)
    vy = np.average((y - wy) ** 2, weights=w)
    if vx <= 0 or vy <= 0:
        return float("nan")
    return float(cov / math.sqrt(vx * vy))


def make_context(train: pd.DataFrame, test_keys: pd.DataFrame) -> pd.DataFrame:
    train = train.copy()
    test_keys = test_keys.copy()
    train["split"] = "train"
    test_keys["split"] = "test"
    all_dates = pd.concat([train[KEYS + ["split"]], test_keys[KEYS + ["split"]]], ignore_index=True)
    all_dates = all_dates.sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    all_dates["subject_row_index"] = all_dates.groupby("subject_id").cumcount()
    all_dates["subject_n_total"] = all_dates.groupby("subject_id")["subject_id"].transform("size")
    all_dates["subject_test_index"] = all_dates.groupby(["subject_id", "split"]).cumcount()
    first_train = train.groupby("subject_id")["sleep_date"].min().rename("train_first_sleep")
    last_train = train.groupby("subject_id")["sleep_date"].max().rename("train_last_sleep")
    n_train = train.groupby("subject_id").size().rename("subject_n_train")
    out = test_keys.merge(all_dates[KEYS + ["subject_row_index", "subject_n_total", "subject_test_index"]], on=KEYS, how="left")
    out = out.merge(first_train, on="subject_id", how="left")
    out = out.merge(last_train, on="subject_id", how="left")
    out = out.merge(n_train, on="subject_id", how="left")
    out["days_after_train"] = (out["sleep_date"] - out["train_last_sleep"]).dt.days
    out["test_day_index"] = out.groupby("subject_id").cumcount()
    out["global_test_index"] = np.arange(len(out))
    return out


def calendar_mask_features(train: pd.DataFrame, test_keys: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    run_rows = []
    for sid in sorted(test_keys["subject_id"].unique()):
        tr_dates = set(train.loc[train["subject_id"] == sid, "sleep_date"])
        te_dates = set(test_keys.loc[test_keys["subject_id"] == sid, "sleep_date"])
        start = min(min(tr_dates), min(te_dates))
        end = max(max(tr_dates), max(te_dates))
        dates = pd.date_range(start, end, freq="D")
        chars = ["E" if d in te_dates else "T" if d in tr_dates else "." for d in dates]

        run_id = -1
        previous = None
        run_start = None
        for idx, (date, ch) in enumerate(zip(dates, chars)):
            if ch != previous:
                if previous is not None:
                    run_rows.append(
                        {
                            "subject_id": sid,
                            "run_id": run_id,
                            "run_type": previous,
                            "run_start": run_start,
                            "run_end": dates[idx - 1],
                            "run_length": idx - int(np.where(dates == run_start)[0][0]),
                        }
                    )
                run_id += 1
                run_start = date
                previous = ch
            rows.append({"subject_id": sid, "sleep_date": date, "calendar_mask": ch, "calendar_run_id": run_id})
        run_rows.append(
            {
                "subject_id": sid,
                "run_id": run_id,
                "run_type": previous,
                "run_start": run_start,
                "run_end": dates[-1],
                "run_length": len(dates) - int(np.where(dates == run_start)[0][0]),
            }
        )

    calendar = pd.DataFrame(rows)
    runs = pd.DataFrame(run_rows)
    prev_next = runs[["subject_id", "run_id", "run_type", "run_length"]].copy()
    prev_next["left_run_type"] = prev_next.groupby("subject_id")["run_type"].shift(1)
    prev_next["right_run_type"] = prev_next.groupby("subject_id")["run_type"].shift(-1)
    prev_next["left_run_length"] = prev_next.groupby("subject_id")["run_length"].shift(1)
    prev_next["right_run_length"] = prev_next.groupby("subject_id")["run_length"].shift(-1)
    calendar = calendar.merge(prev_next, left_on=["subject_id", "calendar_run_id"], right_on=["subject_id", "run_id"], how="left")
    test_features = test_keys[KEYS].merge(calendar, on=["subject_id", "sleep_date"], how="left")
    test_features = test_features.rename(
        columns={
            "run_length": "test_run_length",
            "left_run_type": "left_context_type",
            "right_run_type": "right_context_type",
            "left_run_length": "left_context_length",
            "right_run_length": "right_context_length",
        }
    )
    test_features["calendar_context"] = np.select(
        [
            (test_features["left_context_type"] == "T") & (test_features["right_context_type"] == "T"),
            (test_features["left_context_type"] == "T") & (test_features["right_context_type"].isna()),
            (test_features["left_context_type"].isna()) & (test_features["right_context_type"] == "T"),
            (test_features["left_context_type"] == ".") | (test_features["right_context_type"] == "."),
        ],
        ["between_train_runs", "after_train_run", "before_train_run", "gap_adjacent"],
        default="other",
    )
    return test_features, runs


def subject_prior_features(train: pd.DataFrame, test_keys: pd.DataFrame) -> pd.DataFrame:
    global_prior = train[TARGETS].mean()
    subj_prior = train.groupby("subject_id")[TARGETS].mean().add_prefix("subject_prior_")
    recent = (
        train.sort_values(["subject_id", "sleep_date"])
        .groupby("subject_id", group_keys=False)
        .tail(7)
        .groupby("subject_id")[TARGETS]
        .mean()
        .add_prefix("subject_recent7_")
    )
    out = test_keys[KEYS].merge(subj_prior, on="subject_id", how="left").merge(recent, on="subject_id", how="left")
    for t in TARGETS:
        out[f"subject_prior_{t}"] = out[f"subject_prior_{t}"].fillna(global_prior[t])
        out[f"subject_recent7_{t}"] = out[f"subject_recent7_{t}"].fillna(out[f"subject_prior_{t}"])
    return out


def target_summary(frame: pd.DataFrame, train: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for t in TARGETS:
        old = frame[f"a2c8_{t}"].to_numpy()
        new = frame[f"mixmin_{t}"].to_numpy()
        raw = frame[f"raw05_{t}"].to_numpy()
        move = new - old
        abs_move = np.abs(move)
        thresh = implied_threshold(new, old)
        subj_prior = frame[f"subject_prior_{t}"].to_numpy()
        recent = frame[f"subject_recent7_{t}"].to_numpy()
        global_prior = float(train[t].mean())
        rows.append(
            {
                "target": t,
                "train_prevalence": global_prior,
                "a2c8_mean": float(np.mean(old)),
                "mixmin_mean": float(np.mean(new)),
                "raw05_mean": float(np.mean(raw)),
                "mixmin_minus_a2c8_mean": float(np.mean(move)),
                "mixmin_minus_a2c8_abs_mean": float(np.mean(abs_move)),
                "mixmin_minus_a2c8_abs_p90": float(np.quantile(abs_move, 0.9)),
                "move_up_rate": float(np.mean(move > 0)),
                "move_down_rate": float(np.mean(move < 0)),
                "mean_threshold_for_new_to_win": float(np.nanmean(thresh)),
                "weighted_threshold_for_new_to_win": float(np.average(thresh[np.isfinite(thresh)], weights=abs_move[np.isfinite(thresh)])),
                "ce_delta_at_train_prevalence": float(np.mean(logloss_delta(new, old, global_prior))),
                "ce_delta_at_subject_prior": float(np.mean(logloss_delta(new, old, subj_prior))),
                "ce_delta_at_recent7_prior": float(np.mean(logloss_delta(new, old, recent))),
                "corr_move_with_subject_prior": weighted_corr(move, subj_prior, abs_move),
                "corr_move_with_recent7_prior": weighted_corr(move, recent, abs_move),
                "corr_mixmin_move_with_raw05_move": weighted_corr(move, raw - old, abs_move),
            }
        )
    return pd.DataFrame(rows)


def subject_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for subject, g in frame.groupby("subject_id"):
        target_abs = {t: float(np.mean(np.abs(g[f"mixmin_{t}"] - g[f"a2c8_{t}"]))) for t in TARGETS}
        signed = {t: float(np.mean(g[f"mixmin_{t}"] - g[f"a2c8_{t}"])) for t in TARGETS}
        rows.append(
            {
                "subject_id": subject,
                "n_test": len(g),
                "mean_days_after_train": float(g["days_after_train"].mean()),
                "mean_abs_move_all": float(np.mean([target_abs[t] for t in TARGETS])),
                "max_abs_move_target": max(target_abs, key=target_abs.get),
                "max_abs_move_value": max(target_abs.values()),
                **{f"abs_{t}": target_abs[t] for t in TARGETS},
                **{f"signed_{t}": signed[t] for t in TARGETS},
            }
        )
    return pd.DataFrame(rows).sort_values("mean_abs_move_all", ascending=False)


def row_summary(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame[KEYS + ["global_test_index", "test_day_index", "days_after_train"]].copy()
    moves = []
    raw_dists = []
    for t in TARGETS:
        move = frame[f"mixmin_{t}"] - frame[f"a2c8_{t}"]
        out[f"move_{t}"] = move
        out[f"abs_move_{t}"] = move.abs()
        moves.append(move.abs())
        raw_dists.append((frame[f"mixmin_{t}"] - frame[f"raw05_{t}"]).abs())
    out["mean_abs_move"] = pd.concat(moves, axis=1).mean(axis=1)
    out["max_abs_move"] = pd.concat(moves, axis=1).max(axis=1)
    out["dominant_target"] = pd.concat(moves, axis=1).set_axis(TARGETS, axis=1).idxmax(axis=1)
    out["mean_abs_mixmin_raw05_distance"] = pd.concat(raw_dists, axis=1).mean(axis=1)
    return out.sort_values("mean_abs_move", ascending=False)


def main() -> None:
    train = read_frame(TRAIN_PATH)
    sample = read_frame(SAMPLE_PATH)
    mixmin = read_frame(MIXMIN_PATH)
    a2c8 = read_frame(A2C8_PATH)
    raw05 = read_frame(RAW05_PATH)

    context = make_context(train, sample[KEYS])
    mask_features, calendar_runs = calendar_mask_features(train, sample[KEYS])
    priors = subject_prior_features(train, sample[KEYS])
    frame = context.merge(priors, on=KEYS, how="left")
    frame = frame.merge(
        mask_features[
            KEYS
            + [
                "calendar_run_id",
                "test_run_length",
                "left_context_type",
                "right_context_type",
                "left_context_length",
                "right_context_length",
                "calendar_context",
            ]
        ],
        on=KEYS,
        how="left",
    )
    for name, df in [("mixmin", mixmin), ("a2c8", a2c8), ("raw05", raw05)]:
        renamed = df[KEYS + TARGETS].rename(columns={t: f"{name}_{t}" for t in TARGETS})
        frame = frame.merge(renamed, on=KEYS, how="left")
    if frame[[f"mixmin_{t}" for t in TARGETS]].isna().any().any():
        raise ValueError("submission key alignment failed")

    target = target_summary(frame, train)
    subjects = subject_summary(frame)
    rows = row_summary(frame)
    block = (
        rows.merge(
            frame[
                KEYS
                + [
                    "test_run_length",
                    "calendar_context",
                    "left_context_type",
                    "right_context_type",
                ]
            ],
            on=KEYS,
            how="left",
        )
        .assign(train_span_zone=lambda x: np.where(x["days_after_train"] <= 0, "inside_train_calendar", "after_train_end"))
        .groupby(["calendar_context", "train_span_zone", "test_run_length", "dominant_target"], dropna=False)
        .agg(
            n_rows=("subject_id", "size"),
            mean_abs_move=("mean_abs_move", "mean"),
            max_abs_move=("max_abs_move", "max"),
            mean_mixmin_raw05_distance=("mean_abs_mixmin_raw05_distance", "mean"),
        )
        .reset_index()
        .sort_values(["mean_abs_move", "n_rows"], ascending=[False, False])
    )
    subject_calendar = (
        calendar_runs.groupby(["subject_id", "run_type"])
        .agg(n_runs=("run_id", "size"), mean_run_length=("run_length", "mean"), max_run_length=("run_length", "max"))
        .reset_index()
    )

    target.to_csv(OUT / "post_mixmin_target_delta_summary.csv", index=False)
    subjects.to_csv(OUT / "post_mixmin_subject_delta_summary.csv", index=False)
    rows.head(80).to_csv(OUT / "post_mixmin_row_delta_top80.csv", index=False)
    block.to_csv(OUT / "post_mixmin_calendar_block_delta_summary.csv", index=False)
    subject_calendar.to_csv(OUT / "post_mixmin_calendar_mask_summary.csv", index=False)

    strongest = target.sort_values("mixmin_minus_a2c8_abs_mean", ascending=False).head(3)
    ce_prior = target[["target", "ce_delta_at_train_prevalence", "ce_delta_at_subject_prior", "ce_delta_at_recent7_prior"]]
    best_prior_col = ce_prior.set_index("target").idxmin(axis=1).rename("best_prior_proxy")
    target = target.merge(best_prior_col, on="target")

    lines = []
    lines.append("# Post-Mixmin Observation Audit")
    lines.append("")
    lines.append("This is an observation-first audit, not a model run. It asks what hidden label world must be true for `submission_mixmin_0c916bb4.csv` to beat the previous a2c8 frontier.")
    lines.append("")
    lines.append("## Dataset Shape")
    lines.append("")
    lines.append(f"- train rows: `{len(train)}`")
    lines.append(f"- test/submission rows: `{len(sample)}`")
    lines.append(f"- subjects train/test: `{train['subject_id'].nunique()}` / `{sample['subject_id'].nunique()}`")
    lines.append(f"- train date span: `{train['sleep_date'].min().date()}` to `{train['sleep_date'].max().date()}`")
    lines.append(f"- test date span: `{sample['sleep_date'].min().date()}` to `{sample['sleep_date'].max().date()}`")
    lines.append("")
    lines.append("## First Observations")
    lines.append("")
    for _, r in strongest.iterrows():
        lines.append(
            f"- `{r['target']}` carries large mixmin movement: mean abs move `{r['mixmin_minus_a2c8_abs_mean']:.6f}`, "
            f"signed mean `{r['mixmin_minus_a2c8_mean']:.6f}`, move-up rate `{r['move_up_rate']:.3f}`, "
            f"threshold-for-new-to-win `{r['weighted_threshold_for_new_to_win']:.3f}`."
        )
    lines.append("")
    lines.append("## Prior-World Stress")
    lines.append("")
    for _, r in target.iterrows():
        lines.append(
            f"- `{r['target']}`: CE delta if labels followed train/global prior `{r['ce_delta_at_train_prevalence']:+.8f}`, "
            f"subject prior `{r['ce_delta_at_subject_prior']:+.8f}`, recent7 prior `{r['ce_delta_at_recent7_prior']:+.8f}`; "
            f"best proxy `{r['best_prior_proxy']}`."
        )
    lines.append("")
    lines.append("Negative CE delta means mixmin would beat a2c8 under that proxy label-world. If these simple priors do not favor mixmin, the public gain likely comes from a more structured hidden subset/state rather than ordinary prevalence correction.")
    lines.append("")
    lines.append("## Subject/Row Concentration")
    lines.append("")
    for _, r in subjects.head(5).iterrows():
        lines.append(
            f"- `{r['subject_id']}` has the largest mean movement `{r['mean_abs_move_all']:.6f}` "
            f"over `{int(r['n_test'])}` test rows; dominant target `{r['max_abs_move_target']}`."
        )
    lines.append("")
    lines.append("## Calendar Mask Observation")
    lines.append("")
    lines.append("Train/test is not a simple future split. Test rows are hidden calendar blocks inside each subject's observed timeline, often flanked by train runs.")
    lines.append("")
    top_blocks = block.head(6)
    for _, r in top_blocks.iterrows():
        lines.append(
            f"- `{r['calendar_context']}` / `{r['train_span_zone']}` / run length `{int(r['test_run_length'])}` "
            f"/ dominant `{r['dominant_target']}`: rows `{int(r['n_rows'])}`, mean abs move `{r['mean_abs_move']:.6f}`, "
            f"mixmin-raw05 distance `{r['mean_mixmin_raw05_distance']:.6f}`."
        )
    lines.append("")
    lines.append("This reframes the JEPA context/target question: the natural context may be the train-labeled calendar flanks around a hidden test block, and the target representation may be the block's label-rate vector rather than individual row probabilities.")
    lines.append("")
    lines.append("## New Questions")
    lines.append("")
    lines.append("1. Is mixmin winning because it moves the right target globally, or because it concentrates movement on a few subject/date blocks?")
    lines.append("2. Do the cells where mixmin moves away from a2c8 require label prevalences that resemble train priors, subject priors, or a stranger binary hidden-public world?")
    lines.append("3. Does raw05 fail because it stays too close to a measurement-process manifold, while mixmin crosses a block/state boundary that raw05 cannot express?")
    lines.append("4. Are the high-movement rows public-like, or are they private-risk rows that happened to align with public?")
    lines.append("")
    lines.append("## Falsifiable Next Experiment")
    lines.append("")
    lines.append("Build a mixmin-relative selector target: add mixmin as a known public anchor, then ask whether target/subject/date movement fingerprints can explain mixmin without breaking raw05, stage2, ordinal, and bad-JEPA anchor order. Success means the selector error drops below the mixmin-a2c8 edge scale; failure means E48 was public-subset luck or an anchor-derived worldview that still lacks private safety.")
    lines.append("")

    (OUT / "post_mixmin_observation_report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
