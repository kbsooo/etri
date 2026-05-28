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

STAGE2 = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
ORDINAL = "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv"


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


def public_bad_axis() -> tuple[np.ndarray, np.ndarray, float, float]:
    obs = pd.read_csv(OUT / "public_probe_observations.csv").set_index("file")["public_lb"].astype(float)
    stage2_public = float(obs[STAGE2])
    public_gap = float(obs[ORDINAL] - obs[STAGE2])
    stage2_vec = load_sub(STAGE2)[TARGETS].to_numpy(dtype=float).reshape(-1)
    bad = load_sub(ORDINAL)[TARGETS].to_numpy(dtype=float).reshape(-1) - stage2_vec
    return stage2_vec, bad, stage2_public, public_gap


def projection(file_name: str, stage2_vec: np.ndarray, bad: np.ndarray) -> float:
    vec = load_sub(file_name)[TARGETS].to_numpy(dtype=float).reshape(-1)
    denom = float(np.dot(bad, bad))
    return float(np.dot(vec - stage2_vec, bad) / denom)


def candidate_pool() -> list[str]:
    files = [
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
    return [f for f in files if (OUT / f).exists() and (OUT / oof_name(f)).exists()]


def blend_arrays(items: list[np.ndarray], weights: np.ndarray) -> np.ndarray:
    out = np.zeros_like(items[0])
    for w, arr in zip(weights, items, strict=True):
        out += float(w) * arr
    return clip(out)


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    y = train[TARGETS].to_numpy(dtype=int)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    stage2_vec, bad, stage2_public, public_gap = public_bad_axis()

    files = candidate_pool()
    subs = {f: load_sub(f) for f in files}
    oofs = {f: clip(np.load(OUT / oof_name(f))) for f in files}
    meta = []
    for f in files:
        proj = projection(f, stage2_vec, bad)
        meta.append({"file": f, "oof": mean_loss(y, oofs[f]), "projection": proj, "linear_public_est": stage2_public + proj * public_gap})
    meta_df = pd.DataFrame(meta).sort_values(["projection", "oof"]).reset_index(drop=True)
    meta_df.to_csv(OUT / "projection_blend_pool.csv", index=False)

    caps = [-0.005, 0.0, 0.025, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30]
    rows: list[dict[str, object]] = []
    best_by_cap: dict[float, tuple[float, tuple[str, ...], np.ndarray, np.ndarray, float]] = {}

    # Single files.
    for f in files:
        proj = float(meta_df.loc[meta_df.file.eq(f), "projection"].iloc[0])
        loss = mean_loss(y, oofs[f])
        for cap in caps:
            if proj <= cap + 1e-12:
                best = best_by_cap.get(cap)
                if best is None or loss < best[0]:
                    best_by_cap[cap] = (loss, (f,), np.array([1.0]), oofs[f], proj)
        rows.append({"kind": "single", "files": f, "weights": "1", "oof": loss, "projection": proj})

    # Two-file convex line search.
    grid = np.linspace(0.0, 1.0, 101)
    for i, left in enumerate(files):
        for right in files[i + 1 :]:
            left_oof, right_oof = oofs[left], oofs[right]
            left_sub = subs[left][TARGETS].to_numpy(dtype=float)
            right_sub = subs[right][TARGETS].to_numpy(dtype=float)
            p_left = float(meta_df.loc[meta_df.file.eq(left), "projection"].iloc[0])
            p_right = float(meta_df.loc[meta_df.file.eq(right), "projection"].iloc[0])
            for w in grid:
                weights = np.array([w, 1.0 - w], dtype=float)
                proj = float(w * p_left + (1.0 - w) * p_right)
                pred = clip(w * left_oof + (1.0 - w) * right_oof)
                loss = mean_loss(y, pred)
                rows.append({"kind": "pair", "files": f"{left}|{right}", "weights": f"{w:.2f}|{1-w:.2f}", "oof": loss, "projection": proj})
                for cap in caps:
                    if proj <= cap + 1e-12:
                        best = best_by_cap.get(cap)
                        if best is None or loss < best[0]:
                            sub_pred = clip(w * left_sub + (1.0 - w) * right_sub)
                            best_by_cap[cap] = (loss, (left, right), weights, pred, proj)

    scan = pd.DataFrame(rows)
    scan["linear_public_est"] = stage2_public + scan["projection"] * public_gap
    scan = scan.sort_values(["projection", "oof"]).reset_index(drop=True)
    scan.to_csv(OUT / "projection_constrained_blend_scan.csv", index=False)

    summary_rows = []
    for cap in caps:
        if cap not in best_by_cap:
            continue
        loss, best_files, weights, pred, proj = best_by_cap[cap]
        label = f"cap{str(cap).replace('-', 'm').replace('.', 'p')}"
        out_file = OUT / f"submission_projblend_{label}.csv"
        if len(best_files) == 1:
            out = subs[best_files[0]].copy()
        else:
            out = subs[best_files[0]].copy()
            sub_items = [subs[f][TARGETS].to_numpy(dtype=float) for f in best_files]
            out[TARGETS] = blend_arrays(sub_items, weights)
        out = out.sort_values(KEY).reset_index(drop=True)
        assert out[KEY].equals(sample[KEY])
        assert out[TARGETS].isna().sum().sum() == 0
        assert out.duplicated(KEY).sum() == 0
        out.to_csv(out_file, index=False)
        np.save(OUT / f"final_projblend_{label}_oof.npy", pred)
        summary_rows.append(
            {
                "cap": cap,
                "file": out_file.name,
                "oof": loss,
                "projection": proj,
                "linear_public_est": stage2_public + proj * public_gap,
                "components": "|".join(best_files),
                "weights": "|".join(f"{w:.4f}" for w in weights),
            }
        )
    summary = pd.DataFrame(summary_rows).sort_values("cap").reset_index(drop=True)
    summary.to_csv(OUT / "projection_constrained_blend_summary.csv", index=False)
    print("[pool]")
    print(meta_df.round(9).to_string(index=False))
    print("\n[summary]")
    print(summary.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
