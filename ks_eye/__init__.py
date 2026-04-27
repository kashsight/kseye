"""
ks-eye v2.0 — Online AI Research Platform
Scrape real websites → AI reads & analyzes → Structured reports
"""

__version__ = "2.0.0"
__author__ = "KashSight Platform"

# ── AI Providers ──
AVAILABLE_PROVIDERS = [
    "sky", "phind", "deepseek", "gemini", "groq",
    "openai", "ollama", "kimi", "isou", "pollinations",
]
DEFAULT_PROVIDER = "sky"

# ── Output Types ──
OUTPUT_TYPES = ["summary", "report", "blog", "guide", "proposal"]

# ── Scrape Depth Levels ──
SCRAPE_DEPTH_MAP = {
    1: "quick",      # Top 5 results, minimal scraping
    2: "standard",   # Top 15 results, full content extraction
    3: "deep",       # Top 30 results + academic sources + related articles
}

# ── Multi-Agent Department Sizes ──
MULTI_AGENT_DEPARTMENTS = {
    "collectors": 10,
    "validators": 15,
    "analysts": 5,
    "summarizers": 5,
    "writers": 5,
    "editors": 5,
}
TOTAL_MULTI_AGENTS = sum(MULTI_AGENT_DEPARTMENTS.values())  # 45

# ── Agent-to-Provider Defaults ──
DEFAULT_AGENT_PROVIDERS = {
    "web_search": "sky",
    "academic_search": "gemini",
    "data_synthesis": "deepseek",
    "literature_review": "groq",
    "trend_analysis": "sky",
    "counter_argument": "phind",
    "fact_checker": "openai",
    "gap_analysis": "phind",
    "summary_generator": "sky",
    "statistical_analysis": "openai",
    "outline_builder": "sky",
    "final_synthesis": "openai",
}
