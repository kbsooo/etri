#!/usr/bin/env python3
"""E95 hard-tail gate scan.

E94 explained why E72 can look healthy under soft representation metrics while
still missing public: a small hard-label LogLoss tail is enough. This follow-up
asks whether that tail signal can become an actionable gate, or whether it only
relabels the E89/E90 tradeoff we already found.

No public labels are fitted. The only public use is the already-observed E72
miss, converted into an adverse hard-label direction per cell.
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
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e89_e86_e72_decontamination_scan as e89  # noqa: E402
import e94_soft_health_hard_tail_audit as e94  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402


MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
E72_FILE = "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
E85_FILE = "submission_e85_inverse_conflict_pruned_58b23ed1.csv"
E86_FILE = "submission_e86_e85_consensus_a3f7c96f.csv"
E89_FILE = "submission_e89_e72decontam_00d7807f.csv"
E90_FILE = "submission_e90_e72pareto_28925de5.csv"
NOQ2_FILE = "submission_e87_noq2_source_consensus_a85c4e39.csv"

SCAN_OUT = OUT / "e95_hard_tail_gate_scan.csv"
SUMMARY_OUT = OUT / "e95_hard_tail_gate_summary.csv"
REPORT_OUT = OUT / "e95_hard_tail_gate_report.md"
SUBMISSION_PREFIX = "submission_e95_hardtail"

EPS = 1.0e-6
Q2 = TARGETS.index("Q2")
S1 = TARGETS.index("S1")
S2 = TARGETS.index("S2")
S3 = TARGETS.index("S3")
LIVE_TARGETS = [Q2, S1, S2, S3]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def load_pred(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64)


def e72_adverse_setup(base: np.ndarray, e72: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    e72_delta = logit(e72) - logit(base)
    e72_weight = np.abs(e72_delta)
    wrong_is_zero = e72_delta > 1.0e-9
    wrong_is_one = e72_delta < -1.0e-9
    return e72_delta, e72_weight, wrong_is_zero, wrong_is_one


def hard_tail_map(
    pred: np.ndarray,
    base: np.ndarray,
    wrong_is_zero: np.ndarray,
    wrong_is_one: np.ndarray,
) -> np.ndarray:
    d0, d1 = e94.hard_loss_deltas(pred, base)
    adverse = np.where(wrong_is_zero, d0, np.where(wrong_is_one, d1, 0.0))
    return np.maximum(adverse, 0.0)


def hard_tail_metrics(
    pred: np.ndarray,
    base: np.ndarray,
    e72_weight: np.ndarray,
    wrong_is_zero: np.ndarray,
    wrong_is_one: np.ndarray,
) -> dict[str, float]:
    d0, d1 = e94.hard_loss_deltas(pred, base)
    adverse = np.where(wrong_is_zero, d0, np.where(wrong_is_one, d1, 0.0))
    positive = np.maximum(adverse, 0.0)
    hard_worst = np.maximum(d0, d1)
    kl_base = base * d1 + (1.0 - base) * d0
    return {
        "e72_adverse_positive_exposure_all": float(np.mean(positive)),
        "e72_adverse_weighted_positive_mean": e94.safe_weighted_mean(positive, e72_weight),
        "e72_adverse_positive_weight_frac": e94.safe_weighted_mean((adverse > 0).astype(float), e72_weight),
        "hard_worst_tail_mean": float(np.mean(hard_worst)),
        "kl_if_mixmin_calibrated": float(np.mean(kl_base)),
    }


def high_mask(values: np.ndarray, q: float) -> np.ndarray:
    flat = np.asarray(values, dtype=np.float64).reshape(-1)
    cut = float(np.quantile(flat, q))
    return np.asarray(values, dtype=np.float64) >= cut


def positive_high_mask(values: np.ndarray, q: float) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    positive = arr[arr > 1.0e-12]
    if len(positive) == 0:
        return np.zeros_like(arr, dtype=bool)
    cut = float(np.quantile(positive, q))
    return arr >= cut


def pred_key(pred: np.ndarray) -> str:
    rounded = np.round(np.asarray(pred, dtype=np.float64), 12)
    return hashlib.sha256(rounded.tobytes()).hexdigest()


def target_scope_mask(n_rows: int, scope: str) -> np.ndarray:
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    if scope == "all":
        mask[:, :] = True
    elif scope == "live_q2s1s2s3":
        mask[:, LIVE_TARGETS] = True
    elif scope == "s1s2s3":
        mask[:, [S1, S2, S3]] = True
    elif scope == "q2":
        mask[:, [Q2]] = True
    elif scope == "s3":
        mask[:, [S3]] = True
    elif scope == "q2s3":
        mask[:, [Q2, S3]] = True
    else:
        raise KeyError(scope)
    return mask


def add_pred(
    rows: list[dict[str, Any]],
    preds: list[np.ndarray],
    seen: dict[str, int],
    seen_pred: dict[str, int],
    pred: np.ndarray,
    rec: dict[str, Any],
    base_index: int = 0,
) -> None:
    tag = e83.stable_tag(pred, f"e95_{rec['strategy']}_")
    key = pred_key(pred)
    if key in seen_pred:
        pred_index = seen_pred[key]
    else:
        pred_index = len(preds)
        seen_pred[key] = pred_index
        preds.append(pred)
    seen.setdefault(tag, pred_index)
    rows.append({"pred_index": pred_index, "base_index": base_index, "tag": tag, **rec})


def build_candidates(sample: pd.DataFrame) -> tuple[pd.DataFrame, list[np.ndarray], np.ndarray, dict[str, np.ndarray], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    mixmin = load_pred(MIXMIN_FILE, sample)
    e72 = load_pred(E72_FILE, sample)
    refs = {
        "e85": load_pred(E85_FILE, sample),
        "e86": load_pred(E86_FILE, sample),
        "e89": load_pred(E89_FILE, sample),
        "e90": load_pred(E90_FILE, sample),
        "noq2": load_pred(NOQ2_FILE, sample),
    }
    e72_delta, e72_weight, wrong_is_zero, wrong_is_one = e72_adverse_setup(mixmin, e72)

    mix_logit = logit(mixmin)
    ref_logit = {name: logit(pred) for name, pred in refs.items()}
    deltas = {name: ref_logit[name] - mix_logit for name in refs}
    e86_tail = hard_tail_map(refs["e86"], mixmin, wrong_is_zero, wrong_is_one)
    e90_tail = hard_tail_map(refs["e90"], mixmin, wrong_is_zero, wrong_is_one)
    e89_tail = hard_tail_map(refs["e89"], mixmin, wrong_is_zero, wrong_is_one)

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = [mixmin]
    seen: dict[str, int] = {e83.stable_tag(mixmin, "e95_mixmin_"): 0}
    seen_pred: dict[str, int] = {pred_key(mixmin): 0}

    for name, pred in refs.items():
        add_pred(rows, preds, seen, seen_pred, pred, {"strategy": "control", "source": name})

    # Blend controls ask whether the hard-tail tradeoff is scalar or local.
    for w in [0.20, 0.35, 0.50, 0.65, 0.80]:
        delta = w * deltas["e86"] + (1.0 - w) * deltas["e89"]
        pred = clip_prob(sigmoid(mix_logit + delta))
        add_pred(
            rows,
            preds,
            seen,
            seen_pred,
            pred,
            {"strategy": "blend_e86_e89", "source": "e86", "fallback": "e89", "blend_e86_weight": w},
        )

    for w in [0.25, 0.50, 0.75]:
        delta = w * deltas["e90"] + (1.0 - w) * deltas["e89"]
        pred = clip_prob(sigmoid(mix_logit + delta))
        add_pred(
            rows,
            preds,
            seen,
            seen_pred,
            pred,
            {"strategy": "blend_e90_e89", "source": "e90", "fallback": "e89", "blend_e90_weight": w},
        )

    fallback_names = ["e89", "e85", "mixmin"]
    scopes = ["all", "live_q2s1s2s3", "s1s2s3", "q2s3", "s3"]
    for source_name, source_tail, quantiles in [
        ("e86", e86_tail, [0.50, 0.60, 0.70, 0.80, 0.90]),
        ("e90", e90_tail, [0.60, 0.70, 0.80, 0.90]),
    ]:
        source_tail_row = source_tail.mean(axis=1)
        for q in quantiles:
            cell_tail_mask = positive_high_mask(source_tail, q)
            row_tail_mask = positive_high_mask(source_tail_row, q)[:, None]
            for fallback in fallback_names:
                fallback_delta = np.zeros_like(deltas[source_name]) if fallback == "mixmin" else deltas[fallback]
                for scope in scopes:
                    smask = target_scope_mask(len(sample), scope)
                    cell_mask = cell_tail_mask & smask
                    if not np.any(cell_mask):
                        continue
                    delta = np.where(cell_mask, fallback_delta, deltas[source_name])
                    pred = clip_prob(sigmoid(mix_logit + delta))
                    add_pred(
                        rows,
                        preds,
                        seen,
                        seen_pred,
                        pred,
                        {
                            "strategy": "cell_hardtail_fallback",
                            "source": source_name,
                            "fallback": fallback,
                            "tail_quantile": q,
                            "target_scope": scope,
                        },
                    )

                    row_mask = row_tail_mask & smask
                    if np.any(row_mask):
                        delta = np.where(row_mask, fallback_delta, deltas[source_name])
                        pred = clip_prob(sigmoid(mix_logit + delta))
                        add_pred(
                            rows,
                            preds,
                            seen,
                            seen_pred,
                            pred,
                            {
                                "strategy": "row_hardtail_fallback",
                                "source": source_name,
                                "fallback": fallback,
                                "tail_quantile": q,
                                "target_scope": scope,
                            },
                        )

    return pd.DataFrame(rows).drop_duplicates("tag").reset_index(drop=True), preds, mixmin, refs, (
        e72_delta,
        e72_weight,
        wrong_is_zero,
        wrong_is_one,
    )


def add_tail_metrics(
    scan: pd.DataFrame,
    preds: list[np.ndarray],
    mixmin: np.ndarray,
    tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> pd.DataFrame:
    _, e72_weight, wrong_is_zero, wrong_is_one = tail_state
    rows = []
    for idx, pred in enumerate(preds):
        rows.append({"pred_index": idx, **hard_tail_metrics(pred, mixmin, e72_weight, wrong_is_zero, wrong_is_one)})
    return scan.merge(pd.DataFrame(rows), on="pred_index", how="left")


def add_movement_metrics(scan: pd.DataFrame, preds: list[np.ndarray], mixmin: np.ndarray) -> pd.DataFrame:
    rows = []
    base_logit = logit(mixmin)
    for idx, pred in enumerate(preds):
        delta = logit(pred) - base_logit
        active = np.abs(delta) > 1.0e-9
        rows.append(
            {
                "pred_index": idx,
                "mean_abs_logit_move_vs_mixmin": float(np.mean(np.abs(delta))),
                "max_abs_logit_move_vs_mixmin": float(np.max(np.abs(delta))),
                "moved_cells_vs_mixmin": int(np.sum(active)),
                "moved_rows_vs_mixmin": int(np.sum(active.any(axis=1))),
                "active_targets_vs_mixmin": ",".join(
                    target for target, is_active in zip(TARGETS, active.any(axis=0)) if is_active
                ),
            }
        )
    movement = pd.DataFrame(rows)
    duplicate_cols = [col for col in movement.columns if col != "pred_index" and col in scan.columns]
    if duplicate_cols:
        movement = movement.drop(columns=duplicate_cols)
    return scan.merge(movement, on="pred_index", how="left")


def add_pareto_flags(scan: pd.DataFrame) -> pd.DataFrame:
    out = scan.copy()
    controls = out[out["strategy"].eq("control")].copy()
    e86 = controls[controls["source"].eq("e86")].iloc[0]
    e90 = controls[controls["source"].eq("e90")].iloc[0]
    e89 = controls[controls["source"].eq("e89")].iloc[0]
    e85 = controls[controls["source"].eq("e85")].iloc[0]

    out["tail_reduction_vs_e86"] = (
        float(e86["e72_adverse_positive_exposure_all"]) - out["e72_adverse_positive_exposure_all"]
    )
    out["tail_reduction_vs_e90"] = (
        float(e90["e72_adverse_positive_exposure_all"]) - out["e72_adverse_positive_exposure_all"]
    )
    out["tail_reduction_vs_e89"] = (
        float(e89["e72_adverse_positive_exposure_all"]) - out["e72_adverse_positive_exposure_all"]
    )
    out["margin_loss_vs_e86"] = out["all_delta_vs_mixmin"] - float(e86["all_delta_vs_mixmin"])
    out["margin_gain_vs_e89"] = float(e89["all_delta_vs_mixmin"]) - out["all_delta_vs_mixmin"]
    out["beats_e90_tail_and_margin"] = (
        out["e72_adverse_positive_exposure_all"].lt(float(e90["e72_adverse_positive_exposure_all"]))
        & out["all_delta_vs_mixmin"].lt(float(e90["all_delta_vs_mixmin"]))
    )
    out["beats_e89_tail_and_margin"] = (
        out["e72_adverse_positive_exposure_all"].lt(float(e89["e72_adverse_positive_exposure_all"]))
        & out["all_delta_vs_mixmin"].lt(float(e89["all_delta_vs_mixmin"]))
    )
    out["beats_e85_tail_and_margin"] = (
        out["e72_adverse_positive_exposure_all"].lt(float(e85["e72_adverse_positive_exposure_all"]))
        & out["all_delta_vs_mixmin"].lt(float(e85["all_delta_vs_mixmin"]))
    )
    out["strict_nondominated_vs_e89_e90"] = (
        out["strict_gate"].fillna(False).astype(bool)
        & ~out["strategy"].eq("control")
        & (
            out["beats_e90_tail_and_margin"]
            | out["beats_e89_tail_and_margin"]
            | out["beats_e85_tail_and_margin"]
        )
    )
    return out


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    group_cols = ["strategy", "source", "fallback", "target_scope", "tail_quantile"]
    for keys, group in scan.groupby(group_cols, dropna=False):
        evaluated = group[group["nonanchor_evaluated"].fillna(False).astype(bool)]
        strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)]
        best_tail = group.sort_values(["e72_adverse_positive_exposure_all", "all_delta_vs_mixmin"]).iloc[0]
        best_margin = group.sort_values(["all_delta_vs_mixmin", "e72_adverse_positive_exposure_all"]).iloc[0]
        best_strict_tail = strict.sort_values(
            ["e72_adverse_positive_exposure_all", "all_delta_vs_mixmin"]
        ).iloc[0] if len(strict) else None
        rows.append(
            {
                **dict(zip(group_cols, keys)),
                "rows": int(len(group)),
                "evaluated": int(len(evaluated)),
                "strict": int(len(strict)),
                "nondominated": int(group["strict_nondominated_vs_e89_e90"].sum()),
                "best_tail": float(best_tail["e72_adverse_positive_exposure_all"]),
                "best_tail_all_delta": float(best_tail["all_delta_vs_mixmin"]),
                "best_strict_tail": float(best_strict_tail["e72_adverse_positive_exposure_all"])
                if best_strict_tail is not None
                else np.nan,
                "best_strict_tail_all_delta": float(best_strict_tail["all_delta_vs_mixmin"])
                if best_strict_tail is not None
                else np.nan,
                "best_margin": float(best_margin["all_delta_vs_mixmin"]),
                "best_margin_tail": float(best_margin["e72_adverse_positive_exposure_all"]),
                "best_world": float(evaluated["world_support_minus_base"].min()) if len(evaluated) else np.nan,
                "best_hidden_q2s3": float(evaluated["hidden_q2s3_mean_minus_base"].min()) if len(evaluated) else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["nondominated", "strict", "best_strict_tail", "best_margin"],
        ascending=[False, False, True, True],
    )


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = scan[scan["strict_nondominated_vs_e89_e90"].fillna(False).astype(bool)].copy()
    if eligible.empty:
        return None
    selected = eligible.sort_values(
        [
            "beats_e89_tail_and_margin",
            "beats_e90_tail_and_margin",
            "e72_adverse_positive_exposure_all",
            "all_delta_vs_mixmin",
        ],
        ascending=[False, False, True, True],
    ).iloc[0]
    out = sample[KEYS].copy()
    out[TARGETS] = preds[int(selected["pred_index"])]
    path = OUT / f"{SUBMISSION_PREFIX}_{str(selected['tag'])[-8:]}.csv"
    out.to_csv(path, index=False)
    return path


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, submission_path: Path | None) -> None:
    controls = scan[scan["strategy"].eq("control")].copy()
    candidates = scan[~scan["strategy"].eq("control")].copy()
    strict = candidates[candidates["strict_gate"].fillna(False).astype(bool)].copy()
    nondom = candidates[candidates["strict_nondominated_vs_e89_e90"].fillna(False).astype(bool)].copy()

    cols = [
        "strategy",
        "source",
        "fallback",
        "target_scope",
        "tail_quantile",
        "all_delta_vs_mixmin",
        "e72_adverse_positive_exposure_all",
        "tail_reduction_vs_e86",
        "tail_reduction_vs_e90",
        "tail_reduction_vs_e89",
        "world_support_minus_base",
        "hidden_q2s3_mean_minus_base",
        "block_q2s3_beats_base_rate",
        "block_q2s3_tail_safe_rate",
        "mean_abs_logit_move_vs_mixmin",
        "moved_cells_vs_mixmin",
        "active_targets_vs_mixmin",
        "strict_gate",
        "beats_e90_tail_and_margin",
        "beats_e89_tail_and_margin",
        "tag",
    ]
    lines = [
        "# E95 Hard-Tail Gate Scan",
        "",
        "## Question",
        "",
        "Can E94 hard-label tail exposure become an actionable gate that creates a new non-dominated successor to E86/E90/E89, or does it only restate the existing E89/E90 tradeoff?",
        "",
        "## Method",
        "",
        "- Use mixmin as base and E72 as the known public-negative hard-tail direction.",
        "- Generate only controlled candidates: E86/E90 hard-tail row or cell fallback to E89, E85, or mixmin, plus scalar blends.",
        "- Score with the same combo, hidden/world/block, raw-energy, and strict gates used by E89/E90.",
        "- Promote a file only if a non-control row is strict and non-dominated on both hard-tail exposure and local margin versus E89/E90/E85.",
        "- Report both raw best-tail and strict best-tail because broad fallback to mixmin can look tail-perfect while failing the structural stress gate.",
        "",
        "## Controls",
        "",
        e94.md_table(
            controls[
                [
                    "source",
                    "all_delta_vs_mixmin",
                    "e72_adverse_positive_exposure_all",
                    "world_support_minus_base",
                    "hidden_q2s3_mean_minus_base",
                    "block_q2s3_beats_base_rate",
                    "block_q2s3_tail_safe_rate",
                    "strict_gate",
                ]
            ],
        ),
        "",
        "## Summary",
        "",
        e56.markdown_table(summary.head(40)),
        "",
        "## Best Strict Non-Control Rows By Tail",
        "",
        e56.markdown_table(strict.sort_values(["e72_adverse_positive_exposure_all", "all_delta_vs_mixmin"])[cols].head(40))
        if len(strict)
        else "None.",
        "",
        "## Non-Dominated Rows",
        "",
        e56.markdown_table(nondom.sort_values(["e72_adverse_positive_exposure_all", "all_delta_vs_mixmin"])[cols])
        if len(nondom)
        else "None.",
        "",
        "## Decision",
        "",
    ]
    if submission_path is None:
        lines += [
            "No E95 submission was materialized.",
            "",
            "The hard-tail gate is useful as a risk lens, but under the current strict stress it does not produce a new candidate that dominates E89/E90/E85 on tail and margin. Keep E86/E90/E89 as separate public sensors rather than replacing them with a derived hard-tail blend.",
        ]
    else:
        lines += [
            f"Materialized hard-tail gated candidate: `{submission_path.name}`.",
            "",
            "This file should be read as a direct test that E94's hard-label tail localization adds information beyond the earlier E89/E90 decontamination gates.",
        ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    rows, preds, mixmin, _, tail_state = build_candidates(sample)
    labels, worlds, views, state = e89.build_stress_state(sample, mixmin)
    scan = e83.score_candidate_rows(rows, preds, sample, mixmin, labels, worlds, views, state)
    scan = add_tail_metrics(scan, preds, mixmin, tail_state)
    scan = add_movement_metrics(scan, preds, mixmin)
    scan = add_pareto_flags(scan)
    summary = summarize(scan)
    submission_path = materialize(scan, preds, sample)
    scan["materialized_submission"] = False
    if submission_path is not None:
        scan["materialized_submission"] = scan["tag"].astype(str).str.endswith(submission_path.stem.split("_")[-1])

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scan, summary, submission_path)

    controls = scan[scan["strategy"].eq("control")]
    print(
        {
            "rows": int(len(scan)),
            "evaluated": int(scan["nonanchor_evaluated"].fillna(False).sum()),
            "strict": int(scan["strict_gate"].fillna(False).sum()),
            "nondominated": int(scan["strict_nondominated_vs_e89_e90"].fillna(False).sum()),
            "best_noncontrol_tail": float(
                scan[~scan["strategy"].eq("control")]["e72_adverse_positive_exposure_all"].min()
            ),
            "best_strict_noncontrol_tail": float(
                scan[
                    ~scan["strategy"].eq("control")
                    & scan["strict_gate"].fillna(False).astype(bool)
                ]["e72_adverse_positive_exposure_all"].min()
            ),
            "control_tail": {
                str(row["source"]): float(row["e72_adverse_positive_exposure_all"])
                for row in controls.to_dict("records")
            },
            "submission": str(submission_path) if submission_path is not None else None,
        }
    )


if __name__ == "__main__":
    main()
