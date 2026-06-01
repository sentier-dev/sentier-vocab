from sentier_vocab import coverage, iris


def test_catalog_covers_every_registry_namespace():
    catalog_namespaces = {dt.namespace for dt in coverage.CATALOG}
    for namespace in iris.NAMESPACES.values():
        assert namespace in catalog_namespaces, f"{namespace} missing from coverage catalog"


def test_render_includes_header_and_rows():
    text = coverage.render()
    assert "# Sentier.dev Vocabulary Coverage" in text
    assert "https://vocab.sentier.dev/flows/" in text
    assert "Elementary flows" in text
    # Pilot file present -> at least one native file counted for elementary-flows.
    assert "| Elementary flows |" in text
    assert "Layer" in text
    assert "vocabulary" in text and "data" in text


def test_write_creates_file(tmp_path):
    out = tmp_path / "COVERAGE.md"
    coverage.write(out)
    assert out.exists()
    assert "Vocabulary Coverage" in out.read_text()
