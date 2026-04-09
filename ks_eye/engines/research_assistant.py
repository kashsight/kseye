"""
ks-eye Research Assistant Engine v3
Human-in-the-loop: step-by-step guided research workflow
Auto-creates folder per session, saves everything as .txt
"""

import json
import os
import re
import shutil
from datetime import datetime

from ks_eye.engines.tgpt_engine import run_tgpt
from ks_eye.engines.scholar_search import comprehensive_search, search_wikipedia
from ks_eye.config import config
from ks_eye.ui import console


def _safe_foldername(name):
    """Convert any string to a safe folder name"""
    # Remove dangerous chars
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    safe = safe.strip().strip('. ')
    if not safe:
        safe = 'unnamed_research'
    # Limit length
    if len(safe) > 80:
        safe = safe[:80].rstrip('_')
    return safe


def _txt_box(title, content, width=78):
    """Wrap content in a text box with title"""
    lines = ["=" * width, title.upper().center(width), "=" * width, ""]
    # Split long content into lines
    for paragraph in content.split("\n"):
        if len(paragraph) > width:
            # Word wrap
            words = paragraph.split()
            current = ""
            for w in words:
                if len(current) + len(w) + 1 <= width:
                    current += " " + w if current else w
                else:
                    lines.append(current)
                    current = w
            if current:
                lines.append(current)
        else:
            lines.append(paragraph)
    lines.append("")
    lines.append("=" * width)
    return "\n".join(lines)


class ResearchSession:
    """
    Manages a research session with folder-based storage.
    Each session gets its own folder with all files saved as .txt
    """

    def __init__(self, base_dir=None):
        self.base_dir = base_dir or config.RESEARCH_DIR
        self.folder = None
        self.session_file = None
        self.state = {
            "step": "topic_definition",
            "topic": "",
            "objectives": [],
            "population": "",
            "scope": "",
            "proposal": {},
            "questionnaire": {},
            "collected_data": None,
            "analysis_results": {},
            "literature_sources": [],
            "literature_review": "",
            "report_sections": {},
            "final_output": "",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    def create_session(self, topic):
        """Create a new research folder and save initial state"""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = _safe_foldername(topic)
        folder_name = f"{ts}_{safe_topic}"
        self.folder = os.path.join(self.base_dir, folder_name)
        os.makedirs(self.folder, exist_ok=True)

        # Create subdirectories
        os.makedirs(os.path.join(self.folder, "data"), exist_ok=True)
        os.makedirs(os.path.join(self.folder, "sources"), exist_ok=True)

        self.session_file = os.path.join(self.folder, "session.json")
        self.state["topic"] = topic
        self.state["created_at"] = datetime.now().isoformat()
        self._save_state()

        # Create a README in the folder
        readme = (
            f"Research Session: {topic}\n"
            f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Tool: ks-eye v{__import__('ks_eye').__version__}\n\n"
            "Folder structure:\n"
            "  session.json        — Full session state\n"
            "  proposal.txt        — Research proposal\n"
            "  questionnaire.txt   — Questionnaire (human-readable)\n"
            "  questionnaire.json  — Questionnaire (JSON, for import)\n"
            "  collected_data.json — Raw collected response data\n"
            "  analysis.txt        — Data analysis results\n"
            "  literature.txt      — Literature review\n"
            "  sources.json        — List of academic sources\n"
            "  report.txt          — Final compiled report\n"
            "  data/               — Intermediate data files\n"
            "  sources/            — Individual source details\n"
        )
        with open(os.path.join(self.folder, "README.txt"), "w") as f:
            f.write(readme)

        return self.folder

    def _save_state(self):
        """Save session state to JSON"""
        self.state["updated_at"] = datetime.now().isoformat()
        if self.session_file:
            with open(self.session_file, "w") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)

    def save_txt(self, filename, content):
        """Save any content as .txt in the session folder"""
        if not self.folder:
            raise RuntimeError("No active session. Define topic first.")
        filepath = os.path.join(self.folder, filename)
        if isinstance(content, dict):
            content = json.dumps(content, indent=2, ensure_ascii=False)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(str(content))
        return filepath

    def save_proposal(self, text):
        """Save proposal as formatted .txt"""
        txt = _txt_box("Research Proposal", text)
        self.state["proposal"] = {"text": text, "status": "pending_review"}
        self._save_state()
        return self.save_txt("proposal.txt", txt)

    def save_questionnaire(self, json_data):
        """Save questionnaire as both .txt (readable) and .json"""
        self.state["questionnaire"] = {"data": json_data, "status": "pending_review"}
        self._save_state()

        # Human-readable .txt
        lines = []
        title = json_data.get("title", "Research Questionnaire")
        desc = json_data.get("description", "")
        lines.append(_txt_box("Research Questionnaire", title))
        lines.append("")
        if desc:
            lines.append("INSTRUCTIONS")
            lines.append("-" * 40)
            lines.append(desc)
            lines.append("")
        for section in json_data.get("sections", []):
            lines.append("")
            lines.append(f"SECTION: {section.get('section_name', 'Untitled')}")
            lines.append("-" * 60)
            for q in section.get("questions", []):
                qid = q.get("id", "?")
                qtext = q.get("text", "")
                qtype = q.get("type", "")
                options = q.get("options", [])
                required = q.get("required", False)
                lines.append(f"\n  {qid}. [{qtype.upper()}] {qtext}")
                if options:
                    for i, opt in enumerate(options, 1):
                        lines.append(f"     {i}. {opt}")
                if required:
                    lines.append(f"     * Required")
            lines.append("")
        lines.append("=" * 78)

        txt_content = "\n".join(lines)
        self.save_txt("questionnaire.txt", txt_content)
        self.save_txt("questionnaire.json", json.dumps(json_data, indent=2))
        return os.path.join(self.folder, "questionnaire.txt")

    def save_collected_data(self, data):
        """Save collected response data"""
        self.state["collected_data"] = data
        self._save_state()
        return self.save_txt("data/collected_data.json", json.dumps(data, indent=2))

    def save_analysis(self, text):
        """Save analysis as .txt"""
        txt = _txt_box("Data Analysis", text)
        self.state["analysis_results"] = {"text": text, "status": "pending_review"}
        self._save_state()
        return self.save_txt("analysis.txt", txt)

    def save_literature(self, sources_list, review_text):
        """Save literature review and sources"""
        self.state["literature_sources"] = sources_list
        self.state["literature_review"] = review_text
        self._save_state()

        # Save sources list
        src_lines = ["=" * 78, "RESEARCH SOURCES".center(78), "=" * 78, ""]
        for i, s in enumerate(sources_list, 1):
            src_lines.append(f"[{i}] {s.get('title', 'Untitled')}")
            src_lines.append(f"    Source: {s.get('source', '?')} | Type: {s.get('type', '?')}")
            src_lines.append(f"    Reliability: {s.get('reliability', '?')}")
            if s.get('url'):
                src_lines.append(f"    URL: {s['url']}")
            if s.get('snippet'):
                src_lines.append(f"    Summary: {s['snippet'][:150]}")
            src_lines.append("")
        self.save_txt("sources/list.txt", "\n".join(src_lines))

        # Save literature review
        txt = _txt_box("Literature Review", review_text)
        return self.save_txt("literature.txt", txt)

    def save_report_section(self, section_key, text):
        """Save individual report section"""
        if "report_sections" not in self.state:
            self.state["report_sections"] = {}
        self.state["report_sections"][section_key] = {"text": text, "status": "approved"}
        self._save_state()

        filename = section_key.replace("_", "_") + ".txt"
        txt = _txt_box(section_key.replace("_", " "), text)
        return self.save_txt(f"sections/{filename}", txt)

    def save_final_report(self, text):
        """Save final compiled report"""
        self.state["final_output"] = text
        self.state["step"] = "complete"
        self._save_state()
        return self.save_txt("report.txt", text)

    def load_session(self, folder_path):
        """Load a session from an existing folder"""
        self.folder = folder_path
        self.session_file = os.path.join(folder_path, "session.json")
        if os.path.exists(self.session_file):
            with open(self.session_file, "r") as f:
                self.state = json.load(f)
        return self.state

    @staticmethod
    def list_sessions(base_dir=None):
        """List all existing research folders"""
        base = base_dir or config.RESEARCH_DIR
        if not os.path.exists(base):
            return []
        sessions = []
        for name in sorted(os.listdir(base)):
            folder = os.path.join(base, name)
            if os.path.isdir(folder):
                session_file = os.path.join(folder, "session.json")
                if os.path.exists(session_file):
                    try:
                        with open(session_file, "r") as f:
                            state = json.load(f)
                        sessions.append({
                            "folder": folder,
                            "name": name,
                            "topic": state.get("topic", "Unknown"),
                            "step": state.get("step", "unknown"),
                            "created": state.get("created_at", ""),
                            "has_report": os.path.exists(os.path.join(folder, "report.txt")),
                        })
                    except (json.JSONDecodeError, IOError):
                        pass
        return sessions


class ResearchAssistant:
    """
    Step-by-step research assistant.
    AI suggests, human decides. Never fully automated.
    Uses ResearchSession for folder-based .txt storage.
    """

    def __init__(self):
        self.session = ResearchSession()

    # ════════════════════════════════════════════════════
    #  STEP 1: TOPIC DEFINITION
    # ════════════════════════════════════════════════════

    def step_topic(self, user_input=None):
        """
        Step 1: Define the research topic
        AI asks guiding questions, human provides answers
        """
        if not user_input:
            return {
                "step": "topic_definition",
                "status": "awaiting_input",
                "prompt": (
                    "Let's define your research topic.\n\n"
                    "Please tell me:\n"
                    "  1. What is your research topic?\n"
                    "  2. What are your main objectives? (separate with commas)\n"
                    "  3. Who is your target population?\n"
                    "  4. What is the scope/context? (geographic, industry, etc.)\n\n"
                    "Example:\n"
                    "  Topic: Impact of mobile learning on student performance\n"
                    "  Objectives: Assess effectiveness, identify barriers, measure satisfaction\n"
                    "  Population: High school students aged 14-18\n"
                    "  Scope: Urban schools in Nairobi, Kenya"
                ),
            }

        # Parse user input — supports both labeled and unlabeled formats
        lines = [l.strip() for l in user_input.strip().split("\n") if l.strip()]
        topic = ""
        objectives = []
        population = ""
        scope = ""

        for line in lines:
            lower = line.lower()
            if lower.startswith("topic:"):
                topic = line.split(":", 1)[1].strip()
            elif lower.startswith("objectives:") or lower.startswith("objective:"):
                objectives = [o.strip() for o in line.split(":", 1)[1].split(",") if o.strip()]
            elif lower.startswith("population:"):
                population = line.split(":", 1)[1].strip()
            elif lower.startswith("scope:"):
                scope = line.split(":", 1)[1].strip()
            elif not topic:
                # First unlabeled line = topic
                topic = line
            elif not objectives:
                objectives = [o.strip() for o in line.split(",") if o.strip()]
            elif not population:
                population = line
            elif not scope:
                scope = line

        if not topic:
            return {"step": "topic_definition", "status": "error", "message": "Topic cannot be empty"}

        # Create the research folder
        self.session.create_session(topic)
        self.session.state["objectives"] = objectives
        self.session.state["population"] = population
        self.session.state["scope"] = scope
        self.session.state["step"] = "proposal_generation"
        self.session._save_state()

        return {
            "step": "topic_definition",
            "status": "completed",
            "next_step": "proposal_generation",
            "topic": topic,
            "objectives": objectives,
            "population": population,
            "scope": scope,
            "message": f"Topic saved: {topic}. Next: I'll draft a research proposal for your review.",
        }

    # ════════════════════════════════════════════════════
    #  STEP 2: PROPOSAL GENERATION
    # ════════════════════════════════════════════════════

    def step_proposal(self, action="draft", user_edits=None):
        """Step 2: Generate research proposal. AI drafts, human reviews and edits."""
        if action == "draft":
            topic = self.session.state.get("topic", "")
            objectives = self.session.state.get("objectives", [])
            population = self.session.state.get("population", "")
            scope = self.session.state.get("scope", "")

            if not topic:
                return {"status": "error", "message": "Please define your topic first (Step 1)"}

            prompt = (
                "You are a research assistant helping draft a research proposal.\n\n"
                "Research Topic: {}\n"
                "Objectives: {}\n"
                "Target Population: {}\n"
                "Scope/Context: {}\n\n"
                "Draft a comprehensive research proposal with these sections:\n"
                "1. Introduction and Background\n"
                "2. Problem Statement\n"
                "3. Research Questions (3-5 specific questions)\n"
                "4. Research Objectives (SMART format)\n"
                "5. Significance of the Study\n"
                "6. Scope and Limitations\n"
                "7. Proposed Methodology (suggest survey/questionnaire approach)\n"
                "8. Timeline (realistic phases)\n"
                "9. Expected Outcomes\n\n"
                "Format as clear, professional text. Be specific to this topic."
            ).format(topic, ", ".join(objectives), population, scope)

            proposal_text = run_tgpt(
                message=prompt,
                provider=config.get_agent_provider("final_synthesis"),
                timeout=60,
            )

            if not proposal_text:
                self.session.state["proposal"] = {
                    "text": "",
                    "status": "manual_entry",
                }
                self.session._save_state()
                return {
                    "step": "proposal_generation",
                    "status": "manual_entry",
                    "proposal": None,
                    "ai_available": False,
                    "message": (
                        "AI proposal generation is unavailable (tgpt not installed).\n\n"
                        "Options:\n"
                        "  1. Type your own proposal text below\n"
                        "  2. Type 'skip' to move to questionnaire design"
                    ),
                }

            filepath = self.session.save_proposal(proposal_text)
            return {
                "step": "proposal_generation",
                "status": "awaiting_review",
                "proposal": proposal_text,
                "message": (
                    "Proposal drafted above. Review and choose:\n"
                    "  - 'approve' — accept as-is\n"
                    "  - 'edit: [changes]' — request modifications\n"
                    "  - 'regenerate' — fresh draft"
                ),
            }

        elif action == "approve":
            if self.session.state["proposal"].get("text"):
                self.session.state["proposal"]["status"] = "approved"
                self.session.state["step"] = "questionnaire_design"
                self.session._save_state()
                return {
                    "step": "proposal_generation",
                    "status": "approved",
                    "next_step": "questionnaire_design",
                    "message": "Proposal approved! Next: questionnaire design.",
                }
            return {"status": "error", "message": "No proposal to approve. Draft first."}

        elif action == "edit" and user_edits:
            current = self.session.state["proposal"].get("text", "")
            prompt = (
                "Here is a research proposal draft:\n\n{}\n\n"
                "The reviewer requested these changes:\n{}\n\n"
                "Return the FULL revised proposal incorporating these changes."
            ).format(current, user_edits)
            revised = run_tgpt(
                message=prompt,
                provider=config.get_agent_provider("final_synthesis"),
                timeout=60,
            )
            if revised:
                filepath = self.session.save_proposal(revised)
                self.session.state["proposal"]["status"] = "pending_review"
                return {
                    "step": "proposal_generation",
                    "status": "revised",
                    "proposal": revised,
                    "message": "Proposal revised. Please review again.",
                }
            return {"status": "error", "message": "Failed to revise proposal."}

        elif action == "regenerate":
            return self.step_proposal("draft")

        return {"status": "error", "message": "Invalid action. Use: draft, approve, edit, regenerate"}

    # ════════════════════════════════════════════════════
    #  STEP 3: QUESTIONNAIRE DESIGN
    # ════════════════════════════════════════════════════

    def step_questionnaire(self, action="draft", user_edits=None):
        """
        Step 3: Design questionnaire
        AI generates JSON questionnaire, human reviews and modifies
        """
        if action == "draft":
            topic = self.session.state.get("topic", "")
            objectives = self.session.state.get("objectives", [])
            proposal = self.session.state.get("proposal", {}).get("text", "")

            if not topic:
                return {"status": "error", "message": "Please define topic first"}

            # Extract research questions from proposal if available
            rq_section = ""
            if "Research Questions" in proposal:
                idx = proposal.find("Research Questions")
                rq_section = proposal[idx:idx+500]

            prompt = f"""You are designing a data collection questionnaire.

Research Topic: {topic}
Objectives: {', '.join(objectives)}
{rq_section}

Create a complete questionnaire in JSON format. The JSON must have this exact structure:

{{
  "title": "Questionnaire Title",
  "description": "Brief description and instructions for respondents",
  "sections": [
    {{
      "section_name": "Section Name (e.g., Demographics, Main Survey, etc.)",
      "questions": [
        {{
          "id": "Q1",
          "type": "multiple_choice|likert_scale|yes_no|open_ended|ranking|matrix|demographic",
          "text": "The question text",
          "options": ["option A", "option B", "option C"],
          "required": true,
          "hint": "Optional hint for respondents"
        }}
      ]
    }}
  ]
}}

Requirements:
- Include a demographics section (age, gender, education, etc.)
- Include 15-25 substantive questions aligned with research objectives
- Use appropriate question types (likert scales for attitudes, multiple choice for behaviors, open-ended for opinions)
- Questions should be clear, unbiased, and specific
- Logical flow from general to specific

Return ONLY valid JSON, no extra text."""

            questionnaire_json = run_tgpt(
                message=prompt,
                provider=config.get_agent_provider("outline_builder"),
                timeout=60,
            )

            if questionnaire_json:
                # Try to extract JSON from response
                parsed = self._extract_json(questionnaire_json)
                if parsed:
                    filepath = self.session.save_questionnaire(parsed)
                    return {
                        "step": "questionnaire_design",
                        "status": "awaiting_review",
                        "questionnaire_json": json.dumps(parsed, indent=2),
                        "message": (
                            "Questionnaire designed and saved as .txt and .json.\n\n"
                            "Review the questionnaire above and choose:\n"
                            "  - 'approve' — questions look good\n"
                            "  - 'edit: [changes]' — add/remove/modify\n"
                            "  - 'regenerate' — try again"
                        ),
                    }
                else:
                    return {"status": "error", "message": "Failed to parse questionnaire JSON from AI response."}
            else:
                return {"status": "error", "message": "Failed to generate questionnaire."}

        elif action == "approve":
            if self.session.state["questionnaire"].get("data"):
                self.session.state["questionnaire"]["status"] = "approved"
                self.session.state["step"] = "data_collection"
                self.session._save_state()
                q = self.session.state["questionnaire"]["data"]
                questionnaire_str = json.dumps(q, indent=2)

                return {
                    "step": "questionnaire_design",
                    "status": "approved",
                    "next_step": "data_collection",
                    "export_json": questionnaire_str,
                    "message": (
                        "Questionnaire approved and exported above as JSON!\n\n"
                        "NEXT STEPS (you do this offline):\n"
                        "  1. Copy the JSON questionnaire above\n"
                        "  2. Create your survey (Google Forms, SurveyMonkey, paper, etc.)\n"
                        "  3. Distribute to your target population\n"
                        "  4. Collect responses\n"
                        "  5. Format responses as JSON (same structure)\n"
                        "  6. Come back to ks-eye and paste the collected data\n\n"
                        "When ready, proceed to Step 4: Data Collection"
                    ),
                }
            return {"status": "error", "message": "No questionnaire to approve."}

        elif action == "edit" and user_edits:
            current = json.dumps(self.session.state["questionnaire"].get("data", {}), indent=2)
            prompt = f"""Here is a questionnaire in JSON format:

{current}

Please modify it according to these instructions:
{user_edits}

Return the FULL modified JSON questionnaire."""

            revised = run_tgpt(
                message=prompt,
                provider=config.get_agent_provider("outline_builder"),
                timeout=60,
            )

            if revised:
                parsed = self._extract_json(revised)
                if parsed:
                    self.session.save_questionnaire(parsed)
                    self.session.state["questionnaire"]["status"] = "pending_review"
                    return {
                        "step": "questionnaire_design",
                        "status": "revised",
                        "questionnaire_json": json.dumps(parsed, indent=2),
                        "message": "Questionnaire revised. Please review again.",
                    }
            return {"status": "error", "message": "Failed to revise questionnaire."}

        elif action == "regenerate":
            return self.step_questionnaire("draft")

        return {"status": "error", "message": "Invalid action. Use: draft, approve, edit, regenerate"}

    # ════════════════════════════════════════════════════
    #  STEP 4: DATA COLLECTION (Human pastes data)
    # ════════════════════════════════════════════════════

    def step_data_collection(self, action="receive", data_json=None):
        """
        Step 4: Human pastes collected data, AI validates it
        """
        if action == "receive":
            if not data_json:
                return {
                    "step": "data_collection",
                    "status": "awaiting_input",
                    "prompt": (
                        "Step 4: Data Collection\n\n"
                        "Please paste your collected data as JSON.\n\n"
                        "The data should match your questionnaire structure.\n"
                        "Expected format:\n"
                        '{\n'
                        '  "responses": [\n'
                        '    {\n'
                        '      "respondent_id": "R001",\n'
                        '      "demographics": { ... },\n'
                        '      "answers": { "Q1": "value", "Q2": "value", ... }\n'
                        '    },\n'
                        '    ...\n'
                        '  ]\n'
                        '}\n\n'
                        "Paste your JSON data below:"
                    ),
                }

            # Validate and store
            parsed = None
            if isinstance(data_json, dict):
                parsed = data_json
            elif isinstance(data_json, str):
                parsed = self._extract_json(data_json)

            if parsed:
                response_count = 0
                if "responses" in parsed:
                    response_count = len(parsed["responses"])
                elif "data" in parsed:
                    response_count = len(parsed["data"])
                elif isinstance(parsed, list):
                    response_count = len(parsed)

                self.session.save_collected_data(parsed)
                self.session.state["response_count"] = response_count
                self.session.state["step"] = "data_analysis"

                return {
                    "step": "data_collection",
                    "status": "received",
                    "next_step": "data_analysis",
                    "response_count": response_count,
                    "message": (
                        f"Data received: {response_count} responses detected.\n\n"
                        "Next: I'll analyze this data. Proceed to Step 5."
                    ),
                }
            else:
                return {
                    "status": "error",
                    "message": (
                        "Could not parse JSON data. Please ensure:\n"
                        "  - It's valid JSON format\n"
                        "  - Uses double quotes for keys/strings\n"
                        "  - No trailing commas\n\n"
                        "Tip: Use a JSON validator before pasting."
                    ),
                }

        return {"status": "error", "message": "Invalid action. Use: receive"}

    # ════════════════════════════════════════════════════
    #  STEP 5: DATA ANALYSIS
    # ════════════════════════════════════════════════════

    def step_data_analysis(self, action="analyze", user_direction=None):
        """
        Step 5: AI analyzes collected data, human guides
        """
        if action == "analyze":
            data = self.session.state.get("collected_data")
            if not data:
                return {"status": "error", "message": "No data collected yet. Complete Step 4 first."}

            topic = self.session.state.get("topic", "")
            objectives = self.session.state.get("objectives", [])
            questionnaire = self.session.state.get("questionnaire", {}).get("draft", {})

            # Create data summary for AI context
            data_summary = json.dumps(data, indent=2)[:2000]

            direction_prompt = ""
            if user_direction:
                direction_prompt = f"\nSpecific analysis requests: {user_direction}"

            prompt = f"""You are a data analyst analyzing research data.

Research Topic: {topic}
Objectives: {', '.join(objectives)}

Questionnaire Structure:
{json.dumps(questionnaire, indent=2)[:1500] if questionnaire else "Not available"}

Collected Data (summary):
{data_summary}
{direction_prompt}

Please provide a comprehensive analysis:

1. DATA OVERVIEW
   - Total responses
   - Response rate (if applicable)
   - Data quality assessment

2. DEMOGRAPHIC ANALYSIS
   - Breakdown of respondent demographics
   - Representativeness assessment

3. KEY FINDINGS (per research objective)
   - For each objective, present the relevant findings
   - Include percentages, frequencies, patterns

4. STATISTICAL SUMMARY
   - Descriptive statistics for key variables
   - Notable patterns, trends, correlations

5. QUALITATIVE INSIGHTS
   - Themes from open-ended responses
   - Notable quotes or observations

6. LIMITATIONS
   - Data collection limitations
   - Potential biases
   - Generalizability constraints

7. RECOMMENDATIONS
   - Actionable recommendations based on findings
   - Suggestions for future research

Be specific with numbers and percentages where possible."""

            analysis = run_tgpt(
                message=prompt,
                provider=config.get_agent_provider("statistical_analysis"),
                timeout=90,
            )

            if analysis:
                self.session.state["analysis_results"] = {
                    "full_analysis": analysis,
                    "status": "pending_review",
                    "generated_at": datetime.now().isoformat(),
                }
                self.session.state["step"] = "literature_review"

                return {
                    "step": "data_analysis",
                    "status": "completed",
                    "next_step": "literature_review",
                    "analysis": analysis,
                    "message": (
                        "Analysis complete (above).\n\n"
                        "Please review the findings. Tell me:\n"
                        "  - 'approve' — findings look accurate\n"
                        "  - 'reanalyze: [specific request]' — focus on specific aspects\n"
                        "  - Any feedback or corrections needed\n\n"
                        "After approval, we'll move to literature review."
                    ),
                }
            else:
                return {"status": "error", "message": "Failed to analyze data."}

        elif action == "reanalyze" and user_direction:
            return self.step_data_analysis("analyze", user_direction)

        elif action == "approve":
            if self.session.state["analysis_results"].get("full_analysis"):
                self.session.state["analysis_results"]["status"] = "approved"
                return {
                    "step": "data_analysis",
                    "status": "approved",
                    "next_step": "literature_review",
                    "message": "Analysis approved. Next: Literature Review.",
                }
            return {"status": "error", "message": "No analysis to approve."}

        return {"status": "error", "message": "Invalid action. Use: analyze, reanalyze, approve"}

    # ════════════════════════════════════════════════════
    #  STEP 6: LITERATURE REVIEW (AI assists, human guides)
    # ════════════════════════════════════════════════════

    def step_literature_review(self, action="search", search_queries=None, user_selection=None):
        """
        Step 6: AI finds sources, human selects which to include
        """
        if action == "search":
            topic = self.session.state.get("topic", "")
            objectives = self.session.state.get("objectives", [])

            if not topic:
                return {"status": "error", "message": "No topic defined."}

            # Generate search queries if not provided
            if not search_queries:
                query_prompt = f"""Based on this research topic, suggest 5 specific search queries for academic literature review.

Topic: {topic}
Objectives: {', '.join(objectives)}

Return ONLY a JSON array of 5 search query strings, nothing else.
Example: ["query 1", "query 2", "query 3", "query 4", "query 5"]"""

                queries_text = run_tgpt(
                    message=query_prompt,
                    provider=config.get_agent_provider("web_search"),
                    timeout=30,
                )

                queries = self._extract_json(queries_text)
                if isinstance(queries, list) and queries:
                    search_queries = queries
                else:
                    search_queries = [topic]

            # Run searches (limited to avoid overwhelming)
            all_sources = []
            for q in search_queries[:3]:  # Max 3 queries
                sources = comprehensive_search(q, max_sources=8)
                for s in sources:
                    s["search_query"] = q
                all_sources.extend(sources)

            # Deduplicate
            seen = set()
            unique = []
            for s in all_sources:
                url = s.get("url", "")
                if url and url not in seen:
                    seen.add(url)
                    unique.append(s)

            self.session.state["_search_results"] = unique
            self.session.state["step"] = "literature_review"

            return {
                "step": "literature_review",
                "status": "sources_found",
                "search_queries": search_queries,
                "total_sources": len(unique),
                "sources": unique[:20],  # Show top 20
                "message": (
                    f"Found {len(unique)} sources from {len(search_queries)} searches.\n\n"
                    "Review the sources above and tell me:\n"
                    "  - 'select: 1,3,5,7' — select specific source numbers to include\n"
                    "  - 'select: all' — include all\n"
                    "  - 'search: new query' — run an additional search\n"
                    "  - 'skip' — skip literature review"
                ),
            }

        elif action == "select" and user_selection:
            search_results = self.session.state.get("_search_results", [])
            if not search_results:
                return {"status": "error", "message": "No search results to select from."}

            if user_selection.strip().lower() == "all":
                selected = search_results
            elif user_selection.strip().lower() == "none":
                selected = []
            else:
                try:
                    indices = [int(x.strip()) - 1 for x in user_selection.split(",")]
                    selected = [search_results[i] for i in indices if 0 <= i < len(search_results)]
                except (ValueError, IndexError):
                    return {"status": "error", "message": "Invalid selection. Use comma-separated numbers or 'all'."}

            self.session.state["literature_sources"] = selected

            if not selected:
                self.session.state["literature_review"] = "No sources selected for literature review."
                self.session.state["step"] = "report_writing"
                return {
                    "step": "literature_review",
                    "status": "skipped",
                    "next_step": "report_writing",
                    "message": "No sources selected. Moving to report writing.",
                }

            # Synthesize selected sources
            sources_text = "\n".join([
                f"- {s['title']} ({s.get('source', 'Unknown')}) - {s.get('url', '')}"
                for s in selected
            ])

            synthesis_prompt = f"""You are writing a literature review section.

Research Topic: {self.session.state.get('topic', '')}

The following sources were selected for the literature review:
{sources_text}

Write a synthesized literature review that:
1. Organizes sources thematically (not just listing them)
2. Identifies key findings from each source
3. Shows connections and contradictions between sources
4. Relates findings to the research topic
5. Identifies gaps that the current research addresses
6. Uses proper academic citations

Write as a cohesive literature review section, 500-1000 words."""

            lit_review = run_tgpt(
                message=synthesis_prompt,
                provider=config.get_agent_provider("literature_review"),
                timeout=60,
            )

            if lit_review:
                self.session.state["literature_review"] = lit_review
                self.session.state["step"] = "report_writing"
                return {
                    "step": "literature_review",
                    "status": "completed",
                    "next_step": "report_writing",
                    "literature_review": lit_review,
                    "message": (
                        "Literature review drafted above.\n\n"
                        "Review it and tell me:\n"
                        "  - 'approve' — looks good\n"
                        "  - 'edit: [changes]' — request modifications"
                    ),
                }

            return {"status": "error", "message": "Failed to synthesize literature review."}

        elif action == "approve":
            if self.session.state.get("literature_review"):
                return {
                    "step": "literature_review",
                    "status": "approved",
                    "next_step": "report_writing",
                    "message": "Literature review approved. Moving to report writing.",
                }
            return self.step_literature_review("search")

        return {"status": "error", "message": "Invalid action. Use: search, select, approve"}

    # ════════════════════════════════════════════════════
    #  STEP 7: REPORT WRITING (Section by section, human approves each)
    # ════════════════════════════════════════════════════

    def step_report_writing(self, section="all", action="draft", user_feedback=None):
        """
        Step 7: Write report section by section
        Human reviews and approves each section
        """
        topic = self.session.state.get("topic", "")
        objectives = self.session.state.get("objectives", [])
        analysis = self.session.state.get("analysis_results", {}).get("full_analysis", "")
        lit_review = self.session.state.get("literature_review", "")
        proposal = self.session.state.get("proposal", {}).get("draft", "")

        sections = {
            "executive_summary": "Executive Summary",
            "introduction": "1. Introduction",
            "literature_review": "2. Literature Review",
            "methodology": "3. Methodology",
            "findings": "4. Findings and Results",
            "discussion": "5. Discussion",
            "recommendations": "6. Recommendations",
            "conclusion": "7. Conclusion",
            "references": "References",
        }

        if section == "all":
            # Draft all sections
            results = {}
            for sec_key in sections:
                result = self.step_report_writing(sec_key, "draft")
                if result.get("status") == "drafted":
                    self.session.state["report_sections"][sec_key] = {
                        "content": result.get("content", ""),
                        "status": "pending_review",
                    }
                    results[sec_key] = result.get("content", "")

            return {
                "step": "report_writing",
                "status": "all_sections_drafted",
                "sections": results,
                "message": (
                    f"All {len(results)} sections drafted.\n\n"
                    "Review each section individually:\n"
                    "  'review: section_name' — review a specific section\n"
                    "  'approve_all' — approve all sections\n"
                    "  'export' — compile and export final report"
                ),
            }

        if section not in sections:
            return {"status": "error", "message": f"Unknown section: {section}. Available: {', '.join(sections.keys())}"}

        section_name = sections[section]

        if action == "draft":
            # Build context for this section
            context = f"Research Topic: {topic}\nObjectives: {', '.join(objectives)}\n\n"
            if proposal:
                context += f"Proposal: {proposal[:1000]}\n\n"
            if lit_review:
                context += f"Literature Review: {lit_review[:1000]}\n\n"
            if analysis:
                context += f"Data Analysis: {analysis[:1500]}\n\n"

            section_prompts = {
                "executive_summary": f"""Write an executive summary for this research report.

{context}

The executive summary should be 200-300 words covering:
- Purpose of the study
- Key methodology
- Major findings
- Main recommendations
- Significance

Write concisely and professionally.""",

                "introduction": f"""Write the Introduction section for this research report.

{context}

Include:
- Background and context
- Problem statement
- Research objectives and questions
- Significance of the study
- Scope and limitations

Write in formal academic style.""",

                "literature_review": f"""The literature review section:

{lit_review}

Format this section properly for the final report. Add proper citations if sources are mentioned.
If no literature review was done, write: 'No formal literature review was conducted for this study.'""",

                "methodology": f"""Write the Methodology section.

{context}

Include:
- Research design
- Data collection methods (questionnaire/survey)
- Target population and sampling
- Data analysis approach
- Ethical considerations
- Limitations

Base this on the approved proposal and data collection details.""",

                "findings": f"""Write the Findings and Results section.

{context}

Present:
- Demographic profile of respondents
- Key findings organized by research objective
- Statistical results (percentages, frequencies)
- Notable patterns and trends
- Qualitative insights from open-ended responses

Be specific with numbers and data.""",

                "discussion": f"""Write the Discussion section.

{context}

Include:
- Interpretation of key findings
- Comparison with literature (if available)
- Implications of findings
- Unexpected results
- Limitations and their impact on findings""",

                "recommendations": f"""Write the Recommendations section.

{context}

Provide:
- Specific, actionable recommendations based on findings
- Priority-ranked recommendations
- Implementation suggestions
- Areas for future research""",

                "conclusion": f"""Write the Conclusion section.

{context}

Include:
- Summary of key findings
- Achievement of research objectives
- Main contributions
- Final thoughts""",

                "references": f"""Compile the References section.

Sources available:
{json.dumps(self.session.state.get('literature_sources', []), indent=2)[:1000]}

Format references in {config.get('citation_style', 'apa')} style.
If no formal sources were used, note that this report is based on primary data collection.""",
            }

            prompt = section_prompts.get(section, f"Write the {section_name} section for this research report.\n\n{context}")

            content = run_tgpt(
                message=prompt,
                provider=config.get_agent_provider("final_synthesis"),
                timeout=60,
            )

            if content:
                return {
                    "step": "report_writing",
                    "section": section,
                    "section_name": section_name,
                    "status": "drafted",
                    "content": content,
                    "message": f"{section_name} drafted above. Reply 'approve', 'edit: [changes]', or move to next section.",
                }

            return {"status": "error", "message": f"Failed to draft {section_name}."}

        elif action == "approve":
            if section in self.session.state["report_sections"]:
                self.session.state["report_sections"][section]["status"] = "approved"
                return {
                    "step": "report_writing",
                    "section": section,
                    "status": "approved",
                    "message": f"{sections[section]} approved.",
                }
            return {"status": "error", "message": "Section not drafted yet."}

        elif action == "edit" and user_feedback:
            current = self.session.state["report_sections"].get(section, {}).get("content", "")
            prompt = f"""Here is a draft {section_name}:

{current}

Please revise it based on this feedback:
{user_feedback}

Return the FULL revised section."""

            revised = run_tgpt(message=prompt, provider=config.get_agent_provider("final_synthesis"), timeout=60)
            if revised:
                self.session.state["report_sections"][section] = {
                    "content": revised,
                    "status": "pending_review",
                }
                return {
                    "step": "report_writing",
                    "section": section,
                    "section_name": section_name,
                    "status": "revised",
                    "content": revised,
                    "message": f"{section_name} revised. Review again.",
                }
            return {"status": "error", "message": "Failed to revise section."}

        return {"status": "error", "message": "Invalid action. Use: draft, approve, edit"}

    # ════════════════════════════════════════════════════
    #  STEP 8: FINAL OUTPUT
    # ════════════════════════════════════════════════════

    def step_final_output(self, action="compile"):
        """
        Step 8: Compile all approved sections into final report
        """
        if action == "compile":
            approved_sections = {
                k: v for k, v in self.session.state["report_sections"].items()
                if v.get("status") == "approved"
            }

            if not approved_sections:
                return {"status": "error", "message": "No approved sections yet. Draft and approve sections first."}

            # Build the report
            lines = []
            lines.append("=" * 80)
            lines.append(self.session.state.get("topic", "Research Report").upper())
            lines.append("=" * 80)
            lines.append("")
            lines.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
            lines.append(f"Prepared by: {config.get('username', 'Researcher')}")
            lines.append(f"Tool: ks-eye v{__import__('ks_eye').__version__}")
            lines.append("")

            # Table of Contents
            lines.append("TABLE OF CONTENTS")
            lines.append("-" * 40)
            section_order = ["executive_summary", "introduction", "literature_review",
                           "methodology", "findings", "discussion", "recommendations",
                           "conclusion", "references"]
            page = 1
            for sec_key in section_order:
                if sec_key in approved_sections:
                    name = sec_key.replace("_", " ").title()
                    lines.append(f"  {name} ................................ {page}")
                    page += 1
            lines.append("")
            lines.append("=" * 80)

            # Sections
            for sec_key in section_order:
                if sec_key in approved_sections:
                    sec_name = sec_key.replace("_", " ").title()
                    lines.append("")
                    lines.append(sec_name.upper())
                    lines.append("=" * 80)
                    lines.append(approved_sections[sec_key]["content"])
                    lines.append("")
                    lines.append("-" * 80)

            lines.append("")
            lines.append("=" * 80)
            lines.append(f"End of Report — ks-eye v{__import__('ks_eye').__version__}")
            lines.append("=" * 80)

            report_text = "\n".join(lines)
            self.session.state["final_output"] = report_text
            self.session.state["step"] = "complete"

            return {
                "step": "final_output",
                "status": "compiled",
                "report": report_text,
                "sections_included": list(approved_sections.keys()),
                "message": (
                    "Final report compiled above!\n\n"
                    "To save:\n"
                    "  'save: filename.txt' — save as text file\n"
                    "  'save: filename.docx' — save as Word document (if python-docx installed)"
                ),
            }

        return {"status": "error", "message": "Invalid action. Use: compile"}

    def save_report(self, filepath):
        """Save the final report to file"""
        report = self.session.state.get("final_output", "")
        if not report:
            return {"status": "error", "message": "No report to save. Compile first."}

        if filepath.endswith(".docx"):
            try:
                from ks_eye.engines.docx_formatter import write_docx
                # Build simple dict for docx
                docx_data = {
                    "metadata": {"title": self.session.state.get("topic", "Research Report")},
                    "sections": [
                        {"title": k.replace("_", " ").title(), "content": v["content"]}
                        for k, v in self.session.state["report_sections"].items()
                        if v.get("status") == "approved"
                    ],
                }
                write_docx(docx_data, filepath)
                return {"status": "saved", "filepath": filepath, "format": "docx"}
            except ImportError:
                return {"status": "error", "message": "python-docx not installed. Run: pip install python-docx"}

        # Default: text
        if not filepath.endswith(".txt"):
            filepath += ".txt"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)

        return {"status": "saved", "filepath": filepath, "format": "txt"}

    def export_session(self, filepath=None):
        """Export full session as JSON for later resumption"""
        if not filepath:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(config.RESEARCH_DIR, f"session_{ts}.json")

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.session, f, indent=2, ensure_ascii=False)

        return filepath

    def load_session(self, filepath):
        """Load a saved session"""
        with open(filepath, "r", encoding="utf-8") as f:
            self.session = json.load(f)
        return self.session

    # ── Helpers ──

    def _extract_json(self, text):
        """Extract JSON from text response"""
        if not text:
            return None
        # Try parsing as-is first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # Find JSON block
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass
        # Try array
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass
        return None

    def get_current_step(self):
        return self.session.state.get("step", "topic_definition")

    def get_step_status(self):
        return {
            "current_step": self.session.state.get("step"),
            "topic": self.session.state.get("topic", ""),
            "proposal_status": self.session.state.get("proposal", {}).get("status", "not_started"),
            "questionnaire_status": self.session.state.get("questionnaire", {}).get("status", "not_started"),
            "data_collected": self.session.state.get("collected_data") is not None,
            "response_count": self.session.state.get("response_count", 0),
            "analysis_status": self.session.state.get("analysis_results", {}).get("status", "not_started"),
            "lit_sources_count": len(self.session.state.get("literature_sources", [])),
            "sections_approved": sum(
                1 for v in self.session.state.get("report_sections", {}).values()
                if v.get("status") == "approved"
            ),
        }
