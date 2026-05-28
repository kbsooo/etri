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

from hidden_block_latent_audit import (  # noqa: E402
    KEY,
    TARGETS,
    clip,
    expected_delta,
    load_predictions,
    logit,
    sample_block_ids,
    sigmoid,
)
from hidden_block_orthogonal_gate_candidates import raw_axis_latent_q, stable_tag  # noqa: E402
from hidden_block_rate_reconstruction_audit import public_proxy_scores  # noqa: E402
from raw05_jepa_q3s4_gate_audit import expand_hidden_posterior, focused_scenario_scores  # noqa: E402
from block_public_jepa_q3s4_gate_fusion import make_gates  # noqa: E402


BASES = {
    "pm_tg": "submission_publicmask_jepa_q3s4_50528018.csv",
    "pm_fit": "submission_publicmask_jepa_q3s4_c32a8a7e.csv",
    "block_best": "submission_blockpublic_jepa_q3s4_8e3e0d92.csv",
    "axisc073": "submission_blockscale_jepa_axisproj_pareto03_rt_same_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p03_c0p18_c07320e0.csv",
}

TARGET_SETS = {
    "Q3": ["Q3"],
    "S4": ["S4"],
    "Q3S4": ["Q3", "S4"],
    "noq2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
}


def read_submission(file_name: str) -> pd.DataFrame:
    path = OUT / file_name
    if not path.exists():
        path = JEPA / file_name
    if not path.exists():
        raise FileNotFoundError(file_name)
    return pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def exists(file_name: str) -> bool:
    return (OUT / file_name).exists() or (JEPA / file_name).exists()


def projection_ratio(move: np.ndarray, axis: np.ndarray) -> float:
    a = np.asarray(move, dtype=np.float64).ravel()
    b = np.asarray(axis, dtype=np.float64).ravel()
    denom = float(np.dot(b, b))
    if denom <= 1e-18:
        return 0.0
    return float(np.dot(a, b) / denom)


def mean_shift_delta(probs: np.ndarray, desired_mean: float, cap: float) -> float:
    p = clip(probs)
    desired = float(np.clip(desired_mean, 1e-4, 1.0 - 1e-4))
    current = float(p.mean())
    if abs(current - desired) <= 1e-10:
        return 0.0
    z = logit(p)
    lo, hi = -4.0, 4.0
    for _ in range(36):
        mid = 0.5 * (lo + hi)
        val = float(sigmoid(z + mid).mean())
        if val < desired:
            lo = mid
        else:
            hi = mid
    return float(np.clip(0.5 * (lo + hi), -cap, cap))


def load_block_context(sample: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, list[str], dict[str, np.ndarray], pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        ["subject_id", "lifelog_date"]
    ).reset_index(drop=True)
    block_ids = sample_block_ids(train, sample)
    block_names = list(pd.unique(block_ids))
    block_masks = {block_id: block_ids == block_id for block_id in block_names}
    meta = pd.read_csv(OUT / "hidden_block_posterior_block_summary.csv").set_index("hidden_block_id")
    return train, block_ids, block_names, block_masks, meta


def rate_lookup_for_methods(methods: list[str], reducer: str, block_names: list[str]) -> tuple[np.ndarray, np.ndarray]:
    rates = pd.read_csv(OUT / "block_scale_jepa_target_hidden_rates.csv")
    sub = rates[rates["method"].astype(str).isin(methods)].copy()
    out = np.full((len(block_names), len(TARGETS)), np.nan, dtype=np.float64)
    spread = np.full((len(block_names), len(TARGETS)), np.nan, dtype=np.float64)
    for bi, block_id in enumerate(block_names):
        block = sub[sub["hidden_block_id"].eq(block_id)]
        if block.empty:
            continue
        for tj, target in enumerate(TARGETS):
            vals = block[f"rate_{target}"].dropna().to_numpy(dtype=np.float64)
            if vals.size == 0:
                continue
            if reducer == "median":
                out[bi, tj] = float(np.median(vals))
            else:
                out[bi, tj] = float(np.mean(vals))
            spread[bi, tj] = float(np.std(vals))
    return clip(out), np.nan_to_num(spread, nan=0.0)


def build_rate_sources(block_names: list[str]) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], pd.DataFrame]:
    summary = pd.read_csv(OUT / "block_scale_jepa_target_summary.csv")
    detail = pd.read_csv(OUT / "block_scale_jepa_target_target_detail.csv")
    sources: dict[str, np.ndarray] = {}
    spreads: dict[str, np.ndarray] = {}
    rows = []

    for name, n, reducer in [
        ("best1", 1, "mean"),
        ("top3_mean", 3, "mean"),
        ("top8_median", 8, "median"),
        ("top12_mean", 12, "mean"),
    ]:
        methods = summary.head(n)["method"].astype(str).tolist()
        arr, spread = rate_lookup_for_methods(methods, reducer, block_names)
        sources[name] = arr
        spreads[name] = spread
        rows.append({"source": name, "kind": "global", "n_methods": n, "reducer": reducer, "methods": ";".join(methods)})

    target_best = np.zeros((len(block_names), len(TARGETS)), dtype=np.float64)
    target_top3 = np.zeros((len(block_names), len(TARGETS)), dtype=np.float64)
    target_spread = np.zeros((len(block_names), len(TARGETS)), dtype=np.float64)
    for target in TARGETS:
        best_methods = detail[detail["target"].eq(target)].sort_values("target_logloss").head(1)["method"].astype(str).tolist()
        top3_methods = detail[detail["target"].eq(target)].sort_values("target_logloss").head(3)["method"].astype(str).tolist()
        best_arr, _ = rate_lookup_for_methods(best_methods, "mean", block_names)
        top3_arr, spread = rate_lookup_for_methods(top3_methods, "mean", block_names)
        j = TARGETS.index(target)
        target_best[:, j] = best_arr[:, j]
        target_top3[:, j] = top3_arr[:, j]
        target_spread[:, j] = spread[:, j]
        rows.append({"source": "target_best", "kind": target, "n_methods": 1, "reducer": "mean", "methods": ";".join(best_methods)})
        rows.append({"source": "target_top3_mean", "kind": target, "n_methods": 3, "reducer": "mean", "methods": ";".join(top3_methods)})
    sources["target_best"] = clip(target_best)
    sources["target_top3_mean"] = clip(target_top3)
    spreads["target_best"] = target_spread
    spreads["target_top3_mean"] = target_spread
    return sources, spreads, pd.DataFrame(rows)


def block_gate_from_row_gate(
    gate_matrix: np.ndarray,
    block_masks: dict[str, np.ndarray],
    block_names: list[str],
) -> np.ndarray:
    out = np.ones((len(block_names), len(TARGETS)), dtype=np.float64)
    for bi, block_id in enumerate(block_names):
        idx = block_masks[block_id]
        out[bi] = gate_matrix[idx].mean(axis=0)
    return out


def build_gate_sources(
    sample: pd.DataFrame,
    block_masks: dict[str, np.ndarray],
    block_names: list[str],
    meta: pd.DataFrame,
    rate_sources: dict[str, np.ndarray],
    spreads: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    gates = {"none": np.ones((len(block_names), len(TARGETS)), dtype=np.float64)}
    row_gates, _summary, _detail, _jepa_detail = make_gates(sample)
    for name in ["blockallsign128", "blockrawcompat64_jepa", "blocktarget64_jepa", "blockfit64_jepa"]:
        if name in row_gates:
            gates[name] = block_gate_from_row_gate(row_gates[name], block_masks, block_names)

    for source_name, rates in rate_sources.items():
        spread = spreads[source_name]
        consensus = np.clip(1.0 - spread / 0.10, 0.15, 1.0)
        gates[f"consensus_{source_name}"] = consensus

        raw_agree = np.ones_like(consensus) * 0.18
        for bi, block_id in enumerate(block_names):
            if block_id not in meta.index:
                continue
            for tj, target in enumerate(TARGETS):
                stage = float(meta.loc[block_id, f"stage2_rate_{target}"])
                raw = float(meta.loc[block_id, f"raw05_rate_{target}"])
                if np.sign(rates[bi, tj] - stage) == np.sign(raw - stage):
                    raw_agree[bi, tj] = 1.0
        gates[f"rawagree_{source_name}"] = raw_agree
        if "blockallsign128" in gates:
            gates[f"allsign_rawagree_{source_name}"] = np.clip(gates["blockallsign128"] * raw_agree, 0.0, 1.0)
        if "blockrawcompat64_jepa" in gates:
            gates[f"rawcompatjepa_consensus_{source_name}"] = np.clip(gates["blockrawcompat64_jepa"] * consensus, 0.0, 1.0)
    return gates


def apply_count_shift(
    base: np.ndarray,
    block_names: list[str],
    block_masks: dict[str, np.ndarray],
    rate_source: np.ndarray,
    gate: np.ndarray,
    target_set: list[str],
    alpha: float,
    cap: float,
    round_counts: bool,
) -> tuple[np.ndarray, dict[str, float]]:
    pred = base.copy()
    offsets = []
    active = 0
    for bi, block_id in enumerate(block_names):
        idx = block_masks[block_id]
        n = int(idx.sum())
        for target in target_set:
            tj = TARGETS.index(target)
            current = float(pred[idx, tj].mean())
            desired_rate = float(rate_source[bi, tj])
            if round_counts:
                desired_rate = float(np.clip(round(desired_rate * n) / max(n, 1), 1e-4, 1.0 - 1e-4))
            desired = (1.0 - alpha) * current + alpha * desired_rate
            delta = mean_shift_delta(pred[idx, tj], desired, cap=cap)
            delta *= float(gate[bi, tj])
            if abs(delta) <= 1e-10:
                continue
            pred[idx, tj] = sigmoid(logit(pred[idx, tj]) + delta)
            offsets.append(abs(delta))
            active += n
    return clip(pred), {
        "mean_abs_offset": float(np.mean(offsets)) if offsets else 0.0,
        "max_abs_offset": float(np.max(offsets)) if offsets else 0.0,
        "active_rows_total": float(active),
    }


def score_candidate(pred: np.ndarray, preds: dict[str, np.ndarray], posterior: np.ndarray, raw_q: np.ndarray) -> dict[str, float]:
    raw05_rawaxis = expected_delta(raw_q, preds["raw05"], preds["stage2"])
    bad_axis = preds["jepa_bad_residual"] - preds["stage2"]
    ordinal_axis = preds["ordinal_q"] - preds["stage2"]
    raw_delta = expected_delta(raw_q, pred, preds["stage2"])
    return {
        "posterior_expected_public_vs_anchor": 0.5784273528 + expected_delta(posterior, pred, preds["anchor578"]),
        "raw_axis_expected_public_vs_stage2": 0.5779449757 + raw_delta,
        "delta_vs_raw05_rawaxis": raw_delta - raw05_rawaxis,
        "bad_residual_projection_ratio": projection_ratio(pred - preds["stage2"], bad_axis),
        "ordinal_axis_ratio": projection_ratio(pred - preds["stage2"], ordinal_axis),
        "mean_abs_move_vs_raw05": float(np.abs(pred - preds["raw05"]).mean()),
        "min_prob": float(pred.min()),
        "max_prob": float(pred.max()),
    }


def integrity(files: list[str], sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    ref_key = sample[KEY].reset_index(drop=True)
    for file_name in files:
        df = read_submission(file_name)
        vals = df[TARGETS].to_numpy(dtype=np.float64)
        rows.append(
            {
                "file": file_name,
                "rows": len(df),
                "key_ok": bool(df[KEY].reset_index(drop=True).equals(ref_key)),
                "duplicate_keys": int(df.duplicated(KEY).sum()),
                "null_probs": int(df[TARGETS].isna().sum().sum()),
                "min_prob": float(np.nanmin(vals)),
                "max_prob": float(np.nanmax(vals)),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    train, _block_ids, block_names, block_masks, meta = load_block_context(sample)
    _frames, preds = load_predictions()
    raw_q = raw_axis_latent_q(preds["stage2"], preds["raw05"])
    posterior = preds.get("posterior")
    if posterior is None:
        posterior = expand_hidden_posterior(train, sample)

    rate_sources, spreads, rate_meta = build_rate_sources(block_names)
    rate_meta.to_csv(OUT / "jepa_block_count_shift_rate_sources.csv", index=False)
    gate_sources = build_gate_sources(sample, block_masks, block_names, meta, rate_sources, spreads)

    base_frames = {k: read_submission(v) for k, v in BASES.items() if exists(v)}
    base_preds = {k: f[TARGETS].to_numpy(dtype=np.float64) for k, f in base_frames.items()}

    gate_plan = [
        "none",
        "blockallsign128",
        "blocktarget64_jepa",
        "consensus_best1",
        "rawagree_best1",
        "allsign_rawagree_best1",
    ]
    rate_plan = ["best1", "top3_mean", "target_top3_mean"]
    target_plan = {k: TARGET_SETS[k] for k in ["Q3", "S4", "Q3S4"]}
    alphas = [0.03, 0.06, 0.10, 0.16]
    caps = [0.035, 0.070, 0.120]

    records = []
    candidates: list[tuple[str, pd.DataFrame]] = []
    for base_name, base in base_preds.items():
        for rate_name in rate_plan:
            rates = rate_sources[rate_name]
            for gate_name in gate_plan:
                if gate_name not in gate_sources:
                    continue
                gate = gate_sources[gate_name]
                for target_set_name, target_set in target_plan.items():
                    for alpha in alphas:
                        for cap in caps:
                            for round_counts in [False, True]:
                                pred, shift_meta = apply_count_shift(
                                    base,
                                    block_names,
                                    block_masks,
                                    rates,
                                    gate,
                                    target_set,
                                    alpha=alpha,
                                    cap=cap,
                                    round_counts=round_counts,
                                )
                                if np.abs(pred - base).mean() < 1e-8:
                                    continue
                                tag = stable_tag(f"{base_name}|{rate_name}|{gate_name}|{target_set_name}|{alpha}|{cap}|{round_counts}")
                                file_name = f"submission_jepa_block_countshift_{tag}.csv"
                                rec = {
                                    "file": file_name,
                                    "base": base_name,
                                    "base_file": BASES[base_name],
                                    "rate_source": rate_name,
                                    "gate": gate_name,
                                    "target_set": target_set_name,
                                    "alpha": alpha,
                                    "cap": cap,
                                    "round_counts": bool(round_counts),
                                    "mean_abs_move_vs_base": float(np.abs(pred - base).mean()),
                                }
                                rec.update(shift_meta)
                                rec.update(score_candidate(pred, preds, posterior, raw_q))
                                records.append(rec)
                                out = base_frames[base_name].copy()
                                out[TARGETS] = pred
                                candidates.append((file_name, out))

    scores = pd.DataFrame(records)
    scores["selection_score"] = (
        scores["posterior_expected_public_vs_anchor"]
        + 70.0 * np.maximum(scores["delta_vs_raw05_rawaxis"], 0.0)
        + 0.070 * np.maximum(scores["bad_residual_projection_ratio"], 0.0)
        + 0.035 * np.abs(scores["ordinal_axis_ratio"])
        + 0.25 * np.maximum(scores["mean_abs_move_vs_raw05"] - 0.0030, 0.0)
    )
    scores = scores.sort_values(["selection_score", "delta_vs_raw05_rawaxis", "posterior_expected_public_vs_anchor"]).reset_index(drop=True)
    scores.to_csv(OUT / "jepa_block_count_shift_scores.csv", index=False)

    safe = scores[
        (scores["delta_vs_raw05_rawaxis"] <= 3.0e-6)
        & (scores["bad_residual_projection_ratio"].abs() <= 0.035)
        & (scores["ordinal_axis_ratio"].abs() <= 0.050)
        & (scores["mean_abs_move_vs_raw05"] <= 0.0035)
    ].copy()
    selected = (
        pd.concat(
            [
                safe.head(55),
                scores.sort_values("posterior_expected_public_vs_anchor").head(25),
                scores.sort_values("raw_axis_expected_public_vs_stage2").head(25),
            ],
            ignore_index=True,
        )
        .drop_duplicates("file")
        .head(80)
        .reset_index(drop=True)
    )
    selected.to_csv(OUT / "jepa_block_count_shift_selected.csv", index=False)

    selected_files = set(selected["file"].tolist())
    for file_name, out in candidates:
        if file_name in selected_files:
            out.to_csv(OUT / file_name, index=False)

    selected_names = selected["file"].tolist()
    integ = integrity(selected_names, sample)
    proxy = public_proxy_scores(selected_names)
    focus = focused_scenario_scores(selected_names)
    integ.to_csv(OUT / "jepa_block_count_shift_integrity.csv", index=False)
    proxy.to_csv(OUT / "jepa_block_count_shift_proxy.csv", index=False)
    focus.to_csv(OUT / "jepa_block_count_shift_focused_scenario.csv", index=False)

    shortlist = selected.merge(proxy, on="file", suffixes=("", "_proxy"), how="left")
    if not focus.empty:
        shortlist = shortlist.merge(focus, on="file", how="left")
    shortlist = shortlist.merge(integ, on="file", how="left", suffixes=("", "_integrity"))
    shortlist = shortlist.sort_values(
        ["focused_scenario_score", "mean_expected", "posterior_expected_public_vs_anchor"],
        na_position="last",
    ).reset_index(drop=True)
    shortlist.to_csv(OUT / "jepa_block_count_shift_shortlist.csv", index=False)

    lines = [
        "# JEPA Block Count Shift",
        "",
        "Apply block-level common logit shifts so each hidden block moves toward JEPA-predicted expected counts while preserving row ranking inside each block.",
        "",
        "## Rate Sources",
        "",
        "```csv",
        rate_meta.to_csv(index=False).strip(),
        "```",
        "",
        "## Top Shortlist",
        "",
        "```csv",
        shortlist[
            [
                "file",
                "base",
                "rate_source",
                "gate",
                "target_set",
                "alpha",
                "cap",
                "round_counts",
                "posterior_expected_public_vs_anchor",
                "raw_axis_expected_public_vs_stage2",
                "delta_vs_raw05_rawaxis",
                "bad_residual_projection_ratio",
                "ordinal_axis_ratio",
                "mean_abs_move_vs_raw05",
                "mean_expected",
                "focused_scenario_score",
            ]
        ]
        .head(40)
        .round(10)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## Integrity",
        "",
        "```csv",
        integ.round(10).to_csv(index=False).strip(),
        "```",
    ]
    (OUT / "jepa_block_count_shift_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("[jepa block count shift] candidates", len(scores), "selected", len(selected))
    cols = [
        "file",
        "base",
        "rate_source",
        "gate",
        "target_set",
        "alpha",
        "cap",
        "round_counts",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "mean_expected",
        "focused_scenario_score",
    ]
    print(shortlist[cols].head(25).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
