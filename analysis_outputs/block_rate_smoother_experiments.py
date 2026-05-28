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
TARGETS = d.TARGETS
KEY = d.KEY


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j, target in enumerate(TARGETS)}


@dataclass(frozen=True)
class BlockConfig:
    shrink: float
    alpha: float
    window: int
    gap_weighted: bool
    same_boundary_boost: float = 0.0

    @property
    def name(self) -> str:
        gw = "gap" if self.gap_weighted else "eq"
        return f"s{self.shrink:g}_a{self.alpha:g}_w{self.window}_{gw}_boost{self.same_boundary_boost:g}"


def configs() -> list[BlockConfig]:
    out = []
    for shrink in [4.0, 8.0, 16.0, 32.0]:
        for alpha in [0.15, 0.25, 0.35, 0.50, 0.70, 0.90]:
            for window in [1, 3, 5, 10, 20]:
                for gap_weighted in [False, True]:
                    out.append(BlockConfig(shrink, alpha, window, gap_weighted, 0.0))
    for shrink in [8.0, 16.0]:
        for alpha in [0.25, 0.35, 0.50]:
            for window in [3, 5, 10]:
                out.append(BlockConfig(shrink, alpha, window, True, 0.20))
                out.append(BlockConfig(shrink, alpha, window, True, 0.35))
    return out


def block_ids(ref: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    known = ref[KEY].copy()
    known["_kind"] = "known"
    unknown = rows[KEY].copy()
    unknown["_kind"] = "unknown"
    unknown["_row_pos"] = np.arange(len(rows))
    full = pd.concat([known, unknown], ignore_index=True, sort=False).sort_values(KEY).reset_index(drop=True)
    full["_block"] = full.groupby("subject_id")["_kind"].transform(lambda s: s.ne(s.shift()).cumsum())
    return full[full["_kind"].eq("unknown")].copy()


def subject_prior(ref: pd.DataFrame, rows: pd.DataFrame, shrink: float) -> np.ndarray:
    return cal.subject_prior(ref, rows, shrink)


def block_smoother(ref: pd.DataFrame, rows: pd.DataFrame, cfg: BlockConfig) -> np.ndarray:
    pred = subject_prior(ref, rows, cfg.shrink)
    ref_by_subject = {
        sid: g.sort_values("lifelog_date").reset_index(drop=True)
        for sid, g in ref.groupby("subject_id", sort=False)
    }
    unknown = block_ids(ref, rows)
    rows_reset = rows.reset_index(drop=True)

    for (sid, bid), block in unknown.groupby(["subject_id", "_block"], sort=False):
        locs = block["_row_pos"].to_numpy(dtype=int)
        start = rows_reset.loc[locs, "lifelog_date"].min()
        end = rows_reset.loc[locs, "lifelog_date"].max()
        hist = ref_by_subject.get(sid)
        if hist is None or hist.empty:
            continue
        before = hist[hist["lifelog_date"] < start].tail(cfg.window)
        after = hist[hist["lifelog_date"] > end].head(cfg.window)
        if before.empty and after.empty:
            continue
        local = np.zeros(len(TARGETS), dtype=float)
        weights = []
        values = []
        if not before.empty:
            prev_gap = max(int((start - before["lifelog_date"].max()).days), 1)
            w = 1.0 / prev_gap if cfg.gap_weighted else 1.0
            weights.append(w)
            values.append(before[TARGETS].mean().to_numpy(dtype=float))
        if not after.empty:
            next_gap = max(int((after["lifelog_date"].min() - end).days), 1)
            w = 1.0 / next_gap if cfg.gap_weighted else 1.0
            weights.append(w)
            values.append(after[TARGETS].mean().to_numpy(dtype=float))
        w_arr = np.asarray(weights, dtype=float)
        v_arr = np.vstack(values)
        local = np.average(v_arr, weights=w_arr, axis=0)

        if cfg.same_boundary_boost > 0 and len(values) == 2:
            prev_edge = before.iloc[-1][TARGETS].to_numpy(dtype=float)
            next_edge = after.iloc[0][TARGETS].to_numpy(dtype=float)
            same = prev_edge == next_edge
            edge = prev_edge
            local = np.where(same, (1.0 - cfg.same_boundary_boost) * local + cfg.same_boundary_boost * edge, local)

        pred[locs] = (1.0 - cfg.alpha) * pred[locs] + cfg.alpha * local
    return clip(pred)


def oof(train: pd.DataFrame, cfg: BlockConfig) -> np.ndarray:
    pred = np.zeros((len(train), len(TARGETS)), dtype=float)
    for tr_idx, val_idx in d.make_folds(train, "subject_blocks"):
        ref = train.iloc[tr_idx].copy()
        val = train.iloc[val_idx].copy()
        pred[val_idx] = block_smoother(ref, val, cfg)
    return clip(pred)


def grid_experiment(train: pd.DataFrame) -> pd.DataFrame:
    y = train[TARGETS].to_numpy()
    folds = d.make_folds(train, "subject_blocks")
    base = cal.base_oof(train, folds)
    current = base
    rows = []
    for name, pred, config in [("temporal_base", base, "base")]:
        row = {"model": name, "config": config, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)

    for i, cfg in enumerate(configs()):
        pred = oof(train, cfg)
        for blend in [1.0, 0.35, 0.50, 0.70]:
            p = pred if blend == 1.0 else (1.0 - blend) * current + blend * pred
            row = {
                "model": "block_rate_smoother" if blend == 1.0 else f"tiny_watch_block_blend_{blend:g}",
                "config": cfg.name,
                "mean": mean_loss(y, p),
            }
            row.update(per_target_loss(y, p))
            rows.append(row)
        if i % 50 == 0:
            print(f"[block grid] {i}/{len(configs())}", flush=True)
    out = pd.DataFrame(rows).sort_values("mean")
    out.to_csv(OUT / "block_rate_smoother_results.csv", index=False)
    return out


def nested_selection(train: pd.DataFrame, top_configs: list[BlockConfig]) -> tuple[pd.DataFrame, pd.DataFrame]:
    y = train[TARGETS].to_numpy()
    pred_current = np.zeros_like(y, dtype=float)
    pred_block = np.zeros_like(y, dtype=float)
    pred_blend = np.zeros_like(y, dtype=float)
    selected_rows = []
    for fold_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        inner_y = outer_train[TARGETS].to_numpy()
        inner_current = cal.base_oof(outer_train, d.make_folds(outer_train, "subject_blocks"))
        best = None
        best_loss = np.inf
        best_blend = 1.0
        for cfg in top_configs:
            block_pred = oof(outer_train, cfg)
            for blend in [0.35, 0.50, 0.70, 1.0]:
                p = block_pred if blend == 1.0 else (1.0 - blend) * inner_current + blend * block_pred
                loss = mean_loss(inner_y, p)
                if loss < best_loss:
                    best = cfg
                    best_blend = blend
                    best_loss = loss
        if best is None:
            raise RuntimeError("No block config selected")
        current_val = cal.temporal_base(outer_train, outer_val)
        block_val = block_smoother(outer_train, outer_val, best)
        pred_current[val_idx] = current_val
        pred_block[val_idx] = block_val
        pred_blend[val_idx] = block_val if best_blend == 1.0 else (1.0 - best_blend) * current_val + best_blend * block_val
        selected_rows.append({"fold": fold_id, "config": best.name, "blend": best_blend, "inner_loss": best_loss})
        print(f"[block nested] fold={fold_id} {best.name} blend={best_blend} inner={best_loss:.5f}", flush=True)

    rows = []
    for name, pred in [
        ("temporal_base_refit", pred_current),
        ("nested_block_only", pred_block),
        ("nested_block_blend", pred_blend),
    ]:
        row = {"model": name, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("mean"), pd.DataFrame(selected_rows)


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, cfg: BlockConfig, blend: float) -> pd.DataFrame:
    best_path = OUT / "submission_best.csv"
    if best_path.exists():
        current_pred = pd.read_csv(best_path)[TARGETS].to_numpy(dtype=float)
    else:
        current_pred = cal.temporal_base(train, sub)
    block_pred = block_smoother(train, sub, cfg)
    pred = block_pred if blend == 1.0 else (1.0 - blend) * current_pred + blend * block_pred
    out = sub[["subject_id", "sleep_date", "lifelog_date"]].copy()
    for j, target in enumerate(TARGETS):
        out[target] = clip(pred)[:, j]
    return out


def parse_config(name: str) -> BlockConfig:
    parts = name.split("_")
    shrink = float(parts[0][1:])
    alpha = float(parts[1][1:])
    window = int(parts[2][1:])
    gap_weighted = parts[3] == "gap"
    boost = float(parts[4].replace("boost", ""))
    return BlockConfig(shrink, alpha, window, gap_weighted, boost)


def main() -> None:
    train, sub, _ = d.read_labels()
    train_full = pd.read_parquet(OUT / "train_deep_features.parquet")
    sub_full = pd.read_parquet(OUT / "submission_deep_features.parquet")
    result = grid_experiment(train_full)
    print(result.head(30).round(6).to_string(index=False))
    top = result[result["model"].str.contains("block")].head(12)["config"].drop_duplicates().map(parse_config).tolist()
    nested, selected = nested_selection(train_full, top)
    nested.to_csv(OUT / "block_rate_smoother_nested_results.csv", index=False)
    selected.to_csv(OUT / "block_rate_smoother_nested_selected.csv", index=False)
    print("\nNested")
    print(nested.round(6).to_string(index=False))
    print(selected.to_string(index=False))
    best = nested.iloc[0]
    if best["model"] == "nested_block_blend":
        cfg = parse_config(str(selected["config"].mode().iloc[0]))
        blend = float(selected["blend"].mode().iloc[0])
        make_submission(train_full, sub_full, cfg, blend).to_csv(OUT / "submission_block_rate_smoother.csv", index=False)


if __name__ == "__main__":
    main()
