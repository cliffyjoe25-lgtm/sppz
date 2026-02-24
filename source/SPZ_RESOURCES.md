# SPZ Resources & Dependencies 📦

## Python Scripts (Our Core Tools)

### Main Scripts (in root workspace)

| File | Purpose | Dependencies |
|------|---------|--------------|
| `spz-auto-update.py` | Main orchestrator — runs all scrapers and uploads | subprocess, shutil, glob, datetime |
| `spz-rss-scraper/multi_feed_generator.py` | RSS feed scraper | feedparser, requests, xml.etree |
| `spz-reddit-xml-generator.py` | Reddit scraper | requests, xml.etree, re |
| `spz-twitter-nitter.py` | Twitter scraper via Nitter | requests, xml.etree, re |
| `spz-github-upload.py` | Standalone GitHub uploader | subprocess, shutil |

### Backup/Versions
- `spz-auto-update-v1-backup.py` — נסיון ראשון עם threading (נכשל)
- `spz-auto-update-v2.py`, `spz-auto-update-v3.py` — גרסאות פיתוח

## Python Dependencies

### Required Packages (pip install)
```bash
pip install requests
pip install feedparser
```

### Standard Library Only (no install needed)
- `subprocess` — run external commands
- `shutil` — file operations
- `glob` — file pattern matching
- `datetime`, `time` — timestamps and delays
- `os` — file system operations
- `xml.etree.ElementTree` — XML parsing/generation
- `re` — regular expressions
- `json`, `hashlib` — data processing
- `io` — text encoding

## External Services

### GitHub
- **Repository:** cliffyjoe25-lgtm/sppz
- **Access:** GitHub Personal Token (stored in scripts)
- **Purpose:** Store and version control scraped XML files

### Nitter Instances (Twitter Scraping)
ניסיון אוטומטי עם מספר שרתים אם אחד נופל:
- https://nitter.privacydev.net
- https://nitter.net
- https://nitter.it

### Reddit (JSON API)
- **API:** https://www.reddit.com/r/{subreddit}/new.json
- **No auth required** (public endpoint)
- **Rate limits:** מוגבל לבקשה כל 2-3 שניות

### RSS Feeds
כל ה-feeds הם ציבוריים — אין צורך ב-auth

## Optional OpenClaw Skills

אלה הסקילים שמותקנים אצלי ויכולים להיות שימושיים:

### Essential for SPZ Operations
| Skill | Purpose | Installation |
|-------|---------|--------------|
| `github` | GitHub CLI integration | `openclaw skills install github` |
| `rss-digest` | RSS reading and processing | `openclaw skills install rss-digest` |
| `x-twitter` | Twitter API tools (backup) | `openclaw skills install x-twitter` |

### Useful for Analysis
| Skill | Purpose |
|-------|---------|
| `summarize` | Summarize articles/text |
| `web_search` | Search the web |
| `web_fetch` | Fetch content from URLs |

### Not Required for Scraping
- `spotify-player` — מוזיקה (פרטי)
- `personal-finance` — כספים (פרטי)
- `crypto-agent-payments` — קריפטו (פרטי)

## Configuration Files

### Script Configuration (inside Python files)
Each scraper has CONFIG dict at top:

```python
CONFIG = {
    "output_dir": "spz-feeds/",
    "timeout": 10,
    "delay_between_requests": 2.0,
}
```

### No External Config Files Needed
All settings are hardcoded in the Python scripts for simplicity.

## GitHub Token Setup

אם אתה מתקין מחדש, צריך GitHub token:

1. Go to https://github.com/settings/tokens
2. Create new token (classic)
3. Scopes needed: `repo` (full control)
4. Copy token and update in `spz-auto-update.py`:

```python
GITHUB_TOKEN = "ghp_YOUR_TOKEN_HERE"
```

**Security note:** Token is stored in plain text in script — keep scripts secure!

## Data Storage

### Local (`spz-feeds/`)
- קבצי XML שנוצרו
- מחזיק 4 שעות אחורה (cleanup מוחק ישנים)
- גודל: ~20 קבצים, כ-500KB סה"כ

### GitHub Repository
- כל קבצי ה-XML מועלים
- נשמר历史 ללא הגבלת זמן
- URL: https://github.com/cliffyjoe25-lgtm/sppz

## Rate Limiting

כל הסקרייפרים מוגבלים:
- **RSS:** 1-2 שניות בין feeds
- **Reddit:** 2.5 שניות בין subreddits
- **Twitter:** 2.5 שניות בין accounts
- **Timeout:** 10 שניות לכל request

זה מונע choking של השרתים וחסימות.

## Network Requirements

### Outbound Connections Needed
- reddit.com:443 (HTTPS)
- nitter.privacydev.net:443 (HTTPS)
- Various RSS domains:443 (HTTPS)
- github.com:443 (HTTPS)

### No Inbound Required
Scripts only make outbound HTTP requests.

## Files to Transfer to Pitzi

1. `spz-auto-update.py`
2. `spz-rss-scraper/multi_feed_generator.py`
3. `spz-reddit-xml-generator.py`
4. `spz-twitter-nitter.py`
5. `spz-shared/docs/SPZ_MISSION.md`
6. `spz-shared/docs/SPZ_DIRECTORY_STRUCTURE.md`
7. `spz-shared/docs/SPZ_TROUBLESHOOTING.md`

---

*Updated: 2026-02-24 | By: Tzippi 🐿️*
