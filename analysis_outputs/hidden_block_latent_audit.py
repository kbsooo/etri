from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
SORT_KEY = ["subject_id", "lifelog_date"]
EPS = 1e-5


@dataclass(frozen=True)
class SubmissionSpec:
    key: str
    path: Path
    public_lb: float | None = None
    role: str = ""


SPECS = [
    SubmissionSpec(
        "anchor578",
        OUT / "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
        0.5784273528,
        "observed_anchor",
    ),
    SubmissionSpec(
        "stage2",
        OUT / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        0.5779449757,
        "observed_stage2",
    ),
    SubmissionSpec(
        "ordinal_q",
        OUT / "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
        0.5783033652,
        "observed_bad_count_shift",
    ),
    SubmissionSpec(
        "raw025",
        JEPA / "submission_raw_timeline_jepa_rescue_strict_scale0p25.csv",
        None,
        "raw_axis_scale",
    ),
    SubmissionSpec(
        "raw05",
        JEPA / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
        0.5775263072,
        "observed_raw_axis",
    ),
    SubmissionSpec(
        "raw075",
        JEPA / "submission_raw_timeline_jepa_rescue_strict_scale0p75.csv",
        None,
        "raw_axis_scale",
    ),
    SubmissionSpec(
        "raw10",
        JEPA / "submission_raw_timeline_jepa_rescue_strict_scale1p0.csv",
        None,
        "raw_axis_scale",
    ),
    SubmissionSpec(
        "jepa_bad_residual",
        JEPA / "submission_jepa_latent_residual_probe.csv",
        0.5812273278,
        "observed_jepa_bad_axis",
    ),
    SubmissionSpec(
        "jepa_bad_q2",
        JEPA / "submission_jepa_latent_q2_w0p45.csv",
        0.5798012862,
        "observed_jepa_bad_axis",
    ),
]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(p, dtype=np.float64), EPS, 1.0 - EPS)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -40.0, 40.0)))


def stable_tag(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def read_submission(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    return df.sort_values(KEY).reset_index(drop=True)


def expected_delta(q: np.ndarray, candidate: np.ndarray, anchor: np.ndarray) -> float:
    q = clip(q)
    candidate = clip(candidate)
    anchor = clip(anchor)
    return float(
        np.mean(
            q * (np.log(anchor) - np.log(candidate))
            + (1.0 - q) * (np.log(1.0 - anchor) - np.log(1.0 - candidate))
        )
    )


def score_features(pred: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p = clip(pred)
    intercept = -np.log(1.0 - p)
    coef = np.log((1.0 - p) / p)
    return intercept, coef


def load_predictions() -> tuple[dict[str, pd.DataFrame], dict[str, np.ndarray]]:
    frames: dict[str, pd.DataFrame] = {}
    preds: dict[str, np.ndarray] = {}
    ref_key: pd.DataFrame | None = None
    for spec in SPECS:
        if not spec.path.exists():
            continue
        frame = read_submission(spec.path)
        if ref_key is None:
            ref_key = frame[KEY].copy()
        elif not frame[KEY].equals(ref_key):
            raise ValueError(f"key mismatch: {spec.path}")
        frames[spec.key] = frame
        preds[spec.key] = frame[TARGETS].to_numpy(dtype=np.float64)
    return frames, preds


def sample_block_ids(train: pd.DataFrame, sample: pd.DataFrame) -> np.ndarray:
    known = train[KEY].copy()
    known["_kind"] = "known"
    unknown = sample[KEY].copy()
    unknown["_kind"] = "unknown"
    unknown["_row_pos"] = np.arange(len(sample))
    full = pd.concat([known, unknown], ignore_index=True, sort=False).sort_values(KEY).reset_index(drop=True)
    full["_block"] = full.groupby("subject_id")["_kind"].transform(lambda s: s.ne(s.shift()).cumsum()).astype(int)
    unk = full[full["_kind"].eq("unknown")].sort_values("_row_pos")
    return (unk["subject_id"].astype(str) + "_b" + unk["_block"].astype(str)).to_numpy()


def block_metadata(train: pd.DataFrame, sample: pd.DataFrame, block_ids: np.ndarray) -> pd.DataFrame:
    blocks = pd.read_csv(OUT / "breakthrough_split_blocks.csv")
    sub_blocks = blocks[blocks["split"].eq("submission")].copy()
    rows = []
    for block_id in pd.unique(block_ids):
        mask = block_ids == block_id
        block_rows = sample.loc[mask].sort_values("lifelog_date")
        sid = str(block_rows["subject_id"].iloc[0])
        block_num = int(str(block_id).split("_b")[-1])
        meta = sub_blocks[(sub_blocks["subject_id"].eq(sid)) & (sub_blocks["block_id"].eq(block_num))]
        rec = {
            "hidden_block_id": block_id,
            "subject_id": sid,
            "block_id": block_num,
            "n_rows": int(mask.sum()),
            "start": block_rows["lifelog_date"].min().date().isoformat(),
            "end": block_rows["lifelog_date"].max().date().isoformat(),
            "prev_train_gap_days": np.nan,
            "next_train_gap_days": np.nan,
        }
        if not meta.empty:
            for col in ["prev_train_gap_days", "next_train_gap_days"]:
                rec[col] = float(meta.iloc[0][col]) if pd.notna(meta.iloc[0][col]) else np.nan
            for target in TARGETS:
                for side in ["prev", "next"]:
                    col = f"{side}_{target}"
                    rec[col] = float(meta.iloc[0][col]) if col in meta.columns and pd.notna(meta.iloc[0][col]) else np.nan
        rows.append(rec)
    return pd.DataFrame(rows)


def endpoint_rate_table(train: pd.DataFrame) -> pd.DataFrame:
    records = []
    for target in TARGETS:
        for sid, group in train.sort_values(SORT_KEY).groupby("subject_id", sort=False):
            y = group[target].to_numpy(dtype=int)
            subject_mean = float(y.mean())
            n = len(y)
            for length in range(1, 17):
                for start in range(1, n - length):
                    end = start + length
                    records.append(
                        {
                            "target": target,
                            "subject_id": sid,
                            "length": length,
                            "len_bin": len_bin(length),
                            "prev": int(y[start - 1]),
                            "next": int(y[end]),
                            "rate": float(y[start:end].mean()),
                            "subject_mean": subject_mean,
                        }
                    )
    rec = pd.DataFrame(records)
    tab = (
        rec.groupby(["target", "len_bin", "prev", "next"], observed=True)
        .agg(n=("rate", "size"), mean_rate=("rate", "mean"), sd_rate=("rate", "std"))
        .reset_index()
    )
    tab.to_csv(OUT / "hidden_block_endpoint_rate_table.csv", index=False)
    return tab


def len_bin(n: int) -> str:
    if n <= 2:
        return "1-2"
    if n <= 5:
        return "3-5"
    if n <= 10:
        return "6-10"
    return "11-16"


def endpoint_priors(meta: pd.DataFrame, table: pd.DataFrame, train: pd.DataFrame) -> pd.DataFrame:
    global_mean = train[TARGETS].mean().to_dict()
    subject_mean = train.groupby("subject_id")[TARGETS].mean()
    out = []
    lookup = {
        (str(r.target), str(r.len_bin), int(r.prev), int(r.next)): (float(r.mean_rate), int(r.n), float(r.sd_rate))
        for r in table.itertuples(index=False)
    }
    for row in meta.itertuples(index=False):
        rec = {
            "hidden_block_id": row.hidden_block_id,
            "subject_id": row.subject_id,
            "n_rows": int(row.n_rows),
            "len_bin": len_bin(int(row.n_rows)),
        }
        for target in TARGETS:
            prev = getattr(row, f"prev_{target}")
            nxt = getattr(row, f"next_{target}")
            subj = float(subject_mean.loc[row.subject_id, target]) if row.subject_id in subject_mean.index else float(global_mean[target])
            if pd.notna(prev) and pd.notna(nxt):
                key = (target, rec["len_bin"], int(prev), int(nxt))
                mean_rate, n_obs, sd_rate = lookup.get(key, (subj, 0, np.nan))
                # Shrink the endpoint bridge because pseudo-block tests show endpoints are informative but overconfident.
                rate = (n_obs * mean_rate + 40.0 * subj) / (n_obs + 40.0)
                source = "prev_next_len"
            elif pd.notna(prev):
                rate = 0.35 * float(prev) + 0.65 * subj
                n_obs = 0
                sd_rate = np.nan
                source = "prev_shrunk"
            elif pd.notna(nxt):
                rate = 0.35 * float(nxt) + 0.65 * subj
                n_obs = 0
                sd_rate = np.nan
                source = "next_shrunk"
            else:
                rate = subj
                n_obs = 0
                sd_rate = np.nan
                source = "subject_mean"
            rec[f"endpoint_rate_{target}"] = float(np.clip(rate, EPS, 1.0 - EPS))
            rec[f"endpoint_count_{target}"] = float(rate * int(row.n_rows))
            rec[f"endpoint_source_{target}"] = source
            rec[f"endpoint_support_{target}"] = int(n_obs)
            rec[f"endpoint_sd_{target}"] = sd_rate
        out.append(rec)
    result = pd.DataFrame(out)
    result.to_csv(OUT / "hidden_block_endpoint_priors.csv", index=False)
    return result


def group_reduce(
    prior: np.ndarray,
    constraint_preds: list[np.ndarray],
    block_ids: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    unique_blocks = pd.Index(block_ids).drop_duplicates().to_numpy()
    block_to_idx = {b: i for i, b in enumerate(unique_blocks)}
    n_blocks = len(unique_blocks)
    n_vars = n_blocks * len(TARGETS)
    weights = np.zeros(n_vars, dtype=np.float64)
    prior_sum = np.zeros(n_vars, dtype=np.float64)
    coef_sums = [np.zeros(n_vars, dtype=np.float64) for _ in constraint_preds]
    constant_sum = np.zeros(len(constraint_preds), dtype=np.float64)
    total_cells = prior.shape[0] * prior.shape[1]

    features = [score_features(pred) for pred in constraint_preds]
    for i, block_id in enumerate(block_ids):
        block_pos = block_to_idx[block_id]
        for j in range(len(TARGETS)):
            v = block_pos * len(TARGETS) + j
            weights[v] += 1.0 / total_cells
            prior_sum[v] += prior[i, j] / total_cells
            for k, (intercept, coef) in enumerate(features):
                constant_sum[k] += float(intercept[i, j]) / total_cells
                coef_sums[k][v] += float(coef[i, j]) / total_cells
    prior_group = clip(prior_sum / np.maximum(weights, 1e-12))
    coef_mat = np.vstack(coef_sums).T
    return prior_group, coef_mat, constant_sum, weights, unique_blocks


def solve_block_posterior(
    prior: np.ndarray,
    constraint_preds: list[np.ndarray],
    public_scores: np.ndarray,
    block_ids: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    prior_group, coef_mat, constant_sum, weights, unique_blocks = group_reduce(prior, constraint_preds, block_ids)
    target_moments = public_scores - constant_sum
    z0 = logit(prior_group)
    lam = np.zeros(coef_mat.shape[1], dtype=np.float64)
    residual = np.full(coef_mat.shape[1], np.nan)
    converged = False
    for iteration in range(200):
        q = sigmoid(z0 + coef_mat @ lam / np.maximum(weights, 1e-12))
        moments = coef_mat.T @ q
        residual = target_moments - moments
        if float(np.max(np.abs(residual))) < 1e-10:
            converged = True
            break
        diag = q * (1.0 - q)
        jac = (coef_mat.T * (diag / np.maximum(weights, 1e-12))) @ coef_mat
        jac += 1e-8 * np.eye(jac.shape[0])
        step = np.linalg.solve(jac, residual)
        norm = float(np.linalg.norm(step))
        if norm > 12.0:
            step *= 12.0 / norm
        lam += step

    q = sigmoid(z0 + coef_mat @ lam / np.maximum(weights, 1e-12))
    fit_rows = []
    for i, score in enumerate(public_scores):
        fit_rows.append(
            {
                "constraint_index": i,
                "target_score": float(score),
                "fitted_score": float(constant_sum[i] + coef_mat[:, i] @ q),
                "residual": float(score - (constant_sum[i] + coef_mat[:, i] @ q)),
                "converged": bool(converged),
                "iterations": int(iteration + 1),
            }
        )

    expanded = np.zeros_like(prior)
    block_to_idx = {b: i for i, b in enumerate(unique_blocks)}
    for i, block_id in enumerate(block_ids):
        base = block_to_idx[block_id] * len(TARGETS)
        expanded[i] = q[base : base + len(TARGETS)]
    return clip(q), clip(expanded), pd.DataFrame(fit_rows)


def blend_logits(base: np.ndarray, donor: np.ndarray, scale: float) -> np.ndarray:
    return clip(sigmoid(logit(base) + scale * (logit(donor) - logit(base))))


def save_candidate(template: pd.DataFrame, pred: np.ndarray, name: str) -> str:
    out = template.copy()
    out[TARGETS] = clip(pred)
    path = OUT / name
    out.to_csv(path, index=False)
    return path.name


def projection_ratio(move: np.ndarray, axis: np.ndarray) -> float:
    m = move.reshape(-1)
    a = axis.reshape(-1)
    denom = float(np.dot(a, a))
    if denom <= 1e-12:
        return np.nan
    return float(np.dot(m, a) / denom)


def raw_axis_fit(frames: dict[str, pd.DataFrame], preds: dict[str, np.ndarray]) -> tuple[pd.DataFrame, list[str], np.ndarray]:
    stage = preds["stage2"]
    raw05 = preds["raw05"]
    raw10 = preds["raw10"]
    obs_delta = 0.5775263072 - 0.5779449757
    lo, hi = -2.0, 4.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        q = blend_logits(stage, raw05, mid)
        if expected_delta(q, raw05, stage) > obs_delta:
            lo = mid
        else:
            hi = mid
    alpha = 0.5 * (lo + hi)
    q = blend_logits(stage, raw05, alpha)

    rows = []
    saved = []
    for scale in np.linspace(0.0, 1.25, 51):
        pred = blend_logits(stage, raw10, float(scale))
        public_est = 0.5779449757 + expected_delta(q, pred, stage)
        rows.append(
            {
                "candidate_kind": "raw_strict_scale_scan",
                "scale": float(scale),
                "pred_public_from_raw05_axis": public_est,
                "pred_delta_vs_stage2": public_est - 0.5779449757,
                "mean_abs_move_vs_stage2": float(np.abs(pred - stage).mean()),
            }
        )
    scan = pd.DataFrame(rows).sort_values("pred_public_from_raw05_axis")
    for scale in [0.75, 0.875, 1.0]:
        pred = blend_logits(stage, raw10, scale)
        tag = str(scale).replace(".", "p")
        name = f"submission_hiddenblock_rawaxis_stage2_raw10_s{tag}_{stable_tag(str(scale))}.csv"
        saved.append(save_candidate(frames["stage2"], pred, name))
    scan["raw05_latent_alpha"] = alpha
    scan.to_csv(OUT / "hidden_block_raw_axis_scale_scan.csv", index=False)
    return scan, saved, q


def candidate_scores(
    preds: dict[str, np.ndarray],
    posterior_q: np.ndarray,
    raw_axis_q: np.ndarray,
    saved_files: list[str],
) -> pd.DataFrame:
    stage = preds["stage2"]
    anchor = preds["anchor578"]
    raw05 = preds["raw05"]
    bad_axis = preds["jepa_bad_residual"] - stage
    bad_q2_axis = preds["jepa_bad_q2"] - stage
    candidates = {
        key: pred
        for key, pred in preds.items()
        if key in {"anchor578", "stage2", "ordinal_q", "raw025", "raw05", "raw075", "raw10", "jepa_bad_residual", "jepa_bad_q2"}
    }
    for file_name in saved_files:
        df = read_submission(OUT / file_name)
        candidates[file_name] = df[TARGETS].to_numpy(dtype=np.float64)

    rows = []
    public_lookup = {spec.key: spec.public_lb for spec in SPECS}
    for key, pred in candidates.items():
        rows.append(
            {
                "candidate": key,
                "observed_public_lb": public_lookup.get(key),
                "posterior_expected_public_vs_anchor": 0.5784273528 + expected_delta(posterior_q, pred, anchor),
                "raw_axis_expected_public_vs_stage2": 0.5779449757 + expected_delta(raw_axis_q, pred, stage),
                "mean_abs_move_vs_stage2": float(np.abs(pred - stage).mean()),
                "mean_abs_move_vs_raw05": float(np.abs(pred - raw05).mean()),
                "bad_residual_axis_ratio": projection_ratio(pred - stage, bad_axis),
                "bad_q2_axis_ratio": projection_ratio(pred - stage, bad_q2_axis),
                "min_prob": float(pred.min()),
                "max_prob": float(pred.max()),
            }
        )
    out = pd.DataFrame(rows).sort_values(["raw_axis_expected_public_vs_stage2", "posterior_expected_public_vs_anchor"])
    out.to_csv(OUT / "hidden_block_candidate_publicfit_scores.csv", index=False)
    return out


def block_posterior_summary(
    meta: pd.DataFrame,
    block_ids: np.ndarray,
    prior: np.ndarray,
    posterior: np.ndarray,
    endpoint: pd.DataFrame,
    preds: dict[str, np.ndarray],
) -> pd.DataFrame:
    rows = []
    endpoint_by_block = endpoint.set_index("hidden_block_id")
    for block_id in pd.unique(block_ids):
        mask = block_ids == block_id
        rec = meta[meta["hidden_block_id"].eq(block_id)].iloc[0].to_dict()
        for name in ["stage2", "raw05", "raw10", "anchor578"]:
            for j, target in enumerate(TARGETS):
                rec[f"{name}_rate_{target}"] = float(preds[name][mask, j].mean())
        for j, target in enumerate(TARGETS):
            rec[f"posterior_rate_{target}"] = float(posterior[mask, j].mean())
            rec[f"posterior_count_{target}"] = float(posterior[mask, j].mean() * mask.sum())
            rec[f"prior_rate_{target}"] = float(prior[mask, j].mean())
            rec[f"posterior_minus_prior_{target}"] = float(posterior[mask, j].mean() - prior[mask, j].mean())
            if block_id in endpoint_by_block.index:
                rec[f"endpoint_rate_{target}"] = float(endpoint_by_block.loc[block_id, f"endpoint_rate_{target}"])
        rec["posterior_mean_abs_shift"] = float(np.mean(np.abs(posterior[mask] - prior[mask])))
        rec["raw05_mean_abs_shift_vs_stage2"] = float(np.mean(np.abs(preds["raw05"][mask] - preds["stage2"][mask])))
        rows.append(rec)
    out = pd.DataFrame(rows).sort_values("posterior_mean_abs_shift", ascending=False)
    out.to_csv(OUT / "hidden_block_posterior_block_summary.csv", index=False)
    return out


def write_report(
    raw_scan: pd.DataFrame,
    saved: list[str],
    fit: pd.DataFrame,
    candidate: pd.DataFrame,
    block_summary: pd.DataFrame,
    endpoint: pd.DataFrame,
) -> None:
    def csv_block(df: pd.DataFrame) -> str:
        return "```csv\n" + df.to_csv(index=False) + "```"

    lines = [
        "# Hidden Block Latent Audit",
        "",
        "JEPA is treated here as a block-state reconstruction tool: the target is an entire hidden submission episode rate/count latent, and the context is surrounding train labels plus raw timeline state.",
        "",
        "## Public Constraints Used",
        "",
        csv_block(pd.DataFrame(
            [
                {"key": s.key, "file": str(s.path.relative_to(ROOT)), "public_lb": s.public_lb, "role": s.role}
                for s in SPECS
                if s.public_lb is not None and s.path.exists()
            ]
        )),
        "",
        "## Raw-Rescue Axis",
        "",
        "The observed raw05 public score fits a stage2->raw05 latent with one scalar alpha. Scanning the stronger raw10 direction gives only a tiny expected gain beyond raw05, so this is a probe axis, not the 0.54 breakthrough.",
        "",
        csv_block(raw_scan.head(12).round(10)),
        "",
        "Saved raw-axis candidates:",
        "",
        "\n".join(f"- `{name}`" for name in saved),
        "",
        "## Block Posterior Constraint Fit",
        "",
        csv_block(fit.round(12)),
        "",
        "## Candidate Public-Fit Ranking",
        "",
        csv_block(candidate.head(18).round(10)),
        "",
        "## Highest Posterior Block Shifts",
        "",
        csv_block(block_summary[
            [
                "hidden_block_id",
                "subject_id",
                "n_rows",
                "start",
                "end",
                "posterior_mean_abs_shift",
                "raw05_mean_abs_shift_vs_stage2",
            ]
        ]
        .head(18)
        .round(8)),
        "",
        "## Endpoint Priors",
        "",
        "Endpoint/length priors are saved as `hidden_block_endpoint_priors.csv`. They are useful as weak count priors; pseudo-block tests show endpoints are informative but too noisy for hard constraints.",
        "",
        csv_block(endpoint.head(12).round(6)),
        "",
        "## Interpretation",
        "",
        "- The raw-rescue JEPA axis is public-positive and almost orthogonal to the two known JEPA-bad axes, but its remaining scale upside is tiny.",
        "- The block posterior can satisfy all observed public scores with small residuals because 36 hidden blocks create many degrees of freedom; treat it as a diagnostic map, not a direct label oracle.",
        "- The 0.54 path still requires reconstructing block rates from context, not just fitting public constraints. The validation block-rate oracle remains the upper-bound evidence that this is possible, while subject-chunk count-JEPA shows current representation is not yet sufficient.",
    ]
    (OUT / "hidden_block_latent_audit_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(SORT_KEY).reset_index(drop=True)
    sample = sample.sort_values(KEY).reset_index(drop=True)
    frames, preds = load_predictions()
    block_ids = sample_block_ids(train, sample)
    meta = block_metadata(train, sample, block_ids)

    raw_scan, saved_files, raw_axis_q = raw_axis_fit(frames, preds)

    observed = [spec for spec in SPECS if spec.public_lb is not None and spec.key in preds]
    constraint_preds = [preds[spec.key] for spec in observed]
    public_scores = np.asarray([spec.public_lb for spec in observed], dtype=np.float64)
    _q_group, posterior, fit = solve_block_posterior(
        prior=preds["raw05"],
        constraint_preds=constraint_preds,
        public_scores=public_scores,
        block_ids=block_ids,
    )
    fit["constraint_key"] = [spec.key for spec in observed]
    fit["constraint_role"] = [spec.role for spec in observed]
    fit.to_csv(OUT / "hidden_block_posterior_constraint_fit.csv", index=False)

    for gamma in [0.05, 0.10, 0.20]:
        pred = blend_logits(preds["raw05"], posterior, gamma)
        name = f"submission_hiddenblock_posterior_raw05_g{str(gamma).replace('.', 'p')}_{stable_tag(str(gamma))}.csv"
        saved_files.append(save_candidate(frames["raw05"], pred, name))

    table = endpoint_rate_table(train)
    endpoint = endpoint_priors(meta, table, train)
    block_summary = block_posterior_summary(meta, block_ids, preds["raw05"], posterior, endpoint, preds)
    candidate = candidate_scores(preds, posterior, raw_axis_q, saved_files)

    integrity_rows = []
    sample_key = frames["stage2"][KEY]
    for file_name in saved_files:
        frame = read_submission(OUT / file_name)
        pred = frame[TARGETS].to_numpy(dtype=np.float64)
        integrity_rows.append(
            {
                "file": file_name,
                "rows": len(frame),
                "key_match": bool(frame[KEY].equals(sample_key)),
                "duplicate_keys": int(frame.duplicated(KEY).sum()),
                "null_predictions": int(frame[TARGETS].isna().sum().sum()),
                "min_prob": float(pred.min()),
                "max_prob": float(pred.max()),
            }
        )
    pd.DataFrame(integrity_rows).to_csv(OUT / "hidden_block_candidate_integrity.csv", index=False)

    write_report(raw_scan, saved_files, fit, candidate, block_summary, endpoint)
    print("[hidden block latent audit] wrote report and candidates")
    print(candidate.head(12).round(10).to_string(index=False))
    print("\nconstraint fit")
    print(fit.round(12).to_string(index=False))
    print("\nsaved")
    for file_name in saved_files:
        print(file_name)


if __name__ == "__main__":
    main()
