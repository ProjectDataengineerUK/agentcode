#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FEATURES_DIR = ROOT / ".agentcodex" / "features"
REPORTS_DIR = ROOT / ".agentcodex" / "reports"
ARTIFACT_RE = re.compile(r"^(?:BRAINSTORM|DEFINE|DESIGN|BUILD_REPORT|SHIPPED)_(?P<feature>[A-Z0-9_]+)\.md$")


def collect_features() -> list[str]:
    features: set[str] = set()
    for base in [FEATURES_DIR, REPORTS_DIR]:
        if not base.exists():
            continue
        for path in base.glob("*.md"):
            match = ARTIFACT_RE.match(path.name)
            if match:
                feature = match.group("feature")
                if feature != "EXAMPLE_PROJECT_FEATURE":
                    features.add(feature)
    return sorted(features)


def main() -> int:
    features = collect_features()
    if not features:
        print("No workflow features found for context synchronization.")
        return 0

    for feature in features:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "sync_context_history.py"), feature],
            cwd=str(ROOT),
            check=True,
        )

    print(f"Synchronized context history for {len(features)} feature(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
