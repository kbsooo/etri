from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
SEED = 260991

sys.path.insert(0, str(OUT))
import broad_feature_addon_builder as stage2  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402
import e207_lejepa_identifiability_conditions_audit as e207  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402


@dataclass(frozen=True)
class TrainResult:
    seed: int
    train_mse: float
    val_mse: float
    copy_self_mse: float
    mean_target_mse: float
    random_pair_mse: float
    hidden_var_penalty: float
    pred_var_penalty: float
    hidden_cov_penalty: float
    epochs: int
    hidden: np.ndarray
    pred: np.ndarray


class NeighborJEPA(torch.nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, emb_dim: int, output_dim: int) -> None:
        super().__init__()
        self.encoder = torch.nn.Sequential(
            torch.nn.Linear(input_dim, hidden_dim),
            torch.nn.GELU(),
            torch.nn.LayerNorm(hidden_dim),
            torch.nn.Linear(hidden_dim, emb_dim),
        )
        self.predictor = torch.nn.Sequential(
            torch.nn.LayerNorm(emb_dim),
            torch.nn.Linear(emb_dim, hidden_dim),
            torch.nn.GELU(),
            torch.nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        z = self.encoder(x)
        pred = self.predictor(z)
        return z, pred


def finite(x: np.ndarray) -> np.ndarray:
    return np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(p, dtype=float), 1e-5, 1.0 - 1e-5)


def logit(p: np.ndarray) -> np.ndarray:
    pp = clip(p)
    return np.log(pp / (1.0 - pp))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def family_name(col: str) -> str:
    if "__" in col:
        return col.split("__", 1)[0]
    return "base"


def family_context_matrix(train_feat: pd.DataFrame, sub_feat: pd.DataFrame) -> tuple[np.ndarray, list[dict[str, object]]]:
    all_feat = pd.concat([train_feat, sub_feat], axis=0, ignore_index=True)
    cols = e207.numeric_feature_cols(all_feat)
    by_family: dict[str, list[str]] = {}
    for col in cols:
        by_family.setdefault(family_name(col), []).append(col)

    blocks: list[np.ndarray] = []
    meta: list[dict[str, object]] = []
    for fam, fam_cols in sorted(by_family.items()):
        if len(fam_cols) < 12:
            continue
        x, raw_cols = e207.scaled_matrix(all_feat, fam_cols, top_cols=900)
        n_comp = int(min(10, max(3, len(fam_cols) // 35), x.shape[0] - 2, x.shape[1]))
        if n_comp < 3:
            continue
        pca = PCA(n_components=n_comp, svd_solver="randomized", random_state=SEED + len(meta))
        z = pca.fit_transform(x)
        z = StandardScaler().fit_transform(z)
        blocks.append(finite(z))
        meta.append(
            {
                "family": fam,
                "columns": int(raw_cols),
                "components": int(n_comp),
                "explained_variance": float(np.sum(pca.explained_variance_ratio_)),
            }
        )

    if not blocks:
        raise ValueError("no feature-family context blocks")
    context = np.hstack(blocks)
    context = StandardScaler().fit_transform(context)
    return finite(context), meta


def variance_penalty(x: torch.Tensor, eps: float = 1e-4) -> torch.Tensor:
    std = torch.sqrt(x.var(dim=0, unbiased=False) + eps)
    return torch.relu(1.0 - std).mean()


def covariance_penalty(x: torch.Tensor) -> torch.Tensor:
    if x.shape[0] < 2:
        return x.sum() * 0.0
    xc = x - x.mean(dim=0, keepdim=True)
    cov = (xc.T @ xc) / max(x.shape[0] - 1, 1)
    off = cov - torch.diag(torch.diag(cov))
    return (off**2).sum() / x.shape[1]


def train_neighbor_jepa(
    context: np.ndarray,
    target: np.ndarray,
    pairs_i: np.ndarray,
    pairs_j: np.ndarray,
    seed: int,
    emb_dim: int = 32,
    epochs: int = 520,
) -> TrainResult:
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    device = torch.device("cpu")
    x_all = torch.tensor(context, dtype=torch.float32, device=device)
    t_all = torch.tensor(target, dtype=torch.float32, device=device)

    order = rng.permutation(len(pairs_i))
    val_size = max(40, int(round(0.20 * len(order))))
    val_sel = order[:val_size]
    tr_sel = order[val_size:]
    tr_i = torch.tensor(pairs_i[tr_sel], dtype=torch.long, device=device)
    tr_j = torch.tensor(pairs_j[tr_sel], dtype=torch.long, device=device)
    va_i = torch.tensor(pairs_i[val_sel], dtype=torch.long, device=device)
    va_j = torch.tensor(pairs_j[val_sel], dtype=torch.long, device=device)

    model = NeighborJEPA(context.shape[1], hidden_dim=96, emb_dim=emb_dim, output_dim=target.shape[1]).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=2.0e-3, weight_decay=1.0e-4)

    best_state: dict[str, torch.Tensor] | None = None
    best_val = float("inf")
    bad_epochs = 0
    for epoch in range(epochs):
        model.train()
        z, pred = model(x_all[tr_i])
        loss_pred = torch.nn.functional.mse_loss(pred, t_all[tr_j])
        loss = loss_pred + 0.025 * variance_penalty(z) + 0.010 * covariance_penalty(z) + 0.010 * variance_penalty(pred)
        opt.zero_grad()
        loss.backward()
        opt.step()

        if epoch % 10 == 0 or epoch == epochs - 1:
            model.eval()
            with torch.no_grad():
                z_val, pred_val = model(x_all[va_i])
                val_loss = torch.nn.functional.mse_loss(pred_val, t_all[va_j]).item()
                val_loss += 0.002 * variance_penalty(z_val).item()
            if val_loss < best_val - 1e-6:
                best_val = val_loss
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
                bad_epochs = 0
            else:
                bad_epochs += 10
            if bad_epochs >= 140:
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        hidden_t, pred_t = model(x_all)
        pred_train = model(x_all[tr_i])[1]
        pred_val = model(x_all[va_i])[1]
        train_mse = torch.nn.functional.mse_loss(pred_train, t_all[tr_j]).item()
        val_mse = torch.nn.functional.mse_loss(pred_val, t_all[va_j]).item()
        hv = variance_penalty(hidden_t).item()
        pv = variance_penalty(pred_t).item()
        hc = covariance_penalty(hidden_t).item()

    target_np = finite(target)
    copy_self = float(np.mean((target_np[pairs_i[val_sel]] - target_np[pairs_j[val_sel]]) ** 2))
    mean_target = target_np[pairs_j[tr_sel]].mean(axis=0, keepdims=True)
    mean_target_mse = float(np.mean((mean_target - target_np[pairs_j[val_sel]]) ** 2))
    random_j = rng.permutation(len(target_np))[: len(val_sel)]
    random_pair_mse = float(np.mean((target_np[pairs_i[val_sel]] - target_np[random_j]) ** 2))

    return TrainResult(
        seed=seed,
        train_mse=float(train_mse),
        val_mse=float(val_mse),
        copy_self_mse=copy_self,
        mean_target_mse=mean_target_mse,
        random_pair_mse=random_pair_mse,
        hidden_var_penalty=float(hv),
        pred_var_penalty=float(pv),
        hidden_cov_penalty=float(hc),
        epochs=int(epoch + 1),
        hidden=finite(hidden_t.cpu().numpy()),
        pred=finite(pred_t.cpu().numpy()),
    )


def build_feature_frame(
    rows: pd.DataFrame,
    target: np.ndarray,
    pair_j: np.ndarray,
    results: list[TrainResult],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    feature_map: dict[str, np.ndarray] = {}
    pred_stack = np.stack([r.pred for r in results], axis=0)
    hidden_stack = np.stack([r.hidden for r in results], axis=0)
    pred_mean = pred_stack.mean(axis=0)
    pred_std = pred_stack.std(axis=0)
    hidden_mean = hidden_stack.mean(axis=0)

    target_nn = target[pair_j]
    residual_self = pred_mean - target
    residual_nn = pred_mean - target_nn

    feature_map["e208_pred_norm"] = np.linalg.norm(pred_mean, axis=1)
    feature_map["e208_hidden_norm"] = np.linalg.norm(hidden_mean, axis=1)
    feature_map["e208_pred_seed_std"] = pred_std.mean(axis=1)
    feature_map["e208_resid_self_norm"] = np.linalg.norm(residual_self, axis=1)
    feature_map["e208_resid_nn_norm"] = np.linalg.norm(residual_nn, axis=1)
    feature_map["e208_resid_self_abs_mean"] = np.mean(np.abs(residual_self), axis=1)
    feature_map["e208_resid_nn_abs_mean"] = np.mean(np.abs(residual_nn), axis=1)
    feature_map["e208_pred_to_self_cos"] = np.sum(pred_mean * target, axis=1) / np.maximum(
        np.linalg.norm(pred_mean, axis=1) * np.linalg.norm(target, axis=1), 1e-9
    )
    feature_map["e208_pred_to_nn_cos"] = np.sum(pred_mean * target_nn, axis=1) / np.maximum(
        np.linalg.norm(pred_mean, axis=1) * np.linalg.norm(target_nn, axis=1), 1e-9
    )
    feature_map["e208_nn_target_dist"] = np.linalg.norm(target_nn - target, axis=1)

    for k in range(min(16, pred_mean.shape[1])):
        feature_map[f"e208_pred_pc{k:02d}"] = pred_mean[:, k]
        feature_map[f"e208_resid_self_pc{k:02d}"] = residual_self[:, k]
        feature_map[f"e208_resid_nn_pc{k:02d}"] = residual_nn[:, k]
    for k in range(min(12, hidden_mean.shape[1])):
        feature_map[f"e208_hidden_z{k:02d}"] = hidden_mean[:, k]
    for seed_i, r in enumerate(results):
        feature_map[f"e208_s{seed_i}_pred_norm"] = np.linalg.norm(r.pred, axis=1)
        feature_map[f"e208_s{seed_i}_hidden_norm"] = np.linalg.norm(r.hidden, axis=1)
        for k in range(min(6, r.pred.shape[1])):
            feature_map[f"e208_s{seed_i}_pred_pc{k:02d}"] = r.pred[:, k]

    feature_df = pd.concat([rows[SUB_KEY].reset_index(drop=True), pd.DataFrame(feature_map)], axis=1)
    meta_rows = []
    rng = np.random.default_rng(SEED + 208)
    for name, matrix in {
        "pred_mean": pred_mean,
        "hidden_mean": hidden_mean,
        "pred_resid_self": residual_self,
        "pred_resid_nn": residual_nn,
    }.items():
        moments = e207.projection_moments(matrix, rng)
        cov = e207.covariance_health(matrix)
        meta_rows.append({"embedding": name, **moments, **cov})
    return feature_df, pd.DataFrame(meta_rows)


def fit_corrected(
    train_rows: pd.DataFrame,
    pred_rows: pd.DataFrame,
    train_base: np.ndarray,
    pred_base: np.ndarray,
    target: str,
    feature: str,
    mode: str,
    c_value: float,
) -> np.ndarray:
    j = TARGETS.index(target)
    z_tr, z_pr = broad.transform_pair(train_rows, pred_rows, feature, mode)
    x_tr = np.column_stack([logit(train_base[:, j]), z_tr])
    x_pr = np.column_stack([logit(pred_base[:, j]), z_pr])
    y = train_rows[target].to_numpy(dtype=int)
    if y.min() == y.max():
        return np.full(len(pred_rows), float(y.mean()))
    clf = LogisticRegression(C=float(c_value), solver="lbfgs", max_iter=600)
    clf.fit(x_tr, y)
    return clip(clf.predict_proba(x_pr)[:, 1])


def geometry_summary(train_raw: pd.DataFrame, sub_raw: pd.DataFrame, df: pd.DataFrame, base: np.ndarray, op: dict[str, object]) -> dict[str, float]:
    y = train_raw[TARGETS].to_numpy(dtype=int)
    rows = []
    target = str(op["target"])
    feature = str(op["feature"])
    mode = str(op["mode"])
    c_value = float(op["c_value"])
    weight = float(op["best_weight"])
    j = TARGETS.index(target)
    for tr_idx, val_idx, fold in geom.geometry_folds(train_raw, sub_raw, n_repeats=8):
        ref = df.iloc[tr_idx].reset_index(drop=True)
        val = df.iloc[val_idx].reset_index(drop=True)
        val_pred = base[val_idx].copy()
        corrected = fit_corrected(ref, val, base[tr_idx].copy(), val_pred, target, feature, mode, c_value)
        val_pred[:, j] = clip((1.0 - weight) * val_pred[:, j] + weight * corrected)
        rows.append(
            {
                "fold": fold,
                "delta_mean": mean_loss(y[val_idx], val_pred) - mean_loss(y[val_idx], base[val_idx]),
                "delta_target": loss_col(y[val_idx, j], val_pred[:, j]) - loss_col(y[val_idx, j], base[val_idx, j]),
            }
        )
    g = pd.DataFrame(rows)
    return {
        "geometry_delta_mean": float(g["delta_mean"].mean()),
        "geometry_win_rate": float((g["delta_mean"] < 0).mean()),
        "geometry_target_delta": float(g["delta_target"].mean()),
        "geometry_target_win_rate": float((g["delta_target"] < 0).mean()),
    }


def downstream_scan(train_raw: pd.DataFrame, sub_raw: pd.DataFrame, feature_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base = clip(np.load(OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"))
    df = train_raw[SUB_KEY + TARGETS].merge(feature_df, on=SUB_KEY, how="left")
    cols = [c for c in df.columns if c.startswith("e208_")]
    pre = broad.prefilter(df, base, cols, TARGETS, top_n=18)
    y = train_raw[TARGETS].to_numpy(dtype=int)
    rows = []
    for cand in pre.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        j = TARGETS.index(target)
        base_loss = loss_col(y[:, j], base[:, j])
        for c_value in [0.05, 0.10, 0.20]:
            corrected = broad.oof_corrected(df, base, target, feature, mode, c_value)
            losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corrected) for w in broad.GRID]
            best_i = int(np.argmin(losses))
            row = {
                "target": target,
                "feature": feature,
                "mode": mode,
                "corr": float(cand.corr),
                "c_value": float(c_value),
                "base_loss": base_loss,
                "corrected_loss": loss_col(y[:, j], corrected),
                "best_weight": float(broad.GRID[best_i]),
                "best_loss": float(losses[best_i]),
                "delta_vs_base": float(losses[best_i] - base_loss),
            }
            if row["best_weight"] > 0 and row["delta_vs_base"] < 0:
                row.update(broad.repeated_subject_guardrail(df, y, base, corrected, j))
            else:
                row.update(
                    {
                        "mean_delta": 0.0,
                        "median_delta": 0.0,
                        "p25_delta": 0.0,
                        "p75_delta": 0.0,
                        "win_rate": 0.0,
                        "mean_selected_weight": 0.0,
                        "zero_weight_rate": 1.0,
                    }
                )
            rows.append(row)

    scan = pd.DataFrame(rows).sort_values(["delta_vs_base", "mean_delta"], ascending=[True, True])
    geom_rows = []
    for op in scan[(scan["best_weight"] > 0) & (scan["delta_vs_base"] < -0.0003)].head(16).to_dict(orient="records"):
        enriched = dict(op)
        enriched.update(geometry_summary(train_raw, sub_raw, df, base, op))
        geom_rows.append(enriched)
    geom_df = pd.DataFrame(geom_rows)
    if not geom_df.empty:
        geom_df["passes_e208_probe"] = (
            (geom_df["delta_vs_base"] <= -0.00045)
            & (geom_df["mean_delta"] <= -0.00010)
            & (geom_df["win_rate"] >= 0.62)
            & (geom_df["geometry_delta_mean"] <= 0.0)
        )

    target_rows = []
    for target, group in scan.groupby("target", sort=False):
        best = group.iloc[0]
        target_rows.append(
            {
                "target": target,
                "best_feature": best["feature"],
                "best_mode": best["mode"],
                "best_c_value": float(best["c_value"]),
                "best_weight": float(best["best_weight"]),
                "best_delta_vs_base": float(best["delta_vs_base"]),
                "best_mean_delta": float(best["mean_delta"]),
                "best_win_rate": float(best["win_rate"]),
            }
        )
    return scan, geom_df, pd.DataFrame(target_rows)


def write_report(
    train_rows: pd.DataFrame,
    context_meta: pd.DataFrame,
    train_diag: pd.DataFrame,
    geometry_diag: pd.DataFrame,
    downstream_summary: pd.DataFrame,
    downstream_geom: pd.DataFrame,
) -> None:
    def table(df: pd.DataFrame, cols: list[str], max_rows: int = 16) -> str:
        if df.empty:
            return "_empty_"
        lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
        for _, row in df.head(max_rows)[cols].iterrows():
            vals = []
            for col in cols:
                val = row[col]
                if isinstance(val, float):
                    vals.append(f"{val:.6g}")
                else:
                    vals.append(str(val))
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)

    pass_count = int(downstream_geom["passes_e208_probe"].sum()) if "passes_e208_probe" in downstream_geom else 0
    lines = [
        "# E208 Feature-Neighbor JEPA Probe",
        "",
        "Purpose: actually train a JEPA-style context-to-target representation using the only E207-certified positive-pair regime: feature nearest neighbors in the broad stage2 latent space.",
        "",
        "This probe does not materialize a submission. It tests whether the representation beats copy-self/random controls and whether its features survive downstream OOF, subject bootstrap, and geometry stress.",
        "",
        "## Data",
        "",
        f"- rows: `{len(train_rows)}` train+submission rows",
        f"- context families: `{len(context_meta)}`",
        "",
        "## Context Families",
        "",
        table(context_meta, ["family", "columns", "components", "explained_variance"], max_rows=20),
        "",
        "## JEPA Training Diagnostics",
        "",
        table(
            train_diag,
            [
                "seed",
                "train_mse",
                "val_mse",
                "copy_self_mse",
                "mean_target_mse",
                "random_pair_mse",
                "hidden_var_penalty",
                "pred_var_penalty",
                "hidden_cov_penalty",
                "epochs",
            ],
        ),
        "",
        "## Embedding Geometry",
        "",
        table(
            geometry_diag,
            ["embedding", "skew_abs", "excess_kurt_abs", "effective_rank", "rank_fraction", "cov_eig_cv", "cov_condition"],
        ),
        "",
        "## Downstream Target Summary",
        "",
        table(
            downstream_summary,
            ["target", "best_feature", "best_mode", "best_c_value", "best_weight", "best_delta_vs_base", "best_mean_delta", "best_win_rate"],
            max_rows=10,
        ),
        "",
        "## Geometry-Stressed Candidates",
        "",
        table(
            downstream_geom.sort_values(["passes_e208_probe", "geometry_delta_mean", "delta_vs_base"], ascending=[False, True, True])
            if not downstream_geom.empty
            else downstream_geom,
            [
                "target",
                "feature",
                "mode",
                "c_value",
                "best_weight",
                "delta_vs_base",
                "mean_delta",
                "win_rate",
                "geometry_delta_mean",
                "geometry_win_rate",
                "passes_e208_probe",
            ],
            max_rows=16,
        ),
        "",
        "## Decision",
        "",
        f"- materialization gate pass count: `{pass_count}`",
    ]
    if pass_count:
        lines.append("- E208 found at least one feature that can move to a separate materialization/stress step. Do not submit directly from this probe; build E209 with the passing operation and compare against E95/E154 public-sensor geometry first.")
    else:
        lines.append("- No E208 feature passed the full probe gate. Keep the learned feature-neighbor JEPA as diagnostic energy and revise the target representation before making a submission.")
    lines.append("")
    (OUT / "e208_feature_neighbor_jepa_probe_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    torch.set_num_threads(1)
    train_raw, sub_raw, train_feat, sub_feat = stage2.build_frames()
    rows = e207.make_rows(train_raw, sub_raw)
    broad_space = e207.load_pair_feature_space(train_feat, sub_feat)
    context, context_meta_rows = family_context_matrix(train_feat, sub_feat)
    context_meta = pd.DataFrame(context_meta_rows)

    pair_regime = e207.feature_nn_pairs(rows, broad_space.x, 1, "feature_nn1_all")
    seeds = [SEED + 11, SEED + 29, SEED + 47]
    results = [train_neighbor_jepa(context, broad_space.x, pair_regime.i, pair_regime.j, seed=s) for s in seeds]

    train_diag = pd.DataFrame(
        [
            {
                "seed": r.seed,
                "train_mse": r.train_mse,
                "val_mse": r.val_mse,
                "copy_self_mse": r.copy_self_mse,
                "mean_target_mse": r.mean_target_mse,
                "random_pair_mse": r.random_pair_mse,
                "hidden_var_penalty": r.hidden_var_penalty,
                "pred_var_penalty": r.pred_var_penalty,
                "hidden_cov_penalty": r.hidden_cov_penalty,
                "epochs": r.epochs,
                "val_vs_copy_self_ratio": r.val_mse / max(r.copy_self_mse, 1e-12),
                "val_vs_mean_target_ratio": r.val_mse / max(r.mean_target_mse, 1e-12),
            }
            for r in results
        ]
    )
    feature_df, geometry_diag = build_feature_frame(rows, broad_space.x, pair_regime.j, results)
    feature_df.iloc[: len(train_raw)].to_parquet(OUT / "e208_feature_neighbor_jepa_train_features.parquet", index=False)
    feature_df.iloc[len(train_raw) :].to_parquet(OUT / "e208_feature_neighbor_jepa_submission_features.parquet", index=False)

    scan, downstream_geom, downstream_summary = downstream_scan(train_raw, sub_raw, feature_df)
    train_diag.to_csv(OUT / "e208_feature_neighbor_jepa_training_summary.csv", index=False)
    context_meta.to_csv(OUT / "e208_feature_neighbor_jepa_context_summary.csv", index=False)
    geometry_diag.to_csv(OUT / "e208_feature_neighbor_jepa_geometry_summary.csv", index=False)
    scan.to_csv(OUT / "e208_feature_neighbor_jepa_downstream_scan_summary.csv", index=False)
    downstream_geom.to_csv(OUT / "e208_feature_neighbor_jepa_downstream_geometry_summary.csv", index=False)
    downstream_summary.to_csv(OUT / "e208_feature_neighbor_jepa_target_summary.csv", index=False)
    payload = {
        "pair_regime": pair_regime.name,
        "pair_count": int(len(pair_regime.i)),
        "train_rows": int(len(train_raw)),
        "submission_rows": int(len(sub_raw)),
        "context_dim": int(context.shape[1]),
        "target_dim": int(broad_space.x.shape[1]),
        "seeds": seeds,
        "materialization_gate_pass_count": int(downstream_geom["passes_e208_probe"].sum()) if "passes_e208_probe" in downstream_geom else 0,
    }
    (OUT / "e208_feature_neighbor_jepa_probe_meta.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_report(rows, context_meta, train_diag, geometry_diag, downstream_summary, downstream_geom)

    print(train_diag.round(6).to_string(index=False))
    print(downstream_summary.round(9).to_string(index=False))
    if not downstream_geom.empty:
        cols = ["target", "feature", "mode", "best_weight", "delta_vs_base", "mean_delta", "win_rate", "geometry_delta_mean", "passes_e208_probe"]
        print(downstream_geom.sort_values(["passes_e208_probe", "geometry_delta_mean"], ascending=[False, True])[cols].round(9).to_string(index=False))


if __name__ == "__main__":
    main()
