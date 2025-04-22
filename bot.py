import tweepy
import requests
import os
from time import sleep
from datetime import datetime

# Configuration Twitter API v2
client = tweepy.Client(
    bearer_token=os.environ["TWITTER_BEARER_TOKEN"],
    consumer_key=os.environ["TWITTER_API_KEY"],
    consumer_secret=os.environ["TWITTER_API_SECRET"],
    access_token=os.environ["TWITTER_ACCESS_TOKEN"],
    access_token_secret=os.environ["TWITTER_ACCESS_SECRET"]
)

# Configuration Telegram
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

KEYWORDS = ["bon plan", "promo PS5", "#crypto"]
seen_tweets = set()

def send_telegram_alert(text: str, author: str, url: str):
    """Envoie une notification Telegram formatée"""
    message = (
        f"🔔 **Nouveau Tweet**\n\n"
        f"👤 Auteur: @{author}\n"
        f"📝 Texte: {text}\n\n"
        f"🔗 {url}"
    )
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    )

def check_tweets():
    """Recherche de tweets avec API v2"""
    for keyword in KEYWORDS:
        try:
            response = client.search_recent_tweets(
                query=keyword,
                max_results=5,
                tweet_fields=["author_id"],
                user_fields=["username"],
                expansions="author_id"
            )
            
            if response.data:
                users = {u.id: u.username for u in response.includes['users']}
                for tweet in response.data:
                    if tweet.id not in seen_tweets:
                        seen_tweets.add(tweet.id)
                        author = users[tweet.author_id]
                        tweet_url = f"https://twitter.com/{author}/status/{tweet.id}"
                        send_telegram_alert(tweet.text, author, tweet_url)
        except Exception as e:
            print(f"Erreur: {e}")

if __name__ == "__main__":
    print(f"[{datetime.now()}] → Démarrage du bot")
    while True:
        check_tweets()
        sleep(300)  # 5 minutes
