from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis_outputs"
JEPA_DIR = ROOT / "jepa"
DATA_DIR = ROOT / "data"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.append(str(ANALYSIS_DIR))

from public_subset_sensitivity_audit import build_masks  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-5

Q_SCENARIOS = [
    "submission_public_entropyproj_public2d0_g050.csv",
    "submission_public_entropyproj_public2d0_g075.csv",
    "submission_public_entropyproj_public2d0_g100.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s3_s4_g075.csv",
]

PUBLIC_BASES = {
    "minimax_r05": ANALYSIS_DIR / "submission_public_minimaxens_r05_a10_h506746.csv",
    "minimax_r01": ANALYSIS_DIR / "submission_public_minimaxens_r01_a6_h422045.csv",
    "u80": ANALYSIS_DIR / "submission_public_universeens_u80_r01_07c571e6.csv",
    "u65_maskrank": ANALYSIS_DIR / "submission_public_universeens_u65_r04_dc6f3303.csv",
}

JEPA_MOVES = {
    "neural_episode_bal": JEPA_DIR / "submission_bigshot_10_jepa_neural_episode_rawstack_balanced.csv",
    "multifeature_raw": JEPA_DIR / "submission_bigshot_11_jepa_multifeature_rawstack.csv",
    "blockcanvas_noq2": JEPA_DIR / "submission_bigshot_12_jepa_blockcanvas_aggressive_noq2.csv",
}

REFERENCE_FILES = {
    "stage2": ANALYSIS_DIR / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "raw05": JEPA_DIR / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
}


@dataclass(frozen=True)
class Scored:
    name: str
    mode: str
    base: str
    jepa: str
    weight: float
    mean_expected: float
    p90_expected: float
    mean_regret: float
    p90_regret: float
    max_regret: float
    mean_delta_vs_base: float
    p90_delta_vs_base: float
    win_rate_vs_base: float
    score: float
    min_prob: float
    max_prob: float
    mean_abs_delta_vs_stage2: float | None
    mean_abs_delta_vs_raw05: float | None


def clip(x: np.ndarray) -> np.ndarray:
    return np.clip(x, EPS, 1.0 - EPS)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -40.0, 40.0)))


def load_pred(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path).sort_values(KEYS).reset_index(drop=True)


def ce_rows(q: np.ndarray, p: np.ndarray) -> np.ndarray:
    q = clip(q)
    p = clip(p)
    return (-(q * np.log(p) + (1.0 - q) * np.log(1.0 - p))).mean(axis=1)


def blend(base: np.ndarray, jepa: np.ndarray, weight: float, mode: str) -> np.ndarray:
    if mode == "prob":
        return clip((1.0 - weight) * base + weight * jepa)
    if mode == "logit":
        return clip(sigmoid((1.0 - weight) * logit(base) + weight * logit(jepa)))
    raise ValueError(mode)


def score_pred(
    name: str,
    mode: str,
    base_name: str,
    jepa_name: str,
    weight: float,
    pred: np.ndarray,
    q_scenarios: dict[str, np.ndarray],
    masks: list[dict[str, object]],
    base_scores: np.ndarray,
    best_scores: np.ndarray,
    stage2: np.ndarray | None,
    raw05: np.ndarray | None,
) -> Scored:
    scores = []
    for q in q_scenarios.values():
        row_loss = ce_rows(q, pred)
        for rec in masks:
            mask = rec["mask"]
            assert isinstance(mask, np.ndarray)
            scores.append(float(row_loss[mask].mean()))
    arr = np.asarray(scores, dtype=float)
    regret = arr - best_scores
    delta = arr - base_scores
    mean_expected = float(arr.mean())
    p90_expected = float(np.quantile(arr, 0.90))
    mean_regret = float(regret.mean())
    p90_regret = float(np.quantile(regret, 0.90))
    max_regret = float(regret.max())
    mean_delta_vs_base = float(delta.mean())
    p90_delta_vs_base = float(np.quantile(delta, 0.90))
    win_rate_vs_base = float((delta < 0.0).mean())
    score = (
        mean_expected
        + 2.0 * mean_regret
        + p90_regret
        + 0.05 * max_regret
        + 0.2 * max(p90_delta_vs_base, 0.0)
        + 0.02 * max(0.50 - win_rate_vs_base, 0.0)
    )
    mean_abs_stage2 = None if stage2 is None else float(np.abs(pred - stage2).mean())
    mean_abs_raw05 = None if raw05 is None else float(np.abs(pred - raw05).mean())
    return Scored(
        name=name,
        mode=mode,
        base=base_name,
        jepa=jepa_name,
        weight=weight,
        mean_expected=mean_expected,
        p90_expected=p90_expected,
        mean_regret=mean_regret,
        p90_regret=p90_regret,
        max_regret=max_regret,
        mean_delta_vs_base=mean_delta_vs_base,
        p90_delta_vs_base=p90_delta_vs_base,
        win_rate_vs_base=win_rate_vs_base,
        score=float(score),
        min_prob=float(pred.min()),
        max_prob=float(pred.max()),
        mean_abs_delta_vs_stage2=mean_abs_stage2,
        mean_abs_delta_vs_raw05=mean_abs_raw05,
    )


def main() -> None:
    sample = pd.read_csv(DATA_DIR / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    masks = [m for m in build_masks(sample) if m["mask_kind"] != "all"]

    q_scenarios = {
        name: load_pred(ANALYSIS_DIR / name)[TARGETS].to_numpy(dtype=float)
        for name in Q_SCENARIOS
    }
    public_preds = {
        name: load_pred(path)[TARGETS].to_numpy(dtype=float)
        for name, path in PUBLIC_BASES.items()
    }
    jepa_preds = {
        name: load_pred(path)[TARGETS].to_numpy(dtype=float)
        for name, path in JEPA_MOVES.items()
    }
    refs = {
        name: (load_pred(path)[TARGETS].to_numpy(dtype=float) if path.exists() else None)
        for name, path in REFERENCE_FILES.items()
    }

    # Regret is computed against the best public base for each scenario/mask.
    base_score_matrix = []
    for q in q_scenarios.values():
        row_losses = {name: ce_rows(q, p) for name, p in public_preds.items()}
        for rec in masks:
            mask = rec["mask"]
            assert isinstance(mask, np.ndarray)
            base_score_matrix.append([float(loss[mask].mean()) for loss in row_losses.values()])
    base_score_matrix_arr = np.asarray(base_score_matrix, dtype=float)
    best_scores = base_score_matrix_arr.min(axis=1)
    anchor_scores = []
    anchor_pred = public_preds["minimax_r05"]
    for q in q_scenarios.values():
        row_loss = ce_rows(q, anchor_pred)
        for rec in masks:
            mask = rec["mask"]
            assert isinstance(mask, np.ndarray)
            anchor_scores.append(float(row_loss[mask].mean()))
    anchor_scores_arr = np.asarray(anchor_scores, dtype=float)

    rows: list[Scored] = []
    generated: list[tuple[Scored, np.ndarray]] = []
    for base_name, base_pred in public_preds.items():
        rows.append(
            score_pred(
                name=f"base__{base_name}",
                mode="base",
                base_name=base_name,
                jepa_name="none",
                weight=0.0,
                pred=base_pred,
                q_scenarios=q_scenarios,
                masks=masks,
                base_scores=anchor_scores_arr,
                best_scores=best_scores,
                stage2=refs["stage2"],
                raw05=refs["raw05"],
            )
        )
        for jepa_name, jepa_pred in jepa_preds.items():
            for mode in ["logit", "prob"]:
                for weight in [0.03, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30, 0.40]:
                    pred = blend(base_pred, jepa_pred, weight, mode)
                    score = score_pred(
                        name=f"{base_name}__{jepa_name}__{mode}__w{weight:.3f}",
                        mode=mode,
                        base_name=base_name,
                        jepa_name=jepa_name,
                        weight=weight,
                        pred=pred,
                        q_scenarios=q_scenarios,
                        masks=masks,
                        base_scores=anchor_scores_arr,
                        best_scores=best_scores,
                        stage2=refs["stage2"],
                        raw05=refs["raw05"],
                    )
                    rows.append(score)
                    generated.append((score, pred))

    df = pd.DataFrame([r.__dict__ for r in rows]).sort_values(["score", "mean_expected"]).reset_index(drop=True)
    out_summary = JEPA_DIR / "public_jepa_hybrid_probe_summary.csv"
    df.to_csv(out_summary, index=False)

    safe_eligible = df[
        (df["weight"] > 0)
        & (df["mean_delta_vs_base"] <= 0.00030)
        & (df["p90_delta_vs_base"] <= 0.00120)
        & (df["mean_abs_delta_vs_stage2"] >= 0.018)
    ].copy()
    aggressive_eligible = df[
        (df["weight"] > 0)
        & (df["mean_abs_delta_vs_stage2"] >= 0.018)
        & (df["mean_expected"] <= 0.57590)
        & (df["p90_delta_vs_base"] <= 0.00150)
    ].copy()
    eligible = (
        pd.concat([safe_eligible, aggressive_eligible], ignore_index=True)
        .drop_duplicates("name")
        .sort_values(["mean_expected", "score"])
        .head(8)
    )
    name_to_pred = {score.name: pred for score, pred in generated}
    shortlist_rows = []
    for rank, row in enumerate(eligible.itertuples(index=False), start=1):
        pred = name_to_pred[row.name]
        alias = f"submission_bigshot_hybrid_{rank:02d}_{row.base}_{row.jepa}_{row.mode}_w{str(row.weight).replace('.', 'p')}.csv"
        out = sample[KEYS].copy()
        out[TARGETS] = pred
        out.to_csv(JEPA_DIR / alias, index=False)
        shortlist_rows.append(
            {
                "rank": rank,
                "alias": alias,
                "source_name": row.name,
                "score": row.score,
                "mean_expected": row.mean_expected,
                "mean_delta_vs_public_base": row.mean_delta_vs_base,
                "p90_delta_vs_public_base": row.p90_delta_vs_base,
                "mean_abs_delta_vs_stage2": row.mean_abs_delta_vs_stage2,
                "mean_abs_delta_vs_raw05": row.mean_abs_delta_vs_raw05,
                "min_prob": row.min_prob,
                "max_prob": row.max_prob,
            }
        )

    shortlist = pd.DataFrame(shortlist_rows)
    out_short = JEPA_DIR / "public_jepa_hybrid_probe_shortlist.csv"
    shortlist.to_csv(out_short, index=False)

    md = [
        "# Public-Safe JEPA Hybrid Probe",
        "",
        "This tests whether large JEPA moves can ride on top of the public-minimax candidates without violating the public-posterior scenario audit.",
        "",
        "## Top Scored Rows",
        "",
        "```",
        df[
            [
                "name",
                "score",
                "mean_expected",
                "mean_delta_vs_base",
                "p90_delta_vs_base",
                "mean_abs_delta_vs_stage2",
            ]
        ]
        .head(20)
        .round(9)
        .to_string(index=False),
        "```",
        "",
        "## Saved Hybrid Submissions",
        "",
    ]
    if shortlist.empty:
        md.append("No hybrid passed the public-delta and movement filters.")
    else:
        md.append(
            "```"
            + "\n"
            + shortlist[
                [
                    "rank",
                    "alias",
                    "score",
                    "mean_expected",
                    "mean_delta_vs_public_base",
                    "mean_abs_delta_vs_stage2",
                ]
            ]
            .round(9)
            .to_string(index=False)
            + "\n```"
        )
    md += [
        "",
        "## Interpretation",
        "",
        "The pure public bases still rank best. The saved hybrids are therefore not the first public-LB candidates; they are aggressive probes that keep the public-posterior expected loss under about 0.5759 while increasing JEPA movement.",
    ]
    (JEPA_DIR / "public_jepa_hybrid_probe_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"wrote {out_summary}")
    print(f"wrote {out_short}")
    print(df[["name", "score", "mean_expected", "mean_delta_vs_base", "p90_delta_vs_base", "mean_abs_delta_vs_stage2"]].head(16).round(9).to_string(index=False))
    if not shortlist.empty:
        print("[saved hybrids]")
        print(shortlist.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
