from __future__ import annotations

import argparse
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

import deep_dive_analysis as d


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
Q_TARGETS = ["Q1", "Q2", "Q3"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-5


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


@lru_cache(maxsize=None)
def feasible_total_positive_counts(n_total: int, rule: str) -> tuple[int, ...]:
    values = np.arange(1, 6, dtype=float)
    possible: set[int] = set()
    for c1 in range(n_total + 1):
        for c2 in range(n_total - c1 + 1):
            for c3 in range(n_total - c1 - c2 + 1):
                for c4 in range(n_total - c1 - c2 - c3 + 1):
                    c5 = n_total - c1 - c2 - c3 - c4
                    counts = np.array([c1, c2, c3, c4, c5], dtype=float)
                    mu = float(np.dot(values, counts) / n_total)
                    if rule == "high":
                        pos = int(counts[values > mu].sum())
                    elif rule == "low":
                        pos = int(counts[values < mu].sum())
                    else:
                        raise ValueError(rule)
                    possible.add(pos)
    return tuple(sorted(possible))


def feasible_hidden_counts(known_n: int, hidden_n: int, known_pos: int, rule: str) -> tuple[int, ...]:
    out = []
    for total_pos in feasible_total_positive_counts(known_n + hidden_n, rule):
        hidden_pos = total_pos - known_pos
        if 0 <= hidden_pos <= hidden_n and known_pos <= total_pos and known_n - known_pos <= known_n + hidden_n - total_pos:
            out.append(int(hidden_pos))
    return tuple(sorted(set(out)))


def shift_to_sum(p: np.ndarray, target_sum: float) -> np.ndarray:
    if len(p) == 0:
        return p
    target = float(np.clip(target_sum, EPS * len(p), (1.0 - EPS) * len(p)))
    z = logit(p)
    lo, hi = -40.0, 40.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if sigmoid(z + mid).sum() < target:
            lo = mid
        else:
            hi = mid
    return clip(sigmoid(z + (lo + hi) / 2.0))


def choose_target_sum(current_sum: float, feasible: tuple[int, ...], strategy: str) -> float | None:
    if not feasible:
        return None
    lo, hi = min(feasible), max(feasible)
    if strategy == "range":
        if current_sum < lo:
            return float(lo)
        if current_sum > hi:
            return float(hi)
        return None
    if strategy == "nearest":
        return float(min(feasible, key=lambda x: abs(x - current_sum)))
    raise ValueError(strategy)


def adjust_q_counts_oof(train: pd.DataFrame, base: np.ndarray, strategy: str, weight: float) -> tuple[np.ndarray, pd.DataFrame]:
    pred = base.copy()
    rows = []
    folds = d.make_folds(train, "subject_blocks")
    for fold, (tr_idx, val_idx) in enumerate(folds):
        ref = train.iloc[tr_idx].copy()
        val = train.iloc[val_idx].copy()
        for sid, block in val.groupby("subject_id", sort=False):
            known = ref[ref["subject_id"] == sid]
            local_idx = block.index.to_numpy(dtype=int)
            for target in Q_TARGETS:
                j = TARGETS.index(target)
                rule = "high" if target == "Q1" else "low"
                feasible = feasible_hidden_counts(len(known), len(block), int(known[target].sum()), rule)
                current_sum = float(pred[local_idx, j].sum())
                target_sum = choose_target_sum(current_sum, feasible, strategy)
                changed = target_sum is not None
                if changed:
                    shifted = shift_to_sum(pred[local_idx, j], target_sum)
                    pred[local_idx, j] = clip((1.0 - weight) * pred[local_idx, j] + weight * shifted)
                rows.append(
                    {
                        "fold": fold,
                        "subject_id": sid,
                        "target": target,
                        "known_n": len(known),
                        "hidden_n": len(block),
                        "known_pos": int(known[target].sum()),
                        "feasible_min": min(feasible) if feasible else np.nan,
                        "feasible_max": max(feasible) if feasible else np.nan,
                        "feasible_values": ",".join(map(str, feasible)),
                        "base_sum": current_sum,
                        "target_sum": target_sum if target_sum is not None else current_sum,
                        "changed": changed,
                    }
                )
    return clip(pred), pd.DataFrame(rows)


def adjust_q_counts_submission(train: pd.DataFrame, sub: pd.DataFrame, base_sub: pd.DataFrame, strategy: str, weight: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = base_sub.copy()
    pred = out[TARGETS].to_numpy(dtype=float).copy()
    rows = []
    for sid, block in sub.groupby("subject_id", sort=False):
        known = train[train["subject_id"] == sid]
        local_idx = block.index.to_numpy(dtype=int)
        for target in Q_TARGETS:
            j = TARGETS.index(target)
            rule = "high" if target == "Q1" else "low"
            feasible = feasible_hidden_counts(len(known), len(block), int(known[target].sum()), rule)
            current_sum = float(pred[local_idx, j].sum())
            target_sum = choose_target_sum(current_sum, feasible, strategy)
            changed = target_sum is not None
            if changed:
                shifted = shift_to_sum(pred[local_idx, j], target_sum)
                pred[local_idx, j] = clip((1.0 - weight) * pred[local_idx, j] + weight * shifted)
            rows.append(
                {
                    "subject_id": sid,
                    "target": target,
                    "known_n": len(known),
                    "hidden_n": len(block),
                    "known_pos": int(known[target].sum()),
                    "feasible_min": min(feasible) if feasible else np.nan,
                    "feasible_max": max(feasible) if feasible else np.nan,
                    "feasible_values": ",".join(map(str, feasible)),
                    "base_sum": current_sum,
                    "target_sum": target_sum if target_sum is not None else current_sum,
                    "changed": changed,
                }
            )
    out[TARGETS] = clip(pred)
    return out, pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--base-sub", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--targets", default="Q1,Q2,Q3")
    args = parser.parse_args()
    global Q_TARGETS
    Q_TARGETS = [x.strip() for x in args.targets.split(",") if x.strip()]

    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sample = sub.sort_values(SUB_KEY).reset_index(drop=True)
    base = clip(np.load(OUT / args.base_oof))
    base_sub = pd.read_csv(OUT / args.base_sub, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert base_sub[SUB_KEY].sort_index(axis=1).equals(sample[SUB_KEY].sort_index(axis=1)) or base_sub[SUB_KEY].equals(sub[SUB_KEY])
    y = train[TARGETS].to_numpy(dtype=int)
    base_loss = mean_loss(y, base)

    summary_rows = []
    best = None
    for strategy in ["range", "nearest"]:
        for weight in [0.25, 0.50, 0.75, 1.00]:
            pred, detail = adjust_q_counts_oof(train, base, strategy, weight)
            row = {
                "strategy": strategy,
                "weight": weight,
                "base_loss": base_loss,
                "candidate_loss": mean_loss(y, pred),
                "delta": mean_loss(y, pred) - base_loss,
                "changed_blocks": int(detail["changed"].sum()),
            }
            for target in TARGETS:
                j = TARGETS.index(target)
                row[f"{target}_delta"] = loss_col(y[:, j], pred[:, j]) - loss_col(y[:, j], base[:, j])
            summary_rows.append(row)
            if best is None or row["candidate_loss"] < best[0]["candidate_loss"]:
                best = (row, pred, detail)
    summary = pd.DataFrame(summary_rows).sort_values(["candidate_loss", "changed_blocks"]).reset_index(drop=True)
    summary.to_csv(OUT / f"{args.prefix}_summary.csv", index=False)
    assert best is not None
    best_row, best_pred, best_detail = best
    best_detail.to_csv(OUT / f"{args.prefix}_best_oof_detail.csv", index=False)
    np.save(OUT / f"final_{args.prefix}_{best_row['strategy']}_w{best_row['weight']:g}_oof.npy", best_pred)

    out, sub_detail = adjust_q_counts_submission(train, sub, base_sub, str(best_row["strategy"]), float(best_row["weight"]))
    out = out.sort_values(SUB_KEY).reset_index(drop=True)
    sample = sample.sort_values(SUB_KEY).reset_index(drop=True)
    assert out[SUB_KEY].equals(sample[SUB_KEY])
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(SUB_KEY).sum() == 0
    sub_detail.to_csv(OUT / f"{args.prefix}_submission_detail.csv", index=False)
    out_file = OUT / f"submission_{args.prefix}_{best_row['strategy']}_w{best_row['weight']:g}.csv"
    out.to_csv(out_file, index=False)

    constraints = []
    for sid, block in sub.groupby("subject_id", sort=False):
        known = train[train["subject_id"] == sid]
        for target in Q_TARGETS:
            rule = "high" if target == "Q1" else "low"
            feasible = feasible_hidden_counts(len(known), len(block), int(known[target].sum()), rule)
            constraints.append(
                {
                    "subject_id": sid,
                    "target": target,
                    "known_n": len(known),
                    "hidden_n": len(block),
                    "known_pos": int(known[target].sum()),
                    "feasible_min": min(feasible) if feasible else np.nan,
                    "feasible_max": max(feasible) if feasible else np.nan,
                    "feasible_values": ",".join(map(str, feasible)),
                }
            )
    pd.DataFrame(constraints).to_csv(OUT / f"{args.prefix}_submission_feasible_counts.csv", index=False)

    print(summary.round(9).to_string(index=False))
    print("best")
    print(pd.DataFrame([best_row]).round(9).to_string(index=False))
    print(f"saved {out_file.name}")


if __name__ == "__main__":
    main()
