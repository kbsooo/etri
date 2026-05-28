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
from public_subset_sensitivity_audit import build_masks  # noqa: E402
from raw05_jepa_q3s4_gate_audit import expand_hidden_posterior, focused_scenario_scores  # noqa: E402


Q3S4 = ["Q3", "S4"]

BASES = {
    "axisc073": "submission_blockscale_jepa_axisproj_pareto03_rt_same_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p03_c0p18_c07320e0.csv",
    "axis71": "submission_blockscale_jepa_axisproj_pareto03_rt_local_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p05_c0p08_71abf82b.csv",
    "seq1501": "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv",
    "rate605": "submission_hiddenblock_rateprobe_neutral_605de284.csv",
    "pareto03": "submission_hiddenblock_paretomix_w0.3_b7621063.csv",
    "pm_fit": "submission_publicmask_jepa_q3s4_c32a8a7e.csv",
    "pm_tg": "submission_publicmask_jepa_q3s4_50528018.csv",
}

MOVE_SOURCES = {
    "raw05_stage2": (
        "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    ),
    "gate_seq1501": (
        "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv",
        "submission_raw05_jepa_q3s4gate_81f94b63.csv",
    ),
    "gate_rate605": (
        "submission_hiddenblock_rateprobe_neutral_605de284.csv",
        "submission_raw05_jepa_q3s4gate_f4c2a96d.csv",
    ),
    "gate_seqd0": (
        "submission_hiddenblock_seqmotif_neutral_d0ca7647.csv",
        "submission_raw05_jepa_q3s4gate_718c45ed.csv",
    ),
    "blockjepa_raw05": (
        "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
        "submission_blockscale_jepa_raw05_rt_same_ridge_zctx_a12_blend0p1_q3s4_w0p03_dcf4387c.csv",
    ),
    "blockjepa_pareto": (
        "submission_hiddenblock_paretomix_w0.3_b7621063.csv",
        "submission_blockscale_jepa_pareto03_rt_same_ridge_zctx_a12_blend0p1_q3s4_w0p03_94f874fc.csv",
    ),
}

MASK_TABLES = {
    "fit": "public_lb_inverse_mask_top512.csv",
    "rawcompat": "public_lb_inverse_mask_raw05_compatible_top512.csv",
    "allsign": "public_lb_inverse_mask_all_sign_compatible_top512.csv",
}


def read_submission(file_name: str) -> pd.DataFrame:
    path = OUT / file_name
    if not path.exists():
        path = JEPA / file_name
    if not path.exists():
        raise FileNotFoundError(file_name)
    return pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def normalize01(values: np.ndarray) -> np.ndarray:
    x = np.asarray(values, dtype=np.float64)
    finite = np.isfinite(x)
    if not finite.any():
        return np.zeros_like(x, dtype=np.float64)
    lo = float(np.nanmin(x[finite]))
    hi = float(np.nanmax(x[finite]))
    if hi <= lo + 1e-12:
        return np.zeros_like(x, dtype=np.float64)
    out = (x - lo) / (hi - lo)
    out[~finite] = 0.0
    return np.clip(out, 0.0, 1.0)


def sharpen(values: np.ndarray, lo_q: float = 0.35, hi_q: float = 0.90) -> np.ndarray:
    x = normalize01(values)
    lo = float(np.quantile(x, lo_q))
    hi = float(np.quantile(x, hi_q))
    if hi <= lo + 1e-12:
        return x
    return np.clip((x - lo) / (hi - lo), 0.0, 1.0)


def table_weight(table: pd.DataFrame, top_n: int, temp: float = 0.45) -> pd.DataFrame:
    sub = table.head(top_n).copy()
    score = sub["inverse_fit_score"].astype(float).to_numpy()
    score = score - float(score.min())
    weights = np.exp(-score / max(temp, 1e-6))
    sub["posterior_weight"] = weights / max(float(weights.sum()), 1e-12)
    return sub


def block_context(sample: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, list[str], np.ndarray, np.ndarray]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        ["subject_id", "lifelog_date"]
    ).reset_index(drop=True)
    block_ids = sample_block_ids(train, sample)
    block_names = list(pd.unique(block_ids))
    block_index = {b: i for i, b in enumerate(block_names)}
    block_mat = np.zeros((len(block_names), len(sample)), dtype=np.float64)
    for row_idx, block_id in enumerate(block_ids):
        block_mat[block_index[str(block_id)], row_idx] = 1.0
    block_sizes = block_mat.sum(axis=1)
    block_meta = pd.read_csv(OUT / "hidden_block_posterior_block_summary.csv")
    return train, block_ids, block_names, block_mat, block_sizes, block_meta


def block_scores_from_masks(
    table: pd.DataFrame,
    masks: list[dict[str, object]],
    block_mat: np.ndarray,
    block_sizes: np.ndarray,
    top_n: int,
) -> np.ndarray:
    weighted = table_weight(table, top_n=top_n)
    score = np.zeros(block_mat.shape[0], dtype=np.float64)
    denom = np.maximum(block_sizes, 1.0)
    for row in weighted.itertuples(index=False):
        mask = masks[int(row.mask_index)]["mask"]
        assert isinstance(mask, np.ndarray)
        coverage = (block_mat @ mask.astype(np.float64)) / denom
        score += float(row.posterior_weight) * coverage
    return score


def block_scores_from_target_delta(
    target_delta: pd.DataFrame,
    score_table: pd.DataFrame,
    masks: list[dict[str, object]],
    block_mat: np.ndarray,
    block_sizes: np.ndarray,
    target: str,
    top_n: int,
) -> np.ndarray:
    score_lookup = score_table.set_index(["scenario_file", "mask_index"])["inverse_fit_score"].to_dict()
    sub = target_delta[target_delta["target"].eq(target)].copy()
    sub["inverse_fit_score"] = [score_lookup.get((r.scenario_file, int(r.mask_index)), np.nan) for r in sub.itertuples(index=False)]
    sub = sub.dropna(subset=["inverse_fit_score"]).sort_values("inverse_fit_score").head(top_n).copy()
    gain = np.maximum(-sub["pred_delta_raw05"].astype(float).to_numpy(), 0.0)
    active = gain > 0
    if not active.any():
        return np.zeros(block_mat.shape[0], dtype=np.float64)
    sub = sub.loc[active].copy()
    gain = gain[active]
    fit = sub["inverse_fit_score"].astype(float).to_numpy()
    fit = fit - float(fit.min())
    weights = np.exp(-fit / 0.45) * gain
    weights = weights / max(float(weights.sum()), 1e-12)
    score = np.zeros(block_mat.shape[0], dtype=np.float64)
    denom = np.maximum(block_sizes, 1.0)
    for wt, row in zip(weights, sub.itertuples(index=False)):
        mask = masks[int(row.mask_index)]["mask"]
        assert isinstance(mask, np.ndarray)
        coverage = (block_mat @ mask.astype(np.float64)) / denom
        score += float(wt) * coverage
    return score


def jepa_block_agreement(block_names: list[str], block_meta: pd.DataFrame) -> tuple[dict[str, np.ndarray], pd.DataFrame]:
    summary = pd.read_csv(OUT / "block_scale_jepa_target_summary.csv")
    rates = pd.read_csv(OUT / "block_scale_jepa_target_hidden_rates.csv")
    top_methods = summary.head(12)["method"].astype(str).tolist()
    rates = rates[rates["method"].astype(str).isin(top_methods)].copy()
    meta = block_meta.set_index("hidden_block_id")
    out: dict[str, np.ndarray] = {}
    rows = []
    for target in Q3S4:
        pivot = rates.pivot_table(index="hidden_block_id", columns="method", values=f"rate_{target}", aggfunc="mean")
        agree = np.zeros(len(block_names), dtype=np.float64)
        strength = np.zeros(len(block_names), dtype=np.float64)
        raw_dir_arr = np.zeros(len(block_names), dtype=np.float64)
        jepa_dir_arr = np.zeros(len(block_names), dtype=np.float64)
        post_agree = np.zeros(len(block_names), dtype=np.float64)
        target_rows = []
        for i, block_id in enumerate(block_names):
            if block_id not in meta.index or block_id not in pivot.index:
                continue
            stage = float(meta.loc[block_id, f"stage2_rate_{target}"])
            raw = float(meta.loc[block_id, f"raw05_rate_{target}"])
            posterior = float(meta.loc[block_id, f"posterior_rate_{target}"])
            vals = pivot.loc[block_id].dropna().to_numpy(dtype=np.float64)
            if vals.size == 0:
                continue
            raw_dir = raw - stage
            dirs = vals - stage
            if abs(raw_dir) <= 1e-8:
                agree_i = 0.0
            else:
                agree_i = float(np.mean(np.sign(dirs) == np.sign(raw_dir)))
            jepa_dir = float(np.mean(vals) - stage)
            agree[i] = agree_i
            strength[i] = abs(jepa_dir)
            raw_dir_arr[i] = raw_dir
            jepa_dir_arr[i] = jepa_dir
            post_agree[i] = float(np.sign(posterior - stage) == np.sign(raw_dir)) if abs(raw_dir) > 1e-8 else 0.0
            target_rows.append(
                {
                    "_block_pos": i,
                    "hidden_block_id": block_id,
                    "target": target,
                    "stage2_rate": stage,
                    "raw05_rate": raw,
                    "posterior_rate": posterior,
                    "jepa_mean_rate": float(np.mean(vals)),
                    "jepa_std_rate": float(np.std(vals)),
                    "raw_dir": raw_dir,
                    "jepa_dir": jepa_dir,
                    "jepa_raw_agree_frac": agree_i,
                    "posterior_raw_agree": post_agree[i],
                }
            )
        strength = sharpen(strength, 0.20, 0.85)
        out[target] = np.clip(0.10 + 0.70 * agree * strength + 0.20 * post_agree * agree, 0.0, 1.0)
        for row in target_rows:
            row["jepa_gate"] = float(out[target][int(row["_block_pos"])])
            row.pop("_block_pos", None)
            rows.append(row)
    return out, pd.DataFrame(rows)


def rows_from_block_score(block_ids: np.ndarray, block_names: list[str], block_score: np.ndarray) -> np.ndarray:
    lookup = {b: float(block_score[i]) for i, b in enumerate(block_names)}
    return np.asarray([lookup[str(b)] for b in block_ids], dtype=np.float64)


def make_gates(sample: pd.DataFrame) -> tuple[dict[str, np.ndarray], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train, block_ids, block_names, block_mat, block_sizes, block_meta = block_context(sample)
    masks = build_masks(sample)
    fit_table = pd.read_csv(OUT / "public_lb_inverse_mask_top512.csv")
    target_delta = pd.read_csv(OUT / "public_lb_inverse_target_delta_top64.csv")
    jepa_gate, jepa_detail = jepa_block_agreement(block_names, block_meta)

    gates: dict[str, np.ndarray] = {}
    gate_rows = []
    block_rows = []
    base_block_scores: dict[str, np.ndarray] = {}
    for kind, table_name in MASK_TABLES.items():
        table = pd.read_csv(OUT / table_name)
        for top_n in [24, 64, 128]:
            score = block_scores_from_masks(table, masks, block_mat, block_sizes, top_n=top_n)
            gate = sharpen(score, 0.35, 0.90)
            name = f"block{kind}{top_n}"
            base_block_scores[name] = gate
            mat = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
            row_gate = rows_from_block_score(block_ids, block_names, gate)
            for target in Q3S4:
                mat[:, TARGETS.index(target)] = row_gate
            gates[name] = mat
            gate_rows.append(
                {
                    "gate": name,
                    "kind": kind,
                    "top_n": top_n,
                    "mean": float(row_gate.mean()),
                    "max": float(row_gate.max()),
                    "p90": float(np.quantile(row_gate, 0.90)),
                    "active_frac_0p5": float((row_gate > 0.5).mean()),
                }
            )
            for block_id, raw_score, g in zip(block_names, score, gate):
                block_rows.append({"gate": name, "hidden_block_id": block_id, "raw_score": float(raw_score), "gate_score": float(g)})

    for top_n in [24, 64]:
        target_scores: dict[str, np.ndarray] = {}
        for target in Q3S4:
            score = block_scores_from_target_delta(target_delta, fit_table, masks, block_mat, block_sizes, target, top_n=top_n)
            gate = sharpen(score, 0.10, 0.80)
            target_scores[target] = gate
            row_gate = rows_from_block_score(block_ids, block_names, gate)
            mat = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
            mat[:, TARGETS.index(target)] = row_gate
            name = f"blocktarget{top_n}_{target}"
            gates[name] = mat
            gate_rows.append(
                {
                    "gate": name,
                    "kind": "targetgain",
                    "top_n": top_n,
                    "mean": float(row_gate.mean()),
                    "max": float(row_gate.max()),
                    "p90": float(np.quantile(row_gate, 0.90)),
                    "active_frac_0p5": float((row_gate > 0.5).mean()),
                }
            )
            for block_id, raw_score, g in zip(block_names, score, gate):
                block_rows.append({"gate": name, "hidden_block_id": block_id, "raw_score": float(raw_score), "gate_score": float(g)})

        for source_name in [f"blockrawcompat{top_n}", f"blockfit{top_n}"]:
            if source_name not in base_block_scores:
                continue
            mat = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
            for target in Q3S4:
                combined = np.clip(base_block_scores[source_name] * jepa_gate[target], 0.0, 1.0)
                mat[:, TARGETS.index(target)] = rows_from_block_score(block_ids, block_names, combined)
            name = f"{source_name}_jepa"
            gates[name] = mat
            vals = mat[:, [TARGETS.index(t) for t in Q3S4]]
            gate_rows.append(
                {
                    "gate": name,
                    "kind": "block_public_jepa",
                    "top_n": top_n,
                    "mean": float(vals.mean()),
                    "max": float(vals.max()),
                    "p90": float(np.quantile(vals, 0.90)),
                    "active_frac_0p5": float((vals > 0.5).mean()),
                }
            )

        mat = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
        for target in Q3S4:
            combined = np.clip(target_scores[target] * jepa_gate[target], 0.0, 1.0)
            mat[:, TARGETS.index(target)] = rows_from_block_score(block_ids, block_names, combined)
        name = f"blocktarget{top_n}_jepa"
        gates[name] = mat
        vals = mat[:, [TARGETS.index(t) for t in Q3S4]]
        gate_rows.append(
            {
                "gate": name,
                "kind": "target_public_jepa",
                "top_n": top_n,
                "mean": float(vals.mean()),
                "max": float(vals.max()),
                "p90": float(np.quantile(vals, 0.90)),
                "active_frac_0p5": float((vals > 0.5).mean()),
            }
        )

    return gates, pd.DataFrame(gate_rows), pd.DataFrame(block_rows), jepa_detail


def score_candidate(pred: np.ndarray, preds: dict[str, np.ndarray], posterior: np.ndarray, raw_q: np.ndarray) -> dict[str, float]:
    raw05_rawaxis = expected_delta(raw_q, preds["raw05"], preds["stage2"])
    bad_axis = preds["jepa_bad_residual"] - preds["stage2"]
    ordinal_axis = preds["ordinal_q"] - preds["stage2"]
    raw_expected = 0.5779449757 + expected_delta(raw_q, pred, preds["stage2"])
    posterior_expected = 0.5784273528 + expected_delta(posterior, pred, preds["anchor578"])
    return {
        "posterior_expected_public_vs_anchor": posterior_expected,
        "raw_axis_expected_public_vs_stage2": raw_expected,
        "delta_vs_raw05_rawaxis": expected_delta(raw_q, pred, preds["stage2"]) - raw05_rawaxis,
        "bad_residual_axis_ratio": float(expected_delta(clip(preds["stage2"] + bad_axis), pred, preds["stage2"])),
        "bad_residual_projection_ratio": projection_ratio(pred - preds["stage2"], bad_axis),
        "ordinal_axis_ratio": projection_ratio(pred - preds["stage2"], ordinal_axis),
        "mean_abs_move_vs_raw05": float(np.abs(pred - preds["raw05"]).mean()),
        "min_prob": float(pred.min()),
        "max_prob": float(pred.max()),
    }


def projection_ratio(move: np.ndarray, axis: np.ndarray) -> float:
    a = np.asarray(move, dtype=np.float64).ravel()
    b = np.asarray(axis, dtype=np.float64).ravel()
    denom = float(np.dot(b, b))
    if denom <= 1e-18:
        return 0.0
    return float(np.dot(a, b) / denom)


def integrity(files: list[str], sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    ref_key = sample[KEY].reset_index(drop=True)
    for file_name in files:
        df = read_submission(file_name)
        pred = df[TARGETS].to_numpy(dtype=np.float64)
        rows.append(
            {
                "file": file_name,
                "rows": len(df),
                "key_ok": bool(df[KEY].reset_index(drop=True).equals(ref_key)),
                "duplicate_keys": int(df.duplicated(KEY).sum()),
                "null_probs": int(df[TARGETS].isna().sum().sum()),
                "min_prob": float(np.nanmin(pred)),
                "max_prob": float(np.nanmax(pred)),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        ["subject_id", "lifelog_date"]
    ).reset_index(drop=True)
    _frames, preds = load_predictions()
    raw_q = raw_axis_latent_q(preds["stage2"], preds["raw05"])
    posterior = preds.get("posterior")
    if posterior is None:
        posterior = expand_hidden_posterior(train, sample)

    gates, gate_summary, block_gate_detail, jepa_detail = make_gates(sample)
    gate_summary.to_csv(OUT / "block_public_jepa_q3s4_gate_summary.csv", index=False)
    block_gate_detail.to_csv(OUT / "block_public_jepa_q3s4_block_gate_detail.csv", index=False)
    jepa_detail.to_csv(OUT / "block_public_jepa_q3s4_jepa_block_agreement.csv", index=False)

    base_frames = {k: read_submission(v) for k, v in BASES.items() if (OUT / v).exists() or (JEPA / v).exists()}
    base_preds = {k: f[TARGETS].to_numpy(dtype=np.float64) for k, f in base_frames.items()}

    moves: dict[str, np.ndarray] = {}
    for move_name, (src_base, src_file) in MOVE_SOURCES.items():
        if not ((OUT / src_file).exists() or (JEPA / src_file).exists()):
            continue
        src_base_pred = read_submission(src_base)[TARGETS].to_numpy(dtype=np.float64)
        src_pred = read_submission(src_file)[TARGETS].to_numpy(dtype=np.float64)
        move = logit(src_pred) - logit(src_base_pred)
        keep = np.zeros_like(move, dtype=bool)
        for target in Q3S4:
            keep[:, TARGETS.index(target)] = True
        move[~keep] = 0.0
        moves[move_name] = np.clip(move, -0.40, 0.40)

    gammas = [0.20, 0.35, 0.50, 0.75, 1.00, 1.25]
    records = []
    candidates: list[tuple[str, pd.DataFrame]] = []
    for base_name, base in base_preds.items():
        base_logit = logit(base)
        for move_name, move in moves.items():
            for gate_name, gate in gates.items():
                if gate[:, [TARGETS.index(t) for t in Q3S4]].mean() <= 1e-9:
                    continue
                for gamma in gammas:
                    pred = clip(sigmoid(base_logit + gamma * gate * move))
                    if np.abs(pred - base).mean() < 1e-8:
                        continue
                    tag = stable_tag(f"{base_name}|{move_name}|{gate_name}|{gamma}")
                    file_name = f"submission_blockpublic_jepa_q3s4_{tag}.csv"
                    rec = {
                        "file": file_name,
                        "base": base_name,
                        "base_file": BASES[base_name],
                        "move": move_name,
                        "gate": gate_name,
                        "gamma": gamma,
                        "mean_gate_q3": float(gate[:, TARGETS.index("Q3")].mean()),
                        "mean_gate_s4": float(gate[:, TARGETS.index("S4")].mean()),
                        "active_gate_frac_q3": float((gate[:, TARGETS.index("Q3")] > 0.5).mean()),
                        "active_gate_frac_s4": float((gate[:, TARGETS.index("S4")] > 0.5).mean()),
                        "mean_abs_move_vs_base": float(np.abs(pred - base).mean()),
                    }
                    rec.update(score_candidate(pred, preds, posterior, raw_q))
                    records.append(rec)
                    out = base_frames[base_name].copy()
                    out[TARGETS] = pred
                    candidates.append((file_name, out))

    scores = pd.DataFrame(records)
    scores["selection_score"] = (
        scores["posterior_expected_public_vs_anchor"]
        + 50.0 * np.maximum(scores["delta_vs_raw05_rawaxis"], 0.0)
        + 0.060 * np.maximum(scores["bad_residual_projection_ratio"], 0.0)
        + 0.030 * np.abs(scores["ordinal_axis_ratio"])
        + 0.20 * np.maximum(scores["mean_abs_move_vs_raw05"] - 0.0025, 0.0)
    )
    scores = scores.sort_values(["selection_score", "delta_vs_raw05_rawaxis", "posterior_expected_public_vs_anchor"]).reset_index(drop=True)
    scores.to_csv(OUT / "block_public_jepa_q3s4_scores.csv", index=False)

    safe = scores[
        (scores["delta_vs_raw05_rawaxis"] <= 3.0e-6)
        & (scores["bad_residual_projection_ratio"].abs() <= 0.035)
        & (scores["ordinal_axis_ratio"].abs() <= 0.045)
        & (scores["mean_abs_move_vs_raw05"] <= 0.0032)
    ].copy()
    selected = (
        pd.concat(
            [
                safe.head(45),
                scores.sort_values("posterior_expected_public_vs_anchor").head(25),
                scores.sort_values("raw_axis_expected_public_vs_stage2").head(25),
            ],
            ignore_index=True,
        )
        .drop_duplicates("file")
        .head(60)
        .reset_index(drop=True)
    )
    selected.to_csv(OUT / "block_public_jepa_q3s4_selected.csv", index=False)

    selected_files = set(selected["file"].tolist())
    for file_name, out in candidates:
        if file_name in selected_files:
            out.to_csv(OUT / file_name, index=False)

    selected_names = selected["file"].tolist()
    integ = integrity(selected_names, sample)
    proxy = public_proxy_scores(selected_names)
    focus = focused_scenario_scores(selected_names)
    integ.to_csv(OUT / "block_public_jepa_q3s4_integrity.csv", index=False)
    proxy.to_csv(OUT / "block_public_jepa_q3s4_proxy.csv", index=False)
    focus.to_csv(OUT / "block_public_jepa_q3s4_focused_scenario.csv", index=False)

    shortlist = selected.merge(proxy, on="file", suffixes=("", "_proxy"), how="left")
    if not focus.empty:
        shortlist = shortlist.merge(focus, on="file", how="left")
    shortlist = shortlist.merge(integ, on="file", how="left", suffixes=("", "_integrity"))
    shortlist = shortlist.sort_values(
        ["delta_vs_raw05_rawaxis", "posterior_expected_public_vs_anchor", "focused_scenario_score"],
        na_position="last",
    ).reset_index(drop=True)
    shortlist.to_csv(OUT / "block_public_jepa_q3s4_shortlist.csv", index=False)

    top_block_cols = ["gate", "hidden_block_id", "raw_score", "gate_score"]
    top_blocks = (
        block_gate_detail.sort_values(["gate", "gate_score"], ascending=[True, False])
        .groupby("gate", sort=False)
        .head(6)[top_block_cols]
        .round(8)
    )
    lines = [
        "# Block-Public JEPA Q3/S4 Gate Fusion",
        "",
        "Compress inverse-public row masks into hidden-block gates, then multiply by block-scale JEPA direction agreement.",
        "",
        "## Gate Summary",
        "",
        "```csv",
        gate_summary.round(8).to_csv(index=False).strip(),
        "```",
        "",
        "## Top Blocks By Gate",
        "",
        "```csv",
        top_blocks.to_csv(index=False).strip(),
        "```",
        "",
        "## Top Shortlist",
        "",
        "```csv",
        shortlist[
            [
                "file",
                "base",
                "move",
                "gate",
                "gamma",
                "posterior_expected_public_vs_anchor",
                "raw_axis_expected_public_vs_stage2",
                "delta_vs_raw05_rawaxis",
                "bad_residual_projection_ratio",
                "ordinal_axis_ratio",
                "mean_abs_move_vs_raw05",
                "focused_scenario_score",
            ]
        ]
        .head(35)
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
    (OUT / "block_public_jepa_q3s4_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("[block-public jepa q3/s4] candidates", len(scores), "selected", len(selected))
    print(shortlist[["file", "base", "move", "gate", "gamma", "posterior_expected_public_vs_anchor", "delta_vs_raw05_rawaxis", "focused_scenario_score"]].head(25).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
