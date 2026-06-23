"""Load (and write) native data source files in a format-agnostic way.

A category's source data may be authored as YAML (small, hand-curated) or delivered
as Parquet (large, machine-imported — e.g. FoodEx2). Both reduce to the same shape:
a ``scheme`` IRI plus a list of concept records. The rest of the pipeline
(``generate``, validation, ``build_graph``) consumes records and never cares which
format produced them.

The Parquet contract (see docs spec 2026-06-17-foodex2-parquet-delivery):
- columns are the concept's snake_case slots; scalars are ``string``, ``multivalued``
  slots are ``list<string>``;
- ``scheme`` is NOT a column — it lives in the file's Arrow key-value metadata;
- a row missing an optional field stores null / null-list; readers MUST drop those
  keys so the record matches what ``yaml.safe_load`` produces (byte-identical TTL).
"""

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import yaml
from linkml_runtime import SchemaView

from sentier_vocab.errors import SchemaValidationError

_SCHEME_METADATA_KEY = b"scheme"


def _strip_empty(row: dict) -> dict:
    """Drop keys whose value is None or an empty list.

    This is the correctness keystone for Parquet: ``to_pylist`` materializes every
    column for every row (absent optionals become null / empty), so we strip them to
    match the sparse dicts ``yaml.safe_load`` yields. Without this the emitted TTL
    would differ from the YAML-sourced TTL.
    """
    return {k: v for k, v in row.items() if v is not None and v != []}


def load_source(path: Path | str, items_key: str) -> tuple[str, list[dict]]:
    """Return ``(scheme, records)`` from a ``.yaml`` or ``.parquet`` source file.

    ``items_key`` is the collection's plural slot name (resolved from the schema's
    tree-root); it is only needed to find the list inside a YAML collection mapping.
    """
    path = Path(path)
    if path.suffix in (".yaml", ".yml"):
        raw = yaml.safe_load(path.read_text())
        if not isinstance(raw, dict) or "scheme" not in raw:
            raise SchemaValidationError(f"{path}: not a collection mapping with a 'scheme' key")
        return raw["scheme"], (raw.get(items_key) or [])
    if path.suffix == ".parquet":
        table = pq.read_table(path)
        metadata = table.schema.metadata or {}
        scheme = metadata.get(_SCHEME_METADATA_KEY)
        if scheme is None:
            raise SchemaValidationError(
                f"{path}: parquet file is missing required '{_SCHEME_METADATA_KEY.decode()}' "
                f"schema metadata"
            )
        return scheme.decode(), [_strip_empty(row) for row in table.to_pylist()]
    raise SchemaValidationError(
        f"{path}: unsupported source format {path.suffix!r} (expected .yaml or .parquet)"
    )


def arrow_schema_for(sv: SchemaView, class_name: str):
    """Build an explicit Arrow schema for a concept class from its LinkML slots.

    Scalar slot -> ``string``; ``multivalued`` slot -> ``list<string>``. Internal
    slots (e.g. the collection ``scheme``) are excluded — ``scheme`` is stored as file
    metadata, not a column. An explicit schema is mandatory: ``from_pylist`` infers
    columns from the first row and silently drops optional columns absent there.
    """

    def _ann_internal(slot) -> bool:
        anns = getattr(slot, "annotations", None) or {}
        return "internal" in anns

    fields = []
    for slot_name in sv.class_slots(class_name):
        slot = sv.induced_slot(slot_name, class_name)
        if _ann_internal(slot):
            continue
        fields.append((slot_name, pa.list_(pa.string()) if slot.multivalued else pa.string()))
    return pa.schema(fields)


def dump_parquet(scheme: str, records: list[dict], schema: pa.Schema, path: Path | str) -> Path:
    """Write ``records`` to Parquet with an explicit Arrow ``schema`` and ``scheme`` metadata.

    Rows are sorted by ``notation`` (fallback ``iri``) and compression is pinned, so the
    file is content-stable across re-runs. Used by the one-shot YAML->Parquet migration
    and any local export; routine delivery is produced by sentier-importers.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(records, key=lambda r: (r.get("notation") or r.get("iri") or ""))
    table = pa.Table.from_pylist(ordered, schema=schema)
    table = table.replace_schema_metadata({_SCHEME_METADATA_KEY.decode(): scheme})
    pq.write_table(table, path, compression="snappy")
    return path
