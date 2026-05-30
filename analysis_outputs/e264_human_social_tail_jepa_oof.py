#!/usr/bin/env python3
"""E264: human/social lifestyle JEPA context for Q3/S4 tail-risk.

E262 translated raw lifelog into human-day states. E263 showed that the E256
public miss cells may sit on a different lifestyle state than the E247/E256
common Q3 core. This script asks the falsifiable OOF question:

Can human/social diary context predict held-out Q3/S4 harmful tail cells under
subject/date-block stress?

No submission is created. This is a representation-health test.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import GroupKFold


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, load_sub  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e237_cell_decisive_jepa_target as e237  # noqa: E402


RNG = 20260531 + 264
HUMAN_PATH = OUT / "e262_human_social_day_features.parquet"

SCAN_OUT = OUT / "e264_human_social_tail_jepa_oof_scan.csv"
VIEW_SUMMARY_OUT = OUT / "e264_human_social_tail_jepa_view_summary.csv"
PAIR_OUT = OUT / "e264_human_social_tail_jepa_pair_delta.csv"
FEATURES_OUT = OUT / "e264_human_social_tail_jepa_feature_sets.csv"
REPORT_OUT = OUT / "e264_human_social_tail_jepa_report.md"


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return e237.clip_prob(x)


def fit_predict(model: Any, x_train: pd.DataFrame, y_train: np.ndarray, x_pred: pd.DataFrame) -> np.ndarray:
    yy = np.asarray(y_train, dtype=int)
    if len(yy) == 0:
        return np.full(len(x_pred), 0.5, dtype=np.float64)
    if len(np.unique(yy)) < 2:
        return np.full(len(x_pred), float(np.mean(yy)), dtype=np.float64)
    fitted = clone(model)
    fitted.fit(x_train, yy)
    return clip_prob(fitted.predict_proba(x_pred)[:, 1])


def build_row_keys(train_raw: pd.DataFrame) -> pd.DataFrame:
    out = train_raw[KEYS].copy().reset_index(drop=True)
    out["row_idx"] = np.arange(len(out), dtype=int)
    out["subject_order"] = out.groupby("subject_id").cumcount().astype(int)
    out["dateblock_group"] = out["subject_id"].astype(str) + "_b" + (out["subject_order"] // 7).astype(str)
    return out


def load_human_features(train_raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    human = pd.read_parquet(HUMAN_PATH).copy()
    human["lifelog_date"] = pd.to_datetime(human["lifelog_date"]).dt.strftime("%Y-%m-%d")
    train_raw = train_raw.copy()
    train_raw["lifelog_date"] = pd.to_datetime(train_raw["lifelog_date"]).dt.strftime("%Y-%m-%d")
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    sample["lifelog_date"] = pd.to_datetime(sample["lifelog_date"]).dt.strftime("%Y-%m-%d")

    train_h = human[human["split"].eq("train")].copy()
    test_h = human[human["split"].eq("test")].copy()

    train_keys = build_row_keys(train_raw)
    train_join = train_keys.merge(train_h, on=KEYS, how="left", validate="one_to_one")
    if train_join["split"].isna().any():
        raise RuntimeError("missing E262 human train rows after key merge")

    sample_keys = sample[KEYS].copy()
    sample_keys["row_idx"] = np.arange(len(sample_keys), dtype=int)
    sub_join = sample_keys.merge(test_h, on=KEYS, how="left", validate="one_to_one")
    if sub_join["split"].isna().any():
        raise RuntimeError("missing E262 human test rows after key merge")
    return train_join, sub_join


def select_human_sets(human_cols: list[str]) -> dict[str, list[str]]:
    exclude_suffix = "_subj_z"
    cols = [c for c in human_cols if not c.endswith(exclude_suffix)]
    core = [
        c
        for c in cols
        if c in {"weekday", "is_weekend"}
        or c.startswith("human_")
    ]
    late_tokens = (
        "usage_late_",
        "usage_presleep_",
        "usage_deepnight_",
        "screen_m_screen_use_mean_late",
        "screen_m_screen_use_mean_presleep",
        "charge_m_charging_mean_presleep",
        "charge_m_charging_mean_late",
        "gps_speed_mean_deepnight",
        "gps_speed_mean_evening",
        "gps_speed_mean_presleep",
        "pedo_step_sum_presleep",
        "hr_heart_rate_mean_mean_day",
        "hr_heart_rate_max_mean_day",
        "light_m_light_mean_presleep",
        "wlight_light_mean_presleep",
        "ambience_music_late",
        "ambience_music_evening",
        "ambience_speech_morning",
        "ambience_inside_public_afternoon",
    )
    late = [c for c in cols if c.startswith(late_tokens) or c in core]

    semantic_prefix = (
        "usage_",
        "screen_",
        "charge_",
        "gps_",
        "wifi_",
        "ble_",
        "pedo_",
        "hr_",
        "light_",
        "wlight_",
        "ambience_",
        "activity_",
        "human_",
    )
    semantic = [c for c in cols if c in {"weekday", "is_weekend"} or c.startswith(semantic_prefix)]
    return {
        "human_core": list(dict.fromkeys(core)),
        "human_late": list(dict.fromkeys(late)),
        "human_all_semantic": list(dict.fromkeys(semantic)),
    }


def append_human_context(
    train_raw: pd.DataFrame,
    train_long: pd.DataFrame,
    sub_long: pd.DataFrame,
    base_feats: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    train_h, sub_h = load_human_features(train_raw)
    meta_cols = set(KEYS + ["sleep_date", "lifelog_date_only", "split", "Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"])
    human_cols = [
        c
        for c in train_h.columns
        if c not in meta_cols
        and c not in {"row_idx", "subject_order", "dateblock_group"}
        and pd.api.types.is_numeric_dtype(train_h[c])
    ]
    human_sets = select_human_sets(human_cols)

    row_cols = ["row_idx", "subject_order", "dateblock_group", *sorted(set().union(*human_sets.values()))]
    train_aug = train_long.merge(train_h[row_cols], on="row_idx", how="left", validate="many_to_one")
    sub_aug = sub_long.merge(sub_h[["row_idx", *sorted(set().union(*human_sets.values()))]], on="row_idx", how="left", validate="many_to_one")
    train_aug["dateblock_group"] = train_aug["dateblock_group"].astype(str)

    if train_aug[sorted(set().union(*human_sets.values()))].isna().all(axis=1).any():
        raise RuntimeError("human features failed to join onto train_long")
    if sub_aug[sorted(set().union(*human_sets.values()))].isna().all(axis=1).any():
        raise RuntimeError("human features failed to join onto sub_long")

    feats: dict[str, list[str]] = dict(base_feats)
    feats.update(human_sets)
    feats["movement_human_late"] = list(dict.fromkeys([*base_feats["movement"], *human_sets["human_late"]]))
    feats["latent_human_late"] = list(dict.fromkeys([*base_feats["latent_no_targetid"], *human_sets["human_late"]]))
    feats["latent_human_core"] = list(dict.fromkeys([*base_feats["latent_no_targetid"], *human_sets["human_core"]]))
    feat_rows = []
    for view, cols in feats.items():
        feat_rows.append({"view": view, "n_features": len(cols), "features": ",".join(cols)})
    pd.DataFrame(feat_rows).to_csv(FEATURES_OUT, index=False)
    return train_aug, sub_aug, feats


def fold_indices(df: pd.DataFrame, split: str):
    if split == "subject5":
        groups = df["subject_id"].astype(str).to_numpy()
    elif split == "row5":
        groups = df["row_idx"].astype(str).to_numpy()
    elif split == "dateblock5":
        groups = df["dateblock_group"].astype(str).to_numpy()
    else:
        raise ValueError(split)
    return GroupKFold(n_splits=min(5, len(np.unique(groups)))).split(df, groups=groups)


def oof_bad_predict_custom(
    model: Any,
    df: pd.DataFrame,
    cols: list[str],
    source_scope: str,
    split: str,
    kind: str,
    q: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    pred = np.full(len(df), np.nan, dtype=np.float64)
    eval_label = np.full(len(df), np.nan, dtype=np.float64)
    eval_mask = np.zeros(len(df), dtype=bool)
    active_all = e237.active_mask(df)
    for tr_idx, va_idx in fold_indices(df, split):
        tr_df = df.iloc[tr_idx].reset_index(drop=True)
        va_df = df.iloc[va_idx].reset_index(drop=True)
        thresholds = e237.thresholds_by_task(tr_df.loc[e237.source_mask(tr_df, source_scope)], q)
        tr_label, tr_eval = e237.label_with_thresholds(tr_df, thresholds, kind)
        va_label, va_eval = e237.label_with_thresholds(va_df, thresholds, kind)
        tr_source = e237.source_mask(tr_df, source_scope) & tr_eval
        if kind == "risk":
            tr_source = e237.source_mask(tr_df, source_scope)
        x_fit = tr_df.loc[tr_source, cols]
        y_fit = tr_label[tr_source]
        pred[va_idx] = fit_predict(model, x_fit, y_fit, va_df[cols])
        va_active = e237.active_mask(va_df) & va_eval
        eval_label[np.asarray(va_idx)[va_active]] = va_label[va_active].astype(float)
        eval_mask[np.asarray(va_idx)[va_active]] = True
    if np.isnan(pred[active_all]).any():
        raise RuntimeError(f"NaN OOF predictions for {source_scope} {split} {kind} q={q}")
    pred = np.where(np.isnan(pred), 0.5, pred)
    return clip_prob(pred), eval_label, eval_mask


def group_stats(df: pd.DataFrame, pred: np.ndarray, group_col: str) -> tuple[float, float]:
    active = e237.active_mask(df)
    active_df = df.loc[active].reset_index(drop=True)
    pred_active = pred[active]
    vals: list[float] = []
    for _, idx in active_df.groupby(group_col).groups.items():
        arr = np.asarray(list(idx), dtype=int)
        if len(arr) == 0:
            continue
        y = active_df.loc[arr, "true_label"].to_numpy(dtype=int)
        base = active_df.loc[arr, "base_prob"].to_numpy(dtype=np.float64)
        vals.append(float(e237.loss_vec(y, pred_active[arr]).mean() - e237.loss_vec(y, base).mean()))
    if not vals:
        return float("nan"), float("nan")
    vv = np.asarray(vals, dtype=np.float64)
    return float(vv.mean()), float(np.mean(vv < 0.0))


def evaluate_policy_with_blocks(
    df: pd.DataFrame,
    spec: dict[str, Any],
    bad_prob: np.ndarray,
    eval_label: np.ndarray,
    amp: np.ndarray,
    policy: str,
) -> dict[str, Any]:
    rec = e237.evaluate_oof_policy(df, spec, bad_prob, eval_label, amp, policy)
    pred = e237.predict_from_amp(df, amp)
    dateblock_delta, dateblock_win = group_stats(df, pred, "dateblock_group")
    rec["dateblock_delta"] = dateblock_delta
    rec["dateblock_win_rate"] = dateblock_win
    rec["q3_loss_vs_full"] = rec["q3_policy_delta"] - rec["q3_full_delta"]
    rec["s4_loss_vs_full"] = rec["s4_policy_delta"] - rec["s4_full_delta"]
    rec["strict_lifestyle_gate"] = bool(
        rec["loss_vs_full"] < -1.0e-5
        and rec["subject_win_rate"] >= 0.58
        and rec["dateblock_win_rate"] >= 0.55
        and (np.isnan(rec["dropped_mean_benefit"]) or rec["dropped_mean_benefit"] < 0.0)
    )
    return rec


def scan(train_aug: pd.DataFrame, feats: dict[str, list[str]]) -> pd.DataFrame:
    models = e237.model_defs()
    train_df = train_aug[train_aug["task_name"].isin(e237.CONTROL_TASKS)].reset_index(drop=True)
    # Keep the first falsification deliberately small. Earlier broad sweeps are
    # already abundant in this project; here the question is only whether the
    # lifestyle context survives blocked OOF at all.
    views = [
        "latent_no_targetid",
        "human_core",
        "human_late",
        "latent_human_core",
        "latent_human_late",
    ]
    rows: list[dict[str, Any]] = []
    for view in views:
        cols = feats[view]
        model_names = ["lr_l2_c0p10"]
        if view in {"human_late", "latent_human_late"}:
            model_names.append("hgb_shallow")
        for model_name in model_names:
            model = models[model_name]
            for split in ["dateblock5", "subject5"]:
                for source_scope in ["q3s4", "all3"]:
                    for kind in ["risk", "contrast"]:
                        for q in [0.10]:
                            spec = {
                                "view": view,
                                "n_features": len(cols),
                                "model": model_name,
                                "split": split,
                                "source_scope": source_scope,
                                "target_kind": kind,
                                "tail_q": q,
                            }
                            bad_prob, eval_label, _ = oof_bad_predict_custom(
                                model, train_df, cols, source_scope, split, kind, q
                            )
                            for policy, amp in e237.policy_amplitudes(train_df, bad_prob).items():
                                rows.append(evaluate_policy_with_blocks(train_df, spec, bad_prob, eval_label, amp, policy))
    out = pd.DataFrame(rows)
    out = out.sort_values(
        ["strict_lifestyle_gate", "stress_promote", "loss_vs_full", "tail_auc"],
        ascending=[False, False, True, False],
    ).reset_index(drop=True)
    return out


def summarize(scan_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    view_summary = (
        scan_df.groupby(["view", "model", "split"], as_index=False)
        .agg(
            rows=("policy", "count"),
            strict_gates=("strict_lifestyle_gate", "sum"),
            stress_promotes=("stress_promote", "sum"),
            best_loss_vs_full=("loss_vs_full", "min"),
            best_q3_loss_vs_full=("q3_loss_vs_full", "min"),
            median_tail_auc=("tail_auc", "median"),
            best_tail_auc=("tail_auc", "max"),
            best_subject_win=("subject_win_rate", "max"),
            best_dateblock_win=("dateblock_win_rate", "max"),
        )
        .sort_values(["strict_gates", "best_loss_vs_full"], ascending=[False, True])
    )

    pair_specs = [
        ("latent_human_late", "latent_no_targetid"),
        ("latent_human_core", "latent_no_targetid"),
        ("movement_human_late", "movement"),
    ]
    pair_rows: list[pd.DataFrame] = []
    keys = ["model", "split", "source_scope", "target_kind", "tail_q", "policy"]
    for plus, base in pair_specs:
        left = scan_df[scan_df["view"].eq(plus)].copy()
        right = scan_df[scan_df["view"].eq(base)].copy()
        joined = left.merge(right, on=keys, suffixes=("_plus", "_base"), how="inner")
        if joined.empty:
            continue
        joined["pair"] = f"{plus}_vs_{base}"
        joined["delta_loss_vs_full"] = joined["loss_vs_full_plus"] - joined["loss_vs_full_base"]
        joined["delta_q3_loss_vs_full"] = joined["q3_loss_vs_full_plus"] - joined["q3_loss_vs_full_base"]
        joined["delta_tail_auc"] = joined["tail_auc_plus"] - joined["tail_auc_base"]
        joined["plus_strict_only"] = joined["strict_lifestyle_gate_plus"].astype(bool) & ~joined[
            "strict_lifestyle_gate_base"
        ].astype(bool)
        pair_rows.append(joined)
    pair = pd.concat(pair_rows, ignore_index=True) if pair_rows else pd.DataFrame()
    pair_summary = (
        pair.groupby(["pair", "model", "split"], as_index=False)
        .agg(
            rows=("policy", "count"),
            plus_strict_only=("plus_strict_only", "sum"),
            median_delta_loss=("delta_loss_vs_full", "median"),
            best_delta_loss=("delta_loss_vs_full", "min"),
            median_delta_q3_loss=("delta_q3_loss_vs_full", "median"),
            median_delta_tail_auc=("delta_tail_auc", "median"),
            better_loss_rate=("delta_loss_vs_full", lambda x: float(np.mean(np.asarray(x) < 0.0))),
            better_q3_rate=("delta_q3_loss_vs_full", lambda x: float(np.mean(np.asarray(x) < 0.0))),
        )
        .sort_values(["plus_strict_only", "best_delta_loss"], ascending=[False, True])
        if not pair.empty
        else pd.DataFrame()
    )
    return view_summary, pair_summary


def write_report(scan_df: pd.DataFrame, view_summary: pd.DataFrame, pair_summary: pd.DataFrame) -> None:
    strict = scan_df[scan_df["strict_lifestyle_gate"].astype(bool)].copy()
    human = scan_df[scan_df["view"].str.startswith("human")].copy()
    human_plus = scan_df[scan_df["view"].str.contains("human")].copy()
    report = f"""# E264 Human/Social Tail JEPA OOF

## Question

Can the E262 human diary representation predict held-out Q3/S4 harmful tail cells under subject/date-block stress?

This is the OOF analogue required after E263. No public LB is fit and no submission is created.

## Headline

- scanned rows: `{len(scan_df)}` policies.
- strict lifestyle gates: `{int(scan_df['strict_lifestyle_gate'].sum())}`.
- human-only strict gates: `{int(human['strict_lifestyle_gate'].sum())}`.
- human-containing strict gates: `{int(human_plus['strict_lifestyle_gate'].sum())}`.
- best overall loss_vs_full: `{scan_df['loss_vs_full'].min():.9f}`.
- best human-only loss_vs_full: `{human['loss_vs_full'].min():.9f}`.

## Top Strict Rows

{md_table(strict, ['view','model','split','source_scope','target_kind','tail_q','policy','tail_auc','loss_vs_full','q3_loss_vs_full','s4_loss_vs_full','subject_win_rate','dateblock_win_rate','dropped_cells','dropped_q3','dropped_s4','dropped_mean_benefit'], 30)}

## View Summary

{md_table(view_summary, ['view','model','split','rows','strict_gates','stress_promotes','best_loss_vs_full','best_q3_loss_vs_full','median_tail_auc','best_tail_auc','best_subject_win','best_dateblock_win'], 40)}

## Human-Added Pair Deltas

{md_table(pair_summary, ['pair','model','split','rows','plus_strict_only','median_delta_loss','best_delta_loss','median_delta_q3_loss','median_delta_tail_auc','better_loss_rate','better_q3_rate'], 40)}

## Interpretation Rule

- If human-only or human-added views produce strict gates on `dateblock5` and `subject5`, the lifestyle representation is real enough to become a JEPA target/gate candidate.
- If only row5 works, it is likely local row/order leakage.
- If human-added views improve tail AUC but not policy loss, the representation is diagnostic energy only.
- If human views fail while latent baselines pass, E263's four-cell lifestyle contrast is likely not broad enough for a deployable gate.

## Decision

Use this report to decide whether to build E265 materialization. A submission is allowed only if a lifestyle-conditioned row/cell gate survives blocked OOF and does not reduce to subject/domain prediction.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    train_raw, train_long, sub_long, base_feats = e237.build_frames()
    train_aug, _, feats = append_human_context(train_raw, train_long, sub_long, base_feats)
    scan_df = scan(train_aug, feats)
    view_summary, pair_summary = summarize(scan_df)
    scan_df.to_csv(SCAN_OUT, index=False)
    view_summary.to_csv(VIEW_SUMMARY_OUT, index=False)
    pair_summary.to_csv(PAIR_OUT, index=False)
    write_report(scan_df, view_summary, pair_summary)
    print(f"wrote {SCAN_OUT}")
    print(f"wrote {VIEW_SUMMARY_OUT}")
    print(f"wrote {PAIR_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
