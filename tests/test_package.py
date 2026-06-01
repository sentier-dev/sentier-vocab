"""Package-level structural tests."""

from pathlib import Path

import sentier_vocab


def test_package_imports_and_has_version():
    assert isinstance(sentier_vocab.__version__, str)
    assert sentier_vocab.__version__


def test_package_lives_under_app_dir():
    pkg_dir = Path(sentier_vocab.__file__).resolve().parent
    assert pkg_dir.parent.name == "app", f"expected app/sentier_vocab, got {pkg_dir}"


def test_importers_are_accessible():
    from sentier_vocab.importers.envo import ENVO
    from sentier_vocab.importers.qudt import QUDT

    assert ENVO is not None
    assert QUDT is not None
