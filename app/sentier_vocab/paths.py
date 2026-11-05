"""Repo-root-relative path constants (app/sentier_vocab/paths.py -> repo root is parents[2])."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = REPO_ROOT / "schemas"
TERM_SCHEMA = SCHEMAS_DIR / "term.yaml"
RELATION_SCHEMA = SCHEMAS_DIR / "relation.yaml"
TERMS_DIR = REPO_ROOT / "terms"
RELATIONS_DIR = REPO_ROOT / "relations"
OUTPUT_DIR = REPO_ROOT / "output"
