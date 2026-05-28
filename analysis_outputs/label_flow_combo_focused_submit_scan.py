from __future__ import annotations

from hashlib import sha1
from itertools import product
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

from public_pairwise_order_selector import build_candidate_features, evaluate_pairwise_models, rel_path, score_candidates  # noqa: E402
from public_selector_universe_audit import build_known_and_refs, family_name  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
BASE_FILE = ANALYSIS / "submission_frontier_cvjepa_refine_a2c8d2c8.csv"
RAW05_FILE = JEPA / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
ATOM_FILE = ANALYSIS / "label_flow_combo_gate_atoms.csv"

SCAN_OUT = ANALYSIS / "label_flow_combo_focused_submit_scan.csv"
SCORED_OUT = ANALYSIS / "label_flow_combo_focused_submit_pairwise_scored.csv"
REPORT_OUT = ANALYSIS / "label_flow_combo_focused_submit_report.md"


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
    return mu, np.linalg.pinv(shrink)


def manifold_energy(p: np.ndarray, mu: np.ndarray, inv: np.ndarray) -> np.ndarray:
    x = p - mu[None, :]
    return np.sum((x @ inv) * x, axis=1)


def hash_frame(arr: np.ndarray, tag: str) -> str:
    h = sha1()
    h.update(tag.encode("utf-8"))
    h.update(np.asarray(arr, dtype=np.float32).round(7).tobytes())
    return h.hexdigest()[:8]


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
    atoms = pd.read_csv(ATOM_FILE).set_index("atom_id")
    use_atoms = ["a00", "a01", "a03"]
    deltas = {}
    for atom_id in use_atoms:
        sub = read_submission(ROOT / str(atoms.loc[atom_id, "file"]))
        deltas[atom_id] = sub[TARGETS].to_numpy(dtype=float) - base_arr

    rows = []
    for w0, w1, w3 in product([4.0, 5.0, 6.0, 7.5, 9.0], [0.75, 1.0, 1.35, 1.75, 2.25, 3.0], [1.0, 1.75, 2.25, 3.0, 4.0, 5.5]):
        delta = w0 * deltas["a00"] + w1 * deltas["a01"] + w3 * deltas["a03"]
        arr = clip(base_arr + delta)
        new_energy = manifold_energy(arr, mu, inv)
        new_raw_dist = np.mean(np.abs(arr - raw_arr), axis=1)
        energy_delta = float(np.mean(new_energy - base_energy))
        raw_delta = float(np.mean(new_raw_dist - base_raw_dist))
        mean_move = float(np.mean(np.abs(arr - base_arr)))
        if energy_delta > 0.006 or raw_delta > 0.006 or mean_move > 0.035:
            continue
        tag = f"a00={w0}|a01={w1}|a03={w3}"
        digest = hash_frame(arr, tag)
        out = base.copy()
        out[TARGETS] = arr
        out_path = ANALYSIS / f"submission_label_flow_focused_{digest}.csv"
        out.to_csv(out_path, index=False)
        rows.append(
            {
                "source_path": rel_path(out_path),
                "weights": f"{w0}|{w1}|{w3}",
                "atom_ids": "a00|a01|a03",
                "mean_abs_move_vs_a2c8": mean_move,
                "mean_abs_move_vs_raw05": float(np.mean(np.abs(arr - raw_arr))),
                "raw_dist_delta_vs_base": raw_delta,
                "energy_delta_vs_base": energy_delta,
                "energy_improved_frac": float(np.mean(new_energy < base_energy)),
            }
        )
    scan = pd.DataFrame(rows)
    scan.to_csv(SCAN_OUT, index=False)
    return scan


def score(scan: pd.DataFrame) -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    known, refs, ref_vecs = build_known_and_refs(sample)
    known = known.sort_values("public_lb").reset_index(drop=True)
    model_df, _ = evaluate_pairwise_models(known)
    pool = pd.DataFrame(
        [
            {
                "resolved_path": str((ROOT / str(row["source_path"])).resolve()),
                "source_path": row["source_path"],
                "basename": Path(str(row["source_path"])).name,
                "pool_source": "label_flow_focused_submit",
                "pool_priority": float(row["energy_delta_vs_base"]),
                "candidate_family": family_name(ROOT / str(row["source_path"])),
                **row.to_dict(),
            }
            for _, row in scan.iterrows()
        ]
    )
    features = build_candidate_features(pool, sample, refs, ref_vecs)
    scored = score_candidates(known, features, model_df)
    scored.to_csv(SCORED_OUT, index=False)
    return scored


def main() -> None:
    scan = build_candidates()
    scored = score(scan)
    cols = [
        "source_path",
        "weights",
        "mean_abs_move_vs_a2c8",
        "energy_delta_vs_base",
        "raw_dist_delta_vs_base",
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
    top = scored.sort_values(["pair_delta_vs_a2c8_p90", "pair_rank_score"])[cols].head(30).round(9)
    lines = [
        "# Label-Flow Focused Submit Scan",
        "",
        "Question: can the best S4+Q3 atom combination be pushed over the strict pairwise submit threshold?",
        "",
        f"- generated candidates: `{len(scan)}`",
        f"- pairwise-scored candidates: `{len(scored)}`",
        f"- pair_submit_gate: `{int(scored['pair_submit_gate'].sum())}`",
        f"- pair_control_better_than_a2c8_gate: `{int(scored['pair_control_better_than_a2c8_gate'].sum())}`",
        f"- pair_probe_gate: `{int(scored['pair_probe_gate'].sum())}`",
        f"- pair_selector_conflict: `{int(scored['pair_selector_conflict'].sum())}`",
        f"- best p90 delta vs a2c8: `{float(scored['pair_delta_vs_a2c8_p90'].min()):.9f}`",
        f"- best mean delta vs a2c8: `{float(scored['pair_delta_vs_a2c8_mean'].min()):.9f}`",
        "",
        "```csv",
        top.to_csv(index=False).strip(),
        "```",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")
    print(REPORT_OUT)


if __name__ == "__main__":
    main()
