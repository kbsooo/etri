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
    sys.path.append(str(OUT))

from hidden_block_latent_audit import TARGETS, KEY, clip, logit, read_submission, sample_block_ids, sigmoid  # noqa: E402
from hidden_block_orthogonal_gate_candidates import stable_tag  # noqa: E402
from hidden_block_rate_reconstruction_audit import public_proxy_scores  # noqa: E402
from hidden_block_sequence_motif_neutral_mix import mix_logits  # noqa: E402


RAW05 = JEPA / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
PARETO03 = OUT / "submission_hiddenblock_paretomix_w0.3_b7621063.csv"

SAFE_SOURCES = [
    "submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv",
    "submission_hiddenblock_paretomix_w0.3_b7621063.csv",
    "submission_hiddenblock_paretomix_w0.4_507296eb.csv",
    "submission_hiddenblock_rateprobe_neutral_95ebba6c.csv",
    "submission_hiddenblock_rateprobe_neutral_605de284.csv",
    "submission_hiddenblock_rateprobe_neutral_27ca3bb0.csv",
]


def ce_delta(q: np.ndarray, cand: np.ndarray, base: np.ndarray) -> np.ndarray:
    q = clip(q)
    cand = clip(cand)
    base = clip(base)
    return q * (np.log(base) - np.log(cand)) + (1.0 - q) * (np.log1p(-base) - np.log1p(-cand))


def latent_qs() -> tuple[np.ndarray, np.ndarray]:
    from hidden_block_latent_audit import load_predictions
    from hidden_block_orthogonal_gate_candidates import raw_axis_latent_q

    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        ["subject_id", "lifelog_date"]
    ).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    _frames, preds = load_predictions()
    raw_q = raw_axis_latent_q(preds["stage2"], preds["raw05"])
    block_ids = sample_block_ids(train, sample)
    block_df = pd.read_csv(OUT / "hidden_block_posterior_block_summary.csv").set_index("hidden_block_id")
    posterior = np.zeros_like(preds["raw05"])
    for i, block_id in enumerate(block_ids):
        for j, target in enumerate(TARGETS):
            posterior[i, j] = float(block_df.loc[block_id, f"posterior_rate_{target}"])
    return clip(raw_q), clip(posterior)


def direct_probe_sources() -> list[str]:
    path = OUT / "hidden_block_sequence_motif_candidate_proxy.csv"
    proxy = pd.read_csv(path)
    pool: list[str] = []
    for f in proxy.sort_values(["raw_axis_expected_public_vs_stage2", "posterior_expected_public_vs_anchor"])["file"].head(10):
        if (OUT / str(f)).exists() and str(f) not in pool:
            pool.append(str(f))
    for f in proxy.sort_values(["posterior_expected_public_vs_anchor", "raw_axis_expected_public_vs_stage2"])["file"].head(10):
        if (OUT / str(f)).exists() and str(f) not in pool:
            pool.append(str(f))
    return pool[:14]


def direct_base_for(probe_file: str) -> Path:
    if "_raw05_" in probe_file:
        return RAW05
    if "_pareto03_" in probe_file:
        return PARETO03
    raise ValueError(f"cannot infer direct base: {probe_file}")


def row_metadata() -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        ["subject_id", "lifelog_date"]
    ).reset_index(drop=True)
    block_ids = sample_block_ids(train, sample)
    meta = sample[KEY].copy()
    meta["hidden_block_id"] = block_ids
    meta["row_index"] = np.arange(len(sample))
    block_summary = pd.read_csv(OUT / "hidden_block_posterior_block_summary.csv")[
        ["hidden_block_id", "n_rows", "prev_train_gap_days", "next_train_gap_days"]
    ]
    return meta.merge(block_summary, on="hidden_block_id", how="left")


def decompose_direct_probe(probe_file: str, raw_q: np.ndarray, posterior_q: np.ndarray, meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = read_submission(direct_base_for(probe_file))[TARGETS].to_numpy(dtype=np.float64)
    probe = read_submission(OUT / probe_file)[TARGETS].to_numpy(dtype=np.float64)
    raw = ce_delta(raw_q, probe, base)
    post = ce_delta(posterior_q, probe, base)
    rows = []
    for j, target in enumerate(TARGETS):
        rows.append(
            {
                "file": probe_file,
                "base": direct_base_for(probe_file).name,
                "target": target,
                "raw_delta": float(raw[:, j].mean()),
                "posterior_delta": float(post[:, j].mean()),
                "raw_bad_cell_frac": float((raw[:, j] > 0).mean()),
                "posterior_good_cell_frac": float((post[:, j] < 0).mean()),
                "conflict_cell_frac": float(((raw[:, j] > 0) & (post[:, j] < 0)).mean()),
                "synergy_cell_frac": float(((raw[:, j] <= 0) & (post[:, j] < 0)).mean()),
                "mean_abs_logit_move": float(np.abs(logit(probe[:, j]) - logit(base[:, j])).mean()),
            }
        )
    target_df = pd.DataFrame(rows)
    flat = []
    for j, target in enumerate(TARGETS):
        tmp = meta[["hidden_block_id", "subject_id", "n_rows"]].copy()
        tmp["file"] = probe_file
        tmp["target"] = target
        tmp["raw_delta"] = raw[:, j]
        tmp["posterior_delta"] = post[:, j]
        tmp["logit_move"] = logit(probe[:, j]) - logit(base[:, j])
        tmp["raw_bad_post_good"] = (tmp["raw_delta"] > 0) & (tmp["posterior_delta"] < 0)
        flat.append(tmp)
    cell = pd.concat(flat, ignore_index=True)
    block_target = (
        cell.groupby(["file", "hidden_block_id", "subject_id", "n_rows", "target"], observed=True)
        .agg(
            raw_delta=("raw_delta", "mean"),
            posterior_delta=("posterior_delta", "mean"),
            raw_bad_post_good_frac=("raw_bad_post_good", "mean"),
            mean_abs_logit_move=("logit_move", lambda s: float(np.mean(np.abs(s)))),
        )
        .reset_index()
    )
    return target_df, block_target


def make_cell_gated_candidates(raw_q: np.ndarray, posterior_q: np.ndarray) -> pd.DataFrame:
    probes = direct_probe_sources()
    records = []
    saved = []
    gate_specs = [
        ("raw_nonpos_post_good", 0.0, True),
        ("raw_nonpos", 0.0, False),
        ("raw_tiny_post_good", 2.5e-5, True),
        ("raw_small_post_good", 7.5e-5, True),
        ("raw_budgeted_good", 1.5e-4, True),
    ]
    scales = [0.5, 0.75, 1.0, 1.5, 2.0]
    for safe in SAFE_SOURCES:
        safe_path = OUT / safe
        if not safe_path.exists():
            continue
        safe_df = read_submission(safe_path)
        safe_pred = safe_df[TARGETS].to_numpy(dtype=np.float64)
        for probe in probes:
            probe_pred = read_submission(OUT / probe)[TARGETS].to_numpy(dtype=np.float64)
            direct_base = read_submission(direct_base_for(probe))[TARGETS].to_numpy(dtype=np.float64)
            residual = logit(probe_pred) - logit(direct_base)
            for scale in scales:
                proposed = clip(sigmoid(logit(safe_pred) + scale * residual))
                raw_delta = ce_delta(raw_q, proposed, safe_pred)
                post_delta = ce_delta(posterior_q, proposed, safe_pred)
                for gate_name, raw_limit, require_post_good in gate_specs:
                    keep = raw_delta <= raw_limit
                    if require_post_good:
                        keep &= post_delta < 0
                    if keep.mean() < 0.02:
                        continue
                    cand = safe_pred.copy()
                    cand[keep] = proposed[keep]
                    # The cell gate can be too sparse. Add a very small global residual
                    # on top of the safe cells for rules with strict raw filters.
                    if gate_name == "raw_nonpos_post_good":
                        cand = mix_logits(cand, safe_pred, 0.0)
                    tag = stable_tag(safe + probe + str(scale) + gate_name)
                    name = f"submission_hiddenblock_seqmotif_cellgate_{tag}.csv"
                    out = safe_df.copy()
                    out[TARGETS] = cand
                    out.to_csv(OUT / name, index=False)
                    saved.append(name)
                    records.append(
                        {
                            "file": name,
                            "safe_source": safe.removeprefix("submission_hiddenblock_").removesuffix(".csv")[:64],
                            "probe_source": probe.removeprefix("submission_hiddenblock_rateprobe_").removesuffix(".csv")[:80],
                            "scale": scale,
                            "gate": gate_name,
                            "kept_cell_frac": float(keep.mean()),
                            "kept_targets": ",".join(
                                target for j, target in enumerate(TARGETS) if keep[:, j].mean() > 0.01
                            ),
                            "pre_gate_raw_delta": float(raw_delta.mean()),
                            "pre_gate_posterior_delta": float(post_delta.mean()),
                            "gated_raw_delta": float(ce_delta(raw_q, cand, safe_pred).mean()),
                            "gated_posterior_delta": float(ce_delta(posterior_q, cand, safe_pred).mean()),
                            "mean_abs_move_vs_safe": float(np.abs(cand - safe_pred).mean()),
                        }
                    )
    if not records:
        return pd.DataFrame()
    meta = pd.DataFrame(records)
    proxy = public_proxy_scores(saved)
    out = proxy.merge(meta, on="file", how="left")
    out = out.sort_values(
        ["delta_vs_raw05_rawaxis", "posterior_expected_public_vs_anchor", "gated_posterior_delta"]
    )
    out.to_csv(OUT / "hidden_block_sequence_motif_cellgate_scores.csv", index=False)
    out[out["delta_vs_raw05_rawaxis"].le(0.0)].to_csv(
        OUT / "hidden_block_sequence_motif_cellgate_safe_scores.csv", index=False
    )
    return out


def write_report(target_df: pd.DataFrame, block_df: pd.DataFrame, scores: pd.DataFrame) -> None:
    safe = scores[scores["delta_vs_raw05_rawaxis"].le(0.0)].copy() if not scores.empty else pd.DataFrame()
    lines = [
        "# Hidden Block Sequence Motif Axis Decomposition",
        "",
        "This decomposes why sequence-motif block-rate probes work on pseudo-hidden blocks but hurt the raw05 public axis.",
        "",
        "## Direct probe target decomposition",
        "",
        "```csv",
        target_df.sort_values(["raw_delta", "posterior_delta"]).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Worst raw-axis conflicting block-target cells",
        "",
        "```csv",
        block_df.sort_values("raw_delta", ascending=False).head(40).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Best posterior-friendly block-target cells",
        "",
        "```csv",
        block_df.sort_values("posterior_delta").head(40).round(10).to_csv(index=False).strip(),
        "```",
    ]
    if not scores.empty:
        lines.extend(
            [
                "",
                "## Cell-gated candidate proxy scores",
                "",
                "```csv",
                scores.head(40).round(10).to_csv(index=False).strip(),
                "```",
                "",
                "## Raw-axis-safe cell-gated candidates",
                "",
                "```csv",
                safe.head(40).round(10).to_csv(index=False).strip(),
                "```",
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A negative raw_delta means the motif move is compatible with the raw05 public axis; positive means conflict.",
            "- A negative posterior_delta means the motif move is compatible with the six-public-feedback posterior.",
            "- The useful region is raw_delta <= 0 and posterior_delta < 0. Direct motif probes contain many posterior-good but raw-bad cells, which explains the conflict.",
        ]
    )
    (OUT / "hidden_block_sequence_motif_axis_decompose_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    raw_q, posterior_q = latent_qs()
    meta = row_metadata()
    target_parts = []
    block_parts = []
    for probe in direct_probe_sources():
        t, b = decompose_direct_probe(probe, raw_q, posterior_q, meta)
        target_parts.append(t)
        block_parts.append(b)
    target_df = pd.concat(target_parts, ignore_index=True)
    block_df = pd.concat(block_parts, ignore_index=True)
    target_df.to_csv(OUT / "hidden_block_sequence_motif_axis_target_decomposition.csv", index=False)
    block_df.to_csv(OUT / "hidden_block_sequence_motif_axis_block_decomposition.csv", index=False)
    scores = make_cell_gated_candidates(raw_q, posterior_q)
    write_report(target_df, block_df, scores)
    print("[seqmotif axis] direct probes", len(direct_probe_sources()))
    print(target_df.groupby("target")[["raw_delta", "posterior_delta", "conflict_cell_frac", "synergy_cell_frac"]].mean().round(10).to_string())
    if not scores.empty:
        safe = scores[scores["delta_vs_raw05_rawaxis"].le(0)]
        print("[seqmotif cellgate] candidates", len(scores), "safe", len(safe))
        print(safe.head(30).round(10).to_string(index=False))


if __name__ == "__main__":
    main()
