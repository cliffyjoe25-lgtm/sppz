# SPZ Directory Structure 🗂️

## Complete Directory Tree

```
~/.openclaw/workspace/           # Main OpenClaw workspace (root)
│
├── spz-auto-update.py           # ✅ Main orchestrator script
├── spz-auto-update-v*.py        # Backup versions (not used)
├── spz-reddit-xml-generator.py  # ✅ Reddit scraper
├── spz-twitter-nitter.py        # ✅ Twitter scraper
├── spz-github-upload.py         # Standalone uploader (alt)
├── spz-upload-existing.py       # Manual upload utility
│
├── spz-rss-scraper/             # RSS scraper folder
│   └── multi_feed_generator.py  # ✅ Main RSS generator
│
├── spz-feeds/                   # Output directory (created automatically)
│   ├── ynet-breaking-news.xml
│   ├── ynet-main-news.xml
│   ├── reddit-top10.xml
│   ├── twitter-hot.xml
│   └── ... (20+ XML files)
│
├── spz-config/                  # Configuration files (if any)
│
├── spz-images/                  # Generated images (Shpitzi)
│
├── spz-reddit-scraper/          # Reddit-specific tools
│
├── spz-relevancy-scorer/        # Scoring algorithms (future)
│
├── spz-repo-temp/               # Git clone temp (auto-deleted)
│   └── (timestamp directories created per run)
│
├── spz-rotter-scraper/          # Rotter forum scraper
│
├── spz-shared/                  # Shared team resources
│   ├── docs/
│   │   ├── SPZ_MISSION.md
│   │   ├── SPZ_RESOURCES.md
│   │   ├── SPZ_DIRECTORY_STRUCTURE.md  ← This file
│   │   └── SPZ_TROUBLESHOOTING.md
│   ├── skills/                  # Skills shared across team
│   ├── resources/               # Shared data files
│   ├── templates/               # Document templates
│   ├── config/                  # Team config
│   └── data/                    # Organized outputs
│
├── spz-social-poster/           # Social media posting tools
│
├── memory/                      # Daily logs (YYYY-MM-DD.md)
│   └── 2026-02-24.md
│
├── skills/                      # OpenClaw skills (~70 skills)
│   ├── github/
│   ├── rss-digest/
│   ├── x-twitter/
│   └── ... (many more)
│
└── TOOLS.md                     # Skill reference guide
```

## Directory Creation Script for Pitzi

כדי ליצור את אותה מבנה אצלך, הרץ את זה:

```bash
# Create workspace directory structure
mkdir -p ~/.openclaw/workspace

cd ~/.openclaw/workspace

# Create all SPZ directories
mkdir -p spz-rss-scraper
mkdir -p spz-feeds
mkdir -p spz-config
mkdir -p spz-images
mkdir -p spz-reddit-scraper
mkdir -p spz-relevancy-scorer
mkdir -p spz-repo-temp
mkdir -p spz-rotter-scraper
mkdir -p spz-shared/{docs,skills,resources,templates,config,data}
mkdir -p spz-social-poster
mkdir -p memory

# Verify structure
ls -la
```

## Critical Paths (must match!)

These relative paths are hardcoded in scripts:

| Script | Path Used | Must Exist |
|--------|-----------|------------|
| `spz-auto-update.py` | `spz-feeds/` | ✅ Yes (auto-created) |
| `spz-auto-update.py` | `spz-rss-scraper/multi_feed_generator.py` | ✅ Yes |
| `spz-rss-scraper/*.py` | `spz-feeds/` | ✅ Yes (auto-created) |
| `spz-reddit-xml-generator.py` | `spz-feeds/` | ✅ Yes (auto-created) |
| `spz-twitter-nitter.py` | `spz-feeds/` | ✅ Yes (auto-created) |

## File Locations (Must Preserve)

### Execution Scripts (Root Level)
```
~/.openclaw/workspace/
├── spz-auto-update.py           ← Main orchestrator
├── spz-reddit-xml-generator.py  ← Reddit scraper
└── spz-twitter-nitter.py        ← Twitter scraper
```

### Nested Scripts
```
~/.openclaw/workspace/
└── spz-rss-scraper/
    └── multi_feed_generator.py  ← RSS scraper
```

### Output Directory
```
~/.openclaw/workspace/
└── spz-feeds/                   ← All XML outputs here
    ├── *.xml files
```

## Script Permissions

All Python scripts should be:
- **Readable** by your user
- **Executable** (optional, can run via `python script.py`)

On Windows: No special permissions needed
On Linux/Mac: `chmod +x *.py`

## Checking Your Structure

To verify everything is in place:

```python
import os

# Check if critical files exist
files = [
    "spz-auto-update.py",
    "spz-reddit-xml-generator.py",
    "spz-twitter-nitter.py",
    "spz-rss-scraper/multi_feed_generator.py"
]

for f in files:
    if os.path.exists(f):
        print(f"✅ {f}")
    else:
        print(f"❌ {f} MISSING!")
```

## What Gets Created Automatically

These directories/files are auto-created during runtime:
- `spz-feeds/` — scripts create with `os.makedirs()`
- `spz-repo-temp-*` — temp directories for git operations
- `*.log` files — if logging configured

## Shared Resources Location

טבלת חלוקת משאבים:

| Resource Type | Local | Shared |
|--------------|-------|--------|
| Scraping scripts | ✅ Root level | ✅ `spz-shared/skills/` (copy) |
| Output XML | `spz-feeds/` | GitHub repo |
| Documentation | `spz-shared/docs/` | Git sync |
| Config | `spz-config/` | `spz-shared/config/` |
| Memory logs | `memory/` | Not shared |

## Migration Checklist for Pitzi

פריטים שחייבים להיות אצלך:

- [ ] `spz-auto-update.py`
- [ ] `spz-reddit-xml-generator.py`
- [ ] `spz-twitter-nitter.py`
- [ ] `spz-rss-scraper/multi_feed_generator.py`
- [ ] `spz-feeds/` directory (auto-created)
- [ ] `spz-shared/docs/` (documentation)
- [ ] GitHub token (update in script)
- [ ] `pip install requests feedparser`

---

*Directory map created by Tzippi 🐿️*
