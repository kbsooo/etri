#!/usr/bin/env python3
"""E282: app-entropy story-state materializer with public-free governor.

E281 says the strongest surviving human/social state is
``app_entropy_scattered_day``: a routine/attention-fragmentation story that can
be predicted from other context families and improves Q3/Q2/S2 train slices.

This script turns that story into small E247 logit edits, then refuses to use
public LB as the loop. A candidate is only considered submission-ready if its
row placement beats matched row/subject/dateblock nulls under the existing
public-anchor selector.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e282_appentropy_story_materializer_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e281_story_state_jepa_row_selector_audit as e281  # noqa: E402
from e272_public_free_candidate_audit import (  # noqa: E402
    CURRENT,
    evaluate_models,
    score_candidates,
    selected_models,
)
from public_anchor_bottleneck_decomposition import (  # noqa: E402
    KEYS,
    TARGETS,
    feature_row,
    known_public_table,
    load_sub,
    logit,
)
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


STORY_ID = "app_entropy_scattered_day"
RNG_SEED = 20260531 + 282
N_REPS = 11

STATE_OUT = OUT / "e282_appentropy_story_state.csv"
CANDIDATE_OUT = OUT / "e282_appentropy_story_materializer_candidates.csv"
NULLS_OUT = OUT / "e282_appentropy_story_materializer_nulls.csv"
SCORES_OUT = OUT / "e282_appentropy_story_materializer_scores.csv"
SUMMARY_OUT = OUT / "e282_appentropy_story_materializer_summary.csv"
REPORT_OUT = OUT / "e282_appentropy_story_materializer_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    z = np.asarray(x, dtype=np.float64)
    return 1.0 / (1.0 + np.exp(-z))


def short_hash(df: pd.DataFrame) -> str:
    arr = np.asarray(df[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def normalized_keys(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    out["subject_id"] = out["subject_id"].astype(str)
    return out.reset_index(drop=True)


def md_table(frame: pd.DataFrame, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else format(float(x), floatfmt))
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def story_row() -> pd.Series:
    _, stories, _ = e281.load_frames()
    hit = stories[stories["story_id"].eq(STORY_ID)]
    if hit.empty:
        raise RuntimeError(f"{STORY_ID} missing from E280/E281 story table")
    return hit.iloc[0]


def train_test_context() -> tuple[pd.DataFrame, pd.Series, np.ndarray, list[str]]:
    base, _, feature_frames = e281.load_frames()
    rec = story_row()
    score_col, score = e281.story_score(rec, feature_frames)
    ctx_cols = e281.context_columns(base, str(rec["story_id"]), str(rec["mapped_family"]))
    if not ctx_cols:
        raise RuntimeError("empty story-state context")
    return base, rec, score, ctx_cols


def ridge_oof_and_test(
    x_train: pd.DataFrame,
    y_train: np.ndarray,
    x_test: pd.DataFrame,
    train_meta: pd.DataFrame,
    split_name: str,
) -> tuple[np.ndarray, np.ndarray, float, float]:
    groups = e281.split_groups(train_meta, split_name).reset_index(drop=True)
    n_splits = min(5, int(groups.nunique()))
    if n_splits < 2:
        raise RuntimeError(f"not enough groups for {split_name}")
    folds = GroupKFold(n_splits=n_splits).split(np.zeros(len(groups)), groups=groups)
    oof = np.zeros(len(y_train), dtype=np.float64)
    test_preds: list[np.ndarray] = []
    for train_idx, valid_idx in folds:
        model = make_pipeline(StandardScaler(), Ridge(alpha=8.0))
        model.fit(x_train.iloc[train_idx], y_train[train_idx])
        oof[valid_idx] = model.predict(x_train.iloc[valid_idx])
        test_preds.append(model.predict(x_test))
    test_pred = np.mean(np.column_stack(test_preds), axis=1)
    r2 = float(r2_score(y_train, oof))
    corr = float(np.corrcoef(y_train, oof)[0, 1]) if np.std(y_train) > 1.0e-9 and np.std(oof) > 1.0e-9 else 0.0
    return oof, test_pred, r2, corr


def standardize_with_train(train_values: np.ndarray, test_values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mu = float(np.mean(train_values))
    sd = float(np.std(train_values))
    if sd < 1.0e-9:
        sd = 1.0
    return (train_values - mu) / sd, (test_values - mu) / sd


def build_story_state() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base, rec, score, ctx_cols = train_test_context()
    train_mask = base["split"].eq("train").to_numpy()
    test_mask = base["split"].eq("test").to_numpy()
    train = base.loc[train_mask].reset_index(drop=True)
    test = base.loc[test_mask].reset_index(drop=True)
    x_all = base[ctx_cols].replace([np.inf, -np.inf], 0.0).fillna(0.0).reset_index(drop=True)
    x_train = x_all.loc[train_mask].reset_index(drop=True)
    x_test = x_all.loc[test_mask].reset_index(drop=True)
    y_state = score[train_mask]

    subj_oof, subj_test, subj_r2, subj_corr = ridge_oof_and_test(x_train, y_state, x_test, train, "subject5")
    date_oof, date_test, date_r2, date_corr = ridge_oof_and_test(x_train, y_state, x_test, train, "dateblock5")
    subj_z_train, subj_z_test = standardize_with_train(subj_oof, subj_test)
    date_z_train, date_z_test = standardize_with_train(date_oof, date_test)
    avg_z_train = 0.5 * (subj_z_train + date_z_train)
    avg_z_test = 0.5 * (subj_z_test + date_z_test)

    state = pd.concat([base[KEYS + ["split", "dateblock_group"]].reset_index(drop=True)], axis=1)
    state["story_score_actual"] = score
    state.loc[train_mask, "state_subject_oof"] = subj_oof
    state.loc[test_mask, "state_subject_test"] = subj_test
    state.loc[train_mask, "state_dateblock_oof"] = date_oof
    state.loc[test_mask, "state_dateblock_test"] = date_test
    state.loc[train_mask, "state_subject_z"] = subj_z_train
    state.loc[test_mask, "state_subject_z"] = subj_z_test
    state.loc[train_mask, "state_dateblock_z"] = date_z_train
    state.loc[test_mask, "state_dateblock_z"] = date_z_test
    state.loc[train_mask, "state_avg_z"] = avg_z_train
    state.loc[test_mask, "state_avg_z"] = avg_z_test

    diagnostics = pd.DataFrame(
        [
            {
                "story_id": STORY_ID,
                "mapped_family": rec["mapped_family"],
                "score_col": rec["score_col"],
                "context_cols": len(ctx_cols),
                "split": "subject5",
                "state_oof_r2": subj_r2,
                "state_oof_corr": subj_corr,
            },
            {
                "story_id": STORY_ID,
                "mapped_family": rec["mapped_family"],
                "score_col": rec["score_col"],
                "context_cols": len(ctx_cols),
                "split": "dateblock5",
                "state_oof_r2": date_r2,
                "state_oof_corr": date_corr,
            },
        ]
    )
    return state, diagnostics, base


def target_direction_table(state: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    train_mask = base["split"].eq("train").to_numpy()
    train = base.loc[train_mask].reset_index(drop=True)
    z = state.loc[train_mask, "state_avg_z"].to_numpy(dtype=np.float64)
    x_label = e281.base_label_matrix(train).copy()
    x_label["story_state_avg_z"] = z

    target_detail = pd.read_csv(e281.TARGET_OUT)
    story_detail = target_detail[target_detail["story_id"].eq(STORY_ID)].copy()
    rows: list[dict[str, object]] = []
    for target in TARGETS:
        y = train[target].to_numpy(dtype=int)
        if len(np.unique(y)) < 2:
            coef = 0.0
        else:
            model = make_pipeline(StandardScaler(), LogisticRegression(C=0.35, max_iter=1000, solver="lbfgs"))
            model.fit(x_label, y)
            coef = float(model.named_steps["logisticregression"].coef_[0][-1])
        detail = story_detail[story_detail["target"].eq(target)]
        mean_delta = float(detail["delta_logloss"].mean()) if not detail.empty else np.nan
        min_delta = float(detail["delta_logloss"].min()) if not detail.empty else np.nan
        support = float(max(0.0, -mean_delta)) if pd.notna(mean_delta) else 0.0
        q20, q80 = np.quantile(z, [0.20, 0.80])
        low_rate = float(np.mean(y[z <= q20]))
        high_rate = float(np.mean(y[z >= q80]))
        rows.append(
            {
                "target": target,
                "logistic_coef_state_avg_z": coef,
                "label_rate_high_minus_low": high_rate - low_rate,
                "e281_mean_delta": mean_delta,
                "e281_best_delta": min_delta,
                "support_strength": support,
                "supported_for_materialization": bool(support > 0.001 and coef > 0.0),
            }
        )
    out = pd.DataFrame(rows)
    max_support = float(out["support_strength"].max())
    out["target_weight"] = np.where(
        (out["supported_for_materialization"]) & (max_support > 0.0),
        np.sqrt(out["support_strength"] / max_support),
        0.0,
    )
    return out


def state_shape(values: np.ndarray, train_values: np.ndarray, shape: str) -> np.ndarray:
    v = np.asarray(values, dtype=np.float64)
    if shape == "linear":
        return np.clip(v, -2.0, 2.0)
    if shape == "tail":
        q60 = float(np.quantile(np.abs(train_values), 0.60))
        q95 = float(np.quantile(np.abs(train_values), 0.95))
        scale = max(q95 - q60, 1.0e-9)
        out = np.sign(v) * np.maximum(np.abs(v) - q60, 0.0) / scale
        return np.clip(out, -1.75, 1.75)
    raise ValueError(shape)


def candidate_specs(direction: pd.DataFrame) -> list[dict[str, object]]:
    supported = set(direction.loc[direction["supported_for_materialization"], "target"].astype(str))
    scopes = [
        ("q3", ["Q3"]),
        ("q2q3", ["Q2", "Q3"]),
        ("q2q3s2", ["Q2", "Q3", "S2"]),
    ]
    specs: list[dict[str, object]] = []
    for scope_name, targets in scopes:
        if any(target not in supported for target in targets):
            continue
        if scope_name == "q3":
            shape_grid = [
                ("linear", [0.006, 0.010, 0.016, 0.022, 0.023, 0.024, 0.025, 0.026, 0.028, 0.030]),
                ("tail", [0.010, 0.014, 0.020, 0.030]),
            ]
        else:
            shape_grid = [("linear", [0.006, 0.010]), ("tail", [0.010, 0.014])]
        for shape, amplitudes in shape_grid:
            for amp in amplitudes:
                specs.append(
                    {
                        "scope": scope_name,
                        "targets": targets,
                        "shape": shape,
                        "amp": amp,
                    }
                )
    return specs


def write_candidate_submissions(state: pd.DataFrame, base: pd.DataFrame, direction: pd.DataFrame) -> pd.DataFrame:
    current = load_sub(CURRENT)
    sample = current[KEYS].copy()
    test_state = state[state["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    train_state = state[state["split"].eq("train")].sort_values(KEYS).reset_index(drop=True)
    if not normalized_keys(test_state).equals(normalized_keys(sample)):
        raise RuntimeError("story state test keys do not align with current submission")

    train_z = train_state["state_avg_z"].to_numpy(dtype=np.float64)
    test_z = test_state["state_avg_z"].to_numpy(dtype=np.float64)
    weight_map = direction.set_index("target")["target_weight"].to_dict()
    coef_map = direction.set_index("target")["logistic_coef_state_avg_z"].to_dict()
    specs = candidate_specs(direction)
    base_logits = logit(current[TARGETS].to_numpy(dtype=np.float64))
    rows: list[dict[str, object]] = []

    for spec_idx, spec in enumerate(specs):
        shape_values = state_shape(test_z, train_z, str(spec["shape"]))
        delta = np.zeros_like(base_logits)
        for target in spec["targets"]:
            target_idx = TARGETS.index(target)
            sign = 1.0 if float(coef_map[target]) >= 0.0 else -1.0
            delta[:, target_idx] = float(spec["amp"]) * sign * float(weight_map[target]) * shape_values

        out = current.copy()
        out[TARGETS] = clip_prob(sigmoid(base_logits + delta))
        target_tag = str(spec["scope"])
        amp_tag = f"{float(spec['amp']):.3f}".replace(".", "p")
        stem = f"submission_e282_appentropy_{target_tag}_{spec['shape']}_a{amp_tag}"
        path = OUT / f"{stem}_{short_hash(out)}.csv"
        out.to_csv(path, index=False)

        nonzero = np.abs(delta) > 1.0e-12
        rows.append(
            {
                "candidate_id": spec_idx,
                "basename": path.name,
                "source_path": rel(path),
                "scope": spec["scope"],
                "targets": ",".join(spec["targets"]),
                "shape": spec["shape"],
                "amp": spec["amp"],
                "changed_cells": int(nonzero.sum()),
                "changed_rows": int((np.max(np.abs(delta), axis=1) > 1.0e-12).sum()),
                "mean_abs_logit_delta": float(np.mean(np.abs(delta))),
                "max_abs_logit_delta": float(np.max(np.abs(delta))),
                "mean_signed_state_shape": float(np.mean(shape_values)),
                "std_signed_state_shape": float(np.std(shape_values)),
                "state_q10": float(np.quantile(shape_values, 0.10)),
                "state_q90": float(np.quantile(shape_values, 0.90)),
            }
        )
    candidates = pd.DataFrame(rows)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    return candidates


def test_meta(state: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    meta = state[state["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    out = meta[KEYS + ["dateblock_group"]].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col])
    if not normalized_keys(out).equals(normalized_keys(sample)):
        raise RuntimeError("E282 metadata does not align with current submission keys")
    return out


def write_null_candidate(
    base: pd.DataFrame,
    delta: np.ndarray,
    meta: pd.DataFrame,
    source_path: Path,
    mode: str,
    rep: int,
    seed: int,
) -> Path:
    rng = np.random.default_rng(seed)
    shuffled = np.zeros_like(delta)
    for target_idx in range(delta.shape[1]):
        values = delta[:, target_idx].copy()
        if mode == "row":
            shuffled[:, target_idx] = values[rng.permutation(len(values))]
        elif mode == "subject":
            for _, idx in meta.groupby("subject_id").indices.items():
                idx_arr = np.asarray(idx, dtype=int)
                shuffled[idx_arr, target_idx] = values[idx_arr][rng.permutation(len(idx_arr))]
        elif mode == "dateblock":
            for _, idx in meta.groupby("dateblock_group").indices.items():
                idx_arr = np.asarray(idx, dtype=int)
                shuffled[idx_arr, target_idx] = values[idx_arr][rng.permutation(len(idx_arr))]
        else:
            raise ValueError(mode)

    out = base.copy()
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    out[TARGETS] = clip_prob(sigmoid(base_logits + shuffled))
    stem = source_path.stem.replace("submission_", "")[:75]
    path = NULL_DIR / f"submission_e282null_{stem}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def generate_nulls(candidate_paths: list[Path], state: pd.DataFrame) -> pd.DataFrame:
    NULL_DIR.mkdir(exist_ok=True)
    base = load_sub(CURRENT)
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    meta = test_meta(state, base[KEYS])
    rows: list[dict[str, object]] = []
    for cand_idx, path in enumerate(candidate_paths):
        candidate = load_sub(path, base[KEYS])
        delta = logit(candidate[TARGETS].to_numpy(dtype=np.float64)) - base_logits
        if np.max(np.abs(delta)) < 1.0e-12:
            continue
        for mode in ["row", "subject", "dateblock"]:
            for rep in range(N_REPS):
                seed = RNG_SEED + cand_idx * 1009 + rep * 97 + {"row": 0, "subject": 1, "dateblock": 2}[mode]
                null_path = write_null_candidate(base, delta, meta, path, mode, rep, seed)
                rows.append(
                    {
                        "source_path": rel(path),
                        "source_basename": path.name,
                        "null_path": rel(null_path),
                        "null_basename": null_path.name,
                        "mode": mode,
                        "rep": rep,
                        "seed": seed,
                    }
                )
    nulls = pd.DataFrame(rows)
    nulls.to_csv(NULLS_OUT, index=False)
    return nulls


def feature_rows(paths: list[Path], sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for path in paths:
        key = rel(path)
        if key in seen:
            continue
        seen.add(key)
        row = feature_row(path, sample, refs, ref_vecs)
        row["file"] = key
        row["source_path"] = key
        row["basename"] = path.name
        rows.append(row)
    return pd.DataFrame(rows)


def score_with_nulls(candidates: pd.DataFrame, nulls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sample = load_sub(CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    current_path = OUT / CURRENT
    candidate_paths = [OUT / row["basename"] for row in candidates.to_dict("records")]
    null_paths = [ROOT / row["null_path"] for row in nulls.to_dict("records")]
    all_features = feature_rows([current_path] + candidate_paths + null_paths, sample, refs, ref_vecs)
    model_df = evaluate_models(known)
    scores = score_candidates(known, all_features, model_df)
    scores.to_csv(SCORES_OUT, index=False)
    return scores, model_df, selected_models(model_df)


def summarize(
    scores: pd.DataFrame,
    candidates: pd.DataFrame,
    nulls: pd.DataFrame,
    direction: pd.DataFrame,
    diagnostics: pd.DataFrame,
) -> pd.DataFrame:
    actual = scores.merge(candidates[["basename", "source_path", "scope", "targets", "shape", "amp"]], on=["basename", "source_path"], how="inner")
    null_scores = scores.merge(nulls, left_on="source_path", right_on="null_path", how="inner")
    story_gate_both = bool((diagnostics["state_oof_r2"] > 0.10).all())
    support_map = direction.set_index("target")["supported_for_materialization"].to_dict()

    rows: list[dict[str, object]] = []
    for _, rec in actual.iterrows():
        matched = null_scores[null_scores["source_basename"].eq(rec["basename"])].copy()
        actual_p90 = float(rec["pred_delta_vs_current_p90"])
        actual_mean = float(rec["pred_delta_vs_current_mean"])
        target_list = str(rec["targets"]).split(",")
        target_support_gate = bool(all(bool(support_map.get(target, False)) for target in target_list))
        if matched.empty:
            p90_dom = mean_dom = worst_mode_dom = null_strict_rate = np.nan
            mode_fields: dict[str, object] = {}
            matched_placebo_gate = False
            final_decision = "blocked_missing_matched_nulls"
        else:
            null_p90 = matched["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            null_mean = matched["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
            strict_null = matched["strict_promote_gate"].astype(bool).to_numpy()
            p90_dom = float(np.mean(actual_p90 < null_p90))
            mean_dom = float(np.mean(actual_mean < null_mean))
            null_strict_rate = float(np.mean(strict_null))
            mode_fields = {
                "null_p90_q20": float(np.quantile(null_p90, 0.20)),
                "null_p90_median": float(np.median(null_p90)),
                "null_p90_best": float(np.min(null_p90)),
            }
            mode_doms = []
            for mode, group in matched.groupby("mode"):
                g_p90 = group["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
                dom = float(np.mean(actual_p90 < g_p90))
                mode_doms.append(dom)
                mode_fields[f"{mode}_p90_dominance"] = dom
                mode_fields[f"{mode}_null_strict_rate"] = float(group["strict_promote_gate"].astype(bool).mean())
                mode_fields[f"{mode}_best_null_p90"] = float(np.min(g_p90))
            worst_mode_dom = float(min(mode_doms)) if mode_doms else 0.0
            matched_placebo_gate = bool(
                bool(rec["strict_promote_gate"])
                and p90_dom >= 0.85
                and mean_dom >= 0.75
                and worst_mode_dom >= 0.65
                and null_strict_rate <= 0.10
                and actual_p90 <= mode_fields["null_p90_q20"] - 1.0e-6
            )

        if not target_support_gate:
            final_decision = "blocked_by_train_target_support"
        elif not story_gate_both:
            final_decision = "blocked_by_story_state_transfer"
        elif not bool(rec["strict_promote_gate"]):
            final_decision = str(rec["promotion_decision"])
        elif not matched_placebo_gate:
            final_decision = "blocked_by_matched_placebo"
        else:
            final_decision = "public_free_submission_candidate"

        rows.append(
            {
                "basename": rec["basename"],
                "source_path": rec["source_path"],
                "scope": rec["scope"],
                "targets": rec["targets"],
                "shape": rec["shape"],
                "amp": float(rec["amp"]),
                "old_promotion_decision": rec["promotion_decision"],
                "old_strict_promote": bool(rec["strict_promote_gate"]),
                "actual_mean": actual_mean,
                "actual_p10": float(rec["pred_delta_vs_current_p10"]),
                "actual_p90": actual_p90,
                "actual_beats_current_rate": float(rec["pred_beats_current_rate"]),
                "incremental_bad_axis_vs_current": float(rec["incremental_bad_axis_vs_current"]),
                "null_count": int(len(matched)),
                "null_strict_rate": null_strict_rate,
                "p90_dominance": p90_dom,
                "mean_dominance": mean_dom,
                "worst_mode_p90_dominance": worst_mode_dom,
                "matched_placebo_gate": matched_placebo_gate,
                "story_gate_both": story_gate_both,
                "target_support_gate": target_support_gate,
                "public_free_submission_ready": bool(final_decision == "public_free_submission_candidate"),
                "final_decision": final_decision,
                **mode_fields,
            }
        )
    summary = pd.DataFrame(rows).sort_values(
        ["public_free_submission_ready", "matched_placebo_gate", "old_strict_promote", "actual_p90", "p90_dominance"],
        ascending=[False, False, False, True, False],
    )
    summary.to_csv(SUMMARY_OUT, index=False)
    return summary


def write_report(
    summary: pd.DataFrame,
    candidates: pd.DataFrame,
    direction: pd.DataFrame,
    diagnostics: pd.DataFrame,
    selected: pd.DataFrame,
) -> None:
    ready = summary[summary["public_free_submission_ready"].astype(bool)] if not summary.empty else pd.DataFrame()
    best = summary.iloc[0] if not summary.empty else None
    lines = [
        "# E282 App-Entropy Story-State Materializer",
        "",
        "## Question",
        "",
        "Can the E281 surviving human/social story become a submission-grade edit without spending public LB?",
        "",
        "## Human/Social Worldview",
        "",
        "`app_entropy_scattered_day` is interpreted as a routine-break / attention-fragmentation state: many apps across the day, less single-routine anchoring, and likely noisier sleep-quality self-report. The JEPA-style part is target-free: other context families predict this hidden story-state, and only then do we test whether that state deserves tiny Q3/Q2/S2 logit edits.",
        "",
        "## State Diagnostics",
        "",
        md_table(diagnostics, n=10),
        "",
        "## Target Direction",
        "",
        md_table(
            direction[
                [
                    "target",
                    "logistic_coef_state_avg_z",
                    "label_rate_high_minus_low",
                    "e281_mean_delta",
                    "e281_best_delta",
                    "support_strength",
                    "target_weight",
                    "supported_for_materialization",
                ]
            ],
            n=10,
        ),
        "",
        "## Candidate Movement",
        "",
        md_table(candidates, n=30),
        "",
        "## Public-Free Governor",
        "",
        f"- selected public-anchor selector models: `{len(selected)}`",
        f"- candidates audited: `{len(summary)}`",
        f"- submission-ready candidates: `{len(ready)}`",
        "",
        md_table(
            summary[
                [
                    "basename",
                    "final_decision",
                    "old_promotion_decision",
                    "actual_mean",
                    "actual_p90",
                    "actual_beats_current_rate",
                    "null_strict_rate",
                    "p90_dominance",
                    "worst_mode_p90_dominance",
                    "matched_placebo_gate",
                ]
            ],
            n=40,
        )
        if not summary.empty
        else "_empty_",
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        top = ready.iloc[0]
        lines.append(
            f"Local governor found a submission-grade candidate: `{top['basename']}`. It bets that app-entropy hidden state is row-aligned in test, not just a generic direction/magnitude tweak."
        )
    elif best is not None:
        lines.append(
            f"No E282 app-entropy candidate is submission-ready. Best local row is `{best['basename']}` with decision `{best['final_decision']}`. Keep the story-state hypothesis alive, but do not spend a public LB slot on these materializations."
        )
    else:
        lines.append("No candidate was generated; the target-support gate blocked materialization.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{STATE_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{NULLS_OUT.name}`",
            f"- `{SCORES_OUT.name}`",
            f"- `{SUMMARY_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    state, diagnostics, base = build_story_state()
    direction = target_direction_table(state, base)
    state.to_csv(STATE_OUT, index=False)
    direction.to_csv(OUT / "e282_appentropy_story_materializer_target_direction.csv", index=False)

    candidates = write_candidate_submissions(state, base, direction)
    candidate_paths = [OUT / row["basename"] for row in candidates.to_dict("records")]
    nulls = generate_nulls(candidate_paths, state) if len(candidates) else pd.DataFrame()
    scores, _, selected = score_with_nulls(candidates, nulls) if len(candidates) else (pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
    summary = summarize(scores, candidates, nulls, direction, diagnostics) if len(candidates) else pd.DataFrame()
    write_report(summary, candidates, direction, diagnostics, selected)

    print(f"story={STORY_ID}")
    print(f"candidates={len(candidates)}")
    print(f"nulls={len(nulls)}")
    print(f"ready={int(summary['public_free_submission_ready'].sum()) if not summary.empty else 0}")
    if not summary.empty:
        cols = [
            "basename",
            "final_decision",
            "old_promotion_decision",
            "actual_mean",
            "actual_p90",
            "null_strict_rate",
            "p90_dominance",
            "matched_placebo_gate",
        ]
        print(summary[cols].head(20).round(9).to_string(index=False))
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
