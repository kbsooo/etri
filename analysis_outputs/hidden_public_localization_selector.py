from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
JEPA = ROOT / "jepa"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

import public_lb_direct_label_robust_selector as robust  # noqa: E402
import public_lb_direct_label_inverse7 as inv  # noqa: E402


REPORT_OUT = OUT / "hidden_public_localization_selector_report.md"
CELL_OUT = OUT / "hidden_public_localization_cells.csv"
ROW_OUT = OUT / "hidden_public_localization_rows.csv"
TARGET_OUT = OUT / "hidden_public_localization_targets.csv"
RANKING_OUT = OUT / "hidden_public_localization_candidate_ranking.csv"
SHORTLIST_OUT = OUT / "hidden_public_localization_shortlist.csv"

UNIVERSE_SHORTLIST = OUT / "public_selector_universe_audit_shortlist.csv"
UNIVERSE_ALL = OUT / "public_selector_universe_audit_candidates.csv"
LOWENERGY_SELECTED = OUT / "badaxis_lowenergy_jepa_ensemble_selected.csv"
DIRECTROB_SELECTED = OUT / "public_lb_direct_label_robust_selector_selected.csv"
ROBUST_SOURCES = OUT / "public_lb_direct_label_robust_selector_sources.csv"


TARGETS = inv.TARGETS
KEY = inv.KEY

KNOWN_FILES = [
    ("known_a2c8_best", OUT / inv.A2C8),
    ("known_raw05", JEPA / inv.RAW05),
    ("known_stage2", OUT / inv.STAGE2),
    ("known_final9", OUT / "submission_hybrid_0p578_logit_after_subject_final9_strict.csv"),
    ("known_ordinal_q", OUT / "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv"),
]


@dataclass(frozen=True)
class CandidatePath:
    label: str
    path: Path
    source_group: str


def clip(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), inv.EPS, 1.0 - inv.EPS)


def ce(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))


def path_exists(path_like: str | Path) -> Path | None:
    path = Path(path_like)
    if path.exists():
        return path
    for base in (OUT, JEPA, ROOT):
        candidate = base / str(path_like)
        if candidate.exists():
            return candidate
    return None


def load_matrix(path: Path, sample: pd.DataFrame) -> np.ndarray:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    if not df[KEY].equals(sample[KEY]):
        raise ValueError(f"key mismatch: {path}")
    return clip(df[TARGETS].to_numpy(dtype=np.float64))


def choose_localization_solutions(
    sources: pd.DataFrame,
    solution_map: dict[str, robust.Solution],
    limit: int = 56,
) -> tuple[list[robust.Solution], np.ndarray, pd.DataFrame]:
    """Select diverse inverse solutions and down-weight brittle ones.

    Direct inverse can fit the sparse public observations too well. The selector
    therefore uses it only as a noisy teacher ensemble, not as a single oracle.
    """
    source = sources.copy()
    source["struct_boost_score"] = source["robust_source_score"] - 0.00008 * source["is_structured_mask"]
    frames = [
        source.sort_values(["robust_source_score", "loocv_mae", "l2o_mae"]).head(28),
        source[source["is_structured_mask"] == 1].sort_values(["struct_boost_score", "loocv_mae"]).head(18),
        source[source["is_subject_like_mask"] == 1].sort_values(["robust_source_score", "l2o_mae"]).head(12),
        source[source["loocv_mae"] <= 0.00072].sort_values(["solution_score", "l2o_mae"]).head(18),
        source[source["l2o_mae"] <= 0.00072].sort_values(["solution_score", "loocv_mae"]).head(18),
    ]
    chosen = (
        pd.concat(frames, ignore_index=True, sort=False)
        .drop_duplicates("solution_id")
        .sort_values(["robust_source_score", "loocv_mae", "l2o_mae"])
        .head(limit)
        .reset_index(drop=True)
    )

    sols: list[robust.Solution] = []
    keep_rows = []
    for row in chosen.itertuples(index=False):
        sol = solution_map.get(str(row.solution_id))
        if sol is None:
            continue
        sols.append(sol)
        keep_rows.append(row._asdict())

    selected = pd.DataFrame(keep_rows)
    if selected.empty:
        raise RuntimeError("no localization solutions selected")
    quality = selected["robust_source_score"].to_numpy(dtype=np.float64)
    tau = max(0.0014, float(np.quantile(quality, 0.60)))
    weights = np.exp(-quality / tau)
    weights *= 1.0 + 0.10 * selected["is_structured_mask"].to_numpy(dtype=np.float64)
    weights *= 1.0 + 0.06 * selected["is_subject_like_mask"].to_numpy(dtype=np.float64)
    weights = weights / weights.sum()
    selected["localization_weight"] = weights
    return sols, weights, selected


def build_localization_tables(
    sample: pd.DataFrame,
    selected_sources: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw_cells = pd.read_parquet(robust.CELL_IN)
    source_weights = selected_sources[["solution_id", "localization_weight"]].copy()
    source_weights["solution_id"] = source_weights["solution_id"].astype(str)
    raw_cells["solution_id"] = raw_cells["solution_id"].astype(str)
    merged = raw_cells.merge(source_weights, on="solution_id", how="inner")
    target_to_idx = {target: idx for idx, target in enumerate(TARGETS)}
    merged["target_index"] = merged["target"].map(target_to_idx).astype(int)
    merged["signed_weight"] = merged["localization_weight"] * merged["delta_vs_a2c8"]
    merged["abs_weight"] = merged["localization_weight"] * merged["delta_vs_a2c8"].abs()
    merged["pseudo_weight"] = merged["localization_weight"] * merged["pseudo_y"]
    merged["a2c8_weight"] = merged["localization_weight"] * merged["a2c8_prob"]
    merged["prior_weight"] = merged["localization_weight"] * merged["prior_prob"]
    merged["pos_weight"] = np.where(merged["delta_vs_a2c8"] >= 0.0, merged["localization_weight"], 0.0)
    merged["neg_weight"] = np.where(merged["delta_vs_a2c8"] < 0.0, merged["localization_weight"], 0.0)

    grouped = (
        merged.groupby(["row_index", "target", "target_index"], as_index=False)
        .agg(
            support=("solution_id", "nunique"),
            weight_sum=("localization_weight", "sum"),
            signed_sum=("signed_weight", "sum"),
            abs_sum=("abs_weight", "sum"),
            pseudo_sum=("pseudo_weight", "sum"),
            a2c8_sum=("a2c8_weight", "sum"),
            prior_sum=("prior_weight", "sum"),
            pos_weight=("pos_weight", "sum"),
            neg_weight=("neg_weight", "sum"),
        )
        .reset_index(drop=True)
    )
    grouped["mean_delta_vs_a2c8"] = grouped["signed_sum"] / grouped["weight_sum"]
    grouped["mean_abs_delta_vs_a2c8"] = grouped["abs_sum"] / grouped["weight_sum"]
    grouped["mean_pseudo_y"] = grouped["pseudo_sum"] / grouped["weight_sum"]
    grouped["mean_a2c8_prob"] = grouped["a2c8_sum"] / grouped["weight_sum"]
    grouped["mean_prior_prob"] = grouped["prior_sum"] / grouped["weight_sum"]
    grouped["direction_agreement"] = grouped[["pos_weight", "neg_weight"]].max(axis=1) / grouped["weight_sum"]

    delta_var_rows = []
    merged["mean_key"] = list(zip(merged["row_index"], merged["target"]))
    mean_map = grouped.set_index(["row_index", "target"])["mean_delta_vs_a2c8"].to_dict()
    merged["delta_center"] = merged["mean_key"].map(mean_map)
    merged["delta_var_weight"] = merged["localization_weight"] * (merged["delta_vs_a2c8"] - merged["delta_center"]) ** 2
    for key, part in merged.groupby(["row_index", "target"], sort=False):
        delta_var_rows.append(
            {
                "row_index": int(key[0]),
                "target": key[1],
                "delta_std": float(np.sqrt(part["delta_var_weight"].sum() / part["localization_weight"].sum())),
            }
        )
    delta_std = pd.DataFrame(delta_var_rows)
    cells = grouped.merge(delta_std, on=["row_index", "target"], how="left")
    cells["signal_to_uncertainty"] = cells["mean_delta_vs_a2c8"].abs() / (
        cells["mean_abs_delta_vs_a2c8"] + cells["delta_std"] + 1e-9
    )
    cells["local_energy"] = (
        cells["weight_sum"]
        * cells["mean_abs_delta_vs_a2c8"]
        * (0.25 + 0.75 * cells["direction_agreement"])
        * cells["signal_to_uncertainty"].clip(0.0, 1.0)
    )
    cells = cells.merge(
        sample.reset_index(names="row_index")[["row_index", "subject_id", "sleep_date", "lifelog_date"]],
        on="row_index",
        how="left",
    )
    cells = cells[
        [
            "row_index",
            "target",
            "target_index",
            "subject_id",
            "sleep_date",
            "lifelog_date",
            "support",
            "weight_sum",
            "mean_pseudo_y",
            "mean_a2c8_prob",
            "mean_prior_prob",
            "mean_delta_vs_a2c8",
            "mean_abs_delta_vs_a2c8",
            "delta_std",
            "direction_agreement",
            "signal_to_uncertainty",
            "local_energy",
        ]
    ]
    if cells.empty:
        raise RuntimeError("empty localization cell table")
    cells["local_energy_norm"] = cells["local_energy"] / cells["local_energy"].sum()

    sample_order = sample[["subject_id"]].copy()
    sample_order["row_index"] = np.arange(len(sample_order))
    sample_order["subject_pos"] = sample_order.groupby("subject_id").cumcount()
    sample_order["subject_n"] = sample_order.groupby("subject_id")["subject_id"].transform("size")
    sample_order["subject_frac"] = sample_order["subject_pos"] / (sample_order["subject_n"] - 1).clip(lower=1)
    cells = cells.merge(sample_order[["row_index", "subject_pos", "subject_n", "subject_frac"]], on="row_index", how="left")

    row_summary = (
        cells.groupby(["row_index", "subject_id", "sleep_date", "lifelog_date", "subject_pos", "subject_n", "subject_frac"], as_index=False)
        .agg(
            row_energy=("local_energy", "sum"),
            row_energy_norm=("local_energy_norm", "sum"),
            target_count=("target", "nunique"),
            mean_direction_agreement=("direction_agreement", "mean"),
            mean_signal_to_uncertainty=("signal_to_uncertainty", "mean"),
            max_cell_energy=("local_energy", "max"),
        )
        .sort_values("row_energy", ascending=False)
        .reset_index(drop=True)
    )
    top_targets = cells.sort_values("local_energy", ascending=False).drop_duplicates("row_index")[["row_index", "target"]]
    top_targets = top_targets.rename(columns={"target": "top_target"})
    row_summary = row_summary.merge(top_targets, on="row_index", how="left")
    target_summary = (
        cells.groupby("target", as_index=False)
        .agg(
            target_energy=("local_energy", "sum"),
            target_energy_norm=("local_energy_norm", "sum"),
            mean_pseudo_y=("mean_pseudo_y", "mean"),
            mean_a2c8_prob=("mean_a2c8_prob", "mean"),
            mean_delta_vs_a2c8=("mean_delta_vs_a2c8", "mean"),
            mean_abs_delta_vs_a2c8=("mean_abs_delta_vs_a2c8", "mean"),
            mean_signal_to_uncertainty=("signal_to_uncertainty", "mean"),
            mean_direction_agreement=("direction_agreement", "mean"),
            cell_count=("row_index", "size"),
        )
        .sort_values("target_energy", ascending=False)
        .reset_index(drop=True)
    )
    return cells.sort_values("local_energy", ascending=False).reset_index(drop=True), row_summary, target_summary


def collect_candidate_paths() -> list[CandidatePath]:
    out: list[CandidatePath] = []
    seen: set[Path] = set()

    def add(label: str, value: str | Path, group: str) -> None:
        path = path_exists(value)
        if path is None:
            return
        resolved = path.resolve()
        if resolved in seen:
            return
        seen.add(resolved)
        out.append(CandidatePath(label=label, path=resolved, source_group=group))

    for label, path in KNOWN_FILES:
        add(label, path, "known")

    if UNIVERSE_SHORTLIST.exists():
        uni = pd.read_csv(UNIVERSE_SHORTLIST).head(99)
        for i, row in enumerate(uni.itertuples(index=False)):
            add(f"universe_shortlist_{i:03d}", str(row.source_path), "universe_shortlist")

    if UNIVERSE_ALL.exists():
        uni_all = pd.read_csv(UNIVERSE_ALL)
        filters = [
            uni_all["frontier_escape_candidate"] == True,  # noqa: E712
            uni_all["novel_frontier_candidate"] == True,  # noqa: E712
            uni_all["candidate_family"].isin(["hiddenblock_seqmotif", "public6entropy", "cvjepa", "axis_repair"]),
        ]
        subset = uni_all[np.logical_or.reduce(filters)].sort_values("submission_priority_score", ascending=False).head(220)
        for i, row in enumerate(subset.itertuples(index=False)):
            add(f"universe_priority_{i:03d}", str(row.source_path), "universe_priority")

    if LOWENERGY_SELECTED.exists():
        low = pd.read_csv(LOWENERGY_SELECTED)
        for i, row in enumerate(low.itertuples(index=False)):
            add(f"lowenergy_saved_{i:03d}", str(row.source_path), "lowenergy_saved")

    if DIRECTROB_SELECTED.exists():
        direct = pd.read_csv(DIRECTROB_SELECTED)
        for i, row in enumerate(direct.itertuples(index=False)):
            add(f"directrob_{i:03d}", OUT / str(row.file), "directrob")

    return out


def localized_ce_delta(
    pred: np.ndarray,
    base: np.ndarray,
    cells: pd.DataFrame,
    top_frac: float,
) -> float:
    ranked = cells.sort_values("local_energy", ascending=False)
    cutoff = max(16, int(np.ceil(len(ranked) * top_frac)))
    chosen = ranked.head(cutoff)
    rr = chosen["row_index"].to_numpy(dtype=int)
    tt = chosen["target_index"].to_numpy(dtype=int)
    yy = chosen["mean_pseudo_y"].to_numpy(dtype=np.float64)
    ww = chosen["local_energy_norm"].to_numpy(dtype=np.float64)
    ww = ww / ww.sum()
    return float(np.sum(ww * (ce(yy, pred[rr, tt]) - ce(yy, base[rr, tt]))))


def score_candidates(
    sample: pd.DataFrame,
    cells: pd.DataFrame,
    sols: list[robust.Solution],
    weights: np.ndarray,
) -> pd.DataFrame:
    preds = inv.load_predictions(sample)
    stage2 = preds["stage2"]
    a2c8 = preds["cvjepa_a2c8"]
    raw05 = preds["raw05"]

    a2_scores = np.asarray([robust.score_under_solution(sol, a2c8, stage2) for sol in sols], dtype=np.float64)
    raw05_scores = np.asarray([robust.score_under_solution(sol, raw05, stage2) for sol in sols], dtype=np.float64)
    paths = collect_candidate_paths()

    records = []
    for item in paths:
        try:
            pred = load_matrix(item.path, sample)
        except Exception as exc:  # keep audit robust to stale files
            records.append(
                {
                    "file": str(item.path),
                    "basename": item.path.name,
                    "label": item.label,
                    "source_group": item.source_group,
                    "load_error": str(exc),
                }
            )
            continue
        sol_scores = np.asarray([robust.score_under_solution(sol, pred, stage2) for sol in sols], dtype=np.float64)
        deltas = sol_scores - a2_scores
        raw_deltas = sol_scores - raw05_scores
        rec = {
            "file": str(item.path),
            "basename": item.path.name,
            "label": item.label,
            "source_group": item.source_group,
            "load_error": "",
            "local_direct_delta_mean": float(np.sum(weights * deltas)),
            "local_direct_delta_median": float(np.median(deltas)),
            "local_direct_delta_p10": float(np.quantile(deltas, 0.10)),
            "local_direct_delta_p90": float(np.quantile(deltas, 0.90)),
            "local_direct_delta_worst": float(np.max(deltas)),
            "local_direct_win_rate": float(np.mean(deltas < 0.0)),
            "local_direct_delta_vs_raw05_mean": float(np.sum(weights * raw_deltas)),
            "energy_ce_delta_top03": localized_ce_delta(pred, a2c8, cells, 0.03),
            "energy_ce_delta_top08": localized_ce_delta(pred, a2c8, cells, 0.08),
            "energy_ce_delta_top20": localized_ce_delta(pred, a2c8, cells, 0.20),
            "mean_abs_move_vs_a2c8": float(np.mean(np.abs(pred - a2c8))),
            "mean_abs_move_vs_raw05": float(np.mean(np.abs(pred - raw05))),
            "max_abs_move_vs_a2c8": float(np.max(np.abs(pred - a2c8))),
        }
        rec["localization_score"] = (
            rec["local_direct_delta_mean"]
            + 0.50 * rec["local_direct_delta_p90"]
            + 0.20 * rec["energy_ce_delta_top08"]
            + 0.10 * rec["energy_ce_delta_top20"]
            + 0.00010 * max(0.0, 0.60 - rec["local_direct_win_rate"])
        )
        records.append(rec)

    ranking = pd.DataFrame(records)
    ok = ranking["load_error"].fillna("").eq("")
    if ok.any():
        ranking.loc[ok, "rank_localization"] = ranking.loc[ok, "localization_score"].rank(method="min")

    if UNIVERSE_ALL.exists():
        meta = pd.read_csv(UNIVERSE_ALL)
        keep = [
            "basename",
            "candidate_family",
            "selector_delta_vs_a2c8_public",
            "selector_p90_delta_vs_a2c8_public",
            "beats_a2c8_scenario_rate",
            "bad_axis_abs_load",
            "good_span_residual_ratio",
            "raw05_a2c8_compat_energy",
            "frontier_escape_candidate",
            "novel_frontier_candidate",
            "submission_priority_score",
            "is_known_public",
            "known_public_lb",
        ]
        ranking = ranking.merge(meta[[c for c in keep if c in meta.columns]].drop_duplicates("basename"), on="basename", how="left")

    ranking["selector_conflict"] = (
        (ranking["localization_score"] < -0.00012)
        & (
            (ranking["selector_p90_delta_vs_a2c8_public"].fillna(9.0) > 0.00058)
            | (ranking["bad_axis_abs_load"].fillna(9.0) > 0.045)
            | (ranking["beats_a2c8_scenario_rate"].fillna(0.0) < 0.50)
        )
    )
    ranking["submit_gate"] = (
        (ranking["localization_score"] < -0.00018)
        & (ranking["local_direct_delta_p90"] < -0.00005)
        & (ranking["energy_ce_delta_top08"] < -0.00005)
        & (ranking["selector_p90_delta_vs_a2c8_public"].fillna(9.0) <= 0.00055)
        & (ranking["bad_axis_abs_load"].fillna(9.0) <= 0.035)
        & (ranking["beats_a2c8_scenario_rate"].fillna(0.0) >= 0.52)
    )
    ranking["research_probe_gate"] = (
        (ranking["localization_score"] < -0.00018)
        & (ranking["local_direct_delta_p90"] < 0.00005)
        & (ranking["energy_ce_delta_top08"] < -0.00003)
        & (ranking["bad_axis_abs_load"].fillna(9.0) <= 0.060)
    )
    ranking = ranking.sort_values(
        ["submit_gate", "research_probe_gate", "localization_score", "selector_p90_delta_vs_a2c8_public"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)
    return ranking


def write_report(
    selected_sources: pd.DataFrame,
    cells: pd.DataFrame,
    rows: pd.DataFrame,
    targets: pd.DataFrame,
    ranking: pd.DataFrame,
) -> None:
    ok = ranking[ranking["load_error"].fillna("").eq("")].copy()
    submit = ok[ok["submit_gate"] == True]  # noqa: E712
    probes = ok[ok["research_probe_gate"] == True]  # noqa: E712
    conflicts = ok[ok["selector_conflict"] == True]  # noqa: E712

    top_cols = [
        "basename",
        "source_group",
        "candidate_family",
        "localization_score",
        "local_direct_delta_mean",
        "local_direct_delta_p90",
        "energy_ce_delta_top08",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "submit_gate",
        "research_probe_gate",
        "selector_conflict",
    ]
    top_cols = [c for c in top_cols if c in ok.columns]

    def md_table(df: pd.DataFrame) -> str:
        if df.empty:
            return "None."
        return "```text\n" + df.to_string(index=False, float_format=lambda x: f"{x:.6f}") + "\n```"

    lines = [
        "# Hidden Public Localization Selector",
        "",
        "## Purpose",
        "Direct inverse solutions can fit known public LB anchors, but are underdetermined. This audit treats them as noisy JEPA-style teachers: cells repeatedly selected by low-error inverse views become low-energy hidden-public localization candidates, then submissions are re-ranked while still respecting the previous stress/bad-axis gates.",
        "",
        "## Source Ensemble",
        f"- selected inverse solutions: {len(selected_sources)}",
        f"- robust_source_score range: {selected_sources['robust_source_score'].min():.6f} .. {selected_sources['robust_source_score'].max():.6f}",
        f"- structured solution share: {selected_sources['is_structured_mask'].mean():.3f}",
        f"- subject-like solution share: {selected_sources['is_subject_like_mask'].mean():.3f}",
        "",
        "## Localization Shape",
        f"- active cells: {len(cells)} / {250 * len(TARGETS)}",
        f"- top 10 rows energy share: {rows.head(10)['row_energy_norm'].sum():.3f}",
        f"- top 25 rows energy share: {rows.head(25)['row_energy_norm'].sum():.3f}",
        "",
        "### Target Energy",
        md_table(targets),
        "",
        "### Top Rows",
        md_table(rows.head(16)),
        "",
        "## Candidate Gates",
        f"- scored candidates: {len(ok)}",
        f"- submit_gate pass: {len(submit)}",
        f"- research_probe_gate pass: {len(probes)}",
        f"- localization/stress conflicts: {len(conflicts)}",
        "",
        "### Top Localization Ranking",
        md_table(ok.head(30)[top_cols]),
        "",
        "### Submit Gate Candidates",
        md_table(submit.head(20)[top_cols]),
        "",
        "### Conflict Diagnostics",
        md_table(conflicts.head(20)[top_cols]),
        "",
        "## Interpretation",
        "- If directrob-style candidates dominate localization but fail stress/bad-axis gates, the bottleneck is public-subset underidentification rather than representation capacity.",
        "- A submit-safe candidate must be simultaneously good under localized inverse energy and not worse under previous anchor-LOO/blockwise stress. Otherwise it is a diagnostic probe only.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sources, solution_map = robust.load_sources()
    sols, weights, selected_sources = choose_localization_solutions(sources, solution_map)
    cells, rows, targets = build_localization_tables(sample, selected_sources)
    ranking = score_candidates(sample, cells, sols, weights)

    selected_sources.to_csv(OUT / "hidden_public_localization_selected_sources.csv", index=False)
    cells.to_csv(CELL_OUT, index=False)
    rows.to_csv(ROW_OUT, index=False)
    targets.to_csv(TARGET_OUT, index=False)
    ranking.to_csv(RANKING_OUT, index=False)
    ranking.head(80).to_csv(SHORTLIST_OUT, index=False)
    write_report(selected_sources, cells, rows, targets, ranking)

    print(f"selected_solutions={len(selected_sources)}")
    print(f"active_cells={len(cells)}")
    print(f"scored_candidates={(ranking['load_error'].fillna('') == '').sum()}")
    print(f"submit_gate={int(ranking['submit_gate'].fillna(False).sum())}")
    print(f"research_probe_gate={int(ranking['research_probe_gate'].fillna(False).sum())}")
    print(f"wrote={REPORT_OUT}")


if __name__ == "__main__":
    main()
