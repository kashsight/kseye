"""
Suggestion Engine for ks-eye
Suggests sub-searches and follow-up research directions
"""

import re


class SuggestionEngine:
    """Generates suggestions for sub-searches and follow-up research"""

    def __init__(self):
        self.suggestion_patterns = [
            {
                "pattern": r"(effect|impact|influence|consequence)",
                "suggestion": "Investigate the {term} of {topic} on related fields",
                "reason": "Understanding causal relationships deepens research",
            },
            {
                "pattern": r"(history|evolution|development|origins)",
                "suggestion": "Trace the historical evolution of {topic}",
                "reason": "Historical context provides foundational understanding",
            },
            {
                "pattern": r"(future|trends|prediction|forecast)",
                "suggestion": "Analyze future trends and predictions for {topic}",
                "reason": "Forward-looking analysis adds practical value",
            },
            {
                "pattern": r"(comparison|vs\.?|versus|compared)",
                "suggestion": "Compare {topic} with alternative approaches or systems",
                "reason": "Comparative analysis reveals strengths and weaknesses",
            },
            {
                "pattern": r"(method|technique|approach|algorithm)",
                "suggestion": "Examine the methodology and techniques used in {topic} research",
                "reason": "Methodological rigor is essential for credible findings",
            },
            {
                "pattern": r"(case\s?study|example|application|implementation)",
                "suggestion": "Find case studies and real-world applications of {topic}",
                "reason": "Practical examples demonstrate real-world impact",
            },
            {
                "pattern": r"(controversy|debate|criticism|challenge)",
                "suggestion": "Explore controversies and debates surrounding {topic}",
                "reason": "Critical perspectives reveal research gaps",
            },
            {
                "pattern": r"(statistics|data|evidence|metrics)",
                "suggestion": "Gather quantitative data and statistics on {topic}",
                "reason": "Data-driven insights strengthen arguments",
            },
            {
                "pattern": r"(expert|researcher|scientist|professor|author)",
                "suggestion": "Identify leading experts and their contributions to {topic}",
                "reason": "Expert perspectives carry high authority",
            },
            {
                "pattern": r"(economic|financial|cost|market|revenue)",
                "suggestion": "Analyze economic and financial implications of {topic}",
                "reason": "Economic perspective adds practical relevance",
            },
            {
                "pattern": r"(ethical|moral|privacy|bias|fairness)",
                "suggestion": "Examine ethical implications of {topic}",
                "reason": "Ethical considerations are critical in modern research",
            },
            {
                "pattern": r"(policy|regulation|law|governance|legal)",
                "suggestion": "Investigate policy and regulatory frameworks for {topic}",
                "reason": "Legal context shapes research applications",
            },
        ]

    def generate_suggestions(self, query, results=None, max_suggestions=10):
        """
        Generate sub-search suggestions based on query and results
        
        Args:
            query: Original research query
            results: Agent results dict (optional)
            max_suggestions: Maximum suggestions to return
        
        Returns:
            List of suggestion dicts
        """
        suggestions = []
        seen_queries = set()

        # Pattern-based suggestions
        for pattern_data in self.suggestion_patterns:
            if re.search(pattern_data["pattern"], query, re.IGNORECASE):
                suggestion_query = pattern_data["suggestion"].format(
                    term=self._extract_matching_term(query, pattern_data["pattern"]),
                    topic=query,
                )
                if suggestion_query not in seen_queries:
                    suggestions.append({
                        "query": suggestion_query,
                        "reason": pattern_data["reason"],
                        "type": "pattern",
                    })
                    seen_queries.add(suggestion_query)

        # Standard follow-up suggestions
        standard_suggestions = [
            {
                "query": f"Recent developments in {query}",
                "reason": "Stay current with latest research",
                "type": "temporal",
            },
            {
                "query": f"Criticism and limitations of {query} research",
                "reason": "Identify research limitations",
                "type": "critical",
            },
            {
                "query": f"Meta-analysis and systematic reviews of {query}",
                "reason": "High-level evidence synthesis",
                "type": "synthesis",
            },
            {
                "query": f"Practical applications of {query}",
                "reason": "Bridge theory and practice",
                "type": "application",
            },
            {
                "query": f"Interdisciplinary connections to {query}",
                "reason": "Broader perspective across fields",
                "type": "interdisciplinary",
            },
        ]

        for sug in standard_suggestions:
            if sug["query"] not in seen_queries:
                suggestions.append(sug)
                seen_queries.add(sug["query"])

        # If we have results, suggest deep dives into specific findings
        if results:
            for agent_type, result_data in results.items():
                if result_data.get("status") == "completed" and result_data.get("result"):
                    result_text = result_data["result"]
                    # Extract potential sub-topics
                    sub_topics = self._extract_topics(result_text)
                    for topic in sub_topics[:3]:
                        sub_query = f"{topic} in context of {query}"
                        if sub_query not in seen_queries:
                            suggestions.append({
                                "query": sub_query,
                                "reason": f"Found in {agent_type.replace('_', ' ')} analysis",
                                "type": "derived",
                            })
                            seen_queries.add(sub_query)

        return suggestions[:max_suggestions]

    def _extract_matching_term(self, text, pattern):
        """Extract the matching term from text"""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
        return "this"

    def _extract_topics(self, text, max_topics=5):
        """Extract key topics/phrases from text"""
        # Look for capitalized phrases, technical terms, and noun phrases
        patterns = [
            r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b",  # Capitalized multi-word phrases
            r"\b[A-Z]{2,}\b",  # Acronyms
            r'\b[A-Z]\w+(?:\s+(?:of|in|and|for|with)\s+[A-Z]\w+)+\b',  # Noun phrases
        ]

        topics = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            topics.extend(matches)

        # Remove duplicates and common words
        common_words = {"The", "This", "That", "These", "Those", "And", "For", "With"}
        topics = [t for t in set(topics) if t not in common_words]

        return topics[:max_topics]

    def suggest_agents_to_add(self, current_agents, results):
        """Suggest which additional agents might be useful"""
        from ks_eye import AGENT_TYPES

        current_set = set(current_agents)
        all_set = set(AGENT_TYPES)
        available = all_set - current_set

        suggestions = []
        if not any("counter" in a for a in current_agents):
            suggestions.append({
                "agent": "counter_argument",
                "reason": "No counter-arguments explored yet",
            })
        if not any("fact" in a for a in current_agents):
            suggestions.append({
                "agent": "fact_checker",
                "reason": "Claims should be verified",
            })
        if not any("gap" in a for a in current_agents):
            suggestions.append({
                "agent": "gap_analysis",
                "reason": "Research gaps not yet identified",
            })

        return suggestions
