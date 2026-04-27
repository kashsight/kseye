<p align="center">
  <img src="https://img.shields.io/badge/SECURITY-report%20vulnerabilities-FF6B6B?style=for-the-badge" alt="Security" />
</p>

---

## 🛡️ Security Policy

### Supported Versions

| Version | Supported | End of Life |
|---------|-----------|-------------|
| **1.0.x** | ✅ Active | — |
| **< 1.0** | ❌ Unsupported | EOL |

---

## 🚨 Reporting a Vulnerability

> **DO NOT open a public GitHub issue.**

### How to Report

| Step | Action |
|------|--------|
| **1** | Email: **kashsight@gmail.com** |
| **2** | Include: description, reproduction steps, potential impact, suggested fix |
| **3** | We will respond within **48 hours** with acknowledgment |

### Response Timeline

```
Report Received → 48hrs → Acknowledgment
                       ↓
                  5 days → Initial Assessment
                       ↓
              30 days → Fix Released (severity dependent)
                       ↓
              Public Disclosure (coordinated)
```

---

## 🔒 Security Considerations

### Data Privacy

| Aspect | Details |
|--------|---------|
| **Storage** | All research data stored locally in `data/research_history/` |
| **Transmission** | No data transmitted without explicit user action |
| **AI Queries** | Go through `tgpt` — see [tgpt privacy](https://github.com/aikooo/tgpt) |
| **Session Data** | Saved as `.txt` and `.json` — human-readable, no encryption |

### API Keys & Configuration

| File | Sensitivity | Git Tracked? |
|------|-------------|--------------|
| `data/config/settings.json` | Low (user preferences) | ❌ No (.gitignore) |
| `data/config/agent_providers.json` | Low (provider mapping) | ✅ Yes |
| `.env` files | High (if used) | ❌ No (.gitignore) |

> **Note:** ks-eye does not store API keys directly. Users configure API keys through `tgpt` or environment variables.

### Dependency Security

```bash
# Recommended: audit dependencies periodically
pip audit

# Check for known vulnerabilities
pip check
```

---

## 📋 Best Practices for Contributors

### ✅ DO

| Practice | Example |
|----------|---------|
| **Use environment variables** | `os.environ.get("API_KEY")` |
| **Validate all input** | Check file paths, user-provided data |
| **Use safe file operations** | `os.path.join()`, not string concatenation |
| **Sanitize user input** | Strip dangerous characters from file paths |
| **Review dependencies** | Check for known CVEs before adding packages |
| **Fail safely** | Graceful degradation, no stack traces to users |

### ❌ DON'T

| Anti-Pattern | Risk |
|--------------|------|
| Hardcoded secrets or API keys | Credential exposure |
| `eval()` / `exec()` on user input | Code execution |
| Shell command injection | `os.system(user_input)` |
| Directory traversal | `open(user_path)` without validation |
| Leaking sensitive info in errors | Stack traces with file paths |
| Committing `.env` or config files | Public repository exposure |

---

## 🔍 Security Checklist for PRs

Before submitting a pull request, verify:

```
┌─────────────────────────────────────────────────────────┐
│                  PR SECURITY CHECKLIST                   │
├─────────────────────────────────────────────────────────┤
│ □  No hardcoded secrets or API keys                     │
│ □  Input validation for all user-provided data          │
│ □  Safe file path handling (no directory traversal)     │
│ □  No shell command injection vulnerabilities           │
│ □  Dependencies up to date and secure                   │
│ □  Error messages don't leak sensitive information      │
│ □  No unnecessary permissions requested                 │
│ □  Graceful degradation when dependencies missing       │
│ □  No use of eval/exec on user input                    │
│ □  All sensitive files in .gitignore                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🐛 Known Security History

| Date | Version | Issue | Resolution |
|------|---------|-------|------------|
| 2026-04-08 | 1.0.0 | Topic parsing could crash on malformed input | Added graceful fallback |
| 2026-04-08 | 1.0.0 | Missing tgpt caused unhandled exception | Added graceful manual entry mode |

---

## 📬 Contact

| Purpose | Method |
|---------|--------|
| **Report vulnerability** | kashsight@gmail.com |
| **Security questions** | Open a [private discussion](https://github.com/kashsight/kseye/discussions) |
| **General** | [GitHub Issues](https://github.com/kashsight/kseye/issues) |

---

<p align="center">
  <strong>Thank you for helping keep ks-eye secure! 🔒</strong>
</p>

<p align="center">
  <a href="README.md">← Back to README</a>
</p>
