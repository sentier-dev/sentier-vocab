import subprocess
import sys

import pytest
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, SKOS
from tests.conftest import CORE

from sentier_vocab import paths
from sentier_vocab.layers import write_terms


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "sentier_vocab", *args], capture_output=True, text=True
    )


def test_cli_validate_and_generate_on_fixture(layout, tmp_path):
    terms_dir, relations_dir = layout
    result = _run("validate", "--terms", str(terms_dir), "--relations", str(relations_dir))
    assert result.returncode == 0, result.stderr + result.stdout
    assert "valid" in result.stdout
    out = tmp_path / "out"
    result = _run(
        "generate",
        "--terms",
        str(terms_dir),
        "--relations",
        str(relations_dir),
        "--output-dir",
        str(out),
    )
    assert result.returncode == 0, result.stderr
    graph = Graph().parse(out / "flows.ttl", format="turtle")
    saline = URIRef("https://vocab.sentier.dev/flows/ENVO_00002010")
    assert (saline, SKOS.broader, URIRef("https://vocab.sentier.dev/flows/ENVO_00002006")) in graph
    assert (saline, RDF.type, SKOS.Concept) in graph


def test_cli_validate_reports_errors_and_fails(layout):
    terms_dir, relations_dir = layout
    bad = {
        "iri": "https://vocab.sentier.dev/flows/z",
        "type": "widget",
        "pref_label": "z",
        "source": CORE,
    }
    write_terms([bad], terms_dir, "zed")
    result = _run("validate", "--terms", str(terms_dir), "--relations", str(relations_dir))
    assert result.returncode == 1
    assert "widget" in result.stdout


@pytest.mark.skipif(not paths.TERMS_DIR.exists(), reason="layers not migrated yet")
def test_cli_on_repository_layout():
    """The committed layers validate (slow; the real data)."""
    result = _run("validate")
    assert result.returncode == 0, result.stdout
