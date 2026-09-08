# Demo Reports

Voorbeeld-rapporten gegenereerd door de Quality Transformation Coach MCP Server.

## Bestanden

| Bestand | Beschrijving |
|---|---|
| `cerios-clinic-quality-report.md` | Maturity Assessment Level 2 (Managed), 68.5% coverage, 82% CI/CD |
| `gateway-quality-report.md` | Maturity Assessment Level 2 (Managed), 42% coverage, 95% CI/CD |

## Hoe genereren

Deze rapporten zijn gegenereerd met de `generate_quality_report` tool:

```python
from quality_coach_mcp.tools.knowledge_tools import KnowledgeTools
from quality_coach_mcp.config import load_config

config = load_config()
kt = KnowledgeTools(config)

report = await kt.generate_quality_report(
    project='Cerios Clinic',
    period='last-30-days',
    maturity_scores={'test_planning': 2, 'test_design': 3, 'test_execution': 2},
    coverage_pct=68.5,
    cicd_success_rate=82.0,
)
```

## Via OpenCode chat

De rapporten zijn ook direct op te vragen via een OpenCode-sessie:

- "Genereer een quality report voor Cerios Clinic met scores test_planning=2, test_design=3, test_execution=2"
- "Geef een maturity assessment voor project X"
