#!/usr/bin/env python3
"""E66 Q2/S3 conflict translator probe.

E65 found a real near-zero E56 response pocket, but the best target mask was
`no_q2_s3` and no candidate cleared margin. This probe asks what that exclusion
means: do Q2/S3 fail under actual-anchor target loss, under hidden-rate views,
or only when converted into the nonlinear public-anchor score?
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

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_lb_actual_anchor_ranker import COMBO_TABLES, combo_weights, load_submission  # noqa: E402
from raw05_anchor_jepa_micro_injection import actual_anchor_score, mask_matrix  # noqa: E402
import gradient_amplitude_translation_probe as e64  # noqa: E402
import gradient_consensus_posterior_probe as e63  # noqa: E402
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "q2_s3_conflict_translator_probe_scan.csv"
PAIR_OUT = OUT / "q2_s3_conflict_translator_probe_pair_decomposition.csv"
TARGET_OUT = OUT / "q2_s3_conflict_translator_probe_target_contribution.csv"
REPORT_OUT = OUT / "q2_s3_conflict_translator_probe_report.md"

RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
STAGE2_FILE = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
EPS = 1e-6

BANDS = ["all", "low_slack_half"]
TARGET_MASKS = {
    "all": TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "no_s3": ["Q1", "Q2", "Q3", "S1", "S2", "S4"],
    "no_q2_s3": ["Q1", "Q3", "S1", "S2", "S4"],
    "q2": ["Q2"],
    "s3": ["S3"],
    "q2_s3": ["Q2", "S3"],
}
BASE_CELL_GATES = ["all", "raw_agree", "support60"]
GRADIENT_GATES = ["grad_core_top50", "grad_all_4of6", "grad_all_abs50"]
ROW_GATES = ["all", "teacher_row_top50"]
CAPS = [0.080, 0.120]
SCALES = [0.070, 0.095, 0.130]
SHAPES = ["flat", "core_gain"]


def clip_prob(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray | float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def stable_tag(arr: np.ndarray, prefix: str = "") -> str:
    return prefix + hashlib.sha1(np.asarray(arr, dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def target_mask(name: str) -> np.ndarray:
    allowed = set(TARGET_MASKS[name])
    return np.asarray([target in allowed for target in TARGETS], dtype=np.float64).reshape(1, -1)


def bce_target(prob: np.ndarray, target_rate: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    y = clip_prob(target_rate)
    return -(y * np.log(p) + (1.0 - y) * np.log1p(-p))


def generate_candidates(
    components: dict[str, dict[str, np.ndarray]],
    raw_prior: np.ndarray,
    mixmin: np.ndarray,
    views: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    base_logit = logit(mixmin)
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()
    for band in BANDS:
        component = components[band]
        teacher_delta = component["delta"]
        base_cell_gates = e58.make_cell_gates(component, raw_prior, mixmin)
        base_row_gates = e58.make_row_gates(component, raw_prior, mixmin)
        grad_cell_gates = e63.gradient_gates(teacher_delta, mixmin, views)
        shape_weights = e64.gradient_gain_shapes(teacher_delta, mixmin, views)
        for target_name in TARGET_MASKS:
            tgate = target_mask(target_name)
            for base_cell_name in BASE_CELL_GATES:
                base_cell = base_cell_gates[base_cell_name]
                for grad_gate_name in GRADIENT_GATES:
                    cell_gate = base_cell * grad_cell_gates[grad_gate_name]
                    if cell_gate.mean() <= 0.0:
                        continue
                    for row_gate_name in ROW_GATES:
                        row_gate = (
                            np.ones((teacher_delta.shape[0], 1), dtype=np.float64)
                            if row_gate_name == "all"
                            else base_row_gates["teacher_row_top50"]
                        )
                        gate = tgate * cell_gate * row_gate
                        active = float(gate.mean())
                        if active <= 0.0:
                            continue
                        for shape_name in SHAPES:
                            shaped_gate = gate * shape_weights[shape_name]
                            for cap in CAPS:
                                capped = np.clip(teacher_delta, -cap, cap) * shaped_gate
                                if np.abs(capped).mean() <= 1e-10:
                                    continue
                                for scale in SCALES:
                                    pred = clip_prob(sigmoid(base_logit + scale * capped))
                                    tag = stable_tag(pred)
                                    if tag in seen:
                                        continue
                                    seen.add(tag)
                                    rows.append(
                                        {
                                            "candidate": (
                                                f"toward_teacher|{band}|{target_name}|{base_cell_name}|"
                                                f"{grad_gate_name}|{row_gate_name}|{shape_name}|s{scale:.3f}|c{cap:.3f}"
                                            ),
                                            "pred_index": len(preds),
                                            "band": band,
                                            "target_mask": target_name,
                                            "base_cell_gate": base_cell_name,
                                            "gradient_gate": grad_gate_name,
                                            "row_gate": row_gate_name,
                                            "shape": shape_name,
                                            "scale": scale,
                                            "cap": cap,
                                            "active_gate_mean": active,
                                            "hash": tag,
                                            "direction": "toward_teacher",
                                        }
                                    )
                                    preds.append(pred)
    return pd.DataFrame(rows), preds


def hidden_target_contrib(prob: np.ndarray, mixmin: np.ndarray, views: dict[str, np.ndarray]) -> dict[str, float]:
    core_names = ["calendar_count_strict", "raw_phone_base", "transition_balanced_hidden_sign", "core_median"]
    all_names = [
        "subject_mean",
        "calendar_count_strict",
        "raw_phone_base",
        "transition_row_safe",
        "transition_balanced_hidden_sign",
        "transition_aggressive_hidden_sign",
        "core_median",
    ]
    out: dict[str, float] = {}
    for target_idx, target in enumerate(TARGETS):
        core_vals = []
        all_vals = []
        for name, rate in views.items():
            delta = float(
                bce_target(prob[:, [target_idx]], rate[:, [target_idx]]).mean()
                - bce_target(mixmin[:, [target_idx]], rate[:, [target_idx]]).mean()
            )
            if name in core_names:
                core_vals.append(delta)
            if name in all_names:
                all_vals.append(delta)
        out[f"hidden_core_delta_{target}"] = float(np.mean(core_vals))
        out[f"hidden_all_delta_{target}"] = float(np.mean(all_vals))
    return out


def anchor_target_contrib(preds: list[np.ndarray], sample: pd.DataFrame, mixmin: np.ndarray) -> pd.DataFrame:
    masks = mask_matrix(sample)
    scenario_cache: dict[str, np.ndarray] = {}
    pred_stack = np.stack(preds, axis=0)
    mix_loss_cache: dict[tuple[str, int], np.ndarray] = {}
    rows = []
    for combo_set, table_name in COMBO_TABLES.items():
        table = pd.read_csv(OUT / table_name).head(160).reset_index(drop=True)
        weights = combo_weights(table)
        values = np.zeros((len(preds), len(TARGETS)), dtype=np.float64)
        for i, row in table.iterrows():
            scenario = str(row["scenario_file"])
            if scenario not in scenario_cache:
                scenario_cache[scenario] = load_submission(scenario, sample)
            q = scenario_cache[scenario]
            mask_idx = int(row["mask_index"])
            mask_vec = masks[mask_idx]
            key = (scenario, mask_idx)
            if key not in mix_loss_cache:
                mix_loss_cache[key] = mask_vec @ bce_target(mixmin, q)
            cand_loss = np.einsum("r,crt->ct", mask_vec, bce_target(pred_stack, q[None, :, :]))
            values += weights[i] * (cand_loss - mix_loss_cache[key])
        for pred_idx in range(len(preds)):
            rec: dict[str, float | int | str] = {"pred_index": pred_idx, "combo_set": combo_set}
            for target_idx, target in enumerate(TARGETS):
                rec[f"anchor_mean_delta_{target}"] = float(values[pred_idx, target_idx] / len(TARGETS))
            rec["anchor_mean_delta_sum"] = float(values[pred_idx].sum() / len(TARGETS))
            rec["anchor_mean_delta_q2_s3"] = float(
                (values[pred_idx, TARGETS.index("Q2")] + values[pred_idx, TARGETS.index("S3")]) / len(TARGETS)
            )
            rows.append(rec)
    long = pd.DataFrame(rows)
    agg = long.groupby("pred_index", as_index=False).mean(numeric_only=True)
    return agg


def base_key_columns() -> list[str]:
    return ["band", "base_cell_gate", "gradient_gate", "row_gate", "shape", "scale", "cap"]


def pair_decomposition(scored: pd.DataFrame) -> pd.DataFrame:
    rows = []
    key_cols = base_key_columns()
    for key, group in scored.groupby(key_cols, dropna=False):
        by_mask = {str(row.target_mask): row for row in group.itertuples(index=False)}
        if "no_q2_s3" not in by_mask:
            continue
        base = by_mask["no_q2_s3"]
        rec: dict[str, Any] = dict(zip(key_cols, key, strict=True))
        rec["base_no_q2_s3_anchor_delta"] = float(base.anchor_delta_vs_mixmin)
        for mask_name in ["all", "no_q2", "no_s3", "q2", "s3", "q2_s3"]:
            if mask_name not in by_mask:
                continue
            row = by_mask[mask_name]
            prefix = f"add_{mask_name}"
            rec[f"{prefix}_anchor_minus_no_q2_s3"] = float(row.anchor_delta_vs_mixmin - base.anchor_delta_vs_mixmin)
            rec[f"{prefix}_mean_anchor_minus_no_q2_s3"] = float(row.mean_actual_anchor - base.mean_actual_anchor)
            rec[f"{prefix}_max_set_minus_no_q2_s3"] = float(row.max_set_score - base.max_set_score)
            rec[f"{prefix}_min_set_minus_no_q2_s3"] = float(row.min_set_score - base.min_set_score)
            rec[f"{prefix}_hidden_core_minus_no_q2_s3"] = float(row.hidden_core_mean_delta - base.hidden_core_mean_delta)
            rec[f"{prefix}_anchor_q2_s3_contrib"] = float(row.anchor_mean_delta_q2_s3)
            rec[f"{prefix}_beats_no_q2_s3"] = bool(row.anchor_delta_vs_mixmin < base.anchor_delta_vs_mixmin)
        rows.append(rec)
    return pd.DataFrame(rows)


def target_response(scored: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for mask_name, group in scored.groupby("target_mask", dropna=False):
        best = group.sort_values("anchor_delta_vs_mixmin").iloc[0]
        rec: dict[str, Any] = {
            "target_mask": mask_name,
            "n": int(len(group)),
            "anchor_beats_mixmin": int((group["anchor_delta_vs_mixmin"] < 0.0).sum()),
            "best_anchor_delta": float(best["anchor_delta_vs_mixmin"]),
            "median_anchor_delta": float(group["anchor_delta_vs_mixmin"].median()),
            "best_hidden_core_delta": float(best["hidden_core_mean_delta"]),
            "median_hidden_core_delta": float(group["hidden_core_mean_delta"].median()),
            "best_anchor_q2_s3_contrib": float(best["anchor_mean_delta_q2_s3"]),
            "median_anchor_q2_s3_contrib": float(group["anchor_mean_delta_q2_s3"].median()),
            "best_candidate": str(best["candidate"]),
        }
        for target in TARGETS:
            rec[f"best_anchor_mean_delta_{target}"] = float(best[f"anchor_mean_delta_{target}"])
            rec[f"best_hidden_core_delta_{target}"] = float(best[f"hidden_core_delta_{target}"])
        rows.append(rec)
    return pd.DataFrame(rows).sort_values(["best_anchor_delta", "target_mask"]).reset_index(drop=True)


def write_report(scored: pd.DataFrame, target_summary: pd.DataFrame, pair_summary: pd.DataFrame) -> None:
    best = scored.sort_values("anchor_delta_vs_mixmin").head(20)
    add_cols = [c for c in pair_summary.columns if c.endswith("_anchor_minus_no_q2_s3")]
    q2_s3_adverse = {
        col: int((pair_summary[col] > 0.0).sum())
        for col in add_cols
    }
    lines = [
        "# E66 Q2/S3 Conflict Translator Probe",
        "",
        "## Observe",
        "",
        "E65's best local response excludes Q2 and S3. That could mean target loss conflict, hidden-view conflict, or nonlinear anchor-score conflict.",
        "",
        "## Wonder",
        "",
        "When the same E56 gradient cell set is held fixed, what exactly happens when Q2 and/or S3 are added back?",
        "",
        "## Method",
        "",
        f"- Generated focused matched-mask candidates: `{len(scored)}`.",
        "- Masks: `all`, `no_q2`, `no_s3`, `no_q2_s3`, `q2`, `s3`, `q2_s3`.",
        "- For each candidate, computed actual-anchor score, actual-anchor target mean contribution, hidden core/all target BCE deltas, and paired same-configuration deltas versus `no_q2_s3`.",
        "",
        "## Target Mask Response",
        "",
        e56.markdown_table(target_summary.head(20)),
        "",
        "## Matched Add-Back Summary",
        "",
        f"- matched base configurations: `{len(pair_summary)}`.",
    ]
    for col, count in q2_s3_adverse.items():
        lines.append(f"- `{col}` adverse count: `{count}/{len(pair_summary)}`.")
    if len(pair_summary):
        if "add_all_mean_anchor_minus_no_q2_s3" in pair_summary.columns:
            mean_improves = int((pair_summary["add_all_mean_anchor_minus_no_q2_s3"] < 0.0).sum())
            maxset_worse = int((pair_summary["add_all_max_set_minus_no_q2_s3"] > 0.0).sum())
            minset_better = int((pair_summary["add_all_min_set_minus_no_q2_s3"] < 0.0).sum())
            lines.extend(
                [
                    f"- `add_all` mean-anchor improves: `{mean_improves}/{len(pair_summary)}`.",
                    f"- `add_all` max-set tail worsens: `{maxset_worse}/{len(pair_summary)}`.",
                    f"- `add_all` min-set tail improves: `{minset_better}/{len(pair_summary)}`.",
                ]
            )
        show_cols = base_key_columns() + [
            "base_no_q2_s3_anchor_delta",
            "add_all_anchor_minus_no_q2_s3",
            "add_all_mean_anchor_minus_no_q2_s3",
            "add_all_max_set_minus_no_q2_s3",
            "add_no_q2_anchor_minus_no_q2_s3",
            "add_no_s3_anchor_minus_no_q2_s3",
            "add_q2_s3_anchor_minus_no_q2_s3",
            "add_all_hidden_core_minus_no_q2_s3",
        ]
        lines.extend(["", e56.markdown_table(pair_summary[[c for c in show_cols if c in pair_summary.columns]].sort_values("add_all_anchor_minus_no_q2_s3").head(20))])
    top_cols = [
        "candidate",
        "target_mask",
        "anchor_delta_vs_mixmin",
        "anchor_mean_delta_q2_s3",
        "hidden_core_mean_delta",
        "hidden_core_delta_Q2",
        "hidden_core_delta_S3",
        "mean_abs_logit_move_vs_mixmin",
    ]
    lines.extend(
        [
            "",
            "## Top Candidates",
            "",
            e56.markdown_table(best[[c for c in top_cols if c in best.columns]]),
            "",
            "## Decision",
            "",
            "- E66 is an audit, not a submission generator.",
            "- If Q2/S3 add-back is consistently actual-anchor adverse while hidden deltas remain favorable, the next translator must model target-specific public calibration rather than hidden direction.",
            "- If Q2/S3 are also hidden-adverse, the E56 teacher cell set itself must be redefined for those targets.",
            "",
            "## Outputs",
            "",
            f"- `{SCAN_OUT.relative_to(ROOT)}`",
            f"- `{PAIR_OUT.relative_to(ROOT)}`",
            f"- `{TARGET_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    mixmin = load_sub(e56.MIXMIN_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    a2c8 = load_sub(A2C8, sample)[TARGETS].to_numpy(dtype=np.float64)
    raw05 = load_sub(RAW05_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    raw_prior, _ = e56.raw_prior_from_e54(sample)
    labels = np.load(e56.LABEL_NPZ_OUT, allow_pickle=True)["labels"].astype(np.float64)
    worlds = pd.read_csv(e56.WORLD_OUT)
    state = e55.build_base_state()
    if not state.sample[KEYS].reset_index(drop=True).equals(sample[KEYS].reset_index(drop=True)):
        raise ValueError("sample key mismatch between anchor sample and hidden-rate state")

    views, _ = e63.hidden_row_views(state, sample, mixmin, a2c8)
    components = e58.posterior_components(labels, worlds, raw_prior, mixmin)
    rows, preds = generate_candidates(components, raw_prior, mixmin, views)
    scored = e58.score_prefilter(rows, preds, labels, worlds, mixmin)
    hidden_rows = [e63.hidden_validation_scores(preds[int(row.pred_index)], mixmin, views) for row in scored.itertuples(index=False)]
    hidden_target_rows = [hidden_target_contrib(preds[int(row.pred_index)], mixmin, views) for row in scored.itertuples(index=False)]
    scored = pd.concat(
        [scored.reset_index(drop=True), pd.DataFrame(hidden_rows), pd.DataFrame(hidden_target_rows)],
        axis=1,
    )
    anchor = actual_anchor_score([mixmin, a2c8, raw05] + [preds[int(i)] for i in scored["pred_index"]], sample)
    mixmin_anchor = float(anchor.iloc[0]["actual_anchor_score_final"])
    cand_anchor = anchor.iloc[3:].reset_index(drop=True)
    scored["actual_anchor_score_final"] = cand_anchor["actual_anchor_score_final"].to_numpy(dtype=np.float64)
    scored["anchor_delta_vs_mixmin"] = scored["actual_anchor_score_final"] - mixmin_anchor
    scored["mean_actual_anchor"] = cand_anchor["mean_actual_anchor"].to_numpy(dtype=np.float64)
    scored["min_set_score"] = cand_anchor["min_set_score"].to_numpy(dtype=np.float64)
    scored["max_set_score"] = cand_anchor["max_set_score"].to_numpy(dtype=np.float64)
    scored["anchor_beats_mixmin"] = scored["anchor_delta_vs_mixmin"] < 0.0
    target_contrib = anchor_target_contrib([preds[int(i)] for i in scored["pred_index"]], sample, mixmin)
    target_contrib = target_contrib.drop(columns=["pred_index"]).reset_index(drop=True)
    scored = pd.concat([scored.reset_index(drop=True), target_contrib], axis=1)
    scored = scored.sort_values("anchor_delta_vs_mixmin").reset_index(drop=True)
    scored.to_csv(SCAN_OUT, index=False)
    target_summary = target_response(scored)
    pair_summary = pair_decomposition(scored).sort_values("add_all_anchor_minus_no_q2_s3").reset_index(drop=True)
    target_summary.to_csv(TARGET_OUT, index=False)
    pair_summary.to_csv(PAIR_OUT, index=False)
    write_report(scored, target_summary, pair_summary)

    best = scored.iloc[0]
    print(
        f"generated={len(rows)} scored={len(scored)} best={best['target_mask']} "
        f"best_delta={best['anchor_delta_vs_mixmin']:.6g} "
        f"pairs={len(pair_summary)} wrote={REPORT_OUT.relative_to(ROOT)}"
    )
    print(target_summary[["target_mask", "n", "best_anchor_delta", "median_anchor_delta", "best_anchor_q2_s3_contrib"]].to_string(index=False))


if __name__ == "__main__":
    main()
