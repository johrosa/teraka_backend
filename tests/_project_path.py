"""Helpers for running standalone test scripts from the tests directory."""

from pathlib import Path
import sys


def ensure_project_root() -> Path:
    project_root = Path(__file__).resolve().parents[1]
    root = str(project_root)
    if root not in sys.path:
        sys.path.insert(0, root)
    return project_root
