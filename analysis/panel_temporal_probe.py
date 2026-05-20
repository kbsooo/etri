from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


OUT_DIR = Path("outputs/data_probe")
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]


def feature_cols(df: pd.DataFrame) -> list[str]:
    blocked = set(KEYS + TARGETS + ["split"])
    return [c for c in df.columns if c not in blocked and pd.api.types.is_numeric_dtype(df[c])]


def markdown_table(frame: pd.DataFrame, max_rows: int | None = None) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(max_rows).copy() if max_rows is not None else frame.copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.4g}")
        else:
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else str(x))
    cols = [str(c) for c in view.columns]
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for row in view.itertuples(index=False):
        lines.append("| " + " | ".join(str(x).replace("\n", " ") for x in row) + " |")
    return "\n".join(lines)


def split_timing(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sid, g in df.sort_values("lifelog_date").groupby("subject_id"):
        tr = g[g["split"] == "train"]
        te = g[g["split"] == "test"]
        first_test = te["lifelog_date"].min()
        marks = "".join("T" if s == "train" else "P" for s in g["split"])
        rows.append(
            {
                "subject_id": sid,
                "n_days": len(g),
                "n_train": len(tr),
                "n_test": len(te),
                "date_min": g["lifelog_date"].min().date().isoformat(),
                "date_max": g["lifelog_date"].max().date().isoformat(),
                "train_after_first_test": int((tr["lifelog_date"] >= first_test).sum()),
                "pattern_head": marks[:50],
                "pattern_tail": marks[-50:],
            }
        )
    return pd.DataFrame(rows)


def nearest_train_dates(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = df[df["split"] == "train"]
    test = df[df["split"] == "test"]
    rows = []
    for sid, te in test.groupby("subject_id"):
        tr = train[train["subject_id"] == sid]
        tr_dates = tr["lifelog_date"].values.astype("datetime64[D]")
        for row in te.itertuples(index=False):
            d = np.datetime64(row.lifelog_date.date())
            deltas = np.abs((tr_dates - d).astype("timedelta64[D]").astype(int))
            rows.append({"subject_id": sid, "lifelog_date": row.lifelog_date.date().isoformat(), "nearest_train_gap_days": int(deltas.min())})
    nearest = pd.DataFrame(rows)
    summary = pd.DataFrame(
        [
            {
                "count": len(nearest),
                "median_gap": float(nearest["nearest_train_gap_days"].median()),
                "p90_gap": float(nearest["nearest_train_gap_days"].quantile(0.9)),
                "max_gap": int(nearest["nearest_train_gap_days"].max()),
                **{
                    f"within_{k}d": float((nearest["nearest_train_gap_days"] <= k).mean())
                    for k in [1, 2, 3, 5, 7, 14]
                },
            }
        ]
    )
    return nearest, summary


def adjacent_label_persistence(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = df[df["split"] == "train"].sort_values(["subject_id", "lifelog_date"])
    pairs = []
    for sid, g in train.groupby("subject_id"):
        for prev, cur in zip(g.iloc[:-1].itertuples(index=False), g.iloc[1:].itertuples(index=False)):
            gap = (cur.lifelog_date - prev.lifelog_date).days
            if gap <= 3:
                rec = {"subject_id": sid, "gap": gap}
                for target in TARGETS:
                    rec[target] = int(getattr(prev, target) == getattr(cur, target))
                pairs.append(rec)
    pair_df = pd.DataFrame(pairs)
    persistence = pair_df[TARGETS].mean().rename("adjacent_same_rate").reset_index().rename(columns={"index": "target"})
    marginal = df[df["split"] == "train"][TARGETS].mean().map(lambda p: max(p, 1 - p))
    persistence = persistence.merge(marginal.rename("marginal_same_baseline").reset_index().rename(columns={"index": "target"}), on="target")
    persistence["lift_vs_marginal"] = persistence["adjacent_same_rate"] - persistence["marginal_same_baseline"]
    return pair_df, persistence.sort_values("lift_vs_marginal", ascending=False)


def subject_rate_ranges(df: pd.DataFrame) -> pd.DataFrame:
    rates = df[df["split"] == "train"].groupby("subject_id")[TARGETS].mean()
    summary = pd.DataFrame({"min": rates.min(), "max": rates.max(), "range": rates.max() - rates.min(), "std": rates.std()})
    return summary.sort_values("range", ascending=False).reset_index().rename(columns={"index": "target"})


def feature_family_signal() -> tuple[pd.DataFrame, pd.DataFrame]:
    assoc = pd.read_csv(OUT_DIR / "feature_label_associations_top.csv")

    def fam(name: str) -> str:
        if name.startswith("mUsage_app_"):
            return "mUsage_app_vocab"
        for prefix in ["mUsage", "mWifi", "mBle", "mGps", "gps", "wPedo", "wLight", "hr", "wHr", "mScreen", "mAC", "mLight", "mAmbience", "subject"]:
            if name.startswith(prefix):
                return "mGps" if prefix == "gps" else prefix
        return name.split("_")[0]

    assoc["family"] = assoc["feature"].map(fam)
    counts = pd.crosstab(assoc["target"], assoc["family"]).reset_index()
    strength = assoc.groupby("family")["mi"].agg(["count", "mean", "max"]).sort_values("mean", ascending=False).reset_index()
    return counts, strength


def nearest_neighbor_label_smoothness(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in feature_cols(df) if df[c].notna().mean() >= 0.75]
    x = SimpleImputer(strategy="median").fit_transform(df[cols])
    x = StandardScaler().fit_transform(x)
    train_idx = np.where(df["split"].values == "train")[0]
    x_train = x[train_idx]
    nbrs = NearestNeighbors(n_neighbors=8, metric="euclidean").fit(x_train)
    _, idx = nbrs.kneighbors(x_train)
    rows = []
    train_view = df.iloc[train_idx].reset_index(drop=True)
    for k in [1, 3, 7]:
        same_by_row = []
        for row_pos, neigh in enumerate(idx[:, 1 : k + 1]):
            y = train_view.iloc[row_pos][TARGETS].astype(int).to_numpy()
            neigh_labels = train_view.iloc[neigh][TARGETS].astype(int).to_numpy()
            same_by_row.append((neigh_labels == y).mean(axis=0))
        rates = np.vstack(same_by_row).mean(axis=0)
        for target, value in zip(TARGETS, rates):
            rows.append({"k": k, "target": target, "neighbor_same_rate": float(value)})
    return pd.DataFrame(rows)


def raw_table_budget() -> pd.DataFrame:
    rows = []
    for path in sorted(Path("data/ch2025_data_items").glob("*.parquet")):
        meta = pd.read_parquet(path, columns=["subject_id", "timestamp"])
        rows.append(
            {
                "file": path.name,
                "rows": len(meta),
                "subjects": int(meta["subject_id"].nunique()),
                "time_min": str(meta["timestamp"].min()),
                "time_max": str(meta["timestamp"].max()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    df = pd.read_parquet(OUT_DIR / "all_subject_day_features.parquet")
    df["lifelog_date"] = pd.to_datetime(df["lifelog_date"])
    df["sleep_date"] = pd.to_datetime(df["sleep_date"])

    timing = split_timing(df)
    nearest, nearest_summary = nearest_train_dates(df)
    pairs, persistence = adjacent_label_persistence(df)
    subject_ranges = subject_rate_ranges(df)
    family_counts, family_strength = feature_family_signal()
    nn = nearest_neighbor_label_smoothness(df)
    raw = raw_table_budget()

    timing.to_csv(OUT_DIR / "panel_split_timing.csv", index=False)
    nearest.to_csv(OUT_DIR / "test_nearest_train_date.csv", index=False)
    nearest_summary.to_csv(OUT_DIR / "test_nearest_train_date_summary.csv", index=False)
    pairs.to_csv(OUT_DIR / "adjacent_label_pairs.csv", index=False)
    persistence.to_csv(OUT_DIR / "adjacent_label_persistence.csv", index=False)
    subject_ranges.to_csv(OUT_DIR / "subject_target_rate_ranges.csv", index=False)
    family_counts.to_csv(OUT_DIR / "top_association_family_counts.csv", index=False)
    family_strength.to_csv(OUT_DIR / "top_association_family_strength.csv", index=False)
    nn.to_csv(OUT_DIR / "sensor_nn_label_smoothness.csv", index=False)
    raw.to_csv(OUT_DIR / "raw_table_pretext_budget.csv", index=False)

    lines = [
        "# Panel and temporal probe",
        "",
        "## Split timing",
        markdown_table(timing),
        "",
        "## Test rows near labeled rows of same subject",
        markdown_table(nearest_summary),
        "",
        "## Adjacent labeled-day persistence",
        markdown_table(persistence),
        "",
        "## Subject target-rate ranges",
        markdown_table(subject_ranges),
        "",
        "## Top association feature families",
        markdown_table(family_strength),
        "",
        "## Sensor-nearest-neighbor label smoothness",
        markdown_table(nn),
        "",
        "## Raw table budget for self-supervised/pretext learning",
        markdown_table(raw),
    ]
    (OUT_DIR / "panel_temporal_probe.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_DIR / 'panel_temporal_probe.md'}")


if __name__ == "__main__":
    main()
