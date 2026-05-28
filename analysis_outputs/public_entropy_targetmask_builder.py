from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

from public_entropy_projection_builder import (  # noqa: E402
    ANCHOR,
    CONSTRAINT_FILES,
    CONSTRAINT_OOFS,
    KEY,
    PUBLIC2D0,
    PUBLIC2D0_OOF,
    SORT_KEY,
    STAGE2,
    STAGE2_OOF,
    TARGETS,
    clip,
    cross_entropy,
    expected_scores,
    gamma_prob,
    geometry_like_folds,
    load_public_scores,
    load_sub,
    loss_col,
    mean_loss,
    scores_from_labels,
    solve_projection,
)


GAMMAS = [0.25, 0.50, 0.75, 1.00]
MAX_SAVED = 48


def mask_name(mask: tuple[int, ...]) -> str:
    return "_".join(TARGETS[i].lower() for i in mask)


def target_subsets() -> list[tuple[int, ...]]:
    out: list[tuple[int, ...]] = []
    for r in range(1, len(TARGETS) + 1):
        out.extend(combinations(range(len(TARGETS)), r))
    return out


def masked_gamma_prob(prior: np.ndarray, projected: np.ndarray, gamma: float, mask: tuple[int, ...]) -> np.ndarray:
    out = prior.copy()
    cols = list(mask)
    out[:, cols] = gamma_prob(prior[:, cols], projected[:, cols], gamma)
    return clip(out)


def short_constraint_name(file_name: str) -> str:
    if file_name == ANCHOR:
        return "anchor"
    if file_name == STAGE2:
        return "stage2"
    return "ordinal"


def table_text(df: pd.DataFrame) -> str:
    return "```\n" + df.to_string(index=False) + "\n```"


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(SORT_KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    y = train[TARGETS].to_numpy(dtype=int)

    prior_sub_df = load_sub(PUBLIC2D0)
    prior_sub = prior_sub_df[TARGETS].to_numpy(dtype=float)
    prior_oof = clip(np.load(OUT / PUBLIC2D0_OOF))
    stage2_oof = clip(np.load(OUT / STAGE2_OOF))
    constraint_subs = [load_sub(name)[TARGETS].to_numpy(dtype=float) for name in CONSTRAINT_FILES]
    constraint_oofs = [clip(np.load(OUT / name)) for name in CONSTRAINT_OOFS]
    public_scores = load_public_scores()
    oof_scores = scores_from_labels(y, constraint_oofs)

    public_fit = solve_projection(prior_sub, constraint_subs, public_scores)
    oof_fit = solve_projection(prior_oof, constraint_oofs, oof_scores)
    prior_oof_loss = mean_loss(y, prior_oof)
    stage2_oof_loss = mean_loss(y, stage2_oof)

    folds = geometry_like_folds(train, n_repeats=8, target_frac=0.24)
    fold_contexts = []
    for _tr_idx, val_idx, fold_name in folds:
        y_val = y[val_idx]
        prior_val = prior_oof[val_idx]
        pred_val = [pred[val_idx] for pred in constraint_oofs]
        fold_fit = solve_projection(prior_val, pred_val, scores_from_labels(y_val, pred_val))
        fold_contexts.append((fold_name, val_idx, y_val, prior_val, fold_fit.prob))

    rows = []
    fold_rows = []
    for mask in target_subsets():
        targets = [TARGETS[i] for i in mask]
        tag_targets = "+".join(targets)
        for gamma in GAMMAS:
            sub_prob = masked_gamma_prob(prior_sub, public_fit.prob, gamma, mask)
            oof_prob = masked_gamma_prob(prior_oof, oof_fit.prob, gamma, mask)
            expected_public = expected_scores(sub_prob, constraint_subs)
            expected_oof = expected_scores(oof_prob, constraint_oofs)
            oof_loss = mean_loss(y, oof_prob)

            row: dict[str, float | int | str] = {
                "targets": tag_targets,
                "mask_size": len(mask),
                "gamma": gamma,
                "oof_loss": oof_loss,
                "oof_delta_vs_public2d0": oof_loss - prior_oof_loss,
                "oof_delta_vs_stage2": oof_loss - stage2_oof_loss,
                "public_self_expected_loss": cross_entropy(public_fit.prob, sub_prob),
                "public_crossentropy_gap": cross_entropy(public_fit.prob, sub_prob)
                - cross_entropy(public_fit.prob, public_fit.prob),
                "submission_abs_delta_mean_vs_prior": float(np.abs(sub_prob - prior_sub).mean()),
                "submission_abs_delta_p90_vs_prior": float(np.quantile(np.abs(sub_prob - prior_sub), 0.90)),
                "submission_min": float(sub_prob.min()),
                "submission_max": float(sub_prob.max()),
            }
            for file_name, expected, observed in zip(CONSTRAINT_FILES, expected_public, public_scores, strict=True):
                short = short_constraint_name(file_name)
                row[f"expected_public_{short}"] = float(expected)
                row[f"public_residual_{short}"] = float(expected - observed)
            for file_name, expected, observed in zip(CONSTRAINT_FILES, expected_oof, oof_scores, strict=True):
                short = short_constraint_name(file_name)
                row[f"expected_oof_{short}"] = float(expected)
                row[f"oof_constraint_residual_{short}"] = float(expected - observed)

            deltas = []
            wins = []
            for fold_name, val_idx, y_val, prior_val, fold_full in fold_contexts:
                fold_prob = masked_gamma_prob(prior_val, fold_full, gamma, mask)
                base_loss = mean_loss(y_val, prior_val)
                masked_loss = mean_loss(y_val, fold_prob)
                delta = masked_loss - base_loss
                deltas.append(delta)
                wins.append(delta < 0.0)
                frow: dict[str, float | str | int] = {
                    "targets": tag_targets,
                    "mask_size": len(mask),
                    "gamma": gamma,
                    "fold": fold_name,
                    "rows": int(len(val_idx)),
                    "base_loss": base_loss,
                    "masked_loss": masked_loss,
                    "delta": delta,
                }
                for j, target in enumerate(TARGETS):
                    frow[f"{target}_delta"] = loss_col(y_val[:, j], fold_prob[:, j]) - loss_col(
                        y_val[:, j], prior_val[:, j]
                    )
                fold_rows.append(frow)
            row["geometry_mean_delta"] = float(np.mean(deltas))
            row["geometry_win_rate"] = float(np.mean(wins))
            row["geometry_worst_delta"] = float(np.max(deltas))
            rows.append(row)

    summary = pd.DataFrame(rows)
    summary["risk_score"] = (
        summary["public_self_expected_loss"]
        + summary["public_crossentropy_gap"] * 0.25
        + summary["submission_abs_delta_mean_vs_prior"] * 0.10
        + np.maximum(summary["geometry_mean_delta"], 0.0) * 2.0
        + np.maximum(0.75 - summary["geometry_win_rate"], 0.0) * 0.01
    )
    summary = summary.sort_values(["risk_score", "oof_loss"]).reset_index(drop=True)
    summary.to_csv(OUT / "public_entropy_targetmask_summary.csv", index=False)
    geometry = pd.DataFrame(fold_rows)
    geometry.to_csv(OUT / "public_entropy_targetmask_geometry.csv", index=False)

    strict = summary[
        (summary["geometry_mean_delta"] < 0)
        & (summary["geometry_win_rate"] >= 0.875)
        & (summary["oof_delta_vs_stage2"] < -0.004)
        & (summary["public_self_expected_loss"] <= 0.5770)
    ].copy()
    if strict.empty:
        selected = summary.head(MAX_SAVED).copy()
    else:
        selected = strict.sort_values(["risk_score", "public_self_expected_loss", "oof_loss"]).head(MAX_SAVED).copy()

    selected_rows = []
    integrity_rows = []
    for _, row in selected.iterrows():
        mask = tuple(TARGETS.index(t) for t in str(row["targets"]).split("+"))
        gamma = float(row["gamma"])
        tag = f"{mask_name(mask)}_g{int(round(gamma * 100)):03d}"
        sub_prob = masked_gamma_prob(prior_sub, public_fit.prob, gamma, mask)
        oof_prob = masked_gamma_prob(prior_oof, oof_fit.prob, gamma, mask)
        out = prior_sub_df.copy()
        out[TARGETS] = sub_prob
        out = out.sort_values(KEY).reset_index(drop=True)
        if not out[KEY].equals(sample[KEY]):
            raise ValueError(f"sample key mismatch for {tag}")
        sub_file = f"submission_public_entropytm_public2d0_{tag}.csv"
        oof_file = f"final_public_entropytm_public2d0_{tag}_oof.npy"
        out.to_csv(OUT / sub_file, index=False)
        np.save(OUT / oof_file, oof_prob)
        selected_rows.append(
            {
                "file": sub_file,
                "oof_file": oof_file,
                "targets_changed": row["targets"],
                "donor": "public_entropy_targetmask",
                "mask": row["targets"],
                "weight": gamma,
                "source_file": "public_entropy_targetmask_summary.csv",
                "oof_loss": row["oof_loss"],
                "public_self_expected_loss": row["public_self_expected_loss"],
                "geometry_mean_delta": row["geometry_mean_delta"],
                "geometry_win_rate": row["geometry_win_rate"],
                "risk_score": row["risk_score"],
            }
        )
        integrity_rows.append(
            {
                "file": sub_file,
                "rows": len(out),
                "dups": int(out.duplicated(KEY).sum()),
                "na": int(out[TARGETS].isna().sum().sum()),
                "min_prob": float(out[TARGETS].min().min()),
                "max_prob": float(out[TARGETS].max().max()),
                "oof_shape": str(oof_prob.shape),
                "oof_min": float(oof_prob.min()),
                "oof_max": float(oof_prob.max()),
            }
        )

    selected_out = pd.DataFrame(selected_rows)
    selected_out.to_csv(OUT / "public_entropy_targetmask_selected.csv", index=False)
    pd.DataFrame(integrity_rows).to_csv(OUT / "public_entropy_targetmask_integrity.csv", index=False)

    report = []
    report.append("# Public Entropy Target-Mask Report\n")
    report.append(
        "Target subsets apply the public entropy projection only to selected targets, using public2d0 as the prior.\n"
    )
    report.append("\n## Top Summary Rows\n")
    cols = [
        "targets",
        "gamma",
        "oof_loss",
        "oof_delta_vs_stage2",
        "public_self_expected_loss",
        "public_crossentropy_gap",
        "geometry_mean_delta",
        "geometry_win_rate",
        "submission_abs_delta_mean_vs_prior",
        "risk_score",
    ]
    report.append(table_text(summary[cols].head(24).round(9)))
    report.append("\n\n## Saved Candidates\n")
    report.append(table_text(selected_out.head(24).round(9) if not selected_out.empty else selected_out))
    (OUT / "public_entropy_targetmask_report.md").write_text("".join(report))

    print("[target-mask summary]")
    print(summary[cols].head(30).round(9).to_string(index=False))
    print("\n[saved candidates]")
    print(selected_out.head(30).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
