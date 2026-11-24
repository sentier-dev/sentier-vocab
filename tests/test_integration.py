import subprocess
import sys

from rdflib import Graph, URIRef
from rdflib.namespace import RDF, SKOS
from tests.conftest import CORE, EF, FLOWS, KG, ef_terms

from sentier_vocab.layers import write_relations, write_terms


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


def test_cli_on_repository_layout():
    """The committed layers validate (slow; the real data)."""
    result = _run("validate")
    assert result.returncode == 0, result.stdout


def test_cli_duplicate_flows_prints_the_list_of_a_release(layout):
    terms_dir, relations_dir = layout
    twin = {
        "iri": FLOWS + "twin",
        "type": "elementary-flow",
        "pref_label": "Isosorbide",
        "source": EF,
        "attributes": {"compartment": "air"},
    }
    write_terms(ef_terms() + [twin], terms_dir, "ef-3.1")
    edges = [
        {"subject": FLOWS + code, "predicate": "qudt:hasUnit", "object": KG, "source": EF}
        for code in ("0000b186", "twin")
    ]
    write_relations(edges, relations_dir, "ef-3.1")
    args = ("--terms", str(terms_dir), "--relations", str(relations_dir))
    assert _run("validate", *args).returncode == 1
    result = _run("duplicate-flows", "ef-3.1", *args)
    assert result.returncode == 0, result.stderr
    assert f"{FLOWS}0000b186\n{FLOWS}twin\n" in result.stdout
    known = terms_dir.parent / "schemas" / "known-duplicate-flows"
    known.mkdir(parents=True)
    (known / "ef-3.1.txt").write_text(result.stdout, encoding="utf-8")
    assert _run("validate", *args).returncode == 0
    elsewhere = _run("validate", *args, "--known-duplicates", str(terms_dir.parent / "none"))
    assert elsewhere.returncode == 1
    assert _run("duplicate-flows", "nowhere-1", *args).returncode == 1
