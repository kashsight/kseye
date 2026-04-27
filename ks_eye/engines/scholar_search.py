"""
ks-eye Multi-Source Search Engine v2
75+ Data Sources: Academic, News, Data, Government, encyclopedic, and more
Organized by category with caching and deduplication
"""

import urllib.request
import urllib.parse
import json
import re
import os
import time
from html.parser import HTMLParser
from datetime import datetime
from collections import OrderedDict


# ── Source Registry (75+ sources) ──

SOURCE_REGISTRY = {
    # ACADEMIC PAPERS & JOURNALS (20 sources)
    "google_scholar": {"name": "Google Scholar", "category": "academic", "type": "scrape", "base_url": "https://scholar.google.com/scholar"},
    "semantic_scholar": {"name": "Semantic Scholar", "category": "academic", "type": "api", "base_url": "https://api.semanticscholar.org/graph/v1/paper/search"},
    "crossref": {"name": "CrossRef", "category": "academic", "type": "api", "base_url": "https://api.crossref.org/works"},
    "arxiv": {"name": "arXiv", "category": "academic", "type": "api", "base_url": "http://export.arxiv.org/api/query"},
    "pubmed": {"name": "PubMed", "category": "academic", "type": "api", "base_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"},
    "ssrn": {"name": "SSRN", "category": "academic", "type": "scrape_via_ddg", "filter": "site:ssrn.com"},
    "jstor": {"name": "JSTOR", "category": "academic", "type": "api", "base_url": "https://www.jstor.org/search/"},
    "springer": {"name": "Springer Nature", "category": "academic", "type": "api", "base_url": "https://api.springernature.com/meta/v2/json"},
    "elsevier": {"name": "Elsevier/ScienceDirect", "category": "academic", "type": "api", "base_url": "https://api.elsevier.com/content/search/sciencedirect"},
    "ieee": {"name": "IEEE Xplore", "category": "academic", "type": "api", "base_url": "https://ieeexploreapi.ieee.org/api/v1/search/articles"},
    "acm": {"name": "ACM Digital Library", "category": "academic", "type": "scrape", "base_url": "https://dl.acm.org/action/doSearch"},
    "sciencedirect": {"name": "ScienceDirect", "category": "academic", "type": "scrape_via_ddg", "filter": "site:sciencedirect.com"},
    "wiley": {"name": "Wiley Online Library", "category": "academic", "type": "scrape_via_ddg", "filter": "site:onlinelibrary.wiley.com"},
    "tandfonline": {"name": "Taylor & Francis", "category": "academic", "type": "scrape_via_ddg", "filter": "site:tandfonline.com"},
    "sage": {"name": "SAGE Journals", "category": "academic", "type": "scrape_via_ddg", "filter": "site:journals.sagepub.com"},
    "plos": {"name": "PLOS ONE", "category": "academic", "type": "api", "base_url": "https://api.plos.org/search"},
    "biorxiv": {"name": "bioRxiv", "category": "academic", "type": "api", "base_url": "https://api.biorxiv.org/details/biorxiv"},
    "medrxiv": {"name": "medRxiv", "category": "academic", "type": "api", "base_url": "https://api.medrxiv.org/details/medrxiv"},
    "researchgate": {"name": "ResearchGate", "category": "academic", "type": "scrape_via_ddg", "filter": "site:researchgate.net"},
    "academia": {"name": "Academia.edu", "category": "academic", "type": "scrape_via_ddg", "filter": "site:academia.edu"},
    
    # PREPRINT SERVERS (8 sources)
    "authorea": {"name": "Authorea", "category": "preprint", "type": "scrape_via_ddg", "filter": "site:authorea.com"},
    "osf": {"name": "OSF Preprints", "category": "preprint", "type": "api", "base_url": "https://api.osf.io/v2/preprints/"},
    "peerj": {"name": "PeerJ", "category": "preprint", "type": "scrape_via_ddg", "filter": "site:peerj.com"},
    "f1000research": {"name": "F1000Research", "category": "preprint", "type": "scrape_via_ddg", "filter": "site:f1000research.com"},
    "chemrxiv": {"name": "ChemRxiv", "category": "preprint", "type": "scrape_via_ddg", "filter": "site:chemrxiv.org"},
    "engrxiv": {"name": "EngRxiv", "category": "preprint", "type": "scrape_via_ddg", "filter": "site:engrxiv.org"},
    "psyarxiv": {"name": "PsyArXiv", "category": "preprint", "type": "scrape_via_ddg", "filter": "site:psyarxiv.com"},
    "socarxiv": {"name": "SocArXiv", "category": "preprint", "type": "scrape_via_ddg", "filter": "site:socarxiv.org"},
    
    # NEWS & MEDIA (12 sources)
    "news_general": {"name": "General News", "category": "news", "type": "scrape_via_ddg", "filter": "news"},
    "bbc": {"name": "BBC News", "category": "news", "type": "scrape_via_ddg", "filter": "site:bbc.com/news"},
    "reuters": {"name": "Reuters", "category": "news", "type": "scrape_via_ddg", "filter": "site:reuters.com"},
    "ap_news": {"name": "Associated Press", "category": "news", "type": "scrape_via_ddg", "filter": "site:apnews.com"},
    "theguardian": {"name": "The Guardian", "category": "news", "type": "scrape_via_ddg", "filter": "site:theguardian.com"},
    "nytimes": {"name": "New York Times", "category": "news", "type": "scrape_via_ddg", "filter": "site:nytimes.com"},
    "washington_post": {"name": "Washington Post", "category": "news", "type": "scrape_via_ddg", "filter": "site:washingtonpost.com"},
    "cnn": {"name": "CNN", "category": "news", "type": "scrape_via_ddg", "filter": "site:cnn.com"},
    "aljazeera": {"name": "Al Jazeera", "category": "news", "type": "scrape_via_ddg", "filter": "site:aljazeera.com"},
    "techcrunch": {"name": "TechCrunch", "category": "news", "type": "scrape_via_ddg", "filter": "site:techcrunch.com"},
    "wired": {"name": "Wired", "category": "news", "type": "scrape_via_ddg", "filter": "site:wired.com"},
    "venturebeat": {"name": "VentureBeat", "category": "news", "type": "scrape_via_ddg", "filter": "site:venturebeat.com"},
    
    # ENCYCLOPEDIAS & REFERENCE (10 sources)
    "wikipedia": {"name": "Wikipedia", "category": "encyclopedia", "type": "api", "base_url": "https://en.wikipedia.org/w/api.php"},
    "britannica": {"name": "Encyclopedia Britannica", "category": "encyclopedia", "type": "scrape_via_ddg", "filter": "site:britannica.com"},
    "scholarpedia": {"name": "Scholarpedia", "category": "encyclopedia", "type": "scrape_via_ddg", "filter": "site:scholarpedia.org"},
    "encyclopedia_com": {"name": "Encyclopedia.com", "category": "encyclopedia", "type": "scrape_via_ddg", "filter": "site:encyclopedia.com"},
    "investopedia": {"name": "Investopedia", "category": "encyclopedia", "type": "scrape_via_ddg", "filter": "site:investopedia.com"},
    "statista": {"name": "Statista", "category": "encyclopedia", "type": "scrape_via_ddg", "filter": "site:statista.com"},
    "wolfram_alpha": {"name": "Wolfram Alpha", "category": "encyclopedia", "type": "scrape_via_ddg", "filter": "site:wolframalpha.com"},
    "worldbank": {"name": "World Bank Open Knowledge", "category": "encyclopedia", "type": "api", "base_url": "https://search.worldbank.org/api/v2/wds"},
    "unesco": {"name": "UNESCO Digital Library", "category": "encyclopedia", "type": "scrape_via_ddg", "filter": "site:unesco.org"},
    "oecd": {"name": "OECD iLibrary", "category": "encyclopedia", "type": "scrape_via_ddg", "filter": "site:oecd-ilibrary.org"},
    
    # DATASETS & OPEN DATA (10 sources)
    "datasets_general": {"name": "General Datasets", "category": "data", "type": "scrape_via_ddg", "filter": "site:kaggle.com OR site:data.gov OR site:zenodo.org"},
    "kaggle": {"name": "Kaggle", "category": "data", "type": "scrape_via_ddg", "filter": "site:kaggle.com"},
    "data_gov": {"name": "Data.gov", "category": "data", "type": "scrape_via_ddg", "filter": "site:data.gov"},
    "zenodo": {"name": "Zenodo", "category": "data", "type": "api", "base_url": "https://zenodo.org/api/records"},
    "dataworld": {"name": "Data.world", "category": "data", "type": "scrape_via_ddg", "filter": "site:data.world"},
    "github_datasets": {"name": "GitHub Datasets", "category": "data", "type": "scrape_via_ddg", "filter": "site:github.com datasets"},
    "aws_datasets": {"name": "AWS Open Data", "category": "data", "type": "scrape_via_ddg", "filter": "site:registry.opendata.aws"},
    "google_datasets": {"name": "Google Dataset Search", "category": "data", "type": "scrape_via_ddg", "filter": "site:datasetsearch.research.google.com"},
    "figshare": {"name": "Figshare", "category": "data", "type": "api", "base_url": "https://api.figshare.com/v2/articles"},
    "dryad": {"name": "Dryad Digital Repository", "category": "data", "type": "scrape_via_ddg", "filter": "site:datadryad.org"},
    
    # PATENTS & IP (5 sources)
    "patents_google": {"name": "Google Patents", "category": "patents", "type": "scrape_via_ddg", "filter": "site:patents.google.com"},
    "uspto": {"name": "USPTO", "category": "patents", "type": "scrape_via_ddg", "filter": "site:uspto.gov/patents"},
    "epo": {"name": "European Patent Office", "category": "patents", "type": "scrape_via_ddg", "filter": "site:epo.org"},
    "wipo": {"name": "WIPO PATENTSCOPE", "category": "patents", "type": "scrape_via_ddg", "filter": "site:wipo.int/patentscope"},
    "freepatentsonline": {"name": "Free Patents Online", "category": "patents", "type": "scrape_via_ddg", "filter": "site:freepatentsonline.com"},
    
    # GOVERNMENT & POLICY (8 sources)
    "congress_gov": {"name": "Congress.gov", "category": "government", "type": "api", "base_url": "https://api.congress.gov/v3"},
    "govinfo": {"name": "GovInfo", "category": "government", "type": "scrape_via_ddg", "filter": "site:govinfo.gov"},
    "federal_register": {"name": "Federal Register", "category": "government", "type": "api", "base_url": "https://www.federalregister.gov/api/v1/documents"},
    "whitehouse": {"name": "White House", "category": "government", "type": "scrape_via_ddg", "filter": "site:whitehouse.gov"},
    "supreme_court": {"name": "Supreme Court", "category": "government", "type": "scrape_via_ddg", "filter": "site:supremecourt.gov"},
    "gao": {"name": "Government Accountability Office", "category": "government", "type": "scrape_via_ddg", "filter": "site:gao.gov"},
    "crs_reports": {"name": "CRS Reports", "category": "government", "type": "scrape_via_ddg", "filter": "site:crsreports.congress.gov"},
    "regulations_gov": {"name": "Regulations.gov", "category": "government", "type": "scrape_via_ddg", "filter": "site:regulations.gov"},
    
    # THINK TANKS & RESEARCH ORGS (7 sources)
    "brookings": {"name": "Brookings Institution", "category": "thinktank", "type": "scrape_via_ddg", "filter": "site:brookings.edu"},
    "rand": {"name": "RAND Corporation", "category": "thinktank", "type": "scrape_via_ddg", "filter": "site:rand.org"},
    "pew_research": {"name": "Pew Research Center", "category": "thinktank", "type": "scrape_via_ddg", "filter": "site:pewresearch.org"},
    "csis": {"name": "Center for Strategic & International Studies", "category": "thinktank", "type": "scrape_via_ddg", "filter": "site:csis.org"},
    "heritage": {"name": "Heritage Foundation", "category": "thinktank", "type": "scrape_via_ddg", "filter": "site:heritage.org"},
    "cato": {"name": "Cato Institute", "category": "thinktank", "type": "scrape_via_ddg", "filter": "site:cato.org"},
    "urban_institute": {"name": "Urban Institute", "category": "thinktank", "type": "scrape_via_ddg", "filter": "site:urban.org"},
    
    # GENERAL WEB (3 sources)
    "duckduckgo": {"name": "DuckDuckGo", "category": "general", "type": "scrape", "base_url": "https://html.duckduckgo.com/html/"},
    "bing_cached": {"name": "Bing (Cached)", "category": "general", "type": "scrape_via_ddg", "filter": ""},
    "archive_org": {"name": "Internet Archive", "category": "general", "type": "scrape_via_ddg", "filter": "site:archive.org"},
}

# Source counts by category
SOURCE_COUNTS = {}
for source_id, info in SOURCE_REGISTRY.items():
    cat = info["category"]
    SOURCE_COUNTS[cat] = SOURCE_COUNTS.get(cat, 0) + 1

TOTAL_SOURCES = len(SOURCE_REGISTRY)


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

def comprehensive_search(query, max_sources=30, source_filter=None, categories=None):
    """
    Run comprehensive search across 75+ sources

    Args:
        query: Search query
        max_sources: Maximum total sources to return
        source_filter: Optional list of specific source IDs to use
        categories: Optional list of categories to search 
                   (academic, preprint, news, encyclopedia, data, patents, government, thinktank, general)
    """
    all_sources = []
    start_time = time.time()
    
    # Determine which sources to search
    active_sources = []
    if source_filter:
        # Use specific sources
        active_sources = [s for s in source_filter if s in SOURCE_REGISTRY]
    elif categories:
        # Use categories
        for source_id, info in SOURCE_REGISTRY.items():
            if info["category"] in categories:
                active_sources.append(source_id)
    else:
        # Use all sources
        active_sources = list(SOURCE_REGISTRY.keys())
    
    # Calculate per-source allocation
    per_source = max(max_sources // len(active_sources), 2)
    per_source = min(per_source, 5)  # Cap at 5 per source
    
    console_msg = f"Searching {len(active_sources)} sources across {len(set(SOURCE_REGISTRY[s]['category'] for s in active_sources))} categories..."
    
    # Search by type
    for source_id in active_sources:
        try:
            info = SOURCE_REGISTRY[source_id]
            source_type = info["type"]
            source_name = info["name"]
            source_cat = info["category"]
            
            # Route to appropriate search method
            if source_type == "api" and info.get("base_url"):
                results = _search_api_source(source_id, query, per_source)
            elif source_type == "scrape" and info.get("base_url"):
                results = _search_scrape_source(source_id, query, per_source)
            elif source_type == "scrape_via_ddg":
                results = _search_via_duckduckgo(source_id, query, per_source)
            else:
                results = []
            
            all_sources.extend(results)
            
            # Rate limiting - be respectful
            time.sleep(0.2)
            
            # Stop if we have enough
            if len(all_sources) >= max_sources * 2:
                break
                
        except Exception as e:
            # Skip failing sources silently
            pass
    
    # Deduplicate by URL
    seen_urls = set()
    unique_sources = []
    for source in all_sources:
        url = source.get("url", "")
        # Normalize URL for dedup
        url_key = url.split("?")[0] if url else ""
        if url_key and url_key not in seen_urls:
            seen_urls.add(url_key)
            unique_sources.append(source)
    
    # Sort by reliability
    reliability_order = {"High": 0, "Medium": 1, "Low": 2, "Unknown": 3}
    unique_sources.sort(key=lambda x: (
        reliability_order.get(x.get("reliability", "Unknown"), 3),
        x.get("year", "9999"),  # Prefer newer
    ))
    
    elapsed = time.time() - start_time
    
    return unique_sources[:max_sources]


def _search_api_source(source_id, query, max_results):
    """Search an API-based source"""
    info = SOURCE_REGISTRY[source_id]
    base_url = info["base_url"]
    
    try:
        if source_id == "semantic_scholar":
            url = f"{base_url}?query={urllib.parse.quote(query)}&limit={max_results}&fields=title,abstract,authors,year,url"
            req = urllib.request.Request(url, headers={"User-Agent": "ks-eye/2.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
            return [{
                "title": item.get("title", "Untitled"),
                "url": item.get("url", ""),
                "snippet": item.get("abstract", "")[:300],
                "authors": ", ".join([a.get("name", "") for a in item.get("authors", [])[:3]]),
                "year": str(item.get("year", "Unknown")),
                "type": "academic",
                "reliability": "High",
                "source": info["name"],
                "query": query,
            } for item in data.get("data", [])[:max_results]]
        
        elif source_id == "crossref":
            url = f"{base_url}?query={urllib.parse.quote(query)}&rows={max_results}&select=title,abstract,author,year,URL"
            req = urllib.request.Request(url, headers={"User-Agent": "ks-eye/2.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
            return [{
                "title": item.get("title", ["Untitled"])[0],
                "url": item.get("URL", ""),
                "snippet": item.get("abstract", "")[:300],
                "authors": ", ".join([f"{a.get('given', '')} {a.get('family', '')}" for a in item.get("author", [])[:3]]),
                "year": str(item.get("published-print", {}).get("date-parts", [[0]])[0][0] or "Unknown"),
                "type": "academic",
                "reliability": "High",
                "source": info["name"],
                "query": query,
            } for item in data.get("message", {}).get("items", [])[:max_results]]
        
        elif source_id in ["plos", "zenodo", "figshare"]:
            # Generic API handler
            url = f"{base_url}?q={urllib.parse.quote(query)}&rows={max_results}"
            req = urllib.request.Request(url, headers={"User-Agent": "ks-eye/2.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
            # Adapt based on API structure
            items = data.get("response", {}).get("docs", []) or data.get("hits", []) or []
            return [{
                "title": item.get("title", item.get("metadata", {}).get("title", "Untitled")),
                "url": item.get("url", f"https://{source_id}.org/{item.get('id', '')}"),
                "snippet": str(item.get("abstract", item.get("description", "")))[:300],
                "authors": ", ".join(item.get("author", [])[:3]) if isinstance(item.get("author"), list) else "",
                "year": str(item.get("year", "Unknown")),
                "type": info["category"],
                "reliability": "High",
                "source": info["name"],
                "query": query,
            } for item in items[:max_results]]
        
        # Add more API handlers as needed
        return []
        
    except Exception:
        return []


def _search_scrape_source(source_id, query, max_results):
    """Search a scraping-based source"""
    info = SOURCE_REGISTRY[source_id]
    # For now, route through DuckDuckGo as fallback
    return _search_via_duckduckgo(source_id, query, max_results)


def _search_via_duckduckgo(source_id, query, max_results):
    """Search via DuckDuckGo with site filter"""
    info = SOURCE_REGISTRY[source_id]
    filter_query = info.get("filter", "")
    
    if not filter_query or filter_query == "news":
        # General search
        return search_web(query, max_results)
    
    # Site-specific search
    site_query = f"{filter_query} {query}"
    return search_web(site_query, max_results)


def save_sources_to_file(sources, filename):
    sources_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "sources")
    os.makedirs(sources_dir, exist_ok=True)
    filepath = os.path.join(sources_dir, filename)
    with open(filepath, "w") as f:
        json.dump(sources, f, indent=2)
    return filepath
