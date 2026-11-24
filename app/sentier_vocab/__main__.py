"""Command-line entry point: ``python -m sentier_vocab <command>``.

Commands: validate, generate, coverage, duplicate-flows, pyst-plan, pyst-push, pyst-remove.
"""

import argparse
import sys
from pathlib import Path

from sentier_vocab import flow_identity, paths
from sentier_vocab.coverage import write as write_coverage
from sentier_vocab.generate import generate
from sentier_vocab.layers import load_relations, load_terms
from sentier_vocab.validate import validate


def _layer_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--terms", default=str(paths.TERMS_DIR), help="terms/ directory")
    parser.add_argument(
        "--relations", default=str(paths.RELATIONS_DIR), help="relations/ directory"
    )


def _known_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--known-duplicates",
        default=None,
        help="Directory of the per-release lists of accepted duplicate flows "
        "(default: schemas/known-duplicate-flows/ beside the terms/ directory).",
    )


def cmd_validate(args: argparse.Namespace) -> int:
    errors = validate(args.terms, args.relations, args.known_duplicates)
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


def _pyst_plan(args: argparse.Namespace):
    from sentier_vocab.pyst.publication import build_plan, load_config

    return build_plan(
        load_terms(args.terms), load_relations(args.relations), load_config(args.config)
    )


def _print_plan(plan) -> None:
    for scheme in plan.schemes:
        note = "  (already on the server)" if scheme.existing else ""
        print(f"{len(scheme.concepts):>7}  {scheme.iri}{note}")
    print(f"{sum(len(s.concepts) for s in plan.schemes):>7}  concepts")
    print(f"{len(plan.relationships):>7}  relationships")
    print(f"{plan.skipped_terms:>7}  terms left out (skip)")


def cmd_pyst_plan(args: argparse.Namespace) -> int:
    from sentier_vocab.pyst.publication import PlanError, check_against_pyst

    try:
        plan = _pyst_plan(args)
    except PlanError as err:
        print(err)
        return 1
    _print_plan(plan)
    if args.check:
        errors = check_against_pyst(plan)
        for line in errors[:50]:
            print(line)
        print(f"{len(errors)} document(s) refused by PyST's request models")
        return 1 if errors else 0
    return 0


def cmd_pyst_send(args: argparse.Namespace) -> int:
    from sentier_vocab.pyst.publication import PlanError
    from sentier_vocab.pyst.push import PushError, connect, push, remove

    action = remove if args.command == "pyst-remove" else push
    try:
        plan = _pyst_plan(args)
        report = action(plan, connect(args.server), only=args.scheme, workers=args.workers)
    except (PlanError, PushError) as err:
        print(err, file=sys.stderr)
        return 1
    print(report)
    return 0


def _pyst_args(parser: argparse.ArgumentParser) -> None:
    _layer_args(parser)
    parser.add_argument("--config", default=str(paths.PYST_CONFIG), help="schemas/pyst.yaml")


def _server_args(parser: argparse.ArgumentParser) -> None:
    _pyst_args(parser)
    parser.add_argument("--server", required=True, help="Server URL, e.g. http://localhost:8000")
    parser.add_argument(
        "--scheme", action="append", help="Only this scheme IRI (repeatable). Default: all."
    )
    parser.add_argument("--workers", type=int, default=1, help="Parallel requests.")


def cmd_duplicate_flows(args: argparse.Namespace) -> int:
    terms = load_terms(args.terms)
    if args.release not in flow_identity.flows_by_release(terms):
        print(f"no term file of release {args.release!r} in {args.terms}", file=sys.stderr)
        return 1
    groups = flow_identity.colliding_groups(terms, load_relations(args.relations))
    sys.stdout.write(flow_identity.render(args.release, groups.get(args.release, {})))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sentier_vocab")
    sub = parser.add_subparsers(dest="command", required=True)

    val = sub.add_parser("validate", help="Check terms/ and relations/ against the two contracts.")
    _layer_args(val)
    _known_arg(val)
    val.set_defaults(func=cmd_validate)

    gen = sub.add_parser("generate", help="Validate, then emit TTL.")
    _layer_args(gen)
    _known_arg(gen)
    gen.add_argument("--output-dir", default=str(paths.OUTPUT_DIR), help="Directory for TTL.")
    gen.set_defaults(func=cmd_generate)

    dup = sub.add_parser(
        "duplicate-flows",
        help="Print the flows of a release that share their identity (label, compartment, "
        "sub_compartment, unit): the content of its known-duplicate-flows list.",
    )
    dup.add_argument("release", help="Source release, e.g. ef-3.1.")
    _layer_args(dup)
    dup.set_defaults(func=cmd_duplicate_flows)

    cov = sub.add_parser("coverage", help="Regenerate docs/COVERAGE.md.")
    cov.add_argument("--output", default=None, help="Output path for the coverage matrix.")
    cov.set_defaults(func=cmd_coverage)

    plan = sub.add_parser("pyst-plan", help="Show what would be published on the server.")
    _pyst_args(plan)
    plan.add_argument(
        "--check", action="store_true", help="Validate with PyST's request models (pyst extra)."
    )
    plan.set_defaults(func=cmd_pyst_plan)

    send = sub.add_parser(
        "pyst-push", help="Add the plan to a server. Only adds; the write key is PYST_API_KEY."
    )
    _server_args(send)
    send.set_defaults(func=cmd_pyst_send)

    rem = sub.add_parser("pyst-remove", help="Delete from a server what pyst-push adds.")
    _server_args(rem)
    rem.set_defaults(func=cmd_pyst_send)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
