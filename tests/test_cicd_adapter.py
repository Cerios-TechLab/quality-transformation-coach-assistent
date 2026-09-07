"""Tests for CI/CD adapter."""
import pytest
from unittest.mock import AsyncMock, patch

from quality_coach_mcp.adapters.cicd_adapter import CICDAdapter
from quality_coach_mcp.config import AppConfig


@pytest.fixture
def adapter():
    config = AppConfig()
    return CICDAdapter(config)


def test_calculate_success_rate(adapter):
    runs = [
        {"conclusion": "success"},
        {"conclusion": "success"},
        {"conclusion": "failure"},
        {"conclusion": "success"},
    ]
    rate = adapter._calculate_success_rate(runs)
    assert rate == 75.0


def test_calculate_success_rate_empty(adapter):
    rate = adapter._calculate_success_rate([])
    assert rate == 0.0


def test_calculate_avg_duration(adapter):
    runs = [
        {"run_started_at": "2026-01-01T10:00:00Z", "updated_at": "2026-01-01T10:05:00Z"},
        {"run_started_at": "2026-01-01T11:00:00Z", "updated_at": "2026-01-01T11:03:00Z"},
    ]
    avg = adapter._calculate_avg_duration(runs)
    assert 200 <= avg <= 400  # ~240 seconds average
