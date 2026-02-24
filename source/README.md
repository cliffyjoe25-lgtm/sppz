# SPZ Source Code — Pitzi Onboarding Guide 🐕

## Welcome to the Team!

All source code and documentation now available at:
**https://github.com/cliffyjoe25-lgtm/sppz/tree/main/source**

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/cliffyjoe25-lgtm/sppz.git
```

### 2. Install Python Dependencies
```bash
pip install requests feedparser
```

### 3. Create Directory Structure
See `SPZ_DIRECTORY_STRUCTURE.md` for complete tree.

Key directories to create:
```
~/.openclaw/workspace/
├── spz-auto-update.py          ← From source/
├── spz-reddit-xml-generator.py ← From source/
├── spz-twitter-nitter.py       ← From source/
├── spz-rss-scraper/
│   └── multi_feed_generator.py ← From source/
└── spz-feeds/                  ← Created automatically
```

### 4. Configure GitHub Token
Edit `spz-auto-update.py` line 22:
```python
GITHUB_TOKEN = "ghp_YOUR_TOKEN_HERE"
```

**Get token:** https://github.com/settings/tokens → Generate new token → `repo` scope

### 5. Test Run
```bash
cd ~/.openclaw/workspace
python spz-auto-update.py
```

## What's in This Repo?

| File | Purpose |
|------|---------|
| `spz-auto-update.py` | Main orchestrator — runs all scrapers |
| `spz-reddit-xml-generator.py` | Scrapes Reddit posts |
| `spz-twitter-nitter.py` | Scrapes Twitter via Nitter |
| `multi_feed_generator.py` | Scrapes RSS feeds |
| `SPZ_MISSION.md` | Full mission & workflow docs |
| `SPZ_RESOURCES.md` | Dependencies & resources |
| `SPZ_DIRECTORY_STRUCTURE.md` | Directory layout |
| `SPZ_TROUBLESHOOTING.md` | Problem solving guide |

## Team Coordination

**Goal:** Run simultaneously, scraping different sources

**Suggestion:** Split sources:
- **Tzippi** 🐿️: RSS + GitHub upload
- **Pitzi** 🐕: Reddit + Twitter

Or rotate — you'll figure out what works best!

## Need Help?

Contact:
- **Tzippi** (OpenClaw agent) — for coding issues
- **Ben** — for SPZ architecture questions

## Updating Code

When we fix bugs or add features:
```bash
cd ~/sppz
git pull origin main
# Copy updated files to your workspace
cp source/*.py ~/.openclaw/workspace/
```

---

Good luck, and welcome aboard! 🚀
