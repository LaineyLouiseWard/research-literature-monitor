# Literature Monitor

Daily screening of RSS feeds for papers relevant to the S2S thesis. New papers are scored 0–4 by Claude Haiku; those scoring >= 3 are logged.

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
| `research_scope.md` | Thesis context sent as system prompt |
| `relevance_rules.md` | 0–4 scoring rules sent as system prompt |
| `source_list.md` | RSS feed URLs and justifications |
| `zotero_profile.md` | Zotero library profile (informs scope/rules) |
| `seen_papers.txt` | Normalised titles already processed (auto-generated) |
| `paper_log.csv` | Logged papers with scores >= 3 (auto-generated) |

## Refreshing Zotero context

`zotero_profile.md` captures the state of the LaineyResearch Zotero group library (ID 6343594) at the time of creation. To refresh it, use the Zotero MCP tools (`zotero_get_collections`, `zotero_get_tags`, etc.) against library 6343594 and update the file. This only needs doing if the library's composition changes substantially.

## Notes

- AMS journal feeds are blocked by bot protection; `screen.py` falls back to the Crossref API automatically.
- First run processes the full backlog (~200+ papers). Subsequent runs process only new entries.
- Token cost per run: ~2k tokens system prompt + ~50–200 tokens per paper (Haiku).
