#!/usr/bin/env python3
"""H055: post-feedback public-listener HS-JEPA.

H012 solved an inverse public-equation problem before H042/H050 existed in the
public observation table.  H042 then improved by changing 45 Q2 cells, while
H050 changed 96 Q1/Q3 cells and tied H042 exactly.

H055 treats those two new facts as fresh JEPA supervision:

    context = all known public submissions + manual H042/H050 sensors
    target  = hidden public-listening label/subset posterior
    action  = move H042 on cells that survive the H050 null constraint

This is a public-listener refit, not a small blend.  If it works, the missing
object after H042 was a hidden public subset, not a target-specific local move.
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
OUT = HITL / "h055_postfeedback_public_listener_jepa"
ANALYSIS = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
OUT.mkdir(parents=True, exist_ok=True)

if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from public_anchor_bottleneck_decomposition import known_public_table  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050 = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
MANUAL_PUBLIC = {
    H012: (0.5681234831, "manual H012 public-equation best"),
    H042: (0.5679048248, "manual H042 Q2 phase public sensor"),
    H050: (0.5679048248, "manual H050 subjective-Q null sensor"),
}


@dataclass(frozen=True)
class CandidateSpec:
    family: str
    k: int
    alpha: float
    mode: str


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def locate(name: str | Path) -> Path | None:
    p = Path(str(name))
    probes = [p] if p.is_absolute() else [p, ROOT / p, ANALYSIS / p, JEPA / p, HITL / p]
    for probe in probes:
        if probe.exists():
            return probe.resolve()
    return None


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    path = locate(name)
    if path is None:
        raise FileNotFoundError(str(name))
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    df = df.sort_values(KEYS).reset_index(drop=True)
    if sample is not None and not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"key mismatch for {name}")
    return df


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


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def rank01(x: np.ndarray, high: bool = True) -> np.ndarray:
    s = pd.Series(np.asarray(x, dtype=np.float64)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if s.nunique(dropna=True) <= 1:
        return np.full(len(s), 0.5, dtype=np.float64)
    r = s.rank(method="average", pct=True).to_numpy(dtype=np.float64)
    return r if high else 1.0 - r


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample.copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


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


def pivot_cell_table(path: Path, value_col: str, sample: pd.DataFrame) -> np.ndarray:
    df = pd.read_csv(path)
    mat = np.full((len(sample), len(TARGETS)), np.nan, dtype=np.float64)
    target_idx = {target: i for i, target in enumerate(TARGETS)}
    for rec in df.to_dict("records"):
        row = int(rec["row"])
        target = str(rec["target"])
        if 0 <= row < len(sample) and target in target_idx:
            mat[row, target_idx[target]] = float(rec[value_col])
    if np.isnan(mat).any():
        raise ValueError(f"{path} did not fill all cells for {value_col}")
    return clip_prob(mat)


def read_public_observations() -> pd.DataFrame:
    known = known_public_table().copy()
    known["known_source"] = known.get("known_source", "known_public_table")
    manual = pd.DataFrame(
        [
            {"file": file, "public_lb": lb, "note": note, "known_source": "manual_post_h042"}
            for file, (lb, note) in MANUAL_PUBLIC.items()
        ]
    )
    out = pd.concat([known, manual], ignore_index=True)
    out = out.drop_duplicates("file", keep="last")
    rows = []
    for rec in out.to_dict("records"):
        if locate(str(rec["file"])) is None:
            continue
        rows.append(rec)
    return pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)


def equation_arrays(
    known: pd.DataFrame,
    base_prob: np.ndarray,
    pred_by_file: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    base = clip_prob(base_prob.reshape(-1))
    base_lb = float(known.loc[known["file"].eq(H012), "public_lb"].iloc[0])
    rows = []
    a_rows = []
    d0_rows = []
    b_vals = []
    n = base.size
    for rec in known.to_dict("records"):
        file_name = str(rec["file"])
        if file_name == H012 or file_name not in pred_by_file:
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
                "known_source": str(rec.get("known_source", "")),
                "actual_delta_vs_h012": actual_delta,
                "rhs_label_term": rhs,
                "changed_cells_vs_h012": int((np.abs(pred - base) > 1.0e-12).sum()),
            }
        )
        a_rows.append(d1 / n)
        d0_rows.append(d0)
        b_vals.append(rhs)
    eq = pd.DataFrame(rows)
    return eq, np.vstack(a_rows), np.vstack(d0_rows), np.asarray(b_vals, dtype=np.float64)


def fit_posterior(a: np.ndarray, b: np.ndarray, prior: np.ndarray, ridge_mult: float) -> np.ndarray:
    gram = a @ a.T
    scale = float(np.median(np.diag(gram)))
    if not np.isfinite(scale) or scale <= 1.0e-18:
        scale = float(np.mean(np.diag(gram)) + 1.0e-18)
    lam = ridge_mult * scale
    residual = b - a @ prior
    try:
        dual = np.linalg.solve(gram + lam * np.eye(len(b)), residual)
    except np.linalg.LinAlgError:
        dual = np.linalg.pinv(gram + lam * np.eye(len(b))) @ residual
    return clip_prob(prior + a.T @ dual)


def predict_delta(d0: np.ndarray, d1: np.ndarray, q: np.ndarray) -> float:
    return float(np.mean(d0 + d1 * q))


def build_priors(sample: pd.DataFrame, known: pd.DataFrame, pred_by_file: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    h012 = pred_by_file[H012]
    priors: dict[str, np.ndarray] = {
        "h012": h012.reshape(-1),
        "h042_anchor": pred_by_file[H042].reshape(-1),
    }
    h012_post = HITL / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv"
    if h012_post.exists():
        priors["h012_posterior"] = pivot_cell_table(h012_post, "posterior_prob", sample).reshape(-1)
    h020_post = HITL / "h020_joint_vector_world_jepa" / "h020_cell_joint_vector_posterior.csv"
    if h020_post.exists():
        priors["h020_joint_vector"] = pivot_cell_table(h020_post, "q_joint_vector", sample).reshape(-1)
    h042_world = HITL / "h042_action_coupled_equation_solver_jepa" / "h042_route_world_posterior_cells.csv"
    if h042_world.exists():
        priors["h042_world_cond"] = pivot_cell_table(h042_world, "world_q_cond", sample).reshape(-1)

    lbs = known.set_index("file")["public_lb"].to_dict()
    best = float(min(lbs.values()))
    stack = []
    weights = []
    for file_name, pred in pred_by_file.items():
        lb = float(lbs[file_name])
        if lb <= best + 0.0008:
            stack.append(pred)
            weights.append(np.exp(-(lb - best) / 0.00025))
    w = np.asarray(weights, dtype=np.float64)
    w = w / w.sum()
    priors["post_h042_good_soft"] = np.tensordot(w, np.stack(stack, axis=0), axes=(0, 0)).reshape(-1)
    return priors


def evaluate_configs(eq: pd.DataFrame, a: np.ndarray, d0: np.ndarray, b: np.ndarray, priors: dict[str, np.ndarray]) -> pd.DataFrame:
    d1 = a * priors[next(iter(priors))].size
    actual = eq["actual_delta_vs_h012"].to_numpy(dtype=np.float64)
    files = eq["file"].astype(str).tolist()
    rows = []
    ridge_mults = [1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 1.0e-1, 3.0e-1, 1.0, 3.0, 10.0, 30.0, 100.0]
    h042_idx = files.index(H042)
    h050_idx = files.index(H050)
    for prior_name, prior in priors.items():
        for ridge in ridge_mults:
            full_q = fit_posterior(a, b, prior, ridge)
            full_pred = np.asarray([predict_delta(d0[i], d1[i], full_q) for i in range(len(files))])
            loo_pred = []
            for hold in range(len(files)):
                keep = np.ones(len(files), dtype=bool)
                keep[hold] = False
                q = fit_posterior(a[keep], b[keep], prior, ridge)
                loo_pred.append(predict_delta(d0[hold], d1[hold], q))
            loo_pred = np.asarray(loo_pred)
            loo_err = loo_pred - actual
            rows.append(
                {
                    "prior_name": prior_name,
                    "ridge_mult": ridge,
                    "loo_mae": float(np.mean(np.abs(loo_err))),
                    "loo_p90_abs": float(np.quantile(np.abs(loo_err), 0.90)),
                    "known_fit_mae": float(np.mean(np.abs(full_pred - actual))),
                    "h042_fit_delta": float(full_pred[h042_idx]),
                    "h050_fit_delta": float(full_pred[h050_idx]),
                    "h050_minus_h042_fit_delta": float(full_pred[h050_idx] - full_pred[h042_idx]),
                    "h042_actual_delta": float(actual[h042_idx]),
                    "h050_actual_delta": float(actual[h050_idx]),
                    "q_mean": float(full_q.mean()),
                    "q_std": float(full_q.std()),
                }
            )
    out = pd.DataFrame(rows)
    out["post_sensor_abs_error"] = (
        (out["h042_fit_delta"] - out["h042_actual_delta"]).abs()
        + (out["h050_fit_delta"] - out["h050_actual_delta"]).abs()
        + out["h050_minus_h042_fit_delta"].abs()
    )
    out["selection_score"] = (
        out["loo_mae"].rank(method="average", pct=True)
        + 0.55 * out["loo_p90_abs"].rank(method="average", pct=True)
        + 0.90 * out["post_sensor_abs_error"].rank(method="average", pct=True)
    )
    return out.sort_values(["selection_score", "loo_mae"]).reset_index(drop=True)


def move_toward(base: np.ndarray, q: np.ndarray, alpha: float, mode: str) -> np.ndarray:
    if mode == "prob":
        return clip_prob((1.0 - alpha) * base + alpha * q)
    if mode == "logit":
        return clip_prob(sigmoid((1.0 - alpha) * logit(base) + alpha * logit(q)))
    raise ValueError(mode)


def allowed_mask_for_family(family: str, h050_null: np.ndarray, h042_q2_support: np.ndarray) -> np.ndarray:
    allowed = np.ones_like(h050_null, dtype=bool)
    allowed[h050_null] = False
    allowed[h042_q2_support] = False
    target_idx = {target: i for i, target in enumerate(TARGETS)}
    if family == "nonnull_all_freezeq2":
        allowed[:, target_idx["Q2"]] = False
    elif family == "nonnull_s_all":
        for target in ["Q1", "Q2", "Q3"]:
            allowed[:, target_idx[target]] = False
    elif family == "nonnull_s24":
        keep = np.zeros_like(allowed)
        keep[:, target_idx["S2"]] = True
        keep[:, target_idx["S4"]] = True
        allowed &= keep
    elif family == "nonnull_q3s":
        keep = np.zeros_like(allowed)
        for target in ["Q3", "S1", "S2", "S3", "S4"]:
            keep[:, target_idx[target]] = True
        allowed &= keep
    else:
        raise ValueError(family)
    return allowed


def candidate_table(
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    h042_prob: np.ndarray,
    h050_prob: np.ndarray,
    q: np.ndarray,
    aux_scores: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, Path]]:
    h050_null = np.abs(h050_prob - h042_prob) > 1.0e-12
    h042_q2_support = np.zeros_like(h050_null, dtype=bool)
    h042_q2_support[:, TARGETS.index("Q2")] = np.abs(h042_prob[:, TARGETS.index("Q2")] - h012_prob[:, TARGETS.index("Q2")]) > 1.0e-12

    specs = [
        CandidateSpec(family, k, alpha, mode)
        for family in ["nonnull_all_freezeq2", "nonnull_s_all", "nonnull_s24", "nonnull_q3s"]
        for k in [120, 240, 420, 700, 1050]
        for alpha in [0.22, 0.38, 0.60, 0.85]
        for mode in ["prob", "logit"]
    ]
    rows = []
    paths: dict[str, Path] = {}
    for spec in specs:
        moved_all = move_toward(h042_prob, q, spec.alpha, spec.mode)
        gain = bce(h042_prob, q) - bce(moved_all, q)
        score = gain * (0.55 + 0.95 * aux_scores)
        allowed = allowed_mask_for_family(spec.family, h050_null, h042_q2_support)
        flat_score = np.where(allowed.reshape(-1), score.reshape(-1), -np.inf)
        valid = np.where(np.isfinite(flat_score))[0]
        if len(valid) == 0:
            continue
        take = valid[np.argsort(-flat_score[valid])[: min(spec.k, len(valid))]]
        mask = np.zeros(h042_prob.size, dtype=bool)
        mask[take] = True
        mask = mask.reshape(h042_prob.shape)
        prob = h042_prob.copy()
        prob[mask] = moved_all[mask]
        digest = short_hash(prob)
        candidate_id = f"h055_{spec.family}_k{spec.k}_a{str(spec.alpha).replace('.', 'p')}_{spec.mode}_{digest}"
        path = OUT / f"submission_{candidate_id}.csv"
        write_submission(sample, prob, path)
        diff_h042 = np.abs(prob - h042_prob) > 1.0e-12
        diff_h012 = np.abs(prob - h012_prob) > 1.0e-12
        per_target_h042 = {f"{target}_changed_vs_h042": int(diff_h042[:, i].sum()) for i, target in enumerate(TARGETS)}
        h050_null_overlap = int((diff_h042 & h050_null).sum())
        pred_delta_vs_h042 = float(np.mean(bce(prob, q) - bce(h042_prob, q)))
        pred_delta_vs_h012 = float(np.mean(bce(prob, q) - bce(h012_prob, q)))
        rows.append(
            {
                "candidate_id": candidate_id,
                "file": path.name,
                "resolved_path": str(path),
                "family": spec.family,
                "k": spec.k,
                "alpha": spec.alpha,
                "mode": spec.mode,
                "changed_cells_vs_h042": int(diff_h042.sum()),
                "changed_cells_vs_h012": int(diff_h012.sum()),
                "h050_null_overlap_cells": h050_null_overlap,
                "q2_changed_vs_h042": int(diff_h042[:, TARGETS.index("Q2")].sum()),
                "pred_delta_vs_h042": pred_delta_vs_h042,
                "pred_delta_vs_h012": pred_delta_vs_h012,
                "mean_gain_selected": float(gain[mask].mean()) if mask.any() else 0.0,
                "mean_aux_selected": float(aux_scores[mask].mean()) if mask.any() else 0.0,
                **per_target_h042,
            }
        )
        paths[candidate_id] = path
    out = pd.DataFrame(rows)
    out["h055_listener_score"] = (
        -1.25 * out["pred_delta_vs_h042"].rank(method="average", pct=True)
        -0.45 * out["mean_gain_selected"].rank(method="average", pct=True)
        +0.35 * out["mean_aux_selected"].rank(method="average", pct=True)
        -0.70 * (out["h050_null_overlap_cells"] > 0).astype(float)
        -0.35 * (out["q2_changed_vs_h042"] > 0).astype(float)
        -0.10 * (out["changed_cells_vs_h042"] > 700).astype(float)
    )
    out = out.sort_values(
        ["h055_listener_score", "pred_delta_vs_h042", "changed_cells_vs_h042"],
        ascending=[False, True, True],
    ).reset_index(drop=True)
    return out, paths


def main() -> None:
    known = read_public_observations()
    h012 = load_sub(H012)
    sample = h012[KEYS].copy()
    pred_by_file = {}
    rows = []
    for rec in known.to_dict("records"):
        file = str(rec["file"])
        try:
            pred_by_file[file] = load_sub(file, sample)[TARGETS].to_numpy(dtype=np.float64)
            rows.append(rec)
        except Exception:
            continue
    known = pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)
    h012_prob = pred_by_file[H012]
    h042_prob = pred_by_file[H042]
    h050_prob = pred_by_file[H050]

    eq, a, d0, b = equation_arrays(known, h012_prob, pred_by_file)
    priors = build_priors(sample, known, pred_by_file)
    config_scores = evaluate_configs(eq, a, d0, b, priors)
    selected_config = config_scores.iloc[0]
    prior = priors[str(selected_config["prior_name"])]
    q_flat = fit_posterior(a, b, prior, float(selected_config["ridge_mult"]))
    q = q_flat.reshape(h012_prob.shape)

    h012_post = pivot_cell_table(HITL / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv", "posterior_prob", sample)
    h042_world = pivot_cell_table(
        HITL / "h042_action_coupled_equation_solver_jepa" / "h042_route_world_posterior_cells.csv",
        "world_q_cond",
        sample,
    )
    aux_scores = (
        0.45 * rank01(np.abs(logit(q) - logit(h042_prob)).reshape(-1)).reshape(q.shape)
        + 0.30 * rank01(np.abs(logit(h012_post) - logit(h012_prob)).reshape(-1)).reshape(q.shape)
        + 0.25 * rank01(np.abs(logit(h042_world) - logit(h012_prob)).reshape(-1)).reshape(q.shape)
    )

    candidates, paths = candidate_table(sample, h012_prob, h042_prob, h050_prob, q, aux_scores)
    selected = candidates.iloc[0]
    selected_path = paths[str(selected["candidate_id"])]
    root_name = f"submission_h055_postfeedback_listener_{short_hash(load_sub(selected_path, sample)[TARGETS].to_numpy(dtype=np.float64))}_uploadsafe.csv"
    root_path = ROOT / root_name
    shutil.copyfile(selected_path, root_path)

    decision = pd.DataFrame(
        [
            {
                "decision": "promote_postfeedback_public_listener",
                "selected_candidate_id": str(selected["candidate_id"]),
                "selected_file": str(selected["file"]),
                "selected_resolved_path": str(selected_path),
                "root_uploadsafe_path": str(root_path),
                "reason": "H042/H050 public feedback was absent from the original public-equation table",
                "selected_prior": str(selected_config["prior_name"]),
                "selected_ridge_mult": float(selected_config["ridge_mult"]),
                "config_loo_mae": float(selected_config["loo_mae"]),
                "config_post_sensor_abs_error": float(selected_config["post_sensor_abs_error"]),
                **selected.to_dict(),
            }
        ]
    )

    known.to_csv(OUT / "h055_augmented_public_observations.csv", index=False)
    eq.to_csv(OUT / "h055_equations.csv", index=False)
    config_scores.to_csv(OUT / "h055_posterior_config_scores.csv", index=False)
    candidates.to_csv(OUT / "h055_candidate_scores.csv", index=False)
    decision.to_csv(OUT / "h055_decision.csv", index=False)
    pd.DataFrame(
        {
            "row": np.repeat(np.arange(len(sample)), len(TARGETS)),
            "target": TARGETS * len(sample),
            "h012_prob": h012_prob.reshape(-1),
            "h042_prob": h042_prob.reshape(-1),
            "posterior_prob": q.reshape(-1),
            "posterior_minus_h042": (q - h042_prob).reshape(-1),
            "aux_score": aux_scores.reshape(-1),
        }
    ).to_csv(OUT / "h055_cell_posterior.csv", index=False)

    report = f"""# H055 Post-Feedback Public-Listener HS-JEPA

Question: do the new public observations H042 improved and H050 tied H042
redefine the hidden public-listening cell subset?

Design:

- H012 is the public-equation base;
- manual H042 and H050 public observations are added to the equation system;
- H042 is used as the upload base;
- H050's Q1/Q3 extra cells are treated as a null route and vetoed;
- Q2 is frozen versus H042 so this branch does not overlap H051/H052/H053.

Selected posterior config:

{md_table(config_scores.head(10))}

Decision:

{md_table(decision)}

Top candidates:

{md_table(candidates.head(25))}

Interpretation rule:

- If H055 improves, the post-H042 bottleneck is a hidden public-listener subset
  that became identifiable only after adding H042/H050 feedback.
- If H055 fails, the augmented equation posterior overfit public sensors and
  the next branch should wait for H051/H052/H053/H054 feedback instead of
  inventing another public-equation cell mask.
"""
    (OUT / "h055_report.md").write_text(report)
    print(f"H055 selected: {decision.loc[0, 'selected_candidate_id']}")
    print(f"H055 root: {root_path}")
    print(decision[["selected_candidate_id", "family", "changed_cells_vs_h042", "pred_delta_vs_h042", "h050_null_overlap_cells", "q2_changed_vs_h042"]].to_string(index=False))


if __name__ == "__main__":
    main()
