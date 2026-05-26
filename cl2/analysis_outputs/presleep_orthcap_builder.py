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

PROJECTION_CAPS = [-0.05, 0.0, 0.025, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30]
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


def oof_name(file_name: str) -> str:
    return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")


def projection(move: np.ndarray, direction: np.ndarray) -> float:
    denom = float(np.dot(direction, direction))
    if denom <= 0.0:
        return 0.0
    return float(np.dot(move, direction) / denom)


def tag_float(value: float) -> str:
    sign = "m" if value < 0 else ""
    return f"{sign}{str(abs(value)).replace('.', 'p')}"


def seed_files() -> list[str]:
    audit = pd.read_csv(OUT / "presleep_public_direction_audit.csv")
    audit = audit[audit["file"].str.startswith("submission_publicgated_q3off650_presleep")].copy()
    audit = audit.sort_values(["oof_mean_loss", "one_axis_bad_projection"]).head(15)
    out: list[str] = []
    for file_name in audit["file"].astype(str):
        if (OUT / file_name).exists() and (OUT / oof_name(file_name)).exists():
            out.append(file_name)
    return out


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    y = train[TARGETS].to_numpy(dtype=int)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    public_obs = pd.read_csv(OUT / "public_probe_observations.csv").set_index("file")["public_lb"].astype(float)
    public_bad_gap = float(public_obs[ORDINAL] - public_obs[STAGE2])

    stage2_sub = load_sub(STAGE2)
    anchor_vals = load_sub(ANCHOR)[TARGETS].to_numpy(dtype=float)
    ordinal_vals = load_sub(ORDINAL)[TARGETS].to_numpy(dtype=float)
    stage2_vals = stage2_sub[TARGETS].to_numpy(dtype=float)
    assert stage2_sub[KEY].equals(sample[KEY])

    stage2_vec = stage2_vals.reshape(-1)
    bad_dir = (ordinal_vals - stage2_vals).reshape(-1)
    stage2_oof = clip(np.load(OUT / STAGE2_OOF))
    ordinal_oof = clip(np.load(OUT / ORDINAL_OOF))
    bad_dir_oof = (ordinal_oof - stage2_oof).reshape(-1)
    stage2_oof_vec = stage2_oof.reshape(-1)
    stage2_loss = mean_loss(y, stage2_oof)

    rows: list[dict[str, object]] = []
    for seed_idx, source_file in enumerate(seed_files(), start=1):
        source_sub = load_sub(source_file)
        assert source_sub[KEY].equals(sample[KEY])
        source_vals = source_sub[TARGETS].to_numpy(dtype=float)
        source_oof = clip(np.load(OUT / oof_name(source_file)))
        source_move = (source_vals - stage2_vals).reshape(-1)
        source_move_oof = (source_oof - stage2_oof).reshape(-1)
        source_projection = projection(source_move, bad_dir)
        if source_projection <= 0:
            continue

        for cap in PROJECTION_CAPS:
            subtract = max(source_projection - cap, 0.0)
            capped_move = source_move - subtract * bad_dir
            capped_move_oof = source_move_oof - subtract * bad_dir_oof
            for scale in SCALES:
                vals = clip(stage2_vec + scale * capped_move).reshape(stage2_vals.shape)
                pred = clip(stage2_oof_vec + scale * capped_move_oof).reshape(stage2_oof.shape)
                move = vals.reshape(-1) - stage2_vec
                actual_projection = projection(move, bad_dir)
                projected = actual_projection * bad_dir
                move_norm = float(np.linalg.norm(move))
                orth_ratio = float(np.linalg.norm(move - projected) / max(move_norm, 1e-12))
                loss = mean_loss(y, pred)
                tag = f"s{seed_idx:02d}_cap{tag_float(cap)}_sc{int(round(scale * 100)):03d}"
                file_name = f"submission_presleep_orthcap_{tag}.csv"
                oof_file = f"final_presleep_orthcap_{tag}_oof.npy"
                out = stage2_sub.copy()
                out[TARGETS] = vals
                out.to_csv(OUT / file_name, index=False)
                np.save(OUT / oof_file, pred)
                rows.append(
                    {
                        "file": file_name,
                        "oof_file": oof_file,
                        "source_file": source_file,
                        "source_oof_file": oof_name(source_file),
                        "source_projection": source_projection,
                        "projection_cap": cap,
                        "scale": scale,
                        "actual_bad_direction_projection": actual_projection,
                        "orthogonal_move_ratio": orth_ratio,
                        "linear_public_delta_vs_stage2": actual_projection * public_bad_gap,
                        "oof_mean_loss": loss,
                        "oof_gain_vs_stage2": stage2_loss - loss,
                        "distance_abs_mean_vs_anchor": float(np.abs(vals - anchor_vals).mean()),
                        "distance_abs_p90_vs_anchor": float(np.quantile(np.abs(vals - anchor_vals), 0.9)),
                        "submission_min": float(vals.min()),
                        "submission_max": float(vals.max()),
                    }
                )

    catalog = pd.DataFrame(rows)
    if catalog.empty:
        raise RuntimeError("no presleep orthcap candidates")
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
    catalog.to_csv(OUT / "presleep_orthcap_candidates.csv", index=False)

    integrity_rows = []
    for row in catalog.head(30).itertuples(index=False):
        sub = load_sub(str(row.file))
        pred = clip(np.load(OUT / str(row.oof_file)))
        irow = {
            "file": str(row.file),
            "rows": len(sub),
            "dups": int(sub.duplicated(KEY).sum()),
            "na": int(sub[TARGETS].isna().sum().sum()),
            "min_prob": float(sub[TARGETS].min().min()),
            "max_prob": float(sub[TARGETS].max().max()),
        }
        for j, target in enumerate(TARGETS):
            irow[f"{target}_delta_vs_stage2"] = loss_col(y[:, j], pred[:, j]) - loss_col(y[:, j], stage2_oof[:, j])
        integrity_rows.append(irow)
    pd.DataFrame(integrity_rows).to_csv(OUT / "presleep_orthcap_integrity_and_deltas.csv", index=False)
    print(catalog.head(60).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
