from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from public_pairwise_order_selector import (  # noqa: E402
    build_candidate_features,
    evaluate_pairwise_models,
    rel_path,
    score_candidates,
)
from public_selector_universe_audit import build_known_and_refs, family_name  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
BASE_FILE = ANALYSIS / "submission_frontier_cvjepa_refine_a2c8d2c8.csv"
RAW05_FILE = JEPA / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
LABEL_FLOW_SCORED = ANALYSIS / "label_flow_blockrate_jepa_pairwise_scored.csv"

SCAN_OUT = ANALYSIS / "label_flow_gated_candidate_scan.csv"
SCORED_OUT = ANALYSIS / "label_flow_gated_candidate_pairwise_scored.csv"
SHORTLIST_OUT = ANALYSIS / "label_flow_gated_candidate_shortlist.csv"
REPORT_OUT = ANALYSIS / "label_flow_gated_candidate_scan_report.md"


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def read_submission(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    return df


def target_energy_model() -> tuple[np.ndarray, np.ndarray]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    y = train[TARGETS].to_numpy(dtype=float)
    mu = y.mean(axis=0)
    cov = np.cov(y, rowvar=False)
    cov = np.asarray(cov, dtype=float)
    diag = np.diag(np.diag(cov))
    shrink = 0.35 * diag + 0.65 * cov
    shrink += np.eye(len(TARGETS)) * 0.08
    inv = np.linalg.pinv(shrink)
    return mu, inv


def manifold_energy(p: np.ndarray, mu: np.ndarray, inv: np.ndarray) -> np.ndarray:
    x = np.asarray(p, dtype=float) - mu[None, :]
    return np.sum((x @ inv) * x, axis=1)


def hash_frame(arr: np.ndarray, tag: str) -> str:
    h = sha1()
    h.update(tag.encode("utf-8"))
    h.update(np.asarray(arr, dtype=np.float32).round(7).tobytes())
    return h.hexdigest()[:8]


def donor_pool() -> pd.DataFrame:
    scored = pd.read_csv(LABEL_FLOW_SCORED)
    # Use two views: safest by pair rank and closest by p90 risk. Deduplicate after union.
    rank_top = scored.sort_values("pair_rank_score").head(36)
    p90_top = scored.sort_values("pair_delta_vs_a2c8_p90").head(36)
    raw05_top = scored.sort_values(["pair_delta_vs_raw05_p90", "bad_axis_abs_load"]).head(24)
    pool = pd.concat([rank_top, p90_top, raw05_top], ignore_index=True).drop_duplicates("source_path").reset_index(drop=True)
    return pool


def build_candidates() -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    base = read_submission(BASE_FILE)
    raw05 = read_submission(RAW05_FILE)
    assert base[KEY].equals(sample[KEY])
    assert raw05[KEY].equals(sample[KEY])

    base_arr = base[TARGETS].to_numpy(dtype=float)
    raw_arr = raw05[TARGETS].to_numpy(dtype=float)
    mu, inv = target_energy_model()
    base_energy = manifold_energy(base_arr, mu, inv)
    base_raw_dist = np.mean(np.abs(base_arr - raw_arr), axis=1)

    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    donors = donor_pool()
    alphas = [0.15, 0.25, 0.35, 0.50, 0.70]
    energy_thresholds = [0.0, -0.005, -0.015, -0.030]
    raw_margins = [0.0, 0.0005, 0.0015, 0.0030]
    max_steps = [0.006, 0.010, 0.018, 0.030]
    min_gate_frac = 0.02

    for donor_i, donor_rec in donors.iterrows():
        donor_path = ROOT / str(donor_rec["source_path"])
        if not donor_path.exists():
            continue
        donor = read_submission(donor_path)
        if not donor[KEY].equals(sample[KEY]):
            continue
        donor_arr = donor[TARGETS].to_numpy(dtype=float)
        donor_energy = manifold_energy(donor_arr, mu, inv)
        donor_raw_dist = np.mean(np.abs(donor_arr - raw_arr), axis=1)
        energy_delta = donor_energy - base_energy
        raw_delta = donor_raw_dist - base_raw_dist
        delta = donor_arr - base_arr

        for alpha in alphas:
            for e_thr in energy_thresholds:
                for r_margin in raw_margins:
                    gate = (energy_delta <= e_thr) & (raw_delta <= r_margin)
                    if gate.mean() < min_gate_frac:
                        continue
                    for max_step in max_steps:
                        step = np.clip(delta, -max_step, max_step)
                        arr = clip(base_arr + alpha * gate[:, None] * step)
                        tag = f"{donor_path.name}|a{alpha}|e{e_thr}|r{r_margin}|m{max_step}"
                        digest = hash_frame(arr, tag)
                        if digest in seen:
                            continue
                        seen.add(digest)
                        out = base.copy()
                        out[TARGETS] = arr
                        file_name = f"submission_label_flow_gated_{digest}.csv"
                        out_path = ANALYSIS / file_name
                        out.to_csv(out_path, index=False)

                        new_energy = manifold_energy(arr, mu, inv)
                        new_raw_dist = np.mean(np.abs(arr - raw_arr), axis=1)
                        rows.append(
                            {
                                "source_path": rel_path(out_path),
                                "donor_path": str(donor_rec["source_path"]),
                                "donor_rank": int(donor_i),
                                "alpha": alpha,
                                "energy_threshold": e_thr,
                                "raw_margin": r_margin,
                                "max_step": max_step,
                                "gate_frac": float(gate.mean()),
                                "mean_abs_move_vs_a2c8": float(np.mean(np.abs(arr - base_arr))),
                                "mean_abs_move_vs_raw05": float(np.mean(np.abs(arr - raw_arr))),
                                "raw_dist_delta_vs_base": float(np.mean(new_raw_dist - base_raw_dist)),
                                "energy_delta_vs_base": float(np.mean(new_energy - base_energy)),
                                "energy_improved_frac": float(np.mean(new_energy < base_energy)),
                                "donor_pair_p90_vs_a2c8": float(donor_rec.get("pair_delta_vs_a2c8_p90", np.nan)),
                                "donor_bad_axis_abs_load": float(donor_rec.get("bad_axis_abs_load", np.nan)),
                            }
                        )
    scan = pd.DataFrame(rows)
    if not scan.empty:
        scan = scan.sort_values(
            ["energy_delta_vs_base", "raw_dist_delta_vs_base", "mean_abs_move_vs_a2c8"],
            ascending=[True, True, True],
        ).reset_index(drop=True)
        scan.to_csv(SCAN_OUT, index=False)
    return scan


def pairwise_score(scan: pd.DataFrame) -> pd.DataFrame:
    if scan.empty:
        return pd.DataFrame()
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    known, refs, ref_vecs = build_known_and_refs(sample)
    known = known.sort_values("public_lb").reset_index(drop=True)
    model_df, _known_pairs = evaluate_pairwise_models(known)
    pool_rows = []
    for _, row in scan.iterrows():
        path = ROOT / str(row["source_path"])
        pool_rows.append(
            {
                "resolved_path": str(path.resolve()),
                "source_path": rel_path(path),
                "basename": path.name,
                "pool_source": "label_flow_gated",
                "pool_priority": float(row["energy_delta_vs_base"]),
                "candidate_family": family_name(path),
                **row.to_dict(),
            }
        )
    pool = pd.DataFrame(pool_rows)
    features = build_candidate_features(pool, sample, refs, ref_vecs)
    scored = score_candidates(known, features, model_df)
    scored.to_csv(SCORED_OUT, index=False)
    shortlist = scored[
        scored["pair_submit_gate"].astype(bool)
        | scored["pair_control_better_than_a2c8_gate"].astype(bool)
        | scored["pair_probe_gate"].astype(bool)
    ].copy()
    if shortlist.empty:
        shortlist = scored.head(80).copy()
    shortlist.to_csv(SHORTLIST_OUT, index=False)
    return scored


def table(df: pd.DataFrame, cols: list[str], n: int = 25) -> str:
    if df.empty:
        return "(empty)"
    keep = [c for c in cols if c in df.columns]
    return df[keep].head(n).round(9).to_csv(index=False).strip()


def main() -> None:
    scan = build_candidates()
    scored = pairwise_score(scan)

    submit = int(scored["pair_submit_gate"].sum()) if not scored.empty else 0
    probe = int(scored["pair_probe_gate"].sum()) if not scored.empty else 0
    control = int(scored["pair_control_better_than_a2c8_gate"].sum()) if not scored.empty else 0
    best_p90 = float(scored["pair_delta_vs_a2c8_p90"].min()) if not scored.empty else np.nan

    lines = [
        "# Label-Flow Gated Candidate Scan",
        "",
        "Question: can the real-but-unsafe label-flow/block-rate signal become public-safe if applied only where it lowers target-dependency energy and stays raw05-compatible?",
        "",
        "## Gate Definition",
        "",
        "- base: `submission_frontier_cvjepa_refine_a2c8d2c8.csv`.",
        "- donor pool: safest label-flow/transductive/MP-count candidates from `label_flow_blockrate_jepa_pairwise_scored.csv`.",
        "- row gate: donor target-dependency manifold energy <= base by threshold, and donor raw05 distance <= base raw05 distance plus margin.",
        "- movement: clipped donor-base delta with alpha scaling.",
        "",
        "## Results",
        "",
        f"- generated candidates: `{len(scan)}`",
        f"- pairwise-scored candidates: `{len(scored)}`",
        f"- pair_submit_gate: `{submit}`",
        f"- pair_control_better_than_a2c8_gate: `{control}`",
        f"- pair_probe_gate: `{probe}`",
        f"- best p90 delta vs a2c8: `{best_p90:.9f}`",
        "",
        "## Top Pairwise Candidates",
        "",
        "```csv",
        table(
            scored,
            [
                "source_path",
                "donor_path",
                "alpha",
                "energy_threshold",
                "raw_margin",
                "max_step",
                "gate_frac",
                "energy_delta_vs_base",
                "raw_dist_delta_vs_base",
                "mean_abs_move_vs_a2c8",
                "pair_delta_vs_a2c8_p90",
                "pair_delta_vs_a2c8_mean",
                "pair_beats_a2c8_rate",
                "pair_delta_vs_raw05_p90",
                "bad_axis_abs_load",
                "pair_submit_gate",
                "pair_probe_gate",
                "pair_selector_conflict",
                "pair_rank_score",
            ],
            40,
        ),
        "```",
        "",
        "## Decision",
        "",
    ]
    if submit or control:
        lines.extend(
            [
                "At least one gated candidate survived a strong pairwise gate. Promote the shortlist to full submission survival review.",
            ]
        )
    elif probe:
        lines.extend(
            [
                "No submit candidate, but a probe survived. Treat it as a public sensor candidate only after checking old selector and blockwise stress.",
            ]
        )
    else:
        lines.extend(
            [
                "The gate reduced semantic/manifold risk but still did not produce a public-safe candidate under pairwise stress. This weakens direct label-flow translation further and shifts next work toward either better selector resolution or a different representation move.",
            ]
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{SCAN_OUT.name}`",
            f"- `{SCORED_OUT.name}`",
            f"- `{SHORTLIST_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT_OUT)
    print(table(scored, ["source_path", "pair_delta_vs_a2c8_p90", "pair_beats_a2c8_rate", "bad_axis_abs_load", "pair_submit_gate", "pair_probe_gate", "pair_selector_conflict"], 20))


if __name__ == "__main__":
    main()
