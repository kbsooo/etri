from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.append(str(Path(__file__).resolve().parent))

import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = hbr.TARGETS
KEY = hbr.KEY
EPS = 1e-5


@dataclass(frozen=True)
class MotifConfig:
    mode: str
    radius: int
    k: int
    tau: float
    shrink: float

    @property
    def name(self) -> str:
        tau_tag = str(self.tau).replace(".", "p")
        shrink_tag = str(self.shrink).replace(".", "p")
        return f"motif_{self.mode}_r{self.radius}_k{self.k}_tau{tau_tag}_s{shrink_tag}"


@dataclass(frozen=True)
class PeriodConfig:
    period: int
    k: int
    shrink: float

    @property
    def name(self) -> str:
        shrink_tag = str(self.shrink).replace(".", "p")
        return f"period_same_p{self.period}_k{self.k}_s{shrink_tag}"


@dataclass
class MotifFeature:
    vec_by_target: np.ndarray
    subject_mean: np.ndarray
    global_mean: np.ndarray
    subject_id: str
    start_day: pd.Timestamp
    end_day: pd.Timestamp
    length: int
    prev: np.ndarray
    next: np.ndarray


def clip(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def known_positions_for_subject(rows: pd.DataFrame, known_mask: np.ndarray, sid: str, block_positions: np.ndarray) -> np.ndarray:
    block_set = set(int(p) for p in block_positions)
    subj = rows["subject_id"].astype(str).eq(str(sid)).to_numpy()
    return np.asarray([int(p) for p in np.where(subj & known_mask)[0] if int(p) not in block_set], dtype=int)


def safe_nanmean(values: np.ndarray, fallback: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return fallback.copy()
    out = np.nanmean(values, axis=0)
    return np.nan_to_num(out, nan=fallback)


def take_flank(y: np.ndarray, idxs: np.ndarray, radius: int, side: str, fill: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    out = np.zeros((radius, len(TARGETS)), dtype=np.float64)
    avail = np.zeros((radius, len(TARGETS)), dtype=np.float64)
    chosen = idxs[-radius:][::-1] if side == "prev" else idxs[:radius]
    for r in range(radius):
        if r < len(chosen):
            vals = y[int(chosen[r])].astype(np.float64)
            ok = np.isfinite(vals)
            out[r] = np.where(ok, vals, fill)
            avail[r] = ok.astype(float)
        else:
            out[r] = fill
    return out, avail


def motif_feature(
    rows: pd.DataFrame,
    y: np.ndarray,
    block: hbr.Block,
    known_mask: np.ndarray,
    radius: int,
) -> MotifFeature:
    sid = str(block.subject_id)
    known_subject = known_positions_for_subject(rows, known_mask, sid, block.positions)
    known_all = np.where(known_mask)[0]
    global_mean = np.nanmean(y[known_all], axis=0)
    global_mean = np.nan_to_num(global_mean, nan=0.5)
    subject_mean = safe_nanmean(y[known_subject], global_mean)

    before = known_subject[known_subject < int(block.positions.min())]
    after = known_subject[known_subject > int(block.positions.max())]
    prev_seq, prev_avail = take_flank(y, before, radius, "prev", subject_mean)
    next_seq, next_avail = take_flank(y, after, radius, "next", subject_mean)
    prev_edge = prev_seq[0].copy()
    next_edge = next_seq[0].copy()
    prev = np.where(prev_avail[0] > 0, prev_edge, np.nan)
    nxt = np.where(next_avail[0] > 0, next_edge, np.nan)
    before_mean = safe_nanmean(y[before[-max(radius, 1) :]], subject_mean)
    after_mean = safe_nanmean(y[after[: max(radius, 1)]], subject_mean)

    block_rows = rows.iloc[block.positions]
    start_day = pd.Timestamp(block.start)
    end_day = pd.Timestamp(block.end)
    start_dow = float(start_day.dayofweek)
    end_dow = float(end_day.dayofweek)
    gap_prev = float(int(block.positions.min()) - int(before[-1])) if len(before) else 99.0
    gap_next = float(int(after[0]) - int(block.positions.max())) if len(after) else 99.0
    geom = np.array(
        [
            block.n / 16.0,
            float(block_rows["subject_phase"].mean()),
            float(block_rows["subject_phase"].min()),
            float(block_rows["subject_phase"].max()),
            np.sin(2.0 * np.pi * start_dow / 7.0),
            np.cos(2.0 * np.pi * start_dow / 7.0),
            np.sin(2.0 * np.pi * end_dow / 7.0),
            np.cos(2.0 * np.pi * end_dow / 7.0),
            float(block_rows["is_weekend"].mean()),
            np.log1p(min(gap_prev, 60.0)) / np.log1p(60.0),
            np.log1p(min(gap_next, 60.0)) / np.log1p(60.0),
            min(float(len(before)), 80.0) / 80.0,
            min(float(len(after)), 80.0) / 80.0,
        ],
        dtype=np.float64,
    )
    same_edge = (
        (prev_avail[0] > 0)
        & (next_avail[0] > 0)
        & (np.rint(prev_edge).astype(int) == np.rint(next_edge).astype(int))
    ).astype(float)

    vecs = []
    for j in range(len(TARGETS)):
        target_part = np.concatenate(
            [
                prev_seq[:, j],
                prev_avail[:, j],
                next_seq[:, j],
                next_avail[:, j],
            ]
        )
        all_part = np.concatenate(
            [
                prev_edge,
                prev_avail[0],
                next_edge,
                next_avail[0],
                before_mean,
                after_mean,
                subject_mean,
                global_mean,
                same_edge,
            ]
        )
        vecs.append(np.nan_to_num(np.concatenate([target_part, all_part, geom]), nan=0.0))
    return MotifFeature(
        vec_by_target=np.vstack(vecs).astype(np.float32),
        subject_mean=clip(subject_mean),
        global_mean=clip(global_mean),
        subject_id=sid,
        start_day=start_day,
        end_day=end_day,
        length=int(block.n),
        prev=prev,
        next=nxt,
    )


def context_touches(a: hbr.Block, b: hbr.Block, radius: int) -> bool:
    if a.subject_id != b.subject_id:
        return False
    alo = int(a.positions.min()) - radius
    ahi = int(a.positions.max()) + radius
    blo = int(b.positions.min()) - radius
    bhi = int(b.positions.max()) + radius
    return not (ahi < blo or bhi < alo)


def donor_indices(blocks: list[hbr.Block], i: int, cfg: MotifConfig) -> np.ndarray:
    target = blocks[i]
    keep = []
    for k, block in enumerate(blocks):
        if k == i:
            keep.append(False)
            continue
        if cfg.mode == "strict" and block.subject_id == target.subject_id:
            keep.append(False)
            continue
        if cfg.mode == "same" and block.subject_id != target.subject_id:
            keep.append(False)
            continue
        if context_touches(target, block, cfg.radius):
            keep.append(False)
            continue
        keep.append(True)
    return np.where(np.asarray(keep, dtype=bool))[0]


def motif_predict_one(
    i: int,
    blocks: list[hbr.Block],
    features: list[MotifFeature],
    rates: np.ndarray,
    cfg: MotifConfig,
) -> np.ndarray:
    idx_all = donor_indices(blocks, i, cfg)
    fallback = features[i].subject_mean.copy()
    out = fallback.copy()
    if len(idx_all) == 0:
        return clip(out)
    for j in range(len(TARGETS)):
        x_d = np.vstack([features[k].vec_by_target[j] for k in idx_all]).astype(np.float64)
        x_i = features[i].vec_by_target[j].astype(np.float64)
        mu = x_d.mean(axis=0)
        sd = x_d.std(axis=0)
        sd = np.where(sd < 1e-6, 1.0, sd)
        z_d = (x_d - mu) / sd
        z_i = (x_i - mu) / sd
        dist = np.sqrt(np.maximum(np.mean((z_d - z_i) ** 2, axis=1), 0.0))
        order = np.argsort(dist)[: min(cfg.k, len(idx_all))]
        chosen = idx_all[order]
        d = dist[order]
        raw_w = np.exp(-d / max(cfg.tau, 1e-6))
        if not np.isfinite(raw_w).all() or raw_w.sum() <= 1e-12:
            raw_w = 1.0 / np.maximum(d, 1e-3)
        sim_mass = float(np.clip(raw_w.mean(), 0.05, 1.0) * len(chosen))
        w = raw_w / raw_w.sum()
        local = float(np.dot(w, rates[chosen, j]))
        out[j] = (sim_mass * local + cfg.shrink * fallback[j]) / (sim_mass + cfg.shrink)
    return clip(out)


def period_donor_indices(blocks: list[hbr.Block], i: int) -> np.ndarray:
    target = blocks[i]
    keep = []
    for k, block in enumerate(blocks):
        keep.append(k != i and block.subject_id == target.subject_id and not context_touches(target, block, 1))
    return np.where(np.asarray(keep, dtype=bool))[0]


def circular_day_distance(a: pd.Timestamp, b: pd.Timestamp, period: int) -> float:
    delta = abs(int((a - b).days))
    rem = delta % period
    return float(min(rem, period - rem))


def period_predict_one(
    i: int,
    blocks: list[hbr.Block],
    features: list[MotifFeature],
    rates: np.ndarray,
    cfg: PeriodConfig,
) -> np.ndarray:
    idx_all = period_donor_indices(blocks, i)
    fallback = features[i].subject_mean.copy()
    out = fallback.copy()
    if len(idx_all) == 0:
        return clip(out)
    target = features[i]
    d = []
    for k in idx_all:
        fk = features[k]
        len_pen = abs(fk.length - target.length) / 16.0
        dow_pen = circular_day_distance(target.start_day, fk.start_day, cfg.period) / max(cfg.period / 2.0, 1.0)
        edge_pen = 0.0
        ok_prev = np.isfinite(target.prev) & np.isfinite(fk.prev)
        ok_next = np.isfinite(target.next) & np.isfinite(fk.next)
        if ok_prev.any():
            edge_pen += float(np.mean(np.abs(target.prev[ok_prev] - fk.prev[ok_prev])))
        if ok_next.any():
            edge_pen += float(np.mean(np.abs(target.next[ok_next] - fk.next[ok_next])))
        d.append(len_pen + dow_pen + 0.25 * edge_pen)
    order = np.argsort(np.asarray(d))[: min(cfg.k, len(idx_all))]
    chosen = idx_all[order]
    raw_w = 1.0 / np.maximum(np.asarray(d)[order], 1e-3)
    w = raw_w / raw_w.sum()
    local = w @ rates[chosen]
    sim_mass = float(min(len(chosen), cfg.k))
    out = (sim_mass * local + cfg.shrink * fallback) / (sim_mass + cfg.shrink)
    return clip(out)


def build_features(
    rows: pd.DataFrame,
    y: np.ndarray,
    blocks: list[hbr.Block],
    known: np.ndarray,
    radius: int,
) -> list[MotifFeature]:
    features = []
    for block in blocks:
        mask = known.copy()
        mask[block.positions] = False
        features.append(motif_feature(rows, y, block, mask, radius))
    return features


def evaluate_motif_methods(rows: pd.DataFrame, y: np.ndarray, blocks: list[hbr.Block]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    known = hbr.base_known_mask(rows)
    rates = hbr.true_rates(y, blocks)
    subject_features = build_features(rows, y, blocks, known, radius=1)
    preds: dict[str, np.ndarray] = {
        "subject_mean": np.vstack([f.subject_mean for f in subject_features]),
        "global_mean": np.vstack([f.global_mean for f in subject_features]),
    }
    configs = [
        MotifConfig(mode, radius, k, tau, shrink)
        for mode in ["strict", "local", "same"]
        for radius in [1, 2, 3, 5]
        for k in [3, 5, 8, 16]
        for tau in [0.5, 1.0]
        for shrink in ([8.0, 16.0] if mode == "same" else [16.0, 32.0])
    ]
    period_configs = [
        PeriodConfig(period, k, shrink)
        for period in [7, 14, 21, 28]
        for k in [3, 5, 8]
        for shrink in [8.0, 16.0]
    ]
    feature_cache: dict[int, list[MotifFeature]] = {1: subject_features}
    for cfg in configs:
        if cfg.radius not in feature_cache:
            feature_cache[cfg.radius] = build_features(rows, y, blocks, known, cfg.radius)
        feats = feature_cache[cfg.radius]
        preds[cfg.name] = np.vstack([motif_predict_one(i, blocks, feats, rates, cfg) for i in range(len(blocks))])
    period_feats = feature_cache[1]
    for cfg in period_configs:
        preds[cfg.name] = np.vstack([period_predict_one(i, blocks, period_feats, rates, cfg) for i in range(len(blocks))])
    summary, target_detail = hbr.summarize_predictions(y, blocks, rates, preds)
    return summary, target_detail, preds


def hidden_prediction_for_method(
    method: str,
    rows: pd.DataFrame,
    y: np.ndarray,
    train_blocks: list[hbr.Block],
    hidden_blocks: list[hbr.Block],
) -> np.ndarray:
    known = hbr.base_known_mask(rows)
    train_rates = hbr.true_rates(y, train_blocks)
    if method == "subject_mean":
        return np.vstack([motif_feature(rows, y, block, known, 1).subject_mean for block in hidden_blocks])
    if method.startswith("period_same_"):
        parts = method.split("_")
        cfg = PeriodConfig(
            period=int(parts[2].removeprefix("p")),
            k=int(parts[3].removeprefix("k")),
            shrink=float(parts[4].removeprefix("s").replace("p", ".")),
        )
        train_feats = build_features(rows, y, train_blocks, known, radius=1)
        hidden_feats = [motif_feature(rows, y, block, known, 1) for block in hidden_blocks]
        blocks = train_blocks + hidden_blocks
        feats = train_feats + hidden_feats
        rates = np.vstack([train_rates, np.full((len(hidden_blocks), len(TARGETS)), np.nan)])
        out = []
        for h in range(len(hidden_blocks)):
            i = len(train_blocks) + h
            # Reuse period scoring but force donors to the train side.
            idx_all = period_donor_indices(blocks, i)
            idx_all = idx_all[idx_all < len(train_blocks)]
            fallback = feats[i].subject_mean.copy()
            if len(idx_all) == 0:
                out.append(fallback)
                continue
            target = feats[i]
            d = []
            for k in idx_all:
                fk = feats[k]
                len_pen = abs(fk.length - target.length) / 16.0
                dow_pen = circular_day_distance(target.start_day, fk.start_day, cfg.period) / max(cfg.period / 2.0, 1.0)
                edge_pen = 0.0
                ok_prev = np.isfinite(target.prev) & np.isfinite(fk.prev)
                ok_next = np.isfinite(target.next) & np.isfinite(fk.next)
                if ok_prev.any():
                    edge_pen += float(np.mean(np.abs(target.prev[ok_prev] - fk.prev[ok_prev])))
                if ok_next.any():
                    edge_pen += float(np.mean(np.abs(target.next[ok_next] - fk.next[ok_next])))
                d.append(len_pen + dow_pen + 0.25 * edge_pen)
            order = np.argsort(np.asarray(d))[: min(cfg.k, len(idx_all))]
            chosen = idx_all[order]
            raw_w = 1.0 / np.maximum(np.asarray(d)[order], 1e-3)
            w = raw_w / raw_w.sum()
            local = w @ train_rates[chosen]
            sim_mass = float(min(len(chosen), cfg.k))
            out.append(clip((sim_mass * local + cfg.shrink * fallback) / (sim_mass + cfg.shrink)))
        return np.vstack(out)

    parts = method.split("_")
    cfg = MotifConfig(
        mode=parts[1],
        radius=int(parts[2].removeprefix("r")),
        k=int(parts[3].removeprefix("k")),
        tau=float(parts[4].removeprefix("tau").replace("p", ".")),
        shrink=float(parts[5].removeprefix("s").replace("p", ".")),
    )
    train_feats = build_features(rows, y, train_blocks, known, cfg.radius)
    hidden_feats = [motif_feature(rows, y, block, known, cfg.radius) for block in hidden_blocks]
    blocks = train_blocks + hidden_blocks
    feats = train_feats + hidden_feats
    rates = np.vstack([train_rates, np.full((len(hidden_blocks), len(TARGETS)), np.nan)])
    out = []
    for h in range(len(hidden_blocks)):
        i = len(train_blocks) + h
        idx_all = donor_indices(blocks, i, cfg)
        idx_all = idx_all[idx_all < len(train_blocks)]
        fallback = feats[i].subject_mean.copy()
        pred = fallback.copy()
        for j in range(len(TARGETS)):
            if len(idx_all) == 0:
                continue
            x_d = np.vstack([feats[k].vec_by_target[j] for k in idx_all]).astype(np.float64)
            x_i = feats[i].vec_by_target[j].astype(np.float64)
            mu = x_d.mean(axis=0)
            sd = x_d.std(axis=0)
            sd = np.where(sd < 1e-6, 1.0, sd)
            z_d = (x_d - mu) / sd
            z_i = (x_i - mu) / sd
            dist = np.sqrt(np.maximum(np.mean((z_d - z_i) ** 2, axis=1), 0.0))
            order = np.argsort(dist)[: min(cfg.k, len(idx_all))]
            chosen = idx_all[order]
            raw_w = np.exp(-dist[order] / max(cfg.tau, 1e-6))
            if raw_w.sum() <= 1e-12:
                raw_w = 1.0 / np.maximum(dist[order], 1e-3)
            sim_mass = float(np.clip(raw_w.mean(), 0.05, 1.0) * len(chosen))
            w = raw_w / raw_w.sum()
            local = float(np.dot(w, train_rates[chosen, j]))
            pred[j] = (sim_mass * local + cfg.shrink * fallback[j]) / (sim_mass + cfg.shrink)
        out.append(clip(pred))
    return np.vstack(out)


def write_report(summary: pd.DataFrame, target_detail: pd.DataFrame, hidden_rates: pd.DataFrame, proxy: pd.DataFrame) -> None:
    lines = [
        "# Hidden Block Sequence Motif Audit",
        "",
        "This audit tests whether train-submission sequence correspondence exists at block-rate level.",
        "It uses label flanks, endpoint motif, date phase, weekday, and hidden block length; raw sensor/PCA features are intentionally excluded.",
        "",
        "## Best methods",
        "",
        "```csv",
        summary.head(30).round(8).to_csv(index=False).strip(),
        "```",
        "",
        "## Target detail for best methods",
        "",
        "```csv",
        target_detail[target_detail["method"].isin(summary.head(10)["method"])].round(8).to_csv(index=False).strip(),
        "```",
        "",
        "## Hidden block rates from selected methods",
        "",
        "```csv",
        hidden_rates.head(60).round(6).to_csv(index=False).strip(),
        "```",
    ]
    if not proxy.empty:
        lines.extend(
            [
                "",
                "## Public proxy for generated motif candidates",
                "",
                "```csv",
                proxy.round(10).to_csv(index=False).strip(),
                "```",
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Same-subject motif winning only locally is useful for hidden submission because the hidden blocks are within the same subjects, but it is not a general model improvement.",
            "- Strict-subject motif is a sanity check. If strict is flat but same-subject improves, the signal is subject-sequence specific.",
            "- A candidate is useful only if the motif move stays compatible with raw05/stage2 public axes; pseudo-hidden improvement alone is insufficient.",
        ]
    )
    (OUT / "hidden_block_sequence_motif_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train, sample = hbr.read_data()
    rows = hbr.all_rows(train, sample)
    y = hbr.train_label_matrix(rows, train)
    pseudo_blocks = hbr.make_pseudo_blocks(rows)
    hidden_blocks = hbr.make_hidden_blocks(rows)

    summary, target_detail, _preds = evaluate_motif_methods(rows, y, pseudo_blocks)
    summary.to_csv(OUT / "hidden_block_sequence_motif_summary.csv", index=False)
    target_detail.to_csv(OUT / "hidden_block_sequence_motif_target_detail.csv", index=False)

    # Select only methods that show real pseudo-hidden signal. Keep target masks
    # per method so a strong Q motif does not force a bad S move.
    selected = summary[
        (~summary["method"].isin(["subject_mean", "global_mean"]))
        & (summary["delta_vs_subject_mean"] < -0.0010)
    ].head(6)["method"].tolist()
    if not selected:
        selected = summary[~summary["method"].isin(["subject_mean", "global_mean"])].head(3)["method"].tolist()

    hidden_rows = []
    saved: list[str] = []
    for method in selected:
        hidden_rate = hidden_prediction_for_method(method, rows, y, pseudo_blocks, hidden_blocks)
        for i, block in enumerate(hidden_blocks):
            rec = {
                "method": method,
                "hidden_block_id": block.block_id,
                "subject_id": block.subject_id,
                "n_rows": block.n,
                "start": block.start.date().isoformat(),
                "end": block.end.date().isoformat(),
            }
            for j, target in enumerate(TARGETS):
                rec[f"rate_{target}"] = hidden_rate[i, j]
                rec[f"count_{target}"] = hidden_rate[i, j] * block.n
            hidden_rows.append(rec)

        td = target_detail[target_detail["method"].eq(method)].set_index("target").reindex(TARGETS)
        keep = td["target_delta_vs_subject_mean"].to_numpy(dtype=float) < -0.001
        if keep.any():
            for base in [hbr.RAW05_SUB, hbr.PARETO_SUB]:
                if not base.exists():
                    continue
                for weight in [0.03, 0.05, 0.10]:
                    saved.append(hbr.save_rate_candidate(base, sample, hidden_blocks, rows, hidden_rate, method, weight, keep))

    hidden_df = pd.DataFrame(hidden_rows)
    hidden_df.to_csv(OUT / "hidden_block_sequence_motif_hidden_rates.csv", index=False)
    proxy = hbr.public_proxy_scores(saved) if saved else pd.DataFrame()
    if not proxy.empty:
        proxy.to_csv(OUT / "hidden_block_sequence_motif_candidate_proxy.csv", index=False)

    write_report(summary, target_detail, hidden_df, proxy)
    print("[sequence motif] pseudo blocks", len(pseudo_blocks), "hidden blocks", len(hidden_blocks))
    print(summary.head(25).round(8).to_string(index=False))
    print("\n[target detail: best 8]")
    print(target_detail[target_detail["method"].isin(summary.head(8)["method"])].round(8).to_string(index=False))
    if not proxy.empty:
        print("\n[public proxy candidates]")
        print(proxy.head(20).round(10).to_string(index=False))


if __name__ == "__main__":
    main()
