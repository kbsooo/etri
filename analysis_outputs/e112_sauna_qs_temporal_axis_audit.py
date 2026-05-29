from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
Q_TARGETS = {"Q1", "Q2", "Q3"}
E95_ACTIVE = {"Q2", "S1", "S2", "S3"}


def clip(x: np.ndarray | float) -> np.ndarray | float:
    return np.clip(x, 1e-6, 1 - 1e-6)


def binary_entropy(p: float) -> float:
    p = float(clip(p))
    return float(-(p * np.log(p) + (1 - p) * np.log(1 - p)))


def logloss(y: np.ndarray, p: np.ndarray) -> float:
    p = clip(p)
    return float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    test = pd.read_csv(DATA / "ch2026_submission_sample.csv")
    for frame in [train, test]:
        frame["sleep_date"] = pd.to_datetime(frame["sleep_date"])
        frame["lifelog_date"] = pd.to_datetime(frame["lifelog_date"])
    train["split"] = "train"
    test["split"] = "test"
    return train, test


def target_axis_stats(train: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    ordered = train.sort_values(["subject_id", "sleep_date"]).copy()

    for target in TARGETS:
        y = ordered[target].to_numpy(dtype=float)
        p = float(y.mean())
        global_pred = np.full(len(y), (y.sum() + 0.5) / (len(y) + 1.0))

        subject_sum = ordered.groupby("subject_id")[target].transform("sum").to_numpy(dtype=float)
        subject_n = ordered.groupby("subject_id")[target].transform("count").to_numpy(dtype=float)
        loo_subject = (subject_sum - y + 0.5) / (subject_n - 1 + 1.0)
        subject_ll_gain = logloss(y, global_pred) - logloss(y, loo_subject)

        subject_rates = ordered.groupby("subject_id")[target].mean()
        subject_var = float(subject_rates.var(ddof=0))
        subject_range = float(subject_rates.max() - subject_rates.min())
        icc_proxy = subject_var / (p * (1 - p) + 1e-9)

        pairs: list[tuple[int, int, int]] = []
        for _, grp in ordered.groupby("subject_id", sort=False):
            grp = grp.sort_values("sleep_date")
            dates = grp["sleep_date"].to_numpy()
            vals = grp[target].to_numpy(dtype=int)
            for i in range(1, len(grp)):
                gap = int((dates[i] - dates[i - 1]) / np.timedelta64(1, "D"))
                if gap <= 7:
                    pairs.append((int(vals[i - 1]), int(vals[i]), gap))

        if pairs:
            prev = np.asarray([p_[0] for p_ in pairs], dtype=int)
            curr = np.asarray([p_[1] for p_ in pairs], dtype=int)
            gaps = np.asarray([p_[2] for p_ in pairs], dtype=int)
            equal_rate = float((prev == curr).mean())
            adjacent = gaps == 1
            equal_rate_gap1 = float((prev[adjacent] == curr[adjacent]).mean()) if adjacent.any() else np.nan
            expected_equal = float(p**2 + (1 - p) ** 2)
            persistence_lift = equal_rate - expected_equal
            p11 = float(curr[prev == 1].mean()) if (prev == 1).any() else np.nan
            p01 = float(curr[prev == 0].mean()) if (prev == 0).any() else np.nan
            transition_contrast = p11 - p01 if np.isfinite(p11) and np.isfinite(p01) else np.nan
            pair_count = int(len(pairs))
            gap1_pairs = int(adjacent.sum())
        else:
            equal_rate = equal_rate_gap1 = expected_equal = persistence_lift = np.nan
            p11 = p01 = transition_contrast = np.nan
            pair_count = gap1_pairs = 0

        rows.append(
            {
                "target": target,
                "axis": "Q" if target in Q_TARGETS else "S",
                "e95_axis": target in E95_ACTIVE,
                "prevalence": p,
                "entropy": binary_entropy(p),
                "global_logloss": logloss(y, global_pred),
                "subject_loo_logloss_gain": subject_ll_gain,
                "subject_rate_var": subject_var,
                "subject_rate_range": subject_range,
                "icc_proxy": icc_proxy,
                "temporal_pair_count_gap_le7": pair_count,
                "temporal_pair_count_gap1": gap1_pairs,
                "same_label_rate_gap_le7": equal_rate,
                "same_label_rate_gap1": equal_rate_gap1,
                "expected_same_by_prevalence": expected_equal,
                "persistence_lift_gap_le7": persistence_lift,
                "p_curr1_given_prev1": p11,
                "p_curr1_given_prev0": p01,
                "transition_contrast": transition_contrast,
            }
        )
    return pd.DataFrame(rows)


def pairwise_dependency(train: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    y = train[TARGETS].astype(float)
    for i, a in enumerate(TARGETS):
        for b in TARGETS[i + 1 :]:
            corr = float(y[a].corr(y[b]))
            axis_pair = ("Q" if a in Q_TARGETS else "S") + ("Q" if b in Q_TARGETS else "S")
            rows.append({"target_a": a, "target_b": b, "axis_pair": axis_pair, "corr": corr})
    return pd.DataFrame(rows)


def test_calendar_context(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    all_dates = pd.concat(
        [
            train[["subject_id", "sleep_date", "split"]],
            test[["subject_id", "sleep_date", "split"]],
        ],
        ignore_index=True,
    ).sort_values(["subject_id", "sleep_date", "split"])

    for subject, grp in all_dates.groupby("subject_id", sort=False):
        train_dates = grp.loc[grp["split"].eq("train"), "sleep_date"].sort_values().to_numpy()
        test_dates = grp.loc[grp["split"].eq("test"), "sleep_date"].sort_values().to_numpy()
        for date in test_dates:
            prev = train_dates[train_dates < date]
            nxt = train_dates[train_dates > date]
            prev_gap = int((date - prev[-1]) / np.timedelta64(1, "D")) if len(prev) else np.nan
            next_gap = int((nxt[0] - date) / np.timedelta64(1, "D")) if len(nxt) else np.nan
            rows.append(
                {
                    "subject_id": subject,
                    "sleep_date": pd.Timestamp(date).date().isoformat(),
                    "prev_train_gap_days": prev_gap,
                    "next_train_gap_days": next_gap,
                    "has_prev_train_le3": bool(np.isfinite(prev_gap) and prev_gap <= 3),
                    "has_next_train_le3": bool(np.isfinite(next_gap) and next_gap <= 3),
                    "bracketed_by_train_le3": bool(
                        np.isfinite(prev_gap) and prev_gap <= 3 and np.isfinite(next_gap) and next_gap <= 3
                    ),
                }
            )
    return pd.DataFrame(rows)


def group_summary(target_stats: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "entropy",
        "subject_loo_logloss_gain",
        "subject_rate_var",
        "icc_proxy",
        "same_label_rate_gap_le7",
        "persistence_lift_gap_le7",
        "transition_contrast",
    ]
    rows: list[dict[str, object]] = []
    for name, mask in {
        "Q_targets": target_stats["axis"].eq("Q"),
        "S_targets": target_stats["axis"].eq("S"),
        "E95_active_axis": target_stats["e95_axis"],
        "E95_inactive_axis": ~target_stats["e95_axis"],
    }.items():
        rec: dict[str, object] = {"group": name, "n_targets": int(mask.sum())}
        for metric in metrics:
            rec[f"mean_{metric}"] = float(target_stats.loc[mask, metric].mean())
        rows.append(rec)
    return pd.DataFrame(rows)


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "(empty)"
    cols = list(frame.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in frame.iterrows():
        vals = []
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                vals.append(f"{val:.6f}")
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    train, test = load()
    target_stats = target_axis_stats(train)
    dependencies = pairwise_dependency(train)
    calendar = test_calendar_context(train, test)
    groups = group_summary(target_stats)

    target_path = OUT / "e112_sauna_qs_temporal_axis_target_stats.csv"
    dep_path = OUT / "e112_sauna_qs_temporal_axis_pairwise_corr.csv"
    cal_path = OUT / "e112_sauna_qs_temporal_axis_test_calendar.csv"
    group_path = OUT / "e112_sauna_qs_temporal_axis_group_summary.csv"
    report_path = OUT / "e112_sauna_qs_temporal_axis_report.md"

    target_stats.to_csv(target_path, index=False)
    dependencies.to_csv(dep_path, index=False)
    calendar.to_csv(cal_path, index=False)
    groups.to_csv(group_path, index=False)

    s_group = groups.loc[groups["group"].eq("S_targets")].iloc[0]
    q_group = groups.loc[groups["group"].eq("Q_targets")].iloc[0]
    active_group = groups.loc[groups["group"].eq("E95_active_axis")].iloc[0]
    inactive_group = groups.loc[groups["group"].eq("E95_inactive_axis")].iloc[0]

    top_subject = target_stats.sort_values("subject_loo_logloss_gain", ascending=False).head(3)
    top_temporal = target_stats.sort_values("persistence_lift_gap_le7", ascending=False).head(3)
    dep_summary = dependencies.groupby("axis_pair")["corr"].agg(["mean", "max", "min", "count"]).reset_index()
    bracket_rate = float(calendar["bracketed_by_train_le3"].mean())
    prev_rate = float(calendar["has_prev_train_le3"].mean())
    next_rate = float(calendar["has_next_train_le3"].mean())

    report = f"""# E112 Sauna Q/S Temporal Axis Audit

## Question

E111 says E95 survives as target-axis surgery: mostly S-side movement plus a tiny Q2 component. If that is a real data-generating clue, the train label/order structure should show S or E95-active targets carrying more subject/temporal state than the inactive Q/Q3/S4 axes.

## Key Results

- S-target mean subject-LOO logloss gain: `{s_group['mean_subject_loo_logloss_gain']:.6f}` vs Q-target `{q_group['mean_subject_loo_logloss_gain']:.6f}`.
- S-target mean subject-rate variance: `{s_group['mean_subject_rate_var']:.6f}` vs Q-target `{q_group['mean_subject_rate_var']:.6f}`.
- S-target mean temporal persistence lift: `{s_group['mean_persistence_lift_gap_le7']:.6f}` vs Q-target `{q_group['mean_persistence_lift_gap_le7']:.6f}`.
- E95-active targets mean subject-LOO gain: `{active_group['mean_subject_loo_logloss_gain']:.6f}` vs inactive axes `{inactive_group['mean_subject_loo_logloss_gain']:.6f}`.
- E95-active targets mean temporal persistence lift: `{active_group['mean_persistence_lift_gap_le7']:.6f}` vs inactive axes `{inactive_group['mean_persistence_lift_gap_le7']:.6f}`.
- Test rows with nearby train context: prev<=3 days `{prev_rate:.6f}`, next<=3 days `{next_rate:.6f}`, bracketed by both `{bracket_rate:.6f}`.

## Strongest Subject-Prior Targets

{markdown_table(top_subject[['target', 'axis', 'e95_axis', 'subject_loo_logloss_gain', 'subject_rate_var', 'icc_proxy']])}

## Strongest Temporal-Persistence Targets

{markdown_table(top_temporal[['target', 'axis', 'e95_axis', 'same_label_rate_gap_le7', 'expected_same_by_prevalence', 'persistence_lift_gap_le7', 'transition_contrast']])}

## Pairwise Axis Correlations

{markdown_table(dep_summary)}

## Sauna Interpretation

This is a kill-test for H105, and the result is asymmetric rather than uniformly favorable. S/E95-active axes show stronger subject-state structure, while Q axes show stronger short temporal persistence. Because only a small fraction of test rows are tightly bracketed by nearby train labels, the Q temporal signal is difficult to transfer safely. This makes E95's S-heavy surgery more plausible as restricted subject/block-state translation, and it explains why broad Q/Q3 movement remains dangerous.

## Outputs

- `{target_path.name}`
- `{dep_path.name}`
- `{cal_path.name}`
- `{group_path.name}`
"""
    report_path.write_text(report)

    print(f"wrote {target_path}")
    print(f"wrote {dep_path}")
    print(f"wrote {cal_path}")
    print(f"wrote {group_path}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
