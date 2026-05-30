from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
SEED = 260991

sys.path.insert(0, str(OUT))
import broad_feature_addon_builder as stage2  # noqa: E402


@dataclass(frozen=True)
class PairRegime:
    name: str
    i: np.ndarray
    j: np.ndarray
    note: str


@dataclass(frozen=True)
class LatentSpace:
    name: str
    x: np.ndarray
    source: str
    raw_columns: int


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=float), 1e-5, 1.0 - 1e-5)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def finite(x: np.ndarray) -> np.ndarray:
    return np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)


def numeric_feature_cols(df: pd.DataFrame) -> list[str]:
    excluded = set(TARGETS + SUB_KEY + ["split", "row_id"])
    cols: list[str] = []
    for col in df.columns:
        if col in excluded:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        if s.notna().sum() >= 50 and s.nunique(dropna=True) > 1:
            cols.append(col)
    return cols


def scaled_matrix(df: pd.DataFrame, cols: list[str], top_cols: int = 2500) -> tuple[np.ndarray, int]:
    if not cols:
        raise ValueError("no numeric columns")
    raw = df[cols].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    med = raw.median(numeric_only=True).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    vals = raw.fillna(med).to_numpy(dtype=np.float64)
    vals = finite(vals)

    if vals.shape[1] > top_cols:
        var = np.nanvar(vals, axis=0)
        keep = np.argsort(var)[-top_cols:]
        vals = vals[:, keep]

    scaled = StandardScaler().fit_transform(vals)
    return finite(scaled), len(cols)


def pca_space(name: str, matrix: np.ndarray, source: str, raw_columns: int, dim: int) -> LatentSpace:
    n_comp = int(min(dim, matrix.shape[0] - 2, matrix.shape[1]))
    if n_comp < 2:
        raise ValueError(f"{name}: not enough dimensions for PCA")
    pca = PCA(n_components=n_comp, svd_solver="randomized", random_state=SEED)
    z = pca.fit_transform(matrix)
    z = StandardScaler().fit_transform(z)
    return LatentSpace(name=name, x=finite(z), source=source, raw_columns=raw_columns)


def load_pair_feature_space(train_feat: pd.DataFrame, sub_feat: pd.DataFrame) -> LatentSpace:
    all_feat = pd.concat([train_feat, sub_feat], axis=0, ignore_index=True)
    cols = numeric_feature_cols(all_feat)
    x, raw_cols = scaled_matrix(all_feat, cols, top_cols=3000)
    return pca_space("broad_stage2_pca64", x, "stage2 broad train/sub feature matrix", raw_cols, dim=64)


def load_existing_feature_space(name: str, train_path: Path, sub_path: Path, dim: int) -> LatentSpace | None:
    if not train_path.exists() or not sub_path.exists():
        return None
    train = pd.read_parquet(train_path).sort_values(KEY).reset_index(drop=True)
    sub = pd.read_parquet(sub_path).sort_values(KEY).reset_index(drop=True)
    all_df = pd.concat([train, sub], axis=0, ignore_index=True)
    cols = numeric_feature_cols(all_df)
    if len(cols) < 4:
        return None
    x, raw_cols = scaled_matrix(all_df, cols, top_cols=2500)
    return pca_space(name, x, f"{train_path.name} + {sub_path.name}", raw_cols, dim=dim)


def make_rows(train_raw: pd.DataFrame, sub_raw: pd.DataFrame) -> pd.DataFrame:
    tr = train_raw[SUB_KEY].copy()
    tr["split"] = "train"
    tr["row_in_split"] = np.arange(len(tr))
    su = sub_raw[SUB_KEY].copy()
    su["split"] = "submission"
    su["row_in_split"] = np.arange(len(su))
    rows = pd.concat([tr, su], axis=0, ignore_index=True)
    rows["sleep_date"] = pd.to_datetime(rows["sleep_date"])
    rows["lifelog_date"] = pd.to_datetime(rows["lifelog_date"])
    return rows


def lag_pairs(rows: pd.DataFrame, lag: int, split: str | None, name: str) -> PairRegime:
    pairs_i: list[int] = []
    pairs_j: list[int] = []
    frame = rows.reset_index().rename(columns={"index": "global_index"})
    if split is not None:
        frame = frame[frame["split"] == split]
    for _, sub in frame.sort_values(KEY).groupby("subject_id", sort=False):
        idx = sub["global_index"].to_numpy(dtype=int)
        if len(idx) > lag:
            pairs_i.extend(idx[:-lag].tolist())
            pairs_j.extend(idx[lag:].tolist())
    note = f"same-subject lag={lag}" + (f", split={split}" if split else ", all splits")
    return PairRegime(name, np.asarray(pairs_i, dtype=int), np.asarray(pairs_j, dtype=int), note)


def same_day_cross_subject_pairs(rows: pd.DataFrame) -> PairRegime:
    pairs_i: list[int] = []
    pairs_j: list[int] = []
    frame = rows.reset_index().rename(columns={"index": "global_index"}).sort_values(["lifelog_date", "subject_id"])
    for _, sub in frame.groupby("lifelog_date", sort=False):
        idx = sub["global_index"].to_numpy(dtype=int)
        if len(idx) >= 2:
            pairs_i.extend(idx[:-1].tolist())
            pairs_j.extend(idx[1:].tolist())
    return PairRegime(
        "calendar_same_day_cross_subject",
        np.asarray(pairs_i, dtype=int),
        np.asarray(pairs_j, dtype=int),
        "adjacent subjects on the same lifelog date",
    )


def split_boundary_pairs(rows: pd.DataFrame) -> PairRegime:
    pairs_i: list[int] = []
    pairs_j: list[int] = []
    frame = rows.reset_index().rename(columns={"index": "global_index"}).sort_values(KEY)
    for _, sub in frame.groupby("subject_id", sort=False):
        idx = sub["global_index"].to_numpy(dtype=int)
        splits = sub["split"].to_numpy()
        if len(idx) < 2:
            continue
        mask = splits[:-1] != splits[1:]
        pairs_i.extend(idx[:-1][mask].tolist())
        pairs_j.extend(idx[1:][mask].tolist())
    return PairRegime(
        "train_submission_subject_boundary",
        np.asarray(pairs_i, dtype=int),
        np.asarray(pairs_j, dtype=int),
        "same-subject adjacent rows where split changes",
    )


def feature_nn_pairs(rows: pd.DataFrame, z: np.ndarray, rank: int, name: str) -> PairRegime:
    nbrs = NearestNeighbors(n_neighbors=min(rank + 1, len(rows)), metric="euclidean")
    nbrs.fit(z)
    _, ind = nbrs.kneighbors(z)
    j = ind[:, min(rank, ind.shape[1] - 1)]
    i = np.arange(len(rows), dtype=int)
    return PairRegime(name, i, j.astype(int), f"feature nearest-neighbor rank={rank} in broad PCA space")


def target_neighbor_pairs(train_raw: pd.DataFrame) -> PairRegime:
    y = train_raw[TARGETS].to_numpy(dtype=float)
    nbrs = NearestNeighbors(n_neighbors=min(8, len(y)), metric="hamming")
    nbrs.fit(y)
    _, ind = nbrs.kneighbors(y)
    i = np.arange(len(y), dtype=int)
    j = ind[:, 1].astype(int)
    return PairRegime(
        "train_target_manifold_neighbor",
        i,
        j,
        "train-only nearest neighbor in true 7-label Hamming space; diagnostic upper-bound, not inference-safe",
    )


def make_pair_regimes(rows: pd.DataFrame, broad_z: np.ndarray, train_raw: pd.DataFrame) -> list[PairRegime]:
    regimes = [
        lag_pairs(rows, 1, None, "subject_lag1_all"),
        lag_pairs(rows, 2, None, "subject_lag2_all"),
        lag_pairs(rows, 4, None, "subject_lag4_all"),
        lag_pairs(rows, 8, None, "subject_lag8_all"),
        lag_pairs(rows, 1, "train", "subject_lag1_train"),
        lag_pairs(rows, 1, "submission", "subject_lag1_submission"),
        same_day_cross_subject_pairs(rows),
        split_boundary_pairs(rows),
        feature_nn_pairs(rows, broad_z, 1, "feature_nn1_all"),
        feature_nn_pairs(rows, broad_z, 3, "feature_nn3_all"),
        target_neighbor_pairs(train_raw),
    ]
    return [r for r in regimes if len(r.i) >= 10]


def projection_moments(x: np.ndarray, rng: np.random.Generator, n_proj: int = 48) -> dict[str, float]:
    xx = finite(x)
    if len(xx) < 8:
        return {"skew_abs": float("nan"), "excess_kurt_abs": float("nan")}
    dim = xx.shape[1]
    k = min(n_proj, max(4, dim * 2))
    proj = rng.normal(size=(dim, k))
    proj /= np.maximum(np.linalg.norm(proj, axis=0, keepdims=True), 1e-12)
    vals = xx @ proj
    vals = vals - vals.mean(axis=0, keepdims=True)
    vals = vals / np.maximum(vals.std(axis=0, keepdims=True), 1e-9)
    skew = np.mean(vals**3, axis=0)
    excess = np.mean(vals**4, axis=0) - 3.0
    return {
        "skew_abs": float(np.mean(np.abs(skew))),
        "excess_kurt_abs": float(np.mean(np.abs(excess))),
    }


def gaussian_score(stats: dict[str, float]) -> float:
    skew = 0.0 if not np.isfinite(stats["skew_abs"]) else stats["skew_abs"]
    kurt = 0.0 if not np.isfinite(stats["excess_kurt_abs"]) else stats["excess_kurt_abs"]
    return float(1.0 / (1.0 + skew + 0.5 * kurt))


def covariance_health(x: np.ndarray) -> dict[str, float]:
    if len(x) < 4:
        return {
            "effective_rank": float("nan"),
            "rank_fraction": float("nan"),
            "cov_eig_cv": float("nan"),
            "cov_condition": float("nan"),
        }
    cov = np.cov(finite(x), rowvar=False)
    eig = np.linalg.eigvalsh(cov)
    eig = np.maximum(eig, 1e-12)
    prob = eig / eig.sum()
    effective_rank = float(np.exp(-(prob * np.log(prob)).sum()))
    rank_fraction = float(effective_rank / len(eig))
    return {
        "effective_rank": effective_rank,
        "rank_fraction": rank_fraction,
        "cov_eig_cv": float(eig.std() / max(eig.mean(), 1e-12)),
        "cov_condition": float(eig.max() / eig.min()),
    }


def corr_by_dim(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    aa = finite(a)
    bb = finite(b)
    aa = aa - aa.mean(axis=0, keepdims=True)
    bb = bb - bb.mean(axis=0, keepdims=True)
    num = np.sum(aa * bb, axis=0)
    den = np.sqrt(np.sum(aa**2, axis=0) * np.sum(bb**2, axis=0))
    return np.divide(num, np.maximum(den, 1e-12))


def triangular_score(value: float, peak: float, left: float, right: float) -> float:
    if not np.isfinite(value):
        return 0.0
    if value <= peak:
        return float(np.clip((value - left) / max(peak - left, 1e-9), 0.0, 1.0))
    return float(np.clip((right - value) / max(right - peak, 1e-9), 0.0, 1.0))


def load_frontier_deltas(rows: pd.DataFrame) -> dict[str, np.ndarray]:
    files = {
        "e101_minus_e95": OUT / "submission_e101_q2s3tail_177569bc.csv",
        "e154_minus_e95": OUT / "submission_e154_s3repair_9f2e2e73.csv",
        "e176_minus_e95": OUT / "submission_e176_abl_q2_to0p75_91e49725.csv",
    }
    base_file = OUT / "submission_e95_hardtail_541e3973.csv"
    if not base_file.exists():
        return {}
    base = pd.read_csv(base_file, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    out: dict[str, np.ndarray] = {}
    for name, path in files.items():
        if not path.exists():
            continue
        cand = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        if not cand[SUB_KEY].equals(base[SUB_KEY]):
            continue
        out[name] = logit(cand[TARGETS].to_numpy(dtype=float)) - logit(base[TARGETS].to_numpy(dtype=float))
    return out


def frontier_smoothness(
    regime: PairRegime,
    rows: pd.DataFrame,
    frontier_deltas: dict[str, np.ndarray],
) -> tuple[float, int]:
    if not frontier_deltas:
        return float("nan"), 0
    split = rows["split"].to_numpy()
    sub_pos = rows["row_in_split"].to_numpy(dtype=int)
    mask = (split[regime.i] == "submission") & (split[regime.j] == "submission")
    if int(mask.sum()) < 10:
        return float("nan"), int(mask.sum())
    scores = []
    for delta in frontier_deltas.values():
        di = delta[sub_pos[regime.i[mask]]]
        dj = delta[sub_pos[regime.j[mask]]]
        pair_rmse = float(np.sqrt(np.mean((di - dj) ** 2)))
        global_rmse = float(np.sqrt(np.mean(delta**2)))
        scores.append(1.0 / (1.0 + pair_rmse / max(global_rmse, 1e-12)))
    return float(np.mean(scores)), int(mask.sum())


def label_consistency(regime: PairRegime, rows: pd.DataFrame, train_raw: pd.DataFrame) -> tuple[float, int]:
    split = rows["split"].to_numpy()
    train_pos = rows["row_in_split"].to_numpy(dtype=int)
    mask = (split[regime.i] == "train") & (split[regime.j] == "train")
    if int(mask.sum()) < 10:
        return float("nan"), int(mask.sum())
    y = train_raw[TARGETS].to_numpy(dtype=float)
    yi = y[train_pos[regime.i[mask]]]
    yj = y[train_pos[regime.j[mask]]]
    return float(1.0 - np.mean(np.abs(yi - yj))), int(mask.sum())


def split_stationarity(regime: PairRegime, rows: pd.DataFrame, dist: np.ndarray) -> float:
    split = rows["split"].to_numpy()
    tags = np.where(
        (split[regime.i] == "train") & (split[regime.j] == "train"),
        "train",
        np.where(
            (split[regime.i] == "submission") & (split[regime.j] == "submission"),
            "submission",
            "mixed",
        ),
    )
    means = []
    for tag in ["train", "submission", "mixed"]:
        vals = dist[tags == tag]
        if len(vals) >= 10:
            means.append(float(vals.mean()))
    if len(means) < 2:
        return float("nan")
    return float(np.std(means) / max(np.mean(means), 1e-12))


def score_regime(latent: LatentSpace, regime: PairRegime, rows: pd.DataFrame, train_raw: pd.DataFrame, frontier: dict[str, np.ndarray]) -> dict[str, object]:
    digest = hashlib.sha256(f"{latent.name}|{regime.name}".encode("utf-8")).hexdigest()
    rng = np.random.default_rng(SEED + int(digest[:10], 16) % 1_000_000)
    i = regime.i
    j = regime.j
    if len(i) > 4000:
        keep = rng.choice(len(i), size=4000, replace=False)
        i = i[keep]
        j = j[keep]

    x = latent.x
    xi = x[i]
    xj = x[j]
    diff = xj - xi
    rho = corr_by_dim(xi, xj)
    dist = np.sqrt(np.mean(diff**2, axis=1))

    random_j = rng.permutation(len(x))[: len(i)]
    random_dist = np.sqrt(np.mean((xi - x[random_j]) ** 2, axis=1))
    alignment_ratio = float(dist.mean() / max(random_dist.mean(), 1e-12))

    marg = projection_moments(x, rng)
    inc = projection_moments(diff, rng)
    cov = covariance_health(x)
    frontier_score, frontier_n = frontier_smoothness(regime, rows, frontier)
    lbl_cons, lbl_n = label_consistency(regime, rows, train_raw)

    rho_abs_mean = float(np.mean(np.abs(rho)))
    rho_std = float(np.std(rho))
    rho_intermediate = triangular_score(rho_abs_mean, peak=0.55, left=0.08, right=0.93)
    alignment_info = triangular_score(alignment_ratio, peak=0.45, left=0.05, right=0.92)
    marginal_gauss = gaussian_score(marg)
    increment_gauss = gaussian_score(inc)
    rank_score = float(np.clip(cov["rank_fraction"] / 0.45, 0.0, 1.0))
    rho_isotropy = float(1.0 / (1.0 + rho_std))
    boundary = 0.50 if not np.isfinite(frontier_score) else frontier_score
    readiness = (
        0.16 * marginal_gauss
        + 0.24 * increment_gauss
        + 0.22 * rho_intermediate
        + 0.14 * alignment_info
        + 0.12 * rank_score
        + 0.07 * rho_isotropy
        + 0.05 * boundary
    )

    if readiness >= 0.65 and rho_intermediate >= 0.45 and increment_gauss >= 0.35:
        decision = "true_jepa_candidate"
    elif readiness >= 0.52:
        decision = "energy_or_auxiliary"
    else:
        decision = "diagnostic_only"

    return {
        "latent": latent.name,
        "latent_source": latent.source,
        "latent_dim": int(x.shape[1]),
        "latent_raw_columns": int(latent.raw_columns),
        "pair_regime": regime.name,
        "pair_note": regime.note,
        "pair_count": int(len(regime.i)),
        "sampled_pair_count": int(len(i)),
        "rho_abs_mean": rho_abs_mean,
        "rho_mean": float(np.mean(rho)),
        "rho_std": rho_std,
        "rho_q10": float(np.quantile(rho, 0.10)),
        "rho_q90": float(np.quantile(rho, 0.90)),
        "alignment_ratio": alignment_ratio,
        "positive_dist_mean": float(dist.mean()),
        "random_dist_mean": float(random_dist.mean()),
        "marginal_skew_abs": marg["skew_abs"],
        "marginal_excess_kurt_abs": marg["excess_kurt_abs"],
        "increment_skew_abs": inc["skew_abs"],
        "increment_excess_kurt_abs": inc["excess_kurt_abs"],
        "marginal_gauss_score": marginal_gauss,
        "increment_gauss_score": increment_gauss,
        "effective_rank": cov["effective_rank"],
        "rank_fraction": cov["rank_fraction"],
        "cov_eig_cv": cov["cov_eig_cv"],
        "cov_condition": cov["cov_condition"],
        "rho_intermediate_score": rho_intermediate,
        "alignment_info_score": alignment_info,
        "rank_score": rank_score,
        "rho_isotropy_score": rho_isotropy,
        "frontier_smoothness": frontier_score,
        "frontier_pair_count": frontier_n,
        "train_label_consistency": lbl_cons,
        "train_label_pair_count": lbl_n,
        "split_dist_cv": split_stationarity(regime, rows, dist),
        "lejepa_readiness": float(readiness),
        "decision": decision,
    }


def write_report(summary: pd.DataFrame) -> None:
    top = summary.sort_values("lejepa_readiness", ascending=False).head(18)
    best_by_regime = summary.sort_values("lejepa_readiness", ascending=False).groupby("pair_regime", as_index=False).head(1)
    decisions = summary["decision"].value_counts().to_dict()

    def table(df: pd.DataFrame, cols: list[str]) -> str:
        lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
        for _, row in df[cols].iterrows():
            vals = []
            for col in cols:
                val = row[col]
                if isinstance(val, float):
                    vals.append(f"{val:.6g}")
                else:
                    vals.append(str(val))
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)

    cols = [
        "latent",
        "pair_regime",
        "lejepa_readiness",
        "decision",
        "rho_abs_mean",
        "alignment_ratio",
        "increment_gauss_score",
        "rank_fraction",
        "frontier_smoothness",
        "train_label_consistency",
    ]
    lines = [
        "# E207 LeJEPA Identifiability Conditions Audit",
        "",
        "Purpose: turn the `When Does LeJEPA Learn a World Model?` reading into a precondition audit before training a larger JEPA. The audit scores whether a proposed positive-pair regime has the rough ingredients required for identifiable LeJEPA-style learning: intermediate autocorrelation, Gaussian-ish increments, non-collapsed rank, useful alignment gap, and some compatibility with known frontier movements.",
        "",
        "This is not a submission generator. It is a regime selector for any future true-JEPA run.",
        "",
        "## Decision Counts",
        "",
        "```json",
        str(decisions),
        "```",
        "",
        "## Best Regime/Latent Combinations",
        "",
        table(top, cols),
        "",
        "## Best Latent Per Pair Regime",
        "",
        table(best_by_regime.sort_values("lejepa_readiness", ascending=False), cols),
        "",
        "## Interpretation",
        "",
        "- `true_jepa_candidate` means the pair regime is plausible enough for a real context-to-target JEPA training attempt.",
        "- `energy_or_auxiliary` means the structure is visible but should first be used as an energy/gate or diagnostic feature.",
        "- `diagnostic_only` means a bigger JEPA would probably learn shortcuts, collapse, or a non-identifiable smooth feature under this regime.",
        "",
        "Immediate rule: do not train a single JEPA over all pair types. Choose the top one or two regimes only, and treat same-family high-CV latents that fail this audit as gates rather than frontier submissions.",
        "",
    ]
    (OUT / "e207_lejepa_identifiability_conditions_audit_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    train_raw, sub_raw, train_feat, sub_feat = stage2.build_frames()
    rows = make_rows(train_raw, sub_raw)
    broad_space = load_pair_feature_space(train_feat, sub_feat)

    latent_spaces: list[LatentSpace] = [broad_space]
    optional_specs = [
        ("jepa_group_pca48", JEPA / "train_jepa_features.parquet", JEPA / "submission_jepa_features.parquet", 48),
        ("rawijepa_pca48", JEPA / "train_rawijepa_features.parquet", JEPA / "submission_rawijepa_features.parquet", 48),
        ("neural_jepa_pca48", JEPA / "train_neural_jepa_features.parquet", JEPA / "submission_neural_jepa_features.parquet", 48),
        ("block_canvas_pca48", JEPA / "block_canvas_jepa_train_features.parquet", JEPA / "block_canvas_jepa_submission_features.parquet", 48),
        ("lejepa_l0p2_d32_pca48", JEPA / "lejepa_block_canvas_l0p2_d32_train_features.parquet", JEPA / "lejepa_block_canvas_l0p2_d32_submission_features.parquet", 48),
        ("lejepa_l0p05_d32_pca48", JEPA / "lejepa_block_canvas_l0p05_d32_train_features.parquet", JEPA / "lejepa_block_canvas_l0p05_d32_submission_features.parquet", 48),
    ]
    for name, tr_path, sub_path, dim in optional_specs:
        latent = load_existing_feature_space(name, tr_path, sub_path, dim=dim)
        if latent is not None:
            latent_spaces.append(latent)

    regimes = make_pair_regimes(rows, broad_space.x, train_raw)
    frontier = load_frontier_deltas(rows)
    records = []
    for latent in latent_spaces:
        for regime in regimes:
            records.append(score_regime(latent, regime, rows, train_raw, frontier))

    summary = pd.DataFrame(records).sort_values(["lejepa_readiness", "increment_gauss_score"], ascending=[False, False])
    summary.to_csv(OUT / "e207_lejepa_identifiability_conditions_audit_summary.csv", index=False)
    write_report(summary)
    print(summary.head(20)[["latent", "pair_regime", "lejepa_readiness", "decision", "rho_abs_mean", "alignment_ratio", "increment_gauss_score"]].to_string(index=False))


if __name__ == "__main__":
    main()
