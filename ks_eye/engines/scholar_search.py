"""
Google Scholar & Web Search Engine for ks-eye
Expanded: Wikipedia, arXiv, PubMed, SSRN, News, Patents, Datasets
"""

import urllib.request
import urllib.parse
import json
import re
import os
from html.parser import HTMLParser
from datetime import datetime


# ── Google Scholar ──

class ScholarHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self.current_result = None
        self.in_result = False
        self.in_title = False
        self.in_snippet = False
        self.in_authors = False
        self.current_text = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        class_attr = attrs_dict.get("class", "")
        if tag == "div" and "gs_r" in class_attr:
            self.current_result = {}
            self.in_result = True
        if self.in_result:
            if tag == "h3" and "gs_rt" in class_attr:
                self.in_title = True
                self.current_text = ""
            elif tag == "a" and self.in_title:
                self.current_result["url"] = attrs_dict.get("href", "")
            elif tag == "div" and "gs_rs" in class_attr:
                self.in_snippet = True
                self.current_text = ""
            elif tag == "div" and "gs_a" in class_attr:
                self.in_authors = True
                self.current_text = ""

    def handle_endtag(self, tag):
        if self.in_title and tag == "h3":
            self.in_title = False
            if self.current_result:
                self.current_result["title"] = self.current_text.strip()
        elif self.in_snippet and tag == "div":
            self.in_snippet = False
            if self.current_result:
                self.current_result["snippet"] = self.current_text.strip()
        elif self.in_authors and tag == "div":
            self.in_authors = False
            if self.current_result:
                self.current_result["authors"] = self.current_text.strip()
        elif tag == "div" and self.in_result:
            self.in_result = False
            if self.current_result and self.current_result.get("title"):
                self.results.append(self.current_result)
            self.current_result = None

    def handle_data(self, data):
        if self.in_title or self.in_snippet or self.in_authors:
            self.current_text += data


def search_google_scholar(query, max_results=10):
    sources = []
    try:
        search_url = f"https://scholar.google.com/scholar?q={urllib.parse.quote(query)}&num={max_results}&hl=en"
        req = urllib.request.Request(
            search_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode("utf-8", errors="ignore")
        parser = ScholarHTMLParser()
        parser.feed(html_content)
        for result in parser.results[:max_results]:
            sources.append({
                "title": result.get("title", "Untitled"),
                "url": result.get("url", ""),
                "snippet": result.get("snippet", ""),
                "authors": result.get("authors", ""),
                "type": "academic",
                "reliability": "High",
                "source": "Google Scholar",
                "query": query,
            })
    except Exception:
        pass
    return sources


# ── Semantic Scholar ──

def search_semantic_scholar(query, max_results=10):
    sources = []
    try:
        api_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={urllib.parse.quote(query)}&limit={max_results}&fields=title,authors,year,abstract,url,tldr,citationCount"
        req = urllib.request.Request(api_url, headers={"User-Agent": "ks-eye/2.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
        for paper in data.get("data", [])[:max_results]:
            authors = ", ".join([a.get("name", "") for a in paper.get("authors", []) if a.get("name")])
            sources.append({
                "title": paper.get("title", "Untitled"),
                "url": paper.get("url", ""),
                "snippet": paper.get("abstract", paper.get("tldr", {}).get("text", "") if paper.get("tldr") else ""),
                "authors": authors,
                "year": paper.get("year", "Unknown"),
                "citations": paper.get("citationCount", 0),
                "type": "academic",
                "reliability": "High",
                "source": "Semantic Scholar",
                "query": query,
            })
    except Exception:
        pass
    return sources


# ── CrossRef ──

def search_crossref(query, max_results=10):
    sources = []
    try:
        api_url = f"https://api.crossref.org/works?query={urllib.parse.quote(query)}&rows={max_results}"
        req = urllib.request.Request(api_url, headers={"User-Agent": "ks-eye/2.0 (mailto:researcher@localhost)"})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
        for item in data.get("message", {}).get("items", [])[:max_results]:
            title = item.get("title", ["Untitled"])[0] if item.get("title") else "Untitled"
            sources.append({
                "title": title,
                "url": item.get("URL", item.get("url", "")),
                "snippet": item.get("abstract", ""),
                "authors": ", ".join(str(a) for a in item.get("author", [])),
                "year": item.get("published-print", {}).get("date-parts", [[]])[0][0] if item.get("published-print") else "Unknown",
                "type": "academic",
                "reliability": "High",
                "source": "CrossRef",
                "query": query,
                "doi": item.get("DOI", ""),
            })
    except Exception:
        pass
    return sources


# ── DuckDuckGo Web ──

def search_web(query, max_results=10):
    sources = []
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode("utf-8", errors="ignore")
        clean_tag = re.compile(r'<[^>]+>')
        pattern = re.compile(r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', re.DOTALL)
        for match in pattern.finditer(html_content)[:max_results]:
            url, title, snippet = match.groups()
            sources.append({
                "title": clean_tag.sub("", title).strip()[:80],
                "url": url,
                "snippet": clean_tag.sub("", snippet).strip()[:200],
                "type": "web",
                "reliability": "Medium",
                "source": "DuckDuckGo",
                "query": query,
            })
    except Exception:
        pass
    return sources


# ── Wikipedia ──

def search_wikipedia(query, max_results=3):
    sources = []
    try:
        api_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&srlimit={max_results}"
        req = urllib.request.Request(api_url, headers={"User-Agent": "ks-eye/2.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        for item in data.get("query", {}).get("search", [])[:max_results]:
            title = item.get("title", "")
            snippet = re.sub(r'<[^>]+>', '', item.get("snippet", ""))
            sources.append({
                "title": title,
                "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title)}",
                "snippet": "..." + snippet + "...",
                "type": "wikipedia",
                "reliability": "Medium",
                "source": "Wikipedia",
                "query": query,
                "timestamp": item.get("timestamp", ""),
            })
    except Exception:
        pass
    return sources


def fetch_wikipedia_full(title):
    """Fetch full Wikipedia article content"""
    try:
        api_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=extracts&explaintext=true&format=json"
        req = urllib.request.Request(api_url, headers={"User-Agent": "ks-eye/2.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            if page_id != "-1":
                return page.get("extract", "")
    except Exception:
        pass
    return ""


# ── arXiv ──

def search_arxiv(query, max_results=10):
    sources = []
    try:
        api_url = f"http://export.arxiv.org/api/query?search_query=all:%22{urllib.parse.quote(query)}%22&max_results={max_results}&sortBy=relevance"
        req = urllib.request.Request(api_url, headers={"User-Agent": "ks-eye/2.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_content = response.read().decode("utf-8", errors="ignore")
        # Parse Atom XML
        entry_pattern = re.compile(
            r'<entry>(.*?)</entry>', re.DOTALL
        )
        title_pattern = re.compile(r'<title>(.*?)</title>', re.DOTALL)
        summary_pattern = re.compile(r'<summary>(.*?)</summary>', re.DOTALL)
        author_pattern = re.compile(r'<author>\s*<name>(.*?)</name>', re.DOTALL)
        link_pattern = re.compile(r'<link[^>]*href="([^"]*abs/[^"]*)"', re.DOTALL)
        published_pattern = re.compile(r'<published>(.*?)</published>')

        for entry in entry_pattern.findall(xml_content)[:max_results]:
            title_match = title_pattern.search(entry)
            summary_match = summary_pattern.search(entry)
            authors = author_pattern.findall(entry)
            link_match = link_pattern.search(entry)
            pub_match = published_pattern.search(entry)

            if title_match:
                sources.append({
                    "title": re.sub(r'<[^>]+>', '', title_match.group(1)).strip(),
                    "url": link_match.group(1) if link_match else "",
                    "snippet": re.sub(r'<[^>]+>', '', summary_match.group(1)).strip()[:300] if summary_match else "",
                    "authors": ", ".join(authors),
                    "year": pub_match.group(1)[:4] if pub_match else "Unknown",
                    "type": "arxiv",
                    "reliability": "High",
                    "source": "arXiv",
                    "query": query,
                })
    except Exception:
        pass
    return sources


# ── PubMed ──

def search_pubmed(query, max_results=10):
    sources = []
    try:
        # Step 1: Search for IDs
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}&retmax={max_results}&retmode=json"
        req = urllib.request.Request(search_url, headers={"User-Agent": "ks-eye/2.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            search_data = json.loads(response.read().decode("utf-8"))
        ids = search_data.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return sources

        # Step 2: Fetch summaries
        ids_str = ",".join(ids)
        fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids_str}&retmode=json"
        req = urllib.request.Request(fetch_url, headers={"User-Agent": "ks-eye/2.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            fetch_data = json.loads(response.read().decode("utf-8"))
        results = fetch_data.get("result", {})
        for pmid in ids:
            item = results.get(pmid, {})
            sources.append({
                "title": item.get("title", "Untitled"),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "snippet": item.get("title", ""),
                "authors": ", ".join(item.get("authors", [])[:5]),
                "year": item.get("pubdate", "Unknown"),
                "type": "pubmed",
                "reliability": "High",
                "source": "PubMed",
                "query": query,
                "pmid": pmid,
            })
    except Exception:
        pass
    return sources


# ── SSRN ──

def search_ssrn(query, max_results=10):
    sources = []
    # SSRN doesn't have a public API, search via Google with site:ssrn.com
    try:
        search_url = f"https://html.duckduckgo.com/html/?q=site%3Assrn.com+{urllib.parse.quote(query)}"
        req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode("utf-8", errors="ignore")
        clean_tag = re.compile(r'<[^>]+>')
        pattern = re.compile(r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', re.DOTALL)
        for match in pattern.finditer(html_content)[:max_results]:
            url, title, snippet = match.groups()
            sources.append({
                "title": clean_tag.sub("", title).strip()[:80],
                "url": url,
                "snippet": clean_tag.sub("", snippet).strip()[:200],
                "type": "ssrn",
                "reliability": "High",
                "source": "SSRN",
                "query": query,
            })
    except Exception:
        pass
    return sources


# ── News ──

def search_news(query, max_results=10):
    sources = []
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}+news"
        req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode("utf-8", errors="ignore")
        clean_tag = re.compile(r'<[^>]+>')
        pattern = re.compile(r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', re.DOTALL)
        for match in pattern.finditer(html_content)[:max_results]:
            url, title, snippet = match.groups()
            sources.append({
                "title": clean_tag.sub("", title).strip()[:80],
                "url": url,
                "snippet": clean_tag.sub("", snippet).strip()[:200],
                "type": "news",
                "reliability": "Medium",
                "source": "News Search",
                "query": query,
            })
    except Exception:
        pass
    return sources


# ── Patents (Google Patents via DuckDuckGo) ──

def search_patents(query, max_results=10):
    sources = []
    try:
        search_url = f"https://html.duckduckgo.com/html/?q=site%3Apatents.google.com+{urllib.parse.quote(query)}"
        req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode("utf-8", errors="ignore")
        clean_tag = re.compile(r'<[^>]+>')
        pattern = re.compile(r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', re.DOTALL)
        for match in pattern.finditer(html_content)[:max_results]:
            url, title, snippet = match.groups()
            sources.append({
                "title": clean_tag.sub("", title).strip()[:80],
                "url": url,
                "snippet": clean_tag.sub("", snippet).strip()[:200],
                "type": "patent",
                "reliability": "High",
                "source": "Google Patents",
                "query": query,
            })
    except Exception:
        pass
    return sources


# ── Dataset Discovery ──

def search_datasets(query, max_results=5):
    sources = []
    try:
        search_url = f"https://html.duckduckgo.com/html/?q=dataset+{urllib.parse.quote(query)}+site%3Akaggle.com+OR+site%3Adata.gov+OR+site%3Azenodo.org"
        req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode("utf-8", errors="ignore")
        clean_tag = re.compile(r'<[^>]+>')
        pattern = re.compile(r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', re.DOTALL)
        for match in pattern.finditer(html_content)[:max_results]:
            url, title, snippet = match.groups()
            sources.append({
                "title": clean_tag.sub("", title).strip()[:80],
                "url": url,
                "snippet": clean_tag.sub("", snippet).strip()[:200],
                "type": "dataset",
                "reliability": "Medium",
                "source": "Dataset Search",
                "query": query,
            })
    except Exception:
        pass
    return sources


# ── Comprehensive Search ──

def comprehensive_search(query, max_sources=20, source_filter=None):
    """
    Run comprehensive search across all sources

    Args:
        query: Search query
        max_sources: Maximum total sources to return
        source_filter: Optional list of source types to include
                       (e.g., ['academic', 'arxiv', 'pubmed'])
    """
    all_sources = []
    per_source = max(max_sources // 4, 3)

    # Core sources (always)
    if not source_filter or any(s in source_filter for s in ['academic', 'web']):
        all_sources.extend(search_google_scholar(query, max_results=per_source))
        all_sources.extend(search_semantic_scholar(query, max_results=per_source))
        all_sources.extend(search_crossref(query, max_results=per_source))
        all_sources.extend(search_web(query, max_results=per_source))

    # Extended sources
    if not source_filter or 'wikipedia' in source_filter:
        all_sources.extend(search_wikipedia(query, max_results=3))
    if not source_filter or 'arxiv' in source_filter:
        all_sources.extend(search_arxiv(query, max_results=per_source))
    if not source_filter or 'pubmed' in source_filter:
        all_sources.extend(search_pubmed(query, max_results=per_source))
    if not source_filter or 'ssrn' in source_filter:
        all_sources.extend(search_ssrn(query, max_results=per_source))
    if not source_filter or 'news' in source_filter:
        all_sources.extend(search_news(query, max_results=per_source))
    if not source_filter or 'patent' in source_filter:
        all_sources.extend(search_patents(query, max_results=per_source))
    if not source_filter or 'dataset' in source_filter:
        all_sources.extend(search_datasets(query, max_results=per_source))

    # Deduplicate by URL
    seen_urls = set()
    unique_sources = []
    for source in all_sources:
        url = source.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_sources.append(source)

    # Sort by reliability
    reliability_order = {"High": 0, "Medium": 1, "Low": 2, "Unknown": 3}
    unique_sources.sort(key=lambda x: reliability_order.get(x.get("reliability", "Unknown"), 3))

    return unique_sources[:max_sources]


def save_sources_to_file(sources, filename):
    sources_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "sources")
    os.makedirs(sources_dir, exist_ok=True)
    filepath = os.path.join(sources_dir, filename)
    with open(filepath, "w") as f:
        json.dump(sources, f, indent=2)
    return filepath
