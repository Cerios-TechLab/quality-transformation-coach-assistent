"""Pydantic data models for the Quality Coach MCP server."""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestType(str, Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    UNKNOWN = "unknown"


# --- Code Analysis Models ---

class CodeSmell(BaseModel):
    file: str
    line: int
    smell_type: str
    description: str
    severity: Severity


class CodeQualityResult(BaseModel):
    repo: str
    branch: str
    total_files: int = 0
    avg_complexity: float = 0.0
    duplication_pct: float = 0.0
    smells: list[CodeSmell] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class CoverageGap(BaseModel):
    file: str
    uncovered_lines: int
    total_lines: int
    coverage_pct: float


class CoverageResult(BaseModel):
    repo: str
    overall_coverage_pct: float = 0.0
    total_lines: int = 0
    covered_lines: int = 0
    gaps: list[CoverageGap] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class TestPatternInfo(BaseModel):
    test_type: TestType
    count: int
    percentage: float


class TestPatternResult(BaseModel):
    repo: str
    total_tests: int = 0
    patterns: list[TestPatternInfo] = Field(default_factory=list)
    anti_patterns: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class FlakyTest(BaseModel):
    name: str
    file: str
    failure_rate: float
    total_runs: int
    failures: int


# --- Issue / Defect Models ---

class DefectTrend(BaseModel):
    period: str
    opened: int
    closed: int
    avg_resolution_days: float = 0.0


class IssueAnalysis(BaseModel):
    repo: str
    total_issues: int = 0
    open_issues: int = 0
    trends: list[DefectTrend] = Field(default_factory=list)
    severity_breakdown: dict[str, int] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class QualityHotspot(BaseModel):
    file: str
    defect_count: int
    complexity: float = 0.0
    risk_score: float = 0.0


# --- CI/CD Models ---

class PipelineRun(BaseModel):
    run_id: int
    status: str
    conclusion: str | None = None
    duration_seconds: float = 0.0
    created_at: datetime | None = None


class CICDResult(BaseModel):
    project: str
    total_runs: int = 0
    success_rate: float = 0.0
    avg_duration_seconds: float = 0.0
    recent_runs: list[PipelineRun] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class TestResultSummary(BaseModel):
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    flaky: int = 0


# --- Knowledge / Maturity Models ---

class MaturityLevel(BaseModel):
    level: int
    name: str
    description: str
    score: float = 0.0
    evidence: list[str] = Field(default_factory=list)


class MaturityScore(BaseModel):
    framework: str
    overall_level: int = 1
    overall_score: float = 0.0
    domains: list[MaturityLevel] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class QualityReport(BaseModel):
    project: str
    period: str
    maturity: MaturityScore | None = None
    coverage: CoverageResult | None = None
    code_quality: CodeQualityResult | None = None
    issues: IssueAnalysis | None = None
    cicd: CICDResult | None = None
    action_items: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)
