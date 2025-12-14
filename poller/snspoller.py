# poller/snspoller.py
import os
import tweepy
import sqlite3
from datetime import datetime
import time
from textblob import TextBlob
from dotenv import load_dotenv
import logging

# -------- Logging --------
logging.basicConfig(
    filename="poller.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------- Twitter API Setup --------
load_dotenv()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# -------- Keywords to track --------
keywords = ["python", "aws", "cloud", "data", "ai"]

# -------- Database Setup --------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "tweets.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()

# Create table if it doesn't exist
c.execute("""
CREATE TABLE IF NOT EXISTS tweets (
    id TEXT PRIMARY KEY,
    username TEXT,
    text TEXT,
    created_at TEXT,
    fetched_at TEXT,
    sentiment REAL,
    label TEXT
)
""")
conn.commit()

# -------- Sentiment Analysis --------
def analyze_sentiment(text):
    analysis = TextBlob(text)
    score = analysis.sentiment.polarity
    if score > 0:
        label = "positive"
    elif score < 0:
        label = "negative"
    else:
        label = "neutral"
    return score, label

# -------- Polling Function --------
def poll_once():
    for keyword in keywords:
        query = f"{keyword} lang:en -is:retweet"
        try:
            tweets = client.search_recent_tweets(
                query=query,
                tweet_fields=['author_id', 'created_at'],
                expansions=['author_id'],
                max_results=10
            )

            if tweets.data:
                users = {u["id"]: u for u in tweets.includes['users']} if tweets.includes else {}
                for tweet in tweets.data:
                    try:
                        username = users[tweet.author_id].username if users else "unknown"
                        sentiment_score, label = analyze_sentiment(tweet.text)

                        c.execute(
                            """
                            INSERT INTO tweets 
                            (id, username, text, created_at, fetched_at, sentiment, label)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                tweet.id,
                                username,
                                tweet.text,
                                tweet.created_at,
                                datetime.now(),
                                sentiment_score,
                                label
                            )
                        )
                        conn.commit()
                        logging.info(f"Saved tweet: {tweet.text[:50]}...")
                        print(f"Saved tweet: {tweet.text[:50]}...")

                    except sqlite3.IntegrityError:
                        logging.info("Duplicate tweet skipped.")
                        continue
        except tweepy.errors.TooManyRequests:
            logging.warning(f"Rate limit hit. Waiting 15 minutes before retry...")
            print("Rate limit hit. Waiting 15 minutes...")
            time.sleep(15 * 60)
        except tweepy.TweepyException as e:
            logging.error(f"API error for keyword '{keyword}': {e}")
            print(f"API error for keyword '{keyword}': {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            print(f"Unexpected error: {e}")


# -------- Main Loop --------
if __name__ == "__main__":
    print("Poller started. Keywords:", keywords)
    while True:
        try:
            poll_once()
            time.sleep(60)  # Wait 1 minute before next poll
        except KeyboardInterrupt:
            print("\nPoller stopped by user.")
            conn.close()
            break
