#!/usr/bin/env python3
"""E324: high-repetition stress for E323 ready candidates.

E323 produced the first public-free ready files after removing null-common
movement from E322 near misses.  E324 asks whether that readiness survives a
larger placement-null sample.

No public LB is used.
"""

from __future__ import annotations

from pathlib import Path
import sys
import warnings

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e324_e323_ready_highrep_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import TARGETS, clip_prob  # noqa: E402
from e297_episode_state_materializer import feature_rows, sigmoid  # noqa: E402
from e315_human_ready_composition_materializer import cap_delta, md  # noqa: E402
from e321_mode_adversarial_action_health import PROMOTION_THRESHOLDS  # noqa: E402
from e323_null_common_residual_generator import current_frame, load_delta, null_delta, short_hash  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

E323_GOVERNOR = OUT / "e323_null_common_residual_governor_audit.csv"
GOVERNOR_OUT = OUT / "e324_e323_ready_highrep_governor_audit.csv"
NULL_MAP_OUT = OUT / "e324_e323_ready_highrep_null_map.csv"
SUMMARY_OUT = OUT / "e324_e323_ready_highrep_summary.csv"
REPORT_OUT = OUT / "e324_e323_ready_highrep_report.md"

PLACEMENT_MODES = ["row", "subject", "dateblock"]
ALL_NULL_MODES = ["row", "subject", "dateblock", "target_perm", "sign_flip", "q_s_swap"]
PLACEMENT_REPS = 64
TARGET_REPS = 64
CAP = 0.35


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def ready_candidates() -> pd.DataFrame:
    gov = pd.read_csv(E323_GOVERNOR)
    ready = gov[gov["fresh_public_free_submission_ready"].astype(bool)].copy()
    if ready.empty:
        return ready
    return ready.sort_values(
        ["fresh_null_strict_rate", "fresh_actual_p90", "fresh_mean_dominance"],
        ascending=[True, True, False],
    ).reset_index(drop=True)


def write_null(current: pd.DataFrame, delta: np.ndarray, basename: str, mode: str, rep: int, meta: pd.DataFrame) -> Path:
    out = current.copy()
    nd = cap_delta(null_delta(delta, mode, rep, meta, basename), CAP)
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + nd
    out[TARGETS] = clip_prob(sigmoid(logits))
    NULL_DIR.mkdir(exist_ok=True)
    safe_name = basename[:72].replace("/", "_")
    path = NULL_DIR / f"submission_e324null_{safe_name}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def build_nulls(ready: pd.DataFrame, current: pd.DataFrame) -> tuple[pd.DataFrame, list[Path]]:
    # Reuse the existing E323 metadata columns for subject/dateblock shuffles.
    # They were aligned in E323 and carried through the same 250 test rows.
    from e288_lifestyle_bundle_jepa_audit import load_frames  # local import to keep script startup cheap
    from e297_episode_state_materializer import align_meta_to_current

    base, _, _, _ = load_frames()
    test_df = base.loc[base["split"].eq("test")].reset_index(drop=True)
    meta = align_meta_to_current(test_df, current)

    rows: list[dict[str, object]] = []
    paths: list[Path] = []
    for _, cand in ready.iterrows():
        basename = str(cand["basename"])
        delta = load_delta(OUT / basename, current)
        for mode in ALL_NULL_MODES:
            if mode in PLACEMENT_MODES:
                reps = PLACEMENT_REPS
            elif mode == "target_perm":
                reps = TARGET_REPS
            else:
                reps = 1
            for rep in range(reps):
                path = write_null(current, delta, basename, mode, rep, meta)
                paths.append(path)
                rows.append(
                    {
                        "source_basename": basename,
                        "null_basename": path.name,
                        "null_path": rel(path),
                        "mode": mode,
                        "rep": rep,
                    }
                )
    return pd.DataFrame(rows), paths


def run() -> tuple[pd.DataFrame, pd.DataFrame]:
    current = current_frame()
    ready = ready_candidates()
    if ready.empty:
        empty = pd.DataFrame()
        empty.to_csv(NULL_MAP_OUT, index=False)
        empty.to_csv(GOVERNOR_OUT, index=False)
        return empty, empty

    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    null_map, null_paths = build_nulls(ready, current)
    candidate_paths = [OUT / b for b in ready["basename"]]
    features = feature_rows([OUT / CURRENT, *candidate_paths, *null_paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    cand_scores = scores[scores["basename"].isin(ready["basename"])].copy()
    null_scores = scores[scores["basename"].isin(null_map["null_basename"])].copy()

    rows: list[dict[str, object]] = []
    for _, cand in ready.iterrows():
        basename = str(cand["basename"])
        actual = cand_scores[cand_scores["basename"].eq(basename)].iloc[0]
        these_null = null_scores.merge(
            null_map[null_map["source_basename"].eq(basename)][["null_basename", "mode", "rep"]],
            left_on="basename",
            right_on="null_basename",
            how="inner",
        )
        actual_p90 = float(actual["pred_delta_vs_current_p90"])
        actual_mean = float(actual["pred_delta_vs_current_mean"])
        old_strict = bool(actual["strict_promote_gate"])
        p90_vals = these_null["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        mean_vals = these_null["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        null_strict_rate = float(these_null["strict_promote_gate"].astype(bool).mean()) if len(these_null) else 1.0
        p90_dominance = float(np.mean(actual_p90 < p90_vals)) if len(p90_vals) else 0.0
        mean_dominance = float(np.mean(actual_mean < mean_vals)) if len(mean_vals) else 0.0
        mode_doms: dict[str, float] = {}
        mode_strict: dict[str, float] = {}
        mode_counts: dict[str, int] = {}
        for mode, part in these_null.groupby("mode"):
            vals = part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            mode_doms[f"{mode}_p90_dominance"] = float(np.mean(actual_p90 < vals))
            mode_strict[f"{mode}_null_strict_rate"] = float(part["strict_promote_gate"].astype(bool).mean())
            mode_counts[f"{mode}_count"] = int(len(part))
        worst_mode = float(min(mode_doms.values())) if mode_doms else 0.0
        ready_highrep = bool(
            old_strict
            and actual_p90 <= -2.0e-5
            and null_strict_rate <= PROMOTION_THRESHOLDS["null_strict_rate"]
            and p90_dominance >= PROMOTION_THRESHOLDS["p90_dominance"]
            and mean_dominance >= PROMOTION_THRESHOLDS["mean_dominance"]
            and worst_mode >= PROMOTION_THRESHOLDS["worst_mode_p90_dominance"]
        )
        rows.append(
            {
                "basename": basename,
                "parent_basename": cand.get("parent_basename", ""),
                "base_variant": cand.get("base_variant", ""),
                "source_path": cand.get("source_path", ""),
                "highrep_old_strict_promote": old_strict,
                "highrep_actual_mean": actual_mean,
                "highrep_actual_p10": float(actual["pred_delta_vs_current_p10"]),
                "highrep_actual_p90": actual_p90,
                "highrep_actual_beats_current_rate": float(actual["pred_beats_current_rate"]),
                "highrep_null_count": int(len(these_null)),
                "highrep_null_strict_rate": null_strict_rate,
                "highrep_p90_dominance": p90_dominance,
                "highrep_mean_dominance": mean_dominance,
                "highrep_worst_mode_p90_dominance": worst_mode,
                **{f"highrep_{k}": v for k, v in mode_doms.items()},
                **{f"highrep_{k}": v for k, v in mode_strict.items()},
                **{f"highrep_{k}": v for k, v in mode_counts.items()},
                "highrep_public_free_submission_ready": ready_highrep,
                "highrep_final_decision": "public_free_submission_ready" if ready_highrep else "blocked_by_e324_highrep_nulls",
            }
        )
    governor = pd.DataFrame(rows).sort_values(
        [
            "highrep_public_free_submission_ready",
            "highrep_null_strict_rate",
            "highrep_actual_p90",
        ],
        ascending=[False, True, True],
    )
    null_map.to_csv(NULL_MAP_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    write_report(governor, null_map)
    return governor, null_map


def write_report(governor: pd.DataFrame, null_map: pd.DataFrame) -> None:
    summary = pd.DataFrame(
        [
            {
                "slice": "e323_ready_highrep",
                "rows": int(len(governor)),
                "ready": int(governor["highrep_public_free_submission_ready"].sum()) if not governor.empty else 0,
                "best_p90": float(governor["highrep_actual_p90"].min()) if not governor.empty else np.nan,
                "best_null_strict": float(governor["highrep_null_strict_rate"].min()) if not governor.empty else np.nan,
                "best_worst_mode": float(governor["highrep_worst_mode_p90_dominance"].max()) if not governor.empty else np.nan,
                "null_rows": int(len(null_map)),
            }
        ]
    )
    summary.to_csv(SUMMARY_OUT, index=False)
    cols = [
        "basename",
        "base_variant",
        "highrep_actual_p90",
        "highrep_null_strict_rate",
        "highrep_p90_dominance",
        "highrep_mean_dominance",
        "highrep_worst_mode_p90_dominance",
        "highrep_row_null_strict_rate",
        "highrep_subject_null_strict_rate",
        "highrep_dateblock_null_strict_rate",
        "highrep_public_free_submission_ready",
        "highrep_final_decision",
    ]
    ready = governor[governor["highrep_public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    lines = [
        "# E324 E323 Ready High-Rep Stress",
        "",
        "Public LB was not used.",
        "",
        "## Summary",
        "",
        md(summary, n=5),
        "",
        "## High-Rep Governor",
        "",
        md(governor[[c for c in cols if c in governor.columns]] if not governor.empty else governor, n=20),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        lines.append(f"- `{ready.iloc[0]['basename']}` survives high-repetition local null stress.")
    else:
        lines.append("- No E323 ready file survives high-repetition local null stress.")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{GOVERNOR_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{REPORT_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    governor, null_map = run()
    ready_count = int(governor["highrep_public_free_submission_ready"].sum()) if not governor.empty else 0
    print(f"ready_candidates={len(governor)}")
    print(f"null_rows={len(null_map)}")
    print(f"highrep_ready={ready_count}")
    if not governor.empty:
        print(f"best_highrep_p90={governor['highrep_actual_p90'].min():.9f}")
        print(f"best_highrep_null_strict={governor['highrep_null_strict_rate'].min():.6f}")
        print(f"best_highrep_worst_mode={governor['highrep_worst_mode_p90_dominance'].max():.6f}")
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
