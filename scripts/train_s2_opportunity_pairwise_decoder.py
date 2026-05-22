from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler

from probe_domain_ssl_latents import (
    EPS,
    KEY_COLUMNS,
    TARGET_COLUMNS,
    dataframe_to_markdown,
    feature_views,
    load_latent_table,
    make_subject_time_folds,
    normalize_keys,
    subject_prior,
    write_prediction,
)
from train_pruned_state_decoder import fit_prototype_label, fit_rank_pairwise, safe_logit, sigmoid
from train_s2_opportunity_state_decoder import FIXED_MAP_TARGET_LOSSES, DEFAULT_LATENTS, projected_fixed_avg, s2_reference_drift


@dataclass(frozen=True)
class PairwiseSpec:
    latent: str
    view: str
    decoder: str
    blend: float
    c_value: float = 0.03

    @property
    def name(self) -> str:
        if self.decoder == "logreg":
            c_part = f"c{str(self.c_value).replace('.', 'p')}"
            return f"{self.latent}__{self.view}__{self.decoder}_{c_part}__b{int(self.blend * 100):02d}"
        return f"{self.latent}__{self.view}__{self.decoder}__b{int(self.blend * 100):02d}"


def build_specs() -> list[PairwiseSpec]:
    specs: list[PairwiseSpec] = []
    for latent, views in {
        "psg_opp": ["deviation", "absolute_plus_deviation"],
        "psg_opp_mob": ["deviation"],
        "psg_qrel": ["absolute"],
    }.items():
        for view in views:
            for blend in [0.10, 0.20, 0.35]:
                specs.append(PairwiseSpec(latent, view, "rank_pairwise", blend))
            for blend in [0.10]:
                specs.append(PairwiseSpec(latent, view, "prototype", blend))
            for c_value in [0.03, 0.10]:
                specs.append(PairwiseSpec(latent, view, "logreg", 0.20, c_value))
    return specs


def preprocess(x_fit: np.ndarray, x_eval: np.ndarray, x_sample: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    fit = scaler.fit_transform(imputer.fit_transform(x_fit))
    eval_part = scaler.transform(imputer.transform(x_eval))
    sample = scaler.transform(imputer.transform(x_sample))
    return fit, eval_part, sample


def fit_logreg(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    c_value: float,
) -> tuple[np.ndarray, np.ndarray]:
    if len(np.unique(y_fit)) < 2:
        value = float(np.mean(y_fit))
        return np.full(len(x_eval), value), np.full(len(x_sample), value)
    model = LogisticRegression(C=c_value, solver="lbfgs", max_iter=4000, random_state=13)
    model.fit(x_fit, y_fit.astype(int))
    return model.predict_proba(x_eval)[:, 1], model.predict_proba(x_sample)[:, 1]


def fit_residual_ridge(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    prior_fit: np.ndarray,
    prior_eval: np.ndarray,
    prior_sample: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    if len(np.unique(y_fit)) < 2:
        return prior_eval, prior_sample
    residual = safe_logit(y_fit * 0.98 + 0.01) - safe_logit(prior_fit)
    model = Ridge(alpha=75.0)
    model.fit(x_fit, residual)
    return sigmoid(safe_logit(prior_eval) + model.predict(x_eval)), sigmoid(safe_logit(prior_sample) + model.predict(x_sample))


def predict_spec(
    spec: PairwiseSpec,
    latent_tables: dict[str, tuple[pd.DataFrame, pd.DataFrame, list[str]]],
    train: pd.DataFrame,
    sample: pd.DataFrame,
    fit_idx: np.ndarray,
    eval_idx: np.ndarray,
    args: argparse.Namespace,
) -> tuple[np.ndarray, np.ndarray]:
    train_x, sample_x, z_cols = latent_tables[spec.latent]
    x_fit, x_eval, x_sample = feature_views(train_x, sample_x, z_cols, fit_idx, eval_idx)[spec.view]
    x_fit_s, x_eval_s, x_sample_s = preprocess(x_fit, x_eval, x_sample)
    fit_frame = train.iloc[fit_idx]
    eval_frame = train.iloc[eval_idx]
    y_fit = fit_frame["S2"].to_numpy(int)
    prior_fit = subject_prior(fit_frame, fit_frame, args.prior_alpha)[:, TARGET_COLUMNS.index("S2")]
    prior_eval = subject_prior(fit_frame, eval_frame, args.prior_alpha)[:, TARGET_COLUMNS.index("S2")]
    prior_sample = subject_prior(fit_frame, sample, args.prior_alpha)[:, TARGET_COLUMNS.index("S2")]
    if spec.decoder == "rank_pairwise":
        raw_eval, raw_sample = fit_rank_pairwise(x_fit_s, y_fit, x_eval_s, x_sample_s, args.max_pairs)
    elif spec.decoder == "prototype":
        raw_eval, raw_sample = fit_prototype_label(x_fit_s, y_fit, x_eval_s, x_sample_s, args.n_label_proto)
    elif spec.decoder == "logreg":
        raw_eval, raw_sample = fit_logreg(x_fit_s, y_fit, x_eval_s, x_sample_s, spec.c_value)
    elif spec.decoder == "residual_ridge":
        raw_eval, raw_sample = fit_residual_ridge(x_fit_s, y_fit, prior_fit, prior_eval, prior_sample, x_eval_s, x_sample_s)
    else:
        raise ValueError(spec.decoder)
    pred_eval = sigmoid((1.0 - spec.blend) * safe_logit(prior_eval) + spec.blend * safe_logit(raw_eval))
    pred_sample = sigmoid((1.0 - spec.blend) * safe_logit(prior_sample) + spec.blend * safe_logit(raw_sample))
    return np.clip(pred_eval, EPS, 1.0 - EPS), np.clip(pred_sample, EPS, 1.0 - EPS)


def select_spec_inner(
    specs: list[PairwiseSpec],
    latent_tables: dict[str, tuple[pd.DataFrame, pd.DataFrame, list[str]]],
    train: pd.DataFrame,
    sample: pd.DataFrame,
    outer_train_idx: np.ndarray,
    args: argparse.Namespace,
) -> tuple[PairwiseSpec, list[dict[str, object]]]:
    outer_train = train.iloc[outer_train_idx].reset_index(drop=True)
    inner_folds = make_subject_time_folds(outer_train, args.inner_folds)
    rows = []
    for spec in specs:
        inner_oof = np.zeros(len(outer_train_idx), dtype=float)
        for fit_local, val_local in inner_folds:
            pred, _ = predict_spec(spec, latent_tables, train, sample, outer_train_idx[fit_local], outer_train_idx[val_local], args)
            inner_oof[val_local] = pred
        loss = float(log_loss(outer_train["S2"].to_numpy(int), np.clip(inner_oof, EPS, 1.0 - EPS), labels=[0, 1]))
        rows.append({"candidate": spec.name, "inner_s2_log_loss": loss})
    best_row = min(rows, key=lambda row: row["inner_s2_log_loss"])
    return next(spec for spec in specs if spec.name == best_row["candidate"]), rows


def full_oof_scores(
    specs: list[PairwiseSpec],
    latent_tables: dict[str, tuple[pd.DataFrame, pd.DataFrame, list[str]]],
    train: pd.DataFrame,
    sample: pd.DataFrame,
    folds: list[tuple[np.ndarray, np.ndarray]],
    args: argparse.Namespace,
) -> pd.DataFrame:
    rows = []
    for spec in specs:
        oof = np.zeros(len(train), dtype=float)
        for fit_idx, eval_idx in folds:
            pred, _ = predict_spec(spec, latent_tables, train, sample, fit_idx, eval_idx, args)
            oof[eval_idx] = pred
        rows.append({"candidate": spec.name, "full_oof_s2_log_loss": float(log_loss(train["S2"].to_numpy(int), oof, labels=[0, 1]))})
    return pd.DataFrame(rows).sort_values("full_oof_s2_log_loss")


def materialize_fixed_spec(
    spec: PairwiseSpec,
    latent_tables: dict[str, tuple[pd.DataFrame, pd.DataFrame, list[str]]],
    train: pd.DataFrame,
    sample: pd.DataFrame,
    folds: list[tuple[np.ndarray, np.ndarray]],
    args: argparse.Namespace,
) -> tuple[np.ndarray, np.ndarray]:
    oof = np.zeros(len(train), dtype=float)
    sample_parts = []
    for fit_idx, eval_idx in folds:
        pred, sample_pred = predict_spec(spec, latent_tables, train, sample, fit_idx, eval_idx, args)
        oof[eval_idx] = pred
        sample_parts.append(sample_pred)
    return np.clip(oof, EPS, 1.0 - EPS), np.clip(np.mean(np.stack(sample_parts, axis=0), axis=0), EPS, 1.0 - EPS)


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    latent_tables = {name: load_latent_table(Path(path), train, sample) for name, path in DEFAULT_LATENTS.items()}
    specs = build_specs()
    folds = make_subject_time_folds(train, args.outer_folds)
    oof_s2 = np.zeros(len(train), dtype=float)
    sample_parts = []
    selection_rows = []
    inner_rows = []
    for outer_i, (fit_idx, eval_idx) in enumerate(folds, 1):
        best_spec, rows = select_spec_inner(specs, latent_tables, train, sample, fit_idx, args)
        inner_rows.extend({"outer_fold": outer_i, **row} for row in rows)
        pred, sample_pred = predict_spec(best_spec, latent_tables, train, sample, fit_idx, eval_idx, args)
        oof_s2[eval_idx] = pred
        sample_parts.append(sample_pred)
        selection_rows.append({"outer_fold": outer_i, "selected": best_spec.name})
    sample_s2 = np.mean(np.stack(sample_parts, axis=0), axis=0)
    s2_loss = float(log_loss(train["S2"].to_numpy(int), np.clip(oof_s2, EPS, 1.0 - EPS), labels=[0, 1]))
    projected_avg = projected_fixed_avg(s2_loss)
    full_scores = full_oof_scores(specs, latent_tables, train, sample, folds, args)
    fixed_best_name = str(full_scores.iloc[0]["candidate"])
    fixed_best_spec = next(spec for spec in specs if spec.name == fixed_best_name)
    fixed_best_oof_s2, fixed_best_sample_s2 = materialize_fixed_spec(fixed_best_spec, latent_tables, train, sample, folds, args)
    fixed_best_s2_loss = float(log_loss(train["S2"].to_numpy(int), fixed_best_oof_s2, labels=[0, 1]))
    fixed_best_projected_avg = projected_fixed_avg(fixed_best_s2_loss)
    stress_rows = []
    fixed_exports = {}
    for _, row in full_scores.head(args.stress_top_k).iterrows():
        name = str(row["candidate"])
        spec = next(spec for spec in specs if spec.name == name)
        cand_oof_s2, cand_sample_s2 = materialize_fixed_spec(spec, latent_tables, train, sample, folds, args)
        cand_s2_loss = float(log_loss(train["S2"].to_numpy(int), cand_oof_s2, labels=[0, 1]))
        drift = s2_reference_drift(sample, cand_sample_s2, args.reference_submission)
        stress_rows.append(
            {
                "candidate": name,
                "s2_log_loss": cand_s2_loss,
                "projected_fixed_map_avg": projected_fixed_avg(cand_s2_loss),
                **drift,
            }
        )
        fixed_exports[name] = (cand_oof_s2, cand_sample_s2)
    stress = pd.DataFrame(stress_rows).sort_values(["s2_log_loss", "mean_abs_s2_drift"])

    oof_full = subject_prior(train, train, args.prior_alpha)
    sample_full = subject_prior(train, sample, args.prior_alpha)
    oof_full[:, TARGET_COLUMNS.index("S2")] = oof_s2
    sample_full[:, TARGET_COLUMNS.index("S2")] = sample_s2
    write_prediction(output_dir / "oof_s2_opportunity_pairwise_decoder.csv", train, oof_full, oof=True)
    write_prediction(output_dir / "submission_s2_opportunity_pairwise_decoder.csv", sample, sample_full, oof=False)
    fixed_oof_full = subject_prior(train, train, args.prior_alpha)
    fixed_sample_full = subject_prior(train, sample, args.prior_alpha)
    fixed_oof_full[:, TARGET_COLUMNS.index("S2")] = fixed_best_oof_s2
    fixed_sample_full[:, TARGET_COLUMNS.index("S2")] = fixed_best_sample_s2
    write_prediction(output_dir / "oof_fixed_best_s2_opportunity_pairwise_decoder.csv", train, fixed_oof_full, oof=True)
    write_prediction(output_dir / "submission_fixed_best_s2_opportunity_pairwise_decoder.csv", sample, fixed_sample_full, oof=False)
    stress.to_csv(output_dir / "fixed_candidate_stress.csv", index=False)

    selection = pd.DataFrame(selection_rows)
    inner = pd.DataFrame(inner_rows)
    selection_counts = selection.groupby("selected").size().reset_index(name="outer_count").sort_values(["outer_count", "selected"], ascending=[False, True])
    selection.to_csv(output_dir / "outer_selection.csv", index=False)
    selection_counts.to_csv(output_dir / "selection_counts.csv", index=False)
    inner.to_csv(output_dir / "inner_candidate_scores.csv", index=False)
    full_scores.to_csv(output_dir / "full_oof_candidate_scores.csv", index=False)
    diagnostics = {
        "nested_s2_log_loss": s2_loss,
        "fixed_map_current_s2_log_loss": FIXED_MAP_TARGET_LOSSES["S2"],
        "direct_psg_opp_probe_s2_log_loss": 0.562387,
        "projected_fixed_map_avg": projected_avg,
        "current_fixed_map_avg": float(np.mean([FIXED_MAP_TARGET_LOSSES[target] for target in TARGET_COLUMNS])),
        "best_full_oof_candidate": full_scores.iloc[0].to_dict(),
        "fixed_best_s2_log_loss": fixed_best_s2_loss,
        "fixed_best_projected_fixed_map_avg": fixed_best_projected_avg,
        "fixed_best_s2_reference_drift": s2_reference_drift(sample, fixed_best_sample_s2, args.reference_submission),
        "fixed_candidate_stress": stress.to_dict(orient="records"),
        "selection_counts": selection_counts.to_dict(orient="records"),
        "s2_reference_drift": s2_reference_drift(sample, sample_s2, args.reference_submission),
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(diagnostics, indent=2, ensure_ascii=False), encoding="utf-8")
    report = [
        "# S2 Opportunity Pairwise Decoder",
        "",
        "## Purpose",
        "",
        "Test the same opportunity/Q-state S2 signal with decoders that expand the 450 labels into pairwise ranking comparisons or prototype-to-label distances. This keeps the input family narrow while avoiding the coarse KMeans state bin failure.",
        "",
        "## Result",
        "",
        f"- Nested S2 logloss: `{s2_loss:.6f}`",
        f"- Current protected fixed-map S2 logloss: `{FIXED_MAP_TARGET_LOSSES['S2']:.6f}`",
        "- Direct full-fold `psg_opp` probe S2 logloss: `0.562387`",
        f"- Projected fixed-map avg if only S2 is replaced: `{projected_avg:.6f}`",
        f"- Current fixed-map avg reference: `{diagnostics['current_fixed_map_avg']:.6f}`",
        f"- Best fixed candidate: `{fixed_best_name}`",
        f"- Best fixed candidate S2 logloss: `{fixed_best_s2_loss:.6f}`",
        f"- Best fixed candidate projected fixed-map avg: `{fixed_best_projected_avg:.6f}`",
        "",
        "## Selection Counts",
        "",
        dataframe_to_markdown(selection_counts),
        "",
        "## Best Full-OOF Candidates",
        "",
        dataframe_to_markdown(full_scores.head(20)),
        "",
        "## Inner Candidate Scores",
        "",
        dataframe_to_markdown(inner.sort_values(["outer_fold", "inner_s2_log_loss"]).head(80)),
        "",
        "## Sample Drift vs v83",
        "",
        dataframe_to_markdown(pd.DataFrame([diagnostics["s2_reference_drift"]])),
        "",
        "## Fixed Best Candidate Drift vs v83",
        "",
        dataframe_to_markdown(pd.DataFrame([diagnostics["fixed_best_s2_reference_drift"]])),
        "",
        "## Fixed Candidate Stress",
        "",
        dataframe_to_markdown(stress),
        "",
        "## Read",
        "",
        "- If pairwise ranking beats the protected S2 scout, the label bottleneck is helped by relative-day comparisons.",
        "- If a fixed candidate beats nested selection, the signal is real but model-selection over the candidate grid is unstable. Treat the fixed candidate as a hypothesis to stress-test, not an automatically safe submission rule.",
    ]
    (output_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"nested_s2={s2_loss:.6f} projected_avg={projected_avg:.6f}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a nested S2 opportunity pairwise decoder.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/domain_s2_opportunity_pairwise_decoder_v1")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--outer-folds", type=int, default=5)
    parser.add_argument("--inner-folds", type=int, default=4)
    parser.add_argument("--prior-alpha", type=float, default=8.0)
    parser.add_argument("--max-pairs", type=int, default=12000)
    parser.add_argument("--n-label-proto", type=int, default=10)
    parser.add_argument("--stress-top-k", type=int, default=8)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
