# data/

Canonical source of truth for Sentier.dev **native** curated terms, one subfolder per
LCIA category (ILCD-aligned). Each file is human-authored YAML validated against the
matching schema in `schemas/`, then serialized to TTL in `output/` by `app/sentier_vocab/generate.py`.

External-ontology terms (ENVO, QUDT, OEO, geonames) are NOT here — they are produced by the
transitional importer layer in `app/sentier_vocab/importers/`.
