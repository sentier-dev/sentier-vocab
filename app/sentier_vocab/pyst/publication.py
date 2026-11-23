"""Turn the ``terms/`` and ``relations/`` layers into the documents PyST accepts.

PyST (the server behind vocab.sentier.dev) takes expanded JSON-LD and is
stricter than the TTL this repo generates: every concept needs a status and a
concept scheme that exists, a scheme needs a label, definition, version and
creation date, ``skos:broader`` may not leave its scheme, and a scheme page
lists its top concepts, all on one page. ``schemas/pyst.yaml`` says which terms go to which
scheme; this module builds the plan and nothing here talks to a server.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from urllib.parse import quote

import yaml

from sentier_vocab import paths
from sentier_vocab.layers import release_of
from sentier_vocab.schema import (
    SKOS_CONCEPT,
    Attribute,
    RelationSchema,
    TermSchema,
    load_relation_schema,
    load_term_schema,
)

SKOS = "http://www.w3.org/2004/02/skos/core#"
DCTERMS = "http://purl.org/dc/terms/"
XSD = "http://www.w3.org/2001/XMLSchema#"
BIBO_STATUS = "http://purl.org/ontology/bibo/status/"
STATUS = "http://purl.org/ontology/bibo/status"
VERSION = "http://www.w3.org/2002/07/owl#versionInfo"
PLAIN_LITERAL = "http://www.w3.org/1999/02/22-rdf-syntax-ns#PlainLiteral"
BROADER = SKOS + "broader"
BROAD_MATCH = SKOS + "broadMatch"
#: Predicates PyST stores in its relationship table; every other one is a property.
RELATIONSHIP_VERBS = frozenset(
    SKOS + name
    for name in (
        "broader",
        "narrower",
        "exactMatch",
        "closeMatch",
        "broadMatch",
        "narrowMatch",
        "relatedMatch",
    )
)
PYST_STATUSES = frozenset({"accepted", "draft", "rejected"})
LANGUAGE = "en"
DEFAULT_TOP_CONCEPT_LIMIT = 500


class PlanError(ValueError):
    """The layers and ``pyst.yaml`` do not add up to something PyST would accept."""


@dataclass(frozen=True)
class Scheme:
    iri: str
    existing: bool
    document: dict | None  # None for a scheme that is already on the server
    concepts: tuple[dict, ...]


@dataclass(frozen=True)
class Plan:
    schemes: tuple[Scheme, ...]
    relationships: tuple[dict, ...]
    skipped_terms: int
    dropped_relations: int

    def subject_scheme(self) -> dict[str, str]:
        """``{concept IRI: scheme IRI}`` for every concept of the plan."""
        return {doc["@id"]: scheme.iri for scheme in self.schemes for doc in scheme.concepts}


def api_path(kind: str, iri: str | None = None) -> str:
    """``/api/v1/<kind>/[<quoted iri>]``, the way PyST builds its own paths."""
    return f"/api/v1/{kind}/" + (quote(iri) if iri else "")


def load_config(path: Path | str = paths.PYST_CONFIG) -> dict:
    return yaml.safe_load(Path(path).read_text())


def relationship_pair(document: dict) -> tuple[str, str]:
    """``(source, target)`` of a relationship document."""
    return document["@id"], next(v for k, v in document.items() if k != "@id")[0]["@id"]


def _text(value: str) -> dict:
    return {"@value": str(value), "@language": LANGUAGE}


def _node(iri: str) -> dict:
    return {"@id": iri}


def _attribute_value(value, spec: Attribute) -> dict:
    if spec.type == "uri":
        return _node(str(value))
    if spec.type == "date":
        return {"@value": str(value), "@type": XSD + "date"}
    if spec.type == "double":
        return {"@value": float(value)}
    if spec.lang:
        return {"@value": str(value), "@language": spec.lang}
    return {"@value": str(value)}


def scheme_document(entry: dict) -> dict:
    """The concept scheme PyST is asked to create for one ``schemes`` entry."""
    status = entry.get("status", "draft")
    if status not in PYST_STATUSES:
        raise PlanError(f"scheme {entry['iri']}: status {status!r} is not a PyST status")
    return {
        "@id": entry["iri"],
        "@type": [SKOS + "ConceptScheme"],
        SKOS + "prefLabel": [_text(entry["label"])],
        SKOS + "definition": [_text(entry["definition"])],
        STATUS: [_node(BIBO_STATUS + status)],
        DCTERMS + "created": [{"@type": XSD + "date", "@value": str(entry["created"])}],
        DCTERMS + "creator": [_node(entry["creator"])],
        VERSION: [{"@value": str(entry["version"])}],
    }


def concept_document(
    row: dict,
    scheme_iri: str,
    top: bool,
    links: Mapping[str, list[str]],
    statuses: Mapping[str, str],
    schema: TermSchema,
) -> dict:
    """One term row as a PyST concept. ``links`` are its relations kept as properties."""
    term_type = schema.types[row["type"]]
    types = [SKOS_CONCEPT]
    if term_type.class_uri != SKOS_CONCEPT:
        types.append(term_type.class_uri)
    status = statuses.get(row.get("status", "draft"))
    if status not in PYST_STATUSES:
        raise PlanError(f"{row['iri']}: status {row.get('status')!r} has no PyST status")
    doc = {
        "@id": row["iri"],
        "@type": types,
        SKOS + "prefLabel": [_text(row["pref_label"])],
        STATUS: [_node(BIBO_STATUS + status)],
        SKOS + "inScheme": [_node(scheme_iri)],
        DCTERMS + "source": [_node(row["source"])],
    }
    if top:
        doc[SKOS + "topConceptOf"] = [_node(scheme_iri)]
    if row.get("alt_labels"):
        doc[SKOS + "altLabel"] = [_text(label) for label in row["alt_labels"]]
    if row.get("definition"):
        doc[SKOS + "definition"] = [_text(row["definition"])]
    notations = ([row["notation"]] if row.get("notation") else []) + list(
        row.get("additional_notations") or []
    )
    if notations:
        doc[SKOS + "notation"] = [{"@value": n, "@type": PLAIN_LITERAL} for n in notations]
    for name, value in (row.get("attributes") or {}).items():
        spec = term_type.attributes[name]
        values = value if isinstance(value, list) else [value]
        doc.setdefault(spec.predicate, []).extend(_attribute_value(v, spec) for v in values)
    for predicate, objects in links.items():
        doc.setdefault(predicate, []).extend(_node(obj) for obj in objects)
    return doc


def _assign(terms: Mapping[Path, list[dict]], config: dict) -> tuple[dict, int]:
    """``{scheme index: rows}`` and the number of skipped rows; every row is covered once."""
    target: dict[tuple[str, str], int | None] = {}
    problems = []
    selections = [(i, s) for i, entry in enumerate(config["schemes"]) for s in entry["select"]]
    selections += [(None, s) for s in config.get("skip") or []]
    for index, selection in selections:
        for type_ in selection["types"]:
            key = (selection["release"], type_)
            if key in target:
                problems.append(f"{key[0]} / {key[1]} is selected twice in pyst.yaml")
            target[key] = index
    assigned: dict[int, list[dict]] = defaultdict(list)
    skipped = 0
    missing = set()
    for path, rows in terms.items():
        release = release_of(path)
        for row in rows:
            key = (release, row["type"])
            if key not in target:
                missing.add(key)
            elif target[key] is None:
                skipped += 1
            else:
                assigned[target[key]].append(row)
    problems += [
        f"{release} / {type_} is in terms/ but no scheme or skip entry of pyst.yaml covers it"
        for release, type_ in sorted(missing)
    ]
    if problems:
        raise PlanError("\n".join(problems))
    return assigned, skipped


def build_plan(
    terms: Mapping[Path, list[dict]],
    relations: Mapping[Path, list[dict]],
    config: dict,
    schema: TermSchema | None = None,
    rel_schema: RelationSchema | None = None,
) -> Plan:
    """Everything a push sends, in the order it sends it. Raises ``PlanError``."""
    schema = schema or load_term_schema(paths.TERM_SCHEMA)
    rel_schema = rel_schema or load_relation_schema(paths.RELATION_SCHEMA)
    assigned, skipped = _assign(terms, config)
    scheme_of = {
        row["iri"]: config["schemes"][index]["iri"]
        for index, rows in assigned.items()
        for row in rows
    }

    relationships: dict[tuple[str, str], dict] = {}
    links: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    has_broader = set()
    dropped = 0
    problems = []
    for rows in relations.values():
        for row in rows:
            subject, obj = row["subject"], row["object"]
            predicate = rel_schema.predicates[row["predicate"]].uri
            if subject not in scheme_of:
                dropped += 1
                continue
            if predicate not in RELATIONSHIP_VERBS:
                links[subject][predicate].append(obj)
                continue
            if predicate == BROADER:
                if obj not in scheme_of:
                    problems.append(f"{subject}: broader term {obj} is not published")
                    continue
                if scheme_of[obj] == scheme_of[subject]:
                    has_broader.add(subject)
                else:
                    predicate = BROAD_MATCH
            if (subject, obj) in relationships:
                problems.append(f"{subject} -> {obj}: PyST holds one relationship per pair")
                continue
            relationships[(subject, obj)] = {"@id": subject, predicate: [_node(obj)]}
    if problems:
        raise PlanError("\n".join(problems[:50]))

    statuses = config["status"]
    top_limit = int(config.get("top_concept_limit", DEFAULT_TOP_CONCEPT_LIMIT))
    schemes = []
    for index, entry in enumerate(config["schemes"]):
        existing = bool(entry.get("existing"))
        rows = assigned.get(index, [])
        roots = {row["iri"] for row in rows if row["iri"] not in has_broader}
        # PyST prints every top concept on the scheme's page: a large flat list is
        # left without any, as the flat schemes already on the server are.
        list_roots = not existing and len(roots) <= top_limit
        concepts = tuple(
            concept_document(
                row,
                entry["iri"],
                top=list_roots and row["iri"] in roots,
                links=links.get(row["iri"], {}),
                statuses=statuses,
                schema=schema,
            )
            for row in sorted(rows, key=lambda r: r["iri"])
        )
        schemes.append(
            Scheme(
                iri=entry["iri"],
                existing=existing,
                document=None if existing else scheme_document(entry),
                concepts=concepts,
            )
        )
    return Plan(
        schemes=tuple(schemes),
        relationships=tuple(relationships[key] for key in sorted(relationships)),
        skipped_terms=skipped,
        dropped_relations=dropped,
    )


def check_against_pyst(plan: Plan) -> list[str]:
    """Run every document through PyST's own request models. Needs the ``pyst`` extra."""
    from py_semantic_taxonomy.adapters.routers import request_dto as req

    errors = []

    def check(model, document: dict) -> None:
        try:
            model(**document)
        except ValueError as err:
            errors.append(f"{document['@id']}: {str(err).splitlines()[0:3]}")

    for scheme in plan.schemes:
        if scheme.document:
            check(req.ConceptScheme, scheme.document)
        for document in scheme.concepts:
            check(req.ConceptCreate, document)
    for document in plan.relationships:
        check(req.Relationship, document)
    return errors
