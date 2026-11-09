from sentier_vocab import coverage, iris
from sentier_vocab.layers import load_terms


def test_catalog_covers_every_registry_namespace():
    catalog_namespaces = {dt.namespace for dt in coverage.CATALOG}
    for namespace in iris.NAMESPACES.values():
        assert namespace in catalog_namespaces, f"{namespace} missing from coverage catalog"


def test_count_terms_per_type(layout):
    terms_dir, _ = layout
    counts = coverage.count_terms(load_terms(terms_dir))
    assert counts["elementary-flow"] == 3
    assert counts["source"] == 2
    assert counts.get("unit", 0) == 0


def test_render_includes_header_and_rows(layout):
    terms_dir, _ = layout
    text = coverage.render(load_terms(terms_dir))
    assert "# Sentier.dev Vocabulary Coverage" in text
    assert "| Elementary flows |" in text and "| 3 |" in text
    assert "https://vocab.sentier.dev/flows/" in text


def test_write_creates_file(layout, tmp_path):
    terms_dir, _ = layout
    out = tmp_path / "COVERAGE.md"
    coverage.write(out, load_terms(terms_dir))
    assert "Vocabulary Coverage" in out.read_text()
