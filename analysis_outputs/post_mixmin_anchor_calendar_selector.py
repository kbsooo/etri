#!/usr/bin/env python3
"""E51 post-mixmin anchor-loss x calendar selector audit.

E50 showed that subject-calendar movement is real but not sufficient as a
standalone selector. This script asks the next narrower question: does
calendar context become useful when it is combined with the binary-world
anchor-loss geometry that selected mixmin before its public LB was known?

The script is intentionally a selector audit, not a submission generator.
Known-anchor LOOCV is LOO-safe: the held-out anchor is omitted from the
world-energy calculation used to build its query features.
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
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from post_mixmin_calendar_selector import (  # noqa: E402
    A2C8_FILE,
    A2C8_PUBLIC,
    KNOWN_ANCHORS,
    MIXMIN_EDGE,
    MIXMIN_PUBLIC,
    RAW05_FILE,
    build_masks,
    candidate_file_list,
    df_to_markdown,
    fingerprint_for_file,
    make_context,
    pairwise_rank_accuracy,
    predict_knn,
    read_submission,
    resolve_file,
    spearman_corr,
)
from post_mixmin_observation_audit import EPS, TARGETS  # noqa: E402


WORLD_CSV = OUT / "public_lb_binary_frontier_box_pool_worlds.csv"
NPZ = OUT / "public_lb_binary_frontier_box_pool_labels.npz"

VIEW_OUT = OUT / "post_mixmin_anchor_calendar_selector_views.csv"
LOOCV_OUT = OUT / "post_mixmin_anchor_calendar_selector_loocv.csv"
CANDIDATE_OUT = OUT / "post_mixmin_anchor_calendar_selector_candidates.csv"
FEATURE_OUT = OUT / "post_mixmin_anchor_calendar_selector_anchor_features.csv"
WORLD_ENERGY_OUT = OUT / "post_mixmin_anchor_calendar_selector_world_energy.csv"
REPORT_OUT = OUT / "post_mixmin_anchor_calendar_selector_report.md"


@dataclass(frozen=True)
class Anchor:
    name: str
    file: str
    public_lb: float
    role: str

    @property
    def delta_vs_mixmin(self) -> float:
        return self.public_lb - MIXMIN_PUBLIC

    @property
    def delta_vs_a2c8(self) -> float:
        return self.public_lb - A2C8_PUBLIC


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip_prob(p)
    return np.log(p / (1.0 - p))


def corr_safe(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if np.std(a) <= 1e-12 or np.std(b) <= 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def entropy(values: np.ndarray) -> float:
    v = np.abs(np.asarray(values, dtype=np.float64))
    total = float(v.sum())
    if total <= 1e-15:
        return 0.0
    q = v / total
    return float(-(q * np.log(q + 1e-15)).sum() / np.log(len(q)))


def robust_z(values: pd.Series) -> pd.Series:
    med = float(values.median())
    mad = float((values - med).abs().median())
    scale = 1.4826 * mad
    if scale <= 1e-12:
        std = float(values.std(ddof=0))
        scale = std if std > 1e-12 else 1.0
    return (values - med) / scale


def target_logloss(prob: np.ndarray, labels: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    y = np.asarray(labels, dtype=np.float64)
    return -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)).mean(axis=0)


def load_worlds() -> tuple[pd.DataFrame, np.ndarray]:
    worlds = pd.read_csv(WORLD_CSV)
    labels = np.load(NPZ, allow_pickle=True)["labels"].astype(np.float64)
    labels = labels.reshape(labels.shape[0], labels.shape[1] // len(TARGETS), len(TARGETS))
    if len(worlds) != labels.shape[0]:
        worlds = worlds[worlds["has_incumbent"].astype(bool)].reset_index(drop=True)
    if len(worlds) != labels.shape[0]:
        raise ValueError("world/label count mismatch")
    return worlds.reset_index(drop=True), labels


def target_loss_delta_by_world(prob: np.ndarray, base_prob: np.ndarray, labels: np.ndarray) -> np.ndarray:
    rows = []
    for y in labels:
        rows.append(target_logloss(prob, y) - target_logloss(base_prob, y))
    return np.vstack(rows)


def file_world_metrics(file_name: str, sample: pd.DataFrame, base_prob: np.ndarray, labels: np.ndarray) -> pd.DataFrame:
    df = read_submission(file_name)
    if not df[["subject_id", "sleep_date", "lifelog_date"]].reset_index(drop=True).equals(
        sample[["subject_id", "sleep_date", "lifelog_date"]].reset_index(drop=True)
    ):
        raise ValueError(f"key mismatch: {file_name}")
    prob = clip_prob(df[TARGETS].to_numpy(dtype=float))
    deltas = target_loss_delta_by_world(prob, base_prob, labels)
    weights = np.mean(np.abs(logit(prob) - logit(base_prob)), axis=0)
    if weights.sum() <= 1e-15:
        weights = np.ones(len(TARGETS), dtype=float) / len(TARGETS)
    else:
        weights = weights / weights.sum()

    rows: list[dict[str, float]] = []
    for world_row, delta_t in enumerate(deltas):
        delta_sum = float(delta_t.sum())
        abs_sum = float(np.abs(delta_t).sum())
        row: dict[str, float] = {
            "world_row": float(world_row),
            "delta_mean": float(delta_t.mean()),
            "delta_sum": delta_sum,
            "delta_abs_sum": abs_sum,
            "cancellation_ratio": float(abs_sum / (abs(delta_sum) + 1e-12)),
            "target_delta_entropy": entropy(delta_t),
            "movement_loss_abs_corr": corr_safe(weights, np.abs(delta_t)),
        }
        for target_i, target in enumerate(TARGETS):
            row[f"delta_{target}"] = float(delta_t[target_i])
            row[f"move_weight_{target}"] = float(weights[target_i])
        rows.append(row)
    return pd.DataFrame(rows)


def known_anchor_list() -> list[Anchor]:
    return [Anchor(name, file, lb, role) for name, file, lb, role in KNOWN_ANCHORS]


def candidate_list() -> list[dict[str, str]]:
    rows = candidate_file_list()
    # Keep a compact set; candidate_file_list already de-duplicates by file.
    return rows


def all_files(anchors: list[Anchor], candidates: list[dict[str, str]]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for anchor in anchors:
        if anchor.file not in seen:
            seen.add(anchor.file)
            out.append(anchor.file)
    for item in candidates:
        if item["file"] not in seen:
            seen.add(item["file"])
            out.append(item["file"])
    return out


def compute_world_energy(
    anchors: list[Anchor],
    metrics_by_file: dict[str, pd.DataFrame],
    worlds: pd.DataFrame,
    exclude_name: str | None,
    mode: str,
) -> pd.DataFrame:
    active = [a for a in anchors if a.name != exclude_name and a.file != A2C8_FILE]
    if not active:
        raise RuntimeError("no active anchors for world energy")
    rows = []
    for world_row in range(len(worlds)):
        per_anchor = []
        for anchor in active:
            m = metrics_by_file[anchor.file].iloc[world_row]
            delta_t = np.array([float(m[f"delta_{t}"]) for t in TARGETS], dtype=float)
            weights = np.array([float(m[f"move_weight_{t}"]) for t in TARGETS], dtype=float)
            weights = weights / max(float(weights.sum()), 1e-15)
            public_delta = anchor.delta_vs_a2c8
            sign = 1.0 if public_delta >= 0 else -1.0
            per_anchor.append(
                {
                    "residual": abs(float(m["delta_mean"]) - public_delta),
                    "cancellation": float(m["cancellation_ratio"]),
                    "positive_share": float(weights[(sign * delta_t) > 0].sum()),
                    "movement_loss_corr": float(m["movement_loss_abs_corr"]),
                    "target_entropy": float(m["target_delta_entropy"]),
                }
            )
        pdf = pd.DataFrame(per_anchor)
        rec = {
            "world_row": world_row,
            "world_id": worlds.loc[world_row, "world_id"],
            "objective": worlds.loc[world_row, "objective"],
            "source_role": worlds.loc[world_row, "source_role"],
            "exclude_name": exclude_name or "__all__",
            "mode": mode,
            "anchor_count": len(active),
            "residual_mean": float(pdf["residual"].mean()),
            "cancellation_mean": float(pdf["cancellation"].mean()),
            "positive_share_mean": float(pdf["positive_share"].mean()),
            "movement_loss_corr_mean": float(pdf["movement_loss_corr"].mean()),
            "target_entropy_mean": float(pdf["target_entropy"].mean()),
        }
        rows.append(rec)
    scored = pd.DataFrame(rows)
    scored["residual_rz"] = robust_z(scored["residual_mean"]).clip(-3, 6)
    scored["cancellation_rz"] = robust_z(scored["cancellation_mean"]).clip(-3, 6)
    scored["positive_gap_rz"] = robust_z(1.0 - scored["positive_share_mean"]).clip(-3, 6)
    scored["corr_gap_rz"] = robust_z(1.0 - scored["movement_loss_corr_mean"]).clip(-3, 6)
    if mode == "shape":
        scored["anchor_energy"] = scored["cancellation_rz"] + scored["positive_gap_rz"] + 0.5 * scored["corr_gap_rz"]
    elif mode == "residual":
        scored["anchor_energy"] = (
            scored["residual_rz"]
            + 0.75 * scored["cancellation_rz"]
            + scored["positive_gap_rz"]
            + 0.5 * scored["corr_gap_rz"]
        )
    else:
        raise ValueError(mode)
    scored["anchor_energy_rank"] = scored["anchor_energy"].rank(method="first", ascending=True).astype(int)
    scored["anchor_energy_quantile"] = scored["anchor_energy"].rank(pct=True, ascending=True)
    return scored


def aggregate_band_features(metrics: pd.DataFrame, energy: pd.DataFrame, prefix: str) -> dict[str, float]:
    merged = metrics.merge(
        energy[["world_row", "source_role", "anchor_energy", "anchor_energy_quantile"]],
        on="world_row",
        how="left",
        validate="one_to_one",
    )
    specs = {
        "all": np.ones(len(merged), dtype=bool),
        "low_half": merged["anchor_energy_quantile"].le(0.50).to_numpy(),
        "low_quarter": merged["anchor_energy_quantile"].le(0.25).to_numpy(),
        "low_random_fit": (
            merged["anchor_energy_quantile"].le(0.50) & merged["source_role"].isin(["random", "slack"])
        ).to_numpy(),
        "high_quarter": merged["anchor_energy_quantile"].ge(0.75).to_numpy(),
    }
    out: dict[str, float] = {}
    for band, mask in specs.items():
        sub = merged[mask].copy()
        if sub.empty:
            continue
        delta = sub["delta_mean"].to_numpy(float)
        out[f"{prefix}__{band}__worlds"] = float(len(sub))
        out[f"{prefix}__{band}__delta_mean"] = float(delta.mean())
        out[f"{prefix}__{band}__delta_median"] = float(np.median(delta))
        out[f"{prefix}__{band}__delta_std"] = float(delta.std(ddof=0))
        out[f"{prefix}__{band}__delta_min"] = float(delta.min())
        out[f"{prefix}__{band}__delta_q25"] = float(np.quantile(delta, 0.25))
        out[f"{prefix}__{band}__delta_q75"] = float(np.quantile(delta, 0.75))
        out[f"{prefix}__{band}__delta_max"] = float(delta.max())
        out[f"{prefix}__{band}__better_rate_vs_a2c8"] = float((delta < 0).mean())
        out[f"{prefix}__{band}__cancellation_mean"] = float(sub["cancellation_ratio"].mean())
        out[f"{prefix}__{band}__entropy_mean"] = float(sub["target_delta_entropy"].mean())
        out[f"{prefix}__{band}__movement_loss_corr_mean"] = float(sub["movement_loss_abs_corr"].mean())
        for target in TARGETS:
            vals = sub[f"delta_{target}"].to_numpy(float)
            out[f"{prefix}__{band}__{target}_delta_mean"] = float(vals.mean())
            out[f"{prefix}__{band}__{target}_delta_abs_mean"] = float(np.abs(vals).mean())
    low = merged[merged["anchor_energy_quantile"].le(0.50)]
    high = merged[merged["anchor_energy_quantile"].ge(0.75)]
    if not low.empty and not high.empty:
        out[f"{prefix}__low_minus_high_delta_mean"] = float(low["delta_mean"].mean() - high["delta_mean"].mean())
        out[f"{prefix}__low_minus_high_better_rate"] = float(
            (low["delta_mean"].lt(0).mean()) - (high["delta_mean"].lt(0).mean())
        )
    return out


def compact_calendar_columns(fp: pd.DataFrame, level: str) -> list[str]:
    id_cols = {"name", "file", "role", "public_lb", "public_delta_vs_mixmin"}
    cols = []
    for col in fp.columns:
        if col in id_cols or col.startswith("anchor_"):
            continue
        if col.startswith("all__") or col.startswith("prior__"):
            cols.append(col)
        elif level in {"context_all", "moved_targets"} and "__all__" in col:
            cols.append(col)
        elif level == "moved_targets" and any(f"__{t}__" in col for t in ["Q1", "Q3", "S1", "S3"]):
            cols.append(col)
    return cols


def build_feature_frame(
    rows: list[dict[str, Any]],
    calendar_fp: pd.DataFrame,
    metrics_by_file: dict[str, pd.DataFrame],
    energy: pd.DataFrame,
    mode: str,
) -> pd.DataFrame:
    cal = calendar_fp.set_index("file")
    out_rows = []
    for row in rows:
        file_name = row["file"]
        rec = dict(row)
        rec.update(cal.loc[file_name].drop(labels=[c for c in ["name", "role", "public_lb", "public_delta_vs_mixmin"] if c in cal.columns]).to_dict())
        rec.update(aggregate_band_features(metrics_by_file[file_name], energy, f"anchor_{mode}"))
        out_rows.append(rec)
    return pd.DataFrame(out_rows)


def feature_columns(frame: pd.DataFrame, view: str) -> list[str]:
    id_cols = {"name", "file", "role", "public_lb", "public_delta_vs_mixmin"}
    if view == "anchor_shape":
        return [c for c in frame.columns if c.startswith("anchor_shape__")]
    if view == "anchor_residual":
        return [c for c in frame.columns if c.startswith("anchor_residual__")]
    if view == "targetprior_anchor_shape":
        return compact_calendar_columns(frame, "target_prior") + [c for c in frame.columns if c.startswith("anchor_shape__")]
    if view == "targetprior_anchor_residual":
        return compact_calendar_columns(frame, "target_prior") + [c for c in frame.columns if c.startswith("anchor_residual__")]
    if view == "contextall_anchor_shape":
        return compact_calendar_columns(frame, "context_all") + [c for c in frame.columns if c.startswith("anchor_shape__")]
    if view == "contextall_anchor_residual":
        return compact_calendar_columns(frame, "context_all") + [c for c in frame.columns if c.startswith("anchor_residual__")]
    if view == "movedtargets_anchor_shape":
        return compact_calendar_columns(frame, "moved_targets") + [c for c in frame.columns if c.startswith("anchor_shape__")]
    if view == "movedtargets_anchor_residual":
        return compact_calendar_columns(frame, "moved_targets") + [c for c in frame.columns if c.startswith("anchor_residual__")]
    raise ValueError(view)


def predict_for_view(
    anchors: list[Anchor],
    calendar_fp: pd.DataFrame,
    metrics_by_file: dict[str, pd.DataFrame],
    worlds: pd.DataFrame,
    view: str,
) -> tuple[dict[str, Any], pd.DataFrame]:
    known_rows = [
        {
            "name": a.name,
            "file": a.file,
            "role": a.role,
            "public_lb": a.public_lb,
            "public_delta_vs_mixmin": a.delta_vs_mixmin,
        }
        for a in anchors
    ]
    pred = np.zeros(len(anchors), dtype=float)
    neigh_txt: list[str] = []
    for i, held in enumerate(anchors):
        mode = "residual" if view.endswith("residual") else "shape"
        energy = compute_world_energy(anchors, metrics_by_file, worlds, exclude_name=held.name, mode=mode)
        frame = build_feature_frame(known_rows, calendar_fp, metrics_by_file, energy, mode)
        cols = feature_columns(frame, view)
        x = frame[cols].to_numpy(dtype=float)
        y = frame["public_delta_vs_mixmin"].to_numpy(dtype=float)
        train_idx = np.array([j for j in range(len(anchors)) if j != i], dtype=int)
        p, neigh = predict_knn(x[train_idx], y[train_idx], x[[i]])
        pred[i] = p[0]
        neigh_txt.append(neigh[0])

    actual = np.array([a.delta_vs_mixmin for a in anchors], dtype=float)
    loocv = pd.DataFrame(
        {
            "view": view,
            "name": [a.name for a in anchors],
            "file": [a.file for a in anchors],
            "role": [a.role for a in anchors],
            "public_lb": [a.public_lb for a in anchors],
            "public_delta_vs_mixmin": actual,
            "predicted_delta": pred,
            "error": pred - actual,
            "abs_error": np.abs(pred - actual),
            "neighbor_indices": neigh_txt,
        }
    )
    pred_by_name = loocv.set_index("name")["predicted_delta"].to_dict()
    actual_by_name = loocv.set_index("name")["public_delta_vs_mixmin"].to_dict()
    mixmin_abs_error = float(loocv.loc[loocv["name"].eq("mixmin"), "abs_error"].iloc[0])
    summary: dict[str, Any] = {
        "view": view,
        "n_features": int(len(feature_columns(build_feature_frame(known_rows, calendar_fp, metrics_by_file, compute_world_energy(anchors, metrics_by_file, worlds, exclude_name=None, mode='residual' if view.endswith('residual') else 'shape'), 'residual' if view.endswith('residual') else 'shape'), view))),
        "loocv_mae": float(loocv["abs_error"].mean()),
        "loocv_max_abs_error": float(loocv["abs_error"].max()),
        "mixmin_abs_error": mixmin_abs_error,
        "pairwise_rank_accuracy": pairwise_rank_accuracy(actual, pred),
        "spearman": spearman_corr(actual, pred),
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
    # The feature frame itself is LOO-dependent because world energy excludes the
    # held-out anchor. A permutation-null loop would recompute that frame many
    # times and adds little beyond the direct known-anchor order checks here.
    summary["null_rank_p_ge_actual"] = np.nan
    summary["strict_selector_gate"] = bool(
        summary["loocv_mae"] <= 0.00070
        and summary["pairwise_rank_accuracy"] >= 0.80
        and summary["mixmin_predicted_best"]
        and summary["a2c8_raw05_order_correct"]
        and summary["stage2_ordinal_order_correct"]
        and summary["bad_tail_correct"]
        and summary["mixmin_error_below_edge"]
    )
    summary["loose_selector_gate"] = bool(
        summary["edge_scale_gate"]
        and summary["pairwise_rank_accuracy"] >= 0.70
        and summary["mixmin_predicted_best"]
        and summary["a2c8_raw05_order_correct"]
        and summary["bad_tail_correct"]
    )
    return summary, loocv


def candidate_predictions(
    anchors: list[Anchor],
    candidates: list[dict[str, str]],
    calendar_fp: pd.DataFrame,
    metrics_by_file: dict[str, pd.DataFrame],
    worlds: pd.DataFrame,
    view_summary: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    known_rows = [
        {
            "name": a.name,
            "file": a.file,
            "role": a.role,
            "public_lb": a.public_lb,
            "public_delta_vs_mixmin": a.delta_vs_mixmin,
        }
        for a in anchors
    ]
    query_rows = []
    for item in candidates:
        query_rows.append({"name": item["name"], "file": item["file"], "role": item["role"]})

    rows = []
    energy_rows = []
    for mode in ["shape", "residual"]:
        energy = compute_world_energy(anchors, metrics_by_file, worlds, exclude_name=None, mode=mode)
        energy_rows.append(energy)
        train_frame = build_feature_frame(known_rows, calendar_fp, metrics_by_file, energy, mode)
        query_frame = build_feature_frame(query_rows, calendar_fp, metrics_by_file, energy, mode)
        for view in [v for v in view_summary["view"].tolist() if v.endswith(mode)]:
            cols = feature_columns(train_frame, view)
            pred, neigh = predict_knn(
                train_frame[cols].to_numpy(dtype=float),
                train_frame["public_delta_vs_mixmin"].to_numpy(dtype=float),
                query_frame[cols].to_numpy(dtype=float),
            )
            part = query_frame[["name", "file", "role"]].copy()
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
    return out.sort_values(["view", "predicted_delta_vs_mixmin"]).reset_index(drop=True), pd.concat(energy_rows)


def write_report(view_summary: pd.DataFrame, loocv: pd.DataFrame, candidates: pd.DataFrame) -> None:
    strict_n = int(view_summary["strict_selector_gate"].sum())
    loose_n = int(view_summary["loose_selector_gate"].sum())
    best_view = view_summary.sort_values(
        ["strict_selector_gate", "loose_selector_gate", "loocv_mae"], ascending=[False, False, True]
    ).head(1)
    pivot = (
        candidates.pivot_table(index=["name", "file", "role"], columns="view", values="predicted_public_lb", aggfunc="first")
        .reset_index()
        .sort_values(best_view["view"].iloc[0])
    )
    pivot.columns = [str(c) for c in pivot.columns]

    lines = [
        "# E51 Post-Mixmin Anchor-Calendar Selector",
        "",
        "## Observe",
        "",
        "E50 falsified calendar-only selection: calendar topology is real, but it did not predict held-out mixmin as best.",
        "",
        "## Wonder",
        "",
        "Does subject-calendar context become selector-useful when combined with the binary-world anchor-loss geometry that selected mixmin before the public LB observation?",
        "",
        "## Hypothesis",
        "",
        "If the post-mixmin worldview is right, LOO-safe anchor-loss world aggregates should rescue mixmin-best prediction, and calendar context should improve or at least not degrade that anchor-loss selector.",
        "",
        "## Method",
        "",
        "- Reuse the E30 binary frontier-box worlds and compute every anchor/candidate's per-world LogLoss delta versus a2c8.",
        "- Score worlds by known-anchor energy in two LOO-safe modes: `shape` reproduces E32-style cancellation/sign/correlation energy, while `residual` also includes known-anchor residual fit.",
        "- For each held-out public anchor, omit that anchor from world-energy scoring before predicting it.",
        "- Concatenate low-energy world aggregate features with compact calendar fingerprints from E50.",
        "",
        "## Result",
        "",
        f"- strict selector views: `{strict_n}`.",
        f"- loose selector views: `{loose_n}`.",
        "",
        "## View Summary",
        "",
        df_to_markdown(view_summary),
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
            ].sort_values(["view", "public_delta_vs_mixmin"])
        ),
        "",
        "## Candidate Sensor Predictions",
        "",
        "These are not public forecasts unless a view passes the gate.",
        "",
        df_to_markdown(pivot.head(25)),
        "",
        "## Decision",
        "",
    ]
    if strict_n:
        lines.append("At least one strict anchor-calendar selector exists. It can be used as a candidate gate only after private-risk and targetwise calibration stress.")
    elif loose_n:
        lines.append("A loose selector exists, but not a strict one. Treat its candidate ordering as a public-sensor prior, not a submission forecast.")
    else:
        lines.append("The anchor-calendar combination still does not certify a selector. The missing object is likely a stronger block-rate/count target or a different anchor-world construction.")
    lines += [
        "",
        "## Outputs",
        "",
        f"- `{VIEW_OUT.relative_to(ROOT)}`",
        f"- `{LOOCV_OUT.relative_to(ROOT)}`",
        f"- `{CANDIDATE_OUT.relative_to(ROOT)}`",
        f"- `{FEATURE_OUT.relative_to(ROOT)}`",
        f"- `{WORLD_ENERGY_OUT.relative_to(ROOT)}`",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    anchors = known_anchor_list()
    candidates = candidate_list()
    worlds, labels = load_worlds()
    sample = read_submission(A2C8_FILE)
    base_prob = clip_prob(sample[TARGETS].to_numpy(dtype=float))

    context = make_context()
    masks = build_masks(context)
    raw05 = clip_prob(read_submission(RAW05_FILE)[TARGETS].to_numpy(dtype=float))

    files = all_files(anchors, candidates)
    calendar_rows = []
    metrics_by_file: dict[str, pd.DataFrame] = {}
    for file_name in files:
        resolve_file(file_name)
        calendar_rows.append(fingerprint_for_file(file_name, context, masks, base_prob, raw05))
        metrics_by_file[file_name] = file_world_metrics(file_name, sample, base_prob, labels)
    calendar_fp = pd.DataFrame(calendar_rows)
    meta_rows = [
        {"name": a.name, "file": a.file, "role": a.role, "public_lb": a.public_lb, "public_delta_vs_mixmin": a.delta_vs_mixmin}
        for a in anchors
    ]
    meta_rows.extend({"name": c["name"], "file": c["file"], "role": c["role"]} for c in candidates)
    meta = pd.DataFrame(meta_rows).drop_duplicates("file", keep="first")
    calendar_fp = calendar_fp.merge(meta, on="file", how="left", validate="one_to_one")

    view_rows = []
    loocv_rows = []
    views = [
        "anchor_shape",
        "anchor_residual",
        "targetprior_anchor_shape",
        "targetprior_anchor_residual",
        "contextall_anchor_shape",
        "contextall_anchor_residual",
        "movedtargets_anchor_shape",
        "movedtargets_anchor_residual",
    ]
    for view in views:
        summary, loocv = predict_for_view(anchors, calendar_fp, metrics_by_file, worlds, view)
        view_rows.append(summary)
        loocv_rows.append(loocv)
    view_summary = pd.DataFrame(view_rows).sort_values(
        ["strict_selector_gate", "loose_selector_gate", "loocv_mae"], ascending=[False, False, True]
    )
    loocv_all = pd.concat(loocv_rows, axis=0, ignore_index=True)
    candidates_out, energy_out = candidate_predictions(anchors, candidates, calendar_fp, metrics_by_file, worlds, view_summary)
    known_rows = [
        {
            "name": a.name,
            "file": a.file,
            "role": a.role,
            "public_lb": a.public_lb,
            "public_delta_vs_mixmin": a.delta_vs_mixmin,
        }
        for a in anchors
    ]
    full_residual_energy = compute_world_energy(anchors, metrics_by_file, worlds, exclude_name=None, mode="residual")
    known_feature_frame = build_feature_frame(known_rows, calendar_fp, metrics_by_file, full_residual_energy, "residual")

    view_summary.to_csv(VIEW_OUT, index=False)
    loocv_all.to_csv(LOOCV_OUT, index=False)
    candidates_out.to_csv(CANDIDATE_OUT, index=False)
    known_feature_frame.to_csv(FEATURE_OUT, index=False)
    energy_out.to_csv(WORLD_ENERGY_OUT, index=False)
    write_report(view_summary, loocv_all, candidates_out)

    print(
        f"views={len(view_summary)} strict={int(view_summary['strict_selector_gate'].sum())} "
        f"loose={int(view_summary['loose_selector_gate'].sum())}"
    )
    print(view_summary.to_string(index=False))
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
