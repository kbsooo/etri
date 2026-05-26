from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import current_0p586_gentle_logit_calibration as glc  # noqa: E402
import current_0p591_block_label_postprocess as blp  # noqa: E402
import deep_dive_analysis as d  # noqa: E402


OUT = Path(__file__).resolve().parent
DATA = OUT.parents[0] / "data"
KEY = d.KEY
TARGETS = d.TARGETS


def selected_map(selection: pd.DataFrame, mode: str) -> dict[str, str]:
    if mode == "strict":
        keep = selection[selection["passes_strict"]].copy()
    elif mode == "loose":
        keep = selection[selection["passes_loose"]].copy()
    elif mode == "all":
        keep = selection.copy()
    else:
        raise ValueError(mode)
    keep = keep.sort_values(["target", "delta_vs_base"])
    return {str(row.target): str(row.config) for row in keep.itertuples(index=False)}


def estimate_candidate(train: pd.DataFrame, base_oof: Path, selected: dict[str, str], est_out: Path, oof_out: Path) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    current = np.load(base_oof)
    candidate = current.copy()
    for target, config_name in selected.items():
        j = TARGETS.index(target)
        cfg = glc.parse_config(config_name)
        candidate[:, j] = glc.calibrate(candidate[:, j], cfg)
    np.save(oof_out, candidate)

    rows = []
    for j, target in enumerate(TARGETS):
        current_loss = glc.srq.loss_col(y[:, j], current[:, j])
        candidate_loss = glc.srq.loss_col(y[:, j], candidate[:, j])
        rows.append(
            {
                "target": target,
                "current_loss": current_loss,
                "candidate_loss": candidate_loss,
                "delta_vs_current": candidate_loss - current_loss,
                "source": f"gentle_logit_{selected[target]}" if target in selected else "unchanged",
            }
        )
    estimate = pd.DataFrame(rows)
    estimate.loc[len(estimate)] = {
        "target": "mean",
        "current_loss": float(estimate["current_loss"].mean()),
        "candidate_loss": float(estimate["candidate_loss"].mean()),
        "delta_vs_current": float(estimate["candidate_loss"].mean() - estimate["current_loss"].mean()),
        "source": "target_mean",
    }
    estimate.to_csv(est_out, index=False)
    return estimate


def make_submission(base_sub: Path, sub: pd.DataFrame, selected: dict[str, str], sub_out: Path) -> pd.DataFrame:
    out = pd.read_csv(base_sub, parse_dates=["sleep_date", "lifelog_date"])
    out = out.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    assert out[KEY].equals(sub[KEY])
    for target, config_name in selected.items():
        cfg = glc.parse_config(config_name)
        out[target] = glc.calibrate(out[target].to_numpy(dtype=float), cfg)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    assert list(out.columns) == list(sample.columns)
    assert out[KEY].equals(sample[KEY])
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(KEY).sum() == 0
    assert ((out[TARGETS] >= 0).all().all() and (out[TARGETS] <= 1).all().all())
    out.to_csv(sub_out, index=False)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-sub", required=True)
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--selection", required=True)
    parser.add_argument("--mode", choices=["strict", "loose", "all"], default="strict")
    parser.add_argument("--sub-out", required=True)
    parser.add_argument("--est-out", required=True)
    parser.add_argument("--oof-out", required=True)
    args = parser.parse_args()

    selection = pd.read_csv(args.selection)
    selected = selected_map(selection, args.mode)
    train = blp.train_frame()
    sub = blp.sub_frame()
    estimate = estimate_candidate(train, Path(args.base_oof), selected, Path(args.est_out), Path(args.oof_out))
    out = make_submission(Path(args.base_sub), sub, selected, Path(args.sub_out))
    print("selected", selected)
    print(estimate.round(9).to_string(index=False))
    print("wrote", args.sub_out)
    print("range", float(out[TARGETS].min().min()), float(out[TARGETS].max().max()))


if __name__ == "__main__":
    main()
