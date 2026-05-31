#!/usr/bin/env python3
"""E365: jackknife stress for the E364 public-like cell-action choice.

Question:
    E364 selected a donor-graft candidate inside the E363 basin using only a
    tiny known-public sensor.  Is that candidate stable, or did it overfit one
    public-observed file or one feature view?

JEPA/data2vec translation:
    context views = output movement anatomy, known public-good/bad axes,
                    target-share structure, and compact movement statistics
    target view   = known public delta relative to E247
    health check  = a candidate must remain preferred when individual public
                    observations and feature views are masked

No new probability movement is generated here.  This is an anti-collapse audit
for the E364 latent gate.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402
from e357_public_survival_contrast_latent import KEY, TARGETS, feature_columns, locate, safe_spearman  # noqa: E402
from e359_rowplacement_action_health_probe import clip_prob  # noqa: E402


RNG_SEED = 20260531 + 365
UPLOAD_PREFIX = "submission_e365_jackknife"

KNOWN_IN = OUT / "e364_public_like_cellaction_known.csv"
POOL_IN = OUT / "e364_public_like_cellaction_scores.csv"
E364_SELECTION_IN = OUT / "e364_public_like_cellaction_selection.csv"
E363_SELECTION_IN = OUT / "e363_cell_action_robustness_selection.csv"

SCENARIO_OUT = OUT / "e365_public_like_jackknife_scenarios.csv"
SUPPORT_OUT = OUT / "e365_public_like_jackknife_candidate_support.csv"
SELECTION_OUT = OUT / "e365_public_like_jackknife_selection.csv"
REPORT_OUT = OUT / "e365_public_like_jackknife_report.md"


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    cols = [c for c in KEY + TARGETS if c in frame.columns]
    payload = pd.util.hash_pandas_object(frame[cols], index=False).to_numpy(dtype=np.uint64).tobytes()
    return hashlib.sha1(payload).hexdigest()[:8]


def make_model(name: str, train_n: int):
    if name == "ridge_10":
        return make_pipeline(StandardScaler(), Ridge(alpha=10.0))
    if name == "ridge_1":
        return make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    if name == "knn3":
        return make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=min(3, max(1, train_n - 1)), weights="distance"))
    if name == "extratrees":
        return ExtraTreesRegressor(
            n_estimators=128,
            min_samples_leaf=2,
            max_features=0.70,
            random_state=RNG_SEED,
            n_jobs=1,
        )
    raise ValueError(name)


def good_low(values: pd.Series | np.ndarray) -> pd.Series:
    v = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan)
    return (-v.fillna(v.median())).rank(pct=True)


def good_high(values: pd.Series | np.ndarray) -> pd.Series:
    v = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan)
    return v.fillna(v.median()).rank(pct=True)


def available_feature_sets(known: pd.DataFrame, pool: pd.DataFrame) -> dict[str, list[str]]:
    base = [c for c in feature_columns(known) if c in pool.columns]
    axis = [c for c in base if c.startswith(("cos_", "proj_", "posproj_", "absproj_")) or c.startswith("public_")]
    target_tokens = tuple([f"_{t}" for t in TARGETS] + [f"{t}_" for t in TARGETS])
    target = [c for c in base if c.startswith(("share_", "l1_", "signed_sum_", "mean_", "maxabs_", "pos_frac_", "neg_frac_")) or any(tok in c for tok in target_tokens)]
    anatomy = [
        c
        for c in base
        if c.startswith(("cell_", "row_", "changed_", "top5_", "top20_"))
        or c in {"target_entropy", "row_entropy", "cell_mean_abs", "cell_signed_mean"}
    ]
    bad_good = [c for c in base if "bad" in c or "good" in c or "e323" in c or "e216" in c or "e267" in c]
    compact = [
        c
        for c in [
            "cell_l1",
            "cell_l2",
            "cell_linf",
            "row_l1_mean",
            "row_l1_p90",
            "row_l1_max",
            "target_entropy",
            "row_entropy",
            "share_Q1",
            "share_Q2",
            "share_Q3",
            "share_S1",
            "share_S2",
            "share_S3",
            "share_S4",
            "public_bad_axis_sum",
            "public_good_axis_sum",
            "public_bad_good_gap",
            "public_bad_cos_max",
            "public_good_cos_max",
        ]
        if c in base
    ]
    out = {
        "all": base,
        "axis": axis,
        "target": target,
        "anatomy": anatomy,
        "bad_good": bad_good,
        "compact": compact,
    }
    return {k: v for k, v in out.items() if len(v) >= 3}


def predict_pool(train: pd.DataFrame, pool: pd.DataFrame, cols: list[str]) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    x = train[cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y = train["delta_vs_e247"].to_numpy(dtype=np.float64)
    xp = pool.reindex(columns=cols).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    pred_cols = []
    diagnostics: dict[str, float] = {}
    for model_name in ["ridge_10", "ridge_1", "knn3", "extratrees"]:
        model = make_model(model_name, len(train))
        model.fit(x, y)
        pred = np.asarray(model.predict(xp), dtype=np.float64)
        pred_cols.append(pred)
        fitted = np.asarray(model.predict(x), dtype=np.float64)
        diagnostics[f"train_spearman_{model_name}"] = safe_spearman(y, fitted)
    arr = np.vstack(pred_cols)
    return arr.mean(axis=0), arr.std(axis=0), diagnostics


def score_scenario(pool: pd.DataFrame, pred_mean: np.ndarray, pred_std: np.ndarray, base_variant: str) -> pd.DataFrame:
    scored = pool.copy()
    scored["scenario_pred_public_delta_mean"] = pred_mean
    scored["scenario_pred_public_delta_std"] = pred_std
    for col in [
        "public_bad_axis_sum",
        "public_bad_good_gap",
        "rowstate_pred_public_loss_mean",
        "rowstate_bad_minus_good_exposure",
        "e363_robust_score",
        "pred_delta_vs_current_p90",
    ]:
        if col not in scored.columns:
            scored[col] = 0.0
    scored["scenario_public_like_score"] = (
        1.15 * good_low(scored["scenario_pred_public_delta_mean"])
        + 0.75 * good_low(scored["scenario_pred_public_delta_std"])
        + 0.95 * good_low(scored["public_bad_axis_sum"])
        + 0.55 * good_low(scored["public_bad_good_gap"])
        + 0.90 * good_low(scored["rowstate_pred_public_loss_mean"])
        + 0.80 * good_low(scored["rowstate_bad_minus_good_exposure"])
        + 0.90 * good_high(scored["e363_robust_score"])
        + 0.55 * good_low(scored["pred_delta_vs_current_p90"])
    )
    base = scored[scored["variant"].astype(str).eq(base_variant)]
    if base.empty:
        base = scored.sort_values("e364_public_like_score", ascending=False).head(1)
    base_row = base.iloc[0]
    scored["scenario_gate"] = (
        scored["e363_submission_gate"].fillna(False).astype(bool)
        & (scored["scenario_pred_public_delta_mean"] <= float(base_row["scenario_pred_public_delta_mean"]) + 5.0e-5)
        & (scored["scenario_pred_public_delta_std"] <= float(base_row["scenario_pred_public_delta_std"]) + 2.5e-4)
        & (scored["public_bad_axis_sum"] <= float(base_row["public_bad_axis_sum"]) + 0.12)
        & (scored["rowstate_pred_public_loss_mean"] <= float(base_row["rowstate_pred_public_loss_mean"]) + 2.5e-4)
        & (scored["rowstate_bad_minus_good_exposure"] <= float(base_row["rowstate_bad_minus_good_exposure"]) + 0.035)
        & (scored["e363_robust_score"] >= max(0.50, float(base_row["e363_robust_score"]) - 0.08))
    )
    gated = scored[scored["scenario_gate"]].copy()
    if gated.empty:
        return scored.assign(scenario_rank=np.nan)
    ranks = gated["scenario_public_like_score"].rank(ascending=False, method="min")
    scored["scenario_rank"] = np.nan
    scored.loc[gated.index, "scenario_rank"] = ranks
    return scored


def run_scenarios(known: pd.DataFrame, pool: pd.DataFrame, feature_sets: dict[str, list[str]], e364_variant: str, e363_variant: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    train0 = known[known["available"].fillna(False).astype(bool)].copy().reset_index(drop=True)
    drops: list[tuple[str, str | None]] = [("none", None)]
    drops += [(f"drop_{safe_id(b, 42)}", b) for b in train0["basename"].astype(str).tolist()]
    scenario_rows: list[dict[str, Any]] = []
    rank_rows: list[pd.DataFrame] = []

    for view_name, cols in feature_sets.items():
        for drop_name, drop_base in drops:
            train = train0.copy()
            if drop_base is not None:
                train = train[~train["basename"].astype(str).eq(drop_base)].reset_index(drop=True)
            pred_mean, pred_std, diag = predict_pool(train, pool, cols)
            scored = score_scenario(pool, pred_mean, pred_std, e363_variant)
            gated = scored[scored["scenario_gate"]].copy()
            top = gated.sort_values("scenario_public_like_score", ascending=False).head(1)
            e364 = scored[scored["variant"].astype(str).eq(e364_variant)].head(1)
            e363 = scored[scored["variant"].astype(str).eq(e363_variant)].head(1)
            if top.empty or e364.empty or e363.empty:
                continue
            top_row = top.iloc[0]
            e364_row = e364.iloc[0]
            e363_row = e363.iloc[0]
            scenario_id = f"{view_name}__{drop_name}"
            scenario_rows.append(
                {
                    "scenario_id": scenario_id,
                    "feature_view": view_name,
                    "dropped_public": drop_base or "none",
                    "train_rows": int(len(train)),
                    "feature_count": int(len(cols)),
                    "gated_count": int(len(gated)),
                    "top_variant": top_row["variant"],
                    "top_family": top_row.get("family", ""),
                    "top_file": top_row.get("file", ""),
                    "top_score": float(top_row["scenario_public_like_score"]),
                    "e364_rank": float(e364_row["scenario_rank"]) if pd.notna(e364_row["scenario_rank"]) else np.nan,
                    "e363_rank": float(e363_row["scenario_rank"]) if pd.notna(e363_row["scenario_rank"]) else np.nan,
                    "e364_score": float(e364_row["scenario_public_like_score"]),
                    "e363_score": float(e363_row["scenario_public_like_score"]),
                    "e364_minus_e363_score": float(e364_row["scenario_public_like_score"] - e363_row["scenario_public_like_score"]),
                    "e364_beats_e363": bool(e364_row["scenario_public_like_score"] > e363_row["scenario_public_like_score"]),
                    "top_is_e364": bool(str(top_row["variant"]) == e364_variant),
                    "top_is_e363": bool(str(top_row["variant"]) == e363_variant),
                    **diag,
                }
            )
            slim = scored[
                [
                    "variant",
                    "family",
                    "file",
                    "scenario_gate",
                    "scenario_rank",
                    "scenario_public_like_score",
                    "scenario_pred_public_delta_mean",
                    "scenario_pred_public_delta_std",
                ]
            ].copy()
            slim["scenario_id"] = scenario_id
            rank_rows.append(slim[slim["scenario_gate"] | slim["variant"].astype(str).isin([e364_variant, e363_variant])])

    scenarios = pd.DataFrame(scenario_rows)
    all_ranks = pd.concat(rank_rows, ignore_index=True) if rank_rows else pd.DataFrame()
    scenarios.to_csv(SCENARIO_OUT, index=False)
    return scenarios, all_ranks


def aggregate_support(all_ranks: pd.DataFrame, scenario_count: int) -> pd.DataFrame:
    if all_ranks.empty:
        return pd.DataFrame()
    support = (
        all_ranks.groupby(["variant", "family", "file"], dropna=False)
        .agg(
            gate_count=("scenario_gate", "sum"),
            rank_mean=("scenario_rank", "mean"),
            rank_median=("scenario_rank", "median"),
            rank_min=("scenario_rank", "min"),
            top1_count=("scenario_rank", lambda x: int((x == 1).sum())),
            top5_count=("scenario_rank", lambda x: int((x <= 5).sum())),
            top10_count=("scenario_rank", lambda x: int((x <= 10).sum())),
            score_mean=("scenario_public_like_score", "mean"),
            score_std=("scenario_public_like_score", "std"),
            pred_mean=("scenario_pred_public_delta_mean", "mean"),
            pred_std_mean=("scenario_pred_public_delta_std", "mean"),
        )
        .reset_index()
    )
    for col in ["gate_count", "top1_count", "top5_count", "top10_count"]:
        support[f"{col.replace('_count', '')}_rate"] = support[col] / max(1, scenario_count)
    support = support.sort_values(["top1_count", "top5_count", "rank_mean", "score_mean"], ascending=[False, False, True, False]).reset_index(drop=True)
    support.to_csv(SUPPORT_OUT, index=False)
    return support


def copy_uploadsafe(path: Path, variant: str) -> Path:
    for stale in OUT.glob(f"{UPLOAD_PREFIX}_selected_*_uploadsafe.csv"):
        stale.unlink()
    frame = pd.read_csv(path)
    for target in TARGETS:
        frame[target] = clip_prob(frame[target].to_numpy(dtype=np.float64))
    out = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(variant, 70)}_{short_hash(frame)}_uploadsafe.csv"
    frame.to_csv(out, index=False)
    return out


def decide(pool: pd.DataFrame, support: pd.DataFrame, scenarios: pd.DataFrame, e364_variant: str, e363_variant: str) -> pd.DataFrame:
    scenario_count = max(1, len(scenarios))
    e364_sup = support[support["variant"].astype(str).eq(e364_variant)].head(1)
    e363_sup = support[support["variant"].astype(str).eq(e363_variant)].head(1)
    top_sup = support.head(1)
    e364_top10 = float(e364_sup["top10_rate"].iloc[0]) if len(e364_sup) else 0.0
    e364_top1 = float(e364_sup["top1_rate"].iloc[0]) if len(e364_sup) else 0.0
    e363_top10 = float(e363_sup["top10_rate"].iloc[0]) if len(e363_sup) else 0.0
    e364_better_rate = float(scenarios["e364_beats_e363"].mean()) if "e364_beats_e363" in scenarios else 0.0
    top_variant = str(top_sup["variant"].iloc[0]) if len(top_sup) else e364_variant
    top_top1 = float(top_sup["top1_rate"].iloc[0]) if len(top_sup) else 0.0

    if top_variant != e364_variant and top_top1 >= max(e364_top1 + 0.15, 0.20):
        decision = "select_e365_jackknife_stable_replacement"
        chosen_variant = top_variant
        reason = "A different E363-gated candidate wins substantially more jackknife scenarios than the E364 public-like pick."
    elif e364_better_rate >= 0.60 and e364_top10 >= 0.50:
        decision = "support_e364_publiclike_probe"
        chosen_variant = e364_variant
        reason = "E364 remains ahead of E363 under most leave-public/feature-view stresses and stays frequently in the top10."
    elif e363_top10 > e364_top10 and e364_better_rate < 0.50:
        decision = "demote_to_e363_conservative_reference"
        chosen_variant = e363_variant
        reason = "The jackknife stress prefers the source-law-preserving E363 point over the E364 donor-graft public-like pick."
    else:
        decision = "inconclusive_keep_e364_as_information_probe"
        chosen_variant = e364_variant
        reason = "E364 is not decisively stable, but it remains the more informative donor-graft hypothesis than E363."

    chosen_pool = pool[pool["variant"].astype(str).eq(chosen_variant)].head(1)
    if chosen_pool.empty:
        chosen_pool = pool.sort_values("e364_public_like_score", ascending=False).head(1)
        chosen_variant = str(chosen_pool.iloc[0]["variant"])
    src = locate(chosen_pool.iloc[0]["file"])
    upload = copy_uploadsafe(src, chosen_variant) if src is not None else None
    row = chosen_pool.iloc[0].to_dict()
    row.update(
        {
            "decision": decision,
            "reason": reason,
            "scenario_count": int(scenario_count),
            "e364_variant": e364_variant,
            "e363_variant": e363_variant,
            "e364_better_e363_rate": e364_better_rate,
            "e364_top1_rate": e364_top1,
            "e364_top10_rate": e364_top10,
            "e363_top10_rate": e363_top10,
            "support_top_variant": top_variant,
            "support_top1_rate": top_top1,
            "selected_uploadsafe_file": rel(upload),
        }
    )
    out = pd.DataFrame([row])
    out.to_csv(SELECTION_OUT, index=False)
    return out


def write_report(
    known: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    scenarios: pd.DataFrame,
    support: pd.DataFrame,
    selected: pd.DataFrame,
    e364_variant: str,
    e363_variant: str,
) -> None:
    scenario_summary = (
        scenarios.groupby("feature_view")
        .agg(
            scenarios=("scenario_id", "size"),
            e364_better_rate=("e364_beats_e363", "mean"),
            e364_rank_mean=("e364_rank", "mean"),
            e363_rank_mean=("e363_rank", "mean"),
            gated_mean=("gated_count", "mean"),
            top_e364_rate=("top_is_e364", "mean"),
            top_e363_rate=("top_is_e363", "mean"),
        )
        .reset_index()
        if not scenarios.empty
        else pd.DataFrame()
    )
    selected_cols = [
        "decision",
        "variant",
        "family",
        "selected_uploadsafe_file",
        "scenario_count",
        "e364_better_e363_rate",
        "e364_top1_rate",
        "e364_top10_rate",
        "e363_top10_rate",
        "support_top_variant",
        "support_top1_rate",
        "reason",
    ]
    support_cols = [
        "variant",
        "family",
        "top1_count",
        "top5_count",
        "top10_count",
        "gate_count",
        "rank_mean",
        "score_mean",
        "pred_mean",
        "file",
    ]
    lines = [
        "# E365 Public-Like Jackknife Stress",
        "",
        "## Question",
        "",
        "Did E364's donor-graft candidate survive because it captures a public-like hidden lifestyle-action state, or because the known-public sensor overfit one public observation or feature view?",
        "",
        "## Method",
        "",
        "- Fixed candidate pool: E364/E363 cell-action candidates, no new probability movement generation.",
        "- Stress dimensions: feature view masks plus leave-one-public-file-out training masks.",
        "- Feature views: " + ", ".join(f"`{k}`({len(v)})" for k, v in feature_sets.items()) + ".",
        "- Candidate must pass the E363 local gate and relative E363-selected margins under each scenario before it can rank.",
        "- Decision compares E364 donor-graft against E363 source-law-preserving target-scale under jackknife stability.",
        "",
        "## Inputs",
        "",
        f"- known available public files: `{int(known['available'].fillna(False).sum())}`",
        f"- scenario count: `{len(scenarios)}`",
        f"- E364 variant: `{e364_variant}`",
        f"- E363 variant: `{e363_variant}`",
        "",
        "## Scenario Summary",
        "",
        md_table(scenario_summary, n=20, floatfmt=".6f") if not scenario_summary.empty else "_No scenarios._",
        "",
        "## Top Jackknife-Supported Candidates",
        "",
        md_table(support[[c for c in support_cols if c in support.columns]].head(30), n=30, floatfmt=".6f") if not support.empty else "_No support rows._",
        "",
        "## Decision",
        "",
        md_table(selected[[c for c in selected_cols if c in selected.columns]], n=5, floatfmt=".6f"),
        "",
        "## Interpretation",
        "",
        "- If E364 remains top10 across many feature/drop scenarios, the donor-graft S1-recovery hypothesis is not just a one-observation public-sensor artifact.",
        "- If E363 dominates under jackknife, source-law preservation is safer than public-like donor geometry.",
        "- If a third candidate dominates, E364 found the right validation question but not the most stable point inside the basin.",
        "",
        "## Files",
        "",
        f"- `{rel(SCENARIO_OUT)}`",
        f"- `{rel(SUPPORT_OUT)}`",
        f"- `{rel(SELECTION_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    known = pd.read_csv(KNOWN_IN).replace([np.inf, -np.inf], np.nan)
    pool = pd.read_csv(POOL_IN).replace([np.inf, -np.inf], np.nan)
    e364_variant = str(pd.read_csv(E364_SELECTION_IN).iloc[0]["variant"])
    e363_variant = str(pd.read_csv(E363_SELECTION_IN).iloc[0]["variant"])
    feature_sets = available_feature_sets(known, pool)
    scenarios, all_ranks = run_scenarios(known, pool, feature_sets, e364_variant, e363_variant)
    support = aggregate_support(all_ranks, len(scenarios))
    selected = decide(pool, support, scenarios, e364_variant, e363_variant)
    write_report(known, feature_sets, scenarios, support, selected, e364_variant, e363_variant)

    print(f"feature_views={ {k: len(v) for k, v in feature_sets.items()} }")
    print(f"scenarios={len(scenarios)}")
    print(scenarios.groupby("feature_view")["e364_beats_e363"].mean().round(6).to_string())
    print(support[["variant", "family", "top1_count", "top10_count", "rank_mean", "score_mean"]].head(12).round(6).to_string(index=False))
    print(selected[["decision", "variant", "family", "selected_uploadsafe_file", "e364_better_e363_rate", "e364_top10_rate", "e363_top10_rate"]].round(6).to_string(index=False))
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
