from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

import hidden_public_localization_selector as hpls  # noqa: E402
import public_lb_direct_label_inverse7 as inv  # noqa: E402
import public_lb_direct_label_robust_selector as robust  # noqa: E402
import public_selector_universe_audit as universe  # noqa: E402


SCAN_OUT = OUT / "hidden_public_local_bridge_scan.csv"
SHORTLIST_OUT = OUT / "hidden_public_local_bridge_shortlist.csv"
SELECTED_OUT = OUT / "hidden_public_local_bridge_selected.csv"
REPORT_OUT = OUT / "hidden_public_local_bridge_report.md"

TARGETS = inv.TARGETS
KEY = inv.KEY


@dataclass(frozen=True)
class BridgeSpec:
    donor_file: Path
    donor_family: str
    donor_rank: int
    mode: str
    gate_name: str
    target_mask: str
    scale: float
    cap: float


def stable_hash(text: str) -> str:
    return sha1(text.encode("utf-8")).hexdigest()[:8]


def clip(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), inv.EPS, 1.0 - inv.EPS)


def load_sample() -> pd.DataFrame:
    return pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def write_submission(path: Path, sample: pd.DataFrame, pred: np.ndarray) -> None:
    out = sample[KEY].copy()
    out[TARGETS] = clip(pred)
    out.to_csv(path, index=False)


def target_mask(name: str) -> np.ndarray:
    targets = {
        "all": TARGETS,
        "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
        "q1_q3_s3": ["Q1", "Q3", "S3"],
        "q1_q3_s2_s3": ["Q1", "Q3", "S2", "S3"],
        "q1_s3": ["Q1", "S3"],
    }[name]
    mask = np.zeros(len(TARGETS), dtype=bool)
    for target in targets:
        mask[TARGETS.index(target)] = True
    return mask


def build_cell_gates(cells: pd.DataFrame) -> dict[str, np.ndarray]:
    gates: dict[str, np.ndarray] = {}
    n_rows = int(cells["row_index"].max()) + 1
    n_targets = len(TARGETS)
    all_mask = np.ones((n_rows, n_targets), dtype=bool)
    gates["all"] = all_mask

    ranked_cells = cells.sort_values("local_energy", ascending=False).reset_index(drop=True)
    for frac in [0.03, 0.08, 0.20]:
        keep = ranked_cells.head(max(12, int(np.ceil(len(ranked_cells) * frac))))
        mask = np.zeros_like(all_mask)
        mask[keep["row_index"].to_numpy(dtype=int), keep["target_index"].to_numpy(dtype=int)] = True
        gates[f"cell_top{int(frac * 100):02d}"] = mask

    row_energy = cells.groupby("row_index")["local_energy"].sum().sort_values(ascending=False)
    for top_n in [10, 25, 50]:
        rows = row_energy.head(top_n).index.to_numpy(dtype=int)
        mask = np.zeros_like(all_mask)
        mask[rows, :] = True
        gates[f"row_top{top_n}"] = mask
    return gates


def local_metrics(
    pred: np.ndarray,
    a2c8: np.ndarray,
    raw05: np.ndarray,
    stage2: np.ndarray,
    cells: pd.DataFrame,
    sols: list[robust.Solution],
    weights: np.ndarray,
    a2_scores: np.ndarray,
    raw_scores: np.ndarray,
) -> dict[str, float]:
    sol_scores = np.asarray([robust.score_under_solution(sol, pred, stage2) for sol in sols], dtype=np.float64)
    deltas = sol_scores - a2_scores
    raw_deltas = sol_scores - raw_scores
    return {
        "local_direct_delta_mean": float(np.sum(weights * deltas)),
        "local_direct_delta_p50": float(np.quantile(deltas, 0.50)),
        "local_direct_delta_p90": float(np.quantile(deltas, 0.90)),
        "local_direct_delta_worst": float(np.max(deltas)),
        "local_direct_win_rate": float(np.mean(deltas < 0.0)),
        "local_direct_delta_vs_raw05_mean": float(np.sum(weights * raw_deltas)),
        "energy_ce_delta_top03": hpls.localized_ce_delta(pred, a2c8, cells, 0.03),
        "energy_ce_delta_top08": hpls.localized_ce_delta(pred, a2c8, cells, 0.08),
        "energy_ce_delta_top20": hpls.localized_ce_delta(pred, a2c8, cells, 0.20),
        "mean_abs_move_vs_a2c8_prob": float(np.mean(np.abs(pred - a2c8))),
        "mean_abs_move_vs_raw05_prob": float(np.mean(np.abs(pred - raw05))),
        "max_abs_move_vs_a2c8_prob": float(np.max(np.abs(pred - a2c8))),
    }


def make_bridge(base: np.ndarray, donor: np.ndarray, cell_gate: np.ndarray, tmask: np.ndarray, spec: BridgeSpec) -> np.ndarray:
    pred = base.copy()
    mask = cell_gate & tmask.reshape(1, -1)
    if not mask.any():
        return pred
    if spec.mode == "logit":
        moved = inv.sigmoid(inv.logit(base[mask]) + spec.scale * (inv.logit(donor[mask]) - inv.logit(base[mask])))
    elif spec.mode == "prob":
        moved = base[mask] + spec.scale * (donor[mask] - base[mask])
    else:
        raise ValueError(spec.mode)
    delta = np.clip(moved - base[mask], -spec.cap, spec.cap)
    pred[mask] = clip(base[mask] + delta)
    return pred


def donor_paths() -> list[tuple[Path, str]]:
    ranking = pd.read_csv(hpls.RANKING_OUT)
    ok = ranking[ranking["load_error"].fillna("").eq("")].copy()
    pools = []
    for family, n in [("public6entropy", 3), ("directrob", 1)]:
        part = ok[ok["candidate_family"].astype(str).eq(family)].sort_values("localization_score").head(n)
        pools.append(part)
    selected = pd.concat(pools, ignore_index=True, sort=False).drop_duplicates("basename")
    out: list[tuple[Path, str]] = []
    for row in selected.itertuples(index=False):
        path = Path(str(row.file))
        if path.exists():
            out.append((path, str(row.candidate_family)))
    return out


def generate_and_prefilter() -> pd.DataFrame:
    sample = load_sample()
    preds = inv.load_predictions(sample)
    stage2 = preds["stage2"]
    a2c8 = preds["cvjepa_a2c8"]
    raw05 = preds["raw05"]

    sources, solution_map = robust.load_sources()
    sols, weights, selected_sources = hpls.choose_localization_solutions(sources, solution_map)
    cells, _rows, _targets = hpls.build_localization_tables(sample, selected_sources)
    a2_scores = np.asarray([robust.score_under_solution(sol, a2c8, stage2) for sol in sols], dtype=np.float64)
    raw_scores = np.asarray([robust.score_under_solution(sol, raw05, stage2) for sol in sols], dtype=np.float64)

    all_gates = build_cell_gates(cells)
    gates = {name: all_gates[name] for name in ["all", "cell_top03", "cell_top08", "row_top10", "row_top25"]}
    target_masks = {name: target_mask(name) for name in ["all", "no_q2", "q1_q3_s3", "q1_q3_s2_s3", "q1_s3"]}
    records: list[dict[str, object]] = []
    created = 0
    for donor_rank, (path, family) in enumerate(donor_paths(), start=1):
        donor = hpls.load_matrix(path, sample)
        for mode in ["logit", "prob"]:
            for gate_name, gate in gates.items():
                for mask_name, tmask in target_masks.items():
                    for scale in [0.025, 0.050, 0.090, 0.140]:
                        for cap in [0.004, 0.010]:
                            spec = BridgeSpec(
                                donor_file=path,
                                donor_family=family,
                                donor_rank=donor_rank,
                                mode=mode,
                                gate_name=gate_name,
                                target_mask=mask_name,
                                scale=scale,
                                cap=cap,
                            )
                            pred = make_bridge(a2c8, donor, gate, tmask, spec)
                            if float(np.mean(np.abs(pred - a2c8))) < 1e-5:
                                continue
                            metrics = local_metrics(pred, a2c8, raw05, stage2, cells, sols, weights, a2_scores, raw_scores)
                            metrics["localization_score"] = (
                                metrics["local_direct_delta_mean"]
                                + 0.50 * metrics["local_direct_delta_p90"]
                                + 0.20 * metrics["energy_ce_delta_top08"]
                                + 0.10 * metrics["energy_ce_delta_top20"]
                            )
                            token = stable_hash(
                                f"{path.name}|{mode}|{gate_name}|{mask_name}|{scale:.4f}|{cap:.4f}|{metrics['localization_score']:.12f}"
                            )
                            name = f"submission_hiddenloc_bridge_{token}.csv"
                            out_path = OUT / name
                            write_submission(out_path, sample, pred)
                            created += 1
                            rec = {
                                "file": name,
                                "source_path": str(out_path),
                                "basename": name,
                                "donor_file": path.name,
                                "donor_family": family,
                                "donor_rank": donor_rank,
                                "mode": mode,
                                "gate_name": gate_name,
                                "target_mask": mask_name,
                                "scale": scale,
                                "cap": cap,
                            }
                            rec.update(metrics)
                            records.append(rec)

    frame = pd.DataFrame(records)
    if frame.empty:
        raise RuntimeError("no bridge candidates generated")
    frame["local_prefilter_rank"] = frame["localization_score"].rank(method="min")
    print(f"generated_bridge_candidates={created}")
    return frame.sort_values("localization_score").reset_index(drop=True)


def score_stress(local_scan: pd.DataFrame) -> pd.DataFrame:
    sample = load_sample()
    known, refs, ref_vecs = universe.build_known_and_refs(sample)
    models = universe.evaluate_models(known)

    keep = pd.concat(
        [
            local_scan.sort_values("localization_score").head(420),
            local_scan[local_scan["mean_abs_move_vs_a2c8_prob"].between(0.00003, 0.00120)].sort_values("localization_score").head(220),
            local_scan[local_scan["gate_name"].astype(str).str.startswith("cell_")].sort_values("localization_score").head(180),
            local_scan[local_scan["gate_name"].astype(str).str.startswith("row_")].sort_values("localization_score").head(180),
        ],
        ignore_index=True,
        sort=False,
    ).drop_duplicates("basename")

    rows: list[dict[str, object]] = []
    for row in keep.itertuples(index=False):
        rec = universe.feature_row(str(row.source_path), sample, refs, ref_vecs)
        rec["file"] = str(row.basename)
        rec["source_path"] = str(row.source_path)
        rec["basename"] = str(row.basename)
        rec["candidate_family"] = "hiddenloc_bridge"
        rec["is_known_public"] = False
        rec["known_public_lb"] = np.nan
        rows.append(rec)

    anchor_rows = known.copy()
    anchor_rows["basename"] = anchor_rows["file"].astype(str)
    anchor_rows["source_path"] = anchor_rows["file"].astype(str)
    anchor_rows["candidate_family"] = "known_public"
    candidates = pd.concat([anchor_rows, pd.DataFrame(rows)], ignore_index=True, sort=False)
    proxy = universe.fit_all_predict(known, candidates, models)
    stress = universe.candidate_stress_scores(known, proxy)
    stress = stress.merge(candidates[["file", "source_path", "basename", "candidate_family"]].drop_duplicates("file"), on="file", how="left")
    scored = universe.add_frontier_flags(stress)
    scored = scored.merge(local_scan, on=["basename", "source_path"], how="left", suffixes=("", "_local"))
    scored["bridge_submit_gate"] = (
        (scored["candidate_family"].eq("hiddenloc_bridge"))
        & (scored["localization_score"] < -0.00008)
        & (scored["local_direct_delta_p90"] < 0.00002)
        & (scored["energy_ce_delta_top08"] < -0.00005)
        & (scored["selector_p90_delta_vs_a2c8_public"] <= 0.00060)
        & (scored["bad_axis_abs_load"] <= 0.040)
        & (scored["beats_a2c8_scenario_rate"] >= 0.45)
    )
    scored["bridge_probe_gate"] = (
        (scored["candidate_family"].eq("hiddenloc_bridge"))
        & (scored["localization_score"] < -0.00015)
        & (scored["selector_p90_delta_vs_a2c8_public"] <= 0.00068)
        & (scored["bad_axis_abs_load"] <= 0.060)
    )
    scored["bridge_rank_score"] = (
        scored["selector_p90_delta_vs_a2c8_public"].fillna(9.0)
        + 0.00010 * scored["bad_axis_abs_load"].fillna(0.0)
        + 0.20 * scored["localization_score"].fillna(0.0)
        - 0.00002 * scored["beats_a2c8_scenario_rate"].fillna(0.0)
    )
    return scored.sort_values(
        ["bridge_submit_gate", "bridge_probe_gate", "bridge_rank_score"],
        ascending=[False, False, True],
    ).reset_index(drop=True)


def write_report(local_scan: pd.DataFrame, scored: pd.DataFrame) -> None:
    bridge = scored[scored["candidate_family"].eq("hiddenloc_bridge")].copy()
    submit = bridge[bridge["bridge_submit_gate"] == True]  # noqa: E712
    probe = bridge[bridge["bridge_probe_gate"] == True]  # noqa: E712
    cols = [
        "basename",
        "donor_file",
        "donor_family",
        "mode",
        "gate_name",
        "target_mask",
        "scale",
        "cap",
        "localization_score",
        "local_direct_delta_mean",
        "local_direct_delta_p90",
        "energy_ce_delta_top08",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "bridge_submit_gate",
        "bridge_probe_gate",
        "bridge_rank_score",
    ]
    cols = [c for c in cols if c in bridge.columns]

    def table(df: pd.DataFrame) -> str:
        if df.empty:
            return "None."
        return "```text\n" + df.to_string(index=False, float_format=lambda x: f"{x:.6f}") + "\n```"

    lines = [
        "# Hidden Public Local Bridge",
        "",
        "## Purpose",
        "Take high-localization but high-bad-axis public6/directrob directions and blend only a capped, gated fraction into a2c8. This tests whether the bottleneck is simply over-large movement along the right hidden-public direction.",
        "",
        "## Counts",
        f"- generated candidates: {len(local_scan)}",
        f"- stress-scored candidates including anchors: {len(scored)}",
        f"- bridge_submit_gate pass: {len(submit)}",
        f"- bridge_probe_gate pass: {len(probe)}",
        "",
        "## Best Stress-Local Bridges",
        table(bridge.head(40)[cols]),
        "",
        "## Submit Gate",
        table(submit.head(20)[cols]),
        "",
        "## Probe Gate",
        table(probe.head(30)[cols]),
        "",
        "## Read",
        "- A pass would mean tiny gated movement can transfer local inverse signal without importing the bad public axis.",
        "- If no pass appears, high-localization directions are not merely too large; their sign/geometry conflicts with the stable public selector.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    local_scan = generate_and_prefilter()
    scored = score_stress(local_scan)
    local_scan.to_csv(SCAN_OUT, index=False)
    scored.to_csv(SHORTLIST_OUT, index=False)
    selected = scored[
        scored["candidate_family"].eq("hiddenloc_bridge")
        & (scored["bridge_submit_gate"].fillna(False) | scored["bridge_probe_gate"].fillna(False))
    ].copy()
    if selected.empty:
        selected = scored[scored["candidate_family"].eq("hiddenloc_bridge")].sort_values("bridge_rank_score").head(40)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(local_scan, scored)
    print(f"local_scan={len(local_scan)}")
    print(f"stress_scored={len(scored)}")
    print(f"bridge_submit_gate={int(scored['bridge_submit_gate'].fillna(False).sum())}")
    print(f"bridge_probe_gate={int(scored['bridge_probe_gate'].fillna(False).sum())}")
    print(f"wrote={REPORT_OUT}")


if __name__ == "__main__":
    main()
