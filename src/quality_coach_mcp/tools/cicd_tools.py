"""CI/CD quality tools."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from quality_coach_mcp.config import AppConfig


class CICTools:
    """Tools for CI/CD pipeline health and quality gate checking."""

    def __init__(self, config: AppConfig):
        self.config = config
        self._knowledge_dir = Path(__file__).parent.parent / "knowledge"

    def _load_quality_gates(self) -> list[dict]:
        """Load quality gate definitions from knowledge base."""
        gates_path = self._knowledge_dir / "quality_gates.yaml"
        if not gates_path.exists():
            return []
        with open(gates_path) as f:
            data = yaml.safe_load(f)
        return data.get("gates", [])

    def _evaluate_gate(self, criteria: list[dict], metrics: dict) -> list[dict]:
        """Evaluate quality gate criteria against provided metrics."""
        results = []
        for criterion in criteria:
            metric_name = criterion.get("metric")
            threshold = criterion.get("threshold")
            value = metrics.get(metric_name)

            if value is None and criterion.get("required"):
                passed = False
            elif threshold is not None and value is not None:
                passed = value >= threshold
            else:
                passed = True

            results.append({
                "name": criterion["name"],
                "required": criterion.get("required", False),
                "passed": passed,
                "threshold": threshold,
                "actual": value,
            })
        return results

    async def pipeline_health(self, github_ref: str, days: int = 30) -> dict:
        """Get pipeline health metrics."""
        from quality_coach_mcp.adapters.cicd_adapter import CICDAdapter

        adapter = CICDAdapter(self.config)
        result = await adapter.get_pipeline_health(github_ref)
        return result.model_dump()

    async def test_result_summary(self, github_ref: str, run_id: int) -> dict:
        """Get test result summary for a specific workflow run."""
        from quality_coach_mcp.adapters.cicd_adapter import CICDAdapter

        adapter = CICDAdapter(self.config)
        result = await adapter.get_test_results(github_ref, run_id)
        return result.model_dump()

    async def quality_gate_check(
        self, github_ref: str, gate_id: str = "pull_request", metrics: dict | None = None
    ) -> dict:
        """Check if quality gates are met."""
        gates = self._load_quality_gates()
        gate = next((g for g in gates if g["id"] == gate_id), None)

        if not gate:
            return {"error": f"Quality gate '{gate_id}' not found", "available": [g["id"] for g in gates]}

        criteria = gate.get("criteria", [])
        if metrics is None:
            metrics = {}

        results = self._evaluate_gate(criteria, metrics)
        all_passed = all(r["passed"] for r in results if r["required"])

        return {
            "gate": gate["name"],
            "description": gate["description"],
            "all_required_passed": all_passed,
            "results": results,
        }
