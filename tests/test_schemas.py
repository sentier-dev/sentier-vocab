from linkml_runtime import SchemaView

from sentier_vocab import paths


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
