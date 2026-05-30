#!/usr/bin/env python3
"""E248: OOF invariance audit for the E247 feature-NN1 smoothing selector.

E247 is the first candidate where the JEPA idea is used as a mechanism: choose
Q3 rollback cells because they reduce roughness on the E207 feature-nearest-
neighbor manifold. Its weakness is that the selector is test-geometry-derived,
not OOF-learned.

This audit asks whether the same smoothing score is label-relevant on train
OOF `q3_e224` movements. If rows with high feature-NN1 smoothing gain are rows
where the full E224-like movement is harmful, E247 gains invariance support. If
not, E247 remains a high-information public sensor but not a certified selector.

No submission files are created.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import NearestNeighbors


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import broad_feature_addon_builder as stage2  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e207_lejepa_identifiability_conditions_audit as e207  # noqa: E402
import e232_cross_target_support_invariance as e232  # noqa: E402
import e246_feature_nn1_smoothing_selector_ablation as e246  # noqa: E402


RNG = 20260530 + 248
EPS = 1.0e-12
KEY = ["subject_id", "lifelog_date"]
FRACTIONS = [0.05, 0.10, 34.0 / 250.0, 0.20]

SUMMARY_OUT = OUT / "e248_feature_nn1_oof_smoothing_invariance_summary.csv"
STRESS_OUT = OUT / "e248_feature_nn1_oof_smoothing_invariance_stress.csv"
STRESS_SUMMARY_OUT = OUT / "e248_feature_nn1_oof_smoothing_invariance_stress_summary.csv"
TEST_CONTEXT_OUT = OUT / "e248_feature_nn1_oof_smoothing_invariance_test_context.csv"
REPORT_OUT = OUT / "e248_feature_nn1_oof_smoothing_invariance_report.md"


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def safe_auc(y: np.ndarray, score: np.ndarray) -> float:
    yy = np.asarray(y, dtype=int)
    if len(np.unique(yy)) < 2:
        return float("nan")
    return float(roc_auc_score(yy, np.asarray(score, dtype=float)))


def safe_ap(y: np.ndarray, score: np.ndarray) -> float:
    yy = np.asarray(y, dtype=int)
    if len(np.unique(yy)) < 2:
        return float("nan")
    return float(average_precision_score(yy, np.asarray(score, dtype=float)))


def rank_corr(a: pd.Series, b: pd.Series) -> float:
    aa = pd.to_numeric(a, errors="coerce").rank(method="average")
    bb = pd.to_numeric(b, errors="coerce").rank(method="average")
    return float(aa.corr(bb))


def train_only_feature_space(train_feat: pd.DataFrame) -> np.ndarray:
    cols = e207.numeric_feature_cols(train_feat)
    x, raw_cols = e207.scaled_matrix(train_feat, cols, top_cols=3000)
    return e207.pca_space("broad_stage2_pca64_train_only", x, "train-only broad stage2 matrix", raw_cols, dim=64).x


def all_pca_train_space(train_feat: pd.DataFrame, sub_feat: pd.DataFrame) -> np.ndarray:
    space = e207.load_pair_feature_space(train_feat, sub_feat)
    return space.x[: len(train_feat)]


def nn1_indices(z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    nbrs = NearestNeighbors(n_neighbors=2, metric="euclidean")
    nbrs.fit(z)
    dist, ind = nbrs.kneighbors(z)
    return ind[:, 1].astype(int), dist[:, 1].astype(float)


def smoothing_frame(base_prob: np.ndarray, full_prob: np.ndarray, nn: np.ndarray, dist: np.ndarray, prefix: str) -> pd.DataFrame:
    base = logit(base_prob)
    full = logit(full_prob)
    incoming: list[list[int]] = [[] for _ in range(len(full))]
    for source, target in enumerate(nn):
        incoming[int(target)].append(int(source))

    source_delta = np.abs(base - full[nn]) - np.abs(full - full[nn])
    incoming_delta_sum = np.zeros(len(full), dtype=np.float64)
    incoming_count = np.zeros(len(full), dtype=np.float64)
    for row_idx, sources in enumerate(incoming):
        if not sources:
            continue
        src = np.asarray(sources, dtype=int)
        before = np.abs(full[src] - full[row_idx])
        after = np.abs(full[src] - base[row_idx])
        incoming_delta_sum[row_idx] = float(np.sum(after - before))
        incoming_count[row_idx] = float(len(src))

    total_delta = source_delta + incoming_delta_sum
    affected_count = 1.0 + incoming_count
    amp = np.abs(full - base)
    return pd.DataFrame(
        {
            f"{prefix}_nn_row_idx": nn,
            f"{prefix}_nn_dist": dist,
            f"{prefix}_rollback_amp_abs": amp,
            f"{prefix}_source_pair_delta": source_delta,
            f"{prefix}_incoming_pair_delta_sum": incoming_delta_sum,
            f"{prefix}_incoming_pair_count": incoming_count,
            f"{prefix}_single_row_pair_delta_sum": total_delta,
            f"{prefix}_single_row_pair_delta_mean": total_delta / np.maximum(affected_count, 1.0),
            f"{prefix}_smooth_gain_sum": -total_delta,
            f"{prefix}_smooth_gain_mean": -total_delta / np.maximum(affected_count, 1.0),
            f"{prefix}_amp_smooth_gain_sum": -total_delta * amp,
            f"{prefix}_source_smooth_gain": -source_delta,
            f"{prefix}_incoming_smooth_gain_sum": -incoming_delta_sum,
        }
    )


def build_train_scores() -> tuple[pd.DataFrame, list[str]]:
    stage_train_raw, stage_sub_raw, train_feat, sub_feat = stage2.build_frames()
    train_raw, train_long, _, _ = e232.build_long_frames()
    if not stage_train_raw[KEY].astype(str).equals(train_raw[KEY].astype(str)):
        raise RuntimeError("stage2/e232 train key order mismatch")

    q3 = train_long[train_long["task_name"].eq("q3_e224")].copy().sort_values("row_idx").reset_index(drop=True)
    if len(q3) != len(train_feat):
        raise RuntimeError(f"unexpected q3/train feature row count: {len(q3)} vs {len(train_feat)}")

    z_train_only = train_only_feature_space(train_feat)
    nn_train, dist_train = nn1_indices(z_train_only)
    z_all = all_pca_train_space(train_feat, sub_feat)
    nn_all, dist_all = nn1_indices(z_all)

    base = q3["base_prob"].to_numpy(dtype=float)
    full = q3["full_prob"].to_numpy(dtype=float)
    score = pd.concat(
        [
            q3[["row_idx", "subject_id", "base_prob", "full_prob", "benefit", "abs_logit_step", "full_margin"]].reset_index(drop=True),
            smoothing_frame(base, full, nn_train, dist_train, "trainpca"),
            smoothing_frame(base, full, nn_all, dist_all, "allpca"),
        ],
        axis=1,
    )
    score["harmful"] = (score["benefit"] < 0.0).astype(int)
    score["tail10"] = (score["benefit"] <= float(score["benefit"].quantile(0.10))).astype(int)
    score["tail20"] = (score["benefit"] <= float(score["benefit"].quantile(0.20))).astype(int)
    score["score_amp"] = score["abs_logit_step"].astype(float)
    score["score_trainpca_smooth_sum"] = score["trainpca_smooth_gain_sum"]
    score["score_trainpca_smooth_mean"] = score["trainpca_smooth_gain_mean"]
    score["score_trainpca_amp_smooth"] = score["trainpca_amp_smooth_gain_sum"]
    score["score_trainpca_source"] = score["trainpca_source_smooth_gain"]
    score["score_trainpca_incoming"] = score["trainpca_incoming_smooth_gain_sum"]
    score["score_allpca_smooth_sum"] = score["allpca_smooth_gain_sum"]
    score["score_allpca_smooth_mean"] = score["allpca_smooth_gain_mean"]
    score["score_allpca_amp_smooth"] = score["allpca_amp_smooth_gain_sum"]
    score["score_allpca_source"] = score["allpca_source_smooth_gain"]
    score["score_allpca_incoming"] = score["allpca_incoming_smooth_gain_sum"]
    score["score_neg_trainpca_smooth_sum"] = -score["score_trainpca_smooth_sum"]
    score_cols = [
        "score_amp",
        "score_trainpca_smooth_sum",
        "score_trainpca_smooth_mean",
        "score_trainpca_amp_smooth",
        "score_trainpca_source",
        "score_trainpca_incoming",
        "score_allpca_smooth_sum",
        "score_allpca_smooth_mean",
        "score_allpca_amp_smooth",
        "score_allpca_source",
        "score_allpca_incoming",
        "score_neg_trainpca_smooth_sum",
    ]
    return score, score_cols


def full_score_summary(train: pd.DataFrame, score_cols: list[str]) -> pd.DataFrame:
    benefit = train["benefit"].astype(float)
    rows: list[dict[str, Any]] = []
    n = len(train)
    for score_col in score_cols:
        score = train[score_col].astype(float)
        for frac in FRACTIONS:
            k = max(1, int(round(n * frac)))
            idx = score.sort_values(ascending=False, kind="mergesort").head(k).index
            selected_benefit = benefit.loc[idx]
            rows.append(
                {
                    "score": score_col,
                    "top_frac": frac,
                    "selected_n": int(k),
                    "auc_harmful": safe_auc(train["harmful"].to_numpy(), score.to_numpy()),
                    "ap_harmful": safe_ap(train["harmful"].to_numpy(), score.to_numpy()),
                    "auc_tail10": safe_auc(train["tail10"].to_numpy(), score.to_numpy()),
                    "auc_tail20": safe_auc(train["tail20"].to_numpy(), score.to_numpy()),
                    "benefit_spearman_neg": rank_corr(score, -benefit),
                    "selected_mean_benefit": float(selected_benefit.mean()),
                    "population_mean_benefit": float(benefit.mean()),
                    "drop_delta_vs_full_per_row": float(selected_benefit.sum() / n),
                    "harmful_rate_selected": float((selected_benefit < 0.0).mean()),
                    "harmful_rate_population": float((benefit < 0.0).mean()),
                    "tail20_rate_selected": float((selected_benefit <= benefit.quantile(0.20)).mean()),
                    "smooth_gain_mean_selected": float(train.loc[idx, score_col].mean()),
                }
            )
    return pd.DataFrame(rows).sort_values(["top_frac", "drop_delta_vs_full_per_row"])


def split_random_stratified(frame: pd.DataFrame, n_splits: int = 5) -> list[tuple[str, np.ndarray, np.ndarray]]:
    out: list[tuple[str, np.ndarray, np.ndarray]] = []
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RNG)
    idx = np.arange(len(frame))
    y = frame["harmful"].to_numpy(dtype=int)
    for i, (tr, va) in enumerate(skf.split(idx, y)):
        out.append((f"random_stratified_{i}", tr, va))
    return out


def split_row_contiguous(frame: pd.DataFrame, n_splits: int = 5) -> list[tuple[str, np.ndarray, np.ndarray]]:
    idx = np.arange(len(frame))
    chunks = np.array_split(idx, n_splits)
    out = []
    for i, va in enumerate(chunks):
        tr = np.setdiff1d(idx, va)
        out.append((f"row_contiguous_{i}", tr, va))
    return out


def split_subject_loo(frame: pd.DataFrame) -> list[tuple[str, np.ndarray, np.ndarray]]:
    out = []
    idx = np.arange(len(frame))
    for subject in sorted(frame["subject_id"].astype(str).unique()):
        va = np.where(frame["subject_id"].astype(str).to_numpy() == subject)[0]
        tr = np.setdiff1d(idx, va)
        out.append((f"subject_loo_{subject}", tr, va))
    return out


def stress_eval(train: pd.DataFrame, score_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    splits = split_random_stratified(train) + split_row_contiguous(train) + split_subject_loo(train)
    rows: list[dict[str, Any]] = []
    for split_name, tr, va in splits:
        tr_df = train.iloc[tr]
        va_df = train.iloc[va]
        valid_benefit = va_df["benefit"].astype(float)
        for score_col in score_cols:
            train_score = tr_df[score_col].astype(float)
            valid_score = va_df[score_col].astype(float)
            for frac in FRACTIONS:
                k = max(1, int(round(len(va_df) * frac)))
                top_idx = valid_score.sort_values(ascending=False, kind="mergesort").head(k).index
                threshold = float(train_score.quantile(1.0 - frac))
                threshold_idx = valid_score[valid_score >= threshold].index
                for mode, selected_index in [
                    ("valid_top_frac", top_idx),
                    ("train_quantile_threshold", threshold_idx),
                ]:
                    selected_benefit = valid_benefit.loc[selected_index]
                    selected_n = int(len(selected_benefit))
                    if selected_n == 0:
                        selected_mean = np.nan
                        drop_delta = 0.0
                        harmful_rate = np.nan
                        tail20_rate = np.nan
                    else:
                        selected_mean = float(selected_benefit.mean())
                        drop_delta = float(selected_benefit.sum() / max(len(va_df), 1))
                        harmful_rate = float((selected_benefit < 0.0).mean())
                        tail20_rate = float((selected_benefit <= valid_benefit.quantile(0.20)).mean())
                    rows.append(
                        {
                            "split": split_name,
                            "split_family": split_name.rsplit("_", 1)[0],
                            "score": score_col,
                            "top_frac": frac,
                            "mode": mode,
                            "valid_n": int(len(va_df)),
                            "selected_n": selected_n,
                            "selected_mean_benefit": selected_mean,
                            "valid_mean_benefit": float(valid_benefit.mean()),
                            "drop_delta_vs_full_per_row": drop_delta,
                            "harmful_rate_selected": harmful_rate,
                            "harmful_rate_valid": float((valid_benefit < 0.0).mean()),
                            "tail20_rate_selected": tail20_rate,
                        }
                    )
    stress = pd.DataFrame(rows)
    summary = (
        stress.groupby(["score", "top_frac", "mode"], dropna=False)
        .agg(
            folds=("split", "count"),
            selected_n_mean=("selected_n", "mean"),
            drop_delta_mean=("drop_delta_vs_full_per_row", "mean"),
            drop_delta_std=("drop_delta_vs_full_per_row", "std"),
            win_rate=("drop_delta_vs_full_per_row", lambda x: float((x < 0.0).mean())),
            selected_mean_benefit_mean=("selected_mean_benefit", "mean"),
            harmful_rate_selected_mean=("harmful_rate_selected", "mean"),
            harmful_rate_valid_mean=("harmful_rate_valid", "mean"),
            tail20_rate_selected_mean=("tail20_rate_selected", "mean"),
        )
        .reset_index()
        .sort_values(["top_frac", "mode", "drop_delta_mean"])
    )
    return stress, summary


def test_context() -> pd.DataFrame:
    rows_path = OUT / "e246_feature_nn1_smoothing_selector_rows.csv"
    if not rows_path.exists():
        e246.main()
    rows = pd.read_csv(rows_path)
    if rows.empty:
        return pd.DataFrame()
    e247_set = set(
        rows.sort_values("single_row_smooth_gain_sum", ascending=False).head(34)["row_idx"].astype(int).tolist()
    )
    e237_set = set(rows.loc[rows["e237_drop"].astype(bool), "row_idx"].astype(int))
    swing_set = set(rows.loc[rows["e230_swing25"].astype(bool), "row_idx"].astype(int))
    amp25_set = set(rows.sort_values("rollback_amp_abs", ascending=False).head(25)["row_idx"].astype(int).tolist())
    out: list[dict[str, Any]] = []
    for score_col in [
        "single_row_smooth_gain_sum",
        "single_row_smooth_gain_mean",
        "amp_smooth_gain_sum",
        "source_smooth_gain",
        "incoming_smooth_gain_sum",
        "rollback_amp_abs",
    ]:
        score = rows[score_col].astype(float)
        for frac in FRACTIONS:
            k = max(1, int(round(len(rows) * frac)))
            idx = set(rows.loc[score.sort_values(ascending=False, kind="mergesort").head(k).index, "row_idx"].astype(int))
            out.append(
                {
                    "score": score_col,
                    "top_frac": frac,
                    "selected_n": len(idx),
                    "overlap_e247": len(idx & e247_set),
                    "overlap_e237": len(idx & e237_set),
                    "overlap_e230_swing25": len(idx & swing_set),
                    "overlap_amp_top25": len(idx & amp25_set),
                    "jaccard_e247": float(len(idx & e247_set) / len(idx | e247_set)) if idx or e247_set else 1.0,
                    "mean_smooth_gain": float(rows.loc[rows["row_idx"].isin(idx), "single_row_smooth_gain_sum"].mean()),
                    "mean_amp": float(rows.loc[rows["row_idx"].isin(idx), "rollback_amp_abs"].mean()),
                }
            )
    return pd.DataFrame(out).sort_values(["top_frac", "overlap_e247"], ascending=[True, False])


def write_report(summary: pd.DataFrame, stress_summary: pd.DataFrame, test_ctx: pd.DataFrame) -> None:
    focus_frac = 34.0 / 250.0
    full_focus = summary[np.isclose(summary["top_frac"], focus_frac)].sort_values("drop_delta_vs_full_per_row")
    stress_focus = stress_summary[
        np.isclose(stress_summary["top_frac"], focus_frac) & stress_summary["mode"].eq("valid_top_frac")
    ].sort_values("drop_delta_mean")
    best = full_focus.iloc[0]
    e247_train = summary[
        np.isclose(summary["top_frac"], focus_frac) & summary["score"].eq("score_trainpca_smooth_sum")
    ].head(1)
    e247_all = summary[
        np.isclose(summary["top_frac"], focus_frac) & summary["score"].eq("score_allpca_smooth_sum")
    ].head(1)
    cols = [
        "score",
        "top_frac",
        "selected_n",
        "auc_harmful",
        "auc_tail20",
        "benefit_spearman_neg",
        "drop_delta_vs_full_per_row",
        "harmful_rate_selected",
        "tail20_rate_selected",
    ]
    stress_cols = [
        "score",
        "top_frac",
        "mode",
        "folds",
        "selected_n_mean",
        "drop_delta_mean",
        "drop_delta_std",
        "win_rate",
        "harmful_rate_selected_mean",
        "tail20_rate_selected_mean",
    ]
    test_cols = [
        "score",
        "top_frac",
        "selected_n",
        "overlap_e247",
        "overlap_e237",
        "overlap_e230_swing25",
        "overlap_amp_top25",
        "jaccard_e247",
    ]
    lines = [
        "# E248 Feature-NN1 OOF Smoothing Invariance",
        "",
        "## Question",
        "",
        "Does E247's feature-NN1 Q3 smoothing selector have a train/OOF analogue, or is it only a test-geometry stress survivor?",
        "",
        "The target quantity is OOF `q3_e224` benefit: `base_loss - full_loss`. Negative selected benefit means rolling the full movement back to base would improve LogLoss.",
        "",
        "## Full Train Ranking At E247 Fraction",
        "",
        md_table(full_focus, cols, n=20),
        "",
        "## Split Stress At E247 Fraction",
        "",
        md_table(stress_focus, stress_cols, n=20),
        "",
        "## E247-Analog Rows",
        "",
        md_table(pd.concat([e247_train, e247_all], ignore_index=True), cols, n=5),
        "",
        "## Test Context Sanity",
        "",
        md_table(test_ctx[np.isclose(test_ctx["top_frac"], focus_frac)].sort_values("overlap_e247", ascending=False), test_cols, n=20),
        "",
        "## Decision",
        "",
    ]
    if float(best["drop_delta_vs_full_per_row"]) < 0.0:
        lines.append(
            f"- Best OOF score `{best['score']}` has negative selected rollback delta `{best['drop_delta_vs_full_per_row']:.9f}`. Feature-NN smoothing has some OOF support, but split stress decides whether E247 should be upgraded."
        )
    else:
        lines.append(
            f"- Best OOF score `{best['score']}` is still non-negative at `{best['drop_delta_vs_full_per_row']:.9f}`. E247 remains a high-information public sensor, not an OOF-certified selector."
        )
    train_delta = float(e247_train["drop_delta_vs_full_per_row"].iloc[0]) if not e247_train.empty else float("nan")
    all_delta = float(e247_all["drop_delta_vs_full_per_row"].iloc[0]) if not e247_all.empty else float("nan")
    lines.append(f"- E247 train-only PCA analogue delta: `{train_delta:.9f}`.")
    lines.append(f"- E247 all-PCA analogue delta: `{all_delta:.9f}`.")
    lines.append("- No submission is created by E248.")
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    train, score_cols = build_train_scores()
    summary = full_score_summary(train, score_cols)
    stress, stress_summary = stress_eval(train, score_cols)
    test_ctx = test_context()

    summary.to_csv(SUMMARY_OUT, index=False)
    stress.to_csv(STRESS_OUT, index=False)
    stress_summary.to_csv(STRESS_SUMMARY_OUT, index=False)
    test_ctx.to_csv(TEST_CONTEXT_OUT, index=False)
    write_report(summary, stress_summary, test_ctx)

    focus_frac = 34.0 / 250.0
    print("[E248 full train @E247 fraction]")
    print(
        summary[np.isclose(summary["top_frac"], focus_frac)]
        .sort_values("drop_delta_vs_full_per_row")
        [[
            "score",
            "selected_n",
            "auc_harmful",
            "auc_tail20",
            "benefit_spearman_neg",
            "drop_delta_vs_full_per_row",
            "harmful_rate_selected",
            "tail20_rate_selected",
        ]]
        .head(12)
        .round(9)
        .to_string(index=False)
    )
    print("\n[E248 split stress @E247 fraction]")
    print(
        stress_summary[
            np.isclose(stress_summary["top_frac"], focus_frac)
            & stress_summary["mode"].eq("valid_top_frac")
        ]
        .sort_values("drop_delta_mean")
        [[
            "score",
            "drop_delta_mean",
            "drop_delta_std",
            "win_rate",
            "harmful_rate_selected_mean",
            "tail20_rate_selected_mean",
        ]]
        .head(12)
        .round(9)
        .to_string(index=False)
    )
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
