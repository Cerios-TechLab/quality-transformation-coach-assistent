"""Tests for code analysis tools."""
import pytest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

from quality_coach_mcp.tools.code_analysis import CodeAnalysisTools
from quality_coach_mcp.config import AppConfig


@pytest.fixture
def tools():
    return CodeAnalysisTools(AppConfig())


def test_count_test_files(tools):
    file_list = [
        "src/app.py", "src/utils.py",
        "tests/test_app.py", "tests/test_utils.py",
        "tests/integration/test_api.py",
    ]
    unit, integration, e2e = tools._categorise_test_files(file_list)
    assert unit == 2
    assert integration == 1
    assert e2e == 0


def test_calculate_avg_complexity(tools):
    files = [
        {"name": "a.py", "complexity": 10},
        {"name": "b.py", "complexity": 20},
        {"name": "c.py", "complexity": 5},
    ]
    avg = tools._calculate_avg_complexity(files)
    assert avg == 11.67


def test_identify_test_type(tools):
    assert tools._identify_test_type("tests/test_app.py") == "unit"
    assert tools._identify_test_type("tests/integration/test_api.py") == "integration"
    assert tools._identify_test_type("tests/e2e/test_login.py") == "e2e"
    assert tools._identify_test_type("src/app.py") == "unknown"
