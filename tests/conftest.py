"""Shared test fixtures."""
import pytest
from quality_coach_mcp.config import AppConfig, GitHubConfig


@pytest.fixture
def app_config():
    return AppConfig(
        github=GitHubConfig(token="test-token", default_org="TestOrg")
    )
