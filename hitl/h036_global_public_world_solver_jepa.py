#!/usr/bin/env python3
"""H036: global public-world solver HS-JEPA.

H012 was the jackpot because it treated public LB observations as equations in
hidden public labels.  H035 showed that local edits around H012 are mostly
locked: support swaps can improve a local proxy but fail the route/action-health
stress tests.

H036 changes the target.  It does not ask "which H012 cells should I tweak?".
It asks whether all known public observations can be explained by a sampled
hidden public world:

    context = known submissions and their public LB deltas around H012
    target  = latent public subset + row/target binary label world
    action  = move H012 toward the posterior cells implied by top worlds

If this is real, the best particles should beat permutation nulls by a wide
margin and produce a candidate that survives H024/H025 stress.  If not, the
global public-world story is not enough to justify a post-H012 jump.
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
OUT = HITL / "h036_global_public_world_solver_jepa"
ANALYSIS = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
GPT_SUBS = ROOT / "gpt_pro_pack" / "q2s1_hidden_state_translation" / "submissions"
OUT.mkdir(parents=True, exist_ok=True)

if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from public_anchor_bottleneck_decomposition import known_public_table  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H012_LB = 0.5681234831
E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"


@dataclass(frozen=True)
class WorldConfig:
    q_source: str
    row_prior: str
    subset_size: int
    label_mode: str
    particles: int


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def locate(name: str | Path) -> Path | None:
    path = Path(str(name))
    probes: list[Path] = []
    if path.is_absolute():
        probes.append(path)
    else:
        probes.extend(
            [
                path,
                ROOT / path,
                ANALYSIS / path,
                JEPA / path,
                HITL / path,
                GPT_SUBS / path.name,
            ]
        )
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


def binary_loss(prob: np.ndarray, y: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    yy = np.asarray(y, dtype=np.float64)
    return -(yy * np.log(p) + (1.0 - yy) * np.log(1.0 - p))


def rank01(x: np.ndarray | pd.Series) -> np.ndarray:
    s = pd.Series(np.asarray(x, dtype=np.float64))
    if s.nunique(dropna=True) <= 1:
        return np.full(len(s), 0.5, dtype=np.float64)
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


def normalize_prior(x: np.ndarray, floor: float = 0.03, power: float = 1.0) -> np.ndarray:
    arr = np.asarray(x, dtype=np.float64)
    arr = np.nan_to_num(arr, nan=np.nanmedian(arr[np.isfinite(arr)]) if np.isfinite(arr).any() else 0.0)
    r = rank01(arr)
    p = floor + np.power(np.clip(r, 0.0, 1.0), power)
    p = np.clip(p, floor, None)
    return p / p.sum()


def safe_id(text: str, limit: int = 92) -> str:
    keep = []
    for ch in str(text):
        keep.append(ch if ch.isalnum() or ch in "._-" else "_")
    return "".join(keep).strip("_")[:limit].strip("_")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(prob, 12).tobytes()).hexdigest()[:8]


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


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample.copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


def pivot_cell_table(path: Path, value_col: str, sample: pd.DataFrame) -> np.ndarray:
    df = pd.read_csv(path)
    need = {"row", "target", value_col}
    if not need.issubset(df.columns):
        raise ValueError(f"{path} missing {need - set(df.columns)}")
    mat = np.full((len(sample), len(TARGETS)), np.nan, dtype=np.float64)
    target_idx = {t: i for i, t in enumerate(TARGETS)}
    for rec in df[["row", "target", value_col]].to_dict("records"):
        row = int(rec["row"])
        target = str(rec["target"])
        if 0 <= row < len(sample) and target in target_idx:
            mat[row, target_idx[target]] = float(rec[value_col])
    if np.isnan(mat).any():
        raise ValueError(f"{path} did not fill all cells for {value_col}")
    return clip_prob(mat)


def read_public_observations() -> pd.DataFrame:
    known = known_public_table().copy()
    if H012 not in set(known["file"].astype(str)):
        known = pd.concat(
            [
                known,
                pd.DataFrame(
                    [{"file": H012, "public_lb": H012_LB, "note": "manual H012 best", "known_source": "manual"}]
                ),
            ],
            ignore_index=True,
        )
    rows = []
    for rec in known.to_dict("records"):
        file_name = str(rec["file"])
        if locate(file_name) is None:
            continue
        rows.append(
            {
                "file": file_name,
                "public_lb": float(rec["public_lb"]),
                "note": str(rec.get("note", "")),
                "known_source": str(rec.get("known_source", "")),
            }
        )
    return pd.DataFrame(rows).drop_duplicates("file", keep="last").sort_values("public_lb").reset_index(drop=True)


def load_system() -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, dict[str, np.ndarray]]:
    h012 = load_sub(H012)
    sample = h012[KEYS].copy()
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    known = read_public_observations()
    pred_by_file: dict[str, np.ndarray] = {}
    rows = []
    for rec in known.to_dict("records"):
        file_name = str(rec["file"])
        try:
            df = load_sub(file_name, sample)
        except Exception:
            continue
        pred_by_file[file_name] = clip_prob(df[TARGETS].to_numpy(dtype=np.float64))
        rows.append(rec)
    known = pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)
    if H012 not in pred_by_file:
        raise RuntimeError("H012 missing from public system")
    return known, sample, h012_prob, pred_by_file


def build_q_sources(sample: pd.DataFrame, h012_prob: np.ndarray) -> dict[str, np.ndarray]:
    sources: dict[str, np.ndarray] = {"h012": h012_prob}
    tables = [
        ("h012posterior", HITL / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv", "posterior_prob"),
        ("h015feedback", HITL / "h015_public_equation_self_feedback" / "h015_cell_posterior.csv", "posterior_prob"),
        ("h017joint", HITL / "h017_joint_label_weight_jepa" / "h017_cell_joint_state.csv", "joint_q_median"),
        ("h018hard", HITL / "h018_hard_label_world_jepa" / "h018_cell_hard_posterior.csv", "q_hard"),
        ("h020vector", HITL / "h020_joint_vector_world_jepa" / "h020_cell_joint_vector_posterior.csv", "q_joint_vector"),
    ]
    for name, path, col in tables:
        if path.exists():
            sources[name] = pivot_cell_table(path, col, sample)
    if locate(E247) is not None:
        sources["e247"] = load_sub(E247, sample)[TARGETS].to_numpy(dtype=np.float64)
    # Two deliberately nonlocal mixtures.  They are not candidates by themselves;
    # they create alternate latent-world priors for the sampler.
    if "h012posterior" in sources and "h020vector" in sources:
        sources["posterior_vector_mid"] = clip_prob(0.55 * sources["h012posterior"] + 0.45 * sources["h020vector"])
    if "h017joint" in sources and "h018hard" in sources:
        sources["joint_hard_mid"] = clip_prob(0.50 * sources["h017joint"] + 0.50 * sources["h018hard"])
    return sources


def row_mean_from_cell(path: Path, col: str, sample: pd.DataFrame) -> np.ndarray | None:
    if not path.exists():
        return None
    try:
        mat = pivot_cell_table(path, col, sample)
    except Exception:
        return None
    return np.nanmean(mat, axis=1)


def build_row_priors(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    n = len(sample)
    priors: dict[str, np.ndarray] = {"uniform": np.full(n, 1.0 / n, dtype=np.float64)}

    h019 = HITL / "h019_row_subset_hardworld_jepa" / "h019_row_public_posterior.csv"
    if h019.exists():
        df = pd.read_csv(h019)
        for col in ["inclusion_prob", "row_score", "row_weight", "mean_abs_logit_move_to_proxy"]:
            if col in df.columns and len(df) == n:
                priors[f"h019_{col}"] = normalize_prior(df[col].to_numpy(dtype=np.float64), power=1.2)

    h030 = HITL / "h030_rowtarget_identity_equation_jepa" / "h030_cell_identity_state.csv"
    if h030.exists():
        df = pd.read_csv(h030)
        for col in [
            "score_identity_combo",
            "score_no_h012_combo",
            "score_public_row_subset",
            "score_joint_vector_row",
            "score_memory_public_combo",
        ]:
            if col in df.columns:
                row_score = df.groupby("row")[col].mean().reindex(range(n)).to_numpy(dtype=np.float64)
                priors[f"h030_{col}"] = normalize_prior(row_score, power=1.35)

    h035 = HITL / "h035_basin_boundary_solver_jepa" / "h035_cell_state.csv"
    if h035.exists():
        df = pd.read_csv(h035)
        for col in [
            "route_translator_score",
            "score_public_row_subset",
            "score_identity_combo",
            "private_safe_score",
            "drop_memory_conflict_score",
            "add_no_h012_score",
        ]:
            if col in df.columns:
                row_score = df.groupby("row")[col].mean().reindex(range(n)).to_numpy(dtype=np.float64)
                priors[f"h035_{col}"] = normalize_prior(row_score, power=1.25)

    # Calendar/social state does not determine public membership, but it tests a
    # very different public-subset story than posterior-only rows.
    features_path = HITL / "h013_raw_human_state_jepa_gate" / "h013_human_state_features.csv"
    if features_path.exists():
        feat = pd.read_csv(features_path, parse_dates=["sleep_date", "lifelog_date"])
        test = feat[feat["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
        if len(test) == n and test[KEYS].equals(sample[KEYS]):
            for prefix, tokens in {
                "calendar_pay_weekend": ("payday", "weekend", "month_start", "month_end", "weekday"),
                "late_social_phone": ("usage_late_", "usage_prebed_", "usage_cat_chat", "usage_cat_call"),
                "body_calendar": ("pedo_", "m_activity", "w_hr", "weekday", "weekend"),
            }.items():
                cols = [
                    c
                    for c in test.columns
                    if any(tok in c for tok in tokens) and pd.api.types.is_numeric_dtype(test[c])
                ]
                if cols:
                    arr = test[cols].fillna(test[cols].median(numeric_only=True)).to_numpy(dtype=np.float64)
                    score = np.nanmean(np.abs((arr - np.nanmedian(arr, axis=0)) / (np.nanstd(arr, axis=0) + 1.0e-9)), axis=1)
                    priors[f"h013_{prefix}"] = normalize_prior(score, power=1.15)
    return priors


def build_delta_tensors(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    h012_prob: np.ndarray,
) -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray]:
    files = [f for f in known["file"].astype(str).tolist() if f != H012 and f in pred_by_file]
    d0_rows = []
    d1_adj = []
    actual = []
    h012 = clip_prob(h012_prob)
    z_h012 = logit(h012)
    lb_by_file = known.set_index("file")["public_lb"].to_dict()
    for file_name in files:
        p = clip_prob(pred_by_file[file_name])
        d0 = -np.log(1.0 - p) + np.log(1.0 - h012)
        adj = z_h012 - logit(p)
        d0_rows.append(d0.sum(axis=1))
        d1_adj.append(adj)
        actual.append(float(lb_by_file[file_name]) - H012_LB)
    return files, np.stack(d0_rows, axis=0), np.stack(d1_adj, axis=0), np.asarray(actual, dtype=np.float64)


def spearman_fast(preds: np.ndarray, y: np.ndarray) -> np.ndarray:
    y_rank = rank01(y)
    y_center = y_rank - y_rank.mean()
    y_norm = np.linalg.norm(y_center) + 1.0e-12
    ranks = np.apply_along_axis(rank01, 1, preds)
    ranks = ranks - ranks.mean(axis=1, keepdims=True)
    denom = np.linalg.norm(ranks, axis=1) * y_norm + 1.0e-12
    return (ranks @ y_center) / denom


def sample_worlds(
    configs: list[WorldConfig],
    q_sources: dict[str, np.ndarray],
    row_priors: dict[str, np.ndarray],
    d0_rows: np.ndarray,
    d1_adj: np.ndarray,
    actual_delta: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(2036036)
    n_files, n_rows = d0_rows.shape
    n_targets = len(TARGETS)
    all_masks: list[np.ndarray] = []
    all_labels: list[np.ndarray] = []
    all_preds: list[np.ndarray] = []
    rows: list[dict[str, object]] = []
    global_idx = 0

    for cfg in configs:
        q = clip_prob(q_sources[cfg.q_source])
        prior = np.asarray(row_priors[cfg.row_prior], dtype=np.float64)
        prior = np.clip(prior, 1.0e-12, None)
        prior = prior / prior.sum()
        size = min(max(8, cfg.subset_size), n_rows)
        masks = np.zeros((cfg.particles, n_rows), dtype=bool)
        labels = np.zeros((cfg.particles, n_rows, n_targets), dtype=bool)
        for w in range(cfg.particles):
            chosen = rng.choice(n_rows, size=size, replace=False, p=prior)
            masks[w, chosen] = True
            if cfg.label_mode == "map":
                labels[w, chosen, :] = q[chosen, :] >= 0.5
            elif cfg.label_mode == "temperature_sample":
                z = 0.82 * logit(q[chosen, :])
                qq = sigmoid(z)
                labels[w, chosen, :] = rng.random((size, n_targets)) < qq
            else:
                labels[w, chosen, :] = rng.random((size, n_targets)) < q[chosen, :]

        denom = masks.sum(axis=1).astype(np.float64) * n_targets
        base = masks.astype(np.float64) @ d0_rows.T
        add = np.einsum("wr,wrt,frt->wf", masks.astype(np.float64), labels.astype(np.float64), d1_adj, optimize=True)
        preds = (base + add) / denom[:, None]
        err = preds - actual_delta[None, :]
        mae = np.mean(np.abs(err), axis=1)
        rmse = np.sqrt(np.mean(err**2, axis=1))
        max_abs = np.max(np.abs(err), axis=1)
        rho = spearman_fast(preds, actual_delta)
        for i in range(cfg.particles):
            rows.append(
                {
                    "particle": global_idx + i,
                    "q_source": cfg.q_source,
                    "row_prior": cfg.row_prior,
                    "subset_size": size,
                    "label_mode": cfg.label_mode,
                    "mae": float(mae[i]),
                    "rmse": float(rmse[i]),
                    "max_abs": float(max_abs[i]),
                    "spearman": float(rho[i]),
                    "mean_pred_delta": float(preds[i].mean()),
                    "std_pred_delta": float(preds[i].std()),
                }
            )
        global_idx += cfg.particles
        all_masks.append(masks)
        all_labels.append(labels)
        all_preds.append(preds.astype(np.float32))

    particle_df = pd.DataFrame(rows).sort_values("mae").reset_index(drop=True)
    masks_all = np.concatenate(all_masks, axis=0)
    labels_all = np.concatenate(all_labels, axis=0)
    preds_all = np.concatenate(all_preds, axis=0)
    return particle_df, masks_all, labels_all, preds_all


def permutation_null(preds: np.ndarray, actual_delta: np.ndarray, n_perm: int = 300) -> pd.DataFrame:
    rng = np.random.default_rng(2036037)
    rows = []
    for i in range(n_perm):
        y = rng.permutation(actual_delta)
        err = np.mean(np.abs(preds - y[None, :]), axis=1)
        rows.append({"perm": i, "best_null_mae": float(err.min()), "median_null_mae": float(np.median(err))})
    return pd.DataFrame(rows)


def posterior_from_worlds(
    particle_df: pd.DataFrame,
    masks: np.ndarray,
    labels: np.ndarray,
    h012_prob: np.ndarray,
    top_n: int = 1600,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, pd.DataFrame]:
    top = particle_df.nsmallest(min(top_n, len(particle_df)), "mae").copy()
    idx = top["particle"].to_numpy(dtype=int)
    mae = top["mae"].to_numpy(dtype=np.float64)
    spread = float(np.quantile(mae, 0.20) - mae.min())
    temp = max(0.000035, spread / 3.0)
    w = np.exp(-(mae - mae.min()) / temp)
    w = w / w.sum()
    top["posterior_weight"] = w
    mask_top = masks[idx].astype(np.float64)
    label_top = labels[idx].astype(np.float64)
    row_post = w @ mask_top
    cell_den = np.repeat(row_post[:, None], h012_prob.shape[1], axis=1)
    cell_num = np.einsum("w,wr,wrt->rt", w, mask_top, label_top, optimize=True)
    q_cond = np.divide(cell_num, cell_den, out=h012_prob.copy(), where=cell_den > 1.0e-12)
    q_post = clip_prob(cell_den * q_cond + (1.0 - cell_den) * h012_prob)
    return q_post, q_cond, row_post, top


def expected_delta_for_prob(
    prob: np.ndarray,
    h012_prob: np.ndarray,
    top: pd.DataFrame,
    masks: np.ndarray,
    labels: np.ndarray,
) -> tuple[float, float]:
    p = clip_prob(prob)
    h = clip_prob(h012_prob)
    idx = top["particle"].to_numpy(dtype=int)
    w = top["posterior_weight"].to_numpy(dtype=np.float64)
    mask_top = masks[idx].astype(np.float64)
    label_top = labels[idx].astype(np.float64)
    d0 = (-np.log(1.0 - p) + np.log(1.0 - h)).sum(axis=1)
    adj = logit(h) - logit(p)
    denom = mask_top.sum(axis=1) * len(TARGETS)
    base = mask_top @ d0
    add = np.einsum("wr,wrt,rt->w", mask_top, label_top, adj, optimize=True)
    per_world = (base + add) / denom
    return float(np.sum(w * per_world)), float(np.quantile(per_world, 0.90) - np.quantile(per_world, 0.10))


def build_posterior_tables(
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    q_post: np.ndarray,
    q_cond: np.ndarray,
    row_post: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    z_h012 = logit(h012_prob)
    z_cond = logit(q_cond)
    for r in range(len(sample)):
        for t_i, target in enumerate(TARGETS):
            rows.append(
                {
                    "row": r,
                    "target": target,
                    "subject_id": sample.loc[r, "subject_id"],
                    "sleep_date": sample.loc[r, "sleep_date"],
                    "lifelog_date": sample.loc[r, "lifelog_date"],
                    "h012_prob": float(h012_prob[r, t_i]),
                    "world_q_post": float(q_post[r, t_i]),
                    "world_q_cond": float(q_cond[r, t_i]),
                    "row_public_prob": float(row_post[r]),
                    "abs_logit_shift_cond": float(abs(z_cond[r, t_i] - z_h012[r, t_i])),
                    "signed_logit_shift_cond": float(z_cond[r, t_i] - z_h012[r, t_i]),
                    "cell_world_score": float(row_post[r] * abs(z_cond[r, t_i] - z_h012[r, t_i])),
                }
            )
    cell = pd.DataFrame(rows)
    row = sample.copy()
    row["row"] = np.arange(len(sample))
    row["world_public_prob"] = row_post
    row["mean_cell_world_score"] = cell.groupby("row")["cell_world_score"].mean().reindex(range(len(sample))).to_numpy()
    row["max_cell_world_score"] = cell.groupby("row")["cell_world_score"].max().reindex(range(len(sample))).to_numpy()
    return cell.sort_values("cell_world_score", ascending=False).reset_index(drop=True), row.sort_values(
        "world_public_prob", ascending=False
    ).reset_index(drop=True)


def generate_candidates(
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    q_cond: np.ndarray,
    row_post: np.ndarray,
    cell_table: pd.DataFrame,
    top: pd.DataFrame,
    masks: np.ndarray,
    labels: np.ndarray,
) -> pd.DataFrame:
    z_h012 = logit(h012_prob)
    z_cond = logit(q_cond)
    flat_score = (row_post[:, None] * np.abs(z_cond - z_h012)).reshape(-1)
    flat_order = np.argsort(-flat_score)
    n_rows = len(sample)
    rows = []
    generated: dict[str, Path] = {}

    def materialize(family: str, alpha: float, mask: np.ndarray) -> None:
        if mask.sum() == 0:
            return
        prob = h012_prob.copy()
        z = z_h012.copy()
        z[mask] = (1.0 - alpha) * z_h012[mask] + alpha * z_cond[mask]
        prob[mask] = sigmoid(z[mask])
        delta, dispersion = expected_delta_for_prob(prob, h012_prob, top, masks, labels)
        changed = int(np.sum(np.abs(prob - h012_prob) > 1.0e-6))
        if changed == 0:
            return
        candidate_id = safe_id(f"h036_{family}_a{alpha:g}_c{changed}_{short_hash(prob)}")
        if candidate_id in generated:
            return
        path = OUT / f"submission_{candidate_id}.csv"
        write_submission(sample, prob, path)
        generated[candidate_id] = path
        rows.append(
            {
                "candidate_id": candidate_id,
                "file": path.name,
                "resolved_path": str(path),
                "family": family,
                "alpha": float(alpha),
                "changed_cells": changed,
                "changed_rows": int(np.sum(np.max(np.abs(prob - h012_prob), axis=1) > 1.0e-6)),
                "mean_abs_prob_move_h012": float(np.mean(np.abs(prob - h012_prob))),
                "max_abs_prob_move_h012": float(np.max(np.abs(prob - h012_prob))),
                "world_expected_delta_vs_h012": delta,
                "world_delta_iqr": dispersion,
            }
        )

    for k in [200, 400, 800, 1200, 1600]:
        mask = np.zeros(h012_prob.shape, dtype=bool)
        chosen = flat_order[: min(k, len(flat_order))]
        mask.reshape(-1)[chosen] = True
        for alpha in [0.25, 0.45, 0.70, 1.00]:
            materialize(f"celltop_k{k}", alpha, mask)

    for target in TARGETS:
        t_i = TARGETS.index(target)
        order = np.argsort(-flat_score.reshape(n_rows, len(TARGETS))[:, t_i])
        for k in [40, 80, 140]:
            mask = np.zeros(h012_prob.shape, dtype=bool)
            mask[order[:k], t_i] = True
            for alpha in [0.45, 0.70, 1.00]:
                materialize(f"target_{target}_k{k}", alpha, mask)

    row_order = np.argsort(-row_post)
    for r_count in [20, 35, 55, 80, 110]:
        mask = np.zeros(h012_prob.shape, dtype=bool)
        mask[row_order[:r_count], :] = True
        for alpha in [0.25, 0.45, 0.70]:
            materialize(f"rowworld_r{r_count}", alpha, mask)

    # An aggressive vector move: only rows with high public probability, but all
    # targets are moved together.  This is the high-upside HS-JEPA claim.
    cell_rank = cell_table.set_index(["row", "target"])["cell_world_score"].to_dict()
    for min_cell_rank in [0.002, 0.004, 0.006]:
        mask = np.zeros(h012_prob.shape, dtype=bool)
        threshold = float(np.quantile(cell_table["cell_world_score"], 1.0 - min_cell_rank))
        for r in row_order[:100]:
            for t_i, target in enumerate(TARGETS):
                if cell_rank.get((int(r), target), 0.0) >= threshold:
                    mask[int(r), t_i] = True
        for alpha in [0.70, 1.00]:
            materialize(f"needleworld_q{min_cell_rank:g}", alpha, mask)

    scores = pd.DataFrame(rows)
    if scores.empty:
        return scores
    return scores.sort_values("world_expected_delta_vs_h012").reset_index(drop=True)


def h024_score_candidates(candidate_scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    h024 = import_module(HITL / "h024_action_health_decoder_jepa.py", "h024_h036")
    known = h024.read_public_observations()
    refs = h024.build_reference_pack()
    known_pool = []
    for rec in known.to_dict("records"):
        known_pool.append(
            {
                "file": str(rec["file"]),
                "resolved_path": str(h024.locate(str(rec["file"])) or rec["file"]),
                "source": "known_public",
            }
        )
    cand_pool = candidate_scores[["file", "resolved_path", "candidate_id", "family"]].copy()
    cand_pool["original_file"] = cand_pool["file"]
    cand_pool["file"] = cand_pool["resolved_path"]
    cand_pool["source"] = "h036_global_public_world"
    pool = pd.concat([pd.DataFrame(known_pool), cand_pool], ignore_index=True).drop_duplicates("file", keep="last")
    features = h024.build_feature_table(pool, refs)
    blocked = {
        "file",
        "resolved_path",
        "source",
        "pool_file",
        "pool_resolved_path",
        "pool_candidate_id",
        "pool_family",
        "pool_source",
        "public_lb",
        "known_source",
        "note",
    }
    all_cols = h024.numeric_feature_cols(features.merge(known[["file", "public_lb"]], on="file", how="left"), blocked)
    cols_by_set = h024.feature_sets(all_cols)
    full_model_scores, full_loo = h024.evaluate_known_models(known[["file", "public_lb"]], features, cols_by_set)
    pre_known = known[known["file"] != H012][["file", "public_lb"]].reset_index(drop=True)
    pre_model_scores, pre_loo = h024.evaluate_known_models(pre_known, features, cols_by_set)

    pred_rows = []
    h012_feat = features[features["file"] == H012]
    cand_features = features[features["file"].isin(set(candidate_scores["resolved_path"]))]
    known_features_full = known[["file", "public_lb"]].merge(features, on="file", how="inner")
    known_features_pre = pre_known.merge(features, on="file", how="inner")

    def add_preds(model_scores: pd.DataFrame, known_features: pd.DataFrame, tag: str) -> None:
        if model_scores.empty or known_features.empty or h012_feat.empty:
            return
        top_models = model_scores.sort_values("loo_mae").head(12)
        for m in top_models.to_dict("records"):
            cols = cols_by_set.get(str(m["feature_set"]), [])
            if len(cols) < 2:
                continue
            alpha = float(m["alpha"])
            pred_h012 = float(
                h024.ridge_fit_predict(
                    known_features[cols].to_numpy(dtype=np.float64),
                    known_features["public_lb"].to_numpy(dtype=np.float64),
                    h012_feat[cols].to_numpy(dtype=np.float64),
                    alpha,
                )[0]
            )
            pred = h024.ridge_fit_predict(
                known_features[cols].to_numpy(dtype=np.float64),
                known_features["public_lb"].to_numpy(dtype=np.float64),
                cand_features[cols].to_numpy(dtype=np.float64),
                alpha,
            )
            for file_name, val in zip(cand_features["file"].tolist(), pred):
                pred_rows.append(
                    {
                        "file": file_name,
                        "model_tag": tag,
                        "feature_set": str(m["feature_set"]),
                        "alpha": alpha,
                        "loo_mae": float(m["loo_mae"]),
                        "pred_public": float(val),
                        "pred_h012": pred_h012,
                        "pred_margin_vs_h012": float(val - pred_h012),
                    }
                )

    add_preds(full_model_scores, known_features_full, "full_known")
    add_preds(pre_model_scores, known_features_pre, "pre_h012")
    pred_df = pd.DataFrame(pred_rows)
    if pred_df.empty:
        return features, pd.concat([full_model_scores, pre_model_scores], ignore_index=True), pd.DataFrame()
    agg = (
        pred_df.groupby(["file", "model_tag"])
        .agg(
            h024_pred_public_median=("pred_public", "median"),
            h024_pred_public_p10=("pred_public", lambda x: float(np.quantile(x, 0.10))),
            h024_pred_public_p90=("pred_public", lambda x: float(np.quantile(x, 0.90))),
            h024_margin_vs_h012_median=("pred_margin_vs_h012", "median"),
            h024_margin_vs_h012_p10=("pred_margin_vs_h012", lambda x: float(np.quantile(x, 0.10))),
            h024_margin_vs_h012_p90=("pred_margin_vs_h012", lambda x: float(np.quantile(x, 0.90))),
            h024_support_better_than_h012=("pred_margin_vs_h012", lambda x: float(np.mean(np.asarray(x) < 0.0))),
            h024_model_count=("pred_margin_vs_h012", "size"),
        )
        .reset_index()
    )
    wide_parts = []
    for tag in ["full_known", "pre_h012"]:
        part = agg[agg["model_tag"] == tag].drop(columns=["model_tag"]).copy()
        rename = {c: f"{tag}_{c}" for c in part.columns if c != "file"}
        wide_parts.append(part.rename(columns=rename))
    wide = wide_parts[0]
    for part in wide_parts[1:]:
        wide = wide.merge(part, on="file", how="outer")
    wide = wide.rename(columns={"file": "resolved_path"})
    return features, pd.concat(
        [
            full_model_scores.assign(model_tag="full_known"),
            pre_model_scores.assign(model_tag="pre_h012"),
        ],
        ignore_index=True,
    ), wide


def h025_score_candidates(candidate_scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    h026 = import_module(HITL / "h026_public_private_calibration_veto_jepa.py", "h026_h036")
    rt = h026.prepare_runtime()
    pool = candidate_scores[["file", "resolved_path", "candidate_id", "family"]].copy()
    pool["source"] = "h036_global_public_world"
    scores, cells = rt.h025.score_candidates(
        rt.action_model,
        rt.action_cols,
        pool,
        rt.h012_prob,
        rt.test_pcs,
        rt.sample,
        rt.train_actions,
    )
    return scores, cells


def run_rowperm_stress(selected_file: str) -> pd.DataFrame:
    h026 = import_module(HITL / "h026_public_private_calibration_veto_jepa.py", "h026_h036_rowperm")
    rt = h026.prepare_runtime()
    return rt.h025.row_permutation_candidate_stress(
        rt.action_model,
        rt.action_cols,
        selected_file,
        rt.h012_prob,
        rt.test_pcs,
        rt.sample,
        n_perm=300,
    )


def decision_frame(
    candidate_scores: pd.DataFrame,
    null_df: pd.DataFrame,
    best_world_mae: float,
    selected_rowperm: pd.DataFrame,
) -> pd.DataFrame:
    if candidate_scores.empty:
        return pd.DataFrame(
            [
                {
                    "decision": "no_candidate",
                    "reason": "no generated candidate survived materialization",
                    "promote": False,
                }
            ]
        )
    selected = candidate_scores.iloc[0]
    null_p = float(np.mean(null_df["best_null_mae"].to_numpy(dtype=np.float64) <= best_world_mae)) if len(null_df) else 1.0
    rowperm_p = 1.0
    rowperm_real = np.nan
    if not selected_rowperm.empty:
        real = float(selected_rowperm["real_top1200_sum"].iloc[0])
        rowperm_real = real
        rowperm_p = float(np.mean(selected_rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= real))
    pre_margin = float(selected.get("pre_h012_h024_margin_vs_h012_median", np.nan))
    pre_support = float(selected.get("pre_h012_h024_support_better_than_h012", np.nan))
    world_delta = float(selected["world_expected_delta_vs_h012"])
    promote = bool(
        world_delta < -0.00055
        and np.isfinite(pre_margin)
        and pre_margin < -0.00025
        and np.isfinite(pre_support)
        and pre_support >= 0.60
        and null_p <= 0.15
        and rowperm_p <= 0.35
    )
    reasons = []
    if world_delta >= -0.00055:
        reasons.append("world expected gain too small")
    if not np.isfinite(pre_margin) or pre_margin >= -0.00025:
        reasons.append("H024 pre-H012 decoder does not prefer candidate enough")
    if not np.isfinite(pre_support) or pre_support < 0.60:
        reasons.append("H024 support below 60%")
    if null_p > 0.15:
        reasons.append("world fit not far enough from permutation null")
    if rowperm_p > 0.35:
        reasons.append("H025 row permutation stress weak")
    return pd.DataFrame(
        [
            {
                "decision": "promote" if promote else "do_not_promote",
                "promote": promote,
                "selected_candidate_id": selected["candidate_id"],
                "selected_file": selected["file"],
                "selected_resolved_path": selected["resolved_path"],
                "world_expected_delta_vs_h012": world_delta,
                "pre_h012_h024_margin_vs_h012_median": pre_margin,
                "pre_h012_h024_support_better_than_h012": pre_support,
                "world_null_p_best_le_real": null_p,
                "rowperm_real_top1200_sum": rowperm_real,
                "rowperm_p_perm_ge_real": rowperm_p,
                "reason": "; ".join(reasons) if reasons else "all promotion gates passed",
            }
        ]
    )


def write_report(
    known: pd.DataFrame,
    particle_df: pd.DataFrame,
    config_summary: pd.DataFrame,
    null_df: pd.DataFrame,
    top_worlds: pd.DataFrame,
    cell_table: pd.DataFrame,
    row_table: pd.DataFrame,
    candidate_scores: pd.DataFrame,
    decision: pd.DataFrame,
) -> None:
    best_world = particle_df.iloc[0]
    null_p = float(np.mean(null_df["best_null_mae"].to_numpy(dtype=np.float64) <= float(best_world["mae"]))) if len(null_df) else 1.0
    lines = []
    lines.append("# H036 Global Public-World Solver HS-JEPA\n")
    lines.append("## Question\n")
    lines.append(
        "Can the full set of known public LB observations be explained by a latent public subset plus "
        "a row/target binary label world, and can that posterior justify a nonlocal post-H012 move?\n"
    )
    lines.append("## Sensor facts\n")
    lines.append(f"- known public sensors used: {len(known)}\n")
    lines.append(f"- anchor: `{H012}` = {H012_LB:.10f}\n")
    lines.append(f"- observed files explained relative to H012: {len(known) - 1}\n")
    lines.append("## World fit\n")
    lines.append(
        f"- best particle MAE={float(best_world['mae']):.9f}, RMSE={float(best_world['rmse']):.9f}, "
        f"Spearman={float(best_world['spearman']):.3f}\n"
    )
    lines.append(f"- permutation-null p(best_null_mae <= real_best_mae)={null_p:.3f}\n")
    lines.append("\nTop config families:\n")
    lines.append(md_table(config_summary.head(12), 12))
    lines.append("\n\nTop worlds:\n")
    lines.append(md_table(top_worlds.head(12), 12))
    lines.append("\n\nTop posterior cells:\n")
    lines.append(md_table(cell_table.head(15), 15))
    lines.append("\n\nTop public rows:\n")
    lines.append(md_table(row_table.head(15), 15))
    lines.append("\n\nCandidate ranking:\n")
    keep = [
        c
        for c in [
            "candidate_id",
            "family",
            "alpha",
            "changed_cells",
            "world_expected_delta_vs_h012",
            "pre_h012_h024_pred_public_median",
            "pre_h012_h024_margin_vs_h012_median",
            "pre_h012_h024_support_better_than_h012",
            "h025_score",
            "pred_gain_top1200_sum",
            "h036_score",
        ]
        if c in candidate_scores.columns
    ]
    lines.append(md_table(candidate_scores[keep].head(18), 18) if keep else "_empty_")
    lines.append("\n\nDecision:\n")
    lines.append(md_table(decision, 1))
    lines.append(
        "\n\n## Interpretation\n"
        "- If the permutation-null p-value is high, many fake public worlds fit the observations just as well; the world posterior is not a reliable new target.\n"
        "- If H024/H025 reject the best world move, the public-equation posterior is still not translated into an action-health-safe submission.\n"
        "- Promotion requires all gates because H012 already sits in a narrow basin and local stress failures have been common after H012.\n"
    )
    (OUT / "h036_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    known, sample, h012_prob, pred_by_file = load_system()
    files, d0_rows, d1_adj, actual_delta = build_delta_tensors(known, pred_by_file, h012_prob)
    q_sources = build_q_sources(sample, h012_prob)
    row_priors = build_row_priors(sample)

    configs: list[WorldConfig] = []
    q_names = [name for name in q_sources if name != "e247"]
    row_names = list(row_priors)
    subset_sizes = [70, 95, 125, 155, 190, 230]
    for q_name in q_names:
        for row_name in row_names:
            for size in subset_sizes:
                configs.append(WorldConfig(q_name, row_name, size, "sample", 36))
                configs.append(WorldConfig(q_name, row_name, size, "temperature_sample", 24))
                configs.append(WorldConfig(q_name, row_name, size, "map", 8))

    config_df = pd.DataFrame([cfg.__dict__ for cfg in configs])
    config_df.to_csv(OUT / "h036_world_configs.csv", index=False)

    particle_df, masks, labels, preds = sample_worlds(configs, q_sources, row_priors, d0_rows, d1_adj, actual_delta)
    particle_df.to_csv(OUT / "h036_world_particles.csv", index=False)
    pred_df = pd.DataFrame(preds, columns=[f"pred_delta_{Path(f).stem}" for f in files])
    pred_df.insert(0, "particle", np.arange(len(pred_df)))
    pred_df.to_csv(OUT / "h036_world_predicted_deltas.csv", index=False)

    config_summary = (
        particle_df.groupby(["q_source", "row_prior", "subset_size", "label_mode"])
        .agg(
            best_mae=("mae", "min"),
            median_mae=("mae", "median"),
            best_spearman=("spearman", "max"),
            n_particles=("mae", "size"),
        )
        .reset_index()
        .sort_values("best_mae")
    )
    config_summary.to_csv(OUT / "h036_world_config_summary.csv", index=False)

    null_df = permutation_null(preds, actual_delta, n_perm=300)
    null_df.to_csv(OUT / "h036_world_null_stress.csv", index=False)

    q_post, q_cond, row_post, top_worlds = posterior_from_worlds(particle_df, masks, labels, h012_prob, top_n=1600)
    top_worlds.to_csv(OUT / "h036_top_worlds.csv", index=False)
    cell_table, row_table = build_posterior_tables(sample, h012_prob, q_post, q_cond, row_post)
    cell_table.to_csv(OUT / "h036_world_posterior_cells.csv", index=False)
    row_table.to_csv(OUT / "h036_world_posterior_rows.csv", index=False)

    candidate_scores = generate_candidates(sample, h012_prob, q_cond, row_post, cell_table, top_worlds, masks, labels)
    candidate_scores.to_csv(OUT / "h036_generated_candidates.csv", index=False)

    h024_features = pd.DataFrame()
    h024_models = pd.DataFrame()
    h024_preds = pd.DataFrame()
    h025_scores = pd.DataFrame()
    h025_cells = pd.DataFrame()
    if not candidate_scores.empty:
        h024_features, h024_models, h024_preds = h024_score_candidates(candidate_scores)
        h024_features.to_csv(OUT / "h036_h024_features.csv", index=False)
        h024_models.to_csv(OUT / "h036_h024_model_scores.csv", index=False)
        h024_preds.to_csv(OUT / "h036_h024_candidate_predictions.csv", index=False)
        if not h024_preds.empty:
            candidate_scores = candidate_scores.merge(h024_preds, on="resolved_path", how="left")
        h025_scores, h025_cells = h025_score_candidates(candidate_scores)
        h025_scores.to_csv(OUT / "h036_h025_candidate_scores.csv", index=False)
        if not h025_cells.empty:
            h025_cells.to_csv(OUT / "h036_h025_top_cells.csv", index=False)
        if not h025_scores.empty:
            keep_cols = [
                "file",
                "h025_score",
                "pred_gain_top1200_sum",
                "pred_gain_mean_moved",
                "pred_positive_rate_moved",
                "ood_abs_delta_rate",
            ]
            candidate_scores = candidate_scores.merge(
                h025_scores[[c for c in keep_cols if c in h025_scores.columns]], on="file", how="left"
            )
        h024_margin = candidate_scores.get(
            "pre_h012_h024_margin_vs_h012_median", pd.Series(np.nan, index=candidate_scores.index)
        ).fillna(0.01)
        h024_support = candidate_scores.get(
            "pre_h012_h024_support_better_than_h012", pd.Series(0.0, index=candidate_scores.index)
        ).fillna(0.0)
        h025_score = candidate_scores.get("h025_score", pd.Series(0.0, index=candidate_scores.index)).fillna(0.0)
        candidate_scores["h036_score"] = (
            candidate_scores["world_expected_delta_vs_h012"].rank(method="average", pct=True)
            + h024_margin.rank(method="average", pct=True)
            + h025_score.rank(method="average", pct=True)
            - 0.35 * h024_support
        )
        candidate_scores = candidate_scores.sort_values(
            ["h036_score", "world_expected_delta_vs_h012"], ascending=[True, True]
        ).reset_index(drop=True)
        candidate_scores.to_csv(OUT / "h036_candidate_scores.csv", index=False)

    selected_rowperm = pd.DataFrame()
    if not candidate_scores.empty:
        selected_path = str(candidate_scores.iloc[0]["resolved_path"])
        selected_rowperm = run_rowperm_stress(selected_path)
        selected_rowperm.to_csv(OUT / "h036_selected_h025_rowperm_stress.csv", index=False)

    decision = decision_frame(candidate_scores, null_df, float(particle_df.iloc[0]["mae"]), selected_rowperm)
    decision.to_csv(OUT / "h036_decision.csv", index=False)
    if bool(decision.iloc[0].get("promote", False)):
        selected_path = Path(str(decision.iloc[0]["selected_resolved_path"]))
        root_name = selected_path.name.replace(".csv", "_uploadsafe.csv")
        shutil.copy2(selected_path, ROOT / root_name)
        decision.loc[0, "promoted_root_file"] = root_name
        decision.to_csv(OUT / "h036_decision.csv", index=False)

    known.to_csv(OUT / "h036_known_public_sensors.csv", index=False)
    target_rows = []
    for file_name, actual, pred in zip(files, actual_delta, preds[particle_df.iloc[0]["particle"].astype(int)]):
        target_rows.append({"file": file_name, "actual_delta_vs_h012": float(actual), "best_world_pred_delta": float(pred)})
    pd.DataFrame(target_rows).to_csv(OUT / "h036_best_world_equation_fit.csv", index=False)

    write_report(
        known,
        particle_df,
        config_summary,
        null_df,
        top_worlds,
        cell_table,
        row_table,
        candidate_scores,
        decision,
    )

    print(f"H036 worlds: {len(particle_df)}")
    print(f"H036 best world MAE: {float(particle_df.iloc[0]['mae']):.9f}")
    print(
        "H036 null p: "
        f"{float(np.mean(null_df['best_null_mae'].to_numpy(dtype=np.float64) <= float(particle_df.iloc[0]['mae']))):.3f}"
    )
    if not candidate_scores.empty:
        print(f"H036 selected: {candidate_scores.iloc[0]['candidate_id']}")
        print(f"H036 selected world delta: {float(candidate_scores.iloc[0]['world_expected_delta_vs_h012']):.9f}")
    print(f"H036 decision: {decision.iloc[0]['decision']} - {decision.iloc[0]['reason']}")


if __name__ == "__main__":
    main()
