# tests/conftest.py
import pytest
import pandas as pd
from src.warehouse.core.context import WarehouseContext

@pytest.fixture
def context():
    """Fournit une instance de WarehouseContext à tous les tests."""
    return WarehouseContext()