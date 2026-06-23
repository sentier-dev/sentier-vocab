"""Command-line entry point: `python -m sentier_vocab <command>`."""

import argparse
from pathlib import Path

from sentier_vocab import paths
from sentier_vocab.coverage import write as write_coverage
from sentier_vocab.generate import generate_sources

# Maps a category to its LinkML schema filename under schemas/. The source data for a
# category is *every* `*.yaml`/`*.parquet` file in data/<category>/, merged into one TTL
# (e.g. data/products/ may hold curated `core.yaml` plus bulk `foodex2.parquet`).
NATIVE_CATEGORIES = {
    "elementary-flows": "elementary-flow.yaml",
    "flow-properties": "flow-property.yaml",
    "unit-groups": "unit-group.yaml",
    "products": "product.yaml",
    "impact-categories": "impact-category.yaml",
    "lcia-methods": "lcia-method.yaml",
    "sources": "source.yaml",
    "contacts": "contact.yaml",
    "model-terms": "model-term.yaml",
    "characterization-factors": "characterization-factor.yaml",
    "processes": "process.yaml",
    "organisms": "organism.yaml",
    "qualifiers": "qualifier.yaml",
}

# Source file extensions a category directory may contain.
SOURCE_GLOBS = ("*.yaml", "*.yml", "*.parquet")

# Curated source stems that keep the bare ``<category>.ttl`` output name (committed,
# diff-friendly). Any other source emits ``<category>.<source-stem>.ttl`` — bulk imports
# (e.g. ``foodex2.parquet`` -> ``organisms.foodex2.ttl``) which are gitignored and
# regenerated at deploy. One output TTL per source file; all share the category scheme.
PRIMARY_STEMS = {"core", "water"}


def _category_sources(category: str) -> list[Path]:
    """All source files for a category, sorted for deterministic output order."""
    category_dir = paths.DATA_DIR / category
    files = [f for pattern in SOURCE_GLOBS for f in category_dir.glob(pattern)]
    return sorted(files)


def _output_name(category_stem: str, source: Path) -> str:
    if source.stem in PRIMARY_STEMS:
        return f"{category_stem}.ttl"
    return f"{category_stem}.{source.stem}.ttl"


def cmd_generate(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir) if args.output_dir else paths.OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    for category, schema_name in NATIVE_CATEGORIES.items():
        sources = _category_sources(category)
        if not sources:
            print(f"skip {category}: no source files in {paths.DATA_DIR / category}")
            continue
        stem = "flows" if category == "elementary-flows" else category
        schema_path = paths.SCHEMAS_DIR / schema_name
        for source in sources:
            out = generate_sources(
                schema_path=schema_path,
                data_paths=[source],
                output_path=output_dir / _output_name(stem, source),
            )
            print(f"wrote {out} (from {source.name})")


def cmd_coverage(args: argparse.Namespace) -> None:
    out = write_coverage(args.output or (paths.REPO_ROOT / "docs" / "COVERAGE.md"))
    print(f"wrote {out}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="sentier_vocab")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Validate native data and emit TTL.")
    gen.add_argument("--output-dir", default=None, help="Directory for generated TTL.")
    gen.set_defaults(func=cmd_generate)

    cov = sub.add_parser("coverage", help="Regenerate docs/COVERAGE.md.")
    cov.add_argument("--output", default=None, help="Output path for the coverage matrix.")
    cov.set_defaults(func=cmd_coverage)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
