#!/usr/bin/env python3
"""E347: lifestyle-state re-audit for counter-axis candidates.

E346 showed that some E344/E345 neighborhood candidates avoid known
public-loss axes better than the current upload copies.  This script asks the
missing JEPA-style question:

    Is that safer movement explained by a repeated hidden lifestyle state, or
    is it only a diluted output-space move?

The teacher representation is not a raw reconstruction target.  It is the
existing hidden lifestyle-state stack:
    - E328 own-latent PCs/energies/clusters;
    - E337 target-residual lifestyle states.

Each candidate movement is treated as an action view.  We score whether the
rows receiving the action are unusually aligned with the lifestyle-state
teacher relative to matched row shuffles.  Public LB is not used for tuning;
known public-bad axes are inherited only from the fixed E346 diagnostic.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402


RNG_SEED = 20260531 + 347
EPS = 1.0e-12
NULL_REPS = 96

E346_SCORE = OUT / "e346_counteraxis_public_analog_scores.csv"
E328_FEATURES = OUT / "e328_ownlatent_lifestyle_state_features.parquet"
E337_LATENTS = OUT / "e337_residual_lifestyle_cluster_latent_matrix.parquet"

SCORE_OUT = OUT / "e347_lifestyle_state_candidate_reaudit_scores.csv"
NULL_OUT = OUT / "e347_lifestyle_state_candidate_reaudit_nulls.csv"
REPORT_OUT = OUT / "e347_lifestyle_state_candidate_reaudit_report.md"
UPLOAD_PREFIX = "submission_e347_stateful_counteraxis_lifestyle"


def stable_seed(*parts: object) -> int:
    digest = hashlib.sha1("|".join(map(str, parts)).encode("utf-8")).hexdigest()
    return RNG_SEED + int(digest[:8], 16) % 100000


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def locate(path_or_name: object) -> Path | None:
    raw = Path(str(path_or_name))
    candidates: list[Path] = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.extend([ROOT / raw, OUT / raw.name, OUT / str(path_or_name)])
    for path in candidates:
        if path.exists():
            return path
    return None


def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["sleep_date", "lifelog_date"]:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    return out.sort_values(KEYS).reset_index(drop=True)


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def load_candidate(path: Path, sample: pd.DataFrame) -> pd.DataFrame:
    frame = normalize_dates(pd.read_csv(path))
    sample_norm = normalize_dates(sample.copy())
    if not frame[KEYS].equals(sample_norm[KEYS]):
        raise RuntimeError(f"candidate key mismatch: {path}")
    return frame


def numeric_cols(frame: pd.DataFrame, blocked: Iterable[str]) -> list[str]:
    block = set(blocked)
    return [c for c in frame.columns if c not in block and pd.api.types.is_numeric_dtype(frame[c])]


def robust_z(frame: pd.DataFrame, train_mask: np.ndarray) -> pd.DataFrame:
    work = frame.astype(float).replace([np.inf, -np.inf], np.nan)
    train = work.iloc[train_mask]
    med = train.median(axis=0)
    q75 = train.quantile(0.75, axis=0)
    q25 = train.quantile(0.25, axis=0)
    scale = ((q75 - q25) / 1.349).replace(0, np.nan).fillna(train.std(ddof=0)).replace(0, 1.0)
    out = ((work - med) / scale).replace([np.inf, -np.inf], 0.0).fillna(0.0).clip(-8.0, 8.0)
    return out


def load_lifestyle_teacher(sample: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str], list[str]]:
    own = normalize_dates(pd.read_parquet(E328_FEATURES))
    residual = normalize_dates(pd.read_parquet(E337_LATENTS))
    if not own[KEYS].equals(residual[KEYS]):
        raise RuntimeError("E328/E337 key mismatch")

    own_cols = [
        c
        for c in own.columns
        if c.startswith("ownlife_pc")
        or c in {
            "ownlife_energy",
            "ownlife_global_distance",
            "ownlife_student_resid_mean",
            "ownlife_student_resid_max",
            "ownlife_cluster_distance",
        }
        or c.startswith("ownlife_k8_")
    ]
    residual_cols = [c for c in residual.columns if c.startswith("rs")]
    calendar_cols = [c for c in ["subject_order", "weekday", "is_weekend"] if c in own.columns]

    merged = own[KEYS + ["split", *calendar_cols, *own_cols]].merge(
        residual[KEYS + residual_cols],
        on=KEYS,
        how="inner",
        validate="one_to_one",
    )
    if len(merged) != len(own):
        raise RuntimeError("latent merge lost rows")
    train_mask = merged["split"].eq("train").to_numpy()
    latent_cols = own_cols + residual_cols + calendar_cols
    z = robust_z(merged[latent_cols], train_mask)
    z = pd.concat([merged[KEYS + ["split"]].reset_index(drop=True), z.reset_index(drop=True)], axis=1)
    test = z[z["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    sample_norm = normalize_dates(sample.copy())
    if not test[KEYS].equals(sample_norm[KEYS]):
        raise RuntimeError("test latent/sample key mismatch")
    state_cols = own_cols + residual_cols
    return test, state_cols, residual_cols, calendar_cols


def max_spearman(score: np.ndarray, latent: pd.DataFrame, cols: list[str]) -> tuple[float, str, float]:
    if len(cols) == 0:
        return 0.0, "", 0.0
    s = pd.Series(np.asarray(score, dtype=np.float64))
    vals: list[tuple[float, str, float]] = []
    for col in cols:
        corr = s.corr(pd.Series(latent[col].to_numpy(dtype=np.float64)), method="spearman")
        if not np.isfinite(corr):
            corr = 0.0
        vals.append((abs(float(corr)), col, float(corr)))
    vals.sort(reverse=True, key=lambda x: x[0])
    return vals[0]


def top_enrichment(score: np.ndarray, latent: pd.DataFrame, cols: list[str]) -> tuple[float, str, float]:
    if len(cols) == 0:
        return 0.0, "", 0.0
    x = np.asarray(score, dtype=np.float64)
    if np.max(x) <= EPS:
        return 0.0, "", 0.0
    n = len(x)
    k = min(max(16, int(np.ceil(0.20 * n))), n - 1)
    active_idx = np.argsort(-x)[:k]
    active = np.zeros(n, dtype=bool)
    active[active_idx] = True
    vals: list[tuple[float, str, float]] = []
    for col in cols:
        arr = latent[col].to_numpy(dtype=np.float64)
        diff = float(np.mean(arr[active]) - np.mean(arr[~active]))
        vals.append((abs(diff), col, diff))
    vals.sort(reverse=True, key=lambda v: v[0])
    return vals[0]


def target_story(delta: np.ndarray, latent: pd.DataFrame, cols: list[str]) -> tuple[str, float, str, float]:
    rows: list[tuple[str, float, str, float]] = []
    for j, target in enumerate(TARGETS):
        score = np.abs(delta[:, j])
        if np.max(score) <= EPS:
            continue
        corr_abs, corr_col, corr_signed = max_spearman(score, latent, cols)
        rows.append((target, corr_abs, corr_col, corr_signed))
    if not rows:
        return "", 0.0, "", 0.0
    rows.sort(reverse=True, key=lambda x: x[1])
    return rows[0]


def movement_metrics(delta: np.ndarray, latent: pd.DataFrame, state_cols: list[str], residual_cols: list[str], calendar_cols: list[str], basename: str) -> tuple[dict[str, object], list[dict[str, object]]]:
    row_l2 = np.sqrt(np.mean(delta**2, axis=1))
    row_l1 = np.mean(np.abs(delta), axis=1)
    signed_sum = np.mean(delta, axis=1)

    state_corr_abs, state_corr_col, state_corr = max_spearman(row_l2, latent, state_cols)
    state_enrich_abs, state_enrich_col, state_enrich = top_enrichment(row_l2, latent, state_cols)
    resid_corr_abs, resid_corr_col, resid_corr = max_spearman(row_l2, latent, residual_cols)
    cal_corr_abs, cal_corr_col, cal_corr = max_spearman(row_l2, latent, calendar_cols)
    signed_corr_abs, signed_corr_col, signed_corr = max_spearman(signed_sum, latent, state_cols)
    tgt, tgt_corr_abs, tgt_col, tgt_corr = target_story(delta, latent, state_cols)

    null_rows: list[dict[str, object]] = []
    rng = np.random.default_rng(stable_seed("state-null", basename))
    null_state_corr: list[float] = []
    null_state_enrich: list[float] = []
    null_resid_corr: list[float] = []
    for rep in range(NULL_REPS):
        idx = rng.permutation(len(row_l2))
        shuffled_l2 = row_l2[idx]
        sc, _, _ = max_spearman(shuffled_l2, latent, state_cols)
        se, _, _ = top_enrichment(shuffled_l2, latent, state_cols)
        rc, _, _ = max_spearman(shuffled_l2, latent, residual_cols)
        null_state_corr.append(sc)
        null_state_enrich.append(se)
        null_resid_corr.append(rc)
        null_rows.append(
            {
                "basename": basename,
                "rep": rep,
                "null_state_corr_abs": sc,
                "null_state_enrich_abs": se,
                "null_residual_corr_abs": rc,
            }
        )

    metrics = {
        "state_corr_abs": state_corr_abs,
        "state_corr_col": state_corr_col,
        "state_corr_signed": state_corr,
        "state_enrich_abs": state_enrich_abs,
        "state_enrich_col": state_enrich_col,
        "state_enrich_signed": state_enrich,
        "residual_corr_abs": resid_corr_abs,
        "residual_corr_col": resid_corr_col,
        "residual_corr_signed": resid_corr,
        "calendar_corr_abs": cal_corr_abs,
        "calendar_corr_col": cal_corr_col,
        "calendar_corr_signed": cal_corr,
        "signed_state_corr_abs": signed_corr_abs,
        "signed_state_corr_col": signed_corr_col,
        "signed_state_corr_signed": signed_corr,
        "top_target_state": tgt,
        "top_target_state_corr_abs": tgt_corr_abs,
        "top_target_state_col": tgt_col,
        "top_target_state_corr_signed": tgt_corr,
        "state_corr_dominance": float(np.mean(state_corr_abs > np.asarray(null_state_corr, dtype=np.float64))),
        "state_enrich_dominance": float(np.mean(state_enrich_abs > np.asarray(null_state_enrich, dtype=np.float64))),
        "residual_corr_dominance": float(np.mean(resid_corr_abs > np.asarray(null_resid_corr, dtype=np.float64))),
        "row_l2_q80": float(np.quantile(row_l2, 0.80)),
        "row_l2_max": float(np.max(row_l2)),
        "row_l2_entropy": movement_entropy(row_l2),
        "row_l1_mean": float(np.mean(row_l1)),
    }
    metrics["lifestyle_state_score"] = float(
        0.35 * metrics["state_corr_dominance"]
        + 0.25 * metrics["state_enrich_dominance"]
        + 0.20 * metrics["residual_corr_dominance"]
        + 0.10 * min(metrics["state_corr_abs"] / 0.20, 1.0)
        + 0.10 * min(metrics["state_enrich_abs"] / 0.75, 1.0)
    )
    return metrics, null_rows


def movement_entropy(weight: np.ndarray) -> float:
    x = np.asarray(weight, dtype=np.float64)
    total = float(np.sum(x))
    if total <= EPS or len(x) <= 1:
        return 0.0
    p = x / total
    nz = p[p > 0.0]
    return float(-(nz * np.log(nz)).sum() / np.log(len(x)))


def choose_candidate(scored: pd.DataFrame) -> pd.DataFrame:
    work = scored.copy()
    for col in [
        "local_p90",
        "local_bad_axis",
        "public_analog_risk_score",
        "public_analog_survival_score",
        "poscos_e323",
        "poscos_e216",
        "poscos_e267",
        "poscos_e256",
    ]:
        if col not in work:
            work[col] = np.nan
    direct_bad = work[["poscos_e323", "poscos_e216", "poscos_e267", "poscos_e256"]].fillna(0.0).sum(axis=1)
    work["direct_bad_poscos_sum"] = direct_bad
    work["e347_gate"] = (
        (work["local_p90"].fillna(1.0) <= -0.000049)
        & (work["local_bad_axis"].fillna(9.0) <= 0.01475)
        & (work["public_analog_risk_score"].fillna(9.0) <= 0.0450)
        & (work["public_analog_survival_score"].fillna(0.0) >= 0.48)
        & (work["direct_bad_poscos_sum"] <= 1.0e-12)
        & (work["state_corr_dominance"] >= 0.85)
        & (work["state_enrich_dominance"] >= 0.85)
        & (work["residual_corr_dominance"] >= 0.70)
    )
    work["e347_rank_score"] = (
        3.0 * work["lifestyle_state_score"].fillna(0.0)
        + 2.0 * work["public_analog_survival_score"].fillna(0.0)
        - 10.0 * work["public_analog_risk_score"].fillna(1.0)
        - 1000.0 * work["local_p90"].fillna(0.0)
        - 25.0 * work["local_bad_axis"].fillna(0.0)
        - 100.0 * work["direct_bad_poscos_sum"]
    )
    return work.sort_values(["e347_gate", "e347_rank_score"], ascending=[False, False]).reset_index(drop=True)


def impute_upload_local_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """Fill upload-safe rows from identical generated-candidate fingerprints."""

    out = frame.copy()
    if "local_p90" not in out:
        return out
    available = out[out["local_p90"].notna()].copy()
    if available.empty:
        return out
    fp_cols = [
        "move_l1",
        "changed_rows",
        "changed_cells",
        "share_Q1",
        "share_Q2",
        "share_Q3",
        "share_S1",
        "share_S2",
        "share_S3",
        "share_S4",
    ]
    metric_cols = [
        "local_mean",
        "local_p90",
        "local_bad_axis",
        "bad_axis_margin",
        "p90_margin",
        "variant",
        "counter_weight",
        "veto_strength",
    ]
    if any(col not in out.columns for col in fp_cols):
        return out
    out["local_metric_imputed_from"] = out.get("local_metric_imputed_from", "")
    for idx in out.index[out["local_p90"].isna()]:
        row = out.loc[idx]
        dist = np.zeros(len(available), dtype=np.float64)
        for col in fp_cols:
            values = out[col].to_numpy(dtype=np.float64)
            scale = max(float(np.nanstd(values)), 1.0e-9)
            dist += np.abs(available[col].to_numpy(dtype=np.float64) - float(row[col])) / scale
        best_pos = int(np.argmin(dist))
        if float(dist[best_pos]) <= 1.0e-6:
            src = available.iloc[best_pos]
            for col in metric_cols:
                if col in out.columns and col in src.index:
                    out.at[idx, col] = src[col]
            out.at[idx, "local_metric_imputed_from"] = src.get("basename", "")
    return out


def materialize_upload(selected: pd.Series) -> Path | None:
    if not bool(selected.get("e347_gate", False)):
        return None
    src = locate(selected["file"])
    if src is None:
        return None
    frame = pd.read_csv(src)
    for target in TARGETS:
        if target not in frame.columns:
            raise RuntimeError(f"missing target {target}: {src}")
        frame[target] = clip_prob(frame[target].to_numpy(dtype=np.float64))
    tag = safe_id(str(selected["role"]), 48)
    out = OUT / f"{UPLOAD_PREFIX}_{tag}_{short_hash(frame)}_uploadsafe.csv"
    if src.resolve() == out.resolve():
        return out
    shutil.copyfile(src, out)
    return out


def write_report(scored: pd.DataFrame, nulls: pd.DataFrame, selected_path: Path | None) -> None:
    upload_rows = scored[scored["role"].isin(["E344_upload", "E345_upload"])].copy()
    top_cols = [
        "role",
        "basename",
        "e347_gate",
        "e347_rank_score",
        "lifestyle_state_score",
        "state_corr_abs",
        "state_corr_col",
        "state_corr_dominance",
        "state_enrich_abs",
        "state_enrich_col",
        "state_enrich_dominance",
        "residual_corr_abs",
        "residual_corr_col",
        "residual_corr_dominance",
        "top_target_state",
        "top_target_state_col",
        "public_analog_survival_score",
        "public_analog_risk_score",
        "local_p90",
        "local_bad_axis",
    ]
    top_cols = [c for c in top_cols if c in scored.columns]
    gate_count = int(scored["e347_gate"].sum()) if "e347_gate" in scored else 0
    best = scored.iloc[0].to_dict() if len(scored) else {}
    selected_text = rel(selected_path) if selected_path is not None else "none"
    lines = [
        "# E347 Lifestyle-State Candidate Re-Audit",
        "",
        "## Question",
        "",
        "Do the public-analog safer E344/E345 neighborhood candidates still look like hidden lifestyle-state actions, or are they merely diluted output-space moves?",
        "",
        "## Method",
        "",
        "- Candidate universe: E346 E344/E345 upload and null-safe neighborhood candidates.",
        "- Teacher state: E328 own-latent lifestyle PCs/energy/clusters plus E337 target-residual lifestyle states.",
        "- Action view: candidate logit movement relative to E247.",
        "- Stress: row-movement correlation/enrichment against lifestyle-state features, compared with row-shuffle nulls.",
        "- Public LB is not used; E346 public-analog metrics are fixed diagnostics only.",
        "",
        "## Top Candidates",
        "",
        md_table(scored[top_cols], n=16, floatfmt=".9f"),
        "",
        "## Upload Rows",
        "",
        md_table(upload_rows[top_cols], n=8, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
        f"- E347 gate pass count: `{gate_count}`.",
        f"- Best role: `{best.get('role', '')}`.",
        f"- Best lifestyle-state score: `{float(best.get('lifestyle_state_score', np.nan)):.9f}`.",
        f"- Best state correlation: `{float(best.get('state_corr_abs', np.nan)):.9f}` via `{best.get('state_corr_col', '')}`.",
        f"- Best state enrichment: `{float(best.get('state_enrich_abs', np.nan)):.9f}` via `{best.get('state_enrich_col', '')}`.",
        f"- Selected upload-safe file: `{selected_text}`.",
        "",
    ]
    if gate_count:
        lines.extend(
            [
                "E347 promotes a candidate only if it remains locally visible, has lower public-analog risk than E344 upload, keeps direct E323/E216/E267/E256 positive alignment at zero, and is non-randomly aligned to the hidden lifestyle-state teacher.",
                "",
                "This is a stricter claim than E346: the candidate is not only output-space safer, it also preserves a repeated lifestyle-state explanation.",
            ]
        )
    else:
        lines.extend(
            [
                "No candidate clears the combined statefulness and safety gate.",
                "",
                "That would mean the public-analog safer variants should not replace E344/E345 yet: their safer output anatomy is not sufficiently explained by the hidden lifestyle-state teacher.",
            ]
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(SCORE_OUT)}`",
            f"- `{rel(NULL_OUT)}`",
            f"- `{rel(REPORT_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    e346 = pd.read_csv(E346_SCORE)
    e346 = impute_upload_local_metrics(e346)
    e346 = e346[e346["file"].notna()].copy()
    e346["path"] = e346["file"].map(locate)
    e346 = e346[e346["path"].notna()].copy()

    base = load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)
    base_logit = logit(base[TARGETS].to_numpy(dtype=np.float64))
    latent, state_cols, residual_cols, calendar_cols = load_lifestyle_teacher(base[KEYS])

    rows: list[dict[str, object]] = []
    null_rows: list[dict[str, object]] = []
    for _, row in e346.iterrows():
        path = Path(row["path"])
        cand = load_candidate(path, base[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        metrics, candidate_nulls = movement_metrics(delta, latent, state_cols, residual_cols, calendar_cols, str(row["basename"]))
        out = row.drop(labels=["path"]).to_dict()
        out.update(metrics)
        rows.append(out)
        null_rows.extend(candidate_nulls)

    scored = choose_candidate(pd.DataFrame(rows))
    selected_path = materialize_upload(scored.iloc[0]) if len(scored) else None
    scored["selected_uploadsafe_file"] = ""
    if selected_path is not None and len(scored):
        scored.loc[0, "selected_uploadsafe_file"] = rel(selected_path)
    scored.to_csv(SCORE_OUT, index=False)
    nulls = pd.DataFrame(null_rows)
    nulls.to_csv(NULL_OUT, index=False)
    write_report(scored, nulls, selected_path)

    print(f"wrote {rel(SCORE_OUT)} {scored.shape}")
    print(f"wrote {rel(NULL_OUT)} {nulls.shape}")
    print(f"wrote {rel(REPORT_OUT)}")
    if selected_path is not None:
        print(f"selected {rel(selected_path)}")
    else:
        print("selected none")


if __name__ == "__main__":
    main()
