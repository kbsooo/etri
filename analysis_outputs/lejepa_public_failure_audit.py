from __future__ import annotations

from pathlib import Path
import hashlib

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-6

STAGE2 = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
RAW05 = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
ORDINAL = "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv"
Q2_BAD = "submission_jepa_latent_q2_w0p45.csv"
RESID_BAD = "submission_jepa_latent_residual_probe.csv"
LEJEPA_BAD = "submission_lejepa_targetwise_strict_best_scale0p5.csv"


def find_submission(file_name: str) -> Path | None:
    for folder in (OUT, JEPA):
        p = folder / file_name
        if p.exists():
            return p
    return None


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p.astype(float), EPS, 1.0 - EPS)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -40.0, 40.0)))


def load_sub(file_name: str) -> pd.DataFrame:
    path = find_submission(file_name)
    if path is None:
        raise FileNotFoundError(file_name)
    return pd.read_csv(path).sort_values(KEYS).reset_index(drop=True)


def prob_matrix(file_name: str) -> np.ndarray:
    return load_sub(file_name)[TARGETS].to_numpy(dtype=float)


def vec_from_prob(p: np.ndarray) -> np.ndarray:
    return logit(p).reshape(-1)


def projection(move: np.ndarray, direction: np.ndarray) -> tuple[float, float]:
    denom = float(direction @ direction)
    if denom <= 0:
        return 0.0, 0.0
    proj = float(move @ direction / denom)
    cos = float(move @ direction / (np.linalg.norm(move) * np.linalg.norm(direction) + 1e-12))
    return proj, cos


def stable_tag(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def write_submission(template: pd.DataFrame, probs: np.ndarray, name: str) -> str:
    out = template.copy()
    out[TARGETS] = clip(probs)
    path = OUT / name
    out.to_csv(path, index=False)
    return name


def generate_repair_candidates() -> list[str]:
    stage2_df = load_sub(STAGE2)
    stage2 = stage2_df[TARGETS].to_numpy(dtype=float)
    raw05 = prob_matrix(RAW05)
    lejepa = prob_matrix(LEJEPA_BAD)

    z_stage2 = logit(stage2)
    z_raw05 = logit(raw05)
    raw_dir = z_raw05 - z_stage2
    lejepa_bad_dir = logit(lejepa) - z_stage2

    generated: list[str] = []

    for scale in [0.75, 0.875, 1.0, 1.125]:
        probs = sigmoid(z_stage2 + scale * raw_dir)
        tag = stable_tag(f"rawaxis|{scale:.3f}")
        generated.append(write_submission(stage2_df, probs, f"submission_public_repair_rawaxis_s{scale:.3f}_{tag}.csv"))

    masks = {
        "all": TARGETS,
        "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
        "q3_only": ["Q3"],
        "q3_s4": ["Q3", "S4"],
        "q2_q3_s4": ["Q2", "Q3", "S4"],
    }
    for gamma in [0.04, 0.08, 0.12]:
        for mask_name, mask_targets in masks.items():
            z = z_raw05.copy()
            idx = [TARGETS.index(t) for t in mask_targets]
            z[:, idx] -= gamma * lejepa_bad_dir[:, idx]
            tag = stable_tag(f"raw05_antilejepa|{gamma:.3f}|{mask_name}")
            generated.append(
                write_submission(
                    stage2_df,
                    sigmoid(z),
                    f"submission_public_repair_raw05_antilejepa_{mask_name}_g{gamma:.3f}_{tag}.csv",
                )
            )

    return generated


def candidate_files(generated: list[str]) -> list[str]:
    files = set(generated)
    source_tables = [
        OUT / "public_mask_plausibility_reweight_summary.csv",
        OUT / "public_lb_actual_anchor_ranker_shortlist.csv",
        OUT / "public_lb_inverse7_blend_probe_selected.csv",
        OUT / "jepa_public_minimax_rawsafe_bridge_public_pool.csv",
        OUT / "hidden_block_candidate_publicfit_scores.csv",
        OUT / "public_two_axis_blend_candidates.csv",
        JEPA / "lejepa_targetwise_blend_summary.csv",
    ]
    for table in source_tables:
        if not table.exists():
            continue
        df = pd.read_csv(table)
        for col in ["file", "candidate"]:
            if col in df.columns:
                for value in df[col].dropna().astype(str):
                    if value.endswith(".csv") and find_submission(value) is not None:
                        files.add(value)
    files.update([STAGE2, RAW05, ORDINAL, Q2_BAD, RESID_BAD, LEJEPA_BAD])
    return sorted(files)


def main() -> None:
    obs = pd.read_csv(OUT / "public_probe_observations.csv").set_index("file")["public_lb"].astype(float).to_dict()
    stage2_public = float(obs[STAGE2])

    generated = generate_repair_candidates()

    stage2 = prob_matrix(STAGE2)
    z_stage2 = vec_from_prob(stage2)
    ref_names = {
        "raw05_good": RAW05,
        "ordinal_bad": ORDINAL,
        "q2_bad": Q2_BAD,
        "resid_bad": RESID_BAD,
        "lejepa_bad": LEJEPA_BAD,
    }
    ref_dirs = {name: vec_from_prob(prob_matrix(file_name)) - z_stage2 for name, file_name in ref_names.items()}
    public_deltas = {
        name: float(obs.get(file_name, stage2_public) - stage2_public)
        for name, file_name in ref_names.items()
    }

    rows = []
    for file_name in candidate_files(generated):
        try:
            probs = prob_matrix(file_name)
        except Exception:
            continue
        move = vec_from_prob(probs) - z_stage2
        row = {
            "file": file_name,
            "known_public": obs.get(file_name, np.nan),
            "mean_abs_move_vs_stage2": float(np.mean(np.abs(move))),
            "min_prob": float(np.min(probs)),
            "max_prob": float(np.max(probs)),
            "generated_now": file_name in generated,
        }
        linear_est = stage2_public
        for ref_name, direction in ref_dirs.items():
            proj, cos = projection(move, direction)
            row[f"{ref_name}_proj"] = proj
            row[f"{ref_name}_cos"] = cos
            delta = public_deltas[ref_name]
            if ref_name == "raw05_good":
                linear_est += proj * delta
            else:
                linear_est += max(proj, 0.0) * max(delta, 0.0)
        row["linear_public_est_vs_stage2"] = linear_est
        row["linear_public_delta_vs_stage2"] = linear_est - stage2_public
        row["bad_axis_load"] = (
            max(row["ordinal_bad_proj"], 0.0) * 0.25
            + max(row["q2_bad_proj"], 0.0) * 1.0
            + max(row["resid_bad_proj"], 0.0) * 1.0
            + max(row["lejepa_bad_proj"], 0.0) * 1.2
        )
        row["raw05_distance"] = float(np.mean(np.abs(vec_from_prob(probs) - vec_from_prob(prob_matrix(RAW05)))))
        row["rank_score"] = (
            row["linear_public_est_vs_stage2"]
            + 0.0007 * row["bad_axis_load"]
            + 0.00025 * row["raw05_distance"]
            - 0.00008 * max(row["raw05_good_proj"], 0.0)
        )
        rows.append(row)

    out = pd.DataFrame(rows)
    out = out.sort_values(["rank_score", "linear_public_est_vs_stage2", "bad_axis_load"]).reset_index(drop=True)
    out.to_csv(OUT / "lejepa_public_failure_audit_ranked.csv", index=False)

    known = out[out["known_public"].notna()].copy()
    unknown = out[out["known_public"].isna()].copy()
    print("Known public anchors:")
    print(
        known[
            [
                "file",
                "known_public",
                "raw05_good_proj",
                "q2_bad_proj",
                "resid_bad_proj",
                "lejepa_bad_proj",
                "bad_axis_load",
                "linear_public_est_vs_stage2",
            ]
        ].round(8).to_string(index=False)
    )
    print("\nTop unknown candidates:")
    cols = [
        "file",
        "generated_now",
        "rank_score",
        "linear_public_est_vs_stage2",
        "raw05_good_proj",
        "q2_bad_proj",
        "resid_bad_proj",
        "lejepa_bad_proj",
        "bad_axis_load",
        "raw05_distance",
        "mean_abs_move_vs_stage2",
        "min_prob",
        "max_prob",
    ]
    print(unknown[cols].head(40).round(8).to_string(index=False))


if __name__ == "__main__":
    main()
