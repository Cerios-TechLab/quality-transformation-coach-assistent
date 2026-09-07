"""Tests for configuration loading."""
import os
from pathlib import Path

from quality_coach_mcp.config import load_config, AppConfig


def test_load_config_from_file(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
github:
  token_env: GITHUB_TOKEN
  default_org: "TestOrg"
cicd:
  provider: github_actions
coverage:
  source: local
  format: cobertura
projects:
  - name: "test-project"
    repo: "/tmp/test"
    github: "org/test-repo"
""")
    config = load_config(str(config_file))
    assert config.github.default_org == "TestOrg"
    assert len(config.projects) == 1
    assert config.projects[0].name == "test-project"


def test_load_config_missing_file_uses_defaults():
    config = load_config("/nonexistent/config.yaml")
    assert config.github.default_org == "Cerios-TechLab"


def test_load_config_env_token(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test-token-123")
    config = load_config()
    assert config.github.token == "test-token-123"
