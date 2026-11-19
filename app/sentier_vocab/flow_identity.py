"""Flow identity: (label, compartment, sub_compartment, unit) of an elementary flow.

Within one source release no two flows that state a unit may share an identity:
a reader who knows the name, where the flow goes and its unit must find one term.
The check runs over every term file of a release together, so shards hide nothing.

A source may publish true duplicates (EF 3.1 lists some flows twice under two
UUIDs). A release accepts those in ``schemas/known-duplicate-flows/<release>.txt``:
one flow IRI per line, ``#`` comments and blank lines ignored. A shared identity is
accepted only when every flow sharing it is listed. The list must not rot: a listed
IRI that is not a flow of the release, or that shares its identity with no other
flow, is an error. ``render`` writes the file from the current colliding groups
(``python -m sentier_vocab duplicate-flows <release>``).
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from sentier_vocab.layers import release_of

FLOW_TYPE = "elementary-flow"
UNIT_PREDICATE = "qudt:hasUnit"
#: Folder name of the per-release lists, under ``schemas/``.
KNOWN_DIR_NAME = "known-duplicate-flows"
COMMENT = "#"
_ABSENT = "-"

#: (pref_label, compartment, sub_compartment, unit)
Identity = tuple
#: ``{identity: [iri, ...]}`` for the identities more than one flow has.
Groups = dict[Identity, list[str]]


def default_known_dir(terms_dir: Path | str) -> Path:
    """The lists of the tree ``terms_dir`` belongs to: ``schemas/<KNOWN_DIR_NAME>/``
    beside it."""
    return Path(terms_dir).parent / "schemas" / KNOWN_DIR_NAME


def _units(relations: dict[Path, list[dict]]) -> dict[str, str]:
    units: dict[str, str] = {}
    for rows in relations.values():
        for row in rows:
            if row.get("predicate") == UNIT_PREDICATE:
                units.setdefault(row["subject"], row["object"])
    return units


def flows_by_release(terms: dict[Path, list[dict]]) -> dict[str, set[str]]:
    """IRIs of the elementary flows of each release that has term files."""
    flows: dict[str, set[str]] = {}
    for path, rows in terms.items():
        iris = flows.setdefault(release_of(path), set())
        iris.update(row["iri"] for row in rows if row.get("type") == FLOW_TYPE)
    return flows


def colliding_groups(
    terms: dict[Path, list[dict]], relations: dict[Path, list[dict]]
) -> dict[str, Groups]:
    """Per release, the identities that several flows with a unit share."""
    units = _units(relations)
    by_release: dict[str, dict[Identity, list[str]]] = defaultdict(lambda: defaultdict(list))
    for path, rows in terms.items():
        for row in rows:
            if row.get("type") != FLOW_TYPE or row["iri"] not in units:
                continue
            attrs = row.get("attributes") or {}
            key = (
                row.get("pref_label"),
                attrs.get("compartment"),
                attrs.get("sub_compartment"),
                units[row["iri"]],
            )
            by_release[release_of(path)][key].append(row["iri"])
    return {
        release: {key: sorted(iris) for key, iris in groups.items() if len(iris) > 1}
        for release, groups in by_release.items()
    }


def read_known(known_dir: Path | str) -> dict[str, tuple[Path, list[str]]]:
    """``{release: (file, listed IRIs in file order)}`` for every list in ``known_dir``."""
    known: dict[str, tuple[Path, list[str]]] = {}
    for path in sorted(Path(known_dir).glob("*.txt")):
        lines = (line.strip() for line in path.read_text(encoding="utf-8").splitlines())
        known[path.stem] = (
            path,
            [line for line in lines if line and not line.startswith(COMMENT)],
        )
    return known


def check(
    terms: dict[Path, list[dict]],
    relations: dict[Path, list[dict]],
    known_dir: Path | str,
) -> list[str]:
    """Every shared identity that is not accepted, and every stale list entry."""
    groups = colliding_groups(terms, relations)
    flows = flows_by_release(terms)
    known = read_known(known_dir)
    errors = []
    for release in sorted(groups):
        listed = set(known.get(release, (None, []))[1])
        for key, iris in sorted(groups[release].items(), key=lambda item: item[1]):
            unlisted = [iri for iri in iris if iri not in listed]
            if not unlisted:
                continue
            line = f"{release}: flow identity {key!r} is shared by {', '.join(iris)}"
            if len(unlisted) < len(iris):
                line += f"; not listed as known duplicates: {', '.join(unlisted)}"
            errors.append(line)
    for release, (path, iris) in known.items():
        colliding = {iri for group in groups.get(release, {}).values() for iri in group}
        for iri, count in Counter(iris).items():
            where = f"{path.name}: known duplicate {iri}"
            if count > 1:
                errors.append(f"{where} is listed more than once")
            if iri not in flows.get(release, ()):
                errors.append(f"{where} is not an elementary flow of release {release}")
            elif iri not in colliding:
                errors.append(
                    f"{where} shares its identity with no other flow of release {release}"
                )
    return errors


def _shown(value: object) -> str:
    return _ABSENT if value is None else str(value)


def render(release: str, groups: Groups) -> str:
    """The content of ``schemas/known-duplicate-flows/<release>.txt`` for ``groups``."""
    ordered = sorted(groups.items(), key=lambda item: tuple(_shown(v) for v in item[0]))
    lines = [
        f"# Known duplicate flows of the release {release}.",
        "#",
        "# Flows that share their identity (label | compartment | sub_compartment | unit)",
        "# with another flow of the release and are accepted as the source publishes",
        "# them. `python -m sentier_vocab validate` accepts a shared identity only when",
        "# every flow sharing it is listed here, and refuses a listed flow that is not a",
        "# flow of the release or no longer shares its identity.",
        "#",
        "# Generated, then reviewed. To regenerate:",
        f"#   uv run python -m sentier_vocab duplicate-flows {release} \\",
        f"#     > schemas/{KNOWN_DIR_NAME}/{release}.txt",
        "#",
        f"# {len(groups)} identities shared by {sum(map(len, groups.values()))} flows.",
    ]
    for key, iris in ordered:
        lines += ["", f"# {' | '.join(_shown(value) for value in key)}", *iris]
    return "\n".join(lines) + "\n"
