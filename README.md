# Quality Transformation Coach MCP Server

Een MCP-server die als assistent dient voor software quality transformation — bedoeld voor zowel de quality transformation coach (overzicht, advisering, maturity assessments) als het development/test team (hands-on kwaliteitsanalyse, testondersteuning, CI/CD-inzichten).

## Functionaliteiten

De server biedt 14 tools verdeeld over 4 categorieën:

### Code Analyse
| Tool | Beschrijving |
|---|---|
| `analyze_code_quality` | Scan een repo voor code kwaliteits-metrieken (complexity, duplication, smells) |
| `analyze_test_coverage` | Analyseer test coverage en identificeer gaps |
| `detect_test_patterns` | Herken test patterns (unit/integration/e2e) en anti-patterns |
| `analyze_flaky_tests` | Detecteer flaky tests op basis van CI-logs |

### Issue & Defect Analyse
| Tool | Beschrijving |
|---|---|
| `defect_trend_analysis` | Analyseer issue-trends (aanwas, resolutietijd, severity) |
| `quality_hotspot_detection` | Identificeer modules met hoogste defect-dichtheid |
| `root_cause_categories` | Categoriseer bugs per oorzaak (code, design, requirements, security) |

### CI/CD
| Tool | Beschrijving |
|---|---|
| `pipeline_health` | Analyseer CI/CD pipeline gezondheid (success rate, doorlooptijd) |
| `test_result_summary` | Agregeer test results vanuit CI runs |
| `quality_gate_check` | Controleer of kwaliteits gates behaald zijn |

### Kennis & Maturity
| Tool | Beschrijving |
|---|---|
| `maturity_assessment` | Voer een TMMi/ISO 25010 maturity scan uit |
| `quality_recommendations` | Geef context-gevoelige verbeteradviezen |
| `framework_lookup` | Raadpleeg kennisbank voor kwaliteitsmodellen |
| `generate_quality_report` | Genereer een compleet kwaliteitsrapport in Markdown |

## Installatie

### Vereisten
- Python 3.11+
- GitHub Personal Access Token (voor issue/PR data)

### Lokale installatie

```bash
git clone git@github.com:Cerios-TechLab/quality-transformation-coach-assistent.git
cd quality-transformation-coach-assistent
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Configuratie

Kopieer `config.example.yaml` naar `config.yaml` en pas aan:

```yaml
github:
  token_env: GITHUB_TOKEN
  default_org: "Cerios-TechLab"

cicd:
  provider: github_actions

coverage:
  source: local
  format: cobertura

projects:
  - name: "cerios-clinic"
    repo: "/srv/cerios-clinic"
    github: "Steavy/cerios-clinic"
```

### OpenCode integratie

Voeg toe aan `~/.config/opencode/opencode.json` onder `mcp`:

```jsonc
"quality-coach": {
  "type": "local",
  "command": [
    "/opt/quality-coach-mcp/.venv/bin/python",
    "-m",
    "quality_coach_mcp.server"
  ],
  "cwd": "/opt/quality-coach-mcp",
  "enabled": true
}
```

Herstart OpenCode na wijzigingen:
```bash
systemctl restart opencode-serve-4096
```

## Gebruik

### Via OpenCode chat

De tools zijn beschikbaar als MCP-tools in elke OpenCode-sessie. Voorbeelden:

- "Wat is de test coverage van `/srv/cerios-clinic`?"
- "Geef een maturity assessment voor project X met scores `{'test_planning': 3, 'test_design': 2}`"
- "Genereer een quality report voor gateway met een periode van 30 dagen"
- "Wat zegt ISO 25010 over Maintainability?"
- "Check de quality gate pull_request voor Steavy/cerios-clinic"

### Directe Python API

```python
from quality_coach_mcp.tools.code_analysis import CodeAnalysisTools
from quality_coach_mcp.config import load_config

config = load_config()
tools = CodeAnalysisTools(config)

import asyncio
result = asyncio.run(tools.analyze_code_quality("/srv/cerios-clinic"))
print(result)
```

## Kennisbank

De server bevat een embedded kennisbank met:

- **ISO 25010** — 8 kwaliteitskenmerken met sub-characteristics
- **TMMi** — 5 maturity levels met assessment areas
- **Test Patterns** — Herkenbare patronen en anti-patterns
- **Quality Gates** — Standaard criteria voor PR, release, sprint
- **Recommendations** — Context-gevoelige verbeteradviezen

Kennisbank-bestanden staan in `src/quality_coach_mcp/knowledge/` als YAML.

## Development

### Tests draaien

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

### Projectstructuur

```
src/quality_coach_mcp/
├── server.py              # FastMCP server entry point (14 tools)
├── config.py              # Config loading
├── models/types.py        # Pydantic data models
├── tools/
│   ├── code_analysis.py   # Code kwaliteitsanalyse
│   ├── issue_analysis.py  # Issue & defect analyse
│   ├── cicd_tools.py      # CI/CD pipeline tools
│   └── knowledge_tools.py # Kennis & maturity tools
├── adapters/
│   ├── github_adapter.py  # GitHub API wrapper
│   └── cicd_adapter.py    # CI/CD resultaten parser
└── knowledge/
    ├── iso25010.yaml
    ├── tmmi.yaml
    ├── test_patterns.yaml
    ├── quality_gates.yaml
    └── recommendations.yaml
```

## Licentie

Onderdeel van [Cerios TechLab](https://github.com/Cerios-TechLab).
