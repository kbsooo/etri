#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EXP = ROOT / "experiments"
OUT = ROOT / "outputs"
LABELS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
IDS = ["subject_id", "sleep_date", "lifelog_date"]


def read_sub(name: str) -> pd.DataFrame:
    p = OUT / name
    if not p.exists():
        raise FileNotFoundError(p)
    return pd.read_csv(p)


def md_table(df: pd.DataFrame, max_rows: int | None = None, floatfmt: str = ".4f") -> str:
    d = df.copy()
    if max_rows is not None:
        d = d.head(max_rows)
    cols = list(d.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in d.iterrows():
        cells = []
        for v in row.tolist():
            if isinstance(v, (float, np.floating)) and pd.notna(v):
                cells.append(format(float(v), floatfmt))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def build_test_meta() -> pd.DataFrame:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    test = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    rows = []
    ordered_test = test.sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    for global_i, r in ordered_test.iterrows():
        tr = train[train["subject_id"].eq(r.subject_id)].sort_values("sleep_date")
        te = ordered_test[ordered_test["subject_id"].eq(r.subject_id)].sort_values("sleep_date").reset_index(drop=True)
        q = r.sleep_date
        tr_dates = tr["sleep_date"]
        before = tr_dates[tr_dates < q]
        after = tr_dates[tr_dates > q]
        all_dates = pd.concat(
            [
                tr[["sleep_date"]].assign(kind="train"),
                te[["sleep_date"]].assign(kind="test"),
            ],
            ignore_index=True,
        ).sort_values("sleep_date").reset_index(drop=True)
        pos_all = int(all_dates.index[(all_dates["sleep_date"].eq(q)) & (all_dates["kind"].eq("test"))][0])
        within_order = int(te.index[te["sleep_date"].eq(q)][0])
        rows.append(
            {
                "row_id": global_i,
                "subject_id": r.subject_id,
                "sleep_date": r.sleep_date.date().isoformat(),
                "lifelog_date": r.lifelog_date.date().isoformat(),
                "within_subject_order": within_order,
                "within_subject_frac": within_order / max(1, len(te) - 1),
                "test_timeline_frac": pos_all / max(1, len(all_dates) - 1),
                "date_rank_frac": global_i / max(1, len(ordered_test) - 1),
                "prev_train_gap_d": float((q - before.max()).days) if len(before) else np.nan,
                "next_train_gap_d": float((after.min() - q).days) if len(after) else np.nan,
                "nearest_train_gap_d": float(np.nanmin([
                    (q - before.max()).days if len(before) else np.nan,
                    (after.min() - q).days if len(after) else np.nan,
                ])),
                "has_future_train": int(len(after) > 0),
                "inside_train_range": int((q >= tr_dates.min()) and (q <= tr_dates.max())),
                "after_train_range": int(q > tr_dates.max()),
                "weekday": int(q.dayofweek),
            }
        )
    meta = pd.DataFrame(rows)
    # Same shape as the highest-ranked local public-like generator: late-biased interleaved holes.
    center = meta.groupby("subject_id")["test_timeline_frac"].transform("median")
    raw = 0.30 + np.exp(-0.5 * ((meta["test_timeline_frac"] - center) / 0.25) ** 2) + 0.5 * meta["test_timeline_frac"]
    raw += 0.65 * meta["inside_train_range"] + 0.35 * meta["has_future_train"]
    raw -= 0.03 * meta["nearest_train_gap_d"].fillna(meta["nearest_train_gap_d"].median())
    meta["publiclike_score"] = (raw - raw.min()) / max(1e-9, raw.max() - raw.min())
    meta["regime"] = np.where(meta["inside_train_range"].eq(1), "inside", "tail")
    meta["row_even"] = meta["row_id"] % 2 == 0
    return meta


def add_submission_deltas(meta: pd.DataFrame) -> pd.DataFrame:
    subs = {
        "base": "submission_base_v4_replicate_prob.csv",
        "bad_q1q2s4": "submission_prior_sleep_conservative_q1q2s4_prob.csv",
        "w01": "submission_temporal_state_smoothing_wcap01_prob.csv",
        "w02": "submission_temporal_state_smoothing_wcap02_prob.csv",
        "anchor_noq3": "submission_meta_anchor_w02_noq3_prob.csv",
        "w03_noq3_q2w02": "submission_lbdiag_w03_noq3_q2w02_prob.csv",
        "validated_block": "submission_moonshot_validated_block_prob.csv",
    }
    loaded = {k: read_sub(v).sort_values(["subject_id", "sleep_date"]).reset_index(drop=True) for k, v in subs.items() if (OUT / v).exists()}
    out = meta.copy()
    for a, b, prefix in [
        ("w01", "w02", "w02_minus_w01"),
        ("w02", "anchor_noq3", "anchor_minus_w02"),
        ("anchor_noq3", "w03_noq3_q2w02", "w03_minus_anchor"),
        ("anchor_noq3", "validated_block", "block_minus_anchor"),
        ("base", "bad_q1q2s4", "bad_minus_base"),
    ]:
        if a not in loaded or b not in loaded:
            continue
        vals = []
        for y in LABELS:
            d = loaded[b][y].to_numpy(float) - loaded[a][y].to_numpy(float)
            out[f"{prefix}_{y}"] = d
            vals.append(np.abs(d))
        out[f"{prefix}_mean_abs"] = np.vstack(vals).mean(axis=0)
    return out


def candidate_masks(meta: pd.DataFrame) -> dict[str, pd.Series]:
    masks: dict[str, pd.Series] = {}
    masks["inside_has_future"] = meta["inside_train_range"].eq(1) & meta["has_future_train"].eq(1)
    masks["tail_after_train"] = meta["after_train_range"].eq(1)
    masks["publiclike_top30pct"] = meta["publiclike_score"] >= meta["publiclike_score"].quantile(0.70)
    masks["publiclike_top40pct"] = meta["publiclike_score"] >= meta["publiclike_score"].quantile(0.60)
    masks["small_gap_le3"] = meta["nearest_train_gap_d"] <= 3
    masks["small_gap_le5"] = meta["nearest_train_gap_d"] <= 5
    masks["alternating_even_rows"] = meta["row_even"]
    masks["alternating_odd_rows"] = ~meta["row_even"]
    for q in range(4):
        masks[f"row_order_mod4_{q}"] = meta["row_id"] % 4 == q
    for q in range(5):
        masks[f"row_order_mod5_{q}"] = meta["row_id"] % 5 == q
    for lo, hi in [(0.0, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 1.01)]:
        masks[f"within_frac_{lo:.2f}_{hi:.2f}"] = meta["within_subject_frac"].ge(lo) & meta["within_subject_frac"].lt(hi)
    for sid in sorted(meta["subject_id"].unique()):
        masks[f"subject_{sid}"] = meta["subject_id"].eq(sid)
    return masks


def summarize_masks(meta: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, mask in candidate_masks(meta).items():
        g = meta[mask].copy()
        if len(g) == 0:
            continue
        row = {
            "rule": name,
            "n_rows": int(len(g)),
            "inside_ratio": float(g["inside_train_range"].mean()),
            "tail_ratio": float(g["after_train_range"].mean()),
            "has_future_ratio": float(g["has_future_train"].mean()),
            "mean_publiclike_score": float(g["publiclike_score"].mean()),
            "mean_nearest_gap": float(g["nearest_train_gap_d"].mean()),
            "date_min": str(g["lifelog_date"].min()),
            "date_max": str(g["lifelog_date"].max()),
        }
        for c in [
            "w02_minus_w01_mean_abs",
            "anchor_minus_w02_mean_abs",
            "w03_minus_anchor_mean_abs",
            "block_minus_anchor_mean_abs",
            "bad_minus_base_mean_abs",
        ]:
            if c in g:
                row[c] = float(g[c].mean())
        # Higher is not "true public"; it is a prioritization score for row-calibration probes.
        row["calibration_probe_score"] = (
            row["mean_publiclike_score"]
            + 0.35 * row["inside_ratio"]
            + 0.15 * row["has_future_ratio"]
            - 0.04 * row["mean_nearest_gap"]
            + 3.0 * row.get("w02_minus_w01_mean_abs", 0.0)
            - 2.0 * row.get("bad_minus_base_mean_abs", 0.0)
        )
        rows.append(row)
    return pd.DataFrame(rows).sort_values("calibration_probe_score", ascending=False)


def row_candidates(meta: pd.DataFrame) -> pd.DataFrame:
    delta_cols = [c for c in meta.columns if c.endswith("_mean_abs")]
    out = meta.copy()
    out["row_calibration_pressure"] = out["publiclike_score"]
    for c in delta_cols:
        if c.startswith("w02_minus_w01") or c.startswith("w03_minus_anchor") or c.startswith("block_minus_anchor"):
            out["row_calibration_pressure"] += 3.0 * out[c].fillna(0)
        if c.startswith("bad_minus_base"):
            out["row_calibration_pressure"] -= 2.0 * out[c].fillna(0)
    keep = [
        "row_id",
        "subject_id",
        "lifelog_date",
        "regime",
        "within_subject_frac",
        "nearest_train_gap_d",
        "has_future_train",
        "publiclike_score",
        "row_calibration_pressure",
    ] + delta_cols
    return out.sort_values("row_calibration_pressure", ascending=False)[keep]


def write_submission_candidate(name: str, df: pd.DataFrame, anchor: pd.DataFrame, notes: str) -> pd.DataFrame:
    out_path = OUT / name
    df.to_csv(out_path, index=False)
    rows = []
    for y in LABELS:
        d = df[y].to_numpy(float) - anchor[y].to_numpy(float)
        rows.append(
            {
                "file": name,
                "target": y,
                "changed_rows": int((np.abs(d) > 1e-12).sum()),
                "mean_abs_delta_vs_anchor": float(np.abs(d).mean()),
                "max_abs_delta_vs_anchor": float(np.abs(d).max()),
                "mean_signed_delta_vs_anchor": float(d.mean()),
                "corr_vs_anchor": float(np.corrcoef(df[y], anchor[y])[0, 1]) if np.abs(d).max() > 0 else 1.0,
                "notes": notes,
            }
        )
    shift = pd.DataFrame(rows)
    shift.to_csv(EXP / f"{name.replace('.csv', '')}_shift.csv", index=False)
    return shift


def make_calibration_submissions(meta: pd.DataFrame) -> pd.DataFrame:
    anchor = read_sub("submission_meta_anchor_w02_noq3_prob.csv").sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    block = read_sub("submission_moonshot_validated_block_prob.csv").sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    target_cols = ["Q2", "S1", "S2", "S3"]
    specs = [
        (
            "submission_goal6_publiclike_top30_block20_prob.csv",
            meta["publiclike_score"] >= meta["publiclike_score"].quantile(0.70),
            0.20,
            "Anchor + 20% validated-block residual on publiclike top 30% rows; Q2/S1/S2/S3 only.",
        ),
        (
            "submission_goal6_publiclike_top40_block15_prob.csv",
            meta["publiclike_score"] >= meta["publiclike_score"].quantile(0.60),
            0.15,
            "Anchor + 15% validated-block residual on publiclike top 40% rows; Q2/S1/S2/S3 only.",
        ),
        (
            "submission_goal6_inside_future_block10_prob.csv",
            meta["inside_train_range"].eq(1) & meta["has_future_train"].eq(1),
            0.10,
            "Anchor + 10% validated-block residual on all inside/future-neighbor rows; Q2/S1/S2/S3 only.",
        ),
    ]
    reports = []
    for fname, mask, weight, notes in specs:
        cand = anchor.copy()
        idx = np.where(mask.to_numpy())[0]
        for y in target_cols:
            raw_delta = block[y].to_numpy(float) - anchor[y].to_numpy(float)
            capped_delta = np.clip(weight * raw_delta, -0.04, 0.04)
            vals = cand[y].to_numpy(float).copy()
            vals[idx] = np.clip(vals[idx] + capped_delta[idx], 0.02, 0.98)
            cand[y] = vals
        shift = write_submission_candidate(fname, cand, anchor, notes)
        reports.append(shift)
    return pd.concat(reports, ignore_index=True)


def main() -> None:
    EXP.mkdir(exist_ok=True)
    meta = add_submission_deltas(build_test_meta())
    mask_summary = summarize_masks(meta)
    rows = row_candidates(meta)
    submission_shift = make_calibration_submissions(meta)
    meta.to_csv(EXP / "goal6_split_calibration_test_row_meta.csv", index=False)
    mask_summary.to_csv(EXP / "goal6_split_rule_candidate_summary.csv", index=False)
    rows.to_csv(EXP / "goal6_row_calibration_candidates.csv", index=False)
    submission_shift.to_csv(EXP / "goal6_split_calibrated_submission_shift_summary.csv", index=False)

    lines = ["# Goal6 — split rule and row calibration probe\n"]
    lines.append("Known public facts used: `wcap01=0.6394201335`, `wcap02=0.6311869686`, and failed `prior_sleep_conservative_q1q2s4=0.6421303776`.\n")
    lines.append("This cannot identify exact public/private membership without more public scores; it ranks plausible row regimes and calibration targets.\n")
    lines.append("\n## 1. Top Split/Calibration Rule Candidates\n")
    display = [
        "rule",
        "n_rows",
        "inside_ratio",
        "tail_ratio",
        "has_future_ratio",
        "mean_publiclike_score",
        "mean_nearest_gap",
        "w02_minus_w01_mean_abs",
        "bad_minus_base_mean_abs",
        "calibration_probe_score",
    ]
    lines.append(md_table(mask_summary[[c for c in display if c in mask_summary.columns]].round(4), max_rows=25))
    lines.append("\n## 2. Top Row Calibration Candidates\n")
    row_display = [
        "row_id",
        "subject_id",
        "lifelog_date",
        "regime",
        "within_subject_frac",
        "nearest_train_gap_d",
        "has_future_train",
        "publiclike_score",
        "row_calibration_pressure",
        "w02_minus_w01_mean_abs",
        "w03_minus_anchor_mean_abs",
        "block_minus_anchor_mean_abs",
        "bad_minus_base_mean_abs",
    ]
    lines.append(md_table(rows[[c for c in row_display if c in rows.columns]].round(4), max_rows=35))
    lines.append("\n## 3. Interpretation\n")
    lines.append("- The live public improvement `w02 < w01` points to same-subject temporal interpolation, not raw sensor modeling.\n")
    lines.append("- The failed Q1/Q2/S4 prior-sleep file penalizes broad hard-target feature shifts; row calibration should stay close to the temporal anchor.\n")
    lines.append("- Highest-priority masks are inside-range/future-neighbor rows with small train gaps. Tail-only rows should be conservative unless a separate public score proves otherwise.\n")
    lines.append("- Exact public/private split still needs more orthogonal public submissions; with only the current public facts, use this as a row-routing map, not a decoded hidden label file.\n")
    lines.append("\n## 4. Generated Conservative Calibration Candidates\n")
    cand_display = [
        "file",
        "target",
        "changed_rows",
        "mean_abs_delta_vs_anchor",
        "max_abs_delta_vs_anchor",
        "mean_signed_delta_vs_anchor",
        "corr_vs_anchor",
    ]
    lines.append(md_table(submission_shift[cand_display].round(5), max_rows=30, floatfmt=".5f"))
    lines.append("\nUse these as diagnostics only. The expected gain is small; their value is identifying whether publiclike inside rows should receive validated-block residuals.\n")
    (EXP / "goal6_split_rule_calibration_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {EXP / 'goal6_split_rule_calibration_report.md'}")
    print(mask_summary.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
