import importlib.util

from sentier_vocab import paths


def test_generated_pydantic_model_imports():
    module_path = paths.SCHEMAS_DIR / "_generated" / "elementary_flow.py"
    assert module_path.exists(), "run: gen-pydantic schemas/elementary-flow.yaml"
    spec = importlib.util.spec_from_file_location("ef_generated", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert hasattr(module, "ElementaryFlow")
    assert hasattr(module, "ElementaryFlowCollection")
