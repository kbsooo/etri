from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402


GROUPS: dict[str, list[str]] = {
    "all": TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "stage": ["S1", "S2", "S3", "S4"],
    "s23": ["S2", "S3"],
    "core_q_s23": ["Q1", "Q2", "Q3", "S2", "S3"],
}


@dataclass(frozen=True)
class GraphSpec:
    name: str
    k: int
    time_weight: float
    pca_dim: int


@dataclass(frozen=True)
class FieldConfig:
    graph: str
    smooth_weight: float
    prior_weight: float
    label_weight: float

    @property
    def key(self) -> str:
        return (
            f"{self.graph}_sw{fmt(self.smooth_weight)}"
            f"_pw{fmt(self.prior_weight)}_lw{fmt(self.label_weight)}"
        )


def fmt(x: float) -> str:
    return f"{x:g}".replace(".", "p")


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = adv.clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def reduce_embedding(x: np.ndarray, pca_dim: int, seed: int) -> np.ndarray:
    xs = np.nan_to_num(np.asarray(x, dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0)
    xs = StandardScaler().fit_transform(xs)
    k = min(int(pca_dim), xs.shape[0] - 2, xs.shape[1])
    if k >= 8 and k < xs.shape[1]:
        xs = PCA(n_components=k, svd_solver="randomized", random_state=seed).fit_transform(xs)
    return np.asarray(xs, dtype=np.float32)


def build_graph(rows: pd.DataFrame, x: np.ndarray, spec: GraphSpec, seed: int) -> sparse.csr_matrix:
    z = reduce_embedding(x, spec.pca_dim, seed=seed)
    n = z.shape[0]
    nn = NearestNeighbors(n_neighbors=min(spec.k + 1, n), metric="euclidean")
    nn.fit(z)
    dist, ind = nn.kneighbors(z, return_distance=True)
    edge_r: list[int] = []
    edge_c: list[int] = []
    edge_w: list[float] = []
    for i in range(n):
        neigh = ind[i, 1:]
        d = dist[i, 1:]
        tau = float(np.median(d[d > 0])) if np.any(d > 0) else 1.0
        weights = np.exp(-d / max(tau, 1e-6))
        for j, w in zip(neigh, weights):
            edge_r.append(i)
            edge_c.append(int(j))
            edge_w.append(float(w))
            edge_r.append(int(j))
            edge_c.append(i)
            edge_w.append(float(w))

    for _sid, g in rows.groupby("subject_id", sort=False):
        pos = g["global_pos"].to_numpy(dtype=int)
        for a, b in zip(pos[:-1], pos[1:]):
            edge_r.extend([int(a), int(b)])
            edge_c.extend([int(b), int(a)])
            edge_w.extend([float(spec.time_weight), float(spec.time_weight)])

    w = sparse.coo_matrix((edge_w, (edge_r, edge_c)), shape=(n, n), dtype=np.float32).tocsr()
    w.sum_duplicates()
    row_sum = np.asarray(w.sum(axis=1)).ravel()
    inv = np.divide(1.0, row_sum, out=np.zeros_like(row_sum, dtype=np.float32), where=row_sum > 0)
    return sparse.diags(inv).dot(w).tocsr()


def train_label_matrix(rows: pd.DataFrame, train: pd.DataFrame) -> np.ndarray:
    y = np.full((len(rows), len(TARGETS)), np.nan, dtype=np.float32)
    tr = rows["split"].eq("train").to_numpy()
    idx = rows.loc[tr, "train_idx"].to_numpy(dtype=int)
    y[tr] = train.loc[idx, TARGETS].to_numpy(dtype=np.float32)
    return y


def propagate_field(
    w: sparse.csr_matrix,
    base_logit: np.ndarray,
    y: np.ndarray,
    known_mask: np.ndarray,
    config: FieldConfig,
    n_iter: int,
    label_logit: float = 3.5,
) -> np.ndarray:
    n = base_logit.shape[0]
    anchor_num = float(config.prior_weight) * base_logit.copy()
    anchor_den = np.full(n, float(config.prior_weight), dtype=np.float32)
    if known_mask.any():
        labels = np.where(y[known_mask] > 0.5, label_logit, -label_logit).astype(np.float32)
        anchor_num[known_mask] += float(config.label_weight) * labels
        anchor_den[known_mask] += float(config.label_weight)
    z = base_logit.copy()
    den = anchor_den[:, None] + float(config.smooth_weight)
    for _ in range(int(n_iter)):
        z = (anchor_num + float(config.smooth_weight) * w.dot(z)) / den
    return z.astype(np.float32)


def apply_group_blend(base_logit: np.ndarray, field_logit: np.ndarray, group: str, scale: float) -> np.ndarray:
    out = base_logit.copy()
    cols = [TARGETS.index(t) for t in GROUPS[group]]
    out[:, cols] = base_logit[:, cols] + float(scale) * (field_logit[:, cols] - base_logit[:, cols])
    return adv.clip(sigmoid(out))


def public_axis_for_file(file_name: str) -> dict[str, float]:
    try:
        return adv.public_axis_for(file_name)
    except Exception:
        return {"bad_axis_projection_ratio": np.nan, "good_axis_projection_ratio": np.nan}


def main() -> None:
    repeats = int(os.environ.get("GFJEPA_REPEATS", "3"))
    n_iter = int(os.environ.get("GFJEPA_ITERS", "55"))
    train, sub, base, base_sub = adv.read_data()
    rows, x, base_all = adv.build_row_representation(train, sub, base, base_sub)
    y = train_label_matrix(rows, train)
    y_train = train[TARGETS].to_numpy(dtype=np.float32)
    base_train_logit = adv.logit(base).astype(np.float32)
    base_all_logit = adv.logit(base_all).astype(np.float32)
    sub_row_mask = rows["split"].eq("submission").to_numpy()
    train_row_mask = rows["split"].eq("train").to_numpy()
    row_to_train_idx = rows.loc[train_row_mask, "train_idx"].to_numpy(dtype=int)

    graph_specs = [
        GraphSpec("gk6_t1", k=6, time_weight=1.0, pca_dim=48),
        GraphSpec("gk12_t1", k=12, time_weight=1.0, pca_dim=56),
        GraphSpec("gk20_t2", k=20, time_weight=2.0, pca_dim=64),
    ]
    graphs = {spec.name: build_graph(rows, x, spec, seed=302000 + i) for i, spec in enumerate(graph_specs)}
    configs = [
        FieldConfig(spec.name, smooth, prior, label)
        for spec in graph_specs
        for smooth in [0.10, 0.25, 0.50, 1.00]
        for prior in [0.25, 0.75]
        for label in [8.0, 20.0]
    ]
    scales = [0.15, 0.25, 0.35, 0.50, 0.75]

    field_sum = {cfg.key: np.zeros_like(base_train_logit, dtype=np.float32) for cfg in configs}
    field_count = {cfg.key: np.zeros(len(train), dtype=np.float32) for cfg in configs}
    fold_rows: list[dict[str, float | str | int]] = []
    for fold_i, (tr_idx, val_idx, fold_name) in enumerate(adv.geom.geometry_folds(train, sub, n_repeats=repeats, seed=302991)):
        known = adv.known_mask_for_train(rows, tr_idx)
        val_row_pos = rows.index[rows["split"].eq("train") & rows["train_idx"].isin(val_idx)].to_numpy(dtype=int)
        if len(val_row_pos) != len(val_idx):
            raise RuntimeError("validation row mapping failed")
        for cfg_i, cfg in enumerate(configs):
            field_all = propagate_field(
                graphs[cfg.graph],
                base_all_logit,
                y,
                known,
                cfg,
                n_iter=n_iter,
            )
            val_field = field_all[val_row_pos]
            field_sum[cfg.key][val_idx] += val_field
            field_count[cfg.key][val_idx] += 1.0
            if cfg_i % 12 == 0:
                pred = adv.clip(sigmoid(val_field))
                fold_rows.append(
                    {
                        "fold": fold_name,
                        "config": cfg.key,
                        "fold_i": fold_i,
                        "val_rows": int(len(val_idx)),
                        "base_loss": mean_loss(y_train[val_idx], base[val_idx]),
                        "field_loss_unblended": mean_loss(y_train[val_idx], pred),
                    }
                )
        print(f"graph-field {fold_name}: val={len(val_idx)} done", flush=True)

    fold_diag = pd.DataFrame(fold_rows)
    fold_diag.to_csv(OUT / "graph_field_jepa_inpainting_fold_diag.csv", index=False)

    summary_rows: list[dict[str, float | str | int]] = []
    base_loss = mean_loss(y_train, base)
    for cfg in configs:
        cnt = field_count[cfg.key]
        covered = cnt > 0
        field_logit = base_train_logit.copy()
        field_logit[covered] = field_sum[cfg.key][covered] / cnt[covered, None]
        for group in GROUPS:
            for scale in scales:
                pred = apply_group_blend(base_train_logit, field_logit, group, scale)
                summary_rows.append(
                    {
                        "config": cfg.key,
                        "graph": cfg.graph,
                        "smooth_weight": cfg.smooth_weight,
                        "prior_weight": cfg.prior_weight,
                        "label_weight": cfg.label_weight,
                        "group": group,
                        "scale": scale,
                        "covered_rows": int(covered.sum()),
                        "base_loss": base_loss,
                        "oof_loss": mean_loss(y_train, pred),
                        "oof_delta_vs_stage2": mean_loss(y_train, pred) - base_loss,
                    }
                )
    summary = pd.DataFrame(summary_rows).sort_values(["oof_loss", "scale", "group"]).reset_index(drop=True)
    summary.to_csv(OUT / "graph_field_jepa_inpainting_scan.csv", index=False)

    full_known = adv.known_mask_for_train(rows, np.arange(len(train)))
    base_sub_logit = adv.logit(base_sub[TARGETS].to_numpy(dtype=float)).astype(np.float32)
    emitted: list[dict[str, float | str]] = []
    for rank, row in enumerate(summary.head(24).itertuples(index=False)):
        cfg = next(c for c in configs if c.key == row.config)
        field_all = propagate_field(
            graphs[cfg.graph],
            base_all_logit,
            y,
            full_known,
            cfg,
            n_iter=n_iter,
        )
        sub_field = field_all[sub_row_mask]
        arr = apply_group_blend(base_sub_logit, sub_field, str(row.group), float(row.scale))
        out = base_sub.copy()
        out[TARGETS] = arr
        file_name = (
            f"submission_graph_field_jepa_{rank:02d}_"
            f"{cfg.key}_{row.group}_sc{fmt(float(row.scale))}.csv"
        )
        out.to_csv(OUT / file_name, index=False)
        axis = public_axis_for_file(file_name)
        emitted.append(
            {
                "candidate": file_name,
                "config": cfg.key,
                "group": row.group,
                "scale": float(row.scale),
                "oof_loss": float(row.oof_loss),
                "oof_delta_vs_stage2": float(row.oof_delta_vs_stage2),
                **axis,
            }
        )
    cand = pd.DataFrame(emitted).sort_values(["oof_loss", "scale"]).reset_index(drop=True)
    cand.to_csv(OUT / "graph_field_jepa_inpainting_candidate_summary.csv", index=False)

    best = cand.head(10)
    report = [
        "# Graph Field JEPA Inpainting",
        "",
        "Treat each train/submission row as a node in a JEPA-friendly joint embedding space, clamp known train labels, keep hidden rows on the stage2 prior, and inpaint a smooth 7-target logit field over the graph.",
        "",
        f"- repeats: {repeats}",
        f"- iterations: {n_iter}",
        f"- base full OOF loss: {base_loss:.6f}",
        f"- best emitted OOF loss: {float(best.iloc[0]['oof_loss']):.6f}",
        "",
        "## Top candidates",
        "",
        "```",
        best.to_string(index=False),
        "```",
        "",
        "## Interpretation",
        "",
        "This is a stronger JEPA usage than direct residual blending: the latent space defines which rows should agree, while the task labels are only anchors for visible context. If it helps, the gain should come from hidden-block consistency rather than from a single residual feature.",
    ]
    (OUT / "graph_field_jepa_inpainting_report.md").write_text("\n".join(report) + "\n")
    print(cand.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
