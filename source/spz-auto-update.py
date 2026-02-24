#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPZ Auto-Update Script v2.2
Updates RSS, Reddit, Twitter feeds and uploads to GitHub
SIMPLIFIED: Removed complex threading that caused Windows hangs
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import subprocess
import shutil
import time
import glob
from datetime import datetime, timedelta

# Configuration
GITHUB_REPO = "cliffyjoe25-lgtm/sppz"
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN_HERE"
FEEDS_DIR = "spz-feeds/"
REPO_DIR = "spz-repo-temp/"
BACKUP_RETENTION_HOURS = 4

def safe_remove_dir(path):
    """Safely remove directory - aggressive Windows handling"""
    if not os.path.exists(path):
        return True
    
    # Try multiple times with increasing delays
    for attempt in range(3):
        try:
            # Release file locks by chmod first
            for root, dirs, files in os.walk(path):
                for d in dirs:
                    try:
                        os.chmod(os.path.join(root, d), 0o777)
                    except:
                        pass
                for f in files:
                    try:
                        os.chmod(os.path.join(root, f), 0o666)
                    except:
                        pass
            
            time.sleep(0.5)  # Wait for locks to release
            
            # Try to remove
            shutil.rmtree(path, ignore_errors=True)
            
            # Verify it's gone
            time.sleep(0.2)
            if not os.path.exists(path):
                return True
                
        except Exception as e:
            print(f"[WARN] Cleanup attempt {attempt+1} failed: {e}")
            time.sleep(0.5)
    
    # If all attempts failed, try force remove with system command
    try:
        import subprocess
        subprocess.run(['rmdir', '/s', '/q', path], capture_output=True, timeout=5)
        if not os.path.exists(path):
            return True
    except:
        pass
    
    return False

def cleanup_old_backups():
    """Remove local XML files older than 4 hours"""
    print("\n[BACKUP] Checking for old local files...")
    cutoff_time = datetime.now() - timedelta(hours=BACKUP_RETENTION_HOURS)
    
    xml_files = glob.glob(os.path.join(FEEDS_DIR, "*.xml"))
    removed = 0
    kept = 0
    
    for filepath in xml_files:
        try:
            mtime = os.path.getmtime(filepath)
            file_time = datetime.fromtimestamp(mtime)
            
            if file_time < cutoff_time:
                os.remove(filepath)
                removed += 1
                print(f"   [CLEANUP] Removed: {os.path.basename(filepath)}")
            else:
                kept += 1
        except Exception as e:
            print(f"   [WARN] Could not process {filepath}: {e}")
    
    print(f"[BACKUP] Kept {kept} recent, removed {removed} old")
    return removed

def run_scraper(script_name, description):
    """Run a scraper with simple timeout"""
    print(f"\n[SOURCE] {description}")
    print(f"[RUN] {script_name}...")
    
    start_time = time.time()
    
    try:
        # Increased timeout for more sources
        result = subprocess.run(
            ["python", script_name],
            capture_output=True,
            text=True,
            timeout=600,  # 10 min timeout per scraper
            encoding='utf-8',
            errors='replace'
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"[OK] {description} done in {elapsed:.1f}s")
            if result.stdout:
                # Show last 5 lines
                lines = result.stdout.strip().split('\n')[-5:]
                for line in lines:
                    if line.strip():
                        print(f"   {line[:78]}")
            return True
        else:
            print(f"[ERROR] {description} failed (exit {result.returncode})")
            if result.stderr:
                err = result.stderr[-150:] if len(result.stderr) > 150 else result.stderr
                print(f"   [ERR] {err}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {description} exceeded 300s limit - skipped")
        return False
    except Exception as e:
        print(f"[ERROR] {description} crashed: {e}")
        return False

def upload_to_github():
    """Upload all local XML files to GitHub"""
    print("\n[GITHUB] Starting upload...")
    
    # Use timestamped directory to avoid conflicts  
    import random
    REPO_DIR_UNIQUE = f"{REPO_DIR}{int(time.time())}-{random.randint(1000,9999)}"
    
    # Clean up old temp directories first  
    safe_remove_dir(REPO_DIR)
    
    try:
        # Clone the repo to unique directory
        print("[GIT] Cloning repository...")
        result = subprocess.run(
            ["git", "clone", f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git", REPO_DIR_UNIQUE],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            print(f"[ERROR] Clone failed: {result.stderr}")
            safe_remove_dir(REPO_DIR_UNIQUE)
            return False
        
        # Copy XML files
        print("[GIT] Copying XML files...")
        copied = 0
        for filename in os.listdir(FEEDS_DIR):
            if filename.endswith('.xml'):
                src = os.path.join(FEEDS_DIR, filename)
                dst = os.path.join(REPO_DIR_UNIQUE, filename)
                try:
                    shutil.copy2(src, dst)
                    copied += 1
                    print(f"   - {filename}")
                except Exception as e:
                    print(f"   [SKIP] {filename}: {e}")
        
        if copied == 0:
            print("[WARN] No XML files found")
            return False
        
        # Git config
        subprocess.run(["git", "-C", REPO_DIR_UNIQUE, "config", "user.email", "spz@auto.update"], 
                      capture_output=True, timeout=10)
        subprocess.run(["git", "-C", REPO_DIR_UNIQUE, "config", "user.name", "SPZ Auto"], 
                      capture_output=True, timeout=10)
        
        # Add and commit
        subprocess.run(["git", "-C", REPO_DIR_UNIQUE, "add", "."], 
                      capture_output=True, timeout=10)
        
        # Check for changes
        status = subprocess.run(["git", "-C", REPO_DIR_UNIQUE, "status", "--porcelain"],
                               capture_output=True, text=True, timeout=10)
        if not status.stdout.strip():
            print("[OK] No changes to commit")
            return True
        
        # Commit
        msg = f"Auto-update {datetime.now().strftime('%Y-%m-%d %H:%M')} - {copied} feeds"
        commit = subprocess.run(["git", "-C", REPO_DIR_UNIQUE, "commit", "-m", msg],
                               capture_output=True, text=True, timeout=10)
        if commit.returncode != 0:
            print(f"[ERROR] Commit failed: {commit.stderr}")
            return False
        
        # Push
        print("[GIT] Pushing...")
        push = subprocess.run(["git", "-C", REPO_DIR_UNIQUE, "push"],
                             capture_output=True, text=True, timeout=30)
        if push.returncode != 0:
            print(f"[ERROR] Push failed: {push.stderr}")
            return False
        
        print(f"\n[OK] Uploaded {copied} files to GitHub!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Git upload failed: {e}")
        return False
    finally:
        safe_remove_dir(REPO_DIR_UNIQUE)

def main():
    print("=" * 65)
    print(f"SPZ Auto-Update v2.2 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 65)
    
    os.makedirs(FEEDS_DIR, exist_ok=True)
    
    total_start = time.time()
    
    # PHASE 1: SCRAPE
    print("\n" + "=" * 65)
    print("PHASE 1: SCRAPING")
    print("=" * 65)
    
    rss_ok = run_scraper("spz-rss-scraper/multi_feed_generator.py", "RSS Feeds")
    reddit_ok = run_scraper("spz-reddit-xml-generator.py", "Reddit Posts")
    twitter_ok = run_scraper("spz-twitter-nitter.py", "Twitter Feeds")
    
    scraping_time = time.time() - total_start
    print(f"\n[PHASE 1] Done in {scraping_time:.1f}s")
    
    # Count local files
    local_files = [f for f in os.listdir(FEEDS_DIR) if f.endswith('.xml')]
    print(f"[LOCAL] {len(local_files)} XML files available")
    
    # PHASE 2: UPLOAD (even if scraping failed, use existing files)
    print("\n" + "=" * 65)
    print("PHASE 2: GITHUB UPLOAD")
    print("=" * 65)
    
    upload_start = time.time()
    upload_ok = upload_to_github()
    upload_time = time.time() - upload_start
    
    if upload_ok:
        print(f"[PHASE 2] Done in {upload_time:.1f}s")
    else:
        print(f"[PHASE 2] Failed after {upload_time:.1f}s")
    
    # PHASE 3: CLEANUP
    print("\n" + "=" * 65)
    print("PHASE 3: CLEANUP")
    print("=" * 65)
    removed = cleanup_old_backups()
    
    # Summary
    total_time = time.time() - total_start
    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    print(f"RSS Scraping:     {'✅ Success' if rss_ok else '❌ Failed'}")
    print(f"Reddit Scraping:  {'✅ Success' if reddit_ok else '❌ Failed'}")
    print(f"Twitter Scraping: {'✅ Success' if twitter_ok else '❌ Failed'}")
    print(f"GitHub Upload:    {'✅ Success' if upload_ok else '❌ Failed'}")
    print(f"Old files:        {removed} cleaned")
    print(f"Total time:       {total_time:.1f}s")
    print("=" * 65)
    
    return upload_ok

if __name__ == "__main__":
    # Ensure we run from the script's directory (fixes cron path issues)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"[INIT] Working directory: {script_dir}")
    
    success = main()
    sys.exit(0 if success else 1)

