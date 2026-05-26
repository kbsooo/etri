from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import current_0p586_gentle_logit_calibration as glc
import current_0p588_subject_relative_q_postprocess as srq
import current_0p591_block_label_postprocess as blp
import deep_dive_analysis as d
import geometry_mask_cv_experiments as geom


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY


@dataclass(frozen=True)
class SelectedConfig:
    target: str
    config: str
    train_delta: float


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([srq.loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def transform(rows: pd.DataFrame, p: np.ndarray, kind: str, config_name: str) -> np.ndarray:
    if kind == "subject":
        return srq.subject_relative(rows, p, srq.parse_config(config_name))
    if kind == "logit":
        return glc.calibrate(p, glc.parse_config(config_name))
    raise ValueError(kind)


def config_names(kind: str) -> list[str]:
    if kind == "subject":
        return [cfg.name for cfg in srq.configs()]
    if kind == "logit":
        return [cfg.name for cfg in glc.configs()]
    raise ValueError(kind)


def select_configs(
    rows: pd.DataFrame,
    y: np.ndarray,
    current: np.ndarray,
    kind: str,
    min_delta: float,
    max_targets: int,
) -> list[SelectedConfig]:
    selected: list[SelectedConfig] = []
    for target in TARGETS:
        j = TARGETS.index(target)
        base_loss = srq.loss_col(y[:, j], current[:, j])
        best_name = ""
        best_delta = 0.0
        for name in config_names(kind):
            pred = transform(rows, current[:, j], kind, name)
            delta = srq.loss_col(y[:, j], pred) - base_loss
            if delta < best_delta:
                best_delta = float(delta)
                best_name = name
        if best_name and best_delta <= min_delta:
            selected.append(SelectedConfig(target, best_name, best_delta))
    selected.sort(key=lambda cfg: cfg.train_delta)
    return selected[:max_targets]


def apply_selected(rows: pd.DataFrame, current: np.ndarray, kind: str, selected: list[SelectedConfig]) -> np.ndarray:
    out = current.copy()
    for cfg in selected:
        j = TARGETS.index(cfg.target)
        out[:, j] = transform(rows, out[:, j], kind, cfg.config)
    return out


def parse_kinds(spec: str, max_steps: int) -> list[str]:
    parts = [part.strip() for part in spec.split(",") if part.strip()]
    if not parts:
        raise ValueError("empty step spec")
    kinds: list[str] = []
    for i in range(max_steps):
        kinds.append(parts[i % len(parts)])
    for kind in kinds:
        if kind not in {"subject", "logit"}:
            raise ValueError(kind)
    return kinds


def run(
    base_oof: Path,
    prefix: str,
    max_steps: int,
    min_delta: float,
    max_targets: int,
    n_repeats: int,
    target_frac: float,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = blp.train_frame()
    sub = blp.sub_frame()
    base = np.load(base_oof)
    y_all = train[TARGETS].to_numpy(dtype=int)
    folds = geom.geometry_folds(
        train[KEY + ["sleep_date"] + TARGETS],
        sub[KEY + ["sleep_date"]],
        n_repeats=n_repeats,
        target_frac=target_frac,
    )
    kinds = parse_kinds("subject,logit", max_steps)
    step_rows: list[dict[str, object]] = []
    target_rows: list[dict[str, object]] = []

    for tr_idx, val_idx, fold_name in folds:
        fit_rows = train.iloc[tr_idx].reset_index(drop=True)
        val_rows = train.iloc[val_idx].reset_index(drop=True)
        fit_y = y_all[tr_idx]
        val_y = y_all[val_idx]
        fit_current = base[tr_idx].copy()
        val_current = base[val_idx].copy()
        fit_base_loss = mean_loss(fit_y, fit_current)
        val_base_loss = mean_loss(val_y, val_current)
        print(
            f"[nested residual] {fold_name} train={len(tr_idx)} val={len(val_idx)} "
            f"base_fit={fit_base_loss:.6f} base_val={val_base_loss:.6f}",
            flush=True,
        )
        for step_idx, kind in enumerate(kinds, start=1):
            selected = select_configs(fit_rows, fit_y, fit_current, kind, min_delta, max_targets)
            if not selected:
                step_rows.append(
                    {
                        "fold": fold_name,
                        "step": step_idx,
                        "kind": kind,
                        "n_selected": 0,
                        "selected": "",
                        "fit_loss_before": mean_loss(fit_y, fit_current),
                        "fit_loss_after": mean_loss(fit_y, fit_current),
                        "fit_delta": 0.0,
                        "val_loss_before": mean_loss(val_y, val_current),
                        "val_loss_after": mean_loss(val_y, val_current),
                        "val_delta": 0.0,
                        "cumulative_fit_delta": mean_loss(fit_y, fit_current) - fit_base_loss,
                        "cumulative_val_delta": mean_loss(val_y, val_current) - val_base_loss,
                    }
                )
                continue
            fit_before = mean_loss(fit_y, fit_current)
            val_before = mean_loss(val_y, val_current)
            fit_next = apply_selected(fit_rows, fit_current, kind, selected)
            val_next = apply_selected(val_rows, val_current, kind, selected)
            fit_after = mean_loss(fit_y, fit_next)
            val_after = mean_loss(val_y, val_next)
            selected_s = ";".join(f"{cfg.target}:{cfg.config}:{cfg.train_delta:.6g}" for cfg in selected)
            step_rows.append(
                {
                    "fold": fold_name,
                    "step": step_idx,
                    "kind": kind,
                    "n_selected": len(selected),
                    "selected": selected_s,
                    "fit_loss_before": fit_before,
                    "fit_loss_after": fit_after,
                    "fit_delta": fit_after - fit_before,
                    "val_loss_before": val_before,
                    "val_loss_after": val_after,
                    "val_delta": val_after - val_before,
                    "cumulative_fit_delta": fit_after - fit_base_loss,
                    "cumulative_val_delta": val_after - val_base_loss,
                }
            )
            for cfg in selected:
                j = TARGETS.index(cfg.target)
                fit_col = transform(fit_rows, fit_current[:, j], kind, cfg.config)
                val_col = transform(val_rows, val_current[:, j], kind, cfg.config)
                target_rows.append(
                    {
                        "fold": fold_name,
                        "step": step_idx,
                        "kind": kind,
                        "target": cfg.target,
                        "config": cfg.config,
                        "fit_delta": srq.loss_col(fit_y[:, j], fit_col) - srq.loss_col(fit_y[:, j], fit_current[:, j]),
                        "val_delta": srq.loss_col(val_y[:, j], val_col) - srq.loss_col(val_y[:, j], val_current[:, j]),
                    }
                )
            fit_current = fit_next
            val_current = val_next

    step_df = pd.DataFrame(step_rows)
    target_df = pd.DataFrame(target_rows)
    summary = (
        step_df.groupby(["step", "kind"], as_index=False)
        .agg(
            n_folds=("fold", "nunique"),
            mean_selected=("n_selected", "mean"),
            mean_fit_delta=("fit_delta", "mean"),
            mean_val_delta=("val_delta", "mean"),
            median_val_delta=("val_delta", "median"),
            val_win_rate=("val_delta", lambda x: float((x < 0).mean())),
            mean_cumulative_val_delta=("cumulative_val_delta", "mean"),
            final_val_loss=("val_loss_after", "mean"),
        )
    )
    step_df.to_csv(OUT / f"{prefix}_fold_steps.csv", index=False)
    target_df.to_csv(OUT / f"{prefix}_target_steps.csv", index=False)
    summary.to_csv(OUT / f"{prefix}_summary.csv", index=False)
    return step_df, target_df, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--min-delta", type=float, default=-0.00015)
    parser.add_argument("--max-targets", type=int, default=3)
    parser.add_argument("--n-repeats", type=int, default=10)
    parser.add_argument("--target-frac", type=float, default=0.22)
    args = parser.parse_args()
    _, target_df, summary = run(
        Path(args.base_oof),
        args.prefix,
        args.max_steps,
        args.min_delta,
        args.max_targets,
        args.n_repeats,
        args.target_frac,
    )
    print(summary.round(6).to_string(index=False))
    if not target_df.empty:
        target_summary = (
            target_df.groupby(["kind", "target", "config"], as_index=False)
            .agg(
                n=("fold", "count"),
                mean_fit_delta=("fit_delta", "mean"),
                mean_val_delta=("val_delta", "mean"),
                val_win_rate=("val_delta", lambda x: float((x < 0).mean())),
            )
            .sort_values(["mean_val_delta", "n"])
        )
        target_summary.to_csv(OUT / f"{args.prefix}_target_summary.csv", index=False)
        print(target_summary.head(20).round(6).to_string(index=False))


if __name__ == "__main__":
    main()
