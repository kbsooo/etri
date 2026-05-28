from __future__ import annotations

from hashlib import sha1
from itertools import combinations, product
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
E11_SCORED = ANALYSIS / "label_flow_gated_candidate_pairwise_scored.csv"
E12_SCORED = ANALYSIS / "label_flow_targetwise_amplified_gate_pairwise_scored.csv"

SCAN_OUT = ANALYSIS / "label_flow_combo_gate_scan.csv"
SCORED_OUT = ANALYSIS / "label_flow_combo_gate_pairwise_scored.csv"
SHORTLIST_OUT = ANALYSIS / "label_flow_combo_gate_shortlist.csv"
REPORT_OUT = ANALYSIS / "label_flow_combo_gate_report.md"


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
    x = np.asarray(p, dtype=float) - mu[None, :]
    return np.sum((x @ inv) * x, axis=1)


def hash_frame(arr: np.ndarray, tag: str) -> str:
    h = sha1()
    h.update(tag.encode("utf-8"))
    h.update(np.asarray(arr, dtype=np.float32).round(7).tobytes())
    return h.hexdigest()[:8]


def choose_atoms() -> pd.DataFrame:
    atoms: list[pd.DataFrame] = []
    if E12_SCORED.exists():
        print("loading E12 atoms", flush=True)
        e12 = pd.read_csv(E12_SCORED)
        for mask in ["S4", "Q3", "Q2_Q3"]:
            part = e12[e12["target_mask"].astype(str).eq(mask)].copy()
            if not part.empty:
                atoms.append(part.sort_values(["pair_delta_vs_a2c8_p90", "pair_rank_score"]).head(1))
        controls = e12[e12["pair_control_better_than_a2c8_gate"].astype(bool)].copy()
        if not controls.empty:
            atoms.append(controls.sort_values(["pair_rank_score", "pair_delta_vs_a2c8_p90"]).head(1))
    if E11_SCORED.exists():
        print("loading E11 atoms", flush=True)
        e11 = pd.read_csv(E11_SCORED)
        controls = e11[e11["pair_control_better_than_a2c8_gate"].astype(bool)].copy()
        if not controls.empty:
            atoms.append(controls.sort_values(["pair_delta_vs_a2c8_p90", "pair_rank_score"]).head(1))
            atoms.append(controls.sort_values(["pair_rank_score", "pair_delta_vs_a2c8_p90"]).head(1))
    if not atoms:
        raise RuntimeError("no atom candidates available")
    atom_df = pd.concat(atoms, ignore_index=True).drop_duplicates("file").reset_index(drop=True)
    atom_df["atom_id"] = [f"a{i:02d}" for i in range(len(atom_df))]
    return atom_df.head(6)


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

    atom_df = choose_atoms()
    print(f"atom count {len(atom_df)}", flush=True)
    atom_arrays: dict[str, np.ndarray] = {}
    for _, row in atom_df.iterrows():
        path = ROOT / str(row["file"])
        print(f"read atom {row['atom_id']} {path.name}", flush=True)
        sub = read_submission(path)
        if not sub[KEY].equals(sample[KEY]):
            continue
        atom_arrays[str(row["atom_id"])] = sub[TARGETS].to_numpy(dtype=float) - base_arr

    weights = [0.50, 0.75, 1.00, 1.35, 1.75, 2.25, 3.00, 4.00]
    records: list[dict[str, object]] = []
    seen: set[str] = set()
    atom_ids = list(atom_arrays)

    for k in [1, 2, 3]:
        print(f"combo size {k}", flush=True)
        for combo_ids in combinations(atom_ids, k):
            for combo_weights in product(weights, repeat=k):
                delta = np.zeros_like(base_arr)
                for atom_id, w in zip(combo_ids, combo_weights):
                    delta += w * atom_arrays[atom_id]
                if float(np.mean(np.abs(delta))) <= 0.0:
                    continue
                arr = clip(base_arr + delta)
                new_energy = manifold_energy(arr, mu, inv)
                new_raw_dist = np.mean(np.abs(arr - raw_arr), axis=1)
                energy_delta = float(np.mean(new_energy - base_energy))
                raw_delta = float(np.mean(new_raw_dist - base_raw_dist))
                mean_move = float(np.mean(np.abs(arr - base_arr)))
                if energy_delta > 0.0030 or raw_delta > 0.0025 or mean_move > 0.020:
                    continue
                tag = "|".join(combo_ids) + "|" + ",".join(str(x) for x in combo_weights)
                digest = hash_frame(arr, tag)
                if digest in seen:
                    continue
                seen.add(digest)
                out = base.copy()
                out[TARGETS] = arr
                out_path = ANALYSIS / f"submission_label_flow_combo_{digest}.csv"
                out.to_csv(out_path, index=False)
                records.append(
                    {
                        "source_path": rel_path(out_path),
                        "atom_ids": "|".join(combo_ids),
                        "atom_files": "|".join(atom_df.set_index("atom_id").loc[list(combo_ids), "file"].astype(str).tolist()),
                        "weights": "|".join(str(w) for w in combo_weights),
                        "combo_size": k,
                        "mean_abs_move_vs_a2c8": mean_move,
                        "mean_abs_move_vs_raw05": float(np.mean(np.abs(arr - raw_arr))),
                        "raw_dist_delta_vs_base": raw_delta,
                        "energy_delta_vs_base": energy_delta,
                        "energy_improved_frac": float(np.mean(new_energy < base_energy)),
                    }
                )
    scan = pd.DataFrame(records)
    if not scan.empty:
        scan = scan.sort_values(["energy_delta_vs_base", "raw_dist_delta_vs_base", "mean_abs_move_vs_a2c8"], ascending=[True, True, False])
        scan.to_csv(SCAN_OUT, index=False)
    atom_df.to_csv(ANALYSIS / "label_flow_combo_gate_atoms.csv", index=False)
    return scan


def pairwise_score(scan: pd.DataFrame) -> pd.DataFrame:
    if scan.empty:
        return pd.DataFrame()
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    known, refs, ref_vecs = build_known_and_refs(sample)
    known = known.sort_values("public_lb").reset_index(drop=True)
    model_df, _known_pairs = evaluate_pairwise_models(known)
    pool = pd.DataFrame(
        [
            {
                "resolved_path": str((ROOT / str(row["source_path"])).resolve()),
                "source_path": row["source_path"],
                "basename": Path(str(row["source_path"])).name,
                "pool_source": "label_flow_combo_gate",
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

    cols = [
        "source_path",
        "combo_size",
        "atom_ids",
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
    lines = [
        "# Label-Flow Combo Gate Scan",
        "",
        "Question: do targetwise gated atoms add constructively, or does stress break as soon as S4 and Q-side moves are combined?",
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
        "",
        "## Top By P90 Edge",
        "",
        "```csv",
        table(scored.sort_values(["pair_delta_vs_a2c8_p90", "pair_rank_score"]), cols),
        "```",
        "",
        "## Top By Rank",
        "",
        "```csv",
        table(scored.sort_values(["pair_rank_score", "pair_delta_vs_a2c8_p90"]), cols),
        "```",
        "",
        "## Decision",
        "",
    ]
    if submit:
        lines.append("At least one combined atom candidate passes strict submit gate. Validate it before promotion.")
    elif control:
        lines.append("Combination improves sensor strength but remains below strict submit. Use only if public-sensor value justifies a slot.")
    else:
        lines.append("Combination does not improve over atom-level gates; keep E12 top atom as the boundary.")
    lines.extend(["", "## Files", "", f"- `{SCAN_OUT.name}`", f"- `{SCORED_OUT.name}`", f"- `{SHORTLIST_OUT.name}`"])
    REPORT_OUT.write_text("\n".join(lines) + "\n")
    print(REPORT_OUT)


if __name__ == "__main__":
    main()
