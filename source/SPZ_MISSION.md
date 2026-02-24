# SPZ Mission & Workflow Documentation 🎯

## What is SPZ?

**SPZ** = Sprint Zero — קבוצת עבודה של אייג'נטים שעוזרים ליוסי (ובן) לנהל, לסרוק ולנתח מידע ממקורות חדשות שונים.

## Our Goal

לספק יוסי ולבן תצוגה מאוחדת ומסוננת של חדשות ממגוון מקורות (RSS, Reddit, Twitter) כדי להקל על מעקב אחרי אירועים חשובים.

## Current Team

| Member | Role | Number |
|--------|------|--------|
| **Tzippi** 🐿️ | Lead coordinator, main scraper | Digital |
| **Pitzi** 🐕 | Helper scraper ( onboarding now! ) | +972527222872 |
| **Shpitzi** 🐕‍🦺 | Reddit Agent developer | +972502303683 |
| **Yossi** 👤 | Human owner | +972523112151 |
| **Ben** 👤 | SPZ Lead Programmer | +972544289167 |

## The Workflow (Step-by-Step)

### Phase 1: Scraping (Data Collection)

אנחנו אוספים מידע משלושה מקורות עיקריים:

#### A. RSS Feeds (חדשות מסורתיות)
**Skrip:** `spz-rss-scraper/multi_feed_generator.py`

**מקורות:**
- **ישראל:** Ynet (Breaking, Main, Opinions), Jerusalem Post, Times of Israel, Haaretz, Israel Hayom, Walla
- **בינלאומי:** BBC (Middle East, World), CNN, NYT, Guardian
- **עסקים:** Globes, Calcalist, Mako, Reshet 13

**מה הסקרייפר עושה:**
1. קורא כל RSS feed ברשימה
2. מסנן תוכן לפי מילות מפתח
3. מחלץ כותרת, תקציר, תמונה
4. מייצר score עבור כל כתבה
5. שומר לקבצי XML ב-`spz-feeds/`

#### B. Reddit (קהילות ודיונים)
**Script:** `spz-reddit-xml-generator.py`

**Subreddits:**
- מלחמה/ביטחון: r/IsraelHamasWar, r/IronSwords, r/2ndYomKippurWar, r/CombatFootage
- קהילה: r/Israel, r/Judaism, r/Jewish, r/Zionism
- ניתוח: r/Geopolitics, r/CredibleDefense, r/MiddleEastNews
- עולם: r/WorldNews, r/News

**מה הסקרייפר עושה:**
1. מביא פוסטים חדשים מכל סאברדיט
2. מחלץ תמונות/וידאו מתוך הפוסטים
3. מחשב dual score (תוכן + engagement)
4. מסנן תוכן לפי מילות מפתח
5. יוצר 4 קטגוריות: Top10, Hot, Trending, Fresh

#### C. Twitter (ציוצים בזמן אמת)
**Script:** `spz-twitter-nitter.py`

**Accounts:**
- **ישראל רשמי:** @Israel, @IDF, @IsraeliPM, @netanyahu
- **תקשורת ישראלית:** @Jerusalem_Post, @haaretzcom, @ynetnews, @TimesofIsrael
- **פוליטיקאים:** @naftalibennett, @yairlapid, @gantzbe
- **עולם:** @BBCBreaking, @CNN, @nytimes, @Reuters, @AP

**מה הסקרייפר עושה:**
1. משתמש ב-Nitter (שרת proxy חינם) כדי לגשל לטוויטר בלי API key
2. מנסה מספר instances אם אחד נופל
3. מסנן ציוצים לפי הקשר ישראלי
4. מייצר 4 קטגוריות כמו Reddit

### Phase 2: GitHub Upload

**Script:** `spz-auto-update.py` (חלק ממנו)

**מה קורה:**
1. סורק את תיקיית `spz-feeds/` כדי למצוא קבצי XML
2. יוצר directory זמני ייחודי (`spz-repo-temp-{timestamp}-{random}`)
3. מעתיק את כל קבצי ה-XML לשם
4. מבצע git add, commit, push
5. מנקה את ה-directory הזמני

**Repository:** https://github.com/cliffyjoe25-lgtm/sppz

### Phase 3: Cleanup

מוחק קבצים מקומיים ישנים מ-`spz-feeds/` (שמורים רק 4 שעות)

## The Orchestrator

**Script:** `spz-auto-update.py` — מריץ את כל הסקרייפרים ברצף

```
1. RSS Scraping (multi_feed_generator.py)
2. Reddit Scraping (spz-reddit-xml-generator.py)  
3. Twitter Scraping (spz-twitter-nitter.py)
4. GitHub Upload
5. Cleanup
```

**Runtime:** ~3-4 דקות לכל סייקל

## Content Filtering

### מה מונח (Block):
- Spam, קזינו, הימורים, תוכן פורנוגרפי
- Clickbait ברור

### מה מותר (Allow):
- כל חדשות העולם (USA, אירופה, אסיה, מזרח תיכון)
- ישראל מקבלת בונוס ב-scoring

### מילות מפתח חשובות:
**ישראל:** israel, israeli, gaza, palestine, idf, jerusalem, netanyahu, hamas, jew, jewish
**מלחמה:** war, attack, strike, missile, rocket, explosion
**עולם:** trump, ukraine, iran, geopolitics

## Scoring System

כל כתבה/פוסט/ציוץ מקבל ציון (0-100) לפי:
- **תוכן:** מילות מפתח רלוונטיות (+5 נקודות למילה)
- **מעורבות:** upvotes, comments, upvote ratio (Reddit)

דירוגים:
- S (80-100): קריטי
- A (65-79): חשוב מאוד
- B (50-64): חשוב
- C (35-49): בינוני
- D (0-34): נמוך

## Output Files

כל הקבצים נשמרים ב-`spz-feeds/`:

**RSS:**
- `ynet-breaking-news.xml`, `ynet-main-news.xml`, `ynet-opinions.xml`
- `bbc-middle-east.xml`, `bbc-news.xml`, `bbc-world.xml`
- (ו-14 נוספים...)

**Reddit:**
- `reddit-top10.xml` — 10 הפוסטים הטובים ביותר
- `reddit-hot.xml` — 10 הבאים בטיבם
- `reddit-trending.xml` — 10 טרנדים
- `reddit-fresh.xml` — 10 חדשים

**Twitter:**
- `twitter-top10.xml`, `twitter-hot.xml`, `twitter-trending.xml`, `twitter-fresh.xml`

---

*צויף הידע הזה לפיצי — ברוך הבא לצוות! 🐕*
