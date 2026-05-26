from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd

import deep_dive_analysis as d
import ordinal_q_count_constraint_audit as oq


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = oq.TARGETS
Q_TARGETS = ["Q2", "Q3"]
KEY = oq.KEY
SUB_KEY = oq.SUB_KEY


def log_comb(n: int, k: int) -> float:
    if k < 0 or k > n:
        return -np.inf
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def hidden_count_posterior(known_n: int, hidden_n: int, known_pos: int, rule: str, prior: str) -> tuple[np.ndarray, np.ndarray]:
    n_total = known_n + hidden_n
    ks = []
    logw = []
    feasible_totals = oq.feasible_total_positive_counts(n_total, rule)
    for total_pos in feasible_totals:
        hidden_pos = total_pos - known_pos
        if hidden_pos < 0 or hidden_pos > hidden_n:
            continue
        known_neg = known_n - known_pos
        if known_neg < 0 or known_neg > n_total - total_pos:
            continue
        if prior == "uniform_total":
            prior_log = 0.0
        elif prior == "global_center":
            # Weakly prefer total positive rates near 0.5 while keeping all feasible counts possible.
            rate = total_pos / max(n_total, 1)
            prior_log = -4.0 * (rate - 0.5) ** 2
        else:
            raise ValueError(prior)
        # Treat the observed train part as a sample from the full subject period.
        like = log_comb(total_pos, known_pos) + log_comb(n_total - total_pos, known_neg) - log_comb(n_total, known_n)
        ks.append(float(hidden_pos))
        logw.append(prior_log + like)
    if not ks:
        return np.array([], dtype=float), np.array([], dtype=float)
    k_arr = np.array(ks, dtype=float)
    lw = np.array(logw, dtype=float)
    lw -= np.nanmax(lw)
    w = np.exp(lw)
    w /= w.sum()
    return k_arr, w


def posterior_target_sum(current_sum: float, feasible: tuple[int, ...], known_n: int, hidden_n: int, known_pos: int, rule: str, strategy: str, prior: str) -> float | None:
    if strategy.startswith("nearest"):
        return oq.choose_target_sum(current_sum, feasible, "nearest")
    if strategy == "range":
        return oq.choose_target_sum(current_sum, feasible, "range")
    k, w = hidden_count_posterior(known_n, hidden_n, known_pos, rule, prior)
    if len(k) == 0:
        return None
    if strategy == "posterior_mean":
        return float(np.sum(k * w))
    if strategy == "posterior_mode":
        return float(k[int(np.argmax(w))])
    if strategy == "posterior_mean_nearest":
        mean = float(np.sum(k * w))
        return float(min(feasible, key=lambda x: abs(x - mean)))
    raise ValueError(strategy)


def adjust(train: pd.DataFrame, rows: pd.DataFrame, pred_in: np.ndarray, strategy: str, weight: float, prior: str) -> tuple[np.ndarray, pd.DataFrame]:
    pred = pred_in.copy()
    detail = []
    for sid, block in rows.groupby("subject_id", sort=False):
        known = train[train["subject_id"] == sid]
        local_idx = block.index.to_numpy(dtype=int)
        for target in Q_TARGETS:
            j = TARGETS.index(target)
            rule = "low"
            feasible = oq.feasible_hidden_counts(len(known), len(block), int(known[target].sum()), rule)
            current_sum = float(pred[local_idx, j].sum())
            target_sum = posterior_target_sum(
                current_sum=current_sum,
                feasible=feasible,
                known_n=len(known),
                hidden_n=len(block),
                known_pos=int(known[target].sum()),
                rule=rule,
                strategy=strategy,
                prior=prior,
            )
            changed = target_sum is not None and abs(target_sum - current_sum) > 1e-12
            if changed:
                shifted = oq.shift_to_sum(pred[local_idx, j], target_sum)
                pred[local_idx, j] = oq.clip((1.0 - weight) * pred[local_idx, j] + weight * shifted)
            detail.append(
                {
                    "subject_id": sid,
                    "target": target,
                    "known_n": len(known),
                    "hidden_n": len(block),
                    "known_pos": int(known[target].sum()),
                    "feasible_min": min(feasible) if feasible else np.nan,
                    "feasible_max": max(feasible) if feasible else np.nan,
                    "base_sum": current_sum,
                    "target_sum": target_sum if target_sum is not None else current_sum,
                    "changed": changed,
                }
            )
    return oq.clip(pred), pd.DataFrame(detail)


def adjust_oof(train: pd.DataFrame, base: np.ndarray, strategy: str, weight: float, prior: str) -> tuple[np.ndarray, pd.DataFrame]:
    pred = base.copy()
    details = []
    folds = d.make_folds(train, "subject_blocks")
    for fold, (tr_idx, val_idx) in enumerate(folds):
        ref = train.iloc[tr_idx].copy()
        val = train.iloc[val_idx].copy()
        fold_pred, fold_detail = adjust(ref, val, pred, strategy, weight, prior)
        pred[val_idx] = fold_pred[val_idx]
        fold_detail["fold"] = fold
        details.append(fold_detail)
    return oq.clip(pred), pd.concat(details, ignore_index=True)


def save_submission(train: pd.DataFrame, sub: pd.DataFrame, base_sub: pd.DataFrame, strategy: str, weight: float, prior: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    pred = base_sub[TARGETS].to_numpy(dtype=float).copy()
    # align local row indexes with the sorted submission frame
    sub_rows = sub.reset_index(drop=True).copy()
    out_pred, detail = adjust(train, sub_rows, pred, strategy, weight, prior)
    out = base_sub.copy()
    out[TARGETS] = oq.clip(out_pred)
    return out, detail


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--base-sub", required=True)
    parser.add_argument("--prefix", required=True)
    args = parser.parse_args()

    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sample = sub.sort_values(SUB_KEY).reset_index(drop=True)
    base = oq.clip(np.load(OUT / args.base_oof))
    base_sub = pd.read_csv(OUT / args.base_sub, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    y = train[TARGETS].to_numpy(dtype=int)
    base_loss = oq.mean_loss(y, base)

    rows = []
    best = None
    for prior in ["uniform_total", "global_center"]:
        for strategy in ["range", "nearest", "posterior_mean", "posterior_mode", "posterior_mean_nearest"]:
            for weight in [0.25, 0.50, 0.75, 1.00]:
                pred, detail = adjust_oof(train, base, strategy, weight, prior)
                loss = oq.mean_loss(y, pred)
                row = {
                    "prior": prior,
                    "strategy": strategy,
                    "weight": weight,
                    "base_loss": base_loss,
                    "candidate_loss": loss,
                    "delta": loss - base_loss,
                    "changed_blocks": int(detail["changed"].sum()),
                }
                for target in TARGETS:
                    j = TARGETS.index(target)
                    row[f"{target}_delta"] = oq.loss_col(y[:, j], pred[:, j]) - oq.loss_col(y[:, j], base[:, j])
                rows.append(row)
                if best is None or loss < best[0]["candidate_loss"]:
                    best = (row, pred, detail)
    summary = pd.DataFrame(rows).sort_values(["candidate_loss", "changed_blocks"]).reset_index(drop=True)
    summary.to_csv(OUT / f"{args.prefix}_posterior_summary.csv", index=False)
    assert best is not None
    best_row, best_pred, best_detail = best
    suffix = f"{best_row['prior']}_{best_row['strategy']}_w{best_row['weight']:g}"
    np.save(OUT / f"final_{args.prefix}_{suffix}_oof.npy", best_pred)
    best_detail.to_csv(OUT / f"{args.prefix}_{suffix}_oof_detail.csv", index=False)

    out, sub_detail = save_submission(train, sub, base_sub, str(best_row["strategy"]), float(best_row["weight"]), str(best_row["prior"]))
    out = out.sort_values(SUB_KEY).reset_index(drop=True)
    sample = sample.sort_values(SUB_KEY).reset_index(drop=True)
    assert out[SUB_KEY].equals(sample[SUB_KEY])
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(SUB_KEY).sum() == 0
    sub_detail.to_csv(OUT / f"{args.prefix}_{suffix}_submission_detail.csv", index=False)
    out_file = OUT / f"submission_{args.prefix}_{suffix}.csv"
    out.to_csv(out_file, index=False)

    print(summary.head(30).round(9).to_string(index=False))
    print("best")
    print(pd.DataFrame([best_row]).round(9).to_string(index=False))
    print(f"saved {out_file.name}")


if __name__ == "__main__":
    main()
