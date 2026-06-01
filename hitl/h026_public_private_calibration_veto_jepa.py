from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h026_public_private_calibration_veto_jepa"
ANALYSIS = ROOT / "analysis_outputs"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H012_LB = 0.5681234831


@dataclass(frozen=True)
class Runtime:
    h024: object
    h025: object
    h012: pd.DataFrame
    h012_prob: np.ndarray
    sample: pd.DataFrame
    test_pcs: np.ndarray
    action_model: object
    action_cols: list[str]
    train_actions: pd.DataFrame
    train_abs_delta_p95: float


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def robust_z(x: pd.Series | np.ndarray) -> np.ndarray:
    arr = np.asarray(x, dtype=np.float64)
    med = np.nanmedian(arr)
    mad = np.nanmedian(np.abs(arr - med))
    scale = 1.4826 * mad if mad > 1.0e-12 else np.nanstd(arr)
    if not np.isfinite(scale) or scale < 1.0e-12:
        scale = 1.0
    return np.nan_to_num((arr - med) / scale)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def safe_id(text: str, limit: int = 72) -> str:
    chars = []
    for ch in str(text):
        chars.append(ch if ch.isalnum() or ch in "._-" else "_")
    return "".join(chars).strip("_")[:limit].strip("_")


def short_hash(arr: np.ndarray) -> str:
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def prepare_runtime() -> Runtime:
    h024 = import_module(HITL / "h024_action_health_decoder_jepa.py", "h024_action_health_decoder_jepa")
    h025 = import_module(HITL / "h025_train_counterfactual_action_health_jepa.py", "h025_train_counterfactual_action_health_jepa")

    features = pd.read_csv(h025.FEATURES_IN, parse_dates=["sleep_date", "lifelog_date"])
    features = features.sort_values(["split", "subject_id", "sleep_date", "lifelog_date"]).reset_index(drop=True)
    train_mask = features["split"].eq("train").to_numpy()
    test_mask = features["split"].eq("test").to_numpy()
    train_idx = np.flatnonzero(train_mask)
    test_idx = np.flatnonzero(test_mask)
    train = features.iloc[train_idx].reset_index(drop=True)
    test = features.iloc[test_idx].reset_index(drop=True)
    train_y = train[TARGETS].to_numpy(dtype=np.float64)

    groups = h025.feature_groups(features)
    z_by_group = {name: h025.standardized_matrix(features, cols, train_mask) for name, cols in groups.items()}
    z_all = z_by_group["all"]
    pca = PCA(n_components=16, random_state=2626)
    pcs_all = pca.fit_transform(z_all[train_idx])
    pcs_test = pca.transform(z_all[test_idx])
    folds = h025.make_subject_time_folds(train, n_folds=5)

    actions_path = h025.OUT / "h025_train_counterfactual_actions.csv"
    if actions_path.exists():
        actions = pd.read_csv(actions_path)
    else:
        base_oof, _, _ = h025.fit_oof_base(z_all, train_idx, test_idx, train_y, folds)
        proposals_train, _, _ = h025.build_proposals(features, z_by_group, train_idx, test_idx, train_y, folds)
        actions = h025.build_action_training_set(pcs_all, base_oof, proposals_train, train_y, folds)
    cols = h025.action_feature_cols(actions)
    model = h025.fit_action_model(actions[cols], actions["actual_gain"].to_numpy(dtype=np.float64), seed=9026)

    h012 = h025.load_sub(H012)
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    sample = h012[KEYS].copy()
    test_pcs_df = test[KEYS].copy()
    for j in range(pcs_test.shape[1]):
        test_pcs_df[f"pc{j:02d}"] = pcs_test[:, j]
    test_pcs_df = sample.merge(test_pcs_df, on=KEYS, how="left")
    pc_cols = [f"pc{j:02d}" for j in range(pcs_test.shape[1])]
    if test_pcs_df[pc_cols].isna().any().any():
        raise ValueError("test PCA rows do not align to H012 sample")
    train_abs_delta_p95 = float(np.quantile(actions["abs_delta_logit"].to_numpy(dtype=np.float64), 0.95))
    return Runtime(
        h024=h024,
        h025=h025,
        h012=h012,
        h012_prob=h012_prob,
        sample=sample,
        test_pcs=test_pcs_df[pc_cols].to_numpy(dtype=np.float64),
        action_model=model,
        action_cols=cols,
        train_actions=actions,
        train_abs_delta_p95=train_abs_delta_p95,
    )


def enrich_source_scores(rt: Runtime) -> tuple[pd.DataFrame, pd.DataFrame]:
    pool = rt.h025.collect_candidate_pool()
    scores, _ = rt.h025.score_candidates(
        rt.action_model,
        rt.action_cols,
        pool,
        rt.h012_prob,
        rt.test_pcs,
        rt.sample,
        rt.train_actions,
    )
    known = rt.h024.read_public_observations()[["file", "public_lb"]]
    scores = scores.merge(known, on="file", how="left")
    scores["is_known_public"] = scores["public_lb"].notna()
    bad_name = scores["file"].str.contains("q2_w0p45|residual_probe|lejepa|h010|e323|e216|e267", case=False, regex=True)
    scores["is_known_bad_shortcut"] = scores["is_known_public"] & (
        (scores["public_lb"].fillna(0.0) >= 0.5770) | bad_name
    )
    for col, default in [
        ("h024_pred_public_median", 0.578),
        ("h024_pred_public_p90", 0.580),
        ("h024_support_better_than_h012", 0.0),
        ("h024_bad_to_good_load_ratio", 4.0),
        ("pred_gain_top1200_sum", 0.0),
        ("ood_abs_delta_rate", 0.0),
        ("max_abs_delta_prob", 0.0),
        ("mean_abs_delta_prob", 0.0),
    ]:
        if col not in scores.columns:
            scores[col] = default
        scores[col] = scores[col].fillna(default)

    z_gain = robust_z(scores["pred_gain_top1200_sum"])
    z_public = robust_z(-(scores["h024_pred_public_median"] - H012_LB))
    z_support = robust_z(scores["h024_support_better_than_h012"])
    z_bad = robust_z(scores["h024_bad_to_good_load_ratio"])
    z_ood = robust_z(scores["ood_abs_delta_rate"])
    z_max = robust_z(scores["max_abs_delta_prob"])
    scores["h026_source_score"] = (
        0.75 * z_gain
        + 1.10 * z_public
        + 0.65 * z_support
        - 0.90 * z_bad
        - 0.35 * z_ood
        - 0.20 * z_max
        - 1.25 * scores["is_known_bad_shortcut"].astype(float)
    )
    known_scored = scores[scores["is_known_public"]].copy().sort_values("h026_source_score", ascending=False)
    return scores.sort_values("h026_source_score", ascending=False).reset_index(drop=True), known_scored.reset_index(drop=True)


def anchor_dirs(rt: Runtime) -> dict[str, list[np.ndarray]]:
    bad_files = [
        "submission_h010_objective_s1s4_v2_uploadsafe.csv",
        "submission_e323_5508f966_uploadsafe.csv",
        "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
        "submission_e267_humansocial_tail_balanced_2936100f.csv",
        "submission_jepa_latent_q2_w0p45.csv",
        "submission_jepa_latent_residual_probe.csv",
        "submission_lejepa_targetwise_strict_best_scale0p5.csv",
    ]
    good_files = [
        "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv",
        "submission_e95_hardtail_541e3973.csv",
        "submission_mixmin_0c916bb4.csv",
        "submission_e101_q2s3tail_177569bc.csv",
    ]
    base_logit = logit(rt.h012_prob)
    out = {"bad": [], "good": []}
    for label, files in [("bad", bad_files), ("good", good_files)]:
        for file_name in files:
            path = rt.h025.locate(file_name)
            if path is None:
                continue
            arr = rt.h025.load_sub(path, rt.sample)[TARGETS].to_numpy(dtype=np.float64)
            out[label].append(logit(arr) - base_logit)
    return out


def cell_energy(move_logit: np.ndarray, dirs: list[np.ndarray]) -> np.ndarray:
    if not dirs:
        return np.zeros_like(move_logit, dtype=np.float64)
    energy = np.zeros_like(move_logit, dtype=np.float64)
    for direction in dirs:
        scale = float(np.quantile(np.abs(direction), 0.95))
        scale = scale if scale > 1.0e-12 else 1.0
        energy += np.maximum(0.0, move_logit * direction / scale)
    return energy / max(len(dirs), 1)


def variant_cell_frame(rt: Runtime, candidate_path: str | Path, dirs: dict[str, list[np.ndarray]]) -> pd.DataFrame:
    feat, q = rt.h025.candidate_action_features(candidate_path, rt.h012_prob, rt.test_pcs, rt.sample)
    pred_gain = rt.action_model.predict(feat[rt.action_cols])
    cand_logit = logit(q)
    base_logit = logit(rt.h012_prob)
    move = cand_logit - base_logit
    bad = cell_energy(move, dirs["bad"]).reshape(-1)
    good = cell_energy(move, dirs["good"]).reshape(-1)
    frame = feat[["row_id", "target", "target_i", "delta_prob", "abs_delta_prob", "delta_logit", "abs_delta_logit"]].copy()
    frame["pred_gain"] = pred_gain
    frame["public_bad_energy"] = bad
    frame["public_good_energy"] = good
    frame["q2_shortcut"] = frame["target"].eq("Q2").astype(float) * np.maximum(frame["public_bad_energy"], 0.0)
    frame["moved"] = frame["abs_delta_prob"].to_numpy(dtype=np.float64) > 1.0e-6
    return frame


def write_submission(rt: Runtime, source_path: str | Path, selected: pd.DataFrame, alpha: float, out_path: Path) -> dict[str, float]:
    cand = rt.h025.load_sub(source_path, rt.sample)
    cand_prob = cand[TARGETS].to_numpy(dtype=np.float64)
    base_logit = logit(rt.h012_prob)
    cand_logit = logit(cand_prob)
    out_logit = base_logit.copy()
    for rec in selected.to_dict("records"):
        out_logit[int(rec["row_id"]), int(rec["target_i"])] = base_logit[int(rec["row_id"]), int(rec["target_i"])] + alpha * (
            cand_logit[int(rec["row_id"]), int(rec["target_i"])] - base_logit[int(rec["row_id"]), int(rec["target_i"])]
        )
    out = rt.h012.copy()
    out[TARGETS] = sigmoid(out_logit)
    out[TARGETS] = out[TARGETS].clip(EPS, 1.0 - EPS)
    out.to_csv(out_path, index=False)
    return {
        "mean_abs_delta_prob": float(np.mean(np.abs(out[TARGETS].to_numpy(dtype=np.float64) - rt.h012_prob))),
        "max_abs_delta_prob": float(np.max(np.abs(out[TARGETS].to_numpy(dtype=np.float64) - rt.h012_prob))),
        "changed_cells": int(np.sum(np.abs(out[TARGETS].to_numpy(dtype=np.float64) - rt.h012_prob) > 1.0e-6)),
        "changed_rows": int(np.sum(np.max(np.abs(out[TARGETS].to_numpy(dtype=np.float64) - rt.h012_prob), axis=1) > 1.0e-6)),
    }


def generate_variants(rt: Runtime, source_scores: pd.DataFrame) -> pd.DataFrame:
    dirs = anchor_dirs(rt)
    known_files = set(rt.h024.read_public_observations()["file"])
    unknown = source_scores[~source_scores["file"].isin(known_files)].copy()
    source_candidates = unknown.head(10).copy()
    forced = [
        "submission_h020_joint_vector_world_combined_all_k1750_a1_uploadsafe.csv",
        "submission_h018_hard_label_world_combined_all_k1750_a1_uploadsafe.csv",
        "submission_h015_self_feedback_top_all_k1600_a0.7_uploadsafe.csv",
    ]
    for file_name in forced:
        if file_name in set(source_scores["file"]):
            source_candidates = pd.concat([source_candidates, source_scores[source_scores["file"] == file_name]], ignore_index=True)
    source_candidates = source_candidates.drop_duplicates("resolved_path", keep="first").head(12).reset_index(drop=True)

    rows: list[dict[str, object]] = []
    for source_rank, rec in source_candidates.iterrows():
        source_path = str(rec["resolved_path"])
        source_id = safe_id(Path(str(rec["file"])).stem.replace("submission_", ""))
        cells = variant_cell_frame(rt, source_path, dirs)
        moved = cells[cells["moved"]].copy()
        if moved.empty:
            continue
        for veto_lambda in [0.35, 0.75, 1.25, 2.0]:
            moved["h026_cell_score"] = (
                robust_z(moved["pred_gain"])
                + 0.20 * robust_z(moved["public_good_energy"])
                - veto_lambda * robust_z(moved["public_bad_energy"])
                - 0.55 * robust_z(moved["q2_shortcut"])
                - 0.20 * robust_z(moved["abs_delta_logit"])
            )
            ranked = moved.sort_values("h026_cell_score", ascending=False)
            for top_k in [120, 240, 400, 700, 1000, 1400]:
                if top_k > len(ranked):
                    continue
                selected = ranked.head(top_k).copy()
                if float(selected["pred_gain"].sum()) <= 0:
                    continue
                for alpha in [0.35, 0.55, 0.75, 1.0]:
                    name = f"submission_h026_veto_{source_rank:02d}_k{top_k}_a{str(alpha).replace('.', 'p')}_v{str(veto_lambda).replace('.', 'p')}_{source_id}"
                    out_path = OUT / f"{name}.csv"
                    stats = write_submission(rt, source_path, selected, alpha, out_path)
                    rows.append(
                        {
                            "file": f"hitl/h026_public_private_calibration_veto_jepa/{out_path.name}",
                            "resolved_path": str(out_path),
                            "source_file": rec["file"],
                            "source_rank": int(source_rank),
                            "top_k": int(top_k),
                            "alpha": float(alpha),
                            "veto_lambda": float(veto_lambda),
                            "cell_score_sum": float(selected["h026_cell_score"].sum()),
                            "pred_gain_sum": float(selected["pred_gain"].sum()),
                            "public_bad_energy_mean": float(selected["public_bad_energy"].mean()),
                            "public_good_energy_mean": float(selected["public_good_energy"].mean()),
                            "q2_share": float(np.mean(selected["target"].eq("Q2"))),
                            **stats,
                        }
                    )
    return pd.DataFrame(rows)


def score_variants_with_h024(rt: Runtime, variants: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    known = rt.h024.read_public_observations()
    refs = rt.h024.build_reference_pack()
    known_rows = []
    for rec in known.to_dict("records"):
        known_rows.append({"file": rec["file"], "resolved_path": str(rt.h024.locate(rec["file"]) or rec["file"]), "source": "known_public"})
    var_rows = variants[["file", "resolved_path"]].copy()
    var_rows["source"] = "h026_variant"
    pool = pd.concat([pd.DataFrame(known_rows), var_rows], ignore_index=True)
    features = rt.h024.build_feature_table(pool, refs)
    known_features = known[["file", "public_lb"]].merge(features, on="file", how="inner")
    blocked = {
        "file",
        "resolved_path",
        "source",
        "pool_file",
        "pool_resolved_path",
        "pool_candidate_id",
        "pool_source",
        "pool_source_candidate_id",
        "pool_source_decision",
        "pool_known_public_lb",
        "known_public_lb",
        "public_lb",
    }
    cols = rt.h024.numeric_feature_cols(known_features, blocked)
    cols_by_set = rt.h024.feature_sets(cols)
    model_scores, loo_preds = rt.h024.evaluate_known_models(known_features[["file", "public_lb"]], features, cols_by_set)
    candidate_scores, pred_samples = rt.h024.score_candidates(known_features[["file", "public_lb"]], features, model_scores, cols_by_set)
    scored = variants.merge(candidate_scores, on="file", how="left", suffixes=("", "_h024"))
    scored["h026_variant_score"] = (
        robust_z(scored["pred_gain_sum"])
        - 1.10 * robust_z(scored["public_bad_energy_mean"])
        - 0.45 * robust_z(scored["q2_share"])
        - 1.25 * robust_z(scored["pred_public_median"].fillna(0.58))
        - 0.80 * robust_z((scored["pred_public_p90"] - scored["pred_public_p10"]).fillna(0.01))
        + 0.70 * robust_z(scored["support_better_than_h012"].fillna(0.0))
    )
    return scored.sort_values("h026_variant_score", ascending=False).reset_index(drop=True), model_scores, pred_samples


def selected_stress(rt: Runtime, selected: pd.Series, h024_features: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    rowperm = rt.h025.row_permutation_candidate_stress(
        rt.action_model,
        rt.action_cols,
        str(selected["resolved_path"]),
        rt.h012_prob,
        rt.test_pcs,
        rt.sample,
        n_perm=300,
    )
    known = rt.h024.read_public_observations()
    refs = rt.h024.build_reference_pack()
    pool = pd.DataFrame(
        [{"file": rec["file"], "resolved_path": str(rt.h024.locate(rec["file"]) or rec["file"]), "source": "known_public"} for rec in known.to_dict("records")]
        + [{"file": selected["file"], "resolved_path": selected["resolved_path"], "source": "h026_selected"}]
    )
    features = rt.h024.build_feature_table(pool, refs)
    known_features = known[["file", "public_lb"]].merge(features, on="file", how="inner")
    blocked = {"file", "resolved_path", "source", "public_lb", "known_public_lb"}
    cols = rt.h024.numeric_feature_cols(known_features, blocked)
    cols_by_set = rt.h024.feature_sets(cols)
    public_perm = rt.h024.permutation_stress(known_features[["file", "public_lb"]], features, cols_by_set, str(selected["file"]), n_perm=300)
    return rowperm, public_perm


def decide(scored: pd.DataFrame, known_scored: pd.DataFrame, rowperm: pd.DataFrame, public_perm: pd.DataFrame) -> tuple[str, Path | None]:
    if scored.empty:
        return "no_h026_candidates", None
    selected = scored.iloc[0]
    bad_known_top5 = int(known_scored.head(5)["is_known_bad_shortcut"].sum()) if len(known_scored) else 99
    rowperm_p = 1.0
    if not rowperm.empty:
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
    public_perm_p = 1.0
    if not public_perm.empty:
        real_margin = float(selected["pred_public_median"] - H012_LB)
        public_perm_p = float(np.mean(public_perm["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= real_margin))
    gate = (
        bad_known_top5 == 0
        and rowperm_p <= 0.08
        and public_perm_p <= 0.10
        and float(selected.get("support_better_than_h012", 0.0)) >= 0.25
        and float(selected.get("pred_gain_sum", 0.0)) > 0.0
        and float(selected.get("q2_share", 1.0)) <= 0.30
    )
    if not gate:
        return "diagnostic_only_public_private_veto_not_transfer_safe", None
    source = Path(str(selected["resolved_path"]))
    digest = hashlib.sha1(source.read_bytes()).hexdigest()[:8]
    out = ROOT / f"submission_h026_public_private_veto_{digest}_uploadsafe.csv"
    shutil.copyfile(source, out)
    return "primary_public_private_calibration_veto", out


def write_report(
    source_scores: pd.DataFrame,
    known_scored: pd.DataFrame,
    variants: pd.DataFrame,
    model_scores: pd.DataFrame,
    rowperm: pd.DataFrame,
    public_perm: pd.DataFrame,
    decision: str,
    promoted: Path | None,
) -> None:
    lines = []
    lines.append("# H026 Public/Private Calibration-Veto HS-JEPA\n")
    lines.append("## Question\n")
    lines.append(
        "H025 showed that train-counterfactual action health likes public-bad Q2/residual shortcuts. "
        "H026 asks whether a public/private calibration veto can keep the train-health signal while cutting those shortcut axes.\n"
    )
    lines.append("## Source sanity\n")
    if len(known_scored):
        lines.append("- known public anchors ranked by H026 source score:\n")
        lines.append(md_table(known_scored[["file", "public_lb", "is_known_bad_shortcut", "h026_source_score", "pred_gain_top1200_sum", "h024_pred_public_median", "h024_bad_to_good_load_ratio"]], 12) + "\n")
    lines.append("## Generated variants\n")
    lines.append(f"- generated variants: `{len(variants)}`\n")
    if not variants.empty:
        lines.append(md_table(variants[["file", "source_file", "top_k", "alpha", "veto_lambda", "pred_gain_sum", "public_bad_energy_mean", "q2_share", "pred_public_median", "pred_public_p10", "pred_public_p90", "support_better_than_h012", "h026_variant_score"]], 15) + "\n")
    lines.append("## H024 stress\n")
    if not model_scores.empty:
        top = model_scores.iloc[0]
        lines.append(
            f"- best public decoder in H026 pool: `{top['feature_set']}` alpha `{top['alpha']}`, "
            f"MAE `{top['loo_mae']:.6f}`, Spearman `{top['loo_spearman']:.6f}`, pairwise `{top['loo_pair_acc']:.6f}`\n"
        )
    lines.append("## Selected stress\n")
    if not rowperm.empty:
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
        lines.append(f"- H025 row-permutation p(higher top1200 gain): `{rowperm_p:.9f}`\n")
        lines.append(f"- real top1200 H025 gain: `{float(rowperm['real_top1200_sum'].iloc[0]):.9f}`\n")
    if not public_perm.empty and not variants.empty:
        selected = variants.iloc[0]
        real_margin = float(selected["pred_public_median"] - H012_LB)
        public_perm_p = float(np.mean(public_perm["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= real_margin))
        lines.append(f"- H024 public-score permutation p(lower margin): `{public_perm_p:.9f}`\n")
        lines.append(f"- selected predicted public margin vs H012: `{real_margin:.9f}`\n")
    lines.append("## Decision\n")
    lines.append(f"- decision: `{decision}`\n")
    lines.append(f"- promoted path: `{promoted if promoted is not None else 'none'}`\n")
    lines.append(
        "\nInterpretation: H026 promotes only if train action-health, public-bad shortcut veto, and public/free permutation stresses agree. "
        "If it fails, the live bottleneck is a deeper public/private calibration target rather than a scalar veto on H025.\n"
    )
    (OUT / "h026_report.md").write_text("".join(lines))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rt = prepare_runtime()
    source_scores, known_scored = enrich_source_scores(rt)
    source_scores.to_csv(OUT / "h026_source_scores.csv", index=False)
    known_scored.to_csv(OUT / "h026_known_source_sanity.csv", index=False)

    generated = generate_variants(rt, source_scores)
    generated.to_csv(OUT / "h026_generated_variants_raw.csv", index=False)
    if generated.empty:
        decision, promoted = "no_h026_generated_variants", None
        model_scores = pd.DataFrame()
        rowperm = pd.DataFrame()
        public_perm = pd.DataFrame()
        scored = generated
    else:
        scored, model_scores, pred_samples = score_variants_with_h024(rt, generated)
        scored.to_csv(OUT / "h026_variant_scores.csv", index=False)
        model_scores.to_csv(OUT / "h026_h024_model_scores.csv", index=False)
        pred_samples.to_csv(OUT / "h026_h024_prediction_samples.csv", index=False)
        selected = scored.iloc[0]
        rowperm, public_perm = selected_stress(rt, selected)
        rowperm.to_csv(OUT / "h026_selected_h025_rowperm_stress.csv", index=False)
        public_perm.to_csv(OUT / "h026_selected_h024_public_perm_stress.csv", index=False)
        decision, promoted = decide(scored, known_scored, rowperm, public_perm)
    pd.DataFrame(
        [
            {
                "decision": decision,
                "selected_file": None if generated.empty else scored.iloc[0]["file"],
                "selected_resolved_path": None if generated.empty else scored.iloc[0]["resolved_path"],
                "promoted_path": None if promoted is None else str(promoted),
            }
        ]
    ).to_csv(OUT / "h026_decision.csv", index=False)
    write_report(source_scores, known_scored, scored if not generated.empty else generated, model_scores, rowperm, public_perm, decision, promoted)
    print(pd.read_csv(OUT / "h026_decision.csv").to_string(index=False))
    if not generated.empty:
        print(scored.head(12)[["file", "h026_variant_score", "pred_gain_sum", "public_bad_energy_mean", "q2_share", "pred_public_median", "support_better_than_h012"]].to_string(index=False))


if __name__ == "__main__":
    main()
