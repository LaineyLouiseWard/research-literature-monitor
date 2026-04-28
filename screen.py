#!/usr/bin/env python3
"""
Literature monitor — daily screening workflow.

Fetches RSS feeds, deduplicates against previously seen papers,
screens new papers with Claude Haiku, logs relevant ones, and
optionally adds them to Zotero.

Usage:
    python screen.py              # normal run
    python screen.py --dry-run    # fetch and dedup only, no API call
    python screen.py --no-zotero  # skip Zotero upload

Requires: feedparser, anthropic, requests, pyzotero
"""

import argparse
import csv
import json
import re
import sys
from datetime import date, timedelta
from html import unescape
from pathlib import Path

import feedparser
import requests

# ---------------------------------------------------------------------------
# Paths — everything relative to this script's directory
# ---------------------------------------------------------------------------
DIR = Path(__file__).resolve().parent
SOURCE_LIST = DIR / "source_list.md"
RESEARCH_SCOPE = DIR / "research_scope.md"
RELEVANCE_RULES = DIR / "relevance_rules.md"
PAPER_LOG = DIR / "paper_log.csv"
SEEN_PAPERS = DIR / "seen_papers.txt"

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MODEL = "claude-haiku-4-5-20251001"
MAX_BATCH = 50  # max papers per API call
CROSSREF_ROWS = 30  # max papers to fetch per Crossref query
ZOTERO_LIBRARY_ID = "6343594"
ZOTERO_LIBRARY_TYPE = "group"
ZOTERO_INBOX_KEY = "2IB3JCKI"
CSV_FIELDS = [
    "date", "title", "source", "link",
    "relevance_score", "relevance_summary", "topic_labels",
]

# Crossref fallback for publishers that block scripted RSS access.
# Maps a feed name substring to its journal ISSN.
CROSSREF_FALLBACKS = {
    "Weather and Forecasting": "1520-0434",
    "Monthly Weather Review": "1520-0493",
    "Journal of Climate": "1520-0442",
    "Artificial Intelligence for the Earth Systems": "2769-7525",
}

# Browser-like User-Agent for RSS fetching
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
)


# ---------------------------------------------------------------------------
# 1. Parse feed URLs from source_list.md
# ---------------------------------------------------------------------------
def load_feeds(path: Path) -> list[dict]:
    """Extract feed name and URL from source_list.md.

    Looks for lines matching:
        ### N. Name
        - **Feed:** `url`
    """
    text = path.read_text()
    feeds = []
    name = None
    for line in text.splitlines():
        # Match section headers like "### 1. Weather and Forecasting (AMS)"
        m = re.match(r"^###\s+\d+\.\s+(.+)$", line)
        if m:
            name = m.group(1).strip()
            continue
        # Match feed URL lines like "- **Feed:** `https://...`"
        m = re.match(r"^-\s+\*\*Feed:\*\*\s+`(.+)`", line)
        if m and name:
            feeds.append({"name": name, "url": m.group(1).strip()})
            name = None
    return feeds


# ---------------------------------------------------------------------------
# 2. Fetch papers — RSS with Crossref fallback
# ---------------------------------------------------------------------------
def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = unescape(clean)
    return re.sub(r"\s+", " ", clean).strip()


def fetch_rss(name: str, url: str) -> list[dict]:
    """Parse a single RSS feed and return paper entries."""
    feed = feedparser.parse(url, agent=USER_AGENT)
    papers = []
    for entry in feed.entries:
        title = (entry.get("title") or "").strip()
        if not title:
            continue
        # Skip non-article entries
        skip = {"untitled", "full text pdf", "pdf", "snapshot",
                "journal information and table of contents"}
        if title.lower() in skip:
            continue

        # Try to get an abstract from available fields
        abstract = ""
        for field in ("summary", "description"):
            raw = entry.get(field, "")
            if raw:
                abstract = strip_html(raw)
                break
        if not abstract and entry.get("content"):
            abstract = strip_html(entry.content[0].get("value", ""))

        link = entry.get("link", "")
        papers.append({
            "title": title,
            "abstract": abstract,
            "link": link,
            "source": name,
        })
    return papers


def fetch_crossref(name: str, issn: str) -> list[dict]:
    """Fetch recent articles from a journal via the Crossref API.

    Used as a fallback when RSS feeds are blocked by bot protection.
    Free, no auth required, returns titles + abstracts.
    """
    # Fetch articles published in the last 14 days
    since = (date.today() - timedelta(days=14)).isoformat()
    url = (
        f"https://api.crossref.org/journals/{issn}/works"
        f"?rows={CROSSREF_ROWS}"
        f"&sort=published&order=desc"
        f"&filter=type:journal-article,from-pub-date:{since}"
    )
    headers = {
        "User-Agent": "LiteratureMonitor/1.0 (academic research screening)",
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    papers = []
    for item in data["message"]["items"]:
        title = (item.get("title") or [""])[0].strip()
        if not title:
            continue
        # Skip non-article items (covers, errata, etc.)
        if len(title) < 10:
            continue

        abstract = strip_html(item.get("abstract", ""))
        link = item.get("URL", "")
        papers.append({
            "title": title,
            "abstract": abstract,
            "link": link,
            "source": name,
        })
    return papers


def fetch_all(feeds: list[dict]) -> list[dict]:
    """Fetch papers from all feeds. Falls back to Crossref for blocked feeds."""
    all_papers = []
    for f in feeds:
        name = f["name"]
        try:
            papers = fetch_rss(name, f["url"])

            # If RSS returned nothing, try Crossref fallback
            if not papers:
                issn = None
                for key, val in CROSSREF_FALLBACKS.items():
                    if key in name:
                        issn = val
                        break
                if issn:
                    papers = fetch_crossref(name, issn)
                    print(f"  {name}: {len(papers)} entries (via Crossref)")
                else:
                    print(f"  {name}: 0 entries")
            else:
                print(f"  {name}: {len(papers)} entries")

            all_papers.extend(papers)
        except Exception as e:
            print(f"  {name}: FAILED ({e})")
    return all_papers


# ---------------------------------------------------------------------------
# 3. Deduplicate
# ---------------------------------------------------------------------------
def normalise_title(title: str) -> str:
    """Lowercase and strip punctuation for dedup comparison."""
    return re.sub(r"[^a-z0-9 ]", "", title.lower()).strip()


def load_seen(path: Path) -> set[str]:
    """Load set of normalised titles already seen."""
    if not path.exists():
        return set()
    return {line.strip() for line in path.read_text().splitlines() if line.strip()}


def save_seen(path: Path, titles: list[str]) -> None:
    """Append newly seen titles to the file."""
    with open(path, "a") as f:
        for t in titles:
            f.write(t + "\n")


def deduplicate(papers: list[dict], seen: set[str]) -> list[dict]:
    """Remove papers whose normalised title is already in the seen set.

    Also deduplicates within the current batch (same paper from multiple feeds).
    """
    new = []
    seen_this_run = set()
    for p in papers:
        norm = normalise_title(p["title"])
        if norm in seen or norm in seen_this_run:
            continue
        seen_this_run.add(norm)
        new.append(p)
    return new


# ---------------------------------------------------------------------------
# 4. Build prompt and call Claude
# ---------------------------------------------------------------------------
def build_system_prompt() -> str:
    """Concatenate research_scope.md and relevance_rules.md."""
    scope = RESEARCH_SCOPE.read_text()
    rules = RELEVANCE_RULES.read_text()
    return scope + "\n\n---\n\n" + rules


def build_user_prompt(papers: list[dict]) -> str:
    """Format papers as a numbered list for screening."""
    lines = [
        "Score each paper below using the relevance rules in your system prompt.",
        "Return ONLY a JSON array. For each paper:",
        '  - score >= 3: {"id": <n>, "score": <0-4>, "summary": "<1-2 sentences>", "labels": "<comma-separated>"}',
        '  - score < 3:  {"id": <n>, "score": <0-4>}',
        "Do not include any text outside the JSON array.",
        "",
    ]
    for i, p in enumerate(papers, 1):
        lines.append(f"[{i}]")
        lines.append(f"Title: {p['title']}")
        lines.append(f"Source: {p['source']}")
        if p["abstract"]:
            # Truncate very long abstracts to ~500 words
            words = p["abstract"].split()
            abstract = " ".join(words[:500])
            lines.append(f"Abstract: {abstract}")
        else:
            lines.append("Abstract: (not available — score on title only)")
        lines.append("")
    return "\n".join(lines)


def screen_papers(papers: list[dict]) -> list[dict]:
    """Send papers to Claude for relevance scoring. Returns parsed results."""
    import anthropic

    client = anthropic.Anthropic()
    system_prompt = build_system_prompt()
    results = []

    # Split into batches if needed
    for batch_start in range(0, len(papers), MAX_BATCH):
        batch = papers[batch_start : batch_start + MAX_BATCH]
        user_prompt = build_user_prompt(batch)

        print(f"  Screening papers {batch_start + 1}-{batch_start + len(batch)}...")
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        # Extract text from response
        text = response.content[0].text.strip()

        # Parse JSON — handle possible markdown code fences
        if text.startswith("```"):
            text = re.sub(r"^```\w*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
            text = text.strip()

        try:
            scored = json.loads(text)
        except json.JSONDecodeError:
            print(f"  WARNING: failed to parse Claude response as JSON.")
            print(f"  Raw response:\n{text[:500]}")
            continue

        # Map scores back to paper metadata
        for item in scored:
            idx = item["id"] - 1 + batch_start
            if 0 <= idx < len(papers):
                papers[idx]["score"] = item.get("score", 0)
                papers[idx]["summary"] = item.get("summary", "")
                papers[idx]["labels"] = item.get("labels", "")
                results.append(papers[idx])

    return results


# ---------------------------------------------------------------------------
# 5. Save results
# ---------------------------------------------------------------------------
def save_results(papers: list[dict], today: str) -> int:
    """Append papers with score >= 3 to paper_log.csv. Returns count saved."""
    relevant = [p for p in papers if p.get("score", 0) >= 3]
    if not relevant:
        return 0

    # Create CSV with headers if it doesn't exist
    write_header = not PAPER_LOG.exists()
    with open(PAPER_LOG, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if write_header:
            writer.writeheader()
        for p in relevant:
            writer.writerow({
                "date": today,
                "title": p["title"],
                "source": p["source"],
                "link": p["link"],
                "relevance_score": p["score"],
                "relevance_summary": p["summary"],
                "topic_labels": p["labels"],
            })
    return len(relevant)


# ---------------------------------------------------------------------------
# 6. Add relevant papers to Zotero _Inbox
# ---------------------------------------------------------------------------
def extract_doi(link: str) -> str | None:
    """Extract a bare DOI from a URL like https://doi.org/10.1175/..."""
    m = re.match(r"https?://(?:dx\.)?doi\.org/(10\..+)", link)
    return m.group(1) if m else None


def add_to_zotero(papers: list[dict]) -> int:
    """Add scored papers to the Zotero _Inbox collection with topic tags.

    Tries DOI first (richer metadata), falls back to URL.
    Returns count of papers successfully added.
    """
    import os

    api_key = os.environ.get("ZOTERO_API_KEY")
    if not api_key:
        print("WARNING: ZOTERO_API_KEY not set — skipping Zotero upload.")
        return 0

    from pyzotero import zotero

    zot = zotero.Zotero(ZOTERO_LIBRARY_ID, ZOTERO_LIBRARY_TYPE, api_key)
    added = 0

    for p in papers:
        if p.get("score", 0) < 3:
            continue

        tags = [{"tag": t.strip()} for t in p.get("labels", "").split(",") if t.strip()]
        title = p["title"]
        link = p.get("link", "")
        doi = extract_doi(link)

        try:
            if doi:
                # Create item from DOI metadata via Crossref
                template = zot.item_template("journalArticle")
                template["DOI"] = doi
                template["url"] = link
                template["title"] = title
                template["collections"] = [ZOTERO_INBOX_KEY]
                template["tags"] = tags
                zot.create_items([template])
            else:
                # Fallback: create a minimal item with the URL
                template = zot.item_template("journalArticle")
                template["title"] = title
                template["url"] = link
                template["collections"] = [ZOTERO_INBOX_KEY]
                template["tags"] = tags
                zot.create_items([template])
            added += 1
            print(f"  + Zotero: {title[:70]}...")
        except Exception as e:
            print(f"  ! Zotero failed for '{title[:50]}...': {e}")

    return added


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Literature monitor screening")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Fetch and dedup only — skip the Claude API call",
    )
    parser.add_argument(
        "--no-zotero", action="store_true",
        help="Skip adding papers to Zotero _Inbox",
    )
    args = parser.parse_args()
    today = date.today().isoformat()

    print(f"=== Literature screening: {today} ===\n")

    # Load feeds
    feeds = load_feeds(SOURCE_LIST)
    print(f"Loaded {len(feeds)} feeds from source_list.md\n")

    # Fetch
    print("Fetching papers...")
    papers = fetch_all(feeds)
    print(f"\nTotal entries fetched: {len(papers)}")

    # Deduplicate
    seen = load_seen(SEEN_PAPERS)
    new_papers = deduplicate(papers, seen)
    print(f"New papers after dedup: {len(new_papers)} "
          f"(seen before: {len(papers) - len(new_papers)})\n")

    if not new_papers:
        print("Nothing new to screen. Done.")
        return

    if args.dry_run:
        print("--dry-run: skipping Claude API call.")
        print(f"\nPapers that would be screened:")
        for i, p in enumerate(new_papers, 1):
            has_abstract = "yes" if p["abstract"] else "no"
            print(f"  {i}. [{p['source']}] {p['title']} "
                  f"(abstract: {has_abstract})")
        return

    # Screen with Claude (requires ANTHROPIC_API_KEY in environment)
    import os
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set. "
              "Export it before running:\n"
              "  export ANTHROPIC_API_KEY='sk-ant-...'\n")
        sys.exit(1)

    print("Screening with Claude...")
    results = screen_papers(new_papers)

    # Report scores
    score_counts = {s: 0 for s in range(5)}
    for r in results:
        score_counts[r.get("score", 0)] += 1
    print(f"\nScore distribution: {dict(score_counts)}")

    # Save relevant papers
    saved = save_results(results, today)
    print(f"Saved {saved} relevant papers to paper_log.csv")

    # Add to Zotero _Inbox
    if not args.no_zotero and saved > 0:
        print("\nAdding to Zotero _Inbox...")
        zot_added = add_to_zotero(results)
        print(f"Added {zot_added} papers to Zotero _Inbox")
    elif args.no_zotero:
        print("Skipping Zotero upload (--no-zotero)")

    # Mark all papers as seen (both accepted and rejected)
    new_titles = [normalise_title(p["title"]) for p in new_papers]
    save_seen(SEEN_PAPERS, new_titles)
    print(f"Added {len(new_titles)} titles to seen_papers.txt")

    print("\nDone.")


if __name__ == "__main__":
    main()
