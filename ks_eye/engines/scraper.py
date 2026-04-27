"""
ks-eye v2.0 — Web Scraper Engine
Scrapes real websites, news, academic sources, and extracts content.
Uses scholar_search + direct web scraping via BeautifulSoup/urllib.
"""

import json
import os
import time
import re
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from html.parser import HTMLParser
import hashlib

from ks_eye.engines.scholar_search import comprehensive_search
from ks_eye.config import config
from ks_eye.ui import console, make_progress


# ── HTML Content Extractor ──
class _TextExtractor(HTMLParser):
    """Strip HTML and extract readable text."""

    def __init__(self):
        super().__init__()
        self._texts = []
        self._skip = False
        self._in_script = False
        self._in_style = False

    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        if tag_lower in ("script", "style", "nav", "footer", "noscript"):
            self._skip = True
        if tag_lower == "script":
            self._in_script = True
        if tag_lower == "style":
            self._in_style = True
        if tag_lower in ("br", "p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li"):
            self._texts.append("\n")

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower in ("script", "style", "nav", "footer", "noscript"):
            self._skip = False
        if tag_lower == "script":
            self._in_script = False
        if tag_lower == "style":
            self._in_style = False

    def handle_data(self, data):
        if not self._skip and not self._in_script and not self._in_style:
            self._texts.append(data)

    def get_text(self):
        raw = "".join(self._texts)
        # Collapse multiple blank lines
        lines = [line.strip() for line in raw.split("\n")]
        cleaned = "\n".join(line for line in lines if line)
        return cleaned[:15000]  # Cap at 15K chars per page


def _extract_text(html_content):
    """Extract readable text from HTML."""
    if not html_content:
        return ""
    try:
        parser = _TextExtractor()
        parser.feed(html_content)
        return parser.get_text()
    except Exception:
        return ""


def _fetch_url(url, timeout=15):
    """Fetch a URL and return (html_content, status)."""
    try:
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; ks-eye/2.0; Research Bot)",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        })
        with urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            data = resp.read()
            return data.decode(charset, errors="replace"), True
    except (HTTPError, URLError, OSError, Exception):
        return "", False


def _content_hash(url, text):
    """Generate a hash for deduplication."""
    raw = f"{url}:{text[:500]}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def _clean_url(url):
    """Normalize URL."""
    url = url.strip().rstrip("/")
    if url.startswith("http"):
        return url
    return "https://" + url


# ── Source Categorizer ──
def _categorize_source(url, text, title=""):
    """Categorize a source by type."""
    url_lower = url.lower()
    text_lower = text[:2000].lower()
    title_lower = title.lower() if title else ""

    if any(x in url_lower for x in ["scholar", "arxiv", "pubmed", "ssrn", "jstor", "sciencedirect", "springer", "nature", "ieee"]):
        return "academic"
    if any(x in url_lower for x in ["wikipedia", "encyclopedia"]):
        return "encyclopedia"
    if any(x in url_lower for x in ["news", "bbc", "reuters", "cnn", "nytimes", "theguardian", "apnews", "npr"]):
        return "news"
    if any(x in url_lower for x in ["gov", "data.gov", "who.int", "un.org", "worldbank"]):
        return "government"
    if any(x in url_lower for x in ["github", "stackoverflow", "medium", "substack"]):
        return "article"
    if any(x in text_lower for x in ["abstract", "doi:", "journal", "peer-reviewed", "citation", "issn"]):
        return "academic"
    return "general"


# ── Main Scraper ──
def scrape_topic(topic, depth=2, provider="sky"):
    """
    Scrape content for a research topic.

    Args:
        topic: Research topic
        depth: 1=quick(5), 2=standard(15), 3=deep(30)
        provider: AI provider (for scholar_search)

    Returns:
        dict with sources list, categorized content, metadata
    """
    depth_limits = {1: 5, 2: 15, 3: 30}
    max_sources = depth_limits.get(depth, 15)

    console.print(f"\n[bold green]━━━ SCRAPER: Fetching real-world data ━━━[/bold green]")
    console.print(f"  Topic: {topic}")
    console.print(f"  Depth: {depth} (up to {max_sources} sources)")
    console.print()

    all_sources = []
    seen_hashes = set()
    start_time = time.time()

    # ── Step 1: Comprehensive search via scholar_search ──
    console.print("[dim]  Searching academic, web, news, data sources...[/dim]")
    search_results = comprehensive_search(topic)

    # comprehensive_search returns a list directly, not a dict
    results = []
    if isinstance(search_results, dict) and "results" in search_results:
        results = search_results["results"]
    elif isinstance(search_results, list):
        results = search_results
    elif isinstance(search_results, dict):
        results = [search_results]  # single result dict

    if results:
        console.print(f"  Found {len(results)} raw results, selecting top {max_sources}...")

        for item in results[:max_sources]:
            url = _clean_url(item.get("url", ""))
            if not url:
                continue

            # Deduplicate
            h = _content_hash(url, item.get("snippet", ""))
            if h in seen_hashes:
                continue
            seen_hashes.add(h)

            source_entry = {
                "url": url,
                "title": item.get("title", "Untitled"),
                "snippet": item.get("snippet", ""),
                "source_type": item.get("source", "unknown"),
                "category": _categorize_source(url, item.get("snippet", ""), item.get("title", "")),
                "scraped_content": "",
                "content_length": 0,
                "scrape_success": False,
                "timestamp": datetime.now().isoformat(),
            }
            all_sources.append(source_entry)

    # ── Step 2: Scrape full content from each source ──
    if all_sources:
        console.print(f"\n[dim]  Scraping full content from {len(all_sources)} sources...[/dim]")
        with make_progress() as progress:
            task = progress.add_task("Scraping...", total=len(all_sources))

            for i, source in enumerate(all_sources):
                progress.update(task, description=f"Scraping [{i+1}/{len(all_sources)}] {source['title'][:50]}")

                html, ok = _fetch_url(source["url"])
                if ok and html:
                    text = _extract_text(html)
                    # Clean up text
                    text = re.sub(r'\n{3,}', '\n\n', text).strip()
                    if len(text) > 50:  # Must have substantial content
                        source["scraped_content"] = text
                        source["content_length"] = len(text)
                        source["scrape_success"] = True
                    else:
                        source["scraped_content"] = source["snippet"]
                        source["content_length"] = len(source["snippet"])
                        source["scrape_success"] = False

                progress.advance(task)
                time.sleep(0.3)  # Rate limit
    else:
        console.print("[yellow]  ⚠ No web results found — will use AI knowledge as fallback[/yellow]")

    # ── Step 4: If scraping returned nothing, use AI knowledge as fallback ──
    if not all_sources or all(s.get("content_length", 0) == 0 for s in all_sources):
        console.print("\n[dim]  🤖 Falling back to AI knowledge base (no web results)...[/dim]")
        from ks_eye.engines.tgpt_engine import run_tgpt

        ai_prompt = (
            f"You are a research assistant. Provide comprehensive research on: {topic}\n\n"
            f"Include: key facts, statistics, different perspectives, evidence, and context.\n"
            f"Write at least 2000 words. Structure with clear headings.\n"
            f"Cite any sources you reference with URLs where possible."
        )
        ai_content = run_tgpt(ai_prompt, provider="sky", timeout=120)

        if ai_content:
            # Create a synthetic source from AI knowledge
            ai_source = {
                "url": "ai://internal-knowledge",
                "title": "AI Internal Knowledge Base",
                "snippet": f"AI-generated research on: {topic}",
                "source_type": "ai_knowledge",
                "category": "ai_knowledge",
                "scraped_content": ai_content,
                "content_length": len(ai_content),
                "scrape_success": True,
                "timestamp": datetime.now().isoformat(),
                "note": "AI-generated from training data (no web scraping available)",
            }
            all_sources.append(ai_source)
            console.print(f"[dim]  ✓ AI knowledge base loaded ({len(ai_content)} chars)[/dim]")
        else:
            console.print("[yellow]  ⚠ AI fallback also returned empty[/yellow]")

    # ── Step 5: Categorize ──
    categories = {}
    for source in all_sources:
        cat = source["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(source)

    # ── Step 4: Save to disk ──
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() else "_" for c in topic)[:50]
    folder = os.path.join(config.SOURCES_DIR, f"{safe_topic}_{ts}")
    os.makedirs(folder, exist_ok=True)

    # Save full sources JSON
    sources_file = os.path.join(folder, "sources.json")
    with open(sources_file, "w") as f:
        json.dump({
            "topic": topic,
            "depth": depth,
            "total_sources": len(all_sources),
            "sources_scraped": sum(1 for s in all_sources if s["scrape_success"]),
            "categories": {k: len(v) for k, v in categories.items()},
            "elapsed_seconds": round(time.time() - start_time, 1),
            "sources": all_sources,
        }, f, indent=2)

    # Save readable text file
    text_file = os.path.join(folder, "all_content.txt")
    with open(text_file, "w") as f:
        f.write(f"RESEARCH SOURCES: {topic}\n")
        f.write(f"{'=' * 80}\n")
        f.write(f"Total Sources: {len(all_sources)}\n")
        f.write(f"Successfully Scraped: {sum(1 for s in all_sources if s['scrape_success'])}\n")
        f.write(f"Categories: {', '.join(f'{k}: {len(v)}' for k, v in categories.items())}\n")
        f.write(f"{'=' * 80}\n\n")

        for i, source in enumerate(all_sources, 1):
            f.write(f"{'─' * 80}\n")
            f.write(f"SOURCE #{i}\n")
            f.write(f"Title: {source['title']}\n")
            f.write(f"URL: {source['url']}\n")
            f.write(f"Category: {source['category']}\n")
            f.write(f"Scraped: {'Yes' if source['scrape_success'] else 'No (snippet only)'}\n")
            f.write(f"Content Length: {source['content_length']} chars\n")
            f.write(f"{'─' * 80}\n\n")
            content = source["scraped_content"] if source["scraped_content"] else source["snippet"]
            f.write(f"{content}\n\n\n")

    # ── Summary ──
    elapsed = time.time() - start_time
    console.print(f"\n[bold green]✓ Scraping complete[/bold green]")
    console.print(f"  Sources found: {len(all_sources)}")
    console.print(f"  Successfully scraped: {sum(1 for s in all_sources if s['scrape_success'])}")
    console.print(f"  Categories: {', '.join(f'{k}: {len(v)}' for k, v in categories.items())}")
    console.print(f"  Time: {elapsed:.1f}s")
    console.print(f"  Saved: {folder}/")

    return {
        "topic": topic,
        "depth": depth,
        "folder": folder,
        "sources_file": sources_file,
        "text_file": text_file,
        "sources": all_sources,
        "categories": {k: len(v) for k, v in categories.items()},
        "total_sources": len(all_sources),
        "scraped_count": sum(1 for s in all_sources if s["scrape_success"]),
        "elapsed_seconds": round(elapsed, 1),
    }
