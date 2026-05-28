from __future__ import annotations

import hashlib
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from final_jepa_candidate_priority import candidate_family, load_metric_rows  # noqa: E402
from hidden_block_latent_audit import KEY, TARGETS, clip, logit  # noqa: E402
from jepa_energy_ensemble_optimizer import public_axes  # noqa: E402
from raw05_anchor_jepa_micro_injection import RAW05_FILE, read_submission  # noqa: E402


OUT_CSV = OUT / "lejepa_sigreg_candidate_audit.csv"
OUT_REPORT = OUT / "lejepa_sigreg_candidate_audit_report.md"

BLOCKS = {
    "all": TARGETS,
    "context_q1q2s123": ["Q1", "Q2", "S1", "S2", "S3"],
    "target_q3s4": ["Q3", "S4"],
    "q_block": ["Q1", "Q2", "Q3"],
    "s_block": ["S1", "S2", "S3", "S4"],
}


def stable_rng(file_name: str, *parts: str) -> np.random.Generator:
    key = "|".join((file_name, *parts)).encode("utf-8")
    seed = int.from_bytes(hashlib.blake2b(key, digest_size=8).digest(), "little")
    return np.random.default_rng(seed)


def locate_candidate(file_name: str) -> bool:
    for base in (OUT, ROOT / "jepa", ROOT):
        if (base / file_name).exists():
            return True
    return Path(file_name).exists()


def candidate_files() -> list[str]:
    priority = pd.read_csv(OUT / "final_jepa_candidate_priority_20260527.csv")
    metric_rows = load_metric_rows()
    rows: list[str] = priority["file"].astype(str).tolist()
    local_path = OUT / "local_lb_proxy_validation_candidate_predictions.csv"
    if local_path.exists():
        local = pd.read_csv(local_path)
        if "file" in local.columns:
            local = local.copy()
            sort_col = (
                "available_raw05_relative_lb_proxy_mean"
                if "available_raw05_relative_lb_proxy_mean" in local.columns
                else "raw05_relative_lb_proxy_mean"
            )
            rows.extend(local.sort_values(sort_col)["file"].astype(str).head(120).tolist())
            public6_like = local[local["file"].astype(str).str.contains("public6", na=False)].copy()
            if not public6_like.empty:
                rows.extend(public6_like.sort_values(sort_col)["file"].astype(str).head(120).tolist())
    if not metric_rows.empty:
        metric_rows = metric_rows.copy()
        if "bad_residual_axis_ratio" in metric_rows.columns:
            metric_rows["abs_bad_residual_axis_ratio"] = pd.to_numeric(
                metric_rows["bad_residual_axis_ratio"], errors="coerce"
            ).abs()
        else:
            metric_rows["abs_bad_residual_axis_ratio"] = np.nan
        if "ranker_selection_score" in metric_rows.columns:
            rows.extend(
                metric_rows.sort_values(["ranker_selection_score", "actual_anchor_score_final"])["file"]
                .astype(str)
                .head(140)
                .tolist()
            )
        if "q3s4_corr_score" in metric_rows.columns:
            rows.extend(
                metric_rows.sort_values(["q3s4_corr_score", "actual_anchor_score_final"])["file"]
                .astype(str)
                .head(140)
                .tolist()
            )
        rows.extend(
            metric_rows.sort_values(["actual_anchor_score_final", "abs_bad_residual_axis_ratio"])["file"]
            .astype(str)
            .head(140)
            .tolist()
        )
        rows.extend(
            metric_rows.sort_values(["abs_bad_residual_axis_ratio", "actual_anchor_score_final"])["file"]
            .astype(str)
            .head(100)
            .tolist()
        )
        rows.extend(
            metric_rows.sort_values(["posterior_expected_public_vs_anchor", "actual_anchor_score_final"])["file"]
            .astype(str)
            .head(100)
            .tolist()
        )
        if "metric_source" in metric_rows.columns:
            block_count = metric_rows[
                metric_rows["metric_source"].astype(str).str.contains("block_count_shift", na=False)
            ].copy()
            if not block_count.empty:
                rows.extend(
                    block_count.sort_values(["ranker_selection_score", "actual_anchor_score_final"])["file"]
                    .astype(str)
                    .head(100)
                    .tolist()
                )
            block_count_reg = metric_rows[
                metric_rows["metric_source"].astype(str).str.contains("blockcount_regularized", na=False)
            ].copy()
            if not block_count_reg.empty:
                rows.extend(
                    block_count_reg.sort_values(["selection_score", "actual_anchor_score_final"])["file"]
                    .astype(str)
                    .head(100)
                    .tolist()
                )
            tangent_null = metric_rows[
                metric_rows["metric_source"].astype(str).str.contains("tangent_nullspace", na=False)
            ].copy()
            if not tangent_null.empty:
                rows.extend(
                    tangent_null.sort_values(["selection_score", "actual_anchor_score_final"])["file"]
                    .astype(str)
                    .head(120)
                    .tolist()
                )
            axis_bridge = metric_rows[
                metric_rows["metric_source"].astype(str).str.contains("axisbudget_motif_bridge", na=False)
            ].copy()
            if not axis_bridge.empty:
                rows.extend(
                    axis_bridge.sort_values(["selection_score", "actual_anchor_score_final"])["file"]
                    .astype(str)
                    .head(140)
                    .tolist()
                )
            axis_repair = metric_rows[
                metric_rows["metric_source"].astype(str).str.contains("axisbridge_posterior_repair", na=False)
            ].copy()
            if not axis_repair.empty:
                rows.extend(
                    axis_repair.sort_values(["selection_score", "actual_anchor_score_final"])["file"]
                    .astype(str)
                    .head(160)
                    .tolist()
                )
            axis_trade = metric_rows[
                metric_rows["metric_source"].astype(str).str.contains("axisrepair_tradeoff_direct", na=False)
            ].copy()
            if not axis_trade.empty:
                rows.extend(
                    axis_trade.sort_values(["selection_score", "actual_anchor_score_final"])["file"]
                    .astype(str)
                    .head(180)
                    .tolist()
                )
            struct_refine = metric_rows[
                metric_rows["metric_source"].astype(str).str.contains("structural_constrained_refine", na=False)
            ].copy()
            if not struct_refine.empty:
                rows.extend(
                    struct_refine.sort_values(["selection_score", "actual_anchor_score_final"])["file"]
                    .astype(str)
                    .head(160)
                    .tolist()
                )
            direct_constrained = metric_rows[
                metric_rows["metric_source"].astype(str).str.contains("direct_constrained_search", na=False)
            ].copy()
            if not direct_constrained.empty:
                rows.extend(
                    direct_constrained.sort_values(["direct_score", "actual_anchor_score_final"])["file"]
                    .astype(str)
                    .head(180)
                    .tolist()
                )
            lowbad_motif = metric_rows[
                metric_rows["metric_source"].astype(str).str.contains("lowbad_motif_search", na=False)
            ].copy()
            if not lowbad_motif.empty:
                rows.extend(
                    lowbad_motif.sort_values(["lowbad_score", "actual_anchor_score_final"])["file"]
                    .astype(str)
                    .head(180)
                    .tolist()
                )
            anchorrobust_graft = metric_rows[
                metric_rows["metric_source"].astype(str).str.contains("anchorrobust_motif_graft", na=False)
            ].copy()
            if not anchorrobust_graft.empty:
                rows.extend(
                    anchorrobust_graft.sort_values(["selection_score", "actual_anchor_score_final"])["file"]
                    .astype(str)
                    .head(180)
                    .tolist()
                )
            axislocal = metric_rows[
                metric_rows["metric_source"].astype(str).str.contains("axislocal_posterior_sweep", na=False)
            ].copy()
            if not axislocal.empty:
                rows.extend(
                    axislocal.sort_values(["axislocal_score", "actual_anchor_score_final"])["file"]
                    .astype(str)
                    .head(180)
                    .tolist()
                )

    out: list[str] = []
    seen: set[str] = set()
    for file_name in rows:
        if file_name in seen:
            continue
        if not locate_candidate(file_name):
            continue
        seen.add(file_name)
        out.append(file_name)
    return out


def epps_pulley_sigreg(z: np.ndarray, rng: np.random.Generator, num_slices: int = 192) -> float:
    if z.shape[1] == 0:
        return np.nan
    a = rng.normal(size=(z.shape[1], num_slices))
    a /= np.maximum(np.linalg.norm(a, axis=0, keepdims=True), 1e-12)
    proj = z @ a
    t = np.linspace(-5.0, 5.0, 17)
    target_cf = np.exp(-0.5 * t**2)
    ecf = np.exp(1j * proj[:, :, None] * t.reshape(1, 1, -1)).mean(axis=0)
    err = np.abs(ecf - target_cf.reshape(1, -1)) ** 2 * target_cf.reshape(1, -1)
    return float(np.trapezoid(err, t, axis=1).mean() * z.shape[0])


def normalize_global(z: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    centered = z - z.mean(axis=0, keepdims=True)
    per_dim_std = centered.std(axis=0)
    scale = float(np.sqrt(np.mean(centered**2)))
    scale = max(scale, 1e-12)
    zg = centered / scale
    cov = np.cov(zg, rowvar=False)
    cov = np.atleast_2d(cov)
    eig = np.linalg.eigvalsh(cov)
    eig = np.clip(eig, 0.0, None)
    eig_mean = float(eig.mean()) if len(eig) else np.nan
    stats = {
        "global_scale": scale,
        "min_dim_std": float(per_dim_std.min()) if len(per_dim_std) else np.nan,
        "max_dim_std": float(per_dim_std.max()) if len(per_dim_std) else np.nan,
        "cov_eig_min": float(eig.min()) if len(eig) else np.nan,
        "cov_eig_max": float(eig.max()) if len(eig) else np.nan,
        "cov_eig_cv": float(eig.std() / max(eig_mean, 1e-12)) if len(eig) else np.nan,
        "cov_condition": float(eig.max() / max(eig.min(), 1e-12)) if len(eig) else np.nan,
    }
    return zg, stats


def normalize_diag(z: np.ndarray) -> np.ndarray:
    centered = z - z.mean(axis=0, keepdims=True)
    std = centered.std(axis=0, keepdims=True)
    std = np.where(std < 1e-12, 1.0, std)
    return centered / std


def block_residual(logit_pred: np.ndarray, logit_raw: np.ndarray, block_name: str) -> np.ndarray:
    cols = [TARGETS.index(target) for target in BLOCKS[block_name]]
    return logit_pred[:, cols] - logit_raw[:, cols]


def axis_residual(pred: np.ndarray, raw: np.ndarray, axes: dict[str, np.ndarray | float]) -> np.ndarray:
    delta = pred - raw
    bad = np.asarray(axes["bad_axis"], dtype=np.float64)
    ordinal = np.asarray(axes["ordinal_axis"], dtype=np.float64)
    stage2 = np.asarray(axes["stage2"], dtype=np.float64)
    raw05 = np.asarray(axes["raw05"], dtype=np.float64)
    stage2_axis = stage2 - raw05
    return np.column_stack(
        [
            (delta * bad).sum(axis=1),
            (delta * ordinal).sum(axis=1),
            (delta * stage2_axis).sum(axis=1),
            np.abs(delta).mean(axis=1),
        ]
    )


def score_candidate(
    file_name: str,
    raw_pred: np.ndarray,
    raw_logit: np.ndarray,
    axes: dict[str, np.ndarray | float],
) -> dict[str, float | str]:
    frame = read_submission(file_name)
    pred = clip(frame[TARGETS].to_numpy(dtype=np.float64))
    pred_logit = logit(pred)
    row: dict[str, float | str] = {"file": file_name, "family": candidate_family(file_name)}

    for block_name in BLOCKS:
        z = block_residual(pred_logit, raw_logit, block_name)
        zg, stats = normalize_global(z)
        zd = normalize_diag(z)
        row[f"{block_name}_sigreg_global"] = epps_pulley_sigreg(
            zg, stable_rng(file_name, block_name, "global")
        )
        row[f"{block_name}_sigreg_diag"] = epps_pulley_sigreg(
            zd, stable_rng(file_name, block_name, "diag")
        )
        for key, value in stats.items():
            row[f"{block_name}_{key}"] = value

    axis_z = axis_residual(pred, raw_pred, axes)
    zg, stats = normalize_global(axis_z)
    zd = normalize_diag(axis_z)
    row["public_axis_sigreg_global"] = epps_pulley_sigreg(
        zg, stable_rng(file_name, "public_axis", "global")
    )
    row["public_axis_sigreg_diag"] = epps_pulley_sigreg(
        zd, stable_rng(file_name, "public_axis", "diag")
    )
    for key, value in stats.items():
        row[f"public_axis_{key}"] = value

    row["lejepa_residual_health"] = (
        0.25 * float(row["all_sigreg_global"])
        + 0.20 * float(row["context_q1q2s123_sigreg_global"])
        + 0.20 * float(row["target_q3s4_sigreg_global"])
        + 0.20 * float(row["public_axis_sigreg_global"])
        + 0.15 * float(row["all_cov_eig_cv"])
    )
    return row


def write_report(scored: pd.DataFrame) -> None:
    cols = [
        "file",
        "family",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "lejepa_residual_health",
        "all_sigreg_global",
        "target_q3s4_sigreg_global",
        "public_axis_sigreg_global",
        "all_cov_eig_cv",
        "public_axis_cov_eig_cv",
    ]
    lines = [
        "# LeJEPA SIGReg Candidate Audit",
        "",
        "This audit applies the LeJEPA/SIGReg idea to row-level candidate residual embeddings.",
        "Lower scores mean the residual distribution is closer to an isotropic Gaussian under random projection tests.",
        "",
        "## Counts",
        "",
        f"- candidates scored: {len(scored)}",
        "",
        "## Best Residual Health",
        "",
        "```csv",
        scored.sort_values("lejepa_residual_health")[cols].head(40).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Best Actual-Anchor With Residual Health",
        "",
        "```csv",
        scored.sort_values(["actual_anchor_score_final", "lejepa_residual_health"])[cols].head(40).round(10).to_csv(
            index=False
        ).strip(),
        "```",
        "",
        "## Low Bad-Axis With Residual Health",
        "",
        "```csv",
        scored.sort_values(["bad_residual_axis_ratio", "lejepa_residual_health"])[cols].head(40).round(10).to_csv(
            index=False
        ).strip(),
        "```",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    raw_frame = read_submission(RAW05_FILE)
    if not raw_frame[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
        raise ValueError("raw05 key mismatch")
    raw_pred = clip(raw_frame[TARGETS].to_numpy(dtype=np.float64))
    raw_logit = logit(raw_pred)
    axes = public_axes()

    metric_rows = load_metric_rows()
    metrics = (
        metric_rows.sort_values("metric_source_order").drop_duplicates("file").set_index("file")
        if not metric_rows.empty
        else pd.DataFrame()
    )

    rows = []
    files = candidate_files()
    for i, file_name in enumerate(files, start=1):
        row = score_candidate(file_name, raw_pred, raw_logit, axes)
        if not metrics.empty and file_name in metrics.index:
            for col in [
                "actual_anchor_score_final",
                "posterior_expected_public_vs_anchor",
                "delta_vs_raw05_rawaxis",
                "bad_residual_axis_ratio",
                "mean_abs_move_vs_raw05",
                "bucket",
                "metric_source",
            ]:
                if col in metrics.columns:
                    row[col] = metrics.at[file_name, col]
        rows.append(row)
        if i % 50 == 0:
            print(f"scored {i}/{len(files)}")

    scored = pd.DataFrame(rows)
    scored["health_rank"] = scored["lejepa_residual_health"].rank(method="min")
    scored["actual_rank"] = scored["actual_anchor_score_final"].rank(method="min")
    scored["bad_rank"] = scored["bad_residual_axis_ratio"].rank(method="min")
    scored["lejepa_combined_rank"] = (
        0.45 * scored["actual_rank"].fillna(scored["actual_rank"].max())
        + 0.25 * scored["health_rank"]
        + 0.20 * scored["bad_rank"].fillna(scored["bad_rank"].max())
        + 0.10
        * scored["posterior_expected_public_vs_anchor"].rank(method="min").fillna(
            scored["posterior_expected_public_vs_anchor"].rank(method="min").max()
        )
    )
    scored = scored.sort_values(["lejepa_combined_rank", "actual_anchor_score_final"]).reset_index(drop=True)
    scored.to_csv(OUT_CSV, index=False)
    write_report(scored)

    cols = [
        "file",
        "family",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "bad_residual_axis_ratio",
        "lejepa_residual_health",
        "all_sigreg_global",
        "target_q3s4_sigreg_global",
        "public_axis_sigreg_global",
        "lejepa_combined_rank",
    ]
    print(f"scored={len(scored)} wrote={OUT_CSV}")
    print(scored[cols].head(35).round(10).to_string(index=False))


if __name__ == "__main__":
    main()
