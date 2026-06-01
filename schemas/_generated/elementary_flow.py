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
        "description": "Schema for native elementary-flow terms.",
        "id": "https://vocab.sentier.dev/schemas/elementary-flow",
        "imports": ["linkml:types", "common"],
        "license": "MIT",
        "name": "sentier_elementary_flow",
        "prefixes": {
            "linkml": {"prefix_prefix": "linkml", "prefix_reference": "https://w3id.org/linkml/"},
            "sentier": {
                "prefix_prefix": "sentier",
                "prefix_reference": "https://vocab.sentier.dev/",
            },
            "skos": {
                "prefix_prefix": "skos",
                "prefix_reference": "http://www.w3.org/2004/02/skos/core#",
            },
        },
        "source_file": "schemas/elementary-flow.yaml",
        "title": "Sentier.dev elementary (biosphere) flows",
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
            "linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:prefLabel"}
        },
    )
    alt_labels: Optional[list[str]] = Field(
        default=None,
        description="""Alternative labels / synonyms.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:altLabel"}},
    )
    definition: Optional[str] = Field(
        default=None,
        description="""SKOS definition.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:definition"}
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
        json_schema_extra={"linkml_meta": {"domain_of": ["Concept"]}},
    )


class ElementaryFlow(Concept):
    """
    Material or energy entering the system from, or released to, the environment without human transformation.

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "class_uri": "skos:Concept",
            "from_schema": "https://vocab.sentier.dev/schemas/elementary-flow",
        }
    )

    compartment: Optional[str] = Field(
        default=None,
        description="""Environmental compartment (e.g. air, water, soil).""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ElementaryFlow"]}},
    )
    sub_compartment: Optional[str] = Field(
        default=None,
        description="""Sub-compartment refinement (e.g. \"low population density\").""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ElementaryFlow"]}},
    )
    cas_number: Optional[str] = Field(
        default=None,
        description="""CAS registry number, if applicable.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ElementaryFlow"]}},
    )
    formula: Optional[str] = Field(
        default=None,
        description="""Chemical formula, if applicable.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ElementaryFlow"]}},
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
            "linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:prefLabel"}
        },
    )
    alt_labels: Optional[list[str]] = Field(
        default=None,
        description="""Alternative labels / synonyms.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:altLabel"}},
    )
    definition: Optional[str] = Field(
        default=None,
        description="""SKOS definition.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Concept"], "slot_uri": "skos:definition"}
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
        json_schema_extra={"linkml_meta": {"domain_of": ["Concept"]}},
    )


class ElementaryFlowCollection(ConfiguredBaseModel):
    """
    A scheme/group file holding many elementary flows (one file per group).
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://vocab.sentier.dev/schemas/elementary-flow", "tree_root": True}
    )

    scheme: str = Field(
        default=...,
        description="""The ConceptScheme IRI these flows belong to.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ElementaryFlowCollection"]}},
    )
    flows: Optional[list[ElementaryFlow]] = Field(
        default=None,
        description="""The elementary flows in this group.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ElementaryFlowCollection"]}},
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Concept.model_rebuild()
ElementaryFlow.model_rebuild()
ElementaryFlowCollection.model_rebuild()
