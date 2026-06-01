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
        "description": "Schema for life cycle inventory processes with nested " "exchanges.",
        "id": "https://vocab.sentier.dev/schemas/process",
        "imports": ["linkml:types", "common"],
        "license": "MIT",
        "name": "sentier_process",
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
        "source_file": "schemas/process.yaml",
        "title": "Sentier.dev processes",
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


class FlowDirectionEnum(str, Enum):
    input = "input"
    """
    A flow entering the process.
    """
    output = "output"
    """
    A flow leaving the process.
    """


class ProcessTypeEnum(str, Enum):
    unit = "unit"
    """
    A unit process with explicit inputs and outputs.
    """
    system = "system"
    """
    A system process aggregating multiple unit processes.
    """
    lci_result = "lci_result"
    """
    A cradle-to-gate LCI result.
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


class Exchange(ConfiguredBaseModel):
    """
    A quantified flow exchange within a process.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"class_uri": "ont:Exchange", "from_schema": "https://vocab.sentier.dev/schemas/process"}
    )

    flow: Optional[str] = Field(
        default=None,
        json_schema_extra={"linkml_meta": {"domain_of": ["Exchange"], "slot_uri": "ont:flow"}},
    )
    direction: Optional[FlowDirectionEnum] = Field(
        default=None,
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Exchange"], "slot_uri": "ont:direction"}
        },
    )
    amount: Optional[float] = Field(
        default=None,
        json_schema_extra={"linkml_meta": {"domain_of": ["Exchange"], "slot_uri": "ont:amount"}},
    )
    unit: Optional[str] = Field(
        default=None,
        json_schema_extra={"linkml_meta": {"domain_of": ["Exchange"], "slot_uri": "qudt:hasUnit"}},
    )


class Process(Concept):
    """
    A unit process or system process representing a set of activities with quantified inputs and outputs.

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"class_uri": "ont:Process", "from_schema": "https://vocab.sentier.dev/schemas/process"}
    )

    geography: Optional[str] = Field(
        default=None,
        description="""The geographic scope of this process.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Process"], "slot_uri": "ont:geography"}},
    )
    valid_from: Optional[date] = Field(
        default=None,
        description="""The date from which this process record is valid.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Process"], "slot_uri": "ont:validFrom"}},
    )
    technology: Optional[str] = Field(
        default=None,
        description="""Technology description for this process.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"lang_tagged": {"tag": "lang_tagged", "value": True}},
                "domain_of": ["Process"],
                "slot_uri": "ont:technology",
            }
        },
    )
    process_type: Optional[ProcessTypeEnum] = Field(
        default=None,
        description="""Type of process (unit, system, or LCI result).""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["Process"], "slot_uri": "ont:processType"}
        },
    )
    exchanges: Optional[list[Exchange]] = Field(
        default=None,
        description="""The quantified input and output flows of this process.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "iri_key": {"tag": "iri_key", "value": "flow"},
                    "iri_suffix": {"tag": "iri_suffix", "value": "direction"},
                },
                "domain_of": ["Process"],
                "slot_uri": "ont:hasExchange",
            }
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


class ProcessCollection(ConfiguredBaseModel):
    """
    A collection file holding process records.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "annotations": {"layer": {"tag": "layer", "value": "data"}},
            "from_schema": "https://vocab.sentier.dev/schemas/process",
            "tree_root": True,
        }
    )

    scheme: str = Field(
        default=...,
        description="""The namespace IRI for this collection of processes.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"internal": {"tag": "internal", "value": True}},
                "domain_of": ["ProcessCollection"],
            }
        },
    )
    processes: Optional[list[Process]] = Field(
        default=None,
        description="""The processes in this collection.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["ProcessCollection"]}},
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Concept.model_rebuild()
Exchange.model_rebuild()
Process.model_rebuild()
ProcessCollection.model_rebuild()
