from __future__ import annotations

import itertools
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis_outputs"
TARGETS = d.TARGETS
Q_TARGETS = ["Q2", "Q3"]
KEY = d.KEY


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def q_loss(y: np.ndarray, pred: np.ndarray, target: str) -> float:
    j = Q_TARGETS.index(target)
    return float(log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]))


def mean_q_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([q_loss(y, pred, target) for target in Q_TARGETS]))


def load_train_sub() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    return train.sort_values(KEY).reset_index(drop=True), sub.sort_values(KEY).reset_index(drop=True)


@dataclass(frozen=True)
class BridgeConfig:
    alpha: float
    global_weight: float
    stay_boost: float
    prior_shrink: float
    bridge_weight: float

    @property
    def name(self) -> str:
        return (
            f"a{self.alpha:g}_gw{self.global_weight:g}_"
            f"stay{self.stay_boost:g}_sh{self.prior_shrink:g}_bw{self.bridge_weight:g}"
        )


def configs() -> list[BridgeConfig]:
    return [
        BridgeConfig(alpha, global_weight, stay_boost, prior_shrink, bridge_weight)
        for alpha, global_weight, stay_boost, prior_shrink, bridge_weight in itertools.product(
            [0.2, 0.5, 1.0, 2.0],
            [0.0, 0.5, 1.5, 4.0],
            [1.0, 1.5, 2.5, 4.0],
            [4.0, 8.0, 16.0, 32.0],
            [0.1, 0.2, 0.35, 0.5, 0.7, 0.9, 1.0],
        )
    ]


def transition_counts(rows: pd.DataFrame, target: str, subject_id: str | None = None) -> np.ndarray:
    counts = np.zeros((2, 2), dtype=float)
    data = rows if subject_id is None else rows[rows["subject_id"] == subject_id]
    for _, g in data.sort_values("lifelog_date").groupby("subject_id", sort=False):
        vals = g[target].to_numpy(dtype=int)
        for a, b in zip(vals[:-1], vals[1:]):
            counts[int(a), int(b)] += 1.0
    return counts


def transition_matrix(rows: pd.DataFrame, target: str, sid: str, cfg: BridgeConfig) -> np.ndarray:
    global_counts = transition_counts(rows, target, None)
    subj_counts = transition_counts(rows, target, sid)
    counts = subj_counts + cfg.global_weight * global_counts + cfg.alpha
    p = counts / counts.sum(axis=1, keepdims=True)
    if cfg.stay_boost != 1.0:
        p = p.copy()
        p[0, 0] *= cfg.stay_boost
        p[1, 1] *= cfg.stay_boost
        p = p / p.sum(axis=1, keepdims=True)
    return p


def subject_prior(rows: pd.DataFrame, target: str, sid: str, cfg: BridgeConfig) -> float:
    global_rate = float(rows[target].mean())
    part = rows[rows["subject_id"] == sid]
    if part.empty:
        return global_rate
    return float((part[target].sum() + cfg.prior_shrink * global_rate) / (len(part) + cfg.prior_shrink))


def matrix_power(p: np.ndarray, n: int) -> np.ndarray:
    if n <= 0:
        return np.eye(2)
    return np.linalg.matrix_power(p, n)


def bridge_block_probs(
    ref: pd.DataFrame,
    block: pd.DataFrame,
    target: str,
    cfg: BridgeConfig,
) -> np.ndarray:
    sid = str(block["subject_id"].iloc[0])
    p = transition_matrix(ref, target, sid, cfg)
    prior_1 = subject_prior(ref, target, sid, cfg)
    prior = np.array([1.0 - prior_1, prior_1], dtype=float)
    before = ref[(ref["subject_id"] == sid) & (ref["lifelog_date"] < block["lifelog_date"].min())].sort_values("lifelog_date")
    after = ref[(ref["subject_id"] == sid) & (ref["lifelog_date"] > block["lifelog_date"].max())].sort_values("lifelog_date")
    prev_label = None if before.empty else int(before.iloc[-1][target])
    next_label = None if after.empty else int(after.iloc[0][target])
    n = len(block)
    out = np.zeros(n, dtype=float)
    for t in range(1, n + 1):
        if prev_label is not None and next_label is not None:
            fwd = matrix_power(p, t)[prev_label, :]
            bwd = matrix_power(p, n + 1 - t)[:, next_label]
            dist = fwd * bwd
            if dist.sum() <= 0:
                dist = prior
            else:
                dist = dist / dist.sum()
        elif prev_label is not None:
            dist = np.zeros(2, dtype=float)
            dist[prev_label] = 1.0
            dist = dist @ matrix_power(p, t)
        elif next_label is not None:
            bwd = matrix_power(p, n + 1 - t)[:, next_label]
            dist = prior * bwd
            dist = dist / dist.sum() if dist.sum() > 0 else prior
        else:
            dist = prior
        out[t - 1] = dist[1]
    return clip(out)


def contiguous_blocks(rows: pd.DataFrame) -> list[np.ndarray]:
    blocks = []
    for _, g in rows.sort_values(["subject_id", "lifelog_date"]).groupby("subject_id", sort=False):
        idx = g.index.to_numpy()
        # The folds are contiguous in subject order, but real dates can skip. Split only on index discontinuity.
        cuts = np.where(np.diff(idx) != 1)[0] + 1
        for part in np.split(idx, cuts):
            if len(part):
                blocks.append(part)
    return blocks


def bridge_predict(
    ref: pd.DataFrame,
    rows: pd.DataFrame,
    base_q: np.ndarray,
    target: str,
    cfg: BridgeConfig,
) -> np.ndarray:
    pred = base_q.copy()
    local_rows = rows.copy()
    local_rows["_local_pos"] = np.arange(len(local_rows))
    sorted_rows = local_rows.sort_values(["subject_id", "lifelog_date"])
    for _, subj_rows in sorted_rows.groupby("subject_id", sort=False):
        sid = str(subj_rows["subject_id"].iloc[0])
        subj_rows = subj_rows.sort_values("lifelog_date")
        pos = subj_rows["_local_pos"].to_numpy()
        dates = subj_rows["lifelog_date"].to_numpy()
        ref_dates = ref.loc[ref["subject_id"] == sid, "lifelog_date"].sort_values().to_numpy()
        cut_points = []
        for i in range(1, len(pos)):
            has_ref_between = bool(((ref_dates > dates[i - 1]) & (ref_dates < dates[i])).any())
            if pos[i] != pos[i - 1] + 1 or has_ref_between:
                cut_points.append(i)
        for local_pos in np.split(pos, cut_points):
            block = local_rows.iloc[local_pos].copy()
            bridge = bridge_block_probs(ref, block, target, cfg)
            pred[local_pos] = (1.0 - cfg.bridge_weight) * pred[local_pos] + cfg.bridge_weight * bridge
    return clip(pred)


def build_fold_cache(train: pd.DataFrame) -> list[tuple[np.ndarray, pd.DataFrame, pd.DataFrame, np.ndarray]]:
    cache = []
    for tr_idx, val_idx in d.make_folds(train, "subject_blocks"):
        ref = train.iloc[tr_idx].copy().reset_index(drop=True)
        rows = train.iloc[val_idx].copy().reset_index(drop=True)
        base_all = cal.temporal_base(ref, rows)
        base_q = base_all[:, [TARGETS.index(t) for t in Q_TARGETS]]
        cache.append((val_idx, ref, rows, base_q))
    return cache


def oof_for_config_from_cache(
    n_rows: int,
    cache: list[tuple[np.ndarray, pd.DataFrame, pd.DataFrame, np.ndarray]],
    cfg: BridgeConfig,
) -> np.ndarray:
    pred = np.zeros((n_rows, len(Q_TARGETS)), dtype=float)
    for val_idx, ref, rows, base_q in cache:
        for j, target in enumerate(Q_TARGETS):
            pred[val_idx, j] = bridge_predict(ref, rows, base_q[:, j], target, cfg)
    return clip(pred)


def evaluate_grid(train: pd.DataFrame, cfgs: list[BridgeConfig]) -> pd.DataFrame:
    y = train[Q_TARGETS].to_numpy(dtype=int)
    rows = []
    cache = build_fold_cache(train)
    base = np.zeros((len(train), len(Q_TARGETS)), dtype=float)
    for val_idx, _, _, base_q in cache:
        base[val_idx] = base_q
    rows.append({"config": "temporal_base", "mean_q23": mean_q_loss(y, base), "Q2": q_loss(y, base, "Q2"), "Q3": q_loss(y, base, "Q3")})
    for i, cfg in enumerate(cfgs):
        pred = oof_for_config_from_cache(len(train), cache, cfg)
        row = {"config": cfg.name, "mean_q23": mean_q_loss(y, pred)}
        for target in Q_TARGETS:
            row[target] = q_loss(y, pred, target)
        rows.append(row)
        if i % 100 == 0:
            print(f"[bridge grid] {i}/{len(cfgs)}", flush=True)
    return pd.DataFrame(rows).sort_values("mean_q23")


def choose_by_target(grid: pd.DataFrame) -> dict[str, str]:
    return {target: str(grid.sort_values(target).iloc[0]["config"]) for target in Q_TARGETS}


def parse_config(name: str, cfg_by_name: dict[str, BridgeConfig]) -> BridgeConfig | None:
    if name == "temporal_base":
        return None
    return cfg_by_name[name]


def nested_bridge(train: pd.DataFrame, shortlist: list[BridgeConfig]) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    y = train[Q_TARGETS].to_numpy(dtype=int)
    folds = d.make_folds(train, "subject_blocks")
    base_pred = np.zeros((len(train), len(Q_TARGETS)), dtype=float)
    nested_pred = np.zeros_like(base_pred)
    selected_rows = []
    cfg_by_name = {cfg.name: cfg for cfg in shortlist}

    for outer_id, (tr_idx, val_idx) in enumerate(folds):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        inner_grid = evaluate_grid(outer_train, shortlist)
        choices = choose_by_target(inner_grid)
        base_all = cal.temporal_base(outer_train, outer_val)
        base_q = base_all[:, [TARGETS.index(t) for t in Q_TARGETS]]
        base_pred[val_idx] = base_q
        pred_q = base_q.copy()
        for j, target in enumerate(Q_TARGETS):
            cfg = parse_config(choices[target], cfg_by_name)
            if cfg is not None:
                pred_q[:, j] = bridge_predict(outer_train, outer_val, base_q[:, j], target, cfg)
            selected_rows.append(
                {
                    "outer_fold": outer_id,
                    "target": target,
                    "config": choices[target],
                    "inner_loss": float(inner_grid.sort_values(target).iloc[0][target]),
                }
            )
        nested_pred[val_idx] = pred_q
        print(f"[bridge nested] outer {outer_id} choices={choices}", flush=True)

    rows = []
    for name, pred in [("temporal_base", base_pred), ("nested_bridge", nested_pred)]:
        row = {"model": name, "mean_q23": mean_q_loss(y, pred)}
        for target in Q_TARGETS:
            row[target] = q_loss(y, pred, target)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("mean_q23"), pd.DataFrame(selected_rows), nested_pred


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, choices: dict[str, str], cfg_by_name: dict[str, BridgeConfig]) -> pd.DataFrame:
    if (OUT / "submission_hybrid_overnight_context.csv").exists():
        out = pd.read_csv(OUT / "submission_hybrid_overnight_context.csv", parse_dates=["sleep_date", "lifelog_date"])
        out = out.sort_values(KEY).reset_index(drop=True)
    else:
        out = sub[["subject_id", "sleep_date", "lifelog_date"]].copy()
        for target in TARGETS:
            out[target] = 0.5
    base_all = cal.temporal_base(train, sub)
    base_q = base_all[:, [TARGETS.index(t) for t in Q_TARGETS]]
    for j, target in enumerate(Q_TARGETS):
        cfg = parse_config(choices[target], cfg_by_name)
        if cfg is None:
            pred = base_q[:, j]
        else:
            pred = bridge_predict(train, sub, base_q[:, j], target, cfg)
        out[target] = pred
    return out


def main() -> None:
    train, sub = load_train_sub()
    cfgs = configs()
    full_grid = evaluate_grid(train, cfgs)
    full_grid.to_csv(OUT / "q23_sequence_bridge_grid.csv", index=False)

    # Keep nested selection bounded to the configurations that showed at least some fold-safe signal.
    shortlist_names = set(full_grid.head(30)["config"])
    for target in Q_TARGETS:
        shortlist_names.update(full_grid.sort_values(target).head(30)["config"])
    shortlist = [cfg for cfg in cfgs if cfg.name in shortlist_names]
    nested, selected, _ = nested_bridge(train, shortlist)
    nested.to_csv(OUT / "q23_sequence_bridge_nested_results.csv", index=False)
    selected.to_csv(OUT / "q23_sequence_bridge_nested_selected.csv", index=False)

    choices = choose_by_target(full_grid)
    pd.DataFrame([{"target": target, "config": config} for target, config in choices.items()]).to_csv(
        OUT / "q23_sequence_bridge_full_choices.csv", index=False
    )
    cfg_by_name = {cfg.name: cfg for cfg in cfgs}
    submission = make_submission(train, sub, choices, cfg_by_name)
    submission.to_csv(OUT / "submission_q23_sequence_bridge.csv", index=False)

    old_q2 = 0.6927101523541841
    old_q3 = 0.6622200100969644
    old_mean = 0.6049114285714285
    nested_row = nested[nested["model"] == "nested_bridge"].iloc[0]
    est_mean = old_mean - ((old_q2 + old_q3) - (float(nested_row["Q2"]) + float(nested_row["Q3"]))) / 7.0
    pd.DataFrame(
        [
            {"target": "Q2", "old_loss": old_q2, "new_loss": float(nested_row["Q2"])},
            {"target": "Q3", "old_loss": old_q3, "new_loss": float(nested_row["Q3"])},
            {"target": "mean", "old_loss": old_mean, "new_loss": float(est_mean)},
        ]
    ).to_csv(OUT / "q23_sequence_bridge_hybrid_estimate.csv", index=False)

    print("\nFull bridge grid")
    print(full_grid.head(20).round(6).to_string(index=False))
    print("\nNested bridge")
    print(nested.round(6).to_string(index=False))
    print("\nFull choices")
    print(choices)
    print("\nHybrid context estimate if Q2/Q3 replaced")
    print(pd.read_csv(OUT / "q23_sequence_bridge_hybrid_estimate.csv").round(6).to_string(index=False))


if __name__ == "__main__":
    main()
