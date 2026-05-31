#!/usr/bin/env python3
"""E313: human-diary action signature.

E312 found that candidate action health is mostly predictable from action
geometry. That is useful as a public-free blocker, but it leaves a precise
question open:

    Does the raw human diary state of the rows touched by a candidate add any
    held-out signal beyond the movement geometry?

This script projects every governed candidate delta onto test-side human diary
features from E268/E270/E273, then evaluates those action signatures under
leave-experiment-out stress. No public LB is used and no submission is created.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e312_action_health_world_model import feature_blocks, leave_experiment_out, md  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
Q_TARGETS = ["Q1", "Q2", "Q3"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-5
MAX_HUMAN_AGG_COLS = 520

CURRENT_PATH = OUT / "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
E312_ALL = OUT / "e312_action_health_all.csv"
STORY_PATH = OUT / "e268_human_social_story_features.parquet"
CASH_PATH = OUT / "e270_payday_cashflow_story_features.parquet"
DIARY_PATH = OUT / "e273_human_diary_state_jepa_audit_features.parquet"

FEATURE_OUT = OUT / "e313_human_action_signature_features.csv"
METRICS_OUT = OUT / "e313_human_action_signature_metrics.csv"
OOF_OUT = OUT / "e313_human_action_signature_oof.csv"
SLICE_OUT = OUT / "e313_human_action_signature_slice_metrics.csv"
TOP_FEATURE_OUT = OUT / "e313_human_action_signature_top_features.csv"
READINESS_OUT = OUT / "e313_human_action_signature_readiness_readout.csv"
REPORT_OUT = OUT / "e313_human_action_signature_report.md"


def safe_name(text: str) -> str:
    text = re.sub(r"[^0-9A-Za-z_]+", "_", str(text))
    return re.sub(r"_+", "_", text).strip("_")


def logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p.astype(float), EPS, 1.0 - EPS)
    return np.log(p / (1.0 - p))


def experiment_num(exp: str) -> int:
    match = re.search(r"(\d+)", str(exp))
    return int(match.group(1)) if match else -1


def candidate_paths() -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for path in sorted(OUT.rglob("submission*.csv"), key=lambda p: (len(str(p)), str(p))):
        paths.setdefault(path.name, path)
    return paths


def usable_numeric_columns(df: pd.DataFrame, source: str) -> list[str]:
    exclude = set(KEYS + ["split", "dateblock_group"] + TARGETS)
    cols: list[str] = []
    for col in df.columns:
        if col in exclude:
            continue
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue
        if source == "story":
            if col in {"weekday", "is_weekend", "subject_order"}:
                cols.append(col)
            elif col.endswith("_subj_z") and "_abs_" not in col:
                cols.append(col)
            elif not col.endswith(("_abs_subj_z", "_weekend")) and col not in {"weekday", "is_weekend", "subject_order"}:
                cols.append(col)
        elif source == "cash":
            if col in {"weekday", "is_weekend", "lifelog_dom", "subject_order"}:
                cols.append(col)
            elif col.endswith("_subj_z") or col.endswith("_active"):
                cols.append(col)
        elif source == "diary":
            keep = (
                col in {"subject_order", "weekday", "is_weekend", "lifelog_dom", "lifelog_month"}
                or col.endswith("_energy")
                or "_pc" in col
                or col.startswith("jepa_resid_")
                or col.startswith("jepa_prednorm_")
                or col.startswith("diary_state_")
            )
            if keep:
                cols.append(col)
    return list(dict.fromkeys(cols))


def prefixed_test_frame(path: Path, source: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df = df[df["split"].astype(str).eq("test")].copy()
    cols = usable_numeric_columns(df, source)
    out = df[KEYS + cols].copy()
    rename = {c: f"{source}__{safe_name(c)}" for c in cols}
    return out.rename(columns=rename)


def load_human_matrix(current: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    base = current[KEYS].copy()
    for path, source in [(STORY_PATH, "story"), (CASH_PATH, "cash"), (DIARY_PATH, "diary")]:
        frame = prefixed_test_frame(path, source)
        before = len(base)
        base = base.merge(frame, on=KEYS, how="left", validate="one_to_one")
        if len(base) != before:
            raise RuntimeError(f"row count changed while merging {path}")
    human_cols = [c for c in base.columns if c not in KEYS]
    if base[human_cols].isna().all(axis=None):
        raise RuntimeError("human feature merge produced all missing values")
    values = base[human_cols].apply(pd.to_numeric, errors="coerce")
    med = values.median(axis=0, skipna=True).fillna(0.0)
    values = values.fillna(med)
    std = values.std(axis=0, ddof=0).replace(0.0, 1.0).fillna(1.0)
    values = (values - values.mean(axis=0)) / std
    values = values.replace([np.inf, -np.inf], 0.0).fillna(0.0)
    return values.reset_index(drop=True), list(values.columns)


def weighted_mean(x: np.ndarray, w: np.ndarray) -> np.ndarray:
    denom = float(np.sum(np.abs(w)))
    if denom <= 1e-12:
        return np.zeros(x.shape[1], dtype=np.float64)
    return (x * w[:, None]).sum(axis=0) / denom


def active_mean(x: np.ndarray, mask: np.ndarray) -> np.ndarray:
    if not np.any(mask):
        return np.zeros(x.shape[1], dtype=np.float64)
    return x[mask].mean(axis=0)


def delta_signature(path: Path | None, current_logit: np.ndarray, human: pd.DataFrame, human_cols: list[str]) -> tuple[dict[str, Any], dict[str, float]]:
    if path is None or not path.exists():
        shape = {
            "candidate_file_found": 0.0,
            "changed_cells": 0.0,
            "changed_rows": 0.0,
            "abs_logit_l1": 0.0,
            "max_abs_logit": 0.0,
            "row_l1_top1_share": 0.0,
            "row_l1_top5_share": 0.0,
            "q_abs_share": 0.0,
            "s_abs_share": 0.0,
            "signed_logit_sum": 0.0,
        }
        return shape, {}

    cand = pd.read_csv(path)
    if len(cand) != len(human):
        raise RuntimeError(f"{path} has {len(cand)} rows, expected {len(human)}")
    cand_logit = logit(cand[TARGETS].to_numpy(dtype=float))
    delta = cand_logit - current_logit
    abs_delta = np.abs(delta)
    row_abs = abs_delta.sum(axis=1)
    q_abs = abs_delta[:, : len(Q_TARGETS)].sum(axis=1)
    s_abs = abs_delta[:, len(Q_TARGETS) :].sum(axis=1)
    signed_row = delta.sum(axis=1)
    changed_cells = int((abs_delta > 1e-10).sum())
    changed_rows = int((row_abs > 1e-10).sum())
    total_l1 = float(row_abs.sum())
    sorted_rows = np.sort(row_abs)[::-1]
    shape = {
        "candidate_file_found": 1.0,
        "changed_cells": float(changed_cells),
        "changed_rows": float(changed_rows),
        "abs_logit_l1": total_l1,
        "max_abs_logit": float(abs_delta.max()) if abs_delta.size else 0.0,
        "row_l1_top1_share": float(sorted_rows[:1].sum() / total_l1) if total_l1 > 0 else 0.0,
        "row_l1_top5_share": float(sorted_rows[:5].sum() / total_l1) if total_l1 > 0 else 0.0,
        "q_abs_share": float(q_abs.sum() / total_l1) if total_l1 > 0 else 0.0,
        "s_abs_share": float(s_abs.sum() / total_l1) if total_l1 > 0 else 0.0,
        "signed_logit_sum": float(delta.sum()),
    }
    if total_l1 <= 1e-12:
        return shape, {}

    x = human.to_numpy(dtype=np.float64)
    active = row_abs > 1e-10
    absw = weighted_mean(x, row_abs)
    signw = weighted_mean(x, signed_row)
    act = active_mean(x, active)
    qmean = weighted_mean(x, q_abs)
    smean = weighted_mean(x, s_abs)
    sig: dict[str, float] = {}
    for col, a, b, c, q, s in zip(human_cols, absw, signw, act, qmean, smean, strict=False):
        short = safe_name(col)
        sig[f"human_absw__{short}"] = float(a)
        sig[f"human_signed__{short}"] = float(b)
        sig[f"human_active__{short}"] = float(c)
        sig[f"human_q_minus_s__{short}"] = float(q - s)
    return shape, sig


def build_signatures() -> pd.DataFrame:
    e312 = pd.read_csv(E312_ALL)
    current = pd.read_csv(CURRENT_PATH)
    human, human_cols = load_human_matrix(current)
    current_logit = logit(current[TARGETS].to_numpy(dtype=float))
    path_map = candidate_paths()

    rows: list[dict[str, Any]] = []
    for idx, rec in e312.iterrows():
        basename = str(rec.get("basename", ""))
        path = path_map.get(basename)
        shape, sig = delta_signature(path, current_logit, human, human_cols)
        out = rec.to_dict()
        out.update({f"shape__{k}": v for k, v in shape.items()})
        out.update(sig)
        out["candidate_path_found"] = bool(path is not None)
        rows.append(out)
    combined = pd.DataFrame(rows)

    human_agg_cols = [c for c in combined.columns if c.startswith("human_")]
    if len(human_agg_cols) > MAX_HUMAN_AGG_COLS:
        std = combined[human_agg_cols].std(axis=0, ddof=0).fillna(0.0).sort_values(ascending=False)
        keep = set(std.head(MAX_HUMAN_AGG_COLS).index)
        drop = [c for c in human_agg_cols if c not in keep]
        combined = combined.drop(columns=drop)
    combined.attrs["raw_human_feature_count"] = len(human_cols)
    combined.attrs["selected_human_agg_count"] = len([c for c in combined.columns if c.startswith("human_")])
    return combined


def slice_metrics(df: pd.DataFrame, oof: pd.DataFrame) -> pd.DataFrame:
    meta = df[["experiment", "selector_visible", "null_common", "null_rare", "action_cliff", "actual_p90"]].reset_index().rename(columns={"index": "row_idx"})
    pred = oof.merge(meta, on="row_idx", how="left")
    rows: list[dict[str, Any]] = []
    for block in sorted(pred["feature_block"].unique()):
        for task in ["null_common", "null_rare", "action_cliff"]:
            sub = pred[(pred["feature_block"].eq(block)) & (pred["task"].eq(task))].copy()
            if sub.empty:
                continue
            for name, mask in {
                "all": np.ones(len(sub), dtype=bool),
                "selector_visible": sub["selector_visible"].astype(bool).to_numpy(),
                "old_edge_negative": sub["actual_p90"].fillna(0.0).to_numpy() < 0,
                "e310_e311": sub["experiment"].isin(["e310", "e311"]).to_numpy(),
            }.items():
                s = sub.loc[mask]
                if len(s) < 10 or s["label"].nunique(dropna=True) < 2:
                    continue
                from sklearn.metrics import average_precision_score, roc_auc_score

                rows.append(
                    {
                        "feature_block": block,
                        "task": task,
                        "slice": name,
                        "n": int(len(s)),
                        "positive_rate": float(s["label"].mean()),
                        "auc": float(roc_auc_score(s["label"].astype(int), s["oof_pred"].astype(float))),
                        "average_precision": float(average_precision_score(s["label"].astype(int), s["oof_pred"].astype(float))),
                        "pred_mean": float(s["oof_pred"].mean()),
                    }
                )
    return pd.DataFrame(rows)


def top_human_coefficients(df: pd.DataFrame, human_cols: list[str]) -> pd.DataFrame:
    y = df["null_common"].astype(int).to_numpy()
    if len(np.unique(y)) < 2 or not human_cols:
        return pd.DataFrame()
    x = df[human_cols].copy()
    model = make_pipeline(
        ColumnTransformer(
            [("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), human_cols)],
            remainder="drop",
        ),
        LogisticRegression(C=0.18, max_iter=2500, solver="liblinear", class_weight="balanced"),
    )
    model.fit(x, y)
    coef = model.named_steps["logisticregression"].coef_[0]
    out = pd.DataFrame({"feature": human_cols, "coef_null_common": coef})
    out["abs_coef"] = out["coef_null_common"].abs()
    return out.sort_values("abs_coef", ascending=False).head(80).reset_index(drop=True)


def readiness_readout(df: pd.DataFrame, oof: pd.DataFrame) -> pd.DataFrame:
    sub = oof[oof["task"].eq("readiness_distance")].copy()
    if sub.empty:
        return pd.DataFrame()
    pivot = sub.pivot_table(index="row_idx", columns="feature_block", values="oof_pred", aggfunc="first").reset_index()
    pivot = pivot.rename(columns={c: f"pred_ready__{c}" for c in pivot.columns if c != "row_idx"})
    meta_cols = [
        "experiment",
        "basename",
        "family",
        "target_norm",
        "selector_visible",
        "null_rare",
        "null_common",
        "visible_null_common",
        "visible_null_rare",
        "strict_health",
        "actual_p90",
        "null_strict_rate",
        "readiness_distance",
        "failure_mode",
    ]
    meta = df[[c for c in meta_cols if c in df.columns]].reset_index().rename(columns={"index": "row_idx"})
    out = meta.merge(pivot, on="row_idx", how="left")
    if "pred_ready__human_signature" in out.columns:
        out["human_ready_rank"] = out["pred_ready__human_signature"].rank(method="average")
    if "pred_ready__geometry_only" in out.columns:
        out["geometry_ready_rank"] = out["pred_ready__geometry_only"].rank(method="average")
    sort_cols = [c for c in ["pred_ready__human_signature", "readiness_distance", "actual_p90"] if c in out.columns]
    return out.sort_values(sort_cols, ascending=True).reset_index(drop=True)


def run_models(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    derived_prefixes = ("human_", "shape__")
    base_cols = [c for c in df.columns if not c.startswith(derived_prefixes) and c != "candidate_path_found"]
    e312_blocks = feature_blocks(df[base_cols].copy())
    human_cols = [c for c in df.columns if c.startswith("human_")]
    shape_cols = [c for c in df.columns if c.startswith("shape__")]
    blocks: dict[str, tuple[list[str], list[str]]] = {
        "human_signature": (human_cols, []),
        "shape_signature": (shape_cols, []),
        "human_plus_shape": (human_cols + shape_cols, []),
        "geometry_only": e312_blocks["geometry_only"],
        "geometry_plus_shape": (list(dict.fromkeys(e312_blocks["geometry_only"][0] + shape_cols)), e312_blocks["geometry_only"][1]),
        "geometry_plus_human": (list(dict.fromkeys(e312_blocks["geometry_only"][0] + human_cols)), e312_blocks["geometry_only"][1]),
        "geometry_shape_human": (list(dict.fromkeys(e312_blocks["geometry_only"][0] + shape_cols + human_cols)), e312_blocks["geometry_only"][1]),
        "semantic_plus_human": (list(dict.fromkeys(e312_blocks["semantic_only"][0] + human_cols)), e312_blocks["semantic_only"][1]),
    }
    oof_frames: list[pd.DataFrame] = []
    metric_frames: list[pd.DataFrame] = []
    for name, (num_cols, cat_cols) in blocks.items():
        if not num_cols and not cat_cols:
            continue
        oof, metrics = leave_experiment_out(df, name, num_cols, cat_cols)
        oof_frames.append(oof)
        metric_frames.append(metrics)
    oof_all = pd.concat(oof_frames, ignore_index=True)
    metrics_all = pd.concat(metric_frames, ignore_index=True)
    slices = slice_metrics(df, oof_all)
    tops = top_human_coefficients(df, human_cols)
    return oof_all, metrics_all, slices, tops


def write_report(df: pd.DataFrame, metrics: pd.DataFrame, slices: pd.DataFrame, tops: pd.DataFrame, readiness: pd.DataFrame) -> None:
    global_metrics = metrics[metrics["heldout_experiment"].eq("__global_oof__")].copy()
    global_metrics["task_order"] = global_metrics["task"].map(
        {"null_common": 0, "null_rare": 1, "visible_null_common": 2, "action_cliff": 3, "safe_invisible": 4, "strict_health": 5, "null_strict_rate": 6, "readiness_distance": 7, "actual_p90": 8}
    ).fillna(99)
    global_metrics = global_metrics.sort_values(["task_order", "feature_block"])
    null_common = global_metrics[global_metrics["task"].eq("null_common")].copy()
    pivot = null_common.pivot_table(index="feature_block", values=["auc", "average_precision", "pred_mean"], aggfunc="first").reset_index()
    geo_auc = float(pivot.loc[pivot["feature_block"].eq("geometry_only"), "auc"].iloc[0])
    gph_auc = float(pivot.loc[pivot["feature_block"].eq("geometry_shape_human"), "auc"].iloc[0])
    human_auc = float(pivot.loc[pivot["feature_block"].eq("human_signature"), "auc"].iloc[0])
    ready = global_metrics[global_metrics["task"].eq("readiness_distance")].copy()
    ready_pivot = ready.pivot_table(index="feature_block", values=["mae", "spearman", "pred_mean"], aggfunc="first").reset_index()
    human_ready = float(ready_pivot.loc[ready_pivot["feature_block"].eq("human_signature"), "spearman"].iloc[0])
    geo_ready = float(ready_pivot.loc[ready_pivot["feature_block"].eq("geometry_only"), "spearman"].iloc[0])
    found = int(df["candidate_path_found"].sum())
    human_cols = [c for c in df.columns if c.startswith("human_")]
    top_ready_cols = [
        "experiment",
        "basename",
        "family",
        "target_norm",
        "selector_visible",
        "null_rare",
        "null_common",
        "actual_p90",
        "null_strict_rate",
        "readiness_distance",
        "pred_ready__human_signature",
        "pred_ready__geometry_only",
        "failure_mode",
    ]

    lines = [
        "# E313 Human-Diary Action Signature",
        "",
        "Public LB는 사용하지 않았다. 후보 submission delta를 test-side human diary feature에 투영해서, 실제로 건드린 row의 생활 맥락이 action-health를 설명하는지 검증했다.",
        "",
        "## Data",
        "",
        f"- governed rows: `{len(df)}`",
        f"- candidate files found: `{found}` / `{len(df)}`",
        f"- selected human aggregate columns: `{len(human_cols)}`",
        f"- selector_visible: `{int(df['selector_visible'].sum())}`",
        f"- null_rare: `{int(df['null_rare'].sum())}`",
        f"- visible_null_rare: `{int(df['visible_null_rare'].sum())}`",
        f"- strict_health: `{int(df['strict_health'].sum())}`",
        "",
        "## Global Leave-Experiment-Out Metrics",
        "",
        md(
            global_metrics[
                [
                    "feature_block",
                    "task",
                    "n_valid",
                    "positive_rate",
                    "auc",
                    "average_precision",
                    "mae",
                    "spearman",
                    "pred_mean",
                ]
            ],
            n=120,
        ),
        "",
        "## Null-Common Readout",
        "",
        md(pivot.sort_values("auc", ascending=False), n=20),
        "",
        "## Readiness-Distance Readout",
        "",
        md(ready_pivot.sort_values("spearman", ascending=False), n=20),
        "",
        "## Top Human-Readiness Rows",
        "",
        md(readiness[[c for c in top_ready_cols if c in readiness.columns]], n=25),
        "",
        "## Slice Metrics",
        "",
        md(slices.sort_values(["task", "slice", "auc"], ascending=[True, True, False]), n=80),
        "",
        "## Top Human Signature Coefficients For Null-Common",
        "",
        md(tops[["feature", "coef_null_common", "abs_coef"]], n=40),
        "",
        "## Decision",
        "",
        f"- human_signature null_common AUC: `{human_auc:.6f}`",
        f"- geometry_only null_common AUC: `{geo_auc:.6f}`",
        f"- geometry_shape_human null_common AUC: `{gph_auc:.6f}`",
        f"- human incremental AUC over geometry: `{gph_auc - geo_auc:+.6f}`",
        f"- human_signature readiness-distance Spearman: `{human_ready:.6f}`",
        f"- geometry_only readiness-distance Spearman: `{geo_ready:.6f}`",
    ]
    if gph_auc > geo_auc + 0.005:
        lines.append("- Human row placement adds held-out action-health signal beyond geometry. Next step: use these signatures as a hard veto/gate for a new materializer.")
    elif human_auc > 0.80 and gph_auc <= geo_auc + 0.005:
        lines.append("- Human row placement is predictive by itself but does not improve over action geometry. Treat it as a diagnostic story lens, not a submission certifier.")
    else:
        lines.append("- Human row placement does not currently rescue the action-health bottleneck. The next action should change the materializer/target, not add more story labels to the same action geometry.")
    lines.extend(
        [
            "- No submission is selected by E313.",
            "",
            "## Outputs",
            "",
            f"- `{FEATURE_OUT.relative_to(ROOT)}`",
            f"- `{METRICS_OUT.relative_to(ROOT)}`",
            f"- `{OOF_OUT.relative_to(ROOT)}`",
            f"- `{SLICE_OUT.relative_to(ROOT)}`",
            f"- `{TOP_FEATURE_OUT.relative_to(ROOT)}`",
            f"- `{READINESS_OUT.relative_to(ROOT)}`",
            f"- `{REPORT_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df = build_signatures()
    oof, metrics, slices, tops = run_models(df)
    df.to_csv(FEATURE_OUT, index=False)
    metrics.to_csv(METRICS_OUT, index=False)
    oof.to_csv(OOF_OUT, index=False)
    slices.to_csv(SLICE_OUT, index=False)
    tops.to_csv(TOP_FEATURE_OUT, index=False)
    readiness = readiness_readout(df, oof)
    readiness.to_csv(READINESS_OUT, index=False)
    write_report(df, metrics, slices, tops, readiness)

    global_metrics = metrics[metrics["heldout_experiment"].eq("__global_oof__")]

    def val(block: str, task: str, col: str) -> float:
        vals = global_metrics.loc[
            global_metrics["feature_block"].eq(block) & global_metrics["task"].eq(task),
            col,
        ]
        return float(vals.iloc[0]) if len(vals) and pd.notna(vals.iloc[0]) else np.nan

    print(f"rows={len(df)} files_found={int(df['candidate_path_found'].sum())}")
    print(f"human_cols={len([c for c in df.columns if c.startswith('human_')])}")
    print(f"human_null_common_auc={val('human_signature','null_common','auc'):.6f}")
    print(f"geometry_null_common_auc={val('geometry_only','null_common','auc'):.6f}")
    print(f"geometry_shape_human_null_common_auc={val('geometry_shape_human','null_common','auc'):.6f}")
    print(f"human_readiness_spearman={val('human_signature','readiness_distance','spearman'):.6f}")
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
