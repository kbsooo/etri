from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import jepa_axis_stack_candidates as stack  # noqa: E402


def safe_label(x: float) -> str:
    return str(x).replace("-", "m").replace(".", "p")


def source_from_ops(file_name: str, train_feat: pd.DataFrame, sub_feat: pd.DataFrame, base: np.ndarray, base_sub: pd.DataFrame) -> dict[str, np.ndarray | str]:
    oof, _sub_fit = stack.candidate_from_ops(file_name, train_feat, sub_feat, base, base_sub)
    disk_sub = stack.read_submission(file_name, base_sub)
    base_sub_arr = base_sub[TARGETS].to_numpy(dtype=float)
    return {
        "file": file_name,
        "oof": oof,
        "sub": disk_sub,
        "oof_move": adv.logit(oof) - adv.logit(base),
        "sub_move": adv.logit(disk_sub) - adv.logit(base_sub_arr),
    }


def blend(base: np.ndarray, base_sub: pd.DataFrame, moves: list[tuple[np.ndarray, np.ndarray, float]]) -> tuple[np.ndarray, np.ndarray]:
    base_logit = adv.logit(base)
    sub_base = base_sub[TARGETS].to_numpy(dtype=float)
    sub_logit = adv.logit(sub_base)
    oof_delta = np.zeros_like(base_logit)
    sub_delta = np.zeros_like(sub_logit)
    for oof_move, sub_move, weight in moves:
        oof_delta += float(weight) * oof_move
        sub_delta += float(weight) * sub_move
    return (
        adv.clip(1.0 / (1.0 + np.exp(-(base_logit + oof_delta)))),
        adv.clip(1.0 / (1.0 + np.exp(-(sub_logit + sub_delta)))),
    )


def emit(name: str, base_sub: pd.DataFrame, pred: np.ndarray) -> None:
    out = base_sub.copy()
    out[TARGETS] = adv.clip(pred)
    out.to_csv(OUT / name, index=False)


def main() -> None:
    train, _sub, base, base_sub = adv.read_data()
    y = train[TARGETS].to_numpy(dtype=int)
    base_loss = adv.mean_loss(y, base)
    sub_base = base_sub[TARGETS].to_numpy(dtype=float)

    raw_train = pd.read_parquet(OUT / "raw_timeline_jepa_rescue_train_features.parquet")
    raw_sub = pd.read_parquet(OUT / "raw_timeline_jepa_rescue_submission_features.parquet")
    neural_train = pd.read_parquet(OUT / "neural_block_canvas_jepa_mps_train_features.parquet")
    neural_sub = pd.read_parquet(OUT / "neural_block_canvas_jepa_mps_submission_features.parquet")
    episode_train = pd.read_parquet(OUT / "episode_retrieval_jepa_train_features.parquet")
    episode_sub = pd.read_parquet(OUT / "episode_retrieval_jepa_submission_features.parquet")

    raw_sources = {
        "raw05": source_from_ops("submission_raw_timeline_jepa_rescue_strict_scale0p5.csv", raw_train, raw_sub, base, base_sub),
        "raw075": source_from_ops("submission_raw_timeline_jepa_rescue_strict_scale0p75.csv", raw_train, raw_sub, base, base_sub),
    }
    neural_sources = {
        "nb_top10": source_from_ops("submission_neural_block_canvas_jepa_mps_top_probe_scale1p0.csv", neural_train, neural_sub, base, base_sub),
        "nb_strict10": source_from_ops("submission_neural_block_canvas_jepa_mps_strict_scale1p0.csv", neural_train, neural_sub, base, base_sub),
        "nb_top075": source_from_ops("submission_neural_block_canvas_jepa_mps_top_probe_scale0p75.csv", neural_train, neural_sub, base, base_sub),
    }
    episode_sources = {
        "none": None,
        "er_strict10": source_from_ops("submission_episode_retrieval_jepa_strict_scale1p0.csv", episode_train, episode_sub, base, base_sub),
        "er_top10": source_from_ops("submission_episode_retrieval_jepa_top_probe_scale1p0.csv", episode_train, episode_sub, base, base_sub),
    }

    rows = []
    for raw_name, raw_src in raw_sources.items():
        for nb_name, nb_src in neural_sources.items():
            for er_name, er_src in episode_sources.items():
                for raw_w in [0.5, 0.75, 1.0, 1.25]:
                    for nb_w in [0.5, 0.75, 1.0, 1.25]:
                        er_grid = [0.0] if er_src is None else [0.35, 0.5, 0.75, 1.0]
                        for er_w in er_grid:
                            moves = [
                                (raw_src["oof_move"], raw_src["sub_move"], raw_w),  # type: ignore[list-item]
                                (nb_src["oof_move"], nb_src["sub_move"], nb_w),  # type: ignore[list-item]
                            ]
                            if er_src is not None:
                                moves.append((er_src["oof_move"], er_src["sub_move"], er_w))  # type: ignore[arg-type]
                            oof, sub = blend(base, base_sub, moves)
                            stats = stack.axis_stats(adv.logit(sub) - adv.logit(sub_base), base_sub)
                            name = (
                                "submission_jepa_neural_episode_rawstack_"
                                f"{raw_name}_{nb_name}_{er_name}_"
                                f"rw{safe_label(raw_w)}_nw{safe_label(nb_w)}_ew{safe_label(er_w)}.csv"
                            )
                            emit(name, base_sub, sub)
                            rows.append(
                                {
                                    "candidate": name,
                                    "kind": "global",
                                    "raw": raw_name,
                                    "neural": nb_name,
                                    "episode": er_name,
                                    "raw_weight": raw_w,
                                    "neural_weight": nb_w,
                                    "episode_weight": er_w,
                                    "oof_loss": adv.mean_loss(y, oof),
                                    "oof_delta_vs_stage2": adv.mean_loss(y, oof) - base_loss,
                                    **stats,
                                }
                            )

    # Conservative targetwise variant: choose per-target raw/neural weights and
    # let episode contribute only if it wins despite a penalty.
    base_logit = adv.logit(base)
    sub_logit = adv.logit(sub_base)
    for raw_name in ["raw05", "raw075"]:
        for nb_name in ["nb_top10", "nb_strict10"]:
            for er_name in ["none", "er_strict10"]:
                raw_src = raw_sources[raw_name]
                nb_src = neural_sources[nb_name]
                er_src = episode_sources[er_name]
                choices = []
                oof = base.copy()
                sub = sub_base.copy()
                for j, target in enumerate(TARGETS):
                    best = None
                    for raw_w in [0.0, 0.35, 0.5, 0.75, 1.0]:
                        for nb_w in [0.0, 0.35, 0.5, 0.75, 1.0]:
                            er_grid = [0.0] if er_src is None else [0.0, 0.25, 0.5, 0.75]
                            for er_w in er_grid:
                                delta = raw_w * raw_src["oof_move"][:, j] + nb_w * nb_src["oof_move"][:, j]  # type: ignore[index]
                                if er_src is not None:
                                    delta = delta + er_w * er_src["oof_move"][:, j]  # type: ignore[index]
                                pred = adv.clip(1.0 / (1.0 + np.exp(-(base_logit[:, j] + delta))))
                                loss = stack.broad.loss_col(y[:, j], pred)
                                key = loss + 0.00025 * (raw_w + nb_w + er_w)
                                if best is None or key < best[0]:
                                    best = (key, loss, raw_w, nb_w, er_w, pred)
                    assert best is not None
                    _key, loss, raw_w, nb_w, er_w, pred = best
                    oof[:, j] = pred
                    sub_delta = raw_w * raw_src["sub_move"][:, j] + nb_w * nb_src["sub_move"][:, j]  # type: ignore[index]
                    if er_src is not None:
                        sub_delta = sub_delta + er_w * er_src["sub_move"][:, j]  # type: ignore[index]
                    sub[:, j] = adv.clip(1.0 / (1.0 + np.exp(-(sub_logit[:, j] + sub_delta))))
                    choices.append({"target": target, "raw_weight": raw_w, "neural_weight": nb_w, "episode_weight": er_w, "target_loss": loss})
                stats = stack.axis_stats(adv.logit(sub) - adv.logit(sub_base), base_sub)
                name = f"submission_jepa_neural_episode_rawstack_targetwise_{raw_name}_{nb_name}_{er_name}.csv"
                emit(name, base_sub, sub)
                pd.DataFrame(choices).to_csv(OUT / name.replace("submission_", "").replace(".csv", "_weights.csv"), index=False)
                rows.append(
                    {
                        "candidate": name,
                        "kind": "targetwise",
                        "raw": raw_name,
                        "neural": nb_name,
                        "episode": er_name,
                        "raw_weight": np.nan,
                        "neural_weight": np.nan,
                        "episode_weight": np.nan,
                        "oof_loss": adv.mean_loss(y, oof),
                        "oof_delta_vs_stage2": adv.mean_loss(y, oof) - base_loss,
                        **stats,
                    }
                )

    summary = pd.DataFrame(rows)
    summary["public_safety_rank"] = (
        summary["oof_delta_vs_stage2"]
        + 0.006 * np.maximum(summary["jepa_bad_ratio"], 0.0)
        + 0.0015 * np.maximum(-summary["raw_good_ratio"], 0.0)
        - 0.0007 * np.minimum(summary["raw_good_ratio"], 1.2)
        - 0.0004 * np.maximum(-summary["jepa_bad_ratio"], 0.0)
    )
    summary = summary.sort_values(["public_safety_rank", "oof_delta_vs_stage2"]).reset_index(drop=True)
    summary.to_csv(OUT / "jepa_neural_episode_rawstack_summary.csv", index=False)
    report = [
        "# Neural + Episode + Raw JEPA Stack",
        "",
        "Raw timeline is the public-positive anchor. Neural Block-Canvas contributes the new MPS-trained dual-head JEPA residual, which is anti-aligned with the known bad JEPA public axis. Episode Retrieval is optional and only kept in variants where OOF still improves.",
        "",
        summary.head(100).to_csv(index=False),
    ]
    (OUT / "jepa_neural_episode_rawstack_report.md").write_text("\n".join(report), encoding="utf-8")
    print(summary.head(40).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
