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
import datetime

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

outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../outputs'))
tips_path = os.path.join(outputs_dir, f'this_weeks_tips_{datetime.now().date()}.csv')
speculative_report_path = os.path.join(outputs_dir, f'speculative_sweep_report_{datetime.now().date()}.csv')
social_json_path = os.path.join(outputs_dir, f'speculative_social_data_{datetime.now().date()}.json')

# Helper: Get time window for scraping
def get_time_window(game_datetime):
    end_time = game_datetime
    start_time = end_time - datetime.timedelta(days=5)
    return start_time, end_time

# Twitter scraping using Tweepy (API v2)
def scrape_twitter(keywords, start_time, end_time, max_results=100):
    print("[INFO] Twitter scraping disabled as per requirements.")
    return []

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

# Facebook, Instagram, TikTok scraping placeholders
def scrape_facebook_instagram_tiktok(keywords, start_time, end_time):
    # Removed as per requirements.
    return []

def gather_social_media_data(keywords, game_datetime):
    start_time, end_time = get_time_window(game_datetime)
    # twitter_posts = scrape_twitter(keywords, start_time, end_time)  # Disabled
    reddit_posts = scrape_reddit(keywords, start_time, end_time)
    youtube_posts = scrape_youtube(keywords, start_time, end_time)
    # fb_ig_tt_posts = scrape_facebook_instagram_tiktok(keywords, start_time, end_time)  # Disabled
    all_posts = reddit_posts + youtube_posts
    with open(social_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, indent=2)
    print(f"[INFO] Saved {len(all_posts)} social/forum posts to {social_json_path}")
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
        reliable = post.get('source', '') in ['reddit', 'twitter']
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
    keywords = ['injury', 'suspension', 'transfer', 'coach', 'prediction', 'weather', 'lineup', 'late change'] + list(teams)
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
