"""Gemeinsame Fixtures: die Handfolge n = 6, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: langsamer Test (mehr als etwa 10 Sekunden); schnell mit `pytest -m \"not slow\"`")


@pytest.fixture
def hand():
    """Die Handfolge n = 6: Ränge 1 3 6 2 5 4. Handrechnung: 1 neu, 3 neu, 6 neu, 2 auf die 3, 5 auf die 6, 4 auf die 5 -> [1], [3, 2], [6, 5, 4], drei Stapel = LIS (z. B. 1 3 4)."""
    return (1, 3, 6, 2, 5, 4)
