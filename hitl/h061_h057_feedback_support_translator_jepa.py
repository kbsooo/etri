#!/usr/bin/env python3
"""H061: H057-feedback support translator HS-JEPA.

H057 is the first public-confirmed proof that H042's Q2 support rows can carry
a complete non-Q2 hidden state vector.  H055 did not know the H057 public score.

This experiment treats H057 itself as new JEPA target supervision:

    context = H012/H042/H050/H057 public observations
    target  = hidden public state posterior after seeing H057
    action  = split H057's 270 support cells into core, middle, and tail

If H061 improves, H057's win is decomposable into public-supported and
public-opposed cells.  If it fails, one aggregate H057 observation is not enough
to safely decompose the validated row-state move.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import importlib.util
import hashlib
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h061_h057_feedback_support_translator_jepa"
ANALYSIS = ROOT / "analysis_outputs"
OUT.mkdir(parents=True, exist_ok=True)

if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from public_anchor_bottleneck_decomposition import known_public_table  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050 = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
H057 = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"

MANUAL_PUBLIC = {
    H012: (0.5681234831, "manual H012 public-equation best"),
    H042: (0.5679048248, "manual H042 Q2 phase public sensor"),
    H050: (0.5679048248, "manual H050 non-Q2 target-route null sensor"),
    H057: (0.5677475939, "manual H057 Q2-row full-vector public frontier"),
}


@dataclass(frozen=True)
class SplitSpec:
    top_k: int
    bottom_k: int
    top_alpha: float
    bottom_keep: float
    middle_keep: float
    mode: str
    family: str


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H055MOD = import_module(HITL / "h055_postfeedback_public_listener_jepa.py", "h055mod_for_h061")


def locate(name: str | Path) -> Path | None:
    return H055MOD.locate(name)


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    return H055MOD.load_sub(name, sample)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return H055MOD.clip_prob(x)


def logit(x: np.ndarray) -> np.ndarray:
    return H055MOD.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return H055MOD.sigmoid(x)


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return H055MOD.bce(prob, q)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H055MOD.md_table(frame, n)


def pivot_cell_table(path: Path, value_col: str, sample: pd.DataFrame) -> np.ndarray:
    return H055MOD.pivot_cell_table(path, value_col, sample)


def equation_arrays(
    known: pd.DataFrame,
    base_prob: np.ndarray,
    pred_by_file: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    return H055MOD.equation_arrays(known, base_prob, pred_by_file)


def fit_posterior(a: np.ndarray, b: np.ndarray, prior: np.ndarray, ridge_mult: float) -> np.ndarray:
    return H055MOD.fit_posterior(a, b, prior, ridge_mult)


def predict_delta(d0: np.ndarray, d1: np.ndarray, q: np.ndarray) -> float:
    return H055MOD.predict_delta(d0, d1, q)


def rank01(x: np.ndarray, high: bool = True) -> np.ndarray:
    return H055MOD.rank01(x, high)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    H055MOD.write_submission(sample, prob, path)


def move_toward(base: np.ndarray, q: np.ndarray, alpha: float, mode: str) -> np.ndarray:
    if mode == "prob":
        return clip_prob((1.0 - alpha) * base + alpha * q)
    if mode == "logit":
        return clip_prob(sigmoid((1.0 - alpha) * logit(base) + alpha * logit(q)))
    raise ValueError(mode)


def read_public_observations() -> pd.DataFrame:
    known = known_public_table().copy()
    known["known_source"] = known.get("known_source", "known_public_table")
    manual = pd.DataFrame(
        [
            {"file": file, "public_lb": lb, "note": note, "known_source": "manual_h057_feedback"}
            for file, (lb, note) in MANUAL_PUBLIC.items()
        ]
    )
    out = pd.concat([known, manual], ignore_index=True)
    out = out.drop_duplicates("file", keep="last")
    rows = [rec for rec in out.to_dict("records") if locate(str(rec["file"])) is not None]
    return pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)


def build_priors(sample: pd.DataFrame, known: pd.DataFrame, pred_by_file: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    priors = H055MOD.build_priors(sample, known, pred_by_file)
    priors["h057_anchor"] = pred_by_file[H057].reshape(-1)

    h055_post = HITL / "h055_postfeedback_public_listener_jepa" / "h055_cell_posterior.csv"
    if h055_post.exists():
        priors["h055_posterior"] = pivot_cell_table(h055_post, "posterior_prob", sample).reshape(-1)

    good_files = [H012, H042, H050, H057]
    weights = np.array([0.05, 0.20, 0.20, 0.55], dtype=np.float64)
    stack = np.stack([pred_by_file[file] for file in good_files], axis=0)
    priors["h057_weighted_anchor"] = np.tensordot(weights / weights.sum(), stack, axes=(0, 0)).reshape(-1)
    return priors


def evaluate_configs(eq: pd.DataFrame, a: np.ndarray, d0: np.ndarray, b: np.ndarray, priors: dict[str, np.ndarray]) -> pd.DataFrame:
    n = next(iter(priors.values())).size
    d1 = a * n
    actual = eq["actual_delta_vs_h012"].to_numpy(dtype=np.float64)
    files = eq["file"].astype(str).tolist()
    h042_idx = files.index(H042)
    h050_idx = files.index(H050)
    h057_idx = files.index(H057)
    rows = []
    ridge_mults = [1.0e-5, 3.0e-5, 1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 1.0e-1, 3.0e-1, 1.0]

    for prior_name, prior in priors.items():
        for ridge in ridge_mults:
            full_q = fit_posterior(a, b, prior, ridge)
            full_pred = np.asarray([predict_delta(d0[i], d1[i], full_q) for i in range(len(files))])
            loo_pred = []
            for hold in range(len(files)):
                keep = np.ones(len(files), dtype=bool)
                keep[hold] = False
                q = fit_posterior(a[keep], b[keep], prior, ridge)
                loo_pred.append(predict_delta(d0[hold], d1[hold], q))
            loo_pred = np.asarray(loo_pred)
            loo_err = loo_pred - actual
            rows.append(
                {
                    "prior_name": prior_name,
                    "ridge_mult": ridge,
                    "loo_mae": float(np.mean(np.abs(loo_err))),
                    "loo_p90_abs": float(np.quantile(np.abs(loo_err), 0.90)),
                    "known_fit_mae": float(np.mean(np.abs(full_pred - actual))),
                    "h042_fit_delta": float(full_pred[h042_idx]),
                    "h050_fit_delta": float(full_pred[h050_idx]),
                    "h057_fit_delta": float(full_pred[h057_idx]),
                    "h050_minus_h042_fit_delta": float(full_pred[h050_idx] - full_pred[h042_idx]),
                    "h057_minus_h042_fit_delta": float(full_pred[h057_idx] - full_pred[h042_idx]),
                    "h042_actual_delta": float(actual[h042_idx]),
                    "h050_actual_delta": float(actual[h050_idx]),
                    "h057_actual_delta": float(actual[h057_idx]),
                    "h057_minus_h042_actual_delta": float(actual[h057_idx] - actual[h042_idx]),
                    "q_mean": float(full_q.mean()),
                    "q_std": float(full_q.std()),
                }
            )
    out = pd.DataFrame(rows)
    out["post_sensor_abs_error"] = (
        (out["h042_fit_delta"] - out["h042_actual_delta"]).abs()
        + (out["h050_fit_delta"] - out["h050_actual_delta"]).abs()
        + (out["h057_fit_delta"] - out["h057_actual_delta"]).abs()
        + out["h050_minus_h042_fit_delta"].abs()
        + (out["h057_minus_h042_fit_delta"] - out["h057_minus_h042_actual_delta"]).abs()
    )
    out["selection_score"] = (
        out["loo_mae"].rank(method="average", pct=True)
        + 0.50 * out["loo_p90_abs"].rank(method="average", pct=True)
        + 1.10 * out["post_sensor_abs_error"].rank(method="average", pct=True)
    )
    return out.sort_values(["selection_score", "loo_mae"]).reset_index(drop=True)


def support_table(
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    q055: np.ndarray,
) -> pd.DataFrame:
    support = np.abs(h057_prob - h042_prob) > 1.0e-12
    support[:, TARGETS.index("Q2")] = False
    gain061 = bce(h042_prob, q061) - bce(h057_prob, q061)
    gain055 = bce(h042_prob, q055) - bce(h057_prob, q055)
    direction = np.sign(logit(h057_prob) - logit(h042_prob))
    qdir = np.sign(logit(q061) - logit(h042_prob))
    agreement = direction * qdir
    rows = []
    for row in range(len(sample)):
        for ti, target in enumerate(TARGETS):
            if not support[row, ti]:
                continue
            rows.append(
                {
                    "row": row,
                    "subject_id": sample.loc[row, "subject_id"],
                    "sleep_date": sample.loc[row, "sleep_date"],
                    "lifelog_date": sample.loc[row, "lifelog_date"],
                    "target": target,
                    "h042_prob": float(h042_prob[row, ti]),
                    "h057_prob": float(h057_prob[row, ti]),
                    "q061": float(q061[row, ti]),
                    "q055": float(q055[row, ti]),
                    "gain061_h057_vs_h042": float(gain061[row, ti]),
                    "gain055_h057_vs_h042": float(gain055[row, ti]),
                    "feedback_lift": float(gain061[row, ti] - gain055[row, ti]),
                    "direction_agreement": float(agreement[row, ti]),
                    "abs_h057_move": float(abs(h057_prob[row, ti] - h042_prob[row, ti])),
                    "abs_q061_move": float(abs(q061[row, ti] - h042_prob[row, ti])),
                }
            )
    out = pd.DataFrame(rows)
    out["support_score"] = (
        0.45 * rank01(out["gain061_h057_vs_h042"].to_numpy())
        + 0.25 * rank01(out["feedback_lift"].to_numpy())
        + 0.20 * rank01(out["abs_q061_move"].to_numpy())
        + 0.10 * (out["direction_agreement"].to_numpy() > 0).astype(float)
    )
    return out.sort_values("support_score", ascending=False).reset_index(drop=True)


def make_candidate(
    spec: SplitSpec,
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    support: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, object]]:
    prob = h057_prob.copy()
    top = support.head(spec.top_k)
    bottom = support.tail(spec.bottom_k) if spec.bottom_k else support.iloc[0:0]
    middle_n = max(0, len(support) - spec.top_k - spec.bottom_k)
    middle = support.iloc[spec.top_k : spec.top_k + middle_n]

    top_target = move_toward(h042_prob, q061, spec.top_alpha, spec.mode)
    rollback_target = move_toward(h042_prob, h057_prob, spec.bottom_keep, "prob")
    middle_target = move_toward(h042_prob, h057_prob, spec.middle_keep, "prob")

    if spec.family == "top_only":
        bottom = support.iloc[0:0]
        middle = support.iloc[0:0]
    elif spec.family == "split_tail":
        pass
    elif spec.family == "split_tail_middle":
        pass
    else:
        raise ValueError(spec.family)

    for rec in top.to_dict("records"):
        ri = int(rec["row"])
        ti = TARGETS.index(str(rec["target"]))
        prob[ri, ti] = top_target[ri, ti]
    for rec in bottom.to_dict("records"):
        ri = int(rec["row"])
        ti = TARGETS.index(str(rec["target"]))
        prob[ri, ti] = rollback_target[ri, ti]
    for rec in middle.to_dict("records"):
        ri = int(rec["row"])
        ti = TARGETS.index(str(rec["target"]))
        prob[ri, ti] = middle_target[ri, ti]

    diff057 = np.abs(prob - h057_prob) > 1.0e-12
    diff042 = np.abs(prob - h042_prob) > 1.0e-12
    h057_support_mask = np.abs(h057_prob - h042_prob) > 1.0e-12
    h057_support_mask[:, TARGETS.index("Q2")] = False
    gain_delta = float(np.mean(bce(prob, q061) - bce(h057_prob, q061)))
    retained = int((diff042 & h057_support_mask).sum())
    per_target = {f"{target}_changed_vs_h057": int(diff057[:, i].sum()) for i, target in enumerate(TARGETS)}
    meta = {
        "family": spec.family,
        "top_k": spec.top_k,
        "bottom_k": spec.bottom_k,
        "top_alpha": spec.top_alpha,
        "bottom_keep": spec.bottom_keep,
        "middle_keep": spec.middle_keep,
        "mode": spec.mode,
        "posterior_delta_vs_h057": gain_delta,
        "changed_cells_vs_h057": int(diff057.sum()),
        "changed_rows_vs_h057": int(diff057.any(axis=1).sum()),
        "changed_cells_vs_h042": int(diff042.sum()),
        "retained_h057_support_cells": retained,
        "q2_changed_vs_h057": int(diff057[:, TARGETS.index("Q2")].sum()),
        "mean_top_support": float(top["support_score"].mean()) if len(top) else 0.0,
        "mean_bottom_support": float(bottom["support_score"].mean()) if len(bottom) else 0.0,
        "min_top_gain061": float(top["gain061_h057_vs_h042"].min()) if len(top) else 0.0,
        "max_bottom_gain061": float(bottom["gain061_h057_vs_h042"].max()) if len(bottom) else 0.0,
        **per_target,
    }
    return clip_prob(prob), meta


def candidate_sweep(
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    support: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Path]]:
    specs = [
        SplitSpec(top_k, bottom_k, top_alpha, bottom_keep, middle_keep, mode, family)
        for family in ["split_tail", "split_tail_middle", "top_only"]
        for top_k in [36, 54, 72, 96, 120, 150]
        for bottom_k in ([0] if family == "top_only" else [24, 42, 60, 84, 108, 132])
        for top_alpha in [1.10, 1.35, 1.60, 1.90]
        for bottom_keep in ([1.0] if family == "top_only" else [0.00, 0.20, 0.40])
        for middle_keep in ([1.0] if family != "split_tail_middle" else [0.60, 0.75, 0.90])
        for mode in ["logit", "prob"]
    ]
    rows = []
    paths: dict[str, Path] = {}
    for spec in specs:
        if spec.top_k + spec.bottom_k > len(support):
            continue
        prob, meta = make_candidate(spec, sample, h042_prob, h057_prob, q061, support)
        digest = short_hash(prob)
        cid = (
            f"h061_{spec.family}_t{spec.top_k}_b{spec.bottom_k}_"
            f"a{str(spec.top_alpha).replace('.', 'p')}_bk{str(spec.bottom_keep).replace('.', 'p')}_"
            f"mk{str(spec.middle_keep).replace('.', 'p')}_{spec.mode}_{digest}"
        )
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, prob, path)
        paths[cid] = path
        rows.append({"candidate_id": cid, "file": path.name, "resolved_path": str(path), **meta})
    out = pd.DataFrame(rows)
    out["h061_score"] = (
        -1.20 * out["posterior_delta_vs_h057"].rank(method="average", pct=True)
        + 0.35 * out["changed_cells_vs_h057"].rank(method="average", pct=True)
        + 0.30 * out["mean_top_support"].rank(method="average", pct=True)
        - 0.35 * (out["q2_changed_vs_h057"] > 0).astype(float)
        - 0.15 * (out["changed_cells_vs_h057"] < 90).astype(float)
        - 0.10 * (out["changed_cells_vs_h057"] > 240).astype(float)
    )
    out = out.sort_values(["h061_score", "posterior_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    return out, paths


def validate_upload(path: Path, sample: pd.DataFrame) -> dict[str, object]:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    probs = df[TARGETS].to_numpy(dtype=np.float64)
    return {
        "path": str(path),
        "rows": int(len(df)),
        "columns": ",".join(df.columns),
        "keys_match": bool(df[KEYS].equals(sample[KEYS])),
        "duplicate_keys": int(df.duplicated(KEYS).sum()),
        "nan_cells": int(df[TARGETS].isna().sum().sum()),
        "min_prob": float(np.min(probs)),
        "max_prob": float(np.max(probs)),
        "upload_safe": bool(
            len(df) == len(sample)
            and df[KEYS].equals(sample[KEYS])
            and df.duplicated(KEYS).sum() == 0
            and df[TARGETS].isna().sum().sum() == 0
            and np.min(probs) > 0.0
            and np.max(probs) < 1.0
        ),
    }


def main() -> None:
    known = read_public_observations()
    h012 = load_sub(H012)
    sample = h012[KEYS].copy()
    pred_by_file = {}
    rows = []
    for rec in known.to_dict("records"):
        file = str(rec["file"])
        try:
            pred_by_file[file] = load_sub(file, sample)[TARGETS].to_numpy(dtype=np.float64)
            rows.append(rec)
        except Exception:
            continue
    known = pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)

    h012_prob = pred_by_file[H012]
    h042_prob = pred_by_file[H042]
    h050_prob = pred_by_file[H050]
    h057_prob = pred_by_file[H057]

    eq, a, d0, b = equation_arrays(known, h012_prob, pred_by_file)
    priors = build_priors(sample, known, pred_by_file)
    config_scores = evaluate_configs(eq, a, d0, b, priors)
    selected_config = config_scores.iloc[0]
    q061 = fit_posterior(
        a,
        b,
        priors[str(selected_config["prior_name"])],
        float(selected_config["ridge_mult"]),
    ).reshape(h012_prob.shape)

    q055 = pivot_cell_table(HITL / "h055_postfeedback_public_listener_jepa" / "h055_cell_posterior.csv", "posterior_prob", sample)
    support = support_table(sample, h042_prob, h057_prob, q061, q055)
    candidates, paths = candidate_sweep(sample, h042_prob, h057_prob, q061, support)

    selected = candidates.iloc[0]
    selected_path = paths[str(selected["candidate_id"])]
    selected_prob = load_sub(selected_path, sample)[TARGETS].to_numpy(dtype=np.float64)
    root_name = f"submission_h061_h057feedback_support_{short_hash(selected_prob)}_uploadsafe.csv"
    root_path = ROOT / root_name
    shutil.copyfile(selected_path, root_path)
    upload_check = validate_upload(root_path, sample)

    support_summary = pd.DataFrame(
        [
            {
                "h057_support_cells": int(len(support)),
                "positive_gain061_cells": int((support["gain061_h057_vs_h042"] > 0).sum()),
                "negative_gain061_cells": int((support["gain061_h057_vs_h042"] < 0).sum()),
                "positive_direction_agreement_cells": int((support["direction_agreement"] > 0).sum()),
                "mean_gain061": float(support["gain061_h057_vs_h042"].mean()),
                "mean_gain055": float(support["gain055_h057_vs_h042"].mean()),
                "mean_feedback_lift": float(support["feedback_lift"].mean()),
                "h057_public_delta_vs_h042": MANUAL_PUBLIC[H057][0] - MANUAL_PUBLIC[H042][0],
            }
        ]
    )
    decision = pd.DataFrame(
        [
            {
                "decision": "promote_h057_feedback_support_translator",
                "selected_candidate_id": str(selected["candidate_id"]),
                "selected_file": str(selected["file"]),
                "selected_resolved_path": str(selected_path),
                "root_uploadsafe_path": str(root_path),
                "worldview": "H057 success can be decomposed into public-supported core cells and rollback-tail cells",
                "selected_prior": str(selected_config["prior_name"]),
                "selected_ridge_mult": float(selected_config["ridge_mult"]),
                "config_loo_mae": float(selected_config["loo_mae"]),
                "config_post_sensor_abs_error": float(selected_config["post_sensor_abs_error"]),
                **selected.to_dict(),
                **upload_check,
            }
        ]
    )

    known.to_csv(OUT / "h061_augmented_public_observations.csv", index=False)
    eq.to_csv(OUT / "h061_equations.csv", index=False)
    config_scores.to_csv(OUT / "h061_posterior_config_scores.csv", index=False)
    support.to_csv(OUT / "h061_cell_support.csv", index=False)
    support_summary.to_csv(OUT / "h061_support_summary.csv", index=False)
    candidates.to_csv(OUT / "h061_candidate_scores.csv", index=False)
    decision.to_csv(OUT / "h061_decision.csv", index=False)
    pd.DataFrame(
        {
            "row": np.repeat(np.arange(len(sample)), len(TARGETS)),
            "target": TARGETS * len(sample),
            "h042_prob": h042_prob.reshape(-1),
            "h057_prob": h057_prob.reshape(-1),
            "q055": q055.reshape(-1),
            "q061": q061.reshape(-1),
            "q061_minus_h057": (q061 - h057_prob).reshape(-1),
        }
    ).to_csv(OUT / "h061_cell_posterior.csv", index=False)

    report = f"""# H061 H057-Feedback Support Translator HS-JEPA

Question: can H057's public win be decomposed into supported core cells and
rollback-tail cells after adding H057 public feedback to the public-equation
posterior?

Design:

- base public-equation anchor: H012;
- manual public sensors: H042, H050, H057;
- upload base: H057;
- Q2 is frozen exactly;
- editable cells are H057's `270` non-Q2 support cells against H042;
- H061 posterior is fitted after seeing H057, then used to split support cells.

Selected posterior config:

{md_table(config_scores.head(12))}

Support summary:

{md_table(support_summary)}

Decision:

{md_table(decision)}

Top support cells:

{md_table(support.head(20))}

Top candidates:

{md_table(candidates.head(25))}

Interpretation rule:

- If H061 improves over H057, H057's full-vector law is real but heterogeneous:
  HS-JEPA should learn a support-core/rollback-tail translator.
- If H061 fails, one aggregate H057 public observation is too underidentified to
  decompose the row-state vector; H057's uniform translation remains the
  stronger current law.
"""
    (OUT / "h061_report.md").write_text(report)
    print(f"H061 selected: {decision.loc[0, 'selected_candidate_id']}")
    print(f"H061 root: {root_path}")
    print(decision[["selected_candidate_id", "changed_cells_vs_h057", "changed_cells_vs_h042", "posterior_delta_vs_h057", "q2_changed_vs_h057", "upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    main()
