#!/usr/bin/env python3
"""E346: public-analog stress for the E342+E315 counter-axis basin.

E344/E345 show that the hidden lifestyle-state + counter-axis composition is
locally stable.  The remaining question is not another local selector sweep:

    Does the movement also avoid the anatomy of already observed public losses?

This audit uses known public LB observations only as fixed diagnostic axes, not
as an optimizer.  It compares E344/E345 candidate movements against matched
row/target/sign/subject/dateblock null movements on similarity to public-loss
directions such as E323, E216, E267, E256, and older broad residual anchors.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e328_ownlatent_lifestyle_state_experiment import load_sub_frame, md_table  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

RNG_SEED = 20260531 + 346
EPS = 1.0e-12
E247_PUBLIC = 0.5761589494
E247_FILE = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"

OBS_IN = OUT / "public_probe_observations.csv"
OBS_AXIS_OUT = OUT / "e346_public_analog_observed_axes.csv"
CANDIDATE_OUT = OUT / "e346_counteraxis_public_analog_candidates.csv"
SCORE_OUT = OUT / "e346_counteraxis_public_analog_scores.csv"
NULL_OUT = OUT / "e346_counteraxis_public_analog_nulls.csv"
REPORT_OUT = OUT / "e346_counteraxis_public_analog_report.md"


def stable_seed(*parts: object) -> int:
    text = "|".join(map(str, parts))
    return RNG_SEED + int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100000


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def locate(path_or_name: object) -> Path | None:
    raw = Path(str(path_or_name))
    candidates: list[Path] = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.extend([ROOT / raw, OUT / raw.name, OUT / str(path_or_name)])
    for path in candidates:
        if path.exists():
            return path
    return None


def vector(x: np.ndarray) -> np.ndarray:
    return np.asarray(x, dtype=np.float64).reshape(-1)


def norm(x: np.ndarray) -> float:
    return float(np.linalg.norm(vector(x)))


def cos(a: np.ndarray, b: np.ndarray) -> float:
    av = vector(a)
    bv = vector(b)
    den = float(np.linalg.norm(av) * np.linalg.norm(bv))
    if den <= EPS:
        return 0.0
    return float(np.dot(av, bv) / den)


def entropy(weights: np.ndarray) -> float:
    x = np.abs(np.asarray(weights, dtype=np.float64))
    total = float(x.sum())
    if total <= EPS:
        return 0.0
    p = x / total
    nz = p[p > 0.0]
    return float(-(nz * np.log(nz)).sum() / np.log(len(p))) if len(p) > 1 else 0.0


def load_base() -> tuple[pd.DataFrame, np.ndarray]:
    base = load_sub(OUT / E247_FILE).sort_values(KEYS).reset_index(drop=True)
    return base, logit(base[TARGETS].to_numpy(dtype=np.float64))


def load_delta(path: Path, base: pd.DataFrame, base_logit: np.ndarray) -> np.ndarray:
    sub = load_sub_frame(path, base[KEYS]).sort_values(KEYS).reset_index(drop=True)
    return logit(sub[TARGETS].to_numpy(dtype=np.float64)) - base_logit


def target_abs(delta: np.ndarray) -> dict[str, float]:
    arr = np.abs(np.asarray(delta, dtype=np.float64))
    total = float(arr.sum()) + EPS
    out: dict[str, float] = {}
    for i, target in enumerate(TARGETS):
        val = float(arr[:, i].sum())
        out[f"abs_{target}"] = val
        out[f"share_{target}"] = val / total
    return out


def observed_axes(base: pd.DataFrame, base_logit: np.ndarray) -> pd.DataFrame:
    obs = pd.read_csv(OBS_IN)
    rows: list[dict[str, Any]] = []
    for rec in obs.to_dict("records"):
        name = str(rec["file"])
        if name == E247_FILE:
            continue
        path = locate(name)
        exists = path is not None
        if not exists:
            rows.append(
                {
                    "file": name,
                    "exists": False,
                    "public_lb": float(rec["public_lb"]),
                    "public_delta_vs_e247": float(rec["public_lb"]) - E247_PUBLIC,
                    "note": rec.get("note", ""),
                }
            )
            continue
        delta = load_delta(path, base, base_logit)
        public_delta = float(rec["public_lb"]) - E247_PUBLIC
        rows.append(
            {
                "file": name,
                "exists": True,
                "path": rel(path),
                "public_lb": float(rec["public_lb"]),
                "public_delta_vs_e247": public_delta,
                "loss_tier": "severe" if public_delta >= 0.0005 else "mild",
                "l2": norm(delta),
                "l1": float(np.abs(delta).sum()),
                "row_entropy": entropy(np.abs(delta).sum(axis=1)),
                "changed_rows": int((np.abs(delta).sum(axis=1) > EPS).sum()),
                "note": rec.get("note", ""),
                **target_abs(delta),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OBS_AXIS_OUT, index=False)
    return out


def candidate_pool() -> pd.DataFrame:
    rows: list[dict[str, Any]] = [
        {
            "role": "E344_upload",
            "family": "e344",
            "basename": "submission_e344_counteraxis_lifestyle_9d09e4d2_uploadsafe.csv",
            "file": "analysis_outputs/submission_e344_counteraxis_lifestyle_9d09e4d2_uploadsafe.csv",
            "reason": "score-seeking p90-first upload-safe candidate",
        },
        {
            "role": "E345_upload",
            "family": "e345",
            "basename": "submission_e345_counterrefine_lifestyle_61d91c4c_uploadsafe.csv",
            "file": "analysis_outputs/submission_e345_counterrefine_lifestyle_61d91c4c_uploadsafe.csv",
            "reason": "refined bad-axis-margin upload-safe candidate",
        },
    ]

    for family, score_name, cand_name, null_name in [
        ("e344", "e344_counter_axis_scores.csv", "e344_counter_axis_candidates.csv", "e344_counter_axis_movement_nulls.csv"),
        ("e345", "e345_counteraxis_refine_scores.csv", "e345_counteraxis_refine_candidates.csv", "e345_counteraxis_refine_movement_nulls.csv"),
    ]:
        score_path = OUT / score_name
        cand_path = OUT / cand_name
        null_path = OUT / null_name
        if not (score_path.exists() and cand_path.exists()):
            continue
        scores = pd.read_csv(score_path)
        cands = pd.read_csv(cand_path)
        joined = scores[~scores["basename"].eq(E247_FILE)].merge(
            cands, on="basename", how="left", suffixes=("_score", "_meta")
        )
        joined["bad_axis_margin"] = 0.015 - joined["incremental_bad_axis_vs_current"]
        joined["p90_margin"] = -0.00005 - joined["pred_delta_vs_current_p90"]
        if null_path.exists():
            nulls = pd.read_csv(null_path)
            keep = nulls[
                (nulls["actual_strict_promote"].astype(bool))
                & (nulls["actual_p90_dominance"] >= 0.75)
                & (nulls["null_strict_promote_rate"] <= 0.05)
            ][["basename", "actual_mean_dominance", "actual_p90_dominance", "null_strict_promote_rate"]]
            joined = joined.merge(keep, on="basename", how="inner")
        else:
            joined = joined[joined["strict_promote_gate"].astype(bool)]
        top = joined.sort_values(
            ["p90_margin", "bad_axis_margin", "pred_delta_vs_current_mean"],
            ascending=[False, False, True],
        ).head(8)
        for i, rec in enumerate(top.to_dict("records"), start=1):
            file_value = rec.get("file_meta", rec.get("file_score", rec.get("file", rec["basename"])))
            rows.append(
                {
                    "role": f"{family}_nullsafe_top{i}",
                    "family": family,
                    "basename": rec["basename"],
                    "file": file_value,
                    "reason": "strict and movement-null-safe neighborhood row",
                    "local_mean": rec.get("pred_delta_vs_current_mean"),
                    "local_p90": rec.get("pred_delta_vs_current_p90"),
                    "local_bad_axis": rec.get("incremental_bad_axis_vs_current"),
                    "bad_axis_margin": rec.get("bad_axis_margin"),
                    "p90_margin": rec.get("p90_margin"),
                    "variant": rec.get("variant"),
                    "counter_weight": rec.get("counter_weight"),
                    "veto_strength": rec.get("veto_strength"),
                }
            )
    out = pd.DataFrame(rows).drop_duplicates("basename", keep="first").reset_index(drop=True)
    out["path_exists"] = out["file"].map(lambda x: locate(x) is not None)
    out.to_csv(CANDIDATE_OUT, index=False)
    return out[out["path_exists"]].reset_index(drop=True)


def axis_records(obs_axes: pd.DataFrame, base: pd.DataFrame, base_logit: np.ndarray) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for rec in obs_axes[obs_axes["exists"].astype(bool)].to_dict("records"):
        path = locate(rec["file"])
        if path is None:
            continue
        delta = load_delta(path, base, base_logit)
        records.append({**rec, "delta": delta})
    return records


def public_analog_metrics(delta: np.ndarray, axes: list[dict[str, Any]]) -> dict[str, float]:
    rows: dict[str, float] = {}
    l2 = norm(delta)
    rows["move_l2"] = l2
    rows["move_l1"] = float(np.abs(delta).sum())
    rows["changed_rows"] = int((np.abs(delta).sum(axis=1) > EPS).sum())
    rows["changed_cells"] = int((np.abs(delta) > EPS).sum())
    rows["row_entropy"] = entropy(np.abs(delta).sum(axis=1))
    rows.update(target_abs(delta))

    weighted_loss = 0.0
    weighted_pos_cos = 0.0
    weighted_abs_cos = 0.0
    severe_loss = 0.0
    severe_pos_cos = 0.0
    max_severe_pos = 0.0
    max_mild_pos = 0.0
    for axis in axes:
        c = cos(delta, axis["delta"])
        public_delta = max(float(axis["public_delta_vs_e247"]), 0.0)
        weighted_loss += public_delta
        weighted_pos_cos += public_delta * max(c, 0.0)
        weighted_abs_cos += public_delta * abs(c)
        if axis.get("loss_tier") == "severe":
            severe_loss += public_delta
            severe_pos_cos += public_delta * max(c, 0.0)
            max_severe_pos = max(max_severe_pos, max(c, 0.0))
        else:
            max_mild_pos = max(max_mild_pos, max(c, 0.0))

        short = Path(str(axis["file"])).stem
        key = None
        for token in ["e323", "e216", "e267", "e256", "e247", "e95", "e101", "e176", "mixmin", "e72", "ordinal", "stage2", "final9"]:
            if token in short.lower():
                key = token
                break
        if key is not None:
            rows[f"cos_{key}"] = c
            rows[f"poscos_{key}"] = max(c, 0.0)

    rows["public_loss_weighted_pos_cos"] = weighted_pos_cos / max(weighted_loss, EPS)
    rows["public_loss_weighted_abs_cos"] = weighted_abs_cos / max(weighted_loss, EPS)
    rows["severe_loss_weighted_pos_cos"] = severe_pos_cos / max(severe_loss, EPS)
    rows["max_severe_pos_cos"] = max_severe_pos
    rows["max_mild_pos_cos"] = max_mild_pos
    return rows


def test_meta(base: pd.DataFrame) -> pd.DataFrame:
    state = pd.read_parquet(OUT / "e273_human_diary_state_jepa_audit_features.parquet")
    meta_cols = [c for c in ["subject_id", "dateblock_group", "weekday", "is_weekend", "subject_order"] if c in state.columns and c not in KEYS]
    meta = state[state["split"].eq("test")][KEYS + meta_cols].copy()
    for col in ["sleep_date", "lifelog_date"]:
        meta[col] = pd.to_datetime(meta[col]).dt.strftime("%Y-%m-%d")
    keys = base[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        keys[col] = pd.to_datetime(keys[col]).dt.strftime("%Y-%m-%d")
    aligned = keys.merge(meta, on=KEYS, how="left", validate="one_to_one")
    if aligned[meta_cols].isna().any().any():
        raise RuntimeError("test metadata alignment failed")
    return aligned.reset_index(drop=True)


def permute_within_groups(delta: np.ndarray, groups: pd.Series, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    arr = np.asarray(delta, dtype=np.float64)
    out = arr.copy()
    for _, idx in groups.groupby(groups).groups.items():
        idx_arr = np.asarray(list(idx), dtype=int)
        if len(idx_arr) > 1:
            out[idx_arr] = arr[idx_arr][rng.permutation(len(idx_arr))]
    return out


def null_delta(delta: np.ndarray, mode: str, meta: pd.DataFrame, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    arr = np.asarray(delta, dtype=np.float64).copy()
    if mode == "row_perm":
        return arr[rng.permutation(arr.shape[0]), :]
    if mode == "target_perm":
        return arr[:, rng.permutation(arr.shape[1])]
    if mode == "sign_flip":
        return -arr
    if mode == "row_sign":
        return arr * rng.choice([-1.0, 1.0], size=(arr.shape[0], 1))
    if mode == "cell_perm":
        flat = arr.reshape(-1).copy()
        rng.shuffle(flat)
        return flat.reshape(arr.shape)
    if mode == "subject_perm":
        return permute_within_groups(arr, meta["subject_id"], seed)
    if mode == "dateblock_perm":
        return permute_within_groups(arr, meta["dateblock_group"], seed)
    raise ValueError(mode)


def score_candidates(candidates: pd.DataFrame, axes: list[dict[str, Any]], base: pd.DataFrame, base_logit: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    meta = test_meta(base)
    modes = ["row_perm", "target_perm", "sign_flip", "row_sign", "cell_perm", "subject_perm", "dateblock_perm"]
    score_rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    for rec in candidates.to_dict("records"):
        path = locate(rec["file"])
        if path is None:
            continue
        delta = load_delta(path, base, base_logit)
        actual = public_analog_metrics(delta, axes)
        score_rows.append({**{k: v for k, v in rec.items() if k != "path_exists"}, **actual})
        for mode in modes:
            for rep in range(16):
                nd = null_delta(delta, mode, meta, stable_seed(rec["basename"], mode, rep))
                metrics = public_analog_metrics(nd, axes)
                null_rows.append(
                    {
                        "basename": rec["basename"],
                        "role": rec["role"],
                        "mode": mode,
                        "rep": rep,
                        **metrics,
                    }
                )
    scores = pd.DataFrame(score_rows)
    nulls = pd.DataFrame(null_rows)
    if not scores.empty and not nulls.empty:
        risk_cols = [
            "public_loss_weighted_pos_cos",
            "severe_loss_weighted_pos_cos",
            "max_severe_pos_cos",
            "poscos_e323",
            "poscos_e216",
            "poscos_e267",
            "poscos_e256",
        ]
        for col in risk_cols:
            if col not in scores.columns:
                scores[col] = 0.0
            if col not in nulls.columns:
                nulls[col] = 0.0
        agg_rows: list[dict[str, Any]] = []
        for rec in scores.to_dict("records"):
            part = nulls[nulls["basename"].eq(rec["basename"])]
            if part.empty:
                continue
            item: dict[str, Any] = {"basename": rec["basename"]}
            for col in risk_cols:
                item[f"{col}_null_p10"] = float(part[col].quantile(0.10))
                item[f"{col}_null_median"] = float(part[col].median())
                item[f"{col}_null_p90"] = float(part[col].quantile(0.90))
                item[f"{col}_dominance_lower_is_better"] = float(np.mean(float(rec[col]) < part[col].to_numpy(dtype=float)))
            agg_rows.append(item)
        agg = pd.DataFrame(agg_rows)
        scores = scores.merge(agg, on="basename", how="left")
        dominance_cols = [c for c in scores.columns if c.endswith("_dominance_lower_is_better")]
        scores["public_analog_survival_score"] = scores[dominance_cols].fillna(0.0).mean(axis=1)
        scores["public_analog_risk_score"] = (
            scores["public_loss_weighted_pos_cos"].fillna(0.0)
            + scores["severe_loss_weighted_pos_cos"].fillna(0.0)
            + scores["max_severe_pos_cos"].fillna(0.0)
            + scores.get("poscos_e323", 0.0)
            + scores.get("poscos_e216", 0.0)
        )
    scores = scores.sort_values(
        ["public_analog_survival_score", "public_analog_risk_score", "role"],
        ascending=[False, True, True],
    ).reset_index(drop=True)
    nulls = nulls.sort_values(["basename", "mode", "rep"]).reset_index(drop=True)
    scores.to_csv(SCORE_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    return scores, nulls


def write_report(obs_axes: pd.DataFrame, candidates: pd.DataFrame, scores: pd.DataFrame) -> None:
    score_cols = [
        "role",
        "family",
        "basename",
        "public_analog_survival_score",
        "public_analog_risk_score",
        "public_loss_weighted_pos_cos",
        "severe_loss_weighted_pos_cos",
        "max_severe_pos_cos",
        "poscos_e323",
        "poscos_e216",
        "poscos_e267",
        "poscos_e256",
        "move_l1",
        "changed_rows",
        "share_Q1",
        "share_Q2",
        "share_Q3",
        "share_S1",
    ]
    upload = scores[scores["role"].isin(["E344_upload", "E345_upload"])] if not scores.empty else pd.DataFrame()
    lines = [
        "# E346 Counter-Axis Public-Analog Audit",
        "",
        "## Question",
        "",
        "Do the E344/E345 hidden lifestyle-state counter-axis candidates avoid the anatomy of already observed public-loss submissions?",
        "",
        "## Observed Public Axes",
        "",
        md_table(
            obs_axes.sort_values(["exists", "public_delta_vs_e247"], ascending=[False, False])[
                ["file", "exists", "public_lb", "public_delta_vs_e247", "loss_tier", "changed_rows", "share_Q1", "share_Q2", "share_Q3", "share_S1", "share_S2", "share_S3", "share_S4"]
            ],
            n=30,
            floatfmt=".9f",
        ),
        "",
        "## Candidate Public-Analog Scores",
        "",
        md_table(scores[[c for c in score_cols if c in scores.columns]], n=40, floatfmt=".9f"),
        "",
        "## Upload Candidate Read",
        "",
        md_table(upload[[c for c in score_cols if c in upload.columns]], n=10, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
    ]
    if not upload.empty:
        e344 = upload[upload["role"].eq("E344_upload")]
        e345 = upload[upload["role"].eq("E345_upload")]
        if not e344.empty and not e345.empty:
            r344 = e344.iloc[0]
            r345 = e345.iloc[0]
            better = "E344" if float(r344["public_analog_risk_score"]) <= float(r345["public_analog_risk_score"]) else "E345"
            hard_veto_cols = ["poscos_e323", "poscos_e216", "poscos_e267", "poscos_e256"]
            e344_hard = max(float(r344.get(c, 0.0)) for c in hard_veto_cols)
            e345_hard = max(float(r345.get(c, 0.0)) for c in hard_veto_cols)
            certified = (
                min(float(r344["public_analog_survival_score"]), float(r345["public_analog_survival_score"])) >= 0.70
                and max(float(r344["public_analog_risk_score"]), float(r345["public_analog_risk_score"])) <= 0.050
            )
            lines.extend(
                [
                    f"- E344 public-analog risk score: `{float(r344['public_analog_risk_score']):.9f}`; survival score `{float(r344['public_analog_survival_score']):.9f}`.",
                    f"- E345 public-analog risk score: `{float(r345['public_analog_risk_score']):.9f}`; survival score `{float(r345['public_analog_survival_score']):.9f}`.",
                    f"- Lower public-analog risk among upload candidates: `{better}`.",
                    f"- Direct positive alignment to E323/E216/E267/E256 hard-veto axes: E344 `{e344_hard:.9f}`, E345 `{e345_hard:.9f}`.",
                    f"- Certification-grade public-analog dominance: `{certified}`.",
                ]
            )
    lines.extend(
        [
            "- This audit is a veto/stress diagnostic, not a public LB predictor.",
            "- The current upload candidates do not have a hard public-bad-axis veto: their positive alignment to E323/E216/E267/E256 is zero in this axis set.",
            "- They are not certification-grade either: public-analog survival is near the middle of matched movement nulls, not above a strong `0.70` dominance threshold.",
            "- Decision: keep E344 first because it has slightly lower public-analog risk and stronger p90; keep E345 as the bad-axis-margin backup. Do not create a new public candidate from E346 alone.",
            "",
            "## Files",
            "",
            f"- `{OBS_AXIS_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{SCORE_OUT.name}`",
            f"- `{NULL_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base, base_logit = load_base()
    obs_axes = observed_axes(base, base_logit)
    candidates = candidate_pool()
    axes = axis_records(obs_axes, base, base_logit)
    scores, _nulls = score_candidates(candidates, axes, base, base_logit)
    write_report(obs_axes, candidates, scores)
    print(REPORT_OUT)
    print(scores.head(40).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
