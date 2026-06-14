#!/usr/bin/env python3
"""Team-facing entry point for the HS-JEPA drift line control experiment."""

from __future__ import annotations

from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / "sleep_competition_adapter" / "human_state_drift_line_explorer.py"


if __name__ == "__main__":
    runpy.run_path(str(IMPLEMENTATION), run_name="__main__")
