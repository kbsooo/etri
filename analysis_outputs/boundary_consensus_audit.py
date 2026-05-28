from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

import deep_dive_analysis as d  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
SORT_KEY = ["subject_id", "lifelog_date"]
EPS = 1e-5

BASES = {
    "stage2": (
        "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy",
    ),
    "public2d0": (
        "submission_public2dblend_budget0p0.csv",
        "final_public2dblend_budget0p0_oof.npy",
    ),
    "proj0": (
        "submission_projblend_cap0p0.csv",
        "final_projblend_cap0p0_oof.npy",
    ),
    "minimax": (
        "submission_public_minimaxens_r01_a6_h422045.csv",
        "final_public_minimaxens_r01_a6_h422045_oof.npy",
    ),
}

ANCHOR = "submission_hybrid_0p578_logit_after_subject_final9_strict.csv"
STAGE2 = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
ORDINAL = "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv"
STAGE2_OOF = "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"


@dataclass(frozen=True)
class BoundaryBundle:
    case: np.ndarray
    anchor_prob: np.ndarray
    block_id: np.ndarray
    prev_gap: np.ndarray
    next_gap: np.ndarray


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -40.0, 40.0)))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float((-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp))).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def stable_tag(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def load_labels() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(SORT_KEY).reset_index(drop=True)
    sub = sub.sort_values(SORT_KEY).reset_index(drop=True)
    return train, sub


def load_sub(file_name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def one_axis_metrics(sub_pred: np.ndarray) -> dict[str, float]:
    obs = pd.read_csv(OUT / "public_probe_observations.csv").set_index("file")["public_lb"].astype(float)
    stage2_public = float(obs[STAGE2])
    public_gap = float(obs[ORDINAL] - obs[STAGE2])
    stage2_vec = load_sub(STAGE2)[TARGETS].to_numpy(dtype=float).reshape(-1)
    bad = load_sub(ORDINAL)[TARGETS].to_numpy(dtype=float).reshape(-1) - stage2_vec
    move = sub_pred.reshape(-1) - stage2_vec
    denom = float(np.dot(bad, bad))
    projection = float(np.dot(move, bad) / denom) if denom > 0 else 0.0
    return {
        "one_axis_bad_projection": projection,
        "one_axis_public_est": stage2_public + projection * public_gap,
        "one_axis_public_delta_vs_stage2": projection * public_gap,
    }


def two_axis_metrics(sub_pred: np.ndarray) -> dict[str, float]:
    obs = pd.read_csv(OUT / "public_probe_observations.csv").set_index("file")["public_lb"].astype(float)
    anchor_public = float(obs[ANCHOR])
    stage2_public = float(obs[STAGE2])
    ordinal_public = float(obs[ORDINAL])
    good_gap = stage2_public - anchor_public
    bad_gap = ordinal_public - stage2_public
    anchor_vec = load_sub(ANCHOR)[TARGETS].to_numpy(dtype=float).reshape(-1)
    stage2_vec = load_sub(STAGE2)[TARGETS].to_numpy(dtype=float).reshape(-1)
    ordinal_vec = load_sub(ORDINAL)[TARGETS].to_numpy(dtype=float).reshape(-1)
    axes = np.column_stack([stage2_vec - anchor_vec, ordinal_vec - stage2_vec])
    move = sub_pred.reshape(-1) - stage2_vec
    coef = np.linalg.lstsq(axes, move, rcond=None)[0]
    fitted = axes @ coef
    move_norm = float(np.linalg.norm(move))
    residual_ratio = float(np.linalg.norm(move - fitted) / max(move_norm, 1e-12))
    return {
        "good_axis_coef": float(coef[0]),
        "bad_axis_coef": float(coef[1]),
        "two_axis_residual_ratio": residual_ratio,
        "two_axis_public_est": stage2_public + float(coef[0]) * good_gap + float(coef[1]) * bad_gap,
        "two_axis_public_delta_vs_stage2": float(coef[0]) * good_gap + float(coef[1]) * bad_gap,
    }


def combined_unknown_blocks(ref: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    known = ref[KEY].copy()
    known["_kind"] = "known"
    unknown = rows[KEY].copy()
    unknown["_kind"] = "unknown"
    unknown["_row_pos"] = np.arange(len(rows))
    full = pd.concat([known, unknown], ignore_index=True, sort=False).sort_values(KEY).reset_index(drop=True)
    full["_block"] = full.groupby("subject_id")["_kind"].transform(lambda s: s.ne(s.shift()).cumsum()).astype(int)
    return full[full["_kind"].eq("unknown")].copy()


def boundary_bundle(ref: pd.DataFrame, rows: pd.DataFrame) -> BoundaryBundle:
    rows_reset = rows.reset_index(drop=True)
    unknown = combined_unknown_blocks(ref, rows_reset)
    case = np.full((len(rows_reset), len(TARGETS)), "none", dtype=object)
    anchor_prob = np.full((len(rows_reset), len(TARGETS)), 0.5, dtype=float)
    block_id = np.full(len(rows_reset), "", dtype=object)
    prev_gap = np.full(len(rows_reset), np.nan, dtype=float)
    next_gap = np.full(len(rows_reset), np.nan, dtype=float)
    ref_by_subject = {
        sid: g.sort_values("lifelog_date").reset_index(drop=True)
        for sid, g in ref.groupby("subject_id", sort=False)
    }
    for (sid, bid), block in unknown.groupby(["subject_id", "_block"], sort=False):
        locs = block["_row_pos"].to_numpy(dtype=int)
        start = rows_reset.loc[locs, "lifelog_date"].min()
        end = rows_reset.loc[locs, "lifelog_date"].max()
        block_id[locs] = f"{sid}_b{int(bid)}"
        hist = ref_by_subject.get(sid)
        if hist is None or hist.empty:
            continue
        before = hist[hist["lifelog_date"] < start]
        after = hist[hist["lifelog_date"] > end]
        prev = before.iloc[-1] if not before.empty else None
        nxt = after.iloc[0] if not after.empty else None
        if prev is not None:
            prev_gap[locs] = max(int((start - prev["lifelog_date"]).days), 1)
        if nxt is not None:
            next_gap[locs] = max(int((nxt["lifelog_date"] - end).days), 1)
        for j, target in enumerate(TARGETS):
            pv = None if prev is None else int(prev[target])
            nv = None if nxt is None else int(nxt[target])
            if pv is not None and nv is not None:
                if pv == nv == 0:
                    local_case = "same0"
                    p = 0.15
                elif pv == nv == 1:
                    local_case = "same1"
                    p = 0.85
                else:
                    local_case = "diff01" if pv == 0 else "diff10"
                    p = 0.50
            elif pv is not None:
                local_case = "prev0" if pv == 0 else "prev1"
                p = 0.25 if pv == 0 else 0.75
            elif nv is not None:
                local_case = "next0" if nv == 0 else "next1"
                p = 0.25 if nv == 0 else 0.75
            else:
                local_case = "none"
                p = 0.50
            case[locs, j] = local_case
            anchor_prob[locs, j] = p
    return BoundaryBundle(case=case, anchor_prob=anchor_prob, block_id=block_id, prev_gap=prev_gap, next_gap=next_gap)


def bundle_for_folds(rows: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]]) -> BoundaryBundle:
    case = np.full((len(rows), len(TARGETS)), "none", dtype=object)
    anchor_prob = np.full((len(rows), len(TARGETS)), 0.5, dtype=float)
    block_id = np.full(len(rows), "", dtype=object)
    prev_gap = np.full(len(rows), np.nan, dtype=float)
    next_gap = np.full(len(rows), np.nan, dtype=float)
    for fold_id, (tr_idx, val_idx) in enumerate(folds):
        local = boundary_bundle(rows.iloc[tr_idx].copy(), rows.iloc[val_idx].copy())
        case[val_idx] = local.case
        anchor_prob[val_idx] = local.anchor_prob
        block_id[val_idx] = np.asarray([f"f{fold_id}_{b}" for b in local.block_id], dtype=object)
        prev_gap[val_idx] = local.prev_gap
        next_gap[val_idx] = local.next_gap
    return BoundaryBundle(case=case, anchor_prob=anchor_prob, block_id=block_id, prev_gap=prev_gap, next_gap=next_gap)


def adjust_pred(
    base: np.ndarray,
    bundle: BoundaryBundle,
    weights: np.ndarray,
    mode: str = "same",
) -> np.ndarray:
    out = clip(base.copy())
    z = logit(out)
    target_z = logit(bundle.anchor_prob)
    if mode == "same":
        mask = np.isin(bundle.case, ["same0", "same1"])
    elif mode == "same_or_single":
        mask = np.isin(bundle.case, ["same0", "same1", "prev0", "prev1", "next0", "next1"])
    elif mode == "ones_only":
        mask = np.isin(bundle.case, ["same1"])
    elif mode == "zeros_only":
        mask = np.isin(bundle.case, ["same0"])
    else:
        raise ValueError(mode)
    w = np.asarray(weights, dtype=float).reshape(1, -1)
    out_z = np.where(mask, (1.0 - w) * z + w * target_z, z)
    return clip(sigmoid(out_z))


def target_losses(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: loss_col(y[:, j], pred[:, j]) for j, target in enumerate(TARGETS)}


def row_case_summary(train: pd.DataFrame, bundle: BoundaryBundle, base_pred: np.ndarray) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows: list[dict[str, object]] = []
    for j, target in enumerate(TARGETS):
        for local_case in sorted(pd.unique(bundle.case[:, j])):
            mask = bundle.case[:, j] == local_case
            if not mask.any():
                continue
            yy = y[mask, j]
            p = base_pred[mask, j]
            anchor = bundle.anchor_prob[mask, j]
            rows.append(
                {
                    "target": target,
                    "case": local_case,
                    "n_rows": int(mask.sum()),
                    "n_blocks": int(pd.Series(bundle.block_id[mask]).nunique()),
                    "true_rate": float(yy.mean()),
                    "base_mean_pred": float(p.mean()),
                    "anchor_mean_pred": float(anchor.mean()),
                    "base_loss": loss_col(yy, p),
                    "anchor_loss": loss_col(yy, anchor),
                    "anchor_delta": loss_col(yy, anchor) - loss_col(yy, p),
                }
            )
    return pd.DataFrame(rows).sort_values(["target", "case"]).reset_index(drop=True)


def block_case_summary(train: pd.DataFrame, bundle: BoundaryBundle) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows: list[dict[str, object]] = []
    for j, target in enumerate(TARGETS):
        df = pd.DataFrame(
            {
                "block_id": bundle.block_id,
                "case": bundle.case[:, j],
                "y": y[:, j],
            }
        )
        for (local_case, bid), g in df.groupby(["case", "block_id"], sort=False):
            rows.append(
                {
                    "target": target,
                    "case": local_case,
                    "block_id": bid,
                    "n": int(len(g)),
                    "block_rate": float(g["y"].mean()),
                }
            )
    block = pd.DataFrame(rows)
    out_rows = []
    for (target, local_case), g in block.groupby(["target", "case"], sort=False):
        out_rows.append(
            {
                "target": target,
                "case": local_case,
                "n_blocks": int(len(g)),
                "n_rows": int(g["n"].sum()),
                "block_rate_mean": float(g["block_rate"].mean()),
                "block_rate_std": float(g["block_rate"].std(ddof=0)) if len(g) > 1 else 0.0,
                "row_weighted_rate": float(np.average(g["block_rate"], weights=g["n"])),
            }
        )
    return pd.DataFrame(out_rows).sort_values(["target", "case"]).reset_index(drop=True)


def scan_weights(
    train: pd.DataFrame,
    base_name: str,
    base_oof: np.ndarray,
    bundle: BoundaryBundle,
) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    base_loss = mean_loss(y, base_oof)
    rows: list[dict[str, object]] = []
    grids = [0.0, 0.01, 0.02, 0.035, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30]
    modes = ["same", "same_or_single", "ones_only", "zeros_only"]
    for mode in modes:
        for weight in grids:
            weights = np.full(len(TARGETS), weight, dtype=float)
            pred = adjust_pred(base_oof, bundle, weights, mode=mode)
            row = {
                "base": base_name,
                "mode": mode,
                "scheme": "global_weight",
                "weights": f"{weight:g}",
                "mean": mean_loss(y, pred),
                "delta_vs_base": mean_loss(y, pred) - base_loss,
            }
            row.update(target_losses(y, pred))
            rows.append(row)
    # Target-specific apparent best: useful as an upper bound, not as a final selector.
    for mode in modes:
        target_weights = np.zeros(len(TARGETS), dtype=float)
        for j in range(len(TARGETS)):
            best_w = 0.0
            best_loss = loss_col(y[:, j], base_oof[:, j])
            for weight in grids:
                w = np.zeros(len(TARGETS), dtype=float)
                w[j] = weight
                pred = adjust_pred(base_oof, bundle, w, mode=mode)
                loss = loss_col(y[:, j], pred[:, j])
                if loss < best_loss:
                    best_loss = loss
                    best_w = weight
            target_weights[j] = best_w
        pred = adjust_pred(base_oof, bundle, target_weights, mode=mode)
        row = {
            "base": base_name,
            "mode": mode,
            "scheme": "target_best_apparent",
            "weights": "|".join(f"{target}:{target_weights[j]:g}" for j, target in enumerate(TARGETS)),
            "mean": mean_loss(y, pred),
            "delta_vs_base": mean_loss(y, pred) - base_loss,
        }
        row.update(target_losses(y, pred))
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["base", "mean"]).reset_index(drop=True)


def nested_select_weights(
    train: pd.DataFrame,
    base_oof: np.ndarray,
    mode: str,
    grid: list[float],
) -> tuple[np.ndarray, pd.DataFrame, pd.DataFrame]:
    y = train[TARGETS].to_numpy(dtype=int)
    outer = d.make_folds(train, "subject_blocks")
    pred = base_oof.copy()
    selected_rows: list[dict[str, object]] = []
    for outer_id, (tr_idx, val_idx) in enumerate(outer):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        inner_folds = d.make_folds(outer_train, "subject_blocks")
        inner_global = np.asarray(tr_idx)
        inner_bundle_local = bundle_for_folds(outer_train, inner_folds)
        inner_bundle = BoundaryBundle(
            case=inner_bundle_local.case,
            anchor_prob=inner_bundle_local.anchor_prob,
            block_id=inner_bundle_local.block_id,
            prev_gap=inner_bundle_local.prev_gap,
            next_gap=inner_bundle_local.next_gap,
        )
        inner_base = base_oof[inner_global]
        inner_y = y[inner_global]
        weights = np.zeros(len(TARGETS), dtype=float)
        for j, target in enumerate(TARGETS):
            base_target_loss = loss_col(inner_y[:, j], inner_base[:, j])
            best_w = 0.0
            best_loss = base_target_loss
            for weight in grid:
                w = np.zeros(len(TARGETS), dtype=float)
                w[j] = weight
                p = adjust_pred(inner_base, inner_bundle, w, mode=mode)
                loss = loss_col(inner_y[:, j], p[:, j])
                if loss < best_loss:
                    best_loss = loss
                    best_w = weight
            weights[j] = best_w
            selected_rows.append(
                {
                    "outer_fold": outer_id,
                    "target": target,
                    "selected_weight": best_w,
                    "inner_base_loss": base_target_loss,
                    "inner_selected_loss": best_loss,
                    "inner_delta": best_loss - base_target_loss,
                }
            )
        outer_bundle = boundary_bundle(train.iloc[tr_idx].copy(), train.iloc[val_idx].copy())
        pred[val_idx] = adjust_pred(base_oof[val_idx], outer_bundle, weights, mode=mode)
    base_losses = target_losses(y, base_oof)
    nested_losses = target_losses(y, pred)
    summary = []
    for target in TARGETS:
        summary.append(
            {
                "target": target,
                "base_loss": base_losses[target],
                "nested_loss": nested_losses[target],
                "delta": nested_losses[target] - base_losses[target],
            }
        )
    summary.append(
        {
            "target": "mean",
            "base_loss": mean_loss(y, base_oof),
            "nested_loss": mean_loss(y, pred),
            "delta": mean_loss(y, pred) - mean_loss(y, base_oof),
        }
    )
    return clip(pred), pd.DataFrame(summary), pd.DataFrame(selected_rows)


def actual_submission_boundary_summary(train: pd.DataFrame, sub: pd.DataFrame) -> tuple[BoundaryBundle, pd.DataFrame]:
    bundle = boundary_bundle(train, sub)
    rows = []
    for j, target in enumerate(TARGETS):
        for local_case in sorted(pd.unique(bundle.case[:, j])):
            mask = bundle.case[:, j] == local_case
            rows.append(
                {
                    "target": target,
                    "case": local_case,
                    "n_rows": int(mask.sum()),
                    "n_blocks": int(pd.Series(bundle.block_id[mask]).nunique()) if mask.any() else 0,
                    "anchor_mean_pred": float(bundle.anchor_prob[mask, j].mean()) if mask.any() else np.nan,
                }
            )
    return bundle, pd.DataFrame(rows).sort_values(["target", "case"]).reset_index(drop=True)


def save_submission(
    sample: pd.DataFrame,
    pred: np.ndarray,
    file_name: str,
    oof_pred: np.ndarray,
) -> dict[str, object]:
    out = sample[KEY].copy()
    out[TARGETS] = clip(pred)
    out.to_csv(OUT / file_name, index=False)
    np.save(OUT / file_name.replace("submission_", "final_").replace(".csv", "_oof.npy"), clip(oof_pred))
    return {
        "file": file_name,
        "rows": int(len(out)),
        "duplicate_keys": int(out.duplicated(KEY).sum()),
        "null_predictions": int(out[TARGETS].isna().sum().sum()),
        "min_prob": float(out[TARGETS].min().min()),
        "max_prob": float(out[TARGETS].max().max()),
    }


def build_report(
    base_rows: list[dict[str, object]],
    scan: pd.DataFrame,
    nested: pd.DataFrame,
    sub_summary: pd.DataFrame,
    candidates: pd.DataFrame,
) -> None:
    def table_text(df: pd.DataFrame) -> str:
        if df.empty:
            return "(empty)"
        return df.to_csv(index=False).strip()

    lines = ["# Boundary Consensus Audit\n\n"]
    lines.append("## Decision\n\n")
    best_nested = nested[nested["target"].eq("mean")].sort_values("delta").head(5)
    if not best_nested.empty:
        row = best_nested.iloc[0]
        if float(row["delta"]) < -0.0002:
            lines.append(
                f"Boundary-consensus is weakly positive for `{row['base']}` / `{row['mode']}` "
                f"with nested delta `{float(row['delta']):.6f}`. Treat generated files as low-amplitude probes.\n\n"
            )
        else:
            lines.append(
                "Boundary-consensus is not promoted as a score candidate. Apparent same-boundary gains "
                "do not survive enough nested target-wise validation to outrank existing public-safe probes.\n\n"
            )
    lines.append("## Base Losses\n\n")
    lines.append("```csv\n")
    lines.append(table_text(pd.DataFrame(base_rows).round(6)))
    lines.append("\n```")
    lines.append("\n\n## Best Apparent Weight Scans\n\n")
    lines.append("```csv\n")
    lines.append(table_text(scan.head(12).round(6)))
    lines.append("\n```")
    lines.append("\n\n## Nested Mean Rows\n\n")
    lines.append("```csv\n")
    lines.append(table_text(nested[nested["target"].eq("mean")].sort_values("delta").round(6)))
    lines.append("\n```")
    lines.append("\n\n## Actual Submission Boundary Exposure\n\n")
    pivot = sub_summary.pivot_table(index="target", columns="case", values="n_rows", aggfunc="sum", fill_value=0)
    lines.append("```csv\n")
    lines.append(table_text(pivot.reset_index()))
    lines.append("\n```")
    if not candidates.empty:
        lines.append("\n\n## Generated Diagnostic Candidates\n\n")
        lines.append("```csv\n")
        lines.append(table_text(candidates.round(6)))
        lines.append("\n```")
    (OUT / "boundary_consensus_report.md").write_text("".join(lines))


def main() -> None:
    train, sample = load_labels()
    y = train[TARGETS].to_numpy(dtype=int)
    folds = d.make_folds(train, "subject_blocks")
    boundary = bundle_for_folds(train, folds)

    base_rows: list[dict[str, object]] = []
    base_oofs: dict[str, np.ndarray] = {}
    for base_name, (_sub_file, oof_file) in BASES.items():
        arr = clip(np.load(OUT / oof_file))
        base_oofs[base_name] = arr
        row = {"base": base_name, "mean": mean_loss(y, arr)}
        row.update(target_losses(y, arr))
        base_rows.append(row)

    main_base = "stage2"
    case_summary = row_case_summary(train, boundary, base_oofs[main_base])
    block_summary = block_case_summary(train, boundary)
    case_summary.to_csv(OUT / "boundary_consensus_case_summary.csv", index=False)
    block_summary.to_csv(OUT / "boundary_consensus_block_summary.csv", index=False)

    scan_frames = [scan_weights(train, name, pred, boundary) for name, pred in base_oofs.items()]
    scan = pd.concat(scan_frames, ignore_index=True).sort_values(["mean", "base"]).reset_index(drop=True)
    scan.to_csv(OUT / "boundary_consensus_weight_scan.csv", index=False)

    nested_frames = []
    selected_frames = []
    nested_preds: dict[tuple[str, str], np.ndarray] = {}
    grid = [0.0, 0.01, 0.02, 0.035, 0.05, 0.075, 0.10, 0.15]
    for base_name, pred in base_oofs.items():
        for mode in ["same", "same_or_single", "ones_only", "zeros_only"]:
            nested_pred, summary, selected = nested_select_weights(train, pred, mode, grid)
            summary.insert(0, "base", base_name)
            summary.insert(1, "mode", mode)
            selected.insert(0, "base", base_name)
            selected.insert(1, "mode", mode)
            nested_frames.append(summary)
            selected_frames.append(selected)
            nested_preds[(base_name, mode)] = nested_pred
    nested = pd.concat(nested_frames, ignore_index=True)
    selected = pd.concat(selected_frames, ignore_index=True)
    nested.to_csv(OUT / "boundary_consensus_nested_summary.csv", index=False)
    selected.to_csv(OUT / "boundary_consensus_nested_selected_weights.csv", index=False)

    sample_boundary, sub_summary = actual_submission_boundary_summary(train, sample)
    sub_summary.to_csv(OUT / "boundary_consensus_submission_boundary_exposure.csv", index=False)

    candidate_rows: list[dict[str, object]] = []
    integrity_rows: list[dict[str, object]] = []
    selected_mean = nested[nested["target"].eq("mean")].sort_values("delta").reset_index(drop=True)
    for _, row in selected_mean.head(6).iterrows():
        base_name = str(row["base"])
        mode = str(row["mode"])
        if float(row["delta"]) > 0.00005:
            continue
        base_sub_file, _ = BASES[base_name]
        base_sub = load_sub(base_sub_file)
        mean_weights = (
            selected[(selected["base"].eq(base_name)) & (selected["mode"].eq(mode))]
            .groupby("target")["selected_weight"]
            .mean()
            .reindex(TARGETS)
            .fillna(0.0)
            .to_numpy(dtype=float)
        )
        if float(mean_weights.sum()) <= 0.0:
            continue
        sub_pred = adjust_pred(base_sub[TARGETS].to_numpy(dtype=float), sample_boundary, mean_weights, mode=mode)
        oof_pred = nested_preds[(base_name, mode)]
        tag = stable_tag(f"{base_name}_{mode}_{'|'.join(f'{w:.5f}' for w in mean_weights)}")
        file_name = f"submission_boundary_{base_name}_{mode}_{tag}.csv"
        integrity_rows.append(save_submission(sample, sub_pred, file_name, oof_pred))
        metrics = {
            "file": file_name,
            "base": base_name,
            "mode": mode,
            "oof": mean_loss(y, oof_pred),
            "delta_vs_base": mean_loss(y, oof_pred) - mean_loss(y, base_oofs[base_name]),
            "weights": "|".join(f"{target}:{mean_weights[j]:.4f}" for j, target in enumerate(TARGETS)),
        }
        metrics.update(one_axis_metrics(sub_pred))
        metrics.update(two_axis_metrics(sub_pred))
        candidate_rows.append(metrics)

    candidates = pd.DataFrame(candidate_rows).sort_values(["delta_vs_base", "two_axis_public_delta_vs_stage2"]) if candidate_rows else pd.DataFrame()
    integrity = pd.DataFrame(integrity_rows)
    candidates.to_csv(OUT / "boundary_consensus_candidates.csv", index=False)
    integrity.to_csv(OUT / "boundary_consensus_integrity.csv", index=False)

    build_report(base_rows, scan, nested, sub_summary, candidates)
    print("[boundary case summary]")
    print(case_summary.sort_values("anchor_delta").head(20).round(6).to_string(index=False))
    print("\n[weight scan]")
    print(scan.head(15).round(6).to_string(index=False))
    print("\n[nested mean]")
    print(nested[nested["target"].eq("mean")].sort_values("delta").round(6).to_string(index=False))
    if not candidates.empty:
        print("\n[candidates]")
        print(candidates.round(6).to_string(index=False))


if __name__ == "__main__":
    main()
