from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

import public_selector_universe_audit as universe  # noqa: E402


ROBUST8_SELECTED = OUT / "public_lb_direct_label_robust_selector8_selected.csv"
INVERSE8_SELECTED = OUT / "public_lb_direct_label_inverse8_selected.csv"
OUT_CSV = OUT / "public_lb_inverse8_selected_stress_audit.csv"
REPORT_OUT = OUT / "public_lb_inverse8_selected_stress_audit_report.md"


def collect_selected() -> pd.DataFrame:
    frames = []
    if ROBUST8_SELECTED.exists():
        df = pd.read_csv(ROBUST8_SELECTED).copy()
        df["source_group"] = "robust8"
        df["source_path"] = df["file"].map(lambda x: str(OUT / str(x)))
        frames.append(df)
    if INVERSE8_SELECTED.exists():
        df = pd.read_csv(INVERSE8_SELECTED).copy()
        df["source_group"] = "inverse8_direct"
        df["source_path"] = df["file"].map(lambda x: str(OUT / str(x)))
        frames.append(df)
    if not frames:
        raise FileNotFoundError("inverse8 selected files are missing")
    selected = pd.concat(frames, ignore_index=True, sort=False)
    selected["basename"] = selected["source_path"].map(lambda x: Path(str(x)).name)
    selected = selected.drop_duplicates("basename").reset_index(drop=True)
    return selected


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(universe.KEYS).reset_index(drop=True)
    known, refs, ref_vecs = universe.build_known_and_refs(sample)
    models = universe.evaluate_models(known)

    selected = collect_selected()
    rows = []
    for row in selected.itertuples(index=False):
        path = Path(str(row.source_path))
        if not path.exists():
            continue
        rec = universe.feature_row(str(path), sample, refs, ref_vecs)
        rec["file"] = str(row.basename)
        rec["source_path"] = str(path)
        rec["basename"] = str(row.basename)
        rec["candidate_family"] = f"inverse8_{row.source_group}"
        rec["is_known_public"] = False
        rec["known_public_lb"] = np.nan
        rows.append(rec)

    anchor_rows = known.copy()
    anchor_rows["basename"] = anchor_rows["file"].astype(str)
    anchor_rows["source_path"] = anchor_rows["file"].astype(str)
    anchor_rows["candidate_family"] = "known_public"
    candidates = pd.concat([anchor_rows, pd.DataFrame(rows)], ignore_index=True, sort=False)

    proxy = universe.fit_all_predict(known, candidates, models)
    stress = universe.candidate_stress_scores(known, proxy)
    stress = stress.merge(candidates[["file", "source_path", "basename", "candidate_family"]].drop_duplicates("file"), on="file", how="left")
    scored = universe.add_frontier_flags(stress)
    scored = scored.merge(
        selected[
            [
                col
                for col in [
                    "basename",
                    "source_group",
                    "submit_role",
                    "source_solution_id",
                    "source_mask_name",
                    "source_prior_name",
                    "target_mask",
                    "strength",
                    "cap",
                    "robust_delta_vs_a2c8",
                    "robust_p90_delta_vs_a2c8",
                    "direct_delta_vs_a2c8",
                    "direct_p90_delta_vs_a2c8",
                ]
                if col in selected.columns
            ]
        ],
        on="basename",
        how="left",
    )
    scored["inverse8_submit_gate"] = (
        scored["candidate_family"].astype(str).str.startswith("inverse8_")
        & (scored["selector_p90_delta_vs_a2c8_public"] <= 0.00055)
        & (scored["bad_axis_abs_load"] <= 0.040)
        & (scored["beats_a2c8_scenario_rate"] >= 0.50)
    )
    scored["inverse8_probe_gate"] = (
        scored["candidate_family"].astype(str).str.startswith("inverse8_")
        & (scored["selector_p90_delta_vs_a2c8_public"] <= 0.00070)
        & (scored["bad_axis_abs_load"] <= 0.075)
        & (scored["beats_a2c8_scenario_rate"] >= 0.20)
    )
    scored = scored.sort_values(
        ["inverse8_submit_gate", "inverse8_probe_gate", "selector_p90_delta_vs_a2c8_public", "bad_axis_abs_load"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)
    scored.to_csv(OUT_CSV, index=False)

    cand = scored[scored["candidate_family"].astype(str).str.startswith("inverse8_")].copy()
    submit = cand[cand["inverse8_submit_gate"] == True]  # noqa: E712
    probe = cand[cand["inverse8_probe_gate"] == True]  # noqa: E712
    cols = [
        "basename",
        "source_group",
        "submit_role",
        "source_mask_name",
        "target_mask",
        "strength",
        "cap",
        "selector_delta_vs_a2c8_public",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "mean_abs_move_vs_raw05",
        "inverse8_submit_gate",
        "inverse8_probe_gate",
    ]
    cols = [c for c in cols if c in cand.columns]

    def table(df: pd.DataFrame) -> str:
        if df.empty:
            return "None."
        return "```text\n" + df.to_string(index=False, float_format=lambda x: f"{x:.6f}") + "\n```"

    report = [
        "# Inverse8 Selected Stress Audit",
        "",
        "## Counts",
        f"- selected candidates: {len(cand)}",
        f"- submit gate pass: {len(submit)}",
        f"- probe gate pass: {len(probe)}",
        "",
        "## Top Candidates",
        table(cand.head(40)[cols]),
        "",
        "## Submit Gate",
        table(submit.head(20)[cols]),
        "",
        "## Probe Gate",
        table(probe.head(30)[cols]),
    ]
    REPORT_OUT.write_text("\n".join(report) + "\n")

    print(REPORT_OUT)
    print({"selected": len(cand), "submit": len(submit), "probe": len(probe)})
    print(cand.head(30)[cols].round(9).to_string(index=False))


if __name__ == "__main__":
    main()
