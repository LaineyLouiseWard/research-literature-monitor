# Research Literature Monitor

![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
![Claude API](https://img.shields.io/badge/Claude-Haiku_API-blueviolet)
![Feedparser](https://img.shields.io/badge/Feedparser-RSS-orange)

Automated daily screening of academic RSS feeds for papers relevant to
subseasonal-to-seasonal (S2S) climate prediction research. New papers are
scored 0–4 by Claude Haiku against a configurable research scope; those
scoring >= 3 are logged with metadata and topic labels.

Built as research tooling to support a PhD thesis on S2S forecasting and
compound hydroclimatic extremes, keeping the literature review current with
minimal manual effort.

---

## Tech Stack

| Category | Tools |
|----------|-------|
| **Feed parsing** | Feedparser |
| **LLM screening** | Anthropic Claude Haiku API |
| **Metadata fallback** | Crossref API (for bot-blocked journals) |
| **Language** | Python (standard library + requests) |

---

## Quick start

```bash
# Install dependencies
pip install feedparser anthropic requests

# Dry run (fetch + dedup, no API call)
python screen.py --dry-run

# Live run (requires API key)
export ANTHROPIC_API_KEY='sk-ant-...'
python screen.py
```

## Files

| File | Purpose |
|---|---|
| `screen.py` | Fetch → dedup → screen → save workflow |
| `source_list.md` | RSS feed URLs and justifications |
| `seen_papers.txt` | Normalised titles already processed (auto-generated) |
| `paper_log.csv` | Logged papers with scores >= 3 (auto-generated) |

## Local-only context files

`screen.py` reads three context files that are not tracked in git (`.gitignore`). You need to create these locally before running:

| File | Purpose |
|---|---|
| `research_scope.md` | Thesis context sent as system prompt — defines your research question, include/exclude topics |
| `relevance_rules.md` | 0–4 scoring rules sent as system prompt — defines what scores 3+ vs 0–2 |
| `zotero_profile.md` | Zotero library profile — journals, topics, methods derived from your library |

These can be generated using the [zotero-mcp](https://github.com/54yyyu/zotero-mcp) server against your library and tailored to your research scope. See `screen.py` for the expected format.

## Notes

- AMS journal feeds are blocked by bot protection; `screen.py` falls back to the Crossref API automatically.
- First run processes the full backlog (~200+ papers). Subsequent runs process only new entries.
- Token cost per run: ~2k tokens system prompt + ~50–200 tokens per paper (Haiku).
