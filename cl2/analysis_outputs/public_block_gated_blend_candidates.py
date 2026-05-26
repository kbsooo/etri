from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import geometry_mask_cv_experiments as geom


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
SORT_KEY = ["subject_id", "lifelog_date"]
EPS = 1e-5

ANCHOR = "submission_hybrid_0p578_logit_after_subject_final9_strict.csv"
ANCHOR_OOF = "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy"
STAGE2 = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
STAGE2_OOF = "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"


@dataclass(frozen=True)
class GateConfig:
    name: str
    target_set: str
    mode: str
    low: float
    high: float
    threshold: float = 0.0


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def read_submission(file_name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def target_sets() -> dict[str, list[str]]:
    return {
        "full": TARGETS,
        "drop_q3": ["Q1", "Q2", "S1", "S2", "S3", "S4"],
        "no_q2q3": ["Q1", "S1", "S2", "S3", "S4"],
        "s_only": ["S1", "S2", "S3", "S4"],
        "q1_s": ["Q1", "S1", "S2", "S3", "S4"],
        "s3s4": ["S3", "S4"],
    }


def hidden_block_features(ref: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    known = ref[["subject_id", "lifelog_date"]].copy()
    known["_kind"] = "known"
    hidden = rows[["subject_id", "lifelog_date"]].copy()
    hidden["_kind"] = "hidden"
    hidden["_row_pos"] = np.arange(len(rows))
    full = pd.concat([known, hidden], ignore_index=True, sort=False).sort_values(SORT_KEY).reset_index(drop=True)
    full["_block"] = full.groupby("subject_id")["_kind"].transform(lambda s: s.ne(s.shift()).cumsum())

    h = full[full["_kind"].eq("hidden")].copy()
    h["block_len"] = h.groupby(["subject_id", "_block"])["_row_pos"].transform("size").astype(float)
    h["pos_in_block"] = h.groupby(["subject_id", "_block"]).cumcount().astype(float)
    h["rev_pos_in_block"] = h["block_len"] - 1.0 - h["pos_in_block"]
    h["block_frac"] = np.divide(h["pos_in_block"], np.maximum(h["block_len"] - 1.0, 1.0))
    h["is_edge"] = ((h["pos_in_block"] == 0) | (h["rev_pos_in_block"] == 0)).astype(float)
    h["is_interior"] = 1.0 - h["is_edge"]
    h["is_singleton"] = (h["block_len"] == 1).astype(float)

    known_by_subject = {
        str(sid): pd.to_datetime(g["lifelog_date"]).sort_values().to_numpy(dtype="datetime64[D]")
        for sid, g in ref.groupby("subject_id", sort=False)
    }
    prev_gap = np.full(len(h), np.nan, dtype=float)
    next_gap = np.full(len(h), np.nan, dtype=float)
    for i, row in enumerate(h.itertuples(index=False)):
        sid = str(row.subject_id)
        vals = known_by_subject.get(sid)
        if vals is None or len(vals) == 0:
            continue
        day = np.datetime64(pd.Timestamp(row.lifelog_date).date(), "D")
        pos = int(np.searchsorted(vals, day))
        if pos > 0:
            prev_gap[i] = float((day - vals[pos - 1]).astype("timedelta64[D]").astype(int))
        if pos < len(vals):
            next_gap[i] = float((vals[pos] - day).astype("timedelta64[D]").astype(int))
    h["prev_gap"] = prev_gap
    h["next_gap"] = next_gap
    h["min_gap"] = np.nanmin(np.column_stack([prev_gap, next_gap]), axis=1)
    h["max_gap"] = np.nanmax(np.column_stack([prev_gap, next_gap]), axis=1)
    h["has_both_sides"] = (np.isfinite(prev_gap) & np.isfinite(next_gap)).astype(float)
    h["near_known_3d"] = (h["min_gap"] <= 3).astype(float)
    h["near_known_7d"] = (h["min_gap"] <= 7).astype(float)
    h["long_block"] = (h["block_len"] >= 4).astype(float)
    h["very_long_block"] = (h["block_len"] >= 7).astype(float)
    return h.sort_values("_row_pos").reset_index(drop=True)


def gate_values(features: pd.DataFrame, cfg: GateConfig) -> np.ndarray:
    if cfg.mode == "constant":
        return np.full(len(features), cfg.high, dtype=float)
    if cfg.mode == "edge_high":
        return np.where(features["is_edge"].to_numpy(dtype=float) > 0, cfg.high, cfg.low)
    if cfg.mode == "interior_high":
        return np.where(features["is_interior"].to_numpy(dtype=float) > 0, cfg.high, cfg.low)
    if cfg.mode == "short_high":
        return np.where(features["block_len"].to_numpy(dtype=float) <= cfg.threshold, cfg.high, cfg.low)
    if cfg.mode == "long_low":
        return np.where(features["block_len"].to_numpy(dtype=float) >= cfg.threshold, cfg.low, cfg.high)
    if cfg.mode == "near_known_high":
        return np.where(features["min_gap"].to_numpy(dtype=float) <= cfg.threshold, cfg.high, cfg.low)
    if cfg.mode == "both_sides_high":
        return np.where(features["has_both_sides"].to_numpy(dtype=float) > 0, cfg.high, cfg.low)
    if cfg.mode == "edge_near_high":
        cond = (features["is_edge"].to_numpy(dtype=float) > 0) & (features["min_gap"].to_numpy(dtype=float) <= cfg.threshold)
        return np.where(cond, cfg.high, cfg.low)
    raise ValueError(cfg.mode)


def configs() -> list[GateConfig]:
    modes = [
        ("constant", 0.0, 0.545, 0.0),
        ("constant", 0.0, 0.65, 0.0),
        ("edge_high", 0.35, 0.75, 0.0),
        ("edge_high", 0.50, 0.85, 0.0),
        ("interior_high", 0.45, 0.75, 0.0),
        ("short_high", 0.35, 0.75, 3.0),
        ("short_high", 0.45, 0.85, 5.0),
        ("long_low", 0.35, 0.75, 4.0),
        ("long_low", 0.45, 0.85, 7.0),
        ("near_known_high", 0.35, 0.75, 3.0),
        ("near_known_high", 0.45, 0.85, 7.0),
        ("both_sides_high", 0.35, 0.75, 0.0),
        ("edge_near_high", 0.35, 0.85, 7.0),
    ]
    out = []
    for target_set in target_sets():
        for mode, low, high, threshold in modes:
            name = f"{target_set}_{mode}_lo{int(low*1000):03d}_hi{int(high*1000):03d}"
            if threshold:
                name += f"_t{int(threshold)}"
            out.append(GateConfig(name, target_set, mode, low, high, threshold))
    return out


def apply_gate(anchor: np.ndarray, stage2: np.ndarray, gate: np.ndarray, targets: list[str]) -> np.ndarray:
    out = anchor.copy()
    for target in targets:
        j = TARGETS.index(target)
        out[:, j] = anchor[:, j] + gate * (stage2[:, j] - anchor[:, j])
    return clip(out)


def geometry_summary(train: pd.DataFrame, sub: pd.DataFrame, anchor_oof: np.ndarray, stage2_oof: np.ndarray, cfg: GateConfig) -> dict[str, float]:
    y_all = train[TARGETS].to_numpy(dtype=int)
    rows = []
    targets = target_sets()[cfg.target_set]
    for tr_idx, val_idx, fold in geom.geometry_folds(train, sub, n_repeats=10):
        ref = train.iloc[tr_idx].reset_index(drop=True)
        val = train.iloc[val_idx].reset_index(drop=True)
        feats = hidden_block_features(ref, val)
        gate = gate_values(feats, cfg)
        pred = apply_gate(anchor_oof[val_idx], stage2_oof[val_idx], gate, targets)
        y = y_all[val_idx]
        anchor_loss = mean_loss(y, anchor_oof[val_idx])
        stage2_loss = mean_loss(y, stage2_oof[val_idx])
        pred_loss = mean_loss(y, pred)
        row = {
            "fold": fold,
            "anchor_loss": anchor_loss,
            "stage2_loss": stage2_loss,
            "candidate_loss": pred_loss,
            "delta_vs_anchor": pred_loss - anchor_loss,
            "delta_vs_stage2": pred_loss - stage2_loss,
            "mean_gate": float(gate.mean()),
        }
        for j, target in enumerate(TARGETS):
            row[f"{target}_delta_vs_stage2"] = loss_col(y[:, j], pred[:, j]) - loss_col(y[:, j], stage2_oof[val_idx, j])
        rows.append(row)
    df = pd.DataFrame(rows)
    out = {
        "geometry_delta_vs_anchor": float(df["delta_vs_anchor"].mean()),
        "geometry_delta_vs_stage2": float(df["delta_vs_stage2"].mean()),
        "geometry_win_vs_stage2": float((df["delta_vs_stage2"] < 0).mean()),
        "geometry_mean_gate": float(df["mean_gate"].mean()),
    }
    for target in TARGETS:
        out[f"geometry_{target}_delta_vs_stage2"] = float(df[f"{target}_delta_vs_stage2"].mean())
    return out


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    y = train[TARGETS].to_numpy(dtype=int)

    anchor = read_submission(ANCHOR)
    stage2 = read_submission(STAGE2)
    anchor_sub = anchor[TARGETS].to_numpy(dtype=float)
    stage2_sub = stage2[TARGETS].to_numpy(dtype=float)
    anchor_oof = clip(np.load(OUT / ANCHOR_OOF))
    stage2_oof = clip(np.load(OUT / STAGE2_OOF))
    assert anchor[KEY].equals(sample[KEY])
    assert stage2[KEY].equals(sample[KEY])

    obs = pd.read_csv(OUT / "public_probe_observations.csv").set_index("file")["public_lb"].astype(float)
    anchor_public = float(obs[ANCHOR])
    stage2_public = float(obs[STAGE2])
    stage2_public_gain = stage2_public - anchor_public

    sub_feats = hidden_block_features(train, sub)
    rows = []
    saved = []
    for cfg in configs():
        targets = target_sets()[cfg.target_set]
        sub_gate = gate_values(sub_feats, cfg)
        sub_pred = apply_gate(anchor_sub, stage2_sub, sub_gate, targets)
        oof_gate = np.full(len(train), float(sub_gate.mean()), dtype=float)
        oof_pred_proxy = apply_gate(anchor_oof, stage2_oof, oof_gate, targets)
        row = {
            "file": f"submission_publicblockgate_anchor578_stage2_{cfg.name}.csv",
            "gate": cfg.name,
            "target_set": cfg.target_set,
            "targets_changed": ",".join(targets),
            "mode": cfg.mode,
            "low": cfg.low,
            "high": cfg.high,
            "threshold": cfg.threshold,
            "submission_mean_gate": float(sub_gate.mean()),
            "submission_min_gate": float(sub_gate.min()),
            "submission_max_gate": float(sub_gate.max()),
            "oof_proxy_mean_loss": mean_loss(y, oof_pred_proxy),
            "oof_proxy_delta_vs_anchor": mean_loss(y, oof_pred_proxy) - mean_loss(y, anchor_oof),
            "oof_proxy_delta_vs_stage2": mean_loss(y, oof_pred_proxy) - mean_loss(y, stage2_oof),
            "linear_public_est_from_mean_gate": anchor_public + float(sub_gate.mean()) * stage2_public_gain,
            "distance_abs_mean_vs_anchor": float(np.abs(sub_pred - anchor_sub).mean()),
            "distance_abs_mean_vs_stage2": float(np.abs(sub_pred - stage2_sub).mean()),
            "submission_min": float(sub_pred.min()),
            "submission_max": float(sub_pred.max()),
        }
        row.update(geometry_summary(train, sub, anchor_oof, stage2_oof, cfg))
        rows.append(row)

        if row["geometry_delta_vs_stage2"] <= 0.0 and row["oof_proxy_mean_loss"] <= 0.5735:
            out = anchor.copy()
            out[TARGETS] = sub_pred
            out.to_csv(OUT / row["file"], index=False)
            np.save(OUT / row["file"].replace("submission_", "final_").replace(".csv", "_oof_proxy.npy"), oof_pred_proxy)
            saved.append({"file": row["file"], "gate": cfg.name, "target_set": cfg.target_set})

    summary = pd.DataFrame(rows).sort_values(["geometry_delta_vs_stage2", "oof_proxy_mean_loss"]).reset_index(drop=True)
    summary.to_csv(OUT / "public_block_gated_blend_candidates.csv", index=False)
    pd.DataFrame(saved).to_csv(OUT / "public_block_gated_saved_candidates.csv", index=False)
    display = [
        "gate",
        "target_set",
        "submission_mean_gate",
        "oof_proxy_mean_loss",
        "geometry_delta_vs_stage2",
        "geometry_win_vs_stage2",
        "linear_public_est_from_mean_gate",
        "distance_abs_mean_vs_anchor",
        "file",
    ]
    print(summary[display].head(40).round(8).to_string(index=False))
    print("\n[saved]")
    print(pd.DataFrame(saved).head(30).to_string(index=False))


if __name__ == "__main__":
    main()
