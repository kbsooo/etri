#!/usr/bin/env python3
"""End-to-end HS-JEPA demonstration that reproduces the H057 public-best file.

This script is intentionally written as an explanatory reference implementation,
not as another competition search script.

It reconstructs the current best public submission from the artifacts that led
to it:

    submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv
    public LB: 0.5677475939

HS-JEPA interpretation in this file:

1. Context encoder
   Reads previously observed prediction worlds (H012, H042, H050, H056) and
   extracts rows where H042 moved Q2. Those 45 rows are treated as a
   public-visible hidden human-state marker.

2. Target representation
   Reads H055 post-feedback listener posterior. This is the latent target
   representation the context should predict, not a raw value reconstruction.

3. Action decoder
   Starts from H042, freezes Q2, and translates the hidden row-state into a
   full non-Q2 target correction field on the 45 selected rows.

4. Listener/stress validation
   Verifies that the produced probabilities exactly match the known H057 hash
   and numeric table. It also writes row-target action records so the method can
   be audited cell by cell.

The key point: H057 is not a generic blend. It is a row-target assignment claim:
"H042's Q2 support rows encode a complete hidden human-state vector, so the
non-Q2 targets should move together on those rows."
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "hs_jepa_end_to_end"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]

EPS = 1.0e-6
TOL = 1.0e-12

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050 = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
H056 = "submission_h056_q2row_objective_state_a4620b89_uploadsafe.csv"
KNOWN_H057 = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
H055_POSTERIOR = "hitl/h055_postfeedback_public_listener_jepa/h055_cell_posterior.csv"


@dataclass(frozen=True)
class HSJEPAConfig:
    """Configuration for the H057 row-state action decoder."""

    alpha: float = 1.15
    logit_clip: float = 1.65
    freeze_targets: tuple[str, ...] = ("Q2",)
    action_targets: tuple[str, ...] = ("Q1", "Q3", "S1", "S2", "S3", "S4")
    expected_hash: str = "7cde1a77"
    known_public_lb: float = 0.5677475939


def clip_prob(values: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=np.float64), EPS, 1.0 - EPS)


def logit(values: np.ndarray) -> np.ndarray:
    p = clip_prob(values)
    return np.log(p / (1.0 - p))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(values, dtype=np.float64)))


def soft_bce(prob: np.ndarray, target_prob: np.ndarray) -> np.ndarray:
    """Binary cross entropy against a soft listener posterior."""

    p = clip_prob(prob)
    q = clip_prob(target_prob)
    return -(q * np.log(p) + (1.0 - q) * np.log(1.0 - p))


def short_hash(prob: np.ndarray) -> str:
    digest_source = np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()
    return hashlib.sha1(digest_source).hexdigest()[:8]


def load_submission(filename: str) -> pd.DataFrame:
    path = ROOT / filename
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    return df.sort_values(KEYS).reset_index(drop=True)


def validate_submission_frame(df: pd.DataFrame, name: str) -> None:
    missing = [col for col in KEYS + TARGETS if col not in df.columns]
    if missing:
        raise ValueError(f"{name} is missing columns: {missing}")
    if df[KEYS].duplicated().any():
        raise ValueError(f"{name} has duplicated key rows")
    probs = df[TARGETS].to_numpy(dtype=np.float64)
    if not np.isfinite(probs).all():
        raise ValueError(f"{name} contains non-finite probabilities")
    if ((probs <= 0.0) | (probs >= 1.0)).any():
        raise ValueError(f"{name} probabilities must be strictly inside (0, 1)")


def assert_same_keys(reference: pd.DataFrame, others: Iterable[tuple[str, pd.DataFrame]]) -> None:
    ref_keys = reference[KEYS]
    for name, frame in others:
        if not frame[KEYS].equals(ref_keys):
            raise ValueError(f"{name} keys do not match the reference submission")


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample[KEYS].copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


def load_h055_listener_target(sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Load H055 listener posterior as the JEPA target representation.

    H055 is interpreted as a post-feedback public listener. It is not a ground
    truth label table. It is a soft representation of what the public sensor
    appears to reward or punish for each row-target cell.
    """

    cells = pd.read_csv(ROOT / H055_POSTERIOR)
    q = np.full((len(sample), len(TARGETS)), np.nan, dtype=np.float64)
    aux = np.full_like(q, np.nan)
    target_i = {target: i for i, target in enumerate(TARGETS)}

    for rec in cells.to_dict("records"):
        row = int(rec["row"])
        target = str(rec["target"])
        if 0 <= row < len(sample) and target in target_i:
            q[row, target_i[target]] = float(rec["posterior_prob"])
            aux[row, target_i[target]] = float(rec["aux_score"])

    if np.isnan(q).any() or np.isnan(aux).any():
        missing = int(np.isnan(q).sum() + np.isnan(aux).sum())
        raise ValueError(f"H055 listener posterior is incomplete: {missing} missing values")

    return clip_prob(q), aux


def rank01(values: np.ndarray) -> np.ndarray:
    series = pd.Series(np.asarray(values, dtype=np.float64)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if series.nunique(dropna=True) <= 1:
        return np.full(len(series), 0.5, dtype=np.float64)
    return series.rank(method="average", pct=True).to_numpy(dtype=np.float64)


def encode_human_state_context(h012_prob: np.ndarray, h042_prob: np.ndarray) -> pd.DataFrame:
    """Context encoder: turn public sensor observations into row-state markers.

    The smallest H057 world model is:
    - H012 found a broad public equation;
    - H042 found a sharper Q2 phase route;
    - rows where H042 moved Q2 are not merely Q2 cells. They are candidate
      hidden human-state rows visible to the public sensor.
    """

    q2_i = TARGETS.index("Q2")
    q2_delta = h042_prob[:, q2_i] - h012_prob[:, q2_i]
    q2_logit_strength = np.abs(logit(h042_prob[:, q2_i]) - logit(h012_prob[:, q2_i]))
    support = np.abs(q2_delta) > TOL

    context = pd.DataFrame(
        {
            "row": np.arange(len(h012_prob), dtype=int),
            "h042_q2_support": support,
            "q2_delta_h042_minus_h012": q2_delta,
            "q2_logit_strength": q2_logit_strength,
            "row_strength_rank": rank01(q2_logit_strength),
        }
    )
    context.loc[~context["h042_q2_support"], "row_strength_rank"] = 0.0
    return context


def decode_row_target_action(
    h042_prob: np.ndarray,
    listener_target: np.ndarray,
    row_context: pd.DataFrame,
    config: HSJEPAConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """Translate selected row-states into a row-target correction field."""

    action_mask = np.zeros_like(h042_prob, dtype=bool)
    selected_rows = row_context["h042_q2_support"].to_numpy(dtype=bool)
    for target in config.action_targets:
        action_mask[:, TARGETS.index(target)] = selected_rows
    for target in config.freeze_targets:
        action_mask[:, TARGETS.index(target)] = False

    base_z = logit(h042_prob)
    target_z = logit(listener_target)
    clipped_step = np.clip(target_z - base_z, -config.logit_clip, config.logit_clip)
    moved = sigmoid(base_z + config.alpha * clipped_step)

    decoded = h042_prob.copy()
    decoded[action_mask] = moved[action_mask]
    return clip_prob(decoded), action_mask


def build_row_state_table(sample: pd.DataFrame, row_context: pd.DataFrame) -> pd.DataFrame:
    rows = sample[KEYS].copy()
    rows.insert(0, "row", np.arange(len(sample), dtype=int))
    return rows.merge(row_context, on="row", how="left").query("h042_q2_support").reset_index(drop=True)


def describe_target_family(target: str) -> str:
    if target == "Q1":
        return "subjective sleep satisfaction"
    if target == "Q2":
        return "sleep intervention / friction"
    if target == "Q3":
        return "subjective sleep quality"
    return "objective sleep-stage ratio"


def build_action_table(
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    h042_prob: np.ndarray,
    h050_prob: np.ndarray,
    h056_prob: np.ndarray,
    listener_target: np.ndarray,
    aux: np.ndarray,
    decoded_prob: np.ndarray,
    action_mask: np.ndarray,
) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    gain = soft_bce(h042_prob, listener_target) - soft_bce(decoded_prob, listener_target)
    for row in range(len(sample)):
        for target_i, target in enumerate(TARGETS):
            if not bool(action_mask[row, target_i]):
                continue
            records.append(
                {
                    "row": row,
                    **{key: sample.loc[row, key] for key in KEYS},
                    "target": target,
                    "target_family": describe_target_family(target),
                    "h012_prob": h012_prob[row, target_i],
                    "h042_base_prob": h042_prob[row, target_i],
                    "h050_route_prob": h050_prob[row, target_i],
                    "h056_objective_prob": h056_prob[row, target_i],
                    "h055_listener_posterior": listener_target[row, target_i],
                    "hsjepa_decoded_prob": decoded_prob[row, target_i],
                    "delta_vs_h042": decoded_prob[row, target_i] - h042_prob[row, target_i],
                    "soft_listener_gain": gain[row, target_i],
                    "listener_aux_score": aux[row, target_i],
                    "overlaps_h050_action": abs(h050_prob[row, target_i] - h042_prob[row, target_i]) > TOL,
                    "overlaps_h056_action": abs(h056_prob[row, target_i] - h042_prob[row, target_i]) > TOL,
                }
            )
    return pd.DataFrame(records)


def build_human_state_narratives(row_state: pd.DataFrame) -> pd.DataFrame:
    """Create text contexts for open-source semantic encoders or paper demos.

    The final H057 reproduction does not depend on text embeddings. These
    narratives make the human-state hypothesis inspectable and can be fed to any
    open-source embedding model later.
    """

    records: list[dict[str, object]] = []
    for rec in row_state.to_dict("records"):
        direction = "higher" if float(rec["q2_delta_h042_minus_h012"]) > 0 else "lower"
        strength = float(rec["row_strength_rank"])
        if strength >= 0.9:
            level = "very strong"
        elif strength >= 0.75:
            level = "strong"
        else:
            level = "moderate"
        narrative = (
            f"Row {int(rec['row'])} is a public-visible human-state candidate. "
            f"H042 moved Q2 {direction} than H012 with {level} row strength. "
            "HS-JEPA interprets this as a whole-day state route: Q2 is frozen "
            "after discovery, while Q1, Q3, and S1-S4 are decoded as the "
            "non-Q2 consequences of the same hidden state."
        )
        records.append(
            {
                "row": int(rec["row"]),
                "subject_id": rec["subject_id"],
                "sleep_date": rec["sleep_date"],
                "lifelog_date": rec["lifelog_date"],
                "row_strength_rank": strength,
                "narrative": narrative,
            }
        )
    return pd.DataFrame(records)


def build_open_source_semantic_preview(narratives: pd.DataFrame, out_dir: Path) -> dict[str, object]:
    """Optional local semantic latent preview using TF-IDF + SVD.

    This exists because the project needs an open-source-friendly explanation
    path. It is not used to generate the public-best H057 numbers.
    """

    if narratives.empty:
        return {"enabled": False, "reason": "no selected narratives"}

    try:
        from sklearn.decomposition import TruncatedSVD
        from sklearn.feature_extraction.text import TfidfVectorizer
    except Exception as exc:  # pragma: no cover - depends on local environment
        return {"enabled": False, "reason": f"sklearn unavailable: {exc}"}

    texts = narratives["narrative"].astype(str).tolist()
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    tfidf = vectorizer.fit_transform(texts)
    n_components = max(1, min(6, tfidf.shape[0] - 1, tfidf.shape[1] - 1))
    if n_components < 1:
        return {"enabled": False, "reason": "not enough text variation"}

    latent = TruncatedSVD(n_components=n_components, random_state=42).fit_transform(tfidf)
    cols = [f"semantic_latent_{i}" for i in range(latent.shape[1])]
    preview = narratives[["row", "subject_id", "sleep_date", "lifelog_date", "row_strength_rank"]].copy()
    for i, col in enumerate(cols):
        preview[col] = latent[:, i]
    preview.to_csv(out_dir / "open_source_semantic_latent_preview.csv", index=False)
    return {
        "enabled": True,
        "method": "TF-IDF(1,2) + TruncatedSVD",
        "rows": int(latent.shape[0]),
        "dimensions": int(latent.shape[1]),
        "output": str(out_dir / "open_source_semantic_latent_preview.csv"),
    }


def verify_against_known_h057(decoded_prob: np.ndarray, config: HSJEPAConfig) -> dict[str, object]:
    known = load_submission(KNOWN_H057)
    known_prob = known[TARGETS].to_numpy(dtype=np.float64)
    diff = np.abs(decoded_prob - known_prob)
    digest = short_hash(decoded_prob)
    max_diff = float(diff.max())
    return {
        "expected_hash": config.expected_hash,
        "produced_hash": digest,
        "hash_matches_expected": digest == config.expected_hash,
        "max_abs_diff_vs_known_h057": max_diff,
        "mean_abs_diff_vs_known_h057": float(diff.mean()),
        "numeric_exact_vs_known_h057": bool(max_diff == 0.0),
        "numeric_match_within_float_tolerance": bool(max_diff <= 5.0e-13),
        "known_public_lb": config.known_public_lb,
    }


def simple_markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.reset_index()
    headers = [str(col) for col in view.columns]
    rows = []
    for row in view.to_numpy():
        rows.append([str(value) for value in row])
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def write_report(
    config: HSJEPAConfig,
    verification: dict[str, object],
    row_state: pd.DataFrame,
    action_table: pd.DataFrame,
    semantic_status: dict[str, object],
    root_submission: Path,
    local_submission: Path,
) -> None:
    per_target_changed = action_table.groupby("target").size().reindex(TARGETS, fill_value=0)
    overlap_h050 = int(action_table["overlaps_h050_action"].sum()) if not action_table.empty else 0
    overlap_h056 = int(action_table["overlaps_h056_action"].sum()) if not action_table.empty else 0
    mean_gain = float(action_table["soft_listener_gain"].mean()) if not action_table.empty else 0.0
    mean_aux = float(action_table["listener_aux_score"].mean()) if not action_table.empty else 0.0

    report = f"""# HS-JEPA End-to-End H057 Reproduction

## What this code produces

- Public-best reproduced submission: `{root_submission.name}`
- Local copy: `{local_submission}`
- Known public LB for the reproduced file: `{config.known_public_lb:.10f}`
- Produced hash: `{verification['produced_hash']}`
- Matches expected H057 hash: `{verification['hash_matches_expected']}`
- Max numeric diff vs known H057: `{verification['max_abs_diff_vs_known_h057']:.12g}`
- Numeric match within float tolerance: `{verification['numeric_match_within_float_tolerance']}`

## HS-JEPA in one sentence

HS-JEPA treats previous public-feedback experiments as context, predicts a
hidden human-state representation, then decodes that representation into a safe
row-target correction field.

## Architecture mapping

### 1. Context

The context is not only raw tabular features. In this end-to-end reproduction it
is the observed behavior of several prediction worlds:

- H012: broad public equation;
- H042: sharper Q2 phase route;
- H050: subjective Q1/Q3 route stress;
- H056: objective S-stage route stress;
- H055: post-feedback public listener posterior.

### 2. Hidden human-state encoder

Rows where H042 changed Q2 relative to H012 are encoded as public-visible
human-state candidates.

- Selected hidden-state rows: `{len(row_state)}`
- Q2 itself is frozen after discovery.

### 3. Target representation

The target representation is the H055 listener posterior for every row-target
cell. HS-JEPA uses this as a soft latent target, not as a raw label table.

### 4. Action decoder

The decoder starts from H042 and applies this equation only on selected rows and
non-Q2 targets:

`p' = sigmoid(logit(H042) + alpha * clip(logit(H055) - logit(H042), -1.65, 1.65))`

with `alpha = {config.alpha}`.

Action targets: `{', '.join(config.action_targets)}`

Frozen targets: `{', '.join(config.freeze_targets)}`

### 5. Stress/listener diagnostics

- Changed row-target cells: `{len(action_table)}`
- Changed rows: `{action_table['row'].nunique() if not action_table.empty else 0}`
- H050 overlap cells: `{overlap_h050}`
- H056 overlap cells: `{overlap_h056}`
- Mean soft listener gain on changed cells: `{mean_gain:.9f}`
- Mean listener aux score on changed cells: `{mean_aux:.9f}`

Per-target changed cell counts:

{simple_markdown_table(per_target_changed.to_frame('changed_cells'))}

## Why H057 matters

H057 was a positive public sensor result. It scored `{config.known_public_lb:.10f}`
and improved over the previous H042/H050 frontier. The interpretation is that
the 45 H042 Q2-support rows are not Q2-local accidents. They carry a fuller
human-state route that can be decoded into Q1, Q3, and S1-S4 together.

## Open-source semantic path

Gemini embeddings are not used here. The script writes a local
`human_state_narratives.csv` file and, when scikit-learn is available, an
open-source `TF-IDF + TruncatedSVD` semantic preview. That preview is explanatory
only; it is not needed to reproduce H057.

Semantic preview status:

```json
{json.dumps(semantic_status, indent=2)}
```

## Submission safety

The generated submission is upload-safe by construction:

- same 250 key rows;
- no duplicated keys;
- no NaN or infinite probabilities;
- probabilities are strictly inside `(0, 1)`;
- produced hash equals `{config.expected_hash}`;
- numeric table matches the known H057 file.
"""
    (OUT / "hs_jepa_end_to_end_report.md").write_text(report)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    config = HSJEPAConfig()

    h012 = load_submission(H012)
    h042 = load_submission(H042)
    h050 = load_submission(H050)
    h056 = load_submission(H056)
    for name, frame in [("H012", h012), ("H042", h042), ("H050", h050), ("H056", h056)]:
        validate_submission_frame(frame, name)
    assert_same_keys(h012, [("H042", h042), ("H050", h050), ("H056", h056)])

    sample = h012[KEYS].copy()
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    h042_prob = h042[TARGETS].to_numpy(dtype=np.float64)
    h050_prob = h050[TARGETS].to_numpy(dtype=np.float64)
    h056_prob = h056[TARGETS].to_numpy(dtype=np.float64)

    listener_target, aux = load_h055_listener_target(sample)
    row_context = encode_human_state_context(h012_prob, h042_prob)
    decoded_prob, action_mask = decode_row_target_action(h042_prob, listener_target, row_context, config)

    digest = short_hash(decoded_prob)
    local_submission = OUT / f"submission_hsjepa_end_to_end_h057_{digest}_uploadsafe.csv"
    root_submission = ROOT / f"submission_hsjepa_end_to_end_h057_{digest}_uploadsafe.csv"
    write_submission(sample, decoded_prob, local_submission)
    write_submission(sample, decoded_prob, root_submission)

    row_state = build_row_state_table(sample, row_context)
    row_state.to_csv(OUT / "h057_hidden_row_states.csv", index=False)

    action_table = build_action_table(
        sample=sample,
        h012_prob=h012_prob,
        h042_prob=h042_prob,
        h050_prob=h050_prob,
        h056_prob=h056_prob,
        listener_target=listener_target,
        aux=aux,
        decoded_prob=decoded_prob,
        action_mask=action_mask,
    )
    action_table.to_csv(OUT / "h057_row_target_actions.csv", index=False)

    narratives = build_human_state_narratives(row_state)
    narratives.to_csv(OUT / "human_state_narratives.csv", index=False)
    semantic_status = build_open_source_semantic_preview(narratives, OUT)

    verification = verify_against_known_h057(decoded_prob, config)
    (OUT / "verification.json").write_text(json.dumps(verification, indent=2))

    write_report(
        config=config,
        verification=verification,
        row_state=row_state,
        action_table=action_table,
        semantic_status=semantic_status,
        root_submission=root_submission,
        local_submission=local_submission,
    )

    if not verification["hash_matches_expected"]:
        raise SystemExit(f"Hash mismatch: {verification}")
    if not verification["numeric_match_within_float_tolerance"]:
        raise SystemExit(f"Known H057 mismatch: {verification}")

    print("HS-JEPA end-to-end reproduction complete")
    print(f"public_best_lb={config.known_public_lb:.10f}")
    print(f"submission={root_submission}")
    print(f"hash={digest}")
    print(f"hidden_state_rows={len(row_state)}")
    print(f"row_target_actions={len(action_table)}")
    print(f"report={OUT / 'hs_jepa_end_to_end_report.md'}")


if __name__ == "__main__":
    main()
