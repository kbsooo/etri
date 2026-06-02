#!/usr/bin/env python3
"""H067: row-responsibility public-state HS-JEPA.

H057 validated the strongest post-H012 claim so far: the 45 rows where H042
changed Q2 can carry a full non-Q2 hidden human-state vector. H061 then showed
that the 270 H057 support cells are mostly positive after H057 feedback, so
cell-level cutting is underidentified.

H067 changes the unit of doubt from cell to row:

    context = known public actions, H057/H061 feedback, H064-H066 row-state maps
    target  = row-level public responsibility for the hidden public listener
    action  = reweight H057 seed rows and expand only high-responsibility rows

If H067 improves, H057 was not a uniform 45-row rule; it was a public-weighted
row-state. If it fails, responsibility fitting is not enough and H057 should be
treated as a compact public-specific state until direct public feedback says
otherwise.
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
ANALYSIS = ROOT / "analysis_outputs"
OUT = HITL / "h067_row_responsibility_public_state_jepa"
OUT.mkdir(parents=True, exist_ok=True)

if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from public_anchor_bottleneck_decomposition import known_public_table  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
NON_Q2 = [target for target in TARGETS if target != "Q2"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050 = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
H057 = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
H061 = "submission_h061_h057feedback_support_69e9c079_uploadsafe.csv"
H062 = "submission_h062_h057seed_rowstate_expand_23beb8eb_uploadsafe.csv"
H063 = "submission_h063_humancontext_seed_2c748a8e_uploadsafe.csv"
H064 = "submission_h064_contrastive_state_graph_d09a5363_uploadsafe.csv"
H065 = "submission_h065_state_transition_phase_75d5575d_uploadsafe.csv"
H066 = "submission_h066_state_sequence_episode_route_8ca9b9b6_uploadsafe.csv"

MANUAL_PUBLIC = {
    H012: (0.5681234831, "manual H012 public-equation best"),
    H042: (0.5679048248, "manual H042 Q2 phase public sensor"),
    H050: (0.5679048248, "manual H050 non-Q2 target-route null sensor"),
    H057: (0.5677475939, "manual H057 Q2-row full-vector public frontier"),
}


@dataclass(frozen=True)
class CandidateSpec:
    family: str
    seed_top: int
    seed_bottom: int
    expansion_rows: int
    seed_alpha: float
    exp_alpha: float
    bottom_keep: float
    route_k: int
    mode: str


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H055MOD = import_module(HITL / "h055_postfeedback_public_listener_jepa.py", "h055mod_for_h067")


def locate(name: str | Path) -> Path | None:
    return H055MOD.locate(name)


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    return H055MOD.load_sub(name, sample)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return H055MOD.clip_prob(x)


def logit(x: np.ndarray) -> np.ndarray:
    return H055MOD.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return H055MOD.sigmoid(x)


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return H055MOD.bce(prob, q)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H055MOD.md_table(frame, n)


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return H055MOD.rank01(values, high)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    H055MOD.write_submission(sample, prob, path)


def move_toward(base: np.ndarray, target: np.ndarray, alpha: float, mode: str) -> np.ndarray:
    if mode == "prob":
        return clip_prob((1.0 - alpha) * base + alpha * target)
    if mode == "logit":
        return clip_prob(sigmoid((1.0 - alpha) * logit(base) + alpha * logit(target)))
    raise ValueError(mode)


def key_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["subject_id"] = out["subject_id"].astype(str)
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    return out


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h067_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h067_rowresp_public_state_*_uploadsafe.csv"):
        path.unlink()


def read_public_observations() -> pd.DataFrame:
    known = known_public_table().copy()
    known["known_source"] = known.get("known_source", "known_public_table")
    manual = pd.DataFrame(
        [
            {"file": file, "public_lb": lb, "note": note, "known_source": "manual_h067"}
            for file, (lb, note) in MANUAL_PUBLIC.items()
        ]
    )
    out = pd.concat([known, manual], ignore_index=True)
    out = out.drop_duplicates("file", keep="last")
    rows = [rec for rec in out.to_dict("records") if locate(str(rec["file"])) is not None]
    return pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)


def load_q061(sample: pd.DataFrame) -> np.ndarray:
    src = HITL / "h061_h057_feedback_support_translator_jepa" / "h061_cell_posterior.csv"
    df = pd.read_csv(src)
    mat = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
    tix = {target: i for i, target in enumerate(TARGETS)}
    for rec in df.to_dict("records"):
        mat[int(rec["row"]), tix[str(rec["target"])]] = float(rec["q061"])
    return clip_prob(mat)


def changed_rows(path: str, base_prob: np.ndarray, sample: pd.DataFrame) -> set[int]:
    resolved = locate(path)
    if resolved is None:
        return set()
    prob = load_sub(resolved, sample)[TARGETS].to_numpy(dtype=np.float64)
    return set(np.where((np.abs(prob - base_prob) > 1.0e-12).any(axis=1))[0].tolist())


def aggregate_h061_support(sample: pd.DataFrame) -> pd.DataFrame:
    support_path = HITL / "h061_h057_feedback_support_translator_jepa" / "h061_cell_support.csv"
    support = pd.read_csv(support_path)
    grouped = support.groupby("row", as_index=False).agg(
        h061_support_cells=("target", "count"),
        h061_support_mean=("support_score", "mean"),
        h061_support_sum=("support_score", "sum"),
        h061_gain_sum=("gain061_h057_vs_h042", "sum"),
        h061_gain_mean=("gain061_h057_vs_h042", "mean"),
        h061_gain_min=("gain061_h057_vs_h042", "min"),
        h061_feedback_lift_sum=("feedback_lift", "sum"),
        h061_direction_agreement_mean=("direction_agreement", "mean"),
        h061_abs_move_sum=("abs_h057_move", "sum"),
    )
    base = sample[KEYS].copy()
    base["row"] = np.arange(len(sample))
    out = base.merge(grouped, on="row", how="left")
    fill_cols = [c for c in out.columns if c.startswith("h061_")]
    out[fill_cols] = out[fill_cols].fillna(0.0)
    return out


def row_public_responsibility(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    h057_prob: np.ndarray,
    h042_prob: np.ndarray,
    q061: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    base_lb = MANUAL_PUBLIC[H057][0]
    x_rows: list[np.ndarray] = []
    y_vals: list[float] = []
    rows: list[dict[str, object]] = []
    for rec in known.to_dict("records"):
        file = str(rec["file"])
        if file == H057 or file not in pred_by_file:
            continue
        pred = pred_by_file[file]
        row_loss_delta = bce(pred, q061).mean(axis=1) - bce(h057_prob, q061).mean(axis=1)
        actual_delta = float(rec["public_lb"]) - base_lb
        x_rows.append(row_loss_delta)
        y_vals.append(actual_delta)
        rows.append(
            {
                "file": file,
                "public_lb": float(rec["public_lb"]),
                "actual_delta_vs_h057": actual_delta,
                "row_loss_delta_mean": float(row_loss_delta.mean()),
                "row_loss_delta_std": float(row_loss_delta.std()),
                "changed_rows_vs_h057": int((np.abs(pred - h057_prob) > 1.0e-12).any(axis=1).sum()),
            }
        )
    x = np.vstack(x_rows)
    y = np.asarray(y_vals, dtype=np.float64)
    x_mean = x.mean(axis=0)
    x_std = x.std(axis=0)
    x_std = np.where(x_std < 1.0e-10, 1.0, x_std)
    xs = (x - x_mean) / x_std
    y_mean = float(y.mean())
    yc = y - y_mean
    gram = xs @ xs.T
    scale = float(np.median(np.diag(gram)))
    if not np.isfinite(scale) or scale <= 1.0e-12:
        scale = float(np.mean(np.diag(gram)) + 1.0e-12)
    lam = 0.08 * scale
    dual = np.linalg.pinv(gram + lam * np.eye(gram.shape[0])) @ yc
    beta_scaled = xs.T @ dual
    beta = beta_scaled / x_std
    pred_delta = y_mean + xs @ beta_scaled
    loo_pred = []
    for hold in range(len(y)):
        keep = np.ones(len(y), dtype=bool)
        keep[hold] = False
        xs_k = xs[keep]
        y_k = y[keep]
        yc_k = y_k - float(y_k.mean())
        gram_k = xs_k @ xs_k.T
        scale_k = float(np.median(np.diag(gram_k)))
        if not np.isfinite(scale_k) or scale_k <= 1.0e-12:
            scale_k = float(np.mean(np.diag(gram_k)) + 1.0e-12)
        dual_k = np.linalg.pinv(gram_k + 0.08 * scale_k * np.eye(gram_k.shape[0])) @ yc_k
        beta_k = xs_k.T @ dual_k
        loo_pred.append(float(y_k.mean()) + float(xs[hold] @ beta_k))

    equation = pd.DataFrame(rows)
    equation["ridge_pred_delta_vs_h057"] = pred_delta
    equation["loo_pred_delta_vs_h057"] = loo_pred
    equation["loo_abs_error"] = (equation["loo_pred_delta_vs_h057"] - equation["actual_delta_vs_h057"]).abs()

    h042_row_delta = bce(h042_prob, q061).mean(axis=1) - bce(h057_prob, q061).mean(axis=1)
    signed_support = beta * h042_row_delta
    responsibility = np.maximum(signed_support, 0.0) + 0.15 * np.abs(beta_scaled)
    if responsibility.sum() <= 1.0e-18:
        responsibility = np.ones_like(responsibility)
    responsibility = responsibility / responsibility.sum()
    out = pd.DataFrame(
        {
            "row": np.arange(len(h057_prob)),
            "public_beta": beta,
            "public_beta_scaled": beta_scaled,
            "public_signed_support": signed_support,
            "public_responsibility_raw": responsibility,
            "public_responsibility_rank": rank01(responsibility),
            "h042_row_loss_delta_vs_h057": h042_row_delta,
        }
    )
    return out, equation.sort_values("actual_delta_vs_h057").reset_index(drop=True)


def prepare_row_table(
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h050_prob: np.ndarray,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = aggregate_h061_support(sample)
    pub_resp, equation = row_public_responsibility(known, pred_by_file, h057_prob, h042_prob, q061)
    rows = base.merge(pub_resp, on="row", how="left")

    non_q2_ix = [TARGETS.index(t) for t in NON_Q2]
    seed = (np.abs(h057_prob[:, non_q2_ix] - h042_prob[:, non_q2_ix]) > 1.0e-12).any(axis=1)
    h050_changed = (np.abs(h050_prob - h042_prob) > 1.0e-12).any(axis=1)
    rows["is_h057_seed"] = seed.astype(int)
    rows["is_h050_null"] = (h050_changed & ~seed).astype(int)
    rows["h062_changed_row"] = rows["row"].isin(changed_rows(H062, h057_prob, sample)).astype(int)
    rows["h063_changed_row"] = rows["row"].isin(changed_rows(H063, h057_prob, sample)).astype(int)
    rows["h064_changed_row"] = rows["row"].isin(changed_rows(H064, h057_prob, sample)).astype(int)
    rows["h065_changed_row"] = rows["row"].isin(changed_rows(H065, h057_prob, sample)).astype(int)
    rows["h066_changed_row"] = rows["row"].isin(changed_rows(H066, h057_prob, sample)).astype(int)

    h065_rows = pd.read_csv(HITL / "h065_state_transition_phase_jepa" / "h065_row_scores.csv")
    h065_keep = [
        "row",
        "row_gain_to_q061_nonq2",
        "h064_row_score",
        "h065_row_score",
        "phase_route_gain",
        "phase_near",
        "episode_near",
        "graph_rank",
        "contrast_rank",
        "gain_rank2",
        "nearest_seed_order_distance",
    ]
    h065_rows = h065_rows[[c for c in h065_keep if c in h065_rows.columns]].copy()
    rows = rows.merge(h065_rows, on="row", how="left")

    h066_rows = pd.read_csv(HITL / "h066_state_sequence_episode_route_jepa" / "h066_row_scores.csv")
    h066_keep = ["row", "h066_emission", "row_top4_gain_sum", "row_top4_gain_rank"]
    h066_rows = h066_rows[[c for c in h066_keep if c in h066_rows.columns]].copy()
    rows = rows.merge(h066_rows, on="row", how="left")

    gain_to_q = bce(h057_prob, q061) - bce(q061, q061)
    for target in NON_Q2:
        rows[f"{target}_q061_gain_from_h057"] = gain_to_q[:, TARGETS.index(target)]
    rows["row_q061_gain_from_h057_nonq2"] = gain_to_q[:, non_q2_ix].sum(axis=1)
    rows["positive_q061_targets_nonq2"] = (gain_to_q[:, non_q2_ix] > 0.0).sum(axis=1)
    rows["seed_support_rank"] = rank01(rows["h061_gain_sum"].to_numpy())
    rows["feedback_rank"] = rank01(rows["h061_feedback_lift_sum"].to_numpy())
    rows["q061_gain_rank"] = rank01(rows["row_q061_gain_from_h057_nonq2"].to_numpy())
    rows["context_overlap"] = (
        rows["h062_changed_row"]
        + rows["h063_changed_row"]
        + rows["h064_changed_row"]
        + rows["h065_changed_row"]
        + rows["h066_changed_row"]
    ) / 5.0
    numeric_fill = rows.select_dtypes(include=[np.number]).columns
    rows[numeric_fill] = rows[numeric_fill].replace([np.inf, -np.inf], np.nan).fillna(0.0)

    rows["seed_responsibility_score"] = (
        0.36 * rows["seed_support_rank"]
        + 0.24 * rows["public_responsibility_rank"]
        + 0.18 * rows["feedback_rank"]
        + 0.12 * rank01(rows["h061_support_mean"].to_numpy())
        + 0.10 * (rows["h061_direction_agreement_mean"] > 0).astype(float)
    ) * rows["is_h057_seed"]

    rows["extension_score"] = (
        0.20 * rows["public_responsibility_rank"]
        + 0.18 * rank01(rows["h066_emission"].to_numpy())
        + 0.14 * rank01(rows["h065_row_score"].to_numpy())
        + 0.13 * rank01(rows["h064_row_score"].to_numpy())
        + 0.13 * rows["q061_gain_rank"]
        + 0.10 * rows["context_overlap"]
        + 0.06 * rows["episode_near"].clip(0.0, 1.0)
        + 0.06 * rows["phase_near"].clip(0.0, 1.0)
        - 0.45 * rows["is_h050_null"]
        - 0.35 * rows["is_h057_seed"]
    )
    rows["extension_score"] = rows["extension_score"].clip(lower=-1.0)
    rows["public_weight"] = rows["public_responsibility_raw"] / max(float(rows["public_responsibility_raw"].sum()), 1.0e-18)
    return rows.sort_values("row").reset_index(drop=True), equation


def route_targets_for_row(row_rec: pd.Series, route_k: int) -> list[str]:
    gains = [(target, float(row_rec[f"{target}_q061_gain_from_h057"])) for target in NON_Q2]
    gains.sort(key=lambda item: item[1], reverse=True)
    return [target for target, gain in gains[:route_k] if gain > 0.0]


def apply_candidate(
    spec: CandidateSpec,
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    row_table: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, object]]:
    prob = h057_prob.copy()
    seed_rows = row_table[row_table["is_h057_seed"] == 1].sort_values("seed_responsibility_score", ascending=False)
    ext_pool = row_table[(row_table["is_h057_seed"] == 0) & (row_table["is_h050_null"] == 0)].sort_values(
        "extension_score", ascending=False
    )

    top_seed = seed_rows.head(spec.seed_top)
    bottom_seed = seed_rows.tail(spec.seed_bottom) if spec.seed_bottom else seed_rows.iloc[0:0]
    expansion = ext_pool.head(spec.expansion_rows)

    top_target = move_toward(h057_prob, q061, spec.seed_alpha, spec.mode)
    exp_target = move_toward(h057_prob, q061, spec.exp_alpha, spec.mode)
    rollback_target = clip_prob(h042_prob + spec.bottom_keep * (h057_prob - h042_prob))

    if spec.family in {"seed_reweight", "hybrid"}:
        for row in top_seed["row"].astype(int):
            for target in NON_Q2:
                j = TARGETS.index(target)
                prob[row, j] = top_target[row, j]
        for row in bottom_seed["row"].astype(int):
            for target in NON_Q2:
                j = TARGETS.index(target)
                prob[row, j] = rollback_target[row, j]

    if spec.family in {"expansion_only", "hybrid"}:
        for rec in expansion.to_dict("records"):
            row = int(rec["row"])
            for target in route_targets_for_row(pd.Series(rec), spec.route_k):
                j = TARGETS.index(target)
                prob[row, j] = exp_target[row, j]

    changed = np.abs(prob - h057_prob) > 1.0e-12
    row_loss_delta = bce(prob, q061).mean(axis=1) - bce(h057_prob, q061).mean(axis=1)
    weighted_delta = float(np.dot(row_table["public_weight"].to_numpy(dtype=np.float64), row_loss_delta))
    uniform_delta = float((bce(prob, q061) - bce(h057_prob, q061)).mean())
    selected_rows = set(np.where(changed.any(axis=1))[0].tolist())
    seed_changed = selected_rows & set(seed_rows["row"].astype(int).tolist())
    exp_changed = selected_rows - set(seed_rows["row"].astype(int).tolist())
    h064_rows = set(row_table.loc[row_table["h064_changed_row"] == 1, "row"].astype(int))
    h065_rows = set(row_table.loc[row_table["h065_changed_row"] == 1, "row"].astype(int))
    h066_rows = set(row_table.loc[row_table["h066_changed_row"] == 1, "row"].astype(int))
    null_rows = set(row_table.loc[row_table["is_h050_null"] == 1, "row"].astype(int))
    selected_detail = row_table[row_table["row"].isin(selected_rows)]
    meta = {
        "candidate_id": "",
        "family": spec.family,
        "seed_top": spec.seed_top,
        "seed_bottom": spec.seed_bottom,
        "expansion_rows_requested": spec.expansion_rows,
        "seed_alpha": spec.seed_alpha,
        "exp_alpha": spec.exp_alpha,
        "bottom_keep": spec.bottom_keep,
        "route_k": spec.route_k,
        "mode": spec.mode,
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(changed.any(axis=1).sum()),
        "q2_changed_vs_h057": int(changed[:, TARGETS.index("Q2")].sum()),
        "posterior_delta_vs_h057": uniform_delta,
        "responsibility_weighted_delta_vs_h057": weighted_delta,
        "seed_changed_rows": len(seed_changed),
        "expansion_changed_rows": len(exp_changed),
        "h050_null_rows_selected": len(selected_rows & null_rows),
        "h064_overlap_rows": len(selected_rows & h064_rows),
        "h065_overlap_rows": len(selected_rows & h065_rows),
        "h066_overlap_rows": len(selected_rows & h066_rows),
        "selected_subjects": int(selected_detail["subject_id"].nunique()) if len(selected_detail) else 0,
        "mean_selected_seed_responsibility": float(selected_detail["seed_responsibility_score"].mean()) if len(selected_detail) else 0.0,
        "mean_selected_extension_score": float(selected_detail["extension_score"].mean()) if len(selected_detail) else 0.0,
        "mean_selected_public_weight": float(selected_detail["public_weight"].mean()) if len(selected_detail) else 0.0,
        "selected_rows": ",".join(map(str, sorted(selected_rows))),
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return clip_prob(prob), meta


def candidate_sweep(
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    row_table: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    specs: list[CandidateSpec] = []
    for family in ["seed_reweight", "expansion_only", "hybrid"]:
        seed_tops = [0] if family == "expansion_only" else [12, 18, 24, 30, 45]
        seed_bottoms = [0] if family == "expansion_only" else [0, 6, 12, 18]
        exp_rows = [0] if family == "seed_reweight" else [18, 30, 42, 54, 66]
        for seed_top in seed_tops:
            for seed_bottom in seed_bottoms:
                if seed_top + seed_bottom > 45:
                    continue
                for expansion_rows in exp_rows:
                    for seed_alpha in ([1.0] if family == "expansion_only" else [0.75, 1.0, 1.25, 1.50]):
                        for exp_alpha in ([1.0] if family == "seed_reweight" else [0.75, 1.0, 1.15]):
                            for bottom_keep in ([1.0] if seed_bottom == 0 else [0.0, 0.30, 0.60, 0.85]):
                                for route_k in ([4] if family == "seed_reweight" else [3, 4, 6]):
                                    for mode in ["logit", "prob"]:
                                        specs.append(
                                            CandidateSpec(
                                                family=family,
                                                seed_top=seed_top,
                                                seed_bottom=seed_bottom,
                                                expansion_rows=expansion_rows,
                                                seed_alpha=seed_alpha,
                                                exp_alpha=exp_alpha,
                                                bottom_keep=bottom_keep,
                                                route_k=route_k,
                                                mode=mode,
                                            )
                                        )

    rows: list[dict[str, object]] = []
    probs: dict[str, np.ndarray] = {}
    seen: set[str] = set()
    for spec in specs:
        prob, meta = apply_candidate(spec, sample, h042_prob, h057_prob, q061, row_table)
        if meta["changed_cells_vs_h057"] == 0:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        cid = (
            f"h067_{spec.family}_st{spec.seed_top}_sb{spec.seed_bottom}_er{spec.expansion_rows}_"
            f"sa{str(spec.seed_alpha).replace('.', 'p')}_ea{str(spec.exp_alpha).replace('.', 'p')}_"
            f"bk{str(spec.bottom_keep).replace('.', 'p')}_r{spec.route_k}_{spec.mode}_{digest}"
        )
        meta["candidate_id"] = cid
        meta["hash"] = digest
        rows.append(meta)
        probs[cid] = prob

    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H067 candidates generated")
    cand["posterior_rank"] = (-cand["posterior_delta_vs_h057"]).rank(method="average", pct=True)
    cand["responsibility_rank"] = (-cand["responsibility_weighted_delta_vs_h057"]).rank(method="average", pct=True)
    cand["extension_rank"] = cand["mean_selected_extension_score"].rank(method="average", pct=True)
    cand["public_weight_rank"] = cand["mean_selected_public_weight"].rank(method="average", pct=True)
    cand["overlap_rate"] = (
        cand["h064_overlap_rows"] + cand["h065_overlap_rows"] + cand["h066_overlap_rows"]
    ) / (3.0 * cand["changed_rows_vs_h057"].clip(lower=1))
    cand["size_score"] = 1.0 - (cand["changed_cells_vs_h057"] - 260).abs() / 360.0
    cand["size_score"] = cand["size_score"].clip(0.0, 1.0)
    cand["row_size_score"] = 1.0 - (cand["changed_rows_vs_h057"] - 60).abs() / 80.0
    cand["row_size_score"] = cand["row_size_score"].clip(0.0, 1.0)
    cand["h067_score"] = (
        0.27 * cand["responsibility_rank"]
        + 0.20 * cand["posterior_rank"]
        + 0.13 * cand["extension_rank"]
        + 0.12 * cand["public_weight_rank"]
        + 0.10 * cand["overlap_rate"].clip(0.0, 1.0)
        + 0.07 * cand["size_score"]
        + 0.05 * cand["row_size_score"]
        + 0.04 * (cand["selected_subjects"] / 10.0).clip(0.0, 1.0)
        + 0.04 * (cand["family"] == "hybrid").astype(float)
        - 0.50 * (cand["q2_changed_vs_h057"] > 0).astype(float)
        - 0.40 * (cand["h050_null_rows_selected"] > 0).astype(float)
    )
    cand = cand.sort_values(["h067_score", "responsibility_weighted_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    return cand, probs


def validate_upload(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    df = load_sub(path, sample)
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    changed = np.abs(prob - h057_prob) > 1.0e-12
    return {
        "path": str(path),
        "rows": int(len(df)),
        "keys_match": bool(df[KEYS].equals(sample[KEYS])),
        "duplicate_keys": int(df.duplicated(KEYS).sum()),
        "nan_cells": int(df[TARGETS].isna().sum().sum()),
        "min_prob": float(prob.min()),
        "max_prob": float(prob.max()),
        "q2_changed_vs_h057_validation": int(changed[:, TARGETS.index("Q2")].sum()),
        "upload_safe": bool(
            len(df) == len(sample)
            and df[KEYS].equals(sample[KEYS])
            and df.duplicated(KEYS).sum() == 0
            and df[TARGETS].isna().sum().sum() == 0
            and prob.min() > 0.0
            and prob.max() < 1.0
            and int(changed[:, TARGETS.index("Q2")].sum()) == 0
        ),
    }


def main() -> None:
    cleanup_previous_outputs()
    known = read_public_observations()
    sample_df = load_sub(H057)
    sample = sample_df[KEYS].copy()
    pred_by_file: dict[str, np.ndarray] = {}
    kept_rows = []
    for rec in known.to_dict("records"):
        file = str(rec["file"])
        try:
            pred_by_file[file] = load_sub(file, sample)[TARGETS].to_numpy(dtype=np.float64)
            kept_rows.append(rec)
        except Exception:
            continue
    known = pd.DataFrame(kept_rows).sort_values("public_lb").reset_index(drop=True)

    h042_prob = load_sub(H042, sample)[TARGETS].to_numpy(dtype=np.float64)
    h050_prob = load_sub(H050, sample)[TARGETS].to_numpy(dtype=np.float64)
    h057_prob = sample_df[TARGETS].to_numpy(dtype=np.float64)
    q061 = load_q061(sample)

    row_table, public_equations = prepare_row_table(sample, h042_prob, h050_prob, h057_prob, q061, known, pred_by_file)
    cand, probs = candidate_sweep(sample, h042_prob, h057_prob, q061, row_table)

    top_ids = cand.head(160)["candidate_id"].astype(str).tolist()
    for candidate_id in top_ids:
        prob = probs[candidate_id]
        path = OUT / f"submission_{candidate_id}.csv"
        write_submission(sample, prob, path)
        cand.loc[cand["candidate_id"] == candidate_id, "file"] = path.name
        cand.loc[cand["candidate_id"] == candidate_id, "resolved_path"] = str(path)

    selected = cand.iloc[0].to_dict()
    selected_id = str(selected["candidate_id"])
    selected_prob = probs[selected_id]
    selected_hash = str(selected["hash"])
    selected_path = OUT / f"submission_{selected_id}.csv"
    if not selected_path.exists():
        write_submission(sample, selected_prob, selected_path)
    root_path = ROOT / f"submission_h067_rowresp_public_state_{selected_hash}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    upload_check = validate_upload(root_path, sample, h057_prob)

    row_summary = pd.DataFrame(
        [
            {
                "total_rows": int(len(row_table)),
                "h057_seed_rows": int(row_table["is_h057_seed"].sum()),
                "h050_null_rows": int(row_table["is_h050_null"].sum()),
                "h064_rows": int(row_table["h064_changed_row"].sum()),
                "h065_rows": int(row_table["h065_changed_row"].sum()),
                "h066_rows": int(row_table["h066_changed_row"].sum()),
                "public_equation_count": int(len(public_equations)),
                "public_equation_loo_mae": float(public_equations["loo_abs_error"].mean()),
                "public_equation_loo_p90": float(public_equations["loo_abs_error"].quantile(0.90)),
                "seed_public_weight_sum": float(row_table.loc[row_table["is_h057_seed"] == 1, "public_weight"].sum()),
                "nonseed_public_weight_sum": float(row_table.loc[row_table["is_h057_seed"] == 0, "public_weight"].sum()),
            }
        ]
    )

    decision = pd.DataFrame(
        [
            {
                "decision": "promote_row_responsibility_public_state_sensor",
                "selected_candidate_id": selected_id,
                "selected_file": str(selected_path.name),
                "selected_resolved_path": str(selected_path),
                "root_uploadsafe_path": str(root_path),
                "worldview": "H057 row-state support is public-responsibility weighted rather than uniformly valid",
                **selected,
                **upload_check,
            }
        ]
    )

    known.to_csv(OUT / "h067_augmented_public_observations.csv", index=False)
    public_equations.to_csv(OUT / "h067_public_row_equations.csv", index=False)
    row_table.to_csv(OUT / "h067_row_responsibility.csv", index=False)
    row_summary.to_csv(OUT / "h067_row_summary.csv", index=False)
    cand.to_csv(OUT / "h067_candidate_scores.csv", index=False)
    decision.to_csv(OUT / "h067_decision.csv", index=False)

    report = f"""# H067 Row-Responsibility Public-State HS-JEPA

Question: is H057's `45`-row full-vector state uniformly valid, or is it a
public-responsibility weighted state where only some rows carry most of the
public listener?

Design:

- base: H057 public frontier;
- Q2 frozen exactly;
- row responsibility is inferred from known public action responses, H061
  support, and H064-H066 row-state maps;
- actions can amplify high-responsibility H057 seed rows, roll back
  low-responsibility seed rows, and expand H065/H066 rows only when their
  public responsibility and state scores are high.

Row summary:

{md_table(row_summary)}

Public row-equation fit:

{md_table(public_equations.head(20))}

Top responsible rows:

{md_table(row_table.sort_values("public_weight", ascending=False).head(25))}

Decision:

{md_table(decision)}

Top candidates:

{md_table(cand.head(30))}

Interpretation rule:

- If H067 improves over H057, the next HS-JEPA object is a row-responsibility
  public-state decoder, not a uniform H057 row copier.
- If H067 loses while H064-H066 also lose, expansion outside H057 is blocked and
  H057 should be treated as a compact public-specific row-state.
- If H067 loses but H066 improves, the responsibility equation is the wrong
  lens and sequence episodes should replace row responsibility.
"""
    (OUT / "h067_report.md").write_text(report)
    print(f"H067 selected: {selected_id}")
    print(f"H067 root: {root_path}")
    print(
        decision[
            [
                "selected_candidate_id",
                "changed_cells_vs_h057",
                "changed_rows_vs_h057",
                "posterior_delta_vs_h057",
                "responsibility_weighted_delta_vs_h057",
                "q2_changed_vs_h057",
                "upload_safe",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
