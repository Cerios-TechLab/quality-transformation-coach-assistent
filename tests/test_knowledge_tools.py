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


async def test_ai_readiness_scan_template(tools):
    result = await tools.ai_readiness_scan("test-project", None)
    assert result["framework"] == "AI Readiness Scan MVP1"
    assert result["total_questions"] == 60
    assert len(result["domains"]) == 5
    assert "No answers provided" in result["message"]
    for domain in result["domains"]:
        assert domain["question_count"] > 0
        for q in domain["questions"]:
            assert "maturity_level" in q
            assert "index" in q


async def test_ai_readiness_scan_scoring(tools):
    template = await tools.ai_readiness_scan("test-project", None)
    answers = {}
    for domain in template["domains"]:
        for q in domain["questions"]:
            answers[q["question"]] = "ja"

    result = await tools.ai_readiness_scan("test-project", answers)
    assert result["framework"] == "AI Readiness Scan MVP1"
    assert result["overall_score"] == 100.0
    for name, details in result["domain_details"].items():
        assert details["score"] == 100.0
        assert details["correct"] == details["total"]
    assert len(result["recommendations"]) == 5
    assert all("volwassen niveau bereikt" in r for r in result["recommendations"])


async def test_ai_readiness_scan_partial_scoring(tools):
    template = await tools.ai_readiness_scan("test-project", None)
    answers = {}
    first_domain_id = template["domains"][0]["id"]
    for domain in template["domains"]:
        for q in domain["questions"]:
            answers[q["question"]] = "ja" if domain["id"] == first_domain_id else "nee"

    result = await tools.ai_readiness_scan("test-project", answers)
    first_name = template["domains"][0]["name"]
    assert result["domain_scores"][first_name] == 100.0
    others = [s for name, s in result["domain_scores"].items() if name != first_name]
    assert all(s == 0.0 for s in others)
    assert result["overall_score"] == 20.0
