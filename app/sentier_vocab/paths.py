"""Repo-root-relative path constants (app/sentier_vocab/paths.py -> repo root is parents[2])."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = REPO_ROOT / "schemas"
DATA_DIR = REPO_ROOT / "data"
OUTPUT_DIR = REPO_ROOT / "output"
