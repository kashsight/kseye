# Contributing to ks-eye

Thank you for your interest in contributing to ks-eye! This document provides guidelines for contributing to the project.

## 🧭 Philosophy

ks-eye v3 is an **AI-Human Collaborative Research Assistant**. The core philosophy is:
- **AI suggests, human decides** — Every step requires human review and approval
- **Offline-first** — Core functionality works without AI
- **Step-by-step guided workflow** — No fully automated research

When contributing, ensure new features align with this philosophy.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/kseye.git
   cd kseye
   ```
3. Install dependencies:
   ```bash
   pip install -e .
   ```
4. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.7+
- `tgpt` (optional, for AI features): `go install github.com/aikooo/tgpt/v2@latest`

### Project Structure

```
ks_eye/
├── ks_eye/                 # Main package
│   ├── cli.py              # CLI interface
│   ├── config.py           # Configuration management
│   ├── ui.py               # UI components
│   ├── engines/            # Core engines
│   │   ├── research_assistant.py
│   │   ├── data_processing.py
│   │   ├── quick_research.py
│   │   ├── scholar_search.py
│   │   └── ...
│   └── agents/             # Agent definitions
├── data/                   # Data directory
│   ├── config/             # Configuration files
│   └── research_history/   # Session storage
└── setup.py
```

## Making Changes

### Branch Naming

- `feature/description` — New features
- `fix/description` — Bug fixes
- `docs/description` — Documentation updates
- `refactor/description` — Code refactoring

### Commit Messages

Follow conventional commits:
```
type(scope): description

Longer description if needed
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(cli): add validate command for data files

Adds offline data validation with quality scoring
```

## Submitting a Pull Request

1. **Update your branch** with latest main:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Test your changes**:
   ```bash
   kseye version
   kseye validate test.csv  # If modifying data processing
   ```

3. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open a PR** on GitHub with:
   - Clear title and description
   - Reference any related issues
   - Screenshots if UI changes

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints where helpful
- Maximum line length: 100 characters
- Use double quotes for strings

### Documentation

- Update README.md if adding features
- Add docstrings to new functions/classes
- Update CHANGELOG.md with your changes

### Error Handling

- Use Rich console for user-facing messages
- Provide helpful error messages
- Graceful degradation when AI unavailable

## Testing

### Manual Testing

```bash
# Basic functionality
kseye version

# Data processing (offline)
kseye validate data.csv
kseye analyze data.csv -c column_name

# Quick research (requires tgpt)
kseye quick "test query"
```

### Test Checklist

- [ ] CLI commands work without errors
- [ ] Offline features work without tgpt
- [ ] AI features work with tgpt installed
- [ ] No regressions in existing workflows
- [ ] User messages are clear and helpful

## Reporting Bugs

Open an issue with:

1. **Description** — What happened vs what you expected
2. **Steps to reproduce** — Exact commands
3. **Environment** — Python version, OS, tgpt version
4. **Screenshots** — If applicable

## Feature Requests

Open an issue with:

1. **Problem** — What problem are you trying to solve?
2. **Proposed solution** — How should it work?
3. **Alternatives considered** — Other approaches

## 📄 License

By contributing, you agree that your contributions will be licensed under the project's proprietary license.

---

Thank you for contributing to ks-eye! 🚀
