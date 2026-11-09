import pytest
from rdflib import Namespace

from sentier_vocab import iris


def test_existing_namespaces_are_stable():
    # These four are the published contract — external tools depend on them.
    assert iris.NAMESPACES["flows"] == "https://vocab.sentier.dev/flows/"
    assert iris.NAMESPACES["units"] == "https://vocab.sentier.dev/units/"
    assert iris.NAMESPACES["products"] == "https://vocab.sentier.dev/products/"
    assert iris.NAMESPACES["model-terms"] == "https://vocab.sentier.dev/model-terms/"


def test_new_lcia_namespaces_exact():
    assert iris.NAMESPACES["flow-properties"] == "https://vocab.sentier.dev/flow-properties/"
    assert iris.NAMESPACES["processes"] == "https://vocab.sentier.dev/processes/"
    assert iris.NAMESPACES["lcia-methods"] == "https://vocab.sentier.dev/lcia-methods/"
    assert iris.NAMESPACES["impact-categories"] == "https://vocab.sentier.dev/impact-categories/"
    assert (
        iris.NAMESPACES["characterization-factors"]
        == "https://vocab.sentier.dev/characterization-factors/"
    )
    assert iris.NAMESPACES["sources"] == "https://vocab.sentier.dev/sources/"
    assert iris.NAMESPACES["contacts"] == "https://vocab.sentier.dev/contacts/"


def test_namespace_for_returns_rdflib_namespace():
    ns = iris.namespace_for("flows")
    assert isinstance(ns, Namespace)
    assert str(ns) == "https://vocab.sentier.dev/flows/"


def test_iri_for_and_identifier_from_roundtrip():
    iri = iris.iri_for("flows", "ENVO_00002006")
    assert str(iri) == "https://vocab.sentier.dev/flows/ENVO_00002006"
    assert iris.identifier_from(iri) == "ENVO_00002006"


def test_unknown_category_raises():
    with pytest.raises(KeyError):
        iris.namespace_for("not-a-real-category")


def test_namespaces_is_immutable():
    with pytest.raises(TypeError):
        iris.NAMESPACES["flows"] = "https://evil.example.com/"


def test_identifier_from_accepts_plain_string():
    assert (
        iris.identifier_from("https://vocab.sentier.dev/processes/steel-making") == "steel-making"
    )


def test_ontology_namespace():
    assert iris.ONTOLOGY == "https://vocab.sentier.dev/ontology/"


def test_unit_groups_namespace():
    assert iris.NAMESPACES["unit-groups"] == "https://vocab.sentier.dev/units/group/"


def test_iri_for_cf_is_deterministic():
    cf = iris.iri_for_cf("ipcc-2021-gwp100", "climate-change", "ENVO_carbon_dioxide")
    assert str(cf) == (
        "https://vocab.sentier.dev/characterization-factors/"
        "ipcc-2021-gwp100_climate-change_ENVO_carbon_dioxide"
    )


def test_namespaces_come_from_term_yaml():
    from sentier_vocab import paths
    from sentier_vocab.schema import load_term_schema

    schema = load_term_schema(paths.TERM_SCHEMA)
    assert iris.NAMESPACES == {t.category: t.namespace for t in schema.types.values()}


def test_category_for_type_and_type_for_namespace():
    assert iris.category_for_type("elementary-flow") == "flows"
    assert iris.type_for_iri("https://vocab.sentier.dev/units/group/mass") == "unit-group"
    assert iris.type_for_iri("https://vocab.sentier.dev/units/KiloGM") == "unit"
    assert iris.type_for_iri("https://example.org/x") is None
