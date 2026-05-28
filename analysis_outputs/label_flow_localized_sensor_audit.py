from __future__ import annotations

from pathlib import Path
import hashlib
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_subset_selector_stress import candidate_stress_scores  # noqa: E402
from public_anchor_bottleneck_decomposition import A2C8, TARGETS, feature_row, load_sub, logit  # noqa: E402
from public_pairwise_order_selector import evaluate_pairwise_models, score_candidates  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


SENSORS = {
    "conservative_1bb": OUT / "submission_label_flow_focused_1bbfb735.csv",
    "contrast_6b": OUT / "submission_label_flow_focused_6b9335b1.csv",
}
TARGET_MASKS = {
    "q3_s4": ["Q3", "S4"],
    "s4": ["S4"],
}
SCALES = [1.0, 0.65]

DETAIL_OUT = OUT / "label_flow_localized_sensor_audit.csv"
ZONE_OUT = OUT / "label_flow_localized_sensor_audit_by_zone.csv"
MASK_OUT = OUT / "label_flow_localized_sensor_audit_by_mask.csv"
SHORTLIST_OUT = OUT / "label_flow_localized_sensor_audit_shortlist.csv"
REPORT_OUT = OUT / "label_flow_localized_sensor_audit_report.md"


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def clean_tag(text: object) -> str:
    out = str(text).lower().replace(" ", "_").replace("/", "_").replace(":", "_")
    return "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in out).strip("_")


def stable_name(sensor_tag: str, target_mask: str, row_mask: str, scale: float) -> str:
    key = f"{sensor_tag}|{target_mask}|{row_mask}|{scale:.4f}".encode("utf-8")
    digest = hashlib.md5(key).hexdigest()[:8]
    scale_tag = f"s{scale:.2f}".replace(".", "p")
    return f"submission_label_flow_locsensor_{sensor_tag}_{target_mask}_{clean_tag(row_mask)}_{scale_tag}_{digest}.csv"


def date_blocks(sample: pd.DataFrame) -> pd.Series:
    block = pd.Series(index=sample.index, dtype=object)
    for sid, group in sample.sort_values(["subject_id", "lifelog_date"]).groupby("subject_id", sort=False):
        gaps = group["lifelog_date"].diff().dt.days.fillna(1)
        local_block = gaps.gt(1).cumsum()
        for idx, bid in zip(group.index, local_block, strict=True):
            block.loc[idx] = f"{sid}_b{int(bid):02d}"
    return block


def contiguous_mask_records(sample: pd.DataFrame, delta_abs: np.ndarray, s4_delta: np.ndarray) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    n = len(sample)

    def add(name: str, kind: str, mask: np.ndarray) -> None:
        mask = np.asarray(mask, dtype=bool)
        count = int(mask.sum())
        if count <= 0 or count >= n:
            return
        records.append(
            {
                "row_mask_name": name,
                "row_mask_kind": kind,
                "row_mask": mask,
                "row_mask_size": count,
                "row_mask_frac": float(count / n),
            }
        )

    # Subject identity and subject-complement probes.
    for sid in sorted(sample["subject_id"].unique()):
        sub = sample["subject_id"].eq(sid).to_numpy()
        add(f"subject_{sid}", "subject", sub)
        add(f"not_subject_{sid}", "subject_complement", ~sub)

    # Global date bins.
    order = sample.sort_values(["sleep_date", "subject_id"]).index.to_numpy()
    for k, splits in [("global_tertile", 3), ("global_quintile", 5)]:
        parts = np.array_split(order, splits)
        for i, part in enumerate(parts):
            mask = np.zeros(n, dtype=bool)
            mask[part] = True
            add(f"{k}_{i}", k, mask)

    # Within-subject phase bins.
    rank = sample.groupby("subject_id")["lifelog_date"].rank(method="first", pct=True).to_numpy()
    add("subject_phase_early", "subject_phase", rank <= 1 / 3)
    add("subject_phase_mid", "subject_phase", (rank > 1 / 3) & (rank <= 2 / 3))
    add("subject_phase_late", "subject_phase", rank > 2 / 3)
    add("subject_phase_first_half", "subject_phase", rank <= 0.5)
    add("subject_phase_second_half", "subject_phase", rank > 0.5)

    # Hidden-like contiguous date blocks and complements.
    blocks = date_blocks(sample)
    block_sizes = blocks.value_counts()
    for block_id, size in block_sizes.items():
        if int(size) < 3:
            continue
        mask = blocks.eq(block_id).to_numpy()
        add(f"block_{block_id}", "date_block", mask)
        add(f"not_block_{block_id}", "date_block_complement", ~mask)

    # Movement energy and sign probes.
    energy = np.asarray(delta_abs, dtype=np.float64)
    for q in [0.20, 0.35, 0.50, 0.65, 0.80]:
        threshold = float(np.quantile(energy, 1.0 - q))
        add(f"delta_energy_top_{int(q * 100)}", "delta_energy", energy >= threshold)
        threshold_low = float(np.quantile(energy, q))
        add(f"delta_energy_bottom_{int(q * 100)}", "delta_energy", energy <= threshold_low)

    add("s4_delta_positive", "delta_sign", s4_delta > 1e-12)
    add("s4_delta_negative", "delta_sign", s4_delta < -1e-12)

    weekday = sample["lifelog_date"].dt.dayofweek.to_numpy()
    add("weekend", "calendar", weekday >= 5)
    add("weekday", "calendar", weekday < 5)

    # Subject groups by total movement.
    subject_energy = (
        pd.DataFrame({"subject_id": sample["subject_id"], "energy": energy})
        .groupby("subject_id")["energy"]
        .mean()
        .sort_values()
    )
    low_subjects = set(subject_energy.head(len(subject_energy) // 2).index)
    high_subjects = set(subject_energy.tail(len(subject_energy) // 2).index)
    add("subject_energy_low_half", "subject_energy", sample["subject_id"].isin(low_subjects).to_numpy())
    add("subject_energy_high_half", "subject_energy", sample["subject_id"].isin(high_subjects).to_numpy())

    # Deduplicate identical masks.
    seen: set[bytes] = set()
    unique: list[dict[str, object]] = []
    for rec in records:
        raw = np.packbits(rec["row_mask"]).tobytes()
        if raw in seen:
            continue
        seen.add(raw)
        unique.append(rec)
    return unique


def generate_localized(sample: pd.DataFrame) -> pd.DataFrame:
    base = load_sub(A2C8, sample)
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    rows: list[dict[str, object]] = []

    for sensor_tag, sensor_path in SENSORS.items():
        sensor = load_sub(sensor_path, sample)
        sensor_logits = logit(sensor[TARGETS].to_numpy(dtype=np.float64))
        delta = sensor_logits - base_logits
        delta_abs = np.mean(np.abs(delta[:, [TARGETS.index("Q3"), TARGETS.index("S4")]]), axis=1)
        s4_delta = delta[:, TARGETS.index("S4")]
        row_masks = contiguous_mask_records(sample, delta_abs, s4_delta)

        for row_rec in row_masks:
            row_mask = np.asarray(row_rec["row_mask"], dtype=bool)
            for target_mask_name, target_list in TARGET_MASKS.items():
                target_idx = [TARGETS.index(target) for target in target_list]
                for scale in SCALES:
                    out_logits = base_logits.copy()
                    out_logits[np.ix_(row_mask, target_idx)] = (
                        base_logits[np.ix_(row_mask, target_idx)]
                        + float(scale) * delta[np.ix_(row_mask, target_idx)]
                    )
                    out = base.copy()
                    out[TARGETS] = np.clip(sigmoid(out_logits), 1e-6, 1.0 - 1e-6)
                    name = stable_name(sensor_tag, target_mask_name, row_rec["row_mask_name"], scale)
                    path = OUT / name
                    out.to_csv(path, index=False)
                    meta = {k: v for k, v in row_rec.items() if k != "row_mask"}
                    meta.update(
                        {
                            "source_path": str(path.relative_to(ROOT)),
                            "file": str(path.relative_to(ROOT)),
                            "basename": name,
                            "sensor_tag": sensor_tag,
                            "target_mask_name": target_mask_name,
                            "target_mask": ",".join(target_list),
                            "scale": float(scale),
                        }
                    )
                    rows.append(meta)
    return pd.DataFrame(rows)


def build_feature_frame(generated: pd.DataFrame, sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for rec in generated.to_dict("records"):
        path = ROOT / str(rec["source_path"])
        row = feature_row(path, sample, refs, ref_vecs)
        row.update(rec)
        row["candidate_family"] = "label_flow_localized_sensor"
        rows.append(row)
    gen = pd.DataFrame(rows)

    known, _, _ = build_known_and_refs(sample)
    known = known.copy()
    known["source_path"] = known["file"].astype(str)
    known["basename"] = known["file"].astype(str)
    known["sensor_tag"] = "known_anchor"
    known["target_mask_name"] = "known_anchor"
    known["row_mask_name"] = "known_anchor"
    known["row_mask_kind"] = "known_anchor"
    known["row_mask_size"] = len(sample)
    known["row_mask_frac"] = 1.0
    known["scale"] = np.nan
    known["target_mask"] = ""
    return pd.concat([known, gen], ignore_index=True, sort=False)


def add_flags(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    move_cols = [f"move_abs_a2c8_{target}" for target in TARGETS]
    out["dominant_target"] = out[move_cols].idxmax(axis=1).str.replace("move_abs_a2c8_", "", regex=False)
    out["movement_scale"] = out["mean_abs_move_vs_a2c8"]
    out["q3s4_move_share"] = (
        out["move_abs_a2c8_Q3"] + out["move_abs_a2c8_S4"]
    ) / (out[move_cols].sum(axis=1) + 1e-12)
    out["old_majority"] = out["beats_a2c8_scenario_rate"].fillna(0.0) >= 0.50
    out["pair_majority"] = out["pair_beats_a2c8_rate"].fillna(0.0) >= 0.70
    out["two_selector_majority"] = out["old_majority"] & out["pair_majority"]
    out["pair_p90_negative"] = out["pair_delta_vs_a2c8_p90"] < 0.0
    out["localized_sensor_candidate"] = (
        out["pair_p90_negative"]
        & (out["pair_beats_a2c8_rate"] >= 0.70)
        & (out["beats_a2c8_scenario_rate"] >= 0.40)
        & (out["selector_p90_delta_vs_a2c8_public"] <= 0.00062)
        & (out["bad_axis_abs_load"] <= 0.065)
    )
    out["localization_rank"] = (
        out["pair_delta_vs_a2c8_p90"]
        + 0.25 * out["selector_p90_delta_vs_a2c8_public"].fillna(0.001)
        + 0.00025 * out["bad_axis_abs_load"].fillna(0.0)
        - 0.00008 * out["pair_beats_a2c8_rate"].fillna(0.0)
        - 0.00005 * out["beats_a2c8_scenario_rate"].fillna(0.0)
    )
    return out.sort_values(
        ["two_selector_majority", "localized_sensor_candidate", "localization_rank"],
        ascending=[False, False, True],
    ).reset_index(drop=True)


def score_localized(candidates: pd.DataFrame, known: pd.DataFrame) -> pd.DataFrame:
    old_scored = candidate_stress_scores(known, candidates)
    merge_cols = [
        "file",
        "selector_delta_vs_a2c8_public",
        "selector_p90_delta_vs_a2c8_public",
        "selector_stress_spread",
        "beats_a2c8_scenario_rate",
        "resolved_better_than_a2c8_gate",
        "candidate_selector_risk",
    ]
    old_scored = old_scored[[col for col in merge_cols if col in old_scored.columns]].copy()
    merged = candidates.merge(old_scored, on="file", how="left")
    model_df, _ = evaluate_pairwise_models(known)
    pair_scored = score_candidates(known, merged, model_df)
    generated = pair_scored[pair_scored["sensor_tag"].isin(SENSORS)].copy()
    return add_flags(generated)


def group_summary(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for keys, group in df.groupby(group_cols, sort=True, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        best = group.sort_values("localization_rank").iloc[0]
        rec = {col: key for col, key in zip(group_cols, keys, strict=True)}
        rec.update(
            {
                "n": int(len(group)),
                "pair_p90_negative": int(group["pair_p90_negative"].sum()),
                "pair_majority": int(group["pair_majority"].sum()),
                "old_majority": int(group["old_majority"].sum()),
                "two_selector_majority": int(group["two_selector_majority"].sum()),
                "localized_sensor_candidate": int(group["localized_sensor_candidate"].sum()),
                "best_file": best["source_path"],
                "best_pair_p90": float(best["pair_delta_vs_a2c8_p90"]),
                "best_pair_rate": float(best["pair_beats_a2c8_rate"]),
                "best_old_p90": float(best["selector_p90_delta_vs_a2c8_public"]),
                "best_old_rate": float(best["beats_a2c8_scenario_rate"]),
                "best_bad_axis": float(best["bad_axis_abs_load"]),
                "best_movement": float(best["movement_scale"]),
                "best_row_frac": float(best["row_mask_frac"]),
            }
        )
        rows.append(rec)
    return pd.DataFrame(rows).sort_values(
        ["two_selector_majority", "localized_sensor_candidate", "best_pair_p90", "best_old_p90"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_None._"
    view = df.copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.6g}")
        else:
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else str(x))
    lines = [
        "| " + " | ".join(view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]).replace("\n", " ") for col in view.columns) + " |")
    return "\n".join(lines)


def write_report(scored: pd.DataFrame, by_zone: pd.DataFrame, by_mask: pd.DataFrame, shortlist: pd.DataFrame) -> None:
    best = scored.sort_values("localization_rank").iloc[0]
    best_old = scored[
        (scored["pair_delta_vs_a2c8_p90"] < 0.0)
        & (scored["pair_beats_a2c8_rate"] >= 0.70)
    ].sort_values("selector_p90_delta_vs_a2c8_public").head(1)
    best_old_row = best_old.iloc[0] if not best_old.empty else None
    view_cols = [
        "source_path",
        "sensor_tag",
        "target_mask_name",
        "row_mask_kind",
        "row_mask_name",
        "scale",
        "row_mask_frac",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "movement_scale",
        "two_selector_majority",
        "localized_sensor_candidate",
    ]
    lines = [
        "# Label-Flow Localized Sensor Audit",
        "",
        "Question: after scale failed to reconcile selectors, can row/subject/date/block localization make the S4/Q3 direction selector-consistent?",
        "",
        "## Summary",
        "",
        f"- candidates scored: `{len(scored)}`.",
        f"- pair p90 negative: `{int(scored['pair_p90_negative'].sum())}`.",
        f"- old majority: `{int(scored['old_majority'].sum())}`.",
        f"- two-selector majority: `{int(scored['two_selector_majority'].sum())}`.",
        f"- localized sensor candidates: `{int(scored['localized_sensor_candidate'].sum())}`.",
        f"- best rank file: `{best['source_path']}`, pair p90 `{best['pair_delta_vs_a2c8_p90']:.9f}`, old p90 `{best['selector_p90_delta_vs_a2c8_public']:.9f}`, old rate `{best['beats_a2c8_scenario_rate']:.3f}`.",
    ]
    if best_old_row is not None:
        lines.append(
            f"- lowest-old-risk pairwise-negative file: `{best_old_row['source_path']}`, pair p90 `{best_old_row['pair_delta_vs_a2c8_p90']:.9f}`, old p90 `{best_old_row['selector_p90_delta_vs_a2c8_public']:.9f}`, old rate `{best_old_row['beats_a2c8_scenario_rate']:.3f}`."
        )
    lines.extend(
        [
            "",
            "## By Row Mask Kind",
            "",
            markdown_table(by_zone.head(30)),
            "",
            "## By Sensor/Mask",
            "",
            markdown_table(by_mask.head(30)),
            "",
            "## Shortlist",
            "",
            markdown_table(shortlist[[col for col in view_cols if col in shortlist.columns]]),
            "",
            "## Decision",
            "",
        ]
    )
    if int(scored["two_selector_majority"].sum()) == 0:
        lines.extend(
            [
                "- No subject/date/block/energy/sign localization created two-selector majority.",
                "- This weakens the localization-fix hypothesis: the S4/Q3 pairwise direction remains old-selector-negative even when restricted to simple hidden-DGP row subsets.",
                "- If a public sensor is used, choose it for selector calibration information, not because localization made it submit-safe.",
            ]
        )
    else:
        lines.extend(
            [
                "- At least one localized row subset created two-selector majority. This is the first evidence that localization, not target direction alone, may explain the conflict.",
                "- Before submission, inspect whether the row mask is a plausible DGP structure rather than a selector artifact.",
            ]
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{DETAIL_OUT.name}`",
            f"- `{ZONE_OUT.name}`",
            f"- `{MASK_OUT.name}`",
            f"- `{SHORTLIST_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8)
    generated = generate_localized(sample)
    known, refs, ref_vecs = build_known_and_refs(sample)
    features = build_feature_frame(generated, sample, refs, ref_vecs)
    scored = score_localized(features, known)
    by_zone = group_summary(scored, ["row_mask_kind"])
    by_mask = group_summary(scored, ["sensor_tag", "target_mask_name", "scale"])
    shortlist = scored[
        scored["localized_sensor_candidate"]
        | scored["two_selector_majority"]
        | ((scored["pair_delta_vs_a2c8_p90"] < 0.0) & (scored["pair_beats_a2c8_rate"] >= 0.70))
    ].sort_values(["two_selector_majority", "localized_sensor_candidate", "localization_rank"], ascending=[False, False, True]).head(40)

    scored.to_csv(DETAIL_OUT, index=False)
    by_zone.to_csv(ZONE_OUT, index=False)
    by_mask.to_csv(MASK_OUT, index=False)
    shortlist.to_csv(SHORTLIST_OUT, index=False)
    write_report(scored, by_zone, by_mask, shortlist)

    print(REPORT_OUT)
    print("[overall]")
    print(
        {
            "n": len(scored),
            "pair_p90_negative": int(scored["pair_p90_negative"].sum()),
            "old_majority": int(scored["old_majority"].sum()),
            "two_selector_majority": int(scored["two_selector_majority"].sum()),
            "localized_sensor_candidate": int(scored["localized_sensor_candidate"].sum()),
        }
    )
    print("[by row mask kind]")
    print(by_zone[["row_mask_kind", "n", "pair_p90_negative", "old_majority", "two_selector_majority", "localized_sensor_candidate", "best_pair_p90", "best_old_p90", "best_old_rate"]].to_string(index=False))
    print("[shortlist]")
    cols = [
        "source_path",
        "sensor_tag",
        "target_mask_name",
        "row_mask_kind",
        "row_mask_name",
        "scale",
        "row_mask_frac",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "movement_scale",
        "two_selector_majority",
    ]
    print(shortlist[cols].head(20).to_string(index=False) if not shortlist.empty else "EMPTY")


if __name__ == "__main__":
    main()
