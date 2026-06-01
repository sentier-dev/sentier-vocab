from __future__ import annotations

from enum import Enum
from typing import Any, ClassVar, Optional

from pydantic import BaseModel, ConfigDict, Field, RootModel

metamodel_version = "1.11.0"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias=True,
        validate_by_name=True,
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        strict=False,
    )


class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key: str):
        return getattr(self.root, key)

    def __getitem__(self, key: str):
        return self.root[key]

    def __setitem__(self, key: str, value):
        self.root[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta(
    {
        "default_prefix": "sentier",
        "default_range": "string",
        "description": "Schema for native model-term vocabulary entries.",
        "id": "https://vocab.sentier.dev/schemas/model-term",
        "imports": ["linkml:types", "common"],
        "license": "MIT",
        "name": "sentier_model_term",
        "prefixes": {
            "dcterms": {
                "prefix_prefix": "dcterms",
                "prefix_reference": "http://purl.org/dc/terms/",
            },
            "linkml": {"prefix_prefix": "linkml", "prefix_reference": "https://w3id.org/linkml/"},
            "ont": {
                "prefix_prefix": "ont",
                "prefix_reference": "https://vocab.sentier.dev/ontology/",
            },
            "qudt": {"prefix_prefix": "qudt", "prefix_reference": "http://qudt.org/schema/qudt/"},
            "sentier": {
                "prefix_prefix": "sentier",
                "prefix_reference": "https://vocab.sentier.dev/",
            },
            "skos": {
                "prefix_prefix": "skos",
                "prefix_reference": "http://www.w3.org/2004/02/skos/core#",
            },
            "xsd": {
                "prefix_prefix": "xsd",
                "prefix_reference": "http://www.w3.org/2001/XMLSchema#",
            },
        },
        "source_file": "schemas/model-term.yaml",
        "title": "Sentier.dev model terms",
    }
)


class StatusEnum(str, Enum):
    draft = "draft"
    """
    Proposed, not yet published.
    """
    published = "published"
    """
    Published in the live vocabulary.
    """
    deprecated = "deprecated"
    """
    Retained for stability but no longer recommended.
    """


class Concept(ConfiguredBaseModel):
    """
    Base SKOS concept. Every Sentier.dev term is_a Concept.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "abstract": True,
            "class_uri": "skos:Concept",
            "from_schema": "https://vocab.sentier.dev/schemas/common",
        }
    )

    iri: str = Field(
        default=...,
        description="""Globally unique IRI identifying this concept.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Concept"]}},
    )
    pref_label: str = Field(
        default=...,
        description="""Preferred human-readable label (English).""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"lang_tagged": {"tag": "lang_tagged", "value": True}},
                "domain_of": ["Concept"],
                "slot_uri": "skos:prefLabel",
            }
        },
    )
    alt_labels: Optional[list[str]] = Field(
        default=None,
        description="""Alternative labels / synonyms.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"lang_tagged": {"tag": "lang_tagged", "value": True}},
                "domain_of": ["Concept"],
                "slot_uri": "skos:altLabel",
            }
        },
    )
    definition: Optional[str] = Field(
        default=None,
        description="""SKOS definition.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"lang_tagged": {"tag": "lang_tagged", "value": True}},
                "domain_of": ["Concept"],
                "slot_uri": "skos:definition",
            }
        },
    )
    notation: Optional[str] = Field(
        default=None,
        description="""SKOS notation / code.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:notation"}},
    )
    broader: Optional[str] = Field(
        default=None,
        description="""IRI of the broader (parent) concept.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:broader"}},
    )
    exact_match: Optional[list[str]] = Field(
        default=None,
        description="""Crosswalk: exactly equivalent concept in another vocabulary.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:exactMatch"}
        },
    )
    close_match: Optional[list[str]] = Field(
        default=None,
        description="""Crosswalk: closely related concept in another vocabulary.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:closeMatch"}
        },
    )
    related: Optional[list[str]] = Field(
        default=None,
        description="""Associative (non-hierarchical) related concept.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:related"}},
    )
    status: Optional[StatusEnum] = Field(
        default=None,
        description="""Curation status of this term.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"internal": {"tag": "internal", "value": True}},
                "domain_of": ["Concept"],
            }
        },
    )


class ModelTerm(Concept):
    """
    A named parameter or variable used in a computational model, optionally linked to a QUDT quantity kind and unit.

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "class_uri": "skos:Concept",
            "from_schema": "https://vocab.sentier.dev/schemas/model-term",
        }
    )

    quantity_kind: Optional[str] = Field(
        default=None,
        description="""The QUDT quantity kind associated with this model term.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["ModelTerm"], "slot_uri": "qudt:hasQuantityKind"}
        },
    )
    unit: Optional[str] = Field(
        default=None,
        description="""The QUDT unit associated with this model term.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["ModelTerm"], "slot_uri": "qudt:hasUnit"}
        },
    )
    iri: str = Field(
        default=...,
        description="""Globally unique IRI identifying this concept.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Concept"]}},
    )
    pref_label: str = Field(
        default=...,
        description="""Preferred human-readable label (English).""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"lang_tagged": {"tag": "lang_tagged", "value": True}},
                "domain_of": ["Concept"],
                "slot_uri": "skos:prefLabel",
            }
        },
    )
    alt_labels: Optional[list[str]] = Field(
        default=None,
        description="""Alternative labels / synonyms.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"lang_tagged": {"tag": "lang_tagged", "value": True}},
                "domain_of": ["Concept"],
                "slot_uri": "skos:altLabel",
            }
        },
    )
    definition: Optional[str] = Field(
        default=None,
        description="""SKOS definition.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"lang_tagged": {"tag": "lang_tagged", "value": True}},
                "domain_of": ["Concept"],
                "slot_uri": "skos:definition",
            }
        },
    )
    notation: Optional[str] = Field(
        default=None,
        description="""SKOS notation / code.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:notation"}},
    )
    broader: Optional[str] = Field(
        default=None,
        description="""IRI of the broader (parent) concept.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:broader"}},
    )
    exact_match: Optional[list[str]] = Field(
        default=None,
        description="""Crosswalk: exactly equivalent concept in another vocabulary.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:exactMatch"}
        },
    )
    close_match: Optional[list[str]] = Field(
        default=None,
        description="""Crosswalk: closely related concept in another vocabulary.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:closeMatch"}
        },
    )
    related: Optional[list[str]] = Field(
        default=None,
        description="""Associative (non-hierarchical) related concept.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:related"}},
    )
    status: Optional[StatusEnum] = Field(
        default=None,
        description="""Curation status of this term.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"internal": {"tag": "internal", "value": True}},
                "domain_of": ["Concept"],
            }
        },
    )


class ModelTermCollection(ConfiguredBaseModel):
    """
    A scheme/group file holding many model terms.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "annotations": {"layer": {"tag": "layer", "value": "vocabulary"}},
            "from_schema": "https://vocab.sentier.dev/schemas/model-term",
            "tree_root": True,
        }
    )

    scheme: str = Field(
        default=...,
        description="""The ConceptScheme IRI these model terms belong to.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"internal": {"tag": "internal", "value": True}},
                "domain_of": ["ModelTermCollection"],
            }
        },
    )
    model_terms: Optional[list[ModelTerm]] = Field(
        default=None,
        description="""The model terms in this collection.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ModelTermCollection"]}},
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Concept.model_rebuild()
ModelTerm.model_rebuild()
ModelTermCollection.model_rebuild()
