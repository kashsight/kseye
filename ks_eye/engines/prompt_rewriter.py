"""
ks-eye v2.0 — Prompt Rewriter Engine
AI reads the user's topic and rewrites it into:
  1. A machine-optimized search prompt (for scraping)
  2. A machine-optimized analysis prompt (for the AI analysis phase)

This creates the "internal AI conversation" — the AI talks to itself
to better understand what the user really wants.
"""

from ks_eye.engines.tgpt_engine import run_tgpt
from ks_eye.ui import console, make_progress

# ── Internal System Prompts (AI talking to AI) ──

SEARCH_REWRITE_SYSTEM = """You are a Search Query Optimizer. A user has given you a research topic.
Your job is to rewrite their topic into 5 highly effective search queries that will
return the most relevant, factual, data-rich results from web search engines.

Rules:
- Make queries specific enough to avoid generic results
- Include synonyms, related terms, and alternative phrasings
- At least 2 queries should target data/statistics/evidence
- At least 1 query should target academic/scholarly sources
- At least 1 query should target news/current developments
- Each query should be 3-8 words (good for search engines)
- Output ONLY the 5 queries, one per line, numbered 1-5
- No explanations, no extra text"""

ANALYSIS_REWRITE_SYSTEM = """You are a Research Analyst Planner. A user has given you a research topic.
Your job is to create a structured analysis plan that will guide the AI in
analyzing scraped research data.

Given the user's topic, create:
1. KEY QUESTIONS: 5 specific questions the analysis must answer
2. ANGLES: 4 analytical perspectives (e.g., economic, social, scientific, practical)
3. OUTPUT STRUCTURE: The recommended sections for the final report
4. KEY TERMS: Important terms/concepts that must appear in scraped data

Format your response as:
KEY QUESTIONS:
1. ...
2. ...
3. ...
4. ...
5. ...

ANGLES:
1. ...
2. ...
3. ...
4. ...

OUTPUT STRUCTURE:
- Section 1: ...
- Section 2: ...
- Section 3: ...

KEY TERMS: term1, term2, term3, ..."""


def rewrite_for_search(user_topic):
    """
    AI rewrites the user's topic into optimized search queries.
    Returns a list of 5 search query strings.
    """
    console.print(f"[dim]  🤖 AI is rewriting your topic for optimal search...[/dim]")

    prompt = f"User's research topic: {user_topic}"
    response = run_tgpt(prompt, provider="sky", system_prompt=SEARCH_REWRITE_SYSTEM, timeout=30)

    if not response:
        console.print(f"[dim]  ⚠ AI rewrite failed, using original topic[/dim]")
        return [user_topic]

    # Parse numbered queries
    queries = []
    for line in response.strip().split("\n"):
        line = line.strip()
        # Remove numbering
        cleaned = line.lstrip("0123456789.-) ")
        if cleaned and len(cleaned) > 3:
            queries.append(cleaned)

    if not queries:
        console.print(f"[dim]  ⚠ AI returned empty queries, using original topic[/dim]")
        return [user_topic]

    console.print(f"[dim]  ✓ Generated {len(queries)} optimized search queries[/dim]")
    return queries


def rewrite_for_analysis(user_topic):
    """
    AI rewrites the user's topic into a structured analysis plan.
    Returns a dict with: key_questions, angles, output_structure, key_terms
    """
    console.print(f"[dim]  🤖 AI is creating an analysis plan...[/dim]")

    prompt = f"User's research topic: {user_topic}"
    response = run_tgpt(prompt, provider="sky", system_prompt=ANALYSIS_REWRITE_SYSTEM, timeout=45)

    if not response:
        console.print(f"[dim]  ⚠ AI analysis plan failed, using defaults[/dim]")
        return {
            "key_questions": [f"What is {user_topic}?", f"Why does {user_topic} matter?"],
            "angles": ["General overview"],
            "output_structure": ["Overview", "Key Findings", "Conclusion"],
            "key_terms": [user_topic],
            "raw_plan": "",
        }

    # Parse the structured response
    result = {
        "key_questions": [],
        "angles": [],
        "output_structure": [],
        "key_terms": [],
        "raw_plan": response,
    }

    current_section = None
    for line in response.strip().split("\n"):
        line_stripped = line.strip()
        if not line_stripped:
            continue

        upper = line_stripped.upper()
        if "KEY QUESTIONS" in upper:
            current_section = "key_questions"
            continue
        elif "ANGLES" in upper:
            current_section = "angles"
            continue
        elif "OUTPUT STRUCTURE" in upper:
            current_section = "output_structure"
            continue
        elif "KEY TERMS" in upper:
            # Parse comma-separated terms
            if ":" in line_stripped:
                terms = line_stripped.split(":", 1)[1].strip()
                result["key_terms"] = [t.strip() for t in terms.split(",") if t.strip()]
            current_section = "key_terms"
            continue

        if current_section and line_stripped:
            # Remove numbering and bullet points
            cleaned = line_stripped.lstrip("0123456789.-)•* ")
            if cleaned:
                if current_section == "output_structure":
                    cleaned = cleaned.lstrip("Section ")
                    if ":" in cleaned:
                        cleaned = cleaned.split(":", 1)[1].strip()
                    elif cleaned.startswith("- "):
                        cleaned = cleaned[2:]
                result[current_section].append(cleaned)

    # Ensure we have at least something
    if not result["key_questions"]:
        result["key_questions"] = [f"What are the key facts about {user_topic}?"]
    if not result["angles"]:
        result["angles"] = ["General overview", "Evidence-based analysis"]
    if not result["output_structure"]:
        result["output_structure"] = ["Overview", "Key Findings", "Analysis", "Conclusion"]

    console.print(f"[dim]  ✓ Analysis plan created: {len(result['key_questions'])} questions, {len(result['angles'])} angles[/dim]")
    return result
