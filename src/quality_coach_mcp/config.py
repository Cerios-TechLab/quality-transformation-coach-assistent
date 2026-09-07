"""Configuration loading for the Quality Coach MCP server."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class GitHubConfig(BaseModel):
    token: str = ""
    token_env: str = "GITHUB_TOKEN"
    default_org: str = "Cerios-TechLab"


class CICDConfig(BaseModel):
    provider: str = "github_actions"


class CoverageConfig(BaseModel):
    source: str = "local"
    format: str = "cobertura"


class ProjectConfig(BaseModel):
    name: str
    repo: str
    github: str


class AppConfig(BaseModel):
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    cicd: CICDConfig = Field(default_factory=CICDConfig)
    coverage: CoverageConfig = Field(default_factory=CoverageConfig)
    projects: list[ProjectConfig] = Field(default_factory=list)


_DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"


def load_config(path: str | None = None) -> AppConfig:
    """Load configuration from YAML file, falling back to defaults."""
    config_path = Path(path) if path else _DEFAULT_CONFIG_PATH
    data: dict[str, Any] = {}

    if config_path.exists():
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

    config = AppConfig(**data)

    # Resolve token from environment
    if not config.github.token:
        config.github.token = os.environ.get(config.github.token_env, "")

    return config
