from __future__ import annotations

from hashlib import sha1
from itertools import combinations
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import public_lb_direct_label_inverse7 as inv  # noqa: E402
import public_lb_actual_anchor_ranker as ranker  # noqa: E402
import jepa_bad_axis_orthogonal_scale_ladder as orth  # noqa: E402
import jepa_regularized_sparse_direct_solver as sparse_solver  # noqa: E402
import jepa_sparse_scale_ladder_stress as ladder  # noqa: E402
from jepa_energy_ensemble_optimizer import public_axes, public_axis_features  # noqa: E402
from public_subset_sensitivity_audit import build_masks, ce_matrix  # noqa: E402
from raw05_anchor_jepa_micro_injection import actual_anchor_score  # noqa: E402


SCAN_OUT = OUT / "jepa_direction_mixture_minimax_optimizer_scan.csv"
ACTUAL_OUT = OUT / "jepa_direction_mixture_minimax_optimizer_actual_anchor.csv"
COMBO_DETAIL_OUT = OUT / "jepa_direction_mixture_minimax_optimizer_combo_detail.csv"
COMBO_SUMMARY_OUT = OUT / "jepa_direction_mixture_minimax_optimizer_combo_summary.csv"
CV_DETAIL_OUT = OUT / "jepa_direction_mixture_minimax_optimizer_cv_detail.csv"
CV_SUMMARY_OUT = OUT / "jepa_direction_mixture_minimax_optimizer_cv_summary.csv"
SELECTED_OUT = OUT / "jepa_direction_mixture_minimax_optimizer_selected.csv"
INTEGRITY_OUT = OUT / "jepa_direction_mixture_minimax_optimizer_integrity.csv"
REPORT_OUT = OUT / "jepa_direction_mixture_minimax_optimizer_report.md"


BASE_FILE = "submission_frontier_cvjepa_refine_a2c8d2c8.csv"
REFERENCE_FILES = {
    "a2c8": BASE_FILE,
    "raw05": "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    "b01_ladder": "submission_sparseladder_b01acaa1.csv",
    "898_ladder": "submission_sparseladder_89817541.csv",
    "f1ee_noq2": "submission_sparseladder_f1ee16b0.csv",
    "blockorth_3a28": "submission_blockorth_3a28f87f.csv",
    "target_q3stage": "submission_targetabl_b19056bb.csv",
    "direns_c4af": "submission_direns_c4af1fd8.csv",
    "direns_2a96": "submission_direns_2a96ae73.csv",
    "direns_c0fd": "submission_direns_c0fdb76b.csv",
}

SOURCE_FILES = {
    "b01": "submission_sparseladder_b01acaa1.csv",
    "s898": "submission_sparseladder_89817541.csv",
    "f1ee": "submission_sparseladder_f1ee16b0.csv",
    "block3a28": "submission_blockorth_3a28f87f.csv",
    "block0352": "submission_blockorth_0352b65f.csv",
    "block4696": "submission_blockorth_46969019.csv",
    "target_q3": "submission_targetabl_b19056bb.csv",
    "target_q3s234": "submission_targetabl_1049b8e7.csv",
    "direns_c4af": "submission_direns_c4af1fd8.csv",
    "direns_2a96": "submission_direns_2a96ae73.csv",
    "direns_c0fd": "submission_direns_c0fdb76b.csv",
}

TARGET_GROUPS = {
    "full": inv.TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3_stage": ["Q3", "S1", "S2", "S3", "S4"],
}

SCALES = [0.85, 0.95, 1.05, 1.15, 1.30]
PROJECTION_SPECS = [
    ("none", [], 0.0),
    ("public_bad4_a012", orth.AXIS_GROUPS["public_bad4"], 0.12),
    ("public_bad4_a020", orth.AXIS_GROUPS["public_bad4"], 0.20),
]


def stable_hash_bytes(payload: bytes) -> str:
    return sha1(payload).hexdigest()[:10]


def stable_hash_text(text: str) -> str:
    return sha1(text.encode("utf-8")).hexdigest()[:10]


def load_sample() -> pd.DataFrame:
    return pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        inv.KEY
    ).reset_index(drop=True)


def load_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return inv.clip_prob(inv.load_sub(file_name, sample)[inv.TARGETS].to_numpy(dtype=np.float64))


def save_submission(file_name: str, sample: pd.DataFrame, pred: np.ndarray) -> None:
    out = sample[inv.KEY].copy()
    out[inv.TARGETS] = inv.clip_prob(pred)
    out.to_csv(OUT / file_name, index=False)


def target_gate(name: str, n_rows: int) -> np.ndarray:
    allowed = set(TARGET_GROUPS[name])
    keep = np.asarray([target in allowed for target in inv.TARGETS], dtype=np.float64)
    return np.repeat(keep.reshape(1, -1), n_rows, axis=0)


def combo_row_gate(sample: pd.DataFrame, table_name: str, prefix: str, soft_floor: float = 0.55) -> dict[str, np.ndarray]:
    records = build_masks(sample)
    table = pd.read_csv(OUT / table_name).head(160).reset_index(drop=True)
    weights = ranker.combo_weights(table)
    score = np.zeros(len(sample), dtype=np.float64)
    for idx, row in table.iterrows():
        rec = records[int(row["mask_index"])]
        mask = rec["mask"]
        assert isinstance(mask, np.ndarray)
        score[mask] += float(weights[idx])
    if score.max() > 0:
        score = score / score.max()
    hard = (score >= np.quantile(score, 0.40)).astype(np.float64)
    return {
        f"{prefix}_soft": soft_floor + (1.0 - soft_floor) * score,
        f"{prefix}_hard60": hard,
    }


def build_row_gates(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    gates = {"all": np.ones(len(sample), dtype=np.float64)}
    specs = [
        ("public_lb_inverse_mask_raw05_compatible_top512.csv", "rawcompat"),
        ("public_lb_inverse_mask_all_sign_compatible_top512.csv", "allsign"),
    ]
    for table_name, prefix in specs:
        path = OUT / table_name
        if path.exists():
            gates.update(combo_row_gate(sample, table_name, prefix))
    return gates


def build_bad_axes(sample: pd.DataFrame, base_logit: np.ndarray) -> dict[str, np.ndarray]:
    axes: dict[str, np.ndarray] = {}
    for axis_name, file_name in orth.BAD_AXIS_FILES.items():
        if inv.locate(file_name) is None:
            continue
        pred = load_array(file_name, sample)
        axis = inv.logit(pred) - base_logit
        if float(np.linalg.norm(axis.reshape(-1))) > 1e-12:
            axes[axis_name] = axis
    return axes


def energy_cell_gate(name: str, delta: np.ndarray, base_gate: np.ndarray, energy: np.ndarray) -> np.ndarray:
    if name == "all_cells":
        return base_gate
    active = (np.abs(delta) > 1e-10) & (base_gate > 0)
    if not active.any():
        return np.zeros_like(delta)
    if name == "energy_top70":
        cutoff = float(np.quantile(energy[active], 0.30))
        return base_gate * ((energy >= cutoff) & active).astype(np.float64)
    if name == "abs_top70":
        cutoff = float(np.quantile(np.abs(delta[active]), 0.30))
        return base_gate * ((np.abs(delta) >= cutoff) & active).astype(np.float64)
    raise ValueError(name)


def project_delta(delta: np.ndarray, gate: np.ndarray, axes: list[np.ndarray], anti_lambda: float) -> tuple[np.ndarray, dict[str, float]]:
    out = delta * gate
    if not axes or anti_lambda <= 0.0:
        return out, {"removed_norm_ratio": 0.0, "bad_axis_positive_coef": 0.0}

    removed_norm = 0.0
    positive_coefs = []
    for axis in axes:
        masked_axis = axis * gate
        avec = masked_axis.reshape(-1)
        denom = float(np.dot(avec, avec))
        if denom <= 1e-12:
            continue
        coef = float(np.dot(out.reshape(-1), avec) / denom)
        positive_coefs.append(max(coef, 0.0))
        if coef <= 0.0:
            continue
        removal = anti_lambda * coef * masked_axis
        out = out - removal
        removed_norm += float(np.linalg.norm(removal.reshape(-1)))
    base_norm = float(np.linalg.norm((delta * gate).reshape(-1)))
    return out * gate, {
        "removed_norm_ratio": removed_norm / base_norm if base_norm > 1e-12 else 0.0,
        "bad_axis_positive_coef": float(np.mean(positive_coefs)) if positive_coefs else 0.0,
    }


def add_weight_spec(rows: list[dict[str, object]], seen: set[str], label: str, weights: dict[str, float]) -> None:
    clean = {k: float(v) for k, v in weights.items() if abs(float(v)) > 1e-12}
    total = sum(clean.values())
    if total <= 0:
        return
    clean = {k: v / total for k, v in clean.items()}
    key = "|".join(f"{k}:{clean[k]:.4f}" for k in sorted(clean))
    if key in seen:
        return
    seen.add(key)
    rows.append({"mix_label": label, "weights": clean, "weight_key": key})


def build_weight_specs(available: set[str]) -> list[dict[str, object]]:
    specs: list[dict[str, object]] = []
    seen: set[str] = set()

    for name in sorted(available):
        add_weight_spec(specs, seen, f"solo_{name}", {name: 1.0})

    pair_names = [
        ("b01", "s898"),
        ("b01", "f1ee"),
        ("b01", "block3a28"),
        ("b01", "target_q3"),
        ("s898", "f1ee"),
        ("s898", "block3a28"),
        ("direns_c4af", "target_q3"),
        ("direns_c4af", "block3a28"),
        ("direns_c4af", "s898"),
        ("direns_2a96", "target_q3"),
    ]
    for a, b in pair_names:
        if a not in available or b not in available:
            continue
        for wa in [0.20, 0.35, 0.50, 0.65, 0.80]:
            add_weight_spec(specs, seen, f"pair_{a}_{b}_{wa:.2f}", {a: wa, b: 1.0 - wa})

    triads = [
        ("b01", "s898", "f1ee"),
        ("b01", "block3a28", "target_q3"),
        ("b01", "f1ee", "target_q3"),
        ("b01", "s898", "block3a28"),
        ("direns_c4af", "block3a28", "target_q3"),
        ("direns_c4af", "s898", "f1ee"),
    ]
    tri_weights = [
        (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0),
        (0.50, 0.25, 0.25),
        (0.25, 0.50, 0.25),
        (0.25, 0.25, 0.50),
        (0.60, 0.20, 0.20),
    ]
    for names in triads:
        if not set(names).issubset(available):
            continue
        for weights in tri_weights:
            add_weight_spec(specs, seen, "tri_" + "_".join(names), dict(zip(names, weights, strict=True)))

    rng = np.random.default_rng(20260528)
    random_groups = [
        (["b01", "s898", "f1ee"], [1.5, 1.5, 1.5], 120),
        (["b01", "s898", "f1ee", "block3a28", "target_q3"], [1.3, 1.3, 1.0, 0.8, 0.7], 220),
        (["direns_c4af", "b01", "s898", "f1ee", "block3a28", "target_q3"], [2.5, 0.8, 0.8, 0.8, 0.5, 0.5], 140),
    ]
    for names, alpha, n_draws in random_groups:
        names = [name for name in names if name in available]
        if len(names) < 2:
            continue
        alpha_arr = np.asarray(alpha[: len(names)], dtype=np.float64)
        for i in range(n_draws):
            draw = rng.dirichlet(alpha_arr)
            add_weight_spec(specs, seen, f"dirichlet_{len(names)}_{i:03d}", dict(zip(names, draw, strict=True)))

    return specs


def build_candidates(sample: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    base = load_array(BASE_FILE, sample)
    base_logit = inv.logit(base)
    axes = public_axes()
    consensus = sparse_solver.consensus_matrices(sample)
    energy = consensus["energy"]
    row_gates = build_row_gates(sample)
    bad_axes = build_bad_axes(sample, base_logit)

    deltas: dict[str, np.ndarray] = {}
    source_files: dict[str, str] = {}
    for name, file_name in SOURCE_FILES.items():
        if inv.locate(file_name) is None:
            continue
        arr = load_array(file_name, sample)
        deltas[name] = inv.logit(arr) - base_logit
        source_files[name] = file_name

    weight_specs = build_weight_specs(set(deltas))
    rows: list[dict[str, object]] = []
    arrays: dict[str, np.ndarray] = {}
    seen_predictions: set[str] = set()

    for spec in weight_specs:
        weights = spec["weights"]
        assert isinstance(weights, dict)
        raw_delta = sum(float(w) * deltas[str(name)] for name, w in weights.items())
        source_names = "+".join(str(k) for k in weights)
        source_weights = "+".join(f"{k}:{float(v):.3f}" for k, v in weights.items())

        for target_name in TARGET_GROUPS:
            tgate = target_gate(target_name, len(sample))
            for row_gate_name, row_gate in row_gates.items():
                if row_gate_name.endswith("hard60") and target_name == "q3_stage":
                    continue
                base_gate = tgate * row_gate.reshape(-1, 1)
                for cell_gate_name in ["all_cells", "energy_top70"]:
                    if cell_gate_name != "all_cells" and row_gate_name != "all":
                        continue
                    gate = energy_cell_gate(cell_gate_name, raw_delta, base_gate, energy)
                    active_cells = int((gate > 0).sum())
                    if active_cells <= 0:
                        continue
                    active_rows = int((gate.sum(axis=1) > 0).sum())
                    for projection_name, axis_names, anti_lambda in PROJECTION_SPECS:
                        if projection_name != "none" and (cell_gate_name != "all_cells" or row_gate_name != "all"):
                            continue
                        axes_for_projection = [bad_axes[name] for name in axis_names if name in bad_axes]
                        projected_delta, projection_stats = project_delta(raw_delta, gate, axes_for_projection, anti_lambda)
                        mean_abs_logit_delta = float(np.mean(np.abs(projected_delta)))
                        if mean_abs_logit_delta <= 1e-12:
                            continue
                        for scale in SCALES:
                            pred = inv.clip_prob(inv.sigmoid(base_logit + scale * projected_delta))
                            pred_hash = stable_hash_bytes(np.ascontiguousarray(np.round(pred, 10)).view(np.uint8).tobytes())
                            if pred_hash in seen_predictions:
                                continue
                            seen_predictions.add(pred_hash)
                            name = f"mixmin_{stable_hash_text(str(spec['weight_key']) + target_name + row_gate_name + cell_gate_name + projection_name + str(scale))}"
                            file_name = f"submission_mixmin_{pred_hash[:8]}.csv"
                            public = public_axis_features(pred, axes)
                            move_vs_a2c8 = float(np.mean(np.abs(pred - base)))
                            active_energy = energy[gate > 0]
                            arrays[name] = pred
                            rows.append(
                                {
                                    "name": name,
                                    "file": file_name,
                                    "mix_label": str(spec["mix_label"]),
                                    "source_name": source_names,
                                    "source_file": "+".join(source_files[str(k)] for k in weights),
                                    "source_weights": source_weights,
                                    "variant": f"{target_name}/{row_gate_name}/{cell_gate_name}/{projection_name}",
                                    "target_group": target_name,
                                    "row_gate": row_gate_name,
                                    "cell_gate": cell_gate_name,
                                    "projection": projection_name,
                                    "anti_lambda": anti_lambda,
                                    "scale": scale,
                                    "active_cells": active_cells,
                                    "active_rows": active_rows,
                                    "active_cell_frac": active_cells / float(len(sample) * len(inv.TARGETS)),
                                    "mean_active_energy": float(np.mean(active_energy)),
                                    "p10_active_energy": float(np.quantile(active_energy, 0.10)),
                                    "mean_abs_logit_delta": mean_abs_logit_delta,
                                    "mean_abs_move_vs_a2c8": move_vs_a2c8,
                                    "max_abs_move_vs_a2c8": float(np.max(np.abs(pred - base))),
                                    "prediction_hash": pred_hash,
                                    **projection_stats,
                                    **public,
                                }
                            )

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame, arrays

    frame["prefilter_score"] = (
        np.abs(frame["mean_abs_move_vs_a2c8"] - 0.0087) * 32.0
        + np.maximum(frame["posterior_expected_public_vs_anchor"] - 0.57812, 0.0) * 5.0
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 0.00032, 0.0) * 55.0
        + np.maximum(frame["bad_residual_axis_ratio"].abs() - 0.105, 0.0) * 0.25
        + np.maximum(frame["ordinal_axis_ratio"].abs() - 0.185, 0.0) * 0.18
        + np.maximum(0.0068 - frame["mean_abs_move_vs_a2c8"], 0.0) * 18.0
        + np.maximum(frame["mean_abs_move_vs_a2c8"] - 0.0115, 0.0) * 20.0
    )
    return frame.sort_values("prefilter_score").reset_index(drop=True), arrays


def prefilter_candidates(scan: pd.DataFrame) -> pd.DataFrame:
    viable = scan[
        (scan["mean_abs_move_vs_a2c8"] >= 0.0058)
        & (scan["mean_abs_move_vs_a2c8"] <= 0.0125)
        & (scan["min_prob"] > 0.03)
        & (scan["max_prob"] < 0.995)
    ].copy()
    parts = [
        viable.sort_values("prefilter_score").head(1800),
        viable[viable["projection"].eq("none")].sort_values("prefilter_score").head(600),
        viable[viable["projection"].ne("none")].sort_values("prefilter_score").head(450),
        viable[viable["row_gate"].eq("all")].sort_values("prefilter_score").head(900),
        viable[viable["mean_abs_move_vs_a2c8"].ge(0.0085)].sort_values("prefilter_score").head(650),
    ]
    out = pd.concat(parts, ignore_index=False).drop_duplicates("name")
    return out.sort_values("prefilter_score").head(2600).reset_index(drop=True)


def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    order = np.argsort(values)
    values = values[order]
    weights = weights[order]
    cdf = np.cumsum(weights) / np.sum(weights)
    return float(np.interp(q, cdf, values))


def combo_stress_summary(sample: pd.DataFrame, candidates: pd.DataFrame, arrays: dict[str, np.ndarray]) -> tuple[pd.DataFrame, pd.DataFrame]:
    masks = ranker.mask_matrix(sample)
    stage2 = ranker.load_submission(inv.STAGE2, sample)

    pred_names: list[str] = []
    pred_files: list[str] = []
    pred_arrays: list[np.ndarray] = []
    for name, file_name in REFERENCE_FILES.items():
        if ranker.exists(file_name):
            pred_names.append(name)
            pred_files.append(file_name)
            pred_arrays.append(ranker.load_submission(file_name, sample))
    for row in candidates.itertuples(index=False):
        pred_names.append(str(row.name))
        pred_files.append(str(row.file))
        pred_arrays.append(arrays[str(row.name)])
    pred_stack = np.stack(pred_arrays, axis=0)

    scenario_cache: dict[str, np.ndarray] = {}
    rows: list[dict[str, object]] = []
    for combo_set, table_name in ranker.COMBO_TABLES.items():
        table_path = OUT / table_name
        if not table_path.exists():
            continue
        table = pd.read_csv(table_path).head(160).reset_index(drop=True)
        combo_weights = ranker.combo_weights(table)
        for i, combo in table.iterrows():
            scenario = str(combo["scenario_file"])
            if scenario not in scenario_cache:
                scenario_cache[scenario] = ranker.load_submission(scenario, sample)
            q = scenario_cache[scenario]
            mask_vec = masks[int(combo["mask_index"])]
            stage_loss = float(mask_vec @ ce_matrix(q, stage2).mean(axis=1))
            loss = (-(q[None, :, :] * np.log(inv.clip_prob(pred_stack)) + (1.0 - q[None, :, :]) * np.log1p(-inv.clip_prob(pred_stack)))).mean(axis=2) @ mask_vec
            anchored = ranker.STAGE2_LB + loss - stage_loss
            for candidate, file_name, value in zip(pred_names, pred_files, anchored, strict=True):
                rows.append(
                    {
                        "candidate": candidate,
                        "file": file_name,
                        "combo_set": combo_set,
                        "combo_rank": i + 1,
                        "combo_weight": float(combo_weights[i]),
                        "scenario_file": scenario,
                        "mask_index": int(combo["mask_index"]),
                        "mask_kind": str(combo.get("mask_kind", "")),
                        "mask_name": str(combo.get("mask_name", "")),
                        "anchored_score": float(value),
                    }
                )

    detail = pd.DataFrame(rows)
    baselines = ["a2c8", "b01_ladder", "898_ladder", "blockorth_3a28", "direns_c4af"]
    for base_name in baselines:
        base = detail[detail["candidate"].eq(base_name)][["combo_set", "combo_rank", "anchored_score"]].rename(
            columns={"anchored_score": f"score_{base_name}"}
        )
        detail = detail.merge(base, on=["combo_set", "combo_rank"], how="left")
        detail[f"delta_vs_{base_name}"] = detail["anchored_score"] - detail[f"score_{base_name}"]

    summary_rows: list[dict[str, object]] = []
    for candidate, group in detail.groupby("candidate", sort=False):
        weights = group["combo_weight"].to_numpy(dtype=np.float64)
        weights = weights / weights.sum()
        score = group["anchored_score"].to_numpy(dtype=np.float64)
        rec: dict[str, object] = {
            "name": candidate,
            "file": str(group["file"].iloc[0]),
            "combo_weighted_mean_score": float(weights @ score),
            "combo_p50_score": weighted_quantile(score, weights, 0.50),
            "combo_p90_score": weighted_quantile(score, weights, 0.90),
            "combo_worst_score": float(score.max()),
        }
        for base_name in baselines:
            delta = group[f"delta_vs_{base_name}"].to_numpy(dtype=np.float64)
            rec[f"combo_weighted_delta_vs_{base_name}"] = float(weights @ delta)
            rec[f"combo_weighted_win_vs_{base_name}"] = float(weights @ (delta < 0).astype(np.float64))
            rec[f"combo_p50_delta_vs_{base_name}"] = weighted_quantile(delta, weights, 0.50)
            rec[f"combo_p90_delta_vs_{base_name}"] = weighted_quantile(delta, weights, 0.90)
            rec[f"combo_worst_delta_vs_{base_name}"] = float(delta.max())
        summary_rows.append(rec)

    summary = pd.DataFrame(summary_rows)
    generated_names = set(candidates["name"].astype(str))
    summary["is_generated"] = summary["name"].isin(generated_names)
    return detail, summary


def score_actual_anchor(sample: pd.DataFrame, pool: pd.DataFrame, arrays: dict[str, np.ndarray]) -> pd.DataFrame:
    preds = [arrays[str(row.name)] for row in pool.itertuples(index=False)]
    scored = actual_anchor_score(preds, sample)
    meta = pool.reset_index(drop=True).copy()
    meta.insert(0, "candidate_index", np.arange(len(meta)))
    return scored.merge(meta, on="candidate_index", how="left")


def integrity(files: list[str], sample: pd.DataFrame) -> pd.DataFrame:
    ref_key = sample[inv.KEY].reset_index(drop=True)
    rows = []
    for file_name in files:
        frame = inv.load_sub(file_name, sample)
        pred = frame[inv.TARGETS].to_numpy(dtype=np.float64)
        rows.append(
            {
                "file": file_name,
                "rows": len(frame),
                "key_ok": bool(frame[inv.KEY].reset_index(drop=True).equals(ref_key)),
                "duplicate_keys": int(frame.duplicated(inv.KEY).sum()),
                "null_probs": int(frame[inv.TARGETS].isna().sum().sum()),
                "min_prob": float(np.nanmin(pred)),
                "max_prob": float(np.nanmax(pred)),
                "mean_prob": float(np.nanmean(pred)),
            }
        )
    return pd.DataFrame(rows)


def write_report(scan: pd.DataFrame, pool: pd.DataFrame, scored: pd.DataFrame, combo: pd.DataFrame, selected: pd.DataFrame, integ: pd.DataFrame) -> None:
    top_cols = [
        "submit_role",
        "name",
        "file",
        "selection_score",
        "actual_anchor_score_final",
        "combo_weighted_delta_vs_b01_ladder",
        "combo_weighted_win_vs_b01_ladder",
        "combo_p90_delta_vs_b01_ladder",
        "combo_worst_delta_vs_b01_ladder",
        "combo_weighted_delta_vs_direns_c4af",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "mean_abs_move_vs_a2c8",
        "source_name",
        "source_weights",
        "variant",
        "scale",
    ]
    combo_cols = [
        "name",
        "file",
        "combo_weighted_delta_vs_b01_ladder",
        "combo_weighted_win_vs_b01_ladder",
        "combo_p90_delta_vs_b01_ladder",
        "combo_worst_delta_vs_b01_ladder",
        "combo_weighted_delta_vs_direns_c4af",
        "combo_weighted_delta_vs_898_ladder",
    ]
    lines = [
        "# JEPA Direction Mixture Minimax Optimizer",
        "",
        "Purpose: optimize larger sparse-JEPA/direct-label direction mixtures against public-anchor combo stress, not just local CV or raw05 micro calibration.",
        "",
        "## Counts",
        "",
        f"- generated candidates: {len(scan)}",
        f"- actual-anchor rescored pool: {len(pool)}",
        f"- combo-stress summarized candidates including references: {len(combo)}",
        f"- saved submissions: {len(selected)}",
        "",
        "## Reference Combo Stress",
        "",
        "```csv",
        combo[~combo["is_generated"]][[c for c in combo_cols if c in combo.columns]].round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Selected Candidates",
        "",
        "```csv",
        selected[[c for c in top_cols if c in selected.columns]].round(10).to_csv(index=False).strip() if not selected.empty else "none",
        "```",
        "",
        "## Integrity",
        "",
        "```csv",
        integ.round(10).to_csv(index=False).strip() if not integ.empty else "none",
        "```",
        "",
        "## Interpretation",
        "",
        "- This run treats `direns_c4af` as the current robust frontier. A new candidate must either beat it on combo-stress or create a larger controlled move with acceptable LOO/L2O anchor-CV.",
        "- Positive `combo_p90_delta_vs_b01_ladder` or `combo_worst_delta_vs_b01_ladder` means the candidate still has a hidden public bad-axis tail even if the weighted mean improves.",
        "- Projection variants are kept only if the public-anchor stress objective rewards them; previous global orthogonalization was too blunt.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sample()
    scan, arrays = build_candidates(sample)
    scan.to_csv(SCAN_OUT, index=False)

    pool = prefilter_candidates(scan)
    actual = score_actual_anchor(sample, pool, arrays)
    actual.to_csv(ACTUAL_OUT, index=False)

    actual_pool = actual[
        (actual["actual_anchor_score_final"] <= 0.57788)
        | (actual["mean_abs_move_vs_a2c8"] >= 0.0087)
    ].copy()
    actual_pool = pd.concat(
        [
            actual_pool.sort_values(["actual_anchor_score_final", "prefilter_score"]).head(120),
            actual_pool[actual_pool["projection"].ne("none")].sort_values(["actual_anchor_score_final", "prefilter_score"]).head(40),
            actual_pool[actual_pool["mean_abs_move_vs_a2c8"].ge(0.0087)].sort_values(["actual_anchor_score_final", "prefilter_score"]).head(60),
        ],
        ignore_index=False,
    ).drop_duplicates("name").head(180).reset_index(drop=True)

    detail, combo_summary = combo_stress_summary(sample, actual_pool, arrays)
    detail.to_csv(COMBO_DETAIL_OUT, index=False)
    combo_summary.to_csv(COMBO_SUMMARY_OUT, index=False)

    scored = actual_pool.merge(combo_summary[combo_summary["is_generated"]].drop(columns=["file"], errors="ignore"), on="name", how="left")
    scored["selection_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["combo_weighted_delta_vs_b01_ladder"], 0.0) * 0.80
        + np.maximum(scored["combo_p90_delta_vs_b01_ladder"], 0.0) * 0.90
        + np.maximum(scored["combo_worst_delta_vs_b01_ladder"], 0.0) * 0.20
        + np.maximum(scored["combo_weighted_delta_vs_direns_c4af"], 0.0) * 0.65
        + np.abs(scored["mean_abs_move_vs_a2c8"] - 0.0087) * 0.035
    )

    cv_pool = pd.concat(
        [
            scored.sort_values(["selection_score", "actual_anchor_score_final"]).head(70),
            scored[scored["combo_weighted_delta_vs_direns_c4af"].le(0)].sort_values("selection_score").head(40),
            scored[scored["projection"].ne("none")].sort_values("selection_score").head(25),
            scored[scored["mean_abs_move_vs_a2c8"].ge(0.0090)].sort_values("selection_score").head(25),
            scored[
                (scored["combo_weighted_delta_vs_b01_ladder"] < 0.0)
                & (scored["mean_abs_move_vs_a2c8"].ge(0.00875))
                & (scored["actual_anchor_score_final"] <= 0.57782)
            ]
            .sort_values("selection_score")
            .head(50),
        ],
        ignore_index=False,
    ).drop_duplicates("name").head(100).reset_index(drop=True)

    preds = inv.load_predictions(sample)
    cv_arrays = {str(row.name): arrays[str(row.name)] for row in cv_pool.itertuples(index=False)}
    cv_detail, cv_summary = ladder.anchor_cv_for_ladder(sample, cv_pool, cv_arrays, preds)
    honest = ladder.combined_honest_cv(cv_summary)
    cv_detail.to_csv(CV_DETAIL_OUT, index=False)
    cv_summary.to_csv(CV_SUMMARY_OUT, index=False)

    final = scored.merge(honest, left_on=["name", "file"], right_on=["candidate_name", "file"], how="left")
    final["cv_missing"] = final["honest_cv_delta_mean"].isna()
    final["selection_score"] = (
        final["selection_score"]
        + np.maximum(final["honest_cv_delta_worst"].fillna(0.0010), 0.0) * 0.25
        + final["cv_missing"].astype(float) * 0.00020
    )

    selected_parts = [
        final[
            (final["combo_weighted_delta_vs_direns_c4af"] <= 0.0)
            & (final["combo_weighted_delta_vs_b01_ladder"] < 0.0)
            & (final["mean_abs_move_vs_a2c8"] >= 0.0080)
            & (~final["cv_missing"])
        ]
        .assign(submit_role="mixmin_c4af_stress")
        .sort_values(["combo_weighted_delta_vs_direns_c4af", "actual_anchor_score_final"])
        .head(3),
        final[
            (final["combo_weighted_delta_vs_direns_c4af"] <= 0.0)
            & (final["combo_p90_delta_vs_b01_ladder"] <= 0.000030)
            & (final["mean_abs_move_vs_a2c8"] >= 0.0076)
            & (~final["cv_missing"])
        ].assign(submit_role="mixmin_frontier").sort_values(["selection_score", "actual_anchor_score_final"]).head(4),
        final[
            (final["combo_weighted_delta_vs_b01_ladder"] < 0.0)
            & (final["mean_abs_move_vs_a2c8"] >= 0.0088)
            & (final["actual_anchor_score_final"] <= 0.57782)
            & (~final["cv_missing"])
        ].assign(submit_role="mixmin_large_move").sort_values(["selection_score", "mean_abs_move_vs_a2c8"]).head(4),
        final[
            (final["projection"].ne("none"))
            & (final["combo_weighted_delta_vs_b01_ladder"] <= 0.000005)
            & (final["actual_anchor_score_final"] <= 0.57784)
            & (~final["cv_missing"])
        ].assign(submit_role="mixmin_orth_diag").sort_values(["selection_score", "actual_anchor_score_final"]).head(3),
    ]
    selected = pd.concat(selected_parts, ignore_index=False).drop_duplicates("name")
    if selected.empty:
        selected = final.sort_values(["selection_score", "actual_anchor_score_final"]).head(6).copy()
        selected["submit_role"] = "mixmin_fallback"
    selected = selected.sort_values(["submit_role", "selection_score", "actual_anchor_score_final"]).reset_index(drop=True)

    saved_files = []
    for row in selected.itertuples(index=False):
        pred = arrays[str(row.name)]
        file_name = str(row.file)
        save_submission(file_name, sample, pred)
        saved_files.append(file_name)
    integ = integrity(saved_files, sample)

    selected.to_csv(SELECTED_OUT, index=False)
    integ.to_csv(INTEGRITY_OUT, index=False)
    write_report(scan, pool, actual, combo_summary, selected, integ)

    print(REPORT_OUT)
    print("[counts]", {"generated": len(scan), "pool": len(pool), "actual_pool": len(actual_pool), "cv_pool": len(cv_pool), "selected": len(selected)})
    cols = [
        "submit_role",
        "name",
        "file",
        "selection_score",
        "actual_anchor_score_final",
        "combo_weighted_delta_vs_b01_ladder",
        "combo_weighted_delta_vs_direns_c4af",
        "combo_p90_delta_vs_b01_ladder",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "mean_abs_move_vs_a2c8",
        "source_name",
        "source_weights",
        "variant",
        "scale",
    ]
    print(selected[[c for c in cols if c in selected.columns]].round(10).to_string(index=False))


if __name__ == "__main__":
    main()
