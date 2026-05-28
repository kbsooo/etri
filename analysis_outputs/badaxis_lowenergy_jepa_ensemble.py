from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_subset_selector_stress import candidate_stress_scores  # noqa: E402
from public_anchor_bottleneck_decomposition import (  # noqa: E402
    A2C8,
    FINAL9,
    KEYS,
    LEJEPA_BAD,
    ORDINAL,
    Q2_BAD,
    RAW05,
    RESID_BAD,
    STAGE2,
    TARGETS,
    clip_prob,
    evaluate_models,
    feature_row,
    fit_all_predict,
    known_public_table,
    load_sub,
    logit,
    prob_matrix,
    projection,
    residual_ratio_to_span,
    vec,
)
from public_selector_universe_audit import (  # noqa: E402
    BAD_AXIS_LIMIT,
    P90_SOFT_LIMIT,
    SELECTOR_UNCERTAINTY,
    add_frontier_flags,
)


UNIVERSE_SHORT = OUT / "public_selector_universe_audit_shortlist.csv"
SCAN_OUT = OUT / "badaxis_lowenergy_jepa_ensemble_scan.csv"
SHORT_OUT = OUT / "badaxis_lowenergy_jepa_ensemble_shortlist.csv"
SELECTED_OUT = OUT / "badaxis_lowenergy_jepa_ensemble_selected.csv"
REPORT_OUT = OUT / "badaxis_lowenergy_jepa_ensemble_report.md"

KEEP_FAMILIES = {"public6entropy", "cvjepa", "hiddenblock_seqmotif", "axis_repair"}
BASES = ["a2c8", "raw05", "mid_a2c8_raw05"]
TARGET_MASKS = {
    "all": TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q1_q3_s34": ["Q1", "Q3", "S3", "S4"],
    "q3_s4": ["Q3", "S4"],
    "q3_s2_s3_s4": ["Q3", "S2", "S3", "S4"],
    "stage_only": ["S1", "S2", "S3", "S4"],
}
CELL_GATES = ["all", "signal_top60", "stable", "low_energy", "entropy_stable"]
SCALES = [0.25, 0.50, 0.75, 1.00, 1.25, 1.50, -0.25, -0.50]
DELTA_CAPS = [0.030, 0.060, 0.100]
ANTI_LAMBDAS = [0.0, 0.50, 1.00]
MAX_GENERATED = 60000
MAX_SAVE = 24


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def stable_tag(pred: np.ndarray) -> str:
    return sha1(np.round(clip_prob(pred), 10).tobytes()).hexdigest()[:8]


def source_path_to_path(source_path: str) -> Path:
    path = Path(source_path)
    if path.exists():
        return path
    candidate = ROOT / source_path
    if candidate.exists():
        return candidate
    raise FileNotFoundError(source_path)


def load_sample() -> pd.DataFrame:
    return pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)


def load_prob_from_source(source_path: str, sample: pd.DataFrame) -> np.ndarray:
    path = source_path_to_path(source_path)
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)
    if not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"key mismatch: {source_path}")
    return clip_prob(df[TARGETS].to_numpy(dtype=np.float64))


def build_refs(sample: pd.DataFrame) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], pd.DataFrame]:
    ref_files = {
        "stage2": STAGE2,
        "raw05": RAW05,
        "a2c8": A2C8,
        "final9": FINAL9,
        "ordinal": ORDINAL,
        "q2_bad": Q2_BAD,
        "resid_bad": RESID_BAD,
        "lejepa_bad": LEJEPA_BAD,
    }
    refs = {name: prob_matrix(file_name, sample) for name, file_name in ref_files.items()}
    ref_vecs = {name: vec(prob) for name, prob in refs.items()}

    known_rows = []
    for rec in known_public_table().to_dict("records"):
        row = feature_row(str(rec["file"]), sample, refs, ref_vecs)
        row.update(rec)
        row["file"] = str(rec["file"])
        row["source_path"] = str(rec["file"])
        row["candidate_family"] = "known_public"
        row["is_known_public"] = True
        row["known_public_lb"] = float(rec["public_lb"])
        known_rows.append(row)
    known = pd.DataFrame(known_rows).sort_values("public_lb").reset_index(drop=True)
    return refs, ref_vecs, known


def feature_from_prob(file_id: str, prob: np.ndarray, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> dict[str, object]:
    p = clip_prob(prob)
    z = logit(p).reshape(-1)
    z_stage2 = ref_vecs["stage2"]
    move_stage2 = z - z_stage2
    z_a2c8 = ref_vecs["a2c8"]
    z_raw05 = ref_vecs["raw05"]
    row: dict[str, object] = {
        "file": file_id,
        "min_prob": float(p.min()),
        "max_prob": float(p.max()),
        "mean_prob": float(p.mean()),
        "prob_span": float(p.max() - p.min()),
        "mean_abs_move_vs_stage2": float(np.mean(np.abs(z - z_stage2))),
        "mean_abs_move_vs_raw05": float(np.mean(np.abs(z - z_raw05))),
        "mean_abs_move_vs_a2c8": float(np.mean(np.abs(z - z_a2c8))),
        "rms_move_vs_a2c8": float(np.sqrt(np.mean((z - z_a2c8) ** 2))),
        "max_abs_move_vs_a2c8": float(np.max(np.abs(z - z_a2c8))),
    }
    for target_i, target in enumerate(TARGETS):
        target_move = logit(p[:, [target_i]]) - logit(refs["a2c8"][:, [target_i]])
        row[f"move_abs_a2c8_{target}"] = float(np.mean(np.abs(target_move)))
        row[f"mean_prob_{target}"] = float(np.mean(p[:, target_i]))

    ref_dirs = {
        "a2c8": ref_vecs["a2c8"] - z_stage2,
        "raw05": ref_vecs["raw05"] - z_stage2,
        "final9": ref_vecs["final9"] - z_stage2,
        "ordinal": ref_vecs["ordinal"] - z_stage2,
        "q2_bad": ref_vecs["q2_bad"] - z_stage2,
        "resid_bad": ref_vecs["resid_bad"] - z_stage2,
        "lejepa_bad": ref_vecs["lejepa_bad"] - z_stage2,
    }
    for name, direction in ref_dirs.items():
        coeff, cos = projection(move_stage2, direction)
        row[f"proj_{name}"] = coeff
        row[f"cos_{name}"] = cos
    row["bad_axis_abs_load"] = float(
        abs(row["proj_q2_bad"])
        + abs(row["proj_resid_bad"])
        + abs(row["proj_lejepa_bad"])
        + 0.5 * abs(row["proj_ordinal"])
    )
    row["bad_axis_positive_load"] = float(
        max(row["proj_q2_bad"], 0.0)
        + max(row["proj_resid_bad"], 0.0)
        + max(row["proj_lejepa_bad"], 0.0)
        + 0.5 * max(row["proj_ordinal"], 0.0)
    )
    row["good_axis_load"] = float(abs(row["proj_a2c8"]) + abs(row["proj_raw05"]))
    row["good_span_residual_ratio"] = residual_ratio_to_span(move_stage2, [ref_dirs["a2c8"], ref_dirs["raw05"]])
    row["bad_to_good_load_ratio"] = float(row["bad_axis_abs_load"] / (row["good_axis_load"] + 1e-9))
    row["raw05_a2c8_compat_energy"] = float(
        row["mean_abs_move_vs_raw05"]
        + 0.35 * row["mean_abs_move_vs_a2c8"]
        + 0.015 * row["bad_axis_abs_load"]
        + 0.010 * row["good_span_residual_ratio"]
    )
    return row


def target_mask(name: str, n_rows: int) -> np.ndarray:
    allowed = set(TARGET_MASKS[name])
    keep = np.asarray([target in allowed for target in TARGETS], dtype=np.float64)
    return np.repeat(keep.reshape(1, -1), n_rows, axis=0)


def choose_donors(short: pd.DataFrame) -> pd.DataFrame:
    frame = short.copy()
    frame = frame[frame["candidate_family"].isin(KEEP_FAMILIES)].copy()
    frame = frame[frame["novel_frontier_candidate"].fillna(False).astype(bool)].copy()
    if frame.empty:
        raise RuntimeError("No novel frontier donors found. Run public_selector_universe_audit.py first.")
    parts = []
    for family, group in frame.sort_values("submission_priority_score").groupby("candidate_family", sort=False):
        limit = 6 if family in {"cvjepa", "hiddenblock_seqmotif"} else 4
        parts.append(group.head(limit))
    return pd.concat(parts, ignore_index=True).drop_duplicates("source_path").sort_values("submission_priority_score").reset_index(drop=True)


def build_signal_specs(donors: pd.DataFrame, donor_z: dict[str, np.ndarray], a2c8_z: np.ndarray) -> list[dict[str, object]]:
    specs: list[dict[str, object]] = []
    deltas_by_source = {src: donor_z[src] - a2c8_z for src in donor_z}

    def add_group(name: str, sources: list[str]) -> None:
        if not sources:
            return
        stack = np.stack([deltas_by_source[src] for src in sources], axis=0)
        signs = np.sign(stack)
        nonzero = np.maximum((signs != 0).sum(axis=0), 1)
        sign_agree = np.abs(signs.sum(axis=0)) / nonzero
        var = np.var(stack, axis=0)
        for agg_name, delta in [("mean", np.mean(stack, axis=0)), ("median", np.median(stack, axis=0))]:
            energy = np.abs(delta) / (np.sqrt(var) + 1e-6)
            specs.append(
                {
                    "signal_name": f"{name}_{agg_name}",
                    "signal_family": name,
                    "target_z": a2c8_z + delta,
                    "delta_vs_a2c8": delta,
                    "sign_agree": sign_agree,
                    "variance": var,
                    "energy": energy,
                    "source_count": len(sources),
                }
            )

    all_sources = list(donor_z)
    add_group("allnovel", all_sources)
    for family, group in donors.groupby("candidate_family", sort=False):
        add_group(str(family), group["source_path"].astype(str).tolist())

    for rec in donors.sort_values("submission_priority_score").head(12).to_dict("records"):
        src = str(rec["source_path"])
        delta = deltas_by_source[src]
        specs.append(
            {
                "signal_name": f"solo_{rec['candidate_family']}_{stable_tag(sigmoid(donor_z[src]))}",
                "signal_family": str(rec["candidate_family"]),
                "target_z": donor_z[src],
                "delta_vs_a2c8": delta,
                "sign_agree": np.ones_like(delta),
                "variance": np.zeros_like(delta),
                "energy": np.abs(delta) / (np.median(np.abs(delta)) + 1e-6),
                "source_count": 1,
            }
        )
    return specs


def cell_gate(spec: dict[str, object], gate_name: str, base_prob: np.ndarray) -> np.ndarray:
    delta = np.asarray(spec["delta_vs_a2c8"], dtype=np.float64)
    active = np.abs(delta) > 1e-10
    if gate_name == "all":
        return np.ones_like(delta, dtype=np.float64)
    if gate_name == "signal_top60":
        threshold = float(np.quantile(np.abs(delta[active]), 0.60)) if active.any() else 0.0
        return ((np.abs(delta) >= threshold) & active).astype(np.float64)

    sign_agree = np.asarray(spec["sign_agree"], dtype=np.float64)
    energy = np.asarray(spec["energy"], dtype=np.float64)
    variance = np.asarray(spec["variance"], dtype=np.float64)
    stable = (sign_agree >= 0.60) & active
    if gate_name == "stable":
        threshold = float(np.quantile(np.abs(delta[active]), 0.55)) if active.any() else 0.0
        return (stable & (np.abs(delta) >= threshold)).astype(np.float64)
    if gate_name == "low_energy":
        e_threshold = float(np.quantile(energy[active], 0.60)) if active.any() else 0.0
        v_threshold = float(np.quantile(variance[active], 0.65)) if active.any() else 0.0
        return (stable & (energy >= e_threshold) & (variance <= v_threshold)).astype(np.float64)
    if gate_name == "entropy_stable":
        entropy = -(base_prob * np.log(base_prob + 1e-12) + (1.0 - base_prob) * np.log(1.0 - base_prob + 1e-12))
        e_threshold = float(np.quantile(entropy, 0.60))
        return (stable & (entropy >= e_threshold)).astype(np.float64)
    raise ValueError(gate_name)


def bad_basis(ref_vecs: dict[str, np.ndarray], n_rows: int) -> np.ndarray:
    z_stage2 = ref_vecs["stage2"]
    cols = [
        ref_vecs["q2_bad"] - z_stage2,
        ref_vecs["resid_bad"] - z_stage2,
        ref_vecs["lejepa_bad"] - z_stage2,
        0.5 * (ref_vecs["ordinal"] - z_stage2),
    ]
    basis = np.column_stack(cols)
    if basis.shape[0] != n_rows * len(TARGETS):
        raise ValueError("bad basis shape mismatch")
    return basis


def remove_bad_component(move: np.ndarray, basis: np.ndarray, anti_lambda: float) -> np.ndarray:
    if anti_lambda <= 0.0:
        return move
    flat = move.reshape(-1)
    gram = basis.T @ basis
    beta = np.linalg.pinv(gram + 1e-8 * np.eye(gram.shape[0])) @ basis.T @ flat
    bad = (basis @ beta).reshape(move.shape)
    return move - anti_lambda * bad


def base_logits(refs: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    z_a2c8 = logit(refs["a2c8"])
    z_raw05 = logit(refs["raw05"])
    return {
        "a2c8": z_a2c8,
        "raw05": z_raw05,
        "mid_a2c8_raw05": 0.50 * z_a2c8 + 0.50 * z_raw05,
    }


def generate_candidates(
    sample: pd.DataFrame,
    refs: dict[str, np.ndarray],
    ref_vecs: dict[str, np.ndarray],
    donors: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    bases = base_logits(refs)
    z_stage2 = logit(refs["stage2"])
    z_a2c8 = bases["a2c8"]
    donor_z = {str(row.source_path): logit(load_prob_from_source(str(row.source_path), sample)) for row in donors.itertuples(index=False)}
    specs = build_signal_specs(donors, donor_z, z_a2c8)
    bad = bad_basis(ref_vecs, len(sample))

    rows: list[dict[str, object]] = []
    arrays: dict[str, np.ndarray] = {}
    seen: set[str] = set()
    n_rows = len(sample)

    for spec in specs:
        target_z = np.asarray(spec["target_z"], dtype=np.float64)
        for base_name in BASES:
            base_z = bases[base_name]
            base_prob = clip_prob(sigmoid(base_z))
            raw_delta = target_z - base_z
            for target_mask_name in TARGET_MASKS:
                tgate = target_mask(target_mask_name, n_rows)
                for gate_name in CELL_GATES:
                    cgate = cell_gate(spec, gate_name, base_prob)
                    gate = tgate * cgate
                    active = float(gate.mean())
                    if active <= 0.0:
                        continue
                    for scale in SCALES:
                        for cap in DELTA_CAPS:
                            delta = np.clip(scale * raw_delta, -cap, cap) * gate
                            if float(np.mean(np.abs(delta))) <= 1e-12:
                                continue
                            for anti_lambda in ANTI_LAMBDAS:
                                move = (base_z + delta) - z_stage2
                                adjusted_move = remove_bad_component(move, bad, anti_lambda)
                                pred = clip_prob(sigmoid(z_stage2 + adjusted_move))
                                tag = stable_tag(pred)
                                if tag in seen:
                                    continue
                                seen.add(tag)
                                file_id = f"badaxis_lowenergy_jepa_{tag}"
                                row = feature_from_prob(file_id, pred, refs, ref_vecs)
                                row.update(
                                    {
                                        "source_path": f"generated/{file_id}.csv",
                                        "basename": f"submission_{file_id}.csv",
                                        "candidate_family": "badaxis_lowenergy_jepa",
                                        "is_known_public": False,
                                        "known_public_lb": np.nan,
                                        "signal_name": str(spec["signal_name"]),
                                        "signal_family": str(spec["signal_family"]),
                                        "signal_source_count": int(spec["source_count"]),
                                        "base_name": base_name,
                                        "target_mask": target_mask_name,
                                        "cell_gate": gate_name,
                                        "scale": float(scale),
                                        "delta_cap": float(cap),
                                        "anti_lambda": float(anti_lambda),
                                        "active_gate_mean": active,
                                    }
                                )
                                rows.append(row)
                                arrays[file_id] = pred
                                if len(rows) >= MAX_GENERATED:
                                    return pd.DataFrame(rows), arrays
    return pd.DataFrame(rows), arrays


def materialize_selected(selected: pd.DataFrame, arrays: dict[str, np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rec in selected.head(MAX_SAVE).itertuples(index=False):
        file_id = str(rec.file)
        pred = arrays[file_id]
        name = f"submission_{file_id}.csv"
        out_path = OUT / name
        out = sample[KEYS].copy()
        for j, target in enumerate(TARGETS):
            out[target] = pred[:, j]
        out.to_csv(out_path, index=False)
        rows.append(
            {
                "file": name,
                "source_path": str(out_path.relative_to(ROOT)),
                "rows": len(out),
                "min_prob": float(pred.min()),
                "max_prob": float(pred.max()),
                "null_probs": int(out[TARGETS].isna().sum().sum()),
            }
        )
    return pd.DataFrame(rows)


def write_report(scored: pd.DataFrame, selected: pd.DataFrame, saved: pd.DataFrame, donors: pd.DataFrame) -> None:
    resolved = scored[scored["resolved_better_than_a2c8_gate"]]
    novel = scored[scored["novel_frontier_candidate"]]
    top_cols = [
        "file",
        "source_path",
        "signal_name",
        "base_name",
        "target_mask",
        "cell_gate",
        "scale",
        "delta_cap",
        "anti_lambda",
        "selector_delta_vs_a2c8_public",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "resolved_better_than_a2c8_gate",
        "novel_frontier_candidate",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "mean_abs_move_vs_raw05",
        "submission_priority_score",
    ]
    donor_cols = ["source_path", "candidate_family", "submission_priority_score", "selector_p90_delta_vs_a2c8_public", "bad_axis_abs_load", "mean_abs_move_vs_raw05"]
    lines = [
        "# Bad-Axis Low-Energy JEPA Ensemble",
        "",
        "This is a constrained generation pass over the universe-audit novel donors. It treats cross-family agreement as low latent energy and removes projection onto the known bad public axes before scoring.",
        "",
        "## Donor Pool",
        "",
        "```csv",
        donors[[c for c in donor_cols if c in donors.columns]].round(9).to_csv(index=False).strip(),
        "```",
        "",
        "## Gate Counts",
        "",
        f"- Generated candidates: `{len(scored)}`.",
        f"- Resolved-better strict gate: `{len(resolved)}`.",
        f"- Novel frontier candidates: `{len(novel)}`.",
        f"- Saved research probes: `{len(saved)}`.",
        "",
        "## Selected",
        "",
        "```csv",
        selected[[c for c in top_cols if c in selected.columns]].head(40).round(9).to_csv(index=False).strip(),
        "```",
        "",
        "## Saved Files",
        "",
        "```csv",
        (saved.to_csv(index=False).strip() if not saved.empty else "none"),
        "```",
        "",
        "## Read",
        "",
        "- A strict-gate pass would justify a submission candidate. Without it, these files are research probes only.",
        "- If low-energy consensus improves movement but not selector p90, the bottleneck remains selector resolution rather than candidate generation.",
        "- If hiddenblock donors survive more often than cvjepa/public6, the next modeling branch should prioritize sequence motif latent gates.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not UNIVERSE_SHORT.exists():
        raise FileNotFoundError("Run public_selector_universe_audit.py first.")
    sample = load_sample()
    refs, ref_vecs, known = build_refs(sample)
    donors = choose_donors(pd.read_csv(UNIVERSE_SHORT))
    generated, arrays = generate_candidates(sample, refs, ref_vecs, donors)
    if generated.empty:
        raise RuntimeError("No candidates generated.")

    candidates = pd.concat([generated, known], ignore_index=True, sort=False)
    models = evaluate_models(known)
    proxy_scored = fit_all_predict(known, candidates, models)
    stress_scored = candidate_stress_scores(known, proxy_scored)
    meta_cols = [
        "source_path",
        "basename",
        "candidate_family",
        "signal_name",
        "signal_family",
        "signal_source_count",
        "base_name",
        "target_mask",
        "cell_gate",
        "scale",
        "delta_cap",
        "anti_lambda",
        "active_gate_mean",
    ]
    stress_scored = stress_scored.merge(candidates[["file", *meta_cols]].drop_duplicates("file"), on="file", how="left")
    scored = add_frontier_flags(stress_scored)
    generated_scored = scored[scored["candidate_family"].eq("badaxis_lowenergy_jepa")].copy()
    generated_scored.to_csv(SCAN_OUT, index=False)

    selected = generated_scored[
        generated_scored["resolved_better_than_a2c8_gate"]
        | generated_scored["novel_frontier_candidate"]
        | (
            generated_scored["low_public_bad_axis"]
            & generated_scored["movement_over_selector_uncertainty"]
            & generated_scored["p90_not_too_worse"]
        )
    ].copy()
    if selected.empty:
        selected = generated_scored.head(80).copy()
    selected = selected.sort_values(
        ["resolved_better_than_a2c8_gate", "novel_frontier_candidate", "submission_priority_score"],
        ascending=[False, False, True],
    ).head(120)
    selected.to_csv(SHORT_OUT, index=False)

    saveable = selected[
        selected["novel_frontier_candidate"]
        | selected["resolved_better_than_a2c8_gate"]
        | (selected["submission_priority_score"] <= selected["submission_priority_score"].quantile(0.20))
    ].copy()
    saved = materialize_selected(saveable, arrays, sample)
    saved.to_csv(SELECTED_OUT, index=False)
    write_report(generated_scored, selected, saved, donors)

    print(REPORT_OUT)
    print("[counts]")
    print(
        {
            "generated": len(generated_scored),
            "resolved_better": int(generated_scored["resolved_better_than_a2c8_gate"].sum()),
            "frontier_escape": int(generated_scored["frontier_escape_candidate"].sum()),
            "novel_frontier": int(generated_scored["novel_frontier_candidate"].sum()),
            "saved": len(saved),
        }
    )
    print("[top selected]")
    cols = [
        "file",
        "signal_name",
        "base_name",
        "target_mask",
        "cell_gate",
        "scale",
        "anti_lambda",
        "selector_delta_vs_a2c8_public",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "novel_frontier_candidate",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "mean_abs_move_vs_raw05",
        "submission_priority_score",
    ]
    print(selected[cols].head(30).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
