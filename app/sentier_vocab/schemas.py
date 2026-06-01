"""Validate native term YAML files against their LinkML schemas."""

from pathlib import Path

from linkml.validator import Validator
from linkml.validator.loaders import YamlLoader
from linkml.validator.plugins import JsonschemaValidationPlugin
from linkml_runtime import SchemaView

from sentier_vocab.errors import SchemaValidationError


def _get_tree_root(schema_path: Path | str) -> str:
    """Return the name of the class marked ``tree_root: true`` in the schema.

    Raises ``SchemaValidationError`` if no tree-root class can be found.
    """
    sv = SchemaView(str(schema_path))
    for name, cls in sv.all_classes().items():
        if cls.tree_root:
            return name
    raise SchemaValidationError(f"No class with tree_root: true found in schema {schema_path}")


def validate_data_file(data_path: Path | str, schema_path: Path | str) -> bool:
    """Validate a data file against a LinkML schema.

    Returns True on success; raises SchemaValidationError listing every problem
    on failure. Uses the schema's ``tree_root`` class as the validation target.

    .. note::
        This function uses ``SchemaView`` to resolve schema imports relative to
        the schema file's directory (bypassing a ``linkml.validator.validate_file``
        limitation where imports are resolved relative to the process cwd).  It
        also explicitly passes ``JsonschemaValidationPlugin(closed=True)`` so that
        required-slot enforcement is active; the default ``validate_file`` plugin
        set omits required-field checking in this version of LinkML.
    """
    schema_path = Path(schema_path)
    data_path = Path(data_path)

    sv = SchemaView(str(schema_path))
    target_class = _get_tree_root(schema_path)

    plugin = JsonschemaValidationPlugin(closed=True)
    validator = Validator(sv.schema, validation_plugins=[plugin])

    report = validator.validate_source(YamlLoader(str(data_path)), target_class)
    if report.results:
        messages = "\n".join(f"  - {result.message}" for result in report.results)
        raise SchemaValidationError(
            f"{data_path} failed validation against {schema_path}:\n{messages}"
        )
    return True
