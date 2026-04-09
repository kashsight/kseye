<h1 align="center">ks-eye v3</h1>

<p align="center">
  <strong>AI-Human Collaborative Research Assistant</strong>
</p>

<p align="center">
  <strong>Step-by-step guided research. AI suggests. You decide. Nothing is fully automated.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="Python 3.7+" /></a>
  <a href="https://github.com/kashsightplatform/ks_eye"><img src="https://img.shields.io/badge/version-3.0.0-cyan.svg" alt="Version 3.0.0" /></a>
  <a href="https://termux.dev/"><img src="https://img.shields.io/badge/Termux-✓-green.svg" alt="Termux Compatible" /></a>
</p>

---

## 🧭 Philosophy

ks-eye v3 is **NOT** an automated research tool. It is a **research assistant** that guides you through each step of the research process. At every stage, the AI drafts content and **waits for your review and approval** before moving forward.

| What the AI Does | What You Do |
|-----------------|-------------|
| Asks guiding questions | Define your topic and objectives |
| Drafts a research proposal | Review, edit, approve, or reject |
| Generates a JSON questionnaire | Review questions, add/remove, approve |
| Analyzes pasted data | Collect data offline, paste it in |
| Finds academic sources | Select which sources to include |
| Writes report sections | Approve or edit each section |
| Compiles final report | Choose output format, save |

---

## 🚀 Features

### 8-Step Guided Workflow

1. **Define Topic** — AI asks about your research topic, objectives, and scope
2. **Research Proposal** — AI drafts a complete proposal for your review
3. **Questionnaire Design** — JSON questionnaire with multiple question types
4. **Data Collection** — You collect data offline, paste it in
5. **Data Analysis** — AI analyzes your data for patterns and insights
6. **Literature Review** — Academic search across 10 source types
7. **Report Writing** — AI writes sections, you approve each one
8. **Export** — JSON, TXT, or DOCX output

### Parallel Multi-Agent Research

| Feature | Description |
|---------|-------------|
| **Auto-Scaling** | Automatically selects appropriate agents based on query complexity |
| **Recursive Passes** | 1-5 research passes — each pass deepens analysis |
| **Branching Trees** | Auto-splits queries into sub-queries for comprehensive coverage |
| **Memory Sharing** | Agents share context from previous passes |
| **Parallel Execution** | All agents run simultaneously via ThreadPoolExecutor |
| **Caching** | Results cached to avoid duplicate searches |
| **Streaming** | Real-time progress updates during research |

### Academic Search

Searches **10 source types** simultaneously:
- Google Scholar
- ArXiv
- PubMed
- SSRN
- Semantic Scholar
- Core.ac.uk
- CrossRef
- DOAJ
- Wikidata
- General Web

### AI Providers (10 Supported)

| Free (No API Key) | Requires API Key |
|-------------------|-----------------|
| 🌤️ **Sky** (default, gpt-4.1-mini) | 💎 DeepSeek |
| 🔍 **Phind** | 🌟 Gemini |
| 🤖 **Ollama** (local, private) | ⚡ Groq |
| 🇰🇷 **Kimi** (long context) | 🔷 OpenAI |
| 🔎 **isou** | |
| 🎲 **Pollinations** | |

### Research Templates

Pre-built templates loaded from `data/config/research_templates.json`:

| Template | Agents | Passes | Use Case |
|----------|--------|--------|----------|
| `literature_review` | 11 | 2 | Timeline and gap analysis |
| `debate` | 11 | 3 | Pro vs. counter with fact-checking |
| `meta_analysis` | 11 | 3 | Statistical analysis + knowledge graph |
| `policy_brief` | 11 | 2 | News sentiment and counter-arguments |
| `deep_research` | All | 5 | Maximum depth research |
| `quick` | 5 | 1 | Fast research |
| `standard` | 8 | 2 | Recommended (default) |
| `comparative` | 9 | 2 | Compare multiple perspectives |
| `news_analysis` | 9 | 2 | Bias and sentiment detection |
| `technical_report` | 9 | 3 | Code analysis + statistics |

### Output Formats

- **JSON** — Full structured research data
- **TXT** — Formatted report with citations
- **DOCX** — Professional Word document (optional `python-docx` dependency)
- **Markdown** — GitHub-ready format

### Additional Features

- **Session History** — All research sessions saved locally
- **Resume Past Research** — Browse and resume previous sessions
- **Citation Management** — APA, MLA, Chicago, Harvard, IEEE
- **Suggestion Engine** — AI suggests next steps during research
- **Interactive Mode** — Step-by-step CLI guidance
- **Batch Processing** — Process multiple queries from a file

---

## 📦 Quick Start

### Prerequisites

```bash
# Install tgpt (AI CLI tool)
go install github.com/aikooo/tgpt/v2@latest
```

### Install

```bash
cd ks_eye
pip install -e .

# Optional: Word document output
pip install -e ".[docx]"
```

### Run

```bash
kseye        # Launches interactive step-by-step workflow
```

That's it. The tool guides you through everything.

---

## 📋 CLI Commands

```bash
kseye                    # Interactive 8-step research workflow
kseye version            # Show version info
```

---

## 📁 Project Structure

```
ks_eye/
├── ks_eye/
│   ├── cli.py                    # Interactive step-by-step CLI
│   ├── config.py                 # Settings + session management
│   ├── ui.py                     # Display components
│   ├── engines/
│   │   ├── research_assistant.py # Core 8-step workflow engine
│   │   ├── agent_engine.py       # Parallel multi-agent orchestration
│   │   ├── tgpt_engine.py        # AI provider integration
│   │   ├── scholar_search.py     # Academic source search (10 types)
│   │   ├── output_formatter.py   # Report formatting
│   │   ├── docx_formatter.py     # Word document output
│   │   └── suggestion_engine.py  # AI suggestion engine
│   └── agents/                   # Agent type definitions
├── data/
│   ├── config/
│   │   ├── settings.json         # User settings
│   │   ├── research_templates.json # Research templates
│   │   └── agent_providers.json  # AI provider configs
│   └── research_history/         # Past sessions and reports
└── docs/                         # Documentation
```

---

## 🔧 Configuration

Edit `data/config/settings.json`:

```json
{
    "default_provider": "sky",
    "max_sources_per_query": 20,
    "max_recursive_passes": 5,
    "max_branch_depth": 3,
    "max_branches_per_level": 5,
    "cache_enabled": true,
    "streaming": true,
    "citation_style": "apa",
    "output_dir": "./data/research_history"
}
```

---

## 🌐 Website

Visit **[kash-sight.web.app](https://kash-sight.web.app/kseye.html)** for the full project page.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Submit a pull request

---

## 📄 License

Proprietary — KashSight Platform

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/kashsightplatform">KashSight</a>
</p>
