from __future__ import annotations

from datetime import date
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
        "description": "Schema for native LCIA-method terms.",
        "id": "https://vocab.sentier.dev/schemas/lcia-method",
        "imports": ["linkml:types", "common"],
        "license": "MIT",
        "name": "sentier_lcia_method",
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
        "source_file": "schemas/lcia-method.yaml",
        "title": "Sentier.dev LCIA methods",
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


class LCIAMethod(Concept):
    """
    A life cycle impact assessment method providing characterization factors for one or more impact categories.

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "class_uri": "skos:Concept",
            "from_schema": "https://vocab.sentier.dev/schemas/lcia-method",
        }
    )

    methodology: Optional[str] = Field(
        default=None,
        description="""The overarching methodology or framework of this LCIA method.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"lang_tagged": {"tag": "lang_tagged", "value": True}},
                "domain_of": ["LCIAMethod"],
                "slot_uri": "ont:methodology",
            }
        },
    )
    impact_categories: Optional[list[str]] = Field(
        default=None,
        description="""Impact categories covered by this LCIA method.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["LCIAMethod"], "slot_uri": "ont:impactCategory"}
        },
    )
    source: Optional[str] = Field(
        default=None,
        description="""Source reference for this LCIA method.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["LCIAMethod"], "slot_uri": "dcterms:source"}
        },
    )
    valid_from: Optional[date] = Field(
        default=None,
        description="""Date from which this LCIA method is valid.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["LCIAMethod"], "slot_uri": "ont:validFrom"}
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


class LCIAMethodCollection(ConfiguredBaseModel):
    """
    A scheme/group file holding many LCIA methods.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "annotations": {"layer": {"tag": "layer", "value": "vocabulary"}},
            "from_schema": "https://vocab.sentier.dev/schemas/lcia-method",
            "tree_root": True,
        }
    )

    scheme: str = Field(
        default=...,
        description="""The ConceptScheme IRI these LCIA methods belong to.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"internal": {"tag": "internal", "value": True}},
                "domain_of": ["LCIAMethodCollection"],
            }
        },
    )
    lcia_methods: Optional[list[LCIAMethod]] = Field(
        default=None,
        description="""The LCIA methods in this collection.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["LCIAMethodCollection"]}},
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Concept.model_rebuild()
LCIAMethod.model_rebuild()
LCIAMethodCollection.model_rebuild()
