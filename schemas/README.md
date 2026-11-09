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
