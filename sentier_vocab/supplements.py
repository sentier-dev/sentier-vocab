from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import SKOS

QUDTS = Namespace("http://qudt.org/schema/qudt/")


def add_quantity_kinds_to_graph(
    input_ttl: Path,
    qudt_ttl: Path,
) -> Path:
    """
    The `input_ttl` concept scheme was written by hand (!), but we can make it more useful by
    positioning each input concept in the QUDT quantity kind hierarchy.
    """
    output_ttl = input_ttl.with_suffix(".supplemented" + input_ttl.suffix)
    input_graph = Graph().parse(input_ttl)
    qudt = Graph().parse(qudt_ttl)

    qudt_qk_mapping = {
        s: o
        for s, v, o in qudt.triples((None, QUDTS.hasQuantityKind, None))
        if o.startswith("https://vocab.sentier.dev/units/quantity-kind/")
        and s.startswith("https://vocab.sentier.dev/units/unit/")
    }
    qudt_d_mapping = {
        s: o
        for s, v, o in qudt.triples((None, QUDTS.hasDimensionVector, None))
        if o.startswith("http://qudt.org/vocab/dimensionvector/")
        and s.startswith("https://vocab.sentier.dev/units/unit/")
    }

    for s, v, o in input_graph.triples((None, SKOS.exactMatch, None)):
        if o.startswith("https://vocab.sentier.dev/units/unit/"):
            input_graph.add((s, QUDTS.hasQuantityKind, qudt_qk_mapping[o]))
            input_graph.add((s, QUDTS.hasDimensionVector, qudt_d_mapping[o]))

    input_graph.serialize(destination=output_ttl)
    return output_ttl


if __name__ == "__main__":
    vocab_data_dir = Path(__file__).parent / "data"
    add_quantity_kinds_to_graph(
        vocab_data_dir / "simapro.ttl", vocab_data_dir / "qudt-sentier-dev.ttl"
    )
