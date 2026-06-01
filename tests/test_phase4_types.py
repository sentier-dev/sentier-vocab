import pytest
import yaml
from linkml_runtime import SchemaView

from sentier_vocab import paths
from sentier_vocab.iris import identifier_from, iri_for_cf
from sentier_vocab.schemas import validate_data_file

# (schema filename, data category, data filename, expected member-collection class)
TYPES = [
    ("flow-property.yaml", "flow-properties", "core.yaml", "FlowPropertyCollection"),
    ("unit-group.yaml", "unit-groups", "core.yaml", "UnitGroupCollection"),
    ("product.yaml", "products", "core.yaml", "ProductCollection"),
    ("impact-category.yaml", "impact-categories", "core.yaml", "ImpactCategoryCollection"),
    ("lcia-method.yaml", "lcia-methods", "core.yaml", "LCIAMethodCollection"),
    ("source.yaml", "sources", "core.yaml", "SourceCollection"),
    ("contact.yaml", "contacts", "core.yaml", "ContactCollection"),
    ("model-term.yaml", "model-terms", "core.yaml", "ModelTermCollection"),
    (
        "characterization-factor.yaml",
        "characterization-factors",
        "core.yaml",
        "CharacterizationFactorCollection",
    ),
    ("process.yaml", "processes", "core.yaml", "ProcessCollection"),
]


@pytest.mark.parametrize("schema,category,data,collection", TYPES)
def test_schema_loads_and_pilot_validates(schema, category, data, collection):
    schema_path = paths.SCHEMAS_DIR / schema
    sv = SchemaView(str(schema_path))
    assert collection in sv.all_classes()
    assert sv.get_class(collection).tree_root is True
    layer = sv.get_class(collection).annotations.get("layer")
    assert layer is not None and layer.value in ("vocabulary", "data")
    data_path = paths.DATA_DIR / category / data
    assert data_path.exists()
    assert validate_data_file(data_path, schema_path) is True


@pytest.mark.parametrize("schema,category,data,collection", TYPES)
def test_schema_id_is_stable_uri_and_standalone(schema, category, data, collection):
    text = (paths.SCHEMAS_DIR / schema).read_text()
    parsed = yaml.safe_load(text)
    assert parsed["id"].startswith("https://vocab.sentier.dev/schemas/")
    for imp in parsed.get("imports", []):
        assert imp in ("linkml:types", "common")
    assert "app/" not in text and str(paths.REPO_ROOT) not in text


def test_characterization_factor_iris_follow_convention():
    data = yaml.safe_load((paths.DATA_DIR / "characterization-factors" / "core.yaml").read_text())
    for cf in data["characterization_factors"]:
        expected = iri_for_cf(
            identifier_from(cf["method"]),
            identifier_from(cf["impact_category"]),
            identifier_from(cf["flow"]),
        )
        assert cf["iri"] == str(expected), f"CF iri {cf['iri']} != convention {expected}"
