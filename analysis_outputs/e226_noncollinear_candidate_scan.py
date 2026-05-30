#!/usr/bin/env python3
"""E226: scan live documented candidates for non-collinear post-E224 directions.

E216 made the S2 masked-family JEPA lane public-negative. E224 is the current
capped-Q3/S4-body JEPA sensor, but it is almost the same direction as E223 and
E211. This experiment asks a narrower question before creating any new file:

    If E224 fails or ties, which already-materialized candidate is genuinely a
    different worldview rather than another amplitude tweak on the same axis?

The scan uses only existing submission files referenced in project documents
plus a short manual list of public anchors and active candidates. It does not
train a model and does not create a submission.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e222_e211_support_tail_audit as e222  # noqa: E402


E95_FILE = "submission_e95_hardtail_541e3973.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
E72_FILE = "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E142_FILE = "submission_e142_transferclip_09a92236.csv"
E143_FILE = "submission_e143_activeq2s3repair_68ca656f.csv"
E144_FILE = "submission_e144_activeboundary_d7b4b331.csv"
E155_FILE = "submission_e155_bodytemp_d27e7965.csv"
E156_FILE = "submission_e156_targetaxis_757546d2.csv"
E157_FILE = "submission_e157_lowbodypareto_bd67930d.csv"
E166_FILE = "submission_e166_broadsurv_s0p01_d8bfa94b.csv"
E169_FILE = "submission_e169_ctx_veto_c5e806e3.csv"
E172_FILE = "submission_e172_vis_pos_all_keep0p25_d90f4407.csv"
E174_FILE = "submission_e174_ro_fc_top75_to1p0_95638e73.csv"
E176_FILE = "submission_e176_abl_q2_to0p75_91e49725.csv"
E211_FILE = "submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv"
E216_FILE = "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv"
E223_FILE = "submission_e223_jepa_q3s0p75_s4closer_e154_a0p5_794b0349.csv"
E224_FILE = "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"
E224_E95_FILE = "submission_e224_e224_q3s0p625_s4toward_e95_a0p5_9c52abe2.csv"
BRIDGE_BLEND_M0P75_S1P25 = "bridge_scan_candidates/submission_bridge_blend_m0p75_s1p25.csv"

REPAIRED_BRANCH_FILES = {
    E142_FILE,
    E143_FILE,
    E144_FILE,
    E155_FILE,
    E156_FILE,
    E157_FILE,
}

LOCAL_REJECTED_FILES = {
    BRIDGE_BLEND_M0P75_S1P25,
}

E95_PUBLIC = 0.5762913298
KNOWN_PUBLIC: dict[str, float] = {
    E95_FILE: E95_PUBLIC,
    E101_FILE: 0.5763003660,
    MIXMIN_FILE: 0.5763066405,
    E72_FILE: 0.5764077772,
    "submission_frontier_cvjepa_refine_a2c8d2c8.csv": 0.5774393210,
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv": 0.5775263072,
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv": 0.5779449757,
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv": 0.5783033652,
    "submission_hybrid_0p578_logit_after_subject_final9_strict.csv": 0.5784273528,
    "submission_jepa_latent_q2_w0p45.csv": 0.5798012862,
    "submission_lejepa_targetwise_strict_best_scale0p5.csv": 0.5802468192,
    "submission_jepa_latent_residual_probe.csv": 0.5812273278,
    E176_FILE: 0.5763118310,
    E216_FILE: 0.5772865088,
}

DOCS = [
    "candidate_submissions.md",
    "experiment_log.md",
    "lb_observation_log.md",
    "validation_stress_report.md",
    "hypothesis_graph.md",
    "feature_registry.md",
    "failed_hypotheses.md",
    "latent_diagnostics.md",
]

MANUAL_FILES = [
    E95_FILE,
    E101_FILE,
    MIXMIN_FILE,
    E72_FILE,
    E142_FILE,
    E143_FILE,
    E144_FILE,
    E154_FILE,
    E155_FILE,
    E156_FILE,
    E157_FILE,
    E166_FILE,
    E169_FILE,
    E172_FILE,
    E174_FILE,
    E176_FILE,
    E211_FILE,
    E216_FILE,
    E223_FILE,
    E224_FILE,
    E224_E95_FILE,
    "submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv",
    "submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e95_a0p5_8e3dc02d.csv",
    "submission_e216_maskfam_jepa_s2_rank_e95_s0p75_4f8dc44d.csv",
    "submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv",
    "submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv",
]

SUMMARY_OUT = OUT / "e226_noncollinear_candidate_scan_summary.csv"
TARGET_OUT = OUT / "e226_noncollinear_candidate_scan_targets.csv"
SKIPPED_OUT = OUT / "e226_noncollinear_candidate_scan_skipped.csv"
REPORT_OUT = OUT / "e226_noncollinear_candidate_scan_report.md"

EPS = 1.0e-12


@dataclass(frozen=True)
class FileSpec:
    file_name: str
    path: Path
    source: str


def locate_file(name: str) -> Path | None:
    path = Path(name)
    if path.exists():
        return path
    for base in (OUT, JEPA, ROOT):
        candidate = base / name
        if candidate.exists():
            return candidate
    if name.startswith("analysis_outputs/"):
        candidate = ROOT / name
        if candidate.exists():
            return candidate
    return None


def normalize_file_name(raw: str) -> str:
    text = raw.strip("`'\"),.;")
    if text.startswith("./"):
        text = text[2:]
    if text.startswith(str(ROOT) + "/"):
        text = text[len(str(ROOT)) + 1 :]
    if text.startswith("analysis_outputs/"):
        text = text[len("analysis_outputs/") :]
    return text


def discover_files() -> tuple[list[FileSpec], pd.DataFrame]:
    seen: dict[str, str] = {}
    seen_paths: set[Path] = set()
    skipped: list[dict[str, Any]] = []
    pattern = re.compile(r"(?:analysis_outputs/)?(?:[A-Za-z0-9_./-]*/)?submission_[A-Za-z0-9_.+-]+\.csv")

    for file_name in MANUAL_FILES:
        seen[normalize_file_name(file_name)] = "manual"

    for doc in DOCS:
        path = ROOT / doc
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for match in pattern.finditer(text):
            name = normalize_file_name(match.group(0))
            if "/" in name and not name.startswith("submission_"):
                # Keep subdirectory path if it exists under analysis_outputs.
                name = name
            seen.setdefault(name, f"doc:{doc}")

    specs: list[FileSpec] = []
    for name, source in sorted(seen.items()):
        candidates = [name]
        if "/" in name:
            candidates.append(Path(name).name)
        found = None
        for candidate in candidates:
            found = locate_file(candidate)
            if found is not None:
                if candidate != name and source.startswith("doc:"):
                    source = source + "|basename_fallback"
                name = candidate
                break
        if found is None:
            skipped.append({"file_name": name, "source": source, "reason": "missing"})
            continue
        resolved = found.resolve()
        if resolved in seen_paths:
            skipped.append({"file_name": name, "source": source, "reason": "duplicate_path"})
            continue
        seen_paths.add(resolved)
        specs.append(FileSpec(name, found, source))
    return specs, pd.DataFrame(skipped)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def load_prob_from_path(spec: FileSpec, sample: pd.DataFrame) -> np.ndarray:
    df = pd.read_csv(spec.path, parse_dates=["sleep_date", "lifelog_date"])
    df = df.sort_values(KEYS).reset_index(drop=True)
    if not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"key mismatch: {spec.file_name}")
    return clip_prob(df[TARGETS].to_numpy(dtype=np.float64))


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    den = float(np.linalg.norm(a) * np.linalg.norm(b))
    if den <= EPS:
        return float("nan")
    return float(a @ b / den)


def family_tag(file_name: str) -> str:
    for tag in [
        "e224",
        "e223",
        "e216",
        "e211",
        "e210",
        "e209",
        "e176",
        "e174",
        "e172",
        "e169",
        "e166",
        "e157",
        "e156",
        "e155",
        "e154",
        "e144",
        "e143",
        "e142",
        "e108",
        "e101",
        "e95",
        "e90",
        "e89",
        "e87",
        "e86",
        "e85",
        "e84",
        "e75",
        "e74",
        "e72",
        "mixmin",
        "raw_timeline",
        "hybrid",
        "ordinal",
        "jepa_latent",
        "lejepa",
    ]:
        if tag in file_name:
            return tag
    return "other"


def target_share(abs_logit: np.ndarray) -> dict[str, float]:
    total = float(abs_logit.sum())
    shares = {}
    for j, target in enumerate(TARGETS):
        shares[f"abs_share_{target}"] = float(abs_logit[:, j].sum() / total) if total > EPS else 0.0
    return shares


def movement_summary(
    file_name: str,
    source: str,
    prob: np.ndarray,
    e95: np.ndarray,
    ref_moves: dict[str, np.ndarray],
) -> dict[str, Any]:
    dz = logit(prob).reshape(-1) - logit(e95).reshape(-1)
    dz2 = dz.reshape(prob.shape)
    abs_dz = np.abs(dz2)
    moved = abs_dz > EPS
    swing = np.sort(abs_dz.reshape(-1))[::-1]
    total = float(swing.sum())
    rec: dict[str, Any] = {
        "file_name": file_name,
        "source": source,
        "family": family_tag(file_name),
        "public_lb": KNOWN_PUBLIC.get(file_name, np.nan),
        "public_delta_vs_e95": KNOWN_PUBLIC.get(file_name, np.nan) - E95_PUBLIC
        if file_name in KNOWN_PUBLIC
        else np.nan,
        "known_public_state": "unknown",
        "moved_cells_vs_e95": int(moved.sum()),
        "moved_rows_vs_e95": int(np.where(moved.any(axis=1))[0].size),
        "targets_moved_vs_e95": ",".join([TARGETS[j] for j in np.where(moved.any(axis=0))[0]]),
        "mean_abs_logit_vs_e95": float(abs_dz.mean()),
        "max_abs_logit_vs_e95": float(abs_dz.max()),
        "l1_logit_vs_e95": total,
        "top1_logit_share_vs_e95": float(swing[0] / total) if total > EPS and len(swing) else np.nan,
        "top5_logit_share_vs_e95": float(swing[:5].sum() / total) if total > EPS and len(swing) else np.nan,
        "top25_logit_share_vs_e95": float(swing[:25].sum() / total) if total > EPS and len(swing) else np.nan,
    }
    if file_name in KNOWN_PUBLIC:
        if KNOWN_PUBLIC[file_name] < E95_PUBLIC:
            rec["known_public_state"] = "known_beats_e95"
        elif np.isclose(KNOWN_PUBLIC[file_name], E95_PUBLIC):
            rec["known_public_state"] = "known_e95"
        elif KNOWN_PUBLIC[file_name] <= KNOWN_PUBLIC[MIXMIN_FILE]:
            rec["known_public_state"] = "known_mixmin_safe_loss"
        else:
            rec["known_public_state"] = "known_bad_vs_mixmin"

    rec.update(target_share(abs_dz))
    for name, ref in ref_moves.items():
        rec[f"cos_vs_{name}"] = cosine(dz, ref)
    return rec


def tail_summary(
    file_name: str,
    prob: np.ndarray,
    e95: np.ndarray,
    priors: dict[str, np.ndarray],
    sample: pd.DataFrame,
) -> tuple[dict[str, Any], pd.DataFrame]:
    if not np.any(np.abs(prob - e95) > EPS):
        return {
            "expected_focus": 0.0,
            "adverse_delta": 0.0,
            "support_prob_focus_swing_weighted": np.nan,
            "top1_over_abs_expected": np.nan,
            "top5_over_abs_expected": np.nan,
            "adverse_over_e216_miss": 0.0,
            "cells_for_e95_edge": -1,
            "cells_to_flip_expected_focus": -1,
            "e222_tail_survival_score": 0.0,
            "e222_decision": "anchor_no_movement",
        }, pd.DataFrame()

    spec = e222.Candidate(
        candidate_id=Path(file_name).stem,
        file_name=file_name,
        anchor_file=E95_FILE,
        family=family_tag(file_name),
        status="scan",
        note="E226 documented-candidate non-collinearity scan.",
    )
    rec, target_df, _ = e222.pair_audit(spec, "actual_vs_e95", prob, e95, E95_FILE, priors, sample)
    rec = e222.add_ranking(pd.DataFrame([rec])).iloc[0].to_dict()
    keep = {
        "expected_focus": rec.get("expected_focus", np.nan),
        "adverse_delta": rec.get("adverse_delta", np.nan),
        "support_prob_focus_swing_weighted": rec.get("support_prob_focus_swing_weighted", np.nan),
        "top1_over_abs_expected": rec.get("top1_over_abs_expected", np.nan),
        "top5_over_abs_expected": rec.get("top5_over_abs_expected", np.nan),
        "adverse_over_e216_miss": rec.get("adverse_over_e216_miss", np.nan),
        "cells_for_e95_edge": rec.get("cells_for_e95_edge", np.nan),
        "cells_to_flip_expected_focus": rec.get("cells_to_flip_expected_focus", np.nan),
        "e222_tail_survival_score": rec.get("e222_tail_survival_score", np.nan),
        "e222_decision": rec.get("e222_decision", ""),
    }
    if not target_df.empty:
        target_df = e222.add_ranking(target_df)
        target_df["file_name"] = file_name
    return keep, target_df


def candidate_score(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    known_bad = out["known_public_state"].isin(["known_bad_vs_mixmin", "known_mixmin_safe_loss"])
    known_anchor = out["known_public_state"].isin(["known_e95", "known_beats_e95"])
    same_e224 = out["cos_vs_e224"].abs().fillna(0.0) > 0.90
    q3s4_jepa_family = out["family"].isin(["e209", "e210", "e211", "e223", "e224"]) | (
        out["cos_vs_e224"].fillna(0.0).gt(0.75)
        & out["targets_moved_vs_e95"].isin(["Q3,S4", "Q1,Q3,S2,S3,S4"])
    )
    s2_bad_like = out["cos_vs_e216"].fillna(0.0) > 0.50
    broad_bad_like = out["cos_vs_e176"].fillna(0.0) > 0.80
    e72_bad_like = out["cos_vs_e72"].fillna(0.0) > 0.80
    high_adverse = out["adverse_delta"].fillna(0.0) > 0.006
    hardtail_ancestor = out["family"].isin(["e84", "e85", "e86", "e87", "e89", "e90", "e101", "e108"])
    local_rejected = out["file_name"].isin(LOCAL_REJECTED_FILES)
    repaired_branch_family = out["file_name"].isin(REPAIRED_BRANCH_FILES)
    support = out["support_prob_focus_swing_weighted"].fillna(0.0)
    expected = out["expected_focus"].fillna(0.0)
    adverse = out["adverse_delta"].fillna(0.0)
    edge_cells = out["cells_for_e95_edge"].fillna(0.0)
    top1 = out["top1_over_abs_expected"].replace([np.inf, -np.inf], np.nan).fillna(9.0)
    movement = out["l1_logit_vs_e95"].fillna(0.0)

    out["noncollinear_to_e224"] = ~same_e224
    out["independent_worldview"] = ~(
        same_e224
        | q3s4_jepa_family
        | s2_bad_like
        | broad_bad_like
        | e72_bad_like
        | high_adverse
        | hardtail_ancestor
        | local_rejected
    )
    out["actionable_independent_worldview"] = out["independent_worldview"] & ~local_rejected
    out["known_public_veto"] = known_bad
    out["bad_axis_veto"] = s2_bad_like | broad_bad_like | e72_bad_like | high_adverse
    out["tail_shape_ok"] = (expected < 0.0) & (support >= 0.46) & (top1 <= 0.55) & (edge_cells >= 1)
    out["submission_sensor_score"] = (
        (~same_e224).astype(float) * 0.80
        + out["independent_worldview"].astype(float) * 0.45
        + (1.0 - out["cos_vs_e216"].abs().fillna(0.0).clip(0.0, 1.0)) * 0.30
        + (1.0 - out["cos_vs_e176"].abs().fillna(0.0).clip(0.0, 1.0)) * 0.15
        + np.minimum(np.maximum(-expected, 0.0), 0.0015) * 180.0
        + np.maximum(support - 0.46, 0.0) * 0.80
        + np.minimum(edge_cells, 20.0) * 0.01
        - np.maximum(adverse - 0.0045, 0.0) * 180.0
        - np.maximum(top1 - 0.55, 0.0) * 0.08
        - known_bad.astype(float) * 2.00
        - known_anchor.astype(float) * 1.00
        - q3s4_jepa_family.astype(float) * 0.65
        - e72_bad_like.astype(float) * 0.75
        - hardtail_ancestor.astype(float) * 0.35
        - high_adverse.astype(float) * 0.80
        - local_rejected.astype(float) * 2.50
        - (movement <= EPS).astype(float) * 4.00
    )
    out["candidate_role"] = np.select(
        [
            out["file_name"].eq(E224_FILE),
            (same_e224 | q3s4_jepa_family) & ~out["file_name"].eq(E224_FILE),
            out["file_name"].eq(E154_FILE),
            out["file_name"].eq(E166_FILE),
            out["file_name"].eq(E169_FILE),
            local_rejected,
            repaired_branch_family,
            known_bad,
            s2_bad_like,
            broad_bad_like,
            e72_bad_like,
            high_adverse,
            hardtail_ancestor,
            out["tail_shape_ok"] & ~known_bad & ~same_e224,
        ],
        [
            "current_e224_sensor",
            "same_q3s4_jepa_family",
            "repaired_branch_counterworld",
            "broad_survivor_counterworld",
            "broad_repaired_counterworld",
            "local_rejected_neartie",
            "repaired_branch_family",
            "known_public_negative",
            "s2_bad_axis_neighbor",
            "broad_bad_axis_neighbor",
            "e72_public_bad_neighbor",
            "high_adverse_capacity",
            "hardtail_parent_diagnostic",
            "noncollinear_tail_ok_sensor",
        ],
        default="diagnostic_only",
    )
    return out


def build_report(summary: pd.DataFrame, targets: pd.DataFrame, skipped: pd.DataFrame) -> None:
    rank_cols = [
        "file_name",
        "family",
        "candidate_role",
        "submission_sensor_score",
        "known_public_state",
        "public_delta_vs_e95",
        "cos_vs_e224",
        "cos_vs_e216",
        "cos_vs_e176",
        "cos_vs_e72",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
        "cells_for_e95_edge",
        "targets_moved_vs_e95",
    ]
    live = summary[
        ~summary["known_public_veto"]
        & ~summary["file_name"].eq(E95_FILE)
        & (summary["moved_cells_vs_e95"] > 0)
    ].sort_values("submission_sensor_score", ascending=False)
    noncol = live[live["noncollinear_to_e224"]].copy()
    independent = live[live["actionable_independent_worldview"]].copy()
    locally_rejected = live[live["candidate_role"].eq("local_rejected_neartie")].copy()
    public_known = summary[summary["known_public_state"].ne("unknown")].sort_values("public_lb")
    e224_neighbors = summary[summary["cos_vs_e224"].abs().fillna(0.0).gt(0.80)].sort_values(
        "cos_vs_e224", ascending=False
    )
    target_cols = [
        "file_name",
        "target",
        "moved_cells",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
        "e222_decision",
    ]
    target_view = targets[
        targets["file_name"].isin([E154_FILE, E166_FILE, E169_FILE, E176_FILE, E216_FILE, E224_FILE])
    ].sort_values(["file_name", "expected_focus"])

    best_noncol = independent.iloc[0] if not independent.empty else None
    lines = [
        "# E226 Non-Collinear Candidate Scan",
        "",
        "## Question",
        "",
        "After the E216 public miss and before overusing the E224 axis, which existing materialized candidates remain distinct enough to test a different hidden-world law?",
        "",
        "## Scan Size",
        "",
        f"- evaluated files: `{len(summary)}`",
        f"- skipped missing references: `{len(skipped)}`",
        "",
        "## Main Finding",
        "",
    ]
    if best_noncol is None:
        lines.append("- No independent live candidate survived the scan. E224 remains the only active JEPA-family sensor, and failure should route to new objective design rather than old-file promotion.")
    else:
        lines.append(
            f"- Best independent live sensor by this scan: `{best_noncol['file_name']}` with role `{best_noncol['candidate_role']}`, score `{best_noncol['submission_sensor_score']:.6f}`, cos(E224) `{best_noncol['cos_vs_e224']:.6f}`, cos(E72) `{best_noncol['cos_vs_e72']:.6f}`, expected focus `{best_noncol['expected_focus']:.9f}`, support `{best_noncol['support_prob_focus_swing_weighted']:.6f}`."
        )
        lines.append(
            "- This is a sensor ranking, not a certified improvement claim. Known-public-negative lanes are penalized, and E224-neighbor files are treated as same-family amplitude tests."
        )
    lines.extend(
        [
            "",
            "## Top Independent Counter-World Sensors",
            "",
            md_table(independent, rank_cols, n=20),
            "",
            "## Locally Rejected Near-Tie Sensors",
            "",
            md_table(locally_rejected, rank_cols, n=10),
            "",
            "## Top Live Non-Collinear Sensors",
            "",
            md_table(noncol, rank_cols, n=20),
            "",
            "## E224-Axis Neighbors",
            "",
            md_table(e224_neighbors, rank_cols, n=20),
            "",
            "## Known Public Anchors In Scan",
            "",
            md_table(public_known, rank_cols, n=20),
            "",
            "## Target Tail Anatomy For Key Branches",
            "",
            md_table(target_view, target_cols, n=60),
            "",
            "## Decision",
            "",
            "- E216 S2 remains closed as a submission lane because the public miss is large and the scan marks S2-neighbor directions as bad-axis risk.",
            "- E224 is not a new family; it is a capped-amplitude E211/E223 translator. If it loses worse than mixmin, the right next action is non-collinear search or a support-regularized JEPA objective.",
            "- The raw-bridge `bridge_blend_m0p75_s1p25` file is not promoted despite good E226 shape because E52 already rejected it as a mixmin-relative near-tie, not a replacement.",
            "- Among existing files, the repaired-branch and broad-survivor files are the only plausible already-documented counter-world sensors after removing E72-neighbors, hardtail parents, and same-Q3/S4-JEPA translators. They should be submitted only as worldview tests, not as CV-ranked successors.",
            "",
            "## Outputs",
            "",
            f"- summary: `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- target tail anatomy: `{TARGET_OUT.relative_to(ROOT)}`",
            f"- skipped references: `{SKIPPED_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    specs, skipped = discover_files()
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    e95_spec = FileSpec(E95_FILE, locate_file(E95_FILE) or OUT / E95_FILE, "anchor")
    e95 = load_prob_from_path(e95_spec, sample)

    needed_refs = {
        "e224": E224_FILE,
        "e223": E223_FILE,
        "e211": E211_FILE,
        "e216": E216_FILE,
        "e176": E176_FILE,
        "e154": E154_FILE,
        "e101": E101_FILE,
        "mixmin": MIXMIN_FILE,
        "e72": E72_FILE,
    }
    ref_moves: dict[str, np.ndarray] = {}
    for ref_name, file_name in needed_refs.items():
        path = locate_file(file_name)
        if path is None:
            continue
        prob = load_prob_from_path(FileSpec(file_name, path, "ref"), sample)
        ref_moves[ref_name] = logit(prob).reshape(-1) - logit(e95).reshape(-1)

    rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    load_errors: list[dict[str, Any]] = []
    for spec in specs:
        try:
            prob = load_prob_from_path(spec, sample)
            row = movement_summary(spec.file_name, spec.source, prob, e95, ref_moves)
            tail, target_df = tail_summary(spec.file_name, prob, e95, priors, sample)
            row.update(tail)
            rows.append(row)
            if not target_df.empty:
                target_parts.append(target_df)
        except Exception as exc:  # noqa: BLE001 - audit should skip bad references, not stop.
            load_errors.append({"file_name": spec.file_name, "source": spec.source, "reason": repr(exc)})

    summary = candidate_score(pd.DataFrame(rows))
    summary = summary.sort_values("submission_sensor_score", ascending=False).reset_index(drop=True)
    targets = pd.concat(target_parts, ignore_index=True) if target_parts else pd.DataFrame()
    if not targets.empty:
        targets = targets.sort_values(["file_name", "target"]).reset_index(drop=True)

    skipped_all = pd.concat([skipped, pd.DataFrame(load_errors)], ignore_index=True)
    summary.to_csv(SUMMARY_OUT, index=False)
    targets.to_csv(TARGET_OUT, index=False)
    skipped_all.to_csv(SKIPPED_OUT, index=False)
    build_report(summary, targets, skipped_all)

    live = summary[
        ~summary["known_public_veto"]
        & summary["actionable_independent_worldview"]
        & ~summary["file_name"].eq(E95_FILE)
        & (summary["moved_cells_vs_e95"] > 0)
    ].sort_values("submission_sensor_score", ascending=False)
    print("[E226]")
    print(f"evaluated={len(summary)} skipped={len(skipped_all)} live_independent={len(live)}")
    print(md_table(live, ["file_name", "candidate_role", "submission_sensor_score", "cos_vs_e224", "cos_vs_e216", "cos_vs_e176", "cos_vs_e72", "expected_focus", "support_prob_focus_swing_weighted"], n=10))
    if skipped_all.empty:
        print("skipped=0")
    else:
        print(f"skipped_details={SKIPPED_OUT}")


if __name__ == "__main__":
    main()
