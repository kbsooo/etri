#!/usr/bin/env python3
"""E50 post-mixmin calendar-mask selector audit.

E49 reframed train/test as subject-calendar masking. This script tests whether
that observation becomes a useful selector target after adding mixmin as a known
public anchor. It does not create a submission.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from post_mixmin_observation_audit import (  # noqa: E402
    EPS,
    KEYS,
    TARGETS,
    calendar_mask_features,
    implied_threshold,
    logloss_delta,
    read_frame,
    subject_prior_features,
)


MIXMIN_PUBLIC = 0.5763066405
A2C8_PUBLIC = 0.5774393210
MIXMIN_EDGE = A2C8_PUBLIC - MIXMIN_PUBLIC

A2C8_FILE = "analysis_outputs/submission_frontier_cvjepa_refine_a2c8d2c8.csv"
MIXMIN_FILE = "analysis_outputs/submission_mixmin_0c916bb4.csv"
RAW05_FILE = "jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"

KNOWN_ANCHORS = [
    ("mixmin", MIXMIN_FILE, MIXMIN_PUBLIC, "active_frontier"),
    ("a2c8", A2C8_FILE, A2C8_PUBLIC, "previous_frontier"),
    ("raw05", RAW05_FILE, 0.5775263072, "raw05_positive_anchor"),
    (
        "stage2",
        "analysis_outputs/submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        0.5779449757,
        "stage2_local_cv_anchor",
    ),
    (
        "ordinal",
        "analysis_outputs/submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
        0.5783033652,
        "ordinal_constraint_anchor",
    ),
    (
        "final9",
        "analysis_outputs/submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
        0.5784273528,
        "subject_logit_anchor",
    ),
    ("q2_jepa_bad", "jepa/submission_jepa_latent_q2_w0p45.csv", 0.5798012862, "bad_q2_jepa_anchor"),
    (
        "lejepa_bad",
        "jepa/submission_lejepa_targetwise_strict_best_scale0p5.csv",
        0.5802468192,
        "bad_lejepa_anchor",
    ),
    (
        "jepa_residual_bad",
        "jepa/submission_jepa_latent_residual_probe.csv",
        0.5812273278,
        "bad_all_target_jepa_anchor",
    ),
]

VIEW_OUT = OUT / "post_mixmin_calendar_selector_views.csv"
LOOCV_OUT = OUT / "post_mixmin_calendar_selector_loocv.csv"
CANDIDATE_OUT = OUT / "post_mixmin_calendar_selector_candidates.csv"
FEATURE_OUT = OUT / "post_mixmin_calendar_selector_anchor_features.csv"
REPORT_OUT = OUT / "post_mixmin_calendar_selector_report.md"


@dataclass(frozen=True)
class Mask:
    name: str
    view: str
    idx: np.ndarray


def resolve_file(file_name: str) -> Path:
    path = Path(file_name)
    if path.exists():
        return path
    root_path = ROOT / file_name
    if root_path.exists():
        return root_path
    for parent in (OUT, JEPA, ROOT):
        candidate = parent / file_name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(file_name)


def read_submission(file_name: str) -> pd.DataFrame:
    df = pd.read_csv(resolve_file(file_name))
    for col in ("sleep_date", "lifelog_date"):
        df[col] = pd.to_datetime(df[col])
    return df.sort_values(KEYS).reset_index(drop=True)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip_prob(p)
    return np.log(p / (1.0 - p))


def entropy(p: np.ndarray) -> np.ndarray:
    p = clip_prob(p)
    return -(p * np.log(p) + (1.0 - p) * np.log(1.0 - p))


def make_context() -> pd.DataFrame:
    train = read_frame(DATA / "ch2026_metrics_train.csv")
    sample = read_frame(DATA / "ch2026_submission_sample.csv")
    priors = subject_prior_features(train, sample[KEYS])
    mask_features, _runs = calendar_mask_features(train, sample[KEYS])
    first_train = train.groupby("subject_id")["sleep_date"].min().rename("train_first_sleep")
    last_train = train.groupby("subject_id")["sleep_date"].max().rename("train_last_sleep")
    context = sample[KEYS].merge(mask_features, on=KEYS, how="left")
    context = context.merge(priors, on=KEYS, how="left")
    context = context.merge(first_train, on="subject_id", how="left")
    context = context.merge(last_train, on="subject_id", how="left")
    context["days_after_train"] = (context["sleep_date"] - context["train_last_sleep"]).dt.days
    context["days_from_train_start"] = (context["sleep_date"] - context["train_first_sleep"]).dt.days
    context["train_span_zone"] = np.select(
        [
            context["sleep_date"].lt(context["train_first_sleep"]),
            context["sleep_date"].gt(context["train_last_sleep"]),
        ],
        ["before_train_start", "after_train_end"],
        default="inside_train_calendar",
    )
    context["test_run_length_bin"] = pd.cut(
        context["test_run_length"].fillna(0).astype(float),
        bins=[-1, 1, 3, 7, 999],
        labels=["len1", "len2_3", "len4_7", "len8_plus"],
    ).astype(str)
    context["flank_signature"] = (
        context["calendar_context"].astype(str)
        + "__"
        + context["train_span_zone"].astype(str)
        + "__"
        + context["test_run_length_bin"].astype(str)
    )
    context["_row"] = np.arange(len(context), dtype=int)
    if context["calendar_context"].isna().any():
        raise RuntimeError("calendar context alignment failed")
    return context.reset_index(drop=True)


def add_category_masks(context: pd.DataFrame, masks: list[Mask], col: str, view: str, min_rows: int) -> None:
    for value, group in context.groupby(col, dropna=False, sort=True):
        idx = group["_row"].to_numpy(dtype=int)
        if len(idx) < min_rows:
            continue
        safe_value = str(value).replace(" ", "_").replace("/", "_")
        masks.append(Mask(f"{view}_{safe_value}", view, idx))


def build_masks(context: pd.DataFrame) -> list[Mask]:
    masks = [Mask("all", "target", np.arange(len(context), dtype=int))]
    add_category_masks(context, masks, "subject_id", "subject", min_rows=8)
    add_category_masks(context, masks, "calendar_context", "calendar", min_rows=6)
    add_category_masks(context, masks, "train_span_zone", "calendar", min_rows=6)
    add_category_masks(context, masks, "test_run_length_bin", "calendar", min_rows=6)
    add_category_masks(context, masks, "flank_signature", "calendar_combo", min_rows=4)
    return masks


def mask_features(base: np.ndarray, pred: np.ndarray, raw05: np.ndarray, mask: Mask) -> dict[str, float]:
    idx = mask.idx
    prob_delta = pred[idx] - base[idx]
    logit_delta = logit(pred[idx]) - logit(base[idx])
    entropy_delta = entropy(pred[idx]) - entropy(base[idx])
    raw05_dist = np.abs(pred[idx] - raw05[idx])
    feats: dict[str, float] = {}
    for j, target in enumerate(TARGETS):
        prefix = f"{mask.name}__{target}"
        feats[f"{prefix}__prob_mean"] = float(prob_delta[:, j].mean())
        feats[f"{prefix}__prob_abs_mean"] = float(np.abs(prob_delta[:, j]).mean())
        feats[f"{prefix}__logit_mean"] = float(logit_delta[:, j].mean())
        feats[f"{prefix}__logit_abs_mean"] = float(np.abs(logit_delta[:, j]).mean())
        feats[f"{prefix}__entropy_mean"] = float(entropy_delta[:, j].mean())
        feats[f"{prefix}__raw05_abs_dist"] = float(raw05_dist[:, j].mean())
    feats[f"{mask.name}__all__prob_abs_mean"] = float(np.abs(prob_delta).mean())
    feats[f"{mask.name}__all__logit_abs_mean"] = float(np.abs(logit_delta).mean())
    feats[f"{mask.name}__all__entropy_mean"] = float(entropy_delta.mean())
    feats[f"{mask.name}__all__raw05_abs_dist"] = float(raw05_dist.mean())
    return feats


def prior_features(context: pd.DataFrame, base: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    feats: dict[str, float] = {}
    for j, target in enumerate(TARGETS):
        old = base[:, j]
        new = pred[:, j]
        global_prior = float(
            pd.read_csv(DATA / "ch2026_metrics_train.csv", usecols=[target])[target].mean()
        )
        subj = context[f"subject_prior_{target}"].to_numpy(dtype=float)
        recent = context[f"subject_recent7_{target}"].to_numpy(dtype=float)
        thresh = implied_threshold(new, old)
        finite_thresh = np.isfinite(thresh)
        feats[f"prior__{target}__ce_global"] = float(np.mean(logloss_delta(new, old, global_prior)))
        feats[f"prior__{target}__ce_subject"] = float(np.mean(logloss_delta(new, old, subj)))
        feats[f"prior__{target}__ce_recent7"] = float(np.mean(logloss_delta(new, old, recent)))
        feats[f"prior__{target}__threshold_mean"] = float(np.nanmean(thresh)) if finite_thresh.any() else np.nan
        feats[f"prior__{target}__move_up_rate"] = float(np.mean((new - old) > 0))
        feats[f"prior__{target}__all_priors_adverse"] = float(
            (feats[f"prior__{target}__ce_global"] > 0)
            and (feats[f"prior__{target}__ce_subject"] > 0)
            and (feats[f"prior__{target}__ce_recent7"] > 0)
        )
    feats["prior__all__mean_ce_global"] = float(np.mean([feats[f"prior__{t}__ce_global"] for t in TARGETS]))
    feats["prior__all__mean_ce_subject"] = float(np.mean([feats[f"prior__{t}__ce_subject"] for t in TARGETS]))
    feats["prior__all__mean_ce_recent7"] = float(np.mean([feats[f"prior__{t}__ce_recent7"] for t in TARGETS]))
    feats["prior__all__n_adverse_targets"] = float(np.sum([feats[f"prior__{t}__all_priors_adverse"] for t in TARGETS]))
    return feats


def fingerprint_for_file(file_name: str, context: pd.DataFrame, masks: list[Mask], base: np.ndarray, raw05: np.ndarray) -> dict[str, Any]:
    pred_df = read_submission(file_name)
    key_df = context[KEYS].reset_index(drop=True)
    if not pred_df[KEYS].reset_index(drop=True).equals(key_df):
        raise ValueError(f"key mismatch: {file_name}")
    pred = clip_prob(pred_df[TARGETS].to_numpy(dtype=float))
    row: dict[str, Any] = {"file": file_name}
    for mask in masks:
        row.update(mask_features(base, pred, raw05, mask))
    row.update(prior_features(context, base, pred))
    return row


def view_columns(frame: pd.DataFrame, masks: list[Mask], view: str) -> list[str]:
    id_cols = {"name", "file", "role", "public_lb", "public_delta_vs_mixmin"}
    if view == "target_prior":
        prefixes = {"all", "prior"}
    elif view == "calendar":
        prefixes = {"all", "prior"} | {m.name for m in masks if m.view in {"calendar", "calendar_combo"}}
    elif view == "subject":
        prefixes = {"all", "prior"} | {m.name for m in masks if m.view == "subject"}
    elif view == "subject_calendar":
        prefixes = {"all", "prior"} | {m.name for m in masks if m.view in {"subject", "calendar", "calendar_combo"}}
    elif view == "calendar_no_prior":
        prefixes = {"all"} | {m.name for m in masks if m.view in {"calendar", "calendar_combo"}}
    else:
        raise ValueError(view)
    cols = []
    for col in frame.columns:
        if col in id_cols:
            continue
        prefix = col.split("__", 1)[0]
        if prefix in prefixes:
            cols.append(col)
    return cols


def scale_train_query(x_train: np.ndarray, x_query: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    med = np.nanmedian(x_train, axis=0)
    x_train = np.where(np.isfinite(x_train), x_train, med)
    x_query = np.where(np.isfinite(x_query), x_query, med)
    mu = x_train.mean(axis=0)
    sd = x_train.std(axis=0)
    keep = sd > 1e-10
    if int(keep.sum()) == 0:
        raise RuntimeError("all features constant")
    return (x_train[:, keep] - mu[keep]) / sd[keep], (x_query[:, keep] - mu[keep]) / sd[keep]


def predict_knn(x_train: np.ndarray, y_train: np.ndarray, x_query: np.ndarray) -> tuple[np.ndarray, list[str]]:
    x_train_s, x_query_s = scale_train_query(x_train, x_query)
    preds: list[float] = []
    neigh: list[str] = []
    for x in x_query_s:
        dist = np.linalg.norm(x_train_s - x[None, :], axis=1)
        order = np.argsort(dist)
        k = min(3, len(order))
        top = order[:k]
        weights = 1.0 / np.maximum(dist[top], 1e-6) ** 2
        weights = weights / weights.sum()
        preds.append(float(np.dot(weights, y_train[top])))
        neigh.append(",".join(str(int(i)) for i in top))
    return np.asarray(preds, dtype=float), neigh


def pairwise_rank_accuracy(actual: np.ndarray, pred: np.ndarray) -> float:
    good = total = 0
    for i in range(len(actual)):
        for j in range(i + 1, len(actual)):
            da = actual[i] - actual[j]
            dp = pred[i] - pred[j]
            if abs(da) < 1e-15 or abs(dp) < 1e-15:
                continue
            total += 1
            good += int(da * dp > 0)
    return float(good / total) if total else float("nan")


def spearman_corr(a: np.ndarray, b: np.ndarray) -> float:
    ra = pd.Series(a).rank(method="average").to_numpy(float)
    rb = pd.Series(b).rank(method="average").to_numpy(float)
    if np.std(ra) <= 1e-15 or np.std(rb) <= 1e-15:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def evaluate_view(fp_known: pd.DataFrame, masks: list[Mask], view: str) -> tuple[dict[str, Any], pd.DataFrame]:
    cols = view_columns(fp_known, masks, view)
    x = fp_known[cols].to_numpy(dtype=float)
    y = fp_known["public_delta_vs_mixmin"].to_numpy(dtype=float)
    pred = np.zeros(len(fp_known), dtype=float)
    neigh_txt: list[str] = []
    for i in range(len(fp_known)):
        train_idx = np.array([j for j in range(len(fp_known)) if j != i], dtype=int)
        p, neigh = predict_knn(x[train_idx], y[train_idx], x[[i]])
        pred[i] = p[0]
        neigh_txt.append(neigh[0])

    loocv = fp_known[["name", "file", "role", "public_lb", "public_delta_vs_mixmin"]].copy()
    loocv["view"] = view
    loocv["predicted_delta"] = pred
    loocv["error"] = pred - y
    loocv["abs_error"] = np.abs(loocv["error"])
    loocv["neighbor_indices"] = neigh_txt

    pred_by_name = loocv.set_index("name")["predicted_delta"].to_dict()
    actual_by_name = loocv.set_index("name")["public_delta_vs_mixmin"].to_dict()
    mixmin_abs_error = float(loocv.loc[loocv["name"].eq("mixmin"), "abs_error"].iloc[0])
    summary = {
        "view": view,
        "n_features": int(len(cols)),
        "loocv_mae": float(loocv["abs_error"].mean()),
        "loocv_max_abs_error": float(loocv["abs_error"].max()),
        "mixmin_abs_error": mixmin_abs_error,
        "pairwise_rank_accuracy": pairwise_rank_accuracy(y, pred),
        "spearman": spearman_corr(y, pred),
        "mixmin_predicted_best": bool(pred_by_name["mixmin"] <= min(pred_by_name.values()) + 1e-15),
        "a2c8_raw05_order_correct": bool(
            np.sign(actual_by_name["a2c8"] - actual_by_name["raw05"])
            == np.sign(pred_by_name["a2c8"] - pred_by_name["raw05"])
        ),
        "stage2_ordinal_order_correct": bool(
            np.sign(actual_by_name["stage2"] - actual_by_name["ordinal"])
            == np.sign(pred_by_name["stage2"] - pred_by_name["ordinal"])
        ),
        "bad_tail_correct": bool(
            min(pred_by_name["q2_jepa_bad"], pred_by_name["lejepa_bad"], pred_by_name["jepa_residual_bad"])
            > pred_by_name["final9"]
        ),
        "edge_scale_gate": bool(float(loocv["abs_error"].mean()) <= MIXMIN_EDGE),
        "mixmin_error_below_edge": bool(mixmin_abs_error <= MIXMIN_EDGE),
    }

    rng = np.random.default_rng(20260528)
    null_rank = []
    for _ in range(300):
        y_perm = rng.permutation(y)
        pred_perm = np.zeros(len(fp_known), dtype=float)
        for i in range(len(fp_known)):
            train_idx = np.array([j for j in range(len(fp_known)) if j != i], dtype=int)
            p, _ = predict_knn(x[train_idx], y_perm[train_idx], x[[i]])
            pred_perm[i] = p[0]
        null_rank.append(pairwise_rank_accuracy(y_perm, pred_perm))
    summary["null_rank_p_ge_actual"] = float((np.asarray(null_rank) >= summary["pairwise_rank_accuracy"]).mean())
    summary["strict_selector_gate"] = bool(
        summary["loocv_mae"] <= 0.00070
        and summary["pairwise_rank_accuracy"] >= 0.75
        and summary["mixmin_predicted_best"]
        and summary["a2c8_raw05_order_correct"]
        and summary["stage2_ordinal_order_correct"]
        and summary["bad_tail_correct"]
        and summary["null_rank_p_ge_actual"] <= 0.10
    )
    summary["loose_selector_gate"] = bool(
        summary["edge_scale_gate"]
        and summary["pairwise_rank_accuracy"] >= 0.65
        and summary["mixmin_predicted_best"]
        and summary["a2c8_raw05_order_correct"]
    )
    return summary, loocv


def candidate_predictions(
    fp_known: pd.DataFrame,
    fp_query: pd.DataFrame,
    masks: list[Mask],
    view_summary: pd.DataFrame,
) -> pd.DataFrame:
    y = fp_known["public_delta_vs_mixmin"].to_numpy(float)
    rows: list[pd.DataFrame] = []
    for view in ["target_prior", "calendar_no_prior", "calendar", "subject", "subject_calendar"]:
        cols = view_columns(fp_known, masks, view)
        x_train = fp_known[cols].to_numpy(float)
        x_query = fp_query[cols].to_numpy(float)
        pred, neigh = predict_knn(x_train, y, x_query)
        part = fp_query[["name", "file", "role"]].copy()
        part["view"] = view
        part["predicted_delta_vs_mixmin"] = pred
        part["predicted_public_lb"] = MIXMIN_PUBLIC + pred
        part["neighbor_indices"] = neigh
        rows.append(part)
    out = pd.concat(rows, axis=0, ignore_index=True)
    gate_map = view_summary.set_index("view")["strict_selector_gate"].to_dict()
    loose_map = view_summary.set_index("view")["loose_selector_gate"].to_dict()
    out["view_strict_gate"] = out["view"].map(gate_map).fillna(False)
    out["view_loose_gate"] = out["view"].map(loose_map).fillna(False)
    return out.sort_values(["view", "predicted_delta_vs_mixmin"]).reset_index(drop=True)


def df_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "_empty_"
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_float_dtype(out[col]):
            out[col] = out[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.6g}")
        else:
            out[col] = out[col].map(lambda x: "" if pd.isna(x) else str(x))
    headers = [str(c) for c in out.columns]
    rows = out.astype(str).values.tolist()
    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]

    def fmt(row: list[str]) -> str:
        return "| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(row))) + " |"

    sep = "| " + " | ".join("-" * w for w in widths) + " |"
    return "\n".join([fmt(headers), sep] + [fmt(row) for row in rows])


def candidate_file_list() -> list[dict[str, str]]:
    rows = [{"name": name, "file": file_name, "role": role} for name, file_name, _lb, role in KNOWN_ANCHORS]
    sensor_path = OUT / "worldview_sensor_discriminability_audit.csv"
    if sensor_path.exists():
        sensors = pd.read_csv(sensor_path)
        for _, rec in sensors.head(20).iterrows():
            rows.append({"name": str(rec["role"]), "file": str(rec["file"]), "role": str(rec["lane"])})
    manual = [
        ("inv7_s0p25", "analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv", "conservative_raw_bridge"),
        (
            "s4q3_s0p65",
            "analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv",
            "lower_risk_s4q3_sensor",
        ),
        ("pair_1bb", "analysis_outputs/submission_label_flow_focused_1bbfb735.csv", "pair_s4q3_sensor"),
        ("pair_6b", "analysis_outputs/submission_label_flow_focused_6b9335b1.csv", "pair_s4q3_sensor"),
    ]
    rows.extend({"name": n, "file": f, "role": r} for n, f, r in manual)
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for row in rows:
        if row["file"] in seen:
            continue
        try:
            resolve_file(row["file"])
        except FileNotFoundError:
            continue
        seen.add(row["file"])
        out.append(row)
    return out


def write_report(view_summary: pd.DataFrame, loocv: pd.DataFrame, candidates: pd.DataFrame) -> None:
    strict_n = int(view_summary["strict_selector_gate"].sum())
    loose_n = int(view_summary["loose_selector_gate"].sum())
    best_view = view_summary.sort_values(
        ["strict_selector_gate", "loose_selector_gate", "loocv_mae"], ascending=[False, False, True]
    ).head(1)
    candidate_pivot = (
        candidates.pivot_table(index=["name", "file", "role"], columns="view", values="predicted_public_lb", aggfunc="first")
        .reset_index()
        .sort_values("subject_calendar")
    )
    candidate_pivot.columns = [str(c) for c in candidate_pivot.columns]

    lines = [
        "# E50 Post-Mixmin Calendar Selector",
        "",
        "## Observe",
        "",
        "E49 showed that train/test is an interleaved subject-calendar mask and that mixmin is not a simple prevalence correction.",
        "",
        "## Wonder",
        "",
        "Can calendar-run movement fingerprints explain `mixmin` as the new public-best anchor without breaking raw05, stage2, ordinal, and bad-JEPA anchor order?",
        "",
        "## Hypothesis",
        "",
        "H48 predicts that labeled calendar flanks around hidden test runs contain selector information. If true, a calendar view should recover mixmin as best and keep known-anchor ordering under leave-one-anchor-out.",
        "",
        "## Method",
        "",
        "- Features are probability/logit/entropy movement relative to a2c8, aggregated by target, subject, calendar context, train-span zone, run-length bin, and flank signature.",
        "- Prior stress features reuse train/global, subject, and recent7 proxy LogLoss deltas.",
        "- Public LB is used only for known-anchor LOOCV; no submission is generated.",
        f"- Mixmin-a2c8 public edge scale: `{MIXMIN_EDGE:.9f}`.",
        "",
        "## Result",
        "",
        f"- strict selector views: `{strict_n}`.",
        f"- loose selector views: `{loose_n}`.",
        "",
        "## View Summary",
        "",
        df_to_markdown(
            view_summary[
                [
                    "view",
                    "n_features",
                    "loocv_mae",
                    "mixmin_abs_error",
                    "pairwise_rank_accuracy",
                    "spearman",
                    "mixmin_predicted_best",
                    "a2c8_raw05_order_correct",
                    "stage2_ordinal_order_correct",
                    "bad_tail_correct",
                    "edge_scale_gate",
                    "null_rank_p_ge_actual",
                    "strict_selector_gate",
                    "loose_selector_gate",
                ]
            ]
        ),
        "",
        "## Best View",
        "",
        df_to_markdown(best_view),
        "",
        "## Known Anchor LOOCV",
        "",
        df_to_markdown(
            loocv[
                [
                    "view",
                    "name",
                    "public_delta_vs_mixmin",
                    "predicted_delta",
                    "abs_error",
                    "role",
                    "neighbor_indices",
                ]
            ].sort_values(["view", "public_delta_vs_mixmin"]).head(90)
        ),
        "",
        "## Candidate Sensor Predictions",
        "",
        "These are not submission forecasts unless a view passes the gate.",
        "",
        df_to_markdown(candidate_pivot.head(20)),
        "",
        "## Decision",
        "",
    ]
    if strict_n == 0 and loose_n == 0:
        lines.append(
            "Calendar-mask movement is an important observation, but the tested selector does not yet explain mixmin strongly enough to rank new submissions."
        )
    elif strict_n == 0:
        lines.append(
            "At least one loose calendar selector survives edge-scale stress, but no strict selector passes. Use this only as a diagnostic prior, not as a submission gate."
        )
    else:
        lines.append(
            "A strict calendar selector exists. It can become a mixmin-relative candidate gate after independent raw/anchor/private-risk stress."
        )
    lines += [
        "",
        "## Outputs",
        "",
        f"- `{VIEW_OUT.relative_to(ROOT)}`",
        f"- `{LOOCV_OUT.relative_to(ROOT)}`",
        f"- `{CANDIDATE_OUT.relative_to(ROOT)}`",
        f"- `{FEATURE_OUT.relative_to(ROOT)}`",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    context = make_context()
    masks = build_masks(context)
    base = clip_prob(read_submission(A2C8_FILE)[TARGETS].to_numpy(dtype=float))
    raw05 = clip_prob(read_submission(RAW05_FILE)[TARGETS].to_numpy(dtype=float))

    known_rows: list[dict[str, Any]] = []
    for name, file_name, lb, role in KNOWN_ANCHORS:
        row = fingerprint_for_file(file_name, context, masks, base, raw05)
        row.update({"name": name, "role": role, "public_lb": lb, "public_delta_vs_mixmin": lb - MIXMIN_PUBLIC})
        known_rows.append(row)
    fp_known = pd.DataFrame(known_rows)

    query_rows: list[dict[str, Any]] = []
    for item in candidate_file_list():
        row = fingerprint_for_file(item["file"], context, masks, base, raw05)
        row.update(item)
        query_rows.append(row)
    fp_query = pd.DataFrame(query_rows)

    view_rows = []
    loocv_rows = []
    for view in ["target_prior", "calendar_no_prior", "calendar", "subject", "subject_calendar"]:
        summary, loocv = evaluate_view(fp_known, masks, view)
        view_rows.append(summary)
        loocv_rows.append(loocv)
    view_summary = pd.DataFrame(view_rows).sort_values(
        ["strict_selector_gate", "loose_selector_gate", "loocv_mae"], ascending=[False, False, True]
    )
    loocv_all = pd.concat(loocv_rows, axis=0, ignore_index=True)
    candidates = candidate_predictions(fp_known, fp_query, masks, view_summary)

    view_summary.to_csv(VIEW_OUT, index=False)
    loocv_all.to_csv(LOOCV_OUT, index=False)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    fp_known.to_csv(FEATURE_OUT, index=False)
    write_report(view_summary, loocv_all, candidates)

    print(f"views={len(view_summary)} strict={int(view_summary['strict_selector_gate'].sum())} loose={int(view_summary['loose_selector_gate'].sum())}")
    print(view_summary.to_string(index=False))
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
