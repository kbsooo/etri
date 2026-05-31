#!/usr/bin/env python3
"""E322: E321-guided preselection and fresh null check.

E321 showed that row/subject/dateblock action health is locally learnable, but
it did not promote any already-governed E319 candidate.  E322 asks a sharper
public-free question:

If we use the E321 actual-geometry health target as a preselector over the
unevaluated E319 candidate universe, do any newly selected candidates survive a
fresh matched-null governor?

No public LB is used.  This script does not create a new probability tensor; it
only audits existing E319 candidates that were not previously null-evaluated.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e322_adversarial_preselector_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import TARGETS, clip_prob, load_frames, stable_seed  # noqa: E402
from e297_episode_state_materializer import align_meta_to_current, feature_rows, sigmoid  # noqa: E402
from e321_mode_adversarial_action_health import (  # noqa: E402
    PROMOTION_THRESHOLDS,
    candidate_meta_features,
    md,
    parse_mode_mix,
    safe_corr,
    score_feature_columns,
)
from public_anchor_bottleneck_decomposition import KEYS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

E319_CANDIDATES = OUT / "e319_mode_specialized_generator_candidates.csv"
E319_GOVERNOR = OUT / "e319_mode_specialized_generator_governor.csv"

ALL_AUDIT_OUT = OUT / "e322_adversarial_preselector_all_audit.csv"
OOF_AUDIT_OUT = OUT / "e322_adversarial_preselector_oof_audit.csv"
SELECTED_OUT = OUT / "e322_adversarial_preselector_selected_audit.csv"
GOVERNOR_OUT = OUT / "e322_adversarial_preselector_governor_audit.csv"
NULL_MAP_OUT = OUT / "e322_adversarial_preselector_null_map.csv"
SUMMARY_OUT = OUT / "e322_adversarial_preselector_summary.csv"
REPORT_OUT = OUT / "e322_adversarial_preselector_report.md"

MAX_NULL_EVAL = 56
N_NULL_REPS = 5
CAP = 0.35
PLACEMENT_MODES = ["row", "subject", "dateblock"]
ALL_NULL_MODES = ["row", "subject", "dateblock", "target_perm", "sign_flip", "q_s_swap"]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def current_frame() -> pd.DataFrame:
    return load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)


def cap_delta(delta: np.ndarray, cap: float = CAP) -> np.ndarray:
    return np.clip(np.asarray(delta, dtype=np.float64), -cap, cap)


def load_delta(path: Path, current: pd.DataFrame) -> np.ndarray:
    sub = load_sub(path).sort_values(KEYS).reset_index(drop=True)
    if not sub[KEYS].equals(current[KEYS]):
        raise ValueError(f"key mismatch: {path}")
    return logit(sub[TARGETS].to_numpy(dtype=np.float64)) - logit(current[TARGETS].to_numpy(dtype=np.float64))


def shuffle_rows(delta: np.ndarray, mode: str, meta: pd.DataFrame, seed_parts: tuple[Any, ...]) -> np.ndarray:
    rng = np.random.default_rng(stable_seed("e322shuffle", *map(str, seed_parts)))
    values = np.asarray(delta, dtype=np.float64)
    out = values.copy()
    if mode == "row":
        return values[rng.permutation(len(values))]
    if mode in {"subject", "dateblock"}:
        group_col = "subject_id" if mode == "subject" else "dateblock_group"
        for _, idx in meta.groupby(group_col).indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            if len(idx_arr) > 1:
                out[idx_arr] = values[idx_arr][rng.permutation(len(idx_arr))]
        return out
    raise ValueError(mode)


def null_delta(delta: np.ndarray, mode: str, rep: int, meta: pd.DataFrame, basename: str) -> np.ndarray:
    if mode in {"row", "subject", "dateblock"}:
        return shuffle_rows(delta, mode, meta, (basename, mode, rep))
    if mode == "sign_flip":
        return -delta
    if mode == "target_perm":
        rng = np.random.default_rng(stable_seed("e322targetperm", basename, rep))
        return delta[:, rng.permutation(len(TARGETS))]
    if mode == "q_s_swap":
        out = np.zeros_like(delta)
        out[:, :3] = delta[:, [3, 4, 5]]
        out[:, 3:6] = delta[:, :3]
        out[:, 6] = delta[:, 6]
        return out
    raise ValueError(mode)


def write_null(current: pd.DataFrame, delta: np.ndarray, basename: str, mode: str, rep: int, meta: pd.DataFrame) -> Path:
    out = current.copy()
    nd = cap_delta(null_delta(delta, mode, rep, meta, basename), CAP)
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + nd
    out[TARGETS] = clip_prob(sigmoid(logits))
    NULL_DIR.mkdir(exist_ok=True)
    safe_name = basename[:72].replace("/", "_")
    path = NULL_DIR / f"submission_e322null_{safe_name}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def load_candidate_meta() -> pd.DataFrame:
    candidates = pd.read_csv(E319_CANDIDATES).drop_duplicates("basename").reset_index(drop=True)
    governor = pd.read_csv(E319_GOVERNOR).drop_duplicates("basename")
    candidates["previously_null_evaluated"] = candidates["basename"].isin(governor["basename"])
    candidates = candidates[~candidates["oracle_control"].astype(bool)].copy()
    candidates["path_exists"] = candidates["basename"].map(lambda b: (OUT / str(b)).exists())
    return candidates[candidates["path_exists"]].reset_index(drop=True)


def build_all_scores(candidates: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    paths = [OUT / CURRENT, *[OUT / b for b in candidates["basename"]]]
    features = feature_rows(paths, sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    return scores.drop_duplicates("basename").reset_index(drop=True)


def feature_table(candidates: pd.DataFrame, scores: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    score_cols = score_feature_columns(scores)
    meta = candidate_meta_features(candidates).set_index("basename")
    rows: list[dict[str, Any]] = []
    score_by_base = scores.set_index("basename")
    for _, row in candidates.iterrows():
        basename = str(row["basename"])
        if basename not in score_by_base.index:
            continue
        item: dict[str, Any] = {"basename": basename}
        for col in score_cols:
            item[f"actual__{col}"] = float(score_by_base.loc[basename, col])
        if basename in meta.index:
            item.update(meta.loc[basename].to_dict())
        item["previously_null_evaluated"] = bool(row["previously_null_evaluated"])
        item["old_strict_promote"] = bool(score_by_base.loc[basename, "strict_promote_gate"])
        item["old_info_sensor"] = bool(score_by_base.loc[basename, "info_sensor_gate"])
        item["actual_p90"] = float(score_by_base.loc[basename, "pred_delta_vs_current_p90"])
        item["actual_mean"] = float(score_by_base.loc[basename, "pred_delta_vs_current_mean"])
        item["actual_beats_current_rate"] = float(score_by_base.loc[basename, "pred_beats_current_rate"])
        item["incremental_bad_axis_vs_current"] = float(score_by_base.loc[basename, "incremental_bad_axis_vs_current"])
        rows.append(item)
    table = pd.DataFrame(rows)
    num_cols = [
        c
        for c in table.columns
        if (c.startswith("actual__") or c.startswith("meta_") or c.startswith("mix_"))
        and pd.api.types.is_numeric_dtype(table[c])
    ]
    cat_cols = ["policy", "recipe", "base_variant", "group_key"]
    return table, num_cols, cat_cols


def ridge_model(num_cols: list[str], cat_cols: list[str]):
    transformers: list[tuple[str, Any, list[str]]] = []
    if num_cols:
        transformers.append(("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), num_cols))
    if cat_cols:
        transformers.append(
            (
                "cat",
                make_pipeline(
                    SimpleImputer(strategy="most_frequent"),
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                ),
                cat_cols,
            )
        )
    return make_pipeline(ColumnTransformer(transformers, remainder="drop"), Ridge(alpha=10.0))


def fit_health_preselector(feature_df: pd.DataFrame, num_cols: list[str], cat_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    governor = pd.read_csv(E319_GOVERNOR)
    governor = governor[~governor["oracle_control"].astype(bool)].copy()
    governor["target_worst_placement_dominance"] = governor[
        [f"{m}_p90_dominance" for m in PLACEMENT_MODES]
    ].min(axis=1)
    governor["target_adversarial_health"] = governor["target_worst_placement_dominance"] - governor["null_strict_rate"]
    target_cols = [
        "target_worst_placement_dominance",
        "null_strict_rate",
        "target_adversarial_health",
        "row_p90_dominance",
        "subject_p90_dominance",
        "dateblock_p90_dominance",
    ]
    train = feature_df.merge(
        governor[["basename", *target_cols]],
        on="basename",
        how="inner",
    ).reset_index(drop=True)
    if len(train) < 5:
        raise RuntimeError("not enough governed E319 rows to train E322")

    rows: list[dict[str, Any]] = []
    pred_all = feature_df[["basename"]].copy()
    for target in target_cols:
        y = train[target].astype(float).to_numpy()
        oof = np.full(len(train), float(np.mean(y)), dtype=float)
        folds = KFold(n_splits=max(2, min(5, len(train))), shuffle=True, random_state=322)
        for tr, va in folds.split(train):
            model = ridge_model(num_cols, cat_cols)
            model.fit(train.iloc[tr][num_cols + cat_cols], y[tr])
            oof[va] = model.predict(train.iloc[va][num_cols + cat_cols])
        model = ridge_model(num_cols, cat_cols)
        model.fit(train[num_cols + cat_cols], y)
        pred = model.predict(feature_df[num_cols + cat_cols])
        pred_all[f"pred_{target}"] = pred
        rows.append(
            {
                "target": target,
                "n_train": int(len(train)),
                "target_mean": float(np.mean(y)),
                "oof_spearman": safe_corr(y, oof),
                "oof_pearson": safe_corr(y, oof, "pearson"),
                "oof_rmse": float(np.sqrt(np.mean((y - oof) ** 2))),
                "pred_min": float(np.min(pred)),
                "pred_max": float(np.max(pred)),
            }
        )
    pred_all["pred_worst_placement_dominance"] = pred_all["pred_target_worst_placement_dominance"].clip(0.0, 1.0)
    pred_all["pred_null_strict_rate"] = pred_all["pred_null_strict_rate"].clip(0.0, 1.0)
    pred_all["pred_adversarial_health"] = pred_all["pred_target_adversarial_health"]
    pred_all["pred_ready_score"] = (
        0.75 * pred_all["pred_worst_placement_dominance"]
        - pred_all["pred_null_strict_rate"]
        + 0.25 * pred_all["pred_adversarial_health"]
    )
    out = feature_df.merge(pred_all, on="basename", how="left")
    return out, pd.DataFrame(rows)


def select_for_fresh_null(scored: pd.DataFrame) -> pd.DataFrame:
    pool = scored[~scored["previously_null_evaluated"].astype(bool)].copy()
    pool = pool[pool["old_strict_promote"].astype(bool) & pool["actual_p90"].le(-2.0e-5)].copy()
    if pool.empty:
        pool = scored[~scored["previously_null_evaluated"].astype(bool)].copy()
    ranked = pool.sort_values(
        ["pred_ready_score", "pred_worst_placement_dominance", "pred_null_strict_rate", "actual_p90"],
        ascending=[False, False, True, True],
    )
    frames = [
        ranked.head(22).assign(selection_reason="guided_global"),
        ranked.groupby("recipe", as_index=False).head(4).assign(selection_reason="guided_recipe"),
        ranked.groupby("policy", as_index=False).head(4).assign(selection_reason="guided_policy"),
        ranked.groupby("base_variant", as_index=False).head(3).assign(selection_reason="guided_variant"),
    ]
    selected = pd.concat(frames, ignore_index=True).drop_duplicates("basename")
    selected = selected.sort_values(
        ["pred_ready_score", "pred_worst_placement_dominance", "pred_null_strict_rate", "actual_p90"],
        ascending=[False, False, True, True],
    ).head(MAX_NULL_EVAL)
    return selected.reset_index(drop=True)


def run_governor(
    selected: pd.DataFrame,
    current: pd.DataFrame,
    meta: pd.DataFrame,
    model_df: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if selected.empty:
        return selected, pd.DataFrame(), pd.DataFrame()
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    if model_df is None:
        model_df = evaluate_models(known)

    null_rows: list[dict[str, Any]] = []
    null_paths: list[Path] = []
    for _, row in selected.iterrows():
        basename = str(row["basename"])
        delta = load_delta(OUT / basename, current)
        for mode in ALL_NULL_MODES:
            reps = N_NULL_REPS if mode in {"row", "subject", "dateblock", "target_perm"} else 1
            for rep in range(reps):
                path = write_null(current, delta, basename, mode, rep, meta)
                null_paths.append(path)
                null_rows.append(
                    {
                        "source_basename": basename,
                        "null_basename": path.name,
                        "null_path": rel(path),
                        "mode": mode,
                        "rep": rep,
                    }
                )
    null_map = pd.DataFrame(null_rows)
    paths = [OUT / b for b in selected["basename"]]
    features = feature_rows([OUT / CURRENT, *paths, *null_paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    null_scores = scores[scores["basename"].isin(null_map["null_basename"])].copy()
    cand_scores = scores[scores["basename"].isin(selected["basename"])].copy()

    rows: list[dict[str, Any]] = []
    for _, cand in selected.iterrows():
        basename = str(cand["basename"])
        actual = cand_scores[cand_scores["basename"].eq(basename)]
        if actual.empty:
            continue
        a = actual.iloc[0]
        these_null = null_scores.merge(
            null_map[null_map["source_basename"].eq(basename)][["null_basename", "mode"]],
            left_on="basename",
            right_on="null_basename",
            how="inner",
        )
        actual_p90 = float(a["pred_delta_vs_current_p90"])
        actual_mean = float(a["pred_delta_vs_current_mean"])
        old_strict = bool(a["strict_promote_gate"])
        p90_vals = these_null["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        mean_vals = these_null["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        null_strict_rate = float(these_null["strict_promote_gate"].astype(bool).mean()) if len(these_null) else 1.0
        p90_dominance = float(np.mean(actual_p90 < p90_vals)) if len(p90_vals) else 0.0
        mean_dominance = float(np.mean(actual_mean < mean_vals)) if len(mean_vals) else 0.0
        mode_doms: dict[str, float] = {}
        for mode, part in these_null.groupby("mode"):
            vals = part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            mode_doms[f"{mode}_p90_dominance"] = float(np.mean(actual_p90 < vals))
        worst_mode = float(min(mode_doms.values())) if mode_doms else 0.0
        ready = bool(
            old_strict
            and actual_p90 <= -2.0e-5
            and null_strict_rate <= PROMOTION_THRESHOLDS["null_strict_rate"]
            and p90_dominance >= PROMOTION_THRESHOLDS["p90_dominance"]
            and mean_dominance >= PROMOTION_THRESHOLDS["mean_dominance"]
            and worst_mode >= PROMOTION_THRESHOLDS["worst_mode_p90_dominance"]
        )
        rows.append(
            {
                **cand.to_dict(),
                "fresh_old_strict_promote": old_strict,
                "fresh_actual_mean": actual_mean,
                "fresh_actual_p10": float(a["pred_delta_vs_current_p10"]),
                "fresh_actual_p90": actual_p90,
                "fresh_actual_beats_current_rate": float(a["pred_beats_current_rate"]),
                "fresh_null_count": int(len(these_null)),
                "fresh_null_strict_rate": null_strict_rate,
                "fresh_p90_dominance": p90_dominance,
                "fresh_mean_dominance": mean_dominance,
                "fresh_worst_mode_p90_dominance": worst_mode,
                **{f"fresh_{k}": v for k, v in mode_doms.items()},
                "fresh_public_free_submission_ready": ready,
                "fresh_final_decision": "public_free_submission_ready" if ready else "blocked_by_e322_nulls",
            }
        )
    governor = pd.DataFrame(rows)
    if not governor.empty:
        governor = governor.sort_values(
            [
                "fresh_public_free_submission_ready",
                "fresh_old_strict_promote",
                "fresh_null_strict_rate",
                "fresh_actual_p90",
                "fresh_mean_dominance",
            ],
            ascending=[False, False, True, True, False],
        ).reset_index(drop=True)
    return selected, null_map, governor


def write_report(all_scored: pd.DataFrame, oof: pd.DataFrame, selected: pd.DataFrame, governor: pd.DataFrame) -> None:
    ready = governor[governor["fresh_public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    candidate_summary = pd.DataFrame(
        [
            {
                "slice": "all_non_oracle_e319",
                "rows": int(len(all_scored)),
                "old_strict": int(all_scored["old_strict_promote"].sum()),
                "previously_null_evaluated": int(all_scored["previously_null_evaluated"].sum()),
                "best_pred_ready": float(all_scored["pred_ready_score"].max()),
                "best_pred_health": float(all_scored["pred_adversarial_health"].max()),
            },
            {
                "slice": "selected_for_fresh_null",
                "rows": int(len(selected)),
                "old_strict": int(selected["old_strict_promote"].sum()) if not selected.empty else 0,
                "previously_null_evaluated": int(selected["previously_null_evaluated"].sum()) if not selected.empty else 0,
                "best_pred_ready": float(selected["pred_ready_score"].max()) if not selected.empty else np.nan,
                "best_pred_health": float(selected["pred_adversarial_health"].max()) if not selected.empty else np.nan,
            },
            {
                "slice": "fresh_governor",
                "rows": int(len(governor)),
                "old_strict": int(governor["fresh_old_strict_promote"].sum()) if not governor.empty else 0,
                "ready": int(governor["fresh_public_free_submission_ready"].sum()) if not governor.empty else 0,
                "best_fresh_p90": float(governor["fresh_actual_p90"].min()) if not governor.empty else np.nan,
                "best_null_strict": float(governor["fresh_null_strict_rate"].min()) if not governor.empty else np.nan,
                "best_worst_mode": float(governor["fresh_worst_mode_p90_dominance"].max()) if not governor.empty else np.nan,
            },
        ]
    )
    candidate_summary.to_csv(SUMMARY_OUT, index=False)
    top_cols = [
        "basename",
        "policy",
        "recipe",
        "base_variant",
        "selection_reason",
        "actual_p90",
        "pred_ready_score",
        "pred_worst_placement_dominance",
        "pred_null_strict_rate",
        "pred_adversarial_health",
    ]
    gov_cols = [
        "basename",
        "policy",
        "recipe",
        "base_variant",
        "selection_reason",
        "fresh_actual_p90",
        "fresh_null_strict_rate",
        "fresh_p90_dominance",
        "fresh_mean_dominance",
        "fresh_worst_mode_p90_dominance",
        "fresh_row_p90_dominance",
        "fresh_subject_p90_dominance",
        "fresh_dateblock_p90_dominance",
        "fresh_public_free_submission_ready",
        "fresh_final_decision",
    ]
    lines = [
        "# E322 Adversarial Preselector Null Check",
        "",
        "Public LB was not used. This audits unevaluated E319 candidates selected by the E321 actual-geometry health target.",
        "",
        "## Question",
        "",
        "Can E321-style adversarial health select better unevaluated E319 candidates before fresh null evaluation?",
        "",
        "## Preselector OOF",
        "",
        md(oof, n=20),
        "",
        "## Candidate Universe",
        "",
        md(candidate_summary, n=10),
        "",
        "## Selected For Fresh Null",
        "",
        md(selected[[c for c in top_cols if c in selected.columns]], n=30),
        "",
        "## Fresh Governor",
        "",
        md(governor[[c for c in gov_cols if c in governor.columns]] if not governor.empty else governor, n=40),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        lines.append(
            f"- `{ready.iloc[0]['basename']}` passed E322 public-free governance. Treat it as a scarce public hypothesis only after reviewing private risk."
        )
    else:
        lines.extend(
            [
                "- E321-guided preselection did not find a public-free E319 candidate.",
                "- This weakens the idea that a good candidate was merely skipped by E319's original null-eval budget.",
                "- The useful signal is still the action-health target itself; it needs to be used during generation, not only after E319 averaging.",
            ]
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{ALL_AUDIT_OUT.relative_to(ROOT)}`",
            f"- `{OOF_AUDIT_OUT.relative_to(ROOT)}`",
            f"- `{SELECTED_OUT.relative_to(ROOT)}`",
            f"- `{GOVERNOR_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{REPORT_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    current = current_frame()
    base, _, _, _ = load_frames()
    test_df = base.loc[base["split"].eq("test")].reset_index(drop=True)
    meta = align_meta_to_current(test_df, current)
    candidates = load_candidate_meta()
    scores = build_all_scores(candidates, current)
    feature_df, num_cols, cat_cols = feature_table(candidates, scores)
    scored, oof = fit_health_preselector(feature_df, num_cols, cat_cols)
    selected = select_for_fresh_null(scored)
    # Reuse one public-free selector model set for all fresh nulls.
    known, _, _ = build_known_and_refs(current[KEYS].copy())
    model_df = evaluate_models(known)
    selected, null_map, governor = run_governor(selected, current, meta, model_df=model_df)
    scored.to_csv(ALL_AUDIT_OUT, index=False)
    oof.to_csv(OOF_AUDIT_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    null_map.to_csv(NULL_MAP_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    write_report(scored, oof, selected, governor)
    return scored, selected, governor


def main() -> None:
    scored, selected, governor = run()
    ready_count = int(governor["fresh_public_free_submission_ready"].sum()) if not governor.empty else 0
    print(f"candidate_universe={len(scored)}")
    print(f"selected_for_null={len(selected)}")
    print(f"fresh_ready={ready_count}")
    if not governor.empty:
        print(f"best_fresh_p90={governor['fresh_actual_p90'].min():.9f}")
        print(f"best_null_strict={governor['fresh_null_strict_rate'].min():.6f}")
        print(f"best_worst_mode={governor['fresh_worst_mode_p90_dominance'].max():.6f}")
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
