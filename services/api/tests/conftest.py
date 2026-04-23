from __future__ import annotations

import sys
from pathlib import Path

import pytest

API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(autouse=True)
def reset_rate_limit_store():
    """Reset the in-memory rate limit store before each test to prevent cross-test interference."""
    from app.core import rate_limit
    rate_limit._store.clear()
    yield
    rate_limit._store.clear()
