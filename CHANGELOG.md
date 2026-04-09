# CHANGELOG

All notable changes to ks-eye will be documented in this file.

---

## [3.0.0] — 2026-04-08

### Complete Redesign — Human-in-the-Loop Research Assistant

**Philosophy Change:** ks-eye v3 is NOT a fully automated research tool. It is a **step-by-step guided assistant** where AI suggests and the human decides at every step. Nothing is fully automated.

### New Workflow (8 Steps)

#### Step 1: Topic Definition
- AI asks guiding questions about the research topic
- Human provides: topic, objectives, target population, scope
- Multi-line input with natural language parsing
- AI confirms understanding before proceeding

#### Step 2: Proposal Generation
- AI drafts a research proposal based on the topic
- Proposal includes: Introduction, Problem Statement, Research Questions, Objectives, Significance, Scope/Limitations, Methodology, Timeline, Expected Outcomes
- **Human reviews and chooses:**
  - `approve` — accept as-is
  - `edit: [changes]` — request specific modifications
  - `regenerate` — start over with a fresh draft
- AI revises based on human feedback
- Loop continues until human approves

#### Step 3: Questionnaire Design
- AI generates a **JSON questionnaire** with:
  - Demographics section
  - 15-25 substantive questions
  - Multiple question types: multiple_choice, likert_scale, yes_no, open_ended, ranking, matrix, demographic
  - Proper JSON structure with sections, questions, options, required flags
- **Human reviews the JSON:**
  - `approve` — accept questionnaire
  - `edit: [changes]` — add/remove/modify questions
  - `regenerate` — try again
- On approval, **exports the JSON** for the human to use offline
- Human uses this JSON to create surveys (Google Forms, SurveyMonkey, paper, etc.)
- Human distributes and collects data **offline** (not automated)

#### Step 4: Data Collection (Human Does This)
- AI provides instructions for offline data collection
- Human creates survey, distributes, collects responses
- Human formats responses as JSON
- Human **pastes the collected JSON data** into ks-eye
- AI validates the JSON and counts responses
- Human can `skip` if no data collection needed

#### Step 5: Data Analysis (AI Analyzes, Human Reviews)
- AI analyzes the pasted JSON data
- Provides: Data Overview, Demographic Analysis, Key Findings per Objective, Statistical Summary, Qualitative Insights, Limitations, Recommendations
- **Human reviews findings:**
  - `approve` — findings are accurate
  - `reanalyze: [direction]` — focus on specific aspects differently
- Loop continues until human approves

#### Step 6: Literature Review (AI Finds, Human Selects)
- AI generates search queries for academic literature
- AI searches across 10 source types (Scholar, Semantic, CrossRef, Wikipedia, arXiv, PubMed, SSRN, News, Patents, Datasets)
- **AI presents found sources with numbers**
- **Human selects which sources to include:**
  - `select: 1,3,5,7` — specific sources
  - `select: all` — all sources
  - `skip` — no literature review
- AI synthesizes only the **human-selected** sources into a literature review
- Human reviews and can request edits

#### Step 7: Report Writing (Section by Section, Human Approves Each)
- AI drafts each report section individually:
  1. Executive Summary
  2. Introduction
  3. Literature Review (from Step 6)
  4. Methodology
  5. Findings and Results
  6. Discussion
  7. Recommendations
  8. Conclusion
  9. References
- **For each section, human reviews and chooses:**
  - `approve` — section is good
  - `edit: [feedback]` — request changes
  - `skip` — exclude this section
- Each section uses context from: proposal, questionnaire, collected data, analysis, literature review
- No section is finalized without human approval

#### Step 8: Final Output
- AI compiles all **human-approved** sections into final report
- Includes: Cover page, Table of Contents, all approved sections, footer
- **Human chooses output format:**
  - `.txt` — formatted text file (default)
  - `.docx` — Word document (requires python-docx)
- Report is saved to `data/research_history/`
- Full session saved as JSON for later resumption

### New Architecture

#### `engines/research_assistant.py` (Core Engine)
- `ResearchAssistant` class — manages entire workflow
- Session state tracking (JSON-serializable)
- Step-by-step methods:
  - `step_topic()` — topic definition with multi-line input
  - `step_proposal()` — draft/approve/edit/regenerate loop
  - `step_questionnaire()` — JSON questionnaire generation with review
  - `step_data_collection()` — receives and validates human-pasted data
  - `step_data_analysis()` — analyzes data, human reviews
  - `step_literature_review()` — AI searches, human selects sources
  - `step_report_writing()` — section-by-section drafting with approval
  - `step_final_output()` — compiles approved sections
- `_extract_json()` — robust JSON extraction from AI responses
- `save_report()` — saves as .txt or .docx
- `export_session()` / `load_session()` — save/resume sessions

#### `cli.py` (Interactive CLI)
- Single interactive mode — `kseye` launches step-by-step workflow
- Each step displays clear header: "Step N: Title"
- Clear prompts at every decision point
- Multi-line input for topic definition
- Proposal display in scrollable panel
- Questionnaire JSON display
- Source selection interface (numbered list)
- Section-by-section report review
- Auto-detects saved sessions on launch
- Resume capability from any step

#### Simplified Config
- Removed: caching, auto-scaling, branching, streaming, complex toggles
- Kept: username, default_provider, agent_timeout, citation_style, session tracking
- Session auto-save to `data/research_history/`

### Removed Features (from v2)
- Fully automated parallel agent execution
- Recursive multi-pass research
- Auto-scaling agents
- Branching research trees
- Batch research from file
- Cache layer
- Streaming output
- 29 agents (reduced to 12 selective agents)
- Knowledge graph, sentiment analysis, bias detection as standalone features
- Peer review simulation
- Fact density scoring
- Source reliability dashboard
- Index generation
- Appendix generation

### Retained Features (from v2, adapted)
- tgpt engine integration
- Multi-source search (10 types)
- Citation management (APA, MLA, Chicago, Harvard, IEEE)
- Word document output (.docx)
- Per-agent provider configuration
- 10 AI providers supported

### New File Structure
```
ks_eye/
├── __init__.py              ← 8 workflow steps, 12 agents, constants
├── __main__.py              ← python -m ks_eye
├── cli.py                   ← Step-by-step interactive CLI
├── config.py                ← Simplified settings, session tracking
├── ui.py                    ← Clean step-by-step display
├── engines/
│   ├── tgpt_engine.py       ← tgpt CLI wrapper
│   ├── scholar_search.py    ← 10 source types (from v2)
│   ├── research_assistant.py ← NEW: step-by-step workflow engine
│   ├── output_formatter.py  ← Kept for .docx support
│   └── docx_formatter.py    ← Word document generation
└── data/
    ├── config/
    │   ├── settings.json
    │   └── agent_providers.json
    ├── research_history/     ← Sessions and reports
    ├── sources/
    └── cache/
```

### Philosophy

**v1:** "Run research automatically"
**v2:** "Run MORE research automatically with more features"
**v3:** "AI assists, human decides — every step of the way"

The human:
- Defines the topic
- Reviews and edits the proposal
- Approves the questionnaire
- Collects data offline
- Pastes data into the tool
- Reviews analysis findings
- Selects which literature sources to include
- Approves each report section individually
- Chooses the final output format

The AI:
- Asks guiding questions
- Drafts documents
- Generates questionnaires
- Analyzes pasted data
- Finds academic sources
- Writes report sections
- Compiles final output

**The AI never makes final decisions without human approval.**

---

## [3.0.1] — 2026-04-08

### Bugfixes

- **Topic parsing** — Now supports both labeled input (`Topic: ...`, `Objectives: ...`) and unlabeled input. Previously only unlabeled worked.
- **tgpt not installed** — Graceful fallback when tgpt is unavailable. Instead of crashing, prompts user to manually enter content or skip the step. Applies to: proposal generation, questionnaire design, literature review, report writing.
- **Workflow continuation** — Added `_continue_to_*` helper functions so that when a step is skipped or done manually, the workflow seamlessly continues to the next step instead of stopping.
- **String syntax** — Fixed unterminated string literal in Panel content (Step 4 data collection instructions).

---

## [3.0.2] — 2026-04-08

### Folder-Based Session System

- **Auto-creates research folder per session** — Each research topic gets its own folder: `data/research_history/YYYYMMDD_HHMMSS_topic_name/`
- **Everything saved as .txt** — proposal.txt, questionnaire.txt, analysis.txt, literature.txt, report.txt — all human-readable
- **Questionnaire dual-format** — questionnaire.txt (readable with numbered questions) AND questionnaire.json (for import into survey tools)
- **Subdirectories** — `data/` for collected data, `sources/` for source lists
- **README.txt** — Auto-generated in each folder explaining the structure
- **Session state** — session.json in folder root for resumption
- **Resume from folder** — On launch, shows existing research folders with topic, current step, date, and report status
- **Resume jumps to correct step** — If you were at Step 5, resumes at Step 5

### Quick Research Additions

- **Template JSON files** — `data/templates/` with `.template.json` files defining research workflows
- **Survey analysis template** — Pre-configured for questionnaire data analysis with scraping, JSON loading, and report generation
- **Online data scraping** — Integrates with Google Scholar, Semantic Scholar, CrossRef, Wikipedia, DuckDuckGo, arXiv, PubMed, SSRN, patents, datasets
- **JSON file path input** — Users can paste path to their collected JSON data file for analysis
- **Template-based workflow** — Each template defines: scraping sources, data input format, analysis options, output sections

### Save Behavior Changes

- **No more "choose filename"** — Everything auto-saves in the session folder
- **Report saved as report.txt** — Directly in the session folder
- **Session JSON auto-saved** — Every state change persists to session.json
- **Each section saved individually** — `sections/executive_summary.txt`, `sections/findings.txt`, etc.
- **Sources saved as list.txt** — In `sources/` subdirectory
- **Collected data saved** — In `data/collected_data.json`

---

## [3.1.0] — 2026-04-08

### Offline-First Architecture

- **Everything works without AI** — All data processing, validation, charts, cross-tabs, and auto-coding run fully offline
- **AI as optional enhancement** — When tgpt is available, AI enhances results. When not, everything still works
- **Quick Online Research mode** — `kseye quick "query"` — Fully AI-powered: scrapes web + academic sources, AI synthesizes everything into a research brief. One-shot research
- **Offline data analysis** — CSV/JSON import, validation, frequency charts, cross-tabulation, auto-coding — all without AI
- **Mode detection** — On launch, shows `[AI Online]` or `[Offline Only]` status

### Data Processing Engine (`engines/data_processing.py`)

#### CSV/Excel Import
- `DataImport.from_csv_string()` — Parse CSV text with auto-delimiter detection (comma, semicolon, tab)
- `DataImport.from_csv_file()` — Import from .csv files
- `DataImport.from_json_string()` — Parse JSON with structure normalization
- `_normalize_json()` — Handles `{"responses": [...]}`, `{"data": [...]}`, list of dicts, single objects
- `_flatten()` — Flattens nested dicts to dot-notation keys for column access

#### Data Validation Engine
- `DataValidator` — 8 quality checks, all offline:
  - Empty dataset detection
  - Missing columns per row
  - Empty cell analysis (flags >50%, >20% thresholds)
  - Duplicate row detection
  - Column completeness (flags <10% populated columns)
  - Constant column detection (no variation)
  - Numeric column identification
  - Response ID uniqueness check
- Quality score 0-100 with rating: Excellent/Good/Fair/Poor
- Detailed report with issues (red), warnings (yellow), info (dim)

#### Cross-Tabulation Engine
- `CrossTabulator.cross_tab(row_col, col_col)` — Full cross-tab with counts, percentages, row/col totals, chi-square statistic
- `auto_cross_tabs(demo_cols, question_cols)` — Generate all demographic × question combinations automatically
- Results include: count table, percentage table, chi-square value, category counts

#### Auto-Coding of Open-Ended Responses
- `AutoCoder` — 10 pre-built theme keyword sets: access_issues, satisfaction, dissatisfaction, cost_concerns, time_management, learning_quality, teacher_support, technical_issues, motivation, social_interaction
- Pattern matching against response text — fully offline
- Produces codebook with: count, percentage, example responses per theme
- Optional AI enhancement when tgpt available — generates theme descriptions and discovers missed themes
- `_ai_enhance_coding()` — AI reads sample responses, describes themes, suggests additions

#### ASCII Chart Visualizations
- `ASCIICharts.bar_chart()` — Horizontal bar chart with configurable width, auto-sorted
- `ASCIICharts.likert_chart()` — Diverging Likert scale chart (negative left, positive right, center line)
- `ASCIICharts.pie_chart()` — Pie chart with legend using different block characters
- `ASCIICharts.trend_line()` — Time series with connecting lines, min/max labels
- `ASCIICharts.frequency_table()` — Formatted table with count, percentage, and ASCII bar

#### Statistical Summary
- `Statistics.describe()` — Count, mean, median, std_dev, min, max, range, Q1, Q3
- `Statistics.frequency_distribution()` — Bin-based frequency distribution for numeric data

### Quick Online Research (`engines/quick_research.py`)

- `quick_online_research(query)` — Full AI-powered research in one shot:
  1. Scrapes 30+ sources from 10 source types (Scholar, Semantic, CrossRef, Wikipedia, arXiv, PubMed, SSRN, News, Patents, Datasets)
  2. AI synthesizes all sources into comprehensive brief
  3. Returns: synthesis, key points, methodology notes, gaps, recommendations, source quality rating
- `format_quick_report(result)` — Formats result as readable .txt report with sources table and AI analysis
- CLI: `kseye quick "your query" -o report.txt`

### CLI Updates

**New Commands:**
- `kseye quick "query"` — Quick online research (AI scrapes everything)
- `kseye validate file.csv` — Validate data quality (offline)
- `kseye analyze file.csv -c col1 -c col2 -x col1 col2 -code open_col --ai-code` — Full analysis suite

**Interactive Menu (7 options):**
1. New Research (step-by-step, offline-first)
2. **Quick Online Research** (AI scrapes everything)
3. **Analyze Data File** (CSV/JSON, offline)
4. **Validate Data File** (offline)
5. Settings
6. (existing options preserved)
7. Exit

**Data Collection Enhancements:**
- Accepts pasted CSV text (not just JSON)
- Accepts file path to .csv or .json
- Auto-detects format and imports
- Shows validation report before analysis
- Shows frequency charts for categorical columns
- Interactive cross-tabulation prompt
- Interactive auto-coding prompt

### File Structure Additions

```
ks_eye/
├── engines/
│   ├── data_processing.py   ← NEW: CSV import, validation, cross-tabs, auto-coding, ASCII charts, statistics
│   └── quick_research.py    ← NEW: AI-powered quick research with scraping
├── data/
│   └── templates/
│       └── survey_analysis.template.json ← NEW: Template definition
```

### Output Additions

- ASCII bar charts in analysis output
- Diverging Likert charts for attitude questions
- Trend lines for numeric data over time
- Frequency tables with percentage bars
- Cross-tabulation tables with chi-square
- Auto-coding theme summaries with examples
- Data validation quality score dashboard

---

*End of changelog.*
