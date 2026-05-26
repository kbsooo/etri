from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import sensor_residual_experiments as sr  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j, target in enumerate(TARGETS)}


@dataclass(frozen=True)
class StateConfig:
    mode: str
    shrink: float = 16.0
    alpha: float = 0.2
    tau: float = 14.0
    kappa: float = 3.0
    alpha_diff: float = 0.08

    @property
    def name(self) -> str:
        return (
            f"{self.mode}"
            f"_s{self.shrink:g}"
            f"_a{self.alpha:g}"
            f"_t{self.tau:g}"
            f"_k{self.kappa:g}"
            f"_ad{self.alpha_diff:g}"
        )


def state_configs() -> list[StateConfig]:
    configs: list[StateConfig] = []
    for shrink in [8.0, 16.0, 24.0]:
        for tau in [7.0, 14.0, 28.0]:
            for alpha in [0.08, 0.15, 0.25, 0.35]:
                configs.append(StateConfig("kernel", shrink=shrink, alpha=alpha, tau=tau, kappa=3.0))
    for shrink in [8.0, 16.0, 24.0]:
        for tau in [7.0, 14.0, 28.0]:
            for alpha in [0.08, 0.15, 0.25, 0.35]:
                configs.append(StateConfig("bridge", shrink=shrink, alpha=alpha, tau=tau, kappa=1.0))
    for shrink in [8.0, 16.0, 24.0]:
        for tau in [14.0, 28.0]:
            for alpha in [0.15, 0.25, 0.35, 0.5]:
                for alpha_diff in [0.03, 0.08, 0.15]:
                    configs.append(
                        StateConfig(
                            "bounded",
                            shrink=shrink,
                            alpha=alpha,
                            alpha_diff=alpha_diff,
                            tau=tau,
                            kappa=1.0,
                        )
                    )
    return configs


def _same_subject_hist(ref: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        str(sid): g.sort_values("lifelog_date")[["lifelog_date"] + TARGETS].reset_index(drop=True)
        for sid, g in ref.groupby("subject_id", sort=False)
    }


def state_temporal(ref: pd.DataFrame, rows: pd.DataFrame, cfg: StateConfig) -> np.ndarray:
    subj = cal.subject_prior(ref, rows, cfg.shrink)
    by_subject = _same_subject_hist(ref)
    pred = np.zeros((len(rows), len(TARGETS)), dtype=float)
    for i, (_, row) in enumerate(rows.reset_index(drop=True).iterrows()):
        sid = str(row["subject_id"])
        day = row["lifelog_date"]
        hist = by_subject.get(sid)
        if hist is None or hist.empty:
            pred[i] = subj[i]
            continue
        days = (hist["lifelog_date"] - day).dt.days.to_numpy(dtype=float)
        keep = days != 0
        hist = hist.loc[keep].reset_index(drop=True)
        days = days[keep]
        if hist.empty:
            pred[i] = subj[i]
            continue
        adist = np.abs(days)
        nearest = float(adist.min())
        for j, target in enumerate(TARGETS):
            y = hist[target].to_numpy(dtype=float)
            local = np.nan
            rel = 0.0

            if cfg.mode == "kernel":
                weights = np.exp(-adist / cfg.tau)
                weight_sum = float(weights.sum())
                if weight_sum > 0:
                    local = float(np.dot(weights, y) / weight_sum)
                    rel = cfg.alpha * weight_sum / (weight_sum + cfg.kappa)

            elif cfg.mode == "bridge":
                prev_idx = np.where(days < 0)[0]
                next_idx = np.where(days > 0)[0]
                if len(prev_idx) and len(next_idx):
                    pidx = prev_idx[np.argmax(days[prev_idx])]
                    nidx = next_idx[np.argmin(days[next_idx])]
                    dp = abs(float(days[pidx]))
                    dn = abs(float(days[nidx]))
                    gap = max(dp + dn, 1.0)
                    local = float((y[pidx] * dn + y[nidx] * dp) / gap)
                    rel = cfg.alpha * np.exp(-min(dp, dn) / cfg.tau) * np.exp(-gap / (4.0 * cfg.tau))
                else:
                    nidx = int(np.argmin(adist))
                    local = float(y[nidx])
                    rel = cfg.alpha * np.exp(-nearest / cfg.tau) * 0.6

            elif cfg.mode == "bounded":
                prev_idx = np.where(days < 0)[0]
                next_idx = np.where(days > 0)[0]
                if len(prev_idx) and len(next_idx):
                    pidx = prev_idx[np.argmax(days[prev_idx])]
                    nidx = next_idx[np.argmin(days[next_idx])]
                    dp = abs(float(days[pidx]))
                    dn = abs(float(days[nidx]))
                    gap = max(dp + dn, 1.0)
                    if y[pidx] == y[nidx]:
                        local = float(y[pidx])
                        rel = cfg.alpha * np.exp(-gap / (4.0 * cfg.tau))
                    else:
                        local = float((y[pidx] * dn + y[nidx] * dp) / gap)
                        rel = cfg.alpha_diff * np.exp(-min(dp, dn) / cfg.tau)
                else:
                    nidx = int(np.argmin(adist))
                    local = float(y[nidx])
                    rel = 0.5 * cfg.alpha_diff * np.exp(-nearest / cfg.tau)

            else:
                raise ValueError(cfg.mode)

            rel = float(np.clip(rel, 0.0, 0.95))
            if np.isnan(local):
                pred[i, j] = subj[i, j]
            else:
                pred[i, j] = (1.0 - rel) * subj[i, j] + rel * local
    return clip(pred)


def state_oof(train: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]], cfg: StateConfig) -> np.ndarray:
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    for tr_idx, val_idx in folds:
        pred[val_idx] = state_temporal(train.iloc[tr_idx].copy(), train.iloc[val_idx].copy(), cfg)
    return clip(pred)


def state_grid(train: pd.DataFrame) -> pd.DataFrame:
    folds = d.make_folds(train, "subject_blocks")
    y = train[TARGETS].to_numpy()
    rows = []
    base = cal.base_oof(train, folds)
    row = {"model": "fixed_temporal_base", "config": "cal.temporal_base", "mean": mean_loss(y, base)}
    row.update(per_target_loss(y, base))
    rows.append(row)
    for cfg in state_configs():
        pred = state_oof(train, folds, cfg)
        row = {"model": "state_grid", "config": cfg.name, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)
    out = pd.DataFrame(rows).sort_values("mean")
    out.to_csv(OUT / "state_space_grid_subject_blocks.csv", index=False)
    return out


def nested_state_selection(train: pd.DataFrame, configs: list[StateConfig]) -> tuple[pd.DataFrame, pd.DataFrame]:
    y = train[TARGETS].to_numpy()
    pred_base = np.zeros_like(y, dtype=float)
    pred_state = np.zeros_like(y, dtype=float)
    selected_rows = []
    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        inner_folds = d.make_folds(outer_train, "subject_blocks")
        inner_y = outer_train[TARGETS].to_numpy()
        best_cfg = None
        best_loss = np.inf
        for cfg in configs:
            inner_pred = state_oof(outer_train, inner_folds, cfg)
            loss = mean_loss(inner_y, inner_pred)
            if loss < best_loss:
                best_loss = loss
                best_cfg = cfg
        if best_cfg is None:
            raise RuntimeError("No state config selected")
        pred_base[val_idx] = cal.temporal_base(outer_train, outer_val)
        pred_state[val_idx] = state_temporal(outer_train, outer_val, best_cfg)
        selected_rows.append({"fold_id": fold_id, "config": best_cfg.name, "inner_mean": best_loss})
        print(f"[state outer {fold_id}] {best_cfg.name} inner={best_loss:.5f}", flush=True)

    rows = []
    for name, pred in [("temporal_base", pred_base), ("nested_state", pred_state)]:
        row = {"model": name, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)
    return pd.DataFrame(rows), pd.DataFrame(selected_rows)


def optimize_small_caps(y: np.ndarray, base: np.ndarray, phone: np.ndarray, mobility: np.ndarray) -> dict[str, tuple[str, float]]:
    allowed = {
        "Q2": ("phone", [0.0, 0.02, 0.05, 0.08, 0.10]),
        "Q3": ("mobility", [0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20]),
        "S4": ("mobility", [0.0, 0.02, 0.05, 0.08, 0.10]),
    }
    out: dict[str, tuple[str, float]] = {target: ("base", 0.0) for target in TARGETS}
    sources = {"phone": phone, "mobility": mobility}
    for target, (source, grid) in allowed.items():
        j = TARGETS.index(target)
        losses = []
        for w in grid:
            pred = (1.0 - w) * base[:, j] + w * sources[source][:, j]
            losses.append(log_loss(y[:, j], clip(pred), labels=[0, 1]))
        best = int(np.argmin(losses))
        out[target] = (source, float(grid[best]))
    return out


def apply_small_caps(base: np.ndarray, phone: np.ndarray, mobility: np.ndarray, choices: dict[str, tuple[str, float]]) -> np.ndarray:
    pred = base.copy()
    sources = {"phone": phone, "mobility": mobility}
    for target, (source, weight) in choices.items():
        if source == "base" or weight == 0:
            continue
        j = TARGETS.index(target)
        pred[:, j] = (1.0 - weight) * base[:, j] + weight * sources[source][:, j]
    return clip(pred)


def conservative_sensor_experiment(train: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    y = train[TARGETS].to_numpy()
    pred_base = np.zeros_like(y, dtype=float)
    pred_nested = np.zeros_like(y, dtype=float)
    selected_rows = []

    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        inner_folds = d.make_folds(outer_train, "subject_blocks")
        inner_y = outer_train[TARGETS].to_numpy()
        inner_base = cal.base_oof(outer_train, inner_folds)
        inner_phone = sr.sensor_oof(outer_train, inner_folds, "phone")
        inner_mobility = sr.sensor_oof(outer_train, inner_folds, "mobility")
        choices = optimize_small_caps(inner_y, inner_base, inner_phone, inner_mobility)

        outer_base = cal.temporal_base(outer_train, outer_val)
        outer_phone = sr.fit_sensor_predict(outer_train, outer_val, "phone")
        outer_mobility = sr.fit_sensor_predict(outer_train, outer_val, "mobility")
        pred_base[val_idx] = outer_base
        pred_nested[val_idx] = apply_small_caps(outer_base, outer_phone, outer_mobility, choices)
        for target, (source, weight) in choices.items():
            selected_rows.append({"fold_id": fold_id, "target": target, "source": source, "weight": weight})
        print(f"[sensor outer {fold_id}] {choices}", flush=True)

    folds = d.make_folds(train, "subject_blocks")
    base = cal.base_oof(train, folds)
    phone = sr.sensor_oof(train, folds, "phone")
    mobility = sr.sensor_oof(train, folds, "mobility")
    fixed_choices = {target: ("base", 0.0) for target in TARGETS}
    fixed_choices.update({"Q2": ("phone", 0.10), "Q3": ("mobility", 0.20), "S4": ("mobility", 0.10)})
    full_choices = optimize_small_caps(y, base, phone, mobility)
    fixed_pred = apply_small_caps(base, phone, mobility, fixed_choices)
    full_opt_pred = apply_small_caps(base, phone, mobility, full_choices)

    rows = []
    for name, pred in [
        ("temporal_base", pred_base),
        ("nested_small_cap_sensor", pred_nested),
        ("fixed_manual_small_cap_oof", fixed_pred),
        ("full_oof_small_cap_optimized", full_opt_pred),
    ]:
        row = {"model": name, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)
    result = pd.DataFrame(rows).sort_values("mean")
    full_choice_rows = [
        {"target": target, "source": source, "weight": weight}
        for target, (source, weight) in full_choices.items()
    ]
    return result, pd.DataFrame(selected_rows), pd.DataFrame(full_choice_rows)


def make_state_submission(train: pd.DataFrame, sub: pd.DataFrame, cfg: StateConfig) -> pd.DataFrame:
    pred = state_temporal(train, sub, cfg)
    out = sub[["subject_id", "sleep_date", "lifelog_date"]].copy()
    for j, target in enumerate(TARGETS):
        out[target] = pred[:, j]
    return out


def make_conservative_submission(train: pd.DataFrame, sub: pd.DataFrame, choices: pd.DataFrame) -> pd.DataFrame:
    base = cal.temporal_base(train, sub)
    phone = sr.fit_sensor_predict(train, sub, "phone")
    mobility = sr.fit_sensor_predict(train, sub, "mobility")
    choice_dict = {
        row["target"]: (row["source"], float(row["weight"]))
        for _, row in choices.iterrows()
    }
    pred = apply_small_caps(base, phone, mobility, choice_dict)
    out = sub[["subject_id", "sleep_date", "lifelog_date"]].copy()
    for j, target in enumerate(TARGETS):
        out[target] = pred[:, j]
    return out


def main() -> None:
    train_base = pd.read_parquet(OUT / "train_deep_features.parquet")
    train_sensor = sr.add_extra_features(train_base)
    sub_base = pd.read_parquet(OUT / "submission_deep_features.parquet")
    sub_sensor = sr.add_extra_features(sub_base)

    grid = state_grid(train_base)
    top_configs = []
    seen = set()
    for name in grid.loc[grid["model"] == "state_grid", "config"].head(20):
        for cfg in state_configs():
            if cfg.name == name and cfg.name not in seen:
                top_configs.append(cfg)
                seen.add(cfg.name)
                break
    state_results, state_selected = nested_state_selection(train_base, top_configs)
    state_results.to_csv(OUT / "state_space_nested_selection_results.csv", index=False)
    state_selected.to_csv(OUT / "state_space_nested_selected_by_fold.csv", index=False)

    best_state_name = grid.iloc[0]["config"]
    best_state_cfg = next((cfg for cfg in state_configs() if cfg.name == best_state_name), None)
    if best_state_cfg is not None:
        make_state_submission(train_base, sub_base, best_state_cfg).to_csv(OUT / "submission_state_space_best.csv", index=False)

    sensor_results, sensor_selected, sensor_full_choices = conservative_sensor_experiment(train_sensor)
    sensor_results.to_csv(OUT / "conservative_sensor_results.csv", index=False)
    sensor_selected.to_csv(OUT / "conservative_sensor_selected_by_fold.csv", index=False)
    sensor_full_choices.to_csv(OUT / "conservative_sensor_full_weights.csv", index=False)
    make_conservative_submission(train_sensor, sub_sensor, sensor_full_choices).to_csv(
        OUT / "submission_conservative_sensor_blend.csv",
        index=False,
    )

    print("\nState grid top 12")
    print(grid.head(12).round(5).to_string(index=False))
    print("\nNested state selection")
    print(state_results.round(5).to_string(index=False))
    print("\nNested state selected configs")
    print(state_selected.to_string(index=False))
    print("\nConservative sensor")
    print(sensor_results.round(5).to_string(index=False))
    print("\nFull-train conservative choices")
    print(sensor_full_choices.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
