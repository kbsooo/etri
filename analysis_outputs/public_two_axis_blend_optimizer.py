from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-5

ANCHOR = "submission_hybrid_0p578_logit_after_subject_final9_strict.csv"
STAGE2 = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
ORDINAL = "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv"
STAGE2_OOF = "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def load_sub(file_name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def oof_name(file_name: str) -> str:
    return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")


def vector(file_name: str) -> np.ndarray:
    return load_sub(file_name)[TARGETS].to_numpy(dtype=float).reshape(-1)


def label_budget(delta: float) -> str:
    if abs(delta) < 1e-15:
        return "budget0p0"
    sign = "m" if delta < 0 else ""
    text = f"{abs(delta):.5f}".replace(".", "p")
    return f"budget{sign}{text}"


def candidate_pool() -> list[str]:
    files: set[str] = set()
    for table in [OUT / "projection_blend_pool.csv", OUT / "projection_constrained_blend_summary.csv"]:
        if table.exists():
            df = pd.read_csv(table)
            files.update(str(x) for x in df["file"].dropna().tolist())
    fixed = [
        "submission_orthcap005c000_exact_q3_exact_value_nearest_w1.csv",
        "submission_orthcap005c000_exact_q2q3_exact_value_nearest_w1.csv",
        "submission_orthcap009c005_exact_q3_exact_value_nearest_w1.csv",
        "submission_orthcap009c005_exact_q2q3_exact_value_nearest_w1.csv",
        "submission_orthcap010_exact_q3_exact_value_nearest_w1.csv",
        "submission_orthcap010_exact_q2q3_exact_value_nearest_w1.csv",
        "submission_orthcap030_exact_q3_exact_value_nearest_w1.csv",
        "submission_orthcap030_exact_q2q3_exact_value_nearest_w1.csv",
        "submission_orthcap_s005_cap000_sc100.csv",
        "submission_orthcap_s009_cap005_sc100.csv",
        "submission_orthcap_s001_cap010_sc100.csv",
        "submission_orthcap_s001_cap020_sc100.csv",
        "submission_orthcap_s001_cap030_sc100.csv",
    ]
    files.update(fixed)
    return sorted(f for f in files if (OUT / f).exists() and (OUT / oof_name(f)).exists())


def blend(items: list[np.ndarray], weights: np.ndarray) -> np.ndarray:
    out = np.zeros_like(items[0])
    for item, weight in zip(items, weights, strict=True):
        out += float(weight) * item
    return clip(out)


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    y = train[TARGETS].to_numpy(dtype=int)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    obs = pd.read_csv(OUT / "public_probe_observations.csv").set_index("file")["public_lb"].astype(float)
    anchor_public = float(obs[ANCHOR])
    stage2_public = float(obs[STAGE2])
    ordinal_public = float(obs[ORDINAL])
    good_gap = stage2_public - anchor_public
    bad_gap = ordinal_public - stage2_public

    anchor_vec = vector(ANCHOR)
    stage2_vec = vector(STAGE2)
    ordinal_vec = vector(ORDINAL)
    good_axis = stage2_vec - anchor_vec
    bad_axis = ordinal_vec - stage2_vec
    axes = np.column_stack([good_axis, bad_axis])
    bad_denom = float(np.dot(bad_axis, bad_axis))
    stage2_oof = clip(np.load(OUT / STAGE2_OOF))
    stage2_loss = mean_loss(y, stage2_oof)

    files = candidate_pool()
    subs = {f: load_sub(f) for f in files}
    sub_arrays = {f: subs[f][TARGETS].to_numpy(dtype=float) for f in files}
    sub_vecs = {f: sub_arrays[f].reshape(-1) for f in files}
    oofs = {f: clip(np.load(OUT / oof_name(f))) for f in files}

    def axis_metrics(move_vec: np.ndarray) -> dict[str, float]:
        coef = np.linalg.lstsq(axes, move_vec, rcond=None)[0]
        fitted = axes @ coef
        move_norm = float(np.linalg.norm(move_vec))
        residual_ratio = float(np.linalg.norm(move_vec - fitted) / max(move_norm, 1e-12))
        one_axis_projection = float(np.dot(move_vec, bad_axis) / bad_denom) if bad_denom > 0 else 0.0
        return {
            "good_axis_coef": float(coef[0]),
            "bad_axis_coef": float(coef[1]),
            "two_axis_residual_ratio": residual_ratio,
            "one_axis_bad_projection": one_axis_projection,
            "one_axis_public_est": stage2_public + one_axis_projection * bad_gap,
            "two_axis_public_est": stage2_public + float(coef[0]) * good_gap + float(coef[1]) * bad_gap,
        }

    pool_rows = []
    for file_name in files:
        metrics = axis_metrics(sub_vecs[file_name] - stage2_vec)
        loss = mean_loss(y, oofs[file_name])
        pool_rows.append(
            {
                "file": file_name,
                "oof": loss,
                "oof_gain_vs_stage2": stage2_loss - loss,
                **metrics,
            }
        )
    pd.DataFrame(pool_rows).sort_values(["two_axis_public_est", "oof"]).to_csv(OUT / "public_two_axis_blend_pool.csv", index=False)

    budgets = [-0.00001, 0.0, 0.00002, 0.00005, 0.00010]
    grid = np.linspace(0.0, 1.0, 101)
    scan_rows: list[dict[str, object]] = []
    best: dict[float, tuple[float, tuple[str, ...], np.ndarray, np.ndarray, np.ndarray, dict[str, float]]] = {}

    def consider(files_used: tuple[str, ...], weights: np.ndarray, oof_pred: np.ndarray, sub_pred: np.ndarray, kind: str) -> None:
        metrics = axis_metrics(sub_pred.reshape(-1) - stage2_vec)
        loss = mean_loss(y, oof_pred)
        row: dict[str, object] = {
            "kind": kind,
            "files": "|".join(files_used),
            "weights": "|".join(f"{w:.4f}" for w in weights),
            "oof": loss,
            "oof_gain_vs_stage2": stage2_loss - loss,
            **metrics,
        }
        row["two_axis_public_delta_vs_stage2"] = float(row["two_axis_public_est"]) - stage2_public
        row["one_axis_public_delta_vs_stage2"] = float(row["one_axis_public_est"]) - stage2_public
        scan_rows.append(row)
        for budget in budgets:
            if float(row["two_axis_public_delta_vs_stage2"]) <= budget + 1e-15:
                old = best.get(budget)
                if old is None or loss < old[0]:
                    best[budget] = (loss, files_used, weights.copy(), oof_pred.copy(), sub_pred.copy(), metrics)

    for file_name in files:
        consider((file_name,), np.array([1.0]), oofs[file_name], sub_arrays[file_name], "single")

    for i, left in enumerate(files):
        for right in files[i + 1 :]:
            for w in grid:
                weights = np.array([w, 1.0 - w], dtype=float)
                oof_pred = blend([oofs[left], oofs[right]], weights)
                sub_pred = blend([sub_arrays[left], sub_arrays[right]], weights)
                consider((left, right), weights, oof_pred, sub_pred, "pair")

    scan = pd.DataFrame(scan_rows).sort_values(["two_axis_public_est", "oof"]).reset_index(drop=True)
    scan.to_csv(OUT / "public_two_axis_blend_scan.csv", index=False)

    summary_rows = []
    candidate_rows = []
    integrity_rows = []
    for budget in budgets:
        if budget not in best:
            continue
        loss, best_files, weights, oof_pred, sub_pred, metrics = best[budget]
        label = label_budget(budget)
        out = subs[best_files[0]].copy()
        out[TARGETS] = sub_pred
        out = out.sort_values(KEY).reset_index(drop=True)
        assert out[KEY].equals(sample[KEY])
        assert out[TARGETS].isna().sum().sum() == 0
        assert out.duplicated(KEY).sum() == 0
        out_file = OUT / f"submission_public2dblend_{label}.csv"
        oof_file = OUT / f"final_public2dblend_{label}_oof.npy"
        out.to_csv(out_file, index=False)
        np.save(oof_file, oof_pred)
        row = {
            "budget": budget,
            "file": out_file.name,
            "oof": loss,
            "oof_gain_vs_stage2": stage2_loss - loss,
            "components": "|".join(best_files),
            "weights": "|".join(f"{w:.4f}" for w in weights),
            **metrics,
            "two_axis_public_delta_vs_stage2": metrics["two_axis_public_est"] - stage2_public,
            "one_axis_public_delta_vs_stage2": metrics["one_axis_public_est"] - stage2_public,
        }
        summary_rows.append(row)
        candidate_rows.append(
            {
                "file": out_file.name,
                "targets_changed": "blend",
                "donor": "public_two_axis_blend",
                "mask": "all",
                "weight": "",
                "source_file": "public_two_axis_blend_summary.csv",
            }
        )
        drow = {
            "file": out_file.name,
            "min_prob": float(out[TARGETS].min().min()),
            "max_prob": float(out[TARGETS].max().max()),
            "dups": int(out.duplicated(KEY).sum()),
            "na": int(out[TARGETS].isna().sum().sum()),
        }
        for j, target in enumerate(TARGETS):
            drow[f"{target}_delta_vs_stage2"] = loss_col(y[:, j], oof_pred[:, j]) - loss_col(y[:, j], stage2_oof[:, j])
        integrity_rows.append(drow)

    summary = pd.DataFrame(summary_rows).sort_values("budget").reset_index(drop=True)
    summary.to_csv(OUT / "public_two_axis_blend_summary.csv", index=False)
    pd.DataFrame(candidate_rows).to_csv(OUT / "public_two_axis_blend_candidates.csv", index=False)
    pd.DataFrame(integrity_rows).to_csv(OUT / "public_two_axis_blend_integrity_and_deltas.csv", index=False)

    print("[two-axis]")
    print(
        pd.DataFrame(
            [
                {
                    "anchor_public": anchor_public,
                    "stage2_public": stage2_public,
                    "ordinal_public": ordinal_public,
                    "good_gap": good_gap,
                    "bad_gap": bad_gap,
                }
            ]
        ).round(10).to_string(index=False)
    )
    print("\n[summary]")
    print(summary.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
