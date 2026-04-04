<p align="center">
  <img src="assets/shg-logo.svg" alt="SHG Logo" width="120" height="120">
</p>

<h1 align="center">Skills Health Guardian</h1>

<p align="center">
  <strong>Scan → Diagnose → Report → Fix</strong><br>
  The complete environment health toolkit for AI Agent Skills
</p>

<p align="center">
  <a href="#quick-start"><img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-fc3?style=flat-square&logo=opensourceinitiative&logoColor=white" alt="License: MIT"></a>
  <a href="https://github.com/WorkBuddy-AI/skills-health-guardian/releases"><img src="https://img.shields.io/github/v/release/WorkBuddy-AI/skills-health-guardian?style=flat-square&include_prereleases&sort=date" alt="Release"></a>
  <a href="https://github.com/WorkBuddy-AI/skills-health-guardian/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/WorkBuddy-AI/skills-health-guardian/ci.yml?branch=main&style=flat-square" alt="CI"></a>
  <a href="https://github.com/WorkBuddy-AI/skills-health-guardian/actions"><img src="https://img.shields.io/github/tests/WorkBuddy-AI/skills-health-guardian?style=flat-square" alt="Tests"></a>
  <a href="#coverage"><img src="https://img.shields.io/codecov/c/github/WorkBuddy-AI/skills-health-guardian?style=flat-square" alt="Coverage"></a>
  <a href="https://github.com/WorkBuddy-AI/skills-health-guardian/stargazers"><img src="https://img.shields.io/github/stars/WorkBuddy-AI/skills-health-guardian?style=flat-square&color=%23fbbf24" alt="Stars"></a>
</p>

---

## Elevator Pitch

Managing dozens of AI Agent Skills with different runtime requirements, Python versions, API keys, and hidden dependencies is a nightmare. **Skills Health Guardian (SHG)** is a zero-dependency CLI tool that scans your entire skill inventory, detects conflicts, scores health, generates beautiful reports, and even auto-fixes issues — all in one command.

Think of it as a **health check doctor for your AI agent skill ecosystem**. One scan tells you everything you need to know.

## The Problem

| Pain Point | Impact | SHG Solution |
|---|---|---|
| **Runtime Conflicts** | Skill A needs Python 3.11, Skill B needs 3.13 — which do you install? | Detects version mismatches and suggests isolation plans |
| **Missing Dependencies** | Skills fail silently because `requests` or `numpy` isn't installed | Auto-discovers and lists every missing dependency |
| **Orphaned `.env` Files** | API keys scattered across 50+ directories, none documented | Generates unified `.env` templates from all skills |
| **No Visibility** | "How many skills do we have?" — nobody knows | Scans everything, produces structured inventory |
| **Broken After Updates** | Updated a package, now 3 skills broke silently | Trend tracking shows health changes over time |
| **Onboarding Friction** | New dev spends hours figuring out what each skill needs | One `shg report` gives the full picture |

## Features

- 🔍 **Comprehensive Scanning** — Parses `SKILL.md`, `scripts/`, `package.json`, and more to extract dependencies and runtime requirements
- 📊 **Health Scoring** — 0–100 scoring system with 4 tiers: Healthy / Good / Warning / Critical
- ⚡ **Conflict Detection** — Automatically discovers Python package version conflicts and runtime incompatibilities
- 🔧 **Smart Fix Engine** — One-click install missing dependencies, generate `.env` templates, suggest isolation plans
- 📋 **Multi-format Reports** — Markdown, JSON, or HTML output with dark-themed dashboard visualization
- 🖥️ **Enhanced CLI** — 12 command-line options including format switching, watch mode, color output, and single-skill scanning
- 🐳 **Docker Ready** — 4 runtime profiles: CLI, MCP Server, Web Dashboard, Cron Scheduler
- 🔄 **CI/CD Native** — GitHub Actions pipeline + Makefile for automated quality gates

## Quick Start

### Prerequisites

- Python 3.12 or higher
- No external dependencies required (stdlib only)

### Install

```bash
# Clone the repository
git clone https://github.com/WorkBuddy-AI/skills-health-guardian.git
cd skills-health-guardian

# Run directly (no installation needed)
python scripts/scanner.py --help
```

### Scan Your Skills

```bash
# Full scan of default skills directory
./scripts/health-check.sh

# Or use the scanner directly
python scripts/scanner.py --path ~/.workbuddy/skills

# Generate an HTML dashboard report
python scripts/reporter.py --format html --output shg-report.html
```

### View Results

```bash
# Open the generated report
open shg-report.html          # macOS
xdg-open shg-report.html      # Linux

# Or read the markdown summary
cat shg-report.md
```

That's it. Three steps to full visibility.

## Usage Examples

| Command | Description |
|---|---|
| `python scripts/scanner.py` | Full scan of default skills directory |
| `python scripts/scanner.py --path ./my-skills` | Scan a custom directory |
| `python scripts/scanner.py --skill my-skill-name` | Scan a single skill by name |
| `python scripts/scanner.py --format json` | Output results as JSON |
| `python scripts/scanner.py --no-color` | Disable colored terminal output |
| `python scripts/scanner.py --verbose` | Show detailed dependency info |
| `python scripts/reporter.py --format html` | Generate HTML dashboard report |
| `python scripts/reporter.py --format md` | Generate Markdown summary |
| `python scripts/scripts/fixer.py --auto-fix` | Auto-install missing dependencies |
| `./scripts/health-check.sh` | One-command full health check |
| `watch -n 300 ./scripts/health-check.sh` | Watch mode — scan every 5 minutes |

## Health Score System

Every skill receives a **0–100** health score based on detected issues:

| Score Range | Status | Color | Meaning |
|---|---|---|---|
| **90 – 100** | ✅ Healthy | Green | No issues detected. Ready to run. |
| **70 – 89** | 🟡 Good | Yellow | Minor warnings (optional deps, outdated hints). Functional. |
| **40 – 69** | ⚠️ Warning | Orange | Problems found (missing deps, version conflicts). May fail. |
| **0 – 39** | 🔴 Critical | Red | Broken state. Missing critical dependencies or incompatible runtime. |

### Deduction Rules

| Issue Type | Deduction |
|---|---|
| Missing critical dependency | −15 per item |
| Missing optional dependency | −5 per item |
| Python version mismatch | −20 |
| Runtime not installed (Node, etc.) | −25 |
| Version conflict detected | −10 per conflict pair |
| Missing or invalid `.env` template | −10 |
| Broken script reference | −15 per broken script |

> **Note:** Scores are capped at 0 (floor) and 100 (ceiling). A skill with zero detected issues scores exactly 100.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    SHG Core                         │
│                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │ Scanner  │──▶│  Scorer  │──▶│ Reporter  │        │
│  │          │   │          │   │          │        │
│  │ • Parse  │   │ • Score  │   │ • MD     │        │
│  │ • Extract│   │ • Rank   │   │ • JSON   │        │
│  │ • Index  │   │ • Tier   │   │ • HTML   │        │
│  └────▲─────┘   └──────────┘   └──────────┘        │
│       │                                        ▲    │
│       │         ┌──────────┐                    │    │
│  ┌────┴─────┐   │  Fixer   │────────────────────┘    │
│  │   Disk   │   │          │                         │
│  │ • SKILL  │◀──│ • Install│                         │
│  │ • scripts│   │ • .env   │                         │
│  │ • pkg    │   │ • Isolate│                         │
│  └──────────┘   └──────────┘                          │
│                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │   CLI    │   │   MCP    │   │   Web    │        │
│  │ Terminal │   │ Server   │   │Dashboard │        │
│  └──────────┘   └──────────┘   └──────────┘        │
└─────────────────────────────────────────────────────┘
```

**Four-Layer Pipeline:**

1. **Scanner** (`scripts/scanner.py`) — Discovers and parses all skill files, extracts metadata, dependencies, and runtime requirements
2. **Scorer** (integrated in scanner) — Applies scoring rules, calculates tier classification, identifies conflicts
3. **Fixer** (`scripts/fixer.py`) — Executes remediation actions: installs packages, generates env templates, suggests fixes
4. **Reporter** (`scripts/reporter.py`) — Formats and outputs reports in Markdown, JSON, or HTML (dark-themed dashboard)

## File Structure

```
skills-health-guardian/
├── README.md                    # ← You are here
├── LICENSE                      # MIT License
├── SKILL.md                     # WorkBuddy Skill definition
├── assets/
│   ├── shg-logo.svg            # Project logo (S-shape shield + pulse)
│   ├── landing-page.html       # Dark-themed landing page (~51KB)
│   └── favicon.ico             # Browser favicon
├── scripts/
│   ├── scanner.py              # Core scanning & scoring engine
│   ├── reporter.py             # Report generator (MD/JSON/HTML)
│   ├── fixer.py                # Auto-fix & remediation engine
│   └── health-check.sh         # One-command entry point
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI pipeline (lint/test/build)
│       └── release.yml         # Automated release workflow
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.yml           # 4 service profiles (cli/mcp/web/cron)
├── Makefile                    # Common tasks (scan/report/fix/test)
├── pyproject.toml              # Project metadata (PEP 621)
└── tests/
    ├── test_scanner.py         # Scanner unit tests
    ├── test_scorer.py          # Scoring engine tests
    ├── test_reporter.py        # Report format tests
    └── test_fixer.py           # Fixer integration tests
```

## Screenshots

### Terminal Output (Full Scan)

```
╭──────────────────────────────────────────────────────────╮
│            Skills Health Guardian v1.0.0                 │
│               Environment Health Report                   │
├──────────────────────────────────────────────────────────┤
                                                          │
  📊 Global Health Score:  76.8 / 100                     
  🔍 Skills Scanned:     71                               
  ✅ Healthy:            42 (59%)                          
  ⚠️  Warnings:           19 (27%)                          
  🔴 Critical:           10 (14%)                          
  📦 Dependencies:       289 items found                   
                                                          │
├──────────────────────────────────────────────────────────┤
│  TOP ISSUES FOUND                                       │
│  ─────────────────                                      │
│  1. python 3.13 required but 3.12 installed  [−20 pts]  
│  2. Missing: openai SDK (3 skills affected)              
│  3. Version conflict: requests==2.28 vs ==2.31          
│  4. Missing .env template: anthropic-api-key             
│  5. Node.js >=18 required but not found                  
├──────────────────────────────────────────────────────────┤
│  Run 'fixer.py --auto-fix' for automatic remediation    
╰──────────────────────────────────────────────────────────╯
```

### HTML Dashboard Report

The generated HTML report features:
- **Dark-themed** responsive layout matching the project's Indigo (#6366F1) color system
- **Interactive score cards** for each skill with drill-down details
- **Dependency graph** showing shared and conflicting packages
- **30-day trend chart** tracking health score changes over time
- **Export buttons** for PDF, CSV, and raw JSON

> *Screenshot placeholder — run `python scripts/reporter.py --format html` to generate the live dashboard.*

## Docker Support

SHG ships with 4 pre-configured Docker profiles for different use cases:

```bash
# Profile 1: CLI Mode — one-off scans
docker compose run cli --path /mnt/skills --format json

# Profile 2: MCP Server — expose as Model Context Protocol endpoint
docker compose up mcp    # Available at stdio transport

# Profile 3: Web Dashboard — browser-based UI with scheduled scans
docker compose up web    # Available at http://localhost:8080

# Profile 4: Cron Scheduler — automated periodic scanning
docker compose up cron   # Runs every 6 hours, saves reports to /reports/
```

| Profile | Image Size | Port | Best For |
|---|---|---|---|
| `cli` | ~45MB | None | CI pipelines, one-off audits |
| `mcp` | ~50MB | stdio | Integration with AI agents via MCP protocol |
| `web` | ~85MB | 8080 | Team dashboards, continuous monitoring |
| `cron` | ~48MB | None | Unattended scheduled health checks |

## CI/CD Integration

### GitHub Actions

The included `.github/workflows/ci.yml` pipeline runs on every push and PR:

- **Lint** — Python syntax checking with ruff
- **Test** — Unit test suite with pytest (scanner, scorer, reporter, fixer)
- **Build** — Package validation and metadata checks
- **Report** — Generate a health snapshot as a CI artifact
- **Release** — Automated PyPI publish on tag push (via `release.yml`)

### Makefile Quick Reference

```bash
make scan        # Run a full skills scan
make report      # Generate HTML report
make fix          # Auto-fix detected issues
make test         # Run test suite
make docker-build # Build all Docker images
make clean        # Remove generated artifacts
```

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository and clone your fork
2. **Create a branch**: `git checkout -b feature/your-feature`
3. **Install locally** (no pip needed — stdlib only): `python -m scripts.scanner --help`
4. **Make your changes** and add tests if applicable
5. **Run tests**: `make test` or `pytest tests/`
6. **Commit** with conventional commits: `feat: add npm dependency detection`
7. **Push** and open a Pull Request

### Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) conventions
- Use type hints where possible
- Keep functions under 50 lines
- Write docstrings for public modules
- Maximum complexity: 10 (cyclomatic)

## Roadmap

- [x] v1.0.0 — Core scanner, scorer, reporter, fixer
- [ ] **v1.1.0** — Web dashboard with real-time updates (WebSocket)
- [ ] **v1.2.0** — MCP server with bidirectional sync
- [ ] **v1.3.0** — Skill registry integration (remote health checks)
- [ ] **v2.0.0** — Multi-node distributed scanning

## License

This project is licensed under the terms of the **MIT License**.

```
Copyright (c) 2026 tomansen (https://github.com/tomansen)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

See [LICENSE](./LICENSE) for the full text.

---

<div align="center">

## 🌟 Star This Project

If Skills Health Guardian helps you manage your AI agent skills ecosystem,  
consider giving it a star on GitHub!

<a href="https://github.com/WorkBuddy-AI/skills-health-guardian">
  <img src="https://img.shields.io/github/stars/WorkBuddy-AI/skills-health-guardian?style=social" alt="GitHub Stars">
</a>

**[tomansen](https://github.com/tomansen)** · **[Skills Health Guardian](https://github.com/tomansen/skills-health-guardian)** · **[Report a Bug](https://github.com/tomansen/skills-health-guardian/issues)** · **[Suggest a Feature](https://github.com/tomansen/skills-health-guardian/issues/new)**

*Built with ❤️ for the AI Agent developer community*

</div>
