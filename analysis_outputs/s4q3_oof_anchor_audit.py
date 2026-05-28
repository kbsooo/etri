from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TRAIN_PATH = ROOT / "data" / "ch2026_metrics_train.csv"
BASE_OOF = OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
Q3S4 = ["Q3", "S4"]
EPS = 1e-6


def logloss(y: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, EPS, 1 - EPS)
    return float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())


def target_losses(y: np.ndarray, p: np.ndarray) -> dict[str, float]:
    return {t: logloss(y[:, i], p[:, i]) for i, t in enumerate(TARGETS)}


def scenario_indices(train: pd.DataFrame) -> dict[str, np.ndarray]:
    scenarios: dict[str, np.ndarray] = {"all": np.arange(len(train))}
    for sid, idx in train.groupby("subject_id").indices.items():
        scenarios[f"subject:{sid}"] = np.asarray(idx, dtype=int)
    order = np.arange(len(train))
    for k, part in enumerate(np.array_split(order, 5)):
        scenarios[f"rowblock:{k}"] = np.asarray(part, dtype=int)
    dates = pd.to_datetime(train["sleep_date"])
    month = dates.dt.to_period("M").astype(str)
    for m, idx in train.groupby(month).indices.items():
        scenarios[f"month:{m}"] = np.asarray(idx, dtype=int)
    return scenarios


def stem_from_oof(path: Path) -> str:
    name = path.name
    if name.startswith("final_") and name.endswith("_oof.npy"):
        return name[len("final_") : -len("_oof.npy")]
    if name.endswith("_oof.npy"):
        return name[: -len("_oof.npy")]
    return path.stem


def build_csv_lookup() -> dict[str, Path]:
    lookup: dict[str, Path] = {}
    for folder in [OUT, ROOT / "jepa", ROOT]:
        if not folder.exists():
            continue
        for path in folder.glob("submission*.csv"):
            lookup.setdefault(path.name, path)
    return lookup


def match_submission(oof_path: Path, csv_lookup: dict[str, Path]) -> tuple[str | None, str | None]:
    stem = stem_from_oof(oof_path)
    candidates = [
        f"submission_{stem}.csv",
        f"{stem}.csv" if stem.startswith("submission_") else "",
    ]
    for name in candidates:
        if name and name in csv_lookup:
            path = csv_lookup[name]
            return path.name, str(path.relative_to(ROOT))
    return None, None


def load_pairwise() -> pd.DataFrame:
    path = OUT / "public_pairwise_order_selector_candidates.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    keep = [
        "basename",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "pair_probe_gate",
        "pair_control_better_than_a2c8_gate",
        "pair_submit_gate",
        "pair_selector_conflict",
        "q3s4_move_share",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "candidate_family",
    ]
    keep = [c for c in keep if c in df.columns]
    return df[keep].drop_duplicates("basename")


def load_old_selector() -> pd.DataFrame:
    frames = []
    for path in [
        OUT / "old_positive_anchor_pairwise_rescore.csv",
        OUT / "focused_label_flow_survival_review.csv",
    ]:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "basename" not in df.columns:
            if "file" in df.columns:
                df["basename"] = df["file"].map(lambda x: Path(str(x)).name)
            elif "source_path" in df.columns:
                df["basename"] = df["source_path"].map(lambda x: Path(str(x)).name)
        keep = [
            "basename",
            "selector_p90_delta_vs_a2c8_public",
            "beats_a2c8_scenario_rate",
            "scenario_majority_beats_a2c8",
            "resolved_better_than_a2c8_gate",
        ]
        keep = [c for c in keep if c in df.columns]
        if keep:
            frames.append(df[keep])
    if not frames:
        return pd.DataFrame()
    merged = pd.concat(frames, ignore_index=True)
    merged = merged.sort_values(
        ["basename", "beats_a2c8_scenario_rate"], ascending=[True, False]
    )
    return merged.drop_duplicates("basename")


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_None._"
    view = df.copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.6g}")
        else:
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else str(x))
    headers = list(view.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in view.iterrows():
        vals = [str(row[col]).replace("\n", " ") for col in headers]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    train = pd.read_csv(TRAIN_PATH)
    y = train[TARGETS].to_numpy(float)
    base = np.load(BASE_OOF)
    base_losses = target_losses(y, base)
    scenarios = scenario_indices(train)
    csv_lookup = build_csv_lookup()

    records = []
    for path in sorted(OUT.glob("*_oof.npy")):
        try:
            pred = np.load(path)
        except Exception:
            continue
        if pred.shape != y.shape:
            continue

        losses = target_losses(y, pred)
        deltas = {f"delta_{t}": losses[t] - base_losses[t] for t in TARGETS}
        q3s4_delta = float(np.mean([deltas["delta_Q3"], deltas["delta_S4"]]))
        overall_delta = logloss(y, pred) - logloss(y, base)

        scenario_deltas = []
        for _, idx in scenarios.items():
            if len(idx) == 0:
                continue
            cand_q3 = logloss(y[idx, 2], pred[idx, 2])
            cand_s4 = logloss(y[idx, 6], pred[idx, 6])
            base_q3 = logloss(y[idx, 2], base[idx, 2])
            base_s4 = logloss(y[idx, 6], base[idx, 6])
            scenario_deltas.append(((cand_q3 - base_q3) + (cand_s4 - base_s4)) / 2)
        scenario_deltas = np.asarray(scenario_deltas, dtype=float)

        basename, source_path = match_submission(path, csv_lookup)
        rec = {
            "oof_path": str(path.relative_to(ROOT)),
            "oof_stem": stem_from_oof(path),
            "matched_submission": basename,
            "matched_source_path": source_path,
            "overall_delta_vs_stage2_oof": overall_delta,
            "q3s4_delta_vs_stage2_oof": q3s4_delta,
            "q3_delta_vs_stage2_oof": deltas["delta_Q3"],
            "s4_delta_vs_stage2_oof": deltas["delta_S4"],
            "q3s4_scenario_mean": float(scenario_deltas.mean()),
            "q3s4_scenario_p90": float(np.quantile(scenario_deltas, 0.90)),
            "q3s4_scenario_worst": float(scenario_deltas.max()),
            "q3s4_scenario_win_rate": float((scenario_deltas < 0).mean()),
        }
        records.append(rec)

    scored = pd.DataFrame(records)
    pair = load_pairwise()
    old = load_old_selector()
    if not pair.empty:
        scored = scored.merge(pair, left_on="matched_submission", right_on="basename", how="left")
        scored = scored.drop(columns=[c for c in ["basename"] if c in scored.columns])
    if not old.empty:
        scored = scored.merge(old, left_on="matched_submission", right_on="basename", how="left")
        scored = scored.drop(columns=[c for c in ["basename"] if c in scored.columns])

    scored["local_q3s4_strong"] = (
        (scored["q3s4_delta_vs_stage2_oof"] < -0.002)
        & (scored["q3s4_scenario_win_rate"] >= 0.60)
        & (scored["q3s4_scenario_p90"] < 0)
    )
    scored["pair_public_positive"] = (
        (scored.get("pair_delta_vs_a2c8_p90", np.nan) < 0)
        | (scored.get("pair_beats_a2c8_rate", np.nan) >= 0.70)
    )
    scored["old_public_positive"] = (
        (scored.get("beats_a2c8_scenario_rate", np.nan) >= 0.50)
        | (scored.get("scenario_majority_beats_a2c8", False) == True)
    )
    scored["q3s4_shape"] = scored.get("q3s4_move_share", np.nan) >= 0.70
    scored["oof_anchor_like"] = (
        scored["local_q3s4_strong"]
        & scored["pair_public_positive"].fillna(False)
        & scored["old_public_positive"].fillna(False)
    )
    scored["strict_s4q3_anchor_like"] = scored["oof_anchor_like"] & scored["q3s4_shape"].fillna(False)

    scored = scored.sort_values(
        ["strict_s4q3_anchor_like", "oof_anchor_like", "q3s4_delta_vs_stage2_oof"],
        ascending=[False, False, True],
    )
    out_csv = OUT / "s4q3_oof_anchor_audit.csv"
    scored.to_csv(out_csv, index=False)

    shortlist = scored[
        scored["local_q3s4_strong"]
        | scored["oof_anchor_like"]
        | scored["pair_public_positive"].fillna(False)
        | scored["old_public_positive"].fillna(False)
    ].head(80)
    shortlist.to_csv(OUT / "s4q3_oof_anchor_audit_shortlist.csv", index=False)

    summary = pd.DataFrame(
        [
            {
                "n_oof": len(scored),
                "matched_submission": int(scored["matched_submission"].notna().sum()),
                "matched_pairwise": int(scored["pair_delta_vs_a2c8_p90"].notna().sum())
                if "pair_delta_vs_a2c8_p90" in scored.columns
                else 0,
                "matched_old": int(scored["beats_a2c8_scenario_rate"].notna().sum())
                if "beats_a2c8_scenario_rate" in scored.columns
                else 0,
                "local_q3s4_strong": int(scored["local_q3s4_strong"].sum()),
                "pair_public_positive": int(scored["pair_public_positive"].fillna(False).sum()),
                "old_public_positive": int(scored["old_public_positive"].fillna(False).sum()),
                "oof_anchor_like": int(scored["oof_anchor_like"].sum()),
                "strict_s4q3_anchor_like": int(scored["strict_s4q3_anchor_like"].sum()),
            }
        ]
    )
    summary.to_csv(OUT / "s4q3_oof_anchor_audit_summary.csv", index=False)

    corr_lines = []
    for x in ["q3s4_delta_vs_stage2_oof", "q3s4_scenario_p90", "overall_delta_vs_stage2_oof"]:
        for ycol in ["pair_delta_vs_a2c8_p90", "selector_p90_delta_vs_a2c8_public"]:
            if x in scored.columns and ycol in scored.columns:
                sub = scored[[x, ycol]].dropna()
                if len(sub) >= 5:
                    corr_lines.append(f"- corr({x}, {ycol}) = `{sub[x].corr(sub[ycol]):.3f}` over n={len(sub)}")

    top_cols = [
        "oof_path",
        "matched_submission",
        "q3s4_delta_vs_stage2_oof",
        "q3s4_scenario_p90",
        "q3s4_scenario_win_rate",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "q3s4_move_share",
        "local_q3s4_strong",
        "oof_anchor_like",
        "strict_s4q3_anchor_like",
    ]
    top_cols = [c for c in top_cols if c in scored.columns]
    top_local = scored.sort_values("q3s4_delta_vs_stage2_oof").head(12)[top_cols]
    anchors = scored[scored["oof_anchor_like"]][top_cols]

    report = [
        "# S4/Q3 OOF Anchor Audit",
        "",
        "Question: can existing OOF validation act as the missing independent S4/Q3 anchor?",
        "",
        "## Summary",
        "",
        markdown_table(summary),
        "",
        "## Correlations",
        "",
        "\n".join(corr_lines) if corr_lines else "_No sufficient overlap._",
        "",
        "## Top Local Q3/S4 OOF Improvements",
        "",
        markdown_table(top_local),
        "",
        "## OOF Anchor-Like Candidates",
        "",
        markdown_table(anchors),
        "",
        "## Interpretation",
        "",
    ]
    if int(summary.loc[0, "strict_s4q3_anchor_like"]) == 0:
        report.extend(
            [
                "- Existing OOF files can be used as local sensors, but they do not currently provide a strict S4/Q3 public anchor.",
                "- If local Q3/S4 gains do not overlap with both public-sensitive selectors, OOF is another validation view rather than a resolution of the selector conflict.",
                "- The next useful action is to inspect the strongest local Q3/S4 OOF families and ask whether their signal is row-order/blockwise stable or only local-CV favorable.",
            ]
        )
    else:
        report.extend(
            [
                "- At least one existing OOF candidate overlaps local Q3/S4 strength and both selectors.",
                "- This candidate family should be decomposed targetwise and row-blockwise before any public submission.",
            ]
        )
    (OUT / "s4q3_oof_anchor_audit_report.md").write_text("\n".join(report) + "\n")


if __name__ == "__main__":
    main()
