from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402


OUT = Path(__file__).resolve().parent
DATA = OUT.parent / "data"
TARGETS = d.TARGETS
KEY = d.KEY
EPS = 1e-5
STATE_COUNT = 2 ** len(TARGETS)


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1 - EPS)


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j, target in enumerate(TARGETS)}


def target_bits() -> np.ndarray:
    states = np.arange(STATE_COUNT, dtype=np.int64)
    bits = np.zeros((STATE_COUNT, len(TARGETS)), dtype=float)
    for j in range(len(TARGETS)):
        bits[:, j] = ((states >> j) & 1).astype(float)
    return bits


BITS = target_bits()


def encode_states(rows: pd.DataFrame) -> np.ndarray:
    y = rows[TARGETS].to_numpy(dtype=int)
    out = np.zeros(len(rows), dtype=np.int64)
    for j in range(len(TARGETS)):
        out += y[:, j] << j
    return out


def load_train_sub() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    return train, sub


def split_block_summary(train: pd.DataFrame, sub: pd.DataFrame) -> pd.DataFrame:
    tr = train[KEY + ["sleep_date"] + TARGETS].copy()
    tr["split"] = "train"
    te = sub[KEY + ["sleep_date"]].copy()
    te["split"] = "submission"
    full = pd.concat([tr, te], ignore_index=True, sort=False).sort_values(KEY).reset_index(drop=True)
    full["subject_row"] = full.groupby("subject_id").cumcount()
    full["block_id"] = (
        full.groupby("subject_id")["split"]
        .transform(lambda s: s.ne(s.shift()).cumsum())
        .astype(int)
    )

    rows = []
    for (sid, bid), g in full.groupby(["subject_id", "block_id"], sort=False):
        before = full[(full["subject_id"] == sid) & (full["subject_row"] < int(g["subject_row"].min())) & (full["split"] == "train")]
        after = full[(full["subject_id"] == sid) & (full["subject_row"] > int(g["subject_row"].max())) & (full["split"] == "train")]
        row = {
            "subject_id": sid,
            "block_id": int(bid),
            "split": str(g["split"].iloc[0]),
            "n": int(len(g)),
            "start": g["lifelog_date"].min().date().isoformat(),
            "end": g["lifelog_date"].max().date().isoformat(),
            "subject_row_start": int(g["subject_row"].min()),
            "subject_row_end": int(g["subject_row"].max()),
            "prev_train_gap_days": np.nan,
            "next_train_gap_days": np.nan,
        }
        if not before.empty:
            prev = before.iloc[-1]
            row["prev_train_gap_days"] = int((g["lifelog_date"].min() - prev["lifelog_date"]).days)
            for target in TARGETS:
                row[f"prev_{target}"] = prev[target]
        if not after.empty:
            nxt = after.iloc[0]
            row["next_train_gap_days"] = int((nxt["lifelog_date"] - g["lifelog_date"].max()).days)
            for target in TARGETS:
                row[f"next_{target}"] = nxt[target]
        if row["split"] == "train":
            for target in TARGETS:
                row[f"block_rate_{target}"] = float(g[target].mean())
        rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(OUT / "breakthrough_split_blocks.csv", index=False)
    return out


def subject_prior_oof(train: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]], shrink: float = 16.0) -> np.ndarray:
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    for tr_idx, val_idx in folds:
        pred[val_idx] = cal.subject_prior(train.iloc[tr_idx], train.iloc[val_idx], shrink)
    return clip(pred)


def full_subject_oracle(train: pd.DataFrame) -> np.ndarray:
    means = train.groupby("subject_id")[TARGETS].mean()
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    for i, sid in enumerate(train["subject_id"]):
        pred[i] = means.loc[sid].to_numpy(dtype=float)
    return clip(pred)


def validation_block_oracle(train: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]], shrink: float = 0.5) -> np.ndarray:
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    global_mean = train[TARGETS].mean().to_numpy(dtype=float)
    sorted_train = train.sort_values(["subject_id", "lifelog_date"]).copy()
    sorted_train["orig_index"] = sorted_train.index
    sorted_train["subject_pos"] = sorted_train.groupby("subject_id").cumcount()
    pos_lookup = sorted_train.set_index("orig_index")["subject_pos"].to_dict()
    for _, val_idx in folds:
        val_set = set(int(x) for x in val_idx)
        val_rows = sorted_train[sorted_train["orig_index"].isin(val_set)].copy()
        for _, g in val_rows.groupby("subject_id", sort=False):
            breaks = g["subject_pos"].diff().fillna(1).ne(1).cumsum()
            for _, block in g.groupby(breaks):
                idx = block["orig_index"].to_numpy(dtype=int)
                rate = (block[TARGETS].sum().to_numpy(dtype=float) + shrink * global_mean) / (len(block) + shrink)
                pred[idx] = rate
    return clip(pred)


def leave_one_in_block_oracle(train: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]], shrink: float = 1.0) -> np.ndarray:
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    global_mean = train[TARGETS].mean().to_numpy(dtype=float)
    sorted_train = train.sort_values(["subject_id", "lifelog_date"]).copy()
    sorted_train["orig_index"] = sorted_train.index
    sorted_train["subject_pos"] = sorted_train.groupby("subject_id").cumcount()
    for _, val_idx in folds:
        val_set = set(int(x) for x in val_idx)
        val_rows = sorted_train[sorted_train["orig_index"].isin(val_set)].copy()
        for _, g in val_rows.groupby("subject_id", sort=False):
            breaks = g["subject_pos"].diff().fillna(1).ne(1).cumsum()
            for _, block in g.groupby(breaks):
                y = block[TARGETS].to_numpy(dtype=float)
                idx = block["orig_index"].to_numpy(dtype=int)
                sums = y.sum(axis=0)
                for row_i, orig_idx in enumerate(idx):
                    denom = max(len(block) - 1, 0) + shrink
                    pred[orig_idx] = (sums - y[row_i] + shrink * global_mean) / denom
    return clip(pred)


def oracle_bound_experiment(train: pd.DataFrame) -> pd.DataFrame:
    folds = d.make_folds(train, "subject_blocks")
    y = train[TARGETS].to_numpy()
    preds = {
        "temporal_base_foldsafe": cal.base_oof(train, folds),
        "subject_prior_foldsafe": subject_prior_oof(train, folds),
        "full_subject_rate_oracle": full_subject_oracle(train),
        "validation_block_rate_oracle": validation_block_oracle(train, folds),
        "validation_block_leave_one_oracle": leave_one_in_block_oracle(train, folds),
    }
    rows = []
    for name, pred in preds.items():
        row = {"model": name, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)
    out = pd.DataFrame(rows).sort_values("mean")
    out.to_csv(OUT / "breakthrough_oracle_bounds.csv", index=False)
    return out


@dataclass(frozen=True)
class MarkovConfig:
    trans_alpha: float
    subject_weight: float
    blend_with_base: float

    @property
    def name(self) -> str:
        return f"markov_a{self.trans_alpha:g}_sw{self.subject_weight:g}_bw{self.blend_with_base:g}"


def transition_matrix(ref: pd.DataFrame, subject_id: str | None, alpha: float, global_counts: np.ndarray | None = None) -> np.ndarray:
    counts = np.zeros((STATE_COUNT, STATE_COUNT), dtype=float)
    rows = ref if subject_id is None else ref[ref["subject_id"] == subject_id]
    for _, g in rows.sort_values("lifelog_date").groupby("subject_id", sort=False):
        states = encode_states(g)
        if len(states) < 2:
            continue
        for a, b in zip(states[:-1], states[1:]):
            counts[int(a), int(b)] += 1.0
    if global_counts is not None:
        counts += global_counts
    counts += alpha
    return counts / counts.sum(axis=1, keepdims=True)


def raw_transition_counts(ref: pd.DataFrame) -> np.ndarray:
    counts = np.zeros((STATE_COUNT, STATE_COUNT), dtype=float)
    for _, g in ref.sort_values(["subject_id", "lifelog_date"]).groupby("subject_id", sort=False):
        states = encode_states(g)
        for a, b in zip(states[:-1], states[1:]):
            counts[int(a), int(b)] += 1.0
    return counts


def state_prior(ref: pd.DataFrame, subject_id: str, alpha: float = 0.5) -> np.ndarray:
    states = encode_states(ref[ref["subject_id"] == subject_id])
    counts = np.bincount(states, minlength=STATE_COUNT).astype(float)
    if counts.sum() == 0:
        states = encode_states(ref)
        counts = np.bincount(states, minlength=STATE_COUNT).astype(float)
    counts += alpha
    return counts / counts.sum()


def markov_block_probs(
    ref: pd.DataFrame,
    rows: pd.DataFrame,
    cfg: MarkovConfig,
    base_pred: np.ndarray | None = None,
) -> np.ndarray:
    pred = np.zeros((len(rows), len(TARGETS)), dtype=float)
    global_counts = raw_transition_counts(ref)
    global_p = transition_matrix(ref, None, cfg.trans_alpha)
    ref_sorted = {
        sid: g.sort_values("lifelog_date").reset_index(drop=True)
        for sid, g in ref.groupby("subject_id", sort=False)
    }

    sorted_rows = rows.sort_values(["subject_id", "lifelog_date"]).copy()
    sorted_rows["local_index"] = np.arange(len(rows))[sorted_rows.index.argsort().argsort()]
    # local_index above can be brittle after arbitrary indexes, so overwrite through a direct map.
    index_map = {idx: pos for pos, idx in enumerate(rows.index)}
    sorted_rows["local_index"] = sorted_rows.index.map(index_map).astype(int)

    for sid, target_rows in sorted_rows.groupby("subject_id", sort=False):
        hist = ref_sorted.get(sid)
        p_sub = transition_matrix(ref, str(sid), cfg.trans_alpha, cfg.subject_weight * global_counts)
        p = 0.5 * p_sub + 0.5 * global_p
        prior = state_prior(ref, str(sid))
        positions = target_rows.reset_index(drop=True)
        for _, row in positions.iterrows():
            day = row["lifelog_date"]
            loc = int(row["local_index"])
            if hist is None or hist.empty:
                state_prob = prior
            else:
                prev = hist[hist["lifelog_date"] < day]
                nxt = hist[hist["lifelog_date"] > day]
                if not prev.empty and not nxt.empty:
                    start = int(encode_states(prev.iloc[[-1]])[0])
                    end = int(encode_states(nxt.iloc[[0]])[0])
                    gap = max(int((nxt.iloc[0]["lifelog_date"] - prev.iloc[-1]["lifelog_date"]).days), 1)
                    step = max(int((day - prev.iloc[-1]["lifelog_date"]).days), 1)
                    step = min(step, gap)
                    fwd = np.linalg.matrix_power(p, step)[start]
                    bwd = np.linalg.matrix_power(p, max(gap - step, 0))[:, end]
                    state_prob = fwd * bwd
                    total = state_prob.sum()
                    state_prob = prior if total <= 0 else state_prob / total
                elif not prev.empty:
                    start = int(encode_states(prev.iloc[[-1]])[0])
                    step = max(int((day - prev.iloc[-1]["lifelog_date"]).days), 1)
                    state_prob = np.linalg.matrix_power(p, min(step, 60))[start]
                elif not nxt.empty:
                    end = int(encode_states(nxt.iloc[[0]])[0])
                    step = max(int((nxt.iloc[0]["lifelog_date"] - day).days), 1)
                    likelihood = np.linalg.matrix_power(p, min(step, 60))[:, end]
                    state_prob = prior * likelihood
                    total = state_prob.sum()
                    state_prob = prior if total <= 0 else state_prob / total
                else:
                    state_prob = prior
            pred[loc] = state_prob @ BITS

    pred = clip(pred)
    if base_pred is not None and cfg.blend_with_base < 1.0:
        pred = (1.0 - cfg.blend_with_base) * base_pred + cfg.blend_with_base * pred
    return clip(pred)


def markov_oof(train: pd.DataFrame, cfg: MarkovConfig) -> np.ndarray:
    folds = d.make_folds(train, "subject_blocks")
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    for fold_id, (tr_idx, val_idx) in enumerate(folds):
        ref = train.iloc[tr_idx].copy()
        val = train.iloc[val_idx].copy()
        base = cal.temporal_base(ref, val)
        pred[val_idx] = markov_block_probs(ref, val, cfg, base)
        print(f"[markov] fold={fold_id} {cfg.name}", flush=True)
    return clip(pred)


def markov_experiment(train: pd.DataFrame) -> pd.DataFrame:
    y = train[TARGETS].to_numpy()
    configs = [
        MarkovConfig(0.01, 0.0, 1.0),
        MarkovConfig(0.05, 0.0, 1.0),
        MarkovConfig(0.10, 0.0, 1.0),
        MarkovConfig(0.05, 0.05, 1.0),
        MarkovConfig(0.10, 0.10, 1.0),
        MarkovConfig(0.10, 0.10, 0.25),
        MarkovConfig(0.10, 0.10, 0.50),
        MarkovConfig(0.20, 0.20, 0.25),
        MarkovConfig(0.20, 0.20, 0.50),
    ]
    rows = []
    base = cal.base_oof(train, d.make_folds(train, "subject_blocks"))
    row = {"model": "temporal_base", "config": "base", "mean": mean_loss(y, base)}
    row.update(per_target_loss(y, base))
    rows.append(row)
    for cfg in configs:
        pred = markov_oof(train, cfg)
        row = {"model": "pattern_markov", "config": cfg.name, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)
    out = pd.DataFrame(rows).sort_values("mean")
    out.to_csv(OUT / "breakthrough_markov_results.csv", index=False)
    return out


def feature_matrix(train: pd.DataFrame) -> pd.DataFrame:
    deep = pd.read_parquet(OUT / "train_deep_features.parquet")
    meta_path = OUT / "meta_sensor_features.parquet"
    if meta_path.exists():
        meta = pd.read_parquet(meta_path)
        deep = deep.merge(meta, on=KEY, how="left")
    excluded = set(TARGETS + KEY + ["sleep_date", "split", "dow", "month"])
    cols = [c for c in deep.columns if c not in excluded and pd.api.types.is_numeric_dtype(deep[c])]
    out = train[KEY + TARGETS].merge(deep[KEY + cols], on=KEY, how="left")
    return out


def top_feature_candidates(frame: pd.DataFrame, train_idx: np.ndarray, target: str, limit: int = 350) -> list[str]:
    excluded = set(TARGETS + KEY)
    cols = [c for c in frame.columns if c not in excluded and pd.api.types.is_numeric_dtype(frame[c])]
    y = frame.iloc[train_idx][target].to_numpy(dtype=float)
    scores = []
    for col in cols:
        x = frame.iloc[train_idx][col].replace([np.inf, -np.inf], np.nan).to_numpy(dtype=float)
        mask = np.isfinite(x)
        if mask.sum() < 40 or np.nanstd(x[mask]) == 0:
            continue
        y0 = y[mask] == 0
        y1 = y[mask] == 1
        if y0.sum() < 8 or y1.sum() < 8:
            continue
        diff = abs(float(np.nanmean(x[mask][y1]) - np.nanmean(x[mask][y0])))
        score = diff / (float(np.nanstd(x[mask])) + 1e-9)
        miss_diff = abs(float(np.mean(~mask[y == 1])) - np.mean(~mask[y == 0])) if len(mask) == len(y) else 0.0
        scores.append((score + miss_diff, col))
    scores.sort(reverse=True)
    return [col for _, col in scores[:limit]]


@dataclass
class ThresholdModel:
    col: str
    threshold: float
    rates: dict[str, float]
    default: float


def fit_threshold(x: np.ndarray, y: np.ndarray, col: str, smooth: float = 2.0) -> ThresholdModel:
    x = x.astype(float)
    finite = np.isfinite(x)
    default = float((y.sum() + smooth * 0.5) / (len(y) + smooth))
    if finite.sum() < 20 or np.nanstd(x[finite]) == 0:
        return ThresholdModel(col, np.nan, {"nan": default, "lo": default, "hi": default}, default)
    quantiles = np.unique(np.nanquantile(x[finite], np.linspace(0.10, 0.90, 9)))
    best_loss = np.inf
    best = ThresholdModel(col, float(quantiles[len(quantiles) // 2]), {"nan": default, "lo": default, "hi": default}, default)
    for thr in quantiles:
        bins = {
            "nan": ~finite,
            "lo": finite & (x <= thr),
            "hi": finite & (x > thr),
        }
        rates = {}
        pred = np.full(len(y), default, dtype=float)
        for name, mask in bins.items():
            rate = float((y[mask].sum() + smooth * default) / (mask.sum() + smooth)) if mask.sum() else default
            rates[name] = rate
            pred[mask] = rate
        loss = log_loss(y, clip(pred), labels=[0, 1])
        if loss < best_loss:
            best_loss = loss
            best = ThresholdModel(col, float(thr), rates, default)
    return best


def predict_threshold(model: ThresholdModel, x: np.ndarray) -> np.ndarray:
    x = x.astype(float)
    finite = np.isfinite(x)
    pred = np.full(len(x), model.default, dtype=float)
    pred[~finite] = model.rates.get("nan", model.default)
    pred[finite & (x <= model.threshold)] = model.rates.get("lo", model.default)
    pred[finite & (x > model.threshold)] = model.rates.get("hi", model.default)
    return clip(pred)


def threshold_inner_loss(frame: pd.DataFrame, idx: np.ndarray, target: str, col: str) -> float:
    rows = frame.iloc[idx].reset_index(drop=True)
    losses = []
    for tr_idx, val_idx in d.make_folds(rows, "subject_blocks", n_splits=3):
        xtr = rows.iloc[tr_idx][col].replace([np.inf, -np.inf], np.nan).to_numpy(dtype=float)
        ytr = rows.iloc[tr_idx][target].to_numpy(dtype=int)
        model = fit_threshold(xtr, ytr, col)
        xval = rows.iloc[val_idx][col].replace([np.inf, -np.inf], np.nan).to_numpy(dtype=float)
        yval = rows.iloc[val_idx][target].to_numpy(dtype=int)
        losses.append(log_loss(yval, predict_threshold(model, xval), labels=[0, 1]))
    return float(np.mean(losses))


def threshold_probe(train: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = feature_matrix(train)
    folds = d.make_folds(train, "subject_blocks")
    y = train[TARGETS].to_numpy()
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    selected_rows = []
    oracle_pred = np.zeros_like(pred)

    for fold_id, (tr_idx, val_idx) in enumerate(folds):
        for j, target in enumerate(TARGETS):
            candidates = top_feature_candidates(frame, tr_idx, target, limit=80)
            scored = []
            for col in candidates:
                try:
                    scored.append((threshold_inner_loss(frame, tr_idx, target, col), col))
                except Exception:
                    continue
            scored.sort()
            if not scored:
                p = float(train.iloc[tr_idx][target].mean())
                pred[val_idx, j] = p
                selected_rows.append({"fold": fold_id, "target": target, "rank": 0, "feature": "__prior__", "inner_loss": np.nan})
                continue
            for rank, (loss, col) in enumerate(scored[:10], start=1):
                selected_rows.append({"fold": fold_id, "target": target, "rank": rank, "feature": col, "inner_loss": loss})
            best_col = scored[0][1]
            model = fit_threshold(
                frame.iloc[tr_idx][best_col].replace([np.inf, -np.inf], np.nan).to_numpy(dtype=float),
                train.iloc[tr_idx][target].to_numpy(dtype=int),
                best_col,
            )
            pred[val_idx, j] = predict_threshold(
                model,
                frame.iloc[val_idx][best_col].replace([np.inf, -np.inf], np.nan).to_numpy(dtype=float),
            )

            # Cheating diagnostic: if even validation-selected one-threshold features are weak,
            # a hidden one-column threshold rule is unlikely to exist in the current feature matrix.
            best_oracle_loss = np.inf
            best_oracle_col = None
            for col in candidates:
                m = fit_threshold(
                    frame.iloc[val_idx][col].replace([np.inf, -np.inf], np.nan).to_numpy(dtype=float),
                    train.iloc[val_idx][target].to_numpy(dtype=int),
                    col,
                    smooth=1.0,
                )
                pval = predict_threshold(
                    m,
                    frame.iloc[val_idx][col].replace([np.inf, -np.inf], np.nan).to_numpy(dtype=float),
                )
                loss = log_loss(train.iloc[val_idx][target], pval, labels=[0, 1])
                if loss < best_oracle_loss:
                    best_oracle_loss = loss
                    best_oracle_col = col
                    oracle_pred[val_idx, j] = pval
            selected_rows.append(
                {
                    "fold": fold_id,
                    "target": target,
                    "rank": -1,
                    "feature": best_oracle_col,
                    "inner_loss": best_oracle_loss,
                }
            )
            print(f"[threshold] fold={fold_id} target={target} best={best_col} inner={scored[0][0]:.5f}", flush=True)

    base = cal.base_oof(train, folds)
    rows = []
    for name, p in [
        ("temporal_base", base),
        ("nested_single_threshold", pred),
        ("base_threshold_blend_0.20", 0.80 * base + 0.20 * pred),
        ("base_threshold_blend_0.35", 0.65 * base + 0.35 * pred),
        ("oracle_val_selected_threshold", oracle_pred),
    ]:
        row = {"model": name, "mean": mean_loss(y, p)}
        row.update(per_target_loss(y, p))
        rows.append(row)
    results = pd.DataFrame(rows).sort_values("mean")
    selected = pd.DataFrame(selected_rows)
    results.to_csv(OUT / "breakthrough_threshold_results.csv", index=False)
    selected.to_csv(OUT / "breakthrough_threshold_selected.csv", index=False)
    return results, selected


def target_rate_constraints(train: pd.DataFrame, sub: pd.DataFrame) -> pd.DataFrame:
    rows = []
    totals = pd.concat([train[KEY], sub[KEY]], ignore_index=True).groupby("subject_id").size()
    train_counts = train.groupby("subject_id").size()
    pos = train.groupby("subject_id")[TARGETS].sum()
    for sid in sorted(totals.index):
        n_total = int(totals.loc[sid])
        n_train = int(train_counts.loc[sid])
        n_hidden = n_total - n_train
        for target in TARGETS:
            known_pos = int(pos.loc[sid, target])
            rows.append(
                {
                    "subject_id": sid,
                    "target": target,
                    "known_n": n_train,
                    "hidden_n": n_hidden,
                    "known_pos": known_pos,
                    "known_rate": known_pos / n_train,
                    "min_full_rate": known_pos / n_total,
                    "max_full_rate": (known_pos + n_hidden) / n_total,
                    "hidden_pos_for_full_50pct": max(0, min(n_hidden, round(0.5 * n_total - known_pos))),
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "breakthrough_target_rate_constraints.csv", index=False)
    return out


def main() -> None:
    train_csv, sub = load_train_sub()
    train = pd.read_parquet(OUT / "train_deep_features.parquet")
    threshold_only = "--threshold-only" in sys.argv
    if not threshold_only:
        print("Writing split block summary", flush=True)
        split_block_summary(train_csv, sub)
        print("Writing target rate constraints", flush=True)
        target_rate_constraints(train_csv, sub)

        print("Running oracle bound experiment", flush=True)
        oracle = oracle_bound_experiment(train)
        print(oracle.round(5).to_string(index=False))

        print("Running pattern Markov experiment", flush=True)
        markov = markov_experiment(train)
        print(markov.round(5).to_string(index=False))

    print("Running nested threshold feature probe", flush=True)
    threshold, selected = threshold_probe(train)
    print(threshold.round(5).to_string(index=False))
    print(selected[selected["rank"].isin([1, -1])].head(80).to_string(index=False))


if __name__ == "__main__":
    main()
