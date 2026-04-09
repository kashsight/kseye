"""
Parallel Agent Engine v2 for ks-eye
Auto-scaling, recursive passes, branching trees, memory sharing, streaming, caching
"""

import subprocess
import threading
import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from ks_eye import ALL_AGENTS, CORE_AGENTS, ADVANCED_AGENTS, DEFAULT_AGENT_PROVIDERS, RESEARCH_TEMPLATES
from ks_eye.engines.tgpt_engine import run_tgpt
from ks_eye.engines.scholar_search import comprehensive_search
from ks_eye.config import config
from ks_eye.ui import console


# ── Agent System Prompts (all 29) ──
AGENT_PROMPTS = {
    # Core 15
    "web_search": "You are ks-eye's Web Search Research Agent. Search the web comprehensively. Include multiple perspectives, recent developments, practical applications. Provide URLs where possible.",
    "academic_search": "You are ks-eye's Academic Search Agent. Focus on peer-reviewed research, academic papers, scholarly analysis. Cite sources with author names and publication years. Prioritize high-reliability academic sources.",
    "methodology_extractor": "You are ks-eye's Methodology Extraction Agent. Analyze research methodologies: approaches, data collection, sample sizes, analysis techniques, study limitations.",
    "citation_analyzer": "You are ks-eye's Citation Analysis Agent. Analyze citation patterns, impact, key papers, influential authors, field evolution. Note citation controversies or retractions.",
    "data_synthesis": "You are ks-eye's Data Synthesis Agent. Synthesize findings from multiple sources into coherent insights. Identify patterns, correlations, contradictions, gaps. Present data in structured analytical format.",
    "literature_review": "You are ks-eye's Literature Review Agent. Provide comprehensive literature review: historical context, major contributions, key debates, current state. Organize chronologically and thematically.",
    "trend_analysis": "You are ks-eye's Trend Analysis Agent. Analyze research trends: emerging patterns, future directions, growing interest areas, perspective shifts. Include statistical trends if available.",
    "counter_argument": "You are ks-eye's Counter-Argument Agent. Identify counter-arguments, alternative perspectives, critical viewpoints. Challenge assumptions, present evidence contradicting mainstream conclusions.",
    "reference_checker": "You are ks-eye's Reference Verification Agent. Verify accuracy and reliability of claims. Cross-reference sources, check consistency, flag unreliable or biased sources.",
    "summary_generator": "You are ks-eye's Summary Generation Agent. Create concise, clear summaries. Provide executive summary, key findings, bullet-point takeaways. Accessible but academically rigorous.",
    "outline_builder": "You are ks-eye's Outline Building Agent. Create detailed research paper outline: Introduction, Literature Review, Methodology, Results, Discussion, Conclusion, References with subsections.",
    "fact_checker": "You are ks-eye's Fact Checking Agent. Verify specific claims, statistics, data points. Flag inaccurate or misleading information. Provide corrected facts with sources.",
    "gap_analysis": "You are ks-eye's Gap Analysis Agent. Identify gaps and limitations in current research. What questions remain unanswered? What areas need more study? What methodological weaknesses exist?",
    "source_verification": "You are ks-eye's Source Verification Agent. Evaluate source credibility: author credentials, publication venues, funding sources, potential conflicts of interest.",
    "final_synthesis": "You are ks-eye's Final Synthesis Agent. Combine all findings into a comprehensive research paper. Formal academic style with proper citations. Include: Title, Abstract, Introduction, Literature Review, Methodology, Results, Discussion, Conclusion, References.",
    # Advanced 14
    "statistical_analysis": "You are ks-eye's Statistical Analysis Agent. Extract numbers, statistics, p-values, effect sizes from research. Create data tables and statistical summaries. Identify statistical significance patterns and methodological rigor of quantitative claims.",
    "timeline_generator": "You are ks-eye's Timeline Generator Agent. Extract chronological development of research. 'In YEAR, X discovered...' Format as a clear timeline showing how understanding evolved over decades.",
    "person_profiler": "You are ks-eye's Key Person Profiler Agent. Identify leading researchers in this field. Their publication history, affiliations, key contributions, h-index if available, collaboration networks.",
    "sentiment_analysis": "You are ks-eye's Sentiment Analysis Agent. Analyze the overall tone of research: optimistic, cautious, critical. How sentiment shifts across sub-topics. Identify areas of consensus vs. controversy.",
    "bias_detection": "You are ks-eye's Bias Detection Agent. Identify confirmation bias, selection bias, funding bias, publication bias. Check for political/corporate funding influence. Assess Western vs. non-Western perspective balance.",
    "fact_density_scorer": "You are ks-eye's Fact Density Scorer. Analyze what percentage of claims are backed by specific citations. Detect vague claims vs. evidence-backed statements. Score evidence density per topic area.",
    "peer_reviewer_1": "You are ks-eye's Peer Reviewer 1 (Methodology Focus). Critique the research methodology, sample sizes, statistical methods, reproducibility concerns. Provide constructive academic review feedback.",
    "peer_reviewer_2": "You are ks-eye's Peer Reviewer 2 (Literature Focus). Critique the literature coverage, identify missing key papers, assess whether conclusions follow from evidence. Provide constructive academic review feedback.",
    "knowledge_graph_builder": "You are ks-eye's Knowledge Graph Builder. Map relationships between concepts, authors, papers. Identify which papers cite which, topic clustering, conceptual dependencies.",
    "wikipedia_extractor": "You are ks-eye's Wikipedia Extraction Agent. Extract structured information from Wikipedia: overview, history, key figures, controversies, related topics. Use as grounding baseline.",
    "news_analyst": "You are ks-eye's News Analysis Agent. Analyze recent news coverage. Media sentiment, public discourse, how mainstream media portrays this topic vs. academic consensus.",
    "patent_searcher": "You are ks-eye's Patent Search Agent. Find patents related to this topic. Shows commercial/industry interest, patent citation networks, technology readiness levels.",
    "dataset_finder": "You are ks-eye's Dataset Finder Agent. Find public datasets related to this topic. Links to Kaggle, government data, research repositories. Assess data quality and availability.",
    "source_evaluator": "You are ks-eye's Source Evaluation Agent. Rate each source quality on 1-10 scale. Flag retracted papers, predatory journals, biased sources. Cross-reference claims across sources for consistency.",
}


class ResearchAgent:
    """Single research agent with memory support"""

    def __init__(self, agent_type, provider, query, custom_prompt=None, timeout=60, memory_context=None):
        self.agent_type = agent_type
        self.provider = provider
        self.query = query
        self.custom_prompt = custom_prompt
        self.timeout = timeout
        self.memory_context = memory_context or ""
        self.status = "idle"
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        self.sources = []

    def get_system_prompt(self):
        base = AGENT_PROMPTS.get(self.agent_type, "You are a research assistant.")
        if self.memory_context:
            base += f"\n\nContext from previous research passes:\n{self.memory_context}"
        if self.custom_prompt:
            base += f"\n\nAdditional instructions: {self.custom_prompt}"
        return base

    def run(self):
        self.status = "running"
        self.start_time = datetime.now()
        try:
            research_prompt = f"""
Research Topic: {self.query}

As the {self.agent_type.replace('_', ' ').title()}, provide comprehensive research and analysis.

Requirements:
1. Be thorough and detailed
2. Cite specific sources where possible
3. Include data, statistics, and evidence
4. Note any limitations or uncertainties
5. Provide actionable insights

Please provide your complete analysis:"""
            response = run_tgpt(
                message=research_prompt,
                provider=self.provider,
                system_prompt=self.get_system_prompt(),
                timeout=self.timeout,
            )
            if response:
                self.result = response
                self.status = "completed"
            else:
                self.error = "No response from AI provider"
                self.status = "error"
        except Exception as e:
            self.error = str(e)
            self.status = "error"
        self.end_time = datetime.now()
        return self.result

    def to_dict(self):
        return {
            "agent_type": self.agent_type,
            "provider": self.provider,
            "query": self.query,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (
                (self.end_time - self.start_time).total_seconds()
                if self.start_time and self.end_time else None
            ),
            "sources": self.sources,
        }


class ParallelAgentEngine:
    """
    Manages parallel agent execution with:
    - Auto-scaling based on query complexity
    - Recursive multi-pass research
    - Branching research trees
    - Memory/context sharing between agents
    - Streaming output
    - Caching
    - Resume from interruption
    """

    def __init__(self, max_workers=29, streaming_callback=None):
        self.max_workers = max_workers
        self.agents = []
        self.results = {}
        self.errors = {}
        self.streaming_callback = streaming_callback
        self.all_sources = []
        self.branch_tree = {"query": "", "branches": []}
        self.pass_results = {}

    def _stream_update(self, message, agent_type=None, status=None):
        """Send streaming update"""
        if self.streaming_callback:
            self.streaming_callback(message, agent_type, status)

    def _assess_complexity(self, query):
        """Assess query complexity to determine agent scaling"""
        words = query.split()
        score = 0
        # Length factor
        score += min(len(words) * 2, 20)
        # Technical terms
        tech_indicators = ["algorithm", "neural", "quantum", "machine", "deep",
                          "analysis", "systematic", "meta", "comparative", "evaluation"]
        for term in tech_indicators:
            if term in query.lower():
                score += 5
        # Multi-topic detection
        if any(c in query for c in [' and ', ' vs ', ' versus ', ' compared ', ' between ']):
            score += 10
        # Complexity levels
        if score >= 30:
            return "very_high"
        elif score >= 20:
            return "high"
        elif score >= 10:
            return "medium"
        return "low"

    def _select_agents_auto(self, query):
        """Auto-select agents based on query complexity"""
        complexity = self._assess_complexity(query)
        from ks_eye import ALL_AGENTS, CORE_AGENTS
        if complexity == "very_high":
            return ALL_AGENTS
        elif complexity == "high":
            return CORE_AGENTS + ADVANCED_AGENTS[:8]
        elif complexity == "medium":
            return CORE_AGENTS + ["statistical_analysis", "timeline_generator", "sentiment_analysis"]
        return CORE_AGENTS[:10]

    def create_agents(self, query, selected_agents=None, custom_providers=None, memory_context=None):
        self.agents = []
        agents_to_use = selected_agents or CORE_AGENTS
        for agent_type in agents_to_use:
            provider = config.get_agent_provider(agent_type)
            if custom_providers and agent_type in custom_providers:
                provider = custom_providers[agent_type]
            agent = ResearchAgent(
                agent_type=agent_type,
                provider=provider,
                query=query,
                custom_prompt=None,
                timeout=config.get("agent_timeout", 60),
                memory_context=memory_context,
            )
            self.agents.append(agent)
        return self.agents

    def run_parallel(self, streaming=False):
        """Run agents in parallel with optional streaming"""
        results = {}
        completed_count = 0
        total = len(self.agents)

        def run_single_agent(agent):
            result = agent.run()
            if streaming:
                self._stream_update(
                    f"{agent.agent_type.replace('_', ' ').title()}: {'COMPLETED' if agent.status == 'completed' else 'FAILED'}",
                    agent_type=agent.agent_type,
                    status=agent.status,
                )
            return agent

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(run_single_agent, agent): agent for agent in self.agents}
            for future in as_completed(futures):
                agent = future.result()
                results[agent.agent_type] = agent.to_dict()
                completed_count += 1
                if agent.status == "completed":
                    if not streaming:
                        console.print(f"[green]✓ {agent.agent_type} completed[/green]")
                else:
                    if not streaming:
                        console.print(f"[red]✗ {agent.agent_type} failed: {agent.error}[/red]")

        self.results = results
        return results

    def build_memory_context(self, pass_results):
        """Build memory context from previous pass results for agent sharing"""
        context_parts = []
        for agent_type, data in pass_results.items():
            if data.get("status") == "completed" and data.get("result"):
                # Summarize for context (first 500 chars)
                summary = data["result"][:500]
                context_parts.append(f"[{agent_type}]: {summary}")
        return "\n\n".join(context_parts)

    def generate_sub_queries(self, query, results, max_branches=5):
        """Generate sub-queries for branching research from current results"""
        sub_queries = []
        completed = {k: v for k, v in results.items() if v.get("status") == "completed"}

        # Ask an agent to suggest sub-topics
        summary_data = completed.get("summary_generator", {})
        gap_data = completed.get("gap_analysis", {})

        if summary_data.get("result"):
            # Extract potential sub-topics from summary
            import re
            topics = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', summary_data["result"])
            for topic in list(set(topics))[:max_branches]:
                sub_queries.append(f"{topic} in relation to {query}")

        if gap_data.get("result"):
            # Extract gaps as sub-queries
            import re
            gaps = re.findall(r'[^.]*?(?:lack|need|gap|unclear|unknown|understudied)[^.]*\.', gap_data["result"], re.IGNORECASE)
            for gap in gaps[:max_branches]:
                sub_queries.append(f"Addressing gap: {gap.strip()} in {query}")

        # Default sub-queries if none extracted
        if not sub_queries:
            sub_queries = [
                f"Recent developments in {query}",
                f"Critical analysis of {query}",
                f"Future directions for {query}",
            ]

        return sub_queries[:max_branches]

    def run_with_passes(self, query, selected_agents=None, passes=2,
                        auto_scale=True, branch_depth=0, max_branches=5,
                        memory_sharing=True, run_web_search=True,
                        source_filter=None, custom_providers=None,
                        streaming=False):
        """
        Run research with recursive passes and optional branching

        Args:
            query: Research query
            selected_agents: List of agent types (None = auto or default)
            passes: Number of recursive passes (1-5)
            auto_scale: Auto-select agents based on complexity
            branch_depth: How deep to branch into sub-queries (0 = no branching)
            max_branches: Max branches per level
            memory_sharing: Agents share context from previous passes
            run_web_search: Run web search before agents
            source_filter: Filter source types
            custom_providers: Provider overrides

        Returns:
            Full research output dict
        """
        total_start = datetime.now()
        all_agent_results = {}
        all_sources = []
        pass_summaries = {}
        branch_tree = {"query": query, "depth": 0, "branches": []}

        # ── Step 1: Web/Academic Search ──
        if run_web_search:
            self._stream_update("Running comprehensive source search...")
            if not streaming:
                console.print("[cyan]🔍 Running comprehensive source search...[/cyan]")
            max_src = config.get("max_sources_per_query", 20)
            # Scale up for deep research
            if passes > 2:
                max_src = max_src * 2
            sources = comprehensive_search(query, max_sources=max_src, source_filter=source_filter)
            all_sources.extend(sources)
            self._stream_update(f"Found {len(sources)} sources")
            if not streaming:
                console.print(f"[green]✓ Found {len(sources)} sources[/green]")

        # ── Step 2: Select Agents ──
        if selected_agents is None:
            if auto_scale:
                agents_to_use = self._assess_complexity(query)
                agent_list = self._select_agents_auto(query)
            else:
                from ks_eye import CORE_AGENTS
                agent_list = CORE_AGENTS
        else:
            agent_list = selected_agents

        # ── Step 3: Recursive Passes ──
        memory_context = None
        for pass_num in range(1, passes + 1):
            self._stream_update(f"Starting pass {pass_num}/{passes}", status="running")
            if not streaming:
                console.print(f"\n[cyan]{'='*60}[/cyan]")
                console.print(f"[bold cyan]📊 Research Pass {pass_num}/{passes}[/bold cyan]")
                console.print(f"[cyan]{'='*60}[/cyan]\n")

            # Check cache
            cache_hit = False
            if config.get("cache_enabled", True):
                cache_key = config.cache_key(query, f"pass{pass_num}", 1)
                cached = config.cache_get(cache_key)
                if cached:
                    self._stream_update(f"Pass {pass_num}: Cache HIT")
                    if not streaming:
                        console.print(f"[yellow]⚡ Pass {pass_num}: Using cached results[/yellow]")
                    pass_results = cached
                    cache_hit = True

            if not cache_hit:
                # Create agents with memory from previous pass
                ctx = memory_context if memory_sharing and pass_num > 1 else None
                self.create_agents(query, agent_list, custom_providers, memory_context=ctx)

                # Run
                streaming_on = config.get("streaming", False) or bool(self.streaming_callback)
                pass_results = self.run_parallel(streaming=streaming_on)

                # Cache results
                if config.get("cache_enabled", True):
                    config.cache_set(cache_key, pass_results)

            pass_summaries[f"pass_{pass_num}"] = pass_results

            # Merge results
            for agent_type, result in pass_results.items():
                if agent_type not in all_agent_results:
                    all_agent_results[agent_type] = result
                else:
                    # Append new results
                    existing = all_agent_results[agent_type]
                    if result.get("status") == "completed":
                        existing["result"] = result.get("result", existing.get("result", ""))
                        existing["status"] = "completed"

            # Build memory for next pass
            if memory_sharing and pass_num < passes:
                memory_context = self.build_memory_context(pass_results)

        # ── Step 4: Branching (if depth > 0) ──
        if branch_depth > 0:
            self._run_branching(query, branch_tree, agent_list, passes=1,
                              depth=0, max_depth=branch_depth, max_branches=max_branches,
                              memory_sharing=memory_sharing, custom_providers=custom_providers,
                              all_sources=all_sources, all_agent_results=all_agent_results)

        # ── Step 5: Compile Output ──
        total_duration = (datetime.now() - total_start).total_seconds()

        output = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "sources": all_sources,
            "sources_count": len(all_sources),
            "agent_results": all_agent_results,
            "pass_summaries": pass_summaries,
            "branch_tree": branch_tree,
            "agents_completed": sum(1 for r in all_agent_results.values() if r.get("status") == "completed"),
            "agents_failed": sum(1 for r in all_agent_results.values() if r.get("status") == "error"),
            "total_passes": passes,
            "branch_depth": branch_depth,
            "total_duration_seconds": total_duration,
        }

        return output, all_sources

    def _run_branching(self, parent_query, branch_tree, agents, passes=1,
                       depth=0, max_depth=3, max_branches=5,
                       memory_sharing=True, custom_providers=None,
                       all_sources=None, all_agent_results=None):
        """Recursively branch into sub-topics"""
        if depth >= max_depth:
            return

        # Generate sub-queries
        sub_queries = self.generate_sub_queries(parent_query, all_agent_results or {}, max_branches)

        for sub_query in sub_queries:
            branch_node = {"query": sub_query, "depth": depth + 1, "branches": []}
            branch_tree["branches"].append(branch_node)

            self._stream_update(f"Branch (depth {depth+1}): {sub_query[:60]}...", status="running")
            if not streaming:
                console.print(f"\n[dim]└─ Branch (depth {depth+1}): {sub_query[:60]}...[/dim]")

            # Run research on sub-query
            branch_output, branch_sources = self.run_with_passes(
                query=sub_query,
                selected_agents=agents,
                passes=passes,
                auto_scale=False,
                branch_depth=0,  # No further branching within branches
                memory_sharing=memory_sharing,
                run_web_search=True,
                custom_providers=custom_providers,
            )

            branch_node["results"] = branch_output

            # Merge branch sources and results
            if all_sources is not None:
                all_sources.extend(branch_sources)
            if all_agent_results is not None:
                for agent_type, result in branch_output.get("agent_results", {}).items():
                    key = f"{agent_type}_branch_{sub_query[:30]}"
                    all_agent_results[key] = result

    def get_agent_status(self):
        return [
            {
                "name": a.agent_type.replace("_", " ").title(),
                "provider": a.provider,
                "status": a.status,
                "progress": "████████████████████" if a.status == "completed" else "░░░░░░░░░░░░░░░░░░░░" if a.status == "idle" else "████████░░░░░░░░░░░░",
            }
            for a in self.agents
        ]
