# schemas/

Two plain YAML contracts, validated in code by `app/sentier_vocab/validate.py`:

- `term.yaml`: the columns of every file under `terms/` and the `types` section
  (one entry per term type: IRI namespace, output category, RDF class, allowed
  attribute keys with their predicate and datatype).
- `relation.yaml`: the columns of every file under `relations/` and the
  `predicates` section (one entry per allowed predicate: subject types, object
  types, allowed external IRI prefixes, cardinality).

Adding a term type is one entry in `term.yaml`; adding a kind of link is one
entry in `relation.yaml`. No directory, no code change.

## known-duplicate-flows/

One text file per source release that needs it, `<release>.txt`: the IRIs of the
elementary flows that share their identity (label, compartment, sub_compartment,
unit) with another flow of the release and are accepted as the source publishes
them. One IRI per line; `#` comments and blank lines are ignored, and the generated
comments show the shared identity above each group.

- `validate` accepts a shared identity only when every flow sharing it is listed.
- A listed IRI that is not an elementary flow of the release, that shares its
  identity with no other flow, or that is listed twice is an error, so the list
  cannot outlive the duplicates it names.
- The file is generated and then reviewed:
  `uv run python -m sentier_vocab duplicate-flows <release> > schemas/known-duplicate-flows/<release>.txt`.

A plain list and not YAML: the IRIs are the only content the validator reads, and
one IRI per line keeps the diff of a regenerated list readable.
