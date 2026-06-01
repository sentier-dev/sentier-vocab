import pytest
from linkml_runtime import SchemaView

from sentier_vocab import paths
from sentier_vocab.errors import SchemaValidationError
from sentier_vocab.schemas import validate_data_file

FIXTURES = paths.REPO_ROOT / "tests" / "fixtures"
EF_SCHEMA = paths.SCHEMAS_DIR / "elementary-flow.yaml"


def test_valid_data_file_passes():
    assert validate_data_file(FIXTURES / "valid_flows.yaml", EF_SCHEMA) is True


def test_invalid_data_file_raises():
    with pytest.raises(SchemaValidationError):
        validate_data_file(FIXTURES / "invalid_flows.yaml", EF_SCHEMA)


def test_paths_point_at_repo_root():
    assert (paths.SCHEMAS_DIR / "common.yaml").exists()
    assert paths.DATA_DIR.name == "data"
    assert paths.OUTPUT_DIR.name == "output"


def test_common_schema_defines_concept_base():
    sv = SchemaView(str(paths.SCHEMAS_DIR / "common.yaml"))
    classes = sv.all_classes()
    assert "Concept" in classes
    slots = sv.class_slots("Concept")
    assert "iri" in slots
    assert "pref_label" in slots


def test_elementary_flow_schema_structure():
    sv = SchemaView(str(paths.SCHEMAS_DIR / "elementary-flow.yaml"))
    classes = sv.all_classes()
    assert "ElementaryFlow" in classes
    assert "ElementaryFlowCollection" in classes
    # Collection is the validation tree root for a scheme/group file.
    assert classes["ElementaryFlowCollection"].tree_root is True
    # ElementaryFlow inherits the SKOS spine from Concept.
    ef_slots = sv.class_slots("ElementaryFlow")
    assert "pref_label" in ef_slots
    assert "compartment" in ef_slots
