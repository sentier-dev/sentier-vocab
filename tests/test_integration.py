import subprocess
import sys

from rdflib import Graph, URIRef
from rdflib.namespace import RDF, SKOS

from sentier_vocab import paths
from sentier_vocab.generate import generate_category


def test_end_to_end_generate_flows(tmp_path):
    out = tmp_path / "flows.ttl"
    generate_category(
        category="elementary-flows",
        schema_path=paths.SCHEMAS_DIR / "elementary-flow.yaml",
        data_path=paths.DATA_DIR / "elementary-flows" / "water.yaml",
        output_path=out,
    )
    graph = Graph().parse(out, format="turtle")
    saline = URIRef("https://vocab.sentier.dev/flows/ENVO_00002010")
    assert (saline, SKOS.broader, URIRef("https://vocab.sentier.dev/flows/ENVO_00002006")) in graph
    assert (saline, RDF.type, SKOS.Concept) in graph


def test_cli_generate_runs(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "sentier_vocab", "generate", "--output-dir", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "flows.ttl").exists()
    assert (tmp_path / "impact-categories.ttl").exists()
