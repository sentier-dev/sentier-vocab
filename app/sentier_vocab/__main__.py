"""Command-line entry point: ``python -m sentier_vocab <validate|generate|coverage>``."""

import argparse
import sys
from pathlib import Path

from sentier_vocab import paths
from sentier_vocab.coverage import write as write_coverage
from sentier_vocab.generate import generate
from sentier_vocab.validate import validate


def _layer_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--terms", default=str(paths.TERMS_DIR), help="terms/ directory")
    parser.add_argument(
        "--relations", default=str(paths.RELATIONS_DIR), help="relations/ directory"
    )


def cmd_validate(args: argparse.Namespace) -> int:
    errors = validate(args.terms, args.relations)
    for line in errors:
        print(line)
    if errors:
        print(f"{len(errors)} problem(s)")
        return 1
    print("valid")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    code = cmd_validate(args)
    if code:
        return code
    for path in generate(args.terms, args.relations, Path(args.output_dir)):
        print(f"wrote {path}")
    return 0


def cmd_coverage(args: argparse.Namespace) -> int:
    out = write_coverage(args.output or (paths.REPO_ROOT / "docs" / "COVERAGE.md"))
    print(f"wrote {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sentier_vocab")
    sub = parser.add_subparsers(dest="command", required=True)

    val = sub.add_parser("validate", help="Check terms/ and relations/ against the two contracts.")
    _layer_args(val)
    val.set_defaults(func=cmd_validate)

    gen = sub.add_parser("generate", help="Validate, then emit TTL.")
    _layer_args(gen)
    gen.add_argument("--output-dir", default=str(paths.OUTPUT_DIR), help="Directory for TTL.")
    gen.set_defaults(func=cmd_generate)

    cov = sub.add_parser("coverage", help="Regenerate docs/COVERAGE.md.")
    cov.add_argument("--output", default=None, help="Output path for the coverage matrix.")
    cov.set_defaults(func=cmd_coverage)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
