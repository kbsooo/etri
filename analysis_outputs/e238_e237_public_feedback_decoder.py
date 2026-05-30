#!/usr/bin/env python3
"""E238: pre-public feedback decoder for the E237 cell-level JEPA candidate.

E237 is the first learned Q3 cell-tail intervention that survives the current
public-free stress stack. This script does not train a model and does not
create a submission. It fixes how a future public LB for the top E237 file
should be interpreted before the score is known.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402


E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405
E216_PUBLIC = 0.5772865088

E95_DELTA_VS_MIXMIN = E95_PUBLIC - MIXMIN_PUBLIC
E101_DELTA_VS_E95 = E101_PUBLIC - E95_PUBLIC
MIXMIN_DELTA_VS_E95 = MIXMIN_PUBLIC - E95_PUBLIC

E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E224_FILE = "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"
E230_SWING25_FILE = "submission_e230_q3_swingtop25_drop_e0918606.csv"
E230_RISK21_FILE = "submission_e230_q3_risktop21_drop_7d95c14a.csv"
E230_RISK13_FILE = "submission_e230_q3_risktop13_drop_9704f7c9.csv"
E237_FILE = (
    "submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_"
    "risk_q0p10_drop_q3_top25_426424f2.csv"
)

E224_SELECTED = OUT / "e224_e211_q3_scale_pareto_selected.csv"
E230_SELECTED = OUT / "e230_e224_support_tail_prune_audit_selected.csv"
E237_SELECTED = OUT / "e237_cell_decisive_jepa_target_selected.csv"

ROUTEBOOK_OUT = OUT / "e238_e237_public_feedback_decoder_routebook.csv"
CONTRAST_OUT = OUT / "e238_e237_public_feedback_decoder_e224_contrast_routebook.csv"
EXAMPLES_OUT = OUT / "e238_e237_public_feedback_decoder_examples.csv"
PAIRWISE_OUT = OUT / "e238_e237_public_feedback_decoder_pairwise.csv"
TARGET_OUT = OUT / "e238_e237_public_feedback_decoder_target_anatomy.csv"
OVERLAP_OUT = OUT / "e238_e237_public_feedback_decoder_cell_overlap.csv"
METRICS_OUT = OUT / "e238_e237_public_feedback_decoder_candidate_metrics.csv"
REPORT_OUT = OUT / "e238_e237_public_feedback_decoder_report.md"
SELECTED_OUT = OUT / "e238_e237_public_feedback_decoder_selected.json"

EPS = 1.0e-12


BANDS: list[dict[str, Any]] = [
    {
        "outcome": "cell_tail_breakthrough",
        "delta_lo_exclusive": -np.inf,
        "delta_hi_inclusive": -3.0e-5,
        "world_update_class": "strong_support",
        "hidden_world_update": "E237 wins beyond normal post-E95 edge scale. The learned Q3 decisive-cell target likely captured a real public-tail law.",
        "next_action": "Do not tune a lower-ranked E237 sibling. First compare against E224 if available, then audit which Q3 cells carried the gain.",
        "candidate_to_test": "conditional:e237_component_attribution_or_e224_contrast",
        "forbidden_action": "Do not scale the cell gate or add S4 drops from the same family before attribution.",
        "strengthened": "H232 Q3 cell-level decisive tail; learned JEPA target usefulness",
        "weakened": "E236 row-level failure as evidence against learned Q3 tail",
    },
    {
        "outcome": "clean_win",
        "delta_lo_exclusive": -3.0e-5,
        "delta_hi_inclusive": E95_DELTA_VS_MIXMIN,
        "world_update_class": "support",
        "hidden_world_update": "E237 beats E95 by at least the E95-over-mixmin edge. The combined capped-Q3/S4 body plus learned Q3 cell prune is public-readable.",
        "next_action": "Promote E237 as the learned-Q3-tail anchor. Submit E224 only if the explicit next question is how much the learned prune contributed.",
        "candidate_to_test": f"analysis_outputs/{E224_FILE}",
        "forbidden_action": "Do not submit E230 hand-prune as an automatic victory lap; E237 specifically validates learned cell selection.",
        "strengthened": "learned Q3 cell-tail translator",
        "weakened": "hand-prune-only interpretation",
    },
    {
        "outcome": "micro_win",
        "delta_lo_exclusive": E95_DELTA_VS_MIXMIN,
        "delta_hi_inclusive": -3.0e-6,
        "world_update_class": "weak_support",
        "hidden_world_update": "E237 is public-positive but at one/few-cell scale. The cell-tail law is alive but underresolved.",
        "next_action": "Keep E237 as preferred learned-JEPA sensor, but wait for E224/E230 contrast or exact-score cell attribution before siblings.",
        "candidate_to_test": "conditional:e237_exact_cell_attribution",
        "forbidden_action": "Do not tune top-k from a micro-win.",
        "strengthened": "Q3 cell-tail direction",
        "weakened": "broad JEPA breakthrough claim",
    },
    {
        "outcome": "tie",
        "delta_lo_exclusive": -3.0e-6,
        "delta_hi_inclusive": 3.0e-6,
        "world_update_class": "underresolved",
        "hidden_world_update": "E237 does not separate from E95. The learned Q3 prune may be correct but not readable without E224 contrast.",
        "next_action": "Do not submit lower-ranked E237 files. If E224 is untested, E224 becomes the cleaner contrast; otherwise compare E237-E224.",
        "candidate_to_test": f"analysis_outputs/{E224_FILE}",
        "forbidden_action": "Do not infer top25 is too many or too few from a tie.",
        "strengthened": "frontier hard-label-resolution law",
        "weakened": "E237 expected-score claim",
    },
    {
        "outcome": "small_loss",
        "delta_lo_exclusive": 3.0e-6,
        "delta_hi_inclusive": E101_DELTA_VS_E95,
        "world_update_class": "weak_rejection",
        "hidden_world_update": "E237 loses to E95 but no worse than E101. The learned cell prune is not public-positive on its own, but the JEPA branch is not hard-rejected.",
        "next_action": "Use E224-vs-E237 contrast if E224 is known. If E224 is unknown, do not choose E230/E237 siblings until the loss is attributed.",
        "candidate_to_test": "conditional:e224_or_loss_attribution",
        "forbidden_action": "Do not rescue by dropping more Q3 cells.",
        "strengthened": "support-tail skepticism",
        "weakened": "E237 as next expected-score file",
    },
    {
        "outcome": "mixmin_safe_loss",
        "delta_lo_exclusive": E101_DELTA_VS_E95,
        "delta_hi_inclusive": MIXMIN_DELTA_VS_E95,
        "world_update_class": "rejection",
        "hidden_world_update": "E237 is worse than E101 but still mixmin-safe. The learned Q3 tail helps locally but likely misses public support geometry.",
        "next_action": "Demote E237 siblings. Keep E224 only as a clean diagnostic or move to E166/E154 branch depending on the next hidden-world question.",
        "candidate_to_test": "conditional:e166_or_e154_or_e224_diagnostic",
        "forbidden_action": "Do not submit top13/top10 E237 as scalar variants.",
        "strengthened": "learned-tail translation bottleneck",
        "weakened": "H232 as public-safe submission law",
    },
    {
        "outcome": "branch_loss",
        "delta_lo_exclusive": MIXMIN_DELTA_VS_E95,
        "delta_hi_inclusive": 5.0e-5,
        "world_update_class": "strong_rejection",
        "hidden_world_update": "E237 gives back the frontier edge. The learned Q3 cell law is not the public-tail law at this frontier scale.",
        "next_action": "Close E237 siblings as expected-score candidates. Use E166 for independent broad-world testing or E154 for repaired-branch testing.",
        "candidate_to_test": "conditional:e166_or_e154",
        "forbidden_action": "Do not switch to hand E230 solely because learned E237 failed; first decide whether E224 body or Q3 prune caused the miss.",
        "strengthened": "public-tail mismatch",
        "weakened": "learned Q3 cell-tail translator",
    },
    {
        "outcome": "hard_fail",
        "delta_lo_exclusive": 5.0e-5,
        "delta_hi_inclusive": 3.0e-4,
        "world_update_class": "hard_rejection",
        "hidden_world_update": "E237 is strongly public-incompatible. This is not a one-cell fluctuation.",
        "next_action": "Run miss anatomy before any further E224/E230/E237 family submission.",
        "candidate_to_test": "conditional:e237_public_miss_anatomy",
        "forbidden_action": "Do not submit any same-family Q3 top-k sibling.",
        "strengthened": "LeJEPA shortcut warning",
        "weakened": "current Q3/S4 JEPA translator family",
    },
    {
        "outcome": "e216_like_fail",
        "delta_lo_exclusive": 3.0e-4,
        "delta_hi_inclusive": np.inf,
        "world_update_class": "translator_collapse",
        "hidden_world_update": "E237 fails on the same order as bad JEPA translators. The public-facing translator is shortcut-aligned despite OOF and local stress.",
        "next_action": "Treat E237 as a root-cause failure. Rebuild the target representation rather than tuning a cell threshold.",
        "candidate_to_test": "conditional:root_cause_rebuild",
        "forbidden_action": "Do not submit E224, E230, or any E237 sibling before miss anatomy.",
        "strengthened": "JEPA probability movement unsafe",
        "weakened": "all current E224/E230/E237 family submissions",
    },
]


CONTRAST_BANDS: list[dict[str, Any]] = [
    {
        "outcome": "e237_beats_e224_readably",
        "delta_lo_exclusive": -np.inf,
        "delta_hi_inclusive": -1.0e-5,
        "contrast_update": "The learned Q3 cell-prune adds public value beyond the clean E224 body.",
        "next_action": "Promote E237 over E224; use E230 only as a hand-prune control.",
    },
    {
        "outcome": "e237_beats_e224_micro",
        "delta_lo_exclusive": -1.0e-5,
        "delta_hi_inclusive": -3.0e-6,
        "contrast_update": "The learned prune helps, but only at hard-label-resolution scale.",
        "next_action": "Keep E237 as preferred learned sensor; do not tune top-k without attribution.",
    },
    {
        "outcome": "e237_e224_tie",
        "delta_lo_exclusive": -3.0e-6,
        "delta_hi_inclusive": 3.0e-6,
        "contrast_update": "The learned prune is not public-readable versus E224.",
        "next_action": "Prefer the cleaner E224 for worldview reading; E237 remains diagnostic.",
    },
    {
        "outcome": "e237_worse_than_e224",
        "delta_lo_exclusive": 3.0e-6,
        "delta_hi_inclusive": np.inf,
        "contrast_update": "The learned Q3 cell-prune removed public-useful Q3 movement or selected wrong cells.",
        "next_action": "Demote E237 siblings; compare E224 against E230 hand-prune only if Q3 tail blame remains.",
    },
]


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    df = load_sub(file_name, sample)
    return np.clip(df[TARGETS].to_numpy(dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def movement(pred: np.ndarray, base: np.ndarray) -> np.ndarray:
    return logit(pred) - logit(base)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    den = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if den <= EPS:
        return 0.0
    return float(np.dot(aa, bb) / den)


def target_share(abs_move: pd.DataFrame) -> str:
    total = float(abs_move.to_numpy().sum())
    if total <= EPS:
        return ""
    shares = (abs_move.sum(axis=0) / total).sort_values(ascending=False)
    return ";".join(f"{k}:{v:.6f}" for k, v in shares.items())


def cell_set(move: np.ndarray, threshold: float = 1.0e-9) -> set[tuple[int, int]]:
    rows, cols = np.where(np.abs(move) > threshold)
    return set(zip(rows.astype(int), cols.astype(int)))


def lb_bound(delta: float) -> float:
    return E95_PUBLIC + float(delta)


def build_routebook() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for band in BANDS:
        lo = float(band["delta_lo_exclusive"])
        hi = float(band["delta_hi_inclusive"])
        rows.append(
            {
                "outcome": band["outcome"],
                "delta_vs_e95_lo_exclusive": lo,
                "delta_vs_e95_hi_inclusive": hi,
                "public_lb_lo_exclusive": lb_bound(lo) if np.isfinite(lo) else -np.inf,
                "public_lb_hi_inclusive": lb_bound(hi) if np.isfinite(hi) else np.inf,
                "beats_e95": hi < 0,
                "beats_e101": (lb_bound(hi) < E101_PUBLIC) if np.isfinite(hi) else False,
                "beats_mixmin": (lb_bound(hi) < MIXMIN_PUBLIC) if np.isfinite(hi) else False,
                "world_update_class": band["world_update_class"],
                "hidden_world_update": band["hidden_world_update"],
                "next_action": band["next_action"],
                "candidate_to_test": band["candidate_to_test"],
                "forbidden_action": band["forbidden_action"],
                "strengthened": band["strengthened"],
                "weakened": band["weakened"],
            }
        )
    return pd.DataFrame(rows)


def build_contrast_routebook() -> pd.DataFrame:
    return pd.DataFrame(CONTRAST_BANDS)


def decode_score(routebook: pd.DataFrame, score: float) -> dict[str, Any]:
    delta = float(score) - E95_PUBLIC
    rows = routebook.loc[
        routebook["delta_vs_e95_lo_exclusive"].lt(delta)
        & routebook["delta_vs_e95_hi_inclusive"].ge(delta)
    ]
    if len(rows) != 1:
        raise ValueError(f"score {score} mapped to {len(rows)} routebook rows")
    rec = rows.iloc[0].to_dict()
    rec["score"] = float(score)
    rec["delta_vs_e95"] = delta
    rec["delta_vs_e101"] = float(score) - E101_PUBLIC
    rec["delta_vs_mixmin"] = float(score) - MIXMIN_PUBLIC
    rec["delta_vs_e216"] = float(score) - E216_PUBLIC
    return rec


def decode_e224_contrast(contrast_routebook: pd.DataFrame, e237_score: float, e224_score: float) -> dict[str, Any]:
    delta = float(e237_score) - float(e224_score)
    rows = contrast_routebook.loc[
        contrast_routebook["delta_lo_exclusive"].lt(delta)
        & contrast_routebook["delta_hi_inclusive"].ge(delta)
    ]
    if len(rows) != 1:
        raise ValueError(f"E237-E224 delta {delta} mapped to {len(rows)} rows")
    rec = rows.iloc[0].to_dict()
    rec["e237_score"] = float(e237_score)
    rec["e224_score"] = float(e224_score)
    rec["delta_e237_minus_e224"] = delta
    return rec


def build_examples(routebook: pd.DataFrame) -> pd.DataFrame:
    examples = [
        E95_PUBLIC - 4.0e-5,
        E95_PUBLIC - 2.0e-5,
        E95_PUBLIC - 8.0e-6,
        E95_PUBLIC,
        E101_PUBLIC,
        MIXMIN_PUBLIC,
        E95_PUBLIC + 2.5e-5,
        E95_PUBLIC + 1.0e-4,
        E216_PUBLIC,
    ]
    rows = []
    for score in examples:
        rec = decode_score(routebook, score)
        rows.append(
            {
                "score": score,
                "outcome": rec["outcome"],
                "world_update_class": rec["world_update_class"],
                "delta_vs_e95": rec["delta_vs_e95"],
                "next_action": rec["next_action"],
                "candidate_to_test": rec["candidate_to_test"],
            }
        )
    return pd.DataFrame(rows)


def build_pairwise_and_targets(sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    files = {
        "e95": E95_FILE,
        "e154": E154_FILE,
        "e224_clean": E224_FILE,
        "e230_swing25": E230_SWING25_FILE,
        "e230_risk21": E230_RISK21_FILE,
        "e230_risk13": E230_RISK13_FILE,
        "e237_cell25": E237_FILE,
    }
    probs = {name: load_prob(file_name, sample) for name, file_name in files.items()}
    e95_moves = {name: movement(prob, probs["e95"]) for name, prob in probs.items() if name != "e95"}
    pairs = [
        ("e237_cell25", "e95"),
        ("e237_cell25", "e224_clean"),
        ("e237_cell25", "e154"),
        ("e237_cell25", "e230_swing25"),
        ("e237_cell25", "e230_risk21"),
        ("e224_clean", "e95"),
        ("e224_clean", "e154"),
        ("e230_swing25", "e224_clean"),
        ("e230_risk21", "e224_clean"),
        ("e230_risk13", "e224_clean"),
    ]
    pair_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    for new, base in pairs:
        mv = movement(probs[new], probs[base])
        abs_mv = np.abs(mv)
        flat = abs_mv.reshape(-1)
        nonzero = flat > 1.0e-9
        abs_df = pd.DataFrame(abs_mv, columns=TARGETS)
        row: dict[str, Any] = {
            "pair": f"{new}_vs_{base}",
            "new": new,
            "base": base,
            "moved_cells": int(nonzero.sum()),
            "moved_rows": int((abs_mv.max(axis=1) > 1.0e-9).sum()),
            "mean_abs_logit_delta": float(abs_mv.mean()),
            "max_abs_logit_delta": float(abs_mv.max()),
            "top1_abs_logit": float(np.sort(flat)[-1]) if flat.size else 0.0,
            "top5_abs_logit": float(np.sort(flat)[-5:].sum()) if flat.size >= 5 else float(flat.sum()),
            "top1_share": float(np.sort(flat)[-1] / flat.sum()) if flat.sum() > EPS else 0.0,
            "top5_share": float(np.sort(flat)[-5:].sum() / flat.sum()) if flat.sum() > EPS and flat.size >= 5 else 0.0,
            "target_abs_share": target_share(abs_df),
        }
        if new in e95_moves:
            for ref in ["e154", "e224_clean", "e230_swing25", "e230_risk21", "e216_s2_miss"]:
                if ref in e95_moves:
                    row[f"cosine_vs_{ref}_from_e95"] = cosine(e95_moves[new], e95_moves[ref])
        pair_rows.append(row)
        total_abs = float(abs_mv.sum())
        for j, target in enumerate(TARGETS):
            target_abs = abs_mv[:, j]
            target_rows.append(
                {
                    "pair": f"{new}_vs_{base}",
                    "target": target,
                    "moved_cells": int((target_abs > 1.0e-9).sum()),
                    "abs_logit_sum": float(target_abs.sum()),
                    "abs_logit_share": float(target_abs.sum() / total_abs) if total_abs > EPS else 0.0,
                    "mean_signed_logit_delta": float(mv[:, j].mean()),
                    "max_abs_logit_delta": float(target_abs.max()),
                }
            )
    return pd.DataFrame(pair_rows), pd.DataFrame(target_rows)


def build_overlap(sample: pd.DataFrame) -> pd.DataFrame:
    files = {
        "e224_clean": E224_FILE,
        "e237_cell25": E237_FILE,
        "e230_swing25": E230_SWING25_FILE,
        "e230_risk21": E230_RISK21_FILE,
        "e230_risk13": E230_RISK13_FILE,
    }
    probs = {name: load_prob(file_name, sample) for name, file_name in files.items()}
    base = probs["e224_clean"]
    sets = {
        name: cell_set(movement(prob, base))
        for name, prob in probs.items()
        if name != "e224_clean"
    }
    q3_idx = TARGETS.index("Q3")
    ref = sets["e237_cell25"]
    ref_q3 = {c for c in ref if c[1] == q3_idx}
    rows = []
    for name, cells in sets.items():
        q3_cells = {c for c in cells if c[1] == q3_idx}
        inter = cells & ref
        union = cells | ref
        q3_inter = q3_cells & ref_q3
        q3_union = q3_cells | ref_q3
        rows.append(
            {
                "candidate": name,
                "moved_cells_vs_e224": len(cells),
                "q3_cells_vs_e224": len(q3_cells),
                "overlap_with_e237_cells": len(inter),
                "jaccard_with_e237_cells": len(inter) / len(union) if union else 1.0,
                "q3_overlap_with_e237": len(q3_inter),
                "q3_jaccard_with_e237": len(q3_inter) / len(q3_union) if q3_union else 1.0,
                "same_as_e237": name == "e237_cell25",
            }
        )
    return pd.DataFrame(rows).sort_values(["same_as_e237", "q3_overlap_with_e237"], ascending=[False, False])


def candidate_metrics() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    e224 = pd.read_csv(E224_SELECTED)
    e224_top = e224[e224["submission_file"].eq(E224_FILE)].iloc[0].to_dict()
    rows.append(
        {
            "candidate": "e224_clean",
            "role": "clean_unpruned_jepa",
            "submission_file": E224_FILE,
            "expected_focus": e224_top.get("expected_focus"),
            "adverse_delta": e224_top.get("adverse_delta"),
            "support_prob_focus_swing_weighted": e224_top.get("support_prob_focus_swing_weighted"),
            "expected_loss_vs_e224": 0.0,
            "adverse_reduction_vs_e224": 0.0,
            "support_gain_vs_e224": 0.0,
            "q3_top1_over_abs_expected": e224_top.get("q3_top1_over_abs_expected"),
            "q3_adverse_delta": e224_top.get("q3_adverse_delta"),
            "q3_expected_focus": e224_top.get("q3_expected_focus"),
            "q3_cells_changed_vs_e224": 0,
            "source": "E224 selected",
        }
    )
    e230 = pd.read_csv(E230_SELECTED)
    for _, rec in e230.iterrows():
        rows.append(
            {
                "candidate": f"e230_{rec['candidate_id']}",
                "role": "hand_q3_prune",
                "submission_file": rec["submission_file"],
                "expected_focus": rec.get("expected_focus"),
                "adverse_delta": rec.get("adverse_delta"),
                "support_prob_focus_swing_weighted": rec.get("support_prob_focus_swing_weighted"),
                "expected_loss_vs_e224": rec.get("expected_loss_vs_e224"),
                "adverse_reduction_vs_e224": rec.get("adverse_reduction_vs_e224"),
                "support_gain_vs_e224": rec.get("support_gain_vs_e224"),
                "q3_top1_over_abs_expected": rec.get("q3_top1_over_abs_expected"),
                "q3_adverse_delta": rec.get("q3_adverse_delta"),
                "q3_expected_focus": rec.get("q3_expected_focus"),
                "q3_cells_changed_vs_e224": rec.get("pruned_q3"),
                "source": "E230 selected",
            }
        )
    e237 = pd.read_csv(E237_SELECTED)
    for _, rec in e237.iterrows():
        rows.append(
            {
                "candidate": f"e237_{rec['candidate_id']}",
                "role": "learned_cell_q3_prune",
                "submission_file": rec["submission_file"],
                "expected_focus": rec.get("expected_focus"),
                "adverse_delta": rec.get("adverse_delta"),
                "support_prob_focus_swing_weighted": rec.get("support_prob_focus_swing_weighted"),
                "expected_loss_vs_e224": rec.get("expected_loss_vs_e224"),
                "adverse_reduction_vs_e224": rec.get("adverse_reduction_vs_e224"),
                "support_gain_vs_e224": rec.get("support_gain_vs_e224"),
                "actual_expected_delta_vs_e224": rec.get("actual_expected_delta_vs_e224"),
                "actual_adverse_reduction_vs_e224": rec.get("actual_adverse_reduction_vs_e224"),
                "actual_support_gain_vs_e224": rec.get("actual_support_gain_vs_e224"),
                "q3_top1_over_abs_expected": rec.get("q3_top1_over_abs_expected"),
                "q3_adverse_delta": rec.get("q3_adverse_delta"),
                "q3_expected_focus": rec.get("q3_expected_focus"),
                "q3_cells_changed_vs_e224": rec.get("q3_dropped_cells"),
                "e230_q3_risk_top21_overlap": rec.get("e230_q3_risk_top21_overlap"),
                "e230_q3_swing_top25_overlap": rec.get("e230_q3_swing_top25_overlap"),
                "e237_score": rec.get("e237_score"),
                "source": "E237 selected",
            }
        )
    return pd.DataFrame(rows)


def write_report(
    routebook: pd.DataFrame,
    contrast_routebook: pd.DataFrame,
    examples: pd.DataFrame,
    pairwise: pd.DataFrame,
    target_df: pd.DataFrame,
    overlap: pd.DataFrame,
    metrics: pd.DataFrame,
    selected: dict[str, Any] | None,
    e224_contrast: dict[str, Any] | None,
) -> None:
    route_cols = [
        "outcome",
        "public_lb_lo_exclusive",
        "public_lb_hi_inclusive",
        "world_update_class",
        "next_action",
        "candidate_to_test",
    ]
    metrics_cols = [
        "candidate",
        "role",
        "expected_loss_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "q3_top1_over_abs_expected",
        "q3_cells_changed_vs_e224",
        "e230_q3_risk_top21_overlap",
        "submission_file",
    ]
    pair_cols = [
        "pair",
        "moved_cells",
        "moved_rows",
        "mean_abs_logit_delta",
        "max_abs_logit_delta",
        "top1_share",
        "target_abs_share",
        "cosine_vs_e154_from_e95",
        "cosine_vs_e224_clean_from_e95",
        "cosine_vs_e230_swing25_from_e95",
        "cosine_vs_e230_risk21_from_e95",
    ]
    target_focus = target_df[
        target_df["pair"].isin(
            [
                "e237_cell25_vs_e95",
                "e237_cell25_vs_e224_clean",
                "e224_clean_vs_e95",
                "e230_swing25_vs_e224_clean",
                "e230_risk21_vs_e224_clean",
            ]
        )
    ].sort_values(["pair", "abs_logit_share"], ascending=[True, False])
    lines = [
        "# E238 E237 Public Feedback Decoder",
        "",
        "## Question",
        "",
        "If the E237 learned cell-level JEPA Q3-tail candidate is submitted, how should its public LB be read without post-hoc top-k or sibling tuning?",
        "",
        "## Locked Candidate",
        "",
        f"- candidate: `analysis_outputs/{E237_FILE}`",
        f"- current public frontier: `{E95_PUBLIC:.10f}` from `{E95_FILE}`",
        f"- E101 reference: `{E101_PUBLIC:.10f}`",
        f"- mixmin reference: `{MIXMIN_PUBLIC:.10f}`",
        f"- bad JEPA reference E216: `{E216_PUBLIC:.10f}`",
        "",
        "## Candidate Metrics",
        "",
        md_table(metrics, metrics_cols, n=12),
        "",
        "## Public Routebook",
        "",
        md_table(routebook, route_cols, n=20),
        "",
        "## E237-vs-E224 Contrast Routebook",
        "",
        md_table(contrast_routebook, n=10),
        "",
        "## Example Scores",
        "",
        md_table(examples, n=20),
        "",
        "## Pairwise Movement Anatomy",
        "",
        md_table(pairwise, pair_cols, n=20),
        "",
        "## Cell Overlap Against E224",
        "",
        md_table(overlap, n=10),
        "",
        "## Target Anatomy",
        "",
        md_table(target_focus, n=40),
        "",
        "## Decision Rules",
        "",
        "- A clean win validates the learned Q3 decisive-cell world, not a generic larger JEPA model.",
        "- If E224 is unsubmitted, E237 public feedback cannot fully separate the clean E224 body from the learned Q3 prune.",
        "- If both E237 and E224 are known, the E237-E224 delta decides whether the learned cell prune adds public value.",
        "- A tie or small loss blocks lower-ranked E237 siblings until exact cell attribution is done.",
        "- A branch loss routes away from same-family Q3 top-k tuning toward E166, E154, or a new target representation.",
    ]
    if selected is not None:
        lines += [
            "",
            "## Selected Score Decode",
            "",
            "```json",
            json.dumps(selected, indent=2, sort_keys=True),
            "```",
        ]
    if e224_contrast is not None:
        lines += [
            "",
            "## E224 Contrast Decode",
            "",
            "```json",
            json.dumps(e224_contrast, indent=2, sort_keys=True),
            "```",
        ]
    lines += [
        "",
        "## Outputs",
        "",
        f"- routebook: `analysis_outputs/{ROUTEBOOK_OUT.name}`",
        f"- E224 contrast routebook: `analysis_outputs/{CONTRAST_OUT.name}`",
        f"- examples: `analysis_outputs/{EXAMPLES_OUT.name}`",
        f"- pairwise anatomy: `analysis_outputs/{PAIRWISE_OUT.name}`",
        f"- target anatomy: `analysis_outputs/{TARGET_OUT.name}`",
        f"- cell overlap: `analysis_outputs/{OVERLAP_OUT.name}`",
        f"- candidate metrics: `analysis_outputs/{METRICS_OUT.name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--score", type=float, default=None, help="Optional observed E237 public LB to decode.")
    parser.add_argument("--e224-score", type=float, default=None, help="Optional observed E224 public LB for direct contrast.")
    args = parser.parse_args()

    sample_path = ROOT / "data" / "ch2026_submission_sample.csv"
    sample = pd.read_csv(sample_path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)
    routebook = build_routebook()
    contrast_routebook = build_contrast_routebook()
    examples = build_examples(routebook)
    pairwise, target_df = build_pairwise_and_targets(sample)
    overlap = build_overlap(sample)
    metrics = candidate_metrics()
    selected = decode_score(routebook, args.score) if args.score is not None else None
    e224_contrast = None
    if args.score is not None and args.e224_score is not None:
        e224_contrast = decode_e224_contrast(contrast_routebook, args.score, args.e224_score)

    routebook.to_csv(ROUTEBOOK_OUT, index=False)
    contrast_routebook.to_csv(CONTRAST_OUT, index=False)
    examples.to_csv(EXAMPLES_OUT, index=False)
    pairwise.to_csv(PAIRWISE_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    overlap.to_csv(OVERLAP_OUT, index=False)
    metrics.to_csv(METRICS_OUT, index=False)
    if selected is not None or e224_contrast is not None:
        SELECTED_OUT.write_text(
            json.dumps({"score_decode": selected, "e224_contrast": e224_contrast}, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    write_report(routebook, contrast_routebook, examples, pairwise, target_df, overlap, metrics, selected, e224_contrast)

    print(f"wrote: {REPORT_OUT}")
    if selected is not None:
        print(json.dumps(selected, indent=2, sort_keys=True))
    else:
        print(routebook[["outcome", "public_lb_lo_exclusive", "public_lb_hi_inclusive"]].to_string(index=False))


if __name__ == "__main__":
    main()
