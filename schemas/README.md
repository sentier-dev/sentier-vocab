# schemas/

LinkML schemas describing each Sentier.dev data type. `common.yaml` holds shared SKOS
building blocks; one schema per type `is_a: Concept`. `_generated/` holds derived Pydantic
models (build artifact). Validate data with `app/sentier_vocab/schemas.py`.
