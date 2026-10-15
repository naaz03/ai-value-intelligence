from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def tables():
    from services.data_service import cached_tables, data_ready

    if not data_ready():
        from generators.generate_all import generate_and_save

        generate_and_save()
        cached_tables.cache_clear()
    return cached_tables()
