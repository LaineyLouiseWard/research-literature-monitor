# Research Literature Monitor

Automated daily screening of academic RSS feeds for papers relevant to
subseasonal-to-seasonal (S2S) climate prediction research. New papers are
scored 0-4 by Claude Haiku against a configurable research scope; those
scoring >= 3 are logged with metadata and topic labels, then automatically
added to the Zotero `_Inbox` collection with topic tags for triage.

## Broader context

Built as research tooling to support a PhD thesis on S2S forecasting and
compound hydroclimatic extremes, keeping the literature review current with
minimal manual effort. Works alongside
[zotero-md-pipeline](../zotero-md-pipeline/) which converts Zotero PDFs to
searchable markdown for fast local paper lookup.

## Tech stack

| Category | Tools |
|----------|-------|
| Feed parsing | Feedparser |
| LLM screening | Anthropic Claude Haiku API |
| Metadata fallback | Crossref API (for bot-blocked journals) |
| Zotero integration | PyZotero (Zotero Web API) |
| Language | Python 3 |

## Getting started

```bash
# Install dependencies
pip install feedparser anthropic requests pyzotero

# Set API keys (or add to ~/.bashrc for persistence)
export ANTHROPIC_API_KEY='sk-ant-...'
export ZOTERO_API_KEY='your-zotero-api-key'

# Dry run (fetch + dedup, no API call or Zotero upload)
python screen.py --dry-run

# Full run (screen + log + Zotero upload)
python screen.py

# Screen only, skip Zotero upload
python screen.py --no-zotero
```

## Pipeline

1. **Fetch** - parses 10 RSS feeds from `source_list.md`; falls back to
   Crossref API for AMS journals blocked by bot protection
2. **Dedup** - normalises titles and skips papers already in `seen_papers.txt`
3. **Screen** - batches papers and scores them 0-4 with Claude Haiku using
   `research_scope.md` + `relevance_rules.md` as system prompt
4. **Log** - appends papers scoring >= 3 to `paper_log.csv` with metadata and
   topic labels
5. **Zotero** - adds scored papers to the LaineyResearch group library `_Inbox`
   collection via PyZotero, tagged with Haiku's topic labels (e.g.
   `s2s-prediction`, `compound-extremes`). Uses DOI when available, falls back
   to URL.

## Project structure

| File | Purpose |
|------|---------|
| `screen.py` | Main pipeline: fetch, dedup, screen, save, Zotero upload |
| `source_list.md` | 10 RSS feed URLs with justifications |
| `paper_log.csv` | Logged papers with scores >= 3 (auto-generated) |
| `seen_papers.txt` | Normalised titles already processed (auto-generated) |

### Local-only context files (gitignored)

Create these locally before running. They can be generated using the
[zotero-mcp](https://github.com/54yyyu/zotero-mcp) server against your
library and tailored to your research scope.

| File | Purpose |
|------|---------|
| `research_scope.md` | Thesis context sent as system prompt - research question, include/exclude topics |
| `relevance_rules.md` | 0-4 scoring rules sent as system prompt - what scores 3+ vs 0-2 |
| `zotero_profile.md` | Zotero library profile - journals, topics, methods (reference only) |

## Data

- RSS feeds are fetched live on each run; nothing is cached locally beyond
  `seen_papers.txt` and `paper_log.csv`
- `ANTHROPIC_API_KEY` is required for screening; `ZOTERO_API_KEY` is required
  for Zotero upload (gracefully skipped if unset)
- The Zotero target is the LaineyResearch group library (ID 6343594), `_Inbox`
  collection

## Notes

- AMS journal feeds (Weather and Forecasting, Monthly Weather Review, Journal
  of Climate, AIES) are blocked by CloudFront bot protection; `screen.py`
  falls back to the Crossref API automatically.
- First run processes the full backlog (~200+ papers). Subsequent runs process
  only new entries.
- Token cost per run: ~2k tokens system prompt + ~50-200 tokens per paper.
  At Haiku pricing this is well under $0.01/day.
