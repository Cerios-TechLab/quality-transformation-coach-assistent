"""Quality Transformation Coach MCP Server — entry point."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure src/ is on path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP

from quality_coach_mcp.config import load_config
from quality_coach_mcp.tools.code_analysis import CodeAnalysisTools
from quality_coach_mcp.tools.issue_analysis import IssueAnalysisTools
from quality_coach_mcp.tools.cicd_tools import CICTools
from quality_coach_mcp.tools.knowledge_tools import KnowledgeTools

mcp = FastMCP("quality-coach")

# Load config and initialise tool groups
config = load_config()
code_tools = CodeAnalysisTools(config)
issue_tools = IssueAnalysisTools(config)
cicd_tools = CICTools(config)
knowledge_tools = KnowledgeTools(config)


# ── Code Analysis Tools ──────────────────────────────────────────────

@mcp.tool()
async def analyze_code_quality(repo_path: str, branch: str = "main") -> dict:
    """Scan a repository for code quality metrics (complexity, duplication, smells).

    Args:
        repo_path: Local filesystem path to the repository
        branch: Git branch to analyze (default: main)
    """
    return await code_tools.analyze_code_quality(repo_path, branch)


@mcp.tool()
async def analyze_test_coverage(repo_path: str) -> dict:
    """Analyze test coverage by comparing test files against source files.

    Args:
        repo_path: Local filesystem path to the repository
    """
    return await code_tools.analyze_test_coverage(repo_path)


@mcp.tool()
async def detect_test_patterns(repo_path: str) -> dict:
    """Detect test patterns and anti-patterns in a repository.

    Args:
        repo_path: Local filesystem path to the repository
    """
    return await code_tools.detect_test_patterns(repo_path)


@mcp.tool()
async def analyze_flaky_tests(github_ref: str, run_ids: list[int] | None = None) -> dict:
    """Detect flaky tests from CI run data.

    Args:
        github_ref: GitHub 'owner/repo' reference
        run_ids: Optional list of workflow run IDs to analyze
    """
    return await code_tools.analyze_flaky_tests(github_ref)


# ── Issue & Defect Tools ─────────────────────────────────────────────

@mcp.tool()
async def defect_trend_analysis(github_ref: str, days: int = 90) -> dict:
    """Analyze issue trends (volume, resolution time, severity) for a repository.

    Args:
        github_ref: GitHub 'owner/repo' reference
        days: Number of days to look back (default: 90)
    """
    return await issue_tools.defect_trend_analysis(github_ref, days)


@mcp.tool()
async def quality_hotspot_detection(github_ref: str) -> dict:
    """Identify files with the highest defect density (hotspots).

    Args:
        github_ref: GitHub 'owner/repo' reference
    """
    return await issue_tools.quality_hotspot_detection(github_ref)


@mcp.tool()
async def root_cause_categories(github_ref: str) -> dict:
    """Categorise closed bugs by root cause (code, design, requirements, security).

    Args:
        github_ref: GitHub 'owner/repo' reference
    """
    return await issue_tools.root_cause_categories(github_ref)


# ── CI/CD Tools ──────────────────────────────────────────────────────

@mcp.tool()
async def pipeline_health(github_ref: str, days: int = 30) -> dict:
    """Analyze CI/CD pipeline health (success rate, duration trends).

    Args:
        github_ref: GitHub 'owner/repo' reference
        days: Number of days to look back (default: 30)
    """
    return await cicd_tools.pipeline_health(github_ref, days)


@mcp.tool()
async def test_result_summary(github_ref: str, run_id: int) -> dict:
    """Get test results summary for a specific CI workflow run.

    Args:
        github_ref: GitHub 'owner/repo' reference
        run_id: GitHub Actions workflow run ID
    """
    return await cicd_tools.test_result_summary(github_ref, run_id)


@mcp.tool()
async def quality_gate_check(
    github_ref: str, gate_id: str = "pull_request", metrics: dict | None = None
) -> dict:
    """Check if quality gates are met for a project.

    Args:
        github_ref: GitHub 'owner/repo' reference
        gate_id: Quality gate to check (default: 'pull_request')
        metrics: Optional dict of metric values to check against gate criteria
    """
    return await cicd_tools.quality_gate_check(github_ref, gate_id, metrics)


# ── Knowledge & Maturity Tools ───────────────────────────────────────

@mcp.tool()
async def maturity_assessment(project: str, scores: dict[str, int] | None = None) -> dict:
    """Run a TMMi maturity assessment for a project.

    Args:
        project: Project name
        scores: Optional dict mapping assessment areas to scores (1-5)
    """
    return await knowledge_tools.maturity_assessment(project, scores)


@mcp.tool()
async def quality_recommendations(
    maturity_scores: dict[str, int], context: dict | None = None
) -> dict:
    """Generate prioritised quality improvement recommendations.

    Args:
        maturity_scores: Dict mapping maturity areas to scores (1-5)
        context: Optional additional context (team size, domain, etc.)
    """
    return await knowledge_tools.quality_recommendations(maturity_scores, context)


@mcp.tool()
async def framework_lookup(framework: str, topic: str | None = None) -> dict:
    """Look up information about a quality framework (ISO 25010, TMMi).

    Args:
        framework: Framework name ('iso25010' or 'tmmi')
        topic: Optional specific topic within the framework
    """
    return await knowledge_tools.framework_lookup(framework, topic)


@mcp.tool()
async def generate_quality_report(
    project: str,
    period: str = "last-30-days",
    maturity_scores: dict[str, int] | None = None,
    coverage_pct: float | None = None,
    cicd_success_rate: float | None = None,
) -> str:
    """Generate a comprehensive Markdown quality report.

    Args:
        project: Project name
        period: Reporting period (e.g., 'last-30-days', 'Q3-2026')
        maturity_scores: Optional maturity scores by area
        coverage_pct: Optional test coverage percentage
        cicd_success_rate: Optional CI/CD pipeline success rate
    """
    return await knowledge_tools.generate_quality_report(
        project, period, maturity_scores, coverage_pct, cicd_success_rate
    )


if __name__ == "__main__":
    mcp.run()
