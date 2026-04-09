"""
Research Output Formatter v2 for ks-eye
TOC, Bibliography, Citations (APA/MLA/Chicago/Harvard), Appendix, Index,
Knowledge Graph, Sentiment Dashboard, Bias Check, Peer Review, Fact Density,
Source Reliability Dashboard, Timeline — all in .txt format
"""

import re
import json
from datetime import datetime
from collections import defaultdict


class CitationManager:
    """Format citations in multiple styles"""

    @staticmethod
    def _clean_author(authors):
        if not authors:
            return "Unknown Author"
        # Handle various author formats
        if "," in authors:
            parts = authors.split(",")
            return parts[0].strip()
        parts = authors.strip().split()
        if len(parts) >= 2:
            return parts[0]  # First word (usually last name in academic format)
        return authors.strip()

    @staticmethod
    def _extract_year(source):
        year = source.get("year", "")
        if year and str(year).isdigit():
            return str(year)
        # Try to extract from date strings
        date_str = str(source.get("year", ""))
        match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if match:
            return match.group(0)
        return "n.d."

    @classmethod
    def format_apa(cls, source, index):
        author = cls._clean_author(source.get("authors", ""))
        year = cls._extract_year(source)
        title = source.get("title", "Untitled")
        src = source.get("source", "")
        url = source.get("url", "")
        cite = f"[{index}] {author}. ({year}). {title}. {src}."
        if url:
            cite += f" {url}"
        return cite

    @classmethod
    def format_mla(cls, source, index):
        author = cls._clean_author(source.get("authors", ""))
        title = source.get("title", "Untitled")
        src = source.get("source", "")
        year = cls._extract_year(source)
        url = source.get("url", "")
        cite = f"[{index}] {author}. \"{title}.\" {src}, {year}."
        if url:
            cite += f" {url}."
        return cite

    @classmethod
    def format_chicago(cls, source, index):
        author = cls._clean_author(source.get("authors", ""))
        title = source.get("title", "Untitled")
        src = source.get("source", "")
        year = cls._extract_year(source)
        url = source.get("url", "")
        cite = f"[{index}] {author}. {title}. {src}, {year}."
        if url:
            cite += f" {url}."
        return cite

    @classmethod
    def format_harvard(cls, source, index):
        author = cls._clean_author(source.get("authors", ""))
        year = cls._extract_year(source)
        title = source.get("title", "Untitled")
        src = source.get("source", "")
        url = source.get("url", "")
        cite = f"[{index}] {author}, {year}. {title}. {src}."
        if url:
            cite += f" Available at: {url}"
        return cite

    @classmethod
    def format_ieee(cls, source, index):
        author = cls._clean_author(source.get("authors", ""))
        title = source.get("title", "Untitled")
        src = source.get("source", "")
        year = cls._extract_year(source)
        url = source.get("url", "")
        cite = f"[{index}] {author}, \"{title},\" {src}, {year}."
        if url:
            cite += f" {url}."
        return cite

    FORMATTERS = {
        "apa": format_apa,
        "mla": format_mla,
        "chicago": format_chicago,
        "harvard": format_harvard,
        "ieee": format_ieee,
    }

    @classmethod
    def format_citation(cls, source, index, style="apa"):
        formatter = cls.FORMATTERS.get(style, cls.format_apa)
        return formatter(cls, source, index)

    @classmethod
    def format_bibliography(cls, sources, style="apa"):
        lines = []
        for i, src in enumerate(sources, 1):
            lines.append(cls.format_citation(src, i, style))
        return "\n".join(lines)


class IndexGenerator:
    """Generate alphabetical index of key terms"""

    @staticmethod
    def extract_terms(text, sections=None):
        """Extract indexable terms from text"""
        terms = defaultdict(list)
        # Look for capitalized technical terms
        patterns = [
            r'\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})+\b',  # Multi-word caps
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b(?:AI|ML|DL|NLP|API|UI|UX|IoT|GPU|CPU|RAM|HTTP|SSL|TLS|SSH|FTP|JSON|XML|HTML|CSS|SQL|CLI|IDE|GUI|OS)\b',  # Common acronyms
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                term = match.group(0)
                if len(term) > 1 and term not in {"The", "This", "That", "These", "Those", "And", "For", "With", "From", "Have"}:
                    terms[term].append("")
        return dict(sorted(terms.items()))

    @staticmethod
    def format_index(terms, max_width=78):
        """Format index as text"""
        lines = []
        current_letter = ""
        for term in sorted(terms.keys(), key=str.lower):
            first_letter = term[0].upper()
            if first_letter != current_letter:
                current_letter = first_letter
                lines.append(f"\n  --- {current_letter} ---")
            lines.append(f"    {term}")
        return "\n".join(lines)


class KnowledgeGraphBuilder:
    """Build and format knowledge graph in text"""

    @staticmethod
    def build_from_results(agent_results, sources):
        """Extract concepts and relationships from results"""
        nodes = []
        edges = []

        # Extract concepts from sources
        source_types = defaultdict(int)
        for src in sources:
            src_type = src.get("type", "unknown")
            source_types[src_type] += 1
            nodes.append(f"Source: {src.get('title', 'Untitled')[:50]}")

        # Extract key concepts from agent results
        for agent_type, data in agent_results.items():
            if data.get("result"):
                result_text = data["result"][:500]
                nodes.append(f"[{agent_type}] Analysis")

        return {
            "nodes": nodes[:50],
            "edges": edges[:50],
            "source_type_distribution": dict(source_types),
        }

    @staticmethod
    def format_graph(graph):
        lines = []
        lines.append("  Knowledge Graph Summary")
        lines.append("  " + "-" * 40)
        lines.append(f"  Total Nodes: {len(graph.get('nodes', []))}")
        lines.append(f"  Total Edges: {len(graph.get('edges', []))}")
        lines.append("")
        if graph.get("source_type_distribution"):
            lines.append("  Source Type Distribution:")
            for stype, count in graph["source_type_distribution"].items():
                lines.append(f"    {stype}: {count}")
        lines.append("")
        lines.append("  Nodes:")
        for node in graph.get("nodes", [])[:30]:
            lines.append(f"    • {node}")
        return "\n".join(lines)


class ResearchOutputFormatter:
    """Format research results into comprehensive .txt output"""

    def __init__(self, citation_style="apa"):
        self.citation_style = citation_style

    def create_json_output(self, query, sources, agent_results, suggestions, title=None,
                          pass_summaries=None, branch_tree=None, total_passes=1,
                          branch_depth=0, total_duration=0):
        json_data = {
            "metadata": {
                "title": title or f"Research Paper: {query.title()}",
                "query": query,
                "generated_at": datetime.now().isoformat(),
                "tool": "ks-eye",
                "version": "2.0.0",
                "total_agents_used": len(agent_results),
                "agents_completed": sum(1 for v in agent_results.values() if v.get("status") == "completed"),
                "agents_failed": sum(1 for v in agent_results.values() if v.get("status") == "error"),
                "passes": total_passes,
                "branch_depth": branch_depth,
                "total_duration_seconds": total_duration,
            },
            "abstract": self._generate_abstract(query, agent_results),
            "sources": {
                "total_count": len(sources),
                "academic_sources": sum(1 for s in sources if s.get("type") == "academic"),
                "web_sources": sum(1 for s in sources if s.get("type") == "web"),
                "wikipedia_sources": sum(1 for s in sources if s.get("type") == "wikipedia"),
                "arxiv_sources": sum(1 for s in sources if s.get("type") == "arxiv"),
                "pubmed_sources": sum(1 for s in sources if s.get("type") == "pubmed"),
                "news_sources": sum(1 for s in sources if s.get("type") == "news"),
                "patent_sources": sum(1 for s in sources if s.get("type") == "patent"),
                "dataset_sources": sum(1 for s in sources if s.get("type") == "dataset"),
                "high_reliability": sum(1 for s in sources if s.get("reliability") == "High"),
                "medium_reliability": sum(1 for s in sources if s.get("reliability") == "Medium"),
                "low_reliability": sum(1 for s in sources if s.get("reliability") == "Low"),
                "list": sources,
            },
            "sections": self._build_sections(agent_results),
            "timeline": self._extract_timeline(agent_results),
            "sentiment": self._extract_sentiment(agent_results),
            "bias_analysis": self._extract_bias(agent_results),
            "fact_density": self._extract_fact_density(agent_results),
            "peer_review": self._extract_peer_review(agent_results),
            "knowledge_graph": KnowledgeGraphBuilder.build_from_results(agent_results, sources),
            "methodology": self._extract_methodology(query, agent_results, total_passes),
            "confidence_scores": self._calculate_confidence(agent_results),
            "suggestions": suggestions,
            "limitations": self._extract_limitations(agent_results),
            "full_agent_data": agent_results,
            "pass_summaries": pass_summaries or {},
            "branch_tree": branch_tree or {},
        }
        return json_data

    def _generate_abstract(self, query, agent_results):
        summary_data = agent_results.get("summary_generator", {})
        if summary_data.get("result"):
            return summary_data["result"][:500]
        return f"This research paper examines {query} through comprehensive analysis of academic and web sources. Multiple AI agents conducted parallel research to synthesize current findings, methodologies, and future directions."

    def _build_sections(self, agent_results):
        sections = []
        section_map = [
            ("web_search", "1. Introduction"),
            ("literature_review", "2. Literature Review"),
            ("wikipedia_extractor", "3. Background Overview (Wikipedia)"),
            ("methodology_extractor", "4. Research Methodology"),
            ("data_synthesis", "5. Results and Analysis"),
            ("statistical_analysis", "6. Statistical Analysis"),
            ("timeline_generator", "7. Historical Timeline"),
            ("person_profiler", "8. Key Researchers and Institutions"),
            ("trend_analysis", "9. Trends and Future Directions"),
            ("sentiment_analysis", "10. Research Sentiment Analysis"),
            ("counter_argument", "11. Counter-Arguments and Critical Perspectives"),
            ("bias_detection", "12. Bias and Source Evaluation"),
            ("news_analyst", "13. Media and Public Discourse"),
            ("patent_searcher", "14. Patents and Commercial Research"),
            ("dataset_finder", "15. Available Datasets"),
            ("gap_analysis", "16. Research Gaps and Limitations"),
            ("fact_density_scorer", "17. Evidence Density Analysis"),
            ("peer_reviewer_1", "18. Peer Review: Methodology"),
            ("peer_reviewer_2", "19. Peer Review: Literature Coverage"),
            ("summary_generator", "20. Conclusion"),
        ]
        for agent_key, section_title in section_map:
            if agent_key in agent_results:
                sections.append({
                    "title": section_title,
                    "content": agent_results[agent_key].get("result", ""),
                    "agent": agent_key,
                })
        return sections

    def _extract_timeline(self, agent_results):
        data = agent_results.get("timeline_generator", {})
        if data.get("result"):
            return data["result"]
        return ""

    def _extract_sentiment(self, agent_results):
        data = agent_results.get("sentiment_analysis", {})
        if data.get("result"):
            return data["result"]
        return ""

    def _extract_bias(self, agent_results):
        data = agent_results.get("bias_detection", {})
        if data.get("result"):
            return data["result"]
        return ""

    def _extract_fact_density(self, agent_results):
        data = agent_results.get("fact_density_scorer", {})
        if data.get("result"):
            return data["result"]
        return ""

    def _extract_peer_review(self, agent_results):
        reviews = {}
        r1 = agent_results.get("peer_reviewer_1", {})
        r2 = agent_results.get("peer_reviewer_2", {})
        if r1.get("result"):
            reviews["Methodology Review"] = r1["result"]
        if r2.get("result"):
            reviews["Literature Review"] = r2["result"]
        return reviews

    def _calculate_confidence(self, agent_results):
        confidence = {}
        total = len(agent_results)
        completed = sum(1 for v in agent_results.values() if v.get("status") == "completed")
        confidence["overall"] = int((completed / total * 100) if total > 0 else 0)
        confidence["data_quality"] = 85 if agent_results.get("data_synthesis", {}).get("status") == "completed" else 50
        confidence["source_reliability"] = 90 if agent_results.get("source_verification", {}).get("status") == "completed" else 60
        confidence["factual_accuracy"] = 88 if agent_results.get("fact_checker", {}).get("status") == "completed" else 55
        confidence["academic_rigor"] = 82 if agent_results.get("academic_search", {}).get("status") == "completed" else 50
        confidence["completeness"] = 75 if agent_results.get("literature_review", {}).get("status") == "completed" else 45
        confidence["bias_awareness"] = 80 if agent_results.get("bias_detection", {}).get("status") == "completed" else 50
        confidence["peer_reviewed"] = 70 if agent_results.get("peer_reviewer_1", {}).get("status") == "completed" else 40
        return confidence

    def _extract_methodology(self, query, agent_results, passes=1):
        return {
            "approach": "Multi-agent parallel research synthesis with recursive passes",
            "sources_used": "Google Scholar, Semantic Scholar, CrossRef, DuckDuckGo, Wikipedia, arXiv, PubMed, SSRN, News, Google Patents, Dataset repositories, AI-powered analysis",
            "agents_involved": len(agent_results),
            "recursive_passes": passes,
            "memory_sharing": True,
            "process": [
                "1. Comprehensive web and academic search across multiple sources",
                "2. Parallel AI agent analysis with specialized focuses",
                "3. Data synthesis from multiple perspectives",
                "4. Fact-checking and source verification",
                "5. Bias detection and sentiment analysis",
                "6. Peer review simulation",
                "7. Final synthesis and paper generation",
            ],
            "limitations": [
                "AI-generated content requires human verification",
                "Source quality varies by availability",
                "Real-time data may be limited by API access",
                "Automated analysis may miss nuanced context",
            ],
        }

    def _extract_limitations(self, agent_results):
        limitations = []
        gap = agent_results.get("gap_analysis", {})
        if gap.get("result"):
            for sentence in gap["result"].split(". "):
                if any(w in sentence.lower() for w in ["limitation", "gap", "lack", "insufficient", "unclear"]):
                    limitations.append(sentence.strip())
        return limitations[:5]

    # ─────────────────────────────────────────────────────────
    #  TEXT OUTPUT — Full formatted research paper
    # ─────────────────────────────────────────────────────────

    def format_text_output(self, json_data, include_toc=True, include_index=True,
                          include_appendix=True, include_bibliography=True,
                          include_knowledge_graph=True, include_sentiment=True,
                          include_bias_check=True, include_peer_review=True,
                          include_fact_density=True, include_source_reliability=True):
        output = []

        meta = json_data.get("metadata", {})
        sources = json_data.get("sources", {})
        sections = json_data.get("sections", [])
        confidence = json_data.get("confidence_scores", {})
        suggestions = json_data.get("suggestions", [])
        methodology = json_data.get("methodology", {})
        limitations = json_data.get("limitations", [])

        # Page counter for TOC references
        page_num = 1

        # ════════════════════════════════════════════════════
        #  COVER PAGE
        # ════════════════════════════════════════════════════
        output.append("=" * 80)
        output.append("")
        output.append(meta.get("title", "Research Paper").upper())
        output.append("")
        output.append(f"Query: {meta.get('query', 'N/A')}")
        output.append(f"Generated: {meta.get('generated_at', 'N/A')}")
        output.append(f"Tool: ks-eye v{meta.get('version', '2.0.0')}")
        output.append(f"Agents: {meta.get('agents_completed', 0)}/{meta.get('total_agents_used', 0)} completed")
        output.append(f"Passes: {meta.get('passes', 1)}")
        output.append(f"Duration: {meta.get('total_duration_seconds', 0):.1f}s")
        output.append("")
        output.append("=" * 80)
        output.append("")

        # ════════════════════════════════════════════════════
        #  TABLE OF CONTENTS
        # ════════════════════════════════════════════════════
        if include_toc:
            output.append("TABLE OF CONTENTS")
            output.append("=" * 80)
            toc_entries = [
                ("Abstract", page_num),
            ]
            for section in sections:
                page_num += 1
                toc_entries.append((section.get("title", "Section"), page_num))
            toc_entries.append(("Sources Summary", page_num + 1))
            toc_entries.append(("Source Reliability Dashboard", page_num + 2))
            toc_entries.append(("Confidence Scores", page_num + 3))
            if include_bibliography:
                toc_entries.append(("Bibliography", page_num + 4))
            if include_knowledge_graph:
                toc_entries.append(("Knowledge Graph", page_num + 5))
            if include_sentiment:
                toc_entries.append(("Sentiment Analysis", page_num + 6))
            if include_bias_check:
                toc_entries.append(("Bias Detection", page_num + 7))
            if include_fact_density:
                toc_entries.append(("Fact Density Analysis", page_num + 8))
            if include_peer_review:
                toc_entries.append(("Peer Review", page_num + 9))
            toc_entries.append(("Research Methodology", page_num + 10))
            toc_entries.append(("Limitations", page_num + 11))
            toc_entries.append(("Suggestions for Further Research", page_num + 12))
            if include_index:
                toc_entries.append(("Index", page_num + 13))
            if include_appendix:
                toc_entries.append(("Appendix", page_num + 14))

            max_title_len = max(len(t[0]) for t in toc_entries)
            for title, pg in toc_entries:
                dots = "." * (60 - len(title) - len(str(pg)))
                output.append(f"  {title} {dots} {pg}")
            output.append("")
            output.append("-" * 80)
            output.append("")

        # ════════════════════════════════════════════════════
        #  ABSTRACT
        # ════════════════════════════════════════════════════
        output.append("ABSTRACT")
        output.append("=" * 80)
        output.append(json_data.get("abstract", "N/A"))
        output.append("")
        output.append("-" * 80)
        output.append("")

        # ════════════════════════════════════════════════════
        #  SECTIONS
        # ════════════════════════════════════════════════════
        for section in sections:
            output.append(section.get("title", "Section").upper())
            output.append("=" * 80)
            output.append(section.get("content", "No content available"))
            output.append("")
            output.append("-" * 80)
            output.append("")

        # ════════════════════════════════════════════════════
        #  SOURCES SUMMARY
        # ════════════════════════════════════════════════════
        output.append("SOURCES SUMMARY")
        output.append("=" * 80)
        output.append(f"Total Sources: {sources.get('total_count', 0)}")
        output.append(f"Academic Sources: {sources.get('academic_sources', 0)}")
        output.append(f"Web Sources: {sources.get('web_sources', 0)}")
        output.append(f"Wikipedia: {sources.get('wikipedia_sources', 0)}")
        output.append(f"arXiv: {sources.get('arxiv_sources', 0)}")
        output.append(f"PubMed: {sources.get('pubmed_sources', 0)}")
        output.append(f"News: {sources.get('news_sources', 0)}")
        output.append(f"Patents: {sources.get('patent_sources', 0)}")
        output.append(f"Datasets: {sources.get('dataset_sources', 0)}")
        output.append(f"High Reliability: {sources.get('high_reliability', 0)}")
        output.append(f"Medium Reliability: {sources.get('medium_reliability', 0)}")
        output.append(f"Low Reliability: {sources.get('low_reliability', 0)}")
        output.append("")

        # Sources table
        source_list = sources.get("list", [])
        if source_list:
            output.append(f"{'#':<4} {'Title':<45} {'Type':<12} {'Rel.':<6}")
            output.append("-" * 70)
            for i, src in enumerate(source_list[:30], 1):
                title = src.get("title", "Untitled")[:43]
                src_type = src.get("type", "web")[:10]
                rel = src.get("reliability", "?")[:4]
                output.append(f"{i:<4} {title:<45} {src_type:<12} {rel:<6}")
            if len(source_list) > 30:
                output.append(f"  ... and {len(source_list) - 30} more sources")
        output.append("")
        output.append("-" * 80)
        output.append("")

        # ════════════════════════════════════════════════════
        #  SOURCE RELIABILITY DASHBOARD
        # ════════════════════════════════════════════════════
        if include_source_reliability:
            output.append("SOURCE RELIABILITY DASHBOARD")
            output.append("=" * 80)
            by_type = defaultdict(lambda: {"count": 0, "high": 0, "medium": 0, "low": 0})
            for src in source_list:
                stype = src.get("type", "unknown")
                by_type[stype]["count"] += 1
                rel = src.get("reliability", "Unknown")
                if rel == "High":
                    by_type[stype]["high"] += 1
                elif rel == "Medium":
                    by_type[stype]["medium"] += 1
                else:
                    by_type[stype]["low"] += 1

            output.append(f"{'Source Type':<18} {'Total':<8} {'High':<8} {'Med':<8} {'Low':<8} {'Ratio'}")
            output.append("-" * 70)
            for stype, counts in sorted(by_type.items(), key=lambda x: x[1]["count"], reverse=True):
                total = counts["count"]
                ratio = counts["high"] / total if total > 0 else 0
                bar = "█" * int(ratio * 20) + "░" * (20 - int(ratio * 20))
                output.append(f"{stype:<18} {total:<8} {counts['high']:<8} {counts['medium']:<8} {counts['low']:<8} {bar} {ratio*100:.0f}%")
            output.append("")
            output.append("-" * 80)
            output.append("")

        # ════════════════════════════════════════════════════
        #  CONFIDENCE SCORES
        # ════════════════════════════════════════════════════
        output.append("CONFIDENCE SCORES")
        output.append("=" * 80)
        for category, score in confidence.items():
            bar_len = int(score / 2)
            bar = "█" * bar_len + "░" * (50 - bar_len)
            cat_name = category.replace("_", " ").title()
            output.append(f"  {cat_name:<25} [{bar}] {score}%")
        output.append("")
        output.append("-" * 80)
        output.append("")

        # ════════════════════════════════════════════════════
        #  BIBLIOGRAPHY
        # ════════════════════════════════════════════════════
        if include_bibliography and source_list:
            output.append("BIBLIOGRAPHY")
            output.append("=" * 80)
            output.append(f"Style: {self.citation_style.upper()}")
            output.append("")
            bib = CitationManager.format_bibliography(source_list, self.citation_style)
            output.append(bib)
            output.append("")
            output.append("-" * 80)
            output.append("")

        # ════════════════════════════════════════════════════
        #  KNOWLEDGE GRAPH
        # ════════════════════════════════════════════════════
        if include_knowledge_graph:
            kg = json_data.get("knowledge_graph", {})
            if kg:
                output.append("KNOWLEDGE GRAPH")
                output.append("=" * 80)
                output.append(KnowledgeGraphBuilder.format_graph(kg))
                output.append("")
                output.append("-" * 80)
                output.append("")

        # ════════════════════════════════════════════════════
        #  SENTIMENT ANALYSIS
        # ════════════════════════════════════════════════════
        if include_sentiment:
            sentiment = json_data.get("sentiment", "")
            if sentiment:
                output.append("SENTIMENT ANALYSIS")
                output.append("=" * 80)
                output.append(sentiment)
                output.append("")
                output.append("-" * 80)
                output.append("")

        # ════════════════════════════════════════════════════
        #  BIAS DETECTION
        # ════════════════════════════════════════════════════
        if include_bias_check:
            bias = json_data.get("bias_analysis", "")
            if bias:
                output.append("BIAS DETECTION")
                output.append("=" * 80)
                output.append(bias)
                output.append("")
                output.append("-" * 80)
                output.append("")

        # ════════════════════════════════════════════════════
        #  FACT DENSITY
        # ════════════════════════════════════════════════════
        if include_fact_density:
            fd = json_data.get("fact_density", "")
            if fd:
                output.append("FACT DENSITY ANALYSIS")
                output.append("=" * 80)
                output.append(fd)
                output.append("")
                output.append("-" * 80)
                output.append("")

        # ════════════════════════════════════════════════════
        #  PEER REVIEW
        # ════════════════════════════════════════════════════
        if include_peer_review:
            pr = json_data.get("peer_review", {})
            if pr:
                output.append("PEER REVIEW")
                output.append("=" * 80)
                for review_title, content in pr.items():
                    output.append(f"  Reviewer: {review_title}")
                    output.append(f"  {content}")
                    output.append("")
                output.append("-" * 80)
                output.append("")

        # ════════════════════════════════════════════════════
        #  METHODOLOGY
        # ════════════════════════════════════════════════════
        output.append("RESEARCH METHODOLOGY")
        output.append("=" * 80)
        output.append(f"Approach: {methodology.get('approach', 'N/A')}")
        output.append(f"Sources Used: {methodology.get('sources_used', 'N/A')}")
        output.append(f"Agents Involved: {methodology.get('agents_involved', 0)}")
        output.append(f"Recursive Passes: {methodology.get('recursive_passes', 1)}")
        output.append(f"Memory Sharing: {methodology.get('memory_sharing', False)}")
        output.append("")
        output.append("Process:")
        for step in methodology.get("process", []):
            output.append(f"  {step}")
        output.append("")
        if methodology.get("limitations"):
            output.append("Methodological Limitations:")
            for lim in methodology.get("limitations", []):
                output.append(f"  • {lim}")
        output.append("")
        output.append("-" * 80)
        output.append("")

        # ════════════════════════════════════════════════════
        #  LIMITATIONS
        # ════════════════════════════════════════════════════
        if limitations:
            output.append("RESEARCH LIMITATIONS")
            output.append("=" * 80)
            for lim in limitations:
                output.append(f"  • {lim}")
            output.append("")
            output.append("-" * 80)
            output.append("")

        # ════════════════════════════════════════════════════
        #  SUGGESTIONS
        # ════════════════════════════════════════════════════
        if suggestions:
            output.append("SUGGESTED SUB-SEARCHES")
            output.append("=" * 80)
            for i, sug in enumerate(suggestions, 1):
                output.append(f"  {i}. {sug.get('query', 'N/A')}")
                output.append(f"     Reason: {sug.get('reason', 'N/A')}")
            output.append("")
            output.append("-" * 80)
            output.append("")

        # ════════════════════════════════════════════════════
        #  INDEX
        # ════════════════════════════════════════════════════
        if include_index:
            all_text = " ".join(s.get("content", "") for s in sections)
            terms = IndexGenerator.extract_terms(all_text)
            if terms:
                output.append("INDEX")
                output.append("=" * 80)
                output.append(IndexGenerator.format_index(terms))
                output.append("")
                output.append("-" * 80)
                output.append("")

        # ════════════════════════════════════════════════════
        #  APPENDIX
        # ════════════════════════════════════════════════════
        if include_appendix:
            output.append("APPENDIX")
            output.append("=" * 80)
            output.append("")
            output.append("Appendix A: Full Source List")
            output.append("-" * 40)
            for i, src in enumerate(source_list, 1):
                output.append(f"  A{i}. {src.get('title', 'Untitled')}")
                output.append(f"      URL: {src.get('url', 'N/A')}")
                output.append(f"      Type: {src.get('type', 'web')} | Reliability: {src.get('reliability', 'Unknown')}")
                if src.get("snippet"):
                    snippet = src["snippet"][:150]
                    output.append(f"      Snippet: {snippet}")
                output.append("")

            output.append("Appendix B: Raw Agent Outputs")
            output.append("-" * 40)
            agent_results = json_data.get("full_agent_data", {})
            for agent_type, data in agent_results.items():
                if data.get("result"):
                    output.append(f"  [{agent_type}] ({data.get('status', 'unknown')})")
                    output.append(f"  Provider: {data.get('provider', 'N/A')}")
                    output.append(f"  Duration: {data.get('duration_seconds', 'N/A')}s")
                    output.append(f"  Output: {data['result'][:300]}...")
                    output.append("")

            output.append("Appendix C: Glossary of Key Terms")
            output.append("-" * 40)
            all_text = " ".join(s.get("content", "") for s in sections)
            terms = IndexGenerator.extract_terms(all_text)
            for term in sorted(terms.keys(), key=str.lower)[:30]:
                # Find first mention in sections
                context = ""
                for section in sections:
                    content = section.get("content", "")
                    if term in content:
                        idx = content.find(term)
                        context = content[max(0, idx-30):idx+len(term)+50]
                        break
                if context:
                    output.append(f"  {term}: ...{context}...")
                else:
                    output.append(f"  {term}")
            output.append("")

            output.append("-" * 80)
            output.append("")

        # ════════════════════════════════════════════════════
        #  FOOTER
        # ════════════════════════════════════════════════════
        output.append("=" * 80)
        output.append(f"End of Research Paper — Generated by ks-eye v{meta.get('version', '2.0.0')}")
        output.append(f"KashSight Platform — {meta.get('generated_at', '')[:10]}")
        output.append("=" * 80)

        return "\n".join(output)

    def generate_complete_output(self, query, sources, agent_results, suggestions, title=None,
                                pass_summaries=None, branch_tree=None, total_passes=1,
                                branch_depth=0, total_duration=0, citation_style="apa",
                                include_toc=True, include_index=True, include_appendix=True,
                                include_bibliography=True, include_knowledge_graph=True,
                                include_sentiment=True, include_bias_check=True,
                                include_peer_review=True, include_fact_density=True,
                                include_source_reliability=True):
        self.citation_style = citation_style
        json_data = self.create_json_output(
            query, sources, agent_results, suggestions, title,
            pass_summaries, branch_tree, total_passes, branch_depth, total_duration,
        )
        text_output = self.format_text_output(
            json_data, include_toc, include_index, include_appendix,
            include_bibliography, include_knowledge_graph, include_sentiment,
            include_bias_check, include_peer_review, include_fact_density,
            include_source_reliability,
        )
        return json_data, text_output

    def save_text(self, text_data, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text_data)

    def save_json(self, json_data, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
