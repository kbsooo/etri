from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from probe_domain_ssl_latents import (
    EPS,
    KEY_COLUMNS,
    MERGE_COLUMNS,
    TARGET_COLUMNS,
    dataframe_to_markdown,
    feature_views,
    load_latent_table,
    make_subject_time_folds,
    normalize_keys,
    subject_prior,
    write_prediction,
)


FIXED_MAP_TARGET_LOSSES = {
    "Q1": 0.653762,
    "Q2": 0.682062,
    "Q3": 0.665036,
    "S1": 0.557172,
    "S2": 0.567195,
    "S3": 0.513590,
    "S4": 0.632894,
}


DEFAULT_LATENTS = {
    "psg_opp": "artifacts/domain_psg_q_state_s2_opportunity_only_v1.parquet",
    "psg_opp_mob": "artifacts/domain_psg_q_state_s2_opportunity_mobility_v1.parquet",
    "psg_qrel": "artifacts/domain_best_plus_psg_q_state_s2_relative_q_state_v1.parquet",
    "cc_opp": "outputs/domain_causal_chain_plus_best_latents_v1/best_plus_cc_opportunity.parquet",
}


@dataclass(frozen=True)
class StateSpec:
    latent: str
    view: str
    n_states: int
    decoder: str
    blend: float

    @property
    def name(self) -> str:
        return f"{self.latent}__{self.view}__k{self.n_states}__{self.decoder}__b{int(self.blend * 100):02d}"


def safe_logit(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values, EPS, 1.0 - EPS)
    return np.log(clipped / (1.0 - clipped))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


def build_specs() -> list[StateSpec]:
    specs: list[StateSpec] = []
    # Keep this candidate grid deliberately small. The previous PSG split already
    # identified opportunity, opportunity+mobility, and relative Q-state as the
    # only S2-positive families, so the nested state decoder should test those
    # hypotheses rather than re-running a broad source search.
    grid = [
        ("psg_opp", "deviation", [3, 4, 5], ["state_rate", "soft_state_rate"], [0.25, 0.40]),
        ("psg_opp", "absolute_plus_deviation", [4], ["state_rate", "soft_state_rate"], [0.25]),
        ("psg_opp_mob", "deviation", [4, 5], ["state_rate"], [0.25, 0.40]),
        ("psg_qrel", "absolute", [4, 5], ["state_rate"], [0.25, 0.40]),
        ("cc_opp", "absolute_plus_deviation", [4], ["state_rate"], [0.25, 0.40]),
    ]
    for latent, view, states, decoders, blends in grid:
        for n_states in states:
            for decoder in decoders:
                for blend in blends:
                    specs.append(StateSpec(latent, view, n_states, decoder, blend))
    return specs


def preprocess_for_state(x_fit: np.ndarray, x_eval: np.ndarray, x_sample: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    fit = scaler.fit_transform(imputer.fit_transform(x_fit))
    eval_part = scaler.transform(imputer.transform(x_eval))
    sample = scaler.transform(imputer.transform(x_sample))
    return fit, eval_part, sample


def smooth_rates(labels: np.ndarray, y: np.ndarray, n_states: int, global_rate: float, alpha: float) -> np.ndarray:
    rates = np.zeros(n_states, dtype=float)
    for state in range(n_states):
        mask = labels == state
        rates[state] = (float(y[mask].sum()) + alpha * global_rate) / (float(mask.sum()) + alpha)
    return np.clip(rates, EPS, 1.0 - EPS)


def state_distances(model: KMeans, x: np.ndarray) -> np.ndarray:
    dist = model.transform(x)
    return np.clip(dist, 1e-6, None)


def one_hot(labels: np.ndarray, n_states: int) -> np.ndarray:
    try:
        encoder = OneHotEncoder(categories=[list(range(n_states))], sparse_output=False, handle_unknown="ignore")
    except TypeError:
        encoder = OneHotEncoder(categories=[list(range(n_states))], sparse=False, handle_unknown="ignore")
    return encoder.fit_transform(labels.reshape(-1, 1))


def fit_state_decoder(
    spec: StateSpec,
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    prior_eval: np.ndarray,
    prior_sample: np.ndarray,
    alpha: float,
) -> tuple[np.ndarray, np.ndarray]:
    if len(np.unique(y_fit)) < 2:
        return prior_eval, prior_sample
    x_fit_s, x_eval_s, x_sample_s = preprocess_for_state(x_fit, x_eval, x_sample)
    n_states = min(spec.n_states, max(2, len(x_fit_s) // 8))
    kmeans = KMeans(n_clusters=n_states, random_state=13, n_init=20)
    fit_labels = kmeans.fit_predict(x_fit_s)
    eval_labels = kmeans.predict(x_eval_s)
    sample_labels = kmeans.predict(x_sample_s)
    global_rate = float(np.mean(y_fit))
    rates = smooth_rates(fit_labels, y_fit.astype(float), n_states, global_rate, alpha)

    if spec.decoder == "state_rate":
        eval_raw = rates[eval_labels]
        sample_raw = rates[sample_labels]
    elif spec.decoder == "soft_state_rate":
        fit_dist = state_distances(kmeans, x_fit_s)
        eval_dist = state_distances(kmeans, x_eval_s)
        sample_dist = state_distances(kmeans, x_sample_s)
        fit_scale = np.median(fit_dist, axis=0)
        fit_scale = np.where(fit_scale <= 1e-6, 1.0, fit_scale)
        eval_w = np.exp(-eval_dist / fit_scale)
        sample_w = np.exp(-sample_dist / fit_scale)
        eval_w = eval_w / np.clip(eval_w.sum(axis=1, keepdims=True), 1e-6, None)
        sample_w = sample_w / np.clip(sample_w.sum(axis=1, keepdims=True), 1e-6, None)
        eval_raw = eval_w @ rates
        sample_raw = sample_w @ rates
    elif spec.decoder == "state_logreg":
        fit_dist = state_distances(kmeans, x_fit_s)
        eval_dist = state_distances(kmeans, x_eval_s)
        sample_dist = state_distances(kmeans, x_sample_s)
        fit_features = np.hstack([one_hot(fit_labels, n_states), fit_dist, rates[fit_labels].reshape(-1, 1)])
        eval_features = np.hstack([one_hot(eval_labels, n_states), eval_dist, rates[eval_labels].reshape(-1, 1)])
        sample_features = np.hstack([one_hot(sample_labels, n_states), sample_dist, rates[sample_labels].reshape(-1, 1)])
        model = LogisticRegression(C=0.1, max_iter=2000, solver="lbfgs")
        model.fit(fit_features, y_fit.astype(int))
        eval_raw = model.predict_proba(eval_features)[:, 1]
        sample_raw = model.predict_proba(sample_features)[:, 1]
    else:
        raise ValueError(spec.decoder)

    eval_pred = sigmoid((1.0 - spec.blend) * safe_logit(prior_eval) + spec.blend * safe_logit(eval_raw))
    sample_pred = sigmoid((1.0 - spec.blend) * safe_logit(prior_sample) + spec.blend * safe_logit(sample_raw))
    return np.clip(eval_pred, EPS, 1.0 - EPS), np.clip(sample_pred, EPS, 1.0 - EPS)


def select_spec_inner(
    specs: list[StateSpec],
    latent_tables: dict[str, tuple[pd.DataFrame, pd.DataFrame, list[str]]],
    train: pd.DataFrame,
    sample: pd.DataFrame,
    outer_train_idx: np.ndarray,
    args: argparse.Namespace,
) -> tuple[StateSpec, list[dict[str, object]]]:
    outer_train = train.iloc[outer_train_idx].reset_index(drop=True)
    inner_folds = make_subject_time_folds(outer_train, args.inner_folds)
    rows = []
    for spec in specs:
        inner_oof = np.zeros(len(outer_train_idx), dtype=float)
        train_x, sample_x, z_cols = latent_tables[spec.latent]
        for fit_local, val_local in inner_folds:
            fit_global = outer_train_idx[fit_local]
            val_global = outer_train_idx[val_local]
            views = feature_views(train_x, sample_x, z_cols, fit_global, val_global)
            x_fit, x_val, x_sample = views[spec.view]
            fit_frame = train.iloc[fit_global]
            val_frame = train.iloc[val_global]
            prior_val = subject_prior(fit_frame, val_frame, args.prior_alpha)[:, TARGET_COLUMNS.index("S2")]
            prior_sample = subject_prior(fit_frame, sample, args.prior_alpha)[:, TARGET_COLUMNS.index("S2")]
            pred, _ = fit_state_decoder(
                spec,
                x_fit,
                fit_frame["S2"].to_numpy(int),
                x_val,
                x_sample,
                prior_val,
                prior_sample,
                args.state_alpha,
            )
            inner_oof[val_local] = pred
        loss = float(log_loss(outer_train["S2"].to_numpy(int), np.clip(inner_oof, EPS, 1.0 - EPS), labels=[0, 1]))
        rows.append({"candidate": spec.name, "inner_s2_log_loss": loss})
    best_row = min(rows, key=lambda row: row["inner_s2_log_loss"])
    best_spec = next(spec for spec in specs if spec.name == best_row["candidate"])
    return best_spec, rows


def build_full_spec_scores(
    specs: list[StateSpec],
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
            train_x, sample_x, z_cols = latent_tables[spec.latent]
            views = feature_views(train_x, sample_x, z_cols, fit_idx, eval_idx)
            x_fit, x_eval, x_sample = views[spec.view]
            fit_frame = train.iloc[fit_idx]
            eval_frame = train.iloc[eval_idx]
            prior_eval = subject_prior(fit_frame, eval_frame, args.prior_alpha)[:, TARGET_COLUMNS.index("S2")]
            prior_sample = subject_prior(fit_frame, sample, args.prior_alpha)[:, TARGET_COLUMNS.index("S2")]
            pred, _ = fit_state_decoder(
                spec,
                x_fit,
                fit_frame["S2"].to_numpy(int),
                x_eval,
                x_sample,
                prior_eval,
                prior_sample,
                args.state_alpha,
            )
            oof[eval_idx] = pred
        rows.append({"candidate": spec.name, "full_oof_s2_log_loss": float(log_loss(train["S2"].to_numpy(int), oof, labels=[0, 1]))})
    return pd.DataFrame(rows).sort_values("full_oof_s2_log_loss")


def projected_fixed_avg(s2_loss: float) -> float:
    losses = dict(FIXED_MAP_TARGET_LOSSES)
    losses["S2"] = s2_loss
    return float(np.mean([losses[target] for target in TARGET_COLUMNS]))


def s2_reference_drift(sample: pd.DataFrame, sample_s2: np.ndarray, reference_path: str) -> dict[str, float]:
    if not reference_path:
        return {}
    path = Path(reference_path)
    if not path.exists():
        return {}
    ref = normalize_keys(pd.read_csv(path))
    pred = sample[KEY_COLUMNS].copy()
    pred["S2"] = sample_s2
    merged = pred.merge(ref[KEY_COLUMNS + ["S2"]], on=KEY_COLUMNS, suffixes=("_pred", "_ref"), how="inner", validate="one_to_one")
    if merged.empty:
        return {}
    return {
        "mean_abs_s2_drift": float(np.mean(np.abs(merged["S2_pred"].to_numpy(float) - merged["S2_ref"].to_numpy(float)))),
        "max_abs_s2_drift": float(np.max(np.abs(merged["S2_pred"].to_numpy(float) - merged["S2_ref"].to_numpy(float)))),
        "pred_s2_mean": float(np.mean(merged["S2_pred"].to_numpy(float))),
        "ref_s2_mean": float(np.mean(merged["S2_ref"].to_numpy(float))),
    }


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    specs = build_specs()
    latent_paths = {name: Path(path) for name, path in DEFAULT_LATENTS.items()}
    latent_tables = {name: load_latent_table(path, train, sample) for name, path in latent_paths.items()}
    folds = make_subject_time_folds(train, args.outer_folds)

    oof_s2 = np.zeros(len(train), dtype=float)
    sample_parts = []
    selection_rows = []
    inner_rows = []
    for outer_i, (fit_idx, eval_idx) in enumerate(folds, 1):
        best_spec, rows = select_spec_inner(specs, latent_tables, train, sample, fit_idx, args)
        inner_rows.extend({"outer_fold": outer_i, **row} for row in rows)
        train_x, sample_x, z_cols = latent_tables[best_spec.latent]
        x_fit, x_eval, x_sample = feature_views(train_x, sample_x, z_cols, fit_idx, eval_idx)[best_spec.view]
        fit_frame = train.iloc[fit_idx]
        eval_frame = train.iloc[eval_idx]
        prior_eval = subject_prior(fit_frame, eval_frame, args.prior_alpha)[:, TARGET_COLUMNS.index("S2")]
        prior_sample = subject_prior(fit_frame, sample, args.prior_alpha)[:, TARGET_COLUMNS.index("S2")]
        val_pred, sample_pred = fit_state_decoder(
            best_spec,
            x_fit,
            fit_frame["S2"].to_numpy(int),
            x_eval,
            x_sample,
            prior_eval,
            prior_sample,
            args.state_alpha,
        )
        oof_s2[eval_idx] = val_pred
        sample_parts.append(sample_pred)
        selection_rows.append({"outer_fold": outer_i, "selected": best_spec.name})

    sample_s2 = np.mean(np.stack(sample_parts, axis=0), axis=0)
    s2_loss = float(log_loss(train["S2"].to_numpy(int), np.clip(oof_s2, EPS, 1.0 - EPS), labels=[0, 1]))
    prior_oof = np.zeros(len(train), dtype=float)
    for fit_idx, eval_idx in folds:
        prior_oof[eval_idx] = subject_prior(train.iloc[fit_idx], train.iloc[eval_idx], args.prior_alpha)[:, TARGET_COLUMNS.index("S2")]
    prior_s2_loss = float(log_loss(train["S2"].to_numpy(int), prior_oof, labels=[0, 1]))
    full_scores = build_full_spec_scores(specs, latent_tables, train, sample, folds, args)

    oof_full = subject_prior(train, train, args.prior_alpha)
    sample_full = subject_prior(train, sample, args.prior_alpha)
    oof_full[:, TARGET_COLUMNS.index("S2")] = oof_s2
    sample_full[:, TARGET_COLUMNS.index("S2")] = sample_s2
    write_prediction(output_dir / "oof_s2_opportunity_state_decoder.csv", train, oof_full, oof=True)
    write_prediction(output_dir / "submission_s2_opportunity_state_decoder.csv", sample, sample_full, oof=False)

    selection = pd.DataFrame(selection_rows)
    inner = pd.DataFrame(inner_rows)
    selection_counts = selection.groupby("selected").size().reset_index(name="outer_count").sort_values(["outer_count", "selected"], ascending=[False, True])
    selection.to_csv(output_dir / "outer_selection.csv", index=False)
    selection_counts.to_csv(output_dir / "selection_counts.csv", index=False)
    inner.to_csv(output_dir / "inner_candidate_scores.csv", index=False)
    full_scores.to_csv(output_dir / "full_oof_candidate_scores.csv", index=False)

    projected_avg = projected_fixed_avg(s2_loss)
    diagnostics = {
        "nested_s2_log_loss": s2_loss,
        "subject_prior_s2_log_loss": prior_s2_loss,
        "fixed_map_current_s2_log_loss": FIXED_MAP_TARGET_LOSSES["S2"],
        "projected_fixed_map_avg": projected_avg,
        "current_fixed_map_avg": float(np.mean([FIXED_MAP_TARGET_LOSSES[target] for target in TARGET_COLUMNS])),
        "best_full_oof_candidate": full_scores.iloc[0].to_dict(),
        "selection_counts": selection_counts.to_dict(orient="records"),
        "s2_reference_drift": s2_reference_drift(sample, sample_s2, args.reference_submission),
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(diagnostics, indent=2, ensure_ascii=False), encoding="utf-8")

    report = [
        "# S2 Opportunity-State Decoder",
        "",
        "## Purpose",
        "",
        "Test whether the new S2 PSG opportunity signal can be promoted from source selection into an explicit intermediate-state decoder. Each outer fold first clusters opportunity/Q-state latent rows without labels, then maps those states to S2 with small state-rate or state-logistic decoders selected by inner folds.",
        "",
        "## Result",
        "",
        f"- Nested S2 logloss: `{s2_loss:.6f}`",
        f"- Fold-safe subject-prior S2 logloss: `{prior_s2_loss:.6f}`",
        f"- Current protected fixed-map S2 logloss: `{FIXED_MAP_TARGET_LOSSES['S2']:.6f}`",
        f"- Projected fixed-map avg if only S2 is replaced: `{projected_avg:.6f}`",
        f"- Current fixed-map avg reference: `{diagnostics['current_fixed_map_avg']:.6f}`",
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
        "## Read",
        "",
        "- This is stricter than the previous fixed-map scout because the selected S2 state decoder is chosen inside each outer fold.",
        "- A useful result should beat the protected fixed-map S2 loss or at least approach the direct `psg_opp` probe while using state-mediated decoding.",
        "- If it fails, the opportunity clue is still real but likely needs a richer encoder objective rather than KMeans state bins.",
    ]
    drift = diagnostics["s2_reference_drift"]
    if drift:
        report.extend(
            [
                "",
                "## Sample Drift vs v83",
                "",
                dataframe_to_markdown(pd.DataFrame([drift])),
            ]
        )
    (output_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"nested_s2={s2_loss:.6f} projected_avg={projected_avg:.6f}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a nested S2 opportunity-state decoder.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/domain_s2_opportunity_state_decoder_v1")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--outer-folds", type=int, default=5)
    parser.add_argument("--inner-folds", type=int, default=4)
    parser.add_argument("--prior-alpha", type=float, default=8.0)
    parser.add_argument("--state-alpha", type=float, default=8.0)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
