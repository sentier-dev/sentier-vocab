"""Validate the terms/ and relations/ layers against term.yaml and relation.yaml.

``validate`` returns every problem as one human-readable line, prefixed with the
file it was found in, so CI can print them all at once. ``validate_or_raise``
wraps that for callers that want an exception.
"""

from __future__ import annotations

import datetime as dt
from collections import Counter, defaultdict
from pathlib import Path

from sentier_vocab import paths
from sentier_vocab.errors import ValidationError
from sentier_vocab.iris import identifier_from
from sentier_vocab.layers import load_relations, load_terms, release_of
from sentier_vocab.schema import (
    Attribute,
    RelationSchema,
    TermSchema,
    load_relation_schema,
    load_term_schema,
)

STATUS = ("draft", "published", "deprecated")
UNIT_PREDICATE = "qudt:hasUnit"

#: ``{iri: (type, file)}`` for every term.
Index = dict[str, tuple[str, Path]]


def _attribute_error(name: str, value, spec: Attribute) -> str | None:
    if spec.enum is not None and value not in spec.enum:
        return f"attribute {name!r}: {value!r} is not one of {list(spec.enum)}"
    if spec.type == "date":
        try:
            dt.date.fromisoformat(str(value))
        except ValueError:
            return f"attribute {name!r}: {value!r} is not an ISO date"
    elif spec.type == "double":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return f"attribute {name!r}: {value!r} is not a double"
    elif spec.type == "list[string]":
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            return f"attribute {name!r}: {value!r} is not a list of strings"
    elif not isinstance(value, str):
        return f"attribute {name!r}: {value!r} is not a string"
    return None


def _check_required_and_status(where: str, row: dict, columns) -> list[str]:
    errors = []
    for column in columns.values():
        if column.required and row.get(column.name) in (None, ""):
            errors.append(f"{where}: column {column.name!r} is required")
    status = row.get("status")
    if status is not None and status not in STATUS:
        errors.append(f"{where}: status {status!r} is not one of {list(STATUS)}")
    return errors


def _check_term_rows(path: Path, rows: list[dict], schema: TermSchema) -> list[str]:
    errors = []
    for row in rows:
        where = f"{path.name}: {row.get('iri', '<no iri>')}"
        errors.extend(_check_required_and_status(where, row, schema.columns))
        type_name = row.get("type")
        term_type = schema.types.get(type_name)
        if term_type is None:
            errors.append(f"{where}: type {type_name!r} is not a listed type")
            continue
        if term_type.retired:
            errors.append(f"{where}: type {type_name!r} is retired")
        if not row.get("iri", "").startswith(term_type.namespace):
            errors.append(
                f"{where}: iri is not in the {type_name} namespace {term_type.namespace}"
            )
        for name, value in (row.get("attributes") or {}).items():
            spec = term_type.attributes.get(name)
            if spec is None:
                errors.append(
                    f"{where}: attribute {name!r} is not declared for type {type_name!r}"
                )
                continue
            problem = _attribute_error(name, value, spec)
            if problem:
                errors.append(f"{where}: {problem}")
    return errors


def _check_sources(path: Path, rows: list[dict], index: Index) -> list[str]:
    errors = []
    sources = {row.get("source") for row in rows if row.get("source")}
    if len(sources) > 1:
        errors.append(f"{path.name}: one source per file, found {sorted(sources)}")
    for source in sorted(sources):
        entry = index.get(source)
        if entry is None or entry[0] != "source":
            errors.append(
                f"{path.name}: source {source!r} does not resolve to a term of type source"
            )
        elif identifier_from(source) != release_of(path):
            errors.append(
                f"{path.name}: file stem {release_of(path)!r} must equal the source identifier "
                f"{identifier_from(source)!r}"
            )
    return errors


def _allowed(kinds: tuple[str, ...], type_name: str) -> bool:
    return "any" in kinds or type_name in kinds


def _check_relation_rows(
    path: Path, rows: list[dict], index: Index, rel_schema: RelationSchema
) -> list[str]:
    errors = []
    for row in rows:
        where = f"{path.name}: {row.get('subject')} {row.get('predicate')} {row.get('object')}"
        errors.extend(_check_required_and_status(where, row, rel_schema.columns))
        predicate = rel_schema.predicates.get(row.get("predicate"))
        if predicate is None:
            errors.append(f"{where}: {row.get('predicate')!r} is not a listed predicate")
            continue
        subject_type = index.get(row.get("subject"), (None, None))[0]
        if subject_type is None:
            errors.append(f"{where}: subject {row.get('subject')!r} is not a term")
        elif not _allowed(predicate.subject, subject_type):
            errors.append(
                f"{where}: {predicate.curie} does not accept subject type {subject_type!r}"
            )
        obj = row.get("object") or ""
        object_type = index.get(obj, (None, None))[0]
        if object_type is not None:
            if not _allowed(predicate.object, object_type):
                errors.append(
                    f"{where}: {predicate.curie} does not accept object type {object_type!r}"
                )
        elif not any(obj.startswith(prefix) for prefix in predicate.external):
            errors.append(
                f"{where}: object {obj!r} is neither a term nor an allowed external IRI "
                f"for {predicate.curie}"
            )
    return errors


def _check_cardinality(relations: dict[Path, list[dict]], rel_schema: RelationSchema) -> list[str]:
    counts: Counter[tuple[str, str]] = Counter()
    for rows in relations.values():
        for row in rows:
            spec = rel_schema.predicates.get(row.get("predicate"))
            if spec is not None and spec.max_one_per_subject:
                counts[(row["subject"], spec.curie)] += 1
    return [
        f"{subject}: more than one {curie} edge ({n})"
        for (subject, curie), n in sorted(counts.items())
        if n > 1
    ]


def _check_flow_identity(
    terms: dict[Path, list[dict]], relations: dict[Path, list[dict]]
) -> list[str]:
    """(label, compartment, sub_compartment, unit) is unique per file, for flows with a unit."""
    units: dict[str, str] = {}
    for rows in relations.values():
        for row in rows:
            if row.get("predicate") == UNIT_PREDICATE:
                units.setdefault(row["subject"], row["object"])
    errors = []
    for path, rows in terms.items():
        seen: dict[tuple, str] = {}
        for row in rows:
            if row.get("type") != "elementary-flow" or row["iri"] not in units:
                continue
            attrs = row.get("attributes") or {}
            key = (
                row.get("pref_label"),
                attrs.get("compartment"),
                attrs.get("sub_compartment"),
                units[row["iri"]],
            )
            if key in seen:
                errors.append(
                    f"{path.name}: flow identity {key!r} is shared by {seen[key]} and {row['iri']}"
                )
            else:
                seen[key] = row["iri"]
    return errors


def _index_terms(terms: dict[Path, list[dict]]) -> tuple[Index, list[str]]:
    index: Index = {}
    duplicates: dict[str, set[str]] = defaultdict(set)
    for path, rows in terms.items():
        for row in rows:
            iri = row.get("iri")
            if iri in index:
                duplicates[iri].update({index[iri][1].name, path.name})
            else:
                index[iri] = (row.get("type"), path)
    errors = [
        f"duplicate iri {iri} in {sorted(files)}" for iri, files in sorted(duplicates.items())
    ]
    return index, errors


def validate(
    terms_dir: Path | str = paths.TERMS_DIR,
    relations_dir: Path | str = paths.RELATIONS_DIR,
) -> list[str]:
    """Every problem in both layers as a list of lines; empty means valid."""
    schema = load_term_schema(paths.TERM_SCHEMA)
    rel_schema = load_relation_schema(paths.RELATION_SCHEMA)
    terms = load_terms(terms_dir)
    relations = load_relations(relations_dir) if Path(relations_dir).exists() else {}

    errors: list[str] = []
    for path, rows in terms.items():
        errors.extend(_check_term_rows(path, rows, schema))
    index, duplicate_errors = _index_terms(terms)
    errors.extend(duplicate_errors)
    for path, rows in terms.items():
        errors.extend(_check_sources(path, rows, index))
    for path, rows in relations.items():
        errors.extend(_check_relation_rows(path, rows, index, rel_schema))
        errors.extend(_check_sources(path, rows, index))
    errors.extend(_check_cardinality(relations, rel_schema))
    errors.extend(_check_flow_identity(terms, relations))
    return errors


def validate_or_raise(
    terms_dir: Path | str = paths.TERMS_DIR,
    relations_dir: Path | str = paths.RELATIONS_DIR,
) -> None:
    """Raise ``ValidationError`` listing every problem, or return silently."""
    errors = validate(terms_dir, relations_dir)
    if errors:
        raise ValidationError("\n".join(errors))
