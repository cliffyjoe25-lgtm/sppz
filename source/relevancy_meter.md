# SPZ Relevancy Meter v1.1 🎯

**Skill Purpose:** Score articles/posts for relevance to SPZ mission (1-10 scale)

---

## Scoring Framework

Each article receives a score from **1-10** based on weighted factors:

| Factor | Weight | Description | Scoring Guidelines |
|--------|--------|-------------|-------------------|
| **Threat Exposure** | 20% | Exposure of threats to Jewish/Israeli interests | 10 = Active threat (terror, demographic manipulation, influence ops against Jews/Israel)<br>8 = Leadership misconduct affecting national security<br>5 = Policy harming Jewish communities<br>2 = Indirect threat potential<br>1 = No direct threat |
| **Global Crisis** | 20% | Major international event | 10 = War, terror attack, major diplomatic incident affecting Israel/Jews globally<br>7 = Regional conflict, significant policy change<br>4 = Localized incident with potential spread<br>1 = Minor incident, limited impact |
| **Publisher Status** | 18% | Authority + coverage duplication | 10 = Tier-1 outlet (BBC, NYT, WaPo) + 5+ duplicate publishers<br>7 = Major outlet (Fox, CNN) + 3-4 duplicates<br>4 = Mid-tier blog/social + 1-2 duplicates<br>1 = Unknown source, no verification |
| **Narrative Alignment** | 15% | Alignment with SPZ goals | 10 = Strong pro-Israel content, positive Jewish representation<br>7 = Neutral factual coverage<br>4 = Critical but fair analysis<br>1 = Active anti-Israel propaganda, hate speech |
| **Geographic Proximity** | 12% | Distance from Israel/Palestine | 10 = Directly in Israel/Gaza/West Bank<br>7 = Middle East region (Lebanon, Jordan, Egypt, Iran)<br>4 = Diaspora Jewish communities (Europe, US campuses)<br>1 = Global general interest, no direct connection |
| **Engagement** | 10% | Social virality indicators | 10 = 100K+ likes/shares, trending hashtag<br>7 = 10K-100K engagement, significant spread<br>4 = 1K-10K engagement, niche audience<br>1 = <1K engagement, minimal reach |
| **Ongoing vs Single** | 8% | Story lifecycle stage | 10 = Breaking/developing (first 24 hours), new developments hourly<br>7 = Active story (2-7 days), updates continuing<br>4 = Settled story (>1 week), no new developments<br>1 = Historical reference, archive content |
| **Recency** | 5% | Time since publication | 10 = <6 hours old<br>7 = 6-24 hours old<br>4 = 1-3 days old<br>1 = >3 days old |
| **Verifiability** | 5% | Source credibility | 10 = Reputable news org, multiple confirm sources, official statements<br>7 = Established outlet, some sourcing<br>4 = Blog/aggregator, unverified claims<br>1 = Anonymous source, conspiracy theory, no evidence |

**Calculation:** Weighted sum → normalized to 1-10 scale

**Total Weights:** 100%

---

## Stop Conditions

### Interval Stop (Primary)
- **Total accumulated score ≥ 200** → Stop scraping for this interval
- Check `spz-shared/data/` for running total per 4-hour window

### Immediate Alert (Critical)
- **Any single article scores ≥ 9** → Immediately send WhatsApp alert to:
  - Ben: +972 54-428-9167
  - Yossi: +972 52-722-2872

Alert format:
```
🚨 HIGH RELEVANCY ALERT
Score: [X]/10
Source: [Publisher]
Title: [Article Title]
URL: [Link]
Key Factors: [Why it scored high]
```

---

## Platform Extraction Notes

**Twitter/X:**
- Primary: Tweet text, thread content
- Secondary: Engagement metrics (likes, RTs, replies)
- Notes: Check quoted tweets for context

**Instagram:**
- Primary: Image OCR (if text-heavy), caption
- Secondary: Alt text, comments for context
- Notes: Stories expire — prioritize posts/Reels

**Facebook:**
- Primary: Post text
- Secondary: Reaction types (angry/love vs just likes), shares
- Notes: Comments often contain narrative direction

**YouTube:**
- Primary: Title, description, transcript (if available)
- Secondary: Comments sentiment, view velocity
- Notes: Shorts algorithm different from long-form

**News Sites:**
- Primary: Headline, lead paragraph, dateline
- Secondary: Author credentials, cited sources
- Notes: Paywall may limit access

---

## Data Storage

**Per Article Record:**
```json
{
  "id": "uuid",
  "source_platform": "twitter|instagram|facebook|youtube|web",
  "publisher": "account_name",
  "publisher_category": "advocate|opposition|journalist|etc",
  "url": "direct_link",
  "title": "extracted_title",
  "content_summary": "auto_or_manual_summary",
  "published_at": "ISO_timestamp",
  "scraped_at": "ISO_timestamp",
  "scores": {
    "threat_exposure": 0-10,
    "global_crisis": 0-10,
    "publisher_status": 0-10,
    "narrative_alignment": 0-10,
    "geographic_proximity": 0-10,
    "engagement": 0-10,
    "ongoing_factor": 0-10,
    "recency": 0-10,
    "verifiability": 0-10
  },
  "final_score": 1.0-10.0,
  "alert_triggered": true|false,
  "raw_engagement": {
    "likes": number,
    "shares": number,
    "comments": number
  }
}
```

**Storage Location:** `spz-shared/data/YYYY-MM-DD/articles.jsonl`

---

## Key Scoring Insights

### Internal Threats Matter
Stories exposing threats **from within** (domestic political manipulation, leadership misconduct, influence operations) can score as high as external crises because:
- They affect Israeli/Jewish demographic and political stability
- They expose vulnerabilities that need rapid response
- They often get less mainstream coverage but are critical for audience awareness

### Example: Epstein/Barak Story
- **Threat Exposure: 9** — Alleged demographic manipulation via foreign influence network
- **Publisher Status: 5** — Anadolu (lower tier but story still valid)
- **Final Score: ~8.0** — High priority despite lower-tier publisher

---

## Version History

- **v1.1** (2026-02-12) — Added "Threat Exposure" factor (20%), adjusted all weights
- **v1.0** (2026-02-12) — Initial framework with 8 weighted factors

---

*Managed by Tzippi for SPZ* 🐿️🦞
