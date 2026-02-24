#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPZ Nitter Twitter Scraper
Scrapes Twitter via Nitter RSS feeds (no API token needed)
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
import xml.etree.ElementTree as ET

# Nitter instances (try multiple if one fails)
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.net",
    "https://nitter.it",
]

# Twitter accounts to scrape (Full list restored)
ACCOUNTS = [
    # Israeli Officials & News
    "netanyahu",
    "IsraeliPM",
    "Israel",
    "IDF",
    "Mossadil",
    "IsraelMFA",
    
    # Israeli Media
    "Jerusalem_Post",
    "haaretzcom",
    "ynetnews",
    "i24NEWS_EN",
    "TimesofIsrael",
    "IsraelHayomEng",
    
    # Israeli Politicians & Figures
    "naftalibennett",
    "yairlapid",
    "gantzbe",
    "AvigdorLiberman",
    "ariyederi",
    
    # Tech & Geopolitics
    "elonmusk",
    "michaelisikoff",
    "GeopoliticalCris",
    
    # Middle East Analysts
    "AbrahamHayder",
    "SaraHusseinA",
    "KhaledABselim",
    
    # International Media
    "BBCBreaking",
    "CNN",
    "nytimes",
    "Reuters",
    "AP",
]

CONFIG = {
    "output_dir": "spz-feeds/",
    "timeout": 12,
    "max_tweets_per_account": 5,        # Reduced from 10
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "delay_between_accounts": 2.5,      # Reduced from 5.0
    "max_total_time": 600,              # 10 min max
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


def fetch_nitter_feed(username, instance_idx=0, max_retries=2):
    """Fetch RSS feed from Nitter with limited retries"""
    if instance_idx >= len(NITTER_INSTANCES) or instance_idx > max_retries:
        print(f"   [SKIP] @{username} - all instances failed")
        return None
    
    base_url = NITTER_INSTANCES[instance_idx]
    url = f"{base_url}/{username}/rss"
    headers = {"User-Agent": CONFIG['user_agent']}
    
    try:
        print(f"   [TRY] {base_url}/@{username}")
        resp = requests.get(url, headers=headers, timeout=CONFIG['timeout'])
        
        if resp.status_code == 200:
            return resp.text
        elif resp.status_code == 404:
            print(f"   [404] Account not found: @{username}")
            return None
        else:
            # Try next instance
            return fetch_nitter_feed(username, instance_idx + 1, max_retries)
            
    except Exception as e:
        print(f"   [ERR] {str(e)[:40]}")
        # Try next instance
        return fetch_nitter_feed(username, instance_idx + 1, max_retries)


def parse_tweets(rss_content, username):
    """Parse RSS content into tweet objects"""
    tweets = []
    
    try:
        root = ET.fromstring(rss_content)
        
        for item in root.findall('.//item'):
            title = item.find('title')
            link = item.find('link')
            pub_date = item.find('pubDate')
            description = item.find('description')
            
            # Extract tweet text from title or description
            text = ""
            if title is not None and title.text:
                text = title.text
            elif description is not None and description.text:
                text = description.text
            
            # Clean up text
            text = re.sub(r'<[^>]+>', ' ', text).strip()
            
            # Get tweet ID from link
            tweet_id = ""
            if link is not None and link.text:
                match = re.search(r'/status/(\d+)', link.text)
                if match:
                    tweet_id = match.group(1)
            
            # Parse date
            date_str = ""
            if pub_date is not None and pub_date.text:
                date_str = pub_date.text
            
            tweet = {
                'id': tweet_id or str(int(time.time())),
                'username': username,
                'text': text[:500],
                'url': link.text if link is not None else f"https://twitter.com/{username}/status/{tweet_id}",
                'published': date_str,
                'fetched_at': format_rfc2822(),
            }
            tweets.append(tweet)
            
    except ET.ParseError as e:
        print(f"   [PARSE ERR] {str(e)[:50]}")
        return []
    
    return tweets[:CONFIG['max_tweets_per_account']]


def has_israel_context(text):
    """Check if content has Israel/Jewish context"""
    text = text.lower()
    israel_keywords = [
        'israel', 'israeli', 'israelis', 'gaza', 'palestine', 'palestinian', 
        'idf', 'jerusalem', 'netanyahu', 'tel aviv', 'hamas', 
        'jew', 'jewish', 'jews', 'zionist', 'zionism', 'judaism', 'rabbi',
        'yom kippur', 'rosh hashanah', 'passover', 'hanukkah', 'shabbat',
        'gal gadot', 'natalie portman', 'bar refaeli', 'yair lapid', 
        'benjamin netanyahu', 'benny gantz', 'naftali bennett',
        'mossad', 'shin bet', 'knesset', 'aliyah', 'diaspora'
    ]
    return any(kw in text for kw in israel_keywords)


def is_about_other_country(text):
    """Check if content is about other countries (not Israel)"""
    text = text.lower()
    other_countries = [
        # Ukraine
        'ukraine', 'ukrainian', 'kyiv', 'kharkiv', 'odesa', 'odessa', 'luhansk', 'donetsk', 'kiev',
        # Russia
        'russia', 'russian', 'putin', 'kremlin', 'moscow', 'vladimir',
        # Europe
        'france', 'french', 'macron', 'paris', 'germany', 'german', 'merkel', 'scholz', 'berlin',
        'uk', 'british', 'britain', 'england', 'london', 'boris johnson', 'rishi sunak',
        'italy', 'italian', 'rome', 'meloni', 'spain', 'spanish', 'madrid', 'poland', 'sweden',
        'norway', 'denmark', 'netherlands', 'belgium', 'switzerland', 'austria',
        # Asia
        'china', 'chinese', 'beijing', 'xi jinping', 'japan', 'japanese', 'tokyo',
        'south korea', 'korean', 'seoul', 'north korea', 'pyongyang', 'kim jong',
        'india', 'indian', 'modi', 'pakistan', 'bangladesh', 'thailand', 'vietnam',
        'singapore', 'malaysia', 'indonesia', 'philippines', 'myanmar', 'cambodia',
        # Middle East (non-Israel)
        'iran', 'iranian', 'tehran', 'iraq', 'iraqi', 'baghdad', 'syria', 'syrian', 'damascus', 'assad',
        'lebanon', 'lebanese', 'beirut', 'hezbollah', 'jordan', 'jordanian', 'amman',
        'egypt', 'egyptian', 'cairo', 'turkey', 'turkish', 'erdogan', 'istanbul', 'ankara',
        'saudi', 'saudi arabia', 'riyadh', 'uae', 'emirates', 'dubai', 'qatar', 'doha',
        'kuwait', 'bahrain', 'oman', 'yemen', 'yemeni', 'houthi',
        # Americas
        'usa', 'united states', 'america', 'american', 'biden', 'canada', 'canadian', 'trudeau',
        'mexico', 'mexican', 'brazil', 'brazilian', 'lula', 'argentina', 'chile', 'colombia',
        'venezuela', 'peru', 'bolivia', 'uruguay', 'paraguay',
        # Africa
        'south africa', 'nigeria', 'kenya', 'ethiopia', 'ghana', 'morocco', 'algeria', 'tunisia', 'libya', 'sudan',
        # Australia
        'australia', 'australian', 'new zealand',
    ]
    return any(kw in text for kw in other_countries)


def calculate_score(tweet):
    """Calculate relevance score with strict filtering"""
    text = tweet['text'].lower()
    
    # STRICT FILTER: Only allow if has Israel context OR not about other countries
    if is_about_other_country(text) and not has_israel_context(text):
        return -100  # Will be filtered out
    
    score = 50  # Base
    
    high_keywords = ['israel', 'gaza', 'hamas', 'war', 'attack', 'netanyahu', 'idf']
    medium_keywords = ['jerusalem', 'palestine', 'middle east', 'trump', 'iran']
    
    for kw in high_keywords:
        if kw in text:
            score += 10
    for kw in medium_keywords:
        if kw in text:
            score += 5
    
    return min(100, score)


def create_twitter_summary(tweet):
    """Create twitter-compatible summary"""
    text = tweet['text'][:200]
    username = tweet['username']
    url = tweet['url']
    return f"@{username}: {text}...\n👉 {url}"


def build_rss_description(tweet):
    """Build HTML description for RSS"""
    parts = []
    
    # Header
    parts.append(f'<div style="padding:10px;background:#1da1f2;border-radius:6px;margin-bottom:10px;color:white;">')
    parts.append(f'🐦 <strong>@{tweet["username"]}</strong>')
    parts.append(f'</div>')
    
    # Tweet text
    text = escape_xml(tweet['text'])
    # Linkify URLs
    text = re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', text)
    # Linkify mentions
    text = re.sub(r'@(\w+)', r'<a href="https://twitter.com/\1">@\1</a>', text)
    # Linkify hashtags
    text = re.sub(r'#(\w+)', r'<a href="https://twitter.com/hashtag/\1">#\1</a>', text)
    
    parts.append(f'<p style="font-size:16px;line-height:1.6;padding:10px;">{text}</p>')
    
    # Timestamp
    parts.append(f'<div style="color:#666;font-size:12px;margin-top:10px;">')
    parts.append(f'📅 {tweet["published"] or tweet["fetched_at"]}')
    parts.append(f'</div>')
    
    # Link to tweet
    parts.append(f'<div style="margin-top:15px;padding:12px;background:#f0f0f0;border-radius:6px;text-align:center;">')
    parts.append(f'<a href="{tweet["url"]}" target="_blank"><strong>🔗 צפה בציוץ בטוויטר ←</strong></a>')
    parts.append(f'</div>')
    
    return "\n".join(parts)


def generate_twitter_rss(tweets, filename, title='SPZ Twitter Aggregator', desc='Twitter feed via Nitter'):
    """Generate RSS feed from tweets"""
    tweets = tweets or []
    
    date = format_rfc2822()
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">')
    xml.append('<channel>')
    xml.append(f'  <title>{title}</title>')
    xml.append(f'  <link>https://spz.local/{filename}</link>')
    xml.append(f'  <description>{desc}</description>')
    xml.append(f'  <lastBuildDate>{date}</lastBuildDate>')
    xml.append('  <language>en</language>')
    
    for tweet in tweets:
        xml.append('  <item>')
        xml.append(f'    <title>{escape_xml(tweet["text"][:100])}...</title>')
        xml.append(f'    <link>{tweet["url"]}</link>')
        xml.append(f'    <guid isPermaLink="true">{tweet["url"]}</guid>')
        xml.append(f'    <description><![CDATA[{build_rss_description(tweet)}]]></description>')
        xml.append(f'    <twitter_summary><![CDATA[{create_twitter_summary(tweet)}]]></twitter_summary>')
        xml.append(f'    <twitter:username>@{tweet["username"]}</twitter:username>')
        xml.append(f'    <score>{tweet["score"]}</score>')
        xml.append(f'    <pubDate>{tweet["fetched_at"]}</pubDate>')
        xml.append('  </item>')
    
    xml.append('</channel>')
    xml.append('</rss>')
    
    return '\n'.join(xml)


def main():
    print("=" * 60)
    print("SPZ Twitter Scraper via Nitter")
    print("=" * 60)
    
    all_tweets = []
    
    for idx, username in enumerate(ACCOUNTS, 1):
        print(f"\n[{idx}/{len(ACCOUNTS)}] @{username}")
        
        rss_content = fetch_nitter_feed(username)
        if rss_content:
            tweets = parse_tweets(rss_content, username)
            print(f"   [OK] {len(tweets)} tweets")
            
            # Calculate scores
            for tweet in tweets:
                tweet['score'] = calculate_score(tweet)
            
            # FILTER: Skip Ukraine/negative score tweets
            tweets = [t for t in tweets if t['score'] >= 0]
            
            all_tweets.extend(tweets)
        else:
            print(f"   [FAIL] Could not fetch")
        
        time.sleep(CONFIG.get('delay_between_accounts', 3.0))  # Be nice to Nitter
    
    print(f"\n{'='*60}")
    print(f"Total tweets: {len(all_tweets)}")
    print("=" * 60)
    
    if not all_tweets:
        print("[ERROR] No tweets fetched")
        return
    
    # Sort by score (highest first)
    all_tweets.sort(key=lambda x: -x.get('score', 0))
    
    # Create 4 feeds like Reddit
    feeds = [
        ('twitter-top10.xml', all_tweets[0:10], 'SPZ Twitter - Top 10', 'Highest priority tweets'),
        ('twitter-hot.xml', all_tweets[10:20], 'SPZ Twitter - Hot', 'Hot tweets'),
        ('twitter-trending.xml', all_tweets[20:30], 'SPZ Twitter - Trending', 'Trending tweets'),
        ('twitter-fresh.xml', all_tweets[30:40], 'SPZ Twitter - Fresh', 'Fresh tweets'),
    ]
    
    for filename, tweets, title, desc in feeds:
        if tweets:
            xml = generate_twitter_rss(tweets, filename, title, desc)
            if xml:
                filepath = os.path.join(CONFIG['output_dir'], filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(xml)
                print(f"[SAVED] {filename} ({len(tweets)} tweets)")
        else:
            # Create empty feed
            xml = generate_twitter_rss([], filename, title, desc)
            filepath = os.path.join(CONFIG['output_dir'], filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(xml)
            print(f"[SAVED] {filename} (0 tweets)")
    
    print("\n[DONE]")


if __name__ == "__main__":
    main()
