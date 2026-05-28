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
E11_SCORED = ANALYSIS / "label_flow_gated_candidate_pairwise_scored.csv"

SCAN_OUT = ANALYSIS / "label_flow_targetwise_amplified_gate_scan.csv"
SCORED_OUT = ANALYSIS / "label_flow_targetwise_amplified_gate_pairwise_scored.csv"
SHORTLIST_OUT = ANALYSIS / "label_flow_targetwise_amplified_gate_shortlist.csv"
REPORT_OUT = ANALYSIS / "label_flow_targetwise_amplified_gate_report.md"


TARGET_MASKS: dict[str, list[str]] = {
    "all": TARGETS,
    "Q": ["Q1", "Q2", "Q3"],
    "S": ["S1", "S2", "S3", "S4"],
    "Q1": ["Q1"],
    "Q2": ["Q2"],
    "Q3": ["Q3"],
    "S1": ["S1"],
    "S2": ["S2"],
    "S3": ["S3"],
    "S4": ["S4"],
    "Q1_Q3": ["Q1", "Q3"],
    "Q2_Q3": ["Q2", "Q3"],
    "Q3_S2_S3": ["Q3", "S2", "S3"],
    "S2_S3": ["S2", "S3"],
    "S2_S3_S4": ["S2", "S3", "S4"],
}


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def read_submission(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def target_energy_model() -> tuple[np.ndarray, np.ndarray]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    y = train[TARGETS].to_numpy(dtype=float)
    mu = y.mean(axis=0)
    cov = np.asarray(np.cov(y, rowvar=False), dtype=float)
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
    blocks = [
        scored.sort_values("pair_rank_score").head(18),
        scored.sort_values("pair_delta_vs_a2c8_p90").head(18),
        scored.sort_values(["pair_delta_vs_raw05_p90", "bad_axis_abs_load"]).head(14),
    ]
    if E11_SCORED.exists():
        e11 = pd.read_csv(E11_SCORED)
        control = e11[e11["pair_control_better_than_a2c8_gate"].astype(bool)]
        # Use the underlying original donor paths from the best E11 controls.
        if not control.empty:
            donor_paths = (
                control.sort_values(["pair_rank_score", "pair_delta_vs_a2c8_p90"])["donor_path"]
                .drop_duplicates()
                .head(10)
                .tolist()
            )
            blocks.append(scored[scored["source_path"].isin(donor_paths)])
    pool = pd.concat(blocks, ignore_index=True).drop_duplicates("source_path").reset_index(drop=True)
    return pool.head(12)


def mask_vector(mask_name: str) -> np.ndarray:
    chosen = set(TARGET_MASKS[mask_name])
    return np.array([1.0 if t in chosen else 0.0 for t in TARGETS], dtype=float)[None, :]


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

    # This scan deliberately crosses the E11 scale boundary to locate the first
    # stress break. It is not a blind blend grid: movement is still gated by
    # target-dependency energy and raw05 compatibility.
    alphas = [0.70, 1.00, 1.50, 2.25]
    energy_thresholds = [0.0, -0.010, -0.030]
    raw_margins = [0.0015, 0.0050, 0.0100]
    max_steps = [0.030, 0.050, 0.080]
    min_gate_frac = 0.012

    for donor_i, donor_rec in donors.iterrows():
        print(f"donor {donor_i + 1}/{len(donors)}", flush=True)
        donor_path = ROOT / str(donor_rec["source_path"])
        if not donor_path.exists():
            continue
        donor = read_submission(donor_path)
        if not donor[KEY].equals(sample[KEY]):
            continue
        donor_arr = donor[TARGETS].to_numpy(dtype=float)
        raw_delta_full = np.mean(np.abs(donor_arr - raw_arr), axis=1) - base_raw_dist
        delta = donor_arr - base_arr

        for mask_name in TARGET_MASKS:
            mask = mask_vector(mask_name)
            for max_step in max_steps:
                step = np.clip(delta, -max_step, max_step) * mask
                if float(np.mean(np.abs(step))) <= 0.0:
                    continue
                for alpha in alphas:
                    proposed = clip(base_arr + alpha * step)
                    energy_delta = manifold_energy(proposed, mu, inv) - base_energy
                    proposed_raw_dist = np.mean(np.abs(proposed - raw_arr), axis=1)
                    raw_delta = proposed_raw_dist - base_raw_dist
                    for e_thr in energy_thresholds:
                        for r_margin in raw_margins:
                            gate = (energy_delta <= e_thr) & (raw_delta <= r_margin) & (raw_delta_full <= r_margin + 0.004)
                            if gate.mean() < min_gate_frac:
                                continue
                            arr = clip(base_arr + alpha * gate[:, None] * step)
                            tag = f"{donor_path.name}|{mask_name}|a{alpha}|e{e_thr}|r{r_margin}|m{max_step}"
                            digest = hash_frame(arr, tag)
                            if digest in seen:
                                continue
                            seen.add(digest)

                            out = base.copy()
                            out[TARGETS] = arr
                            file_name = f"submission_label_flow_twampl_{digest}.csv"
                            out_path = ANALYSIS / file_name
                            out.to_csv(out_path, index=False)

                            new_energy = manifold_energy(arr, mu, inv)
                            new_raw_dist = np.mean(np.abs(arr - raw_arr), axis=1)
                            rows.append(
                                {
                                    "source_path": rel_path(out_path),
                                    "donor_path": str(donor_rec["source_path"]),
                                    "donor_rank": int(donor_i),
                                    "target_mask": mask_name,
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
            ascending=[True, True, False],
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
                "pool_source": "label_flow_targetwise_amplified",
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
        shortlist = scored.head(100).copy()
    shortlist.to_csv(SHORTLIST_OUT, index=False)
    return scored


def table(df: pd.DataFrame, cols: list[str], n: int = 30) -> str:
    if df.empty:
        return "(empty)"
    keep = [c for c in cols if c in df.columns]
    return df[keep].head(n).round(9).to_csv(index=False).strip()


def main() -> None:
    scan = build_candidates()
    scored = pairwise_score(scan)

    submit = int(scored["pair_submit_gate"].sum()) if not scored.empty else 0
    control = int(scored["pair_control_better_than_a2c8_gate"].sum()) if not scored.empty else 0
    probe = int(scored["pair_probe_gate"].sum()) if not scored.empty else 0
    conflict = int(scored["pair_selector_conflict"].sum()) if not scored.empty else 0
    best_p90 = float(scored["pair_delta_vs_a2c8_p90"].min()) if not scored.empty else np.nan
    best_mean = float(scored["pair_delta_vs_a2c8_mean"].min()) if not scored.empty else np.nan
    best_move = float(scored["mean_abs_move_vs_a2c8"].max()) if not scored.empty else np.nan

    cols = [
        "source_path",
        "donor_path",
        "target_mask",
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
        "pair_beats_raw05_rate",
        "bad_axis_abs_load",
        "pair_control_better_than_a2c8_gate",
        "pair_submit_gate",
        "pair_probe_gate",
        "pair_selector_conflict",
        "pair_rank_score",
    ]

    lines = [
        "# Label-Flow Targetwise Amplified Gate Scan",
        "",
        "Question: E11 fixed direction but not magnitude. Can targetwise masks and larger gated movement create a selector-resolvable edge without breaking raw05/bad-axis stress?",
        "",
        "## Design",
        "",
        "- Base: `submission_frontier_cvjepa_refine_a2c8d2c8.csv`.",
        "- Donors: top direct label-flow/MP-count donors plus donor paths from E11 controls.",
        "- Target masks: all, Q, S, each target, and dependency-oriented Q/S subsets.",
        "- Gate: proposed targetwise move must lower Q/S dependency energy and stay close to raw05 at row level.",
        "- Stress: same pairwise public-order selector as E11.",
        "",
        "## Results",
        "",
        f"- generated candidates: `{len(scan)}`",
        f"- pairwise-scored candidates: `{len(scored)}`",
        f"- pair_submit_gate: `{submit}`",
        f"- pair_control_better_than_a2c8_gate: `{control}`",
        f"- pair_probe_gate: `{probe}`",
        f"- pair_selector_conflict: `{conflict}`",
        f"- best p90 delta vs a2c8: `{best_p90:.9f}`",
        f"- best mean delta vs a2c8: `{best_mean:.9f}`",
        f"- largest mean_abs_move_vs_a2c8: `{best_move:.9f}`",
        "",
        "## Top By Rank",
        "",
        "```csv",
        table(scored.sort_values(["pair_rank_score", "pair_delta_vs_a2c8_p90"]), cols),
        "```",
        "",
        "## Top By P90 Edge",
        "",
        "```csv",
        table(scored.sort_values(["pair_delta_vs_a2c8_p90", "pair_rank_score"]), cols),
        "```",
        "",
        "## Submit/Control Candidates",
        "",
        "```csv",
        table(
            scored[
                scored["pair_submit_gate"].astype(bool)
                | scored["pair_control_better_than_a2c8_gate"].astype(bool)
            ].sort_values(["pair_submit_gate", "pair_rank_score"], ascending=[False, True]),
            cols,
            n=40,
        ),
        "```",
        "",
        "## Decision",
        "",
    ]
    if submit:
        lines.append("At least one targetwise amplified candidate passes the strict pairwise submit gate. It needs CSV validation and document promotion before submission.")
    elif control:
        lines.append("Targetwise amplification still does not clear the strict submit gate, but it creates control candidates. Treat them as stronger sensors only if their edge is materially larger than E11.")
    else:
        lines.append("Targetwise amplification fails to create even control candidates. The E11 gate is likely at the safe movement boundary.")

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
    REPORT_OUT.write_text("\n".join(lines) + "\n")
    print(REPORT_OUT)


if __name__ == "__main__":
    main()
