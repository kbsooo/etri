#!/usr/bin/env python3
"""E359: row-placement action-health probe after E358.

Question:
    E358 says the compact lifestyle-state action is output-space plausible but
    not row-state-certified.  Can the same compact action become healthier if
    it is redistributed away from E323-heavy lifestyle rows and toward
    E247-like rows?

JEPA/data2vec translation:
    context = E328 row-level own-latent lifestyle state and E268 story tails
    target  = action-health representation: E272 visibility plus E358
              row-state public-survival
    action  = row-gated versions of E351/E356/E357 compact movements

No public LB is optimized here.  Known public observations are used only through
fixed public-free sensors already established in E272/E358.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import (  # noqa: E402
    CURRENT,
    build_features,
    evaluate_models,
    load_sub as selector_load_sub,
    score_candidates,
)
from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402
from e358_rowstate_public_survival_audit import (  # noqa: E402
    feature_columns as e358_feature_columns,
    known_observations as e358_known_observations,
    load_anchor,
    load_row_state,
    make_models as e358_make_models,
    rowstate_features,
)
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


RNG_SEED = 20260531 + 359
EPS = 1.0e-6
KEY = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
UPLOAD_PREFIX = "submission_e359_rowplacement"

SOURCES = {
    "e357_fulls3_noamp": OUT / "submission_e357_publicsurvival_selected_compact_t45_s1_000_s3a1_00_a08a4957_uploadsafe.csv",
    "e356_halfs3_amp": OUT / "submission_e356_transferstable_selected_compact_t45_s1_005_s3a0_50_0ace76e5_uploadsafe.csv",
    "e351_robust_center": OUT / "submission_e351_robustplateau_selected_compact_t75_s1_005_s3a0_25_58e03127_uploadsafe.csv",
    "e349_compact_core": OUT / "submission_e349_lifestate_ablate_selected_cell_abs_top65_q1q2q3s1_93c55c92_uploadsafe.csv",
}

CANDIDATE_OUT = OUT / "e359_rowplacement_action_health_candidates.csv"
SCORE_OUT = OUT / "e359_rowplacement_action_health_scores.csv"
KNOWN_OUT = OUT / "e359_rowplacement_action_health_known.csv"
REPORT_OUT = OUT / "e359_rowplacement_action_health_report.md"
SELECTION_OUT = OUT / "e359_rowplacement_action_health_selection.csv"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def short_hash(frame: pd.DataFrame) -> str:
    payload = pd.util.hash_pandas_object(frame[KEY + TARGETS], index=False).to_numpy(dtype=np.uint64).tobytes()
    return hashlib.sha1(payload).hexdigest()[:8]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def normalize_submission(df: pd.DataFrame) -> pd.DataFrame:
    out = df[KEY + TARGETS].copy()
    for col in KEY:
        if col in {"sleep_date", "lifelog_date"}:
            out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
        else:
            out[col] = out[col].astype(str)
    return out.sort_values(KEY).reset_index(drop=True)


def load_source(path: Path, anchor: pd.DataFrame) -> pd.DataFrame:
    frame = normalize_submission(pd.read_csv(path))
    if not frame[KEY].equals(anchor[KEY]):
        frame = anchor[KEY].merge(frame, on=KEY, how="left", validate="one_to_one")
    if frame[TARGETS].isna().any().any():
        raise RuntimeError(f"source failed to align: {path}")
    return frame


def zscore(values: pd.Series | np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    sd = float(np.nanstd(arr))
    if not np.isfinite(sd) or sd < 1.0e-12:
        return np.zeros_like(arr)
    return (arr - float(np.nanmean(arr))) / sd


def row_state_scores(state: pd.DataFrame) -> pd.DataFrame:
    out = state[KEY + ["ownlife_k8"]].copy()
    bad = (
        pd.to_numeric(state["rowstate_e323_cluster_rate"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
        + pd.to_numeric(state["rowstate_e256_cluster_rate"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
        - pd.to_numeric(state["rowstate_e247_cluster_rate"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    )
    energy = pd.to_numeric(state["ownlife_energy"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    resid = pd.to_numeric(state["ownlife_student_resid_mean"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    dist = pd.to_numeric(state["ownlife_cluster_distance"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    out["risk_core"] = zscore(bad) + 0.20 * zscore(energy) + 0.20 * zscore(resid) + 0.10 * zscore(dist)
    out["good_core"] = -zscore(bad) + 0.50 * zscore(state["rowstate_e247_cluster_rate"])
    out["bad_cluster_rate"] = pd.to_numeric(state["rowstate_e323_cluster_rate"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    out["good_cluster_rate"] = pd.to_numeric(state["rowstate_e247_cluster_rate"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    return out


def gate_specs(scores: pd.DataFrame) -> list[dict[str, Any]]:
    risk = scores["risk_core"].to_numpy(dtype=np.float64)
    good = scores["good_core"].to_numpy(dtype=np.float64)
    bad_rate = scores["bad_cluster_rate"].to_numpy(dtype=np.float64)
    cluster = scores["ownlife_k8"].astype(int).to_numpy()
    specs: list[dict[str, Any]] = []

    for q in [0.70, 0.80, 0.90]:
        high = risk >= np.quantile(risk, q)
        for damp in [0.0, 0.25, 0.50]:
            gate = np.ones(len(scores), dtype=np.float64)
            gate[high] = damp
            specs.append({"gate_id": f"risk_top{int(q*100)}_damp{str(damp).replace('.', 'p')}", "gate": gate, "renorm_cap": 1.00})
            specs.append({"gate_id": f"risk_top{int(q*100)}_damp{str(damp).replace('.', 'p')}_renorm110", "gate": gate, "renorm_cap": 1.10})

    for q in [0.65, 0.75, 0.85]:
        gate = sigmoid(-2.25 * (risk - np.quantile(risk, q)))
        gate = 0.15 + 0.95 * gate
        specs.append({"gate_id": f"smooth_risk_q{int(q*100)}", "gate": gate, "renorm_cap": 1.05})
        specs.append({"gate_id": f"smooth_risk_q{int(q*100)}_renorm115", "gate": gate, "renorm_cap": 1.15})

    for low_q, high_q in [(0.20, 0.80), (0.30, 0.80), (0.30, 0.90)]:
        gate = np.ones(len(scores), dtype=np.float64)
        gate[good >= np.quantile(good, 1.0 - low_q)] = 1.15
        gate[risk >= np.quantile(risk, high_q)] = 0.35
        specs.append({"gate_id": f"goodboost{int(low_q*100)}_riskdamp{int(high_q*100)}", "gate": gate, "renorm_cap": 1.05})

    for clusters, damp in [([3], 0.0), ([3, 6], 0.25), ([3, 6, 5], 0.35)]:
        gate = np.ones(len(scores), dtype=np.float64)
        gate[np.isin(cluster, clusters)] = damp
        specs.append({"gate_id": f"cluster{'-'.join(map(str, clusters))}_damp{str(damp).replace('.', 'p')}", "gate": gate, "renorm_cap": 1.10})

    # The public-bad cluster rate is more interpretable than the PCA risk score.
    high_bad_rate = bad_rate >= np.quantile(bad_rate, 0.80)
    gate = np.ones(len(scores), dtype=np.float64)
    gate[high_bad_rate] = 0.20
    specs.append({"gate_id": "badcluster_rate_top20_damp0p2", "gate": gate, "renorm_cap": 1.10})
    return specs


def write_candidate(anchor: pd.DataFrame, anchor_logit: np.ndarray, gated_delta: np.ndarray, source_id: str, gate_id: str) -> tuple[Path, dict[str, Any]]:
    out = anchor[KEY].copy()
    out[TARGETS] = clip_prob(sigmoid(anchor_logit + gated_delta))
    variant = f"{source_id}__{gate_id}"
    path = OUT / f"{UPLOAD_PREFIX}_{safe_id(variant, 96)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    row_abs = np.abs(gated_delta).sum(axis=1)
    target_abs = np.abs(gated_delta).sum(axis=0)
    total = float(target_abs.sum())
    rec: dict[str, Any] = {
        "variant": variant,
        "source_id": source_id,
        "gate_id": gate_id,
        "file": rel(path),
        "basename": path.name,
        "changed_rows_vs_e247": int((row_abs > 1.0e-12).sum()),
        "changed_cells_vs_e247": int((np.abs(gated_delta) > 1.0e-12).sum()),
        "move_l1": float(np.abs(gated_delta).sum()),
        "move_l2": float(np.linalg.norm(gated_delta.reshape(-1))),
        "row_l1_p90": float(np.quantile(row_abs, 0.90)),
    }
    for i, target in enumerate(TARGETS):
        rec[f"abs_{target}"] = float(target_abs[i])
        rec[f"share_{target}"] = float(target_abs[i] / total) if total > 0 else 0.0
    return path, rec


def generate_candidates(anchor: pd.DataFrame, anchor_logit: np.ndarray, state_scores: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    specs = gate_specs(state_scores)
    for source_id, path in SOURCES.items():
        if not path.exists():
            continue
        src = load_source(path, anchor)
        base_delta = logit(src[TARGETS].to_numpy(dtype=np.float64)) - anchor_logit
        base_l1 = float(np.abs(base_delta).sum())
        for spec in specs:
            gate = np.asarray(spec["gate"], dtype=np.float64)
            gated = base_delta * gate[:, None]
            gated_l1 = float(np.abs(gated).sum())
            if gated_l1 <= 1.0e-12:
                continue
            renorm = min(float(spec["renorm_cap"]), base_l1 / gated_l1)
            gated = gated * renorm
            candidate_path, rec = write_candidate(anchor, anchor_logit, gated, source_id, str(spec["gate_id"]))
            digest = candidate_path.stem.rsplit("_", 1)[-1]
            if digest in seen:
                candidate_path.unlink(missing_ok=True)
                continue
            seen.add(digest)
            rec["renorm"] = float(renorm)
            rec["source_l1"] = base_l1
            rec["gated_l1_ratio"] = float(np.abs(gated).sum() / base_l1) if base_l1 > 0 else 0.0
            rows.append(rec)
    out = pd.DataFrame(rows).sort_values(["source_id", "gate_id"]).reset_index(drop=True)
    out.to_csv(CANDIDATE_OUT, index=False)
    return out


def selector_scores(candidates: pd.DataFrame, anchor: pd.DataFrame) -> pd.DataFrame:
    # E272/public_anchor expects datetime keys from its current anchor loader.
    # E358 normalizes keys to strings, so reuse the selector's own sample here.
    sample = selector_load_sub(CURRENT)[KEY]
    known, refs, ref_vecs = build_known_and_refs(sample)
    files = [CURRENT] + candidates["file"].astype(str).tolist()
    feat = build_features(files, sample, refs, ref_vecs)
    model_df = evaluate_models(known)
    scored = score_candidates(known, feat, model_df)
    return candidates.merge(scored, on="basename", how="left", suffixes=("", "_selector"))


def rowstate_public_scores(scored: pd.DataFrame, anchor: pd.DataFrame, anchor_logit: np.ndarray, state: pd.DataFrame, base_cols: list[str], story_cols: list[str]) -> pd.DataFrame:
    known = e358_known_observations(anchor, anchor_logit, state, base_cols, story_cols)
    known.to_csv(KNOWN_OUT, index=False)
    cols = e358_feature_columns(known)
    x_known = known[cols].replace([np.inf, -np.inf], 0.0).fillna(0.0)
    y = known["delta_vs_e247"].to_numpy(dtype=np.float64)
    rows = []
    for rec in scored.to_dict("records"):
        path = Path(str(rec["file"]))
        if not path.is_absolute():
            path = ROOT / path
        sub = load_source(path, anchor)
        delta = logit(sub[TARGETS].to_numpy(dtype=np.float64)) - anchor_logit
        feats = rowstate_features(delta, state, base_cols, story_cols)
        row = {**rec, **feats}
        rows.append(row)
    out = pd.DataFrame(rows)
    x_pool = out.reindex(columns=cols).replace([np.inf, -np.inf], 0.0).fillna(0.0)
    pred_cols = []
    for name, model in e358_make_models().items():
        model.fit(x_known, y)
        col = f"rowstate_pred_public_loss_{name}"
        out[col] = np.asarray(model.predict(x_pool), dtype=np.float64)
        pred_cols.append(col)
    out["rowstate_pred_public_loss_mean"] = out[pred_cols].mean(axis=1)
    out["rowstate_pred_public_loss_std"] = out[pred_cols].std(axis=1)
    out["rowstate_bad_exposure"] = out["wmean_rowstate_e323_cluster_rate"] + out["wmean_rowstate_e256_cluster_rate"]
    out["rowstate_good_exposure"] = out["wmean_rowstate_e247_cluster_rate"]
    out["rowstate_bad_minus_good_exposure"] = out["rowstate_bad_exposure"] - out["rowstate_good_exposure"]
    return out


def select(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    out["e359_rowgate_score"] = (
        1.30 * out["pred_delta_vs_current_p90"].rank(ascending=False, pct=True)
        + 1.00 * out["pred_beats_current_rate"].rank(ascending=True, pct=True)
        + 1.10 * out["rowstate_pred_public_loss_mean"].rank(ascending=False, pct=True)
        + 1.00 * out["rowstate_bad_minus_good_exposure"].rank(ascending=False, pct=True)
        + 0.40 * out["move_l1"].rank(ascending=True, pct=True)
        - 0.75 * out["incremental_bad_axis_vs_current"].abs().rank(ascending=True, pct=True)
    )
    out["e359_gate"] = (
        out["strict_promote_gate"].fillna(False).astype(bool)
        & (out["pred_delta_vs_current_p90"] < -0.00005)
        & (out["incremental_bad_axis_vs_current"].abs() <= 0.015)
        & (out["rowstate_bad_minus_good_exposure"] <= 0.1685)
        & (out["rowstate_pred_public_loss_mean"] <= 0.00060)
        & (out["rowstate_pred_public_loss_std"] <= 0.00045)
    )
    ranked = out.sort_values(["e359_gate", "e359_rowgate_score"], ascending=[False, False]).reset_index(drop=True)
    passed = ranked[ranked["e359_gate"]].head(1)
    if passed.empty:
        selected = ranked.head(1).copy()
        selected["decision"] = "no_rowplacement_submission"
        selected["selected_uploadsafe_file"] = "none"
        selected["reason"] = "Row gating improved the question but did not clear E272 visibility plus E358 row-state public-survival gates."
    else:
        selected = passed.copy()
        src = ROOT / str(selected.iloc[0]["file"])
        frame = pd.read_csv(src)
        upload = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(str(selected.iloc[0]['variant']), 72)}_{short_hash(frame)}_uploadsafe.csv"
        shutil.copyfile(src, upload)
        selected["decision"] = "select_rowplacement_probe"
        selected["selected_uploadsafe_file"] = rel(upload)
        selected["reason"] = "Row-gated compact action passed E272 visibility and E358 row-state public-survival gates."
    selected.to_csv(SELECTION_OUT, index=False)
    ranked.to_csv(SCORE_OUT, index=False)
    return selected


def write_report(scored: pd.DataFrame, selected: pd.DataFrame) -> None:
    top_cols = [
        "variant",
        "source_id",
        "gate_id",
        "promotion_decision",
        "e359_gate",
        "e359_rowgate_score",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "rowstate_pred_public_loss_mean",
        "rowstate_pred_public_loss_std",
        "rowstate_bad_minus_good_exposure",
        "rowstate_good_exposure",
        "move_l1",
        "gated_l1_ratio",
        "file",
    ]
    top_cols = [c for c in top_cols if c in scored.columns]
    summary = (
        scored.groupby("source_id", dropna=False)
        .agg(
            n=("basename", "count"),
            gate_count=("e359_gate", "sum"),
            best_p90=("pred_delta_vs_current_p90", "min"),
            best_rowstate_loss=("rowstate_pred_public_loss_mean", "min"),
            best_bad_minus_good=("rowstate_bad_minus_good_exposure", "min"),
            info_count=("info_sensor_gate", "sum"),
            strict_count=("strict_promote_gate", "sum"),
        )
        .reset_index()
        .sort_values(["gate_count", "best_p90"], ascending=[False, True])
    )
    lines = [
        "# E359 Row-Placement Action-Health Probe",
        "",
        "## Question",
        "",
        "Can E351/E356/E357 compact actions become row-state healthy if their movement is gated away from E323-heavy lifestyle rows and toward E247-like rows?",
        "",
        "## Method",
        "",
        "- Source actions: E349, E351, E356, E357.",
        "- Row context: E328 own-latent lifestyle state, k8 public-bad/public-good cluster rates, and E358 risk score.",
        "- Candidate generation: row gates that damp high-risk rows, smooth risk exposure, boost good rows, or suppress E323-heavy clusters.",
        "- Stress: E272 public-free selector plus E358 row-state public-survival sensor.",
        "",
        "## Decision",
        "",
        md_table(selected[["decision", "variant", "selected_uploadsafe_file", "e359_rowgate_score", "pred_delta_vs_current_p90", "rowstate_pred_public_loss_mean", "rowstate_bad_minus_good_exposure", "reason"]], n=5, floatfmt=".9f"),
        "",
        "## Source Summary",
        "",
        md_table(summary, n=20, floatfmt=".9f"),
        "",
        "## Top Candidates",
        "",
        md_table(scored[top_cols].head(40), n=40, floatfmt=".9f"),
        "",
        "## Gate-Passing Candidates",
        "",
        md_table(scored[scored["e359_gate"]][top_cols], n=40, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
        "- A pass would mean the compact action was not wrong, only misplaced across lifestyle rows.",
        "- No pass means the compact movement and row-state survival are still entangled: dampening risky rows removes too much visibility or remains row-state risky.",
        "- In that case the next target should be learned row-action health directly, not hand-shaped row gates over the same compact delta.",
        "",
        "## Files",
        "",
        f"- `{rel(CANDIDATE_OUT)}`",
        f"- `{rel(SCORE_OUT)}`",
        f"- `{rel(KNOWN_OUT)}`",
        f"- `{rel(SELECTION_OUT)}`",
        f"- `{rel(REPORT_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    anchor, anchor_logit = load_anchor()
    state, base_cols, story_cols = load_row_state(anchor)
    scores = row_state_scores(state)
    candidates = generate_candidates(anchor, anchor_logit, scores)
    selected_cols = selector_scores(candidates, anchor)
    scored = rowstate_public_scores(selected_cols, anchor, anchor_logit, state, base_cols, story_cols)
    selected = select(scored)
    scored = pd.read_csv(SCORE_OUT)
    write_report(scored, selected)
    print(f"candidates={len(candidates)}")
    print(selected[["decision", "variant", "selected_uploadsafe_file", "e359_rowgate_score", "pred_delta_vs_current_p90", "rowstate_pred_public_loss_mean", "rowstate_bad_minus_good_exposure"]].round(9).to_string(index=False))
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
