"""
ks-eye v2.0 — Research Utilities
Follow-up suggestions, version compare, tags/search, human notes, research templates.
"""

import json
import os
import difflib
import re
from datetime import datetime
from ks_eye.engines.tgpt_engine import run_tgpt
from ks_eye.config import config
from ks_eye.ui import console, display_table


# ═══════════════════════════════════════════════════════════
#  FOLLOW-UP SUGGESTIONS
# ═══════════════════════════════════════════════════════════

FOLLOW_UP_PROMPT = """You are a Research Advisor. Given this completed research:

TOPIC: {topic}

=== RESEARCH ===
{analysis}
=== END ===

Suggest 5 follow-up research topics that would be most valuable.
For each suggestion:
- Title (5-8 words)
- Why it matters (1-2 sentences)
- What new knowledge it would generate
- Difficulty: Easy / Medium / Hard

Make suggestions specific and actionable, not vague."""


def generate_follow_ups(topic, analysis_text, provider="sky"):
    """Generate follow-up research suggestions."""
    prompt = FOLLOW_UP_PROMPT.format(
        topic=topic,
        analysis=analysis_text[:8000],
    )
    result = run_tgpt(prompt, provider, timeout=60)
    return result if result else "No suggestions generated."


# ═══════════════════════════════════════════════════════════
#  VERSION COMPARE
# ═══════════════════════════════════════════════════════════

def compare_versions(file_a, file_b, context_lines=3):
    """
    Compare two research outputs and show differences.

    Args:
        file_a: Path to first file
        file_b: Path to second file
        context_lines: Lines of context around changes

    Returns:
        dict with diff text, stats
    """
    with open(file_a, "r") as f:
        text_a = f.read()
    with open(file_b, "r") as f:
        text_b = f.read()

    lines_a = text_a.split("\n")
    lines_b = text_b.split("\n")

    diff = list(difflib.unified_diff(lines_a, lines_b,
                                      fromfile="Version A", tofile="Version B",
                                      lineterm="", n=context_lines))

    if not diff:
        return {"identical": True, "diff_text": "Files are identical.", "stats": {}}

    # Count changes
    additions = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))

    diff_text = "\n".join(diff[:200])  # Cap display
    if len(diff) > 200:
        diff_text += f"\n\n... ({len(diff) - 200} more diff lines)"

    return {
        "identical": False,
        "diff_text": diff_text,
        "stats": {
            "total_diff_lines": len(diff),
            "additions": additions,
            "deletions": deletions,
            "file_a_chars": len(text_a),
            "file_b_chars": len(text_b),
        }
    }


# ═══════════════════════════════════════════════════════════
#  TAGS & SEARCH
# ═══════════════════════════════════════════════════════════

def tag_session(folder, tags):
    """Add tags to a research session."""
    meta_file = os.path.join(folder, "metadata.json")
    if os.path.exists(meta_file):
        with open(meta_file, "r") as f:
            meta = json.load(f)
        meta["tags"] = list(set(meta.get("tags", []) + tags))
        with open(meta_file, "w") as f:
            json.dump(meta, f, indent=2)
        return True
    # Create tag file
    tag_file = os.path.join(folder, "tags.json")
    with open(tag_file, "w") as f:
        json.dump({"tags": tags}, f, indent=2)
    return True


def search_research_history(query, max_results=20):
    """
    Search through past research sessions.
    Searches: topic, tags, output text, analysis.
    """
    sessions = config.get("research_sessions", [])
    research_dir = config.RESEARCH_DIR
    results = []

    query_lower = query.lower()

    # Search metadata
    for session in sessions:
        topic = session.get("topic", "").lower()
        tags = session.get("tags", [])
        tags_str = " ".join(tags).lower() if isinstance(tags, list) else ""

        score = 0
        if query_lower in topic:
            score += 10
        if query_lower in tags_str:
            score += 5

        if score > 0:
            results.append({
                "topic": session.get("topic", ""),
                "folder": session.get("folder", session.get("file", "")),
                "timestamp": session.get("timestamp", ""),
                "type": session.get("output_type", session.get("type", "")),
                "score": score,
                "match": "metadata",
            })

    # Search file contents
    if os.path.exists(research_dir):
        for entry in sorted(os.listdir(research_dir)):
            folder = os.path.join(research_dir, entry)
            if not os.path.isdir(folder):
                continue

            # Check tags file
            tag_file = os.path.join(folder, "tags.json")
            if os.path.exists(tag_file):
                with open(tag_file, "r") as f:
                    tags_data = json.load(f)
                for tag in tags_data.get("tags", []):
                    if query_lower in tag.lower():
                        results.append({
                            "topic": entry,
                            "folder": folder,
                            "score": 15,
                            "match": f"tag: {tag}",
                        })
                        break

            # Search text files
            for fname in os.listdir(folder):
                if fname.endswith((".txt", ".md")):
                    fpath = os.path.join(folder, fname)
                    try:
                        with open(fpath, "r") as f:
                            content = f.read()[:20000]
                        if query_lower in content.lower():
                            # Count occurrences
                            count = content.lower().count(query_lower)
                            results.append({
                                "topic": entry,
                                "folder": folder,
                                "score": count,
                                "match": f"{count}x in {fname}",
                            })
                    except Exception:
                        pass

    # Deduplicate and sort
    seen = set()
    unique = []
    for r in results:
        key = r.get("folder", "") + r.get("match", "")
        if key not in seen:
            seen.add(key)
            unique.append(r)

    unique.sort(key=lambda x: x.get("score", 0), reverse=True)

    return unique[:max_results]


def list_all_tags():
    """List all tags used across research sessions."""
    all_tags = {}
    research_dir = config.RESEARCH_DIR

    if os.path.exists(research_dir):
        for entry in os.listdir(research_dir):
            folder = os.path.join(research_dir, entry)
            if not os.path.isdir(folder):
                continue

            # Check metadata
            meta_file = os.path.join(folder, "metadata.json")
            if os.path.exists(meta_file):
                with open(meta_file, "r") as f:
                    meta = json.load(f)
                for tag in meta.get("tags", []):
                    all_tags[tag] = all_tags.get(tag, 0) + 1

            # Check tags file
            tag_file = os.path.join(folder, "tags.json")
            if os.path.exists(tag_file):
                with open(tag_file, "r") as f:
                    tags_data = json.load(f)
                for tag in tags_data.get("tags", []):
                    all_tags[tag] = all_tags.get(tag, 0) + 1

    return dict(sorted(all_tags.items(), key=lambda x: -x[1]))


# ═══════════════════════════════════════════════════════════
#  HUMAN NOTES
# ═══════════════════════════════════════════════════════════

def add_note(folder, note_text, author=None):
    """Add a human note to a research folder."""
    notes_file = os.path.join(folder, "human_notes.json")
    notes = []
    if os.path.exists(notes_file):
        with open(notes_file, "r") as f:
            notes = json.load(f)

    note = {
        "text": note_text,
        "author": author or "User",
        "timestamp": datetime.now().isoformat(),
    }
    notes.append(note)

    with open(notes_file, "w") as f:
        json.dump(notes, f, indent=2)

    return note


def get_notes(folder):
    """Get all human notes from a research folder."""
    notes_file = os.path.join(folder, "human_notes.json")
    if os.path.exists(notes_file):
        with open(notes_file, "r") as f:
            return json.load(f)
    return []


# ═══════════════════════════════════════════════════════════
#  RESEARCH TEMPLATES
# ═══════════════════════════════════════════════════════════

RESEARCH_TEMPLATES = {
    "market_research": {
        "name": "Market Research",
        "description": "Analyze a market: size, growth, competitors, customers",
        "prompt_additions": "Focus on: market size, growth rate, key players, customer segments, pricing, barriers to entry, regulatory environment.",
    },
    "policy_analysis": {
        "name": "Policy Analysis",
        "description": "Analyze a policy: goals, effectiveness, unintended consequences",
        "prompt_additions": "Focus on: policy goals, implementation, effectiveness data, unintended consequences, stakeholder impacts, alternatives.",
    },
    "competitor_analysis": {
        "name": "Competitor Analysis",
        "description": "Compare competitors in a market",
        "prompt_additions": "Focus on: each competitor's strengths, weaknesses, market share, strategy, differentiation, threats.",
    },
    "trend_analysis": {
        "name": "Trend Analysis",
        "description": "Analyze emerging trends and their implications",
        "prompt_additions": "Focus on: trend trajectory, evidence, drivers, inhibitors, timeline, implications for different stakeholders.",
    },
    "literature_review": {
        "name": "Literature Review",
        "description": "Academic literature review on a topic",
        "prompt_additions": "Focus on: key papers, methodological approaches, consensus areas, debates, gaps, future directions.",
    },
    "technical_report": {
        "name": "Technical Report",
        "description": "In-depth technical analysis of a technology or system",
        "prompt_additions": "Focus on: technical specifications, performance data, comparisons, limitations, future developments.",
    },
}


def list_templates():
    """List available research templates."""
    return RESEARCH_TEMPLATES


def get_template(name):
    """Get a specific template."""
    return RESEARCH_TEMPLATES.get(name)
