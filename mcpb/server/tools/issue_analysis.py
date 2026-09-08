"""Issue and defect analysis tools."""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quality_coach_mcp.config import AppConfig


class IssueAnalysisTools:
    """Tools for analyzing defects, issue trends, and quality hotspots."""

    def __init__(self, config: AppConfig):
        self.config = config

    def _categorise_severity(self, issue: dict) -> str:
        """Determine severity from issue labels."""
        label_names = [l["name"].lower() for l in issue.get("labels", [])]
        for name in label_names:
            if "critical" in name or "p0" in name:
                return "critical"
            if "high" in name or "p1" in name:
                return "high"
            if "low" in name or "p3" in name:
                return "low"
        return "medium"

    def _categorise_root_cause(self, issue: dict) -> str:
        """Categorise bug root cause from labels."""
        label_names = [l["name"].lower() for l in issue.get("labels", [])]
        for name in label_names:
            if "security" in name:
                return "security"
            if "performance" in name:
                return "performance"
            if "ui" in name or "ux" in name or "design" in name:
                return "design"
            if "requirement" in name or "spec" in name:
                return "requirements"
            if "type:bug" in name or "bug" in name:
                return "code"
        return "unknown"

    def _compute_trends(self, issues: list[dict], weeks: int = 12) -> list[dict]:
        """Compute issue trends grouped by week."""
        if not issues:
            return []

        now = datetime.now()
        weekly = defaultdict(lambda: {"opened": 0, "closed": 0, "resolution_days": []})

        for issue in issues:
            created = issue.get("created_at", "")
            closed = issue.get("closed_at")

            try:
                created_date = datetime.fromisoformat(created.replace("Z", "+00:00")).replace(tzinfo=None)
            except (ValueError, TypeError):
                continue

            week_offset = min((now - created_date).days // 7, weeks - 1)
            week_label = f"Week -{week_offset}"
            weekly[week_label]["opened"] += 1

            if closed:
                try:
                    closed_date = datetime.fromisoformat(closed.replace("Z", "+00:00")).replace(tzinfo=None)
                    resolution_days = (closed_date - created_date).days
                    weekly[week_label]["resolution_days"].append(resolution_days)
                except (ValueError, TypeError):
                    pass

        trends = []
        for week, data in sorted(weekly.items()):
            avg_resolution = (
                round(sum(data["resolution_days"]) / len(data["resolution_days"]), 1)
                if data["resolution_days"]
                else 0.0
            )
            trends.append({
                "period": week,
                "opened": data["opened"],
                "closed": data["closed"],
                "avg_resolution_days": avg_resolution,
            })

        return trends

    async def defect_trend_analysis(self, github_ref: str, days: int = 90) -> dict:
        """Analyze issue trends for a repository."""
        from quality_coach_mcp.adapters.github_adapter import GitHubAdapter

        adapter = GitHubAdapter(self.config)
        issues = await adapter.get_issues(github_ref, state="all")

        cutoff = datetime.now() - timedelta(days=days)
        filtered = []
        for issue in issues:
            try:
                created = datetime.fromisoformat(
                    issue["created_at"].replace("Z", "+00:00")
                ).replace(tzinfo=None)
                if created >= cutoff:
                    filtered.append(issue)
            except (ValueError, TypeError, KeyError):
                continue

        severity_counts = Counter()
        for issue in filtered:
            sev = self._categorise_severity(issue)
            severity_counts[sev] += 1

        trends = self._compute_trends(filtered)

        return {
            "repo": github_ref,
            "total_issues": len(filtered),
            "open_issues": sum(1 for i in filtered if i.get("state") == "open"),
            "trends": trends,
            "severity_breakdown": dict(severity_counts),
        }

    async def quality_hotspot_detection(self, github_ref: str) -> dict:
        """Identify files with the most defects (hotspots)."""
        from quality_coach_mcp.adapters.github_adapter import GitHubAdapter

        adapter = GitHubAdapter(self.config)
        issues = await adapter.get_issues(github_ref, state="all")

        file_defects: dict[str, int] = defaultdict(int)
        for issue in issues:
            title = issue.get("title", "").lower()
            body = (issue.get("body") or "").lower()
            for text in [title, body]:
                paths = re.findall(r"[\w/]+\.\w{1,5}", text)
                for p in paths:
                    file_defects[p] += 1

        hotspots = sorted(file_defects.items(), key=lambda x: x[1], reverse=True)[:20]

        return {
            "repo": github_ref,
            "hotspots": [
                {"file": f, "defect_count": c, "risk_score": round(c * 1.5, 1)}
                for f, c in hotspots
            ],
        }

    async def root_cause_categories(self, github_ref: str) -> dict:
        """Categorise issues by root cause."""
        from quality_coach_mcp.adapters.github_adapter import GitHubAdapter

        adapter = GitHubAdapter(self.config)
        issues = await adapter.get_issues(github_ref, state="closed")

        categories: dict[str, int] = defaultdict(int)
        for issue in issues:
            cause = self._categorise_root_cause(issue)
            categories[cause] += 1

        return {
            "repo": github_ref,
            "categories": dict(categories),
            "total_analyzed": len(issues),
        }
