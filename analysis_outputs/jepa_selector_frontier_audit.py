from __future__ import annotations

from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_subset_selector_stress import candidate_stress_scores  # noqa: E402
from public_anchor_bottleneck_decomposition import (  # noqa: E402
    A2C8,
    DATA,
    FINAL9,
    KEYS,
    LEJEPA_BAD,
    ORDINAL,
    Q2_BAD,
    RAW05,
    RESID_BAD,
    STAGE2,
    TARGETS,
    evaluate_models,
    feature_row,
    fit_all_predict,
    known_public_table,
    prob_matrix,
    vec,
)


FULL_OUT = OUT / "jepa_selector_frontier_audit_candidates.csv"
SHORT_OUT = OUT / "jepa_selector_frontier_audit_shortlist.csv"
FAMILY_OUT = OUT / "jepa_selector_frontier_audit_family_summary.csv"
SKIPPED_OUT = OUT / "jepa_selector_frontier_audit_skipped.csv"
REPORT_OUT = OUT / "jepa_selector_frontier_audit_report.md"

JEPA_RE = re.compile(
    r"jepa|lejepa|raw05|cvjepa|blockorth|blockscale|blockpublic|publicmask|axis|energy|raw_timeline|mixmin",
    re.IGNORECASE,
)

SELECTOR_UNCERTAINTY = 0.001418568
BAD_AXIS_LIMIT = 0.05
P90_SOFT_LIMIT = 0.00080


def discover_submission_paths() -> list[Path]:
    paths: list[Path] = []
    for base in [OUT, JEPA]:
        for path in base.glob("submission*.csv"):
            rel = str(path.relative_to(ROOT))
            if JEPA_RE.search(rel):
                paths.append(path)

    refs = [OUT / STAGE2, JEPA / RAW05, OUT / A2C8, OUT / FINAL9, OUT / ORDINAL, JEPA / Q2_BAD, JEPA / RESID_BAD, JEPA / LEJEPA_BAD]
    for path in refs:
        if path.exists():
            paths.append(path)

    seen: set[Path] = set()
    unique: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return sorted(unique, key=lambda p: str(p.relative_to(ROOT)))


def has_submission_schema(path: Path) -> tuple[bool, str]:
    try:
        cols = pd.read_csv(path, nrows=0).columns.tolist()
    except Exception as exc:  # noqa: BLE001
        return False, f"header_error:{type(exc).__name__}"
    required = set(KEYS + TARGETS)
    missing = sorted(required - set(cols))
    if missing:
        return False, "missing:" + ",".join(missing[:4])
    return True, ""


def family_name(path: Path) -> str:
    text = str(path.relative_to(ROOT)).lower()
    name = path.name.lower()
    if "lejepa" in text:
        return "lejepa"
    if "neural_episode_rawstack" in text:
        return "neural_episode_rawstack"
    if "raw_timeline" in text:
        return "raw_timeline"
    if "raw05_jepa" in text:
        return "raw05_jepa"
    if "blockorth" in text:
        return "blockorth"
    if "blockscale" in text:
        return "blockscale"
    if "blockpublic" in text:
        return "blockpublic"
    if "publicmask" in text:
        return "publicmask"
    if "axis" in name:
        return "axis_repair"
    if "energy" in name:
        return "energy_gate"
    if "mixmin" in name:
        return "mixmin"
    if "cvjepa" in name:
        return "cvjepa"
    if "jepa" in text:
        return "other_jepa"
    return "other"


def build_known_and_refs(sample: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    ref_files = {
        "stage2": STAGE2,
        "raw05": RAW05,
        "a2c8": A2C8,
        "final9": FINAL9,
        "ordinal": ORDINAL,
        "q2_bad": Q2_BAD,
        "resid_bad": RESID_BAD,
        "lejepa_bad": LEJEPA_BAD,
    }
    refs = {name: prob_matrix(file_name, sample) for name, file_name in ref_files.items()}
    ref_vecs = {name: vec(prob) for name, prob in refs.items()}

    known_obs = known_public_table()
    rows = []
    for rec in known_obs.to_dict("records"):
        row = feature_row(str(rec["file"]), sample, refs, ref_vecs)
        row.update(rec)
        row["source_path"] = str(Path(str(rec["file"])))
        row["candidate_family"] = "known_public"
        rows.append(row)
    known = pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)
    return known, refs, ref_vecs


def build_candidate_geometry(sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    skipped: list[dict[str, str]] = []
    paths = discover_submission_paths()
    sample_keys = sample[KEYS]

    for i, path in enumerate(paths, start=1):
        ok, reason = has_submission_schema(path)
        if not ok:
            skipped.append({"source_path": str(path.relative_to(ROOT)), "reason": reason})
            continue
        try:
            df_keys = pd.read_csv(path, usecols=KEYS, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)
            if not df_keys[KEYS].equals(sample_keys):
                skipped.append({"source_path": str(path.relative_to(ROOT)), "reason": "key_mismatch"})
                continue
            row = feature_row(path, sample, refs, ref_vecs)
        except Exception as exc:  # noqa: BLE001
            skipped.append({"source_path": str(path.relative_to(ROOT)), "reason": f"load_error:{type(exc).__name__}"})
            continue
        row["file"] = path.name
        row["source_path"] = str(path.relative_to(ROOT))
        row["candidate_family"] = family_name(path)
        rows.append(row)
        if i % 500 == 0:
            print(f"scored {i}/{len(paths)} paths; valid={len(rows)} skipped={len(skipped)}")

    frame = pd.DataFrame(rows)
    if frame.empty:
        raise RuntimeError("No valid submission candidates found.")
    frame = frame.drop_duplicates("source_path").reset_index(drop=True)
    skipped_frame = pd.DataFrame(skipped)
    return frame, skipped_frame


def add_frontier_flags(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    out["movement_over_selector_uncertainty"] = out["mean_abs_move_vs_a2c8"] >= SELECTOR_UNCERTAINTY
    out["raw05_novel_movement"] = out["mean_abs_move_vs_raw05"] >= SELECTOR_UNCERTAINTY
    out["low_public_bad_axis"] = out["bad_axis_abs_load"] <= BAD_AXIS_LIMIT
    out["p90_not_too_worse"] = out["selector_p90_delta_vs_a2c8_public"] <= P90_SOFT_LIMIT
    out["scenario_majority_beats_a2c8"] = out["beats_a2c8_scenario_rate"] >= 0.50
    out["frontier_escape_candidate"] = (
        out["movement_over_selector_uncertainty"]
        & out["low_public_bad_axis"]
        & out["p90_not_too_worse"]
        & out["scenario_majority_beats_a2c8"]
    )
    out["novel_frontier_candidate"] = out["frontier_escape_candidate"] & out["raw05_novel_movement"]
    out["submission_priority_score"] = (
        out["selector_p90_delta_vs_a2c8_public"].fillna(9.0)
        + 0.20 * out["selector_stress_spread"].fillna(0.0)
        + 0.00015 * out["bad_axis_abs_load"].fillna(0.0)
        - 0.00003 * np.minimum(out["mean_abs_move_vs_a2c8"].fillna(0.0), 0.02)
    )
    return out.sort_values(["frontier_escape_candidate", "submission_priority_score"], ascending=[False, True]).reset_index(drop=True)


def family_summary(scored: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for family, group in scored.groupby("candidate_family", sort=False):
        best = group.sort_values("submission_priority_score").iloc[0]
        rows.append(
            {
                "candidate_family": family,
                "n": int(len(group)),
                "escape_candidates": int(group["frontier_escape_candidate"].sum()),
                "novel_escape_candidates": int(group["novel_frontier_candidate"].sum()),
                "resolved_better": int(group["resolved_better_than_a2c8_gate"].sum()),
                "low_bad_axis_rate": float(group["low_public_bad_axis"].mean()),
                "movement_over_uncertainty_rate": float(group["movement_over_selector_uncertainty"].mean()),
                "raw05_novel_movement_rate": float(group["raw05_novel_movement"].mean()),
                "majority_beats_a2c8_rate": float(group["scenario_majority_beats_a2c8"].mean()),
                "best_file": str(best["file"]),
                "best_source_path": str(best["source_path"]),
                "best_priority_score": float(best["submission_priority_score"]),
                "best_selector_p90_delta": float(best["selector_p90_delta_vs_a2c8_public"]),
                "best_selector_mean_delta": float(best["selector_delta_vs_a2c8_public"]),
                "best_beats_a2c8_rate": float(best["beats_a2c8_scenario_rate"]),
                "best_bad_axis_abs_load": float(best["bad_axis_abs_load"]),
                "best_mean_abs_move_vs_a2c8": float(best["mean_abs_move_vs_a2c8"]),
            }
        )
    return pd.DataFrame(rows).sort_values(["escape_candidates", "best_priority_score"], ascending=[False, True]).reset_index(drop=True)


def write_report(scored: pd.DataFrame, short: pd.DataFrame, families: pd.DataFrame, skipped: pd.DataFrame) -> None:
    resolved = scored[scored["resolved_better_than_a2c8_gate"]]
    escape = scored[scored["frontier_escape_candidate"]]
    novel_escape = scored[scored["novel_frontier_candidate"]]
    low_bad_large = scored[scored["low_public_bad_axis"] & scored["movement_over_selector_uncertainty"]]
    known = scored[scored["is_known_public"]].copy() if "is_known_public" in scored.columns else pd.DataFrame()
    top_cols = [
        "source_path",
        "candidate_family",
        "selector_stress_mean",
        "selector_delta_vs_a2c8_public",
        "selector_p90_delta_vs_a2c8_public",
        "selector_stress_spread",
        "beats_a2c8_scenario_rate",
        "frontier_escape_candidate",
        "novel_frontier_candidate",
        "resolved_better_than_a2c8_gate",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "mean_abs_move_vs_raw05",
        "submission_priority_score",
    ]
    top_cols = [c for c in top_cols if c in scored.columns]
    known_cols = ["source_path", "known_public_lb", "selector_delta_vs_a2c8_public", "selector_p90_delta_vs_a2c8_public", "bad_axis_abs_load", "mean_abs_move_vs_a2c8"]
    known_cols = [c for c in known_cols if c in known.columns]

    lines = [
        "# JEPA Selector Frontier Audit",
        "",
        "This audit expands the previous 213-row candidate check to the JEPA-related submission universe and asks whether any existing representation moves far enough beyond selector uncertainty while staying off the known public-bad axes.",
        "",
        "## Scope",
        "",
        f"- Scored candidates: `{len(scored)}`.",
        f"- Skipped paths: `{len(skipped)}`.",
        f"- Selector uncertainty reference: `{SELECTOR_UNCERTAINTY:.9f}` from a2c8 stress spread.",
        f"- Public-bad-axis limit: `{BAD_AXIS_LIMIT:.3f}`.",
        "",
        "## Gate Counts",
        "",
        f"- Resolved-better than a2c8 gate: `{len(resolved)}`.",
        f"- Frontier escape candidates: `{len(escape)}`.",
        f"- Novel frontier candidates, also moved away from raw05: `{len(novel_escape)}`.",
        f"- Low-bad-axis + movement-over-uncertainty candidates: `{len(low_bad_large)}`.",
        "",
        "## Family Summary",
        "",
        "```csv",
        families.round(9).to_csv(index=False).strip(),
        "```",
        "",
        "## Shortlist",
        "",
        "```csv",
        short[top_cols].head(40).round(9).to_csv(index=False).strip(),
        "```",
        "",
        "## Known Controls In This Audit",
        "",
        "```csv",
        (known[known_cols].sort_values("known_public_lb").round(9).to_csv(index=False).strip() if not known.empty else "missing"),
        "```",
        "",
        "## Read",
        "",
        "- `resolved_better_than_a2c8_gate` is the strict submission gate. A candidate failing it is not evidence of a public improvement.",
        "- `frontier_escape_candidate` is a research gate: enough movement, low bad-axis load, tolerable p90 selector damage, and majority scenario wins. It can justify the next experiment family, not an automatic submission.",
        "- `novel_frontier_candidate` additionally requires movement away from raw05. This is the important gate for escaping the current plateau instead of rediscovering raw05-compatible micro-variants.",
        "- If no strict winner appears, the next useful action is not more raw05-compatible blending. It is a representation run that increases movement while preserving the low-bad-axis constraint.",
        "",
        "## Files",
        "",
        f"- `{FULL_OUT.name}`",
        f"- `{SHORT_OUT.name}`",
        f"- `{FAMILY_OUT.name}`",
        f"- `{SKIPPED_OUT.name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEYS).reset_index(drop=True)

    known, refs, ref_vecs = build_known_and_refs(sample)
    candidates, skipped = build_candidate_geometry(sample, refs, ref_vecs)

    known_files = set(known["file"].astype(str))
    candidates["is_known_public"] = candidates["file"].astype(str).isin(known_files)
    candidates["known_public_lb"] = np.nan
    for _, rec in known.iterrows():
        candidates.loc[candidates["file"].astype(str).eq(str(rec["file"])), "known_public_lb"] = float(rec["public_lb"])

    candidates = pd.concat([candidates, known[~known["file"].astype(str).isin(set(candidates["file"].astype(str)))]]).reset_index(drop=True)
    models = evaluate_models(known)
    proxy_scored = fit_all_predict(known, candidates, models)
    stress_scored = candidate_stress_scores(known, proxy_scored)

    meta_cols = ["source_path", "candidate_family"]
    stress_scored = stress_scored.merge(candidates[["file", *meta_cols]].drop_duplicates("file"), on="file", how="left")
    scored = add_frontier_flags(stress_scored)
    families = family_summary(scored)
    short = scored[
        scored["frontier_escape_candidate"]
        | scored["novel_frontier_candidate"]
        | scored["resolved_better_than_a2c8_gate"]
        | (scored["low_public_bad_axis"] & scored["movement_over_selector_uncertainty"])
    ].copy()
    if short.empty:
        short = scored.head(80).copy()
    else:
        short = short.sort_values(
            ["resolved_better_than_a2c8_gate", "novel_frontier_candidate", "frontier_escape_candidate", "submission_priority_score"],
            ascending=[False, False, False, True],
        ).head(160)

    scored.to_csv(FULL_OUT, index=False)
    short.to_csv(SHORT_OUT, index=False)
    families.to_csv(FAMILY_OUT, index=False)
    skipped.to_csv(SKIPPED_OUT, index=False)
    write_report(scored, short, families, skipped)

    print(REPORT_OUT)
    print("[counts]")
    print(
        {
            "scored": len(scored),
            "skipped": len(skipped),
            "resolved_better": int(scored["resolved_better_than_a2c8_gate"].sum()),
            "frontier_escape": int(scored["frontier_escape_candidate"].sum()),
            "novel_frontier": int(scored["novel_frontier_candidate"].sum()),
            "low_bad_large_move": int((scored["low_public_bad_axis"] & scored["movement_over_selector_uncertainty"]).sum()),
        }
    )
    print("[family top]")
    print(families.head(20).round(9).to_string(index=False))
    print("[shortlist top]")
    print(
        short[
            [
                "source_path",
                "candidate_family",
                "selector_delta_vs_a2c8_public",
                "selector_p90_delta_vs_a2c8_public",
                "beats_a2c8_scenario_rate",
                "frontier_escape_candidate",
                "novel_frontier_candidate",
                "bad_axis_abs_load",
                "mean_abs_move_vs_a2c8",
                "submission_priority_score",
            ]
        ]
        .head(25)
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
