from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
GRID = np.array([0.0, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60])


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(y.shape[1])]))


def proxy_files() -> list[Path]:
    names = []
    for pattern in [
        "sleep_interval_proxy_oof*.npy",
        "sleep_interval_proxy_foldsafe_oof_*.npy",
        "sleep_interval_proxy_augmented_oof_*.npy",
        "sleep_fragmentation_proxy_oof_*.npy",
        "sleep_dynamics_proxy_oof_*.npy",
    ]:
        names.extend(OUT.glob(pattern))
    return sorted({p for p in names if p.is_file()})


def repeated_subject_guardrail(
    train: pd.DataFrame,
    y: np.ndarray,
    base: np.ndarray,
    proxy: np.ndarray,
    target_idx: int,
    n_repeats: int,
    seed: int,
) -> dict[str, float]:
    subjects = np.array(sorted(train["subject_id"].astype(str).unique()))
    rng = np.random.default_rng(seed)
    deltas = []
    selected_weights = []
    zero = 0
    for _ in range(n_repeats):
        picked = set(rng.choice(subjects, size=max(1, len(subjects) // 2), replace=False))
        sel_mask = train["subject_id"].astype(str).isin(picked).to_numpy()
        hold_mask = ~sel_mask
        best = None
        for w in GRID:
            p = (1.0 - w) * base[:, target_idx] + w * proxy[:, target_idx]
            sel_loss = loss_col(y[sel_mask, target_idx], p[sel_mask])
            if best is None or sel_loss < best[0]:
                best = (sel_loss, float(w), p)
        assert best is not None
        hold_current = loss_col(y[hold_mask, target_idx], base[hold_mask, target_idx])
        hold_blend = loss_col(y[hold_mask, target_idx], best[2][hold_mask])
        deltas.append(float(hold_blend - hold_current))
        selected_weights.append(best[1])
        zero += int(best[1] == 0.0)
    arr = np.asarray(deltas, dtype=float)
    return {
        "mean_delta": float(arr.mean()),
        "median_delta": float(np.median(arr)),
        "p25_delta": float(np.quantile(arr, 0.25)),
        "p75_delta": float(np.quantile(arr, 0.75)),
        "win_rate": float((arr < 0).mean()),
        "mean_selected_weight": float(np.mean(selected_weights)),
        "zero_weight_rate": float(zero / n_repeats),
    }


def scan(base_oof: Path, prefix: str, repeats: int, seed: int) -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(KEY).reset_index(drop=True)
    y = train[TARGETS].to_numpy(dtype=int)
    base = clip(np.load(base_oof))
    rows = []
    summary_rows = [
        {"target": "mean", "base_loss": mean_loss(y, base), "proxy": base_oof.name, "note": "base"}
    ]
    for path in proxy_files():
        proxy = clip(np.load(path))
        if proxy.shape != base.shape:
            continue
        for j, target in enumerate(TARGETS):
            base_loss = loss_col(y[:, j], base[:, j])
            proxy_loss = loss_col(y[:, j], proxy[:, j])
            losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * proxy[:, j]) for w in GRID]
            best_i = int(np.argmin(losses))
            best_w = float(GRID[best_i])
            best_loss = float(losses[best_i])
            row = {
                "proxy": path.name,
                "target": target,
                "base_loss": base_loss,
                "proxy_loss": proxy_loss,
                "best_weight": best_w,
                "best_blend_loss": best_loss,
                "delta_vs_base": best_loss - base_loss,
            }
            if best_w > 0.0 and best_loss < base_loss:
                row.update(repeated_subject_guardrail(train, y, base, proxy, j, repeats, seed + 97 * j + len(rows)))
            else:
                row.update(
                    {
                        "mean_delta": 0.0,
                        "median_delta": 0.0,
                        "p25_delta": 0.0,
                        "p75_delta": 0.0,
                        "win_rate": 0.0,
                        "mean_selected_weight": 0.0,
                        "zero_weight_rate": 1.0,
                    }
                )
            row["passes_loose"] = bool(
                row["delta_vs_base"] <= -0.0002 and row["mean_delta"] < 0.0 and row["win_rate"] >= 0.58
            )
            row["passes_strict"] = bool(
                row["delta_vs_base"] <= -0.0005 and row["mean_delta"] <= -0.0002 and row["win_rate"] >= 0.65
            )
            rows.append(row)
    result = pd.DataFrame(rows).sort_values(["passes_strict", "passes_loose", "delta_vs_base"], ascending=[False, False, True])
    result.to_csv(OUT / f"{prefix}_sleep_proxy_residual_scan.csv", index=False)
    top = result.groupby("target", group_keys=False).head(10)
    top.to_csv(OUT / f"{prefix}_sleep_proxy_residual_scan_top.csv", index=False)
    selected = result[result["passes_loose"]].copy()
    selected.to_csv(OUT / f"{prefix}_sleep_proxy_residual_scan_selected.csv", index=False)
    pd.DataFrame(summary_rows).to_csv(OUT / f"{prefix}_sleep_proxy_residual_scan_base.csv", index=False)
    print("base", summary_rows[0])
    print(result.head(30).round(6).to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", type=Path, default=OUT / "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy")
    parser.add_argument("--prefix", default="current_0p578")
    parser.add_argument("--repeats", type=int, default=240)
    parser.add_argument("--seed", type=int, default=260982)
    args = parser.parse_args()
    scan(args.base_oof, args.prefix, args.repeats, args.seed)


if __name__ == "__main__":
    main()
