"""Tests for CI/CD tools."""
import pytest

from quality_coach_mcp.tools.cicd_tools import CICTools
from quality_coach_mcp.config import AppConfig


@pytest.fixture
def tools():
    return CICTools(AppConfig())


def test_check_quality_gate_pass(tools):
    criteria = [
        {"name": "Coverage", "required": True, "threshold": 70, "metric": "coverage_pct"},
        {"name": "Tests", "required": True, "threshold": 0, "metric": "failed_tests"},
    ]
    metrics = {"coverage_pct": 85.0, "failed_tests": 0}
    results = tools._evaluate_gate(criteria, metrics)
    assert all(r["passed"] for r in results)


def test_check_quality_gate_fail(tools):
    criteria = [
        {"name": "Coverage", "required": True, "threshold": 70, "metric": "coverage_pct"},
    ]
    metrics = {"coverage_pct": 45.0}
    results = tools._evaluate_gate(criteria, metrics)
    assert not results[0]["passed"]
