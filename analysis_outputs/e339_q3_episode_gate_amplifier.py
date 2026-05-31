#!/usr/bin/env python3
"""E339: Q3 episode-gated amplifier.

E338 found a clean but too-small Q3/dateblock episode sensor.  This experiment
keeps that row/episode placement fixed and asks a narrower question:

    can an existing stronger Q3 direction be projected through the E338
    episode gate without losing E247 safety or becoming movement-null common?

This is intentionally not a new broad model.  The representation is E338's
hidden lifestyle-state episode; the target is action visibility under the
existing public-free selector and movement-null controls.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from scipy.special import expit


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import E247, load_sub_frame, md_table, safe_id  # noqa: E402
from e337_residual_lifestyle_cluster_state import (  # noqa: E402
    bad_axes,
    cell_bad_veto,
    center_by_target,
    make_null_delta,
    short_hash,
    stable_seed,
    target_abs,
)
from e338_cluster_local_episode_action import cluster_labels, latent_train_test  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, known_public_table, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

EPS = 1.0e-12
RNG_SEED = 20260531 + 339
CAP = 0.10
TOP_NULL_CANDIDATES = 18
NULL_REPS = 5

E338_EPISODE = OUT / "e338_cluster_local_episode_table.csv"

CANDIDATE_OUT = OUT / "e339_q3_episode_gate_amplifier_candidates.csv"
SOURCE_OUT = OUT / "e339_q3_episode_gate_amplifier_sources.csv"
SCORE_OUT = OUT / "e339_q3_episode_gate_amplifier_scores.csv"
ANATOMY_OUT = OUT / "e339_q3_episode_gate_amplifier_anatomy.csv"
MOVE_NULL_OUT = OUT / "e339_q3_episode_gate_amplifier_movement_nulls.csv"
REPORT_OUT = OUT / "e339_q3_episode_gate_amplifier_report.md"

SOURCE_FILES = [
    "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv",
    "submission_e267_humansocial_tail_balanced_2936100f.csv",
    "submission_e95_hardtail_541e3973.csv",
    "submission_mixmin_0c916bb4.csv",
    "submission_e101_q2s3tail_177569bc.csv",
    "submission_e176_abl_q2_to0p75_91e49725.csv",
    "submission_e224_e224_q3s0p625_s4toward_e154_a0p5_5b0439db.csv",
    "submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e154_a0p5_50e6b7ec.csv",
    "submission_e269_anti_e256_tophalf_beta035_4e910856.csv",
    "submission_e269_e247only_all_amp006_control_2cef7c9d.csv",
    "submission_e323_5508f966_uploadsafe.csv",
    "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
]

SCALES = [0.15, 0.25, 0.40, 0.60, 0.85, 1.10]
Q3 = TARGETS.index("Q3")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def load_current() -> pd.DataFrame:
    return load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)


def locate(name: str) -> Path | None:
    path = Path(name)
    if path.exists():
        return path
    candidate = OUT / name
    if candidate.exists():
        return candidate
    return None


def episode_records() -> pd.DataFrame:
    if not E338_EPISODE.exists():
        raise RuntimeError("Run e338_cluster_local_episode_action.py before E339")
    episodes = pd.read_csv(E338_EPISODE)
    episodes = episodes[episodes["episode_gate"].astype(bool) & episodes["target"].eq("Q3")].copy()
    episodes = episodes.sort_values(["strength", "test_rows"], ascending=[False, False]).reset_index(drop=True)
    if episodes.empty:
        raise RuntimeError("No gated Q3 episodes found in E338")
    return episodes


def episode_delta(episodes: pd.DataFrame, selected: pd.DataFrame) -> np.ndarray:
    _train, test, train_lat, test_lat = latent_train_test()
    delta = np.zeros((len(test), len(TARGETS)), dtype=np.float64)
    labels_by_k: dict[int, np.ndarray] = {}
    for rec in selected.itertuples(index=False):
        k = int(rec.k)
        if k not in labels_by_k:
            _tr, te = cluster_labels(train_lat, test_lat, k)
            labels_by_k[k] = te
        rows = labels_by_k[k] == int(rec.cluster)
        delta[rows, Q3] += float(rec.delta_logit)
    return delta


def episode_configs(episodes: pd.DataFrame) -> list[tuple[str, pd.DataFrame]]:
    configs: list[tuple[str, pd.DataFrame]] = []
    configs.append(("q3_top1", episodes.head(1).copy()))
    if len(episodes) >= 2:
        configs.append(("q3_top2", episodes.head(2).copy()))
    if len(episodes) >= 3:
        configs.append(("q3_top3", episodes.head(3).copy()))
    configs.append(("q3_all", episodes.copy()))
    out: list[tuple[str, pd.DataFrame]] = []
    seen: set[str] = set()
    for name, part in configs:
        key = ",".join(f"{int(r.k)}:{int(r.cluster)}" for r in part.itertuples())
        if key and key not in seen:
            seen.add(key)
            out.append((name, part))
    return out


def source_directions(base: pd.DataFrame, base_logit: np.ndarray, signed_gate: np.ndarray) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    rows: list[dict[str, Any]] = []
    dirs: dict[str, np.ndarray] = {}
    public = known_public_table().set_index("file")["public_lb"].to_dict()
    active = np.abs(signed_gate[:, Q3]) > EPS
    gate_sign = np.sign(signed_gate[:, Q3])
    sample = base[KEYS]
    for name in SOURCE_FILES:
        path = locate(name)
        if path is None:
            continue
        src = load_sub_frame(path, sample)
        delta = logit(src[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        dirs[name] = delta
        q = delta[:, Q3]
        active_q = q[active]
        rows.append(
            {
                "source": name,
                "public_lb": public.get(name, np.nan),
                "q3_l1_all": float(np.sum(np.abs(q))),
                "q3_l1_episode": float(np.sum(np.abs(active_q))),
                "q3_nonzero_episode": int((np.abs(active_q) > EPS).sum()),
                "q3_sign_agree_episode": float(np.mean(np.sign(active_q) == gate_sign[active])) if active_q.size else np.nan,
                "q3_mean_signed_gate_dot": float(np.mean(active_q * gate_sign[active])) if active_q.size else np.nan,
                "q3_mean_abs_episode": float(np.mean(np.abs(active_q))) if active_q.size else 0.0,
            }
        )
    out = pd.DataFrame(rows).sort_values(["q3_l1_episode", "q3_mean_signed_gate_dot"], ascending=[False, False]).reset_index(drop=True)
    out.to_csv(SOURCE_OUT, index=False)
    return out, dirs


def candidate_direction(source_delta: np.ndarray, signed_gate: np.ndarray, mode: str) -> np.ndarray:
    active = np.abs(signed_gate[:, Q3]) > EPS
    gate_sign = np.sign(signed_gate[:, Q3])
    src = np.asarray(source_delta[:, Q3], dtype=np.float64)
    out = np.zeros_like(source_delta)
    if mode == "src_raw":
        vals = src.copy()
    elif mode == "src_inv":
        vals = -src
    elif mode == "src_agree":
        vals = np.where(src * gate_sign > 0.0, src, 0.0)
    elif mode == "src_disagree_inv":
        vals = np.where(src * gate_sign < 0.0, -src, 0.0)
    elif mode == "gate_signed_abs":
        vals = gate_sign * np.abs(src)
    elif mode == "gate_signed_sqrt":
        vals = gate_sign * np.sqrt(np.abs(src) + EPS) * np.sqrt(np.nanmedian(np.abs(src[active])) + EPS)
    elif mode == "gate_shape":
        mag = np.nanmedian(np.abs(src[active])) if np.any(active) else 0.0
        vals = gate_sign * float(mag)
    else:
        raise ValueError(mode)
    vals = np.where(active, vals, 0.0)
    out[:, Q3] = vals
    return out


def write_candidate(base: pd.DataFrame, base_logit: np.ndarray, delta: np.ndarray, candidate_id: str) -> Path:
    out = base.copy()
    out[TARGETS] = expit(np.clip(base_logit + np.clip(delta, -CAP, CAP), -40.0, 40.0))
    path = OUT / f"submission_e339_{safe_id(candidate_id, 110)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize(base: pd.DataFrame, episodes: pd.DataFrame) -> tuple[pd.DataFrame, list[Path], np.ndarray, np.ndarray, np.ndarray]:
    base_logit, e323_bad, e216_bad = bad_axes(base)
    # The top2 gate is the current safest sensor, so source diagnostics use it.
    signed_gate_for_sources = center_by_target(episode_delta(episodes, episodes.head(min(2, len(episodes)))))
    source_df, dirs = source_directions(base, base_logit, signed_gate_for_sources)
    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    modes = ["src_raw", "src_inv", "src_agree", "src_disagree_inv", "gate_signed_abs", "gate_signed_sqrt", "gate_shape"]
    transforms = {
        "raw": lambda d: d,
        "centered": center_by_target,
        "veto_centered": lambda d: center_by_target(cell_bad_veto(d, e323_bad, e216_bad)),
    }
    for cfg_name, part in episode_configs(episodes):
        gate = episode_delta(episodes, part)
        if np.sum(np.abs(gate)) <= EPS:
            continue
        for source_name, source_delta in dirs.items():
            for mode in modes:
                raw = candidate_direction(source_delta, gate, mode)
                if np.sum(np.abs(raw)) <= EPS:
                    continue
                for transform_name, transform in transforms.items():
                    direction = transform(raw)
                    if np.sum(np.abs(direction)) <= EPS:
                        continue
                    for scale in SCALES:
                        delta = direction * float(scale)
                        if np.sum(np.abs(delta)) <= EPS:
                            continue
                        candidate_id = f"{cfg_name}_{Path(source_name).stem}_{mode}_{transform_name}_s{scale:.2f}"
                        path = write_candidate(base, base_logit, delta, candidate_id)
                        paths.append(path)
                        rows.append(
                            {
                                "candidate_id": candidate_id,
                                "file": rel(path),
                                "basename": path.name,
                                "config": cfg_name,
                                "source": source_name,
                                "mode": mode,
                                "transform": transform_name,
                                "scale": float(scale),
                                "source_public_lb": source_df.set_index("source").get("public_lb", pd.Series()).get(source_name, np.nan),
                                "episode_count": int(len(part)),
                                "changed_rows": int(np.any(np.abs(delta) > EPS, axis=1).sum()),
                                "changed_cells": int((np.abs(delta) > EPS).sum()),
                                "mean_abs_logit_delta": float(np.mean(np.abs(delta))),
                                "max_abs_logit_delta": float(np.max(np.abs(delta))),
                                "l1_logit_delta": float(np.sum(np.abs(delta))),
                                "cos_with_e323_bad": float(np.sum(delta * e323_bad) / (np.linalg.norm(delta) * np.linalg.norm(e323_bad) + EPS)),
                                "cos_with_e216_bad": float(np.sum(delta * e216_bad) / (np.linalg.norm(delta) * np.linalg.norm(e216_bad) + EPS)),
                                **target_abs(delta),
                            }
                        )
    cand = pd.DataFrame(rows).sort_values(["config", "source", "mode", "transform", "scale"]).reset_index(drop=True)
    cand.to_csv(CANDIDATE_OUT, index=False)
    return cand, paths, base_logit, e323_bad, e216_bad


def score_paths(paths: list[Path]) -> pd.DataFrame:
    if not paths:
        pd.DataFrame().to_csv(SCORE_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(OUT / CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    features = build_features([CURRENT] + [rel(p) for p in paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def anatomy(paths: list[Path], base: pd.DataFrame, base_logit: np.ndarray, e323_bad: np.ndarray, e216_bad: np.ndarray) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in paths:
        cand = load_sub_frame(path, base[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        rows.append(
            {
                "basename": path.name,
                "changed_rows": int(np.any(np.abs(delta) > EPS, axis=1).sum()),
                "changed_cells": int((np.abs(delta) > EPS).sum()),
                "l1_logit_delta": float(np.sum(np.abs(delta))),
                "mean_abs_logit_delta": float(np.mean(np.abs(delta))),
                "max_abs_logit_delta": float(np.max(np.abs(delta))),
                "cos_with_e323_bad": float(np.sum(delta * e323_bad) / (np.linalg.norm(delta) * np.linalg.norm(e323_bad) + EPS)),
                "cos_with_e216_bad": float(np.sum(delta * e216_bad) / (np.linalg.norm(delta) * np.linalg.norm(e216_bad) + EPS)),
                **target_abs(delta),
            }
        )
    out = pd.DataFrame(rows).sort_values(["cos_with_e323_bad", "l1_logit_delta"]).reset_index(drop=True)
    out.to_csv(ANATOMY_OUT, index=False)
    return out


def movement_null_stress(scores: pd.DataFrame, candidates: pd.DataFrame, base: pd.DataFrame, base_logit: np.ndarray) -> pd.DataFrame:
    if scores.empty or candidates.empty:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    non_current = scores[~scores["basename"].eq(CURRENT)].copy()
    joined = non_current.merge(candidates, on="basename", how="left", suffixes=("_score", "_meta"))
    chosen = joined.sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).head(TOP_NULL_CANDIDATES)
    null_paths: list[Path] = []
    null_rows: list[dict[str, Any]] = []
    for rec in chosen.to_dict("records"):
        path = ROOT / str(rec.get("file_meta", rec.get("file", "")))
        cand = load_sub_frame(path, base[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        for mode in ["row_perm", "target_perm", "sign_flip", "row_sign", "cell_perm"]:
            for rep in range(NULL_REPS):
                nd = make_null_delta(delta, mode, stable_seed("e339", rec["basename"], mode, rep))
                npth = write_candidate(base, base_logit, nd, f"null_{Path(rec['basename']).stem}_{mode}_{rep}")
                null_paths.append(npth)
                null_rows.append({"basename": rec["basename"], "null_basename": npth.name, "mode": mode, "rep": rep})
    if not null_paths:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(OUT / CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    null_features = build_features([CURRENT] + [rel(p) for p in null_paths], sample, refs, ref_vecs)
    null_scores = score_candidates(known, null_features, model_df)
    cols = ["basename", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "strict_promote_gate"]
    null_map = pd.DataFrame(null_rows).merge(null_scores[cols].rename(columns={"basename": "null_basename"}), on="null_basename", how="left")
    actual = non_current[cols].rename(
        columns={
            "pred_delta_vs_current_mean": "actual_mean",
            "pred_delta_vs_current_p90": "actual_p90",
            "pred_beats_current_rate": "actual_beats_rate",
            "strict_promote_gate": "actual_strict_promote",
        }
    )
    rows: list[dict[str, Any]] = []
    for basename, part in null_map.groupby("basename"):
        act = actual[actual["basename"].eq(basename)]
        if act.empty:
            continue
        a = act.iloc[0]
        rows.append(
            {
                "basename": basename,
                "null_count": int(len(part)),
                "actual_mean": float(a["actual_mean"]),
                "actual_p90": float(a["actual_p90"]),
                "actual_beats_rate": float(a["actual_beats_rate"]),
                "actual_strict_promote": bool(a["actual_strict_promote"]),
                "null_mean_best": float(part["pred_delta_vs_current_mean"].min()),
                "null_mean_median": float(part["pred_delta_vs_current_mean"].median()),
                "null_p90_best": float(part["pred_delta_vs_current_p90"].min()),
                "null_p90_median": float(part["pred_delta_vs_current_p90"].median()),
                "actual_mean_dominance": float(np.mean(float(a["actual_mean"]) < part["pred_delta_vs_current_mean"].to_numpy(dtype=float))),
                "actual_p90_dominance": float(np.mean(float(a["actual_p90"]) < part["pred_delta_vs_current_p90"].to_numpy(dtype=float))),
                "null_strict_promote_rate": float(part["strict_promote_gate"].astype(bool).mean()),
            }
        )
    out = pd.DataFrame(rows).sort_values(["actual_strict_promote", "actual_p90_dominance", "actual_p90"], ascending=[False, False, True])
    out.to_csv(MOVE_NULL_OUT, index=False)
    return out


def write_report(episodes: pd.DataFrame, candidates: pd.DataFrame, scores: pd.DataFrame, anat: pd.DataFrame, nulls: pd.DataFrame) -> None:
    source_df = pd.read_csv(SOURCE_OUT) if SOURCE_OUT.exists() else pd.DataFrame()
    non_current = scores[~scores["basename"].eq(CURRENT)].copy() if len(scores) else pd.DataFrame()
    promoted = non_current[non_current["strict_promote_gate"].astype(bool)] if len(non_current) else pd.DataFrame()
    info = non_current[non_current["info_sensor_gate"].astype(bool)] if len(non_current) else pd.DataFrame()
    null_safe = pd.DataFrame()
    if len(nulls):
        null_safe = nulls[
            (nulls["actual_strict_promote"].astype(bool))
            & (nulls["actual_mean_dominance"] >= 0.75)
            & (nulls["actual_p90_dominance"] >= 0.75)
            & (nulls["null_strict_promote_rate"] <= 0.05)
        ]
    lines = [
        "# E339 Q3 Episode-Gated Amplifier",
        "",
        "## Question",
        "",
        "Can E338's safe-but-small Q3 lifestyle episode gate amplify an existing stronger Q3 direction without collapsing into E323-like or movement-null-common action?",
        "",
        "## Episode Inputs",
        "",
        f"- gated Q3 episodes: `{len(episodes)}`",
        "",
        md_table(episodes, n=12),
        "",
        "## Source Direction Diagnostics",
        "",
        md_table(source_df, n=20),
        "",
        "## Generated Candidates",
        "",
        f"- generated candidates: `{len(candidates)}`",
        f"- selector-promoted candidates: `{len(promoted)}`",
        f"- information-sensor candidates: `{len(info)}`",
        f"- movement-null-safe promoted candidates: `{len(null_safe)}`",
        "",
        md_table(candidates, n=30),
        "",
        "## Public-Free Selector Scores",
        "",
        md_table(
            non_current.sort_values(["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"], ascending=[False, False, True, True])
            if len(non_current)
            else non_current,
            n=40,
        ),
        "",
        "## Anatomy",
        "",
        md_table(anat, n=30),
        "",
        "## Movement-Null Stress",
        "",
        md_table(nulls, n=25),
        "",
        "## Decision",
        "",
    ]
    if len(null_safe):
        lines.append("At least one E338-gated Q3 amplified action clears selector and movement-null gates. Treat it as a submission candidate after manual public-risk review.")
    elif len(promoted):
        lines.append("E338-gated Q3 amplification reaches selector promotion but fails movement-null certification. Do not submit yet.")
    elif len(info):
        lines.append("E339 finds additional information sensors but no submission-grade action. The E338 episode gate remains useful, but borrowed Q3 directions still cannot cross visibility safely.")
    else:
        lines.append("No amplified Q3 episode action survives. This weakens the route of simply projecting older Q3 directions through the E338 latent gate.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{SOURCE_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{SCORE_OUT.name}`",
            f"- `{ANATOMY_OUT.name}`",
            f"- `{MOVE_NULL_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    episodes = episode_records()
    base = load_current()
    candidates, paths, base_logit, e323_bad, e216_bad = materialize(base, episodes)
    scores = score_paths(paths)
    anat = anatomy(paths, base, base_logit, e323_bad, e216_bad)
    nulls = movement_null_stress(scores, candidates, base, base_logit)
    write_report(episodes, candidates, scores, anat, nulls)
    print(REPORT_OUT)
    if len(scores):
        non_current = scores[~scores["basename"].eq(CURRENT)].copy()
        cols = ["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p10", "pred_delta_vs_current_p90", "pred_beats_current_rate"]
        print(non_current[cols].head(40).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
