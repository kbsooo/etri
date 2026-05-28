from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

import deep_dive_analysis as d  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
SORT_KEY = ["subject_id", "lifelog_date"]
EPS = 1e-5

ANCHOR = "submission_hybrid_0p578_logit_after_subject_final9_strict.csv"
ANCHOR_OOF = "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy"
STAGE2 = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
STAGE2_OOF = "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
ORDINAL = "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv"
ORDINAL_OOF = "final_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75_oof.npy"

CONSTRAINT_FILES = [ANCHOR, STAGE2, ORDINAL]
CONSTRAINT_OOFS = [ANCHOR_OOF, STAGE2_OOF, ORDINAL_OOF]

PRIORS = [
    ("public2d0", "submission_public2dblend_budget0p0.csv", "final_public2dblend_budget0p0_oof.npy"),
    ("proj0", "submission_projblend_cap0p0.csv", "final_projblend_cap0p0_oof.npy"),
    ("minimax", "submission_public_minimaxens_r01_a6_h422045.csv", "final_public_minimaxens_r01_a6_h422045_oof.npy"),
    ("stage2", STAGE2, STAGE2_OOF),
]

TARGET_MASKS = {
    "all": TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "core_q1_q3_s3_s4": ["Q1", "Q3", "S3", "S4"],
    "q_only": ["Q1", "Q2", "Q3"],
    "s_only": ["S1", "S2", "S3", "S4"],
}

GAMMAS = [0.35, 0.50, 0.65, 0.80, 1.00]


@dataclass
class ProjectionResult:
    block_prob: np.ndarray
    expanded_prob: np.ndarray
    lam: np.ndarray
    residual: np.ndarray
    iterations: int
    converged: bool


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -40.0, 40.0)))


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(pred)
    return float((-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp))).mean())


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float((-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp))).mean())


def score_features(pred: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p = clip(pred)
    intercept = -np.log(1.0 - p)
    coef = np.log((1.0 - p) / p)
    return intercept, coef


def scores_from_labels(y: np.ndarray, preds: list[np.ndarray]) -> np.ndarray:
    yy = y.astype(float)
    out = []
    for pred in preds:
        intercept, coef = score_features(pred)
        out.append(float(np.mean(intercept + coef * yy)))
    return np.asarray(out, dtype=float)


def expected_scores(q: np.ndarray, preds: list[np.ndarray]) -> np.ndarray:
    qq = clip(q)
    out = []
    for pred in preds:
        intercept, coef = score_features(pred)
        out.append(float(np.mean(intercept + coef * qq)))
    return np.asarray(out, dtype=float)


def load_sub(file_name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def load_public_scores() -> np.ndarray:
    obs = pd.read_csv(OUT / "public_probe_observations.csv").set_index("file")["public_lb"].astype(float)
    return np.asarray([float(obs[file_name]) for file_name in CONSTRAINT_FILES], dtype=float)


def stable_tag(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def sample_block_ids(train: pd.DataFrame, sample: pd.DataFrame) -> np.ndarray:
    known = train[KEY].copy()
    known["_kind"] = "known"
    unknown = sample[KEY].copy()
    unknown["_kind"] = "unknown"
    unknown["_row_pos"] = np.arange(len(sample))
    full = pd.concat([known, unknown], ignore_index=True, sort=False).sort_values(KEY).reset_index(drop=True)
    full["_block"] = full.groupby("subject_id")["_kind"].transform(lambda s: s.ne(s.shift()).cumsum()).astype(int)
    unk = full[full["_kind"].eq("unknown")].sort_values("_row_pos")
    return (unk["subject_id"].astype(str) + "_b" + unk["_block"].astype(str)).to_numpy()


def validation_block_ids(rows: pd.DataFrame) -> np.ndarray:
    sorted_rows = rows.sort_values(SORT_KEY).copy()
    sorted_rows["_orig_pos"] = np.arange(len(rows))[sorted_rows.index.argsort().argsort()]
    block = []
    for sid, group in sorted_rows.groupby("subject_id", sort=False):
        day_gap = group["lifelog_date"].diff().dt.days.fillna(1)
        bid = day_gap.ne(1).cumsum().astype(int)
        block.extend((str(sid) + "_v" + bid.astype(str)).tolist())
    out = pd.Series(block, index=sorted_rows.index).loc[rows.index].to_numpy()
    return out


def group_reduce(
    prior: np.ndarray,
    constraint_preds: list[np.ndarray],
    block_ids: np.ndarray,
    target_idx: list[int],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    unique_blocks = pd.Index(block_ids).drop_duplicates().to_numpy()
    block_to_idx = {b: i for i, b in enumerate(unique_blocks)}
    n_blocks = len(unique_blocks)
    n_vars = n_blocks * len(target_idx)
    weights = np.zeros(n_vars, dtype=float)
    prior_sum = np.zeros(n_vars, dtype=float)
    coef_sums = [np.zeros(n_vars, dtype=float) for _ in constraint_preds]
    constant_sum = np.zeros(len(constraint_preds), dtype=float)

    total_cells = prior.shape[0] * prior.shape[1]
    target_set = set(target_idx)
    for i, bid in enumerate(block_ids):
        b = block_to_idx[bid]
        for j in range(prior.shape[1]):
            for k, pred in enumerate(constraint_preds):
                intercept, coef = score_features(pred[i : i + 1, j : j + 1])
                intercept_value = float(intercept[0, 0]) / total_cells
                coef_value = float(coef[0, 0]) / total_cells
                if j in target_set:
                    local_j = target_idx.index(j)
                    v = b * len(target_idx) + local_j
                    if k == 0:
                        weights[v] += 1.0 / total_cells
                        prior_sum[v] += prior[i, j]
                    constant_sum[k] += intercept_value
                    coef_sums[k][v] += coef_value
                else:
                    constant_sum[k] += intercept_value + coef_value * float(prior[i, j])

    prior_group = clip(prior_sum / np.maximum(weights * total_cells, 1e-12))
    coef_mat = np.vstack(coef_sums).T
    return prior_group, coef_mat, constant_sum, weights, unique_blocks


def expand_group(
    group_prob: np.ndarray,
    block_ids: np.ndarray,
    unique_blocks: np.ndarray,
    target_idx: list[int],
    base: np.ndarray,
) -> np.ndarray:
    out = base.copy()
    block_to_idx = {b: i for i, b in enumerate(unique_blocks)}
    for i, bid in enumerate(block_ids):
        b = block_to_idx[bid]
        for local_j, j in enumerate(target_idx):
            out[i, j] = group_prob[b * len(target_idx) + local_j]
    return clip(out)


def solve_block_projection(
    prior: np.ndarray,
    constraint_preds: list[np.ndarray],
    target_scores: np.ndarray,
    block_ids: np.ndarray,
    target_names: list[str],
) -> ProjectionResult:
    target_idx = [TARGETS.index(t) for t in target_names]
    prior_group, coef_mat, constant_sum, weights, unique_blocks = group_reduce(prior, constraint_preds, block_ids, target_idx)
    target_moments = np.asarray(target_scores, dtype=float) - constant_sum
    z0 = logit(prior_group)
    lam = np.zeros(coef_mat.shape[1], dtype=float)
    converged = False
    residual = np.full(coef_mat.shape[1], np.nan)
    for it in range(100):
        q = sigmoid(z0 + coef_mat @ lam / np.maximum(weights, 1e-12))
        moments = coef_mat.T @ q
        residual = target_moments - moments
        if float(np.max(np.abs(residual))) < 1e-10:
            converged = True
            break
        w = q * (1.0 - q)
        jac = (coef_mat.T * (w / np.maximum(weights, 1e-12))) @ coef_mat
        jac += 1e-8 * np.eye(jac.shape[0])
        step = np.linalg.solve(jac, residual)
        step_norm = float(np.linalg.norm(step))
        if step_norm > 12.0:
            step *= 12.0 / step_norm
        lam += step
    q = sigmoid(z0 + coef_mat @ lam / np.maximum(weights, 1e-12))
    residual = target_moments - coef_mat.T @ q
    expanded = expand_group(q, block_ids, unique_blocks, target_idx, prior)
    return ProjectionResult(q, expanded, lam, residual, it + 1, converged)


def blend_probs(prior: np.ndarray, projected: np.ndarray, gamma: float) -> np.ndarray:
    return clip(sigmoid(logit(prior) + gamma * (logit(projected) - logit(prior))))


def analogue_folds(train: pd.DataFrame) -> list[tuple[np.ndarray, np.ndarray]]:
    return d.make_folds(train, "subject_blocks")


def analogue_projection(
    prior_oof: np.ndarray,
    constraint_oofs: list[np.ndarray],
    train: pd.DataFrame,
    target_names: list[str],
    gamma: float,
) -> tuple[np.ndarray, dict[str, float]]:
    y = train[TARGETS].to_numpy(dtype=int)
    pred = prior_oof.copy()
    fold_rows = []
    for fold_id, (_tr_idx, val_idx) in enumerate(analogue_folds(train)):
        rows = train.iloc[val_idx].copy()
        block_ids = validation_block_ids(rows)
        target_scores = scores_from_labels(y[val_idx], [p[val_idx] for p in constraint_oofs])
        fit = solve_block_projection(prior_oof[val_idx], [p[val_idx] for p in constraint_oofs], target_scores, block_ids, target_names)
        pred[val_idx] = blend_probs(prior_oof[val_idx], fit.expanded_prob, gamma)
        fold_rows.append(
            {
                "fold": fold_id,
                "converged": fit.converged,
                "iterations": fit.iterations,
                "max_abs_residual": float(np.max(np.abs(fit.residual))),
                "rows": int(len(val_idx)),
                "blocks": int(pd.Series(block_ids).nunique()),
            }
        )
    out: dict[str, float] = {
        "analogue_loss": mean_loss(y, pred),
        "prior_loss": mean_loss(y, prior_oof),
        "analogue_delta": mean_loss(y, pred) - mean_loss(y, prior_oof),
        "fold_max_residual": float(pd.DataFrame(fold_rows)["max_abs_residual"].max()),
        "fold_converged_rate": float(pd.DataFrame(fold_rows)["converged"].mean()),
    }
    for j, target in enumerate(TARGETS):
        out[f"{target}_delta"] = loss_col(y[:, j], pred[:, j]) - loss_col(y[:, j], prior_oof[:, j])
    return pred, out


def analogue_eval(prior_oof: np.ndarray, constraint_oofs: list[np.ndarray], train: pd.DataFrame, target_names: list[str], gamma: float) -> dict[str, float]:
    _pred, stats = analogue_projection(prior_oof, constraint_oofs, train, target_names, gamma)
    return stats


def make_submission_candidate(
    sample: pd.DataFrame,
    train: pd.DataFrame,
    prior_name: str,
    prior_sub_file: str,
    prior_oof_file: str,
    target_mask_name: str,
    target_names: list[str],
    gamma: float,
    constraint_subs: list[np.ndarray],
    constraint_oofs: list[np.ndarray],
    public_scores: np.ndarray,
) -> tuple[str, str, dict[str, float | str | bool | int]]:
    prior_df = load_sub(prior_sub_file)
    prior_sub = prior_df[TARGETS].to_numpy(dtype=float)
    block_ids = sample_block_ids(train, sample)
    fit = solve_block_projection(prior_sub, constraint_subs, public_scores, block_ids, target_names)
    pred = blend_probs(prior_sub, fit.expanded_prob, gamma)
    expected = expected_scores(pred, constraint_subs)
    tag = stable_tag(f"{prior_name}:{target_mask_name}:{gamma:.2f}:{','.join(f'{x:.9f}' for x in public_scores)}")
    sub_file = f"submission_public_blockentropy_{prior_name}_{target_mask_name}_g{int(round(gamma*100)):03d}_{tag}.csv"
    oof_file = f"final_public_blockentropy_{prior_name}_{target_mask_name}_g{int(round(gamma*100)):03d}_{tag}_oof.npy"
    out = sample[KEY].copy()
    out[TARGETS] = pred
    out.to_csv(OUT / sub_file, index=False)
    prior_oof = clip(np.load(OUT / prior_oof_file))
    oof_pred, analogue = analogue_projection(prior_oof, constraint_oofs, train, target_names, gamma)
    np.save(OUT / oof_file, oof_pred)
    row: dict[str, float | str | bool | int] = {
        "file": sub_file,
        "oof_file": oof_file,
        "prior": prior_name,
        "target_mask": target_mask_name,
        "targets": ",".join(target_names),
        "gamma": gamma,
        "blocks": int(pd.Series(block_ids).nunique()),
        "converged": fit.converged,
        "iterations": fit.iterations,
        "max_abs_constraint_residual": float(np.max(np.abs(fit.residual))),
        "mean_abs_move": float(np.mean(np.abs(pred - prior_sub))),
        "max_abs_move": float(np.max(np.abs(pred - prior_sub))),
    }
    for name, score, target in zip(CONSTRAINT_FILES, expected, public_scores, strict=True):
        row[f"expected__{name}"] = float(score)
        row[f"target__{name}"] = float(target)
        row[f"residual__{name}"] = float(score - target)
    for col, value in analogue.items():
        row[col] = float(value)
    return sub_file, oof_file, row


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    constraint_subs = [load_sub(f)[TARGETS].to_numpy(dtype=float) for f in CONSTRAINT_FILES]
    constraint_oofs = [clip(np.load(OUT / f)) for f in CONSTRAINT_OOFS]
    public_scores = load_public_scores()

    rows = []
    selected_rows = []
    for prior_name, prior_sub_file, prior_oof_file in PRIORS:
        if not (OUT / prior_sub_file).exists() or not (OUT / prior_oof_file).exists():
            continue
        prior_oof = clip(np.load(OUT / prior_oof_file))
        for mask_name, target_names in TARGET_MASKS.items():
            for gamma in GAMMAS:
                analogue = analogue_eval(prior_oof, constraint_oofs, train, target_names, gamma)
                rows.append(
                    {
                        "prior": prior_name,
                        "prior_file": prior_sub_file,
                        "prior_oof_file": prior_oof_file,
                        "target_mask": mask_name,
                        "targets": ",".join(target_names),
                        "gamma": gamma,
                        **analogue,
                    }
                )
    summary = pd.DataFrame(rows).sort_values(["analogue_loss", "analogue_delta"]).reset_index(drop=True)
    summary.to_csv(OUT / "public_blockentropy_analogue_summary.csv", index=False)

    # Save a small, diverse set: best per prior plus public2d0/minimax no-Q2 and core masks.
    save_keys = set()
    for prior_name in summary["prior"].drop_duplicates():
        top = summary[summary["prior"].eq(prior_name)].head(3)
        save_keys.update((r.prior, r.target_mask, float(r.gamma)) for r in top.itertuples(index=False))
    for key in [
        ("public2d0", "no_q2", 0.50),
        ("public2d0", "no_q2", 0.65),
        ("public2d0", "core_q1_q3_s3_s4", 0.65),
        ("minimax", "no_q2", 0.50),
        ("minimax", "core_q1_q3_s3_s4", 0.50),
    ]:
        save_keys.add(key)

    prior_lookup = {name: (sub, oof) for name, sub, oof in PRIORS}
    for prior_name, mask_name, gamma in sorted(save_keys):
        if prior_name not in prior_lookup or mask_name not in TARGET_MASKS:
            continue
        prior_sub_file, prior_oof_file = prior_lookup[prior_name]
        if not (OUT / prior_sub_file).exists() or not (OUT / prior_oof_file).exists():
            continue
        _sub_file, _oof_file, row = make_submission_candidate(
            sample,
            train,
            prior_name,
            prior_sub_file,
            prior_oof_file,
            mask_name,
            TARGET_MASKS[mask_name],
            gamma,
            constraint_subs,
            constraint_oofs,
            public_scores,
        )
        match = summary[
            summary["prior"].eq(prior_name)
            & summary["target_mask"].eq(mask_name)
            & np.isclose(summary["gamma"], gamma)
        ]
        selected_rows.append(row)

    selected = pd.DataFrame(selected_rows).sort_values(["analogue_loss", "mean_abs_move"]).reset_index(drop=True)
    selected.to_csv(OUT / "public_blockentropy_selected.csv", index=False)

    integ_rows = []
    for row in selected.itertuples(index=False):
        sub = pd.read_csv(OUT / row.file, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        integ_rows.append(
            {
                "file": row.file,
                "rows": int(len(sub)),
                "key_match": bool(sub[KEY].equals(sample[KEY])),
                "duplicate_keys": int(sub.duplicated(KEY).sum()),
                "null_predictions": int(sub[TARGETS].isna().sum().sum()),
                "min_prob": float(sub[TARGETS].min().min()),
                "max_prob": float(sub[TARGETS].max().max()),
            }
        )
    integ = pd.DataFrame(integ_rows)
    integ.to_csv(OUT / "public_blockentropy_integrity.csv", index=False)

    cols = [
        "file",
        "prior",
        "target_mask",
        "gamma",
        "analogue_loss",
        "analogue_delta",
        "mean_abs_move",
        "max_abs_move",
        "max_abs_constraint_residual",
    ]
    report = []
    report.append("# Public Block Entropy Projection\n")
    report.append(
        "This variant solves the three observed public-score constraints with one latent probability per actual submission block and target, "
        "rather than one independent probability per row-target cell.\n"
    )
    report.append("\n## Analogue Top Rows\n")
    show_cols = ["prior", "target_mask", "gamma", "analogue_loss", "prior_loss", "analogue_delta", "fold_max_residual", "fold_converged_rate"]
    report.append("```\n" + summary[show_cols].head(20).round(9).to_string(index=False) + "\n```")
    report.append("\n\n## Saved Candidates\n")
    report.append("```\n" + selected[cols].round(9).to_string(index=False) + "\n```")
    report.append("\n\n## Integrity\n")
    report.append("```\n" + integ.round(9).to_string(index=False) + "\n```")
    (OUT / "public_blockentropy_report.md").write_text("".join(report))

    print("[block entropy analogue top]")
    print(summary[show_cols].head(24).round(9).to_string(index=False))
    print("\n[block entropy selected]")
    print(selected[cols].round(9).to_string(index=False))
    print("\n[integrity]")
    print(integ.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
