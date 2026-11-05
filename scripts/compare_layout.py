"""Prove the new generator reproduces the old TTL graphs. Run once, then delete.

    uv run python scripts/compare_layout.py OLD_DIR NEW_DIR

Per category, the union of all old ``<category>*.ttl`` graphs, minus the triples
that leave vocab (skos:exactMatch to Brightway, ont:hasExchange and the Exchange
nodes, the characterization-factors category) and minus dcterms:source (which
the new layout adds to every term), must equal the union of the new graphs
minus dcterms:source. Graphs have no blank nodes, so set equality is isomorphism.
"""

import sys
from collections import defaultdict
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS, RDF, SKOS

ONT = "https://vocab.sentier.dev/ontology/"
BRIGHTWAY = ("https://vocab.brightway.one/", "https://vocab.brightway.dev/")


def _load(directory: Path) -> dict[str, set]:
    triples = defaultdict(set)
    for path in sorted(directory.glob("*.ttl")):
        category = path.name.split(".")[0]
        if category == "characterization-factors":
            continue
        triples[category] |= set(Graph().parse(path, format="turtle"))
    return triples


def _strip_old(triples: set) -> set:
    exchange_nodes = {s for s, p, o in triples if p == RDF.type and o == URIRef(ONT + "Exchange")}
    return {
        (s, p, o)
        for s, p, o in triples
        if not (p == SKOS.exactMatch and str(o).startswith(BRIGHTWAY))
        and p != URIRef(ONT + "hasExchange")
        and s not in exchange_nodes
        and p != DCTERMS.source
    }


NEW_TERMS = {URIRef("https://vocab.sentier.dev/sources/sentier-core")}  # minted by the migration


def _strip_new(triples: set) -> set:
    return {t for t in triples if t[1] != DCTERMS.source and t[0] not in NEW_TERMS}


def main(old_dir: str, new_dir: str) -> int:
    old = _load(Path(old_dir))
    new = _load(Path(new_dir))
    ok = True
    for category in sorted(set(old) | set(new)):
        a = _strip_old(old.get(category, set()))
        b = _strip_new(new.get(category, set()))
        missing, extra = a - b, b - a
        status = "OK  " if not missing and not extra else "DIFF"
        ok &= status == "OK  "
        print(
            f"{status} {category}: old {len(a)} new {len(b)} "
            f"missing {len(missing)} extra {len(extra)}"
        )
        for t in sorted(missing, key=str)[:5]:
            print("   missing", t)
        for t in sorted(extra, key=str)[:5]:
            print("   extra  ", t)
    for category, triples in new.items():
        subjects = {s for s, p, o in triples if p == SKOS.inScheme}
        sources = defaultdict(int)
        for s, p, o in triples:
            if p == DCTERMS.source:
                sources[s] += 1
        bad = [s for s in subjects if sources[s] != 1]
        if bad:
            ok = False
            print(
                f"DIFF {category}: {len(bad)} terms without exactly one dcterms:source, "
                f"e.g. {bad[:3]}"
            )
    print("EQUAL" if ok else "NOT EQUAL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
