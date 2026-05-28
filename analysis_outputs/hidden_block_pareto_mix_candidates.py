from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

from hidden_block_latent_audit import TARGETS, KEY, clip, load_predictions, logit, read_submission, sample_block_ids, sigmoid  # noqa: E402
from hidden_block_orthogonal_gate_candidates import Candidate, raw_axis_latent_q, save_selected, score_candidates, stable_tag  # noqa: E402


ROBUST_SOURCES = [
    "submission_hiddenblock_orthgate_noq2_g0.05_cap0.35_b7177075.csv",
    "submission_hiddenblock_orthgate_noq2_g0.05_cap0.5_63347cb5.csv",
    "submission_hiddenblock_orth_noq2_g0.035_cap0.5_739fa428.csv",
    "submission_hiddenblock_orthraw_noq2_g0.035_cap0.5_c0141407.csv",
    "submission_hiddenblock_orthgate_noq2_g0.075_cap0.35_20b55eb5.csv",
]

SAFE_SOURCES = [
    "submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv",
    "submission_hiddenblock_rawgate_s_all_s0.7_5ccfb1c6.csv",
    "submission_hiddenblock_rawgate_s_all_s0.9_89d7a9f5.csv",
    "submission_hiddenblock_rawgate_q3s_s1.1_2f560067.csv",
]


def expand_posterior(preds: dict[str, np.ndarray]) -> np.ndarray:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    block_ids = sample_block_ids(
        train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True),
        sample.sort_values(KEY).reset_index(drop=True),
    )
    block_df = pd.read_csv(OUT / "hidden_block_posterior_block_summary.csv").set_index("hidden_block_id")
    posterior = np.zeros_like(preds["raw05"])
    for i, block_id in enumerate(block_ids):
        for j, target in enumerate(TARGETS):
            posterior[i, j] = float(block_df.loc[block_id, f"posterior_rate_{target}"])
    return clip(posterior)


def make_candidates() -> list[Candidate]:
    candidates: list[Candidate] = []
    for robust in ROBUST_SOURCES:
        if not (OUT / robust).exists():
            continue
        robust_pred = read_submission(OUT / robust)[TARGETS].to_numpy(dtype=np.float64)
        for safe in SAFE_SOURCES:
            if not (OUT / safe).exists():
                continue
            safe_pred = read_submission(OUT / safe)[TARGETS].to_numpy(dtype=np.float64)
            for w_safe in [0.20, 0.30, 0.40, 0.50, 0.65, 0.80]:
                pred = clip(sigmoid((1.0 - w_safe) * logit(robust_pred) + w_safe * logit(safe_pred)))
                text = f"pareto|{robust}|{safe}|{w_safe}"
                robust_short = robust.removeprefix("submission_hiddenblock_").removesuffix(".csv")
                safe_short = safe.removeprefix("submission_hiddenblock_").removesuffix(".csv")
                candidates.append(
                    Candidate(
                        tag=f"hiddenblock_paretomix_w{w_safe:g}_{stable_tag(text)}",
                        pred=pred,
                        kind="paretomix",
                        targets="mixed",
                        params={
                            "scale": w_safe,
                            "gamma": np.nan,
                            "cap": np.nan,
                            "robust_source": robust_short[:42],
                            "safe_source": safe_short[:42],
                        },
                    )
                )
    return candidates


def write_report(scores: pd.DataFrame, selected: pd.DataFrame) -> None:
    cols = [
        "tag",
        "posterior_expected_public_vs_anchor",
        "raw_axis_expected_public_vs_stage2",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "ordinal_axis_ratio",
        "mean_abs_move_vs_raw05",
        "selection_score",
        "scale",
        "robust_source",
        "safe_source",
    ]
    lines = [
        "# Hidden Block Pareto Mix Candidates",
        "",
        "Mixes the best synthetic-robust orthogonal block posterior candidates with raw-axis-safe candidates in logit space.",
        "",
        "## Top Candidates",
        "",
        "```csv",
        scores[cols].head(40).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Saved Candidates",
        "",
        "```csv",
        selected[["file"] + cols[1:]].round(10).to_csv(index=False).strip(),
        "```",
    ]
    (OUT / "hidden_block_pareto_mix_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    frames, preds = load_predictions()
    posterior = expand_posterior(preds)
    raw_q = raw_axis_latent_q(preds["stage2"], preds["raw05"])
    candidates = make_candidates()
    scores = score_candidates(preds, candidates, posterior, raw_q)
    safe_scores = scores[
        scores["delta_vs_raw05_rawaxis"].le(0.0)
        & scores["posterior_expected_public_vs_anchor"].le(0.5775263072)
        & scores["bad_residual_axis_ratio"].le(0.0045)
    ].copy()
    if safe_scores.empty:
        safe_scores = scores.head(24).copy()
    safe_scores.to_csv(OUT / "hidden_block_pareto_mix_scores.csv", index=False)
    selected = save_selected(frames["stage2"], candidates, safe_scores, n_per_kind=24)
    write_report(safe_scores, selected)
    show_cols = [
        "file",
        "posterior_expected_public_vs_anchor",
        "raw_axis_expected_public_vs_stage2",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "ordinal_axis_ratio",
        "mean_abs_move_vs_raw05",
        "selection_score",
        "scale",
    ]
    print("[hidden block pareto mix] generated", len(candidates), "candidates")
    print("[hidden block pareto mix] safe", len(safe_scores), "candidates")
    print(selected[show_cols].head(30).round(10).to_string(index=False))


if __name__ == "__main__":
    main()
