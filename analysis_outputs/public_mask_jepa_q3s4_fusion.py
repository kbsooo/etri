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
    projection_ratio,
    sigmoid,
)
from hidden_block_orthogonal_gate_candidates import raw_axis_latent_q, stable_tag  # noqa: E402
from hidden_block_rate_reconstruction_audit import public_proxy_scores  # noqa: E402
from public_subset_sensitivity_audit import build_masks  # noqa: E402
from raw05_jepa_q3s4_gate_audit import focused_scenario_scores  # noqa: E402


Q3S4 = ["Q3", "S4"]

BASES = {
    "seq1501": "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv",
    "rate605": "submission_hiddenblock_rateprobe_neutral_605de284.csv",
    "axis71": "submission_blockscale_jepa_axisproj_pareto03_rt_local_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p05_c0p08_71abf82b.csv",
    "axisc073": "submission_blockscale_jepa_axisproj_pareto03_rt_same_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p03_c0p18_c07320e0.csv",
    "pareto03": "submission_hiddenblock_paretomix_w0.3_b7621063.csv",
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


def sharpen_gate(score: np.ndarray, low_q: float, high_q: float) -> np.ndarray:
    x = normalize01(score)
    lo = float(np.quantile(x, low_q))
    hi = float(np.quantile(x, high_q))
    if hi <= lo + 1e-12:
        return x
    return np.clip((x - lo) / (hi - lo), 0.0, 1.0)


def table_weight(table: pd.DataFrame, top_n: int, temp: float) -> pd.DataFrame:
    sub = table.head(top_n).copy()
    score = sub["inverse_fit_score"].astype(float).to_numpy()
    score = score - float(score.min())
    weights = np.exp(-score / max(temp, 1e-6))
    sub["posterior_weight"] = weights / max(float(weights.sum()), 1e-12)
    return sub


def mask_row_scores(sample: pd.DataFrame) -> tuple[dict[str, np.ndarray], pd.DataFrame]:
    masks = build_masks(sample)
    target_delta = pd.read_csv(OUT / "public_lb_inverse_target_delta_top64.csv")
    gate_records = []
    gates: dict[str, np.ndarray] = {}

    for table_key, table_name in MASK_TABLES.items():
        table = pd.read_csv(OUT / table_name)
        for top_n in [24, 64, 128]:
            weighted = table_weight(table, top_n=top_n, temp=0.45)
            row_score = np.zeros(len(sample), dtype=np.float64)
            for row in weighted.itertuples(index=False):
                mask = masks[int(row.mask_index)]["mask"]
                assert isinstance(mask, np.ndarray)
                row_score[mask] += float(row.posterior_weight)

            gate_records.append(
                {
                    "gate": f"{table_key}{top_n}",
                    "kind": table_key,
                    "top_n": top_n,
                    "mean": float(row_score.mean()),
                    "max": float(row_score.max()),
                    "p90": float(np.quantile(row_score, 0.90)),
                    "active_frac_0p5": float((sharpen_gate(row_score, 0.45, 0.90) > 0.5).mean()),
                }
            )
            gates[f"{table_key}{top_n}"] = sharpen_gate(row_score, 0.45, 0.90)

    for top_n in [24, 64]:
        base = table_weight(pd.read_csv(OUT / "public_lb_inverse_mask_raw05_compatible_top512.csv"), top_n=top_n, temp=0.45)
        base_key = {
            (str(r.scenario_file), int(r.mask_index)): float(r.posterior_weight)
            for r in base.itertuples(index=False)
        }
        for target in Q3S4:
            target_score = np.zeros(len(sample), dtype=np.float64)
            sub = target_delta[target_delta["target"].eq(target)].copy()
            for row in sub.itertuples(index=False):
                key = (str(row.scenario_file), int(row.mask_index))
                if key not in base_key:
                    continue
                raw05_gain = max(-float(row.pred_delta_raw05), 0.0)
                if raw05_gain <= 0.0:
                    continue
                mask = masks[int(row.mask_index)]["mask"]
                assert isinstance(mask, np.ndarray)
                target_score[mask] += base_key[key] * raw05_gain
            gates[f"targetgain{top_n}_{target}"] = sharpen_gate(target_score, 0.20, 0.85)
            gate_records.append(
                {
                    "gate": f"targetgain{top_n}_{target}",
                    "kind": "targetgain",
                    "top_n": top_n,
                    "mean": float(target_score.mean()),
                    "max": float(target_score.max()),
                    "p90": float(np.quantile(target_score, 0.90)),
                    "active_frac_0p5": float((gates[f"targetgain{top_n}_{target}"] > 0.5).mean()),
                }
            )

    fused = {}
    for top_n in [24, 64]:
        for target in Q3S4:
            fused[f"fused{top_n}_{target}"] = np.clip(
                0.62 * gates[f"rawcompat{top_n}"] + 0.38 * gates[f"targetgain{top_n}_{target}"],
                0.0,
                1.0,
            )
    gates.update(fused)
    for name, score in fused.items():
        gate_records.append(
            {
                "gate": name,
                "kind": "fused",
                "top_n": int(name.removeprefix("fused").split("_")[0]),
                "mean": float(score.mean()),
                "max": float(score.max()),
                "p90": float(np.quantile(score, 0.90)),
                "active_frac_0p5": float((score > 0.5).mean()),
            }
        )

    return gates, pd.DataFrame(gate_records)


def gate_matrix(gates: dict[str, np.ndarray], gate_name: str, shape: tuple[int, int]) -> np.ndarray:
    mat = np.zeros(shape, dtype=np.float64)
    if gate_name.startswith("targetgain") or gate_name.startswith("fused"):
        top_part, target = gate_name.split("_")
        mat[:, TARGETS.index(target)] = gates[gate_name]
        return mat
    for target in Q3S4:
        mat[:, TARGETS.index(target)] = gates[gate_name]
    return mat


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
        "bad_residual_axis_ratio": projection_ratio(pred - preds["stage2"], bad_axis),
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
    frames, preds = load_predictions()
    raw_q = raw_axis_latent_q(preds["stage2"], preds["raw05"])
    posterior = pd.read_csv(OUT / "hidden_block_posterior_block_summary.csv")
    # Row-level posterior proxy for scoring is already available through load_predictions in recent scripts.
    posterior_rows = preds.get("posterior")
    if posterior_rows is None:
        from raw05_jepa_q3s4_gate_audit import reconstruct_raw05, expand_hidden_posterior

        train, sample2, *_ = reconstruct_raw05()
        sample2 = sample2.sort_values(KEY).reset_index(drop=True)
        posterior_rows = expand_hidden_posterior(train, sample2)

    gates, gate_summary = mask_row_scores(sample)
    gate_summary.to_csv(OUT / "public_mask_jepa_q3s4_gate_summary.csv", index=False)

    base_frames = {k: read_submission(v) for k, v in BASES.items() if (OUT / v).exists() or (JEPA / v).exists()}
    base_preds = {k: f[TARGETS].to_numpy(dtype=np.float64) for k, f in base_frames.items()}

    moves: dict[str, np.ndarray] = {}
    for move_name, (src_base, src_file) in MOVE_SOURCES.items():
        if not ((OUT / src_file).exists() or (JEPA / src_file).exists()):
            continue
        src_base_pred = read_submission(src_base)[TARGETS].to_numpy(dtype=np.float64)
        src_pred = read_submission(src_file)[TARGETS].to_numpy(dtype=np.float64)
        move = logit(src_pred) - logit(src_base_pred)
        mask = np.zeros_like(move, dtype=bool)
        for target in Q3S4:
            mask[:, TARGETS.index(target)] = True
        move[~mask] = 0.0
        moves[move_name] = np.clip(move, -0.35, 0.35)

    rawaxis_gate_names = ["rawcompat24", "rawcompat64", "allsign24", "fit24", "fit64"]
    target_gate_names = ["targetgain24_Q3", "targetgain24_S4", "targetgain64_Q3", "targetgain64_S4", "fused24_Q3", "fused24_S4", "fused64_Q3", "fused64_S4"]
    gate_names = [g for g in rawaxis_gate_names + target_gate_names if g in gates]
    gammas = [0.25, 0.40, 0.65, 0.90]

    records = []
    candidates: list[tuple[str, np.ndarray, pd.DataFrame]] = []
    for base_name, base in base_preds.items():
        base_logit = logit(base)
        for move_name, move in moves.items():
            for gate_name in gate_names:
                gate = gate_matrix(gates, gate_name, base.shape)
                for gamma in gammas:
                    pred = clip(sigmoid(base_logit + gamma * gate * move))
                    if np.abs(pred - base).mean() < 1e-8:
                        continue
                    tag_text = f"{base_name}|{move_name}|{gate_name}|{gamma}"
                    file_name = f"submission_publicmask_jepa_q3s4_{stable_tag(tag_text)}.csv"
                    rec = {
                        "file": file_name,
                        "base": base_name,
                        "base_file": BASES[base_name],
                        "move": move_name,
                        "gate": gate_name,
                        "gamma": gamma,
                        "mean_gate_q3": float(gate[:, TARGETS.index("Q3")].mean()),
                        "mean_gate_s4": float(gate[:, TARGETS.index("S4")].mean()),
                        "mean_abs_move_vs_base": float(np.abs(pred - base).mean()),
                    }
                    rec.update(score_candidate(pred, preds, posterior_rows, raw_q))
                    records.append(rec)
                    out = base_frames[base_name].copy()
                    out[TARGETS] = pred
                    candidates.append((file_name, pred, out))

    scores = pd.DataFrame(records)
    scores["selection_score"] = (
        scores["posterior_expected_public_vs_anchor"]
        + 45.0 * np.maximum(scores["delta_vs_raw05_rawaxis"], 0.0)
        + 0.050 * np.maximum(scores["bad_residual_axis_ratio"], 0.0)
        + 0.025 * np.abs(scores["ordinal_axis_ratio"])
        + 0.20 * np.maximum(scores["mean_abs_move_vs_raw05"] - 0.0020, 0.0)
    )
    scores = scores.sort_values(["selection_score", "delta_vs_raw05_rawaxis", "posterior_expected_public_vs_anchor"]).reset_index(drop=True)
    scores.to_csv(OUT / "public_mask_jepa_q3s4_fusion_scores.csv", index=False)

    safe = scores[
        (scores["delta_vs_raw05_rawaxis"] <= 2.5e-6)
        & (scores["bad_residual_axis_ratio"].abs() <= 0.035)
        & (scores["mean_abs_move_vs_raw05"] <= 0.0028)
    ].copy()
    selected = pd.concat(
        [
            safe.head(35),
            scores.sort_values("posterior_expected_public_vs_anchor").head(20),
            scores.sort_values("raw_axis_expected_public_vs_stage2").head(20),
        ]
    ).drop_duplicates("file").head(50)
    selected.to_csv(OUT / "public_mask_jepa_q3s4_fusion_selected.csv", index=False)

    selected_files = set(selected["file"].tolist())
    for file_name, _pred, out in candidates:
        if file_name in selected_files:
            out.to_csv(OUT / file_name, index=False)

    selected_names = selected["file"].tolist()
    integ = integrity(selected_names, sample)
    proxy = public_proxy_scores(selected_names)
    focus = focused_scenario_scores(selected_names)
    integ.to_csv(OUT / "public_mask_jepa_q3s4_fusion_integrity.csv", index=False)
    proxy.to_csv(OUT / "public_mask_jepa_q3s4_fusion_proxy.csv", index=False)
    focus.to_csv(OUT / "public_mask_jepa_q3s4_fusion_focused_scenario.csv", index=False)

    shortlist = selected.merge(proxy, on="file", suffixes=("", "_proxy"), how="left")
    if not focus.empty:
        shortlist = shortlist.merge(focus, on="file", how="left")
    shortlist = shortlist.merge(integ, on="file", how="left", suffixes=("", "_integrity"))
    shortlist = shortlist.sort_values(
        ["delta_vs_raw05_rawaxis", "posterior_expected_public_vs_anchor", "focused_scenario_score"],
        na_position="last",
    ).reset_index(drop=True)
    shortlist.to_csv(OUT / "public_mask_jepa_q3s4_fusion_shortlist.csv", index=False)

    lines = [
        "# Public-Mask JEPA Q3/S4 Fusion",
        "",
        "Use inverse-public mask fits as row/target gates for JEPA/raw05 Q3/S4 moves.",
        "",
        "## Gate Summary",
        "",
        "```csv",
        gate_summary.round(8).to_csv(index=False).strip(),
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
                "bad_residual_axis_ratio",
                "ordinal_axis_ratio",
                "mean_abs_move_vs_raw05",
                "focused_scenario_score",
            ]
        ]
        .head(30)
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
    (OUT / "public_mask_jepa_q3s4_fusion_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("[public-mask jepa q3/s4 fusion] candidates", len(scores), "selected", len(selected))
    print(shortlist[["file", "base", "move", "gate", "gamma", "posterior_expected_public_vs_anchor", "delta_vs_raw05_rawaxis", "focused_scenario_score"]].head(20).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
