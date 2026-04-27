<p align="center">
  <img src="https://img.shields.io/badge/CHANGELOG-ks--eye-00D4AA?style=for-the-badge" alt="Changelog" />
</p>

<p align="center">
  <strong>All notable changes to ks-eye</strong>
</p>

<p align="center">
  This project adheres to <a href="https://keepachangelog.com/en/1.1.0/">Semantic Versioning</a>.
</p>

---

## 📋 Version Summary

```
┌─────────────┬────────────┬──────────────────────────────────────┐
│   Version   │    Date    │  Summary                             │
├─────────────┼────────────┼──────────────────────────────────────┤
│   1.0.0     │ 2026-04-09 │ Industrial-standard release           │
│   3.1.0     │ 2026-04-08 │ Offline-first + quick research       │
│   3.0.2     │ 2026-04-08 │ Folder-based sessions + templates    │
│   3.0.1     │ 2026-04-08 │ Bug fixes + graceful fallbacks       │
│   3.0.0     │ 2026-04-08 │ Complete redesign — human-in-loop    │
│   < 3.0     │ —          │ Legacy versions (deprecated)         │
└─────────────┴────────────┴──────────────────────────────────────┘
```

---

## [1.0.0] — 2026-04-09

### 🏭 Industrial-Standard Release

- **ASCII Art Banner** — Professional multi-line ks-eye logo in CLI
- **Version Reset** — Clean 1.0.0 for new public release
- **AI Prompts** — Minimum 10,000-word outputs with detailed section structure
- **Prompt Architecture** — Centralized `ai_prompts.py` with comprehensive prompts
- **Extended Timeouts** — 180s for all AI operations (was 60s)
- **Enhanced Quick Research** — 8-section research brief with 1,500-4,000 word sections
- **Professional Markdown** — All .md files redesigned with tables, diagrams, badges
- **See It in Action** — Terminal output examples in README

---

## [3.1.0] — 2026-04-08

### 🎯 Offline-First Architecture

> **Everything works without AI.** All data processing, validation, charts, cross-tabs, and auto-coding run fully offline. AI is optional enhancement.

#### Data Processing Engine (`engines/data_processing.py`)

**CSV/JSON Import**
| Method | Description |
|--------|-------------|
| `DataImport.from_csv_string()` | Parse CSV text with auto-delimiter detection (comma, semicolon, tab) |
| `DataImport.from_csv_file()` | Import from `.csv` files |
| `DataImport.from_json_string()` | Parse JSON with structure normalization |
| `_normalize_json()` | Handles `{"responses": [...]}`, `{"data": [...]}`, list of dicts, single objects |
| `_flatten()` | Flattens nested dicts to dot-notation keys for column access |

**Data Validation Engine** — `DataValidator` (8 checks, all offline)

```
Quality Score: 0-100
├── Excellent (90-100) ✓
├── Good      (70-89)  ~
├── Fair      (50-69)  !
└── Poor      (0-49)   ✗

Checks:
├── Empty dataset detection
├── Missing columns per row
├── Empty cell analysis (>50%, >20% thresholds)
├── Duplicate row detection
├── Column completeness (<10% populated)
├── Constant column detection
├── Numeric column identification
└── Response ID uniqueness
```

**Cross-Tabulation Engine**
- `CrossTabulator.cross_tab(row_col, col_col)` — Full cross-tab with counts, percentages, row/col totals, chi-square statistic
- `auto_cross_tabs(demo_cols, question_cols)` — Generate all demographic × question combinations automatically

**Auto-Coding of Open-Ended Responses** — `AutoCoder`
- 10 pre-built theme keyword sets: `access_issues`, `satisfaction`, `dissatisfaction`, `cost_concerns`, `time_management`, `learning_quality`, `teacher_support`, `technical_issues`, `motivation`, `social_interaction`
- Pattern matching against response text — fully offline
- Optional AI enhancement when `tgpt` available

**ASCII Chart Visualizations** — `ASCIICharts`
| Chart Type | Use Case |
|------------|----------|
| `bar_chart()` | Horizontal bar chart with configurable width |
| `likert_chart()` | Diverging Likert scale (negative ← → positive) |
| `pie_chart()` | Pie chart with legend using block characters |
| `trend_line()` | Time series with connecting lines, min/max labels |
| `frequency_table()` | Count, percentage, and ASCII bar |

**Statistical Summary** — `Statistics`
- `describe()` — Count, mean, median, std_dev, min, max, range, Q1, Q3
- `frequency_distribution()` — Bin-based frequency for numeric data

#### Quick Online Research (`engines/quick_research.py`)

```
kseye quick "your query"
├── Scrapes 30+ sources from 10 source types
├── AI synthesizes all sources into brief
├── Returns: synthesis, key points, gaps, recommendations
└── CLI: kseye quick "query" -o report.txt
```

#### CLI Updates

**New Commands:**
| Command | Description | AI |
|---------|-------------|-----|
| `kseye quick "query"` | Quick online research | ✅ Required |
| `kseye validate file.csv` | Validate data quality | ❌ Offline |
| `kseye analyze file.csv -c col1 -c col2 -x col1 col2 -code open_col --ai-code` | Full analysis | Optional |

**Interactive Menu (7 options):**
```
┌─ ks-eye v1.0 Main Menu ──────────────────────────────────┐
│  1.   New Research (step-by-step, offline-first)         │
│  2.   Quick Online Research (AI scrapes everything)      │
│  3.   Analyze Data File (CSV/JSON, offline)              │
│  4.   Validate Data File (offline)                       │
│  5.   Settings                                           │
│  0.   Exit                                              │
└──────────────────────────────────────────────────────────┘
```

#### File Structure Additions

```
ks_eye/
├── engines/
│   ├── data_processing.py         ← NEW: CSV import, validation, cross-tabs, auto-coding, charts
│   └── quick_research.py          ← NEW: AI-powered quick research with scraping
├── data/
│   └── templates/
│       └── survey_analysis.template.json  ← NEW: Template definition
```

---

## [3.0.2] — 2026-04-08

### 📁 Folder-Based Session System

| Feature | Description |
|---------|-------------|
| **Auto-creates research folder** | `data/research_history/YYYYMMDD_HHMMSS_topic_name/` |
| **Everything saved as .txt** | `proposal.txt`, `questionnaire.txt`, `analysis.txt`, `literature.txt`, `report.txt` |
| **Questionnaire dual-format** | `.txt` (readable) + `.json` (for survey tools) |
| **Subdirectories** | `data/` for collected data, `sources/` for source lists |
| **README.txt** | Auto-generated in each folder explaining structure |
| **Session state** | `session.json` in folder root for resumption |
| **Resume from folder** | Shows existing research folders with topic, step, date, report status |
| **Resume jumps to correct step** | If you were at Step 5, resumes at Step 5 |

### Quick Research Additions

- **Template JSON files** — `data/templates/` with `.template.json` files
- **Survey analysis template** — Pre-configured for questionnaire data analysis
- **Online data scraping** — Google Scholar, Semantic Scholar, CrossRef, Wikipedia, DuckDuckGo, arXiv, PubMed, SSRN, patents, datasets
- **JSON file path input** — Users can paste path to their collected JSON data file
- **Template-based workflow** — Each template defines: scraping sources, data input format, analysis options, output sections

### Save Behavior Changes

```
Before: User chooses filename → saves to single location
After:  Auto-saves in session folder

Session Folder Structure:
├── session.json                 # State for resumption
├── proposal.txt
├── questionnaire.txt
├── questionnaire.json
├── analysis.txt
├── literature.txt
├── report.txt
├── sections/
│   ├── executive_summary.txt
│   ├── findings.txt
│   └── ...
├── sources/
│   └── list.txt
├── data/
│   └── collected_data.json
└── README.txt
```

---

## [3.0.1] — 2026-04-08

### 🐛 Bugfixes

| Issue | Fix |
|-------|-----|
| **Topic parsing** | Supports both labeled (`Topic: ...`, `Objectives: ...`) and unlabeled input |
| **tgpt not installed** | Graceful fallback — prompts user to manually enter content or skip |
| **Workflow continuation** | Added `_continue_to_*` helpers so skipped steps continue seamlessly |
| **String syntax** | Fixed unterminated string literal in Panel content (Step 4) |

---

## [3.0.0] — 2026-04-08

### 🔄 Complete Redesign — Human-in-the-Loop Research Assistant

> **Philosophy Change:** ks-eye v1 is NOT a fully automated research tool. It is a **step-by-step guided assistant** where AI suggests and the human decides at every step. Nothing is fully automated.

### 8-Step Workflow

```
┌──────┬──────────────────────┬─────────────────────────────┬──────────┐
│ Step │ Phase                │ AI Action                   │ Human    │
├──────┼──────────────────────┼─────────────────────────────┼──────────┤
│  1   │ Topic Definition     │ Asks guiding questions      │ Provides │
│  2   │ Proposal Generation  │ Drafts proposal             │ Reviews  │
│  3   │ Questionnaire Design │ Generates JSON              │ Approves │
│  4   │ Data Collection      │ Provides instructions       │ Collects │
│  5   │ Data Analysis        │ Analyzes pasted data        │ Reviews  │
│  6   │ Literature Review    │ Searches 10 source types    │ Selects  │
│  7   │ Report Writing       │ Drafts each section         │ Approves │
│  8   │ Final Output         │ Compiles report             │ Chooses  │
└──────┴──────────────────────┴─────────────────────────────┴──────────┘
```

### New Architecture

| File | Purpose |
|------|---------|
| `engines/research_assistant.py` | Core engine: `ResearchAssistant` class, session state, step-by-step methods |
| `cli.py` | Interactive CLI with resume capability |
| `config.py` | Simplified settings, session tracking |
| `ui.py` | Clean step-by-step display |
| `engines/tgpt_engine.py` | tgpt CLI wrapper |
| `engines/scholar_search.py` | 10 source types |
| `engines/output_formatter.py` | .docx support |
| `engines/docx_formatter.py` | Word document generation |

### Removed Features (from v2)

<details>
<summary>Click to expand</summary>

- Fully automated parallel agent execution
- Recursive multi-pass research
- Auto-scaling agents
- Branching research trees
- Batch research from file
- Cache layer
- Streaming output
- 29 agents (reduced to 12 selective agents)
- Knowledge graph, sentiment analysis, bias detection
- Peer review simulation
- Fact density scoring
- Source reliability dashboard
- Index generation
- Appendix generation

</details>

### Retained Features

<details>
<summary>Click to expand</summary>

- tgpt engine integration
- Multi-source search (10 types)
- Citation management (APA, MLA, Chicago, Harvard, IEEE)
- Word document output (.docx)
- Per-agent provider configuration
- 10 AI providers supported

</details>

### Philosophy Evolution

```
v1: "Run research automatically"
v2: "Run MORE research automatically with more features"
v1: "AI assists, human decides — every step of the way"
```

---

## 📝 Legend

| Badge | Meaning |
|-------|---------|
| `✨` | New feature |
| `🐛` | Bug fix |
| `🔧` | Configuration change |
| `📁` | File structure change |
| `⚡` | Performance improvement |
| `🗑️` | Removed feature |
| `♻️` | Refactored |

---

<p align="center">
  <a href="https://github.com/kashsight/kseye/releases">View Releases</a> •
  <a href="https://github.com/kashsight/kseye">Back to README</a>
</p>
