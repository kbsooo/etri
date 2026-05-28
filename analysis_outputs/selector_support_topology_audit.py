from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

DETAIL_OUT = OUT / "selector_support_topology_audit.csv"
SOURCE_OUT = OUT / "selector_support_topology_by_source.csv"
TARGET_OUT = OUT / "selector_support_topology_by_target.csv"
ZONE_OUT = OUT / "selector_support_topology_zones.csv"
SHORTLIST_OUT = OUT / "selector_support_topology_shortlist.csv"
REPORT_OUT = OUT / "selector_support_topology_report.md"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]

SOURCES = [
    ("broad_pairwise_universe", OUT / "public_pairwise_order_selector_candidates.csv", 1),
    ("focused_label_flow_review", OUT / "focused_label_flow_survival_review.csv", 0),
    ("old_positive_rescore", OUT / "old_positive_anchor_pairwise_rescore.csv", 2),
    ("oof_top_rescore", OUT / "s4q3_oof_top_selector_rescore.csv", 3),
    ("block_measurement_rescore", OUT / "block_measurement_selector_rescore.csv", 4),
]


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_None._"
    view = df.copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.6g}")
        else:
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else str(x))
    lines = [
        "| " + " | ".join(view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]).replace("\n", " ") for col in view.columns) + " |")
    return "\n".join(lines)


def read_source(label: str, path: Path, priority: int) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if "source_path" not in df.columns:
        if "file" in df.columns:
            df["source_path"] = df["file"]
        else:
            return pd.DataFrame()
    keep = df.copy()
    keep["support_source"] = label
    keep["support_priority"] = priority
    if "candidate_bucket" not in keep.columns:
        keep["candidate_bucket"] = keep.get("candidate_family", label)
    if "dominant_target" not in keep.columns:
        move_cols = [f"move_abs_a2c8_{target}" for target in TARGETS if f"move_abs_a2c8_{target}" in keep.columns]
        if move_cols:
            keep["dominant_target"] = keep[move_cols].idxmax(axis=1).str.replace("move_abs_a2c8_", "", regex=False)
        else:
            keep["dominant_target"] = ""
    if "q3s4_move_share" not in keep.columns and "q3_s4_move_share" in keep.columns:
        keep["q3s4_move_share"] = keep["q3_s4_move_share"]
    if "q3s4_move_share" not in keep.columns:
        move_cols = [f"move_abs_a2c8_{target}" for target in TARGETS if f"move_abs_a2c8_{target}" in keep.columns]
        if all(f"move_abs_a2c8_{target}" in keep.columns for target in ["Q3", "S4"]) and move_cols:
            total = keep[move_cols].sum(axis=1).replace(0, np.nan)
            keep["q3s4_move_share"] = (keep["move_abs_a2c8_Q3"] + keep["move_abs_a2c8_S4"]) / total
        else:
            keep["q3s4_move_share"] = np.nan
    if "movement_scale" not in keep.columns:
        keep["movement_scale"] = keep.get("mean_abs_move_vs_a2c8", np.nan)
    if "old_majority" not in keep.columns:
        keep["old_majority"] = keep.get("beats_a2c8_scenario_rate", pd.Series(np.nan, index=keep.index)).fillna(0) >= 0.50
    if "pair_majority" not in keep.columns:
        keep["pair_majority"] = keep.get("pair_beats_a2c8_rate", pd.Series(np.nan, index=keep.index)).fillna(0) >= 0.70
    if "pair_strict_p90" not in keep.columns:
        keep["pair_strict_p90"] = keep.get("pair_delta_vs_a2c8_p90", pd.Series(np.nan, index=keep.index)).fillna(9) < 0
    keep["old_p90_close"] = keep.get("selector_p90_delta_vs_a2c8_public", pd.Series(np.nan, index=keep.index)).fillna(9) <= 0.00058
    keep["low_bad_axis"] = keep.get("bad_axis_abs_load", pd.Series(np.nan, index=keep.index)).fillna(9) <= 0.055
    keep["large_move"] = keep["movement_scale"].fillna(0) >= 0.0015
    keep["q3s4_shape70"] = keep["q3s4_move_share"].fillna(0) >= 0.70
    return keep


def load_union() -> pd.DataFrame:
    frames = [read_source(label, path, priority) for label, path, priority in SOURCES]
    frames = [df for df in frames if not df.empty]
    if not frames:
        raise RuntimeError("No selector support sources found.")
    all_rows = pd.concat(frames, ignore_index=True, sort=False)
    all_rows["source_path"] = all_rows["source_path"].astype(str)
    all_rows = all_rows[~all_rows.get("pool_source", "").astype(str).eq("known_anchor")].copy()
    sort_cols = ["support_priority", "pair_submit_gate", "pair_probe_gate", "pair_delta_vs_a2c8_p90"]
    sort_cols = [col for col in sort_cols if col in all_rows.columns]
    ascending = [True] + [False if col.endswith("_gate") else True for col in sort_cols[1:]]
    dedup = all_rows.sort_values(sort_cols, ascending=ascending).drop_duplicates("source_path", keep="first").copy()
    return dedup.reset_index(drop=True)


def add_zones(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["pair_majority"] = out["pair_majority"].fillna(False).astype(bool)
    out["old_majority"] = out["old_majority"].fillna(False).astype(bool)
    out["pair_probe_gate"] = out.get("pair_probe_gate", pd.Series(False, index=out.index)).fillna(False).astype(bool)
    out["pair_submit_gate"] = out.get("pair_submit_gate", pd.Series(False, index=out.index)).fillna(False).astype(bool)
    out["pair_control_better_than_a2c8_gate"] = out.get(
        "pair_control_better_than_a2c8_gate", pd.Series(False, index=out.index)
    ).fillna(False).astype(bool)
    out["two_selector_majority"] = out["pair_majority"] & out["old_majority"]
    out["pair_only"] = out["pair_majority"] & ~out["old_majority"]
    out["old_only"] = out["old_majority"] & ~out["pair_majority"]
    out["neither_support"] = ~out["pair_majority"] & ~out["old_majority"]
    out["near_submit_but_old_no"] = out["pair_probe_gate"] & (out.get("beats_a2c8_scenario_rate", 0).fillna(0) < 0.40)
    out["strict_candidate_shape"] = (
        out["low_bad_axis"].fillna(False)
        & out["large_move"].fillna(False)
        & (out["pair_delta_vs_a2c8_p90"].fillna(9) < 0)
        & out["old_majority"]
    )
    def zone(row: pd.Series) -> str:
        if bool(row["two_selector_majority"]):
            return "two_selector"
        if bool(row["pair_only"]):
            return "pair_only"
        if bool(row["old_only"]):
            return "old_only"
        if bool(row["pair_probe_gate"]):
            return "pair_probe_not_majority"
        return "neither"
    out["support_zone"] = out.apply(zone, axis=1)
    return out


def group_summary(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for keys, group in df.groupby(group_cols, dropna=False, sort=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        rec = {col: key for col, key in zip(group_cols, keys, strict=True)}
        rec.update(
            {
                "n": int(len(group)),
                "pair_strict_p90": int(group["pair_strict_p90"].fillna(False).sum()),
                "pair_majority": int(group["pair_majority"].fillna(False).sum()),
                "old_majority": int(group["old_majority"].fillna(False).sum()),
                "two_selector_majority": int(group["two_selector_majority"].fillna(False).sum()),
                "pair_probe": int(group["pair_probe_gate"].fillna(False).sum()),
                "pair_submit": int(group["pair_submit_gate"].fillna(False).sum()),
                "strict_candidate_shape": int(group["strict_candidate_shape"].fillna(False).sum()),
                "best_pair_p90": float(group["pair_delta_vs_a2c8_p90"].min()),
                "best_old_p90": float(group["selector_p90_delta_vs_a2c8_public"].min()),
                "median_old_rate": float(group["beats_a2c8_scenario_rate"].median()),
                "median_pair_rate": float(group["pair_beats_a2c8_rate"].median()),
                "median_move": float(group["movement_scale"].median()),
                "median_bad_axis": float(group["bad_axis_abs_load"].median()),
                "median_q3s4_share": float(group["q3s4_move_share"].median()),
            }
        )
        rows.append(rec)
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(
        ["two_selector_majority", "pair_strict_p90", "pair_majority", "old_majority", "best_pair_p90"],
        ascending=[False, False, False, False, True],
    ).reset_index(drop=True)


def write_report(df: pd.DataFrame, source_summary: pd.DataFrame, target_summary: pd.DataFrame, zone_summary: pd.DataFrame) -> None:
    key_cols = [
        "source_path",
        "support_source",
        "candidate_bucket",
        "support_zone",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "movement_scale",
        "q3s4_move_share",
        "dominant_target",
        "pair_probe_gate",
        "pair_submit_gate",
        "strict_candidate_shape",
    ]
    key_cols = [col for col in key_cols if col in df.columns]
    pair_only = df[df["pair_only"]].sort_values(["pair_delta_vs_a2c8_p90", "selector_p90_delta_vs_a2c8_public"]).head(25)
    old_only = df[df["old_only"]].sort_values(["selector_p90_delta_vs_a2c8_public", "pair_delta_vs_a2c8_p90"]).head(25)
    probes = df[df["pair_probe_gate"]].sort_values(["pair_delta_vs_a2c8_p90", "selector_p90_delta_vs_a2c8_public"]).head(25)
    strict_shape = df[df["strict_candidate_shape"]].head(25)

    lines = [
        "# Selector Support Topology Audit",
        "",
        "Question: where do pairwise-public support and old hidden-subset support agree or disagree across the already scored candidate universe?",
        "",
        "## Zone Summary",
        "",
        markdown_table(zone_summary),
        "",
        "## Source Summary",
        "",
        markdown_table(source_summary.head(40)),
        "",
        "## Dominant Target Summary",
        "",
        markdown_table(target_summary.head(40)),
        "",
        "## Pair-Only Candidates",
        "",
        markdown_table(pair_only[key_cols]),
        "",
        "## Old-Only Candidates",
        "",
        markdown_table(old_only[key_cols]),
        "",
        "## Pair Probe Candidates",
        "",
        markdown_table(probes[key_cols]),
        "",
        "## Strict Candidate Shape",
        "",
        markdown_table(strict_shape[key_cols]),
        "",
        "## Read",
        "",
        "- `two_selector_majority` is the missing cell. If this remains empty, current candidates do not contain a robust public-positive direction.",
        "- `pair_only` mostly means a candidate sits on the pairwise-public surrogate but lacks hidden-subset support; these are diagnostic sensors, not submissions.",
        "- `old_only` means the old selector sees something, but the pairwise public order vetoes it; these candidates are useful for selector reconciliation, not direct submission.",
        "- A useful next candidate must move from pair-only/old-only into two-selector support, or produce a new anchor that explains why one selector should be retired.",
        "",
        "## Files",
        "",
        f"- `{DETAIL_OUT.name}`",
        f"- `{SOURCE_OUT.name}`",
        f"- `{TARGET_OUT.name}`",
        f"- `{ZONE_OUT.name}`",
        f"- `{SHORTLIST_OUT.name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df = add_zones(load_union())
    source_summary = group_summary(df, ["support_source"])
    target_summary = group_summary(df, ["dominant_target"])
    zone_summary = group_summary(df, ["support_zone"])

    df.to_csv(DETAIL_OUT, index=False)
    source_summary.to_csv(SOURCE_OUT, index=False)
    target_summary.to_csv(TARGET_OUT, index=False)
    zone_summary.to_csv(ZONE_OUT, index=False)

    shortlist = df[
        df["two_selector_majority"]
        | df["pair_only"]
        | df["old_only"]
        | df["pair_probe_gate"]
        | df["strict_candidate_shape"]
    ].copy()
    shortlist_cols = [
        "source_path",
        "support_source",
        "candidate_bucket",
        "support_zone",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "movement_scale",
        "q3s4_move_share",
        "dominant_target",
        "pair_probe_gate",
        "pair_submit_gate",
        "strict_candidate_shape",
    ]
    shortlist_cols = [col for col in shortlist_cols if col in shortlist.columns]
    shortlist.sort_values(
        ["two_selector_majority", "pair_submit_gate", "pair_probe_gate", "pair_delta_vs_a2c8_p90"],
        ascending=[False, False, False, True],
    )[shortlist_cols].head(250).to_csv(SHORTLIST_OUT, index=False)

    write_report(df, source_summary, target_summary, zone_summary)

    print(REPORT_OUT)
    print("[zone summary]")
    print(zone_summary.to_string(index=False))
    print("[source summary]")
    print(source_summary.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
