"""Tests for knowledge and maturity tools."""
import pytest

from quality_coach_mcp.tools.knowledge_tools import KnowledgeTools
from quality_coach_mcp.config import AppConfig


@pytest.fixture
def tools():
    return KnowledgeTools(AppConfig())


def test_framework_lookup_iso25010(tools):
    result = tools._lookup_framework("iso25010", "maintainability")
    assert result is not None
    assert result["id"] == "maintainability"
    assert "Modularity" in [sc["name"] for sc in result["sub_characteristics"]]


def test_framework_lookup_tmmi(tools):
    result = tools._lookup_framework("tmmi", "test_planning")
    assert result is not None
    assert result["id"] == "test_planning"
    assert len(result["levels"]) == 5


def test_calculate_maturity_score(tools):
    scores = {"test_planning": 3, "test_design": 2, "test_execution": 4}
    overall = tools._calculate_overall_level(scores)
    assert overall == 3
