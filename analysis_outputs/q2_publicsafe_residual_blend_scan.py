from __future__ import annotations

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

import geometry_mask_cv_experiments as geom  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
SORT_KEY = ["subject_id", "lifelog_date"]
Q2_IDX = TARGETS.index("Q2")
EPS = 1e-5


BASE_FILES = [
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
    "submission_public_universeens_u65_r01_365a84a6.csv",
    "submission_public_universeens_u65_r02_c0e2b2f1.csv",
    "submission_public_universeens_u65_r03_cf973915.csv",
    "submission_public_universeens_u65_r04_dc6f3303.csv",
    "submission_public_minimaxens_r01_a6_h422045.csv",
    "submission_public_minimaxens_r05_a10_h506746.csv",
    "submission_public_maskplausens_r04_161f5469.csv",
    "submission_public_maskplausens_r05_e8325bb7.csv",
    "submission_public_maskaware_t50_r05_fb7b695a.csv",
    "submission_public_maskaware_t65_r07_768f6df0.csv",
    "submission_public_maskaware_t80_r11_544844af.csv",
]

PINNED_RESIDUAL_FILES = [
    "submission_temporal_bridge_q3off650_r8_Q2__a0.2_gw0.5_stay1.5_sh16_bw0.35_Q3__a0.2_gw0.5_stay1.5_sh16_bw0.35.csv",
    "submission_boundary_minimax_zeros_only_0b236468.csv",
    "submission_q2_soft_app_stack.csv",
    "submission_hybrid_0p573_foldsafe_broad_q2_activity_transition.csv",
    "submission_hybrid_0p573_foldsafe_broad_q1_calltime_q2_activity.csv",
    "submission_hybrid_0p586_subject_relative_resweep_q2loose.csv",
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
]


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


def oof_name_for_submission(file_name: str) -> str:
    return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")


def load_submission(file_name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def load_pair(file_name: str) -> tuple[pd.DataFrame, np.ndarray] | None:
    sub_path = OUT / file_name
    oof_path = OUT / oof_name_for_submission(file_name)
    if not sub_path.exists() or not oof_path.exists():
        return None
    sub = load_submission(file_name)
    oof = clip(np.load(oof_path))
    return sub, oof


def blend_col(base: np.ndarray, donor: np.ndarray, weight: float, mode: str) -> np.ndarray:
    if mode == "prob":
        return clip((1.0 - weight) * base + weight * donor)
    if mode == "logit":
        return clip(sigmoid((1.0 - weight) * logit(base) + weight * logit(donor)))
    raise ValueError(mode)


def candidate_file_catalog(train: pd.DataFrame, top_n: int = 260) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows: list[dict[str, object]] = []
    seen = set()
    for f in PINNED_RESIDUAL_FILES:
        if f in seen:
            continue
        pair = load_pair(f)
        if pair is None:
            continue
        _, oof = pair
        rows.append({"file": f, "source": "pinned", "mean": mean_loss(y, oof), "Q2": loss_col(y[:, Q2_IDX], oof[:, Q2_IDX])})
        seen.add(f)
    for path in sorted(OUT.glob("final_*_oof.npy")):
        if not path.name.endswith("_oof.npy"):
            continue
        f = "submission_" + path.name.removeprefix("final_").removesuffix("_oof.npy") + ".csv"
        if f in seen or not (OUT / f).exists():
            continue
        try:
            oof = clip(np.load(path))
        except Exception:
            continue
        if oof.shape != (len(train), len(TARGETS)):
            continue
        rows.append({"file": f, "source": "auto", "mean": mean_loss(y, oof), "Q2": loss_col(y[:, Q2_IDX], oof[:, Q2_IDX])})
        seen.add(f)
    table = pd.DataFrame(rows).sort_values(["Q2", "mean", "file"]).reset_index(drop=True)
    pinned = table[table["source"].eq("pinned")]
    auto = table[~table["source"].eq("pinned")].head(top_n)
    return pd.concat([pinned, auto], ignore_index=True).drop_duplicates("file").reset_index(drop=True)


def geometry_q2_delta(
    y: np.ndarray,
    base_oof: np.ndarray,
    blended_oof: np.ndarray,
    folds: list[tuple[np.ndarray, np.ndarray, str]],
) -> dict[str, float]:
    deltas = []
    for _tr_idx, val_idx, _fold_name in folds:
        before = loss_col(y[val_idx, Q2_IDX], base_oof[val_idx, Q2_IDX])
        after = loss_col(y[val_idx, Q2_IDX], blended_oof[val_idx, Q2_IDX])
        deltas.append(after - before)
    arr = np.asarray(deltas, dtype=float)
    return {
        "geom_q2_delta_mean": float(arr.mean()),
        "geom_q2_delta_median": float(np.median(arr)),
        "geom_q2_win_rate": float((arr < 0.0).mean()),
        "geom_q2_worst_delta": float(arr.max()),
    }


def axis_context() -> dict[str, object]:
    obs = pd.read_csv(OUT / "public_probe_observations.csv").set_index("file")["public_lb"].astype(float)
    anchor = "submission_hybrid_0p578_logit_after_subject_final9_strict.csv"
    stage2 = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
    ordinal = "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv"
    anchor_vec = load_submission(anchor)[TARGETS].to_numpy(dtype=float).reshape(-1)
    stage2_vec = load_submission(stage2)[TARGETS].to_numpy(dtype=float).reshape(-1)
    ordinal_vec = load_submission(ordinal)[TARGETS].to_numpy(dtype=float).reshape(-1)
    bad = ordinal_vec - stage2_vec
    axes = np.column_stack([stage2_vec - anchor_vec, bad])
    return {
        "stage2_public": float(obs[stage2]),
        "anchor_public": float(obs[anchor]),
        "ordinal_public": float(obs[ordinal]),
        "stage2_vec": stage2_vec,
        "bad": bad,
        "bad_denom": float(np.dot(bad, bad)),
        "axes": axes,
    }


def axis_metrics(sub_pred: np.ndarray, ctx: dict[str, object]) -> dict[str, float]:
    stage2_vec = np.asarray(ctx["stage2_vec"], dtype=float)
    bad = np.asarray(ctx["bad"], dtype=float)
    move = sub_pred.reshape(-1) - stage2_vec
    bad_denom = float(ctx["bad_denom"])
    projection = float(np.dot(move, bad) / bad_denom) if bad_denom > 0 else 0.0
    stage2_public = float(ctx["stage2_public"])
    ordinal_public = float(ctx["ordinal_public"])
    anchor_public = float(ctx["anchor_public"])
    public_gap = ordinal_public - stage2_public

    axes = np.asarray(ctx["axes"], dtype=float)
    coef = np.linalg.lstsq(axes, move, rcond=None)[0]
    fitted = axes @ coef
    move_norm = float(np.linalg.norm(move))
    two_axis_delta = float(coef[0]) * (stage2_public - anchor_public) + float(coef[1]) * public_gap
    return {
        "one_axis_bad_projection": projection,
        "one_axis_public_est": stage2_public + projection * public_gap,
        "one_axis_public_delta_vs_stage2": projection * public_gap,
        "good_axis_coef": float(coef[0]),
        "bad_axis_coef": float(coef[1]),
        "two_axis_residual_ratio": float(np.linalg.norm(move - fitted) / max(move_norm, 1e-12)),
        "two_axis_public_est": stage2_public + two_axis_delta,
        "two_axis_public_delta_vs_stage2": two_axis_delta,
    }


def build_blended_submission(base_sub: pd.DataFrame, donor_sub: pd.DataFrame, weight: float, mode: str) -> pd.DataFrame:
    out = base_sub.copy()
    out["Q2"] = blend_col(
        base_sub["Q2"].to_numpy(dtype=float),
        donor_sub["Q2"].to_numpy(dtype=float),
        weight,
        mode,
    )
    return out


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    sub_sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    y = train[TARGETS].to_numpy(dtype=int)
    folds = geom.geometry_folds(train, sub_sample, n_repeats=8)
    axes = axis_context()

    residual_catalog = candidate_file_catalog(train)
    residual_catalog.to_csv(OUT / "q2_publicsafe_residual_catalog.csv", index=False)

    base_pairs = {f: load_pair(f) for f in BASE_FILES if load_pair(f) is not None}
    residual_pairs = {f: load_pair(f) for f in residual_catalog["file"].tolist() if load_pair(f) is not None}

    records: list[dict[str, object]] = []
    weights = [0.02, 0.035, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30, 0.45, 0.65, 1.0]
    modes = ["logit", "prob"]
    for base_file, (base_sub, base_oof) in base_pairs.items():
        if not base_sub[KEY].equals(sub_sample[KEY]):
            continue
        base_q2 = loss_col(y[:, Q2_IDX], base_oof[:, Q2_IDX])
        base_mean = mean_loss(y, base_oof)
        for donor_file, (donor_sub, donor_oof) in residual_pairs.items():
            if donor_file == base_file or not donor_sub[KEY].equals(sub_sample[KEY]):
                continue
            donor_q2 = loss_col(y[:, Q2_IDX], donor_oof[:, Q2_IDX])
            if donor_q2 > base_q2 + 0.010 and donor_file not in PINNED_RESIDUAL_FILES:
                continue
            for mode in modes:
                for w in weights:
                    pred = base_oof.copy()
                    pred[:, Q2_IDX] = blend_col(base_oof[:, Q2_IDX], donor_oof[:, Q2_IDX], w, mode)
                    q2 = loss_col(y[:, Q2_IDX], pred[:, Q2_IDX])
                    mean = mean_loss(y, pred)
                    if q2 > base_q2 + 0.00020:
                        continue
                    sub_pred = build_blended_submission(base_sub, donor_sub, w, mode)
                    pred_matrix = sub_pred[TARGETS].to_numpy(dtype=float)
                    rec = {
                        "base_file": base_file,
                        "donor_file": donor_file,
                        "mode": mode,
                        "weight": w,
                        "base_mean": base_mean,
                        "blend_mean": mean,
                        "mean_delta": mean - base_mean,
                        "base_Q2": base_q2,
                        "donor_Q2": donor_q2,
                        "blend_Q2": q2,
                        "Q2_delta": q2 - base_q2,
                        "submission_q2_abs_move": float(np.abs(sub_pred["Q2"].to_numpy(dtype=float) - base_sub["Q2"].to_numpy(dtype=float)).mean()),
                    }
                    rec.update(geometry_q2_delta(y, base_oof, pred, folds))
                    rec.update(axis_metrics(pred_matrix, axes))
                    records.append(rec)

    scan = pd.DataFrame(records)
    if scan.empty:
        raise RuntimeError("No Q2 blend records produced.")
    scan["abs_bad_axis"] = scan["bad_axis_coef"].abs()
    scan = scan.sort_values(
        [
            "mean_delta",
            "geom_q2_delta_mean",
            "abs_bad_axis",
            "submission_q2_abs_move",
        ]
    ).reset_index(drop=True)
    scan.to_csv(OUT / "q2_publicsafe_residual_blend_scan.csv", index=False)

    guard = scan[
        (scan["mean_delta"] < -0.00002)
        & (scan["geom_q2_delta_mean"] < -0.00015)
        & (scan["geom_q2_win_rate"] >= 0.625)
        & (scan["abs_bad_axis"] <= 0.18)
        & (scan["submission_q2_abs_move"] <= 0.020)
    ].copy()
    if guard.empty:
        guard = scan[
            (scan["mean_delta"] < -0.00002)
            & (scan["geom_q2_delta_mean"] < 0.0)
            & (scan["geom_q2_win_rate"] >= 0.50)
            & (scan["abs_bad_axis"] <= 0.25)
            & (scan["submission_q2_abs_move"] <= 0.030)
        ].copy()
    guard = guard.sort_values(["mean_delta", "geom_q2_delta_mean", "submission_q2_abs_move"]).head(16).reset_index(drop=True)

    saved_rows: list[dict[str, object]] = []
    for rank, row in guard.iterrows():
        base_file = str(row["base_file"])
        donor_file = str(row["donor_file"])
        mode = str(row["mode"])
        weight = float(row["weight"])
        base_sub, base_oof = base_pairs[base_file]
        donor_sub, donor_oof = residual_pairs[donor_file]
        out = build_blended_submission(base_sub, donor_sub, weight, mode)
        pred_oof = base_oof.copy()
        pred_oof[:, Q2_IDX] = blend_col(base_oof[:, Q2_IDX], donor_oof[:, Q2_IDX], weight, mode)
        tag = stable_tag(f"{base_file}|{donor_file}|{mode}|{weight:.5f}")
        file_name = f"submission_q2_publicsafe_blend_r{rank + 1:02d}_{tag}.csv"
        out.to_csv(OUT / file_name, index=False)
        np.save(OUT / oof_name_for_submission(file_name), clip(pred_oof))
        saved = row.to_dict()
        saved["file"] = file_name
        saved_rows.append(saved)

    selected = pd.DataFrame(saved_rows)
    selected.to_csv(OUT / "q2_publicsafe_residual_blend_selected.csv", index=False)

    cols = [
        "file",
        "base_file",
        "donor_file",
        "mode",
        "weight",
        "mean_delta",
        "Q2_delta",
        "geom_q2_delta_mean",
        "geom_q2_win_rate",
        "submission_q2_abs_move",
        "two_axis_public_delta_vs_stage2",
        "bad_axis_coef",
    ]
    print("[q2 residual catalog]")
    print(residual_catalog.head(24).round(6).to_string(index=False))
    print("\n[q2 selected blends]")
    print(selected[cols].round(9).to_string(index=False) if not selected.empty else "(empty)")


if __name__ == "__main__":
    main()
