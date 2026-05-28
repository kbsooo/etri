from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402


def read_sub(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def move_from(base_logit: np.ndarray, file_name: str) -> np.ndarray:
    df = read_sub(OUT / file_name)
    return adv.logit(df[TARGETS].to_numpy(dtype=float)) - base_logit


def apply_target_weights(moves: dict[str, np.ndarray], recipe: dict[str, dict[str, float]], base_logit: np.ndarray) -> np.ndarray:
    move = np.zeros_like(base_logit)
    for source, weights in recipe.items():
        src = moves[source]
        for j, target in enumerate(TARGETS):
            move[:, j] += float(weights.get(target, weights.get("*", 0.0))) * src[:, j]
    return adv.clip(1.0 / (1.0 + np.exp(-(base_logit + move))))


def main() -> None:
    _train, _sub, _base, base_sub = adv.read_data()
    base_sub = base_sub.sort_values(KEY).reset_index(drop=True)
    base_logit = adv.logit(base_sub[TARGETS].to_numpy(dtype=float))
    sources = {
        "raw05": "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
        "raw075": "submission_raw_timeline_jepa_rescue_strict_scale0p75.csv",
        "segj035": "submission_subject_episode_graph_jepa_strict_scale0p35.csv",
        "segj05": "submission_subject_episode_graph_jepa_strict_scale0p5.csv",
        "segj075": "submission_subject_episode_graph_jepa_strict_scale0p75.csv",
        "segj1": "submission_subject_episode_graph_jepa_strict_scale1p0.csv",
        "neural0": "submission_jepa_neural_episode_rawstack_raw075_nb_top10_er_top10_rw1p25_nw1p25_ew1p0.csv",
        "bc0": "submission_block_canvas_multifeature_k8_c0p02_noq2_scale0p75.csv",
        "tegeom": "submission_transductive_episode_count_jepa_geometry_label_ctx_ridge10_core_q_s23_st0p5_sc0p35.csv",
    }
    moves = {name: move_from(base_logit, file_name) for name, file_name in sources.items() if (OUT / file_name).exists()}
    recipes: dict[str, dict[str, dict[str, float]]] = {
        "tw_raw1_qsegj_light_s23_mid": {
            "raw05": {"*": 1.0},
            "segj05": {"Q1": 0.15, "Q2": 0.10, "Q3": 0.15, "S1": 0.15, "S2": 0.25, "S3": 0.25, "S4": 0.15},
        },
        "tw_raw075_qsegj_mid_s23_deep": {
            "raw075": {"*": 0.75},
            "segj075": {"Q1": 0.20, "Q2": 0.10, "Q3": 0.20, "S1": 0.25, "S2": 0.45, "S3": 0.45, "S4": 0.20},
        },
        "tw_segj_noq2_stage": {
            "segj075": {"Q1": 0.35, "Q2": 0.0, "Q3": 0.35, "S1": 0.50, "S2": 0.75, "S3": 0.75, "S4": 0.45},
        },
        "tw_raw_neural_s23": {
            "raw05": {"*": 1.0},
            "neural0": {"*": 0.10},
            "segj05": {"Q1": 0.10, "Q2": 0.05, "Q3": 0.10, "S1": 0.15, "S2": 0.35, "S3": 0.35, "S4": 0.15},
        },
        "tw_bc_stage_q_light": {
            "bc0": {"S1": 0.35, "S2": 0.50, "S3": 0.50, "S4": 0.35},
            "segj035": {"Q1": 0.15, "Q2": 0.05, "Q3": 0.15},
        },
        "tw_tecount_q_raw_stage": {
            "raw05": {"*": 0.75},
            "tegeom": {"Q1": 0.50, "Q2": 0.50, "Q3": 0.50, "S2": 0.30, "S3": 0.30},
            "segj035": {"S1": 0.20, "S2": 0.25, "S3": 0.25, "S4": 0.20},
        },
        "tw_aggressive_segj_s": {
            "segj1": {"Q1": 0.35, "Q2": 0.20, "Q3": 0.35, "S1": 0.80, "S2": 1.00, "S3": 1.00, "S4": 0.70},
        },
        "tw_public_safe_blend_seed": {
            "raw05": {"*": 1.0},
            "segj035": {"*": 0.15},
            "neural0": {"*": 0.10},
            "tegeom": {"Q1": 0.20, "Q2": 0.20, "Q3": 0.20},
        },
    }
    rows = []
    for i, (name, recipe) in enumerate(recipes.items()):
        missing = [src for src in recipe if src not in moves]
        if missing:
            continue
        arr = apply_target_weights(moves, recipe, base_logit)
        file_name = f"submission_jepa_targetwise_public_blend_{i:02d}_{name}.csv"
        out = base_sub.copy()
        out[TARGETS] = arr
        out.to_csv(OUT / file_name, index=False)
        move = adv.logit(arr) - base_logit
        rows.append(
            {
                "candidate": file_name,
                "recipe": str(recipe),
                "move_norm": float(np.linalg.norm(move)),
                **adv.public_axis_for(file_name),
            }
        )
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "jepa_targetwise_public_blend_summary.csv", index=False)
    report = [
        "# JEPA Targetwise Public Blends",
        "",
        "Hand-authored targetwise logit blends: Q moves are generally shallow, S2/S3 moves are deeper because the JEPA block-rate signal was strongest there.",
        "",
        summary.to_csv(index=False),
    ]
    (OUT / "jepa_targetwise_public_blend_report.md").write_text("\n".join(report), encoding="utf-8")
    print(summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
