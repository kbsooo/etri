#!/usr/bin/env python3
"""E249: feature-NN1 augmented decisive-cell OOF audit.

E248 rejected the direct feature-NN1 smoothing score as an OOF-certified Q3
harmful-row selector. The next smaller question is whether the same manifold can
help when used as context inside the E237 decisive-cell target, rather than as a
standalone top-k smoothing rule.

This experiment adds fold-safe row-neighbor context features to the E237
cell-level bad-tail training frame and compares the OOF policies against the
original E237 scan. No submission files are created.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import broad_feature_addon_builder as stage2  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e207_lejepa_identifiability_conditions_audit as e207  # noqa: E402
import e237_cell_decisive_jepa_target as e237  # noqa: E402


RNG = 20260530 + 249
EPS = 1.0e-12
KEY = ["subject_id", "lifelog_date"]

BASE_OOF_IN = OUT / "e237_cell_decisive_jepa_target_oof_scan.csv"
RAW_OUT = OUT / "e249_feature_nn1_decisive_oof_scan.csv"
SUMMARY_OUT = OUT / "e249_feature_nn1_decisive_oof_summary.csv"
PAIR_OUT = OUT / "e249_feature_nn1_decisive_pair_summary.csv"
REPORT_OUT = OUT / "e249_feature_nn1_decisive_report.md"


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def train_only_feature_space(train_feat: pd.DataFrame) -> np.ndarray:
    cols = e207.numeric_feature_cols(train_feat)
    x, raw_cols = e207.scaled_matrix(train_feat, cols, top_cols=3000)
    return e207.pca_space("broad_stage2_pca64_train_only", x, "train-only broad stage2 matrix", raw_cols, dim=64).x


def nn1_indices(z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    nbrs = NearestNeighbors(n_neighbors=2, metric="euclidean")
    nbrs.fit(z)
    dist, ind = nbrs.kneighbors(z)
    return ind[:, 1].astype(int), dist[:, 1].astype(float)


def sub_feature_space(train_feat: pd.DataFrame, sub_feat: pd.DataFrame) -> np.ndarray:
    space = e207.load_pair_feature_space(train_feat, sub_feat)
    return space.x[len(train_feat) :]


def same_task_arrays(long_df: pd.DataFrame, col: str, task: str) -> np.ndarray:
    part = long_df[long_df["task_name"].eq(task)].sort_values("row_idx")
    arr = part[col].to_numpy(dtype=np.float64)
    expected = np.arange(len(arr), dtype=int)
    if not np.array_equal(part["row_idx"].to_numpy(dtype=int), expected):
        raise RuntimeError(f"unexpected row order for {task}/{col}")
    return arr


def append_feature_nn_context(long_df: pd.DataFrame, nn: np.ndarray, dist: np.ndarray) -> tuple[pd.DataFrame, list[str]]:
    out = long_df.copy()
    row_idx = out["row_idx"].to_numpy(dtype=int)
    out["featnn1_row_idx"] = nn[row_idx].astype(float)
    out["featnn1_dist"] = dist[row_idx].astype(float)

    value_cols = ["base_prob", "full_prob", "prob_gap", "logit_step", "abs_logit_step", "base_margin", "full_margin"]
    nn_cols = ["featnn1_row_idx", "featnn1_dist"]
    for col in value_cols:
        out[f"featnn1_{col}"] = np.nan
        out[f"featnn1_{col}_diff"] = np.nan
        out[f"featnn1_{col}_absdiff"] = np.nan
        nn_cols.extend([f"featnn1_{col}", f"featnn1_{col}_diff", f"featnn1_{col}_absdiff"])

    smooth_cols = [
        "featnn1_source_smooth_gain",
        "featnn1_incoming_smooth_gain_sum",
        "featnn1_incoming_count",
        "featnn1_total_smooth_gain",
        "featnn1_total_smooth_gain_mean",
        "featnn1_full_pair_abs_logit",
        "featnn1_base_pair_abs_logit",
    ]
    for col in smooth_cols:
        out[col] = np.nan
    nn_cols.extend(smooth_cols)

    for task in sorted(out["task_name"].unique()):
        mask = out["task_name"].eq(task)
        rows = out.loc[mask, "row_idx"].to_numpy(dtype=int)
        for col in value_cols:
            vals = same_task_arrays(out, col, str(task))
            nn_vals = vals[nn[rows]]
            cur_vals = out.loc[mask, col].to_numpy(dtype=np.float64)
            out.loc[mask, f"featnn1_{col}"] = nn_vals
            out.loc[mask, f"featnn1_{col}_diff"] = cur_vals - nn_vals
            out.loc[mask, f"featnn1_{col}_absdiff"] = np.abs(cur_vals - nn_vals)

        base = logit(same_task_arrays(out, "base_prob", str(task)))
        full = logit(same_task_arrays(out, "full_prob", str(task)))
        source_gain = np.abs(full - full[nn]) - np.abs(base - full[nn])
        incoming_gain = np.zeros(len(full), dtype=np.float64)
        incoming_count = np.zeros(len(full), dtype=np.float64)
        for src, target in enumerate(nn):
            target = int(target)
            incoming_gain[target] += abs(full[src] - full[target]) - abs(full[src] - base[target])
            incoming_count[target] += 1.0
        total_gain = source_gain + incoming_gain
        out.loc[mask, "featnn1_source_smooth_gain"] = source_gain[rows]
        out.loc[mask, "featnn1_incoming_smooth_gain_sum"] = incoming_gain[rows]
        out.loc[mask, "featnn1_incoming_count"] = incoming_count[rows]
        out.loc[mask, "featnn1_total_smooth_gain"] = total_gain[rows]
        out.loc[mask, "featnn1_total_smooth_gain_mean"] = total_gain[rows] / np.maximum(1.0 + incoming_count[rows], 1.0)
        out.loc[mask, "featnn1_full_pair_abs_logit"] = np.abs(full[rows] - full[nn[rows]])
        out.loc[mask, "featnn1_base_pair_abs_logit"] = np.abs(base[rows] - base[nn[rows]])

    if out[nn_cols].isna().any().any():
        bad = out[nn_cols].isna().sum()
        raise RuntimeError(f"NaN feature-NN context columns: {bad[bad > 0].to_dict()}")
    return out, nn_cols


def build_augmented_frames() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]], list[str]]:
    stage_train_raw, _, train_feat, sub_feat = stage2.build_frames()
    train_raw, train_long, sub_long, base_feats = e237.build_frames()
    if not stage_train_raw[KEY].astype(str).equals(train_raw[KEY].astype(str)):
        raise RuntimeError("stage2/e237 train key order mismatch")

    train_nn, train_dist = nn1_indices(train_only_feature_space(train_feat))
    sub_nn, sub_dist = nn1_indices(sub_feature_space(train_feat, sub_feat))
    train_aug, nn_cols = append_feature_nn_context(train_long, train_nn, train_dist)
    sub_aug, sub_nn_cols = append_feature_nn_context(sub_long, sub_nn, sub_dist)
    if nn_cols != sub_nn_cols:
        raise RuntimeError("train/sub feature-NN context columns mismatch")

    feats = dict(base_feats)
    for name in ["movement", "latent_no_targetid"]:
        cols = list(dict.fromkeys([*base_feats[name], *nn_cols]))
        feats[f"{name}_featnn1"] = cols
    return train_aug, sub_aug, feats, nn_cols


def oof_scan_feature_nn(train_aug: pd.DataFrame, feats: dict[str, list[str]]) -> pd.DataFrame:
    train_df = train_aug[train_aug["task_name"].isin(e237.CONTROL_TASKS)].reset_index(drop=True)
    rows: list[dict[str, Any]] = []
    models = e237.model_defs()
    for source_scope in ["q3s4", "all3"]:
        for view in ["movement_featnn1", "latent_no_targetid_featnn1"]:
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
                            bad_prob, eval_label, _ = e237.oof_bad_predict(
                                model, train_df, cols, source_scope, split, kind, q
                            )
                            for policy, amp in e237.policy_amplitudes(train_df, bad_prob).items():
                                rec = e237.evaluate_oof_policy(train_df, spec, bad_prob, eval_label, amp, policy)
                                rows.append(rec)
    return pd.DataFrame(rows).sort_values(["stress_promote", "loss_vs_full"], ascending=[False, True])


def summarize_against_e237(scan: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = pd.read_csv(BASE_OOF_IN)
    base = base[base["view"].isin(["movement", "latent_no_targetid"])].copy()
    scan = scan.copy()
    scan["base_view"] = scan["view"].str.replace("_featnn1", "", regex=False)
    key = ["source_scope", "base_view", "model", "split", "target_kind", "tail_q", "policy"]
    left = scan.rename(columns={"view": "nn_view"})
    right = base.rename(columns={"view": "base_view"})
    joined = left.merge(
        right,
        on=key,
        how="inner",
        suffixes=("_nn", "_base"),
    )
    joined["delta_loss_vs_full"] = joined["loss_vs_full_nn"] - joined["loss_vs_full_base"]
    joined["delta_tail_auc"] = joined["tail_auc_nn"] - joined["tail_auc_base"]
    joined["delta_subject_win_rate"] = joined["subject_win_rate_nn"] - joined["subject_win_rate_base"]
    joined["promoted_by_nn"] = joined["stress_promote_nn"].astype(bool) & ~joined["stress_promote_base"].astype(bool)
    joined["demoted_by_nn"] = ~joined["stress_promote_nn"].astype(bool) & joined["stress_promote_base"].astype(bool)

    pair_summary = (
        joined.groupby(["base_view", "model"], dropna=False)
        .agg(
            pairs=("policy", "count"),
            mean_delta_loss=("delta_loss_vs_full", "mean"),
            median_delta_loss=("delta_loss_vs_full", "median"),
            p10_delta_loss=("delta_loss_vs_full", lambda x: float(np.quantile(x, 0.10))),
            mean_delta_tail_auc=("delta_tail_auc", "mean"),
            median_delta_tail_auc=("delta_tail_auc", "median"),
            promoted_by_nn=("promoted_by_nn", "sum"),
            demoted_by_nn=("demoted_by_nn", "sum"),
            nn_better_loss_rate=("delta_loss_vs_full", lambda x: float((x < 0.0).mean())),
            nn_better_tail_auc_rate=("delta_tail_auc", lambda x: float((x > 0.0).mean())),
        )
        .reset_index()
        .sort_values(["median_delta_loss", "median_delta_tail_auc"], ascending=[True, False])
    )

    top_nn = scan.sort_values("loss_vs_full").head(30).assign(section="top_nn_loss")
    top_nn_tail = scan.sort_values("tail_auc", ascending=False).head(30).assign(section="top_nn_tail_auc")
    top_base = base.sort_values("loss_vs_full").head(30).assign(section="top_base_loss")
    top_base_tail = base.sort_values("tail_auc", ascending=False).head(30).assign(section="top_base_tail_auc")
    top = pd.concat([top_nn, top_nn_tail, top_base, top_base_tail], ignore_index=True)
    summary_cols = [
        "section",
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
        "dropped_mean_benefit",
        "stress_promote",
    ]
    summary = top[[c for c in summary_cols if c in top.columns]].drop_duplicates(
        ["section", "source_scope", "view", "model", "split", "target_kind", "tail_q", "policy"]
    )
    return summary, pair_summary


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, pair_summary: pd.DataFrame) -> None:
    best_nn = scan.sort_values("loss_vs_full").iloc[0]
    e237_top = pd.read_csv(BASE_OOF_IN)
    e237_ref = e237_top[
        (e237_top["source_scope"].eq("all3"))
        & (e237_top["view"].eq("latent_no_targetid"))
        & (e237_top["model"].eq("hgb_shallow"))
        & (e237_top["split"].eq("subject5"))
        & (e237_top["target_kind"].eq("risk"))
        & (np.isclose(e237_top["tail_q"], 0.10))
        & (e237_top["policy"].eq("drop_q3_top25"))
    ].iloc[0]
    promoted = int(scan["stress_promote"].astype(bool).sum())
    best_pair = pair_summary.iloc[0]
    cols = [
        "section",
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
        "dropped_mean_benefit",
        "stress_promote",
    ]
    pair_cols = [
        "base_view",
        "model",
        "pairs",
        "median_delta_loss",
        "mean_delta_loss",
        "p10_delta_loss",
        "median_delta_tail_auc",
        "promoted_by_nn",
        "demoted_by_nn",
        "nn_better_loss_rate",
        "nn_better_tail_auc_rate",
    ]
    lines = [
        "# E249 Feature-NN1 Decisive OOF Audit",
        "",
        "## Question",
        "",
        "Can feature-NN1 context rescue the E248 failure when used inside the E237 decisive-cell target, instead of as a direct smoothing selector?",
        "",
        "## Headline",
        "",
        f"- Feature-NN1 OOF rows scanned: `{len(scan)}`.",
        f"- Stress-promoted feature-NN1 rows: `{promoted}`.",
        f"- Best feature-NN1 OOF loss_vs_full: `{float(best_nn['loss_vs_full']):.9f}` from `{best_nn['view']}/{best_nn['model']}/{best_nn['split']}/{best_nn['target_kind']}/q={float(best_nn['tail_q']):.2f}/{best_nn['policy']}`.",
        f"- Locked E237 selected OOF loss_vs_full: `{float(e237_ref['loss_vs_full']):.9f}`, tail_auc `{float(e237_ref['tail_auc']):.9f}`.",
        f"- Best paired median delta: `{best_pair['base_view']}/{best_pair['model']}` has median loss delta `{float(best_pair['median_delta_loss']):.9f}` and median tail-AUC delta `{float(best_pair['median_delta_tail_auc']):.9f}`.",
        "",
        "## Top Rows",
        "",
        md_table(summary, cols, n=32),
        "",
        "## Paired Delta Versus Original E237 Views",
        "",
        md_table(pair_summary, pair_cols, n=12),
        "",
        "## Decision",
        "",
    ]
    if float(best_nn["loss_vs_full"]) < float(e237_ref["loss_vs_full"]) and promoted > 0:
        lines.append(
            "- Feature-NN1 context improves the OOF decisive-cell search enough to justify a materialization stress scan. Do not submit directly; next step is an E250 graft/actual gate using only the top OOF survivors."
        )
    else:
        lines.append(
            "- Feature-NN1 context does not beat the locked E237 selected OOF object strongly enough to justify materialization. The manifold remains diagnostic unless a public E247/E237 result says otherwise."
        )
    lines.append("- No submission file is created by E249.")
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    train_aug, _, feats, _ = build_augmented_frames()
    scan = oof_scan_feature_nn(train_aug, feats)
    summary, pair_summary = summarize_against_e237(scan)
    scan.to_csv(RAW_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    pair_summary.to_csv(PAIR_OUT, index=False)
    write_report(scan, summary, pair_summary)
    print("[E249 best feature-NN1 OOF rows]")
    print(
        scan.sort_values("loss_vs_full")
        [[
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
        ]]
        .head(12)
        .round(9)
        .to_string(index=False)
    )
    print("\n[E249 paired deltas]")
    print(pair_summary.round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
