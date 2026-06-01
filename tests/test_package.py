"""Package-level structural tests."""

from pathlib import Path

import sentier_vocab


def test_package_imports_and_has_version():
    assert isinstance(sentier_vocab.__version__, str)
    assert sentier_vocab.__version__


def test_package_lives_under_app_dir():
    pkg_dir = Path(sentier_vocab.__file__).resolve().parent
    assert pkg_dir.parent.name == "app", f"expected app/sentier_vocab, got {pkg_dir}"
