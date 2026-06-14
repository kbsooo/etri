#!/usr/bin/env python3
"""Team wrapper for the action-tail representation world-model boundary."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_action_tail_representation_world_model_core import run  # noqa: E402
from hsjepa_core.run_learned_listener_responsibility_pretext_core import json_safe  # noqa: E402


if __name__ == "__main__":
    print(json.dumps(json_safe(run()), ensure_ascii=False, indent=2))
