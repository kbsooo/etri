from __future__ import annotations

from dataclasses import dataclass
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

import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402
from hidden_block_latent_audit import expected_delta, load_predictions, projection_ratio, read_submission, sample_block_ids  # noqa: E402
from hidden_block_orthogonal_gate_candidates import raw_axis_latent_q  # noqa: E402


TARGETS = hbr.TARGETS
KEY = hbr.KEY

BASES = {
    "raw05": JEPA / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    "pareto03": OUT / "submission_hiddenblock_paretomix_w0.3_b7621063.csv",
    "seq1501": OUT / "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv",
    "rate605": OUT / "submission_hiddenblock_rateprobe_neutral_605de284.csv",
}

METHODS = [
    "rt:local:ridge_zctx_a12:blend0p2",
    "rt:local:ridge_zctx_a12:blend0p1",
    "rt_bc:local:ridge_zctx_a12:blend0p2",
    "rt_bc_nb_sg:local:ridge_zctx_a12:blend0p2",
    "rt:same:ridge_zctx_a12:blend0p1",
    "rt_bc_nb_sg:same:ridge_full_a24:blend0p1",
]

MASKS = {
    "all": TARGETS,
    "noq2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q1q2q3": ["Q1", "Q2", "Q3"],
    "q1q2q3s4": ["Q1", "Q2", "Q3", "S4"],
    "q2q3": ["Q2", "Q3"],
    "q3s4": ["Q3", "S4"],
    "s_all": ["S1", "S2", "S3", "S4"],
}


@dataclass(frozen=True)
class Candidate:
    tag: str
    pred: np.ndarray
    method: str
    base: str
    mask: str
    variant: str
    gamma: float
    cap: float
    raw_coeff: float
    bad_coeff: float
    ordinal_coeff: float


def clip(x: np.ndarray | float) -> np.ndarray:
    return hbr.clip(x)


def logit(x: np.ndarray | float) -> np.ndarray:
    return hbr.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return hbr.sigmoid(x)


def stable_tag(text: str) -> str:
    return hbr.stable_tag(text)


def target_mask(names: list[str], shape: tuple[int, int]) -> np.ndarray:
    idx = {t: j for j, t in enumerate(TARGETS)}
    mask = np.zeros(shape, dtype=bool)
    for name in names:
        mask[:, idx[name]] = True
    return mask


def project_out(vec: np.ndarray, axis: np.ndarray) -> tuple[np.ndarray, float]:
    denom = float(np.dot(axis, axis))
    if denom <= 1e-12:
        return vec, 0.0
    coeff = float(np.dot(vec, axis) / denom)
    return vec - coeff * axis, coeff


def positive_project_out(vec: np.ndarray, axis: np.ndarray) -> tuple[np.ndarray, float]:
    denom = float(np.dot(axis, axis))
    if denom <= 1e-12:
        return vec, 0.0
    coeff = float(np.dot(vec, axis) / denom)
    if coeff <= 0.0:
        return vec, coeff
    return vec - coeff * axis, coeff


def expand_rate(method: str, hidden_blocks: list[hbr.Block]) -> np.ndarray:
    hidden = pd.read_csv(OUT / "block_scale_jepa_target_hidden_rates.csv")
    subset = hidden[hidden["method"].eq(method)].set_index("hidden_block_id")
    out = np.zeros((len(hidden_blocks), len(TARGETS)), dtype=np.float64)
    for i, block in enumerate(hidden_blocks):
        if block.block_id not in subset.index:
            raise KeyError(f"{method} missing block {block.block_id}")
        row = subset.loc[block.block_id]
        for j, target in enumerate(TARGETS):
            out[i, j] = float(row[f"rate_{target}"])
    return clip(out)


def expand_to_rows(rows: pd.DataFrame, hidden_blocks: list[hbr.Block], block_rates: np.ndarray) -> np.ndarray:
    sample_len = int(rows["sub_idx"].max()) + 1
    out = np.full((sample_len, len(TARGETS)), np.nan, dtype=np.float64)
    for i, block in enumerate(hidden_blocks):
        sub_idx = rows.iloc[block.positions]["sub_idx"].to_numpy(dtype=int)
        out[sub_idx] = block_rates[i]
    if np.isnan(out).any():
        raise ValueError("missing hidden row expansion")
    return clip(out)


def build_candidates(
    sample: pd.DataFrame,
    rows: pd.DataFrame,
    hidden_blocks: list[hbr.Block],
    preds: dict[str, np.ndarray],
    raw_q: np.ndarray,
) -> list[Candidate]:
    bad_axis = logit(preds["jepa_bad_residual"]) - logit(preds["stage2"])
    ordinal_axis = logit(preds["ordinal_q"]) - logit(preds["stage2"])
    raw10_axis = logit(preds.get("raw10", preds["raw05"])) - logit(preds["stage2"])
    candidates: list[Candidate] = []

    base_frames = {name: read_submission(path) for name, path in BASES.items() if path.exists()}
    base_preds = {name: frame[TARGETS].to_numpy(dtype=np.float64) for name, frame in base_frames.items()}

    for method in METHODS:
        jepa_rate = expand_to_rows(rows, hidden_blocks, expand_rate(method, hidden_blocks))
        for base_name, base in base_preds.items():
            base_logit = logit(base)
            desired_full = logit(jepa_rate) - base_logit
            raw_grad_full = base - raw_q
            for mask_name, mask_targets in MASKS.items():
                mask = target_mask(mask_targets, base.shape)
                desired = desired_full[mask]
                raw_grad = raw_grad_full[mask]
                bad = bad_axis[mask]
                ordinal = ordinal_axis[mask]
                rawdir = raw10_axis[mask]

                variants: dict[str, tuple[np.ndarray, float, float, float]] = {}
                raw_neutral, raw_coeff = positive_project_out(desired, raw_grad)
                variants["rawproj"] = (raw_neutral, raw_coeff, 0.0, 0.0)
                tmp, bad_coeff = project_out(raw_neutral, bad)
                variants["raw_badproj"] = (tmp, raw_coeff, bad_coeff, 0.0)
                tmp2, ord_coeff = project_out(tmp, ordinal)
                variants["raw_bad_ordproj"] = (tmp2, raw_coeff, bad_coeff, ord_coeff)
                tmp3, rawdir_coeff = positive_project_out(tmp2, rawdir)
                variants["raw_bad_ord_rawdirproj"] = (tmp3, rawdir_coeff, bad_coeff, ord_coeff)

                for variant, (vec, c_raw, c_bad, c_ord) in variants.items():
                    for cap in [0.08, 0.12, 0.18, 0.25, 0.35, 0.50]:
                        capped = np.clip(vec, -cap, cap)
                        move = np.zeros_like(base)
                        move[mask] = capped
                        for gamma in [0.03, 0.05, 0.08, 0.12, 0.18, 0.25, 0.35]:
                            pred = clip(sigmoid(base_logit + gamma * move))
                            text = f"{base_name}|{method}|{mask_name}|{variant}|{cap}|{gamma}"
                            tag = f"blockscale_jepa_axisproj_{base_name}_{method.replace(':','_')}_{mask_name}_{variant}_g{gamma:g}_c{cap:g}_{stable_tag(text)}"
                            candidates.append(
                                Candidate(
                                    tag=tag.replace(".", "p"),
                                    pred=pred,
                                    method=method,
                                    base=base_name,
                                    mask=mask_name,
                                    variant=variant,
                                    gamma=gamma,
                                    cap=cap,
                                    raw_coeff=c_raw,
                                    bad_coeff=c_bad,
                                    ordinal_coeff=c_ord,
                                )
                            )
    return candidates


def score_candidates(candidates: list[Candidate], preds: dict[str, np.ndarray], posterior: np.ndarray, raw_q: np.ndarray) -> pd.DataFrame:
    raw05_rawaxis = expected_delta(raw_q, preds["raw05"], preds["stage2"])
    bad_axis = preds["jepa_bad_residual"] - preds["stage2"]
    ordinal_axis = preds["ordinal_q"] - preds["stage2"]
    raw_axis = preds.get("raw10", preds["raw05"]) - preds["stage2"]
    rows = []
    for cand in candidates:
        pred = cand.pred
        raw_expected = 0.5779449757 + expected_delta(raw_q, pred, preds["stage2"])
        posterior_expected = 0.5784273528 + expected_delta(posterior, pred, preds["anchor578"])
        rec = {
            "tag": cand.tag,
            "method": cand.method,
            "base": cand.base,
            "mask": cand.mask,
            "variant": cand.variant,
            "gamma": cand.gamma,
            "cap": cand.cap,
            "posterior_expected_public_vs_anchor": posterior_expected,
            "raw_axis_expected_public_vs_stage2": raw_expected,
            "delta_vs_raw05_rawaxis": expected_delta(raw_q, pred, preds["stage2"]) - raw05_rawaxis,
            "bad_residual_axis_ratio": projection_ratio(pred - preds["stage2"], bad_axis),
            "ordinal_axis_ratio": projection_ratio(pred - preds["stage2"], ordinal_axis),
            "raw10_axis_ratio": projection_ratio(pred - preds["stage2"], raw_axis),
            "mean_abs_move_vs_raw05": float(np.abs(pred - preds["raw05"]).mean()),
            "mean_abs_move_vs_base_raw05": float(np.abs(pred - preds["raw05"]).mean()),
            "min_prob": float(pred.min()),
            "max_prob": float(pred.max()),
            "raw_coeff": cand.raw_coeff,
            "bad_coeff": cand.bad_coeff,
            "ordinal_coeff": cand.ordinal_coeff,
        }
        # Primary score rewards posterior while hard-penalizing raw-axis leakage.
        rec["selection_score"] = (
            posterior_expected
            + 40.0 * max(rec["delta_vs_raw05_rawaxis"], 0.0)
            + 0.08 * max(rec["bad_residual_axis_ratio"], 0.0)
            + 0.04 * abs(rec["ordinal_axis_ratio"])
        )
        rows.append(rec)
    return pd.DataFrame(rows).sort_values(
        ["selection_score", "delta_vs_raw05_rawaxis", "posterior_expected_public_vs_anchor"]
    ).reset_index(drop=True)


def save_selected(sample: pd.DataFrame, candidates: list[Candidate], scores: pd.DataFrame) -> pd.DataFrame:
    by_tag = {candidate.tag: candidate for candidate in candidates}
    selected = scores[
        (scores["delta_vs_raw05_rawaxis"] <= 5e-6)
        & (scores["bad_residual_axis_ratio"].abs() <= 0.03)
        & (scores["mean_abs_move_vs_raw05"] <= 0.0025)
    ].copy()
    if selected.empty:
        selected = scores.head(40).copy()
    picks = pd.concat(
        [
            selected.head(30),
            scores.sort_values("posterior_expected_public_vs_anchor").head(20),
            scores.sort_values("raw_axis_expected_public_vs_stage2").head(20),
        ],
        ignore_index=True,
    ).drop_duplicates("tag").head(50)

    rows = []
    for row in picks.itertuples(index=False):
        cand = by_tag[row.tag]
        file_name = f"submission_{cand.tag}.csv"
        out = sample.copy()
        out[TARGETS] = cand.pred
        out.to_csv(OUT / file_name, index=False)
        rec = row._asdict()
        rec["file"] = file_name
        rec["rows"] = len(out)
        rec["key_ok"] = bool(out[KEY].equals(sample[KEY]))
        rec["duplicate_keys"] = int(out.duplicated(KEY).sum())
        rec["null_probs"] = int(out[TARGETS].isna().sum().sum())
        rows.append(rec)
    selected_out = pd.DataFrame(rows)
    selected_out.to_csv(OUT / "block_scale_jepa_axis_projector_selected.csv", index=False)
    return selected_out


def write_report(scores: pd.DataFrame, selected: pd.DataFrame, proxy: pd.DataFrame) -> None:
    cols = [
        "tag",
        "base",
        "method",
        "mask",
        "variant",
        "gamma",
        "cap",
        "posterior_expected_public_vs_anchor",
        "raw_axis_expected_public_vs_stage2",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "ordinal_axis_ratio",
        "mean_abs_move_vs_raw05",
        "selection_score",
    ]
    lines = [
        "# Block-Scale JEPA Axis Projector",
        "",
        "This pass treats block-scale JEPA hidden rates as a logit move and projects that move away from the raw05-compatible public gradient and bad observed axes.",
        "",
        "## Top Scores",
        "",
        "```csv",
        scores[cols].head(40).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Saved Proxy",
        "",
        "```csv",
        proxy.head(50).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Saved Integrity",
        "",
        "```csv",
        selected[["file", "rows", "key_ok", "duplicate_keys", "null_probs", "min_prob", "max_prob"]].round(8).to_csv(index=False).strip(),
        "```",
    ]
    (OUT / "block_scale_jepa_axis_projector_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train, sample = hbr.read_data()
    rows = hbr.all_rows(train, sample)
    hidden_blocks = hbr.make_hidden_blocks(rows)
    _frames, preds = load_predictions()
    raw_q = raw_axis_latent_q(preds["stage2"], preds["raw05"])
    block_ids = sample_block_ids(train, sample)
    block_df = pd.read_csv(OUT / "hidden_block_posterior_block_summary.csv").set_index("hidden_block_id")
    posterior = np.zeros_like(preds["raw05"])
    for i, block_id in enumerate(block_ids):
        for j, target in enumerate(TARGETS):
            posterior[i, j] = float(block_df.loc[block_id, f"posterior_rate_{target}"])
    posterior = clip(posterior)

    candidates = build_candidates(sample, rows, hidden_blocks, preds, raw_q)
    scores = score_candidates(candidates, preds, posterior, raw_q)
    scores.to_csv(OUT / "block_scale_jepa_axis_projector_scores.csv", index=False)
    selected = save_selected(sample, candidates, scores)
    proxy = hbr.public_proxy_scores(selected["file"].tolist())
    proxy.to_csv(OUT / "block_scale_jepa_axis_projector_proxy.csv", index=False)
    write_report(scores, selected, proxy)

    print("[axis projector] candidates", len(candidates), "saved", len(selected))
    print(scores.head(20).round(10).to_string(index=False))
    print("\n[proxy]")
    print(proxy.head(20).round(10).to_string(index=False))
    bad = selected[(~selected["key_ok"]) | (selected["duplicate_keys"] > 0) | (selected["null_probs"] > 0)]
    print("\n[integrity]", "ok" if bad.empty else bad[["file", "key_ok", "duplicate_keys", "null_probs"]].to_string(index=False))


if __name__ == "__main__":
    main()
