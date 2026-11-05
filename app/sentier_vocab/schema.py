"""Load the two plain-YAML contracts, ``schemas/term.yaml`` and ``schemas/relation.yaml``.

Everything the validator and the generator need to know about a term type or a
predicate is read from these files; nothing is hardcoded in Python.
"""

from __future__ import annotations

import types
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Mapping

import yaml

SKOS_CONCEPT = "http://www.w3.org/2004/02/skos/core#Concept"
COLUMN_TYPES = frozenset({"string", "list[string]", "json"})
ATTRIBUTE_TYPES = frozenset({"string", "date", "double", "uri", "list[string]"})


def expand_curie(prefixes: Mapping[str, str], value: str) -> str:
    """Expand ``prefix:local`` with ``prefixes``; a full IRI passes through."""
    if "://" in value:
        return value
    prefix, _, local = value.partition(":")
    return prefixes[prefix] + local


def _tuple(value) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple)):
        return tuple(str(v) for v in value)
    return (str(value),)


def _frozen(mapping: dict) -> Mapping:
    return types.MappingProxyType(dict(mapping))


@dataclass(frozen=True)
class Column:
    name: str
    type: str
    required: bool = False
    unique: bool = False
    enum: tuple[str, ...] | str | None = None  # tuple of values, or the section name
    predicate: str | None = None  # expanded IRI
    lang: str | None = None


@dataclass(frozen=True)
class Attribute:
    name: str
    predicate: str  # expanded IRI
    type: str = "string"
    lang: str | None = None
    enum: tuple[str, ...] | None = None


@dataclass(frozen=True)
class TermType:
    name: str
    category: str
    namespace: str
    class_uri: str = SKOS_CONCEPT
    attributes: Mapping[str, Attribute] = field(default_factory=dict)
    retired: bool = False


@dataclass(frozen=True)
class TermSchema:
    version: str
    prefixes: Mapping[str, str]
    columns: Mapping[str, Column]
    types: Mapping[str, TermType]


@dataclass(frozen=True)
class Predicate:
    curie: str
    uri: str
    subject: tuple[str, ...]
    object: tuple[str, ...]
    external: tuple[str, ...] = ()
    max_one_per_subject: bool = False


@dataclass(frozen=True)
class RelationSchema:
    version: str
    prefixes: Mapping[str, str]
    columns: Mapping[str, Column]
    predicates: Mapping[str, Predicate]


def _columns(raw: dict, prefixes: Mapping[str, str]) -> Mapping[str, Column]:
    columns = {}
    for name, spec in raw.items():
        col_type = spec.get("type", "string")
        if col_type not in COLUMN_TYPES:
            raise ValueError(f"column {name!r}: unknown type {col_type!r}")
        enum = spec.get("enum")
        columns[name] = Column(
            name=name,
            type=col_type,
            required=bool(spec.get("required", False)),
            unique=bool(spec.get("unique", False)),
            enum=enum if isinstance(enum, str) else (tuple(enum) if enum else None),
            predicate=expand_curie(prefixes, spec["predicate"]) if "predicate" in spec else None,
            lang=spec.get("lang"),
        )
    return _frozen(columns)


def _attributes(
    raw: dict | None, prefixes: Mapping[str, str], type_name: str
) -> Mapping[str, Attribute]:
    attributes = {}
    for name, spec in (raw or {}).items():
        attr_type = spec.get("type", "string")
        if attr_type not in ATTRIBUTE_TYPES:
            raise ValueError(f"type {type_name!r} attribute {name!r}: unknown type {attr_type!r}")
        attributes[name] = Attribute(
            name=name,
            predicate=expand_curie(prefixes, spec["predicate"]),
            type=attr_type,
            lang=spec.get("lang"),
            enum=tuple(spec["enum"]) if "enum" in spec else None,
        )
    return _frozen(attributes)


@lru_cache(maxsize=None)
def load_term_schema(path: Path | str) -> TermSchema:
    """Parse ``term.yaml``. Cached per path."""
    raw = yaml.safe_load(Path(path).read_text())
    prefixes = _frozen(raw.get("prefixes", {}))
    term_types = {}
    for name, spec in raw["types"].items():
        term_types[name] = TermType(
            name=name,
            category=spec["category"],
            namespace=spec["namespace"],
            class_uri=expand_curie(prefixes, spec["class"]) if "class" in spec else SKOS_CONCEPT,
            attributes=_attributes(spec.get("attributes"), prefixes, name),
            retired=bool(spec.get("retired", False)),
        )
    return TermSchema(
        version=str(raw["version"]),
        prefixes=prefixes,
        columns=_columns(raw["columns"], prefixes),
        types=_frozen(term_types),
    )


@lru_cache(maxsize=None)
def load_relation_schema(path: Path | str) -> RelationSchema:
    """Parse ``relation.yaml``. Cached per path."""
    raw = yaml.safe_load(Path(path).read_text())
    prefixes = _frozen(raw.get("prefixes", {}))
    predicates = {}
    for curie, spec in raw["predicates"].items():
        predicates[curie] = Predicate(
            curie=curie,
            uri=expand_curie(prefixes, curie),
            subject=_tuple(spec["subject"]),
            object=_tuple(spec["object"]),
            external=_tuple(spec.get("external")),
            max_one_per_subject=bool(spec.get("max_one_per_subject", False)),
        )
    return RelationSchema(
        version=str(raw["version"]),
        prefixes=prefixes,
        columns=_columns(raw["columns"], prefixes),
        predicates=_frozen(predicates),
    )
