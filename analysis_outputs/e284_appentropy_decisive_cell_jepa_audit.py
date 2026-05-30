#!/usr/bin/env python3
"""E284: app-entropy as context inside decisive-cell JEPA target.

E281/E282 established `app_entropy_scattered_day` as a real human/social
story-state, while E283 rejected scalar app-entropy rules for Q3 smoothing
cell selection. This experiment changes the target:

    context + app-entropy state -> decisive Q3/S4 cell-tail representation

Rather than sorting Q3 cells by app-entropy, app-entropy becomes a context
coordinate in the E237/E249 cell-level bad-tail predictor. A candidate is only
considered submission-grade if it survives:

1. OOF decisive-cell stress.
2. E237 materialization stress against E224/E154/E95.
3. E247-current matched row/subject/dateblock placebo governance.

No public LB is used.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e284_appentropy_decisive_cell_jepa_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e230_e224_support_tail_prune_audit as e230  # noqa: E402
import e237_cell_decisive_jepa_target as e237  # noqa: E402
import e249_feature_nn1_decisive_oof_audit as e249  # noqa: E402
import e282_appentropy_story_materializer as e282  # noqa: E402
import e246_feature_nn1_smoothing_selector_ablation as e246  # noqa: E402
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


RNG_SEED = 20260531 + 284
N_REPS = 9

OOF_OUT = OUT / "e284_appentropy_decisive_cell_jepa_oof_scan.csv"
PAIR_OUT = OUT / "e284_appentropy_decisive_cell_jepa_pair_summary.csv"
MATERIAL_OUT = OUT / "e284_appentropy_decisive_cell_jepa_materialization_summary.csv"
TARGET_OUT = OUT / "e284_appentropy_decisive_cell_jepa_target_summary.csv"
SELECTED_OUT = OUT / "e284_appentropy_decisive_cell_jepa_selected_summary.csv"
OVERLAP_OUT = OUT / "e284_appentropy_decisive_cell_jepa_overlap_summary.csv"
NULLS_OUT = OUT / "e284_appentropy_decisive_cell_jepa_nulls.csv"
SCORES_OUT = OUT / "e284_appentropy_decisive_cell_jepa_scores.csv"
GOVERNOR_OUT = OUT / "e284_appentropy_decisive_cell_jepa_governor_summary.csv"
REPORT_OUT = OUT / "e284_appentropy_decisive_cell_jepa_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(df: pd.DataFrame) -> str:
    arr = np.asarray(df[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def normalize_keys(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    out["subject_id"] = out["subject_id"].astype(str)
    return out.reset_index(drop=True)


def ensure_app_state() -> pd.DataFrame:
    if e282.STATE_OUT.exists():
        return pd.read_csv(e282.STATE_OUT)
    state, _, _ = e282.build_story_state()
    state.to_csv(e282.STATE_OUT, index=False)
    return state


def row_state_table(train_raw: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    state = ensure_app_state().copy()
    for col in ["sleep_date", "lifelog_date"]:
        state[col] = pd.to_datetime(state[col]).dt.strftime("%Y-%m-%d")
    state["subject_id"] = state["subject_id"].astype(str)

    train_meta = train_raw[KEYS].copy().reset_index().rename(columns={"index": "row_idx"})
    train_meta = train_meta.rename_axis(None, axis=1)
    train_meta["row_idx"] = np.arange(len(train_meta), dtype=int)
    for col in ["sleep_date", "lifelog_date"]:
        train_meta[col] = pd.to_datetime(train_meta[col]).dt.strftime("%Y-%m-%d")
    train_meta["subject_id"] = train_meta["subject_id"].astype(str)

    test_meta = sample[KEYS].copy().reset_index(drop=True)
    test_meta["row_idx"] = np.arange(len(test_meta), dtype=int)
    for col in ["sleep_date", "lifelog_date"]:
        test_meta[col] = pd.to_datetime(test_meta[col]).dt.strftime("%Y-%m-%d")
    test_meta["subject_id"] = test_meta["subject_id"].astype(str)

    keep = [
        "subject_id",
        "sleep_date",
        "lifelog_date",
        "dateblock_group",
        "story_score_actual",
        "state_subject_z",
        "state_dateblock_z",
        "state_avg_z",
    ]
    train_state = train_meta.merge(state[state["split"].eq("train")][keep], on=KEYS, how="left")
    test_state = test_meta.merge(state[state["split"].eq("test")][keep], on=KEYS, how="left")
    required = ["story_score_actual", "state_subject_z", "state_dateblock_z", "state_avg_z"]
    if train_state[required].isna().any().any() or test_state[required].isna().any().any():
        raise RuntimeError("app-entropy state merge failed")
    return train_state, test_state


def zfit_apply(train_vals: np.ndarray, values: np.ndarray) -> np.ndarray:
    mu = float(np.mean(train_vals))
    sd = float(np.std(train_vals))
    if sd < 1.0e-9:
        sd = 1.0
    return (np.asarray(values, dtype=np.float64) - mu) / sd


def add_app_context(long_df: pd.DataFrame, row_state: pd.DataFrame, fit_state: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    out = long_df.copy()
    state_cols = ["story_score_actual", "state_subject_z", "state_dateblock_z", "state_avg_z"]
    state_by_row = row_state.set_index("row_idx")[state_cols]
    fit_by_row = fit_state.set_index("row_idx")[state_cols]

    app_cols: list[str] = []
    for col in state_cols:
        vals = state_by_row.loc[out["row_idx"].astype(int), col].to_numpy(dtype=np.float64)
        fit_vals = fit_by_row[col].to_numpy(dtype=np.float64)
        name = f"appentropy_{col}_zfit"
        out[name] = zfit_apply(fit_vals, vals)
        app_cols.append(name)

    inter_base = [
        "prob_gap",
        "logit_step",
        "abs_logit_step",
        "base_margin",
        "full_margin",
        "featnn1_total_smooth_gain",
        "featnn1_total_smooth_gain_mean",
        "featnn1_base_pair_abs_logit",
        "featnn1_full_pair_abs_logit",
        "featnn1_dist",
    ]
    inter_cols: list[str] = []
    for app_col in ["appentropy_state_avg_z_zfit", "appentropy_story_score_actual_zfit"]:
        for base_col in inter_base:
            if base_col not in out.columns:
                continue
            name = f"{app_col}_x_{base_col}"
            out[name] = out[app_col].astype(float).to_numpy() * out[base_col].astype(float).to_numpy()
            inter_cols.append(name)
    return out, app_cols, inter_cols


def build_app_augmented_frames() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]], pd.DataFrame]:
    train_aug, sub_aug, feats, _ = e249.build_augmented_frames()
    train_raw, _, _, _ = e237.build_frames()
    sample = load_sub(e237.A2C8).sort_values(KEYS).reset_index(drop=True)
    train_state, test_state = row_state_table(train_raw, sample)

    train_app, app_cols, inter_cols = add_app_context(train_aug, train_state, train_state)
    sub_app, sub_app_cols, sub_inter_cols = add_app_context(sub_aug, test_state, train_state)
    if app_cols != sub_app_cols or inter_cols != sub_inter_cols:
        raise RuntimeError("app context column mismatch")

    out_feats = dict(feats)
    base_view = "latent_no_targetid_featnn1"
    if base_view not in out_feats:
        raise RuntimeError(f"missing base view {base_view}")
    out_feats["latent_no_targetid_featnn1_appstate"] = list(dict.fromkeys([*out_feats[base_view], *app_cols[:3]]))
    out_feats["latent_no_targetid_featnn1_appstate_inter"] = list(
        dict.fromkeys([*out_feats[base_view], *app_cols[:3], *[c for c in inter_cols if "state_avg" in c]])
    )
    out_feats["latent_no_targetid_featnn1_appstory_inter"] = list(dict.fromkeys([*out_feats[base_view], *app_cols, *inter_cols]))
    view_info = pd.DataFrame(
        [
            {
                "view": view,
                "feature_count": len(cols),
                "app_feature_count": sum(col.startswith("appentropy_") for col in cols),
                "interaction_count": sum("_x_" in col for col in cols),
            }
            for view, cols in out_feats.items()
            if "app" in view
        ]
    )
    return train_app, sub_app, out_feats, view_info


def app_oof_scan(train_aug: pd.DataFrame, feats: dict[str, list[str]]) -> pd.DataFrame:
    train_df = train_aug[train_aug["task_name"].isin(e237.CONTROL_TASKS)].reset_index(drop=True)
    rows: list[dict[str, Any]] = []
    models = e237.model_defs()
    views = [
        "latent_no_targetid_featnn1_appstate",
        "latent_no_targetid_featnn1_appstate_inter",
        "latent_no_targetid_featnn1_appstory_inter",
    ]
    for source_scope in ["q3s4", "all3"]:
        for view in views:
            cols = feats[view]
            for model_name in ["hgb_shallow", "lr_l2_c0p10"]:
                model = models[model_name]
                for split in ["row5", "subject5"]:
                    for kind in ["risk", "contrast"]:
                        for q in [0.10, 0.20]:
                            spec = {
                                "source_scope": source_scope,
                                "view": view,
                                "model": model_name,
                                "split": split,
                                "target_kind": kind,
                                "tail_q": q,
                            }
                            bad_prob, eval_label, _ = e237.oof_bad_predict(model, train_df, cols, source_scope, split, kind, q)
                            for policy, amp in e237.policy_amplitudes(train_df, bad_prob).items():
                                rows.append(e237.evaluate_oof_policy(train_df, spec, bad_prob, eval_label, amp, policy))
    return pd.DataFrame(rows).sort_values(["stress_promote", "loss_vs_full"], ascending=[False, True])


def compare_to_e249(oof: pd.DataFrame) -> pd.DataFrame:
    base = pd.read_csv(e249.RAW_OUT)
    out = oof.copy()
    out["base_view"] = "latent_no_targetid_featnn1"
    joined = out.merge(
        base.rename(columns={"view": "base_view"}),
        on=["source_scope", "base_view", "model", "split", "target_kind", "tail_q", "policy"],
        how="inner",
        suffixes=("_app", "_base"),
    )
    joined["delta_loss_vs_full"] = joined["loss_vs_full_app"] - joined["loss_vs_full_base"]
    joined["delta_tail_auc"] = joined["tail_auc_app"] - joined["tail_auc_base"]
    joined["promoted_by_app"] = joined["stress_promote_app"].astype(bool) & ~joined["stress_promote_base"].astype(bool)
    joined["demoted_by_app"] = ~joined["stress_promote_app"].astype(bool) & joined["stress_promote_base"].astype(bool)
    summary = (
        joined.groupby(["view", "model"], dropna=False)
        .agg(
            pairs=("policy", "count"),
            mean_delta_loss=("delta_loss_vs_full", "mean"),
            median_delta_loss=("delta_loss_vs_full", "median"),
            p10_delta_loss=("delta_loss_vs_full", lambda x: float(np.quantile(x, 0.10))),
            mean_delta_tail_auc=("delta_tail_auc", "mean"),
            median_delta_tail_auc=("delta_tail_auc", "median"),
            promoted_by_app=("promoted_by_app", "sum"),
            demoted_by_app=("demoted_by_app", "sum"),
            app_better_loss_rate=("delta_loss_vs_full", lambda x: float((x < 0.0).mean())),
            app_better_tail_auc_rate=("delta_tail_auc", lambda x: float((x > 0.0).mean())),
        )
        .reset_index()
        .sort_values(["median_delta_loss", "median_delta_tail_auc"], ascending=[True, False])
    )
    summary.to_csv(PAIR_OUT, index=False)
    return summary


def rename_selected(selected: pd.DataFrame) -> pd.DataFrame:
    out = selected.copy()
    if out.empty:
        return out
    for idx, row in out.iterrows():
        old_name = str(row.get("submission_file", ""))
        old_path = OUT / old_name
        if not old_name or not old_path.exists():
            continue
        sub = pd.read_csv(old_path)
        pred = clip_prob(sub[TARGETS].to_numpy(dtype=np.float64))
        digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
        safe_id = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(row["candidate_id"]))[:82]
        new_name = f"submission_e284_appentropy_decisive_{safe_id}_{digest}.csv"
        new_path = OUT / new_name
        final = sub[KEYS].copy()
        final[TARGETS] = pred
        final.to_csv(new_path, index=False)
        out.loc[idx, "submission_file"] = new_name
        out.loc[idx, "source_path"] = rel(new_path)
        out.loc[idx, "basename"] = new_name
    return out


def decisive_overlap_summary(selected: pd.DataFrame) -> pd.DataFrame:
    if selected.empty:
        out = pd.DataFrame()
        out.to_csv(OVERLAP_OUT, index=False)
        return out
    if not e246.SUMMARY_OUT.exists():
        rows = e246.build_selector_rows()
        local_summary, target_df, overlap = e246.audit_specs(rows, e246.selector_specs(rows))
        local_summary.to_csv(e246.SUMMARY_OUT, index=False)
        target_df.to_csv(e246.TARGET_OUT, index=False)
        overlap.to_csv(e246.OVERLAP_OUT, index=False)
        rows.to_csv(e246.SELECTOR_OUT, index=False)
    selector_summary = pd.read_csv(e246.SUMMARY_OUT)
    e247 = set(map(int, str(selector_summary.loc[selector_summary["candidate_id"].eq("nn_smooth_sum_top34"), "row_idx_list"].iloc[0]).split()))
    e256 = set(map(int, str(selector_summary.loc[selector_summary["candidate_id"].eq("top50_amp_then_smooth25"), "row_idx_list"].iloc[0]).split()))
    sample = load_sub(e230.E224_FILE).sort_values(KEYS).reset_index(drop=True)
    e224 = load_sub(e230.E224_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    e154 = load_sub(e230.E154_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    q3_idx = TARGETS.index("Q3")
    rows: list[dict[str, object]] = []
    for _, rec in selected.drop_duplicates("submission_file").iterrows():
        path = OUT / str(rec["submission_file"])
        candidate = load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
        dist_to_e154 = np.abs(candidate[:, q3_idx] - e154[:, q3_idx])
        dist_to_e224 = np.abs(candidate[:, q3_idx] - e224[:, q3_idx])
        dropped = set(np.where((dist_to_e154 < 1.0e-9) & (dist_to_e224 > 1.0e-9))[0].astype(int).tolist())
        rows.append(
            {
                "candidate_id": rec["candidate_id"],
                "submission_file": rec["submission_file"],
                "q3_dropped": len(dropped),
                "e247_overlap": len(dropped & e247),
                "e247_jaccard": float(len(dropped & e247) / max(len(dropped | e247), 1)),
                "e256_overlap": len(dropped & e256),
                "e256_jaccard": float(len(dropped & e256) / max(len(dropped | e256), 1)),
                "e247_missing": len(e247 - dropped),
                "extra_vs_e247": len(dropped - e247),
            }
        )
    out = pd.DataFrame(rows).sort_values(["e247_jaccard", "e247_overlap"], ascending=[False, False])
    out.to_csv(OVERLAP_OUT, index=False)
    return out


def write_null_candidate(base: pd.DataFrame, delta: np.ndarray, meta: pd.DataFrame, source_path: Path, mode: str, rep: int, seed: int) -> Path:
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
    out[TARGETS] = clip_prob(sigmoid(logit(base[TARGETS].to_numpy(dtype=np.float64)) + shuffled))
    stem = source_path.stem.replace("submission_", "")[:78]
    path = NULL_DIR / f"submission_e284null_{stem}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def test_meta(base: pd.DataFrame) -> pd.DataFrame:
    state = ensure_app_state().copy()
    meta = state[state["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    if not normalize_keys(meta).equals(normalize_keys(base)):
        raise RuntimeError("test metadata does not align with current base")
    out = meta[KEYS + ["dateblock_group"]].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col])
    return out


def generate_nulls(selected: pd.DataFrame) -> pd.DataFrame:
    NULL_DIR.mkdir(exist_ok=True)
    if selected.empty:
        nulls = pd.DataFrame()
        nulls.to_csv(NULLS_OUT, index=False)
        return nulls
    base = load_sub(CURRENT).sort_values(KEYS).reset_index(drop=True)
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    meta = test_meta(base[KEYS])
    rows: list[dict[str, object]] = []
    unique = selected.drop_duplicates("submission_file").reset_index(drop=True)
    for cand_idx, rec in unique.iterrows():
        path = OUT / str(rec["submission_file"])
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


def score_current_anchor(selected: pd.DataFrame, nulls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if selected.empty:
        scores = pd.DataFrame()
        scores.to_csv(SCORES_OUT, index=False)
        return scores, pd.DataFrame()
    sample = load_sub(CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    paths = [OUT / CURRENT]
    paths.extend(OUT / str(path) for path in selected.drop_duplicates("submission_file")["submission_file"].tolist())
    if not nulls.empty:
        paths.extend(ROOT / str(path) for path in nulls["null_path"].tolist())
    feats = feature_rows(paths, sample, refs, ref_vecs)
    model_df = evaluate_models(known)
    scores = score_candidates(known, feats, model_df)
    scores.to_csv(SCORES_OUT, index=False)
    return scores, selected_models(model_df)


def summarize_governor(selected: pd.DataFrame, nulls: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    if selected.empty or scores.empty:
        out = pd.DataFrame()
        out.to_csv(GOVERNOR_OUT, index=False)
        return out
    cand_meta = selected.drop_duplicates("submission_file").copy()
    cand_meta["basename"] = cand_meta["submission_file"]
    cand_meta["source_path"] = cand_meta["source_path"].fillna(cand_meta["submission_file"].map(lambda x: rel(OUT / str(x))))
    actual = scores.merge(cand_meta, on=["basename", "source_path"], how="inner")
    null_scores = scores.merge(nulls, left_on="source_path", right_on="null_path", how="inner") if not nulls.empty else pd.DataFrame()
    public_map = known_public_table().set_index("file")["public_lb"].to_dict()
    rows: list[dict[str, object]] = []
    for _, rec in actual.iterrows():
        matched = null_scores[null_scores["source_basename"].eq(rec["basename"])].copy() if not null_scores.empty else pd.DataFrame()
        actual_p90 = float(rec["pred_delta_vs_current_p90"])
        actual_mean = float(rec["pred_delta_vs_current_mean"])
        if matched.empty:
            p90_dom = mean_dom = worst_mode_dom = null_strict_rate = np.nan
            mode_fields: dict[str, object] = {}
            placebo_gate = False
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
            worst_mode_dom = float(min(mode_doms)) if mode_doms else 0.0
            placebo_gate = bool(
                bool(rec["strict_promote_gate"])
                and p90_dom >= 0.85
                and mean_dom >= 0.75
                and worst_mode_dom >= 0.65
                and null_strict_rate <= 0.10
                and actual_p90 <= mode_fields["null_p90_q20"] - 1.0e-6
            )
        public_lb = public_map.get(str(rec["basename"]), np.nan)
        known_public_worse = bool(pd.notna(public_lb) and public_lb >= public_map.get(CURRENT, np.inf))
        if known_public_worse:
            final_decision = "blocked_known_public_worse"
        elif not bool(rec["strict_promote_gate"]):
            final_decision = str(rec["promotion_decision"])
        elif not placebo_gate:
            final_decision = "blocked_by_matched_placebo"
        else:
            final_decision = "public_free_submission_candidate"
        rows.append(
            {
                "basename": rec["basename"],
                "source_path": rec["source_path"],
                "candidate_id": rec["candidate_id"],
                "view": rec["view"],
                "model": rec["model"],
                "split": rec["split"],
                "target_kind": rec["target_kind"],
                "tail_q": float(rec["tail_q"]),
                "policy": rec["policy"],
                "q3_dropped_cells": int(rec["q3_dropped_cells"]),
                "s4_dropped_cells": int(rec["s4_dropped_cells"]),
                "e237_score": float(rec["e237_score"]),
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
                "matched_placebo_gate": placebo_gate,
                "public_lb_if_known": public_lb,
                "known_public_worse_than_current": known_public_worse,
                "public_free_submission_ready": bool(final_decision == "public_free_submission_candidate"),
                "final_decision": final_decision,
                **mode_fields,
            }
        )
    out = pd.DataFrame(rows).sort_values(
        ["public_free_submission_ready", "matched_placebo_gate", "old_strict_promote", "actual_p90", "p90_dominance"],
        ascending=[False, False, False, True, False],
    )
    out.to_csv(GOVERNOR_OUT, index=False)
    return out


def write_report(
    oof: pd.DataFrame,
    pair: pd.DataFrame,
    view_info: pd.DataFrame,
    material: pd.DataFrame,
    selected: pd.DataFrame,
    overlap: pd.DataFrame,
    governor: pd.DataFrame,
    selected_models_df: pd.DataFrame,
) -> None:
    promoted = oof[oof["stress_promote"].astype(bool)].sort_values("loss_vs_full")
    best_oof = oof.sort_values("loss_vs_full").head(25)
    graft = material[material["pair_kind"].eq("graft_vs_e154")].copy() if not material.empty else pd.DataFrame()
    gate = graft[graft["e237_gate"].astype(bool)].sort_values("e237_score", ascending=False) if not graft.empty else pd.DataFrame()
    ready = governor[governor["public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    oof_cols = [
        "source_scope",
        "view",
        "model",
        "split",
        "target_kind",
        "tail_q",
        "policy",
        "tail_auc",
        "loss_vs_full",
        "subject_win_rate",
        "dropped_cells",
        "dropped_q3",
        "dropped_s4",
        "stress_promote",
    ]
    material_cols = [
        "candidate_id",
        "view",
        "model",
        "split",
        "target_kind",
        "tail_q",
        "policy",
        "q3_dropped_cells",
        "s4_dropped_cells",
        "oof_loss_vs_full",
        "oof_tail_auc",
        "expected_loss_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "actual_expected_delta_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "actual_support_gain_vs_e224",
        "q3_top1_over_abs_expected",
        "e237_gate",
        "e237_score",
        "submission_file",
    ]
    governor_cols = [
        "basename",
        "candidate_id",
        "final_decision",
        "old_promotion_decision",
        "actual_mean",
        "actual_p90",
        "null_strict_rate",
        "p90_dominance",
        "worst_mode_p90_dominance",
        "matched_placebo_gate",
    ]
    lines = [
        "# E284 App-Entropy Decisive-Cell JEPA Audit",
        "",
        "## Question",
        "",
        "Can the validated app-entropy human/social state help learn the hidden Q3/S4 decisive-cell target, rather than directly moving Q3 or re-ranking E247 smoothing cells?",
        "",
        "## Feature Views",
        "",
        md_table(view_info, n=10),
        "",
        "## OOF Comparison Versus E249 Feature-NN1 Baseline",
        "",
        md_table(pair, n=20),
        "",
        "## OOF Promoted Policies",
        "",
        f"- OOF rows: `{len(oof)}`",
        f"- OOF stress-promoted rows: `{int(oof['stress_promote'].sum()) if not oof.empty else 0}`",
        "",
        md_table(promoted, oof_cols, n=30),
        "",
        "## Best OOF Rows",
        "",
        md_table(best_oof, oof_cols, n=25),
        "",
        "## E237 Materialization Stress",
        "",
        f"- graft rows: `{len(graft)}`",
        f"- E237 gate passes: `{len(gate)}`",
        f"- selected files: `{selected['submission_file'].nunique() if not selected.empty else 0}`",
        "",
        md_table(gate, material_cols, n=30),
        "",
        "## Selected Q3 Cell Overlap With E247",
        "",
        md_table(overlap, n=20),
        "",
        "## E247 Current-Anchor Matched Placebo Governor",
        "",
        f"- selected current-anchor models: `{len(selected_models_df)}`",
        f"- public-free ready files: `{len(ready)}`",
        "",
        md_table(governor, governor_cols, n=30) if not governor.empty else "_empty_",
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        top = ready.iloc[0]
        lines.append(
            f"`{top['basename']}` survived the local governor. It is a candidate for manual review because app-entropy helped a decisive-cell target produce E247-relative placebo-resistant movement."
        )
    elif len(gate):
        lines.append(
            "App-entropy context can produce E237-gated decisive-cell files, but none survived the E247-current matched-placebo governor. Do not submit E284 files."
        )
    elif int(oof["stress_promote"].sum()) if not oof.empty else 0:
        lines.append(
            "App-entropy context produces OOF-promoted policies, but they do not survive E237 materialization stress. Keep app-entropy as diagnostic context, not a submitted cell target yet."
        )
    else:
        lines.append(
            "App-entropy context does not improve the decisive-cell JEPA target under this setup. This branch is blocked until the target or context definition changes."
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{OOF_OUT.name}`",
            f"- `{PAIR_OUT.name}`",
            f"- `{MATERIAL_OUT.name}`",
            f"- `{TARGET_OUT.name}`",
            f"- `{SELECTED_OUT.name}`",
            f"- `{OVERLAP_OUT.name}`",
            f"- `{GOVERNOR_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    train_app, sub_app, feats, view_info = build_app_augmented_frames()
    train_df = train_app[train_app["task_name"].isin(e237.CONTROL_TASKS)].reset_index(drop=True)
    sub_df = sub_app[sub_app["task_name"].isin(e237.ACTIVE_TASKS)].reset_index(drop=True)
    oof = app_oof_scan(train_app, feats)
    oof.to_csv(OOF_OUT, index=False)
    pair = compare_to_e249(oof)
    material, targets, selected = e237.scan_materializations(oof, train_df, sub_df, feats)
    selected = rename_selected(selected)
    overlap = decisive_overlap_summary(selected)
    material.to_csv(MATERIAL_OUT, index=False)
    targets.to_csv(TARGET_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    nulls = generate_nulls(selected)
    scores, selected_models_df = score_current_anchor(selected, nulls)
    governor = summarize_governor(selected, nulls, scores)
    write_report(oof, pair, view_info, material, selected, overlap, governor, selected_models_df)

    print(f"oof_rows={len(oof)}")
    print(f"oof_promoted={int(oof['stress_promote'].sum()) if len(oof) else 0}")
    graft = material[material["pair_kind"].eq("graft_vs_e154")] if not material.empty else pd.DataFrame()
    print(f"e237_gate={int(graft['e237_gate'].sum()) if not graft.empty else 0}")
    print(f"selected_files={selected['submission_file'].nunique() if not selected.empty else 0}")
    print(f"ready={int(governor['public_free_submission_ready'].sum()) if not governor.empty else 0}")
    if not governor.empty:
        cols = [
            "basename",
            "final_decision",
            "old_promotion_decision",
            "actual_p90",
            "null_strict_rate",
            "p90_dominance",
            "matched_placebo_gate",
        ]
        print(governor[cols].head(12).round(9).to_string(index=False))
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
