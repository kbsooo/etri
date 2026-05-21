from __future__ import annotations

import argparse
import json
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)


KEY_COLUMNS = ["subject_id", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
DOMAIN_FAMILIES = {
    "day_slicing": ("day", "window", "sleep", "wake", "bedtime", "circadian", "chronotype", "evening", "night", "cutoff", "slicing"),
    "subject_deviation": ("subject", "baseline", "deviation", "z-score", "z score", "percentile", "routine", "personal", "quantile"),
    "rolling_memory": ("7", "14", "28", "rolling", "recent", "debt", "streak", "trend", "ewma", "recovery"),
    "episode": ("episode", "burst", "fragment", "onset", "wake", "bed", "transition", "stillness", "sedentary", "micro"),
    "missingness": ("missing", "coverage", "sensor", "off", "blackout", "imputation", "mask"),
    "cross_modal": ("cross", "modal", "gps", "phone", "screen", "step", "accel", "activity", "coherence", "agreement"),
    "motif_retrieval": ("motif", "prototype", "retrieval", "neighbor", "cluster", "vq", "graph", "kmeans", "similar"),
    "token_ssl": ("transformer", "token", "ssl", "masked", "contrastive", "autoencoder", "forecast", "sequence", "encoder"),
    "target_view": ("q1", "q2", "q3", "s1", "s2", "s3", "s4", "target"),
}
FAMILY_TO_STAGE = {
    "day_slicing": "day_state_features",
    "subject_deviation": "subject_relative_features",
    "rolling_memory": "past_context_features",
    "episode": "token_episode_features",
    "missingness": "value_mask_token_features",
    "cross_modal": "cross_modal_token_features",
    "motif_retrieval": "unsupervised_state_diagnostics",
    "token_ssl": "encoder_ssl_pretraining",
    "target_view": "decoder_probe_later",
    "misc_domain": "manual_review",
}


def slugify(text: str, max_len: int = 80) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9가-힣]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:max_len] or "idea"


def extract_ideas(path: Path, source: str) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    rows: list[dict[str, object]] = []
    seen = set()
    for line in text.splitlines():
        raw = line.strip()
        match = re.match(r"^(?:[-*]\s*)?(?:\*\*)?(\d{1,3})[.)]?\s*(?:\*\*)?\s*(.+)$", raw)
        if not match:
            continue
        idx = int(match.group(1))
        body = re.sub(r"\s+", " ", match.group(2)).strip()
        if len(body) < 8 or body in seen:
            continue
        seen.add(body)
        low = body.lower()
        families = [name for name, tokens in DOMAIN_FAMILIES.items() if any(token in low for token in tokens)]
        if not families:
            families = ["misc_domain"]
        risk = "low"
        if any(token in low for token in ("pseudo", "label", "teacher", "target mean", "distillation")):
            risk = "high"
        elif any(token in low for token in ("retrieval", "neighbor", "prototype", "cluster", "future", "test", "gps", "home")):
            risk = "medium"
        implementation = "domain_state_v1"
        if "ssl" in families or "token_ssl" in families:
            implementation = "encoder_pretrain_later"
        if risk == "high":
            implementation = "hold_until_stress_test"
        primary_family = families[0]
        stage = FAMILY_TO_STAGE.get(primary_family, "manual_review")
        status = "ready"
        if implementation == "encoder_pretrain_later":
            status = "queued_encoder_ssl"
        elif implementation == "hold_until_stress_test":
            status = "gated"
        rows.append(
            {
                "source": source,
                "source_idea_no": idx,
                "idea_id": f"{source}_{idx:03d}_{slugify(body, 48)}",
                "experiment_id": f"domain_{source}_{idx:03d}",
                "idea": body,
                "families": "|".join(families),
                "experiment_family": primary_family,
                "experiment_stage": stage,
                "risk": risk,
                "implementation_batch": implementation,
                "status": status,
                "expected_artifact": (
                    "artifacts/domain_encoder_tokens_v1.npz"
                    if implementation == "encoder_pretrain_later"
                    else "artifacts/domain_state_features_v1.parquet"
                    if implementation == "domain_state_v1"
                    else "experiments/domain_idea_bank/stress_test_queue.json"
                ),
                "validation_gate": (
                    "ssl_reconstruction_and_drift"
                    if implementation == "encoder_pretrain_later"
                    else "feature_schema_and_unsupervised_diagnostics"
                    if implementation == "domain_state_v1"
                    else "nested_oof_before_label_use"
                ),
            }
        )
    return rows


def safe_div(num: pd.Series, den: pd.Series | float, eps: float = 1e-6) -> pd.Series:
    return num.astype(float) / (np.abs(den).astype(float) + eps)


def entropy_from_columns(frame: pd.DataFrame, cols: list[str]) -> pd.Series:
    vals = frame[cols].fillna(0).clip(lower=0).to_numpy(float)
    total = vals.sum(axis=1, keepdims=True)
    prob = np.divide(vals, np.maximum(total, 1e-9), out=np.zeros_like(vals), where=total > 0)
    ent = -(prob * np.log(np.maximum(prob, 1e-12))).sum(axis=1)
    return pd.Series(ent, index=frame.index)


def add_ratio_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    day_step = out.get("day_step_sum", pd.Series(0, index=out.index)).fillna(0)
    day_screen = out.get("day_screen_on_ratio", pd.Series(0, index=out.index)).fillna(0)
    night_screen = out.get("z_night_screen_on_ratio", pd.Series(0, index=out.index)).fillna(0)
    evening_screen = out.get("z_evening_screen_on_ratio", pd.Series(0, index=out.index)).fillna(0)
    late_screen = out.get("z_lateNight_screen_on_ratio", pd.Series(0, index=out.index)).fillna(0)
    night_step = out.get("z_night_step_sum", pd.Series(0, index=out.index)).fillna(0)
    evening_step = out.get("z_evening_step_sum", pd.Series(0, index=out.index)).fillna(0)
    day_gps = out.get("day_gps_speed_mean", pd.Series(0, index=out.index)).fillna(0)
    day_hr = out.get("day_hr_mean", pd.Series(np.nan, index=out.index))

    out["ds_night_screen_share"] = safe_div(night_screen, day_screen + 1e-3)
    out["ds_evening_screen_share"] = safe_div(evening_screen + late_screen, day_screen + 1e-3)
    out["ds_night_step_share"] = safe_div(night_step, day_step + 1.0)
    out["ds_evening_step_share"] = safe_div(evening_step, day_step + 1.0)
    out["ds_screen_per_1k_steps"] = safe_div(day_screen, np.log1p(day_step))
    out["ds_mobility_phone_gap"] = day_gps - day_screen
    out["ds_body_phone_gap"] = np.log1p(day_step) - day_screen
    out["ds_hr_per_activity"] = safe_div(day_hr, np.log1p(day_step))
    out["ds_prebed_phone_total"] = out[[c for c in out.columns if c.startswith("prebed_") and c.endswith("_sec")]].fillna(0).sum(axis=1)
    app_cols = [c for c in out.columns if c.startswith("app_") and c.endswith("_sec")]
    prebed_cols = [c for c in out.columns if c.startswith("prebed_") and c.endswith("_sec")]
    if app_cols:
        out["ds_app_entropy"] = entropy_from_columns(out, app_cols)
        out["ds_app_total_sec"] = out[app_cols].fillna(0).sum(axis=1)
    if prebed_cols:
        out["ds_prebed_app_entropy"] = entropy_from_columns(out, prebed_cols)
        out["ds_prebed_share"] = safe_div(out["ds_prebed_phone_total"], out.get("ds_app_total_sec", pd.Series(0, index=out.index)) + 1.0)
    place_cols = [c for c in ["home_x", "work_or_school_x", "other_x", "elsewhere_x"] if c in out.columns]
    if place_cols:
        out["ds_place_entropy"] = entropy_from_columns(out, place_cols)
    return out


def add_subject_context(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True).copy()
    numeric = [c for c in out.select_dtypes(include=[np.number]).columns if c not in TARGET_COLUMNS]
    grouped = out.groupby("subject_id", sort=False)
    for col in numeric:
        med = grouped[col].transform("median")
        mad = grouped[col].transform(lambda s: np.nanmedian(np.abs(s - np.nanmedian(s))) if s.notna().any() else np.nan)
        out[f"dev_{col}"] = out[col] - med
        out[f"rz_{col}"] = (out[col] - med) / (mad + 1e-6)
    compact_cols = [
        c
        for c in numeric
        if any(token in c for token in ("step", "screen", "sleep", "hr", "gps", "home", "missing", "coverage", "prebed", "entropy", "gap"))
    ][:80]
    for col in compact_cols:
        for window in (3, 7, 14, 28):
            past_mean = grouped[col].transform(lambda s, w=window: s.shift(1).rolling(w, min_periods=2).mean())
            past_std = grouped[col].transform(lambda s, w=window: s.shift(1).rolling(w, min_periods=3).std(ddof=0))
            out[f"roll{window}_delta_{col}"] = out[col] - past_mean
            out[f"roll{window}_z_{col}"] = (out[col] - past_mean) / (past_std + 1e-6)
    date = pd.to_datetime(out["lifelog_date"])
    out["ds_weekday"] = date.dt.weekday.astype(float)
    out["ds_is_weekend"] = (date.dt.weekday >= 5).astype(float)
    out["ds_day_index"] = (date - date.min()).dt.days.astype(float)
    return out


def longest_run(values: np.ndarray) -> float:
    best = 0
    cur = 0
    for value in values.astype(bool):
        cur = cur + 1 if value else 0
        best = max(best, cur)
    return float(best)


def first_idx(values: np.ndarray) -> float:
    idx = np.flatnonzero(values.astype(bool))
    return float(idx[0]) if len(idx) else np.nan


def last_idx(values: np.ndarray) -> float:
    idx = np.flatnonzero(values.astype(bool))
    return float(idx[-1]) if len(idx) else np.nan


def aggregate_token_grid(grid: pd.DataFrame) -> pd.DataFrame:
    rows = []
    event_cols = [c for c in grid.columns if c.startswith("ev_") and not c.endswith(("_run", "_until_next"))]
    value_cols = [c for c in grid.select_dtypes(include=[np.number]).columns if c != "tok"]
    for (subject, date), group in grid.groupby(["subject_id", "date"], sort=False):
        g = group.sort_values("tok")
        row: dict[str, object] = {"subject_id": subject, "lifelog_date": date}
        for col in value_cols:
            values = pd.to_numeric(g[col], errors="coerce")
            if col.startswith("ev_") or col.endswith(("_n", "_rows")):
                row[f"ep_{col}_sum"] = float(values.fillna(0).sum())
                row[f"ep_{col}_ratio"] = float(values.fillna(0).mean())
            elif any(token in col for token in ("screen", "step", "gps", "hr", "charging", "usage", "light")):
                row[f"ep_{col}_mean"] = float(values.mean()) if values.notna().any() else np.nan
                row[f"ep_{col}_max"] = float(values.max()) if values.notna().any() else np.nan
                row[f"ep_{col}_std"] = float(values.std(ddof=0)) if values.notna().any() else np.nan
        for col in ["ev_phone_active", "ev_moving", "ev_no_wear", "ev_low_coverage", "ev_charging_on"]:
            if col in g:
                arr = g[col].fillna(0).to_numpy(float)
                row[f"ep_{col}_first_tok"] = first_idx(arr)
                row[f"ep_{col}_last_tok"] = last_idx(arr)
                row[f"ep_{col}_longest_run"] = longest_run(arr)
        if {"ev_phone_active", "ev_moving"}.issubset(g.columns):
            phone = g["ev_phone_active"].fillna(0).to_numpy(float)
            moving = g["ev_moving"].fillna(0).to_numpy(float)
            row["ep_phone_still_ratio"] = float(((phone == 1) & (moving == 0)).mean())
            row["ep_move_phone_silent_ratio"] = float(((phone == 0) & (moving == 1)).mean())
            row["ep_phone_move_agreement"] = float((phone == moving).mean())
        if {"ev_phone_active", "ev_no_wear"}.issubset(g.columns):
            phone = g["ev_phone_active"].fillna(0).to_numpy(float)
            nowear = g["ev_no_wear"].fillna(0).to_numpy(float)
            row["ep_phone_nowear_contradiction"] = float(((phone == 1) & (nowear == 1)).mean())
        night = g[g["tok"].isin(list(range(0, 12)) + list(range(42, 48)))]
        if len(night):
            for col in ["ev_phone_active", "ev_moving", "ev_no_wear", "ev_low_coverage"]:
                if col in night:
                    row[f"ep_night_{col}_ratio"] = float(night[col].fillna(0).mean())
        rows.append(row)
    return pd.DataFrame(rows)


def add_motif_features(frame: pd.DataFrame, n_clusters: int, seed: int) -> pd.DataFrame:
    out = frame.copy()
    cols = [c for c in out.select_dtypes(include=[np.number]).columns if c not in TARGET_COLUMNS]
    if len(out) < n_clusters or not cols:
        return out
    selected = [c for c in cols if c.startswith(("ds_", "ep_", "roll7_", "roll14_", "dev_"))][:300]
    if len(selected) < 4:
        selected = cols[: min(100, len(cols))]
    x = out[selected].replace([np.inf, -np.inf], np.nan).to_numpy(float)
    x = StandardScaler().fit_transform(SimpleImputer(strategy="median", keep_empty_features=True).fit_transform(x))
    kmeans = KMeans(n_clusters=n_clusters, random_state=seed, n_init=20)
    labels = kmeans.fit_predict(x)
    dists = kmeans.transform(x)
    out["motif_cluster"] = labels.astype(float)
    out["motif_distance_min"] = dists.min(axis=1)
    out["motif_distance_margin"] = np.partition(dists, 1, axis=1)[:, 1] - dists.min(axis=1)
    for k in range(n_clusters):
        out[f"motif_dist_{k}"] = dists[:, k]
    return out


def build_domain_features(master_path: Path, grid_path: Path, output_path: Path, n_clusters: int, seed: int) -> pd.DataFrame:
    master = pd.read_parquet(master_path).copy()
    master["subject_id"] = master["subject_id"].astype(str)
    master["lifelog_date"] = pd.to_datetime(master["lifelog_date"]).dt.strftime("%Y-%m-%d")
    drop_cols = ["role", "date", "sleep_date", *TARGET_COLUMNS]
    base = master.drop(columns=[c for c in drop_cols if c in master.columns])
    base = add_ratio_features(base)
    if grid_path.exists():
        grid = pd.read_parquet(grid_path)
        grid["subject_id"] = grid["subject_id"].astype(str)
        grid["date"] = grid["date"].astype(str)
        episode = aggregate_token_grid(grid)
        base = base.merge(episode, on=KEY_COLUMNS, how="left", validate="one_to_one")
    base = add_subject_context(base)
    base = add_motif_features(base, n_clusters=n_clusters, seed=seed)
    base = base.replace([np.inf, -np.inf], np.nan)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    base.to_parquet(output_path, index=False)
    return base


def write_manifest(idea_paths: list[Path], output_dir: Path) -> pd.DataFrame:
    rows = []
    for path in idea_paths:
        rows.extend(extract_ideas(path, path.stem.replace("idea_", "")))
    manifest = pd.DataFrame(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(output_dir / "domain_idea_manifest.csv", index=False)
    (output_dir / "domain_idea_manifest.json").write_text(
        json.dumps(manifest.to_dict(orient="records"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    family_counts = manifest.assign(families=manifest["families"].str.split("|")).explode("families")["families"].value_counts()
    batch_counts = manifest["implementation_batch"].value_counts()

    def counts_table(counts: pd.Series) -> str:
        lines = ["| name | count |", "| --- | ---: |"]
        lines.extend(f"| {idx} | {int(value)} |" for idx, value in counts.items())
        return "\n".join(lines)

    md = [
        "# Domain Idea Manifest",
        "",
        f"- Source files: `{', '.join(str(p) for p in idea_paths)}`",
        f"- Parsed ideas: `{len(manifest)}`",
        "",
        "## Family Counts",
        "",
        counts_table(family_counts),
        "",
        "## Implementation Batches",
        "",
        counts_table(batch_counts),
        "",
        "## Notes",
        "",
        "- `domain_state_v1` ideas are represented by sleep/routine/debt/episode/missingness/cross-modal/motif feature families in `artifacts/domain_state_features_v1.parquet`.",
        "- `encoder_pretrain_later` ideas need a separate SSL/token pretraining run after the feature bank is validated.",
        "- `hold_until_stress_test` ideas mention labels/pseudo labels/target means and are intentionally gated behind nested validation.",
        "- Each row has an `experiment_id`, `experiment_stage`, `status`, `expected_artifact`, and `validation_gate` so it can be routed into repeatable experiment runners.",
    ]
    (output_dir / "domain_idea_manifest.md").write_text("\n".join(md), encoding="utf-8")
    return manifest


def run(args: argparse.Namespace) -> None:
    idea_paths = [Path(p) for p in args.idea_paths]
    manifest = write_manifest(idea_paths, Path(args.experiment_dir))
    features = build_domain_features(
        Path(args.master_path),
        Path(args.grid_path),
        Path(args.output_path),
        n_clusters=args.n_clusters,
        seed=args.seed,
    )
    numeric_cols = [c for c in features.select_dtypes(include=[np.number]).columns if c not in TARGET_COLUMNS]
    report = {
        "manifest_ideas": int(len(manifest)),
        "feature_path": args.output_path,
        "shape": list(features.shape),
        "n_numeric_features": len(numeric_cols),
        "families": sorted(set("|".join(manifest["families"].fillna("")).split("|"))),
        "date_min": str(features["lifelog_date"].min()),
        "date_max": str(features["lifelog_date"].max()),
        "subjects": sorted(features["subject_id"].astype(str).unique().tolist()),
    }
    out_dir = Path(args.experiment_dir)
    (out_dir / "domain_state_features_v1_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Domain State Features v1",
        "",
        "## Goal",
        "",
        "Convert the 300 imported data-engineering ideas into a traceable feature bank focused on behavioral-day state rather than raw sensor totals.",
        "",
        "## Implemented Families",
        "",
        "- Day/time slicing proxies from existing night/evening/prebed/sleep-window columns.",
        "- Subject-relative routine rupture via median/MAD residuals.",
        "- 3/7/14/28-day past-only rolling deltas and z-scores.",
        "- Episode/missingness features from the 30-minute event-hybrid token grid.",
        "- Cross-modal contradiction features such as phone-active while not moving and moving while phone-silent.",
        "- App/place entropy and prebed usage ratios.",
        "- Unsupervised motif cluster distances over the domain-state feature space.",
        "",
        "## Output",
        "",
        f"- Feature path: `{args.output_path}`",
        f"- Shape: `{features.shape[0]} x {features.shape[1]}`",
        f"- Numeric features: `{len(numeric_cols)}`",
        f"- Parsed ideas: `{len(manifest)}`",
    ]
    (out_dir / "domain_state_features_v1_report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build domain-state feature bank from 300 data-engineering ideas.")
    parser.add_argument("--idea-paths", nargs="+", default=["idea_gpt.md", "idea_claude.md", "idea_gemini.md"])
    parser.add_argument("--master-path", default="artifacts/10_master_daily.parquet")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--output-path", default="artifacts/domain_state_features_v1.parquet")
    parser.add_argument("--experiment-dir", default="experiments/domain_idea_bank")
    parser.add_argument("--n-clusters", type=int, default=12)
    parser.add_argument("--seed", type=int, default=2026)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
