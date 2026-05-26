from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import meta_feature_experiments as mf  # noqa: E402
import q23_presleep_app_experiments as app  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGET = "Q1"
TIDX = d.TARGETS.index(TARGET)


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(log_loss(y, clip(pred), labels=[0, 1]))


def soft_rate_oof(train: pd.DataFrame, r: float, shrink: float) -> np.ndarray:
    pred = np.zeros(len(train), dtype=float)
    folds = d.make_folds(train, "subject_blocks")
    for tr_idx, val_idx in folds:
        ref = train.iloc[tr_idx]
        rows = train.iloc[val_idx].reset_index(drop=True)
        global_rate = float(ref[TARGET].mean())
        for sid, g in rows.groupby("subject_id", sort=False):
            known = ref[ref["subject_id"] == sid]
            n_known = len(known)
            n_hidden = len(g)
            known_pos = float(known[TARGET].sum())
            raw = (r * (n_known + n_hidden) - known_pos + shrink * global_rate) / (n_hidden + shrink)
            pred[val_idx[g.index.to_numpy()]] = float(np.clip(raw, 0.03, 0.97))
    return clip(pred)


def app_oof(train: pd.DataFrame, store: app.AppFeatureStore, cand: app.Candidate) -> np.ndarray:
    pred = np.zeros(len(train), dtype=float)
    for tr_idx, val_idx in d.make_folds(train, "subject_blocks"):
        tr = train.iloc[tr_idx].copy().reset_index(drop=True)
        val = train.iloc[val_idx].copy().reset_index(drop=True)
        pred[val_idx] = app.fit_candidate(tr, val, store, TARGET, cand)
    return clip(pred)


def main() -> None:
    train, sub = mf.prepare(force_meta=False)
    train = train.sort_values(d.KEY).reset_index(drop=True)
    sub = sub.sort_values(d.KEY).reset_index(drop=True)
    y = train[TARGET].to_numpy(dtype=int)
    folds = d.make_folds(train, "subject_blocks")

    backbones = {"temporal": cal.base_oof(train, folds)[:, TIDX]}
    for name in ["overnight_phone", "overnight_all", "overnight_context", "current_missing"]:
        path = OUT / f"{name}_oof.npy"
        if path.exists():
            backbones[name] = np.load(path)[:, TIDX]

    all_keys = pd.concat([train[d.KEY], sub[d.KEY]], ignore_index=True)
    store = app.build_app_feature_store(all_keys)
    app_preds = {
        cand.name: app_oof(train, store, cand)
        for cand in app.CANDIDATES
        if cand.name in {"logreg_c0.03", "te_global_s2", "te_global_s6"}
    }
    soft_preds = {
        (r, shrink): soft_rate_oof(train, r, shrink)
        for r in [0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
        for shrink in [1.0, 2.0, 4.0, 8.0, 16.0]
    }

    rows = []
    for backbone_name, backbone in backbones.items():
        rows.append(
            {
                "backbone": backbone_name,
                "app": "none",
                "app_weight": 0.0,
                "soft_r": np.nan,
                "soft_shrink": np.nan,
                "soft_weight": 0.0,
                "Q1": loss(y, backbone),
            }
        )
        for app_name, app_pred in app_preds.items():
            for app_weight in [0.05, 0.10, 0.15, 0.20, 0.30]:
                pred = (1.0 - app_weight) * backbone + app_weight * app_pred
                rows.append(
                    {
                        "backbone": backbone_name,
                        "app": app_name,
                        "app_weight": app_weight,
                        "soft_r": np.nan,
                        "soft_shrink": np.nan,
                        "soft_weight": 0.0,
                        "Q1": loss(y, pred),
                    }
                )
        for (r, shrink), soft_pred in soft_preds.items():
            for soft_weight in [0.05, 0.10, 0.15, 0.20, 0.30]:
                pred = (1.0 - soft_weight) * backbone + soft_weight * soft_pred
                rows.append(
                    {
                        "backbone": backbone_name,
                        "app": "none",
                        "app_weight": 0.0,
                        "soft_r": r,
                        "soft_shrink": shrink,
                        "soft_weight": soft_weight,
                        "Q1": loss(y, pred),
                    }
                )
        for app_name, app_pred in app_preds.items():
            for (r, shrink), soft_pred in soft_preds.items():
                for app_weight in [0.05, 0.10, 0.15]:
                    for soft_weight in [0.05, 0.10, 0.15]:
                        pred = (1.0 - app_weight - soft_weight) * backbone + app_weight * app_pred + soft_weight * soft_pred
                        rows.append(
                            {
                                "backbone": backbone_name,
                                "app": app_name,
                                "app_weight": app_weight,
                                "soft_r": r,
                                "soft_shrink": shrink,
                                "soft_weight": soft_weight,
                                "Q1": loss(y, pred),
                            }
                        )

    result = pd.DataFrame(rows).sort_values("Q1").reset_index(drop=True)
    result.to_csv(OUT / "q1_soft_app_diagnostic_results.csv", index=False)
    print(result.head(30).round(6).to_string(index=False))


if __name__ == "__main__":
    main()
