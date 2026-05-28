from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
BLEND_WEIGHTS = [0.25, 0.35, 0.50, 0.65, 0.75, 0.85]
Q3OFF_BASE_CHANGED = ["Q1", "Q2", "S1", "S2", "S3", "S4"]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def changed_targets(ops: str, source_base: str) -> str:
    targets = set(Q3OFF_BASE_CHANGED if source_base == "q3off650" else [])
    for chunk in str(ops).split(";"):
        chunk = chunk.strip()
        if ":" in chunk:
            targets.add(chunk.split(":", 1)[0])
    return ",".join([t for t in TARGETS if t in targets])


def submission_stats(path: Path, anchor_sub: pd.DataFrame) -> dict[str, float]:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(SUB_KEY).reset_index(drop=True)
    assert df[SUB_KEY].equals(anchor_sub[SUB_KEY])
    pred = df[TARGETS].to_numpy(dtype=float)
    anchor = anchor_sub[TARGETS].to_numpy(dtype=float)
    dist = np.abs(pred - anchor)
    return {
        "distance_abs_mean_vs_anchor": float(dist.mean()),
        "distance_abs_p90_vs_anchor": float(np.quantile(dist, 0.90)),
        "submission_min": float(pred.min()),
        "submission_max": float(pred.max()),
    }


def build_multitarget_catalog(anchor_loss: float, anchor_sub: pd.DataFrame) -> pd.DataFrame:
    frames = [
        ("anchor578", OUT / "presleep_anchor_candidate_summary.csv", OUT / "presleep_anchor_saved_candidates.csv"),
        ("q3off650", OUT / "presleep_multitarget_candidate_summary.csv", OUT / "presleep_multitarget_saved_candidates.csv"),
    ]
    rows = []
    for source_base, summary_path, saved_path in frames:
        summary = pd.read_csv(summary_path)
        saved = pd.read_csv(saved_path)
        merged = saved.merge(summary, on="combo", how="left", validate="one_to_one")
        for row in merged.itertuples(index=False):
            file = str(row.file)
            rows.append(
                {
                    "file": file,
                    "probe": f"{source_base}_{row.combo}",
                    "targets_changed": changed_targets(str(row.ops), source_base),
                    "source_base": source_base,
                    "note": row.note,
                    "oof_mean_loss": float(row.candidate_loss),
                    "oof_delta_vs_anchor": float(row.candidate_loss - anchor_loss),
                    "geometry_delta": float(row.geometry_delta),
                    "geometry_win_rate": float(row.geometry_win_rate),
                    **submission_stats(OUT / file, anchor_sub),
                }
            )
    catalog = pd.DataFrame(rows)
    source_rank = catalog["source_base"].map({"anchor578": 0, "q3off650": 1}).fillna(9)
    return catalog.assign(_source_rank=source_rank).sort_values(
        ["_source_rank", "oof_mean_loss", "geometry_delta"], ascending=[True, True, True]
    ).drop(columns=["_source_rank"]).reset_index(drop=True)


def blend_slug(combo: str) -> str:
    slug = combo
    if slug.startswith("presleep_core_"):
        slug = slug[len("presleep_core_") :]
    if slug.startswith("q1_s1_s4"):
        slug = "core_q1s1s4" + slug[len("q1_s1_s4") :]
    elif slug.startswith("soft"):
        slug = "core_soft" + slug[len("soft") :]
    slug = slug.replace("q3hr_ble", "q3hrble")
    return slug


def build_blend_catalog(anchor_loss: float, y: np.ndarray, anchor_sub: pd.DataFrame) -> pd.DataFrame:
    anchor_saved = pd.read_csv(OUT / "presleep_anchor_saved_candidates.csv")
    q3off_saved = pd.read_csv(OUT / "presleep_multitarget_saved_candidates.csv")
    anchor_saved = anchor_saved.set_index("combo")
    q3off_saved = q3off_saved.set_index("combo")
    combos = sorted(set(anchor_saved.index).intersection(q3off_saved.index))
    combos = [c for c in combos if "q3hr_ble" in c]
    rows = []
    for combo in combos:
        anchor_oof = clip(np.load(OUT / str(anchor_saved.loc[combo, "oof_file"])))
        q3off_oof = clip(np.load(OUT / str(q3off_saved.loc[combo, "oof_file"])))
        anchor_df = pd.read_csv(OUT / str(anchor_saved.loc[combo, "file"]), parse_dates=["sleep_date", "lifelog_date"]).sort_values(SUB_KEY).reset_index(drop=True)
        q3off_df = pd.read_csv(OUT / str(q3off_saved.loc[combo, "file"]), parse_dates=["sleep_date", "lifelog_date"]).sort_values(SUB_KEY).reset_index(drop=True)
        assert anchor_df[SUB_KEY].equals(anchor_sub[SUB_KEY])
        assert q3off_df[SUB_KEY].equals(anchor_sub[SUB_KEY])
        for weight in BLEND_WEIGHTS:
            slug = f"{blend_slug(combo)}_q3offw{int(weight * 1000):03d}"
            pred_oof = clip((1.0 - weight) * anchor_oof + weight * q3off_oof)
            out = anchor_df.copy()
            out[TARGETS] = clip((1.0 - weight) * anchor_df[TARGETS].to_numpy(float) + weight * q3off_df[TARGETS].to_numpy(float))
            file = f"submission_presleepblend_{slug}.csv"
            oof_file = f"final_presleepblend_{slug}_oof.npy"
            np.save(OUT / oof_file, pred_oof)
            out.to_csv(OUT / file, index=False)
            rows.append(
                {
                    "file": file,
                    "probe": f"presleepblend_{slug}",
                    "targets_changed": "Q1,Q2,Q3,S1,S2,S3,S4",
                    "source_base": "blend_anchor_q3off",
                    "note": f"prob blend between anchor-presleep and q3off-presleep candidates, q3off weight {weight:g}",
                    "weight_q3off": weight,
                    "oof_mean_loss": mean_loss(y, pred_oof),
                    "oof_delta_vs_anchor": mean_loss(y, pred_oof) - anchor_loss,
                    **submission_stats(OUT / file, anchor_sub),
                }
            )
    return pd.DataFrame(rows).sort_values(["oof_mean_loss", "distance_abs_mean_vs_anchor"]).reset_index(drop=True)


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv").sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    y = train[TARGETS].to_numpy(dtype=int)
    anchor_oof = clip(np.load(OUT / "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy"))
    anchor_loss = mean_loss(y, anchor_oof)
    anchor_sub = pd.read_csv(
        OUT / "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
        parse_dates=["sleep_date", "lifelog_date"],
    ).sort_values(SUB_KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SUB_KEY).reset_index(drop=True)
    assert anchor_sub[SUB_KEY].equals(sample[SUB_KEY])

    multitarget = build_multitarget_catalog(anchor_loss, anchor_sub)
    blends = build_blend_catalog(anchor_loss, y, anchor_sub)
    multitarget.to_csv(OUT / "public_presleep_multitarget_candidates.csv", index=False)
    blends.to_csv(OUT / "public_presleep_blend_candidates.csv", index=False)
    print("multitarget")
    print(multitarget.head(16).round(9).to_string(index=False))
    print("blends")
    print(blends.head(20).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
