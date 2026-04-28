"""
Scopus API search utility for systematic literature reviews.

Usage:
    python scopus_search.py "TITLE-ABS-KEY(machine learning drought flood)"
    python scopus_search.py "TITLE-ABS-KEY(machine learning AND compound AND hazard AND prediction)" --count 50

Requires:
    - SCOPUS_API_KEY in ~/.env or as environment variable
    - UCD institutional access (may need VPN for some queries)

API docs: https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl
Boolean syntax: https://dev.elsevier.com/sc_search_tips.html
"""

import os
import sys
import json
import time
import argparse
import csv
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote


def load_api_key():
    """Load Scopus API key from environment or ~/.env file."""
    key = os.environ.get("SCOPUS_API_KEY")
    if key:
        return key
    env_file = Path.home() / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("SCOPUS_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise ValueError("SCOPUS_API_KEY not found in environment or ~/.env")


def search_scopus(query, api_key, count=25, start=0):
    """Run a Scopus search and return parsed results."""
    fields = "dc:title,dc:creator,prism:coverDate,prism:doi,prism:publicationName,citedby-count,dc:description"
    url = (
        f"https://api.elsevier.com/content/search/scopus"
        f"?query={quote(query)}"
        f"&apiKey={api_key}"
        f"&count={count}"
        f"&start={start}"
        f"&field={fields}"
    )
    req = Request(url, headers={"Accept": "application/json"})
    with urlopen(req) as resp:
        data = json.loads(resp.read())

    results = data.get("search-results", {})
    total = int(results.get("opensearch:totalResults", 0))
    entries = results.get("entry", [])

    papers = []
    for e in entries:
        if e.get("error"):
            continue
        papers.append({
            "title": e.get("dc:title", ""),
            "first_author": e.get("dc:creator", ""),
            "date": e.get("prism:coverDate", ""),
            "doi": e.get("prism:doi", ""),
            "journal": e.get("prism:publicationName", ""),
            "citations": e.get("citedby-count", "0"),
            "abstract": e.get("dc:description", ""),
        })
    return total, papers


def search_all(query, api_key, max_results=200):
    """Paginate through all results up to max_results."""
    all_papers = []
    start = 0
    count = 25
    total = None

    while True:
        if total is not None and start >= min(total, max_results):
            break
        t, papers = search_scopus(query, api_key, count=count, start=start)
        if total is None:
            total = t
            print(f"Total results: {total}")
        all_papers.extend(papers)
        start += count
        if not papers:
            break
        time.sleep(0.5)  # respect rate limits

    return all_papers[:max_results]


def main():
    parser = argparse.ArgumentParser(description="Search Scopus API")
    parser.add_argument("query", help="Scopus search query (e.g. TITLE-ABS-KEY(...))")
    parser.add_argument("--count", type=int, default=25, help="Max results (default 25)")
    parser.add_argument("--csv", type=str, help="Export to CSV file")
    args = parser.parse_args()

    api_key = load_api_key()
    papers = search_all(args.query, api_key, max_results=args.count)

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "first_author", "date", "doi", "journal", "citations"])
            writer.writeheader()
            for p in papers:
                writer.writerow({k: v for k, v in p.items() if k != "abstract"})
        print(f"Exported {len(papers)} papers to {args.csv}")
    else:
        for i, p in enumerate(papers, 1):
            print(f"\n{i}. {p['title']}")
            print(f"   {p['first_author']} ({p['date'][:4]}) — {p['journal']}")
            print(f"   DOI: {p['doi']}  |  Citations: {p['citations']}")


if __name__ == "__main__":
    main()
