from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

from train_pruned_state_decoder import EPS, KEY_COLUMNS, TARGET_COLUMNS, average_log_loss, drift_vs_reference, safe_logit, sigmoid, subject_prior, write_prediction
from train_s2_sleep_retrieval_encoder import dataframe_to_markdown, make_subject_time_folds, normalize_keys


SCALES = [0.25, 0.50, 0.75, 1.00, 1.25]
CAPS = [0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.50]
GATE_MODES = ["all", "agreement_with_prior", "top_abs_50", "top_abs_35", "signed_margin"]


def read_oof(path: Path) -> pd.DataFrame:
    df = normalize_keys(pd.read_csv(path))
    pred_cols = [f"pred_{target}" for target in TARGET_COLUMNS]
    missing = [col for col in pred_cols if col not in df.columns]
    if missing:
        raise ValueError(f"{path} missing {missing}")
    return df[KEY_COLUMNS + pred_cols]


def read_submission(path: Path) -> pd.DataFrame:
    df = normalize_keys(pd.read_csv(path))
    missing = [target for target in TARGET_COLUMNS if target not in df.columns]
    if missing:
        raise ValueError(f"{path} missing {missing}")
    return df[KEY_COLUMNS + TARGET_COLUMNS]


def align_oof(train: pd.DataFrame, pred: pd.DataFrame) -> np.ndarray:
    merged = train[KEY_COLUMNS].merge(pred, on=KEY_COLUMNS, how="left", validate="one_to_one")
    cols = [f"pred_{target}" for target in TARGET_COLUMNS]
    if merged[cols].isna().any().any():
        raise ValueError("OOF join failed")
    return np.clip(merged[cols].to_numpy(float), EPS, 1.0 - EPS)


def align_submission(sample: pd.DataFrame, pred: pd.DataFrame) -> np.ndarray:
    merged = sample[KEY_COLUMNS].merge(pred, on=KEY_COLUMNS, how="left", validate="one_to_one")
    if merged[TARGET_COLUMNS].isna().any().any():
        raise ValueError("submission join failed")
    return np.clip(merged[TARGET_COLUMNS].to_numpy(float), EPS, 1.0 - EPS)


def fold_safe_prior(train: pd.DataFrame, sample: pd.DataFrame, folds: int, alpha: float) -> tuple[np.ndarray, np.ndarray]:
    train_prior = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    sample_parts = []
    for fold in make_subject_time_folds(train, folds):
        train_prior[fold.val_idx] = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.val_idx], alpha)
        sample_parts.append(subject_prior(train.iloc[fold.train_idx], sample, alpha))
    return np.clip(train_prior, EPS, 1.0 - EPS), np.clip(np.mean(np.stack(sample_parts, axis=0), axis=0), EPS, 1.0 - EPS)


def residual_gate(
    stable: np.ndarray,
    extended: np.ndarray,
    prior: np.ndarray,
    scale: float,
    cap: float,
    mode: str,
    thresholds: np.ndarray | None = None,
) -> np.ndarray:
    stable_l = safe_logit(stable)
    ext_l = safe_logit(extended)
    prior_l = safe_logit(prior)
    residual = ext_l - stable_l
    clipped = np.clip(residual, -cap, cap) * scale
    gate = np.ones_like(clipped)
    if mode == "agreement_with_prior":
        gate = (np.sign(ext_l - prior_l) == np.sign(stable_l - prior_l)).astype(float)
    elif mode in {"top_abs_50", "top_abs_35"}:
        if thresholds is None:
            pct = 50 if mode == "top_abs_50" else 65
            thresholds = np.percentile(np.abs(residual), pct, axis=0)
        gate = (np.abs(residual) >= thresholds.reshape(1, -1)).astype(float)
    elif mode == "signed_margin":
        gate = (np.abs(ext_l - prior_l) > np.abs(stable_l - prior_l)).astype(float)
    elif mode != "all":
        raise ValueError(mode)
    return np.clip(sigmoid(stable_l + gate * clipped), EPS, 1.0 - EPS)


def targetwise_select(y_df: pd.DataFrame, oof_by_source: dict[str, np.ndarray], sample_by_source: dict[str, np.ndarray]) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    rows = []
    out_oof = np.zeros((len(y_df), len(TARGET_COLUMNS)), dtype=float)
    out_sample = np.zeros((next(iter(sample_by_source.values())).shape[0], len(TARGET_COLUMNS)), dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        best = None
        for name, pred in oof_by_source.items():
            loss = float(log_loss(y_df[target].to_numpy(int), np.clip(pred[:, target_i], EPS, 1.0 - EPS), labels=[0, 1]))
            if best is None or loss < best["log_loss"]:
                best = {"target": target, "source": name, "log_loss": loss}
        if best is None:
            raise RuntimeError(target)
        rows.append(best)
        out_oof[:, target_i] = oof_by_source[best["source"]][:, target_i]
        out_sample[:, target_i] = sample_by_source[best["source"]][:, target_i]
    avg, _ = average_log_loss(y_df, out_oof)
    selected = pd.DataFrame(rows)
    selected["targetwise_avg_log_loss"] = avg
    return selected, np.clip(out_oof, EPS, 1.0 - EPS), np.clip(out_sample, EPS, 1.0 - EPS)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    y_df = train[TARGET_COLUMNS].astype(int)

    stable_oof = align_oof(train, read_oof(Path(args.stable_oof)))
    stable_sample = align_submission(sample, read_submission(Path(args.stable_submission)))
    extended_oof = align_oof(train, read_oof(Path(args.extended_oof)))
    extended_sample = align_submission(sample, read_submission(Path(args.extended_submission)))
    prior_oof, prior_sample = fold_safe_prior(train, sample, args.folds, args.subject_alpha)

    oof_by_source = {
        "stable_signal_s4_temporal": stable_oof,
        "extended_full_oof_winners": extended_oof,
    }
    sample_by_source = {
        "stable_signal_s4_temporal": stable_sample,
        "extended_full_oof_winners": extended_sample,
    }
    score_rows = []
    for name, pred in oof_by_source.items():
        avg, per_target = average_log_loss(y_df, pred)
        score_rows.append({"source": name, "mode": "reference", "scale": np.nan, "cap": np.nan, "avg_log_loss": avg, **per_target})

    train_residual = safe_logit(extended_oof) - safe_logit(stable_oof)
    for mode in GATE_MODES:
        for scale in SCALES:
            for cap in CAPS:
                thresholds = None
                if mode in {"top_abs_50", "top_abs_35"}:
                    pct = 50 if mode == "top_abs_50" else 65
                    thresholds = np.percentile(np.abs(train_residual), pct, axis=0)
                source = f"capgate_{mode}_s{int(scale * 100):03d}_c{int(cap * 100):03d}"
                oof = residual_gate(stable_oof, extended_oof, prior_oof, scale, cap, mode, thresholds)
                sample_pred = residual_gate(stable_sample, extended_sample, prior_sample, scale, cap, mode, thresholds)
                avg, per_target = average_log_loss(y_df, oof)
                oof_by_source[source] = oof
                sample_by_source[source] = sample_pred
                score_rows.append({"source": source, "mode": mode, "scale": scale, "cap": cap, "avg_log_loss": avg, **per_target})

    score_df = pd.DataFrame(score_rows).sort_values("avg_log_loss")
    selected, tw_oof, tw_sample = targetwise_select(y_df, oof_by_source, sample_by_source)
    best_name = str(score_df.iloc[0]["source"])
    best_oof = oof_by_source[best_name]
    best_sample = sample_by_source[best_name]
    best_avg, best_targets = average_log_loss(y_df, best_oof)
    tw_avg, tw_targets = average_log_loss(y_df, tw_oof)
    diagnostics = {
        "best_global_key": best_name,
        "best_global": {"avg_log_loss": best_avg, **best_targets},
        "targetwise": {"avg_log_loss": tw_avg, **tw_targets},
        "targetwise_selection": selected.to_dict(orient="records"),
        "drift_vs_reference_best_global": drift_vs_reference(sample, best_sample, Path(args.reference_submission) if args.reference_submission else None),
        "drift_vs_reference_targetwise": drift_vs_reference(sample, tw_sample, Path(args.reference_submission) if args.reference_submission else None),
        "args": vars(args),
    }

    score_df.to_csv(output_dir / "residual_cap_gate_scores.csv", index=False)
    selected.to_csv(output_dir / "targetwise_selection.csv", index=False)
    write_prediction(output_dir / "oof_residual_cap_gate_best_global.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_residual_cap_gate_best_global.csv", sample, best_sample, oof=False)
    write_prediction(output_dir / "oof_residual_cap_gate_targetwise.csv", train, tw_oof, oof=True)
    write_prediction(output_dir / "submission_residual_cap_gate_targetwise.csv", sample, tw_sample, oof=False)
    (output_dir / "report.json").write_text(json.dumps({"diagnostics": diagnostics, "scores": score_df.head(120).to_dict(orient="records")}, indent=2), encoding="utf-8")
    lines = [
        "# Residual Cap-Gate Decoder",
        "",
        "This experiment uses the stable fixed scaffold as the coordinate system, then injects only a capped/gated logit residual from the extended full-OOF winner map. The goal is to test whether the optimistic extended residual contains a bounded signal that survives without letting large target/panel drift dominate.",
        "",
        "## Best Sources",
        "",
        dataframe_to_markdown(score_df.head(40)),
        "",
        "## Target-wise Selection",
        "",
        dataframe_to_markdown(selected),
        "",
        "## Summary",
        "",
        f"- Best global: `{best_name}` avg `{best_avg:.6f}`",
        f"- Target-wise avg: `{tw_avg:.6f}`",
        f"- Best global drift vs reference: `{diagnostics['drift_vs_reference_best_global'].get('mean_abs_drift', float('nan')):.6f}`",
        f"- Target-wise drift vs reference: `{diagnostics['drift_vs_reference_targetwise'].get('mean_abs_drift', float('nan')):.6f}`",
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"best_global={best_name} avg={best_avg:.6f}")
    print(f"targetwise avg={tw_avg:.6f}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capped/gated residual decoder between stable and extended independent maps.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/residual_cap_gate_decoder_v1")
    parser.add_argument("--stable-oof", default="outputs/stable_extended_consensus_decoder_v1/oof_stable_signal_s4_temporal.csv")
    parser.add_argument("--stable-submission", default="outputs/stable_extended_consensus_decoder_v1/submission_stable_signal_s4_temporal.csv")
    parser.add_argument("--extended-oof", default="outputs/stable_extended_consensus_decoder_v1/oof_extended_full_oof_winners.csv")
    parser.add_argument("--extended-submission", default="outputs/stable_extended_consensus_decoder_v1/submission_extended_full_oof_winners.csv")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--subject-alpha", type=float, default=10.0)
    return parser.parse_args()


if __name__ == "__main__":
    main()
