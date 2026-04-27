<p align="center">
  <img src="https://img.shields.io/badge/CONTRIBUTING-join%20us-00D4AA?style=for-the-badge" alt="Contributing" />
</p>

<p align="center">
  <strong>How to contribute to ks-eye</strong>
</p>

---

## 🧭 Philosophy

> ks-eye is built on one principle: **AI suggests, human decides.**

Every feature you contribute to should align with this core philosophy:
- ✋ **Human-in-the-loop** — No fully automated decisions without human approval
- 📴 **Offline-first** — Core functionality must work without AI
- 🪜 **Step-by-step** — Guided workflows, not black boxes

---

## 📋 Quick Navigation

- [🚀 Getting Started](#-getting-started)
- [🛠️ Development Setup](#️-development-setup)
- [📐 Coding Standards](#-coding-standards)
- [✅ Testing](#-testing)
- [🔀 Submitting a PR](#-submitting-a-pull-request)
- [🐛 Reporting Bugs](#-reporting-bugs)
- [💡 Feature Requests](#-feature-requests)
- [📄 License](#-license)

---

## 🚀 Getting Started

### 1. Fork & Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/kseye.git
cd kseye

# Add upstream
git remote add upstream https://github.com/kashsight/kseye.git
```

### 2. Install Dependencies

```bash
pip install -e .

# Optional: AI features
go install github.com/aikooo/tgpt/v2@latest

# Optional: Word output
pip install -e ".[docx]"
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

---

## 🛠️ Development Setup

### Project Structure

```
ks_eye/
├── ks_eye/                          # Main package
│   ├── cli.py                       # ← CLI interface (Click)
│   ├── config.py                    # ← Configuration management
│   ├── ui.py                        # ← Rich console display
│   ├── engines/                     # ← Core engines
│   │   ├── research_assistant.py    #    8-step workflow
│   │   ├── data_processing.py       #    Offline data tools
│   │   ├── quick_research.py        #    One-shot AI research
│   │   └── scholar_search.py        #    Academic search
│   └── agents/                      # ← Agent definitions
├── data/                            # Runtime data (gitignored)
└── setup.py                         # Package config
```

### Key Files to Know

| File | Modify When |
|------|-------------|
| `cli.py` | Adding CLI commands, interactive menu |
| `config.py` | Changing settings, session management |
| `ui.py` | Updating display, colors, panels |
| `engines/research_assistant.py` | Workflow logic, step methods |
| `engines/data_processing.py` | Data import, validation, charts |
| `engines/quick_research.py` | Quick research, scraping |
| `engines/scholar_search.py` | Academic source search |

---

## 📐 Coding Standards

### Python Style

```python
# ✅ DO: Type hints, double quotes, max 100 chars
def calculate_quality_score(
    data: list[dict],
    columns: list[str],
) -> dict:
    """Calculate data quality score from 0-100."""
    score = 100
    # ... implementation
    return {"score": score, "rating": "Good"}

# ❌ DON'T: No type hints, single quotes, long lines
def calc(data,cols):
    s=100
    # ... implementation that goes way beyond 100 characters and is hard to read
```

### Conventions

| Rule | Example |
|------|---------|
| **Double quotes** | `"hello"`, not `'hello'` |
| **Type hints** | `def foo(x: int) -> str:` |
| **Docstrings** | `"""One-line description."""` |
| **Max line length** | 100 characters |
| **Naming** | `snake_case` for functions, `PascalCase` for classes |
| **Constants** | `MAX_SOURCES = 20` |
| **Imports** | stdlib → third-party → local (alphabetical within groups) |

### User-Facing Messages

```python
# ✅ Use Rich console for all user messages
from ks_eye.ui import show_success, show_error, show_warning, show_info, console
from rich.panel import Panel

show_success("Data validated successfully")
console.print(Panel("Content here", title="Title", border_style="cyan"))

# ❌ Don't use print()
print("Data validated successfully")
```

### Error Handling

```python
# ✅ Graceful degradation when AI unavailable
if not check_tgpt_installed():
    show_warning("AI unavailable — entering manual mode")
    return _handle_manual_entry()

# ❌ Don't crash
result = run_ai_query()  # Raises if tgpt not installed
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

Longer description if needed.

Closes #123
```

| Type | When to Use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style (formatting, no logic change) |
| `refactor` | Code restructuring (no feature change) |
| `test` | Adding/updating tests |
| `chore` | Maintenance tasks |

**Examples:**
```
feat(cli): add validate command for data files

Adds offline data validation with 8 quality checks and
a 0-100 quality score dashboard.

fix(research): handle missing tgpt gracefully in proposal step

docs(readme): update quick start section

refactor(config): simplify settings class
```

---

## ✅ Testing

### Manual Testing Checklist

```bash
# Core functionality
kseye version                          # Should show version + mode
kseye validate data.csv                # Data validation (offline)
kseye analyze data.csv -c column_name  # Analysis (offline)
kseye quick "test query"               # Quick research (needs tgpt)

# Interactive mode
kseye                                  # Main menu should display
```

### Before Submitting PR

- [ ] All existing features still work
- [ ] New feature works without AI (if applicable)
- [ ] New feature works with AI (if applicable)
- [ ] No `print()` statements — use Rich console
- [ ] Code follows style conventions
- [ ] Commit messages are conventional
- [ ] README/CHANGELOG updated if needed
- [ ] No secrets or API keys in code

---

## 🔀 Submitting a Pull Request

### 1. Sync Your Branch

```bash
git fetch upstream
git rebase upstream/main
```

### 2. Push Your Branch

```bash
git push origin feature/your-feature-name
```

### 3. Open PR on GitHub

Your PR should include:

```markdown
## Description
Brief summary of what this PR does.

## Changes
- Added X
- Modified Y
- Fixed Z

## Testing
- [ ] Tested `kseye version`
- [ ] Tested new feature manually
- [ ] No regressions in existing features

## Screenshots (if UI change)
<!-- Add screenshots or terminal output -->

## Related Issues
Closes #123
```

### PR Review Process

```
Your PR → Auto-checks → Maintainer Review → Merge
    ↓           ↓              ↓
  Description  Style ok      Approved?
  Tests ok     No conflicts    ↓
                            Merged ✓
```

---

## 🐛 Reporting Bugs

Open an [issue](https://github.com/kashsight/kseye/issues) with:

```markdown
### Description
What happened vs what you expected.

### Steps to Reproduce
1. `kseye validate data.csv`
2. ...
3. Error appears

### Environment
- **Python**: 3.11.4
- **OS**: Ubuntu 22.04 / Termux / macOS
- **tgpt**: installed / not installed
- **ks-eye version**: 1.0.0

### Error Output
<!-- Paste full error/traceback -->

### Expected Behavior
What should have happened.
```

---

## 💡 Feature Requests

Open an [issue](https://github.com/kashsight/kseye/issues) with:

```markdown
### Problem
What problem are you trying to solve?

### Proposed Solution
How should it work? Include mockups or CLI examples.

### Alternatives
What other approaches did you consider?

### Why This Matters
How does this help ks-eye users?
```

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the project's [proprietary license](LICENSE.md).

---

<p align="center">
  <strong>Thank you for contributing to ks-eye! 🚀</strong>
</p>

<p align="center">
  <a href="https://github.com/kashsight/kseye">Back to README</a>
</p>
