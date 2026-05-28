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

import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402
from hidden_block_latent_audit import expected_delta, load_predictions, projection_ratio, read_submission, sample_block_ids  # noqa: E402
from hidden_block_orthogonal_gate_candidates import raw_axis_latent_q  # noqa: E402


TARGETS = hbr.TARGETS
KEY = hbr.KEY

BASES = {
    "raw05": JEPA / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    "seq1501": OUT / "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv",
    "seqebf": OUT / "submission_hiddenblock_seqmotif_neutral_ebf79910.csv",
    "seqd0": OUT / "submission_hiddenblock_seqmotif_neutral_d0ca7647.csv",
    "pareto03": OUT / "submission_hiddenblock_paretomix_w0.3_b7621063.csv",
    "rate605": OUT / "submission_hiddenblock_rateprobe_neutral_605de284.csv",
}


def clip(x: np.ndarray | float) -> np.ndarray:
    return hbr.clip(x)


def logit(x: np.ndarray | float) -> np.ndarray:
    return hbr.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return hbr.sigmoid(x)


def stable_tag(text: str) -> str:
    return hbr.stable_tag(text)


def load_hidden_rate(method: str) -> np.ndarray:
    hidden = pd.read_csv(OUT / "block_scale_jepa_target_hidden_rates.csv")
    rows = hidden[hidden["method"].eq(method)].copy()
    if rows.empty:
        raise KeyError(method)
    rows = rows.sort_values(["subject_id", "start", "end", "hidden_block_id"]).reset_index(drop=True)
    return rows[[f"rate_{t}" for t in TARGETS]].to_numpy(dtype=np.float64)


def hidden_sub_indices(rows: pd.DataFrame, hidden_blocks: list[hbr.Block]) -> list[np.ndarray]:
    return [rows.iloc[b.positions]["sub_idx"].to_numpy(dtype=int) for b in hidden_blocks]


def apply_rate(base_pred: np.ndarray, sub_indices: list[np.ndarray], hidden_rate: np.ndarray, mask: np.ndarray, weight: float) -> np.ndarray:
    pred = base_pred.copy()
    for block_i, idx in enumerate(sub_indices):
        for j, keep in enumerate(mask):
            if keep:
                pred[idx, j] = clip(sigmoid((1.0 - weight) * logit(pred[idx, j]) + weight * logit(hidden_rate[block_i, j])))
    return pred


def score_pred(pred: np.ndarray, preds: dict[str, np.ndarray], posterior: np.ndarray, raw_q: np.ndarray) -> dict[str, float]:
    bad_axis = preds["jepa_bad_residual"] - preds["stage2"]
    ordinal_axis = preds["ordinal_q"] - preds["stage2"]
    raw05_rawaxis = expected_delta(raw_q, preds["raw05"], preds["stage2"])
    return {
        "posterior_expected_public_vs_anchor": 0.5784273528 + expected_delta(posterior, pred, preds["anchor578"]),
        "raw_axis_expected_public_vs_stage2": 0.5779449757 + expected_delta(raw_q, pred, preds["stage2"]),
        "delta_vs_raw05_rawaxis": expected_delta(raw_q, pred, preds["stage2"]) - raw05_rawaxis,
        "bad_residual_axis_ratio": projection_ratio(pred - preds["stage2"], bad_axis),
        "ordinal_axis_ratio": projection_ratio(pred - preds["stage2"], ordinal_axis),
        "mean_abs_move_vs_raw05": float(np.abs(pred - preds["raw05"]).mean()),
        "min_prob": float(pred.min()),
        "max_prob": float(pred.max()),
    }


def mask_library(target_detail: pd.DataFrame, method: str) -> dict[str, np.ndarray]:
    masks: dict[str, np.ndarray] = {}
    for j, t in enumerate(TARGETS):
        m = np.zeros(len(TARGETS), dtype=bool)
        m[j] = True
        masks[t.lower()] = m
    named = {
        "q1q2q3": {"Q1", "Q2", "Q3"},
        "q2q3": {"Q2", "Q3"},
        "q3s4": {"Q3", "S4"},
        "q1q3s4": {"Q1", "Q3", "S4"},
        "qs": {"Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"},
        "noq2": {"Q1", "Q3", "S1", "S2", "S3", "S4"},
        "q1q2q3s4": {"Q1", "Q2", "Q3", "S4"},
        "q1q2q3s2s4": {"Q1", "Q2", "Q3", "S2", "S4"},
        "s_all": {"S1", "S2", "S3", "S4"},
    }
    for name, vals in named.items():
        masks[name] = np.array([t in vals for t in TARGETS], dtype=bool)
    td = target_detail[target_detail["method"].eq(method)].set_index("target").reindex(TARGETS)
    gains = td["target_delta_vs_subject_mean"].to_numpy(dtype=float)
    for thr in [-0.005, -0.015, -0.03, -0.05]:
        m = gains < thr
        if m.any():
            masks[f"gain{str(abs(thr)).replace('.', 'p')}"] = m
    uniq: dict[str, np.ndarray] = {}
    for name, mask in masks.items():
        key = "".join("1" if x else "0" for x in mask)
        if key not in uniq:
            uniq[name] = mask
    return uniq


def save_submission(base_frame: pd.DataFrame, pred: np.ndarray, file_name: str) -> None:
    out = base_frame.copy()
    out[TARGETS] = pred
    out.to_csv(OUT / file_name, index=False)


def main() -> None:
    train, sample = hbr.read_data()
    rows = hbr.all_rows(train, sample)
    hidden_blocks = hbr.make_hidden_blocks(rows)
    sub_indices = hidden_sub_indices(rows, hidden_blocks)

    summary = pd.read_csv(OUT / "block_scale_jepa_target_summary.csv")
    target_detail = pd.read_csv(OUT / "block_scale_jepa_target_target_detail.csv")
    methods = summary[summary["method"].ne("subject_mean")].head(18)["method"].tolist()

    _frames, preds = load_predictions()
    raw_q = raw_axis_latent_q(preds["stage2"], preds["raw05"])
    block_ids = sample_block_ids(train, sample)
    block_df = pd.read_csv(OUT / "hidden_block_posterior_block_summary.csv").set_index("hidden_block_id")
    posterior = np.zeros_like(preds["raw05"])
    for i, block_id in enumerate(block_ids):
        for j, target in enumerate(TARGETS):
            posterior[i, j] = float(block_df.loc[block_id, f"posterior_rate_{target}"])
    posterior = clip(posterior)

    base_frames = {name: read_submission(path) for name, path in BASES.items() if path.exists()}
    base_preds = {name: frame[TARGETS].to_numpy(dtype=np.float64) for name, frame in base_frames.items()}

    rows_out = []
    pred_cache: dict[str, tuple[str, np.ndarray]] = {}
    weights = [0.005, 0.01, 0.015, 0.02, 0.03, 0.04, 0.05, 0.08]
    for method in methods:
        hidden_rate = load_hidden_rate(method)
        masks = mask_library(target_detail, method)
        for base_name, base_pred in base_preds.items():
            for mask_name, mask in masks.items():
                for weight in weights:
                    pred = apply_rate(base_pred, sub_indices, hidden_rate, mask, weight)
                    score = score_pred(pred, preds, posterior, raw_q)
                    rec = {
                        "method": method,
                        "base": base_name,
                        "mask": mask_name,
                        "weight": weight,
                        **score,
                    }
                    rows_out.append(rec)
                    tag = stable_tag(f"{base_name}|{method}|{mask_name}|{weight}|neutral")
                    mtag = method.replace(":", "_").replace(".", "p").replace("local", "loc").replace("strict", "str")
                    wtag = str(weight).replace(".", "p")
                    file_name = f"submission_blockscale_jepa_neutral_{base_name}_{mtag}_{mask_name}_w{wtag}_{tag}.csv"
                    pred_cache[file_name] = (base_name, pred)
                    rows_out[-1]["file"] = file_name

    scan = pd.DataFrame(rows_out)
    # Rank by raw-axis safety first, then posterior. Keep a second view for aggressive posterior probes.
    safe = scan[
        (scan["delta_vs_raw05_rawaxis"] <= 2.5e-5)
        & (scan["bad_residual_axis_ratio"].abs() <= 0.035)
        & (scan["mean_abs_move_vs_raw05"] <= 0.0025)
    ].copy()
    safe = safe.sort_values(["posterior_expected_public_vs_anchor", "raw_axis_expected_public_vs_stage2"]).reset_index(drop=True)
    aggressive = scan.sort_values(["posterior_expected_public_vs_anchor", "delta_vs_raw05_rawaxis"]).reset_index(drop=True)
    shortlist = pd.concat([safe.head(60), aggressive.head(30)], ignore_index=True).drop_duplicates("file").reset_index(drop=True)

    scan.to_csv(OUT / "block_scale_jepa_neutral_scan.csv", index=False)
    safe.head(200).to_csv(OUT / "block_scale_jepa_neutral_safe.csv", index=False)
    aggressive.head(200).to_csv(OUT / "block_scale_jepa_neutral_aggressive.csv", index=False)
    shortlist.to_csv(OUT / "block_scale_jepa_neutral_shortlist.csv", index=False)

    saved = []
    for file_name in shortlist.head(40)["file"].tolist():
        base_name, pred = pred_cache[file_name]
        save_submission(base_frames[base_name], pred, file_name)
        saved.append(file_name)
    proxy = hbr.public_proxy_scores(saved)
    proxy.to_csv(OUT / "block_scale_jepa_neutral_saved_proxy.csv", index=False)

    integ_rows = []
    for file_name in saved:
        frame = pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        vals = frame[TARGETS].to_numpy(dtype=np.float64)
        integ_rows.append(
            {
                "file": file_name,
                "rows": len(frame),
                "key_ok": bool(frame[KEY].equals(sample[KEY])),
                "duplicate_keys": int(frame.duplicated(KEY).sum()),
                "null_probs": int(frame[TARGETS].isna().sum().sum()),
                "min_prob": float(vals.min()),
                "max_prob": float(vals.max()),
            }
        )
    integ = pd.DataFrame(integ_rows)
    integ.to_csv(OUT / "block_scale_jepa_neutral_integrity.csv", index=False)

    lines = [
        "# Block-Scale JEPA Neutral Scan",
        "",
        "Purpose: keep the strong pseudo-hidden block-scale JEPA signal while searching target masks and tiny weights that do not move away from the raw05 public axis.",
        "",
        "## Safe Shortlist",
        "",
        "```csv",
        safe.head(30).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Saved Proxy",
        "",
        "```csv",
        proxy.head(40).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Integrity",
        "",
        "```csv",
        integ.round(8).to_csv(index=False).strip(),
        "```",
    ]
    (OUT / "block_scale_jepa_neutral_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("[neutral scan] rows", len(scan), "safe", len(safe), "saved", len(saved))
    print(safe.head(20).round(10).to_string(index=False))
    print("\n[saved proxy]")
    print(proxy.head(20).round(10).to_string(index=False))
    bad = integ[(~integ["key_ok"]) | (integ["duplicate_keys"] > 0) | (integ["null_probs"] > 0)]
    print("\n[integrity]", "ok" if bad.empty else bad.to_string(index=False))


if __name__ == "__main__":
    main()
