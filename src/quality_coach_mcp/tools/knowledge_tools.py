"""Knowledge and maturity assessment tools."""
from __future__ import annotations

import math
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from quality_coach_mcp.config import AppConfig


class KnowledgeTools:
    """Tools for quality framework lookup, maturity assessment, and reporting."""

    def __init__(self, config: AppConfig):
        self.config = config
        self._knowledge_dir = Path(__file__).parent.parent / "knowledge"
        self._cache: dict[str, dict] = {}

    def _load_yaml(self, name: str) -> dict:
        """Load and cache a YAML knowledge file."""
        if name not in self._cache:
            path = self._knowledge_dir / f"{name}.yaml"
            if path.exists():
                with open(path) as f:
                    self._cache[name] = yaml.safe_load(f) or {}
            else:
                self._cache[name] = {}
        return self._cache[name]

    def _lookup_framework(self, framework: str, topic: str | None = None) -> dict | None:
        """Look up a framework or specific topic within it."""
        framework = framework.lower().replace(" ", "").replace("-", "")

        if framework in ("iso25010", "iso/iec25010", "iso25010"):
            data = self._load_yaml("iso25010")
            domains = data.get("domains", [])
            if topic:
                topic_lower = topic.lower().replace(" ", "_")
                for domain in domains:
                    if domain["id"] == topic_lower or domain["name"].lower() == topic.lower():
                        return domain
                return None
            return {"framework": "ISO 25010", "domains": domains}

        if framework in ("tmmi", "testingmaturitymodel", "tmmimodel"):
            data = self._load_yaml("tmmi")
            if topic:
                topic_lower = topic.lower().replace(" ", "_")
                for area in data.get("assessment_areas", []):
                    if area["id"] == topic_lower or area["name"].lower() == topic.lower():
                        return area
                return {"levels": data.get("levels", [])}
            return {"framework": "TMMi", "levels": data.get("levels", [])}

        return None

    def _calculate_overall_level(self, scores: dict[str, int]) -> int:
        """Calculate overall maturity level from per-area scores."""
        if not scores:
            return 1
        avg = sum(scores.values()) / len(scores)
        return max(1, min(5, round(avg)))

    def _generate_recommendations(self, maturity_scores: dict[str, int], context: dict | None = None) -> list[str]:
        """Generate prioritized recommendations based on maturity scores."""
        recs_data = self._load_yaml("recommendations")
        recommendations = recs_data.get("recommendations", [])

        triggered = []
        for rec in recommendations:
            score = maturity_scores.get(rec.get("trigger_area", ""), 0)
            threshold = rec.get("trigger_level", 5)
            if score < threshold:
                triggered.append({
                    "priority": rec.get("priority", "medium"),
                    "title": rec["title"],
                    "actions": rec.get("actions", []),
                })

        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        triggered.sort(key=lambda x: priority_order.get(x["priority"], 99))

        return [f"[{r['priority'].upper()}] {r['title']}: {'; '.join(r['actions'][:2])}" for r in triggered]

    async def maturity_assessment(self, project_name: str, scores: dict[str, int] | None = None) -> dict:
        """Run a TMMi maturity assessment."""
        if scores is None:
            return {
                "project": project_name,
                "framework": "TMMi",
                "message": "No assessment data provided. Use 'scores' parameter with area scores.",
                "available_areas": ["test_planning", "test_design", "test_execution"],
            }

        overall = self._calculate_overall_level(scores)
        tmmi_data = self._load_yaml("tmmi")
        levels = tmmi_data.get("levels", [])
        level_info = next((l for l in levels if l["level"] == overall), {})

        recommendations = self._generate_recommendations(scores)

        return {
            "project": project_name,
            "framework": "TMMi",
            "overall_level": overall,
            "overall_score": round(sum(scores.values()) / len(scores), 1) if scores else 0,
            "area_scores": scores,
            "level_name": level_info.get("name", "Unknown"),
            "level_description": level_info.get("description", ""),
            "recommendations": recommendations,
        }

    async def quality_recommendations(self, maturity_scores: dict[str, int], context: dict | None = None) -> dict:
        """Generate context-sensitive quality improvement recommendations."""
        recommendations = self._generate_recommendations(maturity_scores, context)

        return {
            "maturity_scores": maturity_scores,
            "total_recommendations": len(recommendations),
            "recommendations": recommendations,
        }

    async def cicd_readiness_scan(self, project: str, answers: dict[str, str] | None = None) -> dict:
        """Run a CI/CD Readiness Scan assessment.

        Args:
            project: Project name
            answers: Optional dict mapping question text (or index) to "ja"/"nee".
                     If None, returns the full question set for manual assessment.
        """
        data = self._load_yaml("cicd_readiness")
        domains = data.get("domains", [])

        if not answers:
            # Return the full scan template
            result = {
                "project": project,
                "framework": "CI/CD Readiness Scan MVP2",
                "total_questions": sum(len(d.get("questions", [])) for d in domains),
                "domains": [],
                "message": "No answers provided. Return answers as a dict mapping question text to 'ja'/'nee'.",
            }
            for domain in domains:
                result["domains"].append({
                    "id": domain["id"],
                    "name": domain["name"],
                    "question_count": len(domain.get("questions", [])),
                    "questions": [
                        {"index": i, "question": q["question"], "maturity_level": q["maturity_level"]}
                        for i, q in enumerate(domain.get("questions", []))
                    ],
                })
            return result

        # Score each domain
        domain_scores = {}
        domain_details = {}
        for domain in domains:
            qs = domain.get("questions", [])
            correct = 0
            total = len(qs)
            max_level = 0
            details = []
            for i, q in enumerate(qs):
                answer = answers.get(q["question"], answers.get(str(i), None))
                if answer:
                    is_correct = answer.lower() in ("ja", "yes", "true", "1")
                    if is_correct:
                        correct += 1
                        max_level = max(max_level, q["maturity_level"])
                    details.append({
                        "question": q["question"],
                        "answer": answer,
                        "correct": is_correct,
                        "maturity_level": q["maturity_level"],
                    })
            score = round((correct / total) * 100, 1) if total > 0 else 0
            domain_scores[domain["name"]] = score
            domain_details[domain["name"]] = {
                "score": score,
                "correct": correct,
                "total": total,
                "max_maturity_level": max_level,
                "details": details,
            }

        overall = round(sum(domain_scores.values()) / len(domain_scores), 1) if domain_scores else 0
        building_blocks = data.get("building_blocks", {})

        return {
            "project": project,
            "framework": "CI/CD Readiness Scan MVP2",
            "overall_score": overall,
            "domain_scores": domain_scores,
            "domain_details": domain_details,
            "building_blocks": building_blocks,
            "recommendations": self._cicd_readiness_recommendations(domain_scores),
        }

    def _cicd_readiness_recommendations(self, domain_scores: dict[str, float]) -> list[str]:
        """Generate recommendations based on CI/CD readiness scores."""
        recs = []
        for domain, score in sorted(domain_scores.items(), key=lambda x: x[1]):
            if score < 30:
                recs.append(f"[CRITICAL] {domain}: Score {score}% — basisvereisten ontbreken, start met fundament")
            elif score < 60:
                recs.append(f"[HIGH] {domain}: Score {score}% — verdere uitbreiding nodig voor stabiele CI/CD")
            elif score < 80:
                recs.append(f"[MEDIUM] {domain}: Score {score}% — goed bezig, focus op optimalisatie")
            else:
                recs.append(f"[OK] {domain}: Score {score}% — volwassen niveau bereikt")
        return recs

    async def framework_lookup(self, framework: str, topic: str | None = None) -> dict:
        """Look up information about a quality framework."""
        result = self._lookup_framework(framework, topic)
        if result is None:
            return {"error": f"Framework '{framework}' not found", "available": ["iso25010", "tmmi", "cicd_readiness"]}
        return result

    async def generate_quality_report(
        self,
        project: str,
        period: str = "last-30-days",
        maturity_scores: dict[str, int] | None = None,
        coverage_pct: float | None = None,
        cicd_success_rate: float | None = None,
    ) -> str:
        """Generate a comprehensive quality report in Markdown."""
        import datetime as _dt

        lines = [
            f"# Quality Report: {project}",
            f"**Period:** {period}",
            f"**Generated:** {_dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
            "## Executive Summary",
        ]

        if maturity_scores:
            overall = self._calculate_overall_level(maturity_scores)
            tmmi_data = self._load_yaml("tmmi")
            level_name = next(
                (l["name"] for l in tmmi_data.get("levels", []) if l["level"] == overall),
                "Unknown",
            )
            lines.append(f"- **Overall Maturity:** Level {overall} ({level_name})")

        if coverage_pct is not None:
            lines.append(f"- **Test Coverage:** {coverage_pct}%")

        if cicd_success_rate is not None:
            lines.append(f"- **CI/CD Success Rate:** {cicd_success_rate}%")

        lines.append("")

        if maturity_scores:
            lines.extend([
                "## Maturity Assessment by Area",
                "",
                "| Area | Score | Level |",
                "|---|---|---|",
            ])
            for area, score in sorted(maturity_scores.items()):
                level_name = "Initial" if score <= 1 else "Managed" if score <= 2 else "Definition" if score <= 3 else "Management" if score <= 4 else "Optimization"
                lines.append(f"| {area} | {score}/5 | {level_name} |")
            lines.append("")

            recommendations = self._generate_recommendations(maturity_scores)
            if recommendations:
                lines.extend(["## Recommendations", ""])
                for rec in recommendations:
                    lines.append(f"- {rec}")
                lines.append("")

        lines.extend([
            "---",
            "*Report generated by Quality Transformation Coach MCP Server*",
        ])

        return "\n".join(lines)
