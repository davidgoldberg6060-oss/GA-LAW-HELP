"""Regression: modules must import when installed at a shallow path like /app/app.

In the API image the package lives at /app/app, so Path(...).parents[2] does not
exist. Building candidate paths eagerly with parents[2] raised IndexError at import
time and made /public/courtroom-prep and /public/public-defender-offices return 500.
"""
from pathlib import Path

import pytest

from app import courtroom_prep, public_defender_offices


class _ShallowPath(type(Path())):
    @property
    def parents(self):  # only two ancestors, like /app/app
        return (Path("/app"), Path("/"))


@pytest.mark.parametrize("mod", [courtroom_prep, public_defender_offices])
def test_safe_parent_handles_shallow_install(mod, monkeypatch):
    monkeypatch.setattr(mod, "_HERE", _ShallowPath("/app/app"))
    assert mod._safe_parent(1) == Path("/")
    assert mod._safe_parent(2) is None


def test_bundled_data_found():
    assert courtroom_prep._path().is_file()
    assert public_defender_offices._path().is_file()
