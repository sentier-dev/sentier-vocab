"""Read and write the two parquet layers, ``terms/`` and ``relations/``.

Both layers have a fixed Arrow schema (see ``schemas/term.yaml`` and
``schemas/relation.yaml``). Readers get sparse dicts: null scalars, null or
empty lists are dropped, and ``attributes`` is parsed from its JSON string, so a
row looks the same whether it came from parquet or was built in memory.
Writers sort rows deterministically and shard a file that would exceed
``MAX_FILE_BYTES`` into ``<release>-NN.parquet`` pieces.
"""

from __future__ import annotations

import io
import json
import math
import re
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

#: Keep every committed file under the pre-commit large-file guard (3000 KB).
MAX_FILE_BYTES = 2_400_000
COMPRESSION = "snappy"

TERM_SCHEMA = pa.schema(
    [
        ("iri", pa.string()),
        ("type", pa.string()),
        ("pref_label", pa.string()),
        ("alt_labels", pa.list_(pa.string())),
        ("definition", pa.string()),
        ("notation", pa.string()),
        ("additional_notations", pa.list_(pa.string())),
        ("source", pa.string()),
        ("status", pa.string()),
        ("attributes", pa.string()),
    ]
)

RELATION_SCHEMA = pa.schema(
    [
        ("subject", pa.string()),
        ("predicate", pa.string()),
        ("object", pa.string()),
        ("source", pa.string()),
        ("status", pa.string()),
    ]
)

_SHARD_SUFFIX = re.compile(r"-\d{2}$")


def release_of(filename: str | Path) -> str:
    """``ef-3.1-03.parquet`` -> ``ef-3.1``; ``bafu-2026.parquet`` -> ``bafu-2026``."""
    return _SHARD_SUFFIX.sub("", Path(filename).stem)


def _sparse(row: dict) -> dict:
    out = {}
    for key, value in row.items():
        if value is None or value == []:
            continue
        if key == "attributes":
            value = json.loads(value)
            if not value:
                continue
        out[key] = value
    return out


def read_rows(path: Path | str) -> list[dict]:
    """All rows of one parquet file as sparse dicts."""
    return [_sparse(row) for row in pq.read_table(path).to_pylist()]


def _parquet_files(directory: Path | str) -> list[Path]:
    return sorted(Path(directory).glob("*.parquet"))


def load_terms(terms_dir: Path | str) -> dict[Path, list[dict]]:
    """``{file: rows}`` for every term file, in filename order."""
    return {path: read_rows(path) for path in _parquet_files(terms_dir)}


def load_relations(relations_dir: Path | str) -> dict[Path, list[dict]]:
    """``{file: rows}`` for every relation file, in filename order."""
    return {path: read_rows(path) for path in _parquet_files(relations_dir)}


def _check_columns(rows: list[dict], schema: pa.Schema) -> None:
    allowed = set(schema.names)
    for row in rows:
        unknown = set(row) - allowed
        if unknown:
            key = row.get("iri") or row.get("subject")
            raise ValueError(f"row {key!r}: unknown columns {sorted(unknown)}")


def _term_record(row: dict) -> dict:
    record = {name: row.get(name) for name in TERM_SCHEMA.names}
    attributes = row.get("attributes")
    record["attributes"] = (
        json.dumps(attributes, sort_keys=True, ensure_ascii=False) if attributes else None
    )
    return record


def _write_sharded(
    records: list[dict], schema: pa.Schema, directory: Path, release: str
) -> list[Path]:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(records, schema=schema)
    buffer = io.BytesIO()
    pq.write_table(table, buffer, compression=COMPRESSION)
    if buffer.tell() <= MAX_FILE_BYTES:
        path = directory / f"{release}.parquet"
        pq.write_table(table, path, compression=COMPRESSION)
        return [path]
    shards = max(2, math.ceil(buffer.tell() / MAX_FILE_BYTES))
    while True:
        size = math.ceil(len(records) / shards)
        paths = []
        for index in range(shards):
            piece = pa.Table.from_pylist(records[index * size : (index + 1) * size], schema=schema)
            path = directory / f"{release}-{index + 1:02d}.parquet"
            pq.write_table(piece, path, compression=COMPRESSION)
            paths.append(path)
        if all(p.stat().st_size <= MAX_FILE_BYTES for p in paths):
            return paths
        for p in paths:
            p.unlink()
        shards += 1


def write_terms(rows: list[dict], terms_dir: Path | str, release: str) -> list[Path]:
    """Write term rows (sparse dicts, ``attributes`` as a dict) for one release.

    Rows are sorted by ``(type, iri)``; returns the files written.
    """
    _check_columns(rows, TERM_SCHEMA)
    ordered = sorted(rows, key=lambda r: (r["type"], r["iri"]))
    return _write_sharded(
        [_term_record(r) for r in ordered], TERM_SCHEMA, Path(terms_dir), release
    )


def write_relations(rows: list[dict], relations_dir: Path | str, release: str) -> list[Path]:
    """Write relation rows for one release, sorted by ``(subject, predicate, object)``."""
    _check_columns(rows, RELATION_SCHEMA)
    ordered = sorted(rows, key=lambda r: (r["subject"], r["predicate"], r["object"]))
    records = [{name: r.get(name) for name in RELATION_SCHEMA.names} for r in ordered]
    return _write_sharded(records, RELATION_SCHEMA, Path(relations_dir), release)
