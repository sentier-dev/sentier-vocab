"""One-shot migration of data/<type>/* into terms/<release>.parquet + relations/<release>.parquet.

Run once from the repo root, then delete this file:

    uv run python scripts/migrate_layout.py [--brightway-out DIR]

Rules (spec 2026-10-21, approved 2026-11-05):
- every row's ``source`` is the delivering release; rows of a ``core.yaml`` file
  and rows without a source are sentier-core;
- IRI-valued slots become relation rows; literal slots become ``attributes``;
- ``exact_match``/``close_match`` to vocab.brightway.* are exported as a randonneur
  package for sentier-mappings (``--brightway-out``) and dropped from vocab;
- ``exchanges`` and the characterization-factors type are dropped.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import pyarrow.parquet as pq
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from sentier_vocab import paths  # noqa: E402
from sentier_vocab.iris import identifier_from  # noqa: E402
from sentier_vocab.layers import write_relations, write_terms  # noqa: E402

CORE_SOURCE = "https://vocab.sentier.dev/sources/sentier-core"
BRIGHTWAY = ("https://vocab.brightway.one/", "https://vocab.brightway.dev/")
COMMON = (
    "iri",
    "pref_label",
    "alt_labels",
    "definition",
    "notation",
    "additional_notations",
    "source",
    "status",
)

# data folder -> (type, items key, {old slot: ('attr', name) | ('rel', predicate)
#                                   | ('drop', None)})
TYPES = {
    "elementary-flows": (
        "elementary-flow",
        "flows",
        {
            "compartment": ("attr", "compartment"),
            "sub_compartment": ("attr", "sub_compartment"),
            "cas_number": ("attr", "cas_number"),
            "formula": ("attr", "formula"),
        },
    ),
    "flow-properties": (
        "flow-property",
        "flow_properties",
        {
            "default_unit_group": ("rel", "ont:defaultUnitGroup"),
            "default_unit": ("rel", "qudt:hasUnit"),
            "data_type": ("attr", "data_type"),
        },
    ),
    "unit-groups": (
        "unit-group",
        "unit_groups",
        {
            "reference_unit": ("rel", "qudt:hasUnit"),
            "units": ("rel", "ont:hasUnit"),
            "quantity_kind": ("rel", "qudt:hasQuantityKind"),
        },
    ),
    "products": (
        "product",
        "products",
        {
            "cpc_code": ("attr", "cpc_code"),
            "reference_flow_property": ("rel", "ont:referenceFlowProperty"),
        },
    ),
    "impact-categories": (
        "impact-category",
        "impact_categories",
        {
            "indicator": ("attr", "indicator"),
            "reference_unit": ("rel", "qudt:hasUnit"),
            "time_horizon": ("attr", "time_horizon"),
            "method": ("rel", "ont:method"),
            "normalization_factor": ("attr", "normalization_factor"),
            "weighting_factor": ("attr", "weighting_factor"),
        },
    ),
    "lcia-methods": (
        "lcia-method",
        "lcia_methods",
        {
            "methodology": ("attr", "methodology"),
            "impact_categories": ("rel", "ont:impactCategory"),
            "valid_from": ("attr", "valid_from"),
        },
    ),
    "sources": (
        "source",
        "sources",
        {
            "title": ("attr", "title"),
            "creators": ("attr", "creators"),
            "date": ("attr", "date"),
            "publisher": ("attr", "publisher"),
            "identifier": ("attr", "identifier"),
            "citation": ("attr", "citation"),
        },
    ),
    "contacts": (
        "contact",
        "contacts",
        {
            "email": ("attr", "email"),
            "organisation": ("attr", "organisation"),
            "url": ("attr", "url"),
        },
    ),
    "model-terms": (
        "model-term",
        "model_terms",
        {"quantity_kind": ("rel", "qudt:hasQuantityKind"), "unit": ("rel", "qudt:hasUnit")},
    ),
    "processes": (
        "process",
        "processes",
        {
            "geography": ("rel", "ont:geography"),
            "valid_from": ("attr", "valid_from"),
            "technology": ("attr", "technology"),
            "process_type": ("attr", "process_type"),
            "exchanges": ("drop", None),
        },
    ),
    "organisms": ("organism", "organisms", {}),
    "qualifiers": ("qualifier", "qualifiers", {}),
}
COMMON_RELATIONS = {
    "broader": "skos:broader",
    "related": "skos:related",
    "exact_match": "skos:exactMatch",
    "close_match": "skos:closeMatch",
}


def _records(path: Path, items_key: str) -> list[dict]:
    if path.suffix == ".yaml":
        return yaml.safe_load(path.read_text()).get(items_key) or []
    return pq.read_table(path).to_pylist()


def _present(value) -> bool:
    if value is None or value == []:
        return False
    if isinstance(value, float) and value != value:  # NaN from pandas-written parquet
        return False
    return True


def _as_list(value) -> list:
    return list(value) if isinstance(value, (list, tuple)) else [value]


def migrate(brightway_out: Path | None) -> None:
    terms = defaultdict(list)
    relations = defaultdict(list)
    brightway = []
    for folder, (type_name, items_key, slots) in TYPES.items():
        for path in sorted((paths.DATA_DIR / folder).glob("*")):
            if path.suffix not in (".yaml", ".parquet"):
                continue
            for raw in _records(path, items_key):
                rec = {k: v for k, v in raw.items() if _present(v)}
                if path.stem == "core":
                    source = CORE_SOURCE
                elif type_name == "source":
                    source = rec["iri"]  # a source term is delivered by its own release
                else:
                    source = rec.get("source") or CORE_SOURCE
                release = identifier_from(source)
                status = rec.get("status", "draft")
                term = {k: rec[k] for k in COMMON if k in rec}
                term.update({"type": type_name, "source": source, "status": status})
                attrs = {}
                for slot, value in rec.items():
                    if slot in COMMON:
                        continue
                    if slot in COMMON_RELATIONS:
                        for obj in _as_list(value):
                            if slot in ("exact_match", "close_match") and obj.startswith(
                                BRIGHTWAY
                            ):
                                brightway.append(
                                    {"source": {"iri": rec["iri"]}, "target": {"iri": obj}}
                                )
                            else:
                                relations[release].append(
                                    {
                                        "subject": rec["iri"],
                                        "predicate": COMMON_RELATIONS[slot],
                                        "object": obj,
                                        "source": source,
                                        "status": status,
                                    }
                                )
                        continue
                    kind, name = slots[slot]
                    if kind == "drop":
                        continue
                    if kind == "attr":
                        attrs[name] = value
                    else:
                        for obj in _as_list(value):
                            relations[release].append(
                                {
                                    "subject": rec["iri"],
                                    "predicate": name,
                                    "object": obj,
                                    "source": source,
                                    "status": status,
                                }
                            )
                if attrs:
                    term["attributes"] = attrs
                terms[release].append(term)
    terms["sentier-core"].append(
        {
            "iri": CORE_SOURCE,
            "type": "source",
            "pref_label": "Sentier.dev curated terms",
            "definition": (
                "Terms curated by Sentier.dev itself, not imported from a published source."
            ),
            "source": CORE_SOURCE,
            "status": "published",
        }
    )
    for release, rows in sorted(terms.items()):
        files = write_terms(rows, paths.TERMS_DIR, release)
        print(release, "terms", len(rows), [p.name for p in files])
    for release, rows in sorted(relations.items()):
        files = write_relations(rows, paths.RELATIONS_DIR, release)
        print(release, "relations", len(rows), [p.name for p in files])
    if brightway_out:
        brightway_out.mkdir(parents=True, exist_ok=True)
        (brightway_out / "biosphere.json").write_text(
            json.dumps(
                {"name": "ef-3.1__brightway-biosphere", "version": "0.1.0", "replace": brightway},
                indent=1,
            )
        )
        (brightway_out / "metadata.json").write_text(
            json.dumps(
                {
                    "source": "ef-3.1",
                    "target": "brightway",
                    "title": "EF 3.1 flow IRIs -> Brightway flow IRIs (exact matches)",
                    "target_proprietary": False,
                    "schema_version": "0.2.0",
                    "packages": [
                        {
                            "file": "biosphere.json",
                            "kind": "biosphere",
                            "order": 1,
                            "entries": len(brightway),
                            "generated_by": "sentier-vocab scripts/migrate_layout.py",
                        }
                    ],
                },
                indent=2,
            )
        )
        print("brightway entries", len(brightway), "->", brightway_out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--brightway-out", type=Path, default=None)
    migrate(ap.parse_args().brightway_out)
