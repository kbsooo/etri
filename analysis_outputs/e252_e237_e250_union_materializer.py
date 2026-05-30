#!/usr/bin/env python3
"""E252: materialize the E237/E250 Q3 union cell-set sensor.

E251 found that the union of E237 and E250 selected Q3 rollback cells passes
materialization stress more strongly than either parent. This script creates a
submission artifact for that exact union and audits schema/movement integrity.

The file is a public sensor for complementarity, not an OOF-certified successor
to E237.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e230_e224_support_tail_prune_audit as e230  # noqa: E402
import e237_cell_decisive_jepa_target as e237  # noqa: E402
import e251_e237_e250_cellset_contrast as e251  # noqa: E402


REPORT_OUT = OUT / "e252_e237_e250_union_materializer_report.md"
SCHEMA_OUT = OUT / "e252_e237_e250_union_schema_audit.csv"
MOVEMENT_OUT = OUT / "e252_e237_e250_union_movement_audit.csv"
Q3_IDX = TARGETS.index("Q3")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def digest_pred(pred: np.ndarray) -> str:
    return hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    e154 = e230.load_prob(e237.E154_FILE, sample)
    e224 = e230.load_prob(e237.E224_FILE, sample)
    e237_pred = e251.load_prob(e251.E237_FILE, sample)
    e250_pred = e251.load_prob(e251.E250_FILE, sample)
    e237_rows = e251.q3_drop_rows(e237_pred, e224)
    e250_rows = e251.q3_drop_rows(e250_pred, e224)
    union_rows = e237_rows | e250_rows
    pred = e251.build_pred_from_rows(e224, e154, union_rows)
    file_name = f"submission_e252_e237_e250_union_q3top31_{digest_pred(pred)}.csv"
    out_path = OUT / file_name
    out = sample[KEYS].copy()
    out[TARGETS] = pred
    out.to_csv(out_path, index=False)

    sub = pd.read_csv(out_path)
    schema_rows = [
        {"check": "shape", "ok": sub.shape == (250, 10), "value": str(sub.shape)},
        {"check": "columns", "ok": list(sub.columns) == [*KEYS, *TARGETS], "value": ",".join(sub.columns)},
        {
            "check": "key_order",
            "ok": sub[KEYS].astype(str).equals(sample[KEYS].astype(str)),
            "value": "exact_sample_order",
        },
        {"check": "finite", "ok": bool(np.isfinite(sub[TARGETS].to_numpy()).all()), "value": "finite"},
        {"check": "prob_min", "ok": float(sub[TARGETS].min().min()) >= 0.0, "value": f"{sub[TARGETS].min().min():.12f}"},
        {"check": "prob_max", "ok": float(sub[TARGETS].max().max()) <= 1.0, "value": f"{sub[TARGETS].max().max():.12f}"},
    ]
    schema = pd.DataFrame(schema_rows)
    schema.to_csv(SCHEMA_OUT, index=False)

    delta = np.abs(logit(pred) - logit(e224))
    move_rows = []
    for j, target in enumerate(TARGETS):
        target_delta = delta[:, j]
        move_rows.append(
            {
                "target": target,
                "changed_cells_vs_e224": int((target_delta > 1.0e-9).sum()),
                "abs_logit_sum": float(target_delta.sum()),
                "max_abs_logit_delta": float(target_delta.max()),
            }
        )
    movement = pd.DataFrame(move_rows)
    movement.to_csv(MOVEMENT_OUT, index=False)

    report_lines = [
        "# E252 E237/E250 Union Materializer",
        "",
        "## Question",
        "",
        "Can the E251 union of E237 and E250 Q3 rollback cells be preserved as an exact, schema-clean public sensor?",
        "",
        "## Artifact",
        "",
        f"- submission: `analysis_outputs/{file_name}`",
        f"- SHA256: `{sha256(out_path)}`",
        f"- E237 cells: `{len(e237_rows)}`",
        f"- E250 cells: `{len(e250_rows)}`",
        f"- shared cells: `{len(e237_rows & e250_rows)}`",
        f"- union cells: `{len(union_rows)}`",
        "",
        "## Schema Audit",
        "",
        md_table(schema),
        "",
        "## Movement Audit",
        "",
        md_table(movement),
        "",
        "## Decision",
        "",
        "- The file is a clean E251 union artifact. It is not OOF-certified as a standalone selector.",
        "- Submit only if the explicit question is whether E237 and E250 feature-NN/context cell sets are complementary on public.",
        "- For likely score without that question, keep E237 first.",
    ]
    REPORT_OUT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"wrote: {out_path}")
    print(f"sha256: {sha256(out_path)}")
    print(movement.to_string(index=False))


if __name__ == "__main__":
    main()
