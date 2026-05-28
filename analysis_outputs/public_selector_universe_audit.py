from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_subset_selector_stress import candidate_stress_scores  # noqa: E402
from jepa_selector_frontier_audit import (  # noqa: E402
    BAD_AXIS_LIMIT,
    P90_SOFT_LIMIT,
    SELECTOR_UNCERTAINTY,
)
from public_anchor_bottleneck_decomposition import (  # noqa: E402
    A2C8,
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


FULL_OUT = OUT / "public_selector_universe_audit_candidates.csv"
SHORT_OUT = OUT / "public_selector_universe_audit_shortlist.csv"
FAMILY_OUT = OUT / "public_selector_universe_audit_family_summary.csv"
SKIPPED_OUT = OUT / "public_selector_universe_audit_skipped.csv"
REPORT_OUT = OUT / "public_selector_universe_audit_report.md"


def discover_submission_paths() -> list[Path]:
    paths: list[Path] = []
    for base in [OUT, JEPA]:
        paths.extend(base.glob("submission*.csv"))

    refs = [OUT / STAGE2, JEPA / RAW05, OUT / A2C8, OUT / FINAL9, OUT / ORDINAL, JEPA / Q2_BAD, JEPA / RESID_BAD, JEPA / LEJEPA_BAD]
    paths.extend(path for path in refs if path.exists())

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
    rel = str(path.relative_to(ROOT)).lower()
    name = path.name.lower()
    if "frontier_cvjepa" in name:
        return "frontier_cvjepa"
    if "cvjepa" in name:
        return "cvjepa"
    if "raw_timeline" in rel:
        return "raw_timeline"
    if "raw05_jepa" in rel:
        return "raw05_jepa"
    if "lejepa" in rel:
        return "lejepa"
    if "neural_episode_rawstack" in rel:
        return "neural_episode_rawstack"
    if "episode_rawstack" in rel or "episode_retrieval" in rel or "subject_episode_graph" in rel:
        return "episode_graph_rawstack"
    if "sparseladder" in name or "sparsejepa" in name or "sparse_direction" in rel:
        return "sparse_jepa_ladder"
    if "directrob" in name:
        return "directrob"
    if "directcons" in name:
        return "directcons"
    if "direct" in name or "inverse" in name:
        return "direct_inverse"
    if "hiddenblock" in name or "seqmotif" in name or "sequence_motif" in rel:
        return "hiddenblock_seqmotif"
    if "targetabl" in name or "targetwise" in name:
        return "targetwise"
    if "public6entropy" in name:
        return "public6entropy"
    if "axisbridge" in name or "axisrepair" in name or "axiscap" in name or "axis" in name:
        return "axis_repair"
    if "blockorth" in name:
        return "blockorth"
    if "blockscale" in name:
        return "blockscale"
    if "blockpublic" in name:
        return "blockpublic"
    if "publicmask" in name:
        return "publicmask"
    if "energy" in name:
        return "energy_gate"
    if "mixmin" in name:
        return "mixmin"
    if "q2" in name:
        return "q2_specific"
    if "jepa" in rel:
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

    rows = []
    for rec in known_public_table().to_dict("records"):
        row = feature_row(str(rec["file"]), sample, refs, ref_vecs)
        row.update(rec)
        row["file"] = str(rec["file"])
        row["source_path"] = str(rec["file"])
        row["candidate_family"] = "known_public"
        rows.append(row)
    return pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True), refs, ref_vecs


def build_candidate_geometry(sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    skipped: list[dict[str, str]] = []
    sample_keys = sample[KEYS]
    paths = discover_submission_paths()

    for i, path in enumerate(paths, start=1):
        rel = str(path.relative_to(ROOT))
        ok, reason = has_submission_schema(path)
        if not ok:
            skipped.append({"source_path": rel, "reason": reason})
            continue
        try:
            df_keys = pd.read_csv(path, usecols=KEYS, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)
            if not df_keys[KEYS].equals(sample_keys):
                skipped.append({"source_path": rel, "reason": "key_mismatch"})
                continue
            row = feature_row(path, sample, refs, ref_vecs)
        except Exception as exc:  # noqa: BLE001
            skipped.append({"source_path": rel, "reason": f"load_error:{type(exc).__name__}"})
            continue
        row["file"] = rel
        row["source_path"] = rel
        row["basename"] = path.name
        row["candidate_family"] = family_name(path)
        rows.append(row)
        if i % 1000 == 0:
            print(f"scored {i}/{len(paths)} paths; valid={len(rows)} skipped={len(skipped)}", flush=True)

    frame = pd.DataFrame(rows).drop_duplicates("source_path").reset_index(drop=True)
    if frame.empty:
        raise RuntimeError("No valid submissions found.")
    return frame, pd.DataFrame(skipped)


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
        - 0.00002 * out["raw05_novel_movement"].astype(float)
    )
    return out.sort_values(
        ["resolved_better_than_a2c8_gate", "novel_frontier_candidate", "frontier_escape_candidate", "submission_priority_score"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)


def family_summary(scored: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for family, group in scored.groupby("candidate_family", sort=False):
        best = group.sort_values("submission_priority_score").iloc[0]
        rows.append(
            {
                "candidate_family": family,
                "n": int(len(group)),
                "resolved_better": int(group["resolved_better_than_a2c8_gate"].sum()),
                "escape_candidates": int(group["frontier_escape_candidate"].sum()),
                "novel_escape_candidates": int(group["novel_frontier_candidate"].sum()),
                "low_bad_axis_rate": float(group["low_public_bad_axis"].mean()),
                "movement_over_uncertainty_rate": float(group["movement_over_selector_uncertainty"].mean()),
                "raw05_novel_movement_rate": float(group["raw05_novel_movement"].mean()),
                "majority_beats_a2c8_rate": float(group["scenario_majority_beats_a2c8"].mean()),
                "best_source_path": str(best["source_path"]),
                "best_priority_score": float(best["submission_priority_score"]),
                "best_selector_p90_delta": float(best["selector_p90_delta_vs_a2c8_public"]),
                "best_selector_mean_delta": float(best["selector_delta_vs_a2c8_public"]),
                "best_beats_a2c8_rate": float(best["beats_a2c8_scenario_rate"]),
                "best_bad_axis_abs_load": float(best["bad_axis_abs_load"]),
                "best_mean_abs_move_vs_a2c8": float(best["mean_abs_move_vs_a2c8"]),
                "best_mean_abs_move_vs_raw05": float(best["mean_abs_move_vs_raw05"]),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["resolved_better", "novel_escape_candidates", "escape_candidates", "best_priority_score"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)


def write_report(scored: pd.DataFrame, short: pd.DataFrame, families: pd.DataFrame, skipped: pd.DataFrame) -> None:
    resolved = scored[scored["resolved_better_than_a2c8_gate"]]
    escape = scored[scored["frontier_escape_candidate"]]
    novel = scored[scored["novel_frontier_candidate"]]
    known_mask = scored["is_known_public"].fillna(False).astype(bool) if "is_known_public" in scored.columns else pd.Series(False, index=scored.index)
    known = scored[known_mask].copy()

    top_cols = [
        "source_path",
        "candidate_family",
        "selector_delta_vs_a2c8_public",
        "selector_p90_delta_vs_a2c8_public",
        "selector_stress_spread",
        "beats_a2c8_scenario_rate",
        "resolved_better_than_a2c8_gate",
        "frontier_escape_candidate",
        "novel_frontier_candidate",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "mean_abs_move_vs_raw05",
        "submission_priority_score",
    ]
    known_cols = ["source_path", "known_public_lb", "selector_delta_vs_a2c8_public", "selector_p90_delta_vs_a2c8_public", "bad_axis_abs_load", "mean_abs_move_vs_a2c8"]

    lines = [
        "# Public Selector Universe Audit",
        "",
        "This audit removes the previous JEPA filename filter and scores every valid `submission*.csv` under `analysis_outputs/` and `jepa/` with the same public-anchor stress harness.",
        "",
        "## Scope",
        "",
        f"- Scored candidates: `{len(scored)}`.",
        f"- Skipped paths: `{len(skipped)}`.",
        f"- Selector uncertainty reference: `{SELECTOR_UNCERTAINTY:.9f}`.",
        f"- Public-bad-axis limit: `{BAD_AXIS_LIMIT:.3f}`.",
        "",
        "## Gate Counts",
        "",
        f"- Resolved-better than a2c8 gate: `{len(resolved)}`.",
        f"- Frontier escape candidates: `{len(escape)}`.",
        f"- Novel frontier candidates: `{len(novel)}`.",
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
        short[top_cols].head(80).round(9).to_csv(index=False).strip(),
        "```",
        "",
        "## Known Controls",
        "",
        "```csv",
        (known[known_cols].sort_values("known_public_lb").round(9).to_csv(index=False).strip() if not known.empty else "missing"),
        "```",
        "",
        "## Read",
        "",
        "- If this universe audit still has zero strict winners, the plateau is not a naming-filter artifact.",
        "- Families with many novel escape candidates but zero strict winners are useful teacher/gate pools, not direct submission evidence.",
        "- Families with high movement but high bad-axis load should be used only as negative axes or anti-directions.",
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
    candidates["is_known_public"] = candidates["basename"].astype(str).isin(known_files)
    candidates["known_public_lb"] = np.nan
    for _, rec in known.iterrows():
        candidates.loc[candidates["basename"].astype(str).eq(str(rec["file"])), "known_public_lb"] = float(rec["public_lb"])

    anchor_rows = known.copy()
    anchor_rows["basename"] = anchor_rows["file"].astype(str)
    candidates = pd.concat([candidates, anchor_rows], ignore_index=True, sort=False)
    candidates = candidates.drop_duplicates("file").reset_index(drop=True)

    models = evaluate_models(known)
    proxy_scored = fit_all_predict(known, candidates, models)
    stress_scored = candidate_stress_scores(known, proxy_scored)

    meta_cols = ["source_path", "basename", "candidate_family"]
    stress_scored = stress_scored.merge(candidates[["file", *meta_cols]].drop_duplicates("file"), on="file", how="left")
    scored = add_frontier_flags(stress_scored)
    families = family_summary(scored)
    short = scored[
        scored["resolved_better_than_a2c8_gate"]
        | scored["novel_frontier_candidate"]
        | scored["frontier_escape_candidate"]
        | (scored["low_public_bad_axis"] & scored["movement_over_selector_uncertainty"] & scored["scenario_majority_beats_a2c8"])
    ].copy()
    if short.empty:
        short = scored.head(200).copy()
    else:
        short = short.head(240)

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
        }
    )
    print("[family top]")
    print(families.head(24).round(9).to_string(index=False))
    print("[shortlist top]")
    print(
        short[
            [
                "source_path",
                "candidate_family",
                "selector_delta_vs_a2c8_public",
                "selector_p90_delta_vs_a2c8_public",
                "beats_a2c8_scenario_rate",
                "novel_frontier_candidate",
                "bad_axis_abs_load",
                "mean_abs_move_vs_a2c8",
                "mean_abs_move_vs_raw05",
                "submission_priority_score",
            ]
        ]
        .head(30)
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
