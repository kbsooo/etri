#!/usr/bin/env python3
"""E325: semantic null attribution for E323 residual candidates.

E323/E324 produced the first public-free ready files after the E247 frontier,
but the winning local evidence was mostly action-geometry/null rarity.  This
script asks a different question:

    Does the residual action land on human/social diary states in a way that
    row/subject/dateblock null placements cannot reproduce?

This is a LeJEPA-style representation check.  A good action should not only
beat numeric nulls; its touched rows should have a coherent latent human story
relative to matched placements.  Public LB is not used and no submission is
created.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e288_lifestyle_bundle_jepa_audit import (  # noqa: E402
    TARGETS,
    KEYS,
    build_story_matrix,
    load_frames,
    md_table,
)
from e295_episode_state_jepa_audit import (  # noqa: E402
    build_episode_matrix,
    base_story_cols,
    preferred_col,
)
from public_anchor_bottleneck_decomposition import load_sub, logit  # noqa: E402


CURRENT = OUT / "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
E324_GOVERNOR = OUT / "e324_e323_ready_highrep_governor_audit.csv"
SOCIAL_HYP = OUT / "e268_human_social_story_hypotheses.csv"
CASH_HYP = OUT / "e270_payday_cashflow_story_verdicts.csv"

ATTR_OUT = OUT / "e325_e323_semantic_null_attribution.csv"
SUMMARY_OUT = OUT / "e325_e323_semantic_null_summary.csv"
FEATURE_META_OUT = OUT / "e325_e323_semantic_feature_meta.csv"
REPORT_OUT = OUT / "e325_e323_semantic_null_report.md"

NULL_REPS = 128
NULL_MODES = ("row", "subject", "dateblock")
EPS = 1.0e-12
RNG_SEED = 20260531 + 325


def stable_seed(*parts: object) -> int:
    text = "|".join(str(p) for p in parts)
    return RNG_SEED + int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100000


def safe_std(x: np.ndarray) -> float:
    val = float(np.nanstd(x, ddof=0))
    return val if np.isfinite(val) and val > EPS else 1.0


def zscore_train(series: pd.Series, train_mask: np.ndarray) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
    tr = x.iloc[train_mask]
    mu = float(tr.mean())
    sd = float(tr.std(ddof=0))
    if not np.isfinite(sd) or sd < EPS:
        return pd.Series(0.0, index=x.index)
    return ((x - mu) / sd).replace([np.inf, -np.inf], 0.0).fillna(0.0).clip(-8.0, 8.0)


def load_current() -> pd.DataFrame:
    return load_sub(CURRENT).sort_values(KEYS).reset_index(drop=True)


def load_delta(path: Path, current: pd.DataFrame) -> np.ndarray:
    sub = load_sub(path).sort_values(KEYS).reset_index(drop=True)
    if not sub[KEYS].equals(current[KEYS]):
        raise RuntimeError(f"key mismatch: {path}")
    return logit(sub[TARGETS].to_numpy(dtype=float)) - logit(current[TARGETS].to_numpy(dtype=float))


def load_candidates() -> pd.DataFrame:
    gov = pd.read_csv(E324_GOVERNOR)
    gov = gov[gov["highrep_public_free_submission_ready"].astype(bool)].copy()
    gov = gov.sort_values(
        ["highrep_null_strict_rate", "highrep_worst_mode_p90_dominance", "highrep_actual_p90"],
        ascending=[True, False, True],
    ).reset_index(drop=True)
    return gov


def story_meta_map() -> dict[str, dict[str, str]]:
    meta: dict[str, dict[str, str]] = {}
    if SOCIAL_HYP.exists():
        social = pd.read_csv(SOCIAL_HYP)
        for row in social.itertuples(index=False):
            meta[f"hstory__{row.story_id}"] = {
                "family": str(row.family),
                "human_story": str(row.human_story),
            }
    if CASH_HYP.exists():
        cash = pd.read_csv(CASH_HYP)
        for row in cash.itertuples(index=False):
            story_id = str(getattr(row, "story_id"))
            meta[f"cash__{story_id}"] = {
                "family": str(getattr(row, "family", "cashflow")),
                "human_story": str(getattr(row, "human_story", story_id)),
            }
    return meta


def build_semantic_matrix() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base, _raw, stories, feature_frames = load_frames()
    base = base.sort_values(KEYS).reset_index(drop=True)
    train_mask = base["split"].eq("train").to_numpy()

    story_matrix, story_meta = build_story_matrix(base, stories, feature_frames)
    episode_matrix, episode_meta = build_episode_matrix(base, feature_frames)

    frames: list[pd.DataFrame] = [
        story_matrix.add_prefix("e280__"),
        episode_matrix.add_prefix("episode__"),
    ]

    meta_rows: list[dict[str, Any]] = []
    for row in story_meta.itertuples(index=False):
        meta_rows.append(
            {
                "feature": f"e280__{row.story}",
                "source": str(row.source),
                "family": str(row.mapped_family),
                "human_story": str(row.human_story),
            }
        )
    for row in episode_meta.drop_duplicates("episode").itertuples(index=False):
        meta_rows.append(
            {
                "feature": f"episode__{row.episode}",
                "source": "episode",
                "family": str(row.episode),
                "human_story": str(row.human_story),
            }
        )

    meta_hint = story_meta_map()
    for source_name, frame in feature_frames.items():
        prefix = "hstory" if source_name == "human_social" else "cash"
        cols = []
        for base_col in base_story_cols(frame):
            col = preferred_col(frame, base_col)
            if col is not None:
                cols.append((base_col, col))
        keep: dict[str, pd.Series] = {}
        for base_col, col in cols:
            feat = f"{prefix}__{base_col}"
            keep[feat] = zscore_train(frame[col], train_mask)
            hint = meta_hint.get(feat, {})
            meta_rows.append(
                {
                    "feature": feat,
                    "source": source_name,
                    "family": hint.get("family", source_name),
                    "human_story": hint.get("human_story", base_col.replace("_", " ")),
                }
            )
        if keep:
            frames.append(pd.DataFrame(keep, index=base.index))

    calendar = pd.DataFrame(index=base.index)
    for col in ["weekday", "is_weekend", "lifelog_dom", "lifelog_month", "subject_order"]:
        if col in base.columns:
            calendar[f"calendar__{col}"] = zscore_train(base[col], train_mask)
            meta_rows.append(
                {
                    "feature": f"calendar__{col}",
                    "source": "calendar",
                    "family": "calendar",
                    "human_story": col,
                }
            )
    if "lifelog_dom" in base.columns:
        dom = pd.to_numeric(base["lifelog_dom"], errors="coerce").fillna(0.0).astype(float)
        payday_like = pd.DataFrame(
            {
                "calendar__pre25_cash_window": ((dom >= 20) & (dom <= 24)).astype(float),
                "calendar__post25_relief_window": ((dom >= 25) & (dom <= 28)).astype(float),
                "calendar__month_end_bill_window": (dom >= 27).astype(float),
                "calendar__month_start_reset": (dom <= 3).astype(float),
            },
            index=base.index,
        )
        for col in payday_like.columns:
            calendar[col] = zscore_train(payday_like[col], train_mask)
            meta_rows.append(
                {
                    "feature": col,
                    "source": "calendar",
                    "family": "cashflow_calendar",
                    "human_story": col.replace("calendar__", "").replace("_", " "),
                }
            )
    frames.append(calendar)

    semantic = pd.concat(frames, axis=1)
    semantic = semantic.loc[:, ~semantic.columns.duplicated()].replace([np.inf, -np.inf], 0.0).fillna(0.0)
    meta = pd.DataFrame(meta_rows).drop_duplicates("feature")
    return base, semantic, meta


def shuffle_delta(delta: np.ndarray, meta: pd.DataFrame, mode: str, rep: int, basename: str) -> np.ndarray:
    rng = np.random.default_rng(stable_seed(basename, mode, rep))
    if mode == "row":
        return delta[rng.permutation(len(delta))]
    out = delta.copy()
    group_col = "subject_id" if mode == "subject" else "dateblock_group"
    for _, idx in meta.groupby(group_col).indices.items():
        idx_arr = np.asarray(idx, dtype=int)
        if len(idx_arr) > 1:
            out[idx_arr] = delta[idx_arr][rng.permutation(len(idx_arr))]
    return out


def weighted_feature_scores(delta: np.ndarray, features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    abs_rows = []
    signed_rows = []
    for j in range(delta.shape[1]):
        d = delta[:, j]
        weight = np.abs(d)
        denom = float(weight.sum())
        if denom < EPS:
            abs_rows.append(np.zeros(features.shape[1]))
            signed_rows.append(np.zeros(features.shape[1]))
            continue
        abs_rows.append((weight[:, None] * features).sum(axis=0) / denom)
        signed_rows.append((d[:, None] * features).sum(axis=0) / denom)
    return np.vstack(abs_rows), np.vstack(signed_rows)


def attribution_for_candidate(
    basename: str,
    path: Path,
    current: pd.DataFrame,
    test_meta: pd.DataFrame,
    semantic_test: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    delta = load_delta(path, current)
    feature_names = semantic_test.columns.to_numpy()
    feat_values = semantic_test.to_numpy(dtype=float)
    actual_abs, actual_signed = weighted_feature_scores(delta, feat_values)

    null_abs_values = {mode: [] for mode in NULL_MODES}
    null_signed_values = {mode: [] for mode in NULL_MODES}
    for mode in NULL_MODES:
        for rep in range(NULL_REPS):
            ndelta = shuffle_delta(delta, test_meta, mode, rep, basename)
            nabs, nsigned = weighted_feature_scores(ndelta, feat_values)
            null_abs_values[mode].append(nabs)
            null_signed_values[mode].append(nsigned)

    rows: list[dict[str, Any]] = []
    for target_idx, target in enumerate(TARGETS):
        for feature_idx, feature in enumerate(feature_names):
            mode_z_abs = []
            mode_z_signed = []
            mode_dom_abs = []
            mode_dom_signed = []
            for mode in NULL_MODES:
                a_null = np.asarray([x[target_idx, feature_idx] for x in null_abs_values[mode]], dtype=float)
                s_null = np.asarray([x[target_idx, feature_idx] for x in null_signed_values[mode]], dtype=float)
                aval = float(actual_abs[target_idx, feature_idx])
                sval = float(actual_signed[target_idx, feature_idx])
                az = (aval - float(a_null.mean())) / safe_std(a_null)
                sz = (sval - float(s_null.mean())) / safe_std(s_null)
                mode_z_abs.append(az)
                mode_z_signed.append(sz)
                mode_dom_abs.append(max(float(np.mean(aval >= a_null)), float(np.mean(aval <= a_null))))
                mode_dom_signed.append(max(float(np.mean(sval >= s_null)), float(np.mean(sval <= s_null))))
            rows.append(
                {
                    "basename": basename,
                    "target": target,
                    "feature": str(feature),
                    "actual_abs_weighted_mean": float(actual_abs[target_idx, feature_idx]),
                    "actual_signed_weighted_mean": float(actual_signed[target_idx, feature_idx]),
                    "abs_z_worst_abs": float(np.min(np.abs(mode_z_abs))),
                    "abs_z_max_abs": float(np.max(np.abs(mode_z_abs))),
                    "signed_z_worst_abs": float(np.min(np.abs(mode_z_signed))),
                    "signed_z_max_abs": float(np.max(np.abs(mode_z_signed))),
                    "abs_worst_mode_dominance": float(np.min(mode_dom_abs)),
                    "signed_worst_mode_dominance": float(np.min(mode_dom_signed)),
                    "row_abs_z": float(mode_z_abs[0]),
                    "subject_abs_z": float(mode_z_abs[1]),
                    "dateblock_abs_z": float(mode_z_abs[2]),
                    "row_signed_z": float(mode_z_signed[0]),
                    "subject_signed_z": float(mode_z_signed[1]),
                    "dateblock_signed_z": float(mode_z_signed[2]),
                }
            )

    attr = pd.DataFrame(rows)
    nonzero_rows = int(np.any(np.abs(delta) > EPS, axis=1).sum())
    nonzero_cells = int(np.sum(np.abs(delta) > EPS))
    abs_by_target = np.abs(delta).sum(axis=0)
    summary = {
        "basename": basename,
        "source_path": str(path.relative_to(ROOT)),
        "nonzero_rows": nonzero_rows,
        "nonzero_cells": nonzero_cells,
        "mean_abs_delta": float(np.mean(np.abs(delta))),
        "max_abs_delta": float(np.max(np.abs(delta))),
        "q_abs_share": float(abs_by_target[:3].sum() / max(abs_by_target.sum(), EPS)),
        "s_abs_share": float(abs_by_target[3:].sum() / max(abs_by_target.sum(), EPS)),
        "best_abs_semantic_z": float(attr["abs_z_worst_abs"].max()),
        "best_signed_semantic_z": float(attr["signed_z_worst_abs"].max()),
        "semantic_abs_hits_z2": int((attr["abs_z_worst_abs"] >= 2.0).sum()),
        "semantic_signed_hits_z2": int((attr["signed_z_worst_abs"] >= 2.0).sum()),
        "semantic_abs_hits_dom97": int((attr["abs_worst_mode_dominance"] >= 0.97).sum()),
        "semantic_signed_hits_dom97": int((attr["signed_worst_mode_dominance"] >= 0.97).sum()),
    }
    for i, target in enumerate(TARGETS):
        summary[f"abs_delta_{target}"] = float(abs_by_target[i])
    return attr, summary


def main() -> None:
    current = load_current()
    base, semantic, feature_meta = build_semantic_matrix()
    test_mask = base["split"].eq("test")
    test = base.loc[test_mask].sort_values(KEYS).reset_index(drop=True)
    semantic_test = semantic.loc[test_mask].sort_index().reset_index(drop=True)
    test_keys = test[KEYS].astype(str).reset_index(drop=True)
    current_keys = current[KEYS].astype(str).reset_index(drop=True)
    if not current_keys.equals(test_keys):
        raise RuntimeError("semantic test rows do not align with current submission")

    cand = load_candidates()
    all_attr = []
    summary_rows = []
    for row in cand.itertuples(index=False):
        basename = str(row.basename)
        path = ROOT / str(row.source_path)
        attr, summary = attribution_for_candidate(basename, path, current, test, semantic_test)
        summary.update(
            {
                "highrep_actual_p90": float(row.highrep_actual_p90),
                "highrep_actual_mean": float(row.highrep_actual_mean),
                "highrep_null_strict_rate": float(row.highrep_null_strict_rate),
                "highrep_worst_mode_p90_dominance": float(row.highrep_worst_mode_p90_dominance),
            }
        )
        all_attr.append(attr)
        summary_rows.append(summary)

    attr_df = pd.concat(all_attr, ignore_index=True)
    attr_df = attr_df.merge(feature_meta, on="feature", how="left")
    attr_df = attr_df.sort_values(
        ["basename", "signed_z_worst_abs", "abs_z_worst_abs"],
        ascending=[True, False, False],
    ).reset_index(drop=True)
    summary_df = pd.DataFrame(summary_rows).sort_values(
        ["highrep_null_strict_rate", "best_signed_semantic_z"],
        ascending=[True, False],
    ).reset_index(drop=True)

    attr_df.to_csv(ATTR_OUT, index=False)
    summary_df.to_csv(SUMMARY_OUT, index=False)
    feature_meta.to_csv(FEATURE_META_OUT, index=False)

    priority = summary_df.iloc[0]
    top_priority = attr_df[attr_df["basename"].eq(priority["basename"])].copy()
    top_priority = top_priority.sort_values(
        ["signed_z_worst_abs", "abs_z_worst_abs"],
        ascending=[False, False],
    )
    top_all = attr_df.sort_values(
        ["signed_z_worst_abs", "abs_z_worst_abs"],
        ascending=[False, False],
    ).head(30)

    lines = [
        "# E325 E323 Semantic Null Attribution",
        "",
        "Public LB was not used.",
        "",
        "## Question",
        "",
        "Do the E323 residual candidates touch rows with coherent human/social diary states, or can matched row/subject/dateblock placements reproduce the same semantic alignment?",
        "",
        "## Summary",
        "",
        md_table(
            summary_df[
                [
                    "basename",
                    "highrep_actual_p90",
                    "highrep_null_strict_rate",
                    "best_signed_semantic_z",
                    "best_abs_semantic_z",
                    "semantic_signed_hits_z2",
                    "semantic_abs_hits_z2",
                    "q_abs_share",
                    "s_abs_share",
                ]
            ],
            n=10,
        ),
        "",
        "## Priority Candidate Semantic Read",
        "",
        f"Priority by E324 risk remains `{priority['basename']}`.",
        "",
        md_table(
            top_priority[
                [
                    "target",
                    "feature",
                    "source",
                    "family",
                    "signed_z_worst_abs",
                    "abs_z_worst_abs",
                    "signed_worst_mode_dominance",
                    "actual_signed_weighted_mean",
                    "human_story",
                ]
            ],
            n=20,
        ),
        "",
        "## Top Semantic Alignments Across Ready Files",
        "",
        md_table(
            top_all[
                [
                    "basename",
                    "target",
                    "feature",
                    "source",
                    "family",
                    "signed_z_worst_abs",
                    "abs_z_worst_abs",
                    "signed_worst_mode_dominance",
                    "human_story",
                ]
            ],
            n=30,
        ),
        "",
        "## Decision",
        "",
        "- This is an attribution/checking experiment, not a new submission generator.",
        "- A ready file gains semantic support only if its actual touched rows have target/story alignment that remains extreme against row, subject, and dateblock placements.",
        "- If no semantic z-score clears the nulls, E323 should be treated as an action-geometry residual rather than a human-story breakthrough.",
        "",
        "## Outputs",
        "",
        f"- `{ATTR_OUT.relative_to(ROOT)}`",
        f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
        f"- `{FEATURE_META_OUT.relative_to(ROOT)}`",
        f"- `{REPORT_OUT.relative_to(ROOT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {REPORT_OUT}")
    print(summary_df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
