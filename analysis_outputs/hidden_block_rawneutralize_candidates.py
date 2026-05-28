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

from hidden_block_latent_audit import TARGETS, KEY, clip, load_predictions, logit, read_submission, sigmoid  # noqa: E402
from hidden_block_orthogonal_gate_candidates import (  # noqa: E402
    Candidate,
    raw_axis_latent_q,
    save_selected,
    score_candidates,
    stable_tag,
    target_mask,
)


def candidate_source_files() -> pd.DataFrame:
    selected = pd.read_csv(OUT / "hidden_block_orthogonal_gate_selected.csv")
    scenario_path = OUT / "public_posterior_scenario_robustness_summary.csv"
    if scenario_path.exists():
        scenario = pd.read_csv(scenario_path)
        scenario = scenario[scenario["file"].astype(str).str.contains("hiddenblock", na=False)].copy()
        selected = selected.merge(
            scenario[["file", "scenario_robust_score", "mean_expected", "mean_regret"]],
            on="file",
            how="left",
        )
    else:
        selected["scenario_robust_score"] = np.nan
    keep = selected[
        selected["kind"].isin(["orthgate", "orthraw", "orth"])
        & selected["posterior_expected_public_vs_anchor"].lt(0.5769)
        & selected["delta_vs_raw05_rawaxis"].lt(8e-5)
    ].copy()
    keep = keep.sort_values(
        ["scenario_robust_score", "raw_axis_expected_public_vs_stage2", "posterior_expected_public_vs_anchor"],
        na_position="last",
    )
    return keep.head(12).reset_index(drop=True)


def make_scope_mask(scope: str, targets_tag: str, n_rows: int) -> np.ndarray:
    if scope == "all":
        return np.ones((n_rows, len(TARGETS)), dtype=bool)
    if scope == "noq2":
        return target_mask(["Q1", "Q3", "S1", "S2", "S3", "S4"], n_rows)
    if scope == "q3s":
        return target_mask(["Q3", "S1", "S2", "S3", "S4"], n_rows)
    if scope == "same":
        mapping = {
            "q3s134": ["Q3", "S1", "S3", "S4"],
            "s134": ["S1", "S3", "S4"],
            "s_all": ["S1", "S2", "S3", "S4"],
            "noq2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
            "q3s": ["Q3", "S1", "S2", "S3", "S4"],
        }
        return target_mask(mapping.get(targets_tag, TARGETS), n_rows)
    raise ValueError(f"unknown scope: {scope}")


def make_candidates(preds: dict[str, np.ndarray], sources: pd.DataFrame) -> list[Candidate]:
    raw_move = logit(preds["raw10"]) - logit(preds["raw05"])
    candidates: list[Candidate] = []
    for row in sources.itertuples(index=False):
        base_pred = read_submission(OUT / row.file)[TARGETS].to_numpy(dtype=np.float64)
        for scope in ["same", "q3s", "noq2", "all"]:
            mask = make_scope_mask(scope, str(row.targets), base_pred.shape[0])
            move = np.zeros_like(base_pred)
            move[mask] = raw_move[mask]
            for k in [0.20, 0.35, 0.50, 0.70, 0.90, 1.10, 1.35]:
                pred = clip(sigmoid(logit(base_pred) + k * move))
                text = f"rawneutral|{row.file}|{scope}|{k}"
                candidates.append(
                    Candidate(
                        tag=f"hiddenblock_rawneutral_{row.kind}_{row.targets}_{scope}_k{k:g}_{stable_tag(text)}",
                        pred=pred,
                        kind="rawneutral",
                        targets=f"{row.targets}_{scope}",
                        params={
                            "scale": k,
                            "gamma": float(getattr(row, "gamma", np.nan)),
                            "cap": float(getattr(row, "cap", np.nan)),
                            "source_raw_axis_delta": float(row.delta_vs_raw05_rawaxis),
                        },
                    )
                )
    return candidates


def write_report(sources: pd.DataFrame, scores: pd.DataFrame, selected: pd.DataFrame) -> None:
    top_cols = [
        "tag",
        "targets",
        "posterior_expected_public_vs_anchor",
        "raw_axis_expected_public_vs_stage2",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "ordinal_axis_ratio",
        "mean_abs_move_vs_raw05",
        "selection_score",
    ]
    source_cols = [
        "file",
        "kind",
        "targets",
        "posterior_expected_public_vs_anchor",
        "raw_axis_expected_public_vs_stage2",
        "delta_vs_raw05_rawaxis",
        "scenario_robust_score",
    ]
    lines = [
        "# Hidden Block Raw-Neutralized Candidates",
        "",
        "Orthogonal posterior candidates with good synthetic robustness were slightly worse than raw05 on the raw-axis latent. This pass adds a thin raw10 rescue component to make that axis neutral or positive.",
        "",
        "## Source Candidates",
        "",
        "```csv",
        sources[source_cols].round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Top Raw-Neutralized Candidates",
        "",
        "```csv",
        scores[top_cols].head(40).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Saved Candidates",
        "",
        "```csv",
        selected[["file"] + top_cols[1:]].round(10).to_csv(index=False).strip(),
        "```",
    ]
    (OUT / "hidden_block_rawneutralize_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    _train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    frames, preds = load_predictions()
    raw_q = raw_axis_latent_q(preds["stage2"], preds["raw05"])
    posterior_block = pd.read_csv(OUT / "hidden_block_posterior_block_summary.csv")
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    from hidden_block_latent_audit import sample_block_ids

    block_ids = sample_block_ids(
        train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True),
        sample.sort_values(KEY).reset_index(drop=True),
    )
    lookup = posterior_block.set_index("hidden_block_id")
    posterior = np.zeros_like(preds["raw05"])
    for i, block_id in enumerate(block_ids):
        for j, target in enumerate(TARGETS):
            posterior[i, j] = float(lookup.loc[block_id, f"posterior_rate_{target}"])
    posterior = clip(posterior)

    sources = candidate_source_files()
    candidates = make_candidates(preds, sources)
    scores = score_candidates(preds, candidates, posterior, raw_q)
    safe_scores = scores[
        scores["delta_vs_raw05_rawaxis"].le(0.0)
        & scores["posterior_expected_public_vs_anchor"].le(0.5775263072)
        & scores["bad_residual_axis_ratio"].le(0.0045)
    ].copy()
    if safe_scores.empty:
        safe_scores = scores.head(48).copy()
    safe_scores.to_csv(OUT / "hidden_block_rawneutralize_scores.csv", index=False)
    selected = save_selected(frames["stage2"], candidates, safe_scores, n_per_kind=24)
    write_report(sources, safe_scores, selected)

    print("[hidden block raw-neutralize] generated", len(candidates), "candidates")
    print("[hidden block raw-neutralize] safe", len(safe_scores), "candidates")
    show_cols = [
        "file",
        "targets",
        "posterior_expected_public_vs_anchor",
        "raw_axis_expected_public_vs_stage2",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "ordinal_axis_ratio",
        "mean_abs_move_vs_raw05",
        "selection_score",
    ]
    print(selected[show_cols].head(30).round(10).to_string(index=False))


if __name__ == "__main__":
    main()
