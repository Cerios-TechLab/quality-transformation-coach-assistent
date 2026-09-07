"""Code analysis tools for quality assessment."""
from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from quality_coach_mcp.config import AppConfig


class CodeAnalysisTools:
    """Tools for analyzing code quality, coverage, and test patterns."""

    def __init__(self, config: AppConfig):
        self.config = config
        self._knowledge_dir = Path(__file__).parent.parent / "knowledge"

    def _identify_test_type(self, filepath: str) -> str:
        """Categorise a test file as unit, integration, or e2e based on path."""
        parts = Path(filepath).parts
        basename = Path(filepath).name
        is_test_file = basename.startswith("test_") or basename.endswith("_test.py") or ".test." in basename or ".spec." in basename
        if not is_test_file:
            return "unknown"
        if "integration" in parts:
            return "integration"
        if "e2e" in parts or "end_to_end" in parts:
            return "e2e"
        return "unit"

    def _categorise_test_files(self, file_list: list[str]) -> tuple[int, int, int]:
        """Count unit, integration, and e2e test files."""
        unit = integration = e2e = 0
        for f in file_list:
            tt = self._identify_test_type(f)
            if tt == "unit":
                unit += 1
            elif tt == "integration":
                integration += 1
            elif tt == "e2e":
                e2e += 1
        return unit, integration, e2e

    def _calculate_avg_complexity(self, files: list[dict]) -> float:
        """Calculate average cyclomatic complexity from file metadata."""
        if not files:
            return 0.0
        complexities = [f.get("complexity", 0) for f in files]
        return round(sum(complexities) / len(complexities), 2)

    def _scan_python_complexity(self, filepath: str) -> int:
        """Calculate cyclomatic complexity of a Python file using AST."""
        try:
            with open(filepath) as f:
                tree = ast.parse(f.read())
        except (SyntaxError, OSError):
            return 0

        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        return complexity

    async def analyze_code_quality(self, repo_path: str, branch: str = "main") -> dict:
        """Scan a repository for code quality metrics."""
        repo = Path(repo_path)
        if not repo.exists():
            return {"error": f"Repository not found at {repo_path}"}

        python_files = list(repo.rglob("*.py"))
        total_files = len(python_files)
        complexities = []
        smells = []

        for pf in python_files:
            rel = str(pf.relative_to(repo))
            complexity = self._scan_python_complexity(str(pf))
            complexities.append({"name": rel, "complexity": complexity})

            if complexity > 15:
                smells.append({
                    "file": rel,
                    "line": 0,
                    "smell_type": "high_complexity",
                    "description": f"Cyclomatic complexity of {complexity} exceeds threshold of 15",
                    "severity": "high" if complexity > 25 else "medium",
                })

        avg_complexity = self._calculate_avg_complexity(complexities)

        return {
            "repo": repo_path,
            "branch": branch,
            "total_files": total_files,
            "avg_complexity": avg_complexity,
            "smells": smells[:50],
        }

    async def analyze_test_coverage(self, repo_path: str) -> dict:
        """Analyze test coverage by comparing test files against source files."""
        repo = Path(repo_path)
        if not repo.exists():
            return {"error": f"Repository not found at {repo_path}"}

        source_files = [f for f in repo.rglob("*.py") if "test" not in str(f).lower()]
        test_files = [f for f in repo.rglob("*.py") if "test" in str(f).lower()]

        source_modules = {f.stem for f in source_files}
        tested_modules = set()
        for tf in test_files:
            name = tf.stem.replace("test_", "").replace("_test", "")
            if name in source_modules:
                tested_modules.add(name)

        total = len(source_modules) if source_modules else 1
        coverage_pct = round((len(tested_modules) / total) * 100, 1)

        uncovered = source_modules - tested_modules

        return {
            "repo": repo_path,
            "overall_coverage_pct": coverage_pct,
            "total_modules": len(source_modules),
            "tested_modules": len(tested_modules),
            "uncovered_modules": list(uncovered)[:30],
        }

    async def detect_test_patterns(self, repo_path: str) -> dict:
        """Detect test patterns and anti-patterns in a repository."""
        repo = Path(repo_path)
        if not repo.exists():
            return {"error": f"Repository not found at {repo_path}"}

        all_files = [str(f.relative_to(repo)) for f in repo.rglob("*") if f.is_file()]
        unit, integration, e2e = self._categorise_test_files(all_files)

        total_tests = unit + integration + e2e
        if total_tests == 0:
            return {
                "repo": repo_path,
                "total_tests": 0,
                "patterns": [],
                "anti_patterns": ["No tests found"],
                "recommendations": ["Create a basic test suite to establish quality baseline"],
            }

        patterns = []
        if total_tests > 0:
            patterns.append({"test_type": "unit", "count": unit, "percentage": round(unit / total_tests * 100, 1)})
            patterns.append({"test_type": "integration", "count": integration, "percentage": round(integration / total_tests * 100, 1)})
            patterns.append({"test_type": "e2e", "count": e2e, "percentage": round(e2e / total_tests * 100, 1)})

        anti_patterns = []
        recommendations = []

        if unit < total_tests * 0.4:
            anti_patterns.append("Low unit test ratio — possible Ice Cream Cone pattern")
            recommendations.append("Increase unit test count to establish a solid testing foundation")

        if integration == 0 and total_tests > 5:
            anti_patterns.append("No integration tests found")
            recommendations.append("Add integration tests to verify component interactions")

        return {
            "repo": repo_path,
            "total_tests": total_tests,
            "patterns": patterns,
            "anti_patterns": anti_patterns,
            "recommendations": recommendations,
        }

    async def analyze_flaky_tests(self, github_ref: str, runs: list[dict] | None = None) -> dict:
        """Detect flaky tests from CI run data."""
        if not runs:
            return {
                "repo": github_ref,
                "flaky_tests": [],
                "message": "No CI run data provided. Pass workflow run results for flaky test detection.",
            }

        return {
            "repo": github_ref,
            "flaky_tests": [],
            "total_runs_analyzed": len(runs),
            "message": "Flaky test detection requires multiple run results. Implement with real CI data.",
        }
