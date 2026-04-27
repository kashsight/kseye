```
 ██╗  ██╗███████╗    ███████╗██╗   ██╗███████╗
 ██║ ██╔╝██╔════╝    ██╔════╝╚██╗ ██╔╝██╔════╝
 █████╔╝ ███████╗    █████╗   ╚████╔╝ █████╗
 ██╔═██╗ ╚════██║    ██╔══╝    ╚██╔╝  ██╔══╝
 ██║  ██╗███████║    ███████╗   ██║   ███████╗
 ╚═╝  ╚═╝╚══════╝    ╚══════╝   ╚═╝   ╚══════╝
   AI Research Tool — Multi-Agent Search, Citations, Reports
                a Kashsight project by @kashsight
```

<p align="center">
  <img src="https://img.shields.io/badge/kseye-v1.0.0-00D4AA?style=for-the-badge&logo=terminal&logoColor=white" alt="ks-eye version" />
  <img src="https://img.shields.io/badge/python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/termux-✓-25D366?style=for-the-badge&logo=android&logoColor=white" alt="Termux" />
  <img src="https://img.shields.io/badge/license-MIT-00D4AA?style=for-the-badge" alt="License" />
  <img src="https://img.shields.io/github/stars/kashsight/kseye?style=for-the-badge&color=FFD43B" alt="Stars" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AI-Powered-7C3AED?style=flat-square" />
  <img src="https://img.shields.io/badge/Offline-First-06B6D4?style=flat-square" />
  <img src="https://img.shields.io/badge/Human--in--the--Loop-F59E0B?style=flat-square" />
  <img src="https://img.shields.io/badge/10+AI%20Providers-10B981?style=flat-square" />
  <img src="https://img.shields.io/badge/10%20Source%20Types-6366F1?style=flat-square" />
</p>

---

<p align="center">
  <a href="#see-it-in-action">See It in Action</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#ai-providers">AI Providers</a> •
  <a href="#research-templates">Templates</a> •
  <a href="#cli-reference">CLI</a> •
  <a href="#roadmap">Roadmap</a> •
  <a href="#contributing">Contributing</a>
</p>

---

<p align="center">
  <strong>AI-Human Collaborative Research Assistant</strong>
</p>

<p align="center">
  <em>Step-by-step guided research. AI suggests. You decide. Nothing is fully automated.</em>
</p>

---

## ✨ See It in Action

### Interactive 8-Step Research Workflow

```
$ kseye

╔══════════════════════════════════════════════════════════╗
║                   ks-eye v1.0                            ║
║          AI-Human Collaborative Research                 ║
║                   Assistant                              ║
╚══════════════════════════════════════════════════════════╝
Mode: [green]AI Online[/green]

┌─ Resume? ────────────────────────────────────────────────┐
│ Research Folders:                                        │
│   1. [Step 5] Impact of remote learning on student...    │
│   2. [Step 3] Employee satisfaction in tech industry     │
│   3. [✓] Mental health awareness among college...        │
└──────────────────────────────────────────────────────────┘
Resume (number) or n: 1

✓ Loaded: Impact of remote learning on student performance

═══════════════════════════════════════════════════════════
  Step 5: Data Analysis
═══════════════════════════════════════════════════════════

┌─ 📊 Data Validation Report ──────────────────────────────┐
│ Rows: 247    Columns: 12                                 │
│ Quality Score: 84/100 (Good)                             │
│                                                          │
│ Issues: 1    Warnings: 3    Info: 5                      │
└──────────────────────────────────────────────────────────┘

┌─ Distributions: satisfaction_level ──────────────────────┐
│                                                          │
│   Strongly Agree  ████████████████████  89 (36.0%)      │
│   Agree           ███████████████       67 (27.1%)      │
│   Neutral         ██████████            45 (18.2%)      │
│   Disagree        ██████                28 (11.3%)      │
│   Strongly Disagr ███                   18 (7.3%)       │
└──────────────────────────────────────────────────────────┘

Cross-tabulate? Enter: col1 col2 (or n): satisfaction_level department
┌─ Cross-Tab ──────────────────────────────────────────────┐
│ Chi-Square: 24.56 (p < 0.05)                             │
└──────────────────────────────────────────────────────────┘

[cyan]Running AI analysis...[/cyan]
AI completes analysis in ~15 seconds...
```

### Quick Online Research

```
$ kseye quick "impact of AI on medical diagnostics"

⚡ Quick Online Research
Query: impact of AI on medical diagnostics
Sources: 34 scraped from 10 academic sources
AI Synthesis: Complete...

┌─ 🔬 AI Research Brief ───────────────────────────────────┐
│                                                          │
│ KEY FINDINGS:                                           │
│ • AI achieves 92-97% accuracy in radiology (vs 85%      │
│   human average) across 15 studies                      │
│ • Deep learning reduces diagnostic time by 30-50%       │
│ • Major gaps: interpretability, bias in diverse          │
│   populations, regulatory approval bottlenecks          │
│                                                          │
│ SOURCE QUALITY: A- (34 sources, 28 peer-reviewed)       │
│ GAPS IDENTIFIED: 5 research gaps found                  │
│ RECOMMENDATIONS: 3 actionable next steps                │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Top Sources:                                        │ │
│ │ #  │ Source        │ Year | Type     │ Relevance    │ │
│ │ 1  │ Nature Med    │ 2025 | Journal  │ ★★★★★       │ │
│ │ 2  │ Lancet Digital│ 2025 | Journal  │ ★★★★★       │ │
│ │ 3  │ arXiv         │ 2025 | Preprint │ ★★★★☆       │ │
│ │ 4  │ PubMed        │ 2024 | Clinical │ ★★★★☆       │ │
│ │ 5  │ JAMA          │ 2025 | Journal  │ ★★★★★       │ │
│ └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘

Save report? (y/n): y
✓ Saved to: data/research_history/quick_impact_of_AI_on_medi_20260409.txt
```

### Offline Data Analysis (No AI Required)

```
$ kseye analyze survey_results.csv -c satisfaction -c age_group -x satisfaction department --code feedback

┌─ 📁 Data Overview ───────────────────────────────────────┐
│ Rows: 247    Columns: 12                                 │
│ Columns: response_id, age_group, department,             │
│          satisfaction, workload, feedback, ...           │
└──────────────────────────────────────────────────────────┘

┌─ 📈 Statistics: satisfaction ────────────────────────────┐
│ Mean: 3.72  Median: 4.0  Std: 1.08  Range: 4.0         │
│ Min: 1.0  Max: 5.0  Q1: 3.0  Q3: 5.0                    │
└──────────────────────────────────────────────────────────┘

┌─ 🏷️ Auto-Coding Results ─────────────────────────────────┐
│ Method: Keyword Pattern Matching   Responses coded: 198  │
│ Themes found: 8                                          │
│                                                          │
│   satisfaction: 87 (43.9%)                               │
│     → "really enjoy the flexibility and support"         │
│     → "great work environment overall"                   │
│   workload_concerns: 52 (26.3%)                          │
│     → "too much work with tight deadlines"               │
│     → "overwhelmed during peak periods"                  │
└──────────────────────────────────────────────────────────┘
```

---

## 🧭 Philosophy

> **ks-eye is NOT an automated research tool.** It is a **research assistant** that guides you through each step — AI drafts, **you decide** at every stage.

```
┌─────────────────────────────────────────────────────────────┐
│                    THE HUMAN-IN-THE-LOOP                    │
│                                                             │
│  ┌──────────┐    suggests    ┌──────────┐                  │
│  │          │ ─────────────► │          │                  │
│  │   AI     │                │  HUMAN   │                  │
│  │  DRAFTS  │  ◄─────────── │  DECIDES │                  │
│  │          │   approve/edit │          │                  │
│  └──────────┘                └──────────┘                  │
│                                                             │
│  The AI NEVER makes final decisions without human approval │
└─────────────────────────────────────────────────────────────┘
```

| What the AI Does | What You Do |
|------------------|-------------|
| Asks guiding questions | Define your topic and objectives |
| Drafts a research proposal | Review, edit, approve, or reject |
| Generates a JSON questionnaire | Review questions, add/remove, approve |
| Analyzes pasted data | Collect data offline, paste it in |
| Finds academic sources | Select which sources to include |
| Writes report sections | Approve or edit each section |
| Compiles final report | Choose output format, save |

---

## 🚀 Quick Start

### Installation

```bash
# 1. Install tgpt (AI CLI tool) — optional but recommended
go install github.com/aikooo/tgpt/v2@latest

# 2. Install ks-eye
cd ks_eye
pip install -e .

# Optional: Word document output support
pip install -e ".[docx]"
```

### Run in 3 Seconds

```bash
kseye        # Interactive step-by-step workflow
kseye quick "your research query"   # One-shot AI research
kseye version                       # Show version + status
```

### Offline-First — No AI Required

```bash
kseye validate data.csv      # Data quality check (offline)
kseye analyze data.csv -c col1 -x col1 col2 --code open_col   # Full analysis (offline)
```

---

## 🔥 Features

### 8-Step Guided Research

```
┌───────┬──────────────────────────┬──────────────────────────────────┐
│ Step  │ Action                   │ Human Control                    │
├───────┼──────────────────────────┼──────────────────────────────────┤
│   1   │ Define Topic             │ Provide topic, objectives, scope │
│   2   │ Research Proposal        │ Review → approve/edit/regenerate │
│   3   │ Questionnaire Design     │ Approve JSON → export for survey │
│   4   │ Data Collection          │ Collect offline → paste JSON/CSV │
│   5   │ Data Analysis            │ Review findings → approve/reject │
│   6   │ Literature Review        │ Select sources from AI results   │
│   7   │ Report Writing           │ Approve each section individually│
│   8   │ Export                   │ Choose format → save             │
└───────┴──────────────────────────┴──────────────────────────────────┘
```

### Offline Data Processing (Zero AI Required)

| Feature | Description | Tech |
|---------|-------------|------|
| **CSV/JSON Import** | Auto-detect format, delimiter detection | Pure Python |
| **Data Validation** | 8 quality checks → 0-100 score | Built-in |
| **Frequency Charts** | ASCII bar charts for categorical data | Terminal-native |
| **Diverging Likert** | Positive/negative split with center line | Terminal-native |
| **Cross-Tabulation** | Demographic × question with chi-square | Statistical |
| **Auto-Coding** | 10 pre-built themes + AI enhancement | Pattern matching |
| **Statistical Summary** | Mean, median, std, Q1, Q3, range | Built-in |
| **Trend Lines** | Time series with min/max labels | Terminal-native |

```
┌─ Distribution: age_group ──────────────────────────────────┐
│                                                            │
│   18-24  ████████████████              67 (27.1%)         │
│   25-34  ██████████████████████████   103 (41.7%)         │
│   35-44  █████████                     38 (15.4%)         │
│   45-54  █████                         21 (8.5%)          │
│   55+    ██                            10 (4.0%)          │
│                                                            │
│   N=247    Mode: 25-34    Categories: 5                   │
└────────────────────────────────────────────────────────────┘
```

### Academic Search — 10 Source Types

```
┌──────────────────────────────────────────────────────────┐
│                 SOURCE COVERAGE                         │
├──────────────┬──────────────────────────────────────────┤
│  🎓 Scholar  │ Google Scholar, Semantic Scholar, Core   │
│  📄 Preprints│ arXiv, SSRN                              │
│  🏥 Medical   │ PubMed, PMC                              │
│  📊 Metadata  │ CrossRef, DOAJ, Wikidata                 │
│  🌐 Web       │ General Web search                       │
└──────────────┴──────────────────────────────────────────┘
```

### AI Providers — 10 Supported

| Free (No API Key) | Requires API Key |
|-------------------|------------------|
| 🌤️ **Sky** (default, gpt-4.1-mini) | 💎 DeepSeek |
| 🔍 **Phind** | 🌟 Gemini |
| 🤖 **Ollama** (local, private) | ⚡ Groq |
| 🇰🇷 **Kimi** (long context) | 🔷 OpenAI |
| 🔎 **isou** | |
| 🎲 **Pollinations** | |

### Research Templates

| Template | Agents | Passes | Best For |
|----------|--------|--------|----------|
| `quick` | 5 | 1 | Fast research |
| `standard` | 8 | 2 | **Recommended (default)** |
| `literature_review` | 11 | 2 | Timeline & gap analysis |
| `comparative` | 9 | 2 | Multiple perspectives |
| `news_analysis` | 9 | 2 | Bias & sentiment detection |
| `policy_brief` | 11 | 2 | Counter-arguments |
| `technical_report` | 9 | 3 | Code analysis + statistics |
| `debate` | 11 | 3 | Pro vs. counter with fact-check |
| `meta_analysis` | 11 | 3 | Statistical + knowledge graph |
| `deep_research` | All | 5 | Maximum depth |

### Output Formats

- **JSON** — Full structured data with metadata
- **TXT** — Formatted report with ASCII tables
- **DOCX** — Professional Word document (optional)
- **Markdown** — GitHub-ready format

### Session Management

- **Auto-save** — Every state change persists to `session.json`
- **Resume** — Pick up exactly where you left off
- **Folder-based** — Each topic gets its own directory
- **Human-readable** — Everything saved as `.txt` files

---

## 🏗️ Architecture

```
ks_eye/
├── ks_eye/                          # Main package
│   ├── __init__.py                  # Workflow steps, agents, constants
│   ├── __main__.py                  # python -m ks_eye entry
│   ├── cli.py                       # Click-based CLI interface
│   ├── config.py                    # Settings + session management
│   ├── ui.py                        # Rich console display
│   ├── engines/
│   │   ├── research_assistant.py    # Core 8-step workflow engine
│   │   ├── data_processing.py       # Offline: validation, charts, coding
│   │   ├── quick_research.py        # AI-powered one-shot research
│   │   ├── scholar_search.py        # 10-source academic search
│   │   ├── tgpt_engine.py           # AI provider integration
│   │   ├── agent_engine.py          # Multi-agent orchestration
│   │   ├── output_formatter.py      # Report formatting
│   │   ├── docx_formatter.py        # Word document generation
│   │   └── suggestion_engine.py     # AI next-step suggestions
│   └── agents/
│       └── __init__.py              # Agent type definitions
├── data/
│   ├── config/
│   │   ├── settings.json            # User preferences
│   │   └── agent_providers.json     # AI provider mapping
│   ├── research_history/            # Session folders (auto-created)
│   ├── templates/                   # Research templates
│   └── cache/                       # Cache layer
└── setup.py                         # Package configuration
```

---

## 🔧 Configuration

```jsonc
// data/config/settings.json
{
    "default_provider": "sky",       // AI provider for general queries
    "agent_timeout": 60,             // Seconds before timeout
    "citation_style": "apa",         // apa, mla, chicago, harvard, ieee
    "auto_save_sessions": true       // Auto-save on every state change
}
```

```jsonc
// data/config/agent_providers.json
{
    "web_search":     { "provider": "sky" },
    "academic_search":{ "provider": "gemini" },
    "data_synthesis": { "provider": "deepseek" },
    "literature_review": { "provider": "groq" },
    "statistical_analysis": { "provider": "openai" }
}
```

---

## 📋 CLI Reference

| Command | Description | AI Required |
|---------|-------------|-------------|
| `kseye` | Interactive 8-step research | Optional |
| `kseye quick "query"` | One-shot AI research | ✅ Yes |
| `kseye validate file.csv` | Data quality scoring | ❌ No |
| `kseye analyze file.csv` | Charts, cross-tabs, coding | ❌ No |
| `kseye version` | Show version + status | ❌ No |

---

## 🗺️ Roadmap

See [Features to Add](#-features-to-add) section below for upcoming enhancements.

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Coding standards
- Pull request process
- Bug reporting

---

## 📄 License

Proprietary — KashSight Platform. See [LICENSE.md](LICENSE.md) for terms.

---

## 🔒 Security

See [SECURITY.md](SECURITY.md) for:

- Vulnerability reporting
- Data privacy
- Best practices

---

## 🌐 Website

Visit **[kash-sight.web.app/kseye.html](https://kash-sight.web.app/kseye.html)** for the full project page.

---

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-❤️-red?style=flat-square" />
  <strong>by <a href="https://github.com/kashsight">KashSight</a></strong>
</p>

<p align="center">
  <a href="https://github.com/kashsight/kseye/stargazers">
    <img src="https://img.shields.io/github/stars/kashsight/kseye?style=social" alt="Stars" />
  </a>
  <a href="https://github.com/kashsight/kseye/network/members">
    <img src="https://img.shields.io/github/forks/kashsight/kseye?style=social" alt="Forks" />
  </a>
</p>

---

## 💡 Features to Add — Recommended Roadmap

### 🔴 High Priority

| Feature | Description | Impact |
|---------|-------------|--------|
| **PDF Report Export** | Generate professional PDFs with charts, tables, cover page | Professional output |
| **Real-time Streaming** | Stream AI responses token-by-token instead of waiting for full response | UX improvement |
| **Multi-language Support** | i18n for CLI messages — Spanish, French, Arabic, Urdu | Global reach |
| **Git-backed Sessions** | Auto-commit research sessions to local git for version control | Audit trail |
| **Research Collaboration** | Export/import session for team members to contribute | Team research |

### 🟡 Medium Priority

| Feature | Description | Impact |
|---------|-------------|--------|
| **Bibliography Manager** | Zotero/Mendeley integration — import .bib files, manage citations | Academic workflow |
| **Plagiarism Check** | Cross-reference output against web sources | Quality assurance |
| **Research Timeline** | Visual timeline of research progress with milestones | Project tracking |
| **Data Visualization** | Export charts as PNG/SVG (not just ASCII) | Publication-ready |
| **Template Marketplace** | Community-contributed research templates | Ecosystem growth |
| **Reference Manager** | Track, deduplicate, and format references automatically | Time savings |

### 🟢 Nice to Have

| Feature | Description | Impact |
|---------|-------------|--------|
| **Voice Input** | Speech-to-text for topic definition and responses | Accessibility |
| **Web UI** | Optional Flask/FastAPI web interface | Non-CLI users |
| **API Mode** | REST API for programmatic research | Developer integration |
| **Docker Support** | Pre-built Docker image with all dependencies | Easy deployment |
| **Research Graph** | Knowledge graph visualization of sources and connections | Insight discovery |
| **Auto-summary** | Generate TL;DR of long reports for quick review | Executive output |
| **Sentiment Analysis** | Detect bias and sentiment in collected data | Analytical depth |
| **Export to LaTeX** | Academic paper formatting | Journal submission |
| **Peer Review Sim** | AI plays devil's advocate on research findings | Quality check |
| **Batch Mode** | Process multiple research queries from a file | Automation |

### 📊 Data Presentation Enhancements

| Feature | Description |
|---------|-------------|
| **Rich Tables** | Border-styled tables with color-coded cells |
| **Progress Bars** | Visual progress for research steps |
| **Sparklines** | Inline mini-charts in text output |
| **Heat Maps** | Cross-tabulation with color intensity |
| **Tree Views** | Hierarchical data display |
| **Diff View** | Side-by-side comparison of proposal revisions |
| **Gantt Chart** | Research timeline visualization |

---

*Ready to push to GitHub? Run the commands in the next message.*
