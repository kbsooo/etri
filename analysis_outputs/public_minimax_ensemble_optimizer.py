from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

from public_subset_sensitivity_audit import build_masks, load_sub  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-5

Q_SCENARIOS = [
    "submission_public_entropyproj_public2d0_g050.csv",
    "submission_public_entropyproj_public2d0_g075.csv",
    "submission_public_entropyproj_public2d0_g100.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s3_s4_g075.csv",
]
BASELINE_PRIOR = "submission_public2dblend_budget0p0.csv"
BASE_FILES = [
    BASELINE_PRIOR,
    "submission_public_entropyproj_public2d0_g050.csv",
    "submission_public_entropyproj_public2d0_g075.csv",
    "submission_public_entropyproj_public2d0_g100.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g050.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g075.csv",
]


@dataclass
class EvalResult:
    score: float
    mean_expected: float
    p90_expected: float
    mean_regret: float
    p90_regret: float
    p95_regret: float
    max_regret: float
    mean_delta_vs_prior: float
    p90_delta_vs_prior: float
    win_rate_vs_prior: float


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def ce_row_loss(q: np.ndarray, p: np.ndarray) -> np.ndarray:
    qq = clip(q)
    pp = clip(p)
    return (-(qq * np.log(pp) + (1.0 - qq) * np.log(1.0 - pp))).mean(axis=1)


def normalized_mask_matrix(sample: pd.DataFrame) -> np.ndarray:
    masks = [m for m in build_masks(sample) if m["mask_kind"] != "all"]
    mat = np.zeros((len(masks), len(sample)), dtype=np.float64)
    for i, rec in enumerate(masks):
        mask = rec["mask"]
        assert isinstance(mask, np.ndarray)
        mat[i, mask] = 1.0 / float(mask.sum())
    return mat


def candidate_files() -> list[str]:
    files = []
    for f in BASE_FILES:
        if (OUT / f).exists() and f not in files:
            files.append(f)
    robustness_path = OUT / "public_posterior_scenario_robustness_summary.csv"
    if robustness_path.exists():
        for f in pd.read_csv(robustness_path)["file"].head(14).tolist():
            if (OUT / f).exists() and f not in files:
                files.append(f)
    return files


def weights_to_tag(weights: np.ndarray) -> str:
    active = int((weights > 1e-4).sum())
    h = abs(hash(tuple(np.round(weights, 5)))) % 1_000_000
    return f"a{active}_h{h:06d}"


def evaluate(
    weights: np.ndarray,
    pred_stack: np.ndarray,
    q_scenarios: list[np.ndarray],
    mask_mat: np.ndarray,
    best_scores: np.ndarray,
    prior_scores: np.ndarray,
) -> EvalResult:
    p = clip(np.tensordot(weights, pred_stack, axes=(0, 0)))
    scenario_scores = []
    for q in q_scenarios:
        scenario_scores.append(mask_mat @ ce_row_loss(q, p))
    scores = np.concatenate(scenario_scores)
    regret = scores - best_scores
    delta_prior = scores - prior_scores
    mean_expected = float(scores.mean())
    p90_expected = float(np.quantile(scores, 0.90))
    mean_regret = float(regret.mean())
    p90_regret = float(np.quantile(regret, 0.90))
    p95_regret = float(np.quantile(regret, 0.95))
    max_regret = float(regret.max())
    mean_delta_vs_prior = float(delta_prior.mean())
    p90_delta_vs_prior = float(np.quantile(delta_prior, 0.90))
    win_rate_vs_prior = float((delta_prior < 0).mean())
    score = (
        mean_expected
        + 2.0 * mean_regret
        + 1.0 * p90_regret
        + 0.25 * p95_regret
        + 0.05 * max_regret
        + 0.10 * max(p90_delta_vs_prior, 0.0)
        + 0.01 * max(0.80 - win_rate_vs_prior, 0.0)
    )
    return EvalResult(
        score,
        mean_expected,
        p90_expected,
        mean_regret,
        p90_regret,
        p95_regret,
        max_regret,
        mean_delta_vs_prior,
        p90_delta_vs_prior,
        win_rate_vs_prior,
    )


def dirichlet_search(
    pred_stack: np.ndarray,
    q_scenarios: list[np.ndarray],
    mask_mat: np.ndarray,
    best_scores: np.ndarray,
    prior_scores: np.ndarray,
    seed: int = 260526,
) -> list[tuple[np.ndarray, EvalResult, str]]:
    rng = np.random.default_rng(seed)
    n = pred_stack.shape[0]
    starts: list[tuple[np.ndarray, str]] = []
    for i in range(n):
        w = np.zeros(n)
        w[i] = 1.0
        starts.append((w, f"single_{i}"))
    for alpha, count in [(0.15, 3000), (0.30, 3000), (0.70, 2000), (1.50, 1000)]:
        for _ in range(count):
            w = rng.dirichlet(np.full(n, alpha))
            starts.append((w, f"dirichlet_{alpha}"))
    for k in [2, 3, 4, 5]:
        for _ in range(1500):
            idx = rng.choice(n, size=k, replace=False)
            local = rng.dirichlet(np.full(k, 0.7))
            w = np.zeros(n)
            w[idx] = local
            starts.append((w, f"sparse{k}"))

    best: list[tuple[np.ndarray, EvalResult, str]] = []
    for w, source in starts:
        ev = evaluate(w, pred_stack, q_scenarios, mask_mat, best_scores, prior_scores)
        best.append((w, ev, source))
    best.sort(key=lambda x: (x[1].score, x[1].mean_expected))
    return best[:120]


def local_refine(
    candidates: list[tuple[np.ndarray, EvalResult, str]],
    pred_stack: np.ndarray,
    q_scenarios: list[np.ndarray],
    mask_mat: np.ndarray,
    best_scores: np.ndarray,
    prior_scores: np.ndarray,
) -> list[tuple[np.ndarray, EvalResult, str]]:
    refined = []
    n = pred_stack.shape[0]
    for start_w, start_ev, source in candidates[:30]:
        w = start_w.copy()
        best_ev = start_ev
        step = 0.20
        while step >= 0.0025:
            improved = False
            for i in range(n):
                for j in range(n):
                    if i == j or w[i] <= step * 0.25:
                        continue
                    move = min(step, w[i])
                    cand = w.copy()
                    cand[i] -= move
                    cand[j] += move
                    ev = evaluate(cand, pred_stack, q_scenarios, mask_mat, best_scores, prior_scores)
                    if ev.score < best_ev.score - 1e-12:
                        w = cand
                        best_ev = ev
                        improved = True
            if not improved:
                step *= 0.5
        refined.append((w, best_ev, f"{source}_refined"))
    combined = candidates + refined
    combined.sort(key=lambda x: (x[1].score, x[1].mean_expected))
    dedup: list[tuple[np.ndarray, EvalResult, str]] = []
    seen = set()
    for w, ev, source in combined:
        key = tuple(np.round(w, 4))
        if key not in seen:
            dedup.append((w, ev, source))
            seen.add(key)
        if len(dedup) >= 80:
            break
    return dedup


def save_candidate(
    name: str,
    weights: np.ndarray,
    files: list[str],
    pred_stack: np.ndarray,
    oof_stack: np.ndarray,
    sample: pd.DataFrame,
) -> tuple[str, str]:
    sub_prob = clip(np.tensordot(weights, pred_stack, axes=(0, 0)))
    oof_prob = clip(np.tensordot(weights, oof_stack, axes=(0, 0)))
    out = load_sub(files[0])[KEY].copy()
    out[TARGETS] = sub_prob
    out = out.sort_values(KEY).reset_index(drop=True)
    if not out[KEY].equals(sample[KEY]):
        raise ValueError("sample key mismatch")
    sub_file = f"submission_public_minimaxens_{name}.csv"
    oof_file = f"final_public_minimaxens_{name}_oof.npy"
    out.to_csv(OUT / sub_file, index=False)
    np.save(OUT / oof_file, oof_prob)
    return sub_file, oof_file


def oof_name_for_submission(file_name: str) -> str | None:
    if file_name == BASELINE_PRIOR:
        return "final_public2dblend_budget0p0_oof.npy"
    if file_name.startswith("submission_public_entropyproj_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_public_entropytm_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    return None


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    mask_mat = normalized_mask_matrix(sample)
    files = candidate_files()
    pred_stack = np.stack([load_sub(f)[TARGETS].to_numpy(dtype=float) for f in files], axis=0)
    prior_pred = load_sub(BASELINE_PRIOR)[TARGETS].to_numpy(dtype=float)
    q_scenarios = [load_sub(f)[TARGETS].to_numpy(dtype=float) for f in Q_SCENARIOS if (OUT / f).exists()]

    all_candidate_scores = []
    prior_scores = []
    for q in q_scenarios:
        scenario_file_scores = []
        for p in pred_stack:
            scenario_file_scores.append(mask_mat @ ce_row_loss(q, p))
        all_candidate_scores.append(np.vstack(scenario_file_scores).min(axis=0))
        prior_scores.append(mask_mat @ ce_row_loss(q, prior_pred))
    best_scores = np.concatenate(all_candidate_scores)
    prior_scores_vec = np.concatenate(prior_scores)

    top = dirichlet_search(pred_stack, q_scenarios, mask_mat, best_scores, prior_scores_vec)
    top = local_refine(top, pred_stack, q_scenarios, mask_mat, best_scores, prior_scores_vec)

    rows = []
    for rank, (w, ev, source) in enumerate(top, start=1):
        row: dict[str, float | int | str] = {
            "rank": rank,
            "source": source,
            "active_weights": int((w > 1e-4).sum()),
            "score": ev.score,
            "mean_expected": ev.mean_expected,
            "p90_expected": ev.p90_expected,
            "mean_regret": ev.mean_regret,
            "p90_regret": ev.p90_regret,
            "p95_regret": ev.p95_regret,
            "max_regret": ev.max_regret,
            "mean_delta_vs_prior": ev.mean_delta_vs_prior,
            "p90_delta_vs_prior": ev.p90_delta_vs_prior,
            "win_rate_vs_prior": ev.win_rate_vs_prior,
        }
        for file_name, weight in zip(files, w, strict=True):
            if weight > 1e-4:
                row[f"w::{file_name}"] = float(weight)
        rows.append(row)
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "public_minimax_ensemble_summary.csv", index=False)

    oof_arrays = []
    usable = []
    for f in files:
        oof_name = oof_name_for_submission(f)
        if oof_name is None or not (OUT / oof_name).exists():
            usable.append(False)
            oof_arrays.append(np.zeros((450, len(TARGETS))))
        else:
            usable.append(True)
            oof_arrays.append(np.load(OUT / oof_name))
    oof_stack = np.stack(oof_arrays, axis=0)

    selected_rows = []
    saved = 0
    for rank, (w, ev, source) in enumerate(top, start=1):
        if not all((w[i] <= 1e-10) or usable[i] for i in range(len(files))):
            continue
        if saved >= 8:
            break
        tag = weights_to_tag(w)
        sub_file, oof_file = save_candidate(f"r{rank:02d}_{tag}", w, files, pred_stack, oof_stack, sample)
        selected_rows.append(
            {
                "file": sub_file,
                "oof_file": oof_file,
                "rank": rank,
                "source": source,
                "score": ev.score,
                "mean_expected": ev.mean_expected,
                "mean_regret": ev.mean_regret,
                "p90_regret": ev.p90_regret,
                "p95_regret": ev.p95_regret,
                "max_regret": ev.max_regret,
                "mean_delta_vs_prior": ev.mean_delta_vs_prior,
                "win_rate_vs_prior": ev.win_rate_vs_prior,
                "active_weights": int((w > 1e-4).sum()),
                "weights": ";".join(f"{files[i]}={w[i]:.6f}" for i in np.where(w > 1e-4)[0]),
            }
        )
        saved += 1
    selected = pd.DataFrame(selected_rows)
    selected.to_csv(OUT / "public_minimax_ensemble_selected.csv", index=False)

    report = []
    report.append("# Public Minimax Ensemble Report\n")
    report.append(
        "Convex ensembles were optimized against six public-posterior scenarios and simulated public row subsets.\n"
    )
    cols = [
        "rank",
        "source",
        "active_weights",
        "score",
        "mean_expected",
        "mean_regret",
        "p90_regret",
        "p95_regret",
        "max_regret",
        "mean_delta_vs_prior",
        "win_rate_vs_prior",
    ]
    report.append("\n## Top Optimizer Rows\n")
    report.append("```\n" + summary[cols].head(20).round(9).to_string(index=False) + "\n```")
    report.append("\n\n## Saved Submissions\n")
    report.append("```\n" + selected.head(8).round(9).to_string(index=False) + "\n```")
    (OUT / "public_minimax_ensemble_report.md").write_text("".join(report))

    print("[minimax ensemble summary]")
    print(summary[cols].head(20).round(9).to_string(index=False))
    print("\n[saved]")
    print(selected.head(8).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
