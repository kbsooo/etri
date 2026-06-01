#!/usr/bin/env python3
"""H027: public/private-aware HS-JEPA generator.

H026 showed that a scalar public-bad veto can rank known anchors correctly, but
cannot make post-H012 actions public-safe after generation.  H027 changes the
generator itself: a cell is actionable only if a public-equation target, raw
human-state route, same-subject sleep-state memory, and public-bad-axis stress
are compatible enough before materialization.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h027_public_private_aware_generator_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H012_LB = 0.5681234831


@dataclass(frozen=True)
class SourceSpec:
    name: str
    prob_col: str
    strength_cols: tuple[str, ...]
    agree_col: str | None = None


@dataclass(frozen=True)
class StyleSpec:
    name: str
    public_w: float
    private_w: float
    human_w: float
    train_w: float
    good_w: float
    bad_w: float
    conflict_w: float
    q2_w: float
    amp_w: float


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def robust_z(x: pd.Series | np.ndarray) -> np.ndarray:
    arr = np.asarray(x, dtype=np.float64)
    med = np.nanmedian(arr)
    mad = np.nanmedian(np.abs(arr - med))
    scale = 1.4826 * mad if mad > 1.0e-12 else np.nanstd(arr)
    if not np.isfinite(scale) or scale < 1.0e-12:
        scale = 1.0
    return np.nan_to_num((arr - med) / scale)


def rank01(x: pd.Series | np.ndarray) -> np.ndarray:
    return pd.Series(np.asarray(x, dtype=np.float64)).rank(method="average", pct=True).to_numpy(dtype=np.float64)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 80) -> str:
    out = []
    for ch in str(text):
        out.append(ch if ch.isalnum() or ch in "._-" else "_")
    return "".join(out).strip("_")[:limit].strip("_")


def target_subset_mask(subset: str, n_rows: int) -> np.ndarray:
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    mapping = {
        "all": TARGETS,
        "Q": ["Q1", "Q2", "Q3"],
        "S": ["S1", "S2", "S3", "S4"],
        "QS_quality": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
        "S1S2S3": ["S1", "S2", "S3"],
        "Q2S1S3": ["Q2", "S1", "S3"],
    }
    targets = mapping.get(subset, [subset] if subset in TARGETS else [])
    for target in targets:
        mask[:, TARGETS.index(target)] = True
    return mask


def cell_energy(move_logit: np.ndarray, dirs: list[np.ndarray]) -> np.ndarray:
    if not dirs:
        return np.zeros_like(move_logit, dtype=np.float64)
    energy = np.zeros_like(move_logit, dtype=np.float64)
    for direction in dirs:
        scale = float(np.quantile(np.abs(direction), 0.95))
        scale = scale if scale > 1.0e-12 else 1.0
        energy += np.maximum(0.0, move_logit * direction / scale)
    return energy / max(len(dirs), 1)


def load_runtime():
    h026 = import_module(HITL / "h026_public_private_calibration_veto_jepa.py", "h026_public_private_calibration_veto_jepa")
    rt = h026.prepare_runtime()
    return h026, rt


def merge_cell_tables(rt) -> pd.DataFrame:
    base = []
    for row in range(rt.h012_prob.shape[0]):
        for t_i, target in enumerate(TARGETS):
            base.append({"row": row, "target": target, "target_i": t_i, "h012_prob": float(rt.h012_prob[row, t_i])})
    cells = pd.DataFrame(base)

    tables = [
        (
            OUT.parent / "h015_public_equation_self_feedback" / "h015_cell_posterior.csv",
            {
                "posterior_prob": "h015_prob",
                "posterior_minus_h012": "h015_minus_h012",
                "cell_score": "h015_cell_score",
                "direction_consistency": "h015_direction_consistency",
            },
        ),
        (
            OUT.parent / "h016_public_subset_weight_jepa" / "h016_cell_public_weights.csv",
            {
                "public_weight_mean": "h016_public_weight_mean",
                "public_weight_median": "h016_public_weight_median",
                "weight_score": "h016_weight_score",
                "h015_public_gain_score": "h016_h015_public_gain_score",
                "combined_score": "h016_combined_score",
                "mean_weighted_h015_cell_gain": "h016_weighted_h015_gain",
            },
        ),
        (
            OUT.parent / "h020_joint_vector_world_jepa" / "h020_cell_joint_vector_posterior.csv",
            {
                "q_joint_vector": "h020_prob",
                "joint_minus_h012": "h020_minus_h012",
                "cell_gain": "h020_cell_gain",
                "gain_score": "h020_gain_score",
                "move_score": "h020_move_score",
                "combined_score": "h020_combined_score",
            },
        ),
        (
            OUT.parent / "h021_human_state_vector_prior_jepa" / "h021_test_human_state_vector_prior_cells.csv",
            {
                "hs_prob": "h021_hs_prob",
                "h020_prob": "h021_h020_prob",
                "hs_minus_h012": "h021_hs_minus_h012",
                "h020_minus_h012": "h021_h020_minus_h012",
                "h020_gain": "h021_h020_gain",
                "hs_h020_agree": "h021_hs_h020_agree",
                "hs_cell_score": "h021_hs_cell_score",
                "hs_row_conf": "h021_hs_row_conf",
            },
        ),
        (
            OUT.parent / "h023_hs_pareto_proposal_vector_jepa" / "h023_cell_state.csv",
            {
                "hs_prob": "h023_hs_prob",
                "q_h023": "h023_prob",
                "h023_minus_h012": "h023_minus_h012",
                "hs_h023_agree": "h023_hs_h023_agree",
                "cell_gain": "h023_cell_gain",
                "gain_score": "h023_gain_score",
                "move_score": "h023_move_score",
                "combined_score": "h023_combined_score",
            },
        ),
        (
            OUT.parent / "h014_sleep_state_memory_posterior_audit" / "h014_memory_cells.csv",
            {
                "memory_prob_full": "h014_memory_prob",
                "memory_logit_delta": "h014_memory_logit_delta",
                "memory_alignment": "h014_memory_alignment",
                "memory_agrees_h012": "h014_memory_agrees_h012",
                "memory_disagrees_h012": "h014_memory_disagrees_h012",
                "row_full_reliability_q": "h014_row_reliability_q",
                "memory_alignment_q": "h014_memory_alignment_q",
                "private_safe_score": "h014_private_safe_score",
                "posterior_gain": "h014_posterior_gain",
            },
        ),
    ]
    for path, rename in tables:
        df = pd.read_csv(path)
        keep = ["row", "target"] + [c for c in rename if c in df.columns]
        df = df[keep].rename(columns=rename)
        cells = cells.merge(df, on=["row", "target"], how="left")
    for col in cells.columns:
        if col in {"target"}:
            continue
        if pd.api.types.is_bool_dtype(cells[col]):
            cells[col] = cells[col].astype(float)
        elif pd.api.types.is_numeric_dtype(cells[col]):
            cells[col] = cells[col].fillna(0.0)
    return cells


def source_specs() -> list[SourceSpec]:
    return [
        SourceSpec("h015_public_feedback", "h015_prob", ("h015_cell_score", "h016_combined_score", "h016_weighted_h015_gain")),
        SourceSpec("h020_joint_vector", "h020_prob", ("h020_combined_score", "h020_cell_gain", "h021_h020_gain"), "h021_hs_h020_agree"),
        SourceSpec("h023_hs_pareto", "h023_prob", ("h023_combined_score", "h023_cell_gain", "h023_gain_score"), "h023_hs_h023_agree"),
        SourceSpec("h021_hs_prior_probe", "h021_hs_prob", ("h021_hs_cell_score", "h021_hs_row_conf"), None),
    ]


def style_specs() -> list[StyleSpec]:
    return [
        StyleSpec("public_memory_bridge", 1.25, 0.80, 0.55, 0.55, 0.20, 0.70, 0.75, 0.35, 0.25),
        StyleSpec("private_strict", 0.85, 1.35, 0.85, 0.55, 0.15, 1.05, 1.20, 0.65, 0.30),
        StyleSpec("public_born", 1.65, 0.35, 0.30, 0.45, 0.30, 0.65, 0.45, 0.25, 0.25),
        StyleSpec("bad_axis_escape", 1.05, 0.70, 0.45, 0.50, 0.10, 1.75, 0.90, 0.75, 0.35),
        StyleSpec("wild_equation", 2.05, 0.10, 0.15, 0.35, 0.30, 0.35, 0.20, 0.15, 0.20),
    ]


def source_cell_frame(rt, cells: pd.DataFrame, source: SourceSpec, dirs: dict[str, list[np.ndarray]]) -> pd.DataFrame:
    frame = cells.copy()
    q = frame[source.prob_col].to_numpy(dtype=np.float64).reshape(rt.h012_prob.shape)
    q = clip_prob(q)
    h012 = rt.h012_prob
    move = logit(q) - logit(h012)
    feat = rt.h025.action_feature_frame(
        rt.test_pcs,
        h012,
        q,
        alpha=1.0,
        row_ids=np.arange(h012.shape[0]),
        family=source.name,
    )
    pred_gain = rt.action_model.predict(feat[rt.action_cols])
    frame["source"] = source.name
    frame["q_prob"] = q.reshape(-1)
    frame["source_delta_logit"] = move.reshape(-1)
    frame["source_abs_delta_logit"] = np.abs(move).reshape(-1)
    frame["source_delta_prob"] = (q - h012).reshape(-1)
    frame["train_pred_gain"] = pred_gain
    frame["public_bad_energy"] = cell_energy(move, dirs["bad"]).reshape(-1)
    frame["public_good_energy"] = cell_energy(move, dirs["good"]).reshape(-1)
    frame["q2_shortcut"] = frame["target"].eq("Q2").astype(float) * np.maximum(frame["public_bad_energy"], 0.0)

    strength = np.zeros(len(frame), dtype=np.float64)
    for col in source.strength_cols:
        if col in frame:
            strength += robust_z(frame[col])
    frame["public_source_strength"] = strength / max(len(source.strength_cols), 1)

    hs_delta = np.zeros(len(frame), dtype=np.float64)
    for col in ["h021_hs_minus_h012", "h023_hs_prob"]:
        if col == "h023_hs_prob" and col in frame:
            hs_delta += logit(frame[col].to_numpy(dtype=np.float64)) - logit(frame["h012_prob"].to_numpy(dtype=np.float64))
        elif col in frame:
            hs_delta += frame[col].to_numpy(dtype=np.float64)
    frame["human_direction_agree"] = (np.sign(frame["source_delta_logit"]) == np.sign(hs_delta)).astype(float)
    frame.loc[np.abs(hs_delta) <= 1.0e-12, "human_direction_agree"] = 0.0
    if source.agree_col and source.agree_col in frame:
        frame["human_direction_agree"] = np.maximum(frame["human_direction_agree"], frame[source.agree_col].astype(float))
    frame["human_confidence"] = np.maximum(
        rank01(frame.get("h021_hs_cell_score", pd.Series(0.0, index=frame.index))),
        rank01(frame.get("h021_hs_row_conf", pd.Series(0.0, index=frame.index))),
    )

    mem_delta = frame.get("h014_memory_logit_delta", pd.Series(0.0, index=frame.index)).to_numpy(dtype=np.float64)
    frame["memory_direction_agree"] = (np.sign(frame["source_delta_logit"]) == np.sign(mem_delta)).astype(float)
    frame.loc[np.abs(mem_delta) <= 1.0e-12, "memory_direction_agree"] = 0.0
    frame["private_safety"] = (
        0.45 * rank01(frame.get("h014_private_safe_score", pd.Series(0.0, index=frame.index)))
        + 0.25 * rank01(frame.get("h014_memory_alignment_q", pd.Series(0.0, index=frame.index)))
        + 0.20 * rank01(frame.get("h014_row_reliability_q", pd.Series(0.0, index=frame.index)))
        + 0.10 * frame["memory_direction_agree"]
    )
    frame["private_conflict"] = (
        (1.0 - frame["memory_direction_agree"])
        * rank01(np.abs(mem_delta))
        * (0.5 + 0.5 * rank01(frame.get("h014_row_reliability_q", pd.Series(0.0, index=frame.index))))
    )
    frame["moved"] = frame["source_abs_delta_logit"] > 1.0e-7
    return frame


def score_style(frame: pd.DataFrame, style: StyleSpec) -> np.ndarray:
    return (
        style.public_w * robust_z(frame["public_source_strength"])
        + style.private_w * robust_z(frame["private_safety"])
        + style.human_w * robust_z(frame["human_direction_agree"] * frame["human_confidence"])
        + style.train_w * robust_z(frame["train_pred_gain"])
        + style.good_w * robust_z(frame["public_good_energy"])
        - style.bad_w * robust_z(frame["public_bad_energy"])
        - style.conflict_w * robust_z(frame["private_conflict"])
        - style.q2_w * robust_z(frame["q2_shortcut"])
        - style.amp_w * robust_z(frame["source_abs_delta_logit"])
    )


def write_submission(rt, selected: pd.DataFrame, alpha: float, out_path: Path) -> dict[str, float]:
    out_logit = logit(rt.h012_prob)
    base_logit = out_logit.copy()
    for rec in selected.to_dict("records"):
        r = int(rec["row"])
        t = int(rec["target_i"])
        target_logit = float(logit(np.asarray([rec["q_prob"]]))[0])
        out_logit[r, t] = base_logit[r, t] + alpha * (target_logit - base_logit[r, t])
    out = rt.h012.copy()
    out[TARGETS] = sigmoid(out_logit)
    out[TARGETS] = out[TARGETS].clip(EPS, 1.0 - EPS)
    out.to_csv(out_path, index=False)
    diff = np.abs(out[TARGETS].to_numpy(dtype=np.float64) - rt.h012_prob)
    return {
        "mean_abs_delta_prob": float(diff.mean()),
        "max_abs_delta_prob": float(diff.max()),
        "changed_cells": int((diff > 1.0e-6).sum()),
        "changed_rows": int((diff.max(axis=1) > 1.0e-6).sum()),
        "hash": short_hash(out),
    }


def generate_variants(rt, all_cells: pd.DataFrame, dirs: dict[str, list[np.ndarray]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    scored_parts: list[pd.DataFrame] = []
    subsets = ["all", "Q", "S", "QS_quality", "S1S2S3", "Q2S1S3"]
    top_ks = [80, 160, 300, 520, 800, 1200, 1600]
    alphas = [0.25, 0.45, 0.70, 1.00]

    for source in source_specs():
        src = source_cell_frame(rt, all_cells, source, dirs)
        for style in style_specs():
            scored = src.copy()
            scored["style"] = style.name
            scored["h027_cell_score"] = score_style(scored, style)
            scored_parts.append(
                scored.sort_values("h027_cell_score", ascending=False).head(300)[
                    [
                        "source",
                        "style",
                        "row",
                        "target",
                        "q_prob",
                        "source_delta_logit",
                        "h027_cell_score",
                        "public_source_strength",
                        "private_safety",
                        "private_conflict",
                        "human_direction_agree",
                        "train_pred_gain",
                        "public_bad_energy",
                        "public_good_energy",
                    ]
                ]
            )
            for subset in subsets:
                subset_mask = target_subset_mask(subset, rt.h012_prob.shape[0]).reshape(-1)
                allowed = scored["moved"].to_numpy(dtype=bool) & subset_mask
                ranked = scored[allowed].sort_values("h027_cell_score", ascending=False)
                if ranked.empty:
                    continue
                for top_k in top_ks:
                    if top_k > len(ranked):
                        continue
                    selected = ranked.head(top_k).copy()
                    if float(selected["h027_cell_score"].sum()) <= 0:
                        continue
                    if float(selected["train_pred_gain"].sum()) <= 0 and style.name != "wild_equation":
                        continue
                    for alpha in alphas:
                        stem = safe_id(f"h027_{source.name}_{style.name}_{subset}_k{top_k}_a{str(alpha).replace('.', 'p')}")
                        out_path = OUT / f"submission_{stem}.csv"
                        stats = write_submission(rt, selected, alpha, out_path)
                        rows.append(
                            {
                                "file": f"hitl/h027_public_private_aware_generator_jepa/{out_path.name}",
                                "resolved_path": str(out_path),
                                "source": source.name,
                                "style": style.name,
                                "target_subset": subset,
                                "top_k": int(top_k),
                                "alpha": float(alpha),
                                "cell_score_sum": float(selected["h027_cell_score"].sum()),
                                "cell_score_mean": float(selected["h027_cell_score"].mean()),
                                "pred_gain_sum": float(selected["train_pred_gain"].sum()),
                                "public_bad_energy_mean": float(selected["public_bad_energy"].mean()),
                                "public_good_energy_mean": float(selected["public_good_energy"].mean()),
                                "private_safety_mean": float(selected["private_safety"].mean()),
                                "private_conflict_mean": float(selected["private_conflict"].mean()),
                                "human_agree_rate": float(selected["human_direction_agree"].mean()),
                                "memory_agree_rate": float(selected["memory_direction_agree"].mean()),
                                "q2_share": float(selected["target"].eq("Q2").mean()),
                                **stats,
                            }
                        )
    variants = pd.DataFrame(rows)
    top_cells = pd.concat(scored_parts, ignore_index=True) if scored_parts else pd.DataFrame()
    return variants, top_cells


def score_with_h024(h026, rt, variants: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    scored, model_scores, pred_samples = h026.score_variants_with_h024(rt, variants)
    scored["risk_width"] = scored["pred_public_p90"] - scored["pred_public_p10"]
    scored["h027_selection_score"] = (
        0.80 * robust_z(scored["cell_score_sum"])
        + 0.65 * robust_z(scored["pred_gain_sum"])
        + 0.55 * robust_z(scored["private_safety_mean"])
        + 0.35 * robust_z(scored["human_agree_rate"])
        + 0.70 * robust_z(scored["support_better_than_h012"].fillna(0.0))
        - 1.35 * robust_z(scored["pred_public_median"].fillna(0.58))
        - 0.85 * robust_z(scored["risk_width"].fillna(0.02))
        - 0.80 * robust_z(scored["public_bad_energy_mean"])
        - 0.35 * robust_z(scored["q2_share"])
    )
    return scored.sort_values("h027_selection_score", ascending=False).reset_index(drop=True), model_scores, pred_samples


def selected_stress(h026, rt, selected: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    return h026.selected_stress(rt, selected)


def decide(scored: pd.DataFrame, rowperm: pd.DataFrame, public_perm: pd.DataFrame) -> tuple[str, Path | None]:
    if scored.empty:
        return "no_h027_candidates", None
    selected = scored.iloc[0]
    rowperm_p = 1.0
    if not rowperm.empty:
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
    public_perm_p = 1.0
    if not public_perm.empty:
        real_margin = float(selected["pred_public_median"] - H012_LB)
        public_perm_p = float(np.mean(public_perm["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= real_margin))
    support = float(selected.get("support_better_than_h012", 0.0))
    pred_public = float(selected.get("pred_public_median", 0.58))
    gate = (
        pred_public <= H012_LB - 0.00010
        and support >= 0.45
        and rowperm_p <= 0.08
        and public_perm_p <= 0.12
        and float(selected.get("public_bad_energy_mean", 9.0)) <= float(scored["public_bad_energy_mean"].quantile(0.55))
        and float(selected.get("changed_cells", 0)) >= 80
    )
    if not gate:
        return "diagnostic_only_born_public_private_generator_not_promoted", None
    source = Path(str(selected["resolved_path"]))
    digest = hashlib.sha1(source.read_bytes()).hexdigest()[:8]
    out = ROOT / f"submission_h027_born_public_private_{digest}_uploadsafe.csv"
    shutil.copyfile(source, out)
    return "primary_born_public_private_generator", out


def write_report(
    variants: pd.DataFrame,
    top_cells: pd.DataFrame,
    scored: pd.DataFrame,
    model_scores: pd.DataFrame,
    rowperm: pd.DataFrame,
    public_perm: pd.DataFrame,
    decision: str,
    promoted: Path | None,
) -> None:
    lines = []
    lines.append("# H027 Public/Private-Aware Generator HS-JEPA\n")
    lines.append("## Question\n")
    lines.append(
        "H012 proved the public-equation posterior. The external V106 note says same-subject sleep-state/sensor-quality memory is also strong. "
        "H014 showed their simple overlap is too small. H027 asks whether the action generator itself can be born from both views, instead of generating public-only actions and vetoing them later.\n"
    )
    lines.append("## World Model Bet\n")
    lines.append(
        "- context: H015/H020/H023 public posterior targets, H021/H023 human-state agreement, H014 subject/time memory, H026 public-good/bad axes.\n"
        "- target representation: a cell-level action-health state that is public-readable and private-aware before materialization.\n"
        "- if true: H024 should see H027 variants as below H012 with nontrivial support, and H025 row-placement stress should beat row permutations.\n"
        "- if false: post-H012 improvement is not a missing scalar veto or memory overlap; it requires a new public/private calibration target.\n"
    )
    lines.append("## Generated Variants\n")
    lines.append(f"- generated variants: `{len(variants)}`\n")
    if not variants.empty:
        cols = [
            "file",
            "source",
            "style",
            "target_subset",
            "top_k",
            "alpha",
            "cell_score_sum",
            "pred_gain_sum",
            "private_safety_mean",
            "human_agree_rate",
            "public_bad_energy_mean",
            "q2_share",
            "pred_public_median",
            "pred_public_p10",
            "pred_public_p90",
            "support_better_than_h012",
            "h027_selection_score",
        ]
        lines.append(md_table(scored[[c for c in cols if c in scored.columns]], 18) + "\n")
    lines.append("## Top Cells\n")
    if not top_cells.empty:
        lines.append(md_table(top_cells, 18) + "\n")
    lines.append("## Public Decoder Stress\n")
    if not model_scores.empty:
        top = model_scores.iloc[0]
        lines.append(
            f"- best H024 decoder in H027 pool: `{top['feature_set']}` alpha `{top['alpha']}`, "
            f"MAE `{top['loo_mae']:.6f}`, Spearman `{top['loo_spearman']:.6f}`, pairwise `{top['loo_pair_acc']:.6f}`\n"
        )
    lines.append("## Selected Stress\n")
    if not rowperm.empty:
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
        lines.append(f"- H025 row-permutation p(higher top1200 gain): `{rowperm_p:.9f}`\n")
        lines.append(f"- real top1200 H025 gain: `{float(rowperm['real_top1200_sum'].iloc[0]):.9f}`\n")
    if not public_perm.empty and not scored.empty:
        selected = scored.iloc[0]
        real_margin = float(selected["pred_public_median"] - H012_LB)
        public_perm_p = float(np.mean(public_perm["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= real_margin))
        lines.append(f"- H024 public-score permutation p(lower margin): `{public_perm_p:.9f}`\n")
        lines.append(f"- selected predicted public margin vs H012: `{real_margin:.9f}`\n")
    lines.append("## Decision\n")
    lines.append(f"- decision: `{decision}`\n")
    lines.append(f"- promoted path: `{promoted if promoted is not None else 'none'}`\n")
    lines.append(
        "\nInterpretation: H027 is a big-bet generator test. A failure does not kill H012 or subject memory; it kills the idea that existing H015/H020/H023 posterior targets can be made safer by cell-level public/private birth constraints alone.\n"
    )
    (OUT / "h027_report.md").write_text("".join(lines))


def main() -> None:
    h026, rt = load_runtime()
    dirs = h026.anchor_dirs(rt)
    cells = merge_cell_tables(rt)
    variants, top_cells = generate_variants(rt, cells, dirs)
    cells.to_csv(OUT / "h027_merged_cell_state.csv", index=False)
    top_cells.to_csv(OUT / "h027_top_cells_by_source_style.csv", index=False)
    variants.to_csv(OUT / "h027_generated_variants_raw.csv", index=False)

    if variants.empty:
        scored = variants
        model_scores = pd.DataFrame()
        pred_samples = pd.DataFrame()
        rowperm = pd.DataFrame()
        public_perm = pd.DataFrame()
        decision, promoted = "no_h027_generated_variants", None
    else:
        scored, model_scores, pred_samples = score_with_h024(h026, rt, variants)
        scored.to_csv(OUT / "h027_variant_scores.csv", index=False)
        model_scores.to_csv(OUT / "h027_h024_model_scores.csv", index=False)
        pred_samples.to_csv(OUT / "h027_h024_prediction_samples.csv", index=False)
        selected = scored.iloc[0]
        rowperm, public_perm = selected_stress(h026, rt, selected)
        rowperm.to_csv(OUT / "h027_selected_h025_rowperm_stress.csv", index=False)
        public_perm.to_csv(OUT / "h027_selected_h024_public_perm_stress.csv", index=False)
        decision, promoted = decide(scored, rowperm, public_perm)

    pd.DataFrame(
        [
            {
                "decision": decision,
                "selected_file": None if scored.empty else scored.iloc[0]["file"],
                "selected_resolved_path": None if scored.empty else scored.iloc[0]["resolved_path"],
                "promoted_path": None if promoted is None else str(promoted),
            }
        ]
    ).to_csv(OUT / "h027_decision.csv", index=False)
    write_report(variants, top_cells, scored, model_scores, rowperm, public_perm, decision, promoted)
    print(pd.read_csv(OUT / "h027_decision.csv").to_string(index=False))
    if not scored.empty:
        print(
            scored.head(12)[
                [
                    "file",
                    "source",
                    "style",
                    "target_subset",
                    "top_k",
                    "alpha",
                    "h027_selection_score",
                    "pred_gain_sum",
                    "pred_public_median",
                    "support_better_than_h012",
                    "public_bad_energy_mean",
                    "private_safety_mean",
                    "q2_share",
                ]
            ].to_string(index=False)
        )


if __name__ == "__main__":
    main()
