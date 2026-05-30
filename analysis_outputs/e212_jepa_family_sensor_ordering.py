#!/usr/bin/env python3
"""E212: order the JEPA-derived public sensors.

This experiment does not fit a new model and does not create a new
probability tensor. It treats the E209/E210/E211 submissions as hypotheses:

- E209: raw feature-neighbor JEPA translation is enough.
- E210: a blunt target-dependency gate is needed for public hard-tail safety.
- E211: Q3 wants raw JEPA body, while S4 wants dependency-consistent movement.

The output is a pre-registered ordering and a feedback routebook for the next
public slot.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1.0e-12

E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405

E95_FILE = "submission_e95_hardtail_541e3973.csv"

SELECTED_FILES = {
    "E209": OUT / "e209_feature_neighbor_jepa_materialization_selected.csv",
    "E210": OUT / "e210_jepa_target_dependency_gate_selected.csv",
    "E211": OUT / "e211_target_specific_jepa_gate_selected.csv",
}

OUT_SUMMARY = OUT / "e212_jepa_family_sensor_ordering_summary.csv"
OUT_ROUTEBOOK = OUT / "e212_jepa_family_sensor_ordering_routebook.csv"
OUT_PAIRWISE = OUT / "e212_jepa_family_sensor_ordering_pairwise.csv"
OUT_REPORT = OUT / "e212_jepa_family_sensor_ordering_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_submission(file_name: str) -> pd.DataFrame:
    path = OUT / file_name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def clean_file_name(value: Any) -> str:
    text = str(value)
    if text == "nan":
        return ""
    return text.replace("analysis_outputs/", "")


def target_share(delta_abs: pd.DataFrame) -> str:
    total = float(delta_abs.to_numpy().sum())
    if total <= EPS:
        return "none"
    shares = (delta_abs.sum(axis=0) / total).sort_values(ascending=False)
    return ";".join(f"{k}:{v:.6f}" for k, v in shares.items())


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    den = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if den <= EPS:
        return 0.0
    return float(np.dot(aa, bb) / den)


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    view = view.head(n).copy()

    def render(v: Any) -> str:
        if isinstance(v, (float, np.floating)):
            return f"{float(v):.12g}"
        if isinstance(v, (int, np.integer)):
            return str(int(v))
        return str(v)

    def clean(s: str) -> str:
        return s.replace("\n", " ").replace("|", "\\|")

    lines = [
        "| " + " | ".join(clean(str(c)) for c in view.columns) + " |",
        "| " + " | ".join("---" for _ in view.columns) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(clean(render(row[c])) for c in view.columns) + " |")
    return "\n".join(lines)


def family_hypothesis(row: pd.Series) -> tuple[str, str, str, float]:
    family = str(row["family"])
    anchor = str(row["anchor"])
    if family == "E209":
        combo = str(row.get("combo", ""))
        if combo == "s4_rank":
            return (
                "raw_jepa_s4_only",
                "JEPA neighbor latent contains an S4 rank signal without extra dependency gating.",
                "raw JEPA control; narrow target test",
                0.72,
            )
        return (
            "raw_jepa_q3_s4_translation",
            "The feature-neighbor JEPA representation can be translated directly into Q3/S4 frontier movement.",
            "raw JEPA control; cleanest falsifier for actual JEPA usefulness",
            0.82,
        )
    if family == "E210":
        return (
            "blunt_dependency_gate",
            "Public hard-tail safety requires filtering both Q3 and S4 by target-dependency geometry.",
            "high hard-tail sensor, but it loses the E209 local body",
            0.45,
        )
    # E211.
    s4_mode = str(row.get("s4_mode", ""))
    return (
        f"target_specific_q3raw_s4{s4_mode}",
        "Q3 wants the raw JEPA residual body, while S4 wants dependency-consistent JEPA movement.",
        "current strongest JEPA worldview; E154 anchor adds survival but confounds attribution"
        if anchor == "e154"
        else "current strongest clean E95-frontier JEPA sensor",
        1.00,
    )


def load_selected_rows() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for family, path in SELECTED_FILES.items():
        df = pd.read_csv(path)
        for idx, rec in df.iterrows():
            row = rec.to_dict()
            row["family"] = family
            row["family_rank"] = int(idx) + 1
            row["submission_file"] = clean_file_name(row.get("submission_file", ""))
            if family == "E209":
                row["policy_id"] = f'{row["combo"]}|{row["anchor"]}|scale={float(row["scale"]):.2f}'
                row["local_delta"] = float(row["stage2_oof_delta"])
                row["geometry_delta"] = float(row["stage2_geometry_delta"])
                row["geometry_win_rate"] = float(row["stage2_geometry_win_rate"])
                row["subject_half_delta"] = float(row["stage2_subject_half_delta"])
                row["subject_half_win_rate"] = float(row["stage2_subject_half_win_rate"])
                row["local_vs_parent_delta"] = 0.0
                row["parent_integrity_note"] = "raw JEPA materialization"
                row["frontier_keep_abs_share"] = np.nan
            elif family == "E210":
                row["policy_id"] = (
                    f'{row["combo"]}|{row["gate_mode"]}|shrink={float(row["shrink"]):.2f}|'
                    f'{row["anchor"]}|scale={float(row["scale"]):.2f}'
                )
                row["local_delta"] = float(row["local_delta"])
                row["local_vs_parent_delta"] = float(row["local_vs_ungated_delta"])
                row["parent_integrity_note"] = "dependency gate versus E209"
            else:
                row["policy_id"] = (
                    f'q3={float(row["q3_scale"]):.2f}|s4={row["s4_mode"]}|'
                    f's4scale={float(row["s4_scale"]):.2f}|{row["anchor"]}|'
                    f'anchor_scale={float(row["anchor_scale"]):.2f}'
                )
                row["local_delta"] = float(row["delta"])
                row["local_vs_parent_delta"] = float(row["delta_vs_ungated"])
                row["parent_integrity_note"] = "target-specific gate versus E209"
            name, thesis, role, specificity = family_hypothesis(pd.Series(row))
            row["hypothesis_name"] = name
            row["worldview_bet"] = thesis
            row["sensor_role"] = role
            row["hypothesis_specificity"] = specificity
            rows.append(row)
    out = pd.DataFrame(rows)
    out["anchor_cleanliness"] = out["anchor"].map({"e95": 1.0, "e154": 0.62, "mixmin": 0.38}).fillna(0.5)
    out["anchor_purity_note"] = np.where(
        out["anchor"].eq("e95"),
        "clean current-frontier sensor",
        np.where(out["anchor"].eq("e154"), "survival-oriented but E154-confounded", "older anchor control"),
    )
    return out


def add_submission_audit(frame: pd.DataFrame) -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv")
    e95 = read_submission(E95_FILE)
    if not sample[KEYS].astype(str).equals(e95[KEYS].astype(str)):
        raise ValueError("E95 key order does not match sample")
    e95_targets = e95[TARGETS].astype(float)

    audits: list[dict[str, Any]] = []
    vectors: dict[str, np.ndarray] = {}
    for _, row in frame.iterrows():
        file_name = str(row["submission_file"])
        path = OUT / file_name
        sub = read_submission(file_name)
        targets = sub[TARGETS].astype(float)
        delta = targets - e95_targets
        delta_abs = delta.abs()
        vector = (logit(targets.to_numpy()) - logit(e95_targets.to_numpy())).reshape(-1)
        vectors[file_name] = vector
        audits.append(
            {
                "submission_file": file_name,
                "sha256": sha256_file(path),
                "columns_match_sample": list(sub.columns) == list(sample.columns),
                "key_order_match_sample": sample[KEYS].astype(str).equals(sub[KEYS].astype(str)),
                "finite_targets": bool(np.isfinite(targets.to_numpy()).all()),
                "valid_probability_range": bool(
                    (targets.to_numpy() >= 0.0).all() and (targets.to_numpy() <= 1.0).all()
                ),
                "changed_cells_vs_e95": int((delta_abs.to_numpy() > EPS).sum()),
                "changed_rows_vs_e95": int((delta_abs.sum(axis=1).to_numpy() > EPS).sum()),
                "mean_abs_delta_vs_e95": float(delta_abs.to_numpy().mean()),
                "max_abs_delta_vs_e95": float(delta_abs.to_numpy().max()),
                "target_abs_delta_share_vs_e95": target_share(delta_abs),
            }
        )

    audit = pd.DataFrame(audits)
    merged = frame.merge(audit, on="submission_file", how="left")

    pair_rows: list[dict[str, Any]] = []
    files = list(vectors)
    for i, a in enumerate(files):
        for b in files[i + 1 :]:
            pair_rows.append(
                {
                    "file_a": a,
                    "file_b": b,
                    "cosine_vs_e95_movement": cosine(vectors[a], vectors[b]),
                    "mean_abs_logit_gap": float(np.abs(vectors[a] - vectors[b]).mean()),
                    "max_abs_logit_gap": float(np.abs(vectors[a] - vectors[b]).max()),
                }
            )
    pd.DataFrame(pair_rows).sort_values(["cosine_vs_e95_movement", "mean_abs_logit_gap"], ascending=[False, True]).to_csv(
        OUT_PAIRWISE, index=False
    )
    return merged


def add_scores(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    local_ref = max(float(-out["local_delta"].min()), EPS)
    geom_ref = max(float(-out["geometry_delta"].abs().max()), EPS)
    survival_ref = max(float(out["survival_score"].max()), EPS)

    out["local_strength"] = np.clip(-out["local_delta"] / local_ref, 0.0, 1.0)
    out["geometry_strength"] = np.clip(-out["geometry_delta"] / geom_ref, 0.0, 1.0) * (
        0.5 + 0.5 * out["geometry_win_rate"].astype(float)
    )
    parent_loss = np.maximum(out["local_vs_parent_delta"].astype(float), 0.0)
    out["parent_integrity"] = np.exp(-parent_loss / 0.00020)
    out["hardtail_strength"] = np.clip(out["survival_score"] / survival_ref, 0.0, 1.0)
    out["tail_concentration_guard"] = 1.0 / (
        1.0 + np.maximum(out["vs_e95_top1_over_abs_expected"].astype(float), 0.0) / 0.25
    )
    out["bad_axis_guard"] = 1.0 / (1.0 + np.maximum(out["max_bad_cos"].astype(float), 0.0) / 0.20)

    out["structured_survival_score"] = (
        0.24 * out["local_strength"]
        + 0.18 * out["geometry_strength"]
        + 0.20 * out["parent_integrity"]
        + 0.18 * out["hardtail_strength"]
        + 0.08 * out["tail_concentration_guard"]
        + 0.07 * out["bad_axis_guard"]
        + 0.05 * out["hypothesis_specificity"]
    )
    out["clean_sensor_score"] = (
        0.28 * out["local_strength"]
        + 0.18 * out["geometry_strength"]
        + 0.20 * out["parent_integrity"]
        + 0.16 * out["anchor_cleanliness"]
        + 0.12 * out["hypothesis_specificity"]
        + 0.06 * out["bad_axis_guard"]
    )
    out["control_value_score"] = (
        0.35 * out["anchor_cleanliness"]
        + 0.25 * out["hypothesis_specificity"]
        + 0.20 * (out["family"].eq("E209").astype(float))
        + 0.20 * out["parent_integrity"]
    )

    out["survival_rank"] = out["structured_survival_score"].rank(method="first", ascending=False).astype(int)
    out["clean_sensor_rank"] = out["clean_sensor_score"].rank(method="first", ascending=False).astype(int)
    out["control_rank"] = out["control_value_score"].rank(method="first", ascending=False).astype(int)
    return out.sort_values(["survival_rank", "clean_sensor_rank"]).reset_index(drop=True)


def build_routebook(summary: pd.DataFrame) -> pd.DataFrame:
    chosen = summary.loc[
        summary["submission_file"].isin(
            {
                "submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv",
                "submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv",
                "submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv",
                "submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv",
            }
        )
    ].copy()
    route_rows: list[dict[str, Any]] = []
    bands = [
        ("clean_win", float("-inf"), E95_PUBLIC - 0.0000070),
        ("micro_win", E95_PUBLIC - 0.0000070, E95_PUBLIC - 0.0000020),
        ("tie", E95_PUBLIC - 0.0000020, E95_PUBLIC + 0.0000020),
        ("small_loss_branch_alive", E95_PUBLIC + 0.0000020, E101_PUBLIC),
        ("mixmin_safe_loss", E101_PUBLIC, MIXMIN_PUBLIC),
        ("branch_loss", MIXMIN_PUBLIC, MIXMIN_PUBLIC + 0.0000350),
        ("hard_fail", MIXMIN_PUBLIC + 0.0000350, float("inf")),
    ]

    for _, row in chosen.iterrows():
        file_name = str(row["submission_file"])
        family = str(row["family"])
        anchor = str(row["anchor"])
        for outcome, lo, hi in bands:
            strengthened = ""
            weakened = ""
            next_action = ""
            if outcome in {"clean_win", "micro_win"}:
                if family == "E211" and anchor == "e95":
                    strengthened = "clean target-specific JEPA translation"
                    weakened = "JEPA-is-only-E154-confounding"
                    next_action = "test the E211 E154 twin only if chasing survival, otherwise search a second non-collinear JEPA axis"
                elif family == "E211":
                    strengthened = "target-specific JEPA plus E154 repaired-branch survival"
                    weakened = "raw E209-only and blunt E210-first ordering"
                    next_action = "submit the E211 E95 clean twin to separate JEPA from E154 confounding"
                elif family == "E209":
                    strengthened = "raw feature-neighbor JEPA translation"
                    weakened = "dependency gate necessity"
                    next_action = "promote E211 only if needing S4 safety; otherwise search new raw JEPA target axes"
                else:
                    strengthened = "dependency-tail localization"
                    weakened = "raw JEPA body sufficiency"
                    next_action = "compare against E211 before another blunt dependency gate"
            elif outcome in {"tie", "small_loss_branch_alive"}:
                strengthened = "hard-label resolution bottleneck; signal may be real but under public-cell noise"
                weakened = "large JEPA frontier break"
                next_action = "do not tune amplitude; use the paired clean/E154 or raw-control contrast"
            elif outcome == "mixmin_safe_loss":
                strengthened = "same plateau law as E101/E176: local signal exists but public tail rejects the translation"
                weakened = "current probability-graft JEPA path"
                next_action = "try the raw E209 control only if E211 failed; otherwise rebuild representation before submission"
            else:
                strengthened = "JEPA probability graft is misaligned with public hidden cells"
                weakened = "E209/E210/E211 family as expected-score lane"
                next_action = "close this JEPA graft family and return to representation/objective design"
            route_rows.append(
                {
                    "submission_file": file_name,
                    "family": family,
                    "anchor": anchor,
                    "outcome": outcome,
                    "public_lb_lo_exclusive": lo,
                    "public_lb_hi_inclusive": hi,
                    "worldview_if_observed": strengthened,
                    "weakened_if_observed": weakened,
                    "pre_registered_next_action": next_action,
                }
            )
    return pd.DataFrame(route_rows)


def build_report(summary: pd.DataFrame, routebook: pd.DataFrame) -> str:
    survival_cols = [
        "survival_rank",
        "clean_sensor_rank",
        "family",
        "anchor",
        "hypothesis_name",
        "structured_survival_score",
        "clean_sensor_score",
        "local_delta",
        "local_vs_parent_delta",
        "geometry_delta",
        "geometry_win_rate",
        "survival_score",
        "vs_e95_expected_delta_focus_mean",
        "vs_e95_top1_over_abs_expected",
        "max_bad_cos",
        "submission_file",
    ]
    control_cols = [
        "control_rank",
        "family",
        "anchor",
        "hypothesis_name",
        "control_value_score",
        "anchor_purity_note",
        "sensor_role",
        "submission_file",
    ]
    top_survival = summary.sort_values("survival_rank")
    top_clean = summary.sort_values("clean_sensor_rank")
    top_control = summary.sort_values("control_rank")

    pairwise = pd.read_csv(OUT_PAIRWISE) if OUT_PAIRWISE.exists() else pd.DataFrame()
    lines = [
        "# E212 JEPA Family Sensor Ordering",
        "",
        "## Purpose",
        "",
        "E212 freezes the next JEPA-family submission order before public feedback. It does not train a model and does not write a new submission tensor.",
        "",
        "The key distinction is now operational:",
        "",
        "- E209 is the raw feature-neighbor JEPA control.",
        "- E210 is the blunt dependency-gated hard-tail sensor.",
        "- E211 is the target-specific JEPA translation: Q3 raw body, S4 dependency-consistent movement.",
        "",
        "## Main Decision",
        "",
        "If using one slot for maximum structured JEPA survival, submit `analysis_outputs/submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv`.",
        "",
        "If using one slot for the clean current-frontier JEPA sensor, submit `analysis_outputs/submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv`.",
        "",
        "E209 remains the raw-JEPA control. E210 is demoted behind E211 because it has strong hard-tail anatomy but loses the local JEPA body and geometry that E211 preserves.",
        "",
        "## Structured Survival Ranking",
        "",
        md_table(top_survival, survival_cols, n=12),
        "",
        "## Clean Sensor Ranking",
        "",
        md_table(top_clean, survival_cols, n=12),
        "",
        "## Control / Falsification Value",
        "",
        md_table(top_control, control_cols, n=12),
        "",
        "## Pairwise Movement Similarity",
        "",
        md_table(pairwise, n=20),
        "",
        "## Feedback Routebook",
        "",
        md_table(routebook, n=60),
        "",
        "## Interpretation",
        "",
        "- If the E211 E95 clean sensor wins, actual JEPA is useful beyond E154 branch confounding.",
        "- If only the E211 E154 file wins, the signal is mixed: JEPA may help, but the repaired-branch anchor is doing nontrivial work.",
        "- If E211 loses but E209 later wins, the S4 dependency gate is overfit and raw JEPA body should be restored.",
        "- If E211 and E209 both lose, the current JEPA probability-graft path is not the 0.54 route; the next JEPA attempt must change the target representation, not the blend amplitude.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    selected = load_selected_rows()
    audited = add_submission_audit(selected)
    scored = add_scores(audited)
    routebook = build_routebook(scored)
    scored.to_csv(OUT_SUMMARY, index=False)
    routebook.to_csv(OUT_ROUTEBOOK, index=False)
    OUT_REPORT.write_text(build_report(scored, routebook), encoding="utf-8")
    print(f"wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"wrote {OUT_ROUTEBOOK.relative_to(ROOT)}")
    print(f"wrote {OUT_PAIRWISE.relative_to(ROOT)}")
    print(f"wrote {OUT_REPORT.relative_to(ROOT)}")
    print(
        scored.sort_values("survival_rank")[
            ["survival_rank", "clean_sensor_rank", "family", "anchor", "submission_file"]
        ]
        .head(5)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
