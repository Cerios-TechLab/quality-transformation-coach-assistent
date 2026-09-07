"""Tests for issue analysis tools."""
import pytest
from collections import Counter

from quality_coach_mcp.tools.issue_analysis import IssueAnalysisTools
from quality_coach_mcp.config import AppConfig


@pytest.fixture
def tools():
    return IssueAnalysisTools(AppConfig())


def test_categorise_severity(tools):
    assert tools._categorise_severity({"labels": [{"name": "severity:critical"}]}) == "critical"
    assert tools._categorise_severity({"labels": [{"name": "bug"}, {"name": "priority:high"}]}) == "high"
    assert tools._categorise_severity({"labels": []}) == "medium"


def test_categorise_root_cause(tools):
    assert tools._categorise_root_cause({"labels": [{"name": "type:bug"}]}) == "code"
    assert tools._categorise_root_cause({"labels": [{"name": "type:security"}]}) == "security"
    assert tools._categorise_root_cause({"labels": []}) == "unknown"


def test_empty_issues(tools):
    trends = tools._compute_trends([])
    assert trends == []
