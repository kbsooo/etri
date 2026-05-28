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

from hidden_block_latent_audit import KEY, TARGETS, clip, load_predictions, logit, sigmoid  # noqa: E402
from hidden_block_orthogonal_gate_candidates import raw_axis_latent_q, stable_tag  # noqa: E402
from hidden_block_rate_reconstruction_audit import public_proxy_scores  # noqa: E402
from raw05_jepa_q3s4_gate_audit import expand_hidden_posterior, focused_scenario_scores  # noqa: E402
from block_public_jepa_q3s4_gate_fusion import make_gates, read_submission, score_candidate, integrity  # noqa: E402


Q3S4 = ["Q3", "S4"]

BASES = {
    "pm_tg": "submission_publicmask_jepa_q3s4_50528018.csv",
    "pm_tg_alt": "submission_publicmask_jepa_q3s4_5def572e.csv",
    "pm_fit": "submission_publicmask_jepa_q3s4_c32a8a7e.csv",
    "pm_fit64": "submission_publicmask_jepa_q3s4_64ce1de9.csv",
    "block_best": "submission_blockpublic_jepa_q3s4_8e3e0d92.csv",
    "axisc073": "submission_blockscale_jepa_axisproj_pareto03_rt_same_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p03_c0p18_c07320e0.csv",
}

MOVE_SOURCES = {
    "blockjepa_raw05": (
        "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
        "submission_blockscale_jepa_raw05_rt_same_ridge_zctx_a12_blend0p1_q3s4_w0p03_dcf4387c.csv",
    ),
    "blockjepa_pareto": (
        "submission_hiddenblock_paretomix_w0.3_b7621063.csv",
        "submission_blockscale_jepa_pareto03_rt_same_ridge_zctx_a12_blend0p1_q3s4_w0p03_94f874fc.csv",
    ),
    "gate_seq1501": (
        "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv",
        "submission_raw05_jepa_q3s4gate_81f94b63.csv",
    ),
    "gate_seqd0": (
        "submission_hiddenblock_seqmotif_neutral_d0ca7647.csv",
        "submission_raw05_jepa_q3s4gate_718c45ed.csv",
    ),
    "gate_rate605": (
        "submission_hiddenblock_rateprobe_neutral_605de284.csv",
        "submission_raw05_jepa_q3s4gate_f4c2a96d.csv",
    ),
}

GATE_NAMES = [
    "blockallsign24",
    "blockallsign64",
    "blockallsign128",
    "blocktarget24_S4",
    "blocktarget64_S4",
    "blocktarget24_jepa",
    "blocktarget64_jepa",
    "blockrawcompat24_jepa",
    "blockrawcompat64_jepa",
    "blockfit24_jepa",
    "blockfit64_jepa",
]


def exists(file_name: str) -> bool:
    return (OUT / file_name).exists() or (JEPA / file_name).exists()


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
    gates, _gate_summary, _block_detail, _jepa_detail = make_gates(sample)

    base_frames = {k: read_submission(v) for k, v in BASES.items() if exists(v)}
    base_preds = {k: f[TARGETS].to_numpy(dtype=np.float64) for k, f in base_frames.items()}
    moves: dict[str, np.ndarray] = {}
    for move_name, (src_base, src_file) in MOVE_SOURCES.items():
        if not exists(src_base) or not exists(src_file):
            continue
        src_base_pred = read_submission(src_base)[TARGETS].to_numpy(dtype=np.float64)
        src_pred = read_submission(src_file)[TARGETS].to_numpy(dtype=np.float64)
        move = logit(src_pred) - logit(src_base_pred)
        keep = np.zeros_like(move, dtype=bool)
        for target in Q3S4:
            keep[:, TARGETS.index(target)] = True
        move[~keep] = 0.0
        moves[move_name] = np.clip(move, -0.40, 0.40)

    gammas = [0.05, 0.08, 0.10, 0.13, 0.16, 0.20, 0.25, 0.30, 0.35, 0.40, 0.46, 0.52, 0.60]
    records = []
    candidates: list[tuple[str, pd.DataFrame]] = []
    for base_name, base in base_preds.items():
        base_logit = logit(base)
        for move_name, move in moves.items():
            for gate_name in GATE_NAMES:
                if gate_name not in gates:
                    continue
                gate = gates[gate_name]
                if gate[:, [TARGETS.index(t) for t in Q3S4]].mean() <= 1e-9:
                    continue
                for gamma in gammas:
                    pred = clip(sigmoid(base_logit + gamma * gate * move))
                    if np.abs(pred - base).mean() < 1e-8:
                        continue
                    tag = stable_tag(f"refine|{base_name}|{move_name}|{gate_name}|{gamma}")
                    file_name = f"submission_blockpublic_jepa_refine_{tag}.csv"
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
                    rec.update(score_candidate(pred, preds, posterior, raw_q))
                    records.append(rec)
                    out = base_frames[base_name].copy()
                    out[TARGETS] = pred
                    candidates.append((file_name, out))

    scores = pd.DataFrame(records)
    scores["selection_score"] = (
        scores["posterior_expected_public_vs_anchor"]
        + 60.0 * np.maximum(scores["delta_vs_raw05_rawaxis"], 0.0)
        + 0.060 * np.maximum(scores["bad_residual_projection_ratio"], 0.0)
        + 0.030 * np.abs(scores["ordinal_axis_ratio"])
        + 0.20 * np.maximum(scores["mean_abs_move_vs_raw05"] - 0.0025, 0.0)
    )
    scores = scores.sort_values(["selection_score", "delta_vs_raw05_rawaxis", "posterior_expected_public_vs_anchor"]).reset_index(drop=True)
    scores.to_csv(OUT / "block_public_jepa_q3s4_refine_scores.csv", index=False)

    safe = scores[
        (scores["delta_vs_raw05_rawaxis"] <= 1.5e-6)
        & (scores["bad_residual_projection_ratio"].abs() <= 0.030)
        & (scores["ordinal_axis_ratio"].abs() <= 0.040)
        & (scores["mean_abs_move_vs_raw05"] <= 0.0022)
    ].copy()
    selected = (
        pd.concat(
            [
                safe.head(45),
                scores.sort_values("posterior_expected_public_vs_anchor").head(20),
                scores.sort_values("raw_axis_expected_public_vs_stage2").head(20),
            ],
            ignore_index=True,
        )
        .drop_duplicates("file")
        .head(70)
        .reset_index(drop=True)
    )
    selected.to_csv(OUT / "block_public_jepa_q3s4_refine_selected.csv", index=False)

    selected_files = set(selected["file"].tolist())
    for file_name, out in candidates:
        if file_name in selected_files:
            out.to_csv(OUT / file_name, index=False)

    names = selected["file"].tolist()
    integ = integrity(names, sample)
    proxy = public_proxy_scores(names)
    focus = focused_scenario_scores(names)
    integ.to_csv(OUT / "block_public_jepa_q3s4_refine_integrity.csv", index=False)
    proxy.to_csv(OUT / "block_public_jepa_q3s4_refine_proxy.csv", index=False)
    focus.to_csv(OUT / "block_public_jepa_q3s4_refine_focused_scenario.csv", index=False)

    shortlist = selected.merge(proxy, on="file", suffixes=("", "_proxy"), how="left")
    if not focus.empty:
        shortlist = shortlist.merge(focus, on="file", how="left")
    shortlist = shortlist.merge(integ, on="file", how="left", suffixes=("", "_integrity"))
    shortlist = shortlist.sort_values(
        ["focused_scenario_score", "mean_expected", "posterior_expected_public_vs_anchor"],
        na_position="last",
    ).reset_index(drop=True)
    shortlist.to_csv(OUT / "block_public_jepa_q3s4_refine_shortlist.csv", index=False)

    lines = [
        "# Block-Public JEPA Q3/S4 Refine",
        "",
        "Focused gamma scan around row-gated public-mask candidates plus block-public JEPA gates.",
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
                "mean_expected",
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
    (OUT / "block_public_jepa_q3s4_refine_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("[block-public refine] candidates", len(scores), "selected", len(selected))
    cols = ["file", "base", "move", "gate", "gamma", "posterior_expected_public_vs_anchor", "delta_vs_raw05_rawaxis", "mean_expected", "focused_scenario_score"]
    print(shortlist[cols].head(25).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
