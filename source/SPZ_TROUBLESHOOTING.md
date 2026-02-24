# SPZ Troubleshooting Guide 🔧

## Quick Diagnostic Commands

### Check if Python is working
```bash
python --version
# Should show Python 3.x.x
```

### Check installed packages
```bash
pip list | grep -E "(requests|feedparser)"
# Should show both installed
```

### Check directory structure
```bash
ls ~/.openclaw/workspace/spz-*.py
ls ~/.openclaw/workspace/spz-rss-scraper/
```

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'requests'"

**Problem:** Python package not installed

**Solution:**
```bash
pip install requests
pip install feedparser
```

### Issue 2: "FileNotFoundError: [Errno 2] No such file or directory"

**Problem:** Running script from wrong directory

**Solution A:** Run from correct directory
```bash
cd ~/.openclaw/workspace
python spz-auto-update.py
```

**Solution B:** Script auto-fix (already in latest version)
```python
# At top of spz-auto-update.py
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
```

### Issue 3: "Permission denied" on GitHub push

**Problem:** GitHub token invalid or expired

**Solution:**
1. Check token in script: `GITHUB_TOKEN` variable
2. Verify token at: https://github.com/settings/tokens
3. Update token in script:
   ```python
   GITHUB_TOKEN = "ghp_YOUR_NEW_TOKEN"
   ```

### Issue 4: "Timeout expired" on scraping

**Problem:** Network slow or site blocked

**Solution:**
- Increase timeout in CONFIG:
  ```python
  CONFIG = {
      "timeout": 15,  # was 10
  }
  ```
- Check internet connection: `ping google.com`

### Issue 5: Reddit returns 403 Forbidden

**Problem:** Reddit blocking requests (rate limit)

**Solution:**
- Wait 1 hour between runs
- Check User-Agent in script is reasonable
- Increase delay between requests:
  ```python
  CONFIG = {
      "delay_between_subreddits": 5.0,  # was 2.5
  }
  ```

### Issue 6: Nitter returns 404 or timeout

**Problem:** Nitter instance down or account not found

**Solution:**
- Scripts automatically try next instance
- Manually test: `curl https://nitter.privacydev.net/netanyahu/rss`
- If all fail: Twitter temporarily blocked

### Issue 7: "git clone failed"

**Problem:** spz-repo-temp directory locked

**Solution:**
```bash
# Kill any hanging git processes
taskkill /f /im git.exe  # Windows
pkill -f git             # Linux/Mac

# Manually delete temp directory
rm -rf spz-repo-temp*
```

### Issue 8: XML files not being created

**Problem:** Output directory missing or permissions

**Solution:**
```bash
# Create directory manually
mkdir -p ~/.openclaw/workspace/spz-feeds

# Check permissions
ls -la ~/.openclaw/workspace/spz-feeds/
```

### Issue 9: Hebrew text shows as gibberish

**Problem:** Encoding issue in Windows

**Solution:** Already fixed in scripts with:
```python
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

## Debugging Steps

### Step 1: Run individual scrapers
Don't run full orchestrator — test each scraper alone:

```bash
# Test RSS only
python spz-rss-scraper/multi_feed_generator.py

# Test Reddit only
python spz-reddit-xml-generator.py

# Test Twitter only
python spz-twitter-nitter.py
```

### Step 2: Check output files
after each test, verify XML was created:

```bash
ls -lh spz-feeds/
```

### Step 3: Check XML validity
```bash
# Simple syntax check
xmllint --noout spz-feeds/reddit-top10.xml

# Or open in browser
# If Chrome opens it without errors = valid XML
```

### Step 4: Enable verbose logging
Add to top of any script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Issues

### Script takes too long (>10 minutes)

**Normal runtime:** 3-4 minutes

**If taking >10 min:**
1. Check network speed: `speedtest-cli` or fast.com
2. Reduce number of feeds/accounts in script
3. Check if VPN/proxy slowing things

### High memory usage

**Problem:** Scripts load all content into memory

**Solution:** Already optimized — each scraper processes ~10-20 items max

### Disk space issues

**Check size:**
```bash
du -sh spz-feeds/
```

**Typical size:** 500KB-1MB (very small)

**If large:** Cleanup old files is automatic, but check:
```bash
# Manual cleanup
rm spz-feeds/*.xml
```

## GitHub Issues

### "fatal: Authentication failed"

1. Token expired → Create new at github.com/settings/tokens
2. Wrong permissions → Needs `repo` scope
3. 2FA enabled → Use token, not password

### "rejected: non-fast-forward"

**Problem:** Remote repo has new commits we don't have

**Solution:** Script deletes temp dir each time = fresh clone = no conflict

### "merge conflict"

**Should not happen** — fresh clone every time

If happens, manually clear:
```bash
rm -rf spz-repo-temp*
```

## Testing Checklist

לפני שאומרים "זה עובד":

- [ ] Python runs: `python --version`
- [ ] Packages installed: `pip list`
- [ ] Directory structure correct
- [ ] RSS scraper creates XML files
- [ ] Reddit scraper creates XML files
- [ ] Twitter scraper creates XML files (may fail if Nitter down)
- [ ] GitHub upload succeeds
- [ ] Repository shows new commit at https://github.com/cliffyjoe25-lgtm/sppz

## Emergency Recovery

### Reset everything (nuclear option)

```bash
cd ~/.openclaw/workspace

# Stop any running Python
pkill -f python

# Clean temp directories
rm -rf spz-repo-temp*
rm -rf spz-feeds/*.xml

# Clean Python cache
rm -rf spz-rss-scraper/__pycache__

# Re-create directories
mkdir -p spz-feeds
mkdir -p spz-repo-temp

# Re-install packages
pip install --upgrade requests feedparser

# Test run
python spz-auto-update.py
```

## Getting Help

**If stuck:**
1. Check this troubleshooting file again
2. Run script with full output: `python spz-auto-update.py 2>&1 | tee output.log`
3. Share output.log with Ben or Tzippi
4. Tell us: what you ran, what you expected, what actually happened

## Known Limitations

1. **Nitter reliability:** Twitter scraping depends on Nitter uptime — sometimes down
2. **Reddit rate limits:** Can block if scraping too fast
3. **RSS availability:** Some feeds may change URLs
4. **GitHub token:** Needs refresh every ~1 year

---

*Keep this file handy! 🐿️🔧*
