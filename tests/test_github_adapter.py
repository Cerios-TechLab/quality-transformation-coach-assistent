"""Tests for GitHub adapter."""
import pytest
from unittest.mock import AsyncMock, patch

from quality_coach_mcp.adapters.github_adapter import GitHubAdapter
from quality_coach_mcp.config import AppConfig, GitHubConfig


@pytest.fixture
def adapter():
    config = AppConfig(github=GitHubConfig(token="test-token", default_org="TestOrg"))
    return GitHubAdapter(config)


def test_adapter_initialization(adapter):
    assert adapter.config.github.token == "test-token"
    assert adapter.config.github.default_org == "TestOrg"


def test_parse_owner_repo(adapter):
    owner, repo = adapter.parse_owner_repo("TestOrg/my-repo")
    assert owner == "TestOrg"
    assert repo == "my-repo"


def test_parse_owner_repo_slash_in_name(adapter):
    owner, repo = adapter.parse_owner_repo("org/sub/repo")
    assert owner == "org"
    assert repo == "sub/repo"
