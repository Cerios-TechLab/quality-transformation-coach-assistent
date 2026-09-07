"""GitHub API adapter for quality data extraction."""
from __future__ import annotations

import httpx

from quality_coach_mcp.config import AppConfig
from quality_coach_mcp.models.types import (
    CodeQualityResult,
    IssueAnalysis,
    CICDResult,
    DefectTrend,
)

GITHUB_API = "https://api.github.com"


class GitHubAdapter:
    """Lightweight GitHub API wrapper for quality metrics."""

    def __init__(self, config: AppConfig):
        self.config = config
        self._headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {config.github.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def parse_owner_repo(self, github_ref: str) -> tuple[str, str]:
        """Parse 'owner/repo' string, handling extra slashes by joining parts after first."""
        parts = github_ref.strip("/").split("/")
        return parts[0], "/".join(parts[1:])

    async def get_issues(
        self, github_ref: str, state: str = "all", per_page: int = 100
    ) -> list[dict]:
        """Fetch issues from a GitHub repository."""
        owner, repo = self.parse_owner_repo(github_ref)
        url = f"{GITHUB_API}/repos/{owner}/{repo}/issues"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url, headers=self._headers, params={"state": state, "per_page": per_page}
            )
            resp.raise_for_status()
            return resp.json()

    async def get_pull_requests(self, github_ref: str, state: str = "all") -> list[dict]:
        """Fetch pull requests from a GitHub repository."""
        owner, repo = self.parse_owner_repo(github_ref)
        url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url, headers=self._headers, params={"state": state, "per_page": 100}
            )
            resp.raise_for_status()
            return resp.json()

    async def get_workflow_runs(
        self, github_ref: str, per_page: int = 30
    ) -> list[dict]:
        """Fetch recent GitHub Actions workflow runs."""
        owner, repo = self.parse_owner_repo(github_ref)
        url = f"{GITHUB_API}/repos/{owner}/{repo}/actions/runs"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url, headers=self._headers, params={"per_page": per_page}
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("workflow_runs", [])

    async def get_repo_info(self, github_ref: str) -> dict:
        """Fetch basic repository information."""
        owner, repo = self.parse_owner_repo(github_ref)
        url = f"{GITHUB_API}/repos/{owner}/{repo}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers)
            resp.raise_for_status()
            return resp.json()
