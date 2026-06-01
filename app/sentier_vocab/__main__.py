"""Command-line entry point: `python -m sentier_vocab <command>`."""

import argparse
from pathlib import Path

from sentier_vocab import paths
from sentier_vocab.coverage import write as write_coverage
from sentier_vocab.generate import generate_category

# Maps a category to (schema filename, data filename) under schemas/ and data/<category>/.
NATIVE_CATEGORIES = {
    "elementary-flows": ("elementary-flow.yaml", "water.yaml"),
}


def cmd_generate(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir) if args.output_dir else paths.OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    for category, (schema_name, data_name) in NATIVE_CATEGORIES.items():
        out = generate_category(
            category=category,
            schema_path=paths.SCHEMAS_DIR / schema_name,
            data_path=paths.DATA_DIR / category / data_name,
            output_path=output_dir / "flows.ttl",
        )
        print(f"wrote {out}")


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
