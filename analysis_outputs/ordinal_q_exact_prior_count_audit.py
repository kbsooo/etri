from __future__ import annotations

import argparse
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

import deep_dive_analysis as d
import ordinal_q_count_constraint_audit as oq


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = oq.TARGETS
KEY = oq.KEY
SUB_KEY = oq.SUB_KEY


def logaddexp(a: float, b: float) -> float:
    if a == -np.inf:
        return b
    if b == -np.inf:
        return a
    m = max(a, b)
    return float(m + math.log(math.exp(a - m) + math.exp(b - m)))


def log_comb(n: int, k: int) -> float:
    if k < 0 or k > n:
        return -np.inf
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


@lru_cache(maxsize=None)
def exact_total_pos_log_prior(n_total: int, rule: str) -> tuple[tuple[int, float], ...]:
    values = np.arange(1, 6, dtype=float)
    out: dict[int, float] = {}
    log_n_fact = math.lgamma(n_total + 1)
    for c1 in range(n_total + 1):
        for c2 in range(n_total - c1 + 1):
            for c3 in range(n_total - c1 - c2 + 1):
                for c4 in range(n_total - c1 - c2 - c3 + 1):
                    c5 = n_total - c1 - c2 - c3 - c4
                    counts = np.array([c1, c2, c3, c4, c5], dtype=float)
                    mu = float(np.dot(values, counts) / n_total)
                    if rule == "high":
                        total_pos = int(counts[values > mu].sum())
                    elif rule == "low":
                        total_pos = int(counts[values < mu].sum())
                    else:
                        raise ValueError(rule)
                    log_mult = log_n_fact - sum(math.lgamma(int(c) + 1) for c in counts)
                    out[total_pos] = logaddexp(out.get(total_pos, -np.inf), log_mult)
    norm = -np.inf
    for v in out.values():
        norm = logaddexp(norm, v)
    return tuple(sorted((k, v - norm) for k, v in out.items()))


def hidden_count_posterior(
    known_n: int,
    hidden_n: int,
    known_pos: int,
    rule: str,
    prior: str,
) -> tuple[np.ndarray, np.ndarray]:
    n_total = known_n + hidden_n
    ks: list[float] = []
    logw: list[float] = []
    if prior == "exact_value":
        total_prior = dict(exact_total_pos_log_prior(n_total, rule))
    elif prior == "uniform_total":
        total_prior = {k: 0.0 for k in oq.feasible_total_positive_counts(n_total, rule)}
    else:
        raise ValueError(prior)
    known_neg = known_n - known_pos
    for total_pos, prior_log in total_prior.items():
        hidden_pos = total_pos - known_pos
        if hidden_pos < 0 or hidden_pos > hidden_n:
            continue
        if known_neg < 0 or known_neg > n_total - total_pos:
            continue
        like = log_comb(total_pos, known_pos) + log_comb(n_total - total_pos, known_neg) - log_comb(n_total, known_n)
        ks.append(float(hidden_pos))
        logw.append(float(prior_log + like))
    if not ks:
        return np.array([], dtype=float), np.array([], dtype=float)
    k_arr = np.asarray(ks, dtype=float)
    lw = np.asarray(logw, dtype=float)
    lw -= np.max(lw)
    w = np.exp(lw)
    w /= w.sum()
    return k_arr, w


def target_count(current_sum: float, feasible: tuple[int, ...], known_n: int, hidden_n: int, known_pos: int, rule: str, prior: str, strategy: str) -> float | None:
    if strategy == "nearest":
        return oq.choose_target_sum(current_sum, feasible, "nearest")
    if strategy == "range":
        return oq.choose_target_sum(current_sum, feasible, "range")
    k, w = hidden_count_posterior(known_n, hidden_n, known_pos, rule, prior)
    if len(k) == 0:
        return None
    posterior_mean = float(np.sum(k * w))
    posterior_mode = float(k[int(np.argmax(w))])
    if strategy == "posterior_mean":
        return posterior_mean
    if strategy == "posterior_mode":
        return posterior_mode
    if strategy == "posterior_mean_nearest":
        return float(min(feasible, key=lambda x: abs(x - posterior_mean)))
    raise ValueError(strategy)


def adjust(train: pd.DataFrame, rows: pd.DataFrame, pred_in: np.ndarray, q_targets: list[str], prior: str, strategy: str, weight: float) -> tuple[np.ndarray, pd.DataFrame]:
    pred = pred_in.copy()
    details = []
    for sid, block in rows.groupby("subject_id", sort=False):
        known = train[train["subject_id"] == sid]
        local_idx = block.index.to_numpy(dtype=int)
        for target in q_targets:
            j = TARGETS.index(target)
            rule = "high" if target == "Q1" else "low"
            feasible = oq.feasible_hidden_counts(len(known), len(block), int(known[target].sum()), rule)
            current_sum = float(pred[local_idx, j].sum())
            tgt = target_count(current_sum, feasible, len(known), len(block), int(known[target].sum()), rule, prior, strategy)
            changed = tgt is not None and abs(tgt - current_sum) > 1e-12
            if changed:
                shifted = oq.shift_to_sum(pred[local_idx, j], tgt)
                pred[local_idx, j] = oq.clip((1.0 - weight) * pred[local_idx, j] + weight * shifted)
            details.append(
                {
                    "subject_id": sid,
                    "target": target,
                    "known_n": len(known),
                    "hidden_n": len(block),
                    "known_pos": int(known[target].sum()),
                    "feasible_min": min(feasible) if feasible else np.nan,
                    "feasible_max": max(feasible) if feasible else np.nan,
                    "base_sum": current_sum,
                    "target_sum": tgt if tgt is not None else current_sum,
                    "shift": (tgt - current_sum) if tgt is not None else 0.0,
                    "changed": changed,
                }
            )
    return oq.clip(pred), pd.DataFrame(details)


def adjust_oof(train: pd.DataFrame, base: np.ndarray, q_targets: list[str], prior: str, strategy: str, weight: float) -> tuple[np.ndarray, pd.DataFrame]:
    pred = base.copy()
    detail_frames = []
    for fold, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        ref = train.iloc[tr_idx].copy()
        val = train.iloc[val_idx].copy()
        fold_pred, detail = adjust(ref, val, pred, q_targets, prior, strategy, weight)
        pred[val_idx] = fold_pred[val_idx]
        detail["fold"] = fold
        detail_frames.append(detail)
    return oq.clip(pred), pd.concat(detail_frames, ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--base-sub", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--targets", default="Q2,Q3")
    args = parser.parse_args()

    q_targets = [x.strip() for x in args.targets.split(",") if x.strip()]
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sample = sub.sort_values(SUB_KEY).reset_index(drop=True)
    base = oq.clip(np.load(OUT / args.base_oof))
    base_sub = pd.read_csv(OUT / args.base_sub, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    y = train[TARGETS].to_numpy(dtype=int)
    base_loss = oq.mean_loss(y, base)

    rows = []
    best: tuple[dict[str, object], np.ndarray, pd.DataFrame] | None = None
    for prior in ["exact_value", "uniform_total"]:
        for strategy in ["range", "nearest", "posterior_mean", "posterior_mode", "posterior_mean_nearest"]:
            for weight in [0.10, 0.25, 0.50, 0.75, 1.00]:
                pred, detail = adjust_oof(train, base, q_targets, prior, strategy, weight)
                loss = oq.mean_loss(y, pred)
                row: dict[str, object] = {
                    "prior": prior,
                    "strategy": strategy,
                    "targets": ",".join(q_targets),
                    "weight": weight,
                    "base_loss": base_loss,
                    "candidate_loss": loss,
                    "delta": loss - base_loss,
                    "changed_blocks": int(detail["changed"].sum()),
                    "mean_abs_shift": float(detail["shift"].abs().mean()),
                }
                for target in TARGETS:
                    j = TARGETS.index(target)
                    row[f"{target}_delta"] = oq.loss_col(y[:, j], pred[:, j]) - oq.loss_col(y[:, j], base[:, j])
                rows.append(row)
                if best is None or float(row["candidate_loss"]) < float(best[0]["candidate_loss"]):
                    best = (row, pred, detail)
    summary = pd.DataFrame(rows).sort_values(["candidate_loss", "changed_blocks"]).reset_index(drop=True)
    summary.to_csv(OUT / f"{args.prefix}_exact_prior_summary.csv", index=False)
    assert best is not None
    best_row, best_pred, best_detail = best
    suffix = f"{best_row['prior']}_{best_row['strategy']}_w{best_row['weight']:g}"
    np.save(OUT / f"final_{args.prefix}_{suffix}_oof.npy", best_pred)
    best_detail.to_csv(OUT / f"{args.prefix}_{suffix}_oof_detail.csv", index=False)

    sub_pred, sub_detail = adjust(train, sub.reset_index(drop=True), base_sub[TARGETS].to_numpy(dtype=float), q_targets, str(best_row["prior"]), str(best_row["strategy"]), float(best_row["weight"]))
    out = base_sub.copy()
    out[TARGETS] = sub_pred
    out = out.sort_values(SUB_KEY).reset_index(drop=True)
    assert out[SUB_KEY].equals(sample[SUB_KEY])
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(SUB_KEY).sum() == 0
    sub_detail.to_csv(OUT / f"{args.prefix}_{suffix}_submission_detail.csv", index=False)
    out_file = OUT / f"submission_{args.prefix}_{suffix}.csv"
    out.to_csv(out_file, index=False)

    print(summary.head(40).round(9).to_string(index=False))
    print("best")
    print(pd.DataFrame([best_row]).round(9).to_string(index=False))
    print(f"saved {out_file.name}")


if __name__ == "__main__":
    main()
