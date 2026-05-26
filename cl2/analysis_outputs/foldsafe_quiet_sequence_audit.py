from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import current_0p586_gentle_logit_calibration as glc
import current_0p588_subject_relative_q_postprocess as srq
import quiet_feature_logit_postprocess_probe as qlp


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def stage_rows(name: str, y: np.ndarray, before: np.ndarray, after: np.ndarray, sources: dict[str, str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for j, target in enumerate(TARGETS):
        base_loss = loss_col(y[:, j], before[:, j])
        cand_loss = loss_col(y[:, j], after[:, j])
        rows.append(
            {
                "stage": name,
                "target": target,
                "before_loss": base_loss,
                "after_loss": cand_loss,
                "delta": cand_loss - base_loss,
                "source": sources.get(target, "unchanged"),
            }
        )
    rows.append(
        {
            "stage": name,
            "target": "mean",
            "before_loss": mean_loss(y, before),
            "after_loss": mean_loss(y, after),
            "delta": mean_loss(y, after) - mean_loss(y, before),
            "source": "target_mean",
        }
    )
    return rows


def apply_foldsafe_quiet(train: pd.DataFrame, base: np.ndarray, selected_path: Path, targets: list[str]) -> tuple[np.ndarray, dict[str, str]]:
    selected = pd.read_csv(selected_path)
    selected = selected[selected["target"].isin(targets)].sort_values(["target", "delta_vs_base"])
    selected = selected.groupby("target", as_index=False).head(1)
    out = base.copy()
    sources: dict[str, str] = {}
    for row in selected.itertuples(index=False):
        target = str(row.target)
        j = TARGETS.index(target)
        corrected = qlp.oof_corrected(train, out, target, str(row.feature), float(row.c_value))
        out[:, j] = clip((1.0 - float(row.best_weight)) * out[:, j] + float(row.best_weight) * corrected)
        sources[target] = f"{row.feature}|C={row.c_value}|w={row.best_weight}"
    return out, sources


def apply_ops(train: pd.DataFrame, base: np.ndarray, ops_path: Path) -> tuple[np.ndarray, dict[str, str]]:
    ops = pd.read_csv(ops_path)
    out = base.copy()
    sources: dict[str, str] = {}
    for row in ops.itertuples(index=False):
        kind = str(row.kind)
        target = str(row.target)
        config = str(row.config)
        j = TARGETS.index(target)
        if kind == "logit":
            out[:, j] = glc.calibrate(out[:, j], glc.parse_config(config))
        elif kind == "subject":
            out[:, j] = srq.subject_relative(train, out[:, j], srq.parse_config(config))
        else:
            raise ValueError(kind)
        sources[target] = f"{kind}_{config}"
    return clip(out), sources


def main() -> None:
    train_raw = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    quiet = pd.read_parquet(OUT / "quiet_window_residual_features.parquet")
    train = train_raw.merge(quiet, on=KEY, how="left")
    y = train[TARGETS].to_numpy(dtype=int)
    base = clip(np.load(OUT / "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy"))
    rows: list[dict[str, object]] = []

    quiet_oof, sources = apply_foldsafe_quiet(
        train,
        base,
        OUT / "current_0p578_quiet_logit_selected.csv",
        ["Q3", "S2", "S3", "S4"],
    )
    rows.extend(stage_rows("foldsafe_quiet_q3_s2_s3_s4", y, base, quiet_oof, sources))
    np.save(OUT / "final_hybrid_0p575_quiet_logit_q3_s2_s3_s4_foldsafe_oof.npy", quiet_oof)

    gentle_oof, sources = apply_ops(train_raw, quiet_oof, OUT / "quiet_logit_then_gentle_loose_ops.csv")
    rows.extend(stage_rows("foldsafe_quiet_then_gentle_loose", y, quiet_oof, gentle_oof, sources))
    np.save(OUT / "final_hybrid_0p575_quiet_logit_then_gentle_loose_foldsafe_oof.npy", gentle_oof)

    second_oof, sources = apply_ops(train_raw, gentle_oof, OUT / "quiet_logit_then_second_loose_ops.csv")
    rows.extend(stage_rows("foldsafe_quiet_then_second_loose", y, gentle_oof, second_oof, sources))
    np.save(OUT / "final_hybrid_0p575_quiet_logit_then_second_loose_foldsafe_oof.npy", second_oof)

    out = pd.DataFrame(rows)
    out.to_csv(OUT / "foldsafe_quiet_sequence_audit.csv", index=False)
    print(out.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
