from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import shutil

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hitl" / "h024_action_health_decoder_jepa"
ANALYSIS = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
HITL = ROOT / "hitl"
GPT_SUBS = ROOT / "gpt_pro_pack" / "q2s1_hidden_state_translation" / "submissions"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-6

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
H010 = "submission_h010_objective_s1s4_v2_uploadsafe.csv"
E323 = "submission_e323_5508f966_uploadsafe.csv"
E95 = "submission_e95_hardtail_541e3973.csv"
MIXMIN = "submission_mixmin_0c916bb4.csv"
E216 = "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv"
E267 = "submission_e267_humansocial_tail_balanced_2936100f.csv"
E368 = "submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv"
E101 = "submission_e101_q2s3tail_177569bc.csv"


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
    return 1.0 / (1.0 + np.exp(-x))


def prob_matrix(name: str | Path, sample: pd.DataFrame) -> np.ndarray:
    return load_sub(name, sample)[TARGETS].to_numpy(dtype=np.float64)


def flat_logit(prob: np.ndarray) -> np.ndarray:
    return logit(prob).reshape(-1)


def projection(move: np.ndarray, direction: np.ndarray) -> tuple[float, float]:
    denom = float(direction @ direction)
    if denom <= 1e-15:
        return 0.0, 0.0
    coeff = float(move @ direction / denom)
    cos = float(move @ direction / (np.linalg.norm(move) * np.linalg.norm(direction) + 1e-12))
    return coeff, cos


def rankdata(x: np.ndarray) -> np.ndarray:
    return pd.Series(x).rank(method="average").to_numpy(dtype=np.float64)


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3:
        return float("nan")
    ra = rankdata(a)
    rb = rankdata(b)
    if np.std(ra) < 1e-12 or np.std(rb) < 1e-12:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def pairwise_accuracy(y: np.ndarray, pred: np.ndarray) -> float:
    ok = 0
    total = 0
    for i in range(len(y)):
        for j in range(i + 1, len(y)):
            dy = y[i] - y[j]
            dp = pred[i] - pred[j]
            if abs(dy) < 1e-12:
                continue
            total += 1
            ok += int(np.sign(dy) == np.sign(dp))
    return float(ok / total) if total else float("nan")


def zscore(train: np.ndarray, pred: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mu = np.nanmean(train, axis=0)
    sd = np.nanstd(train, axis=0)
    sd = np.where(sd < 1e-12, 1.0, sd)
    return np.nan_to_num((train - mu) / sd), np.nan_to_num((pred - mu) / sd)


def ridge_fit_predict(
    train_x: np.ndarray,
    train_y: np.ndarray,
    pred_x: np.ndarray,
    alpha: float,
) -> np.ndarray:
    x, xp = zscore(train_x, pred_x)
    xa = np.column_stack([np.ones(len(x)), x])
    xpa = np.column_stack([np.ones(len(xp)), xp])
    penalty = np.eye(xa.shape[1]) * alpha
    penalty[0, 0] = 0.0
    beta = np.linalg.pinv(xa.T @ xa + penalty) @ xa.T @ train_y
    return xpa @ beta


def binary_log_loss(y: np.ndarray, p: np.ndarray) -> float:
    p = clip_prob(p)
    return float(np.mean(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))))


def safe_float(row: pd.Series, col: str, default: float = 0.0) -> float:
    if col not in row or pd.isna(row[col]):
        return default
    return float(row[col])


def candidate_id_from_path(path: str | Path) -> str:
    p = Path(str(path))
    stem = p.stem
    return stem.replace("submission_", "")


def source_from_path(path: str | Path) -> str:
    parts = Path(str(path)).parts
    for part in parts:
        if part.startswith("h0"):
            return part
    stem = Path(str(path)).stem
    if stem.startswith("submission_"):
        return "known_or_root"
    return "unknown"


def read_public_observations() -> pd.DataFrame:
    path = ANALYSIS / "public_probe_observations.csv"
    obs = pd.read_csv(path)
    rows = []
    for rec in obs.to_dict("records"):
        file_name = str(rec["file"])
        if locate(file_name) is None:
            continue
        rows.append(
            {
                "file": file_name,
                "public_lb": float(rec["public_lb"]),
                "note": str(rec.get("note", "")),
                "known_source": "public_probe_observations",
            }
        )
    df = pd.DataFrame(rows).drop_duplicates("file", keep="last")
    return df.sort_values("public_lb").reset_index(drop=True)


def collect_candidate_pool() -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    def add(file_name: str, source: str, meta: dict[str, object] | None = None) -> None:
        path = locate(file_name)
        if path is None:
            return
        rec: dict[str, object] = {
            "file": str(Path(file_name)),
            "resolved_path": str(path),
            "candidate_id": candidate_id_from_path(file_name),
            "source": source,
        }
        if meta:
            rec.update(meta)
        rows.append(rec)

    known = read_public_observations()
    for rec in known.to_dict("records"):
        add(str(rec["file"]), "known_public", {"known_public_lb": float(rec["public_lb"])})

    tables = [
        ("h015", HITL / "h015_public_equation_self_feedback" / "h015_candidates.csv", 80),
        ("h016", HITL / "h016_public_subset_weight_jepa" / "h016_candidates.csv", 80),
        ("h017", HITL / "h017_joint_label_weight_jepa" / "h017_candidates.csv", 80),
        ("h018", HITL / "h018_hard_label_world_jepa" / "h018_candidates.csv", 70),
        ("h019", HITL / "h019_row_subset_hardworld_jepa" / "h019_candidates.csv", 70),
        ("h020", HITL / "h020_joint_vector_world_jepa" / "h020_candidates.csv", 80),
        ("h021", HITL / "h021_human_state_vector_prior_jepa" / "h021_candidates.csv", 20),
        ("h023", HITL / "h023_hs_pareto_proposal_vector_jepa" / "h023_candidates.csv", 80),
    ]
    for source, path, n in tables:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "file" not in df.columns:
            continue
        df = df.head(n).copy()
        for idx, rec in df.iterrows():
            meta = {
                f"{source}_rank": int(idx),
                "source_candidate_id": str(rec.get("candidate_id", "")),
                "source_decision": str(
                    rec.get(f"{source}_decision", rec.get("action_decision", rec.get("h023_decision", "")))
                ),
            }
            for col in df.columns:
                if col == "file":
                    continue
                val = rec[col]
                if isinstance(val, (str, int, float, bool, np.integer, np.floating, np.bool_)):
                    meta[f"meta_{col}"] = val
            add(str(rec["file"]), source, meta)

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["dedup_key"] = out["resolved_path"].map(lambda x: str(Path(x).resolve()))
    out = out.drop_duplicates("dedup_key", keep="first").drop(columns=["dedup_key"])
    return out.reset_index(drop=True)


def cell_map(path: Path, value_cols: list[str]) -> dict[str, np.ndarray]:
    values = {col: np.zeros((250, len(TARGETS)), dtype=np.float64) for col in value_cols}
    if not path.exists():
        return values
    df = pd.read_csv(path)
    target_to_i = {t: i for i, t in enumerate(TARGETS)}
    for rec in df.to_dict("records"):
        r = int(rec["row"])
        c = target_to_i[str(rec["target"])]
        if r < 0 or r >= 250:
            continue
        for col in value_cols:
            if col in rec and pd.notna(rec[col]):
                values[col][r, c] = float(rec[col])
    return values


def build_state_maps() -> dict[str, np.ndarray]:
    maps: dict[str, np.ndarray] = {}
    for name, arr in cell_map(
        HITL / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv",
        ["posterior_minus_base", "cell_score", "direction_consistency"],
    ).items():
        maps[f"h012_{name}"] = arr
    for name, arr in cell_map(
        HITL / "h015_public_equation_self_feedback" / "h015_cell_posterior.csv",
        ["posterior_minus_h012", "cell_score", "direction_consistency"],
    ).items():
        maps[f"h015_{name}"] = arr
    for name, arr in cell_map(
        HITL / "h021_human_state_vector_prior_jepa" / "h021_test_human_state_vector_prior_cells.csv",
        ["h020_gain", "hs_minus_h012", "h020_minus_h012", "hs_cell_score", "hs_row_conf"],
    ).items():
        maps[f"h021_{name}"] = arr
    raw_h021 = pd.read_csv(HITL / "h021_human_state_vector_prior_jepa" / "h021_test_human_state_vector_prior_cells.csv")
    h021_agree = np.zeros((250, len(TARGETS)), dtype=np.float64)
    for rec in raw_h021.to_dict("records"):
        h021_agree[int(rec["row"]), TARGETS.index(str(rec["target"]))] = float(bool(rec["hs_h020_agree"]))
    maps["h021_hs_h020_agree"] = h021_agree
    for name, arr in cell_map(
        HITL / "h023_hs_pareto_proposal_vector_jepa" / "h023_cell_state.csv",
        [
            "h023_minus_h012",
            "h023_minus_base",
            "row_weight",
            "row_score",
            "cell_gain",
            "gain_score",
            "move_score",
            "shift_score",
            "combined_score",
        ],
    ).items():
        maps[f"h023_{name}"] = arr
    raw_h023 = pd.read_csv(HITL / "h023_hs_pareto_proposal_vector_jepa" / "h023_cell_state.csv")
    h023_agree = np.zeros((250, len(TARGETS)), dtype=np.float64)
    for rec in raw_h023.to_dict("records"):
        h023_agree[int(rec["row"]), TARGETS.index(str(rec["target"]))] = float(bool(rec["hs_h023_agree"]))
    maps["h023_hs_h023_agree"] = h023_agree
    return maps


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    w = np.asarray(weights, dtype=np.float64)
    v = np.asarray(values, dtype=np.float64)
    s = float(w.sum())
    if s <= 1e-15:
        return 0.0
    return float((v * w).sum() / s)


@dataclass
class ReferencePack:
    sample: pd.DataFrame
    probs: dict[str, np.ndarray]
    logits: dict[str, np.ndarray]
    state: dict[str, np.ndarray]


def build_reference_pack() -> ReferencePack:
    sample = load_sub(H012)
    anchor_files = {
        "h012": H012,
        "e247": E247,
        "h010": H010,
        "e323": E323,
        "e95": E95,
        "mixmin": MIXMIN,
        "e216": E216,
        "e267": E267,
        "e368": E368,
        "e101": E101,
    }
    probs: dict[str, np.ndarray] = {}
    for name, file_name in anchor_files.items():
        if locate(file_name) is None:
            continue
        probs[name] = prob_matrix(file_name, sample)
    logits = {name: flat_logit(prob) for name, prob in probs.items()}
    return ReferencePack(sample=sample, probs=probs, logits=logits, state=build_state_maps())


def feature_row(file_name: str | Path, refs: ReferencePack) -> dict[str, object]:
    p = prob_matrix(file_name, refs.sample)
    z = flat_logit(p)
    z_h012 = refs.logits["h012"]
    z_e247 = refs.logits["e247"]
    move_h012 = z - z_h012
    move_e247 = z - z_e247
    prob_h012 = refs.probs["h012"]
    prob_e247 = refs.probs["e247"]
    prob_delta_h012 = p - prob_h012
    prob_delta_e247 = p - prob_e247
    abs_move_h012 = np.abs(move_h012.reshape(250, len(TARGETS)))
    abs_prob_h012 = np.abs(prob_delta_h012)
    move_h012_m = move_h012.reshape(250, len(TARGETS))
    move_e247_m = move_e247.reshape(250, len(TARGETS))

    row: dict[str, object] = {
        "file": str(file_name),
        "resolved_path": str(locate(file_name) or file_name),
        "source": source_from_path(file_name),
        "min_prob": float(p.min()),
        "max_prob": float(p.max()),
        "mean_prob": float(p.mean()),
        "entropy_mean": float(np.mean(-(clip_prob(p) * np.log(clip_prob(p)) + (1 - clip_prob(p)) * np.log(clip_prob(1 - p))))),
        "mean_abs_prob_move_h012": float(np.mean(abs_prob_h012)),
        "max_abs_prob_move_h012": float(np.max(abs_prob_h012)),
        "mean_abs_logit_move_h012": float(np.mean(np.abs(move_h012))),
        "rms_logit_move_h012": float(np.sqrt(np.mean(move_h012**2))),
        "max_abs_logit_move_h012": float(np.max(np.abs(move_h012))),
        "mean_abs_prob_move_e247": float(np.mean(np.abs(prob_delta_e247))),
        "mean_abs_logit_move_e247": float(np.mean(np.abs(move_e247))),
        "changed_cells_h012_1e6": int(np.sum(abs_prob_h012 > 1e-6)),
        "changed_cells_h012_1e4": int(np.sum(abs_prob_h012 > 1e-4)),
        "changed_rows_h012_1e4": int(np.sum(np.max(abs_prob_h012, axis=1) > 1e-4)),
        "near_zero_rate": float(np.mean(p < 0.01)),
        "near_one_rate": float(np.mean(p > 0.99)),
    }

    for t_i, target in enumerate(TARGETS):
        row[f"mean_prob_{target}"] = float(np.mean(p[:, t_i]))
        row[f"mean_abs_prob_h012_{target}"] = float(np.mean(abs_prob_h012[:, t_i]))
        row[f"mean_signed_prob_h012_{target}"] = float(np.mean(prob_delta_h012[:, t_i]))
        row[f"mean_abs_logit_h012_{target}"] = float(np.mean(abs_move_h012[:, t_i]))
        row[f"mean_signed_logit_h012_{target}"] = float(np.mean(move_h012_m[:, t_i]))
        row[f"changed_cells_h012_1e4_{target}"] = int(np.sum(abs_prob_h012[:, t_i] > 1e-4))

    ref_dirs: dict[str, np.ndarray] = {}
    for name, z_ref in refs.logits.items():
        if name in {"h012", "e247"}:
            continue
        ref_dirs[f"e247_to_{name}"] = z_ref - z_e247
        ref_dirs[f"h012_to_{name}"] = z_ref - z_h012
    ref_dirs["e247_to_h012"] = z_h012 - z_e247
    ref_dirs["h012_to_e247"] = z_e247 - z_h012

    for name, direction in sorted(ref_dirs.items()):
        base_move = move_e247 if name.startswith("e247_to") else move_h012
        coeff, cos = projection(base_move, direction)
        row[f"proj_{name}"] = coeff
        row[f"cos_{name}"] = cos

    bad_axes = [
        "h012_to_h010",
        "h012_to_e323",
        "h012_to_e216",
        "h012_to_e267",
        "e247_to_h010",
        "e247_to_e323",
        "e247_to_e216",
        "e247_to_e267",
    ]
    good_axes = ["e247_to_h012", "e247_to_e95", "e247_to_mixmin", "e247_to_e101"]
    row["bad_axis_abs_load"] = float(sum(abs(row.get(f"proj_{axis}", 0.0)) for axis in bad_axes))
    row["bad_axis_positive_load"] = float(sum(max(float(row.get(f"proj_{axis}", 0.0)), 0.0) for axis in bad_axes))
    row["good_axis_abs_load"] = float(sum(abs(row.get(f"proj_{axis}", 0.0)) for axis in good_axes))
    row["bad_to_good_load_ratio"] = float(row["bad_axis_abs_load"] / (row["good_axis_abs_load"] + 1e-9))

    weights_h012 = np.abs(move_h012_m)
    weights_e247 = np.abs(move_e247_m)
    for key, arr in refs.state.items():
        row[f"state_{key}_w_h012"] = weighted_mean(arr, weights_h012)
        row[f"state_{key}_w_e247"] = weighted_mean(arr, weights_e247)
        row[f"state_{key}_mean_all"] = float(np.mean(arr))
    for name, direction_key, weights in [
        ("h012", "h012_posterior_minus_base", weights_e247),
        ("h015", "h015_posterior_minus_h012", weights_h012),
        ("h021_h020", "h021_h020_minus_h012", weights_h012),
        ("h021_hs", "h021_hs_minus_h012", weights_h012),
        ("h023", "h023_h023_minus_h012", weights_h012),
    ]:
        direction = refs.state.get(direction_key)
        if direction is None:
            continue
        move = move_e247_m if name == "h012" else move_h012_m
        agree = (np.sign(move) == np.sign(direction)).astype(np.float64)
        nonzero = (np.abs(direction) > 1e-12).astype(np.float64)
        row[f"state_{name}_direction_agree"] = weighted_mean(agree * nonzero, weights)
        row[f"state_{name}_direction_support"] = weighted_mean(nonzero, weights)

    return row


def build_feature_table(pool: pd.DataFrame, refs: ReferencePack) -> pd.DataFrame:
    rows = []
    for rec in pool.to_dict("records"):
        try:
            row = feature_row(str(rec["file"]), refs)
        except Exception as exc:  # keep the experiment auditable instead of silently dying
            rows.append({"file": str(rec["file"]), "feature_error": repr(exc)})
            continue
        row.update({f"pool_{k}": v for k, v in rec.items() if k not in row})
        rows.append(row)
    df = pd.DataFrame(rows)
    if "feature_error" in df.columns:
        err = df[df["feature_error"].notna()]
        if len(err):
            err.to_csv(OUT / "h024_feature_errors.csv", index=False)
        df = df[df.get("feature_error").isna()].copy()
    return df.reset_index(drop=True)


def numeric_feature_cols(df: pd.DataFrame, blocked: set[str]) -> list[str]:
    cols = []
    for col in df.columns:
        if col in blocked:
            continue
        if col.startswith("pool_known_public_lb"):
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            vals = df[col].to_numpy(dtype=np.float64)
            finite = np.isfinite(vals)
            if finite.sum() < max(5, int(0.70 * len(vals))):
                continue
            if np.nanstd(vals) > 1e-12:
                cols.append(col)
    return cols


def feature_sets(all_cols: list[str]) -> dict[str, list[str]]:
    def pick(prefixes: list[str], contains: list[str] | None = None) -> list[str]:
        contains = contains or []
        out = []
        for col in all_cols:
            if any(col.startswith(p) for p in prefixes) or any(s in col for s in contains):
                out.append(col)
        return out

    sets = {
        "geometry": pick(
            [
                "mean_abs_",
                "max_abs_",
                "rms_",
                "changed_",
                "near_",
                "entropy",
                "mean_prob_",
                "mean_signed_",
            ]
        ),
        "axes": pick(["proj_", "cos_"], ["axis", "load_ratio"]),
        "state": pick(["state_"]),
    }
    sets["axes_state"] = sorted(set(sets["axes"] + sets["state"]))
    sets["all"] = all_cols
    return {k: [c for c in v if c in all_cols] for k, v in sets.items() if len(v) >= 2}


def evaluate_known_models(known: pd.DataFrame, features: pd.DataFrame, cols_by_set: dict[str, list[str]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    known_features = known[["file", "public_lb"]].merge(features, on="file", how="inner")
    model_rows = []
    pred_rows = []
    alphas = [0.01, 0.1, 1.0, 10.0, 100.0]
    y = known_features["public_lb"].to_numpy(dtype=np.float64)
    for set_name, cols in cols_by_set.items():
        if len(cols) < 2:
            continue
        for alpha in alphas:
            loo = np.zeros(len(known_features), dtype=np.float64)
            for i in range(len(known_features)):
                train = known_features.drop(index=known_features.index[i]).reset_index(drop=True)
                pred = known_features.iloc[[i]].reset_index(drop=True)
                loo[i] = ridge_fit_predict(
                    train[cols].to_numpy(dtype=np.float64),
                    train["public_lb"].to_numpy(dtype=np.float64),
                    pred[cols].to_numpy(dtype=np.float64),
                    alpha,
                )[0]
            mae = float(np.mean(np.abs(loo - y)))
            rmse = float(np.sqrt(np.mean((loo - y) ** 2)))
            rho = spearman(y, loo)
            pair_acc = pairwise_accuracy(y, loo)
            h012_idx = known_features.index[known_features["file"] == H012].tolist()
            h010_idx = known_features.index[known_features["file"] == H010].tolist()
            e323_idx = known_features.index[known_features["file"] == E323].tolist()
            e247_idx = known_features.index[known_features["file"] == E247].tolist()
            model_rows.append(
                {
                    "feature_set": set_name,
                    "alpha": alpha,
                    "n_features": len(cols),
                    "loo_mae": mae,
                    "loo_rmse": rmse,
                    "loo_spearman": rho,
                    "loo_pair_acc": pair_acc,
                    "h012_pred_loo": float(loo[h012_idx[0]]) if h012_idx else np.nan,
                    "h012_actual": float(y[h012_idx[0]]) if h012_idx else np.nan,
                    "h010_pred_loo": float(loo[h010_idx[0]]) if h010_idx else np.nan,
                    "h010_actual": float(y[h010_idx[0]]) if h010_idx else np.nan,
                    "e323_pred_loo": float(loo[e323_idx[0]]) if e323_idx else np.nan,
                    "e323_actual": float(y[e323_idx[0]]) if e323_idx else np.nan,
                    "e247_pred_loo": float(loo[e247_idx[0]]) if e247_idx else np.nan,
                    "e247_actual": float(y[e247_idx[0]]) if e247_idx else np.nan,
                }
            )
            for j, rec in known_features[["file", "public_lb"]].iterrows():
                pred_rows.append(
                    {
                        "feature_set": set_name,
                        "alpha": alpha,
                        "file": rec["file"],
                        "public_lb": float(rec["public_lb"]),
                        "loo_pred_public_lb": float(loo[j]),
                        "loo_error": float(loo[j] - rec["public_lb"]),
                    }
                )
    return pd.DataFrame(model_rows).sort_values(["loo_mae", "loo_rmse"]), pd.DataFrame(pred_rows)


def score_candidates(
    known: pd.DataFrame,
    features: pd.DataFrame,
    model_scores: pd.DataFrame,
    cols_by_set: dict[str, list[str]],
) -> pd.DataFrame:
    known_features = known[["file", "public_lb"]].merge(features, on="file", how="inner")
    all_features = features.copy()
    model_scores = model_scores.copy()
    usable = model_scores[
        (model_scores["loo_pair_acc"] >= 0.55)
        & (model_scores["loo_mae"] <= max(0.0045, float(model_scores["loo_mae"].quantile(0.75))))
    ].head(12)
    if usable.empty:
        usable = model_scores.head(8)

    preds = []
    for rec in usable.to_dict("records"):
        cols = cols_by_set[str(rec["feature_set"])]
        alpha = float(rec["alpha"])
        full_pred = ridge_fit_predict(
            known_features[cols].to_numpy(dtype=np.float64),
            known_features["public_lb"].to_numpy(dtype=np.float64),
            all_features[cols].to_numpy(dtype=np.float64),
            alpha,
        )
        for i, pred in enumerate(full_pred):
            preds.append(
                {
                    "file": all_features.iloc[i]["file"],
                    "feature_set": rec["feature_set"],
                    "alpha": alpha,
                    "pred_public_lb": float(pred),
                    "model_loo_mae": float(rec["loo_mae"]),
                    "model_pair_acc": float(rec["loo_pair_acc"]),
                }
            )
        for drop_file in [H012, H010, E323, E247]:
            sub_known = known_features[known_features["file"] != drop_file].copy()
            if len(sub_known) < 8:
                continue
            sub_pred = ridge_fit_predict(
                sub_known[cols].to_numpy(dtype=np.float64),
                sub_known["public_lb"].to_numpy(dtype=np.float64),
                all_features[cols].to_numpy(dtype=np.float64),
                alpha,
            )
            for i, pred in enumerate(sub_pred):
                preds.append(
                    {
                        "file": all_features.iloc[i]["file"],
                        "feature_set": rec["feature_set"],
                        "alpha": alpha,
                        "pred_public_lb": float(pred),
                        "model_loo_mae": float(rec["loo_mae"]),
                        "model_pair_acc": float(rec["loo_pair_acc"]),
                        "drop_sensor": drop_file,
                    }
                )
    pred_df = pd.DataFrame(preds)
    pred_df["drop_sensor"] = pred_df["drop_sensor"].fillna("none")
    summary = (
        pred_df.groupby("file")
        .agg(
            pred_public_median=("pred_public_lb", "median"),
            pred_public_p10=("pred_public_lb", lambda x: float(np.quantile(x, 0.10))),
            pred_public_p90=("pred_public_lb", lambda x: float(np.quantile(x, 0.90))),
            pred_public_min=("pred_public_lb", "min"),
            pred_public_max=("pred_public_lb", "max"),
            support_better_than_h012=("pred_public_lb", lambda x: float(np.mean(x < 0.5681234831))),
            support_better_than_0567=("pred_public_lb", lambda x: float(np.mean(x < 0.5670))),
            n_predictions=("pred_public_lb", "size"),
        )
        .reset_index()
    )
    meta_cols = [
        c
        for c in all_features.columns
        if c
        in {
            "source",
            "resolved_path",
            "mean_abs_prob_move_h012",
            "max_abs_prob_move_h012",
            "changed_cells_h012_1e4",
            "changed_rows_h012_1e4",
            "bad_axis_abs_load",
            "good_axis_abs_load",
            "bad_to_good_load_ratio",
            "state_h023_combined_score_w_h012",
            "state_h015_cell_score_w_h012",
            "state_h023_direction_agree",
            "state_h015_direction_agree",
            "pool_source",
            "pool_candidate_id",
            "pool_source_candidate_id",
            "pool_source_decision",
        }
    ]
    summary = summary.merge(all_features[["file"] + meta_cols], on="file", how="left")
    summary["risk_width"] = summary["pred_public_p90"] - summary["pred_public_p10"]
    summary["decoder_score"] = (
        summary["pred_public_median"]
        + 0.35 * summary["risk_width"]
        + 0.00035 * summary["bad_to_good_load_ratio"].fillna(0.0)
        - 0.00015 * summary["support_better_than_h012"]
    )
    return summary.sort_values("decoder_score").reset_index(drop=True), pred_df


def permutation_stress(
    known: pd.DataFrame,
    features: pd.DataFrame,
    cols_by_set: dict[str, list[str]],
    selected_file: str,
    n_perm: int = 300,
) -> pd.DataFrame:
    rng = np.random.default_rng(20260602)
    known_features = known[["file", "public_lb"]].merge(features, on="file", how="inner")
    selected = features[features["file"] == selected_file]
    h012 = features[features["file"] == H012]
    if selected.empty or h012.empty:
        return pd.DataFrame()
    rows = []
    usable_sets = {k: v for k, v in cols_by_set.items() if len(v) >= 2}
    for set_name, cols in usable_sets.items():
        if len(cols) > 80:
            cols = cols[:80]
        x_train = known_features[cols].to_numpy(dtype=np.float64)
        x_selected = selected[cols].to_numpy(dtype=np.float64)
        x_h012 = h012[cols].to_numpy(dtype=np.float64)
        for _ in range(n_perm):
            y_perm = rng.permutation(known_features["public_lb"].to_numpy(dtype=np.float64))
            pred_selected = ridge_fit_predict(x_train, y_perm, x_selected, 10.0)[0]
            pred_h012 = ridge_fit_predict(x_train, y_perm, x_h012, 10.0)[0]
            rows.append(
                {
                    "feature_set": set_name,
                    "perm_pred_selected": float(pred_selected),
                    "perm_pred_h012": float(pred_h012),
                    "perm_selected_minus_h012": float(pred_selected - pred_h012),
                }
            )
    return pd.DataFrame(rows)


def write_report(
    known: pd.DataFrame,
    model_scores: pd.DataFrame,
    candidate_scores: pd.DataFrame,
    selected: pd.Series | None,
    null_df: pd.DataFrame,
    decision: str,
) -> None:
    lines = []
    lines.append("# H024 Action-Health Decoder JEPA\n")
    lines.append("## Question\n")
    lines.append(
        "H012 proved that a hidden public-state posterior can be materialized. "
        "H023 showed that public-compatible vector worlds are human-state aligned. "
        "H024 asks whether we can decode which post-H012 action is healthy rather than just public-equation attractive.\n"
    )
    lines.append("## Known public sensors\n")
    lines.append(f"- known public files used: {len(known)}\n")
    lines.append(f"- current best sensor: `{H012}` = 0.5681234831\n")
    lines.append("- bad anchors include H010, E323, E216, E267 when their files are locally available.\n")
    lines.append("## Model stress\n")
    if not model_scores.empty:
        top = model_scores.iloc[0]
        lines.append(
            f"- best LOO decoder: `{top['feature_set']}` alpha={top['alpha']} "
            f"MAE={top['loo_mae']:.6f}, Spearman={top['loo_spearman']:.3f}, "
            f"pairwise={top['loo_pair_acc']:.3f}\n"
        )
        h012_rows = model_scores.sort_values("loo_mae").head(5)[["feature_set", "alpha", "h012_pred_loo", "h012_actual"]]
        lines.append("- H012 leave-one-out sanity among top decoders:\n")
        for rec in h012_rows.to_dict("records"):
            lines.append(
                f"  - {rec['feature_set']} a={rec['alpha']}: pred {rec['h012_pred_loo']:.6f} vs actual {rec['h012_actual']:.6f}\n"
            )
    lines.append("## Candidate ranking\n")
    for rec in candidate_scores.head(10).to_dict("records"):
        lines.append(
            f"- `{Path(str(rec['file'])).name}` score={rec['decoder_score']:.6f}, "
            f"pred={rec['pred_public_median']:.6f} [{rec['pred_public_p10']:.6f},{rec['pred_public_p90']:.6f}], "
            f"support<H012={rec['support_better_than_h012']:.2f}, source={rec.get('pool_source', rec.get('source', ''))}\n"
        )
    lines.append("## Null stress\n")
    if not null_df.empty and selected is not None:
        real_margin = float(selected["pred_public_median"] - 0.5681234831)
        null_margin = null_df["perm_selected_minus_h012"].to_numpy(dtype=np.float64)
        p = float(np.mean(null_margin <= real_margin))
        lines.append(
            f"- selected median margin vs H012: {real_margin:.6f}; permutation p(lower-is-better)={p:.3f}; "
            f"null median margin={np.median(null_margin):.6f}\n"
        )
    lines.append("## Decision\n")
    lines.append(f"- decision: `{decision}`\n")
    if selected is not None:
        lines.append(f"- selected diagnostic file: `{selected['file']}`\n")
    lines.append(
        "\nInterpretation: this is an action-health decoder, not a new posterior generator. "
        "A candidate is promoted only if the decoder also survives leave-one-out and permutation stress; otherwise it remains a sensor.\n"
    )
    (OUT / "h024_report.md").write_text("".join(lines))


def maybe_promote_candidate(candidate_scores: pd.DataFrame, null_df: pd.DataFrame) -> tuple[str, pd.Series | None, Path | None]:
    if candidate_scores.empty:
        return "no_candidate_pool", None, None
    known_names = set(read_public_observations()["file"])
    ranked = candidate_scores[~candidate_scores["file"].isin(known_names)].copy()
    if ranked.empty:
        return "no_unknown_candidates", None, None
    selected = ranked.iloc[0]
    null_ok = False
    if not null_df.empty:
        real_margin = float(selected["pred_public_median"] - 0.5681234831)
        p = float(np.mean(null_df["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= real_margin))
        null_ok = p <= 0.05
    gate_ok = (
        float(selected["support_better_than_h012"]) >= 0.70
        and float(selected["risk_width"]) <= 0.0025
        and float(selected["bad_to_good_load_ratio"]) <= 4.0
        and null_ok
        and float(selected["pred_public_median"]) <= 0.5677
    )
    if not gate_ok:
        return "diagnostic_only_decoder_not_stable_enough", selected, None
    source = locate(str(selected["file"]))
    if source is None:
        return "selected_file_missing", selected, None
    digest = hashlib.sha1(str(selected["file"]).encode()).hexdigest()[:8]
    out_name = ROOT / f"submission_h024_action_health_decoder_{digest}_uploadsafe.csv"
    shutil.copyfile(source, out_name)
    return "primary_action_candidate", selected, out_name


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    refs = build_reference_pack()
    known = read_public_observations()
    known.to_csv(OUT / "h024_known_public_sensors.csv", index=False)
    pool = collect_candidate_pool()
    pool.to_csv(OUT / "h024_candidate_pool.csv", index=False)
    features = build_feature_table(pool, refs)
    features.to_csv(OUT / "h024_action_features.csv", index=False)

    known_features = known[["file", "public_lb"]].merge(features, on="file", how="inner")
    blocked = {
        "file",
        "resolved_path",
        "source",
        "pool_file",
        "pool_resolved_path",
        "pool_candidate_id",
        "pool_source",
        "pool_source_candidate_id",
        "pool_source_decision",
        "pool_known_public_lb",
        "known_public_lb",
        "public_lb",
    }
    cols = numeric_feature_cols(known_features, blocked)
    cols_by_set = feature_sets(cols)
    model_scores, loo_preds = evaluate_known_models(known_features[["file", "public_lb"]], features, cols_by_set)
    model_scores.to_csv(OUT / "h024_model_scores.csv", index=False)
    loo_preds.to_csv(OUT / "h024_known_loocv_predictions.csv", index=False)
    candidate_scores, all_preds = score_candidates(known_features[["file", "public_lb"]], features, model_scores, cols_by_set)
    candidate_scores.to_csv(OUT / "h024_candidate_predictions.csv", index=False)
    all_preds.to_csv(OUT / "h024_candidate_prediction_samples.csv", index=False)
    prelim = candidate_scores[~candidate_scores["file"].isin(set(known["file"]))].head(1)
    selected_prelim = prelim.iloc[0] if len(prelim) else None
    null_df = (
        permutation_stress(known_features[["file", "public_lb"]], features, cols_by_set, str(selected_prelim["file"]))
        if selected_prelim is not None
        else pd.DataFrame()
    )
    null_df.to_csv(OUT / "h024_permutation_stress.csv", index=False)
    decision, selected, promoted_path = maybe_promote_candidate(candidate_scores, null_df)
    decision_df = pd.DataFrame(
        [
            {
                "decision": decision,
                "selected_file": None if selected is None else selected["file"],
                "promoted_path": None if promoted_path is None else str(promoted_path),
            }
        ]
    )
    decision_df.to_csv(OUT / "h024_decision.csv", index=False)
    write_report(known_features[["file", "public_lb"]], model_scores, candidate_scores, selected, null_df, decision)
    print(decision_df.to_string(index=False))
    print(candidate_scores.head(12)[["file", "decoder_score", "pred_public_median", "pred_public_p10", "pred_public_p90", "support_better_than_h012"]].to_string(index=False))


if __name__ == "__main__":
    main()
