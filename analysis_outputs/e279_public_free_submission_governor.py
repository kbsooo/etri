#!/usr/bin/env python3
"""E279: public-free submission governor.

The public LB is too scarce to use as the validation loop. This governor turns
the latest E276/E277/E278 lesson into one executable rule:

1. score a candidate with the known-public selector;
2. compare it with matched row/subject/dateblock shuffle nulls that preserve
   its logit-delta magnitude but destroy row placement;
3. require train row-alignment support when the candidate belongs to a
   q-sleep diary policy family;
4. block known-public losers even if the old selector would have promoted them.

No new public LB is used and no submission is recommended unless it survives all
local gates.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e279_public_free_governor_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import (  # noqa: E402
    CURRENT,
    evaluate_models,
    score_candidates,
    selected_models,
)
from e274_target_specific_diary_energy_audit import FEATURE_PATH, clip_prob  # noqa: E402
from public_anchor_bottleneck_decomposition import (  # noqa: E402
    KEYS,
    TARGETS,
    feature_row,
    known_public_table,
    load_sub,
    logit,
)
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


RNG_SEED = 20260531 + 279
N_REPS = 7

SCORES_OUT = OUT / "e279_public_free_governor_scores.csv"
NULLS_OUT = OUT / "e279_public_free_governor_nulls.csv"
SUMMARY_OUT = OUT / "e279_public_free_governor_summary.csv"
CALIBRATION_OUT = OUT / "e279_public_free_governor_known_calibration.csv"
REPORT_OUT = OUT / "e279_public_free_governor_report.md"


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def short_hash(df: pd.DataFrame) -> str:
    arr = np.asarray(df[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


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


def has_submission_schema(path: Path) -> bool:
    try:
        cols = pd.read_csv(path, nrows=0).columns.tolist()
    except Exception:  # noqa: BLE001
        return False
    return set(KEYS + TARGETS).issubset(cols)


def include_active_candidate(path: Path, public_probe_names: set[str]) -> bool:
    name = path.name
    if not name.startswith("submission_") or not name.endswith(".csv"):
        return False
    blocked_tokens = [
        "e277null",
        "e279null",
        "shuffle_",
        "_shuffle",
        "e276_inverse",
        "inverse_primary",
    ]
    if any(token in name for token in blocked_tokens):
        return False
    active_prefixes = (
        "submission_e247_",
        "submission_e250_",
        "submission_e252_",
        "submission_e256_",
        "submission_e267_",
        "submission_e269_",
        "submission_e271_",
        "submission_e274_",
        "submission_e275_",
        "submission_e276_",
    )
    return name in public_probe_names or name.startswith(active_prefixes)


def discover_candidate_paths(sample: pd.DataFrame) -> list[Path]:
    sample_keys = sample[KEYS].copy()
    rows: list[Path] = []
    seen: set[Path] = set()
    public_probe_names = set(known_public_table()["file"].astype(str))

    for file_name in sorted(public_probe_names):
        path = OUT / file_name
        if not path.exists():
            alt = ROOT / "jepa" / file_name
            path = alt if alt.exists() else path
        if path.exists() and path.resolve() not in seen:
            seen.add(path.resolve())
            rows.append(path)

    for path in sorted(OUT.glob("submission_*.csv")):
        if not include_active_candidate(path, public_probe_names):
            continue
        if path.resolve() in seen or not has_submission_schema(path):
            continue
        try:
            keys = pd.read_csv(path, usecols=KEYS, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)
        except Exception:  # noqa: BLE001
            continue
        if not keys[KEYS].equals(sample_keys):
            continue
        seen.add(path.resolve())
        rows.append(path)

    current_path = OUT / CURRENT
    if current_path.resolve() not in seen:
        rows.insert(0, current_path)
    return rows


def test_meta(sample: pd.DataFrame) -> pd.DataFrame:
    features = pd.read_parquet(FEATURE_PATH)
    meta = features[features["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    out = meta[KEYS + ["dateblock_group"]].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col])
    if not out[KEYS].reset_index(drop=True).equals(sample[KEYS].reset_index(drop=True)):
        raise RuntimeError("E279 metadata does not align with current submission keys")
    return out


def write_null_candidate(base: pd.DataFrame, delta: np.ndarray, meta: pd.DataFrame, source_path: Path, mode: str, rep: int, seed: int) -> Path:
    rng = np.random.default_rng(seed)
    shuffled = np.zeros_like(delta)
    for target_idx in range(delta.shape[1]):
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
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    out[TARGETS] = clip_prob(sigmoid(base_logits + shuffled))
    stem = source_path.stem.replace("submission_", "")[:70]
    tmp_name = f"submission_e279null_{stem}_{mode}_r{rep}_{short_hash(out)}.csv"
    path = NULL_DIR / tmp_name
    out.to_csv(path, index=False)
    return path


def generate_nulls(candidate_paths: list[Path], sample: pd.DataFrame) -> pd.DataFrame:
    NULL_DIR.mkdir(exist_ok=True)
    base = load_sub(CURRENT)
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    meta = test_meta(sample)
    rows: list[dict[str, object]] = []

    for cand_idx, path in enumerate(candidate_paths):
        if path.name == CURRENT:
            continue
        candidate = load_sub(path, sample)
        delta = logit(candidate[TARGETS].to_numpy(dtype=np.float64)) - base_logits
        if np.max(np.abs(delta)) < 1.0e-12:
            continue
        for mode in ["row", "subject", "dateblock"]:
            for rep in range(N_REPS):
                seed = RNG_SEED + cand_idx * 1009 + rep * 97 + {"row": 0, "subject": 1, "dateblock": 2}[mode]
                null_path = write_null_candidate(base, delta, meta, path, mode, rep, seed)
                rows.append(
                    {
                        "source_path": rel(path),
                        "source_basename": path.name,
                        "null_path": rel(null_path),
                        "null_basename": null_path.name,
                        "mode": mode,
                        "rep": rep,
                        "seed": seed,
                    }
                )
    nulls = pd.DataFrame(rows)
    nulls.to_csv(NULLS_OUT, index=False)
    return nulls


def feature_rows(paths: list[Path], sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for path in paths:
        key = rel(path)
        if key in seen:
            continue
        seen.add(key)
        row = feature_row(path, sample, refs, ref_vecs)
        row["file"] = key
        row["source_path"] = key
        row["basename"] = path.name
        rows.append(row)
    return pd.DataFrame(rows)


def policy_id_for_candidate(name: str) -> str:
    checks = [
        ("q3_only", "q3_only"),
        ("q12_only", "q12_only"),
        ("nonjepa_only", "nonjepa_only"),
        ("jepa_only", "jepa_only"),
        ("only_bedtime_phone", "only_bedtime_phone"),
        ("only_mobility_context", "only_mobility_context"),
        ("only_routine_calendar", "only_routine_calendar"),
        ("only_cognitive_money", "only_cognitive_money"),
        ("only_social_comm", "only_social_comm"),
        ("only_media_game", "only_media_game"),
        ("only_diary_global", "only_diary_global"),
        ("no_bedtime_phone", "no_bedtime_phone"),
        ("no_mobility_context", "no_mobility_context"),
        ("no_routine_calendar", "no_routine_calendar"),
        ("no_cognitive_money", "no_cognitive_money"),
        ("no_social_comm", "no_social_comm"),
        ("no_media_game", "no_media_game"),
        ("no_diary_global", "no_diary_global"),
    ]
    for token, policy in checks:
        if token in name:
            return policy
    if "q_sleep" in name or "qsleep" in name or "story_full" in name:
        return "full_qsleep"
    return ""


def train_support_table() -> pd.DataFrame:
    path = OUT / "e278_train_row_alignment_null_summary.csv"
    if not path.exists():
        return pd.DataFrame()
    raw = pd.read_csv(path)
    rows = []
    for policy, group in raw.groupby("candidate_id", dropna=False):
        rows.append(
            {
                "train_policy_id": str(policy),
                "train_gate_splits": int(group["train_align_gate"].astype(bool).sum()),
                "train_gate_both_splits": bool(group["train_align_gate"].astype(bool).sum() >= 2),
                "train_actual_delta_mean": float(group["actual_delta"].mean()),
                "train_actual_delta_max": float(group["actual_delta"].max()),
                "train_min_dominance": float(group["dominance"].min()),
                "train_min_mode_dominance": float(
                    group[["row_dominance", "subject_dominance", "dateblock_dominance"]].min(axis=1).min()
                ),
            }
        )
    return pd.DataFrame(rows)


def make_summary(scores: pd.DataFrame, candidate_paths: list[Path], nulls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    path_frame = pd.DataFrame(
        [{"source_path": rel(path), "basename": path.name, "is_current": path.name == CURRENT} for path in candidate_paths]
    )
    actual = scores.merge(path_frame, on=["source_path", "basename"], how="inner")
    null_scores = scores.merge(nulls, left_on="source_path", right_on="null_path", how="inner")
    public = known_public_table()
    current_public = float(public.loc[public["file"].eq(CURRENT), "public_lb"].iloc[0])
    public_map = public.set_index("file")["public_lb"].to_dict()
    support = train_support_table()
    support_map = support.set_index("train_policy_id").to_dict("index") if not support.empty else {}

    rows: list[dict[str, object]] = []
    for _, rec in actual.iterrows():
        base_name = str(rec["basename"])
        if bool(rec["is_current"]):
            rows.append(
                {
                    "basename": base_name,
                    "source_path": rec["source_path"],
                    "old_promotion_decision": "current_anchor",
                    "old_strict_promote": False,
                    "actual_mean": 0.0,
                    "actual_p90": 0.0,
                    "public_lb_if_known": current_public,
                    "public_delta_vs_current": 0.0,
                    "final_governor_decision": "current_anchor",
                    "public_free_submission_ready": False,
                }
            )
            continue

        matched = null_scores[null_scores["source_basename"].eq(base_name)].copy()
        actual_p90 = float(rec["pred_delta_vs_current_p90"])
        actual_mean = float(rec["pred_delta_vs_current_mean"])
        policy = policy_id_for_candidate(base_name)
        train_rec = support_map.get(policy, {})
        public_lb = public_map.get(base_name, np.nan)
        public_delta = float(public_lb - current_public) if pd.notna(public_lb) else np.nan
        known_public_worse = bool(pd.notna(public_delta) and public_delta >= 0.0 and base_name != CURRENT)

        if matched.empty:
            p90_dominance = mean_dominance = worst_mode_dom = np.nan
            null_strict_rate = np.nan
            null_p90_q20 = null_p90_median = null_p90_best = np.nan
            mode_fields: dict[str, object] = {}
            placebo_gate = False
            decision = "blocked_missing_matched_nulls"
        else:
            null_p90 = matched["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            null_mean = matched["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
            strict_null = matched["strict_promote_gate"].astype(bool).to_numpy()
            p90_dominance = float(np.mean(actual_p90 < null_p90))
            mean_dominance = float(np.mean(actual_mean < null_mean))
            null_strict_rate = float(np.mean(strict_null))
            null_p90_q20 = float(np.quantile(null_p90, 0.20))
            null_p90_median = float(np.median(null_p90))
            null_p90_best = float(np.min(null_p90))
            mode_fields = {}
            mode_doms = []
            for mode, group in matched.groupby("mode"):
                g_p90 = group["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
                dom = float(np.mean(actual_p90 < g_p90))
                mode_doms.append(dom)
                mode_fields[f"{mode}_p90_dominance"] = dom
                mode_fields[f"{mode}_null_strict_rate"] = float(group["strict_promote_gate"].astype(bool).mean())
                mode_fields[f"{mode}_best_null_p90"] = float(np.min(g_p90))
            worst_mode_dom = float(min(mode_doms)) if mode_doms else 0.0
            placebo_gate = bool(
                bool(rec["strict_promote_gate"])
                and p90_dominance >= 0.85
                and mean_dominance >= 0.75
                and worst_mode_dom >= 0.65
                and null_strict_rate <= 0.10
                and actual_p90 <= null_p90_q20 - 1.0e-6
            )
            decision = ""

        q_sleep_policy_known = bool(policy)
        train_support_gate = bool(train_rec.get("train_gate_both_splits", False)) if q_sleep_policy_known else np.nan
        train_required_pass = (not q_sleep_policy_known) or train_support_gate

        if known_public_worse:
            decision = "blocked_known_public_worse_than_current"
        elif not bool(rec["strict_promote_gate"]):
            decision = str(rec["promotion_decision"])
        elif not placebo_gate:
            decision = "blocked_by_matched_placebo"
        elif not train_required_pass:
            decision = "blocked_by_train_row_alignment"
        else:
            decision = "public_free_submission_candidate"

        ready = bool(decision == "public_free_submission_candidate")
        rows.append(
            {
                "basename": base_name,
                "source_path": rec["source_path"],
                "old_promotion_decision": rec["promotion_decision"],
                "old_strict_promote": bool(rec["strict_promote_gate"]),
                "actual_mean": actual_mean,
                "actual_p10": float(rec["pred_delta_vs_current_p10"]),
                "actual_p90": actual_p90,
                "actual_beats_current_rate": float(rec["pred_beats_current_rate"]),
                "incremental_bad_axis_vs_current": float(rec["incremental_bad_axis_vs_current"]),
                "null_count": int(len(matched)),
                "null_strict_rate": null_strict_rate,
                "null_p90_q20": null_p90_q20,
                "null_p90_median": null_p90_median,
                "null_p90_best": null_p90_best,
                "p90_dominance": p90_dominance,
                "mean_dominance": mean_dominance,
                "worst_mode_p90_dominance": worst_mode_dom,
                "matched_placebo_gate": placebo_gate,
                "train_policy_id": policy,
                "train_support_gate": train_support_gate,
                "train_gate_splits": train_rec.get("train_gate_splits", np.nan),
                "train_actual_delta_mean": train_rec.get("train_actual_delta_mean", np.nan),
                "train_min_dominance": train_rec.get("train_min_dominance", np.nan),
                "public_lb_if_known": public_lb,
                "public_delta_vs_current": public_delta,
                "known_public_worse_than_current": known_public_worse,
                "final_governor_decision": decision,
                "public_free_submission_ready": ready,
                **mode_fields,
            }
        )

    summary = pd.DataFrame(rows).sort_values(
        ["public_free_submission_ready", "matched_placebo_gate", "old_strict_promote", "actual_p90", "p90_dominance"],
        ascending=[False, False, False, True, False],
    )
    known_cal = summary[pd.notna(summary["public_lb_if_known"])].copy()
    summary.to_csv(SUMMARY_OUT, index=False)
    known_cal.to_csv(CALIBRATION_OUT, index=False)
    return summary, known_cal


def write_report(summary: pd.DataFrame, known_cal: pd.DataFrame, nulls: pd.DataFrame, selected: pd.DataFrame) -> None:
    ready = summary[summary["public_free_submission_ready"].astype(bool)] if not summary.empty else pd.DataFrame()
    old_strict = int(summary["old_strict_promote"].fillna(False).astype(bool).sum()) if not summary.empty else 0
    placebo_pass = int(summary["matched_placebo_gate"].fillna(False).astype(bool).sum()) if "matched_placebo_gate" in summary else 0
    old_false_positive = (
        known_cal[known_cal["old_strict_promote"].fillna(False).astype(bool) & known_cal["known_public_worse_than_current"].fillna(False).astype(bool)]
        if not known_cal.empty
        else pd.DataFrame()
    )
    cols = [
        "basename",
        "final_governor_decision",
        "old_promotion_decision",
        "actual_mean",
        "actual_p90",
        "null_strict_rate",
        "p90_dominance",
        "worst_mode_p90_dominance",
        "matched_placebo_gate",
        "train_policy_id",
        "train_support_gate",
        "public_delta_vs_current",
    ]
    cal_cols = [
        "basename",
        "public_lb_if_known",
        "public_delta_vs_current",
        "old_promotion_decision",
        "old_strict_promote",
        "final_governor_decision",
        "actual_p90",
        "null_strict_rate",
        "p90_dominance",
    ]
    lines = [
        "# E279 Public-Free Submission Governor",
        "",
        "## Question",
        "",
        "Can we decide whether a candidate deserves a scarce public LB slot without submitting it?",
        "",
        "## Governor Rule",
        "",
        "A candidate is submission-ready only if all of these hold:",
        "",
        "- old E272 strict current-anchor gate passes;",
        "- real row placement beats matched row/subject/dateblock shuffle nulls;",
        "- null strict-promote rate is low (`<= 0.10`);",
        "- if the candidate is q-sleep diary-derived, E278 train row-alignment support exists;",
        "- if the candidate already has public LB and is worse than E247, it is blocked.",
        "",
        "## Summary",
        "",
        f"- candidates audited, including current anchor: `{len(summary)}`",
        f"- matched null files generated: `{len(nulls)}`",
        f"- selected E272 selector models: `{len(selected)}`",
        f"- old strict-promote candidates: `{old_strict}`",
        f"- matched-placebo gate passes: `{placebo_pass}`",
        f"- known-public old strict false positives versus E247: `{len(old_false_positive)}`",
        f"- final public-free submission-ready candidates: `{len(ready)}`",
        "",
        "## Candidate Decisions",
        "",
        md_table(summary[cols], n=80) if not summary.empty else "_empty_",
        "",
        "## Known Public Calibration",
        "",
        md_table(known_cal[cal_cols].sort_values("public_lb_if_known"), n=40) if not known_cal.empty else "_empty_",
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        lines.append("At least one candidate survived the governor. Review the row movement manually before spending a public LB slot.")
    else:
        lines.append("No current candidate is submission-ready. This is intentional: E272-style improvement alone is now treated as insufficient unless row placement beats matched placebo nulls.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The governor separates two ideas that were previously mixed together: target/magnitude direction and row-aligned hidden-state evidence. A file can have a favorable Q-side movement direction and still be blocked if the same movement works after shuffling rows.",
            "",
            "For the human/social q-sleep branch, E278 says train row alignment is real, but E279 still requires test-side matched-placebo resistance before any submission recommendation.",
            "",
            "## Files",
            "",
            f"- `{SUMMARY_OUT.name}`",
            f"- `{SCORES_OUT.name}`",
            f"- `{NULLS_OUT.name}`",
            f"- `{CALIBRATION_OUT.name}`",
            f"- `{NULL_DIR.name}/`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    candidate_paths = discover_candidate_paths(load_sub(CURRENT))
    nulls = generate_nulls(candidate_paths, sample)
    null_paths = [ROOT / row["null_path"] for row in nulls.to_dict("records")]
    candidates = feature_rows(candidate_paths + null_paths, sample, refs, ref_vecs)
    model_df = evaluate_models(known)
    scores = score_candidates(known, candidates, model_df)
    scores.to_csv(SCORES_OUT, index=False)
    summary, known_cal = make_summary(scores, candidate_paths, nulls)
    write_report(summary, known_cal, nulls, selected_models(model_df))

    print(REPORT_OUT)
    print(
        summary[
            [
                "basename",
                "final_governor_decision",
                "old_promotion_decision",
                "actual_p90",
                "null_strict_rate",
                "p90_dominance",
                "matched_placebo_gate",
                "train_policy_id",
                "train_support_gate",
                "public_delta_vs_current",
            ]
        ]
        .head(40)
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
