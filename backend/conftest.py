

import pytest as _pytest


@_pytest.fixture(autouse=True)
def _reset_ai_cooldowns():
    from app import ai_models
    ai_models.reset()
    yield
    ai_models.reset()
