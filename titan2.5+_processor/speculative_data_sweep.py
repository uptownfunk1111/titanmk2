"""
Speculative Data Sweep for Pre-Game Prediction Refinement
- Gathers social media, news, weather, injury, and officiating data
- Performs sentiment and impact analysis
- Adjusts ML predictions in real-time
- Outputs updated tips, risk, and confidence
- Scrapes Twitter, Reddit, and forums for NRL news/rumors
- Filters posts by keywords and validates data sources
- Uses NLP for sentiment and relevance
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime
import argparse
import json
import re
import asyncio
from random import randint
import requests
from bs4 import BeautifulSoup

# Optional: For sentiment analysis
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

# Optional: For Reddit API
try:
    import praw
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False

# Optional: For spaCy and VADER
try:
    import spacy
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    SPACY_AVAILABLE = True
    VADER_AVAILABLE = True
    nlp = spacy.load('en_core_web_sm')
    vader_analyzer = SentimentIntensityAnalyzer()
except ImportError:
    SPACY_AVAILABLE = False
    VADER_AVAILABLE = False
    nlp = None
    vader_analyzer = None

# TikTok API integration
try:
    from TikTokApi import TikTokApi
    TIKTOK_AVAILABLE = True
except ImportError:
    TIKTOK_AVAILABLE = False

outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../outputs'))
tips_path = os.path.join(outputs_dir, f'this_weeks_tips_{datetime.now().date()}.csv')
speculative_report_path = os.path.join(outputs_dir, f'speculative_sweep_report_{datetime.now().date()}.csv')
social_json_path = os.path.join(outputs_dir, f'speculative_social_data_{datetime.now().date()}.json')

# --- Tier 2 Tactical Intelligence Keywords (Grouped by Theme) ---
TIER2_KEYWORDS = {
    'player_availability': [
        'late withdrawal', 'game time decision', 'fitness test', 'not seen at warm-up',
        'limping', 'injury cloud', 'failed HIA', 'concussion protocol', 'sick', 'illness',
        'flu', 'virus', 'soreness', 'tightness', 'nursing injury', 'rested', 'resting',
        'sidelined', 'not named', 'not in squad', 'not in 19', 'not in 22', 'not in 21',
        'not in 18th man', 'not in 18', 'not in 19th man', 'not in 20', 'not in 21st man',
        'not in 22nd man', 'not in 23', 'not in 24', 'not in 25', 'not in 26', 'not in 27',
        'not in 28', 'not in 29', 'not in 30', 'not in 31', 'not in 32', 'not in 33',
        'not in 34', 'not in 35', 'not in 36', 'not in 37', 'not in 38', 'not in 39',
        'not in 40', 'not in 41', 'not in 42', 'not in 43', 'not in 44', 'not in 45',
        'not in 46', 'not in 47', 'not in 48', 'not in 49', 'not in 50',
    ],
    'team_reshuffle': [
        'late change', 'reshuffle', 'unexpected change', 'surprise inclusion',
        'bench swap', 'named to start', 'named on bench', 'switch to bench',
        'switch to starting', 'named as 18th man', 'named as 19th man',
        'named as 20th man', 'named as 21st man', 'named as 22nd man',
        'named as 23rd man', 'named as 24th man', 'named as 25th man',
        'named as 26th man', 'named as 27th man', 'named as 28th man',
        'named as 29th man', 'named as 30th man',
    ],
    'coaching_hints': [
        'coach hint', 'coach suggestion', 'hinted at change', 'hinted at switch',
        'hinted at reshuffle', 'hinted at late change', 'hinted at late switch',
        'hinted at late inclusion', 'hinted at late withdrawal',
    ],
    'warmup_observations': [
        'not seen at warm-up', 'limping in warm-up', 'injured in warm-up',
        'left warm-up early', 'did not warm up', 'not warming up',
    ],
    'officiating_risk': [
        'referee change', 'officiating controversy', 'controversial call',
        'referee risk', 'referee bias', 'referee appointment',
    ],
    'weather': [
        'weather risk', 'rain expected', 'wet weather', 'slippery', 'windy',
        'heavy dew', 'storm forecast', 'weather delay',
    ],
    'insider_meta': [
        'insider tip', 'mail is', 'word is', 'hearing that', 'hearing whispers',
        'whispers are', 'strong mail', 'late mail', 'mail suggests',
    ]
}

# Flatten all keywords for use in sweeps
ALL_TIER2_KEYWORDS = [kw for group in TIER2_KEYWORDS.values() for kw in group]

# Helper: Get time window for scraping
def get_time_window(game_datetime):
    end_time = game_datetime
    start_time = end_time - datetime.timedelta(days=5)
    return start_time, end_time

# Stealth Twitter scraping using Playwright
async def scrape_twitter_stealth_async(keyword, max_results=10, headless=True, cookies_path=None):
    from playwright.async_api import async_playwright
    results = []
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    url = f"https://twitter.com/search?q={keyword}&src=typed_query&f=live"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1280, "height": 800},
            java_script_enabled=True
        )
        if cookies_path and os.path.exists(cookies_path):
            cookies = json.load(open(cookies_path, 'r'))
            await context.add_cookies(cookies)
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_timeout(randint(2000, 4000))
        # Scroll to load more tweets if needed
        last_height = await page.evaluate("document.body.scrollHeight")
        while len(results) < max_results:
            tweets = await page.query_selector_all('article')
            for tweet in tweets[len(results):max_results]:
                try:
                    username = await tweet.query_selector("a[role='link'][href*='/status/'] span")
                    username = await username.inner_text() if username else ''
                    tweet_content = await tweet.query_selector("div[lang]")
                    tweet_text = await tweet_content.inner_text() if tweet_content else ''
                    timestamp_elem = await tweet.query_selector("time")
                    timestamp = await timestamp_elem.get_attribute('datetime') if timestamp_elem else ''
                    link_elem = await tweet.query_selector("a[role='link'][href*='/status/']")
                    link = f"https://twitter.com{await link_elem.get_attribute('href')}" if link_elem else ''
                    results.append({
                        "username": username,
                        "tweet": tweet_text,
                        "timestamp": timestamp,
                        "link": link
                    })
                except Exception as e:
                    continue
            # Scroll if not enough tweets
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(randint(1500, 3000))
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        await browser.close()
    return results[:max_results]

def scrape_twitter_stealth(keywords, max_results=10):
    all_results = []
    for kw in keywords:
        try:
            tweets = asyncio.run(scrape_twitter_stealth_async(kw, max_results=max_results))
            for t in tweets:
                t['source'] = 'twitter_stealth'
                t['keyword'] = kw
            all_results.extend(tweets)
        except Exception as e:
            print(f"[ERROR] Stealth Twitter scraping failed for '{kw}': {e}")
    return all_results

# Reddit scraping using PRAW
def scrape_reddit(keywords, start_time, end_time, limit=100):
    try:
        import praw
    except ImportError:
        print("[WARN] praw not installed, skipping Reddit scraping.")
        return []
    reddit = praw.Reddit(client_id='YOUR_CLIENT_ID',
                         client_secret='YOUR_CLIENT_SECRET',
                         user_agent='nrl_speculative_sweep')
    results = []
    for submission in reddit.subreddit('nrl').new(limit=limit):
        created = datetime.datetime.utcfromtimestamp(submission.created_utc)
        if not (start_time <= created <= end_time):
            continue
        text = submission.title + ' ' + submission.selftext
        if any(kw.lower() in text.lower() for kw in keywords):
            results.append({
                'source': 'reddit',
                'title': submission.title,
                'text': submission.selftext,
                'created_utc': created.isoformat(),
                'url': submission.url
            })
    return results

# YouTube scraping using Google API
def scrape_youtube(keywords, start_time, end_time, max_results=50):
    try:
        from googleapiclient.discovery import build
    except ImportError:
        print("[WARN] googleapiclient not installed, skipping YouTube scraping.")
        return []
    api_key = "YOUR_YOUTUBE_API_KEY"
    youtube = build("youtube", "v3", developerKey=api_key)
    results = []
    for kw in keywords:
        try:
            search_response = youtube.search().list(
                q=kw,
                part="snippet",
                maxResults=max_results,
                publishedAfter=start_time.isoformat("T") + "Z",
                publishedBefore=end_time.isoformat("T") + "Z",
                type="video"
            ).execute()
            for item in search_response.get("items", []):
                snippet = item["snippet"]
                results.append({
                    "source": "youtube",
                    "title": snippet["title"],
                    "description": snippet["description"],
                    "publishedAt": snippet["publishedAt"],
                    "channelTitle": snippet["channelTitle"],
                    "keyword": kw
                })
        except Exception as e:
            print(f"[ERROR] YouTube API error: {e}")
    return results

# TikTok scraping using TikTokApi
def scrape_tiktok(keywords, max_results=20):
    if not TIKTOK_AVAILABLE:
        print("[WARN] TikTokApi not installed, skipping TikTok scraping.")
        return []
    results = []
    try:
        with TikTokApi() as api:
            for kw in keywords:
                try:
                    videos = api.by_hashtag(kw, count=max_results)
                    for video in videos:
                        results.append({
                            'source': 'tiktok',
                            'keyword': kw,
                            'desc': video.get('desc', ''),
                            'author': video.get('author', {}).get('uniqueId', ''),
                            'createTime': video.get('createTime', ''),
                            'stats': video.get('stats', {}),
                            'video_id': video.get('id', ''),
                            'url': f"https://www.tiktok.com/@{video.get('author', {}).get('uniqueId', '')}/video/{video.get('id', '')}"
                        })
                except Exception as e:
                    print(f"[ERROR] TikTok API error for keyword '{kw}': {e}")
    except Exception as e:
        print(f"[ERROR] TikTokApi global error: {e}")
    return results

# NRL.com news scraping
def scrape_nrl_com_news(keywords, max_results=20):
    """
    Scrape NRL.com news for articles matching keywords.
    """
    url = "https://www.nrl.com/news/"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        articles = []
        for item in soup.select(".news-list__item"):
            headline_elem = item.select_one(".news-list__headline")
            if not headline_elem:
                continue
            headline = headline_elem.text.strip()
            link_elem = item.select_one("a")
            link = "https://www.nrl.com" + link_elem["href"] if link_elem else ""
            summary_elem = item.select_one(".news-list__summary")
            summary = summary_elem.text.strip() if summary_elem else ""
            if any(kw.lower() in headline.lower() or kw.lower() in summary.lower() for kw in keywords):
                articles.append({
                    "source": "nrl.com",
                    "headline": headline,
                    "summary": summary,
                    "link": link
                })
            if len(articles) >= max_results:
                break
        return articles
    except Exception as e:
        print(f"[ERROR] NRL.com scraping failed: {e}")
        return []

# Fox League news scraping
def scrape_fox_league_news(keywords, max_results=20):
    """
    Scrape Fox League (Fox Sports) NRL news for articles matching keywords.
    """
    url = "https://www.foxsports.com.au/nrl"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        articles = []
        for item in soup.select(".story-block"):
            headline_elem = item.select_one(".story-block__heading")
            if not headline_elem:
                continue
            headline = headline_elem.text.strip()
            link_elem = item.select_one("a")
            link = link_elem["href"] if link_elem else ""
            summary_elem = item.select_one(".story-block__standfirst")
            summary = summary_elem.text.strip() if summary_elem else ""
            if any(kw.lower() in headline.lower() or kw.lower() in summary.lower() for kw in keywords):
                articles.append({
                    "source": "foxsports.com.au",
                    "headline": headline,
                    "summary": summary,
                    "link": link
                })
            if len(articles) >= max_results:
                break
        return articles
    except Exception as e:
        print(f"[ERROR] Fox League scraping failed: {e}")
        return []

# News.com.au NRL news scraping
def scrape_news_com_au_nrl(keywords, max_results=20):
    """
    Scrape News.com.au NRL section for articles matching keywords.
    """
    url = "https://www.news.com.au/sport/nrl"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        articles = []
        for item in soup.select(".story-block"):
            headline_elem = item.select_one(".story-block__heading")
            if not headline_elem:
                continue
            headline = headline_elem.text.strip()
            link_elem = item.select_one("a")
            link = link_elem["href"] if link_elem else ""
            summary_elem = item.select_one(".story-block__standfirst")
            summary = summary_elem.text.strip() if summary_elem else ""
            if any(kw.lower() in headline.lower() or kw.lower() in summary.lower() for kw in keywords):
                articles.append({
                    "source": "news.com.au",
                    "headline": headline,
                    "summary": summary,
                    "link": link
                })
            if len(articles) >= max_results:
                break
        return articles
    except Exception as e:
        print(f"[ERROR] News.com.au scraping failed: {e}")
        return []

# Wide World of Sports NRL news scraping
def scrape_wide_world_of_sports_nrl(keywords, max_results=20):
    """
    Scrape Wide World of Sports NRL section for articles matching keywords.
    """
    url = "https://wwos.nine.com.au/nrl"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        articles = []
        for item in soup.select(".story-block, .card, .article-card"):
            headline_elem = item.select_one(".story-block__heading, .card__headline, .article-card__headline")
            if not headline_elem:
                continue
            headline = headline_elem.text.strip()
            link_elem = item.select_one("a")
            link = link_elem["href"] if link_elem else ""
            summary_elem = item.select_one(".story-block__standfirst, .card__summary, .article-card__summary")
            summary = summary_elem.text.strip() if summary_elem else ""
            if any(kw.lower() in headline.lower() or kw.lower() in summary.lower() for kw in keywords):
                articles.append({
                    "source": "Wide World of Sports",
                    "headline": headline,
                    "summary": summary,
                    "link": link
                })
            if len(articles) >= max_results:
                break
        return articles
    except Exception as e:
        print(f"[ERROR] Wide World of Sports scraping failed: {e}")
        return []

# Zero Tackle news scraping
def scrape_zero_tackle_news(keywords, max_results=20):
    """
    Scrape Zero Tackle NRL news for articles matching keywords.
    """
    url = "https://www.zerotackle.com/nrl/news/"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        articles = []
        for item in soup.select(".news-list__item, .news-card"):
            headline_elem = item.select_one(".news-list__title, .news-card__title")
            if not headline_elem:
                continue
            headline = headline_elem.text.strip()
            link_elem = item.select_one("a")
            link = link_elem["href"] if link_elem else ""
            summary_elem = item.select_one(".news-list__summary, .news-card__summary")
            summary = summary_elem.text.strip() if summary_elem else ""
            if any(kw.lower() in headline.lower() or kw.lower() in summary.lower() for kw in keywords):
                articles.append({
                    "source": "Zero Tackle",
                    "headline": headline,
                    "summary": summary,
                    "link": link
                })
            if len(articles) >= max_results:
                break
        return articles
    except Exception as e:
        print(f"[ERROR] Zero Tackle scraping failed: {e}")
        return []

# Daily Telegraph news scraping
def scrape_daily_telegraph_nrl(keywords, max_results=20):
    """
    Scrape The Daily Telegraph NRL news for articles matching keywords.
    Note: Most content is paywalled, so only headlines and summaries are scraped.
    """
    url = "https://www.dailytelegraph.com.au/sport/nrl"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        articles = []
        for item in soup.select(".storyblock, .story-block"):
            headline_elem = item.select_one(".storyblock_title, .story-block__title")
            if not headline_elem:
                continue
            headline = headline_elem.text.strip()
            link_elem = item.select_one("a")
            link = link_elem["href"] if link_elem else ""
            summary_elem = item.select_one(".storyblock_standfirst, .story-block__standfirst")
            summary = summary_elem.text.strip() if summary_elem else ""
            if any(kw.lower() in headline.lower() or kw.lower() in summary.lower() for kw in keywords):
                articles.append({
                    "source": "Daily Telegraph",
                    "headline": headline,
                    "summary": summary,
                    "link": link
                })
            if len(articles) >= max_results:
                break
        return articles
    except Exception as e:
        print(f"[ERROR] Daily Telegraph scraping failed: {e}")
        return []

# --- Tier 2 News Outlets (placeholders for future expansion) ---
def scrape_the_athletic_nrl(keywords, max_results=20):
    """
    Placeholder for scraping The Athletic (if NRL coverage exists).
    """
    # TODO: Implement actual scraping logic
    return []

def scrape_code_sports_nrl(keywords, max_results=20):
    """
    Placeholder for scraping CODE Sports NRL section.
    """
    # TODO: Implement actual scraping logic
    return []

def scrape_abc_nrl(keywords, max_results=20):
    """
    Placeholder for scraping ABC NRL news section.
    """
    # TODO: Implement actual scraping logic
    return []

def gather_news_data(keywords):
    nrl_news = scrape_nrl_com_news(keywords)
    fox_news = scrape_fox_league_news(keywords)
    newsau_news = scrape_news_com_au_nrl(keywords)
    wwos_news = scrape_wide_world_of_sports_nrl(keywords)
    zero_tackle_news = scrape_zero_tackle_news(keywords)
    daily_telegraph_news = scrape_daily_telegraph_nrl(keywords)
    # Tier 2 outlets
    athletic_news = scrape_the_athletic_nrl(keywords)
    code_sports_news = scrape_code_sports_nrl(keywords)
    abc_news = scrape_abc_nrl(keywords)
    all_news = (nrl_news + fox_news + newsau_news + wwos_news + zero_tackle_news +
                daily_telegraph_news + athletic_news + code_sports_news + abc_news)
    print(f"[INFO] Gathered {len(nrl_news)} NRL.com, {len(fox_news)} Fox League, {len(newsau_news)} News.com.au, {len(wwos_news)} WWOS, {len(zero_tackle_news)} Zero Tackle, {len(daily_telegraph_news)} Daily Telegraph, {len(athletic_news)} The Athletic, {len(code_sports_news)} CODE Sports, {len(abc_news)} ABC news articles.")
    return all_news

# Facebook, Instagram, TikTok scraping placeholders
def scrape_facebook_instagram_tiktok(keywords, start_time, end_time):
    # Removed as per requirements.
    return []

def gather_social_media_data(keywords, game_datetime):
    start_time, end_time = get_time_window(game_datetime)
    twitter_stealth_posts = scrape_twitter_stealth(keywords, max_results=10)
    reddit_posts = scrape_reddit(keywords, start_time, end_time)
    youtube_posts = scrape_youtube(keywords, start_time, end_time)
    tiktok_posts = scrape_tiktok(keywords)
    all_posts = twitter_stealth_posts + reddit_posts + youtube_posts + tiktok_posts
    # Add news scraping
    news_posts = gather_news_data(keywords)
    all_posts += news_posts
    with open(social_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, indent=2)
    print(f"[INFO] Saved {len(all_posts)} social/forum/news posts to {social_json_path}")
    return all_posts

# --- Data Parsing and Validation ---
def parse_and_validate_social_data(posts, keywords):
    valid_posts = []
    for post in posts:
        text = (post.get('title', '') + ' ' + post.get('text', '')).lower()
        # Simple keyword density
        kw_count = sum(text.count(kw.lower()) for kw in keywords)
        # Sentiment
        sentiment = 0
        if VADER_AVAILABLE:
            sentiment = vader_analyzer.polarity_scores(text)['compound']
        elif TEXTBLOB_AVAILABLE:
            sentiment = TextBlob(text).sentiment.polarity
        # spaCy for entity recognition (optional, for future use)
        entities = []
        if SPACY_AVAILABLE and nlp is not None:
            doc = nlp(text)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
        # Simple source reliability check
        reliable = post.get('source', '') in ['reddit', 'twitter', 'twitter_stealth']
        # Flag if unreliable or low keyword density
        flagged = not reliable or kw_count == 0
        valid_posts.append({
            **post,
            'keyword_count': kw_count,
            'sentiment': sentiment,
            'entities': entities,
            'reliable': reliable,
            'flagged': flagged
        })
    return valid_posts

# --- Speculative Data Fetchers (existing placeholders) ---
def fetch_social_media_sentiment(teams, posts):
    # Aggregate sentiment for each team from posts
    sentiment = {team: 0.0 for team in teams}
    for team in teams:
        team_posts = [p for p in posts if team.lower() in (p.get('title','') + p.get('text','')).lower()]
        if team_posts:
            sentiment[team] = np.mean([p.get('sentiment', 0) for p in team_posts])
        else:
            sentiment[team] = np.random.uniform(-0.2, 0.2)  # fallback
    return sentiment

def fetch_injury_reports():
    print("[INFO] Fetching injury reports (simulated)...")
    return {"Broncos": 0, "Roosters": -0.2, "Storm": -0.1}

def fetch_weather_forecast(venue):
    print(f"[INFO] Fetching weather for {venue} (simulated)...")
    return np.random.uniform(-0.1, 0.1)

def fetch_referee_updates():
    print("[INFO] Fetching referee updates (simulated)...")
    return {"Referee": "John Doe", "Risk": "medium"}

# --- Adjust predictions with speculative data ---
def adjust_predictions_with_speculative(tips_df, sentiment, injuries, weather, referee):
    tips_df = tips_df.copy()
    for idx, row in tips_df.iterrows():
        team = row['RecommendedTip']
        sentiment_adj = sentiment.get(team, 0)
        injury_adj = injuries.get(team, 0)
        weather_adj = weather if isinstance(weather, float) else 0
        adj = sentiment_adj + injury_adj + weather_adj
        tips_df.at[idx, 'WinChance'] = min(100, max(0, row['WinChance'] + adj * 10))
        if abs(adj) > 0.2:
            tips_df.at[idx, 'Confidence'] = 'low'
        elif abs(adj) > 0.1:
            tips_df.at[idx, 'Confidence'] = 'medium'
        tips_df.at[idx, 'RefereeRisk'] = referee.get('Risk', row.get('RefereeRisk', 'unknown'))
    return tips_df

# --- Main ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manual', action='store_true', help='Allow manual speculative data input')
    parser.add_argument('--game_datetime', type=str, default=None, help='Game start datetime in ISO format (e.g., 2025-05-10T19:50:00)')
    args = parser.parse_args()
    tips_df = pd.read_csv(tips_path)
    teams = tips_df['RecommendedTip'].unique()
    keywords = ALL_TIER2_KEYWORDS + list(teams)
    # Use provided game_datetime or default to now
    if args.game_datetime:
        game_datetime = datetime.datetime.fromisoformat(args.game_datetime)
    else:
        game_datetime = datetime.datetime.now()
    posts = gather_social_media_data(keywords, game_datetime)
    valid_posts = parse_and_validate_social_data(posts, keywords)
    sentiment = fetch_social_media_sentiment(teams, valid_posts)
    injuries = fetch_injury_reports()
    venue = "Suncorp Stadium"  # Placeholder, could be dynamic
    weather = fetch_weather_forecast(venue)
    referee = fetch_referee_updates()
    if args.manual:
        print("[MANUAL] Enter manual speculative adjustments (e.g., Broncos: -0.3)")
        for team in teams:
            val = input(f"Adjustment for {team} (blank for 0): ")
            try:
                adj = float(val)
                sentiment[team] += adj
            except:
                pass
    updated_tips = adjust_predictions_with_speculative(tips_df, sentiment, injuries, weather, referee)
    updated_tips.to_csv(speculative_report_path, index=False)
    print(f"[SUCCESS] Speculative sweep report saved to {speculative_report_path}")
    print(updated_tips)
    # Optionally, print flagged/controversial posts
    flagged = [p for p in valid_posts if p['flagged']]
    if flagged:
        print(f"[INFO] Flagged/controversial social posts:")
        for p in flagged[:5]:
            print(f"  - {p.get('title','')[:60]}... (source: {p.get('source','')})")

if __name__ == "__main__":
    main()
```
