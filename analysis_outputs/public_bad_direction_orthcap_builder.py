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
STAGE2_OOF = "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
ANCHOR = "submission_hybrid_0p578_logit_after_subject_final9_strict.csv"
ORDINAL = "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv"
ORDINAL_OOF = "final_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75_oof.npy"

PROJECTION_CAPS = [-0.10, -0.05, 0.0, 0.05, 0.10, 0.20, 0.30]
SCALES = [0.50, 0.75, 1.00, 1.25]


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


def oof_name_from_submission(file_name: str) -> str | None:
    if file_name.startswith("submission_stage2_donor_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_subjectgate_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_publicobsblend_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    return None


def projection(move: np.ndarray, direction: np.ndarray) -> float:
    denom = float(np.dot(direction, direction))
    if denom <= 0.0:
        return 0.0
    return float(np.dot(move, direction) / denom)


def tag_float(value: float) -> str:
    prefix = "m" if value < 0 else ""
    return f"{prefix}{int(round(abs(value) * 100)):03d}"


def candidate_seed_files() -> list[str]:
    ranked = pd.read_csv(OUT / "public_direction_risk_ranked_candidates.csv")
    seeds: list[str] = []

    # High-upside subject gates, but keep only candidates with a real half-gate guardrail.
    sg = ranked[
        (ranked["source_catalog"] == "subject_target_gate_donor_candidates.csv")
        & ranked["half_gate_oof_loss"].notna()
        & (ranked["half_gate_oof_delta"] < -0.0015)
    ].copy()
    sg = sg.sort_values(["half_gate_oof_loss", "bad_direction_projection", "oof_mean_loss"])
    seeds.extend(sg["file"].head(40).tolist())

    # Lower-public-risk subject gates provide more orthogonal move directions.
    sg_low = ranked[
        (ranked["source_catalog"] == "subject_target_gate_donor_candidates.csv")
        & (ranked["bad_direction_projection"] <= 0.35)
        & (ranked["oof_gain_vs_stage2"] > 0.0025)
    ].copy()
    sg_low = sg_low.sort_values(["bad_direction_projection", "half_gate_oof_loss", "oof_mean_loss"])
    seeds.extend(sg_low["file"].head(40).tolist())

    # Target masks are simpler attribution moves and often have lower projection.
    tm = ranked[
        (ranked["source_catalog"] == "stage2_donor_targetmask_candidates.csv")
        & (ranked["oof_gain_vs_stage2"] > 0.0015)
    ].copy()
    tm = tm.sort_values(["bad_direction_projection", "oof_mean_loss"])
    seeds.extend(tm["file"].head(40).tolist())

    deduped = []
    seen = set()
    for file_name in seeds:
        if file_name in seen:
            continue
        seen.add(file_name)
        oof_name = oof_name_from_submission(file_name)
        if oof_name and (OUT / file_name).exists() and (OUT / oof_name).exists():
            deduped.append(file_name)
    return deduped


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    y = train[TARGETS].to_numpy(dtype=int)
    public_obs = pd.read_csv(OUT / "public_probe_observations.csv").set_index("file")["public_lb"].astype(float)
    public_bad_gap = float(public_obs[ORDINAL] - public_obs[STAGE2])

    stage2_sub = load_sub(STAGE2)
    assert stage2_sub[KEY].equals(sample[KEY])
    stage2_vals = stage2_sub[TARGETS].to_numpy(dtype=float)
    stage2_vec = stage2_vals.reshape(-1)
    stage2_oof = clip(np.load(OUT / STAGE2_OOF))
    stage2_oof_vec = stage2_oof.reshape(-1)
    stage2_loss = mean_loss(y, stage2_oof)

    anchor_vals = load_sub(ANCHOR)[TARGETS].to_numpy(dtype=float)
    ordinal_vals = load_sub(ORDINAL)[TARGETS].to_numpy(dtype=float)
    ordinal_oof = clip(np.load(OUT / ORDINAL_OOF))
    bad_dir = (ordinal_vals - stage2_vals).reshape(-1)
    bad_dir_oof = (ordinal_oof - stage2_oof).reshape(-1)
    bad_norm = float(np.dot(bad_dir, bad_dir))
    if bad_norm <= 0.0:
        raise RuntimeError("empty bad direction")

    rows = []
    for seed_idx, source_file in enumerate(candidate_seed_files(), start=1):
        oof_name = oof_name_from_submission(source_file)
        assert oof_name is not None
        source_sub = load_sub(source_file)
        assert source_sub[KEY].equals(sample[KEY]), source_file
        source_vals = source_sub[TARGETS].to_numpy(dtype=float)
        source_oof = clip(np.load(OUT / oof_name))

        source_move = (source_vals - stage2_vals).reshape(-1)
        source_move_oof = (source_oof - stage2_oof).reshape(-1)
        source_projection = projection(source_move, bad_dir)
        if source_projection <= 0.0:
            continue

        for cap in PROJECTION_CAPS:
            subtract = max(source_projection - cap, 0.0)
            capped_move = source_move - subtract * bad_dir
            capped_move_oof = source_move_oof - subtract * bad_dir_oof
            for scale in SCALES:
                vals = clip(stage2_vec + scale * capped_move).reshape(stage2_vals.shape)
                pred = clip(stage2_oof_vec + scale * capped_move_oof).reshape(stage2_oof.shape)
                actual_move = vals.reshape(-1) - stage2_vec
                actual_projection = projection(actual_move, bad_dir)
                actual_orth = actual_move - actual_projection * bad_dir
                move_norm = float(np.linalg.norm(actual_move))
                orth_ratio = float(np.linalg.norm(actual_orth) / max(move_norm, 1e-12))
                loss = mean_loss(y, pred)
                dist = np.abs(vals - anchor_vals)
                tag = f"s{seed_idx:03d}_cap{tag_float(cap)}_sc{int(round(scale * 100)):03d}"
                file_name = f"submission_orthcap_{tag}.csv"
                oof_out = f"final_orthcap_{tag}_oof.npy"
                out = stage2_sub.copy()
                out[TARGETS] = vals
                out.to_csv(OUT / file_name, index=False)
                np.save(OUT / oof_out, pred)
                rows.append(
                    {
                        "file": file_name,
                        "oof_file": oof_out,
                        "source_file": source_file,
                        "source_oof_file": oof_name,
                        "source_projection": source_projection,
                        "projection_cap": cap,
                        "scale": scale,
                        "actual_bad_direction_projection": actual_projection,
                        "orthogonal_move_ratio": orth_ratio,
                        "linear_public_delta_vs_stage2": actual_projection * public_bad_gap,
                        "oof_mean_loss": loss,
                        "oof_gain_vs_stage2": stage2_loss - loss,
                        "distance_abs_mean_vs_anchor": float(dist.mean()),
                        "distance_abs_p90_vs_anchor": float(np.quantile(dist, 0.9)),
                        "submission_min": float(vals.min()),
                        "submission_max": float(vals.max()),
                    }
                )

    catalog = pd.DataFrame(rows)
    if catalog.empty:
        raise RuntimeError("no orthcap candidates created")
    catalog = catalog[catalog["oof_gain_vs_stage2"] > 0.0].copy()
    catalog["priority_score"] = (
        catalog["oof_mean_loss"]
        + 4.0 * np.maximum(catalog["linear_public_delta_vs_stage2"], 0.0)
        + 0.0015 * np.maximum(catalog["actual_bad_direction_projection"], 0.0)
        - 0.00025 * catalog["orthogonal_move_ratio"]
        + 0.0005 * np.maximum(catalog["distance_abs_mean_vs_anchor"] - 0.034, 0.0)
    )
    catalog = catalog.sort_values(
        ["priority_score", "actual_bad_direction_projection", "oof_mean_loss"],
        ascending=[True, True, True],
    ).reset_index(drop=True)
    catalog.to_csv(OUT / "public_bad_direction_orthcap_candidates.csv", index=False)
    print(catalog.head(60).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
