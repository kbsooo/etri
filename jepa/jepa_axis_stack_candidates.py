from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]

STAGE2_PUBLIC = 0.5779449757
PUBLIC = {
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv": 0.5775263072,
    "submission_jepa_latent_residual_probe.csv": 0.5812273278,
    "submission_jepa_latent_q2_w0p45.csv": 0.5798012862,
}

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402


def read_submission(name: str, base_sub: pd.DataFrame) -> np.ndarray:
    df = pd.read_csv(OUT / name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert df[KEY].equals(base_sub[KEY])
    return adv.clip(df[TARGETS].to_numpy(dtype=float))


def safe_label(x: float) -> str:
    return str(x).replace("-", "m").replace(".", "p")


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return adv.mean_loss(y, adv.clip(pred))


def apply_feature_ops(
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    ops: pd.DataFrame,
    base: np.ndarray,
    base_sub: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:
    pred = adv.clip(base.copy())
    sub_pred = adv.clip(base_sub[TARGETS].to_numpy(dtype=float).copy())
    for op in ops.itertuples(index=False):
        target = str(op.target)
        feature = str(op.feature)
        mode = str(op.mode)
        c_value = float(op.c_value)
        if "scaled_weight" in ops.columns:
            weight = float(op.scaled_weight)
        elif "best_weight" in ops.columns:
            weight = float(op.best_weight)
        elif "weight" in ops.columns:
            weight = float(op.weight)
        else:
            raise ValueError(f"cannot infer weight from columns {ops.columns.tolist()}")
        if weight <= 0:
            continue
        j = TARGETS.index(target)
        corrected = broad.oof_corrected(train_feat, pred, target, feature, mode, c_value)
        pred[:, j] = adv.clip((1.0 - weight) * pred[:, j] + weight * corrected)
        sub_corr = broad.fit_corrected(train_feat, sub_feat, pred, sub_pred, target, feature, mode, c_value)
        sub_pred[:, j] = adv.clip((1.0 - weight) * sub_pred[:, j] + weight * sub_corr)
    return adv.clip(pred), adv.clip(sub_pred)


def candidate_from_ops(
    name: str,
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    base: np.ndarray,
    base_sub: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:
    ops = pd.read_csv(OUT / name.replace("submission_", "").replace(".csv", "_ops.csv"))
    return apply_feature_ops(train_feat, sub_feat, ops, base, base_sub)


def logit_move(pred: np.ndarray, base: np.ndarray) -> np.ndarray:
    return adv.logit(pred) - adv.logit(base)


def axis_stats(move: np.ndarray, base_sub: pd.DataFrame) -> dict[str, float]:
    base_logit = adv.logit(base_sub[TARGETS].to_numpy(dtype=float))
    bad_parts = []
    bad_weights = []
    for name in ["submission_jepa_latent_residual_probe.csv", "submission_jepa_latent_q2_w0p45.csv"]:
        arr = read_submission(name, base_sub)
        bad_parts.append(adv.logit(arr) - base_logit)
        bad_weights.append(max(PUBLIC[name] - STAGE2_PUBLIC, 1e-9))
    bad_axis = np.average(np.stack(bad_parts), axis=0, weights=np.asarray(bad_weights))
    raw_good = read_submission("submission_raw_timeline_jepa_rescue_strict_scale0p5.csv", base_sub)
    good_axis = adv.logit(raw_good) - base_logit

    out: dict[str, float] = {}
    for prefix, axis in [("jepa_bad", bad_axis), ("raw_good", good_axis)]:
        flat_m = move.reshape(-1)
        flat_a = axis.reshape(-1)
        out[f"{prefix}_ratio"] = float(np.dot(flat_m, flat_a) / max(float(np.dot(flat_a, flat_a)), 1e-12))
        out[f"{prefix}_cos"] = float(np.dot(flat_m, flat_a) / max(float(np.linalg.norm(flat_m) * np.linalg.norm(flat_a)), 1e-12))
    return out


def emit_submission(name: str, base_sub: pd.DataFrame, pred: np.ndarray) -> None:
    out = base_sub.copy()
    out[TARGETS] = adv.clip(pred)
    out.to_csv(OUT / name, index=False)


def blended_predictions(
    base: np.ndarray,
    base_sub: pd.DataFrame,
    oof_moves: list[tuple[np.ndarray, float]],
    sub_moves: list[tuple[np.ndarray, float]],
    target_weights: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    base_logit = adv.logit(base)
    sub_logit = adv.logit(base_sub[TARGETS].to_numpy(dtype=float))
    oof_delta = np.zeros_like(base_logit)
    sub_delta = np.zeros_like(sub_logit)
    for move, weight in oof_moves:
        oof_delta += float(weight) * move
    for move, weight in sub_moves:
        sub_delta += float(weight) * move
    if target_weights is not None:
        oof_delta *= target_weights.reshape(1, -1)
        sub_delta *= target_weights.reshape(1, -1)
    return adv.clip(1.0 / (1.0 + np.exp(-(base_logit + oof_delta)))), adv.clip(1.0 / (1.0 + np.exp(-(sub_logit + sub_delta))))


def build_source_predictions(base: np.ndarray, base_sub: pd.DataFrame) -> dict[str, dict[str, np.ndarray | str]]:
    raw_train = pd.read_parquet(OUT / "raw_timeline_jepa_rescue_train_features.parquet")
    raw_sub = pd.read_parquet(OUT / "raw_timeline_jepa_rescue_submission_features.parquet")
    bc_train = pd.read_parquet(OUT / "block_canvas_jepa_train_features.parquet")
    bc_sub = pd.read_parquet(OUT / "block_canvas_jepa_submission_features.parquet")

    specs = {
        "raw05": ("submission_raw_timeline_jepa_rescue_strict_scale0p5.csv", raw_train, raw_sub),
        "raw075": ("submission_raw_timeline_jepa_rescue_strict_scale0p75.csv", raw_train, raw_sub),
        "raw10": ("submission_raw_timeline_jepa_rescue_strict_scale1p0.csv", raw_train, raw_sub),
        "bc_noq2_035": ("submission_block_canvas_jepa_strict_noq2_scale0p35.csv", bc_train, bc_sub),
        "bc_noq2_05": ("submission_block_canvas_jepa_strict_noq2_scale0p5.csv", bc_train, bc_sub),
        "bc_noq2_075": ("submission_block_canvas_jepa_strict_noq2_scale0p75.csv", bc_train, bc_sub),
        "bc_noq2_10": ("submission_block_canvas_jepa_strict_noq2_scale1p0.csv", bc_train, bc_sub),
        "bc_strict_035": ("submission_block_canvas_jepa_strict_scale0p35.csv", bc_train, bc_sub),
        "bc_strict_05": ("submission_block_canvas_jepa_strict_scale0p5.csv", bc_train, bc_sub),
        "bc_strict_075": ("submission_block_canvas_jepa_strict_scale0p75.csv", bc_train, bc_sub),
    }
    out: dict[str, dict[str, np.ndarray | str]] = {}
    for label, (file_name, train_feat, sub_feat) in specs.items():
        oof, sub = candidate_from_ops(file_name, train_feat, sub_feat, base, base_sub)
        disk_sub = read_submission(file_name, base_sub)
        # Use the exact already-written submission movement for public-axis geometry.
        out[label] = {
            "file": file_name,
            "oof": oof,
            "sub": disk_sub,
            "oof_move": logit_move(oof, base),
            "sub_move": logit_move(disk_sub, base_sub[TARGETS].to_numpy(dtype=float)),
        }
    return out


def make_global_stack_grid(
    sources: dict[str, dict[str, np.ndarray | str]],
    train_y: np.ndarray,
    base: np.ndarray,
    base_sub: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    raw_labels = ["raw05", "raw075", "raw10"]
    bc_labels = ["bc_noq2_035", "bc_noq2_05", "bc_noq2_075", "bc_noq2_10", "bc_strict_035", "bc_strict_05", "bc_strict_075"]
    raw_weights = [0.0, 0.5, 0.75, 1.0, 1.25]
    bc_weights = [0.0, 0.25, 0.5, 0.75, 1.0]
    base_loss = mean_loss(train_y, base)
    for raw_label in raw_labels:
        for bc_label in bc_labels:
            for wr in raw_weights:
                for wb in bc_weights:
                    if wr == 0.0 and wb == 0.0:
                        continue
                    oof, sub = blended_predictions(
                        base,
                        base_sub,
                        [(sources[raw_label]["oof_move"], wr), (sources[bc_label]["oof_move"], wb)],  # type: ignore[list-item]
                        [(sources[raw_label]["sub_move"], wr), (sources[bc_label]["sub_move"], wb)],  # type: ignore[list-item]
                    )
                    move = logit_move(sub, base_sub[TARGETS].to_numpy(dtype=float))
                    stats = axis_stats(move, base_sub)
                    rows.append(
                        {
                            "kind": "global",
                            "raw": raw_label,
                            "bc": bc_label,
                            "raw_weight": wr,
                            "bc_weight": wb,
                            "oof_loss": mean_loss(train_y, oof),
                            "oof_delta_vs_stage2": mean_loss(train_y, oof) - base_loss,
                            **stats,
                        }
                    )
    df = pd.DataFrame(rows)
    df["public_safety_rank"] = (
        df["oof_delta_vs_stage2"]
        + 0.006 * np.maximum(df["jepa_bad_ratio"], 0.0)
        - 0.0008 * np.minimum(df["raw_good_ratio"], 0.8)
    )
    return df.sort_values(["public_safety_rank", "oof_delta_vs_stage2"]).reset_index(drop=True)


def targetwise_grid(
    raw_label: str,
    bc_label: str,
    sources: dict[str, dict[str, np.ndarray | str]],
    train_y: np.ndarray,
    base: np.ndarray,
    base_sub: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    base_logit = adv.logit(base)
    sub_logit = adv.logit(base_sub[TARGETS].to_numpy(dtype=float))
    oof = base.copy()
    sub = base_sub[TARGETS].to_numpy(dtype=float).copy()
    choices = []
    raw_grid = [0.0, 0.35, 0.5, 0.75, 1.0]
    bc_grid = [0.0, 0.25, 0.35, 0.5, 0.75]
    raw_oof = sources[raw_label]["oof_move"]  # type: ignore[assignment]
    raw_sub = sources[raw_label]["sub_move"]  # type: ignore[assignment]
    bc_oof = sources[bc_label]["oof_move"]  # type: ignore[assignment]
    bc_sub = sources[bc_label]["sub_move"]  # type: ignore[assignment]
    for j, target in enumerate(TARGETS):
        best = None
        for wr in raw_grid:
            for wb in bc_grid:
                if target == "Q2":
                    wb = 0.0
                p = adv.clip(1.0 / (1.0 + np.exp(-(base_logit[:, j] + wr * raw_oof[:, j] + wb * bc_oof[:, j]))))
                loss = broad.loss_col(train_y[:, j], p)
                penalty = 0.0002 * (wr + wb)
                key = loss + penalty
                if best is None or key < best[0]:
                    best = (key, loss, wr, wb, p)
        assert best is not None
        _key, loss, wr, wb, p = best
        oof[:, j] = p
        sub[:, j] = adv.clip(1.0 / (1.0 + np.exp(-(sub_logit[:, j] + wr * raw_sub[:, j] + wb * bc_sub[:, j]))))
        choices.append({"target": target, "raw_weight": wr, "bc_weight": wb, "target_loss": loss})
    return adv.clip(oof), adv.clip(sub), pd.DataFrame(choices)


def emit_top_global(
    grid: pd.DataFrame,
    sources: dict[str, dict[str, np.ndarray | str]],
    train_y: np.ndarray,
    base: np.ndarray,
    base_sub: pd.DataFrame,
    limit: int = 12,
) -> pd.DataFrame:
    emitted = []
    seen = set()
    nonzero_safe = grid[
        (grid["raw_weight"] > 0)
        & (grid["bc_weight"] > 0)
        & (grid["jepa_bad_ratio"] <= 0.03)
        & (grid["raw_good_ratio"].between(0.10, 0.80))
    ]
    nonzero_aggressive = grid[
        (grid["raw_weight"] > 0)
        & (grid["bc_weight"] > 0)
        & (grid["jepa_bad_ratio"] <= 0.0)
        & (grid["raw_good_ratio"].between(0.50, 1.25))
    ]
    pure_block_safe = grid[
        (grid["raw_weight"] == 0)
        & (grid["bc_weight"] > 0)
        & (grid["jepa_bad_ratio"] <= 0.02)
        & (grid["raw_good_ratio"].between(0.05, 0.25))
    ]
    candidates = pd.concat(
        [
            nonzero_safe.head(limit),
            nonzero_aggressive.head(limit),
            pure_block_safe.head(max(3, limit // 3)),
            grid.head(limit),
        ],
        ignore_index=True,
    )
    base_loss = mean_loss(train_y, base)
    for row in candidates.itertuples(index=False):
        key = (row.raw, row.bc, float(row.raw_weight), float(row.bc_weight))
        if float(row.raw_weight) == 0.0:
            key = ("pure", row.bc, 0.0, float(row.bc_weight))
        if key in seen:
            continue
        seen.add(key)
        name = f"submission_jepa_axis_stack_{row.raw}_{row.bc}_rw{safe_label(float(row.raw_weight))}_bw{safe_label(float(row.bc_weight))}.csv"
        oof, sub = blended_predictions(
            base,
            base_sub,
            [(sources[row.raw]["oof_move"], float(row.raw_weight)), (sources[row.bc]["oof_move"], float(row.bc_weight))],  # type: ignore[list-item]
            [(sources[row.raw]["sub_move"], float(row.raw_weight)), (sources[row.bc]["sub_move"], float(row.bc_weight))],  # type: ignore[list-item]
        )
        emit_submission(name, base_sub, sub)
        emitted.append(
            {
                "candidate": name,
                "kind": "global",
                "raw": row.raw,
                "bc": row.bc,
                "raw_weight": float(row.raw_weight),
                "bc_weight": float(row.bc_weight),
                "oof_loss": mean_loss(train_y, oof),
                "oof_delta_vs_stage2": mean_loss(train_y, oof) - base_loss,
                **axis_stats(logit_move(sub, base_sub[TARGETS].to_numpy(dtype=float)), base_sub),
            }
        )
        if len(emitted) >= limit:
            break
    return pd.DataFrame(emitted)


def main() -> None:
    train, _sub, base, base_sub = adv.read_data()
    train_y = train[TARGETS].to_numpy(dtype=int)
    base_loss = mean_loss(train_y, base)
    sources = build_source_predictions(base, base_sub)

    source_rows = []
    for label, item in sources.items():
        oof = item["oof"]  # type: ignore[assignment]
        sub = item["sub"]  # type: ignore[assignment]
        source_rows.append(
            {
                "label": label,
                "file": item["file"],
                "oof_loss": mean_loss(train_y, oof),
                "oof_delta_vs_stage2": mean_loss(train_y, oof) - base_loss,
                **axis_stats(logit_move(sub, base_sub[TARGETS].to_numpy(dtype=float)), base_sub),
            }
        )
    source_summary = pd.DataFrame(source_rows).sort_values("oof_delta_vs_stage2")
    source_summary.to_csv(OUT / "jepa_axis_stack_source_summary.csv", index=False)

    grid = make_global_stack_grid(sources, train_y, base, base_sub)
    grid.to_csv(OUT / "jepa_axis_stack_global_grid.csv", index=False)
    emitted = emit_top_global(grid, sources, train_y, base, base_sub)

    target_emitted = []
    for raw_label, bc_label in [("raw05", "bc_noq2_05"), ("raw05", "bc_noq2_075"), ("raw075", "bc_noq2_05")]:
        oof, sub, choices = targetwise_grid(raw_label, bc_label, sources, train_y, base, base_sub)
        for scale in [0.5, 0.75, 1.0]:
            tw = choices.copy()
            tw["raw_weight"] *= scale
            tw["bc_weight"] *= scale
            target_weights_raw = np.array(tw["raw_weight"].to_numpy(dtype=float))
            target_weights_bc = np.array(tw["bc_weight"].to_numpy(dtype=float))
            oof_s, sub_s = blended_predictions(
                base,
                base_sub,
                [(sources[raw_label]["oof_move"], 1.0), (sources[bc_label]["oof_move"], 1.0)],  # type: ignore[list-item]
                [(sources[raw_label]["sub_move"], 1.0), (sources[bc_label]["sub_move"], 1.0)],  # type: ignore[list-item]
                target_weights=np.zeros(len(TARGETS)),
            )
            base_logit = adv.logit(base)
            sub_logit = adv.logit(base_sub[TARGETS].to_numpy(dtype=float))
            raw_oof = sources[raw_label]["oof_move"]  # type: ignore[assignment]
            raw_sub = sources[raw_label]["sub_move"]  # type: ignore[assignment]
            bc_oof = sources[bc_label]["oof_move"]  # type: ignore[assignment]
            bc_sub = sources[bc_label]["sub_move"]  # type: ignore[assignment]
            oof_s = adv.clip(1.0 / (1.0 + np.exp(-(base_logit + raw_oof * target_weights_raw.reshape(1, -1) + bc_oof * target_weights_bc.reshape(1, -1)))))
            sub_s = adv.clip(1.0 / (1.0 + np.exp(-(sub_logit + raw_sub * target_weights_raw.reshape(1, -1) + bc_sub * target_weights_bc.reshape(1, -1)))))
            name = f"submission_jepa_axis_stack_targetwise_{raw_label}_{bc_label}_scale{safe_label(scale)}.csv"
            emit_submission(name, base_sub, sub_s)
            choices_path = OUT / name.replace("submission_", "").replace(".csv", "_weights.csv")
            tw.to_csv(choices_path, index=False)
            target_emitted.append(
                {
                    "candidate": name,
                    "kind": "targetwise",
                    "raw": raw_label,
                    "bc": bc_label,
                    "scale": scale,
                    "oof_loss": mean_loss(train_y, oof_s),
                    "oof_delta_vs_stage2": mean_loss(train_y, oof_s) - base_loss,
                    **axis_stats(logit_move(sub_s, base_sub[TARGETS].to_numpy(dtype=float)), base_sub),
                }
            )

    summary = pd.concat([emitted, pd.DataFrame(target_emitted)], ignore_index=True).sort_values(
        ["jepa_bad_ratio", "oof_delta_vs_stage2"]
    )
    summary.to_csv(OUT / "jepa_axis_stack_candidate_summary.csv", index=False)
    report = [
        "# JEPA Axis Stack Candidates",
        "",
        "Combines raw-rescue and Block-Canvas JEPA as logit-space residual directions. Public feedback is used only as a geometric guardrail: keep the failed latent/Q2 axis small while preserving the raw-rescue scale0.5 direction that improved public LB.",
        "",
        "## Source Summary",
        "",
        source_summary.to_csv(index=False),
        "",
        "## Emitted Candidates",
        "",
        summary.to_csv(index=False),
        "",
        "## Best Global Grid Rows",
        "",
        grid.head(40).to_csv(index=False),
    ]
    (OUT / "jepa_axis_stack_report.md").write_text("\n".join(report), encoding="utf-8")
    print(summary.head(25).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
