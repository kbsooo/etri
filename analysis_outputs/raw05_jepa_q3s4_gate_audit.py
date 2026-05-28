from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.model_selection import GroupKFold


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

sys.path.insert(0, str(JEPA))
sys.path.insert(0, str(OUT))

import advanced_jepa_experiments as adv  # noqa: E402
import jepa_axis_stack_candidates as stack  # noqa: E402
from hidden_block_latent_audit import (  # noqa: E402
    KEY,
    TARGETS,
    clip,
    expected_delta,
    load_predictions,
    logit,
    sample_block_ids,
    sigmoid,
)
from hidden_block_orthogonal_gate_candidates import raw_axis_latent_q, stable_tag  # noqa: E402
from hidden_block_rate_reconstruction_audit import public_proxy_scores  # noqa: E402
from public_subset_sensitivity_audit import build_masks, ce_matrix  # noqa: E402


Q3S4 = ["Q3", "S4"]
EPS = 1e-5


def ce_loss_matrix(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    pp = clip(p)
    yy = y.astype(np.float64)
    return -(yy * np.log(pp) + (1.0 - yy) * np.log1p(-pp))


def read_analysis_submission(file_name: str) -> pd.DataFrame:
    path = OUT / file_name
    if not path.exists():
        path = JEPA / file_name
    if not path.exists():
        raise FileNotFoundError(file_name)
    return pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def rank01(reference: np.ndarray, values: np.ndarray) -> np.ndarray:
    ref = np.asarray(reference, dtype=np.float64)
    val = np.asarray(values, dtype=np.float64)
    ref = ref[np.isfinite(ref)]
    if ref.size == 0:
        return np.zeros_like(val, dtype=np.float64)
    ordered = np.sort(ref)
    return np.searchsorted(ordered, val, side="right").astype(np.float64) / float(len(ordered))


def add_temporal_context(frame: pd.DataFrame, train: pd.DataFrame | None, sample: pd.DataFrame | None) -> pd.DataFrame:
    out = frame.copy()
    out["subject_id"] = out["subject_id"].astype(str)
    out["dow"] = out["lifelog_date"].dt.dayofweek.astype(float)
    out["dow_sin"] = np.sin(2.0 * np.pi * out["dow"] / 7.0)
    out["dow_cos"] = np.cos(2.0 * np.pi * out["dow"] / 7.0)
    out["is_weekend"] = (out["dow"] >= 5).astype(float)
    out["subject_pos_all"] = out.groupby("subject_id", sort=False).cumcount().astype(float)
    out["subject_count_all"] = out.groupby("subject_id", sort=False)["subject_id"].transform("size").astype(float)
    out["subject_phase_all"] = out["subject_pos_all"] / np.maximum(out["subject_count_all"] - 1.0, 1.0)

    if train is not None:
        out = out.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
        for side, shift in [("prev", 1), ("next", -1)]:
            shifted_date = out.groupby("subject_id", sort=False)["lifelog_date"].shift(shift)
            if side == "prev":
                gap = (out["lifelog_date"] - shifted_date).dt.days
            else:
                gap = (shifted_date - out["lifelog_date"]).dt.days
            out[f"{side}_train_gap_days"] = gap.astype(float)
            for target in TARGETS:
                out[f"{side}_{target}"] = out.groupby("subject_id", sort=False)[target].shift(shift).astype(float)
                out[f"{side}_{target}_same_as_baseguess"] = 0.0
        out["hidden_n_rows"] = 1.0
        out["hidden_block_pos"] = 0.0
        out["hidden_block_phase"] = 0.0
        return out

    assert sample is not None
    train_full = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        ["subject_id", "lifelog_date"]
    ).reset_index(drop=True)
    block_ids = sample_block_ids(train_full, sample)
    block_meta = pd.read_csv(OUT / "hidden_block_posterior_block_summary.csv")
    meta = sample[KEY].copy()
    meta["hidden_block_id"] = block_ids
    meta["hidden_block_pos"] = meta.groupby("hidden_block_id", sort=False).cumcount().astype(float)
    meta["hidden_n_rows"] = meta.groupby("hidden_block_id", sort=False)["hidden_block_id"].transform("size").astype(float)
    meta["hidden_block_phase"] = meta["hidden_block_pos"] / np.maximum(meta["hidden_n_rows"] - 1.0, 1.0)
    keep = ["hidden_block_id", "n_rows", "prev_train_gap_days", "next_train_gap_days"]
    for target in TARGETS:
        keep.extend([f"prev_{target}", f"next_{target}", f"posterior_rate_{target}", f"endpoint_rate_{target}"])
    meta = meta.merge(block_meta[keep], on="hidden_block_id", how="left")
    meta["hidden_n_rows"] = meta["n_rows"].fillna(meta["hidden_n_rows"]).astype(float)
    meta = meta.drop(columns=["n_rows"])
    return out.merge(meta, on=KEY, how="left")


def make_feature_matrices(train_feat: pd.DataFrame, sub_feat: pd.DataFrame, train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str], np.ndarray, np.ndarray]:
    train_aug = add_temporal_context(train_feat, train=train, sample=None)
    sub_aug = add_temporal_context(sub_feat, train=None, sample=sample)

    excluded = set(KEY + TARGETS + ["hidden_block_id"])
    feature_cols = []
    for col in train_aug.columns:
        if col in excluded or col not in sub_aug.columns:
            continue
        tr = pd.to_numeric(train_aug[col], errors="coerce")
        su = pd.to_numeric(sub_aug[col], errors="coerce")
        if tr.notna().sum() >= 80 and (tr.nunique(dropna=True) > 1 or su.nunique(dropna=True) > 1):
            feature_cols.append(col)

    x_train_df = train_aug[feature_cols].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    x_sub_df = sub_aug[feature_cols].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    med = x_train_df.median(numeric_only=True).fillna(0.0)
    x_train = x_train_df.fillna(med).to_numpy(dtype=np.float32)
    x_sub = x_sub_df.fillna(med).to_numpy(dtype=np.float32)
    return train_aug, sub_aug, feature_cols, x_train, x_sub


def reconstruct_raw05() -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, pd.DataFrame, np.ndarray, np.ndarray, dict[str, float]]:
    train, sample, stage2_oof, stage2_sub = adv.read_data()
    raw_train = pd.read_parquet(JEPA / "raw_timeline_jepa_rescue_train_features.parquet")
    raw_sub = pd.read_parquet(JEPA / "raw_timeline_jepa_rescue_submission_features.parquet")
    raw05_oof, raw05_sub_fit = stack.candidate_from_ops(
        "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
        raw_train,
        raw_sub,
        stage2_oof,
        stage2_sub,
    )
    raw05_disk = read_analysis_submission("submission_raw_timeline_jepa_rescue_strict_scale0p5.csv")
    raw05_sub = raw05_disk[TARGETS].to_numpy(dtype=np.float64)
    stats = {
        "subfit_disk_max_abs": float(np.abs(raw05_sub_fit - raw05_sub).max()),
        "subfit_disk_mean_abs": float(np.abs(raw05_sub_fit - raw05_sub).mean()),
    }
    return train, sample, stage2_oof, stage2_sub, raw05_oof, raw05_sub, stats


def fit_gate_models(
    train_aug: pd.DataFrame,
    feature_cols: list[str],
    x_train: np.ndarray,
    x_sub: np.ndarray,
    raw_gain: np.ndarray,
) -> tuple[dict[str, dict[str, np.ndarray]], pd.DataFrame, pd.DataFrame]:
    groups = train_aug["subject_id"].astype(str).to_numpy()
    n_splits = min(5, len(np.unique(groups)))
    splitter = GroupKFold(n_splits=n_splits)
    out: dict[str, dict[str, np.ndarray]] = {}
    importance_rows = []
    summary_rows = []

    for target in Q3S4:
        j = TARGETS.index(target)
        gain = raw_gain[:, j].astype(np.float64)
        win = (gain > 0.0).astype(int)
        reg_oof = np.zeros(len(gain), dtype=np.float64)
        prob_oof = np.zeros(len(gain), dtype=np.float64)

        for fold, (tr_idx, va_idx) in enumerate(splitter.split(x_train, win, groups)):
            reg = ExtraTreesRegressor(
                n_estimators=500,
                max_features=0.55,
                min_samples_leaf=7,
                random_state=270527 + j * 17 + fold,
                n_jobs=-1,
            )
            clf = ExtraTreesClassifier(
                n_estimators=500,
                max_features=0.55,
                min_samples_leaf=7,
                class_weight="balanced",
                random_state=270627 + j * 19 + fold,
                n_jobs=-1,
            )
            reg.fit(x_train[tr_idx], gain[tr_idx])
            reg_oof[va_idx] = reg.predict(x_train[va_idx])
            if len(np.unique(win[tr_idx])) == 1:
                prob_oof[va_idx] = float(win[tr_idx].mean())
            else:
                clf.fit(x_train[tr_idx], win[tr_idx])
                prob_oof[va_idx] = clf.predict_proba(x_train[va_idx])[:, 1]

        reg_final = ExtraTreesRegressor(
            n_estimators=700,
            max_features=0.55,
            min_samples_leaf=6,
            random_state=271527 + j,
            n_jobs=-1,
        )
        clf_final = ExtraTreesClassifier(
            n_estimators=700,
            max_features=0.55,
            min_samples_leaf=6,
            class_weight="balanced",
            random_state=271627 + j,
            n_jobs=-1,
        )
        reg_final.fit(x_train, gain)
        clf_final.fit(x_train, win)
        reg_fit = reg_final.predict(x_train)
        reg_sub = reg_final.predict(x_sub)
        prob_sub = clf_final.predict_proba(x_sub)[:, 1]

        reg_rank_oof = rank01(reg_oof, reg_oof)
        reg_rank_sub = rank01(reg_fit, reg_sub)
        blend_oof = np.clip(0.62 * reg_rank_oof + 0.38 * prob_oof, 0.0, 1.0)
        blend_sub = np.clip(0.62 * reg_rank_sub + 0.38 * prob_sub, 0.0, 1.0)
        out[target] = {
            "gain": gain,
            "win": win.astype(float),
            "reg_oof": reg_oof,
            "prob_oof": prob_oof,
            "reg_rank_oof": reg_rank_oof,
            "blend_oof": blend_oof,
            "reg_sub": reg_sub,
            "prob_sub": prob_sub,
            "reg_rank_sub": reg_rank_sub,
            "blend_sub": blend_sub,
        }

        for name, importances in [
            ("regressor", reg_final.feature_importances_),
            ("classifier", clf_final.feature_importances_),
        ]:
            order = np.argsort(importances)[::-1][:80]
            for rank, idx in enumerate(order, start=1):
                importance_rows.append(
                    {
                        "target": target,
                        "model": name,
                        "rank": rank,
                        "feature": feature_cols[idx],
                        "importance": float(importances[idx]),
                    }
                )
        summary_rows.append(
            {
                "target": target,
                "raw_gain_mean": float(gain.mean()),
                "raw_win_rate": float((gain > 0).mean()),
                "reg_oof_corr_gain": float(np.corrcoef(reg_oof, gain)[0, 1]),
                "prob_oof_win_auc_proxy": float(prob_oof[win == 1].mean() - prob_oof[win == 0].mean()),
                "blend_oof_top30_gain": float(gain[blend_oof >= np.quantile(blend_oof, 0.70)].mean()),
                "blend_oof_bottom30_gain": float(gain[blend_oof <= np.quantile(blend_oof, 0.30)].mean()),
            }
        )
    return out, pd.DataFrame(summary_rows), pd.DataFrame(importance_rows)


def make_gate_matrix(gates: dict[str, dict[str, np.ndarray]], kind: str, target_set: list[str], split: str) -> np.ndarray:
    n = len(next(iter(gates.values()))["blend_oof" if split == "train" else "blend_sub"])
    mat = np.zeros((n, len(TARGETS)), dtype=np.float64)
    suffix = "oof" if split == "train" else "sub"
    for target in target_set:
        key = f"{kind}_{suffix}"
        if kind == "all":
            score = np.ones(n, dtype=np.float64)
        elif kind.startswith("hard"):
            base_key = "blend_oof" if split == "train" else "blend_sub"
            score0 = gates[target][base_key]
            q = float(kind.removeprefix("hard")) / 100.0
            train_scores = gates[target]["blend_oof"]
            cutoff = float(np.quantile(train_scores, q))
            score = (score0 >= cutoff).astype(np.float64)
        else:
            score = gates[target][key]
        mat[:, TARGETS.index(target)] = np.clip(score, 0.0, 1.0)
    return mat


def evaluate_oof_variants(
    y: np.ndarray,
    stage2_oof: np.ndarray,
    raw05_oof: np.ndarray,
    gates: dict[str, dict[str, np.ndarray]],
) -> pd.DataFrame:
    base_loss = ce_loss_matrix(y, stage2_oof)
    raw_move = logit(raw05_oof) - logit(stage2_oof)
    target_sets = {
        "Q3": ["Q3"],
        "S4": ["S4"],
        "Q3S4": ["Q3", "S4"],
    }
    gate_kinds = ["all", "reg_rank", "prob", "blend", "hard50", "hard65", "hard80"]
    rows = []
    for set_name, targets in target_sets.items():
        for gate_kind in gate_kinds:
            gate = make_gate_matrix(gates, gate_kind, targets, "train")
            for scale in [0.15, 0.25, 0.35, 0.50, 0.75, 1.00, 1.25]:
                pred = sigmoid(logit(stage2_oof) + scale * gate * raw_move)
                loss = ce_loss_matrix(y, pred)
                rec = {
                    "target_set": set_name,
                    "gate_kind": gate_kind,
                    "scale": scale,
                    "mean_loss": float(loss.mean()),
                    "delta_vs_stage2": float(loss.mean() - base_loss.mean()),
                    "q3_delta": float(loss[:, TARGETS.index("Q3")].mean() - base_loss[:, TARGETS.index("Q3")].mean()),
                    "s4_delta": float(loss[:, TARGETS.index("S4")].mean() - base_loss[:, TARGETS.index("S4")].mean()),
                    "moved_cell_frac": float((gate[:, [TARGETS.index(t) for t in targets]] > 0).mean()),
                    "mean_gate": float(gate[:, [TARGETS.index(t) for t in targets]].mean()),
                }
                rows.append(rec)
    return pd.DataFrame(rows).sort_values(["delta_vs_stage2", "q3_delta", "s4_delta"]).reset_index(drop=True)


def expand_hidden_posterior(train: pd.DataFrame, sample: pd.DataFrame) -> np.ndarray:
    block_ids = sample_block_ids(train, sample)
    block_df = pd.read_csv(OUT / "hidden_block_posterior_block_summary.csv").set_index("hidden_block_id")
    posterior = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
    for i, block_id in enumerate(block_ids):
        for j, target in enumerate(TARGETS):
            posterior[i, j] = float(block_df.loc[block_id, f"posterior_rate_{target}"])
    return clip(posterior)


def candidate_base_sources() -> list[str]:
    sources = [
        "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv",
        "submission_hiddenblock_seqmotif_neutral_ebf79910.csv",
        "submission_hiddenblock_seqmotif_neutral_d0ca7647.csv",
        "submission_hiddenblock_paretomix_w0.4_507296eb.csv",
        "submission_hiddenblock_rateprobe_neutral_605de284.csv",
        "submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv",
    ]
    return [f for f in sources if (OUT / f).exists()]


def make_filter_matrix(
    name: str,
    target_set: list[str],
    stage2_sub: np.ndarray,
    raw05_sub: np.ndarray,
    raw_q: np.ndarray,
    posterior: np.ndarray,
) -> np.ndarray:
    filt = np.ones_like(stage2_sub, dtype=np.float64)
    raw_ce_delta = (
        raw_q * (np.log(clip(stage2_sub)) - np.log(clip(raw05_sub)))
        + (1.0 - raw_q) * (np.log1p(-clip(stage2_sub)) - np.log1p(-clip(raw05_sub)))
    )
    raw_move = logit(raw05_sub) - logit(stage2_sub)
    post_move = logit(posterior) - logit(stage2_sub)
    for target in target_set:
        j = TARGETS.index(target)
        if name == "plain":
            factor = np.ones(len(stage2_sub), dtype=np.float64)
        elif name == "rawq_good":
            factor = np.where(raw_ce_delta[:, j] <= 0.0, 1.0, 0.10)
        elif name == "rawq_strong":
            cutoff = float(np.quantile(raw_ce_delta[:, j], 0.35))
            factor = np.where(raw_ce_delta[:, j] <= cutoff, 1.0, 0.08)
        elif name == "posterior_agree":
            factor = np.where(np.sign(raw_move[:, j]) == np.sign(post_move[:, j]), 1.0, 0.18)
        elif name == "rawq_post_agree":
            factor = np.where((raw_ce_delta[:, j] <= 0.0) & (np.sign(raw_move[:, j]) == np.sign(post_move[:, j])), 1.0, 0.06)
        else:
            raise ValueError(name)
        filt[:, j] = factor
    return filt


def emit_candidates(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    stage2_sub_df: pd.DataFrame,
    stage2_sub: np.ndarray,
    raw05_sub: np.ndarray,
    gates: dict[str, dict[str, np.ndarray]],
    oof_variants: pd.DataFrame,
) -> tuple[list[str], pd.DataFrame]:
    frames, preds = load_predictions()
    raw_q = raw_axis_latent_q(preds["stage2"], preds["raw05"])
    posterior = expand_hidden_posterior(train, sample)
    raw_residual = logit(raw05_sub) - logit(stage2_sub)
    base_sources = candidate_base_sources()
    top_variants = oof_variants[oof_variants["delta_vs_stage2"].lt(0)].head(18)
    if top_variants.empty:
        top_variants = oof_variants.head(12)
    filters = ["plain", "rawq_good", "rawq_strong", "posterior_agree", "rawq_post_agree"]

    records = []
    saved: list[str] = []
    for base_file in base_sources:
        base_df = read_analysis_submission(base_file)
        base_pred = base_df[TARGETS].to_numpy(dtype=np.float64)
        for row in top_variants.itertuples(index=False):
            target_set = str(row.target_set)
            targets = ["Q3", "S4"] if target_set == "Q3S4" else [target_set]
            gate = make_gate_matrix(gates, str(row.gate_kind), targets, "submission")
            for filter_name in filters:
                filt = make_filter_matrix(filter_name, targets, stage2_sub, raw05_sub, raw_q, posterior)
                weight = np.clip(float(row.scale) * gate * filt, 0.0, 1.35)
                cand = base_pred.copy()
                target_mask = np.zeros_like(cand, dtype=bool)
                for target in targets:
                    target_mask[:, TARGETS.index(target)] = True
                cand[target_mask] = sigmoid(logit(base_pred)[target_mask] + (weight * raw_residual)[target_mask])
                if np.abs(cand - base_pred).mean() < 1e-7:
                    continue
                tag_text = f"{base_file}|{target_set}|{row.gate_kind}|{row.scale}|{filter_name}"
                name = f"submission_raw05_jepa_q3s4gate_{stable_tag(tag_text)}.csv"
                out = base_df.copy()
                out[TARGETS] = clip(cand)
                out.to_csv(OUT / name, index=False)
                saved.append(name)
                records.append(
                    {
                        "file": name,
                        "base_source": base_file,
                        "target_set": target_set,
                        "gate_kind": str(row.gate_kind),
                        "scale": float(row.scale),
                        "filter": filter_name,
                        "oof_delta_vs_stage2_from_stage2": float(row.delta_vs_stage2),
                        "oof_q3_delta_from_stage2": float(row.q3_delta),
                        "oof_s4_delta_from_stage2": float(row.s4_delta),
                        "mean_abs_move_vs_base": float(np.abs(cand - base_pred).mean()),
                        "mean_weight_on_targets": float(weight[target_mask].mean()),
                        "active_target_cell_frac": float((weight[target_mask] > 0.01).mean()),
                    }
                )

    return saved, pd.DataFrame(records)


def integrity(files: list[str], reference: pd.DataFrame) -> pd.DataFrame:
    rows = []
    ref_key = reference[KEY].reset_index(drop=True)
    for f in files:
        df = read_analysis_submission(f)
        pred = df[TARGETS].to_numpy(dtype=np.float64)
        rows.append(
            {
                "file": f,
                "rows": len(df),
                "key_match": bool(df[KEY].reset_index(drop=True).equals(ref_key)),
                "duplicate_keys": int(df.duplicated(KEY).sum()),
                "null_predictions": int(df[TARGETS].isna().sum().sum()),
                "min_prob": float(np.nanmin(pred)),
                "max_prob": float(np.nanmax(pred)),
            }
        )
    return pd.DataFrame(rows)


def focused_scenario_scores(files: list[str]) -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    masks = [m for m in build_masks(sample) if m["mask_kind"] != "all"]
    w = np.zeros((len(masks), len(sample)), dtype=np.float64)
    for i, rec in enumerate(masks):
        mask = rec["mask"]
        assert isinstance(mask, np.ndarray)
        w[i, mask] = 1.0 / float(mask.sum())

    refs = [
        "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        "submission_public_entropyproj_public2d0_g100.csv",
        "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
        "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv",
        "submission_hiddenblock_seqmotif_neutral_ebf79910.csv",
    ]
    eval_files = []
    for f in refs + files:
        if f not in eval_files and ((OUT / f).exists() or (JEPA / f).exists()):
            eval_files.append(f)

    q_files = [
        "submission_public_entropyproj_public2d0_g050.csv",
        "submission_public_entropyproj_public2d0_g075.csv",
        "submission_public_entropyproj_public2d0_g100.csv",
        "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv",
        "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
        "submission_public_entropytm_public2d0_q1_q3_s3_s4_g075.csv",
    ]
    q_files = [f for f in q_files if (OUT / f).exists()]
    pred = {f: read_analysis_submission(f)[TARGETS].to_numpy(dtype=np.float64) for f in eval_files}
    detail_rows = []
    for q_file in q_files:
        q = read_analysis_submission(q_file)[TARGETS].to_numpy(dtype=np.float64)
        scores_by_file = {}
        for f, p in pred.items():
            row_loss = ce_matrix(q, p).mean(axis=1)
            scores_by_file[f] = w @ row_loss
        stacked = np.vstack([scores_by_file[f] for f in eval_files])
        best = stacked.min(axis=0)
        for f in eval_files:
            scores = scores_by_file[f]
            regret = scores - best
            detail_rows.append(
                {
                    "file": f,
                    "q_scenario": q_file,
                    "mean_expected": float(scores.mean()),
                    "p90_expected": float(np.quantile(scores, 0.90)),
                    "mean_regret": float(regret.mean()),
                    "p90_regret": float(np.quantile(regret, 0.90)),
                    "p95_regret": float(np.quantile(regret, 0.95)),
                    "max_regret": float(regret.max()),
                }
            )
    detail = pd.DataFrame(detail_rows)
    if detail.empty:
        return detail
    summary = (
        detail.groupby("file")
        .agg(
            scenarios=("q_scenario", "nunique"),
            mean_expected=("mean_expected", "mean"),
            p90_expected=("p90_expected", "mean"),
            mean_regret=("mean_regret", "mean"),
            p90_regret=("p90_regret", "mean"),
            p95_regret=("p95_regret", "mean"),
            max_regret=("max_regret", "max"),
        )
        .reset_index()
    )
    summary["focused_scenario_score"] = (
        summary["mean_expected"]
        + 2.0 * summary["mean_regret"]
        + summary["p90_regret"]
        + 0.25 * summary["p95_regret"]
    )
    return summary.sort_values(["focused_scenario_score", "mean_expected"]).reset_index(drop=True)


def main() -> None:
    train, sample, stage2_oof, stage2_sub_df, raw05_oof, raw05_sub, raw_recon_stats = reconstruct_raw05()
    y = train[TARGETS].to_numpy(dtype=int)
    stage2_sub = stage2_sub_df[TARGETS].to_numpy(dtype=np.float64)
    raw_train = pd.read_parquet(JEPA / "raw_timeline_jepa_rescue_train_features.parquet")
    raw_sub = pd.read_parquet(JEPA / "raw_timeline_jepa_rescue_submission_features.parquet")
    train_aug, sub_aug, feature_cols, x_train, x_sub = make_feature_matrices(raw_train, raw_sub, train, sample)

    stage2_loss = ce_loss_matrix(y, stage2_oof)
    raw05_loss = ce_loss_matrix(y, raw05_oof)
    raw_gain = stage2_loss - raw05_loss
    target_summary = []
    for j, target in enumerate(TARGETS):
        target_summary.append(
            {
                "target": target,
                "stage2_loss": float(stage2_loss[:, j].mean()),
                "raw05_loss": float(raw05_loss[:, j].mean()),
                "raw05_delta_vs_stage2": float(raw05_loss[:, j].mean() - stage2_loss[:, j].mean()),
                "raw05_win_rate": float((raw_gain[:, j] > 0).mean()),
                "raw05_gain_mean": float(raw_gain[:, j].mean()),
                "raw05_gain_p90": float(np.quantile(raw_gain[:, j], 0.90)),
                "raw05_loss_hurt_p90": float(np.quantile(-raw_gain[:, j], 0.90)),
            }
        )
    target_summary_df = pd.DataFrame(target_summary)
    target_summary_df.to_csv(OUT / "raw05_jepa_q3s4_gate_train_target_summary.csv", index=False)

    gates, gate_summary, importances = fit_gate_models(train_aug, feature_cols, x_train, x_sub, raw_gain)
    gate_summary.to_csv(OUT / "raw05_jepa_q3s4_gate_model_summary.csv", index=False)
    importances.to_csv(OUT / "raw05_jepa_q3s4_gate_feature_importance.csv", index=False)

    oof_variants = evaluate_oof_variants(y, stage2_oof, raw05_oof, gates)
    oof_variants.to_csv(OUT / "raw05_jepa_q3s4_gate_oof_variants.csv", index=False)

    saved, meta = emit_candidates(train, sample, stage2_sub_df, stage2_sub, raw05_sub, gates, oof_variants)
    if saved:
        proxy = public_proxy_scores(saved)
        integ = integrity(saved, stage2_sub_df)
        scenario = focused_scenario_scores(saved)
        scores = meta.merge(proxy, on="file", how="left").merge(integ, on="file", how="left")
        if not scenario.empty:
            scores = scores.merge(scenario, on="file", how="left")
        scores = scores.sort_values(
            [
                "delta_vs_raw05_rawaxis",
                "posterior_expected_public_vs_anchor",
                "focused_scenario_score" if "focused_scenario_score" in scores.columns else "raw_axis_expected_public_vs_stage2",
            ],
            na_position="last",
        ).reset_index(drop=True)
        scores.to_csv(OUT / "raw05_jepa_q3s4_gate_candidate_scores.csv", index=False)
        scenario.to_csv(OUT / "raw05_jepa_q3s4_gate_focused_scenario_scores.csv", index=False)
        integ.to_csv(OUT / "raw05_jepa_q3s4_gate_integrity.csv", index=False)
    else:
        scores = pd.DataFrame()

    lines = [
        "# Raw05 JEPA Q3/S4 Gate Audit",
        "",
        "Goal: connect the public-winning raw05 axis to JEPA-style context-to-target latent prediction residuals, then project the resulting Q3/S4 gate onto hidden/test blocks.",
        "",
        "## Raw05 reconstruction",
        "",
        "```csv",
        pd.DataFrame([raw_recon_stats]).round(12).to_csv(index=False).strip(),
        "```",
        "",
        "## Target-level raw05 OOF effect",
        "",
        "```csv",
        target_summary_df.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Gate model summary",
        "",
        "```csv",
        gate_summary.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Best OOF gate variants",
        "",
        "```csv",
        oof_variants.head(30).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Top JEPA features",
        "",
        "```csv",
        importances.head(40).round(10).to_csv(index=False).strip(),
        "```",
    ]
    if not scores.empty:
        cols = [
            "file",
            "base_source",
            "target_set",
            "gate_kind",
            "scale",
            "filter",
            "delta_vs_raw05_rawaxis",
            "raw_axis_expected_public_vs_stage2",
            "posterior_expected_public_vs_anchor",
            "focused_scenario_score",
            "mean_abs_move_vs_base",
        ]
        cols = [c for c in cols if c in scores.columns]
        lines.extend(
            [
                "",
                "## Top candidate scores",
                "",
                "```csv",
                scores[cols].head(40).round(10).to_csv(index=False).strip(),
                "```",
            ]
        )
    (OUT / "raw05_jepa_q3s4_gate_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("[raw05 jepa q3s4 gate] features", len(feature_cols), "candidates", len(saved))
    print(target_summary_df.round(8).to_string(index=False))
    print(gate_summary.round(8).to_string(index=False))
    print(oof_variants.head(12).round(9).to_string(index=False))
    if not scores.empty:
        show_cols = [
            "file",
            "base_source",
            "target_set",
            "gate_kind",
            "scale",
            "filter",
            "delta_vs_raw05_rawaxis",
            "posterior_expected_public_vs_anchor",
            "focused_scenario_score",
        ]
        show_cols = [c for c in show_cols if c in scores.columns]
        print(scores[show_cols].head(20).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
