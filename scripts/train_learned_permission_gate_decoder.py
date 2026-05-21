from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from train_fixed_permission_policy_decoder import POLICIES, apply_policy, fold_safe_prior
from train_pruned_state_decoder import EPS, TARGET_COLUMNS, average_log_loss, drift_vs_reference, safe_logit, sigmoid, write_prediction
from train_residual_cap_gate_decoder import align_oof, align_submission, read_oof, read_submission
from train_s2_sleep_retrieval_encoder import SEED, dataframe_to_markdown, make_subject_time_folds, normalize_keys


VARIANTS = [
    "stack_logreg",
    "stack_hgb",
    "residual_ridge_c030",
    "residual_hgb_c030",
    "residual_hgb_c050",
    "gate_hgb_ext",
    "gate_logreg_ext",
    "gate_hgb_fixed",
]


def panel_features(keys: pd.DataFrame) -> np.ndarray:
    ordered = keys.reset_index(drop=True).copy()
    ordered["_row"] = np.arange(len(ordered))
    ordered["_pos"] = ordered.groupby("subject_id")["_row"].rank(method="first", pct=True)
    pos = ordered["_pos"].to_numpy(float)
    return np.column_stack(
        [
            pos,
            (pos <= 1 / 3).astype(float),
            ((pos > 1 / 3) & (pos <= 2 / 3)).astype(float),
            (pos > 2 / 3).astype(float),
        ]
    )


def target_meta_features(
    stable: np.ndarray,
    extended: np.ndarray,
    fixed: np.ndarray,
    prior: np.ndarray,
    panel: np.ndarray,
    target_i: int,
) -> np.ndarray:
    s = np.clip(stable[:, target_i], EPS, 1.0 - EPS)
    e = np.clip(extended[:, target_i], EPS, 1.0 - EPS)
    f = np.clip(fixed[:, target_i], EPS, 1.0 - EPS)
    p = np.clip(prior[:, target_i], EPS, 1.0 - EPS)
    sl = safe_logit(s)
    el = safe_logit(e)
    fl = safe_logit(f)
    pl = safe_logit(p)
    er = el - sl
    fr = fl - sl
    return np.column_stack(
        [
            s,
            e,
            f,
            p,
            sl,
            el,
            fl,
            pl,
            er,
            np.abs(er),
            fr,
            np.abs(fr),
            el - pl,
            sl - pl,
            fl - pl,
            (np.abs(el - pl) > np.abs(sl - pl)).astype(float),
            (np.sign(el - pl) == np.sign(sl - pl)).astype(float),
            (np.abs(fl - pl) > np.abs(sl - pl)).astype(float),
            *[panel[:, i] for i in range(panel.shape[1])],
        ]
    )


def row_log_loss(y: np.ndarray, pred: np.ndarray) -> np.ndarray:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y * np.log(pred) + (1 - y) * np.log(1 - pred))


def fit_predict_variant(
    variant: str,
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    stable_fit: np.ndarray,
    stable_eval: np.ndarray,
    stable_sample: np.ndarray,
    extended_fit: np.ndarray,
    extended_eval: np.ndarray,
    extended_sample: np.ndarray,
    fixed_fit: np.ndarray,
    fixed_eval: np.ndarray,
    fixed_sample: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    if len(np.unique(y_fit)) < 2:
        value = float(np.mean(y_fit))
        return np.full(len(x_eval), value), np.full(len(x_sample), value)
    if variant == "stack_logreg":
        model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(C=0.05, max_iter=5000, random_state=SEED))
        model.fit(x_fit, y_fit)
        return model.predict_proba(x_eval)[:, 1], model.predict_proba(x_sample)[:, 1]
    if variant == "stack_hgb":
        model = make_pipeline(
            SimpleImputer(strategy="median"),
            HistGradientBoostingClassifier(max_iter=60, learning_rate=0.035, max_leaf_nodes=5, min_samples_leaf=24, l2_regularization=0.25, random_state=SEED),
        )
        model.fit(x_fit, y_fit)
        return model.predict_proba(x_eval)[:, 1], model.predict_proba(x_sample)[:, 1]
    if variant.startswith("residual_"):
        cap = 0.30 if variant.endswith("c030") else 0.50
        residual = safe_logit((y_fit * 0.98) + 0.01) - safe_logit(stable_fit)
        if variant.startswith("residual_ridge"):
            model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=80.0))
        else:
            model = make_pipeline(
                SimpleImputer(strategy="median"),
                HistGradientBoostingRegressor(max_iter=50, learning_rate=0.03, max_leaf_nodes=5, min_samples_leaf=24, l2_regularization=0.35, random_state=SEED),
            )
        model.fit(x_fit, residual)
        eval_delta = np.clip(model.predict(x_eval), -cap, cap)
        sample_delta = np.clip(model.predict(x_sample), -cap, cap)
        return sigmoid(safe_logit(stable_eval) + eval_delta), sigmoid(safe_logit(stable_sample) + sample_delta)
    if variant in {"gate_hgb_ext", "gate_logreg_ext", "gate_hgb_fixed"}:
        alt_fit = fixed_fit if variant == "gate_hgb_fixed" else extended_fit
        alt_eval = fixed_eval if variant == "gate_hgb_fixed" else extended_eval
        alt_sample = fixed_sample if variant == "gate_hgb_fixed" else extended_sample
        better_alt = (row_log_loss(y_fit, alt_fit) < row_log_loss(y_fit, stable_fit)).astype(int)
        if len(np.unique(better_alt)) < 2:
            gate_eval = np.full(len(x_eval), float(np.mean(better_alt)))
            gate_sample = np.full(len(x_sample), float(np.mean(better_alt)))
        elif variant == "gate_logreg_ext":
            model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(C=0.03, max_iter=5000, random_state=SEED))
            model.fit(x_fit, better_alt)
            gate_eval = model.predict_proba(x_eval)[:, 1]
            gate_sample = model.predict_proba(x_sample)[:, 1]
        else:
            model = make_pipeline(
                SimpleImputer(strategy="median"),
                HistGradientBoostingClassifier(max_iter=45, learning_rate=0.03, max_leaf_nodes=5, min_samples_leaf=28, l2_regularization=0.4, random_state=SEED),
            )
            model.fit(x_fit, better_alt)
            gate_eval = model.predict_proba(x_eval)[:, 1]
            gate_sample = model.predict_proba(x_sample)[:, 1]
        eval_pred = sigmoid((1.0 - gate_eval) * safe_logit(stable_eval) + gate_eval * safe_logit(alt_eval))
        sample_pred = sigmoid((1.0 - gate_sample) * safe_logit(stable_sample) + gate_sample * safe_logit(alt_sample))
        return eval_pred, sample_pred
    raise ValueError(variant)


def run_nested(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    stable_oof: np.ndarray,
    stable_sample: np.ndarray,
    extended_oof: np.ndarray,
    extended_sample: np.ndarray,
    fixed_oof: np.ndarray,
    fixed_sample: np.ndarray,
    prior_oof: np.ndarray,
    prior_sample: np.ndarray,
    args: argparse.Namespace,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], list[dict]]:
    folds = make_subject_time_folds(train, args.folds)
    train_panel = panel_features(train)
    sample_panel = panel_features(sample)
    oof = {variant: np.zeros_like(stable_oof) for variant in VARIANTS}
    sample_parts = {variant: [] for variant in VARIANTS}
    fold_rows = []
    y_df = train[TARGET_COLUMNS].astype(int)
    for fold_i, fold in enumerate(folds):
        fold_sample = {variant: np.zeros_like(stable_sample) for variant in VARIANTS}
        for target_i, target in enumerate(TARGET_COLUMNS):
            x_all = target_meta_features(stable_oof, extended_oof, fixed_oof, prior_oof, train_panel, target_i)
            x_sample = target_meta_features(stable_sample, extended_sample, fixed_sample, prior_sample, sample_panel, target_i)
            y_fit = y_df.iloc[fold.train_idx][target].to_numpy(int)
            for variant in VARIANTS:
                val_pred, sample_pred = fit_predict_variant(
                    variant,
                    x_all[fold.train_idx],
                    y_fit,
                    x_all[fold.val_idx],
                    x_sample,
                    stable_oof[fold.train_idx, target_i],
                    stable_oof[fold.val_idx, target_i],
                    stable_sample[:, target_i],
                    extended_oof[fold.train_idx, target_i],
                    extended_oof[fold.val_idx, target_i],
                    extended_sample[:, target_i],
                    fixed_oof[fold.train_idx, target_i],
                    fixed_oof[fold.val_idx, target_i],
                    fixed_sample[:, target_i],
                )
                oof[variant][fold.val_idx, target_i] = np.clip(val_pred, EPS, 1.0 - EPS)
                fold_sample[variant][:, target_i] = np.clip(sample_pred, EPS, 1.0 - EPS)
        for variant in VARIANTS:
            sample_parts[variant].append(fold_sample[variant])
        fold_rows.append({"fold": fold_i, "fit_rows": len(fold.train_idx), "val_rows": len(fold.val_idx)})
    sample_pred = {variant: np.mean(np.stack(parts, axis=0), axis=0) for variant, parts in sample_parts.items()}
    return oof, sample_pred, fold_rows


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
    fixed_oof = apply_policy(POLICIES["q1s3_signed_s1s2s4_extended_q3_stable"], stable_oof, extended_oof, prior_oof)
    fixed_sample = apply_policy(POLICIES["q1s3_signed_s1s2s4_extended_q3_stable"], stable_sample, extended_sample, prior_sample)

    learned_oof, learned_sample, fold_rows = run_nested(
        train,
        sample,
        stable_oof,
        stable_sample,
        extended_oof,
        extended_sample,
        fixed_oof,
        fixed_sample,
        prior_oof,
        prior_sample,
        args,
    )
    sources = {
        "stable_signal_s4_temporal": (stable_oof, stable_sample),
        "extended_full_oof_winners": (extended_oof, extended_sample),
        "fixed_permission_policy": (fixed_oof, fixed_sample),
        **{f"learned_{name}": (oof, learned_sample[name]) for name, oof in learned_oof.items()},
    }
    rows = []
    for name, (oof, submission) in sources.items():
        avg, per_target = average_log_loss(y_df, oof)
        drift = drift_vs_reference(sample, submission, Path(args.reference_submission) if args.reference_submission else None)
        rows.append({"source": name, "avg_log_loss": avg, **per_target, "drift_vs_reference": drift.get("mean_abs_drift"), "corr_vs_reference": drift.get("corr")})
        write_prediction(output_dir / f"oof_{name}.csv", train, oof, oof=True)
        write_prediction(output_dir / f"submission_{name}.csv", sample, submission, oof=False)
    score_df = pd.DataFrame(rows).sort_values("avg_log_loss")
    pd.DataFrame(fold_rows).to_csv(output_dir / "folds.csv", index=False)
    score_df.to_csv(output_dir / "learned_permission_gate_scores.csv", index=False)
    report = {"scores": score_df.to_dict(orient="records"), "variants": VARIANTS, "args": vars(args)}
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Learned Permission Gate Decoder",
        "",
        "This experiment replaces fixed target permission rules with nested row-level meta decoders. The models use only independent branch predictions (stable, extended, fixed policy), fold-safe subject prior, signed-margin features, and panel position; v83 is used only as a drift diagnostic.",
        "",
        "## Scores",
        "",
        dataframe_to_markdown(score_df),
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(score_df.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Nested learned row-level permission gate decoder.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/learned_permission_gate_decoder_v1")
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
