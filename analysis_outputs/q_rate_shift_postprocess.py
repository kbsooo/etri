from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import deep_dive_analysis as d  # noqa: E402


OUT = Path(__file__).resolve().parent
DATA = OUT.parents[0] / "data"
TARGETS = d.TARGETS
Q_TARGETS = ["Q1", "Q2", "Q3"]
KEY = d.KEY


@dataclass(frozen=True)
class RateShiftConfig:
    total_rate: float
    shrink: float
    strength: float

    @property
    def name(self) -> str:
        return f"r{self.total_rate:g}_s{self.shrink:g}_g{self.strength:g}"


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def target_loss(y: np.ndarray, p: np.ndarray) -> float:
    return float(log_loss(y.astype(int), clip(p), labels=[0, 1]))


def solve_shift(p: np.ndarray, target_mean: float) -> np.ndarray:
    target_mean = float(np.clip(target_mean, 0.03, 0.97))
    z = logit(p)
    lo, hi = -12.0, 12.0
    for _ in range(60):
        mid = (lo + hi) / 2.0
        cur = float(sigmoid(z + mid).mean())
        if cur < target_mean:
            lo = mid
        else:
            hi = mid
    return clip(sigmoid(z + (lo + hi) / 2.0))


def hidden_rate_target(ref: pd.DataFrame, rows: pd.DataFrame, target: str, cfg: RateShiftConfig) -> dict[str, float]:
    global_rate = float(ref[target].mean())
    out = {}
    for sid, g in rows.groupby("subject_id", sort=False):
        known = ref[ref["subject_id"].eq(sid)]
        n_known = len(known)
        n_hidden = len(g)
        known_pos = float(known[target].sum())
        raw = (cfg.total_rate * (n_known + n_hidden) - known_pos + cfg.shrink * global_rate) / (
            n_hidden + cfg.shrink
        )
        out[str(sid)] = float(np.clip(raw, 0.03, 0.97))
    return out


def apply_fold_shift(
    ref: pd.DataFrame,
    rows: pd.DataFrame,
    p: np.ndarray,
    target: str,
    cfg: RateShiftConfig,
) -> np.ndarray:
    out = p.copy()
    targets = hidden_rate_target(ref, rows, target, cfg)
    tmp = rows.reset_index(drop=True)
    for sid, g in tmp.groupby("subject_id", sort=False):
        idx = g.index.to_numpy(dtype=int)
        shifted = solve_shift(p[idx], targets[str(sid)])
        out[idx] = clip((1.0 - cfg.strength) * p[idx] + cfg.strength * shifted)
    return clip(out)


def configs(target: str) -> list[RateShiftConfig]:
    if target == "Q1":
        rates = [0.40, 0.45, 0.50, 0.55, 0.60]
    elif target == "Q2":
        rates = [0.40, 0.45, 0.50, 0.55]
    else:
        rates = [0.45, 0.50, 0.55, 0.60, 0.65]
    return [
        RateShiftConfig(r, shrink, strength)
        for r in rates
        for shrink in [0.0, 1.0, 2.0, 4.0, 8.0, 16.0]
        for strength in [0.15, 0.25, 0.35, 0.50, 0.75, 1.0]
    ]


def subject_block_eval(train: pd.DataFrame, base_pred: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    selected_rows = []
    folds = d.make_folds(train, "subject_blocks")
    for target in Q_TARGETS:
        j = TARGETS.index(target)
        y = train[target].to_numpy(dtype=int)
        rows.append({"target": target, "model": "current_0p598_oof", "config": "none", "loss": target_loss(y, base_pred[:, j])})
        for cfg in configs(target):
            pred = base_pred[:, j].copy()
            for tr_idx, val_idx in folds:
                ref = train.iloc[tr_idx].copy().reset_index(drop=True)
                val = train.iloc[val_idx].copy().reset_index(drop=True)
                pred[val_idx] = apply_fold_shift(ref, val, base_pred[val_idx, j], target, cfg)
            rows.append({"target": target, "model": "rate_logit_shift", "config": cfg.name, "loss": target_loss(y, pred)})
        target_rows = [r for r in rows if r["target"] == target]
        best = min(target_rows, key=lambda r: r["loss"])
        selected_rows.append(best)
    return pd.DataFrame(rows).sort_values(["target", "loss"]), pd.DataFrame(selected_rows)


def half_subject_holdout(train: pd.DataFrame, base_pred: np.ndarray, selected: pd.DataFrame) -> pd.DataFrame:
    # A small guardrail: select rates on subjects id01-id05 and test the same
    # fixed configs on id06-id10. This catches pure subject-rate overfitting.
    rows = []
    first_subjects = set(sorted(train["subject_id"].unique())[:5])
    select_mask = train["subject_id"].isin(first_subjects).to_numpy()
    hold_mask = ~select_mask
    for target in Q_TARGETS:
        j = TARGETS.index(target)
        y = train[target].to_numpy(dtype=int)
        base_loss_hold = target_loss(y[hold_mask], base_pred[hold_mask, j])
        best = None
        for cfg in configs(target):
            pred = base_pred[:, j].copy()
            for tr_idx, val_idx in d.make_folds(train, "subject_blocks"):
                ref = train.iloc[tr_idx].copy().reset_index(drop=True)
                val = train.iloc[val_idx].copy().reset_index(drop=True)
                pred[val_idx] = apply_fold_shift(ref, val, base_pred[val_idx, j], target, cfg)
            sel_loss = target_loss(y[select_mask], pred[select_mask])
            if best is None or sel_loss < best[0]:
                best = (sel_loss, cfg, pred)
        assert best is not None
        rows.append(
            {
                "target": target,
                "selected_config": best[1].name,
                "select_loss": best[0],
                "holdout_base_loss": base_loss_hold,
                "holdout_shift_loss": target_loss(y[hold_mask], best[2][hold_mask]),
            }
        )
    return pd.DataFrame(rows)


def apply_submission_shift(train: pd.DataFrame, sub: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    out = pd.read_csv(OUT / "submission_hybrid_0p598_repro.csv", parse_dates=["sleep_date", "lifelog_date"])
    out = out.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    for row in selected.itertuples(index=False):
        if str(row.model) != "rate_logit_shift":
            continue
        target = str(row.target)
        parts = str(row.config).replace("r", "", 1).split("_")
        total_rate = float(parts[0])
        shrink = float(parts[1].replace("s", ""))
        strength = float(parts[2].replace("g", ""))
        cfg = RateShiftConfig(total_rate, shrink, strength)
        out[target] = apply_fold_shift(train, sub, out[target].to_numpy(dtype=float), target, cfg)
    out[TARGETS] = out[TARGETS].clip(1e-5, 1 - 1e-5)
    out.to_csv(OUT / "submission_hybrid_0p598_q_rate_shift.csv", index=False)
    return out


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    base_pred = np.load(OUT / "final_hybrid_0p598_repro_oof.npy")
    results, selected = subject_block_eval(train, base_pred)
    holdout = half_subject_holdout(train, base_pred, selected)
    results.to_csv(OUT / "q_rate_shift_postprocess_results.csv", index=False)
    selected.to_csv(OUT / "q_rate_shift_postprocess_selected.csv", index=False)
    holdout.to_csv(OUT / "q_rate_shift_postprocess_half_subject_holdout.csv", index=False)
    out = apply_submission_shift(train, sub, selected)

    print("Best per target")
    print(selected.round(6).to_string(index=False))
    print("\nHalf-subject guardrail")
    print(holdout.round(6).to_string(index=False))
    print("wrote", OUT / "submission_hybrid_0p598_q_rate_shift.csv", out.shape)


if __name__ == "__main__":
    main()
