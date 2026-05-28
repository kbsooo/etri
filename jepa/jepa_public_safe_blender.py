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


def flat_cos(a: np.ndarray, b: np.ndarray) -> float:
    aa = a.reshape(-1)
    bb = b.reshape(-1)
    return float(np.dot(aa, bb) / max(float(np.linalg.norm(aa) * np.linalg.norm(bb)), 1e-12))


def projection_ratio(move: np.ndarray, axis: np.ndarray) -> float:
    aa = axis.reshape(-1)
    mm = move.reshape(-1)
    return float(np.dot(mm, aa) / max(float(np.dot(aa, aa)), 1e-12))


def source_pool() -> list[tuple[str, str]]:
    pool: list[tuple[str, str]] = [
        ("raw_rescue_05", "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"),
        ("raw_rescue_075", "submission_raw_timeline_jepa_rescue_strict_scale0p75.csv"),
        ("segj_035", "submission_subject_episode_graph_jepa_strict_scale0p35.csv"),
        ("segj_05", "submission_subject_episode_graph_jepa_strict_scale0p5.csv"),
        ("segj_075", "submission_subject_episode_graph_jepa_strict_scale0p75.csv"),
        ("tecount_geom", "submission_transductive_episode_count_jepa_geometry_label_ctx_ridge10_core_q_s23_st0p5_sc0p35.csv"),
    ]
    for summary_path, label, n in [
        (OUT / "block_canvas_multifeature_candidate_summary.csv", "bc", 4),
        (OUT / "jepa_neural_episode_rawstack_summary.csv", "neural", 6),
        (OUT / "transductive_episode_count_jepa_candidate_summary.csv", "tecount", 4),
    ]:
        if not summary_path.exists():
            continue
        df = pd.read_csv(summary_path)
        if "candidate" not in df:
            continue
        sort_cols = ["oof_delta_vs_stage2"] if "oof_delta_vs_stage2" in df else []
        if "jepa_bad_ratio" in df:
            df = df.sort_values(["jepa_bad_ratio"] + sort_cols)
        elif sort_cols:
            df = df.sort_values(sort_cols)
        for i, cand in enumerate(df["candidate"].dropna().astype(str).head(n)):
            if (OUT / cand).exists():
                pool.append((f"{label}_{i}", cand))
    seen = set()
    unique = []
    for label, cand in pool:
        if cand in seen or not (OUT / cand).exists():
            continue
        seen.add(cand)
        unique.append((label, cand))
    return unique


def build_axes(base: pd.DataFrame) -> dict[str, np.ndarray]:
    base_logit = adv.logit(base[TARGETS].to_numpy(dtype=float))
    axes: dict[str, np.ndarray] = {}
    known = {
        "raw_good": "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
        "segj": "submission_subject_episode_graph_jepa_strict_scale0p75.csv",
        "bad_jepa_1": "submission_jepa_latent_residual_probe.csv",
        "bad_jepa_2": "submission_jepa_latent_q2_w0p45.csv",
    }
    for name, file_name in known.items():
        path = OUT / file_name
        if path.exists():
            axes[name] = adv.logit(read_sub(path)[TARGETS].to_numpy(dtype=float)) - base_logit
    try:
        anchor = read_sub(ANALYSIS / "submission_hybrid_0p578_logit_after_subject_final9_strict.csv")
        stage2 = base
        axes["stage2_good_axis"] = adv.logit(stage2[TARGETS].to_numpy(dtype=float)) - adv.logit(anchor[TARGETS].to_numpy(dtype=float))
        ordinal = read_sub(ANALYSIS / "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv")
        axes["ordinal_bad_axis"] = adv.logit(ordinal[TARGETS].to_numpy(dtype=float)) - base_logit
    except Exception:
        pass
    if "bad_jepa_1" in axes and "bad_jepa_2" in axes:
        axes["bad_jepa_mean"] = 0.65 * axes["bad_jepa_1"] + 0.35 * axes["bad_jepa_2"]
    return axes


def main() -> None:
    _train, sub, _base, base_sub = adv.read_data()
    base_sub = base_sub.sort_values(KEY).reset_index(drop=True)
    base_logit = adv.logit(base_sub[TARGETS].to_numpy(dtype=float))
    axes = build_axes(base_sub)
    pool = source_pool()
    source_moves = {}
    meta_rows = []
    for label, cand in pool:
        df = read_sub(OUT / cand)
        assert df[SUB_KEY].astype(str).equals(base_sub[SUB_KEY].astype(str))
        move = adv.logit(df[TARGETS].to_numpy(dtype=float)) - base_logit
        source_moves[label] = move
        meta_rows.append(
            {
                "label": label,
                "candidate": cand,
                "move_norm": float(np.linalg.norm(move)),
                "raw_good_cos": flat_cos(move, axes["raw_good"]) if "raw_good" in axes else np.nan,
                "segj_cos": flat_cos(move, axes["segj"]) if "segj" in axes else np.nan,
                "bad_jepa_ratio": projection_ratio(move, axes["bad_jepa_mean"]) if "bad_jepa_mean" in axes else np.nan,
                "ordinal_bad_ratio": projection_ratio(move, axes["ordinal_bad_axis"]) if "ordinal_bad_axis" in axes else np.nan,
            }
        )
    pd.DataFrame(meta_rows).to_csv(OUT / "jepa_public_safe_blender_sources.csv", index=False)

    raw_labels = [k for k in source_moves if k.startswith("raw_rescue")]
    segj_labels = [k for k in source_moves if k.startswith("segj")]
    bc_labels = [k for k in source_moves if k.startswith("bc")]
    neural_labels = [k for k in source_moves if k.startswith("neural")]
    tecount_labels = [k for k in source_moves if k.startswith("tecount")]

    combos = []
    for raw in raw_labels[:2]:
        for segj in segj_labels[:3]:
            for bc in ([None] + bc_labels[:3]):
                for neural in ([None] + neural_labels[:4]):
                    for tec in ([None] + tecount_labels[:3]):
                        for raw_w in [0.0, 0.50, 0.75, 1.00]:
                            for segj_w in [0.10, 0.20, 0.35, 0.50]:
                                for bc_w in ([0.0] if bc is None else [0.10, 0.20]):
                                    for neural_w in ([0.0] if neural is None else [0.10, 0.20, 0.35]):
                                        for tec_w in ([0.0] if tec is None else [0.20, 0.35, 0.50]):
                                            move = raw_w * source_moves[raw] + segj_w * source_moves[segj]
                                            parts = [f"{raw}:{raw_w:g}", f"{segj}:{segj_w:g}"]
                                            if bc is not None:
                                                move = move + bc_w * source_moves[bc]
                                                parts.append(f"{bc}:{bc_w:g}")
                                            if neural is not None:
                                                move = move + neural_w * source_moves[neural]
                                                parts.append(f"{neural}:{neural_w:g}")
                                            if tec is not None:
                                                move = move + tec_w * source_moves[tec]
                                                parts.append(f"{tec}:{tec_w:g}")
                                            bad_jepa = projection_ratio(move, axes["bad_jepa_mean"]) if "bad_jepa_mean" in axes else 0.0
                                            ordinal_bad = projection_ratio(move, axes["ordinal_bad_axis"]) if "ordinal_bad_axis" in axes else 0.0
                                            raw_cos = flat_cos(move, axes["raw_good"]) if "raw_good" in axes else 0.0
                                            segj_cos = flat_cos(move, axes["segj"]) if "segj" in axes else 0.0
                                            norm = float(np.linalg.norm(move))
                                            if norm <= 0:
                                                continue
                                            risk = max(0.0, bad_jepa) + 0.35 * max(0.0, ordinal_bad) + 0.01 * max(0.0, norm - 8.0)
                                            score = risk - 0.10 * raw_cos - 0.03 * segj_cos
                                            combos.append(
                                                {
                                                    "recipe": "|".join(parts),
                                                    "score": score,
                                                    "move_norm": norm,
                                                    "bad_jepa_ratio": bad_jepa,
                                                    "ordinal_bad_ratio": ordinal_bad,
                                                    "raw_good_cos": raw_cos,
                                                    "segj_cos": segj_cos,
                                                    "raw": raw,
                                                    "segj": segj,
                                                    "bc": bc or "",
                                                    "neural": neural or "",
                                                    "tecount": tec or "",
                                                    "raw_w": raw_w,
                                                    "segj_w": segj_w,
                                                    "bc_w": bc_w,
                                                    "neural_w": neural_w,
                                                    "tecount_w": tec_w,
                                                }
                                            )
    summary = pd.DataFrame(combos)
    summary = summary.sort_values(["score", "bad_jepa_ratio", "move_norm"]).reset_index(drop=True)
    summary.to_csv(OUT / "jepa_public_safe_blender_grid.csv", index=False)

    emitted = []
    # Mix conservative, raw-aligned and aggressive local candidates.
    selected = pd.concat(
        [
            summary.head(18),
            summary.sort_values(["bad_jepa_ratio", "score"]).head(10),
            summary[summary["move_norm"].between(3.0, 7.0)].head(12),
        ],
        ignore_index=True,
    ).drop_duplicates("recipe").head(40)
    for i, row in enumerate(selected.itertuples(index=False)):
        move = np.zeros_like(base_logit)
        for item in str(row.recipe).split("|"):
            label, weight = item.split(":")
            move += float(weight) * source_moves[label]
        arr = adv.clip(1.0 / (1.0 + np.exp(-(base_logit + move))))
        file_name = f"submission_jepa_public_safe_blend_{i:02d}.csv"
        out = base_sub.copy()
        out[TARGETS] = arr
        out.to_csv(OUT / file_name, index=False)
        emitted.append(
            {
                "candidate": file_name,
                "recipe": row.recipe,
                "score": float(row.score),
                "move_norm": float(np.linalg.norm(move)),
                "bad_jepa_ratio": projection_ratio(move, axes["bad_jepa_mean"]) if "bad_jepa_mean" in axes else np.nan,
                "ordinal_bad_ratio": projection_ratio(move, axes["ordinal_bad_axis"]) if "ordinal_bad_axis" in axes else np.nan,
                "raw_good_cos": flat_cos(move, axes["raw_good"]) if "raw_good" in axes else np.nan,
                "segj_cos": flat_cos(move, axes["segj"]) if "segj" in axes else np.nan,
                **adv.public_axis_for(file_name),
            }
        )
    emitted_df = pd.DataFrame(emitted)
    emitted_df.to_csv(OUT / "jepa_public_safe_blender_candidate_summary.csv", index=False)
    report = [
        "# JEPA Public-Safe Blender",
        "",
        "Combines JEPA-family submission logit moves around the stage2 base while penalizing directions aligned with known harmful JEPA public-feedback axes.",
        "",
        "## Sources",
        "",
        pd.DataFrame(meta_rows).to_csv(index=False),
        "",
        "## Emitted Candidates",
        "",
        emitted_df.to_csv(index=False),
    ]
    (OUT / "jepa_public_safe_blender_report.md").write_text("\n".join(report), encoding="utf-8")
    print(emitted_df.head(40).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
