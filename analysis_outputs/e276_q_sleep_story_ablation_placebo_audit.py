#!/usr/bin/env python3
"""E276: q-sleep story ablation and placebo audit.

E275 produced the first public-free promoted human-diary candidate. This script
tries to kill that interpretation without using new public LB:

- remove or isolate human story families;
- separate JEPA-derived axes from raw diary-energy axes;
- keep movement magnitude but destroy row/state alignment with placebo shuffles;
- invert the direction as a sanity check.

If the same public-free gate also promotes shuffled or inverse controls, E275 is
probably selector/magnitude artifact. If only semantically coherent Q-side
families survive, the hidden lifestyle-state explanation becomes stronger.
"""

from __future__ import annotations

from pathlib import Path
import sys

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
    movement_anatomy,
    score_candidates,
    selected_models,
)
from e274_target_specific_diary_energy_audit import (  # noqa: E402
    AXIS_OUT,
    FEATURE_PATH,
    TARGETS,
    apply_axis_moves,
    clip_prob,
    short_hash,
    sigmoid,
)
from public_anchor_bottleneck_decomposition import KEYS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


RNG_SEED = 20260531 + 276
PRIMARY_FILE = "submission_e275_q_sleep_amp_m160_86528b2f.csv"
SCORE_OUT = OUT / "e276_q_sleep_story_ablation_placebo_scores.csv"
ANATOMY_OUT = OUT / "e276_q_sleep_story_ablation_placebo_anatomy.csv"
VARIANT_OUT = OUT / "e276_q_sleep_story_ablation_placebo_variants.csv"
PLACEBO_OUT = OUT / "e276_q_sleep_story_ablation_placebo_nulls.csv"
AXIS_SUMMARY_OUT = OUT / "e276_q_sleep_story_ablation_placebo_axis_summary.csv"
REPORT_OUT = OUT / "e276_q_sleep_story_ablation_placebo_report.md"


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


def story_family(feature: str) -> str:
    if "mobility_context" in feature:
        return "mobility_context"
    if "bedtime_phone" in feature or "phone" in feature:
        return "bedtime_phone"
    if "routine_calendar" in feature:
        return "routine_calendar"
    if "cognitive_money" in feature or "money" in feature:
        return "cognitive_money"
    if "social_comm" in feature or "social" in feature:
        return "social_comm"
    if "media_game" in feature or "game" in feature or "media" in feature:
        return "media_game"
    if "diary_state" in feature:
        return "diary_global"
    return "other"


def axis_kind(feature: str) -> str:
    if feature.startswith("jepa_prednorm_"):
        return "jepa_prednorm"
    if feature.startswith("jepa_resid_"):
        return "jepa_resid"
    if feature.endswith("_energy") or feature == "diary_state_energy":
        return "energy"
    if "_pc" in feature or feature.startswith("diary_state_pc"):
        return "pc"
    return "other"


def q_axes_top12() -> pd.DataFrame:
    axes = pd.read_csv(AXIS_OUT)
    axes = axes[axes["target"].isin(["Q1", "Q2", "Q3"])].copy()
    axes = axes.sort_values("local_axis_score", ascending=False).head(12).reset_index(drop=True)
    axes["story_family"] = axes["feature"].map(story_family)
    axes["axis_kind"] = axes["feature"].map(axis_kind)
    return axes


def base_config(candidate_id: str) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "n_axes": 32,
        "top_each": 12,
        "amp": 0.045 * 1.60,
        "cap": 0.090,
        "include_diagnostic": True,
        "targets": ["Q1", "Q2", "Q3"],
    }


def write_submission(frame: pd.DataFrame, candidate_id: str) -> str:
    h = short_hash(frame)
    name = f"submission_e276_{candidate_id}_{h}.csv"
    frame.to_csv(OUT / name, index=False)
    return name


def materialize_axis_variant(base: pd.DataFrame, features: pd.DataFrame, axes: pd.DataFrame, candidate_id: str) -> tuple[str, int]:
    cfg = base_config(candidate_id)
    if axes.empty:
        out = base.copy()
        name = write_submission(out, candidate_id)
        return name, 0
    out, cells = apply_axis_moves(base, features, axes.reset_index(drop=True), cfg)
    name = write_submission(out, candidate_id)
    return name, int(len(cells))


def test_meta(features: pd.DataFrame) -> pd.DataFrame:
    test = features[features["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    out = test[KEYS + ["dateblock_group"]].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    return out


def aligned_meta(features: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    meta = test_meta(features)
    keys = base[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        keys[col] = pd.to_datetime(keys[col]).dt.strftime("%Y-%m-%d")
    if not meta[KEYS].equals(keys):
        raise RuntimeError("E276 feature/test keys do not align with current submission")
    return meta


def shuffled_candidate(
    base: pd.DataFrame,
    primary: pd.DataFrame,
    meta: pd.DataFrame,
    candidate_id: str,
    mode: str,
    seed: int,
) -> str:
    rng = np.random.default_rng(seed)
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    primary_logits = logit(primary[TARGETS].to_numpy(dtype=np.float64))
    delta = primary_logits - base_logits
    shuffled = np.zeros_like(delta)
    for target_idx, _ in enumerate(TARGETS):
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
    out[TARGETS] = clip_prob(sigmoid(base_logits + shuffled))
    return write_submission(out, candidate_id)


def inverse_candidate(base: pd.DataFrame, primary: pd.DataFrame, candidate_id: str, scale: float) -> str:
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    primary_logits = logit(primary[TARGETS].to_numpy(dtype=np.float64))
    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(base_logits - scale * (primary_logits - base_logits)))
    return write_submission(out, candidate_id)


def materialize_variants() -> tuple[list[str], pd.DataFrame, pd.DataFrame]:
    base = load_sub(CURRENT)
    primary = load_sub(PRIMARY_FILE)
    features = pd.read_parquet(FEATURE_PATH)
    axes = q_axes_top12()
    meta = aligned_meta(features, base)

    variant_rows: list[dict[str, object]] = []
    files: list[str] = [PRIMARY_FILE]

    def add_axis_variant(candidate_id: str, subset: pd.DataFrame, family: str, kind: str) -> None:
        name, cell_count = materialize_axis_variant(base, features, subset, candidate_id)
        files.append(name)
        variant_rows.append({
            "basename": name,
            "candidate_id": candidate_id,
            "variant_type": "axis_ablation",
            "family_tested": family,
            "axis_kind_tested": kind,
            "axis_count": int(len(subset)),
            "cell_rows": cell_count,
        })

    variant_rows.append({
        "basename": PRIMARY_FILE,
        "candidate_id": "e275_primary_m160",
        "variant_type": "primary",
        "family_tested": "all",
        "axis_kind_tested": "all",
        "axis_count": int(len(axes)),
        "cell_rows": np.nan,
    })

    add_axis_variant("story_full_rebuild_m160", axes, "all", "all")
    add_axis_variant("q3_only_m160", axes[axes["target"].eq("Q3")], "q3_only", "all")
    add_axis_variant("q12_only_m160", axes[axes["target"].isin(["Q1", "Q2"])], "q12_only", "all")
    add_axis_variant("jepa_only_m160", axes[axes["axis_kind"].str.startswith("jepa")], "all", "jepa_only")
    add_axis_variant("nonjepa_only_m160", axes[~axes["axis_kind"].str.startswith("jepa")], "all", "nonjepa_only")

    families = ["mobility_context", "bedtime_phone", "routine_calendar", "cognitive_money", "social_comm", "media_game", "diary_global"]
    for family in families:
        add_axis_variant(f"only_{family}_m160", axes[axes["story_family"].eq(family)], family, "only")
        add_axis_variant(f"no_{family}_m160", axes[~axes["story_family"].eq(family)], family, "leave_one_out")

    files.append(inverse_candidate(base, primary, "inverse_primary_m080", 0.80))
    variant_rows.append({
        "basename": files[-1],
        "candidate_id": "inverse_primary_m080",
        "variant_type": "inverse_control",
        "family_tested": "all",
        "axis_kind_tested": "inverse",
        "axis_count": int(len(axes)),
        "cell_rows": np.nan,
    })

    placebo_rows: list[dict[str, object]] = []
    for mode in ["row", "subject", "dateblock"]:
        for rep in range(5):
            candidate_id = f"shuffle_{mode}_r{rep}"
            name = shuffled_candidate(base, primary, meta, candidate_id, mode, RNG_SEED + rep + 100 * len(placebo_rows))
            files.append(name)
            row = {
                "basename": name,
                "candidate_id": candidate_id,
                "variant_type": "shuffle_placebo",
                "family_tested": mode,
                "axis_kind_tested": "same_delta_shuffled",
                "axis_count": int(len(axes)),
                "cell_rows": np.nan,
            }
            variant_rows.append(row)
            placebo_rows.append(row)

    variants = pd.DataFrame(variant_rows)
    placebos = pd.DataFrame(placebo_rows)
    variants.to_csv(VARIANT_OUT, index=False)
    placebos.to_csv(PLACEBO_OUT, index=False)
    axis_summary = (
        axes.groupby(["target", "story_family", "axis_kind"], dropna=False)
        .agg(
            n_axes=("feature", "size"),
            mean_local_axis_score=("local_axis_score", "mean"),
            min_dateblock_delta=("dateblock_delta", "min"),
            mean_abs_label_lift=("abs_label_lift", "mean"),
            features=("feature", lambda x: ";".join(map(str, x))),
        )
        .reset_index()
        .sort_values(["mean_local_axis_score", "n_axes"], ascending=[False, False])
    )
    axis_summary.to_csv(AXIS_SUMMARY_OUT, index=False)
    return files, variants, axis_summary


def audit(files: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sample = load_sub(CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    all_files = [CURRENT, *files]
    deduped: list[str] = []
    seen: set[str] = set()
    for file_name in all_files:
        if file_name not in seen:
            seen.add(file_name)
            deduped.append(file_name)
    candidates = build_features(deduped, sample, refs, ref_vecs)
    model_df = evaluate_models(known)
    scores = score_candidates(known, candidates, model_df)
    anatomy = movement_anatomy(deduped, sample)
    scores.to_csv(SCORE_OUT, index=False)
    anatomy.to_csv(ANATOMY_OUT, index=False)
    return scores, anatomy, selected_models(model_df)


def write_report(scores: pd.DataFrame, anatomy: pd.DataFrame, selected: pd.DataFrame, variants: pd.DataFrame, axis_summary: pd.DataFrame) -> None:
    merged = scores.merge(variants, on="basename", how="left")
    merged["variant_type"] = merged["variant_type"].fillna("reference")
    merged = merged.sort_values(
        ["strict_promote_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, True, True],
    )
    placebo = merged[merged["variant_type"].eq("shuffle_placebo")].copy()
    axis_variants = merged[merged["variant_type"].isin(["primary", "axis_ablation", "inverse_control"])].copy()
    strict_placebo = int(placebo["strict_promote_gate"].fillna(False).astype(bool).sum())
    strict_axis = int(axis_variants["strict_promote_gate"].fillna(False).astype(bool).sum())
    primary = merged[merged["basename"].eq(PRIMARY_FILE)]
    primary_p90 = float(primary["pred_delta_vs_current_p90"].iloc[0]) if len(primary) else np.nan

    score_cols = [
        "basename",
        "variant_type",
        "family_tested",
        "axis_kind_tested",
        "axis_count",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]
    anatomy_cols = [
        "basename",
        "changed_cells_vs_current",
        "changed_rows_vs_current",
        "l1_logit_delta_vs_current",
        "max_abs_prob_delta_vs_current",
    ]
    axis_cols = ["target", "story_family", "axis_kind", "n_axes", "mean_local_axis_score", "min_dateblock_delta", "mean_abs_label_lift", "features"]
    placebo_summary = (
        placebo.groupby("family_tested", dropna=False)
        .agg(
            n=("basename", "size"),
            strict_promote=("strict_promote_gate", lambda x: int(np.asarray(x, dtype=bool).sum())),
            best_p90=("pred_delta_vs_current_p90", "min"),
            mean_p90=("pred_delta_vs_current_p90", "mean"),
            best_mean=("pred_delta_vs_current_mean", "min"),
        )
        .reset_index()
        .sort_values(["strict_promote", "best_p90"], ascending=[False, True])
        if len(placebo)
        else pd.DataFrame()
    )

    decision = []
    if strict_placebo:
        decision.append("At least one shuffled placebo passes the strict gate. E275 must be demoted until the selector is made less magnitude-sensitive.")
    else:
        decision.append("No shuffled placebo passes the strict gate. This weakens the movement-magnitude artifact explanation.")
    if len(primary) and bool(primary["strict_promote_gate"].iloc[0]):
        decision.append("The original E275 primary remains strict-promoted under the same audit.")
    else:
        decision.append("The original E275 primary no longer strict-promotes under this rerun; do not submit it without rebuilding the gate.")
    if strict_axis:
        top = axis_variants[axis_variants["strict_promote_gate"].fillna(False).astype(bool)].iloc[0]
        decision.append(f"Best surviving semantic variant is `{top['basename']}`; its family/kind is `{top['family_tested']}` / `{top['axis_kind_tested']}`.")
    else:
        decision.append("No semantic ablation strict-promotes; E275 may rely on all-axis interaction rather than a single interpretable family.")

    lines = [
        "# E276 Q-Sleep Story Ablation + Placebo Audit",
        "",
        "## Question",
        "",
        "Does the E275 q-sleep diary-energy candidate survive because it encodes coherent human lifestyle state, or because the public-free selector likes any Q-side movement with similar magnitude?",
        "",
        "## Gate",
        "",
        f"- selected E272-style selector models: `{len(selected)}`",
        f"- primary E275 p90 delta vs E247: `{primary_p90:.9f}`",
        f"- strict semantic/control variants: `{strict_axis}`",
        f"- strict shuffled placebos: `{strict_placebo}`",
        "",
        "## Axis Families In The E275 Story",
        "",
        md_table(axis_summary[axis_cols], n=30),
        "",
        "## Semantic Ablation Scores",
        "",
        md_table(axis_variants[score_cols], n=50),
        "",
        "## Placebo Shuffle Summary",
        "",
        md_table(placebo_summary, n=20),
        "",
        "## Top Placebo Rows",
        "",
        md_table(placebo[score_cols].sort_values("pred_delta_vs_current_p90"), n=20) if len(placebo) else "_empty_",
        "",
        "## Movement Anatomy",
        "",
        md_table(anatomy[anatomy["basename"].isin(merged["basename"])][anatomy_cols].sort_values("l1_logit_delta_vs_current", ascending=False), n=40),
        "",
        "## Decision",
        "",
        *[f"- {line}" for line in decision],
        "",
        "## Interpretation Rules",
        "",
        "- If shuffled placebos pass: treat E275 as a selector artifact, not a lifestyle-state candidate.",
        "- If only Q3/JEPA/mobility variants pass: the useful hidden state is narrower than the broad q-sleep story.",
        "- If leave-one-family variants pass but only-family variants do not: the representation is a composite lifestyle state and should be gated, not simplified.",
        "- If inverse control passes: the direction is not identifiable and the candidate should be rejected.",
        "",
        "## Files",
        "",
        f"- `{SCORE_OUT.name}`",
        f"- `{ANATOMY_OUT.name}`",
        f"- `{VARIANT_OUT.name}`",
        f"- `{PLACEBO_OUT.name}`",
        f"- `{AXIS_SUMMARY_OUT.name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    files, variants, axis_summary = materialize_variants()
    scores, anatomy, selected = audit(files)
    write_report(scores, anatomy, selected, variants, axis_summary)
    print(REPORT_OUT)
    merged = scores.merge(variants, on="basename", how="left")
    print(
        merged.sort_values(["strict_promote_gate", "pred_delta_vs_current_p90"], ascending=[False, True])[
            [
                "basename",
                "variant_type",
                "family_tested",
                "axis_kind_tested",
                "promotion_decision",
                "pred_delta_vs_current_mean",
                "pred_delta_vs_current_p90",
                "pred_beats_current_rate",
            ]
        ].head(30).round(9).to_string(index=False)
    )


if __name__ == "__main__":
    main()
