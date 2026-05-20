from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-6


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values.astype(float), EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -40.0, 40.0)))


def bce_soft(y: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, EPS, 1.0 - EPS)
    return float(np.mean(-(y * np.log(p) + (1.0 - y) * np.log1p(-p))))


def read_submission(path: str | Path, sample: pd.DataFrame, name: str) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if list(frame.columns) != list(sample.columns):
        raise ValueError(f"{name}: columns differ from sample")
    if frame.shape != sample.shape:
        raise ValueError(f"{name}: shape differs from sample")
    if not frame[KEY_COLUMNS].astype(str).equals(sample[KEY_COLUMNS].astype(str)):
        raise ValueError(f"{name}: key rows differ from sample")
    values = frame[TARGET_COLUMNS].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError(f"{name}: non-finite predictions")
    if values.min() < 0.0 or values.max() > 1.0:
        raise ValueError(f"{name}: predictions outside [0, 1]")
    return frame


def values_to_submission(sample: pd.DataFrame, values: np.ndarray) -> pd.DataFrame:
    out = sample.copy()
    clipped = np.clip(values, 1e-5, 1.0 - 1e-5)
    for i, target in enumerate(TARGET_COLUMNS):
        out[target] = clipped[:, i]
    return out


def parse_sources(items: list[str]) -> list[tuple[str, Path]]:
    sources = []
    for item in items:
        if ":" not in item:
            raise ValueError("--source must be name:path")
        name, path = item.split(":", 1)
        sources.append((name, Path(path)))
    return sources


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def blend(base: np.ndarray, source: np.ndarray, weight: float, mode: str, direction: str) -> np.ndarray:
    sign = 1.0 if direction == "toward" else -1.0
    if mode == "prob":
        return np.clip(base + sign * weight * (source - base), 1e-5, 1.0 - 1e-5)
    if mode == "logit":
        return sigmoid(logit(base) + sign * weight * (logit(source) - logit(base)))
    raise ValueError(f"Unknown blend mode: {mode}")


def add_candidate(
    rows: list[dict[str, object]],
    output_dir: Path,
    sample: pd.DataFrame,
    name: str,
    values: np.ndarray,
    posterior: np.ndarray,
    references: dict[str, np.ndarray],
) -> None:
    path = output_dir / name
    submission = values_to_submission(sample, values)
    submission.to_csv(path, index=False)
    clipped = submission[TARGET_COLUMNS].to_numpy(dtype=float)
    row: dict[str, object] = {
        "file": name,
        "sha256": sha256_file(path),
        "pseudo_public_bce": bce_soft(posterior, clipped),
        "min": float(clipped.min()),
        "p01": float(np.quantile(clipped, 0.01)),
        "mean": float(clipped.mean()),
        "p99": float(np.quantile(clipped, 0.99)),
        "max": float(clipped.max()),
        "abs_logit_mean": float(np.mean(np.abs(logit(clipped)))),
    }
    for ref_name, ref_values in references.items():
        row[f"mad_from_{ref_name}"] = float(np.mean(np.abs(clipped - ref_values)))
        row[f"corr_{ref_name}"] = float(np.corrcoef(clipped.ravel(), ref_values.ravel())[0, 1])
    rows.append(row)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    text_df = df.copy()
    for col in text_df.columns:
        if pd.api.types.is_float_dtype(text_df[col]):
            text_df[col] = text_df[col].map(lambda x: f"{x:.6f}")
        else:
            text_df[col] = text_df[col].astype(str)
    lines = [
        "| " + " | ".join(text_df.columns) + " |",
        "| " + " | ".join(["---"] * len(text_df.columns)) + " |",
    ]
    for _, row in text_df.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in text_df.columns) + " |")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for old_path in output_dir.glob("submission_*.csv"):
        old_path.unlink()

    sample = pd.read_csv(args.sample_path)
    base = read_submission(args.base_submission, sample, "base")
    v76 = read_submission(args.v76_submission, sample, "v76")
    posterior = pd.read_csv(args.posterior_values)[TARGET_COLUMNS].to_numpy(dtype=float)

    base_values = base[TARGET_COLUMNS].to_numpy(dtype=float)
    v76_values = v76[TARGET_COLUMNS].to_numpy(dtype=float)
    rows: list[dict[str, object]] = []
    sources = [(name, read_submission(path, sample, name)[TARGET_COLUMNS].to_numpy(dtype=float)) for name, path in parse_sources(args.sources)]

    references = {"base": base_values, "v76": v76_values}
    for source_name, source_values in sources:
        references[source_name] = source_values
        add_candidate(rows, output_dir, sample, f"submission_exact_{source_name}.csv", source_values, posterior, references)
        for mode in ["prob", "logit"]:
            for direction in ["toward", "away"]:
                for weight in parse_float_list(args.weights):
                    tag = str(weight).replace(".", "p")
                    values = blend(base_values, source_values, weight, mode=mode, direction=direction)
                    add_candidate(
                        rows,
                        output_dir,
                        sample,
                        f"submission_base_{direction}_{source_name}_{mode}_w{tag}.csv",
                        values,
                        posterior,
                        references,
                    )

    manifest = pd.DataFrame(rows).sort_values(["pseudo_public_bce", "mad_from_base"]).reset_index(drop=True)
    manifest.to_csv(output_dir / "manifest.csv", index=False)
    top = manifest.head(args.readme_top)
    source_names = ", ".join(name for name, _ in sources)
    readme = [
        "# External Source Public-Calibrated Candidates",
        "",
        "These files test whether label-free external source predictions can move the public-calibrated anchor.",
        f"Sources: {source_names}.",
        "Because the external sources are weak under local OOF, upload candidates should be tiny moves from a public-calibrated anchor, not raw source submissions.",
        "",
        "Top candidates by fitted public-posterior BCE:",
        "",
        dataframe_to_markdown(top),
        "",
    ]
    (output_dir / "README.md").write_text("\n".join(readme), encoding="utf-8")
    print(top[["file", "pseudo_public_bce", "mad_from_base", "corr_base", "min", "max", "abs_logit_mean"]].to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build tiny public-calibrated blends from external environment sources.")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-submission", default="outputs/public_lb_pseudolabel_calibration/submission_01_exact_v77_recommended.csv")
    parser.add_argument("--v76-submission", default="outputs/public_lb_pseudolabel_calibration/submission_02_exact_v76_public_anchor_reconstructed.csv")
    parser.add_argument("--posterior-values", default="outputs/public_lb_pseudolabel_calibration/posterior_values_only.csv")
    parser.add_argument("--source", dest="sources", action="append", required=True)
    parser.add_argument("--weights", default="0.005,0.01,0.02,0.03,0.05")
    parser.add_argument("--output-dir", default="outputs/external_environment_public_candidates")
    parser.add_argument("--readme-top", type=int, default=20)
    return parser.parse_args()


if __name__ == "__main__":
    main()
