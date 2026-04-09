"""
ks-eye: AI-Human Collaborative Research Assistant
Step-by-step guided research: proposal, questionnaire, data collection, analysis, report
"""

__version__ = "3.0.0"
__author__ = "KashSight Platform"

# ── Research Workflow Steps ──
WORKFLOW_STEPS = [
    "topic_definition",
    "proposal_generation",
    "questionnaire_design",
    "data_collection",
    "data_analysis",
    "literature_review",
    "report_writing",
    "final_output",
]

# ── AI Agent Types (used selectively per step) ──
RESEARCH_AGENTS = [
    "web_search",
    "academic_search",
    "data_synthesis",
    "literature_review",
    "trend_analysis",
    "counter_argument",
    "fact_checker",
    "gap_analysis",
    "summary_generator",
    "statistical_analysis",
    "outline_builder",
    "final_synthesis",
]

# ── Default provider ──
DEFAULT_PROVIDER = "sky"

# ── Agent-provider mapping ──
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

# ── Available AI providers ──
AVAILABLE_PROVIDERS = [
    "sky", "phind", "deepseek", "gemini", "groq",
    "openai", "ollama", "kimi", "isou", "pollinations",
]

# ── Questionnaire question types ──
QUESTION_TYPES = [
    "multiple_choice",
    "likert_scale",
    "yes_no",
    "open_ended",
    "ranking",
    "matrix",
    "demographic",
]

# ── Citation styles ──
CITATION_STYLES = ["apa", "mla", "chicago", "harvard", "ieee"]
