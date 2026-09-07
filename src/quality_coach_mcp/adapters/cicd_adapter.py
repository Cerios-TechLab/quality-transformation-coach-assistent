"""CI/CD adapter for pipeline health and test result analysis."""
from __future__ import annotations

from datetime import datetime

import httpx

from quality_coach_mcp.adapters.github_adapter import GitHubAdapter
from quality_coach_mcp.config import AppConfig
from quality_coach_mcp.models.types import CICDResult, PipelineRun, TestResultSummary


class CICDAdapter:
    """Analyzes CI/CD pipeline data from GitHub Actions."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.github = GitHubAdapter(config)

    def _calculate_success_rate(self, runs: list[dict]) -> float:
        """Calculate the success rate from a list of workflow run dicts."""
        if not runs:
            return 0.0
        successes = sum(1 for r in runs if r.get("conclusion") == "success")
        return round((successes / len(runs)) * 100, 1)

    def _calculate_avg_duration(self, runs: list[dict]) -> float:
        """Calculate average duration in seconds from workflow run dicts."""
        durations = []
        for run in runs:
            started = run.get("run_started_at")
            updated = run.get("updated_at")
            if started and updated:
                try:
                    t_start = datetime.fromisoformat(started.replace("Z", "+00:00"))
                    t_end = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                    durations.append((t_end - t_start).total_seconds())
                except (ValueError, TypeError):
                    continue
        return round(sum(durations) / len(durations), 1) if durations else 0.0

    async def get_pipeline_health(
        self, github_ref: str, per_page: int = 30
    ) -> CICDResult:
        """Get pipeline health metrics for a project."""
        runs_raw = await self.github.get_workflow_runs(github_ref, per_page=per_page)
        success_rate = self._calculate_success_rate(runs_raw)
        avg_duration = self._calculate_avg_duration(runs_raw)

        pipeline_runs = []
        for r in runs_raw[:10]:
            pipeline_runs.append(
                PipelineRun(
                    run_id=r["id"],
                    status=r.get("status", "unknown"),
                    conclusion=r.get("conclusion"),
                    duration_seconds=self._calculate_avg_duration([r]),
                )
            )

        return CICDResult(
            project=github_ref,
            total_runs=len(runs_raw),
            success_rate=success_rate,
            avg_duration_seconds=avg_duration,
            recent_runs=pipeline_runs,
        )

    async def get_test_results(self, github_ref: str, run_id: int) -> TestResultSummary:
        """Get test result summary for a specific workflow run."""
        owner, repo = self.github.parse_owner_repo(github_ref)
        url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                headers=self.github._headers,
                params={"per_page": 100},
            )
            resp.raise_for_status()
            data = resp.json()

        total = passed = failed = skipped = 0
        for job in data.get("jobs", []):
            for step in job.get("steps", []):
                total += 1
                conclusion = step.get("conclusion")
                if conclusion == "success":
                    passed += 1
                elif conclusion == "failure":
                    failed += 1
                elif conclusion in ("skipped", "cancelled"):
                    skipped += 1

        return TestResultSummary(total=total, passed=passed, failed=failed, skipped=skipped)
