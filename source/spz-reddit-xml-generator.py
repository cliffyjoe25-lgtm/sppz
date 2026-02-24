#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPZ Reddit XML Generator v3.0 - With Media Extraction
Extracts images/videos directly from Reddit posts
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from datetime import datetime, timezone
import time
import os
import re
import requests

REDDIT_SUBREDDITS = [
    {"name": "r/Israel", "subreddit": "Israel", "category": "news", "priority": "high"},
    {"name": "r/Judaism", "subreddit": "Judaism", "category": "community", "priority": "medium"},
    {"name": "r/Jewish", "subreddit": "Jewish", "category": "community", "priority": "medium"},
    {"name": "r/Zionism", "subreddit": "Zionism", "category": "politics", "priority": "medium"},
    {"name": "r/TelAviv", "subreddit": "TelAviv", "category": "local", "priority": "low"},
    {"name": "r/2ndYomKippurWar", "subreddit": "2ndYomKippurWar", "category": "war", "priority": "high"},
    {"name": "r/IsraelHamasWar", "subreddit": "IsraelHamasWar", "category": "war", "priority": "high"},
    {"name": "r/CombatFootage", "subreddit": "CombatFootage", "category": "military", "priority": "medium"},
    {"name": "r/IronSwords", "subreddit": "IronSwords", "category": "war", "priority": "high"},
    {"name": "r/MiddleEastNews", "subreddit": "MiddleEastNews", "category": "news", "priority": "high"},
    {"name": "r/Geopolitics", "subreddit": "Geopolitics", "category": "analysis", "priority": "high"},
    {"name": "r/CredibleDefense", "subreddit": "CredibleDefense", "category": "military", "priority": "high"},
    {"name": "r/WorldNews", "subreddit": "WorldNews", "category": "news", "priority": "high"},
    {"name": "r/News", "subreddit": "News", "category": "news", "priority": "high"},
]

CONFIG = {
    "posts_per_subreddit": 5,          # Reduced from 10
    "score_threshold": 10,
    "timeout": 10,
    "output_dir": "spz-feeds/",
    "user_agent": "Mozilla/5.0 (compatible; SPZ-Research/1.0; Bot)",
    "delay_between_subreddits": 2.0,   # Reduced from 4.0
}

os.makedirs(CONFIG['output_dir'], exist_ok=True)


def format_rfc2822(dt=None):
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S %z")


def escape_xml(text):
    if not text:
        return ""
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&apos;"))


def extract_media_urls(post_data):
    """Extract image/video URLs from Reddit post"""
    media_urls = []
    
    # Thumbnail
    thumb = post_data.get('thumbnail')
    if thumb and thumb not in ['self', 'default', 'nsfw', 'spoiler', '']:
        media_urls.append(('thumbnail', thumb if thumb.startswith('http') else f'https://{thumb}', 'image'))
    
    # Preview images
    preview = post_data.get('preview', {})
    if preview and 'images' in preview:
        for img in preview['images']:
            if 'source' in img and 'url' in img['source']:
                url = img['source']['url'].replace('&amp;', '&')
                media_urls.append(('preview', url, 'image'))
    
    # Reddit video
    media = post_data.get('media', {}).get('reddit_video', {})
    if media.get('fallback_url'):
        media_urls.append(('reddit_video', media['fallback_url'], 'video'))
    if media.get('scrubber_media_url'):
        media_urls.append(('reddit_thumb', media['scrubber_media_url'], 'image'))
    
    # External media thumbnail
    secure_media = post_data.get('secure_media', {}).get('oembed', {})
    if secure_media.get('thumbnail_url'):
        media_urls.append(('oembed', secure_media['thumbnail_url'], 'image'))
    
    # Direct image/video from URL
    url = post_data.get('url', '')
    if 'i.redd.it' in url or url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
        media_urls.append(('direct', url, 'image'))
    elif 'v.redd.it' in url or url.endswith(('.mp4', '.webm', '.mov')):
        media_urls.append(('direct', url, 'video'))
    
    # Deduplicate
    seen = set()
    unique = []
    for src, url, mtype in media_urls:
        if url not in seen:
            seen.add(url)
            unique.append((src, url, mtype))
    
    return unique[:2]  # Top 2


def calculate_dual_score(post):
    """Combined content + engagement score"""
    title = post.get('title', '').lower()
    keywords = ['israel', 'gaza', 'war', 'hamas', 'trump', 'ukraine', 'attack']
    content_score = sum(5 for kw in keywords if kw in title)
    
    upvotes = post.get('score', 0)
    comments = post.get('num_comments', 0)
    ratio = post.get('upvote_ratio', 0.5)
    
    engagement = (upvotes * 0.01) + (comments * 0.1) + (ratio * 10)
    
    return round(min(100, content_score + engagement), 1)


def get_tier(score):
    if score >= 80: return "S"
    if score >= 65: return "A"
    if score >= 50: return "B"
    if score >= 35: return "C"
    return "D"


def create_twitter_summary(post):
    title = post.get('title', '')[:100]
    subreddit = post.get('subreddit', '')
    score = post.get('score', 0)
    permalink = post.get('permalink', '')
    return f"{title}...\n(r/{subreddit} | {score}🔺)\n👉 https://reddit.com{permalink}"


def build_rss_description(post, media_urls):
    parts = []
    score = post.get('score', 0)
    comments = post.get('num_comments', 0)
    tier = post.get('tier', '?')
    dual = post.get('dual_score', 0)
    
    # Header
    parts.append(f'<div style="padding:10px;background:#f6f8fa;border-radius:6px;margin-bottom:10px;">')
    parts.append(f'🔺 <strong>{score}</strong> | 💬 <strong>{comments}</strong> | דירוג: <strong>{tier}</strong> ({dual}/100)')
    parts.append('</div>')
    
    # MEDIA
    if media_urls:
        parts.append('<div style="margin:15px 0;text-align:center;">')
        for src, url, mtype in media_urls:
            if mtype == 'image':
                parts.append(f'<img src="{url}" style="max-width:100%;max-height:400px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);" /><br/><br/>')
            elif mtype == 'video':
                parts.append(f'<video controls style="max-width:100%;border-radius:8px;"><source src="{url}" type="video/mp4" /></video><br/><br/>')
        parts.append('</div>')
    
    # Content
    selftext = post.get('selftext', '')
    if selftext:
        clean = re.sub(r'<[^>]+>', ' ', selftext).strip()[:600]
        if len(selftext) > 600:
            clean += "..."
        parts.append(f'<p style="line-height:1.6;">{escape_xml(clean)}</p>')
    
    # Links
    parts.append(f'<div style="margin-top:15px;padding:12px;background:#f0f0f0;border-radius:6px;text-align:center;">')
    parts.append(f'<a href="https://reddit.com{post.get("permalink", "")}">🔗 צפה בפוסט ברדיט</a>')
    if post.get('url') and not post.get('is_self'):
        parts.append(f' | <a href="{post["url"]}">🌐 קישור</a>')
    parts.append('</div>')
    
    return "\n".join(parts)


def fetch_subreddit_posts(subreddit_config):
    subreddit = subreddit_config['subreddit']
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={CONFIG['posts_per_subreddit']}"
    headers = {"User-Agent": CONFIG['user_agent']}
    
    try:
        resp = requests.get(url, headers=headers, timeout=CONFIG['timeout'])
        resp.raise_for_status()
        data = resp.json()
        
        posts = []
        for child in data.get('data', {}).get('children', []):
            pd = child.get('data', {})
            
            if pd.get('score', 0) < CONFIG['score_threshold']:
                continue
            if pd.get('stickied'):
                continue
            
            # Filter out Ukraine-related posts
            title_lower = (pd.get('title', '') or '').lower()
            selftext_lower = (pd.get('selftext', '') or '').lower()
            combined = title_lower + ' ' + selftext_lower
            
            # === CONTENT FILTERS ===
            # POSITIVE: Israel/Jewish context (always allow)
            israel_context = [
                'israel', 'israeli', 'israelis', 'gaza', 'palestine', 'palestinian', 
                'idf', 'jerusalem', 'netanyahu', 'tel aviv', 'hamas', 
                'jew', 'jewish', 'jews', 'zionist', 'zionism', 'judaism', 'rabbi',
                'yom kippur', 'rosh hashanah', 'passover', 'hanukkah', 'shabbat',
                'gal gadot', 'natalie portman', 'bar refaeli', 'yair lapid', 
                'mossad', 'knesset', 'aliyah'
            ]
            has_israel_context = any(kw in combined for kw in israel_context)
            
            # NEGATIVE: Other countries (block unless has Israel context)
            other_countries = [
                'ukraine', 'ukrainian', 'kyiv', 'kharkiv', 'odesa', 'odessa', 'luhansk', 'donetsk', 'kiev',
                'russia', 'russian', 'putin', 'kremlin', 'moscow', 'vladimir',
                'france', 'french', 'macron', 'paris', 'germany', 'german', 'merkel', 'scholz', 'berlin',
                'uk', 'british', 'britain', 'england', 'london', 'boris johnson', 'rishi sunak',
                'italy', 'italian', 'rome', 'meloni', 'spain', 'spanish', 'madrid',
                'china', 'chinese', 'beijing', 'xi jinping', 'japan', 'japanese', 'tokyo',
                'india', 'indian', 'modi', 'pakistan', 'bangladesh',
                'iran', 'iranian', 'tehran', 'iraq', 'iraqi', 'baghdad', 
                'syria', 'syrian', 'damascus', 'assad', 'lebanon', 'lebanese', 'beirut',
                'turkey', 'turkish', 'erdogan', 'istanbul',
                'egypt', 'egyptian', 'cairo', 'saudi', 'uae', 'dubai', 'qatar',
                'usa', 'united states', 'america', 'american', 'biden', 'trump',
                'canada', 'canadian', 'trudeau', 'mexico', 'mexican',
                'brazil', 'brazilian', 'lula', 'argentina', 'chile', 'colombia',
                'south africa', 'nigeria', 'kenya', 'australia', 'australian'
            ]
            is_about_other = any(kw in combined for kw in other_countries)
            
            if is_about_other and not has_israel_context:
                print(f"   [FILTERED] Non-Israel content skipped: {pd.get('title', '')[:40]}...")
                continue
            
            post = {
                'id': pd.get('id'),
                'subreddit': pd.get('subreddit'),
                'title': pd.get('title', ''),
                'selftext': pd.get('selftext', ''),
                'url': pd.get('url', ''),
                'permalink': pd.get('permalink', ''),
                'author': pd.get('author', ''),
                'score': pd.get('score', 0),
                'num_comments': pd.get('num_comments', 0),
                'upvote_ratio': pd.get('upvote_ratio', 0),
                'domain': pd.get('domain', ''),
                'is_self': pd.get('is_self', False),
                'fetched_at': format_rfc2822(),
                'category': subreddit_config.get('category', 'reddit'),
            }
            
            post['media_urls'] = extract_media_urls(pd)
            post['dual_score'] = calculate_dual_score(post)
            post['tier'] = get_tier(post['dual_score'])
            posts.append(post)
        
        media_count = sum(1 for p in posts if p['media_urls'])
        print(f"   [OK] {len(posts)} posts ({media_count} with media)")
        return posts
        
    except Exception as e:
        print(f"   [ERR] {str(e)[:40]}")
        return []


def generate_feed_xml(items, title, desc, filename):
    items = items or []
    
    items.sort(key=lambda x: (-x.get('dual_score', 0), -x.get('score', 0)))
    date = format_rfc2822()
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/">')
    xml.append('<channel>')
    xml.append(f'  <title>{escape_xml(title)}</title>')
    xml.append(f'  <link>https://spz.local/{filename}</link>')
    xml.append(f'  <description>{escape_xml(desc)}</description>')
    xml.append(f'  <lastBuildDate>{date}</lastBuildDate>')
    
    for item in items:
        xml.append('  <item>')
        xml.append(f'    <title>{escape_xml(item["title"])}</title>')
        xml.append(f'    <link>https://reddit.com{item["permalink"]}</link>')
        
        media = item.get('media_urls', [])
        desc_content = build_rss_description(item, media)
        xml.append(f'    <description><![CDATA[{desc_content}]]></description>')
        
        # Enclosure for first media
        if media:
            url, mtype = media[0][1], media[0][2]
            mtype_full = 'video/mp4' if mtype == 'video' else 'image/jpeg'
            xml.append(f'    <enclosure url="{url}" type="{mtype_full}" />')
            xml.append(f'    <media:content url="{url}" type="{mtype_full}" />')
        
        xml.append(f'    <dual_score>{item["dual_score"]}</dual_score>')
        xml.append(f'    <tier>{item["tier"]}</tier>')
        xml.append('  </item>')
    
    xml.append('</channel>')
    xml.append('</rss>')
    
    return '\n'.join(xml)


def save_feed(xml_content, filename):
    with open(os.path.join(CONFIG['output_dir'], filename), 'w', encoding='utf-8') as f:
        f.write(xml_content)


def main():
    print("="*60)
    print("SPZ Reddit XML Generator v3.0 - With Media")
    print("="*60)
    
    all_posts = []
    for idx, cfg in enumerate(REDDIT_SUBREDDITS, 1):
        print(f"[{idx}/{len(REDDIT_SUBREDDITS)}] {cfg['name']}")
        posts = fetch_subreddit_posts(cfg)
        if posts:
            all_posts.extend(posts)
        time.sleep(CONFIG.get('delay_between_subreddits', 2.5))
    
    print(f"\nTotal: {len(all_posts)} posts, {sum(1 for p in all_posts if p['media_urls'])} with media")
    
    if not all_posts:
        return
    
    all_posts.sort(key=lambda x: (-x['dual_score'], -x['score']))
    
    feeds = [
        ('reddit-top10.xml', all_posts[0:10], 'Reddit Top 10', 'Top posts'),
        ('reddit-hot.xml', all_posts[10:20], 'Reddit Hot', 'Hot posts'),
        ('reddit-trending.xml', all_posts[20:30], 'Reddit Trending', 'Trending'),
        ('reddit-fresh.xml', all_posts[30:40], 'Reddit Fresh', 'Fresh posts'),
    ]
    
    for filename, items, title, desc in feeds:
        # Always create file, even with 0 posts
        items = items if items else []
        xml = generate_feed_xml(items, title, desc, filename)
        if xml:
            save_feed(xml, filename)
            media_cnt = sum(1 for p in items if p.get('media_urls'))
            print(f"[SAVED] {filename} ({len(items)} posts, {media_cnt} with media)")
    
    print("\n[DONE]")


if __name__ == "__main__":
    main()
