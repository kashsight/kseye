"""
ks-eye Citation & Bibliography Manager
Text-based: APA, MLA, Chicago, Harvard, IEEE citation formats
Generates bibliographies, tracks citations, manages references
"""

import json
import os
import re
from datetime import datetime
from ks_eye.config import config
from ks_eye.ui import console


# ═══════════════════════════════════════════════════════════
#  CITATION FORMATTERS
# ═══════════════════════════════════════════════════════════

class CitationManager:
    """Manage citations in multiple formats"""
    
    SUPPORTED_STYLES = ["apa", "mla", "chicago", "harvard", "ieee"]
    
    def __init__(self):
        self.references = []
        self.style = "apa"
    
    def set_style(self, style):
        if style.lower() in self.SUPPORTED_STYLES:
            self.style = style.lower()
    
    def add_reference(self, ref_dict):
        """Add a reference to the bibliography"""
        required = ["title", "authors", "year"]
        if all(k in ref_dict for k in required):
            self.references.append(ref_dict)
            return True
        return False
    
    def add_references_from_text(self, text):
        """Extract references from text output"""
        # Look for patterns like "Author (Year). Title."
        # Or numbered references
        refs = []
        
        # Pattern 1: Author (Year). Title. Source.
        pattern1 = re.compile(
            r'([A-Z][a-z]+(?:\s+et\s+al)?(?:\s*,\s*[A-Z][a-z]+)*)\s*\((\d{4})\)\.\s*([^.]+)\.\s*(.+)',
            re.MULTILINE
        )
        
        for match in pattern1.finditer(text):
            refs.append({
                "authors": match.group(1),
                "year": match.group(2),
                "title": match.group(3).strip(),
                "source": match.group(4).strip(),
            })
        
        self.references.extend(refs)
        return len(refs)
    
    def format_citation(self, ref):
        """Format a single reference"""
        style = self.style
        
        if style == "apa":
            return self._apa_format(ref)
        elif style == "mla":
            return self._mla_format(ref)
        elif style == "chicago":
            return self._chicago_format(ref)
        elif style == "harvard":
            return self._harvard_format(ref)
        elif style == "ieee":
            return self._ieee_format(ref)
        else:
            return self._apa_format(ref)
    
    def _apa_format(self, ref):
        """APA 7th edition format"""
        authors = ref.get("authors", "Unknown Author")
        year = ref.get("year", "n.d.")
        title = ref.get("title", "Untitled")
        source = ref.get("source", ref.get("url", "Unknown Source"))
        url = ref.get("url", "")
        
        citation = f"{authors} ({year}). {title}. {source}."
        if url:
            citation += f" {url}"
        
        return citation
    
    def _mla_format(self, ref):
        """MLA 9th edition format"""
        authors = ref.get("authors", "Unknown Author")
        title = ref.get("title", "Untitled")
        source = ref.get("source", "Unknown Source")
        year = ref.get("year", "n.d.")
        url = ref.get("url", "")
        
        citation = f'{authors}. "{title}." {source}, {year}.'
        if url:
            citation += f" {url}"
        
        return citation
    
    def _chicago_format(self, ref):
        """Chicago 17th edition format"""
        authors = ref.get("authors", "Unknown Author")
        title = ref.get("title", "Untitled")
        source = ref.get("source", "Unknown Source")
        year = ref.get("year", "n.d.")
        url = ref.get("url", "")
        
        citation = f'{authors}. "{title}." {source} ({year}).'
        if url:
            citation += f" {url}"
        
        return citation
    
    def _harvard_format(self, ref):
        """Harvard referencing format"""
        authors = ref.get("authors", "Unknown Author")
        year = ref.get("year", "n.d.")
        title = ref.get("title", "Untitled")
        source = ref.get("source", "Unknown Source")
        url = ref.get("url", "")
        
        citation = f"{authors}, {year}. {title}. {source}."
        if url:
            citation += f" Available at: {url}"
        
        return citation
    
    def _ieee_format(self, ref):
        """IEEE citation format"""
        authors = ref.get("authors", "Unknown Author")
        title = ref.get("title", "Untitled")
        source = ref.get("source", "Unknown Source")
        year = ref.get("year", "n.d.")
        url = ref.get("url", "")
        
        citation = f"{authors}, \"{title},\" {source}, {year}."
        if url:
            citation += f" [Online]. Available: {url}"
        
        return citation
    
    def generate_bibliography(self):
        """Generate full bibliography"""
        if not self.references:
            return "No references available."
        
        lines = []
        for i, ref in enumerate(self.references, 1):
            formatted = self.format_citation(ref)
            lines.append(f"[{i}] {formatted}")
        
        return "\n".join(lines)
    
    def generate_bibliography_text(self, title="BIBLIOGRAPHY"):
        """Generate formatted bibliography as text block"""
        lines = []
        lines.append("=" * 80)
        lines.append(f"{title} ({self.style.upper()} Style)")
        lines.append("=" * 80)
        lines.append("")
        
        if not self.references:
            lines.append("No references available.")
        else:
            for i, ref in enumerate(self.references, 1):
                formatted = self.format_citation(ref)
                lines.append(f"[{i}] {formatted}")
                lines.append("")
        
        lines.append(f"Total References: {len(self.references)}")
        lines.append("")
        
        return "\n".join(lines)
    
    def save_bibliography(self, filepath=None, topic="research"):
        """Save bibliography to file"""
        if not filepath:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = "".join(c if c.isalnum() else "_" for c in topic)[:40]
            filepath = os.path.join(config.RESEARCH_DIR, f"bibliography_{safe_topic}_{ts}.txt")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        text = self.generate_bibliography_text()
        with open(filepath, "w") as f:
            f.write(text)
        
        # Also save as JSON for programmatic access
        json_path = filepath.replace(".txt", ".json")
        with open(json_path, "w") as f:
            json.dump({
                "style": self.style,
                "references": self.references,
                "generated_at": datetime.now().isoformat(),
            }, f, indent=2)
        
        return filepath, json_path


def generate_citations_from_research(research_text, style="apa"):
    """
    Parse research text and generate citations
    
    This looks for reference patterns in the text
    and extracts them into a bibliography
    """
    cm = CitationManager()
    cm.set_style(style)
    
    # Extract references
    refs_found = cm.add_references_from_text(research_text)
    
    return cm, refs_found
