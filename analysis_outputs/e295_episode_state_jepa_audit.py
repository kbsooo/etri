#!/usr/bin/env python3
"""E295: human episode-state JEPA audit.

After E293/E294, the S4 low-null branch is not worth another public test. This
audit returns to the broader human question: can raw lifelog stories be grouped
into larger day-level episode states that are reconstructable from context and
useful for Q/S labels under matched null stress?

No public LB is used and no submission file is created.
"""

from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e288_lifestyle_bundle_jepa_audit import (  # noqa: E402
    TARGETS,
    base_label_matrix,
    build_context_views,
    clip_prob,
    folds_for,
    groups_for,
    label_cv_loss,
    load_frames,
    md_table,
    oof_multi_ridge,
    shuffled_matrix,
    stable_seed,
)


RNG_SEED = 20260531 + 295
# Fast public-free falsification pass. E295 is an atlas, not a final promotion
# governor; any candidate-like row must be rerun with a stricter null budget.
N_REPS = 4

DEFINITION_OUT = OUT / "e295_episode_state_definition.csv"
RECON_OUT = OUT / "e295_episode_state_recon_summary.csv"
LABEL_OUT = OUT / "e295_episode_state_label_stress.csv"
TARGET_OUT = OUT / "e295_episode_state_target_detail.csv"
NULL_OUT = OUT / "e295_episode_state_nulls.csv"
REPORT_OUT = OUT / "e295_episode_state_jepa_report.md"


EPISODE_SPECS: dict[str, dict[str, Any]] = {
    "commute_pressure": {
        "human_story": "weekday commute, vehicle exposure, routine pressure, less home stability",
        "components": [
            ("human_social", "commute_workday", 1.0),
            ("human_social", "vehicle_noise_day", 0.8),
            ("human_social", "weekday_routine_pressure", 0.7),
            ("human_social", "afterwork_recovery", -0.35),
            ("human_social", "home_stability", -0.55),
        ],
    },
    "bedtime_arousal": {
        "human_story": "bright screen, messages, search spiral, media/game and phone-in-bed before sleep",
        "components": [
            ("human_social", "bright_light_late", 1.0),
            ("human_social", "phone_in_bed", 0.9),
            ("human_social", "deepnight_phone_awake", 0.9),
            ("human_social", "presleep_msg_drag", 0.75),
            ("human_social", "late_msg_call", 0.7),
            ("human_social", "late_search_spiral", 0.75),
            ("human_social", "media_binge_late", 0.55),
            ("human_social", "game_dopamine_late", 0.55),
            ("human_social", "screen_fragmentation", 0.75),
            ("human_social", "quiet_dark_bedtime", -0.65),
        ],
    },
    "routine_fragmentation": {
        "human_story": "scattered app attention, fragmented screen use, broken routine, sensor sparse/noisy day",
        "components": [
            ("human_social", "app_entropy_scattered_day", 1.0),
            ("human_social", "screen_fragmentation", 0.85),
            ("human_social", "single_app_monotony", 0.55),
            ("human_social", "weekend_social_jetlag", 0.65),
            ("human_social", "sensor_sparse_day", 0.45),
            ("human_social", "ritual_anchor", -0.75),
            ("human_social", "charge_bed_anchor", -0.55),
            ("human_social", "quiet_dark_bedtime", -0.70),
        ],
    },
    "routine_anchor_recovery": {
        "human_story": "stable home/charging/ritual routine, quiet bedtime, lower arousal recovery",
        "components": [
            ("human_social", "ritual_anchor", 1.0),
            ("human_social", "charge_bed_anchor", 0.85),
            ("human_social", "quiet_dark_bedtime", 1.0),
            ("human_social", "weekend_ritual_rest", 0.65),
            ("human_social", "home_stability", 0.65),
            ("human_social", "low_hr_recovery", 0.55),
            ("human_social", "app_entropy_scattered_day", -0.75),
            ("human_social", "deepnight_phone_awake", -0.65),
        ],
    },
    "cashflow_stress": {
        "human_story": "money rumination, budget squeeze, bill anxiety, late shopping/finance arousal",
        "components": [
            ("human_social", "finance_shopping_stress", 0.8),
            ("cashflow", "*pre*_cash_stress", 0.9),
            ("cashflow", "*pre*_budget_squeeze", 0.8),
            ("cashflow", "*near*_money_rumination", 0.7),
            ("cashflow", "*late_shopping", 0.5),
            ("cashflow", "eom_bill_anxiety", 0.8),
            ("cashflow", "*post*_relief_home", -0.35),
        ],
    },
    "cashflow_relief_spend": {
        "human_story": "payday/month-start relief, spending/outings, reset energy",
        "components": [
            ("cashflow", "*post*_spend_outing", 0.9),
            ("cashflow", "*post*_relief_home", 0.7),
            ("cashflow", "monthstart_reset_relief", 0.8),
            ("cashflow", "monthstart_spending_reset", 0.75),
            ("cashflow", "*pre*_cash_stress", -0.45),
            ("cashflow", "eom_bill_anxiety", -0.35),
        ],
    },
    "physiology_strain": {
        "human_story": "late heart stress, fatigue, overtraining, sedentary screen load",
        "components": [
            ("human_social", "heart_stress_late", 1.0),
            ("human_social", "physical_fatigue", 0.8),
            ("human_social", "overtraining_arousal", 0.8),
            ("human_social", "sedentary_screen_day", 0.55),
            ("human_social", "low_hr_recovery", -0.75),
            ("human_social", "outdoor_nature_day", -0.35),
        ],
    },
    "home_recovery": {
        "human_story": "home stability, afterwork recovery, low HR recovery, quiet/dark bedtime",
        "components": [
            ("human_social", "home_stability", 1.0),
            ("human_social", "afterwork_recovery", 0.8),
            ("human_social", "low_hr_recovery", 0.75),
            ("human_social", "quiet_dark_bedtime", 0.75),
            ("human_social", "outdoor_nature_day", 0.35),
            ("human_social", "night_out_mobility", -0.65),
            ("human_social", "vehicle_noise_day", -0.45),
        ],
    },
    "social_overload": {
        "human_story": "late communication, public social evening, night-out mobility, less isolation",
        "components": [
            ("human_social", "late_msg_call", 0.85),
            ("human_social", "presleep_msg_drag", 0.8),
            ("human_social", "public_social_evening", 0.75),
            ("human_social", "night_out_mobility", 0.75),
            ("human_social", "social_isolation_media", -0.45),
            ("human_social", "home_stability", -0.35),
        ],
    },
    "measurement_wear_confidence": {
        "human_story": "high sensor wear and dense measurement versus sparse sensor day",
        "components": [
            ("human_social", "high_sensor_wear_day", 1.0),
            ("human_social", "sensor_sparse_day", -1.0),
        ],
    },
    "badnight_aftereffect": {
        "human_story": "morning-after bad-night trace and recovery debt visible in next-day diary",
        "components": [
            ("human_social", "morning_after_badnight", 1.0),
            ("human_social", "physical_fatigue", 0.55),
            ("human_social", "sedentary_screen_day", 0.45),
            ("human_social", "low_hr_recovery", -0.35),
        ],
    },
}


def base_story_cols(frame: pd.DataFrame) -> list[str]:
    blocked = {
        "subject_id",
        "sleep_date",
        "lifelog_date",
        "split",
        "weekday",
        "is_weekend",
        "subject_order",
        "dateblock_group",
        "lifelog_dom",
        *TARGETS,
    }
    suffixes = ("_subj_z", "_abs_subj_z", "_weekend", "_active")
    return [c for c in frame.columns if c not in blocked and not c.endswith(suffixes)]


def robust_standardize(s: pd.Series, train_mask: np.ndarray) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
    tr = x.iloc[train_mask]
    med = float(tr.median())
    q25 = float(tr.quantile(0.25))
    q75 = float(tr.quantile(0.75))
    scale = (q75 - q25) / 1.349
    if not np.isfinite(scale) or scale < 1.0e-9:
        scale = float(tr.std(ddof=0))
    if not np.isfinite(scale) or scale < 1.0e-9:
        return pd.Series(0.0, index=s.index)
    return ((x - med) / scale).replace([np.inf, -np.inf], 0.0).fillna(0.0)


def preferred_col(frame: pd.DataFrame, base_col: str) -> str | None:
    for col in [f"{base_col}_subj_z", base_col, f"{base_col}_active"]:
        if col in frame.columns:
            return col
    return None


def expand_components(spec: dict[str, Any], feature_frames: dict[str, pd.DataFrame]) -> list[tuple[str, str, float]]:
    out: list[tuple[str, str, float]] = []
    seen: set[tuple[str, str]] = set()
    for source, pattern, weight in spec["components"]:
        frame = feature_frames[source]
        bases = base_story_cols(frame)
        if "*" in pattern:
            matches = [base for base in bases if fnmatch(base, pattern)]
        else:
            matches = [pattern] if pattern in bases or preferred_col(frame, pattern) is not None else []
        for base_col in matches:
            col = preferred_col(frame, base_col)
            if col is None or (source, col) in seen:
                continue
            seen.add((source, col))
            out.append((source, col, float(weight)))
    return out


def build_episode_matrix(base: pd.DataFrame, feature_frames: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_mask = base["split"].eq("train").to_numpy()
    definitions: list[dict[str, Any]] = []
    episode_values: dict[str, pd.Series] = {}
    for episode, spec in EPISODE_SPECS.items():
        parts = expand_components(spec, feature_frames)
        if not parts:
            episode_values[episode] = pd.Series(0.0, index=base.index)
            continue
        weighted = []
        total_abs = 0.0
        for source, col, weight in parts:
            z = robust_standardize(feature_frames[source][col], train_mask)
            weighted.append(weight * z)
            total_abs += abs(weight)
            definitions.append(
                {
                    "episode": episode,
                    "human_story": spec["human_story"],
                    "source": source,
                    "feature_col": col,
                    "weight": weight,
                }
            )
        raw_score = sum(weighted) / max(total_abs, 1.0e-9)
        episode_values[episode] = robust_standardize(raw_score, train_mask).clip(-6.0, 6.0)
    return pd.DataFrame(episode_values, index=base.index), pd.DataFrame(definitions)


def fit_predict_test(x_train: pd.DataFrame, y_train: pd.DataFrame, x_test: pd.DataFrame) -> np.ndarray:
    from e288_lifestyle_bundle_jepa_audit import fit_predict_test as _fit_predict_test

    return _fit_predict_test(x_train, y_train, x_test)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    if np.std(a) < 1.0e-12 or np.std(b) < 1.0e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def make_latent(pred_train: np.ndarray, pred_test: np.ndarray, n_components: int = 5) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float]]:
    n_components = max(1, min(n_components, pred_train.shape[1], pred_train.shape[0] - 1))
    scaler = StandardScaler()
    z_train = scaler.fit_transform(pred_train)
    z_test = scaler.transform(pred_test)
    pca = PCA(n_components=n_components, random_state=RNG_SEED)
    train_lat = pca.fit_transform(z_train)
    test_lat = pca.transform(z_test)
    svals = np.linalg.svd(train_lat - train_lat.mean(axis=0, keepdims=True), compute_uv=False)
    if len(svals) == 0 or float(np.sum(svals**2)) <= 1.0e-12:
        participation = 0.0
        anisotropy = np.inf
    else:
        participation = float((np.sum(svals**2) ** 2) / np.sum(svals**4))
        anisotropy = float(np.max(svals) / max(np.min(svals), 1.0e-9))
    cols = [f"episode_pc{i+1}" for i in range(n_components)]
    return (
        pd.DataFrame(train_lat, columns=cols),
        pd.DataFrame(test_lat, columns=cols),
        {
            "latent_dims": float(n_components),
            "explained_var_sum": float(np.sum(pca.explained_variance_ratio_)),
            "participation_ratio": participation,
            "anisotropy": anisotropy,
        },
    )


def mode_groups(train_df: pd.DataFrame) -> dict[str, pd.Series]:
    return {
        "row": groups_for(train_df, "subject5").reset_index(drop=True),
        "subject": groups_for(train_df, "subject5").reset_index(drop=True),
        "dateblock": groups_for(train_df, "dateblock5").reset_index(drop=True),
    }


def shuffle_episode(values: np.ndarray, mode: str, train_df: pd.DataFrame, rng: np.random.Generator) -> np.ndarray:
    if mode == "row":
        return values[rng.permutation(len(values))]
    groups = groups_for(train_df, "subject5" if mode == "subject" else "dateblock5").reset_index(drop=True)
    return shuffled_matrix(values, mode, groups, rng)


def evaluate_episode_targets(
    train_df: pd.DataFrame,
    base_x: pd.DataFrame,
    pred_state: pd.DataFrame,
    view_id: str,
    split_name: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups = groups_for(train_df, split_name).reset_index(drop=True)
    baseline = {t: label_cv_loss(base_x, train_df[t].to_numpy(dtype=int), groups) for t in TARGETS}
    target_rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(stable_seed("e295_target", view_id, split_name))

    for episode in pred_state.columns:
        state = pred_state[[episode]].reset_index(drop=True)
        for target in TARGETS:
            y = train_df[target].to_numpy(dtype=int)
            x = pd.concat([base_x.reset_index(drop=True), state], axis=1)
            actual_loss = label_cv_loss(x, y, groups)
            actual_delta = actual_loss - baseline[target]
            null_vals_by_mode: dict[str, list[float]] = {"row": [], "subject": [], "dateblock": []}
            for mode in null_vals_by_mode:
                for rep in range(N_REPS):
                    shuffled = shuffle_episode(state.to_numpy(), mode, train_df, rng)
                    nx = pd.concat(
                        [base_x.reset_index(drop=True), pd.DataFrame(shuffled, columns=[episode])],
                        axis=1,
                    )
                    ndelta = label_cv_loss(nx, y, groups) - baseline[target]
                    null_vals_by_mode[mode].append(ndelta)
                    null_rows.append(
                        {
                            "view_id": view_id,
                            "split": split_name,
                            "episode": episode,
                            "target": target,
                            "mode": mode,
                            "rep": rep,
                            "null_delta": ndelta,
                        }
                    )
            null_vals = np.asarray(sum(null_vals_by_mode.values(), []), dtype=np.float64)
            mode_dom = {mode: float(np.mean(actual_delta < np.asarray(vals))) for mode, vals in null_vals_by_mode.items()}
            target_rows.append(
                {
                    "view_id": view_id,
                    "split": split_name,
                    "episode": episode,
                    "target": target,
                    "base_loss": baseline[target],
                    "state_loss": actual_loss,
                    "delta_logloss": actual_delta,
                    "null_q20": float(np.quantile(null_vals, 0.20)),
                    "null_median": float(np.median(null_vals)),
                    "null_best": float(np.min(null_vals)),
                    "dominance": float(np.mean(actual_delta < null_vals)),
                    "row_dominance": mode_dom["row"],
                    "subject_dominance": mode_dom["subject"],
                    "dateblock_dominance": mode_dom["dateblock"],
                    "target_gate": bool(
                        actual_delta < -0.0015
                        and np.mean(actual_delta < null_vals) >= 0.85
                        and min(mode_dom.values()) >= 0.58
                    ),
                }
            )
    return target_rows, null_rows


def evaluate_bundle_label_stress(
    train_df: pd.DataFrame,
    base_x: pd.DataFrame,
    pred_state: pd.DataFrame,
    latent_x: pd.DataFrame,
    view_id: str,
    split_name: str,
) -> list[dict[str, Any]]:
    groups = groups_for(train_df, split_name).reset_index(drop=True)
    baseline = {t: label_cv_loss(base_x, train_df[t].to_numpy(dtype=int), groups) for t in TARGETS}
    reps = {
        "episode_scores": pred_state.reset_index(drop=True),
        "episode_pc": latent_x.reset_index(drop=True),
    }
    rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(stable_seed("e295_bundle", view_id, split_name))
    for rep_id, add_x in reps.items():
        x = pd.concat([base_x.reset_index(drop=True), add_x], axis=1)
        deltas = []
        target_delta = {}
        for target in TARGETS:
            delta = label_cv_loss(x, train_df[target].to_numpy(dtype=int), groups) - baseline[target]
            deltas.append(delta)
            target_delta[f"{target}_delta"] = delta
        null_vals = []
        for mode in ["row", "subject", "dateblock"]:
            for rep in range(N_REPS):
                shuffled = shuffle_episode(add_x.to_numpy(), mode, train_df, rng)
                nx = pd.concat(
                    [base_x.reset_index(drop=True), pd.DataFrame(shuffled, columns=add_x.columns)],
                    axis=1,
                )
                losses = [
                    label_cv_loss(nx, train_df[target].to_numpy(dtype=int), groups) - baseline[target]
                    for target in TARGETS
                ]
                null_vals.append(float(np.mean(losses)))
        null = np.asarray(null_vals, dtype=np.float64)
        rows.append(
            {
                "view_id": view_id,
                "split": split_name,
                "rep": rep_id,
                "actual_delta_mean": float(np.mean(deltas)),
                "actual_delta_best": float(np.min(deltas)),
                "actual_delta_worst": float(np.max(deltas)),
                "targets_improved": int(np.sum(np.asarray(deltas) < 0.0)),
                "null_q20": float(np.quantile(null, 0.20)),
                "null_median": float(np.median(null)),
                "null_best": float(np.min(null)),
                "dominance": float(np.mean(float(np.mean(deltas)) < null)),
                "label_gate": bool(float(np.mean(deltas)) < 0.0 and np.mean(float(np.mean(deltas)) < null) >= 0.85),
                **target_delta,
            }
        )
    return rows


def run() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base, raw, _, feature_frames = load_frames()
    story_state, definitions = build_episode_matrix(base, feature_frames)
    contexts = build_context_views(base, raw)
    train_mask = base["split"].eq("train").to_numpy()
    train_df = base.loc[train_mask].reset_index(drop=True)
    test_df = base.loc[~train_mask].reset_index(drop=True)
    y_episode = story_state.loc[train_mask].reset_index(drop=True)

    recon_rows: list[dict[str, Any]] = []
    label_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    base_x = base_label_matrix(train_df)

    for view_id, ctx in contexts.items():
        for split_name in ["subject5", "dateblock5"]:
            x_train = ctx.loc[train_mask].reset_index(drop=True)
            x_test = ctx.loc[~train_mask].reset_index(drop=True)
            groups = groups_for(train_df, split_name).reset_index(drop=True)
            pred_train = oof_multi_ridge(x_train, y_episode, groups)
            pred_test = fit_predict_test(x_train, y_episode, x_test)
            r2_vals = r2_score(y_episode.to_numpy(), pred_train, multioutput="raw_values")
            corr_vals = [corr(y_episode[col].to_numpy(dtype=np.float64), pred_train[:, i]) for i, col in enumerate(y_episode.columns)]
            train_lat, _, diag = make_latent(pred_train, pred_test)
            pred_state = pd.DataFrame(pred_train, columns=y_episode.columns)
            target, null = evaluate_episode_targets(train_df, base_x, pred_state, view_id, split_name)
            target_rows.extend(target)
            null_rows.extend(null)
            label_rows.extend(evaluate_bundle_label_stress(train_df, base_x, pred_state, train_lat, view_id, split_name))
            for i, episode in enumerate(y_episode.columns):
                actual = y_episode[episode].to_numpy(dtype=np.float64)
                pred = pred_train[:, i]
                recon_rows.append(
                    {
                        "view_id": view_id,
                        "split": split_name,
                        "episode": episode,
                        "context_cols": int(x_train.shape[1]),
                        "r2": float(r2_vals[i]),
                        "corr": float(corr_vals[i]),
                        "train_mean": float(actual.mean()),
                        "test_pred_mean": float(pred_test[:, i].mean()),
                        "train_test_pred_z_gap": float((pred_test[:, i].mean() - pred.mean()) / (np.std(pred) + 1.0e-9)),
                        **diag,
                    }
                )
    return definitions, pd.DataFrame(recon_rows), pd.DataFrame(label_rows), pd.DataFrame(target_rows), pd.DataFrame(null_rows)


def write_report(definitions: pd.DataFrame, recon: pd.DataFrame, labels: pd.DataFrame, targets: pd.DataFrame) -> None:
    target_gates = targets[targets["target_gate"].astype(bool)].sort_values("delta_logloss") if not targets.empty else targets
    label_gates = labels[labels["label_gate"].astype(bool)].sort_values("actual_delta_mean") if not labels.empty else labels
    recon_summary = (
        recon.groupby(["view_id", "split"])
        .agg(
            episode_count=("episode", "count"),
            r2_mean=("r2", "mean"),
            r2_median=("r2", "median"),
            r2_positive_rate=("r2", lambda s: float(np.mean(np.asarray(s) > 0.0))),
            corr_mean=("corr", "mean"),
            abs_test_gap_mean=("train_test_pred_z_gap", lambda s: float(np.mean(np.abs(s)))),
        )
        .reset_index()
        .sort_values(["r2_mean", "corr_mean"], ascending=False)
    )
    family = (
        targets.groupby("episode")
        .agg(
            best_delta=("delta_logloss", "min"),
            mean_delta=("delta_logloss", "mean"),
            target_gates=("target_gate", "sum"),
            best_dominance=("dominance", "max"),
        )
        .reset_index()
        .sort_values(["target_gates", "best_delta"], ascending=[False, True])
    )
    lines = [
        "# E295 Human Episode-State JEPA Audit",
        "",
        "## Question",
        "",
        "Can raw lifelog stories be grouped into larger human episode states that are context-predictable and label-useful under matched null stress?",
        "",
        "## Episode States",
        "",
        md_table(definitions[["episode", "human_story", "source", "feature_col", "weight"]], n=80),
        "",
        "## Reconstruction Summary",
        "",
        md_table(recon_summary, n=20),
        "",
        "## Best Episode Reconstructions",
        "",
        md_table(recon.sort_values("r2", ascending=False)[["view_id", "split", "episode", "r2", "corr", "train_test_pred_z_gap"]], n=30),
        "",
        "## Bundle Label Stress",
        "",
        md_table(labels.sort_values(["label_gate", "actual_delta_mean"], ascending=[False, True]), n=20),
        "",
        "## Target-Specific Episode Gates",
        "",
        md_table(
            target_gates[
                [
                    "view_id",
                    "split",
                    "episode",
                    "target",
                    "delta_logloss",
                    "null_median",
                    "null_best",
                    "dominance",
                    "row_dominance",
                    "subject_dominance",
                    "dateblock_dominance",
                ]
            ]
            if not target_gates.empty
            else target_gates,
            n=40,
        ),
        "",
        "## Episode Family Read",
        "",
        md_table(family, n=30),
        "",
        "## Decision",
        "",
    ]
    if len(label_gates) or len(target_gates):
        lines.append("E295 found train/null-surviving episode-state signals. These are not submissions yet; next step is a materialization governor only for the gated episode-target rows.")
    else:
        lines.append("No E295 episode state is submission-ready. Keep the strongest states as diagnostics and do not spend public LB.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This experiment is deliberately more human than cell-level surgery: commute pressure, bedtime arousal, routine fragmentation/anchor, cash-flow stress/relief, physiology strain, home recovery, social overload, measurement confidence, and bad-night aftereffect are treated as hidden day-level states. A state only matters if another context can predict it and if that predicted state beats row/subject/dateblock shuffles on labels.",
            "",
            "## Files",
            "",
            f"- `{DEFINITION_OUT.name}`",
            f"- `{RECON_OUT.name}`",
            f"- `{LABEL_OUT.name}`",
            f"- `{TARGET_OUT.name}`",
            f"- `{NULL_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    definitions, recon, labels, targets, nulls = run()
    definitions.to_csv(DEFINITION_OUT, index=False)
    recon.to_csv(RECON_OUT, index=False)
    labels.to_csv(LABEL_OUT, index=False)
    targets.to_csv(TARGET_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    write_report(definitions, recon, labels, targets)
    print(f"episodes={definitions['episode'].nunique()}")
    print(f"recon_rows={len(recon)}")
    print(f"label_gates={int(labels['label_gate'].sum()) if not labels.empty else 0}")
    print(f"target_gates={int(targets['target_gate'].sum()) if not targets.empty else 0}")
    if not targets.empty:
        best = targets.sort_values("delta_logloss").iloc[0]
        print(f"best_target={best['episode']}/{best['target']} delta={best['delta_logloss']:.9f}")
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
