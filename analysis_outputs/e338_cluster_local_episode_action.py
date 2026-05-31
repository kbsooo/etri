#!/usr/bin/env python3
"""E338: cluster-local episode action.

E337 found three residual lifestyle clusters that survive label/null stress:
Q3/dateblock, Q2/dateblock, and S3/subject.  Its materializer failed because
the cluster logistic correction moved every test row for each target.

This experiment keeps the same hidden lifestyle-state latent, but translates it
only through cluster-local residual episodes:

    hidden state -> selected cluster/target cells -> tiny E247 action

The test is whether row-local episode placement fixes the E337 action smear.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from scipy.special import expit
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import E247, E323, clip_prob, load_sub_frame, md_table, safe_id  # noqa: E402
from e330_target_residual_lifestyle_latent import base_label_matrix_all, groups_for, oof_proba  # noqa: E402
from e331_residual_state_localization import train_test_state  # noqa: E402
from e337_residual_lifestyle_cluster_state import (  # noqa: E402
    E216,
    bad_axes,
    cell_bad_veto,
    center_by_target,
    make_null_delta,
    short_hash,
    stable_seed,
    target_abs,
)
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

EPS = 1.0e-12
RNG_SEED = 20260531 + 338
CAP = 0.10
TOP_NULL_CANDIDATES = 12
NULL_REPS = 4

LATENT_MATRIX = OUT / "e337_residual_lifestyle_cluster_latent_matrix.parquet"
E337_STRESS = OUT / "e337_residual_lifestyle_cluster_label_stress.csv"

EPISODE_OUT = OUT / "e338_cluster_local_episode_table.csv"
CANDIDATE_OUT = OUT / "e338_cluster_local_episode_candidates.csv"
SCORE_OUT = OUT / "e338_cluster_local_episode_scores.csv"
ANATOMY_OUT = OUT / "e338_cluster_local_episode_anatomy.csv"
MOVE_NULL_OUT = OUT / "e338_cluster_local_episode_movement_nulls.csv"
REPORT_OUT = OUT / "e338_cluster_local_episode_report.md"


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def seed338(*parts: object) -> int:
    text = "|".join(map(str, parts))
    return RNG_SEED + int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100000


def load_current() -> pd.DataFrame:
    return load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)


def latent_train_test() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not LATENT_MATRIX.exists() or not E337_STRESS.exists():
        raise RuntimeError("Run e337_residual_lifestyle_cluster_state.py before E338")
    latent = pd.read_parquet(LATENT_MATRIX)
    train, test, _train_views, _test_views = train_test_state()
    train_lat = latent[latent["split"].eq("train")].reset_index(drop=True)
    test_lat = latent[latent["split"].eq("test")].reset_index(drop=True)
    if not train_lat[KEYS].equals(train[KEYS]) or not test_lat[KEYS].equals(test[KEYS]):
        raise RuntimeError("E337 latent matrix key mismatch")
    cols = [c for c in latent.columns if c.startswith("rs")]
    return train, test, train_lat[cols], test_lat[cols]


def cluster_labels(train_lat: pd.DataFrame, test_lat: pd.DataFrame, k: int) -> tuple[np.ndarray, np.ndarray]:
    pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
    z_train = pipe.fit_transform(train_lat)
    z_test = pipe.transform(test_lat)
    km = KMeans(n_clusters=k, random_state=seed338("kmeans", k), n_init=32)
    return km.fit_predict(z_train), km.predict(z_test)


def episode_table() -> pd.DataFrame:
    train, test, train_lat, test_lat = latent_train_test()
    stress = pd.read_csv(E337_STRESS)
    gates = stress[stress["gate"].astype(bool)].copy()
    if gates.empty:
        pd.DataFrame().to_csv(EPISODE_OUT, index=False)
        return pd.DataFrame()
    base_x_train, _base_x_test = base_label_matrix_all(train, test)
    rows: list[dict[str, Any]] = []
    label_cache: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    for _, gate in gates.iterrows():
        k = int(gate["k"])
        target = str(gate["target"])
        split_name = str(gate["split"])
        if k not in label_cache:
            label_cache[k] = cluster_labels(train_lat, test_lat, k)
        tr_lab, te_lab = label_cache[k]
        y = train[target].astype(int).to_numpy()
        groups = groups_for(train, split_name).reset_index(drop=True)
        base_oof = oof_proba(base_x_train, y, groups)
        resid = y.astype(float) - base_oof
        base_prob_level = float(np.mean(base_oof))
        denom = max(base_prob_level * (1.0 - base_prob_level), 0.10)
        for cl in sorted(np.unique(tr_lab)):
            tr_mask = tr_lab == cl
            te_mask = te_lab == cl
            if int(tr_mask.sum()) < 10 or int(te_mask.sum()) < 2:
                continue
            vals = resid[tr_mask]
            mean_resid = float(np.mean(vals))
            med_resid = float(np.median(vals))
            sign_agree = float(np.mean(np.sign(vals) == np.sign(mean_resid))) if abs(mean_resid) > EPS else 0.0
            strength = abs(mean_resid) * np.sqrt(min(int(tr_mask.sum()), 80)) * np.sqrt(min(int(te_mask.sum()), 25))
            delta_logit = float(np.clip(mean_resid / denom, -0.35, 0.35))
            rows.append(
                {
                    "k": k,
                    "cluster": int(cl),
                    "target": target,
                    "split": split_name,
                    "parent_actual_delta": float(gate["actual_delta"]),
                    "parent_dominance": float(gate["dominance"]),
                    "train_rows": int(tr_mask.sum()),
                    "test_rows": int(te_mask.sum()),
                    "mean_resid": mean_resid,
                    "median_resid": med_resid,
                    "sign_agree": sign_agree,
                    "strength": strength,
                    "delta_logit": delta_logit,
                    "episode_gate": bool(strength >= 0.45 and abs(delta_logit) >= 0.08 and sign_agree >= 0.45),
                }
            )
    out = pd.DataFrame(rows)
    if len(out):
        out = out.sort_values(["episode_gate", "strength", "parent_actual_delta"], ascending=[False, False, True]).reset_index(drop=True)
    out.to_csv(EPISODE_OUT, index=False)
    return out


def write_candidate(base: pd.DataFrame, base_logit: np.ndarray, delta: np.ndarray, candidate_id: str) -> Path:
    out = base.copy()
    out[TARGETS] = expit(np.clip(base_logit + np.clip(delta, -CAP, CAP), -40.0, 40.0))
    path = OUT / f"submission_e338_{safe_id(candidate_id, 110)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def build_delta_from_episodes(episodes: pd.DataFrame) -> np.ndarray:
    train, test, train_lat, test_lat = latent_train_test()
    delta = np.zeros((len(test), len(TARGETS)), dtype=np.float64)
    labels_by_k: dict[int, np.ndarray] = {}
    for _, rec in episodes.iterrows():
        k = int(rec["k"])
        if k not in labels_by_k:
            _tr, te = cluster_labels(train_lat, test_lat, k)
            labels_by_k[k] = te
        te_lab = labels_by_k[k]
        rows = te_lab == int(rec["cluster"])
        j = TARGETS.index(str(rec["target"]))
        delta[rows, j] += float(rec["delta_logit"])
    return delta


def materialize(episodes: pd.DataFrame, base: pd.DataFrame) -> tuple[pd.DataFrame, list[Path], np.ndarray, np.ndarray, np.ndarray]:
    base_logit, e323_bad, e216_bad = bad_axes(base)
    if episodes.empty:
        pd.DataFrame().to_csv(CANDIDATE_OUT, index=False)
        return pd.DataFrame(), [], base_logit, e323_bad, e216_bad
    gated = episodes[episodes["episode_gate"].astype(bool)].copy()
    if gated.empty:
        gated = episodes.head(8).copy()
    else:
        gated = gated.head(10)
    paths: list[Path] = []
    rows: list[dict[str, Any]] = []
    configs: list[tuple[str, pd.DataFrame]] = [
        ("top1", gated.head(1)),
        ("top2", gated.head(2)),
        ("top4", gated.head(4)),
        ("topall", gated),
    ]
    families = ["local_raw", "local_veto", "local_centered", "local_veto_centered"]
    scales = [0.20, 0.35, 0.55, 0.80, 1.00]
    for cfg_name, part in configs:
        if part.empty:
            continue
        raw = build_delta_from_episodes(part)
        variants = {
            "local_raw": raw,
            "local_veto": cell_bad_veto(raw, e323_bad, e216_bad),
            "local_centered": center_by_target(raw),
            "local_veto_centered": center_by_target(cell_bad_veto(raw, e323_bad, e216_bad)),
        }
        source_desc = ";".join([f"k{r.k}c{r.cluster}:{r.target}:{r.delta_logit:.3f}" for r in part.itertuples()])
        for family, direction in variants.items():
            for scale in scales:
                delta = direction * float(scale)
                if float(np.sum(np.abs(delta))) <= EPS:
                    continue
                candidate_id = f"{family}_{cfg_name}_s{scale:.2f}"
                path = write_candidate(base, base_logit, delta, candidate_id)
                paths.append(path)
                rows.append(
                    {
                        "candidate_id": candidate_id,
                        "file": rel(path),
                        "basename": path.name,
                        "family": family,
                        "config": cfg_name,
                        "scale": float(scale),
                        "sources": source_desc,
                        "source_count": int(len(part)),
                        "changed_rows": int(np.any(np.abs(delta) > EPS, axis=1).sum()),
                        "changed_cells": int((np.abs(delta) > EPS).sum()),
                        "mean_abs_logit_delta": float(np.mean(np.abs(delta))),
                        "max_abs_logit_delta": float(np.max(np.abs(delta))),
                        "l1_logit_delta": float(np.sum(np.abs(delta))),
                        "cos_with_e323_bad": float(np.sum(delta * e323_bad) / (np.linalg.norm(delta) * np.linalg.norm(e323_bad) + EPS)),
                        "cos_with_e216_bad": float(np.sum(delta * e216_bad) / (np.linalg.norm(delta) * np.linalg.norm(e216_bad) + EPS)),
                        **target_abs(delta),
                    }
                )
    cand = pd.DataFrame(rows).sort_values(["family", "config", "scale"]).reset_index(drop=True)
    cand.to_csv(CANDIDATE_OUT, index=False)
    return cand, paths, base_logit, e323_bad, e216_bad


def score_paths(paths: list[Path]) -> pd.DataFrame:
    if not paths:
        pd.DataFrame().to_csv(SCORE_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(OUT / CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    features = build_features([CURRENT] + [rel(p) for p in paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def anatomy(paths: list[Path], base: pd.DataFrame, base_logit: np.ndarray, e323_bad: np.ndarray, e216_bad: np.ndarray) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in paths:
        cand = load_sub_frame(path, base[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        rows.append(
            {
                "basename": path.name,
                "changed_rows": int(np.any(np.abs(delta) > EPS, axis=1).sum()),
                "changed_cells": int((np.abs(delta) > EPS).sum()),
                "l1_logit_delta": float(np.sum(np.abs(delta))),
                "mean_abs_logit_delta": float(np.mean(np.abs(delta))),
                "max_abs_logit_delta": float(np.max(np.abs(delta))),
                "cos_with_e323_bad": float(np.sum(delta * e323_bad) / (np.linalg.norm(delta) * np.linalg.norm(e323_bad) + EPS)),
                "cos_with_e216_bad": float(np.sum(delta * e216_bad) / (np.linalg.norm(delta) * np.linalg.norm(e216_bad) + EPS)),
                **target_abs(delta),
            }
        )
    out = pd.DataFrame(rows).sort_values(["cos_with_e323_bad", "cos_with_e216_bad", "l1_logit_delta"]).reset_index(drop=True)
    out.to_csv(ANATOMY_OUT, index=False)
    return out


def movement_null_stress(scores: pd.DataFrame, candidates: pd.DataFrame, base: pd.DataFrame, base_logit: np.ndarray) -> pd.DataFrame:
    if scores.empty or candidates.empty:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    non_current = scores[~scores["basename"].eq(CURRENT)].copy()
    joined = non_current.merge(candidates, on="basename", how="left", suffixes=("_score", "_meta"))
    chosen = joined.sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).head(TOP_NULL_CANDIDATES)
    null_paths: list[Path] = []
    null_rows: list[dict[str, Any]] = []
    for rec in chosen.to_dict("records"):
        path = ROOT / str(rec.get("file_meta", rec.get("file", "")))
        cand = load_sub_frame(path, base[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        for mode in ["row_perm", "target_perm", "sign_flip", "row_sign", "cell_perm"]:
            for rep in range(NULL_REPS):
                nd = make_null_delta(delta, mode, stable_seed("e338", rec["basename"], mode, rep))
                npth = write_candidate(base, base_logit, nd, f"null_{Path(rec['basename']).stem}_{mode}_{rep}")
                null_paths.append(npth)
                null_rows.append({"basename": rec["basename"], "null_basename": npth.name, "mode": mode, "rep": rep})
    if not null_paths:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(OUT / CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    null_features = build_features([CURRENT] + [rel(p) for p in null_paths], sample, refs, ref_vecs)
    null_scores = score_candidates(known, null_features, model_df)
    cols = ["basename", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "strict_promote_gate"]
    null_map = pd.DataFrame(null_rows).merge(null_scores[cols].rename(columns={"basename": "null_basename"}), on="null_basename", how="left")
    actual = non_current[cols].rename(
        columns={
            "pred_delta_vs_current_mean": "actual_mean",
            "pred_delta_vs_current_p90": "actual_p90",
            "pred_beats_current_rate": "actual_beats_rate",
            "strict_promote_gate": "actual_strict_promote",
        }
    )
    rows: list[dict[str, Any]] = []
    for basename, part in null_map.groupby("basename"):
        act = actual[actual["basename"].eq(basename)]
        if act.empty:
            continue
        a = act.iloc[0]
        rows.append(
            {
                "basename": basename,
                "null_count": int(len(part)),
                "actual_mean": float(a["actual_mean"]),
                "actual_p90": float(a["actual_p90"]),
                "actual_beats_rate": float(a["actual_beats_rate"]),
                "actual_strict_promote": bool(a["actual_strict_promote"]),
                "null_mean_best": float(part["pred_delta_vs_current_mean"].min()),
                "null_mean_median": float(part["pred_delta_vs_current_mean"].median()),
                "null_p90_best": float(part["pred_delta_vs_current_p90"].min()),
                "null_p90_median": float(part["pred_delta_vs_current_p90"].median()),
                "actual_mean_dominance": float(np.mean(float(a["actual_mean"]) < part["pred_delta_vs_current_mean"].to_numpy(dtype=float))),
                "actual_p90_dominance": float(np.mean(float(a["actual_p90"]) < part["pred_delta_vs_current_p90"].to_numpy(dtype=float))),
                "null_strict_promote_rate": float(part["strict_promote_gate"].astype(bool).mean()),
            }
        )
    out = pd.DataFrame(rows).sort_values(["actual_strict_promote", "actual_p90_dominance", "actual_p90"], ascending=[False, False, True])
    out.to_csv(MOVE_NULL_OUT, index=False)
    return out


def write_report(episodes: pd.DataFrame, candidates: pd.DataFrame, scores: pd.DataFrame, anat: pd.DataFrame, nulls: pd.DataFrame) -> None:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy() if len(scores) else pd.DataFrame()
    promoted = non_current[non_current["strict_promote_gate"].astype(bool)] if len(non_current) else pd.DataFrame()
    info = non_current[non_current["info_sensor_gate"].astype(bool)] if len(non_current) else pd.DataFrame()
    null_safe = pd.DataFrame()
    if len(nulls):
        null_safe = nulls[
            (nulls["actual_strict_promote"].astype(bool))
            & (nulls["actual_p90_dominance"] >= 0.70)
            & (nulls["null_strict_promote_rate"] <= 0.05)
        ]
    lines = [
        "# E338 Cluster-Local Episode Action",
        "",
        "## Question",
        "",
        "Does E337's hidden residual lifestyle cluster become useful when translated only through cluster-local episode rows rather than all test rows?",
        "",
        "## Episode Table",
        "",
        f"- episode-gated rows: `{int(episodes['episode_gate'].sum()) if len(episodes) else 0}`",
        "",
        md_table(episodes, n=30),
        "",
        "## Generated Candidates",
        "",
        f"- generated candidates: `{len(candidates)}`",
        f"- selector-promoted candidates: `{len(promoted)}`",
        f"- information-sensor candidates: `{len(info)}`",
        f"- movement-null-safe promoted candidates: `{len(null_safe)}`",
        "",
        md_table(candidates, n=30),
        "",
        "## Public-Free Selector Scores",
        "",
        md_table(
            non_current.sort_values(["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"], ascending=[False, False, True, True])
            if len(non_current)
            else non_current,
            n=35,
        ),
        "",
        "## Anatomy",
        "",
        md_table(anat, n=35),
        "",
        "## Movement-Null Stress",
        "",
        md_table(nulls, n=20),
        "",
        "## Decision",
        "",
    ]
    if len(null_safe):
        lines.append("At least one local episode action clears selector and movement-null gates. Treat it as a candidate after manual public-risk review.")
    elif len(promoted):
        lines.append("Local episode action reaches selector promotion but fails movement-null certification. Do not submit yet.")
    elif len(info):
        lines.append("Local episode action is visible only as an information sensor. It is not submission-grade, but it improves over E337's global action smear.")
    else:
        lines.append("Cluster-localization does not solve the action layer. The E337 hidden state is label-useful, but current residual-to-logit translation still fails selector visibility.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{EPISODE_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{SCORE_OUT.name}`",
            f"- `{ANATOMY_OUT.name}`",
            f"- `{MOVE_NULL_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    episodes = episode_table()
    base = load_current()
    candidates, paths, base_logit, e323_bad, e216_bad = materialize(episodes, base)
    scores = score_paths(paths)
    anat = anatomy(paths, base, base_logit, e323_bad, e216_bad)
    nulls = movement_null_stress(scores, candidates, base, base_logit)
    write_report(episodes, candidates, scores, anat, nulls)
    print(REPORT_OUT)
    if len(scores):
        non_current = scores[~scores["basename"].eq(CURRENT)].copy()
        cols = ["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p10", "pred_delta_vs_current_p90", "pred_beats_current_rate"]
        print(non_current[cols].head(30).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
