#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPZ Multi-Feed RSS Generator
Creates separate RSS feeds for each source
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import json
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import time
import os
import re

# Israeli News RSS Feeds
ISRAELI_FEEDS = [
    # Ynet (Hebrew)
    {"name": "Ynet Breaking News", "url": "https://www.ynet.co.il/Integration/StoryRss1854.xml", "category": "news", "language": "he", "priority": "high"},
    {"name": "Ynet Main News", "url": "https://www.ynet.co.il/Integration/StoryRss2.xml", "category": "news", "language": "he", "priority": "high"},
    {"name": "Ynet Opinions", "url": "https://www.ynet.co.il/Integration/StoryRss190.xml", "category": "opinion", "language": "he", "priority": "medium"},
    
    # Jerusalem Post
    {"name": "Jerusalem Post - Israel News", "url": "https://www.jpost.com/Rss/RssFeedsIsraelNews.aspx", "category": "news", "language": "en", "priority": "high"},
    
    # Times of Israel
    {"name": "Times of Israel - Israel News", "url": "https://www.timesofisrael.com/feed/", "category": "news", "language": "en", "priority": "high"},
    {"name": "Times of Israel - Jewish News", "url": "https://www.timesofisrael.com/jewish/feed/", "category": "news", "language": "en", "priority": "medium"},
    
    # Haaretz
    {"name": "Haaretz - Israel News", "url": "https://www.haaretz.co.il/misc/rss.xml", "category": "news", "language": "he", "priority": "high"},
    
    # Israel Hayom
    {"name": "Israel Hayom", "url": "https://www.israelhayom.co.il/rss.xml", "category": "news", "language": "he", "priority": "high"},
    
    # Walla
    {"name": "Walla News", "url": "https://rss.walla.co.il/feed/1?type=main", "category": "news", "language": "he", "priority": "high"},
    
    # International - Core
    {"name": "BBC Middle East", "url": "http://feeds.bbci.co.uk/news/world/middle_east/rss.xml", "category": "news", "language": "en", "priority": "high"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/rss.xml", "category": "news", "language": "en", "priority": "medium"},
    {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml", "category": "news", "language": "en", "priority": "medium"},
    
    {"name": "CNN Top Stories", "url": "http://rss.cnn.com/rss/edition.rss", "category": "news", "language": "en", "priority": "high"},
    {"name": "CNN World", "url": "http://rss.cnn.com/rss/edition_world.rss", "category": "news", "language": "en", "priority": "medium"},
    
    {"name": "NYT World", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "category": "news", "language": "en", "priority": "high"},
    {"name": "NYT Homepage", "url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", "category": "news", "language": "en", "priority": "medium"},
    
    {"name": "Guardian - World", "url": "https://www.theguardian.com/world/rss", "category": "news", "language": "en", "priority": "medium"},
    {"name": "Guardian - Middle East", "url": "https://www.theguardian.com/world/middleeast/rss", "category": "news", "language": "en", "priority": "high"},
    
    # Israeli Tech/Business
    {"name": "Globes", "url": "https://www.globes.co.il/webservice/rss/rssfeeder.aspx?feed=news", "category": "business", "language": "he", "priority": "medium"},
    {"name": "Calcalist", "url": "https://www.calcalist.co.il/rss", "category": "business", "language": "he", "priority": "medium"},
    
    # Other Israeli
    {"name": "Mako News", "url": "https://www.mako.co.il/rss/news-all.xml", "category": "news", "language": "he", "priority": "medium"},
    {"name": "Reshet 13 News", "url": "https://13tv.co.il/all-news/", "category": "news", "language": "he", "priority": "medium"},
    {"name": "Arutz Sheva", "url": "https://www.israelnationalnews.com/rss/", "category": "news", "language": "en", "priority": "low"},
]

CONFIG = {
    "articles_per_feed": 5,
    "score_threshold": 6,
    "timeout": 8,
    "content_timeout": 4,
    "max_summary_length": 300,
    "fetch_full_content": False,
    "extract_images": False,
    "output_dir": "spz-feeds/",
    "delay_between_requests": 1.0,      # Reduced from 3.0
    "delay_between_feeds": 2.0,         # Reduced from 4.0
}

# Ensure output directory exists
os.makedirs(CONFIG['output_dir'], exist_ok=True)


def generate_article_id(url):
    """Generate unique ID from URL"""
    return hashlib.md5(url.encode()).hexdigest()[:16]


def format_rfc2822(dt=None):
    """Format datetime to RFC 2822 format"""
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S %z")


def escape_xml(text):
    """Escape special XML characters"""
    if not text:
        return ""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;"))


def extract_image_from_html(html_content, url):
    """Extract main image from article HTML"""
    # Try Open Graph first
    og_match = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', html_content, re.I)
    if og_match:
        return og_match.group(1)
    
    # Try Twitter card
    twitter_match = re.search(r'<meta[^>]*name=["\']twitter:image["\'][^>]*content=["\']([^"\']+)["\']', html_content, re.I)
    if twitter_match:
        return twitter_match.group(1)
    
    # Try to find first image in article content
    img_match = re.search(r'<img[^>]*src=["\']([^"\']+)["\']', html_content, re.I)
    if img_match:
        img_url = img_match.group(1)
        if img_url.startswith('//'):
            return f"https:{img_url}"
        elif img_url.startswith('/'):
            domain_match = re.match(r'(https?://[^/]+)', url)
            if domain_match:
                return f"{domain_match.group(1)}{img_url}"
        return img_url
    
    return None


def extract_article_content(html_content):
    """Extract main article content from HTML"""
    clean = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', html_content, flags=re.I)
    clean = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', clean, flags=re.I)
    clean = re.sub(r'<nav[^>]*>[\s\S]*?</nav>', '', clean, flags=re.I)
    clean = re.sub(r'<header[^>]*>[\s\S]*?</header>', '', clean, flags=re.I)
    clean = re.sub(r'<footer[^>]*>[\s\S]*?</footer>', '', clean, flags=re.I)
    clean = re.sub(r'<aside[^>]*>[\s\S]*?</aside>', '', clean, flags=re.I)
    
    patterns = [
        r'<article[^>]*>([\s\S]*?)</article>',
        r'<div[^>]*class=["\'][^"\']*content[^"\']*["\'][^>]*>([\s\S]*?)</div>',
        r'<div[^>]*class=["\'][^"\']*article[^"\']*["\'][^>]*>([\s\S]*?)</div>',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, clean, re.I)
        if match:
            return match.group(1)
    
    return clean


def create_summary(content, max_length=300):
    """Create text summary from HTML content"""
    if not content:
        return ""
    
    text = re.sub(r'<[^>]+>', ' ', content)
    text = text.replace('&nbsp;', ' ').replace('&quot;', '"')
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'Share this article|Read more|Click here|Subscribe|Advertisement|Comments|Related articles', '', text, flags=re.I)
    
    if len(text) > max_length:
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > int(max_length * 0.8):
            truncated = truncated[:last_space]
        return f"{truncated}..."
    
    return text


def create_twitter_summary(article, max_length=280):
    """Create Twitter/X compatible summary (max 280 chars)
    Format: "Title + Key Points [Author | Source] URL"
    """
    title = article.get('title', '') or ''
    content = article.get('summary', '') or article.get('content', '') or ''
    author = article.get('author', '')
    source = article.get('feed_name', '')
    url = article.get('url', '')
    
    # Clean content
    clean_content = re.sub(r'<[^>]+>', ' ', content)
    clean_content = clean_content.replace('&nbsp;', ' ').replace('&quot;', '"')
    clean_content = clean_content.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    clean_content = re.sub(r'\s+', ' ', clean_content).strip()
    
    # Extract key sentences (first 2-3 sentences that convey the essence)
    sentences = re.split(r'(?<=[.!?])\s+', clean_content)
    key_points = []
    total_len = len(title) + 1
    
    for sent in sentences[:3]:
        if len(sent) > 20:  # Only meaningful sentences
            test_len = total_len + len(sent) + 2
            if test_len < max_length - 30:  # Leave room for attribution
                key_points.append(sent)
                total_len = test_len
    
    summary = ' '.join(key_points) if key_points else clean_content[:200]
    
    # Build attribution
    attr_parts = []
    if source:
        attr_parts.append(source)
    if author and author != source:
        attr_parts.append(author)
    
    attribution = f" ({' | '.join(attr_parts)})" if attr_parts else ""
    short_url = url[:50] + "..." if len(url) > 50 else url
    
    # Calculate total length
    total = len(title) + 1 + len(summary) + len(attribution) + 1 + len(short_url)
    if total > max_length:
        # Truncate content to fit
        excess = total - max_length + 5  # +5 for "..."
        summary = summary[:-excess] + "..."
    
    # Final format with separator for parsing
    twitter_text = f"{title}\n{summary}{attribution}\n👉 {url}"
    
    return twitter_text


def build_rss_description(article):
    """Build rich RSS description with image, summary, and link"""
    parts = []
    
    # 1. IMAGE AT TOP
    if article.get('image_url'):
        parts.append(f'<img src="{escape_xml(article["image_url"])}" alt="{escape_xml(article.get("title", ""))}" style="max-width:100%;height:auto;" />')
        parts.append("")
    
    # 2. SUMMARY
    summary = article.get('summary', '') or article.get('content', '')
    if summary:
        summary = re.sub(r'<[^>]+>', ' ', summary)
        summary = re.sub(r'\s+', ' ', summary).strip()
        if len(summary) > 500:
            summary = summary[:500] + "..."
        parts.append(f'<p>{escape_xml(summary)}</p>')
        parts.append("")
    
    # 3. METADATA
    parts.append('<hr />')
    parts.append("")
    
    if article.get('feed_name'):
        parts.append(f"📡 <strong>מקור:</strong> {escape_xml(article['feed_name'])}")
    
    if article.get('author'):
        parts.append(f"👤 <strong>מחבר:</strong> {escape_xml(article['author'])}")
    
    if article.get('relevancy_score'):
        parts.append(f"⭐ <strong>רלוונטיות:</strong> {article['relevancy_score']}/10")
    
    # 4. LINK AT BOTTOM
    parts.append("")
    parts.append('<div style="margin-top:15px;padding:10px;background:#f5f5f5;border-radius:5px;text-align:center;">')
    parts.append(f'🔗 <a href="{article["url"]}" target="_blank"><strong>קרא את הכתבה המלאה ←</strong></a>')
    parts.append('</div>')
    
    return "\n".join(parts)


def generate_feed_filename(feed_name):
    """Generate safe filename from feed name"""
    # Hebrew to English mapping
    hebrew_map = {
        'ynet': 'ynet',
        'ישראל': 'israel',
        'היום': 'hayom',
        'וואלה': 'walla',
        'מאקו': 'mako',
        'רשת': 'reshet',
        'כלכליסט': 'calcalist',
        'גלובס': 'globes',
    }
    
    # Remove special characters and spaces
    safe_name = feed_name.lower()
    safe_name = re.sub(r'[^\w\s-]', '', safe_name)
    safe_name = re.sub(r'[\s]+', '-', safe_name)
    safe_name = safe_name.strip('-')
    
    # Shorten if too long
    if len(safe_name) > 30:
        safe_name = safe_name[:30]
    
    return f"{safe_name}.xml"


def generate_single_feed_xml(articles, feed_info):
    """Generate RSS XML for a single feed"""
    
    if not articles:
        return None
    
    build_date = format_rfc2822()
    feed_name = feed_info['name']
    feed_lang = feed_info['language']
    
    xml_parts = []
    xml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml_parts.append('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/">')
    xml_parts.append('<channel>')
    xml_parts.append(f'  <title>{escape_xml(feed_name)}</title>')
    xml_parts.append(f'  <link>https://spz.local/{generate_feed_filename(feed_name)}</link>')
    xml_parts.append(f'  <description>Feed from {escape_xml(feed_name)} - with images and summaries</description>')
    xml_parts.append(f'  <language>{feed_lang}</language>')
    xml_parts.append(f'  <lastBuildDate>{build_date}</lastBuildDate>')
    xml_parts.append(f'  <atom:link href="https://spz.local/{generate_feed_filename(feed_name)}" rel="self" type="application/rss+xml" />')
    xml_parts.append(f'  <generator>SPZ Aggregator v2.0 (Per-Feed)</generator>')
    
    for article in articles:
        xml_parts.append('  <item>')
        xml_parts.append(f'    <title>{escape_xml(article.get("title", "Untitled"))}</title>')
        xml_parts.append(f'    <link>{article["url"]}</link>')
        xml_parts.append(f'    <guid isPermaLink="true">{article["url"]}</guid>')
        
        description = build_rss_description(article)
        xml_parts.append(f'    <description><![CDATA[{description}]]></description>')
        
        # Add Twitter summary (max 280 chars)
        twitter_summary = create_twitter_summary(article)
        xml_parts.append(f'    <twitter_summary><![CDATA[{twitter_summary}]]></twitter_summary>')
        
        if article.get('image_url'):
            xml_parts.append(f'    <enclosure url="{article["image_url"]}" type="image/jpeg" length="0" />')
            xml_parts.append(f'    <media:content url="{article["image_url"]}" type="image/jpeg" medium="image" />')
        
        pub_date = article.get('published') or article.get('fetched_at') or format_rfc2822()
        xml_parts.append(f'    <pubDate>{pub_date}</pubDate>')
        
        if article.get('feed_category'):
            xml_parts.append(f'    <category>{escape_xml(article["feed_category"])}</category>')
        
        if article.get('author'):
            xml_parts.append(f'    <author>{escape_xml(article["author"])}</author>')
        
        xml_parts.append('  </item>')
    
    xml_parts.append('</channel>')
    xml_parts.append('</rss>')
    
    return '\n'.join(xml_parts)


def save_feed(xml_content, filename):
    """Save RSS feed to file"""
    filepath = os.path.join(CONFIG['output_dir'], filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    return filepath


def fetch_feed_articles(feed, state):
    """Fetch articles from a single RSS feed"""
    import requests
    
    articles = []
    known_ids = set(state.get("known_ids", []))
    
    try:
        response = requests.get(feed['url'], timeout=CONFIG['timeout'])
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        items = root.findall('.//item')
        
        for item in items[:CONFIG['articles_per_feed']]:
            title = item.findtext('title', '')
            link = item.findtext('link', '') or item.findtext('guid', '')
            description = item.findtext('description', '')
            pub_date = item.findtext('pubDate', '')
            author = item.findtext('author', '') or item.findtext('{http://purl.org/dc/elements/1.1/}creator', '')
            
            article_id = generate_article_id(link)
            if article_id in known_ids:
                continue
            
            # === CONTENT FILTERS ===
            combined_text = f"{title} {description}".lower()
            
            # POSITIVE: Israel/Jewish context keywords (always allow)
            israel_context = [
                'israel', 'israeli', 'israelis', 'gaza', 'palestine', 'palestinian', 
                'idf', 'jerusalem', 'netanyahu', 'tel aviv', 'hamas', 
                'jew', 'jewish', 'jews', 'zionist', 'zionism', 'judaism', 'rabbi',
                'yom kippur', 'rosh hashanah', 'passover', 'hanukkah', 'shabbat',
                # Israeli celebrities/politicians
                'gal gadot', 'natalie portman', 'bar refaeli', 'yair lapid', 
                'benjamin netanyahu', 'benny gantz', 'naftali bennett',
                'mossad', 'shin bet', 'knesset', 'aliyah', 'diaspora'
            ]
            has_israel_context = any(kw in combined_text for kw in israel_context)
            
            # RELAXED FILTER: Only block obvious spam/non-news
            # Removed strict country blocking - keeping only spam/entertainment filters
            blocked_content = [
                # Spam/promotional patterns
                'click here to', 'subscribe now', 'limited time offer',
                'buy now', 'sale ends', 'discount code',
                # Explicit adult content (spam filter)
                'porn', 'xxx', 'adult video', 'sex dating',
                # Casino/gambling spam
                'online casino', 'slot machine', 'bet now', 'gambling',
            ]
            
            # Check for spam only
            has_blocked = any(kw in combined_text for kw in blocked_content)
            
            if has_blocked:
                continue
            
            # Boost score for Israel-relevant content
            score_boost = 3 if has_israel_context else 0
            
            # All other content is now allowed (relaxed filter)
            
            # Check for enclosure image
            enclosure = item.find('enclosure')
            rss_image = None
            if enclosure is not None:
                rss_image = enclosure.get('url')
            
            article = {
                'id': article_id,
                'title': title,
                'content': description,
                'url': link,
                'published': pub_date,
                'author': author,
                'feed_name': feed['name'],
                'feed_category': feed['category'],
                'language': feed['language'],
                'fetched_at': format_rfc2822(),
                'rss_image': rss_image,
            }
            
            # Fetch full article details
            if CONFIG['extract_images'] or CONFIG['fetch_full_content']:
                try:
                    article_resp = requests.get(link, timeout=CONFIG['content_timeout'], 
                        headers={'User-Agent': 'Mozilla/5.0'})
                    
                    if article_resp.ok:
                        html = article_resp.text
                        
                        if CONFIG['extract_images']:
                            img = extract_image_from_html(html, link)
                            if img:
                                article['image_url'] = img
                            elif rss_image:
                                article['image_url'] = rss_image
                        
                        if CONFIG['fetch_full_content']:
                            content_html = extract_article_content(html)
                            summary = create_summary(content_html, CONFIG['max_summary_length'])
                            if summary:
                                article['summary'] = summary
                    
                except Exception as e:
                    pass
            
            articles.append(article)
            known_ids.add(article_id)
            time.sleep(CONFIG.get('delay_between_requests', 1.5))
        
        return articles, known_ids
        
    except Exception as e:
        print(f"   [ERROR] {e}")
        return [], known_ids


def load_state():
    """Load deduplication state"""
    try:
        with open('spz-rss-state.json', 'r') as f:
            return json.load(f)
    except:
        return {"known_ids": [], "last_fetch": None}


def save_state(state):
    """Save deduplication state"""
    with open('spz-rss-state.json', 'w') as f:
        json.dump(state, f, indent=2)


def upload_to_catbox(filepath):
    """Upload file to catbox"""
    import subprocess
    try:
        result = subprocess.run(
            ['curl', '-s', '-F', 'reqtype=fileupload', '-F', f'fileToUpload=@{filepath}', 
             'https://catbox.moe/user/api.php'],
            capture_output=True, text=True, timeout=60
        )
        return result.stdout.strip()
    except:
        return None


def main():
    import requests
    
    print("\n[STATUS] SPZ Multi-Feed RSS Generator")
    print("Creates separate RSS feeds for each source")
    print("=" * 60)
    
    state = load_state()
    all_ids = set(state.get("known_ids", []))
    
    feed_results = {}
    uploaded_urls = {}
    total_feeds = len(ISRAELI_FEEDS)
    processed_count = 0
    
    print(f"[INFO] Processing {total_feeds} RSS feeds...")
    
    for feed in ISRAELI_FEEDS:
        processed_count += 1
        print(f"\n[{processed_count}/{total_feeds}] Processing: {feed['name']}")
        
        articles, new_ids = fetch_feed_articles(feed, state)
        all_ids.update(new_ids)
        
        if articles:
            # Generate feed-specific XML
            xml_content = generate_single_feed_xml(articles, feed)
            if xml_content:
                filename = generate_feed_filename(feed['name'])
                filepath = save_feed(xml_content, filename)
                
                # Upload to catbox
                print(f"   [UPLOAD] Uploading {filename}...")
                url = upload_to_catbox(filepath)
                if url:
                    uploaded_urls[feed['name']] = url
                    print(f"   [OK] URL: {url}")
                else:
                    print(f"   [WARN] Upload failed, saved locally: {filepath}")
                
                feed_results[feed['name']] = {
                    'articles': len(articles),
                    'with_images': sum(1 for a in articles if a.get('image_url')),
                    'with_summaries': sum(1 for a in articles if a.get('summary')),
                    'filename': filename,
                    'url': url
                }
        else:
            print(f"   [INFO] No new articles")
        
        time.sleep(CONFIG.get('delay_between_feeds', 2.0))
    
    # Save state
    state['known_ids'] = list(all_ids)[-5000:]
    state['last_fetch'] = format_rfc2822()
    save_state(state)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for name, result in feed_results.items():
        print(f"\n📰 {name}")
        print(f"   Articles: {result['articles']}")
        print(f"   Images: {result['with_images']}")
        print(f"   Summaries: {result['with_summaries']}")
        if result['url']:
            print(f"   URL: {result['url']}")
    
    print(f"\n[DONE] Generated {len(feed_results)} separate feeds")


if __name__ == "__main__":
    main()
