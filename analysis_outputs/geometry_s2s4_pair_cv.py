from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import deep_dive_analysis as d  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402
import overnight_feature_experiments as ofe  # noqa: E402
import s2s4_pair_blend_nested_experiments as s2s4  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY
PAIR_TARGETS = ["S2", "S4"]
WEIGHT_GRID = np.array([0.0, 0.10, 0.20, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 1.0])


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def loss_1d(y: np.ndarray, p: np.ndarray) -> float:
    return float(log_loss(y.astype(int), clip(p), labels=[0, 1]))


def choice_predict(records: pd.DataFrame, target: str, left: str, right: str, weight_right: float) -> np.ndarray:
    return (
        (1.0 - weight_right) * records[f"{left}__{target}"].to_numpy(dtype=float)
        + weight_right * records[f"{right}__{target}"].to_numpy(dtype=float)
    )


def collect_records(train: pd.DataFrame, sub: pd.DataFrame) -> pd.DataFrame:
    rows = []
    folds = geom.geometry_folds(train[KEY + ["sleep_date"] + TARGETS], sub[KEY + ["sleep_date"]], n_repeats=8, target_frac=0.22)
    for tr_idx, val_idx, fold_name in folds:
        repeat = int(fold_name.split("r")[-1])
        ref = train.iloc[tr_idx].copy().reset_index(drop=True)
        val = train.iloc[val_idx].copy().reset_index(drop=True)
        sources = s2s4.source_predict(ref, val)
        for local_i, global_i in enumerate(val_idx):
            rec = {
                "repeat": repeat,
                "row_index": int(global_i),
                "subject_id": val.loc[local_i, "subject_id"],
                "lifelog_date": val.loc[local_i, "lifelog_date"],
            }
            for target in PAIR_TARGETS:
                rec[f"y__{target}"] = int(val.loc[local_i, target])
            for name, pred in sources.items():
                for target in PAIR_TARGETS:
                    rec[f"{name}__{target}"] = float(pred[local_i, TARGETS.index(target)])
            rows.append(rec)
        print(f"[geometry s2s4] {fold_name} val={len(val_idx)}", flush=True)
    return pd.DataFrame(rows)


def evaluate_choices(records: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    source_names = ["block", "overnight_all", "overnight_context"]
    rows = []
    fixed = s2s4.fixed_choices()
    current = s2s4.current_choices()
    canned: dict[str, dict[str, tuple[str, str, float]]] = {
        "current_subjectblock_choice": current,
        "locked_subjectblock_fixed": fixed,
    }
    for name, choices in canned.items():
        rec = {"model": name, "selection": "fixed"}
        losses = []
        for target in PAIR_TARGETS:
            left, right, weight_right = choices[target]
            p = choice_predict(records, target, left, right, weight_right)
            cur_loss = loss_1d(records[f"y__{target}"].to_numpy(), p)
            rec[target] = cur_loss
            losses.append(cur_loss)
            rec[f"{target}_choice"] = f"{left}+{weight_right:g}*{right}"
        rec["pair_mean"] = float(np.mean(losses))
        rows.append(rec)

    for target in PAIR_TARGETS:
        y = records[f"y__{target}"].to_numpy(dtype=int)
        for name in source_names:
            p = records[f"{name}__{target}"].to_numpy(dtype=float)
            rows.append(
                {
                    "model": f"source_{name}_{target}",
                    "selection": "source_only",
                    "pair_mean": loss_1d(y, p),
                    target: loss_1d(y, p),
                    f"{target}_choice": name,
                }
            )

    # Select on repeats 0-3 and test on repeats 4-7 to avoid pure in-sample
    # geometry-CV tuning.
    select = records[records["repeat"] < 4].copy()
    holdout = records[records["repeat"] >= 4].copy()
    selected_rows = []
    for target in PAIR_TARGETS:
        y_sel = select[f"y__{target}"].to_numpy(dtype=int)
        best = (np.inf, "block", "block", 0.0)
        for left in source_names:
            for right in source_names:
                for weight_right in WEIGHT_GRID:
                    p = choice_predict(select, target, left, right, float(weight_right))
                    cur = loss_1d(y_sel, p)
                    if cur < best[0] - 1e-12:
                        best = (cur, left, right, float(weight_right))
        y_hold = holdout[f"y__{target}"].to_numpy(dtype=int)
        p_hold = choice_predict(holdout, target, best[1], best[2], best[3])
        selected_rows.append(
            {
                "target": target,
                "left": best[1],
                "right": best[2],
                "weight_right": best[3],
                "select_loss": best[0],
                "holdout_loss": loss_1d(y_hold, p_hold),
            }
        )
    selected = pd.DataFrame(selected_rows)
    rec = {"model": "half_selected_geometry_pair", "selection": "select_repeats_0_3_test_4_7"}
    losses = []
    for row in selected.itertuples(index=False):
        target = str(row.target)
        p = choice_predict(holdout, target, str(row.left), str(row.right), float(row.weight_right))
        cur = loss_1d(holdout[f"y__{target}"].to_numpy(), p)
        rec[target] = cur
        rec[f"{target}_choice"] = f"{row.left}+{float(row.weight_right):g}*{row.right}"
        losses.append(cur)
    rec["pair_mean"] = float(np.mean(losses))
    rows.append(rec)
    return pd.DataFrame(rows).sort_values("pair_mean"), selected


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    base = pd.read_csv(OUT / "submission_hybrid_0p598_repro.csv", parse_dates=["sleep_date", "lifelog_date"])
    base = base.sort_values(KEY).reset_index(drop=True)
    sources = s2s4.source_predict(train, sub)
    for row in selected.itertuples(index=False):
        target = str(row.target)
        p = (
            (1.0 - float(row.weight_right)) * sources[str(row.left)][:, TARGETS.index(target)]
            + float(row.weight_right) * sources[str(row.right)][:, TARGETS.index(target)]
        )
        base[target] = clip(p)
    base.to_csv(OUT / "submission_geometry_s2s4_halfselected.csv", index=False)
    return base


def main() -> None:
    train, sub = ofe.prepare()
    train = train.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    records = collect_records(train, sub)
    records.to_csv(OUT / "geometry_s2s4_pair_cv_records.csv", index=False)
    results, selected = evaluate_choices(records)
    results.to_csv(OUT / "geometry_s2s4_pair_cv_results.csv", index=False)
    selected.to_csv(OUT / "geometry_s2s4_pair_cv_selected.csv", index=False)
    out = make_submission(train, sub, selected)
    print(results.round(6).to_string(index=False))
    print("\nSelected")
    print(selected.round(6).to_string(index=False))
    print("wrote", OUT / "submission_geometry_s2s4_halfselected.csv", out.shape)


if __name__ == "__main__":
    main()
