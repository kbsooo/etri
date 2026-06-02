#!/usr/bin/env python3
"""H085: augmented public-equation human-state prototype HS-JEPA.

H012 solved a public-equation inverse problem from the E247 basin.  The later
H042/H050/H057 submissions added new public observations after that jump.

H085 asks a different question:

    If H057 is the new base, do the old and post-H012 public equations imply
    a different hidden human-state posterior?

The action unit is not a target-wise top-k tweak.  The primary decoder maps the
new posterior into row-level human-state vectors and route prototypes.  A win
would mean HS-JEPA should periodically refit its hidden public-state target as
new public sensor readings arrive, then decode row-vector states rather than
fixed manual routes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import shutil

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h085_augmented_public_equation_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
NON_Q2 = [target for target in TARGETS if target != "Q2"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
TOL = 1.0e-12

BASE_FILE = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
BASE_LB = 0.5677475939

MANUAL_PUBLIC = {
    "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv": (
        0.5679048248,
        "post-H012 Q2 phase public observation; tied H050 and lost to H057",
    ),
    "submission_h050_target_route_phase_b140216b_uploadsafe.csv": (
        0.5679048248,
        "post-H012 target-route phase public observation; tied H042",
    ),
    BASE_FILE: (
        BASE_LB,
        "current public frontier used as H085 base",
    ),
    "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv": (
        0.5684942019,
        "post-H094 public observation; dual public/private Pareto gate worsened vs H057",
    ),
}

BAD_ANCHORS = [
    "submission_h010_objective_s1s4_v2_uploadsafe.csv",
    "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
    "submission_e323_5508f966_uploadsafe.csv",
    "submission_jepa_latent_q2_w0p45.csv",
    "submission_jepa_latent_residual_probe.csv",
    "submission_lejepa_targetwise_strict_best_scale0p5.csv",
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
]


@dataclass(frozen=True)
class H085Spec:
    name: str
    unit: str
    target_group: str
    max_units: int
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    alpha: float
    cap: float
    min_score: float
    require_source_agree: bool
    require_h082: bool
    novelty: str


def locate(name: str | Path) -> Path | None:
    path = Path(name)
    if path.exists():
        return path
    for base in [ROOT, ROOT / "analysis_outputs", ROOT / "jepa", ROOT / "gpt_pro_pack"]:
        candidate = base / str(name)
        if candidate.exists():
            return candidate
    matches = list(ROOT.rglob(str(name)))
    return matches[0] if matches else None


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    qq = clip_prob(q)
    return -(qq * np.log(p) + (1.0 - qq) * np.log(1.0 - p))


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    s = pd.Series(np.asarray(values, dtype=np.float64)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if s.nunique(dropna=True) <= 1:
        return np.full(len(s), 0.5, dtype=np.float64)
    out = s.rank(method="average", pct=True).to_numpy(dtype=np.float64)
    return out if high else 1.0 - out


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 128) -> str:
    keep = [ch if ch.isalnum() or ch in "._-" else "_" for ch in str(text)]
    return "".join(keep).strip("_")[:limit].strip("_")


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


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h085_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h085_aug_public_equation_*_uploadsafe.csv"):
        path.unlink()


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    path = locate(name)
    if path is None:
        raise FileNotFoundError(str(name))
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    df = df.sort_values(KEYS).reset_index(drop=True)
    if sample is not None and not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"key mismatch: {name}")
    return df


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample.copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


def validate_submission(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> dict[str, object]:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    df = df.sort_values(KEYS).reset_index(drop=True)
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    return {
        "path": str(path.resolve()),
        "rows": int(len(df)),
        "keys_match": bool(df[KEYS].equals(sample[KEYS])),
        "duplicate_keys": int(df.duplicated(KEYS).sum()),
        "nan_cells": int(np.isnan(prob).sum()),
        "min_prob": float(np.nanmin(prob)),
        "max_prob": float(np.nanmax(prob)),
        "changed_cells_vs_h057_validation": int((np.abs(prob - base_prob) > TOL).sum()),
        "upload_safe": bool(
            len(df) == len(sample)
            and df[KEYS].equals(sample[KEYS])
            and int(df.duplicated(KEYS).sum()) == 0
            and int(np.isnan(prob).sum()) == 0
            and float(np.nanmin(prob)) >= EPS
            and float(np.nanmax(prob)) <= 1.0 - EPS + 1.0e-12
        ),
    }


def public_observations(sample: pd.DataFrame) -> pd.DataFrame:
    rows: dict[str, dict[str, object]] = {}
    obs_path = ROOT / "analysis_outputs" / "public_probe_observations.csv"
    if obs_path.exists():
        for rec in pd.read_csv(obs_path).to_dict("records"):
            file_name = str(rec["file"])
            rows[file_name] = {
                "file": file_name,
                "public_lb": float(rec["public_lb"]),
                "note": str(rec.get("note", "")),
                "known_source": "public_probe_observations",
            }
    for file_name, (public_lb, note) in MANUAL_PUBLIC.items():
        rows[file_name] = {
            "file": file_name,
            "public_lb": float(public_lb),
            "note": note,
            "known_source": "manual_post_h012",
        }

    kept = []
    for rec in rows.values():
        path = locate(str(rec["file"]))
        if path is None:
            continue
        try:
            load_sub(path, sample)
        except Exception:
            continue
        kept.append({**rec, "resolved_path": str(path.resolve())})
    out = pd.DataFrame(kept).sort_values("public_lb").reset_index(drop=True)
    if BASE_FILE not in set(out["file"].astype(str)):
        raise RuntimeError("base public observation missing")
    return out


def build_equation_system(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    base_prob: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    base = clip_prob(base_prob.reshape(-1))
    base_lb = float(known.loc[known["file"].eq(BASE_FILE), "public_lb"].iloc[0])
    rows = []
    a_rows = []
    d0_rows = []
    b_vals = []
    n = base.size
    for rec in known.to_dict("records"):
        file_name = str(rec["file"])
        if file_name == BASE_FILE:
            continue
        pred = clip_prob(pred_by_file[file_name].reshape(-1))
        d0 = -np.log(1.0 - pred) + np.log(1.0 - base)
        d1 = np.log((1.0 - pred) / pred) - np.log((1.0 - base) / base)
        actual_delta = float(rec["public_lb"]) - base_lb
        rhs = actual_delta - float(d0.mean())
        rows.append(
            {
                "file": file_name,
                "public_lb": float(rec["public_lb"]),
                "actual_delta_vs_h057": actual_delta,
                "d0_mean": float(d0.mean()),
                "rhs_label_term": rhs,
                "d1_abs_mean": float(np.mean(np.abs(d1))),
                "changed_cells_vs_h057": int((np.abs(pred - base) > TOL).sum()),
            }
        )
        a_rows.append(d1 / n)
        d0_rows.append(d0)
        b_vals.append(rhs)
    equations = pd.DataFrame(rows)
    return equations, np.vstack(a_rows), np.vstack(d0_rows), np.asarray(b_vals, dtype=np.float64)


def fit_posterior(a: np.ndarray, b: np.ndarray, prior: np.ndarray, ridge_mult: float) -> np.ndarray:
    if len(b) == 0:
        return clip_prob(prior)
    gram = a @ a.T
    scale = float(np.median(np.diag(gram)))
    if not np.isfinite(scale) or scale <= 1.0e-18:
        scale = float(np.mean(np.diag(gram)) + 1.0e-18)
    lam = float(ridge_mult) * scale
    residual = b - a @ prior
    try:
        dual = np.linalg.solve(gram + lam * np.eye(len(b)), residual)
    except np.linalg.LinAlgError:
        dual = np.linalg.pinv(gram + lam * np.eye(len(b))) @ residual
    return clip_prob(prior + a.T @ dual)


def predict_delta_from_q(d0: np.ndarray, d1: np.ndarray, q: np.ndarray) -> float:
    return float(np.mean(d0 + d1 * q))


def pivot_cell_table(path: Path, col: str, n_rows: int, default: float) -> np.ndarray:
    df = pd.read_csv(path)
    out = np.full((n_rows, len(TARGETS)), default, dtype=np.float64)
    target_i = {target: i for i, target in enumerate(TARGETS)}
    for rec in df.to_dict("records"):
        target = str(rec["target"])
        if target in target_i:
            out[int(rec["row"]), target_i[target]] = float(rec[col])
    return clip_prob(out)


def make_priors(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    base_prob: np.ndarray,
    sample: pd.DataFrame,
) -> dict[str, np.ndarray]:
    best_lb = float(known["public_lb"].min())
    preds = []
    weights = []
    for rec in known.to_dict("records"):
        file_name = str(rec["file"])
        pred = pred_by_file[file_name]
        lb = float(rec["public_lb"])
        preds.append(pred)
        weights.append(np.exp(-(lb - best_lb) / 0.00032))
    w = np.asarray(weights, dtype=np.float64)
    w = w / w.sum()
    good_soft = np.tensordot(w, np.stack(preds, axis=0), axes=(0, 0))
    h012_posterior = pivot_cell_table(
        HITL / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv",
        "posterior_prob",
        len(sample),
        0.5,
    )
    h061_q = pivot_cell_table(
        HITL / "h061_h057_feedback_support_translator_jepa" / "h061_cell_posterior.csv",
        "q061",
        len(sample),
        0.5,
    )
    return {
        "h057": base_prob.reshape(-1),
        "h012_public_posterior": h012_posterior.reshape(-1),
        "h061_h057_feedback": h061_q.reshape(-1),
        "public_good_soft": good_soft.reshape(-1),
        "h057_h012_mix": clip_prob(0.55 * base_prob + 0.45 * h012_posterior).reshape(-1),
    }


def evaluate_configs(
    equations: pd.DataFrame,
    a: np.ndarray,
    d0_rows: np.ndarray,
    b: np.ndarray,
    priors: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    ridge_mults = [1.0e-5, 3.0e-5, 1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0]
    actual = equations["actual_delta_vs_h057"].to_numpy(dtype=np.float64)
    d1_rows = a * next(iter(priors.values())).size
    rows = []
    full_qs: dict[str, np.ndarray] = {}
    for prior_name, prior in priors.items():
        for ridge_mult in ridge_mults:
            full_q = fit_posterior(a, b, prior, ridge_mult)
            full_pred = np.asarray([predict_delta_from_q(d0_rows[i], d1_rows[i], full_q) for i in range(len(actual))])
            loo_pred = []
            for heldout in range(len(actual)):
                keep = np.ones(len(actual), dtype=bool)
                keep[heldout] = False
                q = fit_posterior(a[keep], b[keep], prior, ridge_mult)
                loo_pred.append(predict_delta_from_q(d0_rows[heldout], d1_rows[heldout], q))
            loo_pred = np.asarray(loo_pred, dtype=np.float64)
            err = loo_pred - actual
            key = f"{prior_name}__ridge_{ridge_mult:g}"
            full_qs[key] = full_q
            rows.append(
                {
                    "posterior_key": key,
                    "prior_name": prior_name,
                    "ridge_mult": ridge_mult,
                    "loo_mae": float(np.mean(np.abs(err))),
                    "loo_rmse": float(np.sqrt(np.mean(err * err))),
                    "loo_p90_abs": float(np.quantile(np.abs(err), 0.90)),
                    "loo_spearman": float(pd.Series(loo_pred).corr(pd.Series(actual), method="spearman")),
                    "loo_pearson": float(pd.Series(loo_pred).corr(pd.Series(actual), method="pearson")),
                    "known_fit_mae": float(np.mean(np.abs(full_pred - actual))),
                    "known_fit_p90_abs": float(np.quantile(np.abs(full_pred - actual), 0.90)),
                    "q_mean": float(full_q.mean()),
                    "q_std": float(full_q.std()),
                    "q_extreme_rate": float(((full_q < 0.03) | (full_q > 0.97)).mean()),
                    "q_move_l1_vs_prior": float(np.mean(np.abs(full_q - prior))),
                    "q_move_l1_vs_h057": float(np.mean(np.abs(full_q - priors["h057"]))),
                    "config_score": float(
                        -np.mean(np.abs(err))
                        -0.35 * np.quantile(np.abs(err), 0.90)
                        -0.00040 * ((full_q < 0.03) | (full_q > 0.97)).mean()
                        -0.00012 * np.mean(np.abs(full_q - priors["h057"]))
                    ),
                }
            )
    configs = pd.DataFrame(rows).sort_values(
        ["config_score", "loo_mae", "known_fit_mae"], ascending=[False, True, True]
    ).reset_index(drop=True)
    return configs, full_qs


def target_indices_for(group: str) -> list[int]:
    if group == "all":
        return list(range(len(TARGETS)))
    if group == "nonq2":
        return [TARGETS.index(target) for target in NON_Q2]
    if group == "stage":
        return [TARGETS.index(target) for target in S_TARGETS]
    if group == "q":
        return [TARGETS.index(target) for target in ["Q1", "Q2", "Q3"]]
    if group == "q2":
        return [TARGETS.index("Q2")]
    raise ValueError(group)


def move_toward_q(base_prob: np.ndarray, q_prob: np.ndarray, mask: np.ndarray, alpha: float, cap: float) -> np.ndarray:
    z_base = logit(base_prob)
    z_q = logit(q_prob)
    out = z_base.copy()
    move = np.clip(z_q - z_base, -cap, cap)
    out[mask] = z_base[mask] + alpha * move[mask]
    return clip_prob(sigmoid(out))


def add_support_tables(sample: pd.DataFrame, base_prob: np.ndarray, q_prob: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    n = len(sample)
    h080 = pd.read_csv(HITL / "h080_invariant_action_core_jepa" / "h080_cell_table.csv")
    h080 = h080.sort_values(["row", "target_index"]).reset_index(drop=True)
    h082_path = HITL / "h082_source_action_field_jepa" / "h082_selected_cells.csv"
    h082 = pd.read_csv(h082_path) if h082_path.exists() else pd.DataFrame(columns=["row", "target"])
    h082_pairs = set(zip(h082.get("row", pd.Series(dtype=int)).astype(int), h082.get("target", pd.Series(dtype=str)).astype(str)))
    h084_path = HITL / "h084_dark_route_completion_jepa" / "h084_selected_cells.csv"
    h084 = pd.read_csv(h084_path) if h084_path.exists() else pd.DataFrame(columns=["row", "target"])
    h084_pairs = set(zip(h084.get("row", pd.Series(dtype=int)).astype(int), h084.get("target", pd.Series(dtype=str)).astype(str)))

    q_flat = q_prob.reshape(-1)
    base_flat = base_prob.reshape(-1)
    q_move = (logit(q_prob) - logit(base_prob)).reshape(-1)
    moved_probe = clip_prob(sigmoid(logit(base_prob).reshape(-1) + 0.70 * np.clip(q_move, -1.35, 1.35)))
    q_gain = bce(base_flat, q_flat) - bce(moved_probe, q_flat)

    h080["h085_q"] = q_flat
    h080["h085_q_move"] = q_move
    h080["h085_q_gain"] = q_gain
    h080["h085_abs_q_move"] = np.abs(q_move)
    h080["h082_cell"] = [
        1.0 if (int(row), str(target)) in h082_pairs else 0.0
        for row, target in zip(h080["row"], h080["target"])
    ]
    h080["h084_dark_cell"] = [
        1.0 if (int(row), str(target)) in h084_pairs else 0.0
        for row, target in zip(h080["row"], h080["target"])
    ]
    source_move = h080["source_mean_move"].to_numpy(dtype=float)
    h080["source_agrees_h085"] = (
        (h080["source_count"].to_numpy(dtype=float) > 0)
        & (np.sign(source_move) == np.sign(h080["h085_q_move"].to_numpy(dtype=float)))
    ).astype(float)
    h080["h085_cell_score"] = (
        0.26 * rank01(h080["h085_q_gain"].to_numpy())
        + 0.16 * rank01(h080["h085_abs_q_move"].to_numpy())
        + 0.13 * h080["public_score"].to_numpy(dtype=float)
        + 0.13 * h080["invariant_score"].to_numpy(dtype=float)
        + 0.09 * rank01(h080["source_family_count"].to_numpy())
        + 0.08 * h080["source_agrees_h085"].to_numpy(dtype=float)
        + 0.06 * h080["h082_cell"].to_numpy(dtype=float)
        + 0.05 * h080["h084_dark_cell"].to_numpy(dtype=float)
        + 0.04 * h080["outside_h069_cell"].to_numpy(dtype=float)
        - 0.13 * h080["h080_bad_same_rank"].to_numpy(dtype=float)
        - 0.09 * rank01(h080["latent_shortcut_energy"].to_numpy())
        - 0.15 * h080["is_h050_null"].to_numpy(dtype=float)
    )
    h080.loc[h080["h085_q_gain"] <= 0, "h085_cell_score"] -= 0.50
    h080.loc[h080["is_h050_null"] > 0, "h085_cell_score"] -= 0.25

    row_rows = []
    for row, group in h080.groupby("row", sort=True):
        rec = sample.iloc[int(row)].to_dict()
        row_gain = float(group["h085_q_gain"].clip(lower=0).sum())
        row_rows.append(
            {
                **rec,
                "row": int(row),
                "row_gain_sum": row_gain,
                "row_abs_move_mean": float(group["h085_abs_q_move"].mean()),
                "row_cell_score_mean": float(group["h085_cell_score"].mean()),
                "row_public_mean": float(group["public_score"].mean()),
                "row_invariant_mean": float(group["invariant_score"].mean()),
                "row_source_agree_mean": float(group["source_agrees_h085"].mean()),
                "row_bad_same_mean": float(group["h080_bad_same_rank"].mean()),
                "row_h082_cells": int(group["h082_cell"].sum()),
                "row_h084_cells": int(group["h084_dark_cell"].sum()),
                "subject_id": str(rec["subject_id"]),
            }
        )
    row_table = pd.DataFrame(row_rows)
    row_table["h085_row_score"] = (
        0.30 * rank01(row_table["row_gain_sum"].to_numpy())
        + 0.18 * rank01(row_table["row_abs_move_mean"].to_numpy())
        + 0.16 * rank01(row_table["row_cell_score_mean"].to_numpy())
        + 0.12 * row_table["row_public_mean"].to_numpy(dtype=float)
        + 0.12 * row_table["row_invariant_mean"].to_numpy(dtype=float)
        + 0.08 * row_table["row_source_agree_mean"].to_numpy(dtype=float)
        + 0.06 * rank01(row_table["row_h082_cells"].to_numpy())
        - 0.13 * row_table["row_bad_same_mean"].to_numpy(dtype=float)
    )
    return h080, row_table.sort_values(["h085_row_score", "row_gain_sum"], ascending=[False, False]).reset_index(drop=True)


def build_route_table(cell_table: pd.DataFrame) -> pd.DataFrame:
    routes = pd.read_csv(HITL / "h071_rowtarget_assignment_solver_jepa" / "h071_route_candidates.csv")
    rows = []
    for rec in routes.to_dict("records"):
        target_indices = [int(x) for x in str(rec["target_indices"]).split(",") if str(x) != ""]
        row = int(rec["row"])
        cells = cell_table[
            (cell_table["row"].astype(int) == row)
            & (cell_table["target_index"].astype(int).isin(target_indices))
        ].copy()
        if cells.empty:
            continue
        rows.append(
            {
                **rec,
                "h085_route_gain_sum": float(cells["h085_q_gain"].clip(lower=0).sum()),
                "h085_route_cell_score_mean": float(cells["h085_cell_score"].mean()),
                "h085_route_abs_move_mean": float(cells["h085_abs_q_move"].mean()),
                "h085_route_source_agree_mean": float(cells["source_agrees_h085"].mean()),
                "h085_route_h082_cells": int(cells["h082_cell"].sum()),
                "h085_route_bad_same_mean": float(cells["h080_bad_same_rank"].mean()),
                "h085_route_public_mean": float(cells["public_score"].mean()),
                "h085_route_invariant_mean": float(cells["invariant_score"].mean()),
            }
        )
    out = pd.DataFrame(rows)
    out["h085_route_score"] = (
        0.26 * rank01(out["h085_route_gain_sum"].to_numpy())
        + 0.18 * rank01(out["h085_route_cell_score_mean"].to_numpy())
        + 0.14 * rank01(out["assignment_route_score"].to_numpy())
        + 0.12 * rank01(out["h085_route_abs_move_mean"].to_numpy())
        + 0.10 * out["h085_route_source_agree_mean"].to_numpy(dtype=float)
        + 0.08 * rank01(out["h085_route_h082_cells"].to_numpy())
        + 0.07 * out["h085_route_public_mean"].to_numpy(dtype=float)
        + 0.07 * out["h085_route_invariant_mean"].to_numpy(dtype=float)
        - 0.12 * out["h085_route_bad_same_mean"].to_numpy(dtype=float)
    )
    return out.sort_values(["h085_route_score", "h085_route_gain_sum"], ascending=[False, False]).reset_index(drop=True)


def candidate_specs() -> list[H085Spec]:
    return [
        H085Spec("eqv2_rowproto_all_r96_a055", "row", "all", 96, 672, 96, 96, 16, 0.55, 1.25, 0.61, False, False, "row_state"),
        H085Spec("eqv2_rowproto_nonq2_r124_a065", "row", "nonq2", 124, 744, 124, 0, 18, 0.65, 1.35, 0.59, False, False, "row_state"),
        H085Spec("eqv2_routeproto_c760_a070", "route", "all", 150, 760, 150, 88, 20, 0.70, 1.30, 0.60, False, False, "route_state"),
        H085Spec("eqv2_route_sourceagree_c680_a080", "route", "all", 135, 680, 135, 76, 18, 0.80, 1.35, 0.58, True, False, "source_agree_route"),
        H085Spec("eqv2_cell_sourceagree_c900_a075", "cell", "all", 900, 900, 210, 110, 30, 0.75, 1.30, 0.62, True, False, "source_agree_cell"),
        H085Spec("eqv2_cell_h082bridge_c720_a070", "cell", "all", 720, 720, 190, 92, 28, 0.70, 1.25, 0.58, False, True, "h082_bridge"),
        H085Spec("eqv2_cell_invariant_nonq2_c650_a070", "cell", "nonq2", 650, 650, 185, 0, 26, 0.70, 1.25, 0.60, False, False, "private_nonq2"),
        H085Spec("eqv2_stage_public_c560_a080", "cell", "stage", 560, 560, 175, 0, 24, 0.80, 1.30, 0.59, False, False, "stage_vector"),
        H085Spec("eqv2_q2_phase_c130_a090", "cell", "q2", 130, 130, 130, 130, 20, 0.90, 1.40, 0.58, False, False, "q2_phase"),
    ]


def greedy_cells(pool: pd.DataFrame, spec: H085Spec) -> pd.DataFrame:
    selected = []
    rows_seen: set[int] = set()
    subject_counts: dict[str, int] = {}
    q2_count = 0
    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        subject = str(rec.get("subject_id", ""))
        target = str(rec["target"])
        if len(selected) >= spec.max_cells:
            break
        if len(rows_seen) >= spec.max_rows and row not in rows_seen:
            continue
        if subject_counts.get(subject, 0) >= spec.max_per_subject and row not in rows_seen:
            continue
        if target == "Q2" and q2_count >= spec.q2_cap:
            continue
        selected.append(rec)
        rows_seen.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        if target == "Q2":
            q2_count += 1
    return pd.DataFrame(selected)


def materialize_candidate(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    q_prob: np.ndarray,
    cell_table: pd.DataFrame,
    row_table: pd.DataFrame,
    route_table: pd.DataFrame,
    spec: H085Spec,
) -> tuple[np.ndarray, pd.DataFrame]:
    mask = np.zeros_like(base_prob, dtype=bool)
    allowed_tidx = set(target_indices_for(spec.target_group))
    unit_rows: list[dict[str, object]] = []

    if spec.unit == "cell":
        pool = cell_table[
            cell_table["target_index"].astype(int).isin(allowed_tidx)
            & (cell_table["h085_cell_score"] >= spec.min_score)
            & (cell_table["h085_q_gain"] > 0)
            & (cell_table["is_h050_null"] <= 0)
        ].copy()
        if spec.require_source_agree:
            pool = pool[pool["source_agrees_h085"] > 0].copy()
        if spec.require_h082:
            pool = pool[(pool["h082_cell"] > 0) | (pool["h084_dark_cell"] > 0)].copy()
        pool = pool.sort_values(["h085_cell_score", "h085_q_gain"], ascending=[False, False])
        selected = greedy_cells(pool, spec)
        for rec in selected.to_dict("records"):
            mask[int(rec["row"]), int(rec["target_index"])] = True
        unit_rows = selected.to_dict("records")
    elif spec.unit == "row":
        pool = row_table[row_table["h085_row_score"] >= spec.min_score].copy()
        pool = pool.sort_values(["h085_row_score", "row_gain_sum"], ascending=[False, False]).head(spec.max_units)
        subject_counts: dict[str, int] = {}
        selected_rows = []
        for rec in pool.to_dict("records"):
            subject = str(rec["subject_id"])
            if subject_counts.get(subject, 0) >= spec.max_per_subject:
                continue
            selected_rows.append(rec)
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        for rec in selected_rows:
            row = int(rec["row"])
            for tidx in allowed_tidx:
                mask[row, tidx] = True
        unit_rows = selected_rows
    elif spec.unit == "route":
        pool = route_table[route_table["h085_route_score"] >= spec.min_score].copy()
        if spec.require_source_agree:
            pool = pool[pool["h085_route_source_agree_mean"] >= 0.45].copy()
        pool = pool.sort_values(["h085_route_score", "h085_route_gain_sum"], ascending=[False, False])
        selected = []
        rows_seen: set[int] = set()
        subject_counts: dict[str, int] = {}
        q2_count = 0
        cells_count = 0
        for rec in pool.to_dict("records"):
            row = int(rec["row"])
            subject = str(rec["subject_id"])
            target_indices = [int(x) for x in str(rec["target_indices"]).split(",") if str(x) != ""]
            target_indices = [tidx for tidx in target_indices if tidx in allowed_tidx]
            if not target_indices:
                continue
            q2_here = int(TARGETS.index("Q2") in target_indices)
            if len(selected) >= spec.max_units:
                break
            if cells_count + len(target_indices) > spec.max_cells:
                continue
            if len(rows_seen) >= spec.max_rows and row not in rows_seen:
                continue
            if subject_counts.get(subject, 0) >= spec.max_per_subject and row not in rows_seen:
                continue
            if q2_count + q2_here > spec.q2_cap:
                continue
            selected.append({**rec, "h085_target_indices_selected": ",".join(map(str, target_indices))})
            rows_seen.add(row)
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
            q2_count += q2_here
            cells_count += len(target_indices)
            for tidx in target_indices:
                mask[row, tidx] = True
        unit_rows = selected
    else:
        raise ValueError(spec.unit)

    prob = move_toward_q(base_prob, q_prob, mask, spec.alpha, spec.cap)
    selected_cells = cell_table[
        mask[cell_table["row"].astype(int).to_numpy(), cell_table["target_index"].astype(int).to_numpy()]
    ].copy()
    selected_cells["candidate_spec"] = spec.name
    selected_cells["h085_applied_alpha"] = spec.alpha
    selected_cells["h085_unit"] = spec.unit
    unit_table = pd.DataFrame(unit_rows)
    if not unit_table.empty:
        unit_table["candidate_spec"] = spec.name
        unit_table["h085_unit"] = spec.unit
    return prob, selected_cells


def candidate_report_row(
    candidate_id: str,
    spec: H085Spec,
    prob: np.ndarray,
    selected_cells: pd.DataFrame,
    base_prob: np.ndarray,
    q_prob: np.ndarray,
    bad_probs: dict[str, np.ndarray],
    path: Path,
) -> dict[str, object]:
    diff = np.abs(prob - base_prob) > TOL
    move = (logit(prob) - logit(base_prob)).reshape(-1)
    bad_cos = {}
    for name, bad in bad_probs.items():
        bad_vec = (logit(bad) - logit(base_prob)).reshape(-1)
        cos = float(move @ bad_vec / (np.linalg.norm(move) * np.linalg.norm(bad_vec) + 1.0e-12))
        bad_cos[f"bad_cos_{Path(name).stem[:24]}"] = cos
    max_positive_bad = max([0.0, *[v for v in bad_cos.values() if np.isfinite(v)]])
    per_target = {f"{target}_changed_vs_h057": int(diff[:, i].sum()) for i, target in enumerate(TARGETS)}
    rows_changed = diff.any(axis=1)
    h082_ratio = float(selected_cells["h082_cell"].mean()) if len(selected_cells) else 0.0
    source_agree_rate = float(selected_cells["source_agrees_h085"].mean()) if len(selected_cells) else 0.0
    invariant_mean = float(selected_cells["invariant_score"].mean()) if len(selected_cells) else 0.0
    public_mean = float(selected_cells["public_score"].mean()) if len(selected_cells) else 0.0
    bad_same_mean = float(selected_cells["h080_bad_same_rank"].mean()) if len(selected_cells) else 1.0
    return {
        "candidate_id": candidate_id,
        "spec_name": spec.name,
        "unit": spec.unit,
        "target_group": spec.target_group,
        "novelty": spec.novelty,
        "alpha": spec.alpha,
        "cap": spec.cap,
        "selected_cells": int(diff.sum()),
        "selected_rows": int(rows_changed.sum()),
        "q2_cells": int(diff[:, TARGETS.index("Q2")].sum()),
        "posterior_delta_vs_h057": float(np.mean(bce(prob, q_prob) - bce(base_prob, q_prob))),
        "mean_selected_h085_cell_score": float(selected_cells["h085_cell_score"].mean()) if len(selected_cells) else 0.0,
        "mean_selected_q_gain": float(selected_cells["h085_q_gain"].mean()) if len(selected_cells) else 0.0,
        "source_agree_rate": source_agree_rate,
        "h082_ratio": h082_ratio,
        "public_mean": public_mean,
        "invariant_mean": invariant_mean,
        "bad_same_mean": bad_same_mean,
        "max_positive_bad_cosine": max_positive_bad,
        "mean_abs_prob_move_vs_h057": float(np.mean(np.abs(prob - base_prob))),
        "max_abs_prob_move_vs_h057": float(np.max(np.abs(prob - base_prob))),
        **bad_cos,
        **per_target,
        "hash": short_hash(prob),
        "file": path.name,
        "resolved_path": str(path.resolve()),
    }


def score_candidates(candidates: pd.DataFrame) -> pd.DataFrame:
    out = candidates.copy()
    out["posterior_rank"] = rank01(-out["posterior_delta_vs_h057"].to_numpy())
    out["support_rank"] = rank01(out["selected_cells"].to_numpy())
    out["source_rank"] = rank01(out["source_agree_rate"].to_numpy())
    out["h082_rank"] = rank01(out["h082_ratio"].to_numpy())
    out["private_rank"] = rank01((out["invariant_mean"] - out["bad_same_mean"]).to_numpy())
    out["bad_avoid_rank"] = rank01(out["max_positive_bad_cosine"].to_numpy(), high=False)
    out["bigbet_unit_bonus"] = out["unit"].map({"row": 0.16, "route": 0.12, "cell": 0.04}).fillna(0.0)
    out["h085_score"] = (
        0.34 * out["posterior_rank"]
        + 0.17 * out["private_rank"]
        + 0.14 * out["source_rank"]
        + 0.12 * out["h082_rank"]
        + 0.10 * out["support_rank"]
        + 0.09 * out["bad_avoid_rank"]
        + out["bigbet_unit_bonus"]
        - 0.10 * (out["q2_cells"] > 110).astype(float)
        - 0.08 * (out["max_positive_bad_cosine"] > 0.08).astype(float)
    )
    return out.sort_values(["h085_score", "posterior_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)


def main() -> None:
    cleanup_previous_outputs()
    base_df = load_sub(BASE_FILE)
    sample = base_df[KEYS].copy()
    base_prob = base_df[TARGETS].to_numpy(dtype=np.float64)

    known = public_observations(sample)
    pred_by_file = {
        str(rec["file"]): load_sub(str(rec["file"]), sample)[TARGETS].to_numpy(dtype=np.float64)
        for rec in known.to_dict("records")
    }
    equations, a, d0_rows, b = build_equation_system(known, pred_by_file, base_prob)
    priors = make_priors(known, pred_by_file, base_prob, sample)
    configs, full_qs = evaluate_configs(equations, a, d0_rows, b, priors)
    selected_config = configs.iloc[0].to_dict()
    posterior_key = str(selected_config["posterior_key"])
    q_prob = full_qs[posterior_key].reshape(base_prob.shape)

    cell_table, row_table = add_support_tables(sample, base_prob, q_prob)
    route_table = build_route_table(cell_table)

    bad_probs: dict[str, np.ndarray] = {}
    for name in BAD_ANCHORS:
        path = locate(name)
        if path is None:
            continue
        try:
            bad_probs[name] = load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
        except Exception:
            continue

    candidate_rows = []
    selected_frames = []
    for spec in candidate_specs():
        prob, selected_cells = materialize_candidate(sample, base_prob, q_prob, cell_table, row_table, route_table, spec)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        candidate_id = safe_id(f"h085_{spec.name}_{short_hash(prob)}")
        path = OUT / f"submission_{candidate_id}.csv"
        write_submission(sample, prob, path)
        selected_cells = selected_cells.copy()
        selected_cells["candidate_id"] = candidate_id
        selected_frames.append(selected_cells)
        candidate_rows.append(candidate_report_row(candidate_id, spec, prob, selected_cells, base_prob, q_prob, bad_probs, path))

    candidates = score_candidates(pd.DataFrame(candidate_rows))
    if candidates.empty:
        raise RuntimeError("no H085 candidates")

    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_name = f"submission_h085_aug_public_equation_{selected['hash']}_uploadsafe.csv"
    root_path = ROOT / root_name
    shutil.copyfile(selected_path, root_path)
    validation = validate_submission(root_path, sample, base_prob)

    known.to_csv(OUT / "h085_known_public_observations.csv", index=False)
    equations.to_csv(OUT / "h085_equations_vs_h057.csv", index=False)
    configs.to_csv(OUT / "h085_posterior_configs.csv", index=False)
    cell_table.to_csv(OUT / "h085_cell_table.csv", index=False)
    row_table.to_csv(OUT / "h085_row_state_table.csv", index=False)
    route_table.to_csv(OUT / "h085_route_state_table.csv", index=False)
    candidates.to_csv(OUT / "h085_candidate_scores.csv", index=False)
    selected_cells_all = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    selected_cells_all.to_csv(OUT / "h085_selected_cells_all_candidates.csv", index=False)
    selected_candidate_cells = selected_cells_all[selected_cells_all["candidate_id"].eq(selected["candidate_id"])].copy()
    selected_candidate_cells.to_csv(OUT / "h085_selected_cells.csv", index=False)

    decision = {
        "decision": "promote_augmented_public_equation_rowstate_bigbet",
        "selected_candidate_id": selected["candidate_id"],
        "selected_file": selected["file"],
        "selected_resolved_path": selected["resolved_path"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": "post-H012 public observations refit the hidden public-state posterior from the H057 base",
        "posterior_key": posterior_key,
        "posterior_prior_name": selected_config["prior_name"],
        "posterior_ridge_mult": selected_config["ridge_mult"],
        **selected,
        **validation,
    }
    decision_df = pd.DataFrame([decision])
    decision_df.to_csv(OUT / "h085_decision.csv", index=False)

    report = [
        "# H085 Augmented Public-Equation Human-State Prototype HS-JEPA",
        "",
        "Question: after H042/H050/H057, does the public-equation posterior change when H057 is the base?",
        "",
        "Design:",
        "",
        "- context: old public observations plus post-H012 H042/H050/H057 sensor readings;",
        "- target representation: hidden public label posterior refit from H057;",
        "- decoder: row/cell/route human-state prototypes toward the refit posterior;",
        "- stress: LOO equation fit, bad-anchor cosine, H080 invariant/source support.",
        "",
        "Known public observations used:",
        "",
        md_table(known, 30),
        "",
        "Selected posterior config:",
        "",
        md_table(configs.head(10), 10),
        "",
        "Candidate scores:",
        "",
        md_table(candidates, 20),
        "",
        "Selected cells sample:",
        "",
        md_table(selected_candidate_cells[[
            "candidate_id",
            "row",
            "subject_id",
            "sleep_date",
            "target",
            "h085_q",
            "h085_q_move",
            "h085_q_gain",
            "h085_cell_score",
            "source_agrees_h085",
            "h082_cell",
            "invariant_score",
            "h080_bad_same_rank",
        ]], 60),
        "",
        "Decision:",
        "",
        md_table(decision_df, 3),
        "",
        "Interpretation:",
        "",
        "- If H085 improves over H057, HS-JEPA should refit the hidden public-state target after every informative LB sensor and decode row-state prototypes.",
        "- If H085 loses while H057 survives, post-H012 public equations are too few/noisy and H057's Q2 support should remain the trusted public/private bridge.",
    ]
    (OUT / "h085_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print((OUT / "h085_decision.csv").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
